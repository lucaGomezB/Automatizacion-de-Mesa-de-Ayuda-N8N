# Proposal: Plantilla y protocolo de doble etiquetado

## Why

El kappa `0,87` se reporta SIN intervalo de confianza porque la tabla primaria de
acuerdo no se conservo: solo existe el consenso `sector_asignado`, sin etiquetas por
etiquetador (`docs/Tesis/Correcciones/numeros-canonicos.md:198-209`). Ademas, la tesis
declara (`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:55`) que los dos
analistas que fijaron ese consenso son los mismos que operaron el brazo manual y que las
discrepancias se resolvieron por consenso: si esas mismas personas vuelven a etiquetar,
el cegado no se cumple y la referencia queda contaminada (transversal T2 del dictamen
`docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md`).

La revision pre-apply detecto tambien tres esquemas distintos para la misma planilla
etiquetador x caso en c-165, c-167 y c-168 (transversal T1). Este change fija el esquema
UNICO y el validador UNICO de esa planilla, y el protocolo (sujetos, cegado, codebook,
versionado de la tabla primaria) que permite computar el kappa con IC. Cuarto de cinco
changes (c-165..c-169); el etiquetado real corre fuera del repositorio.

## What Changes

- **Esquema unico de la planilla de etiquetado (dueno: c-168)**. Plantilla
  `evaluation/data/plantilla_etiquetado.csv` (UTF-8, separador `,`, encabezado
  obligatorio) con estas columnas, en este orden:
  - `id_caso`: igual al `id` del corpus indicado (`R001..R200` en el corpus de ajuste;
    prefijo `I` en el corpus independiente de c-166). Debe existir en ese corpus.
  - `id_etiquetador`: alias sin PII (`E1`, `E2` para doble etiquetado; `O1`, `O2` para
    los operadores del brazo manual de c-165). Nunca nombre, correo ni legajo.
  - `tarea`: `doble_etiquetado` | `brazo_manual`.
  - `sector_etiquetado`: una de las cinco cadenas de `SECTORES_CANONICOS`
    (`evaluation/corpus.py`), importadas y nunca duplicadas como constantes propias.
  - `sectores_adicionales_etiquetados`: lista separada por `|`, puede ir vacia, no
    repite `sector_etiquetado`, cada elemento canonico.
  - `inicio`: ISO-8601 con zona, comienzo de la clasificacion del caso; obligatorio en
    `brazo_manual`, opcional (puede ir vacio) en `doble_etiquetado`.
  - `timestamp`: ISO-8601 con zona (p. ej. `2026-11-03T14:05:00-03:00`), FIN de la
    clasificacion del caso. En `brazo_manual`, `inicio <= timestamp`: c-167 usa
    `duracion_s = timestamp - inicio` como variable respuesta del efecto de orden.
- **Renombre justificado**: la columna del etiquetador deja de llamarse
  `sector_asignado`. Ese nombre queda reservado al consenso del corpus; con el renombre,
  el requisito de cegado ("no ver `sector_asignado`") deja de ser ambiguo. Por la misma
  razon los adicionales del etiquetador se llaman `sectores_adicionales_etiquetados`.
- **Validador unico** `evaluation/doble_etiquetado.py::validar_doble_etiquetado` (funcion
  pura) con CLI `python -m evaluation.doble_etiquetado --planilla ... --corpus ...
  --tarea ...` y exit codes por tipo de ofensa. Reglas: etiquetadores fijos por tarea
  (exactamente dos `E*` en doble etiquetado; ambos `O1` y `O2`, sin terceros, en brazo manual), cobertura
  (completa por ambos en doble etiquetado; al menos un operador por caso en brazo
  manual), sin duplicados, `id_caso` conocido, sectores
  canonicos, adicionales sin repetir el principal, `timestamp` (e `inicio` si se
  informa) parseables, sin columnas con PII, `tarea` valida, e `inicio` obligatorio y
  no posterior a `timestamp` en brazo manual.
- **Protocolo (runbook)** `docs/campana-medicion/runbook-doble-etiquetado.md`: sujetos
  elegibles y exclusiones, cegado, codebook, tamano (los 200 casos del corpus de ajuste;
  misma plantilla y mismo validador para el corpus independiente), aceptacion, versionado
  de la tabla primaria con SHA-256, tratamiento de discordancias, limitacion declarada si
  no se consiguen etiquetadores nuevos, y como llevar a mano una tabla parcial recuperada
  al esquema y pasarla por el mismo validador.
- **Conservacion de la tabla primaria como criterio de aceptacion**: la planilla validada
  se versiona sin PII en `evaluation/data/campana/doble_etiquetado.csv` junto a
  `evaluation/data/campana/README.md` con su SHA-256 y fecha (patron
  `evaluation/evidence/`).
- **Se elimina el importador** de la version anterior: no hay codigo de importacion; la
  recuperacion de data parcial es un procedimiento manual del runbook.

### Contrato con los otros changes

c-168 es el DUENO del esquema de planilla y del validador. c-165 (brazo manual,
`tarea = brazo_manual`), c-166 (corpus independiente, `id_caso` con prefijo `I`) y c-167
(kappa y exactitud manual) los ADOPTAN y no definen esquemas ni validadores propios.

