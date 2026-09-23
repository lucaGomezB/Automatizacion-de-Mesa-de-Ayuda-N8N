## Context

Ver `proposal.md — Why`. Restricciones verificadas que moldean el enfoque:

- **No existe número de negocio**: `Incidente` solo tiene el PK `id` (`App/Backend/app/models/incidente.py`). El frontend lo padea a 5 dígitos (`SuccessCard.tsx`) y n8n consume `$json.id`. La tesis menciona un prefijo configurable que NO está implementado.
- **Correo**: el nodo `Correo de confirmacion al usuario` usa `toRecipients: {{ $('Normalizar entrada del incidente').item.json.remitente || '' }}`. El switch `Rutear por canal de origen` (salida correo, rama sin revisión) llega a confirmación; la rama `requiere_revision_humana = true` pasa por `Es correo?` y termina en `Marcar correo como leido` sin confirmación. El `from` de Outlook es típicamente un objeto (`from.emailAddress.address`), no una cadena.
- **Web**: `Confirmacion web al usuario` responde `{incidente_id: $json.id, ...}` en la rama normal; `Respuesta web de cierre` responde `{incidente_id: null, resultado: 'sin_alta'}` y es alcanzable desde la rama de revisión humana (`Requiere revision humana` true → `Es correo?` false → `Es web?` true), donde el incidente SÍ fue creado.
- **Telefonía**: la salida de telefonía de `Rutear por canal de origen` no tiene sucesor. El `<Say>` de cierre (`cost_guard/twiml.py`) es asíncrono respecto del alta y desconoce el número. No existe nodo ni cliente de Twilio Messaging.
- **Número llamante**: el webhook de VOZ recibe `From` (`cost_guard.py:65`); el callback de estado de grabación NO lo provee. `telefonia_ingreso.caller_cifrado` existe y se cifra con `EncryptedText`, pero hoy se puebla desde `callback.caller`, que es nulo.
- **Credenciales y costo**: Twilio (`twilio_account_sid`, `twilio_auth_token`) ya vive en el backend (c-52). La guarda de costo es del backend; el envío del SMS es un proveedor pago dentro de su alcance.
- **Alta de telefonía**: el backend NO crea el incidente de telefonía; lo crea n8n vía `POST /api/v1/incidentes` con `origen_message_id = CallSid`. Por lo tanto el número recién se conoce al crear el incidente; el backend puede correlacionar el `CallSid` con el ingreso persistido.

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

- Garantizar que el usuario final reciba el número de incidente en los tres canales, incluida la revisión humana.
- Enviar el SMS de telefonía al llamante sin depender del callback que no trae `From`.
- Corregir la extracción del remitente de correo y el cierre web de la rama de revisión humana.
- Acotar el costo del SMS con la guarda existente y dejar la base de licitud documentada (Ley 25.326).
- No regresar c-46/c-47/c-52.

**Non-Goals:**

- Twilio Media Streams / agente conversacional (diferido, tesis cap. 10).
- Directorio de empleados y resolución de contactos por sector/rol (change futuro; ver D10). No hay roles hoy.
- Prefijo configurable del número de incidente (diferido; ver Open Question 1).
- Reemplazar el correo del canal correo por SMS. El SMS es exclusivo del canal de telefonía.
- Implementar código en esta fase (propose only).

## Decisions

### D1: Número de incidente = PK `id` (prefijo diferido)

Se usa el PK `id` como número canónico y legible. El backend ya lo retorna en el alta, n8n lo usa en sus notificaciones y el frontend lo padea. Se descarta agregar un número de negocio con secuencia/prefijo ahora: exigiría columna nueva, generación de secuencia, unicidad global, migración y backfill de incidentes existentes, y cambiaría el contrato OpenAPI; el prefijo de la tesis es una preocupación de presentación que puede agregarse después como `numero_mostrado` calculado desde configuración, sin tocar el contrato de notificación si se centraliza el formato. Alternativa considerada: número de negocio con prefijo configurable — descartada por blast radius y por ausencia de requisito implementado. **Open Question 1** para confirmación humana.

### D2: El backend envía el SMS (no n8n)

