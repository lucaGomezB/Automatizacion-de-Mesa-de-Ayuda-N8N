# Tasks — c-107 — Propagación de los números canónicos a la tesis v9

> Governance ALTO. Las decisiones editoriales y su reversibilidad están en
> `design.md`. NO se edita el memo canónico, `CHANGES.md` ni ningún archivo fuera
> de `docs/Tesis/v9 (IA)/paper/`.

## 0. Prerrequisitos (solo lectura)

- [ ] 0.1 Confirmar la fuente de verdad contra el memo canónico
  `docs/Tesis/Correcciones/numeros-canonicos.md` (Sección 3.4 y Sección 7) y
  registrar que c-102 está archivado.
- [ ] 0.2 Registrar el conteo de páginas de partida (`main.pdf` = 103) y la fecha
  de verificación (2026-10-21).
- [ ] 0.3 Confirmar con `git status` que el árbol está limpio antes de empezar.

## 1. Retiro del `9,5 %` y reformulación operativa (D1)

- [ ] 1.1 `07-resultados.tex:137-138`: reformular el párrafo para declarar el gate
  (`requiere_revision_humana = (confianza < 0,70)`), que no dispara casos en el
  corpus, y declarar la intervención por caso como NO MEDIDA. Eliminar `9,5 %`,
  `181 (90,5 %)` y `19`.
- [ ] 1.2 Verificar que `07-resultados.tex:155` (`19` aciertos por banda) queda
  INTACTO y que la Tabla 7.5 sigue mostrando `98/26/6/31/39`.
- [ ] 1.3 `00-resumen.tex:13`: eliminar el descenso "100 % → 9,5 %"; reformular el
  aporte operativo como no medido; declarar el estado parcial de la hipótesis.
- [ ] 1.4 `00-resumen.tex:25` (abstract): retirar `9.5 %` y alinear la redacción
  con el resumen en español (decisión D8).
- [ ] 1.5 `08-discusion.tex:14`: eliminar "reducción de la intervención humana al
  9,5 %"; reformular el aporte operativo.
- [ ] 1.6 `09-conclusiones.tex:16`: eliminar "la reducción de la intervención
  humana alcanzó el 9,5 %"; reformular el aporte operativo como no medido.
- [ ] 1.7 `10-recomendaciones.tex:24`: eliminar "en el 9,5 % de los casos" y
  reformular la frase sin la cifra retirada.
- [ ] 1.8 `04-marco-metodologico.tex:61`: reconciliar "sin intervencion humana"
  con la definición rotulada de las dos dimensiones; referir el gate.
- [ ] 1.9 `04-marco-metodologico.tex:34` y `04:65`: conservar las dos dimensiones
  rotuladas de la variable (casos y tiempo) y dejar 7.3 consistente con ellas.

## 2. Universo de días hábiles y proyección (D2)

- [ ] 2.1 `04-marco-metodologico.tex:45`: reemplazar `3.700` / `42 × 88` por
  `≈ 2.646` / `42 × 63` días hábiles.
- [ ] 2.2 `00-resumen.tex:11`: reemplazar "universo aproximado de 3.700" por `≈ 2.646`.
- [ ] 2.3 `00-resumen.tex:25` (abstract): reemplazar `approximately 3,700` por `≈ 2,646`.
- [ ] 2.4 `01-introduccion.tex:18`: reemplazar `45,0 horas-persona` por `32,2 horas-persona`.
- [ ] 2.5 `08-discusion.tex:14`: reemplazar `3.700` por `≈ 2.646` y `45,0 h` por
  `≈ 32,2 h`; actualizar el footnote del cálculo.
- [ ] 2.6 `08-discusion.tex:56`: reemplazar `3.700 incidentes trimestrales` por
  `≈ 2.646` y `45,0 horas-persona` por `≈ 32,2 h`.

## 3. Margen muestral y costo de API (D3, D4)

- [ ] 3.1 `04-marco-metodologico.tex:51`: reemplazar `N = 3.700` por `N ≈ 2.646` y
  `6,74 %` por `6,66 %`; conservar la variante de la fórmula con corrección por finitud.
- [ ] 3.2 Verificar la aritmética: `n0 = 200 × 2645 / 2446 = 216,27`;
  `e = √(0,9604/216,27) = 0,0666`; `n = 216,27/(1 + 215,27/2.646) = 200,0`.
- [ ] 3.3 `08-discusion.tex:56`: recalcular el costo de API con `2.646 × 0,345 ≈
  912,9` invocaciones y `≈ 7×10⁻⁴ USD`; conservar el porcentaje `34,5 %`, los
  supuestos de tokens y la cota de `2 USD`.

## 4. Estado de la hipótesis principal (D5)

- [ ] 4.1 `00-resumen.tex`: declarar la hipótesis como parcialmente confirmada
  (tiempo) y parcialmente refutada (clasificación); no permitir leer confirmación plena.
- [ ] 4.2 `08-discusion.tex:8` y el cierre de 8.1: declarar el estado parcial.
- [ ] 4.3 `09-conclusiones.tex:6` (y el resto del capítulo): declarar el estado parcial.

## 5. Verificación de propagación

- [ ] 5.1 Buscar `9,5 %`, `9.5 %`, `181`, `19` (fuera de `07:155`), `3.700`,
  `3,700` y `45,0` en `sections/*.tex` y confirmar que no quedan como resultado.
- [ ] 5.2 Confirmar que ningún `.tex` fuera de `docs/Tesis/v9 (IA)/paper/` fue tocado.
- [ ] 5.3 Confirmar que `07-resultados.tex` conserva la Tabla 7.5 (`98/26/6/31/39`)
  y el tramo `46 casos ≥ 0,90 con 13 errores` sin cambios.

## 6. Compilación y presupuesto de páginas

- [ ] 6.1 Compilar con la imagen local:
  `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`.
- [ ] 6.2 Confirmar que no hay errores fatales y registrar el conteo de páginas.
  **Nota de presupuesto**: el plan exige ≤ 100 páginas y el PDF parte de 103. c-107
  no posee la reducción; MUST NOT aumentar el conteo. Si sube, usar la variante de
  redacción más corta.
- [ ] 6.3 Verificar que no quedan referencias indefinidas nuevas ni etiquetas rotas.

## 7. Verificación del change (OpenSpec)

- [ ] 7.1 Ejecutar `openspec validate c-107-propagacion-numeros-canonicos --strict`.
- [ ] 7.2 Ejecutar `openspec status --change c-107-propagacion-numeros-canonicos --json`
  y confirmar `isPlanningComplete: true`.
- [ ] 7.3 Confirmar con `git status` que NO se modificó el memo canónico, `CHANGES.md`
  ni `dictamen-correcciones.md`.
