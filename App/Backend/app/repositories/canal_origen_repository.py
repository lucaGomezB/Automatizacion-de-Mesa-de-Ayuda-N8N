"""
Repositorio para la entidad CanalOrigen.

Responsabilidad:
    Extiende BaseRepository con las operaciones de resolucion del canal de
    origen referenciado por un incidente. La resolucion opcional (None cuando
    no se especifica canal) se apoya en `get_or_none` heredado.
"""

from app.models.catalog import CanalOrigen
from app.repositories.base import BaseRepository


class CanalOrigenRepository(BaseRepository[CanalOrigen]):
    """Repositorio de acceso a datos para la entidad CanalOrigen."""

    model = CanalOrigen
