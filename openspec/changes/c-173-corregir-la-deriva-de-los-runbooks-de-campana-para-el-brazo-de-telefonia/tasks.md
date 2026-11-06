## 1. Prerequisitos y anclaje canonico

- [x] 1.1 Confirmar la ausencia de deriva inversa: `grep -rln "voip_softphone\|mint_token" docs/` NO devuelve coincidencias (hoy la herradura del softphone no figura en ningun documento de campana).
- [x] 1.2 Confirmar el default de base URL y el flag requerido: `grep -n "DEFAULT_BASE_URL" scripts/corpus_ingest/ingest_via_n8n.py` informa `https://localhost` y `grep -n "insecure" scripts/corpus_ingest/README.md` muestra el flag documentado.
- [x] 1.3 Confirmar los rates base: `grep -n "cost_guard_rate_limit_calls\|cost_guard_caller_rate_limit_calls" App/Backend/app/config/settings.py` informa `= 30` y `= 3`, y `grep -n "COST_GUARD_RATE_LIMIT_CALLS" docker-compose.yml` muestra el `"200"` SOLO en el perfil `corpus`.
- [x] 1.4 Confirmar el stack de la campana y el tunel: `grep -n "tameness-trilogy-unrefined" docker-compose.yml App/Backend/.env` muestra el dominio reservado en el comando de ngrok y en `BACKEND_PUBLIC_BASE_URL`.
- [x] 1.5 Confirmar que el `env_file` del backend base es `App/Backend/.env`: `grep -n "env_file" docker-compose.yml` lo lista para el servicio `backend`.
- [x] 1.6 Confirmar que las fuentes de verdad del softphone existen: `scripts/voip_softphone/README.md` (secciones 2, 4, 5 y 6) y `scripts/voip_softphone/mint_token.py` (`serve` en `127.0.0.1:8765`, identidad unica por sesion).

## 2. `docs/campana-medicion/guia-ejecucion-campana.md`

- [x] 2.1 Corregir el flag: agregar `--insecure` al ejemplo de `ingest_telefonia_corpus.py` de la seccion 1.5.2 y declarar que aplica a las 4 corridas por sub-plan `automatizado`; verificar con `grep -n "ingest_telefonia_corpus.py" -A 5 docs/campana-medicion/guia-ejecucion-campana.md` que la linea del comando incluye `--insecure`.
- [x] 2.2 Documentar el procedimiento del brazo de telefonia: softphone sobre el stack principal, `python3 scripts/voip_softphone/mint_token.py serve` en `127.0.0.1:8765`, abrir `http://127.0.0.1:8765/`, elegir "Caso del corpus (telefono)", `Call`/`Hangup`, recitar el texto; orden por `posicion` y eleccion del `corpus_case_id`, para las mitades de `O1`/`O2`; verificar con `grep -n "mint_token.py serve\|127.0.0.1:8765\|corpus_case_id" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 2.3 Documentar el prerequisito de la guarda de costo: 81 llamadas vs `COST_GUARD_RATE_LIMIT_CALLS` global 30/h; subir (por ejemplo a 200) en `App/Backend/.env` y recrear (`docker compose up -d backend`); aclarar que la identidad unica por sesion evita el rate por origen (3/h) pero NO el global; verificar con `grep -n "COST_GUARD_RATE_LIMIT_CALLS\|docker compose up -d backend" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 2.4 Documentar los prerequisitos de Twilio: numeros, Voice URL del TwiML App y `BACKEND_PUBLIC_BASE_URL` iguales al dominio ngrok reservado; `TWILIO_ACCOUNT_SID` desde `App/Backend/.env` y `TWILIO_API_KEY_SID`/`TWILIO_API_KEY_SECRET`/`TWILIO_TWIML_APP_SID` desde `scripts/voip_softphone/softphone.env`; verificar con `grep -n "TWILIO_TWIML_APP_SID\|BACKEND_PUBLIC_BASE_URL\|ngrok" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 2.5 Declarar la fuente de verdad unica: remitir a `scripts/voip_softphone/README.md` para el detalle y NO reproducir su contenido; verificar con `grep -n "scripts/voip_softphone/README.md" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 2.6 Aclarar que la campana NO usa el perfil aislado `corpus` (`docs/runbook-corpus-telefonia.md`, c-70); verificar con `grep -in "perfil corpus\|runbook-corpus-telefonia" docs/campana-medicion/guia-ejecucion-campana.md`.

## 3. `docs/campana-medicion/runbook-campana-contrabalanceada.md`

- [x] 3.1 Corregir el flag: agregar `--insecure` al ejemplo de `ingest_telefonia_corpus.py` de la seccion 5.4; verificar con `grep -n "ingest_telefonia_corpus.py" -A 5 docs/campana-medicion/runbook-campana-contrabalanceada.md` que el comando incluye `--insecure`.
- [x] 3.2 Documentar el procedimiento del operador del softphone en 5.4 (arranque con `mint_token.py serve`, pagina `127.0.0.1:8765`, orden por `posicion`, eleccion del `corpus_case_id`), remitiendo a `scripts/voip_softphone/README.md`; verificar con `grep -n "mint_token.py serve\|corpus_case_id\|scripts/voip_softphone/README.md" docs/campana-medicion/runbook-campana-contrabalanceada.md`.
- [x] 3.3 Documentar los prerequisitos (guarda de costo y Twilio) en 5.4 o en la seccion 0, coherentes con la guia; verificar con `grep -n "COST_GUARD_RATE_LIMIT_CALLS\|TWILIO_TWIML_APP_SID" docs/campana-medicion/runbook-campana-contrabalanceada.md`.
- [x] 3.4 Aclarar que la campana corre sobre el stack principal y no sobre el perfil `corpus`; verificar con `grep -in "perfil corpus" docs/campana-medicion/runbook-campana-contrabalanceada.md`.

## 4. Verificacion transversal

- [x] 4.1 Verificar que no se toco codigo ni configuracion: `git status --porcelain` lista solo los dos documentos de `docs/campana-medicion/` y el directorio del change (mas los artefactos de campana preexistentes, ajenos a este change).
- [x] 4.2 Verificar que ambos ejemplos de telefonia llevan `--insecure`: `grep -n "ingest_telefonia_corpus.py" -A 5 docs/campana-medicion/guia-ejecucion-campana.md docs/campana-medicion/runbook-campana-contrabalanceada.md` muestra el flag en los dos.
- [x] 4.3 Verificar que la referencia al softphone aparece en ambos documentos y que no se duplica su README completo: `grep -rn "scripts/voip_softphone/README.md" docs/campana-medicion/` devuelve dos coincidencias.
- [x] 4.4 Verificar que `evaluation/data/campana/README.md` NO fue modificado: `git diff --quiet -- evaluation/data/campana/README.md` termina con exit 0.
- [x] 4.5 Ejecutar `openspec validate "c-173-corregir-la-deriva-de-los-runbooks-de-campana-para-el-brazo-de-telefonia" --strict --no-interactive` y confirmar PASS.
