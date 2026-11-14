Al final de cada tarea, entre paréntesis, los requisitos del change que cumple: por código (`OOS-018`,
`OOS-020` a `OOS-024`, `CAL-007`) o, si el requisito no tiene código, por un nombre corto entre
comillas angulares precedido de su capacidad: `TD` (`tesis-document`), `DIC`
(`tesis-dictamen-v1-3-0`), `NC` (`tesis-numeros-canonicos`) y `DEF` (`tesis-defensa`). Nombres
cortos: TD «Propagación» (Propagación del resultado arbitrado a la discusión, las conclusiones y las
recomendaciones), TD «Sistemas», TD «Trabajos futuros», TD «Subsecciones propias», TD «Apartado
metodológico», TD «Resumen», TD «Afirmaciones acotadas», TD «Balance neto», TD «Reproducibilidad»,
TD «Identificadores internos», TD «Marco teórico», TD «Versión entregada», TD «Repetición de cifras»
y TD «Reporte fuera de muestra» (los dos últimos, requisitos vigentes modificados); DIC «Tabla y
arbitraje ejecutado», DIC «Conclusiones»; NC «Registro aditivo»; DEF «Anexo J». Las tareas de
preparación sin requisito propio no llevan paréntesis.

## 0. Preparación y línea de base

- [x] 0.1 Leer `proposal.md`, `design.md` y los seis specs delta del change, `.agents/SKILLS.md` y
      cargar `python-testing-patterns` (y `python-design-patterns` para el script). Registrar qué
      skills se cargaron.
- [x] 0.2 `git fetch` y comparar `origin/main` con la base del change (`ebd2baa`); si `main`
      avanzó y toca `sections/`, `Bibliography_base.bib`, `numeros-canonicos.md` o
      `evaluation/data/campana/`, rebasar antes de seguir y volver a verificar las líneas citadas
      en el design. Si el dictamen (PR 107) ya entró a `main`, citarlo por su ruta versionada.
- [x] 0.3 Capturar la línea de base y guardarla como evidencia de partida: conteo de palabras del
      resumen y del *abstract* con la regla de c-106; `rg -n "c-[0-9]{3}"` sobre
      `docs/Tesis/v10 (IA)/paper/sections/*.tex`; salida de
      `rg -n "0,8447" "docs/Tesis/v10 (IA)/paper/sections" -g "!07-resultados.tex"` (criterio de
      design D6); conteo en prosa de `0,6893`, `0,2222`, «sin el arbitraje» y «41 de los 47» por
      capítulo; total de páginas y estado de compilación (imagen
      Docker `texlive-thesis`, `MSYS_NO_PATHCONV=1`); `python -m pytest` de `evaluation/` desde su
      carpeta con las variables dummy del CI (baseline de pruebas en verde; si algo falla antes de
      empezar, reportarlo como falla preexistente y no corregirlo).
- [x] 0.4 Verificar el estado de las preguntas abiertas OQ1 a OQ6 del design con los autores y
      registrar la respuesta o «pendiente» en `dictamen-correcciones.md`. Las tareas bloqueadas
      (5.1, 8.5, 9.1, 11) no se ejecutan sin respuesta.

- [x] 0.5 Revisar el estado de c-218, c-219 y c-220 (sección «Coordinación» de `proposal.md`):
      (a) fijar el número de la sección nueva del memo como el primero libre en `origin/main` al
      aplicar (en adelante «sección de c-221»): `main` termina hoy en la `3.28` y el PR 110 aplica
      c-218 como `3.29` y c-219 como `3.30`, de modo que será la `3.31` o posterior si el PR 110 y
      c-220 entran antes; (b) si `analisis_sesgo_corpus_referencia_c219.json` está en el árbol,
      usarlo como anclaje de la exactitud por origen de la referencia (`109/142` y `33/64`) y citar
      esa cifra desde la sección de c-219 en lugar de registrarla otra vez; si no está, registrarla
      en la sección de c-221 con la nota de conciliación; (c) si c-220 ya fijó en el memo un costo
      por derivación errónea con procedencia, agregarlo a la rejilla propia de 5, 10 y 15 minutos
      como escenario adicional o central; si no, correr solo con la rejilla, sin esperar a c-220.
      Registrar lo decidido. (NC «Registro aditivo»; OOS-021; OOS-022)

