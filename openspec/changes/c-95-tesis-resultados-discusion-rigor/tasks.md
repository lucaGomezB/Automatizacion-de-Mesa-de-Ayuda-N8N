# Tasks: c-95 — Rigor de Resultados y Discusión, y límites del Capítulo 9

> Convención: `S = docs/Tesis/v9 (IA)/paper/sections`.
> Verificación de texto: `rg` sobre archivos activos (los `.bak` no se editan ni
> se cuentan). No hay toolchain LaTeX local: la recompilación final es en Overleaf
> con XeLaTeX.
>
> **D-ORDER (obligatorio):** aplicar este change DESPUÉS de c-76, c-77, c-78 y
> c-80. Comparte `S/04-marco-metodologico.tex`, `S/07-resultados.tex`,
> `S/08-discusion.tex` y `S/09-conclusiones.tex` con ellos. No se editan las
> frases propiedad de c-76 (números), c-77 (\(W=0\), calibración), c-78 (Revina y
> evidencia contraria) ni c-80 (deduplicación 8.1/9.1 y rebaja de juicios).
> No se toca `App/**`, `data/corpus_evaluacion_pseudonimizado.json`,
> `evaluation/stats.py`, `CHANGES.md` ni los artefactos de los changes previos.

## 1. Preparación y fuentes de verdad

- [ ] 1.1 Confirmar que c-76, c-77, c-78 y c-80 están aplicados: verificar que `07-resultados.tex` reporta 73,5 % y 0,5207, que no queda `W = 0` en `S/07-resultados.tex` ni en `S/09-conclusiones.tex`, y que `08-discusion.tex` ya no atribuye BERT/91 % a Revina. Verificar con `openspec list --json` y con `rg -n "73,5|0,5207|W = 0|Revina.*BERT" "docs/Tesis/v9 (IA)/paper/sections"`. Si falta alguna dependencia, detener la aplicación y registrar el bloqueo.
- [ ] 1.2 Registrar el corpus de trabajo: calcular el SHA-256 de `data/corpus_evaluacion_pseudonimizado.json`, confirmar 200 casos y los campos `tiempo_manual_s`, `tiempo_automatizado_s`, `descripcion`, `sector_asignado`. Verificar con `sha256sum data/corpus_evaluacion_pseudonimizado.json` y un conteo de casos que devuelva 200.
- [ ] 1.3 Inventariar el estado actual de los siete hallazgos con `rg`: Shapiro en `04:63`, errores sin ejemplo en `07:90-110`, §8.1 sin interrogación en `08:6-16`, baseline en `08:38`, costos en `08:46`, \(W=0\) en `09:16` y afirmación general en `09:22`. Verificar que cada ancla existe antes de editar (las líneas pueden haberse desplazado por las dependencias).
- [ ] 1.4 Confirmar que no existen artefactos del baseline TF-IDF+SVM: barrer `rg -ni "tf.?idf|svm|baseline" evaluation scripts docs data` y verificar que no hay script, partición, predicciones ni fixtures del baseline. Si aparece un artefacto, registrarlo y reconsiderar D3 antes de retirar la cifra.

## 2. A-15 — Reporte de Shapiro-Wilk

- [ ] 2.1 Recalcular Shapiro-Wilk sobre el corpus corregido por c-77 (E3): ejecutar `scipy.stats.shapiro` sobre tiempos manuales, automatizados y diferencias pareadas; registrar \(n\), \(W\) y \(p\) de los tres conjuntos. Verificar que el cálculo usa 200 pares y que el resultado se guarda con la fecha y el hash del corpus.
- [ ] 2.2 Agregar a `evaluation/report.md` una sección "Normalidad (Shapiro-Wilk)" con la tabla de los tres conjuntos, el comando reproducible y el hash del corpus. Verificar que los valores de la tabla coinciden exactamente con la salida de 2.1.
- [ ] 2.3 Reescribir `S/04-marco-metodologico.tex:63` para reportar \(W\) y \(p\) de Shapiro-Wilk en el flujo manual, el automatizado y las diferencias, manteniendo \(\alpha = 0{,}05\) y la justificación de Wilcoxon. Verificar con `rg -n "Shapiro|W = |p =" "docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex"` que aparecen los tres conjuntos y que no queda solo "\(p < 0{,}01\)".
- [ ] 2.4 Agregar en `S/07-resultados.tex:30` una referencia breve al reporte de normalidad de §4.7, sin duplicar los valores ni introducir un estadístico nuevo que compita con la corrección de Wilcoxon de c-77. Verificar con `rg -n "Shapiro|normalidad" "docs/Tesis/v9 (IA)/paper/sections/07-resultados.tex"`.

