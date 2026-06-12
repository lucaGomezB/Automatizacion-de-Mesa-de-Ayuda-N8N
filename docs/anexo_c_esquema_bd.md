# Anexo C — Esquema de Base de Datos

> **Fuente de verdad**: este documento se deriva fielmente de los modelos ORM
> ubicados en `Gestion_Incidentes/app/models/`. La fuente ejecutable de las
> migraciones es Alembic (`Gestion_Incidentes/alembic/`); este anexo es la
> vista documental consolidada para el jurado. (Decisión D4 de C-10.)
>
> Motor de base de datos: **PostgreSQL 15.5**.

---

## Tablas de catálogo

### `sector`

Catálogo de sectores responsables de atender los incidentes. Valores sembrados
en la migración inicial: `Sistemas`, `Operaciones`, `Soporte Técnico`.

```sql
CREATE TABLE sector (
    id          SERIAL          PRIMARY KEY,
    nombre      VARCHAR(100)    NOT NULL,
    descripcion VARCHAR(500),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_sector_nombre UNIQUE (nombre)
);

-- Índice implícito por el UNIQUE constraint sobre nombre
-- Índice de auditoría temporal:
CREATE INDEX ix_sector_created_at ON sector (created_at);
```

**Relaciones**:
- Referenciada por `incidente.sector_id` (FK con `ON DELETE SET NULL`).
- Referenciada por `clasificacion_log.sector_id_predicho` y `clasificacion_log.sector_id_validado`
  (ambas FK con `ON DELETE SET NULL`).

---

### `estado`

Catálogo de estados del ciclo de vida de un incidente.
Valores: `nuevo`, `en proceso`, `en espera`, `resuelto`, `cerrado`.

```sql
CREATE TABLE estado (
    id          SERIAL          PRIMARY KEY,
    nombre      VARCHAR(50)     NOT NULL,
    descripcion VARCHAR(300),
    es_terminal BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_estado_nombre UNIQUE (nombre)
);

CREATE INDEX ix_estado_created_at ON estado (created_at);
```

**Relaciones**:
- Referenciada por `incidente.estado_id` (FK con `ON DELETE RESTRICT`).
  La acción `RESTRICT` evita eliminar un estado que tenga incidentes activos.

---

### `canal_origen`

Catálogo de canales de ingreso de incidentes.
Valores: `correo electrónico`, `formulario web`, `llamada telefónica`.

```sql
CREATE TABLE canal_origen (
    id          SERIAL          PRIMARY KEY,
    nombre      VARCHAR(100)    NOT NULL,
    descripcion VARCHAR(300),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_canal_origen_nombre UNIQUE (nombre)
);

CREATE INDEX ix_canal_origen_created_at ON canal_origen (created_at);
```

**Relaciones**:
- Referenciada por `incidente.canal_origen_id` (FK con `ON DELETE SET NULL`).

---

## Tabla principal

### `incidente`

Entidad central del sistema. Almacena cada ticket de soporte con **doble
representación de la descripción** (ver sección debajo) y los índices compuestos
para las consultas de panel y cola de trabajo.

```sql
CREATE TABLE incidente (
    id                          SERIAL          PRIMARY KEY,

    -- Doble representación de la descripción (arquitectura C-03 / Ley 25.326)
    descripcion_original        TEXT            NOT NULL,   -- cifrado at-rest con Fernet
    descripcion_pseudonimizada  TEXT            NOT NULL,   -- texto en claro con etiquetas PII

    prioridad                   VARCHAR(20)     NOT NULL DEFAULT 'media',
                                                -- Valores: 'baja' | 'media' | 'alta' | 'critica'

    -- FK → sector: SET NULL permite que el sector sea null mientras se clasifica
    sector_id                   INTEGER         REFERENCES sector(id)
                                                ON DELETE SET NULL,

    -- FK → estado: RESTRICT evita borrar un estado con incidentes activos
    estado_id                   INTEGER         NOT NULL
                                                REFERENCES estado(id)
                                                ON DELETE RESTRICT,

    -- FK → canal_origen: SET NULL si el incidente se creó por API sin canal
    canal_origen_id             INTEGER         REFERENCES canal_origen(id)
                                                ON DELETE SET NULL,

    requiere_revision_humana    BOOLEAN         NOT NULL DEFAULT FALSE,

    created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Índice simple sobre sector_id (para FK lookups)
CREATE INDEX ix_incidente_sector_id ON incidente (sector_id);

-- Índice simple sobre estado_id (para FK lookups)
CREATE INDEX ix_incidente_estado_id ON incidente (estado_id);

-- Índice temporal de auditoría
CREATE INDEX ix_incidente_created_at ON incidente (created_at);

-- ── Índices compuestos (optimización de consultas frecuentes) ─────────────────

-- Panel de control: incidentes por sector en rango de fechas
CREATE INDEX ix_incidente_created_sector ON incidente (created_at, sector_id);

-- Cola de trabajo: incidentes activos ordenados por antigüedad
CREATE INDEX ix_incidente_estado_created ON incidente (estado_id, created_at);
```

