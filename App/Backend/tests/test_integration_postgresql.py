"""
Integration tests using real PostgreSQL (C-19).

These tests validate PostgreSQL-specific behaviors that SQLite cannot:
foreign key constraints, cascade deletes, Numeric precision, TIMESTAMPTZ,
composite indices, and UNIQUE constraints.

All tests require a running PostgreSQL instance. If unavailable, they
are skipped automatically via the pg_engine fixture.

Test organization follows the C-19 proposal and delta spec:
  1. Connection and schema validation
  2. Foreign key integrity
  3. Cascade and SET NULL behavior
  4. Type constraints and catalog uniqueness
  5. Indices and schema coexistence
  6. API operations via PostgreSQL
"""

from datetime import datetime, timezone

import pytest

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.catalog import CanalOrigen, Estado, Sector
from app.models.clasificacion_log import ClasificacionLog
from app.models.incidente import Incidente, PrioridadEnum

pytestmark = pytest.mark.integration


# ─────────────────────────────────────────────────────────────────────────────
# 1. Connection and Schema Validation
# ─────────────────────────────────────────────────────────────────────────────

async def test_pg_connection_works(pg_engine):
    """PostgreSQL engine connects and executes queries."""
    async with pg_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


async def test_pg_tables_exist(pg_engine):
    """All expected tables exist in the PostgreSQL public schema."""
    async with pg_engine.connect() as conn:
        tables_result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        table_names = {row[0] for row in tables_result}

    expected = {"incidente", "clasificacion_log", "sector",
                 "estado", "canal_origen", "users"}
    missing = expected - table_names
    assert not missing, f"Missing tables: {missing}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Foreign Key Integrity
# ─────────────────────────────────────────────────────────────────────────────

async def test_create_incidente_valid_fks(pg_session, seed_pg_catalogs):
    """An incidente with valid FKs is persisted correctly."""
    catalogs = seed_pg_catalogs

    incidente = Incidente(
        descripcion_original="Test original",
        descripcion_pseudonimizada="Test pseudonimizado",
        prioridad=PrioridadEnum.media,
        estado_id=catalogs["estado_nuevo"].id,
        sector_id=catalogs["sector_sistemas"].id,
        canal_origen_id=catalogs["canal_correo"].id,
    )
    pg_session.add(incidente)
    await pg_session.flush()

    assert incidente.id is not None
    assert incidente.estado_id == catalogs["estado_nuevo"].id
    assert incidente.sector_id == catalogs["sector_sistemas"].id


async def test_create_incidente_invalid_fk(pg_session, seed_pg_catalogs):
    """Inserting an incidente with invalid sector_id raises IntegrityError."""
    catalogs = seed_pg_catalogs
    nonexistent_sector_id = 99999

    incidente = Incidente(
        descripcion_original="Test FK violation",
        descripcion_pseudonimizada="Test FK violation",
        prioridad=PrioridadEnum.media,
        estado_id=catalogs["estado_nuevo"].id,
        sector_id=nonexistent_sector_id,  # Does not exist in sector table
    )
    pg_session.add(incidente)

    with pytest.raises(IntegrityError):
        await pg_session.flush()


async def test_clasificacion_log_valid_fks(pg_session, seed_pg_catalogs):
    """ClasificacionLog with valid FKs to incidente and sector is persisted."""
    catalogs = seed_pg_catalogs

    # Create an incidente first
    incidente = Incidente(
        descripcion_original="Original for log",
        descripcion_pseudonimizada="Pseudonymized for log",
        prioridad=PrioridadEnum.media,
        estado_id=catalogs["estado_nuevo"].id,
        sector_id=catalogs["sector_sistemas"].id,
    )
    pg_session.add(incidente)
    await pg_session.flush()

    # Create a classification log linked to the incidente
    log = ClasificacionLog(
        incidente_id=incidente.id,
        sector_id_predicho=catalogs["sector_sistemas"].id,
        confianza=0.9500,
        etapa="deterministic",
        requiere_revision_humana=False,
        respuesta_raw="Matched by keyword rule",
    )
    pg_session.add(log)
    await pg_session.flush()

    assert log.id is not None
    assert log.incidente_id == incidente.id


async def test_clasificacion_log_invalid_incidente_fk(pg_session, seed_pg_catalogs):
    """ClasificacionLog with nonexistent incidente_id raises IntegrityError."""
    catalogs = seed_pg_catalogs

    log = ClasificacionLog(
        incidente_id=99999,  # Nonexistent incidente
        sector_id_predicho=catalogs["sector_sistemas"].id,
        confianza=0.8000,
        etapa="gemini",
        requiere_revision_humana=False,
    )
    pg_session.add(log)

    with pytest.raises(IntegrityError):
        await pg_session.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 3. Cascade and SET NULL Behavior
