## ADDED Requirements

### Requirement: Nota del driver de base de datos en el Anexo C

El Anexo C de la tesis (`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`, seccion del esquema de base de datos) SHALL declarar que la capa de acceso a datos del modulo usa `SQLAlchemy 2.0` como ORM y `asyncpg` como driver asincronico para PostgreSQL, en coherencia con la Seccion 5.4 y con el codigo. La nota MUST NOT afirmar que la tesis vigente declara `psycopg2` ni presentar una divergencia inexistente entre la tesis y el codigo.

#### Scenario: El Anexo C declara el driver implementado

- **WHEN** se lee la seccion del esquema de base de datos de `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`
- **THEN** declara `SQLAlchemy 2.0` con `asyncpg` como driver asincronico de PostgreSQL
- **AND** la declaracion es consistente con la Seccion 5.4 del mismo documento

#### Scenario: La nota no introduce una divergencia inexistente

- **WHEN** se busca en el Anexo C la mencion de `psycopg2` como el driver declarado por la tesis
- **THEN** esa mencion no aparece como estado vigente

### Requirement: Subsecciones faltantes del capitulo de recomendaciones

`docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` SHALL incluir una subseccion por cada linea de trabajo futuro que la introduccion del capitulo anticipa en `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` (Seccion de alcance y delimitaciones). En particular, el capitulo SHALL incorporar dos subsecciones ausentes: la integracion con sistemas externos de inventario de activos y de gestion de configuracion de la configuracion, y la automatizacion de la etapa de resolucion tecnica. Cada subseccion SHALL seguir el patron de las subsecciones existentes (`\subsection{...}\label{...}`) y desarrollar su linea en un parrafo academico neutral en espanol, sin introducir cifras nuevas ni afirmaciones no respaldadas.

#### Scenario: La remision de la introduccion tiene destino en el capitulo

- **WHEN** se recorren las cuatro lineas de trabajo futuro enumeradas en la Seccion de alcance y delimitaciones de la introduccion
- **THEN** cada una tiene una subseccion correspondiente en el capitulo de recomendaciones
- **AND** la subseccion de integracion con sistemas externos de inventario y gestion de configuracion existe
- **AND** la subseccion de automatizacion de la etapa de resolucion tecnica existe

#### Scenario: Las subsecciones siguen el patron y el registro del capitulo

- **WHEN** se inspeccionan las dos subsecciones agregadas
- **THEN** cada una usa la forma `\subsection{...}\label{...}` con etiquetas unicas
- **AND** su texto es un parrafo academico neutral, sin cifras nuevas

### Requirement: Coherencia de la narrativa de Kubernetes con su tratamiento aspiracional

La narrativa de la tesis sobre Kubernetes SHALL presentarlo como una evolucion de plataforma aspiracional y futura, nunca como un despliegue vigente. Si la Seccion 5 del capitulo de recomendaciones lista la migracion a Kubernetes entre las evoluciones anticipadas, MUST conservar ese encuadre, consistente con el capitulo de implementacion que la plantea como trabajo futuro sin manifiestos.

#### Scenario: Kubernetes se presenta como trabajo futuro

- **WHEN** se busca en `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` y en `docs/Tesis/v10 (IA)/paper/sections/06-implementacion.tex` la mencion de la migracion a Kubernetes
- **THEN** ambas la presentan como trabajo futuro o evolucion anticipada
- **AND** ninguna afirma que el sistema se despliega actualmente en Kubernetes

### Requirement: Anotacion fechada del cierre de la observacion O8 en el ledger del dictamen

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL registrar el cierre de la observacion O8 (timeout de 10 s en la tesis y el Anexo H frente a 30 s del backend) con una anotacion fechada que la marque como RESUELTA, incluyendo la evidencia verificable: la configuracion vigente declarada en `openspec/config.yaml` (`timeout_s: 30` y `total_timeout_s: 60`) y la remision de `CLAUDE.md` a esa seccion en lugar de repetir el valor retirado. La anotacion MUST conservar el texto original de la observacion como historia.

#### Scenario: O8 figura como resuelta con evidencia

- **WHEN** se lee la fila o la anotacion de la observacion O8 en `docs/Tesis/Correcciones/dictamen-correcciones.md`
- **THEN** declara el estado RESUELTA con fecha
- **AND** cita la evidencia (`openspec/config.yaml` con `timeout_s: 30` y `total_timeout_s: 60`; `CLAUDE.md` remitiendo a esa seccion)

#### Scenario: El texto original de la observacion se conserva

- **WHEN** se compara la observacion O8 con su version previa
- **THEN** el texto original del hecho registrado se conserva integro
- **AND** el cierre se expresa como anotacion fechada, no como sustitucion del hecho