## 1. Script de análisis (TDD estricto)

- [x] 1.1 Fijar en el docstring de
      `evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.py` el método completo
      de D1 a D3 (lecturas; pesos leídos de `sector_asignado` en
      `data/corpus_evaluacion_pseudonimizado.json`, con el vector esperado `Sistemas` 16,
      `Soporte Tecnico Hardware` 85, `Soporte Tecnico Software` 67, `Seguridad Informatica` 31 y
      `Bases de Datos` 1, suma 200, como anclaje; `B = 2000`, semilla `20261021`, descarte de
      réplicas sin alguna clase; candidatos descriptivos de la regla prerregistrada de c-214:
      `0,70` vigente, `0,86`, `0,91`, `0,96`, `0,99` y derivar todo lo escalado; fórmula del
      balance y rejilla de `c`) y los anclajes que abortan; declarar que el análisis es
      posterior y no ciego. Verificar que el docstring contiene esos parámetros antes de escribir
      código. (OOS-020; OOS-022; OOS-024; CAL-007)
- [x] 1.2 **RED** `exactitud_ponderada` e `ic_bootstrap_ponderada`: en
      `test_analisis_propagacion_arbitraje_c221.py`, casos sintéticos con resultado calculado a
      mano (dos clases con sensibilidades distintas y pesos desiguales; clase con peso y sin
      soporte que debe dar error; réplicas sin una clase que se descartan y se cuentan; misma
      semilla, mismo intervalo). Ejecutar
      `python -m pytest evaluation/data/campana/analisis/test_analisis_propagacion_arbitraje_c221.py -q`
      y confirmar que falla porque las funciones no existen. (OOS-020; OOS-024)
- [x] 1.3 **GREEN** implementar lo mínimo para pasar 1.2 reutilizando `metrics.matriz_confusion`,
      `sensibilidad_por_clase`, `remuestreos_indices` y `percentil_intervalo`; ejecutar y
      confirmar verde. (OOS-020; OOS-024)
- [x] 1.4 **RED → GREEN** `desglose`, `metricas_por_clase` y `destinos_de_error`: pruebas con
      grupos de distinto tamaño, un grupo vacío, una clase sin errores y una con errores a dos
      destinos; verificar los intervalos con `metrics.intervalo_wilson`. Ejecutar en rojo, luego
      implementar y ejecutar en verde. (OOS-018; OOS-021; OOS-024)
- [x] 1.5 **RED → GREEN** `calibracion_descriptiva`: pruebas con confianzas sintéticas de
      calibración perfecta, sobreconfianza constante y orden invertido (AUROC menor que `0,5`), y
      una prueba que verifique que la función no devuelve umbral seleccionado; reutilizar
      `calibracion_gate.ece`, `brier`, `auroc`, `sobreconfianza`, `ic_bootstrap_metrica` y
      `barrido_umbral`. (CAL-007; OOS-024)
- [x] 1.6 **RED → GREEN** `balance_neto` y `diferencias_entre_corridas`: el balance con valores
      sintéticos calculados a mano y con signo positivo y negativo; las diferencias con dos listas
      que difieren solo en confianza, solo en sector y en nada. (OOS-022; OOS-023; OOS-024)
- [x] 1.7 **TRIANGULATE**: agregar como pruebas los anclajes reales del design D2 (`142/206`,
      macro-F1 `0,7024`, `87/103`, ponderada `0,8146` sobre los `103`, ECE `0,1715` y Brier
      `0,1935` sobre los `34`, `+6,9` de `tab:balance-neto`, `+25,4`/`+18,7`/`+11,9`), el vector de
      pesos leído del corpus de ajuste (`Sistemas` 16, `Soporte Tecnico Hardware` 85, `Soporte
      Tecnico Software` 67, `Seguridad Informatica` 31, `Bases de Datos` 1), las cardinalidades
      (`64`, `47`, `56`, `6`, `103` dentro de `I001`..`I150`) y, si el artefacto de c-219 está
      presente, la coincidencia por origen con `subconjuntos.consenso` y `subconjuntos.arbitrado`.
      Ejecutar y confirmar verde. (OOS-018; OOS-020; OOS-021; OOS-022; CAL-007)
