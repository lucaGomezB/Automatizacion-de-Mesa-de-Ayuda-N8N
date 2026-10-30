"""
Tests del export pseudonimizado de intervenciones para c-167 (c-165, ECM-003; grupo 4).

`scripts/exportar_intervenciones.py` produce `intervenciones.csv` con UNA fila por log
INTERVENIDO (`validado_en` no nulo) y las columnas, en este orden:

    id_caso, incidente_id, log_id, origen_intervencion, intervencion_inicio_en,
    validado_en, duracion_s, sector_predicho, sector_validado, cambio_sector, actor_alias

- `id_caso` sale del sidecar de la corrida por `incidente_id`; vacio si no se vincula.
- `duracion_s` = `validado_en - intervencion_inicio_en`; vacia si falta el inicio o da
  negativa (reloj del cliente adelantado).
- `actor_alias` = HMAC-SHA256 del id del empleado con la clave `INTERVENCION_EXPORT_HMAC_KEY`,
  truncado a 12 hex; vacio si el actor es NULL. Nunca nombre, email, telefono, legajo ni el
  id en claro.
- Los logs legados (sector validado sin `validado_en`) no se exportan: se cuentan.

Los tests escriben SIEMPRE a `tmp_path`; ninguno genera el CSV real de la campana.
"""

import csv
import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.empleado import Empleado, RolEmpleado
from scripts import exportar_intervenciones as export
from tests.c165_support import crear_log, limpiar_entorno, sembrar_entorno

COLUMNAS_ACORDADAS = [
    "id_caso",
    "incidente_id",
    "log_id",
    "origen_intervencion",
    "intervencion_inicio_en",
    "validado_en",
    "duracion_s",
    "sector_predicho",
    "sector_validado",
    "cambio_sector",
    "actor_alias",
]
CLAVE = "clave-de-prueba-del-export"
INICIO = datetime(2026, 10, 30, 15, 0, 0, tzinfo=timezone.utc)
VALIDADO = datetime(2026, 10, 30, 15, 0, 30, tzinfo=timezone.utc)


@pytest_asyncio.fixture
async def entorno(engine):
    ent = await sembrar_entorno(engine)
    yield ent
    await limpiar_entorno(engine)


def _sidecar(tmp_path: Path, entradas: list[dict], nombre: str = "sidecar_prueba.json") -> Path:
    ruta = tmp_path / nombre
    ruta.write_text(json.dumps(entradas), encoding="utf-8")
    return ruta


