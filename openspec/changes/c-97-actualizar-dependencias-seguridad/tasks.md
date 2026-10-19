# Tasks: c-97 — Actualizar dependencias de seguridad

> **Leer antes**
> - `proposal.md` y `design.md` de este change (matriz de versiones en D2, criterio de fallback en D6).
> - `scripts/security/pip_audit_exceptions.txt` (bloque FOLLOW-UP: es lo que este change ejecuta).
> - `App/Backend/requirements.txt` (pins actuales: `fastapi==0.115.0`, `pytest==8.3.3`, `pytest-asyncio==0.24.0`).
> - `.github/workflows/ci.yml` (job `security-scan`, como se aplican las excepciones por ID).
> - `openspec/specs/ci-pipeline/spec.md` y `openspec/specs/supply-chain-security/spec.md` (politica vigente).
> - `AGENTS.md` (comandos exactos del backend; el subconjunto de integracion requiere PostgreSQL).
>
> **Convencion de rutas**: `R = App/Backend/requirements.txt`, `E = scripts/security/pip_audit_exceptions.txt`.
> **Governance MEDIO**: implementar con checkpoints; registrar en las notas de apply cualquier decision no obvia.
> **Fallback valido (D6)**: si la suite no pasa con la matriz de D2 y la rotura no es acotada, declarar NO viable, revertir los pins y mantener las excepciones con FOLLOW-UP revisado. No forzar la subida.

## 1. Safety net y baseline

- [x] 1.1 Baseline pre-change documentado: `1449 passed, 48 deselected, 1 xfailed` con los pins VIEJOS, verificado en esta sesion antes de bumpear. No se re-corre porque los pins ya estan bumpeados (una corrida pre-change real es imposible ahora). Verificacion: la corrida termino en verde y el conteo queda registrado.
- [x] 1.2 Baseline de auditoria: los 8 IDs (`PYSEC-2026-161/249/248/1943/1941/2281/2280` y `PYSEC-2026-1845`) fueron registrados cuando c-64 creo el archivo de excepciones; con los pins nuevos ya NO aparecen. Limitacion local: `pip-audit -r` no corre en este box (falta ensurepip: no puede crear venv temporal) y con `--no-deps --disable-pip` exige pins exactos (el requirements usa rangos). Fallback best-effort: la auditoria del entorno instalado no reporta advisories para `fastapi`, `starlette`, `pytest` ni `pytest-asyncio`. La verificacion autoritativa queda delegada al job `security-scan` de CI.

## 2. Actualizacion de dependencias

- [x] 2.1 Editar `R` con la matriz de D2: `fastapi==0.135.0`, `starlette==1.3.1`, `pytest==9.1.1`, `pytest-asyncio==1.4.0`, ajustando el comentario de cada linea para registrar el motivo. Verificacion: `pip install -r App/Backend/requirements.txt` resuelve sin conflicto y `pip check` no reporta incompatibilidades. Hecho por el orquestador; re-confirmado en esta sesion (`python3 -m pip check` = "No broken requirements found").
- [x] 2.2 Confirmar las versiones efectivamente instaladas y que `starlette >= 1.3.1`: `cd App/Backend; python -c "import fastapi, starlette, pytest; print(fastapi.__version__, starlette.__version__, pytest.__version__)"`. Verificacion: la salida muestra `fastapi 0.135.0`, `starlette 1.3.1` y `pytest 9.1.1`. Re-confirmado: `0.135.0 1.3.1 9.1.1` (pytest-asyncio `1.4.0`).

## 3. Correccion del fallout de las actualizaciones

- [x] 3.1 Correr la suite offline completa: `cd App/Backend; pytest -m "not integration" -q`. Verificacion: verde con el mismo conteo que la linea base 1.1 (o mayor, sin fallos). Resultado: `1449 passed, 48 deselected, 1 xfailed` — iguala la linea base 1.1. (1 corrida intermedia fallo SOLO en `test_openapi_sync.py` por el fallout de FastAPI 0.135; ver 3.2.)
- [x] 3.2 Corregir en el codigo de aplicacion la rotura causada por starlette 1.x si aparece (puntos de import conocidos: `app/core/error_handlers.py`, `app/main.py`). Verificacion: los imports resuelven y los tests que los ejercitan pasan. Resultado: NO aparecio rotura de imports por starlette 1.x (los tres puntos resuelven). El unico fallout de la actualizacion fue en la generacion del schema OpenAPI de FastAPI 0.135 (las Form con `alias` ahora se emiten con el alias como clave y `ValidationError` ahora expone `ctx`/`input`); se corrigio regenerando `docs/openapi.json` con el generador canonico `python3 scripts/export_openapi.py` (mismo procedimiento documentado en `AGENTS.md` y en el docstring del script). Sin cambios en codigo de aplicacion.
- [x] 3.3 Corregir en los tests la rotura causada por pytest 9.x / pytest-asyncio 1.x si aparece (p. ej. `event_loop`, fixtures async, coleccion). Verificacion: la coleccion no reporta errores y la suite offline pasa. Resultado: NO aparecio rotura; la coleccion es limpia y la suite pasa. `pytest.ini` ya usa la API nueva (`asyncio_mode = auto`, `asyncio_default_fixture_loop_scope = function`).
- [x] 3.4 Si hay PostgreSQL disponible, correr el subconjunto de integracion: `cd App/Backend; pytest -m integration`. Si no lo hay, registrar la limitacion en las notas de apply y delegar la cobertura a CI. Verificacion: el subconjunto pasa o la limitacion queda documentada. Resultado: PostgreSQL reachable (`mesa_local-postgres-1`, healthy, 127.0.0.1:5433); corrida contra la DB desechable autoprovisionada (`mesa_de_ayuda_test`, `TEST_PG_URL` sin setear): `48 passed, 1450 deselected`.

