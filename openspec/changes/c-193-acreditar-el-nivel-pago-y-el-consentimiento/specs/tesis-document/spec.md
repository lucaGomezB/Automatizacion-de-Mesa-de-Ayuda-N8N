## MODIFIED Requirements

### Requirement: Forma del documento tras el dictamen del 9 de noviembre

La seccion 9.3 SHALL anunciar tantas limitaciones como enumera. La seccion 8.3 MUST NOT
contener el anacoluto de la proporcion del tiempo. El glosario SHALL definir, o el cuerpo
desarrollar en su primer uso, TI, URL, E2E, MDE, VIS, HS256, CA, NB, LR y DT, y cada sigla del
glosario SHALL tener uso en el cuerpo. La portada SHALL fecharse el dia de la release que la
contiene. `figures/matriz_confusion.pdf` MUST NOT quedar en el directorio de figuras sin uso
(se retira o se declara como artefacto no embebido fuera de `figures/`). El Anexo B SHALL
nombrar `paper/compilacion.md` y `docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py`,
que la Tabla 23 le atribuye. La seccion 7 (`11-aspectos-legales.tex`) SHALL describir como se
informo y consintio a `E1`, `E2`, `O1` y `O2` conforme al requisito "Registro del consentimiento
informado y confirmacion escrita posterior", y MUST NOT declarar que no hay registro del
procedimiento de informacion y consentimiento. El exceso de paginas sobre el tope total de 100
SHALL quedar declarado en el libro mayor con su magnitud, fecha y decision.

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
- **THEN** figura el procedimiento de informacion y consentimiento de `E1`, `E2`, `O1` y `O2` con la confirmacion escrita y su custodia
- **AND** el texto no declara que no se conservo registro

### Requirement: Trazabilidad del dictamen del 9 de noviembre sobre v1.2.13 en el registro y el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 /
v1.2.13 (2026-11-09) - c-192" con una matriz de 7 columnas (Rec | Sintesis | Change |
Archivo:linea | Ancla | Fragmento verificable | Estado) que cubra cada una de las cuatro
observaciones, el item 12 y cada residual, con su estado, y las decisiones de los autores del
design de c-192; y una seccion "Dictamen v10 / v1.2.13 (2026-11-09) - c-193" que cubra la
recomendacion B4 (nivel pago acreditado por el comprobante de facturacion) y el item 13
(consentimiento informado de los cuatro participantes), con la decision de custodia de la
evidencia fisica. `verificar_matriz_trazabilidad.py` SHALL reportar 0 fallas sobre el arbol y
sobre el tag de la release. El Anexo I (`sec:anexo-trazabilidad`) SHALL incluir una tabla de
trazabilidad del dictamen del 9-11 sobre `v1.2.13` (o actualizar la existente) con las secciones
tocadas y `\autoref`, sin numeros de linea. El archivo del dictamen
(`auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`) SHALL versionarse cuando este
disponible, sin bloquear la release.

#### Scenario: Matriz completa del dictamen v1.2.13

- **WHEN** se leen las secciones de c-192 y de c-193 de `dictamen-correcciones.md`
- **THEN** cada observacion, el item 12, el item 13 y cada residual tiene una fila con archivo, fragmento verificable y estado
- **AND** `verificar_matriz_trazabilidad.py` reporta 0 fallas

#### Scenario: Anexo I actualizado

- **WHEN** se compila y se lee el Anexo I
- **THEN** la tabla de trazabilidad del dictamen del 9-11 sobre v1.2.13 resuelve con sus `\autoref`

#### Scenario: Versionado no bloqueante del dictamen

- **WHEN** el archivo del dictamen no esta todavia en `auditorias/`
- **THEN** la tarea de versionarlo queda declarada y la release no se bloquea
- **AND** cuando el archivo se agrega, queda versionado en `auditorias/`

## ADDED Requirements

### Requirement: Acreditacion del nivel pago de la Gemini API con el registro de facturacion

La seccion 7 (`11-aspectos-legales.tex`, `subsec:transferencia-internacional`) SHALL declarar
que el servicio de inferencia opero en el nivel pago de la Gemini API con creditos prepagos y
que, en ese nivel, el proveedor no utiliza el contenido transferido para mejorar sus productos,
citando `Google2026_gemini_api_pricing`. La misma seccion SHALL declarar que el comprobante de
facturacion del nivel pago se conserva bajo custodia del director de la tesis y no se versiona
porque contiene datos de la cuenta. El texto MUST NOT citar la guia de configuracion
`docs/gemini-api-key-setup.md` como prueba del nivel pago.