## 3. A-20 — Interrogación crítica en §8.1

- [ ] 3.1 Agregar al final de §8.1 (después del párrafo de `S/08-discusion.tex:16`, antes de §8.2 en `:18`) un párrafo con al menos tres explicaciones rivales de la reducción de tiempo: asimetría del instrumento, simplificación de la tarea o mezcla de canales, novedad/Hawthorne o aprendizaje, y selección de la muestra. Para cada una, declarar la evidencia disponible, qué la debilita y qué observación permitiría descartarla. Verificar con `rg -ni "rival|instrumento|Hawthorne|aprendizaje|selección" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"` y por lectura del párrafo.
- [ ] 3.2 Agregar un párrafo sobre la confusión sistemática de Sistemas usando la matriz 5x5 y las métricas reales: precisión 0,3684, sensibilidad 0,4375, F1 0,4000; 7 aciertos y confusiones con Soporte Tecnico Software (5), Bases de Datos (2) y Seguridad Informatica (2). Distinguir ambigüedad léxica/taxonómica de falta de contexto y aclarar que Bases de Datos tiene \(n=1\), por lo que su F1 nulo no es estimable. Verificar los valores contra `evaluation/report.md` con `rg -n "0.3684|0.4375|0.4000" evaluation/report.md` y con `rg -ni "Sistemas|ambigüedad|taxonom" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"`.
- [ ] 3.3 Agregar un párrafo de cierre que separe "consistente con la hipótesis" de "confirmación concluyente" y que declare qué no puede descartarse con el diseño actual; remitir a §4.8 sin repetir sus amenazas. Verificar con `rg -ni "consistente|concluyente|no puede descartarse" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"`.
- [ ] 3.4 Verificar que no se duplican frases propiedad de c-80 F7 ni la tensión de c-78 B1: `rg -ni "valida la hipotesis|consecuencia deseable|materializa el esquema|Revina|BERT" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"` debe conservar exactamente las apariciones previas, sin nuevas.

## 4. A-21 — Alcance del baseline TF-IDF+SVM

- [ ] 4.1 Reescribir `S/08-discusion.tex:38` (quinto punto de "Limitaciones") para retirar "78 %" y "0,764" como resultados y eliminar "confirma que el esquema hibrido propuesto aporta una ganancia sustantiva". Declarar que el chequeo fue exploratorio, que la partición y el \(n\) no se preservaron y que no se reporta como comparación válida. Verificar con `rg -n "78~?\\\\?%|0,764|ganancia sustantiva" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"` sin coincidencias en el pasaje del baseline.
- [ ] 4.2 Agregar en el mismo punto la declaración de que una comparación sistemática contra clasificadores supervisados sobre el corpus completo queda como trabajo futuro, sin prometer resultados ni presentar el chequeo exploratorio como evidencia de superioridad. Verificar por lectura y con `rg -ni "trabajo futuro|comparación sistemática|exploratorio" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"`.
- [ ] 4.3 Verificar que ninguna otra sección usa las cifras del baseline: `rg -n "0,764|78~?\\\\?%|TF-IDF\\+SVM" "docs/Tesis/v9 (IA)/paper/sections"` debe mostrar solo referencias bibliográficas legítimas (por ejemplo Paramesh) y ninguna cifra del baseline propio.

## 5. M-10 — Ejemplos textuales anonimizados en §7.4

