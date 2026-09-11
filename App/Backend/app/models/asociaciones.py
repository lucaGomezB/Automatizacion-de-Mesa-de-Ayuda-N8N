"""
Tablas de union normalizadas para los sectores adicionales (C-27).

Responsabilidad:
    Modela las relaciones N-a-N entre las entidades del dominio y el catalogo
    `sector`, para persistir los sectores adicionales:

        incidente_sector_adicional    -> sectores adicionales del incidente.
        clasificacion_sector_predicho -> sectores adicionales predichos por el
                                         clasificador para un registro de log.
        clasificacion_sector_validado -> sectores adicionales validados por el
                                         operador humano.

    En las tres tablas el sector "principal" no se duplica aqui: vive en la FK
    escalar correspondiente (incidente.sector_id, clasificacion_log.sector_id_predicho,
    clasificacion_log.sector_id_validado). Estas tablas contienen solo el resto
    del conjunto.

Decision (design.md D1):
    Se usan tablas de union (no JSONB) para preservar integridad referencial
    contra el catalogo y permitir agregaciones con JOIN.
"""

from sqlalchemy import Column, ForeignKey, Integer, Table

from app.models.base import Base

# Sectores adicionales del incidente (N-a-N).
incidente_sector_adicional = Table(
    "incidente_sector_adicional",
    Base.metadata,
    Column(
        "incidente_id",
        Integer,
        ForeignKey("incidente.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "sector_id",
        Integer,
        ForeignKey("sector.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)

# Sectores adicionales predichos por el clasificador.
clasificacion_sector_predicho = Table(
    "clasificacion_sector_predicho",
    Base.metadata,
    Column(
        "clasificacion_log_id",
        Integer,
        ForeignKey("clasificacion_log.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "sector_id",
        Integer,
        ForeignKey("sector.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)

# Sectores adicionales validados manualmente por el operador.
clasificacion_sector_validado = Table(
    "clasificacion_sector_validado",
    Base.metadata,
    Column(
        "clasificacion_log_id",
        Integer,
        ForeignKey("clasificacion_log.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "sector_id",
        Integer,
        ForeignKey("sector.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)

__all__ = [
    "incidente_sector_adicional",
    "clasificacion_sector_predicho",
    "clasificacion_sector_validado",
]
