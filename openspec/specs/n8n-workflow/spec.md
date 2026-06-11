# n8n-workflow Specification

## Purpose
TBD - created by archiving change c-04-n8n-workflow-validation. Update Purpose after archive.
## Requirements
### Requirement: Normalización de canales a estructura unificada

El workflow N8N SHALL incluir un nodo de normalización que homogenice la entrada de cualquiera de los tres canales (correo electrónico, formulario web, telefonía con transcripción) en una estructura unificada con exactamente los campos `id` (identificador único), `timestamp` (marca temporal con precisión al milisegundo), `canal_origen` (uno de `correo`, `web`, `telefonia`) y `descripcion` (texto del incidente). Los nodos posteriores SHALL operar exclusivamente sobre esta estructura unificada y no sobre la forma cruda de cada canal.

#### Scenario: Correo electrónico normalizado

- **WHEN** el disparador de Outlook recibe un correo y su carga pasa por el nodo de normalización
- **THEN** la salida contiene `id`, `timestamp` con precisión al milisegundo, `canal_origen = "correo"` y `descripcion` con el cuerpo del incidente

#### Scenario: Transcripción telefónica normalizada

- **WHEN** el AI Agent parsea la transcripción de una llamada Twilio y su salida pasa por el nodo de normalización
- **THEN** la salida contiene los mismos cuatro campos con `canal_origen = "telefonia"`

#### Scenario: Canal de origen inválido rechazado

- **WHEN** la normalización recibe una entrada cuyo canal no es `correo`, `web` ni `telefonia`
- **THEN** el flujo no produce una estructura unificada válida y deriva la entrada a revisión humana

### Requirement: Validación de entrada del canal de correo según Anexo H

El nodo `code` del canal de correo SHALL reemplazar la lógica placeholder por una validación de los campos requeridos para levantar un incidente. SHALL verificar que la descripción exista, no esté en blanco y tenga al menos 10 caracteres. Si la validación falla, el flujo SHALL rutear hacia el nodo que solicita al usuario reenviar los datos faltantes y NO SHALL intentar crear el incidente.

#### Scenario: Correo con datos completos pasa la validación

- **WHEN** el nodo de validación recibe un correo con una descripción de 10 o más caracteres
- **THEN** marca la entrada como válida y el flujo continúa hacia la normalización y clasificación

#### Scenario: Correo con datos faltantes pide reenvío

- **WHEN** el nodo de validación recibe un correo sin descripción o con menos de 10 caracteres
- **THEN** marca la entrada como inválida y el nodo `if` rutea hacia el envío de un mensaje al usuario solicitando los datos faltantes

### Requirement: Validación de la respuesta de clasificación según Anexo H §H.3

El nodo `code` del canal telefónico SHALL validar la respuesta de clasificación aplicando, en orden, los cinco pasos del Anexo H §H.3: (1) parseo JSON válido; (2) presencia de los campos `categoría` y `confianza`; (3) `categoría` exactamente en `{"Sistemas", "Operaciones", "Soporte Técnico"}` (case-sensitive); (4) `confianza` numérica en el rango `[0.0, 1.0]`. Ante el fallo de cualquier paso, SHALL registrar el error, fijar `confianza = 0.0` y marcar el incidente para revisión humana, sin propagar estados inconsistentes.

#### Scenario: Respuesta válida aceptada

- **WHEN** la validación recibe `{"categoría": "Sistemas", "confianza": 0.95}`
- **THEN** la marca como válida y conserva la categoría y la confianza para el ruteo por umbral

#### Scenario: Categoría fuera del conjunto permitido

- **WHEN** la validación recibe una respuesta con `categoría` igual a `"sistemas"` (minúscula) o cualquier valor fuera del conjunto exacto
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: JSON malformado

- **WHEN** la validación recibe un texto que no parsea como JSON
- **THEN** registra el error, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: Confianza fuera de rango

- **WHEN** la validación recibe una `confianza` igual a `1.5` o no numérica
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

### Requirement: Ruteo por umbral de confianza

