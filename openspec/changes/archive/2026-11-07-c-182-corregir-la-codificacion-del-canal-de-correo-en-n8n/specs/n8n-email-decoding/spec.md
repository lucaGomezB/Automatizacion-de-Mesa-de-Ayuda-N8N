## Purpose

Garantiza que el canal de correo electronico del flujo N8N decodifique el cuerpo de los mensajes con el
charset declarado de cada parte, evitando la doble codificacion (mojibake) de los cuerpos enviados como
`quoted-printable`, sobre una imagen N8N derivada, pinneada, verificable y reversible.

## ADDED Requirements

### Requirement: Decodificacion con el charset declarado de las partes quoted-printable

La imagen N8N usada por el canal de correo SHALL decodificar cada parte `quoted-printable` con el charset
declarado por la parte, de modo que un cuerpo UTF-8 con caracteres acentuados se persista sin mojibake.
El comportamiento de las partes `8bit` y `base64` SHALL permanecer correcto. La correccion SHALL
acotarse al canal de correo electronico y MUST NOT alterar el comportamiento de los canales web ni
telefonia.

#### Scenario: Cuerpo quoted-printable con acentos queda limpio

- **WHEN** ingresa por el trigger IMAP un correo cuyo cuerpo se envia como `quoted-printable` con lineas de mas de 78 bytes y caracteres acentuados UTF-8
- **THEN** la descripcion persistida no presenta la firma del mojibake (`Ã`) y conserva los acentos correctos

#### Scenario: Las partes 8bit y base64 no regresan

- **WHEN** ingresa un correo cuyo cuerpo se envia como `8bit` o `base64`
- **THEN** el cuerpo se persiste correctamente, sin mojibake

#### Scenario: Los demas canales no cambian

- **WHEN** ingresa un incidente por el canal web o por el canal telefonico
- **THEN** su descripcion se persiste igual que antes de la correccion

### Requirement: Imagen N8N derivada, pinneada y reproducible

La correccion SHALL entregarse como una imagen N8N derivada de la version pinneada `n8nio/n8n:2.11.2`,
construida a partir de un Dockerfile versionado que aplica un parche documentado sobre el paquete
`@n8n/imap` incluido en la imagen. La version base de N8N MUST NOT cambiar como parte de esta correccion.

#### Scenario: La imagen deriva de la version pinneada

- **WHEN** se inspecciona el Dockerfile derivado
- **THEN** su instruccion `FROM` referencia `n8nio/n8n:2.11.2` y no un tag flotante

#### Scenario: El parche queda documentado y versionado

- **WHEN** se inspecciona el repositorio
- **THEN** existe un Dockerfile y un parche versionados que describen el cambio aplicado al paquete `@n8n/imap`

#### Scenario: El build falla si el parche no aplica

- **WHEN** se construye la imagen derivada sobre un archivo de paquete ausente o con una firma distinta
- **THEN** el build falla en lugar de producir una imagen silenciosamente sin el parche

### Requirement: Verificacion reproducible de la correccion

El proyecto SHALL incluir un procedimiento reproducible que demuestre la correccion enviando un correo
con un cuerpo acentuado de mas de 78 bytes a traves del flujo real y verificando que la descripcion
persistida no presenta la firma del mojibake y conserva los acentos.

#### Scenario: El procedimiento de verificacion reproduce el caso

- **WHEN** un operador ejecuta el procedimiento de verificacion sobre la imagen corregida
- **THEN** obtiene evidencia de que la descripcion almacenada no contiene la firma del mojibake (`Ã`) y si conserva los acentos correctos

#### Scenario: La verificacion distingue imagen corregida de la pinneada

- **WHEN** se ejecuta el mismo procedimiento contra la imagen pinneada sin el parche
- **THEN** la descripcion almacenada presenta la firma del mojibake, lo que confirma que el procedimiento detecta el defecto

### Requirement: Reversibilidad de la imagen derivada

La adopcion de la imagen derivada SHALL ser reversible volviendo a la imagen pinneada upstream mediante
un unico cambio en `docker-compose.yml`, sin cambios de datos ni de esquema.

#### Scenario: El rollback restaura la imagen upstream

- **WHEN** se revierte el servicio a `image: n8nio/n8n:2.11.2` y se recrea el contenedor
- **THEN** el stack vuelve a la imagen upstream sin requerir migracion ni restauracion de datos
