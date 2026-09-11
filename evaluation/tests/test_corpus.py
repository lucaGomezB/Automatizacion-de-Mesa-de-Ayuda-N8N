"""
Tests para evaluation/corpus.py — carga y contrato del corpus JSON multietiqueta.

TDD — ciclos: RED -> GREEN -> TRIANGULATE -> REFACTOR
C-27: el corpus pasa de CSV single-label (`categoria_real`) a JSON multietiqueta
(`sector_asignado` + `sectores_adicionales`).
"""

from __future__ import annotations

import json
import pathlib

import pytest

from evaluation.tests.conftest import CORPUS_FIXTURE_PATH

# ---------------------------------------------------------------------------
# Vocabulario canonico aprobado (C-27): exacto, case-sensitive, SIN tildes.
# ---------------------------------------------------------------------------
SECTORES_CANONICOS = frozenset(
    {
        "Seguridad Informatica",
        "Soporte Tecnico Hardware",
        "Soporte Tecnico Software",
        "Bases de Datos",
        "Sistemas",
    }
)

_BACKEND_DIR = pathlib.Path(__file__).resolve().parents[2] / "App" / "Backend"


def _sectores_del_backend() -> frozenset[str]:
    """Importa la constante canonica del backend para verificar paridad (1.5)."""
    import sys

    backend = str(_BACKEND_DIR)
    if backend not in sys.path:
        sys.path.insert(0, backend)
    from app.constants import SECTORES_CANONICOS as BACKEND

    return frozenset(BACKEND)


def _caso(**overrides: object) -> dict:
    """Construye un caso valido y permite sobrescribir campos."""
    caso = {
        "id": "1",
        "descripcion": "El servidor de base de datos no responde.",
        "canal_origen": "correo",
        "sector_asignado": "Bases de Datos",
        "sectores_adicionales": [],
        "tiempo_manual_s": 180,
        "tiempo_automatizado_s": 12,
    }
    caso.update(overrides)
    return caso


def _escribir_doc(path: pathlib.Path, casos: list[dict], total_casos: object = None) -> pathlib.Path:
    """Escribe un documento JSON de corpus valido (o manipulado) en `path`."""
    doc = {
        "schema_version": 1,
        "metadata": {
            "descripcion": "corpus de prueba",
            "total_casos": len(casos) if total_casos is None else total_casos,
        },
        "casos": casos,
    }
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return path


# ===========================================================================
# 1.5 / 1.6 — Paridad del vocabulario canonico con el backend
# ===========================================================================
def test_categorias_validas_coinciden_con_el_backend():
    """El conjunto canonico de evaluacion debe ser exactamente el del backend (1.5/1.6)."""
    from evaluation.corpus import CATEGORIAS_VALIDAS

    assert frozenset(CATEGORIAS_VALIDAS) == SECTORES_CANONICOS
    assert frozenset(CATEGORIAS_VALIDAS) == _sectores_del_backend()


def test_operaciones_no_pertenece_al_conjunto_canonico():
    """`Operaciones` fue eliminado del dominio y no debe ser valido."""
    from evaluation.corpus import CATEGORIAS_VALIDAS

    assert "Operaciones" not in CATEGORIAS_VALIDAS


# ===========================================================================
# 7.2 RED -> 7.3 GREEN: carga valida del documento JSON
# ===========================================================================
def test_cargar_corpus_valido_devuelve_todos_los_casos():
    """Un JSON valido con 9 casos devuelve 9 CasoEvaluacion y preserva el primero."""
    from evaluation.corpus import cargar_corpus

    casos = cargar_corpus(CORPUS_FIXTURE_PATH)

    assert len(casos) == 9
    primero = casos[0]
    assert primero.id == "1"
    assert "acceso no autorizado" in primero.descripcion
    assert primero.sector_asignado == "Seguridad Informatica"
    assert list(primero.sectores_adicionales) == []


def test_caso_con_sectores_adicionales_los_expone():
    """Un caso con sectores adicionales conserva su arreglo y su conjunto de verdad."""
    from evaluation.corpus import cargar_corpus

    casos = cargar_corpus(CORPUS_FIXTURE_PATH)
    cuarto = casos[3]

    assert cuarto.id == "4"
    assert cuarto.sector_asignado == "Soporte Tecnico Hardware"
    assert cuarto.sectores_adicionales == ["Soporte Tecnico Software"]
    assert cuarto.conjunto_verdad == frozenset(
        {"Soporte Tecnico Hardware", "Soporte Tecnico Software"}
    )


def test_tiempos_y_canal_se_cargan():
    """Los tiempos numericos y el canal de origen se preservan."""
    from evaluation.corpus import cargar_corpus

    primero = cargar_corpus(CORPUS_FIXTURE_PATH)[0]
    assert primero.canal_origen == "correo"
    assert primero.tiempo_manual_s == 180.0
    assert primero.tiempo_automatizado_s == 12.0


def test_sectores_adicionales_vacio_es_valido(tmp_path):
    """`sectores_adicionales: []` es valido y el conjunto de verdad es solo el asignado."""
    from evaluation.corpus import cargar_corpus

    camino = _escribir_doc(tmp_path / "corpus_vacio.json", [_caso()])
    primero = cargar_corpus(camino)[0]
    assert primero.sectores_adicionales == []
    assert primero.conjunto_verdad == frozenset({"Bases de Datos"})


