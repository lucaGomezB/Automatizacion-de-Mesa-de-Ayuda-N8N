## MODIFIED Requirements

### Requirement: Estado de la segunda sub-hipotesis coherente con la variable medida

El estado de la segunda sub-hipotesis SHALL fundarse en un denominador de casos que tuvieron
oportunidad de revision humana, segun la lectura que los autores adopten y registren en
`docs/Tesis/Correcciones/dictamen-correcciones.md` (design D1 de c-190): (A) "refutada", con
25 de 147 casos revisados (17,0 %; IC de Wilson [11,8 %; 23,9 %]), informando 25 de 200 como
dato secundario con la advertencia de que cuenta 53 casos web sin revision; (B) "no
contrastable en esta campaña", porque la regla del reportante determino que casos se
revisaban; o (C) ambos denominadores con el veredicto que la regla de tres vias da a cada uno.
El texto SHALL declarar que la revision humana de la campaña complementaria alcanzo solo los
canales de correo (66) y telefonia (81) por la regla de derivacion por reportante no
identificado, y que los 53 casos del formulario web no tuvieron revision. El estado MUST NOT
ser "no concluyente" fundado unicamente en 25 de 200. Se conserva la declaracion de que la
tasa bruta (147 de 200) no es compatible con la cota de 0,15 pero refleja la regla de
derivacion por reportante de la configuracion de la prueba. Ese estado SHALL ser identico en
el resumen, el abstract, la seccion 1.4 (`01-introduccion.tex`), la seccion 4.7
(`04-marco-metodologico.tex`), la seccion 8.3 (`subsec:reduccion-intervencion`), la seccion
9.1 (`08-discusion.tex`), el parrafo inicial y la sintesis del objetivo especifico 4 de la
seccion 10 (`09-conclusiones.tex`), la Tabla 18 (`tab:cumplimiento-objetivos`, filas del
objetivo general y del objetivo especifico 4) y la seccion 11.3
(`subsec:medicion-intervencion`). La seccion 9.1 SHALL mencionar la segunda sub-hipotesis al
resumir el estado de la hipotesis principal. La Tabla 18 MUST NOT apoyar el objetivo general
ni el objetivo especifico 4 en una intervencion "medida y refutada" por la tasa bruta. La
seccion 11.3 MUST NOT presentar el 73,5 % como defecto del clasificador a reducir y SHALL
proponer la medicion de la variable con reportantes identificados. El resumen y el abstract
MUST NOT contener un parentesis "(73,5 %, IC [67,0 %, 79,1 %])" cuya magnitud pueda
confundirse con la exactitud estricta (tambien 147/200), y SHALL nombrar el denominador de la
cifra de intervencion que informen.

#### Scenario: Estado unico de la sub-hipotesis 2

- **WHEN** se comparan el resumen, el abstract, 1.4, 4.7, 8.3, 9.1, el capitulo 10, la Tabla 18 y 11.3
- **THEN** todos declaran el mismo estado de la sub-hipotesis 2 con el mismo denominador, segun la opcion registrada
- **AND** ninguno la declara "no concluyente" con 25 de 200 como unico fundamento
- **AND** ninguno la declara "refutada" por la tasa de 73,5 %

#### Scenario: Alcance de la revision declarado

- **WHEN** se lee 8.3
- **THEN** se declara que la revision humana alcanzo 66 casos de correo y 81 de telefonia y ninguno de los 53 del formulario web
- **AND** se declara que la regla del reportante determino que casos se revisaban

#### Scenario: Resumen sin ambiguedad de magnitud

- **WHEN** se lee la oracion del resumen y del abstract que enuncia los estados por sub-hipotesis
- **THEN** la cifra de intervencion nombra su magnitud y su denominador
- **AND** no queda un parentesis con 73,5 % y [67,0 %, 79,1 %] adyacente a la intervencion humana

#### Scenario: 11.3 reformulada

- **WHEN** se lee `subsec:medicion-intervencion`
- **THEN** no aparece "respecto del 73,5 %" como meta de reduccion
- **AND** se propone medir la variable con reportantes identificados en el directorio

## ADDED Requirements

### Requirement: Cotejo de las revisiones humanas de la campaña con el consenso

