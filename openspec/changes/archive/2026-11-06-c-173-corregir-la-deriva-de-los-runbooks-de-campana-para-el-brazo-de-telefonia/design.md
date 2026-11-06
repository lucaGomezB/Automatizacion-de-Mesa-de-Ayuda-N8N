## Context

Ver `proposal.md` — Why. La campana se documenta en cuatro piezas con roles distintos; esta correccion toca solo las dos primeras:

- `docs/campana-medicion/guia-ejecucion-campana.md`: punto de entrada unico y orden de los pasos.
- `docs/campana-medicion/runbook-campana-contrabalanceada.md`: procedimiento de los sub-planes, de los harnesses y del brazo de telefonia (seccion 5.4).
- `docs/campana-medicion/plan-campana-de-medicion.md`: plan general, sin detalle de telefonia. NO se toca.
- `evaluation/data/campana/README.md`: fuente de verdad de los artefactos de la campana. NO se toca (ver D6).

Fuente de verdad del softphone: `scripts/voip_softphone/README.md` (prerequisitos, variables, arranque y colocacion de la llamada). Restricciones: cambio docs-only (gobernanza LOW), sin tocar codigo ni configuracion bajo `App/`, `n8n/`, `scripts/`, `evaluation/`; sin ejecutar la campana; cadenas canonicas exactas sin tildes.

## Goals / Non-Goals

**Goals:**

- Que el operador del brazo de telefonia encuentre, en los runbooks de la campana, el procedimiento completo: softphone sobre el stack principal, `mint_token.py serve` en `127.0.0.1:8765`, colocacion de la llamada en orden de `posicion` eligiendo el `corpus_case_id`, para su mitad (`O1`/`O2`).
- Que los ejemplos de ingesta de telefonia incluyan `--insecure` y que el documento declare que aplica a las 4 corridas por sub-plan.
- Que el rate de la guarda de costo quede documentado como prerequisito, con donde se sube y como se recarga el backend.
- Que los prerequisitos de Twilio (TwiML App Voice URL = `BACKEND_PUBLIC_BASE_URL` = dominio ngrok reservado; origen de `TWILIO_TWIML_APP_SID`) queden explicitos.
- Que haya una sola fuente de verdad del detalle del softphone: `scripts/voip_softphone/README.md`; los runbooks remiten, no duplican.

**Non-Goals:**

- No se modifica codigo, `docker-compose.yml`, `.env`, settings ni la guarda de costo.
- No se ejecuta el brazo de telefonia ni la campana.
- No se completa ningun SHA-256 pendiente ni se toca el sidecar `m2-automatizado-t2` (otro cierre).
- No se cambia ningun spec (ver D6); el change marca `skip_specs: true`.

## Decisions

- **D1 — Startck de la campana = stack principal, no el perfil `corpus`.** El brazo de telefonia corre sobre `mesa_de_ayuda_campana`, via nginx base + ngrok reservado, con la Voice URL del TwiML App apuntando al endpoint de voz del backend base. El perfil aislado `corpus` (`docs/runbook-corpus-telefonia.md`, c-70) es un mecanismo anterior y NO se usa en la campana; los runbooks no deben remitir a el. Alternativa descartada: reusar el perfil `corpus`, que corre contra una base descartable y no es la base de la campana.
- **D2 — Fuente de verdad unica del softphone.** El detalle (variables, setup de Twilio, arranque, colocacion de la llamada) vive en `scripts/voip_softphone/README.md`. La guia y el runbook ganan una referencia y solo repiten el minimo operativo (comando de arranque, URL de la pagina, criterio de orden y seleccion de caso). Alternativa descartada: copiar el README del softphone dentro de los runbooks, que duplicaria la fuente y volveria a generar deriva.
- **D3 — `--insecure` en todos los ejemplos de telefonia.** El default `--base-url https://localhost` es el certificado autofirmado de nginx; sin `--insecure` el harness no conecta. Se agrega al ejemplo versionado y se declara que aplica a las 4 corridas por sub-plan `automatizado`. Alternativa descartada: cambiar `--base-url` a un host con certificado valido, que no existe en la campana.
- **D4 — Prerequisito de la guarda de costo documentado, no aplicado.** Con 81 llamadas y un limite global de 30/h, la llamada 31 se deniega (`CAUSE_...`, guarda existente). La guia/runbook indican subir `COST_GUARD_RATE_LIMIT_CALLS` (por ejemplo a 200) en `App/Backend/.env` (el `env_file` del servicio `backend`, `docker-compose.yml:85`) y recrear el servicio (`docker compose up -d backend`) para que tome el valor. El rate por origen (3/h) no es obstaculo: `mint_token.py` acuna una identidad unica por sesion de servidor, de modo que la clave `caller` cambia y el 3/h no se agota; el global 30/h SIGUE aplicando. Alternativa descartada: usar el perfil `corpus` (rate 200) que la campana no usa.
- **D5 — Prerequisitos de Twilio explicitos.** Los numeros Twilio, la Voice URL del TwiML App y `BACKEND_PUBLIC_BASE_URL` deben ser el MISMO dominio ngrok reservado `tameness-trilogy-unrefined.ngrok-free.dev`. `TWILIO_ACCOUNT_SID` proviene de `App/Backend/.env`; `TWILIO_API_KEY_SID`, `TWILIO_API_KEY_SECRET` y `TWILIO_TWIML_APP_SID` de `scripts/voip_softphone/softphone.env` (gitignored). Se documenta, no se ejecuta.
- **D6 — `evaluation/data/campana/README.md` queda fuera de alcance.** La fila de SHA `sidecar_*_tel.json` esta correctamente `pendiente`: los sidecars de telefonia se producen al correr el brazo y aun no existen. El sidecar `m2-automatizado-t2` que esa fila agrupa ya fue producido, pero su SHA pertenece al cierre de m2-t2, no a esta correccion; tocarlo excederia el alcance. Residuo verificado: ningun spec cambia (ECM-005 no enumera flags); se replica la decision de `c-171` y se marca `skip_specs: true`.

## Risks / Trade-offs

- **[Riesgo] La guia y el runbook contrabalanceado se desincronizan al editar solo uno.** -> El procedimiento vive en el runbook (§5.4); la guia remite a el y repite solo el comando de arranque y el criterio de orden/seleccion. Verificacion transversal con `grep` de `--insecure` en ambos.
- **[Riesgo] Documentar un valor (`200`) que no es el default y que podria cambiar.** -> Se documenta como "por ejemplo 200" y se cita la fuente (`docker-compose.yml:348-354` y `settings.py:192-194`), de modo que un cambio de default se detecta por `grep`.
- **[Trade-off] Subir el rate global de 30 a 200 debilita temporalmente la guarda en el stack base.** -> Es un prerequisito de la corrida documentado, no un cambio de codigo; al recrear el backend sin el override, el default vuelve. El rate por origen sigue activo y el limite de bolsa (`COST_GUARD_BUDGET_USD`) no se toca.
- **[Trade-off] Mas detalle operativo en la guia.** -> Aumenta su longitud, pero evita que el operador deba saltar al README del softphone para el arranque y a otro documento para el rate.

## Migration Plan

Docs-only: no hay despliegue ni migracion de datos. Aplicacion = editar los dos documentos. Rollback = `git revert` de los archivos o restaurar desde el commit previo.
