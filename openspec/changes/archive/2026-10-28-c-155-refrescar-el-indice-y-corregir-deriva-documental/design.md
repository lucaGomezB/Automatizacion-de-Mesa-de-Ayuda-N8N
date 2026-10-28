## Context

Change de higiene documental, governance BAJO. Ver `proposal.md` para la motivacion. El estado verificado contra el repositorio es:

- `CHANGES.md` tiene el formato de `FASE {N}` (encabezado + cita) con entradas `### [C-NNN] \`nombre\` — ESTADO (fecha, governance)`, cada una con bloques **Scope**, **Verificacion**, **Rollback** y **Leer antes**. Las lineas de resumen viven en tres lugares: la seccion "Resumen de Changes" (linea Total y linea Fases) y dos parrafos de "Estado actual" al final.
- El directorio `openspec/changes/archive/` contiene 153 directorios (incluye las partes c-63a/b/c); el unico change activo es este (c-155).
- Estados reales: C-151 ARCHIVADO (`2026-10-28`, commit de archive `30b5648`, 20/20); C-152 ARCHIVADO (`2026-10-28`, `76695e6`, 12/12); C-153 ARCHIVADO (`2026-10-28`, `cab14b1`, 42/42); C-154 ARCHIVADO (`2026-10-28`, `a493083`, 21/21).
- Deriva de la base de conocimiento: `07_flujos_principales.md:31` (placeholder), `07_flujos_principales.md:42-43` (agente Redis/refinamiento, retirados por C-72), `03_actores_y_roles.md:28` (niega el modo SECTOR).
- `docs/por_implementar.md:3` (estado `2026-09-17`) y `:18` (umbral `< 0.90`).

Restricciones duras: espanol neutro, sin emojis, sin U+2713; no tocar los cinco strings canonicos de sectores, ni los valores del stack, ni `requirements.txt`, ni `openspec/config.yaml`, ni codigo.

## Goals / Non-Goals

**Goals:**
- Que `CHANGES.md`, la base de conocimiento y `docs/por_implementar.md` coincidan con el estado verificado del repositorio.
- Preservar los registros historicos: corregir el estado vigente sin reescribir las actualizaciones fechadas ni las entradas fechadas.
- Mantener el formato existente del indice para que el diff sea minimo y determinista.

**Non-Goals:**
- No se modifica codigo ni la barrera `scripts/preflight/docs_stack_sync.py`.
- No se agrega `docs/por_implementar.md` a la superficie vigilada por la barrera (seria cambio de codigo, fuera de alcance); la consistencia de ese documento se verifica a mano contra `settings.py`.
- No se archiva este change (lo hace el flujo de archive una vez aplicado).

## Decisions

- **D1 — Correccion de estado en la linea de la entrada, no nueva entrada historica.** Para C-151 y C-153 se cambia el estado del encabezado de la entrada existente a `ARCHIVADO (2026-10-28, ...)` y se ajusta la cita de la FASE si nombra el estado previo. Alternativa descartada: agregar una nota aparte, que duplicaria el estado y complicaria la lectura.
- **D2 — FASE nueva para C-152 y C-154 en lugar de renumerar.** C-152 y C-154 se archivan el 2026-10-28 pero no encajan en las FASES 44 (C-151) y 45 (C-153) existentes. Se agrega una `FASE 46 — Regularizacion del indice (C-152, C-154)` con sus dos entradas. Alternativa descartada: insertar los changes entre las FASES 44 y 45, que obligaria a renumerar todo el tramo final y multiplicaria el diff.
- **D3 — Flujo 3 reescrito a la arquitectura vigente.** Se reemplazan los pasos 3 y 4 por la resolucion en el backend con `HybridClassifier` (C-72) y se conserva una rotulacion historica del agente retirado, en lugar de borrar la traza. Motivo: el canal existe; lo que cambio es quien clasifica.
- **D4 — Modo SECTOR agregado sin tocar los strings canonicos.** En `03_actores_y_roles.md` se agrega SECTOR a la lista de modos de visibilidad y se reemplaza la afirmacion "el aislamiento por sector NO existe", citando `role_policy.py:38` e `incident_visibility.py`. Los cinco strings de sector se citan igual que hoy.
- **D5 — `por_implementar.md` alineado, con historico rotulado.** Se actualiza la fecha del encabezado y el umbral a los valores vigentes (`0.5166` del cortocircuito y `0.70` de revision humana) verificados en `settings.py`; si una seccion no se puede confirmar, se rotula como historica en lugar de afirmarla.

## Risks / Trade-offs

- **Inconsistencia en las lineas de resumen largas** (Total, Fases, Estado actual) → Mitigacion: recalcular los conteos contra `openspec/changes/archive/` y el unico change activo, y revisar las cuatro ubicaciones en una sola pasada.
- **Perder detalle al reescribir una entrada** → Mitigacion: conservar las actualizaciones fechadas integras; solo se edita el estado del encabezado y lo que lo cite.
- **Introducir un emoji o U+2713** → Mitigacion: barrido final con busqueda de pictogramas sobre los archivos editados.
- **Romper una cita canonica de sector o de stack** → Mitigacion: no tocar los literales de sector ni valores del stack; verificar con el preflight existente.

## Migration Plan

- Aplicacion puramente documental; no hay migracion de datos ni despliegue.
- Rollback: `git revert` del commit documental restituye el indice, la base de conocimiento y `docs/por_implementar.md` al estado previo. No se publica tag ni release.

## Open Questions

Ninguna. Las decisiones de ubicacion (D2) y de alcance (D1, D3, D4, D5) quedan resueltas en este documento.
