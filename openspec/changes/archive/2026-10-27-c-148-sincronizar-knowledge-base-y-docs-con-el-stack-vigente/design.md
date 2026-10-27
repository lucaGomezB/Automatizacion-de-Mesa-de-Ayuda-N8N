## Context

Ver `proposal.md` (Why). Estado verificado en el arbol de trabajo (2026-10-27, rama `main`, OpenSpec 1.10.0):

- **Fuente de verdad del stack.** `App/Backend/app/config/settings.py:78` `gemini_model = "gemini-3.6-flash"`; `:85` `gemini_timeout_seconds = 30`; `:97` `gemini_max_retries = 2`; `:104` `gemini_total_timeout_seconds = 60`; `:79-81` temperatura 0.3, top_p 0.9, max_output_tokens 100. `App/Backend/requirements.txt:37` fija `google-genai>=2.31.0,<3`.
- **Procedencia declarada.** `settings.py:72-76` documenta que los parametros de generacion se **calibraron empiricamente sobre el corpus de 200 casos con Gemini 2.5 Flash** y que el modelo default se **migro a 3.6 Flash** porque la familia 2.5 ya no esta disponible para cuentas nuevas; cambiar el modelo exige re-evaluar las metricas de exactitud. La tesis ya usa `gemini-3.6-flash` (integrado el 2026-09-24, `docs/diagrams/cronograma.md`).
- **Ya correctos (no tocar).** `openspec/config.yaml:10,33,34`; `CLAUDE.md:7,40,47,50`.
- **Deriva real (9 archivos).** `knowledge-base/01_vision_y_objetivos.md:5,22`; `02_descripcion_general.md:13,42`; `05_reglas_de_negocio.md:9`; `07_flujos_principales.md:7`; `08_arquitectura_propuesta.md:63`; `09_decisiones_y_supuestos.md:14,15`; `docs/parameters_gemini.md:1,5,51,55,73,75,102,103`; `docs/n8n-workflow-guide.md:852`; `App/Frontend/src/services/api.ts:7-8,42-44`.
- **Noveno archivo (Bloque E, ahora EN ALCANCE).** `App/Frontend/src/services/api.ts:7-8,42-44` afirma "timeout mayor al de Gemini (10 s)" con `timeout: 20_000`. Con el valor vigente (30 s por intento, 60 s total) el comentario es falso: 20 s < 60 s. La decision es subir el timeout de Axios a 65 s (mayor que el peor caso total del backend, 60 s) y corregir los comentarios; el invariante queda verdadero.
- **Hallazgo adyacente (fuera de alcance, se documenta).** `docs/n8n-workflow-guide.md:598,610` conservan el umbral retirado `0.90` (dominio de DOC-004, no de este change).
- **Barrera existente.** `scripts/preflight/docs_stack_sync.py` (12 chequeos) inspecciona SOLO `settings.py`, `constants.py`, `requirements.txt`, `docker-compose.yml`, `openspec/config.yaml` y `CLAUDE.md`; `scripts/preflight/test_docs_stack_sync.py` tiene 35 pruebas. Corre en el job `backend-tests` y via `pytest scripts/preflight`. NO cubre `knowledge-base/**`, el material de referencia ni `App/Frontend/src/services/api.ts`.
- **Residual 1, deriva de versiones de componentes (verificada 2026-10-27).** `knowledge-base/02_descripcion_general.md:7` declara N8N `1.62` y `:8` FastAPI `0.115` / Uvicorn `0.32`; `:30` N8N `v1.62`; `08_arquitectura_propuesta.md:76` N8N `1.62`; `09_decisiones_y_supuestos.md:6` N8N `1.62` y `:21` FastAPI `0.115`. Fuentes: `docker-compose.yml` `image: n8nio/n8n:2.11.2`; `requirements.txt` `fastapi==0.143.3`, `uvicorn[standard]==0.54.0`, `google-genai>=2.31.0,<3`. Los chequeos 4/5/6 ya comparan `config.yaml`/`CLAUDE.md` contra esas fuentes, pero nada compara `knowledge-base/`.
- **Residual 2, exencion falsa de `deprecad` (verificada 2026-10-27).** `MARCADORES_HISTORICOS` incluye `deprecad`. `knowledge-base/02_descripcion_general.md:13` dice "reemplaza al deprecado `google-generativeai`": ese uso rotula el SDK, no el modelo, y hace que la linea quede exenta del chequeo 13. Un token de MODELO retirado agregado a esa linea no se detectaria. `deprecad` no se usa en la superficie para rotular el modelo como historico.

