## MODIFIED Requirements

### Requirement: Reemplazo de nombres propios con exclusion de sectores canonicos

La función `pseudonymize` SHALL reemplazar los nombres propios de personas por la etiqueta `[PERSONA]` (conteo en categoría `persona`), según el patrón heurístico basado en expresiones regulares definido en el diseño. Cuando la frase candidata empiece con un determinante, artículo o posesivo en español (`El`, `La`, `Los`, `Las`, `Un`, `Una`, `Unos`, `Unas`, `Su`, `Sus`, `Este`, `Esta`, `Estos`, `Estas`, `Ese`, `Esa`, `Esos`, `Esas`, `Aquel`, `Aquella`, `Mi`, `Mis`, `Tu`, `Tus`, `Nuestro`, `Nuestra`, `Nuestros`, `Nuestras`), el determinante MUST NOT formar parte del nombre: la heurística SHALL evaluar únicamente el resto de la frase como candidato a persona y SHALL preservar el determinante. Si el resto no es un nombre (una sola palabra capitalizada o un término excluido), la frase completa SHALL preservarse. Si el resto sí es un nombre, se SHALL enmascarar solo el resto. El conjunto de exclusión MUST incluir los cinco nombres canónicos de sector comparados de forma insensible a tildes, de modo que también se preserven variantes acentuadas como `Seguridad Informática`. El sistema SHALL aceptar explícitamente el tradeoff de cobertura del enfoque regex, documentado en `docs/pseudonymization.md`; NO SHALL incorporar NER ni modelos de aprendizaje automático. La corrección MUST NOT debilitar el enmascaramiento de nombres reales: un nombre real en la misma oración se sigue enmascarando.

#### Scenario: Nombre y apellido se reemplazan

- **WHEN** se invoca `pseudonymize("El usuario Juan Pérez reportó el problema", [])`
- **THEN** el resultado contiene `[PERSONA]` y NO contiene `Juan Pérez`

#### Scenario: Las cinco categorías de incidente nunca se pseudonimizan como persona

- **WHEN** se invoca `pseudonymize` sobre un texto que menciona los sectores del dominio `"Seguridad Informatica"`, `"Soporte Tecnico Hardware"`, `"Soporte Tecnico Software"`, `"Bases de Datos"` o `"Sistemas"` sin nombres propios de personas
- **THEN** esas cadenas de sector permanecen intactas y NO son reemplazadas por `[PERSONA]`

#### Scenario: La variante acentuada de un sector canónico se preserva

- **WHEN** se invoca `pseudonymize("Clasificado como Seguridad Informática por el modelo", [])`
- **THEN** el texto conserva `Seguridad Informática`, NO contiene `[PERSONA]` y el conteo `persona` es cero

#### Scenario: Determinante inicial más palabra no-persona se preserva

- **WHEN** se invoca `pseudonymize` sobre textos como `"Su PC se reinicia a cada rato"`, `"La PC no le responde"` o `"El ID del equipo es 42"`
- **THEN** las frases `Su PC`, `La PC` y `El ID` permanecen intactas, NO se inserta `[PERSONA]` y el conteo `persona` es cero

#### Scenario: Un nombre real en la misma oración se sigue enmascarando

- **WHEN** se invoca `pseudonymize("La PC de Juan Pérez no responde", [])`
- **THEN** `La PC` permanece intacta, `Juan Pérez` se reemplaza por `[PERSONA]` y el conteo `persona` es al menos uno

### Requirement: Preservacion de terminos tecnicos, productos y marcas

La función `pseudonymize` SHALL preservar los términos técnicos, nombres de productos, marcas, áreas organizacionales y frases no-persona reconocidas del dominio, de modo que NO sean reemplazados por la etiqueta `[PERSONA]`. La lista SHALL incluir, como mínimo, `Windows Server`, `Active Directory`, `SQL Server`, `Google Chrome`, `Adobe PDF Reader`, `Microsoft Vision`, `NET Framework`, `Recursos Humanos`, `Acceso Denegado`, `San Juan`, `Casa Matriz`, `Rio Negro` y `Cordoba Capital`, con tolerancia a tildes en los topónimos cuando corresponda. La preservación MUST NOT depender del orden de aplicación de los patrones y MUST NOT afectar el reemplazo de nombres propios reales ni de datos personales. Las frases observadas SHALL preservarse por coincidencia de frase completa o por composición de tokens técnicos inequívocos; los tokens ambiguos que puedan formar parte de un nombre real NO SHALL incorporarse a la allowlist por sí solos.

