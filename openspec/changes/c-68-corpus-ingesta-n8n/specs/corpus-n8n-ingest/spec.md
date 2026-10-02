## Purpose

Define el camino de ingesta del corpus de la tesis por el flujo N8N real en los canales de correo y web, la derivacion de la metrica hibrida de latencia por canal, la escritura de los resultados en los archivos del corpus y las garantias de privacidad y trazabilidad que la tesis necesita para que `evaluation/corpus.py` cargue el corpus con tiempos automaticos numericos.

## ADDED Requirements

### Requirement: Ingesta del corpus por el flujo N8N real

El sistema SHALL proveer un harness que cargue los casos del corpus a traves del flujo N8N real, no por un POST directo al backend. Para el canal web el harness SHALL enviar el caso al webhook del formulario web de N8N y SHALL leer el incidente creado por su identificador para obtener `ingresado_en` y `persistido_en`. Para el canal correo el harness SHALL enviar el caso como correo electronico al buzon dedicado y SHALL detectar el incidente creado por el trigger de correo. El harness SHALL cubrir unicamente los canales web y correo (119 casos). El canal de telefonia (81 casos) SHALL quedar FUERA DE ALCANCE del harness y MUST NOT ser ingestado por el; su `tiempo_automatizado_s` SHALL ser cargado MANUALMENTE por el autor.

#### Scenario: Ingesta web por el webhook de N8N

- **WHEN** el harness procesa un caso del canal web
- **THEN** el caso se envia al webhook del formulario web de N8N y el harness lee el incidente resultante por su identificador con sus instantes `ingresado_en` y `persistido_en`

#### Scenario: Ingesta de correo por el buzon dedicado

- **WHEN** el harness procesa un caso del canal correo
- **THEN** el caso se envia como correo electronico al buzon dedicado y el harness detecta el incidente creado por el trigger IMAP sondeando el backend

#### Scenario: Telefono fuera de alcance

- **WHEN** el corpus contiene un caso del canal de telefonia
- **THEN** el harness lo omite sin ingestarlo, sin escribir un valor nulo sobre su tiempo automatico, y lo reporta como pendiente de carga manual por el autor

### Requirement: Derivacion de la metrica hibrida de latencia por canal

El harness SHALL registrar su propio instante de envio `t_envio` en UTC (antes del POST del canal web o antes del envio SMTP del canal correo) y SHALL derivar por caso tres componentes: `t_pipeline_s = latencia_e2e_ms / 1000` (equivalente a `persistido_en - ingresado_en`, libre de la espera del poller); `t_espera_s = ingresado_en - t_envio`; y `t_e2e_s = persistido_en - t_envio = t_espera_s + t_pipeline_s`. El valor canonico `tiempo_automatizado_s` SHALL ser `t_e2e_s` tanto para web como para correo, de modo que la espera del poller quede incluida en el caso de correo y la metrica sea comparable entre canales. El analisis SHALL reportar `t_espera_s` por separado y `t_pipeline_s` como cota inferior libre de poller, y los resultados SHALL reportarse por canal.

#### Scenario: Componentes derivados por caso

- **WHEN** el harness obtiene `ingresado_en` y `persistido_en` de un caso con su `t_envio`
- **THEN** registra `t_pipeline_s`, `t_espera_s` y `t_e2e_s`, y la suma de `t_espera_s` y `t_pipeline_s` coincide con `t_e2e_s`

#### Scenario: Correo incluye la espera del poller

- **WHEN** el canal es correo y el poller recoge el mensaje despues de la llegada al buzon
- **THEN** `t_espera_s` refleja la entrega SMTP y la permanencia en el buzon, y `tiempo_automatizado_s` es `t_e2e_s` con esa espera incluida

#### Scenario: Comportamiento asincronico de la metrica de correo

- **WHEN** se compara la latencia de correo con la de web
- **THEN** el resultado expone `t_pipeline_s` como cota inferior libre de poller y `t_e2e_s` como extremo a extremo percibido, sin mezclar los caveats de canal

### Requirement: Escritura de resultados en el corpus de registro

El harness SHALL escribir los resultados de forma idempotente en AMBOS archivos de registro, el XLSX y su CSV gemelo (mismas columnas en los dos): la columna existente `TIempo de Registro Automatico (Segundos)` SHALL recibir `tiempo_automatizado_s = t_e2e_s`; SHALL escribir `Latencia e2e (ms)` con `latencia_e2e_ms`; y SHALL agregar columnas NUEVAS de descomposicion `Tiempo pipeline (s)` y `Tiempo espera (s)` con `t_pipeline_s` y `t_espera_s` respectivamente. La descomposicion SHALL quedar escrita en el XLSX, en el CSV y en el sidecar. El resto de filas y columnas SHALL preservarse y una re-ejecucion MUST NOT duplicar columnas. El harness SHALL escribir ademas un sidecar JSON de trazabilidad que MUST NOT contener descripciones.

