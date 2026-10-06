# Delta for n8n-workflow

## MODIFIED Requirements

### Requirement: Validación de la respuesta de clasificación según Anexo H §H.3

La clasificacion persistida del incidente SHALL provenir del backend, que valida su propia cascada conforme al contrato de resultado. Si el workflow conserva una validacion de una salida reducida de un modelo para un sub-caso (OQ1), esa validacion SHALL aplicar, en orden, los pasos del Anexo H §H.3: (1) parseo JSON válido; (2) presencia de los campos `sector_predicho` y `confianza`; (3) `sector_predicho` exactamente en `{"Seguridad Informatica", "Soporte Tecnico Hardware", "Soporte Tecnico Software", "Bases de Datos", "Sistemas"}` (case-sensitive, sin tildes); (4) `confianza` numérica en el rango `[0.0, 1.0]`; (5) si el campo `sectores_adicionales` está presente, cada uno de sus valores MUST pertenecer al mismo conjunto canónico. Ante el fallo de cualquier paso, SHALL registrar el error, fijar `confianza = 0.0` y marcar el incidente para revisión humana, sin propagar estados inconsistentes. La salida validada de un modelo reducido MUST NOT determinar el sector persistido del incidente.

#### Scenario: Respuesta válida aceptada

- **WHEN** la validación recibe `{"sector_predicho": "Soporte Tecnico Software", "confianza": 0.95, "sectores_adicionales": ["Bases de Datos"]}`
- **THEN** la marca como válida y conserva el sector predicho, los sectores adicionales y la confianza para el ruteo por umbral, sin que esa salida determine el sector persistido

#### Scenario: Categoría fuera del conjunto permitido

- **WHEN** la validación recibe una respuesta con `sector_predicho` igual a `"operaciones"` (minúscula), `"Operaciones"` o cualquier valor fuera del conjunto exacto
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: Sector adicional inválido

- **WHEN** la validación recibe un `sectores_adicionales` con un valor fuera del conjunto canónico
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: JSON malformado

- **WHEN** la validación recibe un texto que no parsea como JSON
- **THEN** registra el error, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: Confianza fuera de rango

- **WHEN** la validación recibe una `confianza` igual a `1.5` o no numérica
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

### Requirement: Ruteo por umbral de confianza

El gate de revision humana del workflow SHALL ser de dos capas y NO SHALL evaluar la confianza del modelo antes de persistir el incidente.

La primera capa es el nodo `if` pre-POST `Entrada valida`, que es una validación de ENTRADA y no una compuerta de confianza: para los TRES canales (correo, web y telefonía) SHALL verificar la validez y longitud del texto de la descripción pseudonimizada. Para el canal telefonía el nodo MUST NOT evaluar una clasificación producida por un modelo de n8n, porque la clasificación la resuelve el backend. Su condición SHALL ser `confianza >= 0.70 OR revision_forzada == true`, de modo que una entrada con revisión forzada por el tope de refinamiento del agente se persista aunque su confianza sea `0.0`. Cuando la condición es verdadera el flujo SHALL continuar hacia la persistencia; cuando es falsa SHALL derivar a revisión humana.

La segunda capa es el nodo `if` post-POST `Requiere revision humana`, que SHALL evaluar el flag `requiere_revision_humana` devuelto por el backend en la respuesta de `POST /api/v1/incidentes/`. El backend SHALL fijar `requiere_revision_humana = confianza < 0.70` y la respuesta del POST NO SHALL incluir el campo `confianza`; por eso el gate post-POST SHALL leer el flag y NO SHALL intentar leer `confianza` del response. Cuando el flag es verdadero el flujo SHALL notificar al operador designado y registrar auditoría; cuando es falso SHALL continuar con las confirmaciones por canal. Las condiciones de los nodos `if` NO SHALL quedar vacías.

#### Scenario: Confianza por encima del umbral crea el incidente

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.85`
- **THEN** la condición `confianza >= 0.70 OR revision_forzada == true` es verdadera y el flujo rutea hacia la persistencia del incidente

#### Scenario: Confianza por debajo del umbral deriva a revisión humana

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.60` y `revision_forzada = false`
- **THEN** la condición es falsa y el flujo deriva a revisión humana

#### Scenario: Entrada valida acepta revisión forzada aun con confianza baja

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.0` y `revision_forzada = true`
- **THEN** la condición es verdadera por la rama `revision_forzada == true` y el flujo rutea hacia la persistencia

#### Scenario: Telefono valida su entrada como los demas canales

- **WHEN** el nodo `if` pre-POST `Entrada valida` procesa una entrada del canal telefonía
- **THEN** verifica la validez y longitud de la descripción pseudonimizada y NO evalúa una clasificación producida por un modelo de n8n

#### Scenario: Confianza en el límite exacto

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.70` y `revision_forzada = false`
- **THEN** la condición `confianza >= 0.70` es verdadera y el flujo rutea hacia la persistencia (el umbral es inclusivo)

#### Scenario: El gate post-POST lee el flag del backend

- **WHEN** el nodo `if` post-POST `Requiere revision humana` evalúa la respuesta de `POST /api/v1/incidentes/`
- **THEN** su condición evalúa el campo `requiere_revision_humana` del response y NO referencia el campo `confianza`, que el response no incluye

#### Scenario: Flag verdadero deriva a notificación y auditoría

- **WHEN** la respuesta del backend tiene `requiere_revision_humana = true` (confianza por debajo de `0.70`)
- **THEN** el flujo notifica al operador designado y registra la ejecución en auditoría

#### Scenario: Flag falso continúa con las confirmaciones

- **WHEN** la respuesta del backend tiene `requiere_revision_humana = false` (confianza en o por encima de `0.70`)
- **THEN** el flujo rutea por canal de origen y continúa con las confirmaciones sin notificar al operador

