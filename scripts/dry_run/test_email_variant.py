"""§7.2 - the automated email variant is opt-in and absent by default.

These tests pin the gating contract without any SMTP server or credential:

* the CLI flag defaults to OFF;
* ``run_email_variant`` returns no checks at all when the flag is absent, so the
  mandatory cost-zero path completes with no email configuration;
* an explicit opt-in without credentials yields a PENDING (never PASS) check and
  therefore a non-zero exit code;
* a fully configured environment parses into the expected SMTP settings.

Run with:
    cd scripts/dry_run && python -m pytest test_email_variant.py -q
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dry_run
from checks import STATUS_PENDING, exit_code

_EMAIL_ENV = (
    "DRY_RUN_EMAIL_SMTP_HOST",
    "DRY_RUN_EMAIL_SMTP_PORT",
    "DRY_RUN_EMAIL_FROM",
    "DRY_RUN_EMAIL_TO",
    "DRY_RUN_EMAIL_SMTP_USER",
    "DRY_RUN_EMAIL_SMTP_PASSWORD",
    "DRY_RUN_EMAIL_USE_TLS",
)


def _clear_email_env(monkeypatch):
    for name in _EMAIL_ENV:
        monkeypatch.delenv(name, raising=False)


def test_email_flag_defaults_off():
    assert dry_run.build_parser().parse_args([]).with_email is False


def test_email_flag_opts_in():
    assert dry_run.build_parser().parse_args(["--with-email"]).with_email is True


def test_variant_is_absent_when_flag_is_not_set():
    args = SimpleNamespace(with_email=False)
    # Even with a token available, the default path adds zero email checks.
    assert dry_run.run_email_variant(args, "https://localhost", {"token": "token"}) == []


def test_email_config_is_none_when_env_incomplete():
    assert dry_run.email_config_from_env({}) is None
    assert dry_run.email_config_from_env({"DRY_RUN_EMAIL_SMTP_HOST": "smtp.example"}) is None


def test_email_config_parses_complete_env():
    config = dry_run.email_config_from_env(
        {
            "DRY_RUN_EMAIL_SMTP_HOST": "smtp.example",
            "DRY_RUN_EMAIL_FROM": "from@example.com",
            "DRY_RUN_EMAIL_TO": "mesa@example.com",
        }
    )
    assert config == {
        "host": "smtp.example",
        "port": 587,
        "from": "from@example.com",
        "to": "mesa@example.com",
        "user": "",
        "password": "",
        "use_tls": True,
    }


def test_opt_in_without_credentials_is_pending_and_nonzero(monkeypatch):
    _clear_email_env(monkeypatch)
    args = SimpleNamespace(with_email=True, timeout=1, poll_timeout=1)
    results = dry_run.run_email_variant(args, "https://localhost", {"token": "token"})
    assert len(results) == 1
    assert results[0].status == STATUS_PENDING
    assert results[0].ok is False
    assert exit_code(results) != 0
