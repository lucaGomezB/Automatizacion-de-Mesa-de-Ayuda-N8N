# Proposal: c-62-hardening-infra-red

## Why

El gap assessment (ISO 27002 8.20, 8.22, 8.2, 8.31, 5.14) identifico el stack local con servicios de infraestructura expuestos y sin segmentacion: Redis sin contrasena publicado en `6379`, PostgreSQL en `5433`, N8N accesible directo en `5678`, una unica red Docker `mesa_local_default` y un solo compose sin separacion de entornos. Es un quick win de bajo esfuerzo y alto impacto priorizado en el plan de cumplimiento (fila C-62, prioridad 2). El trabajo se declara "alineado con" los controles ISO/NIST; NO implica certificacion.

## What Changes

- **BREAKING**: quitar la publicacion al host de `5433` (PostgreSQL), `6379` (Redis) y `5678` (N8N); revisar los puertos del perfil corpus (`5434`, `8001`, `5679`).
- **BREAKING**: los comandos documentados que dependen de esas publicaciones deben seguir funcionando o tener un equivalente documentado: tests de integracion (`TEST_PG_URL=localhost:5433`), UI y webhooks de N8N (`localhost:5678`), harness `scripts/dry_run`.
- Contrasena en Redis — o retiro del servicio si se confirma que no es consumido.
- Segmentacion de la red Docker por dominios (edge, datos, automatizacion), de modo que N8N no comparta segmento con la base de datos.
- Restriccion del acceso a la UI de N8N (loopback y/o proxy nginx con autenticacion).
- Endurecimiento de nginx (ocultar version, headers de seguridad adicionales, limites de tasa).
- Separacion pragmatica y reversible de entornos dev/test/prod.

## Capabilities

### New Capabilities
- `infra-network-hardening`: exposicion de puertos al host, autenticacion de Redis, segmentacion de red Docker, acceso a la UI de N8N, endurecimiento de nginx y separacion de entornos.

### Modified Capabilities
- `foundation-environment`: el escenario que exige que "los puertos y dependencias del servicio N8N no se alteran" deja de ser valido (la exposicion de red de N8N cambia por este change).

## Impact

Archivos: `docker-compose.yml`, (nuevo) override o perfil de desarrollo, `nginx/nginx.conf`, `.env.example` (raiz), `scripts/up.sh`, `scripts/up.ps1`, `scripts/dry_run/dry_run.py`, `App/Backend/tests/conftest.py`, `scripts/corpus_ingest/test_corpus_compose_isolation.py`, y docs (`docs/operational-guide.md`, `README.md`, `AGENTS.md`). CI: `.github/workflows/ci.yml` NO usa el compose (service container propio en `localhost:5432`), pero el preflight de costo (`.github/workflows/ci.yml:104-108`) SI parsea el compose real; se deben preservar imagen pineada de n8n, `N8N_WEBHOOK_URL` y `EXECUTIONS_TIMEOUT`.

## Governance: ALTO

Cambio de infraestructura que altera el acceso a servicios. El agente NO decide: las Open Questions de `design.md` (OQ-1..OQ-8) deben resolverse antes de `apply`.

## Risks

| Riesgo | Prob. | Mitigacion |
|--------|-------|------------|
| Romper comandos de desarrollo documentados | Alta | Estrategia dev explicita y reversible; verificar cada comando antes de cerrar |
| Romper el preflight de CI que parsea el compose | Media | Preservar claves asertadas; correr `python scripts/preflight/cost_readiness.py` |
| Aislar N8N sin egreso a internet (IMAP/SMTP/Gemini/Twilio) | Media | La red de automatizacion NO es `internal: true` |
| Agenda de red mal asignada y servicios sin alcanzarse | Media | `docker compose config` + arranque y healthchecks en cada fase |

## Rollback Plan

Solo configuracion. Revertir los commits de `docker-compose.yml`, `nginx/nginx.conf`, `.env.example` y scripts; `docker compose up -d` restaura el estado previo (los volumenes persisten). No hay migracion de datos ni cambio de codigo de aplicacion.

## Dependencies

Ninguna. Resolucion previa de OQ-1..OQ-8 (autor) antes de implementar.

## Success Criteria

- [ ] Los servicios internos (PostgreSQL, Redis) no son alcanzables desde la LAN por defecto en el estado versionado.
- [ ] Redis requiere autenticacion o fue retirado con justificacion documentada.
- [ ] N8N no comparte red Docker con PostgreSQL; la segmentacion esta declarada y verificada con `docker compose config`.
- [ ] La UI de N8N no queda accesible sin autenticacion en `0.0.0.0`.
- [ ] nginx oculta su version y aplica los headers y limites acordados.
- [ ] Los comandos de desarrollo documentados siguen funcionando (o su equivalente esta documentado).
- [ ] `openspec validate c-62-hardening-infra-red --strict` pasa y `scripts/preflight/cost_readiness.py` sigue en verde.
