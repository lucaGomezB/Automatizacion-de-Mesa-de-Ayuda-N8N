## 1. Preparación y verificación de prerequisitos

- [x] 1.1 Verificar que `Frontend/package-lock.json` está versionado en git; si falta, generarlo con `npm install` en `Frontend/` y commitearlo (es prerequisito de `npm ci` y del caché de npm)
- [x] 1.2 Medir localmente las violaciones de ruff sobre `Gestion_Incidentes/` (`pip install ruff==<pin>` + `ruff check .` desde `Gestion_Incidentes/`) para calibrar una config que el código actual ya cumpla
- [x] 1.3 Medir localmente las violaciones de ESLint que generaría una config base TS+React sobre `Frontend/src/` para calibrar reglas permisivas

## 2. Lint del backend (ruff)

- [x] 2.1 Crear `Gestion_Incidentes/ruff.toml` con configuración mínima y permisiva (`target-version = "py312"`, subconjunto de reglas que el código actual pasa según la medición de 1.2)
- [x] 2.2 Verificar que `ruff check .` pasa en limpio desde `Gestion_Incidentes/` con esa config (no debe marcar la corrida como fallida por deuda preexistente)

## 3. Lint del frontend (ESLint)

- [x] 3.1 Agregar ESLint y los plugins/parsers para TS + React (typescript-eslint, eslint-plugin-react, eslint-plugin-react-hooks) como `devDependencies` en `Frontend/package.json`, fijados a versiones compatibles con TS 5.5 / Vite 5
- [x] 3.2 Crear `Frontend/eslint.config.js` (flat config) calibrado permisivo según la medición de 1.3 (reglas conflictivas a `warn` o desactivadas)
- [x] 3.3 Agregar el script `lint` (`eslint .`) a `Frontend/package.json`
- [x] 3.4 Actualizar `Frontend/package-lock.json` (`npm install`) y verificar que `npm run lint` pasa en limpio

## 4. Workflow de GitHub Actions

- [x] 4.1 Crear el directorio `.github/workflows/` y el archivo `ci.yml`
- [x] 4.2 Configurar los triggers: `on: push` a `main` y `on: pull_request`
- [x] 4.3 Definir el job `backend-tests` (ubuntu-latest, Python 3.12): `actions/checkout@v4`, `actions/setup-python@v5` con `cache: pip`, instalar `Gestion_Incidentes/requirements.txt`, `pip install ruff==<pin>`, `ruff check .` y `pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing` (todo desde `Gestion_Incidentes/`)
- [x] 4.4 Definir el job `frontend-tests` (ubuntu-latest, Node 20): `actions/checkout@v4`, `actions/setup-node@v4` con `cache: npm` (lockfile en `Frontend/package-lock.json`), `npm ci`, `npm run lint` y `npm run test:coverage` (desde `Frontend/`)
- [x] 4.5 Confirmar que el YAML no declara ni referencia ningún `secrets.*` ni variables de entorno con credenciales
- [x] 4.6 Confirmar que todas las acciones de terceros están pinneadas a versión mayor explícita (`@v4`/`@v5`)

## 5. Badge en el README

- [x] 5.1 Agregar el badge de estado del workflow de GitHub Actions cerca del título de `README.md` (URL nativa `.../actions/workflows/ci.yml/badge.svg`, enlazando al workflow; sin tokens de terceros)

## 6. Verificación

- [x] 6.1 Validar la sintaxis del workflow (actionlint si está disponible, o validación local equivalente)
- [x] 6.2 Ejecutar localmente los comandos exactos del job de backend (ruff + pytest con cobertura desde `Gestion_Incidentes/`) y confirmar que pasan offline sin secretos
- [x] 6.3 Ejecutar localmente los comandos exactos del job de frontend (`npm ci` + `npm run lint` + `npm run test:coverage` desde `Frontend/`) y confirmar que pasan
- [ ] 6.4 Abrir el PR y confirmar que ambos jobs (`backend-tests`, `frontend-tests`) pasan en GitHub Actions (verificación final del pipeline)
- [ ] 6.5 (Opcional) Una vez que el CI corre, medir la cobertura real del backend en Python 3.12 para decidir si conviene fijar un `--cov-fail-under` con holgura; documentar el número
- [x] 6.6 Marcar C-09 como completado en `CHANGES.md`
