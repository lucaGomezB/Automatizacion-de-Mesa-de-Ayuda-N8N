## Why

El dictamen CONEAU v10/v1.2.5 dejo registrada una "deriva fuera de la tesis" que los changes c-161/162/163 NO cubrieron: cinco residuales donde la documentacion, un spec y un comentario de codigo describen un comportamiento ya superado. El caso central es el spec `telefonia-corpus-medicion`: su requirement "Metrica canonica de telefonia" conserva la formula PRE-c-77, mientras el codigo ya usa `duracion_segundos + latencia_e2e_ms / 1000`. La fuente de verdad quedo desincronizada de la implementacion verificada.

## What Changes

- **Spec `telefonia-corpus-medicion`** (MODIFIED): actualiza "Metrica canonica de telefonia" a la formula c-77 (`duracion_segundos + latencia_e2e_ms / 1000`), reconcilia la descomposicion `t_e2e_s = t_pipeline_s = duracion_segundos + latencia_e2e_ms / 1000`, registra la cota inferior por el tope de 45 s y conserva la espera N-A y la exclusion de anomalos.
- **`docs/medicion-latencia-e2e.md`**: misma correccion de la formula en "Telefonía: descomposición y espera N-A"; aclara el caveat de correo (el "sub-mide" aplica a `latencia_e2e_ms`, NO al valor `tiempo_automatizado_s` del corpus, que es otra cantidad).
- **`App/Backend/app/models/incidente.py`** (solo comentario): `requiere_revision_humana` se reescribe para reflejar el comportamiento real (el 0.70 aplica SOLO a la salida de Gemini; el deterministico NO deriva por su confianza; el fallback siempre deriva; y desde 2026-10-13 tambien deriva con reportante no identificado, c-82/VIS-005).
- **`docs/anexo_c_esquema_bd.md`**: agrega la tabla `directorio_empleado` (columnas, cifrado Fernet de email/telefono + indice ciego de c-153, vocabulario `rol` de cuatro valores, FK) y, si corresponde, `directorio_auditoria`.
- **`docs/Tesis/Correcciones/numeros-canonicos.md`**: aclara la fila "Predicciones oficiales" para que el hash "vigente" sea el blob LF `89cf956e...`, conservando la nota del CRLF `3fb5bacd...`.
- **Registro**: cierre en `docs/Tesis/Correcciones/dictamen-correcciones.md` y FASE 51 en `CHANGES.md`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `telefonia-corpus-medicion`: el requirement "Metrica canonica de telefonia" cambia su formula canonica y su descomposicion de tiempo (la telefonia ahora SUMA la duracion de la grabacion, Opción A de c-77).

## Impact

- Docs: `docs/medicion-latencia-e2e.md`, `docs/anexo_c_esquema_bd.md`, `docs/Tesis/Correcciones/numeros-canonicos.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md`, `CHANGES.md`.
- Spec: `openspec/specs/telefonia-corpus-medicion/spec.md` (via delta).
- Codigo: `App/Backend/app/models/incidente.py` (UN comentario; sin cambio de logica).
- Barrera: `scripts/preflight/docs_stack_sync.py` NO lee ninguno de estos archivos; se verifica que siga en 17/17 PASS.
- Sin cambio de runtime, release, ni valores canonicos numericos.
