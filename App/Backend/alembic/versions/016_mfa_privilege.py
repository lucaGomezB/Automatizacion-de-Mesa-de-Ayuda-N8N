"""Migracion 016: privilegio de identidad y MFA TOTP (c-63b, Fase B).

Responsabilidad:
    Agrega a `users` el flag `is_privileged` (fuente de verdad del privilegio,
    IAH-005) y los campos del segundo factor TOTP (IAH-006): `totp_secret`
    (cifrado at-rest por el TypeDecorator del modelo, tipo Text en la DB),
    `totp_enabled` y `mfa_recovery_codes` (JSON con hashes bcrypt de los codigos
    de recuperacion). Marca el `admin` sembrado por la migracion 003 como
    privilegiado.

    Usa `batch_alter_table` para ser portable entre PostgreSQL (ALTER directo) y
    SQLite (recreacion de tabla), de modo que la suite offline la crea via
    `Base.metadata` y la suite de migraciones la corre sobre SQLite en archivo.

    `totp_secret` se declara como `Text`: el cifrado/descifrado Fernet es
    transparente en el ORM (`EncryptedText`), por lo que el valor persistido ya
    es ciphertext base64 (columna de texto).

Revision ID: 016
Revises: 015
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None

_TABLE = "users"


def upgrade() -> None:
    """Agrega `is_privileged` y los campos MFA, y marca `admin` privilegiado."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_privileged",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(sa.Column("totp_secret", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "totp_enabled",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column("mfa_recovery_codes", sa.Text(), nullable=True)
        )

    # El admin sembrado por la migracion 003 queda privilegiado. El bindparam
    # booleano se adapta por dialecto (0/1 en SQLite, false/true en PostgreSQL).
    op.get_bind().execute(
        sa.text(
            "UPDATE users SET is_privileged = :privileged "
            "WHERE username = 'admin'"
        ),
        {"privileged": True},
    )


def downgrade() -> None:
    """Elimina `is_privileged` y los campos MFA (restaura el esquema previo)."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.drop_column("mfa_recovery_codes")
        batch_op.drop_column("totp_enabled")
        batch_op.drop_column("totp_secret")
        batch_op.drop_column("is_privileged")
