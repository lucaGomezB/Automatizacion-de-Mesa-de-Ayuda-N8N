"""
Tests unitarios del helper de escape de comodines LIKE (c-88, IS-002, D4).

El helper convierte un termino de busqueda de texto en un patron literal: los
comodines de LIKE (`%`, `_`) y el caracter de escape (`\\`) se escapan para que
su presencia en el termino NO altere el patron de coincidencia. Los tests son
directos sobre la funcion pura (unidad, sin base de datos).
"""

from app.repositories.incidente_repository import escapar_like


def test_escapar_like_porcentaje_se_convierte_en_literal():
    """El `%` se escapa para no actuar como comodin de "varios caracteres"."""
    assert escapar_like("100%") == "100\\%"


def test_escapar_like_underscore_se_convierte_en_literal():
    """El `_` se escapa para no actuar como comodin de "un caracter"."""
    assert escapar_like("a_b") == "a\\_b"


def test_escapar_like_backslash_se_duplica():
    """El backslash (caracter de escape) se duplica primero."""
    assert escapar_like("a\\b") == "a\\\\b"


def test_escapar_like_sin_comodines_no_cambia():
    """Un termino sin caracteres especiales se devuelve identico."""
    assert escapar_like("base de datos") == "base de datos"


def test_escapar_like_combinado_escapa_los_tres_caracteres():
    """Triangulacion: los tres caracteres se escapan en una misma cadena."""
    assert escapar_like("50%_x\\") == "50\\%\\_x\\\\"
