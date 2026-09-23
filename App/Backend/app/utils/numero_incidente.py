"""
Derivacion del numero de incidente canonico y legible (C-53, OQ1 / design D1).

Punto UNICO de derivacion del numero que se muestra al usuario final. Hoy el numero
canonico es el PK `id` del incidente, por lo que esta funcion devuelve `str(id)`.

El prefijo de negocio futuro (`INC-{id:06d}`) se agrega en este unico lugar: ningun
contrato (backend ni workflow) debe construir el numero por su cuenta.
"""


def formatear_numero_incidente(incidente_id: int) -> str:
    """
    Devuelve el numero de incidente normalizado como string.

    Args:
        incidente_id: identificador persistido del incidente (PK `id`).

    Returns:
        El numero canonico como cadena. Hoy es `str(incidente_id)`; el prefijo de
        negocio se incorporaria aqui sin tocar los contratos consumidores.
    """
    return str(incidente_id)
