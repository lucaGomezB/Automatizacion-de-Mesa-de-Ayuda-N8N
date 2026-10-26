"""
Guards estructurales del borde TLS del despliegue de referencia (c-140, bloque 1).

Verifican, leyendo SOLO artefactos versionados (`nginx/nginx.conf`,
`docker-compose.yml`, `openssl/generate-certs.{sh,ps1}`, `.gitignore`), las
invariantes del borde:

- toda directiva `ssl_protocols` acepta exactamente TLS 1.2 y TLS 1.3;
- `Strict-Transport-Security` solo aparece en bloques que escuchan 443 y nunca
  en el bloque de redireccion del puerto 80;
- el montaje de certificados y las rutas de `mesa.crt`/`mesa.key` son coherentes
  entre compose, nginx y los scripts de generacion;
- nginx no enruta hacia n8n;
- el unico servicio publicado fuera de loopback es nginx (80/443); un mapeo sin
  direccion de host cuenta como todas las interfaces;
- el comentario de cabecera de `docker-compose.yml` describe la postura real;
- los certificados/claves estan ignorados por Git y `openssl/.gitkeep` versionado.

No levantan servicios, no acceden a red y no requieren Docker: parsean los
archivos de configuracion de forma determinista.
"""

from __future__ import annotations

import copy
import re
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
NGINX_CONF_PATH = REPO_ROOT / "nginx" / "nginx.conf"
GENERATE_SH_PATH = REPO_ROOT / "openssl" / "generate-certs.sh"
GENERATE_PS1_PATH = REPO_ROOT / "openssl" / "generate-certs.ps1"
GITKEEP_PATH = REPO_ROOT / "openssl" / ".gitkeep"

EXPECTED_PROTOCOLS = "TLSv1.2 TLSv1.3"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
CERT_MOUNT = "./openssl:/etc/nginx/certs:ro"


# ── Pure parsing helpers (reused by the mutation triangulation) ──────────────


def _strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        idx = line.find("#")
        lines.append(line[:idx] if idx != -1 else line)
    return "\n".join(lines)


def server_blocks(text: str) -> list[str]:
    """Return the body of every top-level ``server { ... }`` block."""
    cleaned = _strip_comments(text)
    blocks: list[str] = []
    cursor = 0
    while True:
        match = re.search(r"\bserver\s*\{", cleaned[cursor:])
        if not match:
            break
        start = cursor + match.end()
        depth = 1
        index = start
        while index < len(cleaned) and depth > 0:
            if cleaned[index] == "{":
                depth += 1
            elif cleaned[index] == "}":
                depth -= 1
            index += 1
        blocks.append(cleaned[start : index - 1])
        cursor = index
    return blocks


def ssl_protocols_directives(text: str) -> list[str]:
    """Return the value of every ``ssl_protocols`` directive (whitespace-normalized)."""
    return [re.sub(r"\s+", " ", value).strip() for value in re.findall(r"ssl_protocols\s+([^;]+);", _strip_comments(text))]


def proxy_pass_targets(text: str) -> list[str]:
    return [value.strip() for value in re.findall(r"proxy_pass\s+([^;]+);", _strip_comments(text))]


def block_listens_on(block: str, port: int) -> bool:
    return re.search(rf"listen\s+(?:[^;]*?\b)?{port}\b", block) is not None


def blocks_with_hsts(text: str) -> list[str]:
    return [block for block in server_blocks(text) if "Strict-Transport-Security" in block]


def blocks_listening(text: str, port: int) -> list[str]:
    return [block for block in server_blocks(text) if block_listens_on(block, port)]


def publications_outside_loopback(services: dict) -> list[tuple[str, str]]:
    """Classify each published port: outside-loopback mappings, as (service, entry).

    A mapping without a host address (for example ``"80:80"``) publishes on ALL
    interfaces and is therefore outside loopback.
    """
    offenders: list[tuple[str, str]] = []
    for name, service in services.items():
        for entry in (service or {}).get("ports", []) or []:
            parts = str(entry).split(":")
            if len(parts) == 2:
                host_ip = None  # bare "<host>:<container>" -> all interfaces
            elif len(parts) == 3:
                host_ip = parts[0]
            else:
                continue
            if host_ip not in LOOPBACK_HOSTS:
                offenders.append((name, str(entry)))
    return offenders


