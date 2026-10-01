## Context

Ver `proposal.md — Why`. Hechos verificados que moldean el enfoque:

- **Stack**: FastAPI + React + n8n + Postgres + Redis por Docker Compose, nombre de proyecto fijo `mesa_local`. Node v22 (nvm) y Twilio CLI v7 instalados; perfil `Luca` autenticado.
- **Dos números Twilio de EE. UU.**: `+13146487338` y `+12295958782`. AMBOS tienen `voiceUrl = https://tameness-trilogy-unrefined.ngrok-free.dev/api/v1/cost-guard/twilio/voice` (POST), dominio reservado servido por el servicio `ngrok` del compose (profile `tunnel`).
- **Auto-llamada bloqueada**: llamar de un número Twilio a otro de la misma cuenta devuelve error `21216 Account not allowed to call <own number>`. El "truco" Twilio-a-Twilio con TTS no es viable.
- **Costo internacional**: marcar el número de EE. UU. desde un celular argentino factura tarifa internacional.
- **Flujo telefónico (c-52)**: llamada entrante -> `POST /api/v1/cost-guard/twilio/voice` (valida `X-Twilio-Signature`, admisión de cost-guard) -> TwiML `<Say>` + `<Record maxLength=45 finishOnKey=# channels=mono>` con `recordingStatusCallback` y `action` -> backend descarga la grabación, STT (Gemini), pseudonimiza, handoff a n8n `POST /webhook/telefonia-handoff` -> n8n crea el incidente vía `POST /api/v1/incidentes`.
- **Firma**: el backend exige `X-Twilio-Signature` fail-closed y que `request.url` (reconstruida con `FORWARDED_ALLOW_IPS`) coincida con la URL pública (ngrok). Ver `app/cost_guard/twilio_signature.py` y `app/routes/cost_guard.py`.
- **Admisión**: `CostGuardService.reserve(provider, caller)` usa el `caller` CRUDO como clave del rate por origen (`AMBITO_CALLER`); el rate por origen por defecto es 3/hora (`cost_guard_caller_rate_limit_calls`). El webhook de voz reserva la superficie `PROVIDER_TWILIO`; el callback de grabación reserva `PROVIDER_BACKEND_STT` (c-52).
- **Patrón de tooling**: `scripts/corpus_ingest/` (CLI + lógica pura + tests offline + `requirements.txt` + README) y `scripts/dry_run/`. Se espeja ese estilo.

### Precondición / riesgo de c-52 (bloquea la verificación end-to-end)

El flujo telefónico HOY falla en el AI Agent de n8n con `NodeOperationError: "No session ID found"`: el nodo `memoryRedisChat` usa el parámetro de sesión (`sessionId`) mientras el nodo espera `sessionKey`/`sessionIdType`. Es un defecto de c-52, SEPARADO de esta herramienta, pero impide verificar el softphone de punta a punta (el incidente no se crea). Se documenta como dependencia/riesgo y se recomienda corregirlo dentro de c-52. La herramienta se verifica hasta el handoff a n8n.

## Goals / Non-Goals

**Goals:**

- Permitir que un operador inyecte su voz al pipeline telefónico existente desde el navegador, sin tramo PSTN internacional y sin auto-llamada.
- Mantener la herramienta aislada y de costo casi nulo: el audio entra por WebRTC, la grabación es `client` (no factura PSTN).
- Acuñar los Access Tokens localmente, con secretos solo desde entorno.
- Ser scriptable en el lado Twilio (API Key + TwiML App vía CLI) y estar documentado paso a paso.
- Tests offline donde sea factible (forma del token, validación de configuración).

**Non-Goals:**

- No es una funcionalidad de producción ni modifica el backend/el workflow de producción.
- No agrega un endpoint de token en el backend de producción; el acuñado es local y aislado.
- No cambia los cinco strings canónicos de sector ni los umbrales del clasificador.
- No reemplaza el canal telefónico ni la STT: solo inyecta audio en el flujo ya existente.
- No implementa una consola de operador con persistencia de tokens ni multi-usuario.

## Decisions

