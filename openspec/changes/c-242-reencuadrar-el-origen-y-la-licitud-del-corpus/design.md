# Design: Reencuadrar el origen y la licitud del corpus

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque (verificado leyendo
los archivos):

- **Escenario real vs narrativo.** La tesis afirma hoy una organizacion real: `01-introduccion.tex`
  §1.1 (L16) "organizacion mediana del sector servicios con sede en Mendoza... ~120 usuarios...
  42 incidentes diarios"; §1.8 (L72) "corpus de 200 casos... recolectado en una unica
  organizacion mediana... ~120 usuarios"; §1.8 (L76) limitacion geografica. `04-marco-metodologico.tex`
  §4.1 (L46) "incidentes... reportados a la mesa de ayuda de la organizacion analizada".
  Los autores precisaron que la organizacion es un dispositivo narrativo: no hay adoptante real
  ni carta de autorizacion.
- **Licitud hoy (a corregir).** `11-aspectos-legales.tex` §7.2 (L16) funda la licitud en
  articulo~5, inciso~2, apartado~d) "la organizacion es la empleadora y trata datos de sus
  propios empleados"; §7.5 (L40) afirma la notificacion de "los 120 empleados" y "una carta de
  autorizacion emitida por la organizacion adoptante"; §7.5 (L48) funda la licitud de lo
  conservado en "el articulo~5... con el consentimiento informado" (colapsa). §7.3 (L30)
  declara el instrumento de transferencia como requisito previo de "la organizacion adoptante".
- **Validez externa.** `08-discusion.tex` (L50) y `09-conclusiones.tex` (L51) declaran validez
  externa acotada a "una sola organizacion... Mendoza".
- **Requisitos en main.** Los requisitos a MODIFICAR viven en `openspec/specs/tesis-document/spec.md`
  (L1000, L1859, L10225, L10247, L10276, L10297). c-240 ya esta archivado (2026-11-17), por lo
  que sus tres requisitos estan en main y un MODIFIED de c-242 SI fusiona sin depender de c-240.
- **Docs de gobernanza ya alineados a medias.** `docs/seguridad/registro-requisitos-legales.md`
  §5 y `registro-actividades-tratamiento.md` §5 declaran al grupo como responsable (no la
  UTN-FRM) y al adoptante como "rol funcional generico" (T3); pero el T2 (corpus) declara como
  salvaguarda solo "pseudonimizacion" sin una base de licitud por regimen. SGD-012 es el
  requisito que los gobierna.
- **c-241 (absorbido).** `c-241-precisar-la-base-de-licitud-en-la-seccion-7-5` propuso precisar
  el inciso de §7.5 asumiendo la base de empleador. Su premisa cae; su analisis del colapso y
  su estructura de compuertas se conservan aqui.

## Goals / Non-Goals

**Goals:**

- Que el documento declare el origen honesto: escenario narrativo y corpus como mezcla de los
  regimenes (a) y (b).
- Que §7.2 deje de fundar la licitud en la base de empleador y que §7.5 declare la base por
  regimen, sin colapsarlas.
- Que `docs/seguridad/` reconcilie la base de licitud del corpus con los dos regimenes.
- Dejar la decision sustantiva (base legal por regimen, redaccion final, tratamiento de las
  cifras y de la transferencia sin instrumento) en manos de los autores, con compuertas.

**Non-Goals:**

- Reintroducir la validacion fuera de muestra retirada ni el corpus independiente como evidencia.
- Reescribir el sistema, las campanas, el consentimiento real ni la pseudonimizacion.
- Decidir por el agente la base legal o el texto final.
- Tocar la legibilidad (c-238), el cierre/recompilacion/tag (c-239) ni la validacion fuera de
  muestra (c-235).

## Decisions

### D1 — Delta: MODIFIED contra requisitos de main + un ADDED

Los requisitos que se modifican ya existen en `openspec/specs/tesis-document/spec.md`, por lo
que `## MODIFIED Requirements` con el header **identico** fusiona sin depender de otro change
(contraste con c-241, que dependia del delta no archivado de c-240). Cada bloque reproduce el
texto completo y TODOS los escenarios vigentes, porque `openspec archive` rechaza un MODIFIED
que omita un escenario presente.

