"""IAH-009: rotacion de la clave Fernet con `MultiFernet` y re-cifrado.

Cubren el descifrado de datos cifrados con la clave anterior, que el cifrado
nuevo use la clave activa, la invalidacion del cache por conjunto de claves, el
inventario exhaustivo de columnas cifradas, el respaldo previo obligatorio del
script de rotacion, el re-cifrado transaccional con conteo, la reversion ante
un fallo a mitad y la reversibilidad de la rotacion.

Los tests usan SQLite (subconjunto offline) con datos de prueba; nunca tocan
datos reales.
"""

from types import SimpleNamespace

import pytest
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import text

import app.utils.encryption as enc
from app.models.catalog import Estado
from app.models.incidente import Incidente
from app.models.telefonia_ingreso import TelefoniaIngreso
from app.models.user import User
from app.utils.encryption import EncryptedText
from scripts.rotate_fernet_key import (
    INVENTORY,
    MIN_BACKUP_BYTES,
    MissingBackupError,
    assert_backup,
    main,
    rotate_fernet_key,
)


def configure_keys(monkeypatch, *, active: str, previous: str = "") -> None:
    """Inyecta el par de claves Fernet en el modulo de cifrado y limpia el cache."""
    settings = SimpleNamespace(
        pseudonymization_encryption_key=active,
        pseudonymization_encryption_key_previous=previous,
    )
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: settings)
    enc._fernet_instance = None
    enc._fernet_key = None


def _type() -> EncryptedText:
    return EncryptedText()


# ── MultiFernet: descifrado con la clave anterior (D-C3) ─────────────────────


def test_multi_fernet_decrypts_data_encrypted_with_previous_key(monkeypatch):
    """Un dato cifrado con la clave anterior se descifra estando en el conjunto."""
    old = Fernet.generate_key().decode()
    new = Fernet.generate_key().decode()
    configure_keys(monkeypatch, active=new, previous=old)

    ciphertext = Fernet(old).encrypt("secreto".encode()).decode()

    assert _type().process_result_value(ciphertext, None) == "secreto"


def test_encryption_uses_active_key(monkeypatch):
    """El cifrado nuevo usa la clave activa (primera); la anterior no lo abre."""
    old = Fernet.generate_key().decode()
    new = Fernet.generate_key().decode()
    configure_keys(monkeypatch, active=new, previous=old)

    ciphertext = _type().process_bind_param("secreto", None)

    assert _type().process_result_value(ciphertext, None) == "secreto"
    assert Fernet(new).decrypt(ciphertext.encode()) == b"secreto"
    with pytest.raises(InvalidToken):
        Fernet(old).decrypt(ciphertext.encode())


def test_cache_invalidated_when_previous_key_changes(monkeypatch):
    """El cache se invalida por el CONJUNTO de claves, no solo por la activa."""
    active = Fernet.generate_key().decode()
    prev_a = Fernet.generate_key().decode()
    prev_b = Fernet.generate_key().decode()

    configure_keys(monkeypatch, active=active, previous=prev_a)
    first = enc._get_fernet()

    configure_keys(monkeypatch, active=active, previous=prev_b)
    second = enc._get_fernet()

    assert first is not second


def test_no_previous_key_behaves_as_single_key(monkeypatch):
    """Sin clave anterior el comportamiento es el actual (una sola clave)."""
    active = Fernet.generate_key().decode()
    configure_keys(monkeypatch, active=active)

    ciphertext = Fernet(active).encrypt("x".encode()).decode()
    assert _type().process_result_value(ciphertext, None) == "x"


def test_unknown_key_ciphertext_is_rejected(monkeypatch):
    """Triangulacion: un ciphertext de una clave ajena al conjunto es rechazado."""
    active = Fernet.generate_key().decode()
    previous = Fernet.generate_key().decode()
    stranger = Fernet.generate_key().decode()
    configure_keys(monkeypatch, active=active, previous=previous)

    ciphertext = Fernet(stranger).encrypt("x".encode()).decode()
    with pytest.raises(InvalidToken):
        _type().process_result_value(ciphertext, None)


# ── Inventario exhaustivo (D-C5) ─────────────────────────────────────────────


