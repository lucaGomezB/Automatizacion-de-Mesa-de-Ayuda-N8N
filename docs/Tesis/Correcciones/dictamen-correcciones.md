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
- **OQ6 CERRADO (c-111, 2026-10-21)**: el tag anotado **`v1.0.0`** se creó sobre el commit **`61a6b117dd1321fbee25f9792d9f29b884e5ac8d`** y se publicó en `origin` (`git ls-remote --tags` lo devuelve). El hash completo quedó consignado en el Anexo B de la tesis (`12-anexos.tex`, §Repositorio de código fuente).
- **Trazabilidad `v1.1.0` (c-121, 2026-10-22)**: el tag anotado **`v1.1.0`** se creó sobre el commit **`7103b649d8c4f51737ad6ad4095dad22c9406400`** y se publicó en `origin` (`git ls-remote --tags` lo devuelve). Ese commit cierra las observaciones del dictamen CONEAU de la v1.0.1 sobre la versión de trabajo `v10 (IA)`, que reproduce el contenido congelado de la v9. El hash completo quedó consignado en el Anexo B de la tesis (`12-anexos.tex`, §Repositorio de código fuente).
- **Trazabilidad `v1.1.1` (c-123, 2026-10-22)**: el tag anotado **`v1.1.1`** se creó sobre el commit **`4160d84286623b073d2904353e6f9163ae211de7`** y se publicó en `origin`. Ese commit agrega la URL explícita del repositorio en el Anexo B (`12-anexos.tex`, §Repositorio de código fuente) y corrige la versión de la entrada bibliográfica `Gomez2026_repositorio` a `(Version 1.1.1)`. El hash completo quedó consignado en el Anexo B.
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

## Dictamen c-144 - Procedencia real y ausencia de preproduccion

**Origen**: change `c-144-declarar-procedencia-real-y-ausencia-de-preproduccion`
(docs-only, MEDIUM). Declara la procedencia real de los ajustes realizados sobre
el corpus de validacion y la ausencia de un corpus de preproduccion. No se
modifica ningun valor numerico ni rotulo.

**Evidencia verificada**:

- `1368fd8` (c-71) amplio el vocabulario del filtro deterministico a partir de
  errores del corpus.
- `a76851e` (c-72) redacto las reglas de frontera del prompt a partir de casos
  del corpus (R002, R038).
- `d6bb474` (c-74) fijo el punto de operacion `tau` por validacion cruzada fuera
  de muestra sobre el corpus.
- Directorio `docs/prompt_gemini_history/` inexistente: sin commit, sin entrada
  en `git ls-files` y sin rama que lo contenga.
- Sin conjunto de ~100 incidentes independientes de preproduccion:
  `rg -l "incidentes de preproduccion" data/ evaluation/` sin resultados.

**Mapeo de objetivos de propagacion T01-T07**:

- T01 - `sections/05-arquitectura.tex:78`: procedencia de filtro, reglas del
  prompt y punto de operacion declarada en lugar de "sin acceso al corpus".
- T02 - `sections/06-implementacion.tex:75`: ajustes derivados de errores del
  corpus; sin conjunto independiente de preproduccion.
- T03 - `sections/08-discusion.tex:18`: metricas como estimaciones dentro de la
  muestra; se acota la mitigacion fuera de muestra de c-74.
- T04 - `sections/12-anexos.tex:135`: procedencia real y ubicacion veraz del
  historial del prompt (`docs/prompt_gemini.txt`).
- T05 - `docs/anexo_h_prompt_gemini.md:160/162`: misma declaracion y ubicacion
  del historial en el Anexo H.
- T06 - `evaluation/README.md:192-204`: advertencia metodologica coherente con
  el historial (commits c-71, c-72, c-74).
- T07 - `sections/10-recomendaciones.tex`: subseccion nueva
  `Validacion sobre un corpus independiente` (`subsec:corpus-independiente`).

