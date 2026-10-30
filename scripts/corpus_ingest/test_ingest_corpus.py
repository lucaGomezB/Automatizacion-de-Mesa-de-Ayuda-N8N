"""Offline unit tests for the corpus ingest harness.

No network, no real corpus file, no mutation of ``data/``. Every filesystem
touch happens inside ``tmp_path``. Descriptions here are synthetic and public.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict, fields, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Los tests de campana arman planes con el paquete `evaluation` de la raiz del repo;
# se agrega la raiz a sys.path de forma relativa al archivo (mismo patron que
# test_ingest_telefonia_corpus.py) para correr tanto desde la raiz como desde este directorio.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import ingest_corpus as ic  # noqa: E402
from evaluation import plan_campana as pc  # noqa: E402


# ── Channel mapping ─────────────────────────────────────────────────────────


def test_channel_mapping_canonical_names():
    assert ic.map_canal_origen_id("Correo") == 1
    assert ic.map_canal_origen_id("Formulario Web") == 2
    assert ic.map_canal_origen_id("Telefono") == 3


def test_channel_mapping_is_case_and_space_insensitive():
    assert ic.map_canal_origen_id("  correo ") == 1
    assert ic.map_canal_origen_id("FORMULARIO WEB") == 2


def test_channel_mapping_unknown_returns_none():
    assert ic.map_canal_origen_id("Paloma Mensajera") is None
    assert ic.map_canal_origen_id("") is None
    assert ic.map_canal_origen_id(None) is None


# ── Payload builder ─────────────────────────────────────────────────────────


def test_build_payload_shape_and_determinism():
    fixed = datetime(2026, 9, 29, 12, 0, 0, tzinfo=timezone.utc)
    payload = ic.build_incidente_payload(
        descripcion="Synthetic description long enough",
        canal_origen_id=2,
        case_id="R007",
        ingresado_en=fixed,
    )
    assert payload["descripcion"] == "Synthetic description long enough"
    assert payload["canal_origen_id"] == 2
    assert payload["origen_evento"] == "creacion_incidente"
    assert payload["origen_message_id"] == "corpus-R007"
    assert payload["ingresado_en"].endswith("+00:00")
    # Message id is deterministic: same case -> same id.
    again = ic.build_incidente_payload(
        descripcion="x" * 20, canal_origen_id=1, case_id="R007", ingresado_en=fixed
    )
    assert again["origen_message_id"] == payload["origen_message_id"]


def test_build_payload_ingresado_en_is_tz_aware():
    payload = ic.build_incidente_payload(
        descripcion="y" * 20, canal_origen_id=1, case_id="R001"
    )
    parsed = datetime.fromisoformat(payload["ingresado_en"])
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None


# ── CSV read/write ──────────────────────────────────────────────────────────


def _write_fixture_csv(path):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n")
        writer.writerow(["Casos de incidentes registrados:", "", "", "", "", "", ""])
        writer.writerow(
            [
                "ID",
                "Descripcion",
                "Canal de Origen",
                "Sector Asignado",
                "Sectores Adicionales",
                "Tiempo de Registro Manual (segundos)",
                "TIempo de Registro Automatico (Segundos)",
            ]
        )
        writer.writerow(
            [
                "R001",
                "No puede ingresar, con coma y todo",
                "Correo",
                "Seguridad Informatica",
                "Soporte Tecnico Software",
                "75",
                "",
            ]
        )
        writer.writerow(
            ["R002", "No puede abrir archivos", "Telefono", "Sistemas", "", "110", ""]
        )


def test_read_cases_csv(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    cases = ic.read_csv_cases(path)
    assert [c.case_id for c in cases] == ["R001", "R002"]
    assert cases[0].canal == "Correo"
    assert cases[0].descripcion.startswith("No puede ingresar")


def test_write_csv_updates_columns_and_preserves_originals(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    results = {
        "R001": ic.CorpusResult(
            case_id="R001",
            incidente_id=11,
            numero_incidente="INC-000011",
            sector="Seguridad Informatica",
            revision=False,
            wall_s=1.5234,
            latencia_e2e_ms=420,
            error=None,
        ),
        "R002": ic.CorpusResult(
            case_id="R002",
            incidente_id=None,
            numero_incidente=None,
            sector=None,
            revision=None,
            wall_s=None,
            latencia_e2e_ms=None,
            error="timeout",
        ),
    }
    ic.write_csv_results(path, results)

    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[1]
    assert header[-1] == ic.LATENCIA_COL
    auto = header.index("TIempo de Registro Automatico (Segundos)")
    lat = header.index(ic.LATENCIA_COL)
    row1 = rows[2]
    row2 = rows[3]
    assert row1[auto] == "1.523"
    assert row1[lat] == "420"
    assert row2[auto] == ""  # error -> left blank
    assert row2[lat] == ""
    # Originals preserved.
    assert row1[0] == "R001"
    assert row1[5] == "75"
    assert rows[0][0] == "Casos de incidentes registrados:"


def test_read_cases_dispatches_csv(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    assert len(ic.read_cases(path, "csv")) == 2


def test_read_csv_cases_skips_blank_rows(tmp_path):
    path = tmp_path / "corpus.csv"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n")
        writer.writerow(["Title:", "", "", "", "", "", ""])
        writer.writerow(
            [
                "ID",
                "Descripcion",
                "Canal de Origen",
                "Sector Asignado",
                "Sectores Adicionales",
                "Tiempo de Registro Manual (segundos)",
                "TIempo de Registro Automatico (Segundos)",
            ]
        )
        writer.writerow(["R001", "Text", "Correo", "Sistemas", "", "50", ""])
        writer.writerow(["", "", "", "", "", "", ""])
    cases = ic.read_csv_cases(path)
    assert [c.case_id for c in cases] == ["R001"]


def test_select_cases_filters_channel_and_applies_limit():
    cases = [
        ic.CorpusCase("R001", "d1", "Correo"),
        ic.CorpusCase("R002", "d2", "Telefono"),
        ic.CorpusCase("R003", "d3", "correo"),
        ic.CorpusCase("R004", "d4", "Formulario Web"),
    ]
    only_correo = ic._select_cases(cases, "Correo", None)
    assert [c.case_id for c in only_correo] == ["R001", "R003"]
    limited = ic._select_cases(cases, None, 2)
    assert [c.case_id for c in limited] == ["R001", "R002"]
    assert ic._select_cases(cases, "Correo", 1)[0].case_id == "R001"


def test_read_xlsx_cases(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "corpus.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Title:"])
    ws.append(
        [
            "ID",
            "Descripcion",
            "Canal de Origen",
            "Sector Asignado",
            "Sectores Adicionales",
            "Tiempo de Registro Manual (segundos)",
            "TIempo de Registro Automatico (Segundos)",
        ]
    )
    ws.append(["R001", "Text", "Correo", "Sistemas", "", 50, None])
    wb.save(path)
    cases = ic.read_cases(path, "xlsx")
    assert [c.case_id for c in cases] == ["R001"]
    assert cases[0].canal == "Correo"


def test_write_csv_is_idempotent(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    results = {
        "R001": ic.CorpusResult(
            case_id="R001",
            incidente_id=11,
            numero_incidente="INC-000011",
            sector="Sistemas",
            revision=True,
            wall_s=2.0,
            latencia_e2e_ms=100,
            error=None,
        )
    }
    ic.write_csv_results(path, results)
    ic.write_csv_results(path, results)
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[1]
    assert header.count(ic.LATENCIA_COL) == 1
    # Every row has the same field count.
    assert len({len(r) for r in rows}) == 1


# ── XLSX read/write ─────────────────────────────────────────────────────────


def test_write_xlsx_updates_columns_and_is_idempotent(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "corpus.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Casos de incidentes registrados:"])
    ws.append(
        [
            "ID",
            "Descripcion",
            "Canal de Origen",
            "Sector Asignado",
            "Sectores Adicionales",
            "Tiempo de Registro Manual (segundos)",
            "TIempo de Registro Automatico (Segundos)",
        ]
    )
    ws.append(["R001", "Text", "Correo", "Seguridad Informatica", "", 75, None])
    ws.append(["R002", "Text2", "Telefono", "Sistemas", "", 110, None])
    wb.save(path)

    results = {
        "R001": ic.CorpusResult(
            case_id="R001",
            incidente_id=11,
            numero_incidente="INC-000011",
            sector="Seguridad Informatica",
            revision=False,
            wall_s=1.5,
            latencia_e2e_ms=420,
            error=None,
        ),
        "R002": ic.CorpusResult(
            case_id="R002",
            incidente_id=None,
            numero_incidente=None,
            sector=None,
            revision=None,
            wall_s=None,
            latencia_e2e_ms=None,
            error="http500",
        ),
    }
    ic.write_xlsx_results(path, results)
    ic.write_xlsx_results(path, results)  # idempotent: no duplicate column

    wb2 = openpyxl.load_workbook(path)
    ws2 = wb2[wb2.sheetnames[0]]
    header = [ws2.cell(row=2, column=c).value for c in range(1, ws2.max_column + 1)]
    assert header.count(ic.LATENCIA_COL) == 1
    assert header[-1] == ic.LATENCIA_COL
    auto_col = header.index("TIempo de Registro Automatico (Segundos)") + 1
    lat_col = header.index(ic.LATENCIA_COL) + 1
    assert ws2.cell(row=3, column=auto_col).value == 1.5
    assert ws2.cell(row=3, column=lat_col).value == 420
    assert ws2.cell(row=4, column=auto_col).value in (None, "")
    assert ws2.cell(row=3, column=1).value == "R001"
    assert ws2.cell(row=3, column=4).value == "Seguridad Informatica"


# ── Sidecar JSON ────────────────────────────────────────────────────────────


def test_sidecar_json_has_no_description(tmp_path):
    path = tmp_path / "resultados.json"
    results = [
        ic.CorpusResult(
            case_id="R001",
            incidente_id=1,
            numero_incidente="INC-000001",
            sector="Sistemas",
            revision=True,
            wall_s=0.9,
            latencia_e2e_ms=300,
            error=None,
        )
    ]
    ic.write_sidecar_json(path, results)
    raw = path.read_text(encoding="utf-8")
    assert "descripcion" not in raw.lower()
    data = json.loads(raw)
    assert data[0]["case_id"] == "R001"
    assert data[0]["latencia_e2e_ms"] == 300


# ── Modo campana (c-166): campos nuevos de CorpusResult (task 2.3) ──────────

CAMPOS_CAMPANA = ["orden", "posicion", "mitad", "brazo_primero", "id_corrida"]


def _corpus_result(case_id: str = "R001") -> ic.CorpusResult:
    """Constructor existente: no pasa ningun campo de campana."""
    return ic.CorpusResult(
        case_id=case_id,
        incidente_id=1,
        numero_incidente="INC-000001",
        sector="Sistemas",
        revision=False,
        wall_s=1.0,
        latencia_e2e_ms=100,
        error=None,
    )


def test_corpus_result_acepta_los_campos_de_campana_al_final_con_default_none():
    resultado = _corpus_result()

    assert [getattr(resultado, campo) for campo in CAMPOS_CAMPANA] == [None] * 5
    assert [f.name for f in fields(ic.CorpusResult)][-5:] == CAMPOS_CAMPANA
    assert list(asdict(resultado))[-5:] == CAMPOS_CAMPANA


def test_corpus_result_guarda_los_campos_de_campana_cuando_se_los_pasa():
    resultado = replace(
        _corpus_result(),
        orden="inverso",
        posicion=3,
        mitad=2,
        brazo_primero="manual",
        id_corrida="corrida-2",
    )

    assert asdict(resultado)["orden"] == "inverso"
    assert asdict(resultado)["posicion"] == 3
    assert asdict(resultado)["mitad"] == 2
    assert asdict(resultado)["brazo_primero"] == "manual"
    assert asdict(resultado)["id_corrida"] == "corrida-2"


def test_result_from_response_deja_los_campos_de_campana_en_none():
    class _Respuesta:
        def json(self):
            return {"id": 5, "numero_incidente": "INC-000005", "sector": {"nombre": "Sistemas"}}

    resultado = ic._result_from_response("R001", _Respuesta(), 0.5)

    assert [getattr(resultado, campo) for campo in CAMPOS_CAMPANA] == [None] * 5


# ── Modo campana (c-166): run() con --plan/--orden (tasks 2.5 y 2.11) ───────


def _write_cases_csv(path, canales) -> None:
    """CSV sintetico con un caso por canal indicado (ids R001, R002, ...)."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n")
        writer.writerow(["Casos de incidentes registrados:", "", "", "", "", "", ""])
        writer.writerow(
            [
                "ID",
                "Descripcion",
                "Canal de Origen",
                "Sector Asignado",
                "Sectores Adicionales",
                "Tiempo de Registro Manual (segundos)",
                "TIempo de Registro Automatico (Segundos)",
            ]
        )
        for numero, canal in enumerate(canales, start=1):
            writer.writerow([f"R{numero:03d}", f"d{numero}", canal, "Sistemas", "", "75", ""])


