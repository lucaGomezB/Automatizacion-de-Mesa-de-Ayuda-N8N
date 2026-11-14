## ADDED Requirements

### Requirement: Propagación del resultado arbitrado a la discusión, las conclusiones y las recomendaciones

`08-discusion.tex`, `09-conclusiones.tex` y `10-recomendaciones.tex` SHALL razonar sobre la
validación fuera de muestra a partir de la cifra primaria del corpus arbitrado y de sus lecturas
complementarias, con las cifras de la sección de c-221 del memo canónico. La discusión SHALL informar
cuántos de los `47` discordantes originales acertó el clasificador y SHALL presentar el arbitraje
como la medición que reemplazó al análisis de escenarios. La estimación sobre `103` casos SHALL
quedar rotulada como etapa previa y, fuera de `07-resultados.tex`, SHALL aparecer una sola vez en
todo `sections/*.tex`, tablas incluidas: en la fila del segundo objetivo de
`tab:cumplimiento-objetivos` (regla de «Repetición de cifras acotada y remisión a la tabla fuera de
muestra», modificada por este change). Esos capítulos MUST NOT afirmar que el arbitraje está pendiente, MUST NOT
contener «sin el arbitraje de los 47» ni el requisito de «41 de los 47», y MUST NOT usar el peor y
el mejor caso como argumento principal.

#### Scenario: Sin razonamiento de arbitraje pendiente

- **WHEN** se buscan en `08-discusion.tex`, `09-conclusiones.tex` y `10-recomendaciones.tex` las cadenas «sin el arbitraje» y «41 de los 47»
- **THEN** no hay coincidencias
- **AND** la discusión informa los aciertos sobre los `47` discordantes originales con remisión a la subsección de la validación fuera de muestra

#### Scenario: Estimación previa acotada

- **WHEN** se ejecuta `rg -n "0,8447" "docs/Tesis/v10 (IA)/paper/sections" -g "!07-resultados.tex"`
- **THEN** devuelve una sola línea, la fila del segundo objetivo de `tab:cumplimiento-objetivos` en `09-conclusiones.tex`
- **AND** esa fila rotula la cifra como etapa previa

### Requirement: Clase Sistemas descrita con el soporte del corpus arbitrado

La discusión, las conclusiones y las recomendaciones SHALL describir la clase `Sistemas` con el
soporte, la F1, la sensibilidad y los destinos de error del corpus arbitrado registrados en la
sección de c-221, y MUST NOT citar la F1 sobre `5` casos como estado vigente ni afirmar que la clase no
puede estimarse. El texto MUST NOT afirmar que el error de `Sistemas` se dirige a una única clase
si los destinos de error registrados incluyen más de una con peso relevante. En
`07-resultados.tex`, el valor `31/61` de `Sistemas` SHALL rotularse como sensibilidad.

#### Scenario: Cifras de Sistemas actualizadas

- **WHEN** se busca `0,2222` en `08-discusion.tex`, `09-conclusiones.tex` y `10-recomendaciones.tex`
- **THEN** no hay coincidencias
- **AND** los tres capítulos citan el soporte de `61` casos y los destinos de error

### Requirement: Trabajos futuros reformulados a partir de lo ejecutado

`10-recomendaciones.tex` MUST NOT proponer como trabajo futuro el sobremuestreo de `Sistemas` con
doble etiquetado y arbitraje por un tercer etiquetador, ni fijar como criterio de éxito que el
arbitraje se ejecute antes de reportar, porque ambas cosas se ejecutaron. La línea de
`subsec:frontera-sistemas` SHALL orientarse al análisis de la taxonomía con los casos disponibles
y SHALL tener criterio de éxito; la de `subsec:corpus-independiente` SHALL proponer un corpus de
composición natural, con cuotas prefijadas y arbitraje por mayoría de tres etiquetadores.

#### Scenario: Líneas ya ejecutadas retiradas

- **WHEN** se leen `subsec:frontera-sistemas` y `subsec:corpus-independiente`
- **THEN** ninguna propone como próximo paso lo ya realizado
- **AND** cada una declara un criterio de éxito

### Requirement: Subsecciones propias para la validación fuera de muestra y las comparaciones

