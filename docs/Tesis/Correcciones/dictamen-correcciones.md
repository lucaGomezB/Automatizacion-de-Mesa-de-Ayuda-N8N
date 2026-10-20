# Correcciones del dictamen (CONEAU) — registro

> Registro de las correcciones de la tesis surgidas del dictamen (perfil evaluador
> `Prompt2.docx`). Se aplican a medida que el autor las provee. Lo que no se puede
> resolver todavía se anota abajo para incorporarlo luego al proyecto / tesis.
>
> Estado: 2026-10-19.

---

## Aplicadas

### A1. Anexo F — declaración de integridad académica
- **Archivo**: `docs/anexo_f_corpus.md`
- **Cambio**: la declaración dejó de afirmar que el corpus disponible es sintético
  y que "no constituye evidencia experimental del desempeño del sistema". Ahora
  afirma que la evaluación se hace sobre el **corpus real** (200 casos
  pseudonimizados, de incidentes reales), que **es fuente de evidencia** del
  Capítulo 7, y que **está versionado** en su forma pseudonimizada.
- Se conserva una **nota histórica** del corpus sintético descartado en C-27, para
  que sus números no se citen como vigentes.
- La sección `## Corpus real (trabajo de campo futuro)` pasó a
  `## Corpus de evaluación (real, pseudonimizado)` (verbo en pasado).