- [ ] 5.1 Seleccionar 2–3 casos mal clasificados de `evaluation/predicciones.json` que ilustren los tres patrones de la Tabla 9 (descripción corta, mezcla de categorías, jerga local). Verificar que el par `sector_asignado`/`sector_predicho` y la `confianza` coinciden con el registro y con la matriz 5x5 de `evaluation/report.md`.
- [ ] 5.2 Anonimizar los textos: eliminar nombres de personas, correos, teléfonos, direcciones, nombres internos de sistemas y cualquier identificador que permita reidentificación. Verificar con un barrido manual y con `rg -ni "@|tel[eé]fono|av\.|calle|dni|legajo"` sobre los textos redactados; conservar solo el rasgo que explica el error.
- [ ] 5.3 Insertar los ejemplos en `S/07-resultados.tex` §7.4, después del párrafo que cierra la tipología (`:108`) y antes de la remisión a trabajo futuro (`:110`). Cada ejemplo MUST indicar descripción anonimizada, sector asignado, sector predicho y confianza. Verificar con `rg -n "asignado|predicho|confianza" "docs/Tesis/v9 (IA)/paper/sections/07-resultados.tex"` y contar 2–3 ejemplos.
- [ ] 5.4 Verificar que no se alteran la Tabla 9 ni sus conteos: `rg -n "43,8|37,5|18,8|16 errores|7 &|6 &|3 &" "docs/Tesis/v9 (IA)/paper/sections/07-resultados.tex"` debe conservar los valores previos.

## 6. M-16 — Fuentes y cotas de costos en §8.4

- [ ] 6.1 Reunir la fuente oficial del costo de inferencia: página de precios de Gemini API, modelo declarado como desplegado en la tesis y fecha de consulta. Calcular el costo por invocación con supuestos explícitos de tokens de entrada y salida; si el resultado no es 0,02 USD, reemplazar la cifra por el calculado o por un rango. Verificar que la fuente y la fecha quedan citadas en una nota al pie.
- [ ] 6.2 Reunir una fuente pública del costo de infraestructura (por ejemplo, precio on-demand de una instancia con 2 vCPU y 4 GB, 730 h/mes) y declarar los rubros incluidos: cómputo, almacenamiento, respaldo y transferencia. Si solo se sostiene un orden de magnitud, expresar una cota con supuestos, no una cotización. Verificar que la fuente y la fecha quedan citadas.
- [ ] 6.3 Reescribir `S/08-discusion.tex:46` para incorporar las fuentes o cotas de 6.1 y 6.2, y alinear el identificador de modelo con el que la tesis declara como desplegado (`gemini-3.6-flash`); no se introduce un precio para un modelo que el documento ya no declara. Verificar con `rg -n "USD|gemini|Gemini" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"` y revisar que cada cifra tenga nota o cota.
- [ ] 6.4 Verificar que no quedan cifras monetarias desnudas en §8.4: `rg -n "[0-9]+([.,][0-9]+)?~?\\\\?%? ?USD|USD ?[0-9]" "docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex"` y confirmar que cada aparición está acompañada por fuente, fecha o cota.

## 7. A-23 — Acotar la afirmación general de §9.2

- [ ] 7.1 Reescribir `S/09-conclusiones.tex:22` para limitar la afirmación al corpus, al dominio y al contraste efectivamente realizado; eliminar "superiores a los de clasificadores supervisados clasicos entrenados sobre representaciones estaticas" como conclusión general. Verificar con `rg -ni "superiores a los de clasificadores|representaciones estaticas|afirmación general de conocimiento" "docs/Tesis/v9 (IA)/paper/sections/09-conclusiones.tex"` sin la formulación general.
- [ ] 7.2 Remitir en §9.2 a la limitación de §8.3 y a la comparación disponible, sin duplicar la tensión bibliográfica de c-78 B1. Verificar con `rg -ni "Revina|BERT|evidencia contraria" "docs/Tesis/v9 (IA)/paper/sections/09-conclusiones.tex"` sin nuevas apariciones.
- [ ] 7.3 Verificar que la formulación conserva el aporte real (arquitectura híbrida, validación en español rioplatense, dominio de mesa de ayuda) sin convertirlo en una ley general sobre LLM. Verificar por lectura y con `rg -ni "en este corpus|en este dominio|este trabajo" "docs/Tesis/v9 (IA)/paper/sections/09-conclusiones.tex"`.

