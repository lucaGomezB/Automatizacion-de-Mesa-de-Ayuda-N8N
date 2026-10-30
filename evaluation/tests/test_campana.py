"""
Tests del analisis de la campana (c-167, evaluation/campana.py).

Secciones, en el orden de las tareas: (3) registro de sujetos y referencia, (4) exactitud del
brazo manual, (5) tasa de intervencion humana, (6) efecto de orden de condicion y de posicion
y (7) evaluacion fuera de muestra. Todo corre sin red ni Gemini sobre fixtures SINTETICOS
(`tests/fixtures/campana/`, ver `tests/fixtures/README.md`); el corpus se carga desde una copia
en `tmp_path` porque `cargar_corpus` puede reescribir `metadata.total_casos`.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
import math
import pathlib
import random
import warnings
from datetime import datetime, timedelta, timezone

import pytest

from evaluation import brazo_manual, campana
from evaluation.brazo_manual import desvios_respecto_del_plan, reconstruir_posicion_real
from evaluation.campana import (
    analizar_intervencion,
    CasoReferencia,
    construir_referencia,
    contraste_independiente,
    contraste_pareado,
    CorridaCruzada,
    duraciones_brazo_manual,
    efecto_orden,
    evaluar_fuera_de_muestra,
    exactitud_brazo_manual,
    FueraDeMuestraError,
    proporcion_tiempo_intervencion,
    Referencia,
    REFERENCIA_CONSENSO_NUEVO,
    REFERENCIA_CONSENSO_ORIGINAL,
    RegistroSujetosError,
    tasa_intervencion_humana,
    validar_registro_sujetos,
)
from evaluation.corpus import cargar_corpus
from evaluation.metrics import (
    ETAPAS_PIPELINE,
    NIVEL_CONFIANZA,
    REMUESTREOS_BOOTSTRAP,
    SEMILLA_BOOTSTRAP,
    intervalo_wilson,
    percentil_intervalo,
    remuestreos_indices,
)
from evaluation.plan_campana import AsignacionCaso, leer_plan_csv, subplan
from evaluation.run_evaluation import Prediccion, cargar_predicciones
from evaluation.stats import ARE_WILCOXON_MINIMA, efecto_minimo_detectable
from evaluation.tests import helpers_campana as h

SEG = "Seguridad Informatica"
HW = "Soporte Tecnico Hardware"
SW = "Soporte Tecnico Software"
BD = "Bases de Datos"
SIS = "Sistemas"


@pytest.fixture
def planilla() -> list[dict[str, str]]:
    """Planilla SINTETICA de C1 con las dos tareas (doble etiquetado y brazo manual)."""
    return h.leer_csv(h.PLANILLA)


@pytest.fixture
def registro() -> list[dict[str, str]]:
    """Registro de sujetos SINTETICO valido (una persona por alias, un rol por persona)."""
    return h.leer_csv(h.REGISTRO_SUJETOS)


@pytest.fixture
def corpus(tmp_path):
    return cargar_corpus(h.copiar_fixture(h.CORPUS_CAMPANA, tmp_path))


# ---------------------------------------------------------------------------
# 3.1 — una misma persona con dos roles bajo dos alias se rechaza por persona
# ---------------------------------------------------------------------------
def test_la_misma_persona_operador_y_etiquetador_bajo_dos_alias_falla_nombrando_todo(planilla):
    registro_con_solape = h.leer_csv(h.REGISTRO_SUJETOS_SOLAPE)

    with pytest.raises(ValueError) as excinfo:
        validar_registro_sujetos(registro_con_solape, planilla)

    mensaje = str(excinfo.value)
    assert "P3" in mensaje
    assert "E2" in mensaje and "O1" in mensaje
    assert "etiquetador" in mensaje and "operador" in mensaje


# ---------------------------------------------------------------------------
# 3.3 — triangulacion del registro de sujetos
# ---------------------------------------------------------------------------
def _sin_alias(registro: list[dict[str, str]], alias: str) -> list[dict[str, str]]:
    return [fila for fila in registro if fila["alias"] != alias]


def _con_rol(registro: list[dict[str, str]], alias: str, rol: str) -> list[dict[str, str]]:
    return [dict(fila, rol=rol) if fila["alias"] == alias else fila for fila in registro]


def test_un_registro_valido_no_falla_y_devuelve_los_alias_verificados_de_la_planilla(registro, planilla):
    assert validar_registro_sujetos(registro, planilla) == ("E1", "E2", "O1", "O2")


def test_el_error_es_un_value_error_propio_del_registro(registro, planilla):
    with pytest.raises(RegistroSujetosError):
        validar_registro_sujetos(_sin_alias(registro, "O2"), planilla)
    assert issubclass(RegistroSujetosError, ValueError)


def test_un_alias_con_dos_roles_falla_y_nombra_alias_y_roles(registro, planilla):
    doble_rol = registro + [{"alias": "O1", "rol": "etiquetador", "persona": "P3"}]

    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(doble_rol, planilla)

    mensaje = str(excinfo.value)
    assert "O1" in mensaje and "etiquetador" in mensaje and "operador" in mensaje


def test_un_alias_con_dos_personas_falla_y_nombra_alias_y_personas(registro, planilla):
    dos_personas = registro + [{"alias": "O1", "rol": "operador", "persona": "P9"}]

    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(dos_personas, planilla)

    mensaje = str(excinfo.value)
    assert "O1" in mensaje and "P3" in mensaje and "P9" in mensaje


def test_un_alias_de_la_planilla_que_no_figura_en_el_registro_falla_y_lo_nombra(registro, planilla):
    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(_sin_alias(registro, "O2"), planilla)

    mensaje = str(excinfo.value)
    assert "O2" in mensaje and "no figura en el registro_sujetos" in mensaje


def test_e1_con_rol_operador_falla_por_rol_incompatible_con_su_tarea(registro, planilla):
    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(_con_rol(registro, "E1", "operador"), planilla)

    mensaje = str(excinfo.value)
    assert "E1" in mensaje and "doble_etiquetado" in mensaje
    assert "deberia ser etiquetador" in mensaje


@pytest.mark.parametrize("rol", ["analista_original", "autor"])
def test_un_alias_de_la_planilla_cuya_persona_es_analista_original_o_autor_falla(registro, planilla, rol):
    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(_con_rol(registro, "E1", rol), planilla)

    mensaje = str(excinfo.value)
    assert "E1" in mensaje and "P1" in mensaje and rol in mensaje


def test_una_persona_con_un_alias_en_la_planilla_y_otro_de_analista_original_falla(registro, planilla):
    mismo_sujeto = registro + [{"alias": "AN3", "rol": "analista_original", "persona": "P1"}]

    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(mismo_sujeto, planilla)

    mensaje = str(excinfo.value)
    assert "P1" in mensaje and "E1" in mensaje and "AN3" in mensaje
    assert "etiquetador" in mensaje and "analista_original" in mensaje


def test_un_rol_desconocido_falla_y_nombra_alias_y_rol(registro, planilla):
    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(_con_rol(registro, "AU1", "revisor"), planilla)

    mensaje = str(excinfo.value)
    assert "AU1" in mensaje and "revisor" in mensaje


def test_una_persona_vacia_falla_y_nombra_el_alias(registro, planilla):
    sin_persona = [dict(fila, persona="") if fila["alias"] == "AN2" else fila for fila in registro]

    with pytest.raises(RegistroSujetosError, match="AN2"):
        validar_registro_sujetos(sin_persona, planilla)


def test_una_columna_faltante_en_el_registro_falla_y_la_nombra(registro, planilla):
    sin_persona = [{"alias": fila["alias"], "rol": fila["rol"]} for fila in registro]

    with pytest.raises(RegistroSujetosError, match="persona"):
        validar_registro_sujetos(sin_persona, planilla)


def test_todos_los_problemas_se_informan_juntos(registro, planilla):
    roto = _sin_alias(registro, "O2") + [{"alias": "O9", "rol": "etiquetador", "persona": "P3"}]

    with pytest.raises(RegistroSujetosError) as excinfo:
        validar_registro_sujetos(roto, planilla)

    mensaje = str(excinfo.value)
    assert "O2" in mensaje  # alias de la planilla sin registrar
    assert "P3" in mensaje and "O9" in mensaje  # persona con dos roles bajo dos alias


def test_las_filas_repetidas_exactas_del_registro_no_cuentan_como_conflicto(registro, planilla):
    repetido = registro + [dict(registro[0])]

    assert validar_registro_sujetos(repetido, planilla) == ("E1", "E2", "O1", "O2")


# ---------------------------------------------------------------------------
# 3.4 — referencia por defecto: el consenso del doble etiquetado nuevo
# ---------------------------------------------------------------------------
def test_la_referencia_nueva_trae_solo_los_casos_donde_e1_y_e2_coinciden(planilla):
    referencia = construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla)

    assert referencia.rotulo == "consenso_doble_etiquetado"
    assert len(referencia.casos) == 20
    assert set(referencia.casos).isdisjoint({"S04", "S11", "S17", "S21"})


def test_el_conjunto_de_verdad_es_el_sector_consensuado_mas_la_interseccion_de_adicionales(planilla):
    casos = construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla).casos

    assert casos["S01"].sector == SEG and casos["S01"].conjunto_verdad == {SEG}
    # S06: E1 y E2 marcan Sistemas como adicional -> entra.
    assert casos["S06"].conjunto_verdad == {SEG, SIS}
    # S07: solo E1 marca Software como adicional -> la interseccion lo deja afuera.
    assert casos["S07"].conjunto_verdad == {HW}
    # S22: ambos marcan Software como adicional -> entra.
    assert casos["S22"].conjunto_verdad == {HW, SW}


def test_el_consenso_nuevo_puede_diferir_del_sector_asignado_original(planilla, corpus):
    casos = construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla).casos
    original = {caso.id: caso.sector_asignado for caso in corpus}

    assert casos["S08"].sector == HW and original["S08"] == SW
    assert casos["S15"].sector == BD and original["S15"] == SIS


def test_declara_conteo_e_ids_de_los_discordantes_con_la_advertencia_de_sesgo(planilla):
    referencia = construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla)

    assert referencia.discordantes == ("S04", "S11", "S17", "S21")
    assert referencia.n_discordantes == 4
    advertencias = " ".join(referencia.advertencias)
    assert "casos faciles" in advertencias and "sobrestimar" in advertencias


def test_la_referencia_no_depende_del_orden_de_las_filas_de_la_planilla(planilla):
    assert construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=list(reversed(planilla))) == (
        construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla)
    )


def test_la_referencia_nueva_exige_la_planilla_de_doble_etiquetado():
    with pytest.raises(ValueError, match="doble_etiquetado"):
        construir_referencia(REFERENCIA_CONSENSO_NUEVO)


def test_un_rotulo_de_referencia_desconocido_falla_y_lista_los_validos(planilla):
    with pytest.raises(ValueError) as excinfo:
        construir_referencia("consenso_inventado", doble_etiquetado=planilla)

    mensaje = str(excinfo.value)
    assert "consenso_inventado" in mensaje
    assert REFERENCIA_CONSENSO_NUEVO in mensaje and REFERENCIA_CONSENSO_ORIGINAL in mensaje


# ---------------------------------------------------------------------------
# 3.5 — referencia alternativa: el consenso original del corpus
# ---------------------------------------------------------------------------
def test_la_referencia_original_devuelve_sector_asignado_y_conjunto_de_verdad_del_corpus(corpus):
    referencia = construir_referencia(REFERENCIA_CONSENSO_ORIGINAL, corpus=corpus)

    assert referencia.rotulo == "consenso_original"
    assert len(referencia.casos) == 24
    assert referencia.casos["S08"].sector == SW
    assert referencia.casos["S04"].sector == BD
    assert referencia.casos["S04"].conjunto_verdad == {BD, SIS}
    assert referencia.casos["S22"].conjunto_verdad == {HW, SW}
    assert all(
        referencia.casos[caso.id].conjunto_verdad == caso.conjunto_verdad for caso in corpus
    )


def test_la_referencia_original_no_excluye_ningun_caso_por_discordancia(corpus):
    referencia = construir_referencia(REFERENCIA_CONSENSO_ORIGINAL, corpus=corpus)

    assert referencia.discordantes == ()
    assert referencia.n_discordantes == 0
    assert not any("sobrestimar" in advertencia for advertencia in referencia.advertencias)


def test_la_referencia_original_exige_el_corpus():
    with pytest.raises(ValueError, match="corpus"):
        construir_referencia(REFERENCIA_CONSENSO_ORIGINAL)


# ---------------------------------------------------------------------------
# 4.1 — exactitud estricta y laxa por operador sobre los casos que cada uno etiqueto
# ---------------------------------------------------------------------------
# Numeros verificados por separado con un script independiente sobre los fixtures:
#   consenso nuevo: O1 evalua 15 casos (10 estrictos, 11 laxos), O2 evalua 15 (11 y 13);
#   quedan afuera los discordantes S04, S11, S17 y S21 (3 de cada operador).
@pytest.fixture
def referencia_nueva(planilla):
    return construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla)


def test_exactitud_estricta_y_laxa_por_operador_con_wilson_y_nivel_declarado(
    planilla, registro, referencia_nueva
):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro)

    o1, o2 = resultado.por_operador["O1"], resultado.por_operador["O2"]
    assert list(resultado.por_operador) == ["O1", "O2"]
    assert (o1.casos, o1.aciertos_estrictos, o1.aciertos_laxos) == (15, 10, 11)
    assert (o2.casos, o2.aciertos_estrictos, o2.aciertos_laxos) == (15, 11, 13)
    assert o1.exactitud_estricta == pytest.approx(10 / 15, abs=1e-12)
    assert o1.ic_estricta == pytest.approx(intervalo_wilson(10, 15), abs=1e-12)
    assert o2.ic_laxa == pytest.approx(intervalo_wilson(13, 15), abs=1e-12)
    assert resultado.nivel_confianza == 0.95


def test_la_salida_declara_la_referencia_usada(planilla, registro, referencia_nueva):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro)

    assert resultado.referencia_usada == "consenso_doble_etiquetado"


def test_la_salida_declara_la_cobertura_de_cada_operador(planilla, registro, referencia_nueva):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro)

    cobertura = {c.id_etiquetador: c for c in resultado.cobertura}
    assert [c.id_etiquetador for c in resultado.cobertura] == ["O1", "O2"]
    for operador in ("O1", "O2"):
        assert cobertura[operador].etiquetados == 18
        assert cobertura[operador].compartidos == 12
        assert cobertura[operador].exclusivos == 6
        assert cobertura[operador].evaluados == 15
        assert cobertura[operador].excluidos_por_discordancia == 3


# ---------------------------------------------------------------------------
# 4.3 — triangulacion: laxa mayor que estricta, casos exclusivos y discordantes
# ---------------------------------------------------------------------------
def _fila(id_caso: str, operador: str, sector: str, adicionales: str = "") -> dict[str, str]:
    return {
        "id_caso": id_caso,
        "id_etiquetador": operador,
        "tarea": "brazo_manual",
        "sector_etiquetado": sector,
        "sectores_adicionales_etiquetados": adicionales,
        "inicio": "2026-11-17T10:00:00-03:00",
        "timestamp": "2026-11-17T10:01:00-03:00",
    }


def _referencia(casos: dict[str, tuple[str, set[str]]], discordantes: tuple[str, ...] = ()) -> Referencia:
    return Referencia(
        rotulo=REFERENCIA_CONSENSO_NUEVO,
        casos={
            id_caso: CasoReferencia(id_caso, sector, frozenset({sector, *extra}))
            for id_caso, (sector, extra) in casos.items()
        },
        discordantes=discordantes,
        advertencias=(),
    )


def test_la_exactitud_laxa_puede_superar_a_la_estricta(registro):
    referencia = _referencia({"A": (SEG, {SIS}), "B": (HW, set())})
    planilla = [_fila("A", "O1", SIS), _fila("B", "O1", HW), _fila("A", "O2", SEG), _fila("B", "O2", HW)]

    resultado = exactitud_brazo_manual(planilla, referencia, registro)

    o1 = resultado.por_operador["O1"]
    assert (o1.aciertos_estrictos, o1.aciertos_laxos) == (1, 2)
    assert o1.exactitud_laxa > o1.exactitud_estricta
    o2 = resultado.por_operador["O2"]
    assert (o2.aciertos_estrictos, o2.aciertos_laxos) == (2, 2)


def test_un_caso_exclusivo_de_o1_no_cuenta_como_error_de_o2(registro):
    referencia = _referencia({"A": (SEG, set()), "B": (HW, set()), "C": (SW, set())})
    planilla = [
        _fila("A", "O1", SEG), _fila("B", "O1", HW),   # O1 etiqueta A y B
        _fila("A", "O2", SEG), _fila("C", "O2", SW),   # O2 etiqueta A y C; B no es suyo
    ]

    resultado = exactitud_brazo_manual(planilla, referencia, registro)

    o2 = resultado.por_operador["O2"]
    assert o2.casos == 2 and o2.aciertos_estrictos == 2 and o2.exactitud_estricta == 1.0
    cobertura = {c.id_etiquetador: c for c in resultado.cobertura}
    assert (cobertura["O1"].etiquetados, cobertura["O1"].compartidos, cobertura["O1"].exclusivos) == (2, 1, 1)
    assert (cobertura["O2"].etiquetados, cobertura["O2"].compartidos, cobertura["O2"].exclusivos) == (2, 1, 1)


def test_hay_advertencia_de_coberturas_distintas_cuando_hay_casos_exclusivos(registro):
    referencia = _referencia({"A": (SEG, set()), "B": (HW, set())})
    planilla = [_fila("A", "O1", SEG), _fila("B", "O2", HW)]

    resultado = exactitud_brazo_manual(planilla, referencia, registro)

    assert any("mezcla operador con dificultad de los casos" in a for a in resultado.advertencias)


def test_sin_casos_exclusivos_no_hay_advertencia_de_coberturas(registro):
    referencia = _referencia({"A": (SEG, set())})
    planilla = [_fila("A", "O1", SEG), _fila("A", "O2", SEG)]

    resultado = exactitud_brazo_manual(planilla, referencia, registro)

    assert resultado.advertencias == ()


def test_los_casos_discordantes_se_excluyen_de_la_exactitud_y_se_cuentan(planilla, registro, referencia_nueva):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro)

    assert resultado.discordantes == ("S04", "S11", "S17", "S21")
    assert resultado.n_discordantes == 4
    # O1 etiqueto 18 casos y 3 son discordantes (S04, S11, S17): evalua 15.
    assert resultado.por_operador["O1"].casos == 15
    assert {c.id_etiquetador: c.excluidos_por_discordancia for c in resultado.cobertura} == {"O1": 3, "O2": 3}
    assert any("casos faciles" in advertencia for advertencia in resultado.advertencias)


def test_un_caso_que_la_referencia_no_conoce_falla_y_nombra_caso_y_operador(registro):
    referencia = _referencia({"A": (SEG, set())})
    planilla = [_fila("A", "O1", SEG), _fila("Z", "O1", HW)]

    with pytest.raises(ValueError) as excinfo:
        exactitud_brazo_manual(planilla, referencia, registro)

    mensaje = str(excinfo.value)
    assert "Z" in mensaje and "O1" in mensaje and "consenso_doble_etiquetado" in mensaje


def test_un_registro_repetido_para_caso_y_operador_falla(registro):
    referencia = _referencia({"A": (SEG, set())})
    planilla = [_fila("A", "O1", SEG), _fila("A", "O1", HW)]

    with pytest.raises(ValueError, match="mas de un registro") as excinfo:
        exactitud_brazo_manual(planilla, referencia, registro)

    assert "A" in str(excinfo.value) and "O1" in str(excinfo.value)


def test_un_sector_no_canonico_del_operador_falla(registro):
    referencia = _referencia({"A": (SEG, set())})

    with pytest.raises(ValueError, match="Redes"):
        exactitud_brazo_manual([_fila("A", "O1", "Redes")], referencia, registro)


def test_sin_filas_de_brazo_manual_falla(planilla, registro, referencia_nueva):
    solo_doble = [f for f in planilla if f["tarea"] == "doble_etiquetado"]

    with pytest.raises(ValueError, match="brazo_manual"):
        exactitud_brazo_manual(solo_doble, referencia_nueva, registro)


def test_el_solape_de_sujetos_aborta_antes_de_reportar_exactitud(planilla, referencia_nueva):
    registro_con_solape = h.leer_csv(h.REGISTRO_SUJETOS_SOLAPE)

    with pytest.raises(RegistroSujetosError):
        exactitud_brazo_manual(planilla, referencia_nueva, registro_con_solape)


# ---------------------------------------------------------------------------
# 4.4 — exactitud agregada: aciertos / etiquetas sobre la union, bootstrap por caso
# ---------------------------------------------------------------------------
# Union de casos de la referencia nueva etiquetados por algun operador: 20 casos, 30 etiquetas
# (10 compartidos x 2 + 5 exclusivos de O1 + 5 de O2), 21 aciertos estrictos y 24 laxos.
def test_la_agregada_es_aciertos_sobre_etiquetas_de_la_union_de_casos(planilla, registro, referencia_nueva):
    agregada = exactitud_brazo_manual(planilla, referencia_nueva, registro).agregada

    assert (agregada.casos, agregada.etiquetas) == (20, 30)
    assert (agregada.aciertos_estrictos, agregada.aciertos_laxos) == (21, 24)
    assert agregada.exactitud_estricta == pytest.approx(21 / 30, abs=1e-12)
    assert agregada.exactitud_laxa == pytest.approx(24 / 30, abs=1e-12)


def test_el_ic_agregado_no_es_wilson_sobre_el_total_de_etiquetas(planilla, registro, referencia_nueva):
    agregada = exactitud_brazo_manual(planilla, referencia_nueva, registro).agregada

    wilson = intervalo_wilson(21, 30)
    assert agregada.ic_estricta != pytest.approx(wilson, abs=1e-6)
    assert agregada.metodo_ic == "bootstrap percentil por caso"
    assert (agregada.semilla, agregada.remuestreos) == (SEMILLA_BOOTSTRAP, REMUESTREOS_BOOTSTRAP)
    assert agregada.nivel_confianza == NIVEL_CONFIANZA
    inferior, superior = agregada.ic_estricta
    assert inferior < agregada.exactitud_estricta < superior


def test_el_ic_agregado_coincide_con_una_recomputacion_independiente_por_caso(
    planilla, registro, referencia_nueva
):
    # Cada caso aporta (aciertos estrictos, aciertos laxos, etiquetas) de los operadores que lo
    # etiquetaron; se remuestrean los casos (ordenados por id) con la semilla del paquete.
    por_caso: dict[str, list[int]] = {}
    for fila in planilla:
        caso = referencia_nueva.casos.get(fila["id_caso"])
        if fila["tarea"] != "brazo_manual" or caso is None:
            continue
        unidad = por_caso.setdefault(fila["id_caso"], [0, 0, 0])
        unidad[0] += fila["sector_etiquetado"] == caso.sector
        unidad[1] += fila["sector_etiquetado"] in caso.conjunto_verdad
        unidad[2] += 1
    unidades = [por_caso[caso] for caso in sorted(por_caso)]
    estrictas, laxas = [], []
    generador = random.Random(SEMILLA_BOOTSTRAP)
    for indices in remuestreos_indices(generador, len(unidades), REMUESTREOS_BOOTSTRAP):
        etiquetas = sum(unidades[i][2] for i in indices)
        estrictas.append(sum(unidades[i][0] for i in indices) / etiquetas)
        laxas.append(sum(unidades[i][1] for i in indices) / etiquetas)

    agregada = exactitud_brazo_manual(planilla, referencia_nueva, registro).agregada

    assert agregada.ic_estricta == pytest.approx(percentil_intervalo(estrictas, NIVEL_CONFIANZA), abs=1e-12)
    assert agregada.ic_laxa == pytest.approx(percentil_intervalo(laxas, NIVEL_CONFIANZA), abs=1e-12)


def test_el_ic_agregado_es_reproducible(planilla, registro, referencia_nueva):
    primera = exactitud_brazo_manual(planilla, referencia_nueva, registro).agregada
    segunda = exactitud_brazo_manual(list(reversed(planilla)), referencia_nueva, registro).agregada

    assert primera == segunda


def test_la_agregada_de_un_solo_caso_con_dos_etiquetas_es_estimable(registro):
    referencia = _referencia({"A": (SEG, set())})
    planilla = [_fila("A", "O1", SEG), _fila("A", "O2", HW)]

    agregada = exactitud_brazo_manual(planilla, referencia, registro).agregada

    assert (agregada.casos, agregada.etiquetas, agregada.aciertos_estrictos) == (1, 2, 1)
    assert agregada.exactitud_estricta == 0.5


def test_sin_casos_evaluables_no_hay_agregada(registro):
    referencia = _referencia({}, discordantes=("A",))
    planilla = [_fila("A", "O1", SEG)]

    resultado = exactitud_brazo_manual(planilla, referencia, registro)

    assert resultado.agregada is None
    assert resultado.por_operador["O1"].casos == 0
    assert resultado.por_operador["O1"].exactitud_estricta is None


# ---------------------------------------------------------------------------
# 4.5 — McNemar por operador contra la prediccion v9 (leida de predicciones.json)
# ---------------------------------------------------------------------------
# Verificado con un script independiente sobre los fixtures (acierto estricto contra la
# referencia nueva; a = acierta solo el operador, b = acierta solo v9):
#   O1: ambas 6, solo operador 4, solo v9 5, ninguna 0  -> p exacto 1,0
#   O2: ambas 6, solo operador 5, solo v9 3, ninguna 1  -> p exacto 93/128
@pytest.fixture
def predicciones_v9():
    return cargar_predicciones(h.PREDICCIONES_IN_SAMPLE)


def _prediccion(caso_id: str, sector_predicho: str) -> Prediccion:
    return Prediccion(
        caso_id=caso_id,
        descripcion="Sintetico",
        sector_asignado=sector_predicho,
        sector_predicho=sector_predicho,
        confianza=0.9,
        etapa="gemini",
    )


def test_mcnemar_por_operador_pareado_contra_la_prediccion_v9(
    planilla, registro, referencia_nueva, predicciones_v9
):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro, predicciones=predicciones_v9)

    contrastes = {c.id_etiquetador: c for c in resultado.contraste_vs_automatizado}
    assert list(contrastes) == ["O1", "O2"]
    o1, o2 = contrastes["O1"].mcnemar, contrastes["O2"].mcnemar
    assert (o1.ambas, o1.solo_a, o1.solo_b, o1.ninguna) == (6, 4, 5, 0)
    assert (o2.ambas, o2.solo_a, o2.solo_b, o2.ninguna) == (6, 5, 3, 1)
    assert o1.pares == o2.pares == 15
    assert o1.criterio == o2.criterio == "exacto"
    assert o1.p_primario == pytest.approx(1.0, abs=1e-12)
    assert o2.p_primario == pytest.approx(93 / 128, abs=1e-12)


def test_el_pareo_es_por_caso_y_operador(planilla, registro, referencia_nueva, predicciones_v9):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro, predicciones=predicciones_v9)

    contrastes = {c.id_etiquetador: c for c in resultado.contraste_vs_automatizado}
    pares_o1 = contrastes["O1"].pares_clave
    assert len(pares_o1) == 15
    assert all(operador == "O1" for _, operador in pares_o1)
    assert [caso for caso, _ in pares_o1] == sorted(caso for caso, _ in pares_o1)
    assert ("S04", "O1") not in pares_o1  # discordante: fuera de la referencia


def test_el_archivo_de_predicciones_conserva_su_sha256(planilla, registro, referencia_nueva):
    antes = hashlib.sha256(h.PREDICCIONES_IN_SAMPLE.read_bytes()).hexdigest()

    exactitud_brazo_manual(
        planilla, referencia_nueva, registro, predicciones=cargar_predicciones(h.PREDICCIONES_IN_SAMPLE)
    )

    assert hashlib.sha256(h.PREDICCIONES_IN_SAMPLE.read_bytes()).hexdigest() == antes


def test_la_exactitud_de_v9_contra_la_referencia_nueva_es_un_numero_nuevo_y_rotulado(
    planilla, registro, referencia_nueva, predicciones_v9
):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro, predicciones=predicciones_v9)

    v9 = resultado.automatizado
    assert (v9.casos, v9.aciertos_estrictos, v9.aciertos_laxos) == (20, 14, 14)
    assert v9.ic_estricta == pytest.approx(intervalo_wilson(14, 20), abs=1e-12)
    assert "consenso_doble_etiquetado" in resultado.nota_automatizado
    assert "numero nuevo" in resultado.nota_automatizado
    assert "no reemplaza" in resultado.nota_automatizado


def test_sin_predicciones_no_hay_contraste_ni_exactitud_de_v9(planilla, registro, referencia_nueva):
    resultado = exactitud_brazo_manual(planilla, referencia_nueva, registro)

    assert resultado.contraste_vs_automatizado == ()
    assert resultado.automatizado is None
    assert resultado.nota_automatizado is None


# ---------------------------------------------------------------------------
# 4.6 — triangulacion: McNemar no aplicable y referencia alternativa
# ---------------------------------------------------------------------------
def test_un_operador_sin_discordancias_con_la_prediccion_da_mcnemar_no_aplicable(registro):
    referencia = _referencia({"A": (SEG, set()), "B": (HW, set())})
    planilla = [_fila("A", "O1", SEG), _fila("B", "O1", SW)]
    predicciones = [_prediccion("A", SEG), _prediccion("B", SW)]  # v9 repite los errores y aciertos de O1

    resultado = exactitud_brazo_manual(planilla, referencia, registro, predicciones=predicciones)

    mcnemar = resultado.contraste_vs_automatizado[0].mcnemar
    assert mcnemar.aplicable is False and mcnemar.criterio == "no aplicable"
    assert (mcnemar.ambas, mcnemar.ninguna) == (1, 1)


def test_un_caso_sin_prediccion_queda_fuera_del_pareo_y_se_declara(registro):
    referencia = _referencia({"A": (SEG, set()), "B": (HW, set())})
    planilla = [_fila("A", "O1", SEG), _fila("B", "O1", HW)]

    resultado = exactitud_brazo_manual(planilla, referencia, registro, predicciones=[_prediccion("A", SEG)])

    contraste = resultado.contraste_vs_automatizado[0]
    assert contraste.sin_prediccion == ("B",)
    assert contraste.pares_clave == (("A", "O1"),)
    assert contraste.mcnemar.pares == 1


def test_una_prediccion_repetida_para_un_caso_falla(registro):
    referencia = _referencia({"A": (SEG, set())})
    planilla = [_fila("A", "O1", SEG)]

    with pytest.raises(ValueError, match="A"):
        exactitud_brazo_manual(
            planilla, referencia, registro, predicciones=[_prediccion("A", SEG), _prediccion("A", HW)]
        )


def test_la_referencia_alternativa_cambia_el_rotulo_y_los_numeros(
    planilla, registro, corpus, predicciones_v9
):
    original = construir_referencia(REFERENCIA_CONSENSO_ORIGINAL, corpus=corpus)

    resultado = exactitud_brazo_manual(planilla, original, registro, predicciones=predicciones_v9)

    assert resultado.referencia_usada == "consenso_original"
    o1, o2 = resultado.por_operador["O1"], resultado.por_operador["O2"]
    assert (o1.casos, o1.aciertos_estrictos, o1.aciertos_laxos) == (18, 11, 12)
    assert (o2.casos, o2.aciertos_estrictos, o2.aciertos_laxos) == (18, 12, 15)
    agregada = resultado.agregada
    assert (agregada.casos, agregada.etiquetas) == (24, 36)
    assert (agregada.aciertos_estrictos, agregada.aciertos_laxos) == (23, 27)
    contrastes = {c.id_etiquetador: c.mcnemar for c in resultado.contraste_vs_automatizado}
    assert (contrastes["O1"].ambas, contrastes["O1"].solo_a, contrastes["O1"].solo_b) == (9, 2, 7)
    assert (contrastes["O2"].ambas, contrastes["O2"].solo_a, contrastes["O2"].solo_b) == (9, 3, 5)
    assert resultado.automatizado.aciertos_estrictos == 20
    assert resultado.discordantes == () and resultado.n_discordantes == 0


# ---------------------------------------------------------------------------
# 5.1 — tasa de intervencion humana de campana: 20 de 200 casos, compatible con la cota
# ---------------------------------------------------------------------------
def _ids_de_la_corrida(n: int) -> list[str]:
    return [f"C{i:03d}" for i in range(1, n + 1)]


def _intervencion(
    id_caso: str,
    origen: str = "gate",
    cambio: str = "false",
    duracion: str = "30",
    actor: str = "a1b2c3d4e5f6",
) -> dict[str, str]:
    """Fila del export C5 (solo las intervenidas); `actor_alias` es un HMAC truncado."""
    return {
        "id_caso": id_caso,
        "incidente_id": "1",
        "log_id": "1",
        "origen_intervencion": origen,
        "intervencion_inicio_en": "",
        "validado_en": "",
        "duracion_s": duracion,
        "sector_predicho": SIS,
        "sector_validado": SIS,
        "cambio_sector": cambio,
        "actor_alias": actor,
    }


def test_20_de_200_casos_da_tasa_010_wilson_y_contraste_compatible():
    casos = _ids_de_la_corrida(200)
    filas = [_intervencion(caso) for caso in casos[:20]]

    resultado = tasa_intervencion_humana(filas, casos)

    assert resultado.casos_corrida == 200
    assert resultado.casos_intervenidos == 20
    assert resultado.tasa.proporcion == pytest.approx(0.10, abs=1e-12)
    assert resultado.tasa.ic == pytest.approx((0.065670, 0.149406), abs=1e-6)
    assert resultado.contraste.resultado == "compatible"


# ---------------------------------------------------------------------------
# 5.3 — triangulacion: no concluyente, refutada, cero intervenciones y denominador
# ---------------------------------------------------------------------------
def test_26_de_200_da_013_y_el_limite_superior_alcanza_la_cota_no_concluyente():
    casos = _ids_de_la_corrida(200)
    filas = [_intervencion(caso) for caso in casos[:26]]

    resultado = tasa_intervencion_humana(filas, casos)

    assert resultado.tasa.proporcion == pytest.approx(0.13, abs=1e-12)
    assert resultado.tasa.ic == pytest.approx((0.090282, 0.183664), abs=1e-6)
    contraste = resultado.contraste
    assert contraste.resultado == "no_concluyente"
    # La salida trae siempre la estimacion y ambos limites, mas la cota.
    assert contraste.cota == 0.15
    assert contraste.estimacion == pytest.approx(0.13, abs=1e-12)
    assert (contraste.limite_inferior, contraste.limite_superior) == pytest.approx(
        (0.090282, 0.183664), abs=1e-6
    )


@pytest.mark.parametrize("intervenidos", [30, 34])
def test_una_estimacion_que_alcanza_o_supera_la_cota_refuta_la_subhipotesis(intervenidos):
    casos = _ids_de_la_corrida(200)
    filas = [_intervencion(caso) for caso in casos[:intervenidos]]

    resultado = tasa_intervencion_humana(filas, casos)

    assert resultado.tasa.proporcion >= 0.15
    assert resultado.contraste.resultado == "refutada"


def test_cero_intervenciones_da_tasa_cero_sin_division_por_cero():
    casos = _ids_de_la_corrida(200)

    resultado = tasa_intervencion_humana([], casos)

    assert resultado.casos_intervenidos == 0
    assert resultado.tasa.proporcion == 0.0
    assert resultado.tasa.ic == pytest.approx((0.0, 0.018845), abs=1e-6)
    assert resultado.contraste.resultado == "compatible"


def test_la_cota_es_un_parametro_y_cambia_el_contraste():
    casos = _ids_de_la_corrida(200)
    filas = [_intervencion(caso) for caso in casos[:20]]  # 0,10: compatible con 0,15

    resultado = tasa_intervencion_humana(filas, casos, cota=0.05)

    assert resultado.contraste.cota == 0.05
    assert resultado.contraste.resultado == "refutada"


def test_el_denominador_es_la_corrida_y_no_el_export():
    casos = _ids_de_la_corrida(200)
    filas = [_intervencion(caso) for caso in casos[:20]]  # el export tiene 20 filas

    resultado = tasa_intervencion_humana(filas, casos)

    assert len(filas) == 20
    assert resultado.casos_corrida == 200
    assert resultado.tasa.denominador == 200


def test_un_caso_con_varias_filas_cuenta_una_sola_vez():
    casos = _ids_de_la_corrida(10)
    filas = [_intervencion("C001"), _intervencion("C001", origen="rederivacion"), _intervencion("C002")]

    resultado = tasa_intervencion_humana(filas, casos)

    assert resultado.casos_intervenidos == 2
    assert resultado.tasa.proporcion == pytest.approx(0.2, abs=1e-12)


# ---------------------------------------------------------------------------
# 5.4 — desgloses, filas no vinculables, ids fuera de la corrida y actor_alias
# ---------------------------------------------------------------------------
def _claves_anidadas(objeto) -> set[str]:
    """Todas las claves de dict que aparecen en un resultado convertido con `dataclasses.asdict`."""
    claves: set[str] = set()
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            claves.add(str(clave))
            claves |= _claves_anidadas(valor)
    elif isinstance(objeto, (list, tuple)):
        for elemento in objeto:
            claves |= _claves_anidadas(elemento)
    return claves


def test_desglose_por_origen_cuenta_casos_con_al_menos_una_intervencion_de_ese_origen():
    casos = _ids_de_la_corrida(20)
    filas = [
        _intervencion("C001", origen="gate", cambio="true"),
        _intervencion("C002", origen="gate", cambio="false"),
        _intervencion("C003", origen="muestreo", cambio="false"),
        _intervencion("C003", origen="rederivacion", cambio="true"),  # C003 figura en dos origenes
        _intervencion("C004", origen="rederivacion", cambio="true"),
    ]

    resultado = tasa_intervencion_humana(filas, casos)

    por_origen = resultado.por_origen
    assert list(por_origen) == ["gate", "muestreo", "rederivacion", "completado_manual"]
    assert [por_origen[o].casos for o in por_origen] == [2, 1, 2, 0]
    assert all(p.denominador == 20 for p in por_origen.values())
    assert por_origen["gate"].proporcion == pytest.approx(0.10, abs=1e-12)
    assert por_origen["gate"].ic == pytest.approx(intervalo_wilson(2, 20), abs=1e-12)
    assert resultado.casos_intervenidos == 4  # C003 cuenta una sola vez en la tasa
    assert any("mas de un origen" in advertencia for advertencia in resultado.advertencias)


def test_desglose_por_cambio_de_sector_separa_correcciones_de_confirmaciones():
    casos = _ids_de_la_corrida(20)
    filas = [
        _intervencion("C001", cambio="true"),
        _intervencion("C002", cambio="false"),
        _intervencion("C003", cambio="false"),
        _intervencion("C003", cambio="true"),  # el caso tuvo una confirmacion y una correccion
    ]

    resultado = tasa_intervencion_humana(filas, casos)

    assert list(resultado.por_cambio_sector) == ["true", "false"]
    assert resultado.por_cambio_sector["true"].casos == 2  # C001 y C003
    assert resultado.por_cambio_sector["false"].casos == 2  # C002 y C003
    assert resultado.por_cambio_sector["true"].ic == pytest.approx(intervalo_wilson(2, 20), abs=1e-12)


def test_un_origen_fuera_del_vocabulario_se_lista_despues_de_los_conocidos():
    casos = _ids_de_la_corrida(10)

    resultado = tasa_intervencion_humana([_intervencion("C001", origen="otro")], casos)

    assert list(resultado.por_origen)[-1] == "otro"
    assert resultado.por_origen["otro"].casos == 1


def test_una_fila_con_id_caso_nulo_es_no_vinculable_y_queda_fuera_de_la_tasa():
    casos = _ids_de_la_corrida(10)
    filas = [_intervencion("C001"), _intervencion("")]

    resultado = tasa_intervencion_humana(filas, casos)

    assert resultado.filas == 2
    assert resultado.no_vinculables == 1
    assert resultado.casos_intervenidos == 1
    assert resultado.tasa.proporcion == pytest.approx(0.1, abs=1e-12)
    assert any("no se pudieron vincular" in advertencia for advertencia in resultado.advertencias)


def test_sin_filas_no_vinculables_no_hay_advertencia_de_cota_inferior():
    resultado = tasa_intervencion_humana([_intervencion("C001")], _ids_de_la_corrida(10))

    assert resultado.no_vinculables == 0
    assert not any("no se pudieron vincular" in advertencia for advertencia in resultado.advertencias)


def test_un_id_caso_fuera_de_la_corrida_falla_y_nombra_el_caso():
    casos = _ids_de_la_corrida(10)

    with pytest.raises(ValueError) as excinfo:
        tasa_intervencion_humana([_intervencion("C001"), _intervencion("C999")], casos)

    assert "C999" in str(excinfo.value)


def test_actor_alias_no_se_usa_como_clave_ni_cambia_el_resultado():
    casos = _ids_de_la_corrida(20)
    con_un_actor = [_intervencion(c, actor="aaaaaaaaaaaa") for c in casos[:5]]
    con_otros_actores = [_intervencion(c, actor=f"{i:012x}") for i, c in enumerate(casos[:5])]

    primero = tasa_intervencion_humana(con_un_actor, casos)
    segundo = tasa_intervencion_humana(con_otros_actores, casos)

    assert primero == segundo
    assert not any("actor" in clave for clave in _claves_anidadas(dataclasses.asdict(primero)))


def test_el_export_sin_la_columna_actor_alias_igual_se_analiza():
    casos = _ids_de_la_corrida(10)
    fila = _intervencion("C001")
    del fila["actor_alias"]

    assert tasa_intervencion_humana([fila], casos).casos_intervenidos == 1


@pytest.mark.parametrize("columna", ["id_caso", "origen_intervencion", "cambio_sector"])
def test_una_columna_faltante_del_export_falla_y_la_nombra(columna):
    fila = _intervencion("C001")
    del fila[columna]

    with pytest.raises(ValueError, match=columna):
        tasa_intervencion_humana([fila], _ids_de_la_corrida(10))


def test_un_cambio_de_sector_que_no_es_booleano_falla_y_nombra_la_fila():
    with pytest.raises(ValueError, match="cambio_sector") as excinfo:
        tasa_intervencion_humana([_intervencion("C001", cambio="quizas")], _ids_de_la_corrida(10))

    assert "quizas" in str(excinfo.value) and "C001" in str(excinfo.value)


@pytest.mark.parametrize(("crudo", "esperado"), [("True", "true"), ("FALSE", "false"), ("1", "true"), ("0", "false")])
def test_el_cambio_de_sector_acepta_las_grafias_habituales_de_un_booleano(crudo, esperado):
    resultado = tasa_intervencion_humana([_intervencion("C001", cambio=crudo)], _ids_de_la_corrida(10))

    assert resultado.por_cambio_sector[esperado].casos == 1


def test_una_corrida_vacia_falla_porque_no_hay_denominador():
    with pytest.raises(ValueError, match="corrida"):
        tasa_intervencion_humana([], [])


# ---------------------------------------------------------------------------
# 5.5 — proporcion de tiempo: cociente de sumas con IC bootstrap por caso
# ---------------------------------------------------------------------------
def test_proporcion_de_tiempo_80_sobre_280_con_el_denominador_rotulado():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}  # 10 casos de 20 s de registro automatizado
    filas = [_intervencion("C001", duracion="30"), _intervencion("C002", duracion="50")]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.estimable is True
    assert tiempo.suma_duracion_s == 80.0
    assert tiempo.suma_tiempo_automatizado_s == 200.0
    assert tiempo.proporcion == pytest.approx(80 / 280, abs=1e-12)
    assert tiempo.proporcion == pytest.approx(0.285714, abs=1e-6)
    assert tiempo.denominador_rotulo == "tiempo de registro automatizado"
    assert "limitacion" in tiempo.limitacion.lower()


def test_el_ic_de_la_proporcion_de_tiempo_es_bootstrap_por_caso_del_cociente_de_sumas():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    filas = [_intervencion("C001", duracion="30"), _intervencion("C002", duracion="50")]
    duraciones = {"C001": 30.0, "C002": 50.0}
    unidades = [(duraciones.get(caso, 0.0), tiempos[caso]) for caso in sorted(casos)]
    cocientes = []
    generador = random.Random(SEMILLA_BOOTSTRAP)
    for indices in remuestreos_indices(generador, len(unidades), REMUESTREOS_BOOTSTRAP):
        duracion = sum(unidades[i][0] for i in indices)
        registro = sum(unidades[i][1] for i in indices)
        cocientes.append(duracion / (registro + duracion))

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.ic == pytest.approx(percentil_intervalo(cocientes, NIVEL_CONFIANZA), abs=1e-12)
    assert tiempo.ic[0] <= tiempo.proporcion <= tiempo.ic[1]
    assert "bootstrap" in tiempo.metodo_ic and "caso" in tiempo.metodo_ic
    assert (tiempo.semilla, tiempo.remuestreos) == (SEMILLA_BOOTSTRAP, REMUESTREOS_BOOTSTRAP)
    assert tiempo.nivel_confianza == NIVEL_CONFIANZA


def test_la_cobertura_de_duracion_se_reporta_como_k_de_m():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    filas = [_intervencion("C001", duracion="30"), _intervencion("C002", duracion="50")]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert (tiempo.con_duracion_completa, tiempo.casos_intervenidos) == (2, 2)
    assert tiempo.cobertura == 1.0
    assert tiempo.casos_incluidos == 10


# ---------------------------------------------------------------------------
# 5.6 — triangulacion: cobertura minima del 80 %, exclusiones y cero intervenciones
# ---------------------------------------------------------------------------
def test_cobertura_de_4_de_5_es_80_por_ciento_y_la_proporcion_es_estimable():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    filas = [
        _intervencion("C001", duracion="10"),
        _intervencion("C002", duracion="20"),
        _intervencion("C003", duracion="30"),
        _intervencion("C004", duracion="40"),
        _intervencion("C005", duracion=""),  # sin inicio: el export no trae la duracion
    ]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.estimable is True
    assert (tiempo.con_duracion_completa, tiempo.casos_intervenidos) == (4, 5)
    assert tiempo.cobertura == pytest.approx(0.8, abs=1e-12)
    # El caso intervenido sin duracion sale del cociente: quedan 9 casos y 180 s de registro.
    assert tiempo.sin_duracion == ("C005",)
    assert tiempo.casos_incluidos == 9
    assert tiempo.suma_tiempo_automatizado_s == 180.0
    assert tiempo.proporcion == pytest.approx(100 / 280, abs=1e-12)


def test_cobertura_de_3_de_4_es_75_por_ciento_y_no_es_estimable_con_el_motivo():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    filas = [
        _intervencion("C001", duracion="10"),
        _intervencion("C002", duracion="20"),
        _intervencion("C003", duracion="30"),
        _intervencion("C004", duracion=""),
    ]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.estimable is False
    assert tiempo.proporcion is None and tiempo.ic is None
    assert tiempo.cobertura == pytest.approx(0.75, abs=1e-12)
    assert (tiempo.con_duracion_completa, tiempo.casos_intervenidos) == (3, 4)
    assert "3 de 4" in tiempo.motivo and "75" in tiempo.motivo and "80" in tiempo.motivo


def test_la_tasa_de_casos_se_reporta_igual_cuando_la_proporcion_de_tiempo_no_es_estimable():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    filas = [_intervencion("C001", duracion="10"), _intervencion("C002", duracion=""),
             _intervencion("C003", duracion=""), _intervencion("C004", duracion="5")]

    analisis = analizar_intervencion(filas, casos, tiempos)

    assert analisis.tiempo.estimable is False
    assert analisis.tasa.casos_intervenidos == 4
    assert analisis.tasa.tasa.proporcion == pytest.approx(0.4, abs=1e-12)


def test_un_caso_sin_tiempo_automatizado_se_excluye_del_cociente_y_se_cuenta():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    tiempos["C010"] = None
    del tiempos["C009"]  # ausente del mapa equivale a sin dato
    filas = [_intervencion("C001", duracion="30")]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.sin_tiempo_automatizado == ("C009", "C010")
    assert tiempo.casos_incluidos == 8
    assert tiempo.suma_tiempo_automatizado_s == 160.0
    assert tiempo.proporcion == pytest.approx(30 / 190, abs=1e-12)


def test_un_caso_intervenido_sin_tiempo_automatizado_no_aporta_su_duracion():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    tiempos["C001"] = None
    filas = [_intervencion("C001", duracion="300"), _intervencion("C002", duracion="30")]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.sin_tiempo_automatizado == ("C001",)
    assert tiempo.suma_duracion_s == 30.0
    assert tiempo.proporcion == pytest.approx(30 / (180 + 30), abs=1e-12)


def test_sin_intervenciones_la_proporcion_de_tiempo_es_cero_sin_division_por_cero():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}

    tiempo = proporcion_tiempo_intervencion([], casos, tiempos)

    assert tiempo.estimable is True
    assert tiempo.proporcion == 0.0
    assert tiempo.ic == (0.0, 0.0)
    assert tiempo.cobertura is None and tiempo.casos_intervenidos == 0


def test_las_duraciones_de_un_caso_con_varias_filas_se_suman():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    filas = [_intervencion("C001", duracion="15"), _intervencion("C001", origen="rederivacion", duracion="25")]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.suma_duracion_s == 40.0
    assert tiempo.casos_intervenidos == 1 and tiempo.con_duracion_completa == 1


def test_un_caso_con_una_fila_sin_duracion_no_tiene_duracion_completa():
    casos = _ids_de_la_corrida(10)
    tiempos = {caso: 20.0 for caso in casos}
    filas = [_intervencion("C001", duracion="15"), _intervencion("C001", origen="rederivacion", duracion="")]

    tiempo = proporcion_tiempo_intervencion(filas, casos, tiempos)

    assert tiempo.con_duracion_completa == 0 and tiempo.sin_duracion == ("C001",)
    assert tiempo.estimable is False  # cobertura 0 de 1


def test_sin_ningun_tiempo_automatizado_no_es_estimable():
    casos = _ids_de_la_corrida(3)

    tiempo = proporcion_tiempo_intervencion([_intervencion("C001")], casos, {})

    assert tiempo.estimable is False
    assert "tiempo_automatizado_s" in tiempo.motivo


def test_una_duracion_negativa_o_no_numerica_falla_y_nombra_la_fila():
    casos = _ids_de_la_corrida(3)

    with pytest.raises(ValueError, match="duracion_s") as excinfo:
        proporcion_tiempo_intervencion([_intervencion("C001", duracion="-5")], casos, {})

    assert "C001" in str(excinfo.value)
    with pytest.raises(ValueError, match="duracion_s"):
        proporcion_tiempo_intervencion([_intervencion("C001", duracion="abc")], casos, {})


# ---------------------------------------------------------------------------
# 5.7 — los fixtures de C5, C6 y del corpus de campana juntos (como los usa el CLI)
# ---------------------------------------------------------------------------
def test_la_intervencion_de_los_fixtures_sale_del_plan_y_del_corpus_de_campana(corpus):
    intervenciones = h.leer_csv(h.INTERVENCIONES)
    casos_corrida = [fila.id_caso for fila in leer_plan_csv(h.PLAN)]
    tiempos = {caso.id: caso.tiempo_automatizado_s for caso in corpus}

    analisis = analizar_intervencion(intervenciones, casos_corrida, tiempos)

    tasa = analisis.tasa
    assert (tasa.casos_corrida, tasa.casos_intervenidos, tasa.filas, tasa.no_vinculables) == (24, 5, 7, 1)
    assert tasa.tasa.proporcion == pytest.approx(5 / 24, abs=1e-12)
    assert tasa.tasa.ic == pytest.approx(intervalo_wilson(5, 24), abs=1e-12)
    assert tasa.contraste.resultado == "refutada"  # 0,208 >= 0,15
    assert [tasa.por_origen[o].casos for o in ("gate", "muestreo", "rederivacion", "completado_manual")] == [
        3, 1, 2, 0
    ]
    assert (tasa.por_cambio_sector["true"].casos, tasa.por_cambio_sector["false"].casos) == (3, 3)
    tiempo = analisis.tiempo
    # S16 no trae duracion (4 de 5 = 80 %: estimable) y S23 y S24 no tienen tiempo automatizado.
    assert tiempo.estimable is True and tiempo.cobertura == pytest.approx(0.8, abs=1e-12)
    assert tiempo.sin_duracion == ("S16",) and tiempo.sin_tiempo_automatizado == ("S23", "S24")
    assert tiempo.casos_incluidos == 21
    assert tiempo.proporcion == pytest.approx(102 / (420 + 102), abs=1e-12)


# ---------------------------------------------------------------------------
# 6.1 — contraste pareado: Wilcoxon con nombres neutros y caso degenerado
# ---------------------------------------------------------------------------
GRUPO_B_PAREADO = [10.0] * 8
GRUPO_A_PAREADO = [11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0]  # diferencias 1..8, todas positivas


def test_el_contraste_pareado_envuelve_wilcoxon_con_nombres_neutros():
    resultado = contraste_pareado(GRUPO_A_PAREADO, GRUPO_B_PAREADO)

    assert resultado.aplicable is True and resultado.motivo is None
    assert resultado.n == 8
    assert resultado.estadistico == 0.0
    assert resultado.t_a_mayor == 36.0 and resultado.t_b_mayor == 0.0
    assert resultado.p == pytest.approx(2 / 256, abs=1e-12)
    assert resultado.p_unilateral_a_mayor_que_b == pytest.approx(1 / 256, abs=1e-12)
    assert resultado.r == pytest.approx(1.0, abs=1e-12)
    assert resultado.dz == pytest.approx(1.837117, abs=1e-6)


def test_el_contraste_pareado_no_usa_los_nombres_manual_ni_automatizado():
    resultado = contraste_pareado(GRUPO_A_PAREADO, GRUPO_B_PAREADO)

    nombres = {campo.name for campo in dataclasses.fields(resultado)}
    assert not any("manual" in nombre or "automatizado" in nombre for nombre in nombres)


def test_el_contraste_pareado_con_el_grupo_a_menor_invierte_el_signo_de_r():
    resultado = contraste_pareado(GRUPO_B_PAREADO, GRUPO_A_PAREADO)

    assert resultado.r == pytest.approx(-1.0, abs=1e-12)
    assert resultado.t_a_mayor == 0.0 and resultado.t_b_mayor == 36.0
    assert resultado.p_unilateral_a_mayor_que_b == pytest.approx(1.0, abs=1e-12)


def test_todas_las_diferencias_cero_se_declaran_no_aplicable_sin_propagar_el_error_de_scipy():
    resultado = contraste_pareado([10.0] * 6, [10.0] * 6)

    assert resultado.aplicable is False
    assert "cero" in resultado.motivo
    assert resultado.p is None and resultado.estadistico is None and resultado.r is None
    assert resultado.lectura == "no aplicable"


# ---------------------------------------------------------------------------
# 6.2 — el envoltorio captura el ValueError de scipy y el p NaN, como _wilcoxon_o_no_aplicable
# ---------------------------------------------------------------------------
def test_un_value_error_de_wilcoxon_se_captura_como_no_aplicable(monkeypatch):
    def wilcoxon_que_falla(manual, automatizado):
        raise ValueError("zero_method 'wilcox' and 'pratt' do not work if x - y is zero for all elements.")

    monkeypatch.setattr(campana, "wilcoxon_tiempos_detallado", wilcoxon_que_falla)

    resultado = contraste_pareado(GRUPO_A_PAREADO, GRUPO_B_PAREADO)

    assert resultado.aplicable is False and resultado.p is None
    assert "zero_method" in resultado.motivo


def test_un_p_nan_de_wilcoxon_se_captura_como_no_aplicable(monkeypatch):
    real = campana.wilcoxon_tiempos_detallado

    def wilcoxon_con_p_nan(manual, automatizado):
        return dataclasses.replace(real(manual, automatizado), p=float("nan"))

    monkeypatch.setattr(campana, "wilcoxon_tiempos_detallado", wilcoxon_con_p_nan)

    resultado = contraste_pareado(GRUPO_A_PAREADO, GRUPO_B_PAREADO)

    assert resultado.aplicable is False and resultado.p is None
    assert "NaN" in resultado.motivo


def test_menos_de_seis_pares_es_no_aplicable_sin_estadistico():
    resultado = contraste_pareado([11.0, 12.0, 13.0, 14.0, 15.0], [10.0] * 5)

    assert resultado.aplicable is False
    assert "6" in resultado.motivo and resultado.n == 5
    assert resultado.estadistico is None and resultado.r is None and resultado.mde is None


def test_dos_grupos_de_distinta_longitud_no_forman_pares():
    with pytest.raises(ValueError, match="misma longitud"):
        contraste_pareado([1.0, 2.0], [1.0])


# ---------------------------------------------------------------------------
# 6.3 — contraste independiente: Mann-Whitney bilateral con r = 2 U_a / (n_a n_b) - 1
# ---------------------------------------------------------------------------
def test_grupos_separados_con_el_grupo_a_menor_dan_u_cero_y_r_menos_uno():
    resultado = contraste_independiente([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], [7.0, 8.0, 9.0, 10.0, 11.0, 12.0])

    assert resultado.aplicable is True
    assert (resultado.n_a, resultado.n_b) == (6, 6)
    assert resultado.estadistico_u == 0.0
    assert resultado.r == pytest.approx(-1.0, abs=1e-12)
    assert resultado.p == pytest.approx(2 / 924, abs=1e-12)  # exacto: 2 / C(12, 6)


def test_grupos_separados_con_el_grupo_a_mayor_dan_u_maximo_y_r_mas_uno():
    resultado = contraste_independiente([7.0, 8.0, 9.0, 10.0, 11.0, 12.0], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    assert resultado.estadistico_u == 36.0
    assert resultado.r == pytest.approx(1.0, abs=1e-12)


def test_grupos_iguales_dan_r_cero_y_p_uno():
    grupo = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    resultado = contraste_independiente(grupo, list(grupo))

    assert resultado.estadistico_u == 18.0
    assert resultado.r == pytest.approx(0.0, abs=1e-12)
    assert resultado.p == pytest.approx(1.0, abs=1e-12)


def test_grupos_intercalados_dan_r_chico_y_p_alto():
    resultado = contraste_independiente([1.0, 3.0, 5.0, 7.0, 9.0, 11.0], [2.0, 4.0, 6.0, 8.0, 10.0, 12.0])

    assert resultado.estadistico_u == 15.0
    assert resultado.r == pytest.approx(2 * 15 / 36 - 1, abs=1e-12)
    assert resultado.p == pytest.approx(0.699134, abs=1e-6)


def test_el_p_de_mann_whitney_es_el_bilateral_de_scipy():
    scipy_stats = pytest.importorskip("scipy.stats")
    a = [61.0, 64.0, 67.0, 70.0, 73.0, 79.0, 81.0]
    b = [60.0, 62.0, 63.0, 66.0, 68.0, 69.0, 72.0, 75.0]

    resultado = contraste_independiente(a, b)

    esperado = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")
    assert resultado.estadistico_u == esperado.statistic
    assert resultado.p == pytest.approx(esperado.pvalue, abs=1e-12)


def test_un_grupo_con_menos_de_seis_casos_es_no_aplicable_sin_estadistico_ni_efecto():
    resultado = contraste_independiente([1.0, 2.0, 3.0, 4.0, 5.0], [7.0, 8.0, 9.0, 10.0, 11.0, 12.0])

    assert resultado.aplicable is False
    assert "6" in resultado.motivo
    assert (resultado.n_a, resultado.n_b) == (5, 6)
    assert resultado.estadistico_u is None and resultado.p is None and resultado.r is None
    assert resultado.mde is None and resultado.lectura == "no aplicable"


def test_todos_los_valores_iguales_en_ambos_grupos_es_no_aplicable():
    resultado = contraste_independiente([5.0] * 6, [5.0] * 6)

    assert resultado.aplicable is False
    assert "NaN" in resultado.motivo or "variabilidad" in resultado.motivo


# ---------------------------------------------------------------------------
# 6.4 — la duracion del brazo manual es timestamp - inicio de la planilla
# ---------------------------------------------------------------------------
def _fila_con_instantes(id_caso: str, operador: str, inicio: str, timestamp: str) -> dict[str, str]:
    return dict(_fila(id_caso, operador, SEG), inicio=inicio, timestamp=timestamp)


def test_la_duracion_es_timestamp_menos_inicio_en_segundos():
    fila = _fila_con_instantes("A", "O1", "2026-11-17T10:00:00-03:00", "2026-11-17T10:01:20-03:00")

    duraciones = duraciones_brazo_manual([fila])

    assert [(d.id_caso, d.id_etiquetador, d.duracion_s) for d in duraciones] == [("A", "O1", 80.0)]


def test_la_duracion_respeta_las_zonas_horarias_de_cada_instante():
    # 13:01:20 UTC es 10:01:20 en -03:00: pasaron 80 s aunque los textos no se parezcan.
    fila = _fila_con_instantes("A", "O1", "2026-11-17T10:00:00-03:00", "2026-11-17T13:01:20+00:00")

    assert duraciones_brazo_manual([fila])[0].duracion_s == 80.0


def test_una_duracion_cero_es_valida():
    fila = _fila_con_instantes("A", "O1", "2026-11-17T10:00:00-03:00", "2026-11-17T10:00:00-03:00")

    assert duraciones_brazo_manual([fila])[0].duracion_s == 0.0


def test_las_duraciones_salen_ordenadas_por_operador_y_caso_y_solo_del_brazo_manual(planilla):
    duraciones = duraciones_brazo_manual(planilla)  # la planilla trae tambien doble etiquetado

    claves = [(d.id_etiquetador, d.id_caso) for d in duraciones]
    assert len(duraciones) == 36
    assert claves == sorted(claves)
    assert {d.id_etiquetador for d in duraciones} == {"O1", "O2"}


def test_las_duraciones_de_los_fixtures_son_las_de_la_planilla(planilla):
    por_clave = {(d.id_etiquetador, d.id_caso): d.duracion_s for d in duraciones_brazo_manual(planilla)}

    # O1 trabaja S09 primero (posicion 1: 50 + 2 + 40 + 1 = 93 s) y S08 al final (posicion 18).
    assert por_clave[("O1", "S09")] == 93.0
    assert por_clave[("O2", "S09")] == 73.0
    assert min(por_clave.values()) == 61.0 and max(por_clave.values()) == 119.0


def test_una_duracion_negativa_falla_y_nombra_caso_y_operador():
    fila = _fila_con_instantes("S07", "O2", "2026-11-17T10:05:00-03:00", "2026-11-17T10:04:00-03:00")

    with pytest.raises(ValueError) as excinfo:
        duraciones_brazo_manual([fila])

    mensaje = str(excinfo.value)
    assert "S07" in mensaje and "O2" in mensaje and "negativa" in mensaje


@pytest.mark.parametrize("campo", ["inicio", "timestamp"])
@pytest.mark.parametrize("valor", ["", "ayer a la tarde", "2026-11-17T10:00:00"])
def test_un_instante_ausente_ilegible_o_sin_zona_falla_y_nombra_campo_caso_y_operador(campo, valor):
    fila = _fila_con_instantes("S07", "O2", "2026-11-17T10:00:00-03:00", "2026-11-17T10:01:00-03:00")
    fila[campo] = valor

    with pytest.raises(ValueError) as excinfo:
        duraciones_brazo_manual([fila])

    mensaje = str(excinfo.value)
    assert campo in mensaje and "S07" in mensaje and "O2" in mensaje


def test_el_tiempo_manual_s_del_corpus_no_interviene_en_la_duracion(planilla):
    base = duraciones_brazo_manual(planilla)
    con_columna_extra = [dict(fila, tiempo_manual_s="999999") for fila in planilla]

    assert duraciones_brazo_manual(con_columna_extra) == base
    assert "corpus" not in inspect.signature(duraciones_brazo_manual).parameters


# ---------------------------------------------------------------------------
# 6.5 — efecto de orden de condicion por operador
# ---------------------------------------------------------------------------
# Verificado con un script independiente sobre los fixtures (grupo_a = brazo_primero manual,
# grupo_b = automatizado; 9 casos en cada grupo para cada operador):
#   O1: U_a = 81, p = 0,0004066, r = +1,0 (todo el grupo manual-primero tarda mas)
#   O2: U_a = 29,5, p = 0,3520917, r = -0,2716
@pytest.fixture
def plan():
    return leer_plan_csv(h.PLAN)


def _por_operador(resultado) -> dict:
    return {orden.id_etiquetador: orden for orden in resultado.por_operador}


def test_orden_de_condicion_con_grupos_independientes_cuando_el_plan_no_cruza_casos(planilla, plan):
    resultado = efecto_orden(planilla, plan)

    assert resultado.respuesta == "duracion del brazo manual (timestamp - inicio), en segundos"
    assert resultado.diseno == "grupos_independientes"
    assert list(_por_operador(resultado)) == ["O1", "O2"]
    for orden in resultado.por_operador:
        assert orden.condicion.diseno == "grupos_independientes"
        assert (orden.condicion.contraste.n_a, orden.condicion.contraste.n_b) == (9, 9)


def test_orden_de_condicion_de_o1_es_significativo_con_r_mas_uno(planilla, plan):
    contraste = _por_operador(efecto_orden(planilla, plan))["O1"].condicion.contraste

    assert contraste.estadistico_u == 81.0
    assert contraste.p == pytest.approx(0.0004066392747530236, abs=1e-12)
    assert contraste.r == pytest.approx(1.0, abs=1e-12)
    assert contraste.lectura == "significativo (p < 0,05)"


def test_orden_de_condicion_de_o2_no_es_significativo(planilla, plan):
    contraste = _por_operador(efecto_orden(planilla, plan))["O2"].condicion.contraste

    assert contraste.estadistico_u == 29.5
    assert contraste.p == pytest.approx(0.35209165427172284, abs=1e-12)
    assert contraste.r == pytest.approx(-0.2716049382716049, abs=1e-12)
    assert contraste.lectura == "no significativo; efectos menores que el MDE no son detectables"


def test_el_mde_de_cada_contraste_independiente_usa_el_n_efectivo_de_los_grupos(planilla, plan):
    contraste = _por_operador(efecto_orden(planilla, plan))["O1"].condicion.contraste

    assert contraste.n_efectivo == pytest.approx(4.5, abs=1e-12)  # 9 * 9 / (9 + 9)
    assert contraste.escala_mde == "d"
    esperado = efecto_minimo_detectable(4.5, eficiencia_relativa=ARE_WILCOXON_MINIMA)
    assert contraste.mde == pytest.approx(esperado, abs=1e-12)
    assert contraste.mde == pytest.approx(1.4209, abs=1e-4)


def test_el_grupo_a_es_el_de_brazo_primero_manual_segun_el_plan(planilla, plan):
    duraciones = {(d.id_etiquetador, d.id_caso): d.duracion_s for d in duraciones_brazo_manual(planilla)}
    brazo = {fila.id_caso: fila.brazo_primero for fila in plan}
    de_o1 = {caso: v for (op, caso), v in duraciones.items() if op == "O1"}
    manual_primero = [v for caso, v in de_o1.items() if brazo[caso] == "manual"]
    automatizado_primero = [v for caso, v in de_o1.items() if brazo[caso] == "automatizado"]

    contraste = _por_operador(efecto_orden(planilla, plan))["O1"].condicion.contraste

    assert contraste.n_a == len(manual_primero) and contraste.n_b == len(automatizado_primero)
    assert min(manual_primero) > max(automatizado_primero)  # r = +1: el grupo a es el mayor


def test_un_grupo_con_menos_de_seis_casos_da_condicion_no_aplicable(planilla, plan):
    manual_primero = {fila.id_caso for fila in plan if fila.brazo_primero == "manual"}
    de_o1 = sorted(f["id_caso"] for f in planilla if f["id_etiquetador"] == "O1" and f["id_caso"] in manual_primero)
    quitar = set(de_o1[5:])  # O1 conserva solo 5 de sus casos manual-primero
    reducida = [f for f in planilla if not (f["id_etiquetador"] == "O1" and f["id_caso"] in quitar)]

    contraste = _por_operador(efecto_orden(reducida, plan))["O1"].condicion.contraste

    assert contraste.aplicable is False
    assert contraste.n_a == 5 and contraste.n_b == 9
    assert contraste.estadistico_u is None and contraste.r is None and contraste.mde is None


def test_un_caso_que_no_esta_en_el_plan_falla_y_nombra_caso_y_operador(planilla, plan):
    sin_s24 = [fila for fila in plan if fila.id_caso != "S24"]

    with pytest.raises(ValueError) as excinfo:
        efecto_orden(planilla, sin_s24)

    mensaje = str(excinfo.value)
    assert "S24" in mensaje and "O2" in mensaje


# --- diseno cruzado: el plan cruza los mismos casos en dos corridas con condicion opuesta ----------
def _asignacion(id_caso: str, brazo_primero: str, posicion: int, mitad: int = 1) -> AsignacionCaso:
    return AsignacionCaso(id_caso, posicion, mitad, brazo_primero, "directo", None)


def _corrida_cruzada(n: int = 8):
    """Dos corridas de n casos: en la 1 los impares van manual-primero; en la 2, al reves."""
    ids = [f"K{i:02d}" for i in range(1, n + 1)]
    plan_1 = [_asignacion(c, "manual" if i % 2 else "automatizado", i) for i, c in enumerate(ids, 1)]
    plan_2 = [_asignacion(c, "automatizado" if i % 2 else "manual", i) for i, c in enumerate(ids, 1)]
    return ids, plan_1, plan_2


def _filas_de_duraciones(operador: str, dia: int, plan_corrida, duraciones: dict[str, int]) -> list[dict[str, str]]:
    """Filas de planilla: cada caso empieza en su propio minuto y dura lo indicado."""
    zona = timezone(timedelta(hours=-3))
    filas = []
    for orden, fila in enumerate(plan_corrida):
        inicio = datetime(2026, 11, dia, 10, orden, 0, tzinfo=zona)
        fin = inicio + timedelta(seconds=duraciones[fila.id_caso])
        filas.append(dict(_fila(fila.id_caso, operador, SEG), inicio=inicio.isoformat(), timestamp=fin.isoformat()))
    return filas


def _duraciones_por_condicion(plan_corrida) -> dict[str, int]:
    """Un caso que va manual-primero tarda 100 + i segundos; cuando va segundo, 90."""
    return {
        fila.id_caso: (100 + int(fila.id_caso[1:]) if fila.brazo_primero == "manual" else 90)
        for fila in plan_corrida
    }


def test_orden_de_condicion_en_diseno_cruzado_es_wilcoxon_pareado_con_r_dz_y_mde_en_d_z():
    _, plan_1, plan_2 = _corrida_cruzada(8)
    filas_1 = _filas_de_duraciones("O1", 17, plan_1, _duraciones_por_condicion(plan_1))
    filas_2 = _filas_de_duraciones("O1", 24, plan_2, _duraciones_por_condicion(plan_2))

    resultado = efecto_orden(filas_1, plan_1, cruce=CorridaCruzada(plan=plan_2, registros_manual=filas_2))

    assert resultado.diseno == "cruzado"
    orden = _por_operador(resultado)["O1"]
    assert orden.condicion.diseno == "cruzado"
    pareado = orden.condicion.contraste
    # Diferencias (manual-primero - automatizado-primero) por caso: (100 + i) - 90 = 10 + i.
    assert pareado.n == 8 and pareado.aplicable is True
    assert pareado.estadistico == 0.0 and pareado.r == pytest.approx(1.0, abs=1e-12)
    assert pareado.p == pytest.approx(2 / 256, abs=1e-12)
    assert pareado.dz == pytest.approx(14.5 / 6**0.5, abs=1e-9)
    assert pareado.escala_mde == "d_z"
    esperado = efecto_minimo_detectable(8, eficiencia_relativa=ARE_WILCOXON_MINIMA)
    assert pareado.mde == pytest.approx(esperado, abs=1e-12)


def test_si_las_diferencias_pareadas_son_todas_cero_el_diseno_cruzado_es_no_aplicable():
    ids, plan_1, plan_2 = _corrida_cruzada(8)
    iguales = {c: 90 for c in ids}
    filas_1 = _filas_de_duraciones("O1", 17, plan_1, iguales)
    filas_2 = _filas_de_duraciones("O1", 24, plan_2, iguales)

    resultado = efecto_orden(filas_1, plan_1, cruce=CorridaCruzada(plan=plan_2, registros_manual=filas_2))

    pareado = _por_operador(resultado)["O1"].condicion.contraste
    assert pareado.aplicable is False and "cero" in pareado.motivo


def test_un_plan_que_no_cruza_los_mismos_casos_con_condicion_opuesta_falla():
    ids, plan_1, plan_2 = _corrida_cruzada(8)
    misma_condicion = [_asignacion(f.id_caso, f.brazo_primero, f.posicion) for f in plan_1]
    filas = _filas_de_duraciones("O1", 17, plan_1, {c: 90 for c in ids})

    with pytest.raises(ValueError, match="condicion opuesta"):
        efecto_orden(filas, plan_1, cruce=CorridaCruzada(plan=misma_condicion, registros_manual=filas))
    with pytest.raises(ValueError, match="mismos casos"):
        efecto_orden(filas, plan_1, cruce=CorridaCruzada(plan=plan_2[:-1], registros_manual=filas))


# ---------------------------------------------------------------------------
# 6.6 — efecto de posicion: Spearman con la posicion REAL y mitad 1 contra mitad 2 del plan
# ---------------------------------------------------------------------------
# Verificado con un script independiente sobre los fixtures:
#   O1: rho = 0,0371901 (p = 0,8835215, n = 18); mitades n = 10 y 8, U_1 = 20, p = 0,0828451,
#       r = -0,5; 0 desvios respecto del plan.
#   O2: rho = 0,0186433 (p = 0,9414685, n = 18); mitades n = 8 y 10, U_1 = 47, p = 0,5621590,
#       r = +0,175; 2 desvios (S19 y S12, intercambiados).
def test_las_funciones_de_posicion_de_c165_se_importan_y_no_se_redefinen():
    assert campana.reconstruir_posicion_real is brazo_manual.reconstruir_posicion_real
    assert campana.desvios_respecto_del_plan is brazo_manual.desvios_respecto_del_plan


def test_efecto_de_posicion_de_o1_spearman_y_mitades(planilla, plan):
    posicion = _por_operador(efecto_orden(planilla, plan))["O1"].posicion

    spearman = posicion.spearman
    assert spearman.aplicable is True and spearman.n == 18
    assert spearman.rho == pytest.approx(0.03719010248943058, abs=1e-12)
    assert spearman.p == pytest.approx(0.88352153757092, abs=1e-12)
    assert spearman.lectura == "no significativo; efectos menores que el MDE no son detectables"
    mitades = posicion.mitades
    assert (mitades.n_a, mitades.n_b) == (10, 8)
    assert mitades.estadistico_u == 20.0
    assert mitades.p == pytest.approx(0.08284513326963502, abs=1e-12)
    assert mitades.r == pytest.approx(-0.5, abs=1e-12)


def test_efecto_de_posicion_de_o2_y_su_cantidad_de_desvios(planilla, plan):
    posicion = _por_operador(efecto_orden(planilla, plan))["O2"].posicion

    assert posicion.spearman.rho == pytest.approx(0.018643312554132103, abs=1e-12)
    assert posicion.spearman.p == pytest.approx(0.941468515027624, abs=1e-12)
    assert (posicion.mitades.n_a, posicion.mitades.n_b) == (8, 10)
    assert posicion.mitades.estadistico_u == 47.0
    assert posicion.mitades.r == pytest.approx(0.17500000000000004, abs=1e-12)
    assert posicion.desvios == 2
    assert posicion.casos_con_desvio == ("S12", "S19")


def test_o1_sigue_el_orden_del_plan_y_no_tiene_desvios(planilla, plan):
    posicion = _por_operador(efecto_orden(planilla, plan))["O1"].posicion

    assert posicion.desvios == 0 and posicion.casos_con_desvio == ()


def test_los_desvios_coinciden_con_los_que_informa_c165(planilla, plan):
    posiciones = reconstruir_posicion_real([f for f in planilla if f["tarea"] == "brazo_manual"])
    esperados = desvios_respecto_del_plan(posiciones, plan)

    resultado = _por_operador(efecto_orden(planilla, plan))

    assert resultado["O1"].posicion.desvios == len([d for d in esperados if d.id_etiquetador == "O1"])
    assert resultado["O2"].posicion.desvios == len([d for d in esperados if d.id_etiquetador == "O2"])


def test_el_mde_de_spearman_es_el_de_fisher_con_n_menos_tres_en_escala_de_correlacion(planilla, plan):
    spearman = _por_operador(efecto_orden(planilla, plan))["O1"].posicion.spearman

    esperado = math.tanh(efecto_minimo_detectable(18 - 3, eficiencia_relativa=ARE_WILCOXON_MINIMA))
    assert spearman.mde == pytest.approx(esperado, abs=1e-12)
    assert "rho" in spearman.escala_mde


def _operador_que_se_cansa(n: int = 12, segundos_por_posicion: int = 5):
    """
    Plan directo de n casos (mitad 1 los primeros n/2) y un operador que sigue el orden del
    runbook de c-166 (mitad por mitad, primero los casos manual-primero y despues los
    automatizado-primero) con una duracion que crece (o decrece) con el orden en que trabaja.
    """
    ids = [f"P{i:02d}" for i in range(1, n + 1)]
    plan_directo = [
        _asignacion(c, "manual" if i % 2 else "automatizado", i, 1 if i <= n // 2 else 2)
        for i, c in enumerate(ids, 1)
    ]
    orden_del_runbook = [
        fila
        for mitad in (1, 2)
        for turno in (1, 2)
        for fila in subplan(plan_directo, mitad, "manual", turno)
    ]
    duraciones = {
        fila.id_caso: 60 + segundos_por_posicion * lugar for lugar, fila in enumerate(orden_del_runbook, 1)
    }
    return plan_directo, _filas_de_duraciones("O1", 17, orden_del_runbook, duraciones)


def test_un_operador_que_se_cansa_da_rho_uno_y_mitad_1_menor_que_mitad_2():
    plan_directo, filas = _operador_que_se_cansa()

    posicion = _por_operador(efecto_orden(filas, plan_directo))["O1"].posicion

    assert posicion.spearman.rho == pytest.approx(1.0, abs=1e-12)
    assert posicion.spearman.lectura == "significativo (p < 0,05)"
    assert posicion.mitades.r == pytest.approx(-1.0, abs=1e-12)  # todo el grupo a (mitad 1) es menor
    assert posicion.mitades.p == pytest.approx(2 / 924, abs=1e-12)
    assert posicion.desvios == 0


def test_un_operador_que_aprende_da_rho_menos_uno_y_r_positivo_en_las_mitades():
    plan_directo, filas = _operador_que_se_cansa(segundos_por_posicion=-3)

    posicion = _por_operador(efecto_orden(filas, plan_directo))["O1"].posicion

    assert posicion.spearman.rho == pytest.approx(-1.0, abs=1e-12)
    assert posicion.mitades.r == pytest.approx(1.0, abs=1e-12)


def test_menos_de_seis_casos_hace_no_aplicable_a_spearman_y_a_las_mitades():
    plan_directo, filas = _operador_que_se_cansa(n=10)
    cinco = [f for f in filas if int(f["id_caso"][1:]) <= 5]

    posicion = _por_operador(efecto_orden(cinco, plan_directo))["O1"].posicion

    assert posicion.spearman.aplicable is False and posicion.spearman.rho is None
    assert posicion.spearman.mde is None
    assert posicion.mitades.aplicable is False


def test_si_una_mitad_tiene_menos_de_seis_casos_solo_las_mitades_son_no_aplicables():
    plan_directo, filas = _operador_que_se_cansa(n=12)
    # La mitad 2 conserva 5 casos; la mitad 1 conserva 6, asi que el operador tiene 11 duraciones.
    reducido = [f for f in filas if f["id_caso"] != "P12"]

    posicion = _por_operador(efecto_orden(reducido, plan_directo))["O1"].posicion

    assert posicion.spearman.aplicable is True and posicion.spearman.n == 11
    assert posicion.mitades.aplicable is False and (posicion.mitades.n_a, posicion.mitades.n_b) == (6, 5)


def test_una_duracion_constante_hace_no_aplicable_a_spearman_sin_advertencias_de_scipy():
    plan_directo, filas = _operador_que_se_cansa(segundos_por_posicion=0)

    with warnings.catch_warnings():
        warnings.simplefilter("error")  # ConstantInputWarning o RuntimeWarning fallarian el test
        posicion = _por_operador(efecto_orden(filas, plan_directo))["O1"].posicion

    assert posicion.spearman.aplicable is False
    assert "constante" in posicion.spearman.motivo
    assert posicion.mitades.aplicable is False  # sin variabilidad entre las mitades


# ---------------------------------------------------------------------------
# 6.7 — efecto minimo detectable con ARE_WILCOXON_MINIMA
# ---------------------------------------------------------------------------
def _grupos_pareados(n: int) -> tuple[list[float], list[float]]:
    """n pares con diferencias 1..7 que se repiten, todas positivas (sin ceros)."""
    return [100.0 + (i % 7) + 1 for i in range(n)], [100.0] * n


def test_mde_pareado_con_200_pares_es_0_2131_en_escala_dz():
    grupo_a, grupo_b = _grupos_pareados(200)

    resultado = contraste_pareado(grupo_a, grupo_b)

    assert resultado.aplicable is True and resultado.n == 200
    assert resultado.escala_mde == "d_z"
    assert resultado.mde == pytest.approx(0.2131, abs=1e-4)


def test_mde_pareado_con_100_pares_es_0_3014():
    grupo_a, grupo_b = _grupos_pareados(100)

    assert contraste_pareado(grupo_a, grupo_b).mde == pytest.approx(0.3014, abs=1e-4)


def test_mde_independiente_con_100_y_100_usa_n_efectivo_50_y_es_0_4262_en_escala_d():
    grupo_a = [100.0 + (i % 9) for i in range(100)]
    grupo_b = [100.5 + (i % 9) for i in range(100)]

    resultado = contraste_independiente(grupo_a, grupo_b)

    assert resultado.aplicable is True
    assert resultado.n_efectivo == pytest.approx(50.0, abs=1e-12)  # 100 * 100 / (100 + 100)
    assert resultado.escala_mde == "d"
    assert resultado.mde == pytest.approx(0.4262, abs=1e-4)


def test_el_mde_independiente_con_grupos_desiguales_usa_el_n_efectivo_armonico():
    resultado = contraste_independiente([1.0, 2, 3, 4, 5, 6, 7, 8, 9, 10], [3.0, 4, 5, 6, 7, 8])

    assert resultado.n_efectivo == pytest.approx(10 * 6 / 16, abs=1e-12)
    esperado = efecto_minimo_detectable(10 * 6 / 16, eficiencia_relativa=ARE_WILCOXON_MINIMA)
    assert resultado.mde == pytest.approx(esperado, abs=1e-12)


# ---------------------------------------------------------------------------
# 6.8 — "no significativo" nunca se rotula como ausencia de efecto
# ---------------------------------------------------------------------------
def test_con_p_mayor_o_igual_a_0_05_el_rotulo_es_no_significativo_con_el_mde():
    resultado = contraste_independiente([1.0, 3.0, 5.0, 7.0, 9.0, 11.0], [2.0, 4.0, 6.0, 8.0, 10.0, 12.0])

    assert resultado.p >= 0.05
    assert resultado.lectura == "no significativo; efectos menores que el MDE no son detectables"
    assert resultado.mde is not None


def test_con_p_menor_a_0_05_el_rotulo_es_significativo():
    resultado = contraste_independiente([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], [7.0, 8.0, 9.0, 10.0, 11.0, 12.0])

    assert resultado.p < 0.05
    assert resultado.lectura == "significativo (p < 0,05)"


def test_el_limite_de_la_lectura_es_p_igual_a_0_05_no_significativo():
    assert campana._lectura(0.05) == campana.LECTURA_NO_SIGNIFICATIVO
    assert campana._lectura(0.0499) == campana.LECTURA_SIGNIFICATIVO
    assert campana._lectura(None) == campana.LECTURA_NO_APLICABLE


def test_ningun_rotulo_ni_la_nota_hablan_de_ausencia_de_efecto(planilla, plan):
    resultado = efecto_orden(planilla, plan)
    textos = [campana.LECTURA_NO_SIGNIFICATIVO, campana.LECTURA_SIGNIFICATIVO]
    for orden in resultado.por_operador:
        textos += [
            orden.condicion.contraste.lectura,
            orden.posicion.spearman.lectura,
            orden.posicion.mitades.lectura,
        ]

    for texto in textos:
        assert "sin efecto" not in texto.lower() and "ausencia de efecto" not in texto.lower()
    assert "no es ausencia de efecto" in resultado.nota  # la nota lo niega expresamente


# ---------------------------------------------------------------------------
# 6.9 — acierto estricto como respuesta secundaria
# ---------------------------------------------------------------------------
# Verificado con un script independiente sobre los fixtures (referencia nueva, sin discordantes):
#   O1: manual-primero 6 de 9 aciertos, automatizado-primero 4 de 6, Fisher p = 1,0
#   O2: manual-primero 7 de 9 aciertos, automatizado-primero 4 de 6, Fisher p = 1,0
def test_acierto_por_condicion_en_grupos_independientes_trae_wilson_por_grupo_y_fisher(
    planilla, plan, referencia_nueva
):
    resultado = efecto_orden(planilla, plan, referencia=referencia_nueva)

    acierto = _por_operador(resultado)["O1"].condicion.acierto
    assert acierto.diseno == "grupos_independientes" and acierto.aplicable is True
    assert (acierto.manual_primero.casos, acierto.manual_primero.denominador) == (6, 9)
    assert (acierto.automatizado_primero.casos, acierto.automatizado_primero.denominador) == (4, 6)
    assert acierto.manual_primero.ic == pytest.approx(intervalo_wilson(6, 9), abs=1e-12)
    assert acierto.automatizado_primero.ic == pytest.approx(intervalo_wilson(4, 6), abs=1e-12)
    assert acierto.p_fisher == pytest.approx(1.0, abs=1e-12)
    assert acierto.mcnemar is None


def test_el_acierto_de_o2_por_condicion_sobre_los_fixtures(planilla, plan, referencia_nueva):
    acierto = _por_operador(efecto_orden(planilla, plan, referencia=referencia_nueva))["O2"].condicion.acierto

    assert (acierto.manual_primero.casos, acierto.manual_primero.denominador) == (7, 9)
    assert (acierto.automatizado_primero.casos, acierto.automatizado_primero.denominador) == (4, 6)


def test_fisher_es_la_prueba_exacta_bilateral_de_scipy():
    scipy_stats = pytest.importorskip("scipy.stats")
    # Grupo manual-primero: 8 de 8 aciertos; grupo automatizado-primero: 2 de 8.
    plan_directo = [_asignacion(f"F{i:02d}", "manual" if i <= 8 else "automatizado", i) for i in range(1, 17)]
    referencia = _referencia({fila.id_caso: (SEG, set()) for fila in plan_directo})
    duraciones = {fila.id_caso: 60 for fila in plan_directo}
    filas = _filas_de_duraciones("O1", 17, plan_directo, duraciones)
    for fila in filas:
        indice = int(fila["id_caso"][1:])
        fila["sector_etiquetado"] = SEG if indice <= 8 or indice in (9, 10) else HW

    acierto = _por_operador(efecto_orden(filas, plan_directo, referencia=referencia))["O1"].condicion.acierto

    esperado = scipy_stats.fisher_exact([[8, 0], [2, 6]], alternative="two-sided")
    assert (acierto.manual_primero.casos, acierto.automatizado_primero.casos) == (8, 2)
    assert acierto.p_fisher == pytest.approx(esperado.pvalue, abs=1e-12)
    assert acierto.p_fisher < 0.05


def test_menos_de_seis_casos_con_referencia_en_un_grupo_hace_no_aplicable_al_acierto(
    planilla, plan, referencia_nueva
):
    # O1 pierde 4 de sus casos automatizado-primero que estaban en la referencia: quedan 2 evaluables.
    auto_primero_en_ref = sorted(
        f["id_caso"]
        for f in planilla
        if f["id_etiquetador"] == "O1"
        and f["id_caso"] in referencia_nueva.casos
        and {p.id_caso: p for p in plan}[f["id_caso"]].brazo_primero == "automatizado"
    )
    quitar = set(auto_primero_en_ref[:4])
    reducida = [f for f in planilla if not (f["id_etiquetador"] == "O1" and f["id_caso"] in quitar)]

    acierto = _por_operador(efecto_orden(reducida, plan, referencia=referencia_nueva))["O1"].condicion.acierto

    assert acierto.aplicable is False
    assert "6" in acierto.motivo
    assert acierto.p_fisher is None


def test_sin_referencia_no_hay_respuesta_secundaria(planilla, plan):
    assert _por_operador(efecto_orden(planilla, plan))["O1"].condicion.acierto is None


def test_en_el_diseno_cruzado_el_acierto_se_contrasta_con_mcnemar_pareado_por_caso():
    ids, plan_1, plan_2 = _corrida_cruzada(8)
    referencia = _referencia({c: (SEG, set()) for c in ids})
    # Para cada caso: acierta si i <= 6 cuando va manual-primero y si i <= 3 cuando va segundo.
    filas_1 = _filas_de_duraciones("O1", 17, plan_1, {c: 90 + int(c[1:]) for c in ids})
    filas_2 = _filas_de_duraciones("O1", 24, plan_2, {c: 90 + int(c[1:]) for c in ids})
    for filas, plan_corrida in ((filas_1, plan_1), (filas_2, plan_2)):
        brazo = {f.id_caso: f.brazo_primero for f in plan_corrida}
        for fila in filas:
            indice = int(fila["id_caso"][1:])
            acierta = indice <= (6 if brazo[fila["id_caso"]] == "manual" else 3)
            fila["sector_etiquetado"] = SEG if acierta else HW

    resultado = efecto_orden(
        filas_1, plan_1, referencia=referencia, cruce=CorridaCruzada(plan=plan_2, registros_manual=filas_2)
    )

    acierto = _por_operador(resultado)["O1"].condicion.acierto
    assert acierto.diseno == "cruzado" and acierto.aplicable is True
    mcnemar = acierto.mcnemar
    assert (mcnemar.ambas, mcnemar.solo_a, mcnemar.solo_b, mcnemar.ninguna) == (3, 3, 0, 2)
    assert mcnemar.p_primario == pytest.approx(0.25, abs=1e-12)
    assert acierto.manual_primero is None and acierto.p_fisher is None


# ---------------------------------------------------------------------------
# 7.1 — evaluacion fuera de muestra: bloques rotulados con desglose por etapa
# ---------------------------------------------------------------------------
# Verificado con un script independiente sobre los fixtures (n, estrictos, laxos):
#   in-sample  (24 casos): total (24, 20, 20); deterministic (8, 8, 8), gemini (12, 9, 9), fallback (4, 3, 3)
#   out-of-sample (12):    total (12, 8, 9);   deterministic (4, 3, 4), gemini (6, 4, 4),  fallback (2, 1, 1)
def _fuera_de_muestra(**cambios):
    """`evaluar_fuera_de_muestra` sobre los fixtures, con los pines que declara el README del fixture."""
    argumentos = {
        "pines_in_sample": h.PINES_IN_SAMPLE,
        "rango_google_genai_vigente": h.RANGO_VIGENTE_GOOGLE_GENAI,
    }
    argumentos.update(cambios)
    rutas = (
        h.PREDICCIONES_IN_SAMPLE,
        h.CORPUS_CAMPANA,
        h.PREDICCIONES_INDEPENDIENTE,
        h.CORPUS_INDEPENDIENTE,
    )
    return evaluar_fuera_de_muestra(*rutas, **argumentos)


def test_devuelve_un_bloque_in_sample_y_otro_out_of_sample_con_exactitud_global_y_wilson():
    resultado = _fuera_de_muestra()

    assert resultado.obtenido is True and resultado.motivo is None and resultado.faltantes == ()
    assert resultado.in_sample.rotulo == "in-sample"
    assert resultado.out_of_sample.rotulo == "out-of-sample"
    en_muestra, fuera = resultado.in_sample.resumen, resultado.out_of_sample.resumen
    assert (en_muestra.casos, en_muestra.aciertos_estrictos, en_muestra.aciertos_laxos) == (24, 20, 20)
    assert en_muestra.ic_estricta == pytest.approx(intervalo_wilson(20, 24), abs=1e-12)
    assert (fuera.casos, fuera.aciertos_estrictos, fuera.aciertos_laxos) == (12, 8, 9)
    assert fuera.ic_estricta == pytest.approx(intervalo_wilson(8, 12), abs=1e-12)
    assert fuera.ic_laxa == pytest.approx(intervalo_wilson(9, 12), abs=1e-12)


def test_el_desglose_por_etapa_sigue_el_orden_de_etapas_pipeline():
    resultado = _fuera_de_muestra()

    assert list(resultado.in_sample.por_etapa) == list(ETAPAS_PIPELINE)
    assert list(resultado.out_of_sample.por_etapa) == list(ETAPAS_PIPELINE)
    en_muestra = {e: (r.casos, r.aciertos_estrictos, r.aciertos_laxos) for e, r in resultado.in_sample.por_etapa.items()}
    fuera = {e: (r.casos, r.aciertos_estrictos, r.aciertos_laxos) for e, r in resultado.out_of_sample.por_etapa.items()}
    assert en_muestra == {"deterministic": (8, 8, 8), "gemini": (12, 9, 9), "fallback": (4, 3, 3)}
    assert fuera == {"deterministic": (4, 3, 4), "gemini": (6, 4, 4), "fallback": (2, 1, 1)}
    assert resultado.out_of_sample.por_etapa["gemini"].ic_estricta == pytest.approx(
        intervalo_wilson(4, 6), abs=1e-12
    )


def test_los_bloques_no_se_mezclan_y_declaran_su_version_y_cantidad_de_casos():
    resultado = _fuera_de_muestra()

    assert resultado.in_sample.casos == 24 and resultado.out_of_sample.casos == 12
    assert resultado.in_sample.classifier_version == resultado.out_of_sample.classifier_version == "hybrid-v3"
    assert resultado.in_sample.rotulo != resultado.out_of_sample.rotulo


# ---------------------------------------------------------------------------
# 7.3 — triangulacion: version, pines y commit del clasificador congelado
# ---------------------------------------------------------------------------
def _cache_con_meta(origen, destino, **cambios) -> pathlib.Path:
    """Copia un cache de predicciones a `destino` cambiando campos de su `cache_meta`."""
    documento = h.leer_json(origen)
    documento["cache_meta"].update(cambios)
    return h.escribir_json(destino / f"cache_{len(list(destino.iterdir()))}.json", documento)


def _fuera_de_muestra_con(*, in_sample=None, independiente=None, **cambios):
    argumentos = {
        "pines_in_sample": h.PINES_IN_SAMPLE,
        "rango_google_genai_vigente": h.RANGO_VIGENTE_GOOGLE_GENAI,
    }
    argumentos.update(cambios)
    return evaluar_fuera_de_muestra(
        in_sample or h.PREDICCIONES_IN_SAMPLE,
        h.CORPUS_CAMPANA,
        independiente or h.PREDICCIONES_INDEPENDIENTE,
        h.CORPUS_INDEPENDIENTE,
        **argumentos,
    )


def test_una_classifier_version_distinta_aborta_mostrando_ambos_valores():
    with pytest.raises(FueraDeMuestraError) as excinfo:
        _fuera_de_muestra_con(independiente=h.PREDICCIONES_INDEPENDIENTE_VERSION)

    mensaje = str(excinfo.value)
    assert "classifier_version" in mensaje and "hybrid-v3" in mensaje and "hybrid-v4" in mensaje


def test_un_modelo_distinto_en_los_pines_aborta_mostrando_ambos_valores():
    with pytest.raises(FueraDeMuestraError) as excinfo:
        _fuera_de_muestra_con(independiente=h.PREDICCIONES_INDEPENDIENTE_PINES)

    mensaje = str(excinfo.value)
    assert "gemini-3.6-flash" in mensaje and "gemini-3.5-flash" in mensaje


@pytest.mark.parametrize(
    ("version_instalada", "rango_violado"),
    [("2.19.0", ">=2.20.0"), ("2.32.0", ">=2.33,<3"), ("3.0.0", ">=2.33,<3"), ("1.9.0", ">=2.20.0")],
)
def test_una_version_instalada_fuera_del_rango_in_sample_o_del_pin_vigente_aborta(
    tmp_path, version_instalada, rango_violado
):
    independiente = _cache_con_meta(
        h.PREDICCIONES_INDEPENDIENTE,
        tmp_path,
        pines={"google_genai": version_instalada, "modelo": "gemini-3.6-flash"},
    )

    with pytest.raises(FueraDeMuestraError) as excinfo:
        _fuera_de_muestra_con(independiente=independiente)

    mensaje = str(excinfo.value)
    assert version_instalada in mensaje and rango_violado in mensaje


@pytest.mark.parametrize("version_instalada", ["2.33.0", "2.34.0", "2.99.9"])
def test_una_version_instalada_que_cumple_ambos_rangos_no_aborta(tmp_path, version_instalada):
    independiente = _cache_con_meta(
        h.PREDICCIONES_INDEPENDIENTE,
        tmp_path,
        pines={"google_genai": version_instalada, "modelo": "gemini-3.6-flash"},
    )

    resultado = _fuera_de_muestra_con(independiente=independiente)

    assert resultado.obtenido is True
    assert resultado.comparabilidad.google_genai_instalada == version_instalada


def test_si_el_in_sample_registra_una_version_exacta_se_exige_la_igualdad(tmp_path):
    independiente = _cache_con_meta(
        h.PREDICCIONES_INDEPENDIENTE, tmp_path, pines={"google_genai": "2.34.0", "modelo": "gemini-3.6-flash"}
    )
    exactos = {"google_genai": "2.34.0", "modelo": "gemini-3.6-flash"}

    resultado = _fuera_de_muestra_con(independiente=independiente, pines_in_sample=exactos)

    assert resultado.obtenido is True
    assert not any("versión instalada in-sample no registrada" in limitacion for limitacion in resultado.limitaciones)
    with pytest.raises(FueraDeMuestraError, match="2.34.0"):
        _fuera_de_muestra_con(
            independiente=independiente, pines_in_sample={"google_genai": "2.30.0", "modelo": "gemini-3.6-flash"}
        )


def test_sin_pines_in_sample_la_seccion_falla_y_manda_al_readme():
    with pytest.raises(FueraDeMuestraError) as excinfo:
        evaluar_fuera_de_muestra(
            h.PREDICCIONES_IN_SAMPLE,
            h.CORPUS_CAMPANA,
            h.PREDICCIONES_INDEPENDIENTE,
            h.CORPUS_INDEPENDIENTE,
            rango_google_genai_vigente=h.RANGO_VIGENTE_GOOGLE_GENAI,
        )

    mensaje = str(excinfo.value)
    assert "pines_in_sample" in mensaje and "README de evaluation/data/campana/" in mensaje


@pytest.mark.parametrize("pines", [{"google_genai": ">=2.20.0"}, {"modelo": "gemini-3.6-flash"}, {}])
def test_unos_pines_in_sample_incompletos_fallan_y_nombran_la_clave_faltante(pines):
    with pytest.raises(FueraDeMuestraError) as excinfo:
        _fuera_de_muestra_con(pines_in_sample=pines)

    assert ("modelo" in str(excinfo.value)) or ("google_genai" in str(excinfo.value))


def test_sin_el_pin_vigente_de_la_configuracion_la_seccion_falla_y_lo_pide():
    with pytest.raises(FueraDeMuestraError) as excinfo:
        evaluar_fuera_de_muestra(
            h.PREDICCIONES_IN_SAMPLE,
            h.CORPUS_CAMPANA,
            h.PREDICCIONES_INDEPENDIENTE,
            h.CORPUS_INDEPENDIENTE,
            pines_in_sample=h.PINES_IN_SAMPLE,
        )

    assert "openspec/config.yaml" in str(excinfo.value)


def test_un_rango_que_no_se_puede_interpretar_falla_y_lo_nombra():
    with pytest.raises(FueraDeMuestraError, match="algo-raro"):
        _fuera_de_muestra_con(rango_google_genai_vigente="algo-raro")


def test_un_commit_distinto_aborta_cuando_ambos_bloques_lo_registran(tmp_path):
    in_sample = _cache_con_meta(h.PREDICCIONES_IN_SAMPLE, tmp_path, commit="d6bb474")

    with pytest.raises(FueraDeMuestraError) as excinfo:
        _fuera_de_muestra_con(in_sample=in_sample)

    mensaje = str(excinfo.value)
    assert "commit" in mensaje and "d6bb474" in mensaje and "c167aa1" in mensaje


def test_un_commit_in_sample_provisto_por_parametro_tambien_se_compara():
    with pytest.raises(FueraDeMuestraError) as excinfo:
        _fuera_de_muestra_con(commit_in_sample="d6bb474")

    assert "d6bb474" in str(excinfo.value) and "c167aa1" in str(excinfo.value)


def test_un_commit_igual_en_ambos_bloques_no_declara_la_limitacion_del_commit(tmp_path):
    in_sample = _cache_con_meta(h.PREDICCIONES_IN_SAMPLE, tmp_path, commit="c167aa1")

    resultado = _fuera_de_muestra_con(in_sample=in_sample)

    assert resultado.comparabilidad.commit_in_sample == resultado.comparabilidad.commit_independiente == "c167aa1"
    assert not any("commit in-sample no registrado" in limitacion for limitacion in resultado.limitaciones)
    assert _fuera_de_muestra_con(commit_in_sample="c167aa1").comparabilidad.commit_in_sample == "c167aa1"


def test_sin_commit_in_sample_no_aborta_y_declara_la_limitacion():
    resultado = _fuera_de_muestra_con()

    assert resultado.obtenido is True
    assert resultado.comparabilidad.commit_in_sample is None
    assert resultado.comparabilidad.commit_independiente == "c167aa1"
    assert (
        "commit in-sample no registrado; comparabilidad verificada por versión y pines"
        in resultado.limitaciones
    )


def test_la_salida_declara_que_la_version_instalada_in_sample_no_esta_registrada():
    resultado = _fuera_de_muestra_con()

    limitacion = next(
        texto for texto in resultado.limitaciones if "versión instalada in-sample no registrada" in texto
    )
    assert ">=2.20.0" in limitacion and "2.34.0" in limitacion and ">=2.33,<3" in limitacion


def test_la_comparabilidad_informa_version_modelo_rangos_y_commits():
    comparabilidad = _fuera_de_muestra_con().comparabilidad

    assert comparabilidad.classifier_version == "hybrid-v3"
    assert comparabilidad.modelo == "gemini-3.6-flash"
    assert comparabilidad.google_genai_instalada == "2.34.0"
    assert comparabilidad.rango_in_sample == ">=2.20.0"
    assert comparabilidad.rango_vigente == ">=2.33,<3"


def test_un_cache_independiente_sin_pines_falla_y_pide_regenerarlo(tmp_path):
    documento = h.leer_json(h.PREDICCIONES_INDEPENDIENTE)
    del documento["cache_meta"]["pines"]
    independiente = h.escribir_json(tmp_path / "sin_pines.json", documento)

    with pytest.raises(FueraDeMuestraError, match="pines"):
        _fuera_de_muestra_con(independiente=independiente)


def test_un_cache_sin_cache_meta_o_sin_classifier_version_falla(tmp_path):
    documento = h.leer_json(h.PREDICCIONES_INDEPENDIENTE)
    del documento["cache_meta"]["classifier_version"]
    sin_version = h.escribir_json(tmp_path / "sin_version.json", documento)
    sin_meta = h.escribir_json(tmp_path / "sin_meta.json", {"predictions": documento["predictions"]})

    with pytest.raises(FueraDeMuestraError, match="classifier_version"):
        _fuera_de_muestra_con(independiente=sin_version)
    with pytest.raises(FueraDeMuestraError, match="cache_meta"):
        _fuera_de_muestra_con(independiente=sin_meta)


# ---------------------------------------------------------------------------
# 7.4 — no solape (c-166) y alineacion de las predicciones con su corpus
# ---------------------------------------------------------------------------
def _corpus_independiente_con(tmp_path, cambio) -> pathlib.Path:
    documento = h.leer_json(h.CORPUS_INDEPENDIENTE)
    cambio(documento["casos"])
    return h.escribir_json(tmp_path / "corpus_independiente_modificado.json", documento)


def _evaluar_con_corpus_independiente(corpus_independiente, predicciones_independiente=None):
    return evaluar_fuera_de_muestra(
        h.PREDICCIONES_IN_SAMPLE,
        h.CORPUS_CAMPANA,
        predicciones_independiente or h.PREDICCIONES_INDEPENDIENTE,
        corpus_independiente,
        pines_in_sample=h.PINES_IN_SAMPLE,
        rango_google_genai_vigente=h.RANGO_VIGENTE_GOOGLE_GENAI,
    )


def test_un_corpus_independiente_en_solape_aborta_nombrando_los_casos_en_solape():
    with pytest.raises(FueraDeMuestraError) as excinfo:
        _evaluar_con_corpus_independiente(h.CORPUS_INDEPENDIENTE_SOLAPE)

    mensaje = str(excinfo.value)
    assert "I012" in mensaje and "S05" in mensaje and "no es independiente" in mensaje


def test_un_id_sin_el_prefijo_i_en_el_corpus_independiente_aborta(tmp_path):
    def renombrar(casos):
        casos[2]["id"] = "X003"

    with pytest.raises(FueraDeMuestraError) as excinfo:
        _evaluar_con_corpus_independiente(_corpus_independiente_con(tmp_path, renombrar))

    assert "X003" in str(excinfo.value)


def test_el_solape_se_verifica_de_nuevo_en_cada_evaluacion(monkeypatch):
    llamadas = []
    real = campana.verificar_no_solape

    def espia(ajuste, candidato, *args, **kwargs):
        llamadas.append((len(ajuste), len(candidato)))
        return real(ajuste, candidato, *args, **kwargs)

    monkeypatch.setattr(campana, "verificar_no_solape", espia)

    _fuera_de_muestra()

    assert llamadas == [(24, 12)]


def test_predicciones_que_no_cubren_un_caso_del_corpus_abortan_nombrando_el_caso(tmp_path):
    documento = h.leer_json(h.PREDICCIONES_INDEPENDIENTE)
    documento["predictions"] = [p for p in documento["predictions"] if p["caso_id"] != "I005"]
    incompleto = h.escribir_json(tmp_path / "incompleto.json", documento)

    with pytest.raises(FueraDeMuestraError) as excinfo:
        _evaluar_con_corpus_independiente(h.CORPUS_INDEPENDIENTE, incompleto)

    mensaje = str(excinfo.value)
    assert "I005" in mensaje and "independiente" in mensaje


def test_una_prediccion_de_un_caso_que_el_corpus_no_tiene_aborta(tmp_path):
    documento = h.leer_json(h.PREDICCIONES_INDEPENDIENTE)
    documento["predictions"][0]["caso_id"] = "I999"
    desalineado = h.escribir_json(tmp_path / "desalineado.json", documento)

    with pytest.raises(FueraDeMuestraError) as excinfo:
        _evaluar_con_corpus_independiente(h.CORPUS_INDEPENDIENTE, desalineado)

    assert "I999" in str(excinfo.value) and "I001" in str(excinfo.value)


def test_una_prediccion_repetida_para_un_caso_aborta(tmp_path):
    documento = h.leer_json(h.PREDICCIONES_INDEPENDIENTE)
    documento["predictions"].append(dict(documento["predictions"][0]))
    repetido = h.escribir_json(tmp_path / "repetido.json", documento)

    with pytest.raises(FueraDeMuestraError, match="I001"):
        _evaluar_con_corpus_independiente(h.CORPUS_INDEPENDIENTE, repetido)


def test_un_sector_asignado_que_difiere_del_corpus_aborta_nombrando_el_caso(tmp_path):
    documento = h.leer_json(h.PREDICCIONES_INDEPENDIENTE)
    documento["predictions"][3]["sector_asignado"] = HW  # I004 es de Seguridad Informatica
    distinto = h.escribir_json(tmp_path / "distinto.json", documento)

    with pytest.raises(FueraDeMuestraError) as excinfo:
        _evaluar_con_corpus_independiente(h.CORPUS_INDEPENDIENTE, distinto)

    assert "I004" in str(excinfo.value)


def test_una_etapa_fuera_de_la_cascada_aborta_nombrando_caso_y_etapa(tmp_path):
    documento = h.leer_json(h.PREDICCIONES_INDEPENDIENTE)
    documento["predictions"][5]["etapa"] = "manual"
    con_etapa_rara = h.escribir_json(tmp_path / "etapa_rara.json", documento)

    with pytest.raises(FueraDeMuestraError) as excinfo:
        _evaluar_con_corpus_independiente(h.CORPUS_INDEPENDIENTE, con_etapa_rara)

    assert "I006" in str(excinfo.value) and "manual" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 7.5 — artefactos ausentes: la seccion se declara "no se obtuvo"
# ---------------------------------------------------------------------------
def test_sin_corpus_independiente_la_seccion_no_se_obtuvo_y_no_trae_metricas_in_sample(tmp_path):
    resultado = _evaluar_con_corpus_independiente(tmp_path / "corpus_independiente.json")

    assert resultado.obtenido is False
    assert resultado.faltantes == ("corpus_independiente.json",)
    assert "no se obtuvo" in resultado.motivo and "corpus_independiente.json" in resultado.motivo
    assert resultado.in_sample is None and resultado.out_of_sample is None
    assert resultado.comparabilidad is None


def test_sin_predicciones_independientes_la_seccion_no_se_obtuvo_nombrando_el_artefacto(tmp_path):
    resultado = _evaluar_con_corpus_independiente(
        h.CORPUS_INDEPENDIENTE, tmp_path / "predicciones_independiente.json"
    )

    assert resultado.obtenido is False
    assert resultado.faltantes == ("predicciones_independiente.json",)
    assert resultado.in_sample is None and resultado.out_of_sample is None


def test_si_faltan_varios_artefactos_se_nombran_todos(tmp_path):
    resultado = evaluar_fuera_de_muestra(
        tmp_path / "predicciones.json",
        h.CORPUS_CAMPANA,
        tmp_path / "predicciones_independiente.json",
        tmp_path / "corpus_independiente.json",
    )

    assert resultado.obtenido is False
    assert resultado.faltantes == (
        "predicciones.json",
        "predicciones_independiente.json",
        "corpus_independiente.json",
    )


def test_con_los_artefactos_ausentes_no_se_exigen_los_pines_porque_no_hay_nada_que_comparar(tmp_path):
    resultado = evaluar_fuera_de_muestra(
        h.PREDICCIONES_IN_SAMPLE,
        h.CORPUS_CAMPANA,
        tmp_path / "predicciones_independiente.json",
        tmp_path / "corpus_independiente.json",
    )

    assert resultado.obtenido is False


# ---------------------------------------------------------------------------
# 7.6 — nunca se llama a Gemini ni se reescriben los artefactos de v9
# ---------------------------------------------------------------------------
def test_la_evaluacion_fuera_de_muestra_no_invoca_main_ni_el_clasificador_real(monkeypatch):
    from evaluation import run_evaluation

    def prohibido(*args, **kwargs):
        raise AssertionError("la evaluacion fuera de muestra no puede llamar a Gemini")

    for nombre in ("main", "main_con_corpus_real", "main_solo_tiempos", "_resolver_clasificador_real", "evaluar_corpus"):
        monkeypatch.setattr(run_evaluation, nombre, prohibido)

    resultado = _fuera_de_muestra()

    assert resultado.obtenido is True


def test_el_modulo_no_importa_ni_llama_al_clasificador_real():
    arbol = ast.parse(inspect.getsource(campana))
    identificadores = {nodo.id for nodo in ast.walk(arbol) if isinstance(nodo, ast.Name)}
    identificadores |= {nodo.attr for nodo in ast.walk(arbol) if isinstance(nodo, ast.Attribute)}
    importados = {
        alias.name for nodo in ast.walk(arbol) if isinstance(nodo, ast.ImportFrom) for alias in nodo.names
    }

    prohibidos = {"main", "main_con_corpus_real", "main_solo_tiempos", "_resolver_clasificador_real", "HybridClassifier", "evaluar_corpus"}
    assert not (identificadores | importados) & prohibidos


def test_los_artefactos_de_v9_conservan_su_sha256_tras_la_evaluacion():
    # `report.md` esta versionado y SIEMPRE se verifica (la evaluacion fuera de
    # muestra no puede reescribirlo). `predicciones.json` es una cache real
    # derivada del corpus con PII, ignorada por git (ver .gitignore, "Caches de
    # predicciones del framework de evaluacion"): no existe en un checkout limpio
    # / CI. Se hashea solo cuando esta presente, para conservar la proteccion
    # local sin romper la suite en CI; la limitacion queda declarada por este
    # comentario y por el assert de que `report.md` siempre integra la lista.
    reales = [h.RAIZ_EVALUATION / "report.md", h.RAIZ_EVALUATION / "predicciones.json"]
    presentes = [ruta for ruta in reales if ruta.exists()]
    assert h.RAIZ_EVALUATION / "report.md" in presentes  # artefacto versionado: obligatorio
    antes = {ruta: hashlib.sha256(ruta.read_bytes()).hexdigest() for ruta in presentes}
    fixtures = [h.PREDICCIONES_IN_SAMPLE, h.PREDICCIONES_INDEPENDIENTE, h.CORPUS_CAMPANA, h.CORPUS_INDEPENDIENTE]
    antes.update({ruta: hashlib.sha256(ruta.read_bytes()).hexdigest() for ruta in fixtures})

    _fuera_de_muestra()

    for ruta, huella in antes.items():
        assert hashlib.sha256(ruta.read_bytes()).hexdigest() == huella, ruta


def test_un_corpus_con_total_casos_desincronizado_no_se_reescribe(tmp_path):
    documento = h.leer_json(h.CORPUS_CAMPANA)
    documento["metadata"]["total_casos"] = 999  # cargar_corpus lo corregiria y reescribiria el archivo
    desincronizado = h.escribir_json(tmp_path / "corpus_desincronizado.json", documento)
    antes = desincronizado.read_bytes()

    resultado = evaluar_fuera_de_muestra(
        h.PREDICCIONES_IN_SAMPLE,
        desincronizado,
        h.PREDICCIONES_INDEPENDIENTE,
        h.CORPUS_INDEPENDIENTE,
        pines_in_sample=h.PINES_IN_SAMPLE,
        rango_google_genai_vigente=h.RANGO_VIGENTE_GOOGLE_GENAI,
    )

    assert resultado.obtenido is True
    assert desincronizado.read_bytes() == antes
