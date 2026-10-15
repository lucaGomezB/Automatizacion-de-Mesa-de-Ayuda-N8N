## Context

Ver `proposal.md` — Why y `specs/` para los requisitos. Estado actual relevante:

- Roles: `RolEmpleado` (tres valores) en `app/models/empleado.py`; CHECK `ck_directorio_empleado_rol` de tres valores; registro unico `ROLE_POLICY`/`PoliticaRol`/`ModoAlcance` (PROPIO/GLOBAL/VACIO) en `app/services/role_policy.py`.
- Visibilidad: `AlcanceIncidentes` + `alcance_desde_empleado` + `permite_incidente` en `app/services/incident_visibility.py`; el filtrado vive en `IncidenteRepository.list_filtered` y en `ClasificacionService._verificar_alcance_incidente`.
- Sectores del incidente: `Incidente.sector_id` (principal) + tabla `incidente_sector_adicional` (`app/models/asociaciones.py`); el conjunto es `{sector_id} U adicionales`.
- Estados: catalogo `Estado` con `nuevo | en proceso | en espera | resuelto | cerrado`; `cerrado` es el unico terminal (`es_terminal=True`).
- Notificaciones: `NotificationRecipientService` resuelve `mesa_de_ayuda` activos (in-process) para la revision; `notify_n8n` emite fire-and-forget; N8N entrega.
- Validacion: `ClasificacionService.validate` propaga el veredicto al incidente (`update_fields(sector_id, requiere_revision_humana=False)`) sin registrar actor.
- Panel: `Administracion/index.tsx` con `TabActiva = 'tickets' | 'revision'`; filas de detalle; accion "Validar" en revision.
- Restricciones: capas `routes -> services -> repositories -> models`; SQLAlchemy 2.0 async con `selectinload` para relaciones serializadas; migraciones Alembic (ultima 017); dominios/identificadores en espanol; sin emojis; TDD estricto.

## Goals / Non-Goals

**Goals:**

- Introducir el cuarto rol `gestion_incidentes` y el alcance `SECTOR` reutilizando el registro unico de politica (sin duplicar mapas rol -> atributo).
- Modelar el cierre por sector, el cierre global, la transicion terminal, la reapertura y la edicion de estado, con atribucion de actor durable.
- Log de comentarios append-only con formato uniforme.
- Historial de cerrados con visibilidad por rol y pestaña en el panel.
- Aviso post-revision a `gestion_incidentes` de los sectores, por el mecanismo N8N existente.

**Non-Goals:**

- No se cambia la clasificacion, el pipeline hibrido ni el contrato multietiqueta (ASG).
- No se introduce borrado logico de incidentes; el historial excluye los eliminados por construccion (hoy el borrado es fisico, `hard_delete`).
- No se cambia la notificacion de revision a `mesa_de_ayuda` (NR-002 se mantiene).
- No se agrega MFA ni privilegio a `gestion_incidentes`.
- No se rediseña el panel de tickets existente mas alla de sumar la pestaña, las acciones de ciclo y los comentarios.

## Decisions

### D1 — Rol, modo SECTOR y atributos de ciclo en el registro de politica

**Decision:** agregar `RolEmpleado.gestion_incidentes`; agregar `ModoAlcance.SECTOR`; extender `PoliticaRol` con `post_review_recipient`, `edita_estado`, `cierra_sector`, `cierra_global` y `reabre`. Entradas: `gestion_incidentes` (`requires_sector=True`, `visibilidad=SECTOR`, no privilegiado, sin directorio, `post_review_recipient=True`, `edita_estado=True`, `cierra_sector=True`); `mesa_de_ayuda` (`edita_estado=True`, `cierra_global=True`, `reabre=True`); resto en falso.

**Por que:** el proyecto exige una unica fuente de verdad del conocimiento de rol (RP-002); los guards derivan de `ROLE_POLICY`, no de listas de strings. Todos los permisos de ciclo quedan declarativos y testeables por coherencia (RP-003).

**Alternativas:** (a) listas de roles en los guards — rechazada por duplicacion y por romper RP-002/RP-003; (b) derivar `cierra_sector` de `visibilidad=SECTOR` — rechazada por acoplar dos conceptos distintos (alcance vs permiso de mutacion).

### D2 — Derivacion del alcance SECTOR

