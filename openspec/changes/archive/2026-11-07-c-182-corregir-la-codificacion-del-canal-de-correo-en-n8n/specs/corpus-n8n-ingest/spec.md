## ADDED Requirements

### Requirement: Codificacion de transferencia base64 del correo de ingesta del harness

El harness `scripts/corpus_ingest/ingest_via_n8n.py` SHALL construir el correo de ingesta del canal de
correo con `Content-Transfer-Encoding: base64`, de modo que el cuerpo no dependa de la rama
`quoted-printable` del trigger IMAP. El cambio SHALL preservar el `Message-ID` deterministico por caso y
SHALL preservar el contenido textual del cuerpo (round-trip exacto entre la descripcion del caso y el
cuerpo del mensaje construido).

#### Scenario: El cuerpo del correo se codifica en base64

- **WHEN** el harness construye el mensaje de ingesta de un caso de correo
- **THEN** el mensaje expone `Content-Transfer-Encoding: base64`

#### Scenario: El round-trip del cuerpo se preserva

- **WHEN** se decodifica el cuerpo del mensaje construido por el harness
- **THEN** el texto resultante es identico a la descripcion del caso, incluidos los caracteres acentuados

#### Scenario: La correlacion deterministica no se altera

- **WHEN** el harness construye el mismo caso de correo dos veces
- **THEN** ambos mensajes comparten el mismo `Message-ID` deterministico derivado del identificador del caso