def test_script_inventory_covers_all_encrypted_columns():
    """El inventario del script cubre EXACTAMENTE las columnas EncryptedText."""
    from app.core.database import Base

    found: set[tuple[str, str]] = set()
    for mapper in Base.registry.mappers:
        for attr in mapper.column_attrs:
            column = attr.columns[0]
            if isinstance(column.type, EncryptedText):
                found.add((mapper.class_.__tablename__, attr.key))

    expected = {(model.__tablename__, name) for _, model, name in INVENTORY}
    assert found == expected
    assert found == {
        ("incidente", "descripcion_original"),
        ("telefonia_ingreso", "caller_cifrado"),
        ("telefonia_ingreso", "transcript_original"),
        ("users", "totp_secret"),
    }


# ── Respaldo previo obligatorio (D-C4) ───────────────────────────────────────


async def _seed(session, *, call_sid: str = "CA-ROT-1") -> dict:
    estado = Estado(nombre="nuevo", descripcion="x", es_terminal=False)
    session.add(estado)
    await session.flush()

    incidente = Incidente(
        descripcion_original="PII uno",
        descripcion_pseudonimizada="[PII]",
        estado_id=estado.id,
    )
    ingreso = TelefoniaIngreso(
        call_sid=call_sid,
        caller_cifrado="+5491100000000",
        transcript_original="hola mundo",
    )
    user = User(
        username=f"rot_{call_sid}",
        hashed_password="x",
        is_active=True,
        totp_secret="JBSWY3DPEHPK3PXP",
    )
    session.add_all([incidente, ingreso, user])
    await session.flush()
    return {"incidente": incidente, "ingreso": ingreso, "user": user}


async def _raw(session, sql: str, params: dict):
    return (await session.execute(text(sql), params)).scalar_one()


# Marcador del encabezado de un dump en formato plano de pg_dump.
_PLAIN_DUMP_HEADER = b"-- PostgreSQL database dump\n"


def _write_valid_backup(path):
    """Crea un respaldo minimo plausible (formato plano de pg_dump)."""
    path.write_bytes(_PLAIN_DUMP_HEADER + b"-- re-cifrado de prueba\n" * 100)
    return path


async def test_rotation_requires_previous_backup(db_session, monkeypatch):
    """Sin un respaldo previo existente la rotacion aborta sin tocar datos."""
    active = Fernet.generate_key().decode()
    configure_keys(monkeypatch, active=active)
    refs = await _seed(db_session)
    before = await _raw(
        db_session,
        "SELECT descripcion_original FROM incidente WHERE id = :id",
        {"id": refs["incidente"].id},
    )

    with pytest.raises(MissingBackupError):
        await rotate_fernet_key(db_session, backup_path="/does/not/exist.dump")

    after = await _raw(
        db_session,
        "SELECT descripcion_original FROM incidente WHERE id = :id",
        {"id": refs["incidente"].id},
    )
    assert after == before


def test_backup_rejects_tiny_file(tmp_path):
    """Un archivo por debajo del tamano minimo no es un respaldo utilizable."""
    tiny = tmp_path / "tiny.dump"
    tiny.write_bytes(b"x")

    with pytest.raises(MissingBackupError):
        assert_backup(tiny)


def test_backup_rejects_content_without_marker(tmp_path):
    """Triangulacion: tamano suficiente pero sin marcador de dump es invalido."""
    junk = tmp_path / "junk.dump"
    junk.write_bytes(b"x" * (MIN_BACKUP_BYTES + 500))

    with pytest.raises(MissingBackupError):
        assert_backup(junk)


def test_backup_accepts_plain_dump_marker(tmp_path):
    """Triangulacion: un dump plano de pg_dump se acepta."""
    valid = _write_valid_backup(tmp_path / "plain.dump")

    assert assert_backup(valid) == valid


def test_backup_accepts_custom_format_marker(tmp_path):
    """Triangulacion: el formato custom de pg_dump (magic `PGDMP`) se acepta."""
    custom = tmp_path / "custom.dump"
    custom.write_bytes(b"PGDMP" + b"\x00" * (MIN_BACKUP_BYTES + 500))

    assert assert_backup(custom) == custom


def test_cli_aborts_without_existing_backup(tmp_path):
    """El CLI devuelve codigo no-cero si el respaldo no existe, no se declara o
    no es un dump utilizable."""
    assert main(["--backup-path", "/does/not/exist.dump"]) == 2

    tiny = tmp_path / "tiny.dump"
    tiny.write_bytes(b"x")
    assert main(["--backup-path", str(tiny)]) == 2

    with pytest.raises(SystemExit):
        main([])


# ── Re-cifrado transaccional, conteo y reversibilidad ────────────────────────


