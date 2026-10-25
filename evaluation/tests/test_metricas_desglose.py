"""
Tests de las metricas puras de desglose de exactitud (c-131, D5/D6).

Strict TDD (por tarea de `tasks.md`):
    RED  -> `evaluation.metrics` no expone `aciertos_laxos`, `resumen_exactitud`,
            `desglose_exactitud`, `distribucion_confianza` ni `calibracion_por_etapa`.
    GREEN -> cada funcion minima, una por ciclo.

Exactitud laxa: el sector predicho principal pertenece al conjunto de verdad del
caso (`sector_asignado` mas `sectores_adicionales` del corpus). No es la
"pertenencia" (sector asignado dentro del conjunto predicho).

Las importaciones se hacen dentro de cada test: en la fase RED solo falla el
test cuya funcion aun no existe.
"""

from __future__ import annotations

import pytest

SIS = "Sistemas"
SW = "Soporte Tecnico Software"
HW = "Soporte Tecnico Hardware"
BD = "Bases de Datos"
SEG = "Seguridad Informatica"


# ---------------------------------------------------------------------------
# 4.1 / 4.3 aciertos_laxos
# ---------------------------------------------------------------------------
def test_laxo_cuenta_la_prediccion_principal_dentro_de_los_adicionales_de_verdad():
    from evaluation.metrics import aciertos_estrictos, aciertos_laxos

    reales = [SIS]
    predichos = [SW]
    verdad = [frozenset({SIS, SW})]

    assert aciertos_laxos(predichos, verdad) == 1
    assert aciertos_estrictos(reales, predichos) == 0


def test_laxo_no_cuenta_una_prediccion_fuera_del_conjunto_de_verdad():
    from evaluation.metrics import aciertos_laxos

    assert aciertos_laxos([BD], [frozenset({SIS, SW})]) == 0


@pytest.mark.parametrize("predicho", ["", "Otro Sector", "sistemas"])
def test_laxo_trata_prediccion_vacia_o_no_canonica_como_error(predicho):
    from evaluation.metrics import aciertos_laxos

    assert aciertos_laxos([predicho], [frozenset({SIS, SW})]) == 0


def test_laxo_y_pertenencia_se_distinguen():
    """Asignado entre los adicionales predichos, pero la principal no esta en la verdad."""
    from evaluation.metrics import aciertos_estrictos, aciertos_laxos, aciertos_pertenencia

    asignados = [SIS]
    predichos = [BD]
    adicionales_predichos = [[SIS]]
    verdad = [frozenset({SIS})]

    assert aciertos_pertenencia(asignados, predichos, adicionales_predichos) == 1
    assert aciertos_laxos(predichos, verdad) == 0
    assert aciertos_estrictos(asignados, predichos) == 0


def _lista_mixta():
    """Seis casos con conteos distintos: estrictos=2, laxos=4."""
    reales = [SIS, SW, HW, BD, SEG, SIS]
    predichos = [SIS, SW, SW, SEG, "", BD]
    verdad = [
        frozenset({SIS}),            # estricto
        frozenset({SW, HW}),         # estricto
        frozenset({HW, SW}),         # laxo (principal en adicionales)
        frozenset({BD, SEG}),        # laxo
        frozenset({SEG}),            # error: prediccion vacia
        frozenset({SIS, SW}),        # error: BD fuera de la verdad
    ]
    return reales, predichos, verdad


def test_laxa_es_mayor_o_igual_que_estricta_en_lista_mixta():
    from evaluation.metrics import aciertos_estrictos, aciertos_laxos

    reales, predichos, verdad = _lista_mixta()
    estrictos = aciertos_estrictos(reales, predichos)
    laxos = aciertos_laxos(predichos, verdad)

    assert (estrictos, laxos) == (2, 4)
    assert laxos >= estrictos


def test_todo_acierto_estricto_es_laxo_en_lista_mixta():
    from evaluation.metrics import aciertos_laxos

    reales, predichos, verdad = _lista_mixta()
    for real, predicho, conjunto in zip(reales, predichos, verdad):
        if real == predicho:
            assert aciertos_laxos([predicho], [conjunto]) == 1


