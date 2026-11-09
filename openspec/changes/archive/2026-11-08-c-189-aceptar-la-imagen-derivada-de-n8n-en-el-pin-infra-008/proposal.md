# Proposal: Aceptar la imagen derivada de N8N en el pin INFRA-008

## Why

El job "Backend tests (Python 3.12)" del CI falla en `main` desde el 2026-11-07 en
`App/Backend/tests/test_c62_infra_hardening.py::test_n8n_image_stays_pinned`. El test lee
`services.n8n.image` de `docker-compose.yml` y espera `n8nio/n8n:2.11.2`, pero desde c-182
(`000abeb`) el servicio `n8n` ya no declara `image`: usa `build: {context: ./docker/n8n,
dockerfile: Dockerfile}` y el pin vive en la primera linea `FROM` de `docker/n8n/Dockerfile`
(`FROM n8nio/n8n:2.11.2`). El pin NO se perdio: lo que quedo desactualizado es el contrato
INFRA-008, que enuncia la imagen literal como unico cumplimiento.

## What Changes

- **Test (`test_c62_infra_hardening.py`)**: `test_n8n_image_stays_pinned` resuelve la imagen
  efectiva con una funcion pura `resolver_imagen_n8n(services, repo_root)`: usa `image` si
  existe; si hay `build`, lee el primer `FROM` del Dockerfile del contexto (ignorando
  `--platform` y el alias `AS`). Se agregan 8 tests de triangulacion con `tmp_path`.
- **Spec (`infra-network-hardening`, INFRA-008)**: el pin de la imagen de n8n se cumple con la
  imagen literal `n8nio/n8n:2.11.2` o con un `build` cuyo Dockerfile parta `FROM` de esa misma
  imagen pineada; un `FROM` distinto (otra version, `latest`) NO cumple.

- **Preflight (`scripts/preflight/cost_readiness.py`)**: la guarda `compose: imagen del servicio n8n
  pineada a version explicita` tambien leia solo `image` (7 tests de `test_cost_readiness.py`
  fallaban en el mismo job de CI). Ahora resuelve `image` o el primer `FROM` del Dockerfile del
  `build`, relativo al directorio del compose. Spec `cost-readiness` (MODIFIED).

## Capabilities

### Modified Capabilities

- `infra-network-hardening`: requisito INFRA-008 (MODIFIED).
- `cost-readiness`: requisito "Guardas del compose verificadas por el preflight" (MODIFIED).

## Impact

- Solo test, guarda del preflight y spec. SIN cambios en `docker-compose.yml`, `docker/n8n/Dockerfile`, backend,
  nginx ni N8N (dominio C-62, gobernanza ALTA: no se toca la infraestructura).
- Rollback: revertir el commit del test y la spec.
