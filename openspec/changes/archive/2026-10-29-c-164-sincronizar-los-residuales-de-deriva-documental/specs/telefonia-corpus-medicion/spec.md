## MODIFIED Requirements

### Requirement: Metrica canonica de telefonia

El sistema SHALL derivar el valor canonico `tiempo_automatizado_s` de una medicion de telefonia como `duracion_segundos + latencia_e2e_ms / 1000` (Grupo E, Opción A de c-77), donde `duracion_segundos` es la duracion de la grabacion/llamada provista por Twilio y `latencia_e2e_ms` es la MISMA metrica de latencia end-to-end que los demas canales, derivada de la MISMA fuente de verdad (`persistido_en - ingresado_en` del incidente vinculado, `docs/medicion-latencia-e2e.md`). Porque en telefonia `ingresado_en` se sella en la recepcion del callback de estado de grabacion (no en el inicio de la llamada), la descomposicion SHALL ser `t_e2e_s = t_pipeline_s = duracion_segundos + latencia_e2e_ms / 1000`: el tiempo de telefonia SUMA la duracion de la grabacion a la latencia de pipeline, y NO existe un componente de espera del cliente. La grabacion esta acotada a 45 s (`<Record maxLength="45">`), por lo que el valor resultante es una COTA INFERIOR del tiempo real de la llamada. Una `duracion_segundos` ausente SHALL contribuir cero, sin fabricar un valor ficticio. La columna `Tiempo espera (s)` SHALL quedar vacia/N-A para telefonia y el sistema SHALL documentar por que la espera no es medible en este canal. Un caso con latencia nula, negativa o marcada como anomala SHALL excluirse sin recortarse a cero.

#### Scenario: Metrica canonica identica a los otros canales

- **WHEN** se mide un caso de telefonia con `latencia_e2e_ms` disponible
- **THEN** `tiempo_automatizado_s` es `duracion_segundos + latencia_e2e_ms / 1000` y coincide con `t_pipeline_s` y `t_e2e_s`, con la misma fuente de latencia que los otros canales

#### Scenario: Espera no medible en telefonia

- **WHEN** se inspecciona la escritura de un caso de telefonia
- **THEN** `Tiempo espera (s)` queda vacia/N-A y no se fabrica un valor de espera

#### Scenario: Caso anomalo excluido

- **WHEN** un caso de telefonia resulta con latencia nula, negativa o anomala
- **THEN** se marca como anomalo, se excluye del corpus y del analisis y no se recorta a cero
