"""
Tests unitarios para el TypeDecorator EncryptedText (cifrado Fernet at-rest).

Responsabilidad:
    Verifica que EncryptedText (app.utils.encryption) cifra y descifra correctamente
    los valores de columna de manera transparente, usando Fernet via settings.

    Los tests inyectan una clave Fernet de prueba mediante override de get_settings(),
    garantizando que los tests son aislados y no requieren .env real.

    Tests síncronos: EncryptedText.process_bind_param / process_result_value
    son métodos síncronos de SQLAlchemy TypeDecorator.

Clave de prueba generada con: Fernet.generate_key().decode()
"""

import pytest
from cryptography.fernet import Fernet
from unittest.mock import MagicMock

from app.config.settings import get_settings
from app.utils.encryption import EncryptedText


# Clave Fernet de prueba (generada con Fernet.generate_key(); no contiene datos reales)
_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="


@pytest.fixture(autouse=True)
def override_settings_with_test_key(monkeypatch):
    """
    Inyecta la clave Fernet de prueba en get_settings() y resetea el caché
    de EncryptedText._fernet para que lo reconstruya con la clave de prueba.
    """
    # Crear settings mock con la clave de prueba
    mock_settings = MagicMock()
    mock_settings.pseudonymization_encryption_key = _TEST_FERNET_KEY

    # Override get_settings y limpiar caché LRU
    get_settings.cache_clear()
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: mock_settings)

    # Resetear la instancia Fernet cacheada (lazy init)
    import app.utils.encryption as enc_module
    enc_module._fernet_instance = None

    yield

    # Cleanup después del test
    enc_module._fernet_instance = None
    get_settings.cache_clear()


# Instancia del TypeDecorator para los tests
_type = EncryptedText()
_dialect = None  # process_bind_param y process_result_value ignoran el dialect


class TestEncryptedTextRoundTrip:
    """Tests de cifrado y descifrado (round-trip)."""

    def test_encrypted_text_round_trip(self) -> None:
        """
        process_bind_param produce un ciphertext distinto del original,
        y process_result_value lo descifra de vuelta al original.
        """
        original = "Incidente reportado por juan.perez@empresa.com al +54 261 555-1234"

        ciphertext = _type.process_bind_param(original, _dialect)
        assert ciphertext != original
        assert isinstance(ciphertext, str)

        decrypted = _type.process_result_value(ciphertext, _dialect)
        assert decrypted == original

    def test_encrypted_text_none_se_preserva_en_bind_param(self) -> None:
        """
        None en process_bind_param retorna None (columnas nullable).
        """
        result = _type.process_bind_param(None, _dialect)
        assert result is None

    def test_encrypted_text_none_se_preserva_en_result_value(self) -> None:
        """
        None en process_result_value retorna None (valor ausente en DB).
        """
        result = _type.process_result_value(None, _dialect)
        assert result is None

    def test_encrypted_text_ciphertext_no_contiene_plaintext(self) -> None:
        """
        El ciphertext producido no contiene la subcadena original como texto plano.
        """
        original = "Nombre: Carlos García. Email: carlos@empresa.com"

        ciphertext = _type.process_bind_param(original, _dialect)

        # El ciphertext Fernet es base64 urlsafe; no debe contener el texto original
        assert "Carlos" not in ciphertext
        assert "garcia" not in ciphertext.lower()
        assert "empresa.com" not in ciphertext

    def test_encrypted_text_distintos_ciphertexts_mismo_plaintext(self) -> None:
        """
        Fernet incluye nonce aleatorio: el mismo texto produce ciphertexts distintos
        en cada llamada (propiedad probabilística del cifrado).
        """
        original = "texto de prueba"
        c1 = _type.process_bind_param(original, _dialect)
        c2 = _type.process_bind_param(original, _dialect)

        # Con Fernet (modo CTR + nonce), dos cifraciones del mismo texto son distintas
        assert c1 != c2
        # Pero ambos descifran al original
        assert _type.process_result_value(c1, _dialect) == original
        assert _type.process_result_value(c2, _dialect) == original

    def test_encrypted_text_cadena_vacia(self) -> None:
        """
        Cadena vacía también puede ser cifrada y descifrada (no crash).
        """
        ciphertext = _type.process_bind_param("", _dialect)
        assert ciphertext is not None
        decrypted = _type.process_result_value(ciphertext, _dialect)
        assert decrypted == ""
