## ADDED Requirements

### Requirement: Consistencia interna del veredicto de la intervencion humana y de la validacion fuera de muestra

El documento SHALL presentar de forma consistente el veredicto de la segunda sub-hipotesis (intervencion humana) entre el resumen, la introduccion y los capitulos de resultados y discusion. El resumen SHALL acompanar la cifra `147 / 17,0 %` con el mismo calificador que el cuerpo ("no concluyente, con estimacion puntual por encima de la cota"). La introduccion SHALL distinguir la **tasa de derivacion erronea a priori del 15 %** (declarada preliminar y **no re-medida**) de la **exactitud estricta del brazo manual medida** en la campana complementaria (`0,8278` = `125/151`, de la que se deriva `e_man = 26/151 = 0,1722`); MUST NOT afirmar de forma plana que la tasa de error manual "no fue re-medida" sin reconocer esa medicion. La introduccion SHALL declarar ademas la validacion **fuera de muestra** (exactitud estricta cruda `0,6893` y ponderada `0,7489` sobre el corpus arbitrado) junto a la validacion dentro de la muestra, sin acotar la contribucion a esta ultima. La introduccion SHALL rotular `82,78 %` como **exactitud estricta del brazo manual**, no como tasa de error.

#### Scenario: Resumen con el calificador del cuerpo

- **WHEN** se lee el resumen en `00-resumen.tex`
- **THEN** la cifra `147 / 17,0 %` aparece con el calificador "no concluyente, con estimacion puntual por encima de la cota"
- **AND** el calificador coincide con el de `08-discusion.tex`, `04-marco-metodologico.tex` y `07-resultados.tex`

#### Scenario: Tasa a priori y medicion del brazo manual distinguidas

- **WHEN** se lee `01-introduccion.tex` en el pasaje del 15 %
- **THEN** el texto declara que ese 15 % es preliminar y no re-medido
- **AND** remite a la medicion del brazo manual de la campana complementaria (`0,8278`; `e_man = 26/151 = 0,1722`) que si mide esa exactitud

#### Scenario: Validacion fuera de muestra declarada en la introduccion

- **WHEN** se lee la contribucion en `01-introduccion.tex`
- **THEN** figuran la validacion dentro de la muestra y la validacion fuera de muestra (`0,6893` cruda y `0,7489` ponderada)
- **AND** el texto no acota la contribucion a la validacion dentro de la muestra

#### Scenario: Rotulo de la exactitud del brazo manual

- **WHEN** se busca "82,78" en los archivos de seccion
- **THEN** aparece rotulado como "exactitud estricta del brazo manual"
- **AND** no aparece rotulado como "tasa de error manual medida"

### Requirement: Procedencia y localizador de las entradas bibliograficas

La bibliografia SHALL declarar la procedencia de cada entrada de modo que su identificador resuelva o su localizador conste. En particular: `Powers2011_evaluation` SHALL conservar el ano `2011` y SHALL agregar un campo `note` que aclare que su URL de arXiv corresponde a un **espejo posterior** del articulo de 2011 (no a su publicacion original); `ramonferrer2026tripletotext` SHALL declarar su editor (`IOS Press`) sin modificar el DOI `10.1177/22104968261440701`, que resuelve al titulo correcto; `AAIP2023_resolucion198` SHALL agregar una URL oficial (Boletin Oficial o AAIP Argentina), por ser la unica entrada sin URL ni DOI. Ninguna de estas correcciones SHALL cambiar el ano, el autor, el titulo ni el DOI de las entradas.

#### Scenario: Ano de Powers conservado con nota del espejo arXiv

- **WHEN** se inspecciona la entrada `Powers2011_evaluation` en `Bibliography_base.bib`
- **THEN** el campo `year` sigue siendo `2011`
- **AND** existe un campo `note` que aclara que la URL de arXiv es un espejo posterior

#### Scenario: Editor de Ramon-Ferrer declarado sin tocar el DOI

- **WHEN** se inspecciona la entrada `ramonferrer2026tripletotext`
- **THEN** existe un campo `publisher` con `IOS Press`
- **AND** el DOI sigue siendo `10.1177/22104968261440701`

#### Scenario: Localizador oficial de la resolucion AAIP

