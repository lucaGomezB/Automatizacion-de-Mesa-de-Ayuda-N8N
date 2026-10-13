"""Migracion 017: rediseno RBAC (c-82).

Responsabilidad (append-only respecto de 016):
    1. Agrega a `incidente` la columna nullable `reportante_empleado_id`
       (FK -> `directorio_empleado.id`, ON DELETE SET NULL) con indice, base del
       alcance PROPIO del rol `usuario_final` (VIS-003).
    2. Backfill ANTES del CHECK nuevo: `UPDATE directorio_empleado SET
       rol='mesa_de_ayuda' WHERE rol='operador'` (OQ-2). El mapeo NO es
       reversible en el downgrade.
    3. Recrea el CHECK `ck_directorio_empleado_rol` con los TRES valores del
       vocabulario (`usuario_final`, `mesa_de_ayuda`, `administrador_directorio`);
       `operador` deja de existir (DIR-003).
    4. Inserta, condicional e idempotentemente, el empleado SINTETICO
       `administrador_directorio` de la cuenta `admin` sembrada por la migracion
       003 (OQ-3 / D9), para que su alcance sea GLOBAL y no VACIO. Sin PII real:
       legajo determinista `SYS-ADMIN`, email sintetico del dominio reservado
       `sys-admin@example.test` (el esquema exige email NOT NULL/UNIQUE) y
       `telefono` nulo. Con SQL crudo, sin importar modelos.

    `batch_alter_table` es portable entre PostgreSQL (ALTER directo) y SQLite
    (recreacion de tabla), de modo que la suite de migraciones corre sobre SQLite
    en archivo.

    `downgrade`: recrea el CHECK de cuatro valores, elimina la columna/index del
    reportante y elimina el empleado sintetico de `admin`. NO re-marca filas.

Revision ID: 017
Revises: 016
Create Date: 2026-10-13
"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None

_INCIDENTE = "incidente"
_DIRECTORIO = "directorio_empleado"
_CHECK = "ck_directorio_empleado_rol"
_INDEX_REPORTANTE = "ix_incidente_reportante_empleado_id"

# Vocabulario nuevo (tres valores) y previo (cuatro valores) para rollback.
_ROL_CHECK_TRES = (
    "rol IN ('usuario_final', 'mesa_de_ayuda', 'administrador_directorio')"
)
_ROL_CHECK_CUATRO = (
    "rol IN ('usuario_final', 'operador', 'administrador_directorio', 'mesa_de_ayuda')"
)

_ADMIN_LEGAJO = "SYS-ADMIN"
_ADMIN_EMAIL = "sys-admin@example.test"

# Naming convention para la recreacion batch de `incidente`: sus FK de la
# migracion 001 no tienen nombre y la copia-and-move de SQLite las necesita.
_NAMING = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}


def _insertar_admin_sintetico(bind) -> None:
    """
    Inserta condicional e idempotentemente el empleado sintetico de `admin`.

    Solo si existe el usuario `admin` y NO tiene un empleado vinculado
    (`directorio_empleado.user_id`). Emplea SQL crudo (sin importar modelos) y
    datos SIN PII real (dominio reservado `.test`).
    """
    fila = bind.execute(
        sa.text("SELECT id FROM users WHERE username = 'admin'")
    ).fetchone()
    if fila is None:
        return
    admin_user_id = fila[0]

    ya_vinculado = bind.execute(
        sa.text(
            f"SELECT 1 FROM {_DIRECTORIO} WHERE user_id = :uid "
            "OR legajo = :legajo"
        ),
        {"uid": admin_user_id, "legajo": _ADMIN_LEGAJO},
    ).fetchone()
    if ya_vinculado is not None:
        return

    ahora = datetime.now(timezone.utc)
    bind.execute(
        sa.text(
            f"INSERT INTO {_DIRECTORIO} "
            "(legajo, nombre, email, telefono, sector_id, rol, activo, user_id, "
            "created_at, updated_at) "
            "VALUES (:legajo, :nombre, :email, NULL, NULL, "
            "'administrador_directorio', :activo, :uid, :now, :now)"
        ),
        {
            "legajo": _ADMIN_LEGAJO,
            "nombre": "Administrador del Sistema",
            "email": _ADMIN_EMAIL,
            "activo": True,
            "uid": admin_user_id,
            "now": ahora,
        },
    )


def upgrade() -> None:
    """Columna de reportante + backfill + CHECK nuevo + empleado sintetico admin."""
    bind = op.get_bind()

    # 1. Backfill ANTES del CHECK nuevo: las filas legacy `operador` migran a
    #    `mesa_de_ayuda` (GLOBAL), que absorbe semanticamente al operador (OQ-2).
    bind.execute(
        sa.text(
            f"UPDATE {_DIRECTORIO} SET rol = 'mesa_de_ayuda' WHERE rol = 'operador'"
        )
    )

    # 2. CHECK nuevo (tres valores).
    with op.batch_alter_table(_DIRECTORIO) as batch_op:
        batch_op.drop_constraint(_CHECK, type_="check")
        batch_op.create_check_constraint(_CHECK, _ROL_CHECK_TRES)

    # 3. Columna + FK + indice del reportante en `incidente`. Se usa batch mode
    #    (SQLite no soporta ALTER de constraints) CON una naming convention: las
    #    FK de `incidente` creadas en la migracion 001 no tienen nombre, y la
    #    recreacion de la tabla necesita nombrarlas.
    with op.batch_alter_table(_INCIDENTE, naming_convention=_NAMING) as batch_op:
        batch_op.add_column(
            sa.Column("reportante_empleado_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_incidente_reportante_empleado",
            "directorio_empleado",
            ["reportante_empleado_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(_INDEX_REPORTANTE, ["reportante_empleado_id"])

    # 4. Empleado sintetico de la cuenta `admin` (condicional e idempotente).
    _insertar_admin_sintetico(bind)


def downgrade() -> None:
    """Restaura el CHECK de cuatro valores, quita la columna y el admin sintetico."""
    bind = op.get_bind()

    # Elimina el empleado sintetico de `admin` (D9).
    bind.execute(
        sa.text(f"DELETE FROM {_DIRECTORIO} WHERE legajo = :legajo"),
        {"legajo": _ADMIN_LEGAJO},
    )

    # Restaura el CHECK previo de cuatro valores (NO re-marca filas migradas).
    with op.batch_alter_table(_DIRECTORIO) as batch_op:
        batch_op.drop_constraint(_CHECK, type_="check")
        batch_op.create_check_constraint(_CHECK, _ROL_CHECK_CUATRO)

    # Elimina la columna/index del reportante.
    with op.batch_alter_table(_INCIDENTE, naming_convention=_NAMING) as batch_op:
        batch_op.drop_index(_INDEX_REPORTANTE)
        batch_op.drop_constraint("fk_incidente_reportante_empleado", type_="foreignkey")
        batch_op.drop_column("reportante_empleado_id")
