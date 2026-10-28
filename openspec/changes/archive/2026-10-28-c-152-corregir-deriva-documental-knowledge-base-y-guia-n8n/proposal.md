## Why

La base de conocimiento y la guia del workflow N8N siguen presentando como trabajo pendiente cambios que ya fueron completados y archivados (C-02, C-04, C-05, C-17), y un bloque de verificacion historico de la guia cita la version de N8N sin ningun marcador historico reconocido. Esa deriva documental induce a error al lector y al auditor sobre el estado real del proyecto, y contradice la regla de que la documentacion declarada como vigente sea reproducible desde el repositorio.

## What Changes

- Corregir el marco de estado en `knowledge-base/07_flujos_principales.md`: las referencias a `C-02`, `C-04` y `C-05` como "pendiente" se actualizan al estado real (completado y archivado), conservando integro el contexto genuinamente historico.
- Corregir el marco de estado en `knowledge-base/10_preguntas_abiertas.md`: las preguntas resueltas por `C-17` (CSV del corpus), `C-05` (credenciales Outlook/Twilio y verificacion funcional de canales) y `C-02` (instancia N8N de pruebas) se marcan como resueltas, sin borrar el texto original.
- Anotar el bloque "Resultados de verificacion 7.1-7.6 (2026-06-11, C-05)" de `docs/n8n-workflow-guide.md` con un marcador historico reconocido por `MARCADORES_HISTORICOS`, para que `N8N 2.25.7` no se lea como la version vigente (el compose fija `n8nio/n8n:2.11.2`), conservando el registro sin reescribirlo.
- No hay cambios en codigo de aplicacion, en los cinco identificadores canonicos de sector, en los valores de `gemini-3.6-flash`, en `requirements.txt` ni en `openspec/config.yaml`.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `project-documentation`: se agregan requisitos de coherencia de estado de los changes en la base de conocimiento y de rotulacion historica del bloque de verificacion del workflow N8N.

## Impact

Solo documentacion: `knowledge-base/07_flujos_principales.md`, `knowledge-base/10_preguntas_abiertas.md` y `docs/n8n-workflow-guide.md`. Sin impacto en API, dependencias, base de datos ni runtime. La barrera `scripts/preflight/docs_stack_sync.py` no cambia de alcance: la version de N8N del material de referencia queda fuera de su barrido de N8N, por lo que la correccion es documental y de coherencia, no una ampliacion del preflight.