def _compose_header_comment() -> str:
    """Return the leading comment block, comment markers stripped and collapsed."""
    header_lines: list[str] = []
    for line in COMPOSE_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "":
            header_lines.append("")
            continue
        if stripped.startswith("#"):
            header_lines.append(stripped.lstrip("#").strip())
            continue
        break
    return re.sub(r"\s+", " ", " ".join(header_lines)).strip()


# ── (a) ssl_protocols ────────────────────────────────────────────────────────


def test_every_ssl_protocols_directive_is_exactly_tls12_tls13():
    directives = ssl_protocols_directives(NGINX_CONF_PATH.read_text(encoding="utf-8"))
    assert directives, "nginx.conf debe declarar al menos una directiva ssl_protocols"
    for value in directives:
        assert value == EXPECTED_PROTOCOLS, (
            f"ssl_protocols debe ser exactamente {EXPECTED_PROTOCOLS!r}; hallado {value!r}"
        )


# ── (b) HSTS solo en bloques 443 ─────────────────────────────────────────────


def test_hsts_only_in_blocks_listening_on_443():
    text = NGINX_CONF_PATH.read_text(encoding="utf-8")
    for block in blocks_with_hsts(text):
        assert block_listens_on(block, 443), (
            "Strict-Transport-Security aparece en un bloque que no escucha 443"
        )


def test_port_80_redirect_block_has_no_hsts():
    text = NGINX_CONF_PATH.read_text(encoding="utf-8")
    for block in blocks_listening(text, 80):
        if block_listens_on(block, 443):
            continue  # catch-all listens on both
        assert "Strict-Transport-Security" not in block, (
            "el bloque de redireccion del puerto 80 no debe emitir HSTS"
        )


# ── (c) rutas de certificados coherentes ─────────────────────────────────────


def test_compose_mounts_openssl_read_only():
    services = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))["services"]
    volumes = [str(v) for v in services["nginx"].get("volumes", [])]
    assert CERT_MOUNT in volumes, (
        f"nginx debe montar {CERT_MOUNT!r}; hallado {volumes!r}"
    )


def test_nginx_references_mesa_crt_and_key_under_etc_nginx_certs():
    text = NGINX_CONF_PATH.read_text(encoding="utf-8")
    assert re.search(r"ssl_certificate\s+/etc/nginx/certs/mesa\.crt;", text)
    assert re.search(r"ssl_certificate_key\s+/etc/nginx/certs/mesa\.key;", text)


def test_generate_scripts_output_mesa_crt_and_key():
    for path in (GENERATE_SH_PATH, GENERATE_PS1_PATH):
        text = path.read_text(encoding="utf-8")
        assert "mesa.crt" in text and "mesa.key" in text, (
            f"{path.name} debe generar mesa.crt y mesa.key"
        )


# ── (d) nginx no enruta hacia n8n ────────────────────────────────────────────


def test_no_proxy_pass_targets_n8n():
    targets = proxy_pass_targets(NGINX_CONF_PATH.read_text(encoding="utf-8"))
    assert targets, "nginx.conf debe declarar al menos un proxy_pass"
    for target in targets:
        assert "n8n" not in target.lower(), (
            f"nginx no debe enrutar hacia n8n; hallado proxy_pass {target!r}"
        )


# ── (e) exposicion unica del borde ───────────────────────────────────────────


def test_only_nginx_publishes_outside_loopback():
    services = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))["services"]
    offenders = []
    for name, entry in publications_outside_loopback(services):
        container_port = int(str(entry).split(":")[-1])
        if name == "nginx" and container_port in (80, 443):
            continue
        offenders.append((name, entry))
    assert not offenders, (
        f"solo nginx puede publicar fuera de loopback (80/443); ofensores: {offenders}"
    )


