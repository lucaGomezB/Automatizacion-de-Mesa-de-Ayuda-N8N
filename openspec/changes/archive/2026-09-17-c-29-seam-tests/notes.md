# c-29-seam-tests — Notas de implementation (fase RED)

## 1. Línea base (safety net)

Capturada ANTES de tocar `App/Backend/tests/conftest.py` y `App/Backend/pytest.ini`.

| Suite | Comando | Resultado base |
|-------|---------|----------------|
| Backend (sin PostgreSQL) | `cd App/Backend; pytest -q` | `267 passed, 18 skipped, 1 xfailed` |
| Frontend | `cd App/Frontend; npm run test` | `21 files passed, 112 tests passed` |
| Backend integración (CON PostgreSQL) | `cd App/Backend; pytest -m integration -q` | `4 failed, 14 error lines (13 tests), 269 deselected` — 17 tests de marker `integration` en rojo por `RuntimeError: ... got Future ... attached to a different loop` / `InterfaceError` de asyncpg |

El conteo base del backend coincide con el enunciado (267 passed / 18 skipped, más el xfail preexistente).
El conteo base del frontend coincide con el enunciado (112 passed).

## 2. Declaración metodológica

Cualquier test que pase de VERDE a ROJO por una costura recién expuesta (por ejemplo, al habilitar
`PRAGMA foreign_keys=ON` en SQLite o al reparar el event loop de la suite PostgreSQL) es un
**hallazgo RED intencional** de esta fase TDD. NO es una regresión. NO se silencia, NO se saltea
y NO se debilita ninguna aserción para forzar el verde.

La única suite que debe quedar en verde con estos cambios de infraestructura es la que ya estaba
en verde y no depende de las costuras: los tests SQLite preexistentes. Los tests NUEVOS de costura
nacen en ROJO por diseño (codifican el comportamiento correcto contra un sistema roto).

## 3. Hallazgos RED

(pendiente de completar durante la implementación de los grupos 4, 5, 6 y 7)