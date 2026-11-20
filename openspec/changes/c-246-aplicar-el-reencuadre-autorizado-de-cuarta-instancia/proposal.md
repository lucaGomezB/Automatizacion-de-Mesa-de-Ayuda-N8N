# Proposal: Aplicar el reencuadre autorizado de cuarta instancia

## Why

La devolucion de cuarta instancia (19/11/2026) dicta **"APTA PARA DEFENSA"**, condicionada a
que la proxima version aplique el reencuadre autorizado (R-01 a R-07) y cierre la observacion
baja B-01. Calificacion provisional 7,2/10 (antes 6,7); proyectada 7,5/10 si R-03 se resuelve
declarando el flujo manual como tarea de laboratorio. La version auditada v1.6.0 (tag) sigue
afirmando en mas de veinte paginas una organizacion real, mediciones de su operacion, una base
legal de empleador, una carta de autorizacion y la notificacion de 120 empleados. El arbol de
trabajo actual tiene el reencuadre MAYORMENTE aplicado (por c-242) pero con residuales
concretos que esta devolucion exige cerrar como **condicion para fijar fecha de defensa**: el
tribunal fija fecha solo al recibir una version con R-01..R-07 aplicados **y el visto bueno
escrito del director**.

## What Changes

- **R-01 (escenario ficticio):** consolidar que la organizacion es un escenario de referencia
  ficticio construido por los autores; las cifras de la "semana laboral representativa" (42
  incidentes/dia, 2 min 45 s, 15 % de derivacion erronea, ~120 usuarios, cinco areas) pasan a
  ser **parametros del escenario**, no mediciones. Sweep de los residuales que aun los
  presentan como hecho (p. ej. "promedio de una semana completa de operacion",
  "mas de tres anos de antiguedad en la mesa de ayuda").
- **R-02 (composicion del corpus):** declarar la composicion de los 200 casos —cuantos son
  incidentes reales del entorno del grupo y cuantos reconstrucciones, quien las escribio, con
  que metodo y con o sin asistente de IA— y agregar a §4.8 la amenaza de que los autores
  escribieron parte de los casos, fijaron su sector y ajustaron el vocabulario de reglas sobre
  ese mismo corpus. Corregir la frase "corpus real pseudonimizado" (12-anexos.tex:235).
- **R-03 (flujo manual):** describir que se midio realmente en el flujo manual de la campana
  2026-10 (donde, sobre que textos, quienes A1/T1, que fechas); RETIRAR "sobre la operacion
  normal de la mesa" y el "periodo relevado del 16 de junio al 10 de septiembre"
  (04-marco-metodologico.tex:46); declararlo **medicion controlada / tarea de laboratorio** y
  leer los "61,6 s" como medicion de tarea controlada, no de operacion normal.
- **R-04 (volumen como supuesto):** presentar los 2.646 incidentes/trimestre como **supuesto
  del escenario** y el balance neto como ejercicio con volumenes supuestos (verificar las
  menciones desnudas de "2.646").
- **R-05 (Capitulo 7):** reescribir el capitulo 7 (tratamiento de datos) —RETIRAR base de
  empleador (art. 5 inc. 2 ap. d), responsable "designado por la organizacion", politica de
  privacidad "para los usuarios de la organizacion", notificacion a 120 empleados, carta de
  autorizacion—; explicar la base real de los incidentes reales del regimen (a); el acta de
  consentimiento debe llevar su fecha real de firma.
- **R-06 (limitaciones):** "una sola organizacion" / "el unico contexto en que se evaluo"
  pasan a "un corpus curado por los autores sobre un escenario de referencia".
- **R-07 (nota de versiones):** agregar al Anexo I.1 una nota: hasta la v1.6.0 el escenario se
  presento como organizacion real; desde la version siguiente se declara ficticio, con
  autorizacion del tribunal.
- **B-01 (nombres de sector):** unificar la cadena del sistema en monoespaciado y con tilde en
  prosa; residual concreto: `\sectorcad{si}` (monoespaciado, sin tilde) usado EN PROSA en
  01-introduccion.tex:48 y :72, debe ser `\sectorprosa{si}`.

**BREAKING (afirmaciones de procedencia):** el documento deja de afirmar como hecho la
organizacion real, las mediciones de su operacion, la base de empleador y la notificacion de
120 empleados, y declara el flujo manual como tarea controlada.

Fuera de alcance (el tribunal lo preserva explicitamente, "lo que no requiere cambios"):
arquitectura, codigo y latencias del flujo automatizado (los 118 tiempos de correo/formulario
coinciden con la base; la campana complementaria del 5/11 se conserva). No se reintroduce la
validacion fuera de muestra retirada. No se recompila, bump ni tag (c-239).

## Capabilities

### New Capabilities

- `tesis-reencuadre-cuarta-instancia`: aplicacion del reencuadre autorizado de cuarta
  instancia (R-01..R-07 + B-01) sobre la prosa de la tesis. Cubre: el escenario como parametro
  ficticio (R-01), la composicion declarada del corpus (R-02), el flujo manual como medicion
  controlada (R-03), el volumen como supuesto (R-04), la base legal real por regimen (R-05),
  la reformulacion de las limitaciones (R-06), la nota de versiones (R-07) y la unificacion de
  los nombres de sector (B-01).

### Modified Capabilities

Ninguna.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` | Modificado | R-01 (§1.1), B-01 (sector en prosa :48, :72) |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | R-01 (§4.2 "antiguedad"), R-03 (§4.2/§4.4 "operacion normal", "16 jun - 10 sep") |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | R-04 (2.646 como supuesto), R-06 (§9.3 "unico entorno") |
| `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` | Modificado | R-06 (§9.1 "unico contexto") |
| `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` | Modificado | R-05 (capitulo 7: base legal, responsable, politica, fecha del acta) |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado | R-02 ("corpus real pseudonimizado":235), R-07 (nota de versiones :233-238), B-01 |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada c-246 y tabla de compuertas (autores + director) |