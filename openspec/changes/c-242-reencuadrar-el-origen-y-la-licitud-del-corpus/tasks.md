# Tasks: Reencuadrar el origen y la licitud del corpus

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`D/` = `docs/seguridad/`. Equivalente de Strict TDD para prosa: cada tarea de edicion tiene una
verificacion que se corre ANTES (linea base; debe mostrar la afirmacion incorrecta) y DESPUES
(estado deseado), y ambas salidas se reportan en `C/dictamen-correcciones.md` (seccion `c-242`).
Reglas: no commitear ni pushear sin pedido; no cambiar cifras, citas ni conclusiones sin
ratificacion de autores; espanol sin emojis; solo alias (`E1`, `E2`, `O1`, `O2`, `A1`, `T1`),
nunca nombres reales ni la correspondencia alias-identidad; no tocar `App/`, `n8n/` ni
`evaluation/`. Orden duro: aplicar DESPUES de c-238 (legibilidad) sobre los mismos archivos.

## 1. Guardas y lectura

- [ ] 1.1 Leer `proposal.md`, `design.md` (D1-D6 + OQ-01 a OQ-05), los deltas
  `specs/tesis-document/spec.md` y `specs/security-governance-docs/spec.md`, y el estado actual
  de los `.tex`. Verificacion (linea base): `rg -n "organizaci.n mediana|120 usuarios|cartade autorizaci|empleadora|una sola organizaci" "S/"` muestra las afirmaciones a corregir.
- [ ] 1.2 Confirmar que c-238 esta aplicado sobre `S/01-introduccion.tex` y `S/11-aspectos-legales.tex`.
  Verificacion: `git log`/`git diff` o `rg -n` muestran sus efectos; si no, detener y reportar.
- [ ] 1.3 Confirmar que c-240 esta archivado (sus requisitos estan en `openspec/specs/tesis-document/spec.md`).
  Verificacion: `rg -n "Parrafo de licitud y alcance en §7.5|§1.8 veraz|Retiro decidido" openspec/specs/tesis-document/spec.md` devuelve los tres.

## 2. Compuertas de autores y director (OQ-01 a OQ-05)

- [ ] 2.1 **[COMPUERTA OQ-01]** Presentar a los autores y al director el reencuadre del origen
  (NO hay organizacion real; el corpus es mezcla de los regimenes (a) y (b)) y registrar su
  ratificacion literal, con fecha y responsable, en la tabla de compuertas de c-242 en
  `C/dictamen-correcciones.md`. Verificacion: la fila existe; sin respuesta, las tareas del
  grupo 3 y 4 quedan bloqueadas.
- [ ] 2.2 **[COMPUERTA OQ-02]** Ratificar la base de licitud por regimen (regimen (a):
  consentimiento informado del grupo, art. 5 inc. 1, + pseudonimizacion; regimen (b): sin datos
  personales, sin base) y la redaccion final de §7.2 y §7.5 declarando AMBOS regimenes.
  Verificacion: la base y la redaccion (o su referencia) figuran en la tabla; sin respuesta, la
  tarea 4.2 y 4.3 quedan bloqueadas.
- [ ] 2.3 **[COMPUERTA OQ-03]** Decidir como tratar la transferencia del art. 12 efectivamente
  realizada durante el estudio sin instrumento suscrito. Verificacion: la decision figura en la
  tabla; condiciona la tarea 4.4.
- [ ] 2.4 **[COMPUERTA OQ-04]** Fijar la descripcion de la validez externa / el escenario
  representativo en §1.8, §8.2 y §9.1. Verificacion: la descripcion ratificada figura en la
  tabla; condiciona las tareas 3.3 y 3.5.
- [ ] 2.5 **[COMPUERTA OQ-05]** Decidir que hacer con la proyeccion "42 incidentes diarios /
  universo 2.646" y con los "120 usuarios". Verificacion: la decision figura en la tabla;
  condiciona las tareas 3.1 y 3.2.
- [ ] 2.6 **[COMPUERTA DIRECTOR]** Registrar el visto bueno del director (el change altera lo
  que la tesis afirma sobre la procedencia de sus datos). Verificacion: la firma/visto bueno
  con fecha figuran en la tabla; sin el, no se escribe prosa.

## 3. tesis-document — Reencuadre del origen (§1.1, §1.2, §1.8, §4.1, §8.2, §9.1)

