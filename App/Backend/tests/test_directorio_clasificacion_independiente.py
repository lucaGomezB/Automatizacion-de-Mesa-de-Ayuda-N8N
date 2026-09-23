"""
Test de DIR-003: el rol del directorio no afecta la clasificacion (c-54, N2).

Caracterizacion del invariante: el clasificador determinista produce el mismo
sector y confianza para un texto fijo, con independencia de los roles presentes
en el directorio; ademas, el modulo del clasificador no referencia el vocabulario
de roles ni el directorio.
"""

import inspect

import pytest

from app.classifiers import deterministic
from app.classifiers.deterministic import DeterministicClassifier
from app.models.catalog import Sector
from app.services.directorio_service import DirectorioService

_TEXTO = "El backup de la base de datos falló durante la replicación."


@pytest.mark.asyncio
async def test_rol_no_afecta_la_clasificacion(db_session):
    """Clasificar un texto fijo no cambia al existir empleados de otros roles."""
    classifier = DeterministicClassifier()
    base = await classifier.classify(_TEXTO)
    assert base.sector_predicho == "Bases de Datos"

    sector = Sector(nombre="Bases de Datos", descripcion="d")
    db_session.add(sector)
    await db_session.flush()
    svc = DirectorioService(db_session)
    await svc.crear_empleado(
        legajo="CL-1", nombre="N", email="cl1@example.test",
        sector_id=sector.id, rol="usuario_final",
    )
    await svc.crear_empleado(
        legajo="CL-2", nombre="N", email="cl2@example.test",
        sector_id=sector.id, rol="operador",
    )
    await svc.crear_empleado(
        legajo="CL-3", nombre="N", email="cl3@example.test",
        rol="administrador_directorio",
    )

    luego = await classifier.classify(_TEXTO)

    assert luego.sector_predicho == base.sector_predicho
    assert luego.confianza == base.confianza


def test_clasificador_no_referencia_el_rol_del_directorio():
    """Regresion estructural: el clasificador no conoce el vocabulario de roles."""
    fuente = inspect.getsource(deterministic)
    assert "RolEmpleado" not in fuente
    assert "directorio_empleado" not in fuente
