# Módulo de Pseudonimización — Documentación Técnica

> **Change C-03 (Ley 25.326)** · Gobernanza: ALTO · Revisión: aprobada  
> Aplica a: `Gestion_Incidentes/app/utils/pseudonymizer.py`, `encryption.py`, `app/models/incidente.py`, `app/services/incidente_service.py`, `alembic/versions/002_doble_representacion.py`

---

## 1. Arquitectura de doble representación

El módulo reemplaza la columna única `descripcion` del modelo `Incidente` por **dos representaciones**:

| Columna | Contenido | Almacenamiento | Expuesta en API | Consumidores |
|---------|-----------|----------------|-----------------|--------------|
| `descripcion_original` | Texto crudo con PII | **Cifrado Fernet** (at-rest) | NO | Solo auditoría / ARCO (fuera de alcance de la API normal) |
| `descripcion_pseudonimizada` | Texto con etiquetas `[EMAIL]`/`[TELEFONO]`/`[HOST]`/`[PERSONA]` | En claro | SÍ | Pipeline de clasificación (determinístico + Gemini), API, dashboards |

La separación garantiza que los datos personales nunca crucen la frontera hacia proveedores externos (Gemini, N8N) ni aparezcan en respuestas HTTP.

---

## 2. Categorías de PII y etiquetas

| Categoría | Patrón | Etiqueta | Conteo |
|-----------|--------|----------|--------|
| Email | RFC-5321 básico (dominio con punto) | `[EMAIL]` | `email` |
| Teléfono | Formatos AR: `+54 261 555-1234`, `2615551234`, `261 555-1234` | `[TELEFONO]` | `telefono` |
| Host interno | Dominios configurados + fallback: `srv-*`, `pc-*`, `*.local`, `localhost` | `[HOST]` | `host` |
| Nombre propio | Heurística regex: secuencias de ≥2 palabras capitalizadas (con tildes y `ñ`) | `[PERSONA]` | `persona` |

---

## 3. Orden de aplicación (libre de colisiones)

Los patrones se aplican **secuencialmente** en el orden siguiente:

1. `[EMAIL]` — alta especificidad; evita que el dominio o el local-part sean capturados como nombres
2. `[TELEFONO]` — secuencias numéricas con formato telefónico
3. `[HOST]` — identificadores de equipo (dominios configurados + fallback heurístico)
4. `[PERSONA]` — heurística de nombres (se aplica **después** de que emails/hosts ya son etiquetas `[MAYÚSCULAS]`)

**Invariante:** el patrón de persona **excluye** subcadenas de la forma `[MAYÚSCULAS]` para no re-procesar etiquetas ya insertadas. Un email como `juan.perez@empresa.com` colapsa a `[EMAIL]` antes de que la heurística de nombre lo fragmente.

---

## 4. Dominios internos parametrizados

La función pura recibe los dominios como argumento:

```python
pseudonymize(text, internal_domains=["corp.empresa.com", "empresa.local"])
```

La lista se configura en el entorno:

```
PSEUDONYMIZATION_INTERNAL_DOMAINS=["corp.empresa.com","empresa.local"]
```

Si la lista está vacía, solo actúa el fallback heurístico (`srv-*`, `pc-*`, `*.local`, `localhost`).

---

## 5. Cifrado Fernet — generación y manejo de la clave

### Generación

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Colocar el resultado en `.env`:

```
PSEUDONYMIZATION_ENCRYPTION_KEY=<clave-generada>
```

### Obligatoriedad

El campo es **obligatorio** en `Settings`. La app falla al arrancar (con error claro de pydantic-settings) si la variable no está configurada. Lo mismo ocurre al ejecutar `alembic upgrade head` cuando hay filas existentes a backfillear.

### Rotación manual (procedimiento operativo)

La rotación automática está fuera del alcance de este change. Para rotar la clave:

1. Generar una nueva clave Fernet.
2. Escribir un script de migración que descifre con la clave vieja y recifre con la nueva para cada fila de `incidente`.
3. Actualizar `PSEUDONYMIZATION_ENCRYPTION_KEY` en el entorno con la nueva clave.
4. Ejecutar el script antes de desplegar el nuevo código.

**Riesgo de pérdida de clave:** si se pierde la clave Fernet, `descripcion_original` queda ilegible de forma permanente. El dato operativo (`descripcion_pseudonimizada`) permanece intacto; solo se pierde la capacidad de auditoría/ARCO sobre el texto original. Hacer backups de la clave con el mismo nivel de seguridad que las credenciales de base de datos.

