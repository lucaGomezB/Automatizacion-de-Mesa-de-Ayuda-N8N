## Context

Ver `proposal.md` — Why para la motivacion. El estado actual relevante:

- El vocabulario canonico vive replicado en al menos nueve puntos (`evaluation/corpus.py`, `evaluation/metrics.py`, `gemini_classifier.py`, `keywords.py`, `001_seed_catalogs.py`, `openspec/config.yaml`, `docs/prompt_gemini.txt`, `n8n/workflow.json`, `App/Frontend/src/types/catalog.ts`). No existe un unico modulo compartido de constantes de sector.
- La verdad del corpus es estrictamente single-label (`categoria_real`); `evaluation/metrics.py` indexa diccionarios por un unico string y una prediccion fuera de `CLASES` produce `KeyError`.
- El backend guarda el sector como FK unica (`incidente.sector_id`, `clasificacion_log.sector_id_predicho`, `sector_id_validado`). No hay estructura para sectores adicionales.
- El contrato `categoria` atraviesa clasificador, schemas, servicio y webhook N8N.
- La migracion `001_seed_catalogs.py` ya fue aplicada y siembra `Sistemas`, `Operaciones` y `Soporte Técnico`.
- No existe endpoint de catalogo; el frontend fija IDs numericos (1, 2, 3) en `types/catalog.ts`.

El cambio es de gobernanza **ALTA/CRITICA**: toca strings de dominio persistidos y una migracion de base de datos. La migracion y la congelacion de los strings canonicos requieren aprobacion humana explicita antes de apply.

## Goals / Non-Goals

**Goals:**

- Un unico vocabulario canonico de 5 sectores, sin tildes, consumido por backend, evaluacion, N8N y frontend.
- Verdad multietiqueta de punta a punta: corpus JSON, contrato de clasificacion, persistencia relacional y metricas.
- Eliminar el corpus sintetico y su andamiaje sin dejar el framework de evaluacion sin cobertura en CI.
- Migrar la base de datos de forma segura y reversible.

**Non-Goals:**

- Reescribir el texto de la tesis (`docs/Tesis/**`) ni los changes archivados (`openspec/changes/archive/**`).
- Migrar programaticamente el corpus real (gitignored y ausente); requiere reexportacion humana.
- Incorporar NER o modelos de aprendizaje automatico al pseudonimizador.
- Optimizar el rendimiento del clasificador mas alla de la redistribucion de keywords.

## Decisions

### D1 — Persistencia de `sectores_adicionales`: tablas de union normalizadas (no JSONB)

**Decision:** Persistir los sectores adicionales del incidente en una tabla de union `incidente_sector_adicional (incidente_id, sector_id)` con PK compuesta/unicidad y FKs a `incidente` (`ON DELETE CASCADE`) y `sector` (`ON DELETE SET NULL` o `RESTRICT`). Para el log de clasificacion, tablas equivalentes para el conjunto predicho y el conjunto validado.

**Alternativa considerada:** columnas `JSONB` en `incidente`/`clasificacion_log`. Es mas simple (sin migracion de esquema relacional) pero no es consultable con joins, no tiene integridad referencial contra el catalogo y complica el dashboard y las estadisticas.

**Razon:** el dashboard y las estadisticas agregan por sector; la FK garantiza que no se persistan sectores inexistentes; y la tabla de union es la forma natural de modelar una relacion N-a-N. El costo es mas DDL y migracion.

### D2 — Migracion Alembic nueva `004` (no mutar `001`)

**Decision:** crear `004_sectores_multietiqueta.py`. No editar `001_seed_catalogs.py`.

**Alternativa considerada:** editar `001` para cambiar el seed. Es inviable: `001` ya fue aplicada; mutarla rompe la reproducibilidad del historial y las bases existentes no se actualizarian.

**Razon:** migracion aditiva, idempotente, con `downgrade` funcional. Requirements: ASG-004.

### D3 — Esquema JSON del corpus