async def test_rotation_reencrypts_inventory_and_reports_counts(
    db_session, monkeypatch, tmp_path
):
    """Re-cifra las columnas del inventario con la clave nueva y reporta conteos."""
    old = Fernet.generate_key().decode()
    new = Fernet.generate_key().decode()
    configure_keys(monkeypatch, active=old)
    refs = await _seed(db_session)
    before = await _raw(
        db_session,
        "SELECT descripcion_original FROM incidente WHERE id = :id",
        {"id": refs["incidente"].id},
    )

    backup = tmp_path / "backup.dump"
    _write_valid_backup(backup)

    configure_keys(monkeypatch, active=new, previous=old)
    report = await rotate_fernet_key(db_session, backup_path=backup)

    after = await _raw(
        db_session,
        "SELECT descripcion_original FROM incidente WHERE id = :id",
        {"id": refs["incidente"].id},
    )
    assert after != before
    assert Fernet(new).decrypt(after.encode()).decode() == "PII uno"

    assert report.counts["incidente.descripcion_original"] == 1
    assert report.counts["telefonia_ingreso.caller_cifrado"] == 1
    assert report.counts["telefonia_ingreso.transcript_original"] == 1
    assert report.counts["users.totp_secret"] == 1
    assert report.total == 4


async def test_rotation_reverts_on_mid_failure(
    engine, db_session, monkeypatch, tmp_path
):
    """Un fallo a mitad revierte todo: no queda estado parcial."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    old = Fernet.generate_key().decode()
    new = Fernet.generate_key().decode()

    # Datos COMMITEADOS (como en una corrida real): la rotacion revierte solo su
    # propia transaccion, no los datos preexistentes.
    configure_keys(monkeypatch, active=old)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as seed:
        estado = Estado(nombre="nuevo", descripcion="x", es_terminal=False)
        seed.add(estado)
        await seed.flush()
        incidente = Incidente(
            descripcion_original="PII uno",
            descripcion_pseudonimizada="[PII]",
            estado_id=estado.id,
        )
        seed.add(incidente)
        await seed.commit()
        incidente_id = incidente.id
        estado_id = estado.id

    try:
        before = await _raw(
            db_session,
            "SELECT descripcion_original FROM incidente WHERE id = :id",
            {"id": incidente_id},
        )

        backup = tmp_path / "backup2.dump"
        _write_valid_backup(backup)
        configure_keys(monkeypatch, active=new, previous=old)

        import scripts.rotate_fernet_key as script

        real = script._reencrypt_column
        calls = {"n": 0}

        async def failing(session, model, attr):
            calls["n"] += 1
            if calls["n"] == 2:
                raise RuntimeError("fallo simulado")
            return await real(session, model, attr)

        monkeypatch.setattr(script, "_reencrypt_column", failing)

        with pytest.raises(RuntimeError):
            await rotate_fernet_key(db_session, backup_path=backup)

        after = await _raw(
            db_session,
            "SELECT descripcion_original FROM incidente WHERE id = :id",
            {"id": incidente_id},
        )
        assert after == before
    finally:
        async with factory() as cleanup:
            await cleanup.execute(
                text("DELETE FROM incidente WHERE id = :id"), {"id": incidente_id}
            )
            await cleanup.execute(
                text("DELETE FROM estado WHERE id = :id"), {"id": estado_id}
            )
            await cleanup.commit()


async def test_rotation_is_reversible(db_session, monkeypatch, tmp_path):
    """Reponer la clave anterior como activa vuelve a dejar los datos legibles."""
    old = Fernet.generate_key().decode()
    new = Fernet.generate_key().decode()
    configure_keys(monkeypatch, active=old)
    refs = await _seed(db_session, call_sid="CA-ROT-3")

    backup = tmp_path / "backup3.dump"
    _write_valid_backup(backup)

    # Rotacion hacia la clave nueva.
    configure_keys(monkeypatch, active=new, previous=old)
    await rotate_fernet_key(db_session, backup_path=backup)
    raw_new = await _raw(
        db_session,
        "SELECT descripcion_original FROM incidente WHERE id = :id",
        {"id": refs["incidente"].id},
    )
    assert Fernet(new).decrypt(raw_new.encode()).decode() == "PII uno"

    # Reversion: la clave anterior vuelve a ser la activa.
    configure_keys(monkeypatch, active=old, previous=new)
    await rotate_fernet_key(db_session, backup_path=backup)

    raw_old = await _raw(
        db_session,
        "SELECT descripcion_original FROM incidente WHERE id = :id",
        {"id": refs["incidente"].id},
    )
    assert Fernet(old).decrypt(raw_old.encode()).decode() == "PII uno"
