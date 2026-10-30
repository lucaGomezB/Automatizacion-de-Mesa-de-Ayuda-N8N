"""
Soporte compartido de los tests de c-165 (intervencion humana, ASG-005 y ECM-003).

No es un modulo de tests (no se colecta): agrupa el sembrado, la limpieza y el
cliente HTTP con cuenta real que usan los tests de validacion, rederivacion,
metrica y export. Cada test siembra lo que necesita y lo limpia al terminar
(`entorno_intervencion`), porque el motor SQLite de la suite es compartido.

Convenciones:
    - La cuenta del cliente por defecto de la suite (`client`, `User(id=1)`) NO tiene
      empleado vinculado: es el caso "actor NULL".
    - `cliente_con_cuenta(engine, user_id)` arma un cliente con la derivacion REAL de
      empleado y alcance (como `tests/test_c90_prioridad_critica_api.py`): es el caso
      "actor con empleado vinculado".
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.cost_guard.dependencies import get_cost_guard
from app.main import create_app
from app.models.asociaciones import (
    clasificacion_sector_predicho,
    clasificacion_sector_validado,
    incidente_sector_adicional,
)
from app.models.catalog import Estado, Sector
from app.models.clasificacion_log import ClasificacionLog
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.models.user import User
from app.routes.incidentes import get_alcance_incidentes
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance

SECTORES = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)


@dataclass
class Entorno:
    """Ids sembrados por `sembrar_entorno`."""

    sector: dict[str, int] = field(default_factory=dict)
    estado_nuevo_id: int = 0
    estado_cerrado_id: int = 0
    user_actor_id: int = 0
    empleado_actor_id: int = 0


def factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


async def sembrar_entorno(engine) -> Entorno:
    """Siembra catalogos, estados y una cuenta con empleado vinculado (mesa_de_ayuda)."""
    ent = Entorno()
    async with factory(engine)() as s:
        sectores = {n: Sector(nombre=n, descripcion=n) for n in SECTORES}
        nuevo = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        cerrado = Estado(nombre="cerrado", descripcion="c", es_terminal=True)
        s.add_all([*sectores.values(), nuevo, cerrado])
        await s.flush()
        # Id explicito y alto: el fixture `client` autentica `User(id=1)` SIN empleado, y
        # SQLite reutiliza ids tras borrar; un id autoincremental podria coincidir con el.
        user = User(id=9101, username="c165-actor", hashed_password="x", is_active=True)
        s.add(user)
        await s.flush()
        empleado = Empleado(
            legajo="C165-ACT",
            nombre="Actor Dos",
            email="c165.actor@example.test",
            rol=RolEmpleado.mesa_de_ayuda,
            sector_id=sectores["Sistemas"].id,
            user_id=user.id,
        )
        s.add(empleado)
        await s.commit()
        ent.sector = {n: sec.id for n, sec in sectores.items()}
        ent.estado_nuevo_id = nuevo.id
        ent.estado_cerrado_id = cerrado.id
        ent.user_actor_id = user.id
        ent.empleado_actor_id = empleado.id
    return ent


async def limpiar_entorno(engine) -> None:
    """Elimina TODO lo sembrado (orden respetando las FK) para no filtrar a otros tests."""
    async with factory(engine)() as s:
        await s.execute(delete(clasificacion_sector_predicho))
        await s.execute(delete(clasificacion_sector_validado))
        await s.execute(delete(incidente_sector_adicional))
        await s.execute(delete(ClasificacionLog))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


async def crear_log(
    engine,
    ent: Entorno,
    *,
    predicho: str | None = "Sistemas",
    requiere_revision: bool = True,
    incidente_requiere_revision: bool | None = None,
    incidente_sector: str | None = "__predicho__",
    cerrado: bool = False,
    adicionales_predichos: tuple[str, ...] = (),
    validado: str | None = None,
    adicionales_validados: tuple[str, ...] = (),
    created_at: datetime | None = None,
    **metadatos,
) -> dict[str, int]:
    """Crea un incidente con UN log de clasificacion y devuelve sus ids.

    `validado` fija `sector_id_validado` SIN metadatos (fila legada, previa a la 024)
    salvo que se pasen `metadatos` (`validado_en`, `origen_intervencion`,
    `validado_por_empleado_id`, `intervencion_inicio_en`) para sembrar un log ya
    intervenido. `incidente_sector="__predicho__"` usa el sector predicho.
    """
    sector_inc = predicho if incidente_sector == "__predicho__" else incidente_sector
    async with factory(engine)() as s:
        incidente = Incidente(
            descripcion_original="caso c165",
            descripcion_pseudonimizada="caso c165",
            estado_id=ent.estado_cerrado_id if cerrado else ent.estado_nuevo_id,
            sector_id=ent.sector[sector_inc] if sector_inc else None,
            prioridad=PrioridadEnum.media,
            requiere_revision_humana=(
                requiere_revision
                if incidente_requiere_revision is None
                else incidente_requiere_revision
            ),
        )
        s.add(incidente)
        await s.flush()
        campos = dict(
            incidente_id=incidente.id,
            sector_id_predicho=ent.sector[predicho] if predicho else None,
            confianza=0.55,
            etapa="gemini",
            requiere_revision_humana=requiere_revision,
            respuesta_raw="{}",
            sector_id_validado=ent.sector[validado] if validado else None,
            **metadatos,
        )
        if created_at is not None:
            campos["created_at"] = created_at
        log = ClasificacionLog(**campos)
        log.sectores_predichos = [
            await s.get(Sector, ent.sector[n]) for n in adicionales_predichos
        ]
        log.sectores_validados = [
            await s.get(Sector, ent.sector[n]) for n in adicionales_validados
        ]
        s.add(log)
        await s.commit()
        return {"incidente_id": incidente.id, "log_id": log.id}


async def leer_log(engine, log_id: int) -> ClasificacionLog:
    """Lee un log con sus colecciones cargadas (selectinload explicito)."""
    async with factory(engine)() as s:
        return (
            await s.scalars(
                select(ClasificacionLog)
                .where(ClasificacionLog.id == log_id)
                .options(
                    selectinload(ClasificacionLog.sectores_predichos),
                    selectinload(ClasificacionLog.sectores_validados),
                )
            )
        ).one()


async def leer_incidente(engine, incidente_id: int) -> Incidente:
    async with factory(engine)() as s:
        return await s.get(Incidente, incidente_id)


def como_utc(valor: datetime | str | None) -> datetime | None:
    """Normaliza a UTC aware un instante leido (SQLite devuelve naive: se asume UTC)."""
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


@asynccontextmanager
async def cliente_con_cuenta(engine, user_id: int, *, alcance_global: bool = False):
    """Cliente HTTP con la cuenta `user_id` y la derivacion REAL del empleado actor.

    El alcance tambien es el real, salvo `alcance_global=True` (como el fixture
    `client`): permite probar el actor de una cuenta cuyo empleado no esta activo sin
    que el alcance VACIO responda 404 antes.
    """
    app = create_app()

    async def override_db():
        async with factory(engine)() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_auth():
        return User(id=user_id, username=f"u{user_id}", hashed_password="", is_active=True)

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[get_cost_guard] = lambda: None
    if alcance_global:
        app.dependency_overrides[get_alcance_incidentes] = lambda: AlcanceIncidentes(
            ModoAlcance.GLOBAL
        )

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock), patch(
        "app.services.clasificacion_service.notify_n8n_post_revision",
        new_callable=AsyncMock,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
            await asyncio.sleep(0)


async def desactivar_empleado(engine, empleado_id: int) -> None:
    """Da de baja al empleado (activo=False): ya no se resuelve como actor."""
    async with factory(engine)() as s:
        empleado = await s.get(Empleado, empleado_id)
        empleado.activo = False
        await s.commit()
