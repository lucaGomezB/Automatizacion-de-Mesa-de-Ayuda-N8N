## Context

Alcance de SMS al llamante, separado de `c-53-notificacion-numero-incidente` (que ya entregó correo, web y número canónico). Restricciones verificadas que moldean el enfoque:

- **Telefonía**: la salida de telefonía de `Rutear por canal de origen` no tiene sucesor. El `<Say>` de cierre (`cost_guard/twiml.py`) es asíncrono respecto del alta y desconoce el número. No existe nodo ni cliente de Twilio Messaging.
- **Número llamante**: el webhook de VOZ recibe `From` (`cost_guard.py:65`); el callback de estado de grabación NO lo provee. `telefonia_ingreso.caller_cifrado` existe y se cifra con `EncryptedText`, pero hoy se puebla desde `callback.caller`, que es nulo.
- **Credenciales y costo**: Twilio (`twilio_account_sid`, `twilio_auth_token`) ya vive en el backend (c-52). La guarda de costo es del backend; el envío del SMS es un proveedor pago dentro de su alcance.
- **Alta de telefonía**: el backend NO crea el incidente de telefonía; lo crea n8n vía `POST /api/v1/incidentes` con `origen_message_id = CallSid`. Por lo tanto el número recién se conoce al crear el incidente; el backend puede correlacionar el `CallSid` con el ingreso persistido.
- **Número de incidente**: lo provee `c-53` (PK `id` como número canónico). `c-67` consume ese número; no lo redefine.

### Flujo objetivo del SMS (telefonía)

```
Twilio VOICE webhook  ──> backend persiste {call_sid, caller_cifrado}   (D3)
Twilio recording cbo  ──> backend STT + pseudonimiza + handoff n8n      (c-52)
n8n clasifica         ──> POST /incidentes (origen_message_id=CallSid)  (c-52)
backend crea incidente ──> tarea fire-and-forget:                      (D2)
        resuelve ingreso por CallSid ──> caller_cifrado
        reserva guarda twilio_sms (D6)
        envía SMS con incidente.id
        (sin caller o guarda denegada => log, sin SMS)
```

## Goals / Non-Goals

**Goals:**

- Enviar el SMS de telefonía al llamante sin depender del callback que no trae `From`.
- Acotar el costo del SMS con la guarda existente.
- Consumir el marco de licitud/minimización y transferencia internacional provisto por `C-66`, sin redefinirlo.

**Non-Goals:**

- Twilio Media Streams / agente conversacional (diferido, tesis cap. 10).
- Directorio de empleados y resolución de contactos por sector/rol (change futuro; ver D10).
- Número de incidente canónico y prefijo configurable (propiedad de `c-53`).
- Redefinir el marco de consentimiento/transferencia internacional (propiedad de `C-66`).
- Habilitar el envío real hasta cerrar OQ3 (entregabilidad AR +54).

## Decisions

### D2: El backend envía el SMS (no n8n)

El SMS lo envía el backend al crear un incidente de telefonía, como tarea fire-and-forget análoga a `notify_n8n`. Razones: (a) el backend ya tiene las credenciales de Twilio (c-52); (b) el `caller` está cifrado en el backend y no hay que ampliar la superficie de PII hacia n8n; (c) la guarda de costo es del backend; (d) el número (`id`) se conoce en la creación. n8n solo debe garantizar que la rama de telefonía dispare el alta con `origen_message_id = CallSid` (ya lo hace). Alternativa considerada: nodo Twilio en n8n — descartada por duplicar credenciales, ampliar la superficie de PII y alejar la reserva de costo del proveedor. La tarea MUST capturar sus excepciones y NO propagarlas al alta.

### D3: Captura del `From` en el webhook de VOZ, persistida por `CallSid`

El único lugar donde Twilio provee `From` es el webhook de voz. Se persiste un registro de ingreso mínimo en ese momento (upsert por `call_sid` en `telefonia_ingreso`: `caller_cifrado`, `transcripcion_estado = pendiente`), de modo que el callback de estado de grabación —que no trae `From`— lo encuentre y lo propague, y el SMS posterior lo resuelva por `CallSid`. Se descarta pasar el número como query string en la `recordingStatusCallback` (PII en URL y logs) y se descarta depender del `caller` del callback (nulo). La operación de upsert MUST preservar la idempotencia existente por `call_sid` y MUST NOT romper la firma `X-Twilio-Signature`. El manejo del número llamante (base de licitud, minimización, transferencia) es propiedad de `C-66`; aquí solo se persiste lo mínimo para notificar.

### D6: Guarda de costo — superficie `twilio_sms`

Se agrega `PROVIDER_TWILIO_SMS = "twilio_sms"` a `cost_guard/constants.py` y `PAID_PROVIDERS`, su costo unitario a `settings.py`/`cost_guard/config.py`/`.env.example`, y la reserva ANTES de invocar al proveedor de mensajería. La clave de rate por origen es el número llamante (reutiliza el límite existente). Default estimado ~USD 0.0079 por SMS a Argentina, configurable y documentado como estimación. Alternativa considerada: reutilizar la superficie `twilio` — descartada: mezclaría admisión de voz con mensajería y perdería la trazabilidad del gasto.

### D7: Consentimiento, minimización y transferencia internacional (marco de `C-66`)

