"""Migracion: agrega origen_message_id y origen_evento a incidente (C-33, ALTA).

Responsabilidad:
    Aditiva respecto de 001/002/003/004. NO muta `001_seed_catalogs.py`.

    Agrega dos columnas a la tabla `incidente`:

    - `origen_message_id` (String(255), nullable) con una restriccion UNIQUE.
      La columna es nullable para no obligar a los emisores que no proveen un
      identificador de mensaje de origen (formulario web, clientes API directos);
      la unicidad se aplica a los valores no nulos, de modo que un mismo
      `Message-ID` de Outlook no puede producir mas de un incidente.

    - `origen_evento` (String(50), nullable, SIN unicidad) que registra el
      marcador de evento declarado por el emisor. Es el campo que satisface el
      escenario "Evento de creacion crea el incidente" de la spec: el marcador
      de creacion queda persistido en la fila; un alta directa sin marcador lo
      deja nulo. No requiere indice: no se consulta por el.

    La restriccion de unicidad se implementa como un indice unico explicito
    (`ix_incidente_origen_message_id`) en lugar de un `UNIQUE` inline: es el
    patron portable entre SQLite (suites unitarias) y PostgreSQL (integracion),
    porque SQLite no acepta agregar una columna con UNIQUE via ALTER TABLE.

Revision ID: 005
Revises: 004
Create Date: 2026-09-17

Aprobacion humana explicita (gobernanza ALTA):
    El usuario aprobo el plan de migracion el 2026-09-17. El 2026-09-17 aprobo
    ademas extender esta misma revision 005 para incluir `origen_evento`
    (nullable, sin unicidad), como fix post-verificacion del warning W2.
"""

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None

_INDEX_NAME = "ix_incidente_origen_message_id"


def upgrade() -> None:
    op.add_column(
        "incidente",
        sa.Column("origen_message_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        _INDEX_NAME,
        "incidente",
        ["origen_message_id"],
        unique=True,
    )
    op.add_column(
        "incidente",
        sa.Column("origen_evento", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("incidente", "origen_evento")
    op.drop_index(_INDEX_NAME, table_name="incidente")
    op.drop_column("incidente", "origen_message_id")
