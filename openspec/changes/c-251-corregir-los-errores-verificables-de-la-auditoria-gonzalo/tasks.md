# Tasks: Corregir los errores verificables de la auditoría Gonzalo (nivel 2)

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `A/` = `auditorias/`;
`C/` = `docs/Tesis/Correcciones/`. Líneas de `main` (versión de defensa `v1.6.5`, tag anotado); el
apply las re-verifica con `rg` antes de editar, porque las ediciones las desplazan. **Mapa
archivo→capítulo (obligatorio):** Ch4 = `04-marco-metodologico.tex`, Ch7 (legal) =
`11-aspectos-legales.tex`, Ch9 (Discusión) = `08-discusion.tex`, Anexo K = `12-anexos.tex`; el nombre
del `.tex` no es el número rendido. Equivalente de Strict TDD para prosa: cada tarea de edición corre
una verificación ANTES (muestra el defecto) y DESPUÉS (estado deseado), ambas registradas en la
sección c-251 de `C/dictamen-correcciones.md`.

**Gobernanza del change: ALTA en E1-E3, MEDIA en E4-E5.** Las tareas del capítulo legal
(`S/11-aspectos-legales.tex`) requieren aprobación explícita de autores+director ANTES de escribir.
Dos compuertas de autor bloquean tareas: **OQ-1** (fecha de notificación: ¿2026-09-30 o 2026-10-01?)
bloquea E2; **OQ-2** (redacción legal fiel de los arts. 2/28/11.3.e) bloquea E1. NO hay hechos
postergables: ambas se resuelven y registran antes del apply de su tarea.

Reglas duras: no editar `.tex` fuera de los pasajes listados; no editar `docs/seguridad/` ni
`auditorias/` (son evidencia); no cambiar ninguna cifra canónica (61,6 s, 17,76 s, 71,2 %, 56,6 s,
51,6 s, 68,6 %, 65,6 %, etc.); no commitear, taggear ni pushear; no compilar; español rioplatense
formal sin emojis; nunca nombres reales de sujetos (solo `A1`, `T1`, `E1`, `E2`, `O1`, `O2`).

## 1. Guardas y línea base

