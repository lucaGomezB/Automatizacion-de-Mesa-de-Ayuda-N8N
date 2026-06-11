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

from cryptography.fernet import Fernet
from sqlalchemy import Text, TypeDecorator

from app.config.settings import get_settings

# Instancia Fernet con inicialización lazy (None hasta el primer uso).
# Esto evita que la importación del módulo falle en entornos sin clave configurada.
_fernet_instance: Fernet | None = None


def _get_fernet() -> Fernet:
    """
    Retorna la instancia Fernet, construyéndola la primera vez.

    La clave se lee de `settings.pseudonymization_encryption_key` en el primer
    acceso (lazy init). Esta estrategia evita que la importación falle en
    entornos donde la clave no está aún configurada (ej. al cargar módulos
    antes de que el entorno esté completo), y permite que los tests inyecten
    la clave vía monkeypatching de `get_settings`.

    Returns:
        Instancia Fernet lista para cifrar/descifrar.

    Raises:
        ValueError: Si la clave no es una clave Fernet válida (base64 de 32 bytes).
        pydantic_settings.ValidationError: Si `pseudonymization_encryption_key`
            no está configurada en el entorno.
    """
    global _fernet_instance
    if _fernet_instance is None:
        key = get_settings().pseudonymization_encryption_key
        _fernet_instance = Fernet(key.encode() if isinstance(key, str) else key)
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
