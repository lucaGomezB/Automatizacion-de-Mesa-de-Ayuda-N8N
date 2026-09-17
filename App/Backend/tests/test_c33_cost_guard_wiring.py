"""
Tests de cobertura automatica del cableado de la notificacion dedicada (C-33, W4).

Responsabilidad:
    Convierte en verificable la propiedad introducida por C-33 D7: el backend
    notifica a una ruta DEDICADA (`notificacion-clasificacion`) distinta del
    webhook de alta (`incidente-web`), y la guia del workflow documenta ese
    acoplamiento. Antes, esa garantia solo se comprobaba por inspeccion manual.

    Los tests son estructurales: leen `docker-compose.yml` (parseado como YAML,
    no por substring ciego) y `docs/n8n-workflow-guide.md`. No levantan servicios.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
WORKFLOW_GUIDE = REPO_ROOT / "docs" / "n8n-workflow-guide.md"

# URL exacta que debe consumir el backend para notificar la clasificacion.
EXPECTED_WEBHOOK_URL = "http://n8n:5678/webhook/notificacion-clasificacion"

# Ruta del webhook dedicado (NO debe ser el webhook de alta).
DEDICATED_WEBHOOK_PATH = "notificacion-clasificacion"
ALTA_WEBHOOK_PATH = "incidente-web"


def _load_compose() -> dict:
    return yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))


def test_compose_backend_points_n8n_webhook_to_dedicated_route():
    """`N8N_WEBHOOK_URL` del backend apunta a la ruta dedicada de notificacion."""
    compose = _load_compose()
    environment = compose["services"]["backend"]["environment"]
    webhook_url = environment.get("N8N_WEBHOOK_URL")

    assert webhook_url == EXPECTED_WEBHOOK_URL, (
        "El backend debe notificar a la ruta dedicada "
        f"{EXPECTED_WEBHOOK_URL!r}; valor actual: {webhook_url!r}"
    )
    assert DEDICATED_WEBHOOK_PATH in webhook_url, (
        f"N8N_WEBHOOK_URL debe contener la ruta {DEDICATED_WEBHOOK_PATH!r}"
    )
    assert ALTA_WEBHOOK_PATH not in webhook_url, (
        "N8N_WEBHOOK_URL no debe apuntar al webhook de alta "
        f"({ALTA_WEBHOOK_PATH!r}): expondria el bucle backend -> N8N -> backend"
    )


def test_workflow_guide_documents_dedicated_notification_coupling():
    """La guia del workflow documenta el acoplamiento al webhook dedicado."""
    guide = WORKFLOW_GUIDE.read_text(encoding="utf-8")

    assert DEDICATED_WEBHOOK_PATH in guide, (
        f"docs/n8n-workflow-guide.md debe documentar el webhook "
        f"{DEDICATED_WEBHOOK_PATH!r}"
    )
    assert "N8N_WEBHOOK_URL" in guide, (
        "docs/n8n-workflow-guide.md debe documentar la variable "
        "N8N_WEBHOOK_URL que acopla el backend al webhook dedicado"
    )
    assert ALTA_WEBHOOK_PATH in guide, (
        "docs/n8n-workflow-guide.md debe contrastar la ruta dedicada con el "
        f"webhook de alta {ALTA_WEBHOOK_PATH!r}"
    )
