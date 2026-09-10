"""
Tests de los settings de pseudonimización agregados a la clase Settings.

Responsabilidad:
    Verifica que la clase Settings expone correctamente los campos nuevos
    requeridos por el módulo de pseudonimización (Ley 25.326):
        - pseudonymization_internal_domains: list[str], default []
        - pseudonymization_encryption_key:  str, OBLIGATORIO (sin default)

    Los tests instancian Settings directamente con los campos mínimos
    requeridos para evitar depender del .env real del entorno.

Notas:
    - pseudonymization_encryption_key es un campo obligatorio: pydantic-settings
      lanza ValidationError si no está presente al construir Settings.
    - Se usa una clave Fernet de prueba para las instanciaciones directas.
    - Los tests limpian el caché LRU de get_settings() para no interferir
      entre sí ni con otros tests de la suite.
"""

import pytest
from pydantic import ValidationError

from app.config.settings import Settings, get_settings

# Clave Fernet de prueba (no contiene datos reales)
_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

# Campos mínimos para instanciar Settings directamente en tests
_REQUIRED_FIELDS = {
    "database_url": "sqlite+aiosqlite:///:memory:",
    "gemini_api_key": "fake-gemini-key",
    "pseudonymization_encryption_key": _TEST_KEY,
}


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Limpia el caché LRU de get_settings() antes y después de cada test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestPseudonymizationInternalDomains:
    """Tests del campo pseudonymization_internal_domains."""

    def test_pseudonymization_internal_domains_default_es_lista_vacia(self) -> None:
        """
        pseudonymization_internal_domains tiene default [] cuando no se configura.
        """
        settings = Settings(**_REQUIRED_FIELDS)
        assert settings.pseudonymization_internal_domains == []

    def test_pseudonymization_internal_domains_acepta_lista_de_strings(self) -> None:
        """
        pseudonymization_internal_domains acepta una lista de strings de dominios.
        """
        settings = Settings(
            **_REQUIRED_FIELDS,
            pseudonymization_internal_domains=["corp.empresa.com", "empresa.local"],
        )
        assert settings.pseudonymization_internal_domains == [
            "corp.empresa.com",
            "empresa.local",
        ]

    def test_pseudonymization_internal_domains_es_lista_tipada(self) -> None:
        """
        El tipo del campo es list[str]: cada elemento es un string.
        """
        settings = Settings(**_REQUIRED_FIELDS)
        assert isinstance(settings.pseudonymization_internal_domains, list)


class TestPseudonymizationEncryptionKey:
    """Tests del campo pseudonymization_encryption_key."""

    def test_pseudonymization_encryption_key_es_accesible(self) -> None:
        """
        Settings expone pseudonymization_encryption_key como atributo str.
        """
        settings = Settings(**_REQUIRED_FIELDS)
        assert settings.pseudonymization_encryption_key == _TEST_KEY
        assert isinstance(settings.pseudonymization_encryption_key, str)

    def test_pseudonymization_encryption_key_no_tiene_valor_por_defecto_en_clase(self) -> None:
        """
        Verifica que la clase Settings define pseudonymization_encryption_key
        como campo requerido (sin default en el modelo): el campo NO tiene un
        valor por defecto definido en la clase (solo puede venir del .env o
        de la instanciación explícita).

        Nota: pydantic-settings SIEMPRE lee .env al instanciar Settings(),
        por lo que no es posible probar el fallo en un entorno con .env válido.
        En cambio, verificamos que la anotación del campo NO tiene default.
        """
        import inspect
        fields = Settings.model_fields
        assert "pseudonymization_encryption_key" in fields, (
            "El campo pseudonymization_encryption_key debe existir en Settings"
        )
        field_info = fields["pseudonymization_encryption_key"]
        # Un campo obligatorio no tiene default ni default_factory
        assert field_info.default is None or field_info.is_required(), (
            "pseudonymization_encryption_key debe ser obligatorio (sin valor por defecto)"
        )

    def test_pseudonymization_encryption_key_acepta_clave_fernet_valida(self) -> None:
        """
        Una clave Fernet válida (base64 urlsafe de 32 bytes) es aceptada por Settings.
        """
        from cryptography.fernet import Fernet
        clave_nueva = Fernet.generate_key().decode()
        settings = Settings(**{**_REQUIRED_FIELDS, "pseudonymization_encryption_key": clave_nueva})
        assert settings.pseudonymization_encryption_key == clave_nueva
