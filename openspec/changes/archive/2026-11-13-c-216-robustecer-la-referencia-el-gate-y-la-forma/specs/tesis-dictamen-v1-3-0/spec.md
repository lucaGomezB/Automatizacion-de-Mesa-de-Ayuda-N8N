## MODIFIED Requirements

### Requirement: Consentimiento de E3 y E4 según el registro

`11-aspectos-legales.tex` SHALL mencionar a los etiquetadores `E3` y `E4` del doble etiquetado
independiente y al árbitro `E5`, y SHALL afirmar solo lo que respalda
`docs/campana-medicion/confirmacion-posterior-consentimiento.md`: información verbal el
`2026-11-12` y confirmación escrita firmada el `2026-11-13`, con los originales en poder del
director y fuera del repositorio. El registro de sujetos (`evaluation/data/campana/registro_sujetos.csv`)
y el README de campaña SHALL ser consistentes con ese estado: el registro SHALL contener las
filas `E3`, `E4` y `E5` sin datos personales y el README SHALL informar el número vigente de
filas. El texto MUST NOT reintroducir la afirmación de confirmación pendiente ni fechas
distintas de las registradas. Este requisito verifica y cierra la recomendación R4 del dictamen
v1.3.0; MUST NOT reescribir el capítulo legal más allá de la consistencia verificada.

#### Scenario: Registro firmado y texto consistente

- **WHEN** el registro tiene `fecha_informacion_verbal = 2026-11-12` y `fecha_confirmacion = 2026-11-13` para `E3`, `E4` y `E5`
- **THEN** el capítulo legal menciona a los tres con esas fechas
- **AND** no aparece la afirmación de que la confirmación escrita está pendiente

#### Scenario: Registro de sujetos y README consistentes

- **WHEN** se cuentan las filas de `registro_sujetos.csv`
- **THEN** el README de campaña informa ese mismo número
- **AND** las filas `E3`, `E4` y `E5` no contienen nombre, correo ni legajo

#### Scenario: Sin fechas inventadas

- **WHEN** se comparan las fechas del capítulo legal con las del registro
- **THEN** coinciden
- **AND** el texto no afirma una fecha de firma que el registro no respalde

#### Scenario: Registro pendiente

- **WHEN** el registro no tiene `fecha_confirmacion` para `E3`, `E4` o `E5`
- **THEN** el capítulo legal no afirma un consentimiento escrito ni completa la fecha por su cuenta
- **AND** el registro no se modifica para hacer que la afirmación cierre