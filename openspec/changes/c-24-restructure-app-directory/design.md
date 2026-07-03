## Context

El repositorio `Automatizacion-de-Mesa-de-Ayuda-N8N` es un anexo de tesis universitaria (UTN-FRM 2026). Contiene 18 cambios OPSX archivados y 3 activos. Los componentes principales — backend FastAPI (`Gestion_Incidentes/`) y frontend React (`Frontend/`) — estan en la raiz del repositorio. Para presentacion academica, ambos deben agruparse bajo `App/`.

### Restricciones
- Git debe preservar el historial de ambos directorios (usar `git mv`, no copia + delete).
- Docker Compose debe seguir levantando el sistema exactamente igual tras el cambio.
- El pipeline CI (GitHub Actions) debe ejecutarse sin modificaciones a la logica de los jobs, solo actualizando paths.
- Las suites de test no deben romperse (usan imports relativos dentro de cada proyecto, no paths absolutos al repo).
- Los 3 cambios OPSX activos (C-19, C-20, C-23) deben quedar documentados como "actualizar tras C-24".
- El codigo fuente interno de ambos proyectos NO se modifica.

## Goals / Non-Goals

**Goals:**
- Agrupar backend y frontend bajo `App/Backend/` y `App/Frontend/` respectivamente.
- Actualizar TODOS los archivos de configuracion y documentacion que referencian las rutas viejas.
- Mantener el sistema 100% funcional tras la reestructuracion (Docker, CI, tests, N8N).
- Crear delta specs para los specs principales que referencian rutas.
- Documentar en los cambios activos que deben actualizarse post-C-24.

**Non-Goals:**
- Modificar codigo fuente de backend o frontend.
- Cambiar la estructura interna de `evaluation/`, `data/`, `docs/`, `openspec/`, `knowledge-base/`, `scripts/`, `twilio/`.
- Crear nuevos directorios raiz.
- Modificar `.engram/` o `.opencode/`.
- Alterar `Automatizacion_Mesa_de_Ayuda.json` (workflow N8N).
- Cambiar convenciones de naming, imports, o patrones de codigo.

## Decisions

### Decision 1: Usar `git mv` para mover directorios

**Alternativa considerada**: Copiar directorios, eliminar originales, hacer commit. Esto pierde el historial de git (los archivos aparecen como "nuevos"). `git mv` preserva el historial porque git detecta el rename.

**Racional**: Para una tesis, el historial de commits es evidencia del proceso de desarrollo. Perderlo debilitaria la trazabilidad del trabajo. `git mv` es la unica opcion que mantiene `git log --follow` funcionando.

### Decision 2: Nombre `App/Backend/` en lugar de `App/Gestion_Incidentes/`

**Alternativa considerada**: Mantener `Gestion_Incidentes` como nombre del subdirectorio (`App/Gestion_Incidentes/`). Rechazado porque:
- El nombre `Gestion_Incidentes` es un artefacto historico de cuando el proyecto era solo backend.
- `App/Backend/` y `App/Frontend/` son nombres estandar, inmediatamente entendibles para un evaluador academico.
- La tesis ya refiere a estos componentes como "backend" y "frontend".

### Decision 3: Orden de operaciones — mover primero, editar despues

**Racional**: Si editamos archivos primero (cambiando paths a `App/Backend/`) y luego movemos directorios, los paths en los archivos apuntarian a ubicaciones que no existen durante el periodo entre edicion y movimiento. Esto rompe el build. En cambio, si movemos primero y editamos despues en el mismo commit, el estado intermedio nunca existe en el historial.

**Orden de operaciones dentro del commit**:
1. `git mv Gestion_Incidentes App/Backend`
2. `git mv Frontend App/Frontend`
3. Editar todos los archivos de configuracion con los nuevos paths
4. Commit unico con mensaje descriptivo

### Decision 4: Delta specs MODIFIED en lugar de editar specs principales directamente

**Alternativa considerada**: Editar los specs principales directamente sin pasar por delta specs. Rechazado porque:
- Los delta specs son el mecanismo estandar de OPSX para cambios en specs existentes.
- El proceso de archive sincronizara automaticamente los deltas con los specs principales.
- Mantiene trazabilidad de QUE cambio y POR QUE.

Los specs principales afectados son:
- `foundation-environment` — 3 referencias a paths
- `ci-pipeline` — 7 referencias a paths
- `project-documentation` — 2 referencias a paths
- `frontend-testing` — 2 referencias a paths

## Risks / Trade-offs

- **[Riesgo] Docker volume paths en Windows**: Los volumenes en `docker-compose.yml` usan paths relativos (`./App/Frontend/src:/app/src:ro`). En Windows con Docker Desktop, los paths relativos funcionan correctamente porque el compose se ejecuta desde la raiz del repo. En Linux, tambien funcionan. No se requieren paths absolutos.
  - **Mitigacion**: Verificar con `docker compose up` tras el cambio. Si falla en Windows, Docker Desktop resuelve paths relativos automaticamente en el contexto del compose file.

- **[Riesgo] CI pipeline en GitHub Actions**: Los `working-directory` y `cache-dependency-path` en el workflow YAML deben apuntar a las nuevas rutas. Si alguna referencia queda sin actualizar, el pipeline fallara.
  - **Mitigacion**: Lista exhaustiva de TODAS las ocurrencias verificada con grep antes del commit. El pipeline mismo es la validacion final.

- **[Riesgo] Script `run_provisional.py`**: Este script usa `sys.path.insert` con path absoluto construido desde `REPO_ROOT`. Al mover `Gestion_Incidentes/` a `App/Backend/`, el path construido cambiara. Si el script no se actualiza, fallara.
  - **Mitigacion**: Actualizar las 4 referencias en el script a `App/Backend/`.

- **[Trade-off] Cambios activos desactualizados**: C-19 y C-23 tienen referencias a `Gestion_Incidentes/` y `Frontend/` en sus proposal.md. Tras C-24, esos paths seran incorrectos. No podemos editar proposals de otros cambios como parte de C-24 (rompe la separacion de concerns).
  - **Mitigacion**: Documentar en CHANGES.md y en las notas de C-24 que C-19 y C-23 deben actualizar sus paths antes de ser aplicados. Agregar una tarea de follow-up.

- **[Trade-off] knowledge-base como documentacion semi-estatica**: La KB fue generada en un momento del proyecto y sus paths reflejan el estado en ese momento. Actualizarlos es necesario para consistencia, pero la KB no es "codigo vivo".
  - **Mitigacion**: Actualizar solo los paths explicitos, no reescribir secciones enteras.

## Open Questions

- Ninguna. El alcance esta completamente definido: mover 2 directorios, actualizar paths en ~12 archivos, crear delta specs para 4 specs principales, documentar follow-up para 3 cambios activos.
