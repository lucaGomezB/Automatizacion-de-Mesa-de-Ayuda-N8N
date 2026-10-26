## MODIFIED Requirements

### Requirement: Consistencia del parrafo introductorio con las columnas de la tabla comparativa del estado del arte

El parrafo introductorio de la tabla comparativa de soluciones (`\label{tab:comparativa}` en `03-estado-del-arte.tex`) SHALL declarar como dimensiones de comparacion exactamente las columnas de la tabla distintas de la clave de fila (`Solucion`), en un numero igual al de esas columnas, y SHALL NOT enunciar como dimension la clave de fila ni una propiedad que no tenga columna propia. La tabla SHALL conservar sus cuatro columnas (Solucion como clave de fila; Despliegue, Clasificacion automatica y Modelo de costo como dimensiones) y su rotulo. La sintesis comparativa posterior a la tabla SHALL NOT afirmar que las soluciones revisadas carecen de una propiedad que la tabla no releva; una propiedad sin columna que se conserve en la prosa SHALL presentarse como rasgo de la propuesta o del contexto y no como resultado de la comparacion.

#### Scenario: Dimensiones declaradas coinciden con las columnas

- **WHEN** se lee el parrafo introductorio de `tab:comparativa` y se cuentan las columnas de la tabla
- **THEN** el numero de dimensiones enunciadas es igual al numero de columnas menos la clave de fila (tres)
- **AND** ni "la solucion considerada" ni otra denominacion de la clave de fila figura entre las dimensiones enumeradas

#### Scenario: Sintesis respaldada por las columnas de la tabla

- **WHEN** se lee la sintesis comparativa posterior a `tab:comparativa`
- **THEN** cada propiedad que la sintesis declara ausente en las soluciones revisadas corresponde a una columna de la tabla
- **AND** el soporte de canales multiples con telefonia y transcripcion automatica no se afirma como carencia de las soluciones revisadas mientras la tabla no tenga una columna que lo releve

#### Scenario: Propiedades sin columna conservadas como prosa

- **WHEN** se leen el parrafo introductorio, la sintesis y el parrafo de posicionamiento posteriores a la tabla
- **THEN** las propiedades relevantes sin columna (por ejemplo, la soberania sobre los datos o el canal telefonico con transcripcion automatica) se mantienen en la prosa circundante como rasgos de la propuesta o del contexto
- **AND** no se elimina del texto ninguna propiedad sustantiva ni se la presenta como resultado de la comparacion

## ADDED Requirements

### Requirement: Cronologia unica y fechada del estudio y de la construccion del artefacto

La tesis SHALL presentar una cronologia unica, en una figura (`\label{fig:cronograma}`) generada desde una fuente Mermaid versionada (`docs/diagrams/cronograma.md`), que feche los periodos de actividad de la construccion bajo Scrumban, la campana de medicion del flujo manual, la campana del flujo automatizado y la integracion de la version del modelo evaluada. Toda mencion textual de esos periodos en `01-introduccion.tex`, `04-marco-metodologico.tex`, `06-implementacion.tex` y `08-discusion.tex` SHALL coincidir con la cronologia. Cada fecha SHALL tener procedencia registrada en la fuente (evidencia verificable del repositorio o confirmacion explicita de los autores, con su fecha) y MUST NOT inventarse, interpolarse ni expresarse con mas precision que su evidencia. La tesis SHALL NOT fijar un numero de iteraciones ni fechas individuales de iteracion mientras no exista fuente primaria o confirmacion de los autores; en ese caso SHALL representar la construccion con la precision disponible (barras de mes).

#### Scenario: Figura de cronograma con fuente reproducible

- **WHEN** se inspeccionan `paper/figures/`, `docs/diagrams/` y las secciones de la tesis
- **THEN** existe `cronograma.png`, generada desde el bloque Mermaid de `docs/diagrams/cronograma.md` y embebida en un entorno `figure` con `\caption` y `\label{fig:cronograma}`
- **AND** la leyenda declara la precision de las fechas y su fuente

#### Scenario: Procedencia de cada fecha