- [x] 1.8 Implementar la lectura de entradas con SHA-256 (normalización LF como c-213/c-214), la
      verificación de anclajes que aborta sin escribir, el control del `commit` declarado por cada
      archivo de predicciones y la escritura de `analisis_propagacion_arbitraje_c221.json`, `.md` y
      `.SHA256SUMS.txt`. El control usa `git merge-base --is-ancestor <commit> origin/main`:
      código `0`, alcanzable desde `main`; código `1`, no alcanzable; cualquier otro código (por
      ejemplo `128`, objeto ausente del clon), también no alcanzable, con aviso en consola de que
      el objeto no está presente en este clon. Si no es alcanzable, identificar el commit que
      versionó el archivo con `git log --diff-filter=A --format=%h -- <archivo>`. No usar
      `git cat-file -t` como prueba de pertenencia al historial (prueba solo la presencia local del
      objeto y da resultados distintos según el clon). El JSON registra la alcanzabilidad y el
      commit que versionó el archivo, no la presencia local, para que las salidas no dependan del
      clon. Pruebas: una que fuerce un anclaje roto y verifique que no se escribe ningún archivo, y
      una del control con los tres códigos de salida simulados. (OOS-023; OOS-024)
- [x] 1.9 **REFACTOR**: extraer constantes (vector esperado de pesos como anclaje, semilla,
      candidatos de umbral, `N`, `Δt`, `e_man`, rejilla de `c`) y eliminar duplicación; ejecutar
      las pruebas después de cada paso. (OOS-024)
- [x] 1.10 Correr el script dos veces desde la raíz y verificar salidas idénticas byte a byte y
      `git status` sin cambios fuera de `evaluation/data/campana/analisis/`. Comparar las cifras
      con el recomputo exploratorio del design y registrar cualquier diferencia (manda el script).
      (OOS-024)
- [x] 1.11 Agregar la entrada del análisis al README de `evaluation/data/campana/analisis/` y
      registrar en `evaluation/data/campana/README.md` que el `commit` declarado en
      `predicciones_independiente.json` (`561b3c4`) no es alcanzable desde `main`, que puede existir
      como objeto colgante en el clon donde se hizo la corrida pero no viaja con `fetch` ni con
      `clone`, y qué commit versionó el archivo; no afirmar que el commit no existe y no editar el
      JSON. (OOS-023; TD «Reproducibilidad»)

## 2. Memo canónico (sección de c-221, aditiva)

- [x] 2.1 Agregar `### 3.N` (el primer número libre; ver 0.5) a `docs/Tesis/Correcciones/numeros-canonicos.md` con cada cifra del
      JSON de c-221 (lecturas, desgloses, métricas por clase, `Sistemas`, calibración descriptiva,
      balance de sensibilidad, controles de reproducibilidad), cada una con archivo, clave del JSON
      y comando; la exactitud por origen de la referencia, como remisión a la sección de c-219 si
      existe (sin registrar el valor otra vez); declarar el carácter aditivo. (NC «Registro
      aditivo»; OOS-021)
- [x] 2.2 Verificar con un diff dirigido que ningún valor ni estado de las secciones previas del
      memo cambió y registrar el resultado. (NC «Registro aditivo»)

## 3. Resultados: estructura y cifras nuevas (`07-resultados.tex`)

- [ ] 3.1 Crear `subsec:validacion-fuera-muestra` después de `subsec:resultados-campana-medicion`
      y mover allí los párrafos de las líneas 312, 314 y 316 y `tab:fuera-de-muestra`, sin cambiar
      etiquetas. Crear `subsec:comparacion-alternativas` y mover los párrafos de 350, 372, 374 a
      396 con `tab:linea-base-clasica` y `tab:gemini-solo`, sin cambiar cifras. Ambas antes de
      `subsec:ruido-referencia`. (TD «Subsecciones propias»; TD «Reporte fuera de muestra»)
