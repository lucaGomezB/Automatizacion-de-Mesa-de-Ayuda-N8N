# Design — c-162: Propagar el contacto del reportante en el flujo N8N

## Context

Ver `proposal.md` — Why. El defecto es de transporte, no de capacidad: el backend ya resuelve reportante.

Estado relevante verificado:

- `n8n/workflow.json`, nodo `Normalizar entrada del incidente` (`n8n-nodes-base.code`, typeVersion 2): ya computa `remitente` normalizado para correo (`normalizarRemitente`) y la telefonía ya propaga `caller_number` desde `Sellar ingreso telefonia`. Hoy NO emite un campo de contacto para el POST.
- `HTTP POST a MESA-AYUDAS` (`n8n-nodes-base.httpRequest`, typeVersion 4.4): `jsonBody` = `={{ JSON.stringify({ descripcion, prioridad, canal_origen_id, origen_message_id, origen_evento: 'creacion_incidente', ingresado_en }) }}`; header `Authorization: Bearer {{ $('Login operador').item.json.access_token }}` (auth = cuenta de operador).
- Backend `App/Backend/app/routes/incidentes.py` `resolver_reportante`: telefonía -> `resolver_por_telefono(payload.reportante_telefono)`; correo -> `resolver_por_email(payload.reportante_email)`; web/unknown -> `resolver_por_usuario(current_user.id)`. Si no resuelve, `requiere_revision_humana = true` (VIS-005, c-82).
- `App/Backend/app/schemas/incidente.py` ya acepta `reportante_email`/`reportante_telefono`; `App/Backend/app/models/incidente.py` solo persiste `reportante_empleado_id`. Enviar el contacto es transitorio y privacy-safe.

## Goals / Non-Goals

**Goals:**

- Que un incidente de correo/telefonía de un empleado del directorio resuelva reportante y NO derive por VIS-005.
- Preservar la garantía de no persistir el contacto crudo ni escribirlo en auditoría.
- Dejar el contrato verificable por tests estructurales offline (sin runtime N8N).

**Non-Goals:**

- No tocar el resolver ni el schema (`App/Backend/app/**`): ya soportan el contrato.
- No agregar contacto al canal web (ver Decisión 3).
- No publicar la release v1.2.6: solo se deja la nota; la publica el orquestador.
- No cambiar strings canónicos, umbrales ni números canónicos.

## Decisions

### Decisión 1 — El contacto viaja como campos dedicados `reportante_email` / `reportante_telefono`, no como `remitente`

El normalizador emite dos campos nuevos, acotados por canal: `reportante_email` (correo, desde `remitenteNorm.remitente`) y `reportante_telefono` (telefonía, desde `caller_number`); `null` en el resto. El POST los agrega al `jsonBody` con `|| null`.

- **Por qué:** son los nombres del contrato `IncidenteCreate`; reutilizarlos evita cualquier mapeo en el backend y respeta la acotación de capas.
- **Por qué NO enviar `remitente` directamente:** `remitente` es el campo interno para la confirmación por correo (N8N-EMAIL-002) y su nombre no coincide con el contrato del backend; además mantiene clara la separación "contacto para confirmación" vs "contacto para resolución".
- **Alternativa considerada:** reusar `remitente` en el POST. Descartada: rompe el contrato y confunde resolución con notificación.

### Decisión 2 — null-safe y transient (sin persistencia cruda)

Cada campo es `... || null`. El backend resuelve y guarda solo `reportante_empleado_id`; el contacto no se persiste ni se audita.

- **Por qué:** minimiza el dato y mantiene la evidencia de la tesis (RES-006, no PII en claro en trazas).
- **Garantía verificable:** el test que niega el campo crudo `remitente` en body/auditoría permanece en verde (el nombre nuevo no contiene la subcadena `remitente`).

### Decisión 3 — El canal web queda FUERA de alcance (declarado)

Por N8N, la autenticación del POST es la cuenta de operador (`Login operador`), de modo que `resolver_por_usuario(current_user.id)` resolvería al OPERADOR, no al usuario final: mis-atribución. Manejar web con un email en el formulario cambiaría el contrato del formulario y del frontend, fuera del objetivo de c-162.

- **Decisión:** web no envía `reportante_email` ni `reportante_telefono`; se declara explícitamente fuera de alcance en la spec (N8N-CONTACT-001).
- **Alternativa considerada:** incluir `usuario` del formulario. Descartada por alcance y por la mis-atribución de la cuenta de servicio.

### Decisión 4 — Modificar N8N-EMAIL-002 en lugar de crear un requisito que la contradiga

N8N-EMAIL-002 afirma que el `remitente` MUST NOT agregarse al POST. c-162 supersede esa parte: el contacto SÍ viaja al POST (como `reportante_email`). Se MODIFICA el requisito acotando el MUST NOT a la persistencia/auditoría del campo crudo.

- **Por qué:** un ADDED que contradiga un requisito vigente deja la spec inconsistente; MODIFIED es el mecanismo correcto para cambiar semántica.
- **Nota de artefacto:** el comentario C-40/C-53 del normalizador ("NO se agrega al POST ni a la auditoria") se reescribe en el mismo sentido.

### Decisión 5 — Supersede parcial de C-40/C-53 registrado en el dictamen

Se registra en `docs/Tesis/Correcciones/dictamen-correcciones.md` el cierre de OQ5 y el supersede parcial de C-40/C-53, y se agrega/annotiza una fila en `tab:configuracion-evaluada-entregada` (Anexo B) declarando la propagación de contacto como capacidad de la versión entregada posterior a la campaña.

## Risks / Trade-offs

- **Confusión "enviar" vs "persistir" el contacto** -> el modelo solo guarda `reportante_empleado_id`; test de no contaminación en verde; spec RES-006 intacta.
- **Regresión del `jsonBody`** (JSON.stringify con un campo mal formado) -> test estructural que parsea el `jsonBody` via `http_json_body`; mantener el formato de expresión única `={{ JSON.stringify({...}) }}`.
- **Deriva documental** (guía N8N y tesis desalineadas) -> tareas de docs incluidas y verificables con grep.
- **`test_c135_n8n_retry_policy.py`** afirma `origen_message_id` y la referencia al normalizador; agregar campos no lo rompe. Se revisa y, si su contrato lo permite, se extiende; no se debilita.

## Migration Plan

1. Editar `n8n/workflow.json` (normalizador + `jsonBody` + comentario).
2. Actualizar/extends tests estructurales y correr el subset offline.
3. Actualizar docs y tesis (guía N8N, anexos, dictamen).
4. Dejar la nota de release v1.2.6 en el registro del dictamen (NO publicar).
5. Verificación: `openspec validate c-162-... --strict`; `pytest -m "not integration"`.

**Rollback:** revertir el commit restaura el `jsonBody` previo y el comentario; sin migraciones ni cambios de datos.

## Open Questions

- **OQ-A (resuelta):** ¿maneja c-162 el canal web? NO. Se acota fuera y se declara (Decisión 3). Motivo: mis-atribución por la cuenta de operador; requiere cambio de contrato del formulario, fuera de alcance.
- **OQ-B (diferible):** ¿necesita actualización `test_c135_n8n_retry_policy.py`? No por obligación; se revisa en tareas y se extiende solo si aporta valor sin debilitar su aserción de idempotencia. No cambia specs ni tareas.
