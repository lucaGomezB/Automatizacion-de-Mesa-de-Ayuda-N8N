## MODIFIED Requirements

### Requirement: Instante de ingreso del incidente

El sistema SHALL persistir por incidente el instante en que el mensaje ingresa al sistema, recibido desde el emisor en el payload de alta como `ingresado_en` en formato ISO-8601 con zona horaria. Para los canales de correo y web, el instante SHALL corresponder al borde del trigger del canal. Para el canal de telefonía, el instante SHALL ser el sellado por el BACKEND al recibir el callback de estado de grabación, ANTES de descargar y transcribir el audio; n8n SHALL propagarlo como passthrough SIN re-sellarlo. En ningún canal el instante SHALL corresponder a un punto posterior del pipeline de procesamiento. Si el emisor no provee el campo, el incidente SHALL crearse igualmente con `ingresado_en` nulo.

#### Scenario: Ingreso persistido y normalizado a UTC

- **WHEN** se crea un incidente con un `ingresado_en` valido con zona horaria
- **THEN** el valor se persiste normalizado a UTC en la columna `ingresado_en`

#### Scenario: Ausencia del instante no bloquea el alta

- **WHEN** el payload de alta no incluye `ingresado_en`
- **THEN** el incidente se crea con `ingresado_en` nulo

#### Scenario: El ingreso refleja el borde del trigger

- **WHEN** el canal es telefonia y el agente de IA consume tiempo antes de la normalizacion
- **THEN** `ingresado_en` es anterior al inicio del agente, de modo que la latencia incluye ese tiempo

#### Scenario: El ingreso de correo y web refleja el borde del trigger

- **WHEN** el canal es correo o web y el pipeline consume tiempo antes de la normalizacion
- **THEN** `ingresado_en` es anterior al inicio de ese procesamiento, de modo que la latencia incluye ese tiempo

#### Scenario: El ingreso de telefonia refleja la recepción del callback del backend

- **WHEN** el canal es telefonia
- **THEN** `ingresado_en` es el instante en que el backend recibió el callback de estado de grabación y es anterior a la descarga y transcripción, de modo que la latencia incluye ese trabajo

### Requirement: Caveats por canal de la medicion

El contrato SHALL declarar las salvedades que condicionan la comparabilidad entre canales: en el canal de correo el ingreso es el instante en que el poller de Outlook recoge el mensaje, NO la llegada al buzon; la latencia EXCLUYE la espera previa a la recogida (hasta aproximadamente 60 s por `everyMinute`), por lo que sub-mide respecto de la llegada real al buzon y no es comparable caso a caso con los otros canales; en el canal de telefonia el ingreso es la recepción del callback de estado de grabación del backend y la latencia INCLUYE la descarga de la grabación, la transcripción con el motor dedicado, la pseudonimización y el handoff hacia n8n, pero NO incluye la duración de la llamada ni el tiempo previo de generación de la grabación en Twilio. La documentacion del contrato SHALL registrar ambos caveats y el analisis SHALL reportarse por canal.

#### Scenario: Caveat de correo declarado

- **WHEN** se consulta la documentacion del contrato de medicion
- **THEN** que la latencia de correo excluye la espera previa a la recogida del poller y sub-mide respecto de la llegada al buzon queda declarado explicitamente

#### Scenario: Caveat de telefonia declarado

- **WHEN** se consulta la documentacion del contrato de medicion
- **THEN** que la latencia de telefonia incluye la descarga, la transcripcion, la pseudonimizacion y el handoff del backend, y excluye la duracion de la llamada, queda declarado explicitamente

#### Scenario: Analisis separado por canal

- **WHEN** se comparan latencias entre canales
- **THEN** el analisis distingue el canal para no mezclar caveats incompatibles

## ADDED Requirements

### Requirement: Latencia de telefonia con transcripcion incluida

La latencia end-to-end del canal de telefonía SHALL medirse como `persistido_en - ingresado_en`, con `ingresado_en` sellado en la recepción del callback del backend. Por construcción, esa latencia SHALL incluir el trabajo de descarga, transcripción, pseudonimización y handoff que ocurre después del sellado y antes del alta. El contrato MUST NOT excluir ese trabajo de la medición ni usar un instante de ingreso posterior al callback.

#### Scenario: La latencia incluye el trabajo del backend

- **WHEN** se mide la latencia de un incidente telefónico
- **THEN** el intervalo incluye la descarga, la transcripción, la pseudonimización y el handoff previos al alta

#### Scenario: El ingreso no se mueve aguas abajo

- **WHEN** se verifica el instante de ingreso de un incidente telefónico sellado por el backend
- **THEN** ese instante es anterior a la descarga y transcripción y no se reemplaza por un instante posterior