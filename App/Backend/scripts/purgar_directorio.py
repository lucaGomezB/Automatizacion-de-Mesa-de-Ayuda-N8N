"""
Purga por retencion del directorio de empleados (c-54, W2 / DIR-007).

Responsabilidad:
    Ejecutar el borrado FISICO de las filas del directorio que superaron la
    retencion "relacion laboral activa + 1 año", es decir, las bajas con
    `activo=false` cuya `fecha_baja + 1 año` ya vencio. Las filas activas y las
    bajas recientes se conservan.

    La purga es IDEMPOTENTE: reejecutarla no vuelve a borrar nada. Registra un
    evento de auditoria con el conteo y SIN datos personales.

Decisiones:
    - El borrado por retencion NO es el camino operativo por defecto (ese es la
      desactivacion); se ejecuta de forma programada/operativa desde este script.
    - El borrado ARCO sigue siendo una accion explicita de `administrador_directorio`
      via la API; este script solo atiende el vencimiento del plazo.

Uso:
    cd App/Backend
    python -m scripts.purgar_directorio
"""

import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.services.directorio_service import DirectorioService

logger = get_logger(__name__)


async def purgar_directorio(
    session: AsyncSession,
    *,
    commit: bool = False,
    ahora: datetime | None = None,
    actor_id: int | None = None,
) -> int:
    """
    Purgar las filas vencidas del directorio.

    Args:
        session:  sesion async de SQLAlchemy.
        commit:   si True, confirma la transaccion (uso del script CLI).
        ahora:    instante de referencia (inyectable para tests).
        actor_id: actor de auditoria (opcional).

    Returns:
        Cantidad de filas eliminadas fisicamente.
    """
    purgados = await DirectorioService(session, actor_id=actor_id).purgar_vencidos(
        ahora=ahora, actor_id=actor_id
    )
    if commit:
        await session.commit()
    return purgados


async def _main() -> None:
    """Punto de entrada CLI: abre una sesion y ejecuta la purga con commit."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.core.database import engine

    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            purgados = await purgar_directorio(session, commit=True)
        print(f"Purga por retencion del directorio completada: {purgados} filas.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_main())
