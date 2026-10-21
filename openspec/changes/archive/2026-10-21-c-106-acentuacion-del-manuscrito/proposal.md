# Proposal: c-106 — Acentuación normalizada del manuscrito y resumen ≤ 250 palabras

## Why

El dictamen CONEAU 2026-10-20 (dimensión 1, recomendación obligatoria 8) observa
una acentuación irregular en todo el manuscrito: conviven títulos acentuados con
centenares de ocurrencias sin tilde en el cuerpo ("realizandose", "informaticos",
"clasificacion", "Capitulo"). Además, el resumen en español tiene 538 palabras
frente a un límite declarado de 250, y el abstract 292. Son defectos objetivos de
disciplina formal que un jurado adversarial detecta de inmediato. c-103 (portada y
remisiones) difirió explícitamente las tildes a c-106.

## What Changes

- Normalizar la acentuación del texto español en los 14 archivos de
  `docs/Tesis/v9 (IA)/paper/sections/*.tex`, **sin tocar** tokens protegidos
  (cadenas de categorías sin tilde, claves de `\label`/`\ref`/`\autoref`/`\cite`,
  rutas, código, URLs/DOI, matemática, palabras ya correctas).
- Reducir el resumen en español (`00-resumen.tex`) a **≤ 250 palabras**,
  conservando problema, método, resultados y conclusión.
- Alinear el abstract en inglés (`00-resumen.tex:25`) al mismo presupuesto y a la
  misma información que el resumen reducido.
- **BREAKING (editorial): no**. No se alteran cifras, claims ni estructura.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se agrega la obligación de acentuación normalizada con tokens
  protegidos, el presupuesto de ≤ 250 palabras del resumen y la consistencia del
  abstract con el resumen reducido.

## Impact

- Texto de la tesis en `docs/Tesis/v9 (IA)/paper/sections/` (14 archivos). No se
  toca código, API, runtime, `Bibliography_base.bib` ni la ruta `docs/Tesis/`.
- Herramienta auxiliar existente: `docs/Tesis/acentuar_tesis.py` (evaluada en
  `design.md`; requiere adaptación, no es usable tal cual).
- Compilación con la imagen local `texlive-thesis`; el PDF (hoy 103 páginas) debe
  seguir compilando sin errores fatales y no aumentar su conteo de páginas.
- Governance: BAJO/MEDIO (texto del manuscrito; sin efecto en el sistema).
- **Secuenciación**: c-106 MUST aplicarse **después** de los changes que editan
  prosa en `sections/*.tex` (c-104 bibliografía, c-105 reubicación del cap. 11,
  c-107 números canónicos y los planificados c-108/c-109/c-110). La reducción del
  resumen MUST ocurrir después de c-107, que también edita `00-resumen.tex`.
