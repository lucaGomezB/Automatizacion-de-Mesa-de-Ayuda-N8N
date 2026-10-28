## ADDED Requirements

### Requirement: Cierre de la divergencia del driver de base de datos en la base de conocimiento

`knowledge-base/10_preguntas_abiertas.md` SHALL declarar la entrada IN-03 (divergencia del driver de base de datos) como RESUELTA, dejando constancia verificable de que la version de trabajo de la tesis declara la capa de acceso a datos con `SQLAlchemy 2.0` y `asyncpg` como driver asincronico (`docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex`, Seccion 5.4) y de que el codigo usa la misma combinacion. La entrada MUST NOT presentar como vigente una divergencia entre un driver `psycopg2` en la tesis y `asyncpg` en el codigo. El texto original de la entrada SHALL conservarse como antecedente historico rotulado cuando aporte contexto, sin reescribirse.

#### Scenario: IN-03 figura como resuelta con evidencia

- **WHEN** se lee la entrada IN-03 de `knowledge-base/10_preguntas_abiertas.md`
- **THEN** la entrada declara el estado RESUELTO
- **AND** cita como evidencia que la Seccion 5.4 de la tesis declara `asyncpg` con `SQLAlchemy 2.0` y que el codigo usa esa combinacion

#### Scenario: No se declara vigente una divergencia inexistente

- **WHEN** se busca en `knowledge-base/10_preguntas_abiertas.md` una afirmacion de que la tesis vigente usa `psycopg2`
- **THEN** esa afirmacion no aparece como estado vigente de la entrada

### Requirement: Cierre de la descripcion stale del workflow N8N en la base de conocimiento

`knowledge-base/10_preguntas_abiertas.md` SHALL declarar la entrada IN-06 (workflow N8N del repositorio frente a la descripcion de la tesis) como reconciliada, y su descripcion del workflow SHALL corresponder al artefacto `n8n/workflow.json` vigente: el disparador de correo usa el nodo IMAP (`Mesa de Ayuda - IMAP`), la clasificacion permanece embebida en el backend y el canal telefonico no usa un agente de IA de LangChain ni memoria de sesion en Redis. La entrada MUST NOT describir como vigentes el disparador de Microsoft Outlook, el agente LangChain ni Redis. El texto original SHALL conservarse como antecedente historico rotulado cuando aporte contexto.

#### Scenario: La descripcion refleja el workflow vigente

- **WHEN** se lee la entrada IN-06 de `knowledge-base/10_preguntas_abiertas.md`
- **THEN** declara el disparador de correo por IMAP y la clasificacion embebida en el backend
- **AND** no presenta el agente LangChain ni Redis como componentes vigentes del canal telefonico

#### Scenario: La divergencia se marca como reconciliada

- **WHEN** se lee el estado de la entrada IN-06
- **THEN** la divergencia queda declarada como reconciliada junto con el artefacto de referencia `n8n/workflow.json`

### Requirement: Estado aspiracional de Kubernetes declarado en la base de conocimiento

`knowledge-base/10_preguntas_abiertas.md` SHALL marcar la pregunta sobre el alcance de Kubernetes (SU-05) como RESUELTA, declarando que la migracion a un cluster Kubernetes queda fuera del alcance del trabajo y se trata como aspiracional (evolucion de plataforma anticipada, sin manifiestos de despliegue en el repositorio). La declaracion SHALL ser consistente con la narrativa de la tesis, que presenta la migracion como trabajo futuro y no como despliegue actual.

#### Scenario: La pregunta de Kubernetes figura resuelta como aspiracional

- **WHEN** se lee la tabla de preguntas abiertas de `knowledge-base/10_preguntas_abiertas.md`
- **THEN** la pregunta sobre Kubernetes (SU-05) figura como RESUELTA con el estado aspiracional/fuera de alcance
- **AND** no se presenta Kubernetes como un despliegue vigente

#### Scenario: Coherencia con la base de conocimiento de arquitectura

- **WHEN** se compara la entrada con `knowledge-base/08_arquitectura_propuesta.md` y `knowledge-base/09_decisiones_y_supuestos.md`
- **THEN** ambas describen el despliegue productivo en Kubernetes como aspiracional, sin manifiestos en el repositorio
