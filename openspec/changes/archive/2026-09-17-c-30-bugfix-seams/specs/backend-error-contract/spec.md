## Purpose

Define el contrato uniforme de errores de la API y la validacion de integridad referencial de los catalogos, de modo que todo fallo predecible del cliente se exprese como un codigo 4xx con un envelope consistente y sin corromper datos.

## ADDED Requirements

### Requirement: ERR-001 — Envelope de error uniforme

La API SHALL responder todo error de aplicacion con el envelope `{"error": {"code": "<CODE>", "message": "<mensaje>", "details?": "<detalle>"}}`. Esto incluye los errores de validacion de request (HTTP 422) y los errores de autenticacion y autorizacion (HTTP 401/403). La respuesta de error MUST NOT exponer el campo `detail` de FastAPI/Pydantic en la raiz del cuerpo. El campo `code` SHALL ser estable y en mayusculas, y `message` SHALL ser legible por un operador.

#### Scenario: Error de validacion responde con el envelope

- **WHEN** se envia un payload invalido a un endpoint de la API
- **THEN** la respuesta tiene HTTP 422 y su cuerpo contiene `error.code`, `error.message` y, cuando corresponde, `error.details`, sin el campo `detail` en la raiz

#### Scenario: Error de autenticacion responde con el envelope

- **WHEN** se envia una peticion sin token o con token invalido a un endpoint protegido
- **THEN** la respuesta tiene HTTP 401 y su cuerpo contiene `error.code` y `error.message`, sin el campo `detail` en la raiz

#### Scenario: Error de recurso inexistente responde con el envelope

- **WHEN** se consulta o modifica un recurso inexistente
- **THEN** la respuesta tiene HTTP 404 y su cuerpo contiene `error.code` y `error.message`

### Requirement: ERR-002 — Validacion de existencia de claves foraneas de catalogo

Antes de persistir una operacion que referencie una entidad de catalogo (`estado`, `sector`, `canal_origen`), el sistema SHALL verificar que la entidad referenciada existe. Si no existe, SHALL responder un codigo 4xx con un mensaje accionable y MUST NOT persistir ni modificar el recurso.

#### Scenario: PATCH con una FK inexistente no persiste

- **WHEN** se envia un PATCH a un incidente referenciando un `estado_id` o `sector_id` que no existe en el catalogo
- **THEN** la respuesta es 4xx (nunca 500) y el incidente permanece sin cambios

#### Scenario: Creacion con una FK inexistente no persiste

- **WHEN** se crea un recurso referenciando una entidad de catalogo inexistente
- **THEN** la respuesta es 4xx con un mensaje que nombra la entidad invalida y no se inserta registro alguno

### Requirement: ERR-003 — Errores de dominio de catalogo mapeados a 4xx

Los errores de dominio por entidad de catalogo inexistente (por ejemplo `CanalOrigenNotFoundError`) SHALL mapearse mediante un handler explicito a un codigo 4xx con el envelope de ERR-001. Ningun error de dominio predecible SHALL producir HTTP 500.

#### Scenario: Canal de origen inexistente no produce 500

- **WHEN** una operacion referencia un canal de origen inexistente y la capa de servicio lanza el error de dominio correspondiente
- **THEN** la respuesta es 4xx con `error.code` y `error.message`, sin traza ni 500

### Requirement: ERR-004 — Disciplina de capas en el acceso a datos

Las rutas SHALL delegar la logica de negocio en la capa de servicios y el acceso a datos en la capa de repositorios. Ninguna ruta SHALL construir consultas ni manipular la sesion de base de datos directamente, y ningun servicio SHALL saltear la capa de repositorios para consultar el ORM directamente.

#### Scenario: Una ruta no accede directamente a la sesion

- **WHEN** se inspecciona el codigo de la capa de rutas
- **THEN** ninguna ruta instancia repositorios, construye consultas ni usa la sesion de base de datos directamente

#### Scenario: Un servicio delega en repositorios

- **WHEN** un servicio necesita leer o escribir datos
- **THEN** lo hace a traves de la capa de repositorios y no consultando el ORM de forma directa
