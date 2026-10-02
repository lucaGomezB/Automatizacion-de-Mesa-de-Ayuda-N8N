## Context

Alcance reducido a correo, web y número canónico de incidente. El alcance de SMS al llamante se movió a `c-67-notificacion-sms-llamante` (dependiente de OQ3 y C-66). Restricciones verificadas que moldean el enfoque:

- **No existe número de negocio**: `Incidente` solo tiene el PK `id` (`App/Backend/app/models/incidente.py`). El frontend lo padea a 5 dígitos (`SuccessCard.tsx`) y n8n consume `$json.id`. La tesis menciona un prefijo configurable que NO está implementado.
- **Correo**: el nodo `Correo de confirmacion al usuario` usa `toRecipients: {{ $('Normalizar entrada del incidente').item.json.remitente || '' }}`. El switch `Rutear por canal de origen` (salida correo, rama sin revisión) llega a confirmación; la rama `requiere_revision_humana = true` pasa por `Es correo?` y termina en `Marcar correo como leido` sin confirmación. El `from` de Outlook es típicamente un objeto (`from.emailAddress.address`), no una cadena.
- **Web**: `Confirmacion web al usuario` responde `{incidente_id: $json.id, ...}` en la rama normal; `Respuesta web de cierre` responde `{incidente_id: null, resultado: 'sin_alta'}` y es alcanzable desde la rama de revisión humana (`Requiere revision humana` true → `Es correo?` false → `Es web?` true), donde el incidente SÍ fue creado.
- **Doc**: `docs/n8n-workflow-guide.md` afirma una confirmación telefónica por TwiML (`<Say>`) que no ocurre.

## Goals / Non-Goals

**Goals:**

- Garantizar que el usuario final reciba el número de incidente en los canales correo y web, incluida la revisión humana.
- Corregir la extracción del remitente de correo y el cierre web de la rama de revisión humana.
- Exponer el número de incidente canónico (`numero_incidente`) derivado del identificador persistido.
- No regresar c-46/c-47/c-52.

**Non-Goals:**

- SMS al llamante y manejo del número llamante (movido a `c-67-notificacion-sms-llamante`).
- Twilio Media Streams / agente conversacional (diferido, tesis cap. 10).
- Directorio de empleados y resolución de contactos por sector/rol (change futuro; ver D10). No hay roles hoy.
- Prefijo configurable del número de incidente (diferido; ver Open Question 1).
- Implementar código en esta fase (propose only).

## Decisions

### D1: Número de incidente = PK `id` (prefijo diferido)

Se usa el PK `id` como número canónico y legible. El backend ya lo retorna en el alta, n8n lo usa en sus notificaciones y el frontend lo padea. Se descarta agregar un número de negocio con secuencia/prefijo ahora: exigiría columna nueva, generación de secuencia, unicidad global, migración y backfill de incidentes existentes, y cambiaría el contrato OpenAPI; el prefijo de la tesis es una preocupación de presentación que puede agregarse después como `numero_mostrado` calculado desde configuración. La derivación se centraliza en `formatear_numero_incidente` y el contrato expone el campo normalizado `numero_incidente` (string). **Open Question 1 (RESUELTA)**.

### D4: Correo — normalizar el `from` y confirmar también en revisión humana

La normalización del canal correo extrae la dirección efectiva admitiendo `from` string y `from.emailAddress.address`, con descarte observable de remitentes inválidos, y la propaga como `remitente`. El nodo `Correo de confirmacion al usuario` se alcanza desde AMBAS ramas del canal correo (normal y revisión humana), con `onError: continueRegularOutput` para no abortar auditoría ni marcado de leído. Se descarta confiar en el ítem corriente posterior al POST (no expone `remitente`).

### D5: Web — separar cierre con alta de cierre sin alta

La rama de revisión humana del web crea el incidente, por lo que su cierre SHALL incluir el `incidente_id`. Las ramas sin incidente (`Entrada valida` falsa, error del POST) SHALL declarar `resultado: 'sin_alta'` sin número. Se implementa una respuesta de cierre para la revisión humana con incidente (o se resuelve el id de forma robusta) y se conserva la guarda `Es web?` que restringe la respuesta al canal web. Se descarta usar un único `Respuesta web de cierre` con `$json.id ?? null` porque mezclaría ramas con y sin incidente.

### D10: Punto de integración con el futuro directorio de empleados

Este change NO implementa el directorio. El diseño deja explícito que un directorio futuro (email/teléfono/sector/rol) se enchufe como una estrategia de resolución de contacto sin cambiar el contrato de entrega del número.

### D11: Gobierno (gobernanza)

- El cambio al grafo N8N y la doc son MEDIUM.
- El envío de SMS y el manejo del teléfono llamante son ALTO (PII y mensajería saliente paga) y pertenecen a `c-67-notificacion-sms-llamante`.

## Risks / Trade-offs

- **[Regresión c-46/c-47/c-52]** editar el mismo grafo N8N → Mitigación: pruebas estructurales de no regresión y no tocar `Sellar ingreso telefonia`, `Restaurar item telefonia` ni `Guard permite?`.

## Migration Plan

1. Editar `n8n/workflow.json` (D4/D5), reimportar en N8N.
2. Actualizar `docs/n8n-workflow-guide.md` y regenerar `docs/openapi.json` por el campo `numero_incidente`.
3. Rollback: revertir el commit y reimportar el workflow previo. Sin backfill.

## Open Questions

### OQ1 — Número de incidente (RESUELTO)

Se adopta el PK `id` como número canónico de incidente. La derivación se centraliza en un único punto (`formatear_numero_incidente(id) -> str`), de modo que el prefijo de negocio (`INC-{id:06d}`) pueda agregarse en el futuro con un cambio en un solo lugar. Todos los contratos exponen el campo normalizado `numero_incidente` (string). El prefijo configurable queda diferido. Las Open Questions del SMS (OQ2, OQ3, OQ4) se movieron a `c-67-notificacion-sms-llamante`.
