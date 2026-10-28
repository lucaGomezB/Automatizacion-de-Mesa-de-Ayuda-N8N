# Proposal: c-151-corregir-pin-google-genai-y-ampliar-la-barrera

## Why

`docs/parameters_gemini.md` todavia declara la restriccion `google-genai >=2.31,<3` como valor vigente en DOS pasajes: la linea 5 ("Versión de cliente", seccion `## Invocación de API`) y la linea 101 (nota de valor vigente dentro de "Historial de Cambios"). El pin autoritativo del repositorio es `>=2.33.0,<3` (`App/Backend/requirements.txt:42`, `openspec/config.yaml:33` y `knowledge-base/02_descripcion_general.md:13`). El residual nacio en c-148 (commit `3392012`), que escribio `>=2.31,<3`, y sobrevivio a c-149 (commit `f666316`), que subio el pin en requirements/config/knowledge-base pero no volvio sobre `parameters_gemini.md`. La barrera no lo detecto porque el chequeo 17 solo recorre `knowledge-base/**`, no el material de referencia (`DOCS_REFERENCIA`): `python3 scripts/preflight/docs_stack_sync.py` imprime hoy 17/17 PASS con el valor obsoleto presente. Este change corrige el documento y, sobre todo, cierra el agujero de la barrera que dejo pasar el residual.

## What Changes

- **Bloque A — corregir el documento (BAJO).** En `docs/parameters_gemini.md`, llevar la restriccion citada como vigente de `google-genai >=2.31,<3` a `google-genai >=2.33,<3` en sus DOS pasajes vigentes: la linea 5 ("Versión de cliente") y la linea 101 (nota de valor vigente). La seccion "Historial de Cambios" y sus referencias historicas (por ejemplo `2.5 Flash`) NO se tocan: son antecedentes rotulados como tales y la linea 101 conserva su texto historico salvo la restriccion vigente que cita.
- **Bloque B — ampliar la barrera (BAJO, TDD estricto).** Extender el chequeo de versiones de componentes de `scripts/preflight/docs_stack_sync.py` para que la COMPARACION de la restriccion de `google-genai` cubra tambien `DOCS_REFERENCIA` (al menos `docs/parameters_gemini.md`), y no solo `knowledge-base/**`. Se reutilizan `_restricciones_genai_en_linea` y `_restriccion_compatible`, y la misma regla de exencion por rotulacion historica (un pasaje bajo un encabezado historico queda exento). La ampliacion se acota a la restriccion de `google-genai`: los barridos de N8N, FastAPI y Uvicorn siguen limitados a `knowledge-base/**`, para no arrastrar discrepancias ajenas del material de referencia (por ejemplo `docs/n8n-workflow-guide.md:767`, un registro de verificacion historica que cita `N8N 2.25.7`). El valor esperado se sigue derivando en tiempo de ejecucion de `requirements.txt`; no se hardcodea. La ampliacion se desarrolla con TDD: primero un test que falla en `scripts/preflight/test_docs_stack_sync.py` (RED), luego la implementacion (GREEN).
- **Sin cambios** en los valores del modelo `gemini-3.6-flash`, en los parametros de inferencia, en las cinco cadenas canonicas de sector, en `requirements.txt` (el pin ya es el correcto) ni en el material historico. No se hardcodea ninguna version en el chequeo: el valor esperado se sigue derivando de `requirements.txt`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-documentation`: se modifica el requisito `DOC-005 — Stack declarado en la documentacion para agentes sincronizado con el codigo` para exigir que la verificacion de la restriccion de `google-genai` cubra explicitamente el material de referencia (`docs/parameters_gemini.md`), no solo `knowledge-base/**`. La barrera MUST derivar el valor esperado en tiempo de ejecucion de `App/Backend/requirements.txt` y MUST reportar un hallazgo cuando el material de referencia declare una restriccion de `google-genai` mas laxa que el pin, salvo que el pasaje este rotulado como historico. El valor vigente que el material de referencia SHOULD declarar pasa a ser `google-genai >=2.33,<3`.

## Impact

- **Edita:** `docs/parameters_gemini.md`; `scripts/preflight/docs_stack_sync.py`; `scripts/preflight/test_docs_stack_sync.py`; `openspec/changes/c-151-corregir-pin-google-genai-y-ampliar-la-barrera/**`; opcionalmente el indice de `CHANGES.md`.
- **No toca:** `App/Backend/requirements.txt` (el pin ya es `>=2.33.0,<3`), `openspec/config.yaml`, `knowledge-base/**`, el codigo de `App/Backend/app/`, el frontend, `n8n/`, las cinco cadenas de categoria ni el historial de `parameters_gemini.md`.
- **Gobernanza:** BAJO (correccion de un valor documental y ampliacion de una barrera de CI, con TDD estricto).
- **Dependencias:** la barrera creada por c-145 y ampliada por c-148/c-149 (`scripts/preflight`, 17 chequeos). El agujero esta en la superficie del chequeo 17, que hoy itera `_leer_superficie_kb(kb_dir)` sin incluir `DOCS_REFERENCIA`.
- **Riesgo principal:** que ampliar toda la superficie del chequeo 17 al material de referencia arrastre discrepancias ajenas (en `docs/n8n-workflow-guide.md:767`, un registro historico cita `N8N 2.25.7` frente al pin `2.11.2`). Se mitiga acotando la ampliacion a la restriccion de `google-genai`, de modo que los barridos de N8N/FastAPI/Uvicorn sigan sobre `knowledge-base/**`. El segundo riesgo es un falso positivo sobre el pasaje historico de `parameters_gemini.md`; se mitiga reutilizando la regla de exencion por rotulacion historica ya probada por los chequeos 13/14/17 (linea 101 queda exenta por el encabezado "Historial de Cambios"; la correccion exigida es la linea 5, vigente).

## Rollback

Revertir con `git revert` de los commits del change: `docs/parameters_gemini.md` vuelve a citar `>=2.31,<3`, y el chequeo de la barrera vuelve a la superficie limitada a `knowledge-base/**`. No se publica tag ni release.

## Success Criteria

- [ ] `docs/parameters_gemini.md` cita `google-genai >=2.33,<3` como valor vigente en sus DOS pasajes vigentes (lineas 5 y 101) y conserva intacta la seccion "Historial de Cambios".
- [ ] `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` esta en verde con un test nuevo que (a) falla si `parameters_gemini.md` declara `>=2.31,<3` en un pasaje no historico y (b) pasa si declara `>=2.33,<3`.
- [ ] Los barridos de N8N, FastAPI y Uvicorn siguen limitados a `knowledge-base/**`: la ampliacion no reporta la discrepancia ajena `docs/n8n-workflow-guide.md:767` (`N8N 2.25.7`).
- [ ] Con la ampliacion implementada, la barrera reportaria un FAIL si `parameters_gemini.md` declarara `2.31`; con el valor corregido, `python3 scripts/preflight/docs_stack_sync.py` sale 0 con 17/17 PASS.
- [ ] `python3 -m pytest scripts/preflight -q` en verde (sin regresiones).
- [ ] `openspec validate c-151-corregir-pin-google-genai-y-ampliar-la-barrera --strict` pasa.
