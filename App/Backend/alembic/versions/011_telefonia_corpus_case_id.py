"""Migracion 011: `corpus_case_id` y tabla corta `telefonia_pending_call` (c-70).

Responsabilidad:
    Aditiva y append-only respecto de 010 (que ya fue publicada):

    1. Agrega la columna nullable `corpus_case_id` (String(64)) a
       `telefonia_ingreso`, con indice `ix_telefonia_ingreso_corpus_case_id`.
       Es ADITIVA y sin backfill: las filas historicas quedan en NULL y las
       llamadas de produccion sin caso de corpus tambien. NO reemplaza a
       `call_sid` (idempotencia) ni al `origen_message_id` del incidente.

    2. Crea la tabla de vida corta `telefonia_pending_call`, que materializa el
       mapeo efimero `call_sid -> corpus_case_id` elegido en OQ1 = Opcion B:

           call_sid        String(64) PK   (clave del upsert)
           corpus_case_id  String(64) NOT NULL
           created_at      TIMESTAMPTZ NOT NULL (base de la purga TTL)

       Sin PII. El TTL se aplica en runtime (purga oportunista y borrado
       explicito en el callback), no en la migracion.

    La migracion NO muta ninguna otra tabla ni siembra datos.

Revision ID: 011
Revises: 010
Create Date: 2026-10-05

Prerequisito de datos: ninguno (columna nueva nullable + tabla nueva).
"""

import sqlalchemy as sa
from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None

_TABLE_INGRESO = "telefonia_ingreso"
_COLUMN = "corpus_case_id"
_INDEX_INGRESO = "ix_telefonia_ingreso_corpus_case_id"
_TABLE_PENDING = "telefonia_pending_call"
_INDEX_PENDING = "ix_telefonia_pending_call_created_at"


def upgrade() -> None:
    op.add_column(
        _TABLE_INGRESO,
        sa.Column(_COLUMN, sa.String(length=64), nullable=True),
    )
    op.create_index(_INDEX_INGRESO, _TABLE_INGRESO, [_COLUMN])

    op.create_table(
        _TABLE_PENDING,
        sa.Column("call_sid", sa.String(length=64), primary_key=True),
        sa.Column("corpus_case_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(_INDEX_PENDING, _TABLE_PENDING, ["created_at"])


def downgrade() -> None:
    op.drop_index(_INDEX_PENDING, table_name=_TABLE_PENDING)
    op.drop_table(_TABLE_PENDING)
    op.drop_index(_INDEX_INGRESO, table_name=_TABLE_INGRESO)
    op.drop_column(_TABLE_INGRESO, _COLUMN)
