# data-pseudonymization Specification

## Purpose
TBD - created by archiving change c-03-pseudonymization-module. Update Purpose after archive.

## Requirements

### Requirement: Función de pseudonimización pura con conteo de cobertura

El sistema SHALL exponer una función pura `pseudonymize(text: str, internal_domains: list[str]) -> PseudonymizationResult` en `app/utils/pseudonymizer.py` que reciba una cadena y la lista de dominios internos, y devuelva un resultado con el texto pseudonimizado y el **conteo de reemplazos por categoría** (`email`, `telefono`, `tarjeta`, `host`, `persona`). La función SHALL ser determinística, sin estado y sin efectos secundarios (sin I/O, sin acceso a red ni a base de datos, sin logging): para una misma entrada SHALL producir siempre la misma salida. Las expresiones regulares SHALL estar compiladas a nivel de módulo. El módulo `app/utils/pseudonymizer.py` NO SHALL importar de `app/classifiers/` ni de `app/services/`.

#### Scenario: La pseudonimización es determinística

- **WHEN** se invoca `pseudonymize(text, domains)` dos veces con los mismos `text` y `domains`
- **THEN** ambas invocaciones devuelven exactamente el mismo texto y los mismos conteos, incluyendo la categoría `tarjeta`

#### Scenario: Texto sin datos personales se devuelve sin cambios y con conteos en cero

- **WHEN** se invoca `pseudonymize(text, domains)` con un texto que no contiene emails, teléfonos, tarjetas, hosts ni nombres propios (por ejemplo `"La impresora no imprime y sale papel atascado"`)
- **THEN** el texto devuelto es idéntico al de entrada y todos los conteos por categoría son cero, incluyendo `tarjeta`

### Requirement: Reemplazo de direcciones de correo electrónico
La función `pseudonymize` SHALL reemplazar toda dirección de correo electrónico por la etiqueta `[EMAIL]` y contar cada reemplazo en la categoría `email`.

#### Scenario: Email simple se reemplaza
- **WHEN** se invoca `pseudonymize("Escribir a juan.perez@empresa.com", [])`
- **THEN** el texto resultante contiene `[EMAIL]`, NO contiene `juan.perez@empresa.com` y el conteo `email` es 1

#### Scenario: Múltiples emails se reemplazan todos
- **WHEN** el texto contiene dos o más direcciones de correo distintas
- **THEN** cada una es reemplazada por `[EMAIL]`, ninguna dirección original permanece y el conteo `email` refleja la cantidad reemplazada

### Requirement: Reemplazo de números telefónicos
La función `pseudonymize` SHALL reemplazar todo número telefónico por la etiqueta `[TELEFONO]` (conteo en categoría `telefono`). El patrón SHALL reconocer formatos argentinos habituales (con o sin prefijo internacional `+54`, con o sin código de área entre paréntesis, con separadores de espacio o guion).

#### Scenario: Teléfono con prefijo internacional se reemplaza
- **WHEN** se invoca `pseudonymize("Llamar al +54 261 555-1234", [])`
- **THEN** el resultado contiene `[TELEFONO]` y NO contiene la secuencia de dígitos del teléfono original

#### Scenario: Teléfono local sin prefijo se reemplaza
- **WHEN** el texto contiene un número telefónico local sin prefijo internacional (por ejemplo `2615551234` o `261 555 1234`)
- **THEN** el número es reemplazado por `[TELEFONO]`

### Requirement: Reemplazo de hosts internos con dominios parametrizados y fallback heurístico
La función `pseudonymize` SHALL reemplazar todo identificador de host interno por la etiqueta `[HOST]` (conteo en categoría `host`). El patrón SHALL reconocer (a) todo host cuyo sufijo de dominio pertenezca a la lista `internal_domains` recibida por parámetro, y (b) como fallback genérico siempre activo, formas habituales de nomenclatura interna: prefijos `srv-*` y `pc-*`, sufijo `*.local` y el literal `localhost`.

#### Scenario: Host con prefijo de servidor se reemplaza por fallback heurístico
- **WHEN** se invoca `pseudonymize("El equipo srv-correo01 no responde", [])`
- **THEN** el resultado contiene `[HOST]` y NO contiene `srv-correo01`

#### Scenario: Host con sufijo `.local` se reemplaza por fallback heurístico
- **WHEN** el texto contiene un nombre de host con sufijo `.local` (por ejemplo `pc-recepcion.local`)
- **THEN** el nombre de host es reemplazado por `[HOST]`

