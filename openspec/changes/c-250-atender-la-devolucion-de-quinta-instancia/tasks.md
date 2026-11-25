# Tasks: Atender la devolucion de quinta instancia

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`Q/` = `auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md` (el PDF homonimo es la
evidencia); `E/` = `evaluation/data/campana/analisis/`. Lineas de `v1.6.4` (verificadas en el
propose); el apply las re-verifica con `rg` antes de editar. Mapa de capitulos: cap. 7 =
`S/11-aspectos-legales.tex`, cap. 8 = `S/07-resultados.tex`, cap. 9 = `S/08-discusion.tex`, cap. 10
= `S/09-conclusiones.tex` (design, Context). Equivalente de Strict TDD para prosa: cada tarea de
edicion corre una verificacion ANTES (muestra el defecto) y DESPUES (estado deseado), registradas
en `C/dictamen-correcciones.md` seccion `c-250`. Reglas: no commitear, taggear ni pushear sin
pedido expreso; no cambiar cifras canonicas vigentes; ninguna cifra nueva se copia del tribunal:
sale de `E/analisis_quinta_instancia_c250.json`; espanol rioplatense formal sin emojis; solo alias
(`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); no tocar `App/`, `n8n/`, artefactos existentes de
`evaluation/`, el JSON del corpus ni la hoja pseudonimizada; en prosa nunca "capitulo" + coma +
nombre de archivo (gitleaks). Marcas: **[GATED OQ-0n]** = bloqueada hasta que la respuesta figure
en la tabla de compuertas de c-250. Dominio HIGH (`S/11-aspectos-legales.tex`, `docs/seguridad/`,
`data/README.md`, grupo 12): texto propuesto mostrado a los autores antes de escribir. Gobernanza
del change: MEDIUM.

## 1. Guardas y linea base

- [ ] 1.1 Leer `proposal.md`, `design.md` (D1-D11, OQ-01 a OQ-07, G-DIR), los tres deltas de
  `specs/` y `Q/` completo. Verificacion: `git diff --stat v1.6.4 HEAD -- "docs/Tesis/v10 (IA)" data`
  vacio (las lineas del design siguen vigentes) o lista de desplazamientos registrada.
- [ ] 1.2 Linea base de cifras y conteos. Verificacion: `rg -c "61,6|17,76|71,2|73,5|W = 363|0,6508|87,2|20,09|77,0" S/`
  y conteo de prosa del Resumen (234) y del Abstract (232) con la regla de `tesis-document`
  ("English abstract"), registrados en la seccion c-250.
- [ ] 1.3 Valores inmutables: `git rev-parse v1.6.4^{commit}` (`f05ef2d...`), `git rev-parse v1.6.3^{commit}`,
  `sha256sum data/corpus_evaluacion_pseudonimizado.json` (`1fd17d7e...`) y SHA-256 del blob de
  `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv`. Verificacion: registrados como valores que el
  apply MUST NOT cambiar.
- [ ] 1.4 Red de seguridad: `python "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS; `pytest E/`
  desde `evaluation/` con las seis variables dummy del CI (conteo registrado; el fallo preexistente
  de `test_analisis_sesgo_corpus_referencia_c219.py` se declara, no se corrige);
  `openspec validate --all --strict` sin fallos.
- [ ] 1.5 Transcripcion: `Q/` existe, LF, UTF-8 sin BOM, encabezado de transcripcion con el PDF como
  evidencia (formato de `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`).
  Verificacion: `file Q/` sin BOM ni CRLF; `rg -c "C-0[1-7]" Q/` >= 7; las 10 preguntas presentes.

## 2. Compuertas de autores y director

- [ ] 2.1 **[COMPUERTA OQ-01]** Presentar a los autores la evidencia E1-E5 del design y las cuatro
  preguntas de OQ-01 (origen de los 165,3 s del borrador; evidencia fechada de junio-agosto, con la
  pista del historial de la hoja y de los metadatos del `.xlsx`; existencia de los originales; "en
  su domicilio") con las ramas (a)/(b) de D3. Registrar respuesta literal, fecha y responsable.
  Verificacion: la fila existe; sin ella, 4.1 a 4.4 quedan bloqueadas.
- [ ] 2.2 **[COMPUERTA OQ-02]** Presentar a los autores (con consulta a `A1`) las cinco preguntas de
  OQ-02 y los datos del design (4 casos de 10 s; `R017`; 199/200 multiplos de 5) con las ramas
  (a)/(b)/(c) de D4. Verificacion: la fila existe; sin ella, 5.2 a 5.4 quedan bloqueadas en lo que
  depende del valor.
- [ ] 2.3 **[COMPUERTA OQ-03]** (HIGH) Presentar las cuatro preguntas de OQ-03 (notificacion del
  01/10; consentimiento del circulo; custodia y destruccion de originales; texto de licitud por
  disociacion). Verificacion: la fila existe; sin ella, 8.1 a 8.3 quedan bloqueadas.
- [ ] 2.4 **[COMPUERTA OQ-04]** (HIGH) Presentar a autores y director las tres preguntas de OQ-04
  (informacion a empleadores; aval escrito del director; texto con el art. 10). Verificacion: la
  fila existe con ambos responsables; sin ella, 8.4 queda bloqueada.
- [ ] 2.5 **[COMPUERTA OQ-05]** Preguntar si se uso un asistente de IA para reescribir las 119
  descripciones del regimen (a). Verificacion: la fila existe; sin ella, 9.1 se aplica solo con el
  hecho del 2026-09-16 y la parte de la reescritura queda bloqueada.
- [ ] 2.6 **[COMPUERTA OQ-06]** Con `E/analisis_quinta_instancia_c250.md` a la vista (tarea 3.4),
  presentar las opciones D6 (a)/(b)/(c) para el rotulo de la sub-hipotesis 1 y la oracion del
  Resumen y el Abstract. Verificacion: la fila existe; sin ella, 6.3 y el rotulo de 5.4 quedan
  bloqueados.
- [ ] 2.7 **[COMPUERTA OQ-07]** Presentar a autores y director la version (`v1.6.5`, D10), la
  decision de paginas (se completa con el total medido en 12.3) y el OK para commits, tag y merge.
  Verificacion: la fila existe con ambos responsables; sin ella, el grupo 12 queda bloqueado.
- [ ] 2.8 **[COMPUERTA G-DIR]** Registrar el visto bueno escrito del director sobre la version de
  defensa (fecha, medio, version), sin versionar el documento si contiene datos personales.
  Verificacion: la fila existe; sin ella, 12.8 (entrega al tribunal) queda bloqueada.

## 3. Recomputo por pares (C-02, C-03, C-04; Strict TDD)

- [ ] 3.1 RED: escribir `E/test_analisis_quinta_instancia_c250.py` (patron de
  `E/test_analisis_rango_robustez_tiempos_c226.py`) con datos sinteticos minimos para
  `reduccion_pareada` (descuento 0 y d; conteo de lecturas `<= 0` sin truncar),
  `ic_bootstrap_pares` (semilla `20261021`, `B = 2000`, determinismo), `wilcoxon_pares`,
  `escenarios` (200 / 119 sin telefonia / 81 telefonicos x descuentos), `grabaciones_frente_a_lectura`
  (media, mediana, maximo, conteo en el tope de 45 s, diferencia y cociente por par) y
  `registro_primario` (presentes y faltantes). Verificacion: `pytest E/test_analisis_quinta_instancia_c250.py`
  falla porque el modulo no existe.
- [ ] 3.2 GREEN: implementar `E/analisis_quinta_instancia_c250.py` con el minimo para pasar,
  reutilizando `ic_reduccion_tiempo` de `E/analisis_dictamen_c207.py` si su importacion no arrastra
  `app.*` (si la arrastra, replicar con la misma semilla y documentarlo en el docstring).
  Verificacion: la prueba pasa.
- [ ] 3.3 TRIANGULATE: segundo caso por comportamiento (p. ej. descuento mayor que un tiempo manual;
  canal sin casos; telefonia con duracion en el tope; `case_id` ausente; escritura determinista byte
  a byte). Verificacion: `pytest` en verde con >= 2 casos por funcion y sin asserts triviales.
- [ ] 3.4 Ejecutar sobre `data/corpus_evaluacion_pseudonimizado.json`,
  `data/corpus_resultados_telefonia.json` y `data/corpus_resultados_web_correo.json`, con descuentos
  0, 5 y 10 s (y el `k` de OQ-02 cuando exista; regenerar entonces). Escribir
  `E/analisis_quinta_instancia_c250.{json,md,SHA256SUMS.txt}`. Verificacion: las anclas reproducen
  71,16 %, 68,61 %, 65,57 %, IC `[0,6716; 0,7459]`, 87,25 / 20,09 / 77,0 %, 61,585 y 17,76, y 118/119
  con `R001` ausente; si no, el script aborta sin escribir. Toda diferencia con las cifras
  aproximadas del tribunal (51,6 s, 65,6 %, 44,1 s, 16,2 s, 63,3 %, "unos 77 s", 18,7 s) se consigna
  en la seccion c-250 sin corregir al tribunal en la tesis.
- [ ] 3.5 REFACTOR y registro: nombres y constantes; `pytest E/` completo en verde (conteo de 1.4
  mas los nuevos); seccion aditiva `3.49` en `C/numeros-canonicos.md` con procedencia por valor,
  SHA-256 de las salidas (blob de git) y estado (`vigente (nuevo)`; los escenarios de `k` sin valor
  declarado, `condicional`). Verificacion: suite en verde; `rg -n "^### 3.49" C/numeros-canonicos.md`
  = 1 y ninguna seccion previa cambia de cifra ni de estado.

## 4. C-01 - Cronologia de la campana manual (alta; gated OQ-01)

- [ ] 4.1 **[GATED OQ-01]** Anexo I.1 (`S/12-anexos.tex:241`): explicar que los 165,3 s del 3 de
  julio fueron el parametro de media de un generador sintetico (`41430a21`) que reproducia una cifra
  del borrador de junio (`2e15de9b`), con el origen de esa cifra segun OQ-01 (1), y por que no hubo
  dos mediciones en el mismo periodo. Verificacion ANTES: `rg -n "165,3" S/12-anexos.tex` devuelve
  `:241` sin mencion del generador; DESPUES: la oracion nombra el generador y coincide con OQ-01 (1).
- [ ] 4.2 **[GATED OQ-01]** §4.2 (`S/04-marco-metodologico.tex:16`), §4.4 (`:46`), Tabla 4 (`:78`,
  columna de fecha "jun--ago 2026") y §4.8 (primera amenaza, `:117`) segun D3: rama (a) cita la
  evidencia fechada con su alcance; rama (b) declara la fecha como declaracion de los autores no
  verificable y la primera amenaza agrega el rastro fechado mas temprano (2026-09-16, E3).
  Verificacion ANTES: `rg -n "jun--ago|junio y agosto" S/04-marco-metodologico.tex` lista `:46`,
  `:78` y las demas; DESPUES: cada coincidencia lleva la evidencia (a) o la clausula de no
  verificabilidad (b), y `rg -n "no verificable|verificable" S/04-marco-metodologico.tex` >= 4 en
  la rama (b).
- [ ] 4.3 **[GATED OQ-01]** `S/04-marco-metodologico.tex:97` y `:117`: "no se conserva en su forma
  original" pasa a la situacion real de los originales (OQ-01 (3); coordinar con 8.3 la custodia).
  Verificacion ANTES: `rg -n "no se conserva en su forma original" S/` devuelve `04:97`; DESPUES:
  0 coincidencias o texto coincidente con OQ-01 (3).
- [ ] 4.4 **[GATED OQ-01]** Cronograma: `docs/diagrams/cronograma.md` (`:39`, `:74`) y leyenda de
  `fig:cronograma` (`S/12-anexos.tex:16-53`) con la fuente de la barra "Campana manual" segun la
  rama; regenerar `cronograma.png` solo si cambia el bloque Mermaid. Verificacion ANTES:
  `rg -n "Campa.a manual" docs/diagrams/cronograma.md`; DESPUES: la fuente declara evidencia o
  declaracion no verificable, coherente con 4.2.

## 5. C-02 - Componente estimado del tiempo manual (alta)

- [ ] 5.1 Tabla 3 (`S/04-marco-metodologico.tex:31`): definicion operacional por brazo segun D4
  (manual: lectura cronometrada por el par, redondeo a 5 s, mas componente de carga estimado, sin
  ticket cargado ni persistido; automatizado: correo y formulario hasta la persistencia confirmada;
  telefonia: grabacion mas latencia posterior al cuelgue). Sin compuerta en la estructura; el valor
  del componente se escribe en 5.2. Verificacion ANTES: `rg -n "persistencia confirmada" S/04-marco-metodologico.tex`
  devuelve una definicion unica para ambos brazos en `:31`; DESPUES: dos definiciones rotuladas por
  brazo y la manual no menciona persistencia.
- [ ] 5.2 **[GATED OQ-02]** Valor del componente en `S/04-marco-metodologico.tex:89` (p. 45) y en la
  octava amenaza (`:131`), segun la rama (a)/(b)/(c) de D4, con la explicacion del minimo de 10 s.
  Verificacion ANTES: `rg -n "tiempo fijo de carga|del orden de 10" S/04-marco-metodologico.tex`
  devuelve `:89` y `:131`; DESPUES: el valor o la declaracion de desconocido coincide con OQ-02 y
  "fijo" figura solo si la rama lo sostiene con la tension declarada.
- [ ] 5.3 **[GATED OQ-02]** `S/01-introduccion.tex:18` (§1.2): "midio el tiempo de registro incidente
  por incidente con cronometraje en vivo" pasa a "cronometro la lectura ... mas un componente de
  carga estimado". Verificacion ANTES: `rg -n "incidente por incidente con cronometraje en vivo" S/01-introduccion.tex`
  devuelve `:18`; DESPUES: 0 y la oracion nombra el componente estimado.
- [ ] 5.4 **[GATED OQ-02; rotulo gated OQ-06]** Mencion del componente estimado en
  `S/00-resumen.tex:13` y `:29` (reemplazar, no agregar; <= 250 palabras de prosa), §8.1
  (`S/07-resultados.tex:36-62`), Tabla 10 (`:15-30`, nota o celda) y Tabla 23
  (`S/09-conclusiones.tex:15-30`, fila de la sub-hipotesis de tiempo), con remision al Anexo K.
  Verificacion ANTES: `rg -n "estimad" S/00-resumen.tex` = 0 y `rg -c "estimad" S/07-resultados.tex S/09-conclusiones.tex`
  registrado; DESPUES: >= 1 en Resumen, Abstract, §8.1, Tabla 10 y Tabla 23; conteo de prosa <= 250
  por bloque, registrado.
- [ ] 5.5 Anexo K (`S/12-anexos.tex:349-370`, `tab:rango-robustez-tiempos`): filas de la reduccion
  sin el componente recomputadas por pares, con IC y Wilcoxon, para 5 y 10 s (y `k` si existe), para
  los 200 pares y para los 119 sin telefonia, tomadas de `E/analisis_quinta_instancia_c250.json`; la
  nota declara que los descuentos son sensibilidad salvo que OQ-02 de `k`. Verificacion ANTES:
  `rg -n "IC" S/12-anexos.tex` dentro de `tab:rango-robustez-tiempos` sin IC por pares; DESPUES: cada
  fila nueva coincide con el JSON (cotejo registrado).

## 6. C-03 - Entradas distintas en telefonia (alta)

- [ ] 6.1 Sexta amenaza (`S/04-marco-metodologico.tex:127`): asimetria de entradas (lectura completa
  en voz alta frente a parafrasis recitada; grabacion acotada a 45 s) con la duracion media y
  mediana de las 81 grabaciones frente a la lectura manual por par, del JSON. Verificacion ANTES:
  `rg -n "par.frasis" S/04-marco-metodologico.tex` y `rg -n "duraci.n media de las 81" S/` = 0;
  DESPUES: la amenaza nombra la asimetria y las cifras del JSON.
- [ ] 6.2 §8.1 (`S/07-resultados.tex`, tras `tab:tiempos-canal`, `:65-78`) y nota de la Tabla 12:
  sub-hipotesis 1 sobre los 119 pares sin telefonia (medias, reduccion, IC, Wilcoxon) y la fila
  telefonica rotulada como contraste de entradas no equivalentes; duracion de las grabaciones frente
  a la lectura manual. Verificacion ANTES: `rg -n "sin telefon|119 pares" S/07-resultados.tex` = 0;
  DESPUES: >= 1 con las cifras del JSON.
- [ ] 6.3 **[GATED OQ-06]** Rotulo de la sub-hipotesis 1 en Tabla 10 (`S/07-resultados.tex:15-30`),
  Tabla 23 (`S/09-conclusiones.tex:15-30`), `S/09-conclusiones.tex:6`, `S/08-discusion.tex:8` y
  Resumen/Abstract segun D6. Verificacion ANTES: `rg -n "confirmad" S/07-resultados.tex S/08-discusion.tex S/09-conclusiones.tex S/00-resumen.tex`;
  DESPUES: rotulo unico coincidente con OQ-06.
- [ ] 6.4 Discusion: `S/08-discusion.tex:22` (asimetria del instrumento) incorpora la asimetria de
  entradas en telefonia con remision a la sexta amenaza. Verificacion ANTES: `rg -n "par.frasis|entradas" S/08-discusion.tex`;
  DESPUES: >= 1 y sin cifras distintas del JSON.

## 7. C-04 - Estado del registro primario (media; sin compuerta)

- [ ] 7.1 Una sola formula en `S/04-marco-metodologico.tex:66`, `:79` (Tabla 4) y
  `S/07-resultados.tex:38` segun D7, con el conteo de `registro_primario` del JSON. Verificacion
  ANTES: `rg -n "118 de 119|sin registro primario conservado" S/` devuelve `04:66`, `04:79`, `07:38`
  en contradiccion; DESPUES: las tres dicen lo mismo y `rg -n "sin registro primario conservado" S/` = 0.

## 8. C-05 y C-06 - Capitulo legal (media; HIGH; gated)

- [ ] 8.1 **[GATED OQ-03]** (HIGH) `S/11-aspectos-legales.tex:46` y `:32`: separar el consentimiento
  de los colaboradores (autores y `A1`) del de los titulares; retirar "titulares de los datos y los
  responsables del tratamiento son las mismas personas" y la frase que presenta el consentimiento
  del 02/10 como refutacion de lo dicho en v1.6.0 sobre los titulares; declarar el consentimiento
  del circulo segun OQ-03 (2). Verificacion ANTES: `rg -n "mismas personas|v1.6.0 afirm" S/11-aspectos-legales.tex`
  devuelve `:46`, `:32`; DESPUES: 0 y el texto coincide con OQ-03.
- [ ] 8.2 **[GATED OQ-03]** (HIGH) `S/11-aspectos-legales.tex:16` y `:32`: licitud fundada en la
  disociacion (arts. 2 y 28, Ley 25.326) con el texto aprobado; "notificacion a los integrantes del
  grupo" definida segun OQ-03 (1). Verificacion ANTES: `rg -n "art.culo~28|disociaci" S/11-aspectos-legales.tex`
  sin art. 28 y `rg -n "notificaci.n a los integrantes" S/11-aspectos-legales.tex` sin definicion;
  DESPUES: art. 2 y art. 28 citados y la notificacion definida.
- [ ] 8.3 **[GATED OQ-03]** (HIGH) Custodia y destruccion de los originales con identificadores en
  §7.2 o §7.5 (`S/11-aspectos-legales.tex:18` o `:52`), `data/README.md:55` y
  `docs/seguridad/registro-actividades-tratamiento.md`; anexo de revision fechado en
  `docs/seguridad/acta-consentimiento-t2.md` (sin reescribir el cuerpo firmado) si la notificacion o
  el vocabulario cambian. Verificacion ANTES: `rg -n -i "destru" S/11-aspectos-legales.tex data/README.md docs/seguridad/registro-actividades-tratamiento.md`
  = 0; DESPUES: quien guarda, donde y cuando se destruyen, coincidente con OQ-03 (3) y con 4.3.
- [ ] 8.4 **[GATED OQ-04]** (HIGH) `S/11-aspectos-legales.tex:18`: "no se requirio autorizacion de
  esas organizaciones" con el aval escrito del director o la declaracion de si los empleadores
  fueron informados, y el deber de confidencialidad (art. 10). Verificacion ANTES:
  `rg -n "no se requiri. autorizaci" S/11-aspectos-legales.tex` devuelve `:18` sin aval ni art. 10;
  DESPUES: aval o declaracion y `rg -n "art.culo~10" S/11-aspectos-legales.tex` >= 1.
- [ ] 8.5 Propagacion: `docs/defensa/respuestas-tribunal.md` y
  `C/respuestas-tribunal-cuarta-instancia.md` sin las frases retiradas en 8.1. Verificacion:
  `rg -n "mismas personas" docs/defensa C/respuestas-tribunal-cuarta-instancia.md` = 0 o con nota de
  superacion fechada.

## 9. C-07 - Coherencia y redaccion (baja)

- [ ] 9.1 **[GATED OQ-05 en la reescritura]** Tabla 26 (`S/12-anexos.tex:261-275`): fila "Corpus
  (descripciones del regimen (a))" con la correccion de 40 erratas y espacios por una sesion de
  agente el 2026-09-16 y, segun OQ-05, el uso o no de IA en la reescritura;
  `C/inventario-uso-asistentes-ia.md` alineado. Verificacion ANTES: `rg -n "Corpus" S/12-anexos.tex`
  sin fila en la tabla; DESPUES: la fila existe y coincide con OQ-05.
- [ ] 9.2 I.3 (`S/12-anexos.tex:279`): el etiquetado lo hicieron `A1`, `T1`, `E1` y `E2` y el
  cronometraje `A1` y `T1`. Verificacion ANTES: `rg -n "etiquetado de los datos--- y las decisiones de contenido son de los autores" S/12-anexos.tex`;
  DESPUES: 0 y los alias nombrados.
- [ ] 9.3 Autoria unificada: `S/12-anexos.tex:241` "redactadas por los autores" pasa a "por un
  autor", coherente con `S/04-marco-metodologico.tex:46`. Verificacion ANTES:
  `rg -n "redactadas por los autores" S/` devuelve `12:241`; DESPUES: 0.
- [ ] 9.4 §7.5 (`S/11-aspectos-legales.tex:54`): mencionar Gemini 3.1 para la validacion retirada,
  como en `S/12-anexos.tex:243`. Verificacion ANTES: `rg -n "Gemini 3.1|gemini-3.1" S/11-aspectos-legales.tex` = 0;
  DESPUES: >= 1.
- [ ] 9.5 Frase repetida: "dispositivo de dimensionamiento y no el lugar de recoleccion" queda solo
  en `S/04-marco-metodologico.tex:46`; `01:16`, `01:62`, `01:72`, `01:76`, `08:22`, `08:50`, `09:52`
  se reformulan o remiten; `S/09-conclusiones.tex:48` sin "corpus propio de la organizacion".
  Verificacion ANTES: `rg -c "dispositivo de dimensionamiento y no el lugar" S/` suma 8 y
  `rg -n "corpus propio de la organizaci" S/` devuelve `09:48`; DESPUES: 1 y 0.
- [ ] 9.6 **[GATED OQ-01 (4)]** "En su domicilio" (`S/04-marco-metodologico.tex:46`) aclarado (de
  quien). Verificacion ANTES: `rg -n "en su domicilio" S/`; DESPUES: el sujeto del domicilio es
  explicito y coincide con OQ-01 (4).

## 10. Respuestas escritas a las diez preguntas

- [ ] 10.1 Crear `C/respuestas-tribunal-quinta-instancia.md` (formato de
  `C/respuestas-tribunal-cuarta-instancia.md`: encabezado con fuentes y estado "borrador para
  revision de los autores y del director"; una seccion por pregunta con el texto literal de `Q/`).
  Respuestas 1-2 (OQ-01, con E1-E3), 3 (OQ-02), 4-5 (JSON del grupo 3), 6 (OQ-05), 7 y 9 (OQ-03),
  8 (OQ-04) y 10 (cifras canonicas existentes: `subsec:sensibilidad-ajustes`, brazo Gemini solo de
  c-215, reparto por etapa de `tab:exactitud-etapa-canal`; sin computo nuevo). Cada respuesta gated
  se escribe solo con su respuesta registrada; mientras tanto queda "pendiente de OQ-0n".
  Verificacion: 10 secciones; ninguna afirma un hecho no registrado.
- [ ] 10.2 Cotejo de cifras: `python3 -I C/cotejar_cifras_respuestas.py --respuestas C/respuestas-tribunal-quinta-instancia.md --ejemplar "docs/Tesis/v10 (IA)/tesis_completa_extraida.txt" --lista-blanca docs/defensa/cotejo-lista-blanca.tsv`
  sobre el texto extraido regenerado en 12.4 (cifras del tribunal citadas como tales, en la lista
  blanca con su justificacion). Verificacion: codigo de salida 0.
- [ ] 10.3 `docs/defensa/respuestas-tribunal.md`: remision a las respuestas de quinta instancia.
  Verificacion: `rg -n "quinta" docs/defensa/respuestas-tribunal.md` >= 1.

## 11. Coherencia

- [ ] 11.1 Cifras canonicas vigentes intactas: repetir el conteo de 1.2. Verificacion: mismos
  valores; el diff solo agrega cifras del JSON de 3.4 o re-rotula.
- [ ] 11.2 Sin nombres reales ni correspondencia alias-identidad en la prosa nueva. Verificacion:
  revision del `git diff` de `S/`, `docs/seguridad/`, `data/README.md`, `C/`, `docs/defensa/`.
- [ ] 11.3 Barrido de residuos: `rg -n "incidente por incidente con cronometraje en vivo|sin registro primario conservado|mismas personas|redactadas por los autores|corpus propio de la organizaci|no se conserva en su forma original" S/`
  = 0 (salvo lo que una respuesta OQ conserve expresamente, registrado) y
  `rg -c "dispositivo de dimensionamiento y no el lugar" S/` = 1.
- [ ] 11.4 Resumen y Abstract <= 250 palabras de prosa; hash del corpus y tags iguales a 1.3;
  `verify_citations.py` PASS; `pytest E/` en verde;
  `openspec validate c-250-atender-la-devolucion-de-quinta-instancia --strict` y
  `openspec validate --all --strict` sin fallos.

## 12. Release v1.6.5 de defensa (HIGH; gated OQ-07; OK expreso antes de cada commit y del tag)

- [ ] 12.1 Precondicion: tareas gated de 4, 5, 6, 8 y 9 aplicadas o expresamente diferidas por los
  autores (C-05 a C-07 pueden exponerse en la defensa; C-01 a C-04 no), con el diferimiento
  registrado. Verificacion: lista de tareas abiertas vacia o con diferimiento registrado; ninguna de
  C-01 a C-04 diferida.
- [ ] 12.2 Nota de versiones I.1 (`S/12-anexos.tex:239-245`): entrada de la quinta instancia
  (componente estimado declarado y propagado, reduccion sin el componente y sin telefonia, cronologia
  segun la rama de OQ-01, capitulo legal). Bump a `v1.6.5` (o la version de OQ-07) y fecha en
  `S/00-portada.tex`, Anexo B (`sec:anexo-repositorio`), `Bibliography_base.bib`
  (`Gomez2026_repositorio`), `README.md`, `knowledge-base/` y `C/inventario-uso-asistentes-ia.md`;
  cifra del Anexo I.3 recomputada con `git rev-list --count` sobre la ref que el texto describe.
  Verificacion: `rg -n "1\.6\.4"` sobre esos archivos solo en registros historicos; la entrada de
  I.1 existe.
- [ ] 12.3 Recompilar: `export MSYS_NO_PATHCONV=1; docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
  (en segundo plano). Verificacion: `grep -c "^!" main.log` = 0; 0 `undefined` de referencias y
  citas; 0 `multiply defined`; biber sin advertencias; filas de tabla con `\\` (no `\`); total de
  paginas (`abspage@last` en `main.aux` o `pdfinfo`) registrado en el libro mayor de paginas de
  `C/dictamen-correcciones.md` con la decision de OQ-07 (2) (requisito "Presupuesto de paginas
  preservado").
- [ ] 12.4 Derivados: `C/resumir_registro_compilacion.py --fuente` (hash del commit compilado) para
  `docs/Tesis/v10 (IA)/paper/compilacion.md`; `build_tesis_para_agente.py`,
  `tesis_para_evaluacion.txt`, `tesis_completa_extraida.txt` y copia de entrega
  `docs/Tesis/tesis_ultima_version.pdf`. Verificacion: SHA-256 de la copia igual al de `main.pdf`;
  `tesis_para_agente.md` contiene el componente estimado en el Resumen.
- [ ] 12.5 Commits y tag segun la regla A (c-249 OQ-05): C3 de contenido y PDF, tag anotado
  `v1.6.5` sobre C3, C4 que consigna el hash en `compilacion.md`; ningun tag publicado se mueve.
  Verificacion: `git cat-file -t v1.6.5` = `tag`; `git rev-parse v1.6.5^{commit}` = C3; `v1.6.4` y
  `v1.6.3` iguales a 1.3.
- [ ] 12.6 `engram sync` del proyecto (nunca `--all`), rama nueva y PR (nunca push directo a `main`),
  solo con pedido expreso; merge con merge commit; CI en verde antes de cerrar. Verificacion:
  `git merge-base --is-ancestor v1.6.5 origin/main` verdadero y checks del PR en verde.
- [ ] 12.7 Verificar que la copia de entrega es la del tag (SHA-256) y que el Anexo B y
  `compilacion.md` describen correctamente el tag y el hash. Verificacion: cotejo registrado.
- [ ] 12.8 **[GATED G-DIR]** Entrega de la version de defensa al tribunal con el visto bueno escrito
  del director registrado. Verificacion: fila G-DIR presente con fecha anterior o igual a la
  entrega.

## 13. Registro y cierre

- [ ] 13.1 `C/dictamen-correcciones.md`: seccion "c-250: atender la devolucion de quinta instancia"
  con la tabla de compuertas OQ-01 a OQ-07 y G-DIR (respuesta literal, fecha, responsable), la
  evidencia E1-E5, las tablas ANTES/DESPUES por bloque, las cifras de 3.4 y sus diferencias con las
  aproximaciones del tribunal, el libro mayor de paginas de la release y la release (`v1.6.5`,
  commits, SHA-256 del PDF). Verificacion: la seccion existe y el diff del archivo es aditivo.
- [ ] 13.2 `CHANGES.md`: entrada `[C-250]` con estado, objetivo, specs (`tesis-quinta-instancia`,
  `tesis-reencuadre-cuarta-instancia`, `tesis-numeros-canonicos`), dependencias (despues de c-249),
  gobernanza (MEDIUM; HIGH en el capitulo legal y la release), tag y "Leer antes", con el formato
  de `[C-249]`. Verificacion: la entrada existe.
- [ ] 13.3 Engram: `mem_save` con `topic_key: "opsx/c-250-atender-la-devolucion-de-quinta-instancia/apply"`;
  despues de cada llamada, `git branch --show-current` (volver a la rama si cambio). Verificacion:
  observacion guardada y rama correcta.
- [ ] 13.4 `openspec validate --all --strict`; archivar el change. Verificacion: valida y el change
  queda en `openspec/changes/archive/`.
