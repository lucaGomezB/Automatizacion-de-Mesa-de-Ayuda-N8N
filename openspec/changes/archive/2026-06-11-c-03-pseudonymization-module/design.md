## Context

> **Revisión incorporada (Gobernanza ALTO — Ley 25.326).** Este diseño fue **revisado y ampliado** respecto de la versión inicial (que persistía únicamente el texto original y pseudonimizaba solo en el egreso a Gemini). El revisor humano aprobó una arquitectura de **doble representación con cifrado at-rest**. Las decisiones 1–4 del revisor (ver `proposal.md` → "Decisiones de gobernanza aprobadas") son **vinculantes** y reemplazan el alcance anterior. Las Decisiones técnicas de este documento son la elaboración de ingeniería de esas cuatro decisiones.

El pipeline de clasificación tiene un único punto de egreso de datos hacia infraestructura externa: la llamada a la API de Gemini en `GeminiClassifier.classify()` (`app/classifiers/gemini_classifier.py`). Allí la descripción se concatena al prompt (`prompt = f"{_PROMPT_TEMPLATE}\n\nDESCRIPCIÓN DEL INCIDENTE:\n{descripcion}"`, línea 255) y se envía con `self._client.aio.models.generate_content(...)` envuelto en `asyncio.wait_for` (SDK nuevo `google-genai`: `genai.Client`).

Estado actual relevante (verificado en el código real):
- `IncidenteService.create_and_classify(payload)` (`app/services/incidente_service.py`) es el método canónico de creación. **Persiste `payload.descripcion` en crudo** (`self._incidente_repo.create(descripcion=payload.descripcion, ...)`, ~línea 180) y **luego** llama `self._classifier.classify(payload.descripcion)` (~línea 191) con el mismo texto crudo. *(El brief mencionaba `create_incidente()`; el nombre real es `create_and_classify()`.)*
- El modelo `Incidente` (`app/models/incidente.py`) tiene **una sola** columna de texto: `descripcion: Mapped[str]` (`Text`, `nullable=False`). Su docstring afirma erróneamente que el texto "ya está pseudonimizado por el flujo de N8N"; esa afirmación es falsa hoy y queda obsoleta con este diseño.
- `HybridClassifier.classify(descripcion)` ejecuta primero `DeterministicClassifier` (local, sin egreso). Si confianza ≥ 0.90 cortocircuita y **nunca** llega a Gemini; solo si < 0.90 invoca `self._gemini.classify(descripcion)`.
- `IncidenteRead` (`app/schemas/incidente.py`) expone `descripcion: str` en el detalle (`GET /api/v1/incidentes/{id}`). `IncidenteListItem` NO la expone. El `IncidenteCreate` recibe `descripcion` (texto crudo del usuario/N8N).
- `BaseRepository.create(**kwargs)` es genérico: agregar columnas no requiere tocar el repositorio.
- La migración inicial existente es `alembic/versions/001_seed_catalogs.py` (`revision="001"`, `down_revision=None`). La nueva migración será **`002`**.
- `requirements.txt` usa `google-genai>=1.0`, `pydantic-settings==2.5.2`, `sqlalchemy[asyncio]==2.0.36`, `alembic==1.13.3`, `aiosqlite` para tests. **No** incluye `cryptography`. **No** existe `.env.example` en el repo (settings lee de `.env`).

Restricciones del entorno:
- Python 3.12 (corre 3.13), FastAPI 0.115; todo el camino de clasificación es `async def`.
- Strict TDD habilitado para apply: cada patrón regex y cada utilidad se construye test-first.
- Convención de capas: `routes → services → repositories → models`; `utils/` es la capa más baja y NO importa de `classifiers/` ni `services/`. La función pura del pseudonymizer no hace I/O.
- Portabilidad de tests: la suite corre sobre **SQLite (`aiosqlite`)**; producción usa **PostgreSQL (`asyncpg`)**. Toda decisión de cifrado/persistencia debe ser idéntica en ambos motores.
- Gobernanza ALTO (Ley 25.326): la implementación NO comienza sin OK final del revisor sobre esta revisión.

