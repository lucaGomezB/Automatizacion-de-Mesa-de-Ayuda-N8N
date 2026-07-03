## Context

C-24 reestructuro `Gestion_Incidentes/` → `App/Backend/` y `Frontend/` → `App/Frontend/`. El codigo fuente quedo bien organizado bajo `App/`, pero la raiz del repositorio tiene tres elementos que rompen la presentacion:

1. `ANEXO_H_Prompt_Gemini_Especificacion.md` — archivo de tesis suelto en raiz. Los otros anexos (C, F) ya estan en `docs/` con nombres normalizados (`anexo_c_esquema_bd.md`, `anexo_f_corpus.md`).
2. `Automatizacion_Mesa_de_Ayuda.json` — workflow N8N suelto en raiz. No tiene agrupador propio.
3. `twilio/` — directorio con artefactos de integracion Twilio (TwiML script + README). Twilio es parte del ecosistema N8N (C-05, C-16).

**Restriccion**: los cambios archivados (`openspec/changes/archive/`) NO se modifican. Son historicos y deben reflejar el estado del repositorio en el momento de su ejecucion. Solo se actualizan archivos activos.

## Goals / Non-Goals

**Goals:**
- Agrupar el workflow N8N y los artefactos Twilio bajo un directorio `n8n/` consistente.
- Mover el anexo H de tesis a `docs/` con nombre normalizado.
- Corregir la referencia obsoleta en `.env.example` raiz.
- Actualizar TODAS las referencias en archivos activos sin romper nada.
- Preservar el historial de git via `git mv`.

**Non-Goals:**
- NO modificar cambios archivados (`openspec/changes/archive/`).
- NO modificar `CLAUDE.md` salvo las referencias a los archivos movidos (el archivo no se renombra ni elimina).
- NO tocar `docs/Comandos_para_iniciar_proyecto.txt` (el usuario decide si renombrar a `.md` despues).
- NO modificar `App/`, specs principales (salvo `project-structure`), ni infraestructura (`.github/`, `.engram/`, `.opencode/`).
- NO introducir nueva funcionalidad ni tests adicionales.

## Decisions

### Decision 1: Nombre del directorio N8N

**Opciones consideradas:**
- `n8n/`: corto, coincide con el nombre de la herramienta, deja espacio para futuros artefactos (workflows adicionales, configuraciones).
- `workflows/`: generico pero ambiguo (podria confundirse con CI/CD workflows de `.github/`).
- `orchestration/`: correcto conceptualmente pero muy generico; no deja claro que es N8N.

**Decision**: `n8n/`. Es el nombre de la herramienta y es auto-documentado. Contiene `workflow.json` (el workflow principal) y `twilio/` (artefactos de integracion telefonica, que es parte del ecosistema N8N).

### Decision 2: Nombre del archivo de workflow

**Opciones:**
- `n8n/workflow.json`: simple, generico. Si hubiera multiples workflows en el futuro, habria que renombrar.
- `n8n/Automatizacion_Mesa_de_Ayuda.json`: preserva el nombre original pero es largo y tiene guiones bajos.
- `n8n/mesa-de-ayuda.json`: nuevo nombre, mas corto, kebab-case.

**Decision**: `n8n/workflow.json`. Es el unico workflow del proyecto y el nombre generico es claro en contexto (`n8n/workflow.json`). Si en el futuro se agregan mas workflows, se pueden nombrar descriptivamente. Mantener el nombre original dentro del archivo JSON (el campo `"name"` no cambia).

### Decision 3: Nombre del anexo H

**Opciones:**
- `docs/ANEXO_H_Prompt_Gemini_Especificacion.md`: preserva el nombre original, pero rompe la convencion de los otros anexos que usan minusculas.
- `docs/anexo_h_prompt_gemini.md`: consistente con `anexo_c_esquema_bd.md` y `anexo_f_corpus.md`. Mas corto.

