#!/usr/bin/env python3
"""Rango de robustez de los tiempos — consolidado de escenarios ya calculados (c-226).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red ni base
de datos, no reclasifica ni reentrena, y no modifica el corpus, las predicciones, los
artefactos congelados ni ningun numero canonico. Es aditivo: sus cifras van a la seccion
3.37 del memo y NO reemplazan ningun valor de las secciones 3.1 a 3.36.

Objeto de la consolidacion: la reduccion de la media del tiempo de registro de la campana
2026-10. Sobre ese estimando se reunen los escenarios ya calculados:

- Rango del estimando primario: descuentos de `0 s` (cifra primaria `71,16 %`), `5 s`
  (`68,61 %`) y `10 s` (`65,57 %`). El minimo es el descuento de `10 s`.
- Cotas de alcance rotuladas (no son el mismo estimando): desagregado por canal,
  reducciones por operador de la campana complementaria, efecto de posicion y cota
  inferior del instrumento (granularidad del redondeo manual).

Entradas versionadas (solo lectura):
- `data/corpus_evaluacion_pseudonimizado.json`: `200` casos con `tiempo_manual_s`,
  `tiempo_automatizado_s` y `canal_origen` (campana 2026-10).
- `evaluation/data/campana/brazo_manual.csv`: duraciones del brazo manual de la campana
  complementaria (`timestamp - inicio`), por `id_etiquetador` (operador).
- `evaluation/data/campana/corpus_campana.json`: `tiempo_automatizado_s` de la corrida
  propia de la campana complementaria (media `14,6 s`), por caso.
- `evaluation/data/campana/analisis/resultados.json`: efecto de posicion (Spearman) de la
  campana complementaria (seccion 3.14 del memo).

DESVIO DECLARADO respecto de `design.md` (D2): el design ubicaba las reducciones por
operador en `resultados.json`; ese artefacto NO contiene tiempos por operador. Las cifras
canonicas `33,8 %` / `79,7 %` / `69,3 %` proceden de `brazo_manual.csv` (manual) cruzado
con `corpus_campana.json` (automatizado de la corrida propia), que es como se calcularon en
c-196 (seccion 3.17 del memo). El script reproduce esas cifras desde esos artefactos.

Anclajes que abortan antes de escribir (exit distinto de cero, sin salidas): `71,16 %`,
`68,61 %` y `65,57 %` globales; `76,98 %`, `51,07 %` y `93,44 %` por canal; `199/200` y
`180/200` de granularidad; `33,8 %`, `79,7 %` y `69,3 %` por operador; y los valores del
efecto de posicion de la seccion 3.14. Las series se leen de los artefactos, no de
constantes.

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_rango_robustez_tiempos_c226.json`,
`.md` y `.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas
byte a byte; el script imprime el SHA-256 de cada salida.

Uso (desde la raiz del replicatorio):
    python3 evaluation/data/campana/analisis/analisis_rango_robustez_tiempos_c226.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import sys
from datetime import datetime
from statistics import fmean
from typing import Mapping, Sequence

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = SALIDA.parent
ROOT = SALIDA.parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation import stats  # noqa: E402

NOMBRE_BASE = "analisis_rango_robustez_tiempos_c226"
SALIDA_JSON = f"{NOMBRE_BASE}.json"
SALIDA_MD = f"{NOMBRE_BASE}.md"
SALIDA_SHA = f"{NOMBRE_BASE}.SHA256SUMS.txt"

RUTA_CORPUS_CANONICO = ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"
RUTA_BRAZO_MANUAL = CAMPANA / "brazo_manual.csv"
RUTA_CORPUS_CAMPANA = CAMPANA / "corpus_campana.json"
RUTA_RESULTADOS = SALIDA / "resultados.json"

DESCUENTOS = (0.0, 5.0, 10.0)

# Clave de ancla -> (valor canonico, numero de decimales con que se coteja).
# Las globales y por canal se cotejan a dos decimales; las de operador a uno (1 decimal
# es la precision con que el memo las registra); el `p` de O2 a cinco.
ANCLAS_ESPERADAS: dict[str, tuple[float, int]] = {
    "reduccion_global_0": (71.16, 2),
    "reduccion_global_5": (68.61, 2),
    "reduccion_global_10": (65.57, 2),
    "reduccion_canal_llamada telefónica": (76.98, 2),
    "reduccion_canal_correo electrónico": (51.07, 2),
    "reduccion_canal_formulario web": (93.44, 2),
    "granularidad_5": (199, 0),
    "granularidad_10": (180, 0),
    "reduccion_operador_O1": (33.8, 1),
    "reduccion_operador_O2": (79.7, 1),
    "reduccion_operador_agregado": (69.3, 1),
    "posicion_rho_O1": (-0.0628, 4),
    "posicion_p_O1": (0.5147, 4),
    "posicion_rho_O2": (-0.3604, 4),
    "posicion_p_O2": (0.00011, 5),
    "posicion_mde_rho": (0.276, 3),
}

NOTA_TELEFONIA = (
    "Telefonia: la grabacion esta acotada a un maximo de 45 s, de modo que el tiempo "
    "automatizado medido de la llamada es una cota inferior de su duracion real y su "
    "reduccion medida es una cota superior de la reduccion telefonica real."
)

NOTA_NO_COMPARABILIDAD = (
    "Las cotas de alcance (por canal, por operador, efecto de posicion y cota del "
    "instrumento) NO son el mismo estimando que el rango primario y no se comparan entre "
    "si: son sensibilidad o reinterpretacion, no una medicion nueva."
)


class AnclaNoReproducida(RuntimeError):
    """Los valores reconstruidos no coinciden con los canonicos."""


# ---------------------------------------------------------------------------
# Entradas (solo lectura)
# ---------------------------------------------------------------------------
def leer_casos_canonicos(ruta: pathlib.Path = RUTA_CORPUS_CANONICO) -> list[dict]:
    """Casos del corpus canonico de la campana 2026-10 (`200` casos)."""
    return json.loads(ruta.read_text(encoding="utf-8"))["casos"]


def leer_registros_manual(ruta: pathlib.Path = RUTA_BRAZO_MANUAL) -> list[dict]:
    """Duraciones del brazo manual de la campana complementaria (`timestamp - inicio`)."""
    registros: list[dict] = []
    with ruta.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            inicio = datetime.fromisoformat(fila["inicio"])
            fin = datetime.fromisoformat(fila["timestamp"])
            registros.append(
                {
                    "caso_id": fila["id_caso"],
                    "operador": fila["id_etiquetador"],
                    "duracion_s": (fin - inicio).total_seconds(),
                }
            )
    return registros


def leer_automatizado_campana(ruta: pathlib.Path = RUTA_CORPUS_CAMPANA) -> dict[str, float]:
    """Tiempo automatizado de la corrida propia de la campana, por `id_caso`."""
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    return {caso["id"]: caso["tiempo_automatizado_s"] for caso in documento["casos"]}


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def rango_descuentos(
    manual: Sequence[float],
    automatizado: Sequence[float],
    descuentos: Sequence[float] = DESCUENTOS,
) -> dict:
    """Reduccion de la media por descuento y el escenario que la minimiza.

    Reutiliza `evaluation.stats.reduccion_relativa` y `estadisticos_descriptivos`. El
    descuento `0` reproduce la cifra primaria; el minimo es el descuento mayor.
    """
    escenarios = []
    for descuento in descuentos:
        ajustado = [float(m) - float(descuento) for m in manual]
        reduccion = stats.reduccion_relativa(ajustado, automatizado).media
        escenarios.append(
            {
                "descuento_s": float(descuento),
                "media_manual_ajustada": stats.estadisticos_descriptivos(ajustado).media,
                "reduccion_media": reduccion,
            }
        )
    minimo = min(escenarios, key=lambda e: e["reduccion_media"])
    primario = next(
        (e for e in escenarios if e["descuento_s"] == 0.0), escenarios[0]
    )
    return {
        "escenarios": escenarios,
        "escenario_minimo": minimo,
        "reduccion_primaria": primario["reduccion_media"],
        "rango": [
            minimo["reduccion_media"],
            max(e["reduccion_media"] for e in escenarios),
        ],
    }


def resumen_por_canal(casos: Sequence[Mapping]) -> dict:
    """Reduccion intra-canal por `canal_origen` y el canal que la minimiza."""
    grupos: dict[str, dict[str, list[float]]] = {}
    for caso in casos:
        canal = caso["canal_origen"]
        grupo = grupos.setdefault(canal, {"manual": [], "automatizado": []})
        grupo["manual"].append(caso["tiempo_manual_s"])
        grupo["automatizado"].append(caso["tiempo_automatizado_s"])
    por_canal = {}
    for canal, grupo in grupos.items():
        reduccion = stats.reduccion_relativa(grupo["manual"], grupo["automatizado"])
        por_canal[canal] = {
            "n": len(grupo["manual"]),
            "reduccion_media": reduccion.media,
            "reduccion_mediana": reduccion.mediana,
        }
    canal_minimo = min(por_canal, key=lambda c: por_canal[c]["reduccion_media"])
    return {
        "por_canal": por_canal,
        "canal_minimo": canal_minimo,
        "reduccion_minima": por_canal[canal_minimo]["reduccion_media"],
    }


def resumen_por_operador(
    registros_manual: Sequence[Mapping],
    automatizado_por_caso: Mapping[str, float],
) -> dict:
    """Reduccion por operador y agregada por caso desde el brazo manual y el corpus propio.

    Por operador se conservan las `n` derivaciones; el agregado promedia las coberturas
    dobles (los casos con dos operadores cuentan una vez).
    """
    por_operador = {}
    for operador in sorted({r["operador"] for r in registros_manual}):
        filas = [r for r in registros_manual if r["operador"] == operador]
        manual = [r["duracion_s"] for r in filas]
        automatizado = [automatizado_por_caso[r["caso_id"]] for r in filas]
        por_operador[operador] = {
            "n": len(filas),
            "manual_media": fmean(manual),
            "automatizado_media": fmean(automatizado),
            "reduccion_media": stats.reduccion_relativa(manual, automatizado).media,
        }

    manuales_por_caso: dict[str, list[float]] = {}
    for registro in registros_manual:
        manuales_por_caso.setdefault(registro["caso_id"], []).append(registro["duracion_s"])
    ids = sorted(manuales_por_caso)
    manual = [fmean(manuales_por_caso[i]) for i in ids]
    automatizado = [automatizado_por_caso[i] for i in ids]
    return {
        "por_operador": por_operador,
        "agregado": {
            "n": len(ids),
            "manual_media": fmean(manual),
            "automatizado_media": fmean(automatizado),
            "reduccion_media": stats.reduccion_relativa(manual, automatizado).media,
        },
    }


def resumen_posicion(resultados: Mapping) -> dict:
    """Coeficiente, `p` y MDE del efecto de posicion (Spearman) por operador."""
    bloques = resultados["secciones"]["orden"]["resultado"]["por_operador"]
    por_operador = {}
    mde_rho = None
    for bloque in bloques:
        spearman = bloque["posicion"]["spearman"]
        por_operador[bloque["id_etiquetador"]] = {
            "rho": spearman["rho"],
            "p": spearman["p"],
            "mde_rho": spearman["mde"],
            "significativo": spearman["p"] < 0.05,
        }
        if mde_rho is None:
            mde_rho = spearman["mde"]
    return {"por_operador": por_operador, "mde_rho": mde_rho}


def cota_instrumento(manual: Sequence[float]) -> dict:
    """Multiplos exactos de `5 s` y `10 s` (resolucion del redondeo) y la nota telefonica."""
    return {
        "n": len(manual),
        "multiplos": stats.granularidad_manual(manual, (5, 10)),
        "nota_telefonia": NOTA_TELEFONIA,
    }


# ---------------------------------------------------------------------------
# Anclajes
# ---------------------------------------------------------------------------
def _anclas_observadas(
    rango: Mapping,
    canal: Mapping,
    instrumento: Mapping,
    operador: Mapping,
    posicion: Mapping,
) -> dict[str, float]:
    """Aplana los bloques calculados a las claves de `ANCLAS_ESPERADAS` (en porcentaje)."""
    escenarios = {int(e["descuento_s"]): e["reduccion_media"] for e in rango["escenarios"]}
    return {
        "reduccion_global_0": escenarios[0] * 100,
        "reduccion_global_5": escenarios[5] * 100,
        "reduccion_global_10": escenarios[10] * 100,
        "reduccion_canal_llamada telefónica": (
            canal["por_canal"]["llamada telefónica"]["reduccion_media"] * 100
        ),
        "reduccion_canal_correo electrónico": (
            canal["por_canal"]["correo electrónico"]["reduccion_media"] * 100
        ),
        "reduccion_canal_formulario web": (
            canal["por_canal"]["formulario web"]["reduccion_media"] * 100
        ),
        "granularidad_5": instrumento["multiplos"][5],
        "granularidad_10": instrumento["multiplos"][10],
        "reduccion_operador_O1": operador["por_operador"]["O1"]["reduccion_media"] * 100,
        "reduccion_operador_O2": operador["por_operador"]["O2"]["reduccion_media"] * 100,
        "reduccion_operador_agregado": operador["agregado"]["reduccion_media"] * 100,
        "posicion_rho_O1": posicion["por_operador"]["O1"]["rho"],
        "posicion_p_O1": posicion["por_operador"]["O1"]["p"],
        "posicion_rho_O2": posicion["por_operador"]["O2"]["rho"],
        "posicion_p_O2": posicion["por_operador"]["O2"]["p"],
        "posicion_mde_rho": posicion["mde_rho"],
    }


def verificar_anclas(
    observados: Mapping[str, float],
    esperadas: Mapping[str, tuple[float, int]] = ANCLAS_ESPERADAS,
) -> None:
    """Aborta con `AnclaNoReproducida` si un valor reconstruido difiere del canonico."""
    diferencias = []
    for clave, (valor, decimales) in esperadas.items():
        observado = observados.get(clave)
        if observado is None:
            diferencias.append(f"{clave}: ausente (esperado {valor})")
        elif round(float(observado), decimales) != round(valor, decimales):
            diferencias.append(f"{clave}: reconstruido {observado!r} != versionado {valor}")
    if diferencias:
        raise AnclaNoReproducida("; ".join(diferencias))


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def sha256(ruta: pathlib.Path, *, normalizar_lf: bool = True) -> str:
    """SHA-256 del archivo; con `normalizar_lf` colapsa CRLF a LF."""
    datos = pathlib.Path(ruta).read_bytes()
    if normalizar_lf:
        datos = datos.replace(b"\r\n", b"\n")
    return hashlib.sha256(datos).hexdigest()


def declaracion_aditiva() -> str:
    """Declaracion aditiva y de sensibilidad; la cifra primaria no cambia."""
    return (
        "Lectura de sensibilidad/reinterpretacion: el rango de robustez reune escenarios "
        "ya calculados y no es una medicion nueva; la cifra primaria 71,2 % y su intervalo "
        "[67,2 %; 74,6 %] no cambian. Registro aditivo en la seccion 3.37 del memo."
    )


def construir_documento(
    *,
    canonica: pathlib.Path = RUTA_CORPUS_CANONICO,
    brazo_manual: pathlib.Path = RUTA_BRAZO_MANUAL,
    corpus_campana: pathlib.Path = RUTA_CORPUS_CAMPANA,
    resultados: pathlib.Path = RUTA_RESULTADOS,
    anclas_esperadas: Mapping[str, tuple[float, int]] | None = None,
) -> dict:
    """Lee los artefactos, calcula los bloques y verifica los anclajes.

    Falla antes de devolver nada si un anclaje versionado no se reproduce. No escribe
    archivos.
    """
    casos = leer_casos_canonicos(canonica)
    manual = [caso["tiempo_manual_s"] for caso in casos]
    automatizado = [caso["tiempo_automatizado_s"] for caso in casos]

    rango = rango_descuentos(manual, automatizado)
    canal = resumen_por_canal(casos)
    instrumento = cota_instrumento(manual)
    operador = resumen_por_operador(
        leer_registros_manual(brazo_manual), leer_automatizado_campana(corpus_campana)
    )
    posicion = resumen_posicion(json.loads(resultados.read_text(encoding="utf-8")))

    observados = _anclas_observadas(rango, canal, instrumento, operador, posicion)
    esperadas = ANCLAS_ESPERADAS if anclas_esperadas is None else anclas_esperadas
    verificar_anclas(observados, esperadas)

    return {
        "change": "c-226-consolidar-el-rango-de-robustez-de-tiempos",
        "generador": "evaluation/data/campana/analisis/analisis_rango_robustez_tiempos_c226.py",
        "metodo": (
            "consolidado de escenarios ya calculados; el rango primario reutiliza "
            "evaluation.stats.reduccion_relativa sobre el corpus canonico; las reducciones "
            "por operador cruzan brazo_manual.csv con corpus_campana.json; el efecto de "
            "posicion se lee de resultados.json; sin red ni Gemini y sin medicion nueva"
        ),
        "rango_primario": {
            "definicion": (
                "reduccion de la media del tiempo de registro de la campana 2026-10"
            ),
            "escenarios": rango["escenarios"],
            "escenario_minimo": rango["escenario_minimo"],
            "rango": rango["rango"],
        },
        "por_canal": canal,
        "por_operador": operador,
        "efecto_posicion": posicion,
        "cota_instrumento": instrumento,
        "entradas_sha256": {
            "corpus_evaluacion_pseudonimizado.json": sha256(canonica),
            "brazo_manual.csv": sha256(brazo_manual),
            "corpus_campana.json": sha256(corpus_campana),
            "resultados.json": sha256(resultados),
        },
        "anclas_verificadas": dict(esperadas),
        "nota_no_comparabilidad": NOTA_NO_COMPARABILIDAD,
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "seccion_memo": "3.37",
            "declaracion": declaracion_aditiva(),
        },
    }


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------
def _p(valor: float | None, decimales: int = 2) -> str:
    """Numero con coma decimal (convencion de la tesis)."""
    if valor is None:
        return "n/d"
    return f"{valor:.{decimales}f}".replace(".", ",")


def _rol_escenario(descuento_s: float, descuento_minimo_s: float) -> str:
    """Rotulo del rol de un escenario de descuento dentro del rango primario."""
    if descuento_s == descuento_minimo_s:
        return "minimo del estimando primario"
    if descuento_s == 0.0:
        return "cifra primaria (cota superior)"
    return "cota inferior"


def renderizar(documento: Mapping) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF, UTF-8 sin BOM."""
    texto_json = (
        json.dumps(
            documento, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
        )
        + "\n"
    )
    rango = documento["rango_primario"]
    lineas = [
        "# Rango de robustez de los tiempos (c-226)",
        "",
        "Solo lectura, offline y determinista; sin red ni Gemini. "
        + documento["aditivo"]["declaracion"],
        "",
        "## Rango del estimando primario",
        "",
        "| Descuento | Media manual ajustada (s) | Reduccion de la media | Rol |",
        "|---|---|---|---|",
    ]
    for escenario in rango["escenarios"]:
        rol = _rol_escenario(
            escenario["descuento_s"], rango["escenario_minimo"]["descuento_s"]
        )
        lineas.append(
            f"| {_p(escenario['descuento_s'], 0)} s | "
            f"{_p(escenario['media_manual_ajustada'], 3)} | "
            f"{_p(escenario['reduccion_media'] * 100)} % | {rol} |"
        )
    lineas += [
        "",
        f"Rango del estimando primario: "
        f"[{_p(rango['rango'][0] * 100)} %; {_p(rango['rango'][1] * 100)} %]; "
        f"el minimo es el descuento de {_p(rango['escenario_minimo']['descuento_s'], 0)} s.",
        "",
        "## Cota de alcance: por canal (intra-canal, no comparable)",
        "",
        "| Canal | n | Reduccion de la media |",
        "|---|---|---|",
    ]
    for canal, datos in documento["por_canal"]["por_canal"].items():
        rotulo = " (minimo intra-canal)" if canal == documento["por_canal"]["canal_minimo"] else ""
        lineas.append(
            f"| {canal}{rotulo} | {datos['n']} | {_p(datos['reduccion_media'] * 100)} % |"
        )
    lineas += [
        "",
        "## Cota de alcance: por operador (campana complementaria, no comparable)",
        "",
        "| Operador | n | Manual (s) | Automatizado (s) | Reduccion de la media |",
        "|---|---|---|---|---|",
    ]
    operador = documento["por_operador"]
    for op, datos in operador["por_operador"].items():
        lineas.append(
            f"| {op} | {datos['n']} | {_p(datos['manual_media'], 1)} | "
            f"{_p(datos['automatizado_media'], 1)} | {_p(datos['reduccion_media'] * 100, 1)} % |"
        )
    lineas.append(
        f"| Agregado | {operador['agregado']['n']} | "
        f"{_p(operador['agregado']['manual_media'], 1)} | "
        f"{_p(operador['agregado']['automatizado_media'], 1)} | "
        f"{_p(operador['agregado']['reduccion_media'] * 100, 1)} % |"
    )
    lineas += [
        "",
        "## Efecto de posicion (Spearman) y cota del instrumento",
        "",
        "| Operador | rho | p | MDE (rho) | Significativo |",
        "|---|---|---|---|---|",
    ]
    for op, datos in documento["efecto_posicion"]["por_operador"].items():
        lineas.append(
            f"| {op} | {_p(datos['rho'], 4)} | {_p(datos['p'], 5)} | "
            f"{_p(datos['mde_rho'], 3)} | {'si' if datos['significativo'] else 'no'} |"
        )
    cota = documento["cota_instrumento"]
    lineas += [
        "",
        f"Granularidad del redondeo manual: multiplos de 5 s {cota['multiplos'][5]}/"
        f"{cota['n']}; de 10 s {cota['multiplos'][10]}/{cota['n']}. {cota['nota_telefonia']}",
        "",
        f"**Nota de no comparabilidad.** {documento['nota_no_comparabilidad']}",
        "",
    ]
    return texto_json, "\n".join(lineas) + "\n"


def escribir(documento: Mapping, directorio: pathlib.Path = SALIDA) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF)."""
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(documento)
    rutas = []
    for nombre, texto in ((SALIDA_JSON, texto_json), (SALIDA_MD, texto_md)):
        ruta = directorio / nombre
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    sumas = "".join(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}\n" for ruta in rutas)
    ruta_sumas = directorio / SALIDA_SHA
    ruta_sumas.write_bytes(sumas.encode("utf-8"))
    rutas.append(ruta_sumas)
    return rutas


def ejecutar(
    *,
    salida: pathlib.Path = SALIDA,
    anclas_esperadas: Mapping[str, tuple[float, int]] | None = None,
) -> dict:
    """Construye, verifica anclajes y escribe; aborta sin escribir si un ancla falla."""
    documento = construir_documento(anclas_esperadas=anclas_esperadas)
    escribir(documento, salida)
    for ruta in (salida / SALIDA_JSON, salida / SALIDA_MD, salida / SALIDA_SHA):
        print(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}")
    return documento


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    args = parser.parse_args(argv)
    try:
        ejecutar(salida=args.salida)
    except (AnclaNoReproducida, ValueError) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