La seccion 8.3 SHALL informar, como dato y sin lectura causal, el cotejo de las revisiones de
la campaña complementaria con el consenso `E1 = E2` de `doble_etiquetado.csv`: de las 85
confirmaciones con consenso disponible, 11 confirmaron un sector que el consenso considera
incorrecto; de los 25 cambios de derivacion, 13 tienen consenso (9 correcciones, 1
empeoramiento, 3 de un error a otro). Las cifras SHALL reproducirse antes de escribirse con un
cruce de `intervenciones.csv` y `doble_etiquetado.csv` y registrarse en
`docs/Tesis/Correcciones/numeros-canonicos.md` con su fuente.

#### Scenario: Cotejo informado

- **WHEN** se lee 8.3
- **THEN** figuran 11 de 85 confirmaciones contra el consenso y 13 cambios con consenso desglosados en 9, 1 y 3
- **AND** el texto no atribuye causa a esas cifras

#### Scenario: Cifras registradas

- **WHEN** se busca el cotejo en `numeros-canonicos.md`
- **THEN** figura cada cifra con el archivo fuente y el criterio de cruce

### Requirement: Enmascaramiento de los operadores coherente con su condicion de autor

La descripcion de la proteccion contra el efecto Hawthorne SHALL ser compatible con la
identidad de los operadores del brazo manual de la campaña 2026-10 que declaran las secciones
4.4, 4.8 y 9.3. Si uno de esos operadores es autor del trabajo (`T1` en
`registro_sujetos.csv`), la seccion 4.2 (`subsec:diseno-experimental`) y la seccion 7.5
(`11-aspectos-legales.tex`, sesion de esclarecimiento) MUST NOT afirmar que a ambos operadores
se les oculto el proposito comparativo ni que ambos lo conocieron en el *debriefing*; SHALL
declarar que el enmascaramiento opero, a lo sumo, para el operador externo. La amenaza del
efecto Hawthorne en 4.8 y la explicacion rival de 9.1 (`08-discusion.tex`) SHALL incorporar esa
condicion. Si los operadores de 2026-10 no son esos analistas, SHALL corregirse 4.4, 4.8 y 9.3
y conservarse 4.2. La tesis MUST NOT incluir datos personales de los sujetos: solo codigos y
roles.

#### Scenario: Sin enmascaramiento imposible

- **WHEN** se comparan 4.2, 4.4, 4.8, 7.5, 9.1 y 9.3
- **THEN** ningun pasaje afirma que un operador autor desconocia el proposito comparativo o fue informado de el en el *debriefing*
- **AND** la descripcion de los operadores es la misma en todos los pasajes

#### Scenario: Amenaza Hawthorne actualizada

- **WHEN** se lee la amenaza del efecto Hawthorne en 4.8 y la explicacion rival en 9.1
- **THEN** ambas declaran el alcance del enmascaramiento efectivo (a lo sumo un operador) o la correccion adoptada

### Requirement: Nota de fuente de la Tabla 19 verificable contra el repositorio

La nota de fuente de `tab:configuracion-evaluada-entregada` (`12-anexos.tex`) MUST NOT
afirmar que entre la revision de la campaña complementaria (`cda7712`) y la entregada solo
difiere `docker-compose.yml`. SHALL declarar que no cambian `requirements.txt`,
`package-lock.json`, `n8n/workflow.json` ni `settings.py`, y que si cambian
`docker-compose.yml` y `docker/n8n/` (imagen derivada) y archivos del backend y del frontend
que no intervienen en la clasificacion. El conteo (24 archivos con `git diff --stat cda7712
v1.2.12 -- App/ n8n/ docker/ docker-compose.yml`) SHALL registrarse en
`docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` con el comando.

#### Scenario: Nota acotada

- **WHEN** se busca "solo" junto a `docker-compose.yml` en la nota de la Tabla 19
- **THEN** no aparece la afirmacion de que solo ese archivo difiere
- **AND** la nota nombra los cuatro archivos de pines sin cambios

#### Scenario: Conteo reproducible

- **WHEN** se ejecuta el comando registrado en `conteos-canonicos-tecnicos.md`
- **THEN** informa 24 archivos y vacio sobre los cuatro archivos de pines

### Requirement: Descripcion unica del canal telefonico y modelo de transcripcion declarado