## 8. A-25 — Retirar la interpretación estadística de §9.1

- [ ] 8.1 Reescribir `S/09-conclusiones.tex:16` para eliminar la lectura de \(W=0\) como "resultado poco frecuente" y "merece ser interpretada con cautela", y cualquier estadístico inferencial nuevo. Conservar solo la referencia breve al resultado y remitir a §7.1/§8.1. Verificar con `rg -n "W ?= ?0|poco frecuente|con cautela|duda razonable" "docs/Tesis/v9 (IA)/paper/sections/09-conclusiones.tex"` sin coincidencias.
- [ ] 8.2 Si la interpretación eliminada es necesaria, moverla a §8.1 o §7.1 sin duplicarla; verificar que no se reintroduce en Conclusiones y que el Capítulo 8 no repite literalmente el párrafo. Verificar con `rg -ni "poco frecuente|con cautela" "docs/Tesis/v9 (IA)/paper/sections"` y comparar ubicaciones.
- [ ] 8.3 Verificar que §9.1 no introduce estadísticos que no estén en el Capítulo 7: `rg -n "p <|p =|r =|W =" "docs/Tesis/v9 (IA)/paper/sections/09-conclusiones.tex"` y confirmar que cada valor tiene su fuente en §7.1 o §8.1.

## 9. Registro de correcciones y coordinación

- [ ] 9.1 Agregar a `docs/Tesis/Correcciones/dictamen-correcciones.md` un grupo "Resultados y Discusión (c-95)" con el mapeo A-15, A-20, A-21, M-10, M-16, A-23 y A-25, la corrección aplicada, los archivos y la fecha. Verificar con `rg -n "c-95|A-15|A-20|A-21|M-10|M-16|A-23|A-25" docs/Tesis/Correcciones/dictamen-correcciones.md`.
- [ ] 9.2 Registrar la decisión de D3 (baseline exploratorio no reproducible, no reconstruido) y la coordinación con c-76, c-77, c-78 y c-80, incluyendo que c-95 no reintroduce \(W=0\) ni la atribución de Revina. Verificar por lectura del registro.

## 9bis. Reubicación de la tabla de tiempos por canal (coordinación con c-77)

- [ ] 9bis.1 Reubicar la tabla `tab:tiempos-canal` que c-77 agregó en §7.1 (telefonía 20,09 s, correo 27,65 s, web 1,88 s, global 17,76 s) a la ubicación definitiva que fije la reestructuración de §7, sin duplicarla ni dejarla huérfana; verificar que `\ref{tab:tiempos-canal}` resuelve y que la tabla queda coherente con la tabla de estadísticos globales. Verificar con `rg -n "tiempos-canal" "docs/Tesis/v9 (IA)/paper/sections/"`.

## 10. Verificación final y recompilación

- [ ] 10.1 Barrido de control en las secciones: `rg -n "W = 0|poco frecuente|interpretada con cautela|78~?\\\\?%|0,764|ganancia sustantiva|superiores a los de clasificadores|50--100 USD|0,02 USD" "docs/Tesis/v9 (IA)/paper/sections"` y verificar que no quedan formulaciones retiradas sin fuente, salvo las que el change decidió conservar con cota explícita.
- [ ] 10.2 Verificar que el change no tocó `App/**`: `git status --porcelain` no debe listar archivos bajo `App/`. Verificar también que no se modificaron `data/corpus_evaluacion_pseudonimizado.json` ni `evaluation/stats.py`.
- [ ] 10.3 Recompilar la tesis en Overleaf (`main.tex`, XeLaTeX): PDF sin errores fatales, tablas y notas al pie renderizan, y la longitud no supera las 100 páginas. Registrar el conteo de páginas.
- [ ] 10.4 Ejecutar `openspec validate c-95-tesis-resultados-discusion-rigor --strict` y confirmar que pasa sin errores.