- [ ] 3.2 Reescribir el párrafo del arbitraje (hoy `:316`): sin «change c-206»; cifra primaria y
      lecturas complementarias con su rótulo (D1); aciertos sobre los `47` discordantes, sobre los
      `56` de refuerzo y por etapa desde la sección de c-221; por origen de la referencia desde la
      sección de c-219 (o desde la de c-221 si c-219 no entró); `31/61` de `Sistemas` rotulado como
      sensibilidad. (OOS-018; OOS-020; OOS-021; DIC «Tabla y arbitraje ejecutado»; TD «Sistemas»)
- [ ] 3.3 En `tab:fuera-de-muestra`: quitar «(c-206)» de la fila de discordantes (`:328`) y
      «change c-206» de la nota (`:347`); rotular las filas de peor caso, mejor caso y cota como
      etapa previa; agregar las filas de las lecturas ponderada y de `150` con sus intervalos.
      (OOS-018; OOS-020; DIC «Tabla y arbitraje ejecutado»; TD «Identificadores internos»)
- [ ] 3.4 Agregar `tab:fuera-de-muestra-clases` (matriz `5×5` del corpus arbitrado con precisión,
      sensibilidad, F1 y soporte), con fuente en la nota; verificar contra
      `evaluation/data/campana/reporte_arbitrado.md` y contra la sección de c-221. (OOS-018;
      TD «Subsecciones propias»)
- [ ] 3.5 En `subsec:calibracion` (`:195`-`:221`): fila descriptiva del corpus arbitrado en
      `tab:calibracion-gate` y nota de que el umbral no se eligió con ella; un párrafo con el
      barrido descriptivo sobre los casos Gemini del arbitrado (candidatos `0,70`, `0,86`, `0,91`,
      `0,96`, `0,99` y derivar todo) y la variación de la confianza entre corridas. La fila de `34`
      se conserva. (CAL-007; TD «Reproducibilidad»)
- [ ] 3.6 Actualizar la frase de `07-resultados.tex:6` para enumerar los nueve apartados.
      (TD «Subsecciones propias»)
- [ ] 3.7 Redirigir a `subsec:validacion-fuera-muestra` las remisiones a contenido de la
      validación (`08-discusion.tex:20`, `:28`, `:60`; `10-recomendaciones.tex:26`) y dejar las
      demás; compilar y verificar cero referencias indefinidas y cero etiquetas duplicadas.
      (TD «Subsecciones propias»; TD «Repetición de cifras»)

## 4. Discusión, conclusiones y recomendaciones

- [ ] 4.1 **[CHECKPOINT DE LOS AUTORES — OQ6]** Mostrar la regla de lectura de D1 y el contenido
      mínimo de D6 antes de editar; registrar la conformidad.
- [ ] 4.2 `08-discusion.tex:8`: reemplazar la oración de `0,8447` por la cifra primaria, las
      lecturas complementarias y la lectura del umbral con los tres límites superiores; remitir a
      `subsec:validacion-fuera-muestra`. (TD «Propagación»; TD «Repetición de cifras»)
- [ ] 4.3 `08-discusion.tex:20`: reemplazar el análisis de escenarios por el resultado medido
      (`25` de `47`, lectura de `150`); conservar la limitación del ajuste sobre el mismo corpus.
      (TD «Propagación»)
- [ ] 4.4 `08-discusion.tex:28`: reescribir la lectura de `Sistemas` con el soporte arbitrado, la
      sensibilidad, los destinos de error y la proporción proveniente del refuerzo; retirar
      «dirigido a una única clase adyacente» si los destinos de la sección de c-221 lo contradicen.
      (TD «Sistemas»)
- [ ] 4.5 `08-discusion.tex:60` (séptima limitación): retirar el bloque de cifras repetido y
      remitir a la subsección. (TD «Propagación»; TD «Repetición de cifras»)
