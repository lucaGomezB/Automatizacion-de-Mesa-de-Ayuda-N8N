## 1. Preparación, línea de base y prerregistro

- [x] 1.1 Leer los cuatro artefactos de entrada (`corpus_independiente_arbitrado.json`,
      `predicciones_arbitrado.json`, `doble_etiquetado_arbitrado.csv`,
      `arbitraje_tres_vias.json`) y confirmar con un conteo reproducible `206` casos, `476`
      filas de etiquetado, `64` arbitrados y `6` de tres vías; registrar los SHA-256 en la
      salida del análisis.
- [x] 1.2 Capturar la línea de base antes de editar: `sent_c197.py` (oraciones `> 60` por
      archivo), conteo de `0,8447` y `0,6893` en prosa por capítulo, total de páginas del PDF
      vigente y estado de compilación; guardar la salida como evidencia de partida.
- [x] 1.3 Fijar el método completo en el docstring de
      `evaluation/data/campana/analisis/analisis_ruido_referencia_c216.py` (kernel con
      suavizado Laplace `0,5`, mezcla convexa `Q_λ = (1−λ)Q + λm` con la marginal `m`,
      calibración de `λ` por bisección a kappa `0,6055 ± 0,005`, `B = 2000`, semilla
      `20261021`, cotas con `δ` de Wilson, rango de tres vías) y declarar que el prerregistro
      no fue ciego; verificar que el docstring contiene los parámetros antes de escribir
      código.

## 2. Análisis de ruido de referencia (TDD)

- [x] 2.1 **RED**: escribir las pruebas de las funciones puras (kernel fila-estocástica,
      calibración de `λ`, cotas distribution-free, rango de tres vías) con casos sintéticos
      que incluyan kappa perfecto y kappa nulo; ejecutar
      `python -m pytest evaluation/data/campana/analisis/test_analisis_ruido_referencia_c216.py -q`
      y confirmar que fallan porque las funciones no existen.
- [x] 2.2 **GREEN**: implementar la mínima versión de esas funciones y volver a ejecutar las
      pruebas hasta que pasen; registrar la salida.
- [x] 2.3 **TRIANGULATE**: agregar casos con kappa intermedio, `λ = 0` (sin ruido), filas de
      soporte chico y un caso de tres vías con tres etiquetas distintas; ejecutar y confirmar
      que la calibración reproduce el kappa objetivo dentro de `±0,005` y que las cotas
      contienen el valor observado.
- [x] 2.4 **REFACTOR**: extraer constantes y funciones puras, sin cambiar comportamiento;
      ejecutar las pruebas después de cada paso y confirmar que siguen en verde.
- [x] 2.5 Implementar la lectura de los artefactos y la simulación de `B = 2000` réplicas;
      ejecutar el script y verificar que reproduce `142/206` (`0,6893`) y macro-F1 `0,7024`
      antes de simular, y que aborta si un anclaje no coincide.
- [x] 2.6 Ejecutar el script dos veces y verificar que
      `analisis_ruido_referencia_c216.json`, `.md` y `.SHA256SUMS.txt` son idénticos byte a
      byte y que `git status` no muestra modificaciones fuera de la carpeta de análisis.
- [x] 2.7 Registrar la entrada del análisis en `evaluation/data/campana/analisis/README.md`
      (entradas, comando, salidas, pruebas y carácter aditivo) y verificar que el comando
      documentado corre desde la raíz del repositorio.

## 3. Memo canónico (sección 3.27, aditiva)

- [x] 3.1 Agregar la sección 3.27 a `docs/Tesis/Correcciones/numeros-canonicos.md` con el
      kappa `0,6055`/`p_o = 0,6867`, los `64` arbitrados y `6` de tres vías, el `λ*`, la
      mediana y percentiles `2,5`/`97,5` de exactitud y macro-F1, `δ`, las cotas y la
      descomposición; cada valor con archivo fuente y comando.
- [x] 3.2 Verificar que la sección 3.27 declara el carácter aditivo y que ningún valor de las
      secciones 3.1 a 3.26 cambió de cifra ni de estado; comparar el diff del memo y registrar
      el resultado.

## 4. Tesis: análisis de ruido (L2)

- [x] 4.1 Agregar el párrafo de método en `04-marco-metodologico.tex` (simulación calibrada,
      `B`, semilla, cotas y supuestos) con remisión al marco teórico del kappa; verificar que
      no duplica la teoría y que las citas resuelven.
- [x] 4.2 Agregar la subsección `subsec:ruido-referencia` en `07-resultados.tex`, después de
      `subsec:resultados-campana-medicion`, con la tabla (observado, mediana, `q2,5`, `q97,5`,
      `δ`, cotas y rango de tres vías) y dos párrafos de lectura; verificar que las cifras
      coinciden con la sección 3.27 y que no se presenta la simulación como verdad latente.
- [x] 4.3 Agregar el párrafo de lectura en `08-discusion.tex` que rotula el análisis como
      sensibilidad y declara que no elimina las demás amenazas del criterio 4; verificar la
      remisión a `subsec:ruido-referencia`.
- [x] 4.4 Verificar el presupuesto de páginas: compilar y confirmar que el crecimiento neto
      atribuible a L2 es de a lo sumo dos páginas; registrar el delta preliminar en el libro
      mayor.

## 5. Reencuadre del human-in-the-loop (L3)

