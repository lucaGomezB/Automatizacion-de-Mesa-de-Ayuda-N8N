"""
Utilidad de paginación genérica para respuestas de listado.

Responsabilidad:
    Provee el schema genérico PaginatedResponse[T] que puede envolver
    cualquier tipo de item en una respuesta paginada estandarizada.
    El uso de Generic[T] permite reutilizar este schema con cualquier
    entidad del sistema sin duplicar código.

    La propiedad has_more permite a los clientes de la API determinar
    si existen más páginas disponibles sin necesidad de calcular si
    offset + limit alcanza el total, simplificando la lógica de paginación
    en los clientes (interfaces web, N8N, scripts de evaluación).
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

# TypeVar sin restricción: PaginatedResponse puede envolver cualquier tipo
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Envelope genérico para respuestas paginadas de la API.

    Estandariza el formato de cualquier endpoint de listado, proveyendo
    siempre los mismos metadatos de paginación independientemente del
    tipo de recurso. Los campos total, limit y offset permiten a los
    clientes calcular el número de páginas y navegar entre ellas.

    Atributos:
        items:  Lista de items de la página actual.
        total:  Cantidad total de registros que cumplen los filtros aplicados.
        limit:  Tamaño de página utilizado en esta consulta.
        offset: Posición de inicio de la página actual.
    """

    items: list[T]
    total: int     # Total de registros disponibles (no solo en esta página)
    limit: int     # Cantidad de items solicitados por página
    offset: int    # Desplazamiento de la página actual

    @property
    def has_more(self) -> bool:
        """
        Indica si existen más registros después de la página actual.

        Permite a los clientes implementar paginación infinita o scroll
        continuo sin necesidad de calcular el total de páginas:
            if response.has_more:
                offset += limit

        Returns:
            True si hay al menos un registro más allá del rango actual.
        """
        return self.offset + self.limit < self.total
