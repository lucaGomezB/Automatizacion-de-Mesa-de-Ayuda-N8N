# Design: Monitorear el servicio de inferencia y la deriva del modelo

## Context

Ver `proposal.md` (Why) para la motivacion. Estado actual y restricciones que condicionan el diseno:

- **Acoplamiento al proveedor.** `App/Backend/app/classifiers/gemini_classifier.py` importa `google-genai` (`genai.Client`, `genai_errors`, `genai_types`) y concentra el cliente compartido, la construccion del prompt, la validacion del contrato, el bucle de reintento con backoff y jitter, y el fallback. `hybrid.py` instancia `GeminiClassifier` y solo conoce su contrato `BaseClassifier`. El modelo se resuelve de `Settings.gemini_model` (`gemini-3.6-flash`) y la clave de cache de la evaluacion es `HYBRID_CACHE_VERSION = "hybrid-v3"` (`App/Backend/app/constants.py`).
- **Evidencia congelada.** `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` es una copia byte a byte del cache de predicciones, con `corpus_hash` (`1fd17d7e…`), `corpus_count` (200) y `generated_at`; respalda las metricas canonicas. El cache vivo (`evaluation/predicciones.json`) esta fuera del repositorio.
- **Gate de corrida paga.** `evaluation/run_evaluation.py` y `evaluation/sensibilidad_ajustes.py` ya exigen `--confirm-paid` o `EVALUATION_CONFIRM_PAID=1` antes de invocar al proveedor (`PaidRunNotConfirmedError`).
- **Metricas reutilizables.** `evaluation/metrics.py` calcula exactitud estricta, F1 macro y metricas por sector sobre las cinco clases canonicas, en funciones puras. `evaluation/stats.py` aporta las utilidades estadisticas.
- **Conjunto independiente disponible.** La validacion fuera de muestra (`evaluation-out-of-sample-validation`) uso un corpus independiente de 150 casos, disjunto del corpus de ajuste; es la fuente natural del conjunto canario.
- **Fallback vigente.** `classification-resilience` ya especifica el fallback con `etapa=fallback`, `confianza=0.0` y `requiere_revision_humana=true` tras agotar los reintentos.

**Hecho del estado actual:** ningun numero canonico (exactitud estricta `0,6893`, F1 macro `0,6508`, ni los valores de las secciones del memo) cambia. La evidencia congelada no se toca.

## Goals / Non-Goals

**Goals:**

- Desacoplar la etapa semantica del proveedor concreto mediante una interfaz, sin cambiar el contrato de clasificacion ni el comportamiento por defecto.
- Permitir el recambio de proveedor o de version de modelo por configuracion, con trazabilidad de la identidad efectiva.
- Detectar de forma periodica y offline la deriva del servicio y del modelo, con umbrales y alertas.
- Documentar el fallback operativo (filtro deterministico con revision humana) y su criterio de restablecimiento.

**Non-Goals:**

- Implementar un proveedor alternativo real ni evaluar modelos abiertos: eso queda como trabajo futuro (`10-recomendaciones.tex`, `subsec:evaluacion-modelos-abiertos`).
- Medir de nuevo la tesis, re-correr la campana o cambiar el corpus, las predicciones canonicas o la evidencia congelada.
- Cambiar el vocabulario deterministico, el prompt, los parametros de inferencia o el punto de operacion.
- Modificar la resiliencia de `classification-resilience` ni el contrato de `evaluation-framework`.
- Recalibrar el gate de confianza (pertenece a otros changes del plan de correccion).

## Decisions

### D1 — Interfaz del proveedor en el nivel de la generacion, no de la clasificacion

La interfaz vive en `App/Backend/app/classifiers/provider.py` y expone una operacion asincrona de generacion:

```
class InferenceProvider(Protocol):
    async def generate(self, *, prompt: str, params: InferenceParams) -> str: ...
```

La etapa semantica conserva del lado del clasificador la construccion del prompt, la validacion del contrato, el bucle de reintento y el fallback; el proveedor solo envuelve el SDK, arma la configuracion de generacion y ejecuta la llamada. `GeminiClassifier` pasa a ser una implementacion (`GeminiProvider`) registrada por nombre.

