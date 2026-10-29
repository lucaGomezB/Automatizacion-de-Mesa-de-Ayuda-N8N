# Delta for n8n-workflow

## MODIFIED Requirements

### Requirement: Normalización de canales a estructura unificada

El workflow N8N SHALL incluir un nodo de normalización que homogenice la entrada de cualquiera de los tres canales (correo electrónico, formulario web, telefonía con transcripción) en una estructura unificada con exactamente los campos `id`, `timestamp` (precisión al milisegundo), `canal_origen` (uno de `correo`, `web`, `telefonia`) y `descripcion`. Los nodos posteriores SHALL operar exclusivamente sobre esta estructura y no sobre la forma cruda de cada canal. Para el canal de correo, la normalización SHALL consumir los campos genéricos del mensaje IMAP (remitente, asunto, cuerpo de texto y fecha de recepción) y NO SHALL depender de campos propios de un proveedor. Para el canal de telefonía, la normalización SHALL consumir el ingreso pseudonimizado sellado por el backend a través del cableado `Sellar -> Normalizar` y MUST NOT depender de un nodo de clasificacion en n8n.

Además, la estructura normalizada SHALL propagar el contacto del reportante acotado por canal, de modo que el backend pueda resolver al reportante: `reportante_email` con la dirección de correo normalizada cuando `canal_origen = "correo"`, y `reportante_telefono` con el número llamante propagado por el handoff cuando `canal_origen = "telefonia"`. En cualquier otro canal, o cuando el canal no provea el contacto, ambos campos SHALL ser `null`. El contacto propagado es un dato de resolución transitoria: la normalización MUST NOT persistirlo ni escribirlo en el registro de auditoría.

#### Scenario: Correo electrónico normalizado

- **WHEN** el disparador IMAP recibe un correo y su carga pasa por el nodo de normalización
- **THEN** la salida contiene `id`, `timestamp` con precisión al milisegundo, `canal_origen = "correo"` y `descripcion` con el cuerpo del incidente

#### Scenario: Transcripción telefónica normalizada

- **WHEN** la transcripción pseudonimizada de una llamada Twilio sellada por el backend atraviesa el cableado `Sellar -> Normalizar` hasta el nodo de normalización
- **THEN** la salida contiene los mismos cuatro campos con `canal_origen = "telefonia"`, sin un nodo de clasificacion en n8n en la ruta

#### Scenario: Canal de origen inválido rechazado

- **WHEN** la normalización recibe una entrada cuyo canal no es `correo`, `web` ni `telefonia`
- **THEN** el flujo no produce una estructura unificada válida y deriva la entrada a revisión humana

#### Scenario: El contacto del reportante viaja en la estructura normalizada

- **WHEN** una entrada del canal correo con remitente válido, o del canal telefonía con número llamante, atraviesa la normalización
- **THEN** la salida contiene `reportante_email` no nulo para correo y `reportante_telefono` no nulo para telefonía, derivados del remitente normalizado y del número llamante respectivamente

#### Scenario: El contacto es nulo en el canal que no corresponde

- **WHEN** la normalización procesa una entrada de un canal sin contacto disponible (por ejemplo web) o un canal cuyo contacto no pudo resolverse
- **THEN** `reportante_email` y `reportante_telefono` son `null` y la normalización no falla

### Requirement: Persistencia del incidente vía backend FastAPI

El nodo HTTP de persistencia SHALL invocar `POST /api/v1/incidentes` del backend FastAPI con un cuerpo JSON conforme al schema `IncidenteCreate` (`descripcion`, `prioridad`, `canal`). El workflow SHALL consumir la respuesta del backend (que incluye `sector`, `confianza` y el indicador de revisión humana producidos por `create_and_classify`) como resultado de la clasificación, sin invocar un endpoint de clasificación independiente. El cuerpo SHALL incluir además `reportante_email` y `reportante_telefono` resueltos por expresión desde la estructura normalizada, de modo que el backend resuelva al reportante contra el directorio; cada campo SHALL ser null-safe (resolver a `null` cuando el canal no aporte el contacto) y MUST NOT transportar el contacto crudo del canal.

#### Scenario: Creación exitosa devuelve 201

- **WHEN** el nodo HTTP envía un `IncidenteCreate` válido a `POST /api/v1/incidentes`
- **THEN** el backend responde `201 Created` con la representación del incidente clasificado y el flujo lo registra como creado

#### Scenario: El payload respeta el contrato del backend

- **WHEN** se inspecciona el cuerpo que el nodo HTTP envía
- **THEN** contiene el campo `descripcion` (string pseudonimizado de 10 a 5000 caracteres) y la prioridad, sin campos ajenos al schema `IncidenteCreate`

#### Scenario: El payload incluye el contacto del reportante resuelto por canal

- **WHEN** la suite estructural inspecciona el `jsonBody` del nodo `HTTP POST a MESA-AYUDAS`
- **THEN** el cuerpo contiene `reportante_email` y `reportante_telefono` resueltos por expresión desde el normalizador y no como constantes

#### Scenario: El contacto del payload es null-safe

- **WHEN** el canal no aporta el contacto correspondiente
- **THEN** el valor enviado para ese campo es `null` y el alta no falla por un contacto ausente

