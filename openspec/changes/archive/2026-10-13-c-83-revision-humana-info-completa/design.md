## Context

Ver `proposal.md` — Why. Estado actual relevante:

- `RevisionHumanaTable` lista la cola con columnas minimas (ID, sector predicho, sector validado, confianza, etapa, fecha) y su accion "Validar" dispara `onValidar(clasificacion)`.
- `ValidarClasificacionDialog` recibe la `ClasificacionLogRead` ya cargada y NO consulta el incidente: solo muestra la prediccion y el selector de sector principal.
- `TicketDetailDialog` (pestaña "Lista de Tickets") ya compone una vista rica con dos consultas en paralelo: `obtenerIncidente` (`GET /api/v1/incidentes/{id}`) y `listarClasificacionesPorIncidente` (`GET /api/v1/clasificaciones/incidente/{id}`), con query keys `incidente-detalle` y `clasificaciones-historial`.
- Los datos ya existen en el backend: `IncidenteRead` expone `descripcion_pseudonimizada`, `prioridad`, `sector`, `sectores_adicionales`, `estado`, `canal_origen`, `created_at`, `updated_at`, `requiere_revision_humana`; `ClasificacionLogRead` expone `sectores_predichos` y `sectores_validados`. El tipo de frontend `ClasificacionLogRead` aun NO declara los dos ultimos.
- La validacion hoy envia un unico `sector_id_validado` (id numerico). El backend ya acepta el payload multi-etiqueta: `ClasificacionValidar` (`app/schemas/clasificacion.py`) acepta `sector_validado` (nombre canonico), `sector_id_validado` (compatibilidad) y `sectores_adicionales` (lista de nombres canonicos); `ClasificacionService.validate_payload`/`validate` (`app/services/clasificacion_service.py`) resuelven el principal por id o nombre y persisten los adicionales via `SectorRepository.get_by_nombres`. No se requiere cambio de backend.
- La consulta de detalle esta acotada por alcance en el backend (403/404 fuera de alcance).

## Goals / Non-Goals

**Goals:**
- Que el operador vea, en un unico dialogo de validacion, la descripcion pseudonimizada y todos los metadatos del incidente mas la clasificacion completa (incluidos sectores adicionales y `respuesta_raw`), antes de decidir el sector.
- Que el operador valide el conjunto multi-etiqueta COMPLETO: sector principal + sectores adicionales, editables desde el mismo dialogo, sin salir de la pestaña.
- Una sola presentacion de detalle reutilizada por la validacion y por el detalle del ticket, sin duplicar campos.
- Sin cambios de backend: reutilizar endpoints, schemas y query keys existentes.

**Non-Goals:**
- No se modifica el backend: `ClasificacionValidar` y el servicio de validacion ya soportan el payload multi-etiqueta.
- No se modifica `RevisionHumanaTable` (columnas ni contrato de `onValidar`).
- No se expone `descripcion_original` (cifrada con PII) en ninguna superficie.
- No se exponen `reportante_empleado_id` ni `ingresado_en`/`persistido_en` del incidente (OQ3).

## Decisions

### D1 — Enriquecer `ValidarClasificacionDialog` y extraer un componente de detalle compartido (opciones A + C)

El dialogo de validacion pasa a consultar `obtenerIncidente(clasificacion.incidente_id)` y `listarClasificacionesPorIncidente(...)` (mismas query keys que `TicketDetailDialog`) y renderiza la informacion con un componente presentacional de solo lectura compartido. `TicketDetailDialog` se refactoriza para consumir ese mismo componente.

- **Rationale**: mantiene el flujo "ver informacion + decidir + validar" en un unico lugar (requisito de la tesis) y evita duplicar la vista rica. La reutilizacion de query keys aprovecha el cache de React Query.
- **Alternativas consideradas**:
  - **B (accion "Ver detalle" reutilizando `TicketDetailDialog`)**: agrega un segundo modal y obliga a abrir/cerrar para decidir; peor flujo, y no mejora el dialogo de validacion.
  - **A solo (duplicar la vista dentro del dialogo)**: cumple el objetivo pero duplica la presentacion, con divergencia a futuro.

### D2 — El componente compartido es de solo lectura y presentacional

Recibe el `IncidenteRead` y la clasificacion principal (o `null`) y renderiza los campos (incluidos `respuesta_raw` y los sectores adicionales predichos/validados); no consulta ni muta. El fetch, el estado de carga/error y los controles EDITABLES (el selector de principal y el multi-select de adicionales) quedan en cada dialogo contenedor.

- **Rationale**: separacion contenedor/presentacional; el componente de lectura es reutilizable y testeable de forma pura, y la edicion multi-etiqueta es responsabilidad de `ValidarClasificacionDialog`.

### D3 — `sectores_predichos`/`sectores_validados` opcionales en el tipo

Se agregan como campos opcionales (`?: SectorRead[]`, default `[]` en render) en `ClasificacionLogRead`.

- **Rationale**: la API ya los devuelve, pero los mocks de tests existentes no los declaran. Hacerlos obligatorios romperia tests que no son objeto de este change. Opcional preserva compatibilidad y refleja que el backend los entrega con default seguro.

### D4 — Multi-etiqueta editable en la validacion (OQ1 RESUELTO)

El dialogo de validacion captura el conjunto multi-etiqueta COMPLETO. Ademas del selector de sector principal (obligatorio), ofrece un multi-select de sectores adicionales tomado del catalogo canonico (`useSectores()`). El operador puede seleccionar y deseleccionar adicionales; las opciones de adicionales EXCLUYEN el sector principal elegido (el conjunto adicional no debe repetir el principal). El componente compartido de detalle se mantiene de solo lectura (D2); la edicion vive en el contenedor.

