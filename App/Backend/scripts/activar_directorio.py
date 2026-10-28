"""CLI env-gateado de activacion deliberada de datos reales del directorio (DIR-014).

Responsabilidad (c-153, Tema F):
    Ejecutar el mecanismo deliberado y auditado que habilita el uso de datos
    personales reales en el directorio. El CLI esta GATEADO POR ENTORNO: obtiene
    el artefacto de aprobacion de `DIRECTORY_ACTIVATION_APPROVAL_ARTIFACT` (o de
    `--artefacto`) y verifica que la aprobacion humana HIGH figure CONCEDIDA con
    fecha. Sin aprobacion verificable ABORTA con codigo no-cero SIN activar nada.

    NO existe un interruptor de runtime oculto: este CLI (o la funcion
    `activar_datos_reales`) es la unica via. La activacion deja constancia en la
    traza durable `directorio_auditoria` (append-only, sin PII).

Uso:
    cd App/Backend
    DIRECTORY_ACTIVATION_APPROVAL_ARTIFACT=../docs/directorio-evidencia-cumplimiento.md \
        python -m scripts.activar_directorio
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from app.services.directorio_activacion import (
    ARTEFACTO_APROBACION_ENV,
    ActivacionNoAprobadaError,
    activar_datos_reales,
    verificacion_aprobacion,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Activa de forma deliberada y auditada el tratamiento de datos "
            "reales del directorio (verificando la aprobacion humana HIGH)."
        ),
    )
    parser.add_argument(
        "--artefacto",
        default=None,
        help=(
            "Ruta al artefacto de aprobacion humana HIGH. Si se omite, se toma "
            f"de la variable de entorno {ARTEFACTO_APROBACION_ENV}."
        ),
    )
    parser.add_argument(
        "--actor-id",
        type=int,
        default=None,
        help="Identificador interno del actor que ejecuta la activacion.",
    )
    return parser


async def _run(artefacto: str, actor_id: int | None) -> None:
    """Abre una sesion sobre el engine de la aplicacion y activa datos reales."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.core.database import engine

    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            await activar_datos_reales(
                session, artefacto=artefacto, actor_id=actor_id
            )
            await session.commit()
    finally:
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada CLI. Devuelve 0 en exito, no-cero si aborta."""
    args = _build_parser().parse_args(argv)

    artefacto = args.artefacto or os.environ.get(ARTEFACTO_APROBACION_ENV)
    try:
        fecha = verificacion_aprobacion(artefacto)
    except ActivacionNoAprobadaError as exc:
        print(f"[abort] {exc}", file=sys.stderr)
        return 2

    asyncio.run(_run(artefacto, args.actor_id))
    print(
        "Activacion de datos reales del directorio completada y auditada "
        f"(aprobacion humana HIGH CONCEDIDA el {fecha})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())