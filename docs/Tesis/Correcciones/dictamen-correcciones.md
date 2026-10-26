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

### P4. Sin observaciones pendientes al 2026-10-26
El bloque P se cerro con P1 a P3. No existe material fuente que complete P4 y no se inventan observaciones: si el autor aporta nuevos items del dictamen, se agregan aqui con su procedencia. Estado: sin observaciones pendientes.

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
- **Trazabilidad `v1.2.0` (c-141, 2026-10-26)**: el tag anotado **`v1.2.0`** se creo sobre el commit **`a49d035c67b32ae17e633ec04b09ecdd2781aac6`** (C1, `docs(tesis): integrar la FASE 36 y publicar v1.2.0 (c-141)`) y se publico en `origin` junto con `ramagonzalo` (`git ls-remote --tags` lo devuelve). Ese commit integra la FASE 36 (c-130 a c-139 y c-142): cierra las recomendaciones A1-A5 y B4-B16 del dictamen CONEAU del 2026-10-22 sobre `v1.1.0` (matriz de cobertura en este registro), con el Anexo I actualizado, el render y la base de conocimiento sincronizados y 109 paginas (cuerpo 100, anexos 9; regla (b), decision del equipo del 2026-10-26). c-140 no se aplico (excluido provisionalmente) y por eso no hubo prueba de humo. El hash completo quedo consignado en el Anexo B (`12-anexos.tex`, Repositorio de codigo fuente).
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

#### G0.1 - Actualizacion 2026-10-26: regla (b) CONFIRMADA por el usuario

**Estado: CONFIRMADA por el usuario (Gonzalo Sevilla, 2026-10-26).** Esta entrada se agrega
sin reescribir la entrada provisional anterior (que queda como historia de la decision).

| Campo | Valor |
|---|---|
| Regla de medicion | **Cuerpo sin anexos** (rama (b)): pagina del encabezado "Anexos" en `main.toc` (`\contentsline {section}{Anexos}{N}`) menos 1 |
| Valor | **cuerpo sin anexos <= 100, anexos sin limite** |
| Fuente | Decision del equipo (no consta exigencia de la catedra) |
| Fecha | 2026-10-26 |
| Palanca de formato P7 (bibliografia compacta) | **Aprobada** por el usuario |
| Compensacion C3 de c-142 (tabla `tab:sensibilidad-ajustes` a un anexo) | Queda disponible, pero no hace falta si P7 alcanza (alcanzo; ver "Compactacion P7") |

Decision textual del usuario: "Adopta la regla (b): cuerpo sin anexos <= 100, anexos sin
limite. Aplica la palanca P7 (bibliografia compacta) y segui con c-141 hasta antes del tag y
el PR." Consecuencia: la brecha de la rama (a) (+9) deja de ser la vara de medir; rige el
margen de la regla (b) (100 - cuerpo). Las tareas 3.4 y 3.5 de c-141 (rama (a)) quedan "no
aplica (regla (b) confirmada el 2026-10-26)". P6 y P8 no se aplican.

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

**Actualizacion 2026-10-25 (c-141, tramo de integracion; decision del orquestador, registrada al aplicar el tramo el 2026-10-26)**: c-140 excluido provisionalmente de la integracion; decision del usuario pendiente. Estado de c-140: 0/73 tareas, sin ediciones de prosa de la tesis. Si el usuario lo incluye, sus bloques de codigo, la prueba de humo (tarea 8.3) y su texto de tesis (posicion 12 de D1, antes de c-137) obligan a repetir la regresion cruzada y la pasada ortotipografica corta; si lo excluye, se archiva como NO REALIZADO con `openspec archive c-140-endurecimiento-tecnico-tls-reintentos-e2e -y --skip-specs` (tarea 2.9) y los descuentos del criterio 5 quedan como limitacion declarada (ver la fila "Criterio 5 (residual)" de la matriz de cobertura).

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
| `+c-133` (`change/c-133-hipotesis-objetivos-metrica-primaria`) | sin commit (lo crea el orquestador) | 105 | 97 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{105}`; `Anexos` en p. 98; brecha frente a 101: +4 (sin compensar habria sido 107); rama (b): cuerpo 97, margen 3 |
| `+c-134 tesis` (`change/c-134-contrastes-estadisticos-y-desagregado-canal`) | sin commit (lo crea el orquestador) | 105 | 97 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{105}`; `Anexos` en p. 98; brecha frente a 101: +4 (la primera compilacion dio 108, +3; las compensaciones dentro de los mismos pasajes devolvieron las tres paginas); rama (b): cuerpo 97, margen 3 |
| `+c-138` (`change/c-138-estado-del-arte-calibracion-y-cascadas`) | sin commit (lo crea el orquestador) | 108 | 100 | 8 | +3 | +3 | (a) total <= 101 | Medido: `abspage@last{108}`; `Anexos` en p. 101; brecha frente a 101: +7; rama (b): cuerpo 100, margen 0 |
| `+c-136` (`change/c-136-recomendaciones-lineas-faltantes`) | sin commit (lo crea el orquestador) | 108 | 100 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{108}`; `Anexos` en p. 101; brecha frente a 101: +7; rama (b): cuerpo 100, margen 0 (el capitulo de recomendaciones ya ocupaba 5 paginas, 89 a 93, con unas 21 lineas libres en la ultima; el agregado neto las consume y no abre una sexta) |
| `+c-135` (`change/c-135-cronologia-y-consistencia-redaccional`) | sin commit (lo crea el orquestador) | 108 | 100 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{108}`; `Anexos` en p. 101; brecha frente a 101: +7; rama (b): cuerpo 100, margen 0 (la figura del cronograma va al Anexo A porque el capitulo 6 no tenia holgura: en 6.6 habria dado 109 o 110) |
| `+c-139` (`change/c-139-correspondencia-texto-fuente-y-metadatos`) | sin commit (lo crea el orquestador) | 109 | 101 | 8 | +1 | +1 | (a) total <= 101 | Medido: `abspage@last{109}`; `Anexos` en p. 102; brecha frente a 101: +8; rama (b): cuerpo 101, margen -1 (cuerpo neutral: Referencias bibliograficas empieza en la p. 94 antes y despues; la bibliografia pasa de 7 a 8 paginas por las 8 entradas nuevas y los metadatos; la primera compilacion dio 111 y los recortes dentro de los parrafos editados recuperaron 2 paginas del cuerpo; palancas tipograficas para c-141) |
| `+c-137` (`change/c-137-revision-ortotipografica`) | sin commit (lo crea el orquestador) | 109 | 101 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{109}`; `Anexos` en p. 102; brecha frente a 101: +8; rama (b): cuerpo 101, margen -1 (neutral por construccion: el cambio es diacritico; `Referencias bibliograficas` empieza en la p. 94 antes y despues; solo se desplazo una linea de la p. 26 a la p. 27 por las comillas de las cadenas A1-A4 y B1, sin cambiar el total; el tope lo decide c-141) |
| integrado (pre-compactacion) (`change/c-141-integracion-release-v1-2-0`; tarea 3.2) | sin commit (lo crea el orquestador) | 110 | 101 | 9 | +1 | 0 | (a) total <= 101 | Medido: `abspage@last{110}`; `Anexos` en p. 102; delta frente a `+c-137` (109 / 101 / 8): +1 total y +1 anexos por el Anexo I (tarea 3.1: Tabla 20 de trazabilidad; prevision de D10 +0,1 a +0,6, cuantizada a una pagina porque la p. 109 estaba llena); **brecha frente a 101: +9**; **regla (b): cuerpo 101, margen -1** (`Referencias bibliograficas` empieza en la p. 94 y ocupa 8 paginas, la ultima con 14 lineas); acumulado de la familia: +8 total / +7 cuerpo / +1 anexos sobre `+c-144` (102 / 94 / 8) y +9 / +8 / +1 sobre la base `v1.1.1`; sin compactar nada (checkpoint HIGH de 3.4 pendiente) |
| compactacion P7 (`change/c-141-integracion-release-v1-2-0`; tareas 3.3 a 3.6) | sin commit (lo crea el orquestador) | 109 | 100 | 9 | -1 | -1 | (b) cuerpo sin anexos <= 100 (confirmada 2026-10-26) | Medido: `abspage@last{109}`; `Anexos` en p. 101; delta frente a "integrado (pre-compactacion)" (110 / 101 / 9): -1 total y -1 cuerpo; **regla (b): cuerpo 100, margen 0 (cumple)**; `Referencias bibliograficas` sigue empezando en la p. 94 y pasa de 8 paginas (la ultima con 14 lineas) a 7 (la ultima, p. 100, con una sola entrada de 3 lineas); anexos 9 sin cambio; brecha frente a la rama (a) (101): +8, ya no vigente; acumulado de la familia: +7 total / +6 cuerpo / +1 anexos sobre `+c-144` (102 / 94 / 8) y +8 / +7 / +1 sobre la base `v1.1.1`. Palanca P7: una linea en el preambulo (ver "Compactacion P7") |
| release v1.2.0 (C1) (`change/c-141-integracion-release-v1-2-0`; tareas 5.1 y 5.2) | sin commit (lo crea el orquestador) | 109 | 100 | 9 | 0 | 0 | (b) cuerpo sin anexos <= 100 (confirmada 2026-10-26) | Medido: `abspage@last{109}`; `Anexos` en p. 101 (`main.toc`); `Referencias bibliograficas` en p. 94; saltos de pagina de `pdftotext` 109; delta frente a "compactacion P7" (109 / 100 / 9): 0 / 0 (el cambio del tag y del titulo de `Gomez2026_repositorio` retira dos lineas del Anexo B y no mueve ninguna pagina); **regla (b): cuerpo 100, margen 0 (cumple)**; coincide con el cierre del libro mayor de la tarea 6.4 |
| release v1.2.0 (C2) (`change/c-141-integracion-release-v1-2-0`; tareas 8.6 y 8.7) | sin commit (lo crea el orquestador) | 109 | 100 | 9 | 0 | 0 | (b) cuerpo sin anexos <= 100 (confirmada 2026-10-26) | Medido: `abspage@last{109}`; `Anexos` en p. 101 (`main.toc`); saltos de pagina de `pdftotext` 109; delta frente a "release v1.2.0 (C1)" (109 / 100 / 9): 0 / 0 (la linea del hash cabe en la p. 102 del Anexo B y no mueve ninguna pagina); **regla (b): cuerpo 100, margen 0 (cumple)**; el conteo final de la release es el de C1 |

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

**Actualizacion 2026-10-25 (c-134, bloque de tesis)**: los grupos 6 a 8 se aplicaron el mismo dia en la rama
`change/c-134-contrastes-estadisticos-y-desagregado-canal` (sobre `0ac3160`, ya con c-133); ver la seccion
"Dictamen v1.1.0 - B7a, B12 y B13b (c-134, bloque de tesis)" al final de este registro. La fila `+c-134 tesis`
del libro mayor (105 / 97 / 8, delta 0 / 0) esta en la tabla de arriba.

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

### Checkpoint de autores (tarea 1.4) - CONFIRMADO el 2026-10-26 (OQ2 y OQ3; OQ4 superada por c-145 G)

El usuario pidio aplicar sin detenerse y no respondio de forma explicita a las Open Questions.
Fecha: 2026-10-25. Cada decision es **PROVISIONAL (default del design, pendiente de
confirmacion del autor)**.

| OQ | Tema | Decision | Estado |
|---|---|---|---|
| OQ1 (D9) | Procedencia de los ajustes sobre el corpus | **RESUELTA por c-144** (`0c7f5bc`): los autores ya declararon la procedencia real al fusionarlo en `main`. T04, T12, T13 y T14 no se reescriben; se ejecutan solo sus verificaciones | Resuelta (hecho) |
| OQ2 (D7) | Alcance de la salvaguarda legal; reasignacion solo por REST | Default del design: se aplica T15. **Confirmada por el autor (2026-10-26)**. Verificacion en codigo: la reasignacion esta en `PATCH /api/v1/incidentes/{id}` (campo `sector_id`) y en `PATCH /api/v1/clasificaciones/{log_id}/validar`; la interfaz web solo la expone para casos derivados; N8N no reasigna; no hay guarda de rol sobre `sector_id`, de modo que un `usuario_final` puede reasignar su propio incidente por REST. El texto de `11-aspectos-legales.tex:34` es exacto | Confirmada |
| OQ3 (D12) | Comentarios y test en `App/Backend` | Si: bloque 7 aplicado | Confirmada |
| OQ4 (D11) | Editar `CLAUDE.md` y `openspec/config.yaml` (solo las lineas del gate) | Si: bloque 8 aplicado | Superada por c-145 G |
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

Tarea 9.1 (roles, agregada por Luca en `2236b26`): aplicada en `04-marco-metodologico.tex:95`.
Evidencia `git shortlog -sne` sobre `224fa16` (re-medida el 2026-10-26): lucaGomezB 418,
GonzaloSevilla22 93, Gonzalo Sevilla 52, Luca Gomez 35, dependabot[bot] 1; **ningun commit a
nombre de Carla Bustos** y ninguna mencion en los mensajes (`git log --grep`). Carla pasa a
revisora de la tesis y colaboradora en anexos y corroboracion de fuentes. **Correccion del
2026-10-26, confirmada por el autor**: la redaccion anterior atribuia a Luca Gomez "el desarrollo
del modulo Python y el modelado de la base de datos" y a Gonzalo Sevilla "la integracion
telefonica mediante Twilio"; el historial la contradice en tres puntos. El modulo inicial
`Gestion_Incidentes` (`7db7fe1`, 2026-05-20) y el frontend inicial (`ca8e2b6`, 2026-05-21) los
firmo `GonzaloSevilla22`, igual que las migraciones iniciales (`ec92689`); todos los commits con
Twilio son de `lucaGomezB`. El texto vigente atribuye la coordinacion general, la integracion de
componentes y la integracion telefonica a Luca Gomez, y la implementacion inicial del modulo
Python, el modelado inicial de la base de datos, el frontend y la configuracion del flujo N8N a
Gonzalo Sevilla. Se conserva la supervision del director.

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

### Checkpoint del bloque 2 (gobernanza HIGH) - PROVISIONAL, 2026-10-25 (FORCE-ESCALATE confirmada el 2026-10-26)

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
sobre `V1` reproduce `b = 16`, `c = 8`, `p = 0,1516` (`docs/deterministic_calibration.md:234`). **Decision CONFIRMADA por el autor (2026-10-26)**: se acepta el uso de la FORCE-ESCALATE. Se explicita la tension con la consigna de c-131 (que pedia no usarla para sensibilidades sobre el corpus vigente): la excepcion se sostiene en que la guarda verifica identificador, descripcion y sector asignado de las 200 entradas (0 diferencias) y en que el lado `V1` de E3 reproduce los `146/200` documentados. `evaluation/report_sensibilidad_ajustes.md` declara el `corpus_hash` distinto en la seccion de procedencia. Si en el futuro se rechazara, E3 y E4 pasan a "no computable" (columna "Global" fuera de la tabla, rama "sin E3" de T01).

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
- Reportes: `evaluation/report_sensibilidad_ajustes.md` (98 lineas, regenerado offline; dos corridas dan archivo identico
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
recompilar. La decision sobre la FORCE-ESCALATE quedo confirmada por el autor el 2026-10-26 (se acepta) y es reversible sin tocar los valores
canonicos: si se rechazara, E3 y E4 pasan a "no computable" y la tabla pierde su cuarta columna.

**Estado**: grupo aplicado.

## Dictamen v1.1.0 - A3 (c-132) - Balance neto entre el ahorro de registro y las derivaciones erroneas

**Origen**: change `c-132-balance-neto-derivaciones-erroneas` (dictamen CONEAU 2026-10-22: VEREDICTO punto 3, seccion 7 (c)
y RECOMENDACION A3). Aplicado el **2026-10-25** en la rama `change/c-132-balance-neto-derivaciones-erroneas`, cortada de
`ramagonzalo` en `31c143a` (merge de c-142). Posicion 5 del orden de la familia (G0.6). Solo documento (gobernanza LOW):
cero llamadas a Gemini, sin codigo, sin tags. Sin commit (lo crea el orquestador).

**A3 - Balance neto de derivaciones erroneas - APLICADO por c-132 (2026-10-25).**

### Open Questions del design - CONFIRMADAS el 2026-10-26 (registradas como PROVISIONAL el 2026-10-25)

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

## Dictamen v1.1.0 - B4, B5 y B6 (c-133) - Hipotesis, objetivos y metrica primaria

**Origen**: change `c-133-hipotesis-objetivos-metrica-primaria` (dictamen CONEAU 2026-10-22: VEREDICTO dimensiones 2 y 3,
RECOMENDACIONES B4, B5 y B6). Aplicado el **2026-10-25** en la rama `change/c-133-hipotesis-objetivos-metrica-primaria`, cortada
de `ramagonzalo` en `d241c0b` (merge de c-132). Posicion 6 del orden de la familia (G0.6). Solo documento (gobernanza LOW): cero
llamadas a Gemini (ningun `--confirm-paid` ni `run_evaluation.py --force`), sin codigo, sin tags. Sin commit (lo crea el orquestador).

### Open Questions del design (tarea 1.1) - CONFIRMADAS el 2026-10-26 (registradas como PROVISIONAL el 2026-10-25)

El usuario pidio aplicar la familia sin detenerse y no respondio de forma explicita a las Open Questions 1 a 3. Cada decision es el
default del design, **PROVISIONAL (pendiente de confirmacion del autor)**, registrada ANTES de editar ningun `.tex`:

| Open Question | Decision PROVISIONAL | Efecto en el apply |
|---|---|---|
| OQ1 - segunda sub-hipotesis | **Opcion A**: cota `0,15 = 1 - 0,85`, estado "no contrastada por ausencia de registro primario" | T1 en la variante principal; la cota entra al memo (3.12) como "explicitada por c-133; no es un resultado" |
| OQ2 - subsidiaria de eficiencia | **"Contrastada de forma acotada"** con las salvedades de D3 y, ademas, con el resultado E4 de c-142 y el McNemar no significativo de c-131 como salvedades adicionales. **La regla de decision de D3 prevalece (ver abajo): con E4 el rotulo efectivo es "no contrastada".** | T10, T3, T11 y T14 en la variante de fallback |
| OQ3 - objetivo 3 tras c-131 | **Sin aceptacion del autor** de la condicion (iii) (la "complejidad operativa percibida" no se da por satisfecha por construccion): la fila queda "Alcanzado parcialmente" aunque c-131 aporte la calidad por canal | T12 variante "calidad por canal publicada"; el componente faltante pasa a ser la complejidad percibida |

### Precondiciones y relevamiento (tarea 1.2)

Los cuatro prerequisitos estan aplicados (37/37, 81/81, 91/91 y 29/29 tareas) y siguen en `openspec/changes/` (el archivo es de c-141).
Rama cortada de `ramagonzalo` `d241c0b`. Relevado:

- **c-130**: terminologia "etapa determinista"/"etapa semantica" en el design; el manuscrito usa "etapa deterministica" (`07:129`, `08:10`,
  `08:16`) y "etapa semantica" (`02`, `10`, `11`). T14 se escribe con "filtro deterministico" y "etapa deterministica". El gate se evalua solo sobre la
  salida de Gemini; la etapa determinista cortocircuita con puntaje de correctitud `>= 0,5166`; 124 de 200 casos con confianza `< 0,70` no escalaron
  (todos de la etapa determinista). T14 retira la formulacion "con confianza suficiente" (la etapa determinista no se evalua por su confianza).
- **c-131**: calidad por canal publicada (`tab:exactitud-etapa-canal` en `07-resultados.tex`; memo 3.9): estricta por canal `53/81 = 0,6543`
  (telefono), `51/66 = 0,7727` (correo), `43/53 = 0,8113` (formulario); por etapa `97/131 = 0,7405` y `50/69 = 0,7246` (IC de Wilson); laxa
  `179/200 = 0,8950`. McNemar entre etapas sobre `S` en el memo 3.9: `|S| = 131`, `130` pares, `b = 16`, `c = 8`, p exacto `0,1516`,
  **no significativo**. `cache_meta` de la FORCE-ESCALATE: `hybrid-v2` (corpus_hash distinto del vigente); por eso la comparacion `97/131` frente a
  `88/130` queda como estimacion dentro de la muestra y solo historica en cuanto a la cache (salvedad 4 de D3).
- **c-142**: `subsec:sensibilidad-ajustes` existe en `07-resultados.tex` (entre `subsec:calibracion` y `subsec:analisis-errores`). **E4** (memo 3.10):
  con el vocabulario previo (`V0`) la etapa de reglas acierta `38/73 = 0,5205` frente a Gemini `48/73 = 0,6575` (`b = 3`, `c = 13`, p exacto
  `0,0213`): las reglas **no superan** a Gemini. Prompt: nivel a (R002, R038, R015 entre los 69 escalados; Gemini `50/69` con ellos y `48/66`
  sin ellos); la FORCE-ESCALATE es **posterior** a las reglas de frontera (nivel b). Limitacion nueva: item "Septimo"; `subsec:limitaciones-estudio` dice "siete".
- **c-132**: `subsec:balance-neto` (`08-discusion.tex`) y `tab:balance-neto` (Tabla 17; `tab:cumplimiento-objetivos` pasa a ser la 18). Clausulas a conservar literales
  (copia previa a editar):
  - `09:6`: "...resulto tecnicamente viable, eficiente en el registro y economicamente accesible para organizaciones medianas, con viabilidad operativa condicionada al balance neto (\autoref{subsec:balance-neto})".
  - `09:41`: "el sistema libera tiempo bruto de registro, cuyo saldo neto esta indeterminado (\autoref{subsec:balance-neto})".
  - `00-resumen.tex` (parrafo final ES/EN): "Los hallazgos confirman la viabilidad tecnica y economica; la operativa es condicional, porque el balance neto frente a las derivaciones erroneas resulta indeterminado." / "The findings confirm technical and economic feasibility; operational feasibility is conditional, since the net balance against misrouted incidents remains undetermined."
  - Umbral del 85 % = paridad con el 15 % manual; `a*` = 77,7 a 80,1 %; la laxa 89,5 % supera los `a*` pero es la cota favorable (`subsec:balance-neto`).

### Linea base (tarea 1.3)

- Paginas de partida: **105** (`abspage@last{105}` de `main.aux`; cuerpo 97, anexos 8; `Anexos` en p. 98 de `main.toc`). Secuencia: 102 tras c-144, 103
  c-130, 103 c-131, 104 c-142, 105 c-132. Inicio de capitulos: 1:11, 2:18, 3:26, 4:31, 5:40, 6:51, 7:61, 8:67, 9:75, 10:84, 11:87, Referencias:92, Anexos:98.
- Palabras de prosa del resumen y del abstract (regla de c-106 con el math en linea como una palabra; script de la sesion que reproduce el conteo de
  c-132): **ES 264, EN 252** (exceso preexistente de +14 / +2 sobre 250).

### Memo (bloque 2, Gate 0)

Seccion **3.12** de `numeros-canonicos.md` ("Hipotesis, objetivos y metrica primaria (c-133)"; 3.7 c-130, 3.8 c-134, 3.9 c-131, 3.10 c-142, 3.11 c-132; las remisiones
del design a la "Seccion 3.7" se leen como 3.12). Cambios, todos solo agregados o anotaciones: Seccion 3.2 (`0,6508` pasa de `condicional` a `vigente`, "Primaria de umbral (c-133 D1)";
`0,5207` con la nota "Informativa; toda cita lleva su aclaracion"), Seccion 3.3 (filas `65,5 %` y `34,5 %`, procedencia `report.md:11-12` actual), Seccion 3.12 (cota `0,15`
"explicitada por c-133; no es un resultado", `97/131`, `88/130`, McNemar `b = 16`, `c = 8`, p exacto `0,1516`, E4, `65,5 %`/`34,5 %`, exactitud por canal), item 5 de la Seccion 5
("superado por c-133 D1"), punto 4 de la Seccion 7 ("decision ratificada por c-133 D1") y linea "Upsert c-133" en la cabecera. `grep -c "c-133"` del memo = 16.
Las cifras `0,7405` y `0,6769` ya estaban en la 3.7 (c-130); c-133 no duplica sus valores, los remite. **Estado de la prueba pareada (tarea 2.5)**: c-131 la registro en la 3.9
(`b = 16`, `c = 8`, p exacto `0,1516`, no significativo); `cache_meta` de la FORCE-ESCALATE es `hybrid-v2` (otro `corpus_hash` que el vigente), de modo que la comparacion `97/131` frente a
`88/130` es historica en cuanto a la cache. Sin llamadas pagas: ningun `--confirm-paid` ni `run_evaluation.py --force`.

### Aplicacion de la regla de decision de E4 (D3) y decision del objetivo 6

- **Hipotesis subsidiaria de eficiencia: "no contrastada" (fallback de T3, T10, T11 y T14).** Con la variante E4 de c-142 la etapa de reglas (`V0`) acierta `38/73 = 0,5205` frente a
  Gemini `48/73 = 0,6575` (p exacto `0,0213`): no supera a Gemini. La ventaja en `S` (`97/131` frente a `88/130`) depende, por lo tanto, del vocabulario ajustado con el corpus. Ademas,
  el McNemar de c-131 en `S` no es significativo (p exacto `0,1516`). La OQ2 PROVISIONAL ("contrastada de forma acotada") queda **sobrepasada por la regla de decision del design**, que es
  anterior y especifica; no es una decision de fondo del autor. `08-discusion.tex` conserva las cifras como descripcion (estimaciones dentro de la muestra, sin diferencia significativa, y
  con la remision a `subsec:sensibilidad-ajustes`) y NO las presenta como evidencia favorable. **Reversible** a "contrastada de forma acotada" si el autor lo decide: variante principal de T10,
  T3, T11 y T14 (texto en el `design.md` de c-133, D9) y upsert de la 3.12. Los cuatro rotulos de la subsidiaria de eficiencia (introduccion, discusion, conclusiones, resumen no la cita) coinciden.
- **Hipotesis subsidiaria de integracion multicanal: "no contrastada"** en introduccion (T3), discusion (frase agregada a `08:10`) y conclusiones (T15). La exactitud por canal de c-131 se
  cita como descriptiva.
- **Objetivo 3 (OQ3)**: "Alcanzado parcialmente" con la calidad por canal publicada: la celda cita `subsec:capa-canales`, "latencia y exactitud por canal (Tabla 12)" y nombra el
  componente faltante, la complejidad operativa percibida no medida (condicion iii de D4 no aceptada por el autor; condiciones i y ii cumplibles con los datos de c-131).
- **Objetivo 2**: "No alcanzado" con macro-F1 de umbral `0,6508`. La exactitud laxa (`89,5 %`) se lee como secundaria y no cambia el estado del objetivo: el criterio del 85 % es la exactitud estricta
  (c-131 y `subsec:balance-neto`: el umbral equivale a la paridad con el 15 % manual y la laxa es la cota favorable).
- **Objetivo 6**: se conserva "Alcanzado" (OQ3 provisional de c-142). Tarea 5.8: la celda ya cita `subsec:analisis-errores`, `subsec:calibracion` (calibracion por etapa de c-131) y
  `subsec:sensibilidad-ajustes` (c-142); las tres piezas existen, ninguna contradice la caracterizacion de la confianza. Sin edicion.
- **Objetivos 1 y 4**: "Alcanzado parcialmente" (sincronica y TLS no verificado; exactitud solo del flujo automatizado e intervencion humana no medida). Objetivo general: "Alcanzado
  parcialmente" con el desglose dentro de la celda (tiempo alcanzado; clasificacion por debajo del umbral; intervencion humana no medida; viabilidad operativa condicionada, `subsec:balance-neto`).

### Mapeo B4 / B5 / B6 -> T1-T18 (bloques 3 a 5)

| Item | Archivo | Estado |
|---|---|---|
| T1 (H2) | `01-introduccion.tex` | aplicado, opcion A: cota `0,15`, contraste con IC de Wilson, "no era contrastable", "no contrastada por ausencia de registro primario"; el `0 de 200` del gate NO se presenta como contraste; remite a `subsec:limitaciones-estudio` ("se falsea" en lugar de "se falsa") |
| T2 (H3) | `01-introduccion.tex` | aplicado ("F1 macro de umbral"; "macro-F1 de umbral de 0,6508 sobre las cuatro clases estimables"); `0,5207` ya no figura en la introduccion |
| T3 | `01-introduccion.tex` | **variante de fallback**: "Ninguna tiene contraste formal y ambas se declaran no contrastadas" |
| T4 | `01-introduccion.tex` | aplicado: se elimina la ultima oracion del objetivo 2 (tres criterios y fuentes intactos); enunciados de los objetivos sin cambios |
| T5, T7 | `04-marco-metodologico.tex` | aplicados (variantes cortas: "Promedio aritmetico del F1 de cada sector; el de umbral excluye los de soporte unitario"; "contra el cual se evalua el criterio de 0,85") |
| T6 | `04-marco-metodologico.tex` | aplicado: "estimable" en la tercera, cuarta "prevista en dos dimensiones rotuladas ... en la version evaluada no se midio, por ausencia de registro primario" |
| T8 | `07-resultados.tex` | aplicado solo en la oracion del macro-F1 (el resto del parrafo es de c-131/c-142 y queda literal) |
| T9 | `07-resultados.tex` | aplicado en el parrafo de estado de `subsec:reduccion-intervencion` (el parrafo del gate, de c-130, intacto) |
| T10 | `08-discusion.tex` | **variante de fallback** (regla de decision de E4), con las cifras como descripcion calificada y la remision a `subsec:sensibilidad-ajustes`; mas una frase sobre la subsidiaria multicanal |
| T11 | `09-conclusiones.tex` | aplicado: "cumplido parcialmente el objetivo general"; clausula de viabilidad de c-132 **literal**; macro-F1 de umbral `0,6508`; estado por sub-hipotesis y de las subsidiarias (no contrastadas); "ha cumplido con el objetivo general" = 0 |
| T12 | `09-conclusiones.tex` | aplicado: filas general, 1, 3 y 4 "Alcanzado parcialmente" con el componente faltante; objetivo 2 con `0,6508 (0,5207 con cinco clases, una no estimable)`; objetivo 3 en la variante "calidad por canal publicada"; columnas ensanchadas (3,6 / 2,2 / 8,4 cm) para que "Alcanzado parcialmente" no se corte (corrige tambien el overfull de la cabecera "Cumplimiento") |
| T13 | `09-conclusiones.tex` | aplicado en variante corta (sin la enumeracion de las cinco capas) |
| T14 | `09-conclusiones.tex` | **variante de fallback**: "el filtro no resuelve" (se retira "con confianza suficiente"); 65,5 %; eficiencia "no se contrasto"; las oraciones de c-131/c-142 (0,7405, 0,7246, laxa, por canal) literales |
| T15 | `09-conclusiones.tex` | aplicado, **variante con calidad por canal**; la oracion del canal telefonico ("El canal telefonico ... demostracion de laboratorio") queda **literal** para c-135 (B13) |
| T16 | `09-conclusiones.tex` | aplicado; clausula de c-132 literal ("el sistema libera tiempo bruto de registro, cuyo saldo neto esta indeterminado (`subsec:balance-neto`)") |
| T17 | `00-resumen.tex` | aplicado en ES y EN (macro-F1 de umbral 0,6508 / 0.6508; estado por sub-hipotesis); parrafo final de c-132 literal |
| T18 | `08-discusion.tex` | aplicado, opcion principal: cardinal "siete" -> "ocho" y limitacion "Octavo" sobre la ausencia de registro primario; lista de 8 ordinales (Primero a Octavo) |
| Tarea 4.8 | `08-discusion.tex` | aplicada como compensacion: se elimina "Tres aspectos de los resultados merecen una interpretacion detallada." |

### Verificaciones (grupos 3 a 7)

`0,5207`/`0,6508` rotulados en todas las fuentes (control global de 3.6 vacio); `cinco sectores objetivo` = 0; `consistente con la hip` = 0; `ha cumplido con el objetivo general` = 0; "Alcanzado parcialmente" = 4 filas;
rotulo "no contrastada por ausencia de registro primario" en resumen, introduccion, resultados y conclusiones (1 en cada archivo; el abstract en ingles lo dice como "not tested ... absence of a primary record");
sin `9,5` como proporcion de intervencion humana (solo `89,5`); sin tildes omitidas en el texto nuevo; `verify_citations.py` PASS (0 huerfanas); `openspec validate c-133-hipotesis-objetivos-metrica-primaria --strict` valido.

### Compilacion, paginas y palabras (bloque 6)

- Docker `texlive-thesis` (`latexmk main.tex`, en el arbol): `grep -c "^!" main.log` = 0, `undefined` = 0, `multiply defined` = 0, `main.blg` sin WARN/ERROR, sin `??` en el texto del PDF.
- **Paginas: antes `abspage@last{105}` (cuerpo 97, anexos 8); despues `abspage@last{105}`; `Anexos` en p. 98: cuerpo 97, anexos 8; delta 0 / 0** (prevision 0). Inicio de capitulos
  identico a la linea base: 1:11, 2:18, 3:26, 4:31, 5:40, 6:51, 7:61, 8:67, 9:75, 10:84, 11:87. Sin compensar habria sido **107** (+2): la primera compilacion desbordaba el marco metodologico
  (2 lineas) y las conclusiones (8 lineas, por la tabla de cumplimiento con "Alcanzado parcialmente" en una columna de 1,7 cm que partia la palabra en tres lineas). Compensaciones: columnas de la
  tabla ensanchadas y celdas de evidencia acortadas; variantes cortas de T5, T6, T7, T11, T13, T14, T15 y T16 (sin cambiar cifras, rotulos ni estados); T4 (ultima oracion del objetivo 2);
  tarea 4.8 ("Tres aspectos ..."); compresion del parrafo de descripcion del sistema del resumen. No se recorto ningun parrafo de otro change.
  Brecha frente al tope vigente de 101 (regla (a) provisional): **+4**, sin cambio respecto de c-132; regla (b) (cuerpo <= 100): cuerpo 97, margen 3. Si c-141 necesita paginas, las palancas
  residuales de c-133 son la nota de la tabla de cumplimiento y las celdas de evidencia de la tabla.
- **Resumen** (regla de c-106, math en linea como una palabra): **ES 264 -> 250, EN 252 -> 243**. El exceso preexistente (+14 / +2) queda corregido: el espanol llega a 250 (maximo permitido) tras las
  ediciones de T17 (-7 palabras en ES y -2 en EN) y la compresion del parrafo de descripcion del sistema (-7 en ES y -7 en EN: se quitan "orquestacion con", "inferencia con", "persistencia" y "determinist." de reglas, y "cada incidente" pasa a "las", en ES; "workflow orchestration", "inference through", "persistence" y "a telephony channel managed by Twilio" -> "a Twilio telephony channel" en EN). **c-132 y c-141 deben conservar ese tope**
  (el espanol no tiene margen: cualquier agregado exige otra compresion). El conteo "plano" (sin colapsar el math) da 252 / 245.

### Libro mayor de paginas

| Change | Commit | Total | Cuerpo sin anexos | Anexos | Delta total | Delta cuerpo | Regla vigente | Estado |
|---|---|---|---|---|---|---|---|---|
| `+c-133` (`change/c-133-hipotesis-objetivos-metrica-primaria`) | sin commit (lo crea el orquestador) | 105 | 97 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{105}`; `Anexos` en p. 98; brecha frente a 101: +4 (sin compensar habria sido 107); rama (b): cuerpo 97, margen 3 |

