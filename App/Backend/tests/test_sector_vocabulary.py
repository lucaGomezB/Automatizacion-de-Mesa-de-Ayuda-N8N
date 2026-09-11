"""
Tests del vocabulario canonico de sectores (C-27).

Fija el contrato de los cinco strings canonicos: exactos, case-sensitive y
SIN tildes. `Operaciones` se elimina por completo y `Sistemas` se mantiene
como categoria propia.

Strict TDD:
    1.x RED   -> los tests no pueden importar la constante (no existe).
    1.3 GREEN -> app.constants define SECTORES_CANONICOS y es_sector_canonico.
    1.4 TRIANGULATE -> variantes con tilde/casing y string vacio se rechazan.
"""

import pytest

from app.constants import SECTORES_CANONICOS, es_sector_canonico


# Orden canonico acordado (C-27, decision aprobada).
SECTORES_ESPERADOS = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)


class TestVocabularioCanonico:
    def test_existe_exactamente_el_conjunto_canonico(self):
        """El vocabulario canonico contiene exactamente los 5 strings acordados."""
        assert list(SECTORES_CANONICOS) == list(SECTORES_ESPERADOS)

    def test_los_strings_no_tienen_tildes_ni_enie(self):
        """Ningun nombre canonico contiene caracteres no ASCII (sin tildes/enie)."""
        for nombre in SECTORES_CANONICOS:
            assert nombre.isascii(), f"{nombre!r} contiene caracteres no ASCII"

    def test_operaciones_fue_eliminada(self):
        """`Operaciones` no pertenece al vocabulario canonico."""
        assert "Operaciones" not in SECTORES_CANONICOS
        assert not es_sector_canonico("Operaciones")

    @pytest.mark.parametrize("sector", SECTORES_ESPERADOS)
    def test_los_cinco_son_aceptados(self, sector):
        """Cada uno de los cinco sectores canonicos es aceptado exactamente."""
        assert es_sector_canonico(sector) is True

    @pytest.mark.parametrize(
        "invalido",
        [
            "",
            "Sistemas ",
            "sistemas",
            "SISTEMAS",
            "Seguridad Informática",
            "Soporte Técnico Hardware",
            "Soporte Tecnico Hardware ",
            "Bases de datos",
            "Operaciones",
            "CategoríaInexistente",
            None,
        ],
    )
    def test_variantes_con_tilde_casing_o_vacio_se_rechazan(self, invalido):
        """Variantes con tilde, casing distinto, espacios, vacio o desconocidas se rechazan."""
        assert es_sector_canonico(invalido) is False
