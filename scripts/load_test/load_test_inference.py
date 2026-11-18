"""Arnes de carga multicanal CON inferencia paga (TASK B, seguimiento de c-218).

Mide, de forma REPRODUCIBLE y ACOTADA, la latencia end-to-end del tramo
compartido donde convergen los canales de entrada CUANDO una fraccion
preregistrada de solicitudes escala a Gemini. Cuantifica la contribucion de la
inferencia comparando, en el mismo nivel, el subconjunto escalado contra el
deterministico (comparacion pareada).

Separacion de caminos (regla dura):
    - El camino de COSTO CERO vive en ``load_test.py`` y NO se modifica: su
      guarda ``verificar_costo_cero`` sigue exigiendo clave ficticia y
      presupuesto exactamente cero, y aborta ante cualquier escalada.
    - Este modulo es un camino INDEPENDIENTE ("corrida paga acotada"). Reutiliza
      ``load_test`` como biblioteca (payloads, cliente HTTP, metricas, reporte) y
      aporta: guarda paga acotada, registro de etapas (permite escalada) y
      metricas de contribucion de la inferencia.

El camino pago exige confirmacion explicita (``--confirm-paid``), una clave real
(distinta de la ficticia) y un presupuesto positivo NO mayor que el tope
preregistrado. Nunca debilita la guarda de costo cero del camino por defecto.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import load_test as lt

# Clave ficticia del camino de costo cero (NO es una clave real). Se importa
# para poder RECHAZARLA de forma explicita en la guarda paga.
DUMMY_GEMINI_API_KEY = lt.DUMMY_GEMINI_API_KEY  # gitleaks:allow

ETAPA_DETERMINISTICA = lt.ETAPA_DETERMINISTICA
ETAPA_SIN_REGISTRO = "sin_registro"

_AQUI = Path(__file__).resolve().parent
_REPO_ROOT = lt._REPO_ROOT

# Precios declarados por la tesis (seccion 8, consultados 2026-10-19), en USD por
# millon de tokens. Fuente unica: evaluation/brazo_gemini_solo.PRECIOS_USD_POR_MILLON.
# La estimacion de costo del arnes es DECLARADA, no facturacion del proveedor.
PRECIO_FUENTE = (
    "precios de lista declarados por la tesis (seccion 8, consultados 2026-10-19); "
    "fuente unica evaluation/brazo_gemini_solo.py:PRECIOS_USD_POR_MILLON"
)
ESCENARIO_PRECIO_POR_DEFECTO = "introductorio"

if str(_REPO_ROOT) not in sys.path:
    sys.path.append(str(_REPO_ROOT))
try:  # fuente unica de precios; el fallback replica la tabla declarada
    from evaluation.brazo_gemini_solo import PRECIOS_USD_POR_MILLON
except Exception:  # pragma: no cover - defensa si `evaluation` no esta disponible
    PRECIOS_USD_POR_MILLON = {
        "introductorio": {"entrada": 0.75, "salida": 3.75},
        "estandar": {"entrada": 1.50, "salida": 7.50},
    }


# Constantes del criterio prerregistrado de la corrida paga. Se fijan ANTES de
# observar datos y NO se reajustan despues (ver PRERREGISTRO del modulo).
CONSTANTES_INFERENCIA = {
    "niveles": (1, 5, 10, 20),
    "solicitudes_por_nivel": 20,
    "repeticiones": 1,
    "techo_p95_ms": 5000.0,
    "tolerancia_throughput": 0.10,
    "tasa_error_max": 0.0,
    "control_escalado_max": 20.0,
    # Condicion secundaria de la corrida paga (design TASK B): el p95 del
    # subconjunto escalado no supera T=4 veces el p95 del deterministico del
    # mismo nivel.
    "tolerancia_inferencia": 4.0,
    # Tope de presupuesto autorizado (USD) y mezcla de escalada esperada del
    # fixture (fraccion de casos ambiguos). Se documentan en el reporte.
    "tope_presupuesto_usd": 1.00,
    "mezcla_escalada_esperada": 0.5,
}

OVERRIDE_INFERENCE = "scripts/load_test/compose.load-test-inference.yml"

# Mismo proyecto de Compose de nombre fijo; NUNCA se pasa `-p` (MLC-007).
COMPOSE_INFERENCE = [
    "docker", "compose",
    "-f", "docker-compose.yml",
    "-f", OVERRIDE_INFERENCE,
    "--profile", "corpus",
]

RUTA_FIXTURE_INFERENCIA = _AQUI / "fixture_descripciones_inferencia.json"


# ── guarda de la corrida paga acotada ────────────────────────────────────────


class GuardaPagaError(RuntimeError):
    """La corrida paga no esta autorizada/aceptada: no se envia ninguna solicitud."""


def verificar_corrida_paga_acotada(env, tope_usd=None, confirmado=False):
    """Exige confirmacion, clave real y presupuesto positivo acotado.

    A diferencia de la guarda de costo cero (que exige clave ficticia y
    presupuesto exactamente cero), esta guarda exige lo OPUESTO dentro de un
    tope: una clave real y un presupuesto positivo que no supere ``tope_usd``.
    Nunca cita el valor de la clave en el mensaje de error.
    """
    if not confirmado:
        raise GuardaPagaError(
            "falta la confirmacion explicita (--confirm-paid): la corrida paga "
            "no se autoriza de forma implicita"
        )
    tope = CONSTANTES_INFERENCIA["tope_presupuesto_usd"] if tope_usd is None else float(tope_usd)

    clave = env.get("GEMINI_API_KEY")
    if not clave or clave == DUMMY_GEMINI_API_KEY:
        raise GuardaPagaError(
            "la GEMINI_API_KEY efectiva no es una clave real (esta ausente o es "
            "la ficticia del camino de costo cero)"
        )

    presupuesto = env.get("COST_GUARD_BUDGET_USD")
    try:
        valor = float(presupuesto)
    except (TypeError, ValueError):
        raise GuardaPagaError(
            "COST_GUARD_BUDGET_USD efectivo no es numerico (valor observado: %r)"
            % (presupuesto,)
        )
    if valor <= 0.0:
        raise GuardaPagaError(
            "COST_GUARD_BUDGET_USD efectivo no es positivo (valor observado: %r)"
            % (presupuesto,)
        )
    if valor > tope:
        raise GuardaPagaError(
            "COST_GUARD_BUDGET_USD efectivo (%s) supera el tope autorizado (%.2f USD)"
            % (valor, tope)
        )


# ── etapa observada y contribucion de la inferencia ──────────────────────────


def etapa_observada(etapas):
    """Primera etapa distinta de la deterministica, o la deterministica si no hay."""
    if not etapas:
        return ETAPA_SIN_REGISTRO
    for etapa in etapas:
        if etapa != ETAPA_DETERMINISTICA:
            return etapa
    return ETAPA_DETERMINISTICA


def resumen_etapas(detalles):
    """Conteo por etapa observable y fraccion escalada del nivel (design TASK B)."""
    conteo = {}
    for detalle in detalles:
        etapa = detalle.get("etapa") or ETAPA_SIN_REGISTRO
        conteo[etapa] = conteo.get(etapa, 0) + 1
    total = len(detalles)
    escalados = sum(n for etapa, n in conteo.items() if etapa != ETAPA_DETERMINISTICA)
    return {
        "conteo_por_etapa": conteo,
        "total": total,
        "escalados": escalados,
        "fraccion_escalada": (escalados / total) if total else 0.0,
    }


def _p50_p95(valores):
    if not valores:
        return {"n": 0, "p50_ms": None, "p95_ms": None}
    pct = lt.percentiles(valores, [50, 95])
    return {"n": len(valores), "p50_ms": pct[50], "p95_ms": pct[95]}


def contribucion_inferencia(repeticiones, detalles):
    """Comparacion pareada del subconjunto escalado contra el deterministico.

    Usa la latencia de CLIENTE (envio -> respuesta, siempre disponible) para
    partir por etapa, y agrega la ``latencia_e2e_ms`` del servidor cuando el
    canal la instrumenta (capa N8N). La razon es ``p95(escalado)/p95(det)`` del
    mismo nivel.
    """
    etapa_por_origen = {d.get("origen_message_id"): d.get("etapa") for d in detalles}
    det_lat, esc_lat = [], []
    for rep in repeticiones:
        for resultado in rep["resultados"]:
            etapa = etapa_por_origen.get(resultado.get("origen_message_id"))
            if etapa is None:
                continue
            latencia = resultado.get("latencia_ms")
            (det_lat if etapa == ETAPA_DETERMINISTICA else esc_lat).append(latencia)

    det_e2e = [
        d["latencia_e2e_ms"]
        for d in detalles
        if d.get("etapa") == ETAPA_DETERMINISTICA and d.get("latencia_e2e_ms") is not None
    ]
    esc_e2e = [
        d["latencia_e2e_ms"]
        for d in detalles
        if d.get("etapa") != ETAPA_DETERMINISTICA and d.get("latencia_e2e_ms") is not None
    ]

    deterministico = _p50_p95(det_lat)
    escalado = _p50_p95(esc_lat)
    e2e_det = _p50_p95(det_e2e)
    e2e_esc = _p50_p95(esc_e2e)
    deterministico["e2e_p50_ms"] = e2e_det["p50_ms"]
    deterministico["e2e_p95_ms"] = e2e_det["p95_ms"]
    escalado["e2e_p50_ms"] = e2e_esc["p50_ms"]
    escalado["e2e_p95_ms"] = e2e_esc["p95_ms"]

    base = deterministico["p95_ms"]
    razon = None
    if base and base > 0 and escalado["p95_ms"] is not None:
        razon = escalado["p95_ms"] / base
    return {
        "deterministico": deterministico,
        "escalado": escalado,
        "razon_p95": razon,
    }


def evaluar_criterio_inferencia(niveles, constantes=None):
    """Criterio de tres vias de c-218 MAS la condicion de degradacion por inferencia.

    Primero aplica el criterio primario de c-218 (techo de p95, throughput, tasa
    de error). Si la corrida es concluyente, agrega una violacion por nivel donde
    ``p95(escalado) > T * p95(deterministico)`` (T preregistrado). La corrida
    incompleta o con niveles inesperados sigue siendo «no concluyente».
    """
    constantes = constantes or CONSTANTES_INFERENCIA
    base = lt.evaluar_criterio(niveles, constantes)
    if base["veredicto"] == "no concluyente":
        return base

    violaciones = list(base["violaciones"])
    for nivel in niveles:
        inf = nivel.get("inferencia") or {}
        det = (inf.get("deterministico") or {}).get("p95_ms")
        esc = (inf.get("escalado") or {}).get("p95_ms")
        if det and esc is not None and esc > det * constantes["tolerancia_inferencia"]:
            violaciones.append(
                {"concurrencia": nivel["concurrencia"], "condicion": "inferencia"}
            )
    return {
        "veredicto": "no sostenida" if violaciones else "sostenida",
        "motivo": "",
        "violaciones": violaciones,
        "control_escalado": base.get("control_escalado"),
    }


# ── uso de tokens, version del modelo y costo declarado (c-243, G3) ──────────


def parsear_eventos_gemini(texto):
    """Extrae los eventos ``gemini_classified`` de una salida de logs.

    Cada linea es un JSON de structlog (posiblemente prefijada por Compose con
    ``servicio | ``). Las lineas que no son JSON o que no son el evento de
    clasificacion se ignoran. No interpreta el texto del prompt ni datos de PII.
    """
    eventos = []
    for linea in texto.splitlines():
        inicio = linea.find("{")
        if inicio == -1:
            continue
        try:
            dato = json.loads(linea[inicio:])
        except ValueError:
            continue
        if isinstance(dato, dict) and dato.get("event") == "gemini_classified":
            eventos.append(dato)
    return eventos


def leer_eventos_gemini(servicio, compose=None):
    """Lee los eventos de uso de los logs del backend (``docker compose logs``).

    Devuelve ``[]`` si no se pueden leer los logs (no aborta la corrida): en ese
    caso la evidencia lo declara con ``tokens_origen="ausente"`` y
    ``gasto_origen="no_registrado"``.
    """
    try:
        salida = subprocess.run(
            [*(compose or COMPOSE_INFERENCE), "logs", servicio],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            check=True, cwd=str(_REPO_ROOT),
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(
            "AVISO: no se pudieron leer los logs de %s: %s" % (servicio, exc),
            file=sys.stderr,
        )
        return []
    return parsear_eventos_gemini(salida)


def resumen_uso(eventos):
    """Agrega tokens y version del modelo a partir de los eventos de uso.

    Suma solo los eventos con conteo de la API (``tokens_origen == "api"``). El
    campo ``tokens_origen`` resume: ``api`` si TODOS los eventos traen uso,
    ``mixto`` si solo algunos, ``ausente`` si ninguno (o si no hay eventos).
    """
    entrada = salida = total = 0
    con_uso = 0
    modelo_solicitado = None
    model_version = None
    for evento in eventos:
        if evento.get("tokens_origen") == "api":
            con_uso += 1
            entrada += int(evento.get("tokens_entrada") or 0)
            salida += int(evento.get("tokens_salida") or 0)
            total += int(evento.get("tokens_total") or 0)
        if modelo_solicitado is None and evento.get("modelo_solicitado"):
            modelo_solicitado = evento["modelo_solicitado"]
        if model_version is None and evento.get("model_version"):
            model_version = evento["model_version"]
    if con_uso and con_uso == len(eventos):
        origen = "api"
    elif con_uso:
        origen = "mixto"
    else:
        origen = "ausente"
    return {
        "eventos": len(eventos),
        "eventos_con_uso": con_uso,
        "modelo_solicitado": modelo_solicitado,
        "model_version": model_version,
        "tokens_entrada": entrada if con_uso else None,
        "tokens_salida": salida if con_uso else None,
        "tokens_total": total if con_uso else None,
        "tokens_origen": origen,
    }


def calcular_costo_usd(
    tokens_entrada, tokens_salida, escenario=ESCENARIO_PRECIO_POR_DEFECTO, precios=None
):
    """Costo en USD de los tokens con el precio DECLARADO del escenario.

    Devuelve ``None`` si falta algun conteo (no se estima a ciegas). El escenario
    desconocido falla con ``KeyError`` (no se inventa un precio).
    """
    if tokens_entrada is None or tokens_salida is None:
        return None
    precio = (precios or PRECIOS_USD_POR_MILLON)[escenario]
    return (
        tokens_entrada * 1e-6 * precio["entrada"]
        + tokens_salida * 1e-6 * precio["salida"]
    )


def origen_gasto(uso):
    """Procedencia del gasto: calculado desde tokens, o no registrado."""
    if uso.get("tokens_entrada") is not None and uso.get("tokens_salida") is not None:
        return "tokens_calculado"
    return "no_registrado"


# ── fixture mixta ────────────────────────────────────────────────────────────


def cargar_fixture_inferencia(ruta):
    """Carga la fixture mixta: exige ``escala_esperada`` booleano por caso."""
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    casos = datos["casos"]
    for caso in casos:
        if "escala_esperada" not in caso or not isinstance(caso["escala_esperada"], bool):
            raise ValueError(
                "caso %s: falta la etiqueta booleana escala_esperada" % caso.get("id")
            )
        if len(caso["descripcion"]) < 10:
            raise ValueError(
                "caso %s: descripcion menor al minimo de 10 caracteres" % caso["id"]
            )
    if len({c["id"] for c in casos}) != len(casos):
        raise ValueError("ids de caso duplicados en la fixture de inferencia")
    return casos


# ── entorno y recolecta de detalles (sin abortar por escalada) ───────────────


def leer_env_contenedor(servicio):
    """Variables efectivas dentro del contenedor del backend (``printenv``)."""
    salida = subprocess.run(
        [*COMPOSE_INFERENCE, "exec", "-T", servicio, "printenv"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=True, cwd=str(_REPO_ROOT),
    ).stdout
    return dict(linea.split("=", 1) for linea in salida.splitlines() if "=" in linea)


def obtener_version_n8n(args):
    try:
        salida = subprocess.run(
            [*COMPOSE_INFERENCE, "exec", "-T", "n8n-corpus", "n8n", "--version"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            check=True, cwd=str(_REPO_ROOT),
        ).stdout.strip()
        return salida.splitlines()[-1] if salida else "desconocido"
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def _recolectar_detalles(base_url, token, repeticiones, timeout):
    """Detalle y etapa de cada incidente creado. NO aborta por escalada."""
    pares = [
        (lt._incidente_id(r), r.get("origen_message_id"), r.get("descripcion"))
        for rep in repeticiones
        for r in rep["resultados"]
        if lt.es_ok(r)
    ]

    def una(par):
        incidente_id, omid, descripcion = par
        if incidente_id is None:
            return {
                "origen_message_id": omid,
                "incidente_id": None,
                "descripcion": descripcion,
                "etapas": None,
                "etapa": ETAPA_SIN_REGISTRO,
                "latencia_e2e_ms": None,
            }
        detalle = lt.consultar_detalle(base_url, token, incidente_id, timeout)
        return {
            "origen_message_id": omid,
            "incidente_id": incidente_id,
            "descripcion": descripcion,
            "etapas": detalle["etapas"],
            "etapa": etapa_observada(detalle["etapas"]),
            "latencia_e2e_ms": detalle["latencia_e2e_ms"],
        }

    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(una, pares))


def _nivel_reporte_inferencia(concurrencia, repeticiones, detalles, esperadas):
    """Metricas del nivel (c-218) MAS etapas y contribucion de la inferencia."""
    m = lt.metricas_nivel(repeticiones)
    e2e = [d["latencia_e2e_ms"] for d in detalles if d.get("latencia_e2e_ms") is not None]
    pct = lt.percentiles(e2e, [50, 95]) if e2e else {50: None, 95: None}
    m.update(
        concurrencia=concurrencia,
        completo=m["total"] == esperadas,
        e2e_n=len(e2e),
        e2e_p50_ms=pct[50],
        e2e_p95_ms=pct[95],
        etapas=resumen_etapas(detalles),
        inferencia=contribucion_inferencia(repeticiones, detalles),
        repeticiones=[
            {
                "total": len(r["resultados"]),
                "ok": sum(1 for x in r["resultados"] if lt.es_ok(x)),
                "segundos": r["segundos"],
                "throughput_rps": lt.throughput(len(r["resultados"]), r["segundos"]),
                "p95_ms": lt.percentiles([x["latencia_ms"] for x in r["resultados"]], [95])[95],
            }
            for r in repeticiones
        ],
    )
    return m


# ── reporte (JSON + Markdown) con la contribucion de la inferencia ───────────


def renderizar_markdown_inferencia(datos):
    lineas = [
        "# Test de carga multicanal CON inferencia paga (TASK B)",
        "",
        "- Commit: %s" % datos["commit"],
        "- Fecha UTC: %s" % datos["fecha_utc"],
        "- Version de N8N: %s" % datos["n8n_version"],
        "- Perfil: %s" % datos["perfil"],
        "- Corrida: %s" % datos["corrida_id"],
        "- SHA-256 de la fixture: %s" % datos["fixture_sha256"],
        "- Tolerancia de inferencia (T): %s" % datos["prerregistro"]["tolerancia_inferencia"],
        "- Tope de presupuesto (USD): %s" % datos["prerregistro"]["tope_presupuesto_usd"],
        "- Veredicto: **%s**" % datos["veredicto"],
        "",
        "## Exclusiones declaradas",
        "",
    ]
    lineas += ["- %s" % e for e in datos["exclusiones"]]
    inf = datos.get("inferencia")
    if inf:
        lineas += [
            "",
            "## Uso de tokens y costo declarado",
            "",
            "- Modelo solicitado: %s" % inf.get("modelo_solicitado"),
            "- Version del modelo (API): %s" % inf.get("model_version"),
            "- Eventos de clasificacion: %s (con uso: %s)" % (
                inf.get("eventos"), inf.get("eventos_con_uso")
            ),
            "- Tokens de entrada: %s" % inf.get("tokens_entrada"),
            "- Tokens de salida: %s" % inf.get("tokens_salida"),
            "- Tokens totales: %s" % inf.get("tokens_total"),
            "- Origen de tokens: %s" % inf.get("tokens_origen"),
            "- Costo estimado (USD): %s" % inf.get("costo_usd"),
            "- Escenario de precio: %s" % inf.get("precio_escenario"),
            "- Fuente del precio: %s" % inf.get("precio_fuente"),
            "- Origen del gasto: %s" % inf.get("gasto_origen"),
        ]
    for nombre, capa in sorted(datos["capas"].items()):
        lineas += [
            "",
            "## Capa %s (veredicto: %s)" % (nombre, capa["criterio"]["veredicto"]),
            "",
            "| Concurrencia | p50 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) | Error | "
            "Escalados | p95 escalado (ms) | p95 deterministico (ms) | Razon |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for n in capa["niveles"]:
            inf_nivel = n.get("inferencia") or {}
            det = inf_nivel.get("deterministico") or {}
            esc = inf_nivel.get("escalado") or {}
            lineas.append(
                "| %d | %.1f | %.1f | %.1f | %.2f | %.4f | %d/%d | %s | %s | %s |"
                % (
                    n["concurrencia"], n["p50_ms"], n["p95_ms"], n["p99_ms"],
                    n["throughput_rps"], n["tasa_error"],
                    (n.get("etapas") or {}).get("escalados", 0),
                    (n.get("etapas") or {}).get("total", 0),
                    _fmt(esc.get("p95_ms")), _fmt(det.get("p95_ms")), _fmt(inf_nivel.get("razon_p95")),
                )
            )
        lineas += [
            "",
            "| Concurrencia | Eventos | Con uso | Tokens entrada | Tokens salida | Tokens total | Origen |",
            "|---|---|---|---|---|---|---|",
        ]
        for n in capa["niveles"]:
            t = n.get("tokens") or {}
            lineas.append(
                "| %d | %s | %s | %s | %s | %s | %s |"
                % (
                    n["concurrencia"], t.get("eventos"), t.get("eventos_con_uso"),
                    t.get("tokens_entrada"), t.get("tokens_salida"), t.get("tokens_total"),
                    t.get("tokens_origen"),
                )
            )
        for v in capa["criterio"].get("violaciones", []):
            lineas.append("")
            lineas.append("Violacion: nivel %s, condicion %s." % (v["concurrencia"], v["condicion"]))
    return "\n".join(lineas) + "\n"


def _fmt(valor):
    return "-" if valor is None else "%.1f" % float(valor)


def escribir_reporte_inferencia(ruta_json, datos, secretos=()):
    """Escribe el JSON y su resumen ``.md`` (LF, UTF-8 sin BOM, sin secretos)."""
    contenido_json = lt.renderizar_json(datos)
    contenido_md = renderizar_markdown_inferencia(datos)
    for secreto in secretos:
        if secreto and (secreto in contenido_json or secreto in contenido_md):
            raise lt.SecretoEnReporte("el reporte contendria un secreto; no se escribe")
    ruta_json = Path(ruta_json)
    ruta_json.write_bytes(contenido_json.encode("utf-8"))
    ruta_json.with_suffix(".md").write_bytes(contenido_md.encode("utf-8"))


# ── corrida ──────────────────────────────────────────────────────────────────


def correr_carga_inferencia(args):
    casos = cargar_fixture_inferencia(args.fixture)
    niveles = [int(x) for x in str(args.niveles).split(",")]
    login = lt.post_json(
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
            lambda cuerpo: lt.post_json(args.backend_url + "/api/v1/incidentes/", cuerpo, cabeceras, args.timeout),
            lt.payload,
        ),
        "n8n": (
            lambda cuerpo: lt.post_json(args.n8n_url + lt.WEBHOOK_WEB, cuerpo, None, args.timeout),
            lt.payload_webhook,
        ),
    }
    # Baseline de eventos de uso ANTES de la primera solicitud: la evidencia solo
    # cuenta lo producido por ESTA corrida (los logs pueden traer corridas previas).
    eventos_previos = len(leer_eventos_gemini(args.servicio_backend))
    eventos_run = []
    capas = {}
    for nombre, (enviar, construir) in destinos.items():
        filas = []
        for c in niveles:
            repeticiones = [
                lt.disparar(enviar, casos, c, args.solicitudes, "paid-%s-%s-c%d-r%d" % (corrida, nombre, c, r), construir)
                for r in range(args.repeticiones)
            ]
            detalles = _recolectar_detalles(args.backend_url, token, repeticiones, args.timeout)
            fila = _nivel_reporte_inferencia(c, repeticiones, detalles, args.solicitudes * args.repeticiones)
            # Uso de tokens del nivel: delta de eventos desde la ultima lectura.
            eventos = leer_eventos_gemini(args.servicio_backend)
            nuevos = eventos[eventos_previos:]
            eventos_previos = len(eventos)
            eventos_run.extend(nuevos)
            fila["tokens"] = resumen_uso(nuevos)
            filas.append(fila)
            print(
                "capa %s nivel %d: p95 %.1f ms, error %.4f, escalados %d/%d, tokens %s"
                % (nombre, c, fila["p95_ms"], fila["tasa_error"],
                   fila["etapas"]["escalados"], fila["etapas"]["total"],
                   fila["tokens"]["tokens_total"])
            )
        constantes = dict(CONSTANTES_INFERENCIA, niveles=tuple(niveles))
        capas[nombre] = {"niveles": filas, "criterio": evaluar_criterio_inferencia(filas, constantes)}
    por_capa = {n: c["criterio"]["veredicto"] for n, c in capas.items()}
    uso_global = resumen_uso(eventos_run)
    costo = calcular_costo_usd(
        uso_global["tokens_entrada"], uso_global["tokens_salida"], args.precio_escenario
    )
    uso_global.update(
        costo_usd=costo,
        precio_fuente=PRECIO_FUENTE,
        precio_escenario=args.precio_escenario,
        precios_usd_por_millon=PRECIOS_USD_POR_MILLON,
        gasto_origen=origen_gasto(uso_global),
    )
    datos = {
        "commit": lt.obtener_commit(),
        "fecha_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n8n_version": obtener_version_n8n(args),
        "perfil": "corpus (postgres-corpus, backend-corpus, n8n-corpus) con override de corrida paga acotada",
        "corrida_id": corrida,
        "fixture_sha256": lt.hash_fixture(args.fixture),
        "constantes": dict(
            CONSTANTES_INFERENCIA,
            tope_presupuesto_usd=args.tope_usd,
            niveles=list(constantes["niveles"]),
            solicitudes_por_nivel=args.solicitudes,
            repeticiones=args.repeticiones,
        ),
        "prerregistro": {
            "tolerancia_inferencia": CONSTANTES_INFERENCIA["tolerancia_inferencia"],
            "tope_presupuesto_usd": args.tope_usd,
            "mezcla_escalada_esperada": CONSTANTES_INFERENCIA["mezcla_escalada_esperada"],
        },
        "inferencia": uso_global,
        "exclusiones": lt.EXCLUSIONES,
        "capas": capas,
        "veredicto": lt.veredicto_global(por_capa),
    }
    if args.json_out:
        escribir_reporte_inferencia(
            args.json_out,
            datos,
            secretos=[
                args.password,
                token,
                DUMMY_GEMINI_API_KEY,
                getattr(args, "clave_gemini_real", None),
            ],
        )
    print("veredicto: %s" % datos["veredicto"])
    return 0


def _parser():
    p = argparse.ArgumentParser(
        description="Test de carga multicanal CON inferencia paga (TASK B), acotado."
    )
    p.add_argument("--json-out", default=None)
    p.add_argument("--backend-url", default="http://127.0.0.1:8001")
    p.add_argument("--n8n-url", default="http://127.0.0.1:5679")
    p.add_argument("--servicio-backend", default="backend-corpus")
    p.add_argument("--username", default=os.environ.get("LOAD_TEST_USERNAME", "admin"))
    p.add_argument("--password", default=os.environ.get("LOAD_TEST_PASSWORD", "admin123"))
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--fixture", default=str(RUTA_FIXTURE_INFERENCIA))
    p.add_argument("--niveles", default=",".join(str(n) for n in CONSTANTES_INFERENCIA["niveles"]))
    p.add_argument("--solicitudes", type=int, default=CONSTANTES_INFERENCIA["solicitudes_por_nivel"])
    p.add_argument("--repeticiones", type=int, default=CONSTANTES_INFERENCIA["repeticiones"])
    p.add_argument("--confirm-paid", action="store_true", help="autoriza explicitamente la corrida paga")
    p.add_argument(
        "--tope-usd", type=float, default=CONSTANTES_INFERENCIA["tope_presupuesto_usd"],
        help="tope autorizado del presupuesto de la guarda de costo (USD)",
    )
    p.add_argument(
        "--precio-escenario", default=ESCENARIO_PRECIO_POR_DEFECTO,
        choices=sorted(PRECIOS_USD_POR_MILLON),
        help="escenario de precio declarado para estimar el costo desde tokens",
    )
    return p


def main(argv=None, leer_env=None, correr=None):
    args = _parser().parse_args(argv)
    leer_env = leer_env or leer_env_contenedor
    correr = correr or correr_carga_inferencia
    env = leer_env(args.servicio_backend)
    try:
        verificar_corrida_paga_acotada(env, tope_usd=args.tope_usd, confirmado=args.confirm_paid)
    except GuardaPagaError as exc:
        print("ABORTADO (corrida paga): %s" % exc, file=sys.stderr)
        return 6
    # La clave real NUNCA se escribe en el reporte; se propaga solo para que el
    # escritor verifique que no aparezca por accidente.
    setattr(args, "clave_gemini_real", env.get("GEMINI_API_KEY"))
    return correr(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