- **WHEN** se revisa la tabla de procedencia de `docs/diagrams/cronograma.md`
- **THEN** cada elemento del cronograma tiene fecha o intervalo, precision (dia o mes) y evidencia (commit, pull request, change archivado o confirmacion de los autores con su fecha)
- **AND** ningun elemento carece de evidencia ni se dibuja con una precision mayor que la de su evidencia

#### Scenario: Menciones textuales conciliadas

- **WHEN** se comparan con la figura las menciones de periodos de `01-introduccion.tex`, `04-marco-metodologico.tex`, `06-implementacion.tex` y `08-discusion.tex`
- **THEN** todas coinciden con la cronologia
- **AND** no subsisten rotulos relativos ("Semanas 1--2" a "Semanas 11--12") ni una duracion total ("12 semanas") que la cronologia no respalde

#### Scenario: Version del modelo fechada en la campana automatizada

- **WHEN** se leen la limitacion sobre la version del modelo en `08-discusion.tex` y la delimitacion temporal de `01-introduccion.tex`
- **THEN** la version evaluada (`gemini-3.6-flash`) se ubica en el periodo de la campana automatizada
- **AND** "junio de 2026" no aparece como fecha de la version evaluada

#### Scenario: Relacion entre iteraciones y campanas explicita

- **WHEN** se lee la seccion de conexion con el proceso Scrumban de `06-implementacion.tex`
- **THEN** se declara que la campana automatizada corresponde a la etapa de validacion experimental y que la campana manual no forma parte de las etapas de construccion
- **AND** ninguna descripcion de iteracion afirma un orden temporal o una condicion incompatible con la cronologia fechada (por ejemplo, ajustes del clasificador declarados sin exposicion al corpus pero fechados despues de su procesamiento)

#### Scenario: Entregable de iteración coherente con la fecha de su artefacto

- **WHEN** se leen la lista de iteraciones de `06-implementacion.tex` (subsec:conexion-scrumban) y la lista de §4.9 de `04-marco-metodologico.tex`
- **THEN** cada entregable concreto atribuido a una iteración existe y su fecha de creación o de archivo (según `docs/diagrams/cronograma.md` y la historia de `openspec/changes/archive/`) cae dentro de la ventana declarada de esa iteración
- **AND** ningún artefacto creado después de la ventana (en particular el documento de arquitectura de `knowledge-base/` del 2026-06-10 y el contrato OpenAPI estático del 2026-06-11) se atribuye a la iteración 1

### Requirement: Parrafo introductorio del capitulo de resultados coherente con sus subsecciones

El parrafo introductorio de `07-resultados.tex` SHALL enumerar exactamente las subsecciones del capitulo, en su orden y con denominaciones coherentes con sus titulos, y SHALL NOT anunciar como dimension de los resultados una magnitud que el propio capitulo declara no medida. Si el parrafo usa un cardinal, este MUST coincidir con el numero de subsecciones.

#### Scenario: Enumeracion igual a las subsecciones

- **WHEN** se cuentan los `\subsection` de `07-resultados.tex` y las dimensiones enumeradas en su parrafo introductorio
- **THEN** ambos conjuntos coinciden en numero y en orden
- **AND** ninguna subseccion queda sin mencion

#### Scenario: Intervencion humana sin reduccion afirmada

- **WHEN** se lee el parrafo introductorio del capitulo de resultados
- **THEN** la dimension correspondiente se denomina "intervencion humana" o con otra denominacion neutra coherente con el titulo de su subseccion
- **AND** no se anuncia una "reduccion de la intervencion humana"

### Requirement: Completitud de las metricas de la tabla de trabajos academicos

La tabla `tab:trabajos-academicos` SHALL consignar en la columna "Metrica reportada" de cada trabajo la cifra principal que su resumen o su texto completo accesible reporten textualmente (nombre de la metrica, valor y modelo o condicion), y en "Corpus/idioma" el tamano y el idioma cuando la fuente los establezca. La leyenda "no reportado en el alcance revisado" SHALL quedar solo en las celdas cuya fuente accesible no consigne el dato, acompanada de su motivo abreviado. Cada celda completada SHALL tener su procedencia (DOI o URL consultada, fecha de consulta y ubicacion en la fuente) registrada en `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`. El documento MUST NOT recalcular, promediar ni inferir cifras, y MUST NOT agregar entradas a `Bibliography_base.bib`.

