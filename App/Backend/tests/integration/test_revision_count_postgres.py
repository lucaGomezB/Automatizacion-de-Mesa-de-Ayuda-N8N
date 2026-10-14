"""
Integracion PostgreSQL del conteo de la cola de revision pendiente (c-85, VIS-006).

Objetivo: verificar contra PostgreSQL real que el total del conteo coincide con
la cantidad de elementos del listado equivalente SIN paginar, para el mismo
alcance. Es el escenario "El conteo coincide con el listado completo" de VIS-006,
ejercitado sobre el motor de produccion (asyncpg) y no sobre SQLite.

Requiere un PostgreSQL alcanzable (fixtures pg_*). Si no lo esta, la suite de
integracion falla ruidosamente (nunca skip silencioso), segun la politica del
proyecto.
"""

import pytest

from app.models.clasificacion_log import ClasificacionLog
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.models.user import User
from app.repositories.clasificacion_repository import ClasificacionRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_count_revision_pendiente_coincide_con_listado_postgres(
    pg_session, seed_pg_catalogs
):
    """El conteo == len(listado sin paginar) para alcance global y propio."""
    cat = seed_pg_catalogs

    user = User(username="c85-count-integ", hashed_password="x", is_active=True)
    pg_session.add(user)
    await pg_session.flush()

    empleado = Empleado(
        legajo="C85-COUNT",
        nombre="Reportante Integ",
        email="c85.count@example.test",
        rol=RolEmpleado.usuario_final,
        user_id=user.id,
        sector_id=cat["sector_sistemas"].id,
    )
    pg_session.add(empleado)
    await pg_session.flush()

    def _incidente() -> Incidente:
        return Incidente(
            descripcion_original="caso integracion conteo",
            descripcion_pseudonimizada="caso integracion conteo",
            prioridad=PrioridadEnum.media,
            estado_id=cat["estado_nuevo"].id,
            sector_id=cat["sector_sistemas"].id,
            reportante_empleado_id=empleado.id,
            requiere_revision_humana=True,
        )

    inc_pend1, inc_pend2, inc_validado = _incidente(), _incidente(), _incidente()
    pg_session.add_all([inc_pend1, inc_pend2, inc_validado])
    await pg_session.flush()

    # Dos pendientes reales (cuentan) y uno ya validado (no cuenta).
    log_pend1 = ClasificacionLog(
        incidente_id=inc_pend1.id, sector_id_predicho=cat["sector_sistemas"].id,
        confianza=0.55, etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
    )
    log_pend2 = ClasificacionLog(
        incidente_id=inc_pend2.id, sector_id_predicho=cat["sector_sistemas"].id,
        confianza=0.55, etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
    )
    log_validado = ClasificacionLog(
        incidente_id=inc_validado.id, sector_id_predicho=cat["sector_sistemas"].id,
        confianza=0.55, etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
        sector_id_validado=cat["sector_sistemas"].id,
    )
    pg_session.add_all([log_pend1, log_pend2, log_validado])
    await pg_session.flush()

    repo = ClasificacionRepository(pg_session)

    for reportante in (None, empleado.id):
        total = await repo.count_pending_review(reportante_empleado_id=reportante)
        listado = await repo.list_pending_review(
            limit=500, offset=0, reportante_empleado_id=reportante
        )
        assert total == len(listado) == 2
