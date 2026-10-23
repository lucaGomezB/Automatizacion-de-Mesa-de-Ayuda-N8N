Convenciones de estas tareas: las rutas `sections/` se refieren a `docs/Tesis/v10 (IA)/paper/sections/` y los comandos se ejecutan desde la raiz del repositorio salvo indicacion. Los textos de `design.md` (D9) se transcribieron sin tildes y se aplican con la acentuacion normalizada del manuscrito. Los `grep` usan subcadenas sin caracteres acentuados (prefijos que terminan antes de la vocal con tilde), para no depender de la configuracion regional; todos los patrones se comprobaron contra las fuentes de v1.1.1. Cada sitio se ubica por etiqueta o por subcadena, no por numero de linea, porque otros changes pueden desplazar las lineas.

## 1. Precondiciones y linea base

- [ ] 1.1 Obtener del autor las decisiones de las Open Questions 1, 2 y 3 de `design.md`: opcion A con cota `0,15` o B para la segunda sub-hipotesis; rotulo "contrastada de forma acotada" o fallback "no contrastada" para la subsidiaria de eficiencia; condicion (iii) del objetivo 3. Registrarlas como borrador de la seccion del change en `docs/Tesis/Correcciones/dictamen-correcciones.md` y elegir la variante de T1, T3 y T10 que corresponda. Verificar que no se edita ningun `.tex` antes de tenerlas registradas.
- [ ] 1.2 Verificar que c-130, c-131, c-142 y c-132 ya se aplicaron (orden definitivo fijado por c-141; `openspec list --json` o sus carpetas en `openspec/changes/archive/`) y relevar lo que publicaron para elegir las variantes de T10, T12, T15 y T18:
  - c-130: terminologia de la etapa determinista.
  - c-131: etiqueta de la calidad por canal (si la publico), filas de McNemar en el memo y su registro sobre `cache_meta`.
  - c-142: etiqueta `subsec:sensibilidad-ajustes` (`grep -n "subsec:sensibilidad-ajustes" sections/07-resultados.tex`); resultado de la variante E4, es decir, si con el vocabulario previo la etapa de reglas supera o no a Gemini (regla de decision de D3); y su limitacion nueva en `subsec:limitaciones-estudio`, con el cardinal de la lista resultante.
  - c-132: etiqueta `subsec:balance-neto` (`grep -n "subsec:balance-neto" sections/08-discusion.tex`) y texto exacto de sus clausulas en `sections/09-conclusiones.tex` (parrafos :6 y :41) y en `sections/00-resumen.tex`. Copiar ese texto al borrador para comprobar en 5.2 y 5.6 que queda literal.

  Anotar el resultado en el borrador de 1.1.
- [ ] 1.3 Compilar la linea base con el contenedor del proyecto. La imagen se construye una vez con `docker build -t texlive-thesis -f "docs/Tesis/v10 (IA)/paper/Dockerfile" "docs/Tesis/v10 (IA)/paper"` y el PDF se compila con `docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`. Registrar tres mediciones:
  - Total de paginas: `grep -o "Output written on main.pdf ([0-9]* pages" "docs/Tesis/v10 (IA)/paper/main.log"`.
  - Paginas de inicio de cada capitulo: `grep "contentsline {section}" "docs/Tesis/v10 (IA)/paper/main.toc"`.
  - Palabras de prosa del resumen y del abstract, con un script fijo que aplique la regla de c-106: quitar comandos LaTeX, `~` y los delimitadores `\(` `\)`, contar los tokens con al menos un caracter alfanumerico y excluir las lineas de palabras clave. El mismo script se reutiliza en 6.3.

## 2. Gate 0: memo de numeros canonicos (D6)

- [ ] 2.1 En `docs/Tesis/Correcciones/numeros-canonicos.md`, Seccion 3.2: pasar la fila "Macro-F1 (4 clases estimables): `0,6508`" de `condicional` a `vigente` con la nota "Primaria de umbral (c-133 D1)", y agregar a la fila de `0,5207` la nota "Informativa; toda cita lleva su aclaracion". Verificar con `grep -n "0,6508" docs/Tesis/Correcciones/numeros-canonicos.md` que la fila de la Seccion 3.2 dice `vigente`.
- [ ] 2.2 En la Seccion 3.3, agregar `65,5 %` (131/200) y `34,5 %` (69/200), con procedencia `evaluation/report.md:9-10` y `08-discusion.tex:10,58` y estado `vigente`. Verificar con `grep -n "65,5\|34,5" docs/Tesis/Correcciones/numeros-canonicos.md`.
- [ ] 2.3 Agregar la Seccion 3.7, "Contraste acotado de la hipotesis subsidiaria de eficiencia (c-133)", con:
  - `0,7405` (97/131), procedencia `docs/deterministic_calibration.md:40,67`.
  - `0,6769` (88/130), procedencia `:41,68`.
  - La cota `0,15 = 1 - 0,85` de la segunda sub-hipotesis, procedencia `01-introduccion.tex:48`, nota "explicitada por c-133; no es un resultado".
  - Las notas de cache FORCE-ESCALATE `hybrid-v2`, del caso excluido y del comando de reproduccion.

  Verificar con `grep -n "0,7405\|0,6769\|88/130\|97/131\|0,15" docs/Tesis/Correcciones/numeros-canonicos.md`.
