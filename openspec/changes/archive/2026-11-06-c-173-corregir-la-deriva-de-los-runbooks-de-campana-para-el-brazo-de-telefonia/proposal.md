## Why

Los runbooks de la campana de medicion derivaron para el brazo de telefonia. Cinco defectos verificados impiden ejecutarlo de forma confiable:

1. Ningun documento bajo `docs/` menciona la herramienta softphone `scripts/voip_softphone/` ni su procedimiento (`grep -rln "voip_softphone\|mint_token" docs/` no devuelve nada). Los runbooks dicen "el operador del softphone hace las llamadas siguiendo el plan" sin identificar la herramienta ni el paso a paso.
2. Los ejemplos de ingesta de telefonia (`docs/campana-medicion/guia-ejecucion-campana.md:193-200` y `docs/campana-medicion/runbook-campana-contrabalanceada.md:161-171`) omiten `--insecure`, requerido contra el default `--base-url https://localhost` (certificado autofirmado de nginx; `scripts/corpus_ingest/README.md:391`).
3. El rate de la guarda de costo no figura como prerequisito. El stack base usa `COST_GUARD_RATE_LIMIT_CALLS=30` (global, 1h) y `COST_GUARD_CALLER_RATE_LIMIT_CALLS=3` (por origen, 1h) (`App/Backend/app/config/settings.py:192-194`). El brazo de telefonia tiene 81 llamadas (m1-t1=16, m1-t2=24, m2-t1=18, m2-t2=23): el rate global de 30/h denegaria la llamada numero 31. Solo el perfil aislado `corpus` relaja el rate a 200 (`docker-compose.yml:348-354`), y la campana NO corre en ese perfil.
4. La campana de telefonia corre sobre el stack principal (`mesa_de_ayuda_campana`), via nginx base + el dominio reservado `tameness-trilogy-unrefined.ngrok-free.dev` (`docker-compose.yml:274`), que debe coincidir con la Voice URL del TwiML App y con `BACKEND_PUBLIC_BASE_URL` (`App/Backend/.env:14`). El perfil aislado `corpus` de `docs/runbook-corpus-telefonia.md` es un mecanismo anterior (c-70) que la campana no usa; los runbooks no deben enviar alli al operador.
5. Faltan los prerequisitos de Twilio (TwiML App Voice URL = `BACKEND_PUBLIC_BASE_URL` = dominio ngrok reservado; origen de `TWILIO_TWIML_APP_SID`).

Corregir esto ANTES de correr el brazo de telefonia evita denegaciones por rate, corridas contra el stack equivocado y llamadas sin correlacion de caso.

## What Changes

- `docs/campana-medicion/guia-ejecucion-campana.md` (§1.5.2): agrega `--insecure` al ejemplo de `ingest_telefonia_corpus.py`; agrega una subseccion del brazo de telefonia con el procedimiento del softphone (`mint_token.py serve` + colocacion de la llamada en orden de `posicion` eligiendo el `corpus_case_id`, para las mitades de `O1`/`O2`) y sus prerequisitos (guarda de costo y Twilio); remite a `scripts/voip_softphone/README.md` como fuente de verdad.
- `docs/campana-medicion/runbook-campana-contrabalanceada.md` (§5.4 Telefonia): agrega `--insecure`, documenta el mismo procedimiento y prerequisitos, y remite al README del softphone.
- Cambio estrictamente documental: NO se modifica codigo, configuracion ni se ejecuta la campana.

## Capabilities

### New Capabilities

None. Cambio docs-only: no introduce comportamiento nuevo en el sistema.

### Modified Capabilities

None. El criterio no cambia a nivel spec. `evaluation-campaign-instrumentation` ECM-005 exige que el runbook contrabalanceado defina "con que flags se corren los harnesses", pero NO enumera los flags: agregar `--insecure` y el procedimiento de telefonia deja el requisito satisfecho sin modificarlo. Igual que `c-171` (misma naturaleza de deriva docs-only), el change marca `skip_specs: true`.

## Impact

- Archivos modificados: `docs/campana-medicion/guia-ejecucion-campana.md`, `docs/campana-medicion/runbook-campana-contrabalanceada.md`.
- NO se modifica: codigo bajo `App/`, `n8n/`, `scripts/`, `evaluation/`; ni `evaluation/data/campana/README.md` (ver design: la fila pendiente de SHA de la telefonia es correcta y el sidecar `m2-automatizado-t2` pertenece a otro cierre); ni `docs/campana-medicion/plan-campana-de-medicion.md`.
- Prerequisito operativo SOLO documentado (no ejecutado): subir `COST_GUARD_RATE_LIMIT_CALLS` (por ejemplo a 200) en `App/Backend/.env` y recrear el backend (`docker compose up -d backend`).
- Dependencias: `scripts/voip_softphone/` (herramienta entregada) y el runbook contrabalanceado de c-166.