**Decision**: `docs/anexo_h_prompt_gemini.md`. Consistencia con los otros anexos en `docs/`.

### Decision 4: Referencias en specs principales

Las specs en `openspec/specs/` que referencian paths movidos se actualizan SOLO si el cambio es puramente mecanico (renombrar un path). Si la spec usa el path como parte de una regla de negocio que ya no aplica, se evalua caso por caso.

- `project-structure/spec.md` linea 67: referencia `twilio/README.md` en contexto de documentacion actualizada. Se actualiza a `n8n/twilio/README.md`.
- `n8n-workflow/spec.md`: usa `Automatizacion_Mesa_de_Ayuda.json` como valor semantico (el nombre del workflow en el contexto N8N), no como path de archivo. Las lineas 107 y 215 mencionan `Automatizacion_Mesa_de_Ayuda.json` parentizado como "el JSON exportado del workflow". **No se modifica** — se refiere al nombre del artefacto, no a su ubicacion en disco.

## Move Plan — Orden de Operaciones

El orden importa porque `git mv` del directorio `twilio/` debe ocurrir DESPUES de crear `n8n/` y ANTES de actualizar referencias.

### Fase 1: Crear estructura destino

1. Crear directorio `n8n/` en raiz.
2. Crear directorio `n8n/twilio/`.

### Fase 2: Mover archivos (git mv)

3. `git mv ANEXO_H_Prompt_Gemini_Especificacion.md docs/anexo_h_prompt_gemini.md`
4. `git mv Automatizacion_Mesa_de_Ayuda.json n8n/workflow.json`
5. `git mv twilio/twiml.xml n8n/twilio/twiml.xml`
6. `git mv twilio/README.md n8n/twilio/README.md`

### Fase 3: Actualizar referencias en archivos activos

**Grupo A — Archivos que referencian `ANEXO_H_Prompt_Gemini_Especificacion.md`:**

| # | Archivo | Linea | Cambio |
|---|---------|-------|--------|
| A1 | `openspec/config.yaml` | 49 | `gemini_spec: ANEXO_H_Prompt_Gemini_Especificacion.md` → `gemini_spec: docs/anexo_h_prompt_gemini.md` |
| A2 | `CHANGES.md` | 149 | `ANEXO_H_Prompt_Gemini_Especificacion.md §H.3` → `docs/anexo_h_prompt_gemini.md §H.3` |
| A3 | `CHANGES.md` | 268 | `ANEXO_H_Prompt_Gemini_Especificacion.md §H.4` → `docs/anexo_h_prompt_gemini.md §H.4` |
| A4 | `CLAUDE.md` | 20 | `ANEXO_H_Prompt_Gemini_Especificacion.md` → `docs/anexo_h_prompt_gemini.md` (en tabla Key Files) |
| A5 | `knowledge-base/README.md` | 3 | `ANEXO_H_Prompt_Gemini_Especificacion.md` → `docs/anexo_h_prompt_gemini.md` |
| A6 | `App/Backend/app/classifiers/gemini_classifier.py` | 9 | Actualizar comentario: `ANEXO_H_Prompt_Gemini_Especificacion.md` → `docs/anexo_h_prompt_gemini.md` |

**Grupo B — Archivos que referencian `Automatizacion_Mesa_de_Ayuda.json`:**

