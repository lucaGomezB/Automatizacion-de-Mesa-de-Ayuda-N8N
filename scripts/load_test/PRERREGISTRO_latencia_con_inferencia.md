# Prerregistro — Latencia e2e CON inferencia paga (TASK B, seguimiento de c-218)

Estado: **fijado ANTES de observar cualquier dato** de la corrida paga. Ninguna
constante de este documento se reajusta despues de ver resultados. El veredicto se
emite contra estas reglas, no al reves.

## Objetivo y alcance

Medir la latencia end-to-end del tramo compartido donde convergen los canales
(`POST /api/v1/incidentes/` del backend y el webhook web de N8N) CUANDO una
fraccion preregistrada de solicitudes escala a Gemini 3.6 Flash, y cuantificar la
**contribucion de la inferencia** frente al camino deterministico ya medido en
`3.29` (c-218). Es la corrida paga que c-218 difirio (design D2, alternativa de
dueno; Open Question).

Declaracion de honestidad: es una **medicion en una sola maquina y un entorno
desechable**, con inferencia real. NO se extrapola a produccion. La finalidad es
contrastar la dimension de latencia del tramo compartido CON inferencia incluida.

## Diseño y costo acotado

- Niveles de concurrencia: `1, 5, 10, 20` (los mismos de c-218).
- Volumen acotado por nivel y capa: `20` solicitudes, `1` repeticion (c-218 uso
  40x3; aqui se reduce a proposito para acotar el gasto a centavos). Total:
  `4 niveles x 20 x 2 capas = 160` solicitudes.
- Fixture mixta (`fixture_descripciones_inferencia.json`): alterna 1:1 casos
  deterministas (cortocircuito) y casos ambiguos/sin senal (escalan a Gemini), de
  modo que la mezcla esperada es **50 % escalada**. La ambiguedad se verifico
  contra `DeterministicClassifier` (empate en el puntaje maximo o ausencia de
  senal): no se observo ningun dato de la corrida de carga para fijar la fixture.
- Entorno: perfil `corpus` (base descartable `mesa_de_ayuda_corpus`, backend en
  `8001`, N8N en `5679`) con el override `compose.load-test-inference.yml`, que
  hereda la `GEMINI_API_KEY` real de `App/Backend/.env` y fija un presupuesto
  POSITIVO acotado. El camino por defecto de costo cero NO se modifica.
- Tope de gasto autorizado: **USD 1.00** (`--tope-usd`). La guarda paga aborta si
  el presupuesto efectivo del contenedor supera el tope. Tasa de la guarda: 200
  llamadas/hora por superficie (suficiente para 160 solicitudes con 50 % de
  escaladas).
- Costo estimado: <= `80` llamadas por capa x `2` capas = `160` llamadas como
  maximo teorico; con ~USD 0,0005-0,002 por llamada, del orden de **USD 0,08 a
  0,32**. Muy por debajo del tope.

## Metricas

Iguales a c-218, por nivel y capa, MAS la contribucion de la inferencia:

- Latencia de CLIENTE (envio -> respuesta): p50, p95, p99, media.
- `latencia_e2e_ms` del servidor (p50, p95) donde el canal la instrumenta (N8N).
- Throughput (req/s) y tasa de error (no 2xx + timeouts, sin descartes).
- **Contribucion de la inferencia (comparacion pareada en el mismo nivel):**
  p50/p95 de la latencia de CLIENTE del subconjunto ESCALADO vs el subconjunto
  DETERMINISTA, y la razon `r = p95(escalado) / p95(deterministico)`.
- Conteo por etapa observada (`deterministic` / `gemini` / `fallback`) y fraccion
  escalada real por nivel.

## Criterio de decision (fijado antes de ver datos)

Por capa, tres vias (identicas en forma a c-218, con una condicion adicional):

1. **Techo absoluto:** `p95 <= 5000 ms` (cliente, inclusivo) en todos los niveles.
2. **Tolerancia de throughput:** no decrece mas del `10 %` respecto del nivel
   anterior (inclusivo).
3. **Tasa de error:** `0` en todos los niveles.
4. **Degradacion por inferencia (condicion adicional de la corrida paga):**
   `r = p95(escalado) / p95(deterministico) <= T = 4` en cada nivel con datos en
   ambos subconjuntos. Cuantifica cuanto encarece la latencia la inferencia.

- **sostenida:** se cumplen (1)-(3) y la condicion (4) en todos los niveles.
- **no sostenida:** algun nivel viola (1)-(4); el reporte nombra nivel y condicion.
- **no concluyente:** corrida incompleta o niveles distintos de los preregistrados.

Veredicto global: el de la peor capa (`no sostenida > no concluyente > sostenida`).

Razon de `T = 4`: el camino deterministico ronda decenas/cientos de ms; la
inferencia de un LLM Flash ronda segundos. `T = 4` es un umbral deliberadamente
EXIGENTE: si la inferencia domina, la condicion se viola y el sistema se declara
**no sostenido** con inferencia incluida. Se prefiere un umbral duro (honesto)
sobre uno laxo que oculte la contribucion.

## Procedencia de la evidencia

`evaluation/evidence/load_test_inferencia_<YYYY-MM-DD>.json` (y su `.md`),
producidos por `scripts/load_test/load_test_inference.py --confirm-paid`. Incluye
`commit`, `fecha_utc`, version de N8N, `perfil`, `corrida_id`, SHA-256 de la
fixture, constantes del criterio, el bloque `prerregistro` (T, tope, mezcla) y las
metricas por nivel de las dos capas. Sin secretos (la clave real nunca se escribe).
