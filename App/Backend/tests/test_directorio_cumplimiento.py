"""
Evidencia de cumplimiento del directorio (c-60, 7.2 / c-153 / DIR-011 / DIR-009).

Inspeccion verificable de las garantias del directorio tras el endurecimiento
(c-153):
  1. El directorio usa una clave dedicada de indice ciego
     (`directory_blind_index_key`) y columnas derivadas (`email_bidx`,
     `telefono_bidx`), con el contacto CIFRADO at-rest (DIR-011). La garantia
     original de ausencia de indice ciego quedo SUPERADA.
  2. Los contactos del directorio son SINTETICOS (dominio reservado `.test`), no
     PII real.
  3. La aprobacion humana HIGH esta registrada como CONCEDIDA (2026-10-28) y el
     mecanismo de activacion de datos reales es deliberado y auditado (DIR-014);
     NO existe un toggle de runtime oculto.
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
_EVIDENCIA_DIRECTORIO = _REPO_ROOT / "docs" / "directorio-evidencia-cumplimiento.md"


def test_settings_expone_la_clave_de_indice_ciego():
    """`Settings` define la clave dedicada `directory_blind_index_key` (DIR-011)."""
    campos = set(Settings.model_fields)
    assert "directory_blind_index_key" in campos
    assert [c for c in campos if "blind" in c.lower()] != []


def test_codigo_y_migraciones_introducen_el_indice_ciego():
    """El codigo y las migraciones referencian el indice ciego (DIR-011).

    La garantia original de ausencia de indice ciego (DIR-005/DIR-009) quedo
    SUPERADA: ahora existe un modulo de derivacion y una migracion que agregan
    las columnas derivadas.
    """
    referencias: list[str] = []
    for base in (_APP_DIR, _ALEMBIC_DIR):
        for path in base.rglob("*.py"):
            fuente = path.read_text(encoding="utf-8").lower()
            if "blind_index" in fuente or "blindindex" in fuente:
                referencias.append(path.relative_to(_BACKEND_ROOT).as_posix())
    assert referencias, "Debe existir el indice ciego del directorio (DIR-011)"


def test_empleado_tiene_columnas_de_indice_ciego():
    """La tabla del directorio expone las columnas derivadas del indice ciego."""
    columnas = {columna.name.lower() for columna in Empleado.__table__.columns}
    assert {"email_bidx", "telefono_bidx"} <= columnas
    # Los campos de contacto siguen existiendo (cifrados at-rest).
    assert {"email", "telefono"} <= columnas


def test_contactos_del_seed_son_sinteticos():
    """Todo email sembrado usa el dominio reservado `.test` (sin PII real)."""
    assert PERSONAS_SINTETICAS, "El seed debe declarar contactos sinteticos"
    for persona in PERSONAS_SINTETICAS:
        assert persona["email"].endswith(".test"), persona["email"]


# ── DIR-009/DIR-014 (c-153 Tema F): aprobacion CONCEDIDA y activacion deliberada ─


def test_evidencia_registra_aprobacion_high_concedida_y_mecanismo_deliberado():
    """El artefacto de evidencia existe, declara la aprobacion humana HIGH como
    CONCEDIDA con fecha y referencia el mecanismo deliberado (DIR-014)."""
    assert _EVIDENCIA_DIRECTORIO.is_file(), (
        f"Falta el artefacto de evidencia: {_EVIDENCIA_DIRECTORIO}"
    )
    contenido = _EVIDENCIA_DIRECTORIO.read_text(encoding="utf-8")
    mayusculas = contenido.upper()
    assert "APROBACION HUMANA HIGH" in mayusculas
    assert "CONCEDIDA" in mayusculas
    assert "2026-10-28" in contenido
    assert "DIR-014" in contenido
    # El directorio sigue operando con datos SINTETICOS hasta que la activacion
    # deliberada se ejecute con aprobacion verificable.
    assert "SINTETICOS" in mayusculas


def test_no_existe_un_interruptor_oculto_de_activacion_de_datos_reales():
    """La activacion es deliberada (DIR-014): NO hay un flag booleano de `Settings`
    ni un endpoint HTTP que active datos reales sin el artefacto de aprobacion."""
    campos = {campo.lower() for campo in Settings.model_fields}
    tokens = ("real_data", "datos_reales", "use_real", "enable_real", "real_directory")
    expuestos = {c for c in campos if any(t in c for t in tokens)}
    assert expuestos == set(), f"Settings no debe exponer un toggle real: {expuestos}"

    from app.routes.directorio import router

    rutas = [getattr(r, "path", "") for r in router.routes]
    assert not any("activ" in path.lower() for path in rutas), (
        "La activacion no debe exponerse por HTTP (no hay interruptor remoto)"
    )