### A2. READMEs de `evaluation/`
- `evaluation/README.md`: `## Dónde Colocar el Corpus Real` ("no está trackeado en
  git por privacidad") → `## Ubicación del Corpus Real` ("versionado en su forma
  pseudonimizada").
- `evaluation/data/README.md`: "no trackeado en git por privacidad" → "versionado
  en su forma pseudonimizada".

### A3. README raíz — referencia rota
- `docs/ANEXO_H_Especificacion_Completa.md` (no existe) →
  `docs/anexo_h_prompt_gemini.md` (canónico, según `openspec/specs/project-structure`).

### A4. `report_provisional.md` → `report.md`
- **Estado: ya satisfecho.** `evaluation/report_provisional.md` fue eliminado y
  renombrado a `evaluation/report.md` en **C-27** (2026-09-11). No queda ninguna
  referencia vigente a `report_provisional.md`; todas las docs usan
  `evaluation/report.md`.

---

## Pendientes (backlog)

### P1.0 — `tiempo_manual_s`: medición real redondeada al alza (declarar + acotar) — APLICADO por c-76 (2026-10-19)
Verificación de los datos de tiempo del corpus (JSON, `Corpus Tesis.xlsx` y ambos CSV).

- `tiempo_manual_s`: **medición real en vivo** durante la atención de usuarios,
  registrada con **redondeo hacia arriba** (solo 31 valores únicos; 180/200
  múltiplos de 10; 199/200 múltiplos de 5; todos enteros). El redondeo al alza es
  un sesgo de medición **sistemático** (infla el tiempo manual), no un error
  aleatorio.
- `tiempo_automatizado_s`: medición real (198 valores únicos, con decimales; p. ej.
  R001: latencia 3721 ms = pipeline 3,721 + espera 17,288 = 21,009 s).
- **Análisis de sensibilidad** — la conclusión es robusta al redondeo:

  | Escenario | manual media | reducción | Wilcoxon p | r (rank-biserial) |
  |---|---|---|---|---|
  | Reportado (redondeado) | 61,6 s | 75,9 % | 2,0e-32 | 0,983 |
  | Conservador (−5 s) | 56,6 s | 73,8 % | 2,6e-30 | 0,966 |
  | Conservador (−10 s) | 51,6 s | 71,3 % | 2,7e-27 | 0,941 |

  > Nota (c-77): esta tabla registra el análisis de sensibilidad tal como se
  > calculó sobre el corpus de c-76. La reducción "Reportado" se rebasó luego a
  > **71,2 %** (\(W = 363\), \(r = 0,9639\)) con el corpus actualizado por c-77
  > (commit `4602bf5`); los escenarios conservadores quedan como registro histórico.

- **Pares invertidos**: en **12/200** casos el flujo automatizado NO fue más rápido
  (auto ≥ manual). La tesis afirma **W=0** ("sin una sola excepción"), que es
  **falso** para el corpus real.
- **Acción (no requiere re-medición)**: (1) declarar el redondeo al alza en la
  metodología; (2) reportar la reducción como cota superior y su cota inferior
  conservadora (≥ 71 %); (3) usar mediana y estadísticos de rango como claim
  primario; (4) reemplazar W=0 por el valor real con corrección por empates; (5)
  los valores de la tesis (manual media 165,3 s) siguen siendo los del corpus
  sintético descartado y deben reemplazarse por los reales.
- Re-medir solo si se necesita una media/IC precisa o si el redondeo fuera a
  minutos enteros en la mayoría de los casos.

### P1. Reconciliar el Cap. 7 (Resultados) y la metodología con el corpus real — APLICADO por c-76 (2026-10-19)
El cuerpo de la tesis todavía reporta los **números y la distribución del corpus
sintético descartado en C-27**.

**Archivos afectados**: `04-marco-metodologico.tex`, `07-resultados.tex`,
`08-discusion.tex` (y menciones con la categoría retirada **"Operaciones"** en
`00-resumen.tex`, `01-introduccion.tex`, `05-arquitectura.tex`).

**Stale (tesis) vs real (corpus 200/200)**:

| Métrica | Tesis (stale) | Corpus real |
|---|---|---|
| Clases | 3 (incluye "Operaciones", retirada) | 5 canónicas |
| Distribución | 82 Sistemas / 64 Operaciones / 54 Soporte Técnico | Sistemas 16 / STH 85 / STS 67 / Seg. Informática 31 / Bases de Datos 1 |
| Exactitud | 92,0 % | 73,5 % (147/200) |
| F1 macro | 0,919 | 0,5207 |
| Manual (media) | 165,3 s | 61,6 s |
| Automatizado (media) | 18,2 s | 17,76 s |
| Reducción | 89,0 % | 71,2 % |
| Wilcoxon | W=0, r=1,00 | W=363, p=3,08e-32, r=0,9639 |

**Datos reales disponibles (listos para aplicar)**:
- Distribución primaria: Sistemas 16, Soporte Técnico Hardware 85, Soporte Técnico
  Software 67, Seguridad Informática 31, Bases de Datos 1.
- Canales: correo 66, web 53, teléfono 81.
- Tiempos: manual media 61,6 s (mediana 50,0; sd 44,9; rango 10–300) vs auto media
  17,76 s (mediana 17,47; sd 13,48; rango 0,525–65,834); reducción 71,2 %.
- Clasificación (`evaluation/report.md`): exactitud estricta 73,5 % (147/200),
  macro-F1 0,5207, micro-F1 0,6654, subset accuracy 0,43, Hamming 0,3586; etapas
  deterministic 131 / Gemini 69.
- Fuentes: `data/corpus_evaluacion_pseudonimizado.json`, `evaluation/report.md`.

### P2. Anexo H — versión del modelo — APLICADO por c-76 (2026-10-19)
El título de `docs/anexo_h_prompt_gemini.md` dice "Gemini 2.5 Flash" mientras
`README.md` y el código usan `gemini-3.6-flash`. Alinear.

### P3. Coherencia del encuadre honesto del objetivo no alcanzado — APLICADO por c-76 (2026-10-19)
Al completar P1/P1.0 quedó una tensión interna en las conclusiones: el
reconocimiento del incumplimiento del segundo objetivo específico (exactitud
73,5~\% / F1 macro 0,5207 frente a las cotas 85~\% / 0,85) coexistía con la
afirmación de que el trabajo "ha cumplido satisfactoriamente con el objetivo
general", sin calificar la meta no alcanzada.

- **Decisión del autor**: mantener el encuadre honesto (declarar la meta de
  exactitud NO alcanzada), sin re-medir.
- **Fix**:
  - `09-conclusiones.tex` (l.6): el objetivo general (construir y validar el
    sistema) se declara cumplido, pero se explicita que el segundo objetivo
    específico NO se alcanza; la reducción de tiempo del 71,2~\% se mantiene como
    resultado central sostenido (\(W = 363\)).
  - `09-conclusiones.tex` (l.12, §Cumplimiento de los objetivos): "brecha que se
    analiza" → "ese objetivo no se alcanza; la brecha se analiza en el Cap. 8",
    consistente con §8.1/§8.3.
- **Sin números nuevos**: solo 73,5~\%, 0,5207, 71,2~\%, \(W = 363\), IC
  [67,0~\%, 79,1~\%].
- **Verificación**: `rg "cumplido satisfactoriamente|supero con holgura|superó los
  umbrales|no deja espacio"` en las secciones devuelve CERO coincidencias en el
  `.tex` vivo (residuo solo en `.tex.bak` trackeados, fuera de alcance).

### P4. (a completar)
Items restantes del dictamen a medida que el autor los provea.

---

## Grupo: Trazabilidad y existencia de datos experimentales (verificado 2026-10-09)

Correcciones adicionales del dictamen, verificadas contra `docs/Tesis/v9 (IA)/paper/sections/` y los datos reales.

### T1. La campaña experimental no debe presentarse como trabajo futuro (Cap. 7 + Anexo F)
Anexo F ya corregido (A1). El Cap. 7 (`07-resultados.tex`) reporta (números stale) como si la campaña estuviera hecha; al reemplazarlos por los reales (P1) queda presentada como **realizada**. Verificar que ningún pasaje del Cap. 7 la presente como pendiente/futura.

### T2. El Anexo F remite a `evaluation/data/` y promete un CSV de 7 columnas (STALE)
- `12-anexos.tex:41` (§Corpus de validación): dice que el corpus se conserva como **CSV en `evaluation/data/`** con 7 columnas (id, descripción, canal, categoría asignada, categoría predicha, tiempo, confianza) + planillas.
- Realidad: `evaluation/data/` NO contiene corpus (C-27); el corpus real es `data/corpus_evaluacion_pseudonimizado.json` (JSON; `categoría predicha`/`confianza` viven en `evaluation/predicciones.json`, no por caso en el corpus).
- Fix: reescribir §5 del Anexo apuntando al corpus real JSON pseudonimizado.

### T3. Caps 7.2 y 1.6 — datos incorrectos
- **7.2** (`07-resultados.tex` §Matriz de confusión y métricas): exactitud 92 %, F1 macro 0,919, 3 clases, 82/64/54 → reales (P1): 73,5 %, 0,5207, 5 clases, 16/85/67/31/1.
- **1.6** (`01-introduccion.tex` §Alcance y delimitaciones): línea 68 "tres sectores (Sistemas, Operaciones y Soporte Técnico)" → cinco; línea 72 "Gemini 2.5 Flash" → `gemini-3.6-flash`; revisar la fecha "junio de 2026".

### T4. Caps 5.5, 8.1, 9.1 — distribución de etapas + etapa fallback no documentada
- Real (`evaluation/report.md`): deterministic 131/200 = **65,5 %**, Gemini 69/200 = **34,5 %**, **fallback 0**.
- **5.5** (`05-arquitectura.tex` §Subsistema de clasificación híbrido, l.58): "≈ 62 % primera etapa / 38 % modelo externo" → 65,5 % / 34,5 %.
- **8.1** (`08-discusion.tex` §Interpretación, l.10): "≈ 62 %".
- **9.1** (`09-conclusiones.tex` §Cumplimiento, l.12): "seis de cada diez" → 65,5 %.
- Existe una etapa **fallback** (0 casos) que la tesis **no documenta**; hay que documentarla y aclarar el orden deterministic → Gemini → fallback.

### T5. Caps 7.1, 4.6, 4.7 — datos de tiempo
Cubierto por P1.0/P1 (declarar redondeo al alza + cota de sensibilidad; números reales).
**Constancia (2026-10-19)**: T5 queda cubierto por las tareas 2.1, 2.2 y 3.2 de c-76 (P1.0/P1); no requiere requisito nuevo, solo referencia.

### T6. Caps 4.2, 4.4, 4.5, 11.5 — anti-Hawthorne incompatible con la ventana temporal
- 4.2 (l.16): observación naturalista, operador no informado de ser cronometrado.
- 4.4 (l.43): población = trimestre jul–sep 2025; muestreo estratificado de 200 (82/64/54 → stale).
- 4.5 (l.53): el flujo automatizado corrió en "una ventana operativa controlada de **tres días hábiles consecutivos**".
- 11.5 (l.28): observación naturalista + debriefing.
- Incompatibilidades: (a) trimestre (jul–sep) vs "tres días hábiles"; (b) observar sin que el operador sepa, durante un trimestre, con cronometraje en vivo por un par, es inconsistente; (c) el diseño pareado (mismos 200 casos manual+auto) exige que ambas condiciones cubran el mismo conjunto/ventana.
- Fix: unificar la ventana temporal real y reconciliar la afirmación anti-Hawthorne con el procedimiento efectivo.
- **Ventana real (confirmada por el autor, 2026-10-09)**: flujo manual **jun–ago 2026**; automatizado **sep–oct 2026**. La tesis dice "jul–sep **2025**" (año y meses erróneos) y "tres días hábiles" (erróneo). El diseño es secuencial pareado, no simultáneo.

### T7. Caps 4.2, 4.6, 7.3 — 3 relatos incompatibles del instrumento de medición manual
- 4.2 (l.16): "planilla de cronometraje" en vivo por el par; valores "**estimados** y redondeados a múltiplos de 5 s y **unos pocos con exactitud al segundo**".
- 4.6 (l.59): "planilla de cronometraje observacional" en vivo por el par; "la mayoría redondeados a múltiplos de 5 s, **sin fracciones**".
- 7.3 (`07-resultados.tex` §Reducción de la intervención humana, l.84): deriva la "intervención humana" de la planilla del flujo manual (remite a 4.6).
- Incompatibilidades: "estimados" (4.2) vs "cronometrados/redondeados" (4.6); "exactitud al segundo" (4.2) vs "sin fracciones" (4.6); la planilla mide tiempo **manual**, no la intervención del flujo **automatizado** (7.3).
- Fix: unificar el relato del instrumento y no derivar la intervención del flujo automatizado de la planilla manual.

---

## Notas

- **Decisiones OQ (c-77, 2026-10-09)**: OQ1=c (rank-biserial directo `r=(T+−T−)/(n(n+1)/2)`), OQ2=c (retirar la sub-pregunta de exactitud humana y reformular H1), OQ3=b (reescribir 6.5 como limitación), OQ4=a (redacción condicional Nginx/TLS), OQ5=b (alinear tesis a 5 sectores), OQ6=diferido (tag).
- **Acción diferida (OQ6)**: al **terminar** las correcciones (c-76 + c-77), crear el tag **`v1.0.0`** sobre el commit entregado al jurado y consignar el **hash completo** en el Anexo B de la tesis.
- Este registro es acumulativo. Las correcciones que dependan de decisiones o de
  trabajo mayor (reescritura de capítulos) quedan en "Pendientes" hasta aplicarse.

---

## Grupo: Bibliografia y atribucion (B1-B3)

Correcciones del plan de auditoria §16.3, items 22-24. Change propuesto: **c-78-tesis-bibliografia-atribucion** (governance HIGH). Verificado contra `docs/Tesis/v9 (IA)/paper/sections/` y `docs/Tesis/v9 (IA)/Bibliography_base.bib` el 2026-10-10.

### B1 (item 22) — Misatribucion de Revina, Buza & Meister (2020)

- **Archivos**: `03-estado-del-arte.tex:28` (§3.3) y `08-discusion.tex:20,22` (§8.2).
- **Claim falso en la tesis**: atribuye a Revina et al. (2020) el uso de arquitecturas basadas en BERT, una exactitud ~91 % y la conclusion de que los modelos preentrenados transfieren conocimiento al dominio de tickets sin ajuste fino.
- **Evidencia verificada** (PDF open-access + abstract): el titulo real es **"IT Ticket Classification: The Simpler, the Better"** (IEEE Access, vol. 8, pp. 193380-193395, 2020, DOI 10.1109/ACCESS.2020.3032840). La palabra "BERT" aparece **CERO** veces; **no** usa transformer ni modelo preentrenado. Compara TF-IDF contra rasgos linguisticos artesanales alimentando clasificadores clasicos (kNN, arboles de decision, naive Bayes, regresion logistica, SVM, semi-supervisado) para predecir la **complejidad** del ticket (baja/media/alta), **no** la categoria. Su conclusion es la opuesta a la tesis: los metodos simples y explicables con pocos rasgos linguisticos ganan. Cita textual sobre embeddings preentrenados: *"pre-trained models would not perform well considering the domain-specific vocabulary which contains many new words compared to the training corpus"*. Otras: *"even simple algorithms can deliver high-quality prediction when using appropriate linguistic features"*; *"we recommend using those classifiers which do not demand complex parameter search and are simple and cheap to implement"*. **No aparece ningun "91 %"** en el cuerpo; la unica exactitud en prosa es un 62 % previo de reglas de los mismos autores.
- **Correccion**: reescribir §3.3 y §8.2 con la conclusion real; presentar a Revina et al. como evidencia de que los metodos simples/explicables con rasgos del dominio son competitivos y que los embeddings preentrenados pueden rendir peor por vocabulario de dominio; incorporar la tension en el cap. 8 (la evidencia contraria fortalece la discusion).

### B2 (item 23) — Modernizacion del estado del arte (2023-2026)

- **Claim sin cita #1**: `08-discusion.tex:20` afirma "88 % a 94 % de exactitud" **sin cita**.
- **Claim sin cita #2**: `03-estado-del-arte.tex:30` afirma sobre la literatura few-shot reciente **sin cita**.
- **Correccion**: incorporar **al menos 12** articulos arbitrados 2023-2026 (listado y BibTeX verbatim en `openspec/changes/c-78-tesis-bibliografia-atribucion/design.md`, Anexo A) cubriendo (a) clasificacion de tickets / mesa de servicio con LLM, (b) evaluacion zero-shot/few-shot multilingue, (c) LLM en espanol / Iberoamerica. Citar evaluaciones concretas o retirar/reformular los dos claims.
- **Brecha declarada**: NO existe articulo arbitrado 2023-2026 que evalue Google Gemini sobre tickets de soporte en espanol. Se declara como brecha / parte de la contribucion; **no se fabrica** una referencia.

### B3 (item 24) — Higiene de citas y atribucion

- **Landis & Koch (1977)**: agregar a la bibliografia **Landis, J. R., & Koch, G. G. (1977). The Measurement of Observer Agreement for Categorical Data. Biometrics, 33(1), 159-174. DOI 10.2307/2529310**. Los rangos interpretativos de Kappa que la tesis atribuye a Cohen son de Landis & Koch. Con \(\kappa = 0{,}87\) el rotulo correcto es **"casi perfecto"**, no "sustancial". Corregir §4.4 (`04-marco-metodologico.tex:47`) y §4.8 ("Amenazas a la validez", `:79`).
- **`Stallings2017_computer_security`**: agregar co-autor **Lawrie Brown** (4ta ed. de "Computer Security: Principles and Practice" es de Stallings & Brown).
- **`OGC2011_itil`**: quitar el campo `edition = {2011}`; la publicacion de *ITIL Service Operation* (2011) es de **The Stationery Office (TSO)** por encargo del Office of Government Commerce; ITIL pertenece hoy a la herencia AXELOS. Se conserva `author = {{Office of Government Commerce}}` y se agrega nota de titularidad.
- **`Jurafsky2023_speech_language`**: la editorial **NO** es Pearson (la 2da edicion si lo era). El borrador de la 3ra edicion es autopublicado / **Stanford University**. Corregir `publisher` y `note`.
- **Estilo "et al."**: normalizar la coma antes del ano segun APA ("Revina et al., 2020", no "Revina et al. 2020") donde la tesis se desvie. El preambulo usa `biblatex` `style=apa`, que ya la aplica; auditar el PDF compilado.
- **Citas huerfanas — RESUELTO (2026-10-10)**: las dos citas huerfanas reportadas por la auditoria estaban en la version **v7** (la version auditada) y eran **Karchhud, R., Singh, A., & Patel, M. (2024)** ("Few-shot ticket classification with large language models: A multilingual evaluation", JISEM 9(2), 145-168) y **Mehdi, S., Kapoor, A., & Larsson, J. (2023)** ("The state of AI in customer support: Industry adoption survey 2020-2023", International Journal of Service Operations Management 45(3), 211-234). Ambas fueron **verificadas como FABRICADAS**: Crossref y OpenAlex devuelven cero resultados para los autores y los titulos; el journal JISEM (ISSN 2468-4376) existe pero el articulo no; en el segundo caso el propio nombre del journal es un **near-miss** del real "International Journal of Services and Operations Management" (ISSN 1744-2389). Firma tipica de alucinacion: journal real plausible + autores/articulo imposibles + venue near-miss. Ambas ya fueron **retiradas entre v7 y v9**, por lo que el arbol v9 tiene **cero citas huerfanas y cero entradas sin usar** (33/33, verificado por `verify_citations.py` y por la comparacion de `paper/main.bcf` contra el `.bib`). El change c-78 MUST NOT reintroducirlas y MUST re-citar/reformular/retirar las dos afirmaciones que sostenian (rango "88 % a 94 %" en `08:20`; adopcion de IA en `03:12`). Como las fabricaciones suelen agruparse, c-78 MUST re-verificar **todas** las entradas restantes del `.bib` contra resolucion por DOI/URL y retirar o reemplazar cualquiera que no resuelva.
- **Fuera de alcance**: item 25 (legal, §11.2) NO pertenece a este grupo.

**Re-verificacion de integridad (2026-10-10)**: se re-verificaron por DOI/landing page las 33 entradas de `docs/Tesis/v9 (IA)/Bibliography_base.bib`. Resultado: **31 REAL, 2 metadatos erroneos, 0 fabricadas**. Las 2 con metadatos erroneos son `Stallings2017_computer_security` (falta el co-autor Lawrie Brown) y `Jurafsky2023_speech_language` (sobra `publisher = {Pearson}`), exactamente las dos ya en alcance de c-78. Las 2 fabricadas de v7 (Karchhud 2024, Mehdi 2023) estan ausentes en v9. `OGC2011_itil` es correcto como esta escrito (ITIL 2011 fue OGC/TSO; AXELOS asumio recien en 2013); el DOI de Landis & Koch (10.2307/2529310) resuelve correctamente.

**Estado de aplicacion de c-78 (2026-10-19)**: change **c-78-tesis-bibliografia-atribucion** APLICADO (grupos 1-3 y 4-6). El `.bib` paso de **33 a 46 entradas**. Evidencia:

- **B1 (item 22) — Revina, Buza & Meister (2020)**: corregido. La clave se renombro `Revina2020_bert_tickets` → **`Revina2020_it_tickets`**. §3.3 (`03-estado-del-arte.tex`) y §8.2 (`08-discusion.tex`) reescritos con la conclusion real: los metodos simples y explicables con rasgos linguisticos del dominio son competitivos y los embeddings preentrenados pueden rendir peor por vocabulario especifico del dominio. El titulo real ("IT Ticket Classification: The Simpler, the Better") y el DOI **10.1109/ACCESS.2020.3032840** se conservan (resuelven en Crossref). Ya no queda "BERT" ni "91 %" atribuido a Revina.
- **B2 (item 23) — Modernizacion del estado del arte**: 12 entradas arbitradas 2023-2026 agregadas al `.bib`, cubriendo clasificacion de tickets/mesa de servicio con LLM, evaluacion zero-shot/few-shot multilingue y LLM en espanol/Iberoamerica. Claves agregadas: **`ahuja2023mega`, `lai2023okapi`, `zhang2023multilingual`, `xuan2025mmluprox`, `grandury2025laleaderboard`, `mayorrocher2026spanish`, `bernalbeltran2025mexicanspanish`, `ramonferrer2026tripletotext`, `paket2024itservice`, `liu2025tickit`, `zangari2023ticket`, `colavito2025benchmarking`**. Todas con DOI verificado por Crossref (ACL Anthology para las de `10.18653/*`). Los dos claims sin cita ("88 % a 94 %" en `08:20`; literatura few-shot en `03:30`) fueron reemplazados por citas concretas. La brecha declarada (no existe articulo arbitrado 2023-2026 que evalue Gemini sobre tickets de soporte en espanol) quedo asentada, sin fabricar referencia.
- **B3 (item 24) — Higiene de citas**: `Landis1977_kappa` agregada (DOI **10.2307/2529310**, Biometrics 33(1), 159-174); los rangos interpretativos de kappa se citan a Landis & Koch y \(\kappa = 0{,}87\) se rotula **"casi perfecto"** (ya no "sustancial"). `Cohen1960_kappa` queda solo para la definicion del coeficiente. `Stallings2017_computer_security` con co-autor **Lawrie Brown**; `OGC2011_itil` sin `edition = {2011}` con nota de titularidad AXELOS/PeopleCert; `Jurafsky2023_speech_language` con `publisher = {Stanford University}` y nota de borrador de 3ra edicion.
- **Citas huerfanas fabricadas — retiradas**: **Karchhud 2024** y **Mehdi 2023** estan ausentes del arbol v9 (`B` y `S`); la unica mencion en el arbol es el docstring de `verify_citations.py` que advierte sobre ellas. Guardia de no reintroduccion verificada.
- **Re-verificacion de las 46 entradas (2026-10-19)**: 22 con DOI resueltas (21 Crossref + `Touvron2023_llama2` via DataCite); 24 sin DOI verificadas por landing de editorial/ACL (URLs HTTP 200; unica excepcion `Ley25326_2000` con HTTP 403 = bloqueo anti-bot de InfoLeg, no enlace muerto). **46/46 resuelven, 0 fabricadas, 0 sin resolver.**
- **Verificacion de citas**: `verify_citations.py` → `46 bib entries, 46 unique keys cited, 76 total citation commands, Orphan citations: 0, Unused entries: 0, STATUS: PASS`. El `.bcf` en repo es un artefacto obsoleto (julio) y solo se regenera al recompilar (diferido a Overleaf, XeLaTeX).

---

## Item 25 (plan de auditoria) — Aspectos legales (11.1-11.3)

Change propuesto: **c-79-tesis-aspectos-legales** (governance HIGH). Verificado contra `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex`, `docs/cumplimiento/marco-legal-ar-2026.md` y `docs/runbook-verificacion-telefonia-c52.md` el 2026-10-12.

### L1 (item 25) — Plazo de conservacion contradictorio
- `11-aspectos-legales.tex:12` (§11.2) anuncia "el principio de limitacion del plazo de conservacion" y acto seguido afirma **"conservacion indefinida"** para incidentes: autocontradictorio, sin plazo concreto.
- Inconsistencia con `05-arquitectura.tex:44` ("30 dias" para logs de ejecucion). Historia: `11-aspectos-legales.tex.bak:12` y `knowledge-base/10_preguntas_abiertas.md` (IN-05) documentan la politica previa "90 dias / 1 ano" reemplazada por C-18.
- El bloqueo de escritura de tickets cerrados (PATCH 409, C-23) es control de integridad, no politica de retencion.
- **Accion**: fijar UN plazo concreto y justificado, consistente entre §11.2 y 05-arquitectura. El valor exacto es decision del autor (OQ-L1).

### L2 (item 25) — Base legal: art. 5 inc. 2 Ley 25.326
- `11-aspectos-legales.tex:12` funda el tratamiento en el **"legitimo interes de la organizacion"**. "Legitimo interes" es concepto GDPR (art. 6.1.f) que **NO existe** como base autonoma en la Ley 25.326.
- Base correcta (investigacion propia del proyecto): art. 5 inc. 2, apartado b) (obligacion legal / funciones del Estado) o d) (relacion contractual/cientifica/profesional) — `marco-legal-ar-2026.md:552-554`, `docs/seguridad/registro-requisitos-legales.md:25`. La tesis nunca cita art. 5 inc. 2.
- **Accion**: reemplazar "legitimo interes" por la base del art. 5 inc. 2 (apartado exacto = OQ-L2).