**Decision:** documento objeto con `schema_version` (entero), `metadata` (`descripcion`, `total_casos`) y `casos`. Cada caso: `id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales` (requerido, `[]` cuando no hay), `tiempo_manual_s`, `tiempo_automatizado_s`. Se elimina `categoria_real`. El loader NORMALIZA `total_casos` a `len(casos)` y lo persiste en disco antes de validar y usar el corpus, de modo que la cabecera nunca queda desincronizada; si no habia cambios, la escritura es idempotente (no reescribe).

**Alternativa considerada:** arreglo JSON de nivel superior (mas simple, pero sin versionado ni metadata) o CSV con columnas extra (`sectores_adicionales` serializado como texto). El objeto con versionado facilita evolucionar el esquema; el CSV no modela de forma nativa un arreglo.

**Razon:** invariantes verificables (sector asignado no repetido en adicionales; todos los valores canonicos) y versionado explicito. Requirements: CORPUS-009, CORPUS-010.

### D4 — Frontend sin IDs numericos fijos

**Decision:** el frontend deja de depender de `SECTOR_IDS` (1, 2, 3). Se agrega un endpoint de solo lectura `GET /api/v1/catalogos/sectores` que devuelve `[{ id, nombre }]`; las opciones del formulario, el dialogo de validacion y el filtro del dashboard se construyen a partir de ese catalogo en runtime. La insignia y el grafico de torta usan el `nombre` como clave de color/etiqueta.

**Alternativa considerada:** mantener un mapa `nombre -> id` hardcodeado. Es mas simple pero reintroduce el mismo acoplamiento que este cambio busca eliminar: cualquier futura migracion de catalogo vuelve a romper la UI.

**Razon:** los IDs cambian con la migracion 004; los nombres son el unico identificador estable de dominio. El costo es un endpoint nuevo y un fetch adicional. Requirements: TAX-004.

### D5 — Definiciones de las metricas multietiqueta

**Decision:**

- **Matriz primaria 5x5:** filas = `sector_asignado`, columnas = `sector_predicho` (sector principal). Es la matriz de referencia y la unica 5x5.
- **Exactitud primaria:** proporcion de casos con `sector_predicho == sector_asignado`.
- **Subset accuracy:** proporcion de casos cuyo conjunto predicho (`{sector_predicho} ∪ sectores_adicionales`) iguala el conjunto de verdad (`{sector_asignado} ∪ sectores_adicionales` de verdad).
- **Hamming loss:** etiquetas erroneas sobre el total de etiquetas del universo del caso.
- **Micro-F1:** F1 calculado sobre TP/FP/FN acumulados de todas las etiquetas.
- **Macro-F1:** media aritmetica de los F1 por sector.
- **Tabla one-vs-rest por sector:** precision, recall, F1 y support.
- **Wilson CI:** sobre las dos definiciones de acierto — (a) igualdad estricta y (b) pertenencia (`sector_asignado ∈` conjunto predicho).
- **Jaccard/IoU:** opcional, por caso.

**Alternativa considerada:** evaluar solo por pertenencia (mas laxa) o solo por igualdad estricta (ignora `sectores_adicionales`). Ambas inducen interpretaciones sesgadas.

**Razon:** reportar las dos definiciones de acierto evita "jugar" con la metrica; subset accuracy y Hamming miden la calidad del conjunto completo; micro/macro cubren agregado y balance. Requirements: evaluation-framework.

### D6 — CI de evaluacion sin corpus sintetico

**Decision:** mantener el job de evaluacion en `.github/workflows/ci.yml`, pero ejecutandolo contra el fixture JSON `evaluation/tests/fixtures/corpus_fixture.json` (migrado con las etiquetas nuevas) y los tests unitarios de loader/metricas/runner. No se usa corpus sintetico de 200 casos.

**Alternativa considerada:** eliminar el job de evaluacion de CI. Se descarta: perderia la unica cobertura automatizada del framework de evaluacion.

**Razon:** conserva cobertura sin reintroducir el artefacto descartado. El corpus real (`data/corpus_evaluacion_pseudonimizado.json`) nunca entra a CI.

### D7 — Migracion de datos existentes y `Operaciones`

**Decision:** en `upgrade`, la migracion `004`:

