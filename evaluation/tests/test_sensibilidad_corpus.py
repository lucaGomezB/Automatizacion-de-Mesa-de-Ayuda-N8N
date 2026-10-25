"""
Caracterizacion de la sensibilidad sobre el corpus REAL (c-142, tarea 6.6).

Test de CARACTERIZACION DE DATOS, no de TDD: no conduce codigo de produccion y por
eso no sigue el ciclo RED/GREEN. Verifica que (a) el adaptador reproduce la etapa
evaluada (131 cortocircuitados, 97 aciertos) y (b) la replica historica reproduce la
linea base que documento c-71. SKIPPED si el corpus no esta presente.

Si (a) falla hay deriva entre el codigo y la etapa evaluada; si (b) falla, la replica
se revisa contra `git show 7925903:...` y la discrepancia se registra con su causa.
Nunca se ajusta la replica a los datos ni el valor esperado sin consultar al usuario.
"""

from __future__ import annotations

import json

import pytest

import evaluation.sensibilidad_ajustes as sa
from evaluation.deterministic_measurement import cargar_corpus_tolerante, recolectar_observaciones

pytestmark = pytest.mark.skipif(
    not sa.CORPUS_REAL_PATH.exists(), reason="el corpus real no esta presente en data/"
)


@pytest.fixture(scope="module")
def corpus():
    return cargar_corpus_tolerante(sa.CORPUS_REAL_PATH)


@pytest.fixture
def entorno_backend(monkeypatch):
    sa.asegurar_backend_en_path()
    pytest.importorskip("app.config.settings")
    for clave, valor in sa.ENTORNO_OFFLINE.items():
        monkeypatch.setenv(clave, valor)
    from app.config.settings import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _vocabulario_vigente():
    return sa.keyword_map_desde_fuente(sa.KEYWORDS_VIGENTE_PATH.read_text(encoding="utf-8"))


def _vocabulario_previo():
    return json.loads((sa.DATOS_DIR / "keywords_pre_c71.json").read_text(encoding="utf-8"))


async def test_v1_con_l1_reproduce_131_cortocircuitados_y_97_aciertos(entorno_backend, corpus):
    observaciones = await recolectar_observaciones(
        corpus, sa.clasificador_con_vocabulario(_vocabulario_vigente())
    )

    resumen = sa.resumen_cortocircuito(observaciones, sa.regla_vigente(0.5166))

    assert len(corpus) == 200
    assert (resumen.casos, resumen.aciertos) == (131, 97)


async def test_v0_con_l0_reproduce_la_linea_base_documentada_por_c71(corpus):
    observaciones = await recolectar_observaciones(
        corpus, sa.ClasificadorLegadoPreC71(_vocabulario_previo())
    )
    canal_por_caso = {c.id: c.canal_origen for c in corpus}

    filas = sa.comparar_linea_base_c71(observaciones, canal_por_caso, sa.LINEA_BASE_C71)

    reproducido = {f.metrica: f.reproducido for f in filas}
    assert reproducido == sa.LINEA_BASE_C71, [f for f in filas if not f.coincide]