### L3 (item 25) — Decision de adecuacion europea
- `11-aspectos-legales.tex:8` (§11.1) dice "Argentina mantiene un regimen de adecuacion ... lo cual facilita los flujos transfronterizos **bidireccionales**": sin cita y enganoso.
- Correcto: **Decision 2003/490/CE** (30/06/2003) + revalidacion **enero 2024**; cubre **UE→AR SOLO**, no habilita **AR→EE.UU.** (transferencia real via Gemini/Twilio) — `marco-legal-ar-2026.md:37-39, 369-391, 538-542`.

### L4 (item 25) — Transferencia telefonica pre-pseudonimizacion
- `11-aspectos-legales.tex:16` (§11.3) afirma "pseudonimizacion previa a la transmision" y **solo** trata Gemini; **nunca menciona Twilio**.
- Es **falso** para telefonia: el **audio crudo** y el numero del llamante cruzan a EE.UU. (Twilio) **antes** de pseudonimizar (el pseudonimizador es un regex de texto en el backend, posterior) — `docs/runbook-verificacion-telefonia-c52.md:13`.
- El DPA ("acuerdo de procesamiento de datos") **no sustituye** el instrumento del art. 12 (consentimiento o Clausulas Contractuales Modelo, DNPDP 60/2016 / Res. AAIP 198/2023).
- **Accion**: nombrar Twilio, declarar la transferencia pre-pseudonimizacion del audio + numero, y citar el instrumento del art. 12.

