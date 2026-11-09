# Tasks: Aceptar la imagen derivada de N8N en el pin INFRA-008

## 1. Test (Strict TDD)

- [x] 1.1 Red de seguridad: `pytest tests/test_c62_infra_hardening.py` = 30 passed, 1 failed (`test_n8n_image_stays_pinned`).
- [x] 1.2 RED: 8 tests de `resolver_imagen_n8n` (imagen literal, build con FROM pineado, contexto como cadena, alias `AS`, sin image ni build, `latest`, otra version, sin Dockerfile) y el test del pin real apuntando al resolver; 9 fallan con `NameError`.
- [x] 1.3 GREEN: `resolver_imagen_n8n` + regex `_FROM_LINE` en el test; 39 passed.
- [x] 1.4 REFACTOR: `ruff check` limpio; sin duplicacion.

## 1b. Guarda del preflight (misma causa; Strict TDD)

- [x] 1b.1 Red de seguridad: `pytest scripts/preflight -q` = 7 failed, 108 passed (guarda `_check_pinned_image` de `cost_readiness.py` solo leia `image`; el CI corre ambas suites).
- [x] 1b.2 RED: 7 tests nuevos de la guarda con `build` (FROM pineado, `latest`, sin etiqueta, sin Dockerfile, sin FROM, alias + `--platform`, `build` como cadena) mas sin image ni build; la fixture `_write_compose` copia el Dockerfile real junto al compose de `tmp_path`.
- [x] 1b.3 GREEN: `_resolve_n8n_image` + `_FROM_LINE` en `cost_readiness.py`; `check_compose` pasa el directorio del compose. 123 passed.
- [x] 1b.4 REFACTOR: `ruff check scripts/preflight` limpio; `test_c62_infra_hardening.py` sigue en 39 passed.
- [x] 1b.5 Delta spec MODIFIED de `cost-readiness` (guardas del compose) y sincronizacion de `openspec/specs/cost-readiness/spec.md`.

## 2. Spec y verificacion

- [x] 2.1 Delta spec MODIFIED de INFRA-008 con los escenarios de imagen literal, build con FROM pineado y build con FROM distinto.
- [x] 2.2 Suite completa del backend sin regresiones respecto del baseline (los errores restantes son los tests de integracion PostgreSQL, que requieren `TEST_PG_URL`, y 3 hashes de la migracion 001 sensibles al CRLF local).
- [x] 2.3 `openspec validate --specs` OK.

## 3. Archive

- [x] 3.1 Archivar y sincronizar `infra-network-hardening`; registrar la FASE 54 en `CHANGES.md`.