- [ ] 4.6 `09-conclusiones.tex:24` (fila del objetivo 2, única aparición de `0,8447` fuera de
      resultados, rotulada como etapa previa), `:37` (sin «change c-206», `Sistemas`
      con `61`, sin la propuesta de sobremuestreo) y `:47` (matiz de viabilidad con `54/91` frente
      a `88/115` por etapa, efecto de selección de la etapa Gemini y remisión a `tab:gemini-solo`).
      (DIC «Conclusiones»; TD «Sistemas»; TD «Afirmaciones acotadas»; TD «Identificadores
      internos»; TD «Repetición de cifras»)
- [ ] 4.7 `10-recomendaciones.tex:18` (taxonomía con los `61` casos y criterio de éxito) y `:26`
      (corpus de composición natural, cuotas prefijadas, arbitraje por mayoría de tres); revisar el
      párrafo introductorio (`:6`) por coherencia. (TD «Trabajos futuros»; TD «Sistemas»)
- [ ] 4.8 Verificar con `rg` en `08`, `09` y `10`: cero «sin el arbitraje», «41 de los 47» y
      `0,2222`; `rg -n "0,8447" "docs/Tesis/v10 (IA)/paper/sections" -g "!07-resultados.tex"`
      devuelve una sola línea, la fila del objetivo 2 en `09-conclusiones.tex`; `0,6893` en prosa a
      lo sumo una vez por capítulo; cada cifra nueva coincide con la sección de c-221 (o con la de
      c-219 para la exactitud por origen). (TD «Propagación»; TD «Repetición de cifras»;
      TD «Sistemas»)

## 5. Metodología del diseño fuera de muestra (`04-marco-metodologico.tex`)

- [ ] 5.1 **[BLOQUEADA HASTA RESPUESTA DE LOS AUTORES — OQ1]** Escribir en
      `subsec:poblacion-muestra-corpus` el párrafo «Corpus independiente de validación» con la
      procedencia y el período que declaren los autores. Sin respuesta, no escribir nada en su
      lugar y dejar la tarea abierta. (TD «Apartado metodológico»)
- [ ] 5.2 En el mismo párrafo (no bloqueado): cuotas y sobremuestreo de
      `runbook-corpus-independiente.md`, composición observada desde la sección de c-221, doble etiquetado ciego,
      refuerzo de `56` casos con su fecha, su ventana de etiquetado y su carácter posterior a los
      datos sin cuota prefijada (`runbook-arbitraje-discordantes.md`, 1.2 y 14), regla de
      arbitraje no mayoritaria, referencias fijadas por `E5` y los `6` casos de tres vías con
      remisión a `subsec:ruido-referencia`. (TD «Apartado metodológico»)
- [ ] 5.3 En `subsec:analisis-estadistico`: una oración por lectura de D1, la calibración
      descriptiva de D3 y la nota de que el orden del prerregistro de la calibración se demuestra
      con las fechas de autor (`git log --format='%h %ai %ci'` de los commits del prerregistro).
      (TD «Apartado metodológico»; TD «Reproducibilidad»)
- [ ] 5.4 En `subsec:amenazas-validez` (`:93`): agregar las amenazas séptima y octava de D5 y
      actualizar el conteo; verificar que el número enunciado coincide con las enumeradas.
      (TD «Apartado metodológico»)

## 6. Resumen, alcance y arquitectura

- [ ] 6.1 `00-resumen.tex` (ES y EN): incorporar la exactitud fuera de muestra (primaria y
      ponderada, sin `0,8447`) y el resultado frente a la línea de base, recortando detalle
      prescindible; contar con la regla de c-106 y verificar ≤ 250 palabras en cada idioma;
      verificar que la lectura del balance coincide con la de la discusión y las conclusiones.
      (TD «Resumen»)
- [ ] 6.2 `01-introduccion.tex:74`: precisar que lo excluido es un modelo supervisado afinado con el
      corpus acumulado en operación y que la línea de base clásica se usa como referencia.
      (TD «Afirmaciones acotadas»)
- [ ] 6.3 `05-arquitectura.tex:68`: conciliar la afirmación de latencia y costo con lo medido en
      `tab:gemini-solo` (razón de llamadas y de costo; latencia solo como cota inferior);
      verificar coherencia con `08-discusion.tex:10`. (TD «Afirmaciones acotadas»)