- [ ] 2.4 Agregar la linea "Upsert c-133" al encabezado del memo y anotar el item 5 de la Seccion 5 ("superado por c-133 D1") y el punto 4 de la Seccion 7 ("decision ratificada por c-133"), sin reescribir el resto del texto historico. Verificar con `grep -c "c-133" docs/Tesis/Correcciones/numeros-canonicos.md`, que debe dar 4 o mas.
- [ ] 2.5 Leer en el memo el estado de la prueba pareada, que calcula y registra c-131 (dueno de las caches). c-133 no la calcula ni invoca a Gemini.
  - Si el memo registra b, c y `p` de McNemar, T10 los cita y la Seccion 3.7 remite a esas filas.
  - Si el registro de c-131 sobre `cache_meta` indica otro modelo o prompt que la corrida oficial, aplicar el fallback de D3 y anotarlo en el borrador de 1.1.
  - Si no hay prueba registrada, anotar "sin prueba pareada" en la Seccion 3.7.

  Verificar que no hubo llamadas pagas: ningun uso de `--confirm-paid` ni de `run_evaluation.py --force`.

## 3. B6: metrica primaria del F1 macro (D1)

- [ ] 3.1 Aplicar T2 en la tercera sub-hipotesis (`sections/01-introduccion.tex`, `subsec:hipotesis-trabajo`): "F1 macro de umbral no inferior a 0,85" y "macro-F1 de umbral de 0,6508 sobre las cuatro clases estimables". Verificar que `grep -n "0[,.]5207" sections/01-introduccion.tex` no devuelve nada y que `grep -n "0,6508" sections/01-introduccion.tex` muestra el rotulo "de umbral".
- [ ] 3.2 Aplicar T5 en la fila "F1 macro promediado" de `tab:variables` y T7 en la oracion "La clase de soporte unitario..." de `subsec:analisis-estadistico` (`sections/04-marco-metodologico.tex`). Verificar que `grep -c "cinco sectores objetivo" sections/04-marco-metodologico.tex` da 0 y que `grep -n "contra el cual se eval" sections/04-marco-metodologico.tex` devuelve una linea.
- [ ] 3.3 Aplicar T8 solo en la oracion del macro-F1 de `subsec:matriz-metricas` (`sections/07-resultados.tex`), sin tocar el resto del parrafo, que pertenece a c-131. Verificar con `grep -n "un quinto del promedio" sections/07-resultados.tex` y `grep -n "no altera el veredicto" sections/07-resultados.tex`.
- [ ] 3.4 Aplicar T17 en el resumen y el abstract (`sections/00-resumen.tex`), solo en las oraciones de macro-F1 y de estado por sub-hipotesis. Verificar que `grep -n "cinco clases, 0,5207\|five-class macro-F1" sections/00-resumen.tex` no devuelve nada, que `grep -n "0,6508\|0.6508" sections/00-resumen.tex` devuelve dos lineas y que `grep -c "no contrastada por ausencia de registro primario" sections/00-resumen.tex` da 1 o mas.
- [ ] 3.5 Aplicar la fila del objetivo 2 de T12 en `tab:cumplimiento-objetivos`: "Exactitud 73,5~\%, IC [67,0~\%, 79,1~\%]; macro-F1 de umbral 0,6508 (0,5207 con cinco clases, una no estimable)", con el corchete del IC cerrado. Verificar con `grep -n "macro-F1 de umbral 0,6508" sections/09-conclusiones.tex`.
- [ ] 3.6 Verificar que `sections/08-discusion.tex` conserva los rotulos de `0,6508` y `0,5207` (sin edicion esperada) y ejecutar el control global: `grep -n "0[,.]5207" sections/*.tex | grep -v -i "cinco\|five\|no estimable\|unitario"` y `grep -n "0[,.]6508" sections/*.tex | grep -v -i "umbral\|threshold\|cuatro\|four\|estimable"` no devuelven nada.

