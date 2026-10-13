## REMOVED Requirements

### Requirement: NR-002 — Resolucion por rol y sector

**Reason**: El criterio de destinatarios de la notificacion de revision cambia: deja de acotarse por el sector del incidente y de seleccionar el rol `operador` (eliminado). Ahora se seleccionan todos los `mesa_de_ayuda` activos.

**Migration**: Reemplazada por "NR-002 — Resolucion por rol" en este mismo delta.

## ADDED Requirements

### Requirement: NR-002 — Resolucion por rol

Para la notificacion de revision humana, el sistema SHALL seleccionar como destinatarios a TODOS los empleados ACTIVOS con rol `mesa_de_ayuda`, con independencia del sector. El rol `mesa_de_ayuda` SHALL ser el unico rol elegible como destinatario de la notificacion de revision. El sistema MUST NOT seleccionar empleados con rol `usuario_final` ni `administrador_directorio`, ni empleados inactivos, ni acotar la seleccion por el sector del incidente o del empleado. Si no existe ningun `mesa_de_ayuda` activo, el resultado SHALL ser una lista vacia, sin error, y N8N aplicara el destinatario de respaldo.

#### Scenario: Mesa de ayuda activo es destinatario

- **WHEN** un incidente requiere revision y existe al menos un `mesa_de_ayuda` activo
- **THEN** cada `mesa_de_ayuda` activo es un destinatario de la notificacion

#### Scenario: Varios mesa de ayuda activos

- **WHEN** un incidente requiere revision y hay N `mesa_de_ayuda` activos
- **THEN** la resolucion devuelve los N destinatarios, sin duplicados

#### Scenario: El sector no acota los destinatarios

- **WHEN** hay `mesa_de_ayuda` activos de distintos sectores o sin sector
- **THEN** la resolucion devuelve a todos, sin filtrar por sector

#### Scenario: Empleados de otros roles excluidos

- **WHEN** el directorio contiene `usuario_final` y `administrador_directorio` activos
- **THEN** ninguno de los dos es destinatario de la notificacion de revision

#### Scenario: Mesa de ayuda inactivo excluido

- **WHEN** el unico `mesa_de_ayuda` esta inactivo
- **THEN** no es destinatario y la lista resuelta queda vacia

#### Scenario: Sin destinatarios no es fatal

- **WHEN** no existe ningun `mesa_de_ayuda` activo
- **THEN** la resolucion devuelve una lista vacia sin lanzar excepcion ni bloquear el alta
