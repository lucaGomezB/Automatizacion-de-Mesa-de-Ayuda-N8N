# Proposal: c-76 — Alineación de la tesis con el corpus real y el dictamen CONEAU

## Why

La tesis LaTeX (`docs/Tesis/v9 (IA)/paper/`) todavía reporta los números y la
distribución del corpus **sintético descartado en C-27**: 3 clases (incluida la
categoría retirada "Operaciones"), exactitud 92 %, F1 macro 0,919 y un Wilcoxon
W=0 ("sin una sola excepción") que es falso. El dictamen CONEAU exige alinear el
documento, sus anexos y el PDF con el **corpus real** de 200 casos ya evaluado.

## What Changes

- **Cap. 7 (Resultados)**: reemplazar tiempos, métricas de clasificación, matriz
  5x5 y distribución por sector por los valores reales; declarar redondeo al alza
  y cota conservadora de sensibilidad; reportar 12/200 pares invertidos.
- **Cap. 4 (Marco metodológico)**: describir la construcción del corpus real
  (200 casos pseudonimizados, 5 sectores, canales correo/web/teléfono) y declarar
  el procedimiento de medición manual en vivo con redondeo al alza.
- **Cap. 8 (Discusión)** y capítulos que citan números (00-resumen,
  01-introducción, 05-arquitectura, 09-conclusiones): eliminar/reemplazar los
  números sintéticos y la categoría retirada "Operaciones".
- **Anexos y docs de soporte**: consolidar A1–A4 ya aplicados en disco (Anexo F,
  `evaluation/README.md`, `evaluation/data/README.md`, `README.md`); alinear
  Anexo H a `gemini-3.6-flash`; recompilar `main.pdf`.

### Grupo: Trazabilidad y existencia de datos experimentales (T1–T7)

- **T1 — Campaña experimental presentada como realizada**: ningún pasaje del
  Cap. 7 ni del Anexo F SHALL presentar la campaña como trabajo futuro o
  pendiente; se reporta como ejecutada sobre datos reales. (Anexo F ya corregido
  en A1.)
- **T2 — Anexo "Corpus de validación" stale**: `12-anexos.tex` §Corpus declara un
  CSV en `evaluation/data/` con 7 columnas. Se reescribe para apuntar al corpus
  real `data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y
  versionado); `evaluation/data/` no contiene corpus desde C-27.
- **T3 — Datos incorrectos en caps 7.2 y 1.6**: 7.2 reporta métricas/3 clases del
  corpus sintético; 1.6 conserva "tres sectores (Sistemas, Operaciones y Soporte
  Técnico)", "Gemini 2.5 Flash" y la fecha "junio de 2026".
- **T4 — Distribución de etapas + etapa fallback**: caps 5.5, 8.1 y 9.1 reportan
  "~62 % / 38 %" (o "seis de cada diez"). Real (`evaluation/report.md`):
  deterministic 131/200 = 65,5 %, Gemini 69/200 = 34,5 %, fallback 0. Se
  documenta la etapa fallback y el orden deterministic → Gemini → fallback.
- **T5 — Datos de tiempo (caps 7.1, 4.6, 4.7)**: ya cubierto por P1.0/P1
  (redondeo al alza + cota de sensibilidad); solo se referencia, sin nuevo
  requisito.
- **T6 — Anti-Hawthorne incompatible con la ventana temporal**: caps 4.2, 4.4,
  4.5 y 11.5 dan una ventana trimestral (jul–sep 2025) y a la vez "tres días
  hábiles", con una observación naturalista sin conocimiento del operador. Se
  unifica la ventana temporal real y se reconcilia la afirmación anti-Hawthorne
  con el procedimiento efectivo.
- **T7 — Tres relatos del instrumento manual**: caps 4.2, 4.6 y 7.3 describen de
  forma incompatible la planilla de cronometraje ("estimados" vs
  "cronometrados"; "exactitud al segundo" vs "sin fracciones") y 7.3 deriva la
  intervención del flujo automatizado de la planilla manual. Se unifica el
  relato y se elimina esa derivación.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: alineación de la tesis con el corpus real (métricas, matriz y
  distribución), divulgación del procedimiento de medición de tiempos,
  trazabilidad del corpus en el Anexo (§Corpus de validación), divulgación de las
  etapas del pipeline (incluida fallback), consistencia de la ventana temporal y
  reconciliación anti-Hawthorne, y un único relato del instrumento manual.
- `evaluation-framework`: divulgación del redondeo de tiempos manuales, reporte
  de la cota de sensibilidad y de los pares invertidos reales, y divulgación de
  la distribución de etapas del pipeline (deterministic/Gemini/fallback).

## Impact

Documentación y artefactos (SIN tocar `App/**`):
`docs/Tesis/v9 (IA)/paper/sections/*.tex` (00-resumen, 01-introduccion,
04-marco-metodologico, 05-arquitectura, 07-resultados, 08-discusion,
09-conclusiones, 11-aspectos-legales, 12-anexos), `main.pdf`,
`docs/anexo_f_corpus.md`, `docs/anexo_h_prompt_gemini.md`,
`evaluation/README.md`, `evaluation/data/README.md`, `README.md`,
`docs/Tesis/Correcciones/dictamen-correcciones.md`.

## Rollback Plan

`git checkout --` sobre los `.tex`, docs y `main.pdf` afectados, o `git revert`
del commit del change. Los artefactos OPSX viven bajo
`openspec/changes/c-76-tesis-correcciones-dictamen/` y se descartan con el
directorio.

## Success Criteria

- [ ] Cap. 7 reporta exactitud 73,5 % (147/200), macro-F1 0,5207 y matriz 5x5 real.
- [ ] La cadena "Operaciones" desaparece como sector en `.tex` y en el PDF.
- [ ] Tiempos reales declarados con redondeo al alza y cota conservadora (≥ 71,3 %).
- [ ] Wilcoxon W=335, p=2,05e-32, r=0,983 y 12/200 inversiones; sin "W=0".
- [ ] Anexo H usa `gemini-3.6-flash`; `main.pdf` recompilado sin errores fatales.
- [ ] Ninguna mención a un CSV en `evaluation/data/` ni a un corpus de 7 columnas
  (T2); el Anexo apunta al JSON pseudonimizado real.
- [ ] Etapas reportadas como 65,5 % deterministic / 34,5 % Gemini / fallback 0,
  con la etapa fallback documentada y su orden explicado (T4).
- [ ] Un único relato del instrumento manual: sin "estimados" vs
  "cronometrados", sin "exactitud al segundo" vs "sin fracciones" (T7).
- [ ] Sin "tres sectores" ni "Operaciones" como sector, y sin "Gemini 2.5 Flash"
  en el cuerpo de la tesis (T3).
- [ ] Ventana temporal unificada y anti-Hawthorne reconciliado (T6); campaña
  presentada como realizada (T1).
- [ ] `openspec validate c-76-tesis-correcciones-dictamen --strict` pasa.
