"""Migración inicial: creación y población de tablas de catálogo.

Responsabilidad:
    Crea las cinco tablas del sistema (sector, estado, canal_origen,
    incidente, clasificacion_log) e inicializa los datos de referencia
    en las tres tablas de catálogo.  Estos datos son prerrequisito para
    el correcto funcionamiento de la API:
        - El servicio de incidentes resuelve el estado "nuevo" de esta tabla.
        - El clasificador resuelve las categorías predichas a registros de sector.
        - El canal de origen identifica el medio de ingreso del incidente.

    Esta migración debe ejecutarse antes de que la API comience a recibir
    solicitudes. En el docker-compose.yml, el comando de inicio del servicio
    'api' ejecuta "alembic upgrade head" antes de levantar uvicorn.

Valores sembrados:
    sector:       Sistemas | Operaciones | Soporte Técnico
    estado:       nuevo | en proceso | en espera | resuelto | cerrado
    canal_origen: correo electrónico | formulario web | llamada telefónica

Revision ID: 001
Revises:
Create Date: 2026-03-01
"""

import sqlalchemy as sa
from alembic import op
from datetime import datetime, timezone

# Metadatos de revisión requeridos por Alembic para gestionar el grafo de migraciones
revision = "001"
down_revision = None       # Primera migración: no tiene predecesora
branch_labels = None
depends_on = None

# Timestamp fijo para todos los registros de seed, garantizando reproducibilidad
NOW = datetime.now(timezone.utc)


