"""TLS edge verification for the reference deployment (c-140, section 7).

Two layers:

* **Pure evaluators** — deterministic, side-effect-free: they take an already
  observed status, header map, fingerprint or ``docker compose config`` service
  tree and return a ``Check``. The harness suite exercises them offline.
* **Probes** — thin I/O wrappers over the standard library (``ssl``, ``socket``,
  ``http.client``) that produce the observations the evaluators judge. Identity
  is always verified: by a trust anchor (``openssl/mesa.crt``) or, when the
  platform rejects the self-signed leaf as an anchor, by SHA-256 fingerprint.
  ``CERT_NONE`` is never used to accept a connection.

The group targets the reference deployment only (the versioned compose +
nginx.conf lifted with ephemeral self-signed certificates); it never bypasses
anti-bot controls and never touches the operational instance.
"""

from __future__ import annotations

import hashlib
import http.client
import re
import socket
import ssl
from pathlib import Path

from checks import Check, failing, passing, pending

# ── Check names ──────────────────────────────────────────────────────────────

CHECK_VERSION_13 = "tls:handshake-1.3"
CHECK_VERSION_12 = "tls:handshake-1.2"
CHECK_IDENTITY = "tls:identity"
CHECK_REDIRECT = "tls:redirect"
CHECK_HEADERS = "tls:headers"
CHECK_SERVER_HEADER = "tls:server-header"
CHECK_UNKNOWN_HOST = "tls:unknown-host"
CHECK_REJECT_11 = "tls:reject-1.1"
CHECK_EXPOSURE = "tls:exposure"

HSTS_VALUE = "max-age=31536000; includeSubDomains"
REQUIRED_SECURITY_HEADERS = (
    ("X-Content-Type-Options", "x-content-type-options"),
    ("X-Frame-Options", "x-frame-options"),
    ("Referrer-Policy", "referrer-policy"),
    ("Permissions-Policy", "permissions-policy"),
)
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _lower_headers(headers) -> dict:
    return {str(key).lower(): value for key, value in (headers or {}).items()}


# ── Pure evaluators ──────────────────────────────────────────────────────────


def evaluate_version(name: str, observed: str | None, expected: str) -> Check:
    """Assert the negotiated protocol version equals the expected one."""
    if observed is None:
        return failing(
            name,
            f"no se pudo negociar {expected}",
            "check the nginx ssl_protocols directive and the certificate mount",
        )
    if observed != expected:
        return failing(
            name,
            f"version negociada={observed!r}, esperada={expected!r}",
            "align nginx ssl_protocols with the expected TLS versions",
        )
    return passing(name, f"handshake negociado en {observed}")


def evaluate_identity(presented_fingerprint: str | None, expected_fingerprint: str | None) -> Check:
    """Assert the presented certificate matches the generated one (SHA-256)."""
    if not presented_fingerprint:
        return failing(
            CHECK_IDENTITY,
            "no se obtuvo la huella del certificado presentado",
            "verify the TLS handshake completes and the certificate is readable",
        )
    if expected_fingerprint and presented_fingerprint.lower() != expected_fingerprint.lower():
        return failing(
            CHECK_IDENTITY,
            f"huella presentada={presented_fingerprint[:16]}... != generada={expected_fingerprint[:16]}...",
            "the served certificate differs from openssl/mesa.crt; regenerate certs and restart nginx",
        )
    return passing(CHECK_IDENTITY, "el certificado presentado coincide con openssl/mesa.crt (SHA-256)")


def evaluate_redirect(status, headers, expected_location: str) -> Check:
    """Assert HTTP->HTTPS 301 preserving path+query and WITHOUT HSTS."""
    lowered = _lower_headers(headers)
    if status != 301:
        return failing(
            CHECK_REDIRECT,
            f"esperado 301, recibido {status}",
            "the HTTP server block must `return 301 https://$host$request_uri`",
        )
    location = lowered.get("location", "")
    if location != expected_location:
        return failing(
            CHECK_REDIRECT,
            f"Location={location!r}, esperado {expected_location!r}",
            "the redirect must preserve path and query string",
        )
    if "strict-transport-security" in lowered:
        return failing(
            CHECK_REDIRECT,
            "la respuesta HTTP trae Strict-Transport-Security (no debe)",
            "HSTS must only be emitted on the 443 server block",
        )
    return passing(CHECK_REDIRECT, f"301 a {location} sin HSTS")


