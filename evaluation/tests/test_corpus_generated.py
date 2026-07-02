"""
Tests para el corpus generado por evaluation/generate_corpus.py.

Verifica que el CSV generado cumple con todas las restricciones:
- 200 casos exactos
- Distribucion estratificada (82/64/54)
- Categorias validas
- Columnas requeridas
- Reproducibilidad (mismo seed = mismo output)
"""

from __future__ import annotations

import csv
import io
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
GENERATED_CORPUS = (
    pathlib.Path(__file__).parent.parent / "data" / "corpus_evaluacion.csv"
)

CATEGORIAS_VALIDAS = {"Sistemas", "Operaciones", "Soporte T\u00e9cnico"}
CANALES_VALIDOS = {"correo", "formulario", "telefono"}


# ---------------------------------------------------------------------------
# RED: test que falla hasta que el corpus exista
# ---------------------------------------------------------------------------
def test_corpus_generado_existe():
    """El archivo corpus_evaluacion.csv debe existir."""
    assert GENERATED_CORPUS.exists(), (
        f"No se encontro el corpus en {GENERATED_CORPUS}. "
        "Ejecuta 'python evaluation/generate_corpus.py' primero."
    )


def test_corpus_generado_tiene_200_casos():
    """El corpus debe contener exactamente 200 casos (filas de datos)."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 200, f"Se esperaban 200 casos, se encontraron {len(rows)}"


def test_corpus_generado_distribucion():
    """La distribucion debe ser exactamente 82 Sistemas, 64 Operaciones, 54 Soporte Tecnico."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    conteo: dict[str, int] = {}
    for row in rows:
        cat = row["categoria_real"]
        conteo[cat] = conteo.get(cat, 0) + 1

    sistemas = next((k for k in conteo if "Sistemas" in k or "sistemas" in k.lower()), "Sistemas")
    operaciones = next((k for k in conteo if "Operaciones" in k or "operaciones" in k.lower()), "Operaciones")
    soporte = next((k for k in conteo if "Soporte" in k), "Soporte T\u00e9cnico")

    assert conteo.get(sistemas, 0) == 82, f"Sistemas: {conteo.get(sistemas, 0)} != 82"
    assert conteo.get(operaciones, 0) == 64, f"Operaciones: {conteo.get(operaciones, 0)} != 64"
    assert conteo.get(soporte, 0) == 54, (
        f"Soporte Tecnico: {conteo.get(soporte, 0)} != 54"
    )


def test_corpus_generado_categorias_validas():
    """Todas las categorias deben pertenecer al conjunto valido."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        assert row["categoria_real"] in CATEGORIAS_VALIDAS, (
            f"Categoria invalida '{row['categoria_real']}' en id={row['id']}"
        )


def test_corpus_generado_columnas_requeridas():
    """El CSV debe tener las columnas id, descripcion, canal_origen, categoria_real."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columnas = reader.fieldnames

    assert columnas is not None, "El CSV no tiene cabecera"
    assert "id" in columnas, f"Falta columna 'id'. Columnas: {columnas}"
    assert "descripcion" in columnas, f"Falta columna 'descripcion'. Columnas: {columnas}"
    assert "canal_origen" in columnas, f"Falta columna 'canal_origen'. Columnas: {columnas}"
    assert "categoria_real" in columnas, (
        f"Falta columna 'categoria_real'. Columnas: {columnas}"
    )


def test_corpus_generado_ids_secuenciales():
    """Los ids deben ser secuenciales de 1 a 200."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    ids = [int(row["id"]) for row in rows]
    assert ids == list(range(1, 201)), (
        f"Ids no secuenciales. Primeros 5: {ids[:5]}, Ultimos 5: {ids[-5:]}"
    )


def test_corpus_generado_canales_validos():
    """Todos los canales deben ser correo, formulario o telefono."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        assert row["canal_origen"] in CANALES_VALIDOS, (
            f"Canal invalido '{row['canal_origen']}' en id={row['id']}"
        )


def test_corpus_generado_descripciones_no_vacias():
    """Ninguna descripcion debe estar vacia y deben tener longitud minima."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        desc = row["descripcion"].strip()
        assert len(desc) > 10, f"Descripcion muy corta en id={row['id']}: '{desc}'"
        assert len(desc) < 500, f"Descripcion muy larga en id={row['id']}: {len(desc)} chars"


def test_corpus_generado_cargable_por_framework():
    """El corpus debe ser cargable por evaluation.corpus.cargar_corpus()."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    from evaluation.corpus import cargar_corpus

    casos = cargar_corpus(GENERATED_CORPUS)
    assert len(casos) == 200
    # Verificar que el primer caso tiene los campos esperados
    primero = casos[0]
    assert primero.id is not None
    assert len(primero.descripcion) > 0
    assert primero.categoria_real in CATEGORIAS_VALIDAS


# ---------------------------------------------------------------------------
# Tests de reproducibilidad (sobre la funcion de generacion, no el CSV)
# ---------------------------------------------------------------------------
def test_generate_corpus_es_reproducible():
    """Dos ejecuciones con el mismo seed producen identico output."""
    # Import diferido: el modulo generate_corpus debe existir
    try:
        from evaluation.generate_corpus import _generar_casos
    except ImportError:
        pytest.skip("generate_corpus.py no existe aun")

    casos_1 = _generar_casos(seed=42)
    casos_2 = _generar_casos(seed=42)

    assert len(casos_1) == 200
    assert len(casos_2) == 200

    for i, (c1, c2) in enumerate(zip(casos_1, casos_2)):
        assert c1["id"] == c2["id"], f"ids distintos en posicion {i}"
        assert c1["descripcion"] == c2["descripcion"], (
            f"Descripciones distintas en posicion {i}"
        )
        assert c1["categoria_real"] == c2["categoria_real"], (
            f"Categorias distintas en posicion {i}"
        )


def test_generate_corpus_seed_diferente_output_diferente():
    """Dos seeds distintos producen output diferente."""
    try:
        from evaluation.generate_corpus import _generar_casos
    except ImportError:
        pytest.skip("generate_corpus.py no existe aun")

    casos_1 = _generar_casos(seed=42)
    casos_2 = _generar_casos(seed=123)

    # Deberian diferir en al menos algunas descripciones
    descs_1 = {c["descripcion"] for c in casos_1}
    descs_2 = {c["descripcion"] for c in casos_2}
    assert descs_1 != descs_2, "Output identico con seeds distintos"


def test_generate_corpus_distribucion_desde_funcion():
    """La funcion _generar_casos produce la distribucion correcta."""
    try:
        from evaluation.generate_corpus import _generar_casos
    except ImportError:
        pytest.skip("generate_corpus.py no existe aun")

    casos = _generar_casos(seed=42)

    conteo: dict[str, int] = {}
    for c in casos:
        conteo[c["categoria_real"]] = conteo.get(c["categoria_real"], 0) + 1

    sistemas = next((k for k in conteo if "Sistemas" in k or "sistemas" in k.lower()), "Sistemas")
    operaciones = next((k for k in conteo if "Operaciones" in k or "operaciones" in k.lower()), "Operaciones")
    soporte = next((k for k in conteo if "Soporte" in k), "Soporte T\u00e9cnico")

    assert conteo.get(sistemas, 0) == 82
    assert conteo.get(operaciones, 0) == 64
    assert conteo.get(soporte, 0) == 54
