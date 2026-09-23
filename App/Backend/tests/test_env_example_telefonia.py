"""
Test estructural de las claves de entorno del canal de telefonia (c-52).

Verifica que `.env.example` documente las claves nuevas y que sus defaults
coincidan con los de `Settings` (unico lugar canonico de defaults). No valida
secretos: las claves sensibles se documentan vacias o con placeholder.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.config.settings import Settings

_ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"

# Claves que c-52 introduce (o cambia de semantica) en la superficie de config.
_REQUIRED_KEYS = (
    "TWILIO_ACCOUNT_SID",
    "GEMINI_STT_MODEL",
    "BACKEND_PUBLIC_BASE_URL",
    "COST_GUARD_UNIT_COST_BACKEND_STT_USD",
)


def _documented_value(text: str, key: str) -> str | None:
    """Valor documentado para `key`, ignorando el prefijo de comentario opcional."""
    match = re.search(rf"^\s*#?\s*{re.escape(key)}=(.*)$", text, re.MULTILINE)
    if match is None:
        return None
    return match.group(1).strip()


def test_env_example_documenta_las_claves_de_c52():
    text = _ENV_EXAMPLE.read_text(encoding="utf-8")
    for key in _REQUIRED_KEYS:
        assert _documented_value(text, key) is not None, f"falta {key} en .env.example"


def test_env_example_defaults_coinciden_con_settings():
    text = _ENV_EXAMPLE.read_text(encoding="utf-8")
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="test-key",
        pseudonymization_encryption_key="test-fernet-key",
        jwt_secret_key="test-jwt-secret",
        _env_file=None,
    )

    stt_default = _documented_value(text, "GEMINI_STT_MODEL")
    assert stt_default == settings.gemini_stt_model

    base_default = _documented_value(text, "BACKEND_PUBLIC_BASE_URL")
    assert base_default == settings.backend_public_base_url

    stt_cost = _documented_value(text, "COST_GUARD_UNIT_COST_BACKEND_STT_USD")
    assert stt_cost is not None
    assert float(stt_cost) == settings.cost_guard_unit_cost_backend_stt_usd
