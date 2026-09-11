# Modelo de Datos

## Dominios

- **Incidentes**: ticket central con ciclo de vida (estado) y derivación (sector).
- **Catálogos**: vocabulario controlado inmutable en runtime (sector, estado, canal_origen) — sembrado por migración Alembic `001_seed_catalogs.py`; el catálogo de sectores se reemplaza por los 5 sectores canónicos en `004_sectores_multietiqueta.py` (C-27).
- **Auditoría de clasificación**: registro histórico de cada decisión del clasificador; base del corpus de evaluación.

## ERD

```
 canal_origen 1───N incidente N───1 sector
                        │  N───1 estado
                        │
                        1
                        │
                        N
                clasificacion_log N───1 sector (sector_id_predicho)
                                  N───1 sector (sector_id_validado)

 -- Multietiqueta (C-27): relaciones N-a-N con el catálogo sector
 incidente         N───N sector  (incidente_sector_adicional: sectores adicionales)
 clasificacion_log N───N sector  (clasificacion_sector_predicho: adicionales predichos)
 clasificacion_log N───N sector  (clasificacion_sector_validado: adicionales validados)
```

> ⚠️ `clasificacion_log` tiene **dos FK** hacia `sector.id`. Ambos lados de cada relationship llevan `foreign_keys` explícito — sin él, SQLAlchemy lanza `AmbiguousForeignKeysError` (bug ya corregido; ver [09](09_decisiones_y_supuestos.md) DD-09).

## Entidades (implementación real en `App/Backend/app/models/`)

### incidente
- `id` PK autoincremental; identificador legible con prefijo configurable (tesis §5.6).
- `descripcion` (texto pseudonimizado segun tesis §11.3 — implementado en C-03 via `utils/pseudonymizer.py`, patrones regex para `[PERSONA]`, `[EMAIL]`, `[TELEFONO]`, `[HOST]`).
- `prioridad`, `created_at`/`updated_at` (TimestampMixin, precisión ms).
- FK: `canal_origen_id`, `sector_id` (sector principal, nullable hasta clasificar), `estado_id`.
- Sectores adicionales: relación N-a-N con `sector` vía `incidente_sector_adicional` (solo el resto del conjunto; el principal no se duplica).
- Relación 1:N con `clasificacion_log` (cascade delete).

### sector
- `id` PK, `nombre` UNIQUE (`uq_sector_nombre`), `descripcion`.
- Valores sembrados: **Seguridad Informatica** · **Soporte Tecnico Hardware** · **Soporte Tecnico Software** · **Bases de Datos** · **Sistemas** (exactos, sin tildes).
- Relaciones inversas: `incidentes`, `clasificaciones` (con `foreign_keys=[ClasificacionLog.sector_id_predicho]`) y las tablas de unión multietiqueta.

### estado
- `id` PK, `nombre` UNIQUE, `descripcion`, `es_terminal` (bool).
- Valores: nuevo · en proceso · en espera · resuelto · cerrado (terminal).

### canal_origen
- `id` PK, `nombre` UNIQUE, `descripcion`.
- Valores: correo electrónico · formulario web · llamada telefónica.

### clasificacion_log
- `id` PK; `incidente_id` FK (CASCADE, indexada).
- `sector_id_predicho` FK→sector (SET NULL; null si fallback total).
- `confianza` Numeric(5,4) ∈ [0,1] — 0.0 señala fallo del clasificador.
- `etapa` String(30): `"deterministic"` | `"gemini"` | `"fallback"`.
- `requiere_revision_humana` bool (true cuando confianza < 0,70).
- `respuesta_raw` Text nullable — respuesta cruda de Gemini para auditoría.
- `sector_id_validado` FK→sector nullable — NULL hasta validación humana; su presencia saca el registro de la cola de revisión y lo convierte en etiqueta de verdad del corpus.
- Sectores adicionales predichos/validados: relaciones N-a-N con `sector` vía `clasificacion_sector_predicho` y `clasificacion_sector_validado` (el principal vive en la FK escalar).

### Tablas de unión multietiqueta (C-27)

| Tabla | PK compuesta | FK principal | FK sector | Propósito |
|---|---|---|---|---|
| `incidente_sector_adicional` | `(incidente_id, sector_id)` | `incidente_id` → `incidente(id)` CASCADE | `sector_id` → `sector(id)` RESTRICT | Sectores adicionales del incidente |
| `clasificacion_sector_predicho` | `(clasificacion_log_id, sector_id)` | `clasificacion_log_id` → `clasificacion_log(id)` CASCADE | `sector_id` → `sector(id)` RESTRICT | Adicionales predichos por el clasificador |
| `clasificacion_sector_validado` | `(clasificacion_log_id, sector_id)` | `clasificacion_log_id` → `clasificacion_log(id)` CASCADE | `sector_id` → `sector(id)` RESTRICT | Adicionales validados por el operador |

La PK compuesta impide duplicar el mismo sector adicional dentro de una entidad. El sector principal nunca se repite en estas tablas. Creadas por la migración `004_sectores_multietiqueta.py` con `downgrade` funcional.

## Seed data inicial (migraciones 001 y 004)

| Tabla | Registros |
|---|---|
| sector | Seguridad Informatica, Soporte Tecnico Hardware, Soporte Tecnico Software, Bases de Datos, Sistemas (migración 004; `Operaciones` eliminado) |
| estado | nuevo, en proceso, en espera, resuelto, cerrado (es_terminal=true) |
| canal_origen | correo electrónico, formulario web, llamada telefónica |

## Politica de conservacion (tesis v8 §11.2, corregida por C-18)

- Conservacion **indefinida** de todos los incidentes. Justificacion: valor estadistico de los datos historicos para analisis de tendencias e identificacion de problemas recurrentes.
- Incidentes en estado cerrado: registro auditable permanente. Pueden consultarse pero no editarse ni eliminarse desde la interfaz (bloqueo 409 implementado en C-23).
- La pseudonimizacion (regex pre-Gemini) y el cifrado Fernet (AES-128-CBC + HMAC-SHA-256) garantizan la proteccion de datos incluso en periodos prolongados.
- Logs de ejecucion N8N: poda automatica a 30 dias (`EXECUTIONS_DATA_PRUNE=true`, `EXECUTIONS_DATA_MAX_AGE=720` en `docker-compose.yml`).