#### Scenario: Nivel pago acreditado por el comprobante

- **WHEN** se lee `subsec:transferencia-internacional`
- **THEN** figura el nivel pago con creditos prepagos y la cita `Google2026_gemini_api_pricing`
- **AND** figura que el comprobante de facturacion lo conserva el director y no se versiona

#### Scenario: Guia de configuracion no usada como prueba

- **WHEN** se busca `gemini-api-key-setup` en `11-aspectos-legales.tex`
- **THEN** no aparece como prueba del nivel pago

### Requirement: Registro del consentimiento informado y confirmacion escrita posterior

La seccion 7 (`11-aspectos-legales.tex`, `subsec:consentimiento-derechos`) SHALL declarar que
los cuatro participantes de la campana complementaria (`E1`, `E2`, `O1` y `O2`) fueron
informados verbalmente, antes de realizar sus tareas, del proposito del estudio, del caracter
pseudonimizado de los registros, de la voluntariedad de la participacion y del derecho a
retirarse; que, con posterioridad a su participacion, firmaron una confirmacion escrita de esa
informacion y de su consentimiento; que los originales firmados se conservan en el expediente
fisico del trabajo, bajo custodia del director de la tesis, y no se versionan porque contienen
datos personales; y que el repositorio conserva la plantilla de la confirmacion y el registro
de que fue obtenida para los cuatro participantes. El texto MUST NOT contener nombres reales ni
la correspondencia entre alias e identidad: solo alias y codigos `P<n>`. El texto MUST NOT
declarar que no se conservo registro del procedimiento de informacion y consentimiento.

#### Scenario: Procedimiento declarado

- **WHEN** se lee `subsec:consentimiento-derechos`
- **THEN** figuran la informacion verbal previa, la confirmacion escrita posterior y la custodia fisica de los originales
- **AND** el texto no declara que no se conservo registro

#### Scenario: Sin datos personales

- **WHEN** se revisa el parrafo y la plantilla
- **THEN** solo figuran alias y codigos `P<n>`
- **AND** no figura ningun nombre real ni la correspondencia alias-identidad

### Requirement: Plantilla de confirmacion del consentimiento versionada

El repositorio SHALL contener `docs/campana-medicion/confirmacion-posterior-consentimiento.md`
como plantilla de una pagina, con marcadores de posicion y sin nombres, que enumere los cuatro
puntos (informacion verbal previa, registros pseudonimizados, autorizacion y firma posterior) y
una tabla de registro con las columnas `alias`, `rol`, `fecha_informacion_verbal`,
`fecha_confirmacion` y `custodia`. La plantilla SHALL declarar que los originales firmados los
conserva el director de la tesis y que solo la plantilla y el registro entran al repositorio y a
Engram.

#### Scenario: Plantilla completa y sin datos personales

- **WHEN** se lee `docs/campana-medicion/confirmacion-posterior-consentimiento.md`
- **THEN** figuran los cuatro puntos y la tabla con las cinco columnas
- **AND** no figura ningun nombre real
- **AND** se declara que los originales los conserva el director

### Requirement: Neutralidad de paginas de las correcciones de c-193

Las correcciones de c-193 MUST NOT llevar el PDF del commit etiquetado `v1.2.15` por encima de
118 paginas (las del tag `v1.2.14`). La compilacion SHALL cumplir el requisito "Thesis PDF
compilation", y el libro mayor de paginas y palabras SHALL registrarse en
`dictamen-correcciones.md`. El resumen y el abstract MUST NOT superar 250 palabras cada uno.

#### Scenario: Paginas dentro del tope

- **WHEN** se compila `main.tex` en el commit de contenido de `v1.2.15`
- **THEN** `compilacion.md` informa a lo sumo 118 paginas

#### Scenario: Resumen dentro del tope

- **WHEN** se cuentan las palabras de `00-resumen.tex` con la regla registrada
- **THEN** el resumen y el abstract tienen a lo sumo 250 palabras cada uno