Alternativa descartada: solo AGREGAR un requisito nuevo y no tocar los existentes. Se descarta
porque dejaria requisitos contradictorios vigentes (§7.2 con base de empleador, §9.1 con "una
sola organizacion").

### D2 — Que se modifica y que se agrega (tesis-document)

| Requisito | Operacion | Motivo |
|---|---|---|
| `Base de licitud conforme a la Ley 25.326` (§7.2) | MODIFIED | La base de empleador (art. 5 inc. 2 d) cae: no hay empleador |
| `Parrafo de licitud y alcance en §7.5...` | MODIFIED | Debe declarar la base por regimen (a)/(b), sin colapsar |
| `§1.8 veraz: una sola organizacion...` | MODIFIED | El escenario no es una organizacion real |
| `Consistencia de la descripcion de la organizacion adoptante` | MODIFIED | El escenario pasa a ser referencia narrativa |
| `Validez externa declarada en las conclusiones...` (§9.1) | MODIFIED | "una sola organizacion" pasa a "unico entorno (escenario)" |
| `Retiro decidido de los textos del corpus independiente...` | MODIFIED | Alinea el caracter de los textos con el regimen (b); el retiro se mantiene |
| `Encuadre honesto del origen del corpus y del entorno de estudio` | ADDED | Comportamiento nuevo: declarar no-realidad del escenario y los dos regimenes |

El ADDED cubre §1.1, §1.2, §1.4/§4.1 y §8.2 (para los que no existe requisito dedicado). Se
elige ADDED (no MODIFIED) porque es una preocupacion nueva, no un cambio de uno existente.

### D3 — Docs de gobernanza: MODIFIED de SGD-012

`security-governance-docs` ya describe al adoptante como "rol funcional generico" y al grupo
como responsable durante la tesis; solo falta la base de licitud por regimen del corpus. Se
MODIFICA SGD-012 (que gobierna el ROPA y el registro de requisitos legales y cubre el acta T1 y
la clasificacion). No se tocan SGD-007, SGD-010/011 ni el resto: ya son consistentes con el
rol generico del adoptante.

### D4 — Preservar lo verdadero

El encuadre NO es un retiro de resultados: el sistema, las campanas, los participantes
(`E1`, `E2`, `O1`, `O2` y el operador con debriefing), su consentimiento documentado y la
pseudonimizacion se preservan y se declaran verdaderos. Las cifras del escenario (120 usuarios,
42 incidentes diarios, 2.646) y su tratamiento quedan en OQ-05.

### D5 — Politica de compuertas

Toda escritura de `.tex` y de `docs/seguridad/` queda bloqueada hasta la ratificacion escrita
de los autores (OQ-01 a OQ-05) y el visto bueno del director. Las compuertas se registran con
fecha y responsable en `dictamen-correcciones.md`. El agente no decide la base legal.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente decide la base legal] | El requisito exige declarar por regimen y consistencia con §7.2; la asignacion queda en OQ-02, con compuerta |
| [Perdida de lo verdadero] | Escenario "Lo verdadero preservado" en el ADDED; Non-Goals explicitos |
| [Contradiccion entre requisitos viejos y el reencuadre] | Se MODIFICAN todos los requisitos que afirman la organizacion real o la base de empleador |
| [Reintroducir la validacion retirada] | Escenario "Retiro no revertido por el reencuadre" |
| [Perdida de detalle al fusionar MODIFIED] | Cada MODIFIED reproduce texto y TODOS los escenarios vigentes (D1) |
| [Conflicto con c-238/c-239 sobre los mismos archivos] | Aplicar despues de c-238; c-239 recompila y etiqueta al final |

## Migration Plan

1. **Compuertas de autores (OQ-01 a OQ-05) y visto bueno del director:** registrar la
   ratificacion en `dictamen-correcciones.md` (fecha, responsable). Precondicion dura.
2. **`tesis-document` (prosa):** aplicar el reencuadre del origen (§1.1, §1.2, §1.8, §4.1,
   §8.2, §9.1) y la licitud por regimen (§7.2, §7.5), y encuadrar §7.3 (transferencia sin
   instrumento). Solo despues de la compuerta.
3. **`security-governance-docs`:** reconciliar el ROPA, el registro de requisitos legales, el
   acta T1 y la clasificacion con los dos regimenes.
4. **Registro y cierre:** entrada de c-242 en `dictamen-correcciones.md`; bateria de `rg`;
   validacion de OpenSpec.

Rollback: `git revert` de los commits de `.tex` y de `docs/seguridad/`; las entradas de
`dictamen-correcciones.md` son aditivas y revertibles por separado.

## Open Questions

- **OQ-01 (autores, director):** ratificar el reencuadre del origen (NO hay organizacion real;
  el corpus es mezcla de los regimenes (a) y (b)). Sin respuesta, las tareas de prosa quedan
  bloqueadas.
- **OQ-02 (autores, legal):** ratificar la base de licitud por regimen (regimen (a):
  consentimiento informado del grupo, art. 5 inc. 1, + pseudonimizacion; regimen (b): sin datos
  personales, sin base) y la redaccion final de §7.2 y §7.5 declarando AMBOS regimenes.
- **OQ-03 (autores, legal):** decidir como tratar la transferencia del art. 12 efectivamente
  realizada durante el estudio sin instrumento suscrito (textos pseudonimizados a Gemini;
  audio crudo recitado). Debe reflejarse en §7.3.
- **OQ-04 (autores):** fijar la descripcion de la validez externa / el "escenario
  representativo" en §1.8, §8.2 y §9.1.
- **OQ-05 (autores):** decidir que hacer con la proyeccion "42 incidentes diarios / universo
  2.646" y con los "120 usuarios" una vez que la organizacion no es real (conservar como
  dispositivo narrativo rotulado, reformular o retirar).
- **Visto bueno del director:** requerido porque el change altera lo que la tesis afirma sobre
  la procedencia de sus datos.