- [ ] 3.1 `S/01-introduccion.tex` §1.1: presentar el escenario como referencia narrativa y el
  corpus como mezcla de los regimenes (a) y (b); no afirmar organizacion real ni notificacion
  de 120 empleados. Verificacion (ANTES): §1.1 afirma una organizacion real; (DESPUES):
  `rg -n "organizacion mediana|120 usuarios" "S/01-introduccion.tex"` ya no la presenta como
  real; aplicar la decision de OQ-05 sobre las cifras.
- [ ] 3.2 `S/01-introduccion.tex` §1.2: aplicar la misma denominacion y tratamiento del
  escenario que en §1.8 (consistencia). Verificacion: comparar §1.2 y §1.8 con `rg -n`;
  coinciden y ninguno presenta el escenario como organizacion real.
- [ ] 3.3 `S/01-introduccion.tex` §1.8: retirar/reescribir la frase del corpus para que la
  validacion se presente dentro de la muestra sobre un unico entorno (escenario narrativo),
  sin organizacion real ni segunda organizacion; conservar la limitacion geografica.
  Verificacion (ANTES): §1.8 afirma "una unica organizacion... ~120 usuarios"; (DESPUES):
  `rg -n "una unica organizacion|segunda organizacion" "S/01-introduccion.tex"` no devuelve la
  afirmacion de organizacion real.
- [ ] 3.4 `S/04-marco-metodologico.tex` §4.1: la poblacion se declara como los incidentes del
  entorno operativo del propio equipo (escenario de referencia), no de "la organizacion
  analizada". Verificacion (ANTES): §4.1 dice "mesa de ayuda de la organizacion analizada";
  (DESPUES): `rg -n "organizacion analizada" "S/04-marco-metodologico.tex"` no devuelve la
  afirmacion de organizacion real. No cambiar el universo 2.646 sin OQ-05.
- [ ] 3.5 `S/08-discusion.tex` §8.2 y `S/09-conclusiones.tex` §9.1: reencuadrar la validez
  externa sobre un unico entorno operativo (escenario narrativo), sin afirmar organizacion
  real. Verificacion (ANTES): ambos dicen "una sola organizacion... Mendoza"; (DESPUES):
  `rg -n "una sola organizacion" "S/08-discusion.tex" "S/09-conclusiones.tex"` no devuelve la
  afirmacion de organizacion real; ningun valor canonico cambia.

## 4. tesis-document — Licitud (§7.2, §7.5) y transferencia (§7.3)

- [ ] 4.1 `S/11-aspectos-legales.tex` §7.2 (`subsec:principios-datos`): retirar la base de
  empleador ("la organizacion es la empleadora...") y declarar la base por regimen conforme a
  OQ-02; no reintroducir una relacion de empleo. Verificacion (ANTES): §7.2 funda la licitud
  en art. 5 inc. 2 ap. d) con "la organizacion es la empleadora"; (DESPUES):
  `rg -n "empleadora|inciso~?2, apartado~?d" "S/11-aspectos-legales.tex"` ya no la presenta
  como base vigente del estudio.
- [ ] 4.2 `S/11-aspectos-legales.tex` §7.5 (`subsec:consentimiento-derechos`): retirar la
  notificacion de "los 120 empleados" y "la carta de autorizacion emitida por la organizacion
  adoptante" (la afirmacion mas expuesta). Verificacion (ANTES): §7.5 las afirma; (DESPUES):
  `rg -n "120 empleados|carta de autorizaci" "S/11-aspectos-legales.tex"` no devuelve esas
  afirmaciones como hechos.
- [ ] 4.3 `S/11-aspectos-legales.tex` §7.5: reescribir la oracion de licitud de los datos
  conservados para declarar la base por regimen (regimen (a): consentimiento del grupo, art. 5
  inc. 1, + pseudonimizacion; regimen (b): sin base), sin colapsarlas y sin base de empleador,
  consistente con §7.2 (segun OQ-02). Verificacion (ANTES): colapsa ambas en "articulo~5...
  con el consentimiento informado"; (DESPUES): declara la base por regimen y no reproduce la
  base de empleador.
- [ ] 4.4 `S/11-aspectos-legales.tex` §7.3 (`subsec:transferencia-internacional`): encuadrar la
  transferencia del art. 12 realizada durante el estudio sin instrumento suscrito (segun
  OQ-03); no declarar el instrumento como suscrito. Verificacion (ANTES/DESPUES): `git diff`
  limitado a las oraciones afectadas; no se altera ninguna otra frase factual ni cifra.