- **Rationale**: el autor humano resolvio que el reviewer debe poder editar el conjunto completo; el backend ya lo persiste. Excluir el principal de las opciones previene la entrada invalida obvia (el backend NO rechaza explicitamente el principal dentro de `sectores_adicionales`, solo lo persiste como asociacion redundante).
- **Alternativas consideradas**:
  - **Solo lectura (alcance original)**: rechazada — no permite corregir el conjunto, que es el objetivo resuelto.
  - **Selector principal unico sin adicionales**: rechazada — deja incompleta la validacion multi-etiqueta.

### D5 — Payload multi-etiqueta por nombres canonicos (OQ1 RESUELTO)

El payload de validacion se codifica con UN UNICO esquema de identificador: nombres canonicos. La accion de confirmar/corregir envia:

```json
{
  "sector_validado": "Soporte Tecnico Software",
  "sectores_adicionales": ["Bases de Datos", "Sistemas"]
}
```

El tipo de frontend `ClasificacionValidar` se redefine a `{ sector_validado: string; sectores_adicionales: string[] }` y `validarClasificacion` lo reenvia tal cual (el servicio ya acepta `ClasificacionValidar`). `sectores_adicionales` puede ser `[]` cuando el operador no marca adicionales.

- **Rationale**: los adicionales SOLO se aceptan por nombre canonico (`ClasificacionValidar._validar_adicionales_canonicos` contra `SECTORES_CANONICOS`); usar el mismo esquema para el principal evita un payload de esquema mixto y alinea con la convencion de dominio del proyecto (`types/catalog.ts`: los nombres canonicos son el unico identificador estable; los ids numericos no se hardcodean). `validate_payload` resuelve el principal por `get_by_nombre(payload.sector_validado)` cuando `sector_id_validado` es `None`.
- **Alternativas consideradas**:
  - **Mantener `sector_id_validado` (id numerico) para el principal y nombres para los adicionales**: rechazada — payload de esquema mixto (id para el principal, nombre para los secundarios) y menos consistente con el identificador estable de dominio.
  - **Enviar `sector_id_validado` y `sector_validado` juntos**: rechazada — redundante; `validate_payload` prioriza el id e ignora el nombre.

### D6 — Manejo de alcance delegado al backend

El dialogo no acota datos por si mismo; si el fetch devuelve 403/404, muestra `ErrorAlert` con reintento y no renderiza el recurso.

- **Rationale**: FR-RBAC-005; el cliente nunca concede informacion que el backend nego. La validacion de escritura tambien respeta el alcance en el backend.

## Risks / Trade-offs

- **Latencia del fetch adicional al abrir el dialogo** → reutilizar query keys cacheadas y `staleTime`; estado de carga compuesto (FD-006) mientras alguna consulta este pendiente.
- **Regresion en `TicketDetailDialog` al refactorizar** → cubrir el componente compartido y ambos dialogos con tests Vitest; conservar los campos existentes.
- **Un adicional duplica el principal** → el backend no lo rechaza explicitamente (persiste una asociacion redundante); la UI excluye el principal de las opciones del multi-select y limpia la seleccion al cambiar el principal, para no enviar entradas invalidas obvias.
- **Payload con un nombre no canonico responde 422** → la UI solo ofrece nombres del catalogo canonico (`useSectores`); el backend ademas valida contra `SECTORES_CANONICOS`.
- **`respuesta_raw` puede ser ruidosa en la revision** → se muestra igual que en auditoria (OQ2 RESUELTO: se muestra); si molesta se ajusta sin cambiar el contrato.

## Migration Plan

1. Declarar `sectores_predichos`/`sectores_validados` opcionales en `types/clasificacion.ts` y redefinir `ClasificacionValidar` a `{ sector_validado: string; sectores_adicionales: string[] }`.
2. Extraer el componente de detalle compartido desde `TicketDetailDialog` sin cambiar su salida visible (incluye `respuesta_raw` y sectores adicionales).
3. Enriquecer `ValidarClasificacionDialog` para consultar el incidente + clasificacion y renderizar el componente compartido, el selector de principal y el multi-select de adicionales.
4. Ajustar el submit para enviar el payload multi-etiqueta por nombres canonicos; conservar las invalidaciones de cache.
5. Tests Vitest: nuevo componente compartido, `ValidarClasificacionDialog` (fetch, metadatos, descripcion, adicionales, multi-select editable, 403/404), `clasificacionesService` (payload) y `TicketDetailDialog` sin regresiones.
6. `npm run lint`, `npm run test`, `npm run build` en `App/Frontend/`.

Rollback: revertir el commit. Es frontend puro, sin migraciones ni estado persistente.

## Open Questions

- **OQ1 — Validacion multi-etiqueta: RESUELTO**. La validacion pasa de solo lectura a EDITABLE: el reviewer edita el conjunto completo (principal + adicionales) y el payload envia `sector_validado` (nombre canonico) + `sectores_adicionales` (nombres canonicos). Ver D4 y D5.
- **OQ2 — Mostrar `respuesta_raw` en revision humana: RESUELTO**. Se MUESTRA en el dialogo de validacion, igual que en auditoria. Ver FRH-003.
- **OQ3 — Campos opcionales de `IncidenteRead`: RESUELTO**. Se AGREGA `sectores_adicionales` (nivel incidente) a la vista de detalle. NO se muestran `reportante_empleado_id` ni `ingresado_en`/`persistido_en`. Ver FRH-002.