### L5 (item 25) — (opcional) Plazo ARCO
- La tesis no fija plazo para rectificacion/supresion. El art. 16 exige **CINCO DIAS HABILES** — `marco-legal-ar-2026.md:230-232, 550-551` (OQ-L5).

---

## Grupo: Aspectos legales (L1-L6) — APLICADO (revision legal 2026-10-19)

Change **c-79-tesis-aspectos-legales** (governance HIGH). Aplicado sobre
`docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex` (§11.1-§11.3),
`05-arquitectura.tex:44` y este registro. Los valores de OQ-L1/L1b/L2/L5
(resueltos 2026-10-12) se aplicaron tal cual; la revision de vigencia de fuentes
(L6) se realizo el **2026-10-19**.

### L1 — Plazo de conservacion y politica de supresion
- §11.2: "conservacion indefinida" → **12 meses rodantes desde la creacion del
  incidente**, justificado por el ciclo estadistico anual. El texto declara el
  periodo, no fechas calendario.
- Reconciliacion con `05-arquitectura.tex:44`: se declara de forma explicita que
  los registros de ejecucion (30 dias, auditoria/diagnostico) y los incidentes
  (12 meses) son **conjuntos de datos distintos** con finalidades distintas y
  plazos propios; se agrego la remision a §11.2 en 05:44.
