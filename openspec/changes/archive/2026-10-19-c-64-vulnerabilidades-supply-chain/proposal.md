## Why

El proyecto no gestiona vulnerabilidades ni cadena de suministro: no hay Dependabot, no hay auditoria de dependencias ni SAST en CI, el pinning de dependencias e imagenes es parcial y no existe evaluacion de seguridad de proveedores. El modelado de amenazas ya registra la brecha como mitigacion pendiente (`docs/seguridad/modelado-amenazas-sdlc.md:56`: "Dependencias sin control de CVE; sin SBOM/SAST -> 8.8, 8.28, 8.29 -> C-64") y el gap assessment la lista entre las brechas criticas (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md:63,140,159`). C-64 cierra esa brecha como valor de defensa y anexo: **la tesis NO afirma seguridad de cadena de suministro**; este change agrega controles mapeados a ISO/IEC 27002:2022 8.8, 8.28, 8.29 y 5.19-5.23, con el lenguaje de alineacion del plan de cumplimiento.

## What Changes

- **Dependabot (T)**: agregar `.github/dependabot.yml` con los ecosistemas `pip` (raiz de `App/Backend/`), `npm` (raiz de `App/Frontend/`) y `github-actions` (raiz del repositorio), con una programacion semanal y actualizaciones agrupadas.
- **Escaneo de seguridad en CI (T)**: agregar un job de escaneo al pipeline existente (`.github/workflows/ci.yml`) que ejecute `pip-audit` sobre las dependencias del backend, `bandit` (SAST) sobre el codigo del backend y `npm audit` sobre las dependencias del frontend. Se define de forma explicita la politica de bloqueo de cada escaneo y su justificacion.
- **Pinning de dependencias e imagenes (T)**: llevar las imagenes Docker publicadas por `docker-compose.yml` a versiones fijas (`nginx:alpine` -> version explicita; `ngrok/ngrok:latest` -> version explicita). Para los rangos de `App/Backend/requirements.txt` y `App/Frontend/package.json` se evalua la mejora mas segura sin romper builds: NO se convierten a pins duros a ciegas; se documenta el tradeoff y se fija solo lo de bajo riesgo. La decision y las alternativas descartadas quedan en `design.md`.
- **Evaluacion de seguridad de proveedores (D)**: agregar `docs/seguridad/evaluacion-seguridad-proveedores.md` con la postura de seguridad y las clausulas a evaluar de Twilio, Gemini, Microsoft y N8N, usando el lenguaje de alineacion ("alineado con" / "controles mapeados a") y SIN afirmar "compliant" ni "certificado". Se registra en el indice de `docs/seguridad/README.md` y en el mapa de trazabilidad (5.19-5.23).
- **Trazabilidad de gobernanza (D)**: actualizar `docs/seguridad/README.md` para listar el nuevo documento y mapear los controles 5.19-5.23.

### Out of scope (no-goals)

- **trivy (escaneo de imagenes) y SBOM**: EVALUADOS y DIFERIDOS. No se implementan en este change. Motivo: el costo de red/complejidad en CI frente al valor como anexo no lo justifica hoy; la decision y su encuadre quedan documentados en `design.md`.
- NO se implementa DAST ni pruebas de penetracion: fuera de alcance.
- NO se implementan formacion en seguridad, NDA ni controles de trabajo remoto: competen a la organizacion adoptante.
- NO se usa lenguaje de "compliant" ni "certificado"; NO se declara certificacion ISO/NIST.
- NO se persigue seguridad de cadena de suministro como afirmacion de la tesis: es valor de defensa y anexo.

## Capabilities

### New Capabilities

- `supply-chain-security`: gestion de vulnerabilidades y cadena de suministro del repositorio: configuracion de Dependabot, politica de pinning de dependencias e imagenes Docker, y la trazabilidad de las decisiones de alcance diferido (trivy/SBOM).

### Modified Capabilities

- `ci-pipeline`: se agrega un job/steps de escaneo de seguridad (auditoria de dependencias y SAST) al workflow de integracion continua, con su politica de bloqueo.
- `security-governance-docs`: se agrega el requisito de la evaluacion de seguridad de proveedores (`docs/seguridad/evaluacion-seguridad-proveedores.md`) y se extiende el mapa de trazabilidad del indice con los controles 5.19-5.23.

## Impact

- **Configuracion nueva**: `.github/dependabot.yml`.
- **Workflow**: `.github/workflows/ci.yml` (nuevo job de escaneo de seguridad).
- **Docker**: `docker-compose.yml` (pinning de `nginx` y `ngrok`).
- **Dependencias**: `App/Backend/requirements.txt`, `App/Frontend/package.json` (evaluacion documentada; fijado conservador de bajo riesgo).
- **Documentacion**: `docs/seguridad/evaluacion-seguridad-proveedores.md` (nuevo), `docs/seguridad/README.md` (indice y trazabilidad).
- **Sin cambios de codigo de aplicacion**: no se toca `App/Backend/app/` ni `App/Frontend/src/`.