El SMS es transaccional: la persona llamó a la mesa de ayuda y entregó su número; el mensaje solo informa el número de su incidente. No hay marketing, perfilado ni reutilización; el número se mantiene cifrado at-rest y fuera de auditoría. La **base de licitud** (Ley 25.326), la **minimización** y el **instrumento de transferencia internacional** de datos hacia el proveedor de mensajería los define/provee el change `C-66` (privacidad-transferencias). `c-67` CONSUME ese marco y MUST NOT redefinirlo. Dado que Estados Unidos NO es un país con nivel adecuado de protección, la transferencia al proveedor de SMS (Twilio, EE. UU.) requiere el instrumento que provea `C-66`; el envío queda condicionado a su vigencia. La postura sin mecanismo de opt-out (mensaje único, disparado por el propio contacto) se adopta como postura de negocio; su validación legal es responsabilidad de `C-66`.

### D8: Idempotencia del SMS

Un incidente genera como máximo un SMS: la tarea se dispara una vez por creación y el vínculo incidente↔ingreso es único. Un `CallSid` repetido no crea un segundo incidente (índice único de `origen_message_id`), por lo que no genera un segundo SMS. Alternativa considerada: registro de envío con estado — sobre-ingeniería para un mensaje; el log estructurado alcanza.

### D9: PII en el SMS y en los logs

El contenido del SMS se limita al número de incidente y una referencia breve. El número llamante no se registra en claro en logs/auditoría; los eventos usan el identificador de llamada o una marca, no el número. El número se almacena cifrado (`EncryptedText`).

### D10: Punto de integración con el futuro directorio de empleados

Este change NO implementa el directorio. El diseño deja explícito que la resolución de contactos hoy es directa (el propio número llamante), de modo que un directorio futuro (email/teléfono/sector/rol) se enchufe como una estrategia de resolución de contacto sin cambiar el contrato de entrega del número.

### D11: Gobierno (gobernanza)

- El envío de SMS y el manejo del teléfono llamante son **ALTO (HIGH/CRITICAL)**: PII, transferencia internacional y mensajería saliente paga. No se habilita credencial real hasta cerrar OQ3 y contar con el instrumento de `C-66`; la implementación requiere revisión humana.

### D12: Sin cambios en el esquema salvo el caller de voz

No se agregan columnas ni tablas nuevas para el SMS. Únicamente se puebla `telefonia_ingreso.caller_cifrado` antes (D3). Si el upsert del webhook de voz requiere un método de repositorio nuevo, no implica migración.

## Risks / Trade-offs

- **[No entregable a +54 (OQ3)]** → Mitigación: bloqueo explícito; no se habilita el envío hasta cerrar el spike.
- **[Transferencia internacional sin instrumento]** → Mitigación: dependencia declarada de `C-66`; sin instrumento vigente no se habilita la credencial real (D7).
- **[Doble envío de SMS]** reintentos del POST o de la tarea → Mitigación: idempotencia del alta por `CallSid` + una reserva/envío por incidente; el log permite detectar duplicados.
- **[Número inválido o ausente]** → Mitigación: sin `From` no se envía; validación mínima de formato; se registra la omisión.
- **[Costo del SMS descontrolado]** → Mitigación: superficie `twilio_sms` en la bolsa global + rate por origen + costo configurable (D6).
- **[PII en URL o logs]** → Mitigación: no pasar el número por query string; cifrado at-rest; logs sin número crudo (D3/D9).
- **[Orden de archivado con c-52]** c-52 también modifica `runtime-cost-guard` (agrega `backend_stt`) y está sin archivar → Mitigación: c-52 debe archivarse ANTES que c-67; este delta copia el estado vigente de la main spec y añade las superficies de c-52 y la nueva. Verificar el orden al archivar.
- **[Verificación runtime del SMS]** no hay harness de Twilio en CI → Mitigación: pruebas unitarias con cliente inyectado + verificación en vivo documentada.

## Migration Plan

1. (Sin migración de esquema; D12.) Si se agrega método de repositorio, no hay Alembic.
2. Implementar en orden de dependencia: settings/`.env.example` → `cost_guard` (constantes/config) → cliente SMS → servicio de notificación telefónica → enganche en `incidente_service` → persistencia del caller en el webhook de voz → repositorio.
3. Verificación en vivo: una llamada de prueba que produzca incidente y SMS; documentar.
4. Rollback: revertir el commit y desactivar la credencial SMS. Sin backfill.

## Open Questions

### OQ3 — Entregabilidad del SMS a Argentina (ABIERTA)

La entregabilidad de Twilio SMS a números argentinos (+54) está bajo un spike externo en curso. El envío de SMS (cliente de Twilio Messaging, superficie `twilio_sms`, captura del llamante específica para SMS y variables de entorno asociadas) queda BLOQUEADO hasta que el spike devuelva resultado. El formato y la longitud exactos del mensaje se fijan al habilitar el envío.

### OQ2 — Consentimiento y costo del SMS (RESUELTO, sujeto a C-66)

El SMS es transaccional: la persona contactó a la mesa de ayuda y proporcionó su número; el contenido es mínimo (número de incidente y referencia breve), sin PII del incidente. La base de licitud (Ley 25.326) y el instrumento de transferencia internacional son provistos por `C-66`; el tope de gasto se aplica con la superficie `twilio_sms` de la guarda de costo.

### OQ4 — Número remitente del SMS (RESUELTO)

El remitente es el `TWILIO_PHONE_NUMBER` existente (o un Messaging Service). No se agrega una variable nueva de remitente. Aplicable al habilitar el SMS (bloqueado por OQ3).

### C-66 — Marco de privacidad (PENDIENTE)

`C-66` (privacidad-transferencias) es dueño del manejo del número llamante y del marco de consentimiento/lawful-basis/transferencia internacional. `c-67` lo consume y MUST NOT redefinirlo. Estados Unidos NO es un país con nivel adecuado de protección; la transferencia requiere el instrumento de `C-66`.
