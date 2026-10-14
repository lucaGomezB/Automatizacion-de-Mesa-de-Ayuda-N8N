## ADDED Requirements

### Requirement: RP-006 — Permiso de asignación de prioridad crítica en el registro de política

El registro canónico de política de rol SHALL declarar un atributo booleano `puede_asignar_prioridad_critica` por rol, del que SHALL derivarse la autorización para asignar (alta) o fijar/cambiar (edición) la prioridad `critica` de un incidente, sin listas de rol duplicadas en las rutas ni en los servicios. En el registro por defecto los roles `mesa_de_ayuda` y `administrador_directorio` SHALL declarar `puede_asignar_prioridad_critica` verdadero; `usuario_final` SHALL declararlo falso. El atributo SHALL convivir con los atributos ya definidos en el registro de política (RP-001) y SHALL ser el único origen de la decisión de autorización de prioridad crítica.

El enforcement SHALL ser server-side y aplicarse por igual al alta `POST /api/v1/incidentes` y a la edición `PATCH /api/v1/incidentes/{id}`: un llamante cuyo rol NO declare el permiso SHALL recibir un error de autorización (HTTP 403) cuando el alta incluya `critica`, o cuando la edición intente fijar o cambiar la prioridad a `critica`, sin persistir ningún cambio. La asignación de las prioridades `baja`, `media` y `alta` SHALL permanecer sin restricción de rol, como ocurre hoy. La restricción MUST NOT ser evitable desde el cliente: la UI no es un límite de seguridad.

#### Scenario: Mesa de ayuda asigna prioridad crítica

- **WHEN** un usuario con rol `mesa_de_ayuda` crea o edita un incidente con prioridad `critica`
- **THEN** el sistema acepta la operación y persiste la prioridad `critica`

#### Scenario: Administrador de directorio asigna prioridad crítica

- **WHEN** un usuario con rol `administrador_directorio` crea o edita un incidente con prioridad `critica`
- **THEN** el sistema acepta la operación y persiste la prioridad `critica`

#### Scenario: Rol no autorizado es rechazado en el alta

- **WHEN** un usuario cuyo rol no declara `puede_asignar_prioridad_critica` crea un incidente con prioridad `critica`
- **THEN** el sistema responde HTTP 403 y no crea ningún incidente

#### Scenario: Rol no autorizado es rechazado en la edición

- **WHEN** un usuario cuyo rol no declara `puede_asignar_prioridad_critica` edita un incidente intentando fijar o cambiar la prioridad a `critica`
- **THEN** el sistema responde HTTP 403 y no modifica la fila

#### Scenario: Las prioridades no críticas siguen sin restricción

- **WHEN** un usuario con rol `usuario_final` crea o edita un incidente con prioridad `baja`, `media` o `alta`
- **THEN** el sistema acepta la operación y persiste la prioridad

#### Scenario: El guard deriva del registro de política

- **WHEN** se inspecciona el guard de prioridad crítica de las rutas de alta y edición
- **THEN** deriva de `puede_asignar_prioridad_critica` del registro de política y no de una lista de roles propia

#### Scenario: Llamante no interactivo sin permiso no rompe la ingesta

- **WHEN** un llamante no interactivo (por ejemplo, el webhook de N8N) sin el permiso envía una prioridad `critica`
- **THEN** el sistema responde HTTP 403 y la ingesta de incidentes con prioridad `baja`, `media` o `alta` permanece inalterada