### Requirement: N8N-REFINE-001 — Tope de refinamiento del agente pago

El canal telefonico MUST NOT depender del `AI Agent` para clasificar el incidente: la clasificacion la resuelve el backend. Si el workflow conserva una invocacion reducida del agente para un sub-caso (OQ1), el numero de intentos de clasificacion/refinamiento del agente SHALL quedar acotado a un maximo explicito (por ejemplo 2), los intentos pagos por incidente SHALL quedar acotados por el producto entre intentos de transporte y de refinamiento, y su salida MUST NOT determinar el sector persistido. Al agotarse cualquier tope sin una clasificacion valida, el flujo SHALL derivar el incidente a un nodo terminal que lo persiste con `requiere_revision_humana=true` y `confianza=0.0`, y MUST NOT reinvocar indefinidamente al proveedor pago. Si la invocacion reducida existe, SHALL declarar un reintento acotado ante fallas transitorias del modelo (`retryOnFail` verdadero, con `maxTries` y `waitBetweenTries` explicitos). Los reintentos de transporte y los refinamientos por respuesta invalida son mecanismos distintos.

#### Scenario: Un fallo dentro del tope reintenta una vez

- **WHEN** la validacion de la salida del agente reducido falla en el primer intento y el tope aun no se agoto
- **THEN** el flujo reingresa al `AI Agent` para un unico intento adicional

#### Scenario: Al agotar el tope no se reinvoca al agente pago

- **WHEN** el refinamiento alcanza el tope sin una salida valida
- **THEN** el flujo NO reingresa al `AI Agent`, persiste el incidente con `requiere_revision_humana=true` y termina, con el sector resuelto por el backend

#### Scenario: Clasificacion valida dentro del tope sigue el flujo normal

- **WHEN** el agente reducido produce una salida valida dentro del tope
- **THEN** el flujo continua hacia la normalizacion y el ruteo por umbral, sin que esa salida determine el sector persistido

#### Scenario: El tope es verificable en el workflow exportado

- **WHEN** la suite estructural inspecciona el nodo `AI Agent` y sus conexiones de refinamiento
- **THEN** existe un tope explicito de intentos (por ejemplo `maxIterations` o un contador) y una ruta terminal que no reinvoca al agente

#### Scenario: Una falla transitoria del modelo se reintenta sin consumir refinamiento

- **WHEN** el modelo de lenguaje del agente reducido falla de forma transitoria en el primer intento de transporte
- **THEN** el workflow reintenta la invocacion del agente segun su `maxTries` declarado, y ese reintento de transporte no cuenta como intento de refinamiento por respuesta invalida

#### Scenario: El reintento de transporte esta acotado y es explicito

- **WHEN** la suite estructural inspecciona el nodo `AI Agent`
- **THEN** el nodo declara `retryOnFail` verdadero con `maxTries` y `waitBetweenTries` numericos y acotados, de modo que el peor caso de invocaciones pagas por incidente es finito y verificable

## REMOVED Requirements

### Requirement: N8N-INTAKE-001 — El POST al backend envia Message-ID, clasificacion precalculada y origen

**Reason**: La clasificacion precalculada de telefonia se elimina; el backend clasifica todos los canales y el POST deja de transportar una clasificacion que pudiera omitir la cascada.
**Migration**: El POST sigue enviando la descripcion, el canal, el `Message-ID` de correo y el marcador de origen bajo un contrato nuevo. La clasificacion la resuelve el backend. Ver N8N-INTAKE-002 y N8N-UNIFY-001.

## ADDED Requirements

### Requirement: N8N-INTAKE-002 — El POST al backend envia origen y no una clasificacion precalculada de telefonia

El nodo HTTP de persistencia SHALL enviar al backend la descripción pseudonimizada, el canal, el `Message-ID` del mensaje IMAP cuando el canal sea correo, y un marcador explícito de origen/evento. Para el canal telefonía el nodo MUST NOT enviar una `clasificacion` precalculada, porque la clasificación la resuelve el backend con su cascada. El workflow MUST NOT descartar el `Message-ID` ni el marcador de origen.

#### Scenario: El POST telefonico NO incluye clasificacion precalculada

- **WHEN** un incidente telefonico llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend NO incluye el sector predicho ni la confianza producidos fuera del backend

#### Scenario: El POST de correo incluye el Message-ID de origen

- **WHEN** un incidente del canal correo llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend incluye el `origen_message_id` tomado del mensaje IMAP

#### Scenario: El marcador de origen es explicito

- **WHEN** se inspecciona el cuerpo que el nodo HTTP envia al backend
- **THEN** contiene un marcador explicito de origen/evento que identifica al canal emisor

### Requirement: N8N-UNIFY-001 — La clasificacion del incidente pertenece al backend

El workflow de n8n MUST NOT ser el camino de clasificacion del incidente en ningun canal. La clasificacion persistida de los tres canales SHALL provenir de la cascada del backend sobre la descripcion pseudonimizada. Cualquier clasificacion producida dentro de n8n MUST NOT persistirse como la clasificacion del incidente ni omitir la cascada del backend. El canal telefonico MUST NOT enviar una clasificacion precalculada que el backend pueda usar para saltear su cascada.

#### Scenario: Los tres canales clasifican en el backend

- **WHEN** un incidente de cualquier canal (correo, web o telefonia) se persiste
- **THEN** su sector proviene de la cascada del backend, no de n8n

#### Scenario: n8n no saltea la cascada

- **WHEN** se inspecciona el cuerpo que n8n envia al backend para un incidente telefonico
- **THEN** no contiene una clasificacion precalculada que el backend pudiera usar para omitir la cascada
