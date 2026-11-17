# Design: Precisar la base de licitud en §7.5 (distinguir las dos bases)

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque:

- **Hallazgo.** c-240 (commit `d7fd6ec`) agrego en §7.5 (`subsec:consentimiento-derechos`, ~L48) la
  oracion: «La licitud de los datos que si se conservan, el corpus de 200 casos pseudonimizado y la
  campana complementaria, se funda en el articulo~5 de la Ley~25.326, con el consentimiento informado
  descrito en esta subseccion y la pseudonimizacion de la `subsec:transferencia-internacional`.»
- **Contradiccion con §7.2.** `subsec:principios-datos` (L16) declara que la licitud del tratamiento
  de datos de empleados «se funda en el articulo~5, inciso~2, apartado~d) ... Esta base se distingue
  del consentimiento analizado para el corpus academico en la `subsec:consentimiento-derechos`».
- **Texto de la ley.** El articulo~5 distingue el consentimiento (inc.~1) del tratamiento que no lo
  requiere, entre ellos el que deriva de una relacion contractual/cientifica/profesional (inc.~2 d).
- **Ubicacion del requisito.** El requisito «Parrafo de licitud y alcance en §7.5 para los datos del
  corpus retirado» vive SOLO en el delta de c-240
  (`openspec/changes/c-240-cerrar-el-residual-de-k-02/specs/tesis-document/spec.md:3`). NO existe en
  `openspec/specs/tesis-document/spec.md` (main) porque c-240 aplica pero NO esta archivado.
- **Archivo y otras ediciones.** §7.5 = `11-aspectos-legales.tex` `subsec:consentimiento-derechos`.
  c-235 ya lo edito (tarea 6.1, L48); c-240 escribio la oracion imprecisa (tarea 2.1, `[x]`); c-238
  lo editara (tarea 6.3, partir oraciones de mas de 60 palabras). La oracion a corregir esta, por
  tanto, al final de una cadena de ediciones sobre el mismo archivo.

## Goals / Non-Goals

**Goals:**

- Que §7.5 declare la base de licitud por artefacto conservado y NO colapse ambas bases.
- Que la base del corpus de 200 sea consistente con §7.2, sin fundar en consentimiento lo que no lo es.
- Dejar la decision sustantiva (inciso por artefacto) en manos de los autores, con compuerta.

**Non-Goals:**

- Reescribir §7.2 ni el requisito «Base de licitud conforme a la Ley 25.326» (main), que ya gobierna
  la base de §7.2.
- Decidir por el agente cual inciso corresponde a cada artefacto.
- Tocar el retiro del corpus, §1.8 (c-240), la legibilidad (c-238) o el tag (c-239).

## Decisions

### D1 — Estructura del delta: MODIFIED contra el requisito de c-240

El requisito que se cambia es el que c-240 agrego (el parrafo de §7.5). La opcion directa es
`## MODIFIED Requirements` con el header **identico** («Parrafo de licitud y alcance en §7.5 para los
datos del corpus retirado»): en MODIFIED, renombrar el header rompe la fusion (se busca por texto).

**Verificacion empirica de la restriccion de orden (investigada, no asumida):**

- `openspec validate c-241-... --strict` **NO** verifica la existencia de la base: valida estructura
  (escenarios en `####`, SHALL/MUST). Con el delta escrito, pasa (ver `tasks.md` 5.1).
- `openspec archive` **SI** la exige: con la base ausente falla con
  `MODIFIED ... not found` sin modificar archivos; y exige reproducir TODOS los escenarios vigentes
  del requisito (`current spec contains scenario(s) not present in the modified block`).

**Consecuencia (dependencia de orden, critica):** c-241 SOLO puede archivarse DESPUES de archivar
c-240. Consecuencia de contenido: el delta reproduce el texto completo del requisito y sus CUATRO
escenarios vigentes (`Parrafo presente`, `Sin datos de terceros y retiro declarados`, `Transferencia
y licitud de lo conservado`, `Respaldo registrado`), actualizados, mas los nuevos.

Alternativa considerada y descartada (por ahora): MODIFICAR el requisito existente en main «Base de
licitud conforme a la Ley 25.326» (que gobierna §7.2 y ya esta en main, por lo que archivaria sin
depender de c-240). Se descarta porque el objeto del cambio es la oracion de §7.5 introducida por
c-240; tocar el requisito de §7.2 ampliaria el alcance. Queda disponible si los autores prefieren
eliminar la dependencia de archivado de c-240.

