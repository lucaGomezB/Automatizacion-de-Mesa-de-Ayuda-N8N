"""Pruebas offline del arnes de carga multicanal (c-218).

Sin red, sin Docker, sin claves. Los valores esperados se calculan a mano y se
documentan junto a cada caso. Pytest se invoca desde la raiz o desde esta
carpeta (``python -m pytest scripts/load_test -q``).
"""

from __future__ import annotations

import pytest

import load_test as lt


# ── 1.1 / 1.3  percentiles ────────────────────────────────────────────────────


def test_percentiles_interpolacion_lineal_cuatro_valores():
    # n=4, posicion = (n-1)*q. p50: 3*0.50=1.5 -> 200 + 0.5*(300-200) = 250.
    # p95: 3*0.95=2.85 -> 300 + 0.85*(400-300) = 385. p99: 3*0.99=2.97 -> 397.
    resultado = lt.percentiles([100, 200, 300, 400], [50, 95, 99])
    assert resultado[50] == pytest.approx(250.0)
    assert resultado[95] == pytest.approx(385.0)
    assert resultado[99] == pytest.approx(397.0)


def test_percentiles_no_depende_del_orden_de_entrada():
    # Misma muestra que el caso anterior, desordenada: mismo resultado.
    resultado = lt.percentiles([400, 100, 300, 200], [50, 95])
    assert resultado[50] == pytest.approx(250.0)
    assert resultado[95] == pytest.approx(385.0)


def test_percentiles_cien_valores_p95():
    # 1..100: posicion = 99*0.95 = 94.05 -> valor 95 + 0.05*(96-95) = 95.05.
    resultado = lt.percentiles(list(range(1, 101)), [95])
    assert resultado[95] == pytest.approx(95.05)


def test_percentiles_un_unico_elemento():
    # Con una sola muestra todo percentil es esa muestra.
    assert lt.percentiles([42.0], [50, 95, 99]) == {50: 42.0, 95: 42.0, 99: 42.0}


def test_percentiles_empates():
    # Todos iguales: cualquier percentil es el valor repetido.
    assert lt.percentiles([5, 5, 5, 5], [50, 99]) == {50: 5.0, 99: 5.0}


def test_percentiles_lista_vacia_es_error_explicito():
    with pytest.raises(ValueError):
        lt.percentiles([], [50])


# ── 1.1 / 1.3  throughput y tasa de error ─────────────────────────────────────


def test_throughput_cociente_solicitudes_segundos():
    # 40 solicitudes en 2 s = 20 req/s; 30 en 4 s = 7,5 req/s.
    assert lt.throughput(40, 2.0) == pytest.approx(20.0)
    assert lt.throughput(30, 4.0) == pytest.approx(7.5)


def test_throughput_con_duracion_no_positiva_es_error():
    with pytest.raises(ValueError):
        lt.throughput(10, 0.0)


def test_tasa_error_cuenta_no_exitosas_sobre_el_total():
    # 38 ok de 40 -> 2 errores -> 0,05. 0 errores -> 0. Todo error -> 1.
    assert lt.tasa_error(38, 40) == pytest.approx(0.05)
    assert lt.tasa_error(40, 40) == 0.0
    assert lt.tasa_error(0, 40) == 1.0


def test_tasa_error_total_cero_es_error_explicito():
    with pytest.raises(ValueError):
        lt.tasa_error(0, 0)


# ── 1.1 / 1.3  evaluar_criterio (tres vias) ───────────────────────────────────


def _nivel(concurrencia, p95, rps, err=0.0, completo=True):
    return {
        "concurrencia": concurrencia,
        "p95_ms": p95,
        "throughput_rps": rps,
        "tasa_error": err,
        "completo": completo,
    }


def _niveles_sanos():
    # p95 holgado, throughput creciente, sin errores.
    return [
        _nivel(1, 100.0, 10.0),
        _nivel(5, 150.0, 35.0),
        _nivel(10, 200.0, 50.0),
        _nivel(20, 300.0, 60.0),
    ]


