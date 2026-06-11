## Why

El clasificador semántico transmite la descripción del incidente al modelo Gemini 2.5 Flash, alojado en infraestructura del proveedor en Estados Unidos (transferencia internacional de datos). Hoy esa descripción se envía **en crudo**: nombres propios, emails, teléfonos y hosts internos viajan sin tratamiento, y además se **persisten en crudo** en la única columna `incidente.descripcion`. La tesis (§11.3) exige un procedimiento de **pseudonimización** ejecutado dentro del módulo Python local, validado por expresiones regulares con pruebas unitarias dedicadas, para legitimar la transferencia bajo el marco de la Ley 25.326. Las firmas de `GeminiClassifier.classify()` y `HybridClassifier.classify()` ya documentan su argumento como "texto pseudonimizado", pero **ningún código lo pseudonimiza** — es el segundo gap funcional del backend (roadmap FASE 2, C-03).

Tras la revisión de gobernanza, el alcance se amplía de "pseudonimizar solo en el egreso a Gemini" a una **arquitectura de doble representación con cifrado at-rest**: el incidente conserva el texto original **cifrado** (solo para auditoría / derechos ARCO) y una versión **pseudonimizada en claro** que es la única que usan la IA, los dashboards, los reportes y las búsquedas.

> **Gobernanza ALTO (datos personales — Ley 25.326).** Esta propuesta crea únicamente artefactos de planificación (proposal, design, specs, tasks). Las decisiones de arquitectura de privacidad fueron **aprobadas por el revisor humano** (ver "Decisiones de gobernanza aprobadas"); la **implementación** queda pendiente del **OK final** tras esta revisión. Ver "Aprobación pendiente" al final.

## Decisiones de gobernanza aprobadas (revisor humano)

Las siguientes cuatro decisiones fueron tomadas por el revisor humano y son **vinculantes** para esta propuesta; reemplazan el alcance inicial (que persistía solo el original y pseudonimizaba únicamente en el egreso). Su elaboración técnica está en `design.md`.

1. **Arquitectura de doble representación.** El modelo `Incidente` pasa a tener DOS representaciones de la descripción: `descripcion_original` (protegida, **CIFRADA at-rest**) y `descripcion_pseudonimizada` (uso operativo, en claro). La IA (pipeline de clasificación / Gemini) procesa **únicamente** `descripcion_pseudonimizada`. Dashboards, reportes y búsquedas (API hacia el frontend) usan la versión pseudonimizada. La original queda cifrada con acceso restringido solo para auditoría (**NO** expuesta en los endpoints normales de la API).
2. **Hosts internos parametrizados.** Los dominios corporativos se parametrizan por settings (lista `pseudonymization_internal_domains`, ej. `empresa.local`, `corp.empresa.com`) + heurísticas genéricas como fallback (`srv-*`, `pc-*`, `*.local`, `localhost`).
3. **Auditoría de cobertura.** Log nivel **DEBUG** con conteo de reemplazos por categoría, sin exponer PII.
4. **Cifrado.** **Fernet app-level** (librería `cryptography`), clave simétrica en la env var `PSEUDONYMIZATION_ENCRYPTION_KEY` vía pydantic-settings. Portable entre PostgreSQL (producción) y SQLite (tests); clave rotable.

## What Changes

- Crear `Gestion_Incidentes/app/utils/pseudonymizer.py`: función pura `pseudonymize(text: str, internal_domains: list[str]) -> PseudonymizationResult` (sin estado, sin I/O) que reemplaza datos personales por etiquetas genéricas mediante regex compiladas a nivel de módulo, y devuelve además el **conteo de reemplazos por categoría** (para la auditoría DEBUG, sin PII).
- Reemplazos soportados, en orden de aplicación fijo para evitar colisiones: emails → `[EMAIL]`, teléfonos → `[TELEFONO]`, hosts internos → `[HOST]`, nombres propios → `[PERSONA]`. Hosts internos = dominios de `internal_domains` (settings) + fallback heurístico (`srv-*`, `pc-*`, `*.local`, `localhost`).
- Crear `Gestion_Incidentes/app/utils/encryption.py`: un `TypeDecorator` de SQLAlchemy (`EncryptedText`) que cifra/descifra de forma transparente con Fernet, usando la clave de settings. Cifra `descripcion_original` at-rest, portable PostgreSQL/SQLite.
- **Doble representación** en el modelo `Incidente`: agregar `descripcion_pseudonimizada` (Text, claro) y `descripcion_original` (cifrada con `EncryptedText`); migrar la actual `descripcion` a ambas.
- **Pseudonimizar en la creación del incidente** (capa service, `IncidenteService.create_and_classify`), como **único punto canónico**: se puebla `descripcion_pseudonimizada` antes de persistir y es la que consume el pipeline de clasificación. `GeminiClassifier` confía en recibir texto ya pseudonimizado (sin llamada defensiva — ver Decisión 2 de `design.md`).
- **API expone solo la pseudonimizada**: `IncidenteRead` pasa a exponer `descripcion_pseudonimizada` en lugar de la columna cruda; la `descripcion_original` cifrada NO se expone en endpoints (acceso de auditoría fuera de alcance de este change).
- **Settings nuevos**: `pseudonymization_internal_domains` (lista) y `pseudonymization_encryption_key` (clave Fernet obligatoria), siguiendo el estilo de `app/config/settings.py`.
- **Migración Alembic `002`**: agrega ambas columnas, backfillea las filas existentes (pseudonimizar + cifrar), las vuelve `NOT NULL` y dropea la columna `descripcion` vieja (con batch mode para SQLite).
- **Auditoría de cobertura**: log DEBUG en el service con los conteos por categoría; nunca el texto crudo ni emparejado con su versión pseudonimizada en INFO.
- **Dependencia nueva**: agregar `cryptography` a `requirements.txt`.
- Tests unitarios por patrón regex + casos borde, round-trip del cifrado, integración (Gemini recibe pseudonimizada / API expone pseudonimizada / original persistida cifrada) y migración. Documentar procedimiento, alcance, límites y riesgo residual en `docs/pseudonymization.md`.

