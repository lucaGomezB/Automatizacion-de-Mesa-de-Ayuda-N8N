"""
Evidencia de cumplimiento del directorio (c-60, 7.2 / DIR-005 / DIR-009).

Inspeccion verificable de tres garantias de la revision humana HIGH:
  1. NO existe clave de indice ciego ni columna de hash ciega del directorio
     (DIR-005: email/telefono en texto plano, sin indice ciego).
  2. Los contactos del directorio son SINTETICOS (dominio reservado `.test`), no
     PII real.
  3. La aprobacion humana HIGH sigue PENDIENTE y los datos reales estan
     BLOQUEADOS; no existe un toggle de runtime que los active (DIR-009).
"""

from __future__ import annotations

from pathlib import Path

from app.config.settings import Settings
from app.models.empleado import Empleado
from scripts.seed_directorio import PERSONAS_SINTETICAS

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _BACKEND_ROOT.parents[1]
_APP_DIR = _BACKEND_ROOT / "app"
_ALEMBIC_DIR = _BACKEND_ROOT / "alembic"
_SCRIPTS_DIR = _BACKEND_ROOT / "scripts"
_EVIDENCIA_DIRECTORIO = _REPO_ROOT / "docs" / "directorio-evidencia-cumplimiento.md"


def test_settings_no_expone_una_clave_de_indice_ciego():
    """`Settings` no define `directory_blind_index_key` ni variantes 'blind'."""
    campos = set(Settings.model_fields)
    assert "directory_blind_index_key" not in campos
    assert [c for c in campos if "blind" in c.lower()] == []


def test_codigo_y_migraciones_no_introducen_indice_ciego():
    """Ni el codigo ni las migraciones referencian una clave/columna de indice ciego."""
    offenders: list[str] = []
    for base in (_APP_DIR, _ALEMBIC_DIR):
        for path in base.rglob("*.py"):
            fuente = path.read_text(encoding="utf-8").lower()
            if "blind_index" in fuente or "blindindex" in fuente:
                offenders.append(path.relative_to(_BACKEND_ROOT).as_posix())
    assert offenders == [], f"No debe existir indice ciego: {offenders}"


def test_empleado_no_tiene_columna_de_hash_ni_indice_ciego():
    """La tabla del directorio no tiene columnas de hash ni de indice ciego."""
    columnas = {columna.name.lower() for columna in Empleado.__table__.columns}
    assert [c for c in columnas if "hash" in c] == []
    assert [c for c in columnas if "blind" in c] == []
    # Los campos de contacto siguen existiendo en texto plano (minimizacion).
    assert {"email", "telefono"} <= columnas


def test_contactos_del_seed_son_sinteticos():
    """Todo email sembrado usa el dominio reservado `.test` (sin PII real)."""
    assert PERSONAS_SINTETICAS, "El seed debe declarar contactos sinteticos"
    for persona in PERSONAS_SINTETICAS:
        assert persona["email"].endswith(".test"), persona["email"]


# ── DIR-009 (c-60 7.4): aprobacion HIGH pendiente y datos reales bloqueados ───


def test_evidencia_registra_aprobacion_high_pendiente_y_datos_reales_bloqueados():
    """El artefacto de evidencia existe y registra EXPLICITAMENTE la aprobacion
    humana HIGH como PENDIENTE y los datos reales como BLOQUEADOS."""
    assert _EVIDENCIA_DIRECTORIO.is_file(), (
        f"Falta el artefacto de evidencia: {_EVIDENCIA_DIRECTORIO}"
    )
    contenido = _EVIDENCIA_DIRECTORIO.read_text(encoding="utf-8").upper()
    assert "PENDIENTE" in contenido
    assert "APROBACION HUMANA HIGH" in contenido
    assert "BLOQUEADO" in contenido
    assert "DATOS REALES" in contenido
    # El directorio opera solo con sinteticos mientras la aprobacion siga pendiente.
    assert "SINTETICOS" in contenido


def test_no_existe_un_toggle_de_activacion_de_datos_reales():
    """Ni `Settings` ni el codigo de produccion exponen un flag/ruta que active
    datos reales del directorio: por diseno NO hay gate de runtime (DIR-009)."""
    campos = {campo.lower() for campo in Settings.model_fields}
    tokens = ("real_data", "datos_reales", "use_real", "enable_real", "real_directory")
    expuestos = {c for c in campos if any(t in c for t in tokens)}
    assert expuestos == set(), f"Settings no debe exponer un toggle real: {expuestos}"

    patrones = (
        "real_data", "datos_reales", "use_real", "enable_real",
        "activate_real", "activar_real", "real_directory", "directorio_real",
    )
    offenders: list[str] = []
    for base in (_APP_DIR, _ALEMBIC_DIR, _SCRIPTS_DIR):
        for path in base.rglob("*.py"):
            fuente = path.read_text(encoding="utf-8").lower()
            for patron in patrones:
                if patron in fuente:
                    rel = path.relative_to(_BACKEND_ROOT).as_posix()
                    offenders.append(f"{rel}:{patron}")
    assert offenders == [], f"No debe existir un toggle de datos reales: {offenders}"
