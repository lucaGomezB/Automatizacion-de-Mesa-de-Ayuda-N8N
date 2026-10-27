## Context

La barrera `scripts/preflight/docs_stack_sync.py` ejecuta 17 chequeos estaticos sobre artefactos del repositorio (c-145 y c-148). Los chequeos 4 (framework), 5 (`google-genai`) y 17 (versiones de componentes en `knowledge-base/**`) comparan la documentacion contra `App/Backend/requirements.txt` y `docker-compose.yml`; por eso el PR #42 de Dependabot no puede mergearse sin actualizar la documentacion vigilada. Ver `proposal.md` para la motivacion.

El segundo defecto es de diseno de la suite: `scripts/preflight/test_docs_stack_sync.py` construye sus fixtures copiando los archivos REALES del repositorio (`_copiar_arbol` copia `requirements.txt`, `docker-compose.yml`, `openspec/config.yaml`, `CLAUDE.md`, `knowledge-base/**`, el material de referencia y `api.ts`) y luego aplica `_sincronizar` con valores de version hardcodeados (`0.143.3`, `0.54.0`, `2.11.2`, `>=2.31,<3`). Las pruebas de deriva inyectan una sola mutacion y afirman `assert len(fails) == 1`. En cuanto el repositorio real cambia una version, `_sincronizar` deja de normalizar y aparecen FAILs adicionales de los chequeos 4, 5 y 17; la afirmacion de un unico fallo revienta (`assert 4 == 1`). La suite queda asi acoplada al estado real del repositorio: es un defecto, no una prueba.

## Goals / Non-Goals

**Goals:**

- Aplicar exactamente el bump del PR #42 en `App/Backend/requirements.txt`, sin tocar `uvicorn[standard]` ni otras lineas.
- Dejar la documentacion vigilada (config.yaml y `knowledge-base/`) declarando las versiones nuevas como hechos vigentes, conservando la historia rotulada.
- Desacoplar la suite de la barrera del estado real del repositorio, de modo que un bump legitimo no la rompa y una deriva inyectada siga aislando exactamente un FAIL.
- Mantener la barrera en verde (17/17) sobre el arbol resultante.

**Non-Goals:**

- No se modifica el codigo de la aplicacion (`App/Backend/app/`) ni el frontend.
- No se toca `docker-compose.yml` (la imagen de N8N 2.11.2 no cambia) ni los pines de `starlette` en la documentacion (solo se declara FastAPI/Uvicorn/google-genai/N8N).
- No se reescriben los registros historicos (por ejemplo la calibracion sobre `gemini-2.5-flash` o el bump de c-127); se rotulan o se acompanan con la nota del bump nuevo.
- No se re-hospeda la logica de los 17 chequeos: la suite los ejerce tal cual.

## Decisions

**D1 — Tomar el bump del PR #42 linea por linea.** Se aplican las seis actualizaciones exactas que propone `origin/dependabot/pip/App/Backend/backend-python-39ad50631f`: `fastapi==0.162.0`, `starlette==1.10.0`, `sqlalchemy[asyncio]==2.1.6`, `alembic==1.20.1`, `pydantic-settings==2.16.1`, `google-genai>=2.33.0,<3`. `uvicorn[standard]` queda en 0.54.0. Alternativa descartada: escribir versiones propias o "de paso" subir otras; el PR es la fuente y todo numero viene de ahi.

**D2 — Criterio vigente vs historico en los comentarios y la documentacion.** Un comentario que declara un HECHO VIGENTE (por ejemplo "Ultima verificada: 2.31.0" o "starlette ... 1.8.0 (par de fastapi 0.143.3)") se actualiza; un comentario que registra un HECHO HISTORICO (por ejemplo "c-127: bump a 0.143.3") se conserva y, cuando aporta, se acompana con la nota del bump nuevo. Es el mismo criterio ya establecido por c-148. Alternativa descartada: reemplazar todos los literales viejos por los nuevos (falsificaria el registro de c-127/c-97).

