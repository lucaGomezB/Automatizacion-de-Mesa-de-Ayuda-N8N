"""Migracion 010: `fecha_baja` del directorio de empleados (c-54, W2).

Responsabilidad:
    Aditiva y append-only respecto de 009 (que ya fue publicada): agrega la
    columna nullable `fecha_baja` (TIMESTAMPTZ) a `directorio_empleado`.

    `fecha_baja` registra el instante de desactivacion de un empleado y es la
    base de la RETENCION (DIR-007): la fila se conserva mientras la relacion
    laboral este activa mas 1 año y luego se ejecuta el borrado fisico. Al
    reactivar un empleado, la columna se limpia (NULL).

    La migracion NO muta ninguna otra tabla ni siembra datos. El borrado por
    retencion es operativo (script `scripts/purgar_directorio.py`), no parte de
    esta migracion.

Revision ID: 010
Revises: 009
Create Date: 2026-09-23

Prerequisito de datos: ninguno (columna nueva nullable; las filas existentes
quedan con `fecha_baja = NULL`).
"""

import sqlalchemy as sa
from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None

_TABLE = "directorio_empleado"
_COLUMN = "fecha_baja"


def upgrade() -> None:
    op.add_column(
        _TABLE,
        sa.Column(_COLUMN, sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column(_TABLE, _COLUMN)