El SMS lo envía el backend al crear un incidente de telefonía, como tarea fire-and-forget análoga a `notify_n8n`. Razones: (a) el backend ya tiene las credenciales de Twilio (c-52); (b) el `caller` está cifrado en el backend y no hay que ampliar la superficie de PII hacia n8n; (c) la guarda de costo es del backend; (d) el número (`id`) se conoce en la creación. n8n solo debe garantizar que la rama de telefonía dispare el alta con `origen_message_id = CallSid` (ya lo hace). Alternativa considerada: nodo Twilio en n8n — descartada por duplicar credenciales, ampliar la superficie de PII y alejar la reserva de costo del proveedor. La tarea MUST capturar sus excepciones y NO propagarlas al alta.

### D3: Captura del `From` en el webhook de VOZ, persistida por `CallSid`

El único lugar donde Twilio provee `From` es el webhook de voz. Se persiste un registro de ingreso mínimo en ese momento (upsert por `call_sid` en `telefonia_ingreso`: `caller_cifrado`, `transcripcion_estado = pendiente`), de modo que el callback de estado de grabación —que no trae `From`— lo encuentre y lo propague, y el SMS posterior lo resuelva por `CallSid`. Se descarta pasar el número como query string en la `recordingStatusCallback` (PII en URL y logs) y se descarta depender del `caller` del callback (nulo). La operación de upsert MUST preservar la idempotencia existente por `call_sid` y MUST NOT romper la firma `X-Twilio-Signature`.

### D4: Correo — normalizar el `from` y confirmar también en revisión humana

La normalización del canal correo extrae la dirección efectiva admitiendo `from` string y `from.emailAddress.address`, con descarte observable de remitentes inválidos, y la propaga como `remitente`. El nodo `Correo de confirmacion al usuario` se alcanza desde AMBAS ramas del canal correo (normal y revisión humana), con `onError: continueRegularOutput` para no abortar auditoría ni marcado de leído. Se descarta confiar en el ítem corriente posterior al POST (no expone `remitente`).

### D5: Web — separar cierre con alta de cierre sin alta

La rama de revisión humana del web crea el incidente, por lo que su cierre SHALL incluir el `incidente_id`. Las ramas sin incidente (`Entrada valida` falsa, error del POST) SHALL declarar `resultado: 'sin_alta'` sin número. Se implementa una respuesta de cierre para la revisión humana con incidente (o se resuelve el id de forma robusta) y se conserva la guarda `Es web?` que restringe la respuesta al canal web. Se descarta usar un único `Respuesta web de cierre` con `$json.id ?? null` porque mezclaría ramas con y sin incidente.

### D6: Guarda de costo — superficie `twilio_sms`

Se agrega `PROVIDER_TWILIO_SMS = "twilio_sms"` a `cost_guard/constants.py` y `PAID_PROVIDERS`, su costo unitario a `settings.py`/`cost_guard/config.py`/`.env.example`, y la reserva ANTES de invocar al proveedor de mensajería. La clave de rate por origen es el número llamante (reutiliza el límite existente). Default estimado ~USD 0.0079 por SMS a Argentina, configurable y documentado como estimación. Alternativa considerada: reutilizar la superficie `twilio` — descartada: mezclaría admisión de voz con mensajería y perdería la trazabilidad del gasto.

### D7: Consentimiento y minimización (Ley 25.326)

El SMS es transaccional: la persona llamó a la mesa de ayuda y entregó su número; el mensaje solo informa el número de su incidente. No hay marketing, perfilado ni reutilización; el número se mantiene cifrado at-rest y fuera de auditoría. Se adopta una postura sin mecanismo de opt-out en este alcance (mensaje único, disparado por el propio contacto), pero la decisión final es de negocio/legal. **Open Question 2**.

### D8: Idempotencia del SMS

Un incidente genera como máximo un SMS: la tarea se dispara una vez por creación y el vínculo incidente↔ingreso es único. Un `CallSid` repetido no crea un segundo incidente (índice único de `origen_message_id`), por lo que no genera un segundo SMS. Alternativa considerada: registro de envío con estado — sobre-ingeniería para un mensaje; el log estructurado alcanza.

### D9: PII en el SMS y en los logs

El contenido del SMS se limita al número de incidente y una referencia breve. El número llamante no se registra en claro en logs/auditoría; los eventos usan el identificador de llamada o una marca, no el número. El número se almacena cifrado (`EncryptedText`).