**D3 — Fixtures sinteticos para la suite de la barrera.** El sistema de fixtures se reescribe: `_arbol_sincronizado(tmp_path)` construye un arbol temporal autosuficiente escribiendo `settings.py`, `constants.py`, `requirements.txt`, `docker-compose.yml`, `config.yaml`, `CLAUDE.md`, los 12 archivos de `knowledge-base/**`, el material de referencia y `api.ts`, con contenido derivado de un mapa de versiones FIJO definido en la propia suite (`_VERS_BASE`). No se copia ningun archivo real. Los chequeos 1 a 17 corren sobre ese arbol. Alternativa descartada: seguir copiando el arbol real y "re-sincronizar" con valores hardcodeados; es el defecto actual, porque un bump real deja la normalizacion obsoleta.

**D4 — La fuente de verdad del fixture no es el repositorio.** Las versiones del fixture viven como constantes de la suite (`fastapi`, `uvicorn`, `n8n`, `google-genai`). Esto es lo que rompe el acoplamiento: el resultado de la suite es funcion solo de sus constantes, no de `App/Backend/requirements.txt`. La verificacion del arbol REAL queda a cargo del CLI de la barrera (`python3 scripts/preflight/docs_stack_sync.py`), que es lo que corre en CI, no de la suite. La parametrizacion `_arbol_sincronizado(tmp_path, versiones=...)` permite triangulacion: construir el arbol con versiones nuevas y comprobar que sigue sincronizado y que una deriva a un unico valor aisla un unico FAIL.

**D5 — OpenAPI: verificar antes de regenerar.** El bump de FastAPI podria alterar el esquema generado. Se ejecuta `tests/test_openapi_sync.py`; solo si falla se regenera `docs/openapi.json` con `python3 scripts/export_openapi.py` (generador canonico, `sort_keys=True`). Nunca se edita el JSON a mano. Alternativa descartada: regenerar por precaución; produciria un diff no justificado si el esquema no cambio.

**D6 — La capsula de configuracion del fixture se parsea desde su propio contenido.** El test parametrizado de duplicacion (`test_g_literal_volatil_en_claude_falla`) deriva hoy los literales prohibidos del `openspec/config.yaml` REAL. Con el fixture sintetico debe leer el `config.yaml` del fixture; se deriva del mismo mapa `_contenido_arbol` para que no haya dos copias.

## Risks / Trade-offs

- **[El bump de FastAPI cambia `docs/openapi.json`] →** se detecta con `tests/test_openapi_sync.py`; si falla, se regenera con el script canonico y se consigna en el reporte. Riesgo aceptado: es el unico fallout esperable de un bump menor de FastAPI.
- **[El piso de `pydantic>=2.14.1` no alcanza para `google-genai>=2.33.0`] →** la suite de backend (SQLite, offline) lo detecta; si falla, se anota y se sube el piso con evidencia, sin inventar la version.
- **[La suite sintetica deja de cubrir el arbol real] →** mitigado: el CLI de la barrera sigue verificando el arbol real y corre en CI (`job backend-tests`). La suite verifica la LOGICA de los chequeos; el CLI verifica el arbol.
- **[El fixture sintetico se desincroniza de los checks si estos cambian] →** mitigado reutilizando las mismas assertions y los mismos sentinelas que las pruebas actuales; cualquier cambio de check con expectativa distinta reaparece como fallo del fixture.
- **[Deriva entre el fixture y los valores que los checks derivan del runtime] →** mitigado porque el fixture es autosuficiente: los valores esperados de los checks 4/5/17 se derivan del `requirements.txt`/compose DEL FIXTURE, no del real, y ambos son coherentes por construccion.

## Migration Plan

1. Bloque A: editar `App/Backend/requirements.txt` (RED del bloque B: la barrera pasa a 14/17 con los chequeos 4, 5 y 17 en FAIL).
2. Guardar la RED de la suite desacoplada: `python3 -m pytest scripts/preflight/ -q` falla por acoplamiento con el bump aplicado.
3. Bloque C: reescribir los fixtures a sinteticos; la suite vuelve a verde con el bump aplicado (GREEN) y se triangula con versiones nuevas.
4. Bloque B: actualizar `openspec/config.yaml` y `knowledge-base/`; la barrera vuelve a 17/17 (GREEN).
5. Regenerar OpenAPI solo si `tests/test_openapi_sync.py` falla.

Rollback: `git revert` de los commits del change; no hay tag ni release.
