# Números canónicos de la tesis (versión de trabajo v10, release prevista `v1.2.0`) — Gate 0 (c-102)

**Este documento es la Fuente Única de Verdad numérica de la tesis.** Todo valor
numérico que la tesis v9 cite en los capítulos `04-marco-metodologico.tex`,
`07-resultados.tex`, `08-discusion.tex` y `09-conclusiones.tex` —y cualquier
rama de corrección que los reescriba, incluida c-104— MUST tomar su valor de la
tabla canónica de la Sección 3. Ninguna rama puede fijar, redefinir ni redondear
un número por separado: toda divergencia se resuelve actualizando este memo, no
el capítulo de forma aislada (ver `spec.md`, requisito "Gate 0 como prerrequisito
de las ramas consumidoras").

- **Change**: `c-102-congelar-numeros-canonicos-tesis` (Gate 0 del plan de corrección del dictamen CONEAU 2026-10-20).
- **Upsert c-108**: `c-108-metricas-paradigma-y-clase-unitaria` agrega la Sección 3.6 (marco métrico unificado e intervalos de confianza: por clase, de conjunto y del kappa). No modifica ningún valor canónico de la Sección 3. Fecha: 2026-10-21.
- **Upsert c-130**: `c-130-gate-revision-humana-por-etapa` agrega la Sección 3.7 (gate de revisión por etapa y punto de operación del cortocircuito), un punto en la Sección 4 (alcance del gate por etapa) y el punto 7 de la Sección 7 (procedencia de la cache FORCE-ESCALATE y salvedad de estimación dentro de la muestra). No modifica ningún valor vigente de las Secciones 3.1 a 3.6. Fecha: 2026-10-25.
- **Upsert c-134**: `c-134-contrastes-estadisticos-y-desagregado-canal` (bloque de código, aplicado el 2026-10-25) agrega la Sección 3.8 (tiempos por canal, contrastes, `d_z`, efecto mínimo detectable, sensibilidad del redondeo y granularidad de la medición manual), notas de convención bilateral en dos filas de la Sección 3.1 y actualiza las remisiones `report.md:99` → `report.md:140` (la línea del SHA-256 se desplazó al agregarse tres subsecciones a "## Tiempos"). No modifica ningún valor vigente de las Secciones 3.1 a 3.7. Los números de sección siguientes se corren (ver `dictamen-correcciones.md`, G0.6). El bloque de tesis de c-134 (grupos 6 a 8, aplicado el 2026-10-25) cita estos valores en `04-marco-metodologico.tex`, `07-resultados.tex`, `08-discusion.tex`, `01-introduccion.tex`, `11-aspectos-legales.tex` y `00-resumen.tex`, agrega a la Sección 3.8 la tabla de cifras con redondeo de tesis y no modifica ningún valor `vigente`.
- **Upsert c-131**: `c-131-metricas-por-etapa-canal-y-exactitud-laxa` (aplicado el 2026-10-25) agrega la Sección 3.9 (exactitud estricta y laxa por etapa y por canal con IC de Wilson, bandas, contingencia, tramo `≥ 0,90` y distribución de confianza por etapa, contraste pareado de McNemar entre etapas y decisión de datos PROVISIONAL), anota en las Secciones 3.3, 4 y 5 (ítem 2) que el contraste agregado `0,697` frente a `0,758` es un efecto de composición entre etapas y registra como `retirado` la lectura de anti-calibración del clasificador en su conjunto. Como el reporte regenerado agrega la línea de procedencia, la exactitud laxa y cuatro secciones antes de `## Tiempos`, **actualiza todas las remisiones `report.md:<línea>`** de este memo (la línea del SHA-256 pasa de `140` a `256`; verificado por correspondencia de contenido línea a línea con el reporte previo). No modifica ningún valor `vigente` de las Secciones 3.1 a 3.8.
- **Upsert c-142**: `c-142-sensibilidad-fuera-de-muestra-ajustes-clasificador` (aplicado el 2026-10-25) agrega la Sección 3.10 (sensibilidad de las métricas frente al ajuste del clasificador con el corpus: variante principal con el vocabulario previo a c-71, descomposición pareada, control de fidelidad de la réplica histórica, E3, E4 y niveles del prompt), notas "estimación dentro de la muestra; ver sección 3.10" en las filas de `97/131`, `0,7405` y `0,6769` y los puntos 8 y 9 de la Sección 7. No modifica ningún valor `vigente` de las Secciones 3.1 a 3.9. Fecha: 2026-10-25.
- **Upsert c-132**: `c-132-balance-neto-derivaciones-erroneas` (aplicado el 2026-10-25) agrega la Sección 3.11 (balance neto trimestral entre el ahorro bruto de registro y el costo de las derivaciones erróneas: insumos con procedencia, fórmulas de `B` y de la exactitud mínima de equilibrio `a*`, tabla de escenarios, escenario central, lectura laxa, comando de referencia y redondeo; todo valor derivado de supuestos con estado `condicional`). No modifica ningún valor `vigente` de las Secciones 3.1 a 3.10. Fecha: 2026-10-25.
- **Upsert c-133**: `c-133-hipotesis-objetivos-metrica-primaria` (aplicado el 2026-10-25) pasa el macro-F1 de umbral de las cuatro clases estimables (`0,6508`) de `condicional` a `vigente` (Sección 3.2), agrega los porcentajes `65,5 %` y `34,5 %` a la Sección 3.3, agrega la Sección 3.12 (cota de la segunda sub-hipótesis y contraste acotado de la hipótesis subsidiaria de eficiencia, con el estado que fija la regla de decisión frente a la variante E4 de c-142) y anota el ítem 5 de la Sección 5 y el punto 4 de la Sección 7. No modifica ningún otro valor `vigente`. Fecha: 2026-10-25.
- **Consolidación c-141** (`c-141-integracion-release-v1-2-0`, tramo de integración; fecha de consolidación: 2026-10-26; versión de trabajo de la tesis: v10; release prevista: `v1.2.0`): verifica que las Secciones 3.7 a 3.12 (c-130, c-134, c-131, c-142, c-132, c-133, en ese orden de aplicación) son únicas y consecutivas y que toda remisión "ver sección 3.N" resuelve; que los números de resultado agregados a `sections/*.tex` por la familia c-130..c-142 (diff contra `v1.1.1`) figuran en alguna sección con procedencia y estado (los redondeos de la tesis a tres decimales o a un decimal porcentual derivan de valores de cuatro decimales ya registrados; los valores de la literatura citados en `tab:trabajos-academicos` tienen su procedencia en `extraccion-metricas-trabajos-c-135.md`); que ninguna corrida de sensibilidad de c-142 cambió un valor `vigente` (las tres filas reformuladas por c-142 conservan valor y estado); y refresca las referencias `archivo:línea` a `sections/*.tex` de las filas `vigente` que el desplazamiento de líneas de la familia había dejado desfasadas (solo el número de línea; ningún valor ni estado cambia). El item 6 de la Sección 7 (conjunto de preproducción, c-144) se conserva sin renumerar. Fecha de consolidación: 2026-10-26.
- **Upsert c-145**: `c-145-correccion-factual-sincronizacion-del-memo-y-portabilidad-del-harness` (aplicado el 2026-10-26) registra el margen de error `6,66 %` como `vigente` con `N ≈ 2.646`, `z = 1,96`, `p = 0,5` y `n = 200` (Sección 3.4), marca `6,74 %` / `N = 3.700` como `retirado` y actualiza el punto 2 de la Sección 7 y la advertencia de arrastre del ítem 4. Además corrige por correspondencia de contenido las referencias `07-resultados.tex:<línea>` desfasadas (mínimo `:129 → :128`, `:75 → :74`, `:167-188 → :166-187` y `:179-183 → :178-182`) y la fila retirada del `9,5 %` que citaba `:160`. No modifica ningún otro valor `vigente`. Fecha: 2026-10-26.
- **Artefacto**: este memo. No se edita ningún `.tex` en este change.
- **Fecha de verificación**: 2026-10-21.
- **SHA-256 del corpus** (`data/corpus_evaluacion_pseudonimizado.json`):
  `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`.
- **Método**: recálculo de solo lectura desde `evaluation/predicciones.json`
  (200 predicciones) y `data/corpus_evaluacion_pseudonimizado.json`, usando las
  funciones puras de `evaluation/metrics.py`. NO se re-ejecutó el clasificador;
  NO hubo llamadas a Gemini, N8N ni Twilio.

## 1. Propósito y alcance

El dictamen CONEAU 2026-10-20 declaró contradicciones numéricas internas
bloqueantes para la defensa. Este memo las reconcilia o las declara no
resolubles con la evidencia disponible, y fija la tabla canónica que las ramas
posteriores deben citar. Los siete puntos del alcance son:

1. Gate de intervención humana.
2. Etapas `131/69` frente a las bandas de confianza.
3. Tramo "46 casos ≥ 0,90 con 13 errores".
4. Universo y proyección horaria.
5. Paradigma métrico (monoetiqueta frente a multietiqueta).
6. Clase `Bases de Datos` con `n = 1`.
7. Tabla canónica final (Sección 3).

## 2. Procedimiento de recálculo (solo lectura, reproducible)

Todas las métricas se reproducen sin invocar el clasificador, desde
`evaluation/predicciones.json` y el corpus. Campos usados: `sector_asignado`
(verdad principal), `sector_predicho` (etiqueta principal emitida),
`confianza`, `etapa`, `sectores_adicionales` (etiquetas **predichas**
adicionales). La verdad multietiqueta proviene del corpus
(`CasoEvaluacion.conjunto_verdad = {sector_asignado} ∪ sectores_adicionales` del
caso), no del archivo de predicciones.

Comando de referencia (desde la raíz del repositorio, para que `evaluation`
resuelva como paquete):

```bash
python3 -c "
import json
from evaluation import metrics as m
from evaluation.corpus import cargar_corpus
preds = json.load(open('evaluation/predicciones.json'))['predictions']
casos = cargar_corpus('data/corpus_evaluacion_pseudonimizado.json')
conf=[p['confianza'] for p in preds]; real=[p['sector_asignado'] for p in preds]
pred=[p['sector_predicho'] for p in preds]
print(m.calibracion_por_bandas(conf, real, pred))
print(m.contingencia_confianza(conf, real, pred, 0.70))
cv=[c.conjunto_verdad for c in casos]
cp=[frozenset(e for e in (p['sector_predicho'],*p['sectores_adicionales']) if e in m.CLASES) for p in preds]
print(m.exactitud_subconjunto(cv,cp), m.perdida_hamming(cv,cp), m.f1_micro(cv,cp))
"
```

- `calibracion_por_bandas` y `contingencia_confianza` son las funciones
  existentes de `evaluation/metrics.py` (probadas en
  `evaluation/tests/test_calibracion_confianza.py`); no se reimplementaron.
- La verdad multietiqueta se carga con `evaluation.corpus.cargar_corpus` y las
  métricas de conjunto con `exactitud_subconjunto`, `perdida_hamming`, `f1_micro`
  y `jaccard_promedio`.

## 3. Tabla canónica

Estados: `vigente` (valor citable), `retirado` (desmentido o reemplazado; NO
citable como resultado) y `condicional` (depende de una decisión editorial).

### 3.1 Tiempos y contraste

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Tiempo manual medio: `61,6 s` | `07-resultados.tex:10`, `07-resultados.tex:21`, `00-resumen.tex:13` | vigente | Medición por caso; reemplaza la estimación preliminar de 2 min 45 s (`01-introduccion.tex:18`). |
| Tiempo automatizado medio: `17,76 s` | `07-resultados.tex:10`, `07-resultados.tex:21`, `00-resumen.tex:13` | vigente | Mediana `17,47 s` (`07-resultados.tex:22`). |
| Reducción relativa de tiempo: `71,2 %` | `07-resultados.tex:10`, `07-resultados.tex:21`, `08-discusion.tex:8` | vigente | Cota superior (manual redondeado al alza, `07-resultados.tex:61`). |
| Reducción media por incidente: `43,82 s` | `report.md:199` | vigente | El `.tex` la aproxima como `43,8 s` (`07-resultados.tex:59`). |
| Wilcoxon `W = 363` | `07-resultados.tex:57`, `00-resumen.tex:13` | vigente | `W = min(T+, T−)`, dos colas (`report.md:185`). Contraste **bilateral**, conservador frente a `H1` direccional (c-134; ver Sección 3.8). |
| `T+ = 19.737`, `T− = 363` | `report.md:189`, `07-resultados.tex:57` | vigente | |
| p-valor `p = 3,08e-32` | `07-resultados.tex:57`, `01-introduccion.tex:32` | vigente | **Bilateral** (conservador frente a `H1: M_manual > M_automatizado`); el `p` unilateral es `1,54e-32` (Sección 3.8, `report.md:239`). |
| Tamaño del efecto `r = 0,9639` | `07-resultados.tex:59`, `07-resultados.tex:59`, `00-resumen.tex:13` | vigente | |
| Pares a favor `188 / 200` (`94,0 %`) | `07-resultados.tex:57`, `09-conclusiones.tex:41` | vigente | Pares no a favor: `12` (`report.md:202`). |

### 3.2 Clasificación (métricas)

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Exactitud estricta: `0,7350` (`73,5 %`; `147/200`) | `report.md:20`, `07-resultados.tex:128`, `07-resultados.tex:74` | vigente | Métrica primaria monoetiqueta. |
| IC Wilson 95 %: `[0,6698; 0,7913]` (`[67,0 %; 79,1 %]`) | `report.md:22`, `07-resultados.tex:128` | vigente | |
| Macro-F1 (5 clases): `0,5207` | `report.md:62`, `07-resultados.tex:128`, `08-discusion.tex:32` | vigente | Valor informativo; incluye la clase no estimable. Informativa; toda cita lleva su aclaración (c-133). |
| Macro-F1 (4 clases estimables): `0,6508` | recálculo (`metrics.py`) | vigente | Primaria de umbral (c-133 D1); excluye `Bases de Datos`. Único referente del criterio `0,85`; ambos macro-F1 quedan por debajo de `0,85`. |
| Micro-F1 (multietiqueta): `0,6654` | `report.md:61`, `07-resultados.tex:128` | vigente | Métrica multietiqueta; NO es equivalente de la exactitud. |
| Subset accuracy: `0,43` | `report.md:59`, `07-resultados.tex:128` | vigente | Contra la referencia multietiqueta. |
| Hamming loss: `0,3586` | `report.md:60`, `07-resultados.tex:128` | vigente | Contra la referencia multietiqueta. |
| Jaccard (IoU) promedio: `0,6414` | `report.md:63` | informativo | No citado en los `.tex` del alcance. |
| F1 por clase | `report.md:51-55`, `07-resultados.tex:141-145` | vigente | Hardware `0,8800`; Software `0,7111`; Seguridad `0,6122`; Sistemas `0,4000`; Bases de Datos `0,0000`. |

### 3.3 Pipeline y confianza

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Etapa determinística: `131` | `report.md:11`, `07-resultados.tex:128` | vigente | |
| Etapa Gemini: `69` | `report.md:12`, `07-resultados.tex:128` | vigente | |
| Etapa fallback: `0` | `report.md:13` | vigente | |
| Casos resueltos por la etapa determinística: `65,5 %` (`131/200`) | `evaluation/report.md:11` (actual; los design de c-133 citan `:9-10`, obsoleto), `08-discusion.tex:10,58` | vigente | Cociente de los `131` casos de la etapa determinística sobre `200`; registrado por c-133. |
| Casos que llegan a la etapa Gemini: `34,5 %` (`69/200`) | `evaluation/report.md:12`, `08-discusion.tex:10,58` | vigente | Complemento de `65,5 %`; registrado por c-133. |
| Bandas de confianza: `98 / 26 / 6 / 31 / 39` | `07-resultados.tex:178-182` | vigente | Reproduce la Tabla 7.5 (`07-resultados.tex:166-187`). **Efecto de composición (c-131):** las bandas bajas son solo de la etapa determinística y las altas casi solo de Gemini; su desglose por etapa figura en la Sección 3.9. |
| Tramo confianza `≥ 0,90`: `46` casos, `13` errores | `07-resultados.tex:189` | vigente | Ver Sección 5, ítem 3. Por etapa (c-131): Gemini `45` casos y `13` errores; determinística `1` caso y `0` errores (Sección 3.9). |

### 3.4 Intervención humana, universo y proyección

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Intervención humana: `9,5 %` (`19/200`; `181/200` sin intervención) | `07-resultados.tex:157-159`, `00-resumen.tex:13`, `08-discusion.tex:14`, `09-conclusiones.tex:16`, `10-recomendaciones.tex:24` | **retirado** | Valor heredado del corpus sintético descartado en C-27 (2026-09-11), sin re-medir (`knowledge-base/01_vision_y_objetivos.md:39,44`; `knowledge-base/README.md:32`); NO derivable del corpus real. La remisión apunta a la sección que declara la intervención como no medida (`:157-159`); el valor retirado ya no figura en el `.tex`. Ver Sección 7. |
| Universo calendario: `3.700 = 42 × 88` | `04-marco-metodologico.tex:45`, `04-marco-metodologico.tex:51` | **retirado** | Criterio incoherente con la tasa diaria de origen semanal. |
| Universo días hábiles: `≈ 2.646 = 42 × 63` | recálculo (`88 × 5/7 ≈ 62,86 ≈ 63` días hábiles) | vigente | Valor canónico propuesto (decisión D5). |
| Margen de error (corrección por finitud): `6,66 %` | `04-marco-metodologico.tex:51`; recálculo con `n = n₀/[1+(n₀−1)/N]`, `n₀ = z²p(1−p)/e²`, `z = 1,96`, `p = 0,5`, `n = 200`, `N ≈ 2.646` | vigente | Upsert c-145 (2026-10-26). Con esos insumos la fórmula reproduce `n ≈ 200,2`. Ver Sección 7, punto 2. |
| Margen de error (calendario): `6,74 %` | `04-marco-metodologico.tex:51` (histórico; calibrado con `N = 3.700`) | **retirado** | Reemplazado por `6,66 %` con `N ≈ 2.646` (upsert c-145). Se conserva solo para trazabilidad; no citar como vigente. |
| Proyección calendario: `45,0 h` | `08-discusion.tex:14`, `01-introduccion.tex:18` | **retirado** | `43,82 × 3.700 / 3.600 = 45,04 h`. |
| Proyección días hábiles: `≈ 32,2 h` | recálculo | vigente | `43,82 × 2.646 / 3.600 = 32,21 h`. |

### 3.5 Referencias de corpus

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| SHA-256 del corpus | `report.md:256` | vigente | `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`. |
| Tamaño del corpus: `n = 200` | `report.md:3`, `04-marco-metodologico.tex:45` | vigente | |
| Kappa de Cohen: `0,87` (doble etiquetado) | `00-resumen.tex:11` | vigente | Contexto de validez; no es una métrica del clasificador. Su IC **no es computable** desde las fuentes permitidas (ver 3.6). |
| Soporte `Bases de Datos`: `n = 1` | `report.md:54`, `08-discusion.tex:24` | vigente | Clase NO estimable (`F1 = 0,0000`). Ver ítem 6. |

### 3.6 Marco métrico unificado e incertidumbre (c-108)

**Paradigma.** La referencia de verdad del corpus es **multietiqueta**
(`107/200 = 53,5 %` de los casos tienen más de un sector de verdad). El
clasificador emite **una etiqueta principal** (monoetiqueta) y, en `8` casos,
etiquetas adicionales predichas. Las métricas primarias se calculan contra la
etiqueta principal (monoetiqueta); las secundarias, contra la referencia
multietiqueta del corpus. Se enuncian en un único marco:

| Métrica | Valor | Referencia de verdad | Rol | Nota |
|---|---|---|---|---|
| Exactitud estricta | `0,7350` (`147/200`) | Monoetiqueta (etiqueta principal) | Primaria | IC Wilson 95 % `[0,6698; 0,7913]`. |
| Macro-F1 (4 clases estimables) | `0,6508` | Monoetiqueta (etiqueta principal) | Primaria de umbral | Excluye `Bases de Datos` (`n = 1`). |
| Macro-F1 (5 clases) | `0,5207` | Monoetiqueta (etiqueta principal) | Informativa | Incluye la clase no estimable. |
| Micro-F1 | `0,6654` | Multietiqueta | Secundaria | **NO** es equivalente de la exactitud estricta (`0,6654 ≠ 0,7350`): acumula TP/FP/FN por etiqueta, no por caso. |
| Subset accuracy | `0,43` | Multietiqueta | Secundaria | Penaliza estructuralmente una salida forzada a una etiqueta. |
| Hamming loss | `0,3586` | Multietiqueta | Secundaria | Ídem; promedio por caso de etiquetas erróneas sobre la unión del caso. |

**Intervalos de confianza por clase (una contra el resto).** Precisión y
sensibilidad se estiman con el IC de Wilson; F1 con bootstrap percentil a nivel
de caso. Nivel de confianza 95 %. Procedencia:
`evaluation/metrics.py::intervalos_por_clase` (semilla `20261021`,
`B = 2.000`).

| Clase | n | Precisión (IC 95 %) | Sensibilidad (IC 95 %) | F1 (IC 95 %) | Estado |
|---|---|---|---|---|---|
| Soporte Técnico Hardware | 85 | `0,8556` `[0,7684; 0,9136]` | `0,9059` `[0,8251; 0,9515]` | `0,8800` `[0,8235; 0,9257]` | vigente |
| Soporte Técnico Software | 67 | `0,7059` `[0,5889; 0,8008]` | `0,7164` `[0,5991; 0,8103]` | `0,7111` `[0,6140; 0,7951]` | vigente |
| Seguridad Informática | 31 | `0,8333` `[0,6078; 0,9416]` | `0,4839` `[0,3197; 0,6516]` | `0,6122` `[0,4444; 0,7500]` | vigente |
| Sistemas | 16 | `0,3684` `[0,1915; 0,5896]` | `0,4375` `[0,2310; 0,6682]` | `0,4000` `[0,1600; 0,5882]` | vigente |
| Bases de Datos | 1 | no estimable | no estimable | no estimable | **no estimable** |

La clase `Bases de Datos` (`n = 1`) es **no estimable**: sin IC, excluida del
macro-F1 de umbral. Su valor puntual `0,0000` NO se presenta como evidencia de
desempeño del clasificador.

**Intervalos de confianza de las métricas de conjunto.** Bootstrap percentil a
nivel de caso (remuestreo de los 200 casos con sus conjuntos verdad y predicho),
misma semilla y `B` que los IC por clase. Procedencia:
`evaluation/metrics.py::intervalos_conjunto`.

| Métrica | Valor puntual | IC 95 % | Estado |
|---|---|---|---|
| Subset accuracy | `0,43` | `[0,3600; 0,4950]` | vigente |
| Hamming loss | `0,3586` | `[0,3125; 0,4058]` | vigente |
| Micro-F1 | `0,6654` | `[0,6224; 0,7061]` | vigente |

**IC del coeficiente kappa — no computable.** El kappa `0,87` proviene del doble
etiquetado independiente, pero **no existe registro por caso de los dos
analistas** en las fuentes permitidas: `data/Corpus Tesis - Hoja 1.csv` y su
versión pseudonimizada tienen las columnas `ID`, `Descripcion`, `Canal de
Origen`, `Sector Asignado`, `Sectores Adicionales` y tiempos, sin columnas de
doble etiquetado por analista; `evaluation/` solo conserva el valor agregado
(`00-resumen.tex:11`; Sección 3.5). En consecuencia el IC del kappa se declara
**no estimable** desde las fuentes permitidas y **no se fabrica**. Es
**reversible si** el autor aporta la tabla primaria de acuerdo observado/esperado
o las etiquetas por analista; en ese caso se calcula por bootstrap con semilla
fija y se hace upsert aquí. El rótulo interpretativo del valor puntual sigue
siendo "casi perfecto" (Landis y Koch, `\kappa > 0,80`).

### 3.7 Gate de revisión por etapa y punto de operación (c-130)

Valores que la tesis cita para describir el alcance del gate de revisión humana
por etapa y el cortocircuito de la etapa determinística. La definición de las
magnitudes (confianza por etapa, puntaje de correctitud, punto de operación) la
fija `05-arquitectura.tex` (`subsec:subsistema-clasificacion`); aquí solo se
registran los números.

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Casos con confianza `< 0,70` sin escalamiento: `124/200` | `07-resultados.tex:178-179` (bandas `98 + 26`), `07-resultados.tex:157`; Sección 4 de este memo; `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` | vigente | Los `124` son **todos** de la etapa determinística (confianza = fuerza de señal, no probabilidad). Repetición offline del 2026-10-25 con `DeterministicClassifier` sobre el corpus versionado: `124` con confianza `< 0,70` (`94` aciertos) y `7` con `≥ 0,70`; coincide con la evidencia versionada `hybrid-v3` (`124` de `200`). |
| Proporción de esos casos: `62,0 %` | `07-resultados.tex:157` (`124/200`) | vigente | Aritmética sobre `124/200`; la tesis lo escribe `62~\%`. |
| Confianza mínima declarada por Gemini: `0,85` en `69` casos | Sección 4 de este memo; `07-resultados.tex:157`; `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` | vigente | Verificado el 2026-10-25 sobre la evidencia versionada: `69` predicciones con `etapa = gemini`, mínimo `0,85`. La etapa de reserva no se activó (`0` casos). |
| Punto de operación del cortocircuito: `0,5166` | `App/Backend/app/config/settings.py:134`; `docs/deterministic_calibration.md:35-36` | vigente | Umbral sobre el `score_correctitud` (no sobre la confianza). Derivado por validación cruzada de cinco pliegues (tau OOF `0,516666…` en los cinco pliegues, truncado a 4 decimales). Sustituye al piso absoluto `0,90` del diseño inicial (ver el punto siguiente). |
| Cobertura del punto: `131/200` (`65,5 %`) | `docs/deterministic_calibration.md:39`; Sección 3.3 (etapa determinística `131`) | vigente | Equivale a cortocircuitar todo caso con señal dominante (`57` sin predicción y `12` ambiguos escalan a Gemini); todos los `131` tienen puntaje `≥ 0,516667` (mínimo repetido offline el 2026-10-25). |
| `precision_det(S)`: `97/131` = `0,7405` | `docs/deterministic_calibration.md:40,67` | vigente | Coincide con la exactitud estricta de la etapa determinística de la corrida oficial (Sección 3.3; c-131 la consume y le agrega el intervalo de confianza). **Estimación dentro de la muestra** (ver el punto 7 de la Sección 7). Sensibilidad: estimación dentro de la muestra; ver sección 3.10. |
| `precision_gem(S)`: `88/130` = `0,6769` | `docs/deterministic_calibration.md:41-44,68` | vigente | Fuente: cache FORCE-ESCALATE (`evaluation/predicciones_calibracion.json`, no versionada; copia congelada en `evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json`). Excluye `1` caso cortocircuitable sin predicción de Gemini en esa cache. **Estimación dentro de la muestra**. Recalculado el 2026-10-25 desde la evidencia versionada: `88` aciertos sobre `130` = `0,6769`. Sensibilidad: estimación dentro de la muestra; ver sección 3.10. |
| Piso absoluto `0,90` del diseño inicial: `1/200` | `docs/deterministic_calibration.md:104,181-182` | **retirado** | Cobertura de un piso de precisión (no de un umbral de confianza) que habría cortocircuitado un único caso; retirado como criterio de operación por c-74. La tesis ya no lo cita (se retira "umbral de confianza superior al 90 %"); se conserva aquí por trazabilidad. |

Salvedades: (i) `97/131` y `88/130` son estimaciones dentro de la muestra
porque el vocabulario del filtro, las reglas de frontera del prompt y el punto
de operación se ajustaron sobre el mismo corpus (c-71, c-72 y c-74; declarado por
c-144 en `08-discusion.tex:20`); (ii) `88/130` proviene de una cache que no es la
corrida oficial y su procedencia queda registrada en el punto 7 de la Sección 7.

### 3.8 Tiempos por canal, contrastes y sensibilidad (c-134)

Valores del bloque "## Tiempos" de `evaluation/report.md` regenerado el 2026-10-25 con
`python -m evaluation.run_evaluation --solo-tiempos` (sin Gemini ni predicciones; el
corpus del checkout de Windows con CRLF da la huella canónica `1fd17d7e…`, en
`evaluation/report.md:256`). Las funciones que los calculan están en
`evaluation/stats.py`. Convenciones fijadas por el change:

- El desvío estándar es **muestral** (divisor `n − 1`) en todo el documento.
- Los `p` de tiempos se informan **bilaterales** (`W = min(T+, T−)`), conservadores
  frente a la hipótesis direccional `H1: M_manual > M_automatizado`; el `p` unilateral
  se informa aparte (`alternative="greater"` sobre `manual − automatizado`, una segunda
  llamada a `scipy`, no la mitad del bilateral).
- `d_z = media(d) / desvío(d)` con `d = manual − automatizado` (desvío muestral); no es
  el rank-biserial `r` (los rótulos no se intercambian).
- El efecto mínimo detectable (MDE, en escala `d_z`) es
  `(z_{1−α/2} + z_{potencia}) / raíz(n · ARE)` con `α = 0,05` bilateral, potencia `0,80`
  y `ARE = 1` (sin ajuste) o `ARE = 0,864` (cota inferior de Hodges-Lehmann, `108/125`,
  de la eficiencia de la prueba de rangos frente a la `t` pareada).

**Brazo manual** (`s`). Procedencia: `evaluation/report.md:223-226`;
`evaluation/stats.py::estadisticos_descriptivos`.

| Ámbito | n | Media | Mediana | Desvío | Mínimo–máximo | Estado |
|---|---|---|---|---|---|---|
| Global | 200 | `61,585` | `50` | `44,896` | `10`–`300` | vigente |
| Llamada telefónica | 81 | `87,247` | `72` | `48,899` | `30`–`220` | vigente |
| Correo electrónico | 66 | `56,515` | `50` | `35,809` | `20`–`300` | vigente |
| Formulario web | 53 | `28,679` | `20` | `16,442` | `10`–`100` | vigente |

**Brazo automatizado** (`s`). Misma procedencia.

| Ámbito | n | Media | Mediana | Desvío | Mínimo–máximo | Estado |
|---|---|---|---|---|---|---|
| Global | 200 | `17,761` | `17,471` | `13,516` | `0,525`–`65,834` | vigente |
| Llamada telefónica | 81 | `20,088` | `18,698` | `6,025` | `14,027`–`59,150` | vigente |
| Correo electrónico | 66 | `27,655` | `25,818` | `14,200` | `8,970`–`65,834` | vigente |
| Formulario web | 53 | `1,882` | `1,265` | `1,266` | `0,525`–`4,162` | vigente |

**Reducción relativa y pares no más rápidos.** Procedencia:
`evaluation/report.md:223-226`; `evaluation/stats.py::reduccion_relativa` y
`reduccion_tiempos`.

| Ámbito | Reducción de la media | Reducción de la mediana | Pares no más rápidos | Estado |
|---|---|---|---|---|
| Global | `71,16 %` | `65,06 %` | `12` de `200` | vigente |
| Llamada telefónica | `76,98 %` | `74,03 %` | `0` de `81` | vigente |
| Correo electrónico | `51,07 %` | `48,36 %` | `12` de `66` | vigente |
| Formulario web | `93,44 %` | `93,67 %` | `0` de `53` | vigente |

Los `12` pares no más rápidos del global (`report.md:202`) pertenecen **todos** al canal
correo electrónico. Los `71,16 %` coinciden con los `71,2 %` de la Sección 3.1 (misma
cifra con más decimales). Sustituyen a la afirmación "reducciones positivas en los tres"
canales de `08-discusion.tex:22`, que no tenía tabla de respaldo.

**Contraste direccional, tamaño del efecto estandarizado y efecto mínimo detectable.**
Procedencia: `evaluation/report.md:239-242`; `evaluation/stats.py::wilcoxon_tiempos_detallado`
(`p`, `p_unilateral`), `tamano_efecto_dz`, `efecto_minimo_detectable` y
`ARE_WILCOXON_MINIMA`.

| Ámbito | n | `p` bilateral | `p` unilateral | `d_z` | MDE (`ARE = 1`) | MDE (`ARE = 0,864`) | Estado |
|---|---|---|---|---|---|---|---|
| Global | 200 | `3,08e-32` | `1,54e-32` | `1,0004` | `0,1981` | `0,2131` | vigente |
| Llamada telefónica | 81 | `5,36e-15` | `2,68e-15` | `1,3674` | `0,3113` | `0,3349` | vigente |
| Correo electrónico | 66 | `4,78e-09` | `2,39e-09` | `0,7345` | `0,3449` | `0,3710` | vigente |
| Formulario web | 53 | `2,39e-10` | `1,19e-10` | `1,6147` | `0,3848` | `0,4140` | vigente |

`d_z` observado frente al mínimo detectable del global: `1,0004 / 0,1981 = 5,05` veces
(`1,0004 / 0,2131 = 4,69` con `ARE`), es decir, más de cuatro veces; por canal, `d_z`
`0,73`–`1,61` frente a mínimos `0,31`–`0,38` (`0,33`–`0,41` con `ARE`). Los `p` y `d_z`
del global y de cada canal son la base de `tab:tiempos-canal`; `W`, `T+`, `T−` y `r` por
canal quedan en el reporte (`report.md:211-213`) y no se citan en la tesis (telefonía y
formulario web tienen `W = 0` y `r = 1`, ver el requisito "Rigor inferencial del tamaño
del efecto").

**Sensibilidad del redondeo manual y granularidad** (conjunto global, descuento fijo a
cada `tiempo_manual_s`). Procedencia: `evaluation/report.md:251-252` y `:254`;
`evaluation/stats.py::escenario_sensibilidad` y `granularidad_manual`.

| Descuento | Media manual ajustada | Reducción de la media | `p` bilateral | `p` unilateral | `r` | Estado |
|---|---|---|---|---|---|---|
| `5 s` | `56,585 s` | `68,61 %` | `4,87e-30` | `2,44e-30` | `0,9286` | vigente |
| `10 s` | `51,585 s` | `65,57 %` | `1,8e-26` | `8,98e-27` | `0,8683` | vigente |

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Múltiplos exactos de `5 s` en `tiempo_manual_s`: `199 / 200` | `evaluation/report.md:254`; `evaluation/stats.py::granularidad_manual` | vigente | El único valor que no es múltiplo de `5` es `72 s`. Precisa el instrumento: la planilla manual tiene resolución efectiva de `5 s`. |
| Múltiplos exactos de `10 s`: `180 / 200` | `evaluation/report.md:254` | vigente | Vincula el escenario de `10 s` con la resolución efectiva de la planilla. |

**Convención del desvío estándar y diferencias pareadas.**

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Desvío estándar manual: `44,9 s` | `evaluation/report.md:223` (`44,8961`) | vigente | Muestral; ya era la convención de `07-resultados.tex:23`. El poblacional daría `44,8` y no se cita. |
| Desvío estándar automatizado: `13,52 s` | `evaluation/report.md:223` (`13,5164`) | vigente | Muestral (divisor `n − 1`). Reemplaza a `13,48`. |
| Desvío estándar automatizado: `13,48 s` | `07-resultados.tex:10,23`, `08-discusion.tex:12` (corregidos por el bloque de tesis de c-134, 2026-10-25; ya no figura en ninguna fuente `.tex`) | **retirado** | Convención poblacional (divisor `n`): `13,5164 × raíz(199/200) = 13,4825`. Se unifica en muestral (decisión D3 del change). Reversible si el autor adopta divisor `n` en todo el documento. |
| Diferencias pareadas: media `43,82 s`, desvío muestral `43,81 s` | media: `evaluation/report.md:199` (`43,82`); desvío: recálculo offline del 2026-10-25 con `estadisticos_descriptivos` sobre los 200 pares (`43,8067`), no figura en el reporte | vigente | `d_z = 43,8244 / 43,8067 = 1,0004` (coincide con la tabla de contrastes). |

**Cifras con redondeo de tesis** (bloque de tesis de c-134, 2026-10-25). Son las formas
redondeadas de los valores canónicos de las tablas anteriores; no son valores nuevos.

| Valor citado en la tesis | Valor canónico de origen | Dónde se cita | Estado |
|---|---|---|---|
| `13,52 s` (desvío automatizado) | `13,5164` | `07-resultados.tex` (texto y `tab:tiempos`), `08-discusion.tex` | vigente |
| `77,0 %`, `51,1 %`, `93,4 %` (reducción de la media por canal) | `76,98 %`, `51,07 %`, `93,44 %` | `tab:tiempos-canal`, `08-discusion.tex` (`51,1`–`93,4`) | vigente |
| `87,2`, `56,5`, `28,7 s` (media manual por canal) y `72,0`, `50,0`, `20,0 s` (mediana) | `87,2469`, `56,5152`, `28,6792` y `72`, `50`, `20` | `tab:tiempos-canal` | vigente |
| `20,09`, `27,65`, `1,88 s` (media automatizada por canal) y `18,70`, `25,82`, `1,26 s` (mediana) | `20,0883`, `27,6546`, `1,8823` y `18,6980`, `25,8180`, `1,2650` | `tab:tiempos-canal` | vigente |
| `d_z`: `1,00`, `1,37`, `0,73`, `1,61` | `1,0004`, `1,3674`, `0,7345`, `1,6147` | `04-marco-metodologico.tex` (potencia), `07-resultados.tex` | vigente |
| MDE: `0,20` y `0,21` (global); `0,31`, `0,34`, `0,38` y `0,33`, `0,37`, `0,41` (por canal, sin y con `ARE`) | `0,1981`, `0,2131`; `0,3113`, `0,3449`, `0,3848` y `0,3349`, `0,3710`, `0,4140` | `04-marco-metodologico.tex` | vigente |
| `p` unilateral global `1,54e-32` | `1,54e-32` | `01-introduccion.tex`, `04-marco-metodologico.tex` | vigente |
| `p` bilateral por canal `5,36e-15`, `4,78e-09`, `2,39e-10` y global `3,08e-32` | idem | `tab:tiempos-canal` (el global también en `01` y `07`) | vigente |
| Media y desvío de las diferencias: `43,82 s` y `43,81 s` | `43,8244` y `43,8067` | `04-marco-metodologico.tex`, `07-resultados.tex` | vigente |
| Pares no más rápidos `0 de 81`, `12 de 66`, `0 de 53` (`12 de 200`) | tabla de reducción relativa de arriba | `tab:tiempos-canal` | vigente |
| Múltiplos de `5 s` `199 / 200` y de `10 s` `180 / 200` | `evaluation/report.md:254` | `04-marco-metodologico.tex` (`subsec:diseno-experimental`) | vigente |

Dos redondeos a dos decimales no coinciden con el redondeo a tres decimales de las tablas
de arriba y no son errores: la media automatizada de correo es `27,6546` (se cita
`27,65`; la forma `27,655` de arriba es la de tres decimales) y la mediana automatizada
de formulario web es `1,2650` a cuatro decimales (se cita `1,26`, el valor que la tabla
previa de la tesis ya tenía). **Hechos del estudio PROVISIONALES** (pendientes de
confirmación del autor, ver `design.md` de c-134, OQ1 y OQ2): el relato del cronometraje
mutuo (`04-marco-metodologico.tex`, `08-discusion.tex`, `11-aspectos-legales.tex`) y la
declaración de que la distribución del universo por sector no está disponible
(`04-marco-metodologico.tex`); no aportan ninguna cifra nueva.

**Reversibilidad.** El `p` bilateral queda como valor principal para no mover `W`, `T+`,
`r` ni las cifras ya canónicas de la Sección 3.1; si el autor prefiere el unilateral como
principal, el cambio se limita a `01-introduccion.tex:32`, `07-resultados.tex:54` y a
esta sección. El MDE por aproximación normal reproduce las cifras vigentes de la tesis
(`0,20` y `0,21`); una potencia por `t` no central daría una diferencia
despreciable que no justifica la dependencia adicional.

### 3.9 Métricas por etapa, por canal y exactitud laxa (c-131)

Valores del reporte `evaluation/report.md` regenerado el 2026-10-25 por cache hit (sin
Gemini) con `python -m evaluation.run_evaluation`, a partir de las predicciones de la
corrida oficial (`hybrid-v3`, 2026-10-07). Las funciones que los calculan están en
`evaluation/metrics.py` (`aciertos_laxos`, `resumen_exactitud`, `desglose_exactitud`,
`calibracion_por_etapa`, `distribucion_confianza`) y las secciones nuevas del reporte
las emite `evaluation/run_evaluation.py`. Definiciones: **exactitud estricta** = sector
predicho principal igual a `sector_asignado`; **exactitud laxa** = sector predicho
principal dentro del conjunto de verdad (`sector_asignado` más `sectores_adicionales`);
la **pertenencia** (`sector_asignado` dentro del conjunto predicho) es otra cosa y vale
`147/200`. La laxa es una métrica **secundaria**: no reemplaza a la estricta ni fija por
sí sola el estado de ningún objetivo (lo decide c-133). Todos los IC son de Wilson al 95 %.

**Decisión de datos y procedencia de la corrida** (gobernanza HIGH, **PROVISIONAL**,
2026-10-25, pendiente de confirmación del autor):

| Decisión / dato | Valor | Procedencia | Estado |
|---|---|---|---|
| Rama de datos (OQ1) | **P1 vía c-143**: las predicciones se toman de la evidencia congelada publicada por c-143 (no hizo falta pedirlas al clon de Luca) | `openspec/changes/archive/2026-10-23-c-143-publicar-predicciones-como-evidencia-de-evaluacion/`; `evaluation/evidence/README.md` | vigente (PROVISIONAL) |
| Corrida paga de reproducción (OQ2) | **No autorizada** (P2 no aplica): cero llamadas a Gemini en este change | instrucción del orquestador, 2026-10-25 | vigente (PROVISIONAL) |
| Versionado de las caches (OQ3, D8) | **Resuelto por c-143**: copias congeladas en `evaluation/evidence/`; las rutas vivas `evaluation/predicciones*.json` siguen ignoradas por git | `evaluation/evidence/`, `.gitignore:72-73` | vigente (PROVISIONAL) |
| Predicciones oficiales | `evaluation/predicciones.json` = copia byte-idéntica de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`; `cache_meta`: `corpus_hash` `1fd17d7e…`, `corpus_count` `200`, `classifier_version` `hybrid-v3`, `generated_at` `2026-10-07T22:22:01.947873+00:00`; SHA-256 `3fb5bacd04f2e9d303f580e4cf2ac4b4c6f2eab628a4fff80a6e1238029cd8fd` | `evaluation/report.md:5` (procedencia declarada por el reporte) | vigente |
| Predicciones FORCE-ESCALATE | `evaluation/predicciones_calibracion.json` = copia de `evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json`; `hybrid-v2`, `generated_at` `2026-10-07T20:33:03.438926+00:00`, `corpus_hash` `5f062e14…` (distinto del vigente; las 200 descripciones coinciden con el corpus); 199 `gemini` + 1 `deterministic`; SHA-256 `2d4f868ce1c01f8a528b29afc69dc541842f7f238c4932c3eee94a6f6298a775` | `docs/deterministic_calibration.md:234` | vigente (contraste de McNemar y sensibilidades E3/E4; uso confirmado 2026-10-26) |
| Huella canónica | `evaluation/tests/test_huella_canonica.py` (7 pruebas) reproduce 147/200, etapas `131/69/0`, bandas `98/26/6/31/39` con `75/19/2/22/29`, contingencia `76/53` y `124/94`, tramo `46/13`, `97/131` y `50/69` y el SHA-256 del corpus | `evaluation/tests/test_huella_canonica.py` | vigente |
| Descripciones de ambas caches | `0` diferencias contra el corpus pseudonimizado (200 de 200, mismo orden): exposición incremental nula | verificación del 2026-10-25 (apply de c-131, tarea 3.4) | vigente |

**Exactitud estricta y laxa por etapa y por canal** (`evaluation/report.md:31-33` y
`:72-76` para global y etapas; `:84-88` para canales):

| Ámbito | Casos | Estricta `k/n` | Exactitud estricta e IC | Laxa `k/n` | Exactitud laxa e IC | Estado |
|---|---|---|---|---|---|---|
| Global | 200 | `147/200` | `0,7350` `[0,6698; 0,7913]` (ya canónico, Sección 3.2) | `179/200` | `0,8950` `[0,8448; 0,9303]` (`89,5 %`) | vigente |
| Etapa determinística | 131 | `97/131` | `0,7405` `[0,6593; 0,8079]` | `119/131` | `0,9084` `[0,8467; 0,9468]` | vigente Sensibilidad: estimación dentro de la muestra; ver sección 3.10. |
| Etapa Gemini | 69 | `50/69` | `0,7246` `[0,6095; 0,8161]` | `60/69` | `0,8696` `[0,7703; 0,9298]` | vigente |
| Etapa fallback | 0 | `0/0` | no aplicable | `0/0` | no aplicable | vigente |
| Llamada telefónica | 81 | `53/81` | `0,6543` `[0,5459; 0,7488]` | `70/81` | `0,8642` `[0,7730; 0,9224]` | vigente |
| Correo electrónico | 66 | `51/66` | `0,7727` `[0,6583; 0,8571]` | `61/66` | `0,9242` `[0,8346; 0,9672]` | vigente |
| Formulario web | 53 | `43/53` | `0,8113` `[0,6864; 0,8941]` | `48/53` | `0,9057` `[0,7975; 0,9590]` | vigente |

Los valores por etapa (`97/131`, `50/69`) coinciden con los que `design.md` de c-131
derivó de agregados canónicos (estado `condicional` en el diseño); la huella los
confirmó, por lo que pasan a `vigente`. La exactitud laxa global (`89,5 %`) supera el `85 %`
del segundo objetivo, pero es una métrica secundaria: **no** cambia el estado de ningún
objetivo (decisión de c-133). La exactitud laxa nunca es menor que la estricta
(`179 ≥ 147`; `119 ≥ 97`; `60 ≥ 50`; en cada canal).

**Composición por etapa de cada canal** (casos `deterministic / gemini / fallback`,
`evaluation/report.md:86-88`): llamada telefónica `58 / 23 / 0`; correo electrónico
`34 / 32 / 0`; formulario web `39 / 14 / 0`. **Composición del corpus por canal**
(recálculo del 2026-10-25 sobre `data/corpus_evaluacion_pseudonimizado.json`; no figura en el
reporte): llamada telefónica `81` casos, `49` multietiqueta (`60,5 %`), asignados Hardware `30`,
Software `28`, Seguridad `14`, Sistemas `9`; correo electrónico `66`, `43` multietiqueta
(`65,2 %`), Hardware `23`, Software `23`, Seguridad `14`, Sistemas `6`; formulario web `53`, `15`
multietiqueta (`28,3 %`), Hardware `32`, Software `16`, Seguridad `3`, Bases de Datos `1`,
Sistemas `1`. Esta composición difiere entre canales (el formulario web concentra Hardware, la
clase con mejor F1, y tiene pocos casos multietiqueta): la diferencia de exactitud entre
canales **no** se atribuye a la transcripción telefónica. Estado: vigente (derivación del corpus).

**Bandas de confianza por etapa** (casos / aciertos / exactitud; IC en
`evaluation/report.md:136-150`). La suma de las dos etapas reproduce, banda por banda, la
Tabla 7.5 canónica (`98/26/6/31/39` casos; `75/19/2/22/29` aciertos).

| Banda | Determinística | Gemini | Suma | Estado |
|---|---|---|---|---|
| `[0; 0,5)` | `98 / 75 / 0,7653` `[0,6724; 0,8382]` | `0 / 0` (no aplicable) | `98 / 75` | vigente |
| `[0,5; 0,7)` | `26 / 19 / 0,7308` `[0,5392; 0,8630]` | `0 / 0` | `26 / 19` | vigente |
| `[0,7; 0,85)` | `6 / 2 / 0,3333` `[0,0968; 0,7000]` | `0 / 0` | `6 / 2` | vigente |
| `[0,85; 0,95)` | `0 / 0` | `31 / 22 / 0,7097` `[0,5341; 0,8390]` | `31 / 22` | vigente |
| `[0,95; 1,00]` | `1 / 1 / 1,0000` `[0,2065; 1,0000]` | `38 / 28 / 0,7368` `[0,5799; 0,8503]` | `39 / 29` | vigente |

La cifra `0,744` (`29/39`) que cita el dictamen para la banda superior incluye el caso
determinístico; Gemini solo vale `28/38 = 0,7368`. Los dos IC de Gemini se solapan.

**Contingencia en 0,70 y tramo `≥ 0,90` por etapa** (`evaluation/report.md:113-116` y
`:124-127`):

| Ámbito | `≥ 0,70`: casos / aciertos | `< 0,70`: casos / aciertos | Tramo `≥ 0,90`: casos / errores | Estado |
|---|---|---|---|---|
| Global | `76 / 53` (`0,6974`) | `124 / 94` (`0,7581`) | `46 / 13` | vigente |
| Determinística | `7 / 3` (`0,4286`) | `124 / 94` (`0,7581`) | `1 / 0` | vigente |
| Gemini | `69 / 50` (`0,7246`) | `0 / 0` | `45 / 13` | vigente |
| Fallback | `0 / 0` | `0 / 0` | `0 / 0` | vigente |

**Distribución de valores de confianza por etapa** (casos / aciertos;
`evaluation/report.md:159-168`). Determinística: `0,0` `90 / 67`; `1/6 ≈ 0,1667` `8 / 8`;
`0,5` `26 / 19`; `0,75` `6 / 2`; `1,0` `1 / 1` (los `98` casos de la banda `[0; 0,5)` son
`90 + 8`). Gemini: `0,85` `24 / 18`; `0,90` `7 / 4`; `0,95` `35 / 25`; `0,98` `3 / 3`. Estado: vigente.

**Contraste pareado de McNemar entre la etapa determinística y Gemini sobre `S`**
(insumo de **c-133** —hipótesis subsidiaria de eficiencia del esquema híbrido— y de
**c-142** —sensibilidad fuera de muestra por el ajuste del clasificador con el corpus, A5—;
c-131 NO lo lleva a la tesis). Procedencia: `docs/deterministic_calibration.md:234`.

| Elemento | Valor | Estado |
|---|---|---|
| Conjunto `S` y pares | `|S| = 131` (señal no ambigua y puntaje `≥ 0,5166`); pares con predicción de ambas etapas `130`; excluido `R099` (cortocircuitó también en la corrida forzada) | vigente |
| Exactitud estricta sobre los pares | determinística `96/130 = 0,7385`; Gemini `88/130 = 0,6769` (control: coincide con `precision_gem(S)` de la Sección 3.7) | vigente |
| Tabla 2×2 | ambas aciertan `80`; solo la determinística (`b`) `16`; solo Gemini (`c`) `8`; ninguna `26` | vigente |
| Estadístico | `χ² = 2,0417` con corrección de continuidad (1 gl), `p = 0,1530`; `p` exacto `0,1516` | vigente |
| `p` primario y criterio | `0,1516`, criterio **exacto** (`b + c = 24 < 25`); no se rechaza la igualdad al 5 % | vigente |
| Control de la reproducción offline | las `131` predicciones determinísticas sobre `S` coinciden `131/131` con las de `etapa = deterministic` de la corrida oficial | vigente |

Salvedades: (i) la predicción de Gemini sobre `S` proviene de otra corrida y otra versión
(`hybrid-v2`) que la oficial, en la que Gemini nunca vio `S`; (ii) el contraste es dentro de
la muestra y `S` se definió con el tau out-of-fold calibrado sobre el mismo corpus; (iii) un
resultado no significativo no demuestra equivalencia (potencia limitada con `24`
discordancias).

**Lectura retirada.** La lectura de «calibración invertida o anti-calibrada» del clasificador
en su conjunto queda **retirada**: el contraste agregado `0,697` (confianza `≥ 0,70`) frente a
`0,758` (`< 0,70`) es un efecto de composición entre etapas (los `124` casos `< 0,70` son
todos de la etapa determinística; el tramo `≥ 0,70` reúne `7` determinísticos y los `69` de
Gemini). Dentro de Gemini las dos bandas rinden `0,7097` y `0,7368` con IC solapados: la
confianza autodeclarada no discrimina aciertos de errores en el rango observado
(`0,85` a `1,00`); y la confianza de la etapa determinística (fuerza de señal en escala
discreta) no ordena la correctitud: sus `98` decisiones con confianza menor que `0,5` aciertan
`75` (`0,7653`) y las `6` de `0,75` aciertan `2`. Estado de la lectura de anti-calibración:
**retirado**. Ningún valor `vigente` de las Secciones 3.1 a 3.8 cambió.

### 3.10 Sensibilidad frente al ajuste del clasificador con el corpus (c-142)

**Sensibilidad: no reemplaza valores canónicos.** Todo valor de esta sección es una
medición de sensibilidad (variantes pre-registradas en el `design.md` de c-142, D2-D4, D8
y D9) y NO sustituye ningún valor de las Secciones 3.1 a 3.9: la corrida oficial y su
`evaluation/report.md` quedan intactos. Fuente única: `evaluation/report_sensibilidad_ajustes.md`
(generado el 2026-10-25 por `python -m evaluation.sensibilidad_ajustes`, offline, sin
Gemini; dos corridas consecutivas dan un archivo idéntico byte a byte). Notación: `V1` =
vocabulario vigente (151 patrones), `V0` = vocabulario previo a c-71 (89 patrones, blob
`858f1c6`, versionado con procedencia en `evaluation/data/sensibilidad_ajustes/`), `L1` =
lógica y punto de operación vigentes (`tau = 0,5166`), `L0` = lógica previa a c-71
(replica; confianza `w/(w + r + 1e-6)`, cortocircuito con confianza `≥ 0,90`).

**Estado de datos.** Rama P1 de c-131 (G0.5): la caché oficial `hybrid-v3` y la FORCE-ESCALATE
`hybrid-v2` (copias congeladas de `evaluation/evidence/`, c-143). La FORCE-ESCALATE tiene
`corpus_hash` `5f062e14…` distinto del vigente (`1fd17d7e…`); antes de usarla como fuente
de predicciones de Gemini, `evaluation/sensibilidad_ajustes.py` verifica que identificador,
descripción y sector asignado de sus 200 entradas coinciden con el corpus (0 diferencias) y
que el lado `V1` de E3 reproduce los `146` aciertos documentados (`docs/deterministic_calibration.md:89`)
sin casos excluidos. Esa verificación sustenta E3 y E4; la decisión de usar la caché
queda PROVISIONAL (ver el grupo c-142 de `dictamen-correcciones.md`).

| Valor de sensibilidad | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Control de fidelidad de la configuración evaluada (`V1 + L1`): `131` casos y `97` aciertos reproducidos | `evaluation/report_sensibilidad_ajustes.md:19-22` | vigente | Reproducción por el adaptador sobre el clasificador de producción: `97/131 = 0,7405` `[0,6593; 0,8079]`, cobertura `131/200`, laxos `119/131`. Idéntica al valor canónico de la Sección 3.9. |
| **E1** variante principal (`V0 + L1`): casos cortocircuitados `n_A = 74` (cobertura `74/200 = 0,3700`) | `evaluation/report_sensibilidad_ajustes.md:28` | vigente | Sensibilidad: no reemplaza valores canónicos. Ablación de un solo factor (vocabulario). |
| E1: aciertos `k_A = 39`; exactitud `p_A = 39/74 = 0,5270`; IC de Wilson 95 % `[0,4148; 0,6366]` | `evaluation/report_sensibilidad_ajustes.md:29` | vigente | Aciertos laxos `57/74` (`:30`). Rama **A** pre-registrada (`p_A < 0,7405`): cota pesimista del sesgo atribuible al vocabulario. |
| E1: diferencia descriptiva `0,7405 − p_A` = `0,2134` (**21,3 puntos**) | `evaluation/report_sensibilidad_ajustes.md:31` | vigente | Exacta (`97/131 − 39/74 = 0,21343`); con los extremos redondeados de la tabla (`0,7405 − 0,5270`) la fórmula de D2 da `21,35`, empate de redondeo sin efecto sobre la rama. No es una diferencia pareada: los conjuntos de casos difieren. |
| Descomposición pareada: cortocircuitados por ambos `67` (aciertos `V1` `38`, `V0` `37`); solo `V1` `64` (aciertos `V1` `59`, `0,9219`); solo `V0` `7` (aciertos `V0` `2`) | `evaluation/report_sensibilidad_ajustes.md:37-39` | vigente | Suman `131` casos y `97` aciertos del lado `V1` (`38 + 59`) y `74` y `39` del lado `V0` (`67 + 7`, `37 + 2`). Los `64` casos que solo cortocircuita `V1` son el aporte de la ampliación de c-71. |
| McNemar sobre los `67` casos comunes (`V1` frente a `V0`): ambas `37`, solo `V1` `1`, solo `V0` `0`, ninguna `29`; `p` exacto `1,0000` | `evaluation/report_sensibilidad_ajustes.md:43-44` | vigente | `b + c = 1 < 25`, criterio exacto. Evidencia descriptiva, sin corrección por multiplicidad; sobre los casos comunes ambos vocabularios aciertan casi lo mismo, de modo que la diferencia de E1 proviene de los casos que solo resuelve `V1`. |
| **Referencia histórica** (`V0 + L0`): `72` casos cortocircuitados (`72/200 = 0,3600`), `37` aciertos, `0,5139` `[0,4007; 0,6257]`, laxos `55/72` | `evaluation/report_sensibilidad_ajustes.md:50-52` | vigente | Reproduce la línea base de c-71. No se lee como cota del sesgo (incluye cambios de lógica legítimos). |
| Control de fidelidad de la réplica `L0` frente a la línea base documentada por c-71: las `11` métricas **coinciden** (`72`; `22/14/36` por canal correo/web/teléfono; `37`; `13/7/17`; `55`; `119` sin coincidencias; `126` predicciones de Seguridad Informatica) | `evaluation/report_sensibilidad_ajustes.md:56-68`; `evaluation/tests/test_sensibilidad_corpus.py` | vigente | Fiel: el test de caracterización pasa sin ajustar la réplica ni el valor esperado. Fuente de lo documentado: `openspec/changes/archive/2026-10-06-c-71-hardening-clasificador-determinista/proposal.md:9-13` y notas de su `tasks.md`. |
| **E3** exactitud global con las predicciones de Gemini fijas (FORCE-ESCALATE, una sola fuente para ambos lados): `V1` `146/200` (`0,7300`); `V0` `128/200` (`0,6400`); `0` casos excluidos | `evaluation/report_sensibilidad_ajustes.md:76-77` | vigente | `V1 = 146` reproduce el valor documentado (`docs/deterministic_calibration.md:89`). Lectura: sin la ampliación del vocabulario, el pipeline acertaría `18` casos menos con Gemini fijo. Sensibilidad: no reemplaza la exactitud global oficial `147/200`. |
| E3: McNemar `V1` frente a `V0` (`200` pares): ambas `128`, solo `V1` `18`, solo `V0` `0`, ninguna `54`; `p` exacto `0,0000` (`2 × 0,5^18 ≈ 7,6 × 10^-6`, **`p < 0,001`**); `χ²` corregido `16,0556` (`p = 0,0001`) | `evaluation/report_sensibilidad_ajustes.md:78-79` | vigente | `b + c = 18 < 25`, criterio exacto. Evidencia descriptiva. |
| **E4** referencia en muestra (`V1`): reglas `96/130 = 0,7385`, Gemini `88/130 = 0,6769`; `b = 16`, `c = 8`, `p` exacto `0,1516` | `evaluation/report_sensibilidad_ajustes.md:80-83` | vigente | Reproduce el contraste de c-131 (Sección 3.9; `docs/deterministic_calibration.md:234`). |
| E4 (`V0`): `|S| = 74`, `73` pares (excluido `R099`); reglas `38/73 = 0,5205`, Gemini `48/73 = 0,6575`; ambas `35`, solo reglas `3`, solo Gemini `13`, ninguna `22`; `p` exacto `0,0213` (`χ²` corregido `5,0625`, `p = 0,0244`) | `evaluation/report_sensibilidad_ajustes.md:84-87` | vigente | Con el vocabulario previo la etapa de reglas **no supera** a Gemini sobre los casos que resuelve (`0,5205` frente a `0,6575`, discordancias `3` frente a `13`, `p` exacto `0,021` sin corrección por multiplicidad). Insumo de c-133: la ventaja de las reglas sobre Gemini en `S` depende del vocabulario ajustado con el corpus. |
| Prompt, **nivel a**: los tres casos motivadores de c-72 (`R002`, `R038`, `R015`) están entre los `69` escalados; etapa Gemini `50/69 = 0,7246` con todos y `48/66 = 0,7273` sin ellos | `evaluation/report_sensibilidad_ajustes.md:93-94` | vigente | Cota débil: solo retira la influencia directa de los casos documentados. Con todos los casos reproduce el `50/69` de la Sección 3.9. `K_EX = 48`, `N_EX = 66`. |
| Prompt, **nivel b**: la FORCE-ESCALATE se clasifica "**posterior**" (`generated_at = 2026-10-07T20:33:03.438926+00:00`, posterior a la aplicación de c-72, 2026-10-06T19:38:20Z); la comparación pareada contra la corrida oficial **no aplica** | `evaluation/report_sensibilidad_ajustes.md:95-96` | vigente | Consecuencia de la tarea 7.3. La suposición de la propuesta (FORCE-ESCALATE generada antes de las reglas de frontera) queda refutada por su `cache_meta`: la comparación `0,7405` frente a `0,6769` no mezcla, por esta vía, dos versiones del prompt. La fecha no prueba qué archivo de prompt cargó esa corrida. |
| Prompt, **nivel c** (ablación paga de dos brazos, misma sesión): prompt vigente `50/69` frente a sin reglas de frontera `46/69`; reservas (fallback, contadas como error) `0` en ambos brazos | `evaluation/report_sensibilidad_ajustes.md:98-99` | vigente | Ejecutada el 2026-10-28 (G0.7a), tras corregir el arnés con c-154. McNemar pareado entre brazos sobre los `69` casos escalados: `p` binomial exacto bilateral `0,3438` (`χ²` corregido `0,9000`, `p = 0,3428`), **no significativo**; deriva del brazo control frente a la corrida oficial `50/69` frente a `50/69` (temperatura `0,3`). Sensibilidad: no sustituye la exactitud de la etapa Gemini de la corrida oficial (`50/69`, Sección 3.9); en esta muestra el efecto de las reglas de frontera no se distingue del azar. Nivel del prompt para la tesis: **c**. |
| Variante por pliegues | `evaluation/report_sensibilidad_ajustes.md:70-72`; Sección 7, punto 8 | no factible | El repositorio no registra qué casos motivaron cada patrón de c-71. Sin valor. |
| Conjunto de incidentes de preproducción | Sección 7, punto 6 (c-144) | no existe | Desenlace D11: no existen / no se localizan; sin datos personales involucrados. Sin valor. |

Salvedades: (i) todo valor de esta sección es una estimación dentro de la muestra: el
vocabulario `V0` se supone no ajustado con el corpus (C-27 lo redistribuyó con el corpus
ausente del repositorio; si los autores informan lo contrario la cota pasa a ser parcial);
(ii) `0,7405 − p_A` es una **cota pesimista** (por exceso), porque `V0` carece también del
conocimiento del dominio que una ampliación hecha con datos independientes habría aportado;
(iii) un resultado no significativo nunca se lee como ausencia de efecto; los `p` son
descriptivos y no llevan corrección por multiplicidad; (iv) E3 y E4 usan predicciones de Gemini de una corrida distinta de la oficial
(salvedad ya registrada en la Sección 3.9 y en el punto 7 de la Sección 7).

### 3.11 Balance neto de derivaciones erróneas (c-132)

**Condicional: no reemplaza valores canónicos.** Esta sección registra el cálculo que
cierra la observación A3 del dictamen CONEAU 2026-10-22 (`subsec:balance-neto` y
`tab:balance-neto` de `08-discusion.tex`). Todo valor derivado de la tasa manual `e_man`,
del costo por derivación errónea `c` o de la rejilla de sensibilidad lleva estado
`condicional`: son supuestos, no mediciones. NO modifica ningún valor de las Secciones 3.1
a 3.10; en particular, `32,2 h` sigue siendo el ahorro bruto vigente de la Sección 3.4.
Cálculo de solo lectura, sin invocar al clasificador (cero llamadas a Gemini).

**Insumos.**

| Insumo | Valor | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|---|
| Universo trimestral `N` | `≈ 2.646 = 42 × 63` | Sección 3.4; `04-marco-metodologico.tex:45,51` | vigente | Escala el balance, no su signo. |
| Ahorro medio por incidente `Δt` | `43,82 s` | Sección 3.1; `report.md:199` | vigente | El `.tex` lo aproxima como `43,8 s`. |
| Tasa de error estricta del clasificador `e_aut` | `0,265 = 53/200 = 1 − 0,7350` | `07-resultados.tex:74,128`; `report.md:20-21` | vigente (derivado) | El `26,5 %` no figura literalmente en el `.tex`. Es una cota **superior** de la tasa operativa de derivación errónea: el `53,5 %` de los casos (`107/200`, `07-resultados.tex:128`) admite más de un sector. |
| Tasa de derivación errónea manual `e_man` | `≈ 15 %` | `01-introduccion.tex:18` | condicional | Estimación **preliminar** de una semana de operación, de la misma naturaleza que los `2 min 45 s` luego corregidos a `61,6 s`; nunca re-medida. La exactitud del brazo manual sobre el corpus NO se midió: el corpus no registra por caso la derivación del operador (`12-anexos.tex`, `sec:anexo-corpus`) y los operadores son los mismos analistas que fijaron la referencia (`04-marco-metodologico.tex:55,87`). |
| Costo por derivación errónea `c` | `10 a 15 min` (`600-900 s`) | `01-introduccion.tex:48` | condicional | Estimación propia de los autores, sin registro cuantitativo conservado. |
| Rejilla de sensibilidad | `e_man ∈ {10 %, 15 %, 20 %, 26,5 %}`; `c ∈ {5, 10, 15} min` | c-132 (`design.md`, D3) | condicional | `10 %` y `20 %` son ±5 puntos alrededor del `15 %`; `26,5 %` es la paridad con el error automatizado; `5 min` es un escenario optimista por debajo de la estimación propia. Supuestos de sensibilidad, no datos. |
| Exactitud laxa `a_laxa` | `179/200 = 0,8950`, IC de Wilson `[0,8448; 0,9303]` (`[84,5 %; 93,0 %]`) | Sección 3.9 (c-131); `report.md:31-33` | vigente | Métrica secundaria; se cita sin recalcular. |

**Fórmulas** (`N` en incidentes por trimestre; `Δt` y `c` en segundos; `B` en horas-persona por trimestre):

- Balance neto: `B = (N / 3.600) × [Δt − (e_aut − e_man) × c]`. El primer sumando es el ahorro bruto (`32,2 h`); el segundo, el costo de las derivaciones erróneas adicionales.
- Exactitud mínima de equilibrio (`B = 0`): `a* = 1 − e_man − Δt / c`.
- Tasa de error automatizada máxima: `e_aut* = e_man + Δt / c`; exceso de error tolerable `Δe* = Δt / c` = `14,6 / 7,3 / 4,9` puntos porcentuales para `5 / 10 / 15 min`.
- Propiedad: `a*` no depende de `N`; el universo escala el balance pero no su signo.
- Supuestos: cada derivación errónea cuesta `c` en ambos flujos; el ahorro `Δt` aplica a todo `N`; la tasa automatizada es la del corpus; el flujo automatizado no agrega tiempo de revisión (el gate no derivó casos); relación lineal.

**Tabla de escenarios** (`Δt = 43,82 s`, `N = 2.646`, `e_aut = 53/200`; una decimal, mitad hacia arriba; `condicional`):

| `e_man` | `a*` 5 min | `a*` 10 min | `a*` 15 min | `B` 5 min | `B` 10 min | `B` 15 min |
|---|---|---|---|---|---|---|
| 10 % | 75,4 | 82,7 | 85,1 | −4,2 | −40,6 | −76,9 |
| 15 % | 70,4 | 77,7 | 80,1 | +6,9 | −18,5 | −43,9 |
| 20 % | 65,4 | 72,7 | 75,1 | +17,9 | +3,5 | −10,8 |
| 26,5 % | 58,9 | 66,2 | 68,6 | +32,2 | +32,2 | +32,2 |

**Escenario central** (`e_man = 15 %`; `c = 10 a 15 min`): derivaciones erróneas adicionales
`(0,265 − 0,15) × 2.646 = 304,3 ≈ 304` por trimestre; costo `50,7 h` (10 min) y `76,1 h`
(15 min); balance `−18,5 h` y `−43,9 h`; `a* = 77,7 %` y `80,1 %`; exceso de error observado
`11,5` puntos (`26,5 % − 15 %`). Con la exactitud estricta (`73,5 %`, IC `[67,0 %; 79,1 %]`):
`a*(15 %, 10 min) = 77,7 %` cae **dentro** del IC (ni con esos supuestos la muestra determina
el signo) y `a*(15 %, 15 min) = 80,1 %` supera su límite superior. `B > 0` con la exactitud
estricta solo si `e_man ≥ 20 %` con `c ≤ 10 min`, con `e_man = 15 %` y `c = 5 min`, o en
paridad (`e_man ≥ e_aut − Δt / c` = `11,9 / 19,2 / 21,6 %` para `5 / 10 / 15 min`).
**El balance es indeterminado con el diseño actual**: la tesis no enuncia su signo como resultado.

**Lectura laxa (rama "laxa disponible" de D4; `condicional`).** Con `e_aut = 1 − a_laxa = 0,105`
(sector principal dentro del conjunto de verdad), el mismo comando devuelve `B` (h por trimestre,
`c` = 5 / 10 / 15 min): `e_man = 10 %`: `+31,1 / +30,0 / +28,9`; `15 %`: `+42,1 / +52,1 / +62,0`;
`20 %`: `+53,2 / +74,1 / +95,1`; `26,5 %`: `+67,5 / +102,8 / +138,0`. La exactitud laxa
(`89,5 %`) supera los 12 valores de `a*` de la tabla (máximo `85,1 %`) y su límite inferior
(`84,5 %`) supera 11 de los 12. Es la cota **favorable**: supone que toda derivación a un sector
válido no genera reasignación, mientras que el `26,5 %` es la cota desfavorable; la tasa
operativa real queda entre ambas y no se midió.

**Sensibilidad opcional (E3 de c-142; no entra a la tesis).** Con el vocabulario previo a c-71
(`128/200`, `e_aut = 0,36`), `B(15 %)` = `−14,1 / −60,4 / −106,7 h` para `5 / 10 / 15 min`;
con el vigente de la corrida de Gemini fija (`146/200`, `e_aut = 0,27`) = `+5,7 / −20,7 / −47,2 h`.
Son lecturas de sensibilidad del ajuste del clasificador (Sección 3.10), condicionales.

**Comando de referencia** (solo lectura, sin invocar el clasificador):

```bash
python3 -c "
from decimal import Decimal as D, ROUND_HALF_UP
r=lambda x: D(x).quantize(D('0.1'), ROUND_HALF_UP)
dt, N, ea = D('43.82'), D('2646'), D(53)/D(200)
S = dt*N/3600
for em in ('0.10','0.15','0.20','0.265'):
    em = D(em)
    print(em, [r((1-em-dt/(60*c))*100) for c in (5,10,15)], [r(S-(ea-em)*N*c/60) for c in (5,10,15)])
"
```

Para la lectura laxa se reemplaza `ea` por `1-D(179)/D(200)`.

**Redondeo.** Una decimal, mitad hacia arriba, con `Δt = 43,82 s` (valor canónico de la
Sección 3.1). Con `Δt = 43,8 s` (la aproximación del `.tex`) difieren dos celdas en `0,1`:
`B(15 %, 5 min) = 6,8` y `B(10 %, 15 min) = −77,0`; la nota de la tabla declara la
convención. El `32,2 h` coincide con ambas.

**Reversibilidad.** Si una réplica mide `e_man` y `c` (registro por caso de la derivación
manual con etiquetadores distintos de los operadores y cronometraje de las reasignaciones;
`subsec:estudios-replicacion`), esta sección se actualiza (upsert), la tabla se recalcula y la
viabilidad operativa puede enunciarse en un sentido u otro. Hasta entonces los valores
permanecen `condicional`.

### 3.12 Hipótesis, objetivos y métrica primaria (c-133)

Cifras que el texto de c-133 cita y su procedencia. c-133 no calcula nada nuevo ni invoca a
Gemini: toda cifra proviene de las secciones 3.3, 3.7, 3.9 y 3.10 de este memo.

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Cota de la segunda sub-hipótesis: `0,15` (`= 1 − 0,85`) | `01-introduccion.tex` (segundo objetivo específico, umbral del `85 %`), subsec:hipotesis-trabajo | vigente | **Explicitada por c-133; no es un resultado.** Complemento del umbral de exactitud fijado a priori. Contraste: proporción con IC de Wilson al 95 %; se falsa si el límite superior no queda por debajo de `0,15`. Estado de la sub-hipótesis: *no contrastada por ausencia de registro primario*; la proporción no se cuantifica y el `0 de 200` del gate no se presenta como contraste (no operacionaliza la variable). No reintroduce el `9,5 %` (`retirado`). |
| Macro-F1 de umbral (cuatro clases estimables): `0,6508` | Sección 3.2 | vigente | Primario y único referente del `0,85` (c-133 D1). |
| Macro-F1 de cinco clases: `0,5207` | Sección 3.2 | vigente | Informativo; incluye Bases de Datos (`n = 1`, no estimable). |
| Etapa determinística: `97/131` = `0,7405` | Sección 3.7 (`docs/deterministic_calibration.md:40,67`) y Sección 3.9 | vigente | **Estimación dentro de la muestra** (Sección 3.10). |
| Gemini sobre `S`: `88/130` = `0,6769` | Sección 3.7 (`docs/deterministic_calibration.md:41-44,68`) | vigente | Cache FORCE-ESCALATE `hybrid-v2` (otra corrida que la oficial); un caso de `S` sin predicción, excluido y no fabricado. **Estimación dentro de la muestra.** |
| McNemar entre etapas sobre `S`: `b = 16`, `c = 8`, `p` exacto `0,1516` | Sección 3.9 | vigente | No significativo. c-133 lo cita; no lo calcula. |
| E4 (`V0`): reglas `38/73` = `0,5205` frente a Gemini `48/73` = `0,6575`, `p` exacto `0,0213` | Sección 3.10 | vigente | Con el vocabulario previo al ajuste la etapa de reglas **no supera** a Gemini. |
| `65,5 %` (`131/200`) y `34,5 %` (`69/200`) | Sección 3.3 | vigente | |
| Exactitud estricta por canal: `0,654` (llamada telefónica), `0,773` (correo), `0,811` (formulario web) | Sección 3.9 | vigente | Se cita en la fila del objetivo específico 3. |

**Regla de decisión aplicada (D3).** Con E4, la ventaja de la etapa de reglas sobre Gemini en
`S` depende del vocabulario ajustado con el propio corpus: la hipótesis subsidiaria de
eficiencia del esquema híbrido se rotula *no contrastada* en la introducción, la discusión y
las conclusiones. Las cifras `97/131`, `88/130` y la prueba de McNemar se citan como
descripción, no como contraste favorable. **Reversible si** el autor decide el rótulo
"contrastada de forma acotada" (variante principal de T10): se actualizan los sitios T3, T10,
T11 y T14 y esta sección.

**Reproducción.** Sin cifras propias: ver los comandos de reproducción de las Secciones 3.7, 3.9
y 3.10. No hubo llamadas a Gemini (`--confirm-paid`, `run_evaluation.py --force`).

## 4. Contingencia del gate de intervención humana

Tabla reconstruida desde `evaluation/predicciones.json` con
`contingencia_confianza(..., umbral = 0,70)`. Alta = `confianza ≥ 0,70` (no
escala a revisión); baja = `confianza < 0,70`.

| Segmento | Confianza `≥ 0,70` | Aciertos alta | Exactitud alta | Confianza `< 0,70` | Aciertos baja | Exactitud baja |
|---|---|---|---|---|---|---|
| Global (200) | 76 | 53 | 0,6974 | 124 | 94 | 0,7581 |
| Determinística (131) | 7 | 3 | 0,4286 | 124 | 94 | 0,7581 |
| Gemini (69) | 69 | 50 | 0,7246 | 0 | 0 | — |

- Los `124` casos con confianza `< 0,70` son **todos** de la etapa
  determinística.
- La etapa determinística asigna una confianza en `{0; 1/6 ≈ 0,1667; 0,5;
  0,75; 1,0}` y reporta `requiere_revision_humana = False` en todos los casos:
  el campo está fijado en `False` en esa etapa
  (`App/Backend/app/classifiers/deterministic.py:227-229,249,294`). Su
  `confianza` es una fuerza de señal, NO el disparador del gate; el
  cortocircuito de Gemini se decide por el `score_correctitud` calibrado, no
  por la confianza (`App/Backend/app/classifiers/hybrid.py:134-135,168`).
- La etapa Gemini asigna `confianza ∈ {0,85; 0,90; 0,95; 0,98}` y **nunca**
  por debajo de `0,85`. El gate implementado es
  `requiere_revision_humana = (confianza < 0,70)`
  (`App/Backend/app/classifiers/gemini_classifier.py:534`,
  `App/Backend/app/classifiers/hybrid.py:252`,
  `App/Backend/app/config/settings.py:117`). Como Gemini nunca baja de `0,85`,
  el umbral de confianza NO dispara revisión en ningún caso del corpus, y la
  etapa determinística nunca la activa.
- Conclusión operativa: la proporción de intervención humana derivable del gate
  de confianza implementado es `0 %`, no `9,5 %`. Esto desmiente el `9,5 %`
  como cifra derivable de las fuentes permitidas (ver Sección 7).
- **Lectura de la contingencia (c-131).** El contraste agregado `0,6974` (`≥ 0,70`) frente a `0,7581` (`< 0,70`) es un **efecto de composición entre etapas**, no evidencia sobre la calibración de la confianza del modelo: los `124` casos `< 0,70` son todos determinísticos y el segmento `≥ 0,70` reúne `7` determinísticos y los `69` de Gemini (`0,4286` y `0,7246`). La lectura de «calibración invertida o anti-calibrada» del clasificador en su conjunto queda **retirada** (Sección 3.9).
- **Alcance del gate por etapa (c-130).** La regla
  `requiere_revision_humana = (confianza < 0,70)` se evalúa **solo sobre la
  salida de Gemini**; la etapa de reserva marca revisión siempre (confianza
  `0,0` por construcción); la etapa determinística no deriva por su confianza
  desde c-74 (el cortocircuito se decide por `score_correctitud >=
  deterministic_score_threshold`). Los docstrings que atribuían la revisión al
  híbrido "de cualquier etapa" o declaraban un cortocircuito por confianza
  `0,90` se corrigen en c-130 (solo comentarios; el test de caracterización
  `tests/test_hybrid_classifier.py` fija el contrato). El backend tiene además
  un segundo disparador, ajeno al clasificador: reportante no identificado
  (VIS-005, c-82; `App/Backend/app/services/incidente_service.py:401-410`).

## 5. Decisiones por ítem

**Ítem 1 — Gate de intervención humana.** Regla implementada declarada en la
Sección 4. La cifra `9,5 %` se marca `retirado`: es un valor heredado del corpus
sintético descartado en C-27 (2026-09-11), que quedó sin re-medir sobre el
corpus real (`knowledge-base/01_vision_y_objetivos.md:39,44`;
`knowledge-base/README.md:32`) y que el gate implementado no reproduce (deriva
`0 %`). El aporte operativo se reformula como no medido hasta que el autor
aporte la tabla primaria de intervención por caso (§7, punto 1).

**Ítem 2 — Coherencia de etapas y bandas.** La distribución `131/69/0` es
consistente con las bandas: los `124` casos `< 0,70` son determinísticos y
Gemini nunca baja de `0,85`. La Tabla 7.5 (`98/26/6/31/39`) reproduce exacto
desde `predicciones.json`. No hay contradicción interna entre etapas y bandas;
la contradicción era entre la Tabla 7.5 y el `9,5 %` (ítem 1).

*Anotación c-131 (2026-10-25).* El gradiente de la Tabla 7.5 entre las bandas bajas y las altas es un efecto de composición entre etapas: las bandas `< 0,70` son determinísticas y las `≥ 0,85` son casi solo de Gemini (más un caso determinístico). La descomposición por etapa que reproduce `98/26/6/31/39` y `75/19/2/22/29` está en la Sección 3.9. Ningún valor `vigente` de este ítem cambia; la lectura de anti-calibración del clasificador en su conjunto figura como **retirada**.

**Ítem 3 — Tramo "46 casos ≥ 0,90 con 13 errores".** Reproducible desde
`predicciones.json`: `46` casos con `confianza ≥ 0,90`, de los cuales `13` son
errores (`28,3 %`). Composición: `45` Gemini + `1` determinístico. El tramo NO
se deduce de la Tabla 7.5 publicada tal como está (la banda `[0,85;0,95]` tiene
`31` casos y la `[0,95;1,00]` tiene `39`; `0,90` corta dentro de la primera
banda). La rama que reescriba `07-resultados.tex:189` debe conservar la
referencia textual a la banda como criterio o justificar por separado el corte
en `0,90`.

**Ítem 4 — Universo y proyección horaria.** Se documentan ambas lecturas. Se
adopta como canónico el criterio de DÍAS HÁBILES (`≈ 2.646`; `≈ 32,2 h`), por
coherencia con la tasa diaria de `42` incidentes tomada de una semana laboral
(`01-introduccion.tex:18`); el valor calendario (`3.700`; `45,0 h`) se conserva
como `retirado`. Propagación obligatoria: `04-marco-metodologico.tex:45` y
`04-marco-metodologico.tex:51` (universo y fórmula de tamaño muestral),
`08-discusion.tex:14` (proyección) y `09-conclusiones.tex:24` (referencia
cualitativa al ahorro). Advertencia de arrastre (actualizada por c-145,
2026-10-26): la fórmula de tamaño muestral de `04-marco-metodologico.tex:51`
ya usa `N ≈ 2.646`; el margen quedó recalculado y registrado como `6,66 %` con
`N ≈ 2.646` (Sección 3.4, upsert c-145; ver §7, punto 2).

**Ítem 5 — Paradigma métrico.** La verdad de referencia es MULTIETIQUETA
(`107/200 = 53,5 %` de los casos del corpus tienen más de un sector de verdad;
distribución de tamaño de conjunto: 1 etiqueta `93`, 2 etiquetas `82`, 3
etiquetas `23`, 4 etiquetas `1`, 5 etiquetas `1`). El clasificador emite UNA
etiqueta principal más, en `8` casos, etiquetas adicionales predichas. Set
métrico final:
- Primario monoetiqueta: exactitud estricta `0,7350` e IC Wilson; macro-F1
  `0,5207`. *(Superado por c-133 D1: el primario de umbral es `0,6508`; `0,5207`
  es informativo y se cita siempre con su aclaración.)*
- Secundario multietiqueta (contra la referencia multietiqueta declarada del
  corpus): subset accuracy `0,43`, Hamming loss `0,3586` y micro-F1 `0,6654`,
  con la advertencia de penalización estructural. El micro-F1 NO debe
  presentarse como equivalente de la exactitud de etiqueta única.
- Corregir la caracterización de `design.md`: los `8` casos con
  `sectores_adicionales` no vacío son etiquetas **predichas** adicionales
  (`predicciones.json`), y NO son la referencia multietiqueta; la referencia
  multietiqueta del corpus tiene `107` casos. Ver §7, punto 3.

**Ítem 6 — Clase `Bases de Datos` (`n = 1`).** Se declara NO ESTIMABLE y se
excluye del macro-F1 de umbral. Se reporta el macro-F1 con las cinco clases
(`0,5207`, informativo) y el macro-F1 sobre las cuatro clases estimables
(`0,6508`, métrica de umbral propuesta). El umbral `0,85` se informa sobre
métricas sin la clase no estimable. El `0,0000` de `Bases de Datos` no debe
presentarse como evidencia de desempeño del clasificador.

**Ítem 7 — Tabla canónica final.** Constituida por las Secciones 3.1 a 3.5.
Todo número citable de la tesis debe figurar en ella.

## 6. Evidencia (archivo y línea)

Fuentes primarias (solo lectura, sin edición):

- `evaluation/predicciones.json` — 200 predicciones; campos `caso_id`,
  `sector_asignado`, `sector_predicho`, `confianza`, `etapa`,
  `sectores_adicionales`; `cache_meta.corpus_hash` verificado.
- `evaluation/report.md` — líneas `3`, `11-13`, `20-22`, `51-55`, `59-63`, `185`,
  `189`, `199`, `202` y `256` (SHA-256; era `99` antes de c-134 y `140` antes de c-131,
  que agrega la procedencia, la exactitud laxa y cuatro secciones antes de "## Tiempos"),
  más las líneas `5`, `31-33`, `72-76`, `84-88`, `113-116`, `124-127`, `136-150` y
  `159-168` de las secciones de c-131 (Sección 3.9).
- `data/corpus_evaluacion_pseudonimizado.json` — verdad multietiqueta (200
  casos); SHA-256 verificado contra `report.md:256`.
- `evaluation/metrics.py` — `calibracion_por_bandas`, `contingencia_confianza`,
  `exactitud_subconjunto`, `perdida_hamming`, `f1_micro`, `jaccard_promedio`,
  `f1_macro`, `intervalo_wilson`, `intervalos_por_clase`, `intervalos_conjunto`.
- `App/Backend/app/classifiers/deterministic.py`, `.../hybrid.py`,
  `.../gemini_classifier.py`, `App/Backend/app/config/settings.py` — regla del
  gate (Sección 4).

Capítulos de la tesis citados (NO editados en este change):
`00-resumen.tex:11,13`; `01-introduccion.tex:18`;
`04-marco-metodologico.tex:45,51`;
`07-resultados.tex:10,22,57,61,63,76,108,119-121,136,138,141-145,157-159,166-187,189`;
`08-discusion.tex:8,14,22,30,34,56`; `09-conclusiones.tex:6,16,24`;
`10-recomendaciones.tex:24`.

### Nota sobre numeración de líneas

Las líneas se citan según la numeración que usan los editores y Python
(`str.splitlines`, universal newlines), que es la misma que emplea `design.md`
de este change. El archivo `07-resultados.tex` contiene un único carácter CR
suelto en su línea 17 (dentro del bloque de la matriz de confusión); las
herramientas que solo cortan por LF (`grep -n`, `sed -n`, `awk`) reportan un
número distinto para todas las líneas posteriores a la 17 (por ejemplo, el
párrafo del marco métrico aparecía en `grep -n` con un número menor que el que
usa `splitlines`).
El contenido de cada línea citada fue verificado; los demás archivos no tienen
CR sueltos y su numeración coincide en todas las herramientas.

*Actualización c-131 (2026-10-25).* En el árbol de trabajo vigente `07-resultados.tex` ya no tiene el CR suelto (`splitlines` y `grep -n` coinciden) y las remisiones a los `.tex` editados por c-131 se actualizaron por correspondencia de contenido: el párrafo del marco métrico, citado antes como `:108`, está hoy en `:128`; `tab:bandas` y la calibración pasan de `145-165` a `166-187` (la sección de calibración cierra en `:189`); las citas de `08-discusion.tex` posteriores al párrafo de gate (`:16`) se corren `+2`.

## 7. Decisiones no resolubles

Cada punto que la evidencia disponible no permite cerrar se declara aquí con la
decisión editorial adoptada y su condición de reversibilidad.

1. **Proporción de intervención humana (`9,5 %`, `19` casos).** No existe
   registro por caso de la intervención humana en `evaluation/predicciones.json`,
   `evaluation/report.md` ni `data/`. El valor proviene del corpus sintético de
   200 casos descartado en C-27 (2026-09-11): figura como `100 % → 9,5 % — a
   re-medir` en `knowledge-base/01_vision_y_objetivos.md:44` (nota en `:39`) y en
   `knowledge-base/README.md:32` como un resultado «descartado ... superado por
   C-27» que quedó sin recomputar sobre el corpus real. El gate de confianza
   implementado (`confianza < 0,70`) derivaría `0 %`, no `9,5 %` (Sección 4).
   Además, `19` no coincide con ningún subconjunto derivable de las predicciones
   (`124` casos `< 0,70`, `46 ≥ 0,90`, `8` con etiquetas adicionales).
   **Decisión adoptada**:
   RETIRAR el `9,5 %` como cifra de resultado y reformular el aporte operativo
   como "intervención por gate no medida". **Reversible si**: el autor aporta la
   tabla de contingencia primaria (intervención por caso). En ese caso el memo se
   actualiza (upsert) y se propaga.

2. **Criterio de universo (`3.700` vs `≈ 2.646`).** El `3.700 = 42 × 88`
   combina una tasa de `42` incidentes/día tomada de una semana laboral
   (`01-introduccion.tex:18`) con `88` días calendario. **Decisión adoptada**:
   adoptar días hábiles (`≈ 2.646`, `≈ 32,2 h`) y retirar el valor calendario.
   **Reversible si**: el autor ratifica el criterio calendario. **Advertencia de
   arrastre (actualizada por c-145, 2026-10-26)**: el cambio de `N` afecta la
   fórmula de tamaño muestral de `04-marco-metodologico.tex:51`. El margen ya
   quedó recalculado y registrado como `6,66 %` con `N ≈ 2.646` (Sección 3.4,
   upsert c-145): el capítulo publica ese valor y la fórmula reproduce
   `n ≈ 200,2`. El margen `6,74 %` calibrado con `N = 3.700` queda `retirado` y
   no debe citarse como vigente. La decisión de universo no cambia.

3. **Referencia multietiqueta (interpretación).** `design.md` describe los `8`
   casos con `sectores_adicionales` como "referencia multietiqueta parcial".
   Verificado: en `predicciones.json` los `8` son etiquetas **predichas**
   adicionales del clasificador, mientras que la referencia del corpus tiene
   `107` casos multietiqueta (`53,5 %`). **Decisión adoptada**: la referencia es
   multietiqueta (corpus, `107` casos) y se documenta el recuento en ambos
   archivos para evitar la confusión. **Reversible**: no; es una corrección de
   exactitud.

4. **Clase `Bases de Datos` (`n = 1`).** La métrica de umbral `0,85` depende de
   si se excluye la clase no estimable. **Decisión adoptada**: declararla no
   estimable y reportar el umbral sobre las cuatro clases estimables
   (macro-F1 `0,6508`), conservando el macro-F1 de cinco clases (`0,5207`) como
   valor informativo. **Reversible si**: el autor prefiere reportar el `0,5207`
   como métrica principal. *(Decisión ratificada por c-133 D1, 2026-10-25: `0,6508`
   es el primario y único referente del umbral `0,85`; la reversibilidad se
   mantiene.)*

5. **Corte en `0,90` del tramo de alta confianza.** El texto cita `46` casos
   `≥ 0,90`, cifra reproducible pero no deducible de la Tabla 7.5 publicada.
   **Decisión adoptada**: conservar el valor `46/13` (reproducible) y declarar
   que su procedencia es el recálculo directo, no la tabla de bandas.
   **Reversible**: no; el número es correcto.

6. **Conjunto de ~100 incidentes de preproducción (no verificable).**
   `12-anexos.tex:135` y `docs/anexo_h_prompt_gemini.md:160` afirmaban que el
   prompt se ajustó sobre "aproximadamente 100 incidentes representativos en
   entornos de preproducción". Verificado: ese conjunto no existe ni existió en
   el repositorio (`data/` y `evaluation/` solo contienen el corpus de 200 casos
   y sus derivados; `rg -l "incidentes de preproduccion" data/ evaluation/` sin
   resultados) y el directorio `docs/prompt_gemini_history/` nunca existió en el
   historial de git (sin commit, sin entrada en `git ls-files`, sin rama).
   **Decisión adoptada**: declarar la procedencia real (los ajustes se derivaron
   del corpus de evaluación) y registrar el desenlace "no existen / no se localizan"
   del conjunto; el texto del Anexo H depende de esta declaración
   (`docs/anexo_h_prompt_gemini.md:160/162`). **Reversible si**: el autor aporta
   el conjunto independiente pseudonimizado; en ese caso corresponde un change de
   gobernanza HIGH propio.

7. **Procedencia de la cache FORCE-ESCALATE y estimaciones dentro de la
   muestra (c-130).** `precision_gem(S) = 88/130` (Sección 3.7) se calculó sobre
   la cache FORCE-ESCALATE (`evaluation/predicciones_calibracion.json`), que
   sigue ignorada por `.gitignore` y no existe en el árbol de trabajo. Desde
   c-143 existe una copia congelada y versionada
   (`evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json`)
   cuyo `cache_meta` aporta: `classifier_version = hybrid-v2`, `generated_at =
   2026-10-07T20:33:03Z` y `corpus_count = 200`; con ella se **reprodujo
   offline** el `88/130 = 0,6769` el 2026-10-25 (199 predicciones de Gemini y 1
   determinística; las 200 descripciones coinciden con el corpus vigente).
   Siguen **sin documentarse**: la versión del prompt con que se generó esa
   cache (el `cache_meta` solo registra la etiqueta `hybrid-v2`) y el motivo de
   que su `corpus_hash` (`5f062e14…`) difiera del hash vigente (`1fd17d7e…`)
   pese a que las descripciones coinciden. **Decisión adoptada**: citar `88/130`
   como cifra de `docs/deterministic_calibration.md` con esta salvedad y no
   fabricar la versión del prompt. **Reversible si** el autor aporta la versión
   del prompt de esa corrida. Además, `97/131` y la exactitud global son
   **estimaciones dentro de la muestra** (el vocabulario del filtro, las reglas
   de frontera del prompt y el punto de operación se ajustaron sobre el mismo
   corpus: c-71, c-72, c-74), probablemente optimistas; su confirmación exige
   un corpus independiente (`08-discusion.tex:20`, `subsec:corpus-independiente`).

8. **Variante por pliegues del vocabulario: no factible (c-142).** El dictamen
   sugiere reconstruir el vocabulario por pliegues. Eso exige saber qué casos del
   corpus motivaron cada uno de los `62` patrones que agregó c-71 (commit `1368fd8`);
   el diff solo trae cinco comentarios de bloque por sector y las propuestas, el diseño
   y las tareas de c-71 describen el procedimiento en forma genérica. Cualquier
   atribución por pliegues requeriría una regla no verificable cuyo resultado dependería
   de la regla elegida. **Decisión adoptada**: declararla no factible, con ese motivo, en
   `evaluation/report_sensibilidad_ajustes.md:70-72` y en una oración de la tesis; la
   aproximación por coincidencia (exploratoria) no se ejecuta. **Reversible si** los
   autores aportan la atribución por patrón (Open Question 4 de c-142: respuesta
   PROVISIONAL, recomendación del design).

9. **Versión del prompt de la FORCE-ESCALATE (c-142, D9).** El `cache_meta.generated_at`
   de la copia congelada (`evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json`)
   es `2026-10-07T20:33:03.438926+00:00`, posterior a la aplicación de c-72
   (`a76851e`, 2026-10-06T19:38:20Z). Clasificación según D9: **"posterior"**; el nivel b
   de la sensibilidad del prompt (comparación pareada contra la corrida oficial) **no
   aplica**. La suposición de la propuesta de c-142 (cache generada el 2026-10-05, antes
   de las reglas de frontera) queda refutada por su `cache_meta`. Esto acota, sin cerrar,
   el punto 7: sigue sin registrarse qué archivo de prompt cargó esa corrida, pero la
   fecha impide atribuirle el prompt previo a c-72. **Decisión adoptada**: no fabricar la
   versión del prompt; informar la clasificación y su fecha. **Reversible si** el autor
   de la corrida aporta la versión del prompt (Open Question 5 de c-142).

---

_Producido por c-102 (Gate 0). Cualquier rama que reescriba `04`, `07`, `08` o
`09` —incluida c-104— debe citar únicamente los valores `vigente` de la
Sección 3._

_Sección 3.6 agregada por c-108 (upsert, 2026-10-21): marco métrico unificado e
intervalos de confianza. No altera los valores canónicos de las Secciones 3.1 a
3.5._
