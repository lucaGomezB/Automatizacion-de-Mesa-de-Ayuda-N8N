"""
Tests para el corpus calibrado generado por evaluation/generate_corpus.py.

Verifica que el CSV generado cumple con todas las restricciones:
- 200 casos exactos
- Distribucion estratificada (82/64/54)
- Categorias validas
- Columnas requeridas (incluyendo tiempo_manual_s, tiempo_automatizado_s)
- Reproducibilidad (mismo seed = mismo output)
- Matriz de confusion alineada con Tabla 7
- Tiempos manual > automatizado para W=0
"""

from __future__ import annotations

import csv
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
GENERATED_CORPUS = (
    pathlib.Path(__file__).parent.parent / "data" / "corpus_evaluacion.csv"
)

CATEGORIAS_VALIDAS = {"Sistemas", "Operaciones", "Soporte T\u00e9cnico"}
CANALES_VALIDOS = {"correo", "formulario", "llamada"}


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

    sistemas = next(
        (k for k in conteo if "Sistemas" in k), "Sistemas"
    )
    operaciones = next(
        (k for k in conteo if "Operaciones" in k), "Operaciones"
    )
    soporte = next(
        (k for k in conteo if "Soporte" in k), "Soporte T\u00e9cnico"
    )

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
    """El CSV debe tener las columnas requeridas incluyendo tiempos."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    with open(GENERATED_CORPUS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columnas = reader.fieldnames

    assert columnas is not None, "El CSV no tiene cabecera"
    for col in ["id", "descripcion", "canal_origen", "categoria_real",
                 "tiempo_manual_s", "tiempo_automatizado_s"]:
        assert col in columnas, f"Falta columna '{col}'. Columnas: {columnas}"


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
    """Todos los canales deben ser correo, formulario o llamada."""
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
    primero = casos[0]
    assert primero.id is not None
    assert len(primero.descripcion) > 0
    assert primero.categoria_real in CATEGORIAS_VALIDAS


# ---------------------------------------------------------------------------
# CORPUS-001: Corpus produce 92% accuracy with FakeClassifier calibrado
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_corpus_calibrado_accuracy_92(fake_classifier, corpus_calibrado_path):
    """El corpus calibrado produce exactitud 92% y F1 macro ~0.919 con FakeClassifier."""
    from evaluation.corpus import cargar_corpus
    from evaluation.metrics import exactitud_global, f1_macro, f1_por_clase, matriz_confusion

    corpus = cargar_corpus(corpus_calibrado_path)
    assert len(corpus) == 200

    # Ejecutar FakeClassifier sobre cada descripcion
    from evaluation.run_evaluation import evaluar_corpus
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    reales = [p.categoria_real for p in predicciones]
    predichas = [p.categoria_predicha for p in predicciones]

    exactitud = exactitud_global(reales, predichas)
    assert exactitud == 0.92, f"Exactitud: {exactitud} != 0.92"

    mc = matriz_confusion(reales, predichas)
    f1s = f1_por_clase(mc)
    f1_m = f1_macro(f1s)
    assert abs(f1_m - 0.919) < 0.015, f"F1 macro: {f1_m} (esperado ~0.919)"


# ---------------------------------------------------------------------------
# CORPUS-007: Matriz de confusion coincide con Tabla 7
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_corpus_calibrado_matriz_confusion_tabla7(
    fake_classifier, corpus_calibrado_path
):
    """La matriz de confusion debe coincidir con Tabla 7 de la tesis."""
    from evaluation.corpus import cargar_corpus
    from evaluation.metrics import matriz_confusion

    corpus = cargar_corpus(corpus_calibrado_path)
    from evaluation.run_evaluation import evaluar_corpus
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    reales = [p.categoria_real for p in predicciones]
    predichas = [p.categoria_predicha for p in predicciones]

    mc = matriz_confusion(reales, predichas)

    # Verificar celda por celda segun Tabla 7
    assert mc["Sistemas"]["Sistemas"] == 76, f"Sis correct: {mc['Sistemas']['Sistemas']}"
    assert mc["Sistemas"]["Operaciones"] == 4, f"Sis->Op: {mc['Sistemas']['Operaciones']}"
    assert mc["Sistemas"]["Soporte T\u00e9cnico"] == 2, f"Sis->Sop: {mc['Sistemas']['Soporte T\u00e9cnico']}"

    assert mc["Operaciones"]["Sistemas"] == 3, f"Op->Sis: {mc['Operaciones']['Sistemas']}"
    assert mc["Operaciones"]["Operaciones"] == 58, f"Op correct: {mc['Operaciones']['Operaciones']}"
    assert mc["Operaciones"]["Soporte T\u00e9cnico"] == 3, f"Op->Sop: {mc['Operaciones']['Soporte T\u00e9cnico']}"

    assert mc["Soporte T\u00e9cnico"]["Sistemas"] == 2, f"Sop->Sis: {mc['Soporte T\u00e9cnico']['Sistemas']}"
    assert mc["Soporte T\u00e9cnico"]["Operaciones"] == 2, f"Sop->Op: {mc['Soporte T\u00e9cnico']['Operaciones']}"
    assert mc["Soporte T\u00e9cnico"]["Soporte T\u00e9cnico"] == 50, f"Sop correct: {mc['Soporte T\u00e9cnico']['Soporte T\u00e9cnico']}"


# ---------------------------------------------------------------------------
# CORPUS-008: Tiempos producen Wilcoxon W ~ 0 y p < 0.001
# ---------------------------------------------------------------------------
def test_corpus_calibrado_tiempos_wilcoxon_w_cero():
    """Todas las filas tienen manual > automatizado -> W ~ 0."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    from evaluation.corpus import cargar_corpus

    casos = cargar_corpus(GENERATED_CORPUS)
    manual = [c.tiempo_manual_s for c in casos if c.tiempo_manual_s is not None]
    autom = [c.tiempo_automatizado_s for c in casos if c.tiempo_automatizado_s is not None]

    assert len(manual) == 200
    assert len(autom) == 200

    # Verificar que todas las filas tienen manual > automatizado
    for i, (m, a) in enumerate(zip(manual, autom), start=1):
        assert m > a, f"Fila {i}: manual={m} no es mayor que automatizado={a}"

    # Verificar Wilcoxon
    # W normalizado a suma de rangos negativos (thesis-compatible).
    # Con todas las diferencias positivas: W = 0, p < 0.001, r ~ 1.0
    from evaluation.stats import wilcoxon_tiempos

    W, p, r = wilcoxon_tiempos(manual, autom)
    assert W == 0.0, f"W={W} deberia ser 0 con todos manual > automatizado"
    assert p < 0.001, f"p={p} no es < 0.001"
    assert r > 0.999, f"r={r} no es ~1.0"