#### Scenario: Host de un dominio corporativo configurado se reemplaza
- **WHEN** se invoca `pseudonymize("Falla en mail.corp.empresa.com", ["corp.empresa.com"])`
- **THEN** el host `mail.corp.empresa.com` es reemplazado por `[HOST]`

#### Scenario: Sin dominios configurados sigue funcionando el fallback
- **WHEN** se invoca `pseudonymize` con `internal_domains` vacío y un texto que contiene `srv-db01` o `localhost`
- **THEN** esos hosts son reemplazados por `[HOST]` aunque no haya dominios configurados

### Requirement: Orden de aplicación de patrones libre de colisiones

La función `pseudonymize` SHALL aplicar los patrones en un orden que evite colisiones. El patrón de tarjeta SHALL aplicarse ANTES que el patrón de teléfono, de modo que la corrida de 16 dígitos de una tarjeta no sea consumida ni parcialmente etiquetada como `[TELEFONO]`. Los patrones de email, tarjeta, teléfono y host SHALL aplicarse ANTES que el de nombres propios, de modo que ningún fragmento ya reemplazado sea re-procesado por un patrón posterior. El resultado SHALL ser estable: ninguna etiqueta ya insertada (`[EMAIL]`, `[TARJETA]`, `[TELEFONO]`, `[HOST]`, `[PERSONA]`) SHALL ser alterada por un patrón aplicado después.

#### Scenario: Email no se fragmenta como nombre propio

- **WHEN** se invoca `pseudonymize` sobre un texto cuyo email contiene un nombre (por ejemplo `juan.perez@empresa.com`)
- **THEN** el email completo se reemplaza por `[EMAIL]` y la porción de nombre embebida NO genera además una etiqueta `[PERSONA]` parcial

#### Scenario: El número de tarjeta no se fragmenta como teléfono

- **WHEN** se invoca `pseudonymize` sobre un texto con contexto de "tarjeta" y una corrida de 16 dígitos (por ejemplo `"mi tarjeta numero 4517 6712 3456 7890 vencio"`)
- **THEN** la corrida completa se reemplaza por `[TARJETA]`, el conteo `telefono` es cero y NO queda ningún dígito de la tarjeta en claro

#### Scenario: Combinación de varias categorías de PII en un texto

- **WHEN** se invoca `pseudonymize` sobre un texto que contiene simultáneamente un nombre propio, un email, un teléfono, un número de tarjeta con contexto y un host
- **THEN** cada elemento se reemplaza por su etiqueta correspondiente, ningún dato personal original permanece, y los conteos por categoría reflejan cada reemplazo

### Requirement: Doble representación de la descripción del incidente
El sistema SHALL almacenar la descripción de cada incidente en DOS representaciones: `descripcion_original` (el texto crudo con datos personales, cifrado at-rest) y `descripcion_pseudonimizada` (el texto con las etiquetas de pseudonimización, en claro). La pseudonimización SHALL ejecutarse en un único punto canónico: la capa de servicio, durante la creación del incidente, ANTES de persistir y ANTES de clasificar. Ambas columnas SHALL poblarse en la misma operación de creación.

#### Scenario: Al crear un incidente se pueblan ambas representaciones
- **WHEN** se crea un incidente cuya descripción contiene datos personales
- **THEN** el registro persistido tiene `descripcion_pseudonimizada` con las etiquetas correspondientes y `descripcion_original` con el texto crudo, ambas pobladas

#### Scenario: La pseudonimización ocurre una sola vez en el servicio
- **WHEN** se crea y clasifica un incidente
- **THEN** la pseudonimización se aplica una única vez en la capa de servicio y el resultado pseudonimizado es el que se pasa al pipeline de clasificación, sin re-pseudonimizar dentro del clasificador

### Requirement: Cifrado at-rest de la descripción original
El sistema SHALL cifrar la columna `descripcion_original` at-rest mediante Fernet (librería `cryptography`), de forma transparente para las capas superiores (un `TypeDecorator` de SQLAlchemy que cifra al escribir y descifra al leer). La clave simétrica SHALL leerse de la configuración (`pseudonymization_encryption_key`, env var `PSEUDONYMIZATION_ENCRYPTION_KEY`) y SHALL ser obligatoria. El cifrado SHALL ser portable entre PostgreSQL y SQLite (el texto cifrado se almacena como texto). El valor almacenado en la base de datos NO SHALL ser legible sin la clave.

