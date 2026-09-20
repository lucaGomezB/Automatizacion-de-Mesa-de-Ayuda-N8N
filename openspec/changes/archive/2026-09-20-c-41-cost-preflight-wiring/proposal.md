## Why

El preflight de preparacion de costo (`scripts/preflight/cost_readiness.py`, 10 guardas, salida 0 solo si todas pasan) existe desde c-36 pero NO esta cableado a ningun camino automatico: ni `scripts/up.sh`, ni el `Makefile`, ni CI lo ejecutan. Un operador puede arrancar el stack con una guarda de costo rota y no se entera hasta que el gasto pago ya esta habilitado. Ademas, `scripts/up.sh` verifica `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY` pero no `JWT_SECRET_KEY`, que `Settings()` exige (`App/Backend/app/config/settings.py:108`); un `.env` sin JWT pasa el preflight de arranque y luego el backend crashea al construir la configuracion.

## What Changes

- **Cableado del preflight al arranque local**: `scripts/up.sh` ejecuta `scripts/preflight/cost_readiness.py` antes de tocar Docker; si el preflight falla, imprime el resumen (nombra las guardas en FAIL), emite un error accionable y termina con exit code distinto de cero sin arrancar el stack ni generar certificados. Modo de fallo no destructivo: el preflight es de solo lectura y el aborto ocurre antes de cualquier efecto.
- **Paridad Windows**: `scripts/up.ps1` recibe el mismo gate y la misma verificacion de `JWT_SECRET_KEY` para no romper el requisito de equivalencia multiplataforma de `local-bootstrap`.
- **Chequeo de `JWT_SECRET_KEY`**: se agrega a la lista de secretos requeridos del preflight de entorno (presencia, no vacio, no placeholder), en `scripts/up.sh` y `scripts/up.ps1`.
- **Objetivo `preflight` en el Makefile**: invocacion manual discoverable del preflight, sin Docker ni red.
- **CI**: el job `backend-tests` instala `scripts/preflight/requirements.txt` y ejecuta la suite `scripts/preflight/test_cost_readiness.py` y el CLI del preflight, cerrando el follow-up que c-36 dejo abierto ("el preflight no corre en CI").
- **Tests**: se extiende `scripts/tests/test_up_preflight.sh` con los casos de JWT y con un stub del preflight para probar el gate del arranque (falla -> no arranca; pasa -> continua).

**Fuera de alcance**: no se modifica la logica de guardas de `cost_readiness.py` (ya es callable por CLI, no requiere refactor); no se tocan los defectos de wiring de N8N (c-40) ni la instrumentacion de tiempos (c-39); no se toca el gate de corrida paga de evaluacion.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cost-readiness`: se agrega el requisito de que el preflight este cableado a los caminos automaticos (gate de arranque local en ambos scripts, objetivo `preflight` del Makefile, ejecucion en CI), con su modo de fallo no destructivo.
- `local-bootstrap`: el requisito de preflight de entorno incorpora `JWT_SECRET_KEY` junto a `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `scripts/up.sh` | Modified | Gate del preflight de costo + `JWT_SECRET_KEY` en secretos requeridos; seam de test `UP_COST_PREFLIGHT`/`UP_PYTHON` |
| `scripts/up.ps1` | Modified | Paridad: mismo gate y mismo chequeo de JWT |
| `Makefile` | Modified | Objetivo `preflight` (solo lectura, sin Docker) |
| `.github/workflows/ci.yml` | Modified | Paso que instala PyYAML y corre la suite + CLI del preflight |
| `scripts/tests/test_up_preflight.sh` | Modified | Casos de JWT y de gate del preflight con stub |
| `scripts/preflight/cost_readiness.py` | Sin cambios | Ya expone CLI con exit code 0/1; no necesita refactor |
| `openspec/specs/cost-readiness/spec.md`, `openspec/specs/local-bootstrap/spec.md` | Delta | Requisitos nuevos/modificados |

- **Gobernanza**: LOW/MEDIUM (herramientas de operacion, sin logica de dominio ni secretos reales). No hay checkpoint HIGH/CRITICAL obligatorio; el cambio es de solo lectura sobre el stack.
- **Dependencias**: c-36 (preflight y guardas verificadas, archivada). Los cambios hermanos c-39 y c-40 son independientes; c-41 no depende de ellos.
- **Riesgo operativo**: el gate introduce una dependencia de PyYAML en el arranque; se mitiga con un mensaje accionable que apunta a `scripts/preflight/requirements.txt`.
