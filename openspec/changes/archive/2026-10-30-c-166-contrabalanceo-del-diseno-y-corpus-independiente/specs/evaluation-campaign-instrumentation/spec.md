## Purpose

Instrumentar la campaña de medición de modo que el efecto de orden del operador humano sea estimable, mediante un plan por caso que contrabalancea el orden de condición (manual-primero frente a automatizado-primero), y que las métricas de clasificación puedan obtenerse sobre un corpus independiente sin tocar los artefactos congelados de la v9.

## ADDED Requirements

### Requirement: ECM-004 — Plan de campaña por caso y contrabalanceo de condición

El proyecto SHALL proveer en `evaluation/plan_campana.py` una función pura `generar_plan_campana(casos, modo, seed)` que componga `ordenar_casos(casos, modo, seed)` (modos `directo`, `inverso`, `alternado`, `aleatorio`) y asigne a cada caso `id_caso`, `posicion` (1..n), `mitad` (1 o 2), `brazo_primero` (`manual` o `automatizado`), `modo` y `seed`. El contrabalanceo SHALL ser de CONDICIÓN: dentro de cada mitad, la cantidad de casos `manual`-primero y `automatizado`-primero MUST diferir en a lo sumo 1. Con N impar, la primera mitad SHALL tener ⌊n/2⌋ casos y la segunda ⌈n/2⌉. El modo `aleatorio` MUST requerir semilla y, con la misma semilla y los mismos casos, MUST producir el mismo plan. El plan SHALL exportarse a CSV UTF-8 con separador `,` (`evaluation/data/campana/plan_campana.csv`). Los harnesses `scripts/corpus_ingest/ingest_via_n8n.py` y `scripts/corpus_ingest/ingest_corpus.py` SHALL aceptar `--plan <csv>` y enviar en el orden de `posicion`, y `--orden/--seed` como atajo que genera el plan y lo escribe junto al sidecar; `scripts/corpus_ingest/ingest_telefonia_corpus.py` no ingesta y, con `--plan`, SHALL limitarse a copiar `posicion`, `mitad` y `brazo_primero` al sidecar. `CaseResult` y `CorpusResult` SHALL recibir al final, con default `None`, los campos `orden`, `posicion`, `mitad`, `brazo_primero` e `id_corrida`. `--limit` SHALL aplicarse antes del orden. Ninguna de estas operaciones MUST requerir servicios externos para ser verificada.

#### Scenario: Plan balanceado por mitad

- **WHEN** se genera el plan de 200 casos con cualquier modo
- **THEN** cada mitad tiene 100 casos, 50 con `brazo_primero` igual a `manual` y 50 con `automatizado`, y `verificar_balance` pasa

#### Scenario: N impar documentado

- **WHEN** se genera el plan de 7 casos
- **THEN** la mitad 1 tiene 3 casos y la mitad 2 tiene 4, y en cada mitad la diferencia entre `manual` y `automatizado` es a lo sumo 1

#### Scenario: Plan reproducible con semilla

- **WHEN** se genera dos veces el plan con `modo` `aleatorio` y la misma semilla sobre los mismos casos
- **THEN** ambos planes son idénticos fila por fila y cada fila registra la semilla

#### Scenario: Aleatorio sin semilla falla

- **WHEN** se pide un plan o un harness con `aleatorio` sin semilla
- **THEN** la operación termina con un error que indica pasar `--seed` y no se genera plan ni se envía ningún caso

#### Scenario: El límite se aplica antes del orden

- **WHEN** un harness corre con `--orden inverso --limit 3`
- **THEN** procesa el reverso de los tres primeros casos del corpus, no los tres últimos

#### Scenario: El harness sigue el plan y registra la asignación

- **WHEN** `ingest_via_n8n.py` o `ingest_corpus.py` corren con `--plan` e `--id-corrida`
- **THEN** envían los casos en orden de `posicion` y cada entrada del sidecar registra `posicion`, `mitad`, `brazo_primero`, `orden` e `id_corrida`

#### Scenario: Telefonía copia el plan sin ingestar

