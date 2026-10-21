# Números canónicos de la tesis v9 — Gate 0 (c-102)

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
| Tiempo manual medio: `61,6 s` | `07-resultados.tex:10`, `07-resultados.tex:22`, `00-resumen.tex:13` | vigente | Medición por caso; reemplaza la estimación preliminar de 2 min 45 s (`01-introduccion.tex:18`). |
| Tiempo automatizado medio: `17,76 s` | `07-resultados.tex:10`, `07-resultados.tex:22`, `00-resumen.tex:13` | vigente | Mediana `17,47 s` (`07-resultados.tex:22`). |
| Reducción relativa de tiempo: `71,2 %` | `07-resultados.tex:10`, `07-resultados.tex:22`, `08-discusion.tex:8` | vigente | Cota superior (manual redondeado al alza, `07-resultados.tex:63`). |
| Reducción media por incidente: `43,82 s` | `report.md:83` | vigente | El `.tex` la aproxima como `43,8 s` (`08-discusion.tex:14`). |
| Wilcoxon `W = 363` | `07-resultados.tex:55`, `00-resumen.tex:13` | vigente | `W = min(T+, T−)`, dos colas (`report.md:69`). |
| `T+ = 19.737`, `T− = 363` | `report.md:73`, `07-resultados.tex:55` | vigente | |
| p-valor `p = 3,08e-32` | `07-resultados.tex:55`, `00-resumen.tex:13` | vigente | |
| Tamaño del efecto `r = 0,9639` | `07-resultados.tex:55`, `07-resultados.tex:61`, `00-resumen.tex:13` | vigente | |
| Pares a favor `188 / 200` (`94,0 %`) | `07-resultados.tex:55`, `07-resultados.tex:61`, `09-conclusiones.tex:16` | vigente | Pares no a favor: `12` (`report.md:86`). |

### 3.2 Clasificación (métricas)

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Exactitud estricta: `0,7350` (`73,5 %`; `147/200`) | `report.md:18`, `07-resultados.tex:108`, `07-resultados.tex:76` | vigente | Métrica primaria monoetiqueta. |
| IC Wilson 95 %: `[0,6698; 0,7913]` (`[67,0 %; 79,1 %]`) | `report.md:20`, `07-resultados.tex:108` | vigente | |
| Macro-F1 (5 clases): `0,5207` | `report.md:52`, `07-resultados.tex:108`, `08-discusion.tex:30` | vigente | Valor informativo; incluye la clase no estimable. |
| Macro-F1 (4 clases estimables): `0,6508` | recálculo (`metrics.py`) | condicional | Métrica de umbral propuesta (decisión D7); excluye `Bases de Datos`. |
| Micro-F1 (multietiqueta): `0,6654` | `report.md:51`, `07-resultados.tex:108` | vigente | Métrica multietiqueta; NO es equivalente de la exactitud. |
| Subset accuracy: `0,43` | `report.md:49`, `07-resultados.tex:108` | vigente | Contra la referencia multietiqueta. |
| Hamming loss: `0,3586` | `report.md:50`, `07-resultados.tex:108` | vigente | Contra la referencia multietiqueta. |
| Jaccard (IoU) promedio: `0,6414` | `report.md:53` | informativo | No citado en los `.tex` del alcance. |
| F1 por clase | `report.md:41-45`, `07-resultados.tex:119-123` | vigente | Hardware `0,8800`; Software `0,7111`; Seguridad `0,6122`; Sistemas `0,4000`; Bases de Datos `0,0000`. |

### 3.3 Pipeline y confianza

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Etapa determinística: `131` | `report.md:9`, `07-resultados.tex:108` | vigente | |
| Etapa Gemini: `69` | `report.md:10`, `07-resultados.tex:108` | vigente | |
| Etapa fallback: `0` | `report.md:11` | vigente | |
| Bandas de confianza: `98 / 26 / 6 / 31 / 39` | `07-resultados.tex:154-158` | vigente | Reproduce la Tabla 7.5 (`07-resultados.tex:145-163`). |
| Tramo confianza `≥ 0,90`: `46` casos, `13` errores | `07-resultados.tex:165` | vigente | Ver Sección 5, ítem 3. |

