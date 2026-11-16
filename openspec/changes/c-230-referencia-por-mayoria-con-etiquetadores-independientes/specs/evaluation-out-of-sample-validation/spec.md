## ADDED Requirements

### Requirement: OOS-026 — Recomputo de la cifra primaria bajo la referencia por mayoria y comparacion honesta

Cuando la referencia del corpus fuera de muestra quede construida por mayoria de cinco etiquetadores
independientes (`discordant-arbitration`, ARB-009), el analisis SHALL recomputar sobre el corpus
arbitrado, con el clasificador congelado y sin invocar a Gemini ni a la red, la exactitud estricta
cruda y las metricas por clase (matriz `5x5` con precision, sensibilidad, F1 y soporte) bajo la
referencia por mayoria y bajo la referencia vigente de arbitro unico, y SHALL reportar AMBAS
lecturas, rotuladas. La lectura por mayoria SHALL rotularse como la referencia primaria nueva solo si
los autores lo confirman; en cualquier caso el analisis MUST NOT ocultar el cambio de la cifra
primaria ni presentar una sola lectura como si la otra no existiera. El analisis SHALL informar el
delta de la exactitud estricta y de la macro-F1 entre ambas referencias, con su conteo de casos que
cambian de acierto a error y de error a acierto, y SHALL conservar la lectura vigente rotulada como
referencia de arbitro unico. El analisis SHALL declarar que la re-clasificacion no se ejecuta dentro
del analisis (usa las predicciones congeladas) y que el veredicto del umbral de `0,85` se recalcula
con el intervalo de Wilson de cada lectura, sin presentarlo como veredicto unico. Antes de escribir
salidas, el analisis SHALL reproducir los anclajes canonicos (`142/206` de exactitud estricta y
macro-F1 `0,7024` sobre la referencia vigente); si no los reproduce, MUST terminar con error sin
escribir archivos. Las salidas SHALL ser deterministas byte a byte y SHALL registrarse en una seccion
aditiva del memo canonico con su archivo fuente y el comando que las produce.

#### Scenario: Dos lecturas rotuladas

- **WHEN** se ejecuta el recomputo con la referencia por mayoria disponible
- **THEN** el resultado informa la exactitud estricta y las metricas por clase bajo la referencia por mayoria y bajo la referencia vigente de arbitro unico
- **AND** cada lectura esta rotulada y ninguna se presenta como si la otra no existiera

#### Scenario: Cambio de la cifra primaria declarado

- **WHEN** la exactitud estricta bajo la referencia por mayoria difiere de la vigente
- **THEN** el resultado informa el delta, los casos que cambian de acierto a error y de error a acierto, y el nuevo intervalo de Wilson
- **AND** la cifra primaria previa no cambia de valor hasta que los autores confirmen la rotulacion

#### Scenario: Anclajes reproducidos antes de escribir

- **WHEN** el analisis lee las predicciones y el corpus congelados
- **THEN** reproduce `142/206` de exactitud estricta y macro-F1 `0,7024` sobre la referencia vigente antes de cualquier comparacion
- **AND** si no los reproduce, termina con error sin escribir salidas

#### Scenario: Veredicto del umbral por lectura

- **WHEN** se compara cada lectura con el umbral de `0,85`
- **THEN** el resultado informa, por lectura, si el limite superior de su intervalo de Wilson queda por debajo de `0,85`
- **AND** no presenta un unico veredicto del umbral

#### Scenario: Sin red ni re-clasificacion

- **WHEN** se ejecuta el analisis
- **THEN** usa las predicciones congeladas y no invoca a Gemini ni a la red
- **AND** `evaluation/report.md`, `evaluation/predicciones.json` y los artefactos congelados quedan sin cambios