# ─────────────────────────────────────────────────────────────────────────────

async def test_cascade_delete_incidente_removes_logs(pg_engine, pg_session, seed_pg_catalogs):
    """Deleting an incidente cascades to delete its ClasificacionLog rows."""
    catalogs = seed_pg_catalogs

    # Create incidente + log
    incidente = Incidente(
        descripcion_original="Cascade test",
        descripcion_pseudonimizada="Cascade test",
        prioridad=PrioridadEnum.media,
        estado_id=catalogs["estado_nuevo"].id,
        sector_id=catalogs["sector_sistemas"].id,
    )
    pg_session.add(incidente)
    await pg_session.flush()

    log = ClasificacionLog(
        incidente_id=incidente.id,
        sector_id_predicho=catalogs["sector_sistemas"].id,
        confianza=0.9000,
        etapa="deterministic",
        requiere_revision_humana=False,
    )
    pg_session.add(log)
    await pg_session.flush()
    log_id = log.id

    # Delete the incidente — should cascade to log
    await pg_session.delete(incidente)
    await pg_session.flush()

    # Verify log is gone
    result = await pg_session.get(ClasificacionLog, log_id)
    assert result is None, "ClasificacionLog should be cascade-deleted"


async def test_set_null_on_sector_delete(pg_engine, pg_session, seed_pg_catalogs):
    """Deleting a sector sets incidente.sector_id to NULL (ON DELETE SET NULL)."""
    catalogs = seed_pg_catalogs

    # Create a temporary sector to delete
    temp_sector = Sector(
        nombre="Temp Sector for SET NULL test",
        descripcion="Will be deleted",
    )
    pg_session.add(temp_sector)
    await pg_session.flush()

    # Create incidente referencing the temp sector
    incidente = Incidente(
        descripcion_original="SET NULL test",
        descripcion_pseudonimizada="SET NULL test",
        prioridad=PrioridadEnum.media,
        estado_id=catalogs["estado_nuevo"].id,
        sector_id=temp_sector.id,
    )
    pg_session.add(incidente)
    await pg_session.flush()
    incidente_id = incidente.id

    # Delete the sector
    await pg_session.delete(temp_sector)
    await pg_session.flush()

    # Refresh incidente from DB — sector_id should now be NULL
    await pg_session.refresh(incidente)
    assert incidente.sector_id is None, (
        "sector_id should be NULL after sector deletion (ON DELETE SET NULL)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Type Constraints and Catalog Uniqueness
# ─────────────────────────────────────────────────────────────────────────────

async def test_unique_constraint_sector_nombre(pg_session, seed_pg_catalogs):
    """Inserting a Sector with duplicate nombre raises IntegrityError."""
    # Attempt to insert "Sistemas" which already exists from seed_pg_catalogs
    duplicate = Sector(nombre="Sistemas", descripcion="Duplicate attempt")
    pg_session.add(duplicate)

    with pytest.raises(IntegrityError):
        await pg_session.flush()


async def test_unique_constraint_estado_nombre(pg_session, seed_pg_catalogs):
    """Inserting an Estado with duplicate nombre raises IntegrityError."""
    duplicate = Estado(
        nombre="nuevo", descripcion="Duplicate", es_terminal=False
    )
    pg_session.add(duplicate)

    with pytest.raises(IntegrityError):
        await pg_session.flush()


async def test_unique_constraint_canal_nombre(pg_session, seed_pg_catalogs):
    """Inserting a CanalOrigen with duplicate nombre raises IntegrityError."""
    duplicate = CanalOrigen(nombre="correo electrónico", descripcion="Duplicate")
    pg_session.add(duplicate)

    with pytest.raises(IntegrityError):
        await pg_session.flush()


async def test_numeric_precision_confianza(pg_session, seed_pg_catalogs):
    """Numeric(5,4) on confianza enforces precision constraints."""
    catalogs = seed_pg_catalogs

    incidente = Incidente(
        descripcion_original="Numeric test",
        descripcion_pseudonimizada="Numeric test",
        prioridad=PrioridadEnum.media,
        estado_id=catalogs["estado_nuevo"].id,
        sector_id=catalogs["sector_sistemas"].id,
    )
    pg_session.add(incidente)
    await pg_session.flush()

    # Value 0.12345 has 5 decimal digits — Numeric(5,4) should truncate
    # or round it. PostgreSQL rounds to 0.1235 (4 decimal places).
    log = ClasificacionLog(
        incidente_id=incidente.id,
        sector_id_predicho=catalogs["sector_sistemas"].id,
        confianza=0.12345,  # 5 decimal digits → should be rounded to 0.1235
        etapa="gemini",
        requiere_revision_humana=False,
    )
    pg_session.add(log)
    await pg_session.flush()

    # Refresh to get the stored value
    await pg_session.refresh(log)

    # PostgreSQL rounds to 4 decimal places: 0.12345 → 0.1235
    assert log.confianza == pytest.approx(0.1235, abs=0.0001), (
        f"Numeric(5,4) should round to 4 decimals, got {log.confianza}"
    )


async def test_created_at_is_timezone_aware(pg_session, seed_pg_catalogs):
    """created_at stores timestamps with UTC timezone (TIMESTAMPTZ)."""
    catalogs = seed_pg_catalogs

    before = datetime.now(timezone.utc)

    incidente = Incidente(
        descripcion_original="Timezone test",
        descripcion_pseudonimizada="Timezone test",
        prioridad=PrioridadEnum.media,
        estado_id=catalogs["estado_nuevo"].id,
        sector_id=catalogs["sector_sistemas"].id,
    )
    pg_session.add(incidente)
    await pg_session.flush()

    after = datetime.now(timezone.utc)

    # Verify the timestamp has timezone info
    assert incidente.created_at is not None
    assert incidente.created_at.tzinfo is not None, (
        "created_at must have timezone info (TIMESTAMPTZ)"
    )
    assert incidente.created_at.tzinfo == timezone.utc, (
        f"created_at must be UTC, got {incidente.created_at.tzinfo}"
    )

    # Verify it falls within the expected time window
    assert before <= incidente.created_at <= after, (
        f"created_at {incidente.created_at.isoformat()} "
        f"not in [{before.isoformat()}, {after.isoformat()}]"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Indices and Schema Coexistence
# ─────────────────────────────────────────────────────────────────────────────

async def test_composite_indices_exist(pg_engine):
    """The composite indices defined in Incidente exist in PostgreSQL."""
    expected_indices = {
        "ix_incidente_created_sector": {"created_at", "sector_id"},
        "ix_incidente_estado_created": {"estado_id", "created_at"},
    }

    async with pg_engine.connect() as conn:
        for index_name, expected_columns in expected_indices.items():
            result = await conn.execute(
                text(
                    "SELECT a.attname "
                    "FROM pg_index i "
                    "JOIN pg_attribute a ON a.attrelid = i.indrelid "
                    "AND a.attnum = ANY(i.indkey) "
                    "JOIN pg_class c ON c.oid = i.indexrelid "
                    "WHERE c.relname = :index_name "
                    "ORDER BY a.attnum"
                ),
                {"index_name": index_name},
            )
            columns = {row[0] for row in result}
            assert columns == expected_columns, (
                f"Index {index_name}: expected columns {expected_columns}, "
                f"got {columns}"
            )


async def test_users_and_incidentes_same_schema(pg_engine):
    """Users and incidentes tables coexist in the public schema."""
    async with pg_engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' "
                "AND table_name IN ('users', 'incidente')"
            )
        )
        table_names = {row[0] for row in result}
        assert table_names == {"users", "incidente"}, (
            f"Expected both tables, got {table_names}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. API Operations via PostgreSQL
# ─────────────────────────────────────────────────────────────────────────────

async def test_patch_updates_estado(pg_engine, pg_client, seed_pg_catalogs):
    """PATCH updates incidente estado in PostgreSQL (full cycle)."""
    catalogs = seed_pg_catalogs

    # Add "en proceso" estado for the PATCH target
    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    async with factory() as session:
        en_proceso = Estado(
            nombre="en proceso",
            descripcion="Asignado y en atencion",
            es_terminal=False,
        )
        session.add(en_proceso)
        await session.commit()
        await session.refresh(en_proceso)
        en_proceso_id = en_proceso.id

    # Create incidente via API
    create_payload = {
        "descripcion": "Estado update test",
        "prioridad": "media",
        "sector_id": catalogs["sector_sistemas"].id,
        "canal_origen_id": catalogs["canal_correo"].id,
    }
    response = await pg_client.post("/api/v1/incidentes", json=create_payload)
    assert response.status_code == 201, f"Create failed: {response.text}"
    incidente_data = response.json()
    incidente_id = incidente_data["id"]

    # Verify initial estado
    assert incidente_data["estado"]["nombre"] == "nuevo"

    # Patch to "en proceso"
    patch_payload = {"estado_id": en_proceso_id}
    response = await pg_client.patch(
        f"/api/v1/incidentes/{incidente_id}", json=patch_payload
    )
    assert response.status_code == 200, f"Patch failed: {response.text}"
    updated = response.json()
    assert updated["estado"]["nombre"] == "en proceso"

    # Verify with GET
    response = await pg_client.get(f"/api/v1/incidentes/{incidente_id}")
    assert response.status_code == 200
    retrieved = response.json()
    assert retrieved["estado"]["nombre"] == "en proceso"