## 4. B5: hipotesis (D2, D3)

- [ ] 4.1 Aplicar T1, o la variante B si el autor la eligio en 1.1, en la segunda sub-hipotesis (`sections/01-introduccion.tex`). Verificar:
  - `grep -n "0,15" sections/01-introduccion.tex` devuelve la cota.
  - `grep -n "no era contrastable" sections/01-introduccion.tex` devuelve una linea.
  - `grep -c "no contrastada por ausencia de registro primario" sections/01-introduccion.tex` da 1 o mas.
  - `grep -n "9,5" sections/01-introduccion.tex` no devuelve nada.
- [ ] 4.2 Aplicar T3, o su variante de fallback, al final del parrafo de hipotesis subsidiarias. Verificar con `grep -n "Ninguna tiene contraste formal" sections/01-introduccion.tex`.
- [ ] 4.3 Aplicar T4 (compensacion): eliminar la ultima oracion del parrafo del segundo objetivo especifico. Verificar:
  - `grep -c "Se trata, en consecuencia, de un criterio" sections/01-introduccion.tex` da 0.
  - Los tres criterios del umbral y sus fuentes siguen presentes: `grep -n "Paramesh2019_it_service_desk" sections/01-introduccion.tex`, `grep -n "propia de los autores" sections/01-introduccion.tex` y `grep -n "pueda ubicarse por encima" sections/01-introduccion.tex`.
- [ ] 4.4 Aplicar T9 en el parrafo de estado de `subsec:reduccion-intervencion` (`sections/07-resultados.tex`), sin tocar el parrafo del gate, que pertenece a c-130. Verificar con `grep -n "no superior a 0,15" sections/07-resultados.tex` y `grep -c "no contrastada por ausencia de registro primario" sections/07-resultados.tex` (1 o mas).
- [ ] 4.5 Aplicar T6 en las oraciones "La tercera..." y "La cuarta..." de `subsec:metricas-instrumentos` (`sections/04-marco-metodologico.tex`). Verificar con `grep -n "evaluada no se mid" sections/04-marco-metodologico.tex`.
- [ ] 4.6 Aplicar T10 en `sections/08-discusion.tex` (parrafo de la eficiencia del esquema hibrido), en la variante decidida en 1.1, 1.2 (regla de decision de E4 de D3) y 2.5. Verificar:
  - `grep -c "consistente con la hip" sections/08-discusion.tex` da 0.
  - Con el contraste acotado, `grep -n "0,7405" sections/08-discusion.tex`, `grep -n "0,6769" sections/08-discusion.tex` y `grep -n "de forma acotada" sections/08-discusion.tex` devuelven lineas, y las cifras quedan calificadas como estimaciones dentro de la muestra con remision a c-142: `grep -n "dentro de la muestra" sections/08-discusion.tex` y `grep -n "subsec:sensibilidad-ajustes" sections/08-discusion.tex` devuelven lineas.
  - Con el fallback, `grep -n "no se contrast" sections/08-discusion.tex` devuelve una linea.
- [ ] 4.7 Aplicar T18 en `subsec:limitaciones-estudio` (`sections/08-discusion.tex`), hallazgo de c-136: agregar al final de la lista la limitacion de intervencion humana no medida y actualizar el conteo de la oracion introductoria. Tras c-142 la lista parte de siete limitaciones ("El estudio presenta siete limitaciones..."), de modo que la nueva seria la octava y el conteo pasaria a "ocho"; el cardinal y el ordinal se verifican contra la lista al aplicar y no se asumen. Con el fallback de D2, en cambio, remitir en T1 a `subsec:reduccion-intervencion` y dejar aviso para c-136 en el borrador de 1.1. Verificar:
  - Opcion principal: `grep -n "registro primario de la acci" sections/08-discusion.tex` devuelve una linea, y el conteo de la oracion introductoria coincide con el numero de limitaciones listadas, contando los ordinales desde "Primero" hasta el ultimo (con c-142 aplicado, el esperado es ocho).
  - Fallback: `grep -n "subsec:reduccion-intervencion" sections/01-introduccion.tex` devuelve la remision de la segunda sub-hipotesis.
- [ ] 4.8 (Solo si 6.2 lo requiere) Compensacion de reserva: eliminar la oracion "Tres aspectos de los resultados merecen una interpretacion detallada." de `subsec:interpretacion-resultados`. Verificar con `grep -c "Tres aspectos de los resultados" sections/08-discusion.tex`, que debe dar 0.

## 5. B4: tabla de cumplimiento y prosa de conclusiones (D4, D5)