Las secciones 5.2 (`05-arquitectura.tex`), 6.4 y 6.6 (`06-implementacion.tex`) SHALL describir
el canal telefonico de la misma manera: Twilio graba la llamada y notifica la grabacion al
backend, que la transcribe con la Gemini API. La tesis MUST NOT atribuir la transcripcion al
servicio de reconocimiento del habla de Twilio ni mencionar un "webhook de transcripcion" hacia
N8N. El modelo de transcripcion (`gemini-3.5-transcribe`, `settings.py` del tag) SHALL
declararse en 6.4, en la Tabla 19 y en el Anexo H, y la seccion 9.5 SHALL declarar su exclusion
del calculo economico. El diagrama de despliegue SHALL mostrar el uso de la Gemini API para la
transcripcion, y su leyenda SHALL nombrar las redes Docker que la figura dibuja.

#### Scenario: Canal telefonico coherente

- **WHEN** se buscan "reconocimiento del habla del proveedor" y "webhook de transcripción" en `sections/`
- **THEN** no hay coincidencias
- **AND** 5.2, 6.4 y 6.6 describen la misma secuencia grabacion -> callback -> transcripcion en el backend

#### Scenario: Modelo de transcripcion declarado

- **WHEN** se busca `gemini-3.5-transcribe` en 6.4, en la Tabla 19 y en el Anexo H
- **THEN** figura en los tres lugares y coincide con `git show v1.2.12:App/Backend/app/config/settings.py`
- **AND** 9.5 declara que su costo queda fuera del calculo

#### Scenario: Despliegue actualizado

- **WHEN** se inspecciona `figures/despliegue.png` y su leyenda
- **THEN** la arista hacia la Gemini API incluye la transcripcion
- **AND** la leyenda no dice "red Docker" en singular

### Requirement: Procedencia declarada de las cifras de la campaña complementaria

La seccion 8.3 SHALL declarar que el denominador de la proporcion del tiempo de intervencion
usa los tiempos automatizados de la campaña complementaria (`corpus_campana.json`). La seccion
8.7 SHALL declarar que la salida en vivo telefonica proviene de la columna `sector_predicho`
del export de intervenciones, que prediccion usa el McNemar y la definicion del conjunto de
verdad laxo del brazo manual (consenso mas la union de los sectores adicionales de E1 y E2). El
efecto minimo detectable del Spearman SHALL coincidir con el que produce la formula
documentada en `evaluation/campana.py` con el `n` declarado, o SHALL declarar el `n` y la
formula que producen el valor informado. El balance laxo maximo SHALL calcularse con el mismo
Δt que declara la Tabla 16. Cada cifra SHALL registrarse en `numeros-canonicos.md` con su
fuente.

#### Scenario: Denominador y origen declarados

- **WHEN** se leen 8.3 y 8.7
- **THEN** se nombran `corpus_campana.json`, `sector_predicho` del export, la prediccion del McNemar y la definicion del conjunto laxo

#### Scenario: MDE reproducible

- **WHEN** se recalcula el MDE con la formula y el `n` que declara el texto
- **THEN** el resultado coincide con el valor impreso a cuatro decimales

### Requirement: Rotulos temporales univocos y alcance del clasificador congelado

Las secciones 2.4, 5.5, 6.3 y 7.5 MUST NOT usar "posterior a las corridas de la campaña" sin
nombrar la campaña: SHALL decir "posterior a la campaña 2026-10". Las figuras
`componentes.png` y `secuencia.png` MUST NOT contener dentro de la imagen "posterior a la
campaña de medición" ni "posterior a la campaña" sin nombre; SHALL regenerarse desde
`docs/diagrams/`. La seccion 4.5 SHALL matizar que la campaña complementaria corrio con
`hybrid-v3` pero con la regla del reportante activa y con una salida en vivo que difiere de la
cache en 13 casos, y MUST NOT afirmar sin esa salvedad que sus metricas de clasificacion son
comparables.

#### Scenario: Rotulos en texto

- **WHEN** se busca "posterior a las corridas de la campaña" en `sections/`
- **THEN** no hay coincidencias

#### Scenario: Rotulos en imagen

- **WHEN** se inspeccionan `componentes.png` y `secuencia.png` y sus fuentes Mermaid
- **THEN** el rotulo temporal nombra la campaña 2026-10

#### Scenario: 4.5 matizada

- **WHEN** se lee 4.5
- **THEN** figuran la regla del reportante activa y las 13 diferencias con la cache

