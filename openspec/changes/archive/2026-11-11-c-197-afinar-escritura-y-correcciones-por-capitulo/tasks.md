# Tasks: Afinar la escritura y las correcciones por capitulo de la tesis (N-02 y concision)

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`.
"N-07" y "N-12" remiten a la devolucion de segunda instancia del 11-11-2026; "D1"-"D6" al
`design.md`. Cada parrafo de los `.tex` es una sola linea fisica; las lineas son orientativas y el
apply localiza por texto (`rg -n`). Reglas para todos los grupos: no commitear ni pushear sin pedido;
no inventar datos; no cambiar cifras canonicas ni contenido sustantivo; no tocar `4.5`, `4.8` ni
`9.1` por N-06 (recitacion de llamadas, verificada como correcta); no reintroducir los residuos que
`c-196` retiro; espanol neutro, sin emojis, sin atribucion de IA. Cada tarea de escritura tiene una
verificacion (grep o medicion) que se corre ANTES (linea base) y DESPUES (resultado), y se reportan
ambas salidas. Equivalente de Strict TDD para prosa: la verificacion describe el estado deseado y
falla antes de la edicion.

## 1. Grupo 0 — Linea base y guardarrailes

- [x] 1.1 Registrar la regla de conteo de D1 en un script de solo lectura (`C/sent_c197.py` o equivalente): oraciones por signo de cierre, excluyendo comandos LaTeX, matematicas, pies de tabla, listados y comentarios; y conteo de "de modo que". Verificacion: el script imprime por archivo el total de oraciones, las de mas de 40 y las de mas de 60 palabras, y el conteo de "de modo que".
- [x] 1.2 Medir la linea base con la regla de 1.1 sobre `S/0*.tex` a `S/12-*.tex` y consignarla (comando y salida) en `C/dictamen-correcciones.md`, seccion `c-197`. Verificacion: el registro cita el comando y la salida; los valores del brief (~24 de mas de 60, ~8,8 % de mas de 40, ~29 "de modo que") se confirman o se corrigen con la medicion.
- [x] 1.3 Congelar la foto de cifras canonicas: `rg -n "73,5|0,6508|0,5207|71,2|W = 363|0,9639|2\.646|32,2|17,76|61,6|0,5569" S/` y guardar la salida como referencia. Verificacion: la salida queda registrada para cotejar, al cierre, que ninguna cifra cambio.
- [x] 1.4 Confirmar la dependencia de orden de archivo de D2: `c-196` primero, `c-197` despues. Verificacion: `openspec list --json` muestra `c-196` y el registro de `c-197` (proposal/design) declara la dependencia; no se archiva nada en este grupo.

## 2. Grupo A — Fila N-02 en el Anexo I (`S/12-anexos.tex`)

- [x] 2.1 Insertar la tabla de revisiones de D3 al inicio de `sec:anexo-trazabilidad`, despues de la subseccion "Revisiones que originaron las correcciones" (lineas ~239-241) y antes de `tab:anexo-trazabilidad`; etiqueta `tab:trazabilidad-revisiones`, `\footnotesize`, columnas `>{\raggedright\arraybackslash}p{...}`. Verificacion: `rg -c "tab:trazabilidad-revisiones" S/12-anexos.tex` >= 1 y la tabla aparece antes de `tab:anexo-trazabilidad` en el orden del archivo.
- [x] 2.2 Cargar la **primera fila** con la auditoria integral del tribunal del 4 de agosto de 2026, con los datos que la prosa ya declara (105 hallazgos, 28 criticos, `3,9/10`; archivo `auditorias/Auditoria_Tesis_Gomez_Bustos_Sevilla_040802026.pdf`). No inventar cifras ni fechas. Verificacion: la primera fila de `tab:trazabilidad-revisiones` contiene "4 de agosto", "105", "28" y "3,9".
- [x] 2.3 Agregar las filas siguientes que distinguen la serie de autoevaluaciones internas con modelo de lenguaje y la devolucion del 11 de noviembre de 2026 (D3), con datos ya declarados en la prosa. Verificacion: la tabla tiene al menos tres filas (auditoria, autoevaluaciones, devolucion) y cada una cita su origen en el repositorio.
- [x] 2.4 Ajustar la prosa de la subseccion para que remita a la fila (evitar duplicar toda la narrativa). Verificacion: `rg -c "tab:trazabilidad-revisiones" S/12-anexos.tex` >= 2 (la etiqueta de la tabla y al menos una remision) y la prosa conserva la distincion de los tres tipos de revision.
- [ ] 2.5 Verificacion del grupo: `rg -n "4 de agosto" S/12-anexos.tex` >= 1; compilar y confirmar 0 `Overfull \hbox` originados en la tabla nueva. Reportar salidas antes/despues. La busqueda `rg` devuelve 2 coincidencias (lineas 239 y 255); la compilacion se difiere por indicacion del usuario.

## 3. Grupo B1 — Afinado de capitulos 1 a 4

- [x] 3.1 Capitulo 1 (`S/01-introduccion.tex`) guiado por el Motivo principal de la seccion 6: partir las oraciones de mas de 60 palabras y acotar las de mas de 40; reemplazar "de modo que" por punto o "por lo tanto" segun el sentido. Verificacion: la medicion con la regla de 1.1, restringida a `S/01-introduccion.tex`, baja en mas de 60 y en mas de 40 respecto de la linea base; ninguna oracion nueva supera 60 palabras.
- [x] 3.2 Capitulos 2 y 3 (`S/02-marco-teorico.tex`, `S/03-estado-del-arte.tex`) con el mismo criterio. Verificacion: la medicion de ambos archivos baja en mas de 60 y en mas de 40; no se altera ninguna cita ni clave bibliografica (`rg -c "\\\\cite" ...` sin cambios de conteo).
- [x] 3.3 Capitulo 4 (`S/04-marco-metodologico.tex`) con el mismo criterio, **sin tocar** las secciones `4.5` y `4.8` por N-06 (solo se admiten ediciones de longitud ajenas a la recitacion, y preferentemente ninguna). Verificacion: la medicion baja en mas de 60 y en mas de 40; el diff de `4.5` y `4.8` no contiene cambios motivados por la recitacion.
- [x] 3.4 Verificacion del grupo: `rg -c "de modo que" S/01-introduccion.tex S/02-marco-teorico.tex S/03-estado-del-arte.tex S/04-marco-metodologico.tex` baja respecto de la linea base; fotografias antes/despues de cifras y citas sin diferencias.

## 4. Grupo B2 — Afinado de capitulos 5 a 7

- [x] 4.1 Capitulo 5 (`S/05-arquitectura.tex`) y capitulo 6 (`S/06-implementacion.tex`) guiados por su Motivo principal (Arquitectura; Desarrollo): partir oraciones largas y acotar "de modo que". Verificacion: la medicion de ambos baja en mas de 60 y en mas de 40; no cambian conteos de nodos ni de capas.
- [x] 4.2 Capitulo 7 (`S/07-resultados.tex`) guiado por Resultados y por N-12 (no reiterar cifras): partir oraciones largas y remitir las cifras repetidas con `\autoref` en lugar de reiterarlas. Verificacion: la medicion baja en mas de 60 y en mas de 40; la foto de cifras canonicas (1.3) no cambia.
- [x] 4.3 Verificacion del grupo: `rg -c "de modo que" S/05-arquitectura.tex S/06-implementacion.tex S/07-resultados.tex` baja; `git diff` no altera `\label` existentes.

## 5. Grupo B3 — Afinado de capitulos 8 a 11, Anexos y Referencias

- [x] 5.1 Capitulo 8 (`S/08-discusion.tex`) con el Motivo principal de Discusion, **sin tocar** la seccion `9.1` por N-06. Verificacion: la medicion baja en mas de 60 y en mas de 40; el diff de `9.1` no contiene cambios por la recitacion.
- [x] 5.2 Capitulos 9 y 10 (`S/09-conclusiones.tex`, `S/10-recomendaciones.tex`) guiados por Conclusiones y N-12: retirar valoraciones sin respaldo (por ejemplo "una via practicamente util") y sintetizar en lugar de reiterar cifras. Verificacion: `rg -n -i "practicamente util|economicamente accesible" S/09-conclusiones.tex S/10-recomendaciones.tex` sin valoraciones sin respaldo; la medicion baja en mas de 60 y en mas de 40.
- [x] 5.3 Capitulo 11 (`S/11-aspectos-legales.tex`) con el mismo criterio de longitud, sin alterar afirmaciones legales. Verificacion: la medicion baja en mas de 60 y en mas de 40; ninguna afirmacion legal cambia de sentido.
- [x] 5.4 Anexos (`S/12-anexos.tex`) y lista de referencias: acotar oraciones largas del Anexo I y de la prosa de anexos; no tocar entradas bibliograficas. Verificacion: la medicion de `S/12-anexos.tex` baja en mas de 60 y en mas de 40; `python verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) sigue en PASS.
- [x] 5.5 Verificacion del grupo: "de modo que" global por debajo de la linea base; `git diff` sin cambios en `Bibliography_base.bib`.

