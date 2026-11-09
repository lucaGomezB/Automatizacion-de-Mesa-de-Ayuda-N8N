## MODIFIED Requirements

### Requirement: Fidelidad bibliografica y fuente de precios segun el dictamen del 9 de noviembre

La seccion 2.4 MUST NOT atribuir a Zanzotto (2019) la reserva del rol humano ante la
ambiguedad semantica y la responsabilidad sin pagina que lo respalde; la atribucion SHALL
separarse en DOS oraciones: la primera SHALL presentar como inferencia de los autores que el
diseno debe reservar a la persona un rol activo ante la ambiguedad semantica y la
responsabilidad sobre las consecuencias de la decision, y la segunda SHALL atribuir al
paradigma \emph{HitAI}, con `\textcite{Zanzotto2019_human_in_the_loop}`, que reclama retribuir
a quienes producen el conocimiento y sostener la supervision humana. Las secciones 2.5 y 9.2
MUST NOT atribuir a Xiong et al. (2024) una "baja discriminacion"; SHALL decir que predecir las
fallas sigue siendo un desafio. El punto unico de contacto (2.1) SHALL citarse con
`OGC2011_itil` y no con Galup et al. (2009). El calculo economico de 9.5 SHALL citar la pagina
de precios de la Gemini API, y la seccion 7 SHALL declarar el nivel de servicio (gratuito o
pago) en que opero el sistema y su consecuencia sobre el uso de los datos transferidos. Las URL
de Zendesk, Vertex (si se conserva) y del Decreto 1558/2001 SHALL resolver a la pagina citada.
La nota de `Zendesk2026_help_desk` SHALL describir lo que la pagina muestra (una pagina de
producto de software de servicio al cliente) y MUST NOT declarar "capacidades y precios";
SHALL conservar autor, titulo, URL `https://www.zendesk.com/service/` y `urldate`. Ramya et al.
SHALL citarse en su version IEEE (CSITSS 2018) con DOI; Kerby (2014) con el localizador
3:11.IT.3.1; Efron y Tibshirani con año y DOI de la misma edicion; FrugalGPT en TMLR solo si se
confirma. Toda entrada nueva o modificada SHALL verificarse en la fuente y `verify_citations.py`
SHALL dar PASS.

#### Scenario: Atribuciones corregidas

- **WHEN** se leen 2.1, 2.4, 2.5 y 9.2
- **THEN** el punto unico de contacto cita ITIL, Zanzotto no sostiene una afirmacion sin respaldo y Xiong no se cita por "baja discriminacion"

#### Scenario: Zanzotto en dos oraciones

- **WHEN** se lee 2.4 (`subsec:human-in-the-loop`)
- **THEN** la inferencia de los autores y el paradigma HitAI estan en oraciones separadas
- **AND** la clausula de retribuir a quienes producen el conocimiento y sostener la supervision humana se atribuye a `Zanzotto2019_human_in_the_loop` con `\textcite`

#### Scenario: Precios y nivel de servicio

- **WHEN** se leen 9.5 y 7
- **THEN** 9.5 cita la pagina de precios de la Gemini API
- **AND** 7 declara el nivel de servicio y su consecuencia sobre los datos

#### Scenario: Nota de Zendesk sin precios

- **WHEN** se lee `Zendesk2026_help_desk` en `Bibliography_base.bib`
- **THEN** la nota describe la pagina de producto y no contiene "precios"
- **AND** la URL y el `urldate` se conservan

#### Scenario: Entradas corregidas

- **WHEN** se compila y se lee la lista de referencias
- **THEN** Ramya figura como IEEE CSITSS 2018 con DOI, Kerby con 3:11.IT.3.1 y Efron con año y DOI concordantes
- **AND** biber no registra advertencias y `verify_citations.py` reporta PASS

### Requirement: Trazabilidad del dictamen del 9 de noviembre sobre v1.2.13 en el registro y el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 /
v1.2.13 (2026-11-09) - c-192" con una matriz de 7 columnas (Rec | Sintesis | Change |
Archivo:linea | Ancla | Fragmento verificable | Estado) que cubra cada una de las cuatro
observaciones, el item 12 y cada residual, con su estado, y las decisiones de los autores del
design de c-192; una seccion "Dictamen v10 / v1.2.13 (2026-11-09) - c-193" que cubra la
recomendacion B4 (nivel pago acreditado por el comprobante de facturacion) y el item 13
(consentimiento informado de los cuatro participantes), con la decision de custodia de la
evidencia fisica; y una seccion "Dictamen v10 / v1.2.13 (2026-11-09) - c-194" que cubra las
recomendaciones residuales C1 (fila "Lim." y atribucion a Zanzotto) y C2 (nota de Zendesk) con
sus decisiones y el libro mayor de paginas. La fila "Lim." del Anexo I
(`tab:anexo-trazabilidad-2810`, `12-anexos.tex`) SHALL leer como SECUENCIA TEMPORAL: primero
`c-169` resolvio dos de los cinco limites estructurales (exactitud del brazo manual e intervalo
del kappa) y dejo sin concluir la sub-hipotesis de intervencion humana; despues `c-190` la
refuto sobre los casos revisados y corrigio la definicion de exactitud laxa; el efecto de orden
no se resolvio y la validacion fuera de muestra permanece como limitacion negativa declarada.
Su columna Change SHALL nombrar `\texttt{c-169}, \texttt{c-190}`. `verificar_matriz_trazabilidad.py`
SHALL reportar 0 fallas sobre el arbol y sobre el tag de la release. El Anexo I
(`sec:anexo-trazabilidad`) SHALL incluir las tablas de trazabilidad del dictamen del 9-11 sobre
`v1.2.13` con las secciones tocadas y `\autoref`, sin numeros de linea. El archivo del dictamen
(`auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`) SHALL versionarse cuando este
disponible, sin bloquear la release.

