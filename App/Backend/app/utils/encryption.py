"""
Módulo de cifrado at-rest para datos personales — Ley 25.326.

Responsabilidad:
    Provee el TypeDecorator de SQLAlchemy `EncryptedText` que cifra y descifra
    de forma transparente los valores de columna usando Fernet (biblioteca
    `cryptography`). Diseñado para la columna `descripcion_original` del modelo
    `Incidente`, que almacena PII protegida.

    El cifrado ocurre en `process_bind_param` (Python → DB) y el descifrado en
    `process_result_value` (DB → Python), de manera transparente para el ORM.
    El ciphertext resultante es texto base64 URL-safe almacenado como `Text`,
    compatible con PostgreSQL (producción) y SQLite (tests).

Clave:
    La clave Fernet se lee de `settings.pseudonymization_encryption_key`.
    Se resuelve lazily (en el primer acceso) para no romper importaciones en
    contextos sin clave configurada. Ver `_get_fernet()`.

    Generar una clave con:
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Referencias:
    design.md § Decisión 4
    tasks.md  § 7
"""

from cryptography.fernet import Fernet, MultiFernet
from sqlalchemy import Text, TypeDecorator

from app.config.settings import get_settings

# Instancia MultiFernet con inicialización lazy (None hasta el primer uso).
# Esto evita que la importación del módulo falle en entornos sin clave configurada.
# `_fernet_key` retiene el CONJUNTO de claves con el que se construyó la
# instancia: si cambia la activa O la anterior (rotación, c-63c), el cache se
# invalida y se reconstruye (design.md D-C3).
_fernet_instance: MultiFernet | None = None
_fernet_key: tuple[str, str | None] | None = None


def _as_key_str(value: object) -> str | None:
    """Normaliza una clave configurada a str; vacio o no textual -> None."""
    if isinstance(value, bytes):
        value = value.decode("ascii")
    if isinstance(value, str) and value:
        return value
    return None


def _configured_keys() -> tuple[str, str | None]:
    """Lee el par de claves del entorno: (activa, anterior o None).

    La activa es OBLIGATORIA (`pseudonymization_encryption_key`); la anterior
    (`pseudonymization_encryption_key_previous`) es opcional y vacia por defecto,
    preservando el comportamiento actual (una sola clave).
    """
    settings = get_settings()
    active_raw = settings.pseudonymization_encryption_key
    active = (
        active_raw.decode("ascii") if isinstance(active_raw, bytes) else active_raw
    )
    previous = _as_key_str(
        getattr(settings, "pseudonymization_encryption_key_previous", "")
    )
    return active, previous


def _get_fernet() -> MultiFernet:
    """
    Retorna la instancia MultiFernet, construyéndola la primera vez o cuando el
    CONJUNTO de claves configurado cambia.

    El conjunto se lee en cada llamada: `[activa, anterior?]`. Al cifrar,
    MultiFernet usa siempre la primera clave (la activa); al descifrar, prueba
    las claves del conjunto (permite leer datos cifrados con la clave anterior
    durante la rotación). Si la activa o la anterior cambian, la instancia se
    reconstruye: la rotación de clave es efectiva sin reiniciar el proceso.

    Returns:
        Instancia MultiFernet lista para cifrar/descifrar.

    Raises:
        ValueError: Si alguna clave no es una clave Fernet válida.
        pydantic_settings.ValidationError: Si `pseudonymization_encryption_key`
            no está configurada en el entorno.
    """
    global _fernet_instance, _fernet_key
    active, previous = _configured_keys()
    cache_key = (active, previous)
    if _fernet_instance is None or _fernet_key != cache_key:
        raw_keys = [active]
        if previous is not None:
            raw_keys.append(previous)
        fernets = [
            Fernet(k.encode() if isinstance(k, str) else k) for k in raw_keys
        ]
        _fernet_instance = MultiFernet(fernets)
        _fernet_key = cache_key
    return _fernet_instance


class EncryptedText(TypeDecorator):
    """
    TypeDecorator de SQLAlchemy que cifra at-rest con Fernet.

    Uso:
        En la declaración de columna del modelo:
            descripcion_original: Mapped[str] = mapped_column(EncryptedText)

    Comportamiento:
        - Python → DB (process_bind_param): cifra el texto con Fernet; almacena
          el ciphertext base64 como texto en la columna `Text`.
        - DB → Python (process_result_value): descifra el ciphertext Fernet;
          devuelve el texto original como str.
        - None en cualquier dirección → None (columnas nullable).

    Portabilidad:
        El ciphertext es texto base64 URL-safe (ASCII), idéntico en PostgreSQL
        y SQLite. No depende de extensiones del servidor de base de datos.

    Atributos:
        impl: SQLAlchemy usa `Text` como tipo subyacente en la DB.
        cache_ok: True — el TypeDecorator no tiene estado mutable que invalide
                  el caché de compilación de SQLAlchemy.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """
        Cifra el valor antes de enviarlo a la base de datos.

        Args:
            value:   Texto plano a cifrar, o None.
            dialect: Dialecto SQL activo (no usado; Fernet es DB-agnóstico).

        Returns:
            Ciphertext base64 como str, o None si value es None.
        """
        if value is None:
            return None
        return _get_fernet().encrypt(value.encode("utf-8")).decode("ascii")

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """
        Descifra el valor leído desde la base de datos.

        Args:
            value:   Ciphertext base64 como str, o None.
            dialect: Dialecto SQL activo (no usado; Fernet es DB-agnóstico).

        Returns:
            Texto plano descifrado como str, o None si value es None.
        """
        if value is None:
            return None
        return _get_fernet().decrypt(value.encode("ascii")).decode("utf-8")
