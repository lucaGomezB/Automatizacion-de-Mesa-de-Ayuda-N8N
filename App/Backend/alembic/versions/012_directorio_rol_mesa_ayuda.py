"""Migracion 012: `mesa_de_ayuda` en el vocabulario de `directorio_empleado.rol` (c-60).

Responsabilidad:
    Append-only respecto de 011 (que ya fue publicada por c-70). Recrea el
    CHECK `ck_directorio_empleado_rol` para sumar el cuarto valor del
    vocabulario, `mesa_de_ayuda`, que identifica al revisor transversal de la
    cola de revision (sin sector, igual que `administrador_directorio`).

    No muta ninguna otra tabla ni siembra datos. La recreacion se hace en modo
    batch (`batch_alter_table`), que en PostgreSQL emite el ALTER directo y en
    SQLite recrea la tabla: esto mantiene la migracion portable para la suite
    de migraciones, que corre sobre SQLite en archivo temporal.

    El `downgrade` restaura el CHECK de tres valores. Falla si existieran filas
    con rol `mesa_de_ayuda` (comportamiento documentado y aceptable en rollback
    sin datos reales: las filas serian recargables).

Revision ID: 012
Revises: 011
Create Date: 2026-10-06

Prerequisito de datos: ninguno (no hay backfill; el vocabulario solo se amplia).
"""

from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None

_TABLE = "directorio_empleado"
_CHECK = "ck_directorio_empleado_rol"

# Vocabulario nuevo (cuatro valores) y previo (tres valores) para rollback.
_ROL_CHECK_CUATRO = (
    "rol IN ('usuario_final', 'operador', 'administrador_directorio', 'mesa_de_ayuda')"
)
_ROL_CHECK_TRES = "rol IN ('usuario_final', 'operador', 'administrador_directorio')"


def upgrade() -> None:
    """Amplia el CHECK de `rol` con el cuarto valor `mesa_de_ayuda`."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.drop_constraint(_CHECK, type_="check")
        batch_op.create_check_constraint(_CHECK, _ROL_CHECK_CUATRO)


def downgrade() -> None:
    """Restaura el CHECK de tres valores (previo a c-60)."""
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.drop_constraint(_CHECK, type_="check")
        batch_op.create_check_constraint(_CHECK, _ROL_CHECK_TRES)