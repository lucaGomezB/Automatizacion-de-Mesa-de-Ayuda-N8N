"""Migracion: contadores de la guarda de costo en runtime (c-45, ALTA).

Responsabilidad:
    Aditiva respecto de 001/002/003/004/005/006. NO muta `001_seed_catalogs.py`.

    Crea la tabla `costo_guarda_contador`, que persiste los contadores de la
    guarda de costo por (ambito, clave, ventana_inicio):

    - `ambito` (String(16), NOT NULL): `global` | `surface` | `caller`.
    - `clave` (String(64), NOT NULL): `budget`, `rate`, nombre de superficie o
      numero E.164 CRUDO para `caller`.
    - `ventana_inicio` (TIMESTAMPTZ, NOT NULL, indexado): inicio de la ventana
      (bucket tumbling); el indice habilita la purga de ventanas vencidas.
    - `llamadas` (Integer, NOT NULL, default 0): llamadas pagas reservadas.
    - `costo_usd` (Numeric(12,6), NOT NULL, default 0): gasto acumulado USD.
    - `created_at` / `updated_at` (TIMESTAMPTZ): auditoria (TimestampMixin).

    La restriccion unica `(ambito, clave, ventana_inicio)` habilita el UPSERT
    atomico de la reserva (`INSERT ... ON CONFLICT ... DO UPDATE ... RETURNING`),
    que evita la carrera chequear-y-actualizar entre peticiones concurrentes.

    El `downgrade` dropea la tabla (los contadores son efimeros; no hay datos de
    negocio que restaurar).

Revision ID: 007
Revises: 006
Create Date: 2026-09-21

Aprobacion humana explicita (gobernanza ALTA):
    El usuario aprobo el plan de la guarda de costo en runtime, incluido el
    almacen en PostgreSQL con la migracion 007, el fail-closed con notificacion
    y la degradacion a deterministico + revision humana, antes de la
    implementacion de este change (engram obs #953, tarea 0.2).
"""

import sqlalchemy as sa
from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None

_TABLE = "costo_guarda_contador"
_UNIQUE_CONSTRAINT = "uq_costo_guarda_contador_ambito_clave_ventana"
_INDEX_VENTANA = "ix_costo_guarda_contador_ventana_inicio"
_INDEX_CREATED = "ix_costo_guarda_contador_created_at"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ambito", sa.String(length=16), nullable=False),
        sa.Column("clave", sa.String(length=64), nullable=False),
        sa.Column("ventana_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "llamadas", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "costo_usd",
            sa.Numeric(precision=12, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "ambito",
            "clave",
            "ventana_inicio",
            name=_UNIQUE_CONSTRAINT,
        ),
    )
    op.create_index(_INDEX_VENTANA, _TABLE, ["ventana_inicio"])
    op.create_index(_INDEX_CREATED, _TABLE, ["created_at"])


def downgrade() -> None:
    op.drop_index(_INDEX_CREATED, table_name=_TABLE)
    op.drop_index(_INDEX_VENTANA, table_name=_TABLE)
    op.drop_table(_TABLE)
