## 1. Preparación, línea base y prerregistro

- [ ] 1.1 Leer los cuatro artefactos de entrada (`corpus_independiente_arbitrado.json`,
      `predicciones_arbitrado.json`, `doble_etiquetado_arbitrado.csv`, `arbitraje_tres_vias.json`) y
      confirmar con un conteo reproducible `206` casos, `476` filas de etiquetado, `142` de consenso,
      `64` arbitrados y `6` de tres vías; registrar los SHA-256 en la salida del análisis.
- [ ] 1.2 Capturar la línea de base antes de editar: cobertura `131`, cortocircuito `115` y aciertos
      `88/115` (`0,7652`) de la etapa determinística; `142/206` (`0,6893`) y macro-F1 `0,7024` del
      híbrido; total de páginas del PDF vigente y estado de compilación; guardar la salida como
      evidencia de partida.
- [ ] 1.3 Fijar el método completo en el docstring del script
      `evaluation/data/campana/analisis/analisis_sesgo_corpus_referencia_c219.py` (derivación del
      vocabulario corpus-blind y su independencia procedimental, métricas de la etapa determinística,
      definición de los subconjuntos de consenso y arbitrado, anclajes a reproducir, conjunto de tres
      vías vacío) y declarar que el prerregistro no es ciego; verificar que el docstring contiene los
      parámetros antes de escribir código.

## 2. Vocabulario corpus-blind y ablación de la etapa determinística (TDD)

- [ ] 2.1 **RED**: escribir las pruebas de las funciones puras (adaptador de scoring sobre
      `KEYWORD_MAP`, cobertura/precisión, deltas frente a `V1`, intervalo de Wilson) con casos
      sintéticos; ejecutar `python -m pytest evaluation/data/campana/analisis/test_analisis_sesgo_corpus_referencia_c219.py -q`
      y confirmar que fallan porque las funciones no existen.
- [ ] 2.2 **GREEN**: implementar la mínima versión de esas funciones y volver a ejecutar las pruebas
      hasta que pasen; registrar la salida.
- [ ] 2.3 **TRIANGULATE**: agregar casos con vocabulario vacío, empates de puntaje, un solo match y
      filas de soporte chico; ejecutar y confirmar que la etapa determinística reproduce `131` de
      cobertura, `115` de cortocircuito y `88/115` de precisión, y que el control de ablación de los
      `62` términos derivados del corpus reproduce `V0`.
- [ ] 2.4 **REFACTOR**: extraer constantes y funciones puras, sin cambiar comportamiento; ejecutar
      las pruebas después de cada paso y confirmar que siguen en verde.
- [ ] 2.5 Construir y versionar el vocabulario corpus-blind
      (`evaluation/data/campana/analisis/vocabulario_corpus_blind_c219.json`) desde la taxonomía
      canónica más un glosario público de mesa de ayuda, sin leer las descripciones del corpus;
      registrar fuente, procedimiento de derivación y SHA-256; verificar que cubre las cinco clases
      canónicas y que se fijó antes de la corrida.
- [ ] 2.6 Implementar la lectura de artefactos y la ablación sobre los `206`; ejecutar el script y
      verificar que reproduce los anclajes (`115`/`88` y `142/206`) antes de medir y que informa
      cobertura, cortocircuito y precisión con IC de Wilson para `V1`, el vocabulario corpus-blind y
      el control `V0`, con el delta frente a `V1` rotulado como sensibilidad.
- [ ] 2.7 Ejecutar el script dos veces y verificar que el `.json`, el `.md` y el `.SHA256SUMS.txt`
      son idénticos byte a byte y que `git status` no muestra modificaciones fuera de la carpeta de
      análisis.
- [ ] 2.8 Registrar la entrada del análisis en `evaluation/data/campana/analisis/README.md`
      (entradas, comando, salidas, pruebas y carácter aditivo) y verificar que el comando documentado
      corre desde la raíz del repositorio.

## 3. Análisis del subconjunto de alto acuerdo (TDD)

- [ ] 3.1 **RED**: escribir las pruebas de la construcción de subconjuntos desde
      `arbitraje_tres_vias.json` (consenso `n = 142`, arbitrado `n = 64`, tres vías `n = 6`, unión
      `206`) y del intervalo de Wilson; ejecutar y confirmar que fallan.
- [ ] 3.2 **GREEN**: implementar la mínima versión y volver a ejecutar hasta que pase; registrar la
      salida.
