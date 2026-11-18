## ADDED Requirements

### Requirement: Muestra probabilistica del universo incorporada solo en una version posterior a la defensa

Este requisito SHALL aplicarse solo en una version de la tesis posterior a la defensa y solo si se
cumplen cuatro condiciones: existe un marco completo verificado (PS-001), la campana probabilistica se
ejecuto, el acta de la compuerta de procedencia (PS-003) y la documentacion de la compuerta etica y
legal (PS-004) de `evaluation-probabilistic-sampling` estan cerradas, y existe la estimacion de PS-006.
Si alguna falta, la tesis MUST NOT mencionar el diseno mas alla de lo que ya fijan los requisitos de
trabajo futuro y de remedio empirico condicional. Cumplidas las condiciones: `subsec:poblacion-muestra-corpus` SHALL
describir la muestra probabilistica como distinta del corpus de 200 casos, que SHALL seguir descrito
como muestra por conveniencia; una subseccion nueva de `07-resultados.tex` (etiqueta propuesta
`subsec:muestra-probabilistica`) SHALL informar la exactitud ponderada y la cruda rotuladas, el DEFF,
el IC con su metodo, las cuotas alcanzadas y las clases declaradas no estimables; la quinta amenaza de
`subsec:amenazas-validez` SHALL precisar que la estimacion se refiere al universo del periodo del
entorno operativo del propio equipo y no a otras organizaciones; `subsec:corpus-independiente` SHALL
conservar los elementos que exige su requisito vigente y agregar una remision a la subseccion de
resultados nueva; `11-aspectos-legales.tex` SHALL declarar la base de licitud por regimen
(consentimiento informado del grupo para el regimen (a); sin datos personales para el regimen (b)), el
consentimiento de los etiquetadores y, en `subsec:transferencia-internacional`, los textos de la
muestra enviados a proveedores con su cantidad, o que no se enviaron. La tesis SHALL declarar que el
diseno no eleva la exactitud del clasificador sino que hace valida la estimacion. El texto MUST NOT
reintroducir cifras, alias de etiquetadores ni descripciones del corpus retirado del ejemplar, MUST NOT
cambiar el valor de ninguna cifra canonica del corpus de 200 y MUST NOT introducir identificadores
`c-NNN` en el cuerpo.

#### Scenario: Sin marco, campana o compuertas, la tesis no cambia

- **WHEN** falta el marco completo, la campana, el acta de procedencia o la documentacion etica y legal
- **THEN** ninguna seccion de la tesis describe la muestra probabilistica como realizada
- **AND** solo figuran las menciones de trabajo futuro y remedio condicional vigentes

#### Scenario: Resultados en subseccion nueva

- **WHEN** se lee la version posterior a la defensa con la campana ejecutada
- **THEN** `subsec:muestra-probabilistica` informa exactitud ponderada y cruda rotuladas, DEFF, IC, cuotas alcanzadas y clases no estimables
- **AND** el corpus de 200 sigue descrito como muestra por conveniencia con sus cifras canonicas intactas

#### Scenario: Transferencias y consentimiento declarados

- **WHEN** se lee el capitulo 7 de esa version
- **THEN** figuran la base de licitud por regimen, el consentimiento del grupo y de los etiquetadores, y los textos enviados a proveedores con su cantidad, o la declaracion de que no se enviaron

#### Scenario: Sin evidencia retirada

- **WHEN** se busca en `sections/*.tex` de esa version alguna cifra o alias de etiquetador de la evidencia retirada fuera de la nota de versiones
- **THEN** no hay coincidencias atribuibles a este change

## MODIFIED Requirements

### Requirement: Validez externa declarada en las conclusiones con su remedio empirico

Las conclusiones SHALL declarar la amenaza a la validez externa con la fuerza que el diseno permite: la muestra es **no probabilistica por conveniencia** (los 200 casos son los incidentes cronometrados), proviene de **un unico entorno operativo** (sector servicios, provincia de Mendoza; presentado como escenario de referencia narrativo, NO como una organizacion real) y el universo es **proyectado, no medido** (`2.646 = 42 x 63`), de modo que las cifras valen para este corpus y no se extrapolan al universo de incidentes. La declaracion SHALL senalar que el remedio empirico es el **diseno de muestreo probabilistico del universo** (change `c-229`), SHALL presentarlo como **condicional y no ejecutado** y MUST NOT afirmar que la validez externa ya fue establecida. En una version posterior a la defensa con el marco completo verificado y la campana ejecutada con sus compuertas de procedencia y etica/legal cerradas, SHALL presentarlo como ejecutado, con remision a sus resultados, y SHALL acotar su alcance al universo del periodo del entorno operativo del propio equipo: MUST NOT afirmar validez externa respecto de otras organizaciones, sectores o regiones. La correccion MUST NOT cambiar el valor de ningun numero canonico, salvo lo que los autores ratifiquen sobre la proyeccion del universo.