### Doble representación de la descripción

| Campo                      | Tipo  | Contenido                             | Exposición |
|----------------------------|-------|---------------------------------------|------------|
| `descripcion_original`     | TEXT  | Texto crudo del usuario, **cifrado at-rest** con Fernet (`EncryptedText`). Solo para auditoría y ejercicio de derechos ARCO (Ley 25.326). | No expuesto por la API |
| `descripcion_pseudonimizada` | TEXT | Texto con PII reemplazada por etiquetas: `[EMAIL]`, `[TELEFONO]`, `[HOST]`, `[PERSONA]`. | Consumida por el clasificador y expuesta en la API |

La pseudonimización ocurre una sola vez en `IncidenteService.create_and_classify()`,
antes de la persistencia. El cifrado de `descripcion_original` usa la clave Fernet
configurada en la variable de entorno `PSEUDONYMIZATION_ENCRYPTION_KEY`.

---

## Tabla de auditoría

### `clasificacion_log`

Registro de cada decisión del clasificador híbrido para un incidente.
Permite calcular métricas de exactitud (accuracy, F1 por categoría) y
analizar la distribución de confianza del sistema.

La tabla tiene **dos claves foráneas distintas apuntando a `sector.id`**:
`sector_id_predicho` (clasificación automática) y `sector_id_validado`
(corrección del operador humano). Esta doble FK es la razón por la cual
los modelos ORM usan `foreign_keys` explícitos en las relaciones SQLAlchemy
para evitar `AmbiguousForeignKeysError`.

```sql
CREATE TABLE clasificacion_log (
    id                      SERIAL          PRIMARY KEY,

    -- FK → incidente: CASCADE garantiza limpieza al eliminar un incidente
    incidente_id            INTEGER         NOT NULL
                                            REFERENCES incidente(id)
                                            ON DELETE CASCADE,

    -- Predicción del clasificador; NULL si el clasificador falló (etapa="fallback")
    sector_id_predicho      INTEGER         REFERENCES sector(id)
                                            ON DELETE SET NULL,

    -- Confianza normalizada en [0.0, 1.0] con 4 decimales de precisión
    confianza               NUMERIC(5, 4)   NOT NULL,

    -- Etapa del pipeline: 'deterministic' | 'gemini' | 'fallback'
    etapa                   VARCHAR(30)     NOT NULL,

    requiere_revision_humana BOOLEAN        NOT NULL DEFAULT FALSE,

    -- Respuesta cruda de Gemini (NULL en etapa deterministic)
    respuesta_raw           TEXT,

    -- Validación humana: llenada a posteriori por el operador
    -- NULL mientras aguarda revisión; filled cuando el ciclo se completa
    sector_id_validado      INTEGER         REFERENCES sector(id)
                                            ON DELETE SET NULL,

    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Índice sobre incidente_id para recuperar el historial de un incidente
CREATE INDEX ix_clasificacion_log_incidente_id ON clasificacion_log (incidente_id);

-- Índice temporal de auditoría
CREATE INDEX ix_clasificacion_log_created_at ON clasificacion_log (created_at);
```

### Doble FK a `sector` en `clasificacion_log`

| Campo               | FK destino    | ON DELETE   | Semántica |
|---------------------|---------------|-------------|-----------|
| `sector_id_predicho`| `sector(id)`  | SET NULL    | Sector que el clasificador asignó automáticamente |
| `sector_id_validado`| `sector(id)`  | SET NULL    | Sector confirmado/corregido por el operador humano |

Cuando `sector_id_validado` es distinto de `sector_id_predicho`, el registro
documenta un error del clasificador y contribuye al análisis de métricas de la tesis.

---

## Resumen de restricciones ON DELETE

| FK origen                        | FK destino        | ON DELETE   | Justificación |
|----------------------------------|-------------------|-------------|---------------|
| `incidente.estado_id`            | `estado(id)`      | **RESTRICT**    | No borrar un estado si hay incidentes activos |
| `incidente.sector_id`            | `sector(id)`      | **SET NULL**    | El incidente persiste sin sector asignado |
| `incidente.canal_origen_id`      | `canal_origen(id)`| **SET NULL**    | El incidente persiste sin canal registrado |
| `clasificacion_log.incidente_id` | `incidente(id)`   | **CASCADE**     | Los logs son dependientes del incidente; se borran con él |
| `clasificacion_log.sector_id_predicho` | `sector(id)` | **SET NULL** | El log persiste; se pierde la referencia al sector |
| `clasificacion_log.sector_id_validado` | `sector(id)` | **SET NULL** | Idem |

---

## Resumen de índices compuestos

| Índice                          | Tabla       | Columnas                     | Propósito |
|---------------------------------|-------------|------------------------------|-----------|
| `ix_incidente_created_sector`   | `incidente` | `(created_at, sector_id)`    | Panel de control: incidentes por sector en rango de fechas |
| `ix_incidente_estado_created`   | `incidente` | `(estado_id, created_at)`    | Cola de trabajo: incidentes activos por antigüedad |
