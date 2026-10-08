# Design: c-62-hardening-infra-red

## Context

Ver `proposal.md` para la motivacion y `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` para la evidencia de las brechas (8.20, 8.22, 8.2, 8.31, 5.14).

Estado actual relevante, verificado sobre el repositorio:

- `docker-compose.yml` (proyecto fijo `mesa_local`) publica al host: `5433:5432` (postgres), `6379:6379` (redis), `5678:5678` (n8n), `80/443` (nginx). El backend (8000) y el frontend (3000) ya NO se publican. Una unica red implicita `mesa_local_default`.
- Perfil `corpus` (aislado) publica `5434:5432`, `8001:8000`, `5679:5678`.
- `redis` no tiene volumen ni contrasena. N8N y `n8n-corpus` reciben `QUEUE_BULL_REDIS_HOST=redis` / `QUEUE_BULL_REDIS_PORT=6379`, pero NO hay `EXECUTIONS_MODE=queue`; `n8n/workflow.json` no referencia Redis y el nodo `memoryRedisChat` fue retirado por c-72. El backend no importa ni usa Redis. Indicio fuerte: Redis no tiene consumidor real hoy.
- `nginx/nginx.conf` termina TLS, redirige HTTP->HTTPS, aplica HSTS / `X-Content-Type-Options` / `X-Frame-Options` y un catch-all `return 444`. No oculta la version, no limita tasa, no aplica `Referrer-Policy` / `Permissions-Policy` / CSP.
- Consumidores de puertos publicados: `App/Backend/tests/conftest.py:85` (default `localhost:5433`), `App/Backend/tests/test_disposable_test_db.py` (5433), `scripts/dry_run/dry_run.py` (`--n8n-port 5678`, "port 5678 is published"), `scripts/up.sh:388` (imprime `http://localhost:5678`), `docs/operational-guide.md` y `README.md`. `scripts/corpus_ingest/test_corpus_compose_isolation.py` afirma los literales `5434:5432`, `8001:8000`, `5679:5678`.
- CI: `.github/workflows/ci.yml` corre el subconjunto de integracion contra su propio service container (`localhost:5432`), NO contra el compose. Pero el job backend SI ejecuta `scripts/preflight/cost_readiness.py`, que parsea el `docker-compose.yml` real y exige imagen de n8n pineada, `N8N_WEBHOOK_URL` con la ruta dedicada y `EXECUTIONS_TIMEOUT`. Esos tres contratos MUST preservarse.
- `App/Backend/app/config/settings.py:50` tiene un flag `environment` (default `"production"`) que hoy no cambia el despliegue.

## Goals / Non-Goals

**Goals:**

- Reducir la superficie de exposicion del host (datos y administracion) sin romper los flujos de desarrollo documentados.
- Segmentar la red Docker para que N8N no comparta segmento con PostgreSQL.
- Establecer una postura de Redis explicita (autenticado o retirado).
- Endurecer nginx y restringir la UI de N8N.
- Separar entornos de forma declarativa y reversible.
- Mantener CI verde y el cambio revertible.

**Non-Goals:**

- Despliegue productivo real (no existe; no se crea infraestructura de hosting).
- TLS interno / mTLS entre contenedores (queda fuera; ver 8.21).
- Gestion de secretos con KMS/Vault (es C-63).
- Reemplazar `N8N_BASIC_AUTH` por un IdP.
- Modificar codigo de aplicacion.

## Decisions

Cada decision presenta opciones; la eleccion final es del autor (governance ALTO) y se rastrea en la Open Question indicada. La recomendacion es una propuesta sujeta a aprobacion.

### D1 — Estrategia de publicacion de puertos (OQ-1)

- **A. Binding a loopback**: cambiar `"5433:5432"` a `"127.0.0.1:5433:5432"`, `"6379:6379"` a `"127.0.0.1:6379:6379"` y `"5678:5678"` a `"127.0.0.1:5678:5678"`.
  - Pros: minimo cambio, reversible, preserva todos los comandos documentados (`localhost:5433`, `localhost:5678`) y el dry-run. Mitiga la exposicion LAN.
  - Contras: el puerto sigue abierto en la interfaz de loopback (no elimina la publicacion); no aborda del todo 8.20.
