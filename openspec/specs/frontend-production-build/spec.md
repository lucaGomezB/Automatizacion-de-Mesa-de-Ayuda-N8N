# frontend-production-build — Spec

## Purpose

Define los requisitos para builds de producción del frontend: multi-stage Docker, npm ci, y configuración nginx para SPA routing.

## Requirements

### Requirement: Frontend Dockerfile SHALL use multi-stage build
The frontend Dockerfile SHALL implement a multi-stage build process with separate build and production stages.

#### Scenario: Build stage compiles TypeScript and bundles assets
- **WHEN** the Docker build runs
- **THEN** the build stage SHALL install dependencies with npm ci
- **AND** compile TypeScript with npm run build
- **AND** generate optimized static assets in dist/ directory

#### Scenario: Production stage serves with nginx
- **WHEN** the production image is created
- **THEN** it SHALL copy only the dist/ output from the build stage
- **AND** serve static files using nginx:alpine base image
- **AND** expose port 3000 for external access

### Requirement: Frontend SHALL use npm ci for deterministic builds
The frontend Dockerfile SHALL use npm ci instead of npm install for dependency installation.

#### Scenario: npm ci installs exact dependencies
- **WHEN** the build stage runs dependency installation
- **THEN** npm ci SHALL be used to install dependencies from package-lock.json
- **AND** the installation SHALL be deterministic and reproducible

### Requirement: Nginx SHALL be configured for SPA routing
The nginx configuration SHALL support client-side routing for single-page applications.

#### Scenario: Nginx serves index.html for all routes
- **WHEN** a user navigates to any frontend route
- **THEN** nginx SHALL serve index.html to enable client-side routing
- **AND** static assets SHALL be served with appropriate caching headers

### Requirement: Frontend SHALL be accessible on port 3000
The frontend application SHALL be accessible on port 3000 in both development and production environments.

#### Scenario: Production frontend serves on port 3000
- **WHEN** the frontend container starts in production mode
- **THEN** the application SHALL be accessible on port 3000
- **AND** serve optimized static assets via nginx

#### Scenario: Development frontend serves on port 3000
- **WHEN** the frontend container starts in development mode
- **THEN** the application SHALL be accessible on port 3000
- **AND** support hot module replacement with vite dev server

### Requirement: VITE_API_BASE_URL como configuración de build de fuente única

La URL base de la API del frontend SHALL resolverse como configuración de build de Vite de fuente única: `docker-compose.yml` SHALL reenviar `VITE_API_BASE_URL` al frontend como build arg (no solo como entorno de runtime del contenedor precompilado), el `Dockerfile` del frontend SHALL declarar el `ARG` correspondiente antes de ejecutar el build, y el valor configurado NO SHALL incluir el sufijo `/api/v1` ya que el cliente HTTP del frontend lo agrega. La suite de pruebas de configuración SHALL verificar las tres condiciones leyendo los archivos de configuración, sin construir la imagen.

#### Scenario: docker-compose reenvía la variable como build arg

- **WHEN** se inspecciona la definición del servicio `frontend` en `docker-compose.yml`
- **THEN** `VITE_API_BASE_URL` aparece bajo `build.args` del servicio
- **AND** no depende exclusivamente de `environment` del contenedor de runtime

#### Scenario: El Dockerfile declara el ARG antes del build

- **WHEN** se inspecciona `App/Frontend/Dockerfile`
- **THEN** declara `ARG VITE_API_BASE_URL` en el stage de build
- **AND** la declaración precede a la ejecución de `npm run build`

#### Scenario: El valor no duplica el sufijo /api/v1

- **WHEN** se inspecciona el valor configurado de `VITE_API_BASE_URL`
- **THEN** el valor no termina en `/api/v1`
- **AND** la URL efectiva del cliente no contiene `/api/v1/api/v1`

### Requirement: Build de Docker propaga VITE_API_BASE_URL

La build de Docker del frontend SHALL propagar la variable `VITE_API_BASE_URL` en tiempo de compilacion, de modo que el bundle resultante use el valor provisto por el entorno de despliegue y MUST NOT quede fijado a una URL hardcodeada. El proceso de build SHALL fallar o advertir explicitamente si la variable falta cuando es requerida.

#### Scenario: La build usa el valor provisto

- **WHEN** se construye la imagen del frontend con `VITE_API_BASE_URL` definido
- **THEN** el bundle incluye ese valor y las llamadas del cliente lo usan

#### Scenario: Sin la variable no queda una URL hardcodeada silenciosa

- **WHEN** se construye la imagen sin `VITE_API_BASE_URL`
- **THEN** el build no produce un bundle que apunte a una URL hardcodeada distinta de la documentada

### Requirement: Volumenes de hot-reload coherentes con lo ejecutado

En el entorno de desarrollo en Docker, los volumenes montados para hot-reload SHALL corresponder al codigo que el proceso efectivamente ejecuta. Un volumen que monte una ruta que el proceso no usa MUST considerarse un defecto de configuracion.

#### Scenario: El codigo editado es el que corre

- **WHEN** se edita un archivo de codigo fuente del frontend o backend en el entorno de desarrollo
- **THEN** el proceso en el contenedor refleja el cambio, porque el volumen montado coincide con la ruta ejecutada

#### Scenario: Un volumen inutil es detectado como defecto

- **WHEN** se inspecciona la configuracion del entorno de desarrollo
- **THEN** no existe un volumen que monte una ruta distinta a la que el proceso ejecuta
