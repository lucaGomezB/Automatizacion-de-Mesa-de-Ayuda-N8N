## MODIFIED Requirements

### Requirement: Thesis PDF compilation

La tesis SHALL compilar desde la fuente LaTeX de la version de trabajo vigente (`docs/Tesis/v10 (IA)/paper/main.tex`) a `docs/Tesis/v10 (IA)/paper/main.pdf` mediante XeLaTeX y biber, sin errores fatales, con las fuentes reales que declara el preambulo (Arial y Courier New) y en el entorno de compilacion de registro consignado en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El PDF SHALL incluir todos los archivos de seccion que `main.tex` incorpora con `\input`, en el orden de `main.tex`. La compilacion de una release SHALL cumplir ademas: cero referencias y citas indefinidas, cero etiquetas duplicadas, biber sin advertencias ni errores, `verify_citations.py` con estado PASS y todo `\includegraphics` resuelto a un archivo existente. Como `main.log` no se versiona, la evidencia de la compilacion de cada release SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

#### Scenario: Compilacion exitosa

- **WHEN** el proyecto LaTeX se compila con `latexmk -xelatex main.tex` (o con la secuencia xelatex -> biber -> xelatex -> xelatex) en el entorno de registro
- **THEN** se produce `docs/Tesis/v10 (IA)/paper/main.pdf` sin errores fatales
- **AND** el PDF contiene los archivos de seccion que `main.tex` incorpora, en el orden de `main.tex`

#### Scenario: Recuperacion ante una falla de compilacion

- **WHEN** ocurre un error de compilacion (paquete faltante, referencia indefinida, fuente no encontrada)
- **THEN** el error se diagnostica desde el `.log`
- **AND** la correccion se aplica en el preambulo o en el `.tex` afectado
- **AND** la recompilacion es exitosa

#### Scenario: Verificaciones de una release

