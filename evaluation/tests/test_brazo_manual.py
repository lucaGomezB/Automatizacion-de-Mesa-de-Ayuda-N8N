"""
Tests del instrumento del brazo manual (c-165, ECM-001).

El brazo manual se captura OFFLINE en la planilla unica de c-168 (`tarea = brazo_manual`)
y se valida con el validador unico de c-168; c-165 NO define esquema ni reglas de reparto
propias. Estos tests cubren, en orden:

1. (tarea 1.1) una planilla sintetica de operadores `O1`/`O2` valida contra el validador de
   c-168, y las tres violaciones del reparto o de los tiempos (caso sin operador, registro
   duplicado, fila sin `inicio`) se rechazan con la regla de c-168 que corresponde;
2. (tarea 1.2) `reconstruir_posicion_real`: posicion de cada caso desde `inicio`;
3. (tarea 1.3) `desvios_respecto_del_plan`: posicion planeada contra posicion real;
4. (tarea 1.4) el modulo no duplica esquema, columnas ni cadenas y no hace entrada/salida.

Todo corre sin red. Los fixtures son SINTETICOS (ver `tests/fixtures/README.md`):
`campana/corpus_brazo_manual_fixture.json` (6 casos `R001..R006`),
`campana/plan_campana_brazo_manual_fixture.csv` (plan de c-166 sobre esos casos, generado
con `python -m evaluation.plan_campana generar --modo aleatorio --seed 4`) y
`campana/brazo_manual_fixture.csv` (planilla de `O1`/`O2` que sigue ese plan). El corpus se
carga desde una copia en `tmp_path` porque `cargar_corpus` puede reescribir
`metadata.total_casos`.
"""

from __future__ import annotations

import ast
import csv
import inspect
import pathlib
import random
import shutil
from datetime import datetime

import pytest

from evaluation import brazo_manual, plan_campana
from evaluation.brazo_manual import (
    BrazoManualError,
    PosicionReal,
    desvios_respecto_del_plan,
    reconstruir_posicion_real,
)
from evaluation.corpus import SECTORES_CANONICOS, cargar_corpus
from evaluation.doble_etiquetado import COLUMNAS_C1, validar_doble_etiquetado
from evaluation.plan_campana import AsignacionCaso, leer_plan_csv

RAIZ_EVALUATION = pathlib.Path(__file__).resolve().parents[1]
PLANTILLA_PATH = RAIZ_EVALUATION / "data" / "plantilla_etiquetado.csv"
DIR_CAMPANA = RAIZ_EVALUATION / "tests" / "fixtures" / "campana"
CORPUS_PATH = DIR_CAMPANA / "corpus_brazo_manual_fixture.json"
PLAN_PATH = DIR_CAMPANA / "plan_campana_brazo_manual_fixture.csv"
PLANILLA_PATH = DIR_CAMPANA / "brazo_manual_fixture.csv"

TAREA = "brazo_manual"


