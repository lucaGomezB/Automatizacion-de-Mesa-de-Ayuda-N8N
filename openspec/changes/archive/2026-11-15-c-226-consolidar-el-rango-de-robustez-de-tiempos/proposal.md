# Proposal: Consolidar el rango de robustez de los tiempos

## Why

La limitación 4 del estudio (instrumentos asimétricos, orden fijo de los brazos y 81 llamadas recitadas) pesa sobre el criterio 4 porque la reducción de tiempos podría estar favorecida por el instrumento y por el locutor. La tesis ya contiene las sensibilidades que la acotan ---descuentos de 5~s y 10~s, desagregado por canal, por operador, efecto de posición y la cota inferior del instrumento---, pero están dispersas entre resultados y discusión. El lector no ve un único rango de robustez, y cada explicación rival cita una cifra aislada.

La exploración `docs/Tesis/Correcciones/analisis-limitaciones-estructurales-v1.4.1.md` (sección 3, P4) propone reunir en una sola tabla los escenarios ya calculados, declarar el rango completo de la reducción y el escenario que lo minimiza. No hace falta medir de nuevo: los artefactos ya están versionados.

La corrección es de síntesis y de redacción. No introduce datos nuevos, no cambia la cifra primaria del `71,2~\%` y no modifica ningún valor canónico vigente.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Análisis offline** | Script de solo lectura `evaluation/data/campana/analisis/analisis_rango_robustez_tiempos_c226.py` (TDD) que consolida los escenarios ya calculados desde los artefactos versionados y emite `analisis_rango_robustez_tiempos_c226.{json,md,.SHA256SUMS.txt}`. Aborta si no reproduce los anclajes canónicos. Sin red, sin Gemini, sin medición nueva. | MEDIUM |
| **B. Memo canónico** | Sección aditiva con el primer número libre (hoy la última es `3.36`; esperado `3.37`) en `docs/Tesis/Correcciones/numeros-canonicos.md`, con cada escenario, su procedencia, su estado y el escenario que minimiza. | LOW |
| **C. Tesis** | Una tabla o párrafo de rango de robustez en `07-resultados.tex` (subsección de tiempos), una remisión desde las seis explicaciones rivales de `08-discusion.tex` y una precisión en la limitación correspondiente y en la amenaza 1 de `04-marco-metodologico.tex`. Todo rotulado como sensibilidad o reinterpretación, nunca como medición nueva. | MEDIUM |
| **D. Trazabilidad** | Entrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` con el change, el artefacto y las anclas de prosa. | LOW |

**No objetivos.**

- No se mide de nuevo, no se invoca a Gemini y no hay llamadas pagas.
- No se cambia la cifra primaria `71,2~\%` ni el intervalo `[67,2~\%; 74,6~\%]`; el rango de robustez se agrega alrededor de ella.
- No se modifica ningún valor ni estado de las Secciones 3.1 a 3.36 del memo; la sección nueva es aditiva.
- No se tocan `App/`, `n8n/`, el clasificador, el corpus, las predicciones ni los artefactos congelados.
- No se reabren las limitaciones estructurales que exigen datos nuevos (muestra por conveniencia, ajuste sobre el mismo corpus, remedición con el mismo instrumento, llamadas con usuarios reales).
- No se reescriben las secciones existentes de resultados y discusión; se agrega una síntesis y remisiones.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se modifica «Divulgacion del procedimiento de medicion de tiempos y analisis de sensibilidad» para exigir una síntesis única del rango de robustez, con los escenarios ya calculados, el escenario que lo minimiza, los rótulos de sensibilidad y la remisión desde la discusión y la limitación.
- `tesis-numeros-canonicos`: se agrega el requisito de registro aditivo del rango de robustez de tiempos, con procedencia, estado y comando por valor.

`evaluation-framework` no se modifica: el consolidado es un análisis de solo lectura que reutiliza `evaluation/stats.py` sin cambiarlo, y el contrato que importa es documental (la sección del memo).

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/analisis/` | Nuevo | Script, prueba, JSON, MD y manifiesto SHA-256 |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Sección nueva con los escenarios y el rango |
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` | Modificado | Tabla o párrafo de rango de robustez |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | Remisión desde las seis explicaciones rivales y precisión en la limitación |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | Precisión en la amenaza 1 (orden y efecto de posición) |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuración, el corpus ni las predicciones. Cero llamadas a Gemini.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Que la tabla se lea como una medición nueva o como un cambio de la cifra primaria | Media | Rótulo explícito de sensibilidad y encabezado que remite a los escenarios ya calculados; la cifra primaria permanece `71,2~\%` |
| Mezclar estimandos distintos (canal, operador, campaña complementaria) en un solo número | Alta | El design fija dos niveles: rango del estimando primario y cotas de alcance rotuladas; cada fila declara su ámbito |
| Duplicar cifras ya presentes y romper la regla de repetición acotada | Media | La tabla es la síntesis; las secciones existentes conservan sus cifras y solo reciben remisión |
| Colisión de numeración con la sección libre del memo | Media | Se fija el primer número libre al aplicar (tarea 0.5) |
| Crecimiento de páginas | Media | Tabla compacta o párrafo de una a dos oraciones; verificación de `\@abspage@last` |

## Rollback Plan

`git revert` del commit del change: el script y sus salidas son aditivos; la sección del memo se retira sin tocar las anteriores; la tabla y las remisiones se revierten por archivo. Ningún valor canónico previo se modifica, de modo que el rollback no deja huecos numéricos.

## Dependencies

- c-134 (sensibilidad de redondeo, granularidad y desagregado por canal), c-196 (tiempos por operador) y c-169 (campaña complementaria y efecto de posición).
- `docs/Tesis/Correcciones/analisis-limitaciones-estructurales-v1.4.1.md` (P4).
- No depende de c-223 ni de c-224/c-225.

## Success Criteria

- [ ] El script reproduce los anclajes canónicos antes de escribir y es determinista (dos corridas byte a byte).
- [ ] La tabla o párrafo declara el rango completo, el escenario que minimiza el estimando primario y las cotas de alcance, con rótulo de sensibilidad.
- [ ] La cifra primaria `71,2~\%` y su intervalo no cambian; `rg` confirma que no se introdujo otro valor como principal.
- [ ] `08-discusion.tex` remite desde las seis explicaciones rivales y la limitación precisa el alcance del rango.
- [ ] La sección nueva del memo no modifica las Secciones 3.1 a 3.36.
- [ ] `openspec validate c-226-consolidar-el-rango-de-robustez-de-tiempos --strict` pasa.