def test_criterio_todos_los_niveles_ok_es_sostenida():
    resultado = lt.evaluar_criterio(_niveles_sanos())
    assert resultado["veredicto"] == "sostenida"
    assert resultado["violaciones"] == []


def test_criterio_un_nivel_con_error_es_no_sostenida_y_nombra_nivel():
    niveles = _niveles_sanos()
    niveles[2]["tasa_error"] = 0.025  # 1 de 40 en el nivel 10
    resultado = lt.evaluar_criterio(niveles)
    assert resultado["veredicto"] == "no sostenida"
    assert [(v["concurrencia"], v["condicion"]) for v in resultado["violaciones"]] == [
        (10, "tasa_error")
    ]


def test_criterio_corrida_incompleta_es_no_concluyente():
    niveles = _niveles_sanos()
    niveles[3]["completo"] = False
    resultado = lt.evaluar_criterio(niveles)
    assert resultado["veredicto"] == "no concluyente"
    assert "incompleta" in resultado["motivo"]


def test_criterio_techo_p95_excedido_es_no_sostenida():
    # 5000,1 ms supera el techo prerregistrado de 5000 ms.
    niveles = _niveles_sanos()
    niveles[1]["p95_ms"] = 5000.1
    resultado = lt.evaluar_criterio(niveles)
    assert resultado["veredicto"] == "no sostenida"
    assert [(v["concurrencia"], v["condicion"]) for v in resultado["violaciones"]] == [
        (5, "p95_techo")
    ]


def test_criterio_p95_exactamente_en_el_techo_es_sostenida():
    # El techo es inclusivo (p95 <= 5000 ms).
    niveles = _niveles_sanos()
    niveles[1]["p95_ms"] = 5000.0
    assert lt.evaluar_criterio(niveles)["veredicto"] == "sostenida"


def test_criterio_caida_de_throughput_mayor_al_10_por_ciento_es_no_sostenida():
    # 50 -> 44 req/s = caida del 12 % (> 10 %) entre los niveles 10 y 20.
    niveles = _niveles_sanos()
    niveles[3]["throughput_rps"] = 44.0
    resultado = lt.evaluar_criterio(niveles)
    assert resultado["veredicto"] == "no sostenida"
    assert [(v["concurrencia"], v["condicion"]) for v in resultado["violaciones"]] == [
        (20, "throughput")
    ]


def test_criterio_caida_de_throughput_exactamente_10_por_ciento_es_sostenida():
    # 100 -> 90 req/s = caida exacta del 10 %: la tolerancia es inclusiva.
    niveles = [
        _nivel(1, 100.0, 100.0),
        _nivel(5, 100.0, 90.0),
        _nivel(10, 100.0, 90.0),
        _nivel(20, 100.0, 90.0),
    ]
    assert lt.evaluar_criterio(niveles)["veredicto"] == "sostenida"


def test_criterio_acumula_todas_las_violaciones():
    # Nivel 5: error y techo; nivel 20: caida de throughput (50 -> 40 = 20 %).
    niveles = _niveles_sanos()
    niveles[1]["tasa_error"] = 0.05
    niveles[1]["p95_ms"] = 6000.0
    niveles[3]["throughput_rps"] = 40.0
    resultado = lt.evaluar_criterio(niveles)
    pares = {(v["concurrencia"], v["condicion"]) for v in resultado["violaciones"]}
    assert pares == {(5, "tasa_error"), (5, "p95_techo"), (20, "throughput")}


def test_criterio_niveles_faltantes_es_no_concluyente():
    # Faltan los niveles 10 y 20 respecto de los prerregistrados (1/5/10/20).
    resultado = lt.evaluar_criterio(_niveles_sanos()[:2])
    assert resultado["veredicto"] == "no concluyente"
    assert "niveles" in resultado["motivo"]


def test_criterio_lista_vacia_es_no_concluyente():
    assert lt.evaluar_criterio([])["veredicto"] == "no concluyente"