- Bloqueo de escritura sobre tickets cerrados (PATCH → 409, C-23): presentado como
  **control de integridad de auditoria**, NO como politica de retencion ni
  excepcion permanente al vencimiento.
- Disposicion al vencimiento: **anonimizacion irreversible**.
- Verificacion: `rg -ni "conservaci[oó]n indefinida"` en el `.tex` vivo → 0
  coincidencias en 11.1-11.3.

### L2 — Base de licitud (Ley 25.326 art. 5 inc. 2)
- §11.2: "legitimo interes de la organizacion" → **Ley 25.326, art. 5, inc. 2,
  apartado d)** (relacion contractual/cientifica/profesional; la organizacion es
  la empleadora). NO apartado b).
- Se dejo constancia de que el deber de informacion del art. 6 subsiste y que el
  consentimiento solo se discute para el corpus de investigacion (§11.5).
- Verificacion: `rg -ni "leg[ií]timo inter[eé]s"` → 0 coincidencias.

### L3 — Adecuacion europea (instrumento y direccion)
- §11.1: cita **Decision 2003/490/CE (30 de junio de 2003)** y su **revalidacion de
  enero de 2024**; direccion corregida: **UE -> Argentina unicamente**; se elimino
  "bidireccionales".
- Se declara que **EE. UU. no es pais adecuado** y que la transferencia hacia
  EE. UU. (Gemini, Twilio) requiere instrumento del art. 12.
- Verificacion: `rg -ni "bidireccional"` → 0 coincidencias.