## 4. Poda de excepciones y documentacion

- [x] 4.1 Quitar de `E` las 7 lineas de `starlette` (PYSEC-2026-161/249/248/1943/1941/2281/2280) y la de `pytest` (PYSEC-2026-1845), dejando solo `python-jose` (PYSEC-2026-4298) y `ecdsa` (PYSEC-2026-1325). Verificacion: `E` lista unicamente esos dos IDs con su motivo. Hecho: el cuerpo del archivo contiene solo `PYSEC-2026-4298` y `PYSEC-2026-1325`.
- [x] 4.2 Actualizar/eliminar el bloque FOLLOW-UP de `E` (era el seguimiento que este change ejecuta) y ajustar el encabezado para reflejar que la lista ya solo contiene hallazgos sin correccion publicada. Verificacion: el archivo no conserva referencias a las excepciones removidas. Hecho: bloque FOLLOW-UP eliminado; encabezado reescrito para declarar que solo se exceptuan hallazgos sin correccion publicada.
- [x] 4.3 Actualizar cualquier comentario o doc que referenciara las excepciones removidas (p. ej. comentarios del job `security-scan` en `.github/workflows/ci.yml` y comentarios de pins en `R`). Verificacion: `rg -n "PYSEC-2026-1845|starlette 0.38.6" scripts/ .github/ App/Backend/` no devuelve referencias obsoletas. Hecho: comentarios del job `security-scan` (encabezado y step de pip-audit) actualizados a la politica de solo "sin correccion publicada"; comentario de `pytest` en `R` marcado como historico. `rg` solo devuelve esa nota historica, sin referencias obsoletas.

## 5. Verificacion final

- [x] 5.1 Correr la suite completa del backend y confirmar verde: `cd App/Backend; pytest -m "not integration" -q` (y el subconjunto de integracion si el entorno lo permite). Verificacion: sin fallos. Resultado: corrida completa verificada por el orquestador DESPUES del upgrade y de la regeneracion de `docs/openapi.json`: `1449 passed, 48 deselected, 1 xfailed` (iguala la linea base 1.1); no se re-corre. Verificacion adicional barata: `pytest tests/test_openapi_sync.py -q` = `5 passed` (la poda es un archivo de texto, no puede afectar la suite).
- [x] 5.2 Correr `pip-audit -r App/Backend/requirements.txt` y confirmar que los IDs removidos NO aparecen y que no hay hallazgos nuevos no exceptuados. Verificacion: los 8 IDs a limpiar estan ausentes; solo quedan `PYSEC-2026-4298` y `PYSEC-2026-1325`. Resultado: LIMITACION LOCAL confirmada; `pip-audit -r` falla con "The virtual environment was not created successfully because ensurepip is not available" (falta `python3.12-venv`) y `--no-deps --disable-pip` falla con "requirement pydantic is not pinned to an exact version" (el requirements usa rangos). La auditoria del entorno global no es representativa (incluye paquetes del sistema ajenos al proyecto). Verificacion por inspeccion: los 8 IDs removidos ya no estan en `E`; solo quedan los 2 IDs sin correccion; versiones instaladas confirmadas `fastapi 0.135.0`, `starlette 1.3.1`, `pytest 9.1.1`, `pytest-asyncio 1.4.0`. La verificacion autoritativa queda en el job `security-scan` de CI.
- [x] 5.3 Correr `openspec validate --strict c-97-actualizar-dependencias-seguridad` y `openspec validate --strict --changes`. Verificacion: 0 fallos. Resultado: change individual valido; `--changes` = `11 passed, 0 failed`.
