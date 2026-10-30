## Context

Ver `proposal.md` (Why). Estado actual verificado contra el código (rama de enmiendas, 2026-10-30):

- **Ningún harness tiene orden ni plan.** `scripts/corpus_ingest/ingest_via_n8n.py`: `parse_args` (:1145), `select_cases` (:575) filtra por canal y aplica `limit` sobre el orden del corpus, `CaseResult` (:519-541) es un dataclass SIN defaults construido en `ingest_via_n8n.py:809` y `:852`, `ingest_telefonia_corpus.py:133` y en los tests (`test_ingest_via_n8n.py:359`, `:453`); `write_sidecar_json` (:728) mergea por `case_id` (una segunda corrida al mismo archivo pisa la primera para los casos válidos); `run` (:1213) llama a `merge_evaluation_json(args.json, ...)` (:1339) y `--json` tiene default `data/corpus_evaluacion_pseudonimizado.json` (:70): una corrida de campaña con defaults pisaría los tiempos canónicos.
- `scripts/corpus_ingest/ingest_corpus.py` NO usa `CaseResult`: tiene su propio `CorpusResult` (:190-205), `_select_cases` (:507, mismo `limit` previo a todo), `write_sidecar_json` (:358) que **sobrescribe** el archivo completo y default de sidecar `data/corpus_resultados.json` (:69, versionado). No tiene `--json`: escribe los tiempos en `--csv`/`--xlsx`.
- `scripts/corpus_ingest/ingest_telefonia_corpus.py` **no ingesta**: recupera la medición de cada caso por `corpus_case_id` desde un endpoint (:159-190) y construye un `ivn.CaseResult` (:133). El orden de las llamadas lo decide el operador del softphone (`scripts/voip_softphone/test_softphone_html.py:153-156`: la página envía `corpus_case_id` solo si el operador lo eligió). Sí **escribe**: sidecar (default `data/corpus_resultados_telefonia.json`, :67, versionado), CSV/XLSX y `merge_evaluation_json` sobre `--json` (`write_back` :229-254).
- Archivos versionados bajo `data/` (`git ls-files`): `corpus_evaluacion_pseudonimizado.json`, `corpus_resultados.json`, `corpus_resultados_telefonia.json` y el CSV pseudonimizado. `data/corpus_resultados_n8n.json` (default de `ingest_via_n8n.py`, :73) está gitignorado por el patrón `data/corpus_resultados*.json`, igual que los originales `data/Corpus Tesis.xlsx` y `data/Corpus Tesis - Hoja 1.csv` (defaults de `--xlsx/--csv`, con PII).
- `evaluation/run_evaluation.py`: `main()` (:1523) no tiene `--corpus`, `--predicciones` ni `--reporte`; llama a `main_con_corpus_real` (:1376), que ya acepta `corpus_path`, `report_path` y `predicciones_path` con defaults `CORPUS_REAL_PATH` (:81), `REPORT_PATH` (:82) y `PREDICCIONES_PATH` (:83). Correrlo contra otro corpus invalida el cache (hash distinto), dispara la corrida paga sujeta a `--confirm-paid` y sobrescribe `evaluation/predicciones.json` y `evaluation/report.md`.
- `evaluation/corpus.py`: `cargar_corpus` (:183) no valida el formato del `id` (acepta `I001`), `SECTORES_CANONICOS` (:52-58). `evaluation/metrics.py` usa `random.Random(semilla)` (:464, :519) con `SEMILLA_BOOTSTRAP = 20261021` (:379): mismo patrón de reproducibilidad que adopta el plan.
- `evaluation/deterministic_measurement.py` solo hace cross-fitting WITHIN-corpus para tau; no cubre validación out-of-sample. Se conserva sin cambios.
- CI (`.github/workflows/ci.yml`) corre el backend, `scripts/preflight` y `evaluation/` (`working-directory: evaluation`, `pytest`). Las suites de `scripts/corpus_ingest/` (`test_*.py` junto al código, sin subcarpeta `tests/`) NO están en el gate.

## Goals / Non-Goals

