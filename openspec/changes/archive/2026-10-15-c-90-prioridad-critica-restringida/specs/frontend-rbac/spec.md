## ADDED Requirements

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
