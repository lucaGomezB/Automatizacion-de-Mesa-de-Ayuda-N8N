## ADDED Requirements

### Requirement: Regla de tres vias asimetrica declarada en la introduccion y en la metodologia

La introduccion y el marco metodologico SHALL declarar de forma expresa que la regla de tres vias de la segunda sub-hipotesis es asimetrica: la rama de refutacion se decide con la estimacion puntual y no con el intervalo, de modo que basta que la estimacion alcance o supere la cota de 0,15. Ambos pasajes SHALL declarar que el denominador de 147 casos revisados se adopto despues de conocer los datos. La declaracion MUST NOT cambiar la cota, la regla ni el veredicto de la sub-hipotesis.

#### Scenario: La introduccion declara la asimetria

- **WHEN** se lee la sub-hipotesis de intervencion humana en `01-introduccion.tex`
- **THEN** el texto dice que la regla es asimetrica y que la refutacion se decide con la estimacion puntual sin usar el intervalo
- **AND** declara que el denominador de 147 casos se adopto despues de conocer los datos

#### Scenario: La metodologia declara la asimetria

- **WHEN** se lee el parrafo de analisis de la campana complementaria en `04-marco-metodologico.tex`
- **THEN** el texto dice que la regla es asimetrica y que la refutacion se decide con la estimacion puntual sin usar el intervalo
- **AND** conserva la constancia de que el denominador se adopto despues de conocer los datos

### Requirement: Enunciado y veredicto separados y umbral del 85 por ciento unificado

En `01-introduccion.tex`, cada sub-hipotesis SHALL quedar enunciada con su contraste y su criterio de falsacion, sin incluir su veredicto ni los resultados observados; el veredicto pertenece a resultados y conclusiones. El umbral de desempeno del 85 por ciento SHALL presentarse como criterio de exito central del estudio, fijado a priori por los autores, y MUST NOT presentarse como un valor tomado de la literatura ni degradarse a criterio no definitorio del objetivo.

#### Scenario: Introduccion sin veredictos

- **WHEN** se buscan en las sub-hipotesis de `01-introduccion.tex` las expresiones de veredicto "se declara confirmada", "se declara refutada" o "se declara no concluyente"
- **THEN** no aparecen en el enunciado de las sub-hipotesis
- **AND** el texto remite a resultados o conclusiones para el veredicto

#### Scenario: Umbral como criterio central

- **WHEN** se lee el segundo objetivo especifico en `01-introduccion.tex`
- **THEN** el umbral del 85 por ciento se declara criterio de exito del objetivo, fijado a priori por los autores
- **AND** no se lo describe como "criterio de exito contingente" ni como ajeno a la definicion del objetivo
- **AND** la literatura se describe como incapaz de fijar un piso comun, sin atribuirle el valor del umbral

### Requirement: Objetivos primero y tercero consistentes con la implementacion y medibles

El primer objetivo especifico SHALL describir la comunicacion entre componentes como sincronica, consistente con la implementacion y con las conclusiones. El tercer objetivo especifico MUST NOT exigir una reduccion de la complejidad operativa percibida si no existe metrica ni instrumento para medirla.

#### Scenario: Objetivo 1 sincronico

- **WHEN** se lee el primer objetivo especifico en `01-introduccion.tex`
- **THEN** describe comunicacion sincronica entre componentes por interfaces REST sobre HTTP cifrado
- **AND** no la describe como asincronica

#### Scenario: Objetivo 3 sin clausula no medible

- **WHEN** se lee el tercer objetivo especifico en `01-introduccion.tex`
- **THEN** integra los tres canales en un unico flujo que normaliza la entrada y centraliza el procesamiento
- **AND** no exige "sin incrementar la complejidad operativa percibida por los usuarios finales"

### Requirement: Cuerpo sin prosa de versiones ni rutas internas y Anexo I reducido

El cuerpo SHALL NOT contener la frase "una version anterior de esta tesis la declaro refutada" ni rutas internas del repositorio en el protocolo de revision del estado del arte. El Anexo I SHALL reducir la reproduccion de los dictamenes a una nota breve de versiones y conservar la divulgacion de asistencia de un modelo de lenguaje. La reduccion MUST NOT eliminar las etiquetas `sec:anexo-trazabilidad` ni `subsec:nota-versiones` de las que dependen remisiones externas.

#### Scenario: Sin prosa de versiones en el cuerpo

- **WHEN** se busca "version anterior de esta tesis" en `01-introduccion.tex` y `04-marco-metodologico.tex`
- **THEN** no hay coincidencias
- **AND** `03-estado-del-arte.tex` no contiene la ruta `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md`

