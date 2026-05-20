"""Migración inicial: creación y población de tablas de catálogo.

Responsabilidad:
    Crea e inicializa los datos de referencia en las tres tablas de catálogo
    del sistema: sector, estado y canal_origen. Estos datos son prerrequisito
    para el correcto funcionamiento de la API, dado que:
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
    Aplica la migración: inserta los registros de catálogo en las tres tablas.

    Se utiliza bulk_insert para insertar todos los registros en una sola
    sentencia SQL por tabla, optimizando el tiempo de ejecución del seed.
    Los timestamps created_at y updated_at son iguales en la creación inicial.
    """

    # ── Tabla sector ──────────────────────────────────────────────────────────
    # Los tres sectores corresponden exactamente a las categorías del clasificador
    # y al prompt documentado en docs/prompt_gemini.txt
    op.bulk_insert(
        sa.table(
            "sector",
            sa.column("nombre", sa.String),
            sa.column("descripcion", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
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

    # ── Tabla estado ──────────────────────────────────────────────────────────
    # Los cinco estados modelan el ciclo de vida completo de un ticket
    # en una mesa de ayuda. Solo "cerrado" es terminal (es_terminal=True).
    op.bulk_insert(
        sa.table(
            "estado",
            sa.column("nombre", sa.String),
            sa.column("descripcion", sa.String),
            sa.column("es_terminal", sa.Boolean),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
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

    # ── Tabla canal_origen ────────────────────────────────────────────────────
    # Los tres canales corresponden a los medios de ingreso del flujo N8N:
    # Outlook (email), API directa (formulario web) y Twilio (llamada).
    op.bulk_insert(
        sa.table(
            "canal_origen",
            sa.column("nombre", sa.String),
            sa.column("descripcion", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
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
    Revierte la migración: elimina todos los registros de catálogo.

    El orden de eliminación respeta las restricciones de clave foránea:
    primero se eliminan los catálogos que no son referenciados por otros,
    aunque en este caso las tres tablas son independientes entre sí.
    """
    op.execute("DELETE FROM canal_origen")
    op.execute("DELETE FROM estado")
    op.execute("DELETE FROM sector")