**Reconciliacion con c-130 y c-142 (PR #40 sin fusionar)**:

c-144 aplica sobre `main` correcciones que c-130 (D9) y c-142 (D11/D13/T08)
aplican sobre el PR #40. Los requisitos de `tesis-document` y
`evaluation-framework` usan los MISMOS nombres que el PR #40
(`Procedencia declarada de los ajustes realizados sobre el corpus de validacion`,
`Ubicacion veraz de las versiones historicas del prompt en el Anexo H`,
`Advertencia metodologica del framework coherente con el historial`) para que la
deduplicacion al fusionar sea mecanica. Al fusionar el PR #40, los bloques
`## ADDED Requirements` de esos tres requisitos en c-130 y c-142 se eliminan o se
convierten en no-op; c-144 es la fuente canonica. c-130 conserva magnitudes por
etapa, alcance del gate y criterio de cortocircuito; c-142 conserva su analisis
de sensibilidad completo.

**Linea base y conteo de paginas**:

- Commit de partida: `d9dfcb3` (rama `RamaLuca`).
- Linea base del PDF: `\@abspage@last{101}` (101 paginas).
- Conteo tras aplicar c-144: `\@abspage@last{102}` (102 paginas), diferencia
  `+1`. Compilacion XeLaTeX (Docker `texlive-thesis`) sin errores fatales y con
  `grep -c "undefined" main.log` = 0.

**Estado**: grupo aplicado.

## FASE 36 - decisiones G0

**Origen**: change `c-141-integracion-release-v1-2-0`, grupo 1 (tareas 1.1 a 1.7), apply
parcial al inicio de la familia, ANTES de aplicar c-130 (design D2). Registrado el
**2026-10-25**. Rama de trabajo: `change/c-141-g0-decisiones` (cortada de `ramagonzalo` en
`f6c121e`). Solo documentacion: no se modifica ningun `.tex`, codigo ni `CHANGES.md`.

**Convencion de estado de las decisiones**: el usuario (Gonzalo Sevilla, coautor) pidio
aplicar la familia sin detenerse y NO respondio de forma explicita a OQ1, OQ2, OQ3, OQ4 ni
OQ7a. Cada decision se registra como **PROVISIONAL (default del design, pendiente de
confirmacion del autor)**, con la opcion por defecto que fija el propio `design.md`. Una
confirmacion o un cambio posterior se agrega en esta misma seccion con su fecha, sin
reescribir la entrada original.

### G0.0 - Linea base movida por c-144 (hecho que condiciona G0.1 y el libro mayor)

La linea base del dictamen era `v1.1.1` = 101 paginas (cuerpo sin anexos 93; encabezado
"Anexos" en la p. 94). El 2026-10-23 Luca Gomez aplico y fusiono en `main` el change
`c-144-declarar-procedencia-real-y-ausencia-de-preproduccion` (commit `0c7f5bc`, ya
incluido en `ramagonzalo`), que recompilo el PDF. Evidencia verificada el 2026-10-25 sobre
el arbol de `ramagonzalo` (`f6c121e`):

- `grep -o "abspage@last{[0-9]*}" "docs/Tesis/v10 (IA)/paper/main.aux"` devuelve
  `abspage@last{102}`.
- `main.toc` contiene `\contentsline {section}{Anexos}{95}{section*.27}`: cuerpo sin
  anexos = 95 - 1 = 94; anexos = 102 - 94 = 8.
- Delta de c-144: +1 pagina (101 -> 102), declarado por el propio c-144 en su seccion
  "Dictamen c-144" de este registro ("Conteo tras aplicar c-144: 102 paginas").

Consecuencia: toda regla de tope se evalua contra el total vigente de **102**, no contra
101. Los `design.md` y `tasks.md` de la familia que citan 101 como linea base se leen como
"101 en `v1.1.1`, 102 tras c-144".

### G0.1 - Tope de paginas (OQ1) y compensacion C3 de c-142

**Estado: PROVISIONAL (default del design D2/D3, pendiente de confirmacion del autor).
Fecha: 2026-10-25.**

| Campo | Valor |
|---|---|
| Regla de medicion | **Total del PDF** (rama (a)), medido con `abspage@last` de `main.aux` o `pdfinfo` |
| Valor | **total <= 101** |
| Fuente | Criterio duro mas reciente de los changes c-120..c-123 (decision del equipo; NO consta que sea una exigencia de la catedra) |
| Fecha | 2026-10-25 (registro); los topes de 100/101 de c-116, c-117, c-118 y c-120..c-123 son anteriores |

Advertencia explicita: la linea base ya esta en **102** por c-144, es decir, la familia
arranca **1 pagina POR ENCIMA** del tope de la rama (a) antes de aplicar cualquier change.
Con la estimacion de D3 (+5,4 a +12,2 paginas, central +7,7) el total sin compactar queda
en 107 a 114 paginas (central unas 109,7). La rama (a) exige entonces compactar de 6,4 a
13,2 paginas, que las palancas de forma P1-P5 (1,6 a 2,9) no cubren; solo cierra la brecha
la palanca P8 (interlineado, formato de la catedra) o reducir el contenido de la familia.
Esto debe revisarse con el autor antes de que el acumulado de c-130..c-139 consuma el margen.

**Candidata recomendada para la rama (b)** (a confirmar por el autor y, si corresponde, por
la catedra): la regla del plan §1.1 de cumplimiento, **cuerpo sin anexos <= 100, anexos sin
limite**, ya aplicada en c-118 con confirmacion del autor. Sobre la linea base vigente deja
un margen de 100 - 94 = **6 paginas** de cuerpo, frente a un crecimiento central estimado
del cuerpo de unas +7,4: la estimacion central supera el margen en unas 1,4 paginas y exige compensaciones locales (palancas P1-P5 o C3).

**Compensacion C3 de c-142** (mover su tabla `tab:sensibilidad-ajustes` a un anexo): **se
adopta CONDICIONALMENTE, solo si se confirma la rama (b)**. Bajo la rama (a) no rinde (el
total no baja al mover contenido de 07 a un anexo) y por lo tanto no se aplica.

Efecto sobre la alarma temprana (D4): ver "Libro mayor de paginas". Bajo la rama (a) la
alarma ya esta activa en la linea base (margen 101 - 102 = -1). Mientras el autor no
confirme, la familia se aplica con la rama (a) como regla registrada y cada fila del libro
mayor se toma como dato de decision, no como bloqueo.

### G0.2 - Entorno de compilacion de registro (OQ3)

**Estado: PROVISIONAL, PARCIAL (entorno registrado; reproduccion de la linea base
PENDIENTE del build Docker). Fecha: 2026-10-25.**

- **Hecho verificado**: en la PC de Gonzalo NO hay `xelatex`, `biber`, `latexmk` ni MiKTeX
  en el PATH (verificado con `which` y busqueda en Program Files y AppData). La opcion (1)
  de D6 (MiKTeX local) queda descartada en esta maquina. Tampoco hay `pdfinfo` en el PATH
  (si `pdftotext`); el conteo de paginas de registro usa `abspage@last` de `main.aux`
  (equivalente documentado en D4/D6) o el conteo de saltos de pagina de `pdftotext`.
- **Entorno adoptado para el registro**: imagen Docker `texlive-thesis`
  (`docs/Tesis/v10 (IA)/paper/Dockerfile`: XeLaTeX + biber + fuentes Microsoft core), la
  misma que uso Luca para compilar c-144 (su seccion "Dictamen c-144" registra
  "Compilacion XeLaTeX (Docker `texlive-thesis`)"). Opcion (2) de D6.
- **Build en curso** en la PC de Gonzalo (lo construye el orquestador en segundo plano).
  Comando de compilacion previsto (montar `docs/Tesis/v10 (IA)`, no la ruta de v9 de los
  comentarios del Dockerfile): `docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work
  -w /work/paper texlive-thesis latexmk main.tex`.

Datos completados el 2026-10-25 (build de `texlive-thesis` terminado con exito en la PC de Gonzalo;
compilacion sobre una copia aislada del arbol de `ramagonzalo` en `f6c121e`, fuente identica a
`0c7f5bc` en `docs/Tesis/v10 (IA)/`, con los artefactos previos borrados y `latexmk main.tex`):

- `xelatex --version`: `XeTeX 3.141592653-2.6-0.999998 (TeX Live 2026)`
- `biber --version`: `biber version: 2.22`
- Prueba de reproduccion de la linea base: `latexmk` salida 0; `abspage@last{102}` (**102 paginas**,
  coincide con la linea base movida por c-144); `grep -c -i "undefined" main.log` = 0;
  `grep -c "multiply defined" main.log` = 0; `grep -E "WARN|ERROR" main.blg` sin resultados;
  `grep -c "^!" main.log` = 0 (0 errores fatales). **Entorno ADOPTADO** como entorno de registro
  de toda la familia (D6, opcion 2). La tarea 1.2 de `tasks.md` queda cerrada.

Nota sobre la tarea 1.2 de `tasks.md`: su redaccion dice "verificar 101 paginas"; tras c-144
el valor de reproduccion correcto es 102 (G0.0). El valor 101 se verifica solo, de forma
opcional, compilando el commit `4160d84` (`v1.1.1`).

### G0.3 - Inclusion de c-140 (OQ4)

**Estado: PROVISIONAL (default del design, pendiente de confirmacion del autor). Fecha:
2026-10-25.**

Decision por defecto: **c-140 SE INCLUYE como opcional** (`endurecimiento-tecnico-tls-reintentos-e2e`),
con su texto de tesis en la **posicion 12 de D1** (despues de c-139 y antes de c-137) y sus
bloques de codigo en paralelo desde G0 (no comparten archivos con la familia). La exclusion
(archivar c-140 como NO REALIZADO con `--skip-specs`, precedente c-67, dejar el criterio 5
como limitacion declarada y buscar otro dueno para el `timeout` de 10 s frente a 30 s)
**queda disponible si el tiempo no alcanza**; se decide antes de aplicar la posicion 12 y se
registra aqui con su fecha.

### G0.4 - Nombre de la release (OQ2)

**Estado: PROVISIONAL. Fecha: 2026-10-25.** Nombre: **`v1.2.0`**. Confirmable (por ejemplo
`v2.0.0` si el jurado o la catedra piden una version nueva numerada para el reexamen) hasta
antes de C1 (tarea 5.1).

### G0.5 - Estado de las caches de predicciones

**Estado: VERIFICADO (hecho, no decision). Fecha de verificacion: 2026-10-25.** Condiciona
A2, B7b y B8 (c-131) y las sensibilidades E3 y E4 de c-142.

Hallazgos:

- `ls evaluation/*.json`: sin resultados. **Las caches vivas NO existen en el arbol de
  trabajo**: ni `evaluation/predicciones.json` ni `evaluation/predicciones_calibracion.json`.
- `.gitignore:71-73` sigue excluyendo ambas rutas (comentario: "derivan del corpus real,
  PII"). No existe `evaluation/.gitignore`. `git check-ignore -v evaluation/predicciones.json`
  confirma la regla `.gitignore:72`.
- **Cambio frente a lo que supone la tarea 1.4**: el change
  `c-143-publicar-predicciones-como-evidencia-de-evaluacion` (Luca, archivado 2026-10-23,
  13/13; commit `fec4c42`) publico copias congeladas byte-identicas de las caches bajo
  `evaluation/evidence/`, **versionadas** (no ignoradas):

| Archivo versionado | `classifier_version` | `corpus_hash` | `generated_at` | Estado frente al corpus vigente |
|---|---|---|---|---|
| `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` | `hybrid-v3` | `1fd17d7e...ac5cb` (coincide con el hash canonico del corpus versionado) | `2026-10-07T22:22:01Z` | **Vigente**: es la corrida principal de 200 casos |
| `evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json` | `hybrid-v2` | `5f062e14...f46a93` (NO coincide) | `2026-10-07T20:33:03Z` | **Solo historica**: corpus y clasificador anteriores |

  y `evaluation/evidence/README.md` (campos de `cache_meta`, recalculo por caso por join
  `caso_id` <-> `id` con `data/corpus_evaluacion_pseudonimizado.json`, advertencia del hash
  de calibracion). c-143 NO modifica `.gitignore` ni crea el cache vivo.
- Consecuencias para la familia:
  - **c-131 (A2, B7b, B8)**: la causa "caches irrecuperables" ya no aplica para la corrida
    principal; las metricas por etapa/canal y el contraste pareado se pueden recomputar sin
    invocar Gemini a partir de la evidencia `hybrid-v3` (no hace falta pedir las caches al
    clon de Luca ni gastar la corrida paga de ~0,05 USD de su opcion alternativa). Para
    regenerar `evaluation/report.md` por el runner (`PREDICCIONES_PATH =
    evaluation/predicciones.json`) c-131 decide si copia la evidencia a esa ruta
    gitignoreada; `HYBRID_CACHE_VERSION` es `hybrid-v3` (cache hit) y el obstaculo de
    huella por fin de linea (`core.autocrlf=true`, corpus de trabajo en CRLF) lo trata
    c-131/c-134, no G0.
  - **c-142 (E3, E4)**: computables sobre la evidencia `hybrid-v3` (sin costo). Su riesgo
    "las caches no se recuperan -> E3, E4 y niveles a y b no computables" queda atenuado:
    la cache de la **configuracion final** esta disponible; la ablacion del prompt (nivel c)
    NO se recupera de ninguna cache (requiere corrida paga, ver G0.7a). La cache de
    calibracion `hybrid-v2` no sirve para sensibilidades sobre el corpus vigente (hash
    distinto).
  - Esto reemplaza, a efectos de c-131 y c-142, la frase de la tarea 1.4 ("no existe en el
    arbol al 2026-10-22"); la decision definitiva sobre su uso sigue siendo de c-131.

### G0.6 - Orden de aplicacion de la familia (D1)

**Estado: FIJADO por c-141 (D1), con la supersesion parcial de c-144. Fecha: 2026-10-25.**

Aplicacion estrictamente secuencial en `ramagonzalo`, un change por vez, cada uno sobre el
resultado del anterior:

| # | Change | Recomendaciones | Debe ir despues de |
|---|---|---|---|
| 0 | c-141, grupo 1 (G0) | Decisiones bloqueantes (esta seccion) | - |
| 1 | c-130 | A1; A5a (mitad declarativa; su D9) | G0 |
| 2 | c-134, bloque de codigo (tareas 1 a 5) | B7a (base), B12 (base) | c-130 |
| 3 | c-131 | A2, B7b, B8; McNemar | c-130 |
| 4 | c-142 | A5b (sensibilidad fuera de muestra) | c-130, c-131 |
| 5 | c-132 | A3 | c-131, c-142 |
| 6 | c-133 | B4, B5, B6 | c-130, c-131, c-142, c-132 |
| 7 | c-134, bloque de tesis | B7a, B12, B13b (cronometraje) | c-132, c-133 |
| 8 | c-138 | Sec. 4 del dictamen; criterio 3 residual | c-130, c-131 |
| 9 | c-136 | B11 | c-130, c-131 (duras); c-132, c-133, c-138 (blandas) |
| 10 | c-135 | B9, B10a-d, B13a (cota telefonica) | c-130, c-131, c-134, c-142 |
| 11 | c-139 | A4, B15, B16a | c-130, c-133, c-134, c-135, c-136 |
| 12 | c-140 (si se incluye; G0.3) | Criterio 5 residual (texto de tesis) | c-130, c-135, c-136, c-139 |
| 13 | c-137 | B14 | todos los anteriores |
| 14 | c-141, grupos 2 a 9 | Cierre y B16b | todos |

Orden lineal: G0 -> c-130 -> c-134 (bloque de codigo) -> c-131 -> c-142 -> c-132 -> c-133 ->
c-134 (bloque de tesis) -> c-138 -> c-136 -> c-135 -> c-139 -> c-140 (si se incluye) ->
c-137 -> c-141 (grupos 2 a 9). La unica paralelizacion admitida es la de los bloques de
codigo de c-140 y la herramienta de c-137, que no tocan la tesis.

**Desacuerdos resueltos** (entregar al orquestador para que ajuste el D7 de c-133):

- **c-132 antes de c-133.** c-133 (D7) proponia c-133 -> c-132; c-132 (D11) y c-136 (D11)
  proponen c-132 -> c-133. Se adopta c-132 -> c-133: c-132 no depende de c-133, la propiedad
  por clausula de c-133 D7 evita conflictos en los parrafos compartidos, c-133 puede citar
  el balance en `tab:cumplimiento-objetivos` y, como compresor del resumen, conviene que
  pase despues de la oracion de viabilidad de c-132. **Accion del orquestador: actualizar el
  D7 de c-133.**
- **c-135 antes de c-139.** c-139 declara que necesita la tabla de trabajos ya completada
  por c-135; c-135 no depende de c-136 ni de c-139 (fragmentos disjuntos en 03). Se sigue
  c-136 D11 (c-138 -> c-136 -> c-139) con c-135 intercalado antes de c-139.
- **c-142 entre c-131 y c-132** (orden que propone c-142 y confirma el orquestador).
- **c-134 en dos tramos** (codigo antes de c-131; tesis despues de c-133), segun c-134 D12.
- **c-140 frente a c-133**: no se adelanta; si c-133 ya esta aplicado, c-140 actualiza solo
  el calificativo de la fila del objetivo 1.

**Divisiones explicitas de recomendaciones**:

- **A5a** (procedencia declarada en `05:78`, `06:75`, `08:18` y primera oracion de
  `12:135`) -> **c-130** (D9); **A5b** (sensibilidad fuera de muestra, limitacion y evidencia
  del objetivo 6) -> **c-142**.
- **B7a** (tiempos manuales por canal y Wilcoxon intra-canal) -> **c-134**; **B7b**
  (exactitud por canal) -> **c-131**.
- **B13a** (salvedad de cota inferior del canal telefonico en `09:39`) -> **c-135**;
  **B13b** (procedimiento de cronometraje en vivo en `04:16`, `08:20`, `11:32`) -> **c-134**.
- **B16a** (metadatos bibliograficos) -> **c-139**; **B16b** (version de
  `Gomez2026_repositorio`) -> **c-141** en C1.

**Supersesion parcial por c-144** (nueva respecto del design de c-141; hecho verificado en
`openspec/changes/archive/2026-10-23-c-144-declarar-procedencia-real-y-ausencia-de-preproduccion/proposal.md`
y en la seccion "Dictamen c-144" de este registro):

- **c-130** conserva magnitudes por etapa, alcance del gate y criterio de cortocircuito, pero
  **aplica T04, T12, T13 y T14 solo como verificacion** (los resuelve c-144: procedencia
  declarada en `05`, `06`, `08` y `12`; Anexo H; advertencia de `evaluation/README.md`;
  subseccion `subsec:corpus-independiente`). No reescribe lo que c-144 ya dejo en `main`.
- **c-142** **omite los requisitos ya cubiertos por c-144** (D11/D13/T08: los tres
  requisitos `ADDED` de procedencia, ubicacion veraz del historial del prompt y advertencia
  metodologica; retirados de c-130 y c-142 en el commit `90b0b9b`). Conserva su analisis de
  sensibilidad completo.
- c-144 es la fuente canonica de esos tres requisitos; al fusionar el PR #40 los bloques
  `ADDED` correspondientes ya son no-op.

**Regla de numeracion de las secciones del memo** (`docs/Tesis/Correcciones/numeros-canonicos.md`):
el primero en aplicarse conserva la "Seccion 3.7"; cada change posterior que cree una
seccion propia toma el siguiente numero libre al aplicar y corrige sus propias remisiones
("ver seccion 3.N", su grupo en este registro, la evidencia de sus tareas). Verificado el
2026-10-25 con `grep -n "^## \|^### " numeros-canonicos.md`: las secciones vigentes son 3.1
a 3.6 (3.6 = marco metrico unificado, c-108), 4, 5, 6 y 7; **no existe 3.7**.
**c-144 NO ocupo un numero de la serie 3.N**: sus 15 lineas agregadas
(`git show 0c7f5bc -- numeros-canonicos.md`) son el **item 6 de la seccion 7 "Decisiones no
resolubles"** (conjunto de ~100 incidentes de preproduccion, no verificable). No hay
colision: la secuencia esperada se mantiene: **3.7 c-130, 3.8 c-131, 3.9 c-142, 3.10 c-132,
3.11 c-133, 3.12 c-134**. La consolidacion de c-141 (tarea 2.7) no debe renumerar el item 6
de la seccion 7 y debe tratarlo como existente.

**Actualizacion 2026-10-25 (c-134, bloque de codigo)**: c-134 se aplica en dos tramos y su
bloque de codigo (que escribe la seccion del memo) va ANTES de c-131; por la regla anterior
tomo la **3.8** ("Tiempos por canal, contrastes y sensibilidad (c-134)"; 3.7 ya era de
c-130, verificado con `grep -n "^## \|^### " numeros-canonicos.md`). La secuencia esperada
se corre: **c-131 -> 3.9, c-142 -> 3.10, c-132 -> 3.11, c-133 -> 3.12**; el bloque de tesis de
c-134 reutiliza la 3.8 y remite a ella ("ver seccion 3.8"). Cada change posterior toma el
siguiente numero libre al aplicar. Ademas, c-134 actualizo en el memo las remisiones
`report.md:99` -> `report.md:140` (la linea del SHA-256 se desplazo al agregar tres
subsecciones a "## Tiempos"); c-131 debe volver a contrastar las lineas del reporte que cite
si agrega secciones antes de "## Tiempos" (D12 de c-134).

**Obligacion de libro mayor**: cada change de la familia agrega su fila al libro mayor de
paginas (subseccion siguiente) despues de su apply, con commit, total, cuerpo sin anexos,
anexos, delta y estado; el orquestador lo incluye en cada prompt de apply. c-141 consolida y
contrasta con el PDF final.

**Regla de ramas** (acordada con el usuario, 2026-10-25): cada change de la familia se aplica
en su propia rama git **`change/<nombre-del-change>`** creada desde **`ramagonzalo`**; al
terminar se **fusiona localmente en `ramagonzalo`** y la rama siguiente se corta de ese
resultado (aplicacion secuencial, coherente con D1). **Sin push ni PR sin confirmacion del
usuario.** El G0 se aplico en `change/c-141-g0-decisiones`. Los changes de codigo (bloque de
codigo de c-134, c-131, c-142) siguen la misma regla. Los tags y el PR de c-141 mantienen
sus checkpoints HIGH propios (tareas 8.5 y 8.8).

### G0.7 - Checkpoints HIGH de c-142 (OQ7)

**(a) Ablacion paga del prompt (nivel c).**
**Estado: NO AUTORIZADA por ahora. Fecha: 2026-10-25.** Alcance consultado: 138
invocaciones (los 69 casos de la etapa Gemini, dos variantes del prompt), del orden de 0,03
USD y como maximo 0,10 USD. El usuario no respondio a la consulta y no hay autorizacion
registrada. **Consecuencia para c-142**: la sensibilidad del prompt (nivel c) se declara
**"no cuantificada"** (rama minima de su limitacion y su subseccion); no se ejecuta ninguna
invocacion paga. Una autorizacion posterior se registra AQUI con fecha y, en ese caso, c-142
ejecuta el nivel c antes de su cierre. Sin esa autorizacion, ninguna tarea de la familia
debe invocar a Gemini (control de la tarea 2.8).

**(b) Conjunto de ~100 incidentes de preproduccion del Anexo H.**
**Estado: RESUELTO por c-144 (hecho verificado). Fecha de resolucion: 2026-10-23
(c-144); registrado aqui 2026-10-25.** El conjunto **no existe**: `rg -l "incidentes de
preproduccion" data/ evaluation/` no devuelve resultados, `data/` y `evaluation/` solo
contienen el corpus de 200 casos y sus derivados, y `docs/prompt_gemini_history/` nunca
existio (verificado inexistente el 2026-10-25). c-144 declara el desenlace "no existen / no
se localizan" (item 6 de la seccion 7 del memo). **Consecuencia para c-142**: **ausencia
declarada**, sin datos personales involucrados (no hay conjunto, por lo tanto no aplica la
Ley 25.326 a este checkpoint ni hace falta aprobacion de pseudonimizacion). c-142 NO intenta
usar un conjunto independiente. **Reversible si** el autor aporta el conjunto pseudonimizado
y etiquetado: corresponde entonces un change de gobernanza HIGH propio.

### Libro mayor de paginas (D4)

Medicion: total = `\@abspage@last` de `main.aux` (`grep -o "abspage@last{[0-9]*}" main.aux`)
o `pdfinfo main.pdf | grep Pages` (no disponible en esta maquina) o, como equivalente, el
conteo de saltos de pagina de `pdftotext -enc UTF-8 main.pdf -`; cuerpo sin anexos = pagina
del encabezado "Anexos" en `main.toc` (`\contentsline {section}{Anexos}{N}`) menos 1; anexos
= total - cuerpo. Todos los conteos de registro salen del entorno de G0.2.

| Change | Commit | Total | Cuerpo sin anexos | Anexos | Delta total | Delta cuerpo | Regla vigente | Estado |
|---|---|---|---|---|---|---|---|---|
| base `v1.1.1` | `4160d84` | 101 | 93 | 8 | - | - | (a) total <= 101 | Medido (dictamen / `main.toc` de v1.1.1) |
| `+c-144` (main) | `0c7f5bc` | 102 | 94 | 8 | +1 | +1 | (a) total <= 101 | Medido: `abspage@last{102}`; `Anexos` en p. 95 |
| `+c-130` (`change/c-130-gate-revision-humana-por-etapa`) | sin commit (lo crea el orquestador) | 103 | 95 | 8 | +1 | +1 | (a) total <= 101 | Medido: `abspage@last{103}`; `Anexos` en p. 96; brecha frente a 101: +2 (con C3 aplicada) |
| `+c-131` (`change/c-131-metricas-por-etapa-canal-y-exactitud-laxa`) | sin commit (lo crea el orquestador) | 103 | 95 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{103}`; `Anexos` en p. 96; brecha frente a 101: +2 (sin compensar habria sido 105) |
| `+c-142` (`change/c-142-sensibilidad-fuera-de-muestra-ajustes-clasificador`) | sin commit (lo crea el orquestador) | 104 | 96 | 8 | +1 | +1 | (a) total <= 101 | Medido: `abspage@last{104}`; `Anexos` en p. 97; brecha frente a 101: +3 (sin los recortes de `09` y la variante de T06 habria sido 105); C3 no aplicada (el total no supera 104) |
| `+c-132` (`change/c-132-balance-neto-derivaciones-erroneas`) | sin commit (lo crea el orquestador) | 105 | 97 | 8 | +1 | +1 | (a) total <= 101 | Medido: `abspage@last{105}`; `Anexos` en p. 98; brecha frente a 101: +4 (la primera compilacion dio 106; las variantes cortas de T10, T11 y T13 recuperaron la pagina); rama (b): cuerpo 97, margen 3 |

Las filas siguientes se agregan al final de esta tabla, una por change, despues de su apply.
Previsiones declaradas por cada change (se contrastan al cerrar):

| Change | Prevision declarada (paginas) |
|---|---|
| c-130 | +0,3 a +0,9 netas (bruto +0,7 a +0,9) |
| c-131 | 0 a +0,9 |
| c-142 | **+1,0 a +1,4 (central +1,2)** |
| c-132 | +1 a +3 (objetivo neto <= +1) |
| c-133 | 0 |
| c-134 | 0 a +0,4 |
| c-135 | 0 |
| c-136 | 0 a +1 |
| c-138 | +2 a +3 |
| c-139 | +1 (bibliografia) |
| c-140 (opcional) | 0 a +0,5 |
| c-137 | 0 |
| c-141 | +0,1 a +0,6 (Anexo I) |
| **Total sin c-140** | **+5,4 a +12,2 (central +7,7)** |

Proyeccion sobre la linea base vigente de 102: total 107 a 114 (central unas 109,7); cuerpo
sin anexos 99,3 a 105,6, central unas 101,4 (el Anexo I es el unico crecimiento de anexos).

**Alarma temprana**: si el delta acumulado supera el margen de la regla vigente menos 1
pagina de reserva, el orquestador se detiene y consulta antes de aplicar el change
siguiente. Aplicada a las dos reglas sobre la linea base de 102 / 94:

- Rama (a), total <= 101: margen = 101 - 102 = **-1**; umbral de alarma = -1 - 1 = -2.
  **La alarma ya esta superada en la linea base** (el acumulado de la familia parte en +1
  por c-144). Efecto provisional: la familia se aplica igual (instruccion del usuario) y
  cada fila del libro mayor se reporta con su brecha frente a 101.
- Rama (b), cuerpo <= 100: margen = 100 - 94 = **6**; la alarma salta cuando el delta
  acumulado del cuerpo supera **5** paginas.

**Verificacion de la fila base**: la fila `v1.1.1` contiene los tres valores (101, 93, 8).

### Nota: c-134, bloque de codigo aplicado (2026-10-25)

c-134 bloque de codigo (tareas 1 a 5 de `tasks.md`) aplicado el 2026-10-25 en la rama
`change/c-134-contrastes-estadisticos-y-desagregado-canal` (sin commit; lo crea el
orquestador); bloque de tesis (grupos 6 a 8) **pendiente**, posicion 7 del orden de la
familia (despues de c-133). Alcance: los modulos `stats.py` y `run_evaluation.py`, el `README.md`, el
`report.md` y los tests de `evaluation/`, y la seccion 3.8 del memo `numeros-canonicos.md`; no toca `.tex`, no
recompila la tesis ni agrega fila al libro mayor de paginas (la agrega el bloque de tesis).
`evaluation/report.md` se regenero con `--solo-tiempos` (sin Gemini ni predicciones):
solo se agregaron tres subsecciones dentro de "## Tiempos"; las filas previas (W, T+, T-,
p, r, desglose por canal) y la huella canonica del corpus no cambiaron.

## Dictamen v1.1.0 - A1 (c-130) - Gate de revision humana por etapa

**Origen**: change `c-130-gate-revision-humana-por-etapa` (dictamen CONEAU 2026-10-22 sobre
v1.1.0/v1.1.1: VEREDICTO punto 1; secciones 5, 6 y 7(a); recomendacion A1). Aplicado el
**2026-10-25** en la rama `change/c-130-gate-revision-humana-por-etapa`, cortada de
`ramagonzalo` en `103f198` (merge del G0). Posicion 1 del orden de la familia (G0.6).

### Linea base (tarea 1.1)

- Commit de partida: `103f198`.
- `grep -o "abspage@last{[0-9]*}" "docs/Tesis/v10 (IA)/paper/main.aux"` devuelve
  **`abspage@last{102}`**, NO 101: la tarea 1.1 de `tasks.md` cita la linea base de `v1.1.1`
  (101); c-144 (`0c7f5bc`) la movio a 102 (G0.0). `main.toc`: `Anexos` en p. 95, cuerpo sin
  anexos 94, anexos 8.

### Red de seguridad y re-verificacion offline (tareas 1.2 y 1.3)

- Tests del backend (`test_hybrid_classifier`, `test_deterministic_classifier`,
  `test_deterministic_correctness_score`, `test_gemini_validation`, `test_gemini_retry`,
  `test_reporter_link`; Docker `mesa_local-backend`): **122 passed** antes de editar.
- Repeticion offline de la etapa determinista (`DeterministicClassifier` real, clave ficticia,
  sin red) sobre `data/corpus_evaluacion_pseudonimizado.json`: 57 sin prediccion, 12
  ambiguos, **131** con senal dominante, todos con score >= 0,516667 (minimo 0,5166667), **97**
  aciertos estrictos (0,7405), **124** con confianza < 0,70 (94 aciertos), 7 con >= 0,70, 1
  con >= 0,90; confianzas {0,0: 90; 1/6: 8; 0,5: 26; 0,75: 6; 1,0: 1}. Coincide con el design:
  no hay deriva entre el codigo y la etapa evaluada.
- Contraste con la evidencia versionada por c-143 (`evaluation/evidence/`): la corrida
  `hybrid-v3` tiene 131 deterministicos y 69 de Gemini, 124 con confianza < 0,70 (todos
  deterministicos), minimo de Gemini 0,85 y 97 aciertos deterministicos; la cache de
  calibracion `hybrid-v2` reproduce **88/130 = 0,6769** de `precision_gem(S)`.

### Checkpoint de autores (tarea 1.4) - PROVISIONAL

El usuario pidio aplicar sin detenerse y no respondio de forma explicita a las Open Questions.
Fecha: 2026-10-25. Cada decision es **PROVISIONAL (default del design, pendiente de
confirmacion del autor)**.

| OQ | Tema | Decision | Estado |
|---|---|---|---|
| OQ1 (D9) | Procedencia de los ajustes sobre el corpus | **RESUELTA por c-144** (`0c7f5bc`): los autores ya declararon la procedencia real al fusionarlo en `main`. T04, T12, T13 y T14 no se reescriben; se ejecutan solo sus verificaciones | Resuelta (hecho) |
| OQ2 (D7) | Alcance de la salvaguarda legal; reasignacion solo por REST | Default del design: se aplica T15 | PROVISIONAL |
| OQ3 (D12) | Comentarios y test en `App/Backend` | Si: bloque 7 aplicado | PROVISIONAL |
| OQ4 (D11) | Editar `CLAUDE.md` y `openspec/config.yaml` (solo las lineas del gate) | Si: bloque 8 aplicado | PROVISIONAL |
| OQ5 | `cache_meta` de la calibracion | Ver abajo | Parcial |
| OQ6 | `usuario_final` puede validar la clasificacion de su incidente | Fuera de alcance (dominio CRITICAL); sin cambios | Abierta |

**OQ5.** c-143 publico `evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json`
(`classifier_version = hybrid-v2`, `generated_at = 2026-10-07T20:33:03Z`, `corpus_hash =
5f062e14...` que NO coincide con el vigente `1fd17d7e...`, solo evidencia historica) y
`predicciones_hybrid-v3_2026-10-07.json` (hash que coincide con el corpus vigente). Eso aporta
una parte del `cache_meta` de la tarea 2.3 (fecha y etiqueta de version del clasificador) y
permite **reproducir 88/130 offline**; NO aporta la version del prompt ni explica la diferencia
de `corpus_hash` (las 200 descripciones coinciden con el corpus vigente). Se registra en la
Seccion 7, punto 7, de `numeros-canonicos.md`; reversible si el autor aporta la version del prompt.

### Mapeo VEREDICTO 1 / seccion 5 / seccion 6 / seccion 7(a) / A1 -> T01-T16

| T | Archivo | Estado |
|---|---|---|
| T01 | `02-marco-teorico.tex:34` | Aplicada (revision selectiva acotada por etapa) |
| T02 | `02-marco-teorico.tex:46` | Aplicada (solo la oracion final) |
| T03 | `05-arquitectura.tex:24` | Aplicada (celda de la capa 4) |
| T04 | `05-arquitectura.tex:78` | Cubierta por c-144 `0c7f5bc`; verificada (`grep -c "sin acceso al corpus de validación"` = 0) |
| T05 | `05-arquitectura.tex:80` | Aplicada (parrafo completo; retira "superior al 90 %") |
| T06 | `05-arquitectura.tex:82` | Aplicada (3 fragmentos; incluye C1) |
| T07 | `06-implementacion.tex:39` | Aplicada (incluye C4) |
| T08 | `06-implementacion.tex:40` | Aplicada (2 fragmentos; acentos corregidos solo en lo reescrito) |
| T09 | `06-implementacion.tex:87,95` | Aplicada |
| T10 | `07-resultados.tex:136` | Aplicada (124/200; solo se modifica la linea 136) |
| T11 | `08-discusion.tex:16` | Aplicada (69 casos de Gemini; valoracion remitida a `subsec:calibracion`) |
| T12 | `08-discusion.tex:18` | Cubierta por c-144; verificada (0 coincidencias de "datos no vistos" y "separación estricta"; 1 de "estimaciones dentro de la muestra") |
| T13 | `06-implementacion.tex:75` | Cubierta por c-144; verificada (0 coincidencias de "sin exposición al corpus de validación") |
| T14 | `12-anexos.tex:135` | Cubierta por c-144; verificada (`grep -c "sin exposición a\|sin acceso al corpus" sections/*.tex` = 0 en todos) |
| T15 | `11-aspectos-legales.tex:34` | Aplicada [D7, PROVISIONAL] |
| T16 | `12-anexos.tex` (tab:anexo_gemini_params) | Aplicada (fila nueva tras `timeout`, sin tocar `timeout`) |

Tarea 9.1 (roles, agregada por Luca en `2236b26`): aplicada en `04-marco-metodologico.tex:108`.
Evidencia `git shortlog -sne HEAD`: lucaGomezB 417, GonzaloSevilla22 93, Luca Gomez 35, Gonzalo
Sevilla 15, dependabot[bot] 1 (con `--all`: 420/93/35/15/6); **ningun commit a nombre de Carla
Bustos** y ninguna mencion en los mensajes (`git log --grep`). Carla pasa a revisora de la tesis y
colaboradora en anexos y corroboracion de fuentes; el modulo Python y el modelado de datos se
atribuyen a Luca Gomez; la configuracion N8N y la integracion telefonica quedan en Gonzalo
Sevilla (commits c-04/c-05 sobre el workflow); se conserva la supervision del director.
**Salvedad para los autores**: el historial tambien muestra que el modulo inicial
`Gestion_Incidentes` y el frontend los commiteo la identidad `GonzaloSevilla22`
(`7db7fe1`, `ca8e2b6`, 2026-05-20/21) y que el codigo de telefonia del backend es de
`lucaGomezB`; la redaccion adoptada sigue el encargo del design y debe confirmarse.

### Codigo (bloque 7, MEDIUM) y documentacion para agentes (bloque 8)

- Test de caracterizacion `test_cortocircuito_deterministico_no_marca_revision_aunque_confianza_menor_a_070`
  (3 casos: confianza 0,0; 1/6; 0,5): pasa en la primera corrida por diseno (RED no aplica);
  una mutacion que marca revision en el cortocircuito lo hace fallar (3/3).
- Docstrings de `hybrid.py`, `deterministic.py` y `gemini_classifier.py` alineados con el
  comportamiento vigente; `wc -l` identico (257/360/604); `ast.dump` sin docstrings
  identico antes y despues (sha256 igual en los tres archivos). Suite: **125 passed** (122 + 3).
- `openspec/config.yaml` (lineas 11 y 42), `CLAUDE.md` (lineas 50 y 100) y `knowledge-base/`
  (RN-CL-02, RN-CL-03, RN-CL-05, DD-07, tabla de variables de entorno y afines) actualizados;
  `openspec validate c-130-gate-revision-humana-por-etapa --strict` en verde.

### Reversibilidad (D6, D7, D9, D10)

- D6: c-131 fija la valoracion final del hallazgo de Gemini (fiabilidad o sobreconfianza).
- D7: se retira la salvedad de la reasignacion solo por REST si un change de codigo expone la
  reasignacion de incidentes no derivados en la interfaz web.
- D9: ya resuelta por c-144; si los autores acreditan que los ajustes usaron datos ajenos al
  corpus, se restituye la afirmacion de no exposicion con esa evidencia.
- D10: la Seccion 3.7 de `numeros-canonicos.md` se actualiza si el autor aporta la version del
  prompt de la cache FORCE-ESCALATE.

### Consignas derivadas a otros changes (tabla de fronteras del design)

- **c-131**: desagregar por etapa con los nombres de D2; reformular `07-resultados.tex:143`
  ("umbral del 70 % que gobierna el gate") y `:165` ("el gate del 70 % no aislo los errores");
  conservar `\label{subsec:calibracion}`; consumir `97/131` de la Seccion 3.7.
- **c-133**: `01-introduccion.tex:34` y `07-resultados.tex:138` (sub-hipotesis de intervencion):
  la base es 69 de 200 casos sujetos al gate; no apoyar la hipotesis de eficiencia en 0,7405
  frente a 0,6769 como evidencia independiente.
- **c-132**: `08-discusion.tex:14` y `09-conclusiones.tex:41` deben reconocer que no hubo derivacion
  por caso basada en la clasificacion sobre el 65,5 %.
- **c-136**: gate por caso sobre el puntaje y confirmacion en corpus independiente.
- **c-135**: fechas de `06-implementacion.tex:75`; deriva de modelo (`CLAUDE.md` y
  `openspec/config.yaml` dicen "Gemini 2.5 Flash"; tesis y `Settings`, 3.6).
- **c-137**: acentuacion fuera de los fragmentos reescritos (por ejemplo `06-implementacion.tex:40`
  "no lo esta", "continua").
- **c-141**: recibe el conteo de paginas (abajo).

### Compilacion y conteo de paginas (tareas 10.3 y 10.4)

- Entorno: Docker `texlive-thesis` (`latexmk main.tex`), en el arbol. Sin errores fatales
  (`grep -c "^!" main.log` = 0), `grep -c -i undefined main.log` = 0, `multiply defined` = 0,
  `grep -E "WARN|ERROR" main.blg` vacio; sin `Overfull \hbox` atribuible a la fila nueva de
  `tab:anexo_gemini_params` (los dos existentes son de las filas `candidate_count` y
  `safety_settings`).
- Antes: `abspage@last{102}` (cuerpo 94, anexos 8). Despues de T01-T16 y 9.1:
  `abspage@last{103}` (`Anexos` en p. 96: cuerpo 95, anexos 8), delta +1.
- Se aplico la compensacion **C3** (`05-arquitectura.tex:84`: se eliminaron la aposicion "redactadas
  con los cinco strings canonicos sin tildes" y la coda "momento en el cual la reserva de costo se
  imputa a la superficie de inferencia del backend") y se recompilo: el conteo **sigue en 103**
  (la ultima pagina del cuerpo, la bibliografia, esta al 70 %). Conteo final de c-130 para c-141:
  **103 paginas** (cuerpo 95, anexos 8), +2 sobre el tope de 101 (rama (a)); +1 sobre la
  prevision de ~+0,7 por el corte de pagina.
- `verify_citations.py`: PASS (59 entradas, 0 huerfanas). `tesis_para_agente.md` regenerado
  (contiene "0,5166" y "124 de los 200 casos"; no contiene "superior al 90").

**Estado**: grupo aplicado.

## Dictamen v1.1.0 - A2, B7b y B8 (c-131) - Metricas por etapa, por canal y exactitud laxa

**Origen**: change `c-131-metricas-por-etapa-canal-y-exactitud-laxa` (dictamen CONEAU 2026-10-22: VEREDICTO
punto 2 y recomendacion A2 condicionante; seccion 6, cuarta observacion; B7 parte de exactitud; B8). Aplicado
el **2026-10-25** en la rama `change/c-131-metricas-por-etapa-canal-y-exactitud-laxa`, cortada de `ramagonzalo`
en `dae365a` (merge del bloque de codigo de c-134). Posicion 3 del orden de la familia (G0.6). Sin commit
(lo crea el orquestador).

### Linea base (tareas 1.1 a 1.5)

- Entorno: imagen Docker `eval-tests` (Python 3.12.15, pytest 9.1.1, pytest-asyncio 1.4.0, **scipy 1.18.1**).
- Baseline de `evaluation/`: **216 passed, 1 skipped** (sin cache viva); con las caches colocadas el skip
  (`test_settings_tau_deriva_del_oof_del_corpus`) pasa a PASSED: 217. Total final: **310 passed**
  (217 + 93 pruebas nuevas).
- Paginas de partida: `abspage@last{103}`, `Anexos` en p. 96 (cuerpo 95, anexos 8): la tarea 1.3 dice 101;
  correccion: **102 tras c-144, 103 tras c-130**.
- c-130 aplicado (37/37 `[x]`, `efc3d3e`): se ejecutan los bloques 10 y 11.
- Hash del corpus (bloque 2): la copia de trabajo hasheaba `7408cd2a...62134` (CRLF por `core.autocrlf=true`);
  tras `.gitattributes` (`data/corpus_evaluacion_pseudonimizado.json text eol=lf`) y refrescar la copia vale
  `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`; `git diff --stat -- data/` vacio y blob
  `76590212b59cec5791094518b8169509461e500c` intacto. Es complementario de la normalizacion CRLF->LF que
  c-134 agrego a `_compute_corpus_hash`.

### Checkpoint de datos (bloque 3, gobernanza HIGH) - PROVISIONAL

El usuario pidio aplicar la familia sin detenerse y no respondio de forma explicita a las preguntas 1 a 3 del
design. Fecha: **2026-10-25**. Cada decision es **PROVISIONAL (pendiente de confirmacion del autor)**.

| Pregunta | Decision | Estado |
|---|---|---|
| 1 - recuperar las caches | **P1 via c-143**: se usan las copias congeladas de `evaluation/evidence/` (c-143, Luca, archivado 2026-10-23); no se pidieron al clon de Luca. Se copian a `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` (rutas ignoradas por git) | PROVISIONAL |
| 2 - corrida paga de reproduccion | **No autorizada (P2 no aplica)**: cero llamadas a Gemini, sin `GEMINI_API_KEY` real | PROVISIONAL |
| 3 - versionado de las caches (D8) | **Resuelto por c-143** con copias congeladas; no se toca `.gitignore` ni se agregan las copias vivas al indice. Bloque 8 marcado "no aplica" | PROVISIONAL |

Verificaciones (tareas 3.2 a 3.4 y 6.1): `evaluation/predicciones.json` es copia byte-identica de
`predicciones_hybrid-v3_2026-10-07.json` (SHA-256 `3fb5bacd04f2e9d303f580e4cf2ac4b4c6f2eab628a4fff80a6e1238029cd8fd`;
`corpus_hash` `1fd17d7e...`, 200 casos, `hybrid-v3`, `2026-10-07T22:22:01.947873+00:00`; 131 deterministicas y 69 de
Gemini). La FORCE-ESCALATE (`hybrid-v2`, SHA-256 `2d4f868ce1c01f8a528b29afc69dc541842f7f238c4932c3eee94a6f6298a775`,
`corpus_hash` `5f062e14...` que NO coincide con el vigente, 199 `gemini` + 1 `deterministic`) reproduce offline
`precision_gem(S) = 88/130 = 0,6769` y tau `0,5166`. Las 200 descripciones de ambas caches son identicas al corpus
pseudonimizado (0 diferencias). `evaluation/tests/test_huella_canonica.py` (7 pruebas) PASSED reproduce los
agregados canonicos; si falta la copia viva, busca la de `evaluation/evidence/` (asi corre PASSED en CI sin versionar
la viva). 6.2 y 6.4 no aplican.

### Codigo (bloques 4, 5 y 7; TDD estricto)

- `evaluation/metrics.py`: `aciertos_laxos`, `ResumenExactitud`, `resumen_exactitud`, `desglose_exactitud`,
  `ETAPAS_PIPELINE`, `ValorConfianza`, `distribucion_confianza`, `calibracion_por_etapa`.
- `evaluation/run_evaluation.py`: lineas de la exactitud laxa, secciones "Exactitud por etapa del pipeline",
  "Exactitud por canal de origen" y "Calibracion de la confianza" (antes de "## Tiempos"), linea de procedencia,
  `cargar_cache_meta`, validacion de alineacion `predicciones[i].caso_id == corpus[i].id` (`ValueError`).
- `evaluation/stats.py`: `ResultadoMcNemar` y `contraste_mcnemar`; `evaluation/deterministic_measurement.py`:
  `contraste_det_gem_en_s`, `contraste_para_cache`, `lineas_contraste_mcnemar` y el parametro `contraste` de
  `formatear_reporte_comparativo`.
- `evaluation/report.md` regenerado por cache hit (sin costo): **116 lineas agregadas, 0 eliminadas**; el SHA-256 del
  corpus pasa de `report.md:140` a **`report.md:256`**; las secciones nuevas de c-134 y las filas previas no cambian.
- `evaluation/README.md`, `docs/deterministic_calibration.md:234` (seccion McNemar, 39 lineas agregadas, 0 eliminadas).
- Desvio respecto del design: D10/6.1 describe la distribucion deterministica como `{0: 98, 0,5: 26, 0,75: 6, 1,0: 1}`;
  los valores reales son `{0,0: 90, 1/6: 8, 0,5: 26, 0,75: 6, 1,0: 1}` (los `98` casos de la banda `[0; 0,5)` son
  `90 + 8`). El test caracteriza los valores reales.

### Valores obtenidos (memo, Seccion 3.9; todos `vigente`)

- Exactitud estricta por etapa: deterministica `97/131 = 0,7405` IC `[0,6593; 0,8079]`; Gemini `50/69 = 0,7246`
  IC `[0,6095; 0,8161]`; fallback sin casos. **Coinciden con los derivados del design** (que quedaban `condicional`).
- Exactitud laxa: global `179/200 = 0,8950` IC `[0,8448; 0,9303]` (**supera el 85 %**, pero es metrica secundaria: no
  cambia el estado del objetivo 2; lo decide c-133); deterministica `119/131 = 0,9084`; Gemini `60/69 = 0,8696`.
- Por canal (estricta / laxa): llamada telefonica `53/81 = 0,6543` / `70/81 = 0,8642`; correo electronico
  `51/66 = 0,7727` / `61/66 = 0,9242`; formulario web `43/53 = 0,8113` / `48/53 = 0,9057`. Composicion distinta
  entre canales (multietiqueta `49/81`, `43/66`, `15/53`): no se atribuye la diferencia a la transcripcion.
- Bandas por etapa: determinista `98/75`, `26/19`, `6/2`, `0/0`, `1/1`; Gemini `0/0`, `0/0`, `0/0`, `31/22`, `38/28`
  (`0,7097` y `0,7368`, IC solapados). La suma reproduce `98/26/6/31/39` y `75/19/2/22/29`.
- Contingencia `76/53` y `124/94` con su composicion; tramo `>= 0,90`: global `46/13`, Gemini `45/13`,
  deterministica `1/0`.
- **McNemar entre etapas sobre `S`** (insumo de c-133 y c-142; no entra a la tesis): `|S| = 131`, pares `130`, excluido
  `R099`; 2x2 ambas `80`, `b = 16`, `c = 8`, ninguna `26`; deterministica `96/130`, Gemini `88/130`; chi-cuadrado
  corregido `2,0417` (p `0,1530`), p exacto `0,1516` (primario, `b + c = 24 < 25`). Las `131` predicciones
  deterministicas offline coinciden `131/131` con la etapa `deterministic` de la cache oficial.

### Tesis (bloques 10 y 11) y paginas

- `04-marco-metodologico.tex:79`, `07-resultados.tex` (marco metrico, `tab:exactitud-etapa-canal` nueva, `tab:bandas`
  reestructurada por etapa, introduccion y parrafo de calibracion), `08-discusion.tex` (`:16`, parrafo nuevo en `:18`,
  `:32`), `09-conclusiones.tex:37`, `11-aspectos-legales.tex:34`. Se retira la lectura de anti-calibracion del
  clasificador en su conjunto (0 coincidencias de "anti-calibr" y "calibracion invertida"). Sin cambios en
  `tab:cumplimiento-objetivos`, `tab:tiempos-canal`, `08:10`, `10-recomendaciones.tex` ni en el blob del corpus.
- Compilacion Docker `texlive-thesis` (`latexmk main.tex`, en el arbol): `grep -c "^!"` = 0, `undefined` = 0,
  `multiply defined` = 0, `main.blg` sin WARN/ERROR; `verify_citations.py` PASS (59 entradas, 0 huerfanas).
- **Paginas: antes `abspage@last{103}` (cuerpo 95, anexos 8); despues `abspage@last{103}`; `Anexos` en p. 96: cuerpo 95,
  anexos 8; delta 0** (prevision 0 a +0,9). Sin compensar habria sido **105** (+2: la metodologia desbordaba 3 lineas a
  una pagina nueva y las conclusiones 2 lineas). Compensaciones de D12 aplicadas: `tab:bandas` sin fila de totales,
  tablas en `\footnotesize` con fuente de una linea, la tabla nueva como flotante `[p]` ubicado tras la figura de la
  matriz (usa la pagina de flotantes que antes quedaba medio vacia) y recorte de redaccion en 04, 07:143/:190, 08 y
  09:37 (en 09:37 se abreviaron dos incisos propios del parrafo, sin tocar valores ni el estado del objetivo 2).
- Brecha frente al tope vigente de 101 (regla (a) provisional): **+2**, sin cambio respecto de c-130; rama (b)
  (cuerpo <= 100): cuerpo 95, margen 5.

### Consignas para otros changes

- **c-142**: el McNemar de `docs/deterministic_calibration.md:234` es su referencia en muestra; las caches viven en
  `evaluation/predicciones*.json` (copias ignoradas) y la evidencia en `evaluation/evidence/`. El runner ya emite por
  etapa y canal: se puede regenerar el reporte sin Gemini. No usar la cache `hybrid-v2` para sensibilidades sobre el
  corpus vigente (hash distinto).
- **c-132**: la exactitud laxa (`0,8950`) y su IC estan en el memo 3.9 para la sensibilidad del balance neto.
- **c-133**: leer la laxa como secundaria (no cambia el objetivo 2); exactitud por etapa `97/131` y `50/69` y McNemar
  (p exacto `0,1516`, no significativo, con sus salvedades) para la hipotesis subsidiaria de eficiencia; por canal
  para el objetivo 3. Cualquier cita `evaluation/report.md:N` debe tomar las lineas **actuales**: etapas `:11-13`
  (los design de c-133 citan `:9-10`, obsoleto), exactitud `:20-33`, SHA-256 `:256`. En `07-resultados.tex` el parrafo
  del marco metrico esta ahora en `:129` y la calibracion en `:190`.
- **c-134 (bloque de tesis)**: las lineas del reporte de "## Tiempos" se corrieron en bloque (`+116`; SHA-256 en `:256`);
  el memo ya fue actualizado. `07-resultados.tex` crecio +25 lineas antes de la seccion de tiempos por canal: revisar
  sus remisiones `:N`.
- **c-136**: la propuesta de aprendizaje activo debe alinearse a la lectura por etapa (la confianza de Gemini no
  discrimina en 0,85-1,00; la etapa de reglas no emite confianza utilizable).
- **c-141**: tope de paginas: total 103 (cuerpo 95); nota de `CHANGES.md` ("Pendientes planificados", punto 2) obsoleta,
  ya resuelta por c-99 y por el runner; consolidar `report.md:256`; recordar que `.gitattributes` es nuevo.

### Reversibilidad

Las tres decisiones de datos son reversibles: si el autor autoriza P2 se ejecuta la reproduccion con rutas separadas
(README de `evaluation/`); si decide versionar las caches vivas se aplica el bloque 8. El `.gitattributes` y los
valores del memo no dependen de esas decisiones.

**Estado**: grupo aplicado.

## Dictamen v1.1.0 - A5 analitica (c-142) - Sensibilidad fuera de muestra frente a los ajustes del clasificador

**Origen**: change `c-142-sensibilidad-fuera-de-muestra-ajustes-clasificador` (dictamen CONEAU 2026-10-22: VEREDICTO
punto 5; seccion 6, septima observacion; seccion 7, ultimo parrafo; recomendacion A5, mitad analitica). Aplicado el
**2026-10-25** en la rama `change/c-142-sensibilidad-fuera-de-muestra-ajustes-clasificador`, cortada de `ramagonzalo`
en `af32630` (merge de c-131). Posicion 4 del orden de la familia (G0.6). Sin commit (lo crea el orquestador).
Cero llamadas a Gemini en todo el change; sin `GEMINI_API_KEY` real.

### Linea base y pre-registro (tareas 1.1 a 1.7, 2.2 y 2.3)

- Entorno: imagen Docker `eval-tests` (Python 3.12.15, scipy 1.18.1, pytest 9.1.1). Baseline de `evaluation/`:
  **310 passed**. Total final: **451 passed, 2 skipped** (310 + 141 pruebas nuevas; los 2 skips son las pruebas
  de igualdad con los blobs del historial git, que se omiten sin `git`/historial, como en un clon superficial de CI).
  Cobertura de `evaluation/sensibilidad_ajustes.py`: **100 %** (589 sentencias, 0 sin cubrir).
- c-130 (37/37) y c-131 (81/81) aplicados; `contraste_mcnemar` (`stats.py:608`) y `contraste_det_gem_en_s`
  (`deterministic_measurement.py:809`) presentes. SHA-256 del corpus
  `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` (copia de trabajo con LF por `.gitattributes`).
- Hechos de 1.6 verificados con el git del host: blob de `keywords.py` en `7925903` = `858f1c6...`; vigente = `334a8ed...`;
  prompt en `a76851e^` = `1daceb3...`; vigente = `49267f4...`; `deterministic_score_threshold` = 0,5166. Ninguno cambio.
  El modulo recalcula los blobs vigentes sin git (`blob_git`) y el reporte los imprime.
- Paginas de partida: `abspage@last{103}`, `Anexos` en p. 96 (cuerpo 95, anexos 8), commit de partida `af32630`.
- Seccion del memo: **3.10** (3.7 c-130, 3.8 c-134, 3.9 c-131). El choque de la "3.7" quedo resuelto por G0.6.
- Tarea 2.3 (congelar el pre-registro): `git log --follow` sobre el `design.md` muestra `e378105` (propose) y `0977104`
  (renumeracion c-137 -> c-142); el segundo solo cambia identificadores de changes (c-125..c-137 -> c-130..c-142) y
  `90b0b9b` solo toco `specs/`. D2-D4, D8, D9 y T01-T08 **no cambiaron** en contenido. Commit de referencia del
  pre-registro: `0977104`. Ninguna variante se ejecuto sobre el corpus real antes de esta verificacion; los tests de
  caracterizacion sobre el corpus (6.6) se ejecutaron despues.

### Checkpoint del bloque 2 (gobernanza HIGH) - PROVISIONAL, 2026-10-25

El usuario pidio aplicar la familia sin detenerse y no respondio de forma explicita a las preguntas del design.
Cada decision queda **PROVISIONAL (pendiente de confirmacion del autor)**, con la recomendacion del design o la
decision ya registrada en G0.7.

| Open Question | Decision | Efecto en el apply |
|---|---|---|
| 1 - ablacion paga del prompt (nivel c, 138 invocaciones) | **NO autorizada** (G0.7a) | Tareas 8.9 y 8.10 "no aplica (sin autorizacion)"; 8.11 cumplida: el reporte declara el nivel c "no computado". El instrumento (`prompt --brazo`, gate, `comparar_brazos`) se implemento por TDD y no se invoco al proveedor. |
| 2 - incidentes de preproduccion | **No existen** (G0.7b; resuelto por c-144, item 6 de la Seccion 7 del memo) | 9.1 registra "no existe o no se localiza"; 9.2 a 9.5 "no aplica". Sin datos personales involucrados. |
| 3 - estado del objetivo especifico 6 | Se conserva "Alcanzado" con la salvedad en la evidencia (recomendacion del design) | T06 solo agrega evidencia; c-133 puede revisarlo. |
| 4 - variante por pliegues | Declarada **no factible** (recomendacion del design) | Memo, Seccion 7, punto 8; reporte `:70-72`; una oracion en la subseccion. |
| 5 - `generated_at` de la FORCE-ESCALATE | Aportado por c-143: `2026-10-07T20:33:03.438926+00:00` | Clasificacion D9: **"posterior"** (posterior a `2026-10-06T19:38:20Z`); consecuencia de 7.3: nivel b "no aplica". |
| 6 - versionado de salidas de corrida paga | No hay corrida paga; no aplica | Se agrego igual a `.gitignore` la regla `evaluation/predicciones_sensibilidad_prompt_*.json` (prevencion; los brazos escriben ahi). |
| 7 - paginas | Se acepto el impacto declarado (+1,0 a +1,4) | Medido +1; C3 no se aplico (total 104, no supera 104). |

Estado de datos de c-131 (tarea 2.2): rama **P1** via c-143. Cache oficial `hybrid-v3` (`corpus_hash` `1fd17d7e...`,
`generated_at` 2026-10-07T22:22:01Z) y FORCE-ESCALATE `hybrid-v2` (199 `gemini` + 1 `deterministic`, `corpus_hash`
`5f062e14...` distinto del vigente aunque las 200 descripciones coinciden). **Uso de la FORCE-ESCALATE**: la consigna de
c-131 pedia no usarla para sensibilidades sobre el corpus vigente por el hash distinto, pero E3, E4 y los niveles a y b
del design pre-registrado dependen de ella. Se uso con una guarda explicita (`verificar_cache_contra_corpus`:
identificador, descripcion y sector asignado de las 200 entradas iguales al corpus, 0 diferencias) y se comprobo que el
lado `V1` de E3 reproduce los `146/200` documentados (`docs/deterministic_calibration.md:89`) con 0 excluidos y que E4
sobre `V1` reproduce `b = 16`, `c = 8`, `p = 0,1516` (`docs/deterministic_calibration.md:234`). **Decision PROVISIONAL**;
si el autor la rechaza, E3 y E4 pasan a "no computable" (columna "Global" fuera de la tabla, rama "sin E3" de T01).

### Codigo (bloques 3 a 6 y 8; TDD estricto)

- `evaluation/sensibilidad_ajustes.py` (nuevo): `keyword_map_desde_fuente`, `clasificador_con_vocabulario` (adaptador
  sobre `DeterministicClassifier`), `ClasificadorLegadoPreC71` (replica L0), `regla_vigente`/`regla_legado`,
  `resumen_cortocircuito`, `descomposicion_pareada`, `exactitud_global_con_cache`, `comparar_linea_base_c71`
  (`LINEA_BASE_C71`), `clasificar_prompt_de_la_cache`, `calcular_nivel_a`/`comparar_corridas`/`calcular_nivel_b`,
  `formatear_reporte_sensibilidad`, `main` (async, fabricas inyectables), `seleccionar_casos_escalados`,
  `prompt_esperado`, `correr_brazo_prompt` (gate, SHA-256 del prompt, `cache_meta` ampliado), `comparar_brazos`,
  `verificar_cache_contra_corpus`, `blob_git`, `construir_procedencia` y la CLI (`python -m evaluation.sensibilidad_ajustes`;
  subcomando `prompt --brazo {vigente,sin-reglas} --confirm-paid`).
- `evaluation/data/sensibilidad_ajustes/` (`keywords_pre_c71.json`, `prompt_gemini_pre_c72.txt`, `procedencia.json`),
  regla `eol=lf` en `.gitattributes`, `evaluation/tests/test_sensibilidad_ajustes.py` (141 pruebas, de las cuales 2 se omiten sin historial git) y
  `evaluation/tests/test_sensibilidad_corpus.py` (2, caracterizacion sobre el corpus real).
- Caracterizacion 6.6: (a) `V1 + L1` = **131 cortocircuitados y 97 aciertos**; (b) `V0 + L0` reproduce **las 11 metricas**
  de la linea base de c-71 (72; 22/14/36; 37; 13/7/17; 55; 119; 126). Sin discrepancia que registrar.
- Desvio de 4.4: el design dice "9:1 -> cortocircuito", pero `w/(w + r + 1e-6)` con 9:1 da 0,8999999 < 0,90 (la constante
  deja el 9:1 apenas por debajo); la replica es fiel al codigo de `7925903` y no se toco. Las pruebas usan 10:1
  (cortocircuita, 0,9091) y 9:1 y 8:1 (no cortocircuitan). Por eso el cortocircuito de la epoca exige ganador >= 10 x segundo.
- Reportes: `evaluation/report_sensibilidad_ajustes.md` (97 lineas, regenerado offline; dos corridas dan archivo identico
  byte a byte; `report.md` y las caches oficiales sin cambios, verificado por SHA-256).

### Valores obtenidos (memo, Seccion 3.10) y ramas elegidas

| Salida | Valor | Rama / lectura |
|---|---|---|
| Configuracion evaluada `V1 + L1` | 131 casos, 97 aciertos, `0,7405` `[0,6593; 0,8079]` | reproduce lo esperado |
| **E1** `V0 + L1` | `n_A = 74` (cobertura `0,3700`), `k_A = 39`, `p_A = 0,5270` `[0,4148; 0,6366]` | **Rama A** (`p_A < 0,7405`); `D_A` = 21,3 puntos (exacto 21,34; con los extremos redondeados 21,35: empate de redondeo sin efecto) |
| Descomposicion pareada | comunes 67 (`V1` 38, `V0` 37); solo `V1` 64 (59 aciertos); solo `V0` 7 (2 aciertos); McNemar comunes `b = 1`, `c = 0`, `p` exacto 1,0000 | la diferencia viene de los 64 casos que solo resuelve `V1` |
| Referencia historica `V0 + L0` | 72 casos, 37 aciertos, `0,5139` `[0,4007; 0,6257]` | **Fiel**: las 11 metricas coinciden |
| **E3** (FORCE-ESCALATE) | `V1` 146/200, `V0` 128/200, 0 excluidos; `b = 18`, `c = 0`, `p < 0,001` | **Con E3** (columna "Global" en la tabla) |
| **E4** | `V1`: 96/130 frente a 88/130, `p = 0,1516` (reproduce c-131); `V0`: reglas 38/73 (0,5205) frente a Gemini 48/73 (0,6575), `b = 3`, `c = 13`, `p` exacto 0,0213 | con `V0` la etapa de reglas **no supera** a Gemini (resultado incomodo pre-anticipado en el design; se reporta igual) |
| Prompt, nivel a | los 3 motivadores (R002, R038, R015) estan entre los 69 escalados; Gemini 50/69 con todos y 48/66 sin ellos | **Nivel a** (el mayor disponible) |
| Prompt, nivel b | FORCE-ESCALATE "posterior"; comparacion pareada "no aplica" | |
| Prompt, nivel c | no computado (sin autorizacion) | |
| Variante por pliegues | no factible | |

Coinciden con lo pre-registrado en cuanto a ramas: la expectativa del design (rama A, cota de unos 20 puntos, y E4 con `V0`
adverso a las reglas) se cumple; el resultado de E1 (21,3 puntos) y el de la referencia historica (0,5139 frente a 0,51
documentado) son consistentes con lo inferido de la linea base de c-71.

### Tesis (bloques 12 y 13) y delta frente a c-144

| Item | Estado |
|---|---|
| T01 `subsec:sensibilidad-ajustes` + `tab:sensibilidad-ajustes` | aplicado (ramas: Fiel, A, con E3, nivel a) en `07-resultados.tex`, entre `subsec:calibracion` y `subsec:analisis-errores` |
| T02 | aplicado en la primera oracion de `subsec:calibracion` que da 0,7405; ademas, calificacion minima en la oracion que presenta `tab:exactitud-etapa-canal` (la tabla de c-131 no se edita) |
| T03 | aplicado en `05-arquitectura.tex:80` ("ambas estimadas dentro de la muestra") |
| T04 | aplicado al final del parrafo de c-130/c-144 en `08-discusion.tex` (sin la clausula de reglas del prompt: nivel a) |
| T05 | aplicado: item "Septimo" y cardinal "siete" en `subsec:limitaciones-estudio` (rama A, nivel a) |
| T06 | aplicado con una variante mas corta (`; dentro de la muestra, \autoref{subsec:sensibilidad-ajustes}`) porque el texto del design hacia crecer el total una pagina; el estado "Alcanzado" no cambia |
| T07 | aplicado ("La exactitud estricta, estimada dentro de la muestra, fue de ..."), con dos recortes de redaccion en `09:37` (" y sus valores" y "sin embargo,") sin perdida de contenido cientifico, para no agregar una pagina |
| T08 | **cubierto por c-144 `0c7f5bc`; verificado** (`12-anexos.tex:136` ya ubica el historial en el repositorio y `prompt_gemini_history` no aparece); el nivel es "a", asi que no corresponde la clausula de nivel b o c |
| R01 | **cubierto por c-144; verificado** (`evaluation/README.md`, "Advertencia Metodologica"); delta aplicado: remision a `python -m evaluation.sensibilidad_ajustes` y a `report_sensibilidad_ajustes.md`, seccion de comandos (offline y brazos pagos con gate) |
| R02 | **cubierto por c-144 en `:160`; `:162` con delta**: se agrego la remision a `evaluation/data/sensibilidad_ajustes/prompt_gemini_pre_c72.txt` |
| Declaracion de procedencia (05:78, 06:75, 08:18, 12:135), `subsec:corpus-independiente` | de c-144; no se reescriben |

Verificaciones: ninguna aparicion de "ausencia de sesgo" ni "demuestra" en la subseccion; "fuera de la muestra" solo en la
oracion que atribuye la estimacion a un corpus independiente; `grep -c "NO fue ajustado" evaluation/README.md` = 0;
`grep -rn prompt_gemini_history` sin resultados; sin cambios en `04-marco-metodologico.tex`, `00-resumen.tex`,
`10-recomendaciones.tex`, `12-anexos.tex`, `tab:bandas`, `tab:exactitud-etapa-canal` ni en otras filas de
`tab:cumplimiento-objetivos`. Barrido 12.2 (apariciones de `0,7405`, `97/131`, `0,6769`, `88/130` en `sections/`):
`05:80` (c-130; faltaba -> T03), `07` tabla de c-131 y su oracion (faltaba -> calificada en la oracion), `07` calibracion
(faltaba -> T02), `09:37` (c-131; faltaba -> T07); `08` no tiene esas cifras (el contraste de `08:10` es de c-133).

### Compilacion y conteo de paginas (tareas 14.1 y 14.2)

- Docker `texlive-thesis` (`latexmk main.tex`, en el arbol): `grep -c "^!" main.log` = 0, `undefined` = 0, `main.blg` sin
  WARN/ERROR, sin `Overfull \hbox` en `07-resultados.tex` (ni en `tab:sensibilidad-ajustes`); el unico en `09-conclusiones.tex`
  es el de la cabecera "Cumplimiento" (preexistente, columna de 1,7 cm). `verify_citations.py` PASS.
  `tesis_para_agente.md` regenerado (contiene "Sensibilidad al ajuste del clasificador", no contiene `prompt_gemini_history`).
- **Paginas: antes `abspage@last{103}` (cuerpo 95, anexos 8); despues `abspage@last{104}`; `Anexos` en p. 97: cuerpo 96,
  anexos 8; delta +1 / +1** (prevision +1,0 a +1,4). Sin los recortes de `09` y la variante de T06 habria sido 105 (+2: la
  seccion de conclusiones estaba al borde de pagina). Brecha frente al tope vigente de 101 (regla (a) provisional): **+3**;
  regla (b) (cuerpo <= 100): cuerpo 96, margen 4. **C3 no se aplico** (el total 104 no supera 104).

### Mapeo del dictamen

VEREDICTO punto 5, seccion 6 (septima observacion), seccion 7 (ultimo parrafo) y A5 (mitad analitica) -> D1-D15
(analisis, variantes pre-registradas, artefactos con procedencia, reporte, memo, paginas), T01-T08 y R01-R02. La mitad
declarativa de A5 es de c-130 y c-144.

### Consignas para otros changes

- **c-132**: E3 (146 -> 128 aciertos sobre 200 con Gemini fijo, `p < 0,001`) puede usarse como escenario de sensibilidad
  del balance neto; no es obligatorio.
- **c-133**: (1) calificar `0,7405` frente a `0,6769` como estimaciones dentro de la muestra con remision a
  `subsec:sensibilidad-ajustes` en `08:10`; (2) **E4**: con el vocabulario previo la etapa de reglas no supera a Gemini en
  los casos que resuelve (0,5205 frente a 0,6575; `p` exacto 0,0213), de modo que la ventaja del esquema hibrido en `S`
  depende del vocabulario ajustado con el corpus: considerarlo al rotular la hipotesis subsidiaria de eficiencia; (3)
  la FORCE-ESCALATE es **posterior** a las reglas de frontera (`generated_at` 2026-10-07T20:33:03Z), por lo que la
  comparacion `0,7405` frente a `0,6769` no mezcla versiones del prompt por esa via (la fecha no prueba que archivo de
  prompt cargo esa corrida); (4) estado del objetivo 6: se conserva "Alcanzado" (OQ3 provisional); (5) cardinal de
  `subsec:limitaciones-estudio`: ahora **siete** items; el item que agregue c-133 (T18) parte de "siete" y debe pasar a
  "ocho".
- **c-135**: `07:6` debe enumerar la subseccion nueva (`subsec:sensibilidad-ajustes`, 8.5) entre las vigentes.
- **c-136**: conservar la validacion sobre un corpus independiente como linea de trabajo (no hay conjunto de
  preproduccion; item 6 de la Seccion 7).
- **c-141**: incorporar A5 y c-142 a la trazabilidad y a las precondiciones; libro mayor de paginas (fila `+c-142`: 104 /
  96 / 8, +1 / +1); `evaluation/report.md` y las caches oficiales no cambiaron (SHA-256 verificado); `.gitattributes`
  tiene ahora una segunda regla (`evaluation/data/sensibilidad_ajustes/*`); la copia local de `report_sensibilidad_ajustes.md`
  esta con CRLF como `report.md`. Una autorizacion posterior de la ablacion paga se registra en G0.7a y exige correr los dos
  brazos antes de cerrar (el instrumento esta listo).
- **c-137** (ortotipografia): las tildes de los textos T01-T08 ya son las normativas.

### Reversibilidad

`git checkout <commit-previo> -- evaluation/ .gitattributes .gitignore "docs/Tesis/v10 (IA)/" docs/anexo_h_prompt_gemini.md
docs/Tesis/Correcciones/numeros-canonicos.md docs/Tesis/Correcciones/dictamen-correcciones.md`, regenerar el render y
recompilar. Las decisiones PROVISIONALES (OQ1 a OQ7 y el uso de la FORCE-ESCALATE) se pueden revertir sin tocar los valores
canonicos: si se rechaza la FORCE-ESCALATE, E3 y E4 pasan a "no computable" y la tabla pierde su cuarta columna.

**Estado**: grupo aplicado.

## Dictamen v1.1.0 - A3 (c-132) - Balance neto entre el ahorro de registro y las derivaciones erroneas

**Origen**: change `c-132-balance-neto-derivaciones-erroneas` (dictamen CONEAU 2026-10-22: VEREDICTO punto 3, seccion 7 (c)
y RECOMENDACION A3). Aplicado el **2026-10-25** en la rama `change/c-132-balance-neto-derivaciones-erroneas`, cortada de
`ramagonzalo` en `31c143a` (merge de c-142). Posicion 5 del orden de la familia (G0.6). Solo documento (gobernanza LOW):
cero llamadas a Gemini, sin codigo, sin tags. Sin commit (lo crea el orquestador).

**A3 - Balance neto de derivaciones erroneas - APLICADO por c-132 (2026-10-25).**

### Open Questions del design - PROVISIONAL, 2026-10-25 (pendiente de confirmacion del autor)

El usuario pidio aplicar la familia sin detenerse y no respondio de forma explicita a las preguntas del design. Decisiones del
orquestador, **PROVISIONALES**:

| Open Question | Decision | Efecto en el apply |
|---|---|---|
| OQ1 - tope de paginas | Lo decide c-141. Hoy rige provisionalmente la rama (a) total <= 101 (G0.1), ya superada: la base de este change era 104. c-132 apunta a <= +1 y registra el exceso. | Medido +1 (total 105); ver "Paginas" y el libro mayor. |
| OQ2 - correccion colateral T13 (`09-conclusiones.tex`, "costo operativo dominado por el consumo de API de inferencia") | **Se incluye** (recomendacion del design). | T13 aplicado en una variante mas corta (ver "Mapeo T1-T14"). |
| OQ3 - orden respecto de c-131 | **Rama "laxa disponible" de D4**: c-131 registro la exactitud laxa (`179/200 = 0,8950`, IC `[0,8448; 0,9303]`, memo 3.9). No se usa el fallback. | Laxa en la nota de `tab:balance-neto`, una frase con el balance laxo y las filas laxas en el memo 3.11 (`condicional`). |

### Linea base y coordinacion (bloque 1)

- Paginas de partida: `abspage@last{104}`, `Anexos` en p. 97 (cuerpo 96, anexos 8). La tarea 1.1 dice 101: **102 tras c-144, 103 tras c-130,
  103 tras c-131, 104 tras c-142**. Inicio de capitulos (`main.toc`): 1:11, 2:18, 3:26, 4:31, 5:40, 6:51, 7:61, 8:67, 9:75, 10:83, 11:86.
- Rama de D4 (tarea 1.2): **laxa disponible** (`grep -n -i "laxa" numeros-canonicos.md` -> Seccion 3.9, c-131).
- Anclas de D6 (tarea 1.3): las 12 anclas existian (1 ocurrencia cada una). Adaptaciones al estado vigente: la sexta limitacion se
  extiende dentro de un listado que ahora tiene **siete** limitaciones (c-142; el check "presenta seis limitaciones" se lee
  "siete limitaciones", y el cardinal no cambia); `10-recomendaciones.tex` tiene **9** `\subsection` en la base (no 8) y sigue en 9.
- Conteo de las conclusiones del resumen (tarea 1.4): ES 34, EN 31 (esperado 34 y 31).

### Memo (bloque 2, Gate 0)

Seccion **3.11** de `numeros-canonicos.md` ("Balance neto de derivaciones erroneas (c-132)"; 3.7 c-130, 3.8 c-134, 3.9 c-131,
3.10 c-142), mas la linea de upsert de la cabecera. Solo agregados (`git diff -U0 | grep "^-[^-]"` vacio). El comando de referencia
reproduce la tabla de D3 (10/15/20/26,5 %: `a*` y `B`), el escenario central (304,3; 50,7 h; 76,1 h; `Delta e*` 14,6 / 7,3 / 4,9)
y, en la rama laxa, `B` laxo (`e_aut = 0,105`): 10 %: +31,1 / +30,0 / +28,9; 15 %: +42,1 / +52,1 / +62,0; 20 %: +53,2 / +74,1 / +95,1;
26,5 %: +67,5 / +102,8 / +138,0 (todos `condicional`). Insumos `vigente`: `N`, `Delta t`, `e_aut`; `condicional`: `e_man`, `c`, la rejilla y
los valores derivados. Consigna de c-142: la sensibilidad E3 (`128/200` y `146/200` con Gemini fijo) se registro en el memo como
lectura opcional (`B(15 %)` = -14,1 / -60,4 / -106,7 h y +5,7 / -20,7 / -47,2 h) y **no entra a la tesis**.

### Mapeo T1-T14 (bloques 3 a 5)

| Item | Archivo | Estado |
|---|---|---|
| Subseccion `subsec:balance-neto` (9.5) y `tab:balance-neto` (Tabla 17) | `08-discusion.tex`, entre `subsec:implicancias-practicas` y `subsec:reflexiones-generalizacion` (que pasa de 9.5 a 9.6) | aplicado, con la rama laxa de D4 |
| T1, T2 | `00-resumen.tex` (conclusion ES y EN) | aplicado: viabilidad tecnica y economica; operativa condicional; 34 y 31 palabras |
| T3 | `01-introduccion.tex`, planteamiento | aplicado (15 % preliminar no re-medido, "brutas", sin "costo de oportunidad significativo"); neto +14 palabras (<= 15) |
| T4 | `01-introduccion.tex`, justificacion organizacional | aplicado con el borrador del design |
| T5 | `08-discusion.tex`, `subsec:interpretacion-resultados` | S1 y S2 retiradas; "32,2 horas-persona brutas ---unas cuatro jornadas laborales de un operador---"; S4 reemplazada por la remision; nota al pie intacta |
| T6 | `08-discusion.tex`, sexta limitacion | aplicado ("exactitud de ese brazo" en lugar de "del brazo manual", para no repetir) |
| T7 | `08-discusion.tex`, implicancias | aplicado; ademas "libera al personal tecnico" -> "puede liberar al personal tecnico" (coherencia con el saldo neto; +1 palabra) |
| T8, T9 | `08-discusion.tex` | aplicados |
| T10 | `09-conclusiones.tex`, parrafo inicial | aplicado en variante corta: "...con viabilidad operativa condicionada al balance neto (\autoref{subsec:balance-neto})" |
| T11 | `09-conclusiones.tex`, evaluacion comparativa | **variante**: "el sistema libera tiempo bruto de registro, cuyo saldo neto esta indeterminado (\autoref{subsec:balance-neto})" en lugar de "...depende del costo de las derivaciones erroneas": ahorra la linea que desbordaba el capitulo a una pagina nueva |
| T12 | `09-conclusiones.tex` | aplicado ("tecnicamente viable") |
| T13 | `09-conclusiones.tex`, aportes (OQ2) | aplicado en variante corta: "su costo monetario, dominado por la infraestructura y no por la inferencia, se cuantifica en la \autoref{subsec:implicancias-practicas}" |
| T14 | `10-recomendaciones.tex`, `subsec:estudios-replicacion` | aplicado (21 palabras); c-136 NO debe duplicarla |

Sin tasa manual presentada como medida: el unico valor atribuido al flujo manual es el 15 % preliminar; 10 %, 20 % y 26,5 % se rotulan
"supuestos de sensibilidad". Prosa de la subseccion: **492 palabras** con el comando de la tarea 3.6 (incluye la nota de la tabla y el
texto matematico en linea; el objetivo era <= 280 y el maximo 320): excede el presupuesto de prosa del design, pero el delta de paginas
cumple (ver abajo); si c-141 necesita paginas, la nota de la tabla y la frase laxa son las palancas.
`grep -c "absorbe la carga rutinaria"` y `"preserva la calidad del servicio"` sobre `sections/*.tex` = 0; `32,2` se conserva.

### Revision del autor (gobernanza LOW con recomendacion de revision) - PROVISIONAL

**Quedan marcadas para revision del autor antes de la release** la redaccion final del **resumen/abstract** (T1 y T2) y de la
**conclusion** (T10 a T13 y el parrafo inicial de `09-conclusiones.tex`). Ningun valor vigente cambio. Reversible: si una replicacion
mide un balance positivo, la viabilidad operativa puede enunciarse como sostenida (upsert del memo 3.11 y propagacion inversa de T1, T2 y T10).

### Compilacion y paginas (bloque 6)

- Docker `texlive-thesis` (`latexmk main.tex`, en el arbol): `grep -c "^!" main.log` = 0, `undefined` = 0, `multiply defined` = 0, `main.blg` sin
  WARN/ERROR, sin `Overfull \hbox` en `08-discusion.tex` (ni en `tab:balance-neto`); el unico en `09-conclusiones.tex` es el de la cabecera
  "Cumplimiento" (preexistente). `verify_citations.py` PASS (59 entradas, 0 huerfanas). `tesis_para_agente.md` regenerado (contiene la
  subseccion; 0 apariciones de "absorbe la carga rutinaria").
- **Paginas: antes `abspage@last{104}` (cuerpo 96, anexos 8); despues `abspage@last{105}`; `Anexos` en p. 98: cuerpo 97, anexos 8; delta +1 / +1**
  (prevision +1 a +3, objetivo <= +1). Primera compilacion: 106 (+2: la subseccion agrego 1 pagina a la discusion y las conclusiones
  desbordaban una linea a una pagina nueva); las variantes cortas de T10, T11 y T13 recuperaron la pagina. Inicio de capitulos despues: 1:11 ... 9:75,
  10:84, 11:87 (el capitulo 9 pasa de 8 a 9 paginas; el 10 y el 11 conservan su extension). Brecha frente al tope vigente de 101 (regla (a)
  provisional): **+4**; regla (b) (cuerpo <= 100): cuerpo 97, margen 3.
- Resumen: conteo con la regla de c-106 (prosa, math como una palabra, sin "Palabras clave"): **ES 264 -> 264, EN 252 -> 252** (delta 0).
  Exceso preexistente frente a las 250 palabras del requisito (+14 ES, +2 EN) que c-132 no agrava ni corrige; lo ajusta c-133 o c-141.

### Mapeo del dictamen

VEREDICTO punto 3, seccion 7 (c) y RECOMENDACION A3 -> subseccion `subsec:balance-neto` (formula, tabla, indeterminacion), T1 a T14 y memo 3.11.

### Consignas para otros changes

- **c-133**: `subsec:balance-neto` y `tab:balance-neto` existen con esos nombres; citar como evidencia en `tab:cumplimiento-objetivos`. El umbral del
  85 % equivale a la paridad con el 15 % manual y `a*` (77,7 a 80,1 % para 15 % y 10-15 min) es menos exigente (esta dicho en la subseccion); la
  exactitud laxa (89,5 %) supera los doce `a*` pero es la cota favorable. La clausula de viabilidad de `09:6` ya dice "tecnicamente viable ... operativa
  condicionada"; la frase del objetivo 2 y la tabla siguen siendo de c-133. La seccion siguiente del memo es la 3.12.
- **c-136**: la linea de replicacion (registro por caso de la derivacion manual, etiquetadores distintos, cronometraje) ya esta en `subsec:estudios-replicacion`
  (T14); no duplicarla. `10-recomendaciones.tex` tiene 9 subsecciones.
- **c-141**: libro mayor (fila `+c-132`: 105 / 97 / 8, +1 / +1); revision del autor pendiente sobre resumen y conclusion; el resumen ES conserva 264 palabras
  (exceso preexistente); renders regenerados con 105 paginas; `Tabla 17` es la tabla nueva y la de cumplimiento pasa a la 18 (las remisiones son por rotulo).
  Reflexiones sobre la generalizacion pasa de 9.5 a 9.6 (los registros historicos no se reescriben).
- **c-137** (ortotipografia): el texto nuevo lleva tildes; quedan palabras sin tilde preexistentes fuera de lo reescrito (p. ej. "derivacion erronea" en la primera
  oracion del planteamiento, `continua` y `antiguedad` en las implicancias).

### Reversibilidad

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex" "docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex"
"docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex" "docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex"
"docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex" docs/Tesis/Correcciones/numeros-canonicos.md docs/Tesis/Correcciones/dictamen-correcciones.md`,
regenerar el render y recompilar. Si otro change cito `subsec:balance-neto` o `tab:balance-neto`, retirar esas remisiones en el mismo rollback.

**Estado**: grupo aplicado.
