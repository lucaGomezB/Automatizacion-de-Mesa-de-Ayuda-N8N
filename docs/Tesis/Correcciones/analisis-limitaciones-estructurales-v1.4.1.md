# Analisis de limitaciones estructurales (tesis v1.4.1)

- **Fecha**: 2026-11-15.
- **Origen**: exploracion OPSX sobre la tesis v1.4.1 y el dictamen CONEAU post-v1.3.0.
- **Alcance**: identificar que limitaciones estructurales pesan mas sobre la nota y que se puede hacer con los artefactos ya versionados, sin datos nuevos ni llamadas pagas a Gemini.
- **Regla**: todo lo propuesto se rotula como sensibilidad, reinterpretacion o analisis offline. Nada se presenta como medicion nueva.
- **Registro**: Engram `#2032` (proyecto `automatizacion-de-mesa-de-ayuda-n8n`).

## 1. Hallazgo verificable: el arbitraje por mayoria ya coincide con la regla vigente

La regla actual de la referencia arbitrada es: consenso de `E3` y `E4`; cuando difieren, decide `E5`. El dictamen la cuestiona porque un solo arbitro fija 64 de 206 casos.

Contra los artefactos versionados (`evaluation/data/campana/doble_etiquetado_arbitrado.csv`, 476 registros, y `evaluation/data/campana/arbitraje_tres_vias.json`):

- La regla vigente coincide con la etiqueta mayoritaria de `{E3, E4, E5}` en **200 de 206 casos**.
- Solo **6 casos** tienen tres etiquetas distintas y carecen de mayoria: `I033`, `I042`, `I056`, `I130`, `I194`, `I198`.
- El rango de la exactitud estricta al reasignar esos 6 casos va de `142/206` (`0,6893`) a `147/206` (`0,7136`). Todas las lecturas quedan por debajo del umbral `0,85`.

**Consecuencia**: la linea de trabajo futuro que propone "arbitraje por mayoria de tres" es un **no-op sobre estos datos**. El remedio real contra la fragilidad de la referencia exige mas etiquetadores independientes, es decir, datos nuevos. Lo que si se puede hacer ahora es declarar con precision que la regla vigente ya equivale a la mayoria en 200 de 206 casos y acotar el efecto de los 6 restantes.

## 2. Ranking de limitaciones por peso sobre la nota

| # | Limitacion | Criterio que afecta | Por que pesa | Mitigacion actual | Accion factible ahora | Esfuerzo |
|---|---|---|---|---|---|---|
| 1 | Referencia fragil: kappa `0,5569`; etiquetadores que son operadores y uno es autor; arbitro unico `E5` en 64/206 | c4 + c6 | Afecta la validez de todas las metricas de clasificacion | Limitacion 8; amenazas 2 y 8; sensibilidad de ruido de referencia | Acotar el arbitraje por mayoria y declarar el no-op (P1) | S |
| 2 | Ajuste y evaluacion sobre el mismo corpus (vocabulario y reglas del prompt) | c4 + c6 | Las metricas primarias son dentro de la muestra y probablemente optimistas | Limitacion 7; ablacion de prompt; vocabulario externo | Robustez de la linea de base frente a la eleccion de referencia (P2) | M |
| 3 | Muestra por conveniencia, una sola organizacion, `n = 200` | c2 + c4 + c7 | Limita validez externa y potencia | Limitaciones 1 y 2; amenazas 4 y 5 | No sin datos nuevos | — |
| 4 | Instrumentos asimetricos, orden fijo y llamadas recitadas | c4 | La reduccion de tiempos podria estar favorecida por el instrumento y el locutor | Seis explicaciones rivales en `08`; amenazas 1 y 6 | Consolidar una tabla de rango de robustez con todos los escenarios ya calculados (P4) | S |
| 5 | Arbitro unico `E5` e inestabilidad de la confianza (7 de 34 casos) | c6 | Acota la precision fuera de muestra | Amenaza 8; resultados linea 220 | Invariancia de la calibracion a las 7 diferencias (P3, opcional) | S |

## 3. Propuestas factibles

### P1. Acotar el arbitraje por mayoria (limitacion 1)

- Script offline nuevo (TDD) que lea `doble_etiquetado_arbitrado.csv` y `arbitraje_tres_vias.json` y calcule:
  - coincidencia entre la regla vigente y la mayoria de `{E3, E4, E5}` (200/206);
  - los 6 casos sin mayoria y su efecto minimo/maximo en la exactitud (`142/206` a `147/206`);
  - la tabla de metricas por clase bajo ambos extremos.
- Prosa: precisar la limitacion 8 y reformular la linea de trabajo futuro de `10-recomendaciones.tex` que hoy propone la mayoria de tres como si no existiera.
- No cambia la cifra primaria ni el veredicto del umbral.

### P2. Robustez de la linea de base frente a la referencia (limitacion 2)