# ===========================================================================
# 7.4 / 7.14 TRIANGULATE: errores de carga accionables
# ===========================================================================
def test_cargar_corpus_inexistente_lanza_error(tmp_path):
    """Una ruta que no existe lanza FileNotFoundError mencionando el archivo."""
    from evaluation.corpus import cargar_corpus

    ruta_falsa = tmp_path / "no_existe.json"
    with pytest.raises(FileNotFoundError, match="no_existe.json"):
        cargar_corpus(ruta_falsa)


def test_json_malformado_lanza_error_con_ruta_y_motivo(tmp_path):
    """Un JSON malformado lanza error claro que incluye la ruta y el motivo."""
    from evaluation.corpus import cargar_corpus

    roto = tmp_path / "roto.json"
    roto.write_text("{ esto no es json", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON malformado"):
        cargar_corpus(roto)

    with pytest.raises(ValueError, match="roto.json"):
        cargar_corpus(roto)


def test_documento_sin_casos_lanza_error(tmp_path):
    """Un documento sin el arreglo `casos` lanza error identificando el campo."""
    from evaluation.corpus import cargar_corpus

    doc = tmp_path / "sin_casos.json"
    doc.write_text(json.dumps({"schema_version": 1, "metadata": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="casos"):
        cargar_corpus(doc)


def test_total_casos_desincronizado_se_normaliza_y_persiste(tmp_path):
    """
    `metadata.total_casos` distinto de len(casos) NO se rechaza (design D3):
    se normaliza a len(casos) y se persiste en disco antes de usarlo (7.14/7.15).
    """
    from evaluation.corpus import cargar_corpus

    doc = _escribir_doc(tmp_path / "inconsistente.json", [_caso()], total_casos=99)

    casos = cargar_corpus(doc)
    assert len(casos) == 1

    en_disco = json.loads(doc.read_text(encoding="utf-8"))
    assert en_disco["metadata"]["total_casos"] == 1


def test_total_casos_consistente_no_reescribe_el_archivo(tmp_path):
    """
    La normalizacion es idempotente: si `total_casos` ya coincide, no se
    reescribe el archivo (7.15).
    """
    from evaluation.corpus import cargar_corpus

    doc = _escribir_doc(tmp_path / "consistente.json", [_caso()], total_casos=1)
    texto_antes = doc.read_text(encoding="utf-8")

    cargar_corpus(doc)

    assert doc.read_text(encoding="utf-8") == texto_antes


def test_campo_requerido_ausente_lanza_error(tmp_path):
    """Omitir `sector_asignado` lanza error que identifica el campo y el caso (7.14)."""
    from evaluation.corpus import cargar_corpus

    caso = _caso()
    del caso["sector_asignado"]
    doc = _escribir_doc(tmp_path / "sin_sector.json", [caso])

    with pytest.raises(ValueError, match="sector_asignado"):
        cargar_corpus(doc)


def test_sectores_adicionales_ausente_lanza_error(tmp_path):
    """Omitir `sectores_adicionales` lanza error que identifica el campo requerido."""
    from evaluation.corpus import cargar_corpus

    caso = _caso()
    del caso["sectores_adicionales"]
    doc = _escribir_doc(tmp_path / "sin_adicionales.json", [caso])

    with pytest.raises(ValueError, match="sectores_adicionales"):
        cargar_corpus(doc)


def test_sector_asignado_invalido_lanza_error(tmp_path):
    """Un sector asignado fuera del conjunto (minuscula) lanza error identificando el valor."""
    from evaluation.corpus import cargar_corpus

    doc = _escribir_doc(tmp_path / "cat_invalida.json", [_caso(sector_asignado="sistemas")])

    with pytest.raises(ValueError, match="sistemas"):
        cargar_corpus(doc)


def test_operaciones_asignado_lanza_error(tmp_path):
    """`Operaciones` es invalido en el sector asignado."""
    from evaluation.corpus import cargar_corpus

    doc = _escribir_doc(tmp_path / "operaciones.json", [_caso(sector_asignado="Operaciones")])

    with pytest.raises(ValueError, match="Operaciones"):
        cargar_corpus(doc)


def test_sector_adicional_invalido_lanza_error(tmp_path):
    """Un valor fuera del conjunto en adicionales lanza error identificando el valor."""
    from evaluation.corpus import cargar_corpus

    doc = _escribir_doc(
        tmp_path / "adicional_invalido.json",
        [_caso(sectores_adicionales=["Redes"])],
    )

    with pytest.raises(ValueError, match="Redes"):
        cargar_corpus(doc)


def test_sector_asignado_repetido_en_adicionales_lanza_error(tmp_path):
    """Repetir `sector_asignado` dentro de `sectores_adicionales` viola la invariante."""
    from evaluation.corpus import cargar_corpus

    doc = _escribir_doc(
        tmp_path / "repetido.json",
        [_caso(sector_asignado="Sistemas", sectores_adicionales=["Sistemas"])],
    )

    with pytest.raises(ValueError, match="repite|invariante"):
        cargar_corpus(doc)