### 3.4 Intervención humana, universo y proyección

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| Intervención humana: `9,5 %` (`19/200`; `181/200` sin intervención) | `07-resultados.tex:138`, `00-resumen.tex:13`, `08-discusion.tex:14`, `09-conclusiones.tex:16`, `10-recomendaciones.tex:24` | **retirado** | Valor heredado del corpus sintético descartado en C-27 (2026-09-11), sin re-medir (`knowledge-base/01_vision_y_objetivos.md:39,44`; `knowledge-base/README.md:32`); NO derivable del corpus real. Ver Sección 7. |
| Universo calendario: `3.700 = 42 × 88` | `04-marco-metodologico.tex:45`, `04-marco-metodologico.tex:51` | **retirado** | Criterio incoherente con la tasa diaria de origen semanal. |
| Universo días hábiles: `≈ 2.646 = 42 × 63` | recálculo (`88 × 5/7 ≈ 62,86 ≈ 63` días hábiles) | vigente | Valor canónico propuesto (decisión D5). |
| Proyección calendario: `45,0 h` | `08-discusion.tex:14`, `01-introduccion.tex:18` | **retirado** | `43,82 × 3.700 / 3.600 = 45,04 h`. |
| Proyección días hábiles: `≈ 32,2 h` | recálculo | vigente | `43,82 × 2.646 / 3.600 = 32,21 h`. |

### 3.5 Referencias de corpus

| Valor canónico | Procedencia (archivo:línea) | Estado | Notas |
|---|---|---|---|
| SHA-256 del corpus | `report.md:99` | vigente | `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`. |
| Tamaño del corpus: `n = 200` | `report.md:3`, `04-marco-metodologico.tex:45` | vigente | |
| Kappa de Cohen: `0,87` (doble etiquetado) | `00-resumen.tex:11` | vigente | Contexto de validez; no es una métrica del clasificador. Su IC **no es computable** desde las fuentes permitidas (ver 3.6). |
| Soporte `Bases de Datos`: `n = 1` | `report.md:44`, `08-discusion.tex:22` | vigente | Clase NO estimable (`F1 = 0,0000`). Ver ítem 6. |

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

**Ítem 3 — Tramo "46 casos ≥ 0,90 con 13 errores".** Reproducible desde
`predicciones.json`: `46` casos con `confianza ≥ 0,90`, de los cuales `13` son
errores (`28,3 %`). Composición: `45` Gemini + `1` determinístico. El tramo NO
se deduce de la Tabla 7.5 publicada tal como está (la banda `[0,85;0,95]` tiene
`31` casos y la `[0,95;1,00]` tiene `39`; `0,90` corta dentro de la primera
banda). La rama que reescriba `07-resultados.tex:165` debe conservar la
referencia textual a la banda como criterio o justificar por separado el corte
en `0,90`.

**Ítem 4 — Universo y proyección horaria.** Se documentan ambas lecturas. Se
adopta como canónico el criterio de DÍAS HÁBILES (`≈ 2.646`; `≈ 32,2 h`), por
coherencia con la tasa diaria de `42` incidentes tomada de una semana laboral
(`01-introduccion.tex:18`); el valor calendario (`3.700`; `45,0 h`) se conserva
como `retirado`. Propagación obligatoria: `04-marco-metodologico.tex:45` y
`04-marco-metodologico.tex:51` (universo y fórmula de tamaño muestral),
`08-discusion.tex:14` (proyección) y `09-conclusiones.tex:24` (referencia
cualitativa al ahorro). Advertencia de arrastre: la fórmula de tamaño muestral
de `04-marco-metodologico.tex:51` usa `N = 3.700`; al adoptar `≈ 2.646` debe
recalcularse el margen de error asociado (ver §7, punto 2).

