# Proposal: c-149-actualizar-dependencias-y-endurecer-la-barrera

## Why

El PR #42 de Dependabot (`dependabot/pip/App/Backend/backend-python-39ad50631f`) propone un bump de dependencias de `App/Backend/requirements.txt` que NO puede mergearse tal cual: cambia versiones que la documentacion vigilada esta obligada a espejar, de modo que la barrera `scripts/preflight/docs_stack_sync.py` lo rechaza correctamente (chequeos 4, 5 y 17 en FAIL). Hay, ademas, un segundo defecto acoplado: la propia suite de la barrera (`scripts/preflight/test_docs_stack_sync.py`) lee los archivos REALES del repositorio (`requirements.txt`, `docker-compose.yml`, `openspec/config.yaml`) como linea base e inyecta una unica deriva esperando exactamente un FAIL (`assert len(fails) == 1`); por eso CUALQUIER bump legitimo de dependencias la rompe con `assert 4 == 1`. Un change que solo tomara el bump naufragaria igual en su propia suite de pruebas.

## What Changes

- **Bloque A — tomar el bump de Dependabot (BAJO).** Aplicar en `App/Backend/requirements.txt` las mismas versiones que propone el PR #42: `fastapi` 0.143.3 -> 0.162.0, `starlette` 1.8.0 -> 1.10.0, `sqlalchemy[asyncio]` 2.1.5 -> 2.1.6, `alembic` 1.20.0 -> 1.20.1, `pydantic-settings` 2.16.0 -> 2.16.1, `google-genai` `>=2.31.0,<3` -> `>=2.33.0,<3`. NO se toca `uvicorn[standard]` (0.54.0) ni ninguna otra linea. Se conservan los comentarios y se actualizan los que citan una version como hecho vigente y quedarian falsos.
- **Bloque B — espejar las versiones nuevas en la documentacion vigilada (MEDIO).** Actualizar `openspec/config.yaml` (`stack.backend.framework`, `stack.inference.model`) y `knowledge-base/02_descripcion_general.md` y `knowledge-base/09_decisiones_y_supuestos.md` para que declaren las versiones nuevas. Criterio del repositorio: un valor que es un HECHO VIGENTE se actualiza; un REGISTRO HISTORICO se rotula como historia y no se falsifica. Si el bump de FastAPI cambia la salida OpenAPI, se regenera `docs/openapi.json` con el generador canonico (nunca a mano).
- **Bloque C — endurecer la suite de la barrera (MEDIO, codigo, TDD estricto).** Reescribir el sistema de fixtures de `scripts/preflight/test_docs_stack_sync.py` para que construya un ARBOL SINTETICO autosuficiente (settings, constantes, requirements, compose, `config.yaml`, `CLAUDE.md`, `knowledge-base/**`, material de referencia y `api.ts`), con versiones FIJAS definidas en la propia suite, desacoplado del estado real del repositorio. Los chequeos 1 a 17 se ejercitan sobre ese arbol; una deriva inyectada debe aislar exactamente un FAIL, y un bump coordinado de versiones debe seguir dando cero hallazgos. Se agregan pruebas de aislamiento que fijan esa propiedad.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-documentation`: se modifica el requisito `DOC-005 — Stack declarado en la documentacion para agentes sincronizado con el codigo` para (a) actualizar el valor vigente de la restriccion de `google-genai` a `>=2.33,<3`, coherente con el bump del PR #42, y (b) exigir que la suite de la barrera sea HERMETICA: sus fixtures NO SHALL depender de las versiones reales de `requirements.txt`, `docker-compose.yml` ni `openspec/config.yaml`, de modo que un bump legitimo de dependencias no la rompa, y una unica deriva inyectada MUST seguir aislando exactamente un hallazgo.

## Impact

- **Edita:** `App/Backend/requirements.txt`; `openspec/config.yaml`; `knowledge-base/02_descripcion_general.md`; `knowledge-base/09_decisiones_y_supuestos.md`; `scripts/preflight/test_docs_stack_sync.py`; `CHANGES.md`. Condicionalmente `docs/openapi.json` si el bump de FastAPI cambia la salida del esquema.
- **No toca:** el codigo de `App/Backend/app/`, `App/Frontend/`, `n8n/`, `docker-compose.yml`, las cinco cadenas de categoria, los numeros canonicos de la tesis, ni `CLAUDE.md` (ya remite a `config.yaml` sin restatear los literales).
- **Gobernanza:** A BAJO (bump de dependencias menor/parche); B MEDIO (documentacion con valor de evidencia para la tesis); C MEDIO (codigo de la barrera y su suite, TDD estricto).
- **Dependencias:** la barrera y su suite creadas por c-145 y ampliadas por c-148 (17 chequeos, 108 pruebas en `scripts/preflight`). Los chequeos 4, 5 y 17 son los que hoy bloquean el PR #42.
- **Riesgo principal:** el bump de FastAPI 0.143.3 -> 0.162.0 podria alterar `docs/openapi.json`; se verifica con `tests/test_openapi_sync.py` y, si falla, se regenera con `scripts/export_openapi.py`. El bump tambien podria exigir una `pydantic` mas nueva; se verifica que la suite de backend siga verde sin tocar el codigo.

## Rollback

Revertir con `git revert` de los commits del change: `requirements.txt` vuelve a 0.143.3/1.8.0/2.1.5/1.20.0/2.16.0/`>=2.31.0,<3`, la documentacion vuelve a las versiones anteriores y la suite de la barrera vuelve al sistema de fixtures acoplado. No se publica tag ni release.

## Success Criteria

- [ ] `App/Backend/requirements.txt` declara exactamente las versiones del PR #42 y `uvicorn[standard]==0.54.0` sin cambios.
- [ ] `python3 scripts/preflight/docs_stack_sync.py` sale 0 con 17/17 PASS sobre el arbol resultante.
- [ ] `python3 -m pytest scripts/preflight/ -q` esta en verde con el bump aplicado y con el arbol REAL sin bump: la suite ya no depende del estado real del repositorio.
- [ ] Un bump de version en la entrada de un fixture sintetico sigue aislando exactamente un FAIL inyectado.
- [ ] `openspec validate c-149-... --strict` pasa.