- [ ] 5.1 Aplicar T12 en las filas del objetivo general y de los objetivos especificos 1, 3 y 4 de `tab:cumplimiento-objetivos`, en la variante de la fila del objetivo 3 que corresponda segun 1.2. Verificar que `grep -c "Alcanzado parcialmente" sections/09-conclusiones.tex` da 4 o mas, y que la tabla contiene "sincr", "TLS" y "no medid": `grep -n "sincr\|TLS\|no medid" sections/09-conclusiones.tex`. La fila del objetivo 4 remite a la subseccion de c-132: `grep -n "subsec:balance-neto" sections/09-conclusiones.tex` devuelve una linea.
- [ ] 5.2 Aplicar T11 en el primer parrafo de `sections/09-conclusiones.tex`, conservando literal la clausula de viabilidad asignada a c-132. Verificar:
  - `grep -n "cumplido parcialmente el objetivo general" sections/09-conclusiones.tex` devuelve una linea.
  - `grep -c "ha cumplido con el objetivo general" sections/09-conclusiones.tex` da 0.
  - `grep -n "subsidiarias" sections/09-conclusiones.tex` devuelve una linea.
  - La clausula de viabilidad, en la forma que dejo c-132 (copia de 1.2), sigue literal: `git diff` no la muestra modificada.
- [ ] 5.3 Aplicar T13 en el parrafo de arquitectura. Verificar que `grep -c "los principios de separaci" sections/09-conclusiones.tex` da 0 y que `grep -n "se alcanza, sin embargo, solo parcialmente" sections/09-conclusiones.tex` devuelve una linea.
- [ ] 5.4 Aplicar T14 en el parrafo del clasificador hibrido, con la terminologia de c-130 para la etapa determinista. Verificar con `grep -n "contraste acotado" sections/09-conclusiones.tex` y comprobar que no queda "con confianza suficiente" si c-130 retiro esa formulacion (`grep -c "con confianza suficiente" sections/09-conclusiones.tex`).
- [ ] 5.5 Aplicar T15 en el parrafo de canales, en la variante segun 1.2, sin tocar la oracion del canal telefonico ("El canal telefonico ... demostracion de laboratorio"): su salvedad de cota inferior (B13) la agrega despues c-135. Verificar:
  - `grep -c "no introduce dispersi" sections/09-conclusiones.tex` da 0.
  - `grep -n "no la contrastan" sections/09-conclusiones.tex` devuelve una linea.
  - La oracion del canal telefonico sigue literal: `grep -c "demostraci" sections/09-conclusiones.tex` sigue dando 1 y `git diff` no la muestra modificada.
- [ ] 5.6 Aplicar T16 en el parrafo de comparacion, conservando literal la clausula de c-132 en la forma en que c-132 la dejo (copia de 1.2). Verificar con `grep -n "fico se alcanza parcialmente" sections/09-conclusiones.tex` y comprobar en `git diff` que la clausula de c-132 no aparece modificada.
- [ ] 5.7 Verificar que los enunciados de los objetivos no cambiaron: en `git diff -- "docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex"`, los parrafos del objetivo general y de los objetivos especificos 1 y 3 a 6 no tienen cambios, y el del objetivo 2 solo pierde su ultima oracion (T4).
- [ ] 5.8 Decidir y aplicar la fila del objetivo 6 de `tab:cumplimiento-objetivos` (D4), con la evidencia de c-142: "Alcanzado" (recomendacion) si estan disponibles la tipologia de errores (`subsec:analisis-errores`), la calibracion por etapa de c-131 y `subsec:sensibilidad-ajustes`; si falta alguna, aplicar la regla general de D4 y nombrar el componente faltante. Verificar con `grep -n "subsec:sensibilidad-ajustes" sections/09-conclusiones.tex` y `grep -n "subsec:analisis-errores" sections/09-conclusiones.tex`, y registrar la decision en el borrador de 1.1.

## 6. Compilacion, paginas y palabras (D8)

- [ ] 6.1 Recompilar con el comando de 1.3. Verificar que `main.log` no contiene errores (`grep -c "^! " "docs/Tesis/v10 (IA)/paper/main.log"` da 0) ni referencias o citas indefinidas (`grep -c "undefined" "docs/Tesis/v10 (IA)/paper/main.log"` da 0), y que el texto del PDF no contiene `??`.
- [ ] 6.2 Comparar con la linea base de 1.3 el total de paginas (`Output written on main.pdf (N pages)`) y las paginas de inicio de capitulo (`main.toc`). Si el total aumento o se desplazo el inicio de algun capitulo:
  - Aplicar en orden 4.8 y luego ajustes de redaccion dentro de los parrafos propios de D7 (T1, T3, T10, T11, T14, T15, T18), sin cambiar cifras, rotulos ni estados, y recompilar.
  - Si persiste el exceso, registrar en `dictamen-correcciones.md` el capitulo, las lineas y las paginas excedentes para el gate G0 de c-141, que fija el tope global, sin recortar parrafos de otros changes.