#### Scenario: Anexo I reducido sin romper remisiones

- **WHEN** se lee el Anexo I en `12-anexos.tex`
- **THEN** conserva la nota de versiones y un parrafo breve de trazabilidad
- **AND** no reproduce las tablas de los nueve dictamenes ni la tabla de la devolucion de segunda instancia
- **AND** las etiquetas `sec:anexo-trazabilidad` y `subsec:nota-versiones` siguen existiendo

### Requirement: Fundamentos teoricos del acuerdo entre anotadores, la clasificacion multietiqueta y las pruebas estadisticas

El marco teorico SHALL presentar, antes de la metodologia, el acuerdo entre anotadores y el coeficiente kappa, la clasificacion multietiqueta y las pruebas estadisticas empleadas en la tesis (Wilcoxon, intervalos de Wilson, bootstrap y McNemar). Las citas SHALL usar claves existentes en `Bibliography_base.bib`.

#### Scenario: Conceptos presentes en el marco teorico

- **WHEN** se lee `02-marco-teorico.tex`
- **THEN** contiene una subseccion sobre acuerdo entre anotadores y coeficiente kappa
- **AND** contiene una subseccion sobre clasificacion multietiqueta
- **AND** contiene una subseccion sobre las pruebas estadisticas empleadas

#### Scenario: Citas sin huerfanas

- **WHEN** se ejecuta el verificador de citas
- **THEN** el estado es PASS con cero citas huerfanas y cero entradas sin usar

### Requirement: Ubicacion del capitulo de aspectos legales justificada

El capitulo de consideraciones eticas y legales SHALL conservar su posicion entre implementacion y resultados y SHALL declarar en una oracion por que esa posicion es pertinente. No se exige mover el capitulo ni renumerar secciones.

#### Scenario: Justificacion explicita

- **WHEN** se lee el inicio de `11-aspectos-legales.tex`
- **THEN** una oracion explica que el capitulo se ubica entre implementacion y resultados porque el marco legal y etico condiciona la lectura de la evidencia
- **AND** el orden de los `\input` de `main.tex` no cambia

### Requirement: Metadatos bibliograficos de la release y de los tipos de entrada

La entrada del repositorio propio SHALL declarar la version 1.3.0. Las entradas de PMLR cargadas como `@article` SHALL tipificarse como `@inproceedings` conservando sus datos. La atribucion a Zanzotto SHALL indicar la pagina 243. Los DOI de las entradas de 2025 y 2026 SHALL resolver contra su editor y MUST NOT modificarse sin verificacion.

#### Scenario: Version del repositorio

- **WHEN** se lee la entrada `Gomez2026_repositorio` en `Bibliography_base.bib`
- **THEN** declara la version 1.3.0

#### Scenario: Actas tipificadas como proceedings

- **WHEN** se leen las entradas `Radford2023_whisper`, `Guo2017_calibration` y `Zhao2021_calibrate_before_use`
- **THEN** estan tipificadas como `@inproceedings` con su `booktitle`
- **AND** conservan volumen, paginas y URL

#### Scenario: Pagina de Zanzotto

- **WHEN** se busca la atribucion a Zanzotto en `02-marco-teorico.tex`
- **THEN** la cita indica la pagina 243

### Requirement: Glosario completado con iPaaS, SaaS, kNN y CoT

El glosario SHALL incluir iPaaS, SaaS, kNN y CoT con su expansion, conservando el orden alfabetico de sus columnas.

#### Scenario: Siglas presentes

- **WHEN** se buscan las entradas `iPaaS`, `SaaS`, `kNN` y `CoT` en `00-glosario.tex`
- **THEN** las cuatro existen con su expansion
- **AND** el orden alfabetico de cada columna se conserva

### Requirement: Vacancia del corpus en espanol acotada a la evidencia

La afirmacion sobre la ausencia de trabajos con corpus en espanol SHALL formularse como una ausencia relativa al alcance revisado, reconociendo que el idioma no se informa en la mayoria de los trabajos relevados y que entre los que lo consignan ninguno declara espanol. MUST NOT afirmarse que ningun trabajo declara un corpus en espanol como si fuera una constatacion sobre toda la literatura.

#### Scenario: Afirmacion acotada

- **WHEN** se lee la justificacion academica en `01-introduccion.tex`
- **THEN** el texto dice que el idioma del corpus no se informa en la mayoria de los trabajos relevados
- **AND** acota la ausencia al alcance revisado
- **AND** no afirma de forma absoluta que ningun trabajo declara un corpus en espanol
