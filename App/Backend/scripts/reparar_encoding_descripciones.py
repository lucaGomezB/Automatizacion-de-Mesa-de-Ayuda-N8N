"""Reparacion puntual del mojibake de las descripciones de correo (c-181).

Responsabilidad:
    Reparar de forma IDEMPOTENTE y SELECTIVA las descripciones de incidentes
    corrompidas por el mojibake de doble codificacion introducido en el canal
    de ingesta (`@n8n/imap` descarta el charset de las partes
    `quoted-printable` y las re-codifica dos veces). Repara la columna
    operativa en claro `descripcion_pseudonimizada` y, para las MISMAS filas,
    la columna cifrada de auditoria `descripcion_original`
    (descifrado -> reverso -> re-cifrado).

Naturaleza:
    NO es una migracion de Alembic. Es una reparacion de DATOS de una sola vez
    que se ejecuta de forma MANUAL y controlada. La aplicacion sobre la base de
    la campana requiere aprobacion explicita del usuario. Ver
    `docs/runbook-reparacion-encoding-descripciones.md`.

Modos:
    DRY-RUN por defecto: no escribe NADA. La escritura requiere `--apply`.
    Cada fila se confirma en su PROPIA transaccion, de modo que el fallo de
    una fila no produce escrituras parciales ni impide reparar el resto.

Uso:
    cd App/Backend
    # Dry-run sobre la base de la app (engine por defecto):
    python -m scripts.reparar_encoding_descripciones
    # Dry-run sobre la base de la campana:
    python -m scripts.reparar_encoding_descripciones \\
        --database-url postgresql+asyncpg://.../mesa_de_ayuda_campana
    # Escritura explicita (requiere respaldo previo con pg_dump):
    python -m scripts.reparar_encoding_descripciones --apply
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.models.incidente import Incidente

# Firma del mojibake clasico: un byte LEAD de una secuencia UTF-8 renderizado
# como latin-1 (U+00C2, U+00C3, U+00E2, U+00F0) seguido de un byte de
# continuacion (U+0080-U+00BF). Es la guarda adicional que separa un texto
# realmente corrupto de un texto limpio que casualmente revierta.
_MOJIBAKE_SIGNATURE = re.compile(r"[\u00c2\u00c3\u00e2\u00f0][\u0080-\u00bf]")


def revertir_mojibake(value: str) -> str | None:
    """Devuelve el reverso del mojibake o None si el texto no es reversible.

    El reverso de la doble codificacion es `value.encode('latin-1').decode('utf-8')`.
    Si el texto no es codificable en latin-1 (por ejemplo un emoji) o el
    resultado no es utf-8 valido, devuelve None sin propagar la excepcion.
    """
    try:
        return value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None


def es_mojibake(value: str) -> bool:
    """Indica si `value` esta corrupto por el mojibake de doble codificacion.

    La deteccion es positiva SOLO si se cumplen las tres condiciones: (a) el
    texto presenta la firma del mojibake; (b) el reverso tiene exito; y (c) el
    texto revertido difiere estrictamente del original y ya no presenta la
    firma. Determinista y sin efectos secundarios.
    """
    if _MOJIBAKE_SIGNATURE.search(value) is None:
        return False
    revertido = revertir_mojibake(value)
    if revertido is None or revertido == value:
        return False
    return _MOJIBAKE_SIGNATURE.search(revertido) is None


@dataclass
class ReporteReparacion:
    """Conteo de filas escaneadas, reparadas y fallidas por la corrida."""

    candidatos: int = 0
    reparados: int = 0
    omitidos: int = 0
    errores: int = 0
    detalles_error: list[str] = field(default_factory=list)

    def resumen(self) -> str:
        """Resumen legible de los conteos de la corrida."""
        return (
            f"candidatos={self.candidatos} reparados={self.reparados} "
            f"omitidos={self.omitidos} errores={self.errores}"
        )


async def _reparar_fila(session: AsyncSession, incidente_id: int) -> None:
    """Repara una fila corrupta y la confirma en SU PROPIA transaccion.

    Repara `descripcion_pseudonimizada` (reverso directo) y, si el texto plano
    de `descripcion_original` tambien esta corrupto, la columna cifrada
    (descifrado -> reverso -> re-cifrado, forzado con `flag_modified`). Si el
    token no descifra, la excepcion sube SIN dejar cambios parciales: el
    llamador hace rollback y reporta la fila como error.
    """
    incidente = await session.get(Incidente, incidente_id)
    if incidente is None:
        raise LookupError(f"incidente {incidente_id} no existe")

    # Descifra la columna cifrada (puede lanzar InvalidToken): ocurre ANTES de
    # escribir nada, de modo que un token invalido no deja cambios parciales.
    original_plano = incidente.descripcion_original
    nuevo_original = original_plano
    if original_plano is not None and es_mojibake(original_plano):
        nuevo_original = revertir_mojibake(original_plano)

    nuevo_pseudo = revertir_mojibake(incidente.descripcion_pseudonimizada)
    if nuevo_pseudo is None:
        raise ValueError(
            f"incidente {incidente_id}: descripcion_pseudonimizada no reversible"
        )

    incidente.descripcion_pseudonimizada = nuevo_pseudo
    if nuevo_original != original_plano:
        incidente.descripcion_original = nuevo_original
        flag_modified(incidente, "descripcion_original")

    await session.commit()


async def reparar_descripciones(
    session: AsyncSession,
    *,
    apply: bool = False,
) -> ReporteReparacion:
    """Repara las descripciones corruptas por mojibake, fila por fila.

    Recorre las filas de `incidente` y selecciona SOLO las corruptas por firma
    (sin filtro de canal ni de borrado logico). En dry-run (`apply=False`) no
    escribe nada. Con `apply=True` repara cada candidata en su propia
    transaccion: el fallo de una fila se reporta como error sin escrituras
    parciales ni impedir el resto. La operacion es idempotente.
    """
    reporte = ReporteReparacion()

    filas = (
        await session.execute(
            select(Incidente.id, Incidente.descripcion_pseudonimizada)
        )
    ).all()

    for incidente_id, pseudonimizada in filas:
        if not es_mojibake(pseudonimizada):
            reporte.omitidos += 1
            continue

        reporte.candidatos += 1
        if not apply:
            continue

        try:
            await _reparar_fila(session, incidente_id)
        except Exception as exc:  # noqa: BLE001 - se reporta por fila
            await session.rollback()
            reporte.errores += 1
            reporte.detalles_error.append(f"incidente {incidente_id}: {exc}")
            continue

        reporte.reparados += 1

    return reporte


async def _run(database_url: str | None, apply: bool) -> ReporteReparacion:
    """Abre una sesion (engine propio o el de la app) y ejecuta la reparacion."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    if database_url is None:
        from app.core.database import engine

        engine_propio = False
    else:
        engine = create_async_engine(database_url)
        engine_propio = True

    try:
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            return await reparar_descripciones(session, apply=apply)
    finally:
        if engine_propio:
            await engine.dispose()


