## Context

Ver `proposal.md` - Why. El estado actual que condiciona el diseno:

- `App/Backend/requirements.txt` fija `fastapi==0.115.0`, `pytest==8.3.3`, `pytest-asyncio==0.24.0`. No declara `starlette`: entra como dependencia transitiva de fastapi y resuelve a `0.38.6`.
- El cap que bloquea el fix esta en el metadata de fastapi: `0.115.0` declara `starlette<0.39.0,>=0.37.2`. La lista de excepciones (`scripts/security/pip_audit_exceptions.txt`) registra 7 advisories de `starlette 0.38.6` y `PYSEC-2026-1845` de `pytest 8.3.3` como "corregibles solo con actualizacion mayor rompiente", con un bloque FOLLOW-UP.
- El codigo importa `starlette` de forma directa: `app/core/error_handlers.py:25` (`starlette.exceptions.HTTPException`), `app/main.py:43` (`starlette.types`), `tests/test_c91_refresh_cookie.py:228` (`starlette.middleware.cors`).
- `App/Backend/pytest.ini` ya declara `asyncio_mode = auto` y `asyncio_default_fixture_loop_scope = function` (configuracion estilo pytest-asyncio 1.x).
- El job `security-scan` de `.github/workflows/ci.yml` convierte cada ID del archivo de excepciones en un `--ignore-vuln <ID>` explicito; no exporta los pins, solo audita `requirements.txt`.

### Verificacion de versiones en PyPI (hecha al proponer)

- fastapi: ultima publicada `0.149.0` (NO existe una 1.x pese a la nota FOLLOW-UP). La cota de starlette por version: `0.115.0` -> `<0.39.0`; `0.116.0` -> `<0.47.0`; `0.130.0` -> `<1.0.0`; `0.135.0` y posteriores -> `starlette>=0.46.0` (sin cota superior).
- starlette: versiones de fix por advisory: `1.0.1`, `1.3.1`, `1.3.0`, `0.40.0`, `0.47.2`, `1.1.0`, `1.1.0`. El maximo es `1.3.1`, por lo que limpiar las 7 exige `starlette >= 1.3.1`.
- pytest: `8.4.x` y `9.x` publicadas; la 9.x trae el fix de `PYSEC-2026-1845`.
- pytest-asyncio: `0.24.0`/`0.25.3`/`0.26.0`/`1.0.0`/`1.1.0`/`1.2.0` declaran `pytest<9`; recien `1.3.0` admite `pytest<10,>=8.2`. Por lo tanto pytest 9.x exige `pytest-asyncio >= 1.3.0`.

## Goals / Non-Goals

**Goals:**

- Definir la matriz exacta de versiones objetivo y la cadena de restricciones que la justifica.
- Determinar por adelantado la viabilidad de la actualizacion y el criterio para declararla no viable.
- Dejar explicito el plan de rollback y los riesgos de cambio de comportamiento de las majors.

**Non-Goals:**

- No se fija una version de `starlette` por encima de la minima que limpia las advisories (evitar blast radius innecesario).
- No se agrega ninguna dependencia nueva de forma directa; no se persigue adoptar opentelemetry.
- No se toca el frontend ni la politica de bloqueo del pipeline.
- No se convierte el archivo de `requirements.txt` en un lock completo.

## Decisions

### D1 - Veredicto de viabilidad: FEASIBLE

La actualizacion es viable con los pins disponibles en PyPI. No hace falta salir de Python 3.12 ni romper la cadena pydantic. La condicion de fallback de la spec (registrar no-viabilidad) NO se activa, salvo que la corrida de la suite durante el apply demuestre rotura desproporcionada (ver D6).

### D2 - Matriz de versiones objetivo

| Dependencia | Actual | Objetivo | Motivo |
|-------------|--------|----------|--------|
| `fastapi` | `0.115.0` | `0.135.0` | Primera version que levanta el cap: declara `starlette>=0.46.0` sin cota superior. |
| `starlette` | `0.38.6` (transitiva) | `1.3.1` (pin explicito) | Version minima que limpia las 7 advisories (max fix = `1.3.1`). |
| `pytest` | `8.3.3` | `9.1.1` | Limpia `PYSEC-2026-1845` (fix en 9.x). |
| `pytest-asyncio` | `0.24.0` | `1.4.0` | Requerida por pytest 9.x (`1.3.0` es el piso; `1.4.0` es la estable actual). |

Restricciones de compatibilidad verificadas:

- `fastapi 0.135.0` exige `pydantic>=2.7.0`; el proyecto ya tiene `pydantic>=2.12.5`. Sin conflicto.
- `starlette 1.3.1` exige `anyio>=3.6.2,<5` y Python >=3.10. Compatible con Python 3.12.
- `pytest-asyncio 1.4.0` exige `pytest<10,>=8.4`; `pytest 9.1.1` cumple.

### D3 - Preferir `fastapi==0.135.0` sobre `0.149.0`

