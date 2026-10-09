# Design: c-76 — Alineación de la tesis con el corpus real y el dictamen CONEAU

## Context

Ver `proposal.md` — Why. La tesis (working copy en `docs/Tesis/v9 (IA)/paper/`)
y sus docs de soporte reportan el corpus sintético descartado en C-27. El régimen
de evidencia real ya existe y está computado:

- Corpus real: `data/corpus_evaluacion_pseudonimizado.json` (200 casos).
- Métricas: `evaluation/report.md` (matriz 5x5, exactitud 73,5 %, macro-F1 0,5207).
- Registro de correcciones: `docs/Tesis/Correcciones/dictamen-correcciones.md`
  (A1–A4 aplicadas; P1.0, P1, P2 en backlog).
- Modelo real en código: `App/Backend/app/config/settings.py` → `gemini-3.6-flash`.

Ya hay ediciones sin commitear para A1–A4 en `README.md`,
`docs/anexo_f_corpus.md`, `evaluation/README.md`, `evaluation/data/README.md`
(todos en disco) que este change formaliza.

Restricción dura: NO tocar `App/**`. Governance MEDIUM.

## Goals / Non-Goals

**Goals:**
- Reconciliar el cuerpo de la tesis con el corpus real (números, distribución,
  matriz, categorías) y eliminar la categoría retirada "Operaciones".
- Declarar el procedimiento de medición manual y su redondeo, con cota
  conservadora de sensibilidad.
- Dejar Anexos y READMEs consistentes, alinear Anexo H y recompilar `main.pdf`.

**Non-Goals:**
- No re-medir tiempos ni regenerar el corpus.
- No modificar el clasificador ni código bajo `App/**`.
- No cambiar el nombre del modelo en el cuerpo de la tesis (ver D4).
- No archivar el change (fuera del alcance del propose).

## Decisions

### D1 — El corpus real es la única fuente de números vigentes
Reemplazar en Cap. 7 (y donde se citen) los valores sintéticos por los de
`evaluation/report.md` y `data/corpus_evaluacion_pseudonimizado.json`.
Alternativa descartada: mantener ambos juegos de números con nota — el dictamen
exige un único resultado vigente.

### D2 — Declarar redondeo al alza y NO re-medir (ex-OQ, resuelto)
`tiempo_manual_s` es medición real en vivo redondeada al alza (31 valores únicos;
180/200 múltiplos de 10). Decisión del autor: **no re-medir**; declarar el sesgo
sistemático en la metodología y reportar la reducción como cota superior más una
cota inferior conservadora.

| Escenario | manual media | reducción | Wilcoxon p | r |
|---|---|---|---|---|
| Reportado (redondeado) | 61,6 s | 75,9 % | 2,0e-32 | 0,983 |
| Conservador (−5 s) | 56,6 s | 73,8 % | 2,6e-30 | 0,966 |
| Conservador (−10 s, peor caso) | 51,6 s | 71,3 % | 2,7e-27 | 0,941 |

Alternativa descartada: re-medir (costo alto, sin cambio material en la
conclusión).

### D3 — Claim primario por mediana y rangos; W real con empates
Usar mediana (manual 50,0 s; auto 12,4 s) y rank-biserial como claim primario.
Reemplazar "W=0 / sin excepción" por **W=335, p=2,05e-32, r=0,983** y declarar
**12/200** pares invertidos. Fórmula y definiciones ya están en Cap. 4.

### D4 — Anexo H: alinear solo el nombre del modelo
P2 del dictamen se limita a `docs/anexo_h_prompt_gemini.md` ("Gemini 2.5 Flash" →
`gemini-3.6-flash`, consistente con README y `settings.gemini_model`). Las
referencias "Gemini 2.5 Flash" del **cuerpo** de la tesis quedan fuera de alcance
y se señalan como riesgo (R3).

### D5 — Formalizar A1–A4 como parte del change
Las ediciones en disco de `README.md`, `docs/anexo_f_corpus.md`,
`evaluation/README.md` y `evaluation/data/README.md` se incorporan al change.
`report_provisional.md → report.md` ya quedó satisfecho en C-27 (sin acción).

### D6 — Recompilación del PDF
Compilar con `latexmk -xelatex main.tex` (o Overleaf XeLaTeX) desde
`docs/Tesis/v9 (IA)/paper/` para regenerar `main.pdf`.