- Extender el analisis ya versionado `evaluation/data/campana/analisis/contraste_linea_de_base_c213.py` a tres subconjuntos: consenso `E3`/`E4` (142), 150 originales sin exclusion y corpus arbitrado completo (206).
- Reportar la brecha hibrido vs linea de base en cada subconjunto, con IC.
- Prosa: una tabla o parrafo en resultados/discusion; la limitacion 5 y la 7 se mantienen, pero la conclusion sobre la linea de base deja de depender de una sola referencia.
- No requiere llamadas pagas: las predicciones de ambos clasificadores ya estan versionadas.

### P3. Invariancia de la calibracion a las 7 diferencias de confianza (limitacion 5, opcional)

- Recorrer las 7 diferencias de confianza entre corridas (`I026`, `I043`, `I050`, `I055`, `I067`, `I084`, `I085`) y recalcular el ECE, Brier y AUROC con cada escenario.
- Reportar el rango; si no cambia la conclusion cualitativa, declararlo.
- No es una remedicion: es un analisis de robustez sobre predicciones versionadas.

### P4. Consolidar el rango de robustez de tiempos (limitacion 4)

- Reunir en una sola tabla los escenarios ya calculados: descuento de 5 s y 10 s, desagregado por canal, por operador, efecto de posicion y la cota inferior del instrumento.
- Declarar el rango completo de la reduccion y el escenario que lo minimiza.
- Prosa: un parrafo en resultados y una remision desde la limitacion correspondiente.
- No mide de nuevo: sintetiza artefactos existentes.

### P5. Preservar el commit de la primera corrida fuera de muestra (limitacion de reproducibilidad)

- Change `c-223`: tag anotado `archivo/corrida-fuera-de-muestra-561b3c4`, declaracion en README y tesis, verificacion en clon limpio.
- No cambia ningun resultado.

## 4. Separacion por factibilidad

**(a) Genuinamente factible con datos existentes**

- P1, P2, P3, P4 y P5.

**(b) Parcialmente mitigable con un analisis nuevo**

- La fragilidad de la referencia: se acota con P1, pero no se elimina sin mas etiquetadores.
- El ajuste sobre el mismo corpus: se acota con P2 y con las sensibilidades ya existentes, pero no se elimina sin un corpus verdaderamente independiente.
- La asimetria de instrumentos y el orden fijo: se acotan con P4, pero no se eliminan sin remedir ambos brazos con el mismo instrumento y contrabalancear el orden.

**(c) No factible sin datos nuevos o trabajo humano**

- Una sola organizacion y `n = 200`.
- Reetiquetado independiente con mas etiquetadores.
- Remedicion de tiempos con el mismo instrumento.
- Llamadas con usuarios reales.
- Clasificador entrenado sobre el corpus acumulado en operacion.
- Brazo solo-LLM sobre los 206 casos.

## 5. Impacto esperado y techo

El criterio 4 (metodologia) concentra el peso. Sin evidencia nueva, las correcciones de redaccion y sensibilidad tienen un techo estimado de **~8,5**; la proyeccion del dictamen es **~8,57**. P1, P2 y P4 no suben el techo por si solas: reducen la percepcion de fragilidad y ordenan la evidencia para la defensa. La unica via para mover el techo es evidencia nueva (otra organizacion, mas etiquetadores, remedicion), que excede el alcance de esta entrega.

## 6. Changes recomendados

| Change | Limitacion | Alcance | Governance |
|---|---|---|---|
| `c-223-preservar-el-commit-de-la-corrida-fuera-de-muestra` | Reproducibilidad | Tag de archivo, README y declaracion en tesis | LOW/MEDIUM; HIGH para el tag |
| `c-224-acotar-el-arbitraje-por-mayoria` | 1 | Script offline + memo + prosa | MEDIUM |
| `c-225-robustez-de-la-linea-de-base-frente-a-la-referencia` | 2 | Extension del analisis de linea de base + prosa | MEDIUM |
| `c-226-consolidar-el-rango-de-robustez-de-tiempos` | 4 | Sintesis de sensibilidades + tabla | LOW/MEDIUM |

Nota de numeracion: la exploracion original reservaba `c-226` para la invariancia de calibracion (limitacion 5) y `c-227` para las cotas de tiempo. En esta sintesis se asigna `c-226` a la limitacion 4, que es la pedida; la limitacion 5 queda disponible como `c-227` si se decide abordarla.

## 7. Fuentes leidas

- `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (limitaciones y explicaciones rivales).
- `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (amenazas a la validez).
- `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (fuera de muestra, calibracion, linea de base).
- `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` y `10-recomendaciones.tex`.
- `auditorias/Dictamen_Tesis_v10_post-v1.3.0_5734ea8_CONEAU_2026-11-13.md`.
- `auditorias/Dictamen_Tesis_v10_v1.3.0_CONEAU_2026-11-13.md`.
- `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- `evaluation/data/campana/README.md` y artefactos de `evaluation/data/campana/analisis/`.

No se modifico ningun archivo durante la exploracion.