`07-resultados.tex` SHALL presentar la validación fuera de muestra en la subsección
`subsec:validacion-fuera-muestra` y las comparaciones con la línea de base clásica y con el
esquema de modelo de lenguaje solo en `subsec:comparacion-alternativas`, ambas después de
`subsec:resultados-campana-medicion` y antes de `subsec:ruido-referencia`. Las etiquetas
`tab:fuera-de-muestra`, `tab:linea-base-clasica` y `tab:gemini-solo` SHALL conservar su nombre. La
validación SHALL incluir las tres lecturas de la exactitud con su rótulo, el desglose por origen
de la referencia y por etapa, y una tabla nueva `tab:fuera-de-muestra-clases` con la matriz de
confusión y las métricas por clase del corpus arbitrado. Las remisiones del resto del documento a
contenido de la validación SHALL apuntar a `subsec:validacion-fuera-muestra`. La frase inicial del
capítulo SHALL enumerar todos sus apartados.

#### Scenario: Estructura y referencias

- **WHEN** se compila la tesis
- **THEN** existen las dos subsecciones nuevas y la tabla de métricas por clase
- **AND** no hay referencias indefinidas ni etiquetas duplicadas
- **AND** la frase inicial del capítulo nombra la validación fuera de muestra y las comparaciones

### Requirement: Apartado metodológico del diseño fuera de muestra

`04-marco-metodologico.tex` SHALL describir el diseño de la validación fuera de muestra: la
procedencia y el período de los casos según lo declaren los autores; las cuotas por canal y el
sobremuestreo de `Bases de Datos`; el refuerzo de clases chicas, su fecha, que se reunió después
de conocer el desempeño en `Sistemas` y sin cuota prefijada, y su composición; la regla de
arbitraje (decide el tercer etiquetador cuando los dos primeros difieren; no es mayoría); la
cantidad de referencias fijadas por el tercer etiquetador; y los casos con tres etiquetas
distintas. La sección de amenazas a la validez SHALL incorporar las amenazas propias de esa
validación y su conteo SHALL coincidir con las amenazas enumeradas. La tesis MUST NOT inventar la
procedencia ni el período: si los autores no los aportan, la tarea queda bloqueada.

#### Scenario: Diseño declarado

- **WHEN** se lee el capítulo 4
- **THEN** figuran las cuotas, el refuerzo posterior a los datos, la regla de arbitraje, las referencias fijadas por `E5` y los `6` casos de tres vías
- **AND** el conteo de amenazas coincide con las enumeradas

### Requirement: Resumen con la evidencia fuera de muestra

`00-resumen.tex` SHALL mencionar, en el resumen y en el *abstract*, la exactitud fuera de muestra
sin exclusión y el resultado frente a la línea de base clásica, con cifras de la sección de c-221 o de
secciones vigentes del memo, y SHALL respetar el límite de 250 palabras con la regla de conteo de
c-106. La lectura del balance neto SHALL coincidir con la de la discusión y las conclusiones.

#### Scenario: Resumen completo y dentro del límite

- **WHEN** se cuenta y se lee el resumen
- **THEN** menciona la exactitud fuera de muestra y la línea de base
- **AND** el resumen y el *abstract* tienen 250 palabras o menos cada uno

### Requirement: Afirmaciones acotadas a lo medido

`05-arquitectura.tex` MUST NOT afirmar que el diseño compositivo reduce la latencia y el costo de
inferencia sin remitir a lo medido en `tab:gemini-solo` y sin declarar que la latencia se midió
solo como cota inferior. `09-conclusiones.tex` SHALL matizar la viabilidad del modelo de lenguaje
para la clasificación con la exactitud por etapa fuera de muestra y con la salvedad de que la
etapa Gemini recibe los casos que las reglas no resuelven. `01-introduccion.tex` SHALL precisar
que lo excluido del alcance es un modelo supervisado afinado con el corpus acumulado en operación
y que la línea de base clásica se usa como referencia de comparación.

#### Scenario: Latencia y costo con respaldo

- **WHEN** se busca «reduce la latencia y el costo de inferencia» en `05-arquitectura.tex`
- **THEN** no hay coincidencias sin remisión a `tab:gemini-solo`

#### Scenario: Alcance precisado

- **WHEN** se lee el alcance en `01-introduccion.tex`
- **THEN** la exclusión nombra el modelo supervisado afinado con el corpus de operación y no contradice la línea de base medida

