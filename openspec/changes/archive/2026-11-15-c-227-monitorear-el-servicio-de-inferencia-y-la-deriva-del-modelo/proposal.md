# Proposal: Monitorear el servicio de inferencia y la deriva del modelo

## Why

Las limitaciones 3 y 4 del estudio declaran dos riesgos operativos intrinsecos al enfoque basado en un modelo de lenguaje externo: la dependencia de un servicio externo de inferencia (Gemini) y la dependencia de la version especifica del modelo (`gemini-3.6-flash`, integrada al clasificador el 24 de septiembre de 2026). La discusion exige gestionar esa dependencia "como un riesgo operativo" y la limitacion 4 aconseja "un regimen de monitoreo continuo de las metricas de clasificacion" (\autoref{subsec:limitaciones-estudio}).

Hoy el clasificador esta cableado a un unico proveedor: `GeminiClassifier` importa `google-genai` y el `HybridClassifier` solo conoce la implementacion concreta. No existe ningun artefacto que detecte un deterioro del servicio ni un cambio de comportamiento del modelo alojado. Un recambio de proveedor o de version de modelo exigiria editar el codigo del clasificador.

Este change responde a esas dos limitaciones con una capa de abstraccion del proveedor y un monitoreo periodico de la deriva, sin medir de nuevo y sin tocar ningun numero canonico.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Abstraccion del proveedor** | Interfaz abstracta del proveedor de inferencia (`App/Backend/app/classifiers/provider.py`) de la que depende el `HybridClassifier`; el `GeminiClassifier` pasa a ser una implementacion detras de ella. La seleccion de proveedor y de version de modelo queda por configuracion (`Settings`) con el proveedor y el modelo vigentes por defecto, de modo que el comportamiento con la configuracion actual NO cambia. | MEDIUM |
| **B. Conjunto canario y job de reevaluacion** | Conjunto canario fijo y versionado (`evaluation/data/canario/`), disjunto del corpus de ajuste, con su linea de base congelada de metricas; y un job offline (`evaluation/monitoreo/`) que recalcula las metricas del clasificador sobre el canario y detecta deriva contra la base. | MEDIUM |
| **C. Umbrales de alerta y fallback documentado** | Umbrales (piso) por metrica monitoreada, configurables sin recompilar; la alerta cuando una metrica cae bajo su piso; y la documentacion operativa del fallback al filtro deterministico con revision humana cuando el servicio no esta disponible. | LOW/MEDIUM |
| **D. Trazabilidad** | Procedimiento de monitoreo en `docs/operational-guide.md` y registro de cada corrida del job con su proveedor, su modelo y sus hashes. | LOW |

**No objetivos.**

- No cambia ningun numero canonico ni la cifra primaria (`0,6893` de exactitud estricta, `0,6508` de F1 macro): el monitoreo es senal operativa, no medicion nueva.
- No sobrescribe `evaluation/evidence/` ni ningun artefacto congelado; la linea de base del canario es un archivo nuevo y aditivo.
- No invoca al proveedor pago sin confirmacion explicita (`--confirm-paid` o `EVALUATION_CONFIRM_PAID=1`).
- No cambia el contrato del clasificador con el proveedor por defecto: los cinco sectores canonicos, el prompt, los parametros y el esquema de resultado permanecen.
- No implementa un proveedor alternativo real; la abstraccion habilita el recambio, pero evaluar modelos abiertos queda como trabajo futuro.
- No modifica el clasificador deterministico, el vocabulario ni las reglas del prompt.
- No toca `n8n/`, la guarda de costo, la configuracion de despliegue ni el corpus de evaluacion.

## Capabilities

### New Capabilities

- `inference-provider-abstraction`: interfaz del proveedor de inferencia, seleccion de proveedor y modelo por configuracion, y neutralidad por defecto del contrato canonico.
- `model-drift-monitoring`: conjunto canario fijo, job de reevaluacion offline, deteccion de deriva, umbrales de alerta y fallback documentado.

### Modified Capabilities

