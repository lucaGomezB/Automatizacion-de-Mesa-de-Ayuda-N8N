"""Migración 002: doble representación de descripción (Ley 25.326).

Responsabilidad:
    Reemplaza la columna `descripcion` de la tabla `incidente` por dos columnas:

        descripcion_original       — texto crudo con PII, cifrado at-rest con Fernet
                                     (EncryptedText TypeDecorator de SQLAlchemy).
                                     Solo para auditoría y ejercicio de derechos ARCO.

        descripcion_pseudonimizada — texto operativo en claro con etiquetas
                                     [EMAIL]/[TELEFONO]/[HOST]/[PERSONA].
                                     Única representación que consume el pipeline de
                                     clasificación y que expone la API.

    Estrategia (nullable → backfill → not null → drop):
        1. Agregar ambas columnas como nullable.
        2. Backfillear cada fila existente: pseudonimizar el texto y cifrar el original.
        3. Pasar ambas columnas a NOT NULL.
        4. Eliminar la columna `descripcion` vieja.

    El backfill usa batch_alter_table para compatibilidad con SQLite (ALTER COLUMN
    y DROP COLUMN no están soportados nativamente en SQLite sin batch mode).

    PREREQUISITO: PSEUDONYMIZATION_ENCRYPTION_KEY debe estar en el entorno antes
    de ejecutar esta migración. Si falta, el backfill fallará con un error claro.

Revision ID: 002
Revises: 001
Create Date: 2026-06-11
"""

import sqlalchemy as sa
from alembic import op

# Metadatos de revisión
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def _backfill_upgrade(connection) -> None:
    """
    Rellena descripcion_original (cifrada) y descripcion_pseudonimizada (en claro)
    para cada fila existente en la tabla incidente.

    Importa las utilidades del app en tiempo de ejecución de la migración,
    lo cual es el patrón estándar para migraciones de datos en Alembic.
    """
    from app.utils.encryption import EncryptedText
    from app.utils.pseudonymizer import pseudonymize

    # Leer todas las filas con el id y la descripcion original
    rows = connection.execute(
        sa.text("SELECT id, descripcion FROM incidente WHERE descripcion IS NOT NULL")
    ).fetchall()

    if not rows:
        return

    enc = EncryptedText()

    for row_id, descripcion in rows:
        # Pseudonimizar: genera el texto operativo
        resultado = pseudonymize(descripcion, [])
        texto_pseudo = resultado.texto

        # Cifrar el original (EncryptedText.process_bind_param espera un valor en Python)
        original_cifrado = enc.process_bind_param(descripcion, None)

        connection.execute(
            sa.text(
                "UPDATE incidente "
                "SET descripcion_pseudonimizada = :pseudo, descripcion_original = :original "
                "WHERE id = :id"
            ),
            {"pseudo": texto_pseudo, "original": original_cifrado, "id": row_id},
        )


def _backfill_downgrade(connection) -> None:
    """
    Restaura la columna 'descripcion' con el texto original descifrado
    a partir de 'descripcion_original'.

    El downgrade prioriza recuperar el texto original (no la pseudonimizada)
    para no perder datos en un rollback.
    """
    from app.utils.encryption import EncryptedText

    rows = connection.execute(
        sa.text(
            "SELECT id, descripcion_original FROM incidente "
            "WHERE descripcion_original IS NOT NULL"
        )
    ).fetchall()

    if not rows:
        return

    enc = EncryptedText()

    for row_id, original_cifrado in rows:
        # Descifrar el original para restaurarlo en 'descripcion'
        texto_original = enc.process_result_value(original_cifrado, None)

        connection.execute(
            sa.text(
                "UPDATE incidente SET descripcion = :descripcion WHERE id = :id"
            ),
            {"descripcion": texto_original, "id": row_id},
        )


def upgrade() -> None:
    """
    Aplica la migración 002: agrega columnas, backfillea y dropea 'descripcion'.

    Usa batch_alter_table para compatibilidad con SQLite (producción usa PostgreSQL
    pero los tests corren sobre SQLite; batch mode hace la transformación segura
    en ambos motores).
    """
    # ── Paso 1: Agregar las dos columnas nuevas como nullable ─────────────────
    with op.batch_alter_table("incidente", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("descripcion_pseudonimizada", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("descripcion_original", sa.Text(), nullable=True)
        )

    # ── Paso 2: Backfill de filas existentes ─────────────────────────────────
    connection = op.get_bind()
    _backfill_upgrade(connection)

    # ── Paso 3: Cambiar ambas columnas a NOT NULL + drop de 'descripcion' ─────
    # batch_alter_table es necesario para ALTER COLUMN y DROP COLUMN en SQLite
    with op.batch_alter_table("incidente", schema=None) as batch_op:
        batch_op.alter_column(
            "descripcion_pseudonimizada",
            existing_type=sa.Text(),
            nullable=False,
        )
        batch_op.alter_column(
            "descripcion_original",
            existing_type=sa.Text(),
            nullable=False,
        )
        batch_op.drop_column("descripcion")


def downgrade() -> None:
    """
    Revierte la migración 002: restaura 'descripcion' con el texto original
    descifrado y elimina las dos columnas nuevas.

    El downgrade prioriza la recuperación del dato original (texto con PII)
    sobre la pseudonimizada, para no perder información en un rollback.
    El código que corra con el esquema revertido debe ser la versión anterior
    del app (que usa 'descripcion'); coordinar con el despliegue.
    """
    # ── Paso 1: Restaurar la columna 'descripcion' como nullable ──────────────
    with op.batch_alter_table("incidente", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("descripcion", sa.Text(), nullable=True)
        )

    # ── Paso 2: Backfill inverso: descifrar original → descripcion ────────────
    connection = op.get_bind()
    _backfill_downgrade(connection)

    # ── Paso 3: Poner 'descripcion' como NOT NULL + drop de las dos nuevas ────
    with op.batch_alter_table("incidente", schema=None) as batch_op:
        batch_op.alter_column(
            "descripcion",
            existing_type=sa.Text(),
            nullable=False,
        )
        batch_op.drop_column("descripcion_pseudonimizada")
        batch_op.drop_column("descripcion_original")
