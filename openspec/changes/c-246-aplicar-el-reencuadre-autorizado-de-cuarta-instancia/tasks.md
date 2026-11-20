# Tasks: Aplicar el reencuadre autorizado de cuarta instancia

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` =
`docs/Tesis/Correcciones/`. Equivalente de Strict TDD para prosa: cada tarea de edicion tiene
una verificacion que se corre ANTES (linea base; debe mostrar la afirmacion incorrecta) y
DESPUES (estado deseado), y ambas salidas se reportan en `C/dictamen-correcciones.md` (seccion
`c-246`). Reglas: no commitear ni pushear sin pedido; no cambiar cifras, citas ni conclusiones
sin ratificacion de autores; espanol sin emojis; solo alias (`E1`, `E2`, `O1`, `O2`, `A1`,
`T1`), nunca nombres reales ni la correspondencia alias-identidad; no tocar `App/`, `n8n/` ni
`evaluation/`. Planning only: este change NO escribe `.tex` en su fase de propose; las tareas
de edicion se ejecutan en apply, DESPUES del visto bueno del director (gate duro del tribunal).

## 1. Guardas y lectura

- [x] 1.1 Leer `proposal.md`, `design.md` (D1-D6 + OQ-01 a OQ-03), el delta
  `specs/tesis-reencuadre-cuarta-instancia/spec.md`, la devolucion de cuarta instancia
  (`auditorias/Devolución de cuarta instancia...pdf` o `/tmp/opencode/cuarta_instancia.md`) y
  el estado actual de los `.tex`. Verificacion (linea base): `rg -n` sobre los residuales de
  R-01..R-07 y B-01 muestra las afirmaciones a corregir.
- [x] 1.2 Confirmar el estado de c-242 (precedente de reencuadre). Verificacion:
  `openspec list --json` muestra c-242 `in-progress` y NO archivado; confirmar que su delta
  (ADDED "Encuadre honesto...") no esta en `openspec/specs/tesis-document/spec.md`. Si c-242
  ya fue archivado, releer su delta desde main y ajustar las remisiones.

## 2. Compuertas de autores (OQ) y visto bueno del director (gate duro)

- [x] 2.1 **[COMPUERTA OQ-01 (R-02 composicion)]** Presentar a los autores la solicitud del
  desglose exacto del corpus de 200 casos: cuantos incidentes reales del entorno del grupo
  (regimen (a)) y cuantos reconstrucciones (regimen (b)); quien escribio las reconstrucciones;
  con que metodo; con o sin asistente de IA. Registrar su respuesta literal, con fecha y
  responsable, en la tabla de compuertas de c-246 en `C/dictamen-correcciones.md`. Verificacion:
  la fila existe; sin respuesta, la tarea 4.2 queda bloqueada; el agente NO inventa proporciones.
- [x] 2.2 **[COMPUERTA OQ-02 (R-05 redaccion y fecha)]** Ratificar la redaccion exacta de la
  base de licitud del regimen (a) en §7.2/§7.5 (consentimiento informado del grupo, art. 5 inc.
  1, reconciliando la caracterizacion del tribunal de "incidentes reales de terceros") y la
  **fecha real de firma del acta de consentimiento** (verificar si la actual "2026-10-02" en
  `11-aspectos-legales.tex` es la fecha real). Verificacion: la redaccion (o su referencia) y
  la fecha figuran en la tabla; sin respuesta, las tareas 5.x quedan bloqueadas.
- [x] 2.3 **[COMPUERTA OQ-03 (R-03 laboratorio)]** Confirmar que el flujo manual de la campana
  2026-10 se declara como medicion controlada / tarea de laboratorio, junto con la descripcion
  factual de donde, sobre que textos, quienes (A1/T1) y en que fechas. Verificacion: la
  confirmacion figura en la tabla; estructurara las tareas 3.2.
- [x] 2.4 **[COMPUERTA DIRECTOR (gate duro)]** Registrar el visto bueno escrito del director
  (condicion del tribunal para fijar fecha de defensa). Verificacion: la firma/visto bueno con
  fecha figuran en la tabla; sin el, NO se escribe prosa (todas las tareas del grupo 3 al 6
  quedan bloqueadas).

## 3. tesis-document — R-01, R-03, R-04 (escenario, flujo manual, volumen)

- [x] 3.1 `S/01-introduccion.tex` §1.1: presentar las cifras de la semana representativa (42
  incidentes/dia, 2 min 45 s, 15 %, ~120 usuarios, cinco areas) como parametros del escenario,
  retirar "obtenida del promedio de una semana completa de operacion" (linea 18). Verificacion
  (ANTES): §1.1 deriva 2 min 45 s de una semana de operacion; (DESPUES): `rg -n "semana completa
  de operacion" "S/01-introduccion.tex"` no devuelve la afirmacion como fuente real.
