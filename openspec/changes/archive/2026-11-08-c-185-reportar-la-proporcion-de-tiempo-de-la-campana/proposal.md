## Why

El marco metodológico anuncia la "proporción del tiempo" como la segunda dimensión
rotulada de la variable de intervención humana (`04-marco-metodologico.tex:69`), y la
spec principal de `tesis-document` ya obliga a reportarla con su intervalo bootstrap,
pero el valor NO aparece en ningún lado del cuerpo de la tesis: las subsecciones de
resultados reportan la proporción de casos (73,5 %) y omiten la proporción de tiempo.
El change c-169 (aplicado y archivado) dejó esa omisión como unidad propia.

## What Changes

- Reportar en `07-resultados.tex` (`subsec:reduccion-intervencion`, junto a la
  proporción de casos) la proporción de tiempo de la campaña complementaria:
  estimación `0,5307`, IC bootstrap `[0,4407; 0,6111]` (`B = 2000`, semilla
  `20261021`), cobertura `0,9388` (147 casos intervenidos, 138 con duración completa) y
  la limitación del denominador.
- Desambiguar `04-marco-metodologico.tex:69` para precisar el denominador medido y
  remitir a los resultados.
- Valores FIJOS tomados del memo canónico (Sección 3.14, rama (b') "estimable"): no se
  inventan, recalculan ni alteran. El memo ya registra los valores; no se edita.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `tesis-document`: se refuerza el requisito "Reporte de la tasa de intervencion humana
  de la campaña de medicion" para exigir de forma explícita el valor puntual de la
  proporción de tiempo, su intervalo bootstrap del cociente, la cobertura observada y la
  limitación del denominador, con un escenario que fija los valores observados.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (`subsec:reduccion-intervencion`).
- `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (línea 69).
- Sin impacto en código, API, datos ni migraciones. Governance LOW (documentación).
- Posible aumento de páginas por la oración nueva (ver `design.md`); coordinar con c-184
  (recorte de páginas), que corre en paralelo.