#### Scenario: La descripción original se almacena cifrada
- **WHEN** se persiste un incidente con `descripcion_original` conteniendo datos personales
- **THEN** el valor crudo almacenado en la base de datos es texto cifrado ilegible y NO contiene el texto original en claro

#### Scenario: La descripción original se descifra de forma transparente al leer con la clave
- **WHEN** se recupera el incidente a través del ORM con la clave correcta configurada
- **THEN** el atributo `descripcion_original` devuelve el texto original en claro, sin que las capas superiores invoquen explícitamente descifrado

### Requirement: La IA consume únicamente la descripción pseudonimizada
El sistema SHALL pasar al pipeline de clasificación (determinístico y Gemini) ÚNICAMENTE la `descripcion_pseudonimizada`. El texto enviado a la API de Gemini (transferencia internacional) NO SHALL contener datos personales originales. La `descripcion_original` NO SHALL ser transmitida al proveedor externo bajo ninguna ruta.

#### Scenario: Gemini recibe la descripción pseudonimizada
- **WHEN** un incidente cuya descripción contiene datos personales es escalado al clasificador Gemini
- **THEN** el texto enviado a la API de Gemini contiene las etiquetas de pseudonimización y NO contiene los datos personales originales

#### Scenario: La etapa determinística también opera sobre la pseudonimizada
- **WHEN** el clasificador determinístico resuelve el incidente sin escalar a Gemini
- **THEN** opera sobre la `descripcion_pseudonimizada` y no requiere ni accede a la `descripcion_original`

### Requirement: La API expone únicamente la descripción pseudonimizada
El sistema SHALL exponer en los endpoints de la API (detalle, listados, búsquedas, reportes) ÚNICAMENTE la `descripcion_pseudonimizada`. La `descripcion_original` cifrada NO SHALL exponerse en los endpoints normales de la API; su acceso queda restringido a auditoría y fuera del alcance de los contratos REST de este change.

#### Scenario: El detalle de un incidente devuelve la versión pseudonimizada
- **WHEN** un cliente solicita el detalle de un incidente que contenía datos personales
- **THEN** la respuesta incluye la descripción pseudonimizada con etiquetas y NO incluye la descripción original con datos personales

#### Scenario: La descripción original no es accesible por los endpoints normales
- **WHEN** se consume cualquier endpoint REST de incidentes (detalle, listado)
- **THEN** ningún campo de la respuesta contiene el texto original con datos personales

### Requirement: Auditoría de cobertura sin fuga de PII

El sistema SHALL emitir, en la capa de servicio durante la creación del incidente, un evento de logging de nivel **DEBUG** con el conteo de reemplazos por categoría (`email`, `telefono`, `tarjeta`, `host`, `persona`). Ningún log de nivel INFO SHALL contener el texto original con datos personales, ni emparejar el texto original con su versión pseudonimizada. El módulo de pseudonimización NO SHALL emitir logs.

#### Scenario: El log de cobertura registra conteos sin texto

- **WHEN** se pseudonimiza una descripción al crear un incidente y el nivel DEBUG está habilitado
- **THEN** se emite un evento DEBUG con los conteos de reemplazos por categoría, incluyendo `tarjeta`, y SIN el texto original ni el pseudonimizado completo

#### Scenario: Ningún log INFO expone el texto crudo

- **WHEN** se crea y clasifica un incidente con datos personales y el sistema emite logs de nivel INFO
- **THEN** ningún evento INFO contiene el texto original con PII ni lo empareja con su versión pseudonimizada

### Requirement: Reemplazo de nombres propios con exclusion de sectores canonicos
La función `pseudonymize` SHALL reemplazar los nombres propios de personas por la etiqueta `[PERSONA]` (conteo en categoría `persona`), según el patrón heurístico basado en expresiones regulares definido en el diseño. El conjunto de exclusión de personas MUST incluir los cinco nombres canónicos de sector, de modo que nunca se enmascaren como `[PERSONA]`. El sistema SHALL aceptar explícitamente el tradeoff de cobertura del enfoque regex (posibles falsos positivos y falsos negativos sobre nombres en español), documentado en `docs/pseudonymization.md`; NO SHALL incorporar NER ni modelos de aprendizaje automático.