# ---------------------------------------------------------------------------
# Helpers y fixtures
# ---------------------------------------------------------------------------
def _leer_csv(ruta: pathlib.Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


@pytest.fixture(scope="module")
def corpus(tmp_path_factory):
    """Corpus sintetico de 6 casos (`R001..R006`), cargado desde una copia en tmp_path."""
    copia = tmp_path_factory.mktemp("corpus_brazo_manual") / CORPUS_PATH.name
    shutil.copyfile(CORPUS_PATH, copia)
    return cargar_corpus(copia)


@pytest.fixture
def planilla() -> list[dict[str, str]]:
    """Planilla `brazo_manual` valida (fixture SINTETICO), mutable por test."""
    return _leer_csv(PLANILLA_PATH)


@pytest.fixture(scope="module")
def plan():
    """Plan de campana de c-166 sobre los 6 casos, leido con el lector de c-166."""
    return leer_plan_csv(PLAN_PATH)


def _ofensas_de(resultado, regla: str) -> list:
    return [o for o in resultado.ofensas if o.regla == regla]


def _fila_de(planilla: list[dict[str, str]], id_caso: str, operador: str) -> dict[str, str]:
    return next(f for f in planilla if f["id_caso"] == id_caso and f["id_etiquetador"] == operador)


def _fila(
    id_caso: str, operador: str, inicio: str, timestamp: str | None = None
) -> dict[str, str]:
    """Fila `brazo_manual` con las siete columnas de c-168; `timestamp` por defecto = `inicio`."""
    return {
        "id_caso": id_caso,
        "id_etiquetador": operador,
        "tarea": TAREA,
        "sector_etiquetado": SECTORES_CANONICOS[0],
        "sectores_adicionales_etiquetados": "",
        "inicio": inicio,
        "timestamp": inicio if timestamp is None else timestamp,
    }


def _intercambiar_tiempos(planilla, uno: tuple[str, str], otro: tuple[str, str]) -> None:
    """Intercambia `inicio` y `timestamp` de dos filas `(id_caso, operador)` de la planilla."""
    fila_uno, fila_otro = _fila_de(planilla, *uno), _fila_de(planilla, *otro)
    for columna in ("inicio", "timestamp"):
        fila_uno[columna], fila_otro[columna] = fila_otro[columna], fila_uno[columna]


def _posiciones(resultado) -> list[tuple[str, str, int]]:
    return [(p.id_etiquetador, p.id_caso, p.posicion) for p in resultado]


def _desvios(resultado) -> list[tuple[str, str, int, int]]:
    return [
        (d.id_etiquetador, d.id_caso, d.posicion_planeada, d.posicion_real) for d in resultado
    ]


# ---------------------------------------------------------------------------
# 1.1 — La planilla del brazo manual valida con el validador unico de c-168
# ---------------------------------------------------------------------------
def test_planilla_sintetica_de_operadores_valida_con_el_validador_de_c168(corpus, planilla):
    resultado = validar_doble_etiquetado(planilla, corpus, tarea=TAREA)

    assert resultado.valida, resultado.ofensas
    assert resultado.resumen.n_casos == 6
    assert resultado.resumen.n_registros == 7
    assert resultado.resumen.etiquetadores == ("O1", "O2")


def test_planilla_usa_el_encabezado_de_la_plantilla_de_c168_con_inicio_antes_de_timestamp():
    with PLANILLA_PATH.open(encoding="utf-8", newline="") as archivo:
        encabezado = next(csv.reader(archivo))
    with PLANTILLA_PATH.open(encoding="utf-8", newline="") as archivo:
        encabezado_plantilla = next(csv.reader(archivo))

    assert encabezado == encabezado_plantilla
    assert tuple(encabezado) == COLUMNAS_C1
    assert encabezado[-2:] == ["inicio", "timestamp"]


@pytest.mark.parametrize("operador", ["O1", "O2"])
def test_cada_operador_registra_sector_canonico_e_instantes_con_zona(planilla, operador):
    filas = [fila for fila in planilla if fila["id_etiquetador"] == operador]

    assert filas, f"el fixture no tiene filas del operador {operador}"
    for fila in filas:
        inicio = datetime.fromisoformat(fila["inicio"])
        fin = datetime.fromisoformat(fila["timestamp"])
        assert fila["tarea"] == TAREA
        assert fila["sector_etiquetado"] in SECTORES_CANONICOS
        assert inicio.tzinfo is not None and fin.tzinfo is not None
        assert inicio < fin


def test_reparto_por_mitades_segun_el_plan_con_un_caso_de_doble_cobertura(planilla, plan):
    mitad_de = {fila.id_caso: fila.mitad for fila in plan}
    casos_de = {
        operador: {f["id_caso"] for f in planilla if f["id_etiquetador"] == operador}
        for operador in ("O1", "O2")
    }
    primera_mitad = {caso for caso, mitad in mitad_de.items() if mitad == 1}
    segunda_mitad = {caso for caso, mitad in mitad_de.items() if mitad == 2}

    assert primera_mitad <= casos_de["O1"]
    assert segunda_mitad == casos_de["O2"]
    doble_cobertura = casos_de["O1"] & casos_de["O2"]
    assert len(doble_cobertura) == 1
    assert casos_de["O1"] | casos_de["O2"] == set(mitad_de)


# R005 solo lo clasifica O1 y R003 solo O2: ambos lados del reparto quedan cubiertos.
@pytest.mark.parametrize("id_caso", ["R005", "R003"])
def test_caso_del_plan_sin_ningun_operador_es_rechazado_por_el_validador(
    corpus, planilla, id_caso
):
    sin_el_caso = [fila for fila in planilla if fila["id_caso"] != id_caso]

    resultado = validar_doble_etiquetado(sin_el_caso, corpus, tarea=TAREA)

    assert not resultado.valida
    assert [o.id_caso for o in _ofensas_de(resultado, "b")] == [id_caso]
    assert {o.regla for o in resultado.ofensas} == {"b"}


@pytest.mark.parametrize("id_caso, operador", [("R004", "O1"), ("R003", "O2")])
def test_registro_duplicado_por_caso_y_operador_es_rechazado_por_el_validador(
    corpus, planilla, id_caso, operador
):
    duplicada = dict(_fila_de(planilla, id_caso, operador))

    resultado = validar_doble_etiquetado([*planilla, duplicada], corpus, tarea=TAREA)

    assert not resultado.valida
    reglas_c = _ofensas_de(resultado, "c")
    assert [(o.id_caso, o.id_etiquetador) for o in reglas_c] == [(id_caso, operador)]


@pytest.mark.parametrize("id_caso, operador", [("R001", "O2"), ("R004", "O1")])
def test_fila_de_brazo_manual_sin_inicio_es_rechazada_e_informa_la_fila(
    corpus, planilla, id_caso, operador
):
    _fila_de(planilla, id_caso, operador)["inicio"] = ""

    resultado = validar_doble_etiquetado(planilla, corpus, tarea=TAREA)

    assert not resultado.valida
    reglas_j = _ofensas_de(resultado, "j")
    assert [(o.id_caso, o.id_etiquetador) for o in reglas_j] == [(id_caso, operador)]


# ---------------------------------------------------------------------------
# 1.2 — reconstruir_posicion_real: posiciones 1..N por `inicio` dentro de cada operador
# ---------------------------------------------------------------------------
def test_posicion_real_sigue_el_orden_de_inicio_dentro_de_cada_operador(planilla):
    # La planilla del fixture esta ordenada por id_caso: la posicion no es el orden de fila.
    resultado = reconstruir_posicion_real(planilla)

    assert _posiciones(resultado) == [
        ("O1", "R004", 1),
        ("O1", "R005", 2),
        ("O1", "R006", 3),
        ("O1", "R002", 4),
        ("O2", "R003", 1),
        ("O2", "R001", 2),
        ("O2", "R002", 3),
    ]


def test_cada_operador_tiene_su_propia_secuencia_aunque_trabajen_los_mismos_casos_al_reves():
    filas = [
        _fila("R001", "O1", "2026-11-17T10:00:00-03:00"),
        _fila("R002", "O1", "2026-11-17T10:05:00-03:00"),
        _fila("R003", "O1", "2026-11-17T10:10:00-03:00"),
        _fila("R003", "O2", "2026-11-17T14:00:00-03:00"),
        _fila("R002", "O2", "2026-11-17T14:05:00-03:00"),
        _fila("R001", "O2", "2026-11-17T14:10:00-03:00"),
    ]

    resultado = reconstruir_posicion_real(filas)

    assert _posiciones(resultado) == [
        ("O1", "R001", 1),
        ("O1", "R002", 2),
        ("O1", "R003", 3),
        ("O2", "R003", 1),
        ("O2", "R002", 2),
        ("O2", "R001", 3),
    ]


def test_el_orden_usa_el_instante_y_no_el_texto_cuando_las_zonas_horarias_difieren():
    # Instantes reales: R002 = 12:30Z, R003 = 12:45Z, R001 = 13:00Z. Ordenados como texto
    # ("10:00-03:00" < "12:30+00:00" < "12:45Z") darian R001, R002, R003.
    filas = [
        _fila("R001", "O1", "2026-11-17T10:00:00-03:00"),
        _fila("R002", "O1", "2026-11-17T12:30:00+00:00"),
        _fila("R003", "O1", "2026-11-17T12:45:00Z"),
    ]

    resultado = reconstruir_posicion_real(filas)

    assert _posiciones(resultado) == [("O1", "R002", 1), ("O1", "R003", 2), ("O1", "R001", 3)]


def test_el_desempate_de_un_mismo_inicio_es_el_timestamp_aunque_se_exprese_en_otra_zona():
    # Ambos inicios son el mismo instante (13:00Z) escrito en dos zonas; R002 termina antes.
    filas = [
        _fila("R001", "O1", "2026-11-17T10:00:00-03:00", "2026-11-17T10:02:00-03:00"),
        _fila("R002", "O1", "2026-11-17T13:00:00+00:00", "2026-11-17T10:01:00-03:00"),
    ]

    resultado = reconstruir_posicion_real(filas)

    assert _posiciones(resultado) == [("O1", "R002", 1), ("O1", "R001", 2)]


@pytest.mark.parametrize("ids_en_el_orden_de_llegada", [("R002", "R001"), ("R001", "R002")])
def test_ante_un_empate_exacto_de_inicio_y_timestamp_desempata_el_id_caso(
    ids_en_el_orden_de_llegada,
):
    filas = [
        _fila(id_caso, "O1", "2026-11-17T10:00:00-03:00")
        for id_caso in ids_en_el_orden_de_llegada
    ]

    resultado = reconstruir_posicion_real(filas)

    assert _posiciones(resultado) == [("O1", "R001", 1), ("O1", "R002", 2)]


def test_el_resultado_no_depende_del_orden_en_que_llegan_las_filas(planilla):
    esperado = _posiciones(reconstruir_posicion_real(planilla))

    for semilla in range(5):
        barajada = list(planilla)
        random.Random(semilla).shuffle(barajada)
        assert _posiciones(reconstruir_posicion_real(barajada)) == esperado


def test_sin_filas_no_hay_posiciones():
    assert reconstruir_posicion_real([]) == []


@pytest.mark.parametrize(
    "inicio",
    [
        pytest.param("", id="vacio"),
        pytest.param(None, id="ausente"),
        pytest.param("2026-11-17T10:00:00", id="sin_zona_horaria"),
        pytest.param("ayer a la tarde", id="ilegible"),
    ],
)
def test_una_fila_con_inicio_invalido_levanta_un_error_que_nombra_campo_operador_y_caso(inicio):
    filas = [
        _fila("R001", "O1", "2026-11-17T10:00:00-03:00"),
        _fila("R002", "O2", "2026-11-17T10:05:00-03:00"),
    ]
    filas[1]["inicio"] = inicio

    with pytest.raises(BrazoManualError) as error:
        reconstruir_posicion_real(filas)

    mensaje = str(error.value)
    assert "inicio" in mensaje and "O2" in mensaje and "R002" in mensaje


def test_una_fila_con_timestamp_invalido_levanta_un_error_que_nombra_el_campo():
    filas = [_fila("R001", "O1", "2026-11-17T10:00:00-03:00", "sin hora")]

    with pytest.raises(BrazoManualError) as error:
        reconstruir_posicion_real(filas)

    mensaje = str(error.value)
    assert "timestamp" in mensaje and "O1" in mensaje and "R001" in mensaje


def test_un_mismo_caso_dos_veces_para_el_mismo_operador_levanta_un_error():
    filas = [
        _fila("R001", "O1", "2026-11-17T10:00:00-03:00"),
        _fila("R001", "O1", "2026-11-17T10:05:00-03:00"),
    ]

    with pytest.raises(BrazoManualError) as error:
        reconstruir_posicion_real(filas)

    mensaje = str(error.value)
    assert "R001" in mensaje and "O1" in mensaje


def test_los_errores_del_brazo_manual_se_pueden_capturar_como_value_error():
    with pytest.raises(ValueError):
        reconstruir_posicion_real([_fila("R001", "O1", "sin hora")])


# ---------------------------------------------------------------------------
# 1.3 — desvios_respecto_del_plan: posicion planeada vs posicion real
# ---------------------------------------------------------------------------
def test_una_planilla_que_sigue_el_plan_no_tiene_desvios(planilla, plan):
    # El fixture hace R005 (posicion 3) antes que R006 (posicion 2): es el turno 1 antes que
    # el turno 2 de la mitad 1, que es lo que el runbook de c-166 le pide al operador manual.
    posiciones = reconstruir_posicion_real(planilla)

    assert desvios_respecto_del_plan(posiciones, plan) == []


def test_un_caso_adelantado_se_reporta_con_su_posicion_planeada_y_real(planilla, plan):
    # O1 toma R006 antes que R005: R006 pasa del lugar planeado 3 al real 2 y R005 del 2 al 3.
    _intercambiar_tiempos(planilla, ("R005", "O1"), ("R006", "O1"))

    resultado = desvios_respecto_del_plan(reconstruir_posicion_real(planilla), plan)

    assert _desvios(resultado) == [("O1", "R006", 3, 2), ("O1", "R005", 2, 3)]


def test_los_desvios_se_ordenan_por_operador_y_por_posicion_real(planilla, plan):
    _intercambiar_tiempos(planilla, ("R005", "O1"), ("R006", "O1"))
    _intercambiar_tiempos(planilla, ("R003", "O2"), ("R001", "O2"))

    resultado = desvios_respecto_del_plan(reconstruir_posicion_real(planilla), plan)

    assert _desvios(resultado) == [
        ("O1", "R006", 3, 2),
        ("O1", "R005", 2, 3),
        ("O2", "R001", 2, 1),
        ("O2", "R003", 1, 2),
    ]


def test_un_desvio_de_un_operador_no_se_atribuye_al_otro(planilla, plan):
    _intercambiar_tiempos(planilla, ("R003", "O2"), ("R001", "O2"))

    resultado = desvios_respecto_del_plan(reconstruir_posicion_real(planilla), plan)

    assert {d.id_etiquetador for d in resultado} == {"O2"}


def test_un_caso_de_la_segunda_mitad_tomado_antes_de_tiempo_desplaza_a_los_siguientes(
    planilla, plan
):
    # O1 trabaja R002 (segunda mitad) justo despues de R004: lo planeado es hacerlo al final.
    _fila_de(planilla, "R002", "O1").update(
        inicio="2026-11-17T10:00:30-03:00", timestamp="2026-11-17T10:01:00-03:00"
    )

    resultado = desvios_respecto_del_plan(reconstruir_posicion_real(planilla), plan)

    assert _desvios(resultado) == [
        ("O1", "R002", 4, 2),
        ("O1", "R005", 2, 3),
        ("O1", "R006", 3, 4),
    ]


def test_un_caso_no_registrado_no_genera_desvios_en_los_demas(planilla, plan):
    # La cobertura del plan es del validador de c-168 (regla b), no un desvio de posicion.
    sin_r005 = [
        f for f in planilla if not (f["id_caso"] == "R005" and f["id_etiquetador"] == "O1")
    ]

    resultado = desvios_respecto_del_plan(reconstruir_posicion_real(sin_r005), plan)

    assert resultado == []


def test_el_resultado_no_depende_del_orden_de_las_filas_del_plan(planilla, plan):
    _intercambiar_tiempos(planilla, ("R005", "O1"), ("R006", "O1"))
    posiciones = reconstruir_posicion_real(planilla)
    esperado = desvios_respecto_del_plan(posiciones, plan)

    for semilla in range(5):
        plan_barajado = list(plan)
        random.Random(semilla).shuffle(plan_barajado)
        assert desvios_respecto_del_plan(posiciones, plan_barajado) == esperado


def test_las_funciones_no_modifican_sus_entradas(planilla, plan):
    _intercambiar_tiempos(planilla, ("R005", "O1"), ("R006", "O1"))
    filas_antes = [dict(fila) for fila in planilla]
    plan_antes = list(plan)

    posiciones = reconstruir_posicion_real(planilla)
    posiciones_antes = list(posiciones)
    desvios_respecto_del_plan(posiciones, plan)

    assert planilla == filas_antes
    assert posiciones == posiciones_antes
    assert plan == plan_antes


def test_el_plan_ordena_el_turno_1_antes_que_el_turno_2_dentro_de_cada_mitad():
    def asignacion(id_caso, posicion, mitad, brazo_primero):
        return AsignacionCaso(id_caso, posicion, mitad, brazo_primero, "directo")

    # Mitad 1: A1 va automatizado-primero y B1 manual-primero, asi que el operador
    # manual hace B1 (turno 1) y despues A1 (turno 2), aunque A1 tenga menor `posicion`.
    plan_a_mano = [
        asignacion("A1", 1, 1, "automatizado"),
        asignacion("B1", 2, 1, "manual"),
        asignacion("A2", 3, 2, "automatizado"),
        asignacion("B2", 4, 2, "manual"),
    ]
    sigue_los_turnos = [
        PosicionReal("O1", "B1", 1),
        PosicionReal("O1", "A1", 2),
        PosicionReal("O1", "B2", 3),
        PosicionReal("O1", "A2", 4),
    ]
    sigue_solo_posicion = [
        PosicionReal("O1", "A1", 1),
        PosicionReal("O1", "B1", 2),
        PosicionReal("O1", "A2", 3),
        PosicionReal("O1", "B2", 4),
    ]

    assert desvios_respecto_del_plan(sigue_los_turnos, plan_a_mano) == []
    assert _desvios(desvios_respecto_del_plan(sigue_solo_posicion, plan_a_mano)) == [
        ("O1", "A1", 2, 1),
        ("O1", "B1", 1, 2),
        ("O1", "A2", 4, 3),
        ("O1", "B2", 3, 4),
    ]


def test_sin_posiciones_reales_no_hay_desvios(plan):
    assert desvios_respecto_del_plan([], plan) == []
    assert desvios_respecto_del_plan([], []) == []


def test_un_caso_que_no_esta_en_el_plan_levanta_un_error_que_nombra_operador_y_caso(plan):
    posiciones = [PosicionReal("O1", "R004", 1), PosicionReal("O1", "R999", 2)]

    with pytest.raises(BrazoManualError) as error:
        desvios_respecto_del_plan(posiciones, plan)

    mensaje = str(error.value)
    assert "R999" in mensaje and "O1" in mensaje


def test_flujo_del_runbook_una_planilla_valida_puede_tener_desvios(corpus, planilla, plan):
    _intercambiar_tiempos(planilla, ("R005", "O1"), ("R006", "O1"))

    validacion = validar_doble_etiquetado(planilla, corpus, tarea=TAREA)
    desvios = desvios_respecto_del_plan(reconstruir_posicion_real(planilla), plan)

    assert validacion.valida, validacion.ofensas
    assert [d.id_caso for d in desvios] == ["R006", "R005"]


# ---------------------------------------------------------------------------
# 1.4 — El modulo no duplica esquema, columnas ni cadenas y no hace entrada/salida
# ---------------------------------------------------------------------------
FUENTE_BRAZO_MANUAL = inspect.getsource(brazo_manual)
ARBOL_BRAZO_MANUAL = ast.parse(FUENTE_BRAZO_MANUAL)


def test_el_modulo_no_declara_las_cadenas_canonicas_de_sector():
    declaradas = [sector for sector in SECTORES_CANONICOS if sector in FUENTE_BRAZO_MANUAL]

    assert declaradas == []


def test_el_modulo_no_redeclara_el_esquema_de_columnas_de_c1():
    for nodo in ast.walk(ARBOL_BRAZO_MANUAL):
        if isinstance(nodo, (ast.Tuple, ast.List, ast.Set)):
            textos = {
                elemento.value
                for elemento in nodo.elts
                if isinstance(elemento, ast.Constant) and isinstance(elemento.value, str)
            }
            assert len(textos & set(COLUMNAS_C1)) < 2, (
                f"linea {nodo.lineno}: coleccion con varias columnas de C1 {sorted(textos)}"
            )


def test_el_modulo_expone_solo_las_dos_funciones_que_importa_c167():
    funciones_publicas = sorted(
        nombre
        for nombre, valor in vars(brazo_manual).items()
        if inspect.isfunction(valor)
        and valor.__module__ == brazo_manual.__name__
        and not nombre.startswith("_")
    )

    assert funciones_publicas == ["desvios_respecto_del_plan", "reconstruir_posicion_real"]


def test_el_modulo_reutiliza_el_plan_de_c166_sin_redefinirlo():
    assert brazo_manual.subplan is plan_campana.subplan
    assert brazo_manual.AsignacionCaso is plan_campana.AsignacionCaso
    assert brazo_manual.BRAZO_MANUAL is plan_campana.BRAZO_MANUAL


def test_el_modulo_solo_importa_biblioteca_estandar_y_el_plan_de_c166():
    importados: set[str] = set()
    for nodo in ast.walk(ARBOL_BRAZO_MANUAL):
        if isinstance(nodo, ast.Import):
            importados |= {alias.name for alias in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module is not None:
            importados.add(nodo.module)

    permitidos = {"__future__", "dataclasses", "datetime", "typing", "evaluation.plan_campana"}
    assert importados <= permitidos, f"imports no previstos: {sorted(importados - permitidos)}"