def _nombre_base(database_url: str | None) -> str:
    """Nombre de la base objetivo para el resumen (o el engine de la app)."""
    if database_url is None:
        return "<engine de la aplicacion>"
    return make_url(database_url).database or database_url


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reparar_encoding_descripciones",
        description=(
            "Repara el mojibake de las descripciones de correo. DRY-RUN por "
            "defecto: sin --apply no escribe en la base."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Escribe los cambios (por defecto solo informa, sin escribir).",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help=(
            "URL SQLAlchemy de la base objetivo; por defecto el engine de la "
            "aplicacion (app.core.database.engine)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada CLI. Devuelve 0 en exito."""
    args = _build_parser().parse_args(argv)
    nombre_base = _nombre_base(args.database_url)

    if args.apply:
        print(
            "[aviso] --apply ESCRIBE sobre la base objetivo: "
            f"{nombre_base}. Respaldala con pg_dump antes de continuar.",
            file=sys.stderr,
        )

    reporte = asyncio.run(_run(args.database_url, args.apply))

    modo = "apply" if args.apply else "dry-run"
    print(f"[{modo}] base objetivo: {nombre_base}")
    print(f"[{modo}] resumen: {reporte.resumen()}")
    for detalle in reporte.detalles_error:
        print(f"[error] {detalle}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
