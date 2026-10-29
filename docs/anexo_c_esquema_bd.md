# Anexo C — Esquema de Base de Datos

> **Fuente de verdad**: este documento se deriva fielmente de los modelos ORM
> ubicados en `App/Backend/app/models/`. La fuente ejecutable de las
> migraciones es Alembic (`App/Backend/alembic/`); este anexo es la
> vista documental consolidada para el jurado. (Decisión D4 de C-10.)
>
> Motor de base de datos: **PostgreSQL 15.5**.

---

## Tablas de catálogo

### `sector`

Catálogo de sectores responsables de atender los incidentes. Los cinco valores
canónicos vigentes (exactos, sin tildes) fueron sembrados/upsertados por la
migración `004_sectores_multietiqueta.py`: `Seguridad Informatica`,
`Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos` y
`Sistemas`. Las filas legacy `Operaciones` y `Soporte Técnico` fueron eliminadas
por esa misma migración (C-27).

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

## Estructuras multietiqueta (migración `004_sectores_multietiqueta.py`)

La migración `004` (C-27) agrega tres tablas de unión para la verdad multietiqueta.
En las tres, el sector **principal** no se duplica: vive en la FK escalar
correspondiente (`incidente.sector_id`, `clasificacion_log.sector_id_predicho`,
`clasificacion_log.sector_id_validado`). La clave primaria compuesta impide
repetir el mismo sector adicional dentro de una entidad.

```sql
-- Sectores adicionales del incidente (relación N-a-N)
CREATE TABLE incidente_sector_adicional (
    incidente_id    INTEGER NOT NULL REFERENCES incidente(id) ON DELETE CASCADE,
    sector_id       INTEGER NOT NULL REFERENCES sector(id)    ON DELETE RESTRICT,
    PRIMARY KEY (incidente_id, sector_id)
);

-- Sectores adicionales predichos por el clasificador
CREATE TABLE clasificacion_sector_predicho (
    clasificacion_log_id INTEGER NOT NULL REFERENCES clasificacion_log(id) ON DELETE CASCADE,
    sector_id            INTEGER NOT NULL REFERENCES sector(id)            ON DELETE RESTRICT,
    PRIMARY KEY (clasificacion_log_id, sector_id)
);

-- Sectores adicionales validados por el operador humano
CREATE TABLE clasificacion_sector_validado (
    clasificacion_log_id INTEGER NOT NULL REFERENCES clasificacion_log(id) ON DELETE CASCADE,
    sector_id            INTEGER NOT NULL REFERENCES sector(id)            ON DELETE RESTRICT,
    PRIMARY KEY (clasificacion_log_id, sector_id)
);
```

**Relaciones**:
- `incidente_sector_adicional` referencia `incidente` (CASCADE) y `sector` (RESTRICT).
- `clasificacion_sector_predicho` y `clasificacion_sector_validado` referencian
  `clasificacion_log` (CASCADE) y `sector` (RESTRICT).
- `RESTRICT` en `sector` evita eliminar un sector referenciado por un conjunto
  adicional; `CASCADE` limpia las uniones al eliminar la entidad dueña.

---

## Directorio de empleados y su auditoría

### `directorio_empleado`

Directorio interno de la mesa de ayuda (c-54, endurecido por c-153). Es una
entidad de contacto SEPARADA de la autenticación (`users`): `user_id` es un
vínculo opcional. El contacto personal (`email`, `telefono`) se almacena
**cifrado at-rest con Fernet** (`EncryptedText`); como el ciphertext Fernet no es
determinista, la unicidad y la búsqueda por contacto se resuelven con un **índice
ciego** determinista (HMAC-SHA-256 de la forma normalizada, c-153 DIR-011),
materializado en `email_bidx` (UNIQUE) y `telefono_bidx` (no UNIQUE: el teléfono
es repetible). El vocabulario de `rol` tiene **cuatro** valores exactos.

```sql
CREATE TABLE directorio_empleado (
    id              SERIAL          PRIMARY KEY,

    legajo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(200)    NOT NULL,

    -- Contacto cifrado at-rest con Fernet (`EncryptedText`, c-153)
    email           TEXT            NOT NULL,   -- cifrado at-rest con Fernet
    telefono        TEXT,                       -- E.164, opcional; cifrado at-rest con Fernet

    -- Índice ciego determinista (HMAC-SHA-256, c-153 DIR-011); no es PII en claro.
    -- La unicidad del email vive sobre `email_bidx` (el ciphertext no es determinista).
    email_bidx      VARCHAR(64),
    telefono_bidx   VARCHAR(64),

    -- FK → sector: SET NULL permite desasociar el sector sin borrar al empleado
    sector_id       INTEGER         REFERENCES sector(id)
                                    ON DELETE SET NULL,

    rol             VARCHAR(30)     NOT NULL,

    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    -- Instante de desactivación (retención DIR-007); NULL = activo
    fecha_baja      TIMESTAMPTZ,

    -- FK → users (autenticación): SET NULL desvincula la cuenta sin borrar al empleado
    user_id         INTEGER         REFERENCES users(id)
                                    ON DELETE SET NULL,

    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_directorio_empleado_legajo UNIQUE (legajo),
    CONSTRAINT uq_directorio_empleado_email_bidx UNIQUE (email_bidx),
    CONSTRAINT ck_directorio_empleado_rol CHECK (
        rol IN ('usuario_final', 'mesa_de_ayuda',
                'administrador_directorio', 'gestion_incidentes')
    )
);

-- Índices simples (FK lookups y búsquedas por contacto vía índice ciego)
CREATE INDEX ix_directorio_empleado_email_bidx ON directorio_empleado (email_bidx);
CREATE INDEX ix_directorio_empleado_telefono_bidx ON directorio_empleado (telefono_bidx);
CREATE INDEX ix_directorio_empleado_sector_id ON directorio_empleado (sector_id);
CREATE INDEX ix_directorio_empleado_user_id ON directorio_empleado (user_id);
```

