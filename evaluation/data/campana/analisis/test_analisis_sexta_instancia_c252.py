"""Pruebas de la extensión media de descripciones por canal y por régimen (c-252, D-04).

TDD estricto de las funciones puras con casos sintéticos (sin red, sin base de datos y
sin condenar al modelo), más la escritura determinista de las salidas. Cubre:

- la extensión media en palabras y en caracteres por canal de origen;
- la agregación por régimen ((a) = correo electrónico + formulario web, (b) = llamada
  telefónica);
- la escritura determinista de `.json`, `.md` y `.SHA256SUMS.txt` byte a byte.

Sigue el patrón de `test_analisis_regimen_c249.py` y su módulo `analisis_regimen_c249.py`.
Las descripciones sintéticas son mínimas y de extensión conocida para verificar la media sin
ambigüedad de tokenización.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_sexta_instancia_c252 as c252  # noqa: E402


CASOS = [
    {"id": "R001", "descripcion": "No puede ingresar al sistema", "canal_origen": "correo electrónico"},
    {"id": "R002", "descripcion": "La impresora no imprime a doble faz", "canal_origen": "correo electrónico"},
    {"id": "R003", "descripcion": "Falla la carga", "canal_origen": "formulario web"},
    {"id": "R004", "descripcion": "No enciende el monitor", "canal_origen": "llamada telefónica"},
]


# ---------------------------------------------------------------------------
# Extensión por canal
# ---------------------------------------------------------------------------
def test_extension_por_canal_palabras():
    r = c252.extension_por_canal(CASOS)
    # correo: "No puede ingresar al sistema" (5) + "La impresora no imprime a doble faz" (7) → media 6,0
    assert r["correo electrónico"]["palabras_media"] == pytest.approx(6.0)
    assert r["correo electrónico"]["n"] == 2
    # formulario: "Falla la carga" (3) → media 3,0
    assert r["formulario web"]["palabras_media"] == pytest.approx(3.0)
    assert r["formulario web"]["n"] == 1
    # telefonía: "No enciende el monitor" (4) → media 4,0
    assert r["llamada telefónica"]["palabras_media"] == pytest.approx(4.0)


def test_extension_por_canal_caracteres():
    r = c252.extension_por_canal(CASOS)
    correo = c252._n_caracteres("No puede ingresar al sistema") + c252._n_caracteres(
        "La impresora no imprime a doble faz"
    )
    assert r["correo electrónico"]["caracteres_media"] == pytest.approx(correo / 2)
    assert r["llamada telefónica"]["caracteres_media"] == pytest.approx(
        c252._n_caracteres("No enciende el monitor")
    )


def test_extension_por_canal_sin_casos():
    vacio = [c for c in CASOS if c["canal_origen"] != "llamada telefónica"]
    r = c252.extension_por_canal(vacio)
    assert r["llamada telefónica"]["n"] == 0
    assert r["llamada telefónica"]["palabras_media"] is None
    assert r["llamada telefónica"]["caracteres_media"] is None


def test_extension_por_canal_canales_conocidos_en_orden():
    r = c252.extension_por_canal(CASOS)
    # Los tres canales canónicos presentes, en el orden fijo de CANALES.
    assert list(r.keys()) == list(c252.CANALES)


# ---------------------------------------------------------------------------
# Extensión por régimen
# ---------------------------------------------------------------------------
def test_extension_por_regimen_agrega_a_y_b():
    r = c252.extension_por_regimen(CASOS)
    # régimen (a) = correo (2) + formulario (1) = 3 casos
    assert r["a"]["n"] == 3
    assert r["b"]["n"] == 1
    palabras_a = 5 + 7 + 3
    assert r["a"]["palabras_media"] == pytest.approx(palabras_a / 3)
    assert r["b"]["palabras_media"] == pytest.approx(4.0)


def test_extension_por_regimen_sin_casos_del_regimen_b():
    sin_b = [c for c in CASOS if c["canal_origen"] != "llamada telefónica"]
    r = c252.extension_por_regimen(sin_b)
    assert r["b"]["n"] == 0
    assert r["b"]["palabras_media"] is None
    assert r["b"]["caracteres_media"] is None


# ---------------------------------------------------------------------------
# Conteo de palabras y caracteres
# ---------------------------------------------------------------------------
def test_n_palabras_separa_por_espacios():
    assert c252._n_palabras("uno dos tres") == 3
    assert c252._n_palabras("  con   espacios   extra  ") == 3
    assert c252._n_palabras("") == 0


def test_n_caracteres_cuenta_sin_espacios():
    assert c252._n_caracteres("abc def") == 6  # no cuenta el espacio intermedio
    assert c252._n_caracteres("") == 0


# ---------------------------------------------------------------------------
# Resultado y escritura determinista
# ---------------------------------------------------------------------------
def _resultado_sintetico() -> dict:
    return c252.construir_resultado(
        casos=CASOS,
        rutas_entrada={"corpus": "sintetico"},
    )


def test_construir_resultado_incluye_secciones():
    r = _resultado_sintetico()
    assert set(r) >= {"schema_version", "extension_por_canal", "extension_por_regimen", "entradas"}


def test_escritura_determinista(tmp_path):
    r = _resultado_sintetico()
    a = c252.escribir_salidas(r, tmp_path / "a")
    b = c252.escribir_salidas(r, tmp_path / "b")
    for pa, pb in zip(a, b):
        assert pa.name == pb.name
        assert pa.read_bytes() == pb.read_bytes()


def test_escritura_emite_json_md_y_suma(tmp_path):
    rutas = c252.escribir_salidas(_resultado_sintetico(), tmp_path)
    nombres = [p.name for p in rutas]
    assert any(n.endswith(".json") for n in nombres)
    assert any(n.endswith(".md") for n in nombres)
    assert any(n.endswith(".SHA256SUMS.txt") for n in nombres)