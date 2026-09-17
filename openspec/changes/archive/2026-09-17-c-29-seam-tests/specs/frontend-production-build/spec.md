## ADDED Requirements

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
