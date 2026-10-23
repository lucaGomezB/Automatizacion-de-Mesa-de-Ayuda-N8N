## Context

El change responde a la ausencia de literatura sobre calibracion de la confianza de LLM y sobre cascadas hibridas que senala el dictamen CONEAU 2026-10-22 sobre `v1.1.0`/`v1.1.1` (ver `proposal.md` - Why). Es documental y aditivo: incorpora fuentes nuevas por una extension declarada del protocolo de revision y las integra en tres capitulos. No modifica numeros, codigo ni atribuciones existentes.

Estado verificado de las fuentes LaTeX (`docs/Tesis/v10 (IA)/paper/sections/`, release `v1.1.1`, solo lectura, 22-10-2026):

- `03-estado-del-arte.tex:8` contiene el parrafo `\textbf{Protocolo de revision.}`: seis bases (Scopus, IEEE Xplore, ACM DL, ACL Anthology, Google Scholar, arXiv), cadenas A1-A4 y B1, corte 21-10-2026, criterios y bitacora `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md`. La linea 6 anuncia "tres areas". La subseccion 3.3 (`subsec:trabajos-academicos`, lineas 24-56) termina en la linea 56; la 3.4 (`subsec:analisis-comparativo`) empieza en la 58. Ningun `.tex` remite a "Seccion 3.4" en duro: insertar una subseccion no rompe remisiones.
- `02-marco-teorico.tex:46` (2.5, `subsec:nlp-llm`) es el parrafo de calibracion, con cuatro oraciones: O1 "Los LLM generan ... una estimacion de confianza ..."; O2 "La calibracion designa el grado de correspondencia ..."; O3 "\textcite{xuan2025mmluprox} documentan ... que la calibracion depende del modelo y del dominio" (atribucion erronea, dictamen secciones 5 y 9); O4 "En el sistema propuesto este concepto fundamenta el umbral operativo de revision humana ..." (contradicha por el comportamiento del gate, dictamen A1). La linea 54 menciona "un esquema hibrido que combine ambas estrategias" sin fuente.
- `08-discusion.tex` 9.2 (`subsec:comparacion-literatura`, lineas 26-34) compara exactitud y F1 con Paramesh y Revina y cierra con "La novedad del aporte radica ..." (linea 34). No menciona calibracion ni cascadas.
- `07-resultados.tex:165` sostiene hoy la "calibracion invertida" del clasificador en su conjunto; `c-126` la rehace por etapa (dictamen A2). `05-arquitectura.tex:84` ya llama "cascada hibrida" al subsistema de clasificacion.
- `Bibliography_base.bib`: 59 entradas; bloques aditivos comentados por change (c-110 HITL, c-113 alucinacion); convencion de claves `ApellidoAnio_palabra_clave`. `verify_citations.py` exige cero huerfanas y cero sin usar.
- PDF `main.pdf`: 101 paginas. Holgura medida con `pdftotext -layout` (lineas hasta el ultimo texto frente a unas 37-38 de una pagina llena): fin del capitulo 2 (p. 25) unas 15 lineas libres; fin del capitulo 3 (p. 30) llena; fin del capitulo 9 (p. 80) 1-2 lineas libres; fin de la bibliografia (p. 93) unas 10 lineas libres. Los capitulos y la bibliografia cierran con `\newpage`, de modo que el desborde de cualquiera de ellos suma una pagina.

Restricciones: numeros canonicos congelados (`numeros-canonicos.md`); sin cifras de terceros salvo cita textual con pagina; el protocolo descrito en el texto y la bitacora deben coincidir (requisito vigente "Protocolo de revision de literatura declarado y trazable"); toda vacancia debe acotarse al alcance revisado (requisito vigente "Afirmacion de vacancia acotada al alcance revisado"); tope de paginas tratado como duro por c-116 y c-121, con verificacion final en `c-136`.

## Goals / Non-Goals

**Goals:**

- Cubrir los dos ejes del hallazgo mas original de la tesis con fuentes arbitradas, verificadas una por una en existencia, metadatos y contenido: (a) calibracion de la confianza (concepto, medicion, calibracion posterior, confianza verbalizada de LLM, sesgo de etiquetas en clasificacion por instrucciones) y (b) cascadas de modelos con criterio de costo-exactitud.
- Proveer la fundamentacion de reemplazo de la calibracion en 2.5, para que `c-134` pueda retirar la atribucion a Xuan et al. sin dejar el concepto sin fuente.
- Hacer trazable la incorporacion mediante una extension declarada del protocolo (C1-C2) y una bitacora con correspondencia afirmacion-fuente.
- Acotar y medir el impacto en paginas, con contingencia declarada.

**Non-Goals:**