Los nodos `if` del workflow SHALL evaluar la condición `confianza >= 0.70`. Cuando la condición es verdadera, el flujo SHALL rutear hacia la creación directa del incidente. Cuando es falsa (o la validación previa fijó `confianza = 0.0`), el flujo SHALL marcar el incidente para revisión humana. Las condiciones de los nodos `if` NO SHALL quedar vacías.

#### Scenario: Confianza por encima del umbral crea el incidente

- **WHEN** un nodo `if` evalúa una entrada con `confianza = 0.85`
- **THEN** la condición `confianza >= 0.70` es verdadera y el flujo rutea hacia la persistencia del incidente

#### Scenario: Confianza por debajo del umbral deriva a revisión humana

- **WHEN** un nodo `if` evalúa una entrada con `confianza = 0.60`
- **THEN** la condición es falsa y el flujo marca el incidente para revisión humana

#### Scenario: Confianza en el límite exacto

- **WHEN** un nodo `if` evalúa una entrada con `confianza = 0.70`
- **THEN** la condición `confianza >= 0.70` es verdadera y el flujo rutea hacia la persistencia (el umbral es inclusivo)

### Requirement: Persistencia del incidente vía backend FastAPI

El nodo HTTP de persistencia SHALL invocar `POST /api/v1/incidentes` del backend FastAPI con un cuerpo JSON conforme al schema `IncidenteCreate` (`descripcion`, `prioridad`, `canal`). El workflow SHALL consumir la respuesta del backend (que incluye `sector`, `confianza` y el indicador de revisión humana producidos por `create_and_classify`) como resultado de la clasificación, sin invocar un endpoint de clasificación independiente.

#### Scenario: Creación exitosa devuelve 201

- **WHEN** el nodo HTTP envía un `IncidenteCreate` válido a `POST /api/v1/incidentes`
- **THEN** el backend responde `201 Created` con la representación del incidente clasificado y el flujo lo registra como creado

#### Scenario: El payload respeta el contrato del backend

- **WHEN** se inspecciona el cuerpo que el nodo HTTP envía
- **THEN** contiene el campo `descripcion` (string pseudonimizado de 10 a 5000 caracteres) y la prioridad, sin campos ajenos al schema `IncidenteCreate`

### Requirement: Descripción pseudonimizada en tránsito

El workflow SHALL garantizar que la `descripcion` enviada al backend ya esté pseudonimizada conforme al módulo de pseudonimización (C-03), de modo que no se transmita información personal identificable en claro hacia el subsistema de clasificación. El flujo NO SHALL enviar PII en claro en el campo `descripcion`.

#### Scenario: Descripción pseudonimizada antes de persistir

- **WHEN** una descripción contiene datos personales (nombre, email, teléfono) y atraviesa el flujo hasta el nodo HTTP de persistencia
- **THEN** el valor del campo `descripcion` enviado al backend no contiene la PII en claro, sino su forma pseudonimizada

### Requirement: Workflow exportado verificable por estructura

El JSON exportado del workflow (`Automatizacion_Mesa_de_Ayuda.json`) SHALL ser verificable mediante un conjunto de pruebas automatizadas que validen su estructura sin requerir una instancia N8N en ejecución. Las pruebas SHALL comprobar: la presencia de los nodos esperados, que las condiciones de los nodos `if` no estén vacías, que los nodos `code` no contengan la lógica placeholder `myNewField = 1`, y que el nodo HTTP de persistencia apunte a la ruta `/api/v1/incidentes`.

#### Scenario: Ausencia de placeholders

- **WHEN** la suite de pruebas inspecciona el código de los nodos `code` del workflow exportado
- **THEN** ningún nodo `code` contiene la cadena `myNewField = 1`

#### Scenario: Condiciones IF configuradas

- **WHEN** la suite de pruebas inspecciona los nodos `if` del workflow exportado
- **THEN** cada nodo `if` tiene al menos una condición no vacía que referencia la confianza y el umbral 0.70

#### Scenario: Nodo HTTP de persistencia apunta al endpoint correcto

- **WHEN** la suite de pruebas inspecciona los nodos `httpRequest` del workflow exportado
- **THEN** existe un nodo cuyo destino es la ruta `/api/v1/incidentes`

