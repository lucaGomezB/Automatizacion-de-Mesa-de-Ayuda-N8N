# evaluation/data/campana/

Esta carpeta guarda la **tabla primaria del doble etiquetado**: la planilla
etiquetador x caso que permite calcular el kappa de Cohen con su intervalo de
confianza. No contiene datos personales (PII) ni la descripción de los casos:
solo alias (`E1`, `E2`), identificadores de caso, sectores canónicos y marcas de
tiempo. El esquema es el de `evaluation/data/plantilla_etiquetado.csv` y el único
validador es `evaluation/doble_etiquetado.py`.

Desde c-166 la carpeta también aloja los artefactos de la campaña contrabalanceada y del
corpus independiente (ver la sección "Artefactos de la campaña contrabalanceada y del
corpus independiente (c-166)", al final).

La conservación de esta tabla es **criterio de aceptación de la campaña**: sin ella
el kappa vuelve a quedar sin intervalo de confianza. El protocolo completo
(sujetos, cegado, codebook, versionado) está en
`docs/campana-medicion/runbook-doble-etiquetado.md`.

## Estado actual

**Pendiente de campaña.** Todavía no existe `doble_etiquetado.csv`: el etiquetado
real corre fuera del repositorio y la tabla se agrega después, siguiendo el
runbook. Mientras el archivo no exista, el test de integridad
(`test_tabla_primaria_versionada_integra`) se omite.

## Archivos de esta carpeta

- `doble_etiquetado.csv`: tabla primaria validada (se agrega después de la campaña).
- `registro_sujetos.csv`: columnas `alias, rol, persona` (se agrega después de la
  campaña; sin nombres, ver el runbook).
- `*.csv` se versionan con fin de línea LF (`.gitattributes`) para que el SHA-256
  coincida en Windows y Linux.

## Procedencia de la tabla primaria

Completar **al versionar** la tabla, con una línea `- campo: valor` por campo. El
test de integridad lee `sha256` de esta sección y lo compara con el hash real del
archivo. Mientras no exista la tabla, los valores quedan en `pendiente`.

- archivo: pendiente
- sha256: pendiente
- fecha: pendiente
- corpus: pendiente
- corpus_sha256: pendiente
- tarea: pendiente
- comando_de_validacion: pendiente
- codebook_sha256: d9777139e9eaffe7903fa63d69d2bee346ff2b43599409aedaaebd21a8be9167
- estado_cegado: pendiente
- motivo_limitacion: no aplica

Significado de cada campo:

- `archivo`: ruta de la tabla (`evaluation/data/campana/doble_etiquetado.csv`).
- `sha256`: SHA-256 del archivo tal como está versionado (LF). Calcularlo con
  `sha256sum evaluation/data/campana/doble_etiquetado.csv`.
- `fecha`: fecha ISO (`AAAA-MM-DD`) en que se versionó.
- `corpus`: corpus contra el que se validó (por ejemplo
  `data/corpus_evaluacion_pseudonimizado.json`) y, en `corpus_sha256`, su SHA-256.
- `tarea`: `doble_etiquetado`.
- `comando_de_validacion`: el comando exacto y su resultado (exit code `0`), por
  ejemplo
  `python -m evaluation.doble_etiquetado --planilla evaluation/data/campana/doble_etiquetado.csv --corpus data/corpus_evaluacion_pseudonimizado.json --tarea doble_etiquetado`.
- `codebook_sha256`: SHA-256 del codebook operativo congelado antes de etiquetar (el
  mismo documento para `E1` y `E2`; ver el runbook).
- `estado_cegado`: `cumplido` | `limitacion_declarada`.
  - `cumplido`: `E1` y `E2` son personas distintas entre sí, de los dos analistas
    originales, de los autores y de los operadores `O*`, y etiquetaron sin ver el
    consenso, las predicciones ni las etiquetas del par.
  - `limitacion_declarada`: no se consiguieron etiquetadores nuevos. En
    `motivo_limitacion` se registra el motivo y los roles solapados. El resultado
    se reporta como limitación y **no** como etiquetado ciego.

## Artefactos de la campaña contrabalanceada y del corpus independiente (c-166)

Esta carpeta también aloja, desde c-166, los artefactos de la campaña contrabalanceada y de la clasificación del corpus independiente. Ninguno contiene datos personales ni sobrescribe un artefacto de la v9: los harnesses y el runner abortan antes de escribir si se los apunta a `data/corpus_evaluacion_pseudonimizado.json`, a `data/corpus_resultados*.json`, a `evaluation/predicciones.json` o a `evaluation/report.md`. Los protocolos están en `docs/campana-medicion/runbook-campana-contrabalanceada.md` y `docs/campana-medicion/runbook-corpus-independiente.md`.

| Archivo | Qué es | Cómo se genera |
|---|---|---|
| `plan_campana.csv` | Plan de campaña por caso: `id_caso,posicion,mitad,brazo_primero,modo,seed` | `python -m evaluation.plan_campana generar` |
| `subplan_m<mitad>_<brazo>_t<turno>.csv` | Sub-plan de un turno (conserva la `posicion` global); se versionan los efectivamente usados | `python -m evaluation.plan_campana subplan` |
| `corpus_campana.json` | Copia de campaña del corpus canónico con `tiempo_automatizado_s` y `tiempo_manual_s` en `null`: es el `--json` de las corridas con `--plan` | `python -m evaluation.plan_campana preparar-corpus` |
| `sidecar_<id_corrida>.json` | Sidecar propio de una corrida (sin descripciones), con `orden`, `posicion`, `mitad`, `brazo_primero` e `id_corrida` por caso | `--sidecar` de los harnesses |
| `sidecar_<id_corrida>.json.plan.csv` | Plan que dejó `--orden` junto al sidecar (solo si se usó ese atajo) | `--orden` de los harnesses |
| `corpus_independiente.json` | Corpus independiente pseudonimizado (ids `I001..`), solo en su forma pseudonimizada; ruta recomendada | runbook del corpus independiente |
| `predicciones_independiente.json` | Cache de predicciones del corpus independiente; su `cache_meta` trae `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines` | `python -m evaluation.run_evaluation --corpus ... --predicciones ... --reporte ...` |
| `reporte_independiente.md` | Reporte propio de esa corrida (ruta recomendada de `--reporte`) | idem |

La copia de campaña tiene más valores nulos que el corpus canónico: es intencional. Un caso no medido en la campaña queda nulo y no hereda el tiempo canónico (`merge_evaluation_json` solo escribe mediciones válidas).

### SHA-256 por archivo

Al versionar cada archivo se completa su SHA-256 (en minúsculas, calculado sobre el archivo tal como queda versionado, con fin de línea LF: `.gitattributes` lo fija para los `*.csv`, `*.json` y `*.md` de esta carpeta; un archivo generado en Windows con CRLF se normaliza antes con `sed -i 's/$//' <archivo>`), con el mismo patrón que `evaluation/evidence/README.md`. Mientras un archivo no exista, su hash queda en `pendiente`. Esta tabla no usa el formato `- campo: valor` de la sección de procedencia de la tabla primaria, que lee el test de integridad de c-168.

| Archivo | SHA-256 |
|---|---|
| `plan_campana.csv` | pendiente |
| `corpus_campana.json` | pendiente |
| `corpus_independiente.json` | pendiente |
| `predicciones_independiente.json` | pendiente |
| `reporte_independiente.md` | pendiente |
| `plantilla_etiquetado.csv` | pendiente |
| `predicciones_in_sample.json` | pendiente |
| cada `sidecar_<id_corrida>.json` y `subplan_*.csv` usado | pendiente (una fila por archivo, al versionarlo) |

Los datos de la campaña se citan desde `evaluation/data/README.md`, que describe el resto de esta jerarquía.

## Referencia in-sample de la validación fuera de muestra (c-166)

La corrida in-sample de referencia es la de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, copia congelada del cache de v9 (`generated_at` `2026-10-07T22:22:01Z`; evidencia publicada en `fec4c42`, c-143). El análisis de c-167 la compara con `predicciones_independiente.json` y recibe estos valores como parámetro (`pines_in_sample`). Esta sección usa el formato `- campo: valor`, con nombres distintos de los de la procedencia de la tabla primaria.

- classifier_version_in_sample: hybrid-v3
- commit_in_sample: no registrado en la generación (2026-10-07); evidencia publicada en fec4c42 (c-143)
- pines_in_sample: google_genai >=2.20.0 (rango declarado, versión instalada no registrada); modelo gemini-3.6-flash

Valor del parámetro `pines_in_sample` de c-167 (el `google_genai` del in-sample es un **rango declarado**, no una versión instalada):

```json
{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}
```

### Fuentes de los pines

1. **`openspec/config.yaml`, `stack.inference`**: hoy declara `Gemini 3.6 Flash (google-genai >=2.33,<3)`. El modelo coincide con el de v9; el rango de `google-genai` es el de la configuración **entregada** (`v1.2.7`), no el de la corrida in-sample.
2. **Anexo B de la tesis (v10), Tabla "Configuración evaluada y configuración entregada"** (`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`, etiqueta `tab:configuracion-evaluada-entregada`): la configuración evaluada es la del commit `d6bb474` (2026-10-07), con `google-genai >=2.20.0`, y el modelo `gemini-3.6-flash` figura "sin cambios" entre la evaluada y la entregada.

Verificación contra el commit evaluado: `git show d6bb474:App/Backend/requirements.txt` declara `google-genai>=2.20.0`, `git show d6bb474:App/Backend/app/config/settings.py` fija `gemini_model = "gemini-3.6-flash"` y `git show d6bb474:App/Backend/app/constants.py` fija `HYBRID_CACHE_VERSION = "hybrid-v3"`. En ese mismo commit `openspec/config.yaml` todavía decía `Gemini 2.5 Flash (google-genai >= 1.0)`: la fuente 1 se actualizó después y **no describe** la corrida de v9.

**Discrepancia declarada**: las dos fuentes difieren en el rango de `google-genai` (`>=2.20.0` evaluada frente a `>=2.33,<3` entregada). Para v9 vale la evaluada (fuente 2 y `git show d6bb474`); el rango de `openspec/config.yaml` es el vigente y se usa para el cache independiente solo como contexto.

### Limitación declarada

La evidencia congelada no registró `commit` ni `pines`: su `cache_meta` trae solo `corpus_hash`, `corpus_count`, `classifier_version` y `generated_at`. Por eso:

- La comparabilidad in-sample/out-of-sample se verifica por `classifier_version` idéntico (`hybrid-v3`) y por `pines`: el `modelo` debe coincidir exactamente. El in-sample solo conserva el **rango** declarado de `google-genai`, mientras que el cache independiente registra la versión **instalada**: la igualdad exacta de versiones instaladas no es verificable, y lo comprobable es que la versión del cache independiente cumpla el rango del in-sample; esa versión se informa junto con los resultados.
- El `commit` es obligatorio solo en el cache independiente (se registra con `git rev-parse --short HEAD` al generarlo y la corrida falla antes de clasificar si no puede obtenerse). En el in-sample no se puede recuperar el commit de generación: solo se sabe que la cascada `hybrid-v3` está versionada desde `d6bb474` y que la evidencia se publicó en `fec4c42`.

## Export de intervenciones (c-165)

`intervenciones.csv` es el dataset de intervención humana de la campaña: lo produce `App/Backend/scripts/exportar_intervenciones.py` a partir de `clasificacion_log` y lo lee c-167 para la `tasa_intervencion_humana` y la proporción de tiempo. No contiene datos personales: el actor es un alias derivado con clave. El protocolo (cuándo y cómo se produce y cómo se verifica) está en `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`.

Columnas, en este orden: `id_caso, incidente_id, log_id, origen_intervencion, intervencion_inicio_en, validado_en, duracion_s, sector_predicho, sector_validado, cambio_sector, actor_alias`.

- Una fila por log **intervenido** (`validado_en` no nulo), ordenada por `log_id`. Los logs legados (sector validado sin `validado_en`, anteriores a la migración 024) no se exportan: el resumen del comando informa cuántos quedaron afuera.
- `id_caso` sale del sidecar de la corrida (`case_id`) por `incidente_id`; queda vacío si el incidente no figura en los sidecars o figura en dos casos distintos. El denominador de la tasa **no** sale de este archivo: c-167 lo toma de `plan_campana.csv` o del sidecar de la corrida.
- `intervencion_inicio_en` y `validado_en` son ISO-8601 en UTC con zona (`+00:00`). `duracion_s` es `validado_en - intervencion_inicio_en` en segundos; queda vacía si falta el inicio o si da negativa (reloj del cliente adelantado).
- `cambio_sector` es `true` o `false` (un sector predicho nulo cuenta como cambio). `origen_intervencion` es `gate`, `muestreo` o `rederivacion`; `completado_manual` está reservado y no tiene escritor.
- `actor_alias` es el HMAC-SHA256 del id del empleado con la clave de la variable de entorno `INTERVENCION_EXPORT_HMAC_KEY`, truncado a 12 hex; vacío si no hay actor. La clave es secreta, no se versiona ni se imprime, y debe ser **la misma** en todas las corridas de la campaña para que el alias sea estable. El archivo no trae nombre, email, teléfono, legajo ni el id del empleado.

Comando (desde `App/Backend`, con la variable definida en el entorno de esa terminal):

```bash
python -m scripts.exportar_intervenciones \
  --sidecar ../../evaluation/data/campana/sidecar_<id_corrida>.json \
  --desde AAAA-MM-DD --hasta AAAA-MM-DD \
  --salida ../../evaluation/data/campana/intervenciones.csv
```

`--sidecar` se repite una vez por corrida y `--desde`/`--hasta` acotan los logs por su `created_at` (días de negocio, ambos inclusivos). El comando se niega a escribir sobre `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`, `evaluation/predicciones.json` y `evaluation/evidence/`.

Procedencia del export (completar **al versionar** `intervenciones.csv`; formato `- campo: valor`, con nombres propios para no mezclarse con los de la tabla primaria):

- intervenciones_archivo: evaluation/data/campana/intervenciones.csv
- intervenciones_sha256: pendiente
- intervenciones_fecha: pendiente
- intervenciones_comando: pendiente
- intervenciones_rango: pendiente
- intervenciones_legados_excluidos: pendiente

| Archivo | SHA-256 |
|---|---|
| `intervenciones.csv` | pendiente |

### Planilla del brazo manual (c-165)

`brazo_manual.csv` es la planilla del brazo manual (`tarea = brazo_manual`, operadores `O1` y `O2`, con `inicio` y `timestamp` obligatorios en cada fila) que pasó `python -m evaluation.doble_etiquetado --planilla evaluation/data/campana/brazo_manual.csv --corpus data/corpus_evaluacion_pseudonimizado.json --tarea brazo_manual` con exit code `0`. El procedimiento (sujetos, reparto, plan, aceptación) está en `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`. No contiene datos personales: solo alias de operador, identificadores de caso, sectores canónicos y marcas de tiempo. Mientras no exista, su hash y los desvíos quedan en `pendiente`.

- brazo_manual_desvios_informados: pendiente

| Archivo | SHA-256 |
|---|---|
| `brazo_manual.csv` | pendiente |

## Entradas del análisis de campaña (c-170)

El análisis de solo lectura de c-167 (`evaluation/analisis_campana.py`) espera dos entradas en esta carpeta que ningún runbook producía. Las ensambla `evaluation/preparar_entradas_analisis.py` (offline, TDD), el único camino documentado para generarlas:

```bash
python -m evaluation.preparar_entradas_analisis \
  --entrada evaluation/data/campana \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json
```

| Entrada | Qué es | Procedencia (fuente) |
|---|---|---|
| `plantilla_etiquetado.csv` | Unión C1, bajo un único encabezado, de `doble_etiquetado.csv` (`tarea = doble_etiquetado`) y `brazo_manual.csv` (`tarea = brazo_manual`), en el orden de origen; LF y UTF-8 sin BOM | `evaluation/data/campana/doble_etiquetado.csv` + `evaluation/data/campana/brazo_manual.csv`, re-validadas por tarea con `python -m evaluation.doble_etiquetado` |
| `predicciones_in_sample.json` | Copia **byte a byte** del cache congelado de v9 (referencia in-sample); la fuente es de solo lectura y nunca se regenera | `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` |

El helper escribe LF sin BOM, imprime el SHA-256 de cada salida y su procedencia (fuente y hash de la fuente), y aborta con un error accionable que nombra el archivo (y la `tarea`) si una fuente falta o no pasa el validador. Se niega a escribir sobre un artefacto congelado, sobre `evaluation/evidence/**` o sobre sus propias fuentes. Con las mismas fuentes, dos corridas producen salidas byte a byte idénticas; por eso `predicciones_in_sample.json` comparte el SHA-256 de la fuente congelada.

SHA-256 y procedencia (completar **al versionar** la campaña, formato `- campo: valor`):

- entradas_analisis_planilla_archivo: evaluation/data/campana/plantilla_etiquetado.csv
- entradas_analisis_planilla_sha256: pendiente
- entradas_analisis_planilla_fuentes: doble_etiquetado.csv + brazo_manual.csv (sus SHA-256 en las filas de arriba)
- entradas_analisis_in_sample_archivo: evaluation/data/campana/predicciones_in_sample.json
- entradas_analisis_in_sample_sha256: pendiente (debe coincidir con el de evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json)
- entradas_analisis_fecha: pendiente
- entradas_analisis_comando: `python -m evaluation.preparar_entradas_analisis --entrada evaluation/data/campana --corpus data/corpus_evaluacion_pseudonimizado.json --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`

### Recomendación: enmendar el gate de c-169 (tarea 0.2)

El gate de la campaña de c-169 (tarea 0.2) exige hoy `doble_etiquetado.csv`, `plan_campana.csv`, `intervenciones.csv`, `registro_sujetos.csv` y `analisis/` con las salidas de c-167, pero **no** las dos entradas nuevas. Como el análisis de c-167 no se puede correr end-to-end sin `plantilla_etiquetado.csv` y `predicciones_in_sample.json` (ambas declaradas "Entradas esperadas" en `analisis/README.md`), el gate SHOULD exigirlas también (con su SHA-256 coincidente). Esta recomendación es un seguimiento de c-170: **no** se edita c-169.