def _leer_csv(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


async def _exportar(engine, tmp_path, sidecars, *, desde=None, hasta=None, clave=CLAVE):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    salida = tmp_path / "intervenciones.csv"
    async with factory() as session:
        resumen = await export.exportar_intervenciones(
            session, sidecars=sidecars, salida=salida, clave=clave, desde=desde, hasta=hasta
        )
    return salida, resumen


async def _intervenido(engine, ent, **extra):
    campos = dict(
        predicho="Sistemas", validado="Sistemas", requiere_revision=True,
        intervencion_inicio_en=INICIO, validado_en=VALIDADO, origen_intervencion="gate",
    )
    campos.update(extra)
    return await crear_log(engine, ent, **campos)


# -- 4.1: columnas, orden y filas ------------------------------------------------


@pytest.mark.asyncio
async def test_el_csv_tiene_exactamente_las_columnas_acordadas_en_ese_orden(
    engine, entorno, tmp_path
):
    ids = await _intervenido(engine, entorno)
    sidecar = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": ids["incidente_id"]}])

    salida, _ = await _exportar(engine, tmp_path, [sidecar])

    primera_linea = salida.read_text(encoding="utf-8").splitlines()[0]
    assert primera_linea.split(",") == COLUMNAS_ACORDADAS
    assert list(export.COLUMNAS) == COLUMNAS_ACORDADAS


@pytest.mark.asyncio
async def test_exporta_solo_los_logs_intervenidos_y_cuenta_los_legados(engine, entorno, tmp_path):
    intervenido = await _intervenido(engine, entorno)
    await crear_log(engine, entorno, predicho="Sistemas", validado="Bases de Datos")  # legado
    await crear_log(engine, entorno, predicho="Sistemas", requiere_revision=True)  # no intervenido
    sidecar = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": intervenido["incidente_id"]}])

    salida, resumen = await _exportar(engine, tmp_path, [sidecar])

    filas = _leer_csv(salida)
    assert [f["log_id"] for f in filas] == [str(intervenido["log_id"])]
    assert resumen.exportados == 1
    assert resumen.legados_excluidos == 1


@pytest.mark.asyncio
async def test_id_caso_se_vincula_por_incidente_id_y_queda_vacio_si_no_figura_en_el_sidecar(
    engine, entorno, tmp_path
):
    vinculado = await _intervenido(engine, entorno)
    sin_vinculo = await _intervenido(engine, entorno)
    sidecar = _sidecar(
        tmp_path,
        [
            {"case_id": "R007", "incidente_id": vinculado["incidente_id"]},
            {"case_id": "R999", "incidente_id": 424242},  # otro incidente: no interviene
        ],
    )

    salida, resumen = await _exportar(engine, tmp_path, [sidecar])

    por_log = {int(f["log_id"]): f for f in _leer_csv(salida)}
    assert por_log[vinculado["log_id"]]["id_caso"] == "R007"
    assert por_log[sin_vinculo["log_id"]]["id_caso"] == ""
    assert por_log[sin_vinculo["log_id"]]["incidente_id"] == str(sin_vinculo["incidente_id"])
    assert resumen.sin_id_caso == 1


@pytest.mark.asyncio
async def test_los_sidecars_de_varias_corridas_se_combinan(engine, entorno, tmp_path):
    a = await _intervenido(engine, entorno)
    b = await _intervenido(engine, entorno)
    s1 = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": a["incidente_id"]}], "s1.json")
    s2 = _sidecar(tmp_path, [{"case_id": "R002", "incidente_id": b["incidente_id"]}], "s2.json")

    salida, resumen = await _exportar(engine, tmp_path, [s1, s2])

    assert {f["id_caso"] for f in _leer_csv(salida)} == {"R001", "R002"}
    assert resumen.sin_id_caso == 0


@pytest.mark.asyncio
async def test_sectores_canonicos_cambio_de_sector_origen_e_instantes_en_utc(
    engine, entorno, tmp_path
):
    confirmado = await _intervenido(engine, entorno, predicho="Sistemas", validado="Sistemas")
    corregido = await _intervenido(
        engine, entorno, predicho="Sistemas", validado="Bases de Datos",
        origen_intervencion="muestreo",
    )
    sidecar = _sidecar(tmp_path, [])

    salida, _ = await _exportar(engine, tmp_path, [sidecar])

    por_log = {int(f["log_id"]): f for f in _leer_csv(salida)}
    fila = por_log[confirmado["log_id"]]
    assert (fila["sector_predicho"], fila["sector_validado"], fila["cambio_sector"]) == (
        "Sistemas", "Sistemas", "false",
    )
    assert fila["origen_intervencion"] == "gate"
    assert fila["intervencion_inicio_en"] == "2026-10-30T15:00:00+00:00"
    assert fila["validado_en"] == "2026-10-30T15:00:30+00:00"
    fila = por_log[corregido["log_id"]]
    assert (fila["sector_predicho"], fila["sector_validado"], fila["cambio_sector"]) == (
        "Sistemas", "Bases de Datos", "true",
    )
    assert fila["origen_intervencion"] == "muestreo"


@pytest.mark.asyncio
async def test_un_predicho_nulo_exporta_el_sector_vacio_y_cuenta_como_cambio(
    engine, entorno, tmp_path
):
    ids = await _intervenido(
        engine, entorno, predicho=None, validado="Sistemas", origen_intervencion="rederivacion"
    )

    salida, _ = await _exportar(engine, tmp_path, [_sidecar(tmp_path, [])])

    fila = _leer_csv(salida)[0]
    assert fila["log_id"] == str(ids["log_id"])
    assert fila["sector_predicho"] == ""
    assert fila["cambio_sector"] == "true"


@pytest.mark.asyncio
async def test_duracion_s_en_segundos_y_vacia_cuando_falta_el_inicio(engine, entorno, tmp_path):
    con_inicio = await _intervenido(engine, entorno)
    sin_inicio = await _intervenido(engine, entorno, intervencion_inicio_en=None,
                                    origen_intervencion="rederivacion")

    salida, resumen = await _exportar(engine, tmp_path, [_sidecar(tmp_path, [])])

    por_log = {int(f["log_id"]): f for f in _leer_csv(salida)}
    assert por_log[con_inicio["log_id"]]["duracion_s"] == "30"
    assert por_log[sin_inicio["log_id"]]["duracion_s"] == ""
    assert por_log[sin_inicio["log_id"]]["intervencion_inicio_en"] == ""
    assert resumen.sin_inicio == 1


@pytest.mark.asyncio
async def test_duracion_s_conserva_los_milisegundos_y_queda_vacia_si_es_negativa(
    engine, entorno, tmp_path
):
    fraccion = await _intervenido(
        engine, entorno,
        intervencion_inicio_en=datetime(2026, 10, 30, 15, 0, 0, tzinfo=timezone.utc),
        validado_en=datetime(2026, 10, 30, 15, 0, 12, 500000, tzinfo=timezone.utc),
    )
    # Reloj del cliente adelantado: el inicio declarado es POSTERIOR al instante del servidor.
    negativa = await _intervenido(
        engine, entorno,
        intervencion_inicio_en=datetime(2026, 10, 30, 15, 5, 0, tzinfo=timezone.utc),
        validado_en=datetime(2026, 10, 30, 15, 0, 30, tzinfo=timezone.utc),
    )

    salida, resumen = await _exportar(engine, tmp_path, [_sidecar(tmp_path, [])])

    por_log = {int(f["log_id"]): f for f in _leer_csv(salida)}
    assert por_log[fraccion["log_id"]]["duracion_s"] == "12.5"
    assert por_log[negativa["log_id"]]["duracion_s"] == ""
    # El inicio se conserva tal cual: solo la duracion se anula.
    assert por_log[negativa["log_id"]]["intervencion_inicio_en"] == "2026-10-30T15:05:00+00:00"
    assert resumen.duracion_negativa == 1


@pytest.mark.asyncio
async def test_el_rango_acota_la_cohorte_por_created_at_del_log(engine, entorno, tmp_path):
    from datetime import date

    dentro = await _intervenido(engine, entorno, created_at=datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc))
    await _intervenido(engine, entorno, created_at=datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc))
    await _intervenido(engine, entorno, created_at=datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc))

    salida, resumen = await _exportar(
        engine, tmp_path, [_sidecar(tmp_path, [])], desde=date(2026, 10, 1), hasta=date(2026, 10, 31)
    )

    assert [int(f["log_id"]) for f in _leer_csv(salida)] == [dentro["log_id"]]
    assert resumen.exportados == 1