(La fila queda registrada aqui y, en la tabla de la seccion G0, como `+c-133`; el orquestador la consolida.)

### Mapeo del dictamen

VEREDICTO dimensiones 2 y 3, RECOMENDACIONES B4 (tabla de cumplimiento y prosa), B5 (segunda sub-hipotesis y subsidiarias) y B6 (metrica primaria) -> D1-D9 (con el desvio de T3/T10/T11/T14 por la regla de E4), T1-T18 y memo 3.12.

### Consignas para otros changes

- **c-134 (bloque de tesis)**: la 3.8 del memo es suya; las remisiones del resumen/abstract a la convencion de `p` no cambian. El resumen ES queda en exactamente 250 palabras: si agrega texto debe comprimir otro. `08-discusion.tex:10` cita `\(p = 0{,}1516\)` (McNemar exacta, bilateral); aplicar la convencion de `p` de c-134 si corresponde.
- **c-138 / c-136**: `10-recomendaciones.tex` afirma que la medicion de intervencion humana ataca un defecto "reconocido entre las limitaciones": ahora es cierto (limitacion "Octavo" de `subsec:limitaciones-estudio`, ocho limitaciones). c-136 debe proponer como linea futura el registro primario por caso de la accion manual que
  permitiria contrastar la segunda sub-hipotesis contra `0,15`, la validacion en un corpus independiente y el dato de que la ventaja de las reglas depende del vocabulario (E4); no duplicar `subsec:estudios-replicacion` (T14 de c-132).
- **c-135 (B13)**: la oracion del canal telefonico de `09-conclusiones.tex` esta literal; agregar ahi la salvedad de cota inferior. `07:6` debe seguir enumerando `subsec:sensibilidad-ajustes`. La nueva frase de `08:10` sobre la subsidiaria multicanal remite a "capacidad bajo carga concurrente" (no medida).
- **c-139**: sin cambios en `01:66`. Las atribuciones del objetivo 2 (Paramesh2019) y sus tres criterios quedan intactos.
- **c-140**: autorizado a actualizar solo la fila del objetivo 1 de `tab:cumplimiento-objetivos` (hoy "Alcanzado parcialmente": invocacion sincronica y TLS no verificado) y la oracion del objetivo 1 de `09:35` segun la regla de D4 (volver a "Alcanzado" solo con TLS verificado y comunicacion asincronica; celda con "incorporado despues de la validacion experimental"). Si solo resuelve el TLS la fila conserva solo la invocacion sincronica.
- **c-141**: (1) libro mayor: fila `+c-133` = 105 / 97 / 8, delta 0 / 0; (2) revision del autor pendiente: OQ1 a OQ3, el rotulo "no contrastada" de la subsidiaria de eficiencia (regla de E4) y la redaccion de la tabla de objetivos; (3) `Tabla 18` es la de cumplimiento (la 17 es `tab:balance-neto`); (4) el resumen ES esta en 250 palabras (topado); (5) la regeneracion final del render y `main.bbl`
  son suyas; (6) si el McNemar o E4 se actualizan, `08:10` es el unico sitio de la subsidiaria de eficiencia en la discusion; (7) `numeros-canonicos.md`: la seccion siguiente libre es la 3.13.
- **c-137** (ortotipografia): el texto nuevo lleva tildes; "falsea" reemplaza a "falsa" solo en la segunda sub-hipotesis (el resto del documento conserva "falsacion").