def test_criterio_incompleta_prevalece_sobre_violaciones():
    niveles = _niveles_sanos()
    niveles[0]["tasa_error"] = 0.5
    niveles[3]["completo"] = False
    assert lt.evaluar_criterio(niveles)["veredicto"] == "no concluyente"


def test_control_de_escalado_se_informa_sin_alterar_el_veredicto():
    # p95(20)/p95(1) = 300/100 = 3 <= 20: cumple.
    cumple = lt.evaluar_criterio(_niveles_sanos())["control_escalado"]
    assert cumple["razon"] == pytest.approx(3.0)
    assert cumple["cumple"] is True
    # p95(1)=10 y p95(20)=300 -> 30 > 20: no cumple, pero es secundario.
    niveles = _niveles_sanos()
    niveles[0]["p95_ms"] = 10.0
    resultado = lt.evaluar_criterio(niveles)
    assert resultado["control_escalado"]["razon"] == pytest.approx(30.0)
    assert resultado["control_escalado"]["cumple"] is False
    assert resultado["veredicto"] == "sostenida"


@pytest.mark.parametrize(
    "por_capa, esperado",
    [
        ({"backend": "sostenida", "n8n": "sostenida"}, "sostenida"),
        ({"backend": "sostenida", "n8n": "no sostenida"}, "no sostenida"),
        ({"backend": "sostenida", "n8n": "no concluyente"}, "no concluyente"),
        ({"backend": "no sostenida", "n8n": "no concluyente"}, "no sostenida"),
    ],
)
def test_veredicto_global_combina_las_capas(por_capa, esperado):
    # Cualquier capa no sostenida domina; luego no concluyente; sostenida solo
    # si todas las capas lo son.
    assert lt.veredicto_global(por_capa) == esperado


# ── 1.4  armado de solicitudes y cliente concurrente ─────────────────────────

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class _Estado:
    def __init__(self):
        self.lock = threading.Lock()
        self.cuerpos = []
        self.auth = []
        self.en_vuelo = 0
        self.max_en_vuelo = 0
        self.demora = 0.0
        self.etapa = "deterministic"
        self.fallar_cada = 0  # si > 0, la solicitud k-esima (k % fallar_cada == 0) da 500


def _servidor_falso(estado):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silencio
            pass

        def _responder(self, status, cuerpo):
            data = json.dumps(cuerpo).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            largo = int(self.headers.get("Content-Length", "0"))
            cuerpo = json.loads(self.rfile.read(largo) or b"{}")
            if self.path.endswith("/auth/login"):
                self._responder(200, {"access_token": "tok-falso", "token_type": "bearer"})
                return
            with estado.lock:
                estado.en_vuelo += 1
                estado.max_en_vuelo = max(estado.max_en_vuelo, estado.en_vuelo)
                estado.cuerpos.append(cuerpo)
                estado.auth.append(self.headers.get("Authorization"))
                k = len(estado.cuerpos)
            try:
                time.sleep(estado.demora)
                if estado.fallar_cada and k % estado.fallar_cada == 0:
                    self._responder(500, {"detail": "boom"})
                else:
                    self._responder(201, {"id": k, "incidente_id": k, "latencia_e2e_ms": 12.5})
            finally:
                with estado.lock:
                    estado.en_vuelo -= 1

        def do_GET(self):
            if self.path.startswith("/api/v1/clasificaciones/incidente/"):
                self._responder(200, [{"etapa": estado.etapa}])
            else:
                self._responder(200, {"id": 1, "latencia_e2e_ms": 33.0})

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    return servidor, "http://127.0.0.1:%d" % servidor.server_address[1]


@pytest.fixture
def servidor():
    estado = _Estado()
    srv, url = _servidor_falso(estado)
    yield estado, url
    srv.shutdown()
    srv.server_close()


CASO = {"id": "F01", "sector": "Sistemas", "descripcion": "El servidor de produccion esta caido"}


