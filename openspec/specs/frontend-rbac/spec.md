# frontend-rbac Specification

## Purpose

Hace que la interfaz de usuario conozca y refleje el rol y el alcance de incidentes del usuario autenticado (PROPIO/GLOBAL/VACIO), de modo que la navegacion, el guard de rutas, la vista de incidentes y el filtro de sector dejen de ser role-blind. Es una capa de UX y least-surprise: NO es el limite de seguridad, que sigue residiendo en el backend.

## Requirements

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

### Requirement: FR-RBAC-006 — Acción de borrado lógico exclusiva del administrador con confirmación

La superficie de administración SHALL ofrecer una acción para borrar lógicamente un incidente, visible y ejecutable ÚNICAMENTE por un usuario con rol `administrador_directorio`. La UI SHALL derivar la visibilidad de la acción del rol autenticado ya expuesto por el estado de autenticación (FR-RBAC-001) y MUST NOT mostrarla a `mesa_de_ayuda`, `usuario_final` ni a cuentas con alcance vacío. La acción SHALL exigir un paso de confirmación explícito antes de invocar el backend. Tras una confirmación exitosa, la UI SHALL invalidar los listados afectados de modo que el incidente borrado desaparezca de inmediato. La UI MUST NOT considerar la acción como un límite de seguridad: ante una respuesta 403 o 404 del backend, SHALL manejarla sin exponer el recurso, conforme a FR-RBAC-005.

#### Scenario: El administrador ve la acción

- **WHEN** un usuario con rol `administrador_directorio` abre el detalle de un incidente
- **THEN** la UI muestra la acción de borrado lógico

#### Scenario: Los demás roles no ven la acción

- **WHEN** un usuario con rol `mesa_de_ayuda` o `usuario_final` abre el detalle de un incidente
- **THEN** la UI no muestra la acción de borrado lógico

#### Scenario: La acción exige confirmación

- **WHEN** el administrador activa la acción de borrado lógico
- **THEN** la UI presenta un paso de confirmación y no invoca el backend hasta que el administrador confirme

#### Scenario: La cancelación no borra nada

- **WHEN** el administrador cancela la confirmación
- **THEN** la UI no invoca el backend y el incidente permanece visible

#### Scenario: Tras borrar, el incidente desaparece de la vista

- **WHEN** el backend confirma el borrado lógico
- **THEN** la UI invalida los listados afectados y el incidente ya no aparece

#### Scenario: La denegación del backend se maneja sin exponer el recurso

- **WHEN** el backend responde 403 o 404 a la acción de borrado lógico
- **THEN** la UI muestra un estado de acceso denegado o no encontrado y no expone los datos del incidente

### Requirement: FR-RBAC-007 — Navegacion por rol del directorio

La navegacion principal SHALL poder renderizar enlaces en funcion del ROL del usuario, ademas del modo de alcance. El enlace a `/directorio` SHALL mostrarse UNICAMENTE a usuarios con rol `administrador_directorio`. Como el modo `GLOBAL` tambien incluye a `mesa_de_ayuda`, el enlace NO SHALL mostrarse a un usuario `GLOBAL` cuyo rol no sea `administrador_directorio`. El enlace al portal y los enlaces por alcance existentes NO SHALL verse alterados.

#### Scenario: El administrador ve el enlace del directorio

- **WHEN** un usuario con rol `administrador_directorio` observa la navegacion
- **THEN** la UI muestra el enlace a `/directorio`

#### Scenario: Un rol GLOBAL distinto no ve el enlace

- **WHEN** un usuario con rol `mesa_de_ayuda` (alcance `GLOBAL`) observa la navegacion
- **THEN** la UI no muestra el enlace a `/directorio`

#### Scenario: Los enlaces existentes no cambian

- **WHEN** cualquier usuario autenticado observa la navegacion
- **THEN** los enlaces al portal, a la superficie operativa y a "Mis incidentes" se muestran segun las reglas de alcance ya vigentes

