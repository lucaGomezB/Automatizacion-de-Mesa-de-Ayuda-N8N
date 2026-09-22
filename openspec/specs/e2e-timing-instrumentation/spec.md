# e2e-timing-instrumentation Specification

## Purpose
Define el contrato de medicion de la latencia END-TO-END por incidente, desde el ingreso del mensaje al sistema hasta su persistencia confirmada en la base, de modo que la tesis pueda derivar `tiempo_automatizado_s` de forma reproducible y auditable.

## Requirements

### Requirement: Instante de ingreso del incidente

El sistema SHALL persistir por incidente el instante en que el mensaje ingresa al sistema, recibido desde el emisor en el payload de alta como `ingresado_en` en formato ISO-8601 con zona horaria. El instante SHALL corresponder al borde del trigger del canal y MUST NOT corresponder a un punto posterior del pipeline de procesamiento. Si el emisor no provee el campo, el incidente SHALL crearse igualmente con `ingresado_en` nulo.

#### Scenario: Ingreso persistido y normalizado a UTC

- **WHEN** se crea un incidente con un `ingresado_en` valido con zona horaria
- **THEN** el valor se persiste normalizado a UTC en la columna `ingresado_en`

#### Scenario: Ausencia del instante no bloquea el alta

- **WHEN** el payload de alta no incluye `ingresado_en`
- **THEN** el incidente se crea con `ingresado_en` nulo

#### Scenario: El ingreso refleja el borde del trigger

- **WHEN** el canal es telefonia y el agente de IA consume tiempo antes de la normalizacion
- **THEN** `ingresado_en` es anterior al inicio del agente, de modo que la latencia incluye ese tiempo

### Requirement: Persistencia confirmada e inmutable

El backend SHALL sellar `persistido_en` una sola vez, dentro de la transaccion de alta y clasificacion, como el instante en que se finalizan las escrituras del incidente y su clasificacion inmediatamente antes del commit. `persistido_en` SHALL ser inmutable: ningun update posterior del incidente (revision humana, cambio de estado o actualizacion parcial) SHALL modificarlo. `updated_at` MUST NOT usarse como instante de persistencia confirmada porque se recalcula en cada update.

#### Scenario: Sellado en el alta

- **WHEN** se crea y clasifica un incidente
- **THEN** `persistido_en` queda con un valor no nulo

#### Scenario: Inmutable ante updates posteriores

- **WHEN** se actualiza un incidente existente (estado, sector o bandera de revision humana)
- **THEN** `persistido_en` conserva su valor original

#### Scenario: Independiente de updated_at

- **WHEN** un update modifica `updated_at`
- **THEN** `persistido_en` no cambia

### Requirement: Derivacion de la latencia end-to-end

La latencia SHALL derivarse como `latencia_e2e_ms = persistido_en - ingresado_en` expresada en milisegundos. El sistema SHALL exponer `latencia_e2e_ms` en la representacion de lectura del incidente. La latencia SHALL ser nula cuando falte cualquiera de los dos instantes. El sistema MUST NOT persistir la latencia como columna denormalizada, para no duplicar la fuente de verdad.

La exposicion SHALL alcanzar AMBAS representaciones de lectura del incidente: el detalle y la proyeccion de listado. La proyeccion de listado SHALL exponer ademas los dos instantes fuente (`ingresado_en`, `persistido_en`) y SHALL derivar `latencia_e2e_ms` con la misma logica que el detalle, de modo que ambas representaciones devuelvan el mismo valor para un mismo incidente. Un incidente con instantes ausentes SHALL listarse igualmente con `latencia_e2e_ms` nulo, sin fallar la serializacion.

#### Scenario: Derivacion correcta

- **WHEN** el incidente tiene `ingresado_en` y `persistido_en` no nulos
- **THEN** `latencia_e2e_ms` es la diferencia entre ambos instantes

#### Scenario: Latencia nula si falta un instante

- **WHEN** falta `ingresado_en` o `persistido_en`
- **THEN** `latencia_e2e_ms` es nulo

#### Scenario: Unidades en milisegundos

- **WHEN** la diferencia entre `persistido_en` e `ingresado_en` es de 12.5 segundos
- **THEN** `latencia_e2e_ms` es 12500

#### Scenario: Proyeccion de listado expone los instantes y la latencia

- **WHEN** se consulta el listado de incidentes y un incidente tiene `ingresado_en` y `persistido_en` no nulos
- **THEN** cada item del listado incluye ambos instantes fuente y `latencia_e2e_ms` con un valor no nulo

#### Scenario: Proyeccion de listado con instantes ausentes

- **WHEN** un incidente del listado tiene `ingresado_en` o `persistido_en` nulo
- **THEN** el item expone `latencia_e2e_ms` nulo y el listado se serializa sin error

#### Scenario: Paridad de derivacion entre detalle y listado

- **WHEN** un mismo incidente se lee por el endpoint de detalle y por el endpoint de listado
- **THEN** `latencia_e2e_ms` coincide en ambas representaciones al milisegundo