- No se retira ni reescribe ninguna atribucion existente (Xuan, Lai, Zhang, Mayor-Rocher, Revina, Paket/Colavito, Touvron, Paramesh): es de `c-134`.
- No se modifica el analisis de calibracion del capitulo de resultados ni su tabla de bandas (`c-126`), ni la descripcion del gate y del umbral de 0,70 (`c-125`), ni las recomendaciones (`c-131`), ni las tablas `tab:trabajos-academicos` y `tab:comparativa` (`c-130`).
- No se reejecutan las cadenas A1-A4 y B1 ni se mueve su fecha de corte; la vacancia sobre Gemini (A4) no cambia.
- No se calculan metricas nuevas (ECE, Brier) sobre el corpus: si `c-126` las reporta, cita las claves de este change.
- No se crean tags, no se regeneran renders (`tesis_para_agente.md`) ni se edita `dictamen-correcciones.md`: es de `c-136`.

## Decisions

### D1 - Extension del protocolo con cadenas C1-C2, misma bitacora, corte propio

Se agregan dos cadenas, formuladas en ingles como las existentes:

- **C1:** ("calibration" OR "confidence estimation" OR "confidence elicitation" OR "uncertainty") AND ("large language model" OR "LLM" OR "language model" OR "neural network") AND ("classification" OR "few-shot" OR "verbalized" OR "overconfidence")
- **C2:** ("cascade" OR "cascading" OR "routing" OR "hybrid" OR "rule-based") AND ("large language model" OR "LLM" OR "natural language processing" OR "NLP") AND ("classification" OR "cost" OR "efficiency")

Mismas seis bases. Criterios del grupo C: inclusion de publicaciones arbitradas (revistas y actas con revision por pares, incluidas ICML/PMLR, ICLR, las sedes de ACL y TMLR) que traten explicitamente la calibracion o estimacion de la confianza de clasificadores o modelos de lenguaje (C1) o las cascadas o el enrutamiento de modelos con criterio de costo-exactitud (C2), con evaluacion empirica o metodo de referencia, sin restriccion temporal (como B1, porque los trabajos fundacionales son anteriores a 2023); exclusion de literatura no arbitrada (incluidos preprints sin version arbitrada), notas de prensa y material comercial. Regla de seleccion declarada: entre los trabajos que cumplen los criterios se incorporan los mas proximos al escenario de la tesis (LLM consultado como servicio con confianza verbalizada; clasificacion en etiquetas fijas por instrucciones; cascada de una etapa economica y una costosa), hasta seis. Fecha de corte propia (`FECHA_CORTE_C`): la de ejecucion de las consultas al aplicar, posterior al 21-10-2026, identica en texto y bitacora. La bitacora `bitacora-busqueda-c-110.md` se extiende in situ: encabezado con la extension, seccion "Grupo C" (tabla base/cadenas/fecha/resultado, excluidas con motivo), tabla de verificacion por fuente y tabla de correspondencia afirmacion-fuente.

**Alternativas consideradas:** (a) una bitacora nueva `bitacora-busqueda-c-133.md`: se descarta porque el texto remite a una sola bitacora y el requisito exige consistencia texto-bitacora; dos archivos duplican la superficie de consistencia. (b) Reejecutar A1-A4 con un corte nuevo: se descarta porque altera el alcance de la vacancia A4 y la tabla de trabajos (`c-130`) y excede el objetivo. (c) Restringir C1 a "LLM" como en el esbozo inicial: se descarta porque no captura el trabajo de referencia que define la medicion de la calibracion en clasificadores (Guo et al. 2017); agregar "neural network" y "few-shot" lo captura sin recurrir a busqueda por bola de nieve. (d) Renombrar la bitacora: se descarta para no tocar la ruta citada en el texto.

### D2 - Seleccion de seis fuentes nucleo y reserva verificada

Fuentes nucleo (eje, motivo de seleccion):

