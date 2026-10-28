## MODIFIED Requirements

### Requirement: Sensibilidad de la etapa semantica frente a las reglas de frontera del prompt

El framework SHALL permitir acotar el efecto de las reglas de frontera del prompt sobre los casos que la configuracion evaluada escala a la etapa Gemini (los que no cortocircuita; 69 en el corpus vigente), por niveles: (a) exactitud de esa etapa con y sin los casos motivadores documentados de las reglas, a partir de la cache oficial; (b) comparacion pareada con una corrida historica cuyo prompt anteceda a las reglas, solo si su fecha de generacion es anterior a la propuesta de las reglas; y (c) ablacion controlada en dos brazos, prompt vigente y prompt sin reglas de frontera, sobre los mismos casos y en una misma sesion. La ablacion SHALL invocar al proveedor solo con confirmacion explicita, evaluada antes de construir el clasificador; SHALL usar en el camino pago la credencial real del proveedor resuelta por la configuracion del backend (archivo `App/Backend/.env`) cuando el entorno del proceso no la defina, y MUST NOT inyectar sobre el camino pago un valor inerte que haga fallar la autenticacion; SHALL cargar para cada brazo el prompt que le corresponde ANTES de que cualquier componente del clasificador lo lea, de modo que el SHA-256 del prompt cargado coincida con el esperado para el brazo; SHALL verificar, antes de la primera invocacion, que el SHA-256 del prompt cargado coincide con el esperado para el brazo; SHALL escribir cada brazo en un archivo propio con metadatos de brazo, hash y origen del prompt, modelo, temperatura, version del clasificador, hash del corpus, casos, fecha y cantidad de respuestas de reserva; SHALL contar una respuesta de reserva como error; y MUST NOT escribir las predicciones ni el reporte oficiales. El reporte SHALL presentar cada nivel disponible y declarar los no disponibles.

#### Scenario: Corrida paga sin confirmacion

- **WHEN** se solicita un brazo de la ablacion sin `--confirm-paid` ni la variable de confirmacion
- **THEN** la ejecucion falla con un error de corrida paga no confirmada antes de construir el clasificador real
- **AND** no se realiza ninguna invocacion al proveedor

#### Scenario: Prompt verificado antes de invocar

- **WHEN** el prompt cargado por el backend para un brazo no tiene el SHA-256 esperado para ese brazo
- **THEN** la ejecucion falla antes de la primera invocacion y no escribe ningun archivo de salida

#### Scenario: Brazos sobre los mismos casos y en archivos separados

- **WHEN** se ejecutan ambos brazos con confirmacion
- **THEN** cada brazo clasifica exactamente los casos que la configuracion evaluada no cortocircuita y escribe su propio archivo con los metadatos requeridos
- **AND** `evaluation/predicciones.json` y `evaluation/report.md` no cambian

#### Scenario: Credencial real en el camino pago

- **WHEN** se ejecuta un brazo de la ablacion con confirmacion y el entorno del proceso no define la credencial del proveedor
- **THEN** el clasificador real se construye con la credencial resuelta por la configuracion del backend y no con un valor inerte
- **AND** las invocaciones del brazo llegan al proveedor en lugar de fallar por credencial invalida, de modo que las respuestas de reserva por autenticacion no dominan el brazo

#### Scenario: Cada brazo carga su propio prompt

- **WHEN** se ejecuta un brazo cuya version del prompt difiere de la vigente (por ejemplo, el brazo sin reglas de frontera)
- **THEN** el prompt efectivamente cargado corresponde al del brazo y su SHA-256 coincide con el esperado
- **AND** el estado de importacion previo del paquete del clasificador no congela el prompt vigente de forma que el gate de SHA-256 rechace el brazo

#### Scenario: Comparacion pareada entre brazos

- **WHEN** existen las predicciones de ambos brazos
- **THEN** el reporte declara los aciertos estrictos de cada brazo sobre los mismos casos, las respuestas de reserva contadas como error y el contraste pareado de McNemar
- **AND** si la cache oficial esta disponible, declara tambien la deriva del brazo vigente frente a la corrida oficial

#### Scenario: Version del prompt de una corrida historica

- **WHEN** se evalua el nivel (b) con una corrida historica
- **THEN** su prompt se clasifica como "previa confirmada", "probablemente previa", "posterior" o "indeterminada" segun su fecha de generacion frente a la propuesta y a la aplicacion de las reglas de frontera
- **AND** solo la clase "previa confirmada" habilita el uso del nivel (b) fuera del reporte

## ADDED Requirements

### Requirement: Separacion entre el camino pago y los caminos offline del analisis de sensibilidad

El analisis de sensibilidad SHALL mantener separados el camino pago (corrida autorizada que invoca al proveedor) y los caminos puramente offline (re-medicion deterministica y lectura del punto de operacion). Los caminos offline SHALL completar las variables que exige la configuracion del backend con valores inertes —sin credenciales reales— de modo que nunca invoquen al proveedor y sigan siendo reproducibles sin conexion. La correccion del camino pago MUST NOT depender de que los caminos offline inyecten una credencial ficticia en el entorno del proceso, ni modificar sus resultados. La suite SHALL incluir una prueba que falle si el camino pago vuelve a quedar con un valor inerte en la credencial del proveedor, y una prueba que verifique que los caminos offline siguen operando con valores inertes.

#### Scenario: Los caminos offline siguen inertes y sin red

- **WHEN** se corre la re-medicion offline y la lectura del punto de operacion sin credenciales reales en el entorno
- **THEN** ambas completan sus resultados con valores inertes y no invocan al proveedor
- **AND** la inyeccion de valores inertes no pisa una credencial real ya presente en el entorno

#### Scenario: Prueba de regresion del camino pago

- **WHEN** se modifica el arnes para que el camino pago vuelva a resolver la credencial del proveedor como un valor inerte, o para que el prompt de un brazo se congele antes de fijarse
- **THEN** la suite de `evaluation/` falla
- **AND** la suite incluye una prueba que fija que el prompt de cada brazo se carga antes de que el clasificador lo lea