#### Scenario: Nombre y apellido se reemplazan
- **WHEN** se invoca `pseudonymize("El usuario Juan Pérez reportó el problema", [])`
- **THEN** el resultado contiene `[PERSONA]` y NO contiene `Juan Pérez`

#### Scenario: Las cinco categorías de incidente nunca se pseudonimizan como persona
- **WHEN** se invoca `pseudonymize` sobre un texto que menciona los sectores del dominio `"Seguridad Informatica"`, `"Soporte Tecnico Hardware"`, `"Soporte Tecnico Software"`, `"Bases de Datos"` o `"Sistemas"` sin nombres propios de personas
- **THEN** esas cadenas de sector permanecen intactas y NO son reemplazadas por `[PERSONA]`

### Requirement: Preservacion de terminos tecnicos, productos y marcas

La función `pseudonymize` SHALL preservar los terminos tecnicos, nombres de productos y marcas reconocidas del dominio (por ejemplo `Windows Server`, `Active Directory`, `SQL Server`, `Google Chrome`), de modo que NO sean reemplazados por la etiqueta `[PERSONA]`. La preservacion MUST NOT depender del orden de aplicacion de los patrones y MUST NOT afectar el reemplazo de nombres propios reales ni de datos personales.

#### Scenario: Producto de infraestructura no se enmascara como persona

- **WHEN** se invoca `pseudonymize("Falla en Windows Server y Active Directory", [])`
- **THEN** el texto resultante conserva `Windows Server` y `Active Directory` y el conteo de la categoría `persona` es cero

#### Scenario: Base de datos y navegador no se enmascaran como persona

- **WHEN** el texto contiene `SQL Server` o `Google Chrome`
- **THEN** esos terminos permanecen en el texto y no se cuentan como reemplazos de la categoría `persona`

#### Scenario: Un nombre propio real se sigue enmascarando

- **WHEN** el texto contiene un nombre de persona real junto a terminos tecnicos preservados
- **THEN** el nombre real se reemplaza por `[PERSONA]` y los terminos tecnicos se conservan

### Requirement: El texto crudo de telefonía nunca transita el borde de N8N

El sistema SHALL pseudonimizar el transcript de telefonía INMEDIATAMENTE después de obtenerlo y ANTES de cualquier entrega a n8n. La única representación del texto que cruce el borde hacia n8n SHALL ser la pseudonimizada. El transcript crudo MUST NOT transmitirse a n8n bajo ninguna ruta ni incluirse en el payload del handoff.

#### Scenario: El handoff lleva solo texto pseudonimizado

- **WHEN** el backend entrega el ingreso telefónico a n8n
- **THEN** el texto entregado contiene las etiquetas de pseudonimización y no contiene PII en claro

#### Scenario: El transcript crudo no cruza el borde

- **WHEN** se inspecciona el payload que el backend envía a n8n
- **THEN** no contiene el transcript original con datos personales

### Requirement: La IA de N8N consume únicamente la descripción pseudonimizada de telefonía

El sistema SHALL garantizar que el `AI Agent` del canal de telefonía reciba como entrada ÚNICAMENTE la descripción pseudonimizada. El prompt del agente MUST NOT interpolar un transcript crudo. El texto enviado al proveedor de inferencia desde n8n NO SHALL contener datos personales originales de la llamada. Esta regla corrige la fuga latente de la ruta previa, donde el prompt interpolaba el transcript crudo antes de cualquier pseudonimización.

#### Scenario: El prompt del agente no interpola transcript crudo

- **WHEN** se inspecciona la entrada del `AI Agent` en el canal de telefonía
- **THEN** el texto interpolado en el prompt es la descripción pseudonimizada y no un transcript crudo

#### Scenario: La inferencia externa no recibe PII original

- **WHEN** el `AI Agent` invoca al proveedor de inferencia para un incidente telefónico
- **THEN** el contenido enviado contiene las etiquetas de pseudonimización y no los datos personales originales

### Requirement: Reemplazo de números de tarjeta con disparador contextual

