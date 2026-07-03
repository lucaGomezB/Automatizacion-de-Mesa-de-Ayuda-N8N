## MODIFIED Requirements

### Requirement: Infraestructura de pruebas del frontend

El proyecto SHALL proveer una infraestructura de pruebas automatizadas para el frontend React ejecutable por comando. La configuracion SHALL usar Vitest como runner, un entorno DOM (`happy-dom`) que permita renderizar componentes React, el alias `@/` resuelto al directorio `src/` (espejando `vite.config.ts`), y un archivo de setup que registre los matchers de `@testing-library/jest-dom` para todas las pruebas. El proyecto MUST exponer un script `test` en `App/Frontend/package.json` que ejecute la suite, y un medio para generar el reporte de cobertura. Las dependencias de prueba MUST agregarse solo como `devDependencies`, sin alterar las dependencias de runtime.

#### Scenario: La suite se ejecuta por comando

- **WHEN** se ejecuta el script `test` definido en `App/Frontend/package.json`
- **THEN** Vitest descubre y ejecuta los archivos de prueba del frontend en el entorno DOM configurado, sin requerir un servidor backend en ejecucion

#### Scenario: El alias de importacion resuelve como en produccion

- **WHEN** una prueba importa un modulo del frontend mediante el prefijo `@/` (por ejemplo `@/services/api`)
- **THEN** la importacion resuelve al archivo correspondiente bajo `src/`, igual que en la build de Vite

#### Scenario: Los matchers de jest-dom estan disponibles

- **WHEN** una prueba de componente usa un matcher de DOM (por ejemplo `toBeInTheDocument` o `toBeDisabled`)
- **THEN** el matcher esta registrado y disponible sin importarlo en cada archivo de prueba