## 7. Balance neto y reproducibilidad

- [ ] 7.1 En `subsec:balance-neto` (`08-discusion.tex`): agregar el párrafo de sensibilidad con las
      tasas ponderada y cruda de la sección de c-221 y su rótulo; ajustar la síntesis final («con una referencia
      común el balance neto no resulta negativo») para declarar de qué exactitud depende el signo.
      (OOS-022; TD «Balance neto»)
- [ ] 7.2 Verificar que la variación de la confianza entre corridas (3.5) y la nota de fechas de
      autor (5.3) figuran en la tesis, y que el README de campaña registra el `commit` no
      alcanzable desde `main` y el que versionó el archivo (1.11). (TD «Reproducibilidad»;
      OOS-023)

## 8. Marco teórico, glosario, estado del arte, bibliografía y capítulo legal

- [ ] 8.1 `02-marco-teorico.tex`: párrafo breve sobre TF-IDF y regresión logística y otro sobre
      Brier y AUROC, con fuentes primarias ya presentes o nuevas verificadas;
      `00-glosario.tex`: agregar AUROC, Brier y TF-IDF en orden alfabético. (TD «Marco teórico»)
- [ ] 8.2 Leer el texto completo de `MosqueiraRey2023_human_in_the_loop`; si respalda la frase de
      `02-marco-teorico.tex:32`, agregar la ubicación; si no, atenuarla a lo que el artículo hace.
      Registrar la evidencia. (TD «Marco teórico»)
- [ ] 8.3 `03-estado-del-arte.tex` (`:34` y la fila `:51`): salvedad de que Colavito y
      colaboradores clasifican incidencias de GitHub; verificar en el texto completo las cifras
      atribuidas a Paramesh y a Colavito y declarar la fuente efectiva si solo constan en el
      resumen. (TD «Marco teórico»)
- [ ] 8.4 Bibliografía: verificar el año de la edición citada de `Date2003_database`,
      `Hohpe2003_eip`, `Stallings2017_computer_security`, `Efron1993_bootstrap` y
      `Jurafsky2023_speech_language`; alinear el campo y renombrar la clave (8 usos en
      `sections/`); comprobar la URL de `ServiceNow2026_itsm` y reemplazarla por una fuente
      oficial accesible si no responde; ejecutar `verify_citations.py`. (TD «Marco teórico»)
- [ ] 8.5 **[BLOQUEADA — OQ4; gobernanza HIGH]** Verificar la Resolución AAIP 198/2023 en el
      Boletín Oficial o en Infoleg (número, fecha, organismo, objeto). Solo si se verifica y los
      autores aprueban el diff, agregar la entrada bibliográfica y una oración en
      `11-aspectos-legales.tex` junto a la Disposición 60-E/2016. Si no, no citarla y registrar el
      motivo. (TD «Marco teórico»)

## 9. Forma: Anexo J, identificadores, cronograma y versión

- [ ] 9.1 **[BLOQUEADA — OQ3]** Según la decisión de los autores registrada en
      `dictamen-correcciones.md`: retirar de `12-anexos.tex` la sección
      `sec:anexo-respuestas-tribunal` (recomendado; la fuente sigue en
      `docs/defensa/respuestas-tribunal.md`), o conservarla y actualizar sus cifras al arbitraje en
      el anexo y en el documento fuente por igual. Verificar el escenario de `tesis-defensa` que
      corresponde a la rama elegida; el delta cubre las dos y no se descarta. (DEF «Anexo J»)
- [ ] 9.2 Retirar los identificadores internos (`07-resultados.tex`, `09-conclusiones.tex:37`,
      `12-anexos.tex:151` y los que haya agregado el rebase) y verificar que
      `rg -n "c-[0-9]{3}"` sobre `sections/*.tex` solo devuelve comentarios. (TD «Identificadores
      internos»)
- [ ] 9.3 Actualizar `docs/diagrams/cronograma.md` con los hitos del 12 y 13-11-2026 y su
      evidencia (marcas de `doble_etiquetado_arbitrado.csv`, fechas de autor de los commits),
      regenerar `paper/figures/cronograma.png` con el comando documentado y revisar la leyenda de
      `fig:cronograma` en `12-anexos.tex`. (TD «Versión entregada»)