1. **Guo et al. (2017)**, ICML, PMLR 70 - calibracion: define la calibracion de la confianza en clasificacion, la mide con diagramas de fiabilidad y ECE, muestra la sobreconfianza de las redes modernas y la correccion posterior por escalado de temperatura; incluye clasificacion de documentos.
2. **Zhao et al. (2021)**, ICML, PMLR 139 - calibracion en clasificacion con LLM por instrucciones: los LLM en clasificacion few-shot se sesgan hacia ciertas etiquetas (sesgos de etiqueta mayoritaria, de recencia en el prompt y de token frecuente) y la calibracion contextual de la distribucion de salida lo corrige. Es el paradigma de la tesis (prompt con ejemplos y etiquetas fijas). Sirve ademas a `c-134` para la sensibilidad al prompt.
3. **Tian et al. (2023)**, EMNLP - confianza verbalizada: en LLM ajustados con retroalimentacion humana la confianza verbalizada suele estar mejor calibrada que las probabilidades condicionales; motiva la derivacion a un experto en predicciones de baja confianza (vinculo directo con el gate).
4. **Xiong et al. (2024)**, ICLR - confianza verbalizada en LLM de caja negra (API comercial con entrada y salida textual, el caso de Gemini): tiende a la sobreconfianza, se concentra en valores altos y discrimina poco aciertos de errores; distingue calibracion (ECE) de prediccion de fallos (AUROC).
5. **Varshney y Baral (2022)**, EMNLP - cascadas: modelos de capacidad creciente con umbral sobre la confianza de prediccion para decidir si responder o derivar; mejora eficiencia y exactitud en clasificacion NLU.
6. **Chen, Zaharia y Zou (2024)**, FrugalGPT, TMLR - cascadas de LLM: consulta secuencial de API de costo creciente con una funcion de puntaje aprendida que decide aceptar o escalar; reduce costo con exactitud comparable; incluye tareas de clasificacion.

Reserva verificada (solo para sustituir una nucleo que no supere la verificacion de contenido al aplicar, re-verificando la sustituta): Geng et al. (2024, NAACL, survey de calibracion de LLM), Desai y Durrett (2020, EMNLP, calibracion de transformers en clasificacion), Jiang et al. (2021, TACL), Moslem y Kelleher (2026, TMLR, survey de enrutamiento y cascadas), Lin, Hilton y Evans (2022, TMLR), Zhou, Jurafsky y Hashimoto (2023, EMNLP), Brier (1950) y Naeini, Cooper y Hauskrecht (2015, AAAI). Excluidas: Kadavath et al. (2022, arXiv:2207.05221), preprint sin version arbitrada; la version arXiv de FrugalGPT, sustituida por su version arbitrada en TMLR.

**Alternativas consideradas:** (a) solo surveys (Geng 2024 + Moslem 2026): se descarta como base porque no aportan hallazgos empiricos puntuales contra los cuales contrastar el resultado propio; quedan en reserva. (b) Cinco fuentes sin Zhao et al.: se descarta porque el eje de calibracion quedaria sin una obra de LLM en clasificacion por instrucciones, que es lo que pide A4. (c) Incluir Kadavath et al. por su difusion: se descarta por el criterio de exclusion declarado. Orden de retiro si el presupuesto lo exige (D8): primero Tian et al., luego Varshney y Baral; minimo viable de cuatro (Guo, Zhao, Xiong, Chen), que cubre ambos ejes.

### D3 - Verificacion en tres compuertas por fuente, sin evadir controles anti-bot

Cada fuente pasa, antes de citarse: (1) **existencia** - `curl -sI https://doi.org/<doi>` responde 302 hacia la editorial, o, para sedes sin DOI, la pagina oficial responde 200 (PMLR; listado y `.bib` oficiales de TMLR en `jmlr.org/tmlr/papers/`; foro de OpenReview identificado por MLAnthology o por el encabezado "Published as a conference paper at ICLR 2024"); (2) **metadatos** - cotejo de titulo, autores, sede, ano y paginas contra Crossref (`api.crossref.org/works/<doi>`) o contra los metadatos oficiales de la sede; (3) **contenido** - lectura del texto completo y registro, en la bitacora, de cada afirmacion atribuida con su seccion o pagina. Si una compuerta falla, la fuente se descarta y se reemplaza desde la reserva (re-verificada). Los controles anti-bot no se evaden: el PDF de OpenReview de la version TMLR de FrugalGPT devolvio 403 con desafio de verificacion; al aplicar, se pide al usuario que lo descargue, o, si no es posible, se registra que el contenido se verifico sobre arXiv:2305.05176v1 y la atribucion se limita al concepto de cascada con funcion de puntaje, presente en el resumen de ambas versiones.

**Pre-verificacion realizada en propose (22-10-2026)** - a repetir y registrar formalmente al aplicar:

