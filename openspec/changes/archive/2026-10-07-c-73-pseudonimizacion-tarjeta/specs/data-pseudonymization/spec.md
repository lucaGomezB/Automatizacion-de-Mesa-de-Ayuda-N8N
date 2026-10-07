# Delta for data-pseudonymization

## MODIFIED Requirements

### Requirement: Función de pseudonimización pura con conteo de cobertura

El sistema SHALL exponer una función pura `pseudonymize(text: str, internal_domains: list[str]) -> PseudonymizationResult` en `app/utils/pseudonymizer.py` que reciba una cadena y la lista de dominios internos, y devuelva un resultado con el texto pseudonimizado y el **conteo de reemplazos por categoría** (`email`, `telefono`, `tarjeta`, `host`, `persona`). La función SHALL ser determinística, sin estado y sin efectos secundarios (sin I/O, sin acceso a red ni a base de datos, sin logging): para una misma entrada SHALL producir siempre la misma salida. Las expresiones regulares SHALL estar compiladas a nivel de módulo. El módulo `app/utils/pseudonymizer.py` NO SHALL importar de `app/classifiers/` ni de `app/services/`.

#### Scenario: La pseudonimización es determinística

- **WHEN** se invoca `pseudonymize(text, domains)` dos veces con los mismos `text` y `domains`
- **THEN** ambas invocaciones devuelven exactamente el mismo texto y los mismos conteos, incluyendo la categoría `tarjeta`

#### Scenario: Texto sin datos personales se devuelve sin cambios y con conteos en cero

- **WHEN** se invoca `pseudonymize(text, domains)` con un texto que no contiene emails, teléfonos, tarjetas, hosts ni nombres propios (por ejemplo `"La impresora no imprime y sale papel atascado"`)
- **THEN** el texto devuelto es idéntico al de entrada y todos los conteos por categoría son cero, incluyendo `tarjeta`

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

### Requirement: Auditoría de cobertura sin fuga de PII

El sistema SHALL emitir, en la capa de servicio durante la creación del incidente, un evento de logging de nivel **DEBUG** con el conteo de reemplazos por categoría (`email`, `telefono`, `tarjeta`, `host`, `persona`). Ningún log de nivel INFO SHALL contener el texto original con datos personales, ni emparejar el texto original con su versión pseudonimizada. El módulo de pseudonimización NO SHALL emitir logs.

#### Scenario: El log de cobertura registra conteos sin texto

- **WHEN** se pseudonimiza una descripción al crear un incidente y el nivel DEBUG está habilitado
- **THEN** se emite un evento DEBUG con los conteos de reemplazos por categoría, incluyendo `tarjeta`, y SIN el texto original ni el pseudonimizado completo

#### Scenario: Ningún log INFO expone el texto crudo

- **WHEN** se crea y clasifica un incidente con datos personales y el sistema emite logs de nivel INFO
- **THEN** ningún evento INFO contiene el texto original con PII ni lo empareja con su versión pseudonimizada

## ADDED Requirements

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