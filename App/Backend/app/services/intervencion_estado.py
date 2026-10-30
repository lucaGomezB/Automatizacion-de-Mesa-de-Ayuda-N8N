"""
Estado de la intervencion humana de un log de clasificacion (c-165, ASG-005 y ECM-003).

Responsabilidad:
    Concentra, en un unico lugar, las reglas con las que la metrica backend
    `tasa_intervencion_backend` y el export pseudonimizado para c-167 deciden en que
    estado esta un log. Ambos consumidores usan la MISMA definicion, de modo que el
    numerador de la tasa y las filas exportadas no pueden divergir.

    Este modulo es de la capa de servicios: no abre sesiones ni ejecuta consultas.
    Provee funciones puras (para Python) y re-exporta las condiciones SQL (que se
    definen en `app.models.clasificacion_log`); un test las contrasta fila por fila.

Estados de un log (derivados, sin columna propia ni backfill):
    no_intervenido                     validado_en IS NULL y sector_id_validado IS NULL
    intervenido                        validado_en IS NOT NULL
    intervencion_legada_sin_metadatos  sector_id_validado IS NOT NULL y validado_en IS NULL
                                       (validado antes de la migracion 024)

    Un log LEGADO no se cuenta como intervenido ni como no intervenido: no se le
    inventa un instante ni un origen retroactivos. La metrica y el export lo excluyen
    y declaran cuantos excluyeron.

Cambio de sector:
    `cambio_sector = sector_validado != sector_predicho`, donde un predicho NULL
    (clasificador sin senal) cuenta como cambio. Se evalua con `IS DISTINCT FROM`
    (NULL-safe) para que SQL y Python coincidan.

Utilidades del instante:
    `a_utc` normaliza el inicio declarado por el cliente antes de persistirlo. SQLite
    (la costura de tests) descarta la zona de `DateTime(timezone=True)`: un
    `12:00-03:00` se guardaria como `12:00` ingenuo y la duracion quedaria desfasada.
"""

from datetime import datetime, timezone
from typing import Final

# Las condiciones SQL viven en el modelo (capa mas baja) para que el repositorio de
# estadisticas las use sin importar de `services`; aca se re-exportan junto a la
# funcion pura, de modo que consumidores y tests tengan un unico punto de entrada.
from app.models.clasificacion_log import (
    condicion_cambio_de_sector,
    condicion_intervenido,
    condicion_legado,
    condicion_no_intervenido,
)

__all__ = [
    "ESTADO_INTERVENIDO",
    "ESTADO_LEGADO",
    "ESTADO_NO_INTERVENIDO",
    "a_utc",
    "condicion_cambio_de_sector",
    "condicion_intervenido",
    "condicion_legado",
    "condicion_no_intervenido",
    "estado_intervencion",
    "hubo_cambio_de_sector",
]

#: Estados derivados de un log (valores textuales de la especificacion ASG-005).
ESTADO_NO_INTERVENIDO: Final[str] = "no_intervenido"
ESTADO_INTERVENIDO: Final[str] = "intervenido"
ESTADO_LEGADO: Final[str] = "intervencion_legada_sin_metadatos"


def estado_intervencion(
    *, validado_en: datetime | None, sector_id_validado: int | None
) -> str:
    """
    Clasifica un log en uno de los tres estados a partir de dos columnas.

    `validado_en` manda: si esta presente el log fue intervenido (aunque el sector
    validado se haya anulado despues por `ON DELETE SET NULL` del sector). Sin
    `validado_en`, un sector validado delata una fila previa a la migracion 024.
    """
    if validado_en is not None:
        return ESTADO_INTERVENIDO
    if sector_id_validado is not None:
        return ESTADO_LEGADO
    return ESTADO_NO_INTERVENIDO


def hubo_cambio_de_sector(
    sector_id_predicho: int | None, sector_id_validado: int | None
) -> bool:
    """
    Indica si la intervencion cambio el sector respecto del predicho.

    Un predicho nulo cuenta como cambio frente a cualquier sector validado; dos
    nulos no son un cambio. Equivale a `IS DISTINCT FROM` en SQL.
    """
    return sector_id_predicho != sector_id_validado


def a_utc(instante: datetime | None) -> datetime | None:
    """
    Normaliza un instante a UTC con zona explicita.

    - `None` se devuelve tal cual (el inicio es opcional).
    - Un instante con zona se convierte a UTC.
    - Un instante SIN zona se interpreta como UTC: las columnas del proyecto almacenan
      UTC y SQLite devuelve los valores sin zona.

    Raises:
        TypeError: Si el valor no es un `datetime` (ni `None`).
    """
    if instante is None:
        return None
    if not isinstance(instante, datetime):
        raise TypeError(f"Se esperaba un datetime, no {type(instante).__name__}.")
    if instante.tzinfo is None:
        return instante.replace(tzinfo=timezone.utc)
    return instante.astimezone(timezone.utc)
