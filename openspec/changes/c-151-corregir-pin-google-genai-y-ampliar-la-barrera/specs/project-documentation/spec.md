## MODIFIED Requirements

### Requirement: DOC-005 — Stack declarado en la documentacion para agentes sincronizado con el codigo

La documentacion que heredan los agentes (`CLAUDE.md` y `openspec/config.yaml`), la base de conocimiento (`knowledge-base/**`) y el material de referencia que esos documentos alcanzan (`docs/parameters_gemini.md` y `docs/n8n-workflow-guide.md`) SHALL declarar solo valores de stack que se puedan reproducir desde el codigo o desde los archivos de dependencias: el modelo de inferencia y sus parametros desde `App/Backend/app/config/settings.py`, los umbrales de decision desde el mismo `Settings`, el conjunto canonico de sectores desde `App/Backend/app/constants.py`, y las versiones de framework y librerias desde `App/Backend/requirements.txt` y `docker-compose.yml`. Ningun valor MUST provenir de otro documento, y ningun valor retirado MUST citarse como vigente.

El flujo de clasificacion y los servicios de infraestructura que esos documentos describan MUST existir en el repositorio; una etapa o un servicio que ya no existe MUST retirarse o declararse historico, no describirse como vigente.

Las versiones de componentes que declaren `knowledge-base/**` y el material de referencia (`docs/parameters_gemini.md`) SHALL coincidir con la misma fuente de verdad que usan `CLAUDE.md` y `openspec/config.yaml`: FastAPI, Uvicorn y la restriccion de `google-genai` desde `App/Backend/requirements.txt`, y la version de N8N desde la imagen pinneada de `docker-compose.yml`. En particular, la restriccion de `google-genai` declarada en `docs/parameters_gemini.md` MUST ser al menos tan estricta como el pin de `App/Backend/requirements.txt`; una restriccion mas laxa (por ejemplo `>=2.31,<3` frente al pin `>=2.33.0,<3`) MUST reportarse como hallazgo. Una version de componente retirada MUST NOT presentarse como vigente; solo se admite en un pasaje rotulado como historico. El marcador historico MUST identificar el hecho historico que rotula y MUST NOT inferirse de una palabra que en el mismo pasaje describa otra cosa: en particular, la mencion de que el SDK `google-generativeai` esta deprecado no convierte en historica una mencion del modelo retirado en esa misma linea.

Cada valor volatil MUST tener una sola fuente declarada: cuando `CLAUDE.md` repita un valor que ya vive en `openspec/config.yaml`, MUST remitir a esa seccion en lugar de restatear el literal, para que la superficie vigilada no tenga dos copias que puedan divergir. La unica excepcion es el nombre del modelo, que se declara en ambos documentos y se verifica por coincidencia con `Settings.gemini_model`.

Los hechos historicos documentados SHALL conservarse y rotularse de forma explicita como historicos, sin presentarse como el valor vigente. En particular, la calibracion empirica de los parametros de generacion realizada sobre `gemini-2.5-flash` y la decision DD-04 de `knowledge-base/09_decisiones_y_supuestos.md` son hechos historicos declarados que SHALL permanecer citables, rotulados como antecedente, mientras que el valor vigente (`gemini-3.6-flash`, timeout 30 s por intento, 60 s total y 2 reintentos, con `google-genai >=2.33,<3`) SHALL ser el que la documentacion declare como actual. Un pasaje que mencione el modelo retirado MUST distinguir de forma explicita el valor vigente del hecho historico y MUST NOT afirmar un invariante de tiempos que el valor vigente desmienta.

El timeout del cliente HTTP declarado en `App/Frontend/src/services/api.ts` SHALL superar el peor caso total de una clasificacion del backend (`Settings.gemini_total_timeout_seconds`), de modo que el cliente no desista antes que la API resuelva su propio fallback.

La suite de pruebas de la barrera (`scripts/preflight/test_docs_stack_sync.py`) SHALL ser hermética respecto del estado real del repositorio: sus fixtures MUST construir arboles sinteticos autosuficientes con las versiones de componentes fijadas por la propia prueba, y MUST NOT derivar la linea base de las versiones reales declaradas en `App/Backend/requirements.txt`, `docker-compose.yml` u `openspec/config.yaml`. Un cambio legitimo de version de dependencia MUST NOT producir hallazgos por si mismo en la suite, y una unica deriva inyectada sobre un arbol sincronizado MUST aislar exactamente un hallazgo.

#### Scenario: Modelo y parametros de inferencia coinciden con la configuracion