### Reversibilidad

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex" "docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex"
"docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex" "docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex" "docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex" docs/Tesis/Correcciones/numeros-canonicos.md
docs/Tesis/Correcciones/dictamen-correcciones.md`, regenerar el render y recompilar. Las decisiones PROVISIONALES (OQ1 a OQ3) y el rotulo de la subsidiaria de eficiencia se pueden invertir sin tocar los valores canonicos
(ver D1 a D4 del design y la 3.12).

**Estado**: grupo aplicado.

## Dictamen v1.1.0 - B7a, B12 y B13b (c-134, bloque de tesis) - Contrastes de tiempos, muestreo y cronometraje

**Origen**: change `c-134-contrastes-estadisticos-y-desagregado-canal`, bloque de tesis (grupos 6, 7 y 8 de `tasks.md`; 20 tareas, 6.1 a 8.7)
(dictamen CONEAU 2026-10-22: seccion 6, observaciones primera, segunda, tercera y quinta; seccion 7, desagregado por canal; recomendaciones B7a,
B12 y B13b). Aplicado el **2026-10-25** en la rama `change/c-134-contrastes-estadisticos-y-desagregado-canal`, ya actualizada con `ramagonzalo`
(`0ac3160`, merge de c-133); el bloque de codigo (grupos 1 a 5) estaba commiteado en `78957f7`. Posicion 7 del orden de la familia (G0.6). Cero
llamadas a Gemini; `evaluation/`, `data/`, `App/`, `n8n/` y `CHANGES.md` sin cambios en este tramo (`git diff --quiet` verificado). Sin commit
(lo crea el orquestador). Gobernanza MEDIUM: solo documento.

### Open Questions del design (tareas 7.1 y 7.3) - CONFIRMADAS el 2026-10-26 (OQ1, OQ2 y OQ3)

El usuario pidio aplicar la familia sin detenerse y nadie respondio a OQ1 ni a OQ2 (hechos del estudio que solo conocen los autores). Cada
decision es el **texto por defecto del design, PROVISIONAL**, registrada tambien en `design.md` (seccion Open Questions) ANTES de cerrar el grupo:

| Open Question | Decision PROVISIONAL (2026-10-25) | Pasajes afectados | Reversible si |
|---|---|---|---|
| OQ1 - procedimiento del cronometraje | **CONFIRMADA por el autor (2026-10-26). Opcion (a)**: los dos operadores trabajaron en pares y se cronometraron mutuamente, sabian que la campana registraba tiempos; no se anunciaron el inicio de cada medicion ni el proposito comparativo; el debriefing informo el proposito; Hawthorne atenuado, no eliminado, amenaza residual. Granularidad 199/200 (5 s) y 180/200 (10 s) declarada como hecho verificable de la planilla, sin afirmar si es por diseno o por redondeo a ojo | `04` (`:16`), `08` (explicacion rival "Tercero"), `11` (`:32`, con `\parencite{APA2017}` intacto); `04:67` sin cambios | confirmado (2026-10-26) |
| OQ2 - universo y seleccion de los 200 casos | **CONFIRMADA por el autor (2026-10-26): A y B, en ese orden.** El tamano total se fijo por disponibilidad operativa (N = 200: los incidentes efectivamente cronometrados en la campana manual) y, dentro de ese marco, la seleccion se estratifico con asignacion proporcional a la distribucion por sector observada en el periodo relevado. La distribucion del universo por sector no esta disponible, por lo que la proporcionalidad frente al universo no es verificable; Bases de Datos `n = 1` no es estimable y en replicaciones conviene sobremuestrear las clases minoritarias. El texto de `04:45` ya expresa las dos cosas y el abstract conserva "drawn by stratified sampling" | `04` (`:45`), `00-resumen.tex` (`:27`) | sin cambio de texto; si el autor aporta el universo por sector se agrega una frase y una fila al memo |
| OQ3 - IC del tiempo medio | **Default**: se retira la promesa del intervalo de confianza (`04:65`) y la lista declarada queda alineada con lo reportado | `04` (`:65`) | el autor prefiere reportar el IC: se agrega al runner y una fila a `tab:tiempos` |

### Mapeo de tareas 6.1 a 8.7 -> pasajes (anclas P1-P18 re-ubicadas por texto; las lineas son las vigentes tras la edicion)

| Tarea | Ancla | Resultado |
|---|---|---|
| 6.1 | P1-P3 | `13,48` -> `13,52` en `07:10`, `07:23` y `08:12` (`grep -rn "13,48" sections/` = 0; `13,52`: 2 en 07 y 1 en 08); `08:12` ademas compactada ("consecuencia de la automatizacion y no un objetivo del diseno") para la compensacion de paginas |
| 6.2 | P4 | `04:65`: la metrica de tiempo declara media, mediana, desvio estandar muestral, minimo, maximo y reduccion relativa de la media; sin "intervalo de confianza al 95" en el parrafo de la metrica de tiempo (`grep -c "intervalo de confianza al 95" 04` = 0); el resto del parrafo (exactitud, F1 macro, intervencion humana) intacto |
| 6.3 | P5-P7 | `04:71`: "Los p de tiempos son bilaterales, conservadores frente a la H1 direccional; el unilateral global (`alternative=greater`) es 1,54 x 10^-32"; `01:32`: `p = 3,08e-32` rotulado bilateral con `1,54e-32` unilateral; `07:57`: el mismo p rotulado bilateral con remision a `subsec:analisis-estadistico`; sensibilidad (`07:61`): `p = 1,8 x 10^-26` rotulado bilateral. `08:10`: la cita del McNemar `p = 0,1516` pasa a "McNemar exacta bilateral" (convencion coherente, sin cambiar el valor). `1{,}54` en 01 y 04 = 1 y 1; `3{,}08` en 01 y 07 = 1 y 1 |
| 6.4 | P8 | `04:87`: MDE en escala `d_z` (0,20; 0,21 con ARE 0,864), `d_z` observado 1,00 ("mas de cuatro veces"), por canal 1,37 / 0,73 / 1,61 frente a 0,31 / 0,34 / 0,38 (0,33 / 0,37 / 0,41 con el ajuste); `grep -c "supera holgadamente ese m" 04` = 0, `0{,}864` = 1 |
| 6.5 | P9 | `07:59`: la ecuacion desplegada de `r` pasa a expresion en linea (`r = 19.374/20.100 = 0,9639`) mas `d_z = 1,00` rotulado y distinguido del `r`; sin `\[` en la subseccion; sin rank-biserial `1,00`. Compensacion no prevista por D10: la formula de `r` de `04:73` tambien pasa de display a en linea (misma formula, mismo contenido) |
| 6.6 | P16 | `07:32` reescrita y `tab:tiempos-canal` (Tabla 10) reemplazada por la tabla de D7: Canal, Casos, manual media / mediana, automatizado media / mediana, reduccion de la media, pares no mas rapidos, p bilateral, `d_z`; 3 canales y Global; `\footnotesize`, `\tabcolsep` 2,5 pt, cabecera de dos niveles, "(cota inferior)" en la fila telefonica, nota de convencion de p y de `d_z` y remision a `evaluation/report.md` para `W`, `T+`, `T-` y `r`; linea de fuente conservada (`grep -c Fuente 07` = 8, como antes); sin `W = 0` en ninguna fuente; la celda del p global se escribe en texto (`3,08e-32`) para que `3{,}08` figure una sola vez en 07 |
| 6.7 | P13 | `08:22` ("Segundo"): remite a `tab:tiempos-canal` (reducciones del 51,1 al 93,4 % y contraste intra-canal significativo), conserva "lo debilita" y la dependencia de la magnitud global respecto de la composicion; sin "se descartaria con un contraste intra-canal" (= 0); `tab:tiempos-canal` en 08 = 1 |
| 6.8 | P17-P18 | retiradas las notas historicas de `04:51` ("Ese margen sustituye al 6,5 %...") y de `04:77` ("La definicion anterior... queda reemplazada..."); `6,5~` = 0, `queda reemplazada por esta` = 0; el parrafo conserva formula, `N`, `z`, `p`, `e = 6,66 %` y la declaracion de tamano fijado por disponibilidad |
| 7.1 | OQ2 | registrada (tabla de arriba y `design.md`) |
| 7.2 | P10-P11 | `04:45` (default de D8) y abstract `00-resumen.tex:27`; `grep -c "estratificado proporcional un corpus" 04` = 0, `proportional stratified sampling` = 0; no se aporta cifra de universo (no hay valores nuevos para el memo por esta via) |
| 7.3 | OQ1 | registrada (tabla de arriba y `design.md`) |
| 7.4 | P12 | `04:16` (default de D9, opcion a): relato del cronometraje mutuo, no anunciado el inicio ni el proposito, debriefing, Hawthorne atenuado y residual, y granularidad 199/200 y 180/200 vinculada a los descuentos de 5 s y 10 s; `no fue anunciado en tiempo real al operador` = 0; `199` y `180` figuran en el texto y en el memo 3.8. Se quito de `04:16` la descripcion del registro automatico (duplicada en `04:67`, inciso (a)) como compensacion |
| 7.5 | P14-P15 | `08:22` ("Tercero"): los operadores sabian que se cronometraba y el procedimiento atenua el efecto sin eliminarlo, con remision a `subsec:diseno-experimental`; `11:32`: mismo relato, "conocimiento diferido" -> "informacion diferida sobre el proposito del estudio", `\parencite{APA2017}` = 1 (sin cambio); ningun capitulo afirma que el operador ignoraba el cronometraje durante toda la campana ni describe la planilla como "estimados" o "con exactitud al segundo" |
| 8.1 | trazabilidad | cada cifra nueva o modificada figura en la Seccion 3.8 del memo con estado `vigente` (tabla nueva "Cifras con redondeo de tesis"): `13,52`, `1,54e-32`, `d_z` 1,00 / 1,37 / 0,73 / 1,61, MDE, medias y medianas por canal, reducciones 77,0 / 51,1 / 93,4, pares no mas rapidos 0 / 12 / 0, `199` y `180`, media y desvio de las diferencias; sin universo (OQ2 sin aporte); dos redondeos explicados (`27,65` de `27,6546`; `1,26` de `1,2650`) |
| 8.2 | compilacion | ver "Compilacion" |
| 8.3 | paginas | ver "Compilacion" y libro mayor |
| 8.4 | `verify_citations.py` | PASS: 59 entradas, 59 claves citadas, 100 comandos de cita, 0 huerfanas, 0 sin usar (no se agregan citas ni entradas `.bib`) |
| 8.5 | render | `tesis_para_agente.md` regenerado (`build_tesis_para_agente.py`): `13,48` = 0, `13,52` = 3, contiene la tabla por canal nueva |
| 8.6 | alcance | `git diff --quiet -- data/ evaluation/ App/ n8n/ CHANGES.md` sin diferencias; `git status` de este tramo: las seis secciones `.tex` editadas (`00`, `01`, `04`, `07`, `08`, `11`), `numeros-canonicos.md`, `dictamen-correcciones.md`, `design.md` y `tasks.md` del change, el render y los artefactos de compilacion versionados (`main.aux`, `main.toc`, `main.lof`, `main.lot`, `main.out`, `main.fdb_latexmk`, `main.xdv`, `main.pdf`) |
| 8.7 | cierre | tabla TDD de los grupos 2-4 ya entregada en el apply del codigo (153 -> 216 tests): se referencia, no se rehace; handoffs en "Consignas" |

### Compilacion, paginas y palabras (tareas 8.2 y 8.3)

- Docker `texlive-thesis` (`latexmk main.tex`, en el arbol): `grep -c "^!" main.log` = 0, `undefined` = 0, `multiply defined` = 0, `main.blg` sin WARN/ERROR, 29 `Overfull \hbox` (los mismos 29 de la linea base; ninguno en `tab:tiempos-canal`, que no genera `Overfull`).
- **Paginas: antes `abspage@last{105}` (cuerpo 97, anexos 8); despues `abspage@last{105}`; `Anexos` en p. 98: cuerpo 97, anexos 8; delta 0 / 0** (prevision 0 a +0,4). Inicio de capitulos identico a la linea base: 1:11, 2:18, 3:26, 4:31, 5:40, 6:51, 7:61, 8:67, 9:75, 10:84, 11:87, Referencias:92, Anexos:98.
- **Sin compensar habria sido 108 (+3)**: la primera compilacion con los textos completos de D8 y D9 y la tabla ancha dio `abspage@last{108}` (cuerpo 100). La causa es que tres paginas finales de capitulo estaban casi llenas en la linea base (medido con `\the\pagetotal` al cierre de cada capitulo en una copia instrumentada, sin tocar el arbol): el marco metodologico terminaba en la p. 39 con 684 de 700 pt (una linea de margen), la discusion en la p. 83 con 684 de 700 pt, y los resultados en la p. 74 con 473 de 552 pt (con un flotante); el texto nuevo desborda cada una (+1, +1 y +1 pagina).
- **Reservas de D10 y compensaciones aplicadas** (dentro de los pasajes que posee c-134): (1) `07:32` reducida a un parrafo corto que remite a la tabla; tabla en `\footnotesize`, `\tabcolsep` 2,5 pt, rotulo de cota inferior en la fila y nota y fuente en un solo parrafo; (2) textos por defecto de D8 y D9 acortados (`04:45`, `04:16`; en `04:16` se quita la descripcion del registro automatico, duplicada en `04:67`); (3) notas historicas de `04:51` y `04:77` retiradas (P17-P18, previstas); (4) ecuacion de `r` compactada en `07` (P9, prevista) y, ademas, formula de `r` en linea en `04:73`; (5) `08:12` y la explicacion rival "Segundo" de `08:22` acortadas (se quita la enumeracion de los canales, ya en la tabla). No se recorto ningun parrafo de otro change. La compensacion de `08` y de `04` dejo cada capitulo en el mismo punto de corte que la linea base (684 de 700 pt en `04` y en `08`; `07`: 539 de 552 pt).
- **Margen para los changes siguientes: cero.** Las ultimas paginas del marco metodologico (p. 39) y de la discusion (p. 83) vuelven a estar llenas (una linea de margen) y la de resultados (p. 74) tiene unos 13 pt: cualquier agregado de c-135, c-136, c-138 o c-139 en `04`, `07` u `08` agrega una pagina entera salvo que compense en el mismo pasaje.
- Brecha frente al tope provisional 101 (regla (a) de G0.1): **+4**, sin cambio respecto de c-133; regla (b) (cuerpo <= 100): cuerpo 97, margen 3.
- **Resumen** (regla de c-106, math en linea como una palabra): **ES 250 -> 250** (los parrafos en espanol no se tocan; el cambio de muestreo del resumen solo alcanza al abstract) y **EN 243 -> 242** ("proportional stratified sampling" -> "stratified sampling"; la reproduccion del conteo con un script propio da el mismo delta de -1: 232 -> 231 en esa variante de conteo, cuyo valor absoluto difiere del de c-132 y c-133 porque no se recupero su script). El espanol sigue topado en 250.

### Libro mayor de paginas

| Change | Commit | Total | Cuerpo sin anexos | Anexos | Delta total | Delta cuerpo | Regla vigente | Estado |
|---|---|---|---|---|---|---|---|---|
| `+c-134 tesis` (`change/c-134-contrastes-estadisticos-y-desagregado-canal`) | sin commit (lo crea el orquestador) | 105 | 97 | 8 | 0 | 0 | (a) total <= 101 | Medido: `abspage@last{105}`; `Anexos` en p. 98; brecha frente a 101: +4 (sin compensar habria sido 108, +3); rama (b): cuerpo 97, margen 3 |

(La fila queda registrada aqui y, en la tabla de la seccion G0, como `+c-134 tesis`; el orquestador la consolida.)

### Mapeo del dictamen

VEREDICTO seccion 6 (observaciones primera a tercera y quinta), seccion 7 (desagregado por canal), RECOMENDACIONES B7a (tiempos manuales por canal y Wilcoxon intra-canal), B12 (muestreo y asignacion) y B13b (procedimiento de cronometraje) -> D1, D2, D3, D7, D8, D9, D10 y P1-P18; memo 3.8.

### Consignas para otros changes

- **c-138 / c-136 / c-135 / c-139 (paginas)**: ver "Margen para los changes siguientes: cero" arriba. Los capitulos 4 (p. 39), 8 (p. 74) y 9 (p. 83) estan al limite; todo agregado debe compensar en el mismo pasaje.
- **c-135 (B9, B10a-d, B13a)**: la salvedad de cota inferior del canal telefonico queda en la fila de `tab:tiempos-canal` ("cota inferior") y en el parrafo de `07:32` (no duplicarla ahi); la de `09:39` es suya. Las fechas de la campana siguen en `04:45` (la clausula de muestreo es de c-134; no pisar la oracion de las fechas) y `04:16` ya no contiene fechas. `07:6` (parrafo introductorio) es suyo. La nota de Scrumban de `04` es suya.
- **c-136 (B11)**: `04:45` declara de forma autocontenida la asignacion no proporcional con sobremuestreo de las clases minoritarias para replicaciones; puede recogerla en `subsec:estudios-replicacion` con remision, sin duplicar. El hecho de OQ1/OQ2 es PROVISIONAL: si el autor lo cambia, la recomendacion se ajusta.
- **c-137 (B14, ortotipografia)**: el texto nuevo lleva tildes; los `p` aparecen en tres formas (`3{,}08 \times 10^{-32}` en prosa de `07` y `04`, `3{,}08\text{e-}32` en `01`, `3,08e-32` en texto plano dentro de `tab:tiempos-canal`); decidir si se unifican (la tabla evita el math para que `3{,}08` figure una sola vez en `07`, como pide la tarea 6.3). Decimales con coma; `d_z` siempre en math.
- **Change bibliografico de B15 (c-139)**: este change NO agrega citas ni entradas `.bib`; quedan sin referencia primaria la prueba de Wilcoxon de rangos con signo (`04:71`), el analisis de potencia y la eficiencia relativa asintotica 0,864 de la prueba de rangos frente a la `t` pareada (`04:87`) y la definicion de `d_z`.
- **c-141 (integracion)**: (1) libro mayor: fila `+c-134 tesis` = 105 / 97 / 8, delta 0 / 0 (sin compensar +3); (2) revision del autor pendiente: OQ1 y OQ2 de c-134 (hechos del cronometraje y del muestreo) y OQ3; (3) `CHANGES.md` ("Pendientes planificados", punto 2) sigue diciendo que la seccion de normalidad del reporte es manual: ya no lo es (c-99 la cableo al runner); (4) el requisito vigente "Presupuesto de paginas preservado" de `tesis-document` fija <= 100 mientras la familia opera con <= 101; (5) `tab:tiempos-canal` es la Tabla 10; (6) el resumen ES esta en 250 palabras (topado); (7) la regeneracion final del render y de `main.bbl` es suya (el render se regenero en este tramo); (8) `numeros-canonicos.md`: la 3.8 queda completa (la serie libre sigue en 3.13); (9) opcional: `.gitattributes` para el corpus (seguimiento de D6).

### Reversibilidad

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex" "docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex"
"docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex" "docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex" docs/Tesis/Correcciones/numeros-canonicos.md
docs/Tesis/Correcciones/dictamen-correcciones.md`, regenerar el render y recompilar. Las decisiones PROVISIONALES (OQ1 a OQ3) se pueden invertir sin tocar los valores canonicos
(ver D1 a D9 del design y la 3.8).

**Estado**: grupo aplicado.

## Dictamen v1.1.0 - Seccion 4 y criterio 3 residual (c-138) - Estado del arte sobre calibracion y cascadas

**Origen**: change `c-138-estado-del-arte-calibracion-y-cascadas` (dictamen CONEAU 2026-10-22: seccion 4, seccion 5 y recomendacion A4 en su parte de fuentes de calibracion). Aplicado el **2026-10-25** en la rama `change/c-138-estado-del-arte-calibracion-y-cascadas`, cortada de `ramagonzalo` en `738a3d4` (merge del bloque de tesis de c-134). Posicion 8 del orden de la familia (G0.6). Solo documento (gobernanza LOW): cero llamadas a Gemini, sin codigo, sin tags, sin commit (lo crea el orquestador). Archivos editados: `02-marco-teorico.tex`, `03-estado-del-arte.tex`, `08-discusion.tex`, `Bibliography_base.bib`, `bitacora-busqueda-c-110.md` (mas `tasks.md` y `design.md` del change y los artefactos de compilacion).

### Open Questions del design - CONFIRMADAS el 2026-10-26 (registradas como PROVISIONAL el 2026-10-25)

| Open Question | Decision PROVISIONAL | Efecto |
|---|---|---|
| OQ1 - tope de paginas | Lo decide c-141 (hoy regla (a) total <= 101, ya superada; linea base 105). Este change declara +2 esperadas (+3 peor caso) y registra el impacto medido; compensa dentro de su texto si supera +2 | Impacto medido +3 (ver Compilacion y paginas); sin contingencia de D8 |
| OQ2 - ITSM-BERT y Alsac et al. | **Fuera** de este change (default) | No se citan ni se registran en la bitacora |
| OQ3 - vacancia acotada en 3.4 | **Se enuncia** solo porque C1-C2 la confirman (default) | Frase de cierre de 3.4, acotada a las fuentes consultadas con C1 y C2 hasta 2026-10-25 |
| OQ4 - FrugalGPT | **No evadir** los controles anti-bot de OpenReview: el PDF dio 403; se verifica sobre arXiv:2305.05176v1 y se limita la atribucion al concepto de cascada con funcion de puntaje y umbral | Registrado en la bitacora (nota de FrugalGPT) |

### Linea base y vecinos (tareas 1.1 a 1.3)

Rama real `change/c-138-...` (regla G0.6, no `ramagonzalo` literal); arbol limpio; PDF 105 paginas (cuerpo 97, anexos 8); `.bib` 59 entradas; `verify_citations.py` PASS. Holgura: cap. 2 (p. 25) unas 18 lineas; cap. 3 (p. 30) llena; cap. 9 (p. 83) una linea; bibliografia (p. 97) unas 14 lineas. Vecinos: la oracion de Xuan et al. (O3) sigue en 2.5 y no se toco; c-130 y c-131 aplicados (`grep -i "invertida|anti-calibr"` en 07 = 0), por lo que el bloque 7 se ejecuto; ninguna de las seis claves existia.

### Busqueda C1-C2 (bloque 2; detalle en la bitacora, Grupo C)

`FECHA_CORTE_C` = 2026-10-25. arXiv por API: C1 2334 y C2 3600 resultados, 100 primeros de cada una examinados (200) mas 3 consultas dirigidas a tickets y Gemini (7). ACL Anthology (8 examinados) y ACM DL (4) por motor web restringido al dominio; IEEE Xplore: sin resultados del dominio, 0; Scopus: sin acceso, 0; Google Scholar: CAPTCHA (no evadido), 0. Condiciones 2.3: (a) ninguna cascada de reglas y LLM con confianza verbalizada sobre tickets en español; (b) ningun trabajo arbitrado 2023-2026 que evalue Gemini sobre tickets en español (no hubo que detener la aplicacion). Vacancia acotada confirmada sobre las fuentes consultadas.

### Verificacion de las seis fuentes (bloque 3)

Las seis superan las tres compuertas (existencia, metadatos, texto completo): Guo 2017 y Zhao 2021 (PMLR, HTTP 200, metadatos `citation_*`), Tian 2023 y Varshney 2022 (DOI 302 a ACL Anthology, Crossref coincidente), Xiong 2024 (foro de OpenReview con desafio, existencia por la pagina de ICLR, MLAnthology y encabezado del PDF; texto de arXiv v2), Chen 2024 (listado y `.bib` oficiales de TMLR 200; PDF de OpenReview 403, texto de arXiv v1). Reserva de D2 no utilizada.

### Tesis (bloques 4 a 7)

| Tarea | Resultado |
|---|---|
| 4.1 a 4.3 | Bloque aditivo "CALIBRACION DE LA CONFIANZA Y CASCADAS DE MODELOS" en el `.bib` (59 -> 65 entradas; cinco `@inproceedings` y un `@article`); cada clave una sola vez; `git diff --numstat`: 69 agregadas, 0 borradas |
| 5.1 a 5.3 | 2.5: dos oraciones nuevas a continuacion de O2 (Guo, Tian, Xiong) y clausula de cascada en la oracion del esquema hibrido (Varshney, Chen); O3 (Xuan) y O4 (umbral) intactas; lo agregado no cita `xuan2025mmluprox` ni contiene cifras. Presupuesto: unas 13 lineas (supera las 8 del design; absorbidas por la holgura del cap. 2, que no crecio) |
| 6.1 a 6.4 | 3: protocolo extendido con C1, C2, criterios y regla de seleccion, fecha de corte 25-10-2026 (A1-A4, B1 y el corte del 21-10-2026 intactos; las cadenas de C se componen con `\shorthandoff{"}` para que las comillas rectas no se interpreten como atajos de babel); oracion introductoria con cuatro areas; subseccion `subsec:calibracion-cascadas` (3.4) entre 3.3 y la comparativa. El agregado del cap. 3 ronda las 35 lineas (presupuesto 30) |
| 7.1 a 7.3 | 9.2: un parrafo antes de "La novedad del aporte radica", por etapa (confianza de Gemini sobreconfiada segun Xiong; cortocircuito de la etapa determinística por el puntaje de correctitud, no por su confianza; revision humana dependiente de la confianza verbalizada de Gemini); la eficiencia del esquema hibrido sigue "sin contrastarse"; sin cifras nuevas; sin "invertida" ni "anti-calibr" (0). Unas 9 lineas (presupuesto 7) |

### Compilacion y paginas (bloque 8)

- Docker `texlive-thesis` (`latexmk main.tex`, en el arbol): `^!` = 0, `undefined` = 0, `multiply defined` = 0, `main.blg` sin WARN/ERROR, "Found 65 citekeys" = 65 entradas; `verify_citations.py` PASS (65 entradas, 65 claves citadas, 113 comandos de cita, 0 huerfanas, 0 sin usar).
- **Paginas: antes 105 (cuerpo 97, anexos 8); despues `abspage@last{108}`; `Anexos` en p. 101: cuerpo 100, anexos 8; delta +3 / +3.** Inicio de capitulos: 1:11, 2:18, 3:26, 4:32, 5:41, 6:52, 7:62, 8:68, 9:76, 10:86, 11:89, Referencias:94, Anexos:101. Crecieron: cap. 3 (+1, p. 26-31, ultima pagina casi llena), cap. 9 (+1, la pagina nueva contiene 9.6 con unas 13 lineas) y bibliografia (+1, 18 lineas en la pagina nueva). El cap. 2 no crecio. No se aplico la contingencia de D8 (el aumento no supera +3).
- Brecha frente al tope provisional 101 (regla (a)): **+7**; regla (b) (cuerpo <= 100): cuerpo 100, margen 0.

### Libro mayor de paginas

| Change | Commit | Total | Cuerpo sin anexos | Anexos | Delta total | Delta cuerpo | Regla vigente | Estado |
|---|---|---|---|---|---|---|---|---|
| `+c-138` (`change/c-138-estado-del-arte-calibracion-y-cascadas`) | sin commit (lo crea el orquestador) | 108 | 100 | 8 | +3 | +3 | (a) total <= 101 | Medido: `abspage@last{108}`; `Anexos` en p. 101; brecha frente a 101: +7; rama (b): cuerpo 100, margen 0 |

(La fila queda aqui y en la tabla de la seccion G0; el orquestador la consolida.)

### Consignas para otros changes

- **c-136**: puede citar `Guo2017_calibration` (ECE, escalado de temperatura como recalibracion posterior), `Xiong2024_confidence_elicitation` y `Tian2023_verbalized_confidence` (la confianza verbalizada es sobreconfiada, depende de la elicitacion y puede recalibrarse; proponer registrar la accion manual y validar el gate sobre el puntaje en corpus independiente) y `Zhao2021_calibrate_before_use` (calibracion contextual, sensibilidad al prompt). Sin "anti-calibracion" agregada. No afirmar que la cascada reduzca costo: la eficiencia del esquema sigue "no contrastada".
- **c-139**: las seis claves ya existen (reutilizar; `grep -c "{<clave>,"` = 1); `Zhao2021_calibrate_before_use` sirve para la sensibilidad al prompt (solo para GPT-3/GPT-2 con calibracion de la distribucion de salida, no para API sin probabilidades). Retirar O3 (Xuan) de 2.5 libera lineas en el cap. 2. Compensaciones de paginas disponibles: fecha de consulta duplicada en las entradas `@online` y parrafo de Revina duplicado entre 3.3 y 9.2 (el cap. 9 crecio +1 con 13 lineas en la pagina nueva). Las comillas rectas de las cadenas A1-A4 y B1 del protocolo (`03`, parrafo "Protocolo de revision") se imprimen mal por los atajos de babel ("ÏT support", "çlassification"); es un defecto preexistente que en C1-C2 se evito con `\shorthandoff{"}`.
- **c-137**: el texto nuevo lleva tildes; el defecto de comillas de A1-A4/B1 (arriba) es de ortotipografia y puede corregirse sin cambiar el texto fuente de las cadenas (grupo `{\shorthandoff{"}...}`, sin impacto en paginas).
- **c-135**: el cap. 3 queda con unas 2 a 3 lineas de margen en su ultima pagina; cualquier agregado en 3 desborda a una pagina nueva salvo compensacion. `tab:trabajos-academicos` y `tab:comparativa` no se tocaron; la subseccion nueva es 3.4 y la comparativa pasa a 3.5.
- **c-141**: fila `+c-138` = 108 / 100 / 8, +3 / +3; revision del autor pendiente de OQ1 a OQ4; la regeneracion del render y de `main.bbl` es suya; verificacion de FrugalGPT sobre el texto de la version TMLR opcional; Scopus, IEEE Xplore y Google Scholar sin acceso (convencion de la bitacora).

### Reversibilidad

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/02-marco-teorico.tex" "docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex" "docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib" docs/Tesis/Correcciones/bitacora-busqueda-c-110.md`, recompilar. Si c-139 ya retiro O3 o c-136 cita las claves, conservar la fundamentacion de 2.5 y las entradas.

**Estado**: grupo aplicado.


## Dictamen v1.1.0 - B11 (c-136) - Recomendaciones: lineas prioritarias faltantes

**Origen**: change `c-136-recomendaciones-lineas-faltantes` (dictamen CONEAU 2026-10-22: seccion 8 y recomendacion B11). Aplicado el **2026-10-25** en la rama `change/c-136-recomendaciones-lineas-faltantes`, cortada de `ramagonzalo` en `9443331` (merge de c-138). Posicion 9 del orden de la familia (G0.6). Solo documento (gobernanza LOW): sin codigo, sin Gemini, sin tags, sin commit (lo crea el orquestador). Archivos editados: `10-recomendaciones.tex` (unico fuente de tesis), este registro y los artefactos de compilacion versionados de `paper/` (`main.pdf`, `main.xdv`, `main.toc`, `main.aux`, `main.bbl`, `main.bcf`, `main.blg`, `main.lof`, `main.lot`, `main.out`, `main.fdb_latexmk`).

### Open Questions del design - CONFIRMADAS el 2026-10-26 (registradas como PROVISIONAL el 2026-10-25)

| Open Question | Decision PROVISIONAL | Efecto |
|---|---|---|
| OQ1 - extension D7 (SSO, prefijo configurable, Kubernetes, parametros de inferencia) | **Se incluye** en este change (recomendado) | Tres temas nombrados en el nivel de extensiones del parrafo de priorizacion y una oracion sobre los parametros de inferencia en `subsec:calibracion-gate` (unas 40 palabras); las cuatro remisiones de `05` y `06` a `sec:recomendaciones` encuentran destino |
| OQ2 - presupuesto de paginas | **Aceptar +1 pagina** con renegociacion del tope en c-141 (recomendado), aplicando igual las compensaciones del bloque 6 (D10) | No hizo falta la pagina: delta medido 0 (ver Compilacion y paginas); las compensaciones se aplicaron igual |
| OQ3 - citas de recalibracion | **c-138 ya aplicado**: se usan sus claves | `Guo2017_calibration`, `Xiong2024_confidence_elicitation` y `Tian2023_verbalized_confidence` citadas donde se nombra la tecnica; `Zhao2021_calibrate_before_use` no se cita (la calibracion contextual no se nombra); `Bibliography_base.bib` sin cambios (65 entradas) |

### Precondiciones y linea base (tareas 1.1 a 1.4)

- c-130 y c-131 aplicados (`openspec list`: completos); rotulos vigentes: `subsec:calibracion` (07, calibracion por etapa), `subsec:reduccion-intervencion` (07), `subsec:subsistema-clasificacion` (05), `subsec:analisis-errores` (07), `subsec:balance-neto` (08, c-132), `subsec:hipotesis-trabajo` (01, c-133), `subsec:poblacion-muestra-corpus` (04, c-134), `subsec:calibracion-cascadas` (03.4, c-138), `subsec:limitaciones-estudio` (ocho limitaciones), `subsec:capa-procesamiento`, `anexo:H`, `tab:variables`. Las cuatro claves de calibracion existen una vez en el `.bib`.
- Paginas antes: 108 (cuerpo 100, anexos 8); capitulo de recomendaciones 89 a 93 (5 paginas; Referencias en p. 94), con 9 lineas de texto en la p. 93 (unas 21 libres). Palabras antes por subseccion (conteo sobre la fuente, sin comandos): introduccion 106, clasificador supervisado 160, canales 88, panel de monitoreo 170, aprendizaje activo 74, corpus independiente 102, replicacion 112, modelos abiertos 85, base de conocimientos 271, agente conversacional 328; total 1.496.
- Linea base en rojo (tarea 1.4): `label{subsec:calibracion-gate}` y `label{subsec:medicion-intervencion}` = 0; `autoref{subsec:analisis-errores}` = 0 (la remision apuntaba a `subsec:calibracion`); "de todos modos ocurre" = 1; "Kubernetes", "SSO" y "prefijo" = 0; `autoref{subsec:capa-procesamiento}` = 0.

### Mapeo del dictamen (B11) -> pasajes

| Observacion | Correccion | Rotulo |
|---|---|---|
| Linea prioritaria anunciada sin desarrollo: calibracion del gate | Subseccion nueva 11.1 (diagnostico por etapa, validacion propia, senales independientes, recalibracion con advertencia, umbral por curva cobertura-precision fuera de muestra con piso previo) | `subsec:calibracion-gate` |
| Linea prioritaria anunciada sin desarrollo: medicion de intervencion | Subseccion nueva 11.3 (registro primario por caso de cuatro campos, `clasificacion_log` o tabla dedicada, definicion alineada con `tab:variables`, contraste contra la cota de 0,15 o como cobertura efectiva del gate, derivaciones erroneas para el balance neto) | `subsec:medicion-intervencion` |
| Aprendizaje activo prioriza por baja confianza y presupone derivaciones del gate | Seleccion por senales independientes; confianza solo tras recalibracion validada; revisiones vinculadas al registro primario; se retira "de todos modos ocurre" | `subsec:aprendizaje-activo` |
| Replicaciones sin exactitud manual ni muestreo no proporcional | La oracion de c-132 (T14) se extiende, sin duplicarla, con la exactitud del flujo manual sobre el mismo corpus y la asignacion no proporcional con ponderacion (remision a `04:45`, c-134) | `subsec:estudios-replicacion` |
| Parrafo de priorizacion incoherente y remision erronea al analisis de errores | Un parrafo en tres niveles con `autoref` a las tres prioritarias; remision corregida | `subsec:analisis-errores` |
| Remisiones anticipadas sin destino (D7) | SSO, prefijo configurable y Kubernetes en el nivel de extensiones; parametros de inferencia en 11.1 | `sec:recomendaciones` |

Lectura de las consignas previas: la validacion sobre un corpus independiente se conserva (`subsec:corpus-independiente`, de c-144, sin tocar; 11.1 remite a ella para confirmar el umbral y el parrafo de priorizacion la clasifica); la dependencia de la ventaja de las reglas respecto del vocabulario (E4 de c-142) se nombra en 11.1 con remision a `subsec:sensibilidad-ajustes`, sin repetir cifras; la cota de 0,15 de la segunda sub-hipotesis es el contraste de 11.3. Para contener el tope de palabras de 11.1 se retiro la oracion "si ninguna senal alcanza el piso, el gate no queda justificado y la salvaguarda es la revision por muestreo" (D2 punto 5, parte final); la revision por muestreo sigue como una de las senales.

### Palabras por subseccion (antes -> despues; tope)

| Subseccion | Antes | Despues | Tope |
|---|---|---|---|
| Introduccion (parrafo fundido) | 106 | 137 | 140 |
| Calibracion del gate (nueva) | 0 | 219 | 220 |
| Medicion de intervencion (nueva) | 0 | 177 | 180 |
| Aprendizaje activo | 74 | 107 | 110 |
| Estudios de replicacion | 112 | 136 | 140 |
| Base de conocimientos (2 parrafos) | 271 | 152 | 170 |
| Agente conversacional | 328 | 168 | 170 |
| Clasificador supervisado, canales, panel, corpus independiente, modelos abiertos | 605 | 605 | sin cambios |
| **Total** | **1.496** | **1.701** | +205 |

Compensaciones aplicadas (bloque 6): base de conocimientos -119 palabras, agente conversacional -160. Se conservaron todos los elementos exigidos: Twilio Media Streams, vista previa, mu-law 8 kHz a PCM 16 kHz, turnos de habla, costo por minuto, prueba de concepto con la grabacion actual como respaldo (se retiro la deteccion de actividad de voz); y, en la base de conocimientos, dos parrafos, los tres ejemplos de incidentes simples, las dos remisiones y cero citas. El "hacia" mal acentuado de la base de conocimientos desaparecio al reescribir la oracion.

### Verificaciones (tarea 7.3; antes en rojo, despues en verde)

| Verificacion | Antes | Despues |
|---|---|---|
| (a) tres rotulos prioritarios precedentes a `ampliacion-canales` y referenciados en el parrafo introductorio | 1 de 3 | 3 de 3 (orden 11.1, 11.2, 11.3) |
| (b) temas de `ref{sec:recomendaciones}` presentes (SSO, prefijo, Kubernetes, parametros de inferencia) | 0 de 4 | 4 de 4 |
| (c) numeros del diff en la lista blanca | n/a | 0,15 (vigente), 0,70, 0,85, 1,00, 85 %, 100, 45, 8, 16; ninguno nuevo ni retirado |
| (d) `verify_citations.py` | PASS | PASS (65 entradas, 65 claves, 115 comandos, 0 huerfanas, 0 sin usar) |
| (e) topes de palabras | n/a | todos respetados (tabla anterior) |
| "invertida" / "anti-calibr" | 0 | 0 |
| "9,5" en el capitulo | 0 | 0 |
| Partes protegidas (clasificador supervisado, primer parrafo del panel, modelos abiertos) | n/a | `git diff` sin cambios en ellas |

### Compilacion y paginas (tareas 7.1 y 7.2)

- Docker `texlive-thesis` (`latexmk main.tex`, en el arbol): `^!` = 0, `undefined` = 0, `multiply defined` = 0, `main.blg` sin WARN/ERROR, "??" = 0 en el texto del PDF.
- **Paginas: antes 108 (cuerpo 100, anexos 8); despues `abspage@last{108}`; `Anexos` en p. 101: cuerpo 100, anexos 8; delta 0 / 0.** Capitulo de recomendaciones: antes 89 a 93, despues 89 a 93 (5 paginas, dentro del limite duro); Referencias en p. 94. La prevision del design (+1 pagina) no se materializo porque la p. 93 tenia unas 21 lineas libres y el agregado neto es de +205 palabras (unas 20 lineas).
- **Margen restante del capitulo: 0 a 2 lineas** en la p. 93 (llena). Cualquier crecimiento de mas de dos lineas en el capitulo (por ejemplo, la correccion de la frase de Touvron por c-139 si se alarga) abre una sexta pagina y rompe la regla (b) (cuerpo 101).
- Brecha frente al tope provisional 101 (regla (a)): **+7**; regla (b) (cuerpo <= 100): cuerpo 100, margen 0.

### Consignas para otros changes

- **c-135**: hallazgo D7 resuelto aqui (OQ1 incluida); queda sin destino en el capitulo el primer item del alcance excluido de `01-introduccion.tex:74` (integracion con inventario de activos y gestion de configuracion), que remite a `sec:recomendaciones`. La tabla `tab:anexo_gemini_params` califica de "optimizados" los parametros de inferencia mientras `05` dice que no hay optimizacion documentada (hallazgo del design).
- **c-139**: el capitulo cita `Guo2017_calibration`, `Xiong2024_confidence_elicitation` y `Tian2023_verbalized_confidence` en `subsec:calibracion-gate` (verificar la atribucion: escalado de temperatura de Guo; sobreconfianza y dependencia de la elicitacion de Xiong y Tian; "recalibrable" no se afirma de la confianza verbalizada, solo de un puntaje). `subsec:clasificador-supervisado` no se toco (la frase de Touvron sigue intacta, con "hacia" mal acentuado). Cuidar el margen de 0 a 2 lineas del capitulo.
- **c-137**: oraciones reescritas con ortografia revisada (introduccion, 11.1, 11.3, aprendizaje activo, replicacion, base de conocimientos, agente). Quedan intactos los defectos preexistentes: "hacia" en el clasificador supervisado, "aquellas" acentuado, "alla" en el panel y "heterogeneos" ya corregido solo en replicacion.
- **c-141**: fila `+c-136` = 108 / 100 / 8, delta 0 / 0 (prevision 0 a +1); el contrato de rotulos `subsec:calibracion-gate` y `subsec:medicion-intervencion` queda fijado; revision del autor pendiente de OQ1 a OQ3 (PROVISIONAL); `tesis_para_agente.md` no se regenero.
- **c-140**: si agrega remisiones nuevas a `sec:recomendaciones`, debe darles destino en el capitulo (margen de 0 a 2 lineas).

### Reversibilidad

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex" docs/Tesis/Correcciones/dictamen-correcciones.md`, recompilar. Si otros changes ya citan `subsec:calibracion-gate` o `subsec:medicion-intervencion`, conservar las subsecciones.

**Estado**: grupo aplicado.

## Dictamen v1.1.0 - B9, B10 y B13 (cota) (c-135) - Cronologia y consistencia redaccional

**Origen**: change `c-135-cronologia-y-consistencia-redaccional` (dictamen CONEAU 2026-10-22: B9, B10, B13 parte cota telefonica; mas la consistencia del Anexo H y el tiempo de espera de la inferencia, asignados por el orquestador desde c-136). Aplicado el **2026-10-25** en la rama `change/c-135-cronologia-y-consistencia-redaccional`, cortada de `ramagonzalo` en `9865300` (merge de c-136). Posicion 10 del orden de la familia (G0.6). Solo documento y una figura (gobernanza LOW, checkpoint MEDIUM de OQ-3).

### Open Questions del design - CONFIRMADAS el 2026-10-26 (OQ-1 a OQ-5)

| Open Question | Decision PROVISIONAL | Efecto |
|---|---|---|
| OQ-1 - iteraciones | **RESUELTA por el autor (2026-10-26)**: no hubo un numero fijo de iteraciones; se ajustaron durante el proyecto. El tablero tecnico fue Jira y su trial se dio de baja sin export; GitHub Projects se uso para la coordinacion del grupo. No hay fuente primaria de fechas. Regla (iv) de D5: ninguna fecha por interpolacion; la tarea 5.2 se cierra como no reconstruible con fuente primaria | Las iteraciones no se fechan por separado; la figura muestra dos barras de mes (actividad de desarrollo del repositorio, abril a julio y septiembre a octubre de 2026, con pausa 2026-07-10 a 2026-09-10); se retiran "de dos semanas", "12 semanas" y "(Semanas k--k+1)"; no se fija numero de iteraciones; la tarea 5.2 queda cerrada con la salvedad documentada |
| OQ-2 - campanas | Ventana mensual confirmada el 2026-10-09 (manual junio a agosto; automatizada septiembre a octubre de 2026) mas hitos del repositorio | Hitos: `gemini-3.6-flash` 2026-09-24, corrida de correo y formulario 2026-10-02, corrida de telefonia 2026-10-06, recalculo telefonico 2026-10-19; cada uno con comando en `docs/diagrams/cronograma.md` |
| OQ-3 - checkpoint MEDIUM (`06:75`) | El item 5 ya no afirma "sin exposicion al corpus" (c-144/c-130); no declara fechas; c-135 no lo edita | Redaccion final PROVISIONAL |
| OQ-4 - telefonia en `tab:comparativa` | Opcion (b) | Telefonia fuera de la afirmacion comparativa; rasgo de la propuesta en `03:84`; tabla de cuatro columnas sin cambios |
| OQ-5 - acceso institucional | Sin acceso desde esta maquina | Paket 2024 y Colavito 2025 con "no reportado en el alcance revisado" y motivo; Zangari 2023 (acceso abierto) bloqueado por anti-bot: idioma sin dato |

### Precondiciones y linea base (tareas 1.1 a 1.4)

- Predecesores aplicados (`openspec list`: c-130, c-131, c-132, c-133, c-134, c-136, c-138 y c-142 completos; siguen sin archivar, eso es de c-141). Estructura de resultados vigente: seis `subsection` (tiempos, matriz y metricas, intervencion humana, calibracion, sensibilidad, analisis de errores).
- Paginas antes: **108** (cuerpo 100, anexos 8; `Anexos` en p. 101). Ultima pagina por capitulo antes -> despues (lineas no vacias, incluido el encabezado): cap. 1 32 -> 32; cap. 3 36 -> 38; cap. 4 32 -> 26; cap. 6 20 -> 21; cap. 8 36 -> 36; cap. 9 13 -> 13; cap. 10 32 -> 32.
- Instantanea de numeros canonicos (`73,5`, `0,5207`, `71,2`, `363`, `0,9639`, `0,87`, `2.646`, `32,2` sobre `sections/*.tex`): 9, 3, 10, 5, 0, 2, 8, 8 antes y despues (sin cambios).

### Mapeo del dictamen -> pasajes

| Observacion | Correccion | Archivo |
|---|---|---|
| B9 cronologia no conciliada | Fuente unica `docs/diagrams/cronograma.md` (Gantt Mermaid + tabla de procedencia), figura `fig:cronograma` (Anexo A); se retiran los rotulos "Semanas k--k+1", "de dos semanas cada una" y "12 semanas"; 4.9 condensada (la lista de iteraciones se reemplaza por una remision a 6.6 y a la figura); 6.6 declara que la campana manual no es una iteracion y que la automatizada es la iteracion 6; campanas de `04:14` con remision a la figura; "junio de 2026" de la cuarta limitacion reemplazado por `gemini-3.6-flash` (integrada el 2026-09-24); delimitacion de `01:76` | `04`, `06`, `08`, `01`, `12-anexos` |
| B9 (tarea 6.8) entregable de la iteracion 1 | Se retira "el documento de arquitectura y el contrato OpenAPI inicial" de la iteracion 1: `knowledge-base/08_arquitectura_propuesta.md` es de 2026-06-10 (`0ceebe0`) y `docs/openapi.json` de 2026-06-11 (`15f9516`) | `06` |
| B10 resultados | Parrafo introductorio enumera los seis apartados vigentes; "intervencion humana" sin "reduccion" | `07` |
| B10 comparativa | Tres dimensiones; sintesis sin telefonia; telefonia como rasgo propio en el posicionamiento | `03` |
| B10 trabajos academicos | Metrica y corpus completados desde resumen o texto abierto; residuo con motivo; procedencia en `extraccion-metricas-trabajos-c-135.md` | `03` |
| B13 cota | "es una cota inferior de la duracion real por el tope de 45 s de grabacion", con remision a `subsec:metricas-instrumentos`; 20,1 s sin cambios | `09` |
| Anexo H (desde c-136) | "configuracion adoptada" en lugar de "optimizados"; `candidate_count`: "acota la latencia" | `12-anexos` |
| Tiempo de espera (D15) | 10 s -> 30 s por intento y 60 s de presupuesto total (`settings.py:85`, `:104`; commits `11036be` y `429f2c9`); procedencia en `conteos-canonicos-tecnicos.md` | `05`, `12-anexos` |

### Procedencia del cronograma y representacion de las iteraciones

Tabla completa en `docs/diagrams/cronograma.md`. Resumen: desarrollo abril a julio (primer commit 2026-04-06; ultimo previo a la pausa 2026-07-10) y septiembre a octubre (primer commit tras la pausa 2026-09-10), precision de mes; campana manual junio a agosto y automatizada septiembre a octubre de 2026, precision de mes (confirmacion del autor 2026-10-09, T6); hitos de dia: 2026-09-24 (`11036be`), 2026-10-02 (c-68 6.4), 2026-10-06 (c-70 8.2), 2026-10-19 (`4602bf5`). Render: mmdc 11.17.0 (`npx -y @mermaid-js/mermaid-cli@11 ... -w 760`) mas recorte con Pillow.

### Extraccion de metricas (D8)

Detalle por celda en `extraccion-metricas-trabajos-c-135.md`. Revina 2020: exactitud 1,000 (arbol de decision, rasgos linguisticos) frente a 0,433 maximo con TF-IDF, sobre 30 y 60 tickets etiquetados (texto abierto). Zangari 2023: >28 % F1 y ML-BERT hasta 5,7 % F1 y 5,4 % exactitud (resumen); idioma no reportado. Paket 2024: metrica no reportada (acceso cerrado). Liu 2025: F1 0,862 frente a 0,801 de los modelos pequenos; 160 tickets de prueba; idioma no reportado (preprint arXiv). Colavito 2025: tamano y metrica no reportados (acceso cerrado). `verify_citations.py`: PASS (65 entradas, 0 huerfanas, 0 sin usar); `Bibliography_base.bib` sin cambios.

### Compilacion y paginas (tareas 8.1 y 8.2)

- Docker `texlive-thesis` (`latexmk main.tex`): `^!` = 0, `undefined` = 0, `multiply defined` = 0, `main.blg` sin WARN/ERROR.
- **Paginas: antes 108 (cuerpo 100, anexos 8); despues `abspage@last{108}`; `Anexos` en p. 101: cuerpo 100, anexos 8; delta 0 / 0.** Brecha frente al tope provisional 101: **+7**; regla (b) (cuerpo <= 100): cuerpo 100, margen 0.
- Palancas aplicadas (D12): 4.9 condensada; figura recortada y con alto limitado; **desvio**: la figura se reproduce en el Anexo A y no en 6.6, porque el capitulo 6 no tenia holgura (con la figura en 6.6 el total fue 110, y 109 tras acotarla; el Anexo A la absorbe con delta 0); celdas y linea de fuente de `tab:trabajos-academicos` acortadas y columna de metrica ensanchada; parrafos de `01`, `07` y `03` reescritos en longitud neutra. El capitulo 3 queda con 38 lineas en su ultima pagina (sin margen): cualquier agregado lo extiende.
- Libro mayor (G0): fila `+c-135` agregada (108 / 100 / 8, delta 0 / 0).

### Consignas para otros changes

- **c-130**: `CLAUDE.md` y `openspec/config.yaml` siguen diciendo 10 s de timeout; deben alinearse con 30 s por intento y 60 s totales (confirmacion del usuario). c-135 no los toco.
- **c-139**: `03:32` ("confirma el desplazamiento hacia LLM") queda en tension con Paket 2024 y Colavito 2025 (BERT supera o es mas consistente); `01:66` atribuye corpus en ingles, aleman o portugues a Zangari y Colavito, cuyo idioma no consta en las fuentes accesibles; `03:30` puede matizar que las cifras de Revina vienen de 30 y 60 tickets etiquetados.
- **c-140**: la figura esta en el Anexo A (no consume holgura del capitulo 6, que no tiene); solo verificar que el tiempo de espera de la tesis (30 s por intento y 60 s totales, 2 reintentos del backend al modelo) coincide con el codigo; `06:60` (N8N al backend, sin reintentos) no se edito.
- **c-137**: ortografia fuera de los fragmentos reescritos (por ejemplo "multiples" en `03`, "gestiono" en `04`) sin tocar.
- **c-141**: fila `+c-135` = 108 / 100 / 8; hallazgo colateral heredado de c-136: el primer item del alcance excluido de `01-introduccion.tex:74` (inventario de activos y gestion de configuracion) remite a `sec:recomendaciones` sin destino; archivar c-135 con la tarea 5.2 abierta (OQ-1) o cerrarla antes con las fechas de los autores; `tesis_para_agente.md` no se regenero.

### Lo que los autores deben confirmar

1. Inicio y fin de cada una de las seis iteraciones y si fueron de dos semanas y contiguas (OQ-1); con eso se reemplazan las dos barras de mes por seis barras y se cierra la tarea 5.2.
2. Si hubo procesamiento automatizado del corpus entre 2026-09-01 y 2026-09-23 (con `gemini-2.5-flash`) y cuando se generaron las predicciones evaluadas (OQ-2).
3. La redaccion del item 5 de 6.6 y su orden respecto de la campana (c-71 y c-74 midieron sobre el corpus el 2026-10-05 y 2026-10-07) (OQ-3).
4. Que el `.env` de la campana no sobreescribio `GEMINI_TIMEOUT_SECONDS` ni `GEMINI_TOTAL_TIMEOUT_SECONDS` (D15).
5. Acceso institucional a Paket 2024 y Colavito 2025, y al texto de Zangari 2023 (idioma) (OQ-5).

### Reversibilidad

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections" docs/Tesis/Correcciones/dictamen-correcciones.md docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`, `git rm` de `docs/diagrams/cronograma.md`, `paper/figures/cronograma.png` y `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`, y recompilar.

**Estado**: grupo aplicado (34 de 35 tareas; la 5.2 queda abierta por OQ-1).

## Dictamen v1.1.0 - A4, B15 y B16 (c-139) - Correspondencia texto-fuente y metadatos

**Origen**: change `c-139-correspondencia-texto-fuente-y-metadatos` (dictamen CONEAU 2026-10-22: observacion 4 / recomendacion A4, correcciones B15 y B16). Aplicado el **2026-10-25** en la rama `change/c-139-correspondencia-texto-fuente-y-metadatos`, cortada de `ramagonzalo` en `69a9b34` (merge de c-135). Posicion 11 del orden de la familia (G0.6). Documental y bibliografico; un bloque TDD estricto sobre `verify_citations.py` (gobernanza LOW). Ningun numero canonico cambia.

### Open Questions del design - CONFIRMADAS el 2026-10-26 (registradas como PROVISIONAL el 2026-10-25)

| Open Question | Decision PROVISIONAL (del orquestador) | Efecto |
|---|---|---|
| OQ1 - cifras de Paramesh y Shreedhara | **Rama B** (sin acceso al texto completo; no se descargaron copias no autorizadas) | Se retiran 10.000 tickets, "ingles", TF-IDF como representacion y 87 % de los cinco sitios; la fila de `tab:trabajos-academicos` declara "no reportado en el alcance revisado"; el primer criterio del umbral del 85 % (`01:48`) deja de tener ancla numerica |
| OQ2 - ISO/IEC 27701 | **Edicion 2025** (la 2019 figura retirada el 2025-10-14 en el IEC Webstore) | `ISO27701_2025`; `11:40` dice "la norma de gestion de la privacidad ISO/IEC 27701:2025" |
| OQ3 - Russell y Norvig | **2021** (ano de copyright, criterio D8) | Sin cambio de la entrada; el 2020 del dictamen es la fecha de puesta en venta |
| OQ4 - alcance adicional | **Incluidos**: FastAPI (Ramirez), RGPD con URL, y las precisiones de `11:44` y `11:68` | Ver B16 y B15 |
| OQ5 - paginas | Palanca tipografica **reservada para c-141**; criterio de c-139: cuerpo neutral (D13) | El preambulo no se edita; la bibliografia crece |

### Precondiciones y linea base (tareas 1.1 a 1.3)

- Predecesores aplicados (`openspec list`: c-130, c-131, c-132, c-133, c-134, c-136, c-138 y c-142 completos; c-135 con la tarea 5.2 abierta; ninguno archivado). c-138 no se aplicaba en paralelo. c-138 ya inserto las fuentes de calibracion (Guo, Zhao, Tian, Xiong): **no se dejo ancla `% [c-138]`** (0 lineas).
- `verify_citations.py` antes: PASS, 65 entradas, "65 <-> 92 unique citation keys" (rotulo erroneo: suma por archivo). `main.bib`: 65 entradas.
- Paginas antes: **108** (cuerpo 100, anexos 8; `Anexos` en p. 101). "Referencias bibliograficas" empieza en la **p. 94**, la bibliografia ocupa las p. 94-100 y su ultima pagina llega a la fila 21 de ~36 de `pdftotext -lineprinter` (unas 15 filas libres); la ultima pagina del cuerpo (p. 93) esta llena (fila 36). Ultima pagina por capitulo (fila de la ultima linea no vacia): cap. 2 p. 25 fila 39; cap. 3 p. 31 fila 39 (sin holgura).

### Tabla D15 - A4: hallazgo, fuente, evidencia y frase aplicada

Nivel de evidencia: TC = texto completo leido; R = resumen de la pagina del editor o de ACL Anthology; F = ficha oficial; S = fuente secundaria.

| Id / sitio (clave) | Atribucion previa | Lo que la fuente sostiene | Evidencia (URL, nivel) | Correccion aplicada |
|---|---|---|---|---|
| T1 `02:46` `xuan2025mmluprox` | "documentan ... que la calibracion depende del modelo y del dominio" | Benchmark de rendimiento multilingue (29 idiomas, 36 modelos); no trata calibracion (0 apariciones de "calibrat" en el texto) | https://aclanthology.org/2025.emnlp-main.79/ (R); https://arxiv.org/pdf/2503.10497 (TC) | **Frase principal**: oracion retirada; definicion y frase del gate intactas; sin ancla (c-138 ya aplicado) |
| T2 `02:50` Xuan, Lai, Zhang, Grandury, Mayor-Rocher | Zhang "no generalizan homogeneamente fuera del ingles"; Grandury y Mayor-Rocher "diferencias atribuibles al dialecto" | Xuan: caida marcada en idiomas de bajos recursos. Lai: ajuste por instrucciones de LLM abiertos concentrado en ingles y pocos idiomas. Zhang: alternancia de codigo; rinden por debajo de modelos ajustados mucho mas pequenos. Grandury: tabla abierta, 66 conjuntos, 50 modelos, variedades del espanol y lenguas de Espana y America Latina. Mayor-Rocher: TELEIA; comprenden bien el espanol, lejos de la competencia gramatical nativa | https://aclanthology.org/2025.emnlp-main.79/, https://aclanthology.org/2023.emnlp-demo.28/, https://aclanthology.org/2023.emnlp-main.774/, https://aclanthology.org/2025.acl-long.1561/, https://academic.oup.com/applij/advance-article/doi/10.1093/applin/amag048/8789841 (todas R; Mayor-Rocher coincide con Crossref) | **Frase principal** de D3 (acortada para la pagina) |
| T3 `02:44` `ahuja2023mega`, `lai2023okapi` | MEGA y Okapi "evidencian que la seleccion de ejemplos, su orden y la redaccion ... modifican el rendimiento de manera sustancial" | MEGA compara prompting monolingue, cross-lingual zero-shot y translate-test; translate-test mejora a menudo, con ganancias "substantial" en idiomas de pocos recursos y similar en los de muchos; el orden y la seleccion de ejemplos los cita como trabajo previo (Zhao et al., 2021), no los estudia (usa ejemplos aleatorios). Okapi no trata sensibilidad al prompt | https://arxiv.org/pdf/2303.12528 secciones 2.3.1 y 3.1 (TC) | **Atenuada**: "la estrategia elegida puede modificar el rendimiento de manera sustancial, sobre todo en idiomas con pocos recursos"; Lai sale de esta frase; orden y seleccion de ejemplos retirados |
| T4 `02:48` `colavito2025benchmarking` | "muestran que el etiquetado automatico requiere validacion ... no puede aceptarse sin control" | LLM generativos: desempeno que "varies significantly across datasets" y costo computacional; BERT ajustados, consistentes | https://conf.researchr.org/details/esem-2025/esem-2025-journal-first-track/2/Benchmarking-large-language-models-for-automated-labeling-The-case-of-issue-report-c (R, listado ESEM 2025; ScienceDirect y ricerca.uniba.it devuelven 403) | **Frase principal**: la cita respalda la premisa (variacion entre conjuntos); la conclusion queda como inferencia de los autores ("Esta exigencia motiva ...") |
| T5 `02:52` Xuan, Ahuja | "combinan multiples tareas y reportan resultados desagregados" | MMLU-ProX: 14 disciplinas, resultados por idioma; MEGA: 16 conjuntos, 70 idiomas, por idioma | arXiv 2503.10497 y 2303.12528 (TC) | **Precision aplicada**: "abarcan multiples tareas o disciplinas y reportan resultados desagregados por idioma" |
| T6 `02:38` `Jurafsky2023_speech_language` | "sistematizan la disciplina en torno a tres ejes principales" | El indice de la version del 19-08-2026 (Vol. I: n-gramas, embeddings, redes neuronales, Transformers) no enuncia "tres ejes" | https://web.stanford.edu/~jurafsky/slp3/ (TC del indice) | **Atenuada**: "abordan, entre otros temas, el modelado estadistico de secuencias, la representacion distribuida de palabras y las arquitecturas neuronales profundas" (se retira "comprension semantica", que el indice no sostiene) |
| T7 `03:30` `Revina2020_it_tickets` | "Un hallazgo ... los modelos preentrenados pueden rendir peor en este dominio" | Sec. II: los word embeddings "are not applicable in our study" por tres razones (vocabulario del dominio, corpus limitado, explicabilidad): decision de diseno, no resultado medido. Sec. IV.A: expertos etiquetaron 30 y 60 tickets (Data1 y Data2). Conclusion: algoritmos simples con rasgos linguisticos logran buena prediccion | https://depositonce.tu-berlin.de/items/93f30592-198d-48d3-9b05-e36bfc914f6d/full (copia de acceso abierto, TC) | **Frase principal**; ademas "competitivos o superiores" pasa a "competitivos", "Con 30 y 60 tickets etiquetados" (matiz pedido por c-135) y la cola del parrafo se reemplaza por una remision a `subsec:comparacion-literatura` (el argumento ya se enuncia alli; compensa paginas) |
| T8 `03:32` `paket2024itservice`, `colavito2025benchmarking` | "confirma el desplazamiento hacia LLM" | Paket: BERT supera a Titan, Llama y Mistral en 172 clases en turco. Colavito: BERT ajustados mas consistentes y menos costosos que LLM zero-shot | resumen de Paket via OpenAlex https://api.openalex.org/works/doi:10.1109/UBMK63289.2024.10773473 (R; IEEE Xplore no accesible) y listado ESEM (R) | **Frase principal** (acortada) |
| T9 `03:56` | Lai y Zhang en "favorecen a los idiomas con mas recursos" | Lai y Zhang no sostienen esa afirmacion; Ahuja y Xuan si | resumenes citados arriba | Agrupamiento reducido a `ahuja2023mega, xuan2025mmluprox`; las oraciones de Grandury, Mayor-Rocher, Bernal-Beltran y Ramon-Ferrer se conservan |
| T10 `08:30` | "resultan consistentes con los reportados" (contradice "por debajo" de la oracion siguiente) | - | - | **Aplicada**: "se contrastan a continuacion con los reportados"; Revina acortado (argumento solo en `08:34`) |
| T11 `08:34` `Revina2020_it_tickets` | "observan que los modelos preentrenados pueden degradarse" | Ver T7 | Ver T7 (TC) | **Frase principal**: "excluyen por diseno ... lo que desaconseja suponer" |
| T12 `10:14` `Touvron2023_llama2` | "sugieren que los LLM desplegados localmente alcanzan rendimientos competitivos en clasificacion" | Touvron et al. no evaluan clasificacion de tickets; aporta la disponibilidad de pesos abiertos. Paket: BERT supera a Llama y Mistral | resumen de Paket (R) | **Frase principal** (se corrige tambien "hacia") |
| T13 `01:66` `zangari2023ticket`, `colavito2025benchmarking` | "corpus en ingles y, en menor medida, aleman o portugues" | El resumen de Zangari no nombra idiomas; el de Colavito habla de issues de GitHub sin idioma. Ninguna fila vigente de `tab:trabajos-academicos` declara un corpus en espanol (Paramesh: no reportado; Revina: ingles predominante; Zangari: no reportado; Paket: turco; Liu: no reportado; Colavito: sin idioma) | tabla vigente tras c-135 | **Frase principal**: anclada en `\autoref{tab:trabajos-academicos}`; Zangari y Colavito salen de la oracion (siguen citados en el cap. 3) |
| T14 `08:38` | "menor cobertura del espanol ... ingles o aleman" sin cita | Lai: ajuste concentrado en ingles; Xuan: caida en idiomas de menos recursos. Ninguna fuente reporta desempeno en aleman | resumenes (R) | **Frase principal**: cita `lai2023okapi, xuan2025mmluprox`; "aleman" retirado; la cifra propia y la atribucion al esquema multietiqueta no se tocan |
| Paramesh `01:48`, `03:28`, `03:44`, `08:30`, `08:32` `Paramesh2019_it_service_desk` | 10.000 tickets, ingles, TF-IDF, 87 %, "uno de los primeros trabajos exhaustivos" | El resumen (Springer) compara NB multinomial, regresion logistica, kNN y SVM sobre tickets reales no estructurados de una mesa de servicio de infraestructura de TI; "classifier based on SVM performed well on all data samples". TF-IDF solo figura como palabra clave. Sin tamano, idioma ni exactitud. Autoria Paramesh y Shreedhara (Springer y Crossref); "Paramesh y Ramya" es un error de denominacion del dictamen | https://link.springer.com/chapter/10.1007/978-981-13-2514-4_28 (R) | **Rama B** (OQ1): cinco sitios corregidos segun D4; **atenuacion**: el resumen no dice que SVM supere explicitamente a los otros, asi que se escribe "buen desempeno de SVM en todas las muestras" y no "mejor desempeno" |

### B15 - entradas nuevas (tareas 5.1 a 5.5; verificacion del 2026-10-25)

| Clave | Evidencia (URL, nivel) | Datos verificados |
|---|---|---|
| `ISO27001_2022` | https://webstore.iec.ch/en/publication/79694 (F) | ISO/IEC 27001:2022, ed. 3.0, 2022-10-25, titulo completo; Amd 1:2024 es publicacion aparte |
| `ISO27002_2022` | https://webstore.iec.ch/en/publication/74287 (F) | ISO/IEC 27002:2022, ed. 3.0, 2022-02-15 |
| `ISO27701_2025` | https://webstore.iec.ch/en/publication/110123 (F); https://webstore.iec.ch/en/publication/65597 (F) | ISO/IEC 27701:2025, ed. 2.0, 2025-10-14, "Privacy information management systems - Requirements and guidance"; la ficha de 2019 (ed. 1.0, 2019-08-05) figura **Withdrawn 2025-10-14** y remite a la 2025 |
| `NIST2024_csf` | https://doi.org/10.6028/NIST.CSWP.29 -> 302 a https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf (TC); Crossref | CSWP 29, 2024-02-26; sin `urldate` (DOI) |
| `Decreto1558_2001` | http://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=70368 y .../anexos/70000-74999/70368/norma.htm (200; F) | P.E.N., 29-nov-2001, B.O. 03-dic-2001, Reglamentacion de la Ley 25.326 |
| `Wilcoxon1945_individual_comparisons` | doi.org/10.2307/3001968 -> 302 JSTOR; Crossref y OpenAlex (Biometrics Bulletin 1(6), 1945-12, primera pagina 80) | **Paginas 80-83: nivel S** (citas de Wikipedia, DocCheck y OrDB; JSTOR y UCL bloquean la consulta automatizada); Crossref solo registra p. 80 |
| `Cohen1988_power_analysis` | Open Library `isbn/0805802835` (catalogo, LCCN 88012110): 2.a ed., 1988, L. Erlbaum Associates | Sin DOI (el de la reedicion 2013 no se usa) |
| `Efron1993_bootstrap` | doi.org/10.1007/978-1-4899-4541-9 -> 302 Springer; Crossref: 1993, Springer US, ISBN 9780412042317 / 9781489945419 | Editorial Chapman & Hall (ISBN 0-412-04231-2) |

Citas en el texto: `11:8` (decreto), `11:40` (las cuatro normas y marcos, primera mencion; ninguna en titulos, leyendas ni lineas de fuente), `04:71`, `04:75` y `04:87` (Wilcoxon, Efron y Tibshirani con `\textcite` para no encadenar dos parentesis, y Cohen); `Virtanen2020_scipy` sigue citada en `07`. Precisiones de OQ4: `11:44` ("controles de ISO/IEC 27002:2022, que corresponden al Anexo A de ISO/IEC 27001:2022"): el Anexo A de 27002:2022 trata atributos y el Anexo B la correspondencia con 2013 (S: SGS white paper sobre 27002:2022, https://www.sgs.com/-/media/sgscorp/documents/corporate/white-papers/sgs-kn-key-changes-in-iso-iec-27002-white-paper-en-(2).cdn.bg-BG.pdf; el indice oficial de ISO esta tras un control anti-bot); `11:68` ("escala propia del relevamiento"): CSWP 29 define Tiers 1 a 4 de rigor de la gestion del riesgo (Partial, Risk Informed, Repeatable, Adaptive) y no una escala de madurez 0 a 4 (TC).

### B16 - metadatos (tareas 6.1 a 6.8)

| Entrada | Antes | Despues | Evidencia |
|---|---|---|---|
| `Paramesh2019_it_service_desk` | `booktitle` = nombre de la serie | libro *Data Analytics and Learning: Proceedings of DAL 2018*, editores Nagabhushan, Guru, Shekar y Sharath Kumar, serie LNNS vol. 43, pp. 331-346, Springer | pagina de capitulo y de libro de Springer (R) |
| `OGC2011_itil` | autor OGC; nota "por encargo del OGC" | autor Cabinet Office, TSO, ISBN 978-0-11-331307-5, sin nota | portadilla (Crown copyright, licencia del Cabinet Office) vista en un resultado de busqueda; Open Library y AbeBooks para el ISBN; un registro de la Union Africana con ISBN discrepante lista al OGC como autor corporativo (ver desvios) |
| `Jurafsky2023_speech_language` | 2023, sin URL | 2026, URL, `urldate`, "Borrador de la 3.a edicion, version del 19 de agosto de 2026", titulo con "... Speech Recognition with Language Models" | https://web.stanford.edu/~jurafsky/slp3/ (TC); la entrada se conserva `@unpublished` |
| `Stallings2017_computer_security` | 2017 | **2018** | Pearson: "Published by Pearson (August 4, 2017) (c) 2018" (resultado de busqueda; la pagina de producto no es recuperable) |
| `Date2003_database` | 2003 | **2004** | NII CiNii BA63430879 (c2004, LCCN 2003052442) |
| `Russell2021_ai_modern` | 2021 | **2021** (sin cambio) | Pearson (c) 2021 (resultado de busqueda) y portadilla "Copyright 2021, 2010, 2003"; catalogo Libris (c)2021 (no recuperable); AIMA lista 2020 (puesta en venta) |
| `liu2025tickit` | FSE | *FSE Companion '25*, Trondheim, Norway | Crossref (evento "FSE Companion '25 ... Trondheim Norway", pp. 343-354) |
| `Tiangolo2024_fastapi` | "Tiangolo, Sebastian Ramirez" | Ramirez, Sebastian | perfil de GitHub (name), LICENSE y PyPI (author) |
| `GDPR2016` | sin URL | URL ELI + `urldate` | CELEX 32016R0679 resuelve en publications.europa.eu al DO L 119, 4.5.2016; data.europa.eu redirige (307) a la URL ELI; EUR-Lex responde 202 (control anti-bot) |
| Nueve `@manual`/`@misc` con URL | sin `urldate` | `urldate` 2026-10-25 (200 verificado: Airflow, n8n, PostgreSQL 15, FastAPI, 12factor, InfoLEG Ley 25.326, GitHub); `SEPyME2026_mipyme` (200, titulo coherente) y `APA2017` con 2026-10-19 tomada de su nota | `curl -m 40`; APA bloquea con Incapsula (no verificable desde esta maquina) |
| Cinco `@online` y notas | fecha duplicada en la nota; `;` en notas | solo `urldate = {2026-10-19}`; notas sin fecha ni punto y coma (`APA2017`, `SEPyME2026_mipyme`, `mayorrocher2026spanish`) | render de la bibliografia (una sola fecha) |

Comentario agregado al `.bib`: las claves conservan el ano historico (D8); el ano impreso es el de copyright.

### verify_citations.py - TDD (bloque 7)

- **Red de seguridad**: PASS, "65 bibliography entries <-> 92 unique citation keys" (rotulo erroneo; con 73 entradas y las citas nuevas el mismo defecto mostraba "73 <-> 117").
- **RED**: `test_verify_citations.py` (`unittest`, co-ubicado) con el caso de claves compartidas; `python -m unittest test_verify_citations -v` -> `ImportError: cannot import name 'count_unique_cited_keys'` (FAILED, errors=1).
- **GREEN**: `count_unique_cited_keys(file_keys) = len(set().union(*file_keys.values()))` y uso en "Total unique citation keys" y en el mensaje de PASS -> 1 prueba OK.
- **TRIANGULATE**: claves disjuntas (3), diccionario vacio (0) y prueba de `main()` con `SECTIONS_DIR`/`BIB_FILE` temporales: "2 bibliography entries <-> 2 unique citation keys" y "Total unique citation keys: 2" -> 4 pruebas; la ultima asercion (rotulo de la suma por archivo) quedo en rojo a proposito (RED del refactor).
- **REFACTOR**: la suma por archivo se informa como "Total key-file appearances" -> 4 pruebas OK. Salida final sobre la tesis: `73 bibliography entries <-> 73 unique citation keys match perfectly`, `Total key-file appearances: 117`, `Summary: 73 bib entries, 73 unique keys cited, 126 total citation commands`, `STATUS: PASS`.

### Compilacion y paginas (bloque 8)

- Docker `texlive-thesis` (`latexmk main.tex`, incluye `main.bbl`): `^!` = 0, `undefined` = 0, `main.blg` sin WARN/ERROR, "Found 73 citekeys" = 73 entradas del `.bib`, sin `(?`/`??` en el PDF.
- **Paginas: antes 108 (cuerpo 100, anexos 8); despues `abspage@last{109}`; `Anexos` en p. 102: cuerpo 101, anexos 8; delta +1 / +1 / 0.** "Referencias bibliograficas" empieza en la **p. 94 antes y despues** (cuerpo neutral, D13 regla 1). Bibliografia: p. 94-100 antes (ultima fila 21) -> p. 94-101 despues (ultima fila 17): el desborde es de unas 17 filas. Brecha frente al tope provisional 101: **+8**; regla (b) (cuerpo <= 100): cuerpo 101, **margen -1**.
- La primera compilacion dio 111 paginas (`Referencias` en p. 96: los capitulos 2 y 3 crecieron una pagina cada uno). Recortes aplicados dentro de los parrafos editados por c-139: frases de T2, T3, T7 y T8 acortadas; Paramesh (`03:28`) en dos lineas; cola del parrafo de Revina de `03:30` reemplazada por una remision (el argumento ya esta en `08:34`); fila de Paramesh de la tabla con celdas breves. Recortes de B16: fechas de consulta duplicadas de las cinco `@online`, nota de OGC y notas de `APA2017`/`SEPyME2026_mipyme`. Sin tocar el preambulo ni eliminar cifras, figuras o tablas.
- **Palancas para c-141** (D13, no aplicadas): reducir `\bibitemsep` (73 entradas; unas 20 a 22 filas), `\renewcommand*{\bibfont}{\small}` (del orden de 0,8 paginas) o retirar las notas descriptivas de las cuatro `@manual` (2 a 4 filas). Con cualquiera de las dos primeras la bibliografia vuelve a 7 paginas y el cuerpo a 100.
- Libro mayor (G0): fila `+c-139` agregada (109 / 101 / 8, delta +1 / +1).

### Desvios respecto de la letra del dictamen o del design

1. **ISO/IEC 27701:2025** en lugar de la 2019 retirada (OQ2, D6). Las fichas se verificaron en el **IEC Webstore** y las `url` de las tres normas apuntan alli (no a iso.org, que responde 403 con control anti-bot desde esta maquina; no se evadio); es el co-editor oficial de las normas ISO/IEC.
2. **Russell y Norvig 2021** (OQ3).
3. **Paramesh y Shreedhara**: autoria de Crossref y Springer (no "Paramesh y Ramya"); rama B (OQ1); redaccion atenuada a "buen desempeno de SVM en todas las muestras".
4. ***Biometrics Bulletin*** (nombre de la revista hasta 1947), no *Biometrics*; paginas 80-83 con nivel S (pendiente de confirmar en JSTOR).
5. **Cabinet Office** como autor de `OGC2011_itil` (D10): un registro de la biblioteca de la Union Africana lista al OGC para la edicion de 2011 de TSO, con un ISBN (9780113313068) que Open Library asigna a *Service Transition*; se priorizo la portadilla (Crown copyright, licencia del Cabinet Office) y la coherencia con `02:16`.
6. **Jurafsky y Martin**: el titulo vigente de la pagina incluye "with Language Models" y el indice no sostiene "tres ejes"; T6 aplicada.
7. T3 sin "Lai"; T7 con "competitivos" (no "competitivos o superiores"); T14 "reportado para el ingles" (interpretacion de los autores, respaldada por las fuentes de la misma oracion).
8. Wilcoxon, Efron y Tibshirani se citan con `\textcite` en `04:75` para no encadenar parentesis.
9. Hallazgos del registro del compilador (FastAPI, RGPD) y precisiones `11:44` y `11:68` incluidos (OQ4).
10. No verificables desde esta maquina: ficha de ISO (403), `apa.org` (Incapsula), EUR-Lex (202), JSTOR (paginas), ScienceDirect/ricerca.uniba.it (403), IEEE Xplore (Paket, 418/vacio) y paginas de producto de Pearson; en cada caso se uso la fuente alternativa indicada y se atenuo.

### Consignas para otros changes

- **c-138**: sin ancla pendiente; la sugerencia de Zhao et al. (2021) ya estaba cubierta por c-138. Las seis claves de calibracion no se tocaron.
- **c-133**: el primer criterio del umbral del 85 % ya no aporta un ancla numerica (rama B); `01:48` queda con la oracion de D4 y el resto del parrafo literal.
- **c-137** (pasada de ortografia): quedan sin tocar, entre otros, "decada" y la tilde erronea del verbo "formula" en `02`, la tilde erronea de "hacia" en `11:8`, "evalue" en `03:56` y "erronea" en `01:48`.
- **c-140**: nada de c-139 (independiente); `tesis_para_agente.md` no se regenero.
- **c-141**: (1) fila `+c-139` = 109 / 101 / 8 y las palancas de D13 (arriba); (2) `Gomez2026_repositorio` lleva `urldate = 2026-10-25` con version 1.1.1: actualizar ambos al cambiar la version; (3) control de anclas `% [c-138]`: 0 en `02`; (4) control de T13: si `tab:trabajos-academicos` suma un trabajo con corpus en espanol, ajustar `01:66`; (5) regenerar `tesis_para_agente.md`; (6) confirmar con los autores las paginas de Wilcoxon (JSTOR) y la autoria de `OGC2011_itil`.

### Lo que los autores deben confirmar

1. Acceso institucional al capitulo de Paramesh y Shreedhara (OQ1): con el texto completo se pasa a la rama A (pagina por cifra).
2. ISO/IEC 27701:2025 (OQ2), Russell y Norvig 2021 (OQ3), inclusion de FastAPI, RGPD y las precisiones de `11:44` y `11:68` (OQ4), palanca tipografica reservada (OQ5).
3. Paginas 80-83 de Wilcoxon (1945) en JSTOR y autor corporativo de `OGC2011_itil` en un catalogo nacional.

### Reversibilidad

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections" "docs/Tesis/v10 (IA)/Bibliography_base.bib" "docs/Tesis/v10 (IA)/verify_citations.py" docs/Tesis/Correcciones/dictamen-correcciones.md`, eliminar `docs/Tesis/v10 (IA)/test_verify_citations.py` y recompilar. No se crean ni mueven tags.

**Estado**: grupo aplicado (46 de 46 tareas).

## Grupo: Revision ortotipografica (B14, c-137)

**Origen**: change `c-137-revision-ortotipografica` (dictamen CONEAU 2026-10-22: seccion 1, tercer defecto de forma, y recomendacion B14). Bloque 1 (herramienta `revision_tildes.py` con TDD estricto) aplicado antes en el commit `b241ec8`; bloques 2 a 8 aplicados el **2026-10-25** en la rama `change/c-137-revision-ortotipografica`, con todo `ramagonzalo` fusionado (posicion 13 del orden de la familia, G0.6; c-140 excluido de este tramo, ver mas abajo). Sin commit propio de este apply (lo crea el orquestador). Gobernanza LOW: solo diacriticos, las comillas de seis cadenas de busqueda, una opcion de geometria (ver "Desvios") y, por OQ1, las menciones de sectores.

**Commit base de la pasada**: `f1fc134dc59673939a19c99364a13991f3468e4b` (merge de `ramagonzalo` en `change/c-137-revision-ortotipografica`; descendiente de `846189f`, c-139). Copia de las versiones base de `paper/sections/*.tex` (15 archivos), `paper/main.tex`, `paper/preambles/preamble.tex` y `Bibliography_base.bib` en un directorio temporal del repositorio, borrado al cerrar.

### Open Questions del design - CONFIRMADAS el 2026-10-26 (registradas como PROVISIONAL el 2026-10-25)

| Open Question | Decision PROVISIONAL (del orquestador) | Efecto |
|---|---|---|
| OQ1 - nombres de sector | **Si, unificar** a la cadena canonica sin tildes las 15 menciones con tilde de los 5 pasajes que presentan los sectores como "canonicos" (recomendacion D7; el default del design para "sin respuesta" era no unificar) | Ver "Decision OQ1". Reversible: `git checkout f1fc134 -- "docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex" ...` restaura las formas con tilde sin tocar el resto |
| OQ2 - fe de errata del dictamen | **No** editar el dictamen auditado | La discrepancia de conteos se consigna solo aqui ("formula" verbal 1 y no 4; "continua" verbal 4 y no 11) |

### Precondiciones y linea base (tareas 2.1 a 2.5)

- Predecesores (`openspec list --json`): c-130, c-131, c-132, c-133, c-134, c-136, c-138, c-139 y c-142 con todas sus tareas completas; c-135 con 34 de 35 (la 5.2 abierta); ninguno archivado. **c-140 no edito prosa de la tesis**: `git log --oneline -- "docs/Tesis/v10 (IA)/paper/sections"` no muestra commits de c-140 (ultimo: c-139, `c269f09`). c-140 queda excluido de este tramo por decision del orquestador, pendiente del usuario; si luego edita prosa, correr `revision_tildes.py --check` despues.
- Arbol limpio en `docs/Tesis/v10 (IA)` al inicio. La herramienta (292 pruebas) estaba en verde.
- Compilacion base (`texlive-thesis`, `latexmk main.tex`): `abspage@last{109}` (cuerpo 101, anexos 8; `Anexos` en p. 102 de `main.toc`), `grep -c "^!" main.log` = 0, referencias/citas indefinidas = 0, `main.blg` sin `WARN`/`ERROR`, **0 avisos de `fancyhdr`** (el unico `headheight` del log es el volcado del parametro `\headheight=12.0pt`), 33 avisos `Overfull`.
- Conteos base en `sections/`: `Seguridad Informatica` 7, `Soporte Tecnico Hardware` 8, `Soporte Tecnico Software` 16, `Bases de Datos` 15, `Sistemas` 14; con tilde (Informatica, Tecnico): 5 menciones de cada una de las tres cadenas con acento posible. "mejora continua" 3, "integracion continua" 5, "la formula" (sustantivo) 3. `verify_citations.py`: PASS, 73 entradas, 0 huerfanas. 73 claves `@tipo{clave` en el `.bib`.

### Inventario y correcciones (tareas 3.1 a 3.3 y 4.1 a 4.5)

Inventario regenerado sobre el arbol posterior a c-139 (la linea base del design ya no existe tal cual: c-136, c-138 y c-139 reescribieron pasajes y retiraron "multiples" de `03`, dos "hacia" de `10`, "esta acotada" de `07`, "simultanea" y "asigno"). Toda errata conocida que seguia presente figuro en el inventario.

| Clase | Cantidad | Tratamiento |
|---|---|---|
| Inventario inicial | 50 candidatos: 23 `INEQUIVOCO` prosa, 25 `AMBIGUO` prosa, 1 `INEQUIVOCO` tabla (`Version`), 1 `AMBIGUO` tabla (`telefono`) | - |
| Candidatos agregados por los ajustes de la herramienta (ver abajo) | +8: 5 `INEQUIVOCO` prosa ("guian" x2, "envian", "demas" x2) y 3 `AMBIGUO` tabla ("Si, ..." de `tab:comparativa`) | - |
| **Total** | **58** | - |
| Corregidos por `--apply` (`INEQUIVOCO` prosa) | **28** ocurrencias en 24 lineas | `--diff` revisado hunk por hunk (sin falsos positivos); segundo `--diff` vacio; sin `.bak` |
| `AMBIGUO` prosa corregidos a mano | **17** | fila `corregir` con justificacion gramatical |
| Celdas de tabla corregidas a mano | **3** ("Si" -> "Si" con tilde en la tabla comparativa de soluciones, sin cadenas canonicas) | fila `corregir` |
| `mantener` | **10**: "valida" x2 (verbo), "explicita" (verbo), "fijo" (adjetivo), "invalida" (verbo), "Aun"/"aun" x3 (valor de "incluso"), `telefono` (identificador del modelo de datos), "Version" (expansion en ingles del glosario) | fila `mantener` |

Registro de decisiones: `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv`, **36 filas** (26 `corregir`, 10 `mantener`; incluye 6 filas de documentacion de OQ1 y de la etiqueta de version del `.bib`, que no son candidatos del inventario). `revision_tildes.py --check` termina con **codigo 0** y sin avisos.

Conteos por forma, antes -> despues, en `sections/` (a mano: `grep -o -w`):

| Forma | Antes | Despues | Via |
|---|---|---|---|
| erronea / erroneas | 2 / 1 | 0 / 0 | script |
| heterogeneas / heterogeneos | 2 / 1 | 0 / 0 | script |
| multiples | 5 (`01` x4, `06` x1) | 0 | script |
| inequivocos, antiguedad, perimetro, enganosa, escaner, decada | 1, 2, 2, 1, 1, 1 | 0 | script |
| "mas alla" (alla) | 3 | 0 | script |
| "aquellas" con tilde indebida (`10:22`) | 1 | 0 (sin tilde) | script |
| guian / envian / demas | 2 / 1 / 2 | 0 | script (lexico ampliado, ver abajo) |
| "hacia" con tilde indebida, preposicion (`02:84`, `11:8`) | 2 | 0 | a mano |
| "se formula" con tilde indebida, verbo (`02:44`) | 1 | 0 (sin tilde) | a mano |
| "continua" verbal (`01:10`, `06:40`, `06:50`, `08:62`) | 4 | 0 (verbo acentuado) | a mano |
| "esta"/"este" verbales sin tilde (`06:40`: "lo esta", "no este vacia") | 2 | 0 | a mano |
| evalue, sustento, gestiono, comun, cache | 1 cada una | 0 | a mano (se acentuan) |
| cual / como interrogativos (`01:28`) | 1 / 1 | 0 | a mano (se acentuan) |
| "por si mismo" (`11:20`) | 1 | 0 (pronombre con tilde) | a mano |
| mejora continua / integracion continua / la formula con tilde, sustantivo (usos legitimos) | 3 / 5 / 3 | 3 / 5 / 3 | intactos |

**Discrepancias con el dictamen (OQ2, solo aqui)**: el dictamen informa 4 "formula" verbales y 11 "continua" verbales; la verificacion encuentra **1** y **4**. Un reemplazo ciego de las 16 "continua" o de las 4 "formula" habria introducido 15 erratas nuevas. Los criterios de aceptacion de este change se formularon por categoria gramatical.

**Hallazgos fuera de la muestra del dictamen**: "multiples" (5 tras c-139; 6 en la linea base), "alla" (3), "escaner", "por si mismo", "decada", "evalue" (`03:56`), "sustento" (`06:85`), "gestiono" (`04:97`), "comun" (`02:28`), "cache" (`02:65`), interrogativos sin tilde en `01:28`, "guian" (2), "envian", "demas" (2) y "Si" de la tabla comparativa de `03` (3), mas las cadenas de `main.tex`, del preambulo y las notas del `.bib` (abajo). Las del tipo "guian", "envian", "demas" y "Si" **escaparon a la herramienta** y se descubrieron con un barrido propio de las 4.102 palabras distintas de la prosa (3.234 sin tilde de 4+ letras revisadas a ojo) y de las zonas `tabla` y `cita`; se corrigieron ampliando la herramienta con prueba previa.

**Barrido `--todos` (tarea 4.4)**: 949 filas en total (452 "que", 169 "como", 77 "registro", 60 "esta", 48 "este", 39 "cuando", 24 "donde", 15 "hacia", 11 "si", 11 "continua", 10 "cual", 8 "desarrollo", 6 "cuales", 5 "promedio", 3 "formula", 3 "aun", ...). Revisadas una por una las **149 ocurrencias de los cinco pares de riesgo** ("esta"/"este" 108, "continua" 11, "formula" nominal y verbal 4, "hacia" 15, "si" 11), mas "aun", "cual/cuales", "donde", "cuando" y los sustantivos homografos "registro/desarrollo/promedio" (por palabra previa). Ningun caso adicional salvo los de la lista anterior. Todas las "esta/este" restantes son demostrativos (sin tilde, incluido "tampoco esta se contrasta" y "que esta se corrige", pronombres sin tilde segun la ortografia vigente), todas las "continua" son adjetivos y todas las "hacia" son preposiciones.

### Ajustes a la herramienta (TDD; suite 292 -> 298 pruebas)

Cada ajuste con su prueba RED antes del GREEN; la salida del script nunca se edito a mano.

1. Lexico `INEQUIVOCO` ampliado con **"guian", "envian", "demas"** (formas con tilde en las tres) (3 casos parametrizados nuevos en `test_forma_sin_tilde_que_no_es_palabra_valida_es_inequivoca`; RED 3 fallos, GREEN). Ninguna forma es homografo valido.
2. Senal de "si" (conjuncion, sin tilde) frente al pronombre o afirmacion con tilde: se informa tambien cuando va **seguido de puntuacion al inicio de frase o de celda** ("Si, modulo de IA"), no solo tras preposicion (2 casos nuevos en `test_pares_ambiguos_se_informan_con_senal_de_contexto`, uno en celda `tabular`; RED 2 fallos, GREEN). Los usos legitimos ("si se proyecta ...", "si el valor supera ..., entonces") siguen sin reporte.
3. `--check` ya no avisa en stderr de decisiones `corregir` sin candidato (la correccion esta aplicada por definicion): `test_check_no_avisa_de_decisiones_corregir_ya_aplicadas` (RED 1 fallo, GREEN). Las decisiones `mantener` huerfanas siguen avisando.

Los falsos positivos `AMBIGUO` ("valida", "explicita", "fijo", "invalida", "aun") no se corrigieron en el lexico: son homografos legitimos que la herramienta debe seguir informando y se resuelven con `mantener` en el registro (D2/D4). Ningun falso positivo `INEQUIVOCO` aparecio en `--diff`.

### Cadenas visibles y bibliografia impresa (bloque 5)

- `paper/main.tex`: los tres titulos "Indice ..." (general, de tablas, de figuras) y el titulo "Referencias bibliograficas" de `\printbibliography` pasan a llevar tilde (4 lineas; comentarios intactos).
- `paper/preambles/preamble.tex`: encabezado "AUTOMATIZACION DE MESA DE AYUDA" (con tilde en la O), `pdftitle`, `pdfkeywords` (automatizacion, clasificacion, espanol), `bibliography = {Referencias bibliograficas}` y, ademas, el `\title{...}` (automatizacion, orquestacion), que el design no listaba (5 lineas).
- `Bibliography_base.bib`: 7 campos `note` ("Documentaci{\'o}n t{\'e}cnica [oficial]" x4, "Documentaci{\'o}n de la plataforma ..." x3) y la etiqueta "(Versi{\'o}n 1.1.1)" del titulo de `Gomez2026_repositorio` (decision D6 registrada en el TSV); "edici{\'o}n" ya la habia corregido c-139. La lista de claves `@tipo{clave` es identica a la base (73). **Nota para c-141 (B16b)**: al actualizar el numero de version de `Gomez2026_repositorio`, conservar "Versi{\'o}n".
- Control de la herramienta sobre `main.tex` y el preambulo (`--archivos`): sin candidatos pendientes.

### Decision OQ1 - nombres de sector (bloque 6)

PROVISIONAL, 2026-10-25: se unifican a la cadena canonica sin tildes las **15 menciones** de los 5 pasajes `01-introduccion.tex:48` y `:72`, `04-marco-metodologico.tex:36` (fila de la tabla de variables, en zona tabla) y `:45`, y `05-arquitectura.tex:100` (fila del modelo de datos, en zona tabla); cada pasaje consta en el TSV. Conteos de las cinco cadenas canonicas (`grep -o` sobre `sections/*.tex`):

| Cadena | Antes | Despues | Esperado (base + unificadas) |
|---|---|---|---|
| `Seguridad Informatica` | 7 | 12 | 7 + 5 |
| `Soporte Tecnico Hardware` | 8 | 13 | 8 + 5 |
| `Soporte Tecnico Software` | 16 | 21 | 16 + 5 |
| `Bases de Datos` | 15 | 15 | sin cambio |
| `Sistemas` | 14 | 14 | sin cambio |

Las formas con tilde quedaron en 0 (antes 5, 5 y 5). Ninguna ocurrencia previa de las cinco cadenas se altero. La tarea 6.3 (excepcion documentada) no aplica.

### Comillas rectas de las cadenas A1-A4 y B1 (consigna de c-138/c-139)

Las cadenas de busqueda A1, A2, A3, A4 y B1 del parrafo "Protocolo de revision" (`03-estado-del-arte.tex:8`) se imprimian mal por los atajos de babel ("ÏT support", "çlassification", con `.` en lugar del cierre). Se envolvio cada `\emph{(...)}` en `{\shorthandoff{"}...}`, igual que c-138 hizo con C1-C2; el texto fuente de las cadenas no cambia. Resultado en el PDF: `("help desk" OR "service desk" OR "IT support")`, impreso con comillas de cierre a ambos lados, ahora **identico en forma a C1-C2** (las comillas de apertura se imprimen con el glifo de cierre; es el comportamiento de XeLaTeX con el mapeo `tex-text` y se deja como esta para no tocar el texto). Es la unica modificacion no diacritica de `sections/` (una linea, solo la envoltura).

### Verificacion global (bloque 7)

- **Invariante diacritico** (`--base`): sobre `sections/` contra la base, codigo 1 con **una sola linea** reportada (`03:8`, la envoltura `{\shorthandoff{"}...}` de las cinco cadenas); contra una copia de la base a la que solo se aplico esa envoltura, **codigo 0**. Sobre `main.tex`, preambulo y `.bib` contra la base, codigo 1 con una sola linea (`preamble.tex:20`, opcion `headheight=13pt`, ver "Desvios"); contra una copia de la base con esa unica opcion, **codigo 0**. Cifras, claves, rutas y numero de lineas intactos.
- Formas inequivocas en cero (`grep -o -w`), contextos de la linea base en cero, usos legitimos 3 / 5 / 3 iguales a la base, cadenas canonicas segun la tabla de OQ1.
- Compilacion final (`texlive-thesis`, `latexmk main.tex`): `abspage@last{109}` (**igual a la base**), `Anexos` en p. 102, `grep -c "^!" main.log` = 0, referencias/citas indefinidas = 0, `main.blg` sin `WARN`/`ERROR`, **0 avisos `fancyhdr`**, 31 `Overfull` (base 33). `Referencias bibliograficas` (con tilde) figura en `main.toc` (p. 94). El PDF muestra el encabezado, los tres indices y el titulo de la bibliografia acentuados. Comparacion pagina a pagina del texto del PDF antes/despues (`pdftotext`, sin diacriticos): solo difieren las pp. 26-27 (comillas de A1-A4/B1 y una linea que pasa a la p. 27).
- `verify_citations.py`: PASS (73 entradas, 0 huerfanas). `tesis_para_agente.md` regenerado con `build_tesis_para_agente.py`: no contiene ninguna forma inequivoca corregida ni los contextos de la base ni formas con tilde de sectores. **Aviso**: el render anterior estaba desactualizado (c-130..c-139 no lo regeneraron), de modo que el diff incluye tambien el contenido de esos changes.
- Cierre tecnico: `--check` codigo 0; suite de la herramienta 298 pruebas en verde.

### Desvios y causa raiz

- **Desvio (headheight)**: la mayuscula acentuada del encabezado ("AUTOMATIZACION" con tilde en la O) eleva la caja del encabezado a 12,56 pt y `fancyhdr` emitio **105 avisos** (`\headheight is too small (12.0pt)`) en la primera compilacion. Se agrego `headheight=13pt` a las opciones de `geometry` (`paper/preambles/preamble.tex:20`). Con `top=2.54cm` el cuerpo del texto no se mueve (el encabezado vive en el margen), y la paginacion se mantuvo en 109. Es una modificacion no diacritica, minima y reversible (quitar la opcion devuelve los 105 avisos, sin efecto visible). A confirmar por los autores.
- **Causa raiz**: `docs/Tesis/acentuar_tesis.py` mapea de forma incondicional "hacia" (preposicion) a su forma con tilde (imperfecto de "hacer") y "aquellas" (determinante) a su forma con tilde (commit `e2bbd3f`, que tambien creo la utilidad); `acentuar_tesis_v9.py` (c-106) mantiene "formula" (verbo) -> forma con tilde del sustantivo y "fijo" (adjetivo) -> el preterito "fij" con tilde en la o ("se formula" con tilde indebida entra con `f0546ec`). Precedente: c-80 (F1) ya tuvo que revertir 50 erratas del mismo diccionario. Ambas utilidades quedan marcadas **DEPRECADO (c-137)** en su docstring de cabecera (sin cambios de logica; `grep -c DEPRECADO` = 1 en cada una; el diff solo agrega 7 lineas al docstring; compilan).

### Procedimiento de la pasada corta (para c-141)

Despues de cualquier edicion tardia de la prosa, desde la raiz del repositorio: `python "docs/Tesis/v10 (IA)/revision_tildes.py" --check` (codigo 0 = sin pendientes). Si falla: `--diff` y `--apply` para lo `INEQUIVOCO` en prosa; decidir uno por uno lo `AMBIGUO`, de tabla o de cita y registrarlo en `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv` (columnas `archivo`, `token`, `contexto`, `decision`, `forma_final`, `justificacion`; clave por archivo, token y contexto, sin numero de linea); repetir hasta 0. Si c-141 edita `main.tex`, el preambulo o el `.bib`, repetir ademas los `grep` del bloque 5 y `revision_tildes.py --archivos paper/main.tex paper/preambles/preamble.tex`. `--base <dir>` verifica que una pasada sea puramente diacritica. La herramienta no detecta todo (ver "guian", "demas"): un barrido propio de palabras sin tilde antes de la release es recomendable.

### Para c-141 y para los autores

- c-141: (1) fila `+c-137` del libro mayor = 109 / 101 / 8 (neutral); el tope lo decide c-141 (brecha +8 frente a 101; rama (b): cuerpo 101, margen -1); (2) correr `--check` despues de todo cambio de prosa y regenerar `tesis_para_agente.md`; (3) conservar "Versi{\'o}n" y la opcion `headheight=13pt`; (4) si c-140 edita prosa, correr la pasada corta.
- Confirmadas por el autor el 2026-10-26: OQ1 (unificacion de sectores), la opcion `headheight=13pt`, la forma de las comillas de apertura de A1-A4/B1/C1/C2 (glifo de cierre) y "cache" (sin tilde) en `02:65`.

### Reversibilidad

`git checkout f1fc134 -- "docs/Tesis/v10 (IA)/paper/sections" "docs/Tesis/v10 (IA)/paper/main.tex" "docs/Tesis/v10 (IA)/paper/preambles/preamble.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib" "docs/Tesis/v10 (IA)/tesis_para_agente.md" docs/Tesis/acentuar_tesis.py docs/Tesis/acentuar_tesis_v9.py`, recompilar y regenerar `tesis_para_agente.md`. La herramienta, sus pruebas y el registro de decisiones pueden conservarse. No se crean ni mueven tags.

**Estado**: grupo aplicado (41 de 41 tareas; bloque 1 en `b241ec8`).

## Integracion c-141 - tramo de integracion (FASE 36, grupos 2 a 4 y 6)

**Origen**: change `c-141-integracion-release-v1-2-0`, apply parcial del tramo de integracion: tareas 2.1 a 2.8, 3.1, 3.2, 4.1 a 4.6 y 6.1 a 6.3 de `tasks.md`. Aplicado el **2026-10-26** en la rama `change/c-141-integracion-release-v1-2-0` (cortada de `ramagonzalo` en `b3c6f0f`, merge de c-137). Sin commit (lo crea el orquestador), sin push, sin merge, sin tag, sin archivado de changes. **Actualizacion 2026-10-26 (tramo A del apply)**: con la decision del usuario sobre el tope de paginas se ejecutaron 3.3 a 3.6 y la parte permitida de 2.9 (ver "Compactacion P7" y "Archivo de la familia" mas abajo). **Actualizacion 2026-10-26 (tramo B del apply)**: se ejecutaron 5.1, 5.2, 5.3, 6.4, 7.1 a 7.7 y 8.1 (secciones "Contenido de C1 y compilacion de registro", "Cierre del libro mayor", "Renders y base de conocimiento" y "Verificacion previa al tag", mas abajo); 8.2 (commit C1) la hace el orquestador con este arbol; 8.3 no aplica (c-140 no aplicado). **No ejecutadas** (motivo): 8.4 a 8.8 y 9.x (tag, push, C2, PR y cierre documental: acciones publicas o posteriores al tag). Gobernanza MEDIUM. Cero llamadas a Gemini; `App/`, `n8n/`, `data/`, `evaluation/` (salvo lectura) y `CLAUDE.md` sin cambios en este tramo.

### Estado de la familia (tarea 2.1)

`openspec list --json` y `ls openspec/changes/archive/ | grep -E "c-12[5-9]-|c-13[0-5]-|c-142-"` (2026-10-26): ningun change de la FASE 36 esta archivado (el archivo es de la tarea 2.9); los archivados c-125..c-129 son de otra fase.

| Change | Tareas | Estado | Pendiente de archivo |
|---|---|---|---|
| c-130 | 37/37 | aplicado | si |
| c-131 | 81/81 | aplicado | si |
| c-132 | 29/29 | aplicado | si |
| c-133 | 42/42 | aplicado | si |
| c-134 | 47/47 | aplicado | si |
| c-135 | 34/35 | aplicado con la **tarea 5.2 abierta** (fechas de las seis iteraciones Scrumban sin fuente primaria: `gh` sin scope `read:project`; OQ-1 PROVISIONAL) | si, con la 5.2 abierta o cerrada antes con las fechas de los autores |
| c-136 | 24/24 | aplicado | si |
| c-137 | 41/41 | aplicado | si |
| c-138 | 30/30 | aplicado | si |
| c-139 | 46/46 | aplicado | si |
| c-140 | 0/73 | **EXCLUIDO provisionalmente** de la integracion (decision del orquestador, 2026-10-25); no edito prosa de la tesis (`git log -- "docs/Tesis/v10 (IA)/paper/sections"` sin commits de c-140); **decision del usuario pendiente**: incluirlo (bloques de codigo, prueba de humo y texto de tesis antes de c-137, lo que obliga a repetir la pasada corta) o archivarlo como NO REALIZADO con `openspec archive c-140-endurecimiento-tecnico-tls-reintentos-e2e -y --skip-specs` (precedente c-67) | -- |
| c-142 | 91/91 | aplicado | si |
| c-141 | 7/52 antes de este tramo (grupo 1) | en curso | su archivo es de la fase archive |

### Reconciliacion del mapeo de D1 con los artefactos (tarea 2.2)

Contraste de los `proposal.md` y `tasks.md` de cada change y de los grupos de este registro con el mapeo de D1. Resultado: **ninguna parte de A1-A5 ni de B4-B16 queda sin dueno y ninguna tiene dos duenos de edicion**; dos salvedades que se devuelven al orquestador:

| Parte | Dueno | Comentario |
|---|---|---|
| A1 | c-130 | Magnitudes por etapa, alcance del gate y cortocircuito; c-133 solo alinea la sub-hipotesis de intervencion con la base de 69 casos |
| A2 | c-131 | Exactitud por etapa, calibracion por etapa y McNemar |
| A3 | c-132 | Balance neto |
| A4 | c-139 (correspondencia texto-fuente) y c-138 (fuentes de calibracion y cascadas, seccion 4 del dictamen y criterio 3 residual) | **Salvedad 1**: el `proposal.md` de c-138 y el de c-139 nombran ambos a A4. No hay solapamiento de texto (c-138 agrego seis entradas y la subseccion 3.4; c-139 corrige atribuciones y agrega ocho entradas). La matriz las separa en filas distintas |
| A5a | c-130 (a traves de c-144, que ya declaro la procedencia en `0c7f5bc`) | T04, T12, T13 y T14 de c-130 solo se verificaron |
| A5b | c-142 | Sensibilidad fuera de muestra, septima limitacion y evidencia del objetivo 6 |
| B4, B5, B6 | c-133 | |
| B7a | c-134 | |
| B7b | c-131 | |
| B8 | c-131 | |
| B9 | c-135 | |
| B10a-d | c-135 | |
| B11 | c-136 | |
| B12 | c-134 | |
| B13a | c-135 | |
| B13b | c-134 | |
| B14 | c-137 | |
| B15 | c-139 | |
| B16a | c-139 | |
| B16b | c-141 | En C1 (tarea 5.1); pendiente |

Observaciones no numeradas del dictamen (D10): `timeout` de 10 s frente a 30 s -> dueno **c-135** (D15; aplicado: `05-arquitectura.tex` y `tab:anexo_gemini_params` dicen 30 s por intento y 60 s en total, procedencia en `conteos-canonicos-tecnicos.md`; c-140, opcional, trata otro timeout, el del handoff telefonico, `TELEFONIA_HANDOFF_TIMEOUT_S`, no el de la inferencia). **Salvedad 2**: `CLAUDE.md` (linea 51) y `openspec/config.yaml` (linea 34) siguen diciendo 10 s; c-135 lo dejo a c-130 "con confirmacion del usuario" y c-130 solo edito las lineas del gate: queda **sin dueno** y fuera de la tesis. Se registra como pendiente (ver "Pendientes").

### Sincronizacion con el remoto (tarea 2.3)

- `git fetch origin` (2026-10-26): sin errores. `origin/main` = `origin/RamaLuca` = `11e969c5919e56ca65bf10ca8e9c5bc4e43e19ac`.
- `git log --oneline ramagonzalo..origin/main | wc -l` = **0** y `git log --oneline ramagonzalo..origin/RamaLuca | wc -l` = **0**.
- `git merge-base --is-ancestor origin/main HEAD` (y lo mismo para `origin/RamaLuca`): **verdadero**. `git diff --stat $(git merge-base HEAD origin/main) origin/main -- docs/Tesis/ knowledge-base/ evaluation/ CHANGES.md` vacio (idem `origin/RamaLuca`).
- No hay nada que integrar: **no se hizo `git merge`** (instruccion del orquestador). Hay que repetir esta comprobacion antes de C1 (tarea 8.1).

### Regresion cruzada (tarea 2.4)

Se re-ejecutaron sobre el arbol integrado (HEAD `b3c6f0f` mas las ediciones de este tramo) los comandos de verificacion automatizables de los `tasks.md` de c-130..c-139 y c-142 (greps de frase presente/ausente y de conteos, existencia de rotulos y claves del `.bib`, conteos de palabras del resumen) con un ejecutor propio (170 comprobaciones, mas las manuales de c-135, que no tiene greps en su `tasks.md`), mas las suites y herramientas. Las verificaciones de compilacion de cada `tasks.md` (sin indefinidas, sin `??`, `main.blg` limpio, `verify_citations.py`) se cumplen en el arbol final (ver "Compilacion de verificacion").

| Change | Resultado | Detalle |
|---|---|---|
| c-130 | **PASS** | 28 comprobaciones; 1 con expectativa superada por un cambio posterior legitimo: `grep -c "estimaciones dentro de la muestra" 08-discusion.tex` da 3 y la tarea 5.3 esperaba 1 (c-142 T04 y c-133 agregaron la calificacion en otros parrafos); las frases refutadas siguen en 0. Suite del backend de la tarea 1.2: **125 passed** |
| c-131 | **PASS** | 3 comprobaciones; suite `evaluation/` **451 passed, 2 skipped** (linea base de c-142; los 2 skips son las pruebas contra el historial git) |
| c-132 | **PASS** | 27 comprobaciones; 2 con expectativa superada: "presenta seis limitaciones" (4.2) hoy es "presenta ocho limitaciones" por c-142 (septima) y c-133 (octava), cardinal confirmado; `subsec:balance-neto` en `10-recomendaciones.tex` aparece 2 veces (5.6 esperaba 1) porque c-136 la cita en la subseccion de medicion de intervencion. Resumen: 34 y 31 palabras en la conclusion ES/EN |
| c-133 | **PASS** | 27 comprobaciones, 0 desvios |
| c-134 | **PASS** | 23 comprobaciones, 0 desvios (`13,48` = 0, `13,52` en 07 y 08, `W = 0` = 0) |
| c-135 | **PASS** | Comprobaciones manuales: `Semanas [0-9]` = 0 en 06, `12 semanas` = 0 en 04, `junio de 2026` = 0 en 08, `entre junio y octubre de 2026` = 0 en 01, `optimiz` = 0 en 12, "tres dimensiones" = 1 en 03, "cota inferior" y "20,1 segundos" = 1 en 09, `timeout` de `tab:anexo_gemini_params` = 30 s por intento y 60 s en total, `figures/cronograma.png` existe y resuelve. Desvio ya documentado en su grupo: `label{fig:cronograma}` esta en `12-anexos.tex` (Anexo A) y no en `06-implementacion.tex` (la tarea 6.1 esperaba 1 en 06). La tarea **5.2 sigue abierta** (OQ-1) |
| c-136 | **PASS** | 15 comprobaciones; rotulos `subsec:calibracion-gate` y `subsec:medicion-intervencion` = 1 cada uno y orden 11.1, 11.2, 11.3 |
| c-137 | **PASS** | 5 comprobaciones de grep; `revision_tildes.py --check` codigo **0** y 298 pruebas de la herramienta en verde; formas diacriticas del dictamen en 0 |
| c-138 | **PASS** | 10 comprobaciones; las seis claves de calibracion y cascadas existen una vez en el `.bib` |
| c-139 | **PASS** | 25 comprobaciones; 73 entradas, 8 claves nuevas de B15 = 8; `test_verify_citations.py` 4 pruebas OK; `verify_citations.py` **PASS** (73 <-> 73) |
| c-142 | **PASS** | 7 comprobaciones; los 451 tests de `evaluation/` (incluidos los 141 de `sensibilidad_ajustes`) |

Resumen de ejecutor: 170 comprobaciones, **5 sin cumplir la expectativa literal**: las tres expectativas superadas por cambios posteriores legitimos (c-130 5.3; c-132 4.2 y 5.6) y dos artefactos del ejecutor (c-137 5.1 cuenta lineas de comentario de `main.tex`: 0 si se excluyen; c-139 2.3 espera 1, como indica su propia nota). **Ninguna FAIL de contenido; no se parcho nada ajeno.** `openspec validate <change> --strict` pasa para los doce changes (c-130..c-139, c-142 y c-141).

Suite completa del backend (`App/Backend`, imagen `eval-tests`, `GEMINI_API_KEY=test-key`): 1453 passed, 3 failed, 48 errors, 5 skipped, 1 xfailed. Los 48 errores son pruebas de integracion contra PostgreSQL (no hay base levantada en este entorno) y los 3 fallos son `test_001_seed_catalogs_no_fue_modificado`, que compara el SHA-256 de `001_seed_catalogs.py` y falla porque el arbol de trabajo tiene fin de linea CRLF (`core.autocrlf=true`). Ni las migraciones ni esos tests cambiaron desde `v1.1.1` (`git diff v1.1.1 --stat -- App/Backend/migrations` vacio): es una limitacion del entorno de verificacion, no una regresion de la familia. Los cambios de `App/Backend` desde `v1.1.1` son los de c-130 (comentarios, test de caracterizacion) y los de otros changes de la linea de Luca.

### Controles de familia (tarea 2.5)

Ejecutor: `python` sobre `paper/sections/*.tex` (reejecutable en 4.6).

- **Valores `retirado` del memo** (`9,5` como proporcion de intervencion humana, `3.700`, `42 x 88`, `45,0 h`, `13,48`, `W = 0`, `Operaciones` como sector): **0 coincidencias** en `sections/*.tex`. Las apariciones de `9,5` en los listados de control eran `95~\%` (intervalo de confianza) y `89,5` (exactitud laxa): descartadas con la expresion `(?<![0-9,.])9(,|\{,\})5(?![0-9])`.
- **`97/131`, `0,7405`, `0,6769`**: `0,6769` y `88/130` no figuran en la tesis. `97/131` y `0,7405` aparecen en 8 lugares, **todos calificados como estimacion dentro de la muestra o con remision a `subsec:sensibilidad-ajustes`**: `05-arquitectura.tex:80`, `07-resultados.tex:117` (fila de `tab:exactitud-etapa-canal`, calificada en la oracion que presenta la tabla), `:189`, `:204` y `:213` (la propia subseccion de sensibilidad), `08-discusion.tex:10` y `:56`, `09-conclusiones.tex:37`.
- **Ausencia de fuga de datos**: 0 coincidencias de "sin acceso al corpus", "sin exposicion al corpus", "datos no vistos", "separacion estricta", "held-out", "estrictamente fuera de muestra".
- **Resumen en espanol** (regla de c-106 reproducida: math en linea como una palabra, `~` como separador salvo antes de un digito): **ES 250, EN 242** (identicos a los valores registrados por c-133 y c-134); recuento plano con cada token separado: ES 258, EN 248. El espanol esta exactamente en el tope de 250: cualquier agregado exige comprimir otro pasaje.
- **Referencias cruzadas**: 263 `\ref`/`\autoref`/`\pageref` en `sections/*.tex` (214 antes del Anexo I y 49 de la Tabla 20 y su parrafo), 137 `\label` (mas el del listado `lst:validar-gemini`, declarado en `\lstlisting[label=...]`), **0 sin destino** y 0 rotulos duplicados.
- **Sectores canonicos**: 0 formas con tilde (c-137, OQ1).

### Libro mayor de paginas (tarea 2.6)

El libro mayor de la seccion G0 tiene una fila por change aplicado que modifica la tesis: base `v1.1.1`, `+c-144`, c-130, c-131, c-142, c-132, c-133, `c-134 tesis`, c-138, c-136, c-135, c-139 y c-137 (el bloque de codigo de c-134 y c-140 no tocan la tesis y no tienen fila). **No falta ninguna; no hubo que reconstruir ninguna.** La fila de c-142 (+1 / +1) esta dentro de su prevision de +1,0 a +1,4. Todas las filas se contrastaron con las previsiones declaradas: c-130 +1 (prevision +0,3 a +0,9; mas el corte de pagina), c-131 0, c-132 +1, c-133 0, c-134 0, c-136 0, c-135 0, c-138 +3 (prevision +2 a +3), c-139 +1 (+1 en la bibliografia), c-137 0. Acumulado de la familia c-130..c-137 sobre `+c-144` (102): +7 (109), dentro de +5,4 a +12,2 (central +7,7). Con el Anexo I de c-141 (tarea 3.1) el total integrado es 110: ver "Anexo I y presupuesto de paginas".

### Memo canonico (tarea 2.7)

Archivo `docs/Tesis/Correcciones/numeros-canonicos.md` (solo estructura, referencias y encabezado; **ningun valor ni estado cambio**):

- **Numeracion**: encabezados 3.1 a 3.12 unicos y consecutivos (3.7 c-130, 3.8 c-134, 3.9 c-131, 3.10 c-142, 3.11 c-132, 3.12 c-133, que es el orden de aplicacion tras el ajuste de G0.6); el item 6 de la Seccion 7 (c-144) se conserva sin renumerar. Toda remision "Seccion 3.N" del memo y de este registro resuelve a una seccion existente (las remisiones historicas a "3.7" de los design de c-131, c-133 y c-134 estan explicadas en los grupos respectivos).
- **Numeros de la familia**: `git diff -U0 v1.1.1 -- sections/` agrega 148 tokens numericos nuevos (no presentes en las lineas retiradas del mismo archivo); 123 figuran literalmente en el memo y los 25 restantes se explican asi: 17 son redondeos de la tesis a tres decimales o a un decimal porcentual de valores de cuatro decimales registrados en las secciones 3.8 a 3.10 (`0,546` de `0,5459`, `0,610` de `0,6095`, `0,670` de `0,6698`, `0,725` de `0,7246`, `0,737` de `0,7368`, `0,749` de `0,7488`, `0,808` de `0,8079`, `0,835` de `0,8346`, `0,845` de `0,8448`, `0,847` de `0,8467`, `0,870` de `0,8696`, `0,906` de `0,9059`/`0,9057`, `0,947` de `0,9468`, `53,4`, `58,0`, `83,9` y `85,0 %` de `0,5341`, `0,5799`, `0,8390` y `0,85`); 5 son valores de la literatura citados en `tab:trabajos-academicos` (`0,433`, `0,801`, `0,862`, `28.243`, `4.684`), cuya procedencia esta en `extraccion-metricas-trabajos-c-135.md` y que no son resultados de la tesis; y 3 no son resultados (`0.28` de la altura de una figura, `0.6508` del abstract con punto decimal, `1558/2001` numero de decreto). No quedo ningun numero de resultado solo en la tesis.
- **Procedencia (`archivo:linea`)**: se verificaron 90 citas de las filas del memo; las filas `vigente` cuyas lineas de `sections/*.tex` se habian desplazado por la familia se actualizaron (19 citas mas 4 ajustes manuales: `07-resultados.tex:22 -> 21`, `:55 -> :57`, `:61 -> :59`, `:129 -> :128`, `:158 -> :157`, `:190 -> :189`, entre otras; solo el numero de linea). Las filas `retirado` conservan su ubicacion historica a proposito. Las citas restantes marcadas por el verificador son diferencias de formato (`94,0 %` derivado, `65,5` en `report.md`, `19.737` como `19737.0000`).
- **Ninguna corrida de sensibilidad cambio un valor `vigente`**: las tres filas que c-142 reformulo (`97/131`, `88/130` y la fila de la etapa determinista) conservan valor y estado; ninguna de las 27 filas `vigente` de `v1.1.1` ni de las 44 anteriores a c-142 cambio de valor ni de estado.
- **Decisiones no resolubles**: la Seccion 7 conserva sus nueve puntos con su condicion de reversibilidad (punto 6, conjunto de preproduccion, c-144; punto 7, procedencia de la cache FORCE-ESCALATE, c-130; punto 8, variante por pliegues, y punto 9, version del prompt de la FORCE-ESCALATE, c-142). Los valores no derivables: nivel c del prompt (corrida paga no autorizada) figura como "no computado"; las sensibilidades E3/E4 dependen de la cache `hybrid-v2` con `corpus_hash` distinto (decision confirmada por el autor el 2026-10-26: se acepta; si se rechazara pasan a "no computable").
- **Encabezado**: titulo "version de trabajo v10, release prevista `v1.2.0`"; nueva vineta "Consolidacion c-141" con la fecha de consolidacion 2026-10-26; conserva el SHA-256 del corpus `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`.

### Reportes de evaluacion (tarea 2.8)

- `evaluation/report.md` conserva sus secciones: Etapas del pipeline, Exactitud, Matriz de Confusion, Metricas por sector, Metricas de conjunto, **Exactitud por etapa** y **por canal** y **Calibracion de la confianza** (c-131), **Tiempos** con Normalidad (Shapiro-Wilk), Prueba de Wilcoxon, Reduccion de tiempos, Desglose por canal (y, de c-134, Descriptivos, Contraste direccional y Escenarios de sensibilidad del redondeo). Los valores canonicos coinciden con el memo (`0.7350`, `0.5207`, `0.6654`, `0.3586`, `61.5850`, `17.7606`, `71.16`, `W = 363`, `T+ = 19737`, `r = 0.9639`, `0.7405`, `0.7246`); los valores de cuatro decimales de `report.md` que el memo no registra son descriptivos que la tesis no cita.
- `evaluation/report_sensibilidad_ajustes.md` existe (98 lineas); sus 32 valores de cuatro decimales figuran en el memo (3.10) salvo constantes de diseno (`0.2000`, `0.3000`, `0.5000`). Declara el nivel c "no computado; requiere autorizacion explicita y no se ejecuto".
- **Sin invocaciones pagas**: la ablacion del prompt (G0.7a) no esta autorizada y `report_sensibilidad_ajustes.md` no registra corrida paga; ninguna tarea de este tramo invoco a Gemini.
- `report.md` y las caches oficiales no fueron modificados por c-142 (`git show --stat 59b9967 -- evaluation/report.md evaluation/evidence` vacio; `git log -- evaluation/report.md` solo muestra c-134 codigo, c-131 y el versionado inicial).
- Huella del corpus: `git show HEAD:data/corpus_evaluacion_pseudonimizado.json | sha256sum` = `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` (coincide con la esperada). Las copias vivas `evaluation/predicciones*.json` siguen ignoradas (`.gitignore:72`) y son copias locales de las evidencias versionadas de c-143.

### Anexo I y presupuesto de paginas (tareas 3.1 y 3.2)

- **3.1**: `12-anexos.tex`, `sec:anexo-trazabilidad`: se conserva el parrafo que remite a `docs/Tesis/Correcciones/dictamen-correcciones.md`; se agrega la identificacion del dictamen (22 de octubre de 2026, version de trabajo v10 publicada como `v1.1.0`, aplicable a `v1.1.1`) y la **Tabla 20** (`tab:anexo-trazabilidad`, `\small`, 18 filas, columnas Rec., Change y Secciones de la tesis con `\autoref`) para A1 a A5 y B4 a B16 (A4, A5, B7, B13 y B16 con los changes de cada parte). Sin numeros de linea de las fuentes. Los 48 `\autoref` de la tabla resuelven (0 referencias indefinidas tras compilar). Nota: el parrafo de la ruta del registro ya producia un `Overfull \hbox` de 67 pt (la ruta en `\texttt` no se parte) en `v1.1.1`/c-137; no se toco.
- **3.2**: compilacion en el entorno de registro (Docker `texlive-thesis`, `latexmk main.tex`, en el arbol): `abspage@last{110}`; `main.toc`: `Anexos` en p. 102 (cuerpo sin anexos 101, anexos 9). Fila **"integrado (pre-compactacion)"** agregada al libro mayor de la seccion G0. **Brecha frente a la rama (a)** (total <= 101): **+9 paginas**. **Margen de la regla (b)** (cuerpo <= 100): **-1** (cuerpo 101). Sin compactar nada.
- El Anexo I costo +1 pagina de total (110 frente a 109; prevision de D10: +0,1 a +0,6): la pagina 109 estaba llena con el final del Anexo H y el Anexo I, por lo que ni la tabla ni un parrafo de enumeracion caben sin abrir una pagina; la tabla queda en la p. 110 con las dos ultimas lineas del parrafo nuevo. Crece fuera del cuerpo (regla (b)).

**Palancas de D5 para el checkpoint HIGH** (sin aplicar; ahorros estimados de D5 y de los grupos de los changes, a confirmar sobre el PDF):

| Palanca | Ahorro estimado (paginas) | Clase | Nota sobre el PDF integrado |
|---|---|---|---|
| P1 Redundancia introducida por la familia (gate y procedencia de los ajustes repetidos; una explicacion y remisiones `\autoref`) | 0,5 a 1,0 | Forma | Candidatos: `05:80`, `07:157`, `08:16-20`, `09:37` repiten la regla por etapa y la procedencia |
| P2 Leyendas de tablas y figuras nuevas | 0,2 a 0,4 | Forma | `tab:exactitud-etapa-canal`, `tab:sensibilidad-ajustes`, `tab:balance-neto`, `tab:tiempos-canal`, Tabla 20 |
| P3 Tablas nuevas con la densidad de las existentes | 0,3 a 0,5 | Forma | |
| P4 Espaciado de flotantes y listas | 0,3 a 0,5 | Forma (preambulo) | |
| P5 Anexos H e I compactos | 0,3 a 0,5 | Forma | La p. 110 contiene solo la Tabla 20 y dos lineas del parrafo nuevo: una enumeracion en parrafo mas compacta o acortar la prosa del Anexo I podria devolver esa pagina al total (no al cuerpo); a confirmar |
| P6 Indices de tablas y de figuras en una misma pagina | 0,5 a 1,0 | Formato: requiere aprobacion | |
| P7 Bibliografia en `\small` o `\bibitemsep` reducido | 0,8 a 1,2 | Formato: requiere aprobacion | La ultima pagina de Referencias (p. 101) tiene 14 lineas: por si sola cierra el -1 de la regla (b) |
| P8 Interlineado del cuerpo de 2 a 1,5 | del orden de 10 a 14 | Formato de la catedra: requiere aprobacion explicita | Unico que cierra la brecha de +9 de la rama (a) |

Lectura: las palancas de forma P1-P5 rinden 1,6 a 2,9 y con P6 y P7, 2,9 a 5,1; **no cierran la brecha de +9 de la rama (a)** (total <= 101); solo la cierra P8 o recortar contenido de la familia. Bajo la **regla (b)** (cuerpo <= 100) basta recuperar **1 pagina del cuerpo**: P7 sola (0,8 a 1,2) o P1 mas P2; alternativas locales: la ultima pagina de Discusion (p. 85) tiene 13 lineas y la de Implementacion (p. 61) 21, de modo que compactar esas lineas en sus capitulos devuelve una pagina sin tocar el preambulo. Ultima pagina de cada capitulo (lineas no vacias de `pdftotext -layout`): 1: 31, 2: 33, 3: 35, 4: 26, 5: 31, 6: 21, 7: 41, 8: 36, 9: 13, 10: 32, 11: 32, Referencias: 14.

### Compactacion P7 (tareas 3.3 a 3.6) - 2026-10-26

Decision del usuario registrada en G0.1 (regla (b), P7 aprobada). Se aplico **solo P7**, de forma minima y reversible; no se tocaron margenes, interlineado del cuerpo (P8), indices (P6) ni contenido.

- **Lineas agregadas** (dos, un comentario y un comando) en `docs/Tesis/v10 (IA)/paper/preambles/preamble.tex`, justo despues de `\addbibresource{../Bibliography_base.bib}` (lineas 104 y 105):

  ```
  % Bibliografia compacta (c-141, palanca P7): cuerpo de letra \small solo en la lista de referencias
  \renewcommand*{\bibfont}{\normalfont\small}
  ```
- **`\bibitemsep` no se agrego**: el estilo `biblatex-apa` ya fija `\setlength{\bibitemsep}{0pt}` (`apa.bbx`, linea 2242, TeX Live 2026 de la imagen `texlive-thesis`), de modo que reducirlo no ahorra nada; la separacion entre entradas viene del interlineado doble y de la sangria francesa. Por eso la unica palanca efectiva es `\bibfont` en `\small`. Reversible: borrar esas dos lineas del preambulo.
- **Medicion antes y despues** (Docker `texlive-thesis`, `latexmk main.tex`, en el arbol; `abspage@last` de `main.aux` y `main.toc`; el conteo de saltos de pagina de `pdftotext -enc UTF-8 main.pdf -` coincide):

  | Estado | Total | Cuerpo sin anexos | Anexos | `Referencias bibliograficas` (pagina) | `Anexos` (pagina) |
  |---|---|---|---|---|---|
  | Antes (integrado, pre-compactacion) | 110 | 101 | 9 | 94 | 102 |
  | Despues (con `\bibfont` `\small`) | **109** | **100** | **9** | 94 | 101 |
  | Ahorro | -1 | -1 | 0 | 0 | -1 |

  La bibliografia pasa de 8 paginas (94 a 101, la ultima con 14 lineas) a 7 (94 a 100); la ultima, p. 100, queda con una sola entrada (Zhao et al., 3 lineas) y unas 34 lineas libres, es decir, el ahorro real es de unas 1,4 paginas y el margen de la regla (b) queda en 0 con holgura local en esa pagina.
- **3.3**: regla (b) cumplida: total **109**, cuerpo sin anexos **100** (`\contentsline {section}{Anexos}{101}` menos 1). Fuente: decision del equipo, confirmada el 2026-10-26 (G0.1); no consta exigencia de la catedra.
- **3.4 y 3.5**: no aplica (regla (b) confirmada el 2026-10-26); no hubo recortes de contenido ni bloques de compactacion de la rama (a).
- **3.6**: tope final verificado con la regla vigente: cuerpo 100 <= 100. La portada ocupa exactamente una pagina (la p. 2 es el resumen; `pdftotext -f 1 -l 1` termina en la fecha de la portada).
- **Verificaciones tras P7**: `grep -c "^!" main.log` = 0; `grep -i undefined main.log` vacio; `grep -c "multiply defined" main.log` = 0; `grep -E "WARN|ERROR" main.blg` vacio; "Found 73 citekeys" = 73 entradas; `verify_citations.py` STATUS: PASS; `??` en el texto del PDF = 0. Solo se recompusieron `main.pdf`, `main.xdv`, `main.aux`, `main.toc`, `main.lof`, `main.lot` y `main.fdb_latexmk`; `main.bbl`, `main.blg` y `main.bcf` quedaron sin cambios.
- **Brecha actualizada**: bajo la regla (b) el margen es **0** (>= 0, cumple); antes era -1. La brecha de la rama (a) (+8) ya no rige. Para C1 (tarea 5.1, cambio de version en el Anexo B y en el `.bib`) no se esperan paginas adicionales; el margen 0 deja solo la holgura de la p. 100 (bibliografia); cualquier crecimiento del cuerpo anterior a la bibliografia exige compensar.

### Archivo de la familia (tarea 2.9) - 2026-10-26

Alcance fijado por el usuario: archivar **solo** los changes con todas las tareas `[x]`. Verificado antes con `openspec list --json` (N/N): c-130 37/37, c-131 81/81, c-132 29/29, c-133 42/42, c-134 47/47, c-136 24/24, c-137 41/41, c-138 30/30, c-139 46/46, c-142 91/91. Orden de archivo (el de aplicacion de D1, para que los deltas sobre un mismo spec se sincronicen en ese orden): c-130, c-134, c-131, c-142, c-132, c-133, c-138, c-136, c-139, c-137; comando `openspec archive <change> -y` (sin `--skip-specs`).

| Change | Carpeta en `openspec/changes/archive/` | Deltas sincronizados |
|---|---|---|
| c-130 | `2026-10-26-c-130-gate-revision-humana-por-etapa` | +9 ~3 |
| c-131 | `2026-10-26-c-131-metricas-por-etapa-canal-y-exactitud-laxa` | +12 ~3 |
| c-132 | `2026-10-26-c-132-balance-neto-derivaciones-erroneas` | +6 |
| c-133 | `2026-10-26-c-133-hipotesis-objetivos-metrica-primaria` | +7 ~5 |
| c-134 | `2026-10-26-c-134-contrastes-estadisticos-y-desagregado-canal` | +11 |
| c-136 | `2026-10-26-c-136-recomendaciones-lineas-faltantes` | +8 |
| c-137 | `2026-10-26-c-137-revision-ortotipografica` | +9 ~1 |
| c-138 | `2026-10-26-c-138-estado-del-arte-calibracion-y-cascadas` | +7 |
| c-139 | `2026-10-26-c-139-correspondencia-texto-fuente-y-metadatos` | +9 ~4 |
| c-142 | `2026-10-26-c-142-sensibilidad-fuera-de-muestra-ajustes-clasificador` | +9 |

Specs sincronizados: `classification-resilience`, `incident-visibility`, `project-documentation`, `evaluation-framework`, `evaluation-prediction-cache`, `tesis-document` y `tesis-numeros-canonicos`. Ningun conflicto de merge de deltas. `openspec validate --specs --strict --no-interactive`: **64 de 64 pasan, 0 fallan** (linea base del 2026-10-22: 63 de 63; el spec extra proviene de un change posterior a esa linea base). `ls openspec/changes/archive/ | grep -c "2026-10-26-c-1"` = 10; `openspec list --json` ya no devuelve ninguno de los diez.

**Quedan activos** (no archivados, por instruccion del usuario):

- **c-135** (`c-135-cronologia-y-consistencia-redaccional`, 34/35): su tarea 5.2 sigue abierta a la espera de las fechas de las seis iteraciones Scrumban de los autores (sin fuente primaria; OQ-1 PROVISIONAL).
- **c-140** (`c-140-endurecimiento-tecnico-tls-reintentos-e2e`, 0/73): el usuario todavia no decidio incluirlo o archivarlo como NO REALIZADO (`--skip-specs`, precedente c-67).
- **c-141** (este change): se archiva en su propia fase archive, despues de la release.

Con esto, la tarea 2.9 queda **parcialmente cumplida**: faltan c-135 y c-140; `openspec list --json` todavia devuelve c-135 y c-140, de modo que la verificacion final "no devuelve changes c-130..c-140 ni c-142" se completa cuando el usuario decida sobre ambos (tramo de release, 9.2).

### Pasada ortotipografica corta (tarea 4.1)

Commit de apply de c-137: `492f56c` (merge `b3c6f0f`). `git diff 492f56c..HEAD -- "docs/Tesis/v10 (IA)/paper/sections/"` esta **vacio**; el unico texto de prosa modificado despues de c-137 es el del Anexo I de este tramo (`git diff 492f56c -- sections/` = 36 lineas agregadas en `12-anexos.tex`). Verificaciones de c-137 sobre ese texto: `revision_tildes.py --check` codigo **0**; ninguna ocurrencia de los pares `hacia`/`hacia`, `formula`, `continua`, `esta`/`este`, `si`/`aun`/`solo` ni de las palabras enumeradas por el dictamen (`erronea`, `heterogeneos`, `multiples`, `inequivocos`, `antiguedad`, `perimetro`, `enganosa`, `escaner`, `decada`, `alla`, `guian`, `envian`, `demas`) en las lineas agregadas; se revisaron a mano. No se reaplicaron `acentuar_tesis.py` ni `acentuar_tesis_v9.py`.

### Compilacion de verificacion (tareas 4.2 a 4.6) - arbol integrado pre-compactacion

- **Entorno**: Docker `texlive-thesis` (XeTeX 3.141592653-2.6-0.999998, TeX Live 2026; biber 2.22). **Comando**: `MSYS_NO_PATHCONV=1 docker run --rm -v "<repo>/docs/Tesis/v10 (IA):/work" -w /work/paper texlive-thesis latexmk main.tex`.
- **Paginas**: `abspage@last{110}`; `Anexos` en p. 102: cuerpo 101, anexos 9. `pdftotext` cuenta 110 saltos de pagina; la portada ocupa una pagina.
- **Log** (`main.log`, no versionado): errores fatales (`grep -c "^!"`) **0**; referencias o citas indefinidas **0**; `multiply defined` **0**; `Overfull \hbox`: 31 avisos, **22 mayores de 10 pt** (todos preexistentes: celdas de `Courier New` de las tablas de arquitectura y rutas de la API, el comando `pytest --cov` de 04 y 06, parrafos con rutas y literales de los Anexos B, F, H e I y dos filas de la tabla del capitulo 7; ninguno en `tab:anexo-trazabilidad`; 31 avisos = los 31 de c-137). Sin avisos de `fancyhdr`.
- **biber**: `main.blg` sin `WARN` ni `ERROR`; "Found 73 citekeys" = 73 entradas de `Bibliography_base.bib`; `verify_citations.py` **STATUS: PASS** (73 entradas <-> 73 claves, 126 comandos de cita, 0 huerfanas, 0 sin usar).
- **Figuras y texto**: los 12 `\includegraphics` de `sections/*.tex` resuelven contra `\graphicspath` (`figures/`, `./`, `assets/`), incluida `figures/cronograma.png`; `pdftotext -enc UTF-8 main.pdf - | grep -c "??"` = **0**.
- **4.6**: los controles de familia (tarea 2.5) se repitieron sobre este arbol final del tramo (mismo ejecutor, resultados de la seccion anterior) y el conteo se contrasta con el tope en "Anexo I y presupuesto de paginas": 110 / 101 / 9, sin tope cumplido (3.6 no ejecutada: depende del checkpoint HIGH).
  - **Actualizacion 2026-10-26**: tras P7 el conteo es 109 / 100 / 9 y el tope de 3.6 (regla (b), cuerpo <= 100) **se cumple** con margen 0; los controles de la tarea 2.5 no dependen de la tipografia de la bibliografia y no se alteraron (el texto de las secciones no cambio).

### Contenido de C1 y compilacion de registro (tareas 5.1 a 5.3) - 2026-10-26

- **5.1 Contenido de C1** (patron de `4160d84`): en `sec:anexo-repositorio` de `12-anexos.tex` el tag `v1.1.1` pasa a `v1.2.0` y se retira la linea del hash de `v1.1.1` (con su linea en blanco); en `Bibliography_base.bib`, `Gomez2026_repositorio` cambia solo el numero de version del titulo, `1.1.1` -> `1.2.0`, conservando la etiqueta acentuada `Versi{\'o}n` que dejo c-137, y su `urldate` pasa de 2026-10-25 a 2026-10-26 (consigna de c-139). Verificaciones: `grep -c "v1.2.0" sections/12-anexos.tex` = 1; `grep -c "4160d84286623b073d2904353e6f9163ae211de7" sections/12-anexos.tex` = 0; la linea `title` de `Gomez2026_repositorio` termina en `1.2.0)}`; `grep -c "1.1.1)\|1.0.0)"` sobre el `.bib` = 0. Queda en `12-anexos.tex:152` la mencion historica de `v1.1.0` y `v1.1.1` del Anexo I (el dictamen se emitio sobre `v1.1.0`, aplicable por igual a `v1.1.1`); no se toca.
- **5.2 Compilacion de registro**: `latexmk main.tex` en el arbol (artefactos versionados incluido `main.bbl`, que cambia por el titulo y el `urlday`). Fila "release v1.2.0 (C1)" agregada al libro mayor: **109 / 100 / 9**.
- **5.3 Evidencia de compilacion (D6)** - los datos son:
  1. **Entorno y versiones**: Docker `texlive-thesis` (XeTeX 3.141592653-2.6-0.999998, TeX Live 2026; biber 2.22), el mismo de G0.2.
  2. **Comando**: `MSYS_NO_PATHCONV=1 docker run --rm -v "<repo>/docs/Tesis/v10 (IA):/work" -w /work/paper texlive-thesis latexmk main.tex`.
  3. **Paginas**: `abspage@last{109}`; `\contentsline {section}{Anexos}{101}` en `main.toc` => cuerpo sin anexos 100, anexos 9; `Referencias bibliograficas` en p. 94; `pdftotext -enc UTF-8 main.pdf -` cuenta 109 saltos de pagina; la portada ocupa una pagina (la p. 1 termina en la fecha 26 de octubre de 2026). Tope de 3.6: cuerpo 100 <= 100, margen 0.
  4. **Errores fatales** (`grep -c "^!" main.log`): 0.
  5. **Referencias o citas indefinidas** (`grep -i undefined main.log`): ninguna.
  6. **Etiquetas duplicadas** (`grep -c "multiply defined" main.log`): 0.
  7. **`Overfull \hbox`**: 30 avisos (31 en la compilacion previa a C1), **22 mayores de 10 pt**, igual que en 4.3: celdas de `Courier New` de las tablas de arquitectura y rutas de la API, el comando `pytest --cov`, parrafos con rutas y literales de los Anexos B, F, H e I y dos filas de la tabla del capitulo 7; no bloqueantes, sin texto visible fuera de margen. La entrada de la subseccion H.1 de `main.toc` pasa de la p. 106 a la p. 105: el numero habia quedado desfasado en el `main.toc` versionado con el commit de P7 y esta compilacion lo corrige.
  8. **biber**: `main.blg` sin `WARN` ni `ERROR`; "Found 73 citekeys" = `grep -c "^@" Bibliography_base.bib` = 73.
  9. **`verify_citations.py`**: `STATUS: PASS` (73 entradas, 73 claves citadas, 126 comandos de cita, 0 huerfanas, 0 sin usar).
  10. **`??` en el texto del PDF** (`pdftotext -enc UTF-8 main.pdf - | grep -c "??"`): 0. Los 12 `\includegraphics` de `sections/*.tex` resuelven. (Diez entradas numeradas: estan todos los datos que piden D6 y la tarea 5.3.)
- `revision_tildes.py --check`: codigo 0 sobre el arbol final.

### Cierre del libro mayor (tarea 6.4)

Resumen de la FASE 36 (todas las cifras en paginas: total / cuerpo sin anexos / anexos):

| Etapa | Total | Cuerpo | Anexos | Delta total | Delta cuerpo |
|---|---|---|---|---|---|
| Linea base `v1.1.1` | 101 | 93 | 8 | - | - |
| `+c-144` (main, previo a la familia) | 102 | 94 | 8 | +1 | +1 |
| Familia c-130..c-139 (c-130 +1, c-132 +1, c-138 +3, c-139 +1, c-142 +1; c-131, c-133, c-134, c-135, c-136 y c-137 con 0) | 109 | 101 | 8 | +7 | +7 |
| Anexo I de c-141 (tarea 3.1) | 110 | 101 | 9 | +1 | 0 |
| Compactacion P7 (`\bibfont` `\small`, tareas 3.3 a 3.6) | 109 | 100 | 9 | -1 | -1 |
| **release v1.2.0 (C1)** | **109** | **100** | **9** | 0 | 0 |

- **Acumulado frente a `v1.1.1`**: +8 total (101 -> 109), +7 cuerpo (93 -> 100), +1 anexos (8 -> 9); +1 de `+c-144`, +7 de la familia, +1 del Anexo I y -1 de P7.
- **Previsiones declaradas**: la familia (+7 sobre 102) queda dentro de +5,4 a +12,2 (central +7,7); c-142 +1 dentro de +1,0 a +1,4; c-141 (Anexo I) +1 total / 0 cuerpo frente a +0,1 a +0,6 (cuantizado a una pagina).
- **Compactacion aplicada**: solo P7 (rama (b), regla confirmada el 2026-10-26: cuerpo sin anexos <= 100, anexos sin limite); sin recortes de contenido, sin P6 ni P8.
- **Conteo final de C1**: 109 / 100 / 9; margen de la regla (b) = 0 (cumple). **Coincide con el conteo de la tarea 5.2** (misma compilacion). Cualquier crecimiento del cuerpo anterior a la bibliografia exige compensar; el crecimiento de anexos no afecta la regla.

### Renders y base de conocimiento (tareas 7.1 a 7.7) - 2026-10-26

- **7.1 `build_tesis_para_agente.py`** (D8, TDD estricto, prueba co-ubicada `docs/Tesis/v10 (IA)/test_build_tesis_para_agente.py`): **RED**: 12 pruebas fallan antes de tocar el script (sin `leer_inputs`, `verificar_orden` ni `construir_encabezado`; el script no corre sin la release ni fuera de la raiz). **GREEN**: la release pasa a ser argumento obligatorio (sin argumento o con mas de uno: codigo 2, mensaje en stderr y nada en stdout), el encabezado declara la release recibida, `ORDER` se compara con los `\input{sections/...}` de `main.tex` (ignora comentarios y fin de linea CRLF) y el script termina con codigo 1 si difieren; las rutas pasan a ser relativas al script (corre desde cualquier carpeta). **TRIANGULATE**: dos releases (`v1.2.0`, `v9.9.9`), orden alterado, seccion faltante y sobrante en un `main.tex` temporal, `main.tex` con CRLF, dos argumentos, `main()` con orden alterado devuelve 1 sin escribir (esta ultima fallo antes de pasar `MAIN_TEX` explicitamente a `verificar_orden`). **REFACTOR**: `renderizar_cuerpo()` extraida y `verificar_orden` sin valor por defecto ligado en la definicion. Total: **15 pruebas en verde** (317 en `docs/Tesis/v10 (IA)/` con las de `revision_tildes` y `verify_citations`). Se retiraron `FALLBACK_RELEASE` y `detect_release()` (el script ya no contiene ninguna release cableada; `grep -c "v1.1.0"` = 0 y tampoco `v1.1.1`). Regresion: con `v1.1.1` el script produce, byte a byte, la misma salida que antes del cambio.
- **7.2 Regeneracion del render**: `python "docs/Tesis/v10 (IA)/build_tesis_para_agente.py" v1.2.0 > "docs/Tesis/v10 (IA)/tesis_para_agente.md"` (Docker `eval-tests`, desde la raiz). Encabezado `(v10 / v1.2.0)`; el Anexo B del render contiene `v1.2.0`; dos corridas seguidas: **SHA-256 `0b8e763326be461400fe493e2bd98f526c91250b57f2de3a3fc9abd5cc3bd8cf`** (salida LF, UTF-8). El archivo del checkout se normalizo a CRLF como el resto (`core.autocrlf=true`): SHA-256 del archivo de trabajo `d83189da6f885377042f1512ecd50d2cdee9f2aaa6d53e85daf9d0e99a02f4c5`; el contenido versionado es el LF.
- **7.3 Textos extraidos**, desde el `main.pdf` de 5.2: `pdftotext -enc UTF-8 main.pdf "../tesis_para_evaluacion.txt"` y el mismo texto con espacios colapsados (`tr -s '[:space:]' ' '`) en `../tesis_completa_extraida.txt`. Verificado: texto acentuado, la portada con "Prof. Alberto Cortez y Prof. Ariel Enferrel" en ambos y 109 saltos de pagina (`\f`) en `tesis_para_evaluacion.txt`, igual a las paginas del PDF.
- **7.4 `paper/tesis.docx` (OQ5)**: **no hay pandoc** en el host (`which pandoc` vacio). Se declara **render legado no regenerado para `v1.2.0`** `docs/Tesis/v10 (IA)/paper/tesis.docx`, junto con las dos fuentes legadas de la raiz de v10 (`1_Tesis_Mesa_Ayuda_UTN_COMPLETA.docx` y `1_Tesis_Mesa_Ayuda_UTN_FINAL_MEJORADA_ESQUELETO.docx`); la version autoritativa es `paper/main.pdf`. Ningun puntero activo los presenta como vigentes: `openspec/config.yaml`, `knowledge-base/README.md` y `CLAUDE.md` no los mencionan (solo `add_disclaimer.py` los referencia como herramienta).
- **7.5 Puntero `thesis:` de `openspec/config.yaml`** (linea 48): `docs/Tesis/v10 (IA)/tesis_para_agente.md`; `test -f` verdadero; la ruta no cambio, no se repunta.
- **7.6 `knowledge-base/11_evaluacion_experimental.md`** (D9): bloque "Resultados vigentes (release v1.2.0)" con los valores `vigente` del memo (Secciones 3.1 a 3.12, incluida la sensibilidad de c-142 y el balance neto `condicional`), con el memo como fuente unica; la linea "Anti data-leakage" se reemplazo por la procedencia real de los ajustes (c-71, c-72 y c-74 con el corpus de evaluacion) y la remision a `subsec:sensibilidad-ajustes` y a la Seccion 3.10; las afirmaciones de recalculo pendiente (valores esperados, tipologia de errores y baseline) pasaron al estado vigente que declara la tesis; las cifras del corpus sintetico quedan solo como historia rotulada como superada. `grep -n -i "re-mid\|se recalcula\|se re-calcula\|al re-ejecutar\|held-out\|SIN acceso"` sobre ese archivo: sin resultados. Sin ningun numero que no este en el memo.
- **7.7 `knowledge-base/README.md`** (D9): ruta del render `docs/Tesis/v10 (IA)/tesis_para_agente.md`; modelo `gemini-3.6-flash`; resumen ejecutivo con los resultados vigentes y la viabilidad tecnica y economica confirmada con la operativa condicional (balance neto indeterminado), como la dejo c-132; la fila del indice de `11_...` actualizada. `grep` sin `docs/Tesis/tesis_para_agente.md` ni "Gemini 2.5 Flash" en el README. Ningun archivo de `knowledge-base/` presenta como vigente un valor `retirado` ni afirma ausencia de fuga de datos. Residuales **fuera del alcance de D9** (solo se declaran): `01_vision_y_objetivos.md`, `02_descripcion_general.md`, `05_reglas_de_negocio.md` y `09_decisiones_y_supuestos.md` siguen diciendo "Gemini 2.5 Flash" (arquitectura y decision DD-04 historicas); `01_vision_y_objetivos.md:46` conserva el `9,5 %` dentro de la tabla que se rotula "superado - corpus sintetico" y "a re-medir", es decir, como historia y no como valor vigente.

### Verificacion previa al tag (tarea 8.1) - 2026-10-26

- `git tag -l v1.2.0`: vacio. `git ls-remote --tags origin v1.2.0`: vacio.
- Tags previos en sus commits: `v1.0.0` = `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`; `v1.0.1` = `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`; `v1.1.0` = `7103b649d8c4f51737ad6ad4095dad22c9406400`; `v1.1.1` = `4160d84286623b073d2904353e6f9163ae211de7` (los cuatro coinciden con `tasks.md`).
- `git fetch origin` y `git merge-base --is-ancestor origin/main HEAD`: verdadero (`origin/main` = `11e969c5919e56ca65bf10ca8e9c5bc4e43e19ac`). No hizo falta repetir 2.3 ni los grupos 4 y 5. Repetir el fetch inmediatamente antes de crear el tag.
- 8.3 (prueba de humo de c-140): no aplicable, c-140 no se aplico (excluido provisionalmente; decision del usuario pendiente).

### Release v1.2.0 - C2 y cierre documental (tareas 8.6, 8.7, 9.1 y 9.2) - 2026-10-26

- **8.6 Preparacion de C2** (patron de `e18b9c4`): en `sec:anexo-repositorio` de `12-anexos.tex`, despues de la oracion del tag, se agrego la linea con el hash completo de `git rev-parse v1.2.0^{commit}` con la redaccion de la linea de `v1.1.1` ("El hash completo de ese commit es ..., que constituye la referencia verificable de la version corregida."); el hash va en `\texttt{\small ...}` porque en `\texttt{}` al cuerpo normal desbordaba el margen 17,8 pt (un `Overfull \hbox` nuevo, 23 mayores de 10 pt) y con `\small` cabe (22, igual que en C1). La nota "Trazabilidad `v1.2.0` (c-141, 2026-10-26)" quedo en "## Notas" de este registro con tag, hash y alcance (FASE 36: A1-A5 y B4-B16; c-140 no aplicado, sin prueba de humo). Verificado: el hash de 40 caracteres (`a49d035c67b32ae17e633ec04b09ecdd2781aac6`) aparece **una vez** en `12-anexos.tex` y **una vez** en la nota de "## Notas"; `git cat-file -t v1.2.0` = `tag`, `git rev-parse v1.2.0^{commit}` = ese hash y `git ls-remote --tags origin v1.2.0` devuelve el tag y su linea `^{}` apuntando al mismo commit.
- **8.7 Recompilacion** (Docker `texlive-thesis`, `latexmk main.tex`, mismo entorno que 5.2): `abspage@last{109}`; `Anexos` en p. 101 => cuerpo 100, anexos 9 (tope de 3.6 cumplido, margen 0); `grep -c "^!" main.log` = 0; `grep -i undefined main.log` vacio; `multiply defined` = 0; 30 `Overfull \hbox`, 22 mayores de 10 pt (igual que en C1); `main.blg` sin `WARN` ni `ERROR`, "Found 73 citekeys"; `main.bbl` sin cambios; `pdftotext -enc UTF-8 main.pdf - | grep -c "??"` = 0; `verify_citations.py` `STATUS: PASS`; `revision_tildes.py --check` codigo 0. El texto del PDF contiene el hash (p. 102).
- **Renders de C2**: `tesis_para_agente.md` regenerado con `build_tesis_para_agente.py v1.2.0` (dos corridas, mismo SHA-256 de la salida LF `0a5c0d3d4c116312e4e186e83bf00de7c8e64df7242ac5bc57c9be68c3944c9f`; normalizado a CRLF en el checkout) y contiene el hash una vez; `tesis_para_evaluacion.txt` (109 saltos de pagina) y `tesis_completa_extraida.txt` regenerados con `pdftotext` desde el `main.pdf` de C2 y contienen el hash. La portada conserva "Prof. Alberto Cortez y Prof. Ariel Enferrel".
- **Matriz de trazabilidad tras C2**: la linea del hash desplaza dos lineas la fila A5a (`12-anexos.tex:142` -> `:144`); se corrio `verificar_matriz_trazabilidad.py --reubicar` ("Filas: 41; fallas: 0") y la matriz queda calculada sobre el arbol de C2, que es la punta de la release. El tag `v1.2.0` apunta a C1, de modo que `--rev v1.2.0` da 40 aciertos y una falla esperada (A5a, 2 lineas de desfase); desde el commit C2 la verificacion sin `--rev` (o con `--rev` del commit C2) da 0 fallas.
- **9.1 `CHANGES.md`**: FASE 36 con C-130, C-131, C-132, C-133, C-134, C-136, C-137, C-138, C-139 y C-142 como ARCHIVADO (2026-10-26, N/N), C-141 APLICADO, C-135 ACTIVO (34/35) y C-140 ACTIVO (0/73, excluido provisionalmente); nota fechada en "Notas del analisis" (release `v1.2.0`, hash, 109 paginas con cuerpo 100 y anexos 9, regla del tope); lineas Total y Fases y "Primer change recomendado" con 3 activos, C-01..C-144 y la release vigente `v1.2.0`.
- **9.2 Verificacion final**: `openspec validate c-141-integracion-release-v1-2-0 --strict` valido; `openspec list --json` muestra solo c-141, c-135 y c-140; tags previos intactos (`v1.0.0` = `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` = `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` = `7103b649d8c4f51737ad6ad4095dad22c9406400`, `v1.1.1` = `4160d84286623b073d2904353e6f9163ae211de7`). **Por que siguen activos**: c-135 (34/35) tiene abierta la tarea 5.2, que espera las fechas reales de las iteraciones de los autores; c-140 (0/73) esta excluido provisionalmente de la integracion y espera la decision del usuario (incluirlo en una release posterior o archivarlo como NO REALIZADO con `--skip-specs`, precedente c-67); c-141 sigue activo hasta su fase archive.
- **Pasos siguientes** (en este orden): (1) actualizar el titulo y la descripcion del PR #40 `ramagonzalo` -> `main` (tag `v1.2.0`, hash, numeracion c-130..c-144, merge commit); (2) cerrar c-135 (fechas de los autores) y resolver c-140 (incluir o NO REALIZADO) y entonces la tarea 2.9; (3) archivar c-141 (fase archive: `CHANGES.md` pasa de APLICADO a ARCHIVADO); (4) mergear el PR #40 con **merge commit** (nunca squash ni rebase, que dejarian C1 fuera de la historia de `main`); (5) verificar `git merge-base --is-ancestor v1.2.0 origin/main` (debe ser verdadero) tras `git fetch origin`.

### Pendientes y verificaciones diferidas

- Repetir 2.3 (fetch y ancestro) antes de C1 (8.1 lo repitio el 2026-10-26); repetir 4.2-4.6 tras cualquier compactacion o edicion de la tesis; la matriz de trazabilidad se recalculo tras el contenido de C1 (0 fallas); resuelto el 2026-10-26 en C2: reubicada sobre el arbol de C2 (0 fallas; `--rev v1.2.0`, que lee C1, da una falla esperada en A5a).
- `CLAUDE.md` (linea 51) y `openspec/config.yaml` (linea 34): alinear el timeout de la inferencia (30 s por intento y 60 s en total) con confirmacion del usuario; ademas dicen "Gemini 2.5 Flash" (la tesis usa `gemini-3.6-flash`), fuera del alcance declarado de c-141.
- `CHANGES.md` ("Pendientes planificados", punto 2) sigue diciendo que la seccion de normalidad del reporte es manual: obsoleto desde c-99 (tarea 9.1).
- Resuelto en el tramo B (2026-10-26): `knowledge-base/11_evaluacion_experimental.md` y `README.md` (7.6 y 7.7) y los renders (7.1 a 7.3) reflejan el Anexo I y el contenido de C1. Para C2 hay que volver a generar el render y los textos extraidos (8.7).
- El primer item del alcance excluido de `01-introduccion.tex:74` (integracion con inventario de activos y gestion de configuracion) remite a `sec:recomendaciones` y el capitulo no tiene una subseccion para ese tema (hallazgo heredado de c-136 y c-135): decidir si se agrega una linea o se acota la remision.
- Suite completa del backend: 3 fallos y 48 errores de entorno (ver 2.4); no son de la familia.

### Confirmacion de las Open Questions de la FASE 36 (2026-10-26)

El autor reviso las decisiones que habian quedado PROVISIONALES en los grupos c-130, c-132, c-133, c-134, c-136, c-137, c-138, c-139 y c-135. Se confirman 29 y se declara superada 1 (c-130 OQ4, por el bloque G de c-145). Las decisiones ya confirmadas antes (c-130 OQ2, c-134 OQ1, c-134 OQ2, FORCE-ESCALATE de c-142 y c-135 OQ-1) figuran en sus grupos.

| Change | OQ | Decision confirmada |
|---|---|---|
| c-130 | OQ3 | Comentarios y test en `App/Backend`: si, bloque 7 aplicado. |
| c-130 | OQ4 | Superada por c-145 G (alineacion completa de `CLAUDE.md` y `openspec/config.yaml`); no se confirma como decision vigente. |
| c-132 | OQ1 | Tope de paginas decidido por c-141 (cuerpo <= 100); +1 medido. |
| c-132 | OQ2 | Incluir la correccion colateral T13 (costo operativo) en variante corta. |
| c-132 | OQ3 | Rama "laxa disponible" de D4; exactitud laxa `179/200 = 0,8950`. |
| c-133 | OQ1 | Segunda sub-hipotesis: cota 0,15, "no contrastada por ausencia de registro primario". |
| c-133 | OQ2 | Subsidiaria de eficiencia: "no contrastada" (prevalece D3 con E4). |
| c-133 | OQ3 | Objetivo 3: "Alcanzado parcialmente" (complejidad operativa percibida no satisfecha). |
| c-134 | OQ3 | Se retira la promesa del IC del tiempo medio; la lista declarada queda alineada con lo reportado. |
| c-136 | OQ1 | Incluir la extension D7 (SSO, prefijo, Kubernetes, parametros de inferencia). |
| c-136 | OQ2 | Aceptar +1 pagina, con renegociacion en c-141; delta medido 0. |
| c-136 | OQ3 | Usar las claves de c-138; `Zhao2021_calibrate_before_use` no se cita. |
| c-138 | OQ1 | Tope por c-141; +2 esperadas (+3 peor caso), compensado en el texto. |
| c-138 | OQ2 | ITSM-BERT y Alsac fuera del change. |
| c-138 | OQ3 | Vacancia acotada enunciada solo con C1-C2. |
| c-138 | OQ4 | FrugalGPT por arXiv, sin evadir los controles anti-bot. |
| c-139 | OQ1 | Paramesh rama B; se retiran las cifras no verificadas y la fila declara "no reportado en el alcance revisado". |
| c-139 | OQ2 | ISO/IEC 27701:2025. |
| c-139 | OQ3 | Russell y Norvig 2021. |
| c-139 | OQ4 | Incluir FastAPI, RGPD y las precisiones de `11:44` y `11:68`. |
| c-139 | OQ5 | Palanca tipografica reservada a c-141; cuerpo neutral. |
| c-137 | OQ1 | Unificar los 5 pasajes canonicos a las cadenas sin tilde. |
| c-137 | OQ2 | No editar el dictamen auditado. |
| c-137 | Tipografica 1 | `headheight=13pt`. |
| c-137 | Tipografica 2 | Glifo de cierre en las comillas de apertura de A1-A4/B1/C1/C2. |
| c-137 | Tipografica 3 | "cache" sin tilde en `02:65`. |
| c-135 | OQ-2 | Ventana mensual confirmada (manual junio-agosto; automatizada septiembre-octubre de 2026) e hitos del repositorio. |
| c-135 | OQ-3 | Checkpoint MEDIUM de `06:75` sin "sin exposicion al corpus" y sin fechas. |
| c-135 | OQ-4 | Telefonia fuera de la comparativa; el rasgo queda en `03:84`. |
| c-135 | OQ-5 | Acceso institucional "no reportado"; Zangari sin dato de idioma. |

## Dictamen v10 / v1.1.0 (2026-10-22) - cobertura por change (FASE 36)

**Origen**: change `c-141-integracion-release-v1-2-0`, tarea 6.1 (matriz de trazabilidad), 6.2 (observaciones no numeradas) y 6.3 (rubrica). Escrito el **2026-10-26**. La matriz da, por recomendacion o parte de recomendacion, el change dueno, el `archivo:linea`, el `\label` ancla mas cercano (el del flotante si la linea esta dentro de una tabla o figura; si no, el de la seccion o subseccion previa), un fragmento verificable y el estado.

**Alcance de las lineas**: calculadas sobre el **arbol integrado pre-compactacion y pre-C1** (HEAD `b3c6f0f` mas las ediciones del tramo de integracion, Anexo I incluido). Valen en `v1.2.0` solo si C1 (tarea 5.1: Anexo B y titulo de `Gomez2026_repositorio`) y una eventual compactacion (3.4/3.5) no desplazan esas lineas: las filas de `12-anexos.tex` posteriores al Anexo B y la fila B16b son las sensibles. **Hay que recalcular tras C1 y antes de crear el tag** con `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py --reubicar` (arbol de trabajo) y verificar contra la etiqueta con `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py --rev v1.2.0` (la tarea 6.1 pide `git show v1.2.0:<archivo> | sed -n '<linea>p'` por fila; el script lo automatiza y comprueba el `\label`). Verificacion de este tramo: **todas las filas pasan** (41 filas; B16b se omitia por PENDIENTE). **Actualizacion 2026-10-26 (tramo B, tarea 5.1)**: con el contenido de C1 aplicado, la fila A5a se desplazo dos lineas (`12-anexos.tex:144` -> `:142`, por el retiro de la linea del hash y de su linea en blanco) y se reubico con `--reubicar`; la fila B16b ya no se omite (`Bibliography_base.bib:795`); resultado: 41 filas, 0 fallas. Repetir con `--rev v1.2.0` tras el tag.

| Rec | Sintesis | Change | Archivo:linea en v1.2.0 | Ancla | Fragmento verificable | Estado |
|---|---|---|---|---|---|---|
| A1 | Gate de revision acotado por etapa: el umbral 0,70 aplica solo a la salida de Gemini | c-130 | `docs/Tesis/v10 (IA)/paper/sections/02-marco-teorico.tex:34` | `subsec:human-in-the-loop` | `revisión selectiva acotada por etapa` | cerrada |
| A1 | Arquitectura: la reserva fija confianza 0,0 y el cortocircuito se decide por el puntaje de correctitud | c-130 | `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex:82` | `subsec:subsistema-clasificacion` | `fija la confianza en 0,0` | cerrada |
| A1 | 124 de 200 casos con confianza < 0,70 no escalan (todos de la etapa determinista) | c-130 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:157` | `subsec:reduccion-intervencion` | `124 de los 200 casos` | cerrada |
| A2 | Calibracion aparente invertida = efecto de composicion entre etapas, no anti-calibracion | c-131 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:189` | `subsec:calibracion` | `es un efecto de composición` | cerrada (cache de la corrida principal via c-143; PROVISIONAL) |
| A2 | Exactitud estricta y laxa por etapa del pipeline (tab:exactitud-etapa-canal) | c-131 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:117` | `tab:exactitud-etapa-canal` | `Etapa determinística & 131 & 97/131` | cerrada |
| A3 | Subseccion nueva de balance neto entre ahorro bruto de registro y derivaciones erroneas | c-132 | `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex:70` | `subsec:balance-neto` | `Balance neto de la automatización` | cerrada (revision del autor pendiente sobre resumen y conclusion) |
| A3 | Conclusiones: tiempo bruto liberado con saldo neto indeterminado | c-132 | `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex:41` | `subsec:cumplimiento-objetivos` | `cuyo saldo neto está indeterminado` | cerrada |
| A4 | Atribuciones de las fuentes sobre rendimiento multilingue acotadas a lo que sostienen | c-139 | `docs/Tesis/v10 (IA)/paper/sections/02-marco-teorico.tex:50` | `subsec:nlp-llm` | `tampoco es uniforme entre idiomas` | cerrada (acceso a texto completo parcial; PROVISIONAL) |
| A4 | Hallazgo de Revina 2020 presentado como decision de diseno y no como resultado medido | c-139 | `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex:30` | `subsec:trabajos-academicos` | `no como resultado medido` | cerrada |
| A4 | Literatura de calibracion de la confianza y cascadas de modelos (subseccion 3.4) | c-138 | `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex:58` | `subsec:calibracion-cascadas` | `Calibración de la confianza y cascadas de modelos` | cerrada |
| A5a | Procedencia declarada: ajustes del filtro y del prompt hechos con el corpus de evaluacion | c-130 / c-144 | `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex:20` | `subsec:interpretacion-resultados` | `La procedencia de los datos de ajuste merece una observación aparte` | cerrada (declaracion de c-144) |
| A5a | Anexo H: prompt ajustado sobre el corpus de validacion, sin corpus independiente de preproduccion | c-130 / c-144 | `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex:144` | `subsec:anexo-iteracion-prompt` | `no se dispuso de un corpus independiente de preproducción` | cerrada (declaracion de c-144) |
| A5b | Sensibilidad fuera de muestra de los ajustes (subseccion y tabla nuevas) | c-142 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:191` | `subsec:sensibilidad-ajustes` | `Sensibilidad al ajuste del clasificador con el corpus` | cerrada (nivel c del prompt no cuantificado; PROVISIONAL) |
| A5b | Septima limitacion: metricas estimadas dentro de la muestra | c-142 | `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex:56` | `subsec:limitaciones-estudio` | `Séptimo, el vocabulario del filtro` | cerrada |
| B4 | Tabla de cumplimiento de objetivos sin sobreestimar (objetivo general: alcanzado parcialmente) | c-133 | `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex:22` | `tab:cumplimiento-objetivos` | `Objetivo general: viabilidad y desempeño & Alcanzado parcialmente` | cerrada |
| B5 | Segunda sub-hipotesis contrastable contra la cota 0,15; estado no contrastada | c-133 | `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex:34` | `subsec:hipotesis-trabajo` | `complemento del umbral de exactitud fijado a priori` | cerrada (OQ1 PROVISIONAL) |
| B6 | Macro-F1 primaria de umbral (cuatro clases estimables) unificada | c-133 | `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:75` | `subsec:analisis-estadistico` | `contra el cual se eval` | cerrada |
| B7a | Tiempos manuales y automatizados por canal con contraste intra-canal | c-134 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:37` | `tab:tiempos-canal` | `label{tab:tiempos-canal}` | cerrada |
| B7b | Exactitud estricta y laxa por canal de origen | c-131 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:119` | `tab:exactitud-etapa-canal` | `Llamada telefónica & 81 & 53/81` | cerrada |
| B8 | Exactitud laxa definida junto a la estricta (metrica secundaria) | c-131 | `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:75` | `subsec:analisis-estadistico` | `exactitud laxa` | cerrada |
| B9 | Cronograma con procedencia: figura en el Anexo A | c-135 | `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex:22` | `fig:cronograma` | `label{fig:cronograma}` | cerrada parcialmente: fechas de las seis iteraciones sin fuente primaria (tarea 5.2 de c-135 abierta) |
| B9 | Cuarta limitacion: version del modelo vigente durante la campana (24-09-2026) | c-135 | `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex:50` | `subsec:limitaciones-estudio` | `integrada al clasificador el 24 de septiembre de 2026` | cerrada |
| B10a | Introduccion de resultados enumera los seis apartados vigentes | c-135 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:6` | `sec:resultados` | `Los resultados se presentan en seis apartados` | cerrada |
| B10b | Dimension nombrada como intervencion humana (sin 'reduccion') | c-135 | `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:6` | `sec:resultados` | `intervención humana, calibración de la confianza` | cerrada |
| B10c | Tabla comparativa: tres dimensiones; telefonia fuera de la afirmacion comparativa | c-135 | `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex:66` | `subsec:analisis-comparativo` | `tres dimensiones` | cerrada (OQ-4 PROVISIONAL) |
| B10d | Metricas de los trabajos academicos completadas desde la fuente accesible | c-135 | `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex:46` | `tab:trabajos-academicos` | `20.000 reclamos + 35.000 issues` | cerrada parcialmente: Paket 2024 y Colavito 2025 sin acceso (OQ-5) |
| B11 | Linea prioritaria: calibracion del gate | c-136 | `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex:8` | `subsec:calibracion-gate` | `label{subsec:calibracion-gate}` | cerrada |
| B11 | Linea prioritaria: correccion de la medicion de intervencion humana | c-136 | `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex:16` | `subsec:medicion-intervencion` | `label{subsec:medicion-intervencion}` | cerrada |
| B12 | Muestreo: asignacion proporcional no verificable frente al universo; clase con n = 1 no estimable | c-134 | `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:45` | `subsec:poblacion-muestra-corpus` | `estratificado` | cerrada (OQ2 PROVISIONAL) |
| B13a | Canal telefonico: duracion de 20,1 s como cota inferior por el tope de grabacion | c-135 | `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex:39` | `subsec:cumplimiento-objetivos` | `cota inferior` | cerrada |
| B13b | Cronometraje en vivo: relato del procedimiento, efecto Hawthorne atenuado y residual | c-134 | `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:16` | `subsec:diseno-experimental` | `Hawthorne` | cerrada (OQ1 PROVISIONAL) |
| B14 | Revision ortotipografica: titulos acentuados de indices y bibliografia | c-137 | `docs/Tesis/v10 (IA)/paper/main.tex:79` | - | `Referencias bibliográficas` | cerrada |
| B15 | Normas y metodos estadisticos con entrada bibliografica (ISO/IEC 27001:2022) | c-139 | `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex:40` | `subsec:cumplimiento-marco` | `ISO27001_2022` | cerrada |
| B16a | Metadatos bibliograficos (Jurafsky y Martin: edicion 2026, URL y fecha de consulta) | c-139 | `docs/Tesis/v10 (IA)/Bibliography_base.bib:96` | - | `@unpublished{Jurafsky2023_speech_language` | cerrada |
| B16b | Version de Gomez2026_repositorio alineada con la release (1.2.0) | c-141 | `docs/Tesis/v10 (IA)/Bibliography_base.bib:795` | - | `n 1.2.0)}` | Aplicado en C1 (tarea 5.1, 2026-10-26); verificado por el script |
| Criterio 5 (residual) | TLS no verificado e invocacion sincronica declarados como limite (c-140 excluido provisionalmente) | c-140 / limitacion declarada | `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex:23` | `tab:cumplimiento-objetivos` | `TLS no verificado` | residual declarado |
| B11 | Aprendizaje activo: seleccion por senales independientes y confianza solo tras recalibracion | c-136 | `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex:30` | `subsec:aprendizaje-activo` | `label{subsec:aprendizaje-activo}` | cerrada |
| B12 | Contraste direccional: p unilateral global junto al bilateral de los tiempos | c-134 | `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:71` | `subsec:analisis-estadistico` | `alternative=greater` | cerrada |
| B12 | Potencia expresada en d_z con eficiencia relativa asintotica 0,864 | c-134 | `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:87` | `subsec:amenazas-validez` | `0{,}864` | cerrada |
| Residual criterio 4 (A1/B5) | Intervencion humana no medida: sin registro primario de la accion manual por caso | c-130 / c-133 | `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex:58` | `subsec:limitaciones-estudio` | `no se conservó un registro primario de la acción manual` | residual declarado |
| Residual criterio 4 (kappa) | Registros primarios del doble etiquetado no conservados: kappa sin incertidumbre cuantificada | - | `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:55` | `subsec:poblacion-muestra-corpus` | `registros que no se conservaron en las fuentes disponibles` | residual declarado |

Estados: *cerrada* (la correccion esta en el arbol integrado), *cerrada parcialmente* (con la justificacion indicada), *residual declarado* (limitacion que la tesis declara; no corregible con los datos disponibles) y *PENDIENTE* (se cierra en un paso posterior). Las decisiones PROVISIONALES de cada change figuran en sus grupos de este registro y en la lista consolidada de "Pendientes y verificaciones diferidas". El `Rec` A4 tiene dos duenos de parte (c-139 para la correspondencia texto-fuente; c-138 para las fuentes de calibracion y cascadas, seccion 4 del dictamen y criterio 3 residual); A5 se divide en A5a (c-130, a traves de la declaracion de c-144) y A5b (c-142).

### Observaciones del dictamen sin numero de recomendacion (tarea 6.2)

| # | Observacion | Dueno | Estado |
|---|---|---|---|
| O1 | Registros primarios del doble etiquetado no conservados (kappa sin incertidumbre) | Fuera de alcance (no recuperables); limitacion declarada en `subsec:poblacion-muestra-corpus` (fila "Residual criterio 4 (kappa)" de la matriz) | residual declarado |
| O2 | Doble fecha de consulta en las cinco entradas `@online` | c-139 (B16) | cerrada: solo `urldate = {2026-10-19}`; notas sin fecha |
| O3 | Seudonimo como apellido en `Tiangolo2024_fastapi` | c-139 (B16) | cerrada: `Ramirez, Sebastian` |
| O4 | `GDPR2016` y `Jurafsky2023_speech_language` sin enlace | c-139 (B16) | cerrada: URL y `urldate` en ambas |
| O5 | Sede omitida en Liu et al. 2025 (`liu2025tickit`) | c-139 (B16) | cerrada: *FSE Companion '25*, Trondheim |
| O6 | Ausencia de `main.log` en el repositorio | c-141 (D6) | cerrada por evidencia: la compilacion se consigna en este registro (seccion "Compilacion de verificacion"); la evidencia de la release se completo en 5.3 (seccion "Contenido de C1 y compilacion de registro") |
| O7 | Version del modelo fechada en "junio de 2026" frente a `11036be` (24-09-2026) | c-135 (B9) | cerrada: la cuarta limitacion cita `gemini-3.6-flash`, integrada el 24-09-2026 |
| O8 | `timeout` de 10 s en la tesis y en el Anexo H frente a 30 s del backend | c-135 (D15); el residual de `CLAUDE.md` y `openspec/config.yaml` no tiene dueno (fuera de la tesis) | cerrada en la tesis (30 s por intento y 60 s en total); pendiente fuera de la tesis |
| O9 | Remision al inexistente `docs/prompt_gemini_history/` y afirmacion refutada en `evaluation/README.md` y `docs/anexo_h_prompt_gemini.md` | c-144 y c-142 | cerrada: `prompt_gemini_history` = 0 en `sections/` y en `docs/anexo_h_prompt_gemini.md`; `NO fue ajustado` = 0 en `evaluation/README.md` |
| O10 | Afirmacion refutada en `knowledge-base/11_evaluacion_experimental.md` | c-141 (D9, tarea 7.6) | cerrada (2026-10-26): la linea "Anti data-leakage" se reemplazo por la procedencia real de los ajustes (c-71, c-72 y c-74 con el corpus de evaluacion); ver "Renders y base de conocimiento" |

Las diez observaciones tienen dueno o declaracion de residual; ninguna queda sin cubrir.

### Verificacion de cierre contra la rubrica del dictamen (tarea 6.3)

Rubrica de la catedra tal como la aplico el dictamen del 22-10-2026 (revision vigente, ponderado **7,67**, nota 8): nueve criterios evaluables sobre peso efectivo 105; el criterio 10 (defensa oral, peso 10) **no es aplicable** a este documento. **No se asignan puntajes nuevos**: la columna "Puntaje" repite el del dictamen y la evidencia es la fila de la matriz. "Aplicado, pendiente de release" significa que la correccion esta en el arbol integrado y se consolida al etiquetar `v1.2.0`.

| Criterio | Peso | Puntaje (dictamen) | Descuento | Change dueno | Estado tras la release | Evidencia (matriz) |
|---|---|---|---|---|---|---|
| 1 Definicion del problema | 15 | 8,5 | Sub-hipotesis 2 no contrastable | c-133 (B5) | aplicado, pendiente de release | B5 |
| 1 Definicion del problema | 15 | 8,5 | Hipotesis subsidiarias no contrastadas | c-133 (B5) | aplicado, pendiente de release (rotuladas "no contrastadas") | B5 |
| 1 Definicion del problema | 15 | 8,5 | Sub-pregunta de calidad por canal sin respuesta | c-131 (B7b) | aplicado, pendiente de release | B7b |
| 2 Justificacion y relevancia | 10 | 9 | Sin descuentos (verificar que c-132 no altere el argumento) | c-132 / c-139 (verificacion) | aplicado, pendiente de release: c-132 matizo dos verbos de `subsec:justificacion` ("busca liberar") y no altero las tres dimensiones; revision del autor pendiente | A3 |
| 3 Marco teorico y revision | 15 | 8 | Metricas de la tabla de trabajos previos no extraidas | c-135 (B10d) | aplicado, pendiente de release; cerrada parcialmente: Paket 2024 y Colavito 2025 sin acceso (OQ-5) | B10d |
| 3 Marco teorico y revision | 15 | 8 | Telefonia no evidenciada por la tabla comparativa | c-135 (B10c) | aplicado, pendiente de release | B10c |
| 3 Marco teorico y revision | 15 | 8 | Sin literatura de calibracion y cascadas | c-138 | aplicado, pendiente de release | A4 (c-138) |
| 3 Marco teorico y revision | 15 | 8 | Atribuciones imprecisas a fuentes de NLP | c-139 (A4) | aplicado, pendiente de release | A4 (c-139) |
| 4 Metodologia | 20 | 7 | Contraste unilateral con p bilateral | c-134 (B12) | aplicado, pendiente de release | B12 (alternative=greater) |
| 4 Metodologia | 20 | 7 | Comparacion de potencia heterogenea | c-134 (B12) | aplicado, pendiente de release | B12 (0{,}864) |
| 4 Metodologia | 20 | 7 | Estratificacion no verificable y clase con n = 1 | c-134 (B12) | aplicado, pendiente de release (OQ2 PROVISIONAL) | B12 (estratificado) |
| 4 Metodologia | 20 | 7 | Exactitud laxa no reportada | c-131 (B8) | aplicado, pendiente de release | B8 |
| 4 Metodologia | 20 | 7 | Variable de intervencion humana nunca medida | c-130 (A1) y c-133 (B5) | residual declarado: "Octavo, no se conservo un registro primario" (`subsec:limitaciones-estudio`) | Residual criterio 4 (A1/B5) |
| 4 Metodologia | 20 | 7 | Registros primarios del doble etiquetado no conservados | - | residual declarado en `subsec:poblacion-muestra-corpus` | Residual criterio 4 (kappa) |
| 4 Metodologia | 20 | 7 | Afirmacion de ausencia de fuga de datos desmentida por el historial | c-130 (A5a) y c-142 (A5b) | aplicado, pendiente de release | A5a, A5b |
| 5 Desarrollo tecnico | 15 | 8 | TLS no desplegado, invocacion sincronica sin reintentos, sin pruebas de extremo a extremo | c-140 (excluido provisionalmente) o limitacion declarada | residual declarado (objetivo 1 "Alcanzado parcialmente"); si el usuario incluye c-140 se re-evalua | Criterio 5 (residual) |
| 5 Desarrollo tecnico | 15 | 8 | Gate de revision no aplicado a la etapa determinista sin documentarlo | c-130 (A1) | aplicado, pendiente de release | A1 |
| 6 Resultados y analisis | 10 | 6,5 | Calibracion invertida como artefacto de agregacion | c-131 (A2) | aplicado, pendiente de release | A2 |
| 6 Resultados y analisis | 10 | 6,5 | 124 casos bajo el umbral no escalados sin explicacion | c-130 (A1) | aplicado, pendiente de release | A1 |
| 6 Resultados y analisis | 10 | 6,5 | Sin exactitud por etapa ni por canal | c-131 (A2, B7b) | aplicado, pendiente de release | A2, B7b |
| 6 Resultados y analisis | 10 | 6,5 | Tiempos manuales por canal no tabulados | c-134 (B7a) | aplicado, pendiente de release | B7a |
| 6 Resultados y analisis | 10 | 6,5 | Exactitud reportada sin advertir que es en parte una estimacion dentro de la muestra | c-130 (A5a) y c-142 (A5b) | aplicado, pendiente de release | A5a, A5b |
| 7 Conclusiones y aportes | 10 | 7 | Tabla de cumplimiento sobreestimada (objetivos 1, 3 y 4) | c-133 (B4) | aplicado, pendiente de release | B4 |
| 7 Conclusiones y aportes | 10 | 7 | Viabilidad operativa sin computar el costo de la derivacion erronea | c-132 (A3) | aplicado, pendiente de release (revision del autor sobre resumen y conclusion) | A3 |
| 7 Conclusiones y aportes | 10 | 7 | Dos lineas prioritarias anunciadas sin desarrollo | c-136 (B11) | aplicado, pendiente de release | B11 |
| 7 Conclusiones y aportes | 10 | 7 | Aprendizaje activo contradictorio con el hallazgo de calibracion | c-136 (B11) | aplicado, pendiente de release | B11 (aprendizaje activo) |
| 8 Redaccion y estructura | 5 | 7 | Patron sistematico de tildes incorrectas | c-137 (B14) | aplicado, pendiente de release | B14 |
| 8 Redaccion y estructura | 5 | 7 | Cronologia no conciliada entre capitulos | c-135 (B9) | aplicado, pendiente de release; cerrada parcialmente (fechas de las seis iteraciones, tarea 5.2 abierta) | B9 |
| 8 Redaccion y estructura | 5 | 7 | Residuos de redaccion en el capitulo 7 y en la tabla comparativa | c-135 (B10a, B10b, B10c) | aplicado, pendiente de release | B10a, B10b, B10c |
| 9 Referencias | 5 | 7,5 | Correspondencia semantica texto-fuente deficiente | c-139 (A4) | aplicado, pendiente de release | A4 (c-139) |
| 9 Referencias | 5 | 7,5 | Normas ISO/IEC y NIST sin entrada bibliografica | c-139 (B15) | aplicado, pendiente de release | B15 |
| 9 Referencias | 5 | 7,5 | Metadatos incompletos o discordantes | c-139 (B16a) y c-141 (B16b) | B16a y B16b aplicados (B16b en el contenido de C1, tarea 5.1) | B16a, B16b |
| 10 Defensa oral | 10 | - | No evaluable en este dictamen | - | no aplicable | - |

Los nueve criterios evaluables figuran con todos los descuentos que enumera el dictamen (incluidos los dos de A5 en los criterios 4 y 6); el criterio 10 queda no aplicable; no hay puntajes nuevos. Residuales: el kappa sin incertidumbre y la intervencion humana no medida (criterio 4) y el TLS, los reintentos y las pruebas de extremo a extremo (criterio 5) son los descuentos que la release no corrige; el criterio 5 depende de la decision del usuario sobre c-140.

## Correccion factual de la release v1.2.0 (c-145)

**Origen**: change `c-145-correccion-factual-sincronizacion-del-memo-y-portabilidad-del-harness`, aplicado el **2026-10-26** sobre la rama `change/c-145-...` (cortada de `main` en `224fa16`, merge del PR #40 ya integrado). Corrige afirmaciones que el repositorio desmiente en la release `v1.2.0` (A1: 16 pruebas de integracion PostgreSQL con omision; A2: recuentos congelados de frontend; A3: identificadores internos `OQ1 = A`/`OQ2 = A del change c-72` en el cuerpo), sincroniza el memo canonico (B: margen `6,66 %` vigente y barrido de referencias), precisa la discusion (C), resuelve el placeholder `P4` (D), hace portable el arnes de sensibilidad (E) y agrega la barrera ejecutable `scripts/preflight/docs_stack_sync.py` de `DOC-005` (H). Gobernanza: A/B/C MEDIO; D/E/G/H BAJO; F (release) ALTO.

### Red de seguridad y linea base (tareas 1.1 a 1.5) - 2026-10-26

- **1.1 Interprete y entorno**: `python3 --version` = **`Python 3.12.3`** (empieza con `Python 3.12.3`, verificado); `uname -a` = `Linux skywalker-SF20GM7-2023 6.8.0-147-generic #147-Ubuntu SMP PREEMPT_DYNAMIC Thu Sep 24 11:33:16 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux`. La maquina de trabajo usa **3.12.3**; la CI usa **3.12.15** (Python de CI documentado en el design, D-Entorno).
- **1.2 Baseline de la suite de evaluacion**: `cd evaluation && python3 -m pytest -q` = **4 failed, 448 passed, 1 skipped** (28 warnings, 17,06 s). Coincide con el baseline esperado para 3.12.3. Los 4 fallos son de `tests/test_sensibilidad_ajustes.py` y el mensaje es `error: ambiguous option: --brazo could match --brazo-vigente, --brazo-sin-reglas` (`SystemExit: 2`). No se corrigen fallos preexistentes.
- **1.3 Suite de sensibilidad aislada**: `cd evaluation && python3 -m pytest tests/test_sensibilidad_ajustes.py -q` = **4 failed, 137 passed** (6,97 s); los 4 fallos coinciden exactamente con los de 1.2.
- **1.4 Linea base de paginas**: `pdfinfo "docs/Tesis/v10 (IA)/paper/main.pdf" | grep Pages` = **109**; `grep -n "contentsline {section}{Anexos}" main.toc` = linea 96, pagina **101**. Cuerpo = 101 - 1 = **100**; anexos = 109 - 100 = **9**. Ledger base: **109 / 100 / 9** (margen 0 de la regla cuerpo sin anexos <= 100).
- **1.5 Estado de los tags**: `git rev-parse v1.2.0^{commit}` = `a49d035c67b32ae17e633ec04b09ecdd2781aac6`; `git cat-file -t v1.2.0` = `tag`; tags previos: `v1.0.0` = `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` = `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` = `7103b649d8c4f51737ad6ad4095dad22c9406400`, `v1.1.1` = `4160d84286623b073d2904353e6f9163ae211de7`. Los cinco coinciden con los valores de `tasks.md`.

### Portabilidad del arnes (bloque E, tareas 2.1 a 2.7) - 2026-10-26

TDD estricto. **E1**: se agrego `allow_abbrev=False` al `ArgumentParser` de nivel superior de `evaluation/sensibilidad_ajustes.py` (`construir_parser`). Sin el flag, en Python 3.12.3 `--brazo` (opcion del subcomando `prompt`) se resuelve contra `--brazo-vigente`/`--brazo-sin-reglas` y el parser aborta con `ambiguous option`.

- **RED**: `tests/test_sensibilidad_ajustes.py::test_c145_cli_prompt_reconoce_brazo_como_opcion_del_subcomando` falla antes del cambio con `SystemExit: 2` y el mensaje `ambiguous option: --brazo could match --brazo-vigente, --brazo-sin-reglas` (la misma causa que 1.2/1.3).
- **GREEN**: `pytest tests/test_sensibilidad_ajustes.py -q` pasa de 4 fallos a **142 passed**; `python -m evaluation.sensibilidad_ajustes prompt --brazo vigente --help` sale con codigo 0 y no imprime `ambiguous option`.
- **TRIANGULATE**: `--brazo sin-reglas` (subcomando), `--brazo-vigente`/`--brazo-sin-reglas` (nivel superior, nombres exactos), prefijos no exactos `--brazo-v`/`--brazo-s` (no se resuelven silenciosamente; el caso falla si se elimina `allow_abbrev=False`, verificado) y el comando del escenario por `subprocess` (`prompt --brazo vigente --help`, codigo 0). Total del archivo: **148 passed**.
- **REFACTOR**: el parser ya estaba extraido como funcion pura (`construir_parser` devuelve un parser nuevo por llamada, sin estado compartido); no hizo falta otra extraccion. Suite verde despues del cambio.
- **E2-i**: `tests/test_run_evaluation.py::test_c145_cli_solo_tiempos_con_reporte_ausente_falla_sin_traza` (RED: `FileNotFoundError` crudo; GREEN: `main()` envuelve la llamada a `main_solo_tiempos()` en `try/except FileNotFoundError`, imprime `ERROR: ...` en stderr y sale con `SystemExit(1)` sin traza). TRIANGULATE: corpus ausente sale igual de limpio. `tests/test_run_evaluation.py` = **70 passed**.
- **2.6 Suite completa**: `cd evaluation && python3 -m pytest -q` = **461 passed, 1 skipped, 0 failed** (baseline 452 recolectadas; 9 pruebas nuevas: 7 en `test_sensibilidad_ajustes.py` y 2 en `test_run_evaluation.py`).
- **E2-ii (excluido, tarea 2.7)**: la identidad de las caches de predicciones en `construir_procedencia` (ruta, SHA-256 y `generated_at`) queda como **trabajo futuro**. Motivo: agregarla ampliaria el esquema del reporte de sensibilidad, sus pruebas de formato y la documentacion de `evaluation/README.md` sin ser un defecto que bloquee el PR ni la release (disciplina de alcance, design D8). No se implementa en c-145.

### Barrera documental `docs_stack_sync.py` (bloque H, tareas 2.8 a 2.13) - 2026-10-26

Barrera ejecutable de `DOC-005` (`scripts/preflight/docs_stack_sync.py`), con doce chequeos (design D15) sobre `settings.py` y `constants.py` (via `ast`), `requirements.txt`, `docker-compose.yml`, `openspec/config.yaml` y `CLAUDE.md`. Contrato reutilizado de `cost_readiness.py`/`gemini_readiness.py` (`Check`, `check_docs`, `run_docs_stack_sync`, `exit_code`, `format_summary`).

- **TDD (tareas 2.8 a 2.11)**: **RED**: `scripts/preflight/test_docs_stack_sync.py` falla al recolectar con `ModuleNotFoundError: No module named 'docs_stack_sync'`; los 48 preflights existentes siguen en verde. **GREEN**: se implementa el modulo; `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` = **32 passed**. **TRIANGULATE**: (a) los cinco documentos en sincronia -> 0 hallazgos y `exit_code` 0; (b) cada drift por separado -> exactamente un FAIL que nombra el valor (modelo, timeout, reintentos, muestreo, FastAPI, Uvicorn, google-genai en config y en `CLAUDE.md`, N8N en config y en `CLAUDE.md`, umbrales, categorias); (c) YAML malformado -> FAIL explicito sin traza; (d) seccion ausente -> FAIL, no excepcion; (e) `CLAUDE.md` sin el modelo -> FAIL; (f) `SECTORES_CANONICOS` en distinto orden -> FAIL del chequeo 11; (g) los cinco literales volatiles (`0.5166`, `0.70`, `0.115`, `>= 1.0`, `2.11.2`) restateados en `CLAUDE.md` -> FAIL del chequeo 12; (h) el mismo valor como remision a `openspec/config.yaml` -> PASS del chequeo 12; (i) cambiar el umbral en `config.yaml` y restatear el valor nuevo -> FAIL del chequeo 12 (la lista se deriva, no esta hardcodeada); (j) identificador retirado `2.5 Flash` que ya no figura en `config.yaml` -> FAIL por la lista estatica. **REFACTOR**: los parsers ya estan extraidos como funciones puras (`_leer_settings`, `_leer_constantes`, `_leer_requirements`, `_leer_compose`, `_leer_docs`, `_leer_claude`); se extrajo ademas `_comparar_valores` para unificar la comparacion de parametros de los chequeos 2, 3 y 10 (regla de tres), sin cambios de comportamiento. Suite verde despues del refactor. Total del directorio `scripts/preflight`: **80 passed**.
- **2.12 Cableado en CI**: paso `Run docs stack sync preflight` (`run: python scripts/preflight/docs_stack_sync.py`) agregado en el job `backend-tests`, despues de `Run Gemini readiness preflight`. Verificado: `yaml.safe_load` del workflow parsea y el nombre del paso figura **una sola vez**.
- **2.13 PRUEBA DE LA BARRERA (arbol con la documentacion sin corregir)**: `python3 scripts/preflight/docs_stack_sync.py` termina con **codigo 1** y **8 de 12 chequeos en FAIL**. Salida completa:

```text
[FAIL] modelo: config.yaml y CLAUDE.md coinciden con Settings.gemini_model - config.yaml declara 'Gemini 2.5 Flash' y Settings dice 'gemini-3.6-flash'; CLAUDE.md menciona 'gemini-2.5-flash' y Settings dice 'gemini-3.6-flash'
[FAIL] timeout y reintentos: config.yaml coincide con Settings - timeout_s: config.yaml=10 vs Settings=30; config.yaml no declara total_timeout_s (Settings: 60); config.yaml no declara max_retries (Settings: 2)
[PASS] parametros de muestreo: config.yaml coincide con Settings
[FAIL] framework: FastAPI/Uvicorn de config.yaml compatibles con requirements.txt - FastAPI: config.yaml declara 0.115 y requirements.txt fija 0.143.3
[FAIL] google-genai: restriccion de config.yaml y CLAUDE.md compatible con requirements.txt - config.yaml declara google-genai >= 1.0 y requirements.txt fija >=2.31.0,<3; CLAUDE.md declara google-genai >= 1.0 y requirements.txt fija >=2.31.0,<3
[FAIL] n8n: version declarada coincide con la imagen del compose - CLAUDE.md declara N8N 1.62 y la imagen es n8nio/n8n:2.11.2
[FAIL] servicios: los descritos en CLAUDE.md existen en el compose - CLAUDE.md describe servicios inexistentes: Redis (servicio 'redis' ausente en docker-compose.yml)
[FAIL] etapas retiradas: ninguna se describe como vigente - CLAUDE.md menciona la etapa retirada LangChain (retirada por c-72)
[PASS] config.yaml: YAML valido y con las claves que consume el CLI
[PASS] umbrales: config.yaml coincide con Settings
[PASS] categorias: config.yaml coincide con SECTORES_CANONICOS (contenido y orden)
[FAIL] duplicacion: CLAUDE.md no restatea literales volatiles de config.yaml - CLAUDE.md repite literales que viven en openspec/config.yaml: '0.5166' (derivado de conventions.thresholds.deterministic_score); '0.7' (derivado de conventions.thresholds.human_review); '>= 1.0' (derivado de stack.inference.model (google-genai)); '2.5 Flash' (derivado de lista estatica de identificadores retirados); '1.62' (derivado de lista estatica de identificadores retirados)

RESULT: 4/12 chequeos en PASS (8 en FAIL). Documentacion desincronizada.
```

  Los hallazgos nombran, como minimo: **"Gemini 2.5 Flash"** (chequeo 1), el **timeout de 10 s** (chequeo 2), **"FastAPI 0.115"** (chequeo 4), la **imagen de N8N** (`1.62` declarado frente a `n8nio/n8n:2.11.2`, chequeo 6), el **servicio Redis** (chequeo 7) y la **duplicacion de literales en `CLAUDE.md`** (chequeo 12: `0.5166`, `0.7`, `>= 1.0`, `2.5 Flash`, `1.62`). La barrera detecta el drift real: no sale 0.
- **Asimetria esperada (chequeos 10 y 11 en PASS)**: los umbrales (`0.5166` y `0.70`) y las categorias de `config.yaml` ya coinciden con `Settings` y con `SECTORES_CANONICOS` en este punto (los corrigio el PR #40), de modo que los chequeos 10 y 11 **pasan desde el primer dia**. El valor a probar con 2.13 es que el chequeo **12** detecte la duplicacion de esos mismos valores en prosa dentro de `CLAUDE.md`, no que todo falle. Una barrera que solo falla donde el drift ya se conoce no agrega nada; la asimetria muestra que el chequeo nuevo (12) atrapa la duplicacion sin cobertura que dejaba pasar un cambio de umbral con el pipeline en verde. Los chequeos 3 (muestreo) y 9 (YAML valido) tambien pasan por el mismo motivo. El cierre de la barrera (exit 0 con la documentacion corregida) corresponde al bloque G y se registra en la tarea 10.6.

### Sincronizacion del memo canonico (bloque B, tareas 4.1 a 4.5) - 2026-10-26

- **4.1 Upsert del margen**: se agrega en `numeros-canonicos.md` (Seccion 3.4) la fila `6,66 %` con estado `vigente`, `N ≈ 2.646`, `z = 1,96`, `p = 0,5`, `n = 200`, formula `n = n₀/[1+(n₀−1)/N]` con `n₀ = z²p(1−p)/e²` y procedencia `04-marco-metodologico.tex:51`. Verificacion aritmetica: `n₀ = 216,52`; `216,52/[1+215,52/2646] = 200,21 ≈ 200`.
- **4.2 Retiro del margen calendario**: se conserva la fila `6,74 %` / `N = 3.700` con estado `retirado` y nota de reemplazo por `6,66 %` / `N ≈ 2.646`; no se cita como vigente.
- **4.3 Seccion 7 y `MEMO:732`**: el punto 2 y la advertencia de arrastre del item 4 ahora remiten al upsert de 4.1 y declaran el margen `6,66 %`; el `6,74 %` figura solo como retirado.
- **4.4 Barrido de referencias `07-resultados.tex:<linea>`** (por correspondencia de contenido sobre el archivo vigente):

  | Antes | Despues | Pasaje verificado |
  |---|---|---|
  | `:129` | `:128` | Parrafo del marco metrico, reparto `131/69` y `107/200` |
  | `:75` | `:74` | Exactitud estricta `73,5 % (147/200)` |
  | `:167-188` | `:166-187` | Entorno de `tab:bandas` |
  | `:179-183` | `:178-182` | Filas de bandas `98/26/6/31/39` |
  | `:179-180` | `:178-179` | Bandas `98 + 26` = `124` casos `< 0,70` |
  | `:160` | `:157-159` | Fila `retirado` del `9,5 %`: remite a la seccion que declara la intervencion como no medida |
  | `:55` | `:57` | Parrafo de Wilcoxon `W = 363` |
  | `:21` (mediana) | `:22` | Fila `Mediana (s) = 17,47` |
  | `:190` | `:189` | Parrafo del tramo `>= 0,90` |
  | `:129` (nota c-131) | `:128` | Parrafo del marco metrico en la nota de numeracion |

  Verificacion: cada linea destino contiene el valor citado (`sed -n '<linea>p'`). No se modifico ningun valor ni estado distinto del upsert 6,66/6,74.
- **4.5 Encabezado**: se agrega la entrada `Upsert c-145` con fecha y alcance.

### Correccion factual de la tesis (bloque A, tareas 5.1 a 5.7) - 2026-10-26

- **5.1 Recuento real de integracion**: con las variables dummy de CI exportadas solo en el entorno (sin escribirlas en el repositorio), `cd App/Backend && python3 -m pytest -m integration --collect-only -q` devuelve:

  ```text
  48/1510 tests collected (1462 deselected) in 6.70s
  ```

  Coincide con el esperado `48/1510`. `grep -n "pytest.skip" ".../06-implementacion.tex"` no devuelve coincidencias en la clausula de PostgreSQL.
- **5.2**: `06-implementacion.tex:87` reemplaza "16 tests con un mecanismo de omision automatica (`pytest.skip`) cuando PostgreSQL no esta disponible" por "48 pruebas marcadas como integracion, que fallan de forma ruidosa si PostgreSQL no esta disponible en lugar de omitirse". `grep -n "16 tests\|omisión automática"` = 0; `grep -n "48 pruebas"` = linea 87.
- **5.3**: `06-implementacion.tex:91` retira "357" y "56 archivos" y conserva la remision al reporte vigente del pipeline. `grep -n "357\|56 archivos"` = 0.
- **5.4**: `06-implementacion.tex:44` y `:54` reemplazan los identificadores internos por lenguaje llano que preserva el hecho. `grep -n "OQ1 = A\|OQ2 = A\|change c-72"` = 0.
- **5.5**: el Anexo I (`12-anexos.tex`, `sec:anexo-trazabilidad`) agrega una nota breve que atribuye las dos decisiones al change `c-72`; el cuerpo de `06-implementacion.tex` ya no lo menciona.
- **5.6 Causa raiz de A1**:

  | Hecho | Commit | Fecha | Efecto |
  |---|---|---|---|
  | Se agregan 16 pruebas de integracion PostgreSQL con omision automatica | `a0436e0` (C-19) | 2026-07-03 | Nace la oracion "16 tests ... `pytest.skip`" |
  | `conftest.py` pasa a fallo ruidoso y la suite crece | `ef656ac` (c-29/c-30/c-32) | 2026-09-17 | La oracion queda obsoleta |
  | Copia de trabajo v9 | `8466cbe` | 2026-10-01 | Arrastra la oracion |
  | Copia de trabajo v10 | `7408543` (c-122) | 2026-10-22 | La publica en v10 |

- **5.7 Evidencia de A2**: `find "App/Frontend/src" -type f \( -name '*.test.ts' -o -name '*.test.tsx' \) | wc -l` = **59** archivos; `App/Frontend/node_modules` **ausente** en el worktree. Decision: retirar los recuentos congelados de la tesis (no se ejecuto `npm install` ni Vitest en esta fase) y dejar la cifra sujeta al reporte vigente del pipeline.
- **Paginas (aviso para bloque 8)**: no se recompilo la tesis en estas tareas. El cuerpo sigue en **100** segun la linea base de 1.4; el bloque 8 debe re-medir el conteo tras estos cambios de texto.
