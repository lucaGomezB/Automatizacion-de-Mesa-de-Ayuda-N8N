"""
Documentos y minimizacion de retencion/ARCO del directorio (c-153, Tema E / DIR-015).

Verificacion textual y estructural:
  - El runbook de retencion existe y documenta la purga MANUAL mas la alerta de
    acumulacion, declarando la ausencia de cron/scheduler/worker.
  - El procedimiento ARCO del directorio cubre ACCESO y RECTIFICACION ademas de
    la supresion, con procedimiento y constancia auditable.
  - La ventana de retencion de la auditoria del directorio queda documentada y
    alineada con el ciclo de vida.
  - La revision de minimizacion confirma que el modelo no agrega columnas PII:
    solo el indice ciego no-PII.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

from app.models.empleado import Empleado

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DOCS_SEGURIDAD = _REPO_ROOT / "docs" / "seguridad"

_RUNBOOK = _DOCS_SEGURIDAD / "runbook-retencion-directorio.md"
_ARCO_DIRECTORIO = _DOCS_SEGURIDAD / "procedimiento-arco-directorio.md"
_RETENCION_LOGS = _DOCS_SEGURIDAD / "politica-retencion-logs.md"

_COLUMNAS_PII = {"legajo", "nombre", "email", "telefono"}
_COLUMNAS_DERIVADAS = {"email_bidx", "telefono_bidx"}


def _normalizar(texto: str) -> str:
    """Minusculas y sin acentos, para comparar sin depender de la diacritica."""
    sin_acentos = "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return sin_acentos.lower()


def test_runbook_retencion_documenta_purga_manual_alerta_y_sin_cron():
    """El runbook existe y cubre purga manual + alerta, sin cron/scheduler/worker."""
    assert _RUNBOOK.is_file(), f"Falta el runbook: {_RUNBOOK}"
    texto = _normalizar(_RUNBOOK.read_text(encoding="utf-8"))
    for token in ("purga", "manual", "alerta", "conteo", "fecha_baja", "retencion"):
        assert token in texto, f"El runbook no menciona {token!r}"
    # Declara explicitamente que NO hay automatizacion de la purga.
    for token in ("cron", "scheduler", "worker"):
        assert token in texto, f"El runbook no declara la ausencia de {token!r}"


def test_arco_directorio_cubre_acceso_y_rectificacion_ademas_de_supresion():
    """El procedimiento ARCO del directorio no se limita a la supresion."""
    assert _ARCO_DIRECTORIO.is_file(), f"Falta el procedimiento: {_ARCO_DIRECTORIO}"
    texto = _normalizar(_ARCO_DIRECTORIO.read_text(encoding="utf-8"))
    for token in ("acceso", "rectificaci", "supresi", "constancia", "auditable"):
        assert token in texto, f"El procedimiento ARCO no cubre {token!r}"
    # Plazos legales del acceso y la rectificacion, alineados con el procedimiento.
    assert "10 dias" in texto, "Falta el plazo de acceso (10 dias corridos)"
    assert "5 dias" in texto, "Falta el plazo de rectificacion (5 dias habiles)"
    # Alineado con el procedimiento general.
    assert "procedimiento-arco" in texto or "procedimiento arco" in texto


def test_retencion_de_auditoria_del_directorio_documentada_y_alineada():
    """La politica de retencion define la ventana de la auditoria del directorio."""
    assert _RETENCION_LOGS.is_file(), f"Falta la politica: {_RETENCION_LOGS}"
    texto = _normalizar(_RETENCION_LOGS.read_text(encoding="utf-8"))
    assert "directorio" in texto, "No se documenta la retencion del directorio"
    assert "auditoria" in texto, "No se documenta la retencion de la auditoria"
    assert "ciclo de vida" in texto, "La ventana no se alinea con el ciclo de vida"


def test_minimizacion_no_agrega_columnas_pii():
    """El modelo conserva EXACTAMENTE las columnas PII conocidas; solo suma el
    indice ciego no-PII (`email_bidx`/`telefono_bidx`)."""
    columnas = {c.name.lower() for c in Empleado.__table__.columns}
    assert _COLUMNAS_PII <= columnas, "Faltan columnas PII esperadas del directorio"
    assert _COLUMNAS_DERIVADAS <= columnas, "Falta el indice ciego no-PII"

    # Ninguna columna adicional que sugiera un dato personal nuevo.
    sospechosas = {
        "dni", "cuil", "cuit", "direccion", "domicilio", "fecha_nacimiento",
        "nacimiento", "genero", "nacionalidad", "foto", "documento",
    }
    assert not (columnas & sospechosas), (
        f"Se agrego una columna PII no prevista: {sorted(columnas & sospechosas)}"
    )

    # Las unicas columnas derivadas del endurecimiento son los dos indices ciegos.
    derivadas = {c for c in columnas if c.endswith("_bidx")}
    assert derivadas == _COLUMNAS_DERIVADAS