- **WHEN** se leen las lineas de `CLAUDE.md` y de `openspec/config.yaml` que declaran el modelo y los parametros de inferencia
- **THEN** el modelo coincide con `Settings.gemini_model`
- **AND** temperature, top_p y max_output_tokens coinciden con `Settings`
- **AND** el timeout, el timeout total y los reintentos declarados coinciden con `Settings.gemini_timeout_seconds`, `gemini_total_timeout_seconds` y `gemini_max_retries`

#### Scenario: Versiones de framework y dependencias coinciden con los pines

- **WHEN** se leen las versiones de FastAPI, Uvicorn y `google-genai` declaradas en `openspec/config.yaml`
- **THEN** coinciden con las restricciones vigentes de `App/Backend/requirements.txt`
- **AND** la version de N8N declarada coincide con la imagen pinneada del compose

#### Scenario: Umbrales y sectores canonicos coinciden con el codigo

- **WHEN** se leen `conventions.thresholds` y `conventions.categorias` de `openspec/config.yaml`
- **THEN** los umbrales coinciden con `Settings.deterministic_score_threshold` y `Settings.human_review_threshold`
- **AND** los sectores coinciden, en contenido y en orden, con `SECTORES_CANONICOS` de `App/Backend/app/constants.py`

#### Scenario: Un valor volatil no se duplica fuera de su fuente

- **WHEN** se busca en `CLAUDE.md` un umbral, una version de framework o de plataforma que ya declara `openspec/config.yaml`
- **THEN** el valor no aparece como literal repetido
- **AND** el texto remite a la seccion correspondiente de `openspec/config.yaml`
- **AND** el nombre del modelo es la excepcion: figura en ambos documentos y ambos coinciden con `Settings.gemini_model`

#### Scenario: Flujo y servicios descritos existen en el repositorio

- **WHEN** la documentacion para agentes describe una etapa de clasificacion o un servicio de infraestructura
- **THEN** la etapa o el servicio existe en el codigo o en el compose
- **AND** ninguna etapa o servicio retirado se describe como vigente

#### Scenario: Valores retirados no se citan como vigentes

- **WHEN** se busca en `CLAUDE.md` y `openspec/config.yaml` un modelo, una version o un servicio que el codigo ya no usa
- **THEN** no aparece como valor vigente del stack

#### Scenario: Barrera ejecutable detecta la divergencia

- **WHEN** un valor de stack declarado en `CLAUDE.md`, en `openspec/config.yaml`, en `knowledge-base/**` o en el material de referencia (`docs/parameters_gemini.md`, `docs/n8n-workflow-guide.md`) diverge de `settings.py`, de `requirements.txt` o del compose, o se describe un servicio o etapa que ya no existe
- **THEN** el preflight `scripts/preflight/docs_stack_sync.py` termina con codigo distinto de cero
- **AND** el hallazgo nombra el valor o el servicio divergente
- **AND** el paso corre en el job `backend-tests` del pipeline de integracion continua

#### Scenario: Barrera ejecutable en verde con la documentacion sincronizada

- **WHEN** la documentacion para agentes declara unicamente valores que coinciden con el codigo y el compose
- **THEN** el preflight termina con codigo 0 y sin hallazgos
- **AND** su suite de pruebas queda incluida en `python -m pytest scripts/preflight -q`

#### Scenario: Documentacion de agentes valida como configuracion

- **WHEN** se carga `openspec/config.yaml` con un lector YAML y se ejecuta el CLI de OpenSpec
- **THEN** el archivo parsea sin errores
- **AND** los comandos de OpenSpec siguen respondiendo sobre el proyecto

#### Scenario: Base de conocimiento y material de referencia declaran el modelo vigente

- **WHEN** se buscan tokens de modelo (`gemini-<version>-flash` o `<version> Flash`) en `knowledge-base/**` y en `docs/parameters_gemini.md` y `docs/n8n-workflow-guide.md`
- **THEN** todo token que no sea `Settings.gemini_model` aparece unicamente en un pasaje rotulado como historico
- **AND** los archivos que declaran la configuracion vigente citan `gemini-3.6-flash` y `google-genai >=2.33,<3`
- **AND** el timeout declarado en contexto de parametros de Gemini es 30 s por intento, con 60 s total y 2 reintentos

#### Scenario: Versiones de componentes de la base de conocimiento coinciden con los pins

- **WHEN** se leen las versiones de N8N, FastAPI, Uvicorn y `google-genai` declaradas en `knowledge-base/**` y en `docs/parameters_gemini.md`
- **THEN** N8N coincide con la imagen pinneada de `docker-compose.yml`
- **AND** FastAPI y Uvicorn coinciden con los pines exactos de `App/Backend/requirements.txt`
- **AND** la restriccion de `google-genai` declarada en `knowledge-base/**` y en `docs/parameters_gemini.md` es al menos tan estricta como `>=2.33.0,<3`
- **AND** una version de componente retirada solo aparece en un pasaje rotulado como historico

