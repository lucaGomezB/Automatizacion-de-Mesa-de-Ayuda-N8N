# Delta for telephony-test-softphone

## ADDED Requirements

### Requirement: Seleccion del caso de corpus y listado telefonico en el softphone

El softphone SHALL presentar un control de seleccion (`<select>`) poblado UNICAMENTE con los casos de canal telefonico del corpus de evaluacion (81 casos), con valor por defecto vacio. El modo `serve` SHALL exponer por loopback una lista de casos telefonicos leida de la copia pseudonimizada del corpus (`data/corpus_evaluacion_pseudonimizado.json`), tolerante a la forma exacta del rotulo de canal. Cuando el autor selecciona un caso, la llamada entrante SHALL enviar el `corpus_case_id` seleccionado como parametro custom de la llamada hacia el TwiML App; cuando la seleccion esta vacia, MUST NOT enviarse el parametro (modo de desarrollo sin correlacion). El autor SHALL RECITAR el texto del caso durante la llamada: la herramienta MUST NOT reproducir audio del caso. La lista y su pagina SHALL exponerse solo en loopback y MUST NOT loguear las descripciones de los casos.

#### Scenario: El selector se puebla solo con casos telefonicos

- **WHEN** el operador carga la pagina del softphone servida por el modo `serve`
- **THEN** el control de seleccion lista los casos del canal telefonico del corpus y no casos de otros canales

#### Scenario: Valor por defecto vacio

- **WHEN** el operador abre la pagina sin seleccionar un caso
- **THEN** el control de seleccion no tiene un caso preseleccionado y la llamada no envia `corpus_case_id`

#### Scenario: El caso seleccionado viaja con la llamada

- **WHEN** el operador selecciona un caso y coloca la llamada
- **THEN** la llamada se establece hacia el TwiML App con el `corpus_case_id` seleccionado como parametro custom

#### Scenario: Sin reproduccion de audio

- **WHEN** el operador prepara la recitacion de un caso
- **THEN** la herramienta muestra el texto del caso para recitarlo a mano y no lo reproduce por audio

#### Scenario: Solo loopback y sin logueo de descripciones

- **WHEN** se inspecciona el servidor del softphone
- **THEN** escucha solo en loopback y ninguna descripcion de caso se escribe en un registro persistido
