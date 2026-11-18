# Test de carga multicanal CON inferencia paga (TASK B)

- Commit: d0592d3
- Fecha UTC: 2026-11-18T20:04:46Z
- Version de N8N: 2.11.2
- Perfil: corpus (postgres-corpus, backend-corpus, n8n-corpus) con override de corrida paga acotada
- Corrida: 6ad5e32d
- SHA-256 de la fixture: 88cab8788273ed9df21dad03b1a653c855e31c2fd3294ee94869098f1935e163
- Tolerancia de inferencia (T): 4.0
- Tope de presupuesto (USD): 1.25
- Veredicto: **no sostenida**

## Exclusiones declaradas

- correo: sondeo IMAP por minuto, no apto para inyeccion concurrente; la convergencia en POST /api/v1/incidentes/ es agnostica al canal
- telefonia: canal pago (Twilio); no se invoca ni se mide

## Uso de tokens y costo declarado

- Modelo solicitado: gemini-3.6-flash
- Version del modelo (API): gemini-3.6-flash
- Eventos de clasificacion: 360 (con uso: 360)
- Tokens de entrada: 274920
- Tokens de salida: 6648
- Tokens totales: 281568
- Origen de tokens: api
- Costo estimado (USD): 0.23112
- Escenario de precio: introductorio
- Fuente del precio: precios de lista declarados por la tesis (seccion 8, consultados 2026-10-19); fuente unica evaluation/brazo_gemini_solo.py:PRECIOS_USD_POR_MILLON
- Origen del gasto: tokens_calculado

## Capa backend (veredicto: no sostenida)

| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Error | Escalados | p95 escalado (ms) | p95 deterministico (ms) | Razon |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1007.6 | 2089.3 | 2330.6 | 0.93 | 0.0000 | 90/180 | 2177.2 | 431.0 | 5.1 |
| 5 | 1221.9 | 2708.4 | 3968.1 | 3.50 | 0.0000 | 90/180 | 3092.1 | 827.8 | 3.7 |

| Concurrencia | Eventos | Con uso | Tokens entrada | Tokens salida | Tokens total | Origen |
|---|---|---|---|---|---|---|
| 1 | 90 | 90 | 68730 | 1648 | 70378 | api |
| 5 | 90 | 90 | 68730 | 1648 | 70378 | api |

Violacion: nivel 1, condicion inferencia.

## Capa n8n (veredicto: no sostenida)

| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Error | Escalados | p95 escalado (ms) | p95 deterministico (ms) | Razon |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1757.9 | 2919.8 | 5033.4 | 0.56 | 0.0000 | 90/180 | 3390.0 | 1445.2 | 2.3 |
| 5 | 4307.7 | 7545.7 | 8684.4 | 1.07 | 0.0000 | 90/180 | 8531.9 | 5024.7 | 1.7 |

| Concurrencia | Eventos | Con uso | Tokens entrada | Tokens salida | Tokens total | Origen |
|---|---|---|---|---|---|---|
| 1 | 90 | 90 | 68730 | 1675 | 70405 | api |
| 5 | 90 | 90 | 68730 | 1677 | 70407 | api |

Violacion: nivel 5, condicion p95_techo.