- **WHEN** se compila la fuente que se va a etiquetar como release
- **THEN** el `.log` no contiene referencias ni citas indefinidas ni etiquetas `multiply defined`
- **AND** `main.blg` no contiene lineas `WARN` ni `ERROR`
- **AND** `python verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) reporta `STATUS: PASS`
- **AND** el texto extraido del PDF no contiene la secuencia `??`

#### Scenario: Figuras resueltas

- **WHEN** se recorren los `\includegraphics` de `sections/*.tex` contra el `\graphicspath` del preambulo
- **THEN** cada uno resuelve a un archivo existente de `figures/` o `assets/`
- **AND** ninguna figura requerida por changes previos falta en el PDF

#### Scenario: Entorno de registro validado contra la release previa

- **WHEN** se adopta un entorno de compilacion de registro para medir una release nueva
- **THEN** ese entorno reproduce sobre la fuente de la release previa su conteo de paginas publicado (101 paginas para `v1.1.1`)
- **AND** el registro consigna el entorno, sus versiones de XeLaTeX y biber y el resultado de esa reproduccion

#### Scenario: Evidencia de la compilacion registrada

- **WHEN** se cierra la compilacion de una release
- **THEN** `dictamen-correcciones.md` consigna el comando, el entorno, el conteo de paginas (total y cuerpo sin anexos) y los conteos extraidos del log (errores fatales, referencias y citas indefinidas, etiquetas duplicadas, `Overfull \hbox` mayores a 10pt revisados)
- **AND** consigna el estado de biber y de `verify_citations.py`

### Requirement: Presupuesto de páginas preservado

El total de paginas de la tesis SHALL cumplir el tope vigente de paginas. El tope vigente SHALL declararse en un unico lugar, la seccion de presupuesto de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md`, con su regla de medicion (total del PDF, o cuerpo sin anexos entendido como las paginas anteriores al encabezado "Anexos"), su valor, su fuente (exigencia de la catedra o decision del equipo) y su fecha. Mientras no se registre un tope renegociado, el tope vigente SHALL ser de 101 paginas sobre el total del PDF. El conteo SHALL medirse sobre `main.pdf` compilado en el entorno de registro, con `pdfinfo` o un conteo equivalente de paginas del PDF. La portada SHALL seguir ocupando exactamente una pagina. Este requisito SHALL prevalecer sobre los topes de 100 paginas que enuncian requisitos anteriores de reduccion de paginas, de incorporacion de la tabla de trabajos academicos y del capitulo de cumplimiento, que reflejaban el tope vigente en su momento. Una reduccion para cumplir el tope MUST NOT eliminar contenido cientifico, numeros canonicos, figuras o tablas requeridas, referencias ni correcciones previas.

#### Scenario: Tope por defecto

- **WHEN** no hay un tope renegociado registrado y se ejecuta `pdfinfo main.pdf | grep Pages` (o el conteo equivalente) sobre el PDF de la release
- **THEN** el total es de 101 paginas o menos
- **AND** la portada sigue ocupando exactamente una pagina

#### Scenario: Tope renegociado documentado

- **WHEN** se registra un tope distinto del de 101 paginas sobre el total
- **THEN** el registro declara su regla de medicion, su valor, su fuente y su fecha
- **AND** el PDF de la release cumple esa regla
- **AND** el registro consigna los dos conteos, total y cuerpo sin anexos

#### Scenario: Conteo segun la regla registrada

- **WHEN** la regla vigente es sobre el total del PDF
- **THEN** el conteo incluye portada, indices, glosario, cuerpo, referencias y anexos
- **AND** no se computa un subconjunto para dar por cumplido el tope

#### Scenario: Cuerpo sin anexos

- **WHEN** la regla vigente es sobre el cuerpo sin anexos
- **THEN** el conteo excluye unicamente las paginas desde el encabezado "Anexos" (`\contentsline {section}{Anexos}{N}` de `main.toc`)
- **AND** referencias, indices y glosario se cuentan dentro del cuerpo

#### Scenario: Reduccion sin perdida de contenido

- **WHEN** se compacta el documento para cumplir el tope
- **THEN** los numeros canonicos, las figuras y tablas requeridas, las referencias y las correcciones de c-102 a c-142 permanecen
- **AND** las palancas aplicadas son de forma, o de formato con aprobacion registrada del usuario

### Requirement: Coherencia de la version bibliografica con la release publicada

La entrada `Gomez2026_repositorio` de `docs/Tesis/v10 (IA)/Bibliography_base.bib` SHALL declarar en su titulo la misma version que el tag de release que identifica el Anexo B (`sec:anexo-repositorio`). Para la release `v1.2.0`, el titulo SHALL enunciar la version `1.2.0`, con la etiqueta "Version" o con su forma acentuada si la revision ortotipografica la acentuo por decision registrada, y SHALL NOT conservar numeros de version anteriores como `1.1.1` o `1.0.0`. El numero de version SHALL actualizarlo el change que publica la release, en el mismo commit que cambia el tag del Anexo B; ningun otro change MUST modificar ese numero. Los demas campos de la entrada (autoria, ano, `url` y `note`) SHALL conservarse y la referencia SHALL seguir imprimiendose en la seccion de Referencias.

#### Scenario: Version bibliografica alineada con el tag del Anexo B

- **WHEN** se compara el titulo de `Gomez2026_repositorio` con el tag que consigna el Anexo B
- **THEN** el titulo enuncia la version `1.2.0` y el Anexo B enuncia `v1.2.0`
- **AND** el titulo de `Gomez2026_repositorio` no conserva los numeros de version `1.1.1` ni `1.0.0`

#### Scenario: Integridad de la entrada preservada

- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib`
- **THEN** la entrada sigue existiendo y sigue siendo referenciada por las citas del anexo
- **AND** sus campos `author`, `year`, `url` y `note` se mantienen, sin introducir citas huerfanas ni entradas sin usar

## ADDED Requirements

### Requirement: Integracion verificada de la familia de correcciones del dictamen v10

La release que cierra el dictamen CONEAU del 2026-10-22 sobre la tesis v10 / `v1.1.0` SHALL publicarse solo despues de integrar la familia c-130..c-142 (c-130 a c-140 y c-142). Las decisiones del gate G0 (tope de paginas, entorno de compilacion de registro, inclusion de c-140, checkpoints de c-142 sobre la corrida paga de la ablacion del prompt y sobre el conjunto de preproduccion, orden de aplicacion y nombre de la release) SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md` antes de aplicar c-130. Cada change de la familia SHALL estar archivado, o excluido con justificacion registrada (un change excluido se archiva como no realizado sin sincronizar specs); la exclusion SHALL limitarse a c-140, porque los demas changes atienden recomendaciones que condicionan la aprobacion o correcciones de consistencia. Cada parte de cada recomendacion A1-A5 y B4-B16 SHALL tener exactamente un change dueno. Los comandos de verificacion de cada change SHALL pasar de nuevo sobre el arbol integrado y ningun valor `retirado` del memo canonico MUST reaparecer como resultado. El registro SHALL llevar un libro mayor de paginas con una fila por change aplicado. La rama de integracion SHALL incluir `origin/main` antes del commit que se etiqueta.

#### Scenario: Decisiones G0 previas a la familia

- **WHEN** se lee la seccion de decisiones G0 del registro
- **THEN** figuran el tope de paginas, el entorno de compilacion de registro, la decision sobre c-140, los checkpoints de c-142 (corrida paga del prompt y existencia de los incidentes de preproduccion), el orden de aplicacion y el nombre de la release
- **AND** su fecha es anterior al primer commit de apply de c-130

#### Scenario: Familia cerrada antes del tag

- **WHEN** se ejecuta `openspec list --json` antes del commit C1 de la release
- **THEN** no figura ningun change activo entre c-130 y c-140 ni c-142
- **AND** cada uno existe en `openspec/changes/archive/`, y toda exclusion tiene su justificacion en el registro

#### Scenario: Un unico dueno por parte de recomendacion

- **WHEN** se recorre la matriz de trazabilidad del registro
- **THEN** cada parte de recomendacion (incluidas A5a, A5b, B7a, B7b, B13a, B13b, B16a y B16b) tiene un solo change dueno
- **AND** ninguna recomendacion A1-A5 o B4-B16 queda sin dueno

#### Scenario: Regresion cruzada sobre el arbol integrado

- **WHEN** se re-ejecutan sobre el arbol integrado los comandos de verificacion del `tasks.md` archivado de cada change de la familia
- **THEN** todos pasan
- **AND** toda falla bloquea la release hasta que la corrige el change dueno o, si ya esta archivado, un change de correccion acotado

#### Scenario: Valores retirados ausentes

- **WHEN** se buscan en `sections/*.tex` los valores que el memo canonico marca `retirado` (incluidos 9,5 %, 3.700, "Operaciones" y W = 0)
- **THEN** ninguno aparece como resultado vigente
- **AND** el resumen en espanol conserva un maximo de 250 palabras de prosa

#### Scenario: Metricas calificadas segun la procedencia de los ajustes

- **WHEN** se buscan en `sections/*.tex` las menciones de `97/131`, `0,7405` y `0,6769` y las afirmaciones de ausencia de fuga de datos
- **THEN** cada mencion de esas metricas esta calificada como estimacion dentro de la muestra o remite a la subseccion de sensibilidad de c-142
- **AND** ninguna oracion afirma que el filtro determinista o el prompt se ajustaron sin acceso al corpus de evaluacion

#### Scenario: Libro mayor de paginas completo

- **WHEN** se lee el libro mayor de paginas del registro
- **THEN** hay una fila por change aplicado con total, cuerpo sin anexos, anexos y delta respecto de la linea base `v1.1.1` (101, 93 y 8)
- **AND** el acumulado coincide con el conteo del PDF de la release

#### Scenario: Integracion con la rama principal

- **WHEN** se crea el commit C1 de la release
- **THEN** `git merge-base --is-ancestor origin/main <C1>` es verdadero en ese momento
- **AND** cualquier conflicto en `docs/Tesis/`, `knowledge-base/`, `evaluation/` o `CHANGES.md` se resolvio antes de compilar la version de registro

### Requirement: Trazabilidad de las recomendaciones del dictamen v10 en el registro y en el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL contener una seccion dedicada al dictamen del 2026-10-22 sobre la tesis v10 / `v1.1.0` con una matriz de una fila por recomendacion o parte de recomendacion (A1 a A5 y B4 a B16, con A5, B7, B10, B13 y B16 divididas en sus partes), cada una con su sintesis, el change dueno, el archivo y la linea validos en el commit etiquetado `v1.2.0`, el `\label` mas cercano como ancla, un fragmento verificable y su estado (cerrada, o cerrada parcialmente con justificacion). La seccion SHALL listar tambien las observaciones del dictamen que no tienen numero de recomendacion, cada una con su dueno o con la declaracion de que queda fuera de alcance. El Anexo I de la tesis (`sec:anexo-trazabilidad`) SHALL identificar el dictamen (fecha y version examinada), SHALL citar la ruta del registro y SHALL presentar el mapeo recomendacion -> change -> seccion de la tesis mediante referencias cruzadas, sin numeros de linea de las fuentes.

#### Scenario: Matriz completa

- **WHEN** se leen las filas de la matriz del registro
- **THEN** hay al menos una fila para cada una de A1, A2, A3, A4, A5, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15 y B16
- **AND** ninguna fila carece de change dueno ni de estado

#### Scenario: Lineas verificables contra el tag

- **WHEN** para cada fila se ejecuta `git show v1.2.0:<archivo> | sed -n '<linea>p'`
- **THEN** la linea obtenida contiene el fragmento verificable registrado
- **AND** el `\label` ancla existe en ese archivo en `v1.2.0`

#### Scenario: Anexo I con el mapeo

- **WHEN** se lee el Anexo I en el PDF compilado
- **THEN** identifica el dictamen del 22 de octubre de 2026 sobre la version `v1.1.0`
- **AND** presenta cada recomendacion con su change y la seccion de la tesis donde se atendio
- **AND** cita `docs/Tesis/Correcciones/dictamen-correcciones.md` y no contiene numeros de linea de las fuentes

#### Scenario: Observaciones no numeradas cubiertas

- **WHEN** se lee la tabla de observaciones no numeradas del dictamen
- **THEN** cada observacion tiene un change dueno o la declaracion explicita de que queda fuera de alcance, con su motivo

### Requirement: Verificacion de cierre contra la rubrica del dictamen

El registro SHALL contener una tabla con los nueve criterios evaluables de la rubrica que aplico el dictamen (criterios 1 a 9), cada uno con su peso, el puntaje del dictamen y sus descuentos, y para cada descuento el change que lo atiende y su estado tras la release, remitiendo a la fila de la matriz de trazabilidad como evidencia. El criterio 10 (defensa oral) SHALL declararse no aplicable. La tabla MUST NOT asignar puntajes nuevos. Todo descuento no corregible SHALL declararse como residual con la seccion de la tesis donde figura como limitacion.

#### Scenario: Nueve criterios cubiertos

- **WHEN** se lee la tabla de la rubrica en el registro
- **THEN** figuran los criterios 1 a 9 con todos los descuentos que enumera el dictamen
- **AND** cada descuento tiene un change dueno o figura como residual declarado

#### Scenario: Sin puntajes nuevos

- **WHEN** se lee la tabla de la rubrica
- **THEN** solo figuran los puntajes del dictamen
- **AND** no hay puntajes asignados por los autores

#### Scenario: Residuales con ubicacion en la tesis

- **WHEN** un descuento figura como residual (por ejemplo, los registros primarios del doble etiquetado que no se conservaron)
- **THEN** el registro cita la seccion de la tesis que lo declara como limitacion

### Requirement: Renders derivados regenerados desde la fuente de la release

`docs/Tesis/v10 (IA)/tesis_para_agente.md` SHALL regenerarse desde las fuentes de la release con `docs/Tesis/v10 (IA)/build_tesis_para_agente.py`. El script SHALL recibir el identificador de la release como argumento obligatorio y SHALL fallar si su lista de secciones difiere del orden de `\input` de `main.tex`. El encabezado del render SHALL declarar la release `v1.2.0` y SHALL NOT declarar una release anterior como vigente. `tesis_para_evaluacion.txt` y `tesis_completa_extraida.txt` SHALL regenerarse desde el `main.pdf` de la release mediante extraccion de texto UTF-8. El campo `thesis:` de `openspec/config.yaml` SHALL resolver a un archivo existente. Todo render que no se regenere (por ejemplo `paper/tesis.docx` sin pandoc disponible) SHALL declararse como render legado en el registro. Los renders SHALL regenerarse en el commit etiquetado y en el commit que consigna el hash.

#### Scenario: Render para agentes vigente

- **WHEN** se lee el encabezado de `tesis_para_agente.md` en el commit etiquetado
- **THEN** declara la release `v1.2.0`
- **AND** no declara `v1.1.0` ni `v1.1.1` como release vigente
- **AND** su Anexo B contiene el tag `v1.2.0`

#### Scenario: Generacion determinista

- **WHEN** se ejecuta el script dos veces seguidas sobre la misma fuente con el mismo argumento
- **THEN** ambas salidas tienen el mismo SHA-256

#### Scenario: Orden de secciones verificado

- **WHEN** la lista de secciones del script difiere del orden de `\input` de `main.tex`
- **THEN** el script termina con error y no escribe un render

#### Scenario: Textos extraidos desde el PDF de la release

- **WHEN** se leen `tesis_para_evaluacion.txt` y `tesis_completa_extraida.txt`
- **THEN** contienen texto acentuado y la portada con los dos directores (Prof. Alberto Cortez y Prof. Ariel Enferrel)
- **AND** la cantidad de saltos de pagina de `tesis_para_evaluacion.txt` coincide con la cantidad de paginas del PDF

#### Scenario: Puntero de configuracion resoluble

- **WHEN** se lee el campo `thesis:` de `openspec/config.yaml`
- **THEN** la ruta indicada existe en el arbol de trabajo

#### Scenario: Renders legados declarados

- **WHEN** un render derivado no se regenera para la release
- **THEN** el registro lo declara como render legado, con el motivo
- **AND** el render no se presenta como vigente en ningun puntero activo

### Requirement: Etiqueta de la release v1.2.0 y trazabilidad del hash

La version de trabajo de la tesis `docs/Tesis/v10 (IA)/` SHALL publicarse mediante un tag anotado `v1.2.0` creado sobre el commit C1, que cambia el tag del Anexo B a `v1.2.0`, retira la linea del hash de la release anterior y actualiza la version de `Gomez2026_repositorio`. El tag SHALL crearse solo despues de integrar la familia c-130..c-142 y de recompilar el PDF con las verificaciones de release. El commit C2 SHALL consignar en el Anexo B (`sec:anexo-repositorio`) el hash completo de 40 caracteres del commit etiquetado, coincidente con `git rev-parse v1.2.0^{commit}`, y el mismo hash SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El tag SHALL publicarse en `origin`, y la integracion a `main` SHALL hacerse con merge commit, de modo que el commit etiquetado quede en la historia de `main`. Los tags previos `v1.0.0`, `v1.0.1`, `v1.1.0` y `v1.1.1` MUST NOT moverse.

#### Scenario: Tag anotado sobre C1

- **WHEN** se ejecutan `git cat-file -t v1.2.0` y `git rev-parse v1.2.0^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`, no `commit`) y apunta a C1
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.2.0` lo devuelve)

#### Scenario: Commit etiquetado sin hash de la release anterior

- **WHEN** se lee `sec:anexo-repositorio` en `git show v1.2.0:"docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`
- **THEN** figura el tag `v1.2.0`
- **AND** no figura el hash `4160d84286623b073d2904353e6f9163ae211de7` de `v1.1.1`

#### Scenario: Hash consignado y coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en el commit C2 y se compara con `git rev-parse v1.2.0^{commit}`
- **THEN** figura el hash completo de 40 caracteres del commit etiquetado
- **AND** el hash coincide en los 40 caracteres y tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Tags previos inmutables

- **WHEN** se comparan `git rev-parse v1.0.0^{commit}`, `git rev-parse v1.0.1^{commit}`, `git rev-parse v1.1.0^{commit}` y `git rev-parse v1.1.1^{commit}` con sus valores previos
- **THEN** `v1.0.0` sigue en `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` en `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` en `7103b649d8c4f51737ad6ad4095dad22c9406400` y `v1.1.1` en `4160d84286623b073d2904353e6f9163ae211de7`
- **AND** ningun tag existente fue reescrito ni re-creado

#### Scenario: Tag alcanzable desde la rama principal

- **WHEN** el PR de `ramagonzalo` a `main` se integro y se ejecuta `git fetch origin`
- **THEN** `git merge-base --is-ancestor v1.2.0 origin/main` es verdadero