## Goals / Non-Goals

**Goals:**

- Que la base de conocimiento y el material de referencia declaren el valor vigente del modelo y de sus parametros (A, B).
- Que la procedencia historica (calibracion sobre 2.5 Flash, DD-04) sobreviva rotulada como historia y no como valor actual (C).
- Que el invariante del timeout del cliente quede verdadero: Axios 65 s > peor caso total del backend 60 s (E).
- Que la barrera detecte automaticamente esta clase de deriva sobre la superficie ampliada (incluido el invariante del cliente), con TDD estricto (D).

**Non-Goals:**

- No cambiar comportamiento de aplicacion del backend ni de N8N; el unico cambio de codigo es el timeout de Axios de `App/Frontend/src/services/api.ts` (Bloque E).
- No tocar `openspec/config.yaml` ni `CLAUDE.md` (correctos desde c-145).
- No re-ejecutar el clasificador, Gemini, N8N ni la evaluacion; no se generan valores nuevos.
- No corregir los umbrales `0.90` de `docs/n8n-workflow-guide.md:598,610` (fuera de alcance; se registran).
- No reescribir `knowledge-base/11_evaluacion_experimental.md` ni los numeros de resultado (dominio del requisito `Sincronia de la base de conocimiento...`).

## Decisions

### D1 — Separar valor vigente de hecho historico por rotulacion explicita

Regla: cada valor de stack se escribe desde su fuente (codigo o dependencias), y cada mencion del modelo retirado va acompanada de una rotulacion historica explicita.

| Dato | Valor vigente (se escribe) | Hecho historico (se conserva rotulado) | Fuente verificada |
|---|---|---|---|
| Modelo | `gemini-3.6-flash` / "Gemini 3.6 Flash" | calibracion de parametros sobre `gemini-2.5-flash` | `settings.py:78`, `:72-76` |
| Timeout por intento | 30 s | 10 s (valor previo) | `settings.py:85` |
| Timeout total | 60 s | — | `settings.py:104` |
| Reintentos | 2 (peor caso 3 intentos) | — | `settings.py:97` |
| SDK | `google-genai >=2.31,<3` | `>= 1.0` | `requirements.txt:37` |
| Parametros | temperature 0.3, top_p 0.9, max_output_tokens 100 | mismos (calibrados sobre 2.5) | `settings.py:79-81` |

**Marcador historico:** conjunto declarado y testable de substrings que rotulan un pasaje como historico (`historico`, `historica`, `historicamente`, `calibrad`, `antecedente`, `superad`, `migro`, `migrado`, `retirado`, `deprecad`, `previo`). La barrera exime una mencion retirada SOLO si su linea o su encabezado de seccion contiene un marcador.

**Alternativa considerada:** reemplazo global `2.5` -> `3.6`. Se descarta: destruye la procedencia de la calibracion, que es una limitacion declarada de la tesis y evidencia de auditoria.

### D2 — `knowledge-base/07_flujos_principales.md:7`: invariante restaurado con el Bloque E

La linea afirma "Axios, timeout 20 s > timeout Gemini 10 s". Con el valor vigente (30 s por intento, 60 s total) el invariante era FALSO: 20 s < 60 s. El Bloque E sube el timeout de Axios a 65 s, de modo que el invariante VUELVE A SER VERDADERO: 65 s (cliente) > 60 s (peor caso total de una clasificacion, `Settings.gemini_total_timeout_seconds`). La linea se reescribe declarando los valores reales de cada capa y la desigualdad verdadera, y remite a `App/Frontend/src/services/api.ts`.

