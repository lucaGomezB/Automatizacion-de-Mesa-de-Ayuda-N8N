# Design: Aplicar el reencuadre autorizado de cuarta instancia

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque (verificado leyendo los
archivos y la devolucion de cuarta instancia):

- **Precedente c-242 (misma familia de reencuadre).** c-242 ya declaro la organizacion como
  dispositivo narrativo y el corpus como mezcla de los regimenes (a) y (b). Su delta (ADDED
  "Encuadre honesto del origen del corpus y del entorno de estudio" + MODIFIED de base de
  licitud / §1.8 / consistencia / validez externa / retiro) NO esta archivado: c-242 sigue
  `in-progress` con 30/31 tareas y su **visto bueno del director (tarea 2.6) sin marcar**. Por
  eso el reencuadre de c-242 aun vive en el delta, no en `openspec/specs/tesis-document/spec.md`.
  c-246 cierra los residuales que c-242 dejo deliberadamente cualitativos (R-02: composicion
  numerica) o que no alcanzo (R-03, R-05, R-06, R-07, B-01).
- **La devolucion fija la precondicion de defensa.** El tribunal fija fecha solo con R-01..R-07
  aplicados + visto bueno escrito del director. El visto bueno del director pasa de "recomendado
  por convencion" (c-242) a **condicion dura del tribunal**. c-246 debe documentar esa compuerta
  como gate duro.
