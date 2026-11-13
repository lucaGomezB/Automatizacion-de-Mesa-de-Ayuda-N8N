#!/usr/bin/env python3
"""Recuperacion append-only de la memoria de Engram omitida por el watermark (c-208).

Por que: el export incremental de `engram` 1.20.0 filtra con un watermark GLOBAL
(`lastChunkTime`, el max `created_at` de los chunks de TODAS las maquinas). Los
datos locales mas viejos que el chunk de otra maquina no se re-exportan nunca, y
un clon limpio puede quedar sin observaciones que una relacion referencia.

Modos:
- DETECCION (por defecto, SOLO LECTURA): abre la base local con `mode=ro`, compara
  contra la union de los chunks de `.engram/` e imprime SOLO CONTEOS de las
  observaciones y los prompts del proyecto ausentes en todos los chunks.
- REPARACION (opt-in, `--repair --confirm-publish`): adelanta `updated_at` SOLO de
  las observaciones estrictamente faltantes (el contenido no cambia) y ejecuta
  `engram sync --project <proyecto>` (NUNCA `--all`), lo que produce un chunk
  NUEVO. Los chunks existentes jamas se editan ni se borran.

ADVERTENCIA: la reparacion PUBLICA memoria. El chunk nuevo, una vez commiteado en
el repositorio publico, es inmutable por contrato (append-only): no se puede
editar ni borrar. Revisar el conteo de la deteccion antes de confirmar.

Los prompts no se reparan por este mecanismo: la tabla `user_prompts` no tiene
`updated_at`, de modo que solo se detectan y se informan.

Base local: `$ENGRAM_DATA_DIR/engram.db`, por defecto `~/.engram/engram.db`
(`engram --help`: ENGRAM_DATA_DIR).

Uso:
    python3 scripts/security/reexport_missing_engram_data.py [--engram-dir .engram]
        [--db RUTA] [--project NOMBRE] [--repair --confirm-publish] [--backup RUTA]

Exit codes:
    0 = nada ausente (o reparacion verificada), 1 = hay ausentes o fallo el sync,
    2 = error de uso o de I/O.

Nunca imprime titulos, contenido, prompts ni ids de la memoria: solo conteos.
Solo biblioteca estandar.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

DEFAULT_PROJECT = "Automatizacion-de-Mesa-de-Ayuda-N8N"
_SUMMARY = (
    "Detecta (solo lectura) las observaciones y prompts del proyecto ausentes en los "
    "chunks de Engram y, con --repair --confirm-publish, los re-exporta en un chunk nuevo."
)


@dataclass(frozen=True)
class Missing:
    observations: tuple[str, ...]
    prompts: tuple[str, ...]
    deleted_observations: int
    observations_without_sync_id: int


def default_db_path() -> Path:
    data_dir = os.environ.get("ENGRAM_DATA_DIR")
    base = Path(data_dir) if data_dir else Path.home() / ".engram"
    return base / "engram.db"


def open_readonly(db_path: Path) -> sqlite3.Connection:
    """Abre la base en modo solo lectura; no la crea si no existe."""
    return sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True)


def _chunk_ids(engram_dir: Path) -> tuple[set[str], set[str]]:
    observations: set[str] = set()
    prompts: set[str] = set()
    for path in sorted((engram_dir / "chunks").glob("*.jsonl.gz")):
        with gzip.open(path, "rb") as handle:
            chunk = json.loads(handle.read().decode("utf-8"))
        observations.update(o["sync_id"] for o in chunk.get("observations") or [] if o.get("sync_id"))
        prompts.update(p["sync_id"] for p in chunk.get("prompts") or [] if p.get("sync_id"))
    return observations, prompts


def find_missing(conn: sqlite3.Connection, project: str, engram_dir: Path) -> Missing:
    chunk_obs, chunk_prompts = _chunk_ids(engram_dir)
    live = [
        row[0]
        for row in conn.execute(
            "SELECT sync_id FROM observations WHERE lower(project) = lower(?) AND deleted_at IS NULL"
            " AND sync_id IS NOT NULL ORDER BY id",
            (project,),
        )
    ]
    prompts = [
        row[0]
        for row in conn.execute(
            "SELECT sync_id FROM user_prompts WHERE lower(project) = lower(?) AND sync_id IS NOT NULL ORDER BY id",
            (project,),
        )
    ]
    deleted = conn.execute(
        "SELECT COUNT(*) FROM observations WHERE lower(project) = lower(?) AND deleted_at IS NOT NULL"
        " AND sync_id IS NOT NULL",
        (project,),
    ).fetchone()[0]
    no_sync_id = conn.execute(
        "SELECT COUNT(*) FROM observations WHERE lower(project) = lower(?) AND deleted_at IS NULL"
        " AND sync_id IS NULL",
        (project,),
    ).fetchone()[0]
    return Missing(
        observations=tuple(s for s in live if s not in chunk_obs),
        prompts=tuple(s for s in prompts if s not in chunk_prompts),
        deleted_observations=deleted,
        observations_without_sync_id=no_sync_id,
    )


def _describe(label: str, found: Missing) -> str:
    return (
        f"{label}: {len(found.observations)} observaciones y {len(found.prompts)} prompts "
        f"ausentes en los chunks (no cuentan: {found.deleted_observations} borradas, "
        f"{found.observations_without_sync_id} sin sync_id)"
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _run_engram(argv: Sequence[str], cwd: Path) -> int:
    return subprocess.run(list(argv), cwd=str(cwd), check=False).returncode


def _backup(db_path: Path, backup_path: Path) -> None:
    source = open_readonly(db_path)
    try:
        target = sqlite3.connect(backup_path)
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()


def bump_updated_at(db_path: Path, project: str, sync_ids: Sequence[str], stamp: str) -> int:
    """Adelanta `updated_at` SOLO de las observaciones indicadas del proyecto."""
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            changed = 0
            for sync_id in sync_ids:
                cur = conn.execute(
                    "UPDATE observations SET updated_at = ? WHERE sync_id = ? AND lower(project) = lower(?)"
                    " AND deleted_at IS NULL",
                    (stamp, sync_id, project),
                )
                changed += cur.rowcount
        return changed
    finally:
        conn.close()


def _valid_project(project: str) -> bool:
    return bool(project) and not project.startswith("-")


def _detect(db_path: Path, project: str, engram_dir: Path) -> Missing:
    conn = open_readonly(db_path)
    try:
        return find_missing(conn, project, engram_dir)
    finally:
        conn.close()


def _repair(args, found: Missing, runner: Callable, now: Callable[[], str]) -> int:
    db_path = args.db or default_db_path()
    backup = args.backup or db_path.with_name(db_path.name + ".pre-c208.bak")
    _backup(db_path, backup)
    changed = bump_updated_at(db_path, args.project, found.observations, now())
    print(f"Reparacion: updated_at adelantado en {changed} observaciones (respaldo de la base en {backup})")
    argv = [args.engram_bin, "sync", "--project", args.project]
    code = runner(argv, args.engram_dir.resolve().parent)
    if code != 0:
        print(f"error: engram sync termino con codigo {code}; revisar y no commitear a ciegas", file=sys.stderr)
        return 1
    after = _detect(db_path, args.project, args.engram_dir)
    print(_describe("Deteccion posterior", after))
    return 0 if not after.observations else 1


def main(
    argv: Sequence[str] | None = None,
    runner: Callable | None = None,
    now: Callable[[], str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=_SUMMARY)
    parser.add_argument("--engram-dir", default=".engram", type=Path)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--repair", action="store_true",
                        help="adelanta updated_at de las observaciones faltantes y corre engram sync --project")
    parser.add_argument("--confirm-publish", action="store_true",
                        help="confirma que la reparacion PUBLICA memoria (append-only, irreversible)")
    parser.add_argument("--backup", type=Path, default=None,
                        help="copia de la base antes de reparar (por defecto <db>.pre-c208.bak)")
    parser.add_argument("--engram-bin", default="engram")
    args = parser.parse_args(argv)
    if not _valid_project(args.project):
        print("error: --project invalido (vacio o con forma de flag)", file=sys.stderr)
        return 2
    if args.repair and not args.confirm_publish:
        print(
            "error: --repair publica memoria en un repositorio publico y es append-only; "
            "agregar --confirm-publish tras revisar la deteccion",
            file=sys.stderr,
        )
        return 2
    db_path = args.db or default_db_path()
    try:
        found = _detect(db_path, args.project, args.engram_dir)
    except sqlite3.OperationalError:
        print(f"error: no se pudo abrir la base {db_path} en solo lectura", file=sys.stderr)
        return 2
    print(_describe(f"Deteccion (solo lectura) proyecto={args.project}", found))
    if not args.repair:
        return 1 if (found.observations or found.prompts) else 0
    if not found.observations:
        print("Nada que reparar: no hay observaciones ausentes.")
        return 0
    return _repair(args, found, runner or _run_engram, now or _utc_now)


if __name__ == "__main__":
    sys.exit(main())
