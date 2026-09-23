"""Migracion 009: directorio de empleados (c-54).

Responsabilidad:
    Aditiva respecto de 001..008. NO muta las anteriores.

    Crea la tabla `directorio_empleado`, entidad de contacto SEPARADA de la
    autenticacion (`users`), con los campos minimizados (design.md D6b):

    - `legajo` (String(50), NOT NULL, UNIQUE): identificador laboral.
    - `nombre` (String(200), NOT NULL).
    - `email` (String(254), NOT NULL, UNIQUE e indexado): TEXTO PLANO, sin
      cifrado de aplicacion ni indice ciego (D4).
    - `telefono` (String(20), NULL, indexado, repetible): E.164 en texto plano.
    - `sector_id` (Integer, NULL, FK -> sector.id ON DELETE SET NULL).
    - `rol` (String(30), NOT NULL) con CHECK del vocabulario de tres valores.
    - `activo` (Boolean, NOT NULL, default true).
    - `user_id` (Integer, NULL, FK -> users.id ON DELETE SET NULL).
    - `created_at` / `updated_at` (TIMESTAMPTZ, NOT NULL).

    NO se siembra PII real (D9): el seed sintetico es un script dev-only fuera
    de Alembic.

    El `downgrade` dropea la tabla (no hay datos de negocio que restaurar: las
    filas son recargables desde su fuente).

Revision ID: 009
Revises: 008
Create Date: 2026-09-23

Prerequisito de datos: ninguno (tabla nueva; sin backfill).
"""

import sqlalchemy as sa
from alembic import op

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None

_TABLE = "directorio_empleado"
_INDEX_LEGAJO = "ix_directorio_empleado_legajo"
_INDEX_EMAIL = "ix_directorio_empleado_email"
_INDEX_TELEFONO = "ix_directorio_empleado_telefono"
_INDEX_SECTOR = "ix_directorio_empleado_sector_id"
_INDEX_USER = "ix_directorio_empleado_user_id"
_INDEX_CREATED = "ix_directorio_empleado_created_at"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("legajo", sa.String(length=50), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.Column("sector_id", sa.Integer(), nullable=True),
        sa.Column("rol", sa.String(length=30), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sector_id"], ["sector.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.CheckConstraint(
            "rol IN ('usuario_final', 'operador', 'administrador_directorio')",
            name="ck_directorio_empleado_rol",
        ),
    )
    # Indices UNIQUE: unicidad de legajo y email.
    op.create_index(_INDEX_LEGAJO, _TABLE, ["legajo"], unique=True)
    op.create_index(_INDEX_EMAIL, _TABLE, ["email"], unique=True)
    # Indices de apoyo: telefono (repetible), sector y cuenta vinculada.
    op.create_index(_INDEX_TELEFONO, _TABLE, ["telefono"])
    op.create_index(_INDEX_SECTOR, _TABLE, ["sector_id"])
    op.create_index(_INDEX_USER, _TABLE, ["user_id"])
    op.create_index(_INDEX_CREATED, _TABLE, ["created_at"])


def downgrade() -> None:
    op.drop_index(_INDEX_CREATED, table_name=_TABLE)
    op.drop_index(_INDEX_USER, table_name=_TABLE)
    op.drop_index(_INDEX_SECTOR, table_name=_TABLE)
    op.drop_index(_INDEX_TELEFONO, table_name=_TABLE)
    op.drop_index(_INDEX_EMAIL, table_name=_TABLE)
    op.drop_index(_INDEX_LEGAJO, table_name=_TABLE)
    op.drop_table(_TABLE)
