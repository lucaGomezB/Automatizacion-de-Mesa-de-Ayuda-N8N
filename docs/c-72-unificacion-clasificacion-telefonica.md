# c-72 — Unificacion de la clasificacion telefonica: decisiones y nota de evaluacion

Change: `c-72-unificar-clasificacion-telefonica`.
Este documento registra las decisiones resueltas por el autor y la nota de
evaluacion del beneficio determinista-primero para el canal telefonico.

> Estado de los numeros: FINALES. El corpus de evaluacion esta completo (200
> casos; 81 con `canal_origen == "llamada telefónica"`) y los valores numericos
> de esta nota son mediciones reales con peso de decision. El punto de operacion
> del cortocircuito determinista es el comparativo de c-74
> (`Settings.deterministic_score_threshold = 0.5166`, derivado out-of-fold),
> que reemplaza al piso absoluto 1.0 de c-71. Medicion offline sobre el corpus
> real y sobre la corrida oficial cacheada; sin invocar Gemini.

## 1. Decisiones del autor (resueltas y vinculantes)

| OQ | Decision | Efecto |
|----|----------|--------|
| OQ1 | A | El `AI Agent` de telefonia se retira; hay UN clasificador (la cascada del backend) para los tres canales. |
| OQ2 | A | Traslado de costo confirmado: la telefonia no reserva `n8n_gemini`; la escalacion reserva `backend_gemini`. |
| OQ4 | A | SIN backfill de incidentes telefonicos historicos. Declarado fuera de alcance (ver seccion 3). |
| OQ5 | A | Se adoptan, de forma verbatim, las reglas minimas de frontera del diseno en el prompt compartido. |

Las reglas de frontera adoptadas (OQ5 = A) son:

- Acciones sobre aplicaciones o sistemas operativos (acceder, iniciar sesion,
  abrir una aplicacion) -> `Soporte Tecnico Software`.
- Dispositivos fisicos y su digitalizacion (escaner, impresora, periferico,
  error de digitalizacion) -> `Soporte Tecnico Hardware`.
- Infraestructura y servicios de plataforma (servidor, red, SMTP, VM) ->
  `Sistemas`.

## 2. Camino unico de clasificacion y traslado de costo

- El backend es propietario de la clasificacion telefonica: la resuelve con la
  cascada hibrida (determinista -> Gemini -> revision humana) sobre la
  descripcion pseudonimizada, igual que correo y web.
- El handoff telefonico no transporta una clasificacion precalculada; el canal
  no puede omitir la cascada.
- Hay un solo prompt de clasificacion (`docs/prompt_gemini.txt`), con las reglas
  de frontera de la seccion 1; no hay prompt divergente en N8N.
- Costo: la clasificacion telefonica no reserva `n8n_gemini`; la escalacion
  reserva `backend_gemini`. El atajo determinista, cuando aplica, no invoca a
  Gemini y no consume cuota.

Referencias de documentacion alineada: `docs/anexo_h_prompt_gemini.md` (H.6) y
la narrativa de tesis en `docs/Tesis/v9 (IA)/paper/sections/` (Capitulos 5, 6 y 8).

## 3. Fuera de alcance: backfill de incidentes historicos (tarea 6.3, OQ4 = A)

El alcance de c-72 es la unificacion del camino de clasificacion, no la
correccion de datos ya persistidos. Por decision del autor (OQ4 = A), el
backfill de incidentes telefonicos historicos creados con una clasificacion
precalculada queda **explicitamente FUERA DE ALCANCE** de este change:

- No se re-clasifican ni se mutan incidentes telefonicos existentes.
- No hay migracion de datos ni tarea de reparacion retroactiva.
- Los incidentes creados bajo la vigencia del change conservan el sector con el
  que fueron persistidos.

Si el autor decide abordar el backfill en el futuro, debe tratarse como un
change separado con su propio spec, plan de migracion y gobernanza.

## 4. Nota de evaluacion: beneficio determinista-primero (tarea 5.3)

### 4.1. Mecanismo

Cuando la telefonia clasifica por la cascada del backend, cada caso pasa
primero por el filtro determinista. Si el filtro alcanza el umbral calibrado,
el incidente se resuelve sin invocar a Gemini (Gemini evitado). Solo los casos
que no alcanzan el umbral escalan a la etapa semantica, donde aplica la reserva
`backend_gemini`. El beneficio esperado del change es, por lo tanto, una
fraccion de casos telefonicos resueltos sin costo de inferencia externa.