- **WHEN** `ingest_telefonia_corpus.py` corre con `--plan`
- **THEN** recupera las mediciones por `corpus_case_id` como antes y copia `posicion`, `mitad` y `brazo_primero` del plan al sidecar, sin decidir el orden de las llamadas

#### Scenario: Sidecars históricos siguen válidos

- **WHEN** se lee o se mergea un sidecar previo que no tiene los campos nuevos
- **THEN** se procesa sin errores y los campos ausentes valen `None`

### Requirement: ECM-005 — Protocolo de campaña contrabalanceada registrado

El proyecto SHALL incluir el runbook versionado `docs/campana-medicion/runbook-campana-contrabalanceada.md` que defina cómo se genera y verifica el plan, cómo se reparten los casos por `brazo_primero` dentro de cada mitad, cómo el operador manual sigue el plan fuera del repositorio, qué registra en la planilla de c-168 con `tarea` igual a `brazo_manual` (`inicio` en ISO-8601 al tomar el caso y `timestamp` al asignar el sector, de modo que `timestamp - inicio` es la duración por caso), con qué flags se corren los harnesses, y un criterio de aceptación explícito: contrabalanceo efectivo registrado por caso. Los operadores del brazo manual MUST ser distintos de los etiquetadores del doble etiquetado, de los dos analistas originales y de los autores. El runbook MUST NOT depender de datos de campo ya recolectados y SHALL delegar la estimación del efecto de orden a c-167.

#### Scenario: El operador sigue el plan

- **WHEN** un operador ejecuta el brazo manual según el runbook
- **THEN** procesa los casos en orden de `posicion`, en el turno que indica `brazo_primero`, y registra cada caso en la planilla con `tarea` igual a `brazo_manual`, `inicio` al tomar el caso y `timestamp` al asignar el sector

#### Scenario: Contrabalanceo efectivo registrado por caso

- **WHEN** se cierra la campaña
- **THEN** cada caso tiene `posicion`, `mitad` y `brazo_primero` en el sidecar y su registro manual, la asignación realizada coincide con el plan y `verificar_balance` pasa

#### Scenario: Estimación del efecto de orden delegada a c-167

- **WHEN** un autor consulta cómo estimar el efecto de orden
- **THEN** el runbook remite al análisis de c-167, que parea por caso las mediciones de las distintas corridas y toma la posición del plan

### Requirement: ECM-006 — Corpus independiente sin solape con el corpus de ajuste

El proyecto SHALL proveer `evaluation/no_solape.py::verificar_no_solape(ajuste, candidato)` y el runbook `docs/campana-medicion/runbook-corpus-independiente.md`. Los ids del corpus independiente MUST llevar el prefijo `I` (`I001..`). La verificación MUST fallar de forma accionable, nombrando el caso, si un id del candidato no tiene el prefijo, si un id aparece en ambos corpus o si coincide el SHA-256 de la descripción normalizada (NFKC, minúsculas, espacios colapsados); la similitud Jaccard de tokens por encima de un umbral SHALL reportarse como advertencia. La verificación SHALL declarar que no detecta paráfrasis y MUST ejecutarse como paso previo obligatorio antes de clasificar el corpus independiente. El corpus independiente SHALL pseudonimizarse con el mismo protocolo que el de ajuste y doble-etiquetarse con la plantilla y el validador de c-168, y SHALL clasificarse con el clasificador CONGELADO (`classifier_version` y commit iguales a los del in-sample), sin recalibrar tau, prompt ni vocabulario después de ver el corpus.

#### Scenario: Prefijo obligatorio

- **WHEN** un caso del corpus candidato tiene un id sin el prefijo `I`
- **THEN** la verificación falla y nombra ese caso

#### Scenario: Mismo caso con otro id bloquea la corrida

- **WHEN** un caso del candidato tiene un id nuevo pero su descripción normalizada coincide con la de un caso de ajuste
- **THEN** la verificación falla identificando ambos casos y no se clasifica el corpus independiente

#### Scenario: Corpus disjunto habilita la medición

- **WHEN** el candidato no comparte ids ni descripciones normalizadas con el corpus de ajuste
- **THEN** la verificación pasa, devuelve las advertencias de similitud si se pidió umbral, y la clasificación puede proceder