| Clave fijada | Sede y paginas | Identificador | Existencia | Metadatos | Contenido verificado |
|---|---|---|---|---|---|
| `Guo2017_calibration` | ICML 2017, PMLR 70, 1321-1330 | proceedings.mlr.press/v70/guo17a.html | 200 | meta `citation_*` PMLR: 4 autores, paginas OK | texto completo (arXiv 1706.04599): sec. 2 diagramas de fiabilidad y ECE (atribuido a Naeini et al. 2015); sec. 4.2 escalado de temperatura; sec. 5 20 News, Reuters, SST |
| `Zhao2021_calibrate_before_use` | ICML 2021, PMLR 139, 12697-12706 | proceedings.mlr.press/v139/zhao21c.html | 200 | meta PMLR: 5 autores, paginas OK | texto completo PMLR: sesgos de etiqueta mayoritaria, reciente y de token frecuente (sec. 1 y 4); calibracion contextual con entrada sin contenido (sec. 5); clasificacion de texto (AGNews, DBPedia, SST-2, entre otras) |
| `Tian2023_verbalized_confidence` | EMNLP 2023, 5433-5442 | doi 10.18653/v1/2023.emnlp-main.330 | 302 a ACL Anthology | Crossref: 8 autores, paginas OK | texto completo ACL: p. 5433 (resumen y sec. 1) derivacion a un experto; confianza verbalizada mejor calibrada que las probabilidades condicionales en ChatGPT, GPT-4 y Claude (TriviaQA, SciQ, TruthfulQA); ECE con referencia a Guo et al. |
| `Xiong2024_confidence_elicitation` | ICLR 2024 | openreview.net/forum?id=gjeQKFxFpZ | foro identificado por MLAnthology; PDF arXiv v2 con encabezado ICLR 2024 | 7 autores (arXiv, MLAnthology) | texto completo arXiv v2: p. 2 y p. 6 (sec. 5.1) sobreconfianza y valores "predominantly ... within the 80% to 100% range", multiplos de 5; API comerciales solo textuales (p. 2); prediccion de fallos debil (sec. 5.1-5.2) |
| `Varshney2022_model_cascading` | EMNLP 2022, 11007-11021 | doi 10.18653/v1/2022.emnlp-main.756 | 302 a ACL Anthology | Crossref/OpenAlex: 2 autores, paginas OK | texto completo ACL: sec. 1 umbral sobre MaxProb para responder o derivar; sec. 4.1 diez conjuntos de clasificacion NLU |
| `Chen2024_frugalgpt` | TMLR 2024 (ISSN 2835-8856), dic. 2024 | openreview.net/forum?id=cSimKw5p6R | listado y `.bib` oficiales TMLR 200; PDF OpenReview 403 (anti-bot) | `.bib` TMLR: 3 autores, ano 2024 | arXiv 2305.05176v1 (unica version arXiv): sec. 3 (p. 5) funcion de puntaje aprendida y umbral; sec. 4 (p. 6) HEADLINES, OVERRULING, COQA. Pendiente: texto completo de la version TMLR |

Reserva (existencia y metadatos verificados; contenido verificado solo a nivel de resumen, salvo indicacion; lectura completa obligatoria antes de usarla):

| Clave reservada | Obra | Identificador |
|---|---|---|
| `Geng2024_confidence_survey` | NAACL 2024, 6577-6595 | doi 10.18653/v1/2024.naacl-long.366 |
| `Desai2020_calibration_transformers` | EMNLP 2020, 295-302 | doi 10.18653/v1/2020.emnlp-main.21 |
| `Jiang2021_lm_calibration` | TACL 9, 962-977 | doi 10.1162/tacl_a_00407 |
| `Moslem2026_routing_cascading` | TMLR 2026 (survey) | openreview.net/forum?id=ypRg1TvQaM (arXiv journal-ref TMLR 2026) |
| `Lin2022_uncertainty_words` | TMLR 2022 | openreview.net/forum?id=8s8K2UZGTZ |
| `Zhou2023_epistemic_markers` | EMNLP 2023, 5506-5524 | doi 10.18653/v1/2023.emnlp-main.335 |
| `Brier1950_verification` | Monthly Weather Review 78(1), 1-3 | doi 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2 |
| `Naeini2015_bayesian_binning` | AAAI 29(1), 2901-2907 | doi 10.1609/aaai.v29i1.9602 |

**Alternativas consideradas:** verificar solo existencia y metadatos (como alcanzo en versiones previas): se descarta porque es exactamente el defecto que el dictamen encontro en Xuan et al. (fuente real que no trata lo atribuido).

### D4 - Mapa de atribuciones permitidas por fuente

Para no repetir el error de Xuan et al., cada fuente se cita solo para lo que sostiene:

