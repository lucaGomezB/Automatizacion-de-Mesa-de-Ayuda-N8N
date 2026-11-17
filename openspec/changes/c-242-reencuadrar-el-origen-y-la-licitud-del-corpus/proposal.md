# Proposal: Reencuadrar el origen y la licitud del corpus

## Why

La tesis presenta su estudio empirico como realizado en una organizacion REAL (mediana,
sector servicios, provincia de Mendoza, aproximadamente 120 usuarios internos, cinco areas
funcionales). Los autores precisaron que esa organizacion es un **dispositivo narrativo**:
NO existe una organizacion adoptante real, ni la "carta de autorizacion emitida por la
organizacion adoptante", ni la notificacion de 120 empleados. Los incidentes SI son reales,
pero el corpus es una **mezcla de dos regimenes**: (a) incidentes reales del entorno
operativo del propio equipo, pseudonimizados (son datos personales: base de licitud =
consentimiento informado del grupo, articulo 5 inciso 1 de la Ley 25.326); y (b)
reconstrucciones de tipos de incidente reales construidas desde la practica, sin datos de
terceros (sin datos personales: no requiere base de licitud). La base de licitud de
empleador (articulo 5, inciso 2, apartado d) que §7.2 declara cae porque no hay empleador.
Las afirmaciones sin respaldo deben corregirse antes de la entrega.

Este change **absorbe y supersede** a
`c-241-precisar-la-base-de-licitud-en-la-seccion-7-5`: su premisa (base de empleador) es
invalida y su alcance (solo "precisar el inciso" de §7.5) queda subsumido aqui. NO elimina
c-241: lo retira el orquestador por separado.

## What Changes

- **BREAKING (afirmaciones de procedencia):** el documento deja de afirmar que existe una
  organizacion adoptante real, una carta de autorizacion y la notificacion de 120 empleados;
  declara el escenario como narrativo y el corpus como mezcla de los regimenes (a) y (b).
- **§7.2** (`11-aspectos-legales.tex`): la licitud NO se funda en la base de empleador
  (articulo 5, inciso 2, apartado d); se declara la base por regimen.
- **§7.5**: declara la base de licitud de los datos conservados por regimen, sin colapsarlas
  en una unica invocacion generica del articulo 5 con consentimiento.
- **§7.3**: encuadra la transferencia del articulo 12 efectivamente realizada durante el
  estudio sin instrumento suscrito (decision de autores).
- **§1.1, §1.2, §1.8, §4.1, §8.2, §9.1**: reencuadre del origen y de la validez externa o
  del escenario representativo.
- **`docs/seguridad/`**: reconcilia ROPA, registro de requisitos legales, acta T1 y
  clasificacion con los dos regimenes.
- **Compuertas de autores** (OQ-01 a OQ-05) y **visto bueno del director** antes de escribir
  cualquier `.tex`.

Fuera de alcance: reintroducir la validacion fuera de muestra retirada; recompilar, bump y
tag (c-239); legibilidad (c-238); y decidir por el agente la base legal sustantiva.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: reencuadre del origen y de la licitud. ADDED: encuadre honesto del origen
  del corpus y del entorno de estudio. MODIFIED: "Base de licitud conforme a la Ley 25.326"
  (§7.2), "Parrafo de licitud y alcance en §7.5 para los datos del corpus retirado",
  "§1.8 veraz: una sola organizacion y validacion dentro de la muestra", "Consistencia de la
  descripcion de la organizacion adoptante", "Validez externa declarada en las conclusiones
  con su remedio empirico" y "Retiro decidido de los textos del corpus independiente del
  repositorio publico".
- `security-governance-docs`: MODIFIED SGD-012 declara la base de licitud por regimen
  (consentimiento del grupo para el regimen (a); sin datos personales para el (b)).

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` | Modificado | §1.1, §1.2, §1.8: origen narrativo |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | §4.1: poblacion = entorno operativo del equipo |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | §8.2: validez externa |
| `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` | Modificado | §9.1: validez externa |
| `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` | Modificado | §7.2, §7.3, §7.5: licitud y transferencia |
| `docs/seguridad/*.md` | Modificado | ROPA, registro de requisitos legales, acta T1, clasificacion |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada del change y tabla de compuertas (autores) |
| `openspec/changes/c-241-...` | Superseded | Absorbido; NO se elimina aqui |

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Que el agente decida la base legal sustantiva | Media | OQ-02 y compuerta de autores antes de escribir; el requisito exige declarar por regimen |
| Perdida de lo verdadero (sistema, campanas, consentimiento real, pseudonimizacion) | Media | El encuadre preserva explicitamente lo verdadero |
| Contradiccion residual entre §7.2 y §7.5 | Media | Escenario de coherencia entre subsecciones |
| Reintroducir la validacion fuera de muestra retirada | Baja | Prohibicion explicita en el requisito de retiro |
| Fusionar un MODIFIED omitiendo escenarios | Alta | Cada MODIFIED reproduce el texto y TODOS sus escenarios vigentes |

## Rollback Plan

`git revert` de los commits de `.tex` y de `docs/seguridad/`. Las entradas de
`dictamen-correcciones.md` son aditivas y revertibles por separado. Los deltas de spec no
tocan `openspec/specs/` hasta el archivado; el delta ADDED no modifica requisitos existentes.

## Dependencies

- Ratificacion escrita de los autores (OQ-01 a OQ-05) y visto bueno del director:
  precondicion dura antes de escribir `.tex`.
- Coordinacion con c-238 (legibilidad) y c-239 (cierre, recompilacion y tag) sobre los mismos
  archivos; aplicar despues de c-238.
- c-241 queda superseded; su archivado no procede.

## Success Criteria

- [ ] El documento NO afirma organizacion adoptante real, carta de autorizacion ni
  notificacion de 120 empleados.
- [ ] El corpus se declara mezcla de regimenes (a) y (b), preservando el sistema, las
  campanas, el consentimiento documentado y la pseudonimizacion.
- [ ] §7.2 no usa la base de empleador; §7.5 declara la base por regimen sin colapsarlas.
- [ ] `openspec validate c-242-reencuadrar-el-origen-y-la-licitud-del-corpus --strict` y
  `openspec validate --all --strict` pasan.
