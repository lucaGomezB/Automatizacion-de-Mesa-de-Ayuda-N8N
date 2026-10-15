## Context

Ver `proposal.md`. Estado actual relevante: `GET /api/v1/incidentes` (routes -> service -> repository) soporta filtros por sector, estado, prioridad, revision humana, rango de fechas y `origen_message_id` (exacto); no hay texto libre. `list_filtered` arma condiciones AND y ordena por `created_at desc`. El alcance por rol se deriva en el servicio (`incident_visibility`) y se materializa como `reportante_empleado_id` o lista vacia; el frontend ya tiene barra de filtros, `EmptyState` en `TicketsTable` y la cadena `IncidenteListParams -> useIncidentes -> listarIncidentes`. Suite backend en dos subsets (SQLite unidad + PostgreSQL integracion, migraciones Alembic hasta 017).

## Goals / Non-Goals

**Goals:**
- Agregar busqueda por texto libre segura, combinable y respetuosa del alcance, sin cambios rupturistas.
- Sostener la busqueda por subcadena con un indice adecuado.
- Integrar una barra de busqueda con debounce al flujo de datos existente y un estado vacio coherente.

**Non-Goals:**
- Sin busqueda difusa, insensible a acentos, ni motor de full-text (FTS/tsvector).
- Sin busqueda por nombre de sector, estado ni prioridad como texto (ya tienen filtro propio).
- Sin exponer `descripcion_pseudonimizada` en la proyeccion de lista (`IncidenteListItem`) ni mostrar fragmentos de coincidencia.
- Sin cambios al modelo de visibilidad; la busqueda no introduce ninguna via de acceso.

## Decisions

- **D1 - Campos buscados**: `descripcion_pseudonimizada` (coincidencia parcial ILIKE) OR `id` (coincidencia exacta, solo si `q` es numerico). Se EXCLUYE el nombre de sector: ya existe un filtro de sector dedicado y buscar en el catalogo acoplaria el texto de la busqueda a datos de catalogo, con un JOIN extra y semantica redundante. Alternativa considerada: incluir `sector.nombre`; descartada por redundancia.
- **D2 - Longitud minima**: 2 caracteres tras recortar. `q` vacio, de solo espacios o de 1 caracter se ignora (equivale a sin filtro). Alternativa: minima 1; descartada por consultas demasiado amplias y poco utiles.
- **D3 - Debounce**: 300 ms en el frontend, aplicado antes de emitir la consulta. Alternativa: 500 ms; descartada por sensacion de lentitud en uso interactivo.
- **D4 - Seguridad de la consulta**: condicion SQLAlchemy `.ilike(...)` con bind de parametros (nunca interpolacion) y un helper que escapa `\`, `%` y `_`, usando `escape='\\'`. Nunca se referencia `descripcion_original`. Alternativa: `func.lower(...) LIKE ...`; descartada por perder el manejo de dialecto de `ilike`.
- **D5 - Composicion con alcance**: `q` se agrega como una condicion AND mas dentro de `list_filtered`; el alcance sigue derivandose en el servicio y no se reimplementa. Esto hace que `q` componga con GLOBAL, PROPIO, VACIO y con el futuro modo por sector de c-86 (`gestion_incidentes`) sin cambios en la busqueda.
- **D6 - Indice**: nueva migracion Alembic `020` (`down_revision = "019"`) que ejecuta `CREATE EXTENSION IF NOT EXISTS pg_trgm` y crea un indice GIN trigram (`gin_trgm_ops`) sobre `descripcion_pseudonimizada`. Un ILIKE de subcadena no puede usar un B-tree; el trigram lo acelera para terminos de 3+ caracteres. Alternativa: omitir indice; descartada por dejar un full scan en la consulta principal del panel. `pg_trgm` es trusted en PostgreSQL 15, por lo que el dueno de la base puede crear la extension sin superusuario.
- **D7 - Contrato API**: nuevo query param `q` (opcional, `max_length=200`) en la ruta; se regenera `docs/openapi.json` (guarda `tests/test_openapi_sync.py`).
- **D8 - Estado del frontend**: `q` se agrega a `IncidenteListParams` y se gestiona dentro del estado `filtros` de la pagina; un hook nuevo `useDebouncedValue` retrasa el valor efectivo 300 ms. Cualquier cambio de `q` reinicia la pagina a 1 (mismo patron que los filtros existentes). `listarIncidentes` ya reenvia `params` sin cambios.
- **D9 - Estado vacio**: se reutiliza el `EmptyState` ya presente en `TicketsTable` (cubre lista vacia); se ajusta el copy para contemplar busqueda y filtros. No se agrega estado nuevo.

## Risks / Trade-offs

- [El indice trigram no acelera terminos de 2 caracteres] -> Longitud minima 2 y corpus acotado de tesis; aceptable. Ruta de mejora futura: subir minima a 3.
- [Perdida de rendimiento por ILIKE en tablas grandes] -> Indice GIN trigram para el caso comun (3+); se documenta el limite.
- [Escapes de comodines incorrectos amplian la coincidencia] -> Helper de escape unico y cubierto por tests (escenarios de comodines literales).
- [Acoplamiento con c-86] -> `q` es ortogonal al alcance; se agrega un test de regresion de busqueda bajo alcance PROPIO.
- [La extension `pg_trgm` no disponible en algun entorno] -> El subset SQLite de unidad no usa migraciones; la integracion PostgreSQL si; `pg_trgm` viene con PostgreSQL estandar.

## Migration Plan

1. Backend: agregar `q` a la ruta, pasarlo por `list_incidentes` y aplicarlo en `list_filtered` con helper de escape.
2. Migracion `020` (`down_revision = "019"`) con `pg_trgm` + indice GIN; `downgrade` elimina el indice (deja la extension instalada, sin efectos adversos).
3. Frontend: campo `q` en `IncidenteListParams`, hook de debounce, input en el panel, reinicio de pagina y copy del estado vacio.
4. Regenerar `docs/openapi.json`.
5. Rollback: revertir el codigo y ejecutar `alembic downgrade 019`; el parametro opcional `q` es retrocompatible, por lo que no hay migracion de datos.

## Open Questions

Ninguna pendiente. Resueltas y fijadas en Decisiones: campos buscados (D1), longitud minima 2 (D2), debounce 300 ms (D3), indice si con `pg_trgm` GIN (D6).