- [ ] 4.5 Mantener sin cambio el resto de §7.2, §7.3 y §7.5 (retiro del corpus, ausencia de
  datos de terceros, remisiones). Verificacion: `git diff` limitado a las oraciones de origen y
  licitud; no se altera ninguna otra frase factual ni cifra.

## 5. security-governance-docs — Reconciliacion de la base por regimen

- [ ] 5.1 `D/registro-actividades-tratamiento.md` (ROPA) y `D/registro-requisitos-legales.md`:
  declarar que el corpus de investigacion (T2) es mezcla de los regimenes (a) y (b), con su base
  de licitud por regimen (consentimiento del grupo, art. 5 inc. 1, para el (a); sin base para
  el (b)); retirar cualquier base de empleador para el corpus. Verificacion (ANTES): T2 solo
  declara "pseudonimizacion" como salvaguarda; (DESPUES): ambas tablas (§5) declaran la base por
  regimen.
- [ ] 5.2 `D/acta-consentimiento-t1.md` y `D/clasificacion-etiquetado-informacion.md`:
  reconciliar la base de licitud por regimen y el caracter de reconstruccion (regimen (b)) del
  corpus; mantener el lenguaje de alineacion y sin PII real. Verificacion:
  `rg -n "regimen \(a\)|regimen \(b\)|consentimiento informado" "D/"` muestra la reconciliacion;
  los documentos no afirman certificacion.
- [ ] 5.3 Confirmar que el adoptante sigue presentado como "rol funcional generico futuro" en
  `D/` y que ningun documento afirma una organizacion real adoptante. Verificacion:
  `rg -ni "organizacion adoptante" "D/"` revisado; ningun pasaje presenta una organizacion real.

## 6. Verificacion de coherencia

- [ ] 6.1 Coherencia §7.2 <-> §7.5: la base del regimen (a) y el tratamiento del regimen (b)
  son los mismos en ambas subsecciones. Verificacion: comparar `rg -n "inciso|regimen" "S/11-aspectos-legales.tex"`
  en `subsec:principios-datos` y `subsec:consentimiento-derechos`; coinciden.
- [ ] 6.2 Sin afirmacion residual de organizacion real. Verificacion:
  `rg -ni "organizacion real|organizacion adoptante real|carta de autorizaci|120 empleados"
  "S/" "D/"` no devuelve afirmaciones como hechos.
- [ ] 6.3 Sin base de empleador como base del estudio. Verificacion:
  `rg -n "empleadora|relacion contractual, cientifica o profesional|inciso~?2, apartado~?d"
  "S/11-aspectos-legales.tex"` no la presenta como base vigente del trabajo.
- [ ] 6.4 Sin reintroduccion de la validacion retirada. Verificacion:
  `rg -ni "fuera de muestra|corpus independiente" "S/01-introduccion.tex"` no la reintroduce
  como evidencia vigente.
- [ ] 6.5 Compilacion de verificacion: copiar `docs/Tesis/v10 (IA)` a un directorio temporal y
  compilar alli (`latexmk main.tex`). Verificacion: 0 errores fatales, 0 referencias/citas
  indefinidas, 0 etiquetas duplicadas. No versionar el PDF ni regenerar `compilacion.md`.

## 7. Registro y cierre

- [ ] 7.1 `C/dictamen-correcciones.md`: agregar la entrada de c-242 con la tabla de compuertas
  (OQ-01 a OQ-05 y visto bueno del director: respuesta, fecha, responsable), las salidas
  ANTES/DESPUES de las verificaciones y la nota de que c-242 supersede a c-241. Verificacion:
  la seccion `c-242` existe y contiene cada bloque; las entradas previas quedan intactas.
- [ ] 7.2 `openspec validate c-242-reencuadrar-el-origen-y-la-licitud-del-corpus --strict`.
  Verificacion: pasa.
- [ ] 7.3 `openspec validate --all --strict`. Verificacion: pasa.
- [ ] 7.4 Confirmar que NO se edito ningun archivo fuera de `docs/Tesis/`, `docs/seguridad/`,
  `C/` y `openspec/changes/c-242-...`. Verificacion: `git status` no muestra cambios en
  `App/`, `n8n/` ni `evaluation/`.
