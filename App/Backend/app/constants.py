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

#: Nombre canonico del canal de telefonia en el catalogo `canal_origen` (migracion
#: 001). c-72: reconocer el canal por nombre evita acoplarse a su ID numerico. La
#: clasificacion telefonica es propiedad del backend sobre la descripcion
#: pseudonimizada; el nombre acentuado debe coincidir EXACTO con el seed.
CANAL_TELEFONIA: Final[str] = "llamada telefónica"

#: Nombre canonico del canal de correo en el catalogo `canal_origen` (migracion
#: 001). c-82: reconocer el canal de correo por nombre evita acoplarse a su ID
#: numerico al resolver el reportante por el email del remitente (VIS-004).
CANAL_CORREO: Final[str] = "correo electrónico"

#: Clave de version del clasificador hibrido para el cache de evaluacion (C-34).
#: Vive en este modulo liviano para que el runner de evaluacion la lea sin
#: importar app.classifiers (que arrastra app.core.database -> get_settings) y
#: asi un cache hit no exija credenciales (W-3). HybridClassifier la reutiliza
#: como unica fuente de verdad.
#: c-74: sube a hybrid-v3 porque el cortocircuito pasa de `confianza` al score
#: de correctitud (ordena la correctitud esperada; NO es una probabilidad
#: calibrada); el cambio altera clasificaciones e invalida el cache de
#: predicciones de la corrida previa (hybrid-v2).
HYBRID_CACHE_VERSION: Final[str] = "hybrid-v3"

#: Vocabulario cerrado del ORIGEN de una intervencion humana sobre un log de
#: clasificacion (c-165, ASG-005). Lo deriva SIEMPRE el backend; el cliente nunca
#: lo declara. Se valida en la capa de aplicacion (la base no tiene CHECK).
ORIGEN_GATE: Final[str] = "gate"
ORIGEN_MUESTREO: Final[str] = "muestreo"
ORIGEN_REDERIVACION: Final[str] = "rederivacion"
#: Reservado: sin escritor en c-165 (se declara y se desglosa, siempre en cero).
ORIGEN_COMPLETADO_MANUAL: Final[str] = "completado_manual"

#: Los cuatro valores, en el orden del desglose de la metrica y del export.
ORIGENES_INTERVENCION: Final[tuple[str, ...]] = (
    ORIGEN_GATE,
    ORIGEN_MUESTREO,
    ORIGEN_REDERIVACION,
    ORIGEN_COMPLETADO_MANUAL,
)


def es_sector_canonico(nombre: object) -> bool:
    """
    Indica si un valor pertenece al vocabulario canonico de sectores.

    La comparacion es exacta (case-sensitive y sin normalizacion Unicode): las
    variantes con tilde, casing distinto o espacios no son validas.
    """
    return isinstance(nombre, str) and nombre in _SECTORES_CANONICOS_SET


def es_canal_telefonia(nombre: object) -> bool:
    """
    Indica si el nombre del canal de origen corresponde a telefonia (c-72).

    La comparacion es exacta contra el nombre sembrado en la migracion 001
    ("llamada telefónica", con tilde). Un canal ausente (None) no es telefonia.
    """
    return nombre == CANAL_TELEFONIA


def es_canal_correo(nombre: object) -> bool:
    """Indica si el nombre del canal de origen corresponde a correo (c-82)."""
    return nombre == CANAL_CORREO


__all__ = [
    "SECTORES_CANONICOS",
    "HYBRID_CACHE_VERSION",
    "ORIGEN_GATE",
    "ORIGEN_MUESTREO",
    "ORIGEN_REDERIVACION",
    "ORIGEN_COMPLETADO_MANUAL",
    "ORIGENES_INTERVENCION",
    "CANAL_TELEFONIA",
    "CANAL_CORREO",
    "es_sector_canonico",
    "es_canal_telefonia",
    "es_canal_correo",
]
