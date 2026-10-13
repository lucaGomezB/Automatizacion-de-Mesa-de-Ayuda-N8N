## 1. Preparacion y contrato de datos

- [x] 1.1 Safety net: ejecutar la suite Vitest existente del panel de Administracion (`npm run test` en `App/Frontend/`) y registrar la linea base de tests en verde antes de tocar archivos
- [x] 1.2 Declarar `sectores_predichos` y `sectores_validados` como campos opcionales (`?: SectorRead[]`) en `ClasificacionLogRead` (`src/types/clasificacion.ts`) y verificar que `npm run build` typechequea sin errores
- [x] 1.3 Redefinir `ClasificacionValidar` a `{ sector_validado: string; sectores_adicionales: string[] }` en `src/types/clasificacion.ts` y verificar que `npm run build` typechequea (los callers que aun envían `sector_id_validado` fallaran y se corrigen en la tarea 4.2)

## 2. Componente de detalle compartido (TDD)

- [x] 2.1 RED: crear `src/pages/Administracion/DetalleIncidente.test.tsx` que afirme el render de descripcion pseudonimizada, estado, sector, sectores adicionales del incidente, prioridad, canal, fechas, confianza, etapa, sector validado y `respuesta_raw`; verificar que falla por no existir el componente
- [x] 2.2 GREEN: implementar `src/pages/Administracion/DetalleIncidente.tsx` como componente presentacional de solo lectura (recibe `IncidenteRead` y la clasificacion) hasta que 2.1 pase
- [x] 2.3 TRIANGULAR: agregar casos para clasificacion ausente, sin `respuesta_raw`, sin sectores adicionales, `requiere_revision_humana` verdadero y estado terminal; verificar que pasan
- [x] 2.4 Refactorizar `TicketDetailDialog.tsx` para consumir `DetalleIncidente` y verificar que su suite existente sigue pasando sin regresiones

## 3. Dialogo de validacion enriquecido (TDD)

- [x] 3.1 RED: extender `ValidarClasificacionDialog.test.tsx` mockeando `obtenerIncidente` y `listarClasificacionesPorIncidente` para afirmar que se muestran la descripcion pseudonimizada, los metadatos del incidente (incluidos los `sectores_adicionales` del incidente) y `respuesta_raw`; verificar que falla
- [x] 3.2 GREEN: consultar el detalle y el historial en `ValidarClasificacionDialog.tsx` (query keys `incidente-detalle` y `clasificaciones-historial`) y renderizar `DetalleIncidente` junto a los controles de validacion; verificar 3.1 en verde
- [x] 3.3 Manejar el estado de carga compuesto y el error 403/404 con reintento, sin exponer datos del recurso; verificar con tests
- [x] 3.4 TRIANGULAR: casos con y sin `respuesta_raw`, con y sin `sectores_adicionales` del incidente, y con `requiere_revision_humana` en ambos valores; verificar que pasan

## 4. Validacion multi-etiqueta editable (TDD)

- [x] 4.1 RED: extender `ValidarClasificacionDialog.test.tsx` para afirmar que el dialogo renderiza un multi-select de sectores adicionales tomado del catalogo (`useSectores`), que las opciones EXCLUYEN el sector principal elegido, y que al confirmar se envia el payload `{ sector_validado, sectores_adicionales }` por nombres canonicos; verificar que falla
- [x] 4.2 GREEN: agregar el estado del conjunto de adicionales y el control multi-select a `ValidarClasificacionDialog.tsx`; construir el payload con `sector_validado` (nombre canonico del principal) y `sectores_adicionales` (nombres canonicos de los adicionales); verificar 4.1 en verde
- [x] 4.3 TRIANGULAR: seleccionar y deseleccionar adicionales; cambiar el principal actualiza el conjunto de opciones y elimina cualquier duplicado del principal; confirmar sin adicionales envia `sectores_adicionales: []`; verificar que los casos pasan
- [x] 4.4 RED/GREEN: actualizar `src/services/clasificacionesService.test.ts` para que `validarClasificacion` afirme que reenvia el payload multi-etiqueta `{ sector_validado, sectores_adicionales }`; verificar que falla y luego pasa
- [x] 4.5 TRIANGULAR: extender la prueba del servicio con al menos dos casos de adicionales (uno y varios) y uno sin adicionales; verificar que pasan

## 5. Verificacion integral

- [x] 5.1 Ejecutar `npm run lint`, `npm run test` y `npm run build` en `App/Frontend/` y verificar que todo pasa
- [x] 5.2 Verificar cobertura de los escenarios FRH-001 a FRH-007 con tests y correr `openspec validate c-83-revision-humana-info-completa --strict`
