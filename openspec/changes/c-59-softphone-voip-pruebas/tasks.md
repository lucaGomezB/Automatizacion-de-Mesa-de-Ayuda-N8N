## 1. Preparación, defaults y estructura

- [ ] 1.1 Registrar el baseline de las suites que se van a tocar (solo scripts, sin backend): ejecutar `python -m pytest scripts/corpus_ingest scripts/dry_run -q` y anotar el conteo en verde; si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificación: conteo de baseline anotado.
- [ ] 1.2 Resolver las Open Questions del `design.md` con defaults explícitos antes de codificar: identidad por defecto `softphone-dev-<timestamp>`, TTL del token 1800 s, el API Key Secret se captura en entorno (nunca a archivo) y `setup_twilio` recibe `--voice-url` con el valor por defecto del dominio ngrok reservado. Verificación: los cuatro defaults quedan anotados en `design.md` como resueltos.
- [ ] 1.3 Crear la estructura `scripts/voip_softphone/` con placeholders `mint_token.py`, `softphone.html`, `setup_twilio.py`, `requirements.txt`, `README.md` y verificar que la carpeta contiene exactamente esos archivos. Verificación: `ls scripts/voip_softphone/`.

## 2. Utilidad de acuñado de token (TDD)

- [ ] 2.1 RED: escribir `scripts/voip_softphone/test_mint_token.py` que describa la forma del Access Token: JWT HS256 firmado con el API Key Secret, `iss` = API Key SID, `sub` = Account SID, `grants.voice.outgoing.application_sid` = TwiML App SID, `grants.identity` = identidad y `exp` futuro acotado. Ejecutar y confirmar que falla por módulo inexistente. Verificación: test en rojo.
- [ ] 2.2 GREEN: implementar `mint_token.py` usando `twilio.jwt.access_token.AccessToken` + `VoiceGrant` del SDK oficial, con secretos leídos solo de entorno. Verificación: `python -m pytest scripts/voip_softphone/test_mint_token.py -q` en verde.
- [ ] 2.3 TRIANGULATE: agregar casos de (a) identidad explícita vs. identidad única por defecto (dos corridas producen identidades distintas y ambas válidas), (b) TTL configurable acotado, y (c) el modo CLI que imprime el token. Verificación: todos los casos en verde, sin red.
- [ ] 2.4 RED: escribir el caso de validación de configuración: sin las variables de entorno requeridas la utilidad aborta con un mensaje claro y código de salida no cero. Verificación: test en rojo.
- [ ] 2.5 GREEN: implementar la validación de entorno. Verificación: el test de 2.4 pasa; cubrir las variables faltantes requeridas (`TWILIO_ACCOUNT_SID`, `TWILIO_API_KEY_SID`, `TWILIO_API_KEY_SECRET`, `TWILIO_TWIML_APP_SID`).
- [ ] 2.6 Aislar la dependencia en `scripts/voip_softphone/requirements.txt` (SDK `twilio`) y verificar que `pip install -r scripts/voip_softphone/requirements.txt` es suficiente para correr los tests. Verificación: tests en verde tras la instalación aislada.

## 3. Servidor local y página del softphone

- [ ] 3.1 RED: escribir `scripts/voip_softphone/test_serve.py` que describa el servidor local: `GET /` devuelve el HTML del softphone, `GET /token` devuelve un JWT fresco en JSON y el binding es EXCLUSIVAMENTE loopback. Verificación: test en rojo.
- [ ] 3.2 GREEN: implementar el modo `serve` de `mint_token.py` con `http.server.ThreadingHTTPServer` en `127.0.0.1`, sirviendo la página y el token desde el mismo origen. Verificación: `python -m pytest scripts/voip_softphone/test_serve.py -q` en verde.
- [ ] 3.3 TRIANGULATE: cubrir que el token servido es acuñado por request (no un valor fijo) y que una ruta desconocida responde 404. Verificación: casos en verde.
- [ ] 3.4 Crear `scripts/voip_softphone/softphone.html` con el Voice SDK desde CDN, indicador de estado y botones Call/Hangup; `device.connect()` inicia la llamada al TwiML App y el botón de fin la desconecta. Verificación estructural: el HTML no requiere build, carga el SDK del CDN y contiene los tres elementos (estado, Call, Hangup); validar que el servidor de 3.2 lo entrega en `GET /`.

## 4. Configuración scriptable de Twilio

- [ ] 4.1 RED: escribir `scripts/voip_softphone/test_setup_twilio.py` que describa la construcción de los comandos del Twilio CLI (API Key y TwiML App con `--voice-url`/`--voice-method POST`) y el perfil `Luca`, con el CLI inyectado/fakeado. Verificación: test en rojo.
- [ ] 4.2 GREEN: implementar `setup_twilio.py` que construye y ejecuta los comandos, mostrando API Key SID, API Key Secret (solo una vez) y TwiML App SID. Verificación: `python -m pytest scripts/voip_softphone/test_setup_twilio.py -q` en verde.
- [ ] 4.3 TRIANGULATE: cubrir el `--voice-url` por defecto (endpoint de voz existente sobre el dominio ngrok reservado) y el override explícito; verificar que el script NO escribe el secret a ningún archivo. Verificación: casos en verde.

## 5. Documentación operativa

- [ ] 5.1 Escribir `scripts/voip_softphone/README.md` con la guía paso a paso: prerequisites (stack, ngrok, Twilio CLI `Luca`), creación del API Key y TwiML App (script y alternativa manual), variables de entorno exactas, arranque del servidor y colocación de la llamada. Verificación: un lector puede seguirla sin leer el código; lista las cinco variables de entorno y el comando del servidor.
- [ ] 5.2 Documentar en el README la implicación del `From = client:<identity>` en la guarda de costo (rate por origen) y la mitigación de identidad única por sesión. Verificación: la sección existe y menciona el rate por origen.
- [ ] 5.3 Documentar en el README la dependencia/riesgo de c-52 (`memoryRedisChat`: "No session ID found") que bloquea la creación del incidente en la verificación end-to-end. Verificación: la sección de limitaciones lo referencia como defecto de c-52.

## 6. Verificación integrada

- [ ] 6.1 Correr la suite offline de la herramienta desde la raíz: `python -m pytest scripts/voip_softphone -q`. Verificación: todos los tests en verde sin red ni credenciales reales.
- [ ] 6.2 Confirmar que no hay secretos versionados: `git status` de la carpeta y `python3 scripts/security/scan_engram_secrets.py` (si aplica) sobre los archivos nuevos; verificar que `.env` de la herramienta (si existe) está gitignorado y que ningún archivo contiene un secret real. Verificación: sin hallazgos; el hook `.githooks/pre-commit` no bloquea.
- [ ] 6.3 Verificación en vivo (manual, documentada): con backend + n8n + ngrok arriba, correr `mint_token.py serve`, colocar una llamada desde el navegador, confirmar el `<Say>`/`<Record>` y el handoff a n8n. NOTA: la creación del incidente puede fallar por el defecto de c-52; registrar el resultado y no marcar como fallo de esta herramienta. Verificación: el callback de grabación y el handoff ocurren; el resultado se registra en el README o en un anexo.
- [ ] 6.4 Ejecutar `openspec validate --strict --changes c-59-softphone-voip-pruebas` y confirmar que pasa. Verificación: validación estricta en verde.
