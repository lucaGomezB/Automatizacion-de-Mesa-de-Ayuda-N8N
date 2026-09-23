"""
Seed dev-only del directorio de empleados (c-54, OQ1 / D9).

Responsabilidad:
    Sembrar UN usuario sintetico por rol con datos de contacto utiles, creando
    AMBAS filas: la cuenta de autenticacion (`users`, login) y la fila del
    directorio (`directorio_empleado`), enlazadas por `user_id`. Esto resuelve el
    bootstrap del primer administrador (sin huevo-y-gallina).

Idempotencia:
    La clave de idempotencia es el `legajo`. Si ya existe, no se recrea ni se
    duplica la cuenta. Reejecutar el seed deja el mismo estado.

NO PII REAL:
    Todos los datos son sinteticos y usan el dominio reservado `.test`. Las
    contrasenas son de desarrollo y deben cambiarse antes de cualquier uso real.

Uso:
    cd App/Backend
    python scripts/seed_directorio.py
"""

import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.empleado import RolEmpleado
from app.repositories.user_repository import UserRepository
from app.services.auth_service import get_password_hash
from app.services.directorio_service import DirectorioService

logger = get_logger(__name__)

# Un usuario sintetico por rol. `sector` es obligatorio para usuario_final y
# operador; el administrador no tiene sector. Sin PII real (dominio .test).
PERSONAS_SINTETICAS: list[dict[str, Any]] = [
    {
        "username": "directorio.admin",
        "password": "cambiar-esta-clave-admin",  # gitleaks:allow (password de desarrollo, usuario sintetico)
        "legajo": "DIR-ADMIN",
        "nombre": "Administrador Directorio (sintetico)",
        "email": "directorio.admin@example.test",
        "telefono": "+5491100000001",
        "rol": RolEmpleado.administrador_directorio.value,
        "sector": None,
    },
    {
        "username": "directorio.operador",
        "password": "cambiar-esta-clave-operador",  # gitleaks:allow (password de desarrollo, usuario sintetico)
        "legajo": "DIR-OPERADOR",
        "nombre": "Operador Sistemas (sintetico)",
        "email": "directorio.operador@example.test",
        "telefono": "+5491100000002",
        "rol": RolEmpleado.operador.value,
        "sector": "Sistemas",
    },
    {
        "username": "directorio.usuario",
        "password": "cambiar-esta-clave-usuario",  # gitleaks:allow (password de desarrollo, usuario sintetico)
        "legajo": "DIR-USUARIO",
        "nombre": "Usuario Final (sintetico)",
        "email": "directorio.usuario@example.test",
        "telefono": "+5491100000003",
        "rol": RolEmpleado.usuario_final.value,
        "sector": "Sistemas",
    },
]


async def seed_directorio(
    session: AsyncSession, *, commit: bool = False, actor_id: int | None = None
) -> dict[str, int]:
    """
    Siembra (idempotentemente) un usuario sintetico por rol.

    Args:
        session:  sesion async de SQLAlchemy.
        commit:   si True, confirma la transaccion (uso del script CLI).
        actor_id: actor de auditoria (opcional).

    Returns:
        Conteo de empleados creados y omitidos por ya existir.
    """
    from app.repositories.empleado_repository import EmpleadoRepository

    creados = 0
    existentes = 0

    for persona in PERSONAS_SINTETICAS:
        empleado_repo = EmpleadoRepository(session)
        if await empleado_repo.get_by_legajo(persona["legajo"]) is not None:
            existentes += 1
            continue

        user = await UserRepository(session).get_by_username(persona["username"])
        if user is None:
            from app.models.user import User

            user = User(
                username=persona["username"],
                hashed_password=get_password_hash(persona["password"]),
                is_active=True,
            )
            session.add(user)
            await session.flush()

        sector_id = None
        if persona["sector"] is not None:
            from app.repositories.sector_repository import SectorRepository

            sector = await SectorRepository(session).get_by_nombre(persona["sector"])
            if sector is None:
                raise RuntimeError(
                    f"Sector canonico '{persona['sector']}' no encontrado. "
                    "Ejecutar las migraciones (seed de catalogos) antes del seed."
                )
            sector_id = sector.id

        await DirectorioService(session, actor_id=actor_id).crear_empleado(
            legajo=persona["legajo"],
            nombre=persona["nombre"],
            email=persona["email"],
            telefono=persona["telefono"],
            sector_id=sector_id,
            rol=persona["rol"],
            user_id=user.id,
            actor_id=actor_id,
        )
        creados += 1

    if commit:
        await session.commit()

    logger.info("seed_directorio", creados=creados, existentes=existentes)
    return {"creados": creados, "existentes": existentes}


async def _main() -> None:
    """Punto de entrada CLI: abre una sesion y ejecuta el seed con commit."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.core.database import engine

    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            resultado = await seed_directorio(session, commit=True)
        print(
            f"Seed del directorio completado: {resultado['creados']} creados, "
            f"{resultado['existentes']} ya existentes."
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_main())