| Clave | Se puede atribuir | No se debe atribuir |
|---|---|---|
| `Guo2017_calibration` | definicion de calibracion en clasificacion; sobreconfianza de redes neuronales modernas; medicion con diagramas de fiabilidad y ECE; correccion posterior (escalado de temperatura) | resultados sobre LLM o confianza verbalizada; la invencion del ECE (Naeini et al. 2015) |
| `Zhao2021_calibrate_before_use` | sesgo de LLM en clasificacion few-shot hacia ciertas etiquetas; sensibilidad al formato, a los ejemplos y a su orden; calibracion contextual de la distribucion de salida | calibracion confianza-acierto en sentido ECE; aplicabilidad a API sin acceso a probabilidades |
| `Tian2023_verbalized_confidence` | confianza verbalizada de LLM ajustados con retroalimentacion humana mejor calibrada que sus probabilidades condicionales en las tareas evaluadas; utilidad de la confianza para derivar a un experto; dependencia de la estrategia de elicitacion | resultados en clasificacion propiamente dicha; resultados sobre Gemini; calibracion garantizada |
| `Xiong2024_confidence_elicitation` | escenario de caja negra (API comercial textual); sobreconfianza de la confianza verbalizada; concentracion en valores altos (cifra 80-100 % solo con cita textual y p. 6); capacidad debil para separar aciertos de errores; ECE frente a AUROC | resultados sobre Gemini; imposibilidad de calibrar; generalizacion a tareas no evaluadas |
| `Varshney2022_model_cascading` | cascadas de modelos de capacidad creciente; derivacion por umbral sobre la confianza de prediccion; mejora conjunta de eficiencia y exactitud en clasificacion NLU | resultados con LLM o con una primera etapa de reglas |
| `Chen2024_frugalgpt` | cascadas de LLM como estrategia de reduccion de costo; aceptacion o escalamiento segun una funcion de puntaje aprendida y un umbral | que la cascada use la confianza autodeclarada por el LLM (usa un evaluador aprendido aparte); cifras de ahorro sin cita textual con pagina |

Las afirmaciones sobre el sistema propio (primera etapa de reglas, confianza verbalizada en JSON de la etapa Gemini) son del texto de la tesis y no se atribuyen a estas fuentes.

### D5 - Interfaz con c-134 y c-125 en el parrafo de calibracion de 2.5 (propiedad por oracion)

| Oracion de `02-marco-teorico.tex:46` | Dueno | Accion |
|---|---|---|
| O1 "Los LLM generan ... estimacion de confianza ..." | - | sin cambios |
| O2 "La calibracion designa ..." | c-133 | ancla; puede recibir la cita de Guo et al. |
| (nuevas, a continuacion de O2) | c-133 | medicion y correccion (Guo); confianza verbalizada en LLM consultados como servicio, sobreconfianza y dependencia de la elicitacion (Xiong; Tian) |
| O3 Xuan et al. "la calibracion depende del modelo y del dominio" | c-134 | retirar |
| O4 "En el sistema propuesto este concepto fundamenta el umbral ..." | c-125 | reescribir |

c-133 se ancla en el texto de O2, que ni c-134 ni c-125 editan, de modo que el orden de aplicacion entre los tres es conmutativo. c-133 MUST NOT editar ni borrar O3 ni O4 y MUST NOT citar `xuan2025mmluprox` en lo que agrega. En la linea 54 ("... un esquema hibrido que combine ambas estrategias ...") c-133 agrega la nocion de cascada con `Varshney2022_model_cascading` y `Chen2024_frugalgpt`. Si al aplicar se observa que O3 ya fue retirada, se inserta igual a continuacion de O2. Registro compartido de claves: las de D3 son fijas para toda la familia; el change que llegue primero agrega la entrada y los demas la reutilizan (en particular `c-134` con `Zhao2021_calibrate_before_use` y `c-126`/`c-131` con `Guo2017_calibration`), verificando `grep -c "{<clave>,"` = 1.

**Alternativas consideradas:** (a) que c-133 reescriba el parrafo completo, retirando O3: se descarta porque el orquestador asigno la retirada a c-134 y porque O4 es de c-125; reescribir el parrafo entero garantiza conflicto con dos changes. (b) Insertar despues de O3: se descarta porque el ancla desapareceria cuando c-134 la retire.

### D6 - Ubicacion en el capitulo 3: subseccion propia entre 3.3 y 3.4

Se agrega `\subsection{Calibracion de la confianza y cascadas de modelos}\label{subsec:calibracion-cascadas}` entre el final de 3.3 y el inicio de 3.4, con dos parrafos (calibracion: Guo, Zhao, Tian, Xiong; cascadas: Varshney y Baral, Chen et al.) y, solo si la busqueda C1-C2 no identifica trabajo que lo refute, un cierre de vacancia acotada ("en las fuentes consultadas con las cadenas C1-C2 hasta `FECHA_CORTE_C`, no se identifico trabajo arbitrado que evalue una cascada de reglas deterministicas y LLM con confianza verbalizada sobre tickets de soporte en espanol"). La linea 6 pasa a anunciar cuatro areas. Division de contenido para no duplicar: 2.5 da los conceptos (que es calibrar, como se mide, que es la confianza verbalizada, que es una cascada); 3.x da los hallazgos de la literatura y la brecha.