#### Scenario: Metricas completadas desde la fuente

- **WHEN** se contrasta cada celda de metrica de `tab:trabajos-academicos` con su registro de procedencia
- **THEN** el valor consignado coincide textualmente con el de la fuente registrada
- **AND** la celda identifica la metrica, el valor y el modelo o la condicion a que corresponde

#### Scenario: Residuo no reportado justificado

- **WHEN** una celda conserva "no reportado en el alcance revisado"
- **THEN** el registro de procedencia documenta que el resumen no consigna el dato y que el texto completo no fue accesible o tampoco lo consigna
- **AND** la celda declara ese motivo de forma abreviada

#### Scenario: Sin altas bibliograficas ni citas huerfanas

- **WHEN** se ejecuta `verify_citations.py` y se inspecciona el diff de `Bibliography_base.bib` tras completar la tabla
- **THEN** no hay citas huerfanas ni entradas sin usar
- **AND** `Bibliography_base.bib` no tiene cambios atribuibles a este cambio

### Requirement: Salvedad de cota inferior del tiempo telefonico en las conclusiones

Toda mencion del tiempo automatizado del canal telefonico en `09-conclusiones.tex` SHALL acompanarse de la salvedad de que el valor es una cota inferior de la duracion real de la llamada por el tope de 45 s de la grabacion, en coherencia con `04-marco-metodologico.tex` (`subsec:metricas-instrumentos`), `06-implementacion.tex` y `07-resultados.tex`. El valor reportado (20,1 s) MUST NOT cambiar.

#### Scenario: Cota inferior declarada en las conclusiones

- **WHEN** se lee la mencion del canal telefonico en `09-conclusiones.tex`
- **THEN** el texto declara que los 20,1 s son una cota inferior por el tope de 45 s de grabacion
- **AND** el valor coincide con el de `tab:tiempos-canal` redondeado (20,09 s)

#### Scenario: Coherencia entre capitulos

- **WHEN** se comparan las menciones del tiempo telefonico en metodologia, implementacion, resultados y conclusiones
- **THEN** todas declaran la condicion de cota inferior
- **AND** ninguna presenta el valor como la duracion completa de la llamada

### Requirement: Coherencia del Anexo H con el capitulo 5 sobre los parametros de inferencia

La descripcion de los parametros de inferencia en el Anexo H (`subsec:anexo-parametros-config` y `tab:anexo_gemini_params` de `12-anexos.tex`) SHALL ser coherente con la de `05-arquitectura.tex` (`subsec:capa-procesamiento`): los parametros SHALL presentarse como la configuracion adoptada para el despliegue y SHALL NOT calificarse como optimizados mientras no se documente un procedimiento de optimizacion con los valores alternativos evaluados. El cambio MUST NOT alterar los valores de los parametros salvo el tiempo de espera, que se rige por el requisito "Tiempo de espera de la inferencia coherente con la configuracion vigente durante la campana", ni introducir otras cifras.

#### Scenario: Sin calificativo de optimizacion en el Anexo H

- **WHEN** se leen la prosa de `subsec:anexo-parametros-config`, la leyenda y las filas de `tab:anexo_gemini_params`
- **THEN** no se afirma que los parametros esten optimizados ni que un valor optimice la latencia, la exactitud o el costo
- **AND** los parametros se describen como configuracion adoptada, en coherencia con `subsec:capa-procesamiento`

#### Scenario: Valores sin cambios salvo el tiempo de espera

- **WHEN** se comparan los valores de `tab:anexo_gemini_params` antes y despues del cambio
- **THEN** los valores de temperatura, top_p, max_tokens, candidate_count, safety_settings y version del SDK permanecen iguales
- **AND** el unico valor modificado es el del tiempo de espera, y no se agrega ninguna otra cifra a la prosa ni a la tabla

### Requirement: Tiempo de espera de la inferencia coherente con la configuracion vigente durante la campana

