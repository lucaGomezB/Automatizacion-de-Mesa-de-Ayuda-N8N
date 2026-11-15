## MODIFIED Requirements

### Requirement: Versión entregada identificable y con la evidencia vigente

La portada (`00-portada.tex`), la entrada bibliográfica del repositorio (`Bibliography_base.bib`, `Gomez2026_repositorio`) y el Anexo B (`12-anexos.tex`, `sec:anexo-repositorio`) SHALL identificar la misma versión nueva del documento, cuyo tag SHALL contener el texto y los artefactos de evidencia que la tesis cita, incluidos los de `c-223`, `c-224`, `c-225` y `c-226`. El Anexo B MUST NOT afirmar que los commits posteriores al tag no modifican las fuentes si eso no es verificable; SHALL declarar que el commit posterior al tag solo consigna su hash. El Anexo B SHALL desambiguar de forma explícita la `versión entregada` del documento (el tag del manuscrito) de la `configuración entregada` del software (el tag `v1.3.0`), de modo que la misma palabra no designe dos objetos distintos. El commit etiquetado SHALL llevar en el Anexo B la oración de reemplazo sin imprimir el hash de una release previa, y el commit inmediatamente posterior SHALL reemplazarla por el hash completo del commit etiquetado. El cronograma SHALL registrar la validación fuera de muestra, el arbitraje, la línea de base y los análisis posteriores con la precisión de su evidencia. `paper/compilacion.md` SHALL regenerarse con la compilación final. La creación y la publicación del tag MUST NOT realizarse sin confirmación expresa de los autores.

#### Scenario: Tag coherente con el documento

- **WHEN** se compara el hash del Anexo B con `git rev-parse <tag>^{commit}`
- **THEN** coinciden
- **AND** `git show <tag>:` encuentra los artefactos de evidencia citados por la tesis, incluidos los de `c-223` a `c-226`
- **AND** la portada, la entrada del repositorio y el Anexo B nombran la misma versión

#### Scenario: El tag contiene la evidencia nueva

- **WHEN** se ejecuta `git merge-base --is-ancestor <commit-de-c-223> <tag>` y la verificación análoga para `c-224`, `c-225` y `c-226`
- **THEN** los cuatro commits son ancestros del tag
- **AND** `git show <tag>:docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` contiene el anexo nuevo de números canónicos

#### Scenario: Desambiguación de documento y software

- **WHEN** se lee `sec:anexo-repositorio` en el Anexo B
- **THEN** la `versión entregada` designa el tag del documento de tesis y la `configuración entregada` designa el tag del software
- **AND** las dos expresiones se declaran como objetos distintos

#### Scenario: Sin hash ajeno en el PDF etiquetado

- **WHEN** se extrae el texto del PDF compilado en el tag y se busca el hash de la release previa (`v1.4.1`)
- **THEN** el PDF etiquetado no contiene ese hash
- **AND** el Anexo B del PDF etiquetado muestra la oración de reemplazo

#### Scenario: Cronograma actualizado

- **WHEN** se lee `docs/diagrams/cronograma.md`
- **THEN** figuran los hitos de noviembre de 2026 con su evidencia

### Requirement: Trazabilidad de la devolución de segunda instancia en el registro

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una sección "Dictamen v10 / v1.2.18 (2026-11-11) - c-196 (devolución de segunda instancia)" con una matriz de 7 columnas (Rec | Síntesis | Change | Archivo:línea | Ancla | Fragmento verificable | Estado) con una fila por N-01 a N-16, fragmentos tomados del texto final y estado; las decisiones del design de c-196; el inventario de `PENDIENTE-AUTORES`; y el libro mayor de páginas y palabras. El estado de cada fila SHALL reflejar el texto vigente del repositorio: las observaciones `N-02`, `N-04`, `N-05` y `P16` SHALL figurar como cerradas, con el fragmento verificable y el `archivo:línea` del texto vigente (`12-anexos.tex` para `N-02` y `P16`; `04-marco-metodologico.tex` para `N-04` y `N-05`) y la referencia al commit `c5b2fb9` (2026-11-11), que las cerró. Ninguna de esas cuatro observaciones SHALL figurar en el inventario `PENDIENTE-AUTORES`, que SHALL quedar sin filas pendientes. Las filas de matrices anteriores cuyo párrafo reescribe c-196 SHALL marcarse "SUPERADA por c-196". `verificar_matriz_trazabilidad.py` SHALL reportar 0 fallas y la compilación SHALL cumplir el requisito "Thesis PDF compilation" (0 errores, 0 referencias o citas indefinidas, `verify_citations.py` PASS, `compilacion.md` con el SHA-256 del PDF).

