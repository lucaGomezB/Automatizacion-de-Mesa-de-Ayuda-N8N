## ADDED Requirements

### Requirement: Aceleración opcional del aviso en las llamadas del softphone

El softphone de desarrollo SHALL enviar la tasa de locución del aviso (`tts_rate`) como
parámetro custom de la llamada cuando haya un caso del corpus seleccionado, de modo que
la campaña entregue el aviso a esa tasa. El valor SHALL ser un porcentaje dentro del rango
soportado (por ejemplo `125%`). Cuando NO haya un caso seleccionado, la llamada MUST NOT
enviar `tts_rate` y MUST mantener el modo de desarrollo vigente sin cambios. La
herramienta MUST NOT introducir dependencias adicionales ni reproducir audio del caso.

#### Scenario: Con caso seleccionado la llamada lleva la tasa de aviso

- **WHEN** el operador selecciona un caso y coloca la llamada
- **THEN** la llamada se establece hacia el TwiML App con `corpus_case_id` y `tts_rate` como parámetros custom de la llamada

#### Scenario: Sin caso seleccionado la llamada no lleva la tasa

- **WHEN** el operador coloca la llamada sin un caso seleccionado
- **THEN** la llamada no envía `tts_rate` ni `corpus_case_id` y se mantiene el modo de desarrollo vigente