def _escribir_plan(path, ids, modo="directo", seed=None):
    pc.escribir_plan_csv(pc.generar_plan_campana(ids, modo, seed), path)
    return path


class _RespuestaFalsa:
    status_code = 201

    def json(self) -> dict:
        return {
            "id": 1,
            "numero_incidente": "INC-000001",
            "sector": {"nombre": "Sistemas"},
            "requiere_revision_humana": False,
            "latencia_e2e_ms": 100,
        }


def _ingesta_falsa(monkeypatch, vistos: list[str]) -> list[str]:
    """Cliente falso: registra los case_id enviados, en orden.

    Devuelve la lista donde se anotan las llamadas a los writers de CSV/XLSX (que no
    escriben nada), para poder afirmar si el modo campana los invoca.
    """
    escrituras: list[str] = []

    def post(session, base_url, token, payload, verify, timeout):
        vistos.append(payload["origen_message_id"].removeprefix(ic.MESSAGE_ID_PREFIX))
        return _RespuestaFalsa(), 0.5

    monkeypatch.setenv("INGEST_OPERATOR_USERNAME", "operador")
    monkeypatch.setenv("INGEST_OPERATOR_PASSWORD", "pw")
    monkeypatch.setattr(ic, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(ic, "post_incidente", post)
    monkeypatch.setattr(ic, "write_csv_results", lambda *a, **k: escrituras.append("csv"))
    monkeypatch.setattr(ic, "write_xlsx_results", lambda *a, **k: escrituras.append("xlsx"))
    return escrituras


def _argv_campana(tmp_path, csv_path, *extra) -> list[str]:
    return [
        "--source",
        "csv",
        "--csv",
        str(csv_path),
        "--sidecar",
        str(tmp_path / "corrida.json"),
        "--id-corrida",
        "corrida-1",
        "--sleep",
        "0",
        *extra,
    ]


def test_orden_inverso_con_limit_procesa_el_reverso_de_los_tres_primeros(tmp_path, monkeypatch):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 5)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--orden", "inverso", "--limit", "3"))

    assert codigo == 0
    assert vistos == ["R003", "R002", "R001"]  # NO los tres ultimos (R005, R004, R003)