def test_laxo_ignora_etiquetas_no_canonicas_aun_si_figuran_en_la_verdad():
    """Una verdad corrupta no convierte una etiqueta fuera de las cinco en acierto."""
    from evaluation.metrics import aciertos_laxos

    assert aciertos_laxos(["Otro Sector"], [frozenset({"Otro Sector", SIS})]) == 0
    assert aciertos_laxos([""], [frozenset({"", SIS})]) == 0


# ---------------------------------------------------------------------------
# 4.4 / 4.6 ResumenExactitud y resumen_exactitud
# ---------------------------------------------------------------------------
def _datos(n_estrictos: int, n_laxos_extra: int, n_errores: int):
    """
    Construye `n` casos: los primeros son aciertos estrictos, luego laxos (la
    prediccion cae en un adicional de verdad) y al final errores.
    """
    reales, predichos, verdad = [], [], []
    for _ in range(n_estrictos):
        reales.append(SIS)
        predichos.append(SIS)
        verdad.append(frozenset({SIS}))
    for _ in range(n_laxos_extra):
        reales.append(SIS)
        predichos.append(SW)
        verdad.append(frozenset({SIS, SW}))
    for _ in range(n_errores):
        reales.append(SIS)
        predichos.append(BD)
        verdad.append(frozenset({SIS}))
    return reales, predichos, verdad


def test_resumen_cuenta_aciertos_y_calcula_wilson_en_ambas_definiciones():
    from evaluation.metrics import intervalo_wilson, resumen_exactitud

    resumen = resumen_exactitud(*_datos(7, 2, 1))

    assert resumen.casos == 10
    assert resumen.aciertos_estrictos == 7
    assert resumen.aciertos_laxos == 9
    assert resumen.exactitud_estricta == pytest.approx(0.7)
    assert resumen.exactitud_laxa == pytest.approx(0.9)
    assert resumen.ic_estricta == intervalo_wilson(7, 10)
    assert resumen.ic_laxa == intervalo_wilson(9, 10)
    assert resumen.ic_estricta[0] <= resumen.exactitud_estricta <= resumen.ic_estricta[1]


def test_resumen_sin_casos_devuelve_none_y_nunca_el_intervalo_0_1():
    from evaluation.metrics import resumen_exactitud

    resumen = resumen_exactitud([], [], [])

    assert resumen.casos == 0
    assert resumen.aciertos_estrictos == 0
    assert resumen.aciertos_laxos == 0
    assert resumen.exactitud_estricta is None
    assert resumen.exactitud_laxa is None
    assert resumen.ic_estricta is None
    assert resumen.ic_laxa is None


def test_resumen_es_inmutable():
    import dataclasses

    from evaluation.metrics import resumen_exactitud

    resumen = resumen_exactitud(*_datos(1, 0, 0))
    with pytest.raises(dataclasses.FrozenInstanceError):
        resumen.casos = 99  # type: ignore[misc]


def test_resumen_con_otros_conteos_coincide_con_wilson_calculado_a_mano():
    from evaluation.metrics import resumen_exactitud

    # 3/7 -> 0,4286 [0,1582; 0,7495]
    chico = resumen_exactitud(*_datos(3, 0, 4))
    assert chico.exactitud_estricta == pytest.approx(0.4286, abs=5e-5)
    assert chico.ic_estricta == pytest.approx((0.1582, 0.7495), abs=5e-5)
    assert chico.exactitud_laxa == chico.exactitud_estricta

    # 50/69 -> 0,7246 [0,6095; 0,8161]
    etapa = resumen_exactitud(*_datos(50, 0, 19))
    assert etapa.casos == 69
    assert etapa.exactitud_estricta == pytest.approx(0.7246, abs=5e-5)
    assert etapa.ic_estricta == pytest.approx((0.6095, 0.8161), abs=5e-5)