### Requirement: N8N-EMAIL-002 — Destinatario de confirmación resuelto desde el remitente original

El nodo `Correo de confirmacion al usuario` SHALL resolver `toRecipients` desde el remitente original propagado en la estructura normalizada (campo `remitente`) y MUST NOT depender del ítem corriente posterior al POST, que es la respuesta del backend y no expone `remitente` ni `from`. La estructura normalizada SHALL propagar `remitente` desde el payload del trigger de correo (`from`), admitiendo que el remitente llegue tanto como cadena de texto como como objeto estructurado que anida la dirección (`from.emailAddress.address`); la normalización SHALL extraer la dirección de correo efectiva en ambos casos y SHALL descartar, con señal observable, un remitente que no resuelva a una dirección válida. El contacto normalizado SHALL propagarse al cuerpo del POST únicamente como `reportante_email` para la resolución transitoria del reportante en el backend; el campo `remitente` como tal MUST NOT persistirse ni agregarse al registro de auditoría, por ser dato personal.
(Previously: el `remitente` MUST NOT agregarse al cuerpo del POST ni a la auditoría; ahora se acota a que el campo crudo `remitente` no se persiste, mientras el contacto normalizado SÍ viaja al POST como `reportante_email` para resolver reportante.)

#### Scenario: Un correo con remitente produce destinatario no vacío

- **WHEN** un correo con remitente válido llega al nodo de confirmación por la rama del canal correo
- **THEN** `toRecipients` resuelve a una dirección no vacía tomada de la estructura normalizada

#### Scenario: Remitente en forma de objeto resuelve la dirección

- **WHEN** el `from` del mensaje entrante es un objeto estructurado con la dirección anidada
- **THEN** la normalización extrae la dirección de correo efectiva y `toRecipients` la usa

#### Scenario: Remitente inválido no produce destinatario inválido

- **WHEN** el remitente entrante no puede resolverse a una dirección válida
- **THEN** la normalización lo descarta con una señal observable y no propaga una representación inválida como destinatario

#### Scenario: La expresión referencia el nodo normalizador

- **WHEN** la suite estructural inspecciona `toRecipients` del nodo de confirmación
- **THEN** la expresión referencia `Normalizar entrada del incidente` (aguas arriba) y no solo el ítem corriente

#### Scenario: El remitente no contamina el payload ni la auditoría

- **WHEN** se inspecciona el cuerpo del POST de persistencia y el código del nodo de auditoría
- **THEN** el cuerpo no incluye el campo crudo `remitente` (sí el `reportante_email` de resolución) y el código de auditoría no incluye el contacto

#### Scenario: El contacto normalizado se propaga al POST sin persistirse ni auditarse

- **WHEN** un correo con remitente válido atraviesa el flujo hasta el POST
- **THEN** el cuerpo incluye `reportante_email` con esa dirección y el contacto no aparece en el registro de auditoría ni como campo crudo del canal

## ADDED Requirements

### Requirement: N8N-CONTACT-001 — El flujo N8N propaga el contacto del reportante para su resolución en el backend

El workflow N8N SHALL propagar el contacto del reportante al backend para que este resuelva al empleado contra el directorio, sin que el incidente caiga en revisión humana por reportante no identificado (VIS-005, c-82) cuando el contacto corresponde a un empleado del directorio. Para el canal de correo SHALL propagar `reportante_email`; para el canal de telefonía SHALL propagar `reportante_telefono`. El canal web queda FUERA del alcance de este change (declarado): el formulario web no aporta contacto y la cuenta autenticada es la del operador, de modo que el web MUST NOT enviar `reportante_email` ni `reportante_telefono` en este change. El contacto SHALL ser null-safe y transitorio: MUST NOT persistirse crudo ni escribirse en auditoría.

#### Scenario: El canal de correo propaga el email del reportante

- **WHEN** un correo de un empleado del directorio atraviesa el flujo hasta el POST
- **THEN** el cuerpo enviado incluye `reportante_email` con la dirección del remitente y el backend resuelve al empleado

#### Scenario: El canal de telefonía propaga el teléfono del reportante

- **WHEN** una llamada de un número presente en el directorio atraviesa el flujo hasta el POST
- **THEN** el cuerpo enviado incluye `reportante_telefono` con el número llamante y el backend resuelve al empleado

#### Scenario: El canal web queda fuera de alcance y no envía contacto

- **WHEN** la suite estructural inspecciona el `jsonBody` del POST para una entrada del canal web
- **THEN** el campo `reportante_email` y el campo `reportante_telefono` no resuelven a un valor de contacto del formulario, porque el canal web se declara fuera del alcance de este change

#### Scenario: El contacto no deriva por reportante no identificado cuando resuelve

- **WHEN** el contacto propagado corresponde a un empleado activo del directorio
- **THEN** el backend vincula el incidente al empleado y no marca la derivación por reportante no identificado de VIS-005

#### Scenario: El contacto propagado no es PII persistida

- **WHEN** el incidente se persiste
- **THEN** el modelo almacena la referencia al empleado (`reportante_empleado_id`) y no el contacto crudo, y la auditoría del workflow no registra el contacto
