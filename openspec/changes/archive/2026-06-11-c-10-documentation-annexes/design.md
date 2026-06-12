## Context

C-10 es el último change del roadmap. Sus dependencias (C-04, C-05, C-09) están mergeadas. El backend FastAPI, los 5 modelos ORM, el framework de evaluación (C-08) y la infraestructura Docker ya existen y son las fuentes de verdad de las que esta documentación debe derivarse —no inventarse.

Estado actual relevante:
- **Modelos ORM** (`Gestion_Incidentes/app/models/`): `catalog.py` (Sector, Estado, CanalOrigen), `incidente.py` (Incidente, con doble representación de la descripción e índices compuestos), `clasificacion_log.py` (ClasificacionLog, con doble FK a sector). Estas son las fuentes para el Anexo C.
- **Rutas** (`Gestion_Incidentes/app/routes/`): `incidentes.py`, `clasificaciones.py`, `health.py`. La app expone `/docs` y `/redoc` **solo en modo debug**; el OpenAPI estático debe generarse invocando la app, no scrapeando un servidor corriendo.
- **App factory**: `app.main:create_app()` construye la instancia; `app.main.app` es la instancia global. La config (`pydantic-settings`) no tiene defaults: requiere `database_url`, `gemini_api_key`, `pseudonymization_encryption_key`. CI (C-09) ya inyecta dummies para estas.
- **Corpus**: `data/corpus_sintetico_provisional.csv` (columnas `id,descripcion,categoria_real`) es sintético. El contrato del corpus lo define el spec de `evaluation-framework`. El corpus real (`data/corpus_evaluacion_pseudonimizado.csv`, 200 casos) no está en git y es trabajo de campo futuro.
- **Infra**: `docker-compose.yml` (raíz) levanta postgres:15.5-alpine (puerto host 5433), redis, backend (build desde `Gestion_Incidentes/Dockerfile`, puerto 8000, `alembic upgrade head` + uvicorn, healthcheck a `/health`) y n8n. El Frontend (Vite, puerto 3000) no está en el compose.

Restricción transversal: la documentación es del proyecto/tesis y se escribe en **español rioplatense**.

## Goals / Non-Goals

**Goals:**
- Producir los artefactos de documentación de los Anexos A, C, D, F, G más troubleshooting y README, cada uno verificable contra una fuente de verdad del repo.
- Generar `docs/openapi.json` de forma reproducible DESDE la app FastAPI, con una verificación de sincronía ejecutable en CI.
- Mantener los diagramas como fuente de texto versionable (no binarios) para que evolucionen con el código.

**Non-Goals:**
- No se modifica código de producción ni comportamiento del sistema.
- No se genera el corpus real ni se ejecuta la evaluación experimental (eso es C-08 / trabajo de campo futuro).
- No se editan los archivos `.docx` de la tesis; los anexos se materializan como `.md`/artefactos en `docs/` para que la tesis los referencie.
- No se documenta el Anexo H (ya existe `ANEXO_H_Prompt_Gemini_Especificacion.md`) ni los Anexos B/E (repositorio y JSON de N8N ya existen).
- No se agrega autenticación ni se "completa" el contrato REST más allá de lo que la app ya expone (la tesis menciona tokens bearer; la app actual no los implementa — el OpenAPI documenta lo REAL, no lo aspiracional).

## Decisions

