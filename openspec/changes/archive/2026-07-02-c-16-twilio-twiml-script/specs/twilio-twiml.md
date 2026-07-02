# Especificacion: TwiML Script para Canal Telefonico

## TW-SPEC-01: Archivo TwiML XML

El proyecto debe contener un archivo `twilio/twiml.xml` con marcado TwiML valido segun la especificacion de Twilio Programmable Voice.

### Escenario: El archivo TwiML existe y es XML valido

- **DADO** que el repositorio esta clonado
- **CUANDO** se lee `twilio/twiml.xml`
- **ENTONCES** el archivo existe y comienza con `<?xml version="1.0" encoding="UTF-8"?>`
- **Y** contiene un elemento raiz `<Response>`

### Escenario: El mensaje de bienvenida usa voseo rioplatense

- **DADO** el archivo `twilio/twiml.xml`
- **CUANDO** se inspecciona el primer elemento `<Say>`
- **ENTONCES** contiene al menos una de las palabras: "Describi", "Tenes", "presiona"
- **Y** el texto esta en espanol

### Escenario: La configuracion de grabacion cumple los requisitos de la tesis

- **DADO** el archivo `twilio/twiml.xml`
- **CUANDO** se inspecciona el elemento `<Record>`
- **ENTONCES** `maxLength` es `45`
- **Y** `finishOnKey` es `#`
- **Y** `transcribe` es `true`
- **Y** `playBeep` es `true`

## TW-SPEC-02: Documentacion de Configuracion

El directorio `twilio/` debe contener un `README.md` con instrucciones de configuracion.

### Escenario: El README cubre el flujo completo de setup

- **DADO** el archivo `twilio/README.md`
- **CUANDO** se lee el contenido
- **ENTONCES** incluye instrucciones para crear una cuenta Twilio
- **Y** incluye instrucciones para comprar/configurar un numero virtual
- **Y** incluye al menos 3 opciones para hostear el TwiML
- **Y** menciona las 4 variables de entorno requeridas

### Escenario: El README cubre testing local con ngrok

- **DADO** el archivo `twilio/README.md`
- **CUANDO** se lee el contenido
- **ENTONCES** incluye una seccion sobre como probar localmente con ngrok
- **Y** menciona la configuracion del webhook en la consola Twilio

## TW-SPEC-03: Variables de Entorno

El archivo `.env.example` del backend debe incluir las variables de entorno para Twilio.

### Escenario: Las variables Twilio estan documentadas en .env.example

- **DADO** el archivo `Gestion_Incidentes/.env.example`
- **CUANDO** se lee el contenido
- **ENTONCES** contiene una seccion comentada `# Twilio (canal telefonico) — C-16`
- **Y** contiene las variables: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `TWILIO_WEBHOOK_URL`

### Escenario: Los valores son placeholders seguros

- **DADO** el archivo `Gestion_Incidentes/.env.example`
- **CUANDO** se inspeccionan los valores de las variables Twilio
- **ENTONCES** todos los valores contienen texto placeholder (ej. `your_account_sid_here`)
- **Y** ningun valor es una credencial real
