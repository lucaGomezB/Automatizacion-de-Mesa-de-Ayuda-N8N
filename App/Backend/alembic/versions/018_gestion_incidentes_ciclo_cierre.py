"""Migracion 018: rol gestion_incidentes y ciclo de cierre (c-86).

Responsabilidad (append-only respecto de 017):
    1. Amplia el CHECK `ck_directorio_empleado_rol` a los CUATRO valores del
       vocabulario, incorporando `gestion_incidentes` (DIR-003, D12). Es una
       ampliacion aditiva: no requiere backfill de datos.
    2. Crea `incidente_cierre_sector` (cierre por sector, PK compuesta), 
       `incidente_evento` (auditoria del ciclo) e `incidente_comentario`
       (comentarios append-only), con sus FKs e indices (D4/D7/D8).

    `batch_alter_table` es portable entre PostgreSQL (ALTER directo) y SQLite
    (recreacion de tabla).

    `downgrade`: reasigna las filas `gestion_incidentes -> usuario_final` ANTES
    de restaurar el CHECK de tres valores (para no dejar filas que lo violen);
    luego elimina las tres tablas.

Revision ID: 018
Revises: 017
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None

_DIRECTORIO = "directorio_empleado"
_CHECK = "ck_directorio_empleado_rol"

# Vocabulario nuevo (cuatro valores) y previo (tres valores) para rollback.
_ROL_CHECK_CUATRO = (
    "rol IN ('usuario_final', 'mesa_de_ayuda', 'administrador_directorio', "
    "'gestion_incidentes')"
)
_ROL_CHECK_TRES = (
    "rol IN ('usuario_final', 'mesa_de_ayuda', 'administrador_directorio')"
)

_CIERRE = "incidente_cierre_sector"
_EVENTO = "incidente_evento"
_COMENTARIO = "incidente_comentario"


def upgrade() -> None:
    """CHECK de cuatro valores + tablas del ciclo de cierre."""
    # 1. CHECK nuevo (cuatro valores). Ampliacion aditiva, sin backfill.
    with op.batch_alter_table(_DIRECTORIO) as batch_op:
        batch_op.drop_constraint(_CHECK, type_="check")
        batch_op.create_check_constraint(_CHECK, _ROL_CHECK_CUATRO)

    # 2. Cierre por sector (D4): PK compuesta (incidente_id, sector_id).
    op.create_table(
        _CIERRE,
        sa.Column("incidente_id", sa.Integer(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.Column("cerrado_por", sa.Integer(), nullable=True),
        sa.Column("cerrado_en", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["incidente_id"], ["incidente.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["cerrado_por"], ["directorio_empleado.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("incidente_id", "sector_id"),
    )
    op.create_index(
        "ix_incidente_cierre_sector_sector_id", _CIERRE, ["sector_id"]
    )
    op.create_index(
        "ix_incidente_cierre_sector_cerrado_por", _CIERRE, ["cerrado_por"]
    )

    # 3. Auditoria del ciclo (D8).
    op.create_table(
        _EVENTO,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("incidente_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("actor_empleado_id", sa.Integer(), nullable=True),
        sa.Column("sector_id", sa.Integer(), nullable=True),
        sa.Column("estado_anterior", sa.String(length=50), nullable=True),
        sa.Column("estado_nuevo", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["incidente_id"], ["incidente.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["actor_empleado_id"], ["directorio_empleado.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incidente_evento_incidente_id", _EVENTO, ["incidente_id"])
    op.create_index(
        "ix_incidente_evento_actor_empleado_id", _EVENTO, ["actor_empleado_id"]
    )
    op.create_index("ix_incidente_evento_created_at", _EVENTO, ["created_at"])

    # 4. Comentarios append-only (D7).
    op.create_table(
        _COMENTARIO,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("incidente_id", sa.Integer(), nullable=False),
        sa.Column("autor_empleado_id", sa.Integer(), nullable=True),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["incidente_id"], ["incidente.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["autor_empleado_id"], ["directorio_empleado.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_incidente_comentario_incidente_id", _COMENTARIO, ["incidente_id"]
    )
    op.create_index(
        "ix_incidente_comentario_autor_empleado_id", _COMENTARIO, ["autor_empleado_id"]
    )
    op.create_index(
        "ix_incidente_comentario_created_at", _COMENTARIO, ["created_at"]
    )


def downgrade() -> None:
    """Elimina las tablas y restaura el CHECK de tres valores (reasigna antes)."""
    bind = op.get_bind()

    # 1. Reasignar ANTES de restaurar el CHECK: ninguna fila debe violarlo.
    bind.execute(
        sa.text(
            f"UPDATE {_DIRECTORIO} SET rol = 'usuario_final' "
            "WHERE rol = 'gestion_incidentes'"
        )
    )

    # 2. Restaurar el CHECK de tres valores.
    with op.batch_alter_table(_DIRECTORIO) as batch_op:
        batch_op.drop_constraint(_CHECK, type_="check")
        batch_op.create_check_constraint(_CHECK, _ROL_CHECK_TRES)

    # 3. Eliminar las tablas del ciclo (los indices se eliminan con ellas).
    op.drop_table(_COMENTARIO)
    op.drop_table(_EVENTO)
    op.drop_table(_CIERRE)
