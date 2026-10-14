## ADDED Requirements

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