### Requirement: Balance neto con sensibilidad fuera de muestra

`subsec:balance-neto` SHALL incluir la sensibilidad del balance con la tasa de error fuera de
muestra (ponderada y cruda) registrada en la sección de c-221, rotulada como sensibilidad que mezcla
corpus y referencias, y SHALL ajustar su síntesis para declarar de qué exactitud depende el signo.

#### Scenario: Sensibilidad presente

- **WHEN** se lee `subsec:balance-neto`
- **THEN** figuran los balances con 5, 10 y 15 minutos para las dos tasas fuera de muestra con el rótulo de sensibilidad

### Requirement: Reproducibilidad declarada

La tesis SHALL declarar que la confianza de Gemini difirió entre las dos corridas fuera de muestra
en los casos comunes, con la cantidad registrada, y que el orden del prerregistro de la calibración
se demuestra con las fechas de autor de los commits. La documentación de la campaña SHALL registrar
que el `commit` declarado en `predicciones_independiente.json` no es alcanzable desde `main` (puede
existir como objeto colgante en el clon donde se hizo la corrida, pero no viaja con `fetch` ni con
`clone`) y cuál commit versionó el archivo. MUST NOT afirmar que ese commit no existe.

#### Scenario: Declaraciones presentes

- **WHEN** se leen la calibración de resultados y la metodología
- **THEN** figuran la variación entre corridas y la nota sobre las fechas de autor

#### Scenario: Commit de la primera corrida descrito por alcanzabilidad

- **WHEN** se lee el README de la campaña sobre `predicciones_independiente.json`
- **THEN** dice que el `commit` declarado no es alcanzable desde `main` y nombra el commit que versionó el archivo
- **AND** no afirma que el commit no exista

### Requirement: Sin identificadores internos de cambio en el cuerpo

`sections/*.tex` MUST NOT contener, fuera de comentarios, identificadores de cambio con la forma
`c-NNN`. Los nombres de archivos versionados con sufijo `_cNNN` SHALL admitirse solo como rutas en
notas de fuente de tablas o figuras.

#### Scenario: Búsqueda sin coincidencias

- **WHEN** se ejecuta `rg -n "c-[0-9]{3}"` sobre `sections/*.tex`
- **THEN** toda coincidencia está en una línea de comentario

### Requirement: Marco teórico, glosario, estado del arte y bibliografía completos

`02-marco-teorico.tex` SHALL presentar la representación TF-IDF, la regresión logística, el puntaje
de Brier y el AUROC antes de su uso metodológico; `00-glosario.tex` SHALL definir AUROC, Brier y
TF-IDF. La atribución a `MosqueiraRey2023_human_in_the_loop` SHALL verificarse en el texto completo
o atenuarse a lo que el artículo hace. `03-estado-del-arte.tex` SHALL declarar que el trabajo de
Colavito y colaboradores clasifica incidencias de GitHub y no tickets de mesa de ayuda. Las claves
bibliográficas SHALL coincidir con el año de su campo, verificado contra la edición citada. Las URL
citadas SHALL responder o reemplazarse por una fuente oficial accesible. Una norma solo SHALL
citarse si se verificó en una fuente oficial.

#### Scenario: Términos definidos y claves coherentes

- **WHEN** se revisan el glosario y la bibliografía
- **THEN** AUROC, Brier y TF-IDF figuran en el glosario
- **AND** ninguna clave tiene un año distinto del de su campo
- **AND** `verify_citations.py` no informa citas huérfanas ni entradas sin uso

### Requirement: Versión entregada identificable y con la evidencia vigente

La portada, la entrada bibliográfica del repositorio y el Anexo B SHALL identificar la misma
versión nueva, cuyo tag SHALL contener el texto y los artefactos de evidencia que la tesis cita. El
Anexo B MUST NOT afirmar que los commits posteriores al tag no modifican las fuentes si eso no es
verificable; SHALL declarar que el commit posterior al tag solo consigna su hash. El cronograma
SHALL registrar la validación fuera de muestra, el arbitraje, la línea de base y los análisis
posteriores con la precisión de su evidencia. `paper/compilacion.md` SHALL regenerarse con la
compilación final. La creación y la publicación del tag MUST NOT realizarse sin confirmación
expresa de los autores.

#### Scenario: Tag coherente con el documento