#### Scenario: Matriz completa del dictamen v1.2.13

- **WHEN** se leen las secciones de c-192, c-193 y c-194 de `dictamen-correcciones.md`
- **THEN** cada observacion, el item 12, el item 13, C1 y C2 tienen una fila con archivo, fragmento verificable y estado
- **AND** `verificar_matriz_trazabilidad.py` reporta 0 fallas

#### Scenario: Fila Lim. como secuencia temporal

- **WHEN** se compila y se lee la fila "Lim." del Anexo I
- **THEN** declara primero el aporte de `c-169` y despues el de `c-190`, en ese orden
- **AND** su columna Change nombra `c-169` y `c-190` y no contiene numeros de linea

#### Scenario: Anexo I actualizado

- **WHEN** se compila y se lee el Anexo I
- **THEN** las tablas de trazabilidad del dictamen del 9-11 sobre v1.2.13 resuelven con sus `\autoref`

#### Scenario: Versionado no bloqueante del dictamen

- **WHEN** el archivo del dictamen no esta todavia en `auditorias/`
- **THEN** la tarea de versionarlo queda declarada y la release no se bloquea
- **AND** cuando el archivo se agrega, queda versionado en `auditorias/`

## ADDED Requirements

### Requirement: Secuencia temporal de la fila Lim. del Anexo I

La fila "Lim." del Anexo I SHALL expresar la secuencia temporal de los residuales del dictamen
del 28 de octubre: el primer tramo (`c-169`) resolvio la exactitud del brazo manual y el
intervalo del kappa y dejo sin concluir la sub-hipotesis de intervencion humana, sin resolver
el efecto de orden; el segundo tramo (`c-190`) refuto esa sub-hipotesis sobre los casos
revisados y corrigio la definicion de exactitud laxa del brazo manual. La validacion fuera de
muestra SHALL permanecer declarada como limitacion negativa por ausencia de un corpus
independiente. La fila MUST NOT presentar el efecto de orden como resuelto ni como refutado, y
MUST NOT contener numeros de linea de las fuentes.

#### Scenario: Orden de los tramos

- **WHEN** se lee la fila "Lim." del Anexo I
- **THEN** el aporte de `c-169` precede al de `c-190`
- **AND** el efecto de orden figura como no resuelto y la validacion fuera de muestra como limitacion negativa

### Requirement: Consistencia de las referencias de la version entregada en v1.2.16

Las referencias a la configuracion entregada SHALL nombrar la release vigente `v1.2.16` en
`05-arquitectura.tex`, `06-implementacion.tex`, `11-aspectos-legales.tex` y `12-anexos.tex`
(incluidos el Anexo A, el Anexo B, la Tabla de configuracion evaluada frente a entregada y su
nota de fuente). El texto MUST NOT nombrar `v1.2.15` como configuracion entregada. Las dos
referencias historicas al dictamen del 9 de noviembre sobre `v1.2.12`
(`12-anexos.tex`, parrafo del Anexo I y el que presenta la tabla) SHALL conservarse intactas.

#### Scenario: Version entregada vigente

- **WHEN** se busca `v1.2.15` como referencia de configuracion entregada en los cuatro archivos
- **THEN** no hay coincidencias
- **AND** las referencias de configuracion entregada nombran `v1.2.16`

#### Scenario: Referencias historicas intactas

- **WHEN** se busca `v1.2.12` en `12-anexos.tex`
- **THEN** conserva las dos referencias al dictamen sobre esa version

### Requirement: Etiqueta de la release v1.2.16 y trazabilidad del hash

La release entregada SHALL ser `v1.2.16`. El Anexo B (`sec:anexo-repositorio`,
`12-anexos.tex`) SHALL nombrar el tag anotado `v1.2.16` creado sobre el commit de contenido; el
commit de contenido SHALL llevar la oracion de verificacion `git rev-list -n1 v1.2.16` en lugar
del hash, y el commit inmediatamente posterior SHALL reemplazarla por el hash completo del
commit de contenido. Los commits posteriores MUST NOT modificar las fuentes de la tesis. El PDF
compilado en el tag MUST NOT imprimir el hash de una release previa (ni `f72e6c8` de `v1.2.15`
ni cualquier otro).

#### Scenario: Anexo B nombra la release vigente

- **WHEN** se compila el commit de contenido y se lee el Anexo B
- **THEN** el tag nombrado es `v1.2.16` y figura la oracion `git rev-list -n1 v1.2.16`

#### Scenario: PDF del tag sin hash ajeno

- **WHEN** se extrae el texto del PDF compilado en `v1.2.16`
- **THEN** no figura el hash de una release previa

### Requirement: Neutralidad de paginas de las correcciones de c-194

Las correcciones de c-194 MUST NOT llevar el PDF del commit etiquetado `v1.2.16` por encima de
118 paginas (las del tag `v1.2.15`). La compilacion SHALL cumplir el requisito "Thesis PDF
compilation", y el libro mayor de paginas y palabras SHALL registrarse en
`dictamen-correcciones.md`. El resumen y el abstract MUST NOT superar 250 palabras cada uno y
MUST NOT cambiar.

#### Scenario: Paginas dentro del tope

- **WHEN** se compila `main.tex` en el commit de contenido de `v1.2.16`
- **THEN** `compilacion.md` informa a lo sumo 118 paginas
- **AND** el libro mayor queda registrado en `dictamen-correcciones.md`

#### Scenario: Resumen y abstract intactos

- **WHEN** se compara `00-resumen.tex` con el de `v1.2.15`
- **THEN** no hay cambios y cada uno tiene a lo sumo 250 palabras