### L4 — Transferencia telefonica previa a la pseudonimizacion
- §11.3: se nombra a **Twilio** (EE. UU.) y se declara que el **audio crudo del
  llamante y su numero** se transfieren a EE. UU. **antes** de cualquier
  pseudonimizacion (orden: grabar -> transferir/transcribir -> pseudonimizar).
- Se cita el instrumento del art. 12 (consentimiento o clausulas contractuales
  modelo) y se aclara que el DPA es **complemento, no sustituto**.
- Verificacion: `rg -ni "pseudonimizaci[oó]n previa a la transmisi[oó]n"` → 0
  coincidencias.

### L5 — Plazo ARCO
- §11.2: el plazo de rectificacion/actualizacion/supresion se declara como **cinco
  dias habiles** (art. 16). No se usa "cinco dias corridos".
- Nota de alcance: el plazo se declaro en §11.2 (dentro del alcance 11.1-11.3);
  §11.5 (c-76/c-77) no se modifico.
- Verificacion: `rg -ni "d[ií]as corridos"` → 0 coincidencias.

### L6 — Revision de vigencia de fuentes juridicas (2026-10-19)
- Normas revisadas y vigentes a la fecha: Ley 25.326 (2000) y su decreto
  reglamentario; AAIP como autoridad de aplicacion; RGPD (UE 2016/679); Decision
  2003/490/CE (revalidada en enero de 2024); instrumentos de transferencia del art.
  12 (Disposicion DNPDP 60/2016, Resolucion AAIP 198/2023, Resolucion AAIP
  159/2018). Fuente: `docs/cumplimiento/marco-legal-ar-2026.md` (la Ley 25.326
  sigue vigente en 2026; no se sanciono reforma integral).
- **No se cita ninguna norma superada o derogada** en 11.1-11.3.
- **Fecha de la revision legal: 2026-10-19.** Resultado: control de vigencia OK.

---

## Grupo: Forma y evidencia visual (Bloque 4, items 26-32)

Change propuesto: **c-80-tesis-forma-evidencia-visual** (governance BAJO). Verificado contra `docs/Tesis/v9 (IA)/paper/sections/` el 2026-10-12. **Depende de c-76/c-77/c-78** (comparte `08-discusion.tex` y `09-conclusiones.tex`; aplicar despues).

### F1 (item 26) — Ortografia
- 52 ocurrencias de 4 formas; **50 son errores**. `desarrolló` aparece 11 veces pero **2 son verbos legitimos** (`00-resumen.tex:11`, `06-implementacion.tex:87`) — sustitucion **contextual**, no ciega. La forma real es `diseñó` (con ñ), no `disenó`.
- Portada (`00-portada.tex`) y titulos de seccion sin tildes (TECNOLOGICA, Programacion, Automatizacion, Tecnico, Republica, Introduccion, etc.).

### F2 (item 27) — Figuras
- Hoy hay **1 sola** figura (`05-arquitectura.tex:31-36`). Faltan las **8** pedidas: despliegue, secuencia correo, ER, captura flujo N8N, captura panel admin, captura dashboard, boxplot de tiempos, matriz de confusion.
- Fuentes Mermaid sin embeber: `docs/diagrams/despliegue.md`, `secuencia.md`, `componentes.md`.

### F3 (item 28) — Anexos
- `12-anexos.tex`: 7 `\section` = Anexos A-G, **todos descriptivos/placeholder** sin contenido embebido (hay `docs/anexo_c_esquema_bd.md`, `docs/openapi.json`, el export N8N, el corpus JSON, la doc operativa, pero no se incluyen).
- **Anexo H** (`docs/anexo_h_prompt_gemini.md`, 208 lineas) **no esta en la tesis** (0 referencias en `.tex`).

### F4 (item 29) — Fuente de tablas
- 9 tablas; `\small` en **4/9** (si: tab:comparativa, tab:variables, tab:entidades, tab:errores; no: tab:capas, tab:api, tab:tiempos, tab:matriz, tab:metricas). Tablas 1 (`03-estado-del-arte.tex:36`) y 3 (`05-arquitectura.tex:12`) difieren en fuente y composicion de columnas.

### F5 (item 30) — Duplicaciones (~900 palabras)
- 1.1/2.1 (`01-introduccion.tex:8,10` ↔ `02-marco-teorico.tex:10,12`), 5.3/6.3 (`05-arquitectura.tex:44,60` ↔ `06-implementacion.tex:39,41,44`), 8.1/9.1 (`08-discusion.tex:8,10,14` ↔ `09-conclusiones.tex:12,24`).

### F6 (item 31) — Nota obsoleta N8N "1.62 / Docker Hub"
- `05-arquitectura.tex:21` y `06-implementacion.tex:10`. Contradice "N8N 2.11.2" de `12-anexos.tex:37` y `docs/diagrams/despliegue.md`. Retirar y reconciliar la version.

### F7 (item 32) — Afirmaciones valorativas sin respaldo
- `08-discusion.tex:8-16` ("superan ampliamente", "valida la hipotesis subsidiaria", "consecuencia deseable", "garantia metodologica que no todos los trabajos...").
- `09-conclusiones.tex:6-18` ("cumplido satisfactoriamente", "supero con holgura", "no deja espacio para la duda razonable", "resultado poco frecuente en la investigacion aplicada", "trasciende lo meramente estadistico").
- Rebajar a formulaciones respaldadas por la evidencia de `07-resultados.tex`.

---

## Plan de auditoria — cobertura por change (actualizado 2026-10-12)

Con c-79 y c-80, **los 32 items del plan de auditoria quedan cubiertos por un change**:

| Bloque del plan | Items | Change | Governance |
|---|---|---|---|
| 1 (brecha probatoria) | 1-6 | c-76 | — |
| 2 (estadistica/metodologia) | 7-14 | c-77 (+ c-76 T1-T7) | — |
| 3 (documento/artefacto) | 15-21 | c-76 / c-77 | — |
| 3 (bibliografia y atribucion) | 22-24 | c-78 | HIGH |
| 3 (legal, §11.2) | 25 | **c-79** | HIGH |
| 4 (forma y evidencia visual) | 26-32 | **c-80** | BAJO |

Ninguno de los seis changes esta aplicado todavia (0 tareas). Orden recomendado de aplicacion: c-76 -> c-77 -> c-78 -> c-79 -> c-80 (c-80 al final por compartir archivos con c-76/c-77).

---

## Nueva auditoria (2026-10-19) — cobertura por change (FASE 31)

