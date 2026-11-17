# Test de carga multicanal CON inferencia paga (TASK B)

- Commit: bbc5865
- Fecha UTC: 2026-11-17T22:51:41Z
- Version de N8N: 2.11.2
- Perfil: corpus (postgres-corpus, backend-corpus, n8n-corpus) con override de corrida paga acotada
- Corrida: 6d1917ed
- SHA-256 de la fixture: 88cab8788273ed9df21dad03b1a653c855e31c2fd3294ee94869098f1935e163
- Tolerancia de inferencia (T): 4.0
- Tope de presupuesto (USD): 1.0
- Veredicto: **no sostenida**

## Exclusiones declaradas

- correo: sondeo IMAP por minuto, no apto para inyeccion concurrente; la convergencia en POST /api/v1/incidentes/ es agnostica al canal
- telefonia: canal pago (Twilio); no se invoca ni se mide

## Capa backend (veredicto: no sostenida)

| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Error | Escalados | p95 escalado (ms) | p95 deterministico (ms) | Razon |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 815.9 | 1913.1 | 1937.4 | 1.12 | 0.0000 | 10/20 | 1929.1 | 171.1 | 11.3 |
| 5 | 946.3 | 1982.7 | 1999.4 | 4.41 | 0.0000 | 10/20 | 1993.7 | 395.6 | 5.0 |
| 10 | 1182.9 | 2759.6 | 2763.9 | 6.03 | 0.0000 | 10/20 | 2762.5 | 779.0 | 3.5 |
| 20 | 2185.3 | 3424.2 | 3445.8 | 5.76 | 0.0000 | 10/20 | 3438.4 | 1782.9 | 1.9 |

Violacion: nivel 1, condicion inferencia.

Violacion: nivel 5, condicion inferencia.

## Capa n8n (veredicto: no sostenida)

| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Error | Escalados | p95 escalado (ms) | p95 deterministico (ms) | Razon |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1314.6 | 2149.5 | 2163.2 | 0.75 | 0.0000 | 10/20 | 2158.5 | 622.4 | 3.5 |
| 5 | 2129.8 | 3660.4 | 3674.8 | 1.82 | 0.0000 | 10/20 | 3669.8 | 2087.9 | 1.8 |
| 10 | 4519.8 | 8352.7 | 8596.7 | 1.83 | 0.0000 | 10/20 | 8513.2 | 5376.9 | 1.6 |
| 20 | 8378.2 | 10183.6 | 10197.6 | 1.96 | 0.0000 | 10/20 | 10192.8 | 8382.9 | 1.2 |

Violacion: nivel 10, condicion p95_techo.

Violacion: nivel 20, condicion p95_techo.
