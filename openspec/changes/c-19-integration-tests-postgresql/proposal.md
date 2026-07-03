# C-19: Tests de Integracion con PostgreSQL Real

## Por que

La tesis (Cap 6, §6.7) afirma que las pruebas de integracion usan PostgreSQL real. Actualmente todo el test suite usa SQLite en memoria via `aiosqlite`. SQLite no valida:
- Tipos PostgreSQL (Numeric(5,4), JSONB, arrays)
- Secuencias e identidades de PostgreSQL
- Constraints a nivel de schema
- Comportamiento de FK con SET NULL / CASCADE especificos de PG
- Sintaxis SQL propia de PostgreSQL

Tener tests contra PostgreSQL real es valido en si mismo, independientemente de lo que diga la tesis.

## Que cambia

### Backend: tests de integracion con PostgreSQL

Agregar un marcador `pytest.mark.integration` para tests que requieren PostgreSQL real. Estos tests:

1. Usan un contenedor PostgreSQL desechable (via `testing.postgresql` o `testcontainers-python`) O usan la instancia local de PostgreSQL si esta disponible
2. Se ejecutan con una database limpia por sesion de test
3. Validan: creacion de incidentes con todas las FKs, clasificacion completa, constraints de integridad, tipos PG
4. Se ejecutan OPCIONALMENTE en CI (requieren PostgreSQL disponible) y OBLIGATORIAMENTE en local cuando PG esta corriendo
5. Los tests unitarios rapidos (SQLite) se mantienen como estan

### Estrategia de implementacion

Usar `pytest-postgresql` o `testcontainers-python[postgres]`:
- Si PostgreSQL local esta disponible → usar esa instancia con una DB temporal
- Si no → skipear los tests de integracion (marcador `skipif`)
- En CI → agregar un servicio PostgreSQL al workflow

### Archivos a crear/modificar

- `Gestion_Incidentes/tests/conftest.py`: agregar fixtures `pg_engine`, `pg_session` para PostgreSQL
- `Gestion_Incidentes/tests/test_integration_postgresql.py`: 10-15 tests de integracion
- `Gestion_Incidentes/pytest.ini`: agregar marcador `integration`
- `.github/workflows/ci.yml`: agregar servicio PostgreSQL (o job separado)

### Tests minimos (10-15)

1. Crear incidente con todas las FKs y verificar integridad
2. Crear incidente con sector_id invalido → error de FK
3. Clasificar incidente → verificar clasificacion_log con FK a sector
4. Validar cascade delete: borrar incidente → borra clasificacion_log
5. Verificar constraints UNIQUE en catalogos
6. Verificar tipo Numeric(5,4) en confianza
7. Verificar created_at con timezone
8. Actualizar estado de incidente via PATCH
9. Verificar indices (created_at + sector_id)
10. Verificar que usuarios e incidentes coexisten en mismo schema

## Gobernanza

MEDIUM — cambios en tests, sin impacto en codigo de produccion.

## Dependencias

C-15 (JWT Auth) — los tests de integracion deben probar tambien rutas protegidas.

**NOTA C-24**: Los paths en este archivo referencian `Gestion_Incidentes/` (directorio antiguo). Antes de aplicar C-19, actualizar todas las referencias a `App/Backend/` (ver C-24-restructure-app-directory).