def test_plan_con_limit_se_rechaza_con_error_accionable_y_no_envia_nada(
    tmp_path, monkeypatch, capsys
):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 4)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003", "R004"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--plan", str(plan), "--limit", "2"))

    err = capsys.readouterr().err
    assert codigo == 2
    assert "--limit" in err and "--plan" in err
    assert vistos == []


# ── Modo campana (c-166): --plan, --orden, sidecar y proteccion (task 2.11) ──

IDS_5 = ["R001", "R002", "R003", "R004", "R005"]
CSV_CANONICO = "data/Corpus Tesis - Hoja 1.csv"


def _leer_sidecar(tmp_path) -> list[dict]:
    return json.loads((tmp_path / "corrida.json").read_text(encoding="utf-8"))


def _argv_con_modo(modo_argv, **opciones) -> list[str]:
    """argv de campana donde cada opcion es un flag explicito (None = no se pasa)."""
    argv = ["--source", "csv", "--id-corrida", "corrida-1", "--sleep", "0", *modo_argv]
    for flag, valor in opciones.items():
        if valor is not None:
            argv += [f"--{flag}", valor]
    return argv


def test_plan_envia_los_casos_en_orden_de_posicion(tmp_path, monkeypatch):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo", "Telefono", "Formulario Web", "Correo", "Correo"])
    plan = _escribir_plan(tmp_path / "plan.csv", IDS_5, "inverso")
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--plan", str(plan)))

    assert codigo == 0
    assert vistos == ["R005", "R004", "R003", "R002", "R001"]