### Requirement: Formulaciones no mas afirmativas que la evidencia en 1.6, resumen y Tabla 18

La seccion 1.6 MUST NOT anunciar una "validacion rigurosa" con "doble etiquetado
independiente"; SHALL ser coherente con 4.4 y 9.3 (validacion dentro de la muestra, analista
autor, acuerdo moderado). El resumen y el abstract SHALL usar "respaldan" / "support" y MUST
NOT usar "confirman" / "confirm" para la viabilidad. La fila del primer objetivo de la Tabla 18
SHALL decir "reintentos idempotentes de la configuración entregada", y la celda del cuarto
objetivo MUST NOT repetir "exactitud del brazo manual" en clausulas consecutivas.

#### Scenario: Sin sobreafirmaciones

- **WHEN** se buscan "validación rigurosa" en `01-introduccion.tex` y "confirman la viabilidad" en `00-resumen.tex`
- **THEN** no hay coincidencias

#### Scenario: Tabla 18 precisa

- **WHEN** se leen las filas del OE1 y del OE4 de `tab:cumplimiento-objetivos`
- **THEN** la del OE1 califica los reintentos como de la configuracion entregada
- **AND** la del OE4 nombra la exactitud del brazo manual una sola vez

### Requirement: Forma del documento tras el dictamen del 9 de noviembre

La seccion 9.3 SHALL anunciar tantas limitaciones como enumera. La seccion 8.3 MUST NOT
contener el anacoluto de la proporcion del tiempo. El glosario SHALL definir, o el cuerpo
desarrollar en su primer uso, TI, URL, E2E, MDE, VIS, HS256, CA, NB, LR y DT, y cada sigla del
glosario SHALL tener uso en el cuerpo. La portada SHALL fecharse el dia de la release que la
contiene. `figures/matriz_confusion.pdf` MUST NOT quedar en el directorio de figuras sin uso
(se retira o se declara como artefacto no embebido fuera de `figures/`). El Anexo B SHALL
nombrar `paper/compilacion.md` y `docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py`,
que la Tabla 23 le atribuye. La seccion 7 (`11-aspectos-legales.tex`) SHALL describir como se
informo y consintio a E1, E2, O1 y O2, o declarar que no hay registro. El exceso de paginas
sobre el tope total de 100 SHALL quedar declarado en el libro mayor con su magnitud, fecha y
decision.

#### Scenario: Conteo de limitaciones

- **WHEN** se compara la frase de apertura de 9.3 con la enumeracion
- **THEN** el numero anunciado coincide con el de limitaciones enumeradas

#### Scenario: Siglas cubiertas

- **WHEN** se busca cada sigla de la lista con `rg -w` en `sections/`
- **THEN** cada una esta en el glosario o desarrollada en su primer uso

#### Scenario: Portada, figura huerfana y Anexo B

- **WHEN** se leen `00-portada.tex`, el directorio `figures/` y el Anexo B
- **THEN** la portada tiene la fecha de la release, `matriz_confusion.pdf` no esta en `figures/` y el Anexo B nombra `compilacion.md` y el verificador

#### Scenario: Consentimiento de los sujetos

- **WHEN** se lee 7
- **THEN** figura el procedimiento de informacion y consentimiento de E1, E2, O1 y O2 o la declaracion de que no se registro

### Requirement: Fidelidad bibliografica y fuente de precios segun el dictamen del 9 de noviembre

La seccion 2.4 MUST NOT atribuir a Zanzotto (2019) la reserva del rol humano ante la
ambiguedad semantica y la responsabilidad sin pagina que lo respalde; SHALL reformularse como
inferencia de los autores o citar la pagina. Las secciones 2.5 y 9.2 MUST NOT atribuir a Xiong
et al. (2024) una "baja discriminacion"; SHALL decir que predecir las fallas sigue siendo un
desafio. El punto unico de contacto (2.1) SHALL citarse con `OGC2011_itil` y no con Galup et
al. (2009). El calculo economico de 9.5 SHALL citar la pagina de precios de la Gemini API, y la
seccion 7 SHALL declarar el nivel de servicio (gratuito o pago) en que opero el sistema y su
consecuencia sobre el uso de los datos transferidos. Las URL de Zendesk, Vertex (si se
conserva) y del Decreto 1558/2001 SHALL resolver a la pagina citada. Ramya et al. SHALL citarse
en su version IEEE (CSITSS 2018) con DOI; Kerby (2014) con el localizador 3:11.IT.3.1; Efron y
Tibshirani con año y DOI de la misma edicion; FrugalGPT en TMLR solo si se confirma. Toda
entrada nueva o modificada SHALL verificarse en la fuente y `verify_citations.py` SHALL dar
PASS.