def test_payload_backend_es_un_incidente_create_valido():
    cuerpo = lt.payload(CASO, "load-abc-000001")
    assert cuerpo["descripcion"] == CASO["descripcion"]
    assert len(cuerpo["descripcion"]) >= 10  # IncidenteCreate.descripcion min_length=10
    assert cuerpo["canal_origen_id"] == 2  # formulario web (catalogo migracion 001)
    assert cuerpo["origen_message_id"] == "load-abc-000001"
    assert cuerpo["prioridad"] == "media"


def test_payload_webhook_no_fija_canal_y_lleva_origen():
    # El canal lo marca el workflow ("Marcar canal web"); el webhook solo lleva
    # descripcion, prioridad y origen_message_id.
    cuerpo = lt.payload_webhook(CASO, "load-abc-000002")
    assert cuerpo == {
        "descripcion": CASO["descripcion"],
        "prioridad": "media",
        "origen_message_id": "load-abc-000002",
    }


def test_origenes_unicos_por_solicitud():
    ids = {lt.origen_id("load-abc", i) for i in range(500)}
    assert len(ids) == 500
    assert lt.origen_id("load-abc", 7) != lt.origen_id("load-xyz", 7)


def test_post_json_mide_latencia_y_parsea_respuesta(servidor):
    estado, url = servidor
    estado.demora = 0.05
    r = lt.post_json(url + "/api/v1/incidentes/", {"a": 1}, {"Authorization": "Bearer t"}, 5)
    assert r["status"] == 201
    assert r["error"] is None
    assert r["cuerpo"]["latencia_e2e_ms"] == 12.5
    assert r["latencia_ms"] >= 50.0  # el servidor durmio 50 ms
    assert estado.auth == ["Bearer t"]


def test_post_json_timeout_se_registra_como_error(servidor):
    estado, url = servidor
    estado.demora = 0.5
    r = lt.post_json(url + "/x", {}, None, 0.1)
    assert r["status"] is None
    assert r["error"] == "timeout"


def test_post_json_servidor_inalcanzable(servidor):
    r = lt.post_json("http://127.0.0.1:1/x", {}, None, 1)
    assert r["status"] is None
    assert r["error"] is not None


def test_disparar_respeta_la_concurrencia_fija(servidor):
    estado, url = servidor
    estado.demora = 0.1
    enviar = lambda cuerpo: lt.post_json(url + "/api/v1/incidentes/", cuerpo, None, 5)
    nivel = lt.disparar(enviar, [CASO], concurrencia=4, n_solicitudes=12, prefijo="t1")
    assert estado.max_en_vuelo == 4  # pool de 4: nunca mas, y llega a 4
    assert len(nivel["resultados"]) == 12
    assert nivel["segundos"] > 0


def test_disparar_origen_message_id_unico_y_conteo_2xx_igual_al_enviado(servidor):
    estado, url = servidor
    enviar = lambda cuerpo: lt.post_json(url + "/api/v1/incidentes/", cuerpo, None, 5)
    nivel = lt.disparar(enviar, [CASO, dict(CASO, id="F02")], concurrencia=5, n_solicitudes=20, prefijo="t2")
    ids = [c["origen_message_id"] for c in estado.cuerpos]
    assert len(ids) == 20 and len(set(ids)) == 20
    assert sum(1 for r in nivel["resultados"] if 200 <= r["status"] < 300) == 20


def test_disparar_rota_las_descripciones_del_fixture(servidor):
    estado, url = servidor
    casos = [dict(CASO, id="A", descripcion="descripcion A larga"), dict(CASO, id="B", descripcion="descripcion B larga")]
    enviar = lambda cuerpo: lt.post_json(url + "/api/v1/incidentes/", cuerpo, None, 5)
    lt.disparar(enviar, casos, concurrencia=1, n_solicitudes=4, prefijo="t3")
    assert [c["descripcion"] for c in estado.cuerpos] == [
        "descripcion A larga", "descripcion B larga", "descripcion A larga", "descripcion B larga",
    ]