- [x] 5.1 Reescribir en `08-discusion.tex` y `10-recomendaciones.tex` las frases que equiparan
      "la revisión humana no actuó" con "la confianza no discriminó": afirmar que el
      human-in-the-loop actuó por la regla del reportante (`147`; `66`+`81`; `25`; `17,0 %`) y
      que la señal de confianza no discriminó (AUROC `0,5168`); verificar con `rg` que no
      quedan las frases anteriores.
- [x] 5.2 Ajustar `07-resultados.tex`, `09-conclusiones.tex` y la frase de supervisión de
      `11-aspectos-legales.tex` para distinguir las dos señales y la configuración evaluada de
      la entregada; verificar que `147`, `66`, `81`, `25`, `17,0 %` y `0,5168` coinciden con el
      memo y que no se atribuyen casos al gate de confianza.
- [x] 5.3 **[DECISIÓN DEL DUEÑO — OQ1]** Si el dueño autoriza por escrito la corrida de la
      configuración entregada, ejecutarla con `evaluation/run_evaluation.py --confirm-paid` y
      registrar un cache nuevo sin tocar los congelados; si no la autoriza (por defecto),
      agregar en `08-discusion.tex` la limitación de que la configuración entregada no se midió
      y cerrar la tarea con esa rama. Verificar en ambos casos que la tesis no presenta
      resultados de una corrida no ejecutada. **Cierre real (2026-11-13):** el dueño determinó
      que la corrida era REDUNDANTE y no la autorizó; el clasificador entregado es lógicamente
      idéntico al evaluado (`bf5e099`..`HEAD` solo cambia documentación e importación perezosa en
      `app/classifiers`, sin tocar vocabulario, prompt ni umbrales), por lo que el texto declara
      la equivalencia en `08-discusion.tex` en lugar de la limitación.

## 6. Verificación y cierre de R4 (L4)

- [x] 6.1 Verificar que `confirmacion-posterior-consentimiento.md` registra `E3`, `E4` y `E5`
      con información verbal `2026-11-12` y confirmación `2026-11-13`, sin identidad, y que
      `11-aspectos-legales.tex` menciona a los tres con las mismas fechas y sin "pendiente";
      registrar el resultado como PASS/FAIL.
- [x] 6.2 Verificar que `evaluation/data/campana/registro_sujetos.csv` tiene `11` filas y que
      `E3`/`E4`/`E5` figuran con `rol = etiquetador` y sin datos personales; corregir en
      `evaluation/data/campana/README.md` el conteo "8 filas" y la lista de roles; verificar que
      el README y el CSV coinciden.
- [x] 6.3 Agregar la fila de verificación de R4 de c-216 en
      `docs/Tesis/Correcciones/dictamen-correcciones.md` y ejecutar
      `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` para confirmar `0`
      fallas; si el verificador no cubre la fila nueva, registrarlo y dejar la evidencia manual.
- [x] 6.4 Revisar el diff del capítulo legal antes de escribirlo con el dueño (gobernanza HIGH)
      y confirmar que solo se parten oraciones o párrafos, sin cambios de sentido, cifras ni
      citas.

## 7. Forma: repetición y oraciones largas (L5)

- [x] 7.1 Contar las apariciones en prosa de `0,8447` y `0,6893` por capítulo y reemplazar las
      repeticiones de `08`, `09` y `10` por `\autoref{tab:fuera-de-muestra}` o
      `\autoref{subsec:resultados-campana-medicion}`; verificar que cada pareja aparece como
      máximo una vez fuera de resultados y que las tablas quedan exentas.
- [x] 7.2 Partir en `11-aspectos-legales.tex` los párrafos de las líneas 14, 42, 10, 38 y 18 y
      las oraciones de las líneas 28 y 42; ejecutar
      `python docs/Tesis/Correcciones/sent_c197.py` y verificar `0` oraciones `> 60` palabras y
      ningún párrafo `> 2000` caracteres.
- [x] 7.3 Verificar que los cortes de 7.2 no cambiaron cifras, citas, remisiones ni salvedades
      (diff dirigido y `verify_citations.py`), y registrar en `dictamen-correcciones.md` cada
      oración y párrafo partido con su ubicación previa.

## 8. Compilación y verificación de cierre

- [x] 8.1 Compilar con la imagen `texlive-thesis` (`latexmk main.tex`) y verificar `0` errores
      fatales, `0` referencias o citas indefinidas y `0` etiquetas duplicadas; registrar el
      SHA-256 del PDF y el total de páginas.
- [x] 8.2 Ejecutar `python docs/Tesis/Correcciones/verify_citations.py`, `sent_c197.py`, el
      conteo de repeticiones y
      `python -m pytest evaluation/data/campana/analisis/test_analisis_ruido_referencia_c216.py -q`;
      confirmar todos en verde y registrar las salidas.
- [x] 8.3 Actualizar el libro mayor de páginas y la sección de trazabilidad del change en
      `dictamen-correcciones.md` con el delta de páginas, los cortes de L5 y el estado de R4;
      verificar que el exceso sobre el tope de `100` sigue declarado y honrado.
- [x] 8.4 Revisar el diff completo contra la línea de base de 1.2 y confirmar que ningún número
      canónico, corpus, predicción, configuración ni artefacto congelado cambió; registrar el
      resultado como evidencia de cierre.