- [x] 3.2 `S/04-marco-metodologico.tex` §4.2/§4.4: declarar el flujo manual como medicion
  controlada / tarea de laboratorio; retirar "sobre la operacion normal de la mesa" y el
  "periodo relevado del 16 de junio al 10 de septiembre de 2026" (linea 46); describir donde,
  sobre que textos, quienes y en que fechas (segun OQ-03); conservar `42 x 63 ~ 2.646` como
  supuesto. Verificacion (ANTES): linea 46 afirma operacion normal y periodo relevado; (DESPUES):
  `rg -n "operacion normal de la mesa|16 de junio al 10 de septiembre" "S/04-marco-metodologico.tex"`
  no devuelve esas frases como hecho; los 61,6 s se leen como tarea controlada.
- [x] 3.3 `S/04-marco-metodologico.tex` (linea 64): retirar "con mas de tres anos de antiguedad
  en la mesa de ayuda" al describir los operadores. Verificacion (ANTES): linea 64 apela a una
  antiguedad en mesa real; (DESPUES): `rg -n "antiguedad en la mesa de ayuda" "S/04-marco-metodologico.tex"`
  no devuelve la afirmacion.
- [x] 3.4 Sweep de "la organizacion" como hecho en `S/*.tex` (p. ej. `01-introduccion.tex:64`).
  Verificacion (ANTES): `rg -n "otorga a la organizacion control pleno|la organizacion como entidad real"`
  revisado; (DESPUES): las menciones residuales presentan el escenario de referencia o el rol
  generico futuro del adoptante, no una organizacion real.
- [x] 3.5 `S/08-discusion.tex` y `S/12-anexos.tex`: rotular las menciones de "2.646" como
  supuesto del escenario (R-04), sin cambiar el valor numerico. Verificacion (ANTES): `rg -n
  "2\.646|2.646" "S/08-discusion.tex" "S/12-anexos.tex"` muestra menciones sin rotular;
  (DESPUES): cada ocurrencia queda como supuesto del escenario (proyeccion 42 x 63).

## 4. tesis-document — R-02 (composicion del corpus) y R-07 (nota de versiones)

- [x] 4.1 `S/12-anexos.tex` (linea 235): corregir la frase "corpus real pseudonimizado" para no
  afirmar que el corpus completo es real; distinguir el regimen (a) (real pseudonimizado) del
  regimen (b) (reconstruccion). Verificacion (ANTES): linea 235 dice "corpus real
  pseudonimizado"; (DESPUES): `rg -n "corpus real pseudonimizado" "S/12-anexos.tex"` no devuelve
  la frase como descripcion del corpus completo.
- [x] 4.2 `S/04-marco-metodologico.tex` §4.4 y `S/12-anexos.tex` Anexo I.1: declarar la
  composicion del corpus (cuantos reales vs reconstrucciones, autor, metodo, asistente) segun
  OQ-01. Verificacion (ANTES): no existe desglose numerico respaldado; (DESPUES): el desglose
  coincide con la respuesta consignada de los autores; no se inventa ninguna proporcion.
- [x] 4.3 `S/04-marco-metodologico.tex` §4.8: agregar la amenaza de que los autores escribieron
  parte de los casos, fijaron su sector y ajustaron el vocabulario de reglas sobre el mismo
  corpus. Verificacion (ANTES): §4.8 no la enumera; (DESPUES): `rg -n "autores.*escribieron|fijaron.*sector|ajustaron.*vocabulario" "S/04-marco-metodologico.tex"`
  muestra la amenaza declarada y el cardinal de amenazas de §4.8 sigue coherente.
- [x] 4.4 `S/12-anexos.tex` `subsec:nota-versiones` (lineas 233-238): agregar la nota de que
  hasta la v1.6.0 el escenario se presento como organizacion real y desde la version siguiente
  se declara ficticio, con autorizacion del tribunal. Verificacion (ANTES): la nota no existe;
  (DESPUES): `rg -n "ficticio|organizacion real" "S/12-anexos.tex"` muestra la nota siguiendo el
  patron del corpus sintetico de julio y la validacion retirada.

## 5. tesis-document — R-05 (capitulo 7) y R-06 (limitaciones)

- [x] 5.1 `S/11-aspectos-legales.tex` §7.2 (`subsec:principios-datos`) y §7.5
  (`subsec:consentimiento-derechos`): retirar la base de empleador (art. 5 inc. 2 ap. d) como
  base del estudio y explicar la base real del regimen (a) (consentimiento del grupo, art. 5
  inc. 1) segun OQ-02. Verificacion (ANTES): §7.2 funda en la base de empleador; (DESPUES):
  `rg -n "empleadora|inciso~?2, apartado~?d" "S/11-aspectos-legales.tex"` no la presenta como
  base vigente del estudio.
