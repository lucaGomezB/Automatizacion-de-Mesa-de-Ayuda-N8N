"""
Mecanismo de activacion deliberada y auditada de datos reales (c-153, Tema F, DIR-014).

Cubre el requisito DIR-014, que REEMPLAZA la compuerta historica "sin mecanismo
de activacion" (DIR-009 original) por un procedimiento explicito y auditable:

    - SIN aprobacion humana HIGH registrada no hay activacion: el mecanismo
      aborta y el directorio permanece en modo sintetico (bloqueado por defecto).
    - CON la aprobacion registrada de forma verificable, la activacion se
      ejecuta y deja constancia en la traza durable (`directorio_auditoria`),
      sin PII.
    - NO existe un interruptor de runtime oculto: la unica via es el mecanismo
      deliberado (env gateado + artefacto de aprobacion), no un flag booleano de
      `Settings` ni un endpoint.

Estrategia RED (7.3): estos tests fallan mientras no exista el modulo de
activacion ni el CLI env-gateado.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.config.settings import Settings
from app.models.directorio_auditoria import DirectorioAuditoria
from app.services.directorio_activacion import (
    ACTIVACION_OPERACION,
    ARTEFACTO_APROBACION_ENV,
    ActivacionNoAprobadaError,
    activar_datos_reales,
    verificacion_aprobacion,
)

_ARTEFACTO_CONCEDIDA = """# Evidencia de cumplimiento (sintetica)

## 4. Revision humana HIGH

La APROBACION HUMANA HIGH para tratar datos reales fue CONCEDIDA el 2026-10-28.
"""

_ARTEFACTO_PENDIENTE = """# Evidencia de cumplimiento (sintetica)

## 4. Revision humana HIGH

La APROBACION HUMANA HIGH figura PENDIENTE. Los datos reales estan BLOQUEADOS.
"""

_ARTEFACTO_SIN_SECCION = """# Otro documento