def upgrade() -> None:
    """
    Aplica la migración: crea las cinco tablas y siembra los catálogos.

    Orden de creación respeta dependencias de FK:
        1. sector, estado, canal_origen  (sin dependencias externas)
        2. incidente                     (FK → sector, estado, canal_origen)
        3. clasificacion_log             (FK → incidente, sector)

    Los índices compuestos de incidente se crean con op.create_index()
    ya que op.create_table() no acepta sa.Index directamente.
    """

    # ── 1. Tabla sector ───────────────────────────────────────────────────────
    op.create_table(
        "sector",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", name="uq_sector_nombre"),
    )
    op.create_index("ix_sector_created_at", "sector", ["created_at"])

    # ── 2. Tabla estado ───────────────────────────────────────────────────────
    op.create_table(
        "estado",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(50), nullable=False),
        sa.Column("descripcion", sa.String(300), nullable=True),
        sa.Column("es_terminal", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", name="uq_estado_nombre"),
    )
    op.create_index("ix_estado_created_at", "estado", ["created_at"])

    # ── 3. Tabla canal_origen ─────────────────────────────────────────────────
    op.create_table(
        "canal_origen",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.String(300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", name="uq_canal_origen_nombre"),
    )
    op.create_index("ix_canal_origen_created_at", "canal_origen", ["created_at"])

    # ── 4. Tabla incidente (FK → sector, estado, canal_origen) ────────────────
    op.create_table(
        "incidente",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("prioridad", sa.String(20), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=True),
        sa.Column("estado_id", sa.Integer(), nullable=False),
        sa.Column("canal_origen_id", sa.Integer(), nullable=True),
        sa.Column("requiere_revision_humana", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["sector_id"], ["sector.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["estado_id"], ["estado.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["canal_origen_id"], ["canal_origen.id"], ondelete="SET NULL"
        ),
    )
    # Índices simples sobre FK (optimizan JOIN y filtros individuales)
    op.create_index("ix_incidente_sector_id", "incidente", ["sector_id"])
    op.create_index("ix_incidente_estado_id", "incidente", ["estado_id"])
    op.create_index("ix_incidente_created_at", "incidente", ["created_at"])
    # Índices compuestos definidos en __table_args__ del modelo ORM
    op.create_index(
        "ix_incidente_created_sector", "incidente", ["created_at", "sector_id"]
    )
    op.create_index(
        "ix_incidente_estado_created", "incidente", ["estado_id", "created_at"]
    )

    # ── 5. Tabla clasificacion_log (FK → incidente, sector) ───────────────────
    op.create_table(
        "clasificacion_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("incidente_id", sa.Integer(), nullable=False),
        sa.Column("sector_id_predicho", sa.Integer(), nullable=True),
        sa.Column("confianza", sa.Numeric(5, 4), nullable=False),
        sa.Column("etapa", sa.String(30), nullable=False),
        sa.Column("requiere_revision_humana", sa.Boolean(), nullable=False),
        sa.Column("respuesta_raw", sa.Text(), nullable=True),
        sa.Column("sector_id_validado", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["incidente_id"], ["incidente.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["sector_id_predicho"], ["sector.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["sector_id_validado"], ["sector.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_clasificacion_log_incidente_id", "clasificacion_log", ["incidente_id"]
    )
    op.create_index(
        "ix_clasificacion_log_created_at", "clasificacion_log", ["created_at"]
    )

    # ── Seed: tabla sector ────────────────────────────────────────────────────
    # Los tres sectores corresponden exactamente a las categorías del clasificador
    # y al prompt documentado en docs/prompt_gemini.txt
    op.bulk_insert(
        sa.table(
            "sector",
            sa.column("nombre", sa.String),
            sa.column("descripcion", sa.String),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "nombre": "Sistemas",
                "descripcion": "Infraestructura, redes, servidores, bases de datos, ciberseguridad",
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "Operaciones",
                "descripcion": "Procesos compartidos, gestión de servicios, planificación, continuidad operativa",
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "Soporte Técnico",
                "descripcion": "Equipamiento de usuarios, periféricos, software cliente, asistencia remota",
                "created_at": NOW,
                "updated_at": NOW,
            },
        ],
    )

    # ── Seed: tabla estado ────────────────────────────────────────────────────
    # Los cinco estados modelan el ciclo de vida completo de un ticket.
    # Solo "cerrado" es terminal (es_terminal=True).
    op.bulk_insert(
        sa.table(
            "estado",
            sa.column("nombre", sa.String),
            sa.column("descripcion", sa.String),
            sa.column("es_terminal", sa.Boolean),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "nombre": "nuevo",
                "descripcion": "Incidente recibido, sin asignar",
                "es_terminal": False,
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "en proceso",
                "descripcion": "Asignado y en atención por el sector responsable",
                "es_terminal": False,
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "en espera",
                "descripcion": "Bloqueado esperando respuesta o información del usuario",
                "es_terminal": False,
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "resuelto",
                "descripcion": "Solución aplicada, pendiente de confirmación del usuario",
                "es_terminal": False,
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "cerrado",
                "descripcion": "Finalizado. No admite más modificaciones.",
                "es_terminal": True,  # Estado terminal del ciclo de vida
                "created_at": NOW,
                "updated_at": NOW,
            },
        ],
    )

    # ── Seed: tabla canal_origen ──────────────────────────────────────────────
    # Los tres canales corresponden a los medios de ingreso del flujo N8N:
    # Outlook (email), API directa (formulario web) y Twilio (llamada).
    op.bulk_insert(
        sa.table(
            "canal_origen",
            sa.column("nombre", sa.String),
            sa.column("descripcion", sa.String),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "nombre": "correo electrónico",
                "descripcion": "Incidente recibido vía trigger de Microsoft Outlook en N8N",
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "formulario web",
                "descripcion": "Incidente ingresado directamente por la API REST o formulario web",
                "created_at": NOW,
                "updated_at": NOW,
            },
            {
                "nombre": "llamada telefónica",
                "descripcion": "Incidente recibido vía transcripción de llamada de Twilio en N8N",
                "created_at": NOW,
                "updated_at": NOW,
            },
        ],
    )


def downgrade() -> None:
    """
    Revierte la migración: elimina las cinco tablas en orden inverso a las FK.

    El orden respeta las dependencias de clave foránea: primero se eliminan
    las tablas hijas antes que las tablas padre que referencian.

        clasificacion_log  (FK → incidente, sector)
        incidente          (FK → sector, estado, canal_origen)
        canal_origen       (sin hijos)
        estado             (sin hijos)
        sector             (sin hijos)
    """
    op.drop_table("clasificacion_log")
    op.drop_table("incidente")
    op.drop_table("canal_origen")
    op.drop_table("estado")
    op.drop_table("sector")