#### Scenario: Atribuciones corregidas

- **WHEN** se leen 2.1, 2.4, 2.5 y 9.2
- **THEN** el punto unico de contacto cita ITIL, Zanzotto no sostiene una afirmacion sin respaldo y Xiong no se cita por "baja discriminacion"

#### Scenario: Precios y nivel de servicio

- **WHEN** se leen 9.5 y 7
- **THEN** 9.5 cita la pagina de precios de la Gemini API
- **AND** 7 declara el nivel de servicio y su consecuencia sobre los datos

#### Scenario: Entradas corregidas

- **WHEN** se compila y se lee la lista de referencias
- **THEN** Ramya figura como IEEE CSITSS 2018 con DOI, Kerby con 3:11.IT.3.1 y Efron con año y DOI concordantes
- **AND** biber no registra advertencias y `verify_citations.py` reporta PASS

### Requirement: Linea futura de medicion de la intervencion con denominador revisable

La seccion 11.3 (`subsec:medicion-intervencion`) SHALL incluir, ademas de los reportantes
identificados, dos requisitos de una medicion valida de la segunda sub-hipotesis: que la
revision alcance a todos los canales o a una muestra aleatoria de cada uno, y que cada
validacion se coteje con una referencia independiente.

#### Scenario: Requisitos de la medicion futura

- **WHEN** se lee 11.3
- **THEN** figuran la revision de todos los canales (o muestra aleatoria por canal) y el cotejo con una referencia independiente

### Requirement: Trazabilidad del dictamen del 9 de noviembre en el registro y en el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 /
v1.2.12 (2026-11-09) - c-190" con una matriz de 7 columnas que cubra cada recomendacion (A1-A3,
B1-B4, C1-C2) y cada item del inventario (1-30), con su estado, y las decisiones de los autores
del design de c-190. `verificar_matriz_trazabilidad.py` SHALL reportar 0 fallas sobre el arbol
y sobre el tag de la release. El Anexo I (`sec:anexo-trazabilidad`) SHALL incluir una tabla
`tab:anexo-trazabilidad-0911` con las recomendaciones del dictamen del 9 de noviembre y las
secciones tocadas, y su frase de cabecera SHALL contar siete dictamenes hasta el 9 de noviembre
de 2026. El dictamen SHALL versionarse en `auditorias/` en el commit de contenido de la release.

#### Scenario: Matriz completa

- **WHEN** se lee la seccion de c-190 de `dictamen-correcciones.md`
- **THEN** cada recomendacion y cada item 1-30 tiene una fila con archivo, fragmento verificable y estado
- **AND** el verificador reporta 0 fallas

#### Scenario: Anexo I actualizado

- **WHEN** se compila y se lee el Anexo I
- **THEN** `tab:anexo-trazabilidad-0911` resuelve y la cabecera cuenta siete dictamenes

#### Scenario: Dictamen versionado

- **WHEN** se ejecuta `git ls-tree v1.2.13 auditorias/`
- **THEN** figura `Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`

### Requirement: Neutralidad de paginas y palabras de las correcciones de c-190

Las correcciones de c-190 MUST NOT llevar el PDF del commit etiquetado `v1.2.13` por encima de
118 paginas (las del tag `v1.2.12`). El resumen y el abstract MUST NOT superar 250 palabras
cada uno con la regla de medicion registrada. La compilacion SHALL cumplir el requisito
"Thesis PDF compilation", y el libro mayor de paginas y palabras SHALL registrarse en
`dictamen-correcciones.md`.

#### Scenario: Paginas dentro del tope

- **WHEN** se compila `main.tex` en el commit de contenido de la release
- **THEN** `compilacion.md` informa a lo sumo 118 paginas

#### Scenario: Resumen dentro del tope

- **WHEN** se cuentan las palabras de `00-resumen.tex` con la regla registrada
- **THEN** el resumen y el abstract tienen a lo sumo 250 palabras cada uno
