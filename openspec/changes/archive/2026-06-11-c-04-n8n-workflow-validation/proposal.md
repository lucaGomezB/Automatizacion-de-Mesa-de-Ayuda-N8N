## Why

El workflow N8N (`Automatizacion_Mesa_de_Ayuda.json`) es el corazón de la capa de orquestación (tesis §5.3), pero hoy está incompleto: los dos nodos `code` contienen lógica placeholder (`myNewField = 1`), los dos nodos `if` no tienen condiciones configuradas y no existe un nodo que homogenice los canales en la estructura unificada que describe la tesis. En este estado el flujo no valida los datos de entrada, no aplica el umbral de confianza ≥ 0.70 para derivar a revisión humana ni persiste incidentes contra el backend FastAPI real. C-04 cierra ese hueco para que el flujo exportado refleje el comportamiento especificado en el Anexo H y la tesis §6.3.

## What Changes

- Reemplazar la lógica placeholder del nodo `code` del canal de correo ("Se verifica que la informacion sea la necesaria...") por validación real de campos requeridos según el Anexo H.
- Reemplazar la lógica placeholder del nodo `code` del canal telefónico ("Se verifica lo que trajo la IA") por validación de la respuesta parseada por el AI Agent, incluyendo la validación de 5 pasos del Anexo H §H.3 sobre `categoría` y `confianza`.
- Agregar un **nodo de normalización** que homogenice la estructura de los tres canales (correo, formulario web, telefonía) en un formato unificado con `id`, `timestamp` (precisión al milisegundo), `canal_origen` y `descripcion`, tal como exige la tesis §5.3.
- Configurar las condiciones de los dos nodos `if` para evaluar `confianza >= 0.70` y rutear: por encima del umbral → creación directa del incidente; por debajo → marca de revisión humana.
- Configurar el nodo HTTP de persistencia para invocar `POST /api/v1/incidentes` del backend FastAPI con el payload `IncidenteCreate` (`descripcion`, `prioridad`, `canal`).
- **Reconciliar el contrato de clasificación**: el backend implementado NO expone un endpoint `POST /api/v1/clasificar` independiente; la clasificación (pipeline híbrido determinístico → Gemini) ocurre dentro de `POST /api/v1/incidentes` vía `IncidenteService.create_and_classify()`, que devuelve `sector`, `confianza` y `requiere_revision`. El workflow debe consumir ese contrato de una sola llamada en lugar de las dos llamadas separadas que sugieren la tesis §6.3 y el roadmap. **Ver design.md para la decisión y sus alternativas.**
- Agregar un script de validación en `tests/` (pytest) que valide la estructura del JSON del workflow exportado: presencia de nodos, condiciones IF no vacías, ausencia de placeholders, URLs de los nodos HTTP y forma del payload de normalización. Esto hace el workflow declarativo verificable bajo Strict TDD.
- Documentar el flujo, sus nodos y cómo importarlo/probarlo en `docs/n8n-workflow-guide.md`.

## Capabilities

### New Capabilities
- `n8n-workflow`: Estructura y comportamiento del workflow N8N de orquestación — normalización de canales a formato unificado, validación de entrada por canal según Anexo H, ruteo por umbral de confianza ≥ 0.70 hacia creación directa vs revisión humana, e invocación del backend FastAPI para persistir incidentes clasificados.

### Modified Capabilities
<!-- Ninguna. C-04 no cambia requisitos de specs existentes (foundation-environment, n8n-notification, data-pseudonymization); consume sus contratos sin modificarlos. -->

## Impact

- **Archivo del workflow**: `Automatizacion_Mesa_de_Ayuda.json` — reescritura de 2 nodos `code`, configuración de 2 nodos `if`, alta de 1 nodo de normalización, ajuste de los nodos `httpRequest` para apuntar a `POST /api/v1/incidentes`.
- **Tests**: nuevo `Gestion_Incidentes/tests/test_n8n_workflow.py` (o equivalente) que valida la estructura del JSON exportado. No altera la suite existente (81 passed / 1 skipped); solo agrega casos.
- **Backend (consumo, sin cambios productivos esperados)**: el workflow invoca `POST /api/v1/incidentes`. Si durante la verificación se detecta que el payload o la respuesta no alcanzan para el ruteo del workflow, se documenta como gap para un change posterior (no se modifica el backend en C-04 salvo decisión explícita registrada en design.md).
- **Documentación**: nuevo `docs/n8n-workflow-guide.md`.
- **Dependencias externas**: N8N 1.62 (Docker autoalojado), backend FastAPI corriendo, PostgreSQL. El canal telefónico depende del AI Agent + Redis ya presentes en el JSON.
- **Pseudonimización (C-03)**: la `descripcion` que viaja al backend ya debe ir pseudonimizada; el flujo no debe enviar PII en claro hacia el módulo de clasificación. Se contempla en el diseño del nodo de normalización.
- **Governance**: MEDIO — implementar con checkpoints; las decisiones no obvias (contrato de endpoint, dónde ocurre la pseudonimización en el flujo) se elevan en design.md.