@pytest.mark.asyncio
async def test_el_orden_es_por_log_id_y_el_export_es_reproducible(engine, entorno, tmp_path):
    for _ in range(3):
        await _intervenido(engine, entorno)
    sidecar = _sidecar(tmp_path, [])

    salida1, _ = await _exportar(engine, tmp_path, [sidecar])
    contenido1 = salida1.read_bytes()
    salida2, _ = await _exportar(engine, tmp_path, [sidecar])

    ids = [int(f["log_id"]) for f in _leer_csv(salida1)]
    assert ids == sorted(ids) and len(ids) == 3
    assert salida2.read_bytes() == contenido1


# -- 4.3: privacidad y alias del actor ---------------------------------------------


def _alias_esperado(empleado_id: int, clave: str) -> str:
    """HMAC-SHA256 truncado a 12 hex, calculado aca de forma independiente."""
    return hmac.new(clave.encode("utf-8"), str(empleado_id).encode("ascii"), hashlib.sha256).hexdigest()[:12]


async def _empleado_distintivo(engine, empleado_id: int) -> None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        s.add(
            Empleado(
                id=empleado_id,
                legajo="LEG-ZQ-77",
                nombre="Zulema Quispe",
                email="zulema.quispe@ejemplo.test",
                telefono="+5491155550199",
                rol=RolEmpleado.mesa_de_ayuda,
            )
        )
        await s.commit()


@pytest.mark.asyncio
async def test_el_csv_no_contiene_nombre_email_telefono_legajo_ni_el_id_del_empleado(
    engine, entorno, tmp_path
):
    empleado_id = 987654
    await _empleado_distintivo(engine, empleado_id)
    ids = await _intervenido(engine, entorno, validado_por_empleado_id=empleado_id)
    sidecar = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": ids["incidente_id"]}])

    salida, _ = await _exportar(engine, tmp_path, [sidecar])

    texto = salida.read_text(encoding="utf-8")
    for dato in ("Zulema", "Quispe", "zulema.quispe@ejemplo.test", "+5491155550199",
                 "5491155550199", "LEG-ZQ-77", str(empleado_id)):
        assert dato not in texto, f"el export filtra {dato!r}"
    assert set(_leer_csv(salida)[0]) == set(COLUMNAS_ACORDADAS)


@pytest.mark.asyncio
async def test_actor_alias_es_hmac_sha256_con_la_clave_truncado_a_12_hex(
    engine, entorno, tmp_path
):
    empleado_id = 987654
    await _empleado_distintivo(engine, empleado_id)
    await _intervenido(engine, entorno, validado_por_empleado_id=empleado_id)

    salida, _ = await _exportar(engine, tmp_path, [_sidecar(tmp_path, [])])

    alias = _leer_csv(salida)[0]["actor_alias"]
    assert len(alias) == 12
    assert all(c in "0123456789abcdef" for c in alias)
    assert alias == _alias_esperado(empleado_id, CLAVE)
    # Un hash PLANO del id seria reversible por enumeracion: no puede coincidir.
    assert alias != hashlib.sha256(str(empleado_id).encode()).hexdigest()[:12]


