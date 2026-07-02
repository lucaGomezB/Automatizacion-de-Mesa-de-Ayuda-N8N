# Tareas: C-16 Twilio TwiML Script

## Lista de Tareas

- [x] 1. Crear directorio `twilio/` y archivo `twiml.xml` con marcado TwiML valido
  - Mensaje de bienvenida en espanol rioplatense con voseo
  - Configuracion de `<Record>`: maxLength=45, finishOnKey="#", transcribe=true
  - Mensaje de despedida confirmando registro
  - Placeholder `TU_DOMINIO` en `transcribeCallback` para que el usuario lo reemplace

- [x] 2. Agregar variables de entorno Twilio a `Gestion_Incidentes/.env.example`
  - Seccion comentada `# Twilio (canal telefonico) — C-16`
  - Variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_WEBHOOK_URL
  - Todos los valores son placeholders seguros (sin credenciales reales)

- [x] 3. Crear `twilio/README.md` con instrucciones de configuracion
  - Como crear cuenta Twilio y obtener credenciales
  - Como comprar y configurar un numero virtual
  - Tres opciones de hosting para el TwiML (TwiML Bin, hosting estatico, endpoint N8N)
  - Como probar localmente con ngrok
  - Referencia de las 4 variables de entorno requeridas

- [x] 4. Verificar que el TwiML XML es sintacticamente valido
  - Parsear el XML con Python (`xml.etree.ElementTree`) para confirmar que no tiene errores
  - Verificar que contiene los elementos requeridos: `<Response>`, `<Say>` (x2), `<Record>`

- [x] 5. Guardar decisiones en Engram
  - Registrar la eleccion de voz (Polly.Mia-Neural, es-US) como la mejor aproximacion disponible al espanol rioplatense
  - Registrar la estructura del directorio `twilio/`
  - Registrar que el transcribeCallback usa placeholder `TU_DOMINIO`
