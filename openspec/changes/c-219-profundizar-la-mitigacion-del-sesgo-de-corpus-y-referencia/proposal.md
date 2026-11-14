## Why

El dictamen CONEAU v1.3.0 (criterio 4, peso 20) descuenta por «ajuste y evaluación sobre el
mismo corpus» y por «referencia de verdad frágil», y declara que subir ese criterio **exige
evidencia nueva, no redacción** (`auditorias/Dictamen_Tesis_v10_v1.3.0_CONEAU_2026-11-13.md:182`).
c-142 acotó el sesgo del vocabulario con el vocabulario previo `V0`, pero su propia salvedad
admite que `V0` pudo ajustarse con el corpus y la tesis lo rotula «cota pesimista» e
«interpretación, no medición» (memo 3.10). c-216 acotó el ruido de la referencia por simulación,
pero no desagrega el desempeño según cuán robusta es la referencia. Este change produce evidencia
nueva, offline y reproducible sobre ambas amenazas sin cambiar ningún número canónico.

## What Changes

- **(a) Ablación con vocabulario independiente del corpus.** Construir un vocabulario
  *corpus-blind* a partir de una fuente externa documentada (taxonomía sectorial canónica más un
  glosario público de mesa de ayuda), fijado y versionado **antes** de medir. Re-medir la etapa
  determinística (cobertura, precisión y conjunto de cortocircuito) sobre los `206` casos
  arbitrados y cuantificar el sesgo «ajustado sobre el mismo corpus» frente al vocabulario vigente
  `V1`; la ablación de términos derivados del corpus (equivalente a `V0`) se reusa como control
  secundario.
- **(b) Análisis del subconjunto de alto acuerdo.** Reportar la exactitud estricta del clasificador
  sobre el subconjunto de consenso `E3 = E4` (`n = 142`) frente al subconjunto arbitrado por `E5`
  (`n = 64`) y frente a los `206`, acotando cuánto del resultado depende de la referencia.
- Sección canónica **3.29** aditiva, prosa en `04`/`07`/`08` y entrada en
  `dictamen-correcciones.md`.

**No objetivos:** no se reclasifica, reentrena, cambia el vocabulario vigente `V1`, el prompt, los
umbrales, el corpus, las predicciones ni ningún artefacto congelado; no hay trabajo de campo ni
corrida paga por defecto (ver OQ1).

## Capabilities

### New Capabilities
- `evaluation-corpus-bias-mitigation`: medición offline y reproducible de (a) el sesgo del
  vocabulario ajustado con el corpus y (b) la dependencia de la referencia vía el subconjunto de
  alto acuerdo, con entradas versionadas y salidas determinísticas.

### Modified Capabilities
- `tesis-numeros-canonicos`: sección aditiva 3.29 con archivo fuente, comando y SHA-256 por valor.
- `tesis-document`: método en `04`, subsección de resultados en `07` y lectura de limitación en `08`.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/analisis/` | Nuevo | Script de solo lectura, vocabulario corpus-blind versionado, JSON/MD y SHA-256 |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Modificado | Sección 3.29 aditiva |
| `docs/Tesis/v10 (IA)/paper/sections/{04,07,08}-*.tex` | Modificado | Método, resultados y discusión |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Modificado | Entrada y matriz de trazabilidad |
| `evaluation/data/campana/analisis/README.md` | Modificado | Registro de entradas, comando, salidas y pruebas |

## Risks and rollback

- Un vocabulario corpus-blind puede rendir muy por debajo y leerse como «accuracy corregida» →
  rotularlo como **sensibilidad/cota**, no como medición; informar cobertura y precisión por
  separado; declarar la independencia como **procedimental** (prerregistro), no de contenido.
- El subconjunto literal «`E3` = `E4` = `E5`» es vacío por construcción (`E5` solo etiquetó los
  `64` discordantes) → definir el alto acuerdo como el consenso `E3 = E4` (`n = 142`) y declarar
  el hallazgo del conjunto vacío.
- Rollback: `git revert` del script, del vocabulario, de los artefactos nuevos y de la sección del
  memo; no hay migración de datos ni cambio de configuración.

## Success Criteria

- [ ] El script reproduce `88/115` (etapa determinística) y `142/206` (híbrido) antes de medir, es
      determinista (dos corridas byte a byte) y no usa red ni Gemini.
- [ ] La ablación informa cobertura, precisión y delta de cortocircuito para `V1`, el vocabulario
      corpus-blind y el control `V0`, rotulados como sensibilidad.
- [ ] El subconjunto de alto acuerdo informa `109/142` frente a `33/64` frente a `142/206` con IC de
      Wilson y no afirma causalidad sobre la referencia.
- [ ] La sección 3.29 es aditiva y ningún valor `vigente` de las secciones 3.1 a 3.28 cambia.
- [ ] La tesis compila y crece a lo sumo dos páginas netas.
