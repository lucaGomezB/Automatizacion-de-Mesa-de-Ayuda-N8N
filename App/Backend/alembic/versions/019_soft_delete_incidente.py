"""Migracion 019: borrado logico de incidentes (c-87, SD-001).

Responsabilidad (aditiva y append-only respecto de 018):
    Agrega a `incidente` las dos columnas del borrado logico:
        - `deleted_at` (TIMESTAMPTZ, nullable): NULL = activo; un instante no
          nulo retira el incidente de todas las superficies de lectura.
        - `deleted_by` (INTEGER, nullable): FK a `directorio_empleado.id` con
          `ON DELETE SET NULL`, indexada; registra el actor del borrado.

    NO muta datos ni siembra nada: las filas existentes quedan con ambas
    columnas en NULL (activas). NO crea ni elimina filas.

    El `upgrade` usa `op.add_column` (soportado nativamente por PostgreSQL y
    SQLite para columnas nullable) y crea el indice de `deleted_by`. El
    `downgrade` usa `batch_alter_table` para eliminar las columnas de forma
    portable (SQLite no soporta DROP COLUMN directo).

Revision ID: 019
Revises: 018
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None

_TABLA = "incidente"
_INDICE_DELETED_BY = "ix_incidente_deleted_by"


def upgrade() -> None:
    """Agrega `deleted_at` y `deleted_by` (nullable) y el indice de `deleted_by`."""
    with op.batch_alter_table(_TABLA) as batch_op:
        batch_op.add_column(
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "deleted_by",
                sa.Integer(),
                sa.ForeignKey(
                    "directorio_empleado.id",
                    ondelete="SET NULL",
                    name="fk_incidente_deleted_by_directorio_empleado",
                ),
                nullable=True,
            )
        )
    op.create_index(_INDICE_DELETED_BY, _TABLA, ["deleted_by"])


def downgrade() -> None:
    """Elimina el indice y las columnas del borrado logico (esquema previo)."""
    op.drop_index(_INDICE_DELETED_BY, table_name=_TABLA)
    with op.batch_alter_table(_TABLA) as batch_op:
        batch_op.drop_column("deleted_by")
        batch_op.drop_column("deleted_at")