@pytest.mark.asyncio
async def test_actor_alias_es_estable_entre_corridas_y_cambia_con_la_clave(
    engine, entorno, tmp_path
):
    empleado_id = 987654
    await _empleado_distintivo(engine, empleado_id)
    await _intervenido(engine, entorno, validado_por_empleado_id=empleado_id)
    sidecar = _sidecar(tmp_path, [])

    salida1, _ = await _exportar(engine, tmp_path, [sidecar])
    alias1 = _leer_csv(salida1)[0]["actor_alias"]
    salida2, _ = await _exportar(engine, tmp_path, [sidecar])
    alias2 = _leer_csv(salida2)[0]["actor_alias"]
    salida3, _ = await _exportar(engine, tmp_path, [sidecar], clave="otra-clave-distinta")
    alias3 = _leer_csv(salida3)[0]["actor_alias"]

    assert alias1 == alias2
    assert alias3 != alias1
    assert alias3 == _alias_esperado(empleado_id, "otra-clave-distinta")


@pytest.mark.asyncio
async def test_actor_alias_queda_vacio_si_el_actor_es_nulo(engine, entorno, tmp_path):
    await _intervenido(engine, entorno, validado_por_empleado_id=None)

    salida, _ = await _exportar(engine, tmp_path, [_sidecar(tmp_path, [])])

    assert _leer_csv(salida)[0]["actor_alias"] == ""


def test_alias_de_actor_dos_empleados_distintos_dan_alias_distintos():
    assert export.alias_de_actor(1, CLAVE) != export.alias_de_actor(2, CLAVE)
    assert export.alias_de_actor(None, CLAVE) == ""


# -- Clave HMAC: variable de entorno propia, error explicito si falta ------------


def test_la_clave_se_lee_de_intervencion_export_hmac_key(monkeypatch):
    monkeypatch.setenv("INTERVENCION_EXPORT_HMAC_KEY", "mi-clave-secreta")

    assert export.leer_clave_hmac() == "mi-clave-secreta"


@pytest.mark.parametrize("valor", [None, "", "   "])
def test_sin_la_clave_el_export_falla_con_un_error_explicito(monkeypatch, valor):
    if valor is None:
        monkeypatch.delenv("INTERVENCION_EXPORT_HMAC_KEY", raising=False)
    else:
        monkeypatch.setenv("INTERVENCION_EXPORT_HMAC_KEY", valor)

    with pytest.raises(export.ClaveHmacAusente) as exc:
        export.leer_clave_hmac()

    assert "INTERVENCION_EXPORT_HMAC_KEY" in str(exc.value)