- **Residuales concretos (verificados contra el arbol actual).** R-01:
  `01-introduccion.tex:18` ("promedio de una semana completa de operacion"),
  `04-marco-metodologico.tex:64` ("mas de tres anos de antiguedad en la mesa de ayuda"), mas
  menciones de "la organizacion" como hecho (`01-introduccion.tex:64`). R-02:
  `12-anexos.tex:235` ("corpus real pseudonimizado"); falta el desglose y la amenaza de §4.8.
  R-03: `04-marco-metodologico.tex:46` ("sobre la operacion normal de la mesa" + "del 16 de
  junio al 10 de septiembre de 2026"). R-04: `08-discusion.tex` (lineas 14, 74, 80, 109) y
  `12-anexos.tex:319` con "2.646" sin rotular como supuesto. R-05:
  `11-aspectos-legales.tex:38` ("politica de privacidad... " + "responsable... designado por la
  organizacion") y la fecha del acta ("2026-10-02" en la transferencia). R-06:
  `09-conclusiones.tex:49` ("el unico contexto en que se evaluo") y `08-discusion.tex:50`
  ("un unico entorno operativo"). R-07: `12-anexos.tex` `subsec:nota-versiones` (lineas
  233-238) sin la nota del escenario ficticio. B-01: `01-introduccion.tex:48` y `:72`
  `\sectorcad{si}` en prosa.
- **Lo que NO cambia (preservado por el tribunal).** Arquitectura, codigo y latencias del flujo
  automatizado: los 118 tiempos de correo/formulario de la corrida del 2/10 coinciden con la
  base; la campana complementaria del 5/11 (E1, E2, O1, O2) se conserva. No se reintroduce la
  validacion fuera de muestra (c-235/c-242 la retiraron).

## Goals / Non-Goals

**Goals:**

- Aplicar R-01..R-07 + B-01 como un cambio de PROSA UNICAMENTE, con compuertas de autores
  (OQ) y el visto bueno del director como gate DURO (condicion del tribunal).
- Declarar el flujo manual como medicion controlada / tarea de laboratorio (R-03), condicion
  explicita del tribunal para la calificacion proyectada de 7,5. Esta es la posicion que
  estructura las tareas.
- Reescribir el capitulo 7 (R-05) fundando el regimen (a) en el consentimiento del grupo
  (art. 5 inc. 1), reconciliando la frase del tribunal "incidentes reales de terceros" con el
  hecho de que los titulares son los propios integrantes del grupo.
- Documentar —sin inventar— los desgloses que solo los autores pueden aportar (R-02
  composicion, R-05 redaccion y fecha del acta).

**Non-Goals:**

- No tocar arquitectura, codigo ni latencias (preservado por el tribunal).
- No reintroducir la validacion fuera de muestra retirada.
- No recompilar, bump ni tag (c-239).
- No decidir por el agente ni el desglose de R-02, ni la redaccion/fecha de R-05.
- No editar ningun `.tex` en esta fase (planning only); la escritura es del apply, despues del
  visto bueno.

## Decisions

### D1 — Capacidad NUEVA dedicada (no MODIFIED sobre tesis-document)

Se crea la capacidad `tesis-reencuadre-cuarta-instancia` como ADDED, en lugar de MODIFICAR
requisitos de `tesis-document`. Motivo: c-242 esta `in-progress` y sus MODIFIED (base de
licitud, §1.8, consistencia, validez externa) aun no estan en main; intentar un MODIFIED de
esos requisitos desde c-246 produciria una pila de dependencias no archivadas y una fusion
fragil. Los residuales de c-246 son comportamientos NUEVOS de prosa (no revisiones de un
requisito ya en main), por lo que ADDED es la operacion correcta segun la guia del CLI. La
reconciliacion final con `tesis-document` ocurre al archivar en orden (c-242 primero), no en
esta fase de planning.

Alternativa descartada: MODIFIED de los seis requisitos de c-242. Se descarta por el riesgo de
fusion sobre main desincronizado y porque c-246 no cambia la semantica de un requisito vigente
en main, sino que agrega exigencias nuevas del tribunal.

### D2 — Resolver R-03 como "tarea de laboratorio" (condicion de 7,5)

La estructura del change asume la lectura que el tribunal premia: el flujo manual de la
campana 2026-10 fue una **medicion controlada / tarea de laboratorio**, y "61,6 s" se lee como
medicion de tarea controlada. Es factual: §4.2 ya describe el cronometraje por pares (A1/T1).
Esta decision queda flaggeada como compuerta OQ para confirmacion final de los autores, pero
las tareas y escenarios se redactan sobre esa lectura.

### D3 — R-05: reconciliar "terceros" del tribunal con "el propio grupo"

El dictamen pregunta "con que base usaron los incidentes reales de terceros" (Q7). La realidad
declarada por el grupo es que los titulares del regimen (a) son los PROPIOS integrantes del
grupo (base: consentimiento informado, art. 5 inc. 1), no terceros ajenos. La prosa debe
aclarar esa distincion; el agente MUST NOT inventar una base para terceros. Flaggeado como OQ:
es una decision de autores, no del agente.

### D4 — Compuertas de autores y gate duro del director

Toda escritura de `.tex` queda bloqueada hasta: (i) la respuesta escrita de los autores a los
OQ (composicion R-02; redaccion/fecha R-05; confirmacion de R-03 como laboratorio) y (ii) el
**visto bueno escrito del director**, que esta devolucion eleva a condicion dura del tribunal
para fijar fecha. Las compuertas se registran con fecha y responsable en
`docs/Tesis/Correcciones/dictamen-correcciones.md`. El agente no decide desglose ni redaccion.

### D5 — Verificacion estilo "prosa TDD"

Igual que c-238/c-242: cada tarea de edicion tiene una verificacion ANTES (linea base, muestra
la afirmacion incorrecta via `rg`) y DESPUES (estado deseado), y ambas salidas se reportan en
`dictamen-correcciones.md` (seccion `c-246`). Esto sustituye al TDD de codigo (no hay codigo en
un change de prosa) y preserva la trazabilidad que exige la auditoria de la tesis.

### D6 — Sin cambios a cifras canonicas del sistema/campana

El reencuadre re-rotula (escenario/parametros/supuestos) pero MUST NOT cambiar el valor de
ningun numero canonico del sistema ni de la campana (61,6 s, 17,76 s, W = 363, 73,5 %, etc.).
R-04 solo anade el rotulo de "supuesto" a 2.646; no altera la formula 42 x 63.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente inventa el desglose R-02 o la redaccion/fecha R-05] | Compuertas OQ; los escenarios exigen consignar la respuesta de autores con fecha; sin respuesta, la tarea queda bloqueada |
| [Leer "terceros" literal y fundar una base para terceros ajenos] | D3: la prosa aclara que los titulares son el propio grupo; OQ de autores |
| [No declarar R-03 como laboratorio y perder la proyeccion a 7,5] | D2: la estructura asume la lectura de laboratorio, flageada como OQ de confirmacion |
| [Dependencia de c-242 no archivado] | c-246 es una capacidad ADDED independiente; el orden de archivado c-242 → c-246 se documenta; no se fusiona nada sobre main desincronizado |
| [Perder lo verdadero (sistema, campanas, consentimiento, pseudonimizacion)] | D6 + Non-Goals explicitos; el reencuadre re-rotula, no retira resultados |
| [Reintroducir la validacion fuera de muestra] | Non-Goals y prohibicion heredada de c-242/c-235 |
| [Cambiar un numero canonico al re-rotular] | Escenario "valores canonicos intactos"; `rg` de cifras antes/despues |
| [Escribir prosa sin el visto bueno del director] | Visto bueno como gate DURO (condicion del tribunal); tarea de compuerta bloqueante |

## Migration Plan

1. **Compuertas (gate duro):** registrar las respuestas de autores a los OQ (R-02 desglose,
   R-05 redaccion/fecha, R-03 confirmacion de laboratorio) y el **visto bueno escrito del
   director**, con fecha y responsable, en `dictamen-correcciones.md` (tabla c-246). Precondicion
   dura antes de cualquier edicion.
2. **Prosa (apply, despues del gate):** aplicar R-01..R-07 + B-01 sobre
   `01-introduccion.tex`, `04-marco-metodologico.tex`, `08-discusion.tex`,
   `09-conclusiones.tex`, `11-aspectos-legales.tex` y `12-anexos.tex`, con verificacion
   ANTES/DESPUES por tarea (D5).
3. **Verificacion de coherencia:** bateria `rg` de residuales (organizacion real, base de
   empleador, "operacion normal", "una sola organizacion", `\sectorcad{si}` en prosa,
   "corpus real pseudonimizado") + compilacion de verificacion en directorio temporal.
4. **Registro y cierre:** entrada c-246 en `dictamen-correcciones.md`; `openspec validate`
   del change y `--all --strict`.

Orden de archivado recomendado (no en esta fase): c-242 antes que c-246, para que el
reencuadre de c-242 aterrice en main antes de reconciliar los residuales de c-246.

## Open Questions

- **OQ-01 (autores, CONFIRMADA 2026-11-20):** composicion numerica por canal — **119 reales**
  (regimen (a)) = 66 correo electronico + 53 formulario web; **81 reconstrucciones** (regimen
  (b)) = 81 telefonicos. Las reconstrucciones las escribio el autor que recolecto los incidentes,
  SIN asistente de IA, anotando una descripcion general, sin detalles explicitos y pseudonimizada,
  de cada llamada telefonica recibida en su trabajo. Supera a c-242 D5 (que, por falta de registro
  primario, declaro la mezcla como cualitativa y sin desglose por canal): el autor aporta ahora el
  desglose respaldable, por lo que la tesis puede declarar la composicion numerica que exige R-02.
  La tarea 4.2 consigna el desglose por canal sin inventar ningun numero.
- **OQ-02 (autores, CONFIRMADA 2026-11-20):** la base del regimen (a) es el consentimiento
  informado del propio grupo (art. 5 inc. 1); los incidentes reales son del propio equipo, no
  terceros ajenos. Fechas: la **firma real del acta es 2026-11-20**; el "2026-10-02" que hoy
  figura corresponde a la **notificacion** (correcta como tal), no a la firma. La tarea 5.3 debe
  consignar la firma el 2026-11-20 y reenmarcar "2026-10-02" como fecha de notificacion.
- **OQ-03 (autores, CONFIRMADA 2026-11-20):** el flujo manual de la campana 2026-10 se declara
  como medicion controlada / tarea de laboratorio; los 61,6 s se leen como medicion de tarea
  controlada. La descripcion factual (donde, sobre que textos, quienes A1/T1, fechas) ya esta
  en §4.2/§4.4; el apply la redacta sin inventar (tarea 3.2).
- **Visto bueno del director (gate duro):** condicion del tribunal para fijar fecha; sin el, no
  se escribe prosa.