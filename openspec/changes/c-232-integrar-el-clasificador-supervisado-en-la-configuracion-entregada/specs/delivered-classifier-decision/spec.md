## Purpose

Define el contraste pareado cabeza a cabeza del modelo supervisado integrado contra el
clasificador hibrido vigente sobre el corpus probabilistico acreditado con referencia por
mayoria, la regla de decision pre-registrada y acreditada (reemplazar la etapa semantica,
complementar el hibrido o conservarlo) y las compuertas de procedencia y etica que preceden
al contraste, con veredicto honesto que incluye la salida «no supera».

## ADDED Requirements

### Requirement: DCD-001 — Contraste pareado cabeza a cabeza sobre el corpus probabilistico acreditado

El analisis SHALL calcular el contraste solo sobre el corpus probabilistico acreditado de
`c-229` con la referencia por mayoria de `c-230`, sobre los **mismos casos emparejados** por
`caso_id`: por cada sistema (modelo supervisado integrado e hibrido vigente), la exactitud
estricta y laxa, el macro-F1 y las metricas por clase con soporte; y la **diferencia pareada**
de la exactitud estricta con su intervalo de confianza del 95 % por bootstrap percentil de
semilla fija y la prueba de McNemar, reutilizando `evaluation/metrics.py` y
`evaluation/stats.py`, con la estimacion referida al universo del estimador de `c-229`. El
analisis SHALL incluir todos los casos; los subconjuntos que use la regla SHALL estar
pre-especificados en ella y MUST NOT elegirse ni reintentarse casos despues de ver
resultados. El corpus de 200 casos MUST NOT usarse como conjunto de contraste, porque el
hibrido se ajusto con el, y el analisis MUST NOT usar como ancla, insumo o comparador ninguna
cifra ni artefacto retirado por `c-235`. Antes de comparar, el analisis SHALL verificar los
SHA-256 de las entradas declarados en la regla pre-registrada y MUST terminar con error sin
escribir si no coinciden o si algun caso carece de prediccion en alguno de los sistemas. El
analisis SHALL ser determinista byte a byte, de solo lectura y MUST NOT usar red.

#### Scenario: Tabla pareada con IC y McNemar

- **WHEN** se ejecuta el contraste sobre el corpus probabilistico acreditado
- **THEN** figuran por sistema la exactitud estricta y laxa, el macro-F1 y las metricas por clase con soporte
- **AND** se informa la diferencia pareada de la exactitud estricta con su intervalo y la prueba de McNemar

#### Scenario: Sin conjunto de contraste alternativo

- **WHEN** el corpus probabilistico acreditado no existe
- **THEN** el contraste no se ejecuta y se registra el bloqueo
- **AND** no se sustituye por el corpus de 200 casos ni por material retirado

#### Scenario: Entradas distintas de las pre-registradas

- **WHEN** el SHA-256 de alguna entrada difiere del declarado en la regla pre-registrada
- **THEN** el analisis termina con error sin escribir salidas

#### Scenario: Caso sin pareja

- **WHEN** un `caso_id` del corpus no tiene prediccion en alguno de los sistemas
- **THEN** el analisis termina con error y no escribe artefactos

### Requirement: DCD-002 — Regla de decision pre-registrada, acreditada ante el director, y veredicto honesto

Antes de obtener las predicciones sobre el corpus acreditado, el change SHALL registrar y
versionar una **regla de decision pre-registrada** con tres salidas mutuamente exclusivas y
exhaustivas, evaluadas sobre la diferencia pareada (modelo supervisado menos hibrido):
**reemplazar** la etapa semantica, **complementar** el hibrido (segunda opinion o senal de
gate) o **conservar** el hibrido. La regla SHALL incluir umbrales, margen de macro-F1,
subconjuntos pre-especificados, correccion por comparaciones multiples y los SHA-256 de las
entradas previstas. Como la fecha de un commit la controlan los autores, el pre-registro
SHALL acreditarse ademas con una constancia entregada al director antes de medir (con el
SHA-256 del documento de la regla), que queda en su custodia y cuya fecha se registra; sin
esa constancia el contraste MUST NOT ejecutarse. El veredicto SHALL ser exactamente uno de
los tres, con su evidencia y su intervalo, y SHALL informarse honestamente, **incluida la
salida «no supera»**. La regla MUST NOT redefinirse despues de observar el resultado. El
clasificador entregado por defecto SHALL cambiar solo si el veredicto es **reemplazar**; en
cualquier otro caso el hibrido SHALL permanecer como clasificador entregado.

#### Scenario: Regla acreditada antes de medir

- **WHEN** se inicia el contraste
- **THEN** existe una regla versionada con las tres salidas, sus umbrales y los hashes de entrada
- **AND** consta la constancia entregada al director con fecha anterior a la obtencion de las predicciones

#### Scenario: Veredicto unico y honesto

- **WHEN** se emite el veredicto
- **THEN** es exactamente uno de reemplazar, complementar o conservar, con su evidencia y su intervalo
- **AND** el veredicto «no supera al hibrido» se informa como resultado valido y no se oculta

#### Scenario: Default solo cambia al reemplazar

- **WHEN** el veredicto es complementar o conservar
- **THEN** el clasificador entregado por defecto sigue siendo el hibrido
- **AND** el modelo supervisado queda disponible sin reemplazar la etapa semantica

#### Scenario: Complemento sin reemplazo

- **WHEN** el veredicto es complementar
- **THEN** el modelo se integra como segunda opinion o senal de gate sobre un subconjunto pre-especificado
- **AND** no reemplaza la etapa semantica del hibrido

### Requirement: DCD-003 — Compuertas de procedencia y etica y legal previas al contraste

El contraste MUST NOT ejecutarse sin verificar que constan cerradas, para el corpus y la
referencia que se consumen, la compuerta de procedencia (registro crudo exportado del sistema
con sus marcas temporales originales, constancia de la organizacion en custodia del director,
SHA-256 del export en el repositorio, ningun texto redactado por los autores ni generado o
asistido por IA presentado como real, y verificacion del director antes del analisis) y la
compuerta etica y legal (autorizacion institucional escrita, base de licitud bajo la Ley
25.326 y consentimiento). Las predicciones del hibrido SHALL tomarse de las registradas en
operacion con su version o, si deben generarse, la corrida que envia textos a la Gemini API
SHALL ejecutarse solo si la autorizacion cubre expresamente ese envio, y SHALL declararse
(cantidad de textos, fecha y modelo). Los fixtures sinteticos SHALL rotularse como tales en el
nombre del archivo, en la cabecera y en toda salida.

#### Scenario: Compuerta abierta bloquea el contraste

- **WHEN** alguna compuerta del corpus o de la referencia no consta cerrada
- **THEN** el contraste no se ejecuta
- **AND** el bloqueo se registra

#### Scenario: Envio a la Gemini API sin autorizacion expresa

- **WHEN** las predicciones del hibrido requieren una corrida nueva y la autorizacion no cubre ese envio
- **THEN** la corrida no se ejecuta y el contraste queda bloqueado

#### Scenario: Envio autorizado declarado

- **WHEN** se ejecuta una corrida autorizada contra la Gemini API
- **THEN** se registran la cantidad de textos enviados, la fecha y el modelo
