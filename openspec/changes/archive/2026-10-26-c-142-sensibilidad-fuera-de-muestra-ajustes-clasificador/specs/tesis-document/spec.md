## ADDED Requirements

### Requirement: Analisis de sensibilidad frente al ajuste del clasificador con el corpus en resultados

El capitulo de resultados (`07-resultados.tex`) SHALL incluir la subseccion `subsec:sensibilidad-ajustes`, que: enuncia el metodo (re-medicion de la etapa deterministica sin invocar al modelo con el vocabulario previo a su ampliacion con el corpus, conservando la logica de decision y el punto de operacion evaluados, y referencia con la logica de entonces junto con el resultado de su control de fidelidad); declara no factible la reconstruccion del vocabulario por pliegues y su motivo; presenta una tabla compacta `tab:sensibilidad-ajustes` con la configuracion evaluada y las variantes (casos resueltos por la etapa y exactitud con su IC de Wilson al 95 %, y la exactitud global con Gemini fijo solo si es computable); informa el efecto de las reglas de frontera del prompt con el mayor nivel de evidencia disponible o declara que no se cuantifico; y lee los resultados segun las reglas pre-registradas en el diseno del change. Todo valor citado SHALL coincidir con el memo de numeros canonicos. La subseccion MUST NOT afirmar la ausencia de sesgo, MUST NOT presentar metricas obtenidas sobre el corpus como estimaciones fuera de la muestra y MUST NOT modificar ningun valor canonico.

#### Scenario: Subseccion y tabla presentes

- **WHEN** se compila el documento y se lee el capitulo de resultados
- **THEN** existe `subsec:sensibilidad-ajustes` con la tabla `tab:sensibilidad-ajustes`, que incluye la configuracion evaluada (131 casos, 0,7405 con su IC) y las variantes con casos, exactitud e IC
- **AND** las referencias a ambos rotulos resuelven sin advertencias

#### Scenario: Valores trazables al memo