- **WHEN** se inspecciona la entrada `AAIP2023_resolucion198`
- **THEN** existe un campo `url` con el localizador oficial (Boletin Oficial o AAIP Argentina)
- **AND** `verify_citations.py` sigue reportando `STATUS: PASS`

### Requirement: Nomenclatura canonica de los sectores en la prosa del documento

Cuando el texto cite los sectores como **cadenas del sistema** (su nombre canonico), SHALL usar la forma exacta, case-sensitive y **sin tildes**: `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`. En prosa puramente narrativa puede conservarse la forma en espanol natural con tildes cuando no exista riesgo de confusion con la cadena canonica. El documento MUST NOT introducir una forma intermedia (por ejemplo, con tilde en unas ocurrencias y sin ella en otras dentro del mismo pasaje que cita el sistema).

#### Scenario: Sectores canonicos donde se citan como cadenas del sistema

- **WHEN** se leen `01-introduccion.tex:48`, `01-introduccion.tex:72`, `08-discusion.tex:26` y `07-resultados.tex:347`
- **THEN** los sectores citados como cadenas del sistema usan la forma canonica sin tildes
- **AND** no queda una forma intermedia con tilde que contradiga la cadena canonica en el mismo pasaje

#### Scenario: Prosa narrativa sin riesgo de confusion

- **WHEN** un pasaje usa el nombre de un sector solo como descripcion narrativa
- **THEN** puede conservar el espanol natural (con tilde)
- **AND** la regla aplicada queda declarada en el `design.md`

### Requirement: Tipografia y rotulos de la prosa

Los signos de apertura de interrogacion del documento SHALL ser `¿` (no un `?` seguido de comilla invertida). El documento MUST NOT contener la secuencia malformada en las preguntas de investigacion de la introduccion (4 ocurrencias). Cuando el texto declare el numero de limitaciones del estudio, las que se autocancelan SHALL quedar rotuladas de forma explicita como superadas o resueltas, sin que el conteo y su estado se contradigan.

#### Scenario: Signos de interrogacion bien formados

- **WHEN** se buscan las preguntas de investigacion en `01-introduccion.tex`
- **THEN** cada apertura de interrogacion usa `¿`
- **AND** no queda ninguna ocurrencia de la secuencia `?` seguida de comilla invertida

#### Scenario: Novena limitacion rotulada como superada

- **WHEN** se lee la lista de limitaciones en `08-discusion.tex`
- **THEN** el texto declara nueve limitaciones y rotula la novena (acceso cerrado a `paket2024itservice`) como ya **superada o resuelta**
- **AND** no se presenta una limitacion auto-cancelada como limitacion vigente

### Requirement: Mapa de lectura del documento

La introduccion SHALL incluir un parrafo de organizacion del documento ("mapa de lectura") que describa la estructura de los capitulos y anexos y guie al lector. El parrafo SHOULD ubicarse al final de `01-introduccion.tex`, antes del `\newpage`. Si el parrafo agrega paginas, el conteo final SHALL registrarse en `compilacion.md`.

#### Scenario: Mapa de lectura presente

- **WHEN** se lee el final de `01-introduccion.tex`
- **THEN** existe un parrafo que describe la organizacion del documento (capitulos y anexos)
- **AND** el documento compilado no excede la linea base de paginas sin declararlo en `compilacion.md`

### Requirement: Desambiguacion de las etiquetas de release

Cuando el documento cite releases de software con etiquetas que coexisten (`v1.2.2` y `v1.3.0`), SHALL desambiguarlas explicitamente: `v1.2.2` SHALL identificarse como el **despliegue de referencia** de la prueba de humo TLS y `v1.3.0` como la **configuracion entregada**. La correccion MUST NOT alterar los hechos subyacentes (que la terminacion TLS se verifica sobre ese despliegue de referencia, que los casos de uso de la campana corrieron sobre otros perfiles y que la configuracion evaluada es `bf5e099`).

#### Scenario: Etiquetas de release desambiguadas

- **WHEN** se leen `11-aspectos-legales.tex:34`, `11-aspectos-legales.tex:107` y `05-arquitectura.tex:8`
- **THEN** `v1.2.2` se identifica como el despliegue de referencia de la prueba de humo TLS
- **AND** `v1.3.0` se identifica como la configuracion entregada
- **AND** ningun hecho sobre la campana experimental o la configuracion evaluada cambia

### Requirement: Anclaje de las cifras de cobertura y pruebas a la configuracion evaluada