Ninguna. La resiliencia ante fallas transitorias del proveedor ya esta especificada en `classification-resilience` y este change NO la modifica: la referencia como fallback vigente. Tampoco se modifica `evaluation-framework`: el job reutiliza sus metricas y su gate de corrida paga sin cambiar su contrato.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `App/Backend/app/classifiers/provider.py` | Nuevo | Interfaz abstracta del proveedor de inferencia y su taxonomia de errores |
| `App/Backend/app/classifiers/gemini_classifier.py` | Modificado | Pasa a implementar la interfaz; la logica de reintento y validacion se conserva |
| `App/Backend/app/classifiers/hybrid.py` | Modificado | Depende de la interfaz, no del SDK del proveedor |
| `App/Backend/app/config/settings.py` | Modificado | Proveedor y modelo por configuracion; defaults iguales a los vigentes |
| `evaluation/data/canario/` | Nuevo | Conjunto canario versionado y linea de base congelada |
| `evaluation/monitoreo/` | Nuevo | Job de reevaluacion, deteccion de deriva y umbrales, con sus pruebas |
| `docs/operational-guide.md` | Aditivo | Procedimiento de monitoreo y fallback documentado |

Sin cambios en `n8n/`, el corpus de evaluacion, las predicciones canonicas ni la evidencia congelada.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Que la abstraccion altere el resultado con la configuracion por defecto | Baja | Prueba de neutralidad: el proveedor por defecto reproduce caso por caso las predicciones del clasificador vigente; la linea de base del canario no cambia |
| Que el job escriba sobre la evidencia congelada o un numero canonico | Media | Escritura restringida a rutas nuevas y fechadas; verificacion de que `evaluation/evidence/` queda byte a byte identica |
| Que la corrida paga se dispare sin confirmacion | Baja | El job reutiliza el gate de corrida paga del framework; sin `--confirm-paid` aborta sin invocar al proveedor |
| Que el canario se contamine con el corpus de ajuste | Media | El canario se toma del conjunto independiente, es fijo y se declara no apto para ajuste |
| Deriva real no detectada por un umbral mal fijado | Media | Los pisos se fijan contra la linea de base congelada con una tolerancia declarada y quedan configurables |

## Rollback Plan

`git revert` del commit del change. La interfaz y su implementacion son aditivas; volver el `HybridClassifier` y el `GeminiClassifier` a su forma previa restaura el acoplamiento directo sin tocar el contrato. El canario y el job son archivos nuevos que se retiran sin afectar artefactos previos. Ningun numero canonico ni la evidencia congelada se modifican, de modo que el rollback no deja huecos numericos.

## Dependencies

- `classification-resilience` (fallback y reintento acotado, como comportamiento vigente que el fallback documentado referencia).
- `evaluation-framework` y `evaluation-prediction-cache` (metricas, gate de corrida paga y cache de predicciones que el job reutiliza sin modificar).
- `evaluation-out-of-sample-validation` (corpus independiente del que se toma el conjunto canario).
- No depende de c-228 ni de c-229.

## Success Criteria

- [ ] El `HybridClassifier` depende de la interfaz del proveedor y una implementacion falsa se inyecta sin importar el SDK del proveedor.
- [ ] Con la configuracion por defecto, el clasificador reproduce las predicciones vigentes caso por caso y no se altera ningun numero canonico.
- [ ] El job reproduce la linea de base del canario desde la evidencia congelada sin invocar al proveedor, y aborta sin `--confirm-paid` cuando la corrida es paga.
- [ ] Una degradacion simulada de una metrica por encima de la tolerancia se reporta como deriva; sin cambio, no se reporta deriva.
- [ ] Los umbrales se ajustan por configuracion sin recompilar y una metrica bajo su piso emite una alerta con el fallback documentado.
- [ ] `evaluation/evidence/` queda byte a byte identica tras una corrida del job.
- [ ] `openspec validate c-227-monitorear-el-servicio-de-inferencia-y-la-deriva-del-modelo --strict` pasa.