- [ ] 6.3 Recontar con el script de 1.3 las palabras del resumen y del abstract. Ambos conteos deben ser menores o iguales que la linea base y estar en 250 o menos. Si el resumen supera 250, comprimir la descripcion del sistema (parrafo que empieza "Esta investigaci") conservando problema, componentes esenciales y canales; si el abstract supera 250, comprimir de forma analoga su parrafo "This thesis designs". Recontar y registrar ambos valores.
- [ ] 6.4 Revisar que todos los textos aplicados lleven la acentuacion normalizada: los textos de D9 se transcribieron sin tildes. Verificar en las lineas de `git diff -U0 -- "docs/Tesis/v10 (IA)/paper/sections/"` que no aparecen formas sin tilde como "hipotesis", "sincronica", "deterministica", "especifico", "estimacion" o "clasificacion" en el texto nuevo.

## 7. Verificacion global y trazabilidad

- [ ] 7.1 Verificar que cada cifra nueva del texto editado (`0,15`, `97`, `131`, `0,7405`, `88`, `130`, `0,6769`, `65,5`, `0,6508` y, si se computo, los valores de McNemar) figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con el mismo valor, y que `grep -n "9,5" sections/*.tex` no devuelve ninguna proporcion de intervencion humana.
- [ ] 7.2 Verificar el rotulo de la segunda sub-hipotesis en los cuatro capitulos: `grep -c "no contrastada por ausencia de registro primario" sections/00-resumen.tex sections/01-introduccion.tex sections/07-resultados.tex sections/09-conclusiones.tex` da 1 o mas en cada archivo.
- [ ] 7.3 Verificar que los estados de las hipotesis subsidiarias coinciden en introduccion, discusion y conclusiones (`grep -n "subsidiari" sections/01-introduccion.tex sections/08-discusion.tex sections/09-conclusiones.tex` y lectura de cada pasaje).
- [ ] 7.4 Revisar `git diff` por archivo y confirmar que solo cambiaron los parrafos asignados a c-133 en la tabla de D7, que las oraciones de c-130, c-131, c-142 y c-132 (aplicados antes) dentro de parrafos compartidos quedaron literales y que no se toco la oracion del canal telefonico de `09-conclusiones.tex` (B13, c-135).
- [ ] 7.5 Regenerar el render solo como verificacion: `python3 "docs/Tesis/v10 (IA)/build_tesis_para_agente.py" > "docs/Tesis/v10 (IA)/tesis_para_agente.md"`. Repetir sobre el render los controles de 3.6 y 7.2. La regeneracion final con el encabezado de version corresponde a c-141.
- [ ] 7.6 Completar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la seccion "Grupo: Hipotesis, objetivos y metrica primaria (c-133) - dictamen v10/v1.1.0 B4-B6" con:
  - El mapeo B4/B5/B6 a los sitios T1-T17.
  - Las decisiones D1-D4 con su reversibilidad y las decisiones del autor (1.1).
  - El estado de la prueba pareada (2.5).
  - Las mediciones de paginas y palabras antes y despues (1.3, 6.2 y 6.3).
  - La aplicacion de la regla de decision de E4 (c-142) a la subsidiaria de eficiencia y la decision sobre el objetivo 6 (5.8).
  - Las notas de coordinacion: B13 queda en c-135 (oracion telefonica intacta); limitacion de intervencion humana incorporada o fallback de remision (4.7), con aviso a c-136; registro primario de intervencion como linea futura para c-136; autorizaciones de D7 (c-135, c-140 y c-141).

  Verificar con `grep -n "c-133" docs/Tesis/Correcciones/dictamen-correcciones.md`.
- [ ] 7.7 Ejecutar `openspec validate c-133-hipotesis-objetivos-metrica-primaria --type change --strict --no-interactive` y confirmar que es valido.
- [ ] 7.8 Confirmar el alcance con `git status --short`: solo cambian los seis `.tex` de `sections/` (00, 01, 04, 07, 08 y 09), los dos memos de `docs/Tesis/Correcciones/`, el render `tesis_para_agente.md` y los artefactos del change. No se tocan `App/`, `n8n/`, `evaluation/`, `data/`, `Bibliography_base.bib`, figuras ni tags.