### D7 — T2: El Anexo apunta al corpus JSON real, no a un CSV inexistente
`12-anexos.tex` §Corpus de validación describe un CSV de 7 columnas en
`evaluation/data/` que ya no existe (C-27). Se reescribe para referenciar
`data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y versionado)
y aclarar que `categoría predicha`/`confianza` viven en
`evaluation/predicciones.json`, no por caso en el corpus. Alternativa descartada:
recrear el CSV en `evaluation/data/` — contradice C-27 y el requisito de datos
pseudonimizados versionados.

### D8 — T4: Documentar la etapa fallback y el reparto real de etapas
La tesis reporta un reparto de dos etapas (~62 %/38 %) e ignora la etapa
**fallback**. Se documenta el pipeline real en tres etapas
(deterministic → Gemini → fallback) y se reportan los valores reales de
`evaluation/report.md`: deterministic 131/200 = 65,5 %, Gemini 69/200 = 34,5 %,
fallback 0/200. Se actualizan caps 5.5, 8.1 y 9.1. Alternativa descartada: omitir
fallback por tener 0 casos — el dictamen exige documentar el pipeline completo.

### D9 — T6: Ventana temporal unificada (real) y anti-Hawthorne reconciliado
Los caps 4.2, 4.4, 4.5 y 11.5 se contradicen: la tesis dice "trimestre jul–sep
2025" (población) y "tres días hábiles consecutivos" (corrida automatizada), y
sostiene una observación naturalista sin conocimiento del operador que es
incompatible con el cronometraje en vivo por un par durante el diseño pareado.

**Ventana temporal real (confirmada por el autor, 2026-10-09):**
- Flujo **manual** cronometrado: **junio – agosto 2026**.
- Flujo **automatizado** ejecutado: **septiembre – octubre 2026**.

Se reemplazan las fechas stale por estas. El diseño es **secuencial pareado**
(mismos 200 casos, primero el flujo manual y luego el automatizado), no
simultáneo. La afirmación anti-Hawthorne se reformula como medición en vivo con
conocimiento diferido y `debriefing`, en lugar de un naturalismo estricto durante
toda la campaña. Alternativa descartada: conservar ambas descripciones con una
nota — el dictamen exige consistencia, no reconciliación narrativa.

### D10 — T7: Un único instrumento manual; sin derivar la intervención automática
Los caps 4.2, 4.6 y 7.3 describen de forma incompatible la planilla manual y 7.3
deriva la "intervención humana" del flujo automatizado del registro manual. Se
unifica la descripción del instrumento (medición en vivo cronometrada por el par,
con redondeo al alza consistente con D2) en 4.2, 4.6 y 7.3, y 7.3 SHALL dejar de
derivar la intervención del flujo automatizado de la planilla manual (usa sus
propios registros automáticos). Alternativa descartada: mantener la derivación y
solo matizar el texto — la planilla mide el flujo manual, no el automatizado.

### T1/T3/T5 — Cobertura cruzada (sin decisión nueva)
- **T1**: la presentación de la campaña como realizada la garantiza D1 (nuevos
  números reales en Cap. 7) + verificación explícita de ausencia de lenguaje de
  trabajo futuro en Cap. 7 y Anexo F.
- **T3**: caps 7.2 y 1.6 los cubre D1 (valores reales) y D4 (nombre del modelo);
  se añade la fecha "junio de 2026" y la mención "tres sectores" a la checklist.
- **T5**: tiempos ya cubiertos por D2/D3 (P1.0/P1); solo se referencia.

## Risks / Trade-offs

- [Entorno LaTeX no disponible] → verificar `latexmk`/XeLaTeX antes de aplicar; si
  no está, documentar el resultado de Overleaf.
- [Números dispersos en varios capítulos] → checklist que barre `.tex` por "165",
  "18,2", "0,919", "92", "Operaciones", "W=0", "tres sectores".
- [R3] El repo tiene tres denominaciones de modelo (config.yaml "Gemini 2.5
  Flash", settings.py `gemini-3.6-flash`, README "Gemini 3.6 Flash"). Este change
  solo alinea Anexo H; la inconsistencia queda registrada para el autor.
- [Riesgo de scope creep] Tocar `evaluation/` código no corresponde: la delta de
  `evaluation-framework` es un contrato de reporte, no una re-implementación.

## Migration Plan

1. Aplicar ediciones `.tex` por capítulo (Cap. 4, 7, 8 y menciones).
2. Aplicar las correcciones T1–T7: Anexo §Corpus (T2), caps 5.5/8.1/9.1 con
   fallback (T4), ventana temporal + anti-Hawthorne en 4.2/4.4/4.5/11.5 (T6),
   instrumento único en 4.2/4.6/7.3 (T7), y caps 7.2/1.6 (T3, T1).
3. Consolidar docs de soporte (A1–A4) y alinear Anexo H.
4. Recompilar `main.pdf` (Overleaf XeLaTeX, no hay toolchain local).
5. Verificar: `rg` de términos stale (T1–T7), `openspec validate ... --strict` y
   compilación sin errores fatales.

Rollback: `git checkout --` de los archivos afectados o `git revert` del commit.

## Open Questions

- Ninguna abierta. La ventana temporal de T6 fue confirmada por el autor
  (manual jun–ago 2026; automatizado sep–oct 2026) y quedó resuelta en D9.
  D1–D10 resueltas; la metodología del tiempo quedó resuelta en D2/D3.