- **Orden de APLICACION recomendado**: c-168 antes de la tarea 1.x de c-165 (el
  instrumento del brazo manual reutiliza este esquema y este validador).
- **Orden de ARCHIVO**: c-165 -> c-166 -> c-168 sigue siendo seguro (solo ADDED, sin
  requisitos repetidos en `evaluation-campaign-instrumentation`).

## Capabilities

### New Capabilities

- `evaluation-campaign-instrumentation`: c-168 AGREGA ECM-008, ECM-009 y ECM-010 a la
  capability creada por c-165 (ECM-001..003) y extendida por c-166 (ECM-004..007).

### Modified Capabilities

- None. El doble etiquetado se modela como instrumentacion de campana (ECM), no como
  cambio de contrato de `evaluation-framework` (que c-167 modifica).

## Impact

Archivos nuevos:

- `evaluation/doble_etiquetado.py` (validador puro + CLI, solo stdlib + `evaluation.corpus`).
- `evaluation/tests/test_doble_etiquetado.py` (tests offline, sin red).
- `evaluation/tests/fixtures/campana/doble_etiquetado_fixture.csv` (SINTETICO).
- `evaluation/data/plantilla_etiquetado.csv` (solo encabezado).
- `evaluation/data/campana/README.md` (procedencia, SHA-256, fecha, estado del cegado).
- `docs/campana-medicion/runbook-doble-etiquetado.md`.

Archivos modificados (solo documentacion de carpetas):

- `evaluation/data/README.md` (hoy afirma que no se trackea ningun CSV).
- `evaluation/tests/fixtures/README.md` (declara el fixture nuevo como SINTETICO).
- `.gitattributes` (fin de linea LF para los CSV versionados, para que el SHA-256
  coincida en Windows y Linux).

Archivos que se agregan DESPUES de la campana siguiendo el runbook (no al aplicar):
`evaluation/data/campana/doble_etiquetado.csv` (tabla primaria validada, sin PII) y
`evaluation/data/campana/registro_sujetos.csv` (alias, rol y persona seudonima
`P<n>`; sin nombres), ambos referenciados con su SHA-256 en `evaluation/data/campana/README.md`.

Sin cambios a `docs/Tesis/v9 (IA)/`, a las cadenas de sector (LOCKED), al corpus
(`data/corpus_evaluacion_pseudonimizado.json`), a `evaluation/corpus.py`, a
`evaluation/predicciones.json`, a `evaluation/report.md` ni a los numeros canonicos. Sin
datos de campo en el repositorio al aplicar: la tabla primaria se agrega despues de la
campana siguiendo el runbook.

## Risks

| Riesgo | Probabilidad | Mitigacion |
|--------|--------------|------------|
| Etiquetadores no independientes o no ciegos | Media | Runbook exige personas distintas de analistas originales, autores y operadores; registro de sujetos sin nombres; validador exige alias fijos por tarea (exactamente dos en doble etiquetado; ambos `O1` y `O2` en brazo manual) |
| No se consiguen etiquetadores nuevos | Media | Limitacion declarada obligatoria en el README de la tabla; prohibido presentarlo como cegado |
| Consenso contamina el re-etiquetado | Media | Renombre de columna; el runbook prohibe exponer `sector_asignado`, `sectores_adicionales`, predicciones y etiquetas del par |
| Cobertura parcial del corpus | Media | Validador exige registro de ambos etiquetadores por caso; falla accionable |
| Tabla primaria se pierde otra vez | Baja | Versionado con SHA-256 y test de integridad |
| Deriva de cadenas de sector | Baja | Validador importa `SECTORES_CANONICOS` |

## Rollback Plan

Eliminar la plantilla, el validador, sus tests y fixture, el README de `campana/` y el
runbook, y revertir las lineas de `evaluation/data/README.md`,
`evaluation/tests/fixtures/README.md` y `.gitattributes`. No hay migraciones ni cambios
de esquema del corpus; c-167 y los numeros canonicos quedan intactos.

## Dependencies

- `evaluation/corpus.py` (`SECTORES_CANONICOS`, `cargar_corpus`) y el corpus
  pseudonimizado `data/corpus_evaluacion_pseudonimizado.json`.
- c-165 y c-166 adoptan el esquema y el validador; c-167 consume la tabla validada y el
  registro de sujetos; c-169 reporta el estado del cegado (cumplido o limitacion
  declarada).

## Success Criteria

- [ ] Existe `evaluation/data/plantilla_etiquetado.csv` con las siete columnas en orden.
- [ ] `validar_doble_etiquetado` cubre las reglas (a)-(j) con tests offline en verde.
- [ ] El CLI devuelve exit code distinto de cero por tipo de ofensa.
- [ ] Existe el runbook con sujetos, cegado, codebook, tamano, aceptacion, versionado,
  discordancias, limitacion declarada y recuperacion manual.
- [ ] `evaluation/data/campana/README.md` define el versionado con SHA-256 de la tabla
  primaria, y su conservacion es criterio de aceptacion de la campana.
- [ ] `openspec validate --strict` en verde.