Alternativas descartadas:
- **Interfaz en el nivel de clasificacion** (`classify(descripcion) -> ClasificacionResult`): habria movido el prompt y la validacion canonica dentro de cada proveedor, con riesgo de divergencia del contrato y de los cinco sectores. Se descarta.
- **Abstraer solo por variable de entorno sin interfaz**: no desacopla `hybrid.py` del SDK y no permite inyectar implementaciones falsas en pruebas sin red.

La taxonomia de errores (transitorio/terminal) forma parte del contrato de la interfaz: la implementacion traduce los errores de su SDK a esa taxonomia, y el bucle de reintento del clasificador deja de depender de `genai_errors`.

### D2 — Seleccion por configuracion con neutralidad por defecto

`Settings` incorpora `inference_provider: str = "gemini"` y `inference_model: str = "gemini-3.6-flash"`. Un registro resuelve el nombre del proveedor a su factory. Si `inference_model` no se define, se conserva el valor de `gemini_model` para compatibilidad. Los defaults resuelven exactamente al proveedor y al modelo vigentes.

La clave de cache distingue la identidad: el metadata de la cache de predicciones gana los campos `provider` y `model`, y una entrada es valida solo si coinciden (ademas del `corpus_hash` y el `classifier_version` vigentes). Para no invalidar la evidencia congelada —cuyas predicciones no declaran proveedor ni modelo—, la ausencia de esos campos se interpreta como el proveedor y el modelo por defecto, que coinciden con los de la configuracion vigente. `HYBRID_CACHE_VERSION` no cambia su valor por defecto.

Alternativas descartadas:
- **Incrementar `HYBRID_CACHE_VERSION` al introducir la abstraccion**: invalidaria el cache vivo y forzaria una corrida paga innecesaria; el comportamiento por defecto no cambia, de modo que no corresponde un cambio de version.
- **Guardar el modelo en constantes**: impide cambiarlo sin recompilar, contra el requisito de seleccion por configuracion.

### D3 — Conjunto canario fijo tomado del corpus independiente

El canario se versiona en `evaluation/data/canario/canario.json` (descripciones pseudonimizadas y sectores asignados) como un subconjunto fijo, con `canario.SHA256SUMS.txt`. Se toma del corpus independiente ya disponible (`evaluation-out-of-sample-validation`), que es disjunto del corpus de ajuste; su composicion por sector y por canal queda registrada y es estable. La linea de base congelada (`evaluation/data/canario/canario_baseline.json`) registra las metricas del canario calculadas una sola vez desde los artefactos versionados (offline, determinista).

Alternativas descartadas:
- **Etiquetar un conjunto nuevo**: exige trabajo de etiquetado y no aporta independencia adicional respecto del corpus independiente que ya existe.
- **Usar el corpus de evaluacion de 200 casos**: su vocabulario y sus reglas de prompt derivan del ajuste, con lo que el canario dejaria de ser un held-out limpio y podria enmascarar una deriva correlacionada con el ajuste.

### D4 — Job offline por defecto, con gate de corrida paga

El job vive en `evaluation/monitoreo/` (`monitor_deriva.py` + `test_monitor_deriva.py`). Por defecto lee las predicciones de los artefactos versionados y reproduce la linea de base sin invocar al proveedor. Una corrida con predicciones frescas reutiliza el gate de `evaluation/run_evaluation.py` (`--confirm-paid` / `EVALUATION_CONFIRM_PAID=1`) y escribe un reporte fechado en `evaluation/data/canario/reportes/`, sin sobrescribir la linea de base ni la evidencia.

Funciones puras (prueba sintetica antes de implementar):

| Funcion | Que calcula | Reutiliza |
|---|---|---|
| `metricas_canario(pares)` | Exactitud estricta, F1 macro y por sector sobre el canario | `evaluation/metrics.py` |
| `comparar_con_base(actual, base)` | Diferencia por metrica y bandera de degradacion | — |
| `detectar_deriva(metricas, base, tolerancias, identidad, base_identidad)` | Veredicto y tipo de deriva (metrica o identidad) | — |
| `evaluar_alertas(metricas, pisos)` | Alertas por metrica bajo su piso | — |
| `identidad_proveedor(config)` | Proveedor y modelo efectivos | `Settings` |