**Goals:**
- Un plan de campaña por caso, puro y reproducible, que contrabalancee el **orden de condición** (manual-primero vs automatizado-primero) y deconfunda mitad y orden.
- Que los harnesses sigan el plan y registren por caso `posicion/mitad/brazo_primero/id_corrida`, sin poder pisar lo congelado.
- Una ruta segura para clasificar un corpus independiente con el clasificador congelado y guardar sus predicciones aparte.
- Que todo el TDD de este change quede en CI.

**Non-Goals:**
- Ejecutar la campaña o recolectar datos (c-169 documenta resultados).
- Estimar el efecto de orden o reportar métricas out-of-sample (c-167: `evaluar_fuera_de_muestra` y el análisis del efecto de orden).
- Definir la planilla de etiquetado o su validador (c-168).
- Reemplazar el cross-fitting within-corpus de tau; cambiar contratos de `corpus-n8n-ingest`, cadenas de categorías o números canónicos.

## Decisions

### D1. Por qué el efecto de orden que importa es el del operador

La tesis (`04-marco-metodologico.tex:14`) motiva el diseño secuencial por "el efecto de aprendizaje del operador humano sobre el corpus" y reconoce que mitad y operador quedaron colineales. La KB (`11_evaluacion_experimental.md:56`) define el contrabalanceo como "una mitad procesada primero manual, la otra primero automatizada". El humano participa en ambos brazos: procesa el caso a mano en el brazo manual y valida/corrige la clasificación en el brazo automatizado (instrumento de c-165). Por eso lo que hay que aleatorizar es **qué brazo ve primero cada caso**, no el orden en que una máquina recibe los envíos. Alternativa descartada: `--orden` como reordenamiento del brazo automatizado (versión anterior de este change), que no produce efecto de orden estimable y cuyo campo `orden` guardaba el modo, idéntico para todos los casos.

### D2. Plan de campaña (contrato C6)

- **Ubicación**: `evaluation/plan_campana.py`. Motivo: CI ya corre `evaluation/` y el plan es metodología de evaluación, no I/O de ingesta. Los harnesses de `scripts/corpus_ingest/` lo importan agregando la raíz del repo a `sys.path` (patrón ya usado en `scripts/corpus_ingest/test_ingest_telefonia_corpus.py:20-24` y `pseudonymize_corpus.py:40-49`, que agrega `App/Backend`). Alternativa descartada: `scripts/corpus_ingest/plan_campana.py` (fuera de CI hasta que exista el job nuevo, y obligaría a `evaluation/` a importar de `scripts/`).
- **`ordenar_casos(casos, modo, seed) -> list[T]`**: genérica sobre los elementos (los harnesses la llaman con sus `Case`/`CorpusCase`; el plan, con ids). `directo` preserva; `inverso` invierte; `alternado` intercala mitades (1, ⌊n/2⌋+1, 2, ⌊n/2⌋+2, ...); `aleatorio` usa `random.Random(seed).shuffle` sobre una copia. Modo desconocido: `ValueError` que lista los modos válidos.
- **`aleatorio` sin semilla**: `ValueError` accionable ("el modo aleatorio exige --seed <entero>; registrá la semilla en el plan"). En los otros modos la semilla no tiene efecto y la columna `seed` queda vacía.
- **N impar**: la primera mitad tiene ⌊n/2⌋ casos y la segunda ⌈n/2⌉ (el caso medio va a la segunda mitad). En `alternado` el último elemento es de la segunda mitad. N = 1 da un único caso en mitad 2; N = 0 da un plan vacío.
- **`generar_plan_campana(casos, modo, seed) -> list[AsignacionCaso]`**: `casos` es la secuencia de `id_caso` (= `id` del corpus). Compone `ordenar_casos` y asigna `posicion` 1..n según el orden resultante, `mitad = 1` si `posicion <= n // 2` y `2` si no, y `brazo_primero = manual` en posiciones impares y `automatizado` en pares. `AsignacionCaso` es un dataclass congelado con `id_caso, posicion, mitad, brazo_primero, modo, seed`. Con `n = 200`: 50/50 en cada mitad. Con n impar, cada mitad difiere en a lo sumo 1 caso. La aleatorización de qué caso cae en qué brazo la aporta el modo (`aleatorio` con semilla es el recomendado para la campaña). Ids repetidos: `ValueError`.
- **`verificar_balance(plan)`**: cuenta `mitad × brazo_primero` y falla si en alguna mitad la diferencia supera 1. Es el criterio de aceptación ejecutable del contrabalanceo.
- **Export y lectura**: `escribir_plan_csv(plan, ruta)` y `leer_plan_csv(ruta)` (UTF-8, separador `,`, encabezado `id_caso,posicion,mitad,brazo_primero,modo,seed`). `leer_plan_csv` valida columnas, posiciones contiguas 1..n, ids únicos y valores de `mitad`/`brazo_primero`. Ruta canónica: `evaluation/data/campana/plan_campana.csv`.
- **Sub-planes por turno**: `subplan(plan, mitad, brazo, turno)` devuelve las filas de esa mitad donde `brazo` va en ese turno (turno 1: `brazo_primero == brazo`; turno 2: el otro), conservando la `posicion` global. Así el harness y el operador ejecutan, dentro de cada mitad, primero los casos donde su brazo va primero y después el resto, sin que el harness tenga que conocer la lógica de turnos. CLI: `python -m evaluation.plan_campana generar|subplan ...`.

