# Twilio — Canal Telefonico

Documentacion para la integracion de Twilio Programmable Voice con la mesa de ayuda N8N.

## Descripcion General

El TwiML ya NO se sirve como archivo estatico. La URL de voz del numero de Twilio
apunta al **webhook pre-llamada del backend**, que consulta la guarda de costo
(c-45) y decide antes de grabar:

```
POST /api/v1/cost-guard/twilio/voice
```

- PERMITIDO: el backend responde TwiML con `<Say>` de bienvenida + `<Record>` mono
  (SIN `transcribe`) con `recordingStatusCallback` y `action` (el contenido de
  referencia vive en `n8n/twilio/twiml.xml`). El `<Say>` de cierre se sirve en el
  documento `action`, `POST /api/v1/telefonia/record-complete`.
- DENEGADO: el backend responde `<Say>` + `<Hangup/>`, de modo que no se grabe.

La grabacion la procesa el backend: Twilio invoca
`POST /api/v1/telefonia/recording-status` cuando la grabacion esta disponible; el
backend descarga el audio (Basic auth), lo transcribe con el motor dedicado de
speech-to-text (Gemini), lo pseudonimiza y hace handoff a N8N por webhook
(`n8n_telefonia_webhook_url`, header `X-N8N-Secret`). El workflow
(`n8n/workflow.json`) pasa por el nodo `Guard de costo` antes del AI Agent.

## Requisitos Previos