def test_resumen_respeta_el_nivel_de_confianza_pedido():
    from evaluation.metrics import intervalo_wilson, resumen_exactitud

    resumen = resumen_exactitud(*_datos(7, 2, 1), confianza=0.90)

    assert resumen.ic_estricta == intervalo_wilson(7, 10, 0.90)
    # un IC al 90 % es mas angosto que el de 95 %
    ancho_95 = intervalo_wilson(7, 10)[1] - intervalo_wilson(7, 10)[0]
    assert resumen.ic_estricta[1] - resumen.ic_estricta[0] < ancho_95


# ---------------------------------------------------------------------------
# 4.7 / 4.9 desglose_exactitud y ETAPAS_PIPELINE
# ---------------------------------------------------------------------------
def _datos_etapas():
    """
    Cinco casos: 'deterministic' x3 (2 estrictos, 1 laxo), 'gemini' x2 (1 estricto,
    1 error). Ninguna prediccion de 'fallback'.
    """
    claves = ["deterministic", "deterministic", "deterministic", "gemini", "gemini"]
    reales = [SIS, SW, HW, BD, SEG]
    predichos = [SIS, SW, SW, BD, SIS]
    verdad = [
        frozenset({SIS}),
        frozenset({SW}),
        frozenset({HW, SW}),   # laxo
        frozenset({BD}),
        frozenset({SEG}),      # error
    ]
    return claves, reales, predichos, verdad


def test_etapas_del_pipeline_estan_en_el_orden_canonico():
    from evaluation.metrics import ETAPAS_PIPELINE

    assert ETAPAS_PIPELINE == ("deterministic", "gemini", "fallback")


def test_desglose_con_orden_explicito_lista_tambien_la_etapa_vacia():
    from evaluation.metrics import ETAPAS_PIPELINE, desglose_exactitud

    desglose = desglose_exactitud(*_datos_etapas(), orden=ETAPAS_PIPELINE)

    assert list(desglose) == ["deterministic", "gemini", "fallback"]
    assert (desglose["deterministic"].casos, desglose["deterministic"].aciertos_estrictos,
            desglose["deterministic"].aciertos_laxos) == (3, 2, 3)
    assert (desglose["gemini"].casos, desglose["gemini"].aciertos_estrictos,
            desglose["gemini"].aciertos_laxos) == (2, 1, 1)
    assert desglose["fallback"].casos == 0
    assert desglose["fallback"].exactitud_estricta is None
    assert desglose["fallback"].ic_laxa is None


def test_desglose_es_aditivo_respecto_del_global():
    from evaluation.metrics import ETAPAS_PIPELINE, desglose_exactitud, resumen_exactitud

    claves, reales, predichos, verdad = _datos_etapas()
    desglose = desglose_exactitud(claves, reales, predichos, verdad, orden=ETAPAS_PIPELINE)
    global_ = resumen_exactitud(reales, predichos, verdad)

    assert sum(r.casos for r in desglose.values()) == global_.casos == 5
    assert sum(r.aciertos_estrictos for r in desglose.values()) == global_.aciertos_estrictos
    assert sum(r.aciertos_laxos for r in desglose.values()) == global_.aciertos_laxos


def test_desglose_sin_orden_ordena_por_conteo_descendente():
    from evaluation.metrics import desglose_exactitud

    claves = ["b", "a", "a", "c", "a", "b"]
    reales = [SIS] * 6
    predichos = [SIS] * 6
    verdad = [frozenset({SIS})] * 6

    desglose = desglose_exactitud(claves, reales, predichos, verdad)

    assert list(desglose) == ["a", "b", "c"]
    assert [desglose[k].casos for k in desglose] == [3, 2, 1]


def test_desglose_sin_orden_desempata_alfabeticamente():
    from evaluation.metrics import desglose_exactitud

    claves = ["web", "tel", "mail", "tel", "web", "mail"]
    reales = [SIS] * 6
    predichos = [SIS] * 6
    verdad = [frozenset({SIS})] * 6

    desglose = desglose_exactitud(claves, reales, predichos, verdad)

    assert list(desglose) == ["mail", "tel", "web"]