Las menciones del tiempo de espera de la inferencia con Gemini en `05-arquitectura.tex` (`subsec:capa-procesamiento`) y en la fila `timeout` de `tab:anexo_gemini_params` (`12-anexos.tex`) SHALL coincidir con la configuracion vigente durante la campana automatizada, determinada por `App/Backend/app/config/settings.py` y su historia en git: 30 s por intento (`gemini_timeout_seconds`, desde el commit `11036be`, 2026-09-24) y 60 s de presupuesto total por clasificacion (`gemini_total_timeout_seconds`, desde el commit `429f2c9`, 2026-09-29), salvo que los autores declaren un override aplicado durante la campana, que prevalece y se registra. El valor de 10 s MUST NOT presentarse como el del sistema evaluado. La procedencia SHALL registrarse en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`. El cambio MUST NOT introducir cifras que no surjan de `settings.py`, de la historia del repositorio o de la declaracion registrada de los autores.

#### Scenario: Tiempo de espera alineado en el capitulo 5 y en el Anexo H

- **WHEN** se leen `subsec:capa-procesamiento` en `05-arquitectura.tex` y la fila `timeout` de `tab:anexo_gemini_params`
- **THEN** ambas declaran el tiempo de espera por intento y el presupuesto total vigentes durante la campana (30 s y 60 s, salvo override registrado)
- **AND** ninguna mencion de la tesis presenta 10 s como el tiempo de espera del sistema evaluado

#### Scenario: Procedencia registrada en el memo de conteos tecnicos

- **WHEN** se revisa `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`
- **THEN** figuran como `vigente` el tiempo de espera por intento y el presupuesto total, con archivo y linea de `settings.py` y el commit que los introdujo, y el valor de 10 s como `retirado`
- **AND** la seccion de alineacion lista los cambios de `05-arquitectura.tex` y `12-anexos.tex` (ANTES y DESPUES)

#### Scenario: Reintentos del modelo distinguidos de la invocacion de N8N

- **WHEN** se lee la descripcion del tiempo de espera por intento junto con la seccion de desafios de integracion de `06-implementacion.tex`
- **THEN** queda claro que los intentos se refieren a la invocacion del backend al modelo
- **AND** la descripcion no contradice la afirmacion de que la invocacion de N8N al backend no tiene reintentos

#### Scenario: Archivos de configuracion de agentes sin cambios

- **WHEN** se inspecciona el diff del cambio
- **THEN** `CLAUDE.md` y `openspec/config.yaml` no tienen modificaciones atribuibles a este cambio
- **AND** la nota de coordinacion con c-130 sobre esos archivos figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

### Requirement: Neutralidad de paginas de las correcciones de cronologia y consistencia

La aplicacion de este cambio SHALL ser neutral en paginas: el total del PDF compilado despues del cambio MUST ser menor o igual que el total medido inmediatamente antes de aplicarlo, contado sobre el documento completo. La figura de cronograma SHALL compensarse con palancas de forma admitidas (condensar la lista redundante de iteraciones de la seccion Scrumban de `04-marco-metodologico.tex`, limitar el alto de la figura, redacciones de longitud neutra) sin eliminar contenido cientifico.

#### Scenario: Total de paginas sin aumento

- **WHEN** se compila `main.tex` antes y despues del cambio con la misma cadena (XeLaTeX y biber) y se cuentan las paginas del PDF completo
- **THEN** el total posterior es menor o igual que el anterior
- **AND** ambos conteos quedan registrados en las tareas

#### Scenario: Compensacion sin perdida de contenido

- **WHEN** se compara la seccion Scrumban de `04-marco-metodologico.tex` antes y despues del cambio
- **THEN** la lista de iteraciones condensada remite a la seccion de conexion con Scrumban y a la figura, donde se conserva el detalle de cada iteracion
- **AND** la demarcacion entre el metodo de investigacion y el metodo de construccion permanece

#### Scenario: Compilacion sin errores

- **WHEN** se compila con `latexmk` (XeLaTeX)
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** el registro no contiene referencias indefinidas ni etiquetas definidas mas de una vez