- Cuenta de Twilio (https://www.twilio.com/try-twilio)
- Numero de telefono virtual comprado en Twilio
- Backend accesible desde internet por HTTPS (el webhook pre-llamada)
- `TWILIO_AUTH_TOKEN` cargado en `App/Backend/.env`
- N8N corriendo con el workflow importado (el nodo `webhook` de telefonia recibe
  el handoff pseudonimizado del backend)

## Paso a Paso

### 1. Crear cuenta Twilio

Registrarse en https://www.twilio.com/try-twilio. La cuenta gratuita incluye
credito inicial para pruebas.

### 2. Obtener credenciales

En la consola de Twilio (https://console.twilio.com), copiar:

- **Account SID**: identificador de la cuenta
- **Auth Token**: token de autenticacion (se muestra solo al crearlo)

### 3. Comprar un numero virtual

1. Ir a **Phone Numbers > Manage > Buy a Number**
2. Buscar numeros con capacidad **Voice**
3. Elegir uno con prefijo de Argentina (`+54`) si se desea numero local
4. Completar la compra

### 4. Configurar el webhook de voz (obligatorio)

En la consola Twilio, ir a **Phone Numbers > Manage > Active Numbers**, hacer clic
en el numero comprado y en la seccion **Voice & Fax** configurar:

- **A call comes in**: `https://<backend-publico>/api/v1/cost-guard/twilio/voice`
- **Method**: **HTTP POST**

La URL debe ser la MISMA URL publica que Twilio firma (ver "Autenticacion del
webhook"). No usar un TwiML Bin ni hosting estatico: esas opciones **omiten la
guarda de costo** y no deben usarse.

### 5. Autenticacion del webhook

Twilio Programmable Voice **no puede** adjuntar headers personalizados. Su unico
mecanismo de autenticacion es la firma `X-Twilio-Signature` (HMAC-SHA1 sobre la
URL completa mas los parametros de formulario ordenados), que Twilio envia en
todas sus peticiones.

- Con `TWILIO_AUTH_TOKEN` configurado, el backend exige una firma valida: toda
  peticion sin firma valida responde **HTTP 401**.
- Sin `TWILIO_AUTH_TOKEN`, el backend responde **HTTP 401** (fail-closed) y emite
  `cost_guard_twilio_token_missing` al arrancar. Cargar el token activa la
  validacion de firma sin ningun otro cambio.
- El header `X-Cost-Guard-Secret` **no** se usa en este endpoint (Twilio no puede
  enviarlo); se reserva para el endpoint de reserva que consume n8n.

> **Caveat de proxy**: Twilio firma la URL publica configurada en su consola. Si el
> backend corre detras de Nginx, la URL reconstruida por FastAPI debe coincidir con
> esa URL publica (esquema, host, puerto, path y query). Un desajuste produce 401
> por firma invalida aunque la peticion provenga de Twilio.

### 6. Probar localmente con ngrok

Para pruebas locales sin exponer el stack a internet:

1. Instalar ngrok: https://ngrok.com/download
2. Iniciar el tunel hacia Nginx (puerto 443) para exponer el backend:
   ```bash
   ngrok http 443
   ```
3. Copiar la URL publica de ngrok (ej. `https://abc123.ngrok.io`)
4. Configurar **A call comes in** con
   `https://abc123.ngrok.io/api/v1/cost-guard/twilio/voice` y **Method: POST**
5. Configurar `BACKEND_PUBLIC_BASE_URL` en `App/Backend/.env` con la URL publica
   de ngrok, de modo que los callbacks del `<Record>` (`recordingStatusCallback`
   y `action`) apunten a endpoints alcanzables por Twilio.
6. Llamar al numero Twilio y verificar que el flujo funciona.

**Nota**: ngrok gratuito cambia la URL en cada reinicio. Para desarrollo continuo,
considerar ngrok pro o una alternativa como Cloudflare Tunnel.

## Variables de Entorno

Backend (`App/Backend/.env`):

| Variable | Descripcion | Donde obtenerla |
|----------|-------------|-----------------|
| `TWILIO_AUTH_TOKEN` | Token de autenticacion; habilita la validacion de `X-Twilio-Signature` en el webhook de voz | Console > Account Info |
| `TWILIO_ACCOUNT_SID` | Identificador de cuenta Twilio; el backend lo usa como usuario del HTTP Basic (`AccountSid:AuthToken`) para descargar la grabacion | Console > Account Info |
| `TWILIO_PHONE_NUMBER` | Numero virtual comprado (referencia) | Console > Phone Numbers |
| `BACKEND_PUBLIC_BASE_URL` | Base publica del backend tal como la ve Twilio; construye los callbacks del `<Record>` (estado de grabacion y accion de cierre) | URL publica del backend (p. ej. el host de Nginx) |
| `N8N_TELEFONIA_WEBHOOK_URL` | URL del webhook de handoff de telefonia en N8N; sin valor, el handoff se omite con evento observable | n8n (nodo `webhook` de telefonia) |

N8N (`.env` de la RAIZ del repo, inyectado por `docker-compose.yml`):

| Variable | Descripcion |
|----------|-------------|
| `COST_GUARD_SHARED_SECRET` | Secreto compartido del endpoint de reserva; el nodo `Guard de costo` lo envia como `X-Cost-Guard-Secret`. Fuente unica: la raiz del repo, inyectada tambien en el backend |

## Arquitectura del Flujo

```
Usuario llama al +54xxxxxxxxxx
        │
        ▼
Twilio contesta ──► POST /api/v1/cost-guard/twilio/voice (backend, firma X-Twilio-Signature)
        │
        ├─ DENEGADO ──► <Say> + <Hangup/> (sin grabar)
        │
        └─ PERMITIDO ──► <Say> bienvenida + <Record> mono (sin transcribe, callbacks)
        │
        ▼
Twilio recordingStatusCallback ──► POST /api/v1/telefonia/recording-status (backend)
        │  idempotencia CallSid ──► reserva backend_stt ──► descarga Basic auth
        │  ──► Gemini STT ──► pseudonimiza
        ▼
Backend ──► POST /webhook/telefonia-handoff (X-N8N-Secret) ──► N8N webhook
        │
        ▼
N8N: Guard de costo ──► AI Agent (LangChain) + Redis ──► POST /api/v1/incidentes ──► FastAPI
```

## Referencias

- [Twilio webhooks security](https://www.twilio.com/docs/usage/webhooks/webhooks-security)
- [Documentacion TwiML](https://www.twilio.com/docs/voice/twiml)
- [TwiML <Say> reference](https://www.twilio.com/docs/voice/twiml/say)
- [TwiML <Record> reference](https://www.twilio.com/docs/voice/twiml/record)
- [ngrok](https://ngrok.com/)
