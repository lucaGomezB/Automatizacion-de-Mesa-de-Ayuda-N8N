# c-72 — Unificacion de la clasificacion telefonica: decisiones y nota de evaluacion

Change: `c-72-unificar-clasificacion-telefonica`.
Este documento registra las decisiones resueltas por el autor y la nota de
evaluacion del beneficio determinista-primero para el canal telefonico.

> Estado de los numeros: PROVISIONAL. El corpus de evaluacion de telefonia no
> esta completo, por lo que los valores numericos de esta nota no tienen peso
> de decision hasta que el corpus se cargue. Los numeros se documentan para
> trazabilidad, no como resultado final de tesis.

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

### 4.2. Medicion offline (tarea 5.1) — PROVISIONAL

Medicion OFFLINE sobre los casos telefonicos del corpus (canal
`llamada telefónica`), sin invocar Gemini y sin tocar
`evaluation/corpus.py::_a_float`:

| Metrica | Valor (provisional) |
|---------|---------------------|
| Casos telefonicos medidos | 81 |
| Umbral determinista vigente | 1.0 |
| Cortocircuitados | 0 |
| Tasa de cortocircuito | 0.0000 |
| Exactitud estricta del subconjunto cortocircuitado | N/A (0/0) |
| Cobertura del vocabulario (telefonia) | 0.7407 (21 sin match) |
| Exactitud estricta del determinista (telefonia) | 0.4444 |
| F1 macro estricto del determinista (telefonia) | 0.3810 |

Interpretacion provisional: con el umbral calibrado de c-71 en 1.0 el
cortocircuito telefonico es 0.0, de modo que el beneficio de costo de c-72 NO
se materializa todavia. Es una consecuencia directa de la calibracion de c-71
("preferir precision sobre cobertura") y queda como hallazgo para que el autor
decida si baja el piso de precision o enriquece el vocabulario. La calibracion
global de c-71 (200 casos) esta en `docs/deterministic_calibration.md`.

Estos valores son PROVISIONALES: el corpus de telefonia no esta completo y el
autor decidio que los numeros no pesan en la decision hasta que el corpus se
cargue.

### 4.3. Medicion hibrida (tarea 5.2) — PENDIENTE

La re-corrida de `evaluation/run_evaluation.py` sobre telefonia (delta de F1
hibrido vs determinista) queda **PENDIENTE**. Motivos:

- Cuota de Gemini no verificada y corrida paga sujeta a confirmacion explicita
  (`--confirm-paid`); no se invoca al modelo solo para forzar la medicion.
- El corpus de telefonia es provisional; una corrida paga sobre datos
  incompletos no aportaria un numero con peso de decision.

No se fabrican numeros. Cuando haya cuota y el corpus este completo, la medicion
se registra en esta nota reemplazando el estado PENDIENTE.
