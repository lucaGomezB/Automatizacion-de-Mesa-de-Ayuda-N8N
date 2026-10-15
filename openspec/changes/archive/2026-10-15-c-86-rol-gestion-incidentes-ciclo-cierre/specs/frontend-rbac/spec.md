## MODIFIED Requirements

### Requirement: FR-RBAC-001 — La UI conoce el rol y el alcance autenticados

El frontend SHALL obtener el rol y el modo de alcance del usuario autenticado desde el backend y exponerlos a la UI a traves del estado de autenticacion global. El alcance SHALL representarse con los modos `PROPIO`, `GLOBAL`, `SECTOR` y `VACIO`. El frontend NO SHALL inferir el rol ni el alcance a partir de la ruta, del nombre de usuario, ni de banderas de identidad como `is_privileged`.

#### Scenario: Sesion autenticada expone rol y alcance

- **WHEN** un usuario completa el login (o el segundo factor)
- **THEN** la UI dispone del rol y del modo de alcance devueltos por el backend, incluido el modo `SECTOR`

#### Scenario: Cuenta sin empleado vinculado obtiene alcance vacio

- **WHEN** un usuario autenticado no tiene empleado activo vinculado en el directorio
- **THEN** la UI trata su alcance como `VACIO` y no habilita superficies operativas

#### Scenario: Gestion sin sector obtiene alcance vacio

- **WHEN** un usuario `gestion_incidentes` no tiene sector asignado
- **THEN** la UI trata su alcance como `VACIO` y no habilita la superficie operativa

#### Scenario: El alcance se recomputa, no se cachea indefinidamente

- **WHEN** el directorio cambia el rol o el sector del usuario
- **THEN** la UI refleja el nuevo alcance en la siguiente resolucion de identidad, sin requerir un cambio de codigo ni una bandera embebida en el token

#### Scenario: La UI no infiere el rol de la identidad ni de la ruta

- **WHEN** la UI evalua el acceso de un usuario
- **THEN** usa el rol y el alcance devueltos por el backend y no el pathname, el nombre de usuario ni `is_privileged`

### Requirement: FR-RBAC-002 — Guard de rutas por alcance

El guard de las rutas SHALL evaluar el modo de alcance del usuario, no solo su autenticacion. La superficie operativa SHALL admitir el modo `GLOBAL` (todos los incidentes) y el modo `SECTOR` (los incidentes activos de su sector); la cola de revision SHALL seguir exigiendo `GLOBAL`. La vista "Mis incidentes" SHALL exigir el modo `PROPIO`. Una cuenta con alcance `VACIO` SHALL NOT acceder a ninguna de esas vistas y SHALL ser redirigida al portal. El acceso anonimo SHALL seguir redirigiendo a `/login`, sin cambios respecto del comportamiento previo.

#### Scenario: Rol GLOBAL accede a la superficie operativa

- **WHEN** un usuario con alcance `GLOBAL` navega a la superficie operativa
- **THEN** la UI lo admite y habilita el listado de todos los incidentes y la cola de revision

#### Scenario: Rol SECTOR accede a la superficie operativa acotada

- **WHEN** un usuario con alcance `SECTOR` navega a la superficie operativa
- **THEN** la UI lo admite y el listado muestra unicamente los incidentes activos de su sector; la cola de revision queda fuera de su alcance

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

La navegacion principal SHALL renderizar los enlaces disponibles segun el modo de alcance del usuario, NO segun el pathname. El enlace a la superficie operativa SHALL mostrarse a usuarios con alcance `GLOBAL` y con alcance `SECTOR`; el enlace a "Mis incidentes" SHALL mostrarse unicamente a usuarios con alcance `PROPIO`; el enlace al portal SHALL permanecer visible para todo usuario autenticado.

#### Scenario: Rol GLOBAL ve el enlace operativo

- **WHEN** un usuario con alcance `GLOBAL` observa la navegacion
- **THEN** la UI muestra el enlace a la superficie operativa

#### Scenario: Rol SECTOR ve el enlace operativo

- **WHEN** un usuario con alcance `SECTOR` observa la navegacion
- **THEN** la UI muestra el enlace a la superficie operativa acotada a su sector

#### Scenario: Rol PROPIO ve el enlace a "Mis incidentes"

- **WHEN** un usuario con alcance `PROPIO` observa la navegacion
- **THEN** la UI muestra el enlace a "Mis incidentes" y no el enlace a la superficie operativa

#### Scenario: Alcance vacio no ve enlaces operativos

- **WHEN** un usuario con alcance `VACIO` observa la navegacion
- **THEN** la UI muestra el portal y no muestra el enlace a la superficie operativa ni el de "Mis incidentes"
