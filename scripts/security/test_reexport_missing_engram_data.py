"""Tests del procedimiento de recuperacion append-only de la memoria (c-208).

El modulo `scripts/security/reexport_missing_engram_data.py` detecta (SOLO
LECTURA) las observaciones y prompts del proyecto que existen en la base local
de Engram y NO estan en ningun chunk, y, bajo un flag explicito, adelanta
`updated_at` de las observaciones estrictamente faltantes y ejecuta
`engram sync --project <proyecto>` para que se publique un chunk NUEVO.

Estos tests NO tocan la base real ni `.engram/` real: usan una base SQLite
temporal con la forma de esquema de la que depende el script, un directorio de
chunks temporal y un ejecutor de `engram` inyectado (mock) que registra el argv.

Ejecucion (desde la raiz del repo):
    python3 -m pytest scripts/security/test_reexport_missing_engram_data.py -q

Strict TDD: RED (modulo ausente) -> GREEN -> TRIANGULATE -> REFACTOR.
Todos los datos son sinteticos; los centinelas SENTINEL_* verifican que la salida
nunca imprime contenido de la memoria.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "security"))

import reexport_missing_engram_data as recovery  # noqa: E402

PROJECT = "proyecto-sintetico"
OTHER_PROJECT = "otro-proyecto"
SENTINEL_TITLE = "SENTINEL_TITLE_no_imprimir"
SENTINEL_CONTENT = "SENTINEL_CONTENT_no_imprimir"
SENTINEL_PROMPT = "SENTINEL_PROMPT_no_imprimir"
OLD_TS = "2026-01-01 00:00:00"
FIXED_NOW = "2026-11-13 12:00:00"

_SCHEMA = """
CREATE TABLE observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_id TEXT,
    session_id TEXT NOT NULL DEFAULT 's',
    type TEXT NOT NULL DEFAULT 'note',
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    project TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);
CREATE TABLE user_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_id TEXT,
    session_id TEXT NOT NULL DEFAULT 's',
    content TEXT NOT NULL,
    project TEXT,
    created_at TEXT NOT NULL
);
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_db(
    path: Path,
    observations: list[tuple[str | None, str | None, str | None]] = (),
    prompts: list[tuple[str | None, str | None]] = (),
) -> Path:
    """observations: (sync_id, project, deleted_at); prompts: (sync_id, project)."""
    conn = sqlite3.connect(path)
    conn.executescript(_SCHEMA)
    for sync_id, project, deleted_at in observations:
        conn.execute(
            "INSERT INTO observations (sync_id, title, content, project, created_at,"
            " updated_at, deleted_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sync_id, SENTINEL_TITLE, SENTINEL_CONTENT, project, OLD_TS, OLD_TS, deleted_at),
        )
    for sync_id, project in prompts:
        conn.execute(
            "INSERT INTO user_prompts (sync_id, content, project, created_at)"
            " VALUES (?, ?, ?, ?)",
            (sync_id, SENTINEL_PROMPT, project, OLD_TS),
        )
    conn.commit()
    conn.close()
    return path


def _write_chunk(engram: Path, name: str, observations=(), prompts=()) -> Path:
    chunks = engram / "chunks"
    chunks.mkdir(parents=True, exist_ok=True)
    path = chunks / f"{name}.jsonl.gz"
    body = {
        "observations": [{"sync_id": s} for s in observations],
        "prompts": [{"sync_id": s} for s in prompts],
    }
    with gzip.open(path, "wb") as handle:
        handle.write(json.dumps(body).encode("utf-8"))
    return path


def _dump(db: Path) -> list[tuple]:
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute("SELECT * FROM observations ORDER BY id").fetchall()
        rows += conn.execute("SELECT * FROM user_prompts ORDER BY id").fetchall()
        return rows
    finally:
        conn.close()


