"""
Guards estructurales del endurecimiento de infraestructura y red (c-62).

Verifican, leyendo SOLO artefactos de configuracion del repositorio
(`docker-compose.yml`, `docker-compose.dev.yml`, `nginx/nginx.conf`), las
invariantes de los requisitos INFRA-001..INFRA-008:

- los servicios internos (PostgreSQL, Redis) no publican en todas las
  interfaces del host; Redis fue retirado del stack;
- la UI de N8N queda acotada a loopback;
- la segmentacion de red no deja que N8N comparta red con PostgreSQL;
- nginx oculta su version, agrega headers y limita tasa sin perder el
  catch-all ni la redireccion HTTP->HTTPS;
- el override de desarrollo existe y NO re-expone puertos.

No levantan servicios, no acceden a red y no requieren Docker: parsean los
archivos de configuracion de forma determinista.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
DEV_OVERRIDE_PATH = REPO_ROOT / "docker-compose.dev.yml"
NGINX_CONF_PATH = REPO_ROOT / "nginx" / "nginx.conf"

LOOPBACK_PREFIX = "127.0.0.1:"
N8N_IMAGE = "n8nio/n8n:2.11.2"
NOTIF_WEBHOOK_SUFFIX = "/webhook/notificacion-clasificacion"

# Pares (automatizacion, datos) que NUNCA deben compartir una red Docker.
FORBIDDEN_SERVICE_PAIRS = (
    ("n8n", "postgres"),
    ("n8n-corpus", "postgres-corpus"),
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _compose() -> dict:
    return yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))


def _services() -> dict:
    return _compose()["services"]


def _ports(service: dict) -> list[str]:
    return [str(p) for p in service.get("ports", [])]


def _service_networks(service: dict) -> set[str]:
    """Normaliza la seccion `networks` de un servicio (lista o dict)."""
    networks = service.get("networks")
    if networks is None:
        return {"default"}
    if isinstance(networks, dict):
        return set(networks.keys())
    return set(networks)


def _network_members() -> dict[str, set[str]]:
    """Mapa red -> conjunto de servicios conectados a ella."""
    members: dict[str, set[str]] = {}
    for name, service in _services().items():
        for network in _service_networks(service):
            members.setdefault(network, set()).add(name)
    return members


def _dev_override() -> dict:
    return yaml.safe_load(DEV_OVERRIDE_PATH.read_text(encoding="utf-8"))


def _nginx_conf() -> str:
    return NGINX_CONF_PATH.read_text(encoding="utf-8")


def _assert_loopback_only(ports: list[str], expected: str, service: str) -> None:
    """Asserta que `ports` es exactamente [expected] y que usa loopback."""
    assert ports == [expected], (
        f"{service}: se esperaba publicacion {expected!r} (loopback), "
        f"pero se encontro {ports!r}"
    )
    assert ports[0].startswith(LOOPBACK_PREFIX), (
        f"{service}: la publicacion {ports[0]!r} NO esta acotada a loopback"
    )


# ── INFRA-001 / tarea 2.5 — postura de puertos base ───────────────────────────


def test_postgres_is_bound_to_loopback_only():
    ports = _ports(_services()["postgres"])
    _assert_loopback_only(ports, "127.0.0.1:5433:5432", "postgres")


def test_redis_service_was_retired():
    assert "redis" not in _services(), (
        "El servicio 'redis' debe retirarse del stack (OQ-2=A): no tiene "
        "consumidor real"
    )


def test_n8n_ui_is_bound_to_loopback_only():
    ports = _ports(_services()["n8n"])
    _assert_loopback_only(ports, "127.0.0.1:5678:5678", "n8n")


def test_no_published_port_is_exposed_on_all_interfaces():
    """Ningun puerto publicado del stack base queda en 0.0.0.0."""
    offenders = {
        name: ports
        for name, service in _services().items()
        if (ports := _ports(service))
        and any(str(p).startswith("0.0.0.0:") for p in ports)
    }
    assert not offenders, (
        f"Puertos publicados en todas las interfaces (0.0.0.0): {offenders}"
    )


def test_n8n_no_longer_publishes_a_bare_host_mapping():
    """Regresion: `5678:5678` (todas las interfaces) no debe reaparecer."""
    ports = _ports(_services()["n8n"])
    assert "5678:5678" not in ports, (
        "El mapeo desnudo '5678:5678' expone la UI en 0.0.0.0; usar loopback"
    )


# ── INFRA-002 / OQ-7 — puertos del perfil corpus ─────────────────────────────


def test_corpus_postgres_is_bound_to_loopback_only():
    ports = _ports(_services()["postgres-corpus"])
    _assert_loopback_only(ports, "127.0.0.1:5434:5432", "postgres-corpus")


def test_corpus_backend_is_bound_to_loopback_only():
    ports = _ports(_services()["backend-corpus"])
    _assert_loopback_only(ports, "127.0.0.1:8001:8000", "backend-corpus")


def test_corpus_n8n_is_bound_to_loopback_only():
    ports = _ports(_services()["n8n-corpus"])
    _assert_loopback_only(ports, "127.0.0.1:5679:5678", "n8n-corpus")


# ── INFRA-003 — contratos de dependencia preservados ─────────────────────────


def test_no_service_depends_on_the_retired_redis():
    offenders = [
        name
        for name, service in _services().items()
        if "redis" in (service.get("depends_on") or {})
    ]
    assert not offenders, (
        f"Servicios con depends_on: redis tras retirar Redis: {offenders}"
    )


def test_no_queue_bull_redis_variables_remain():
    offenders = {
        name: sorted(
            key
            for key in (service.get("environment") or {})
            if "QUEUE_BULL_REDIS" in str(key)
        )
        for name, service in _services().items()
    }
    offenders = {name: keys for name, keys in offenders.items() if keys}
    assert not offenders, (
        f"Variables QUEUE_BULL_REDIS_* sobrevivientes: {offenders}"
    )


# ── INFRA-004 / tarea 4.5 — segmentacion de red ──────────────────────────────


def test_three_logical_networks_are_declared():
    networks = _compose().get("networks") or {}
    assert {"edge", "data", "automation"} <= set(networks), (
        f"Faltan redes logicas; declaradas: {sorted(networks)}"
    )
    assert networks["data"].get("internal") is True, (
        "La red 'data' debe ser internal: true"
    )
    assert not (networks.get("automation") or {}).get("internal"), (
        "La red 'automation' NO debe ser internal: N8N necesita egreso"
    )
    assert not (networks.get("edge") or {}).get("internal"), (
        "La red 'edge' NO debe ser internal"
    )


def test_host_access_network_exists_only_to_publish_data_ports():
    """La red de acceso al host es NO internal y solo une servicios de datos.

    Una red `internal: true` no puede publicar puertos al host, por lo que
    postgres necesita una red no-internal adicional para el loopback. Esa red NO
    debe incluir n8n, nginx ni el frontend.
    """
    networks = _compose().get("networks") or {}
    assert "host_access" in networks, "falta la red 'host_access'"
    assert not (networks.get("host_access") or {}).get("internal"), (
        "host_access NO debe ser internal: debe permitir publicar al host"
    )
    members = _network_members().get("host_access", set())
    assert members <= {"postgres", "postgres-corpus"}, (
        f"host_access solo debe unir servicios de datos; tiene {sorted(members)}"
    )


def test_no_network_contains_an_automation_and_a_data_service():
    members = _network_members()
    for automation, data in FORBIDDEN_SERVICE_PAIRS:
        for network, names in members.items():
            assert not (
                {automation, data} <= names
            ), f"La red {network!r} contiene {automation!r} y {data!r} juntos"


def test_postgres_is_isolated_to_data_and_host_access():
    networks = _service_networks(_services()["postgres"])
    assert networks == {"data", "host_access"}, (
        f"postgres debe estar en data + host_access; hallado {sorted(networks)}"
    )
    assert "automation" not in networks and "edge" not in networks


def test_n8n_stays_only_on_the_automation_network():
    assert _service_networks(_services()["n8n"]) == {"automation"}


def test_nginx_and_frontend_are_not_on_the_data_network():
    for name in ("nginx", "frontend"):
        assert "data" not in _service_networks(_services()[name]), (
            f"{name} no debe estar en la red de datos"
        )


def test_backend_joins_edge_data_and_automation():
    assert _service_networks(_services()["backend"]) == {
        "edge",
        "data",
        "automation",
    }


def test_corpus_services_respect_the_same_segmentation():
    services = _services()
    assert _service_networks(services["postgres-corpus"]) == {
        "data",
        "host_access",
    }
    assert _service_networks(services["n8n-corpus"]) == {"automation"}
    backend_corpus = _service_networks(services["backend-corpus"])
    assert {"data", "automation"} <= backend_corpus


# ── INFRA-006 — nginx endurecido ─────────────────────────────────────────────


def test_nginx_hides_its_version():
    assert "server_tokens off" in _nginx_conf(), (
        "nginx.conf debe declarar 'server_tokens off'"
    )


def test_nginx_adds_referrer_and_permissions_policy():
    conf = _nginx_conf()
    assert "Referrer-Policy" in conf, "falta el header Referrer-Policy"
    assert "strict-origin-when-cross-origin" in conf
    assert "Permissions-Policy" in conf, "falta el header Permissions-Policy"


def test_nginx_rate_limits_login_and_webhooks():
    conf = _nginx_conf()
    assert "limit_req_zone" in conf, "falta la definicion de zona limit_req_zone"
    assert "limit_req " in conf, "falta aplicar limit_req en alguna location"
    assert "/api/v1/auth/login" in conf, (
        "el limite de tasa debe aplicarse sobre el login"
    )
    assert "/api/v1/cost-guard/twilio/voice" in conf, (
        "el limite de tasa debe aplicarse sobre el webhook de voz"
    )


def test_nginx_keeps_catchall_and_http_to_https_redirect():
    conf = _nginx_conf()
    assert "return 444" in conf, "el catch-all debe conservarse"
    assert "return 301 https://" in conf, (
        "la redireccion HTTP->HTTPS debe conservarse"
    )


def test_nginx_defers_csp():
    """CSP se difiere por decision del autor (OQ-6): no debe agregarse.

    Se busca la DIRECTIVA (no la mera mencion en un comentario).
    """
    assert "add_header Content-Security-Policy" not in _nginx_conf()


# ── INFRA-007 / OQ-5 — override de desarrollo ────────────────────────────────


def test_dev_override_exists():
    assert DEV_OVERRIDE_PATH.exists(), (
        "Debe existir docker-compose.dev.yml como override opt-in de desarrollo"
    )


def test_dev_override_declares_development_environment():
    override = _dev_override()
    backend = (override.get("services") or {}).get("backend") or {}
    environment = backend.get("environment") or {}
    assert environment.get("ENVIRONMENT") == "development", (
        "El override de desarrollo debe declarar ENVIRONMENT=development en el "
        f"backend; encontrado: {environment!r}"
    )


def test_dev_override_is_not_a_port_reexposer():
    override = _dev_override()
    offenders = [
        name
        for name, service in (override.get("services") or {}).items()
        if (service or {}).get("ports")
    ]
    assert not offenders, (
        f"El override de desarrollo NO debe re-exponer puertos: {offenders}"
    )


def test_default_compose_has_no_override_for_ports():
    """El estado por defecto (sin -f) queda endurecido."""
    assert not DEV_OVERRIDE_PATH.name == "docker-compose.override.yml", (
        "El override no debe ser el automatico docker-compose.override.yml"
    )


def test_default_compose_does_not_enable_development_app_posture():
    """TRIANGULATE (INFRA-007): el modo por defecto NO es desarrollo."""
    backend_environment = _services()["backend"].get("environment") or {}
    assert backend_environment.get("ENVIRONMENT") != "development", (
        "El compose base no debe fijar ENVIRONMENT=development; esa postura es "
        "opt-in via docker-compose.dev.yml"
    )


# ── INFRA-008 — contratos de CI preservados ──────────────────────────────────


def test_n8n_image_stays_pinned():
    image = str(_services()["n8n"].get("image", ""))
    assert image == N8N_IMAGE, (
        f"La imagen de n8n debe seguir pineada a {N8N_IMAGE!r}; hallado {image!r}"
    )


def test_n8n_webhook_url_keeps_the_dedicated_route():
    value = str(_services()["backend"]["environment"]["N8N_WEBHOOK_URL"])
    assert value.endswith(NOTIF_WEBHOOK_SUFFIX), (
        f"N8N_WEBHOOK_URL debe terminar en {NOTIF_WEBHOOK_SUFFIX!r}; {value!r}"
    )


def test_n8n_execution_timeouts_are_preserved():
    environment = _services()["n8n"]["environment"]
    assert "EXECUTIONS_TIMEOUT" in environment
    assert "EXECUTIONS_TIMEOUT_MAX" in environment
    assert int(str(environment["EXECUTIONS_TIMEOUT_MAX"])) >= int(
        str(environment["EXECUTIONS_TIMEOUT"])
    )
    assert "EXECUTIONS_DATA_PRUNE" in environment
    assert str(environment["EXECUTIONS_DATA_MAX_AGE"]) == "720"