#### Scenario: Columnas del corpus actualizadas

- **WHEN** el harness completa un caso exitoso
- **THEN** tanto el XLSX como el CSV exponen `tiempo_automatizado_s` en la columna de tiempo automatico, `Latencia e2e (ms)`, y las columnas nuevas `Tiempo pipeline (s)` y `Tiempo espera (s)`

#### Scenario: Descomposicion en ambos formatos

- **WHEN** se inspeccionan el XLSX y el CSV gemelo tras una corrida
- **THEN** ambos contienen las mismas columnas de descomposicion con los mismos valores por caso

#### Scenario: Escritura idempotente

- **WHEN** el harness se ejecuta dos veces sobre los mismos archivos
- **THEN** no se duplican columnas y los valores se actualizan en su lugar

#### Scenario: Sidecar sin descripciones

- **WHEN** se inspecciona el sidecar JSON
- **THEN** no contiene ninguna descripcion de caso y solo expone identificadores, instantes y tiempos

### Requirement: Carga del corpus de evaluacion sin debilitar el validador

El harness SHALL escribir `tiempo_automatizado_s` numerico en el corpus de evaluacion JSON, cruzando por identificador de caso, de modo que `evaluation/corpus.py` lo cargue. El merge SHALL ser idempotente y MUST NOT sobrescribir un valor numerico existente con un valor nulo. El validador del corpus (`evaluation/corpus.py::_a_float`) MUST NOT ser debilitado ni modificado para aceptar nulos. Cuando un caso no tenga medicion, el harness SHALL dejar su valor como estaba y SHALL reportar explicitamente el conteo de casos aun nulos. El corpus completo solo queda cargable cuando el autor completa manualmente los 81 valores de telefonia; el harness cubre unicamente los 119 casos de web y correo.

#### Scenario: Corpus de evaluacion cargable

- **WHEN** todos los casos del corpus tienen `tiempo_automatizado_s` numerico (web y correo por el harness, telefonia cargada manualmente por el autor)
- **THEN** `evaluation/corpus.py` carga el corpus sin lanzar `CorpusError`

#### Scenario: Caso sin medicion no se marca nulo

- **WHEN** un caso del corpus no tiene medicion disponible
- **THEN** su `tiempo_automatizado_s` existente se preserva y el harness reporta el conteo de casos aun sin valor

#### Scenario: Telefonia pendiente reportada

- **WHEN** el harness termina una corrida sin que el autor haya cargado los 81 valores de telefonia
- **THEN** el resumen reporta el conteo de casos aun nulos (telefono pendiente) y no modifica esos valores

#### Scenario: El validador no se debilita

- **WHEN** se inspecciona `evaluation/corpus.py`
- **THEN** la validacion que rechaza un `tiempo_automatizado_s` no numerico permanece intacta

### Requirement: Trazabilidad e idempotencia del canal de correo

El harness SHALL asignar a cada correo un encabezado `Message-ID` deterministico derivado del identificador del caso, de modo que mapee al `origen_message_id` que el flujo N8N envia al backend y que la reutilizacion del mismo caso no cree un incidente duplicado. El harness SHALL normalizar el formato del `Message-ID` al correlacionar el caso con el incidente, de modo que la trazabilidad no dependa de los delimitadores de corchete del encabezado. La correlacion PRIMARIA SHALL ser EXACTA, comparando el `origen_message_id` normalizado expuesto por el contrato de lectura provisto por `c-69-dedup-correlacion-altas` (prerequisito de este change), no por heuristica temporal. La correlacion por ventana temporal SHALL considerarse solo un fallback documentado, nunca el mecanismo principal.

#### Scenario: Correlacion exacta por el contrato de lectura

- **WHEN** el harness busca el incidente de un caso de correo
- **THEN** lo correlaciona comparando el `origen_message_id` normalizado expuesto por el contrato de lectura de `c-69` con el `Message-ID` normalizado del caso, sin depender de una ventana temporal

#### Scenario: Fallback documentado

- **WHEN** no se dispone del contrato de lectura exacto
- **THEN** el harness puede recurrir a la correlacion por ventana temporal como fallback documentado, con buzon dedicado, un caso en vuelo y ids reclamados, y lo reporta como modo degradado

#### Scenario: Message-ID deterministico

- **WHEN** el harness envia el mismo caso de correo dos veces
- **THEN** ambos envios comparten el mismo `Message-ID` y el backend devuelve el mismo incidente sin crear una fila nueva