**Alternativas consideradas:** (a) un parrafo con encabezado en negrita dentro de 3.3: ahorra unas dos lineas, pero 3.3 trata de tickets y el contenido quedaria mal ubicado y menos visible para el evaluador. (b) Filas nuevas en `tab:trabajos-academicos`: se descarta porque estas obras no clasifican tickets y la tabla es de `c-130`. (c) Agregar la vacancia en la sintesis de 3.4: se descarta porque esa sintesis la edita `c-130` (propiedad de telefonia).

### D7 - Parrafo de discusion en 9.2, condicionado a c-125 y c-126, sin numeros nuevos

Se inserta un parrafo inmediatamente antes de "La novedad del aporte radica" que: (i) lee el hallazgo del capitulo de resultados tal como lo formula `c-126` (la confianza autodeclarada por la etapa Gemini se concentro en el extremo superior de la escala y no discrimino aciertos de errores dentro del rango observado; la etapa de reglas no emite una confianza utilizable como criterio de derivacion a revision) y lo relaciona con la sobreconfianza y la baja capacidad de discriminacion de la confianza verbalizada documentadas por Xiong et al., con la salvedad de Tian et al. sobre la dependencia de la elicitacion; (ii) senala que en la literatura de cascadas la derivacion entre etapas depende de una senal de fiabilidad correlacionada con el acierto y de un umbral (confianza de prediccion en Varshney y Baral; funcion de puntaje aprendida en Chen et al.). El sistema propuesto adopta ese esquema en su primera transicion: segun `numeros-canonicos.md` (seccion 4) y `App/Backend/app/classifiers/hybrid.py`, el cortocircuito de la etapa de reglas se gobierna por un puntaje de correctitud con un punto de operacion fijado fuera de muestra, que ordena la correctitud esperada pero no es una probabilidad calibrada, y no por su campo `confianza` (fuerza de senal); en cambio, la salvaguarda de revision humana depende de la confianza verbalizada de la etapa Gemini, que es precisamente la senal que la literatura muestra sobreconfiada. El parrafo usa la terminologia que fije `c-125` para ambas magnitudes y concluye que la eficiencia del esquema hibrido frente a una alternativa solo-modelo no puede afirmarse sin la exactitud por etapa (`c-126`) ni un brazo de comparacion (hipotesis subsidiaria no contrastada, `c-128`). Remite a `\autoref{subsec:calibracion}` y a `\autoref{subsec:calibracion-cascadas}` en lugar de repetir cifras; MUST NOT reintroducir "calibracion invertida" ni afirmar demostrada la eficiencia del esquema hibrido.

**Alternativas consideradas:** ubicarlo en 9.1 junto al parrafo del gate: se descarta porque 9.1 lo reescriben `c-125`, `c-126` y `c-127`, y el orquestador asigno a este change la seccion "Comparacion con la literatura". Aplicarlo antes de `c-126`: se descarta porque el capitulo de resultados aun sostendria la calibracion invertida del clasificador en su conjunto y el parrafo quedaria incoherente con el.

### D8 - Presupuesto de lineas por insercion e impacto en paginas

| Insercion | Presupuesto | Holgura disponible | Efecto esperado |
|---|---|---|---|
| 2.5 (oraciones de calibracion + clausula de cascada en linea 54) | <= +8 lineas | unas 15 lineas (p. 25) | 0 paginas |
| 3: protocolo (C1-C2, criterios, corte) | <= +8 lineas | ninguna (p. 30 llena) | +1 pagina para todo el capitulo |
| 3: oracion introductoria | <= +1 linea | idem | incluido arriba |
| 3: subseccion nueva (con titulo) | <= +21 lineas | idem | incluido arriba (total <= 30 lineas, deja unas 7 para `c-130` en la pagina nueva) |
| 9.2: parrafo de contraste | <= +7 lineas | 1-2 lineas (p. 80) | 0 o +1 pagina, segun lo que hagan `c-125`-`c-127` en el capitulo |
| Bibliografia: 6 entradas | unas 24 lineas impresas (3-5 por entrada) | unas 10 lineas (p. 93) | +1 pagina |

Impacto esperado: +2 paginas (101 -> 103), +3 en el peor caso. Las lineas se estiman a unos 95 caracteres por linea de cuerpo y se miden al aplicar con el PDF recompilado. Compensacion dentro del alcance: redaccion compacta, sin duplicar 2.5 en 3.x, y el parrafo de 9.2 remite a 3.x en lugar de describir de nuevo las fuentes. Contingencia si el aumento atribuible supera +3: reducir el parrafo de 9.2 a dos oraciones y retirar fuentes en el orden de D2. Compensaciones disponibles fuera del alcance, informadas a `c-136`: la fecha de consulta duplicada en las entradas `@online` (`c-134`), el parrafo de Revina duplicado entre 3.3 y 9.2 (`c-134`) y la frase "El relevamiento propio ..." repetida en 3.1 (`c-130`). La decision sobre el tope de la familia es de `c-136` (ver Open Questions).

