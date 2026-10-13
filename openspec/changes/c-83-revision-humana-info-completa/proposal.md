## Why

En la pestaña "Revision Humana" del Panel de Administracion, el operador valida clasificaciones de baja confianza (< 0.70) a ciegas: ni la tabla ni el dialogo de validacion muestran la descripcion del incidente. El operador debe abandonar la pestaña y abrir el ticket en "Lista de Tickets" para poder decidir el sector, lo que rompe el flujo de revision y degrada la calidad del corpus de evaluacion.

## What Changes

- El dialogo de validacion humana muestra, en el mismo lugar, toda la informacion disponible del incidente antes de decidir el sector: descripcion pseudonimizada, metadatos (estado, sector, prioridad, canal, fechas), clasificacion (sector predicho, confianza, etapa, respuesta raw) y sectores adicionales predichos/validados.
- Se extrae una vista de detalle de incidente de solo lectura y reutilizable, compartida por `TicketDetailDialog` y la validacion, para no duplicar la presentacion.
- El tipo de frontend `ClasificacionLogRead` incorpora `sectores_predichos` y `sectores_validados` (ya devueltos por la API, hoy sin declarar).
- El flujo "ver informacion + decidir + validar" queda en un unico dialogo, que captura el conjunto multi-etiqueta EDITABLE: sector principal + sectores adicionales. La validacion envia `sector_validado` (nombre canonico del principal) y `sectores_adicionales` (nombres canonicos de los adicionales); el tipo `ClasificacionValidar` se redefine en consecuencia.
- Frontend unicamente: no se modifican endpoints ni schemas del backend; `ClasificacionValidar` y el servicio de validacion ya aceptan el payload multi-etiqueta.

## Capabilities

### New Capabilities

- `frontend-revision-humana`: experiencia de revision humana en el Panel de Administracion — el operador accede a la informacion completa del incidente y de su clasificacion dentro del flujo de validacion, incluida la descripcion pseudonimizada y los sectores multietiqueta editables (principal + adicionales), antes de confirmar o corregir el conjunto de sectores.

### Modified Capabilities

- Ninguna. Los contratos de datos (`frontend-data-layer`) y de alcance/RBAC (`frontend-rbac`, `incident-visibility`) no cambian: se reutilizan las consultas existentes y el backend sigue acotando la visibilidad.

## Impact

- `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.tsx` — se enriquece para consultar y mostrar el detalle del incidente + clasificacion.
- `App/Frontend/src/pages/Administracion/TicketDetailDialog.tsx` — se refactoriza para consumir el componente de detalle compartido.
- `App/Frontend/src/pages/Administracion/RevisionHumanaTable.tsx` — sin cambios de contrato (seguira disparando `onValidar`).
- Nuevo componente compartido de detalle (solo lectura) en `App/Frontend/src/pages/Administracion/` o `components/shared/`.
- `App/Frontend/src/types/clasificacion.ts` — agrega `sectores_predichos`/`sectores_validados` opcionales y redefine `ClasificacionValidar` a `{ sector_validado: string; sectores_adicionales: string[] }`.
- Tests Vitest: `ValidarClasificacionDialog.test.tsx`, `RevisionHumanaTable.test.tsx` y los del detalle compartido.
- Sin cambios en backend, N8N, migraciones ni dependencias externas.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Duplicar la vista de detalle entre los dos dialogos | Media | Extraer un unico componente de detalle compartido y reutilizarlo |
| El fetch escapa al alcance del operador | Baja | El backend acota la consulta; 403/404 se renderizan como error sin exponer el recurso (FR-RBAC-005) |
| El fetch adicional degrada la UX (latencia) | Baja | Reutilizar las query keys `incidente-detalle` y `clasificaciones-historial` ya cacheadas; estado de carga compuesto (FD-006) |

## Rollback Plan

Revertir el commit del change. Al ser frontend y no introducir endpoints, esquemas ni migraciones, no hay estado persistente que migrar de vuelta. Los archivos de tipos y componentes vuelven a su version anterior.

## Dependencies

- Ninguna nueva. Se reutilizan `obtenerIncidente` y `listarClasificacionesPorIncidente`, ya existentes.

## Success Criteria

- [ ] Al abrir "Validar" desde Revision Humana, el operador ve la descripcion pseudonimizada y todos los metadatos del incidente sin salir de la pestaña.
- [ ] El dialogo muestra la clasificacion completa (sector predicho, confianza, etapa, respuesta raw) y los sectores adicionales predichos/validados.
- [ ] `TicketDetailDialog` sigue mostrando la misma informacion usando el componente compartido, sin regresiones en sus tests.
- [ ] Un 403/404 del backend se muestra como error sin exponer datos del recurso.
- [ ] La suite Vitest del frontend pasa.

## Open Questions

1. **Sectores adicionales en la validacion (multi-etiqueta): RESUELTO.** La validacion pasa a ser EDITABLE: el reviewer edita el conjunto completo (principal + adicionales) y el payload envia `sector_validado` + `sectores_adicionales` por nombres canonicos. Ver `design.md` (D4, D5) y FRH-006/FRH-007.
2. **Visibilidad de `respuesta_raw` en revision: RESUELTO.** Se MUESTRA en el dialogo de validacion, igual que en el detalle de auditoria. Ver FRH-003.
3. **Campos opcionales de `IncidenteRead`: RESUELTO.** Se agrega `sectores_adicionales` (nivel incidente); NO se muestran `reportante_empleado_id` ni `ingresado_en`/`persistido_en`. Ver FRH-002.
