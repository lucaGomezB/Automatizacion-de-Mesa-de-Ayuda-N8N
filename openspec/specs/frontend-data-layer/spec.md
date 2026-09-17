# frontend-data-layer Specification

## Purpose
Consolida el comportamiento de la capa de datos del frontend: una unica fuente de verdad para la base URL del API, llamadas sin redirecciones que pierdan credenciales, e invalidacion, conteos, fechas y estados de carga correctos en las vistas de administracion y dashboard.

## Requirements

### Requirement: FD-001 — Base URL unica del API

El frontend SHALL resolver la base URL del API desde una unica fuente de verdad (`VITE_API_BASE_URL`). MUST NOT existir una URL por defecto duplicada y hardcodeada que compita con la variable de entorno. La variable SHALL ser efectiva tambien en la build de produccion dentro de Docker.

#### Scenario: La variable de entorno define la base URL

- **WHEN** el frontend se compila con `VITE_API_BASE_URL` definido
- **THEN** todas las llamadas del cliente usan ese valor y no una URL hardcodeada distinta

#### Scenario: Sin variable de entorno se usa un unico fallback

- **WHEN** el frontend se ejecuta sin `VITE_API_BASE_URL`
- **THEN** el cliente usa un fallback unico y documentado, sin duplicar la constante en varios modulos

### Requirement: FD-002 — Llamadas sin redireccion que pierda credenciales

El cliente HTTP SHALL construir las rutas de modo que no disparen un redirect 307 del proxy inverso. Un 307 sobre un request autenticado SHALL considerarse un defecto, porque puede perder el header `Authorization` y el cuerpo del request.

#### Scenario: Las llamadas autenticadas no disparan 307

- **WHEN** el cliente realiza una llamada autenticada a traves del proxy inverso
- **THEN** la respuesta no es un 307 y el request conserva `Authorization` y cuerpo

#### Scenario: La barra final es consistente con la ruta del backend

- **WHEN** se inspecciona la construccion de rutas del cliente y de los servicios
- **THEN** la union de base URL y ruta produce exactamente la ruta del backend, sin barra faltante ni duplicada

### Requirement: FD-003 — Invalidacion del detalle del ticket tras mutar

Tras una mutacion exitosa de un incidente (edicion o cambio de estado), el frontend SHALL invalidar la query del detalle de ese incidente ademas de la lista, de modo que el detalle muestre los datos actualizados.

#### Scenario: Editar un ticket refresca su detalle

- **WHEN** el usuario edita un incidente desde el detalle y la mutacion resuelve con exito
- **THEN** la query del detalle de ese incidente se invalida y el detalle se refetcha con los datos nuevos

#### Scenario: Cambiar de estado refresca la lista y el detalle

- **WHEN** cambia el estado de un incidente
- **THEN** se invalidan tanto la lista como la query del detalle del incidente afectado

### Requirement: FD-004 — Contador de revision humana sobre el total

El contador de la cola de revision humana SHALL reflejar el total de items pendientes reportado por el backend, no la cantidad de items de la pagina visible.

#### Scenario: El contador no se limita a la pagina

- **WHEN** el backend reporta mas items pendientes que los de la pagina actual
- **THEN** el contador muestra el total del backend, mayor que el tamano de la pagina

### Requirement: FD-005 — Fechas del dashboard sin desfase UTC

El frontend SHALL calcular y mostrar las fechas del dashboard en la zona horaria local del usuario, sin desplazarlas un dia por conversiones a UTC.

#### Scenario: La fecha mostrada coincide con la fecha local

- **WHEN** el usuario selecciona o visualiza una fecha en el dashboard
- **THEN** la fecha mostrada coincide con la fecha local seleccionada, sin corrimiento de un dia

### Requirement: FD-006 — Estado de carga compuesto

Las vistas que combinan varias consultas SHALL calcular su estado de carga de modo que, con al menos una consulta en curso, la vista se considere cargando; el error se muestra solo cuando todas las consultas necesarias fallaron y la vista no tiene datos utilizables.

#### Scenario: Una consulta pendiente mantiene el estado de carga

- **WHEN** una de varias consultas de la vista sigue pendiente y las demas resolvieron
- **THEN** la vista muestra estado de carga en lugar de datos parciales o de un error

#### Scenario: Error solo con todas las consultas fallidas

- **WHEN** todas las consultas necesarias fallan sin datos utilizables
- **THEN** la vista muestra el estado de error