### Requirement: Politica de latencia negativa

Cuando `latencia_e2e_ms` resulte menor que cero, el sistema SHALL NOT reportarlo como una medicion valida. El valor SHALL marcarse como anomalo y SHALL excluirse del corpus y del analisis; el sistema MUST NOT aceptarlo en silencio. La anomalia SHALL quedar registrada para diagnostico (por ejemplo, ingreso futuro dentro de la tolerancia o skew de relojes). La marca de anomalia SHALL ser observable en toda representacion de lectura que exponga la latencia, incluida la proyeccion de listado.

#### Scenario: Latencia negativa marcada como anomalia

- **WHEN** `persistido_en - ingresado_en` es menor que cero
- **THEN** `latencia_e2e_ms` se marca como anomalo y no como medicion valida

#### Scenario: Excluida del corpus y del analisis

- **WHEN** se construye el corpus o el analisis de latencias
- **THEN** los casos con `latencia_e2e_ms` negativo se excluyen

#### Scenario: Nunca aceptada en silencio

- **WHEN** se deriva una latencia negativa
- **THEN** el sistema no la reporta como valida sin marcar la anomalia

#### Scenario: Anomalia visible en la proyeccion de listado

- **WHEN** un incidente del listado tiene `persistido_en` anterior a `ingresado_en`
- **THEN** el item expone `latencia_e2e_ms` nulo y la marca de anomalia en verdadero

### Requirement: Validacion del instante de ingreso

El backend SHALL aceptar `ingresado_en` solo si es un instante ISO-8601 con zona horaria explicita. Un valor sin zona horaria (naive) SHALL rechazarse con error de validacion. Un valor posterior al instante del servidor mas alla de una tolerancia configurable SHALL rechazarse para evitar latencias negativas. La tolerancia SHALL ser configurable con un valor por defecto de 30 s. Un valor nulo SHALL aceptarse.

#### Scenario: Valor con zona horaria aceptado

- **WHEN** `ingresado_en` incluye un sufijo `Z` u offset explicito
- **THEN** se acepta y se normaliza a UTC

#### Scenario: Valor sin zona horaria rechazado

- **WHEN** `ingresado_en` no incluye zona horaria
- **THEN** se rechaza con un error de validacion que identifica el campo

#### Scenario: Futuro fuera de tolerancia rechazado

- **WHEN** `ingresado_en` supera el ahora del servidor mas alla de la tolerancia configurada
- **THEN** se rechaza con un error de validacion

#### Scenario: Desfase de reloj dentro de tolerancia aceptado

- **WHEN** `ingresado_en` esta en el futuro por un desfase menor a la tolerancia
- **THEN** se acepta para tolerar skew de relojes entre contenedores

#### Scenario: Tolerancia por defecto de 30 s

- **WHEN** no se configura explicitamente la tolerancia de futuro
- **THEN** la tolerancia aplicada es de 30 s

### Requirement: Exclusion de replays idempotentes de la medicion

Un reintento del mismo `origen_message_id` SHALL devolver el incidente existente SIN re-medir: `ingresado_en` y `persistido_en` SHALL conservar los valores del alta original. La medicion SHALL realizarse a nivel de fila de incidente, de modo que un replay no genere una segunda fila ni una segunda latencia.

#### Scenario: El replay conserva la medicion original

- **WHEN** llega un segundo alta con el mismo `origen_message_id`
- **THEN** se devuelve la fila existente con sus `ingresado_en` y `persistido_en` originales

#### Scenario: El replay no crea fila nueva

- **WHEN** ocurre un replay idempotente
- **THEN** la cantidad de filas de incidente para ese `origen_message_id` no aumenta

### Requirement: Caveats por canal de la medicion

El contrato SHALL declarar las salvedades que condicionan la comparabilidad entre canales: en el canal de correo el ingreso es el instante en que el poller de Outlook recoge el mensaje, NO la llegada al buzon; la latencia EXCLUYE la espera previa a la recogida (hasta aproximadamente 60 s por `everyMinute`), por lo que sub-mide respecto de la llegada real al buzon y no es comparable caso a caso con los otros canales; en el canal de telefonia el ingreso es la recepcion del resumen post-llamada de Twilio y la latencia NO incluye la duracion de la llamada ni la generacion del resumen en Twilio. La documentacion del contrato SHALL registrar ambos caveats y el analisis SHALL reportarse por canal.

#### Scenario: Caveat de correo declarado

- **WHEN** se consulta la documentacion del contrato de medicion
- **THEN** que la latencia de correo excluye la espera previa a la recogida del poller y sub-mide respecto de la llegada al buzon queda declarado explicitamente

#### Scenario: Caveat de telefonia declarado

- **WHEN** se consulta la documentacion del contrato de medicion
- **THEN** el inicio post-resumen de la telefonia queda declarado explicitamente

#### Scenario: Analisis separado por canal

- **WHEN** se comparan latencias entre canales
- **THEN** el analisis distingue el canal para no mezclar caveats incompatibles