## Goals / Non-Goals

**Goals:**
- **Doble representación** en `Incidente`: `descripcion_original` (texto crudo, **cifrado at-rest**) y `descripcion_pseudonimizada` (texto operativo en claro).
- Pseudonimizar **en la creación del incidente** (capa service, al persistir): `descripcion_pseudonimizada` se puebla ahí y es la **única** entrada del pipeline de clasificación.
- La IA (Gemini) procesa **únicamente** `descripcion_pseudonimizada`.
- La **API expone únicamente** la versión pseudonimizada; la original queda cifrada y **fuera** de los endpoints normales (acceso de auditoría fuera de alcance de este change).
- Función pura `pseudonymize(text, internal_domains) -> PseudonymizationResult` con regex compiladas a nivel de módulo: emails → `[EMAIL]`, teléfonos → `[TELEFONO]`, hosts internos → `[HOST]`, nombres propios → `[PERSONA]`. Devuelve también **conteos por categoría** (para auditoría DEBUG sin PII).
- **Hosts internos parametrizados** por settings (`pseudonymization_internal_domains`) + heurísticas genéricas de fallback (`srv-*`, `pc-*`, `*.local`, `localhost`).
- **Cifrado Fernet** app-level (`cryptography`), clave simétrica en `PSEUDONYMIZATION_ENCRYPTION_KEY` vía pydantic-settings; portable PostgreSQL/SQLite; clave rotable.
- **Auditoría de cobertura**: log nivel DEBUG con conteo de reemplazos por categoría, sin exponer PII.
- Migración Alembic `002` que agrega ambas columnas y trata las filas existentes.
- Cobertura test-first por patrón + casos borde + integración + cifrado + migración; documentación en `docs/pseudonymization.md`.

**Non-Goals:**
- NO se introduce NER ni modelos de ML para nombres propios (la tesis acepta el enfoque regex y su tradeoff; §11.5 lo declara como línea futura).
- NO se construye un endpoint de acceso de auditoría a la `descripcion_original` cifrada (queda fuera de alcance; se documenta como restricción).
- NO se cambia el SDK de Gemini ni los parámetros del modelo (Anexo H §H.2).
- NO se rota la clave automáticamente ni se implementa envelope encryption / KMS (la clave única rotable manualmente basta para el alcance de la tesis; mejora futura declarada).
- NO se pseudonimiza la etapa determinística como tal: recibe directamente la pseudonimizada porque es la única representación operativa (ver Decisión 3).

## Decisions

### Decisión 1 — Arquitectura de doble representación (reemplaza "persistir solo el original")

**Elegido:** el modelo `Incidente` pasa a tener DOS columnas de texto:

| Columna | Contenido | At-rest | Expuesta en API | Consumidores |
|---------|-----------|---------|-----------------|--------------|
| `descripcion_original` | Texto crudo con PII | **CIFRADO (Fernet)** | NO | Solo auditoría (fuera de alcance de este change) |
| `descripcion_pseudonimizada` | Texto con etiquetas `[EMAIL]/[TELEFONO]/[HOST]/[PERSONA]` | En claro | SÍ | Pipeline de clasificación (Gemini + determinístico), dashboards, reportes, búsquedas |

**Rationale:** separa el dato sensible (minimizado y cifrado, solo para ejercer ARCO y trazabilidad bajo §11.4/§11.5) del dato operativo (pseudonimizado, el que realmente usa el sistema). La transferencia internacional a Gemini queda legitimada porque lo que cruza la frontera es exclusivamente la versión pseudonimizada (§11.3). El frontend, los reportes y las búsquedas nunca tocan PII.

