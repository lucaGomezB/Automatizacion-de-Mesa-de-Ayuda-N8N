## Why

El canal de telefonía (c-52) no se puede probar de forma barata ni repetible. Llamar al número Twilio de EE. UU. desde un celular argentino genera cargos internacionales; llamar de un número Twilio a otro número de la MISMA cuenta está bloqueado por Twilio (error `21216`, `Account not allowed to call <own number>`). Por eso el "truco" Twilio-a-Twilio con TTS no es viable. Se necesita una herramienta de DESARROLLO que permita a un operador inyectar su voz en el pipeline telefónico existente sin una llamada PSTN internacional.

## What Changes

- Agrega una herramienta standalone de desarrollo en `scripts/voip_softphone/`: un softphone VoIP de navegador (Twilio Voice SDK sobre WebRTC) que permite al operador hablar por el micrófono y que esa voz entre al flujo telefónico y cree un incidente.
- Agrega una utilidad local de acuñado de Access Token de Twilio (JWT HS256 con `VoiceGrant` y una identidad), con secretos EXCLUSIVAMENTE desde variables de entorno.
- Agrega una página HTML estática (sin paso de build) con indicador de estado y botones Call/Hangup; obtiene el token y coloca la llamada.
- Sirve la página y el token en un servidor local de loopback dentro de la misma utilidad (sin CORS, sin build).
- Documenta y automatiza la configuración del lado Twilio (API Key + TwiML App) mediante el Twilio CLI (perfil `Luca`).
- Entrega una guía operativa paso a paso como entregable explícito.
- NO modifica el flujo de producción del backend: reutiliza el endpoint de voz existente.

## Capabilities

### New Capabilities

- `telephony-test-softphone`: herramienta de desarrollo que inyecta audio de un operador en el pipeline telefónico mediante un softphone de navegador, con acuñado local de tokens y configuración scriptable de Twilio.

### Modified Capabilities

- None

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `scripts/voip_softphone/` | New | Softphone HTML, utilidad de token, servidor local, script de configuración, tests y README |
| `scripts/voip_softphone/requirements.txt` | New | Dependencia aislada del SDK de Twilio para el acuñado de tokens |
| Cuenta Twilio | Config | API Key y TwiML App creadas por CLI (perfil `Luca`); la Voice URL reutiliza el endpoint existente |
| `App/Backend/` | Sin cambios | El backend de producción no se modifica |
| `.gitignore` / higiene de secretos | Sin cambios | Los secretos quedan en entorno; el hook `.githooks/pre-commit` y gitleaks los bloquean |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| La admisión de cost-guard recibe un `From` no-E.164 (`client:<identity>`) y el rate por origen (3/h) corta pruebas repetidas | Med | Identidad única por sesión de prueba (default con marca de tiempo); no se toca el backend. La bolsa global y el rate global siguen acotando el gasto |
| Defecto de sesión de `memoryRedisChat` en el intake telefónico | Baja (residual) | RESUELTO: c-52 ya corrigió el nodo de memoria (commit `4946584`: `sessionIdType: customKey` + `sessionKey`), por lo que el intake telefónico es funcional y la verificación 6.3 puede confirmar la creación end-to-end del incidente. Riesgo residual bajo: verificar contra el estado ACTUAL de `n8n/workflow.json`, no contra el baseline previo al fix |
| Fuga de secretos (API Key secret) | Low | Secretos solo por entorno; el secret del API Key se muestra una sola vez; hook + gitleaks |
| Dependencia nueva (`twilio` SDK) | Low | Requirements aislado en `scripts/voip_softphone/`; no se toca el backend |

## Rollback Plan

Eliminar `scripts/voip_softphone/` revierte todo el código de la herramienta. En Twilio, borrar el TwiML App y el API Key creados (`twilio api:core:applications:delete`, `twilio api:core:keys:delete`) restaura el estado previo; los números y su `voiceUrl` apuntan al endpoint existente y no se modifican. No hay migraciones ni cambios de datos.

## Dependencies

- Cuenta Twilio con al menos un número con capacidad Voice y el túnel ngrok activo (`--profile tunnel`).
- Twilio CLI v7 autenticado (perfil `Luca`) para la configuración scriptable.
- Backend y n8n arriba para la verificación end-to-end.

## Success Criteria

- [ ] Un operador coloca una llamada desde el navegador y su voz entra al pipeline telefónico sin tramo PSTN internacional.
- [ ] El Access Token se acuña localmente con `VoiceGrant` (`outgoingApplicationSid` + identidad) y secretos solo desde entorno.
- [ ] La Voice URL del TwiML App reutiliza el endpoint existente y el backend de producción queda sin cambios.
- [ ] La guía operativa paso a paso permite configurar las credenciales y correr el softphone.
- [ ] Tests offline cubren la forma del token y la validación de configuración.
- [ ] `openspec validate --strict --changes c-59-softphone-voip-pruebas` pasa.