#### Scenario: Correlacion tolerante al formato

- **WHEN** el encabezado `Message-ID` incluye delimitadores de corchete
- **THEN** el harness correlaciona el incidente con el mismo identificador de caso sin depender de los delimitadores

### Requirement: Chequeo secundario de confirmacion de correo

El harness SHALL observar el correo de confirmacion que el flujo N8N envia al remitente como verificacion end-to-end SECUNDARIA, ademas de la lectura de los instantes de la API (medicion primaria y canonica). El harness MUST NOT observar la confirmacion en la misma bandeja que alimenta el trigger IMAP de ingesta, sino por un camino de recepcion SEPARADO (carpeta o buzon dedicado), de modo que la confirmacion no sea re-ingestada como un incidente espurio. El harness SHALL registrar `t_confirmacion` y `confirmacion_recibida` y derivar `t_confirmacion_s = t_confirmacion - t_envio`; la ausencia de confirmacion dentro del timeout MUST NOT invalidar la medicion primaria.

#### Scenario: Confirmacion observada por camino separado

- **WHEN** el flujo N8N envia el correo de confirmacion de un caso
- **THEN** el harness lo detecta en el camino de recepcion separado (no en la bandeja de ingesta), empareja la confirmacion con el caso y registra `t_confirmacion` y `confirmacion_recibida`

#### Scenario: Confirmacion ausente no bloquea la medicion primaria

- **WHEN** la confirmacion no llega dentro del timeout
- **THEN** el caso se reporta con `confirmacion_recibida` en falso y su medicion primaria `t_e2e_s` derivada de los instantes de la API se conserva

#### Scenario: La confirmacion no contamina la ingesta

- **WHEN** se observa una confirmacion
- **THEN** el camino de recepcion de la confirmacion es distinto del que alimenta el trigger IMAP de ingesta y no crea un incidente adicional

### Requirement: Privacidad de las descripciones

El harness SHALL MUST NOT loguear, imprimir ni persistir la descripcion de un caso. Ante un error SHALL emitir solo una etiqueta corta y MUST NOT volcar el cuerpo de una respuesta ni el texto del caso. El sidecar de trazabilidad SHALL ser libre de descripciones por construccion.

#### Scenario: Ninguna descripcion en la salida

- **WHEN** el harness procesa un caso, con exito o con error
- **THEN** ninguna descripcion aparece en la salida estandar, en logs ni en el sidecar

#### Scenario: Error reportado sin cuerpo

- **WHEN** una respuesta del backend o de N8N falla
- **THEN** el harness reporta una etiqueta corta y no el cuerpo de la respuesta

### Requirement: Prerrequisitos de operacion y anomalias

El harness SHALL documentar y verificar sus prerrequisitos de operacion: el workflow N8N activo con las credenciales de IMAP, SMTP y operador cableadas; el camino de recepcion de confirmacion separado del de ingesta; y las credenciales de login leidas exclusivamente del entorno (`INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD`). Ninguna credencial SHALL hardcodearse en el codigo. La corrida COMPLETA SHALL depender de `c-69-dedup-correlacion-altas` (dedup web y correlacion exacta de correo) y del completado manual de los 81 valores de telefonia por el autor; la implementacion del harness MUST NOT quedar bloqueada por esos gates. Los casos con latencia negativa o nula, o con una metrica no positiva, SHALL marcarse como anomalos y excluirse del corpus y del analisis sin recortarlos a cero, y el harness SHALL terminar con codigo distinto de cero ante fallos o anomalias.

#### Scenario: Credenciales desde el entorno

- **WHEN** faltan `INGEST_OPERATOR_USERNAME` o `INGEST_OPERATOR_PASSWORD`
- **THEN** el harness aborta con un mensaje claro y codigo distinto de cero, sin usar ninguna credencial embebida

#### Scenario: Prerrequisitos de N8N documentados

- **WHEN** un operador consulta el runbook del harness
- **THEN** encuentra los pasos para activar el workflow, cablear las credenciales de IMAP, SMTP y operador, y habilitar el camino de confirmacion separado

#### Scenario: Dependencia c-69 documentada como gate de corrida

- **WHEN** el autor consulta las dependencias del harness
- **THEN** `c-69-dedup-correlacion-altas` aparece como prerequisito de la corrida completa y el harness sigue siendo implementable y testeable sin c-69 (contrato mockeado) y sin los 81 valores manuales de telefonia

#### Scenario: Anomalia excluida

- **WHEN** un caso resulta con latencia negativa, nula o metrica no positiva
- **THEN** el caso se marca como anomalo, se excluye del corpus y del analisis y no se recorta a cero
