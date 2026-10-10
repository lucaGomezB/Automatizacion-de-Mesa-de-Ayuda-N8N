# Correcciones del dictamen (CONEAU) — registro

> Registro de las correcciones de la tesis surgidas del dictamen (perfil evaluador
> `Prompt2.docx`). Se aplican a medida que el autor las provee. Lo que no se puede
> resolver todavía se anota abajo para incorporarlo luego al proyecto / tesis.
>
> Estado: 2026-10-09.

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

### P1.0 — `tiempo_manual_s`: medición real redondeada al alza (declarar + acotar)
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

### P1. Reconciliar el Cap. 7 (Resultados) y la metodología con el corpus real
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
| Automatizado (media) | 18,2 s | 14,8 s |
| Reducción | 89,0 % | 75,9 % |
| Wilcoxon | W=0, r=1,00 | W=335, p=2,05e-32, r=0,983 |

**Datos reales disponibles (listos para aplicar)**:
- Distribución primaria: Sistemas 16, Soporte Técnico Hardware 85, Soporte Técnico
  Software 67, Seguridad Informática 31, Bases de Datos 1.
- Canales: correo 66, web 53, teléfono 81.
- Tiempos: manual media 61,6 s (mediana 50,0; sd 44,9; rango 10–300) vs auto media
  14,8 s (mediana 12,4; sd 13,1; rango 0,5–65,8); reducción 75,9 %.
- Clasificación (`evaluation/report.md`): exactitud estricta 73,5 % (147/200),
  macro-F1 0,5207, micro-F1 0,6654, subset accuracy 0,43, Hamming 0,3586; etapas
  deterministic 131 / Gemini 69.
- Fuentes: `data/corpus_evaluacion_pseudonimizado.json`, `evaluation/report.md`.

### P2. Anexo H — versión del modelo
El título de `docs/anexo_h_prompt_gemini.md` dice "Gemini 2.5 Flash" mientras
`README.md` y el código usan `gemini-3.6-flash`. Alinear.

### P3. (a completar)
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
