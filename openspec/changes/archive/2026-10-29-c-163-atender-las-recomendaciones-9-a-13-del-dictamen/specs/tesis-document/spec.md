## ADDED Requirements

### Requirement: Declaracion del diseno cuasiexperimental

La subseccion 4.1 del marco metodologico (`04-marco-metodologico.tex`, `subsec:diseno-investigacion`) SHALL rotular el diseno del estudio como cuasiexperimental, coherente con la asignacion no aleatoria de los casos y con el control parcial de las condiciones. El texto MUST NOT describirlo como "experimental" ni como un experimento "bajo condiciones controladas".

#### Scenario: Rotulo cuasiexperimental en 4.1

- **WHEN** se lee la subseccion 4.1 del PDF compilado
- **THEN** el diseno se describe como cuasiexperimental
- **AND** no aparece la caracterizacion "experimental" con "bajo condiciones controladas"

### Requirement: Separacion del efecto de cobertura y del efecto de exactitud en la comparacion de configuraciones

La subseccion 8.5 (`07-resultados.tex`) SHALL separar el efecto de COBERTURA (el paso de 74 a 131 casos clasificados por cortocircuito deterministico) del efecto de EXACTITUD (38 aciertos frente a 37 en los 67 casos comunes) al comparar la configuracion previa con la entregada. La "cota pesimista" SHALL presentarse como una INTERPRETACION de esa lectura y no como una medicion. El texto MUST NOT atribuir a la exactitud una ganancia que provenga de la cobertura.

#### Scenario: Cobertura y exactitud separadas

- **WHEN** se lee la comparacion de configuraciones en 8.5
- **THEN** el cambio de cobertura (74 -> 131 casos) y el cambio de exactitud (38 vs 37 en los 67 casos comunes) se presentan por separado
- **AND** la "cota pesimista" se rotula como interpretacion

#### Scenario: Sin ganancia de exactitud atribuida a la cobertura

- **WHEN** se lee la conclusion de 8.5 sobre la mejora entre configuraciones
- **THEN** la mejora de cobertura no se presenta como una mejora de exactitud
- **AND** el texto no afirma una ganancia sustantiva que la comparacion de los 67 casos comunes no respalde

### Requirement: Completitud del Anexo H sobre `safety_settings`, ejemplos por clase y grafia de la clave JSON

El Anexo H (`12-anexos.tex`, `sec:anexo-prompt-gemini`) SHALL completar: (a) las categorias y umbrales de `safety_settings` configurados; (b) el numero de ejemplos por clase del prompt; y (c) la grafia exacta de la clave JSON del clasificador (`categoría`, con tilde), coherente con el contrato real. El Anexo MUST NOT quedar con datos faltantes ni con una grafia de clave distinta de la del codigo.

#### Scenario: `safety_settings` detallados

- **WHEN** se lee el Anexo H en el PDF compilado
- **THEN** figuran las categorias de `safety_settings` con sus umbrales
- **AND** no queda la sola mencion "`safety_settings`" sin detalle

#### Scenario: Ejemplos por clase declarados

- **WHEN** se lee la descripcion del prompt del Anexo H
- **THEN** se declara el numero de ejemplos por clase
- **AND** el numero es coherente con el prompt versionado

#### Scenario: Grafia de la clave JSON correcta

- **WHEN** se lee el ejemplo de salida JSON del Anexo H
- **THEN** la clave aparece como `categoría` (con tilde), como en el contrato real
- **AND** no aparece `categoria` sin tilde como la clave del JSON

### Requirement: Precision del marco legal de la Ley 25.326 y del RGPD

La seccion 11 del capitulo de consideraciones eticas y legales (`11-aspectos-legales.tex`) SHALL: (a) emplear "disociacion" (articulo 2 de la Ley 25.326) junto a "pseudonimizacion"; (b) enunciar el derecho de acceso con el plazo del articulo 14 (diez dias corridos) y el de rectificacion, actualizacion o supresion con el del articulo 16 (cinco dias habiles); (c) presentar la trazabilidad como una medida TECNICA que facilita el cumplimiento del articulo 9 (calidad de los datos), no como una exigencia literal de la ley; (d) describir el ambito de aplicacion del RGPD segun su articulo 3.2 ("personas que se encuentren en la Union"), no como "residentes europeos"; y (e) respaldar la mencion a la Decision 2003/490/CE con su entrada bibliografica. El texto MUST NOT atribuir a la ley una exigencia que su texto no enuncia.