1. Crea las tablas de union.
2. Pone en `NULL` las referencias a `Operaciones` y al viejo `Soporte Técnico` en `incidente` y `clasificacion_log` (FKs `SET NULL`).
3. Elimina las filas `Operaciones` y `Soporte Técnico` (con tilde) del catalogo.
4. Hace upsert de los cinco sectores canonicos (incluido `Sistemas`, que ya existe).

`downgrade` revierte las tablas y reinserta los valores previos. Antes de aplicar en una base con datos reales MUST tomarse un backup (`scripts/backup.sh`).

**Alternativa considerada:** conservar `Operaciones` como fila legacy oculta del clasificador. Se descarta: contradice ASG-004 y deja ambiguedad sobre el vocabulario vigente.

**Razon:** vocabulario unico y consistente. El costo es una migracion de datos destructiva de bajo riesgo en este proyecto (datos locales/de prueba), mitigada por el backup obligatorio.

### D8 — Un unico mapa de keywords redistribuido

**Decision:** reescribir `App/Backend/app/classifiers/keywords.py` con cinco claves canonicas. Los terminos hoy asociados a `Sistemas` se reparten entre `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos` y `Sistemas`; los de `Soporte Técnico` se dividen entre `Soporte Tecnico Hardware` y `Soporte Tecnico Software`; `Operaciones` desaparece.

**Alternativa considerada:** renombrar claves sin redistribuir. Invalida: el clasificador quedaria sesgado y `Operaciones` seguiria muy poblado.

**Razon:** es un cambio de comportamiento del clasificador, no un rename mecanico; invalida los numeros de referencia del corpus sintetico.

## Risks / Trade-offs

- **Migracion destructiva de datos** (`Operaciones`/`Soporte Técnico` puestas en NULL y borradas) → Mitigacion: backup obligatorio previo; `downgrade` funcional; aprobacion humana explicita.
- **Strings sin tildes vs prosa con tildes** → Mitigacion: los cinco strings canonicos se centralizan y se testean por igualdad exacta; el pseudonimizador los incluye en el set de exclusion.
- **Precision del clasificador cambia** → Mitigacion: los numeros 82/64/54, exactitud 92%, F1 ~0.919 y Tabla 7 quedan declarados superados; la precision real se vuelve a medir con el corpus real.
- **Nuevo fetch del catalogo en el frontend** puede degradar la primera carga → Mitigacion: React Query cachea el catalogo; estado de carga explicito en el formulario y el dialogo.
- **Doble contabilidad en metricas** (estricta y por pertenencia) puede confundir la lectura → Mitigacion: el reporte etiqueta cada definicion y la matriz primaria 5x5 queda como referencia unica.
- **Riesgo de no cubrir `sectores_adicionales` en validacion humana** → Mitigacion: ASG-005 exige persistir el conjunto validado; tests dedicados.
- **El corpus real esta ausente** → Mitigacion: el runner falla con error claro (no inventa datos); el fixture JSON mantiene la cobertura.

## Migration Plan

1. Congelar y centralizar los cinco strings canonicos; actualizar `openspec/config.yaml`, `AGENTS.md`, `CLAUDE.md`, prompt y N8N.
2. Crear la migracion `004` y las tablas de union; correr `alembic upgrade head` en local; verificar `alembic downgrade` y re-upgrade.
3. Redistribuir keywords y alinear Gemini (prompt, enum, validacion).
4. Renombrar el contrato a `sector_predicho` + `sectores_adicionales` en schemas/servicio/webhook y actualizar los ~16 tests de backend.
5. Migrar el corpus fixture a JSON y reescribir el loader/metricas/runner; refactorizar el job de evaluacion de CI.
6. Actualizar frontend (catalogo dinamico, insignia, torta, formulario) y sus tests.
7. Eliminar corpus sintetico y artefactos provisionales; actualizar docs y knowledge-base; regenerar `docs/openapi.json`.
8. **Rollback:** `alembic downgrade 001` seguido del revert del cambio de codigo. Restaurar backup si la base tenia datos reales.

## Open Questions

- Define el numero definitivo de terminos por sector en `keywords.py` (se resuelve durante apply con casos de prueba; no cambia el contrato ni el enfoque).
- El endpoint de catalogo puede devolver tambien estados y canales en el futuro; en este cambio se limita a sectores.