- **WHEN** se coteja cada valor de la subseccion con `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** cada valor figura en la seccion de sensibilidad del memo con su procedencia

#### Scenario: Lectura de una exactitud menor como cota pesimista

- **WHEN** la exactitud de la variante principal es menor que 0,7405
- **THEN** la diferencia se presenta como cota pesimista del sesgo atribuible al vocabulario, con la razon por la que lo es
- **AND** no se la presenta como estimacion puntual del sesgo

#### Scenario: Lectura de una exactitud no menor

- **WHEN** la exactitud de la variante principal no es menor que 0,7405
- **THEN** se declara que el analisis no detecta un sesgo atribuible al vocabulario, sin descartarlo, por la diferencia entre los conjuntos de casos comparados

#### Scenario: Efecto del prompt informado o declarado

- **WHEN** se lee la subseccion
- **THEN** el efecto de las reglas de frontera sobre los 69 casos de la etapa Gemini figura con su nivel de evidencia y su contraste pareado, o se declara no cuantificado

#### Scenario: Columna global solo si es computable

- **WHEN** la exactitud global con Gemini fijo no fue computable
- **THEN** la tabla no incluye esa columna ni su nota

### Requirement: Sesgo optimista acotado en las limitaciones y en la evidencia del objetivo especifico 6

La subseccion `subsec:limitaciones-estudio` de `08-discusion.tex` SHALL incluir una limitacion que declare que el vocabulario del filtro deterministico y las reglas de frontera del prompt se ajustaron con errores observados en el corpus de evaluacion, que las metricas de clasificacion son estimaciones dentro de la muestra, la cota que aporta el analisis de sensibilidad con remision a `subsec:sensibilidad-ajustes`, y que solo un corpus independiente permitiria estimar el desempeno fuera de la muestra. El cardinal de la oracion introductoria de esa subseccion SHALL coincidir con la cantidad de limitaciones enumeradas. El parrafo de procedencia de los datos de ajuste en `subsec:interpretacion-resultados` SHALL remitir a `subsec:sensibilidad-ajustes`. La celda de evidencia del objetivo especifico 6 en `tab:cumplimiento-objetivos` SHALL incluir la referencia a `subsec:sensibilidad-ajustes` y la salvedad de estimacion dentro de la muestra; este requisito MUST NOT alterar el estado de ningun objetivo.

#### Scenario: Limitacion presente y cardinal coherente

- **WHEN** se lee `subsec:limitaciones-estudio`
- **THEN** una limitacion declara el ajuste con el corpus, la naturaleza dentro de la muestra de las metricas y la cota del analisis de sensibilidad, con remision a la subseccion
- **AND** el cardinal de la oracion introductoria coincide con la cantidad de items de la lista

#### Scenario: Remision desde la interpretacion

- **WHEN** se lee el parrafo de procedencia de los datos de ajuste en `subsec:interpretacion-resultados`
- **THEN** remite a `subsec:sensibilidad-ajustes` sin repetir sus valores

#### Scenario: Evidencia del objetivo 6 sin cambio de estado

- **WHEN** se lee la fila del objetivo especifico 6 en `tab:cumplimiento-objetivos`
- **THEN** su evidencia incluye `subsec:sensibilidad-ajustes` y la salvedad de estimacion dentro de la muestra
- **AND** su estado es el que fijen los autores y el change dueno de los estados, sin cambio introducido por este requisito

### Requirement: Calificacion dentro de la muestra de la exactitud deterministica y del contraste entre etapas

Toda aparicion en `sections/*.tex` de la exactitud de la etapa deterministica (`97/131`, `0,7405`) y de la comparacion entre etapas sobre el conjunto cortocircuitable (`0,7405` frente a `0,6769`; `88/130`) SHALL figurar en una oracion o parrafo que la califique como estimacion dentro de la muestra o que remita a `subsec:sensibilidad-ajustes`. La cuantificacion del sesgo SHALL residir solo en `subsec:sensibilidad-ajustes`; los demas pasajes SHALL limitarse a calificar o remitir. Este requisito MUST NOT cambiar ningun valor numerico.

#### Scenario: Cada aparicion calificada

- **WHEN** se listan con `grep` las apariciones de `0,7405`, `97/131`, `97 de 131`, `0,6769` y `88/130` en `sections/*.tex`
- **THEN** cada una esta en una oracion o parrafo que la califica como estimacion dentro de la muestra o que remite a `subsec:sensibilidad-ajustes`

#### Scenario: Cuantificacion en un unico lugar

- **WHEN** se buscan los valores del analisis de sensibilidad fuera de `subsec:sensibilidad-ajustes`
- **THEN** solo aparecen en la limitacion del capitulo de discusion, que remite a la subseccion
- **AND** ningun otro pasaje repite la tabla ni su lectura

#### Scenario: Valores sin cambio

- **WHEN** se comparan los valores numericos de la tesis antes y despues de agregar las calificaciones
- **THEN** no cambia ninguno

<!-- c-144 (archivado el 2026-10-23 en main) ya incorporo al spec vivo el requisito "Ubicacion veraz de las versiones historicas del prompt en el Anexo H"; este change solo verifica el texto resultante. -->
### Requirement: Impacto de paginas del analisis de sensibilidad

El change SHALL registrar el conteo de paginas del PDF compilado tras aplicarlo y su diferencia con el conteo de partida, para la decision de tope de la release. El analisis SHALL presentarse con una unica tabla compacta. Si el conteo supera el tope vigente registrado por el gate G0, SHALL aplicar las compensaciones declaradas en su diseno en el orden previsto y registrar el exceso remanente y su causa; MUST NOT eliminar contenido cientifico, numeros canonicos ni la linea de fuente de la tabla para compensar paginas, aunque SHALL poder trasladar la tabla a un anexo si la regla de G0 limita solo el cuerpo.

#### Scenario: Conteo registrado

- **WHEN** se compila `main.tex` tras aplicar el change
- **THEN** el conteo de paginas y su diferencia con el de partida quedan registrados en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Compensacion sin perdida de contenido

- **WHEN** el conteo supera el tope vigente
- **THEN** se aplican las compensaciones declaradas en el diseno y el exceso remanente se registra para el change de integracion
- **AND** no se elimina ningun valor de la subseccion ni la linea de fuente de la tabla