### D1: Softphone de navegador con TwiML App (WebRTC), no llamada PSTN

El operador abre una página local, el `Twilio.Device` (Voice SDK) se registra con un Access Token y `device.connect()` inicia una llamada saliente hacia el TwiML App. Twilio ejecuta la Voice URL del App en el contexto de la llamada: el `<Say>` y el `<Record>` de c-52 corren igual que en una llamada entrante, pero el audio grabado es el del micrófono del operador (leg `client`). No hay tramo PSTN a Argentina ni auto-llamada entre números de la misma cuenta.

Alternativa considerada: Twilio-a-Twilio con `<Say>`/TTS — descartada: bloqueada por `21216`. Alternativa: llamada de prueba desde un celular — descartada: costo internacional y no repetible.

### D2: La Voice URL del TwiML App REUTILIZA `/api/v1/cost-guard/twilio/voice` (backend sin cambios)

Se configura el TwiML App con `Voice URL = https://tameness-trilogy-unrefined.ngrok-free.dev/api/v1/cost-guard/twilio/voice` (POST), el MISMO endpoint que usa una llamada entrante. Ventaja: el operador entra directo al flujo real (incluida la admisión de cost-guard) sin un `<Dial>` a un número propio (que sería una auto-llamada). El backend NO se modifica.

**Implicación del `From = client:<identity>`**: en una llamada iniciada por un cliente Voice SDK, el webhook recibe `From` como `client:<identity>` (no E.164). La firma `X-Twilio-Signature` se valida igual (Twilio firma la URL + params). La admisión de cost-guard usa ese `From` como clave del rate por origen; con la identidad del operador el contador `caller` acumula y a la tercera llamada en una hora la guarda denegaría con `CAUSE_CALLER_RATE` (comportamiento EXISTENTE, no un bug).

**Mitigación**: la utilidad acuña por defecto una identidad ÚNICA por sesión (`softphone-dev-<timestamp>`), de modo que cada corrida usa una clave `caller` distinta y el rate por origen no corta las pruebas. La bolsa global (`COST_GUARD_BUDGET_USD`) y el rate global (30/h) SIGUEN aplicando, que es el comportamiento deseado de seguridad de costo. Se permite fijar la identidad con `--identity` para escenarios que quieran ejercitar el rate.

Alternativa considerada: un TwiML dev dedicado (TwiML Bin o endpoint dev-only que graba sin admisión) — descartada: omitiría la guarda de costo y/u obligaría a tocar el backend de producción, contra el non-goal. Alternativa: bypass dev-only del caller rate en el backend — descartada: modifica producción.

### D3: Utilidad de token en Python con el SDK oficial `twilio` (requirements aislado)

El acuñado usa `twilio.jwt.access_token.AccessToken` + `twilio.jwt.access_token.grants.VoiceGrant` del SDK oficial, declarado en `scripts/voip_softphone/requirements.txt` (no se toca `App/Backend/requirements.txt`). El token es un JWT HS256 con `iss` = API Key SID, `sub` = Account SID, `grants.voice.outgoing.application_sid` = TwiML App SID, `grants.identity` = identidad, `exp` acotado (default 1800 s) y `jti`.

Rationale: delega la construcción del JWT y del grant al SDK mantenido (misma lógica con la que se validó la firma contra `twilio-python`), evita reintroducir criptografía a mano y mantiene la herramienta en Python, consistente con `scripts/corpus_ingest/`. Los tests offline decodifican y verifican el JWT con el API Key Secret, sin red.

Alternativas consideradas: PyJWT con claims manuales — descartada: reimplementa el formato del grant y es más frágil. HMAC manual con stdlib — descartada: más superficie de error criptográfico. Node con `twilio` npm — descartada: menos consistente con el tooling del repo.

### D4: Página estática sin build + servidor de token en loopback

El softphone es UN archivo `softphone.html` que carga `@twilio/voice-sdk` desde el CDN de Twilio (sin bundler, sin `node_modules`). La utilidad `mint_token.py serve` levanta un `ThreadingHTTPServer` de la stdlib en `127.0.0.1:8765` que sirve `GET /` (el HTML) y `GET /token` (JWT fresco en JSON), ambos por el mismo origen: sin CORS. El modo `mint_token.py token` imprime un token para inspección. El servidor se ata SOLO a loopback y emite tokens de vida corta.

