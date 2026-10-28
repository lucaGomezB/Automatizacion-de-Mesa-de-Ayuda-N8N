"""Migracion 023: auditoria durable del directorio (c-153, Tema D).

Responsabilidad:
    Crea la tabla append-only `directorio_auditoria`, traza DURABLE de las
    operaciones del directorio (gestion y resolucion de contactos), analoga a
    `incidente_evento` (c-86, D8). Complementa el evento estructurado de structlog
    con una fila persistente por operacion.

Privacidad (DIR-013):
    La tabla almacena SOLO identificadores internos (`empleado_id`,
    `actor_empleado_id`), la operacion, el resultado, el canal de resolucion y el
    instante. NO se crean columnas para email, telefono ni nombre: la auditoria no
    contiene PII en claro. Los identificadores son enteros opacos SIN clave
    foranea: la auditoria no impone acoplamiento referencial.

Append-only:
    No se crea ningun endpoint ni trigger de edicion/borrado; la inmutabilidad es
    de aplicacion (el repositorio no expone update/delete).

Reversibilidad:
    El downgrade elimina los indices y la tabla. No toca ninguna otra entidad.

Revision ID: 023
Revises: 022
Create Date: 2026-10-28
"""

import sqlalchemy as sa
from alembic import op

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None

_TABLE = "directorio_auditoria"


def upgrade() -> None:
    """Crea la tabla de auditoria durable sin PII y sus indices."""
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("operacion", sa.String(length=40), nullable=False),
        sa.Column("resultado", sa.String(length=20), nullable=False),
        sa.Column("canal", sa.String(length=20), nullable=True),
        sa.Column("empleado_id", sa.Integer(), nullable=True),
        sa.Column("actor_empleado_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_directorio_auditoria_empleado_id", _TABLE, ["empleado_id"]
    )
    op.create_index(
        "ix_directorio_auditoria_actor_empleado_id", _TABLE, ["actor_empleado_id"]
    )
    op.create_index("ix_directorio_auditoria_created_at", _TABLE, ["created_at"])


def downgrade() -> None:
    """Elimina la tabla de auditoria durable y sus indices (reversible)."""
    op.drop_index("ix_directorio_auditoria_created_at", table_name=_TABLE)
    op.drop_index(
        "ix_directorio_auditoria_actor_empleado_id", table_name=_TABLE
    )
    op.drop_index("ix_directorio_auditoria_empleado_id", table_name=_TABLE)
    op.drop_table(_TABLE)
