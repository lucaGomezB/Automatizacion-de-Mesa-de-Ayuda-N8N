"""Migracion: instrumentacion temporal end-to-end de incidentes (C-39, ALTA).

Responsabilidad:
    Aditiva respecto de 001/002/003/004/005. NO muta `001_seed_catalogs.py`.

    Agrega dos columnas TIMESTAMPTZ nullable a la tabla `incidente`:

    - `ingresado_en`: instante en que el mensaje INGRESA al sistema, capturado
      en el borde del trigger del canal y enviado por N8N en el payload de alta.
      Nullable: los clientes API directos y las filas historicas pueden no
      proveerlo; la ausencia no bloquea el alta.

    - `persistido_en`: instante en que finalizan las escrituras del incidente y
      su log de clasificacion, sellado UNA sola vez dentro de la transaccion de
      alta. Inmutable: no usa `onupdate` y no figura en el contrato de update,
      de modo que una revision humana posterior no lo sobrescribe.

    Ambas columnas son nullable y SIN indices: no se agrega backfill de filas
    historicas (no existe el dato de ingreso y fabricarlo violaria la honestidad
    de la medicion). El `downgrade` dropea ambas.

    La latencia end-to-end NO se denormaliza: se deriva en la capa de lectura
    como `persistido_en - ingresado_en`.

Revision ID: 006
Revises: 005
Create Date: 2026-09-19

Aprobacion humana explicita (gobernanza ALTA):
    El usuario aprobo el plan de migracion, la definicion del instante de ingreso
    (borde del trigger por canal), la tolerancia de futuro (30 s) y la politica de
    latencia negativa (marcar como anomalia y excluir del corpus) antes de la
    implementacion de este change. El plan de migracion es aditivo, sin backfill.
"""

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "incidente",
        sa.Column("ingresado_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "incidente",
        sa.Column("persistido_en", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("incidente", "persistido_en")
    op.drop_column("incidente", "ingresado_en")
