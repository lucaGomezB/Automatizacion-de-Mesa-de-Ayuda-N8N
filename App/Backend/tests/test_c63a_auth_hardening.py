"""Guards estructurales del endurecimiento de autenticacion (c-63a).

Verifican, leyendo artefactos del repositorio (nginx.conf) y la configuracion
en memoria, las invariantes de coherencia entre el limite de tasa de login y el
umbral de bloqueo por cuenta (IAH-004, D7), y los defaults conservadores que
preservan el flujo de desarrollo (D8).

No levantan servicios ni requieren Docker: son deterministas.
"""

import re
from pathlib import Path

from app.config.settings import get_settings

REPO_ROOT = Path(__file__).resolve().parents[3]
NGINX_CONF_PATH = REPO_ROOT / "nginx" / "nginx.conf"

LOGIN_LOCATION = "/api/v1/auth/login"


def _nginx_conf() -> str:
    return NGINX_CONF_PATH.read_text(encoding="utf-8")


def _login_location_block() -> str:
    """Extrae el bloque `location /api/v1/auth/login { ... }` de nginx.conf."""
    conf = _nginx_conf()
    marker = f"location {LOGIN_LOCATION} {{"
    start = conf.index(marker)
    end = conf.index("}", start)
    return conf[start : end + 1]


def test_nginx_login_zone_rate_is_declared():
    assert "zone=login_limit" in _nginx_conf()


def test_nginx_login_burst_exceeds_lockout_threshold():
    """La capacidad del limit_req supera el umbral de lockout (>= 2x)."""
    block = _login_location_block()
    match = re.search(r"burst=(\d+)", block)
    assert match is not None, "La location de login debe declarar burst=N"
    burst = int(match.group(1))

    threshold = get_settings().account_lockout_threshold
    assert burst >= threshold * 2, (
        f"burst={burst} debe superar el umbral de lockout ({threshold}) para "
        "que el bloqueo sea observable antes del 429 de nginx"
    )


def test_lockout_default_is_disabled_and_conservative():
    """D8: flag apagado y parametros del bloqueo conservadores por defecto."""
    settings = get_settings()
    assert settings.account_lockout_enabled is False
    assert settings.account_lockout_threshold == 5
    assert settings.account_lockout_duration_minutes == 15


def test_short_access_token_default_and_refresh_lifetime():
    """El access por defecto es de vida corta y el refresh de vida mas larga."""
    settings = get_settings()
    assert settings.jwt_access_expire_minutes == 15
    assert settings.jwt_refresh_expire_minutes > settings.jwt_access_expire_minutes


def test_password_policy_defaults_do_not_invalidate_dev_seeds():
    """El minimo por defecto no invalida las credenciales dev grandfathered."""
    settings = get_settings()
    assert settings.password_min_length == 12