- **B. Retirar la publicacion + override de desarrollo opt-in**: quitar `ports` de postgres/redis/n8n en el compose versionado y ofrecer `docker-compose.dev.yml` que los re-expone, usado con `-f` o via perfil.
  - Pros: postura endurecida real por defecto; alineacion plena con 8.20.
  - Contras: rompe el `docker compose up -d postgres` del flujo de tests y el dry-run si no se usa el override; exige actualizar `conftest.py`, `dry_run.py`, `up.sh`, docs y el test de aislamiento del corpus.
- **C. Perfiles con servicios duplicados**: mantener servicios endurecidos sin `ports` y agregar copias con `profiles: ["dev"]`.
  - Pros: opt-in explicito.
  - Contras: duplica servicios y complica `depends_on`; mayor mantenimiento.
- **Recomendacion (sujeta a OQ-1)**: A como linea base inmediata y B como objetivo si el autor acepta actualizar los comandos documentados. C se descarta por complejidad.

### D2 — Redis (OQ-2)

- **A. Retirar Redis** del stack base y del corpus, quitando `QUEUE_BULL_REDIS_*` y `depends_on`.
  - Pros: elimina una superficie sin consumidor real; menos configuracion.
  - Contras: si en el futuro se habilita `EXECUTIONS_MODE=queue`, hay que reintroducirlo.
- **B. Conservar Redis con `requirepass`** y propagar la credencial por variable de entorno a n8n (y backend si aplica).
  - Pros: conserva la capacidad de cola de N8N.
  - Contras: mantiene un servicio aparentemente no usado; hay que rotar la credencial.
- **Recomendacion (sujeta a OQ-2)**: confirmar consumidores; si se confirma que nadie lo usa, A. Si se conserva, B con la credencial en el `.env` gitignorado y `${VAR:-default}` no adivinable. La verificacion de consumidores es un prerequisito (tarea 3.1).

### D3 — Topologia de red (OQ-3, OQ-7)

Implementacion vigente (verificada en el apply):

| Red | Servicios | Propiedad |
|-----|-----------|-----------|
| `edge` | nginx, frontend, backend, ngrok (y backend-corpus para su tunel) | publica |
| `data` | postgres, backend (y postgres-corpus, backend-corpus) | `internal: true` |
| `automation` | n8n, backend (y n8n-corpus) | con egreso |
| `host_access` | postgres, postgres-corpus | no-`internal`, solo para publicar en loopback |

Invariantes verificadas: `n8n` y `postgres` no comparten red; nginx/frontend no estan en `data`; `automation` NO es `internal` porque n8n necesita salir a IMAP/SMTP/Gemini/Twilio.

- **Red de soporte `host_access` (hallazgo del apply)**: Docker no puede publicar puertos de un contenedor que SOLO esta en una red `internal: true`; por eso los servicios de datos unen ademas `host_access` (no-`internal`, sin n8n/nginx/frontend). Preserva la invariante de segmentacion y habilita el loopback de OQ-1=A. `INFRA-004` lo permite ("al menos tres redes" + red de soporte opcional).
- **Redis**: retirado (OQ-2=A), no aplica en la tabla.
- **Alternativa descartada**: dos redes (`edge`, `data`) poniendo n8n en `data` — incumple que N8N no comparta segmento con la base.
- **Recomendacion aplicada (OQ-3/OQ-7)**: redes reutilizadas por el perfil corpus.

### D4 — Acceso a la UI de N8N (OQ-4)

- **A. Binding a loopback**: `127.0.0.1:5678:5678`. La UI y los webhooks locales quedan accesibles solo desde la maquina.
- **B. Exposicion via nginx tras autenticacion**: proxy de la UI en un `location` dedicado. N8N no soporta path-prefix de forma confiable (limitacion ya documentada en el design archivado de c-20) y requeriria subdominio/DNS.
- **C. Solo override de desarrollo**: sin UI accesible por defecto; se habilita con el mecanismo de D5.
- **Recomendacion (sujeta a OQ-4)**: A como base; B solo si el autor acepta el trabajo de subdominio/path. C es compatible con D1-B.

### D5 — Separacion de entornos (OQ-5)

- **A. Perfiles de Compose** (`dev`): el estado por defecto es endurecido; `--profile dev` re-expone.
- **B. Archivos override** (`docker-compose.override.yml` gitignorado o `docker-compose.dev.yml` con `-f`).
- **C. Archivos por entorno** (`docker-compose.dev.yml`, `docker-compose.test.yml`, `docker-compose.prod.yml`).
- **Recomendacion (sujeta a OQ-5)**: A o B por ser reversibles y de bajo costo; el "prod" real no existe, por lo que C se considera prematuro. Cualquiera sea la via, el modo por defecto MUST ser el endurecido.

