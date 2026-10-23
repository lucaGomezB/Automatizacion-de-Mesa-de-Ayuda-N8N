## MODIFIED Requirements

### Requirement: Calibración de la confianza del clasificador

La tesis SHALL reportar la relacion entre la confianza devuelta por el clasificador y su exactitud DESAGREGADA POR ETAPA del pipeline, porque la etapa deterministica y la etapa Gemini emiten magnitudes de confianza de naturaleza distinta (definidas en el subsistema de clasificacion, `subsec:subsistema-clasificacion`). El capitulo de resultados MUST incluir la exactitud por banda de confianza separada por etapa (casos, aciertos y exactitud), la exactitud estricta de cada etapa con su IC de Wilson y la contingencia de confianza alta/baja en torno a 0,70 con su composicion por etapa. La conclusion sobre calibracion SHALL restringirse a la etapa Gemini y a su rango efectivo observado (0,85 a 1,00) y SHALL declarar que la etapa de reglas no emite una confianza utilizable como criterio de derivacion. La tesis MUST NOT caracterizar al clasificador en su conjunto como "anti-calibrado" ni como de "calibracion invertida". El capitulo de discusion MUST interpretar la implicancia de la lectura por etapa para el umbral de revision humana de 0,70.

#### Scenario: Tabla de calibracion por etapa presente

- **WHEN** se lee el capitulo de resultados
- **THEN** existe una tabla que cruza las bandas de confianza con la etapa del pipeline y reporta casos, aciertos y exactitud por celda
- **AND** se reportan la precision del segmento de confianza `>= 0,70` y la del segmento `< 0,70` junto con su composicion por etapa (los 124 casos con confianza `< 0,70` son de la etapa deterministica; el segmento `>= 0,70` reune 7 casos deterministicos y los 69 de Gemini)

#### Scenario: Contraste agregado leido como efecto de composicion

- **WHEN** se lee la interpretacion del contraste agregado entre confianza alta (0,697) y confianza baja (0,758)
- **THEN** se presenta como una comparacion entre la etapa de reglas y la etapa de modelo, no como evidencia sobre la calibracion de la confianza
- **AND** ninguna fuente `.tex` contiene las expresiones "anti-calibr" ni "calibracion invertida" (con o sin tilde)

#### Scenario: Conclusion restringida al rango efectivo de Gemini

- **WHEN** se lee la conclusion de la subseccion de calibracion
- **THEN** se reportan las exactitudes de la etapa Gemini en las bandas `[0,85; 0,95)` y `[0,95; 1,00]` con su IC de Wilson y se declara que la confianza autodeclarada por Gemini no discrimina aciertos de errores dentro del rango observado
- **AND** se declara que la etapa de reglas no emite una confianza utilizable como criterio de derivacion

#### Scenario: Discusion del umbral de 0,70

- **WHEN** se lee el capitulo de discusion
- **THEN** se interpreta la implicancia de la lectura por etapa para el umbral de revision humana de 0,70, de forma coherente con el alcance del gate declarado en el capitulo de arquitectura
- **AND** se conserva el hallazgo de que la etapa Gemini nunca devolvio una confianza inferior a 0,85 en el corpus

## ADDED Requirements

### Requirement: Exactitud por etapa del pipeline en resultados

El capitulo de resultados SHALL reportar la exactitud estricta de cada etapa del pipeline con su IC de Wilson al 95% ---etapa deterministica `97/131`, etapa Gemini `50/69`, etapa fallback sin casos--- y, cuando se disponga de predicciones por caso, tambien su exactitud laxa. La mencion de la distribucion de casos por etapa (131/69/0) SHALL conservarse. Todo valor por etapa MUST figurar en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia.

#### Scenario: Exactitud por etapa presente

- **WHEN** se lee el capitulo de resultados
- **THEN** se reporta la exactitud estricta de la etapa deterministica (0,7405; 97/131) y de la etapa Gemini (0,7246; 50/69), cada una con su IC de Wilson al 95%
- **AND** se declara que la etapa fallback no registro casos

#### Scenario: Valores por etapa trazables

- **WHEN** se compara cada valor por etapa citado en la tesis con el memo de numeros canonicos
- **THEN** cada valor figura en el memo con procedencia y estado `vigente`

### Requirement: Exactitud laxa reportada junto a la estricta

El marco metodologico SHALL definir la exactitud laxa como la proporcion de casos cuyo sector predicho principal pertenece al conjunto de sectores de verdad del caso (sector asignado o sectores adicionales), como metrica secundaria operativa distinta de la exactitud estricta. El capitulo de resultados SHALL reportarla con su IC de Wilson al 95% junto a la exactitud estricta, y la discusion SHALL leerla como la proporcion de derivaciones operativamente aceptables. La exactitud laxa MUST NOT presentarse como metrica primaria ni como cumplimiento del umbral del segundo objetivo especifico: el estado de ese objetivo lo fija la metrica primaria declarada. Si no se dispone de predicciones por caso para calcularla, la tesis SHALL declararla no computable con los artefactos disponibles y MUST NOT consignar un valor estimado.

#### Scenario: Definicion en el marco metodologico

- **WHEN** se lee el analisis estadistico del marco metodologico
- **THEN** la exactitud laxa se define como la pertenencia del sector predicho principal al conjunto de sectores de verdad del caso
- **AND** se la distingue de la exactitud estricta y se la rotula como metrica secundaria

#### Scenario: Valor con intervalo en resultados

- **WHEN** se lee la subseccion de metricas de clasificacion
- **THEN** la exactitud laxa figura con sus aciertos, su proporcion y su IC de Wilson junto a la exactitud estricta
- **AND** su valor no es inferior al de la exactitud estricta (147/200)