### D3. Harnesses y sidecar (contrato C8)

- **`--plan <csv>`** en `ingest_via_n8n.py` e `ingest_corpus.py`: los casos se envían en el orden de `posicion` del plan (o del sub-plan); un `id_caso` del plan ausente del corpus aborta antes de enviar. Los canales no ingestables siguen omitiéndose como hoy (`INGESTABLE_CHANNELS`). El `id_caso` del plan se mapea al `case_id` del sidecar (mismo valor).
- **`--orden/--seed`** son un atajo: generan el plan al vuelo con `generar_plan_campana` y lo escriben junto al sidecar (`<sidecar>.plan.csv`). `--plan` y `--orden` son mutuamente excluyentes. A efectos de protección, `--orden` se trata igual que `--plan`.
- **`--limit` antes del orden**: con `--orden`, primero `select_cases`/`_select_cases` (canal y `limit`, sobre el orden del corpus) y después `ordenar_casos`: `--limit 10 --orden inverso` da el reverso de los primeros 10. Con `--plan`, `--limit` se rechaza con error accionable (el plan ya es la selección; para acotar se genera un plan o sub-plan más chico).
- **`--id-corrida`** obligatorio con `--plan`/`--orden`.
- **Campos nuevos**: `CaseResult` y `CorpusResult` reciben AL FINAL, con default `None`, `orden`, `posicion`, `mitad`, `brazo_primero`, `id_corrida`. Al ir al final con default, ningún constructor existente cambia. `orden` guarda el modo; `posicion` es la del plan global.
- **Sidecar por corrida**: con `--plan`, `--sidecar` es obligatorio (sin default). En `ingest_via_n8n.py`, si el archivo ya existe con otro `id_corrida`, aborta (con el mismo `id_corrida` se permite reanudar con la semántica de merge actual). En `ingest_corpus.py`, cuyo writer sobrescribe todo, un sidecar existente se rechaza (no hay reanudación: se corre con otro `id_corrida`).
- **Protección de archivos versionados** (regla en código, con test, evaluada antes de leer credenciales o enviar nada): si `--plan`/`--orden` están presentes y `--json` o `--sidecar` resuelven a un archivo de la lista explícita `ARCHIVOS_CONGELADOS` (`data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados.json`, `data/corpus_resultados_telefonia.json`, `data/corpus_resultados_n8n.json` y cualquier `data/corpus_resultados*.json`), el harness termina con código distinto de cero y un mensaje que nombra el archivo y la ruta de campaña a usar. `--json` de campaña: `evaluation/data/campana/corpus_campana.json`.
- **Copia de campaña del corpus**: `preparar_corpus_campana(origen, destino)` en `evaluation/plan_campana.py` copia el corpus canónico con `tiempo_automatizado_s` y `tiempo_manual_s` en `null`, de modo que un caso no medido en la campaña quede nulo y no herede el tiempo canónico (`merge_evaluation_json` solo escribe mediciones válidas). Rechaza un destino existente o congelado.
- **CSV/XLSX con `--plan`**: los harnesses también escriben `--csv/--xlsx` (originales locales, gitignorados, con PII). Con `--plan`/`--orden` ese write-back se omite: los datos de campaña viven solo en el sidecar y en la copia de campaña. Extensión de C8 ratificada por el orquestador; la protección cubre también `write_back` de telefonía.
- **Telefonía**: `ingest_telefonia_corpus.py` acepta `--plan` y `--id-corrida`; selecciona los casos `telefono` del plan, recupera como hoy y copia `posicion/mitad/brazo_primero` (y `orden` = modo del plan) en el `CaseResult`. Aplica la misma protección de `--json/--sidecar`, porque `write_back` escribe ambos.
- **Sidecars históricos**: se siguen leyendo; los campos ausentes equivalen a `None` (test con un sidecar sin las claves nuevas).

