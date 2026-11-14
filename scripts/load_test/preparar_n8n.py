"""Prepara el N8N del perfil ``corpus`` para el test de carga (c-218).

Importa y activa en ``n8n-corpus`` una copia de costo cero de
``n8n/workflow.json`` (NO modifica el archivo versionado): reutiliza la
transformacion del dry-run (login con las credenciales locales del operador,
nodos de canales pagos removidos, ``webhookId`` estable) y reapunta el login a
``backend-corpus``. Solo queda cableado el canal web.

Uso (con el perfil corpus ya levantado, ver README.md):
    python scripts/load_test/preparar_n8n.py
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI))
sys.path.insert(0, str(_AQUI.parent / "dry_run"))

import dry_run  # noqa: E402  (reutiliza _workflow_for_dry_run)
from load_test import COMPOSE, _REPO_ROOT  # noqa: E402

CONTENEDOR = "mesa_local-n8n-corpus-1"
LOGIN_BACKEND = "http://backend:8000/api/v1/auth/login"
LOGIN_CORPUS = "http://backend-corpus:8000/api/v1/auth/login"


def _compose(*args, entrada=None, timeout=180):
    return subprocess.run(
        [*COMPOSE, *args], capture_output=True, text=True, encoding="utf-8", errors="replace", input=entrada,
        timeout=timeout, cwd=str(_REPO_ROOT),
    )


def flujo_para_corpus(usuario, clave):
    flujo, _ = dry_run._workflow_for_dry_run(usuario, clave)
    for nodo in flujo["nodes"]:
        if nodo.get("name") == "Login operador":
            nodo["parameters"]["url"] = LOGIN_CORPUS
    return flujo


def _esperar_webhook(url, espera):
    limite = time.time() + espera
    while time.time() < limite:
        try:
            urllib.request.urlopen(url, timeout=5)
            return True
        except urllib.error.HTTPError:
            return True  # respondio (p. ej. 404/405): el proceso esta arriba
        except Exception:  # noqa: BLE001
            time.sleep(3)
    return False


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--username", default=os.environ.get("LOAD_TEST_USERNAME", "admin"))
    p.add_argument("--password", default=os.environ.get("LOAD_TEST_PASSWORD", "admin123"))
    p.add_argument("--n8n-url", default="http://127.0.0.1:5679")
    args = p.parse_args(argv)

    flujo = flujo_para_corpus(args.username, args.password)
    # La copia lleva las credenciales inline: vive en un temporal FUERA del repo
    # y se borra siempre.
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "workflow.load-test.json"
        copia.write_text(json.dumps(flujo, ensure_ascii=False), encoding="utf-8")
        cp = subprocess.run(
            ["docker", "cp", str(copia), CONTENEDOR + ":/tmp/workflow.load-test.json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if cp.returncode != 0:
            print("no se pudo copiar el flujo: " + cp.stderr.strip()[-200:], file=sys.stderr)
            return 1
    imp = _compose("exec", "-T", "n8n-corpus", "n8n", "import:workflow", "--input=/tmp/workflow.load-test.json")
    if imp.returncode != 0:
        print("import fallido: " + (imp.stderr or imp.stdout).strip()[-300:], file=sys.stderr)
        return 1
    wid = dry_run.WORKFLOW_ID
    _compose("exec", "-T", "n8n-corpus", "n8n", "update:workflow", "--id=" + wid, "--active=true")
    pub = _compose("exec", "-T", "n8n-corpus", "n8n", "publish:workflow", "--id=" + wid)
    if pub.returncode != 0:
        print("publish fallido: " + (pub.stderr or pub.stdout).strip()[-300:], file=sys.stderr)
        return 1
    # Reinicio SOLO del servicio n8n-corpus para registrar el webhook.
    if _compose("restart", "n8n-corpus").returncode != 0:
        print("no reinicio n8n-corpus", file=sys.stderr)
        return 1
    if not _esperar_webhook(args.n8n_url + "/webhook/incidente-web", 120):
        print("n8n-corpus no volvio tras el reinicio", file=sys.stderr)
        return 1
    print("flujo web activo en n8n-corpus (id=%s)" % wid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
