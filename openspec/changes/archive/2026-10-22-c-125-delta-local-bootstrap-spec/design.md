## Context

Ver `proposal.md` - Why. El spec vivo `openspec/specs/local-bootstrap/spec.md` describe 7 requisitos; solo 2 divergen del codigo mergeado en `main` (commit `5de674d`, PR #36). Este change es DOC-ONLY: no modifica `scripts/up.sh`, `scripts/up.ps1` ni ningun otro archivo de codigo. El codigo ya es el estado final; el delta solo alinea la especificacion.

## Goals / Non-Goals

**Goals:**
- Expresar como delta los dos requisitos que cambiaron respecto del codigo mergeado.
- Dejar constancia explicita de que los otros cinco requisitos fueron auditados y siguen exactos.

**Non-Goals:**
- No introducir requisitos nuevos (ADDED). No se speculativamente documenta comportamiento no representado hoy (ver Open Questions).
- No tocar codigo, compose, Makefile ni tests.

## Decisions

**Decision 1: MODIFIED (no ADDED) para ambos requisitos.**
El comportamiento externo de los comandos sigue existiendo; cambio su contenido (conjunto de secretos; texto del recordatorio). Corresponde `## MODIFIED Requirements` con el bloque completo (requisito + escenarios) para que el archive no pierda detalle.
- Alternativa descartada: REMOVED + ADDED. Seria mas ruidoso y perderia la trazabilidad del requisito (mismo nombre, misma intencion).

**Decision 2: Se agrega un escenario especifico para `COST_GUARD_CALLER_HMAC_KEY`.** El spec ya tenia dos escenarios dedicados a `JWT_SECRET_KEY`; por simetria y para cubrir el caso nuevo de forma testeable, se agrega su equivalente para la cuarta variable. El escenario generico de "variable vacia o placeholder" se amplia a las cuatro.

**Decision 3: En el requisito de recordatorio, el texto se alinea 1:1 con la salida real de los scripts.** Se nombran IMAP, SMTP, login del operador y secreto del webhook de telefonia, y se explicita que Gemini vive en el `.env` del backend. No se conserva la lista vieja "Outlook, Twilio y Gemini".

**Decision 4: Los cinco requisitos restantes no se tocan.** Verificados contra los scripts; ver `## Risks / Trade-offs`.

| Requisito auditado | Estado |
|---|---|
| Generacion automatica de certificados TLS cuando faltan | Exacto: `ensure_certificates` / `Invoke-EnsureCertificates` |
| Arranque del stack y espera de salud acotada | Exacto: `docker compose up -d --build` sin `-p`; `wait_for_healthy` con timeout |
| Verificacion de salud y salida de acceso | Exacto: dos `curl -k`; URLs `https://localhost/` y `http://localhost:5678` |
| Equivalencia multiplataforma y alias opcional | Exacto: `up.sh` + `up.ps1` + `Makefile` con `up/down/ps/logs/health` |
| Credenciales de desarrollo local parametrizadas por entorno | Exacto: `${POSTGRES_PASSWORD:-mesa_local_dev}`; `create_db.sql` pide `-v db_password` |

## Risks / Trade-offs

- [Texto del recordatorio atado a la redaccion literal del script] -> El spec describe el CONTRATO (que credenciales hay que crear y que Gemini va en el backend), no la frase exacta; pequenos cambios de redaccion no invalidan el requisito.
- [Deriva futura silenciosa entre spec y script] -> Mitigado por los tests `scripts/tests/test_up_preflight.sh` y por incluir la re-verificacion como tarea del change.
- [Gap preexistente: los preflights de costo y Gemini (`check_cost_preflight`, `check_gemini_preflight`) existen en el codigo pero no estan representados en ningun requisito de esta capacidad] -> No es deriva de un requisito existente y queda FUERA del alcance de este delta. Ver Open Questions.

## Migration Plan

1. Aplicar el delta al spec vivo al archivar (`openspec archive`), o via `openspec sync` si se prefiere adelantar.
2. Verificar con `openspec validate local-bootstrap --strict` que el spec vivo sigue valido tras el sync.
3. Rollback: revertir el commit de sincronizacion del spec; no hay efecto sobre el codigo.

## Open Questions

- Los preflights de costo y Gemini merecen requisitos propios en `local-bootstrap` o en otra capacidad (`cost-readiness` / `n8n-workflow`)? Se difiere: no afecta a este delta ni al conjunto de requisitos que se modifica.