### D4. Corpus independiente, no solape y flags (contrato C9)

- **`evaluation/no_solape.py::verificar_no_solape(ajuste, candidato, umbral_jaccard=None)`**: recibe dos secuencias de `CasoEvaluacion`. Falla (`SolapeError`, nombrando el caso) si algún `id` del candidato no empieza con `I`, si un `id` aparece en ambos corpus, o si el SHA-256 de la descripción normalizada (NFKC, minúsculas, espacios colapsados y recortados) coincide. Con `umbral_jaccard`, la similitud Jaccard de tokens por encima del umbral se devuelve como **advertencia**, no como error. El docstring y el runbook declaran que el control **no detecta paráfrasis**. Vive en `evaluation/` para estar en CI.
- **Flags de `run_evaluation.py`**: `--corpus <ruta>`, `--predicciones <ruta>`, `--reporte <ruta>`, cableados a `main_con_corpus_real`. Si `--corpus` no resuelve a `CORPUS_REAL_PATH`: `--predicciones` y `--reporte` son obligatorios, y si resuelven a `PREDICCIONES_PATH` o `REPORT_PATH` el runner aborta (`parser.error`, código 2) antes de cargar el clasificador; además ejecuta `verificar_no_solape(cargar_corpus(CORPUS_REAL_PATH), cargar_corpus(corpus))` como paso previo obligatorio y aborta si falla. `--solo-tiempos` con un `--corpus` no canónico se rechaza. Sin flags, la conducta actual no cambia. Destino recomendado: `evaluation/data/campana/predicciones_independiente.json`. El gate `--confirm-paid` se conserva tal cual.
- **Procedencia ampliada del cache independiente** (ajuste de C9 decidido por el orquestador): el `cache_meta` de v9 (`main_con_corpus_real`, `run_evaluation.py:1459-1464`; copia congelada en `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`) solo trae `corpus_hash`, `corpus_count`, `classifier_version` y `generated_at`, sin commit. Cuando `--corpus` no es el canónico, el runner escribe en el `cache_meta` de `evaluation/data/campana/predicciones_independiente.json`, además de esos cuatro, `commit` (hash corto de `git rev-parse --short HEAD` al generar) y `pines` (`{"google_genai": <versión instalada>, "modelo": <settings.gemini_model, hoy "gemini-3.6-flash">}`). Si no puede obtener el commit (sin repo git o `git` ausente) o los pines, la corrida falla con error accionable **antes** de invocar al clasificador y antes de escribir el archivo. El commit y los pines se obtienen por funciones inyectables para testear sin git ni red. El cache canónico no cambia de formato (la conducta sin flags se conserva).
- **Referencia in-sample para c-167**: `evaluation/data/campana/README.md` registra `classifier_version` (`hybrid-v3`) y `commit_in_sample` de la corrida de referencia, citando su fuente en `evaluation/evidence/`. Como esa copia no registró commit, la comparabilidad in-sample/out-of-sample se verifica por `classifier_version` idéntico (`hybrid-v3`) y `pines` idénticos a los de `openspec/config.yaml`; el commit es obligatorio en el cache independiente y opcional en el in-sample, y el README registra `commit_in_sample = no registrado en la generación (2026-10-07); evidencia publicada en fec4c42 (c-143)` con la limitación declarada, y `pines_in_sample` (versión de google-genai y modelo con los que se generó v9, tomados de `openspec/config.yaml` `stack.inference` y de la Tabla de configuración evaluada del Anexo B de la tesis, citando ambas fuentes), que c-167 recibe como parámetro `pines_in_sample` (tarea 4.9).
- **Congelamiento del clasificador**: el runbook exige `classifier_version` (queda en la metadata del cache) y commit iguales a los del in-sample (`hybrid-v3`, `evaluation/evidence/README.md`) y prohíbe recalibrar tau, prompt o vocabulario después de ver el corpus independiente. La comprobación automática de esa igualdad al evaluar es de c-167.

