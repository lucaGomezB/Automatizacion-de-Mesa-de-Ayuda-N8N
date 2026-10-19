## Why

La lista de excepciones de `pip-audit` (`scripts/security/pip_audit_exceptions.txt`, c-64) registra 10 hallazgos: 8 de ellos figuran como "corregibles solo mediante una actualizacion mayor rompiente" (7 advisories de `starlette 0.38.6` via `fastapi 0.115`, y `pytest 8.3.3` via `PYSEC-2026-1845`) con un seguimiento (FOLLOW-UP) declarado deuda tecnica pendiente. Mantener esa deuda sin resolver engrosa la superficie de vulnerabilidades mitigada solo por excepcion. Este change ejecuta ese seguimiento: sube las dependencias afectadas para limpiar los 8 hallazgos, dejando la lista de excepciones con unicamente los hallazgos sin correccion publicada.

## What Changes

- **Actualizacion de dependencias backend (T)**: subir los pins de `App/Backend/requirements.txt` que habilitan los fixes: `fastapi` a una version que levante el cap `starlette<0.39` (>= `0.135.0`, que admite `starlette` 1.x), de modo que `starlette` resuelva a >= `1.3.1`; y `pytest` a 9.x con un `pytest-asyncio` compatible (>= `1.3.0`, que admite `pytest<10`). Se registra la matriz exacta de versiones y las restricciones de compatibilidad en `design.md`.
- **Correccion de fallout (T)**: instalar las nuevas versiones y correr la suite completa del backend (SQLite offline y, si es viable, el subconjunto PostgreSQL `@pytest.mark.integration`). Corregir la rotura causada por las actualizaciones en codigo de aplicacion y/o de tests, sin refactors ajenos al cambio.
- **Poda de excepciones (T)**: quitar de `scripts/security/pip_audit_exceptions.txt` las 7 advisories de `starlette` y `PYSEC-2026-1845` de `pytest`, dejando unicamente `python-jose` y `ecdsa` (sin correccion publicada) con su motivo. Actualizar el bloque FOLLOW-UP (marcarlo resuelto/eliminado) y cualquier comentario o doc que referenciara las excepciones removidas.
- **Verificacion (T)**: correr la suite completa y `pip-audit -r App/Backend/requirements.txt` confirmando que los IDs removidos ya no aparecen, y `openspec validate`.

### Condicion de viabilidad (fallback valido)

Si la actualizacion mayor NO es viable sin rotura desproporcionada, el design MUST registrar esa conclusion con evidencia y recomendar mantener las excepciones con un FOLLOW-UP revisado. Este fallback es un resultado valido del change, no un fracaso.

### Out of scope (no-goals)

- NO se refactoriza codigo ajeno a la rotura causada por las subidas de version.
- NO se tocan las advisories de npm del frontend (`npm audit` opera en modo reporte; es un concern separado).
- NO se agregan capacidades nuevas ni se cambia la politica de bloqueo del pipeline.
- NO se resuelven `python-jose` ni `ecdsa` (sin fix publicado; fuera de alcance).

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `supply-chain-security`: se agrega el requisito de resolver las excepciones de auditoria que solo requieren una actualizacion mayor rompiente, subiendo las dependencias afectadas y reduciendo la lista de excepciones a los hallazgos sin correccion publicada.
- `ci-pipeline`: se ajusta el requisito del job de escaneo para que la lista de excepciones de la auditoria del backend contenga unicamente hallazgos sin correccion publicada (los corregibles solo con actualizacion mayor rompiente quedan resueltos, no exceptuados).

## Impact

- **Dependencias**: `App/Backend/requirements.txt` (`fastapi`, `pytest`, `pytest-asyncio`; `starlette` resuelto transitivamente).
- **Politica de excepciones**: `scripts/security/pip_audit_exceptions.txt` (poda de IDs y actualizacion del bloque FOLLOW-UP).
- **Potencial codigo de aplicacion/tests**: solo los ajustes necesarios para absorber la rotura de las actualizaciones mayores (`App/Backend/app/`, `App/Backend/tests/`).
- **Documentacion**: comentarios en `requirements.txt` y en el job `security-scan` de `.github/workflows/ci.yml` que referencien las excepciones removidas.
- **Sin cambios**: `.github/workflows/ci.yml` mantiene su politica de bloqueo (no se altera el mecanismo de excepciones, solo su contenido); no se toca el frontend.