`fastapi 0.135.0` es el bump minimo que habilita starlette 1.x y NO agrega dependencias obligatorias nuevas. `fastapi 0.149.0` incorpora `opentelemetry-api>=1.44.0` y `opentelemetry-sdk` como dependencias base (no opcionales), lo que amplia el arbol y la superficie de auditoria sin necesidad. Se prefiere el menor blast radius.

### D4 - Pin explicito de `starlette`

El codigo importa `starlette` directamente (D-Context), por lo que declararlo en `requirements.txt` es legitimo (mismo criterio que `python-multipart`). Se fija `starlette==1.3.1` para (a) garantizar que el fix quede aplicado y (b) evitar que pip resuelva a una `1.x` mucho mas nueva con blast radius no medido. Alternativa considerada: no declararlo y dejar que fastapi resuelva la ultima `starlette` (potencialmente `1.9.0`); se descarta por menor control y mayor superficie de regresion.

### D5 - `pytest` y `pytest-asyncio` deben subir juntos

`pytest 9.x` es incompatible con `pytest-asyncio <=1.2.0` (`pytest<9`). Subir solo pytest rompe la coleccion. Se suben en el mismo paso a `pytest==9.1.1` + `pytest-asyncio==1.4.0`. La configuracion de `pytest.ini` ya usa la API nueva (`asyncio_default_fixture_loop_scope`), lo que reduce el fallout esperado.

### D6 - Criterio de fallback

Si con la matriz de D2 la suite completa (SQLite offline) NO pasa y la rotura se concentra en APIs removidas de starlette/pytest sin un ajuste acotado, se declara NO viable: se revierte a los pins actuales y se conservan las excepciones con un FOLLOW-UP revisado. Escalation intermedia antes de ese veredicto: probar `fastapi==0.135.0` con una `starlette` mas conservadora, o subir `fastapi` a una version contemporanea de `starlette 1.3.1`. El veredicto final y su evidencia quedan en el `verify`/notas de apply.

### D7 - Poda de excepciones

Se eliminan del archivo las 7 lineas de `starlette` (PYSEC-2026-161/249/248/1943/1941/2281/2280) y la de `pytest` (PYSEC-2026-1845). Quedan solo `python-jose` (PYSEC-2026-4298) y `ecdsa` (PYSEC-2026-1325), con su motivo "sin correccion publicada". El bloque FOLLOW-UP se marca resuelto/elimina, porque era precisamente el seguimiento que este change ejecuta.

## Risks / Trade-offs

- [Rotura por starlette `0.38.6` -> `1.3.1` (major: se removieron APIs)] -> Los tres puntos de import del repo (`error_handlers`, `main`, test CORS) usan APIs estables; verificar con la suite completa. Mitigacion adicional: D4 acota la version.
- [Rotura por `pytest 9.x` (features deprecadas removidas) o `pytest-asyncio 1.x` (fixture `event_loop` eliminada)] -> `pytest.ini` ya adopta la config nueva; revisar faltantes/fixtures async en la corrida y corregir en tests.
- [Resolucion transitiva inestable: pip podria resolver una `starlette` distinta si se relaja el pin] -> D4 fija `starlette==1.3.1` de forma explicita.
- [Falso "limpio" de pip-audit por la base de datos de advisories] -> La verificacion corre `pip-audit` explicitamente y comprueba que los IDs removidos no aparezcan.
- [Impacto en la imagen Docker del backend] -> La imagen instala desde `requirements.txt`; el cambio se propaga al reconstruir. No hay pin de imagen que ajustar.

## Migration Plan

1. Baseline: correr `cd App/Backend; pytest -m "not integration" -q` y registrar el conteo de tests (safety net) antes de tocar pins.
2. Actualizar `App/Backend/requirements.txt` con la matriz de D2 (`fastapi==0.135.0`, `starlette==1.3.1`, `pytest==9.1.1`, `pytest-asyncio==1.4.0`).
3. `pip install -r App/Backend/requirements.txt`.
4. Correr la suite completa; corregir el fallout acotado.
5. Podar `scripts/security/pip_audit_exceptions.txt` (D7) y actualizar comentarios relacionados.
6. Verificar: suite completa + `pip-audit -r App/Backend/requirements.txt` (sin los IDs removidos) + `openspec validate`.

**Rollback**: revertir `App/Backend/requirements.txt` a los pins previos (`fastapi==0.115.0`, `pytest==8.3.3`, `pytest-asyncio==0.24.0`, quitar la linea de `starlette`), reinstalar y restaurar `pip_audit_exceptions.txt` desde git. El punto de retorno conocido-bueno es el commit previo al change.

## Open Questions

- Si el subconjunto de integracion PostgreSQL es ejecutable en el entorno local durante el apply; si no lo es, se reporta y se delega la cobertura a CI (no cambia specs, enfoque ni tareas).
- Si `pip-audit` esta disponible localmente para la verificacion; si no, se instala en un entorno aislado o se confia en el job `security-scan` de CI.