def evaluate_security_headers(headers) -> Check:
    """Assert the exact HSTS value and the presence of the security headers."""
    lowered = _lower_headers(headers)
    hsts = lowered.get("strict-transport-security")
    if hsts != HSTS_VALUE:
        return failing(
            CHECK_HEADERS,
            f"Strict-Transport-Security={hsts!r}, esperado {HSTS_VALUE!r}",
            "set the exact HSTS header in the 443 server block",
        )
    missing = [display for display, key in REQUIRED_SECURITY_HEADERS if not lowered.get(key)]
    if missing:
        return failing(
            CHECK_HEADERS,
            f"faltan cabeceras de seguridad: {missing}",
            "add the missing security headers to the 443 server block",
        )
    return passing(CHECK_HEADERS, "HSTS exacto y cabeceras de seguridad presentes")


def evaluate_server_header(headers) -> Check:
    """Assert the Server header carries no version number."""
    server = str(_lower_headers(headers).get("server", ""))
    if re.search(r"\d+\.\d+", server):
        return failing(
            CHECK_SERVER_HEADER,
            f"la cabecera Server expone version: {server!r}",
            "set 'server_tokens off' in nginx.conf",
        )
    return passing(CHECK_SERVER_HEADER, f"Server sin version ({server or 'ausente'})")


def evaluate_unknown_host(outcome) -> Check:
    """Assert an unknown Host closes the connection with no HTTP response (444)."""
    if outcome is None:
        return passing(CHECK_UNKNOWN_HOST, "conexion cerrada sin respuesta (catch-all 444)")
    return failing(
        CHECK_UNKNOWN_HOST,
        f"se obtuvo respuesta HTTP {outcome} para un Host desconocido",
        "the catch-all default_server must `return 444`",
    )


def evaluate_tls11_rejection(offerable: bool, error: str | None) -> Check:
    """Assert TLS 1.1 is rejected; PENDING if the client cannot offer it."""
    if not offerable:
        return pending(
            CHECK_REJECT_11,
            "el cliente local no puede ofrecer TLS 1.1; no se puede probar el rechazo",
            "run on a platform whose OpenSSL can offer TLS 1.1, or document the limitation",
        )
    if error:
        return passing(CHECK_REJECT_11, f"el handshake TLS 1.1 fue rechazado ({error})")
    return failing(
        CHECK_REJECT_11,
        "el servidor acepto un handshake TLS 1.1",
        "restrict ssl_protocols to TLSv1.2 TLSv1.3",
    )


def _port_entry(entry) -> tuple[str | None, int | None]:
    """Normalize a compose port entry to (host_ip, container_port).

    Accepts both the YAML string form (``"80:80"``, ``"127.0.0.1:5433:5432"``)
    and the ``docker compose config`` dict form (``{"target": 80, "published":
    "80"}`` / with ``host_ip``).
    """
    if isinstance(entry, dict):
        host_ip = str(entry.get("host_ip", "") or "")
        target = entry.get("target")
        return host_ip or None, target if isinstance(target, int) else None
    parts = str(entry).split(":")
    if len(parts) == 2:
        return None, int(parts[1]) if parts[1].isdigit() else None
    if len(parts) == 3:
        return parts[0], int(parts[1]) if parts[1].isdigit() else None
    return None, None


def evaluate_edge_exposure(services: dict) -> Check:
    """Assert nginx is the only service published outside loopback (80/443)."""
    offenders = []
    for name, service in (services or {}).items():
        for entry in (service or {}).get("ports", []) or []:
            host_ip, target = _port_entry(entry)
            if host_ip in LOOPBACK_HOSTS:
                continue
            if name == "nginx" and target in (80, 443):
                continue
            offenders.append(f"{name}:{entry}")
    if offenders:
        return failing(
            CHECK_EXPOSURE,
            f"publicaciones fuera de loopback no permitidas: {offenders}",
            "only nginx may publish 80/443; bind the rest to 127.0.0.1",
        )
    return passing(CHECK_EXPOSURE, "solo nginx publica fuera de loopback (80/443)")