**Decision:** `AlcanceIncidentes` incorpora `sector_id: int | None`. `alcance_desde_empleado` devuelve `AlcanceIncidentes(ModoAlcance.SECTOR, sector_id=empleado.sector_id)` cuando la politica es SECTOR; si `empleado.sector_id` es `None` (rol que requiere sector pero sin sector) devuelve VACIO. `permite_incidente` para SECTOR verifica pertenencia al conjunto de sectores y no-cierre.

**Por que:** reutiliza la derivacion rol -> alcance existente y mantiene el modelo de modos. El protocolo `IncidenteVisible` se amplia para exponer el conjunto de sectores (`sector_id` + ids de `sectores_adicionales`) y los sectores ya cerrados, de modo que la verificacion puntual no haga queries ocultas.

**Alternativas:** verificar SECTOR solo en el repositorio — rechazada porque la verificacion puntual de `ClasificacionService` tambien necesita la regla.

### D3 — Filtrado SQL del alcance SECTOR

**Decision:** vista activa para el sector S:

```
(incidente.sector_id = S
 OR incidente.id IN (SELECT incidente_id FROM incidente_sector_adicional WHERE sector_id = S))
AND incidente.estado_id != <id de 'cerrado'>
AND NOT EXISTS (SELECT 1 FROM incidente_cierre_sector c
                WHERE c.incidente_id = incidente.id AND c.sector_id = S)
```

La transicion terminal usa: `COUNT(DISTINCT c.sector_id) de incidente_cierre_sector del incidente == tamano del conjunto {sector_id} U adicionales`. El id de `cerrado` se resuelve una vez por `estado.es_terminal` (no por nombre hardcodeado donde sea evitable).

**Por que:** expresa exactamente "pertenece al conjunto y no cerrado para el sector" con integridad referencial, sin arrays ni JSONB. Es server-side y reutilizable por listado, acceso puntual e historial.

**Alternativas:** filtrar en el cliente — prohibido (VIS-007); precalcular un booleano `cerrado_para_sector` en el incidente — rechazado por denormalizacion y por no soportar N sectores.

### D4 — Modelo de cierre y transicion terminal

**Decision:** tabla `incidente_cierre_sector` (`incidente_id`, `sector_id`, `cerrado_por` nullable FK a `directorio_empleado` ON DELETE SET NULL, `cerrado_en` timestamptz), PK compuesta `(incidente_id, sector_id)`, FK incidente CASCADE, sector RESTRICT. `POST /{id}/cierre-sector` (gestion) inserta/upserta el cierre de su sector; `POST /{id}/cierre-global` (mesa de ayuda) inserta los cierres de TODOS los sectores del conjunto y fija `estado=cerrado`. Cerrar por sector verifica, tras insertar, si todos los sectores cerraron y, en tal caso, fija `estado=cerrado` (terminal).

**Por que:** el cierre por sector necesita su propia fila para la vista activa y el historial inmediato por sector; la PK compuesta da idempotencia natural. Un incidente sin sectores solo puede cerrarse globalmente.

**Alternativas:** reutilizar `estado` por sector — imposible, el estado es unico por incidente.

### D5 — Reapertura (rehabilitar)

**Decision:** `POST /{id}/rehabilitar` exclusiva de `mesa_de_ayuda` (politica `reabre=True`). Borra las filas de `incidente_cierre_sector` del incidente, fija `estado=en proceso` de forma deterministica y registra un `incidente_evento` tipo `reapertura` con `estado_anterior='cerrado'` y `estado_nuevo='en proceso'`. Rechaza la reapertura de un incidente que no esta cerrado.

**Por que:** limpiar los cierres devuelve el incidente a la vista activa normal por sus reglas; `en proceso` es determinista y evita tener que persistir el estado previo al cierre. La auditoria en `incidente_evento` conserva quien y cuando, aunque los cierres se borren.

**Alternativas:** (a) conservar los cierres y marcarlos reabiertos — complica la condicion "todos cerrados" y la vista activa; (b) restaurar el estado previo — requiere persistir el estado pre-cierre en cada transicion; se descarta por simplicidad y por ser un dato reconstruible de la auditoria.

### D6 — Edicion de estado