#### Scenario: Matriz de c-196 verificada

- **WHEN** se ejecuta `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` desde la raíz
- **THEN** el resumen informa filas de la sección de c-196 y 0 fallas

#### Scenario: Estados reales de N-02, N-04, N-05 y P16

- **WHEN** se lee la fila de `N-02`, `N-04` o `N-05` en la tabla de correcciones de la sección c-196
- **THEN** su Estado es cerrada y no "PENDIENTE", con el fragmento del texto vigente y la referencia a `c5b2fb9`
- **AND** la observación, la corrección y el archivo declarados no cambian

#### Scenario: Inventario PENDIENTE-AUTORES sin pendientes

- **WHEN** se lee el inventario `PENDIENTE-AUTORES` de la sección c-196
- **THEN** no contiene ninguna fila de `N-02`, `N-04`, `N-05` ni `P16`
- **AND** la sección declara que no quedan pendientes de autores

## ADDED Requirements

### Requirement: Anexo de números canónicos citados y cuerpo sin referencias internas al memo

`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` SHALL incorporar un anexo nuevo (rotulado «Anexo» en español, con etiqueta `sec:anexo-numeros-canonicos`) que reúna los números canónicos que el cuerpo cita, y solo ellos, ubicado de modo que no renumere los anexos A a I existentes. El anexo SHALL ser una transcripción condensada del memo: cada valor SHALL llevar su cifra, su procedencia (archivo o comando que lo reproduce) y un estado en `{vigente, sensibilidad, reinterpretacion, condicional, retirado}` tomados del memo `docs/Tesis/Correcciones/numeros-canonicos.md`. El anexo MUST NOT reproducir las secciones completas del memo, MUST NOT introducir valores ausentes del memo y MUST NOT modificar ningún valor canónico. El memo SHALL conservarse como fuente interna de verdad del proyecto. Las referencias del cuerpo al memo por número de sección (`Sección 3.xx`) SHALL reemplazarse por una remisión al anexo (`\autoref{sec:anexo-numeros-canonicos}`); tras el change, ningún capítulo del cuerpo SHALL citar el memo de números canónicos por número de sección. El crecimiento de páginas del anexo SHALL registrarse en el libro mayor de `dictamen-correcciones.md`.

#### Scenario: Anexo con los números citados

- **WHEN** se compila y se lee el anexo nuevo del Anexo de números canónicos
- **THEN** figuran los valores de las secciones `3.31`, `3.33`, `3.35` y `3.36` del memo que el cuerpo cita
- **AND** ningún otro valor del memo se reproduce

#### Scenario: Procedencia y estado por cifra

- **WHEN** se recorre el anexo nuevo
- **THEN** cada valor declara su procedencia (archivo o comando) y su estado
- **AND** el estado coincide con el del memo

#### Scenario: Cuerpo sin referencias internas por sección

- **WHEN** se busca `Sección[~ ]3\.[0-9]{2}` en `docs/Tesis/v10 (IA)/paper/sections/*.tex`
- **THEN** no quedan coincidencias en los capítulos del cuerpo
- **AND** cada oración que citaba el memo por sección remite ahora a `\autoref{sec:anexo-numeros-canonicos}`

#### Scenario: Sin cifras nuevas ni valores cambiados

- **WHEN** se comparan los valores del anexo con el memo
- **THEN** cada cifra del anexo existe en el memo con el mismo valor y estado
- **AND** ningún valor canónico vigente cambia