#### Scenario: Disociacion junto a pseudonimizacion

- **WHEN** se lee el tratamiento de datos de la seccion 11
- **THEN** "disociacion" (art. 2, Ley 25.326) aparece junto a "pseudonimizacion"
- **AND** no se presenta la pseudonimizacion como el unico mecanismo de proteccion

#### Scenario: Plazos del articulo 14 y del articulo 16

- **WHEN** se leen los plazos legales de la seccion 11
- **THEN** el acceso se enuncia con diez dias corridos (art. 14) y la rectificacion, actualizacion o supresion con cinco dias habiles (art. 16)
- **AND** los plazos citados coinciden con el texto de la ley

#### Scenario: Trazabilidad como medida tecnica

- **WHEN** se lee la justificacion de la trazabilidad
- **THEN** se presenta como una medida tecnica que facilita el cumplimiento del articulo 9
- **AND** no se presenta como una exigencia literal de la ley

#### Scenario: Ambito del RGPD segun el articulo 3.2

- **WHEN** se lee la delimitacion del RGPD
- **THEN** el ambito se enuncia conforme al articulo 3.2 ("personas que se encuentren en la Union")
- **AND** no se usa "residentes europeos"

#### Scenario: Decision 2003/490/CE con entrada bibliografica

- **WHEN** se cita la Decision 2003/490/CE
- **THEN** existe la entrada bibliografica correspondiente en `Bibliography_base.bib`
- **AND** la referencia compilada resuelve a la norma

### Requirement: Remision a las figuras desde el cuerpo

El cuerpo de la tesis SHALL citar las figuras que sustenta desde la prosa, sin dejar figuras sin citar. En particular, la Figura 8 SHALL citarse desde la subseccion 8.1 (`07-resultados.tex`) y las Figuras 3 a 5 SHALL citarse desde el capitulo 5 (`05-arquitectura.tex`), mediante `\ref`/`\autoref` a sus etiquetas. El texto MUST NOT dejar una figura requerida sin una remision en prosa.

#### Scenario: Figura 8 citada desde 8.1

- **WHEN** se lee la subseccion 8.1 del PDF compilado
- **THEN** se remite a la Figura 8 por su etiqueta
- **AND** la figura no queda sin citar en el cuerpo

#### Scenario: Figuras 3 a 5 citadas desde el capitulo 5

- **WHEN** se lee el capitulo 5 del PDF compilado
- **THEN** se remite a las Figuras 3, 4 y 5 por sus etiquetas
- **AND** ninguna de las tres queda sin citar

### Requirement: Rol de cada director declarado en el marco metodologico

La subseccion 4.9 del marco metodologico (`04-marco-metodologico.tex`) SHALL aclarar el rol o la contribucion de cada director del trabajo, de modo que su mencion no quede sin especificar. La aclaracion SHALL ser coherente con la portada y con la autoria registrada en el repositorio. El texto MUST NOT atribuir a los directores un rol que el repositorio no respalde.

#### Scenario: Roles de los directores explicitados

- **WHEN** se lee la subseccion 4.9
- **THEN** se declara el rol o la contribucion de cada director
- **AND** la mencion es coherente con la portada y con la autoria registrada

### Requirement: Conformidad formal APA 7 y metadatos del aparato bibliografico

El aparato bibliografico SHALL cumplir las convenciones formales de APA 7 senaladas por el dictamen: coma antes del ano en todas las citas parenteticas con "et al."; titulos en sentence case; ordinales de edicion con punto y o voladita ("2.a ed."); raya corta (no guion largo) en los rangos de paginas; "ISO/IEC" como autor institucional de las normas; formato "(Vol., pp.)" en Paramesh; dia en las entradas legales; Hohpe y Woolf (2004); nota de Mayor-Rocher en espanol; apellido compuesto de Touvron; version arbitrada de Ramya et al. o justificacion registrada del preprint con fecha de consulta; y edicion, editor y DOI de Efron y Tibshirani verificados. La definicion del estilo SHALL residir en `preambles/preamble.tex` cuando corresponda. El documento MUST NOT imprimir citas o entradas que incumplan esas convenciones.

