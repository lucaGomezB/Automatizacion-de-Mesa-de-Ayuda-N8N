## ADDED Requirements

### Requirement: Trazabilidad de la devolucion de tercera instancia en el registro y el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 / v1.5.2 (2026-11-16) - c-239 (devolucion de tercera instancia)" con una matriz de 7 columnas (Rec | Sintesis | Change | Archivo:linea | Ancla | Fragmento verificable | Estado) con al menos una fila por cada observacion de la devolucion de tercera instancia del 16-11-2026: K-01, K-02, A-01, A-02, A-03, M-01, M-02, M-03, M-04, B-01, B-02 y B-03. Cada fila SHALL nombrar el change que la atendio (`c-235` a `c-239`), el archivo y la linea del texto vigente y un fragmento tomado del texto final. Las observaciones que el retiro de la validacion fuera de muestra vuelve inaplicables (A-02 y B-02, y M-02 si su atencion es la acotacion de la conclusion) SHALL figurar con estado "no aplica por retiro (c-235)" y con un fragmento verificable del texto que declara el retiro. La seccion SHALL registrar el estado final de N-07 y N-15 (parciales en la devolucion de tercera instancia) con el change que las cerro, y SHALL marcar "SUPERADA por c-239" las filas previas cuyo estado ya no refleje el texto vigente. La seccion SHALL incluir el inventario `PENDIENTE-AUTORES` de las respuestas P1 a P12 con su estado. El Anexo I.2 de `12-anexos.tex` (subseccion "Revisiones que originaron las correcciones") SHALL nombrar la devolucion de tercera instancia del 16 de noviembre de 2026 junto a las revisiones previas. `verificar_matriz_trazabilidad.py` SHALL reportar 0 fallas.

#### Scenario: Doce observaciones asentadas

- **WHEN** se lee la matriz de la seccion de c-239
- **THEN** hay al menos una fila por cada una de K-01, K-02, A-01, A-02, A-03, M-01, M-02, M-03, M-04, B-01, B-02 y B-03
- **AND** cada fila nombra su change, su archivo:linea y su estado

#### Scenario: Observaciones no aplicables por el retiro

- **WHEN** se lee la fila de A-02 o de B-02
- **THEN** su estado es "no aplica por retiro (c-235)"
- **AND** su fragmento verificable es texto vigente que declara el retiro

#### Scenario: Estado final de N-07 y N-15

- **WHEN** se lee la seccion de c-239
- **THEN** N-07 y N-15 figuran con su estado final y el change que las cerro
- **AND** las filas de la tabla de c-196 que las daban por cerradas quedan marcadas como superadas o conciliadas

#### Scenario: Anexo I.2 nombra la tercera instancia

- **WHEN** se lee la subseccion "Revisiones que originaron las correcciones" en `12-anexos.tex`
- **THEN** nombra la devolucion de tercera instancia del tribunal del 16 de noviembre de 2026

#### Scenario: Matriz verificada

- **WHEN** se ejecuta `python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` desde la raiz
- **THEN** el resumen incluye filas de la seccion de c-239 y 0 fallas

### Requirement: Cierre de version y compilacion de la entrega posterior a la tercera instancia

El change SHALL cerrar la entrega que incorpora `c-235` a `c-239`. La version del documento SHALL bumpearse a la version que decidan los autores (propuesta: `v1.6.0`) de forma consistente en `00-portada.tex`, `12-anexos.tex` (Anexo B, tag y oracion del hash) y el titulo de `Gomez2026_repositorio` en `Bibliography_base.bib`, sin dejar una mencion vigente de `1.5.2` en esos puntos. El PDF SHALL recompilarse con la imagen Docker `texlive-thesis` (XeLaTeX y biber) con 0 errores fatales, 0 referencias o citas indefinidas y 0 etiquetas duplicadas; `paper/compilacion.md` SHALL regenerarse con `docs/Tesis/Correcciones/resumir_registro_compilacion.py`, sin editarlo a mano; `verify_citations.py` SHALL dar `STATUS: PASS`. El registro SHALL consignar el conteo de paginas y el conteo de palabras del cuerpo con el metodo unico documentado por `c-238` (herramienta, archivos o rango de paginas y exclusiones), aplicado a `v1.5.2` y a la entrega nueva, y SHALL declarar su diferencia con las cifras que el tribunal informo para `v1.5.2` (164 paginas; cuerpo de aproximadamente 51.900 palabras). Si `c-237` dejo un inventario reproducible del uso de asistentes de IA, sus conteos SHALL re-ejecutarse sobre una ref declarada de la entrega y la declaracion del Anexo I SHALL actualizarse si cambian. `tesis_para_agente.md`, `tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt` y la copia de entrega `docs/Tesis/tesis_ultima_version.pdf` SHALL regenerarse desde la compilacion de cierre, y `README.md` SHALL declarar la version nueva. `CHANGES.md` SHALL registrar las entradas de `c-235` a `c-239` y una linea "Actualizacion" fechada de la entrega. El tag anotado SHALL cortarse solo con autorizacion expresa de los autores (gobernanza ALTA), sobre el commit de recompilacion, y su hash SHALL consignarse en el Anexo B en un commit inmediatamente posterior; ningun tag previo SHALL moverse.

