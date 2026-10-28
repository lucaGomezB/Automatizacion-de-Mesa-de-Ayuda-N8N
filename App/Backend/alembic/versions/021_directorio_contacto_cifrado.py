"""Migracion 021: cifrado at-rest del contacto del directorio (c-153, Tema A).

Responsabilidad:
    Convierte `directorio_empleado.email` y `directorio_empleado.telefono` de
    `VARCHAR` (texto plano, DIR-005) a `TEXT` cifrado con el TypeDecorator
    `EncryptedText` (Fernet), y RELLENA (backfill) las filas existentes
    cifrando el contacto con la clave Fernet activa.

Motivacion:
    DIR-005 (texto plano) queda SUPERADA por el ADR de reversion
    (`docs/seguridad/adr-001-...`). El contacto pasa a protegerse en reposo
    (DIR-011 del delta). El cifrado Fernet NO es determinista (IV aleatorio), de
    modo que la busqueda por igualdad se resuelve en el Tema B (indice ciego).

Reversibilidad (downgrade DOCUMENTADO):
    El downgrade DESCIFRA el contacto y restaura el tipo `VARCHAR`, devolviendo
    el texto plano. Es una accion de governance HIGH: reintroducir PII en claro
    exige justificacion escrita (ver el ADR y el plan de migracion del change).
    El downgrade es tolerante: un valor que no sea un token Fernet valido se deja
    intacto (permite revertir bases con filas insertadas en claro por fuera de la
    aplicacion).

Portabilidad:
    Usa `batch_alter_table` para que el cambio de tipo funcione tanto en
    PostgreSQL (`ALTER TABLE`) como en SQLite (recreacion de tabla, usada por la
    suite de migraciones).

Revision ID: 021
Revises: 020
Create Date: 2026-10-28

Prerequisito de datos: la clave Fernet activa
(`settings.pseudonymization_encryption_key`) debe estar disponible para cifrar
el backfill.
"""

import sqlalchemy as sa
from alembic import op

revision = "021"
down_revision = "020"
branch_labels = None
depends_on = None

_TABLE = "directorio_empleado"


def _ensure_encrypted(value: str | None) -> str | None:
    """Cifra el valor si no es ya un token Fernet (idempotente, tolerante)."""
    if value is None:
        return None
    from app.utils.encryption import decrypt_value, encrypt_value

    try:
        decrypt_value(value)  # ya es un token valido -> no re-cifrar
        return value
    except Exception:
        return encrypt_value(value)


def _ensure_plain(value: str | None) -> str | None:
    """Descifra el valor; si no es un token Fernet valido lo deja intacto."""
    if value is None:
        return None
    from app.utils.encryption import decrypt_value

    try:
        return decrypt_value(value)
    except Exception:
        return value


def _leer_contacto(bind) -> list[tuple[int, str | None, str | None]]:
    filas = bind.execute(
        sa.text(f"SELECT id, email, telefono FROM {_TABLE} ORDER BY id")
    ).fetchall()
    return [(fila[0], fila[1], fila[2]) for fila in filas]


def _reescribir_contacto(
    bind, filas: list[tuple[int, str | None, str | None]], transform: str
) -> None:
    send = _ensure_encrypted if transform == "encrypt" else _ensure_plain
    for fila_id, email, telefono in filas:
        bind.execute(
            sa.text(f"UPDATE {_TABLE} SET email=:e, telefono=:t WHERE id=:id"),
            {"e": send(email), "t": send(telefono), "id": fila_id},
        )


def upgrade() -> None:
    bind = op.get_bind()
    # 1) Leer el contacto en claro ANTES de recrear/alterar la columna.
    filas = _leer_contacto(bind)
    # 2) Convertir el tipo a TEXT (impl de EncryptedText).
    with op.batch_alter_table(_TABLE) as batch:
        batch.alter_column(
            "email",
            existing_type=sa.String(length=254),
            type_=sa.Text(),
            existing_nullable=False,
        )
        batch.alter_column(
            "telefono",
            existing_type=sa.String(length=20),
            type_=sa.Text(),
            existing_nullable=True,
        )
    # 3) Backfill: cifrar el contacto existente.
    _reescribir_contacto(bind, filas, "encrypt")


def downgrade() -> None:
    bind = op.get_bind()
    filas = _leer_contacto(bind)
    with op.batch_alter_table(_TABLE) as batch:
        batch.alter_column(
            "email",
            existing_type=sa.Text(),
            type_=sa.String(length=254),
            existing_nullable=False,
        )
        batch.alter_column(
            "telefono",
            existing_type=sa.Text(),
            type_=sa.String(length=20),
            existing_nullable=True,
        )
    # Reintroducir texto plano es una accion HIGH (ver ADR / plan de migracion).
    _reescribir_contacto(bind, filas, "decrypt")