- [ ] 3.3 **TRIANGULATE**: agregar casos con exactitud estricta y laxa, subconjunto vacío y el
      conjunto literal `E3` = `E4` = `E5`; ejecutar y confirmar que reproduce `109/142` (`0,7676`,
      IC `[0,6916; 0,8295]`), `33/64` (`0,5156`, IC `[0,3958; 0,6337]`) y `142/206` (`0,6893`, IC
      `[0,6231; 0,7486]`), y que el conjunto literal de tres vías es `0`.
- [ ] 3.4 **REFACTOR**: extraer constantes y funciones puras, sin cambiar comportamiento; ejecutar
      las pruebas después de cada paso y confirmar que siguen en verde.
- [ ] 3.5 Integrar el análisis de subconjuntos en el mismo script y salida; verificar que informa la
      exactitud por subconjunto con IC de Wilson, declara el conjunto literal vacío y no afirma
      causalidad de la referencia.

## 4. Memo canónico (sección 3.29, aditiva)

- [ ] 4.1 Agregar la sección 3.29 a `docs/Tesis/Correcciones/numeros-canonicos.md` con los anclajes,
      las métricas por vocabulario (`V1`, corpus-blind, `V0`) y la exactitud por subconjunto
      (consenso, arbitrado, total); cada valor con archivo fuente y comando.
- [ ] 4.2 Verificar que la sección 3.29 declara el carácter aditivo y que ningún valor de las
      secciones 3.1 a 3.28 cambió de cifra ni de estado; comparar el diff del memo y registrar el
      resultado. Si otro change tomó la numeración `3.29` antes, registrar la desviación y renumerar.

## 5. Tesis: método, resultados, discusión y decisión de corrida paga

- [ ] 5.1 Agregar el párrafo de método en `04-marco-metodologico.tex` (ablación con vocabulario
      externo e independencia procedimental; subconjunto de consenso frente a arbitrado) con remisión
      al capítulo de resultados; verificar que no duplica el marco teórico y que las citas resuelven.
- [ ] 5.2 Agregar la subsección `subsec:sesgo-corpus-referencia` en `07-resultados.tex`, después de
      `subsec:sensibilidad-ajustes`, con la tabla de cobertura/precisión por vocabulario y la tabla de
      exactitud por subconjunto; verificar que las cifras coinciden con la sección 3.29 y que el
      conjunto literal de tres vías se declara vacío.
- [ ] 5.3 Agregar el párrafo de lectura en `08-discusion.tex` que rotula ambos resultados como
      sensibilidad y declara que no eliminan las amenazas del criterio 4; verificar la remisión a
      `subsec:sesgo-corpus-referencia`.
- [ ] 5.4 Verificar el presupuesto de páginas: compilar y confirmar que el crecimiento neto atribuible
      a este change es de a lo sumo dos páginas; registrar el delta preliminar en el libro mayor.
- [ ] 5.5 **[DECISIÓN DEL DUEÑO — OQ1]** Si el dueño autoriza por escrito la corrida paga acotada,
      propagar el vocabulario corpus-blind al híbrido completo con `--confirm-paid` y un caché nuevo,
      sin tocar los congelados, y registrar el resultado como corrida separada; si no la autoriza (por
      defecto), declarar en `08-discusion.tex` la frontera offline (la ablación mide la etapa
      determinística y no el híbrido completo) y cerrar la tarea con esa rama. Verificar en ambos
      casos que la tesis no presenta resultados de una corrida no ejecutada.

## 6. Verificación y cierre

- [ ] 6.1 Ejecutar `python -m pytest evaluation/data/campana/analisis/test_analisis_sesgo_corpus_referencia_c219.py -q`
      y confirmar todo en verde; registrar la salida.
- [ ] 6.2 Compilar con la imagen `texlive-thesis` (`latexmk main.tex`) y verificar `0` errores
      fatales, `0` referencias o citas indefinidas y `0` etiquetas duplicadas; registrar el SHA-256
      del PDF y el total de páginas.
- [ ] 6.3 Ejecutar `python docs/Tesis/Correcciones/verify_citations.py` y `sent_c197.py`; confirmar
      `0` huérfanas y `0` oraciones fuera de límite en los archivos editados; registrar las salidas.
- [ ] 6.4 Agregar la entrada de c-219 y la fila de la matriz de trazabilidad en
      `docs/Tesis/Correcciones/dictamen-correcciones.md`; ejecutar
      `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` y confirmar `0` fallas.
- [ ] 6.5 Revisar el diff completo contra la línea base de 1.2 y confirmar que ningún número canónico,
      corpus, predicción, vocabulario `V1`, configuración ni artefacto congelado cambió; registrar el
      resultado como evidencia de cierre.