La función `pseudonymize` SHALL reemplazar por la etiqueta `[TARJETA]` (conteo en categoría `tarjeta`) las corridas de 16 dígitos que representan números de tarjeta, en dos formas: agrupada 4-4-4-4 con separadores de espacio o guion, y contigua de 16 dígitos. La detección SHALL ser CONTEXTUAL: SHALL activarse únicamente cuando exista una mención de `tarjeta` o `tarjetas` (case-insensitive) y el número aparezca dentro de una ventana de proximidad de 40 caracteres DESPUÉS del disparador. La etiqueta SHALL ser exactamente `[TARJETA]` en mayúsculas, consistente con las categorías existentes. La ventana SHALL ser una constante a nivel de módulo. La regla NO SHALL validar Luhn ni reconocer longitudes distintas de 16 dígitos. La función permanece PURA: sin I/O, sin acceso a settings ni logging.

#### Scenario: Tarjeta agrupada con espacios se reemplaza

- **WHEN** se invoca `pseudonymize("mi tarjeta numero 4517 6712 3456 7890 vencio", [])`
- **THEN** el resultado contiene `[TARJETA]`, NO contiene `4517 6712 3456 7890` ni ningún remanente de sus dígitos, y el conteo `tarjeta` es 1

#### Scenario: Tarjeta agrupada con guiones se reemplaza

- **WHEN** el texto contiene una mención de "tarjeta" seguida de un número agrupado con guiones (por ejemplo `"4517-6712-3456-7890"`)
- **THEN** el número se reemplaza por `[TARJETA]` y el conteo `tarjeta` es 1

#### Scenario: Tarjeta contigua de 16 dígitos se reemplaza

- **WHEN** se invoca `pseudonymize("Hola, mi tarjeta es 0102301239999320 y no puedo operar", [])`
- **THEN** el resultado contiene `[TARJETA]`, NO contiene `0102301239999320` ni sus dígitos, y el conteo `tarjeta` es 1

#### Scenario: La etiqueta es exactamente [TARJETA] en mayúsculas

- **WHEN** se pseudonimiza cualquier número de tarjeta con contexto
- **THEN** la etiqueta insertada es exactamente `[TARJETA]` (mayúsculas), sin variantes como `[Tarjeta]` ni `[TARJETA]` con otro formato

#### Scenario: Variantes de disparador activan la regla

- **WHEN** el texto contiene `"tarjeta de credito"`, `"tarjeta de debito"`, `"numero de tarjeta"` o el plural `"tarjetas"` seguido de un número de 16 dígitos dentro de la ventana
- **THEN** el número se reemplaza por `[TARJETA]` y el conteo `tarjeta` se incrementa por cada reemplazo

#### Scenario: Un número de 16 dígitos fuera de la ventana no se enmascara

- **WHEN** el texto menciona "tarjeta" y luego, a más de 40 caracteres de distancia, aparece una corrida de 16 dígitos sin nueva mención de "tarjeta"
- **THEN** esa corrida NO se reemplaza por `[TARJETA]` y el conteo `tarjeta` es cero

#### Scenario: Un número de 16 dígitos sin mención de tarjeta no se enmascara

- **WHEN** el texto contiene una corrida de 16 dígitos pero ninguna mención de "tarjeta" o "tarjetas"
- **THEN** la regla de tarjeta no se activa y el conteo `tarjeta` es cero

### Requirement: No regresión de corridas de dígitos sin contexto de tarjeta

La incorporación de la categoría `[TARJETA]` NO SHALL alterar el tratamiento de corridas de dígitos que no tienen contexto de tarjeta. En particular, la corrida de dígitos del nombre de DLL del caso R067 (`axm0102301239999320002302`, canal WEB, sin la palabra "tarjeta") NO SHALL clasificarse como `[TARJETA]` ni incrementar el conteo `tarjeta`. La mención de "tarjeta" sin dígitos asociados (caso R169) NO SHALL modificar el texto ni los conteos.

#### Scenario: El identificador de DLL de R067 no se clasifica como tarjeta

- **WHEN** se invoca `pseudonymize` sobre el texto de R067 `"Le sale un cartel \"Falta el dll axm0102301239999320002302\" al intentar iniciar el sistema principal"` con dominios vacíos
- **THEN** el resultado NO contiene `[TARJETA]` y el conteo `tarjeta` es cero

#### Scenario: La mención de tarjeta sin dígitos no altera el texto

- **WHEN** se invoca `pseudonymize("Tiene problemas al dar de alta una tarjeta", [])` (caso R169)
- **THEN** el texto resultante es idéntico al de entrada, el conteo `tarjeta` es cero y no se inserta ninguna etiqueta de tarjeta
