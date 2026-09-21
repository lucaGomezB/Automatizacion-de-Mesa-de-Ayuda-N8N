## Why

El change c-24 movió el módulo Python de `Gestion_Incidentes/` a `App/Backend/`, pero varios documentos vigentes todavía presentan `Gestion_Incidentes/` como ubicación actual del módulo, de su `.env` y de sus comandos. Esas rutas son obsoletas y engañosas: quien sigue la guía operativa o la de troubleshooting copia o edita rutas inexistentes. En paralelo, la documentación de variables de entorno quedó incompleta: ni la tabla del `README.md` ni el bloque dotenv de la guía operativa (sección 1.2) mencionan `JWT_SECRET_KEY`, aunque el preflight de bootstrap ya la exige y el propio README la nombra en prosa (c-42). El resultado es una inconsistencia interna y una deuda de exactitud documental.

## What Changes

- Reemplazar las referencias obsoletas a `Gestion_Incidentes/` por la ruta vigente `App/Backend/` en los documentos que describen la ubicación actual del módulo, la configuración de entorno y los comandos.
- **Excepción histórica**: en `docs/security-hardening.md` el token aparece en la narrativa de un incidente real pasado (el archivo estaba realmente en `Gestion_Incidentes/.env`). El hecho MUST conservarse y anotarse como ruta histórica; no se reescribe la historia.
- Añadir `JWT_SECRET_KEY` a la tabla de variables de entorno del `README.md` (sección "Configurar las variables de entorno"), con descripción de clave de firma HS256 y comando de generación.
- Añadir `JWT_SECRET_KEY` al bloque dotenv de `docs/operational-guide.md` (sección 1.2).
- Verificar cada reemplazo contra la estructura real del repo (`App/Backend/scripts/export_openapi.py`, `App/Backend/requirements.txt`, imports del módulo de evaluación) en lugar de sustituir a ciegas.
- Añadir una red de seguridad estructural (test) que falle si la documentación vuelve a desincronizarse.
- Change documental atómico: no toca código de producción, scripts, `n8n/workflow.json` ni el texto de tesis bajo `docs/Tesis/**`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-documentation`: el requisito "Anexo G — Guía operativa" suma que la sección 1.2 liste `JWT_SECRET_KEY` y que los comandos usen rutas post-reestructuración; el requisito "README de despliegue local reproducible" suma que la tabla de variables de entorno liste `JWT_SECRET_KEY`; se agrega un requisito nuevo de consistencia de rutas post-reestructuración.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `README.md` (sección 2, tabla de variables) | Modified | Se agrega `JWT_SECRET_KEY` a la tabla de entorno |
| `docs/operational-guide.md` (líneas 43, 46, 372, 383; sección 1.2) | Modified | Rutas `Gestion_Incidentes/` → `App/Backend/`; `JWT_SECRET_KEY` en el bloque dotenv |
| `docs/troubleshooting.md` (líneas 25, 27, 85, 152) | Modified | Rutas `Gestion_Incidentes/.env` → `App/Backend/.env` |
| `docs/como_cargar_datos_corpus.md` (línea 189) | Modified | `PYTHONPATH` ajustado a la ruta vigente |
| `docs/diagrams/componentes.md` (línea 3) | Modified | Ruta del módulo en capas |
| `docs/parameters_gemini.md` (línea 59) | Modified | Ruta del clasificador Gemini |
| `docs/pseudonymization.md` (línea 4) | Modified | Ruta del módulo de pseudonimización |
| `docs/anexo_c_esquema_bd.md` (líneas 4, 5) | Modified | Rutas de modelos y migraciones (Anexo C) |
| `docs/security-hardening.md` (línea 179) | Modified | Solo anotación de ruta histórica; el hecho no se altera |
| `App/Backend/tests/` (test estructural) | New/Modified | Assertions sobre README y docs; control negativo de `Gestion_Incidentes/` |
| `docs/Tesis/**` | Out of scope | Texto de tesis excluido del change |

Sin cambios en API, esquema de datos, dependencias, infraestructura ni scripts de runtime.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reescribir a ciegas y apuntar a una ruta que no existe | Med | Verificar cada destino contra el repo real antes de reemplazar (tarea explícita de verificación) |
| Borrar el hecho histórico de `docs/security-hardening.md` | Low | Anotar la ruta como histórica; no eliminar el token ni reescribir la narrativa |
| Test estructural acopla la suite a prosa | Med | Asserts solo sobre tokens estables (rutas, `JWT_SECRET_KEY`), no sobre oraciones |
| Desliz de alcance hacia `docs/Tesis/**` | Low | Declarado explícitamente fuera de alcance; el control negativo excluye ese directorio |

## Rollback Plan

Revertir el commit de documentación y eliminar el test estructural. No hay cambios de runtime, esquema ni infraestructura, por lo que no existe estado que restaurar.

## Success Criteria

- [ ] Ningún documento vigente (fuera de la anotación histórica) presenta `Gestion_Incidentes/` como ruta actual.
- [ ] `README.md` y `docs/operational-guide.md` (sección 1.2) listan `JWT_SECRET_KEY`.
- [ ] El test estructural pasa en verde y su control negativo cubre el token obsoleto.
- [ ] `cd App/Backend; pytest -m "not integration" -q` no reporta regresiones.
- [ ] `openspec validate --strict --changes c-43-docs-restructure-sync` pasa.