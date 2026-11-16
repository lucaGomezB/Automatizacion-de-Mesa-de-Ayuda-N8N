## Why

La limitación 1 del estudio es la fragilidad de la referencia: kappa de `0,5569` y un árbitro
único (`E5`) que fija `64` de las `206` referencias con una regla no mayoritaria. Un análisis
offline sobre los artefactos ya versionados muestra que la regla vigente (consenso de `E3` y
`E4`; `E5` cuando difieren) coincide con la etiqueta mayoritaria de `{E3, E4, E5}` en `200` de
`206` casos. Solo `6` casos (`I033`, `I042`, `I056`, `I130`, `I194`, `I198`) tienen tres
etiquetas distintas. Reasignar esos `6` casos mueve la exactitud estricta de `142/206`
(`0,6893`) a `147/206` (`0,7136`), por debajo del umbral de `0,85`.

La línea de trabajo futuro de `10-recomendaciones.tex` que propone "arbitraje por mayoría de
tres" es un no-op sobre estos datos. El remedio real exige más etiquetadores independientes
(datos nuevos). Este change documenta el hallazgo y corrige la narrativa, sin modificar la
cifra primaria ni el veredicto del umbral.

## What Changes

- **Script offline (TDD)**: `analisis_arbitraje_mayoria_c224.py`, de solo lectura, que calcula
  la coincidencia (`200/206`), lista los `6` casos sin mayoría y acota la exactitud y las
  métricas por clase (`142/206` a `147/206`).
- **Memo canónico**: sección `3.35` aditiva en `numeros-canonicos.md` con fuente y comando.
- **Prosa**: `08-discusion.tex` (limitación 8) precisa que la regla vigente ya equivale a la
  mayoría en `200/206` casos; `07-resultados.tex` registra el rango de sensibilidad en el
  párrafo del arbitraje; `10-recomendaciones.tex` retira la propuesta de "arbitraje por mayoría
  de tres" y la sustituye por la necesidad de más etiquetadores independientes.
- **Trazabilidad**: sección de c-224 en `dictamen-correcciones.md`.

No se reabren mediciones, no se reclasifica, no se invoca a Gemini y no se altera ningún valor
vigente del memo, la cifra primaria `0,6893` ni el veredicto del umbral.

## Capabilities

### New Capabilities

Ninguna. El análisis se apoya en artefactos existentes y no introduce una capacidad nueva.

### Modified Capabilities

- `tesis-numeros-canonicos`: sección `3.35` aditiva con la coincidencia (`200/206`), los `6`
  casos y los rangos de exactitud y métricas por clase, con fuente y comando.
- `tesis-document`: precisión de la limitación 8, rango de sensibilidad en resultados y
  reformulación del trabajo futuro en recomendaciones.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/analisis/` | Nuevo | Script, pruebas, JSON, MD y SHA256SUMS (c-224) |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | Limitación 8 precisada |
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` | Modificado | Rango de sensibilidad en el párrafo del arbitraje |
| `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` | Modificado | Trabajo futuro: más etiquetadores, no mayoría de tres |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Modificado | Sección `3.35` aditiva |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Modificado | Matriz de trazabilidad `C24/…` |

Sin cambios en `App/`, `n8n/`, el clasificador, el corpus, las predicciones ni los artefactos
congelados.