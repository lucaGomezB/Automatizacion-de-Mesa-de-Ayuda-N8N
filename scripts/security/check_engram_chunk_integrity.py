#!/usr/bin/env python3
"""Guarda de integridad referencial de la memoria de Engram (c-208).

La carpeta `.engram/` se versiona en un repositorio PUBLICO. Un clon limpio
restaura la memoria con `engram sync --import`, y ese import falla de forma
dura ("relation FK precondition not met: referenced observation missing") si
alguna mutacion de relacion referencia una observacion que NO esta en ningun
chunk. Este script reproduce esa precondicion antes de publicar:

1. descomprime TODOS los `<engram>/chunks/*.jsonl.gz` (solo lectura);
2. recolecta los `sync_id` de las observaciones de la UNION de chunks;
3. crea una base SQLite TEMPORAL (en memoria) con FK de las relaciones hacia las
   observaciones y aplica las mutaciones `entity == "relation"`, `op == "upsert"`;
4. cada FK violada es una referencia colgante: se nombra la relacion y el extremo
   (`source_id` o `target_id`) faltante.

Solo biblioteca estandar; sin red ni secretos. NO modifica chunks ni manifest.
Nunca imprime contenido de la memoria: solo ids de relaciones y de extremos.

Uso:
    python3 scripts/security/check_engram_chunk_integrity.py [DIR_ENGRAM]

`DIR_ENGRAM` por defecto es `.engram`.

Exit codes:
    0 = integra (0 referencias colgantes), 1 = referencias colgantes,
    2 = error de uso o de I/O (directorio ausente, sin chunks, chunk ilegible).
"""

from __future__ import annotations

import argparse
import gzip
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

_ENDPOINT_FIELDS = ("source_id", "target_id")


class ChunkError(Exception):
    """Un chunk no se pudo leer o no tiene la forma esperada."""


@dataclass(frozen=True)
class Dangling:
    """Un extremo de relacion ausente en la union de chunks."""

    chunk: str
    relation: str
    field: str
    missing_id: str

    def render(self) -> str:
        return (
            f"{self.chunk}: relacion {self.relation}: "
            f"{self.field} {self.missing_id} ausente en todos los chunks"
        )


@dataclass(frozen=True)
class Report:
    chunks: int
    observations: int
    relations: int
    dangling: tuple[Dangling, ...]


def parse_chunk(path: Path) -> dict:
    """Lee un chunk `.jsonl.gz`: un unico objeto JSON."""
    try:
        with gzip.open(path, "rb") as handle:
            chunk = json.loads(handle.read().decode("utf-8"))
    except (OSError, EOFError, ValueError) as exc:
        raise ChunkError(f"chunk ilegible {path.name}: {type(exc).__name__}") from exc
    if not isinstance(chunk, dict):
        raise ChunkError(f"chunk ilegible {path.name}: no es un objeto JSON")
    return chunk


def collect_observation_ids(chunks: Sequence[dict]) -> set[str]:
    """`sync_id` de las observaciones de la union de chunks."""
    return {
        obs["sync_id"]
        for chunk in chunks
        for obs in chunk.get("observations") or []
        if obs.get("sync_id")
    }


def iter_relation_upserts(chunk: dict) -> Iterator[dict]:
    """Payloads de las mutaciones de relacion `upsert`; `mutations` ausente/nulo = vacio."""
    for mutation in chunk.get("mutations") or []:
        if mutation.get("entity") != "relation" or mutation.get("op") != "upsert":
            continue
        payload = mutation.get("payload")
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except ValueError as exc:
            raise ChunkError("payload de relacion ilegible") from exc
        if not isinstance(data, dict):
            raise ChunkError("payload de relacion ilegible")
        data.setdefault("sync_id", mutation.get("entity_key"))
        yield data


def _new_store(observation_ids: set[str]) -> sqlite3.Connection:
    store = sqlite3.connect(":memory:")
    store.execute("PRAGMA foreign_keys=ON")
    store.execute("CREATE TABLE observations (sync_id TEXT PRIMARY KEY)")
    store.execute(
        "CREATE TABLE relations ("
        " sync_id TEXT PRIMARY KEY,"
        " source_id TEXT NOT NULL REFERENCES observations(sync_id),"
        " target_id TEXT NOT NULL REFERENCES observations(sync_id))"
    )
    store.executemany(
        "INSERT INTO observations VALUES (?)", [(i,) for i in sorted(observation_ids)]
    )
    return store


def _missing_endpoints(store: sqlite3.Connection, relation: dict) -> list[tuple[str, str]]:
    missing = []
    for field in _ENDPOINT_FIELDS:
        value = relation.get(field)
        known = store.execute(
            "SELECT 1 FROM observations WHERE sync_id = ?", (value,)
        ).fetchone()
        if not known:
            missing.append((field, str(value)))
    return missing


def apply_relations(
    named_chunks: Sequence[tuple[str, dict]], observation_ids: set[str]
) -> tuple[int, list[Dangling]]:
    """Aplica las relaciones sobre la base temporal; devuelve (relaciones, colgantes)."""
    store = _new_store(observation_ids)
    applied = 0
    dangling: list[Dangling] = []
    try:
        for name, chunk in named_chunks:
            for relation in iter_relation_upserts(chunk):
                applied += 1
                row = (relation.get("sync_id"), relation.get("source_id"), relation.get("target_id"))
                try:
                    store.execute("INSERT OR REPLACE INTO relations VALUES (?, ?, ?)", row)
                except sqlite3.IntegrityError:
                    for field, missing in _missing_endpoints(store, relation):
                        dangling.append(
                            Dangling(name, str(relation.get("sync_id")), field, missing)
                        )
    finally:
        store.close()
    return applied, dangling


def check(engram_dir: Path) -> Report:
    if not engram_dir.is_dir():
        raise ChunkError(f"no existe el directorio {engram_dir}")
    paths = sorted((engram_dir / "chunks").glob("*.jsonl.gz"))
    if not paths:
        raise ChunkError(f"sin chunks .jsonl.gz en {engram_dir / 'chunks'}")
    named = [(path.stem.removesuffix(".jsonl"), parse_chunk(path)) for path in paths]
    observation_ids = collect_observation_ids([chunk for _n, chunk in named])
    relations, dangling = apply_relations(named, observation_ids)
    return Report(len(paths), len(observation_ids), relations, tuple(dangling))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Falla si una relacion de la memoria de Engram referencia una "
        "observacion ausente en la union de chunks."
    )
    parser.add_argument("engram_dir", nargs="?", default=".engram", type=Path)
    args = parser.parse_args(argv)
    try:
        report = check(args.engram_dir)
    except ChunkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for item in report.dangling:
        print(item.render())
    print(
        f"{report.chunks} chunks, {report.observations} observaciones, "
        f"{report.relations} mutaciones de relacion: "
        f"{len(report.dangling)} referencias colgantes"
    )
    return 1 if report.dangling else 0


if __name__ == "__main__":
    sys.exit(main())
