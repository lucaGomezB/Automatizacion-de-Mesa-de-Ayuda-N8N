## Why

La tesis define siete anexos (A-G) y un capítulo de implementación que referencian artefactos de documentación todavía marcados como `{A desarrollar}` o inexistentes en disco: el esquema SQL completo (Anexo C), la especificación OpenAPI estática (Anexo D), la descripción del corpus de validación (Anexo F) y la documentación operativa (Anexo G). C-10 es el último change del roadmap (camino crítico C-01→…→C-09→C-10) y cierra esa brecha documental, dejando el proyecto listo para entrega al jurado con un README que permita un despliegue local reproducible en menos de 15 minutos.

## What Changes

- Crear diagramas de arquitectura UML en `docs/diagrams/` (despliegue, secuencia, componentes) en formato texto versionable (Mermaid), cubriendo el Anexo A.
- Generar la especificación OpenAPI 3.1 estática en `docs/openapi.json` **desde la app FastAPI** (no a mano), más un script reproducible y una verificación de sincronía, cubriendo el Anexo D.
- Crear `docs/anexo_c_esquema_bd.md` desde cero con el script SQL completo de las 5 tablas (`sector`, `estado`, `canal_origen`, `incidente`, `clasificacion_log`), sus FKs, índices secundarios y restricciones, derivado de los modelos ORM reales.
- Crear `docs/anexo_f_corpus.md` desde cero describiendo el corpus de validación, su esquema CSV y su naturaleza **sintética/provisional** actual (el corpus real es trabajo de campo futuro).
- Crear `docs/operational-guide.md` (Anexo G) con procedimientos de despliegue, backup, restauración y monitoreo.
- Crear `docs/troubleshooting.md` con una guía de resolución de problemas para operadores.
- Actualizar `README.md` con instrucciones de despliegue local reproducible en menos de 15 minutos.

No hay cambios de código de producción ni de comportamiento del sistema; el único artefacto ejecutable nuevo es el script de generación de `openapi.json` y su verificación de sincronía.

## Capabilities

### New Capabilities
- `project-documentation`: Conjunto de artefactos de documentación técnica y operativa del proyecto (diagramas de arquitectura, OpenAPI estático con verificación de sincronía, esquema SQL del Anexo C, descripción del corpus del Anexo F, guía operativa, guía de troubleshooting y README de despliegue), cada uno con criterios de exactitud verificables contra las fuentes de verdad del repositorio (modelos ORM, app FastAPI, docker-compose, corpus CSV).

### Modified Capabilities
<!-- Ninguna: C-10 no modifica requisitos de capacidades existentes; solo agrega documentación. -->

## Impact

- **Archivos nuevos**: `docs/diagrams/*.mmd` (o `.md` con bloques Mermaid), `docs/openapi.json`, `docs/anexo_c_esquema_bd.md`, `docs/anexo_f_corpus.md`, `docs/operational-guide.md`, `docs/troubleshooting.md`, y un script de generación de OpenAPI (p. ej. `Gestion_Incidentes/scripts/export_openapi.py`).
- **Archivos modificados**: `README.md`.
- **Código**: sin cambios en producción. La generación de `openapi.json` importa la app FastAPI (`app.main:app`) en modo lectura; requiere las env dummies que ya usa CI (`database_url`, `gemini_api_key`, `pseudonymization_encryption_key`).
- **CI**: se añade un chequeo opcional de que `docs/openapi.json` está en sincronía con la app (el spec generado coincide con el commiteado), siguiendo el patrón de jobs de C-09.
- **Dependencias**: ninguna nueva en runtime; la generación usa FastAPI ya presente.
- **Governance**: BAJO. Documentación y un script de solo-lectura; sin riesgo sobre datos de usuario ni lógica de negocio.