def test_disparar_cuenta_fallos_sin_descartarlos(servidor):
    estado, url = servidor
    estado.fallar_cada = 4  # solicitudes 4, 8, 12 -> 3 errores de 12
    enviar = lambda cuerpo: lt.post_json(url + "/api/v1/incidentes/", cuerpo, None, 5)
    nivel = lt.disparar(enviar, [CASO], concurrencia=1, n_solicitudes=12, prefijo="t4")
    metricas = lt.metricas_nivel([nivel])
    assert metricas["total"] == 12 and metricas["ok"] == 9
    assert metricas["tasa_error"] == pytest.approx(0.25)  # 3/12


def test_consultar_detalle_devuelve_e2e_y_etapas(servidor):
    _, url = servidor
    detalle = lt.consultar_detalle(url, "tok", 1, 5)
    assert detalle["latencia_e2e_ms"] == 33.0
    assert detalle["etapas"] == ["deterministic"]


# ── 1.7  fixture y verificacion de no escalada ────────────────────────────────

from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixture_descripciones.json"
SECTORES = {
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
}


def test_fixture_versionado_es_valido():
    casos = lt.cargar_fixture(FIXTURE)
    assert len(casos) >= 25
    assert len({c["id"] for c in casos}) == len(casos)  # ids unicos
    assert all(len(c["descripcion"]) >= 10 for c in casos)  # IncidenteCreate min_length=10
    assert {c["sector"] for c in casos} == SECTORES  # cubre los cinco sectores canonicos