- [ ] 9.4 Preparar, sin crear el tag, los textos de la versión nueva: Anexo B (`12-anexos.tex:58`)
      con la afirmación verificable de D9 en lugar de «los commits posteriores no modifican las
      fuentes de la tesis»; portada (`00-portada.tex:30-31`) y `Gomez2026_repositorio` con la
      versión y la fecha de OQ2 (placeholder explícito mientras OQ2 siga pendiente).
      (TD «Versión entregada»)

## 10. Compilación y verificación de cierre

- [ ] 10.1 Compilar con Docker `texlive-thesis` (`latexmk main.tex`): cero errores fatales,
      referencias o citas indefinidas y etiquetas duplicadas; revisar visualmente los anexos por
      paginación; regenerar `paper/compilacion.md` con `resumir_registro_compilacion.py` y copiar
      el PDF a `docs/Tesis/tesis_ultima_version.pdf`. (TD «Subsecciones propias»; TD «Versión
      entregada»)
- [ ] 10.2 Ejecutar `python -m pytest` de `evaluation/` (con las variables dummy del CI y desde su
      carpeta), `python "docs/Tesis/v10 (IA)/verify_citations.py"` y
      `python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` después de agregar las
      filas `C18/…` (archivo, línea, etiqueta y frase ancla por cada pasaje editado); todos en
      verde. (OOS-024; TD «Marco teórico»)
- [ ] 10.3 Repetir los conteos de 0.3 y registrar el antes y el después (palabras del resumen,
      identificadores, salida del `rg` de `0,8447`, repeticiones, cadenas retiradas).
      (TD «Propagación»; TD «Repetición de cifras»; TD «Resumen»; TD «Identificadores internos»)
- [ ] 10.4 Agregar la fila `+c-221` al libro mayor de páginas de `dictamen-correcciones.md` con el
      delta y su causa (presupuesto de D13) y la sección de trazabilidad del change con el estado
      de cada una de las 17 recomendaciones y de las observaciones por sección.
- [ ] 10.5 Revisar el diff completo con el patrón del falso positivo de gitleaks (palabra que
      contiene «api», «key», «token», «auth» o «secret» seguida a menos de 20 caracteres de coma,
      dos puntos o igual y de una cadena de 10 o más caracteres sin espacios) y reescribir los
      casos; si hay Docker, correr gitleaks con `.gitleaks.toml` sobre el árbol de trabajo.
- [ ] 10.6 Confirmar que ningún corpus, predicción, configuración ni artefacto congelado cambió
      (`git diff --stat` contra la base) y agregar la fase del change en `CHANGES.md`. (OOS-024)

## 11. Release (requiere confirmación de los autores)

- [ ] 11.1 **[BLOQUEADA — OQ2]** Completar versión y fecha en portada, Anexo B y
      `Gomez2026_repositorio`; recompilar. (TD «Versión entregada»)
- [ ] 11.2 Commit C1 de contenido en una rama nueva (no `main`), con fuentes, PDF y
      `compilacion.md`; verificar con `git show C1:` que contiene los artefactos de evidencia que la
      tesis cita (lista de D9). (TD «Versión entregada»)
- [ ] 11.3 **[CONFIRMACIÓN EXPRESA DE LOS AUTORES — OQ5]** Crear el tag anotado sobre C1; luego el
      commit C2 que solo consigna el hash completo en el Anexo B y regenera el PDF; verificar
      `git rev-parse <tag>^{commit}` igual al hash del Anexo B y que
      `git diff <tag> C2 -- "docs/Tesis/v10 (IA)/paper/sections"` solo toca esa línea.
      (TD «Versión entregada»)
- [ ] 11.4 **[CONFIRMACIÓN EXPRESA DE LOS AUTORES — OQ5]** Push de la rama y del tag y apertura del
      PR (la sincronización de la memoria la hacen los autores); esperar que todos los checks del
      CI pasen y, si alguno falla, diagnosticar y corregir antes de cerrar. (TD «Versión entregada»)