| # | Archivo | Linea(s) | Cambio |
|---|---------|----------|--------|
| B1 | `docker-compose.yml` | 113 | `./Automatizacion_Mesa_de_Ayuda.json:/data/Automatizacion_Mesa_de_Ayuda.json:ro` → `./n8n/workflow.json:/data/workflow.json:ro` |
| B2 | `App/Backend/tests/test_n8n_workflow.py` | 4, 27 | Actualizar docstring y WORKFLOW_PATH: `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B3 | `AGENTS.md` | 57 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` (component map) |
| B4 | `CHANGES.md` | 176 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B5 | `CLAUDE.md` | 17, 99 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B6 | `README.md` | 82, 112 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B7 | `knowledge-base/08_arquitectura_propuesta.md` | 37 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B8 | `knowledge-base/06_funcionalidades.md` | 62 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B9 | `knowledge-base/10_preguntas_abiertas.md` | 35 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B10 | `docs/n8n-workflow-guide.md` | 9, 251, 262, 282, 446, 479, 557, 561 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` (8 ocurrencias) |
| B11 | `docs/operational-guide.md` | 111 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B12 | `docs/troubleshooting.md` | 195 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |
| B13 | `docs/diagrams/despliegue.md` | 21 | `Automatizacion_Mesa_de_Ayuda.json` → `n8n/workflow.json` |

**Grupo C — Archivos que referencian `twilio/`:**

| # | Archivo | Linea(s) | Cambio |
|---|---------|----------|--------|
| C1 | `n8n/twilio/README.md` | 62, 74 | `twilio/twiml.xml` → `n8n/twilio/twiml.xml` (ya se movio, actualizar referencias internas) |
| C2 | `openspec/specs/project-structure/spec.md` | 67 | `twilio/README.md` → `n8n/twilio/README.md` |

**Grupo D — Correccion de `.env.example`:**

| # | Archivo | Linea | Cambio |
|---|---------|-------|--------|
| D1 | `.env.example` | 3 | `Gestion_Incidentes/.env` → `App/Backend/.env` |

### Fase 4: Verificar

7. Ejecutar tests del backend: `cd App/Backend; pytest tests/test_n8n_workflow.py -v` (verifica que el path al JSON del workflow funciona).
8. Ejecutar `docker compose config` para validar que el compose sigue siendo valido.
9. Buscar referencias huerfanas: `rg "ANEXO_H_Prompt_Gemini_Especificacion" --glob '!openspec/changes/archive/**'` y `rg "Automatizacion_Mesa_de_Ayuda\.json" --glob '!openspec/changes/archive/**'` deben dar cero resultados (fuera de archived changes).
10. Revisar `git status` para confirmar que los 4 archivos se movieron correctamente.

## Riesgos / Trade-offs

- **[Riesgo] Rotura de CI**: Los tests en CI usan `WORKFLOW_PATH` calculado con `parents[3]`. Con el archivo movido a `n8n/workflow.json`, `parents[3]` desde `App/Backend/tests/` sigue siendo la raiz del repo. El path relativo cambia pero `Path(__file__).resolve().parents[3] / "n8n/workflow.json"` es correcto. → **Mitigacion**: ejecutar tests antes de commitear.
- **[Riesgo] Docker volume mount roto**: El cambio en `docker-compose.yml` de `./Automatizacion_Mesa_de_Ayuda.json` a `./n8n/workflow.json` debe ser exacto. → **Mitigacion**: `docker compose config` valida la sintaxis.
- **[Riesgo] Referencias olvidadas**: Algun archivo puede tener una referencia que no se detecto en el analisis. → **Mitigacion**: grep post-move para confirmar cero referencias huerfanas en archivos activos.
- **[Trade-off] Nombre `workflow.json`**: Generico, pero es el unico workflow. Si en el futuro se agregan mas, se renombra. La alternativa (`mesa-de-ayuda.json`) es prematura.
- **[Trade-off] Archived changes**: No se actualizan, lo que significa que los archived changes de C-16 mencionan `twilio/twiml.xml` que ya no existe en ese path. Esto es aceptable: los archived changes son historicos y reflejan el estado del repo EN ESE MOMENTO. La spec principal (`project-structure`) SI se actualiza.

## Open Questions

Ninguna. El plan es deterministico y todos los archivos afectados estan identificados. El unico punto de decision del usuario es `docs/Comandos_para_iniciar_proyecto.txt`, que se deja sin cambios.