La aprobacion fue CONCEDIDA el 2026-10-28, pero no es el artefacto de evidencia.
"""


def _escribir(tmp_path, nombre: str, contenido: str):
    path = tmp_path / nombre
    path.write_text(contenido, encoding="utf-8")
    return path


async def _registros_activacion(session) -> list[DirectorioAuditoria]:
    result = await session.execute(
        select(DirectorioAuditoria).where(
            DirectorioAuditoria.operacion == ACTIVACION_OPERACION
        )
    )
    return list(result.scalars().all())


# ── Verificacion del artefacto de aprobacion ───────────────────────────────────


def test_artefacto_con_aprobacion_concedida_es_verificable(tmp_path):
    """Un artefacto que declara CONCEDIDA con fecha es verificable."""
    artefacto = _escribir(tmp_path, "concedida.md", _ARTEFACTO_CONCEDIDA)

    fecha = verificacion_aprobacion(artefacto)

    assert fecha == "2026-10-28"


def test_artefacto_pendiente_no_es_verificable(tmp_path):
    """Un artefacto que declara PENDIENTE no habilita la activacion."""
    artefacto = _escribir(tmp_path, "pendiente.md", _ARTEFACTO_PENDIENTE)

    with pytest.raises(ActivacionNoAprobadaError):
        verificacion_aprobacion(artefacto)


def test_artefacto_sin_seccion_de_revision_no_es_verificable(tmp_path):
    """Triangulacion: CONCEDIDA fuera de la seccion de revision no sirve."""
    artefacto = _escribir(tmp_path, "otro.md", _ARTEFACTO_SIN_SECCION)

    with pytest.raises(ActivacionNoAprobadaError):
        verificacion_aprobacion(artefacto)


def test_artefacto_inexistente_no_es_verificable(tmp_path):
    """Triangulacion: una ruta inexistente no es un artefacto de aprobacion."""
    with pytest.raises(ActivacionNoAprobadaError):
        verificacion_aprobacion(tmp_path / "no-existe.md")


def test_artefacto_vacio_no_es_verificable():
    """Sin artefacto (None o cadena vacia) la activacion queda bloqueada."""
    with pytest.raises(ActivacionNoAprobadaError):
        verificacion_aprobacion(None)
    with pytest.raises(ActivacionNoAprobadaError):
        verificacion_aprobacion("")


# ── Activacion: bloqueada por defecto, auditada con aprobacion ─────────────────


@pytest.mark.asyncio
async def test_sin_aprobacion_no_hay_activacion(db_session, tmp_path):
    """(DIR-014) Sin artefacto de aprobacion no se activa ni se audita el cambio."""
    artefacto = _escribir(tmp_path, "pendiente.md", _ARTEFACTO_PENDIENTE)

    with pytest.raises(ActivacionNoAprobadaError):
        await activar_datos_reales(db_session, artefacto=artefacto, actor_id=9)

    assert await _registros_activacion(db_session) == []


@pytest.mark.asyncio
async def test_sin_artefacto_no_hay_activacion(db_session):
    """(DIR-014) El estado por defecto es BLOQUEADO: sin artefacto no se activa."""
    with pytest.raises(ActivacionNoAprobadaError):
        await activar_datos_reales(db_session, artefacto=None, actor_id=9)

    assert await _registros_activacion(db_session) == []


@pytest.mark.asyncio
async def test_con_aprobacion_la_activacion_queda_auditada(db_session, tmp_path):
    """(DIR-014) Con aprobacion registrada, la activacion deja traza durable."""
    artefacto = _escribir(tmp_path, "concedida.md", _ARTEFACTO_CONCEDIDA)

    registro = await activar_datos_reales(db_session, artefacto=artefacto, actor_id=42)

    assert registro.operacion == ACTIVACION_OPERACION
    assert registro.resultado == "ok"
    assert registro.actor_empleado_id == 42
    assert registro.created_at is not None

    registros = await _registros_activacion(db_session)
    assert len(registros) == 1
    assert registros[0].id == registro.id


@pytest.mark.asyncio
async def test_la_activacion_no_registra_pii(db_session, tmp_path):
    """Triangulacion: la constancia de activacion no contiene datos personales."""
    artefacto = _escribir(tmp_path, "concedida.md", _ARTEFACTO_CONCEDIDA)

    await activar_datos_reales(db_session, artefacto=artefacto, actor_id=7)

    filas = (await db_session.execute(select(DirectorioAuditoria))).scalars().all()
    serializado = repr([(f.operacion, f.resultado, f.canal) for f in filas])
    for valor in ("@example.test", "+54911", "Nombre"):
        assert valor not in serializado
    assert all(f.canal is None for f in filas)


# ── Sin interruptor oculto: mecanismo deliberado, no flag de runtime ───────────


def test_no_existe_un_booleano_de_settings_que_active_datos_reales():
    """(DIR-014) `Settings` no expone un flag booleano que active datos reales.

    El unico camino es el mecanismo deliberado (env + artefacto). Un booleano de
    configuracion seria un interruptor de runtime oculto.
    """
    tokens = (
        "real_data",
        "datos_reales",
        "enable_real",
        "use_real",
        "activar_real",
        "habilitar_real",
    )
    booleanos = {
        nombre
        for nombre, campo in Settings.model_fields.items()
        if any(t in nombre.lower() for t in tokens)
        and campo.annotation is bool
    }
    assert booleanos == set(), f"Settings no debe exponer un flag booleano: {booleanos}"


def test_no_existe_endpoint_de_activacion():
    """(DIR-014) La activacion no se expone por HTTP: no hay interruptor remoto."""
    from app.routes.directorio import router

    rutas = [getattr(r, "path", "") for r in router.routes]
    assert not any("activ" in path.lower() for path in rutas)


def test_cli_bloqueado_por_defecto_sin_variable_de_entorno(monkeypatch, tmp_path):
    """(DIR-014) El CLI env-gateado aborta si falta la variable de entorno.

    Bloqueado por defecto: sin `DIRECTORY_ACTIVATION_APPROVAL_ARTIFACT` no hay
    activacion, ni siquiera con una ruta explicita invalida.
    """
    from scripts.activar_directorio import main

    monkeypatch.delenv(ARTEFACTO_APROBACION_ENV, raising=False)

    assert main(["--artefacto", str(tmp_path / "no-existe.md")]) == 2
    assert main([]) == 2