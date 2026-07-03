"""Migracion: crea tabla users y siembra usuario admin.

Responsabilidad:
    Crea la tabla 'users' para almacenar credenciales de operadores
    y siembra un usuario administrador inicial con password hasheada
    con bcrypt. El seed solo se ejecuta si la tabla esta vacia (idempotente).

    Esta migracion debe ejecutarse antes de proteger las rutas con
    autenticacion JWT, ya que sin un usuario en la base de datos
    el login seria imposible.

Usuario sembrado:
    username: admin
    password: admin123 (bcrypt hashed)

IMPORTANTE: Cambiar la password en produccion inmediatamente despues
del primer despliegue.

Revision ID: 003
Revises: 002
Create Date: 2026-07-02
"""

import sqlalchemy as sa
from alembic import op
from datetime import datetime, timezone

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

# Hash bcrypt de "admin123" generado con bcrypt.
# Se incluye inline para que la migracion no dependa de
# imports de la aplicacion (passlib, modelos, etc.).
ADMIN_PASSWORD_HASH = (
    "$2b$12$SipUYgfdVzN6Go4dl9/X.Ovyr20T6w/WBL6YA0Z.VyugrWYdeIw7q"
)


def upgrade() -> None:
    """Crea la tabla users y siembra el usuario admin si la tabla esta vacia."""
    now = datetime.now(timezone.utc)

    # ── Crear tabla users ───────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_created_at", "users", ["created_at"])

    # ── Seed: usuario admin (solo si la tabla esta vacia) ───────────────────
    # Usamos raw SQL para verificar si ya hay registros, evitando dependencia
    # de imports de la aplicacion en el contexto de la migracion.
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT COUNT(*) FROM users"))
    count = result.scalar()

    if count == 0:
        op.bulk_insert(
            sa.table(
                "users",
                sa.column("username", sa.String),
                sa.column("hashed_password", sa.String),
                sa.column("is_active", sa.Boolean),
                sa.column("created_at", sa.DateTime(timezone=True)),
                sa.column("updated_at", sa.DateTime(timezone=True)),
            ),
            [
                {
                    "username": "admin",
                    "hashed_password": ADMIN_PASSWORD_HASH,
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
        )


def downgrade() -> None:
    """Elimina la tabla users."""
    op.drop_table("users")