### D5 — Deteccion de deriva: dos ejes separados

La deteccion compara la identidad del proveedor y del modelo y, por separado, cada metrica contra su linea de base con su tolerancia. El veredicto es uno de: `sin_deriva`, `deriva_de_identidad` (cambio de proveedor o de version de modelo), `deriva_de_metrica` (degradacion con identidad estable) o `ambas`. La separacion evita atribuir a un cambio de codigo lo que en realidad es un cambio de modelo, y viceversa.

### D6 — Umbrales y fallback documentado

Los pisos por metrica se leen de `Settings` (`monitoring_*_floor`) y por defecto se derivan de la linea de base congelada menos una tolerancia declarada. Una metrica bajo su piso emite una alerta con la metrica, su valor, su piso y la corrida. La alerta incorpora el fallback vigente de `classification-resilience` (filtro deterministico preservado con revision humana) y el criterio para restablecer el servicio. La alerta es informativa: no altera el clasificador ni dispara un recambio automatico de proveedor.

### D7 — Preservacion de lo canonico

El job escribe solo en rutas nuevas (`evaluation/data/canario/`). Ninguna salida toca `evaluation/evidence/`, `evaluation/predicciones.json`, `data/corpus_evaluacion_pseudonimizado.json` ni los artefactos de campana. La verificacion de cierre compara el SHA-256 de `evaluation/evidence/` antes y despues de una corrida. Un valor que se decida citar solo se registra por el mecanismo del memo canonico, sin retirar ningun valor vigente.

### D8 — Gobernanza y frontera

Interfaz, configuracion y job: **MEDIUM**, con checkpoint de los autores antes de fijar los pisos por defecto (la calibracion de umbrales es una decision operativa). No hay bloque HIGH ni CRITICAL: no se toca autenticacion, facturacion ni datos personales; el canario reutiliza descripciones ya pseudonimizadas. Sin cambios en `n8n/`, la guarda de costo ni el corpus de evaluacion. Cero llamadas pagas fuera del gate de confirmacion.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| La abstraccion altera el resultado por defecto | Prueba de neutralidad caso por caso contra las predicciones vigentes; los defaults resuelven al proveedor y modelo actuales |
| Invalidar la evidencia congelada por el cambio de clave de cache | La ausencia de `provider`/`model` se interpreta como los valores por defecto; `HYBRID_CACHE_VERSION` no cambia |
| El canario se contamina con el corpus de ajuste | Se toma del corpus independiente y se declara no apto para ajuste |
| El job sobrescribe un artefacto canonico | Escritura restringida a rutas nuevas; verificacion de SHA-256 de `evaluation/evidence/` |
| Un umbral mal fijado no detecta una deriva real o genera ruido | Los pisos se derivan de la linea de base con tolerancia declarada y quedan configurables; el checkpoint de D8 los revisa |
| Sobre-ingenieria del registro de proveedores | El registro arranca con un unico proveedor (Gemini); se agregan entradas solo cuando exista un proveedor real que evaluar |

## Migration Plan

1. Preparacion y linea de base (grupo 0): registrar el estado, la evidencia y los anclajes.
2. Interfaz del proveedor y neutralidad (grupo 1, TDD).
3. Conjunto canario y linea de base (grupo 2).
4. Job de reevaluacion, deteccion de deriva y umbrales (grupo 3, TDD).
5. Fallback documentado y trazabilidad (grupo 4).
6. Verificacion de cierre (grupo 5): no regresiones, evidencia intacta, `openspec validate --strict`.

Rollback: revertir el commit restaura `hybrid.py` y `gemini_classifier.py` a su forma previa; el canario y el job se retiran como archivos nuevos. Sin huecos numericos.

## Open Questions

- **OQ1 (autores, operativa, difiere a la aplicacion)**: valores por defecto de la tolerancia y de los pisos por metrica. Afecta el valor configurable, no la especificacion ni el desglose de tareas; se fija en el checkpoint de D8 sin cambiar los specs.
- **OQ2 (autores, operativa, difiere a la aplicacion)**: cadencia del job y tamano del canario. Las tareas construyen el job y el canario con un tamano verificable; la cadencia de produccion y el tamano final son parametros operativos.
