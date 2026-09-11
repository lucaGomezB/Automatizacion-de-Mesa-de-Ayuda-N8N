"""Migracion: sectores multietiqueta (C-27).

Responsabilidad:
    Aditiva respecto de 001/002/003. NO muta `001_seed_catalogs.py`.

    1. Crea las tablas de union normalizadas para sectores adicionales:
           incidente_sector_adicional
           clasificacion_sector_predicho
           clasificacion_sector_validado
    2. Pone en NULL toda referencia a `Operaciones` y al viejo `Soporte Técnico`
       en `incidente` y `clasificacion_log`.
    3. Elimina las filas `Operaciones` y `Soporte Técnico` del catalogo.
    4. Hace upsert de los cinco sectores canonicos (sin tildes).

    El `downgrade` elimina las tablas de union, retira los cuatro sectores
    nuevos y reinserta `Operaciones` y `Soporte Técnico`.

Aprobacion humana explicita (gobernanza ALTA/CRITICA):
    La migracion es destructiva de datos por diseno; el usuario aprobo que no
    se requiere backup (datos simulados/incorrectos).

Revision ID: 004
Revises: 003
Create Date: 2026-09-11
"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None

# Vocabulario canonico (exacto, case-sensitive, sin tildes).
SECTORES_CANONICOS = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)

DESCRIPCIONES = {
    "Seguridad Informatica": "Ciberseguridad, accesos, identidad y proteccion de la informacion",
    "Soporte Tecnico Hardware": "Equipamiento de usuarios, perifericos y fallas fisicas",
    "Soporte Tecnico Software": "Software cliente, aplicaciones, instalaciones y asistencia remota",
    "Bases de Datos": "Motores de datos, consultas, replicacion, backup y recuperacion",
    "Sistemas": "Infraestructura, redes, servidores y servicios de plataforma",
}

# Sectores legacy que se retiran.
SECTORES_LEGACY = ("Operaciones", "Soporte Técnico")

# Sectores que introduce esta migracion (para el downgrade).
SECTORES_NUEVOS = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _create_association_tables() -> None:
    op.create_table(
        "incidente_sector_adicional",
        sa.Column("incidente_id", sa.Integer(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("incidente_id", "sector_id"),
        sa.ForeignKeyConstraint(
            ["incidente_id"], ["incidente.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"], ondelete="RESTRICT"),
    )
    op.create_table(
        "clasificacion_sector_predicho",
        sa.Column("clasificacion_log_id", sa.Integer(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("clasificacion_log_id", "sector_id"),
        sa.ForeignKeyConstraint(
            ["clasificacion_log_id"], ["clasificacion_log.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"], ondelete="RESTRICT"),
    )
    op.create_table(
        "clasificacion_sector_validado",
        sa.Column("clasificacion_log_id", sa.Integer(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("clasificacion_log_id", "sector_id"),
        sa.ForeignKeyConstraint(
            ["clasificacion_log_id"], ["clasificacion_log.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"], ondelete="RESTRICT"),
    )


def _drop_association_tables() -> None:
    op.drop_table("clasificacion_sector_validado")
    op.drop_table("clasificacion_sector_predicho")
    op.drop_table("incidente_sector_adicional")


def _existing_sector_names(connection) -> set[str]:
    rows = connection.execute(sa.text("SELECT nombre FROM sector")).fetchall()
    return {row[0] for row in rows}


def _insert_sector(connection, nombre: str) -> None:
    now = _now()
    connection.execute(
        sa.text(
            "INSERT INTO sector (nombre, descripcion, created_at, updated_at) "
            "VALUES (:nombre, :descripcion, :created_at, :updated_at)"
        ),
        {
            "nombre": nombre,
            "descripcion": DESCRIPCIONES[nombre],
            "created_at": now,
            "updated_at": now,
        },
    )


def upgrade() -> None:
    connection = op.get_bind()

    # ── Paso 1: tablas de union ──────────────────────────────────────────────
    _create_association_tables()

    # ── Paso 2: NULL en referencias a sectores legacy ────────────────────────
    legacy_ids = connection.execute(
        sa.text("SELECT id FROM sector WHERE nombre IN :nombres").bindparams(
            sa.bindparam("nombres", expanding=True)
        ),
        {"nombres": list(SECTORES_LEGACY)},
    ).fetchall()
    legacy_id_list = [row[0] for row in legacy_ids]

    if legacy_id_list:
        params = {"ids": legacy_id_list}
        connection.execute(
            sa.text(
                "UPDATE incidente SET sector_id = NULL "
                "WHERE sector_id IN :ids"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            params,
        )
        connection.execute(
            sa.text(
                "UPDATE clasificacion_log SET sector_id_predicho = NULL "
                "WHERE sector_id_predicho IN :ids"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            params,
        )
        connection.execute(
            sa.text(
                "UPDATE clasificacion_log SET sector_id_validado = NULL "
                "WHERE sector_id_validado IN :ids"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            params,
        )

        # ── Paso 3: eliminar filas legacy ────────────────────────────────────
        connection.execute(
            sa.text("DELETE FROM sector WHERE id IN :ids").bindparams(
                sa.bindparam("ids", expanding=True)
            ),
            params,
        )

    # ── Paso 4: upsert de los cinco sectores canonicos ───────────────────────
    existentes = _existing_sector_names(connection)
    for nombre in SECTORES_CANONICOS:
        if nombre not in existentes:
            _insert_sector(connection, nombre)


def downgrade() -> None:
    connection = op.get_bind()

    # ── Revertir asociaciones ────────────────────────────────────────────────
    _drop_association_tables()

    # ── Retirar sectores nuevos (Sistemas se preserva) ───────────────────────
    connection.execute(
        sa.text("DELETE FROM sector WHERE nombre IN :nombres").bindparams(
            sa.bindparam("nombres", expanding=True)
        ),
        {"nombres": list(SECTORES_NUEVOS)},
    )

    # ── Restaurar vocabulario legacy ─────────────────────────────────────────
    existentes = _existing_sector_names(connection)
    legacy_descripciones = {
        "Operaciones": (
            "Procesos compartidos, gestion de servicios, planificacion, "
            "continuidad operativa"
        ),
        "Soporte Técnico": (
            "Equipamiento de usuarios, perifericos, software cliente, "
            "asistencia remota"
        ),
    }
    for nombre, descripcion in legacy_descripciones.items():
        if nombre not in existentes:
            now = _now()
            connection.execute(
                sa.text(
                    "INSERT INTO sector (nombre, descripcion, created_at, updated_at) "
                    "VALUES (:nombre, :descripcion, :created_at, :updated_at)"
                ),
                {
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "created_at": now,
                    "updated_at": now,
                },
            )
