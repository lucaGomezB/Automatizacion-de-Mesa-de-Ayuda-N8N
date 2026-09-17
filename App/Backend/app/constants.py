"""
Constantes canonicas compartidas del backend.

Responsabilidad:
    Centraliza el vocabulario de dominio que debe ser consistente entre el
    clasificador determinista, Gemini, el pseudonimizador, los schemas y la
    persistencia. Evita la duplicacion de listas de sectores en varios modulos.

Vocabulario canonico (C-27, decision aprobada):
    Los cinco strings son EXACTOS, case-sensitive y SIN tildes. `Operaciones`
    se elimina del dominio y `Sistemas` se mantiene como categoria propia.
"""

from typing import Final

#: Conjunto canonico de sectores, en el orden de presentacion acordado.
SECTORES_CANONICOS: Final[tuple[str, ...]] = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)

#: Vista de conjunto para validaciones O(1).
_SECTORES_CANONICOS_SET: Final[frozenset[str]] = frozenset(SECTORES_CANONICOS)

#: Clave de version del clasificador hibrido para el cache de evaluacion (C-34).
#: Vive en este modulo liviano para que el runner de evaluacion la lea sin
#: importar app.classifiers (que arrastra app.core.database -> get_settings) y
#: asi un cache hit no exija credenciales (W-3). HybridClassifier la reutiliza
#: como unica fuente de verdad.
HYBRID_CACHE_VERSION: Final[str] = "hybrid-v1"


def es_sector_canonico(nombre: object) -> bool:
    """
    Indica si un valor pertenece al vocabulario canonico de sectores.

    La comparacion es exacta (case-sensitive y sin normalizacion Unicode): las
    variantes con tilde, casing distinto o espacios no son validas.
    """
    return isinstance(nombre, str) and nombre in _SECTORES_CANONICOS_SET


__all__ = ["SECTORES_CANONICOS", "HYBRID_CACHE_VERSION", "es_sector_canonico"]