# ── Probes (standard library only) ───────────────────────────────────────────


def fingerprint_from_der(der: bytes) -> str:
    return hashlib.sha256(der).hexdigest()


def cert_fingerprint_from_file(path) -> str:
    """SHA-256 fingerprint (hex) of a PEM certificate file."""
    pem = Path(path).read_text(encoding="utf-8")
    return fingerprint_from_der(ssl.PEM_cert_to_DER_cert(pem))


def verify_context(trust_anchor=None) -> ssl.SSLContext:
    """A verifying client context, optionally anchored on the generated cert."""
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    if trust_anchor is not None:
        context.load_verify_locations(cafile=str(trust_anchor))
    return context


def negotiate(host, port, minimum, maximum, trust_anchor=None, timeout=10):
    """Return (version_name, sha256_fingerprint) for a verified handshake.

    Verifies identity by trust anchor; if the platform rejects the self-signed
    leaf as an anchor, re-verifies the fetched certificate as ``cadata`` and
    reports the SHA-256 fingerprint for the identity check.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = minimum
    context.maximum_version = maximum
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    if trust_anchor is not None:
        context.load_verify_locations(cafile=str(trust_anchor))
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                der = ssock.getpeercert(binary_form=True)
                return ssock.version(), fingerprint_from_der(der)
    except ssl.SSLCertVerificationError:
        pem = ssl.get_server_certificate((host, port))
        fingerprint = fingerprint_from_der(ssl.PEM_cert_to_DER_cert(pem))
        fallback = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        fallback.minimum_version = minimum
        fallback.maximum_version = maximum
        fallback.check_hostname = True
        fallback.verify_mode = ssl.CERT_REQUIRED
        fallback.load_verify_locations(cadata=pem)
        try:
            with socket.create_connection((host, port), timeout=timeout) as sock:
                with fallback.wrap_socket(sock, server_hostname=host) as ssock:
                    return ssock.version(), fingerprint
        except ssl.SSLError:
            return None, fingerprint


def http_get(host, port, path, *, tls=False, context=None, timeout=10):
    """Return (status, headers_dict, body) for one GET, without following redirects."""
    if tls:
        connection = http.client.HTTPSConnection(
            host, port, timeout=timeout, context=context or verify_context()
        )
    else:
        connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        connection.request("GET", path, headers={"Host": host})
        response = connection.getresponse()
        headers = {key: value for key, value in response.getheaders()}
        body = response.read().decode("utf-8", "replace")
        return response.status, headers, body
    finally:
        connection.close()


def probe_unknown_host(host, port, trust_anchor=None, timeout=10):
    """Return the HTTP status for an unknown Host, or None if the connection closed."""
    connection = http.client.HTTPSConnection(
        host, port, timeout=timeout, context=verify_context(trust_anchor)
    )
    try:
        connection.request("GET", "/", headers={"Host": "unknown.invalid"})
        response = connection.getresponse()
        return response.status
    except Exception:  # noqa: BLE001 - a closed connection is the expected outcome
        return None
    finally:
        connection.close()


def probe_tls11(host, port, trust_anchor=None, timeout=10):
    """Return (offerable, error). ``offerable`` False when the client cannot offer 1.1."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_1
    context.maximum_version = ssl.TLSVersion.TLSv1_1
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    if trust_anchor is not None:
        context.load_verify_locations(cafile=str(trust_anchor))
    # Lower the security level so the protocol can actually be offered.
    context.set_ciphers("DEFAULT@SECLEVEL=0")
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host):
                return True, None  # accepted -> violation
    except ssl.SSLError as error:
        message = str(error)
        if "NO_PROTOCOLS_AVAILABLE" in message.upper():
            return False, message
        return True, message
    except OSError as error:
        return True, f"{type(error).__name__}: {error}"
