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
- Este registro es acumulativo. Las correcciones que dependan de decisiones o de
  trabajo mayor (reescritura de capítulos) quedan en "Pendientes" hasta aplicarse.