La nueva auditoria es capitulo por capitulo: el texto vivo esta en
`docs/Tesis/Correcciones/auditoria-capitulos.md` y el informe completo, en
`auditorias/Auditoria_Tesis_Gomez_Bustos_Sevilla_040802026.pdf`. Reporta **105
hallazgos: 28 criticos / 34 altos / 29 medios / 14 bajos**. El cruce con los
changes existentes esta en `docs/Tesis/Correcciones/reconciliacion-cobertura.md`.
Cinco changes nuevos (FASE 31) cubren los hallazgos A/M/B que C-76..C-80 no
abordan; todos `openspec validate --strict` OK y sin aplicar (0 tareas).

### Cobertura de los hallazgos NUEVOS (A/M/B) por change

| Change | Governance | Capitulo | Hallazgos cubiertos |
|---|---|---|---|
| `c-92-tesis-marco-teorico-profundidad` | MEDIO | Cap 2 | A-04, A-05, M-03, M-04 (+ M-02 y A-06 parciales) |
| `c-93-tesis-metodologia-rigor` | MEDIO | Cap 4 | A-07, A-08, A-09, A-10, M-05, M-06, M-07, A-03 |
| `c-94-tesis-implementacion-verificabilidad` | MEDIO | Caps 5-6 | A-11, A-12, A-13, M-08, M-09, M-12, M-13 |
| `c-95-tesis-resultados-discusion-rigor` | MEDIO | Caps 7-8 | A-15, A-20, A-21, M-10, M-16 (+ A-23 y A-25 parciales) |
| `c-96-tesis-citas-tablas-evidencia` | BAJO | Cap 3 / transversal | A-26, M-01 + cita huerfana APA 2017, A-27, B-01 (+ fuente de las 9 tablas, densidad de citas) |

Detalle por hallazgo:

| Codigo | Hallazgo | Change |
|---|---|---|
| A-03 | Tercer criterio del umbral 85 % de §1.6 (zona de rechazo inexistente) | c-93 |
| A-04 | §2.4 eje LLM en cuatro parrafos; sin prompting/calibracion/alucinacion/idioma/evaluacion | c-92 |
| A-05 | §2.7 define exactitud con formula binaria y la corrige al lado | c-92 |
| A-06 | §2.2 atribucion editorial de ITIL Service Operation 2011 (parcial; `.bib` en c-78 B3) | c-92 |
| A-07 | §4.4 margen/tamaño muestral no reproduce n=200 | c-93 |
| A-08 | §4.5/§6.7 cobertura de pruebas sin informe ni comando | c-93 |
| A-09 | Sin analisis de potencia a priori | c-93 |
| A-10 | §4.2 rotacion de operadores confundida con el efecto de operador | c-93 |
| A-11 | §6.7 pruebas e2e de N8N inexistentes | c-94 |
| A-12 | §6.7 recuento/cobertura de la suite frontend no reproducibles | c-94 |
| A-13 | §6.4 latencia telefonica 12-15 s no atribuible (C-17) | c-94 |
| A-15 | Sin estadistico ni p de Shapiro-Wilk (§4.7) | c-95 |
| A-20 | §8.1 interpreta y no interroga; sin hipotesis alternativa | c-95 |
| A-21 | §8.3 baseline TF-IDF+SVM sin procedimiento ni codigo | c-95 |
| A-23 | §9.2 generaliza superioridad de LLM sobre clasificadores supervisados (parcial) | c-95 |
| A-25 | §9.1 interpretacion estadistica (Wilcoxon) en conclusiones (parcial) | c-95 |
| A-26 | Tabla 1 (Cap 3) sin fuente, citas ni fecha; fila "Propuesta" autoevaluada | c-96 |
| A-27 | §1.7 y §6.1 rotulan a N8N como "codigo abierto" | c-96 |
| M-01 | §1.1 cita huerfana: SEPyME define "empresa mediana" | c-96 |
| M-02 | §1.7 corpus EN/DE/PT sin respaldo (parcial; reutiliza refs de c-78) | c-92 |
| M-03 | §2.5 Whisper detallado sin correlato en el artefacto (usa Twilio) | c-92 |
| M-04 | §2.6 justifica PostgreSQL sin alternativas concretas | c-92 |
| M-05 | Sin criterios de exclusion de incidentes del corpus | c-93 |
| M-06 | §4.9 Scrumban es gestion de proyecto, no metodologia | c-93 |
| M-07 | No se declaran los dos analistas etiquetadores del corpus | c-93 |
| M-08 | §6.8 ejemplo hipotetico presentado como "caso concreto" (parcial) | c-94 |
| M-09 | §6.1 "migracion a Kubernetes 1.30" sin manifiesto | c-94 |
| M-10 | §7.4 tipifica 16 errores sin un ejemplo textual | c-95 |
| M-12 | §5.4 parametros de inferencia "optimizados" sin procedimiento | c-94 |
| M-13 | Tabla 5 incompleta vs API real | c-94 |
| M-16 | §8.4 costos (50-100 USD/mes; 0,02 USD/invocacion) sin fuente | c-95 |
| B-01 | §1.2/§1.8 organizacion adoptante inconsistente | c-96 |
| — | Cita huerfana "(APA, 2017)" en §11.5 | c-96 |
| — | Fuente APA 7 ausente en las 9 tablas; densidad de citas desigual | c-96 |

### Criticos C-01..C-28

Los 28 criticos del informe completo ya tienen owner en C-76..C-80 (26 CUBIERTO,
2 PARCIAL: C-17 y C-21); no quedan criticos huerfanos. El mapeo detallado esta en
`reconciliacion-cobertura.md` (seccion 2).

### C-18 — STALE

C-18 (el canal de origen nunca llega al backend) describia el flujo PREVIO a
c-29. El artefacto ya fue corregido por c-29 (commit `ef656ac`, 2026-09-17): el
POST envia seis campos incluido `canal_origen_id` y el Switch esta en modo
`rules`. Es un hallazgo stale de software. Residuo: solo el texto de la tesis
(Tabla 4 usa `id_canal`; §5.3 describe dos llamadas), ya asignado a **c-77 C3**.
No requiere change de software.

### Drift del HEAD

La auditoria se hizo sobre el commit `d7df92c` (2026-07-02); el repositorio
evoluciono. Los conteos del informe estan stale respecto del HEAD (136 archivos
`test_*.py` en backend, 56 archivos de prueba frontend con 340 `it(`, 33 rutas
en `docs/openapi.json`). Las tareas de c-94 exigen re-medir en HEAD, no
hardcodear (A-11, A-12, M-13).

### A-19 — requiere re-verificacion

La auditoria afirma que §5.6 anuncia "seis entidades" frente a "cinco tablas" del
Anexo C. El `.tex` en HEAD (`05-arquitectura.tex:64`) dice **"siete entidades
principales"** y la `tab:entidades` (Tabla 4) lista **siete**, incluida
`directorio_empleado`. La premisa "seis vs cinco" no coincide con el `.tex`
actual: requiere re-verificacion antes de corregir. c-80 mantuvo 7 y lo
documento.