**Decision:** `PATCH /{id}/estado` con cuerpo `{ "estado": "en proceso" | "en espera" | "resuelto" }`. Autorizado cuando la politica del actor tiene `edita_estado=True` y el incidente esta dentro de su alcance (gestion: su sector; mesa de ayuda: cualquiera). `cerrado` en el cuerpo produce error de validacion (422). Registra `incidente_evento` tipo `cambio_estado`.

**Por que:** separa la edicion de estado del cierre; `cerrado` solo se alcanza por el modelo de cierre (ILC-003). No colisiona con el `PATCH /incidentes/{id}` existente al ser un subrecurso distinto.

**Alternativas:** extender el `PATCH /incidentes/{id}` existente — rechazada porque ese endpoint tiene otro proposito y su contrato esta asentado.

### D7 — Comentarios append-only

**Decision:** tabla `incidente_comentario` (`id`, `incidente_id` FK CASCADE, `autor_empleado_id` nullable FK SET NULL, `texto` text, `created_at` timestamptz). Endpoints `POST`/`GET /api/v1/incidentes/{id}/comentarios`, permissionados por `AlcanceIncidentes` (misma regla que la lectura). Sin endpoints de edicion/borrado. El backend devuelve `created_at` en UTC; el render formatea `HH:MM:SS DD/MM/AAAA` en `America/Argentina/Buenos_Aires` reutilizando `app/utils/business_time.py`.

**Por que:** append-only sin numeracion; el formato exacto y el separador `----------` son de presentacion. Reutilizar `business_time` evita depender de la zona del servidor.

**Alternativas:** reutilizar `clasificacion_log` — rechazada: mezcla auditoria del clasificador con comentarios de usuario.

### D8 — Auditoria de ciclo de vida

**Decision:** tabla `incidente_evento` (`id`, `incidente_id` FK CASCADE, `tipo` varchar, `actor_empleado_id` nullable FK SET NULL, `sector_id` nullable FK SET NULL, `estado_anterior` nullable, `estado_nuevo` nullable, `created_at` timestamptz). Tipos: `cierre_sector`, `cierre_global`, `reapertura`, `cambio_estado`. Se escribe en los servicios de ciclo.

**Por que:** es el unico registro durable del actor cuando los cierres se borran en la reapertura (D5); cubre la atribucion exigida (ILC-006). ON DELETE SET NULL preserva el evento ante el borrado ARCO del empleado, sin PII.

**Alternativas:** campos de auditoria en `incidente` — insuficientes: solo guardan el ultimo cambio y no los cierres por sector.

### D9 — Aviso post-revision (disparador y payload)

**Decision:** al finalizar con exito `ClasificacionService.validate` (tras `update_fields(requiere_revision_humana=False)`), resolver los `gestion_incidentes` ACTIVOS cuyo sector pertenece al conjunto validado (principal + adicionales). Nuevo metodo `NotificationRecipientService.resolver_destinatarios_gestion(sector_ids)` apoyado en `EmpleadoRepository.listar_activos_por_rol_y_sectores(rol, sector_ids)`. Nueva funcion fire-and-forget `notify_n8n_post_revision(incidenteId, sectores, destinatarios)` en `app/utils/n8n_webhook.py` (mismo URL/secret), con payload `{ incidente_id, sectores, destinatarios_gestion: [...], evento: "incidente_validado_gestion" }`. Degradacion a lista vacia; sin PII en logs; no bloquea la validacion.

**Por que:** el punto natural de "paso la revision" es la validacion; resolver por el conjunto validado evita notificar sectores que ya no aplican. Mantiene el patron fire-and-forget y de respaldo de N8N.

**Alternativas:** notificar en la alta por correo/N8N — rechazada: aun no paso la revision humana.

### D10 — Visibilidad del historial de cerrados

**Decision:** `GET /api/v1/incidentes/historial-cerrados`, declarado ANTES de `GET /{id}` para evitar el conflicto de path. Filtro por alcance: GLOBAL -> incidentes con estado `cerrado`; SECTOR -> incidentes con fila en `incidente_cierre_sector` para el sector del usuario; PROPIO -> incidentes `cerrado` del propio reportante. Excluye incidentes eliminados (hoy ausentes por borrado fisico). El estado mostrado en la vista es "Cerrado".

**Por que:** separa "cerrado para mi sector" (inmediato) de "cerrado globalmente", y respeta PROPIO/GLOBAL/SECTOR sin duplicar la derivacion de alcance.