Alternativa considerada: `python -m http.server` sirviendo el HTML y un token escrito a archivo — descartada: el token caduca y obligaría a regenerar/recargar a mano; un servidor de token mínimo es más simple de operar y sigue sin build.

### D5: Configuración de Twilio scriptable con el CLI + doc de respaldo

`scripts/voip_softphone/setup_twilio.py` (o `.sh`) usa el Twilio CLI con el perfil `Luca` para: crear un API Key (`twilio api:core:keys:create`), crear un TwiML App (`twilio api:core:applications:create --voice-url ... --voice-method POST`) y mostrar los SIDs. El API Key Secret se muestra UNA sola vez: el script instruye capturarlo en el entorno y NUNCA escribirlo a un archivo versionado. El README documenta la alternativa manual por consola y las variables exactas.

### D6: Ubicación, estilo y gobernanza

Todo vive en `scripts/voip_softphone/` (mirroring `scripts/corpus_ingest/`): CLI + lógica pura + `test_*.py` offline + `requirements.txt` + `README.md`. Gobernanza MEDIUM: es tooling de desarrollo; el operador configura la cuenta Twilio; no hay código de auth ni de facturación. Secretos solo por entorno; `.githooks/pre-commit` y gitleaks los bloquean.

## Risks / Trade-offs

- **[c-52 `No session ID found`]** bloquea la creación del incidente -> Mitigación: documentar como dependencia; verificar hasta el handoff; recomendar el fix en c-52.
- **[Rate por origen]** identidad `client:` acumula en `caller` -> Mitigación: identidad única por sesión (D2); el gasto sigue acotado por las bolsas globales.
- **[Costo]** la admisión reserva `PROVIDER_TWILIO` y la STT `PROVIDER_BACKEND_STT` aun con audio `client` -> Mitigación: son estimaciones acotadas; el audio WebRTC no tiene tarifa PSTN y la grabación dura como máximo 45 s.
- **[Secretos]** el API Key Secret es de un solo uso visible -> Mitigación: se captura en entorno; nunca a disco versionado; hook + gitleaks.
- **[ngrok]** el túnel debe estar arriba y el dominio whitelisteado en nginx -> Mitigación: documentar `docker compose -p mesa_local --profile tunnel up -d ngrok` y los tres lugares donde el dominio debe coincidir.
- **[Firma]** la Voice URL del App debe ser EXACTAMENTE la URL pública -> Mitigación: usar el mismo valor que los números y `BACKEND_PUBLIC_BASE_URL`.

## Migration Plan

1. Crear `scripts/voip_softphone/` con la utilidad de token, el HTML, el servidor local, el script de setup y los tests.
2. Configurar Twilio (API Key + TwiML App) con el CLI o por consola; cargar los valores en el entorno.
3. Levantar el backend + n8n + ngrok; correr `mint_token.py serve`.
4. Colocar una llamada de prueba desde el navegador y verificar el handoff a n8n.
5. Rollback: borrar `scripts/voip_softphone/`; en Twilio, borrar el TwiML App y el API Key. No hay migraciones ni datos.

## Open Questions

1. **Identidad por defecto**: confirmar el prefijo canónico de la identidad dev (`softphone-dev-<timestamp>`) y si conviene exponer `--identity` en el HTML o solo por CLI.
2. **TLL del token**: confirmar 1800 s como TTL por defecto del Access Token (dentro del máximo permitido) y si la UI debe re-acuñar antes de expirar.
3. **Manejo del API Key Secret**: confirmar si el script de setup debe imprimir el secret a stdout (para pasarlo a una variable) o exigir creación manual para evitar que quede en el historial de shell.
4. **Alcance del setup**: decidir si `setup_twilio` crea el TwiML App apuntando ya al dominio ngrok reservado o si requiere que el operador pase `--voice-url` explícitamente.
