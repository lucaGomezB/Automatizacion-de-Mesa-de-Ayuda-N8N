## Why

La documentacion de cumplimiento quedo desfasada respecto del codigo y de los changes ya archivados: el `gap-assessment` sigue declarando como ausentes controles que C-61 a C-66 implementaron, y varios documentos de `docs/seguridad/` conservan referencias a Redis, a C-63/C-67 como pendientes y al minimizacion del directorio como justificacion vigente. Esa deriva debilita la evidencia de la tesis y puede hacer que un lector (o un evaluador) concluya que el sistema no implementa controles que si existen.

## What Changes

- Reconciliar `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` con el estado vigente: agregar un "Registro de estado vigente" (control -> estado -> evidencia -> residual -> change archivado) y corregir las afirmaciones obsoletas de MFA, Redis, politicas, inventario, clasificacion, proveedores, plan de IR, SAST/pip-audit y retencion de logs. No se debilitan los residuales reales del adoptante (5.35, 8.14, offsite, contratos con proveedores).
- Agregar un lint documental hermetico (test pytest) que valide encabezados y secciones requeridas, termine prohibidos de certificacion/conformidad y completitud del indice y de las referencias cruzadas de `docs/seguridad/`, ejecutado por la suite de backend (sin cambios en `ci.yml`).
- Corregir referencias cruzadas obsoletas en `inventario-activos-informacion.md`, `README.md` de `docs/seguridad/` y `registro-actividades-tratamiento.md` (Redis retirado, Microsoft Outlook inactivo, C-63 archivado como c-63a/b/c, C-62..C-67 ya cerrados, justificacion superada por `adr-001-...` + `clasificacion-etiquetado-informacion.md`).
- Corregir la afirmacion de la tesis sobre MFA y rotacion de claves (`v10` y `v9`), distinguiendo "implementado en el repositorio" de "KMS/PAM y produccion como accion del adoptante", y registrar que el PDF debe recompilarse (release vigente v1.2.3).
- Implementar el aviso de privacidad del saludo telefonico en el TwiML (`cost_guard/twiml.py`) con prueba automatizada, en lugar de dejarlo como requisito solo documentado.
- Agregar una seccion de manejo de evidencia y cadena de custodia (control 5.28) en el plan de respuesta a incidentes y en la politica de retencion de logs.
- Agregar `docs/seguridad/inventario-licencias.md` con el inventario de dependencias y licencias del proyecto (control 5.32).

## Capabilities

### New Capabilities

_(ninguna)_

### Modified Capabilities

- `security-governance-docs`: se agregan requisitos de reconciliacion continua del gap assessment, lint documental, manejo de evidencia (5.28) e inventario de licencias (5.32), y se ajusta la trazabilidad del indice a los changes archivados.
- `privacy-runtime-surface`: se agrega el aviso de privacidad en el canal telefonico (saludo TwiML) como superficie de informacion al titular.
- `tesis-document`: se agrega el requisito de declarar el estado real de MFA y rotacion de claves en el capitulo legal, separando lo implementado en el repositorio de lo que queda como accion del adoptante.

## Impact

- Documentacion: `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`, `docs/seguridad/README.md`, `docs/seguridad/inventario-activos-informacion.md`, `docs/seguridad/registro-actividades-tratamiento.md`, `docs/seguridad/politica-privacidad-runtime.md`, `docs/seguridad/plan-respuesta-incidentes-seguridad.md`, `docs/seguridad/politica-retencion-logs.md`, nuevo `docs/seguridad/inventario-licencias.md`.
- Codigo: `App/Backend/app/cost_guard/twiml.py` (texto del saludo) y `App/Backend/tests/test_twiml_record.py` (o un test dedicado al aviso).
- Pruebas nuevas: `App/Backend/tests/test_compliance_docs_lint.py` (hermetico, sin servicios externos).
- Tesis (fuente LaTeX, sin recompilar en este change): `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` y su gemelo `docs/Tesis/v9 (IA)/...`. Requiere recompilar el PDF y publicar una release de correccion posterior (v1.2.3 ya publicada; el rebuild se registra como tarea).
- CI: sin cambios en `.github/workflows/ci.yml`; el lint corre dentro del job `backend-tests` porque es un test pytest mas.
- Sin cambios en las cinco cadenas canonicas de sector, en `requirements.txt`, en `openspec/config.yaml` ni en parametros de Gemini.