def test_plan_registra_la_asignacion_del_plan_en_cada_entrada_del_sidecar(tmp_path, monkeypatch):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 5)
    plan = _escribir_plan(tmp_path / "plan.csv", IDS_5, "aleatorio", seed=7)
    esperado = {fila.id_caso: fila for fila in pc.leer_plan_csv(plan)}
    _ingesta_falsa(monkeypatch, [])

    ic.run(_argv_campana(tmp_path, csv_path, "--plan", str(plan)))

    entradas = _leer_sidecar(tmp_path)
    assert sorted(entrada["case_id"] for entrada in entradas) == IDS_5
    for entrada in entradas:
        fila = esperado[entrada["case_id"]]
        assert entrada["posicion"] == fila.posicion
        assert entrada["mitad"] == fila.mitad
        assert entrada["brazo_primero"] == fila.brazo_primero
        assert entrada["orden"] == "aleatorio"
        assert entrada["id_corrida"] == "corrida-1"


def test_plan_acepta_un_subplan_con_posiciones_globales_no_contiguas(tmp_path, monkeypatch):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 5)
    subplan = tmp_path / "subplan.csv"
    completo = pc.generar_plan_campana(IDS_5, "directo")
    pc.escribir_plan_csv(pc.subplan(completo, mitad=2, brazo="manual", turno=1), subplan)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--plan", str(subplan)))

    assert codigo == 0
    assert vistos == ["R003", "R005"]
    assert [entrada["posicion"] for entrada in _leer_sidecar(tmp_path)] == [3, 5]