### D2 — Analisis de las dos bases (contenido, no decision del agente)

| Artefacto conservado | Origen del dato | Base que el texto debe distinguir |
|---|---|---|
| Corpus de 200 casos pseudonimizado | Incidentes de empleados de la organizacion | La que §7.2 declara para datos derivados de la relacion de empleo: articulo~5, inciso~2, apartado~d) (NO consentimiento) |
| Campana complementaria | Sujetos independientes (`E1`, `E2`, `O1`, `O2`) | Consentimiento informado (articulo~5, inciso~1), o la base que los autores ratifiquen |

El requisito exige la DISTINCION y la consistencia con §7.2; NO fija la base del segundo artefacto.
La asignacion exacta es la OQ-01 (autores). El defecto a corregir no es la eleccion del inciso, sino
el colapso de ambos en «articulo 5 + consentimiento», que (a) atribuye consentimiento a un corpus
cuya base §7.2 declara distinta y (b) omite el inciso que §7.2 si precisa.

Alternativa descartada: dejar §7.5 como esta. El tribunal de tercera instancia ya senalo §7.5
(K-02) y la contradiccion con §7.2 es verificable; la imprecision legal en una tesis auditada no se
mantiene.

### D3 — Codificacion de la dependencia de orden

- **Change-level:** en `proposal.md` (secciones Dependencies y Risks) y en este design (D1 y
  Migration Plan seccion 3).
- **Spec-level:** (i) eleccion estructural `## MODIFIED` contra un requisito cuya base solo existe
  en el delta de c-240 — la dependencia es estructural, no solo documental; (ii) un comentario HTML
  de encabezado en `specs/tesis-document/spec.md` que la declara (tolerado por `validate` y
  `archive`, verificado); (iii) dependencia de aplicacion: ejecutar c-241 despues de c-238 y c-240.

### D4 — Politica de deltas

Solo MODIFIED, un unico requisito en `tesis-document`. No se AGREGAN requisitos (evita fragmentar
§7.5 en dos contratos) ni se tocan otros requisitos de `tesis-document`. Sin `skip_specs`: hay cambio
de comportamiento a nivel de spec.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente decide la base legal] | El requisito exige distinguir y ser consistente con §7.2; la asignacion queda en OQ-01 con compuerta de autores |
| [Colapso persistente de las bases] | Escenarios «Bases de licitud distinguidas por artefacto» y «Coherencia con §7.2» |
| [Fusionar el delta antes de archivar c-240] | Dependencia documentada + comentario en el delta; `archive` falla fuerte con «not found» (sin perdida de datos) |
| [Conflicto con c-238 sobre el mismo archivo] | Aplicar despues de c-238; localizar por texto (`rg -n`) |
| [Perdida de detalle al fusionar MODIFIED] | El delta reproduce texto y TODOS los escenarios vigentes del requisito |

## Migration Plan

1. Compuertas de autores: registrar en `dictamen-correcciones.md` la ratificacion de la base por
   artefacto (OQ-01) y de la redaccion final (OQ-02).
2. §7.5: reescribir la oracion de licitud de los datos conservados para declarar la base por
   artefacto, consistente con §7.2.
3. Orden: aplicar despues de c-238 (tarea 6.3) y de c-240 (tarea 2.1); archivar solo despues de
   archivar c-240.
4. Cierre: `openspec validate --strict` y bateria de `rg`.

Rollback: `git revert` del commit de `.tex`; la entrada de `dictamen-correcciones.md` es aditiva.

## Open Questions

- **OQ-01 (autores, legal):** ratificar que la base del corpus de 200 es la de §7.2 (articulo~5,
  inciso~2, apartado~d) y que la de la campana complementaria es el consentimiento (articulo~5,
  inciso~1), o indicar la asignacion correcta por artefacto. Sin respuesta, la oracion no se escribe.
- **OQ-02 (autores):** aprobar la redaccion final de la oracion de licitud por artefacto.
- **OQ-03 (fuera de alcance, registrar sin expandir):** revisar si la misma imprecision (invocar
  «articulo~5» sin distinguir la base) reaparece en otra parte del capitulo (por ejemplo §7.7,
  `subsec:cumplimiento-legal`, L116). No se corrige en este change; solo se deja anotada.
