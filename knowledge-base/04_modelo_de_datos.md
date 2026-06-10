# Modelo de Datos

## Dominios

- **Incidentes**: ticket central con ciclo de vida (estado) y derivación (sector).
- **Catálogos**: vocabulario controlado inmutable en runtime (sector, estado, canal_origen) — sembrado por migración Alembic `001_seed_catalogs.py`.
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
```

> ⚠️ `clasificacion_log` tiene **dos FK** hacia `sector.id`. Ambos lados de cada relationship llevan `foreign_keys` explícito — sin él, SQLAlchemy lanza `AmbiguousForeignKeysError` (bug ya corregido; ver [09](09_decisiones_y_supuestos.md) DD-09).

## Entidades (implementación real en `Gestion_Incidentes/app/models/`)

### incidente
- `id` PK autoincremental; identificador legible con prefijo configurable (tesis §5.6).
- `descripcion` (texto crudo **pseudonimizado** según tesis §11.3 — pendiente C-03).
- `prioridad`, `created_at`/`updated_at` (TimestampMixin, precisión ms).
- FK: `canal_origen_id`, `sector_id` (nullable hasta clasificar), `estado_id`.
- Relación 1:N con `clasificacion_log` (cascade delete).

### sector
- `id` PK, `nombre` UNIQUE (`uq_sector_nombre`), `descripcion`.
- Valores sembrados: **Sistemas** · **Operaciones** · **Soporte Técnico**.
- Relaciones inversas: `incidentes`, `clasificaciones` (con `foreign_keys=[ClasificacionLog.sector_id_predicho]`).

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

## Seed data inicial (migración 001)

| Tabla | Registros |
|---|---|
| sector | Sistemas, Operaciones, Soporte Técnico |
| estado | nuevo, en proceso, en espera, resuelto, cerrado (es_terminal=true) |
| canal_origen | correo electrónico, formulario web, llamada telefónica |

## Reglas de retención (tesis §11.2 — pendiente de implementar)

- Registros operativos: 90 días.
- Incidentes resueltos: 1 año → luego anonimizar o eliminar.
- Logs de ejecución N8N: 30 días.