**Alternativa considerada:** dejar el cliente en 20 s y reescribir solo la documentacion para no afirmar la desigualdad. Se descarta: el autor decide restaurar el invariante (el cliente debe esperar mas que el peor caso del backend para no desistir antes); es un cambio de configuracion acotado (un unico literal de timeout) y verificado por el chequeo 16 de la barrera.

**Por que 65 s y no 70 s:** 65 s es el menor multiplo de 5 estrictamente mayor que el peor caso total del backend (60 s); deja 5 s de margen sin alargar la espera del usuario mas de lo necesario. El valor se verifica contra `Settings.gemini_total_timeout_seconds` (no se hardcodea la comparacion).

### D3 — `docs/parameters_gemini.md`: separar la configuracion viva de la procedencia

El documento mezcla la configuracion vigente con el registro de la calibracion. Se retitula con el modelo vigente, se actualizan `model`, `timeout` y la restriccion de `google-genai`, y se conserva el relato de calibracion (lineas 100-105) bajo una seccion explicita de procedencia historica. `CLAUDE.md` apunta a este archivo, de modo que es material alcanzable por los agentes.

**Alternativa considerada:** dejar el archivo como "documento historico". Se descarta: describe la invocacion real del clasificador y los agentes lo leen como vigente.

### D4 — Extension de la barrera: chequeos nuevos con regla de rotulacion (TDD estricto)

Se agregan a `docs_stack_sync.py`:

- `SUPERFICIE_KB` = `knowledge-base/**/*.md`; `DOCS_REFERENCIA` = `docs/parameters_gemini.md`, `docs/n8n-workflow-guide.md`.
- **Chequeo 13 — modelo vigente en la superficie ampliada.** Extrae todos los tokens de modelo (`gemini-\d+\.\d+-flash` o `\d+\.\d+ Flash`); cada token distinto de `Settings.gemini_model` MUST estar en un pasaje rotulado como historico; si no, FAIL con `archivo:linea` y el token.
- **Chequeo 14 — timeout vigente en contexto de parametros de Gemini.** Sobre las lineas que mencionan Gemini o un parametro (`top_p`, `max_tokens`, `max_output_tokens`, `candidate_count`, `timeout`) extrae el valor de timeout; un timeout retirado (10) sin rotulacion historica es FAIL; 30 es PASS.
- **Chequeo 15 — superficie cubierta.** La lista de archivos inspeccionados incluye la base de conocimiento y el material de referencia; si un archivo esperado no existe, FAIL (no excepcion).
- **Chequeo 16 — invariante del timeout del cliente (Bloque E).** Extrae el timeout de Axios de `App/Frontend/src/services/api.ts` (ms) y lo compara con `Settings.gemini_total_timeout_seconds * 1000`. El timeout del cliente MUST ser estrictamente mayor que el peor caso total del backend; si no, FAIL nombrando ambos valores. La comparacion se deriva de `Settings` (no se hardcodea `65_000`).

Los chequeos 1 a 12 y el contrato (`Check`, `exit_code`, `format_summary`) NO cambian. La lista estatica de identificadores retirados (`2.5 Flash`, `1.62`) se reutiliza para la superficie ampliada SOLO para los tokens de modelo (`2.5 Flash`); `1.62` no se reutiliza porque la base de conocimiento menciona legitimamente N8N 1.62 en pasajes fuera del alcance de este change y el chequeo 13 se restringe a tokens de modelo (`gemini-<version>-flash` o `<version> Flash`).

**Prueba de que la barrera sirve (RED):** con los 8 archivos sin corregir, el preflight DEBE fallar nombrando "Gemini 2.5 Flash" y "timeout 10 s" en la base de conocimiento y el material de referencia. Si sale 0, la extension no sirve y el apply se detiene.