- [x] 5.2 `S/11-aspectos-legales.tex` §7.5 (linea 38): retirar "politica de privacidad... para
  los usuarios de la organizacion", el "responsable de proteccion de datos designado por la
  organizacion", la notificacion a 120 empleados y la carta de autorizacion. Verificacion
  (ANTES): linea 38 las afirma; (DESPUES): `rg -n "usuarios de la organizacion|designado por la
  organizacion|120 empleados|carta de autorizaci" "S/11-aspectos-legales.tex"` no las presenta
  como hechos del estudio.
- [x] 5.3 `S/11-aspectos-legales.tex` (transferencia, cerca de la linea 30): consignar la fecha
  REAL de firma del acta de consentimiento segun OQ-02. Verificacion (ANTES): figura una fecha
  que puede no ser la real ("2026-10-02"); (DESPUES): la fecha consignada coincide con la
  respuesta de los autores; no se inventa.
- [x] 5.4 `S/09-conclusiones.tex` (linea 49) y `S/08-discusion.tex` (linea 50): reformular "una
  sola organizacion" / "el unico contexto en que se evaluo" / "un unico entorno operativo" como
  "un corpus curado por los autores sobre un escenario de referencia". Verificacion (ANTES):
  lineas 49 y 50 presentan el unico contexto/entorno; (DESPUES): `rg -n "unico contexto en que
  se evaluo|unico entorno operativo|una sola organizacion" "S/09-conclusiones.tex"
  "S/08-discusion.tex"` ya no devuelve la formulacion de organizacion real unica.

## 6. tesis-document — B-01 (nombres de sector)

- [x] 6.1 `S/01-introduccion.tex` lineas 48 y 72: cambiar `\sectorcad{si}` (monoespaciado, sin
  tilde) por `\sectorprosa{si}` en prosa. Verificacion (ANTES): `rg -n "\\sectorcad\{si\}"
  "S/01-introduccion.tex"` muestra las lineas 48 y 72; (DESPUES): esas menciones usan
  `\sectorprosa{si}`; las cinco cadenas canonicas del sistema no cambian de valor ni de tilde.

## 7. Verificacion de coherencia

- [x] 7.1 Coherencia §7.2 <-> §7.5: la base del regimen (a) y el tratamiento del regimen (b)
  son los mismos en ambas subsecciones. Verificacion: comparar `rg -n "inciso|regimen" "S/11-aspectos-legales.tex"`
  en `subsec:principios-datos` y `subsec:consentimiento-derechos`; coinciden.
- [x] 7.2 Sin residual de la devolucion. Verificacion: `rg -ni "organizacion real|carta de
  autorizaci|120 empleados|operacion normal de la mesa|16 de junio al 10 de septiembre|una sola
  organizacion|corpus real pseudonimizado"` "S/" no devuelve afirmaciones como hechos.
- [x] 7.3 Sin `\sectorcad` en prosa. Verificacion: `rg -n "\\sectorcad\{si\}" "S/01-introduccion.tex"`
  no devuelve menciones en prosa.
- [x] 7.4 Cifras canonicas intactas. Verificacion: `rg -n "61,6 s|17,76 s|W = 363|73,5"` "S/"
  y `git diff` limitado a re-rotulado; ningun valor canonico del sistema ni de la campana cambia.
- [ ] 7.5 Compilacion de verificacion: copiar `docs/Tesis/v10 (IA)` a un directorio temporal y compilar alli (`latexmk main.tex`). Verificacion: 0 errores fatales, 0 referencias/citas indefinidas, 0 etiquetas duplicadas. No versionar el PDF. [DEFERIDA: regla no-build; no se compila]
  compilar alli (`latexmk main.tex`). Verificacion: 0 errores fatales, 0 referencias/citas
  indefinidas, 0 etiquetas duplicadas. No versionar el PDF.

## 8. Registro y cierre

- [x] 8.1 `C/dictamen-correcciones.md`: agregar la entrada de c-246 con la tabla de compuertas
  (OQ-01 a OQ-03 y visto bueno del director: respuesta, fecha, responsable), las salidas
  ANTES/DESPUES de las verificaciones y la nota de dependencia con c-242. Verificacion: la
  seccion `c-246` existe y contiene cada bloque; las entradas previas quedan intactas.
- [x] 8.2 `openspec validate c-246-aplicar-el-reencuadre-autorizado-de-cuarta-instancia --strict`.
  Verificacion: pasa.
- [x] 8.3 `openspec validate --all --strict`. Verificacion: pasa.
- [x] 8.4 Confirmar que NO se edito ningun archivo fuera de `docs/Tesis/`, `C/` y
  `openspec/changes/c-246-...`. Verificacion: `git status` no muestra cambios en `App/`,
  `n8n/` ni `evaluation/`. El change es de prosa unicamente.