### Requirement: FR-RBAC-008 — Guard de ruta por rol

El guard de las rutas SHALL poder exigir un rol especifico, ademas del modo de alcance y de la autenticacion. Cuando una ruta exige un rol, el guard SHALL admitir unicamente a usuarios autenticados cuyo rol coincida con el exigido, y SHALL redirigir a cualquier otro usuario de forma segura (un anonimo a `/login`; un autenticado sin el rol al portal). El guard de las rutas existentes (`GLOBAL`/`PROPIO`) NO SHALL verse alterado. Esta decision SHALL ser una funcion pura y verificable, sin efectos secundarios.

#### Scenario: El guard admite el rol exigido

- **WHEN** un usuario autenticado con el rol exigido evalua una ruta con requisito de rol
- **THEN** el guard lo admite

#### Scenario: El guard rechaza un rol distinto

- **WHEN** un usuario autenticado sin el rol exigido evalua una ruta con requisito de rol
- **THEN** el guard lo redirige al portal sin exponer la ruta

#### Scenario: El anonimo sigue yendo a login

- **WHEN** un usuario no autenticado evalua una ruta con requisito de rol
- **THEN** el guard lo redirige a `/login`

#### Scenario: Las rutas por alcance no cambian

- **WHEN** se evaluan las rutas existentes que exigen `GLOBAL` o `PROPIO`
- **THEN** su comportamiento de admision y redireccion permanece igual que antes

### Requirement: FR-RBAC-009 — Asignación de prioridad crítica restringida al rol autorizado

La superficie de administración SHALL ofrecer un control editable para asignar la prioridad de un incidente, incluida la opción `critica`, visible y ejecutable por los roles que tengan el permiso de asignación de prioridad crítica conforme a RP-006 (`mesa_de_ayuda` y `administrador_directorio`), y oculto o deshabilitado para los roles sin el permiso (por ejemplo, `usuario_final`). La UI SHALL derivar la disponibilidad de la opción `critica` del rol autenticado ya expuesto por el estado de autenticación (FR-RBAC-001) y MUST NOT ofrecer `critica` a los demás roles. El formulario de reporte del usuario final SHALL seguir sin ofrecer la opción `critica`. Los indicadores visuales de prioridad SHALL representar `critica` de forma distinguible de `baja`, `media` y `alta`. La UI MUST NOT considerar el control como un límite de seguridad: ante una respuesta 403 del backend SHALL manejarla sin exponer el recurso, conforme a FR-RBAC-005.

#### Scenario: El rol autorizado asigna prioridad crítica

- **WHEN** un usuario con rol `mesa_de_ayuda` abre el control de prioridad de un incidente en el panel de administración
- **THEN** la UI ofrece la opción `critica` y permite asignarla

#### Scenario: El administrador de directorio asigna prioridad crítica

- **WHEN** un usuario con rol `administrador_directorio` abre el control de prioridad de un incidente en el panel de administración
- **THEN** la UI ofrece la opción `critica` y permite asignarla

#### Scenario: Los roles sin permiso no ofrecen la opción crítica

- **WHEN** un usuario con rol `usuario_final` abre el panel de administración
- **THEN** la UI no ofrece la opción `critica` en el control de prioridad

#### Scenario: El formulario de reporte no ofrece prioridad crítica

- **WHEN** un usuario final abre el formulario de reporte de incidentes
- **THEN** la UI no ofrece la opción `critica` entre las prioridades seleccionables

#### Scenario: El indicador de prioridad crítica es distinguible

- **WHEN** la UI renderiza un incidente con prioridad `critica`
- **THEN** el indicador visual de prioridad la distingue de `baja`, `media` y `alta`

#### Scenario: La denegación del backend se maneja sin exponer el recurso

- **WHEN** el backend responde 403 a una asignación de prioridad crítica
- **THEN** la UI muestra un estado de acceso denegado y no expone los datos del incidente
