# frontend-revision-humana Specification

## Purpose

Permite al operador de mesa de ayuda revisar toda la informacion disponible de un incidente y de su clasificacion dentro del flujo de validacion humana del Panel de Administracion, sin abandonar la pestaña "Revision Humana", antes de confirmar o corregir el conjunto de sectores asignado.

## Requirements

### Requirement: FRH-001 — El flujo de validacion expone la descripcion del incidente

Al abrir la validacion de una clasificacion pendiente, el sistema SHALL mostrar la descripcion del incidente en el mismo dialogo. La descripcion mostrada MUST ser la pseudonimizada; la descripcion original (cifrada con PII) NUNCA SHALL exponerse.

#### Scenario: La validacion muestra la descripcion pseudonimizada

- **WHEN** el operador abre el dialogo de validacion de una clasificacion pendiente y el incidente tiene descripcion
- **THEN** el dialogo muestra el texto de `descripcion_pseudonimizada` del incidente

#### Scenario: El incidente no tiene descripcion disponible

- **WHEN** el detalle del incidente no aporta descripcion pseudonimizada
- **THEN** el dialogo muestra un estado o texto que indica ausencia de descripcion, sin romper el flujo de validacion

### Requirement: FRH-002 — El flujo de validacion expone los metadatos del incidente

El dialogo de validacion SHALL mostrar los metadatos disponibles del incidente: estado, sector asignado, sectores adicionales del incidente, prioridad, canal de origen, fecha de creacion y fecha de ultima actualizacion. La informacion SHALL presentarse en el mismo lugar que el selector de sector y el boton de validacion. Los campos `reportante_empleado_id`, `ingresado_en` y `persistido_en` NO SHALL mostrarse.

#### Scenario: Se muestran los metadatos del incidente

- **WHEN** el operador abre la validacion de una clasificacion pendiente
- **THEN** el dialogo muestra estado, sector, prioridad, canal de origen y las fechas de creacion y actualizacion del incidente

#### Scenario: El incidente declara sectores adicionales

- **WHEN** el incidente expone `sectores_adicionales`
- **THEN** el dialogo los muestra junto a los demas metadatos del incidente

#### Scenario: El incidente senala revision humana requerida

- **WHEN** el incidente tiene `requiere_revision_humana` verdadero
- **THEN** el dialogo lo indica de forma visible al operador

### Requirement: FRH-003 — El flujo de validacion expone el resultado completo de la clasificacion

El dialogo de validacion SHALL mostrar el resultado de la clasificacion: sector predicho, confianza, etapa del pipeline, respuesta raw (cuando exista) y, si ya la hubiera, el sector validado. Ademas SHALL mostrar los sectores adicionales predichos y validados cuando existan.

#### Scenario: Se muestra la prediccion principal

- **WHEN** el operador abre la validacion de una clasificacion pendiente
- **THEN** el dialogo muestra el sector predicho, la confianza y la etapa del pipeline

#### Scenario: La clasificacion tiene sectores adicionales

- **WHEN** la clasificacion expone sectores adicionales predichos o validados
- **THEN** el dialogo los lista, diferenciando los predichos de los validados

#### Scenario: La clasificacion tiene respuesta raw

- **WHEN** la clasificacion incluye `respuesta_raw` (etapa Gemini)
- **THEN** el dialogo la muestra como informacion de auditoria

### Requirement: FRH-004 — La informacion de detalle es consistente entre la validacion y el detalle del ticket

La presentacion de la informacion de detalle del incidente SHALL ser la misma en el dialogo de validacion y en el detalle del ticket, de modo que un cambio en los campos mostrados se refleje en ambas superficies sin divergencia.

#### Scenario: Ambas superficies muestran los mismos campos del incidente

- **WHEN** se compara la informacion de un mismo incidente mostrada en la validacion y en el detalle del ticket
- **THEN** ambas superficies presentan el mismo conjunto de campos de detalle (estado, sector, sectores adicionales, prioridad, canal, fechas y descripcion pseudonimizada)

### Requirement: FRH-005 — El fetch del detalle respeta el alcance y no expone recursos denegados

El dialogo de validacion SHALL obtener el detalle del incidente desde el backend y SHALL tratar una denegacion o inexistencia (403/404) como un estado de error, sin exponer datos del recurso ni del alcance. El frontend NUNCA SHALL conceder por si mismo informacion que el backend no devolvio.

#### Scenario: Recurso fuera de alcance denegado

- **WHEN** el backend responde 403 o 404 al solicitar el detalle del incidente
- **THEN** el dialogo muestra un estado de error sin renderizar datos del recurso

#### Scenario: Error de carga con reintento

- **WHEN** la consulta del detalle del incidente falla
- **THEN** el dialogo ofrece la opcion de reintentar la carga

#### Scenario: Estado de carga compuesto

- **WHEN** el detalle del incidente o la clasificacion aun estan cargando
- **THEN** el dialogo muestra su estado de carga en lugar de datos parciales

### Requirement: FRH-006 — La validacion edita el conjunto multi-etiqueta completo

La accion de validacion SHALL permitir al operador elegir el sector principal y seleccionar o deseleccionar sectores adicionales (seleccion multiple) desde el catalogo canonico de sectores. Los sectores adicionales seleccionables SHALL excluir el sector principal elegido. La interfaz SHALL impedir que el conjunto adicional repita el principal.

#### Scenario: El operador elige principal y sectores adicionales

- **WHEN** el operador selecciona el sector principal y uno o mas sectores adicionales en el dialogo de validacion
- **THEN** la interfaz refleja el conjunto multi-etiqueta completo (principal + adicionales) antes de confirmar

#### Scenario: El operador deselecciona un sector adicional

- **WHEN** el operador quita un sector adicional previamente seleccionado
- **THEN** ese sector deja de formar parte del conjunto que se enviara en la validacion

#### Scenario: Las opciones adicionales excluyen el principal

- **WHEN** el operador elige un sector principal
- **THEN** ese sector no aparece como opcion seleccionable entre los sectores adicionales y no puede quedar duplicado

### Requirement: FRH-007 — El payload de validacion envia el conjunto multi-etiqueta por nombres canonicos

La accion de confirmar o corregir SHALL enviar la decision del operador como nombres canonicos de sector: el principal en `sector_validado` y los adicionales en `sectores_adicionales`. Cuando el operador no seleccione adicionales, `sectores_adicionales` SHALL enviarse como lista vacia.

#### Scenario: Confirmar envia principal y adicionales por nombre canonico

- **WHEN** el operador confirma o corrige el conjunto y acciona la validacion
- **THEN** el sistema envia `sector_validado` con el nombre canonico del sector principal y `sectores_adicionales` con los nombres canonicos de los adicionales seleccionados

#### Scenario: Confirmar sin adicionales envia lista vacia

- **WHEN** el operador confirma sin seleccionar sectores adicionales
- **THEN** el sistema envia `sectores_adicionales` como lista vacia

#### Scenario: Exito de validacion refresca las superficies afectadas

- **WHEN** la validacion se completa con exito
- **THEN** el sistema refresca la cola de revision pendiente, la lista de incidentes, el detalle del incidente afectado y el historial de clasificaciones
