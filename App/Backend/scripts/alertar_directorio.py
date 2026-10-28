"""
Alerta de acumulacion por retencion del directorio de empleados (c-153 / DIR-015).

Responsabilidad:
    Reportar el CONTEO de filas desactivadas que superaron "relacion laboral
    activa + 1 año" y aun no fueron purgadas, para que un `administrador_directorio`
    dispare la purga MANUAL (`scripts/purgar_directorio.py`). La alerta NO expone
    datos personales ni el detalle de las filas: solo el conteo agregado.

Decisiones:
    - NO hay cron/scheduler/worker: la alerta se invoca de forma explicita y
      operativa desde este script (ver `docs/seguridad/runbook-retencion-directorio.md`).
    - No modifica datos: es de solo lectura (conteo). La purga sigue siendo una
      accion humana separada.

Uso:
    cd App/Backend
    python -m scripts.alertar_directorio
"""

import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.directorio_service import DirectorioService


async def alertar_directorio(
    session: AsyncSession,
    *,
    ahora: datetime | None = None,
) -> int:
    """
    Devuelve el conteo de bajas vencidas sin purgar y emite la alerta sin PII.

    Args:
        session: sesion async de SQLAlchemy (solo lectura).
        ahora:   instante de referencia (inyectable para tests).

    Returns:
        Cantidad de filas vencidas sin purgar (0 si no hay acumulacion).
    """
    return await DirectorioService(session).alertar_acumulacion_vencidos(ahora=ahora)


async def _main() -> None:
    """Punto de entrada CLI: abre una sesion y reporta la acumulacion."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.core.database import engine

    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            conteo = await alertar_directorio(session)
        print(
            "Alerta de retencion del directorio: "
            f"{conteo} filas vencidas sin purgar. "
            "Disparar la purga manual si corresponde."
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_main())