`06-implementacion.tex` SHALL anclar las cifras de cobertura de sentencias y el numero de pruebas unitarias a la **configuracion evaluada** (commit `bf5e099`, 7-10-2026), medida con el comando reproducible `pytest -m "not integration" --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing` sobre un arbol de trabajo de esa revision con sus dependencias pinneadas. SHALL reportar ademas, si difiere, el contador correspondiente a la **configuracion entregada** (tag `v1.3.0`, commit `1b17e55`), porque la tesis distingue configuracion evaluada de entregada. La medicion SHALL registrar el entorno empleado (version de Python, requirements de la revision) y SHALL declarar la deriva de dependencias como riesgo. Si una cifra cambia respecto del valor anclado a `v1.2.18`, el cambio SHALL declararse explicitamente y registrarse en el memo `docs/Tesis/Correcciones/numeros-canonicos.md`.

#### Scenario: Cifras ancladas a la configuracion evaluada

- **WHEN** se lee la subseccion de pruebas de `06-implementacion.tex`
- **THEN** la cobertura y el numero de pruebas se anclan a `bf5e099` (7-10-2026) con el comando reproducible
- **AND** el texto distingue la configuracion evaluada de la entregada

#### Scenario: Contraparte de la configuracion entregada reportada

- **WHEN** las cifras de `v1.3.0` (`1b17e55`) difieren de las de `bf5e099`
- **THEN** el texto reporta ambas lecturas, rotuladas por revision
- **AND** si no difieren, el texto declara que coinciden

#### Scenario: Cambio de cifra declarado y canalizado

- **WHEN** alguna cifra de cobertura o de conteo de pruebas cambia respecto del valor anclado a `v1.2.18`
- **THEN** el cambio se declara explicitamente en la prosa
- **AND** se registra en el memo `numeros-canonicos.md` con su procedencia y su estado

#### Scenario: Deriva de dependencias declarada

- **WHEN** el entorno pinneado de la revision evaluada no puede instalarse o la medicion no se reproduce
- **THEN** la prosa lo declara como limitacion de reproducibilidad
- **AND** no se reporta una cifra no reproducida como si lo fuera

### Requirement: Cierre de version y compilacion de la release v1.5.1

El change SHALL recompilar el PDF y actualizar `docs/Tesis/v10 (IA)/paper/compilacion.md` con el nuevo conteo de paginas (la linea base compilada es de 159 pp, con el encabezado "Anexos" en p. 141), mediante el generador `docs/Tesis/Correcciones/resumir_registro_compilacion.py`, sin editar el resumen a mano. La version del documento SHALL bumpearse a **`v1.5.1`** de forma consistente en `00-portada.tex`, `12-anexos.tex` (Anexo B) y la entrada bibliografica `Gomez2026_repositorio` de `Bibliography_base.bib`. El archivo de auditoria `docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md` SHALL quedar trackeado en git. El tag anotado `v1.5.1` SHALL cortarse solo con **autorizacion expresa del autor** (checkpoint de gobernanza ALTA) y SHALL consignarse su hash en un commit inmediatamente posterior en el Anexo B, siguiendo el patron de `v1.5.0`.

#### Scenario: Compilacion de cierre y conteo de paginas

- **WHEN** se cierra la release
- **THEN** `main.pdf` compila sin errores fatales, con 0 referencias/citas indefinidas y 0 etiquetas duplicadas
- **AND** `compilacion.md` registra el nuevo conteo de paginas y el SHA-256 del PDF

#### Scenario: Version v1.5.1 consistente

- **WHEN** se busca la version del documento
- **THEN** `00-portada.tex`, `12-anexos.tex` y `Gomez2026_repositorio` declaran `1.5.1` / `v1.5.1`
- **AND** no queda una mencion vigente de la version previa en esos tres puntos

#### Scenario: Tag anotado con autorizacion y hash consignado

- **WHEN** el autor autoriza el tag
- **THEN** se corta el tag anotado `v1.5.1` sobre el commit de contenido
- **AND** un commit posterior consigna el hash del tag en el Anexo B
- **AND** ningun tag previo se mueve

#### Scenario: Archivo de auditoria trackeado

- **WHEN** se cierra el change
- **THEN** `docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md` esta trackeado en git
- **AND** ya no figura como archivo sin seguimiento
