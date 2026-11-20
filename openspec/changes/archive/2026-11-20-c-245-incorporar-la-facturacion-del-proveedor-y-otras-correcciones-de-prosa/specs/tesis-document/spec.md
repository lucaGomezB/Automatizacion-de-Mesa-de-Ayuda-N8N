<!--
  Delta de c-245 sobre la capacidad `tesis-document`.

  Requisito ADDED (no MODIFIED): distinguir el costo POR CORRIDA del total facturado
  por el proveedor en el PERIODO es una preocupacion nueva. No colisiona con
  "Fuentes y cotas de costos operativos" (openspec/specs/tesis-document/spec.md, L1736),
  que gobierna la Seccion 8.4, ni con "Acreditacion del nivel pago de la Gemini API con
  el registro de facturacion" (L8463), que gobierna la seccion 7 de 11-aspectos-legales.tex.
  El texto del body vive en el limite "Quinto" y en la nota de `tab:carga-inferencia` de
  `07-resultados.tex`.

  El requisito ADDED es de documento (no hay implementacion de codigo). El cambio de
  comportamiento es a nivel de spec, por lo que no aplica `skip_specs`.
-->

## ADDED Requirements

### Requirement: Distincion entre el costo por corrida y la facturacion del proveedor del periodo

El documento SHALL distinguir, en la prosa de la sonda de latencia con inferencia incluida, el costo **por corrida** del total facturado por el proveedor en el **periodo**. En el limite «Quinto» de `07-resultados.tex` y en la nota de `tab:carga-inferencia`, el texto SHALL declarar que el costo por corrida se calcula a partir de tokens con el precio declarado de la tesis (`gasto_origen = tokens_calculado`) y que la facturacion del periodo proviene del proveedor (Google Cloud Billing), como evidencia versionada distinta. La nota de `tab:carga-inferencia` SHALL citar, junto a los dos JSON de las corridas, las dos evidencias de facturacion (`evaluation/evidence/billing-gemini-2026-11-17-18-oficial.csv` y `billing-gemini-2026-11-17-18-resumen.csv`) con sus prefijos de SHA-256 (`f860b5cd\ldots` y `636fdd70\ldots`). El texto SHALL declarar el total del periodo **cerrado** (`455.309` tokens —`444.634` de entrada y `10.675` de salida— y USD `0,373501`), de la re-exportacion del `2026-11-20` con la ventana cerrada (la del 18/11 estaba abierta y subestimaba el 18/11). El texto SHALL declarar el contraste con `usage_metadata` de la corrida ampliada (la facturacion del `2026-11-18` —`286.259` tokens— coincide con los `281.568` tokens de su `usage_metadata`; el resto del periodo —`169.050` tokens del `2026-11-17`— corresponde a la corrida original, sin `usage_metadata`) y que el **precio queda confirmado** por coincidir el precio implicito con el escenario de la tesis (`0,75` USD por millon de entrada y `3,75` por millon de salida), de modo que NO es una diferencia de precio. El documento MUST NOT conservar ninguna afirmacion que presente el gasto como «no facturacion del proveedor» sin la distincion por corrida y por periodo. La incorporacion MUST NOT cambiar ninguna cifra canonica ni el contenido sustantivo, y MUST NOT introducir oraciones de mas de 60 palabras.

#### Scenario: Limite Quinto distingue por corrida y por periodo

- **WHEN** se lee el limite «Quinto» de la sonda de latencia en `07-resultados.tex`
- **THEN** declara que el costo por corrida se calcula desde tokens (`tokens_calculado`)
- **AND** declara que la facturacion del periodo es del proveedor (Cloud Billing) y evidencia aparte
- **AND** no afirma sin mas que el gasto es «no facturacion del proveedor»

#### Scenario: Nota de la tabla cita la evidencia de facturacion con sus hashes

- **WHEN** se lee la nota de `tab:carga-inferencia`
- **THEN** cita los dos JSON de las corridas
- **AND** cita `billing-gemini-2026-11-17-18-oficial.csv` (`f860b5cd\ldots`) y `billing-gemini-2026-11-17-18-resumen.csv` (`636fdd70\ldots`)

#### Scenario: Total del periodo cerrado

- **WHEN** se lee el total del periodo de la facturacion del proveedor
- **THEN** figura `455.309` tokens y USD `0,373501` como **total cerrado**
- **AND** se declara que la exportacion del 18/11 estaba abierta y subestimaba el 18/11, y que el total proviene de la re-exportacion cerrada del `2026-11-20`

#### Scenario: Precio confirmado y contraste con usage_metadata

- **WHEN** se lee el contraste entre la facturacion del periodo y la evidencia de la corrida ampliada
- **THEN** se declara que la facturacion del dia de la corrida ampliada (`2026-11-18`) coincide con su `usage_metadata` y que el resto del periodo (`2026-11-17`) corresponde a la corrida original, sin `usage_metadata`
- **AND** se declara que el precio implicito coincide con el escenario declarado de la tesis y que NO es una diferencia de precio

#### Scenario: Barrido de coherencia con la evidencia nueva

- **WHEN** se busca en `sections/*.tex` y en el memo cualquier afirmacion que dependa de la facturacion del proveedor
- **THEN** cada afirmacion refleja la distincion por corrida y por periodo
- **AND** la declaracion de uso de IA (Anexo I.3, `12-anexos.tex`) y `inventario-uso-asistentes-ia.md` conservan el conteo «162 de 1221» sin cifras stale
