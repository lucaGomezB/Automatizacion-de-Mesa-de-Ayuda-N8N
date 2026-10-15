"""Migracion 020: indice trigram para la busqueda de incidentes (c-88, D6).

Responsabilidad (aditiva respecto de 019):
    Sostener la busqueda por subcadena de `descripcion_pseudonimizada` (IS-001)
    con un indice adecuado. Un ILIKE de subcadena NO puede usar un B-tree; el
    indice GIN de trigramas lo acelera para terminos de 3+ caracteres:
        - `CREATE EXTENSION IF NOT EXISTS pg_trgm`.
        - `CREATE INDEX ... USING gin (descripcion_pseudonimizada gin_trgm_ops)`.

    `pg_trgm` es una extension TRUSTED en PostgreSQL 15, por lo que el dueno de
    la base puede crearla sin privilegios de superusuario.

    La migracion NO muta datos ni siembra nada.

Portabilidad:
    El DDL es especifico de PostgreSQL. En motores que no son PostgreSQL (por
    ejemplo el SQLite con el que corren los tests de migraciones) la migracion
    es un NO-OP, de modo que la cadena de migraciones sigue siendo portable y
    las migraciones previas siguen aplicandose sin cambios.

    El `downgrade` elimina el indice; la extension `pg_trgm` queda instalada
    (sin efectos adversos).

Revision ID: 020
Revises: 019
Create Date: 2026-10-15
"""

from alembic import op

revision = "020"
down_revision = "019"
branch_labels = None
depends_on = None

_TABLA = "incidente"
_COLUMNA = "descripcion_pseudonimizada"
_INDICE = "ix_incidente_descripcion_pseudonimizada_trgm"


def upgrade() -> None:
    """Habilita `pg_trgm` y crea el indice GIN trigram (no-op fuera de PostgreSQL)."""
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        f"CREATE INDEX {_INDICE} ON {_TABLA} "
        f"USING gin ({_COLUMNA} gin_trgm_ops)"
    )


def downgrade() -> None:
    """Elimina el indice trigram (deja la extension instalada)."""
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(f"DROP INDEX IF EXISTS {_INDICE}")