**Ítem 5 — Paradigma métrico.** La verdad de referencia es MULTIETIQUETA
(`107/200 = 53,5 %` de los casos del corpus tienen más de un sector de verdad;
distribución de tamaño de conjunto: 1 etiqueta `93`, 2 etiquetas `82`, 3
etiquetas `23`, 4 etiquetas `1`, 5 etiquetas `1`). El clasificador emite UNA
etiqueta principal más, en `8` casos, etiquetas adicionales predichas. Set
métrico final:
- Primario monoetiqueta: exactitud estricta `0,7350` e IC Wilson; macro-F1
  `0,5207`.
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
- `evaluation/report.md` — líneas `3`, `9-11`, `18-20`, `41-45`, `49-53`,
  `69`, `73`, `83`, `86`, `99`.
- `data/corpus_evaluacion_pseudonimizado.json` — verdad multietiqueta (200
  casos); SHA-256 verificado contra `report.md:99`.
- `evaluation/metrics.py` — `calibracion_por_bandas`, `contingencia_confianza`,
  `exactitud_subconjunto`, `perdida_hamming`, `f1_micro`, `jaccard_promedio`,
  `f1_macro`, `intervalo_wilson`, `intervalos_por_clase`, `intervalos_conjunto`.
- `App/Backend/app/classifiers/deterministic.py`, `.../hybrid.py`,
  `.../gemini_classifier.py`, `App/Backend/app/config/settings.py` — regla del
  gate (Sección 4).

Capítulos de la tesis citados (NO editados en este change):
`00-resumen.tex:11,13`; `01-introduccion.tex:18`;
`04-marco-metodologico.tex:45,51`;
`07-resultados.tex:10,22,55,61,63,76,108,119-123,136,138,145-163,165`;
`08-discusion.tex:8,14,22,30,34,56`; `09-conclusiones.tex:6,16,24`;
`10-recomendaciones.tex:24`.

### Nota sobre numeración de líneas

Las líneas se citan según la numeración que usan los editores y Python
(`str.splitlines`, universal newlines), que es la misma que emplea `design.md`
de este change. El archivo `07-resultados.tex` contiene un único carácter CR
suelto en su línea 17 (dentro del bloque de la matriz de confusión); las
herramientas que solo cortan por LF (`grep -n`, `sed -n`, `awk`) reportan un
número **uno menor** para todas las líneas posteriores a la 17 (por ejemplo, el
párrafo citado como `07-resultados.tex:108` aparece como `:107` en `grep -n`).
El contenido de cada línea citada fue verificado; los demás archivos no tienen
CR sueltos y su numeración coincide en todas las herramientas.

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
   arrastre**: el cambio de `N` afecta la fórmula de tamaño muestral de
   `04-marco-metodologico.tex:51` (margen de error del `6,74 %` calibrado con
   `N = 3.700`); la rama que edite ese capítulo debe recalcular el margen o
   justificar la conservación de `N`.

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
   como métrica principal.

5. **Corte en `0,90` del tramo de alta confianza.** El texto cita `46` casos
   `≥ 0,90`, cifra reproducible pero no deducible de la Tabla 7.5 publicada.
   **Decisión adoptada**: conservar el valor `46/13` (reproducible) y declarar
   que su procedencia es el recálculo directo, no la tabla de bandas.
   **Reversible**: no; el número es correcto.

---

_Producido por c-102 (Gate 0). Cualquier rama que reescriba `04`, `07`, `08` o
`09` —incluida c-104— debe citar únicamente los valores `vigente` de la
Sección 3._

_Sección 3.6 agregada por c-108 (upsert, 2026-10-21): marco métrico unificado e
intervalos de confianza. No altera los valores canónicos de las Secciones 3.1 a
3.5._