def test_desglose_con_orden_explicito_omite_la_clave_ausente_del_orden():
    """Comportamiento declarado: solo se listan las claves de `orden`."""
    from evaluation.metrics import desglose_exactitud

    claves = ["a", "b", "b"]
    desglose = desglose_exactitud(
        claves, [SIS] * 3, [SIS] * 3, [frozenset({SIS})] * 3, orden=("b", "z")
    )

    assert list(desglose) == ["b", "z"]
    assert desglose["b"].casos == 2
    assert desglose["z"].casos == 0


# ---------------------------------------------------------------------------
# 4.10 / 4.12 distribucion_confianza y calibracion_por_etapa
# ---------------------------------------------------------------------------
def test_distribucion_agrupa_valores_redondeados_y_los_ordena_ascendente():
    from evaluation.metrics import distribucion_confianza

    confianzas = [0.5, 1 / 6, 0.1666666667, 0.5, 0.0, 0.5]
    reales = [SIS] * 6
    predichos = [SIS, BD, SIS, SIS, BD, BD]   # aciertos: 0.5 -> 2 de 3; 1/6 -> 1 de 2; 0.0 -> 0 de 1

    distribucion = distribucion_confianza(confianzas, reales, predichos)

    assert [(v.valor, v.casos, v.aciertos) for v in distribucion] == [
        (0.0, 1, 0),
        (0.1667, 2, 1),
        (0.5, 3, 2),
    ]
    assert sum(v.casos for v in distribucion) == len(confianzas)


def test_distribucion_respeta_los_decimales_pedidos():
    from evaluation.metrics import distribucion_confianza

    distribucion = distribucion_confianza([0.123, 0.124], [SIS, SIS], [SIS, SIS], decimales=2)

    assert [(v.valor, v.casos) for v in distribucion] == [(0.12, 2)]


def test_distribucion_vacia_devuelve_lista_vacia():
    from evaluation.metrics import distribucion_confianza

    assert distribucion_confianza([], [], []) == []


def _datos_calibracion_por_etapa():
    """Composicion de juguete: deterministica 0 / 0,5 / 0,75 / 1,0; Gemini 0,85 / 0,90 / 0,95."""
    etapas = ["deterministic"] * 6 + ["gemini"] * 5
    confianzas = [0.0, 0.0, 0.5, 0.75, 0.75, 1.0, 0.85, 0.85, 0.90, 0.95, 0.95]
    ok = [True, False, True, False, True, True, True, False, True, True, False]
    reales = [SIS] * 11
    predichos = [SIS if acierto else BD for acierto in ok]
    return confianzas, reales, predichos, etapas


def test_calibracion_por_etapa_lista_las_etapas_en_orden_con_sus_bandas():
    from evaluation.metrics import ETAPAS_PIPELINE, calibracion_por_etapa

    resultado = calibracion_por_etapa(*_datos_calibracion_por_etapa())

    assert list(resultado) == list(ETAPAS_PIPELINE)
    det = {b.limite_inferior: (b.total, b.aciertos) for b in resultado["deterministic"]}
    gem = {b.limite_inferior: (b.total, b.aciertos) for b in resultado["gemini"]}
    assert det == {0.0: (2, 1), 0.5: (1, 1), 0.7: (2, 1), 0.85: (0, 0), 0.95: (1, 1)}
    assert gem == {0.0: (0, 0), 0.5: (0, 0), 0.7: (0, 0), 0.85: (3, 2), 0.95: (2, 1)}


def test_calibracion_por_etapa_suma_la_banda_global():
    from evaluation.metrics import calibracion_por_bandas, calibracion_por_etapa

    confianzas, reales, predichos, etapas = _datos_calibracion_por_etapa()
    por_etapa = calibracion_por_etapa(confianzas, reales, predichos, etapas)
    global_ = calibracion_por_bandas(confianzas, reales, predichos)

    for indice, banda_global in enumerate(global_):
        assert sum(bandas[indice].total for bandas in por_etapa.values()) == banda_global.total
        assert (
            sum(bandas[indice].aciertos for bandas in por_etapa.values())
            == banda_global.aciertos
        )


