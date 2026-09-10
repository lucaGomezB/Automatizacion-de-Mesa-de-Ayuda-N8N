"""
Tests de la migración Alembic 002 (doble representación).

Sección 10 del plan TDD de c-03-pseudonymization-module.

Verifica que:
- Después de upgrade head la tabla incidente tiene descripcion_original
  y descripcion_pseudonimizada y NO tiene descripcion.
- Round-trip: una fila preexistente con descripcion queda backfilleada
  correctamente (pseudonimizada enmascarada, original cifrada y descifrable).
- Downgrade revierte el esquema a la columna descripcion.

Estrategia:
    SQLite en archivo temporal (no in-memory) para que Alembic pueda
    gestionar el historial de revisiones sobre una conexión real.
    La clave Fernet de prueba se inyecta vía variable de entorno.
"""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

# Clave Fernet de prueba (misma en toda la suite)
_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

# Ruta de la raíz del backend (donde vive alembic.ini)
_BACKEND_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """
    Base de datos SQLite en archivo temporal + variables de entorno
    inyectadas para que alembic/env.py y EncryptedText funcionen
    sin la .env real del proyecto.
    """
    db_path = tmp_path / "test_migration.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("PSEUDONYMIZATION_ENCRYPTION_KEY", _TEST_FERNET_KEY)
    monkeypatch.setenv("PSEUDONYMIZATION_INTERNAL_DOMAINS", "[]")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "")

    # Invalidar el cache de settings para que lea las vars de entorno nuevas
    from app.config.settings import get_settings
    get_settings.cache_clear()

    # También resetear la instancia Fernet
    import app.utils.encryption as enc_module
    enc_module._fernet_instance = None

    yield db_path

    enc_module._fernet_instance = None
    get_settings.cache_clear()


def _run_alembic(command: list[str], db_path: Path) -> None:
    """
    Ejecuta un comando de Alembic programáticamente sobre la DB de prueba.
    Usa alembic.config.main() para no depender del shell.
    """
    from alembic.config import Config
    from alembic import command as alembic_cmd

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    cfg.set_main_option(
        "sqlalchemy.url", f"sqlite:///{db_path}"
    )
    # Silenciar el output de logging de Alembic durante los tests
    import logging
    logging.getLogger("alembic").setLevel(logging.WARNING)

    if command[0] == "upgrade":
        alembic_cmd.upgrade(cfg, command[1])
    elif command[0] == "downgrade":
        alembic_cmd.downgrade(cfg, command[1])


