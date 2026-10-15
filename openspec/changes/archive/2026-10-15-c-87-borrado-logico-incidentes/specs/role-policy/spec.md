## ADDED Requirements

### Requirement: RP-005 — Permiso de borrado logico de incidentes en el registro de politica

El registro canonico de politica de rol SHALL declarar un atributo `can_delete_incident` por rol, del que SHALL derivarse el guard del endpoint de borrado logico de incidentes (SD-002) sin listas de rol duplicadas en la ruta ni en el servicio. Unicamente el rol `administrador_directorio` SHALL declarar `can_delete_incident` verdadero; `usuario_final` y `mesa_de_ayuda` SHALL declararlo falso. El atributo SHALL convivir con los atributos ya definidos en el registro de politica (ver RP-001) y SHALL ser el unico origen de la decision de autorizacion de borrado logico.

#### Scenario: El administrador puede borrar incidentes

- **WHEN** se consulta `can_delete_incident` del rol `administrador_directorio`
- **THEN** es verdadero

#### Scenario: Los demas roles no pueden borrar incidentes

- **WHEN** se consulta `can_delete_incident` de los roles `usuario_final` y `mesa_de_ayuda`
- **THEN** ambos son falsos

#### Scenario: El guard deriva del registro de politica

- **WHEN** se inspecciona el guard del endpoint de borrado logico de incidentes
- **THEN** deriva de `can_delete_incident` del registro de politica y no de una lista de roles propia
