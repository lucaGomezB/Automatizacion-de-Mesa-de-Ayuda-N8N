# Delta for telefonia-corpus-medicion

## Purpose

Define la corrida de medicion del corpus de la tesis por el canal de telefonia REAL: aislamiento en una base descartable, correlacion exacta de cada llamada con su caso del corpus, metrica canonica de telefonia, recuperacion de la medicion por `corpus_case_id`, escritura de vuelta en los archivos del corpus y reemplazo de mediciones previas. Cierra la carga manual que `corpus-n8n-ingest` dejo fuera de alcance para los 81 casos telefonicos.

## ADDED Requirements

### Requirement: Corrida de telefonia sobre una base descartable

El sistema SHALL ofrecer un perfil de Compose (`corpus`) que corra el flujo telefonico contra una base de datos DESCARTABLE (por ejemplo `mesa_de_ayuda_corpus`), separada de la base de la aplicacion, de modo que una corrida de medicion del corpus MUST NOT contaminar la base operativa. El perfil SHALL incluir los servicios que el flujo telefonico necesita (backend + N8N + PostgreSQL) y SHALL usar volumenes propios de la base descartable. La base descartable SHALL poder limpiarse por completo tras la corrida sin afectar la base de la aplicacion. El sistema SHALL documentar como la Voice URL del TwiML App se conmuta al backend del corpus durante la corrida y el procedimiento de wipe, junto con sus tradeoffs. La corrida de telefonia MUST NOT escribir en la base operativa.

#### Scenario: Base descartable aislada de la operativa

- **WHEN** se levanta el perfil `corpus` y se ejecuta una llamada de medicion
- **THEN** el ingreso y su incidente se persisten en la base descartable y la base de la aplicacion no recibe ninguna fila de la corrida

#### Scenario: Wipe sin tocar la base de la aplicacion

- **WHEN** la corrida termina y se ejecuta el procedimiento de wipe
- **THEN** la base descartable y sus volumenes quedan vacios y la base de la aplicacion permanece intacta

#### Scenario: Conmutacion de la Voice URL documentada

- **WHEN** un operador consulta el runbook de la corrida
- **THEN** encuentra como apuntar la Voice URL del TwiML App al backend del corpus y como restaurarla

### Requirement: Correlacion exacta de la llamada con el caso del corpus

El backend SHALL persistir en el ingreso de telefonia el `corpus_case_id` opcional asociado a la llamada, de modo que una llamada de medicion quede correlacionada de forma EXACTA con su caso del corpus sin heuristica temporal. La correlacion SHALL ser nullable: una llamada de produccion sin caso de corpus MUST NOT ser afectada ni rechazada. El `corpus_case_id` MUST NOT reemplazar ni modificar `call_sid` ni `origen_message_id`, que conservan su rol de idempotencia. El sistema SHALL permitir recuperar el ULTIMO ingreso de un `corpus_case_id` dado.

#### Scenario: Correlacion exacta de la llamada

- **WHEN** el autor coloca una llamada de medicion seleccionando un caso del corpus
- **THEN** el ingreso resultante queda asociado a ese `corpus_case_id` y la recuperacion por ese identificador devuelve la fila correcta

#### Scenario: Llamada sin caso de corpus no se altera

- **WHEN** llega una llamada de produccion sin `corpus_case_id`
- **THEN** el ingreso se procesa igual con `corpus_case_id` nulo y sin cambios en su idempotencia

#### Scenario: La idempotencia por CallSid se preserva

- **WHEN** se persiste un ingreso con `corpus_case_id`
- **THEN** `call_sid` sigue siendo la clave de idempotencia unica y `origen_message_id` del incidente sigue siendo el `CallSid`

### Requirement: Metrica canonica de telefonia