#### Scenario: Mismo protocolo y clasificador congelado

- **WHEN** se prepara y clasifica el corpus independiente según el runbook
- **THEN** se aplican la misma pseudonimización, la plantilla y el validador de c-168 y el clasificador con el mismo `classifier_version` y commit que el in-sample, sin recalibración posterior

### Requirement: ECM-007 — Protección de los artefactos congelados en la campaña y en el corpus independiente

Las corridas de campaña y la clasificación del corpus independiente MUST NOT escribir sobre los artefactos de la v9. Los harnesses SHALL abortar con error accionable, antes de enviar nada, si con `--plan` u `--orden` el `--json` o el `--sidecar` apuntan a `data/corpus_evaluacion_pseudonimizado.json` o a cualquier `data/corpus_resultados*.json`; con `--plan`, `--sidecar` SHALL ser obligatorio y propio de la corrida. `evaluation/run_evaluation.py` SHALL aceptar `--corpus`, `--predicciones` y `--reporte`; si `--corpus` no es el canónico, `--predicciones` y `--reporte` SHALL ser obligatorios y el runner MUST abortar si apuntan a `evaluation/predicciones.json` o `evaluation/report.md`. Las predicciones del corpus independiente SHALL guardarse separadas (`evaluation/data/campana/predicciones_independiente.json`) y su `cache_meta` SHALL incluir, además de `corpus_hash`, `corpus_count`, `classifier_version` y `generated_at`, los campos `commit` (hash corto de `HEAD` al generar) y `pines` (versión de `google-genai` y modelo); si el commit o los pines no pueden obtenerse, la corrida MUST fallar antes de escribir. El README de `evaluation/data/campana/` SHALL registrar `classifier_version`, `commit_in_sample` y `pines_in_sample` (versión de google-genai y modelo de v9, citando `openspec/config.yaml` `stack.inference` y la Tabla de configuración evaluada del Anexo B) de la corrida in-sample de referencia; como la copia congelada de v9 no registró commit, la comparabilidad SHALL verificarse por `classifier_version` y `pines` idénticos, y el commit es obligatorio solo en el cache independiente. El reporte out-of-sample es de c-167.

#### Scenario: Abort por json congelado

- **WHEN** un harness corre con `--plan` y `--json` apunta a `data/corpus_evaluacion_pseudonimizado.json`, o lo deja en su default
- **THEN** termina con código distinto de cero, nombra el archivo y la ruta de campaña a usar, y no envía ningún caso

#### Scenario: Abort por sidecar versionado

- **WHEN** un harness corre con `--plan` y `--sidecar` apunta a un `data/corpus_resultados*.json`
- **THEN** termina con error accionable sin enviar ni escribir nada

#### Scenario: Abort por predicciones o reporte canónicos

- **WHEN** `run_evaluation.py` corre con un `--corpus` no canónico y `--predicciones` apunta a `evaluation/predicciones.json` o `--reporte` a `evaluation/report.md`, o alguno de los dos falta
- **THEN** aborta antes de construir el clasificador y no modifica ningún archivo

#### Scenario: Predicciones independientes separadas

- **WHEN** se clasifica el corpus independiente con rutas propias
- **THEN** las predicciones quedan en `evaluation/data/campana/predicciones_independiente.json` y `evaluation/predicciones.json` y `evaluation/report.md` no cambian

#### Scenario: Procedencia completa del cache independiente

- **WHEN** se clasifica el corpus independiente con rutas propias
- **THEN** el `cache_meta` de `predicciones_independiente.json` trae `classifier_version`, `commit` y `pines` además de `corpus_hash`, `corpus_count` y `generated_at`

#### Scenario: Cache sin commit falla antes de escribir

- **WHEN** al clasificar el corpus independiente no se puede obtener el commit o los pines
- **THEN** la corrida termina con error accionable antes de invocar al clasificador y no escribe el archivo de predicciones

#### Scenario: Sin flags nuevos la conducta no cambia

- **WHEN** los harnesses o `run_evaluation.py` corren sin los flags nuevos
- **THEN** se comportan exactamente como antes de este change
