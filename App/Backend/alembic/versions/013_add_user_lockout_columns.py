"""Migracion 013: columnas de bloqueo por intentos fallidos en `users` (IAH-002, c-63a).

Responsabilidad:
    Agrega a `users` el contador de intentos fallidos consecutivos
    (`failed_attempts`) y el instante de fin de bloqueo (`locked_until`). El
    bloqueo es por CUENTA, configurable y apagado por defecto via el flag
    `account_lockout_enabled`.

    La recreacion usa `batch_alter_table` para ser portable entre PostgreSQL
    (ALTER directo) y SQLite (recreacion de tabla), de modo que la suite de
    migraciones corre sobre SQLite en archivo temporal.

    NO muta datos ni siembra nada. Las credenciales sembradas de desarrollo
    quedan grandfather (no se tocan).

Revision ID: 013
Revises: 012
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None

_TABLE = "users"


def upgrade() -> None:
    """Agrega `failed_attempts` (default 0) y `locked_until` (nullable)."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.add_column(
            sa.Column(
                "failed_attempts",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch_op.add_column(
            sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    """Elimina las columnas de bloqueo (restaura el esquema previo)."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.drop_column("locked_until")
        batch_op.drop_column("failed_attempts")