El sistema SHALL derivar el valor canonico `tiempo_automatizado_s` de una medicion de telefonia como `latencia_e2e_ms / 1000`, la MISMA metrica de latencia end-to-end que los demas canales y la MISMA fuente de verdad (`persistido_en - ingresado_en` del incidente, `docs/medicion-latencia-e2e.md`). Porque en telefonia `ingresado_en` se sella en la recepcion del callback de estado de grabacion (no en el inicio de la llamada), la descomposicion SHALL ser `t_e2e_s = t_pipeline_s = latencia_e2e_ms / 1000` y NO existe un componente de espera del cliente. La columna `Tiempo espera (s)` SHALL quedar vacia/N-A para telefonia y el sistema SHALL documentar por que la espera no es medible en este canal. Un caso con latencia nula, negativa o marcada como anomala SHALL excluirse sin recortarse a cero.

#### Scenario: Metrica canonica identica a los otros canales

- **WHEN** se mide un caso de telefonia con `latencia_e2e_ms` disponible
- **THEN** `tiempo_automatizado_s` es `latencia_e2e_ms / 1000` y coincide con `t_pipeline_s` y `t_e2e_s`

#### Scenario: Espera no medible en telefonia

- **WHEN** se inspecciona la escritura de un caso de telefonia
- **THEN** `Tiempo espera (s)` queda vacia/N-A y no se fabrica un valor de espera

#### Scenario: Caso anomalo excluido

- **WHEN** un caso de telefonia resulta con latencia nula, negativa o anomala
- **THEN** se marca como anomalo, se excluye del corpus y del analisis y no se recorta a cero

### Requirement: Recuperacion de la medicion por corpus_case_id

El sistema SHALL proveer un script que, para un `corpus_case_id`, recupere el ULTIMO ingreso de telefonia y resuelva la medicion desde los instantes o la latencia del incidente vinculado (fuente unica de la metrica), exigiendo autenticacion de un operador con alcance de lectura total (`administrador_directorio`). El camino de lectura SHALL exponer el `corpus_case_id` para permitir la recuperacion exacta. Ninguna credencial SHALL hardcodearse: el login SHALL leerse exclusivamente del entorno. Si un `corpus_case_id` no tiene ingreso, el script SHALL reportarlo como pendiente y MUST NOT escribir un valor nulo sobre uno existente.

#### Scenario: Recuperacion del ultimo ingreso

- **WHEN** el script procesa un `corpus_case_id` con mas de un ingreso
- **THEN** recupera el ULTIMO y deriva la metrica de su incidente vinculado

#### Scenario: Credenciales desde el entorno

- **WHEN** faltan las credenciales del operador en el entorno
- **THEN** el script aborta con un mensaje claro y codigo distinto de cero, sin credenciales embebidas

#### Scenario: Caso sin ingreso reportado

- **WHEN** un `corpus_case_id` no tiene ningun ingreso
- **THEN** el script lo reporta como pendiente y no escribe ningun valor sobre su tiempo automatico

### Requirement: Write-back al corpus con las mismas garantias

El script SHALL escribir los resultados de telefonia de forma idempotente en AMBOS archivos de registro (XLSX y su CSV gemelo) y en el JSON de evaluacion, reutilizando el merge/skip y las reglas de privacidad del harness `corpus-n8n-ingest`: la columna `TIempo de Registro Automatico (Segundos)` SHALL recibir `tiempo_automatizado_s`; SHALL escribir `Latencia e2e (ms)` con `latencia_e2e_ms`; SHALL escribir `Tiempo pipeline (s)` con `t_pipeline_s = t_e2e_s`; y SHALL dejar `Tiempo espera (s)` vacia/N-A. El resto de filas y columnas SHALL preservarse, una re-ejecucion MUST NOT duplicar columnas y MUST NOT sobrescribir un valor valido con vacio. El merge del JSON SHALL escribir `tiempo_automatizado_s` numerico por identificador de caso y MUST NOT debilitar `evaluation/corpus.py::_a_float`. El script MUST NOT loguear, imprimir ni persistir descripciones de caso; ante error SHALL emitir solo una etiqueta corta.

#### Scenario: Columnas del corpus con valores de telefonia

- **WHEN** el script completa un caso valido
- **THEN** el XLSX y el CSV exponen `tiempo_automatizado_s`, `Latencia e2e (ms)` y `Tiempo pipeline (s)` con el valor de telefonia, y `Tiempo espera (s)` vacia/N-A

#### Scenario: Escritura idempotente

