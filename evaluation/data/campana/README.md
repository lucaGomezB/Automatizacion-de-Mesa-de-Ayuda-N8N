# evaluation/data/campana/

Esta carpeta guarda la **tabla primaria del doble etiquetado**: la planilla
etiquetador x caso que permite calcular el kappa de Cohen con su intervalo de
confianza. No contiene datos personales (PII) ni la descripción de los casos:
solo alias (`E1`, `E2`), identificadores de caso, sectores canónicos y marcas de
tiempo. El esquema es el de `evaluation/data/plantilla_etiquetado.csv` y el único
validador es `evaluation/doble_etiquetado.py`.

La conservación de esta tabla es **criterio de aceptación de la campaña**: sin ella
el kappa vuelve a quedar sin intervalo de confianza. El protocolo completo
(sujetos, cegado, codebook, versionado) está en
`docs/campana-medicion/runbook-doble-etiquetado.md`.

## Estado actual

**Pendiente de campaña.** Todavía no existe `doble_etiquetado.csv`: el etiquetado
real corre fuera del repositorio y la tabla se agrega después, siguiendo el
runbook. Mientras el archivo no exista, el test de integridad
(`test_tabla_primaria_versionada_integra`) se omite.

## Archivos de esta carpeta

- `doble_etiquetado.csv`: tabla primaria validada (se agrega después de la campaña).
- `registro_sujetos.csv`: columnas `alias, rol, persona` (se agrega después de la
  campaña; sin nombres, ver el runbook).
- `*.csv` se versionan con fin de línea LF (`.gitattributes`) para que el SHA-256
  coincida en Windows y Linux.

## Procedencia de la tabla primaria

Completar **al versionar** la tabla, con una línea `- campo: valor` por campo. El
test de integridad lee `sha256` de esta sección y lo compara con el hash real del
archivo. Mientras no exista la tabla, los valores quedan en `pendiente`.

- archivo: pendiente
- sha256: pendiente
- fecha: pendiente
- corpus: pendiente
- corpus_sha256: pendiente
- tarea: pendiente
- comando_de_validacion: pendiente
- codebook_sha256: pendiente
- estado_cegado: pendiente
- motivo_limitacion: no aplica

Significado de cada campo:

- `archivo`: ruta de la tabla (`evaluation/data/campana/doble_etiquetado.csv`).
- `sha256`: SHA-256 del archivo tal como está versionado (LF). Calcularlo con
  `sha256sum evaluation/data/campana/doble_etiquetado.csv`.
- `fecha`: fecha ISO (`AAAA-MM-DD`) en que se versionó.
- `corpus`: corpus contra el que se validó (por ejemplo
  `data/corpus_evaluacion_pseudonimizado.json`) y, en `corpus_sha256`, su SHA-256.
- `tarea`: `doble_etiquetado`.
- `comando_de_validacion`: el comando exacto y su resultado (exit code `0`), por
  ejemplo
  `python -m evaluation.doble_etiquetado --planilla evaluation/data/campana/doble_etiquetado.csv --corpus data/corpus_evaluacion_pseudonimizado.json --tarea doble_etiquetado`.
- `codebook_sha256`: SHA-256 del codebook operativo congelado antes de etiquetar (el
  mismo documento para `E1` y `E2`; ver el runbook).
- `estado_cegado`: `cumplido` | `limitacion_declarada`.
  - `cumplido`: `E1` y `E2` son personas distintas entre sí, de los dos analistas
    originales, de los autores y de los operadores `O*`, y etiquetaron sin ver el
    consenso, las predicciones ni las etiquetas del par.
  - `limitacion_declarada`: no se consiguieron etiquetadores nuevos. En
    `motivo_limitacion` se registra el motivo y los roles solapados. El resultado
    se reporta como limitación y **no** como etiquetado ciego.
