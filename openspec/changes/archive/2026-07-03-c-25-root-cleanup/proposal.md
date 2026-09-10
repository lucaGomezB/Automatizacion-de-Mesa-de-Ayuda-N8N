## Why

C-24 unifico el codigo fuente bajo `App/`, pero tres archivos sueltos en la raiz del repositorio rompen la presentacion ordenada que se espera de un anexo de tesis universitaria. `ANEXO_H_Prompt_Gemini_Especificacion.md` es un documento teorico-tesis que pertenece a `docs/` junto al resto de los anexos. `Automatizacion_Mesa_de_Ayuda.json` es un artefacto de N8N que merece su propio directorio agrupador. `twilio/` es parte de la integracion telefonica de N8N y tiene mas sentido bajo ese mismo agrupador. Ademas, el `.env.example` raiz contiene una referencia obsoleta a `Gestion_Incidentes/` que ya no existe tras C-24.

El repositorio se entrega como material complementario de la tesis. La raiz debe verse profesional: codigo bajo `App/`, artefactos N8N bajo `n8n/`, documentacion bajo `docs/`.

## What Changes

- Mover `ANEXO_H_Prompt_Gemini_Especificacion.md` a `docs/anexo_h_prompt_gemini.md` y actualizar 5 archivos activos que lo referencian (openspec/config.yaml, CHANGES.md, CLAUDE.md, knowledge-base/README.md, gemini_classifier.py).
- Mover `Automatizacion_Mesa_de_Ayuda.json` a `n8n/workflow.json` y actualizar ~14 archivos activos que lo referencian (docker-compose.yml, tests, AGENTS.md, CHANGES.md, CLAUDE.md, README.md, knowledge-base/, docs/).
- Mover `twilio/` completo (2 archivos) a `n8n/twilio/` y actualizar referencias internas en twilio/README.md y en la spec project-structure. Los cambios archivados (C-16) no se modifican.
- Corregir referencia obsoleta en `.env.example` raiz: `Gestion_Incidentes/.env` → `App/Backend/.env`.
- Crear el directorio `n8n/` que agrupa workflow.json y twilio/.
- El archivo `docs/Comandos_para_iniciar_proyecto.txt` se deja como esta (quick-reference, el usuario puede decidir despues).

## Capabilities

### New Capabilities

Ninguna. Este change es puramente reestructuracion de archivos, no introduce nueva funcionalidad.

### Modified Capabilities

- `project-structure`: la especificacion de la estructura canonica del repositorio debe reflejar el directorio `n8n/` con los artefactos agrupados, la ausencia de archivos sueltos en la raiz que no pertenecen ahi, y el nuevo path del TwiML script bajo `n8n/twilio/`.

## Impact

- **Archivos movidos (git mv)**: `ANEXO_H_Prompt_Gemini_Especificacion.md`, `Automatizacion_Mesa_de_Ayuda.json`, `twilio/twiml.xml`, `twilio/README.md`.
- **Archivos activos modificados**: 20 archivos reciben actualizaciones de path (ver design.md para la lista exhaustiva).
- **Archivos NO modificados**: cambios archivados (`openspec/changes/archive/`), specs principales salvo `project-structure`.
- **docker-compose.yml**: cambio de volume mount path (operacional, no logico).
- **Tests**: `test_n8n_workflow.py` necesita actualizar la ruta al JSON del workflow (operacional, no logico).
- **Riesgo de ruptura**: bajo. Todos los cambios son mecanicos (renames + update de strings). No se modifica logica de negocio.
