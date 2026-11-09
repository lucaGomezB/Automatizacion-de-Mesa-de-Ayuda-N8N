# Proposal: Acreditar el nivel pago de la Gemini API y el consentimiento de los cuatro participantes

## Why

El dictamen CONEAU del 2026-11-09 sobre la release `v1.2.13` dejo dos puntos pendientes a
cargo de los autores (recomendacion B4 e item 13 del inventario): el nivel pago de la Gemini
API solo se respalda con una guia de configuracion, que no acredita un hecho operativo, y no
hay registro del consentimiento de los cuatro participantes de la campana complementaria. Son
debilidades de acreditacion y de etica que un jurado puede observar en la defensa. La release
`v1.2.15` las cierra con evidencia documental fisica (comprobante de facturacion y constancias
firmadas) sin incorporar datos personales al repositorio.

## What Changes

- **Nivel pago (7, transferencia internacional)**: se conserva que el servicio opero en el
  nivel pago de la Gemini API con creditos prepagos y que en ese nivel el proveedor no utiliza
  el contenido transferido para mejorar sus productos (`Google2026_gemini_api_pricing`); se
  retira la guia de configuracion como prueba y se agrega que el comprobante de facturacion se
  conserva bajo custodia del director y no se versiona porque contiene datos de la cuenta.
- **Consentimiento (7, consentimiento y derechos)**: se reemplaza la declaracion de ausencia de
  registro por el procedimiento real: informacion verbal previa a las tareas (proposito,
  registros pseudonimizados, voluntariedad y derecho a retirarse) y confirmacion escrita
  posterior; los originales firmados quedan en el expediente fisico del trabajo, bajo custodia
  del director, y no se versionan porque contienen datos personales. El repositorio conserva
  la plantilla de la confirmacion y el registro de que se obtuvo para `E1`, `E2`, `O1` y `O2`.
  Sin nombres reales: solo alias y codigos `P<n>`.
- **Plantilla nueva**: `docs/campana-medicion/confirmacion-posterior-consentimiento.md`, de una
  pagina, con marcadores de posicion, los cuatro puntos y la tabla de registro
  `alias, rol, fecha_informacion_verbal, fecha_confirmacion, custodia`.
- **Registro y release**: seccion `c-193` en `dictamen-correcciones.md` (B4 e item 13), FASE 58
  en `CHANGES.md`, regeneracion de `tesis_para_agente.md` y `paper/compilacion.md`, y release
  `v1.2.15` con el patron de hash del Anexo B de c-188 (oracion de verificacion en el commit de
  contenido, hash real en el commit posterior; el PDF etiquetado no imprime un hash ajeno).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos sobre la acreditacion del nivel pago con el registro
  de facturacion, el registro del consentimiento verbal y la confirmacion escrita posterior, la
  plantilla de confirmacion versionada y la neutralidad de paginas de `v1.2.15`; se modifican
  los requisitos de forma del documento y de trazabilidad del dictamen del 9-11 sobre `v1.2.13`
  para que cubran B4 y el item 13.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex`
  (`subsec:transferencia-internacional` y `subsec:consentimiento-derechos`).
- `docs/campana-medicion/confirmacion-posterior-consentimiento.md` (nuevo).
- `docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion c-193), `CHANGES.md` (FASE 58),
  `docs/Tesis/v10 (IA)/tesis_para_agente.md` y `paper/compilacion.md` regenerados.
- Artefactos de release: Anexo B (`12-anexos.tex`) con el tag `v1.2.15` y la oracion
  `git rev-list -n1 v1.2.15`; tag anotado `v1.2.15` y commit posterior del hash.
- Gobernanza: MEDIUM/HIGH (datos personales, etica y release). Los originales firmados y el
  comprobante de facturacion no entran al repositorio ni a Engram.
