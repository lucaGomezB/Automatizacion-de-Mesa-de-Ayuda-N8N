"""Coteja la tabla `tab:carga-inferencia` contra los dos JSON de evidencia (c-243).

Script de solo lectura (biblioteca estandar). Extrae las ocho filas de la tabla
`tab:carga-inferencia` del `.tex` y las compara cifra por cifra contra los dos
artefactos de la sonda acotada con inferencia incluida: la corrida ampliada
(niveles 1 y 5, `load_test_inferencia_ampliada_2026-11-18.json`) y la corrida
original (niveles 10 y 20, `load_test_inferencia_2026-11-17.json`). Valida ademas
el orden capa/nivel, la corrida de origen y el n rotulados en cada fila, el
redondeo por columna (una decimal para latencias, dos para throughput y cociente,
cuatro para la tasa de error), el cociente de inferencia recalculado como
`p95(escalado)/p95(deterministico)` y el veredicto del nivel derivado del criterio
por capa (techo de p95, tolerancia de throughput, tasa de error y degradacion por
inferencia). El codigo de salida es 0 solo si no hay fallas. No modifica ningun
archivo ni vuelve a medir.

Uso, desde la raiz del repositorio:

    python3 -I docs/Tesis/Correcciones/cotejar_carga_inferencia.py \\
        --tex "docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex" \\
        --evidencia-ampliada evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json \\
        --evidencia-original evaluation/evidence/load_test_inferencia_2026-11-17.json
"""
import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

N_COLUMNAS = 11
ETIQUETA_TABLA = r"\label{tab:carga-inferencia}"
_EPS = 1e-9

# Opcion A: niveles 1 y 5 desde la corrida ampliada; 10 y 20 desde la original.
MAPEO_NIVEL_CORRIDA = {1: "ampliada", 5: "ampliada", 10: "original", 20: "original"}
ETIQUETA_CORRIDA = {"ampliada": "ampl.", "original": "orig."}
ETIQUETAS_CONDICION = {
    "p95_techo": "techo",
    "inferencia": "inferencia",
    "tasa_error": "error",
    "throughput": "throughput",
}
ESPERADO = (
    ("backend", 1),
    ("backend", 5),
    ("backend", 10),
    ("backend", 20),
    ("n8n", 1),
    ("n8n", 5),
    ("n8n", 10),
    ("n8n", 20),
)
DECIMALES = {"p50": 1, "p95": 1, "p99": 1, "throughput": 2, "error": 4, "r": 2}


class TablaAusente(Exception):
    """La tabla `tab:carga-inferencia` no esta presente en el `.tex`."""


@dataclass(frozen=True)
class Fila:
    capa: str
    corrida: str
    n: int
    concurrencia: int
    p50: str
    p95: str
    p99: str
    throughput: str
    error: str
    escalados: str
    r: str
    veredicto: str


@dataclass(frozen=True)
class Falla:
    fila: int
    campo: str
    mensaje: str


def normalizar_capa(celda):
    texto = celda.lower()
    if "backend" in texto:
        return "backend"
    if "webhook" in texto or "n8n" in texto:
        return "n8n"
    return texto


def parsear_corrida(celda):
    partes = celda.replace(r"\emph{", "").replace("}", "").split()
    if not partes:
        raise ValueError("celda de corrida vacia")
    etiqueta = partes[0]
    if etiqueta not in ("ampl.", "orig."):
        raise ValueError(f"etiqueta de corrida desconocida: {etiqueta!r}")
    n = int(partes[1]) if len(partes) > 1 else 0
    return ("ampliada" if etiqueta == "ampl." else "original"), n


def formatear(valor, decimales):
    """Formatea un valor con la convencion de la tesis (coma decimal)."""
    return f"{valor:.{decimales}f}".replace(".", ",")


def extraer_filas(texto):
    """Extrae las filas de `tab:carga-inferencia`; levanta TablaAusente si falta."""
    inicio = texto.find(ETIQUETA_TABLA)
    if inicio == -1:
        raise TablaAusente("tabla ausente: no se encontro \\label{tab:carga-inferencia}")
    fin = texto.find(r"\end{tabular}", inicio)
    if fin == -1:
        raise TablaAusente("tabla ausente: falta \\end{tabular} despues del label")
    filas = []
    for linea in texto[inicio:fin].splitlines():
        linea = linea.strip()
        if "&" not in linea or r"\textbf" in linea:
            continue
        celdas = [c.strip() for c in linea.rstrip("\\").split("&")]
        if len(celdas) != N_COLUMNAS:
            continue
        corrida, n = parsear_corrida(celdas[1])
        filas.append(
            Fila(
                capa=normalizar_capa(celdas[0]),
                corrida=corrida,
                n=n,
                concurrencia=int(celdas[2]),
                p50=celdas[3],
                p95=celdas[4],
                p99=celdas[5],
                throughput=celdas[6],
                error=celdas[7],
                escalados=celdas[8],
                r=celdas[9],
                veredicto=celdas[10],
            )
        )
    return filas