- **WHEN** se compara el hash del Anexo B con `git rev-parse <tag>^{commit}`
- **THEN** coinciden
- **AND** `git show <tag>:` encuentra los artefactos de evidencia citados por la tesis
- **AND** la portada y la entrada del repositorio nombran la misma versión

#### Scenario: Cronograma actualizado

- **WHEN** se lee `docs/diagrams/cronograma.md`
- **THEN** figuran los hitos de noviembre de 2026 con su evidencia

## MODIFIED Requirements

### Requirement: Repetición de cifras acotada y remisión a la tabla fuera de muestra

La exactitud estricta fuera de muestra `0,8447` con `n = 103` (estimación con exclusión, etapa
previa) SHALL aparecer fuera de `07-resultados.tex` una sola vez en todo `sections/*.tex`, tablas
incluidas: en la fila del segundo objetivo de `tab:cumplimiento-objetivos`, rotulada como etapa
previa. La pareja exactitud estricta arbitrada `0,6893` con `n = 206` SHALL aparecer en prosa como
máximo una vez por capítulo en `08-discusion.tex`, `09-conclusiones.tex` y
`10-recomendaciones.tex`; para esta cifra las tablas, incluidas `tab:fuera-de-muestra` y la tabla
de cumplimiento de objetivos, quedan exentas. Las menciones restantes SHALL reemplazarse por una
remisión a `tab:fuera-de-muestra` o a `subsec:validacion-fuera-muestra`. La reducción MUST NOT
cambiar el valor de ninguna cifra, cita ni afirmación sustantiva, y MUST NOT introducir referencias
cruzadas sin destino.

#### Scenario: Conteo de repeticiones en prosa

- **WHEN** se ejecuta `rg -n "0,8447" "docs/Tesis/v10 (IA)/paper/sections" -g "!07-resultados.tex"` y se cuentan las apariciones en prosa de `0,6893` en los capítulos 8, 9 y 10
- **THEN** `0,8447` devuelve una sola línea, la fila del segundo objetivo en `09-conclusiones.tex`
- **AND** `0,6893` aparece en prosa como máximo una vez por capítulo
- **AND** las demás menciones son remisiones a `tab:fuera-de-muestra` o a `subsec:validacion-fuera-muestra`

#### Scenario: Cifras y citas intactas

- **WHEN** se compara el texto antes y después de la reducción
- **THEN** ninguna cifra canónica, cita o afirmación sustantiva cambia
- **AND** todas las remisiones nuevas resuelven a una etiqueta existente

### Requirement: Reporte de la validacion fuera de muestra

La tesis SHALL reportar en `subsec:validacion-fuera-muestra` las metricas fuera de
muestra por etapa del clasificador congelado sobre el corpus independiente
(`evaluation/data/campana/predicciones_independiente.json`, reporte in-sample frente a
out-of-sample de c-167, y `evaluation/data/campana/predicciones_arbitrado.json` sobre el corpus
arbitrado), con su `n` e intervalos, contrastadas con las estimaciones
dentro de la muestra, y SHALL actualizar `08-discusion.tex` (parrafo de procedencia de
los datos de ajuste) y `subsec:corpus-independiente` en consecuencia. Si no existe
`predicciones_independiente.json`, la tesis SHALL declarar "sin corpus independiente
declarado" y que las metricas permanecen como estimaciones dentro de la muestra. La
procedencia de los ajustes y la calificacion dentro de la muestra de los 200 casos se
rigen por el requisito "Procedencia declarada de los ajustes realizados sobre el corpus
de validacion"; este requisito solo agrega el resultado fuera de muestra.

#### Scenario: Validacion fuera de muestra reportada

- **WHEN** existe `predicciones_independiente.json` y se lee `subsec:validacion-fuera-muestra`
- **THEN** se reportan las metricas por etapa sobre el corpus independiente con su `n` y sus intervalos, junto a las estimaciones dentro de la muestra
- **AND** `subsec:corpus-independiente` se retitula como replicacion sobre corpus adicionales y remite a resultados

#### Scenario: Sin corpus independiente declarado

- **WHEN** no existe `predicciones_independiente.json`
- **THEN** la tesis declara "sin corpus independiente declarado" en resultados, discusion y memo
- **AND** `subsec:corpus-independiente` conserva la recomendacion de construir ese corpus