**Alternativas:** reutilizar el listado activo con un filtro `estado=cerrado` — no expresa el cierre por sector aun no global.

### D11 — Cableado del panel

**Decision:** `TabActiva` pasa a `'tickets' | 'revision' | 'historial'`. Nuevo `HistorialTable` consume `useHistorialCerrados`. Las acciones de ciclo (cerrar por sector / cerrar global / reabrir / editar estado) y los comentarios viven en el detalle del incidente con permisos derivados del alcance y el rol expuestos por el backend. El guard y la navegacion admiten `SECTOR` (FR-RBAC-002/003).

**Por que:** reutiliza el patron de pestanas y tablas existente; el detalle conserva el contexto. La UI nunca amplia el alcance.

### D12 — Migracion 018

**Decision:** `018_gestion_incidentes_ciclo_cierre.py`: (1) `DROP`/`CREATE` del CHECK `ck_directorio_empleado_rol` a cuatro valores (ampliacion aditiva, sin backfill de datos); (2) crear `incidente_cierre_sector`, `incidente_evento`, `incidente_comentario` con sus FKs e indices (`sector_id` del cierre, `incidente_id` de evento y comentario). `downgrade`: `UPDATE` filas `gestion_incidentes -> usuario_final` ANTES de restaurar el CHECK de tres valores; luego `DROP` de las tres tablas.

**Por que:** la base no lee el registro de politica (RP-002), asi que el CHECK debe enumerar el cuarto valor. Ampliar un CHECK es seguro. El downgrade no puede dejar filas que violen el CHECK restaurado, por eso reasigna antes.

**Alternativas:** una tabla de catalogo de roles — rechazada por sobre-ingenieria y por desviarse del patron existente.

## Risks / Trade-offs

- [El CHECK, el enum y el registro divergen] -> Test de coherencia RP-003 extendido a cuatro valores y a `requires_sector`/SECTOR; migracion revisada contra el enum.
- [El filtro SECTOR filtra de menos y expone otro sector] -> Filtro server-side unico reutilizado por listado, acceso puntual e historial; tests por rol y escenarios VIS-001/VIS-007.
- [Cierre parcial confundido con cerrado global] -> `cerrado` solo por transicion terminal o cierre global; tests ILC-001/002/003; la vista de historial normaliza el estado mostrado.
- [Reapertura pierde el estado previo] -> `incidente_evento` conserva estado anterior y nuevo; reapertura determinista a `en proceso` (D5).
- [Migracion con datos `gestion_incidentes` en downgrade] -> Reasignacion a `usuario_final` antes del CHECK de tres valores (D12).
- [Aviso post-revision acoplado a la validacion] -> Fire-and-forget con degradacion y respaldo N8N; sin PII; tests NR-008.
- [Conflictos de ruta `/historial-cerrados` con `/{id}`] -> Declaracion estatica antes del path con parametro (D10).
- [Doble carga de relaciones en el detalle] -> `selectinload` explicito para `sectores_adicionales`, comentarios y eventos; nunca lazy en async.

## Migration Plan

1. Migracion 018 (CHECK a cuatro valores + tres tablas) y modelos ORM.
2. Registro de politica (rol + SECTOR + atributos) y coherencia (RP-003).
3. Visibilidad SECTOR (derivacion + filtrado en el repositorio) y guards.
4. Ciclo de vida: cierre por sector, cierre global, transicion terminal, reapertura, edicion de estado y auditoria `incidente_evento`.
5. Comentarios (servicio + endpoints + formato).
6. Historial (endpoint + filtro por alcance).
7. Aviso post-revision (servicio + payload + N8N `n8n/workflow.json`).
8. Frontend: alcance SECTOR, pestana historial, acciones de ciclo, comentarios.
9. Regenerar `docs/openapi.json`.
10. Rollback: revertir el commit; `alembic downgrade` de 018 (reasigna `gestion_incidentes` a `usuario_final`, elimina tablas, restaura el CHECK de tres valores).

## Open Questions

Ninguna. Las decisiones que el enunciado pidio resolver autonomamente quedan fijadas en D3 (SQL del alcance SECTOR), D5 (semantica de reapertura), D7 (almacenamiento y formato de comentarios), D9 (disparador y payload del aviso post-revision) y D11 (cableado de la pestana). Estan registradas tambien en la seccion Open Questions del `proposal.md`.