def test_calibracion_por_etapa_vacia_devuelve_bandas_en_cero():
    from evaluation.metrics import calibracion_por_etapa

    resultado = calibracion_por_etapa(*_datos_calibracion_por_etapa())

    assert [b.total for b in resultado["fallback"]] == [0, 0, 0, 0, 0]
    assert [b.aciertos for b in resultado["fallback"]] == [0, 0, 0, 0, 0]
    assert len(resultado["fallback"]) == 5


def test_calibracion_por_etapa_acepta_bandas_propias():
    from evaluation.metrics import calibracion_por_etapa

    confianzas, reales, predichos, etapas = _datos_calibracion_por_etapa()
    resultado = calibracion_por_etapa(
        confianzas, reales, predichos, etapas, bandas=((0.0, 0.7), (0.7, 1.0))
    )

    assert [(b.total, b.aciertos) for b in resultado["deterministic"]] == [(3, 2), (3, 2)]
    assert [(b.total, b.aciertos) for b in resultado["gemini"]] == [(0, 0), (5, 3)]


def _composicion_del_design():
    """Imita la composicion por etapa de `design.md` (Context): 131 deterministicas y 69 de Gemini."""
    grupos = [
        # (etapa, confianza, casos, aciertos)
        ("deterministic", 0.0, 98, 75),
        ("deterministic", 0.5, 26, 19),
        ("deterministic", 0.75, 6, 2),
        ("deterministic", 1.0, 1, 1),
        ("gemini", 0.85, 24, 18),
        ("gemini", 0.90, 7, 4),
        ("gemini", 0.95, 20, 15),
        ("gemini", 0.98, 18, 13),
    ]
    etapas, confianzas, predichos = [], [], []
    for etapa, confianza, casos, aciertos in grupos:
        for i in range(casos):
            etapas.append(etapa)
            confianzas.append(confianza)
            predichos.append(SIS if i < aciertos else BD)
    return confianzas, [SIS] * len(etapas), predichos, etapas


def test_descomposicion_por_etapa_reproduce_las_bandas_canonicas():
    from evaluation.metrics import calibracion_por_bandas, calibracion_por_etapa

    confianzas, reales, predichos, etapas = _composicion_del_design()
    por_etapa = calibracion_por_etapa(confianzas, reales, predichos, etapas)
    global_ = calibracion_por_bandas(confianzas, reales, predichos)

    assert [(b.total, b.aciertos) for b in global_] == [
        (98, 75), (26, 19), (6, 2), (31, 22), (39, 29)
    ]
    assert [(b.total, b.aciertos) for b in por_etapa["deterministic"]] == [
        (98, 75), (26, 19), (6, 2), (0, 0), (1, 1)
    ]
    assert [(b.total, b.aciertos) for b in por_etapa["gemini"]] == [
        (0, 0), (0, 0), (0, 0), (31, 22), (38, 28)
    ]


def test_distribucion_por_etapa_reproduce_la_distribucion_del_design():
    from evaluation.metrics import ETAPAS_PIPELINE, distribucion_confianza

    confianzas, reales, predichos, etapas = _composicion_del_design()
    distribuciones = {}
    for etapa in ETAPAS_PIPELINE:
        seleccion = [i for i, e in enumerate(etapas) if e == etapa]
        distribuciones[etapa] = distribucion_confianza(
            [confianzas[i] for i in seleccion],
            [reales[i] for i in seleccion],
            [predichos[i] for i in seleccion],
        )

    assert {v.valor: v.casos for v in distribuciones["deterministic"]} == {
        0.0: 98, 0.5: 26, 0.75: 6, 1.0: 1
    }
    assert {v.valor: (v.casos, v.aciertos) for v in distribuciones["gemini"]} == {
        0.85: (24, 18), 0.90: (7, 4), 0.95: (20, 15), 0.98: (18, 13)
    }
    assert distribuciones["fallback"] == []