def _get_column_names(db_path: Path) -> set[str]:
    """Devuelve los nombres de columnas actuales de la tabla incidente."""
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute("PRAGMA table_info(incidente)")
        return {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()


# ── 10.1: RED — migración 002 inexistente ────────────────────────────────────

class TestMigration002Esquema:
    """
    10.1 RED → 10.2 GREEN:
    Tras upgrade head, la tabla incidente tiene las dos nuevas columnas
    y NO tiene la columna 'descripcion' vieja.
    """

    def test_upgrade_head_agrega_columnas_doble_representacion(self, db_file, monkeypatch):
        """
        10.1 RED → 10.2 GREEN:
        Aplica alembic upgrade head y verifica el esquema resultante.
        """
        _run_alembic(["upgrade", "head"], db_file)

        columnas = _get_column_names(db_file)

        assert "descripcion_original" in columnas, (
            "La columna 'descripcion_original' debe existir tras la migración 002"
        )
        assert "descripcion_pseudonimizada" in columnas, (
            "La columna 'descripcion_pseudonimizada' debe existir tras la migración 002"
        )
        assert "descripcion" not in columnas, (
            "La columna 'descripcion' vieja debe ser eliminada por la migración 002"
        )

    def test_upgrade_head_es_idempotente_en_segunda_ejecucion(self, db_file, monkeypatch):
        """
        10.2 GREEN extra:
        Ejecutar upgrade head dos veces no falla (idempotente).
        """
        _run_alembic(["upgrade", "head"], db_file)
        _run_alembic(["upgrade", "head"], db_file)  # segunda vez: no debe lanzar

        columnas = _get_column_names(db_file)
        assert "descripcion_original" in columnas
        assert "descripcion_pseudonimizada" in columnas


# ── 10.3: TRIANGULATE — round-trip con fila preexistente ────────────────────

class TestMigration002Backfill:
    """
    10.3 TRIANGULATE:
    Inserta una fila con 'descripcion' antes de migrar y verifica
    que el backfill llena correctamente ambas columnas.
    """

    def test_backfill_fila_existente_con_pii(self, db_file, monkeypatch):
        """
        10.3 TRIANGULATE (backfill):
        Una fila preexistente con descripcion que contiene PII queda con
        descripcion_pseudonimizada enmascarada y descripcion_original cifrada
        (y descifrable al texto crudo).
        """
        from datetime import datetime, timezone

        NOW = datetime.now(timezone.utc).isoformat()
        TEXTO_CON_PII = "Juan Pérez reportó falla en juan.perez@empresa.com"

        # Aplicar solo la migración 001 primero (esquema inicial con 'descripcion')
        _run_alembic(["upgrade", "001"], db_file)

        # Insertar una fila con el esquema anterior (columna 'descripcion')
        conn = sqlite3.connect(str(db_file))
        try:
            conn.execute(
                "INSERT INTO incidente "
                "(descripcion, prioridad, estado_id, requiere_revision_humana, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (TEXTO_CON_PII, "media", 1, 0, NOW, NOW),
            )
            conn.commit()
        finally:
            conn.close()

        # Aplicar migración 002 (backfill)
        _run_alembic(["upgrade", "002"], db_file)

        # Verificar que la pseudonimizada tiene etiquetas
        conn = sqlite3.connect(str(db_file))
        try:
            row = conn.execute(
                "SELECT descripcion_pseudonimizada, descripcion_original FROM incidente LIMIT 1"
            ).fetchone()
        finally:
            conn.close()

        pseudo, original_cifrado = row

        # La pseudonimizada tiene al menos una etiqueta y no el email crudo
        assert pseudo is not None, "descripcion_pseudonimizada no debe ser NULL tras backfill"
        assert "[EMAIL]" in pseudo or "[PERSONA]" in pseudo, (
            f"descripcion_pseudonimizada debe tener etiquetas PII: {pseudo!r}"
        )
        assert "juan.perez@empresa.com" not in pseudo, (
            "El email crudo no debe aparecer en descripcion_pseudonimizada"
        )

        # La original cifrada no es el texto en claro
        assert original_cifrado is not None, "descripcion_original no debe ser NULL tras backfill"
        assert original_cifrado != TEXTO_CON_PII, (
            "descripcion_original debe estar cifrada (no en claro)"
        )

        # Y se puede descifrar al texto original
        from app.utils.encryption import EncryptedText
        import app.utils.encryption as enc_module
        enc_module._fernet_instance = None  # Forzar reinicialización con la clave de prueba

        et = EncryptedText()
        descifrado = et.process_result_value(original_cifrado, None)
        assert descifrado == TEXTO_CON_PII, (
            f"descripcion_original descifrada debe coincidir con el texto original. "
            f"Obtenido: {descifrado!r}"
        )


# ── 10.3: TRIANGULATE — downgrade reversible ─────────────────────────────────

class TestMigration002Downgrade:
    """
    10.3 TRIANGULATE (downgrade):
    El downgrade de 002 a 001 restaura la columna 'descripcion' y
    elimina las dos columnas nuevas.
    """

    def test_downgrade_002_restaura_columna_descripcion(self, db_file, monkeypatch):
        """
        10.3 TRIANGULATE (downgrade):
        Tras downgrade -1 (002 → 001), la tabla incidente vuelve a tener
        'descripcion' y no tiene las columnas nuevas.
        """
        # Migrar a head
        _run_alembic(["upgrade", "head"], db_file)

        # Regresar dos pasos (003→002→001) para restaurar esquema original
        _run_alembic(["downgrade", "-2"], db_file)

        columnas = _get_column_names(db_file)

        assert "descripcion" in columnas, (
            "La columna 'descripcion' debe ser restaurada por el downgrade de 002"
        )
        assert "descripcion_original" not in columnas, (
            "La columna 'descripcion_original' debe ser eliminada por el downgrade"
        )
        assert "descripcion_pseudonimizada" not in columnas, (
            "La columna 'descripcion_pseudonimizada' debe ser eliminada por el downgrade"
        )

    def test_downgrade_con_fila_recupera_texto_descifrado(self, db_file, monkeypatch):
        """
        10.3 TRIANGULATE (downgrade round-trip):
        Una fila que fue migrada a doble representación, al hacer downgrade,
        recupera el texto original descifrado en 'descripcion'.
        """
        from datetime import datetime, timezone

        NOW = datetime.now(timezone.utc).isoformat()
        TEXTO_CON_PII = "El servidor srv-bd01 no responde desde usuario@corp.empresa.com"

        # Migrar al esquema inicial
        _run_alembic(["upgrade", "001"], db_file)

        # Insertar fila
        conn = sqlite3.connect(str(db_file))
        try:
            conn.execute(
                "INSERT INTO incidente "
                "(descripcion, prioridad, estado_id, requiere_revision_humana, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (TEXTO_CON_PII, "alta", 1, 0, NOW, NOW),
            )
            conn.commit()
        finally:
            conn.close()

        # Migrar a 002
        _run_alembic(["upgrade", "002"], db_file)

        # Hacer downgrade
        _run_alembic(["downgrade", "-1"], db_file)

        # Verificar que 'descripcion' contiene el texto original descifrado
        conn = sqlite3.connect(str(db_file))
        try:
            row = conn.execute(
                "SELECT descripcion FROM incidente LIMIT 1"
            ).fetchone()
        finally:
            conn.close()

        descripcion = row[0]
        assert descripcion == TEXTO_CON_PII, (
            f"El downgrade debe restaurar el texto original descifrado. "
            f"Obtenido: {descripcion!r}"
        )
