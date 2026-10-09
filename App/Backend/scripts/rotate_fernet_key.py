"""Rotacion de la clave Fernet con re-cifrado transaccional (c-63c, IAH-009).

Responsabilidad:
    Re-cifrar IN SITU todas las columnas cifradas con Fernet del inventario,
    usando el conjunto `MultiFernet` configurado (clave nueva como activa,
    clave anterior como respaldo). El re-cifrado descifra cada valor con la
    clave vigente y lo vuelve a cifrar con la clave ACTIVA, dentro de UNA
    transaccion: cualquier error revierte todo (sin estado parcial).

Respaldo previo OBLIGATORIO (design.md D-C4):
    El script exige `--backup-path` apuntando a un archivo de respaldo existente,
    de tamano no trivial y con el marcador de un dump de `pg_dump` (formato plano
    `-- PostgreSQL database dump` o formato custom `PGDMP`). Si falta, no existe,
    es demasiado pequeno o no parece un dump, aborta con codigo no-cero SIN tocar
    datos. El respaldo es la red de seguridad para revertir: reponer la clave
    anterior como activa (o restaurar el respaldo) deja los datos legibles.

Inventario explicito (design.md D-C5):
    El script enumera las columnas, NO las infiere. Un test verifica que la lista
    cubre exactamente las columnas declaradas con `EncryptedText`:
      - incidente.descripcion_original        (NOT NULL)
      - telefonia_ingreso.caller_cifrado      (nullable)
      - telefonia_ingreso.transcript_original (nullable)
      - users.totp_secret                     (nullable, c-63b)

Orden de rotacion (design.md D-C4):
    (1) configurar la clave nueva como activa y la anterior como respaldo;
    (2) ejecutar este script; (3) confirmar por conteo; (4) recien entonces
    retirar la clave anterior del conjunto.

Uso:
    cd App/Backend
    python -m scripts.rotate_fernet_key --backup-path /ruta/al/respaldo.dump
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.logging import get_logger
from app.models.incidente import Incidente
from app.models.telefonia_ingreso import TelefoniaIngreso
from app.models.user import User

logger = get_logger(__name__)


class MissingBackupError(RuntimeError):
    """El respaldo previo obligatorio falta o no es valido."""


# Tamano minimo de un respaldo usable (S2). Un archivo menor no es un dump real
# de la base y no sirve como red de seguridad de la rotacion.
MIN_BACKUP_BYTES = 1024

# Marcadores aceptados del encabezado de un dump de pg_dump: formato plano y
# formato custom (magic `PGDMP`). Se inspecciona solo el encabezado.
_BACKUP_MARKERS: tuple[bytes, ...] = (
    b"-- PostgreSQL database dump",
    b"PGDMP",
)
_MARKER_SCAN_BYTES = 8192


# Inventario explicito: (etiqueta, modelo, atributo). NO inferir tablas.
INVENTORY: tuple[tuple[str, Type, str], ...] = (
    ("incidente.descripcion_original", Incidente, "descripcion_original"),
    ("telefonia_ingreso.caller_cifrado", TelefoniaIngreso, "caller_cifrado"),
    ("telefonia_ingreso.transcript_original", TelefoniaIngreso, "transcript_original"),
    ("users.totp_secret", User, "totp_secret"),
)


@dataclass
class RotationReport:
    """Conteo de filas re-cifradas por columna del inventario."""

    counts: dict[str, int] = field(default_factory=dict)
    total: int = 0


def assert_backup(backup_path: str | Path | None) -> Path:
    """Verifica que exista un respaldo previo USABLE antes de tocar datos.

    Criterios (S2): el archivo debe existir, ser un archivo regular, tener al
    menos `MIN_BACKUP_BYTES` y presentar el marcador de un dump de `pg_dump`
    (plano o custom) en su encabezado. Asi un operador que pasa el archivo
    equivocado aborta sin re-cifrar.

    Raises:
        MissingBackupError: si la ruta falta, no existe, es demasiado pequena o
            no parece un dump utilizable.
    """
    if not backup_path:
        raise MissingBackupError(
            "Se requiere --backup-path con un respaldo previo existente; "
            "la rotacion aborta sin tocar datos."
        )
    path = Path(backup_path)
    if not path.is_file():
        raise MissingBackupError(f"El respaldo previo no existe: {path}")

    size = path.stat().st_size
    if size < MIN_BACKUP_BYTES:
        raise MissingBackupError(
            f"El respaldo previo es demasiado pequeno para ser un dump utilizable "
            f"({size} bytes < {MIN_BACKUP_BYTES}): {path}"
        )

    with path.open("rb") as fh:
        head = fh.read(_MARKER_SCAN_BYTES)
    if not any(marker in head for marker in _BACKUP_MARKERS):
        raise MissingBackupError(
            "El respaldo previo no parece un dump de pg_dump (falta el marcador "
            f"esperado en su encabezado): {path}"
        )
    return path


async def _reencrypt_column(session: AsyncSession, model: Type, attr: str) -> int:
    """Descifra y re-cifra con la clave activa todas las filas no nulas.

    Fuerza el re-cifrado aunque el valor en claro no cambie: se marca el
    atributo como modificado para que el TypeDecorator vuelva a cifrar con la
    clave activa en el `flush`. Retorna el numero de filas procesadas.
    """
    column = getattr(model, attr)
    rows = (
        await session.execute(select(model).where(column.is_not(None)))
    ).scalars().all()

    for obj in rows:
        plaintext = getattr(obj, attr)  # descifrado por MultiFernet (activa/anterior)
        setattr(obj, attr, plaintext)
        flag_modified(obj, attr)  # fuerza el re-cifrado con la clave activa
    await session.flush()
    return len(rows)


async def rotate_fernet_key(
    session: AsyncSession,
    *,
    backup_path: str | Path | None,
    commit: bool = False,
) -> RotationReport:
    """Re-cifra en UNA transaccion las columnas Fernet del inventario.

    Args:
        session:     sesion async de SQLAlchemy.
        backup_path: ruta al respaldo previo obligatorio.
        commit:      si True, confirma la transaccion al terminar.

    Returns:
        RotationReport con el conteo por columna y el total.

    Raises:
        MissingBackupError: si el respaldo previo falta o no es valido.
        Exception: cualquier fallo del re-cifrado (se revierte la transaccion).
    """
    backup = assert_backup(backup_path)
    report = RotationReport()

    try:
        for label, model, attr in INVENTORY:
            count = await _reencrypt_column(session, model, attr)
            report.counts[label] = count
            report.total += count
        if commit:
            await session.commit()
    except Exception:
        await session.rollback()
        raise

    logger.info(
        "fernet_rotation_completed",
        backup=str(backup),
        total=report.total,
        counts=report.counts,
    )
    return report


async def _run(backup_path: str) -> RotationReport:
    """Abre una sesion sobre el engine de la aplicacion y ejecuta la rotacion."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.core.database import engine

    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            return await rotate_fernet_key(
                session, backup_path=backup_path, commit=True
            )
    finally:
        await engine.dispose()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rota la clave Fernet re-cifrando las columnas del inventario.",
    )
    parser.add_argument(
        "--backup-path",
        required=True,
        help="Ruta al respaldo previo de los datos (obligatorio).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada CLI. Devuelve 0 en exito, no-cero si aborta."""
    args = _build_parser().parse_args(argv)

    try:
        assert_backup(args.backup_path)
    except MissingBackupError as exc:
        print(f"[abort] {exc}", file=sys.stderr)
        return 2

    report = asyncio.run(_run(args.backup_path))
    print(
        "Rotacion de la clave Fernet completada: "
        f"{report.total} filas re-cifradas. {report.counts}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