def test_cargar_fixture_rechaza_descripciones_cortas(tmp_path):
    ruta = tmp_path / "f.json"
    ruta.write_text(json.dumps({"casos": [{"id": "X", "sector": "Sistemas", "descripcion": "corta"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="X"):
        lt.cargar_fixture(ruta)


def test_hash_fixture_es_sha256_estable(tmp_path):
    ruta = tmp_path / "f.json"
    ruta.write_bytes(b"abc")
    # SHA-256 de b"abc" (vector de prueba estandar FIPS 180-2).
    assert lt.hash_fixture(ruta) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    ruta.write_bytes(b"abd")
    assert lt.hash_fixture(ruta) != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_no_escalada_acepta_solo_etapa_deterministica():
    lt.verificar_no_escalada("desc", ["deterministic"])  # no lanza


@pytest.mark.parametrize(
    "etapas, observada",
    [(["gemini"], "gemini"), (["fallback"], "fallback"), (["deterministic", "gemini"], "gemini"), ([], "sin registro")],
)
def test_escalada_o_ausencia_de_registro_es_fallo_ruidoso(etapas, observada):
    with pytest.raises(lt.EscaladaDetectada) as info:
        lt.verificar_no_escalada("mi descripcion", etapas)
    assert "mi descripcion" in str(info.value)
    assert observada in str(info.value)


# ── 1.8  guarda de costo cero ─────────────────────────────────────────────────


def test_costo_cero_acepta_clave_ficticia_y_presupuesto_nulo():
    lt.verificar_costo_cero({"GEMINI_API_KEY": lt.DUMMY_GEMINI_API_KEY, "COST_GUARD_BUDGET_USD": "0"})  # gitleaks:allow
    lt.verificar_costo_cero({"GEMINI_API_KEY": lt.DUMMY_GEMINI_API_KEY, "COST_GUARD_BUDGET_USD": "0.0"})  # gitleaks:allow


@pytest.mark.parametrize(
    "env",
    [
        {"GEMINI_API_KEY": "otra-clave", "COST_GUARD_BUDGET_USD": "0"},  # clave distinta de la ficticia  # gitleaks:allow
        {"GEMINI_API_KEY": lt.DUMMY_GEMINI_API_KEY, "COST_GUARD_BUDGET_USD": "5"},  # presupuesto > 0  # gitleaks:allow
        {"GEMINI_API_KEY": lt.DUMMY_GEMINI_API_KEY, "COST_GUARD_BUDGET_USD": "0.01"},  # gitleaks:allow
        {"GEMINI_API_KEY": lt.DUMMY_GEMINI_API_KEY},  # presupuesto ausente: no se asume cero  # gitleaks:allow
        {"COST_GUARD_BUDGET_USD": "0"},  # clave ausente
        {"GEMINI_API_KEY": lt.DUMMY_GEMINI_API_KEY, "COST_GUARD_BUDGET_USD": "abc"},  # gitleaks:allow
    ],
)
def test_costo_cero_rechaza_cualquier_otra_configuracion(env):
    with pytest.raises(lt.GuardaCostoError):
        lt.verificar_costo_cero(env)


def test_costo_cero_no_filtra_la_clave_real_en_el_mensaje():
    clave_real = "AIzaSyREAL-0123456789"  # gitleaks:allow
    with pytest.raises(lt.GuardaCostoError) as info:
        lt.verificar_costo_cero({"GEMINI_API_KEY": clave_real, "COST_GUARD_BUDGET_USD": "0"})
    assert clave_real not in str(info.value)


def test_main_aborta_sin_enviar_nada_si_la_guarda_falla():
    llamadas = []
    codigo = lt.main(
        ["--json-out", "x.json"],
        leer_env=lambda servicio: {"GEMINI_API_KEY": "real", "COST_GUARD_BUDGET_USD": "9"},  # gitleaks:allow
        correr=lambda args: llamadas.append(args),
    )
    assert codigo != 0
    assert llamadas == []  # ninguna solicitud ni corrida


def test_main_corre_si_la_guarda_pasa():
    llamadas = []
    codigo = lt.main(
        [],
        leer_env=lambda servicio: {"GEMINI_API_KEY": lt.DUMMY_GEMINI_API_KEY, "COST_GUARD_BUDGET_USD": "0"},  # gitleaks:allow
        correr=lambda args: llamadas.append(args) or 0,
    )
    assert codigo == 0
    assert len(llamadas) == 1


# ── 1.5  reporte determinista sin secretos ────────────────────────────────────


def _datos_reporte():
    nivel = {
        "concurrencia": 1,
        "total": 120,
        "ok": 120,
        "tasa_error": 0.0,
        "p50_ms": 20.5,
        "p95_ms": 40.25,
        "p99_ms": 55.0,
        "media_ms": 22.0,
        "throughput_rps": 45.5,
        "e2e_p50_ms": 15.0,
        "e2e_p95_ms": 30.0,
    }
    return {
        "commit": "a82a111",
        "fecha_utc": "2026-11-13T12:00:00Z",
        "n8n_version": "2.11.2",
        "perfil": "corpus",
        "fixture_sha256": "0" * 64,
        "constantes": {"niveles": [1], "techo_p95_ms": 5000.0},
        "exclusiones": ["correo: sondeo IMAP", "telefonia: canal pago"],
        "capas": {
            "backend": {"niveles": [nivel], "criterio": {"veredicto": "sostenida", "violaciones": []}},
            "n8n": {"niveles": [nivel], "criterio": {"veredicto": "sostenida", "violaciones": []}},
        },
        "veredicto": "sostenida",
    }


def test_reporte_es_determinista_byte_a_byte(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    lt.escribir_reporte(a, _datos_reporte())
    lt.escribir_reporte(b, _datos_reporte())
    assert a.read_bytes() == b.read_bytes()
    assert a.with_suffix(".md").read_bytes() == b.with_suffix(".md").read_bytes()


def test_reporte_lf_utf8_sin_bom(tmp_path):
    ruta = tmp_path / "r.json"
    lt.escribir_reporte(ruta, _datos_reporte())
    for archivo in (ruta, ruta.with_suffix(".md")):
        crudo = archivo.read_bytes()
        assert not crudo.startswith(b"\xef\xbb\xbf")
        assert b"\r" not in crudo
        assert crudo.endswith(b"\n")
        crudo.decode("utf-8")


def test_reporte_json_trae_la_trazabilidad_pedida(tmp_path):
    ruta = tmp_path / "r.json"
    lt.escribir_reporte(ruta, _datos_reporte())
    leido = json.loads(ruta.read_text(encoding="utf-8"))
    for clave in ("commit", "fecha_utc", "n8n_version", "perfil", "fixture_sha256", "constantes", "capas", "veredicto", "exclusiones"):
        assert clave in leido
    md = ruta.with_suffix(".md").read_text(encoding="utf-8")
    assert "sostenida" in md and "40.2" in md  # p95 con un decimal


def test_reporte_no_contiene_secretos(tmp_path):
    datos = _datos_reporte()
    datos["nota"] = "contrasena-del-operador-xyz"
    ruta = tmp_path / "r.json"
    with pytest.raises(lt.SecretoEnReporte):
        lt.escribir_reporte(ruta, datos, secretos=["contrasena-del-operador-xyz"])
    assert not ruta.exists()  # no escribe nada si detecta el secreto
    # Sin la nota, escribe con la lista de secretos presente y ninguno aparece.
    lt.escribir_reporte(ruta, _datos_reporte(), secretos=["contrasena-del-operador-xyz", "token-abc", lt.DUMMY_GEMINI_API_KEY])
    texto = ruta.read_text(encoding="utf-8") + ruta.with_suffix(".md").read_text(encoding="utf-8")
    for secreto in ("contrasena-del-operador-xyz", "token-abc", lt.DUMMY_GEMINI_API_KEY):
        assert secreto not in texto


# ── orquestacion: correr_carga de punta a punta contra el servidor falso ─────


def _argumentos(url, tmp_path, solicitudes=4, repeticiones=1):
    return lt._parser().parse_args(
        [
            "--backend-url", url,
            "--n8n-url", url,
            "--solicitudes", str(solicitudes),
            "--repeticiones", str(repeticiones),
            "--json-out", str(tmp_path / "rep.json"),
        ]
    )


@pytest.fixture
def entorno_falso(monkeypatch):
    monkeypatch.setattr(lt, "obtener_commit", lambda: "abc1234")
    monkeypatch.setattr(lt, "obtener_version_n8n", lambda args: "2.11.2")


def test_correr_carga_ejecuta_las_dos_capas_en_los_cuatro_niveles(servidor, tmp_path, entorno_falso):
    estado, url = servidor
    args = _argumentos(url, tmp_path)
    assert lt.correr_carga(args) == 0
    reporte = json.loads((tmp_path / "rep.json").read_text(encoding="utf-8"))
    assert set(reporte["capas"]) == {"backend", "n8n"}
    for capa in reporte["capas"].values():
        assert [n["concurrencia"] for n in capa["niveles"]] == [1, 5, 10, 20]
        assert all(n["total"] == 4 and n["ok"] == 4 for n in capa["niveles"])
        assert all(n["e2e_p50_ms"] == 33.0 for n in capa["niveles"])  # del detalle del servidor
    assert reporte["veredicto"] in {"sostenida", "no sostenida", "no concluyente"}
    assert reporte["commit"] == "abc1234" and reporte["n8n_version"] == "2.11.2"
    assert len(reporte["exclusiones"]) == 2
    # 2 capas x 4 niveles x 4 solicitudes de incidente; el login no cuenta.
    assert len([c for c in estado.cuerpos if "descripcion" in c]) == 32
    assert "tok-falso" not in (tmp_path / "rep.json").read_text(encoding="utf-8")


def test_correr_carga_aborta_ruidosamente_si_algo_escala(servidor, tmp_path, entorno_falso):
    estado, url = servidor
    estado.etapa = "gemini"
    args = _argumentos(url, tmp_path)
    assert lt.correr_carga(args) == 4
    assert not (tmp_path / "rep.json").exists()  # sin reporte de una corrida invalida


def test_correr_carga_login_fallido_es_error_de_infraestructura(tmp_path, entorno_falso):
    args = _argumentos("http://127.0.0.1:1", tmp_path)
    assert lt.correr_carga(args) == 5


# ── 1.6  refactor: bordes del control de escalado ────────────────────────────


def test_control_de_escalado_con_p95_base_nulo_no_cumple_sin_dividir_por_cero():
    niveles = _niveles_sanos()
    niveles[0]["p95_ms"] = 0.0
    control = lt.evaluar_criterio(niveles)["control_escalado"]
    assert control["razon"] == float("inf")
    assert control["cumple"] is False
