## MODIFIED Requirements

### Requirement: Verificador de la matriz de trazabilidad vigente

`docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` SHALL verificar todas las
matrices de 7 columnas con encabezado "Fragmento verificable" de
`dictamen-correcciones.md`, en cualquier seccion (dictamenes del 22-10, del 28-10, del
8-11 y del 9-11). Una fila SHALL pasar cuando el fragmento aparece en el archivo citado y el
ancla `\label` existe en el; si el fragmento esta en otra linea, SHALL pasar con un aviso de
desplazamiento, salvo con `--estricto`, que exige la linea exacta. Las filas cuyo estado
empieza con "PENDIENTE" o "SUPERADA" SHALL omitirse. Ademas, toda seccion `## Dictamen ...` cuyo
titulo nombre un change `c-NNN` con NNN mayor o igual que 190 SHALL contener al menos una fila de
matriz; una seccion asi sin matriz SHALL contarse como falla con un mensaje que nombre la
seccion, de modo que un ciclo de correcciones sin trazar no pase inadvertido. El script SHALL
conservar `--rev`, `--reubicar` y `--estricto`. Cada comportamiento SHALL tener una prueba en
`test_verificar_matriz_trazabilidad.py` escrita antes del codigo (Strict TDD). Tras el apply,
el script SHALL terminar con codigo 0 sobre el arbol de trabajo y con `--rev` del tag de la
release; cada fila marcada "SUPERADA" SHALL nombrar el change que reescribio el parrafo. Las
filas cuyo parrafo reescribio `c-197` SHALL alinearse con el texto final (por ejemplo, por
capitalizacion o puntuacion) o marcarse "SUPERADA por c-197", y la seccion "Dictamen v10 /
v1.2.19 (2026-11-11) - c-197" SHALL contener su propia matriz de 7 columnas, de modo que el
script reporte 0 fallas.

#### Scenario: Todas las matrices verificadas

- **WHEN** se ejecuta `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` desde la raiz
- **THEN** el resumen informa filas de las matrices del 22-10, del 28-10, del 8-11 y de las secciones de c-190 a c-195
- **AND** el codigo de salida es 0 y la cantidad de fallas es 0

#### Scenario: Desplazamiento de linea no es falla

- **WHEN** el fragmento de una fila aparece en el archivo en una linea distinta de la citada
- **THEN** sin `--estricto` la fila pasa con el aviso "desplazada"
- **AND** con `--estricto` la fila falla

#### Scenario: Fragmento ausente o ancla inexistente

- **WHEN** el fragmento no aparece en ninguna linea del archivo o el ancla no existe
- **THEN** la fila falla con un mensaje que nombra el fragmento o el ancla

#### Scenario: Seccion de dictamen sin matriz

- **WHEN** el registro tiene una seccion `## Dictamen ... - c-192` sin ninguna matriz de 7 columnas
- **THEN** el script informa una falla que nombra esa seccion y termina con codigo distinto de 0
- **AND** una seccion de un change anterior a c-190 sin matriz no se cuenta como falla

#### Scenario: Pruebas primero y en verde

- **WHEN** se ejecuta `python -m unittest test_verificar_matriz_trazabilidad -v` desde `docs/Tesis/Correcciones/`
- **THEN** todas las pruebas pasan, incluidas las de matrices multiples, desplazamiento, `--estricto`, filas SUPERADA y secciones sin matriz

#### Scenario: Filas de c-197 alineadas y su seccion con matriz

- **WHEN** se ejecuta el verificador sobre el arbol de trabajo tras este change
- **THEN** las filas c-188 A2, c-190 Res. 11.3 y c-195 C1/13 pasan (fragmento alineado con el retexto de c-197) o figuran "SUPERADA por c-197"
- **AND** la seccion "Dictamen v10 / v1.2.19 (2026-11-11) - c-197" contiene al menos una fila de matriz
- **AND** el resumen final informa `fallas: 0`

## ADDED Requirements

### Requirement: Trazabilidad de las citas de commits a la historia saneada

Los artefactos de evidencia de la tesis que citan commits del repositorio SHALL referenciar la
historia saneada (los SHAs alcanzables desde `HEAD`), no la historia previa al saneo. En
particular, los dictamenes de `auditorias/` y los textos extraidos de la tesis
(`docs/Tesis/v10 (IA)/tesis_completa_extraida.txt` y `docs/Tesis/v10 (IA)/tesis_para_evaluacion.txt`)
SHALL citar, para cada commit que mencionan, su SHA de la historia saneada. Los SHAs de blob
(identificadores de contenido, no de commit) MUST NOT remapearse. Un SHA de commit citado que no
sea ancestro de `HEAD` SHALL considerarse evidencia invalida y corregirse.

#### Scenario: Citas de commit alcanzables desde HEAD

- **WHEN** se extraen los SHAs de commit citados en los dictamenes de `auditorias/` y en los `.txt` extraidos de la tesis
- **THEN** cada uno es ancestro de `HEAD` (`git merge-base --is-ancestor <sha> HEAD` devuelve exito)
- **AND** el texto del documento no cambia: solo la cadena del SHA

#### Scenario: Los SHAs de blob no se remapean

- **WHEN** se revisan los SHAs de blob citados en los mismos artefactos (por ejemplo `858f1c67`, `334a8edb`, `49267f4a`, `1daceb38`, `e69de29b`)
- **THEN** conservan su valor: no dependen del saneo de la historia de commits
- **AND** `git cat-file -t <blob>` sigue devolviendo `blob`

#### Scenario: Los `.txt` extraidos son una instantanea regenerable

- **WHEN** se citan commits dentro de `tesis_completa_extraida.txt` o `tesis_para_evaluacion.txt`
- **THEN** su contenido se reconoce como la extraccion con `pdftotext` de `main.pdf` versionada como instantanea
- **AND** el remapeo mantiene coherente la instantanea; la regeneracion desde un `main.pdf` recompilado es la via durable y queda fuera de este change