def _obs_row(db: Path, sync_id: str) -> dict:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        return dict(
            conn.execute("SELECT * FROM observations WHERE sync_id = ?", (sync_id,)).fetchone()
        )
    finally:
        conn.close()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FakeRunner:
    """Reemplaza la ejecucion de `engram`: registra argv/cwd y simula el export."""

    def __init__(self, returncode: int = 0, export_into: Path | None = None, db: Path | None = None):
        self.calls: list[tuple[list[str], Path]] = []
        self.returncode = returncode
        self.export_into = export_into
        self.db = db

    def __call__(self, argv, cwd):
        self.calls.append((list(argv), Path(cwd)))
        if self.returncode == 0 and self.export_into is not None and self.db is not None:
            # Simula el chunk nuevo: exporta las observaciones con updated_at adelantado.
            conn = sqlite3.connect(self.db)
            bumped = [
                r[0]
                for r in conn.execute(
                    "SELECT sync_id FROM observations WHERE updated_at != ? AND project = ?",
                    (OLD_TS, PROJECT),
                )
            ]
            conn.close()
            _write_chunk(self.export_into, "nuevo0000", observations=bumped)
        return self.returncode


def _main(argv, runner=None, capsys=None):
    code = recovery.main(argv, runner=runner, now=lambda: FIXED_NOW)
    out = capsys.readouterr() if capsys else None
    return code, (out.out + out.err) if out else ""


@pytest.fixture
def world(tmp_path):
    """Una memoria con: 2 obs en chunks, 3 faltantes, 1 de otro proyecto, 1 borrada."""
    engram = tmp_path / "repo" / ".engram"
    _write_chunk(engram, "viejo1111", observations=["obs-1", "obs-2"], prompts=["pr-1"])
    db = _make_db(
        tmp_path / "engram.db",
        observations=[
            ("obs-1", PROJECT, None),
            ("obs-2", PROJECT, None),
            ("obs-miss-1", PROJECT, None),
            ("obs-miss-2", PROJECT, None),
            ("obs-miss-3", PROJECT, None),
            ("obs-other", OTHER_PROJECT, None),
            ("obs-deleted", PROJECT, "2026-02-02 00:00:00"),
            (None, PROJECT, None),
        ],
        prompts=[("pr-1", PROJECT), ("pr-miss-1", PROJECT), ("pr-miss-2", PROJECT), ("pr-other", OTHER_PROJECT)],
    )
    return {"engram": engram, "db": db, "tmp": tmp_path}


def _cli(world, *extra):
    return [
        "--engram-dir", str(world["engram"]),
        "--db", str(world["db"]),
        "--project", PROJECT,
        *extra,
    ]


# ---------------------------------------------------------------------------
# 6.1 Deteccion (solo lectura)
# ---------------------------------------------------------------------------
def test_detection_counts_only_strictly_missing_project_rows(world):
    conn = recovery.open_readonly(world["db"])
    try:
        found = recovery.find_missing(conn, PROJECT, world["engram"])
    finally:
        conn.close()

    assert found.observations == ("obs-miss-1", "obs-miss-2", "obs-miss-3")
    assert found.prompts == ("pr-miss-1", "pr-miss-2")
    assert found.deleted_observations == 1
    assert found.observations_without_sync_id == 1


def test_detection_of_a_fully_exported_project_reports_zero(tmp_path):
    engram = tmp_path / ".engram"
    _write_chunk(engram, "todo0000", observations=["a", "b"], prompts=["p"])
    db = _make_db(tmp_path / "e.db", [("a", PROJECT, None), ("b", PROJECT, None)], [("p", PROJECT)])

    conn = recovery.open_readonly(db)
    found = recovery.find_missing(conn, PROJECT, engram)
    conn.close()

    assert found.observations == () and found.prompts == ()


def test_readonly_connection_rejects_writes(world):
    conn = recovery.open_readonly(world["db"])
    try:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("UPDATE observations SET updated_at = 'x'")
    finally:
        conn.close()


def test_open_readonly_does_not_create_a_missing_database(tmp_path):
    ghost = tmp_path / "no-existe.db"

    with pytest.raises(sqlite3.OperationalError):
        recovery.open_readonly(ghost)

    assert not ghost.exists()


