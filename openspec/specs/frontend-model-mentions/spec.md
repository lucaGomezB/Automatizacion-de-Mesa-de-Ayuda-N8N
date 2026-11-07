# frontend-model-mentions Specification

## Purpose
Define el contrato de presentación del modelo de clasificación en la interfaz del frontend: las
menciones del modelo que ve el usuario (la etiqueta de la etapa del pipeline y el texto informativo
del portal de reporte) identifican la etapa o al proveedor de forma agnóstica a la versión, de modo
que un cambio del modelo vigente no deje la UI obsoleta.

## Requirements

### Requirement: La etiqueta de la etapa del pipeline es agnóstica a la versión del modelo

La presentación de la etapa del pipeline de clasificación SHALL identificar la etapa de análisis sin
nombrar un proveedor ni una versión del modelo. La etapa `gemini` SHALL rotularse exactamente
"Análisis por IA". Las etiquetas de las etapas `deterministic` y `fallback` NO cambian
("Determinístico" y "Sin clasificar"). La etiqueta resultante MUST NOT contener el nombre de un
proveedor (por ejemplo "Gemini") ni un número de versión (por ejemplo "2.5 Flash"). Esta regla aplica
a todas las superficies que renderizan la etapa del pipeline: el detalle del ticket, el diálogo de
validación, la cola de revisión y la tarjeta de confirmación del portal de reporte.

#### Scenario: La etapa gemini se etiqueta sin versión

- **WHEN** se formatea la etapa `gemini` para mostrarla en la UI
- **THEN** la etiqueta resultante es "Análisis por IA" y no contiene "Gemini", ni un número de versión, ni el literal "2.5 Flash"

#### Scenario: Las etapas determinística y fallback conservan su etiqueta

- **WHEN** se formatean las etapas `deterministic` y `fallback`
- **THEN** sus etiquetas siguen siendo "Determinístico" y "Sin clasificar"

#### Scenario: Una superficie de clasificación no muestra una versión retirada

- **WHEN** una clasificación con etapa `gemini` se muestra en el detalle del ticket, el diálogo de
  validación, la cola de revisión o la tarjeta de confirmación del portal de reporte
- **THEN** la etapa se presenta como "Análisis por IA", sin nombre de proveedor ni versión del modelo

### Requirement: El texto del portal de reporte no nombra una versión del modelo

El texto informativo del portal de reporte de incidentes que describe la clasificación automática
SHALL ser agnóstico al proveedor y a la versión del modelo. MUST NOT nombrar un proveedor (por
ejemplo "Gemini") ni una versión concreta (por ejemplo "Gemini 2.5 Flash" o "Gemini 3.6 Flash").
El aviso sobre el umbral de revisión humana (confianza < 70%) SHALL conservarse intacto y con el
mismo significado.

#### Scenario: El encabezado del portal no nombra una versión

- **WHEN** un usuario abre el portal de reporte de incidentes
- **THEN** el texto que describe la clasificación automática no contiene "Gemini", ni "2.5 Flash", ni ninguna otra versión del modelo

#### Scenario: La mención del proveedor es agnóstica a la versión

- **WHEN** el texto del portal describe la clasificación automática
- **THEN** lo hace sin nombrar un proveedor ni un modelo, y conserva el aviso del umbral de revisión humana del 70%