- [ ] 1.1 Leer `proposal.md`, `design.md` (D1-D6, OQ-1 y OQ-2), los dos deltas de `specs/` y `A/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md` (observación C-05). Verificación: `git rev-parse v1.6.5^{commit}` coincide con el commit de `main` y `git diff --stat v1.6.5 HEAD -- "docs/Tesis/v10 (IA)" docs/seguridad` vacío, o lista de desplazamientos registrada en la sección c-251.
- [ ] 1.2 Línea base de cifras y conteos. Verificación: `rg -n "61,6|17,76|71,2|56,6|51,6|68,6|65,6" S/` devuelve los valores vigentes y se registran; `rg -n "art.culo 28 dispone|v1.6.0 afirm|2026-09-30" S/11-aspectos-legales.tex` devuelve los tres defectos (E1/E2/E3) como fallas ANTES.
- [ ] 1.3 Red de seguridad: `python "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS y `openspec validate --all --strict` sin fallos. Si algo falla antes de editar, se reporta como falla preexistente y no se corrige aquí.

## 2. Compuertas de autor (OQ-1 y OQ-2)

- [ ] 2.1 Registrar OQ-1 en la tabla de decisiones de la sección c-251: la fecha de notificación correcta (¿2026-09-30 o 2026-10-01?), con fuente (acta firmada vs. registro del equipo) y responsable (autores+director). Verificación: la fila OQ-1 existe con fecha, decisión literal y responsable; ninguna ambigüedad entre dos fechas.
- [ ] 2.2 Registrar OQ-2 en la misma tabla: la redacción legal fiel de los arts. 2/28/11.3.e para la fundamentación de la licitud por disociación, decidida por autores+director. Verificación: la fila OQ-2 existe con el texto aprobado (o un puntero al párrafo aprobado) y responsable.
- [ ] 2.3 (Gobernanza) Mostrar el texto propuesto para E1, E2 y E3 a autores+director con el diff completo; recoger el OK escrito antes de escribir en `S/11-aspectos-legales.tex`. Verificación: el OK consta en la sección c-251; sin OK no se edita.

## 3. E1 - Paráfrasis fiel del art. 28 de la Ley 25.326 (ALTA)

- [ ] 3.1 `S/11-aspectos-legales.tex:12`: reemplazar "el artículo 28 dispone que los datos disociados no se consideran datos personales a los efectos de la ley; ambos artículos fundamentan aquí la licitud por disociación" por la lectura fiel aprobada en OQ-2 (art. 2 define disociación; art. 28 exime encuestas/estadística/investigación con datos no atribuibles y, en 28.2, manda disociar; art. 11.3.e cubre la cesión sin consentimiento cuando media disociación). Verificación ANTES: `rg -n "art.culo 28 dispone que los datos disociados no se consideran datos personales" S/11-aspectos-legales.tex` devuelve `:12`; DESPUÉS: 0 coincidencias de esa frase y el párrafo atribuye a cada artículo lo que dice.
- [ ] 3.2 Verificar la propagación en `:16`, `:18`, `:32`, `:36`, `:46`, `:54`: cada pasaje que funda la licitud por disociación lo hace sin repetir la paráfrasis inexacta. Verificación ANTES: `rg -n "disociac|sin datos personales|sin dato personal|no contiene dato personal" S/11-aspectos-legales.tex`; DESPUÉS: las líneas listadas fundan la licitud con lectura fiel, sin "disociado = no dato personal" como cita de un artículo.
- [ ] 3.3 Registrar la fila ANTES/DESPUES de E1 en la sección c-251 con el texto aprobado. Verificación: `rg -n "E1" C/dictamen-correcciones.md` muestra la fila con el diff.

## 4. E2 - Fecha de notificación unificada (ALTA)

- [ ] 4.1 `S/11-aspectos-legales.tex:32`: unificar la fecha "2026-09-30" a la decidida en OQ-1 (consistente con el acta `docs/seguridad/acta-consentimiento-t2.md`, cabecera y §4, y con la referencia de `A/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md` C-05). Verificación ANTES: `rg -n "2026-09-30" S/11-aspectos-legales.tex` devuelve `:32`; DESPUÉS: la única fecha coincide con la del acta y no queda "2026-09-30" en el capítulo.
- [ ] 4.2 Cruzar fecha con el acta: `rg -n "notificaci.n|2026-10-01" docs/seguridad/acta-consentimiento-t2.md` y leer §4. Verificación: la fecha del capítulo legal y la del acta coinciden; si OQ-1 eligió una fecha distinta del acta, la sección c-251 registra la razón (y el acta no se edita aquí).
- [ ] 4.3 Nota fuera de alcance (sin editar): registrar en la sección c-251 que el acta §1 conserva la frase stale "propio entorno operativo" (C-06), fuera del alcance de este change. Verificación: la nota existe en c-251 y `git status` confirma que `docs/seguridad/acta-consentimiento-t2.md` NO se modificó.

## 5. E3 - Retiro de la frase sobre v1.6.0 (ALTA)

- [ ] 5.1 `S/11-aspectos-legales.tex:32` (oración final): retirar "La versión v1.6.0 afirmó que no se había recabado el consentimiento de los titulares para la transferencia internacional; esa afirmación no se sostiene, porque el consentimiento verbal se prestó el 2026-10-02, aunque su constancia escrita es posterior." Verificación ANTES: `rg -n "La versi.n v1.6.0 afirm" S/11-aspectos-legales.tex` devuelve `:32`; DESPUÉS: 0 coincidencias de la oración.
- [ ] 5.2 Conservar la cronología del consentimiento verbal: verificar que `rg -n "2026-10-02" S/11-aspectos-legales.tex` sigue devolviendo los pasajes que describen el consentimiento verbal, solo que sin la oposición a la v1.6.0. Verificación: la fecha 2026-10-02 permanece; solo se retiró la oración de la v1.6.0.

## 6. E4 - Dirección de la asimetría de alcance (MEDIA)

- [ ] 6.1 `S/08-discusion.tex:22`: separar "instrumento" de "alcance" en la primera explicación rival y corregir la dirección del alcance. Reemplazar el párrafo "la asimetría del instrumento y del alcance ... Eso favorece al segundo" por una redacción que distinga: el INSTRUMENTO (cronómetro humano en vivo) infla el manual y favorece al automatizado; el ALCANCE (manual = clasificación pura, alcance estrecho sub-contado; automatizado = extremo a extremo, alcance amplio) es conservador y SUB-ESTIMA la ventaja del automatizado (reducción reportada como cota inferior). Verificación ANTES: `rg -n "asimetr.a del instrumento y del alcance|favorece al segundo" S/08-discusion.tex` devuelve `:22`; DESPUÉS: instrumento y alcance están separados y la dirección del alcance es "cota inferior".
- [ ] 6.2 Coherencia con la octava amenaza: verificar que `rg -n "direcci.n y la magnitud.*alcance|direcci.n y la magnitud de esa diferencia de alcance" S/04-marco-metodologico.tex` apunta a `:131` y que la redacción de 6.1 remite a esa amenaza sin cuantificar la magnitud (mantiene "no se estimaron"). Verificación: la magnitud queda "no estimada"; no se introduce un número nuevo.

## 7. E5 - Re-etiquetado de -10 s en el Anexo K (MEDIA)

- [ ] 7.1 `S/12-anexos.tex:354`: re-etiquetar los descuentos. El `-5 s` pasa a "cota de redondeo" (redondeo hacia arriba a múltiplos de 5 s; inflación máxima por caso < 5 s); el `-10 s` pasa de "redondeo" a "escenario solicitado por el tribunal cuando la descripción aún incluía la carga ~10 s (retirada por C-02)". Los valores 56,6 s / 51,6 s y 68,6 % / 65,6 % quedan sin cambio. Verificación ANTES: `rg -n "redondeo|descuenta 5~s y 10~s" S/12-anexos.tex` devuelve `:354`; DESPUÉS: el -10 s ya no se justifica por redondeo y los valores son idénticos.
- [ ] 7.2 `S/04-marco-metodologico.tex:16`: re-etiquetar "resolución efectiva del instrumento que vincula los descuentos de 5 s y 10 s del análisis de sensibilidad con el procedimiento" para no atribuir el -10 s al redondeo. Verificación ANTES: `rg -n "descuentos de 5~s y 10~s|resoluci.n efectiva del instrumento" S/04-marco-metodologico.tex` devuelve `:16`; DESPUÉS: el -5 s vincula con el redondeo y el -10 s con el escenario C-02.
- [ ] 7.3 `S/08-discusion.tex:22/24`: ajustar la mención "mantiene la reducción por encima del 65 % aun descontando 10 s por caso" para que el -10 s no se presente como redondeo (es el escenario adverso del tribunal). Verificación: el -10 s queda como escenario adverso pedido por el tribunal, no como redondeo; la cifra 65,6 % no cambia.
- [ ] 7.4 Conservar el rótulo "mínimo del estimando primario" de la tabla de robustez (`12-anexos.tex:370`) y los valores. Verificación: `rg -n "m.nimo del estimando primario|65,6" S/12-anexos.tex` sigue devolviendo el rótulo y el valor, sin cambio.

## 8. Cierre y verificación

- [ ] 8.1 Verificación global ANTES/DESPUES: `rg -n "art.culo 28 dispone|v1.6.0 afirm|2026-09-30" S/11-aspectos-legales.tex` = 0 coincidencias; `rg -n "favorece al segundo" S/08-discusion.tex` = 0; `rg -n "65,6|65,6~\\\\%|51,6" S/12-anexos.tex` conserva los valores; `git diff --stat -- "docs/Tesis/v10 (IA)/paper/sections" docs/seguridad` muestra SOLO los pasajes previstos (sin tocar `docs/seguridad/`).
- [ ] 8.2 `python "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS y `openspec validate --all --strict` sin fallos. Verificación: ambos en verde tras las ediciones.
- [ ] 8.3 Completar la sección c-251 de `C/dictamen-correcciones.md`: tabla de decisiones OQ-1/OQ-2, filas ANTES/DESPUES por corrección (E1-E5) y la nota de la frase stale del acta. Verificación: `rg -n "OQ-1|OQ-2|E1|E2|E3|E4|E5" C/dictamen-correcciones.md` muestra todas las entradas con gobernanza cumplida y ningún elemento "EN CURSO".
