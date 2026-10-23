## Why

Dependabot mantiene activos tres PRs (#32 github-actions, #33 backend-python, #34 frontend-npm) y sigue proponiendo saltos de version MAYOR que el proyecto no puede adoptar a ciegas: fija versiones exactas (ver `AGENTS.md`, `App/Backend/requirements.txt`, `App/Frontend/package.json`) y un salto de mayor rompe pruebas o la instalacion (p.ej. #33 sqlalchemy 2.0->2.1 / structlog 24->26 / cryptography 43->50 / bcrypt 4->5, que rompio un test; #34 React 18->19 / eslint 9->10, que rompio `npm ci`). Esto satura la cola de PRs con cambios no accionables y oculta las actualizaciones menores/parche que si importan.

## What Changes

- `.github/dependabot.yml`: declarar explicitamente los tres ecosistemas (`pip` en `/App/Backend`, `npm` en `/App/Frontend`, `github-actions` en `/`), preservando `version: 2`, `schedule.interval: weekly` y los `groups` por ecosistema que ya existen.
- `.github/dependabot.yml`: agregar a cada ecosistema una regla `ignore` que excluya las actualizaciones de version mayor (`dependency-name: "*"` + `update-types: [version-update:semver-major]`).
- Resultado: Dependabot deja de proponer saltos de version mayor; las actualizaciones menores y de parche siguen proponiendose. Las migraciones de mayor se gestionan con changes OpenSpec explicitos (c-127 backend, c-128 frontend).

No hay cambio de codigo de aplicacion.

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `supply-chain-security`: la requirement "Actualizacion automatizada de dependencias con Dependabot" pasa a exigir, ademas de las tres entradas con programacion semanal y agrupacion, la exclusion explicita de las actualizaciones de version mayor en cada ecosistema.

## Impact

- Archivo afectado: `.github/dependabot.yml` (unico cambio de comportamiento).
- Sin cambios en `.github/workflows/ci.yml`, `App/Backend/`, `App/Frontend/` ni `docker-compose.yml`.
- Proceso: la cola de PRs de Dependabot se reduce a menores/parche accionables; los PRs de mayor abiertos (#33/#34) quedan cubiertos por c-127/c-128.