#### Scenario: Producto de infraestructura no se enmascara como persona

- **WHEN** se invoca `pseudonymize("Falla en Windows Server y Active Directory", [])`
- **THEN** el texto resultante conserva `Windows Server` y `Active Directory` y el conteo de la categoría `persona` es cero

#### Scenario: Base de datos y navegador no se enmascaran como persona

- **WHEN** el texto contiene `SQL Server` o `Google Chrome`
- **THEN** esos términos permanecen en el texto y no se cuentan como reemplazos de la categoría `persona`

#### Scenario: Un nombre propio real se sigue enmascarando

- **WHEN** el texto contiene un nombre de persona real junto a términos técnicos preservados
- **THEN** el nombre real se reemplaza por `[PERSONA]` y los términos técnicos se conservan

#### Scenario: Productos y áreas observadas se preservan

- **WHEN** se invoca `pseudonymize("Instalaron Adobe PDF Reader, Microsoft Vision y NET Framework; lo derivó Recursos Humanos", [])`
- **THEN** `Adobe PDF Reader`, `Microsoft Vision`, `NET Framework` y `Recursos Humanos` permanecen intactos, NO se inserta `[PERSONA]` y el conteo `persona` es cero

#### Scenario: Topónimos y frases de error observadas se preservan

- **WHEN** se invoca `pseudonymize("Sucursal San Juan, Casa Matriz, Rio Negro y Cordoba Capital; cartel Acceso Denegado", [])`
- **THEN** `San Juan`, `Casa Matriz`, `Rio Negro`, `Cordoba Capital` y `Acceso Denegado` permanecen intactos, NO se inserta `[PERSONA]` y el conteo `persona` es cero

## ADDED Requirements

### Requirement: Invariante de no regresión de cobertura de PII genuina y equivalencia del corpus publicado

La corrección del sobreenmascaramiento SHALL limitarse a reducir falsos positivos y MUST NOT debilitar la cobertura de PII genuina. Todo nombre propio de persona de dos o más palabras (incluidos tildes y ñ), email, teléfono argentino, host interno y número de tarjeta con disparador contextual SHALL seguir enmascarándose con su etiqueta correspondiente. El archivo publicado `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv` SHALL ser la salida del módulo corregido, NO SHALL contener etiquetas `[PERSONA]` ni `[TELEFONO]` sobre el corpus de la tesis (las nueve observadas eran falsos positivos) y SHALL coincidir con `data/corpus_evaluacion_pseudonimizado.json` en todas las descripciones, ignorando espacios finales. `data/corpus_evaluacion_pseudonimizado.json` MUST NOT modificarse. Ninguna métrica reportada cambia: el corpus evaluado ya es la salida del módulo corregido, por lo que repetir la corrida es un no-op.

#### Scenario: La PII genuina sigue enmascarada

- **WHEN** se invoca `pseudonymize` sobre un texto con un nombre real, un email, un teléfono, un host y una tarjeta con contexto
- **THEN** cada dato se reemplaza por su etiqueta, ningún valor original permanece y los conteos por categoría reflejan cada reemplazo

#### Scenario: El CSV publicado queda sin falsos positivos y coincide con el corpus evaluado

- **WHEN** se regenera `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv` con el módulo corregido
- **THEN** el CSV no contiene ninguna etiqueta `[PERSONA]` ni `[TELEFONO]`, y cada descripción coincide con la del caso homónimo de `data/corpus_evaluacion_pseudonimizado.json` al ignorar espacios finales

#### Scenario: El corpus evaluado y las métricas no cambian

- **WHEN** se compara el corpus evaluado antes y después del change
- **THEN** `data/corpus_evaluacion_pseudonimizado.json` es idéntico y no se requiere una nueva corrida de clasificación para sostener las métricas reportadas