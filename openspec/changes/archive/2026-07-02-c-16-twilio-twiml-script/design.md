# Diseno: Script TwiML para Twilio Programmable Voice

## Decisiones de Arquitectura

### D-01: Estructura del TwiML

El script sigue la especificacion TwiML de Twilio con tres verbos secuenciales:

```xml
<Response>
    <Say>  <!-- Bienvenida en espanol rioplatense -->
    <Record>  <!-- Grabacion con configuracion -->
    <Say>  <!-- Mensaje de despedida -->
</Response>
```

**Justificacion**: Es la estructura canonica para un IVR simple de recepcion de incidentes. No requiere branching (Gather) porque el flujo es lineal: bienvenida -> grabacion -> despedida.

### D-02: Voz y Lenguaje

- **Voice**: `Polly.Mia-Neural` (AWS Polly, voz femenina, ingles americano)
- **Language**: `es-US` (espanol latinoamericano, el acento mas cercano al rioplatense disponible en Polly)

**Alternativa considerada**: `alice` (voz TTS nativa de Twilio) con `es-MX`. Se descarto porque Polly.Mia-Neural produce un acento mas natural y menos robotico. La combinacion `es-US` + `Polly.Mia-Neural` es la que mejor se aproxima al espanol rioplatense entre las opciones disponibles.

**Nota**: Twilio no ofrece una voz especifica para espanol rioplatense/argentino. `es-US` con `Polly.Mia-Neural` es la mejor aproximacion disponible.

### D-03: Configuracion de Grabacion

```xml
<Record
    maxLength="45"
    finishOnKey="#"
    transcribe="true"
    transcribeCallback="https://TU_DOMINIO/webhook/twilio-transcripcion"
    playBeep="true"
/>
```

| Atributo | Valor | Justificacion |
|----------|-------|--------------|
| `maxLength` | `45` | La tesis especifica 45 segundos (Seccion 6.4) |
| `finishOnKey` | `#` | Estandar en IVRs: el usuario presiona numeral para terminar |
| `transcribe` | `true` | Twilio transcribe automaticamente --- no necesitamos servicio externo |
| `transcribeCallback` | placeholder | Webhook de N8N que recibe la transcripcion |
| `playBeep` | `true` | Indica al usuario que la grabacion comenzo |

### D-04: Ubicacion del Archivo

```
twilio/
├── twiml.xml      # Script TwiML para Twilio
└── README.md      # Instrucciones de configuracion
```

**Justificacion**: Directorio dedicado en la raiz del proyecto. Separado de `Gestion_Incidentes/` (backend) y `Frontend/` porque es un asset de infraestructura, no de aplicacion. Coopera con N8N, no con FastAPI.

### D-05: Hosting del TwiML

Tres opciones documentadas (de menor a mayor complejidad):

1. **TwiML Bin** (recomendado para desarrollo): Se copia el contenido del XML en un TwiML Bin de la consola Twilio. URL publica generada por Twilio. Sin infraestructura adicional.
2. **Hosting estatico**: Servir `twiml.xml` desde GitHub Pages, Netlify, o S3 con Content-Type `text/xml`.
3. **Endpoint N8N**: N8N sirve el TwiML como respuesta a un webhook entrante. Mas complejo pero centraliza toda la logica en N8N.

### D-06: Variables de Entorno

Se agregan a `Gestion_Incidentes/.env.example` porque es el unico archivo `.env.example` del repositorio y las variables de Twilio son necesarias para el ecosistema completo:

```
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+54xxxxxxxxxx
TWILIO_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/webhook/transcripcion
```

### D-07: Redaccion del Mensaje

El mensaje de bienvenida usa voseo rioplatense ("Describi", "Tenes", "presiona") y es conciso (menos de 15 segundos de lectura) para maximizar el tiempo de grabacion disponible:

> Bienvenido a la mesa de ayuda. Describi tu problema despues del tono. Cuando termines, presiona numeral. Tenes hasta cuarenta y cinco segundos.

El mensaje de despedida confirma el registro y establece expectativa:

> Gracias. Tu incidente fue registrado. Vas a recibir un numero de ticket por correo.

## Diagrama de Secuencia

```
Usuario         Twilio          N8N             FastAPI
  |               |               |                |
  |-- llama ----->|               |                |
  |               |-- GET TwiML ->| (o TwiML Bin)  |
  |<-- bienvenida-|               |                |
  |-- habla ----->|               |                |
  |-- presiona #->|               |                |
  |<-- despedida -|               |                |
  |-- cuelga ---->|               |                |
  |               |-- transcribe   |                |
  |               |-- POST ------>|                |
  |               |  call-summary |                |
  |               |               |-- AI Agent --->|
  |               |               |  + Redis       |
  |               |               |<-- 201 --------|
  |               |               |-- notifica --->|
```