**Alternativa considerada:** extender el chequeo 12 (duplicacion) a la nueva superficie. Se descarta: el 12 mide duplicacion de literales de `config.yaml`, una semantica distinta de "valor retirado no citado como vigente".

### D5 — Estrategia de spec: `MODIFIED` sobre DOC-005

Se MODIFICA `DOC-005` (no se agrega un requisito nuevo) porque su texto enumera literalmente la superficie ("`CLAUDE.md` y `openspec/config.yaml`") y `openspec/config.yaml` declara `knowledge-base/` como documentacion de contexto para agentes. El bloque MODIFIED copia el requisito completo (los 9 escenarios vivos, con nombre literal) y agrega los escenarios de base de conocimiento, rotulacion historica y cobertura de la barrera. Se evita el pitfall de contenido parcial copiando el bloque entero.

**Alternativa considerada:** agregar `DOC-006` como requisito hermano. Se descarta: duplicaria la semantica de "valor vigente vs retirado" en dos requisitos y dejaria el escenario de barrera de DOC-005 incompleto.

### D6 — Noveno archivo: `App/Frontend/src/services/api.ts` (Bloque E)

El comentario de cabecera (lineas 7-8) y el comentario en linea (42-44) afirman que el timeout del cliente supera el de Gemini, con `timeout: 20_000`. Con el valor vigente el comentario es falso (20 s < 60 s). Se decide:

1. Subir `timeout: 20_000` a `timeout: 65_000` (D2).
2. Reescribir ambos comentarios para declarar el invariante verdadero: el cliente (65 s) espera mas que el peor caso total de una clasificacion del backend (60 s), de modo que la API resuelve su propio fallback antes de que el cliente desista.

El valor 65 s se fija como literal en `api.ts` (el frontend no lee `Settings` del backend); el chequeo 16 de la barrera lo compara contra `Settings.gemini_total_timeout_seconds` para que la deriva futura falle de forma automatica.

**Alternativa considerada:** dejar `api.ts` fuera de alcance (como decia el proposal original) y registrar solo el hallazgo. Se descarta: el autor decide restaurar el invariante ahora; mantener un comentario falso es exactamente la clase de deriva que este change ataca.

### D7 — Versiones de componentes: valor vigente por fuente, no rotulacion historica (residual 1)

La misma regla de D1 (valor vigente desde el codigo, hecho historico rotulado) se aplica a las versiones de componentes de `knowledge-base/`. La fuente es `requirements.txt` para FastAPI/Uvicorn/google-genai y la imagen del compose para N8N; no se toma ningun valor de otro documento.

| Archivo:linea | Declarado hoy | Valor vigente | Fuente |
|---|---|---|---|
| `02_descripcion_general.md:7` | N8N `1.62` | `2.11.2` | `docker-compose.yml` (`n8nio/n8n:2.11.2`) |
| `02_descripcion_general.md:8` | FastAPI `0.115` / Uvicorn `0.32` | `0.143.3` / `0.54.0` | `requirements.txt:5,9` |
| `02_descripcion_general.md:30` | N8N `v1.62` | `v2.11.2` | `docker-compose.yml` |
| `08_arquitectura_propuesta.md:76` | N8N oficial `1.62` | `2.11.2` | `docker-compose.yml` |
| `09_decisiones_y_supuestos.md:6` | N8N `1.62` autoalojado | `2.11.2` | `docker-compose.yml` |
| `09_decisiones_y_supuestos.md:21` | FastAPI `0.115` sobre Uvicorn | `0.143.3` sobre Uvicorn `0.54.0` | `requirements.txt:5,9` |

**Decision por linea en `09_decisiones_y_supuestos.md`:** DD-01 ("N8N como orquestador") y DD-06 ("FastAPI + Pydantic") son decisiones VIGENTES: la decision arquitectonica sigue en pie y lo unico desactualizado es la version con la que se implementa. Por eso se actualiza la version y NO se rotula la linea como historica. El criterio es el mismo que se aplico a `config.yaml`/`CLAUDE.md` en c-145. Distinto es DD-04, que si es un registro de una calibracion pasada y por eso queda rotulado como historico (D1).

