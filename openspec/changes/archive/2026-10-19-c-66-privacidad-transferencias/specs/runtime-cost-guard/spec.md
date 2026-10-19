## REMOVED Requirements

### Requirement: Captura y registro del número de origen crudo con exclusión del corpus

**Reason**: El gap assessment (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`, brechas 5.34 y 8.12) identifico que el registro CRUDO del numero de origen en los eventos estructurados de la guarda constituye una fuga de PII en logs (`cost_guard/guard.py:236,252`). El plan de cumplimiento (`docs/cumplimiento/plan-cambios-cumplimiento.md`, fila C-66) exige quitar o seudonimizar el numero llamante en los logs.

**Migration**: El numero de origen se sigue capturando y usando como clave del contador de tasa por origen en el almacen de contadores; deja de emitirse CRUDO en los logs y notificaciones. Ver el requisito AGREGADO "Seudonimizacion del numero de origen en logs con exclusion del corpus". No hay migracion de datos: los contadores por origen son efimeros y se purgan al vencer su ventana.

## ADDED Requirements

### Requirement: Seudonimizacion del numero de origen en logs con exclusion del corpus

El sistema SHALL capturar el numero de origen provisto por el proveedor de telefonia y SHALL usarlo como clave del contador de tasa por origen en el almacen de contadores. El sistema MUST NOT emitir el numero de origen CRUDO en los eventos estructurados de la guarda ni en la notificacion externa; en su lugar SHALL emitir un identificador DERIVADO y no reversible, apto para correlacionar llamadas del mismo origen dentro de la ventana de conteo. El identificador derivado SHALL derivarse con HMAC-SHA-256 usando una clave de configuracion DEDICADA al proposito, independiente de la clave de pseudonimizacion (Fernet): la derivacion MUST NOT reutilizar la clave de pseudonimizacion ni derivar material de ella, y MUST NOT acoplar la rotacion de la pseudonimizacion. El identificador derivado SHALL ser determinista bajo la misma clave dentro de la ventana y MUST NOT permitir recuperar el numero CRUDO con la informacion disponible para quien lee los logs. El numero CRUDO MUST NOT incorporarse a las tablas de negocio del incidente ni al corpus de evaluacion de la tesis. La retencion del numero CRUDO en el almacen SHALL quedar acotada a la ventana del contador de origen. La limitacion de tasa por origen SHALL preservarse sin cambios: el disparo por origen sigue decidiendose sobre el numero CRUDO como clave del contador.

#### Scenario: El numero crudo no aparece en el evento de disparo

- **WHEN** la guarda evalua una llamada de telefonia con un numero de origen disponible y se dispara
- **THEN** el evento estructurado emitido contiene un identificador derivado no reversible y NO contiene el numero de origen crudo

#### Scenario: El numero crudo no aparece en el evento de almacen no disponible

- **WHEN** el almacen de contadores no responde durante una evaluacion con un numero de origen disponible
- **THEN** el evento estructurado de indisponibilidad contiene un identificador derivado no reversible y NO contiene el numero de origen crudo

#### Scenario: La limitacion de tasa por origen se preserva

- **WHEN** un numero de origen alcanza o supera el limite configurado en la ventana vigente
- **THEN** la guarda se dispara e impide llamadas pagas adicionales de ese origen, sin impedir por si sola las de otros origenes por debajo de su limite

#### Scenario: El identificador derivado correlaciona el mismo origen en la ventana

- **WHEN** se evaluan dos llamadas del mismo numero de origen dentro de la misma ventana
- **THEN** ambos eventos muestran el mismo identificador derivado, permitiendo correlacionar las llamadas sin exponer el numero crudo

#### Scenario: El identificador derivado no es el numero crudo

- **WHEN** un actor con acceso a los logs aplica al identificador derivado la operacion inversa conocida
- **THEN** no obtiene el numero de origen crudo (la derivacion no es reversible con la informacion del log)

#### Scenario: La derivacion usa una clave dedicada, no la de pseudonimizacion

- **WHEN** se inspecciona como se deriva el identificador de origen
- **THEN** la derivacion usa HMAC-SHA-256 con la clave de configuracion dedicada al proposito y NO reutiliza ni deriva material de la clave de pseudonimizacion (Fernet)

#### Scenario: Rotar la clave dedicada cambia el identificador derivado

- **WHEN** se reemplaza la clave dedicada por otra y se deriva el identificador del mismo numero de origen
- **THEN** el identificador derivado cambia y sigue sin ser reversible al numero crudo

#### Scenario: La retencion del numero crudo queda acotada a la ventana

- **WHEN** transcurre la ventana del contador de origen y comienza una ventana nueva
- **THEN** el numero crudo como clave del contador de origen se purga y deja de conservarse

#### Scenario: El numero de origen no entra al corpus de evaluacion

- **WHEN** se genera o actualiza el corpus de evaluacion de la tesis
- **THEN** el corpus NO incluye el numero de origen
