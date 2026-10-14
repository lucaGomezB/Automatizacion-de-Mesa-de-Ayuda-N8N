## ADDED Requirements

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
