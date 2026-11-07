## MODIFIED Requirements

### Requirement: FRH-003 — El flujo de validacion expone el resultado completo de la clasificacion

El dialogo de validacion SHALL mostrar el resultado de la clasificacion: sector predicho, confianza,
etapa del pipeline y, si ya la hubiera, el sector validado. Ademas SHALL mostrar los sectores
adicionales predichos y validados cuando existan. La respuesta raw del clasificador (`respuesta_raw`)
NO SHALL mostrarse en el dialogo de validacion, aunque el campo exista en los datos de la
clasificacion.

#### Scenario: Se muestra la prediccion principal

- **WHEN** el operador abre la validacion de una clasificacion pendiente
- **THEN** el dialogo muestra el sector predicho, la confianza y la etapa del pipeline

#### Scenario: La clasificacion tiene sectores adicionales

- **WHEN** la clasificacion expone sectores adicionales predichos o validados
- **THEN** el dialogo los lista, diferenciando los predichos de los validados

#### Scenario: La clasificacion tiene respuesta raw

- **WHEN** la clasificacion incluye `respuesta_raw` (etapa Gemini)
- **THEN** el dialogo NO muestra la respuesta raw del clasificador
