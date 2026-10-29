## Context

Ver `proposal.md - Why`. Los cinco residuales estan documentados en `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada de c-158, "deriva fuera de la tesis", linea ~3188) y en la nota "fuera de alcance" del design archivado de c-158 (`openspec/changes/archive/2026-10-29-c-158-.../design.md:179`). Ninguno esta cubierto por c-161/162/163.

Estado vigente del codigo (fuente de la verdad):
- `scripts/corpus_ingest/ingest_telefonia_corpus.py:9,88-112`: `t_pipeline_s = t_e2e_s = duracion_segundos + latencia_e2e_ms / 1000`, `t_espera_s = None`.
- `openspec/specs/evaluation-framework/spec.md:354-374`: ya declara la formula c-77 para el corpus.
- `App/Backend/app/services/incidente_service.py:411-417`: `requiere_revision = bool(result.requiere_revision_humana) or (reportante_empleado_id is None)`.
- `openspec/config.yaml:42`: el umbral 0.70 aplica "solo sobre la salida de Gemini".

## Goals / Non-Goals

**Goals:**
- Alinear el spec `telefonia-corpus-medicion` con la formula c-77 y reconciliar la descomposicion.
- Alinear los tres documentos de `docs/` y el comentario del modelo con el comportamiento vigente.
- Registrar el cierre en el ledger del dictamen y abrir la FASE 51.

**Non-Goals:**
- NO cambiar logica en `App/` (el unico cambio de codigo es un comentario).
- NO tocar `n8n/`, `evaluation/`, `openspec/config.yaml`, las cinco cadenas canonicas, los numeros canonicos ni `docs/Tesis/v9 (IA)/`.
- NO modificar `openspec/specs/e2e-timing-instrumentation/spec.md` (instrumenta `ingresado_en`/`persistido_en`/`latencia_e2e_ms`, no la derivacion del tiempo telefonico; no cambia).

## Decisions

### D1 — Delta spec acotado a "Metrica canonica de telefonia"

Se usa MODIFIED con el bloque COMPLETO del requirement (incluyendo los TRES escenarios existentes, con sus nombres EXACTOS: "Metrica canonica identica a los otros canales", "Espera no medible en telefonia", "Caso anomalo excluido"). El nombre del primer escenario se conserva aunque la telefonia ya no sea literalmente "identica" (ahora suma la duracion): la convencion de archive exige preservar los nombres para no perder detalle. El requirement "Write-back al corpus" (`t_pipeline_s = t_e2e_s`) sigue siendo valido sin cambio.
- Alternativa considerada: renombrar el escenario. Descartada por la regla de MODIFIED (perdida de detalle al archivar).

### D2 — Descomposicion: la telefonia SUMA la grabacion

`t_e2e_s = t_pipeline_s = duracion_segundos + latencia_e2e_ms / 1000`. El componente de pipeline es la misma latencia end-to-end de los demas canales; la diferencia conceptual (Opción A de c-77) es que se agrega `duracion_segundos` para igualar la base de comparacion con el tiempo manual. La cota inferior (45 s del `<Record maxLength="45">`) se declara explicitamente.

### D3 — Comentario de `requiere_revision_humana`

Solo el comentario (lineas ~233-235 de `models/incidente.py`) se reescribe: el 0.70 aplica SOLO a la etapa Gemini; el deterministico no deriva por su confianza (cortocircuita por score); el fallback siempre deriva; y desde 2026-10-13 el backend tambien deriva cuando el reportante no esta identificado (c-82, VIS-005). Ninguna linea de logica se modifica.

### D4 — Anexo C: `directorio_empleado` + `directorio_auditoria`

Se agrega la tabla `directorio_empleado` (columnas de `empleado.py`: legajo, nombre, email/telefono con `EncryptedText` Fernet, `email_bidx` UNIQUE / `telefono_bidx` del indice ciego HMAC-SHA-256 de c-153, `sector_id` FK SET NULL, `rol` CHECK de CUATRO valores, `activo`, `fecha_baja`, `user_id` FK SET NULL, timestamps) y se incluye `directorio_auditoria` (traza append-only de c-153/DIR-013: `operacion`, `resultado`, `canal`, `empleado_id`, `actor_empleado_id`, `created_at`). Se respetan las secciones y el estilo existentes (bloque SQL + "Relaciones" + filas del resumen de ON DELETE).
- Alternativa considerada: omitir `directorio_auditoria` por ser tabla de auditoria. Descartada: es parte del modelo de datos entregado (migracion 023, c-153) y del mismo endurecimiento del directorio que este item documenta.

### D5 — Hash canonico en `numeros-canonicos.md`

La fila "Predicciones oficiales" (linea ~390) se ajusta para que el hash "vigente" sea el blob LF `89cf956e82f660dd8675a2d23b7b4d17efd62da542c0ba35bea28e0e54572ede`, conservando la nota del CRLF `3fb5bacd04f2e9d303f580e4cf2ac4b4c6f2eab628a4fff80a6e1238029cd8fd` (hoy citado por la procedencia de la evidencia). El memo ya lo explica en la seccion ~686-691; se alinea la fila con esa explicacion. NO se cambia ningun valor numerico canonico.
- Alternativa considerada: reemplazar el hash CRLF. Descartada: la procedencia de la evidencia (`evaluation/report.md:5`) lo cita; se conserva como nota historica.

## Risks / Trade-offs

- [El comentario reescrito contradice el codigo] → El texto se transcribe del `incidente_service.py:411-417` y de `openspec/config.yaml:42`; se verifica por lectura.
- [MODIFIED pierde escenarios] → Se copia el bloque completo con los tres nombres EXACTOS; `openspec validate --strict` lo verifica.
- [Anexo C desincronizado del modelo] → Se copian columnas literales de `empleado.py`/`directorio_auditoria.py`; el bloque SQL se redacta en el estilo del documento.
- [Romper la barrera documental] → `docs_stack_sync.py` no lee estos archivos; se corre tras los cambios y debe quedar 17/17 PASS.

## Migration Plan

1. Editar la documentacion y el comentario (sin runtime).
2. Sincronizar el delta spec al spec principal al archivar (o via sync).
3. Rollback: `git checkout --` de los archivos tocados; sin efecto en runtime ni release.

## Open Questions

- Ninguna que cambie los specs, el enfoque o las tareas. La unica ambiguedad (`directorio_auditoria` en Anexo C) se resuelve en D4: se incluye, por ser parte del modelo entregado.
