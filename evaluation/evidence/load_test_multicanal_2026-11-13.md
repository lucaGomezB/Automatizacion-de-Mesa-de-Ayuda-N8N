# Test de carga multicanal

- Commit: a82a111
- Fecha UTC: 2026-11-14T02:37:31Z
- Version de N8N: 2.11.2
- Perfil: corpus (postgres-corpus, backend-corpus, n8n-corpus) con override de costo cero
- SHA-256 del fixture: 1f5c06caf6c48ae98e95fe52272b41dcdfe28ff815e632736e0ffb3e8cdf0aab
- Veredicto: **no sostenida**

## Exclusiones declaradas

- correo: sondeo IMAP por minuto, no apto para inyeccion concurrente; la convergencia en POST /api/v1/incidentes/ es agnostica al canal
- telefonia: canal pago (Twilio); no se invoca ni se mide

## Capa backend (veredicto: sostenida)

| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Tasa de error |
|---|---|---|---|---|---|
| 1 | 44.5 | 62.2 | 84.6 | 20.79 | 0.0000 |
| 5 | 186.9 | 290.6 | 324.5 | 25.19 | 0.0000 |
| 10 | 349.5 | 457.4 | 588.3 | 26.84 | 0.0000 |
| 20 | 594.8 | 1215.8 | 1293.8 | 24.21 | 0.0000 |

## Capa n8n (veredicto: no sostenida)

| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Tasa de error |
|---|---|---|---|---|---|
| 1 | 307.4 | 338.4 | 368.2 | 3.21 | 0.0000 |
| 5 | 1339.6 | 1804.2 | 2157.3 | 3.75 | 0.0000 |
| 10 | 2565.4 | 3526.5 | 4065.0 | 3.82 | 0.0000 |
| 20 | 4732.6 | 6788.4 | 7469.2 | 3.78 | 0.0000 |

Violacion: nivel 20, condicion p95_techo.
