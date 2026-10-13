## Purpose

Hace que la interfaz de usuario conozca y refleje el rol y el alcance de incidentes del usuario autenticado (PROPIO/GLOBAL/VACIO), de modo que la navegacion, el guard de rutas, la vista de incidentes y el filtro de sector dejen de ser role-blind. Es una capa de UX y least-surprise: NO es el limite de seguridad, que sigue residiendo en el backend.

## ADDED Requirements

### Requirement: FR-RBAC-001 — La UI conoce el rol y el alcance autenticados

El frontend SHALL obtener el rol y el modo de alcance del usuario autenticado desde el backend y exponerlos a la UI a traves del estado de autenticacion global. El alcance SHALL representarse con los modos `PROPIO`, `GLOBAL` y `VACIO`. El frontend NO SHALL inferir el rol ni el alcance a partir de la ruta, del nombre de usuario, ni de banderas de identidad como `is_privileged`.

#### Scenario: Sesion autenticada expone rol y alcance

- **WHEN** un usuario completa el login (o el segundo factor)
- **THEN** la UI dispone del rol y del modo de alcance devueltos por el backend

#### Scenario: Cuenta sin empleado vinculado obtiene alcance vacio

- **WHEN** un usuario autenticado no tiene empleado activo vinculado en el directorio
- **THEN** la UI trata su alcance como `VACIO` y no habilita superficies operativas

#### Scenario: El alcance se recomputa, no se cachea indefinidamente

- **WHEN** el directorio cambia el rol del usuario
- **THEN** la UI refleja el nuevo alcance en la siguiente resolucion de identidad, sin requerir un cambio de codigo ni una bandera embebida en el token

#### Scenario: La UI no infiere el rol de la identidad ni de la ruta

- **WHEN** la UI evalua el acceso de un usuario
- **THEN** usa el rol y el alcance devueltos por el backend y no el pathname, el nombre de usuario ni `is_privileged`

### Requirement: FR-RBAC-002 — Guard de rutas por alcance

El guard de las rutas SHALL evaluar el modo de alcance del usuario, no solo su autenticacion. La superficie operativa (listado de tickets y cola de revision) SHALL exigir el modo `GLOBAL`. La vista "Mis incidentes" SHALL exigir el modo `PROPIO`. Una cuenta con alcance `VACIO` SHALL NOT acceder a ninguna de esas vistas y SHALL ser redirigida al portal. El acceso anonimo SHALL seguir redirigiendo a `/login`, sin cambios respecto del comportamiento previo.

#### Scenario: Rol GLOBAL accede a la superficie operativa

- **WHEN** un usuario con alcance `GLOBAL` navega a la superficie operativa
- **THEN** la UI lo admite y habilita el listado de todos los incidentes y la cola de revision

#### Scenario: Rol PROPIO accede a "Mis incidentes" y no a la superficie operativa

- **WHEN** un usuario con alcance `PROPIO` navega a la vista de sus incidentes
- **THEN** la UI lo admite y presenta unicamente sus propios incidentes; si intenta la superficie operativa, es redirigido

#### Scenario: Alcance vacio no accede a la superficie operativa

- **WHEN** un usuario con alcance `VACIO` intenta navegar a la superficie operativa o a "Mis incidentes"
- **THEN** la UI lo redirige al portal sin exponer listados ni acciones operativas

#### Scenario: Acceso anonimo redirige a login

- **WHEN** una cuenta no autenticada intenta navegar a una ruta protegida
- **THEN** la UI la redirige a `/login`, igual que antes

### Requirement: FR-RBAC-003 — Navegacion renderizada segun el alcance

La navegacion principal SHALL renderizar los enlaces disponibles segun el modo de alcance del usuario, NO segun el pathname. El enlace a la superficie operativa SHALL mostrarse unicamente a usuarios con alcance `GLOBAL`; el enlace a "Mis incidentes" SHALL mostrarse unicamente a usuarios con alcance `PROPIO`; el enlace al portal SHALL permanecer visible para todo usuario autenticado.

#### Scenario: Rol GLOBAL ve el enlace operativo

- **WHEN** un usuario con alcance `GLOBAL` observa la navegacion
- **THEN** la UI muestra el enlace a la superficie operativa

#### Scenario: Rol PROPIO ve el enlace a "Mis incidentes"

- **WHEN** un usuario con alcance `PROPIO` observa la navegacion
- **THEN** la UI muestra el enlace a "Mis incidentes" y no el enlace a la superficie operativa

#### Scenario: Alcance vacio no ve enlaces operativos

- **WHEN** un usuario con alcance `VACIO` observa la navegacion
- **THEN** la UI muestra el portal y no muestra el enlace a la superficie operativa ni el de "Mis incidentes"

### Requirement: FR-RBAC-004 — El filtro de sector es una conveniencia, no un control de acceso

El filtro de sector de la superficie operativa SHALL ser un filtro de conveniencia de la interfaz y SHALL NOT considerarse un mecanismo de seguridad. El frontend MUST NOT ocultar ni acotar datos por sector por su cuenta: la visibilidad la determina exclusivamente el backend. Cualquier rol autorizado a la vista de listado MAY usar el filtro de sector, y su ausencia o cambio MUST NOT alterar el conjunto de datos que el backend devuelve.

#### Scenario: El filtro no restringe el acceso

- **WHEN** un usuario con acceso a la superficie operativa limpia o cambia el filtro de sector
- **THEN** el conjunto de datos autorizado sigue siendo el que determina el backend, sin que el sector actue como frontera

#### Scenario: El sector no oculta datos por si mismo

- **WHEN** el backend devuelve incidentes de mas de un sector a un usuario GLOBAL
- **THEN** la UI puede filtrarlos visualmente, pero no elimina del alcance ningun dato que el backend haya autorizado

#### Scenario: El filtro no es la fuente de verdad

- **WHEN** se inspecciona el comportamiento del filtro de sector
- **THEN** se documenta y testea que es conveniencia de UX y que la seguridad reside en el backend

### Requirement: FR-RBAC-005 — La UI no reemplaza el enforcement del backend

Los controles del frontend SHALL ser de experiencia de usuario y SHALL NOT considerarse el limite de seguridad. Ante una respuesta del backend que niegue el acceso a un recurso fuera de alcance (por ejemplo 403 o 404), la UI SHALL manejarla sin exponer el recurso y sin asumir acceso por su cuenta.

#### Scenario: Recurso fuera de alcance denegado por el backend

- **WHEN** el backend responde que un recurso esta fuera del alcance del usuario
- **THEN** la UI no lo muestra y presenta un estado de acceso denegado o no encontrado, sin datos del recurso

#### Scenario: El frontend no concede datos por si mismo

- **WHEN** el backend no devuelve un recurso por estar fuera de alcance
- **THEN** ninguna logica del frontend lo reconstruye ni lo muestra