def test_plan_con_un_id_caso_ausente_del_corpus_aborta_antes_de_enviar(
    tmp_path, monkeypatch, capsys
):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R999"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--plan", str(plan)))

    assert codigo == 2
    assert "R999" in capsys.readouterr().err
    assert vistos == []
    assert not (tmp_path / "corrida.json").exists()


def test_plan_y_orden_juntos_se_rechazan_y_no_envian_nada(tmp_path, monkeypatch, capsys):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--plan", str(plan), "--orden", "inverso"))

    err = capsys.readouterr().err
    assert codigo == 2
    assert "--plan" in err and "--orden" in err
    assert vistos == []


@pytest.mark.parametrize("modo", ["plan", "orden"])
def test_la_falta_de_id_corrida_se_rechaza_con_plan_y_con_orden(
    tmp_path, monkeypatch, capsys, modo
):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    modo_argv = ["--plan", str(plan)] if modo == "plan" else ["--orden", "inverso"]

    codigo = ic.run(
        [
            "--source", "csv", "--csv", str(csv_path),
            "--sidecar", str(tmp_path / "corrida.json"), "--sleep", "0",
            *modo_argv,
        ]
    )  # fmt: skip

    assert codigo == 2
    assert "--id-corrida" in capsys.readouterr().err
    assert vistos == []


def test_orden_genera_el_plan_lo_escribe_junto_al_sidecar_y_procesa_en_ese_orden(
    tmp_path, monkeypatch
):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 6)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    plan_esperado = pc.generar_plan_campana([f"R{n:03d}" for n in range(1, 7)], "aleatorio", 11)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--orden", "aleatorio", "--seed", "11"))

    assert codigo == 0
    assert pc.leer_plan_csv(tmp_path / "corrida.json.plan.csv") == plan_esperado
    assert vistos == [fila.id_caso for fila in plan_esperado]


def test_orden_aleatorio_sin_seed_termina_con_error_que_pide_seed_y_no_envia_nada(
    tmp_path, monkeypatch, capsys
):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 3)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--orden", "aleatorio"))

    assert codigo == 2
    assert "--seed" in capsys.readouterr().err
    assert vistos == []
    assert not (tmp_path / "corrida.json").exists()
    assert not (tmp_path / "corrida.json.plan.csv").exists()