def test_main_sin_la_clave_termina_con_error_sin_tocar_la_base_ni_escribir(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.delenv("INTERVENCION_EXPORT_HMAC_KEY", raising=False)
    sidecar = _sidecar(tmp_path, [])
    salida = tmp_path / "intervenciones.csv"

    codigo = export.main(["--sidecar", str(sidecar), "--salida", str(salida)])

    assert codigo != 0
    assert "INTERVENCION_EXPORT_HMAC_KEY" in capsys.readouterr().err
    assert not salida.exists()


# -- 4.4: el CLI no escribe sobre los archivos congelados --------------------------

REPO = Path(__file__).resolve().parents[3]
CONGELADOS = [
    "data/corpus_evaluacion_pseudonimizado.json",
    "data/corpus_resultados.json",
    "data/corpus_resultados_telefonia.json",
    "data/corpus_resultados_n8n.json",  # sidecar versionado por patron (puede no existir aun)
    "evaluation/predicciones.json",
    "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json",
]


def _huella(ruta: Path) -> tuple | None:
    if not ruta.exists():
        return None
    return (hashlib.sha256(ruta.read_bytes()).hexdigest(), ruta.stat().st_mtime_ns)


@pytest.mark.parametrize("relativa", CONGELADOS)
def test_el_cli_se_niega_a_escribir_sobre_un_archivo_congelado(
    relativa, monkeypatch, tmp_path, capsys
):
    monkeypatch.setenv("INTERVENCION_EXPORT_HMAC_KEY", CLAVE)  # el rechazo no es por la clave
    objetivo = REPO / relativa
    antes = _huella(objetivo)
    sidecar = _sidecar(tmp_path, [])

    codigo = export.main(["--sidecar", str(sidecar), "--salida", str(objetivo)])

    assert codigo != 0
    assert Path(relativa).name in capsys.readouterr().err
    assert _huella(objetivo) == antes, "el archivo congelado fue modificado"


def test_el_cli_tambien_detecta_el_archivo_congelado_con_una_ruta_relativa(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.setenv("INTERVENCION_EXPORT_HMAC_KEY", CLAVE)
    objetivo = REPO / "data" / "corpus_resultados.json"
    antes = _huella(objetivo)
    monkeypatch.chdir(REPO / "App" / "Backend")

    codigo = export.main(
        ["--sidecar", str(_sidecar(tmp_path, [])), "--salida", "../../data/corpus_resultados.json"]
    )

    assert codigo != 0
    assert _huella(objetivo) == antes


@pytest.mark.parametrize(
    "ruta",
    ["evaluation/data/campana/intervenciones.csv", "evaluation/data/campana/otra_salida.csv"],
)
def test_las_salidas_de_la_campana_estan_permitidas(ruta):
    export.verificar_salida_permitida(REPO / ruta)  # no lanza


def test_una_salida_fuera_del_repo_esta_permitida(tmp_path):
    export.verificar_salida_permitida(tmp_path / "intervenciones.csv")  # no lanza


@pytest.mark.parametrize("relativa", CONGELADOS)
def test_verificar_salida_permitida_lanza_para_cada_congelado(relativa):
    with pytest.raises(export.SalidaCongelada):
        export.verificar_salida_permitida(REPO / relativa)


# -- Vinculo con el sidecar -----------------------------------------------------------


def test_cargar_vinculos_toma_case_id_por_incidente_id_y_omite_los_incompletos(tmp_path):
    sidecar = _sidecar(
        tmp_path,
        [
            {"case_id": "R001", "incidente_id": 165},
            {"case_id": "R002", "incidente_id": None},      # sin incidente: no vincula
            {"case_id": None, "incidente_id": 170},          # sin caso: no vincula
            {"case_id": "R003", "incidente_id": "171"},     # entero como texto
        ],
    )

    vinculos, ambiguos = export.cargar_vinculos([sidecar])

    assert vinculos == {165: "R001", 171: "R003"}
    assert ambiguos == set()


def test_un_incidente_asignado_a_dos_casos_distintos_es_ambiguo_y_no_se_vincula(tmp_path):
    s1 = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": 165}], "s1.json")
    s2 = _sidecar(tmp_path, [{"case_id": "R002", "incidente_id": 165}], "s2.json")

    vinculos, ambiguos = export.cargar_vinculos([s1, s2])

    assert 165 not in vinculos
    assert ambiguos == {165}


def test_el_mismo_vinculo_repetido_en_dos_sidecars_no_es_ambiguo(tmp_path):
    s1 = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": 165}], "s1.json")
    s2 = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": 165}], "s2.json")

    vinculos, ambiguos = export.cargar_vinculos([s1, s2])

    assert vinculos == {165: "R001"}
    assert ambiguos == set()


@pytest.mark.asyncio
async def test_un_vinculo_ambiguo_deja_el_id_caso_vacio_y_se_declara(engine, entorno, tmp_path):
    ids = await _intervenido(engine, entorno)
    s1 = _sidecar(tmp_path, [{"case_id": "R001", "incidente_id": ids["incidente_id"]}], "s1.json")
    s2 = _sidecar(tmp_path, [{"case_id": "R002", "incidente_id": ids["incidente_id"]}], "s2.json")

    salida, resumen = await _exportar(engine, tmp_path, [s1, s2])

    assert _leer_csv(salida)[0]["id_caso"] == ""
    assert resumen.sin_id_caso == 1
    assert resumen.vinculos_ambiguos == 1


def test_un_sidecar_que_no_es_una_lista_da_un_error_claro(tmp_path):
    ruta = tmp_path / "sidecar_malo.json"
    ruta.write_text(json.dumps({"case_id": "R001"}), encoding="utf-8")

    with pytest.raises(export.SidecarInvalido) as exc:
        export.cargar_vinculos([ruta])

    assert "sidecar_malo.json" in str(exc.value)


def test_main_con_un_sidecar_inexistente_termina_con_error(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("INTERVENCION_EXPORT_HMAC_KEY", CLAVE)
    salida = tmp_path / "intervenciones.csv"

    codigo = export.main(["--sidecar", str(tmp_path / "no_existe.json"), "--salida", str(salida)])

    assert codigo != 0
    assert "no_existe.json" in capsys.readouterr().err
    assert not salida.exists()
