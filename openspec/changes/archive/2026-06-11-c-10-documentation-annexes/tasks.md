## 1. OpenAPI estático y verificación de sincronía (Anexo D)

- [x] 1.1 Crear `Gestion_Incidentes/scripts/export_openapi.py` que importe `app.main` (instanciando con env dummies si faltan, igual que CI de C-09), llame a `app.openapi()` y escriba `docs/openapi.json` con indentación estable y orden determinístico de claves
- [x] 1.2 Ejecutar el script y commitear `docs/openapi.json`; verificar que `openapi` empieza con `3.1` y que `paths` contiene las rutas de incidentes, clasificaciones y health
- [x] 1.3 Crear el test de sincronía `Gestion_Incidentes/tests/test_openapi_sync.py` que regenere el esquema en memoria y lo compare contra `docs/openapi.json`, fallando con mensaje accionable si difieren (RED: el test falla si el archivo no existe o difiere)
- [x] 1.4 Verificar que `pytest` corre el test de sincronía en verde con el `openapi.json` commiteado, y que falla si se altera artificialmente el archivo (triangulación: caso en-sincronía + caso desincronizado)
- [x] 1.5 Referenciar el test desde el workflow de CI (patrón del job backend de C-09, con las env dummies `database_url`, `gemini_api_key`, `pseudonymization_encryption_key`)

## 2. Diagramas de arquitectura UML (Anexo A)

- [x] 2.1 Crear `docs/diagrams/despliegue.md` con un diagrama de despliegue Mermaid de los servicios reales de `docker-compose.yml` (postgres, redis, backend, n8n) y sus relaciones
- [x] 2.2 Crear `docs/diagrams/secuencia.md` con un diagrama de secuencia Mermaid del flujo extremo a extremo de un incidente (canal → N8N → backend /clasificar y /incidentes → confirmación)
- [x] 2.3 Crear `docs/diagrams/componentes.md` con un diagrama de componentes Mermaid de las capas del módulo Python (routes, services, repositories, classifiers, models)
- [x] 2.4 Verificar que los tres bloques Mermaid son sintácticamente válidos y que el de despliegue no inventa componentes ausentes en el compose

## 3. Anexo C — Esquema de base de datos

- [x] 3.1 Crear `docs/anexo_c_esquema_bd.md` con `CREATE TABLE` para las 5 tablas (`sector`, `estado`, `canal_origen`, `incidente`, `clasificacion_log`) derivado de los modelos ORM, con tipos, PKs, FKs con su `ON DELETE` real, unique constraints e índices
- [x] 3.2 Documentar los índices compuestos de `incidente` (`(created_at, sector_id)`, `(estado_id, created_at)`) y la doble FK de `clasificacion_log` a `sector` (predicho/validado)
- [x] 3.3 Documentar la doble representación de la descripción (`descripcion_original` cifrada at-rest, `descripcion_pseudonimizada` en claro)
- [x] 3.4 Verificar el anexo contra `Gestion_Incidentes/app/models/` (las 5 tablas exactas, sin inventar; `ON DELETE` correctos: RESTRICT en estado, SET NULL en sector/canal, CASCADE en incidente_id)

## 4. Anexo F — Corpus de validación

- [x] 4.1 Crear `docs/anexo_f_corpus.md` describiendo el esquema CSV (`id`, `descripcion`, `categoria_real` + opcionales de cronometraje), las 3 categorías válidas exactas y el tamaño objetivo de 200 casos
- [x] 4.2 Declarar de forma inequívoca que el corpus disponible (`data/corpus_sintetico_provisional.csv`) es sintético/provisional y que el corpus real es trabajo de campo futuro
- [x] 4.3 Verificar consistencia con el contrato del framework de evaluación (spec `evaluation-framework` de C-08): mismas columnas y mismo conjunto de categorías

## 5. Guía operativa (Anexo G) y troubleshooting

- [x] 5.1 Crear `docs/operational-guide.md` con secciones de despliegue (`docker compose up`), backup/restauración de PostgreSQL y monitoreo de salud (`/health`), con comandos concretos
- [x] 5.2 Verificar que los nombres de servicios, puertos y endpoints de la guía coinciden con `docker-compose.yml`
- [x] 5.3 Crear `docs/troubleshooting.md` con entradas por síntoma (síntoma / causa probable / remediación) cubriendo al menos: backend no levanta, base de datos no disponible, baja confianza → revisión humana, fallo de Gemini

## 6. README de despliegue local

- [x] 6.1 Agregar a `README.md` la sección "Despliegue local" con prerrequisitos, configuración de `.env` desde plantilla, `docker compose up` y verificación de salud, sin contradecir el compose
- [x] 6.2 Enlazar `docs/operational-guide.md` y `docs/troubleshooting.md` desde el README; documentar el arranque opcional del Frontend (Vite, puerto 3000) por separado
- [x] 6.3 Revisar que el camino documentado permita levantar el sistema en menos de 15 minutos desde un clon limpio

## 7. Validación final

- [x] 7.1 Correr `openspec validate --strict --change "c-10-documentation-annexes"` y dejarlo en verde
- [x] 7.2 Correr la suite de tests del backend (incluido el test de sincronía de OpenAPI) y confirmar que pasa
- [x] 7.3 Marcar todas las tareas como completadas y dejar el change listo para archive
