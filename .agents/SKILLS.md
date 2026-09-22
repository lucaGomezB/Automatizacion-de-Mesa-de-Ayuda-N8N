# SKILLS — Registro de skills del proyecto

Indice canonico de las skills de agente disponibles en este repositorio.
Un agente DEBE leer este archivo antes de implementar (fase apply) y cargar las
skills de dominio que correspondan a las tareas del change.

## Como estan organizadas

- Las **skills de dominio** estan vendorizadas (copiadas) en `.agents/skills/<nombre>/SKILL.md`.
  Al clonar el repo ya las tenes: no hace falta instalar nada ni depender de la
  configuracion global de la maquina de cada colaborador.
- La trazabilidad de origen y version esta en `skills-lock.json` (raiz del repo).
- Las **skills de flujo OPSX** viven en `.opencode/skills/` (ver seccion final).
  Son parte del proyecto y tambien estan versionadas.

## Regla de carga (fase apply)

1. Lee este registro.
2. Identifica que skills matchean las tareas del change.
3. Carga el `SKILL.md` COMPLETO de cada skill que matchee, ANTES de escribir codigo.
4. Los patrones y convenciones de la skill tienen prioridad sobre el conocimiento
   general del agente. Si la skill contradice una regla dura del proyecto
   (`AGENTS.md`, `openspec/config.yaml`), gana la regla del proyecto.

## Skills de dominio vendorizadas

| Skill | Alcance | Cargar cuando | Origen | Licencia |
|-------|---------|---------------|--------|----------|
| `sqlalchemy-postgres` | SQLAlchemy 2.0 async + Pydantic + PostgreSQL: modelos, repositorios, migraciones Alembic, queries | Tareas de capa de datos (`app/models/`, `app/repositories/`, `alembic/`) | `cfircoo/claude-code-toolkit` | MIT |
| `python-testing-patterns` | Patrones pytest detallados: AAA, fixtures, mocking, freezegun, markers, coverage | Al escribir o extender tests de backend o de evaluation | `wshobson/agents` | MIT |
| `python-testing` | Principios generales de pytest y TDD: unit / integration / property-based, mocking | Marco general al arrancar trabajo de testing | `mindrally/skills` | Apache-2.0 |
| `pytest-coverage` | Flujo operativo de cobertura con `--cov-report=annotate` hasta cerrar las lineas sin cubrir | Cuando hay que medir o subir la cobertura | `github/awesome-copilot` | MIT |
| `python-design-patterns` | KISS, SRP, separation of concerns, composicion sobre herencia, deteccion de acoplamiento | Al disenar o refactorizar servicios y componentes | `wshobson/agents` | MIT |
| `tailwind-design-system` | Design system con Tailwind CSS **v4**: tokens, libreria de componentes, responsive, a11y | Tareas de UI/frontend, CON el caveat de version de abajo | `wshobson/agents` | MIT |
| `find-skills` | Descubrir e instalar nuevas skills del ecosistema abierto | Cuando falta una capacidad que podria existir como skill instalable | `vercel-labs/skills` | MIT |

## Caveats (leer antes de aplicar una skill)

- **`tailwind-design-system` apunta a Tailwind v4, el proyecto usa v3.** El frontend
  esta en `tailwindcss ^3.4.11` con `tailwind.config.ts` (sintaxis `content` / `theme` /
  `plugins`). La skill es CSS-first v4 (`@import "tailwindcss"`, `@theme`,
  `@custom-variant`). Usar de ella SOLO los conceptos transferibles: design tokens,
  variantes de componentes, patrones responsive y accesibilidad. Ignorar toda la
  sintaxis v4. Para configuracion, seguir `App/Frontend/tailwind.config.ts` y el estilo
  de `src/components/ui/` (shadcn/ui).
- **`python-testing` y `python-testing-patterns` se solapan.** `python-testing-patterns`
  es el mas profundo (278 lineas, con ejemplos trabajados) y es el que se debe preferir
  al escribir tests. `python-testing` aporta el marco conceptual general. No hace falta
  cargar las dos si la tarea es concreta.
- **`pytest-coverage` es operativa y acotada**: solo describe el flujo de
  `--cov-report=annotate` para llegar a 100%. No reemplaza a las otras dos.
- **`find-skills` no aporta conocimiento de dominio**: sirve para descubrir e instalar
  skills. Su escaneo de seguridad de Snyk dio "Med Risk" (instala paquetes de terceros).
  Usarla con criterio y revisar siempre lo que propone instalar.
- **`sqlalchemy-postgres` asume SQLAlchemy 2.0 + Pydantic + PostgreSQL.** El proyecto
  cumple, pero hay reglas duras que la skill NO conoce y hay que respetar: `selectinload()`
  obligatorio para relationships serializados (nunca lazy-load en async) y la disciplina
  de capas `routes -> services -> repositories -> models`.

## Skills de flujo OPSX (`.opencode/skills/`)

Estas no son de dominio: son el workflow del proyecto y ya vienen versionadas.

| Skill | Para que |
|-------|----------|
| `openspec-explore` | Modo exploracion, sin implementar |
| `openspec-propose` | Crear un change con todos los artefactos |
| `openspec-apply-change` | Implementar las tareas de un change |
| `openspec-archive-change` | Sincronizar delta specs y archivar el change |
| `openspec-sync-specs` | Fusionar delta specs sin archivar |

## Mantenimiento

```bash
# Ver si hay actualizaciones de las skills vendorizadas
npx skills check

# Actualizar todas las skills instaladas en el proyecto
npx skills update

# Reinstalar exactamente lo que declara skills-lock.json (en otra maquina o tras un clon)
npx skills experimental_install

# Instalar o reinstalar una skill puntual, copiada al repo
npx skills add <owner/repo> -s <skill> --copy -y
```

Al agregar o quitar una skill, actualizar este registro y `skills-lock.json` en el
mismo commit.

## Atribucion y licencias

Las skills vendorizadas son contenido de terceros, distribuidas bajo licencias
permisivas. Se conserva el origen y la licencia para cumplir con la atribucion:

| Skill | Repositorio de origen | Licencia |
|-------|-----------------------|----------|
| `sqlalchemy-postgres` | https://github.com/cfircoo/claude-code-toolkit | MIT |
| `python-testing-patterns` | https://github.com/wshobson/agents | MIT |
| `python-design-patterns` | https://github.com/wshobson/agents | MIT |
| `tailwind-design-system` | https://github.com/wshobson/agents | MIT |
| `python-testing` | https://github.com/mindrally/skills | Apache-2.0 |
| `pytest-coverage` | https://github.com/github/awesome-copilot | MIT |
| `find-skills` | https://github.com/vercel-labs/skills | MIT |

Nota de cumplimiento: las licencias MIT y Apache-2.0 exigen conservar el aviso de
copyright y el texto de la licencia en las copias. Este registro cubre la atribucion;
si el repositorio se distribuye publicamente, conviene ademas incluir los textos
completos de licencia de cada origen.