#### Scenario: Coma antes del ano en las citas con "et al."

- **WHEN** se inspecciona una cita parentetica con tres o mas autores en el PDF compilado
- **THEN** el separador entre autor y ano es la coma ("X et al., ano")
- **AND** no aparece la forma sin coma en ninguna cita parentetica

#### Scenario: Titulos, ordinales y rangos conformes

- **WHEN** se inspecciona la bibliografia impresa
- **THEN** los titulos usan sentence case y los rangos de paginas usan raya corta
- **AND** las ediciones se numeran con el ordinal conforme ("2.a ed.")

#### Scenario: Autor institucional y entradas particulares

- **WHEN** se inspeccionan las entradas de normas, Paramesh y las legales
- **THEN** las normas usan "ISO/IEC" como autor institucional, Paramesh usa "(Vol., pp.)" y las entradas legales incluyen el dia
- **AND** Hohpe y Woolf consignan 2004, la nota de Mayor-Rocher esta en espanol y el apellido de Touvron es compuesto

#### Scenario: Ramya y Efron verificadas

- **WHEN** se inspeccionan las entradas `ramya2021classifying` y `Efron1993_bootstrap`
- **THEN** Ramya remite a la version arbitrada o registra la justificacion del preprint con fecha de consulta
- **AND** la edicion, el editor y el DOI de Efron y Tibshirani quedan verificados

### Requirement: Fuentes primarias de los procedimientos estadisticos y de calibracion restantes

La tesis SHALL incorporar, verificadas antes de citarlas, las fuentes primarias de los procedimientos estadisticos que aun carecen de ellas: la prueba de Shapiro-Wilk (Shapiro & Wilk, 1965), la prueba de McNemar (McNemar, 1947), las metricas multietiqueta de subset accuracy, Hamming loss y micro-F1, el coeficiente r rank-biserial, la eficiencia relativa asintotica de la prueba de rangos con signo (Hodges & Lehmann, 1956) y la regresion isotonica como metodo de calibracion. La prueba de Wilcoxon en 8.1 SHALL respaldarse ademas con su fuente primaria, no solo con la implementacion (SciPy). Cada entrada nueva SHALL incluir autor, titulo, ano y campo de publicacion mas `doi` o `url`, y existir en `Bibliography_base.bib`. El documento MUST NOT citar un metodo estadistico sin su fuente primaria correspondiente.

#### Scenario: Fuentes primarias incorporadas

- **WHEN** se inspecciona `Bibliography_base.bib`
- **THEN** existen entradas para Shapiro-Wilk, McNemar, las metricas multietiqueta, el r rank-biserial, la eficiencia relativa asintotica y la regresion isotonica
- **AND** cada una incluye metadatos completos y `doi` o `url`

#### Scenario: Wilcoxon respaldado en 8.1

- **WHEN** se lee la seccion 8.1 del PDF compilado
- **THEN** la prueba de Wilcoxon cita su fuente primaria ademas de la implementacion
- **AND** no queda respaldada unicamente por la implementacion

#### Scenario: Sin metodo sin fuente

- **WHEN** se recorren los metodos estadisticos y de calibracion citados en la tesis
- **THEN** cada uno tiene su fuente primaria en `Bibliography_base.bib`
- **AND** no queda ningun metodo sin entrada

## MODIFIED Requirements

### Requirement: Desdoblamiento de la hipótesis principal en sub-hipótesis contrastables

