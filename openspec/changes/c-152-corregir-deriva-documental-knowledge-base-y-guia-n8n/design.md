## Context

Ver `proposal.md - Why`. Dos hallazgos de deriva documental, verificados el 2026-10-28 contra `openspec/changes/archive/` y `CHANGES.md`:

1. `knowledge-base/07_flujos_principales.md` (lineas 11, 26 y 36) y `knowledge-base/10_preguntas_abiertas.md` (lineas 41, 43 y 45) rotulan los changes `C-02`, `C-04`, `C-05` y `C-17` como pendientes. Los cuatro figuran archivados: `2026-06-10-c-02-notify-n8n-hook`, `2026-06-11-c-04-n8n-workflow-validation`, `2026-06-11-c-05-n8n-channel-triggers` y `2026-07-02-c-17-evaluation-corpus-simulado`. Las preguntas correspondientes ya estan resueltas.

2. `docs/n8n-workflow-guide.md:767` cita `N8N 2.25.7` dentro del bloque "Resultados de verificacion 7.1-7.6 (2026-06-11, C-05)", mientras el compose fija `n8nio/n8n:2.11.2`.

Restricciones que moldean el enfoque:
- La barra de sincronizacion documental (`scripts/preflight/docs_stack_sync.py`) limita el barrido de N8N a `knowledge-base/**`; el material de referencia solo se escanea para `google-genai` (decision de c-151). Por eso el hallazgo 2 no la rompe, pero sigue siendo una incoherencia para el lector.
- El requisito existente "Anotacion fechada de los registros historicos sin reescritura" prohibe reescribir registros historicos: la correccion debe preservar el texto original.
- La barrera reconoce un pasaje como historico si la linea o el encabezado de su seccion contiene un token de `MARCADORES_HISTORICOS` (`historico`, `historica`, `antecedente`, `superad`, `migro`, `migrado`, `retirado`, `previo`, `calibrad`).

## Goals / Non-Goals

**Goals:**
- Alinear el estado declarado en la base de conocimiento con el estado real de archivado de los changes referenciados.
- Rotular el registro de verificacion N8N 7.1-7.6 como historico con un marcador reconocido, conservando el texto original.
- Mantener la coherencia con el patron ya usado en la guia (el bloque hermano 8.1-8.3 lleva una "Nota historica" en la linea 575).

**Non-Goals:**
- No ampliar el alcance de `scripts/preflight/docs_stack_sync.py` ni crear un chequeo 18.
- No corregir la version `2.25.7` a `2.11.2` (no es un typo).
- No tocar codigo de aplicacion, `requirements.txt`, `openspec/config.yaml` ni los identificadores canonicos.

## Decisions

### D1. La version 2.25.7 es un hecho historico, no un typo

`git log -S "2.25.7" -- docs/n8n-workflow-guide.md` lo rastrea al commit `5d06268` (2026-06-11, "fix(c-05): verificacion funcional 7.1-7.6"). En esa fecha el compose aun no fijaba la imagen: el pin `n8nio/n8n:2.11.2` llego con C-34 (2026-09-17). El bloque hermano 8.1-8.3, de la misma fecha, ya lo aclara: "en esa verificacion se uso una imagen `latest`; el compose vigente fija `n8nio/n8n:2.11.2` (pin C-34)" (linea 575). Por lo tanto `2.25.7` fue la version real del tag `latest` observada en la verificacion; el defecto es la AUSENCIA de rotulacion historica, no el valor.

Alternativas consideradas: (a) reemplazar `2.25.7` por `2.11.2` — RECHAZADA, falsifica un registro historico fechado y contradice el requisito de no reescritura; (b) dejar el bloque como esta — RECHAZADA, mantiene la ambiguedad de que el lector lo tome como vigente.

### D2. Rotular via el encabezado de seccion, no via la linea suelta

La barrera evalua `_tiene_marcador(linea) or _tiene_marcador(encabezado)`. El encabezado del bloque (`### Resultados de verificacion 7.1-7.6 (2026-06-11, C-05)`) no contiene marcador. La correccion SHALL incorporar un token reconocido en el encabezado (por ejemplo, `Resultados de verificacion historicos 7.1-7.6 (2026-06-11, C-05)`) para que toda la seccion —incluida la linea de la version— quede rotulada como historica, siguiendo el patron del bloque 8.1-8.3.

Alternativa considerada: agregar una "Nota historica" en la linea 767 — descartada como unica medida, porque marca solo esa linea y no la seccion; se puede combinar como refuerzo, pero el encabezado es la pieza robusta.

### D3. Tratamiento de las referencias stale de la base de conocimiento

Para `07_flujos_principales.md`:
- Linea 11: `*(Pendiente C-02)* notify_n8n()` se corrige a su estado real (implementado, C-02 archivado), sin borrar el hecho de que en su momento estaba pendiente.
- Lineas 26 y 36: los encabezados "(pendiente C-04/C-05)" y "(pendiente C-05)" se corrigen al estado de implementacion real. Los flujos de correo y telefonia ya estan implementados (C-55, C-52, C-53), por lo que corresponde declararlos implementados con su change vigente.

Para `10_preguntas_abiertas.md` (tabla de preguntas abiertas):
- Linea 41 (CSV del corpus, "Resuelto... C-17"): confirmar el marco de resuelto.
- Linea 43 (credenciales Outlook/Twilio, bloquea `C-05`): C-05 archivado; el transporte de correo fue redefinido en C-55 (IMAP/App Password) y las credenciales se gestionan fuera del alcance del change. Marcar resuelta/cerrada.
- Linea 45 (instancia N8N de pruebas, bloquea `C-02`): C-02 archivado; marcar resuelta.

Regla de edicion: se preserva el texto original como evidencia cuando aporta contexto historico, y se corrige el marco de estado; no se elimina la fila ni el hecho previo.

## Risks / Trade-offs

- [Reescribir un registro historico (violacion de la regla dura)] -> La correccion se limita a rotular y corregir marcos de estado; el texto original del bloque N8N y de las afirmaciones de estado se conserva. Verificacion por inspeccion del diff.
- [Rotular de mas y exemptar lineas que si requieren vigilancia] -> El marcador se coloca en el encabezado del bloque 7.1-7.6 y solo aplica a esa seccion; no se toca el encabezado de la seccion de version vigente de la guia (linea 505 ni vecinas). El barrido de N8N de la barrera no cubre `docs/`, de modo que no hay riesgo de enmascarar un hallazgo activo.
- [Corregir un estado que en realidad sigue pendiente] -> Se verifico contra `openspec/changes/archive/` y `CHANGES.md`: C-02, C-04, C-05 y C-17 estan archivados. La tarea incluye re-verificar el estado antes de editar.

## Migration Plan

No aplica migracion: son ediciones de documentacion, sin despliegue. Rollback: `git checkout` de los tres archivos. No hay datos ni esquemas afectados.

## Open Questions

Ninguna.