#### Scenario: Version consistente en los tres loci

- **WHEN** se busca la version del documento tras el bump
- **THEN** `00-portada.tex`, el Anexo B y `Gomez2026_repositorio` declaran la misma version nueva
- **AND** no queda una mencion vigente de `1.5.2` en esos puntos

#### Scenario: Compilacion de cierre

- **WHEN** se cierra la entrega
- **THEN** `main.pdf` compila sin errores fatales, con 0 referencias o citas indefinidas y 0 etiquetas duplicadas
- **AND** `compilacion.md` registra el conteo de paginas y el SHA-256 del PDF
- **AND** `verify_citations.py` da `STATUS: PASS`

#### Scenario: Conteo de palabras con metodo documentado

- **WHEN** se lee el registro del conteo de palabras del cuerpo
- **THEN** declara la herramienta, el rango contado y las exclusiones
- **AND** informa el valor del mismo metodo sobre `v1.5.2` y su diferencia con la cifra del tribunal

#### Scenario: Conteos de uso de asistentes re-ejecutados

- **WHEN** existe `docs/Tesis/Correcciones/contar_uso_asistentes.py` de `c-237`
- **THEN** se re-ejecuta sobre la ref declarada de la entrega
- **AND** las cifras de la declaracion del Anexo I coinciden con su salida o la diferencia queda registrada

#### Scenario: Derivados regenerados

- **WHEN** se compara el SHA-256 de `docs/Tesis/tesis_ultima_version.pdf` con el de `main.pdf` de la compilacion de cierre
- **THEN** coinciden
- **AND** los tres extractos declaran la version nueva

#### Scenario: Tag solo con autorizacion

- **WHEN** los autores no autorizaron el tag
- **THEN** no se crea ningun tag ni se publica nada
- **AND** el registro consigna que la entrega queda sin tag

### Requirement: Condiciones del tribunal verificadas antes del tag de la entrega

Antes de solicitar la autorizacion del tag de la entrega, el change SHALL completar y registrar en `dictamen-correcciones.md` un checklist de las dos condiciones que la devolucion de tercera instancia fija para fijar fecha de defensa: (1) K-01 resuelta en el ejemplar (validacion fuera de muestra retirada con todo lo que depende de ella, sin cifras fuera de muestra en el Resumen, el Abstract, §1.7, §8, §9, §10, la Tabla de balance ni el Anexo J) y (2) K-02 resuelta en el ejemplar (textos de la tercera organizacion retirados de la tesis y, segun decidan los autores, del repositorio publico; §7.3 corregido con todas las transferencias). El checklist SHALL registrar ademas si las resoluciones fueron comunicadas al director, como dato que aportan los autores. Cada item SHALL apoyarse en una busqueda textual verificable sobre el ejemplar corregido. El change MUST NOT declarar cumplida una condicion que dependa de un hecho no confirmado por los autores.

#### Scenario: Checklist completo antes del tag

- **WHEN** se solicita a los autores la autorizacion del tag
- **THEN** el registro contiene el checklist de K-01 y K-02 con la busqueda textual de cada item y su resultado

#### Scenario: Comunicacion al director como dato de autores

- **WHEN** los autores no confirmaron la comunicacion al director
- **THEN** el checklist la registra como pendiente de autores
- **AND** no la declara cumplida