La introducción (`01-introduccion.tex`, §Hipótesis de trabajo) SHALL formular la
hipótesis principal desdoblada en tres sub-hipótesis contrastables: (a) tiempo de
registro, (b) proporción de intervención humana y (c) exactitud o F1 macro. Cada
sub-hipótesis SHALL enunciar su propio contraste y su criterio de falsación
explícito. El contraste de la sub-hipótesis temporal SHALL ser el contraste no
paramétrico `H0`/`H1` cuya hipótesis nula se enuncia sobre las DIFERENCIAS
PAREADAS de los tiempos de registro (no sobre la igualdad de medianas), y la misma
formulación SHALL repetirse en la subsección 8.1 (`07-resultados.tex`). El de
exactitud o F1 SHALL formularse como umbral de desempeño verificado contra la
exactitud observada y su intervalo de confianza de Wilson, sin invocar la zona de
rechazo del contraste de tiempos. El documento MUST NOT presentar la hipótesis
principal como una conjunción indivisible que se confirme o refute como bloque,
ni enunciar la hipótesis nula de tiempos como una igualdad de medianas.

#### Scenario: Tres sub-hipótesis con contraste propio

- **WHEN** se lee la subsección de hipótesis de trabajo en `01-introduccion.tex`
- **THEN** se distinguen tres sub-hipótesis: tiempo, intervención humana y exactitud/F1
- **AND** cada una enuncia su propio contraste

#### Scenario: Hipótesis nula de Wilcoxon sobre las diferencias pareadas

- **WHEN** se lee el contraste de la sub-hipótesis temporal en 1.4 y en 8.1
- **THEN** la hipótesis nula se enuncia sobre las diferencias pareadas de los tiempos
- **AND** no se enuncia como una igualdad de medianas

#### Scenario: Criterio de falsación explícito por sub-hipótesis

- **WHEN** se lee cada sub-hipótesis
- **THEN** declara la condición que la falsaría
- **AND** la sub-hipótesis de exactitud/F1 usa el umbral `85 %`/`0,85` como criterio de desempeño verificado contra el intervalo de confianza, no como zona de rechazo

#### Scenario: Sin conjunción indivisible

- **WHEN** se lee la formulación de la hipótesis principal
- **THEN** no se enuncia como una única conjunción de mecanismo y umbral de desempeño
- **AND** no se declara confirmada o refutada en bloque

### Requirement: Cobertura y densidad de citas por capitulo

Las afirmaciones que se apoyan en literatura SHALL citar una referencia
verificable en el punto donde se formulan. Ademas de las dos entradas requeridas
para la definicion de empresa mediana y el marco etico, el change SHALL poder
incorporar las fuentes primarias de los procedimientos estadisticos y de
calibracion (Shapiro-Wilk, McNemar, metricas multietiqueta, r rank-biserial,
eficiencia relativa asintotica, regresion isotonica y la Decision 2003/490/CE);
fuera de esas excepciones, la bibliografia moderna 2023-2026 incorporada por c-78
SHALL reutilizarse, sin duplicar su trabajo. El documento MUST NOT introducir
referencias nuevas ajenas a esos conjuntos ni dejar citas huerfanas o entradas sin
usar.

#### Scenario: Capitulo 7 con citas donde corresponde

- **WHEN** se leen las afirmaciones del Capitulo~7 (`07-resultados.tex`) que se apoyan en literatura o en metodos de terceros
- **THEN** esas afirmaciones citan una referencia verificable
- **AND** el capitulo deja de tener cero citas sobre afirmaciones propias que requieren respaldo

#### Scenario: Capitulo 6 y Capitulo 3 con respaldo

- **WHEN** se revisan las afirmaciones metodologicas del Capitulo~6 (`06-implementacion.tex`) y la comparacion del Capitulo~3
- **THEN** las afirmaciones apoyadas en literatura citan una referencia verificable
- **AND** la Tabla~1 del Capitulo~3 deja de sostener su comparacion sin citas

#### Scenario: Sin duplicar la bibliografia de c-78

- **WHEN** se inspecciona `Bibliography_base.bib` despues de este change
- **THEN** las entradas agregadas son las fuentes primarias de metodo, la Decision 2003/490/CE y las dos ya habilitadas, sin duplicar las de c-78
- **AND** las referencias 2023-2026 usadas provienen de las ya incorporadas por c-78
- **AND** no se crean entradas duplicadas ni citas huerfanas nuevas