def test_nginx_publishes_exactly_80_and_443_outside_loopback():
    services = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))["services"]
    nginx_ports = {str(p) for p in services["nginx"].get("ports", [])}
    assert {"80:80", "443:443"} <= nginx_ports, (
        f"nginx debe publicar 80 y 443; hallado {nginx_ports!r}"
    )


# ── (f) el comentario del compose describe la postura real ───────────────────


def test_compose_header_does_not_claim_80_443_are_loopback():
    header = _compose_header_comment()
    lowered = header.lower()
    assert "todos acotados a loopback" not in lowered, (
        "el comentario de cabecera afirma falsamente que TODOS los puertos "
        "(incluidos 80/443) estan acotados a loopback"
    )
    assert "nginx" in lowered and "todas las interfaces" in lowered, (
        "el comentario debe describir nginx como el unico borde publicado en "
        "todas las interfaces"
    )
    assert "postgres" in lowered and "n8n" in lowered and "loopback" in lowered, (
        "el comentario debe declarar PostgreSQL y N8N acotados a loopback"
    )


# ── (g) certificados ignorados y .gitkeep versionado ─────────────────────────


def test_generated_certificates_are_gitignored():
    result = subprocess.run(
        ["git", "check-ignore", "openssl/mesa.crt", "openssl/mesa.key"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "openssl/mesa.crt y openssl/mesa.key deben estar ignorados por Git"
    )


def test_openssl_gitkeep_is_tracked():
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "openssl/.gitkeep"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "openssl/.gitkeep debe estar versionado"


# ── TRIANGULATE (7.4): copias mutadas en memoria que el verificador rechaza ──


def _real_services() -> dict:
    return yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))["services"]


def test_bare_mapping_on_n8n_is_an_offender():
    services = copy.deepcopy(_real_services())
    services["n8n"]["ports"] = ["5678:5678"]
    assert ("n8n", "5678:5678") in publications_outside_loopback(services)


def test_zero_zero_zero_zero_postgres_is_an_offender():
    services = copy.deepcopy(_real_services())
    services["postgres"]["ports"] = ["0.0.0.0:5433:5432"]
    assert ("postgres", "0.0.0.0:5433:5432") in publications_outside_loopback(services)


def test_loopback_mapping_is_not_an_offender():
    services = {"postgres": {"ports": ["127.0.0.1:5433:5432"]}}
    assert publications_outside_loopback(services) == []


def test_tls11_protocols_mutation_is_rejected():
    mutated = NGINX_CONF_PATH.read_text(encoding="utf-8").replace(
        EXPECTED_PROTOCOLS, "TLSv1.1 TLSv1.2", 1
    )
    directives = ssl_protocols_directives(mutated)
    assert any(value != EXPECTED_PROTOCOLS for value in directives), (
        "una directiva ssl_protocols con TLSv1.1 debe ser rechazada"
    )


def test_hsts_injected_in_port_80_block_is_rejected():
    marker = "    # Redirect ALL HTTP traffic to HTTPS, preserving path and query string"
    mutated = NGINX_CONF_PATH.read_text(encoding="utf-8").replace(
        marker,
        '    add_header Strict-Transport-Security "max-age=1" always;\n' + marker,
        1,
    )
    offending = [
        block for block in blocks_with_hsts(mutated) if not block_listens_on(block, 443)
    ]
    assert offending, "HSTS dentro del bloque del puerto 80 debe ser rechazado"


def test_proxy_pass_to_n8n_is_rejected():
    mutated = NGINX_CONF_PATH.read_text(encoding="utf-8").replace(
        "proxy_pass http://backend:8000;", "proxy_pass http://n8n:5678;", 1
    )
    assert any("n8n" in target.lower() for target in proxy_pass_targets(mutated)), (
        "un proxy_pass hacia n8n debe ser rechazado"
    )
