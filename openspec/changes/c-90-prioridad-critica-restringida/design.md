## Context

Ver `proposal.md` (Why). Estado actual verificado:

- `PrioridadEnum` = `baja | media | alta | critica` (columna con default `media`). El formulario web (`IncidenteForm.tsx`) solo ofrece `baja|media|alta`.
- El backend NO restringe `critica` en `POST /api/v1/incidentes` (`IncidenteCreate`) ni `PATCH /api/v1/incidentes/{id}` (`IncidenteUpdate`).
- Registro canónico: `app/services/role_policy.py` (`PoliticaRol`, `ROLE_POLICY`, `politica_de_rol`). El guard del directorio (`routes/directorio.py`) ya sigue el patrón lista-blanca derivada de un atributo de política y lanza 403 con el envelope `FORBIDDEN`.
- `c-86` (pendiente) modifica RP-001/002/003; por eso este cambio solo AGREGA RP-006.

## Goals / Non-Goals

**Goals:**
- Enforcar server-side la asignación de prioridad `critica` en alta y edición, derivada del registro de política.
- Ofrecer a los roles autorizados (`mesa_de_ayuda` y `administrador_directorio`) la asignación de prioridad (incluida `critica`) en el panel, y renderizar `critica` de forma distinguible.
- No romper la ingesta no interactiva (n8n).

**Non-Goals:**
- No se introduce una capability nueva ni un endpoint nuevo.
- No se toca el formulario de reporte (ya excluye `critica`).
- No se modifica RP-001/002/003 (los cambia `c-86`).

## Decisions

**D1 — Permiso en el registro, no listas de rol.** `PoliticaRol` gana `puede_asignar_prioridad_critica: bool`; `usuario_final=false`, `mesa_de_ayuda=true`, `administrador_directorio=true` (ver OQ-1, RESUELTA). Se expone un helper derivado (p. ej. `roles_con_asignacion_prioridad_critica()` / `puede_asignar_prioridad_critica(rol)`), igual que `roles_con_lectura_directorio`. Alternativa descartada: lista de roles en la ruta (viola RP-002).

**D2 — Enforcement en la capa de rutas (guard), no en el servicio.** Un guard de ruta resuelve el `empleado` por `current_user.id` (igual que `get_alcance_incidentes`), obtiene la política con `politica_de_rol(empleado.rol)` y, si `payload.prioridad == critica` y el atributo es falso, lanza `HTTPException(403)` (envelope `FORBIDDEN`, sin código nuevo). El guard se aplica en `create_incidente` y en `update_incidente`. El servicio permanece puro de autorización (mantiene la disciplina de capas). Alternativa descartada: pasar el rol al servicio (amplía su firma sin necesidad; los guards ya viven en las rutas).

**D3 — Condición de disparo: el payload pide explícitamente `critica`.** En alta, el default es `media`, así que solo un `prioridad=critica` explícito dispara. En edición, solo `payload.prioridad == critica`. Un PATCH que no incluye `prioridad` (o la incluye `baja|media|alta`) se permite aunque el incidente ya esté en `critica` — evita bloquear ediciones legítimas de otros campos. **Resuelve OQ-2.**

**D4 — 403 de autorización (no 422).** La denegación es de permiso, no de formato: 403 con el envelope estándar, consistente con el guard del directorio y con FR-RBAC-005.

**D5 — Interacción con n8n.** n8n se autentica con un login de operador y hoy NUNCA envía `critica` (default `media`), por lo que la ingesta de correo/telefonía queda intacta. Un llamante sin empleado/rol en el registro (incluida una cuenta de servicio) deniega por defecto ante `critica` (403), pero no afecta altas con prioridad no crítica. **Resuelve OQ-3.**

**D6 — Superficie de UI: control editable en el diálogo de detalle.** Se agrega un control de prioridad en `TicketDetailDialog` (o `DetalleIncidente`) habilitado solo cuando el rol tiene el permiso; ante 403 se maneja sin exponer el recurso (FR-RBAC-005). Los badges (`TicketsTable.PrioridadBadge`, `MisIncidentes.PrioridadBadge`, `DetalleIncidente`) mapean `critica` a una variante propia (p. ej. `destructive` intensificado) en vez del fallback actual. `formatearPrioridad` cubre `critica`.

**D7 — Sin migración de base.** El permiso es política/código puro; ninguna columna ni CHECK cambia (R4).

**D8 — OpenAPI.** No cambia la forma del request; si se documenta la nueva respuesta 403 en los endpoints, regenerar `docs/openapi.json` con `python scripts/export_openapi.py` (guardado por `test_openapi_sync.py`).

## Risks / Trade-offs

- [n8n futuro enviando `critica`] → La ingesta no interactiva recibiría 403; se documenta la regla y se recomienda que n8n nunca envíe `critica` (hoy no lo hace).
- [Denegar por defecto a cuenta sin empleado] → Comportamiento correcto de seguridad, pero un operador legítimo sin empleado vinculado no podría asignar `critica`; mitigación: mismo patrón que el resto de guards de política.
- [Clobber de `c-86`] → Mitigado agregando RP-006 en lugar de modificar RP-001/002/003.

## Migration Plan

Sin migración de datos. Despliegue: cambio de código backend + frontend. Rollback: revertir los commits (sin estado persistido que deshacer). Orden sugerido: registro de política → guard de rutas → tests backend → UI de prioridad/badges → tests frontend → regenerar OpenAPI.

## Open Questions

- **OQ-1 (RESUELTA el 2026-10-14):** ¿`administrador_directorio` también puede asignar `critica`? Decisión humana confirmada: SÍ. `puede_asignar_prioridad_critica` es verdadero para `mesa_de_ayuda` y `administrador_directorio`; es falso para `usuario_final` y para el futuro rol `gestion_incidentes` (introducido por el pendiente `c-86`), que NO puede asignar `critica`. El autor había dicho inicialmente "solo mesa_de_ayuda"; el diseño queda ahora en la regla de dos roles.
- OQ-2 (resuelto en D3): "set/keep" se interpreta como payload explícito `critica`.
- OQ-3 (resuelto en D5): n8n no envía `critica`; regla segura = guard por rol con denegación por defecto.