Ademas hay conflictos internos entre changes a resolver antes de aplicar (c-80
debe usar la matriz 5x5 real de c-76 y fijar el numero real de entidades), ver
`reconciliacion-cobertura.md` seccion 4.

---

## Grupo: Resultados y Discusión (c-95) — APLICADO (2026-10-19)

Change **c-95-tesis-resultados-discusion-rigor** (governance MEDIO). Aplicado sobre
`docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex`, `07-resultados.tex`,
`08-discusion.tex`, `09-conclusiones.tex` y `evaluation/report.md`. Se aplico
**despues** de c-76, c-77, c-78 y c-80 (D-ORDER): comparte `04`, `07`, `08` y `09`
con esos changes.

### Mapeo de hallazgos y corrección aplicada

| Código | Corrección aplicada | Archivos | Fecha |
|---|---|---|---|
| A-15 | Shapiro-Wilk reportado con \(W\) y \(p\) para los tres conjuntos (\(n=200\)): manual \(W=0{,}803\), \(p=3{,}71\times10^{-15}\); automatizado \(W=0{,}902\), \(p=3{,}47\times10^{-10}\); diferencias \(W=0{,}822\), \(p=2{,}37\times10^{-14}\). Justifica Wilcoxon con \(\alpha=0{,}05\). | `04:69`, `evaluation/report.md` (§Normalidad), ref. breve en `07:50` | 2026-10-19 |
| A-20 | §8.1 ya no interpreta sin interrogar: agrega explicaciones rivales (asimetría del instrumento, mezcla de canales, Hawthorne/aprendizaje, selección muestral) con evidencia, debilidad y condición de descarte; nota de confusión de Sistemas con métricas reales y \(n=1\) en Bases de Datos; cierre que distingue "consistente con la hipótesis" de "confirmación concluyente". | `08:20`, `08:22`, `08:24` | 2026-10-19 |
| A-21 | El baseline TF-IDF+SVM de §8.3 se declara chequeo exploratorio no reproducible (partición y \(n\) no preservados) y NO se reporta como comparación válida; la cifra 78~\%/0,764 se retira como resultado y la comparación sistemática queda como trabajo futuro. | `08:48` | 2026-10-19 |
| M-10 | §7.4 incorpora tres ejemplos textuales anonimizados de casos mal clasificados (descripción corta, mezcla de categorías, jerga local), con sector asignado, predicho y confianza. | `07:198` | 2026-10-19 |
| M-16 | §8.4 reemplaza las cifras desnudas (50--100 USD/mes; 0,02 USD/invocación) por cotas con fuente y fecha: infraestructura 24--32 USD/mes (precio de lista DigitalOcean, 19-10-2026) e inferencia \(\approx 7\times10^{-4}\) USD por invocación con `gemini-3.6-flash`. | `08:56` | 2026-10-19 |
| A-23 | §9.2 acota la afirmación general: la conclusión se limita "a este corpus" y "a este dominio", se conserva el aporte real (arquitectura híbrida, español rioplatense, dominio de mesa de ayuda) y se remite a la limitación de §8.3. Se retira la superioridad general de LLM sobre clasificadores supervisados entrenados sobre representaciones estáticas. | `09:22` | 2026-10-19 |
| A-25 | §9.1 mantiene solo una referencia breve al resultado (188/200 pares; 9,5~\% de intervención humana) y remite a §7.1/§8.1. Se retira la lectura "merece ser interpretada con cautela" y no se introducen estadísticos ausentes del Capítulo 7. | `09:16` | 2026-10-19 |

Verificación (2026-10-19): `rg` de control en `S/` sin las formulaciones
retiradas (salvo el \(W=0{,}803\) de Shapiro, que es un estadístico lícito);
`openspec validate c-95-tesis-resultados-discusion-rigor --strict` OK.

### D3 — Decisión: baseline TF-IDF+SVM exploratorio, no reproducible (no reconstruido)

- **Decisión**: el chequeo exploratorio con un clasificador TF-IDF+SVM (78~\%, F1
  0,764) **no se reconstruye** y **no se reporta** como comparación válida. La
  partición, el tamaño del subconjunto y el código no quedaron preservados, por lo
  que la cifra no es reproducible ni comparable con las métricas del Capítulo 7.
- **Justificación**: confirmado por barrido que **no existen artefactos** del
  baseline (script, partición, predicciones ni fixtures) en `evaluation/`,
  `scripts/` ni `data/`; la única coincidencia en código es la tabla interna
  "Baseline / policy-B" de `evaluation/deterministic_measurement.py` (delta de
  c-74), ajena al clasificador supervisado clásico. Sin artefactos, presentar la
  cifra como resultado sería una afirmación no reproducible.
- **Consecuencia**: §8.3 (Limitaciones) declara el chequeo como exploratorio y deja
  la comparación sistemática contra clasificadores supervisados sobre el corpus
  completo como trabajo futuro, sin prometer resultados.

### Coordinación con c-76, c-77, c-78 y c-80

- **c-76** (números y encuadre honesto): c-95 consume los valores ya corregidos
  (exactitud 73,5~\%, F1 macro 0,5207, reducción 71,2~\%, segundo objetivo NO
  alcanzado) y no los redefine. A-15 solo agrega el reporte de Shapiro.
- **c-77** (\(W=0\), calibración): c-95 **no reintroduce \(W=0\)**. El valor vivo es
  \(W=363\), \(p=3{,}08\times10^{-32}\), \(r=0{,}9639\) (§7.1/§0-resumen). §9.1 ya no
  reinterpreta el \(W\); su lectura queda en §7.1 y §8.1. La tabla
  `tab:tiempos-canal` de c-77 se conserva en §7.1.
- **c-78** (Revina y atribución): c-95 **no reintroduce ni la atribución de BERT/91~\%**
  **a Revina** ni la tensión bibliográfica B1; §9.2 no menciona "Revina", "BERT" ni
  "evidencia contraria". La única mención a Revina en el texto vivo es la correcta
  de §8.2, propiedad de c-78.
- **c-80** (deduplicación 8.1/9.1 y rebaja de juicios): c-95 respeta la rebaja de
  c-80 F7 y no duplica frases valorativas; A-25 elimina la última lectura
  interpretativo-estadística que quedaba en §9.1.

**Estado**: grupo aplicado. Recompilación final en Overleaf (XeLaTeX) diferida
(ver tarea 10.3 del change).
