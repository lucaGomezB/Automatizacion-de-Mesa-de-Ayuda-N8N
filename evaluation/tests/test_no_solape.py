"""
Tests de la verificacion de no solape del corpus independiente (c-166, ECM-006).

`verificar_no_solape(ajuste, candidato)` es pura: recibe dos secuencias de
`CasoEvaluacion` y no lee archivos ni usa red. Los casos de prueba son sinteticos.
"""

from __future__ import annotations

import pytest

from evaluation import no_solape
from evaluation.corpus import CasoEvaluacion
from evaluation.no_solape import SolapeError, verificar_no_solape


def _caso(id_caso: str, descripcion: str) -> CasoEvaluacion:
    return CasoEvaluacion(id=id_caso, descripcion=descripcion, sector_asignado="Sistemas")


AJUSTE = [
    _caso("R001", "No puedo ingresar a la VPN desde casa"),
    _caso("R002", "La impresora del segundo piso no imprime"),
]


# ---------------------------------------------------------------------------
# 4.1 — Reglas basicas: prefijo, ids disjuntos, descripcion repetida
# ---------------------------------------------------------------------------
def test_un_candidato_disjunto_con_ids_I_pasa():
    candidato = [
        _caso("I001", "El servidor de correo esta caido desde la manana"),
        _caso("I002", "Necesito restaurar una copia de seguridad de la base"),
    ]

    verificar_no_solape(AJUSTE, candidato)  # no levanta


def test_un_id_del_candidato_sin_el_prefijo_I_falla_y_nombra_el_caso():
    candidato = [_caso("I001", "Caso distinto uno"), _caso("X007", "Caso distinto dos")]

    with pytest.raises(SolapeError, match="X007") as excinfo:
        verificar_no_solape(AJUSTE, candidato)

    assert "prefijo" in str(excinfo.value)


def test_un_id_presente_en_ambos_corpus_falla_y_nombra_el_id():
    ajuste = [*AJUSTE, _caso("I001", "Texto del caso uno del otro corpus")]
    candidato = [_caso("I001", "Texto completamente distinto del candidato")]

    with pytest.raises(SolapeError, match="I001") as excinfo:
        verificar_no_solape(ajuste, candidato)

    assert "ambos corpus" in str(excinfo.value)


def test_la_misma_descripcion_con_otro_id_falla_e_identifica_ambos_casos():
    candidato = [_caso("I001", "No puedo ingresar a la VPN desde casa")]

    with pytest.raises(SolapeError) as excinfo:
        verificar_no_solape(AJUSTE, candidato)

    mensaje = str(excinfo.value)
    assert "I001" in mensaje and "R001" in mensaje
    assert "descripcion" in mensaje


def test_todas_las_infracciones_se_informan_juntas():
    candidato = [
        _caso("X001", "Caso con prefijo invalido"),
        _caso("I002", "La impresora del segundo piso no imprime"),
    ]

    with pytest.raises(SolapeError) as excinfo:
        verificar_no_solape(AJUSTE, candidato)

    mensaje = str(excinfo.value)
    assert "X001" in mensaje and "I002" in mensaje and "R002" in mensaje


# ---------------------------------------------------------------------------
# 4.3 — TRIANGULATE: la comparacion usa la descripcion normalizada
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "variante",
    [
        "NO PUEDO INGRESAR A LA VPN DESDE CASA",
        "  No puedo   ingresar\ta la VPN\n desde casa  ",
        "No puedo ingresar a la \uff36\uff30\uff2e desde casa",
    ],
    ids=["mayusculas", "espacios_tabs_y_saltos", "nfkc_ancho_completo"],
)
def test_descripciones_que_solo_difieren_en_la_forma_se_consideran_la_misma(variante):
    with pytest.raises(SolapeError, match="R001"):
        verificar_no_solape(AJUSTE, [_caso("I001", variante)])


def test_descripciones_que_difieren_en_una_palabra_no_se_consideran_la_misma():
    verificar_no_solape(AJUSTE, [_caso("I001", "No puedo ingresar a la VPN desde la casa")])


# ---------------------------------------------------------------------------
# 4.4 — Advertencia opcional por similitud Jaccard (no detecta parafrasis)
# ---------------------------------------------------------------------------
CASI_IGUAL = "No puedo ingresar a la VPN desde mi casa"  # 8 de 9 palabras en comun con R001


def test_con_umbral_un_par_muy_similar_se_devuelve_como_advertencia_sin_levantar_error():
    advertencias = verificar_no_solape(AJUSTE, [_caso("I001", CASI_IGUAL)], umbral_jaccard=0.8)

    assert [(a.id_candidato, a.id_ajuste) for a in advertencias] == [("I001", "R001")]
    assert advertencias[0].similitud == pytest.approx(8 / 9)


def test_un_par_por_debajo_del_umbral_no_genera_advertencia():
    assert verificar_no_solape(AJUSTE, [_caso("I001", CASI_IGUAL)], umbral_jaccard=0.95) == []


def test_un_par_exactamente_en_el_umbral_no_es_advertencia_porque_debe_estar_por_encima():
    ajuste = [_caso("R001", "alfa beta gamma delta")]
    candidato = [_caso("I001", "alfa beta gamma epsilon")]  # Jaccard = 3 / 5

    assert verificar_no_solape(ajuste, candidato, umbral_jaccard=0.6) == []
    assert len(verificar_no_solape(ajuste, candidato, umbral_jaccard=0.59)) == 1


def test_las_advertencias_siguen_el_orden_del_candidato_y_del_ajuste():
    ajuste = [_caso("R001", "uno dos tres cuatro"), _caso("R002", "uno dos tres cinco")]
    candidato = [_caso("I001", "uno dos tres seis"), _caso("I002", "uno dos tres siete")]

    advertencias = verificar_no_solape(ajuste, candidato, umbral_jaccard=0.5)

    assert [(a.id_candidato, a.id_ajuste) for a in advertencias] == [
        ("I001", "R001"),
        ("I001", "R002"),
        ("I002", "R001"),
        ("I002", "R002"),
    ]


def test_sin_umbral_no_se_calcula_la_similitud(monkeypatch):
    def no_deberia_llamarse(*args, **kwargs):
        raise AssertionError("la similitud no se calcula sin umbral_jaccard")

    monkeypatch.setattr(no_solape, "_similitud_jaccard", no_deberia_llamarse)

    assert verificar_no_solape(AJUSTE, [_caso("I001", CASI_IGUAL)]) == []


def test_el_control_no_detecta_parafrasis_y_lo_declara():
    parafrasis = [_caso("I001", "Me resulta imposible conectarme por VPN cuando estoy en mi domicilio")]

    assert verificar_no_solape(AJUSTE, parafrasis, umbral_jaccard=0.5) == []
    documentacion = (verificar_no_solape.__doc__ or "").lower()
    assert "parafrasis" in documentacion.replace("\u00e1", "a")


def test_una_infraccion_de_id_o_de_descripcion_prevalece_sobre_las_advertencias():
    candidato = [_caso("X001", CASI_IGUAL)]

    with pytest.raises(SolapeError, match="X001"):
        verificar_no_solape(AJUSTE, candidato, umbral_jaccard=0.5)
