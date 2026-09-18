"""Unit tests for the disposable PostgreSQL test database infrastructure (c-32).

These tests pin the contract of the test-only URL resolution and safety guard
defined in ``tests/conftest.py``. They are NOT marked as integration: they only
inspect URL strings and the guard decision, so they run in the fast SQLite suite
without touching any real database.
"""

import warnings

import pytest

from tests import conftest
from tests.conftest import (
    UnsafeTestDatabaseError,
    _assert_safe_pg_target,
    _database_name,
    _get_pg_url,
    _maintenance_url,
)

APP_DB_URL = "postgresql+asyncpg://mesa:mesa_local_dev@localhost:5433/mesa_de_ayuda"
SAFE_PG_URL = "postgresql+asyncpg://mesa:mesa_local_dev@localhost:5433/mesa_de_ayuda_test"


def test_default_pg_url_never_targets_app_database(monkeypatch):
    """Without TEST_PG_URL the resolved target is the disposable test database."""
    monkeypatch.delenv("TEST_PG_URL", raising=False)

    resolved = _get_pg_url()
    resolved_name = _database_name(resolved)

    assert resolved_name == "mesa_de_ayuda_test"
    assert resolved_name != "mesa_de_ayuda"
    assert "_test" in resolved_name


def test_test_pg_url_is_honored(monkeypatch):
    """An explicit TEST_PG_URL overrides the default resolution."""
    explicit = "postgresql+asyncpg://user:pw@dbhost:5555/explicitly_chosen_db"
    monkeypatch.setenv("TEST_PG_URL", explicit)

    assert _get_pg_url() == explicit


def test_guard_aborts_when_target_matches_app_database(monkeypatch):
    """A target whose name equals the app database aborts with an actionable error."""
    monkeypatch.setenv("DATABASE_URL", APP_DB_URL)
    monkeypatch.setenv("TEST_PG_URL", APP_DB_URL)
    monkeypatch.delenv("TEST_PG_ALLOW_APP_DB", raising=False)

    with pytest.raises(UnsafeTestDatabaseError) as excinfo:
        _assert_safe_pg_target(APP_DB_URL)

    message = str(excinfo.value)
    assert "mesa_de_ayuda" in message
    assert "TEST_PG_ALLOW_APP_DB" in message


def test_guard_allows_explicit_opt_in(monkeypatch):
    """TEST_PG_ALLOW_APP_DB=1 is the only explicit opt-in for an app-DB target."""
    monkeypatch.setenv("DATABASE_URL", APP_DB_URL)
    monkeypatch.setenv("TEST_PG_ALLOW_APP_DB", "1")

    _assert_safe_pg_target(APP_DB_URL)  # must not raise


def test_guard_allows_a_different_database(monkeypatch):
    """A target whose name differs from the app database is never blocked."""
    monkeypatch.setenv("DATABASE_URL", APP_DB_URL)
    monkeypatch.delenv("TEST_PG_ALLOW_APP_DB", raising=False)

    _assert_safe_pg_target(SAFE_PG_URL)  # must not raise


def test_guard_does_not_block_the_ci_scenario(monkeypatch):
    """CI: DATABASE_URL is a dummy (ci_dummy) while TEST_PG_URL names the service DB.

    The guard compares by name, so a dummy DATABASE_URL must not block a target
    whose name differs (the CI service container DB). This keeps ci.yml working
    without TEST_PG_ALLOW_APP_DB.
    """
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy"
    )
    ci_target = "postgresql+asyncpg://mesa:mesa_local_dev@localhost:5432/mesa_de_ayuda"
    monkeypatch.setenv("TEST_PG_URL", ci_target)
    monkeypatch.delenv("TEST_PG_ALLOW_APP_DB", raising=False)

    _assert_safe_pg_target(ci_target)  # must not raise


def test_maintenance_url_targets_postgres_database():
    """The maintenance URL keeps credentials/host but swaps the database to postgres."""
    maintenance = _maintenance_url(SAFE_PG_URL)
    assert _database_name(maintenance) == "postgres"


def test_provisioning_only_when_test_pg_url_absent(monkeypatch):
    """Provisioning happens only when TEST_PG_URL is not explicitly set."""
    monkeypatch.delenv("TEST_PG_URL", raising=False)
    assert conftest._should_provision_disposable_database() is True

    monkeypatch.setenv("TEST_PG_URL", SAFE_PG_URL)
    assert conftest._should_provision_disposable_database() is False


def test_provision_falls_back_with_warning(monkeypatch):
    """When CREATE DATABASE is unavailable, provisioning warns and does not abort."""

    async def _boom(pg_url):
        raise RuntimeError("permission denied to create database")

    monkeypatch.setattr(conftest, "_ensure_database_async", _boom)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        provisioned = conftest._provision_disposable_database(SAFE_PG_URL)

    assert provisioned is False
    assert any(
        "descartable" in str(w.message).lower() or "disposable" in str(w.message).lower()
        for w in caught
    )