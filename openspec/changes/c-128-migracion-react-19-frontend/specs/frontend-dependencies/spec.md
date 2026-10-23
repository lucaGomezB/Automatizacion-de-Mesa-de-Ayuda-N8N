# frontend-dependencies — Delta Spec

## Purpose

Define el contrato no funcional del conjunto de dependencias del frontend: que el manifiesto y el lockfile resuelvan de forma reproducible, que el toolchain de lint/build/test sea internamente compatible sin flags de escape, y que las compuertas de calidad y el comportamiento observable se preserven tras la actualización de React y react-router.

## ADDED Requirements

### Requirement: Instalación reproducible del conjunto de dependencias

El frontend SHALL instalar sus dependencias de forma reproducible desde `App/Frontend/package.json` y `App/Frontend/package-lock.json` con `npm ci`. La instalación MUST completar sin conflictos de peer sin resolver entre las dependencias declaradas.

#### Scenario: La instalación limpia completa

- **WHEN** se ejecuta `npm ci` en `App/Frontend` sobre un árbol de dependencias limpio
- **THEN** el comando finaliza con código 0

#### Scenario: Sin conflictos de peer sin resolver

- **WHEN** una dependencia declara un rango de `peerDependencies` sobre otra declarada en el manifiesto
- **THEN** la versión declarada por el manifiesto satisface ese peer y `npm ci` no aborta con `ERESOLVE`

### Requirement: Compatibilidad interna del toolchain sin flags de escape

El árbol de dependencias SHALL resolverse sin recurrir a `--force`, `--legacy-peer-deps` ni overrides que enmascaren un conflicto. Todas las herramientas de desarrollo (linter, bundler y runner de pruebas) MUST ser mutuamente compatibles dentro de un mismo árbol, sin exigir la actualización de sus versiones mayores.

#### Scenario: La instalación no usa flags de escape

- **WHEN** se inspeccionan los pasos de instalación del frontend (workflow de CI y `Dockerfile`)
- **THEN** ninguno pasa `--force` ni `--legacy-peer-deps` al instalar

#### Scenario: Linter, bundler y runner conviven en el mismo árbol

- **WHEN** se instala el árbol completo de dependencias del frontend
- **THEN** el linter, el bundler y el runner de pruebas quedan instalados sin conflicto de peers entre sí

#### Scenario: La actualización de React no fuerza mayores del toolchain

- **WHEN** se actualizan `react` y `react-dom` a 19.x y `react-router-dom` a 7.x
- **THEN** `vite`, `vitest`, `eslint` y `tailwindcss` permanecen en sus versiones mayores actuales y el árbol resuelve sin conflicto

### Requirement: Paridad de las compuertas de lint, build y test

Las compuertas de calidad del frontend SHALL seguir operativas tras la actualización de dependencias. Los scripts `lint`, `build` y `test` de `App/Frontend/package.json` MUST ejecutarse exitosamente sobre el conjunto actualizado, conservando las mismas reglas efectivas de lint y la misma suite de pruebas.

#### Scenario: El lint pasa con las mismas reglas efectivas

- **WHEN** se ejecuta `npm run lint`
- **THEN** finaliza con código 0 con el mismo conjunto de reglas activas que antes de la migración

#### Scenario: El build de producción pasa

- **WHEN** se ejecuta `npm run build` (chequeo de tipos más bundle)
- **THEN** finaliza con código 0 y produce el artefacto en `dist/`

#### Scenario: La suite de pruebas pasa

- **WHEN** se ejecuta `npm run test`
- **THEN** la suite finaliza con código 0 con la misma cobertura funcional

### Requirement: Comportamiento observable preservado

La migración SHALL preservar el comportamiento observable del frontend (enrutado, autenticación, formularios, tableros y directorio). La suite de pruebas existente MUST pasar sin eliminar ni deshabilitar cobertura con el único fin de forzar el verde.

#### Scenario: La suite existente permanece verde

- **WHEN** se ejecuta la suite de pruebas del frontend tras la migración
- **THEN** todas las pruebas existentes pasan

#### Scenario: No se retira cobertura para pasar

- **WHEN** se revisa el diff de pruebas del change
- **THEN** no se elimina ni se marca como omitida una prueba existente para lograr el verde

### Requirement: Versión de Node soportada y consistente

La versión de Node usada para construir y probar el frontend SHALL ser una versión con soporte vigente (no fin de vida) y MUST ser consistente entre el `Dockerfile` y el workflow de CI. El bump a Node 24 responde al fin de vida de Node 20 (2026-04-30) y es independiente de los requisitos de React 19 y react-router 7.

#### Scenario: Docker y CI declaran la misma versión

- **WHEN** se inspeccionan `App/Frontend/Dockerfile` y `.github/workflows/ci.yml`
- **THEN** ambos usan una versión de Node con soporte vigente y coincidente entre sí

#### Scenario: El build corre sobre la versión declarada

- **WHEN** el build del frontend se ejecuta en la versión de Node declarada
- **THEN** el toolchain arranca sin errores de versión mínima