#### Scenario: Sin reemplazo de la metrica primaria

- **WHEN** se leen la discusion y las conclusiones
- **THEN** la exactitud laxa no se presenta como metrica primaria ni como evidencia de cumplimiento del umbral del 85% del segundo objetivo especifico

#### Scenario: Exactitud laxa no computable declarada

- **WHEN** las predicciones por caso no estan disponibles al aplicar el change
- **THEN** la tesis declara que la exactitud laxa no es computable con los artefactos disponibles
- **AND** no consigna ningun valor estimado de exactitud laxa

### Requirement: Exactitud de clasificacion por canal de origen

El capitulo de resultados SHALL reportar la exactitud estricta y laxa de clasificacion por canal de origen (llamada telefonica, correo electronico y formulario web), con la cantidad de casos por canal y su IC de Wilson al 95%, en una tabla compacta que reuna los desgloses por etapa y por canal. La discusion SHALL leerla como evidencia de la dimension de calidad del tercer objetivo especifico y del efecto potencial de la transcripcion telefonica, y SHALL advertir que la comparacion entre canales no aisla ese efecto porque la composicion sectorial y la proporcion de casos multietiqueta difieren entre canales. La tesis MUST NOT atribuir causalmente a la transcripcion una diferencia entre canales. Si no se dispone de predicciones por caso, SHALL declararla no computable sin consignar valores.

#### Scenario: Tabla por canal presente

- **WHEN** se lee la subseccion de metricas de clasificacion
- **THEN** una tabla reporta, para cada canal de origen (81, 66 y 53 casos), la exactitud estricta y la laxa con su IC de Wilson
- **AND** la suma de los casos por canal es 200

#### Scenario: Salvedad de composicion entre canales

- **WHEN** se lee la interpretacion de la exactitud por canal en la discusion
- **THEN** se advierte que la composicion sectorial y la proporcion multietiqueta difieren entre canales
- **AND** no se atribuye a la transcripcion telefonica, como causa, una diferencia de exactitud entre canales

#### Scenario: Exactitud por canal no computable declarada

- **WHEN** las predicciones por caso no estan disponibles al aplicar el change
- **THEN** la tesis declara que la exactitud por canal no es computable con los artefactos disponibles
- **AND** no consigna ningun valor de exactitud por canal

### Requirement: Propagacion de la lectura de calibracion por etapa

Los capitulos de discusion (`08-discusion.tex`), conclusiones (`09-conclusiones.tex`) y aspectos eticos y legales (`11-aspectos-legales.tex`) SHALL reflejar la lectura de calibracion por etapa: donde citen el analisis de calibracion o el umbral de 0,70 como salvaguarda, SHALL restringir la afirmacion de no discriminacion a la confianza de la etapa Gemini dentro de su rango observado y declarar que la etapa de reglas no emite una confianza utilizable para derivar. Los rotulos `subsec:calibracion`, `tab:bandas` y `subsec:matriz-metricas` SHALL conservarse, porque otros capitulos los referencian. El change MUST NOT editar la tabla de cumplimiento de objetivos, la tabla de tiempos por canal ni el capitulo de recomendaciones, que pertenecen a otros changes del plan de correccion.

#### Scenario: Discusion y capitulo legal coherentes con la lectura por etapa

- **WHEN** se leen los pasajes de `08-discusion.tex` y `11-aspectos-legales.tex` que citan el analisis de calibracion o el umbral de 0,70
- **THEN** la afirmacion de no discriminacion se restringe a la confianza de la etapa Gemini dentro de su rango observado
- **AND** se declara que la etapa de reglas no emite una confianza utilizable como criterio de derivacion

#### Scenario: Conclusiones con la exactitud por etapa

- **WHEN** se lee el parrafo de conclusiones sobre el clasificador hibrido
- **THEN** se cita la exactitud estricta de cada etapa y, si fueron computables, la exactitud laxa y la exactitud por canal

#### Scenario: Rotulos preservados

- **WHEN** se compila el documento tras el change
- **THEN** los rotulos `subsec:calibracion`, `tab:bandas` y `subsec:matriz-metricas` existen y no hay referencias indefinidas

#### Scenario: Limites con los changes hermanos

- **WHEN** se inspecciona el diff del change sobre las fuentes `.tex`
- **THEN** no se modifican las filas de `tab:cumplimiento-objetivos`, la tabla `tab:tiempos-canal` ni `10-recomendaciones.tex`

### Requirement: Impacto de paginas de las metricas por etapa, canal y exactitud laxa

El change SHALL dejar el PDF compilado en 101 paginas o menos. La reestructuracion de `tab:bandas` SHALL reemplazar la tabla de bandas vigente en lugar de agregar una tabla nueva de bandas, y los desgloses por etapa y por canal SHALL reunirse en una unica tabla compacta. Si tras las compensaciones previstas el PDF supera las 101 paginas, el exceso SHALL registrarse con su causa y la decision final del tope SHALL delegarse al change de integracion de la release (c-141). El change MUST NOT eliminar contenido cientifico, numeros canonicos, figuras ni tablas con linea de fuente para compensar paginas.

#### Scenario: Tope de paginas respetado o exceso registrado

- **WHEN** se compila `main.tex` tras aplicar el change y se cuenta el total de paginas
- **THEN** el total es 101 o menos
- **AND** si es mayor, el exceso y su causa quedan registrados para c-141 sin haberse eliminado contenido cientifico

#### Scenario: Sin tabla de bandas duplicada

- **WHEN** se buscan las tablas de bandas de confianza en `07-resultados.tex`
- **THEN** existe una unica tabla de bandas (`tab:bandas`), desagregada por etapa
