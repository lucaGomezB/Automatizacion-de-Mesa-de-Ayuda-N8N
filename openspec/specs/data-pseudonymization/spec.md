# data-pseudonymization Specification

## Purpose
TBD - created by archiving change c-03-pseudonymization-module. Update Purpose after archive.
## Requirements
### Requirement: Función de pseudonimización pura con conteo de cobertura
El sistema SHALL exponer una función pura `pseudonymize(text: str, internal_domains: list[str]) -> PseudonymizationResult` en `app/utils/pseudonymizer.py` que reciba una cadena y la lista de dominios internos, y devuelva un resultado con el texto pseudonimizado y el **conteo de reemplazos por categoría** (`email`, `telefono`, `host`, `persona`). La función SHALL ser determinística, sin estado y sin efectos secundarios (sin I/O, sin acceso a red ni a base de datos, sin logging): para una misma entrada SHALL producir siempre la misma salida. Las expresiones regulares SHALL estar compiladas a nivel de módulo. El módulo `app/utils/pseudonymizer.py` NO SHALL importar de `app/classifiers/` ni de `app/services/`.

#### Scenario: La pseudonimización es determinística
- **WHEN** se invoca `pseudonymize(text, domains)` dos veces con los mismos `text` y `domains`
- **THEN** ambas invocaciones devuelven exactamente el mismo texto y los mismos conteos

#### Scenario: Texto sin datos personales se devuelve sin cambios y con conteos en cero
- **WHEN** se invoca `pseudonymize(text, domains)` con un texto que no contiene emails, teléfonos, hosts ni nombres propios (por ejemplo `"La impresora no imprime y sale papel atascado"`)
- **THEN** el texto devuelto es idéntico al de entrada y todos los conteos por categoría son cero

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

### Requirement: Reemplazo de nombres propios
La función `pseudonymize` SHALL reemplazar los nombres propios de personas por la etiqueta `[PERSONA]` (conteo en categoría `persona`), según el patrón heurístico basado en expresiones regulares definido en el diseño. El sistema SHALL aceptar explícitamente el tradeoff de cobertura del enfoque regex (posibles falsos positivos y falsos negativos sobre nombres en español), documentado en `docs/pseudonymization.md`; NO SHALL incorporar NER ni modelos de aprendizaje automático.

#### Scenario: Nombre y apellido se reemplazan
- **WHEN** se invoca `pseudonymize("El usuario Juan Pérez reportó el problema", [])`
- **THEN** el resultado contiene `[PERSONA]` y NO contiene `Juan Pérez`

#### Scenario: Las tres categorías de incidente nunca se pseudonimizan como persona
- **WHEN** se invoca `pseudonymize` sobre un texto que menciona las categorías del dominio `"Sistemas"`, `"Operaciones"` o `"Soporte Técnico"` sin nombres propios de personas
- **THEN** esas cadenas de categoría permanecen intactas y NO son reemplazadas por `[PERSONA]`

### Requirement: Orden de aplicación de patrones libre de colisiones
La función `pseudonymize` SHALL aplicar los patrones en un orden que evite colisiones: los patrones de email, teléfono y host SHALL aplicarse ANTES que el de nombres propios, de modo que ningún fragmento ya reemplazado sea re-procesado por un patrón posterior. El resultado SHALL ser estable: ninguna etiqueta ya insertada (`[EMAIL]`, `[TELEFONO]`, `[HOST]`, `[PERSONA]`) SHALL ser alterada por un patrón aplicado después.

#### Scenario: Email no se fragmenta como nombre propio
- **WHEN** se invoca `pseudonymize` sobre un texto cuyo email contiene un nombre (por ejemplo `juan.perez@empresa.com`)
- **THEN** el email completo se reemplaza por `[EMAIL]` y la porción de nombre embebida NO genera además una etiqueta `[PERSONA]` parcial

#### Scenario: Combinación de varias categorías de PII en un texto
- **WHEN** se invoca `pseudonymize` sobre un texto que contiene simultáneamente un nombre propio, un email, un teléfono y un host
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
El sistema SHALL emitir, en la capa de servicio durante la creación del incidente, un evento de logging de nivel **DEBUG** con el conteo de reemplazos por categoría (`email`, `telefono`, `host`, `persona`). Ningún log de nivel INFO SHALL contener el texto original con datos personales, ni emparejar el texto original con su versión pseudonimizada. El módulo de pseudonimización NO SHALL emitir logs.

#### Scenario: El log de cobertura registra conteos sin texto
- **WHEN** se pseudonimiza una descripción al crear un incidente y el nivel DEBUG está habilitado
- **THEN** se emite un evento DEBUG con los conteos de reemplazos por categoría y SIN el texto original ni el pseudonimizado completo

#### Scenario: Ningún log INFO expone el texto crudo
- **WHEN** se crea y clasifica un incidente con datos personales y el sistema emite logs de nivel INFO
- **THEN** ningún evento INFO contiene el texto original con PII ni lo empareja con su versión pseudonimizada

