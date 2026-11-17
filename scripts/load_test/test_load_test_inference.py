"""Pruebas offline del arnes de carga CON inferencia paga (TASK B, c-218).

Sin red, sin Docker, sin claves. Complementa ``test_load_test.py`` (camino de
costo cero), que NO se modifica. Los valores esperados se calculan a mano y se
documentan junto a cada caso.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import load_test_inference as lti


AQUI = Path(__file__).resolve().parent
FIXTURE_INF = AQUI / "fixture_descripciones_inferencia.json"
OVERRIDE_INF = AQUI / "compose.load-test-inference.yml"


# ── etapa observada y resumen por etapa ───────────────────────────────────────


def test_etapa_observada_toma_la_primera_no_deterministica():
    assert lti.etapa_observada(["deterministic"]) == "deterministic"
    assert lti.etapa_observada(["deterministic", "gemini"]) == "gemini"
    assert lti.etapa_observada(["fallback"]) == "fallback"
    assert lti.etapa_observada([]) == "sin_registro"


def _detalle(etapa, e2e, omid):
    return {"origen_message_id": omid, "etapa": etapa, "latencia_e2e_ms": e2e}


def test_resumen_etapas_cuenta_por_etapa_y_fraccion():
    detalles = [
        _detalle("deterministic", 10.0, "a"),
        _detalle("gemini", 100.0, "b"),
        _detalle("deterministic", 11.0, "c"),
        _detalle("fallback", 50.0, "d"),
    ]
    r = lti.resumen_etapas(detalles)
    assert r["conteo_por_etapa"] == {"deterministic": 2, "gemini": 1, "fallback": 1}
    assert r["total"] == 4
    assert r["escalados"] == 2
    assert r["fraccion_escalada"] == pytest.approx(0.5)


def test_resumen_etapas_sin_detalles_no_divide_por_cero():
    r = lti.resumen_etapas([])
    assert r["total"] == 0
    assert r["fraccion_escalada"] == 0.0


# ── contribucion de la inferencia (comparacion pareada) ───────────────────────


def test_contribucion_inferencia_parte_por_etapa_con_latencia_de_cliente():
    # Deterministicos: 10 y 20 ms -> p95 = 10 + 0.95*(20-10) = 19.5.
    # Escalados:      100 y 200 ms -> p95 = 195.0. Razon = 195/19.5 = 10.
    rep = {
        "resultados": [
            {"origen_message_id": "a", "latencia_ms": 10.0, "status": 201, "error": None},
            {"origen_message_id": "b", "latencia_ms": 100.0, "status": 201, "error": None},
            {"origen_message_id": "c", "latencia_ms": 20.0, "status": 201, "error": None},
            {"origen_message_id": "d", "latencia_ms": 200.0, "status": 201, "error": None},
        ],
        "segundos": 1.0,
    }
    detalles = [
        _detalle("deterministic", 1.0, "a"),
        _detalle("gemini", 9.0, "b"),
        _detalle("deterministic", 2.0, "c"),
        _detalle("gemini", 18.0, "d"),
    ]
    r = lti.contribucion_inferencia([rep], detalles)
    assert r["deterministico"]["n"] == 2
    assert r["escalado"]["n"] == 2
    assert r["deterministico"]["p95_ms"] == pytest.approx(19.5)
    assert r["escalado"]["p95_ms"] == pytest.approx(195.0)
    assert r["razon_p95"] == pytest.approx(10.0)
    # e2e del servidor: deterministicos [1,2] -> p95 1.95; escalados [9,18] -> 17.55.
    assert r["deterministico"]["e2e_p95_ms"] == pytest.approx(1.95)
    assert r["escalado"]["e2e_p95_ms"] == pytest.approx(17.55)


def test_contribucion_inferencia_sin_subconjunto_deja_none_sin_dividir_por_cero():
    rep = {
        "resultados": [
            {"origen_message_id": "a", "latencia_ms": 10.0, "status": 201, "error": None},
        ],
        "segundos": 1.0,
    }
    detalles = [_detalle("gemini", 9.0, "a")]
    r = lti.contribucion_inferencia([rep], detalles)
    assert r["deterministico"]["n"] == 0
    assert r["deterministico"]["p95_ms"] is None
    assert r["razon_p95"] is None


# ── criterio con la condicion de inferencia ───────────────────────────────────


def _nivel(concurrencia, p95, rps, err=0.0, completo=True, det_p95=None, esc_p95=None):
    return {
        "concurrencia": concurrencia,
        "p95_ms": p95,
        "throughput_rps": rps,
        "tasa_error": err,
        "completo": completo,
        "inferencia": {
            "deterministico": {"p95_ms": det_p95},
            "escalado": {"p95_ms": esc_p95},
        },
    }


def _niveles(ratios=(3.0, 3.0, 3.0, 3.0)):
    base = [
        (1, 100.0, 10.0),
        (5, 150.0, 35.0),
        (10, 200.0, 50.0),
        (20, 300.0, 60.0),
    ]
    niveles = []
    for (c, p95, rps), razon in zip(base, ratios):
        det = 50.0
        niveles.append(_nivel(c, p95, rps, det_p95=det, esc_p95=None if razon is None else det * razon))
    return niveles


def test_criterio_inferencia_dentro_de_tolerancia_es_sostenida():
    # Tolerancia T = 4 (preregistrada): razon 3 <= 4 en todos los niveles.
    assert lti.evaluar_criterio_inferencia(_niveles()) ["veredicto"] == "sostenida"


def test_criterio_inferencia_excedida_es_no_sostenida_y_nombra_nivel():
    # Nivel 10: razon 10 > 4 -> violacion de condicion "inferencia".
    niveles = _niveles(ratios=(3.0, 3.0, 10.0, 3.0))
    r = lti.evaluar_criterio_inferencia(niveles)
    assert r["veredicto"] == "no sostenida"
    assert (10, "inferencia") in {
        (v["concurrencia"], v["condicion"]) for v in r["violaciones"]
    }


def test_criterio_inferencia_sin_datos_del_subconjunto_no_viola():
    niveles = _niveles(ratios=(None, None, None, None))
    # Sin datos de escalado (p95 None), la condicion de inferencia no aplica.
    assert lti.evaluar_criterio_inferencia(niveles)["veredicto"] == "sostenida"


def test_criterio_inferencia_hereda_las_violaciones_primarias():
    niveles = _niveles()
    niveles[2]["tasa_error"] = 0.05
    r = lti.evaluar_criterio_inferencia(niveles)
    assert r["veredicto"] == "no sostenida"
    assert (10, "tasa_error") in {
        (v["concurrencia"], v["condicion"]) for v in r["violaciones"]
    }


def test_criterio_inferencia_incompleto_es_no_concluyente():
    niveles = _niveles()
    niveles[3]["completo"] = False
    assert lti.evaluar_criterio_inferencia(niveles)["veredicto"] == "no concluyente"


def test_criterio_inferencia_niveles_faltantes_es_no_concluyente():
    assert lti.evaluar_criterio_inferencia(_niveles()[:2])["veredicto"] == "no concluyente"


# ── guarda de la corrida paga acotada ─────────────────────────────────────────


def _env(clave="AIzaSyReal-0123456789", presupuesto="0.50"):  # gitleaks:allow
    return {"GEMINI_API_KEY": clave, "COST_GUARD_BUDGET_USD": presupuesto}


def test_paga_requiere_confirmacion_explicita():
    with pytest.raises(lti.GuardaPagaError, match="confirm"):
        lti.verificar_corrida_paga_acotada(_env(), tope_usd=1.0, confirmado=False)


def test_paga_acepta_clave_real_y_presupuesto_positivo_bajo_el_tope():
    lti.verificar_corrida_paga_acotada(_env(), tope_usd=1.0, confirmado=True)  # no lanza


@pytest.mark.parametrize(
    "env",
    [
        _env(clave=lti.DUMMY_GEMINI_API_KEY),          # clave ficticia
        _env(clave=""),                                 # clave ausente
        {"COST_GUARD_BUDGET_USD": "0.5"},               # clave ausente del todo
        _env(presupuesto="0"),                          # presupuesto nulo
        _env(presupuesto="0.0"),                        # presupuesto nulo
        _env(presupuesto="-1"),                         # presupuesto negativo
        _env(presupuesto="abc"),                        # presupuesto no numerico
        _env(presupuesto="2.0"),                        # supera el tope de 1.0
    ],
)
def test_paga_rechaza_configuraciones_inseguras(env):
    with pytest.raises(lti.GuardaPagaError):
        lti.verificar_corrida_paga_acotada(env, tope_usd=1.0, confirmado=True)


def test_paga_no_filtra_la_clave_real_en_el_mensaje():
    clave = "AIzaSyREAL-0123456789"  # gitleaks:allow
    # El presupuesto supera el tope: la guarda aborta y no debe citar la clave.
    with pytest.raises(lti.GuardaPagaError) as info:
        lti.verificar_corrida_paga_acotada(
            _env(clave=clave, presupuesto="9.0"), tope_usd=1.0, confirmado=True
        )
    assert clave not in str(info.value)


def test_main_paga_aborta_sin_confirmacion_y_no_envia_nada():
    llamadas = []
    codigo = lti.main(
        [],
        leer_env=lambda servicio: _env(),
        correr=lambda args: llamadas.append(args) or 0,
    )
    assert codigo == 6
    assert llamadas == []


def test_main_paga_corre_con_confirmacion_valida():
    llamadas = []
    codigo = lti.main(
        ["--confirm-paid"],
        leer_env=lambda servicio: _env(),
        correr=lambda args: llamadas.append(args) or 0,
    )
    assert codigo == 0
    assert len(llamadas) == 1


def test_main_paga_aborta_si_la_guarda_falla_aunque_confirme():
    llamadas = []
    codigo = lti.main(
        ["--confirm-paid"],
        leer_env=lambda servicio: _env(clave=lti.DUMMY_GEMINI_API_KEY),
        correr=lambda args: llamadas.append(args) or 0,
    )
    assert codigo == 6
    assert llamadas == []


# ── fixture mixta y override de compose ───────────────────────────────────────


def test_fixture_inferencia_es_valida_y_mezcla_ambos_grupos():
    casos = lti.cargar_fixture_inferencia(FIXTURE_INF)
    assert len(casos) >= 8
    assert len({c["id"] for c in casos}) == len(casos)
    assert all(len(c["descripcion"]) >= 10 for c in casos)
    escalan = [c for c in casos if c["escala_esperada"]]
    assert 0 < len(escalan) < len(casos)  # hay mezcla real de ambos grupos


def test_cargar_fixture_inferencia_rechaza_falta_de_etiqueta(tmp_path):
    ruta = tmp_path / "f.json"
    ruta.write_text(
        json.dumps({"casos": [{"id": "X", "descripcion": "descripcion larga valida"}]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="escala_esperada"):
        lti.cargar_fixture_inferencia(ruta)


def test_override_inferencia_no_es_costo_cero_y_hereda_la_clave():
    import re

    texto = OVERRIDE_INF.read_text(encoding="utf-8")
    # Inyecta un presupuesto positivo y NO fija la clave ficticia del camino de
    # costo cero; la clave real la hereda de `env_file` (App/Backend/.env). El
    # override NO define `GEMINI_API_KEY` como variable de entorno (solo la
    # menciona en el comentario explicativo).
    assert "COST_GUARD_BUDGET_USD" in texto
    assert "load-test-dummy-gemini-key-not-real" not in texto
    assert not re.search(r"(?m)^\s*GEMINI_API_KEY\s*:", texto)


def test_parser_paga_acepta_las_banderas_del_camino_pago():
    args = lti._parser().parse_args(
        ["--confirm-paid", "--tope-usd", "0.75", "--fixture", "x.json"]
    )
    assert args.confirm_paid is True
    assert args.tope_usd == pytest.approx(0.75)
    assert args.fixture == "x.json"