**Alternativa considerada:** rotular DD-01/DD-06 como historicos y dejar `1.62`/`0.115`. Se descarta: falsificaria la decision vigente presentandola como antecedente y dejaria dos valores actuales en la KB (el decision document y la tabla de stack) que se contradicen.

### D8 — Chequeo 17 y marcador `deprecad` (residuales 2 y 3)

**`deprecad`:** se retira de `MARCADORES_HISTORICOS`. En esta superficie `deprecad` rotula al SDK retirado `google-generativeai` (`knowledge-base/02_descripcion_general.md:13`, `docs/parameters_gemini.md:5`), no al modelo. Mantenerlo exime la linea completa del chequeo 13 y permite que un token de modelo retirado pase inadvertido. El hecho historico del modelo (DD-04) ya se rotula con `historico`/`antecedente`/`calibrad`, de modo que retirar `deprecad` no deja ningun pasaje legitimo sin marcador.

**Chequeo 17 — versiones de componentes en la KB.** Se agrega `_check_versiones_componentes(requirements, compose, kb_dir)`, que recorre `knowledge-base/**/*.md` con el mismo criterio de marcador historico y:

- extrae la version de N8N anclada al token `N8N` (tabla `| N8N | 1.62 |`, `N8N v1.62`, `N8N oficial 1.62`, `N8N 1.62 autoalojado`) y la compara con el tag de la imagen del compose;
- extrae FastAPI/Uvicorn de la tabla (`FastAPI + Uvicorn | X / Y`) y de la prosa (`FastAPI X sobre Uvicorn Y`) y los compara con los pines exactos de `requirements.txt` usando `_prefijo_declarado` (misma semantica que el chequeo 4);
- extrae las restricciones de `google-genai` (incluida la forma entre backticks) y las valida con `_restriccion_compatible` contra `requirements.txt` (misma semantica que el chequeo 5).

Los valores esperados se derivan EN TIEMPO DE EJECUCION (`_pin_exacto`, `_n8n_tag`, `requirements`); no se hardcodea `2.11.2`, `0.143.3`, `0.54.0` ni `>=2.31,<3` en el chequeo. Los patrones estan anclados al token del componente para no capturar cualquier numero de la linea (puertos, dias, `python:3.12`, `postgres:15.5`). El chequeo se agrega al final de la lista: los chequeos 1-16 y el contrato `Check`/`exit_code`/`format_summary` no cambian.

**Prueba de que sirve (RED real):** antes de corregir la KB, el preflight paso de 16/16 a 17 chequeos con el 17 en FAIL, nombrando las siete declaraciones: `02_descripcion_general.md:7` N8N 1.62, `:8` FastAPI 0.115 y Uvicorn 0.32, `:30` N8N 1.62, `08_arquitectura_propuesta.md:76` N8N 1.62, `09_decisiones_y_supuestos.md:6` N8N 1.62 y `:21` FastAPI 0.115.

**Alternativa considerada:** extender los chequeos 4/5/6 para que tambien recorran la KB. Se descarta para no cambiar la semantica ni el contrato de los chequeos existentes (hoy comparan `config.yaml`/`CLAUDE.md`); un chequeo 17 dedicado aisla los hallazgos y mantiene intactos los 16 anteriores.

## Risks / Trade-offs

