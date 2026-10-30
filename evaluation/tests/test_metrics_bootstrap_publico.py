"""
Promocion de los helpers de bootstrap de `evaluation/metrics.py` a API publica (c-167, D3).

`_percentil_intervalo` y `_remuestreos_indices` pasan a `percentil_intervalo` y
`remuestreos_indices` porque los comparten tres consumidores (kappa, exactitud agregada del
brazo manual y proporcion de tiempo de intervencion). Los nombres privados se conservan como
alias retrocompatibles y el comportamiento NO cambia: los valores fijados aca (golden master)
se capturaron ANTES del renombre con los helpers privados, sobre `corpus_fixture.json`.
"""

from __future__ import annotations

import pathlib
import random
import shutil

import pytest

from evaluation import metrics
from evaluation.corpus import cargar_corpus
from evaluation.metrics import (
    SEMILLA_BOOTSTRAP,
    intervalos_conjunto,
    intervalos_por_clase,
    percentil_intervalo,
    remuestreos_indices,
)

CORPUS_FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "corpus_fixture.json"

# Posiciones del dataset (corpus_fixture.json repetido 4 veces) con una prediccion equivocada:
# la clase predicha es la siguiente de las cinco canonicas.
POSICIONES_CON_ERROR = (1, 4, 7, 11, 14, 18, 25, 28, 34)


# ---------------------------------------------------------------------------
# 1.1 — los helpers publicos dan lo mismo que daban los privados
# ---------------------------------------------------------------------------
def test_percentil_intervalo_interpola_linealmente_sobre_la_muestra_ordenada():
    muestras = [float(i) for i in range(1, 11)]

    assert percentil_intervalo(muestras, 0.95) == pytest.approx((1.225, 9.775), abs=1e-12)


def test_percentil_intervalo_ordena_antes_de_tomar_los_cuantiles():
    assert percentil_intervalo([5.0, 1.0, 9.0, 3.0], 0.90) == pytest.approx((1.3, 8.4), abs=1e-12)


def test_percentil_intervalo_de_una_muestra_vacia_o_unitaria():
    assert percentil_intervalo([], 0.95) == (0.0, 0.0)
    assert percentil_intervalo([7.0], 0.95) == (7.0, 7.0)


def test_remuestreos_indices_reproduce_la_secuencia_de_la_semilla():
    generador = random.Random(SEMILLA_BOOTSTRAP)

    remuestras = [list(indices) for indices in remuestreos_indices(generador, 5, 2)]

    assert remuestras == [[4, 3, 4, 0, 3], [3, 2, 1, 3, 3]]


def test_remuestreos_indices_sin_casos_devuelve_listas_vacias():
    remuestras = [list(indices) for indices in remuestreos_indices(random.Random(1), 0, 2)]

    assert remuestras == [[], []]


def test_los_nombres_privados_siguen_siendo_alias_de_los_helpers_publicos():
    assert metrics._percentil_intervalo is metrics.percentil_intervalo
    assert metrics._remuestreos_indices is metrics.remuestreos_indices


# ---------------------------------------------------------------------------
# 1.3 — los IC bootstrap existentes no cambian (golden master previo al renombre)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    """`corpus_fixture.json` repetido 4 veces, con 9 predicciones equivocadas."""
    copia = tmp_path_factory.mktemp("corpus_fixture") / CORPUS_FIXTURE.name
    shutil.copyfile(CORPUS_FIXTURE, copia)
    corpus = cargar_corpus(copia)
    reales = [caso.sector_asignado for caso in corpus] * 4
    verdad = [caso.conjunto_verdad for caso in corpus] * 4
    predichos = list(reales)
    for i in POSICIONES_CON_ERROR:
        predichos[i] = metrics.CLASES[(metrics.CLASES.index(reales[i]) + 1) % len(metrics.CLASES)]
    return reales, predichos, verdad


def test_intervalos_por_clase_conserva_los_f1_de_antes_del_renombre(dataset):
    reales, predichos, _ = dataset

    resultado = intervalos_por_clase(reales, predichos)

    esperado = {
        "Seguridad Informatica": (0.5, 0.9473684210526316),
        "Soporte Tecnico Hardware": (0.6657894736842119, 1.0),
        "Soporte Tecnico Software": (0.0, 1.0),
        "Bases de Datos": (0.3333333333333333, 0.9413312693498443),
        "Sistemas": (0.25, 0.875),
    }
    assert {clase: ic.f1 for clase, ic in resultado.items()} == pytest.approx(esperado, abs=1e-12)


def test_intervalos_conjunto_conserva_los_intervalos_de_antes_del_renombre(dataset):
    _, predichos, verdad = dataset

    resultado = intervalos_conjunto(verdad, [frozenset({p}) for p in predichos])

    assert resultado.subset_accuracy == pytest.approx((0.2222222222222222, 0.5277777777777778), abs=1e-12)
    assert resultado.hamming_loss == pytest.approx((0.3194444444444444, 0.5555555555555557), abs=1e-12)
    assert resultado.micro_f1 == pytest.approx((0.5333333333333333, 0.7209302325581396), abs=1e-12)
