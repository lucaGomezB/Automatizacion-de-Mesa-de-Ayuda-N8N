## Purpose

Define el contraste pareado cabeza a cabeza del modelo supervisado integrado contra el
clasificador hibrido vigente y la regla de decision pre-registrada (reemplazar la etapa
semantica, complementar el hibrido o conservarlo), con veredicto honesto que incluye la
salida «no supera».

## ADDED Requirements

### Requirement: DCD-001 — Contraste pareado cabeza a cabeza contra el hibrido vigente

El analisis SHALL calcular, sobre los **mismos casos emparejados** por `caso_id`, la exactitud
estricta y laxa, el macro-F1 y las metricas por clase con soporte por cada sistema (el modelo
supervisado integrado y el clasificador hibrido vigente), y la **diferencia pareada** de la
exactitud estricta con su intervalo de confianza del 95 % por bootstrap percentil de semilla
fija y la prueba de McNemar, reutilizando las funciones puras de `evaluation/metrics.py` y
`evaluation/stats.py`. El contraste SHALL reportarse sobre la referencia retenida (los `206`
casos y los subconjuntos alineados que la tesis informa por separado) y sobre el corpus fresco
de prevalencia natural de `c-229`, que sera la lectura primaria. Antes de escribir salidas, el
analisis SHALL reproducir los anclajes canonicos (`142/206` de exactitud estricta y macro-F1
`0,7024` sobre la referencia vigente) y MUST terminar con error sin escribir archivos si no
los reproduce. El analisis SHALL ser determinista byte a byte, de solo lectura, MUST NOT usar
red ni Gemini, y SHALL abortar si algun caso carece de prediccion en alguno de los sistemas.
Toda lectura sobre los `206` SHALL rotularse como contraste descriptivo y SHALL declarar que el
umbral `0,85` no es alcanzable sobre esa referencia.

#### Scenario: Tabla pareada con IC y McNemar

- **WHEN** se ejecuta el contraste sobre los casos pareados de la referencia retenida
- **THEN** figuran por sistema la exactitud estricta y laxa, el macro-F1 y las metricas por clase con soporte
- **AND** se informa la diferencia pareada de la exactitud estricta con su intervalo y la prueba de McNemar

#### Scenario: Lectura primaria sobre prevalencia natural

- **WHEN** se ejecuta el contraste sobre el corpus de `c-229`
- **THEN** el resultado distingue la lectura del modelo supervisado de la del hibrido sobre el mismo corpus
- **AND** la lectura de prevalencia natural se rotula como primaria y cada comparacion queda rotulada

#### Scenario: Anclajes reproducidos antes de escribir

- **WHEN** el analisis lee las predicciones y la referencia congeladas
- **THEN** reproduce `142/206` y macro-F1 `0,7024` sobre la referencia vigente antes de cualquier comparacion
- **AND** si no los reproduce, termina con error sin escribir salidas

#### Scenario: Caso sin pareja

- **WHEN** un `caso_id` de la referencia no tiene prediccion en alguno de los sistemas
- **THEN** el analisis termina con error y no escribe artefactos

#### Scenario: No alcanzabilidad declarada sobre los 206

- **WHEN** se lee el contraste sobre los `206`
- **THEN** se declara que el umbral `0,85` no es alcanzable sobre esa referencia
- **AND** la lectura no se presenta como validacion del modelo supervisado

### Requirement: DCD-002 — Regla de decision pre-registrada y veredicto honesto

Antes de ejecutar el contraste, el change SHALL registrar y versionar una **regla de decision
pre-registrada** con tres salidas mutuamente exclusivas y exhaustivas, evaluadas sobre la
diferencia pareada (modelo supervisado menos hibrido): **reemplazar** la etapa semantica,
**complementar** el hibrido (como segunda opinion o senal de gate) o **conservar** el hibrido.
El veredicto SHALL ser exactamente uno de los tres, con su evidencia y su intervalo de
confianza, y SHALL informarse honestamente, **incluida la salida «no supera»**. La regla MUST
NOT redefinirse despues de observar el resultado. El clasificador entregado por defecto SHALL
cambiar solo si el veredicto es **reemplazar**; en cualquier otro caso el hibrido SHALL
permanecer como el clasificador entregado y el modelo supervisado queda seleccionable sin ser
predeterminado.

#### Scenario: Regla declarada antes de ver el resultado

- **WHEN** se inicia el contraste
- **THEN** existe una regla de decision versionada con las tres salidas y sus umbrales, registrada con anterioridad
- **AND** la regla no se modifica despues de observar el resultado

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