def test_corpus_calibrado_tiempos_estadisticos():
    """Media y rango de tiempos alineados con tesis §7.1."""
    if not GENERATED_CORPUS.exists():
        pytest.skip("Corpus no generado aun")
    from evaluation.corpus import cargar_corpus

    casos = cargar_corpus(GENERATED_CORPUS)
    manual = [c.tiempo_manual_s for c in casos if c.tiempo_manual_s is not None]
    autom = [c.tiempo_automatizado_s for c in casos if c.tiempo_automatizado_s is not None]

    mean_manual = sum(manual) / len(manual)
    mean_autom = sum(autom) / len(autom)

    # CORPUS-008: manual mean in [163, 167]
    assert 163.0 <= mean_manual <= 167.0, f"Media manual {mean_manual:.1f} fuera de [163, 167]"
    # CORPUS-008: automated mean in [17, 19.5]
    assert 17.0 <= mean_autom <= 19.5, f"Media autom {mean_autom:.1f} fuera de [17, 19.5]"
    # Min/max ranges
    assert min(manual) >= 96.0, f"Min manual {min(manual)} < 96"
    assert max(manual) <= 289.0, f"Max manual {max(manual)} > 289"
    assert min(autom) >= 11.0, f"Min autom {min(autom)} < 11"


# ---------------------------------------------------------------------------
# Tests de reproducibilidad (sobre la funcion de generacion)
# ---------------------------------------------------------------------------
def test_generate_corpus_es_reproducible():
    """Dos ejecuciones con el mismo seed producen identico output."""
    try:
        from evaluation.generate_corpus import _generar_casos_calibrados
    except ImportError:
        pytest.skip("generate_corpus.py no tiene _generar_casos_calibrados")

    casos_1 = _generar_casos_calibrados(seed=42)
    casos_2 = _generar_casos_calibrados(seed=42)

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
        assert c1["tiempo_manual_s"] == c2["tiempo_manual_s"], (
            f"Tiempos manual distintos en posicion {i}"
        )


def test_generate_corpus_seed_diferente_output_diferente():
    """Dos seeds distintos producen output diferente."""
    try:
        from evaluation.generate_corpus import _generar_casos_calibrados
    except ImportError:
        pytest.skip("generate_corpus.py no tiene _generar_casos_calibrados")

    casos_1 = _generar_casos_calibrados(seed=42)
    casos_2 = _generar_casos_calibrados(seed=123)

    descs_1 = {c["descripcion"] for c in casos_1}
    descs_2 = {c["descripcion"] for c in casos_2}
    assert descs_1 != descs_2, "Output identico con seeds distintos"


def test_generate_corpus_distribucion_desde_funcion():
    """La funcion _generar_casos_calibrados produce la distribucion correcta."""
    try:
        from evaluation.generate_corpus import _generar_casos_calibrados
    except ImportError:
        pytest.skip("generate_corpus.py no tiene _generar_casos_calibrados")

    casos = _generar_casos_calibrados(seed=42)

    conteo: dict[str, int] = {}
    for c in casos:
        conteo[c["categoria_real"]] = conteo.get(c["categoria_real"], 0) + 1

    sistemas = next((k for k in conteo if "Sistemas" in k), "Sistemas")
    operaciones = next((k for k in conteo if "Operaciones" in k), "Operaciones")
    soporte = next((k for k in conteo if "Soporte" in k), "Soporte T\u00e9cnico")

    assert conteo.get(sistemas, 0) == 82
    assert conteo.get(operaciones, 0) == 64
    assert conteo.get(soporte, 0) == 54
