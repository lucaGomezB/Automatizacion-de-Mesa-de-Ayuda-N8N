"""
Lint documental hermetico de `docs/seguridad/` (C-156, SGD-018).

TDD: los casos describen primero el contrato del validador y se ejecutan antes de
implementarlo. El lint valida cuatro invariantes sobre el cuerpo documental de
`docs/seguridad/`, sin red ni servicios externos:

    (a) cada documento listado en `README.md` existe;
    (b) cada documento de gobernanza de la carpeta esta listado en el indice;
    (c) cada documento de gobernanza abre con los encabezados requeridos
        (control mapeado, estado, alcance y encuadre);
    (d) ningun documento afirma certificacion o conformidad con terminos
        afirmativos prohibidos (se toleran las negaciones y el encuadre
        "alineado con").

Se ejecuta como un test mas de la suite de backend, de modo que el job de
integracion continua existente lo corre sin modificar `.github/workflows/ci.yml`.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SEGURIDAD_DIR = _REPO_ROOT / "docs" / "seguridad"

# Documentos de la carpeta que NO son documentos de gobernanza con plantilla
# comun: el acta de consentimiento T1 es un anexo. Allowlist explicita.
_ALLOWLIST = frozenset({"acta-consentimiento-t1.md"})

# Encabezados que todo documento de gobernanza debe declarar.
_REQUIRED_HEADERS = ("Control mapeado", "Estado", "Alcance", "Encuadre")

# Afirmaciones positivas de certificacion/conformidad (terminos prohibidos en
# contexto afirmativo). Se toleran las negaciones y el encuadre "alineado con".
_FORBIDDEN_CLAIMS = (
    r"est[áa]\s+certificad",
    r"\bsistema\s+certificad",
    r"\bes\s+compliant\b",
    r"\bsomos\s+compliant\b",
    r"cumple\s+(con\s+)?(iso|nist|ley)",
    r"certificaci[óo]n\s+obtenida",
)

# Marcadores que descartan una linea del escaneo de terminos prohibidos:
# negaciones y encuadre de alineacion, y la propia regla de lenguaje del indice.
_EXCLUDE_LINE = (
    r"\bno\b",
    r"\bsin\b",
    r"\bni\b",
    r"alineado con",
    r"prohibid",
    r"a evitar",
)


def _linea_excluida(linea: str) -> bool:
    return any(re.search(p, linea, re.IGNORECASE) for p in _EXCLUDE_LINE)


def lint_seguridad_docs(seguridad_dir: Path) -> list[str]:
    """Valida la integridad documental de `docs/seguridad/` de forma hermética."""
    index_text = (seguridad_dir / "README.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"`([^`]+\.md)`", index_text))

    repo_root = seguridad_dir.parents[1]
    fallas: list[str] = []

    for name in sorted(listed):
        resolubles = (seguridad_dir / name).exists() or (repo_root / name).exists()
        if not resolubles:
            fallas.append(f"documento listado inexistente: {name}")

    all_md = sorted(p.name for p in seguridad_dir.glob("*.md"))
    governance = [n for n in all_md if n != "README.md" and n not in _ALLOWLIST]

    for name in governance:
        if name not in listed:
            fallas.append(f"documento de gobernanza no listado en el indice: {name}")

    for name in governance:
        text = (seguridad_dir / name).read_text(encoding="utf-8")
        for campo in _REQUIRED_HEADERS:
            if campo not in text:
                fallas.append(f"encabezado requerido faltante en {name}: {campo}")
        for linea in text.splitlines():
            if _linea_excluida(linea):
                continue
            for patron in _FORBIDDEN_CLAIMS:
                if re.search(patron, linea, re.IGNORECASE):
                    fallas.append(
                        f"afirmacion prohibida en {name}: '{linea.strip()}'"
                    )
                    break

    return fallas


def _doc_valido(extra: str = "") -> str:
    """Documento de gobernanza minimo con los cuatro encabezados requeridos."""
    return (
        "# Documento de prueba\n\n"
        "> **Control mapeado**: ISO/IEC 27002:2022 5.1.\n"
        "> **Estado**: v1 (2026-10-28).\n"
        "> **Alcance**: prueba del lint documental.\n"
        "> **Encuadre**: documento alineado con los marcos; no es certificacion.\n\n"
        + extra
    )


# ── Casos base (RED) ─────────────────────────────────────────────────────────


def test_lint_falla_si_documento_listado_no_existe(tmp_path):
    """Un documento del indice que no existe en la carpeta rompe el lint."""
    (tmp_path / "README.md").write_text("| `inexistente.md` |\n", encoding="utf-8")
    fallas = lint_seguridad_docs(tmp_path)
    assert any("inexistente.md" in f for f in fallas), fallas


def test_lint_falla_si_documento_de_gobernanza_no_esta_listado(tmp_path):
    """Un documento de gobernanza presente pero no listado rompe el lint."""
    (tmp_path / "README.md").write_text("# Indice sin documentos.\n", encoding="utf-8")
    (tmp_path / "nuevo.md").write_text(_doc_valido(), encoding="utf-8")
    fallas = lint_seguridad_docs(tmp_path)
    assert any("nuevo.md" in f for f in fallas), fallas


def test_lint_falla_si_falta_un_encabezado_requerido(tmp_path):
    """Un documento de gobernanza sin un encabezado requerido rompe el lint."""
    (tmp_path / "README.md").write_text("| `incompleto.md` |\n", encoding="utf-8")
    (tmp_path / "incompleto.md").write_text(
        "# Doc\n\n"
        "> **Control mapeado**: 5.1.\n"
        "> **Estado**: v1.\n"
        "> **Alcance**: x.\n",
        encoding="utf-8",
    )
    fallas = lint_seguridad_docs(tmp_path)
    assert any("incompleto.md" in f and "Encuadre" in f for f in fallas), fallas


def test_lint_falla_ante_afirmacion_de_certificacion(tmp_path):
    """Una afirmacion positiva de certificacion rompe el lint."""
    (tmp_path / "README.md").write_text("| `cert.md` |\n", encoding="utf-8")
    (tmp_path / "cert.md").write_text(
        _doc_valido("El sistema esta certificado y cumple ISO 27001.\n"),
        encoding="utf-8",
    )
    fallas = lint_seguridad_docs(tmp_path)
    assert any("cert.md" in f for f in fallas), fallas


# ── Triangulacion ────────────────────────────────────────────────────────────


def test_lint_tolera_encuadre_de_alineacion(tmp_path):
    """El encuadre 'alineado con' no es una afirmacion de certificacion."""
    (tmp_path / "README.md").write_text("| `alineado.md` |\n", encoding="utf-8")
    (tmp_path / "alineado.md").write_text(
        _doc_valido("El sistema esta alineado con los marcos.\n"),
        encoding="utf-8",
    )
    fallas = lint_seguridad_docs(tmp_path)
    assert not any("alineado.md" in f for f in fallas), fallas


def test_lint_tolera_negacion_de_certificacion(tmp_path):
    """La negacion 'no constituye certificacion' no debe romper el lint."""
    (tmp_path / "README.md").write_text("| `negacion.md` |\n", encoding="utf-8")
    (tmp_path / "negacion.md").write_text(
        _doc_valido("Este documento no constituye certificacion ni auditoria.\n"),
        encoding="utf-8",
    )
    fallas = lint_seguridad_docs(tmp_path)
    assert not any("negacion.md" in f for f in fallas), fallas


def test_lint_no_exige_encabezados_al_anexo(tmp_path):
    """El acta de consentimiento (allowlist) no exige encabezados de gobernanza."""
    (tmp_path / "README.md").write_text(
        "| `acta-consentimiento-t1.md` |\n", encoding="utf-8"
    )
    (tmp_path / "acta-consentimiento-t1.md").write_text(
        "# Acta sin encabezados de gobernanza\n", encoding="utf-8"
    )
    fallas = lint_seguridad_docs(tmp_path)
    assert not any("acta-consentimiento-t1.md" in f for f in fallas), fallas


def test_lint_pasa_sobre_el_repositorio_real():
    """El lint debe pasar sobre el estado real de `docs/seguridad/`."""
    fallas = lint_seguridad_docs(_SEGURIDAD_DIR)
    assert fallas == [], "el lint documental fallo:\n" + "\n".join(fallas)
