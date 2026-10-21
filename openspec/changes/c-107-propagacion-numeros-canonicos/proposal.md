# Proposal: c-107 — Propagación de los números canónicos a la tesis v9

## Why

El Gate 0 c-102 congeló la tabla canónica y marcó como `retirado` tres cifras que
la tesis v9 sigue citando como resultado: la intervención humana del `9,5 %`, el
universo calendario `3.700 = 42 × 88` y la proyección `45,0 h`. El dictamen CONEAU
2026-10-20 (recomendaciones obligatorias 1, 2 y 4) exige retirar la cifra del
9,5 % y reformular el aporte operativo si no se reconcilia con los datos, declarar
el estado de la hipótesis principal como parcialmente confirmada y parcialmente
refutada, y recalcular el universo y la proyección horaria o justificar el criterio
calendario. El autor confirmó las decisiones editoriales el 2026-10-21. Sin esta
propagación, el texto defiende un resultado operativo que su propia tabla de
calibración desmiente.

## What Changes

- **BREAKING (editorial): retirar el `9,5 %` de intervención humana.** Reformular
  el aporte operativo como intervención por gate NO MEDIDA en `07-resultados.tex`,
  `00-resumen.tex`, `08-discusion.tex`, `09-conclusiones.tex` y
  `10-recomendaciones.tex`; reconciliar `04-marco-metodologico.tex:61` ("sin
  intervención humana") con la definición de las dos dimensiones rotuladas.
- **Adoptar días hábiles como criterio de universo.** Reemplazar
  `3.700 = 42 × 88` por `≈ 2.646 = 42 × 63` y la proyección `45,0 h` por
  `≈ 32,2 h` en `04-marco-metodologico.tex:45`, `08-discusion.tex:14`,
  `08-discusion.tex:56`, `00-resumen.tex:11` y `01-introduccion.tex:18`.
- **Recalcular el margen de muestreo** de `04-marco-metodologico.tex:51` con
  `N ≈ 2.646` y actualizar las cifras de costo de API que usan `3.700` en
  `08-discusion.tex:56`.
- **Declarar el estado de la hipótesis principal** como parcialmente confirmada
  (tiempo) y parcialmente refutada (clasificación) en el resumen, la discusión y
  las conclusiones.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-numeros-canonicos`: se agrega la obligación de propagación de las ramas
  consumidoras — c-107 MUST reescribir los capítulos citando solo valores
  `vigente` y MUST NOT reintroducir los valores `retirado` del memo.
- `tesis-document`: se modifican el criterio de universo (días hábiles), el
  reporte de intervención humana (no medida), el margen de muestreo recalculado y
  la declaración del estado de la hipótesis principal.

## Impact

- Archivos de texto de la tesis en `docs/Tesis/v9 (IA)/paper/sections/`
  (`00`, `01`, `04`, `07`, `08`, `09`, `10`). No se toca código, API ni runtime.
- Fuente de verdad: `docs/Tesis/Correcciones/numeros-canonicos.md` (c-102, solo
  lectura en este change).
- Compilación: `latexmk` con Docker (`texlive-thesis`); el PDF debe seguir
  compilando y respetar el presupuesto de ≤ 100 páginas del plan (hoy 103).
- Governance: ALTO (afecta afirmaciones centrales de la tesis). Las decisiones
  editoriales y su reversibilidad se registran en `design.md`.