@pytest.mark.parametrize("modo", ["orden", "plan"])
@pytest.mark.parametrize(
    "sidecar_arg",
    [
        "data/corpus_resultados.json",
        "data/corpus_resultados_telefonia.json",
        "data/corpus_resultados_n8n.json",
        "data/corpus_resultados_otra.json",
    ],
)
def test_con_plan_u_orden_aborta_si_el_sidecar_apunta_a_un_archivo_versionado(
    tmp_path, monkeypatch, capsys, modo, sidecar_arg
):
    monkeypatch.chdir(tmp_path)  # cualquier escritura indebida caeria aca, no en el repo
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    for variable in ("INGEST_OPERATOR_USERNAME", "INGEST_OPERATOR_PASSWORD"):
        monkeypatch.delenv(variable)  # la proteccion se evalua antes de leer credenciales
    modo_argv = ["--orden", "inverso"] if modo == "orden" else ["--plan", str(plan)]

    codigo = ic.run(_argv_con_modo(modo_argv, csv=CSV_CANONICO, sidecar=sidecar_arg))

    err = capsys.readouterr().err
    assert codigo == 2
    assert sidecar_arg in err
    assert "evaluation/data/campana/" in err
    assert "INGEST_OPERATOR" not in err
    assert vistos == []
    assert not (tmp_path / "data").exists()


def test_con_plan_la_ruta_absoluta_a_un_archivo_versionado_del_repo_tambien_se_rechaza(
    tmp_path, monkeypatch, capsys
):
    versionado = _REPO_ROOT / "data" / "corpus_resultados.json"
    antes = versionado.read_bytes() if versionado.exists() else None
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 2)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    # Red de seguridad: este writer SOBRESCRIBE el archivo; aun si la proteccion fallara,
    # nada toca el repo real.
    intentos_de_escritura: list[str] = []
    monkeypatch.setattr(
        ic, "write_sidecar_json", lambda ruta, *a, **k: intentos_de_escritura.append(str(ruta))
    )

    codigo = ic.run(
        _argv_con_modo(["--plan", str(plan)], csv=str(csv_path), sidecar=str(versionado))
    )

    assert codigo == 2
    assert "corpus_resultados.json" in capsys.readouterr().err
    assert vistos == []
    assert intentos_de_escritura == []
    assert (versionado.read_bytes() if versionado.exists() else None) == antes


@pytest.mark.parametrize("modo", ["orden", "plan"])
def test_con_plan_u_orden_el_sidecar_es_obligatorio(tmp_path, monkeypatch, capsys, modo):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    monkeypatch.chdir(tmp_path)
    modo_argv = ["--orden", "inverso"] if modo == "orden" else ["--plan", str(plan)]

    codigo = ic.run(_argv_con_modo(modo_argv, csv=str(csv_path)))

    err = capsys.readouterr().err
    assert codigo == 2
    assert "--sidecar" in err and "obligatorio" in err
    assert vistos == []
    assert not (tmp_path / "data").exists()  # el default NO rige en modo campana


def test_un_sidecar_existente_se_rechaza_aunque_sea_de_la_misma_corrida(
    tmp_path, monkeypatch, capsys
):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 3)
    sidecar = tmp_path / "corrida.json"
    previo = [{"case_id": "R001", "id_corrida": "corrida-1"}]
    sidecar.write_text(json.dumps(previo), encoding="utf-8")
    antes = sidecar.read_bytes()
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ic.run(_argv_campana(tmp_path, csv_path, "--orden", "directo"))

    err = capsys.readouterr().err
    assert codigo == 2
    assert "corrida.json" in err and "ya existe" in err
    assert vistos == []
    assert sidecar.read_bytes() == antes  # este writer sobrescribe todo: no hay reanudacion


@pytest.mark.parametrize("modo", ["orden", "plan"])
def test_con_plan_u_orden_no_se_escriben_ni_el_csv_ni_el_xlsx(tmp_path, monkeypatch, modo):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    escrituras = _ingesta_falsa(monkeypatch, vistos)
    modo_argv = ["--orden", "inverso"] if modo == "orden" else ["--plan", str(plan)]

    codigo = ic.run(_argv_campana(tmp_path, csv_path, *modo_argv))

    assert codigo == 0
    assert len(vistos) == 3
    assert escrituras == []


def test_sin_plan_ni_orden_se_siguen_escribiendo_el_csv_y_el_xlsx(tmp_path, monkeypatch):
    csv_path = tmp_path / "corpus.csv"
    _write_cases_csv(csv_path, ["Correo"] * 2)
    escrituras = _ingesta_falsa(monkeypatch, [])

    codigo = ic.run(
        [
            "--source", "csv", "--csv", str(csv_path),
            "--sidecar", str(tmp_path / "sidecar.json"), "--sleep", "0",
        ]
    )  # fmt: skip

    assert codigo == 0
    assert escrituras == ["csv", "xlsx"]