**Alternativas consideradas:** (a) tres fuentes en lugar de seis: no evita la pagina extra de la bibliografia (tres entradas ya superan la holgura de unas 10 lineas) y debilita la cobertura. (b) Ubicar todo en el marco teorico para aprovechar su holgura: se descarta porque el dictamen observa la ausencia en el estado del arte.

### D9 - Fuentes senaladas por el dictamen sobre tickets: verificadas, fuera del alcance por defecto

El dictamen menciona trabajos de clasificacion de tickets "no relevados" (ITSM-BERT sobre portugues) y el orquestador agrego Alsac et al. Ambos fueron verificados en propose:

| Obra | Sede | Identificador | Contenido (resumen) |
|---|---|---|---|
| Carvalho, Lobato, Jacob Junior y Carmona Cortes (2026), "ITSM-BERT: Classificacao de Tickets de Service Desk via Fine-Tuning do BERTimbau Integrado com Sistema GLPI" | Anais do XLI SBBD 2026, SBC, 317-330 | doi 10.5753/sbbd.2026.249215 (302 a sol.sbc.org.br) | tickets en portugues de Brasil (80.879 registros reales); BERTimbau ajustado; comparacion con SVM, TF-IDF, Word2Vec y BERT-SVM |
| Alsac, Yilmaz, Kocoglu y Seker (2025), "Towards Intelligent IT Service Management: A Comparative Evaluation of Machine Learning and Language Models for Ticket Classification and Assignment" | UBMK 2025, IEEE, 265-270 | doi 10.1109/ubmk67458.2025.11207046 (302 a IEEE Xplore) | base corporativa; representaciones BERT, BERTurk, MiniLM y XLM; MLP y ajuste fino de BERT para clasificacion y asignacion |

No son capturadas por C1-C2 (no tratan calibracion ni cascadas), caen en la cadena A1 cuyo corte no se mueve, su lugar natural es `tab:trabajos-academicos` (de `c-130`) y su incorporacion cuesta unas 8 lineas mas en un capitulo sin holgura. Por defecto NO se incorporan ni se registran en la bitacora (que solo admite consultas declaradas en el texto); sus datos quedan aqui para que `c-134` (si sostiene con fuente la mencion a corpus en portugues) o una decision posterior los reutilicen. Ver Open Questions.

**Alternativas consideradas:** incorporarlas como "complemento de A1 por referencia de la evaluacion externa" con filas nuevas en la tabla: valida y util para la tabla, pero cambia el alcance de A1, depende de `c-130` y suma paginas; se deja a decision del usuario.

### D10 - Bloque bibliografico aditivo y tipado

Las seis entradas se agregan en un bloque nuevo a continuacion del bloque HITL de c-110, con encabezado comentado "CALIBRACION DE LA CONFIANZA Y CASCADAS DE MODELOS - entradas aditivas agregadas por c-133, verificadas (DOI/Crossref, PMLR, TMLR/OpenReview; <fecha>). No se modifica ninguna entrada existente." Tipos: `@inproceedings` para Guo, Zhao, Tian, Xiong y Varshney (con `booktitle`, `pages` cuando existen, `publisher`/`series` y `doi` o `url`); `@article` para Chen et al. (`journal = {Transactions on Machine Learning Research}`, `issn = {2835-8856}`, `url` del foro). Las sedes sin DOI (PMLR, ICLR, TMLR) llevan `url` oficial, como `Brown2020_few_shot`. Conteo esperado: 59 -> 65.

**Alternativas consideradas:** citar la version arXiv de FrugalGPT (`@misc` con `eprint`): se descarta porque existe version arbitrada (TMLR, diciembre de 2024) y el protocolo excluye lo no arbitrado.

### D11 - Estrategia de verificacion (TDD no aplica)

Cambio documental sin test runner para prosa ni `.bib`: Strict TDD no aplica (mismo criterio que c-110). Las compuertas son: `curl`/Crossref por fuente (D3), `python verify_citations.py`, compilacion con `latexmk` en el contenedor `texlive-thesis` (sin errores fatales ni referencias o citas indefinidas en `main.log`; `main.blg` sin advertencias de claves duplicadas), conteo de paginas, `grep` de anclas, de claves y de numeros en el texto agregado, y `git diff` acotado a los cinco archivos.

## Risks / Trade-offs