#### Scenario: El marcador historico no se infiere de una palabra que rotula otra cosa

- **WHEN** una linea de `knowledge-base/**` menciona un token de modelo retirado junto a la palabra "deprecado" o "deprecada" referida al SDK `google-generativeai`
- **THEN** la linea no se considera historica por esa palabra
- **AND** el preflight reporta el token de modelo retirado si no hay un marcador historico que lo rotule

#### Scenario: Hechos historicos preservados y rotulados como historicos

- **WHEN** se lee la procedencia de la calibracion de parametros y la decision DD-04 en `knowledge-base/09_decisiones_y_supuestos.md` y en `docs/parameters_gemini.md`
- **THEN** el hecho de que los parametros se calibraron sobre `gemini-2.5-flash` se conserva
- **AND** el pasaje esta rotulado de forma explicita como antecedente historico
- **AND** no se presenta `gemini-2.5-flash` ni un timeout de 10 s como el valor vigente
- **AND** el pasaje remite al valor vigente (`gemini-3.6-flash`, 30 s por intento, 60 s total, 2 reintentos)

#### Scenario: Barrera ejecutable cubre la base de conocimiento y el material de referencia

- **WHEN** un token de modelo retirado, un timeout retirado o una version de componente retirada aparece en `knowledge-base/**` o en el material de referencia sin rotulacion historica
- **THEN** el preflight `scripts/preflight/docs_stack_sync.py` termina con codigo distinto de cero
- **AND** el hallazgo nombra el archivo, la linea y el token o valor divergente
- **AND** los valores esperados de las versiones de componentes se derivan en tiempo de ejecucion de `requirements.txt` y de `docker-compose.yml`, no se hardcodean en el chequeo
- **AND** la lista de archivos inspeccionados por el preflight incluye `knowledge-base/**`, `docs/parameters_gemini.md` y `docs/n8n-workflow-guide.md`

#### Scenario: La restriccion de google-genai del material de referencia se valida contra requirements.txt

- **WHEN** `docs/parameters_gemini.md` declara una restriccion de `google-genai` mas laxa que el pin de `App/Backend/requirements.txt` (por ejemplo `>=2.31,<3` frente al pin `>=2.33.0,<3`) en un pasaje no rotulado como historico
- **THEN** el preflight `scripts/preflight/docs_stack_sync.py` termina con codigo distinto de cero
- **AND** el hallazgo nombra `docs/parameters_gemini.md`, la linea y la restriccion divergente
- **AND** el valor esperado de la restriccion de `google-genai` se deriva en tiempo de ejecucion de `App/Backend/requirements.txt`, no se hardcodea
- **AND** cuando el mismo archivo declara la restriccion corregida (`google-genai >=2.33,<3`), el chequeo pasa

#### Scenario: El timeout del cliente supera el peor caso total del backend

- **WHEN** se compara el timeout de Axios declarado en `App/Frontend/src/services/api.ts` con `Settings.gemini_total_timeout_seconds`
- **THEN** el timeout del cliente es estrictamente mayor que el peor caso total del backend (65 s > 60 s)
- **AND** el comentario del cliente declara ese invariante sin afirmar un valor de Gemini retirado
- **AND** la barrera `scripts/preflight/docs_stack_sync.py` verifica el invariante y termina con codigo distinto de cero si el timeout del cliente no supera el peor caso del backend

#### Scenario: La suite de la barrera es hermética frente a las versiones reales del repositorio

- **WHEN** se ejecuta `python3 -m pytest scripts/preflight -q` con una version de dependencia distinta de la que la suite tiene fijada (por ejemplo, tras un bump de `App/Backend/requirements.txt`)
- **THEN** la suite permanece en verde y no depende del contenido real de `requirements.txt`, `docker-compose.yml` ni `openspec/config.yaml`
- **AND** sus fixtures construyen el arbol sobre el que corren los chequeos con las versiones fijadas por la propia prueba

#### Scenario: Una deriva inyectada aísla exactamente un hallazgo

- **WHEN** sobre un arbol sintetico sincronizado se muta un unico valor (un modelo, una version de componente, un umbral o un timeout)
- **THEN** la barrera reporta exactamente un FAIL, nombrando el valor divergente
- **AND** el resto de los chequeos sigue en PASS, tambien cuando el arbol sintetico usa versiones de componentes nuevas
