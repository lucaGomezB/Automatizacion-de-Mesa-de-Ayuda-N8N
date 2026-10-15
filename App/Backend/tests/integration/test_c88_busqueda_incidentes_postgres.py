"""Integracion PostgreSQL de la busqueda por texto libre (c-88, IS-001/IS-002).

Requiere un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Verifica en el motor real que el ILIKE parcial case-insensitive con escape de
comodines y la coincidencia OR por `id` numerico devuelven el conjunto correcto.
"""

import pytest

from app.models.incidente import Incidente, PrioridadEnum
from app.repositories.incidente_repository import IncidenteRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_busqueda_texto_libre_postgres(pg_session, seed_pg_catalogs):
    """Replica la busqueda (parcial, id numerico y comodines) en PostgreSQL."""
    cat = seed_pg_catalogs
    estado = cat["estado_nuevo"]
    base = dict(
        descripcion_original="original",
        prioridad=PrioridadEnum.media,
        estado_id=estado.id,
    )
    a = Incidente(
        id=4242,
        descripcion_pseudonimizada="El servidor de correo no responde",
        origen_message_id="c88-pg-a",
        **base,
    )
    b = Incidente(
        descripcion_pseudonimizada="Impresora sin toner",
        origen_message_id="c88-pg-b",
        **base,
    )
    c = Incidente(
        descripcion_pseudonimizada="Progreso 100% completado",
        origen_message_id="c88-pg-c",
        **base,
    )
    d = Incidente(
        descripcion_pseudonimizada="Progreso 1000 completado",
        origen_message_id="c88-pg-d",
        **base,
    )
    pg_session.add_all([a, b, c, d])
    await pg_session.flush()

    repo = IncidenteRepository(pg_session)

    # Busqueda parcial case-insensitive.
    por_texto = {i.id for i in await repo.list_filtered(q="CORREO", limit=100)}
    assert por_texto == {a.id}

    # Termino numerico: coincide por id (OR) aunque la descripcion no lo contenga.
    por_id = {i.id for i in await repo.list_filtered(q="4242", limit=100)}
    assert por_id == {a.id}

    # Comodin `%` tratado como literal: no matchea "1000".
    por_pct = {i.id for i in await repo.list_filtered(q="100%", limit=100)}
    assert por_pct == {c.id}

    # Termino corto se ignora: devuelve todas las filas.
    sin_filtro = {i.id for i in await repo.list_filtered(q="a", limit=100)}
    assert sin_filtro == {a.id, b.id, c.id, d.id}

    await pg_session.rollback()
