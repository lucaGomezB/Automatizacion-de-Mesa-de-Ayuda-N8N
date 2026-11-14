"""Arnes de carga multicanal (c-218).

Mide la capacidad del tramo compartido donde convergen los canales de entrada
(backend ``POST /api/v1/incidentes/`` y webhook web de N8N) bajo concurrencia
creciente, de forma reproducible y de costo cero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import socket
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Clave ficticia inyectada por compose.load-test.yml (capa 1 del costo cero).
DUMMY_GEMINI_API_KEY = "load-test-dummy-gemini-key-not-real"  # gitleaks:allow

ETAPA_DETERMINISTICA = "deterministic"
CANAL_WEB_ID = 2  # formulario web (catalogo canal_origen, migracion 001)

_EPS = 1e-9

CONSTANTES = {
    "niveles": (1, 5, 10, 20),
    "solicitudes_por_nivel": 40,
    "repeticiones": 3,
    "techo_p95_ms": 5000.0,
    "tolerancia_throughput": 0.10,
    "tasa_error_max": 0.0,
    "control_escalado_max": 20.0,
}


def percentiles(latencias, qs):
    """Percentiles por interpolacion lineal entre rangos (posicion (n-1)*q/100)."""
    if not latencias:
        raise ValueError("no hay latencias para calcular percentiles")
    ordenadas = sorted(float(x) for x in latencias)
    ultimo = len(ordenadas) - 1
    resultado = {}
    for q in qs:
        posicion = ultimo * q / 100.0
        inferior = math.floor(posicion)
        superior = min(inferior + 1, ultimo)
        fraccion = posicion - inferior
        resultado[q] = ordenadas[inferior] + fraccion * (
            ordenadas[superior] - ordenadas[inferior]
        )
    return resultado


def throughput(n, segundos):
    if segundos <= 0:
        raise ValueError("la duracion debe ser positiva")
    return n / segundos


def tasa_error(ok, total):
    if total <= 0:
        raise ValueError("el total de solicitudes debe ser positivo")
    return (total - ok) / total


def evaluar_criterio(niveles, constantes=None):
    """Veredicto de tres vias sobre las metricas por nivel (design D6).

    Cada nivel: ``concurrencia``, ``p95_ms``, ``throughput_rps``, ``tasa_error``
    y ``completo``. El control de escalado es secundario: se informa, no decide.
    """
    constantes = constantes or CONSTANTES
    esperados = tuple(constantes["niveles"])
    if not niveles or any(not n["completo"] for n in niveles):
        return _no_concluyente("corrida incompleta")
    if tuple(n["concurrencia"] for n in niveles) != esperados:
        return _no_concluyente(
            "niveles distintos de los prerregistrados %s" % (list(esperados),)
        )
    violaciones = []
    anterior = None
    for nivel in niveles:
        c = nivel["concurrencia"]
        if nivel["tasa_error"] > constantes["tasa_error_max"]:
            violaciones.append({"concurrencia": c, "condicion": "tasa_error"})
        if nivel["p95_ms"] > constantes["techo_p95_ms"]:
            violaciones.append({"concurrencia": c, "condicion": "p95_techo"})
        if anterior is not None:
            piso = anterior["throughput_rps"] * (1 - constantes["tolerancia_throughput"])
            if nivel["throughput_rps"] < piso - _EPS:
                violaciones.append({"concurrencia": c, "condicion": "throughput"})
        anterior = nivel
    base = niveles[0]["p95_ms"]
    razon = niveles[-1]["p95_ms"] / base if base > 0 else math.inf
    return {
        "veredicto": "no sostenida" if violaciones else "sostenida",
        "motivo": "",
        "violaciones": violaciones,
        "control_escalado": {
            "razon": razon,
            "cumple": razon <= constantes["control_escalado_max"],
        },
    }


def _no_concluyente(motivo):
    return {
        "veredicto": "no concluyente",
        "motivo": motivo,
        "violaciones": [],
        "control_escalado": None,
    }


def veredicto_global(por_capa):
    """Combina las capas: no sostenida domina; luego no concluyente."""
    valores = set(por_capa.values())
    if "no sostenida" in valores:
        return "no sostenida"
    if "no concluyente" in valores:
        return "no concluyente"
    return "sostenida"


# ── armado de solicitudes ─────────────────────────────────────────────────────


def origen_id(prefijo, indice):
    """``origen_message_id`` unico por solicitud (evita la idempotencia)."""
    return "%s-%06d" % (prefijo, indice)


def payload(caso, origen_message_id, canal_origen_id=CANAL_WEB_ID):
    """Cuerpo de ``POST /api/v1/incidentes/`` (``IncidenteCreate``)."""
    return {
        "descripcion": caso["descripcion"],
        "prioridad": "media",
        "canal_origen_id": canal_origen_id,
        "origen_message_id": origen_message_id,
    }


def payload_webhook(caso, origen_message_id):
    """Cuerpo del webhook web de N8N (el canal lo marca el workflow)."""
    return {
        "descripcion": caso["descripcion"],
        "prioridad": "media",
        "origen_message_id": origen_message_id,
    }


# ── cliente HTTP (biblioteca estandar) ────────────────────────────────────────


def _es_timeout(exc):
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return True
    return isinstance(exc, urllib.error.URLError) and isinstance(
        exc.reason, (socket.timeout, TimeoutError)
    )


def _parsear(datos):
    try:
        return json.loads(datos.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _solicitar(metodo, url, cuerpo, headers, timeout):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    cabeceras = {"Content-Type": "application/json", **(headers or {})}
    pedido = urllib.request.Request(url, data=datos, headers=cabeceras, method=metodo)
    inicio = time.perf_counter()
    status, respuesta, error = None, None, None
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resp:
            status = resp.status
            respuesta = _parsear(resp.read())
    except urllib.error.HTTPError as exc:
        status = exc.code
        respuesta = _parsear(exc.read())
    except Exception as exc:  # noqa: BLE001 - toda falla de red cuenta como error
        error = "timeout" if _es_timeout(exc) else type(exc).__name__
    latencia = (time.perf_counter() - inicio) * 1000.0
    return {"status": status, "latencia_ms": latencia, "cuerpo": respuesta, "error": error}


def post_json(url, cuerpo, headers, timeout):
    return _solicitar("POST", url, cuerpo, headers, timeout)


def get_json(url, headers, timeout):
    return _solicitar("GET", url, None, headers, timeout)


def es_ok(resultado):
    return resultado["error"] is None and resultado["status"] is not None and 200 <= resultado["status"] < 300


# ── disparo concurrente y metricas por nivel ─────────────────────────────────


def disparar(enviar, casos, concurrencia, n_solicitudes, prefijo, construir=payload):
    """Dispara ``n_solicitudes`` con un pool de ``concurrencia`` hilos.

    ``enviar(cuerpo)`` devuelve el dict de ``post_json``. Las descripciones del
    fixture rotan; cada solicitud lleva un ``origen_message_id`` distinto.
    """

    def una(indice):
        caso = casos[indice % len(casos)]
        omid = origen_id(prefijo, indice)
        resultado = enviar(construir(caso, omid))
        resultado["origen_message_id"] = omid
        resultado["caso_id"] = caso.get("id")
        resultado["descripcion"] = caso["descripcion"]
        return resultado

    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrencia) as pool:
        resultados = list(pool.map(una, range(n_solicitudes)))
    segundos = time.perf_counter() - inicio
    return {"resultados": resultados, "segundos": segundos}


def metricas_nivel(repeticiones):
    """Metricas agregadas (agrupando las repeticiones) de un nivel."""
    resultados = [r for rep in repeticiones for r in rep["resultados"]]
    total = len(resultados)
    ok = sum(1 for r in resultados if es_ok(r))
    segundos = sum(rep["segundos"] for rep in repeticiones)
    latencias = [r["latencia_ms"] for r in resultados]
    pct = percentiles(latencias, [50, 95, 99])
    return {
        "total": total,
        "ok": ok,
        "tasa_error": tasa_error(ok, total),
        "p50_ms": pct[50],
        "p95_ms": pct[95],
        "p99_ms": pct[99],
        "media_ms": sum(latencias) / total,
        "throughput_rps": throughput(total, segundos),
        "segundos": segundos,
    }


def consultar_detalle(base_url, token, incidente_id, timeout):
    """``latencia_e2e_ms`` del detalle y etapas del registro de clasificacion."""
    cabeceras = {"Authorization": "Bearer " + token}
    detalle = get_json("%s/api/v1/incidentes/%s" % (base_url, incidente_id), cabeceras, timeout)
    clasif = get_json(
        "%s/api/v1/clasificaciones/incidente/%s" % (base_url, incidente_id), cabeceras, timeout
    )
    cuerpo = detalle["cuerpo"] if isinstance(detalle["cuerpo"], dict) else {}
    logs = clasif["cuerpo"] if isinstance(clasif["cuerpo"], list) else []
    return {
        "latencia_e2e_ms": cuerpo.get("latencia_e2e_ms"),
        "etapas": [log.get("etapa") for log in logs],
    }


# ── fixture y verificacion de no escalada ────────────────────────────────────


class EscaladaDetectada(RuntimeError):
    """Una solicitud del fixture no se resolvio en la etapa determinística."""


def cargar_fixture(ruta):
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    casos = datos["casos"]
    for caso in casos:
        if len(caso["descripcion"]) < 10:
            raise ValueError(
                "caso %s: descripcion menor al minimo de 10 caracteres" % caso["id"]
            )
    if len({c["id"] for c in casos}) != len(casos):
        raise ValueError("ids de caso duplicados en el fixture")
    return casos


def hash_fixture(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def verificar_no_escalada(descripcion, etapas):
    """Falla de forma ruidosa si el incidente no quedo solo en la etapa determinística."""
    if etapas == [ETAPA_DETERMINISTICA]:
        return
    observada = next((e for e in etapas if e != ETAPA_DETERMINISTICA), None)
    if observada is None:
        observada = "sin registro" if not etapas else ETAPA_DETERMINISTICA + " (repetida)"
    raise EscaladaDetectada(
        "la descripcion %r no se resolvio solo en la etapa determinística: etapa observada %s"
        % (descripcion, observada)
    )


# ── guarda de costo cero ─────────────────────────────────────────────────────


class GuardaCostoError(RuntimeError):
    """La guarda de costo cero no esta en efecto: no se envia ninguna solicitud."""


def verificar_costo_cero(env):
    """Exige clave Gemini ficticia y presupuesto de la guarda exactamente cero."""
    if env.get("GEMINI_API_KEY") != DUMMY_GEMINI_API_KEY:
        raise GuardaCostoError(
            "la GEMINI_API_KEY efectiva del backend no es la ficticia del override"
        )
    presupuesto = env.get("COST_GUARD_BUDGET_USD")
    try:
        cero = presupuesto is not None and float(presupuesto) == 0.0
    except ValueError:
        cero = False
    if not cero:
        raise GuardaCostoError(
            "COST_GUARD_BUDGET_USD efectivo no es cero (valor observado: %r)" % (presupuesto,)
        )


# ── reporte determinista ─────────────────────────────────────────────────────


class SecretoEnReporte(RuntimeError):
    """El reporte contendria un secreto: no se escribe."""


def renderizar_json(datos):
    return json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def renderizar_markdown(datos):
    lineas = [
        "# Test de carga multicanal",
        "",
        "- Commit: %s" % datos["commit"],
        "- Fecha UTC: %s" % datos["fecha_utc"],
        "- Version de N8N: %s" % datos["n8n_version"],
        "- Perfil: %s" % datos["perfil"],
        "- SHA-256 del fixture: %s" % datos["fixture_sha256"],
        "- Veredicto: **%s**" % datos["veredicto"],
        "",
        "## Exclusiones declaradas",
        "",
    ]
    lineas += ["- %s" % e for e in datos["exclusiones"]]
    for nombre, capa in sorted(datos["capas"].items()):
        lineas += [
            "",
            "## Capa %s (veredicto: %s)" % (nombre, capa["criterio"]["veredicto"]),
            "",
            "| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Tasa de error |",
            "|---|---|---|---|---|---|",
        ]
        for n in capa["niveles"]:
            lineas.append(
                "| %d | %.1f | %.1f | %.1f | %.2f | %.4f |"
                % (n["concurrencia"], n["p50_ms"], n["p95_ms"], n["p99_ms"], n["throughput_rps"], n["tasa_error"])
            )
        for v in capa["criterio"].get("violaciones", []):
            lineas.append("")
            lineas.append("Violacion: nivel %s, condicion %s." % (v["concurrencia"], v["condicion"]))
    return "\n".join(lineas) + "\n"


def escribir_reporte(ruta_json, datos, secretos=()):
    """Escribe el JSON y su resumen ``.md`` (LF, UTF-8 sin BOM, sin secretos)."""
    contenido_json = renderizar_json(datos)
    contenido_md = renderizar_markdown(datos)
    for secreto in secretos:
        if secreto and (secreto in contenido_json or secreto in contenido_md):
            raise SecretoEnReporte("el reporte contendria un secreto; no se escribe")
    ruta_json = Path(ruta_json)
    ruta_json.write_bytes(contenido_json.encode("utf-8"))
    ruta_json.with_suffix(".md").write_bytes(contenido_md.encode("utf-8"))


# ── punto de entrada ─────────────────────────────────────────────────────────


_REPO_ROOT = Path(__file__).resolve().parents[2]
# Mismo proyecto de Compose de nombre fijo; NUNCA se pasa `-p` (MLC-007).
COMPOSE = [
    "docker", "compose",
    "-f", "docker-compose.yml",
    "-f", "scripts/load_test/compose.load-test.yml",
    "--profile", "corpus",
]


def leer_env_contenedor(servicio):
    """Variables efectivas dentro del contenedor del backend (``printenv``)."""
    salida = subprocess.run(
        [*COMPOSE, "exec", "-T", servicio, "printenv"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, cwd=str(_REPO_ROOT),
    ).stdout
    return dict(l.split("=", 1) for l in salida.splitlines() if "=" in l)


EXCLUSIONES = [
    "correo: sondeo IMAP por minuto, no apto para inyeccion concurrente; la convergencia en POST /api/v1/incidentes/ es agnostica al canal",
    "telefonia: canal pago (Twilio); no se invoca ni se mide",
]
RUTA_FIXTURE = Path(__file__).resolve().parent / "fixture_descripciones.json"
WEBHOOK_WEB = "/webhook/incidente-web"


def obtener_commit():
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def obtener_version_n8n(args):
    try:
        salida = subprocess.run(
            [*COMPOSE, "exec", "-T", "n8n-corpus", "n8n", "--version"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, cwd=str(_REPO_ROOT),
        ).stdout.strip()
        return salida.splitlines()[-1] if salida else "desconocido"
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def _incidente_id(resultado):
    cuerpo = resultado["cuerpo"]
    if isinstance(cuerpo, dict):
        return cuerpo.get("incidente_id", cuerpo.get("id"))
    return None


def _nivel_reporte(concurrencia, repeticiones, detalles, esperadas):
    m = metricas_nivel(repeticiones)
    e2e = [d["latencia_e2e_ms"] for d in detalles if d["latencia_e2e_ms"] is not None]
    pct = percentiles(e2e, [50, 95]) if e2e else {50: None, 95: None}
    m.update(
        concurrencia=concurrencia,
        completo=m["total"] == esperadas,
        e2e_n=len(e2e),
        e2e_p50_ms=pct[50],
        e2e_p95_ms=pct[95],
        verificadas_deterministicas=len(detalles),
        repeticiones=[
            {
                "total": len(r["resultados"]),
                "ok": sum(1 for x in r["resultados"] if es_ok(x)),
                "segundos": r["segundos"],
                "throughput_rps": throughput(len(r["resultados"]), r["segundos"]),
                "p95_ms": percentiles([x["latencia_ms"] for x in r["resultados"]], [95])[95],
            }
            for r in repeticiones
        ],
    )
    return m


def _verificar_nivel(base_url, token, repeticiones, timeout):
    """Detalle y etapa de cada incidente creado; falla si alguno escalo."""
    pares = [
        (_incidente_id(r), r["descripcion"])
        for rep in repeticiones for r in rep["resultados"] if es_ok(r)
    ]

    def una(par):
        incidente_id, descripcion = par
        if incidente_id is None:
            raise EscaladaDetectada("respuesta sin identificador de incidente para %r" % descripcion)
        detalle = consultar_detalle(base_url, token, incidente_id, timeout)
        verificar_no_escalada(descripcion, detalle["etapas"])
        return detalle

    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(una, pares))


def correr_carga(args):
    casos = cargar_fixture(args.fixture)
    niveles = [int(x) for x in str(args.niveles).split(",")]
    login = post_json(
        args.backend_url + "/api/v1/auth/login",
        {"username": args.username, "password": args.password},
        None,
        args.timeout,
    )
    token = login["cuerpo"].get("access_token") if isinstance(login["cuerpo"], dict) else None
    if login["status"] != 200 or not token:
        print("ABORTADO: login del operador fallido (estado %s)" % login["status"], file=sys.stderr)
        return 5
    cabeceras = {"Authorization": "Bearer " + token}
    corrida = os.urandom(4).hex()
    destinos = {
        "backend": (
            args.backend_url,
            lambda cuerpo: post_json(args.backend_url + "/api/v1/incidentes/", cuerpo, cabeceras, args.timeout),
            payload,
        ),
        "n8n": (
            args.n8n_url,
            lambda cuerpo: post_json(args.n8n_url + WEBHOOK_WEB, cuerpo, None, args.timeout),
            payload_webhook,
        ),
    }
    capas = {}
    try:
        for nombre, (base, enviar, construir) in destinos.items():
            filas = []
            for c in niveles:
                repeticiones = [
                    disparar(enviar, casos, c, args.solicitudes, "load-%s-%s-c%d-r%d" % (corrida, nombre, c, r), construir)
                    for r in range(args.repeticiones)
                ]
                detalles = _verificar_nivel(args.backend_url, token, repeticiones, args.timeout)
                filas.append(_nivel_reporte(c, repeticiones, detalles, args.solicitudes * args.repeticiones))
                print("capa %s nivel %d: p95 %.1f ms, error %.4f" % (nombre, c, filas[-1]["p95_ms"], filas[-1]["tasa_error"]))
            constantes = dict(CONSTANTES, niveles=tuple(niveles))
            capas[nombre] = {"niveles": filas, "criterio": evaluar_criterio(filas, constantes)}
    except EscaladaDetectada as exc:
        print("ABORTADO (escalada): %s" % exc, file=sys.stderr)
        return 4
    por_capa = {n: c["criterio"]["veredicto"] for n, c in capas.items()}
    datos = {
        "commit": obtener_commit(),
        "fecha_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n8n_version": obtener_version_n8n(args),
        "perfil": "corpus (postgres-corpus, backend-corpus, n8n-corpus) con override de costo cero",
        "corrida_id": corrida,
        "fixture_sha256": hash_fixture(args.fixture),
        "constantes": dict(CONSTANTES, niveles=list(CONSTANTES["niveles"]),
                           solicitudes_por_nivel=args.solicitudes, repeticiones=args.repeticiones),
        "exclusiones": EXCLUSIONES,
        "capas": capas,
        "veredicto": veredicto_global(por_capa),
    }
    if args.json_out:
        escribir_reporte(args.json_out, datos, secretos=[args.password, token, DUMMY_GEMINI_API_KEY])
    print("veredicto: %s" % datos["veredicto"])
    return 0


def _parser():
    p = argparse.ArgumentParser(description="Test de carga multicanal (c-218), costo cero.")
    p.add_argument("--json-out", default=None)
    p.add_argument("--backend-url", default="http://127.0.0.1:8001")
    p.add_argument("--n8n-url", default="http://127.0.0.1:5679")
    p.add_argument("--servicio-backend", default="backend-corpus")
    p.add_argument("--username", default=os.environ.get("LOAD_TEST_USERNAME", "admin"))
    p.add_argument("--password", default=os.environ.get("LOAD_TEST_PASSWORD", "admin123"))
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--fixture", default=str(RUTA_FIXTURE))
    p.add_argument("--niveles", default=",".join(str(n) for n in CONSTANTES["niveles"]))
    p.add_argument("--solicitudes", type=int, default=CONSTANTES["solicitudes_por_nivel"])
    p.add_argument("--repeticiones", type=int, default=CONSTANTES["repeticiones"])
    return p


def main(argv=None, leer_env=None, correr=None):
    args = _parser().parse_args(argv)
    leer_env = leer_env or leer_env_contenedor
    correr = correr or correr_carga
    try:
        verificar_costo_cero(leer_env(args.servicio_backend))
    except GuardaCostoError as exc:
        print("ABORTADO (costo cero): %s" % exc, file=sys.stderr)
        return 3
    return correr(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
