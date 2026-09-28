"""Tests del escáner de secretos para la memoria de Engram (C-38).

El módulo `scripts/security/scan_engram_secrets.py` recorre los chunks
comprimidos que escribe `engram sync` (`.engram/chunks/*.jsonl.gz`) y avisa si
quedó algún valor con forma de credencial antes de publicarlo en el repo.

Capas:
- Tests de unidad sobre `find_secrets` (puro, sin I/O).
- Tests de contrato sobre el CLI (`main`/subprocess) para exit codes, redacción
  y lectura de archivos `.gz` reales.

Ejecución (desde la raíz del repo):
    python3 -m pytest scripts/security/test_scan_engram_secrets.py -q

Strict TDD: RED (módulo ausente) -> GREEN -> TRIANGULATE -> REFACTOR.

Nota: los literales que parecen secretos en este archivo son falsos y llevan el
marcador `gitleaks:allow` para no activar el hook pre-commit del repo.
"""

from __future__ import annotations

import gzip
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "scripts" / "security" / "scan_engram_secrets.py"

sys.path.insert(0, str(SCRIPT_DIR := REPO_ROOT / "scripts" / "security"))

import scan_engram_secrets as scanner  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _run_cli(*args: str) -> subprocess.CompletedProcess:
    """Ejecuta el scanner como proceso, desde la raíz del repo."""
    return subprocess.run(
        [sys.executable, str(SCANNER), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def _write_gzip_chunk(directory: Path, text: str) -> Path:
    """Escribe un chunk `.jsonl.gz` de una sola línea, como hace engram sync."""
    path = directory / "chunk.jsonl.gz"
    with gzip.open(path, "wb") as handle:
        handle.write(text.encode("utf-8"))
    return path


# ---------------------------------------------------------------------------
# 1.1 Google API key dentro de un chunk gzip -> 1 finding, exit 1, redactado
# ---------------------------------------------------------------------------
def test_google_key_in_gzip_chunk_is_flagged_and_redacted(tmp_path):
    raw_key = "AIzaSyFAKEfakeFAKEfakeFAKEfakeFAKEfake"  # gitleaks:allow
    chunk = _write_gzip_chunk(
        tmp_path,
        '{"type":"observation","data":"' + raw_key + '"}',
    )

    result = _run_cli(str(chunk))

    assert result.returncode == 1, result.stdout + result.stderr
    assert "[google_api_key]" in result.stdout
    assert raw_key not in result.stdout
    assert raw_key not in result.stderr
    assert "Total: 1" in result.stdout


# ---------------------------------------------------------------------------
# 1.2 Credenciales por defecto
# ---------------------------------------------------------------------------
def test_admin_admin123_is_flagged():
    findings = scanner.find_secrets("admin/admin123", "mem")  # gitleaks:allow
    assert [f.pattern_name for f in findings] == ["default_credentials"]


def test_admin_admin_is_flagged():
    findings = scanner.find_secrets("admin/admin", "mem")  # gitleaks:allow
    assert [f.pattern_name for f in findings] == ["default_credentials"]


def test_mesa_and_n8n_local_dev_are_flagged():
    assert scanner.find_secrets("mesa_local_dev", "mem")
    assert scanner.find_secrets("n8n_local_dev", "mem")


# ---------------------------------------------------------------------------
# 1.3 Connection string con credenciales embebidas
# ---------------------------------------------------------------------------
def test_connection_string_with_credentials_is_flagged():
    text = "postgresql://mesa:mesa@localhost:5432/db"  # gitleaks:allow
    names = [f.pattern_name for f in scanner.find_secrets(text, "mem")]
    assert "conn_string_creds" in names


# ---------------------------------------------------------------------------
# 1.3b Asignación genérica key/secret/token = valor largo
# ---------------------------------------------------------------------------
def test_assignment_secret_is_flagged():
    text = '"api_key": "abcdefghijklmnopqrstuvwxyz123456"'  # gitleaks:allow
    names = [f.pattern_name for f in scanner.find_secrets(text, "mem")]
    assert "assignment_secret" in names


# ---------------------------------------------------------------------------
# 1.3c Exclusión acotada: referencias a código (rutas de atributos punteadas)
#      NO son credenciales literales.
# ---------------------------------------------------------------------------
def test_dotted_code_reference_is_not_flagged():
    assert scanner.find_secrets("api_key=settings.gemini_api_key", "mem") == []  # gitleaks:allow


def test_dotted_code_reference_with_spaces_is_not_flagged():
    assert scanner.find_secrets("secret = settings.n8n_webhook_secret", "mem") == []  # gitleaks:allow


def test_literal_secret_value_is_still_flagged():
    text = "api_key=AbCdEf0123456789AbCdEf0123456789"  # gitleaks:allow
    names = [f.pattern_name for f in scanner.find_secrets(text, "mem")]
    assert names.count("assignment_secret") == 1


# ---------------------------------------------------------------------------
# 1.4 Clave estilo Fernet (44 chars base64 + '=')
# ---------------------------------------------------------------------------
def test_fernet_key_is_flagged():
    key = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="  # gitleaks:allow
    findings = scanner.find_secrets(key, "mem")
    assert [f.pattern_name for f in findings] == ["fernet_key"]
    assert findings[0].redacted == "2BFq***"
    assert key not in findings[0].redacted


# ---------------------------------------------------------------------------
# 1.5 Controles de falso positivo: NO deben marcarse
# ---------------------------------------------------------------------------
def test_placeholder_values_are_not_flagged():
    control = "\n".join(
        [
            '"api_key": "your-api-key-here"',  # gitleaks:allow
            '"credential_id": "REPLACE_WITH_X_CREDENTIAL_ID"',  # gitleaks:allow
            "nota: [REDACTADO]",
            "nota: [clave-de-prueba]",
            "GEMINI_API_KEY=ci-dummy-key",  # gitleaks:allow
            '"integrity": "sha512-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV=="',  # gitleaks:allow
        ]
    )

    assert scanner.find_secrets(control, "control") == []


# ---------------------------------------------------------------------------
# 1.6 Allowlist por match: "example" lejos del secreto NO lo suprime
# ---------------------------------------------------------------------------
def test_allowlist_is_applied_per_match_not_per_line():
    raw_key = "AIzaSyREALfakeREALfakeREALfake12345"  # gitleaks:allow
    # "example" aparece en la misma línea pero a más de 40 chars del match.
    text = '{"note":"example",' + (" " * 80) + '"data":"' + raw_key + '"}'

    findings = scanner.find_secrets(text, "chunk")

    assert len(findings) == 1
    assert findings[0].pattern_name == "google_api_key"


def test_allowlist_token_next_to_match_does_suppress():
    raw_key = "AIzaSyFAKEfakeFAKEfakeFAKEfakeFAKEfake"  # gitleaks:allow
    text = '{"note":"example placeholder","data":"' + raw_key + '"}'

    assert scanner.find_secrets(text, "chunk") == []


# ---------------------------------------------------------------------------
# 1.7 Chunk gzip limpio -> exit 0, sin hallazgos
# ---------------------------------------------------------------------------
def test_clean_gzip_chunk_exits_zero(tmp_path):
    chunk = _write_gzip_chunk(tmp_path, '{"type":"observation","note":"hola mundo"}')

    result = _run_cli(str(chunk))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Total: 0" in result.stdout


# ---------------------------------------------------------------------------
# 1.8 Archivo plano (no gzip) también se escanea
# ---------------------------------------------------------------------------
def test_plain_file_is_scanned(tmp_path):
    raw_key = "AIzaSyFAKEfakeFAKEfakeFAKEfakeFAKEfake"  # gitleaks:allow
    plain = tmp_path / "memory.json"
    plain.write_text('{"data":"' + raw_key + '"}', encoding="utf-8")

    result = _run_cli(str(plain))

    assert result.returncode == 1
    assert "[google_api_key]" in result.stdout
    assert raw_key not in result.stdout


# ---------------------------------------------------------------------------
# 1.9 Path inexistente -> exit 2 (error de uso/IO)
# ---------------------------------------------------------------------------
def test_missing_path_is_usage_error(tmp_path):
    result = _run_cli(str(tmp_path / "does-not-exist"))
    assert result.returncode == 2


# ---------------------------------------------------------------------------
# 1.10 Configuración de patrones y allowlist
# ---------------------------------------------------------------------------
def test_all_documented_patterns_are_registered():
    expected = {
        "google_api_key",
        "google_oauth",
        "private_key_pem",
        "assignment_secret",
        "twilio",
        "jwt",
        "fernet_key",
        "ngrok",
        "aws_key",
        "github_pat",
        "slack",
        "stripe",
        "conn_string_creds",
        "default_credentials",
    }
    assert expected <= set(scanner.PATTERN_NAMES)
