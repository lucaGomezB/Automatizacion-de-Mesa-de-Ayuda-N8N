"""Migracion 015: `lockout_window_start` dedicada en `users` (W2, c-63a).

Responsabilidad:
    Agrega a `users` la columna `lockout_window_start`, que ancla la ventana de
    conteo de intentos fallidos del bloqueo por cuenta (IAH-002). Antes la
    ventana se derivaba de `updated_at`, que cualquier update ajeno (p. ej.
    desactivar la cuenta) podia mover y reiniciar el contador de forma no
    deseada. La columna dedicada elimina esa dependencia.

    Usa `batch_alter_table` para ser portable entre PostgreSQL (ALTER directo) y
    SQLite (recreacion de tabla), de modo que la suite de migraciones corre
    sobre SQLite en archivo temporal.

    NO muta datos ni siembra nada. Las cuentas existentes quedan con la columna
    en NULL (sin ventana activa).

Revision ID: 015
Revises: 014
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None

_TABLE = "users"


def upgrade() -> None:
    """Agrega `lockout_window_start` (nullable)."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.add_column(
            sa.Column(
                "lockout_window_start",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Elimina `lockout_window_start` (restaura el esquema previo)."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.drop_column("lockout_window_start")