### D6 — Endurecimiento de nginx (OQ-6)

- `server_tokens off;` para ocultar la version.
- Headers adicionales: `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` restrictiva, y `Content-Security-Policy` sujeta a que no rompa la SPA (evaluar).
- `limit_req_zone` + `limit_req` sobre endpoints publicos sensibles (por ejemplo login y webhooks), con umbral a acordar.
- Conservar catch-all `444`, redireccion HTTP->HTTPS y los headers actuales.
- **Recomendacion (sujeta a OQ-6)**: aplicar `server_tokens`, `Referrer-Policy` y `Permissions-Policy` sin discusion; CSP y rate-limit con valores a confirmar.

## Risks / Trade-offs

- [Romper comandos de desarrollo documentados] -> Verificar cada comando listado en Contexto antes de cerrar; tarea 7 de verificacion.
- [Romper el preflight de CI que parsea el compose] -> Preservar imagen pineada de n8n, `N8N_WEBHOOK_URL` y `EXECUTIONS_TIMEOUT`; correr el preflight en cada fase.
- [Aislar N8N sin egreso] -> `automation` no es `internal: true`.
- [Romper `scripts/corpus_ingest/test_corpus_compose_isolation.py`] -> Si cambian los puertos del corpus, actualizar el test en el mismo change.
- [CSP que rompa la SPA] -> Dejar CSP fuera del alcance inicial o validarla contra la app.

## Migration Plan

1. Resolver OQ-1..OQ-8 con el autor.
2. Aplicar puertos (D1) y verificar comandos documentados.
3. Redis (D2) y segmentacion (D3).
4. nginx + UI de N8N (D4, D6).
5. Separacion de entornos (D5) y docs.
6. Verificacion de arranque, tests y preflight; luego archivar.

Rollback: solo configuracion; revertir los commits y `docker compose up -d`. Los volumenes persisten; no hay migracion de datos.

## Open Questions — RESUELTAS (autor, 2026-10-08)

- **OQ-1 (Puertos) = A (binding a loopback).** Publicar `127.0.0.1:5433`, `127.0.0.1:5678` (y `127.0.0.1:6379` si Redis se conservara; no aplica, ver OQ-2). NO se retira la publicacion: se acota a loopback. Los comandos documentados (`localhost:*`) siguen vigentes; OQ-8 sin cambios.
- **OQ-2 (Redis) = A (retirar).** Redis no tiene consumidor real (sin `EXECUTIONS_MODE=queue`; el workflow no lo referencia; el backend no lo importa). Se retira el servicio `redis`, sus `depends_on` y las variables `QUEUE_BULL_REDIS_*`. La tarea 3.3 (REDIS_PASSWORD) queda N/A.
- **OQ-3 (Segmentacion) = SI.** Tres redes `edge` / `data` (`internal: true`) / `automation`; invariante "n8n nunca comparte red con postgres".
- **OQ-4 (UI de N8N) = A (loopback).** `127.0.0.1:5678`.
- **OQ-5 (Entornos) = B (override explicito).** Archivo `docker-compose.dev.yml` usado con `-f`; el estado por defecto queda endurecido. Con OQ-1=A este override es una postura delgada (variables de desarrollo, p.ej. `ENVIRONMENT=development`) y NO un re-expositor de puertos.
- **OQ-6 (nginx) = SI.** `server_tokens off`, `Referrer-Policy`, `Permissions-Policy` y `limit_req` sobre login/webhooks con umbral conservador. **CSP se difiere** (validar contra la SPA por separado).
- **OQ-7 (Corpus) = SI.** Mismo tratamiento loopback para `5434`/`8001`/`5679`; actualizar `scripts/corpus_ingest/test_corpus_compose_isolation.py` si cambian los literales.
- **OQ-8 (Comandos documentados) = OK.** Con OQ-1=A no cambian `TEST_PG_URL` ni `localhost:5678`; solo se documenta el binding a loopback.

Consecuencia para las tareas: 2.3 (mecanismo opt-in de puertos) es N/A (no se retira la publicacion); 3.3 (REDIS_PASSWORD) es N/A (Redis se retira). La 6 implementa el override de OQ-5=B para la separacion de entornos.
