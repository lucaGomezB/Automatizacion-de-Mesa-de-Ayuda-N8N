# Prerregistro — Latencia e2e CON inferencia paga, corrida AMPLIADA (c-243, G2/G3)

Estado: **fijado ANTES de observar cualquier dato** de la corrida ampliada. Ninguna
constante de este documento se reajusta despues de ver resultados. El veredicto se
emite contra estas reglas, no al reves.

Este documento es una **enmienda acotada** al prerregistro original
(`PRERREGISTRO_latencia_con_inferencia.md`, TASK B). Conserva el objetivo, la
fixture, el entorno y el criterio; solo agranda la muestra para responder la
compuerta **G2** (suficiencia de una corrida con n = 10 por subconjunto) y leer la
instantanea del modelo y el gasto por tokens para **G3**.

## Objetivo y alcance

Medir de nuevo la latencia end-to-end del tramo compartido con inferencia real
incluida (`POST /api/v1/incidentes/` del backend y el webhook web de N8N) con una
muestra mayor, y capturar el uso de tokens y la version del modelo devuelta por la
API. La corrida ampliada **afina la precision** de la sonda; **no busca cambiar el
veredicto** de la corrida original, ni convertirse en un resultado de capacidad.

Declaracion de honestidad: es una **medicion en una sola maquina y un entorno
desechable**, con inferencia real. NO se extrapola a produccion.

## Que cambia respecto del prerregistro original

- Niveles de concurrencia: **solo `1 y 5`** (los dos niveles donde la corrida
  original violo la condicion relativa de inferencia). Los niveles 10 y 20 quedan
  fuera para acotar el gasto.
- Volumen por nivel y capa: **60 solicitudes**, **3 repeticiones** (contra 20 x 1).
- Total: `2 niveles x 60 x 3 repeticiones x 2 capas = 720` solicitudes.
- Escaladas esperadas: mezcla 50 % => `n = 360` llamadas escaladas; `n = 90` por
  subconjunto escalado y por nivel-capa (60 x 3 / 2).
- Tope de gasto autorizado: **USD 1.25** (`--tope-usd 1.25`).
- Captura de uso: el arnes lee los eventos `gemini_classified` de los logs del
  backend (JSON de structlog) y agrega `modelo_solicitado`, `model_version`,
  tokens de entrada/salida/total, `tokens_origen`, `costo_usd`, `precio_fuente` y
  `gasto_origen`.

## Diseno y costo acotado

- Fixture mixta: `fixture_descripciones_inferencia.json` (misma que la corrida
  original; alterna 1:1 casos deterministicos y ambiguos). Mezcla esperada 50 %.
- Entorno: perfil `corpus` (base descartable `mesa_de_ayuda_corpus`, backend en
  `8001`, N8N en `5679`) con el override `compose.load-test-inference.yml`. El
  override eleva la tasa de la guarda de costo a **600 llamadas/hora** por
  superficie (la original fijaba 200, insuficiente para ~360 escaladas). El camino
  por defecto de costo cero NO se modifica.
- La clave real se hereda de `App/Backend/.env`; nunca se escribe en la evidencia.
- Costo estimado: `360` llamadas escaladas; con los precios declarados por la tesis
  (entrada USD 0,75 / salida USD 3,75 por millon de tokens, escenario
  `introductorio`) y del orden de `800-1000` tokens de entrada y `15-30` de salida
  por llamada, del orden de **USD 0,25-0,45**, muy por debajo del tope de USD 1.25.
- El gasto de la evidencia se calcula **desde los tokens** (`gasto_origen:
  tokens_calculado`), con el precio declarado; NO es facturacion del proveedor.

## Metricas

Iguales al prerregistro original, por nivel y capa, MAS el uso de tokens y la
version del modelo:

- Latencia de CLIENTE (envio -> respuesta): p50, p95, p99, media.
- `latencia_e2e_ms` del servidor (p50, p95) donde el canal la instrumenta (N8N).
- Throughput (req/s) y tasa de error (no 2xx + timeouts, sin descartes).
- Contribucion de la inferencia (comparacion pareada en el mismo nivel):
  p50/p95 de la latencia de CLIENTE del subconjunto ESCALADO vs el DETERMINISTA, y
  la razon `r = p95(escalado) / p95(deterministico)`.
- Uso de tokens por nivel y total (entrada, salida, total) y version del modelo
  devuelta por la API.

## Criterio de decision (fijado antes de ver datos)

Por capa, tres vias (identicas en forma al prerregistro original, con la condicion
adicional de degradacion por inferencia):

1. **Techo absoluto:** `p95 <= 5000 ms` (cliente, inclusivo) en todos los niveles.
2. **Tolerancia de throughput:** no decrece mas del `10 %` respecto del nivel
   anterior (inclusivo).
3. **Tasa de error:** `0` en todos los niveles.
4. **Degradacion por inferencia:** `r = p95(escalado) / p95(deterministico) <= T = 4`
   en cada nivel con datos en ambos subconjuntos.

- **sostenida:** se cumplen (1)-(3) y la condicion (4) en todos los niveles.
- **no sostenida:** algun nivel viola (1)-(4); el reporte nombra nivel y condicion.
- **no concluyente:** corrida incompleta o niveles distintos de los preregistrados.

Veredicto global: el de la peor capa (`no sostenida > no concluyente > sostenida`).

Con solo los niveles `1 y 5`, el veredicto del backend depende de la condicion (4)
en esos dos niveles. La corrida **afina la precision** de la estimacion de la razon
`r` (mas repeticiones y mas solicitudes por subconjunto) y **no esta destinada a
invertir** el veredicto de la corrida original.

## Procedencia de la evidencia

`evaluation/evidence/load_test_inferencia_ampliada_<YYYY-MM-DD>.json` (y su `.md`),
producidos por `scripts/load_test/load_test_inference.py --confirm-paid
--tope-usd 1.25`. Incluye `commit`, `fecha_utc`, version de N8N, `perfil`,
`corrida_id`, SHA-256 de la fixture, constantes del criterio, el bloque
`prerregistro` (T, tope, mezcla) y el bloque `inferencia` (uso de tokens, version
del modelo, costo declarado y procedencia del gasto), ademas de las metricas por
nivel de las dos capas. Sin secretos (la clave real nunca se escribe).
