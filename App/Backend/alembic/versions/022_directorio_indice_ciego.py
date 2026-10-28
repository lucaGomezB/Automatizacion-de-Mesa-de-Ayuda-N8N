"""Migracion 022: indice ciego del directorio (c-153, Tema B).

Responsabilidad:
    Agrega a `directorio_empleado` las columnas derivadas de busqueda
    determinista `email_bidx` y `telefono_bidx` (HMAC-SHA-256 de la forma
    normalizada del contacto) y RELLENA (backfill) las filas existentes con el
    indice ciego derivado del contacto descifrado.

Motivacion (DIR-011/DIR-012 del delta):
    El cifrado Fernet de `email`/`telefono` (migracion 021) NO es determinista
    (IV aleatorio por operacion), de modo que la igualdad SQL sobre la columna
    cifrada no sirve para buscar. El indice ciego determinista restaura la
    busqueda por igualdad. La unicidad del email se preserva con un indice UNIQUE
    sobre `email_bidx`; `telefono_bidx` no es UNIQUE (el telefono es repetible).

Clave dedicada:
    La derivacion usa `settings.directory_blind_index_key` (HMAC-SHA-256, clave
    dedicada del directorio, independiente de la clave Fernet de
    pseudonimizacion). Debe estar disponible para el backfill.

Reversibilidad (downgrade DOCUMENTADO):
    El downgrade elimina `email_bidx`, `telefono_bidx` y sus indices. No toca el
    contacto cifrado: la migracion 021 es la que posee el cifrado.

Portabilidad:
    Usa `batch_alter_table` para que el alta/borrado de columnas funcione tanto
    en PostgreSQL (`ALTER TABLE`) como en SQLite (recreacion de tabla, usada por
    la suite de migraciones).

Revision ID: 022
Revises: 021
Create Date: 2026-10-28

Prerequisito de datos: la clave `DIRECTORY_BLIND_INDEX_KEY` debe estar
configurada para derivar el indice del backfill.
"""

import sqlalchemy as sa
from alembic import op

revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None

_TABLE = "directorio_empleado"
_INDEX_EMAIL_BIDX = "ix_directorio_empleado_email_bidx"
_INDEX_TELEFONO_BIDX = "ix_directorio_empleado_telefono_bidx"


def _contacto_plano(valor: str | None) -> str | None:
    """Devuelve el contacto en claro: descifra el token Fernet o deja el valor.

    Tolerante: un valor que no sea un token Fernet valido (p. ej. una fila
    insertada en texto por fuera de la aplicacion) se devuelve tal cual.
    """
    if valor is None:
        return None
    from app.utils.encryption import decrypt_value

    try:
        return decrypt_value(valor)
    except Exception:
        return valor


def _leer_contacto(bind) -> list[tuple[int, str | None, str | None]]:
    filas = bind.execute(
        sa.text(f"SELECT id, email, telefono FROM {_TABLE} ORDER BY id")
    ).fetchall()
    return [(fila[0], fila[1], fila[2]) for fila in filas]


def _backfill(bind) -> None:
    """Deriva `email_bidx`/`telefono_bidx` de cada fila existente."""
    from app.config.settings import get_settings
    from app.utils.blind_index import indice_ciego_email, indice_ciego_telefono

    clave = get_settings().directory_blind_index_key
    for fila_id, email, telefono in _leer_contacto(bind):
        email_plano = _contacto_plano(email)
        telefono_plano = _contacto_plano(telefono)
        email_bidx = indice_ciego_email(email_plano, clave) if email_plano else None
        telefono_bidx = (
            indice_ciego_telefono(telefono_plano, clave) if telefono_plano else None
        )
        bind.execute(
            sa.text(
                f"UPDATE {_TABLE} SET email_bidx=:eb, telefono_bidx=:tb WHERE id=:id"
            ),
            {"eb": email_bidx, "tb": telefono_bidx, "id": fila_id},
        )


def upgrade() -> None:
    # 1) Agregar las columnas derivadas (nullable: son un indice de busqueda; la
    #    aplicacion las completa en cada escritura. Las filas legadas o
    #    insertadas fuera de la aplicacion pueden quedar con NULL).
    with op.batch_alter_table(_TABLE) as batch:
        batch.add_column(sa.Column("email_bidx", sa.String(length=64), nullable=True))
        batch.add_column(
            sa.Column("telefono_bidx", sa.String(length=64), nullable=True)
        )
    # 2) Backfill: derivar el indice ciego del contacto existente.
    _backfill(op.get_bind())
    # 3) Unicidad del email sobre el indice determinista; telefono repetible.
    op.create_index(_INDEX_EMAIL_BIDX, _TABLE, ["email_bidx"], unique=True)
    op.create_index(_INDEX_TELEFONO_BIDX, _TABLE, ["telefono_bidx"])


def downgrade() -> None:
    op.drop_index(_INDEX_TELEFONO_BIDX, table_name=_TABLE)
    op.drop_index(_INDEX_EMAIL_BIDX, table_name=_TABLE)
    with op.batch_alter_table(_TABLE) as batch:
        batch.drop_column("telefono_bidx")
        batch.drop_column("email_bidx")