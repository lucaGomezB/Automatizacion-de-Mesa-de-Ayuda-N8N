# Proposal: Precisar la base de licitud en §7.5 (distinguir las dos bases)

## Why

El parrafo de licitud que c-240 agrego en §7.5 (`11-aspectos-legales.tex`,
`subsec:consentimiento-derechos`, ~L48) funda la licitud de los datos que se conservan en «el
articulo~5 de la Ley~25.326, con el consentimiento informado...». Esa frase colapsa dos bases que
la ley distingue y que §7.2 (`subsec:principios-datos`, L16) ya separa:

- **Corpus de 200 casos (derivado de empleados).** Su base es la que §7.2 declara: articulo~5,
  inciso~2, apartado~d) (relacion contractual/cientifica/profesional, que NO es consentimiento).
- **Campana complementaria (etiquetadores y operadores independientes, alias `E1`, `E2`, `O1`,
  `O2`).** Se apoya en el consentimiento informado (articulo~5, inciso~1).

La ley separa el consentimiento (art. 5, inc. 1) del caso en que no se requiere consentimiento
(art. 5, inc. 2 d). Invocar una unica vez «el articulo~5» con consentimiento para ambos artefactos
es impreciso y contradice §7.2. La correccion es una decision de redaccion legal de los autores, no
mecanica.

## What Changes

- **§7.5:** la oracion de licitud de los datos conservados distingue la base de cada artefacto y
  no colapsa ambas en «articulo 5 + consentimiento»; queda consistente con §7.2.
- **Compuerta de autores:** la asignacion del inciso/apartado por artefacto y la redaccion final se
  ratifican por escrito antes de escribir (OQ legal). El agente no decide la base sustantiva.

Fuera de alcance: reescribir §7.2; recompilar, bump y tag (`c-239`); retiro del corpus y §1.8
(`c-240`); legibilidad (`c-238`). No se toca ningun archivo `.tex` distinto de la oracion de licitud
de §7.5, ni `App/`, `n8n/` ni `evaluation/`.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se MODIFICA el requisito «Parrafo de licitud y alcance en §7.5 para los datos
  del corpus retirado» (introducido por c-240, aun NO archivado) para exigir que la clausula (iv)
  declare la base de licitud por artefacto, la distinga y no la colapse, consistente con §7.2.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` | Modificado | Oracion de licitud de §7.5 (~L48): base por artefacto |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada del change y tabla de compuertas (ratificacion legal) |
| Spec `tesis-document` | Delta | MODIFIED del requisito de c-240 (fusion tras archivar c-240) |
| Changes c-238, c-240 | Coordinacion, no edicion | Orden de aplicacion y de archivado |

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Redactar la base legal por decision del agente | Media | OQ de autores antes de escribir; el requisito exige consistencia con §7.2, no fija la base |
| Colapso persistente de las bases | Media | Escenarios «Bases distinguidas» y «Coherencia con §7.2» |
| Fusionar el delta antes de archivar c-240 | Alta | Orden documentado: `archive` falla con «not found» si la base no existe |
| Conflicto con c-238 sobre el mismo archivo | Media | Se aplica despues de c-238; localiza por texto (`rg -n`) |

## Rollback Plan

`git revert` del commit unico de edicion de `.tex` (reemplazo localizado de una oracion). La entrada
de `dictamen-correcciones.md` es aditiva y revertible por separado. El delta de spec no toca main
hasta el archivado.

## Dependencies

- **Aplicacion:** DESPUES de c-238 (tarea 6.3 parte oraciones de `11-aspectos-legales.tex`) y de
  c-240 (tarea 2.1, que escribio la oracion de licitud hoy imprecisa).
- **Archivado:** el delta MODIFICA un requisito que solo existe en el delta de c-240; c-241 SOLO
  puede archivarse DESPUES de archivar c-240 (si no, `openspec archive` falla con «not found»).
- Precondicion dura: ratificacion escrita de los autores de la base por artefacto y de la redaccion.

## Success Criteria

- [ ] §7.5 declara la base de licitud por artefacto y no colapsa ambas bases en «articulo 5 + consentimiento».
- [ ] La base del corpus de 200 es consistente con §7.2; ningun artefacto cuya base no sea el consentimiento se funda en el consentimiento.
- [ ] La ratificacion de los autores figura con fecha en `dictamen-correcciones.md`.
- [ ] `openspec validate c-241-precisar-la-base-de-licitud-en-la-seccion-7-5 --strict` pasa.