def test_default_invocation_is_read_only_and_prints_counts_only(world, capsys):
    before = _dump(world["db"])
    chunks_before = {p: _sha(p) for p in world["engram"].rglob("*") if p.is_file()}
    runner = FakeRunner()

    code, out = _main(_cli(world), runner, capsys)

    assert code == 1  # hay faltantes: la deteccion lo senala con exit 1
    assert runner.calls == []
    assert _dump(world["db"]) == before
    assert {p: _sha(p) for p in world["engram"].rglob("*") if p.is_file()} == chunks_before
    assert "3 observaciones" in out and "2 prompts" in out
    for forbidden in (SENTINEL_TITLE, SENTINEL_CONTENT, SENTINEL_PROMPT, "obs-miss", "pr-miss"):
        assert forbidden not in out


def test_detection_with_nothing_missing_exits_zero(tmp_path, capsys):
    engram = tmp_path / ".engram"
    _write_chunk(engram, "todo0000", observations=["a"], prompts=["p"])
    db = _make_db(tmp_path / "e.db", [("a", PROJECT, None)], [("p", PROJECT)])

    code, out = _main(
        ["--engram-dir", str(engram), "--db", str(db), "--project", PROJECT], FakeRunner(), capsys
    )

    assert code == 0
    assert "0 observaciones" in out and "0 prompts" in out


def test_missing_database_is_a_usage_error(tmp_path, capsys):
    engram = tmp_path / ".engram"
    _write_chunk(engram, "x0000000", observations=["a"])

    code, out = _main(
        ["--engram-dir", str(engram), "--db", str(tmp_path / "nope.db"), "--project", PROJECT],
        FakeRunner(),
        capsys,
    )

    assert code == 2
    assert not (tmp_path / "nope.db").exists()


def test_default_db_path_honours_engram_data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("ENGRAM_DATA_DIR", str(tmp_path / "datos"))

    assert recovery.default_db_path() == tmp_path / "datos" / "engram.db"