- **WHEN** el script se ejecuta dos veces sobre los mismos archivos
- **THEN** no se duplican columnas y los valores se actualizan en su lugar

#### Scenario: Ninguna descripcion en la salida

- **WHEN** el script procesa un caso, con exito o con error
- **THEN** ninguna descripcion aparece en la salida estandar, en logs ni en el sidecar

#### Scenario: El validador no se debilita

- **WHEN** se inspecciona `evaluation/corpus.py`
- **THEN** la validacion que rechaza un `tiempo_automatizado_s` no numerico permanece intacta

### Requirement: Reemplazo de mediciones previas de un caso

El script SHALL ofrecer una opcion `--replace` que, al re-medir un caso, elimine el/los ingreso(s) e incidente(s) telefonicos previos de ese `corpus_case_id` (conservando solo el mas reciente) y reemplace el valor del corpus con la nueva medicion valida. Sin `--replace`, el script SHALL actualizar el valor con la ultima medicion y SHALL conservar las filas previas, documentando la diferencia. El borrado SHALL estar acotado por `corpus_case_id`, SHALL respetar las relaciones FK con las tablas hijas (por ejemplo `clasificacion_log`) y MUST NOT afectar filas de otros casos. Antes de cualquier borrado el script SHALL poder operar en modo sin escritura (dry-run).

#### Scenario: Reemplazo conserva solo la medicion nueva

- **WHEN** un caso se re-mide y el script corre con `--replace`
- **THEN** los ingresos e incidentes previos de ese `corpus_case_id` se eliminan, queda solo el mas reciente y el valor del corpus se reemplaza

#### Scenario: Sin replace conserva el historial

- **WHEN** un caso se re-mide y el script corre sin `--replace`
- **THEN** el valor del corpus se actualiza con la ultima medicion y las filas previas permanecen

#### Scenario: Borrado acotado al caso

- **WHEN** el script elimina mediciones previas de un `corpus_case_id`
- **THEN** las filas de otros casos y de otros canales no se modifican

#### Scenario: Dry-run sin escritura

- **WHEN** el script corre en modo dry-run
- **THEN** calcula y reporta el reemplazo y el write-back sin borrar ni escribir nada

### Requirement: Cobertura completa de los 81 casos de telefonia

La corrida de medicion SHALL cubrir los 81 casos del corpus cuyo canal es la llamada telefonica, sin muestreo. El autor SHALL medir cada caso por el flujo real, recitando el texto del caso en la llamada. El script SHALL reportar el conteo de casos medidos, pendientes y anomalos, y el corpus completo SHALL quedar cargable por `evaluation/corpus.py` una vez cargados los 81 valores.

#### Scenario: Los 81 casos medidos

- **WHEN** el autor completa la corrida de telefono
- **THEN** los 81 casos del canal telefonico tienen `tiempo_automatizado_s` numerico o un reporte explicito de los pendientes/anomalos

#### Scenario: Sin muestreo

- **WHEN** se configura la corrida
- **THEN** no existe un modo que limite la medicion a una muestra y el reporte refleja los 81 casos

#### Scenario: Corpus cargable al completar

- **WHEN** web, correo y los 81 telefonos tienen `tiempo_automatizado_s` numerico
- **THEN** `evaluation/corpus.py` carga el corpus sin lanzar `CorpusError`

### Requirement: Privacidad y secretos de la corrida de telefonía

El script y la corrida SHALL leer todas las credenciales exclusivamente de variables de entorno y MUST NOT contener secretos hardcodeados. El script MUST NOT loguear, imprimir ni persistir la descripcion de un caso; el sidecar de trazabilidad SHALL ser libre de descripciones por construccion. La lista de casos servida al softphone SHALL provenir de la copia pseudonimizada del corpus y SHALL exponerse solo en loopback.

#### Scenario: Sin secretos en el codigo

- **WHEN** se inspecciona el contenido versionado del script y del perfil de Compose
- **THEN** no contiene secretos ni credenciales, solo referencias a variables de entorno

#### Scenario: Sidecar sin descripciones

- **WHEN** se inspecciona el sidecar de la corrida de telefonia
- **THEN** no contiene ninguna descripcion de caso, solo identificadores, instantes y tiempos