## 6. Cierre — compilacion, derivados y registro

- [x] 6.1 Perfil de guardarrailes: `rg -n -E "\b[cC]-[0-9]{2,3}[ab]?\b" S/0*.tex S/1[01]-*.tex` sin coincidencias fuera del Anexo I y de comentarios; `rg -n "0\{?,\}?87" S/` solo en `4.4` y la nota de versiones del Anexo I. Verificacion: ambas busquedas con el resultado esperado; reportar salidas.
- [ ] 6.2 Recompilar (`latexmk -xelatex main.tex` en el entorno de registro): 0 errores fatales, 0 referencias y citas indefinidas, 0 etiquetas duplicadas, `main.blg` sin WARN/ERROR, 0 `??` en el texto extraido. Verificacion: se produce `paper/main.pdf`; se reporta el total de paginas y su delta respecto de `v1.2.18`. Diferida por indicacion del usuario: el PDF se recompila aparte.
- [ ] 6.3 Regenerar `paper/compilacion.md` con `C/resumir_registro_compilacion.py` y `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py` (no vacio). Verificacion: el SHA-256 de `compilacion.md` coincide con `sha256sum main.pdf`; `tesis_para_agente.md` no esta vacio. `tesis_para_agente.md` se regenero; `compilacion.md` queda pendiente de la recompilacion diferida.
- [x] 6.4 Cotejo de cifras: comparar la foto de 1.3 con el estado final. Verificacion: cero diferencias; ninguna cifra canonica cambio de valor.
- [x] 6.5 Medir el resultado final con la regla de 1.1 y consignar la linea base y el resultado en `C/dictamen-correcciones.md` (seccion `c-197`), junto con el inventario de pasajes editados por capitulo. Verificacion: el registro tiene, por capitulo, el pasaje y el motivo atendido; la concision final es menor que la linea base.
- [x] 6.6 `CHANGES.md`: agregar la fase de `c-197` con su scope, la dependencia de orden (`c-196` antes que `c-197`) y el estado. Verificacion: la entrada existe y cita la dependencia.
- [x] 6.7 `openspec validate c-197-afinar-escritura-y-correcciones-por-capitulo --strict --no-interactive`. Verificacion: el comando pasa (0 errores).