def cargar_json(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _buscar_nivel(datos, capa, concurrencia):
    for nivel in datos["capas"][capa]["niveles"]:
        if nivel["concurrencia"] == concurrencia:
            return nivel
    return None


def derivar_veredicto_nivel(datos, capa, concurrencia):
    """Deriva el veredicto del nivel desde el criterio por capa (techo, throughput,
    tasa de error e inferencia), con la misma logica del arnes."""
    constantes = datos["constantes"]
    niveles = sorted(datos["capas"][capa]["niveles"], key=lambda n: n["concurrencia"])
    indice = next((i for i, n in enumerate(niveles) if n["concurrencia"] == concurrencia), None)
    if indice is None:
        raise ValueError(f"la evidencia no tiene la capa {capa!r} en el nivel {concurrencia}")
    nivel = niveles[indice]
    condiciones = []
    if nivel["tasa_error"] > constantes["tasa_error_max"]:
        condiciones.append("tasa_error")
    if nivel["p95_ms"] > constantes["techo_p95_ms"]:
        condiciones.append("p95_techo")
    if indice > 0:
        anterior = niveles[indice - 1]
        piso = anterior["throughput_rps"] * (1 - constantes["tolerancia_throughput"])
        if nivel["throughput_rps"] < piso - _EPS:
            condiciones.append("throughput")
    inf = nivel["inferencia"]
    cociente = inf["escalado"]["p95_ms"] / inf["deterministico"]["p95_ms"]
    if cociente > constantes["tolerancia_inferencia"]:
        condiciones.append("inferencia")
    if not condiciones:
        return "cumple"
    return "no cumple (" + ", ".join(ETIQUETAS_CONDICION[c] for c in condiciones) + ")"


def _falla(fila, campo, mensaje):
    return Falla(fila, campo, f"fila {fila} [{campo}] {mensaje}")


def _comparar(fallas, fila, capa, concurrencia, campo, crudo, esperado, decimales):
    correcto = formatear(esperado, decimales)
    if crudo != correcto:
        fallas.append(
            _falla(
                fila,
                campo,
                f"({capa}, {concurrencia}): {campo} = {crudo!r} y la evidencia da {correcto!r}",
            )
        )


def cotejar(ruta_tex, ruta_ampliada, ruta_original):
    """Devuelve la lista de Falla del cotejo (vacia si todo pasa)."""
    texto = Path(ruta_tex).read_text(encoding="utf-8")
    try:
        filas = extraer_filas(texto)
    except TablaAusente as exc:
        return [Falla(0, "tabla", str(exc))]
    ampliada = cargar_json(ruta_ampliada)
    original = cargar_json(ruta_original)
    fallas = []
    if len(filas) != len(ESPERADO):
        fallas.append(_falla(0, "conteo", f"se esperaban {len(ESPERADO)} filas y hay {len(filas)}"))
    for indice, (capa_esperada, concurrencia) in enumerate(ESPERADO, start=1):
        if indice > len(filas):
            fallas.append(_falla(indice, "fila", f"ausente ({capa_esperada}, nivel {concurrencia})"))
            continue
        fila = filas[indice - 1]
        if fila.capa != capa_esperada or fila.concurrencia != concurrencia:
            fallas.append(
                _falla(
                    indice,
                    "orden",
                    f"se esperaba ({capa_esperada}, {concurrencia}) y hay ({fila.capa}, {fila.concurrencia})",
                )
            )
            continue
        fuente = MAPEO_NIVEL_CORRIDA[concurrencia]
        if fila.corrida != fuente:
            fallas.append(
                _falla(
                    indice,
                    "corrida",
                    f"({capa_esperada}, {concurrencia}): corrida {fila.corrida!r} y se esperaba {fuente!r} ({ETIQUETA_CORRIDA[fuente]})",
                )
            )
        datos = ampliada if fuente == "ampliada" else original
        nivel = _buscar_nivel(datos, capa_esperada, concurrencia)
        if nivel is None:
            fallas.append(
                _falla(indice, "evidencia", f"({capa_esperada}, {concurrencia}) no esta en la evidencia {fuente}")
            )
            continue
        escalados = nivel["etapas"]["escalados"]
        if fila.n != escalados:
            fallas.append(
                _falla(indice, "n", f"({capa_esperada}, {concurrencia}): n {fila.n} y la evidencia {escalados}")
            )
        celda_escalados = f"{escalados}/{nivel['etapas']['total']}"
        if fila.escalados != celda_escalados:
            fallas.append(
                _falla(
                    indice,
                    "escalados",
                    f"({capa_esperada}, {concurrencia}): {fila.escalados!r} y la evidencia {celda_escalados!r}",
                )
            )
        for campo, clave in (("p50", "p50_ms"), ("p95", "p95_ms"), ("p99", "p99_ms")):
            _comparar(
                fallas, indice, capa_esperada, concurrencia, campo, getattr(fila, campo), nivel[clave], DECIMALES[campo]
            )
        _comparar(
            fallas, indice, capa_esperada, concurrencia, "throughput", fila.throughput, nivel["throughput_rps"], DECIMALES["throughput"]
        )
        _comparar(
            fallas, indice, capa_esperada, concurrencia, "error", fila.error, nivel["tasa_error"], DECIMALES["error"]
        )
        inf = nivel["inferencia"]
        cociente = inf["escalado"]["p95_ms"] / inf["deterministico"]["p95_ms"]
        _comparar(fallas, indice, capa_esperada, concurrencia, "r", fila.r, cociente, DECIMALES["r"])
        veredicto = derivar_veredicto_nivel(datos, capa_esperada, concurrencia)
        if fila.veredicto != veredicto:
            fallas.append(
                _falla(
                    indice,
                    "veredicto",
                    f"({capa_esperada}, {concurrencia}): {fila.veredicto!r} y el criterio deriva {veredicto!r}",
                )
            )
    return fallas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tex", required=True)
    ap.add_argument(
        "--evidencia-ampliada",
        default="evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json",
    )
    ap.add_argument(
        "--evidencia-original",
        default="evaluation/evidence/load_test_inferencia_2026-11-17.json",
    )
    args = ap.parse_args(argv)
    fallas = cotejar(args.tex, args.evidencia_ampliada, args.evidencia_original)
    for falla in fallas:
        print(f"FALLA {falla.mensaje}")
    print(f"Filas cotejadas: {len(ESPERADO)}; fallas: {len(fallas)}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
