"""Migracion 014: tabla `refresh_token` y `token_version` en `users` (c-63a).

Responsabilidad:
    Crea la tabla `refresh_token` que persiste los refresh tokens OPACOS
    rotativos (solo su hash SHA-256, `user_id`, expiracion, revocacion y el
    enlace al token rotado `rotated_from`), y agrega `token_version` a `users`
    para la revocacion administrativa masiva (IAH-003/IAH-004).

    La tabla es compatible con SQLite (sin tipos PostgreSQL-especificos), de
    modo que el subconjunto offline de la suite la crea tanto via `Base.metadata`
    como via Alembic.

    NO siembra datos. El access token de vida corta y el refresh rotativo usan
    la configuracion nueva (`jwt_access_expire_minutes`,
    `jwt_refresh_expire_minutes`).

Revision ID: 014
Revises: 013
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None

_USERS = "users"
_TABLE = "refresh_token"


def upgrade() -> None:
    """Agrega `token_version` y crea la tabla `refresh_token`."""
    with op.batch_alter_table(_USERS) as batch_op:
        batch_op.add_column(
            sa.Column(
                "token_version",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rotated_from", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["rotated_from"], ["refresh_token.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_token_token_hash"),
    )
    op.create_index("ix_refresh_token_user_id", _TABLE, ["user_id"])
    op.create_index("ix_refresh_token_token_hash", _TABLE, ["token_hash"])
    op.create_index("ix_refresh_token_revoked_at", _TABLE, ["revoked_at"])


def downgrade() -> None:
    """Elimina la tabla `refresh_token` y `token_version` (rollback)."""
    op.drop_index("ix_refresh_token_revoked_at", table_name=_TABLE)
    op.drop_index("ix_refresh_token_token_hash", table_name=_TABLE)
    op.drop_index("ix_refresh_token_user_id", table_name=_TABLE)
    op.drop_table(_TABLE)

    with op.batch_alter_table(_USERS) as batch_op:
        batch_op.drop_column("token_version")