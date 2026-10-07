"""
Guards estaticos de aislamiento del perfil Compose `corpus` (c-70, archivado).

Cierra con prueba automatizada (offline) los tres escenarios de
`telefonia-corpus-medicion` que quedaban como verificacion manual/operativa:

1. "Base descartable aislada de la operativa": los servicios del corpus estan
   gateados por `profiles: ["corpus"]`, usan su PROPIA base (`mesa_de_ayuda_corpus`),
   puertos y volumenes, y nunca montan los volumenes de la aplicacion.
2. "Wipe sin tocar la base de la aplicacion": el runbook documenta el wipe
   ACOTADO POR SERVICIO (`down -v postgres-corpus backend-corpus n8n-corpus`),
   el unico seguro dado que el nombre de proyecto Compose es compartido.
3. "Conmutacion de la Voice URL documentada": el runbook documenta como apuntar
   la Voice URL del TwiML App al backend del corpus y como restaurarla.

Estos guards afirman invariantes de CONFIGURACION y DOCUMENTACION, no una
corrida viva. El aislamiento en vivo se ejercita manualmente via el runbook.
"""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
COMPOSE_PATH = REPO / "docker-compose.yml"
RUNBOOK_PATH = REPO / "docs" / "runbook-corpus-telefonia.md"

CORPUS_SERVICES = ("postgres-corpus", "backend-corpus", "n8n-corpus")
BASE_SERVICES = ("postgres", "backend", "n8n", "nginx", "frontend")
APP_VOLUMES = {"postgres_data", "n8n_data"}


def _compose() -> dict:
    return yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))


def _services() -> dict:
    return _compose()["services"]


def _ports(service: dict) -> list[str]:
    return [str(p) for p in service.get("ports", [])]


def _named_volumes(service: dict) -> list[str]:
    sources = []
    for volume in service.get("volumes", []):
        source = volume if isinstance(volume, str) else volume.get("source", "")
        # Solo volumenes nombrados (los bind mounts empiezan con '.' o '/')
        if source and not source.startswith((".", "/")):
            sources.append(source.split(":")[0])
    return sources


def test_corpus_services_are_gated_by_the_corpus_profile():
    services = _services()
    for name in CORPUS_SERVICES:
        assert services[name].get("profiles") == ["corpus"], (
            f"{name} debe estar gateado por profiles: ['corpus']"
        )


def test_base_services_are_not_part_of_the_corpus_profile():
    services = _services()
    for name in BASE_SERVICES:
        profiles = services[name].get("profiles") or []
        assert "corpus" not in profiles, (
            f"{name} (stack base) no debe portar el perfil 'corpus'"
        )


def test_corpus_postgres_uses_its_own_database_and_port():
    service = _services()["postgres-corpus"]
    assert service["environment"]["POSTGRES_DB"] == "mesa_de_ayuda_corpus"
    # Distinta de la base operativa (5433) para poder coexistir.
    assert "5434:5432" in _ports(service)


def test_corpus_backend_points_only_to_the_corpus_database():
    service = _services()["backend-corpus"]
    database_url = str(service["environment"]["DATABASE_URL"])
    assert "postgres-corpus" in database_url
    assert "mesa_de_ayuda_corpus" in database_url
    # Distinto del backend operativo (8000) para el tunel propio del corpus.
    assert "8001:8000" in _ports(service)


def test_corpus_n8n_is_isolated_and_bound_to_the_corpus_backend():
    service = _services()["n8n-corpus"]
    assert service["environment"]["BACKEND_URL"] == "http://backend-corpus:8000"
    # Distinto del N8N operativo (5678).
    assert "5679:5678" in _ports(service)


def test_corpus_services_never_mount_the_application_volumes():
    services = _services()
    for name in CORPUS_SERVICES:
        mounted = set(_named_volumes(services[name]))
        assert not (mounted & APP_VOLUMES), (
            f"{name} no debe montar volumenes de la aplicacion: {mounted & APP_VOLUMES}"
        )
    declared = set((_compose().get("volumes") or {}).keys())
    assert {"postgres_corpus_data", "n8n_corpus_data"} <= declared, (
        "El perfil corpus debe declarar sus propios volumenes"
    )


def test_runbook_documents_the_service_scoped_wipe():
    doc = RUNBOOK_PATH.read_text(encoding="utf-8")
    # El wipe sin nombres de servicio borraria tambien la base operativa; el
    # runbook debe documentar la forma acotada por servicio.
    assert "down -v postgres-corpus backend-corpus n8n-corpus" in doc


def test_runbook_documents_the_voice_url_switch_and_restore():
    doc = RUNBOOK_PATH.read_text(encoding="utf-8")
    assert "applications:update" in doc
    assert "--voice-url" in doc
    assert "/api/v1/cost-guard/twilio/voice" in doc
    # Debe documentar tanto la conmutacion al corpus como la restauracion.
    lowered = doc.lower()
    assert "restaurar" in lowered
