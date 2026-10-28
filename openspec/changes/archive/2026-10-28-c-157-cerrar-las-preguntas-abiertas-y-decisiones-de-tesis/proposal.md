## Why

El registro de preguntas abiertas de la base de conocimiento y el ledger del dictamen conservan entradas que ya no se corresponden con el estado real del sistema y de la tesis: la pregunta IN-03 describe una divergencia de driver de base de datos que la version de trabajo de la tesis ya no exhibe, la pregunta IN-06 describe el workflow N8N con un disparador Outlook, un agente de IA y Redis que el artefacto ya no usa, la pregunta SU-05 sobre Kubernetes sigue abierta pese a que el autor decidio (B2) tratarlo como aspiracional, y el ledger anota el timeout O8 como pendiente "fuera de la tesis" cuando ya esta cerrado en el codigo y en la configuracion. Ademas, el capitulo de recomendaciones remite en su introduccion a cuatro lineas de trabajo futuro, pero solo dos tienen subseccion. Cerrar estas entradas evita que un lector o un auditor tomen por vigente un estado ya superado y completa la remision interna del capitulo de recomendaciones.

## What Changes

- Cerrar IN-06 en `knowledge-base/10_preguntas_abiertas.md`: actualizar la descripcion del workflow N8N a la arquitectura vigente (disparador IMAP, clasificacion embebida en el backend, sin agente de IA de LangChain ni Redis en el canal telefonico) y marcar la divergencia como reconciliada, preservando el texto original como antecedente historico rotulado.
- Cerrar IN-03 en `knowledge-base/10_preguntas_abiertas.md`: marcar la divergencia de driver como resuelta, dejando constancia verificable de que la tesis vigente ya declara `SQLAlchemy 2.0 async` con `asyncpg` (`docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex:74`) y de que la decision DD-08 ya la confirma.
- Reforzar la reconciliacion de IN-03 en el Anexo C de la tesis (`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`): agregar una nota factica que declare que la capa de acceso a datos usa `SQLAlchemy 2.0 async` con `asyncpg`, consistente con el codigo y con la Seccion 5.4.
- Cerrar la observacion O8 del ledger del dictamen en `docs/Tesis/Correcciones/dictamen-correcciones.md`: agregar una nota fechada que la marque como RESUELTA, con la evidencia verificable (`openspec/config.yaml` con `timeout_s: 30` y `total_timeout_s: 60`; `CLAUDE.md` remitiendo a esa seccion en lugar de repetir el valor).
- Marcar SU-05 (B2) como RESUELTA en `knowledge-base/10_preguntas_abiertas.md`: la migracion a Kubernetes queda declarada como aspiracional y fuera de alcance, consistente con la narrativa de la tesis que ya la presenta como trabajo futuro.
- Agregar en `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` (B1) las dos subsecciones faltantes que la introduccion del capitulo anticipa: la integracion con sistemas externos de inventario de activos y gestion de configuracion, y la automatizacion de la etapa de resolucion tecnica, con una subseccion y una etiqueta por linea, en un parrafo academico neutral cada una.
- Dejar registrado que las ediciones de los `.tex` (items de Anexo C y de recomendaciones) exigen recompilar el PDF en una release posterior a `v1.2.4`; la recompilacion NO forma parte de este change.
- No hay cambios en codigo de aplicacion, en los cinco identificadores canonicos de sector, en los valores de `gemini-3.6-flash`, en `requirements.txt` ni en `openspec/config.yaml`.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `project-documentation`: se agregan requisitos de cierre de las entradas stale de `knowledge-base/10_preguntas_abiertas.md` (driver de base de datos IN-03, workflow N8N IN-06 y alcance de Kubernetes SU-05), declarando la reconciliacion con evidencia verificable y preservando el texto original como antecedente rotulado.
- `tesis-document`: se agregan requisitos de cierre documental en la tesis: la nota del driver en el Anexo C, las dos subsecciones faltantes del capitulo de recomendaciones y la coherencia de la narrativa de Kubernetes con su tratamiento aspiracional, ademas de la anotacion fechada que cierra la observacion O8 en el ledger del dictamen.

## Impact

Solo documentacion: `knowledge-base/10_preguntas_abiertas.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md`, `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` y `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`. Sin impacto en API, dependencias, base de datos, runtime ni en la barrera `scripts/preflight/docs_stack_sync.py`. Las ediciones de los `.tex` requieren una recompilacion diferida del PDF (`docs/Tesis/v10 (IA)/paper/main.pdf`) en una release posterior a `v1.2.4`, fuera del alcance de aplicacion de este change.