### D10: Punto de integración con el futuro directorio de empleados

Este change NO implementa el directorio. El diseño deja explícito que la resolución de contactos hoy es directa (el propio número llamante), de modo que un directorio futuro (email/teléfono/sector/rol) se enchufe como una estrategia de resolución de contacto sin cambiar el contrato de entrega del número. No se crean roles ni tabla de directorio.

### D11: Gobierno (gobernanza)

- El envío de SMS y el manejo del teléfono llamante son **HIGH/CRITICAL**: PII y mensajería saliente paga. No se escribe código en esta fase; la implementación requiere revisión humana antes de activar credenciales reales.
- El cambio al grafo N8N y la doc son MEDIUM.

### D12: Sin cambios en el esquema salvo el caller de voz

No se agregan columnas ni tablas nuevas para el SMS ni para el número de incidente. Únicamente se puebla `telefonia_ingreso.caller_cifrado` antes (D3). Si el upsert del webhook de voz requiere un método de repositorio nuevo, no implica migración.

## Risks / Trade-offs

- **[Doble envío de SMS]** reintentos del POST o de la tarea → Mitigación: idempotencia del alta por `CallSid` + una reserva/envío por incidente; el log permite detectar duplicados.
- **[Número inválido o ausente]** → Mitigación: sin `From` no se envía; validación mínima de formato; se registra la omisión.
- **[Costo del SMS descontrolado]** → Mitigación: superficie `twilio_sms` en la bolsa global + rate por origen + costo configurable (D6).
- **[PII en URL o logs]** → Mitigación: no pasar el número por query string; cifrado at-rest; logs sin número crudo (D3/D9).
- **[Orden de archivado con c-52]** c-52 también modifica `runtime-cost-guard` (agrega `backend_stt`) y está sin archivar → Mitigación: c-52 debe archivarse ANTES que c-53; este delta copia el estado vigente de la main spec y añade las superficies de c-52 y la nueva. Verificar el orden al archivar.
- **[Regresión c-46/c-47/c-52]** editar el mismo grafo N8N → Mitigación: pruebas estructurales de no regresión y no tocar `Sellar ingreso telefonia`, `Restaurar item telefonia` ni `Guard permite?`.
- **[Verificación runtime del SMS]** no hay harness de Twilio en CI → Mitigación: pruebas unitarias con cliente inyectado + verificación en vivo documentada.
- **[Consentimiento]** postura sin opt-out para mensaje único transaccional → Mitigación: Open Question 2 con revisión de negocio/legal.

## Migration Plan

1. (Sin migración de esquema; D12.) Si se agrega método de repositorio, no hay Alembic.
2. Implementar en orden de dependencia: settings/`.env.example` → `cost_guard` (constantes/config) → cliente SMS → servicio de notificación telefónica → enganche en `incidente_service` → persistencia del caller en el webhook de voz → repositorio.
3. Editar `n8n/workflow.json` (D4/D5), reimportar en N8N.
4. Actualizar `docs/n8n-workflow-guide.md` y regenerar `docs/openapi.json` si cambia el contrato web.
5. Verificación en vivo: una llamada de prueba que produzca incidente y SMS; documentar.
6. Rollback: revertir el commit, reimportar el workflow previo y desactivar la credencial SMS. Sin backfill.

## Open Questions

1. **Número de incidente**: ¿se confirma el PK `id` como número canónico, o se requiere un número de negocio con prefijo configurable (tesis)? Recomendación: adoptar el PK `id` y diferir el prefijo. Decisión humana.
2. **Consentimiento y costo (Ley 25.326)**: ¿se confirma la postura transaccional sin opt-out y el tope de gasto del SMS? Recomendación: postura transaccional, sin marketing, con costo unitario conservador. Decisión de negocio/legal.
3. **Formato y longitud del SMS**: definir el texto exacto (por ejemplo `Mesa de Ayuda: su incidente N° <id> fue registrado.`) y si se usa un `MessagingServiceSid` o un número remitente directo.
4. **Número remitente**: definir si el SMS sale de un número Twilio dedicado o de un Messaging Service, y si afecta la configuración de `TWILIO_PHONE_NUMBER` (hoy comentada en `.env.example`).