---

## 6. Límites del enfoque regex

El pseudonymizer usa expresiones regulares, **no NER ni modelos de aprendizaje automático** (decisión de la tesis, §11.5).

### Falsos negativos conocidos (PII que puede escapar)

- Nombres con una sola palabra capitalizada (apellidos sin nombre, alias)
- Nombres completamente en minúsculas en texto informal
- Teléfonos en formatos muy atípicos o sin separadores
- Emails sin punto en el dominio (poco frecuentes pero válidos)

### Falsos positivos conocidos (no-PII que puede enmascararse)

- Topónimos o marcas capitalizadas al inicio de oración → `[PERSONA]`
- Palabras técnicas capitalizadas fuera del listado de exclusión → `[PERSONA]`
- Números que coincidan con el patrón de teléfono (p. ej. números de versión largos)

### Lista de exclusión

Las tres categorías del clasificador (`Sistemas`, `Operaciones`, `Soporte Técnico`) y otras palabras del dominio se excluyen del patrón de nombres para no degradar la clasificación.

---

## 7. Riesgo de reidentificación residual

Aunque el texto pseudonimizado reemplaza los identificadores directos (nombre, email, teléfono, host), puede conservar **contexto organizacional** que permita la reidentificación indirecta (§11.5 de la tesis):

- Nombres de proyectos o áreas específicas no capturados por el regex
- Detalles técnicos únicos que identifiquen a un usuario particular

**Mitigaciones implementadas (C-03):**

1. La versión que cruza la frontera hacia Gemini es la pseudonimizada (§11.3 — transferencia internacional legitimada).
2. La original cifrada solo es accesible por auditoría (fuera del alcance de la API normal).
3. El log de cobertura es de nivel DEBUG y no expone texto.

**Mejoras futuras (fuera de alcance de la tesis):** anonimización diferencial, k-anonimato, NER para nombres propios (§11.5).

---

## 8. Auditoría DEBUG sin PII

Durante la creación de cada incidente, el service emite un evento de logging nivel **DEBUG**:

```python
logger.debug("pseudonimizacion_cobertura", email=1, telefono=0, host=1, persona=1)
```

- Contiene: los **conteos por categoría** (enteros).
- NO contiene: el texto original, el texto pseudonimizado, ni ningún fragmento de PII.
- El módulo `pseudonymizer.py` **no emite logs** (función pura sin efectos secundarios).

Para habilitarlo en producción: configurar el nivel de logging del logger `app.services.incidente_service` en `DEBUG`.

---

## 9. Acceso a la descripción original cifrada

El acceso a `descripcion_original` queda **fuera de los endpoints normales de la API** (restricción de diseño). No existe ningún endpoint REST en este change que exponga ese campo. Su acceso está reservado para:

- Ejercicio de derechos ARCO (Acceso, Rectificación, Cancelación, Oposición) por parte del titular, mediante procedimiento administrativo fuera de la API pública.
- Auditoría interna con acceso directo a la base de datos (previa autorización).

Implementar un endpoint de auditoría con autenticación reforzada queda como línea futura (§11.4).

---

## 10. Migración Alembic 002

La migración `002_doble_representacion.py` aplica la estrategia **nullable → backfill → not null → drop**:

```
upgrade:
  1. ADD COLUMN descripcion_pseudonimizada TEXT NULL
  2. ADD COLUMN descripcion_original       TEXT NULL
  3. Backfill: para cada fila con 'descripcion', pseudonimizar → pseudo; cifrar → original
  4. ALTER COLUMN descripcion_pseudonimizada NOT NULL
  5. ALTER COLUMN descripcion_original       NOT NULL
  6. DROP COLUMN descripcion

downgrade:
  1. ADD COLUMN descripcion TEXT NULL
  2. Backfill inverso: descifrar descripcion_original → descripcion
  3. ALTER COLUMN descripcion NOT NULL
  4. DROP COLUMN descripcion_pseudonimizada
  5. DROP COLUMN descripcion_original
```

Usa `op.batch_alter_table` para compatibilidad con SQLite (suite de tests) y PostgreSQL (producción).

**Prerequisito:** `PSEUDONYMIZATION_ENCRYPTION_KEY` debe estar en el entorno antes de ejecutar `alembic upgrade head`. Sin la clave, el backfill falla con un error claro.