**Vocabulario de `rol`** (cuatro valores, `ck_directorio_empleado_rol`):

| Valor | Alcance |
|-------|---------|
| `usuario_final` | Reportante; alcance PROPIO (solo lo que reportó). |
| `mesa_de_ayuda` | Rol transversal; alcance GLOBAL, privilegiado. |
| `administrador_directorio` | Alcance GLOBAL, privilegiado; gestiona el directorio. |
| `gestion_incidentes` | Rol operativo por sector (c-86); alcance SECTOR, no privilegiado. |

**Relaciones**:
- `directorio_empleado.sector_id` → `sector(id)` (FK con `ON DELETE SET NULL`).
- `directorio_empleado.user_id` → `users(id)` (FK con `ON DELETE SET NULL`;
  `users` es la tabla de autenticación y no se detalla en este anexo).
- No es referenciada por ninguna otra tabla del esquema.

### `directorio_auditoria`

Traza DURABLE y **append-only** de las operaciones del directorio (c-153, DIR-013),
análoga a `incidente_evento`. Almacena solo identificadores internos, la operación,
el resultado, el canal de resolución y el instante: NUNCA email, teléfono, nombre
ni otro dato personal en claro. No existe endpoint ni método de edición o borrado
y el modelo **no** expone `updated_at` (no hereda `TimestampMixin`). Los
identificadores `empleado_id` y `actor_empleado_id` son enteros internos OPACOS
**sin clave foránea**: una traza de auditoría no debe imponer un acoplamiento
referencial que pueda hacer fallar la operación que audita.

```sql
CREATE TABLE directorio_auditoria (
    id                  SERIAL          PRIMARY KEY,

    operacion           VARCHAR(40)     NOT NULL,
    resultado           VARCHAR(20)     NOT NULL,
    canal               VARCHAR(20),    -- 'email' | 'telefono' | 'usuario'; NULL en gestión

    -- Identificadores internos opacos, SIN FK (la traza no impone acoplamiento referencial)
    empleado_id         INTEGER,
    actor_empleado_id   INTEGER,

    -- Inmutable: no existe `updated_at` (append-only)
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_directorio_auditoria_empleado_id ON directorio_auditoria (empleado_id);
CREATE INDEX ix_directorio_auditoria_actor_empleado_id ON directorio_auditoria (actor_empleado_id);
CREATE INDEX ix_directorio_auditoria_created_at ON directorio_auditoria (created_at);
```

**Relaciones**:
- Sin claves foráneas: los identificadores son internos y opacos por diseño
  (DIR-013), de modo que el borrado ARCO de un empleado no elimina la traza.

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
| `incidente_sector_adicional.incidente_id` | `incidente(id)` | **CASCADE** | Las uniones de sectores adicionales dependen del incidente |
| `incidente_sector_adicional.sector_id` | `sector(id)` | **RESTRICT** | No borrar un sector referenciado por un conjunto adicional |
| `clasificacion_sector_predicho.clasificacion_log_id` | `clasificacion_log(id)` | **CASCADE** | Las uniones predichas dependen del log |
| `clasificacion_sector_predicho.sector_id` | `sector(id)` | **RESTRICT** | Integridad referencial del catálogo |
| `clasificacion_sector_validado.clasificacion_log_id` | `clasificacion_log(id)` | **CASCADE** | Las uniones validadas dependen del log |
| `clasificacion_sector_validado.sector_id` | `sector(id)` | **RESTRICT** | Integridad referencial del catálogo |
| `directorio_empleado.sector_id` | `sector(id)` | **SET NULL** | El empleado persiste sin sector asignado |
| `directorio_empleado.user_id` | `users(id)` | **SET NULL** | La cuenta se desvincula sin borrar al empleado |

> `directorio_auditoria` no aporta filas: sus identificadores son internos y
> opacos, sin clave foránea (DIR-013).

---

## Resumen de índices compuestos

| Índice                          | Tabla       | Columnas                     | Propósito |
|---------------------------------|-------------|------------------------------|-----------|
| `ix_incidente_created_sector`   | `incidente` | `(created_at, sector_id)`    | Panel de control: incidentes por sector en rango de fechas |
| `ix_incidente_estado_created`   | `incidente` | `(estado_id, created_at)`    | Cola de trabajo: incidentes activos por antigüedad |

> `directorio_empleado` y `directorio_auditoria` solo agregan índices simples
> (FK, índice ciego del contacto y sello temporal); no definen índices compuestos.