## Capabilities

### New Capabilities
- `data-pseudonymization`: Pseudonimización y protección de datos personales conforme a la Ley 25.326. Define la arquitectura de **doble representación** (original cifrada at-rest + pseudonimizada operativa), qué categorías de PII se reemplazan y por qué etiquetas, el orden de aplicación, el cifrado Fernet de la representación original, la garantía de que la IA y la API operan **solo** sobre la pseudonimizada, los hosts internos parametrizados por settings con fallback heurístico, y la auditoría de cobertura en DEBUG sin PII.

### Modified Capabilities
<!-- Ninguna capability previa cambia sus requisitos. `foundation-environment` y `n8n-notification` permanecen intactas: el cambio es aditivo sobre el modelo de incidente y la ruta de creación/clasificación. -->

## Impact

- **Código nuevo**: `app/utils/pseudonymizer.py` (función pura + regex + conteos) y `app/utils/encryption.py` (`EncryptedText` TypeDecorator Fernet).
- **Código modificado**:
  - `app/models/incidente.py`: doble representación (`descripcion_pseudonimizada`, `descripcion_original` cifrada); corregir el docstring obsoleto ("pseudonimizada por N8N").
  - `app/services/incidente_service.py` (`create_and_classify`): pseudonimizar antes de persistir, poblar ambas columnas, log DEBUG de cobertura, pasar la pseudonimizada al clasificador.
  - `app/schemas/incidente.py`: `IncidenteRead` expone `descripcion_pseudonimizada`; la original cifrada no se expone.
  - `app/config/settings.py`: `pseudonymization_internal_domains`, `pseudonymization_encryption_key`.
  - `GeminiClassifier`/`HybridClassifier`: sin cambio funcional; se actualizan docstrings para reflejar que el argumento es texto ya pseudonimizado (contrato garantizado por el service). `app/utils/` NO importa de `classifiers/` ni `services/` (dirección de dependencias preservada).
- **Migración**: nueva `alembic/versions/002_*.py` (doble representación + backfill + drop de `descripcion`).
- **Tests nuevos**: `tests/test_pseudonymizer.py`, `tests/test_encryption.py`, integración del egreso/persistencia (`tests/test_pseudonymization_integration.py` o ampliación), y verificación de la migración.
- **Documentación nueva**: `docs/pseudonymization.md`; opcionalmente `Gestion_Incidentes/.env.example` (no existe hoy) para documentar la clave Fernet y los dominios.
- **Dependencias**: **nueva** — `cryptography` (Fernet). Explícitamente **fuera de alcance**: NER / ML para nombres, KMS / envelope encryption, endpoint de auditoría a la original cifrada.
- **Riesgo / Gobernanza**: **ALTO** — el módulo procesa datos personales sujetos a la Ley 25.326. La doble representación + cifrado at-rest mitiga estructuralmente el riesgo de reidentificación y fuga (§11.4/§11.5). Pérdida de clave Fernet, falsos positivos/negativos del regex y migración sobre SQLite son riesgos gestionados en `design.md`.

## Aprobación pendiente (Gobernanza ALTO)

Las cuatro decisiones de arquitectura de privacidad ya fueron **aprobadas por el revisor** (sección "Decisiones de gobernanza aprobadas"). Esta revisión de los artefactos las incorpora; la **implementación sigue bloqueada hasta el OK final** del revisor sobre los artefactos revisados (proposal + design). El revisor debe validar, como mínimo:

1. La arquitectura de doble representación y que **solo** la pseudonimizada cruce la frontera y se exponga en la API.
2. El cifrado Fernet at-rest de la original vía `EncryptedText` (TypeDecorator) y el manejo de la clave en settings/`.env`.
3. La estrategia de migración `002` (nullable → backfill → NOT NULL → drop `descripcion`) y el comportamiento del downgrade.
4. El conjunto de patrones regex, su orden, los dominios parametrizados + fallback, y el tradeoff aceptado para nombres propios.
5. La política de logging: auditoría de cobertura en DEBUG sin PII; sin fuga del original en INFO.

Hasta ese OK final, `/opsx:apply` no debe ejecutarse para este cambio. Las Open Questions residuales están al final de `design.md`.