### D5. Qué estima c-167 con el plan

c-167 lee el plan, los sidecars por corrida y la planilla de c-168 y estima el efecto de orden sobre el tiempo del operador (`duracion_s = timestamp - inicio` de las filas `tarea=brazo_manual`): unidad de pareo = caso (sus mediciones en las distintas corridas, unidas por `id_caso`/`case_id` e `id_corrida`), factor = `brazo_primero`, covariable de aprendizaje = `posicion` tomada del plan (no del orden de llegada) y `mitad`. El mínimo de pares y el MDE (dz ~ 0,21 con n = 200) son de c-167. c-166 solo garantiza que esos campos existan y sean confiables.

### D6. CI

Job nuevo `corpus-ingest-tests` en `.github/workflows/ci.yml` (Python 3.12): instala `scripts/corpus_ingest/requirements.txt` más `pytest` y `pyyaml` (lo importa `test_corpus_compose_isolation.py`) y corre las suites de ingesta desde la raíz. `test_pseudonymize_corpus.py` importa módulos de `App/Backend`: si requiere dependencias o variables del backend, el job lo excluye de forma explícita y lo declara en un comentario.

## Lo que NO cambia

- `docs/Tesis/v9 (IA)/` (congelada): cadenas, números y resultados.
- Cadenas de categorías (`evaluation/corpus.py:52-58`) y números canónicos (`docs/Tesis/Correcciones/numeros-canonicos.md`).
- `data/corpus_evaluacion_pseudonimizado.json` y `data/corpus_resultados*.json`.
- `evaluation/predicciones.json` (cache local, gitignorado; su copia congelada está en `evaluation/evidence/`) y `evaluation/report.md` (versionado).
- La conducta por defecto de los tres harnesses y de `run_evaluation.py` sin los flags nuevos.
- El cross-fitting within-corpus de tau.

## Risks / Trade-offs

- Alternar `brazo_primero` por paridad de posición es determinista dado el orden: con `directo` el reparto es sistemático (R001 manual, R002 automatizado). Mitigación: el runbook fija `aleatorio` con semilla registrada para la campaña.
- La copia de campaña con tiempos nulos hace que los consumidores vean más nulos que en el canónico: es intencional y se documenta en `evaluation/data/campana/README.md`.
- `verificar_no_solape` no detecta paráfrasis: se declara; la similitud Jaccard es solo una advertencia.
- Los harnesses importan `evaluation.plan_campana` vía `sys.path`: acoplamiento acotado y ya existente en la suite de telefonía.

## Migration Plan

Aditivo y retrocompatible: sin `--plan/--orden` los harnesses se comportan como hoy; sin `--corpus` el runner también. Rollback: quitar flags, campos, módulos nuevos, job de CI y runbooks. No hay migración de datos.

## Open Questions

- Ninguna abierta.
- Resueltas: CSV/XLSX bajo `--plan`/`--orden` (extensión de C8 ratificada por el orquestador: se omite el write-back a `--csv/--xlsx` y la protección cubre también `write_back` de telefonía; ver D3 y tarea 2.10); fuente del tiempo manual por caso (la planilla de c-168 agrega la columna `inicio`, ISO-8601, obligatoria para `tarea=brazo_manual`, y `timestamp` es el fin; `duracion_s = timestamp - inicio` es la variable respuesta del efecto de orden que estima c-167; ver D5 y tarea 3.2); nombre y ubicación de los runbooks (`docs/campana-medicion/runbook-campana-contrabalanceada.md` y `docs/campana-medicion/runbook-corpus-independiente.md`, separados); ubicación de `verificar_no_solape` (`evaluation/no_solape.py`); dueño del reporte out-of-sample (c-167).
