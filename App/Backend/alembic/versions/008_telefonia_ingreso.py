"""Migracion 008: tabla de ingreso de telefonia asincronico (c-52, ALTA).

Responsabilidad:
    Aditiva respecto de 001/002/003/004/005/006/007. NO muta las anteriores.

    Crea la tabla `telefonia_ingreso`, que persiste un registro por llamada del
    canal de telefonia con DOBLE REPRESENTACION del transcript:

    - `call_sid` (String(64), NOT NULL, UNIQUE): clave de idempotencia del
      ingreso. El indice unico impide una segunda fila ante un callback repetido.
    - `recording_sid` (String(64), NULL): identificador de la grabacion.
    - `caller_cifrado` (Text, NULL): numero llamante cifrado at-rest (Fernet).
    - `duracion_segundos` (Integer, NULL): duracion informada por Twilio.
    - `transcript_original` (Text, NULL): transcript crudo cifrado at-rest.
    - `descripcion_pseudonimizada` (Text, NULL): unica representacion que cruza
      el borde hacia n8n.
    - `ingresado_en` / `persistido_en` (TIMESTAMPTZ, NULL): sellos temporales.
    - `transcripcion_estado` (String(32), NOT NULL, default 'pendiente').
    - `incidente_id` (Integer, NULL, FK -> incidente.id ON DELETE SET NULL).
    - `error_detalle` (Text, NULL), `provider` (String(50), NULL),
      `model` (String(100), NULL).
    - `created_at` / `updated_at` (TIMESTAMPTZ, NOT NULL): auditoria.

    `EncryptedText` es un TypeDecorator sobre `Text` (ciphertext base64), de modo
    que las columnas cifradas se declaran como `sa.Text()`.

    El `downgrade` dropea la tabla (no hay datos de negocio que restaurar: el
    ingreso se reconstruye a partir de las grabaciones de Twilio).

Revision ID: 008
Revises: 007
Create Date: 2026-09-23

Prerequisito de datos: ninguno (tabla nueva; sin backfill).
"""

import sqlalchemy as sa
from alembic import op

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None

_TABLE = "telefonia_ingreso"
_INDEX_CALL_SID = "ix_telefonia_ingreso_call_sid"
_INDEX_INCIDENTE = "ix_telefonia_ingreso_incidente_id"
_INDEX_CREATED = "ix_telefonia_ingreso_created_at"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("call_sid", sa.String(length=64), nullable=False),
        sa.Column("recording_sid", sa.String(length=64), nullable=True),
        sa.Column("caller_cifrado", sa.Text(), nullable=True),
        sa.Column("duracion_segundos", sa.Integer(), nullable=True),
        sa.Column("transcript_original", sa.Text(), nullable=True),
        sa.Column("descripcion_pseudonimizada", sa.Text(), nullable=True),
        sa.Column("ingresado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("persistido_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "transcripcion_estado",
            sa.String(length=32),
            nullable=False,
            server_default="pendiente",
        ),
        sa.Column("incidente_id", sa.Integer(), nullable=True),
        sa.Column("error_detalle", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["incidente_id"],
            ["incidente.id"],
            ondelete="SET NULL",
        ),
    )
    # Indice UNIQUE: clave de idempotencia por CallSid.
    op.create_index(_INDEX_CALL_SID, _TABLE, ["call_sid"], unique=True)
    op.create_index(_INDEX_INCIDENTE, _TABLE, ["incidente_id"])
    op.create_index(_INDEX_CREATED, _TABLE, ["created_at"])


def downgrade() -> None:
    op.drop_index(_INDEX_CREATED, table_name=_TABLE)
    op.drop_index(_INDEX_INCIDENTE, table_name=_TABLE)
    op.drop_index(_INDEX_CALL_SID, table_name=_TABLE)
    op.drop_table(_TABLE)