- [La deteccion del timeout da falsos positivos porque "10" es un token generico] -> Restringir el chequeo 14 a lineas en contexto de parametros de Gemini y a la lista declarada de timeouts retirados (`10`); eximir con marcador historico; triangular con casos negativos.
- [El marcador historico se vuelve una convencion fragil] -> Conjunto de marcadores declarado como constante y probado; la rotulacion se agrega al texto, no se infiere.
- [El apply no recompila la tesis] -> Fuera de alcance; la tesis ya usa 3.6 Flash. Los renders no se tocan.
- [Subir el timeout del cliente a 65 s alarga la espera percibida ante un backend colgado] -> 65 s solo aplica al peor caso; el backend degrada a fallback o responde antes en el camino normal. El margen sobre el backend (5 s) es el minimo razonable y se verifica contra `Settings`.
- [El apply edita 9 archivos con riesgo de reemplazo ciego] -> Cada valor se toma de `settings.py`/`requirements.txt`/el compose; verificacion final por grep de "2.5 Flash", "timeout 10 s", "1.62", "0.115" y "0.32" fuera de pasajes rotulados y por los chequeos 16 y 17.
- [El chequeo 17 da falsos positivos por capturar cualquier numero de una linea de KB] -> Los patrones estan anclados al token del componente (N8N, FastAPI/Uvicorn, google-genai) y hay pruebas negativas con `python:3.12`, `postgres:15.5` y timeouts de N8N en las mismas lineas o en lineas vecinas.
- [Retirar `deprecad` rompe pasajes legitimos que solo se rotulaban con esa palabra] -> Verificado sobre el arbol real: los unicos usos de `deprecad` rotulan el SDK `google-generativeai`, no el modelo; el preflight sigue 17/17 y el hecho historico del modelo conserva `historico`/`antecedente`/`calibrad`.

## Migration Plan

1. **Safety Net:** `python3 -m pytest scripts/preflight -q` (baseline) y `python3 scripts/preflight/docs_stack_sync.py` (debe salir 0 hoy).
2. **Bloque D (TDD):** RED con las pruebas de los chequeos 13-16 (fallan porque no existen); GREEN implementando los chequeos; TRIANGULATE con mutaciones; REFACTOR; correr el preflight sobre el arbol SIN corregir y confirmar que falla nombrando la deriva.
3. **Bloques A y B:** editar la base de conocimiento y el material de referencia tomando cada valor de su fuente.
4. **Bloque C:** rotular los pasajes historicos; verificar que "2.5 Flash" solo aparece en pasajes rotulados.
5. **Bloque E:** subir el timeout de `api.ts` a 65 s y corregir sus comentarios; confirmar el invariante con el chequeo 16.
6. **Bloque F (residual 1):** actualizar las seis versiones de componentes de la KB desde `requirements.txt`/el compose; verificar `grep -rn "1\.62\|0\.115\|0\.32" knowledge-base/` sin coincidencias.
7. **Bloque G (residuales 2 y 3, TDD):** RED con las pruebas del chequeo 17 y de la exencion falsa de `deprecad`; GREEN retirando `deprecad` y agregando el chequeo 17; TRIANGULATE con N8N desconocido, N8N rotulado, FastAPI/Uvicorn de tabla y de prosa, `google-genai` retirado y derivacion de valores en runtime; REFACTOR. Verificar que sobre el arbol SIN corregir el preflight falla con las siete declaraciones de version.
8. **Verificacion:** `python3 scripts/preflight/docs_stack_sync.py` = 0 (17/17); `pytest scripts/preflight -q` verde; `openspec validate c-148-... --strict` y `openspec validate --specs --strict`; frontend `npm run lint`, `npm run test`, `npm run build`.
9. **Rollback:** `git revert` de los commits; la barrera vuelve a 12 chequeos, el cliente a 20 s y la documentacion a su estado previo.

## Open Questions

- **Timeout del cliente vs backend (D2, D6).** El autor decidio restaurar el invariante: el cliente sube a 65 s y supera el peor caso total del backend (60 s). El valor 65 s (multiplo de 5, minimo con margen) queda como literal en `api.ts`; la barrera (chequeo 16) lo compara contra `Settings.gemini_total_timeout_seconds` para detectar deriva futura. Si en el futuro el peor caso del backend crece por encima de 60 s, el chequeo 16 falla y obliga a revisar el literal.
- **Umbrales `0.90` de `docs/n8n-workflow-guide.md:598,610`.** Pertenecen al dominio de DOC-004. Se registran como hallazgo; no se corrigen aqui salvo decision explicita del orchestrator.