**Consecuencia sobre la columna `descripcion` actual:** se **renombra conceptualmente**. Decisión concreta de migración en Decisión 5. El docstring obsoleto del modelo ("pseudonimizada por N8N") se corrige: N8N ya no garantiza nada; la pseudonimización ahora ocurre dentro de esta API.

### Decisión 2 — Punto canónico de pseudonimización: capa service, en la creación (UN solo punto)

**Elegido:** la pseudonimización corre **una sola vez**, en `IncidenteService.create_and_classify()`, **antes** de persistir. El flujo nuevo es:

```python
# app/services/incidente_service.py (pseudocódigo del diseño)
async def create_and_classify(self, payload: IncidenteCreate) -> Incidente:
    ...
    resultado = pseudonymize(payload.descripcion, self._internal_domains)
    incidente = await self._incidente_repo.create(
        descripcion_original=payload.descripcion,         # se cifra at-rest (Decisión 4)
        descripcion_pseudonimizada=resultado.texto,       # claro, operativo
        ...
    )
    logger.debug("pseudonimizacion_cobertura", **resultado.conteos)  # DEBUG, sin PII
    result = await self._classifier.classify(resultado.texto)        # IA recibe SOLO pseudonimizada
    ...
```

**`GeminiClassifier` confía en recibir texto ya pseudonimizado (KISS — sin llamada defensiva).** El punto canónico es el service; `GeminiClassifier.classify()` y `HybridClassifier.classify()` reciben `descripcion_pseudonimizada` y **NO** vuelven a pseudonimizar.

**Rationale (KISS + SRP):** un único punto de transformación elimina ambigüedad sobre "quién pseudonimiza" y evita doble trabajo / doble masking (que produciría etiquetas anidadas). Dado que la pseudonimizada es la **única** representación operativa que sale del service hacia el clasificador, es *imposible* que un texto crudo llegue a Gemini sin pasar por el service. La defensa en profundidad se logra estructuralmente (el clasificador nunca ve `descripcion_original`), no con un segundo `pseudonymize()` redundante.

**Trade-off asumido y mitigación:** se renuncia a la garantía "localizada en el punto de egreso" del diseño previo. A cambio, se documenta explícitamente el contrato: *el argumento `descripcion` de `GeminiClassifier.classify`/`HybridClassifier.classify` DEBE ser texto ya pseudonimizado; el único llamador en producción es el service, que lo garantiza.* Los docstrings (que hoy ya dicen "Texto pseudonimizado del incidente") pasan a ser **verdad** por construcción. Un test de integración a nivel service verifica que Gemini recibe la versión pseudonimizada (ver tasks).

**Alternativas consideradas:**
- **Pseudonimizar dentro de `GeminiClassifier` (diseño previo)** — descartado: con doble representación, la pseudonimizada ya existe persistida; volver a pseudonimizar en el clasificador sería trabajo redundante sobre un texto que ya está enmascarado y rompería el principio de "una sola fuente operativa".
- **Doble pseudonimización (service + clasificador, defensiva)** — descartada por KISS: el masking no es idempotente respecto de conteos y podría re-procesar etiquetas; introduce complejidad sin beneficio real dado el contrato estructural.

### Decisión 3 — La etapa determinística también consume la pseudonimizada

**Elegido:** `HybridClassifier` recibe `descripcion_pseudonimizada` y la pasa tanto al determinístico como a Gemini.

**Rationale:** la pseudonimizada es la única representación operativa. El `DeterministicClassifier` matchea palabras clave técnicas del dominio ("servidor", "impresora", "red"…), que **no** son PII y por tanto **no** son enmascaradas por el pseudonymizer; su recall no se degrada. Mantener una sola entrada para ambas etapas simplifica el contrato del clasificador.

**Trade-off / verificación:** existe un riesgo teórico de que un nombre propio enmascarado como `[PERSONA]` coincidiera con una keyword determinística — improbable porque las keywords son sustantivos comunes en minúscula. Se cubre con un test de que el determinístico sigue clasificando correctamente sobre texto pseudonimizado representativo.