- **[Atribucion que excede la fuente, repitiendo el error de Xuan et al.]** -> Mitigacion: mapa de atribuciones (D4), lectura de texto completo y tabla afirmacion-fuente con seccion o pagina en la bitacora; revision cruzada por `c-134`.
- **[Incoherencia con la reformulacion por etapa de c-126]** -> Mitigacion: el parrafo de 9.2 se aplica solo con `c-125` y `c-126` aplicados (D7), remite a `\autoref{subsec:calibracion}` y no repite cifras.
- **[Crecimiento de paginas]** -> Mitigacion: presupuesto por insercion, medicion antes y despues, contingencia (D8) e informe a `c-136`.
- **[Busqueda poco reproducible en bases por suscripcion]** -> Mitigacion: misma convencion de la bitacora c-110 (registrar trabajos examinados e incorporados por base cuando el conteo bruto no es recuperable).
- **[La busqueda C1-C2 encuentra un trabajo mas proximo (p. ej. cascada reglas-LLM en tickets) o uno que refute la vacancia]** -> Mitigacion: la regla de seleccion de D1 permite sustituir; la vacancia de 3.x solo se enuncia si la busqueda la confirma.
- **[La busqueda encuentra un trabajo arbitrado 2023-2026 que evalua Gemini sobre tickets en espanol]** -> Mitigacion: se detiene la aplicacion y se informa al orquestador; la vacancia A4 no es de este change.
- **[OpenReview bloquea el acceso automatizado al texto de la version TMLR de FrugalGPT]** -> Mitigacion: descarga asistida por el usuario o atribucion minima verificada sobre arXiv v1 (D3); nunca se evade el control.
- **[Claves duplicadas si c-126, c-131 o c-134 agregan las mismas obras]** -> Mitigacion: registro unico de claves (D3/D5) y verificacion `grep -c` = 1 por clave.
- **[Conflicto textual con c-130 o c-134 en 03 y 08]** -> Mitigacion: insercion por anclas de contenido en regiones que esos changes no editan (D5-D7) y `git diff` acotado.

## Migration Plan

1. Linea base: arbol limpio en `ramagonzalo`; paginas (101), entradas (59), `verify_citations.py` PASS; holgura de p. 25, 30, 80 y 93; estado de `c-125`, `c-126` y `c-134` (presencia de O3, terminologia de confianza por etapa, texto de "calibracion invertida").
2. Ejecutar C1-C2 en las seis bases con `FECHA_CORTE_C`, aplicar criterios y regla de seleccion, y registrar en la bitacora (D1).
3. Re-verificar las seis fuentes en las tres compuertas y completar las tablas de verificacion y de correspondencia afirmacion-fuente (D3, D4); sustituir desde la reserva si alguna falla.
4. Agregar el bloque bibliografico (D10).
5. Editar 2.5 (D5), luego el capitulo 3 (protocolo, oracion introductoria y subseccion; D1, D6) y verificar la consistencia texto-bitacora.
6. Con `c-125` y `c-126` aplicados, insertar el parrafo de 9.2 (D7); si no lo estan, posponer solo este paso y dejarlo pendiente en `tasks.md`.
7. Compilar, correr `verify_citations.py`, medir paginas y aplicar la contingencia de D8 si corresponde; registrar el conteo para `c-136`.
8. Rollback: `git checkout <commit-previo> --` sobre los cinco archivos y recompilar; si `c-134` ya retiro O3, conservar la fundamentacion de 2.5 y sus entradas o revertir junto con `c-134` (ver `proposal.md` - Rollback).

## Open Questions

1. **Tope de paginas de v1.2.0:** este change agrega +2 paginas esperadas (+3 en el peor caso) y la familia c-125..c-134 agrega contenido exigido por el dictamen. Se mantiene el tope de 101 con compensacion de la familia, o `c-136` fija un tope nuevo? Recomendacion: decidirlo en `c-136` con el conteo real de todos los changes; este change solo garantiza su presupuesto (D8).
2. **ITSM-BERT y Alsac et al. (D9):** se incorporan como filas de `tab:trabajos-academicos` mediante un complemento declarado de A1 (despues de `c-130`), o quedan fuera? Recomendacion por defecto: fuera de este change; reconsiderar si `c-134` decide sostener la mencion a corpus en portugues.
3. **Vacancia acotada en 3.x:** se enuncia solo si C1-C2 la confirman (D6). El usuario puede preferir omitirla aunque se confirme, para no sumar una afirmacion de inexistencia; por defecto se enuncia acotada.
4. **Texto completo de FrugalGPT en TMLR:** se acepta la descarga asistida por el usuario del PDF de OpenReview, o la atribucion minima verificada sobre arXiv v1 (D3)?
