"""Tests de la guarda de integridad referencial de la memoria de Engram (c-208).

El modulo `scripts/security/check_engram_chunk_integrity.py` carga TODOS los
chunks `.engram/chunks/*.jsonl.gz` y falla si alguna mutacion de relacion
(`entity == "relation"`, `op == "upsert"`) referencia una observacion (`sync_id`)
ausente en la union de los chunks: es la precondicion que hace fallar el import
de un clon limpio ("relation FK precondition not met").

Capas:
- Contrato del CLI (`main` con argv + capsys) sobre fixtures sinteticos.
- Un caso sobre la memoria real del repo (la union de chunks debe ser integra).

Ejecucion (desde la raiz del repo):
    python3 -m pytest scripts/security/test_check_engram_chunk_integrity.py -q

Strict TDD: RED (modulo ausente) -> GREEN -> TRIANGULATE -> REFACTOR.
Los fixtures son 100% sinteticos: ningun dato real de la memoria.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_ENGRAM = REPO_ROOT / ".engram"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "security"))

import check_engram_chunk_integrity as guard  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers (fixtures parametrizables)
# ---------------------------------------------------------------------------
def _obs(sync_id: str) -> dict:
    return {"sync_id": sync_id, "title": "t", "content": "c", "project": "p"}


def _rel_mutation(
    rel_id: str,
    source: str,
    target: str,
    op: str = "upsert",
    entity: str = "relation",
) -> dict:
    payload = {
        "sync_id": rel_id,
        "source_id": source,
        "target_id": target,
        "relation": "not_conflict",
    }
    return {
        "entity": entity,
        "entity_key": rel_id,
        "op": op,
        "payload": json.dumps(payload),
    }


def _write_chunk(engram: Path, name: str, chunk: dict) -> Path:
    """Escribe un chunk `.jsonl.gz` de una sola linea, como hace engram sync."""
    chunks = engram / "chunks"
    chunks.mkdir(parents=True, exist_ok=True)
    path = chunks / f"{name}.jsonl.gz"
    with gzip.open(path, "wb") as handle:
        handle.write(json.dumps(chunk).encode("utf-8"))
    return path


def _run(engram: Path, capsys) -> tuple[int, str]:
    code = guard.main([str(engram)])
    out = capsys.readouterr()
    return code, out.out + out.err


# ---------------------------------------------------------------------------
# 2.1 Memoria sana: una observacion y una relacion que la referencia
# ---------------------------------------------------------------------------
def test_healthy_memory_exits_zero_with_zero_dangling(tmp_path, capsys):
    _write_chunk(
        tmp_path,
        "aaaa1111",
        {
            "observations": [_obs("obs-a"), _obs("obs-b")],
            "mutations": [_rel_mutation("rel-1", "obs-a", "obs-b")],
        },
    )

    code, out = _run(tmp_path, capsys)

    assert code == 0
    assert "0 referencias colgantes" in out


# ---------------------------------------------------------------------------
# 2.2 Relacion upsert cuyo target_id no existe en ningun chunk
# ---------------------------------------------------------------------------
def test_dangling_target_fails_and_names_relation_and_endpoint(tmp_path, capsys):
    _write_chunk(
        tmp_path,
        "bbbb2222",
        {
            "observations": [_obs("obs-a")],
            "mutations": [_rel_mutation("rel-dangling", "obs-a", "obs-ghost")],
        },
    )

    code, out = _run(tmp_path, capsys)

    assert code == 1
    assert "rel-dangling" in out
    assert "obs-ghost" in out
    assert "target_id" in out
    assert "1 referencias colgantes" in out


# ---------------------------------------------------------------------------
# 2.3 Triangulacion: formas validas del chunk que NO deben fallar
# ---------------------------------------------------------------------------
def test_chunk_without_mutations_key_is_healthy(tmp_path, capsys):
    _write_chunk(tmp_path, "cccc3333", {"observations": [_obs("obs-a")]})

    code, _out = _run(tmp_path, capsys)

    assert code == 0


def test_chunk_with_null_mutations_is_healthy(tmp_path, capsys):
    _write_chunk(
        tmp_path, "dddd4444", {"observations": [_obs("obs-a")], "mutations": None}
    )

    code, _out = _run(tmp_path, capsys)

    assert code == 0


def test_non_upsert_relation_does_not_require_its_endpoints(tmp_path, capsys):
    _write_chunk(
        tmp_path,
        "eeee5555",
        {
            "observations": [_obs("obs-a")],
            "mutations": [
                _rel_mutation("rel-del", "obs-a", "obs-ghost", op="delete"),
            ],
        },
    )

    code, _out = _run(tmp_path, capsys)

    assert code == 0


def test_non_relation_mutation_is_ignored(tmp_path, capsys):
    _write_chunk(
        tmp_path,
        "ffff6666",
        {
            "observations": [_obs("obs-a")],
            "mutations": [
                _rel_mutation("x-1", "obs-ghost", "obs-ghost2", entity="session")
            ],
        },
    )

    code, _out = _run(tmp_path, capsys)

    assert code == 0


def test_several_relations_in_one_chunk_report_each_dangling_one(tmp_path, capsys):
    _write_chunk(
        tmp_path,
        "gggg7777",
        {
            "observations": [_obs("obs-a"), _obs("obs-b")],
            "mutations": [
                _rel_mutation("rel-ok", "obs-a", "obs-b"),
                _rel_mutation("rel-bad-1", "obs-a", "obs-ghost-1"),
                _rel_mutation("rel-bad-2", "obs-a", "obs-ghost-2"),
            ],
        },
    )

    code, out = _run(tmp_path, capsys)

    assert code == 1
    assert "rel-bad-1" in out and "obs-ghost-1" in out
    assert "rel-bad-2" in out and "obs-ghost-2" in out
    assert "rel-ok" not in out
    assert "2 referencias colgantes" in out


# ---------------------------------------------------------------------------
# 4.1 Triangulacion: la FK se satisface contra la UNION de todos los chunks
# ---------------------------------------------------------------------------
def test_relation_may_reference_observation_from_another_chunk(tmp_path, capsys):
    _write_chunk(tmp_path, "hhhh8888", {"observations": [_obs("obs-old")]})
    _write_chunk(
        tmp_path,
        "iiii9999",
        {
            "observations": [_obs("obs-new")],
            "mutations": [_rel_mutation("rel-x", "obs-new", "obs-old")],
        },
    )

    code, out = _run(tmp_path, capsys)

    assert code == 0
    assert "0 referencias colgantes" in out


def test_dangling_source_fails_and_names_source_id(tmp_path, capsys):
    _write_chunk(
        tmp_path,
        "jjjj0000",
        {
            "observations": [_obs("obs-b")],
            "mutations": [_rel_mutation("rel-src", "obs-ghost-src", "obs-b")],
        },
    )

    code, out = _run(tmp_path, capsys)

    assert code == 1
    assert "rel-src" in out
    assert "obs-ghost-src" in out
    assert "source_id" in out


def test_both_endpoints_missing_are_both_reported(tmp_path, capsys):
    _write_chunk(
        tmp_path,
        "kkkk1111",
        {
            "observations": [_obs("obs-a")],
            "mutations": [_rel_mutation("rel-both", "obs-g1", "obs-g2")],
        },
    )

    code, out = _run(tmp_path, capsys)

    assert code == 1
    assert "source_id" in out and "obs-g1" in out
    assert "target_id" in out and "obs-g2" in out
    assert "2 referencias colgantes" in out


# ---------------------------------------------------------------------------
# Contrato de uso y hermeticidad
# ---------------------------------------------------------------------------
def test_missing_directory_is_a_usage_error(tmp_path, capsys):
    code, out = _run(tmp_path / "no-existe", capsys)

    assert code == 2
    assert "no-existe" in out


def test_directory_without_chunks_is_a_usage_error(tmp_path, capsys):
    (tmp_path / "chunks").mkdir()

    code, _out = _run(tmp_path, capsys)

    assert code == 2


def test_corrupt_chunk_is_a_usage_error_naming_the_file(tmp_path, capsys):
    chunks = tmp_path / "chunks"
    chunks.mkdir()
    (chunks / "roto0000.jsonl.gz").write_bytes(b"esto no es gzip")

    code, out = _run(tmp_path, capsys)

    assert code == 2
    assert "roto0000" in out


def test_guard_never_modifies_chunks_or_manifest(tmp_path, capsys):
    path = _write_chunk(
        tmp_path,
        "llll2222",
        {
            "observations": [_obs("obs-a")],
            "mutations": [_rel_mutation("rel-bad", "obs-a", "obs-ghost")],
        },
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"version": 1, "chunks": []}', encoding="utf-8")
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (path, manifest)}

    _run(tmp_path, capsys)

    after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (path, manifest)}
    assert after == before
    assert sorted(p.name for p in tmp_path.rglob("*") if p.is_file()) == sorted(
        ["llll2222.jsonl.gz", "manifest.json"]
    )


# ---------------------------------------------------------------------------
# Memoria real del repositorio: debe estar integra
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not (REAL_ENGRAM / "chunks").is_dir(), reason="sin .engram/chunks en el checkout"
)
def test_real_repository_memory_has_zero_dangling_references(capsys):
    code, out = _run(REAL_ENGRAM, capsys)

    assert code == 0, out
    assert "0 referencias colgantes" in out