### Decisión 4 — Cifrado at-rest: TypeDecorator de SQLAlchemy con Fernet (elegido sobre helper manual)

**Elegido:** un **`TypeDecorator`** de SQLAlchemy (`EncryptedText`) en `app/utils/encryption.py` que cifra al escribir (`process_bind_param`) y descifra al leer (`process_result_value`) de forma **transparente**, usando Fernet (`cryptography`). La columna `descripcion_original` se declara `mapped_column(EncryptedText, ...)`.

```python
# app/utils/encryption.py (forma del diseño)
from cryptography.fernet import Fernet
from sqlalchemy import Text, TypeDecorator

class EncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True
    def process_bind_param(self, value, dialect):   # Python -> DB (cifra)
        if value is None: return None
        return _get_fernet().encrypt(value.encode("utf-8")).decode("ascii")
    def process_result_value(self, value, dialect): # DB -> Python (descifra)
        if value is None: return None
        return _get_fernet().decrypt(value.encode("ascii")).decode("utf-8")
```

La clave se resuelve perezosamente desde `settings.pseudonymization_encryption_key` (no al importar, para no romper imports en tests sin clave). Se documenta la generación: `Fernet.generate_key()`.

**Rationale (TypeDecorator vs helper manual):**
- **Transparencia y SRP:** el cifrado vive en el tipo de columna; el service, los repositorios y los schemas escriben/leen `descripcion_original` como un `str` normal. Nadie tiene que recordar llamar `encrypt()`/`decrypt()` — imposible olvidar un cifrado.
- **Portabilidad PostgreSQL/SQLite:** el ciphertext es texto base64 (`Text`); idéntico en ambos motores. No depende de `pgcrypto` ni de extensiones del servidor (a diferencia de cifrado en la DB), lo que mantiene los tests sobre SQLite fieles a producción.
- **Testabilidad:** `EncryptedText` se testea aislado (round-trip cifrar→descifrar) y el modelo se testea con una clave de prueba inyectada vía settings override.
- **Clave rotable:** al ser app-level, rotar la clave es cambiar la env var (con el ciclo de descifrado-con-clave-vieja / recifrado documentado como procedimiento operativo futuro; fuera de alcance automatizarlo).

**Alternativa considerada — helper de funciones (`encrypt(text)`/`decrypt(text)` llamadas a mano en el service):** descartada. Es más simple de leer pero **frágil**: cualquier nuevo camino de escritura que olvide llamar `encrypt()` filtra PII en claro a la DB. El `TypeDecorator` hace el cifrado una invariante del esquema, no una disciplina del programador. Coste: un poco más de "magia" SQLAlchemy, aceptable y bien acotado.

**Alternativa considerada — `pgcrypto` / cifrado en la base:** descartada — rompe portabilidad a SQLite (tests), acopla a una extensión de PostgreSQL y mueve la clave al servidor de base de datos. Fernet app-level es lo que el revisor aprobó (Decisión 4 del revisor).

### Decisión 5 — Estrategia de migración Alembic 002: columnas nullable + backfill + ajuste final

**Elegido:** una migración `002` (`down_revision="001"`) que:

1. **`add_column`** `descripcion_pseudonimizada` (`Text`, **nullable=True** temporalmente) y `descripcion_original` (`Text`, **nullable=True** temporalmente — almacena ciphertext base64).
2. **Backfill** de filas existentes: por cada incidente con `descripcion` poblada, calcular la pseudonimizada (regex) para `descripcion_pseudonimizada` y cifrar el original para `descripcion_original`. *(El backfill se hace en Python dentro de la migración, reutilizando `pseudonymize` y el cifrado Fernet; en la práctica las tablas estarán vacías en esta etapa de tesis, pero la migración es correcta para datos existentes.)*
3. **`alter_column`** ambas a **`nullable=False`** una vez backfilleadas.
4. **`drop_column`** `descripcion` (la columna vieja), ya migrada a las dos nuevas. El `downgrade()` revierte: recrea `descripcion`, copia desde `descripcion_pseudonimizada` (o descifra `descripcion_original` si se prefiere recuperar el crudo — se documenta que el downgrade prioriza recuperar el texto original descifrado para no perder datos), y elimina las dos columnas nuevas.