def test_default_db_path_falls_back_to_home_engram(monkeypatch, tmp_path):
    monkeypatch.delenv("ENGRAM_DATA_DIR", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    assert recovery.default_db_path() == tmp_path / ".engram" / "engram.db"


# ---------------------------------------------------------------------------
# 6.2 Reparacion (opt-in): bump de updated_at + engram sync --project
# ---------------------------------------------------------------------------
def test_repair_without_confirmation_refuses_and_changes_nothing(world, capsys):
    before = _dump(world["db"])
    runner = FakeRunner()

    code, out = _main(_cli(world, "--repair"), runner, capsys)

    assert code == 2
    assert runner.calls == []
    assert _dump(world["db"]) == before
    assert "--confirm-publish" in out


def test_repair_advances_updated_at_only_of_strictly_missing_rows(world, capsys):
    runner = FakeRunner()
    others = {s: _obs_row(world["db"], s) for s in ("obs-1", "obs-2", "obs-other", "obs-deleted")}
    prompts_before = [r for r in _dump(world["db"]) if len(r) == 6 and r[3] == SENTINEL_PROMPT]

    _main(_cli(world, "--repair", "--confirm-publish"), runner, capsys)

    for sync_id in ("obs-miss-1", "obs-miss-2", "obs-miss-3"):
        row = _obs_row(world["db"], sync_id)
        assert row["updated_at"] == FIXED_NOW
        assert row["created_at"] == OLD_TS
        assert row["title"] == SENTINEL_TITLE
        assert row["content"] == SENTINEL_CONTENT
        assert row["project"] == PROJECT
    for sync_id, original in others.items():
        assert _obs_row(world["db"], sync_id) == original
    rows_null_sync = sqlite3.connect(world["db"]).execute(
        "SELECT updated_at FROM observations WHERE sync_id IS NULL"
    ).fetchall()
    assert rows_null_sync == [(OLD_TS,)]
    assert [r for r in _dump(world["db"]) if len(r) == 6 and r[3] == SENTINEL_PROMPT] == prompts_before


def test_repair_invokes_engram_with_explicit_project_and_never_all(world, capsys):
    runner = FakeRunner()

    _main(_cli(world, "--repair", "--confirm-publish"), runner, capsys)

    assert len(runner.calls) == 1
    argv, cwd = runner.calls[0]
    assert argv == ["engram", "sync", "--project", PROJECT]
    assert "--all" not in argv
    assert cwd == world["engram"].parent


def test_repair_leaves_existing_chunks_untouched_and_appends_a_new_one(world, capsys):
    runner = FakeRunner(export_into=world["engram"], db=world["db"])
    before = {p: _sha(p) for p in (world["engram"] / "chunks").glob("*.jsonl.gz")}

    code, out = _main(_cli(world, "--repair", "--confirm-publish"), runner, capsys)

    after = {p: _sha(p) for p in (world["engram"] / "chunks").glob("*.jsonl.gz") if p in before}
    assert after == before
    assert (world["engram"] / "chunks" / "nuevo0000.jsonl.gz").exists()
    # Quedan 0 observaciones ausentes; los 2 prompts no son recuperables por bump.
    assert "0 observaciones" in out.split("posterior")[-1]
    assert code == 0


def test_repair_backs_up_the_database_before_touching_it(world, capsys):
    backup = world["tmp"] / "copia.db"
    original = _dump(world["db"])

    _main(_cli(world, "--repair", "--confirm-publish", "--backup", str(backup)), FakeRunner(), capsys)

    assert _dump(backup) == original


def test_repair_reports_engram_failure_with_nonzero_exit(world, capsys):
    runner = FakeRunner(returncode=3)

    code, out = _main(_cli(world, "--repair", "--confirm-publish"), runner, capsys)

    assert code == 1
    assert "engram sync" in out and "3" in out


def test_repair_with_nothing_missing_does_not_call_engram(tmp_path, capsys):
    engram = tmp_path / ".engram"
    _write_chunk(engram, "todo0000", observations=["a"])
    db = _make_db(tmp_path / "e.db", [("a", PROJECT, None)])
    runner = FakeRunner()

    code, _out = _main(
        ["--engram-dir", str(engram), "--db", str(db), "--project", PROJECT,
         "--repair", "--confirm-publish"],
        runner,
        capsys,
    )

    assert code == 0
    assert runner.calls == []


def test_repair_output_never_prints_memory_content(world, capsys):
    runner = FakeRunner(export_into=world["engram"], db=world["db"])

    _code, out = _main(_cli(world, "--repair", "--confirm-publish"), runner, capsys)

    for forbidden in (SENTINEL_TITLE, SENTINEL_CONTENT, SENTINEL_PROMPT, "obs-miss", "pr-miss"):
        assert forbidden not in out


@pytest.mark.parametrize("bad_project", ["", "--all", "-x"])
def test_project_that_could_be_parsed_as_a_flag_is_rejected(world, capsys, bad_project):
    runner = FakeRunner()

    code, _out = _main(
        ["--engram-dir", str(world["engram"]), "--db", str(world["db"]),
         f"--project={bad_project}", "--repair", "--confirm-publish"],
        runner,
        capsys,
    )

    assert code == 2
    assert runner.calls == []


# ---------------------------------------------------------------------------
# Engram normaliza el nombre del proyecto a minusculas en su base local
# ---------------------------------------------------------------------------
def test_project_name_is_matched_case_insensitively(tmp_path, capsys):
    engram = tmp_path / ".engram"
    _write_chunk(engram, "viejo0000", observations=["a"])
    db = _make_db(
        tmp_path / "e.db",
        observations=[("a", "Proyecto-Mixto", None), ("m", "proyecto-mixto", None)],
        prompts=[("p", "proyecto-mixto")],
    )

    conn = recovery.open_readonly(db)
    found = recovery.find_missing(conn, "Proyecto-MIXTO", engram)
    conn.close()

    assert found.observations == ("m",)
    assert found.prompts == ("p",)


def test_repair_bumps_rows_stored_under_the_lowercase_project_name(tmp_path, capsys):
    engram = tmp_path / "repo" / ".engram"
    _write_chunk(engram, "viejo0000", observations=["a"])
    db = _make_db(tmp_path / "e.db", observations=[("m", "proyecto-mixto", None)])
    runner = FakeRunner()

    code, _out = _main(
        ["--engram-dir", str(engram), "--db", str(db), "--project", "Proyecto-Mixto",
         "--repair", "--confirm-publish"],
        runner,
        capsys,
    )

    assert _obs_row(db, "m")["updated_at"] == FIXED_NOW
    assert runner.calls[0][0] == ["engram", "sync", "--project", "Proyecto-Mixto"]