### D1: Diagramas en Mermaid (texto), no .drawio binario
La tesis (Anexo A) menciona `.drawio`, pero ese formato es binario/XML y mal versionable en diffs. **Decisión**: usar Mermaid en archivos `docs/diagrams/*.md` (un bloque ```mermaid por diagrama). Mermaid renderiza nativamente en GitHub y es diff-friendly. Se documenta esta desviación respecto del `.drawio` mencionado en la tesis. *Alternativa descartada*: PlantUML (requiere toolchain Java para renderizar; Mermaid no requiere nada). *Alternativa descartada*: exportar PNG desde drawio (no versionable, no auditable en review).

### D2: openapi.json generado desde la app, no a mano
Un script `Gestion_Incidentes/scripts/export_openapi.py` importa `app.main` (o llama `create_app()`) y serializa `app.openapi()` a `docs/openapi.json`. **Razón**: FastAPI ya genera OpenAPI 3.1 fiel a los `@router`; escribirlo a mano garantiza drift inmediato. El script setea env dummies si no están presentes (mismo patrón que CI de C-09) para que `Settings` instancie sin DB real. *Alternativa descartada*: `curl http://localhost:8000/openapi.json` contra un servidor corriendo — requiere DB y servidor up, y además `/docs` solo se habilita en debug, lo que complica la reproducibilidad en CI.

### D3: Verificación de sincronía como test/CI check
La sincronía se valida regenerando el esquema en memoria y comparándolo con `docs/openapi.json`. **Decisión**: implementarlo como un test de pytest (`tests/test_openapi_sync.py`) que falle si difieren, reutilizando el conftest/fixtures del backend, y referenciarlo desde CI siguiendo el patrón del job backend de C-09 (que ya inyecta las env dummies). Un test es más simple de mantener y correr localmente que un step de shell ad-hoc. *Alternativa descartada*: comparar via diff en un step de bash — duplica la lógica de carga de env y no corre con `pytest` local.

### D4: Anexo C derivado de los modelos ORM, escrito como SQL legible a mano
El SQL del Anexo C se escribe manualmente reflejando fielmente los modelos ORM (no se autogenera con `create_all` dumpeado, que produce DDL ruidoso dependiente de dialecto). **Razón**: el anexo es para lectura humana del jurado; el SQL debe ser limpio y anotado, pero exacto en tipos, FKs (con `ON DELETE` real), unique constraints e índices. Una tarea de verificación cruza el anexo contra los modelos. *Nota*: las migraciones Alembic siguen siendo la fuente ejecutable; el anexo es la vista documental consolidada.

### D5: Anexo F declara honestamente la naturaleza sintética del corpus
El corpus disponible es sintético/provisional. **Decisión**: el Anexo F describe el esquema, las categorías y el tamaño objetivo (200), pero declara de forma inequívoca que los datos actuales son sintéticos y que el corpus real es trabajo de campo futuro; no presenta los sintéticos como resultados experimentales. Esto preserva la integridad académica del trabajo.

### D6: README reescrito alrededor del despliegue local < 15 min
El README actual no tiene una sección de despliegue paso a paso. **Decisión**: agregar una sección "Despliegue local" con prerrequisitos, `.env` desde plantilla, `docker compose up`, verificación de salud y enlaces a la guía operativa y troubleshooting, manteniendo las secciones existentes (clasificación, hook anti-secretos, engram).

## Risks / Trade-offs

- **[Drift de openapi.json]** → La verificación de sincronía (D3) lo detecta en CI; si la app cambia rutas, el test falla hasta regenerar.
- **[Anexo C desincronizado de los modelos al evolucionar el schema]** → Tarea de verificación que cruza el anexo contra los modelos en el momento de escribirlo; se acepta que es un snapshot documental (las migraciones Alembic son la fuente ejecutable de verdad).
- **[Mermaid difiere del `.drawio` que menciona la tesis]** → Desviación documentada y justificada (versionabilidad); el jurado obtiene diagramas legibles y mantenibles.
- **[El script de export importa la app y dispara side-effects]** → `create_app()` no abre conexiones a DB en import (el engine usa lazy connect y el lifespan no corre fuera del servidor); el script solo necesita las env para instanciar `Settings`. Riesgo bajo.
- **[Comandos operativos que no matchean el compose]** → Tareas de verificación que contrastan los comandos del operational-guide y del README contra `docker-compose.yml`.

## Migration Plan

No aplica migración de datos ni de código. Despliegue de la documentación: merge del PR. Rollback: revertir el PR (solo archivos de docs + un script y un test de solo-lectura). El test de sincronía se incorpora al pipeline existente sin cambiar la build del backend.

## Open Questions

- ¿El Frontend (Vite, puerto 3000) debe incluirse en las instrucciones de despliegue local del README? El compose actual no lo levanta. **Resolución propuesta**: documentar el arranque del Frontend por separado (`npm install && npm run dev` en `Frontend/`) como paso opcional, sin bloquear el camino de < 15 min del backend + N8N.
