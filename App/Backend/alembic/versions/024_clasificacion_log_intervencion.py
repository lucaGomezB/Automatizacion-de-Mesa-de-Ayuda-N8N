"""Migracion 024: metadatos de intervencion humana en `clasificacion_log` (c-165, ASG-005).

Responsabilidad (aditiva respecto de 023; checkpoint 2.1 aprobado el 2026-10-30):
    Agrega a `clasificacion_log` las cuatro columnas que registran cada
    intervencion humana sobre una clasificacion, todas NULLABLE y SIN default:
        - `validado_por_empleado_id` (INTEGER): actor de la ultima intervencion.
          FK nombrada `fk_clasificacion_log_validado_por_directorio_empleado` a
          `directorio_empleado.id` con `ON DELETE SET NULL` (la purga por
          retencion DIR-007 deja el actor en NULL sin tocar el log), indexada.
          NULL tambien cuando la cuenta no tiene empleado vinculado.
        - `intervencion_inicio_en` (TIMESTAMPTZ): inicio declarado por el cliente
          al abrir el dialogo de validacion; NULL si no se envio o en la
          rederivacion.
        - `validado_en` (TIMESTAMPTZ): instante del servidor en que se registro la
          intervencion, distinto de `created_at`.
        - `origen_intervencion` (VARCHAR(20)): `gate`, `muestreo`, `rederivacion` o
          `completado_manual` (reservado, sin escritor). Sin CHECK: ampliar el
          vocabulario no debe exigir otra migracion; se valida en la aplicacion.

    NO hay backfill. Una fila ya validada antes de esta revision queda con
    `validado_en` NULL y se clasifica como `intervencion_legada_sin_metadatos`:
    inventar un instante o un origen retroactivos seria fabricar registro primario.
    El delta antes/despues se reconstruye desde las columnas predicho/validado que
    ya existen, por lo que no hacen falta columnas para eso.

    Usa `batch_alter_table` (portable a SQLite, que recrea la tabla por
    copy-and-move) y, como la 019, crea el indice del actor aparte. El `downgrade`
    retira indice, FK y columnas sin tocar las filas existentes.

Rollback operativo: primero revertir el codigo de aplicacion (el codigo previo
ignora columnas extra) y despues `alembic downgrade 023`. Nunca bajar el esquema
antes de revertir el codigo.

Revision ID: 024
Revises: 023
Create Date: 2026-10-30
"""

import sqlalchemy as sa
from alembic import op

revision = "024"
down_revision = "023"
branch_labels = None
depends_on = None

_TABLA = "clasificacion_log"
_FK_ACTOR = "fk_clasificacion_log_validado_por_directorio_empleado"
_INDICE_ACTOR = "ix_clasificacion_log_validado_por_empleado_id"


def upgrade() -> None:
    """Agrega las cuatro columnas de intervencion (nullable) y el indice del actor."""
    with op.batch_alter_table(_TABLA) as batch_op:
        batch_op.add_column(
            sa.Column(
                "validado_por_empleado_id",
                sa.Integer(),
                sa.ForeignKey(
                    "directorio_empleado.id",
                    ondelete="SET NULL",
                    name=_FK_ACTOR,
                ),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column("intervencion_inicio_en", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("validado_en", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("origen_intervencion", sa.String(length=20), nullable=True)
        )
    op.create_index(_INDICE_ACTOR, _TABLA, ["validado_por_empleado_id"])


def downgrade() -> None:
    """Elimina el indice, la FK y las cuatro columnas (esquema previo, filas intactas)."""
    op.drop_index(_INDICE_ACTOR, table_name=_TABLA)
    with op.batch_alter_table(_TABLA) as batch_op:
        batch_op.drop_column("origen_intervencion")
        batch_op.drop_column("validado_en")
        batch_op.drop_column("intervencion_inicio_en")
        batch_op.drop_column("validado_por_empleado_id")