### 4.2. Medicion offline (tarea 5.1)

Medicion OFFLINE sobre los 81 casos telefonicos del corpus (canal
`llamada telefónica`), sin invocar Gemini y sin tocar
`evaluation/corpus.py::_a_float`. El punto de operacion vigente es el
**comparativo** de c-74 (`Settings.deterministic_score_threshold = 0.5166`,
derivado out-of-fold en `evaluation/deterministic_measurement.py`), no el piso
absoluto 1.0 de c-71. El cortocircuito ocurre cuando la senal es dominante (no
`sin_prediccion` y no ambigua) y el `score_correctitud >= 0.5166`.

| Metrica | Valor |
|---------|-------|
| Casos telefonicos medidos | 81 |
| Umbral determinista vigente (tau, c-74) | 0.5166 |
| Cortocircuitados (senal no ambigua y score >= tau) | 58 |
| Tasa de cortocircuito (cobertura del cortocircuito) | 0.7160 (58/81) |
| Exactitud estricta del subconjunto cortocircuitado | 0.6207 (36/58) |
| Cobertura del vocabulario (telefonia) | 0.7407 (21 sin match) |
| Exactitud estricta del determinista (telefonia) | 0.4444 |
| F1 macro estricto del determinista (telefonia, None = error) | 0.3810 |

Interpretacion: con el punto de operacion comparativo de c-74 (tau 0.5166) el
cortocircuito telefonico es 0.7160 (58/81), con una exactitud estricta de 0.6207
sobre el subconjunto cortocircuitado. El beneficio de costo de c-72 SI se
materializa: 58 de cada 81 llamadas se resuelven sin invocar a Gemini. El umbral
absoluto 1.0 de c-71 producia 0 cortocircuitos (ver historial de esta nota); la
revision comparativa de c-74 es la que habilita el atajo.

La exactitud estricta del determinista (0.4444) y su F1 macro estricto (0.3810)
se miden sobre los 81 casos y son invariantes al umbral (describen al
determinista como clasificador, con `None = error`); coinciden con la
convencion de `docs/deterministic_calibration.md` (F1 macro 0.4196 sobre los 200
casos). Bajo la convencion de pares canonicos (la de
`evaluation/run_evaluation.py`), el F1 macro del determinista en telefonia es
0.4536; ver la nota de metodo en 4.3.

### 4.3. Medicion hibrida (tarea 5.2)

Medicion sobre los 81 casos telefonicos usando la corrida OFICIAL cacheada
(`evaluation/predicciones.json`, `cache_meta.classifier_version = hybrid-v3`),
sin invocar Gemini. Las metricas se calculan como en
`evaluation/run_evaluation.py::generar_reporte` (pares canonicos para el F1
macro; `conjunto_verdad` contra el conjunto predicho filtrado para micro y
subset):

| Metrica | Valor |
|---------|-------|
| Exactitud estricta | 0.6543 |
| F1 macro estricto | 0.4783 |
| F1 micro | 0.6034 |
| Subset accuracy | 0.3580 |
| Etapa determinista (cortocircuito) | 58 |
| Etapa Gemini | 23 |
| Etapa fallback | 0 |
| Delta F1 macro (hibrido - determinista) | +0.0974 |

El delta positivo en F1 macro (+0.0974) confirma que, en telefonia, escalar los
23 casos sin senal dominante o con score insuficiente a la etapa semantica
mejora la clasificacion respecto de dejar solo al determinista. La tasa de
cortocircuito de la corrida oficial (58/81 = 0.7160) coincide con la medicion
offline de 4.2, lo que valida la consistencia entre el cache y el clasificador
determinista actual.

Nota de metodo (delta): el delta principal usa el F1 macro del determinista con
`None = error` (0.3810), la misma convencion que la referencia global de
`docs/deterministic_calibration.md` (0.4196 sobre 200 casos). Si se mide el
determinista con la convencion de pares canonicos (0.4536 en telefonia), el
delta consistente es +0.0247. Ambos deltas son positivos; la diferencia es de
convencion, no de senal.

Referencia global (200 casos, mismo cache oficial): exactitud estricta 0.7350,
F1 macro 0.5207, F1 micro 0.6654, subset accuracy 0.4300; determinista solo
(F1 macro, `None = error`) 0.4196; delta global +0.1011. Estos valores coinciden
con `evaluation/report.md`.
