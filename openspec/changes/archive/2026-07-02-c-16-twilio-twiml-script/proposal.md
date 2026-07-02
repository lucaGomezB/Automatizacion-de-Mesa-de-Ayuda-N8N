# Propuesta: Script TwiML para Twilio Programmable Voice

## Que

Crear el script TwiML XML que Twilio ejecuta cuando un usuario llama al numero virtual de la mesa de ayuda. El script reproduce un mensaje de bienvenida en espanol rioplatense, graba el problema del usuario durante hasta 45 segundos (finalizando con tecla `#`), transcribe la grabacion y envia el resultado a N8N via webhook.

## Por que

El workflow N8N (`Automatizacion_Mesa_de_Ayuda.json`) ya tiene un nodo `twilioTrigger` que escucha eventos `call-summary.complete`. Sin embargo, NO existe ningun script TwiML en el repositorio. Sin el TwiML, Twilio no sabe que hacer cuando contesta una llamada: el canal telefonico esta incompleto.

La tesis (Capitulo 6, Seccion 6.4) describe este flujo completo. Crear el TwiML cierra la brecha entre la documentacion teorica y el sistema implementable.

## Alcance

- Crear archivo `twilio/twiml.xml` con marcado TwiML valido
- Mensaje de bienvenida en espanol rioplatense (voseo, acento argentino)
- Configuracion de grabacion: 45 segundos maximo, finalizacion con `#`, transcripcion automatica
- Documentacion de configuracion en `twilio/README.md`
- Variables de entorno para Twilio en `.env.example`
- No requiere credenciales reales de Twilio (preparacion unicamente)

## No alcance

- No incluye backend API para recibir el webhook de Twilio (eso ya lo maneja N8N)
- No incluye configuracion de la cuenta Twilio (se documenta en el README, no se automatiza)
- No incluye pruebas end-to-end con Twilio real (requiere credenciales)

## Gobernanza

**Nivel: MEDIUM** — modificacion de configuracion e infraestructura documental. No afecta auth, billing ni seguridad. Sin embargo, establece el contrato de integracion con un servicio externo (Twilio), lo que justifica la revision cuidadosa del diseno.