#### Scenario: Fuerza correcta en la conclusion

- **WHEN** se leen las conclusiones (`09-conclusiones.tex`)
- **THEN** el texto declara la muestra no probabilistica por conveniencia, el unico entorno operativo (escenario de referencia narrativo) y el universo proyectado (`2.646 = 42 x 63`)
- **AND** las cifras se declaran validas para este corpus y no extrapolables al universo

#### Scenario: Remedio empirico declarado como condicional

- **WHEN** se lee la declaracion de validez externa y el diseno no se ejecuto con sus compuertas cerradas
- **THEN** remite al diseno de muestreo probabilistico (change `c-229`) como remedio empirico
- **AND** lo presenta como condicional y no ejecutado, sin afirmar que la validez externa ya esta establecida

#### Scenario: Remedio ejecutado con alcance acotado

- **WHEN** se lee una version posterior a la defensa con el marco completo verificado y la campana ejecutada con las compuertas cerradas
- **THEN** la declaracion remite a los resultados de la muestra probabilistica y acota su alcance al universo del periodo del entorno operativo del propio equipo
- **AND** no afirma validez externa respecto de otras organizaciones, sectores o regiones

#### Scenario: Valores canonicos intactos

- **WHEN** se compara el `.tex` antes y despues del change
- **THEN** ningun valor canonico cambia de valor
- **AND** las unicas diferencias son palabras y remisiones de procedencia

#### Scenario: Sin organizacion real en la conclusion

- **WHEN** se lee la declaracion de validez externa de las conclusiones
- **THEN** no se presenta el entorno como una organizacion real ni como una organizacion adoptante
- **AND** la limitacion se declara sobre el escenario de referencia narrativo

### Requirement: Seleccion de los casos por conveniencia declarada

La seccion 4.4 (`subsec:poblacion-muestra-corpus`) SHALL describir una sola forma de seleccion de
los 200 casos: muestreo no probabilistico por conveniencia (disponibilidad), siendo los 200 casos
los incidentes cronometrados en la campaña manual; la formula de tamaño muestral SHALL informarse
como margen de error implicado y no como diseño. La tesis MUST NOT describir el corpus de 200 casos
como muestreo estratificado ni con asignacion proporcional en `04-marco-metodologico.tex`, el
resumen, el abstract ("convenience sample") ni la discusion. Solo en una version posterior a la
defensa con la muestra probabilistica ejecutada y sus compuertas cerradas, la tesis MAY describir
como estratificada esa muestra nueva, siempre identificada como distinta del corpus de 200 casos.
La seccion 4.8 SHALL incluir el sesgo de seleccion como amenaza a la validez externa. Las fechas del
periodo relevado y el criterio de seleccion MUST NOT inventarse: quedan marcados
`PENDIENTE-AUTORES(N-04)` hasta que los autores los aporten.

#### Scenario: Una sola descripcion

- **WHEN** se busca "estratificad" o "stratified" en `00-resumen.tex`, `04-marco-metodologico.tex` y `08-discusion.tex`
- **THEN** no hay coincidencias afirmativas referidas al corpus de 200 casos (una negacion explicita se cuenta aparte)
- **AND** 4.4 y el abstract nombran el muestreo por conveniencia

#### Scenario: Muestra nueva distinguida

- **WHEN** una version posterior a la defensa describe como estratificada la muestra probabilistica
- **THEN** el texto la identifica como distinta del corpus de 200 casos
- **AND** el corpus de 200 casos sigue descrito como muestra por conveniencia

#### Scenario: Sesgo de seleccion en 4.8

- **WHEN** se lee `subsec:amenazas-validez`
- **THEN** figura el sesgo de seleccion como amenaza a la validez externa
