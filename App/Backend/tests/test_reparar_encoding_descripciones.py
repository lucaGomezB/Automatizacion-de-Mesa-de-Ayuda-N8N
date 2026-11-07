"""Tests del script de reparacion del mojibake (c-181).

Cubren, en tres bloques, la logica del script
`scripts/reparar_encoding_descripciones.py`:

  1. deteccion/reverso PUROS (`revertir_mojibake`, `es_mojibake`), sin base ni
     red;
  2. el nucleo de reparacion `reparar_descripciones(session, apply=...)` sobre
     SQLite in-memory (dry-run, apply de ambas columnas, idempotencia y error por
     token no descifrable);
  3. el CLI (dry-run por defecto, `--apply` con advertencia y base objetivo).

Todos los tests corren en el subconjunto offline (sin PostgreSQL ni servicios).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
import pytest_asyncio
from cryptography.fernet import Fernet
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.utils.encryption as enc
from app.core.database import Base
from app.models import *  # noqa: F401,F403  (registra todas las tablas)
from app.models.catalog import Estado
from app.models.incidente import Incidente
from scripts.reparar_encoding_descripciones import (
    es_mojibake,
    main,
    reparar_descripciones,
    revertir_mojibake,
)


# Texto limpio y su mojibake de doble codificacion (UTF-8 leido como latin-1).
TEXTO_LIMPIO = "Reunión de equipo de soporte"
TEXTO_CORRUPTO = "ReuniÃ³n de equipo de soporte"
OTRO_CORRUPTO = "SeÃ±al de red perdida"
OTRO_LIMPIO = "Señal de red perdida"
LIMPIO_SIN_ACENTOS = "La impresora no imprime y sale papel atascado"


# ---------------------------------------------------------------------------
# Grupo 1 — Logica pura de deteccion y reverso
# ---------------------------------------------------------------------------


def test_revertir_mojibake_devuelve_el_texto_limpio():
    """El reverso de doble codificacion devuelve el texto original."""
    assert revertir_mojibake(TEXTO_CORRUPTO) == TEXTO_LIMPIO
    assert revertir_mojibake(OTRO_CORRUPTO) == OTRO_LIMPIO


def test_es_mojibake_detecta_el_texto_corrupto():
    """Un texto con la firma del mojibake se detecta positivo."""
    assert es_mojibake(TEXTO_CORRUPTO) is True
    assert es_mojibake(OTRO_CORRUPTO) is True


def test_es_mojibake_no_detecta_texto_limpio():
    """Un texto limpio no se detecta como corrupto."""
    assert es_mojibake(TEXTO_LIMPIO) is False
    assert es_mojibake(LIMPIO_SIN_ACENTOS) is False
    assert es_mojibake("café") is False


def test_es_mojibake_maneja_texto_no_reversible_sin_excepcion():
    """Texto no latin-1 (emoji) o de reverso no-utf8 no rompe la deteccion."""
    assert es_mojibake("Sin conexión 😀") is False
    assert revertir_mojibake("Sin conexión 😀") is None
    # Firma presente pero el reverso no es utf-8 valido (secuencia truncada).
    assert es_mojibake("\u00e2\u0080") is False
    assert revertir_mojibake("\u00e2\u0080") is None


def test_detector_es_idempotente():
    """Un texto ya reparado no vuelve a detectarse."""
    reparado = revertir_mojibake(TEXTO_CORRUPTO)
    assert reparado == TEXTO_LIMPIO
    assert es_mojibake(reparado) is False


# ---------------------------------------------------------------------------
# Infraestructura de los tests de reparacion (SQLite in-memory)
# ---------------------------------------------------------------------------

# Clave Fernet de prueba (no contiene datos reales); se inyecta por test para no
# depender del `.env` y poder descifrar `descripcion_original` en los asserts.
_TEST_FERNET_KEY = Fernet.generate_key().decode()


@pytest.fixture(autouse=True)
def _fernet_test_key(monkeypatch):
    """Inyecta una clave Fernet de prueba y limpia el cache lazy del modulo."""
    settings = SimpleNamespace(
        pseudonymization_encryption_key=_TEST_FERNET_KEY,
        pseudonymization_encryption_key_previous="",
    )
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: settings)
    enc._fernet_instance = None
    enc._fernet_key = None
    yield
    enc._fernet_instance = None
    enc._fernet_key = None


@pytest_asyncio.fixture
async def script_engine():
    """Motor SQLite in-memory aislado con el esquema completo creado."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def script_session(script_engine):
    """Sesion async sobre el motor aislado (sin rollback: los tests commitean)."""
    factory = async_sessionmaker(script_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


async def _seed_estado(session) -> int:
    estado = Estado(nombre="nuevo", descripcion="x", es_terminal=False)
    session.add(estado)
    await session.flush()
    return estado.id


async def _seed_incidente(session, estado_id, *, pseudonimizada, original) -> int:
    incidente = Incidente(
        descripcion_original=original,
        descripcion_pseudonimizada=pseudonimizada,
        estado_id=estado_id,
    )
    session.add(incidente)
    await session.flush()
    return incidente.id


async def _pseudo(session, incidente_id) -> str:
    return (
        await session.execute(
            text(
                "SELECT descripcion_pseudonimizada FROM incidente WHERE id = :id"
            ),
            {"id": incidente_id},
        )
    ).scalar_one()


async def _ciphertext(session, incidente_id) -> str:
    return (
        await session.execute(
            text("SELECT descripcion_original FROM incidente WHERE id = :id"),
            {"id": incidente_id},
        )
    ).scalar_one()


# ---------------------------------------------------------------------------
# Grupo 2 — Nucleo de reparacion sobre sesion
# ---------------------------------------------------------------------------


async def test_dry_run_no_modifica_y_reporta_conteos(script_session):
    """En dry-run ninguna fila cambia y el resumen reporta candidatos/omitidos."""
    estado_id = await _seed_estado(script_session)
    candidato_id = await _seed_incidente(
        script_session,
        estado_id,
        pseudonimizada=TEXTO_CORRUPTO,
        original=TEXTO_CORRUPTO,
    )
    await _seed_incidente(
        script_session,
        estado_id,
        pseudonimizada=LIMPIO_SIN_ACENTOS,
        original=LIMPIO_SIN_ACENTOS,
    )
    await script_session.commit()

    reporte = await reparar_descripciones(script_session, apply=False)

    assert reporte.candidatos == 1
    assert reporte.reparados == 0
    assert reporte.omitidos == 1
    assert reporte.errores == 0
    assert await _pseudo(script_session, candidato_id) == TEXTO_CORRUPTO


async def test_apply_repara_ambas_columnas(script_session):
    """Con apply, la pseudonimizada queda limpia y la original descifra limpia."""
    estado_id = await _seed_estado(script_session)
    incidente_id = await _seed_incidente(
        script_session,
        estado_id,
        pseudonimizada=TEXTO_CORRUPTO,
        original=OTRO_CORRUPTO,
    )
    await script_session.commit()

    reporte = await reparar_descripciones(script_session, apply=True)

    assert reporte.candidatos == 1
    assert reporte.reparados == 1
    assert reporte.errores == 0
    assert await _pseudo(script_session, incidente_id) == TEXTO_LIMPIO
    assert enc.decrypt_value(await _ciphertext(script_session, incidente_id)) == (
        OTRO_LIMPIO
    )


async def test_fila_limpia_intacta_incluido_su_ciphertext(script_session):
    """Una fila limpia no se modifica: ni su descripcion ni su ciphertext."""
    estado_id = await _seed_estado(script_session)
    limpio_id = await _seed_incidente(
        script_session,
        estado_id,
        pseudonimizada=LIMPIO_SIN_ACENTOS,
        original=LIMPIO_SIN_ACENTOS,
    )
    await script_session.commit()
    cipher_antes = await _ciphertext(script_session, limpio_id)

    reporte = await reparar_descripciones(script_session, apply=True)

    assert reporte.omitidos == 1
    assert reporte.reparados == 0
    assert await _pseudo(script_session, limpio_id) == LIMPIO_SIN_ACENTOS
    assert await _ciphertext(script_session, limpio_id) == cipher_antes
    assert enc.decrypt_value(cipher_antes) == LIMPIO_SIN_ACENTOS


async def test_segunda_corrida_no_repara_nada(script_session):
    """La reparacion es idempotente: la segunda corrida reporta cero reparados."""
    estado_id = await _seed_estado(script_session)
    incidente_id = await _seed_incidente(
        script_session,
        estado_id,
        pseudonimizada=TEXTO_CORRUPTO,
        original=TEXTO_CORRUPTO,
    )
    await script_session.commit()

    primera = await reparar_descripciones(script_session, apply=True)
    assert primera.reparados == 1
    cipher_tras_primera = await _ciphertext(script_session, incidente_id)

    segunda = await reparar_descripciones(script_session, apply=True)

    assert segunda.candidatos == 0
    assert segunda.reparados == 0
    assert await _ciphertext(script_session, incidente_id) == cipher_tras_primera


async def test_fila_con_token_no_descifrable_no_bloquea_ni_deja_parciales(
    script_session,
):
    """Una fila con token invalido se reporta como error sin bloquear al resto."""
    estado_id = await _seed_estado(script_session)
    await script_session.commit()

    # Fila con un ciphertext NO valido insertada por SQL crudo (evita el
    # TypeDecorator, que cifraria cualquier valor). Queda ANTES de la buena.
    await script_session.execute(
        text(
            "INSERT INTO incidente "
            "(descripcion_original, descripcion_pseudonimizada, prioridad, "
            " estado_id, requiere_revision_humana, created_at, updated_at) "
            "VALUES (:orig, :pseudo, 'media', :estado, 0, :now, :now)"
        ),
        {
            "orig": "no-es-un-token-fernet",
            "pseudo": OTRO_CORRUPTO,
            "estado": estado_id,
            "now": datetime.now(timezone.utc),
        },
    )
    await script_session.commit()
    mala_id = (
        await script_session.execute(
            text(
                "SELECT id FROM incidente "
                "WHERE descripcion_pseudonimizada = :p"
            ),
            {"p": OTRO_CORRUPTO},
        )
    ).scalar_one()

    buena_id = await _seed_incidente(
        script_session,
        estado_id,
        pseudonimizada=TEXTO_CORRUPTO,
        original=TEXTO_CORRUPTO,
    )
    await script_session.commit()

    reporte = await reparar_descripciones(script_session, apply=True)

    assert reporte.candidatos == 2
    assert reporte.reparados == 1
    assert reporte.errores == 1
    assert reporte.omitidos == 0
    assert any(str(mala_id) in detalle for detalle in reporte.detalles_error)
    # La fila fallida NO escribio su pseudonimizada.
    assert await _pseudo(script_session, mala_id) == OTRO_CORRUPTO
    # La fila buena SI se reparo pese al fallo previo.
    assert await _pseudo(script_session, buena_id) == TEXTO_LIMPIO


# ---------------------------------------------------------------------------
# Grupo 3 — CLI delgado (dry-run por defecto; --apply con advertencia)
# ---------------------------------------------------------------------------


async def _seed_file_db(url: str) -> int:
    """Crea el esquema en la base de archivo y siembra un incidente corrupto."""
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            estado = Estado(nombre="nuevo", descripcion="x", es_terminal=False)
            session.add(estado)
            await session.flush()
            incidente = Incidente(
                descripcion_original=TEXTO_CORRUPTO,
                descripcion_pseudonimizada=TEXTO_CORRUPTO,
                estado_id=estado.id,
            )
            session.add(incidente)
            await session.commit()
            return incidente.id
    finally:
        await engine.dispose()


async def _leer_pseudo_file_db(url: str, incidente_id: int) -> str:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            return (
                await conn.execute(
                    text(
                        "SELECT descripcion_pseudonimizada FROM incidente "
                        "WHERE id = :id"
                    ),
                    {"id": incidente_id},
                )
            ).scalar_one()
    finally:
        await engine.dispose()


def test_cli_sin_apply_no_escribe(tmp_path):
    """El flujo CLI sin --apply no modifica ningun dato."""
    db_path = tmp_path / "cli_dryrun.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    incidente_id = asyncio.run(_seed_file_db(url))

    rc = main(["--database-url", url])

    assert rc == 0
    assert asyncio.run(_leer_pseudo_file_db(url, incidente_id)) == TEXTO_CORRUPTO


def test_cli_apply_advertencia_y_nombre_base(tmp_path, capsys):
    """--apply advierte del respaldo, nombra la base objetivo y repara."""
    db_path = tmp_path / "cli_apply.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    incidente_id = asyncio.run(_seed_file_db(url))

    rc = main(["--database-url", url, "--apply"])

    assert rc == 0
    salida = capsys.readouterr()
    texto = salida.out + salida.err
    assert db_path.name in texto
    assert "pg_dump" in texto
    assert asyncio.run(_leer_pseudo_file_db(url, incidente_id)) == TEXTO_LIMPIO
