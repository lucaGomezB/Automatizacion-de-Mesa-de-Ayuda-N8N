# Twilio — Canal Telefonico

Script TwiML y documentacion para la integracion de Twilio Programmable Voice con la mesa de ayuda N8N.

## Descripcion General

Cuando un usuario llama al numero virtual de la mesa de ayuda, Twilio ejecuta el script `twiml.xml`:

1. Reproduce un mensaje de bienvenida en espanol rioplatense
2. Graba el problema del usuario (maximo 45 segundos, finaliza con `#`)
3. Transcribe automaticamente la grabacion
4. Envia la transcripcion a N8N via webhook
5. Reproduce un mensaje de despedida confirmando el registro

El workflow N8N (`Automatizacion_Mesa_de_Ayuda.json`) procesa la transcripcion con un AI Agent (LangChain + Redis) y crea el incidente via la API FastAPI.

## Requisitos Previos

- Cuenta de Twilio (gratuita para desarrollo: https://www.twilio.com/try-twilio)
- Numero de telefono virtual comprado en Twilio
- N8N corriendo con el workflow importado (el nodo `twilioTrigger` escucha `call-summary.complete`)

## Paso a Paso

### 1. Crear cuenta Twilio

Registrarse en https://www.twilio.com/try-twilio. La cuenta gratuita incluye credito inicial para pruebas.

### 2. Obtener credenciales

En la consola de Twilio (https://console.twilio.com), copiar:

- **Account SID**: identificador de la cuenta
- **Auth Token**: token de autenticacion (se muestra solo al crearlo)
- Ambos valores van en las variables de entorno (ver seccion abajo)

### 3. Comprar un numero virtual

1. Ir a **Phone Numbers > Manage > Buy a Number**
2. Buscar numeros con capacidad **Voice**
3. Elegir uno con prefijo de Argentina (`+54`) si se desea numero local
4. Completar la compra (el credito gratuito cubre el costo mensual)

### 4. Configurar el webhook de voz

En la consola Twilio, ir a **Phone Numbers > Manage > Active Numbers**, hacer clic en el numero comprado, y en la seccion **Voice & Fax** configurar:

- **A call comes in**: URL del TwiML (ver opciones de hosting abajo)
- **Method**: HTTP GET
- Guardar cambios

### 5. Hosting del TwiML — tres opciones

Hay tres formas de servir `twiml.xml` a Twilio. Elegir la que mejor se adapte al entorno:

#### Opcion A: TwiML Bin (recomendado para desarrollo)

La mas simple. Sin infraestructura adicional.

1. Ir a **Develop > TwiML > TwiML Bins** en la consola Twilio
2. Crear un nuevo TwiML Bin con el boton `+`
3. Copiar y pegar el contenido completo de `twilio/twiml.xml`
4. Reemplazar `TU_DOMINIO` por la URL real del webhook N8N
5. Guardar: Twilio genera una URL publica (ej. `https://handler.twilio.com/twiml/EH...`)
6. Usar esa URL como **A call comes in** en la configuracion del numero

**Ventaja**: sin servidor, sin DNS. **Desventaja**: editar requiere entrar a la consola Twilio.

#### Opcion B: Hosting estatico

Servir `twiml.xml` desde cualquier servidor HTTP con Content-Type `text/xml`.

Ejemplos:
- **GitHub Pages**: subir `twiml.xml` a un repo publico, acceder via `https://<user>.github.io/<repo>/twilio/twiml.xml`
- **Netlify/Vercel**: deploy del archivo con redirect/rewrite para Content-Type correcto
- **S3/Cloud Storage**: bucket publico con Content-Type `text/xml`

**Ventaja**: versionado en git, actualizable sin consola Twilio. **Desventaja**: requiere DNS o URL publica.

#### Opcion C: Endpoint N8N (avanzado)

Crear un nodo Webhook en N8N que responda con el contenido del TwiML.

1. Agregar un nodo **Webhook** al workflow (metodo GET)
2. Conectar un nodo **Respond to Webhook** que devuelva el XML con header `Content-Type: text/xml`
3. Usar la URL del webhook de N8N como **A call comes in**

**Ventaja**: toda la logica centralizada en N8N. **Desventaja**: mayor complejidad, N8N debe estar siempre accesible.

### 6. Probar localmente con ngrok

Para pruebas locales sin exponer N8N a internet:

1. Instalar ngrok: https://ngrok.com/download
2. Iniciar tunel hacia el puerto de N8N:
   ```bash
   ngrok http 5678
   ```
3. Copiar la URL publica de ngrok (ej. `https://abc123.ngrok.io`)
4. Reemplazar `TU_DOMINIO` en `twiml.xml` por la URL de ngrok:
   ```
   transcribeCallback="https://abc123.ngrok.io/webhook/twilio-transcripcion"
   ```
5. Configurar el webhook de voz del numero Twilio con la URL del TwiML (puede ser el mismo ngrok si se usa Opcion C, o un TwiML Bin)
6. Llamar al numero Twilio y verificar que el flujo funciona

**Nota**: ngrok gratuito cambia la URL en cada reinicio. Para desarrollo continuo, considerar ngrok pro o una alternativa como Cloudflare Tunnel.

## Variables de Entorno

Agregar al archivo `.env` del backend (`Gestion_Incidentes/.env`):

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+54xxxxxxxxxx
TWILIO_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/webhook/transcripcion
```

| Variable | Descripcion | Donde obtenerla |
|----------|-------------|----------------|
| `TWILIO_ACCOUNT_SID` | Identificador de cuenta Twilio | Console > Account Info |
| `TWILIO_AUTH_TOKEN` | Token de autenticacion | Console > Account Info |
| `TWILIO_PHONE_NUMBER` | Numero virtual comprado | Console > Phone Numbers |
| `TWILIO_WEBHOOK_URL` | URL del webhook de transcripcion de N8N | N8N > Webhook node URL |

## Arquitectura del Flujo

```
Usuario llama al +54xxxxxxxxxx
        │
        ▼
Twilio contesta ──► GET twiml.xml (desde TwiML Bin / hosting / N8N)
        │
        ▼
Reproduce <Say> bienvenida (espanol rioplatense, Polly.Mia-Neural)
        │
        ▼
<Record> graba hasta 45s (usuario presiona # para terminar)
        │
        ▼
Reproduce <Say> despedida
        │
        ▼
Twilio transcribe ──► POST transcribeCallback ──► N8N twilioTrigger
        │
        ▼
N8N: AI Agent (LangChain) + Redis ──► POST /api/v1/incidentes ──► FastAPI
```

## Referencias

- [Documentacion TwiML](https://www.twilio.com/docs/voice/twiml)
- [TwiML <Say> reference](https://www.twilio.com/docs/voice/twiml/say)
- [TwiML <Record> reference](https://www.twilio.com/docs/voice/twiml/record)
- [Twilio Transcription](https://www.twilio.com/docs/voice/twiml/record#transcribe)
- [ngrok](https://ngrok.com/)
