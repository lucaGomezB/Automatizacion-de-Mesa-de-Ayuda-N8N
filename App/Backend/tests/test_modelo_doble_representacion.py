"""
Tests de la doble representación en el modelo Incidente.

Sección 9 del plan TDD de c-03-pseudonymization-module.

Verifica que:
- Incidente tenga los atributos descripcion_original y descripcion_pseudonimizada.
- descripcion_original usa EncryptedText (TypeDecorator que cifra/descifra).
- El campo descripcion viejo NO existe en el modelo.
- Los índices compuestos siguen intactos.
"""

import pytest
from unittest.mock import MagicMock

from app.config.settings import get_settings
from app.models.incidente import Incidente


# Clave Fernet de prueba (la misma que usa test_encryption.py)
_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="


@pytest.fixture(autouse=True)
def override_encryption_key(monkeypatch):
    """Inyecta la clave Fernet de prueba antes de cada test."""
    mock_settings = MagicMock()
    mock_settings.pseudonymization_encryption_key = _TEST_FERNET_KEY

    get_settings.cache_clear()
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: mock_settings)

    import app.utils.encryption as enc_module
    enc_module._fernet_instance = None

    yield

    enc_module._fernet_instance = None
    get_settings.cache_clear()


class TestIncidenteDobleRepresentacion:
    """Verifica la estructura del modelo Incidente con doble representación."""

    def test_incidente_tiene_descripcion_pseudonimizada(self):
        """
        9.1 RED (parte a): Incidente debe tener el atributo descripcion_pseudonimizada.
        """
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(Incidente)
        columnas = {col.key for col in mapper.columns}
        assert "descripcion_pseudonimizada" in columnas, (
            "El modelo Incidente debe tener la columna 'descripcion_pseudonimizada'"
        )

    def test_incidente_tiene_descripcion_original(self):
        """
        9.1 RED (parte b): Incidente debe tener el atributo descripcion_original.
        """
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(Incidente)
        columnas = {col.key for col in mapper.columns}
        assert "descripcion_original" in columnas, (
            "El modelo Incidente debe tener la columna 'descripcion_original'"
        )

    def test_incidente_no_tiene_columna_descripcion_vieja(self):
        """
        9.3 REFACTOR check: La columna 'descripcion' (singular, sin sufijo) fue eliminada.
        """
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(Incidente)
        columnas = {col.key for col in mapper.columns}
        assert "descripcion" not in columnas, (
            "La columna 'descripcion' vieja debe ser eliminada del modelo; "
            "solo deben existir 'descripcion_original' y 'descripcion_pseudonimizada'"
        )

    def test_descripcion_original_usa_encrypted_text(self):
        """
        9.1 RED (parte c): descripcion_original debe usar el tipo EncryptedText.
        """
        from sqlalchemy import inspect as sa_inspect
        from app.utils.encryption import EncryptedText

        mapper = sa_inspect(Incidente)
        col = mapper.columns["descripcion_original"]
        assert isinstance(col.type, EncryptedText), (
            f"descripcion_original debe usar EncryptedText, pero usa {type(col.type)}"
        )

    def test_descripcion_pseudonimizada_es_text_plano(self):
        """
        9.1 RED (parte d): descripcion_pseudonimizada debe ser Text (no cifrado).
        """
        from sqlalchemy import Text, inspect as sa_inspect

        mapper = sa_inspect(Incidente)
        col = mapper.columns["descripcion_pseudonimizada"]
        # El tipo debe ser Text (no EncryptedText)
        assert isinstance(col.type, Text), (
            f"descripcion_pseudonimizada debe ser Text, pero es {type(col.type)}"
        )

    def test_indices_compuestos_siguen_intactos(self):
        """
        9.3 REFACTOR check: los índices compuestos definidos en __table_args__ persisten.
        """
        from sqlalchemy import inspect as sa_inspect

        mapper = sa_inspect(Incidente)
        table = mapper.local_table
        index_names = {idx.name for idx in table.indexes}
        assert "ix_incidente_created_sector" in index_names
        assert "ix_incidente_estado_created" in index_names

    def test_incidente_instanciable_con_ambas_columnas(self):
        """
        9.2 GREEN check: Incidente puede instanciarse con los nuevos campos sin crash.

        La instanciación no implica DB — solo verifica que el constructor acepta
        los nuevos atributos correctamente.
        """
        inc = Incidente(
            descripcion_original="Juan Pérez reportó falla en srv-correo01",
            descripcion_pseudonimizada="[PERSONA] reportó falla en [HOST]",
            prioridad="media",
            estado_id=1,
            requiere_revision_humana=False,
        )
        assert inc.descripcion_original == "Juan Pérez reportó falla en srv-correo01"
        assert inc.descripcion_pseudonimizada == "[PERSONA] reportó falla en [HOST]"