**Rationale:** el patrón "nullable → backfill → not null" es el estándar seguro para agregar columnas obligatorias sobre una tabla que podría tener filas, sin violar la restricción durante la transición. Drop de `descripcion` cierra la doble representación dejando un esquema limpio (no se arrastra una tercera copia).

**Consideración SQLite:** SQLite tiene soporte limitado de `ALTER COLUMN` / `DROP COLUMN`. Alembic lo maneja con **batch mode** (`op.batch_alter_table`). La migración usa batch mode para que `upgrade head` funcione tanto en PostgreSQL como en la suite SQLite. *(Decisión de implementación a fijar en apply: si el batch mode complica el backfill, alternativa documentada = mantener `descripcion` como alias de `descripcion_original` sin drop; se decide test-first.)*

**Trade-off:** correr `pseudonymize` + cifrado dentro de la migración acopla la migración al código de `app/utils/`. Es aceptable y común (las migraciones de datos importan helpers del app); se documenta la dependencia. Riesgo residual: si la clave Fernet no está presente al migrar, el backfill del cifrado falla con error claro → se documenta que `PSEUDONYMIZATION_ENCRYPTION_KEY` debe estar en el entorno antes de `alembic upgrade head`.

### Decisión 6 — Settings nuevos siguiendo el estilo existente

**Elegido:** agregar a `app/config/settings.py` (clase `Settings`, pydantic-settings):

```python
# ── Pseudonimización (Ley 25.326) ─────────────────────────────────────────
# Dominios corporativos internos cuyos hosts se enmascaran como [HOST].
# Ejemplo .env: PSEUDONYMIZATION_INTERNAL_DOMAINS=["empresa.local","corp.empresa.com"]
pseudonymization_internal_domains: list[str] = []
# Clave Fernet (base64 urlsafe de 32 bytes) para cifrar descripcion_original at-rest.
# Generar con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# OBLIGATORIA antes de arrancar la app o correr migraciones que toquen incidentes.
pseudonymization_encryption_key: str
```

**Rationale:** sigue el patrón existente (campos tipados, comentarios con ejemplo `.env`, listas como `cors_allow_origins: list[str]`). `pseudonymization_encryption_key` es **obligatoria** (sin default) como `gemini_api_key` y `database_url` — así pydantic-settings falla al arrancar si falta, en lugar de fallar al primer cifrado. `pseudonymization_internal_domains` tiene default `[]` (solo aplica el fallback heurístico si no se configuran dominios).

**Documentación de la clave:** dado que no existe `.env.example`, el apply **crea** `Gestion_Incidentes/.env.example` documentando `DATABASE_URL`, `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `PSEUDONYMIZATION_INTERNAL_DOMAINS` (y referenciando los ya existentes) — o, si se prefiere no introducir un archivo nuevo, se documenta exclusivamente en `docs/pseudonymization.md`. Se decide en apply (preferencia: `.env.example` para ergonomía de despliegue).

### Decisión 7 — Patrón de hosts internos: dominios por settings + heurísticas de fallback

**Elegido:** el patrón de host combina dos fuentes:
1. **Dominios corporativos parametrizados** (`pseudonymization_internal_domains`): cualquier token que termine en uno de esos sufijos (p. ej. `*.empresa.local`, `*.corp.empresa.com`) se enmascara como `[HOST]`. Construido dinámicamente desde settings.
2. **Heurísticas genéricas de fallback** (siempre activas): `srv-*`, `pc-*`, sufijo `*.local`, y `localhost`.

`pseudonymize(text, internal_domains)` recibe la lista de dominios como **argumento** (no la lee de settings dentro de la función) para mantenerse **pura** y testeable; el service la inyecta desde `get_settings()`.

**Rationale:** parametrizar por settings cubre el dominio real de la organización sin recompilar; el fallback heurístico garantiza cobertura aunque no se configuren dominios. Pasar los dominios como argumento preserva la pureza de la función (sin I/O ni dependencia de settings → trivialmente testeable con dominios arbitrarios).

### Decisión 8 — Orden de aplicación libre de colisiones: email → teléfono → host → persona

**Elegido:** patrones secuenciales en orden fijo. Los estructurados (email, teléfono, host) — alta especificidad — primero; el heurístico de nombres (propenso a falsos positivos) último, sobre texto donde emails/hosts ya son etiquetas `[MAYÚSCULAS]`.

**Rationale:** evita colisiones. `juan.perez@empresa.com` colapsa a `[EMAIL]` **antes** de que el patrón de nombres capture `juan.perez`. Las etiquetas insertadas tienen forma `[MAYÚSCULAS]` y el patrón de nombres las excluye, de modo que ninguna etiqueta se re-procesa. Secuencia de `re.sub` independientes (no un mega-regex) por KISS y testabilidad: un test unitario por categoría. `re.subn` provee el **conteo por categoría** que alimenta el log DEBUG de cobertura, sin exponer el texto.

### Decisión 9 — Nombres propios en español: heurística acotada con lista de exclusión

**Elegido:** regex heurístico para secuencias de palabras capitalizadas (nombre+apellido en español, con tildes y `ñ`), con **lista de exclusión** mínima para términos del dominio que empiezan con mayúscula pero NO son personas: las tres categorías canónicas `Sistemas`, `Operaciones`, `Soporte Técnico`, y arranques de oración frecuentes. Detalle del patrón y la lista se fijan en apply, test-first.

**Rationale:** es lo que la tesis (§11.3) describe y acepta. Se prioriza minimizar **falsos negativos sobre PII real** (no dejar pasar nombres) aceptando **falsos positivos** (enmascarar de más alguna palabra capitalizada), porque el costo de filtrar de más es bajo para clasificar (Gemini sigue clasificando bien con `[PERSONA]`), mientras que dejar pasar un nombre es fuga de PII.

**Trade-off documentado en `docs/pseudonymization.md`:** el regex no captura todos los nombres (apellidos atípicos, minúsculas) ni evita todo falso positivo (topónimos, productos capitalizados). Límite conocido y aceptado.

### Decisión 10 — Logging: auditoría de cobertura en DEBUG, sin PII; sin fuga en INFO

**Elegido:**
- `pseudonymize` devuelve un `PseudonymizationResult` con `texto: str` y `conteos: dict[str,int]` (reemplazos por categoría). El módulo **no emite logs** (sigue siendo función pura).
- El **service** emite un log **nivel DEBUG** (`pseudonimizacion_cobertura`) con los conteos por categoría (p. ej. `{"email": 1, "telefono": 0, "host": 2, "persona": 1}`) — **nunca** el texto original ni el pseudonimizado completo.
- Ningún log **INFO** contiene la `descripcion_original` ni la empareja con su versión pseudonimizada. Los logs INFO existentes (`incidente_created`, `incidente_classified`, `gemini_classified`) **no** incluyen texto de descripción.

**Rationale:** cumple el requisito de no-fuga (§11.4) y aporta la **auditoría de cobertura** que pidió el revisor (Decisión 3 del revisor) sin reintroducir PII. Mantener el pseudonymizer libre de logging lo conserva puro y testeable.

## Risks / Trade-offs

- **[Reidentificación residual]** El regex reduce pero no elimina el riesgo cuando el texto conserva contexto organizacional (§11.5). → La doble representación lo mitiga estructuralmente: lo que sale a Gemini es la pseudonimizada; el original cifrado nunca cruza la frontera. Mejoras futuras (anonimización diferencial / k-anonimato) quedan como línea futura. Documentar en `docs/pseudonymization.md`.
- **[Clave Fernet faltante]** Si `PSEUDONYMIZATION_ENCRYPTION_KEY` no está en el entorno, la app no arranca (campo obligatorio) y la migración 002 falla al backfillear. → Mitigación: campo obligatorio en settings (falla temprana y clara), documentar generación y requisito en `.env.example` / `docs/pseudonymization.md`.
- **[Pérdida/rotación de clave]** Perder la clave hace ilegible `descripcion_original` (ciphertext irreversible). → Riesgo aceptado y documentado: el dato operativo (pseudonimizada) sigue intacto; la original es solo para auditoría/ARCO. Rotación documentada como procedimiento operativo manual (descifrar-con-vieja / recifrar-con-nueva) — automatizarla es Non-Goal.
- **[Migración sobre SQLite con batch mode]** `DROP COLUMN`/`ALTER COLUMN` en SQLite requieren `op.batch_alter_table`. → Mitigación: la migración usa batch mode; si el backfill+batch se complica, alternativa documentada (no dropear `descripcion`). Se cubre corriendo `alembic upgrade head` en la suite SQLite.
- **[Falsos negativos de nombres]** Un nombre no capturado viajaría a Gemini en la pseudonimizada. → Priorizar recall (heurística amplia), tests con variantes; residual aceptado como límite.
- **[Falsos positivos]** Palabras capitalizadas no-PII enmascaradas como `[PERSONA]` podrían degradar levemente la clasificación. → Lista de exclusión para categorías del dominio; impacto bajo (Gemini infiere de contexto). Cubierto por escenario de spec.
- **[Acoplamiento migración ↔ app/utils]** La migración 002 importa `pseudonymize` y el cifrado. → Aceptado (patrón común de migración de datos); documentado.
- **[Contrato implícito del clasificador]** `GeminiClassifier`/`HybridClassifier` confían en recibir texto ya pseudonimizado (sin defensa). → Mitigación: contrato documentado + test de integración a nivel service que prueba que Gemini recibe la pseudonimizada y nunca el original.

## Migration Plan

Despliegue con migración de esquema (a diferencia del diseño previo, que no tenía migración):

1. Agregar `cryptography` a `requirements.txt`; instalar.
2. Generar la clave Fernet y colocar `PSEUDONYMIZATION_ENCRYPTION_KEY` (y opcionalmente `PSEUDONYMIZATION_INTERNAL_DOMAINS`) en el entorno / `.env`.
3. Agregar `app/utils/pseudonymizer.py`, `app/utils/encryption.py`, settings nuevos, ajustar modelo/schemas/service.
4. Ejecutar `alembic upgrade head` → aplica `002` (agrega columnas, backfillea, dropea `descripcion`).
5. Rollback: `alembic downgrade 001` revierte a la columna `descripcion` (recuperando el texto original descifrado); el código se revierte por commit. Mientras la columna `descripcion` no exista, el código viejo no debe correr (coordinar despliegue).

## Open Questions

> Las Open Questions del diseño previo sobre conservar el original y parametrizar hosts **quedaron resueltas** por las decisiones del revisor (doble representación + cifrado; dominios por settings). Residuales para el OK final:

1. **`.env.example` vs solo `docs/`** — ¿se introduce `Gestion_Incidentes/.env.example` (no existe hoy) o se documenta la clave solo en `docs/pseudonymization.md`? Preferencia del diseño: `.env.example` por ergonomía. (Decisión menor, MEDIA.)
2. **Estrategia exacta de migración en SQLite** — confirmar que el batch mode con backfill es viable; si no, adoptar la alternativa de no dropear `descripcion`. Se valida test-first en apply.
3. **Downgrade de 002** — ¿el `descripcion` recuperado en el downgrade debe ser el **original descifrado** (postura del diseño, no perder datos) o la pseudonimizada? Confirmar con el revisor (impacta qué dato sobrevive a un rollback).
