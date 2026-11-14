#!/usr/bin/env python3
"""Sensibilidad del clasificador a referencias alternativas plausibles (c-216).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red, no
reclasifica, no reentrena ni modifica el corpus, las predicciones o los numeros canonicos.
Es aditivo: reproduce los anclajes `142/206` (exactitud estricta `0,6893`) y macro-F1
`0,7024` de la referencia arbitrada de c-206 antes de simular y no reemplaza ningun valor
de las secciones 3.1 a 3.26 del memo canonico.

Entradas versionadas (solo lectura):
- `evaluation/data/campana/corpus_independiente_arbitrado.json` (206 casos)
- `evaluation/data/campana/predicciones_arbitrado.json` (clasificador congelado `hybrid-v3`)
- `evaluation/data/campana/doble_etiquetado_arbitrado.csv` (476 filas: E3 y E4 sobre los
  206 casos, E5 sobre los 64 discordantes)
- `evaluation/data/campana/arbitraje_tres_vias.json` (64 arbitrados por E5, 6 de tres vias)

METODO COMPLETO, FIJADO EN ESTE DOCSTRING ANTES DE CORRER (tarea 1.3)
=====================================================================

Preregistro: el metodo, los parametros y las reglas de decision de este docstring se
fijaron antes de generar cualquier salida. El prerregistro NO fue ciego: el corpus, las
predicciones y los agregados canonicos (142/206, macro-F1 0,7024, kappa 0,6055, p_o 0,6867)
ya se conocian; lo que no se habia observado era la distribucion de la simulacion, que
estas reglas gobiernan. Se informan todos los escenarios, favorables o no.

1. Kernel de ruido Q. Matriz 5x5 fila-estocastica `Q[c, c']` = probabilidad empirica de
   que un etiquetador independiente asigne `c'` cuando la referencia arbitrada es `c`. Se
   construye con las etiquetas de E3 y E4 sobre todo el corpus y las de E5 sobre los 64
   casos que arbitro; cada etiquetador pondera segun la cantidad de casos que etiqueto
   (pool de las 476 filas). Se aplica suavizado de Laplace `0,5` por fila y se declara el
   soporte (conteo crudo) de cada fila. `Q` no es una estimacion de la verdad: es la
   confusion empirica entre la referencia y las etiquetas recolectadas.

2. Calibracion de la intensidad lambda. Mezcla convexa
   `Q_lambda = (1 - lambda) * Q + lambda * m`, donde `m` es la distribucion marginal
   empirica de clases de la referencia repetida por fila. En `lambda = 0` la concordancia
   es la del kernel empirico (superior al kappa observado); en `lambda = 1` la etiqueta
   simulada es independiente de la referencia (kappa = 0). Se busca por biseccion el
   `lambda*` tal que el kappa esperado entre una etiqueta simulada con `Q_lambda*` y la
   referencia reproduzca `0,6055` con tolerancia `+-0,005`; se informa tambien el `p_o`
   esperado contra `0,6867` como chequeo. El kappa esperado se calcula de forma analitica
   (determinista) a partir de `Q_lambda`, la marginal y la distribucion de referencia; la
   simulacion Monte Carlo con semilla fija se usa despues para verificar que el kappa
   realizado cae dentro de la tolerancia. `lambda*` es una intensidad de ruido CONSISTENTE
   CON EL ACUERDO MEDIDO, no una estimacion de la verdad latente ni de la tasa de error
   real de la referencia.

3. Replicas. `B = 2000` replicas con semilla `20261021`. En cada replica se genera una
   referencia alternativa `R*` por caso con `R* ~ Q_lambda*(R, .)` (una extraccion
   independiente por caso) y se recalculan la exactitud estricta y la macro-F1 de las
   predicciones fijas contra `R*`. Se informan la mediana, los percentiles `2,5` y `97,5`,
   la proporcion de replicas con exactitud mayor o igual a `0,6893` y la distribucion
   completa en el JSON.

4. Descomposicion. Con `64` errores observados (206 - 142), se informa el intervalo de
   errores bajo referencias alternativas `[q2,5; q97,5]` y se separa: (i) error robusto, el
   que persiste en el extremo mas favorable de la simulacion (cota inferior de errores); y
   (ii) error atribuible a la referencia, la diferencia entre el error observado y ese
   extremo. La separacion se rotula como SENSIBILIDAD, no como causalidad ni como verdad
   latente. Si el error observado queda por debajo del extremo favorable, el componente
   atribuible resulta negativo; se informa tal cual, sin recortarlo ni reordenar el metodo.

5. Cotas distribution-free (metodo secundario). Sea `delta` la cota superior de Wilson al
   95 % de la probabilidad media de etiqueta alternativa fuera de la diagonal de
   `Q_lambda*`, promediada sobre los 206 casos con la distribucion de referencia. Con
   `m = round(delta * 206)`, las cotas de exactitud estricta son
   `[max(0, (142 - m) / 206), min(1, (142 + m) / 206)]`. Son cotas validas bajo el supuesto
   "a lo sumo `m` etiquetas de referencia son erroneas", se declaran como sensibilidad y no
   como medicion, y no dependen de la calibracion por kappa: sirven de contraste.

6. Casos de tres vias. Se listan los `6` casos con `tres_vias = true`: sus etiquetas de E3,
   E4 y E5, la referencia usada (la de E5), si el clasificador acerto y el rango de
   exactitud estricta que resulta de asignar el caso a cada una de las tres etiquetas
   (cada caso mueve como maximo `1/206`). No se elige una etiqueta "verdadera": el rango es
   el resultado.

7. Anclajes. Antes de simular, el script calcula la exactitud estricta y la macro-F1 con
   las predicciones fijas contra la referencia y ABORTA sin escribir salidas si no
   reproduce `142/206` y macro-F1 `0,7024` (tolerancia `1e-4`). Tambien aborta si los
   conteos no coinciden con `206`, `476`, `64` y `6`.

Salidas (UTF-8 sin BOM, LF, en esta misma carpeta):
`analisis_ruido_referencia_c216.json`, `.md` y `.SHA256SUMS.txt`. Dos corridas con las
mismas entradas producen salidas identicas byte a byte; el script imprime el SHA-256 de
cada salida.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_ruido_referencia_c216.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.metrics import (  # noqa: E402
    CLASES,
    NIVEL_CONFIANZA,
    f1_macro,
    f1_por_clase,
    intervalo_wilson,
    matriz_confusion,
    percentil_intervalo,
)

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = ROOT / "evaluation/data/campana"
RUTA_CORPUS = CAMPANA / "corpus_independiente_arbitrado.json"
RUTA_PREDICCIONES = CAMPANA / "predicciones_arbitrado.json"
RUTA_ETIQUETADO = CAMPANA / "doble_etiquetado_arbitrado.csv"
RUTA_ARBITRAJE = CAMPANA / "arbitraje_tres_vias.json"

NOMBRE_BASE = "analisis_ruido_referencia_c216"
NOMBRE_JSON = f"{NOMBRE_BASE}.json"
NOMBRE_MD = f"{NOMBRE_BASE}.md"
NOMBRE_SUMAS = f"{NOMBRE_BASE}.SHA256SUMS.txt"

# Parametros fijados en el prerregistro (docstring).
B = 2000
SEMILLA = 20261021
SUAVIZADO_LAPLACE = 0.5
KAPPA_OBJETIVO = 0.6055
TOLERANCIA_KAPPA = 0.005
NIVEL_COTA = NIVEL_CONFIANZA
N_ESPERADO = 206
N_ETIQUETADO_ESPERADO = 476
N_ARBITRADOS_ESPERADO = 64
N_TRES_VIAS_ESPERADO = 6
ACIERTOS_ESPERADOS = 142
EXACTITUD_ESPERADA = 142 / 206
MACRO_F1_ESPERADA = 0.7024
TOLERANCIA_ANCLA = 1e-4
TOLERANCIA_BISECCION = 1e-12
ETIQUETADORES = ("E3", "E4", "E5")

class AnclaNoReproducida(RuntimeError):
    """Los anclajes calculados no coinciden con los valores canonicos versionados."""


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def _validar_clase(etiqueta: str, clases: list[str]) -> None:
    if etiqueta not in clases:
        raise ValueError(f"Etiqueta fuera de las clases canonicas: {etiqueta!r}")


def construir_kernel(
    referencia: dict[str, str],
    etiquetas: dict[str, dict[str, str]],
    clases: list[str],
    suavizado: float = SUAVIZADO_LAPLACE,
) -> dict:
    """Matriz 5x5 fila-estocastica de la referencia a las etiquetas recolectadas."""
    conteos = {clase: {otra: 0 for otra in clases} for clase in clases}
    soporte = {clase: 0 for clase in clases}
    for caso, clase_referencia in referencia.items():
        _validar_clase(clase_referencia, clases)
        if caso not in etiquetas:
            raise ValueError(f"Caso sin etiquetas: {caso!r}")
        for etiquetador, etiqueta in etiquetas[caso].items():
            _validar_clase(etiqueta, clases)
            conteos[clase_referencia][etiqueta] += 1
            soporte[clase_referencia] += 1

    probabilidades = {}
    for clase in clases:
        denominador = soporte[clase] + suavizado * len(clases)
        if denominador == 0:
            raise ValueError(
                f"Fila sin soporte y sin suavizado para la clase {clase!r}"
            )
        probabilidades[clase] = {
            otra: (conteos[clase][otra] + suavizado) / denominador for otra in clases
        }
    return {
        "conteos": conteos,
        "probabilidades": probabilidades,
        "soporte": soporte,
        "suavizado": suavizado,
    }


def marginal_empirica(referencia: dict[str, str], clases: list[str]) -> dict[str, float]:
    """Distribucion marginal empirica de clases de la referencia."""
    if not referencia:
        raise ValueError("La referencia esta vacia")
    conteos = {clase: 0 for clase in clases}
    for clase in referencia.values():
        _validar_clase(clase, clases)
        conteos[clase] += 1
    total = len(referencia)
    return {clase: conteos[clase] / total for clase in clases}


def mezclar_kernel(
    probabilidades: dict[str, dict[str, float]],
    marginal: dict[str, float],
    lam: float,
    clases: list[str],
) -> dict[str, dict[str, float]]:
    """Mezcla convexa `(1 - lam) * Q + lam * m` repetida por fila."""
    if not 0.0 <= lam <= 1.0:
        raise ValueError(f"lambda fuera de [0, 1]: {lam}")
    return {
        clase: {
            otra: (1.0 - lam) * probabilidades[clase][otra] + lam * marginal[otra]
            for otra in clases
        }
        for clase in clases
    }


def p_o_esperado(
    mezcla: dict[str, dict[str, float]],
    distribucion: dict[str, float],
    clases: list[str],
) -> float:
    """Acuerdo observado esperado entre la referencia y una etiqueta simulada."""
    return sum(distribucion[clase] * mezcla[clase][clase] for clase in clases)


def kappa_esperado(
    mezcla: dict[str, dict[str, float]],
    distribucion: dict[str, float],
    clases: list[str],
) -> float:
    """Kappa de Cohen esperado entre la referencia y una etiqueta de la mezcla."""
    p_o = p_o_esperado(mezcla, distribucion, clases)
    marginal_etiqueta = {
        otra: sum(distribucion[clase] * mezcla[clase][otra] for clase in clases)
        for otra in clases
    }
    p_e = sum(distribucion[clase] * marginal_etiqueta[clase] for clase in clases)
    if abs(1.0 - p_e) < 1e-15:
        raise ValueError("kappa no estimable: p_e = 1")
    return (p_o - p_e) / (1.0 - p_e)


def _evaluar_mezcla(
    probabilidades: dict[str, dict[str, float]],
    distribucion: dict[str, float],
    clases: list[str],
    lam: float,
) -> dict:
    """Kappa y p_o esperados de la mezcla para una intensidad `lam`."""
    mezcla = mezclar_kernel(probabilidades, distribucion, lam, clases)
    return {
        "lambda": lam,
        "kappa": kappa_esperado(mezcla, distribucion, clases),
        "p_o": p_o_esperado(mezcla, distribucion, clases),
    }


def calibrar_lambda(
    probabilidades: dict[str, dict[str, float]],
    distribucion: dict[str, float],
    clases: list[str],
    objetivo: float,
    tolerancia: float,
    iteraciones: int = 200,
) -> dict:
    """Biseccion de `lambda` para reproducir el kappa objetivo."""
    if not 0.0 <= objetivo <= 1.0:
        raise ValueError(f"kappa objetivo fuera de [0, 1]: {objetivo}")

    extremo_cero = _evaluar_mezcla(probabilidades, distribucion, clases, 0.0)
    extremo_uno = _evaluar_mezcla(probabilidades, distribucion, clases, 1.0)
    if abs(extremo_cero["kappa"] - objetivo) <= tolerancia:
        return extremo_cero
    if abs(extremo_uno["kappa"] - objetivo) <= tolerancia:
        return extremo_uno
    if not extremo_uno["kappa"] <= objetivo <= extremo_cero["kappa"]:
        raise ValueError(
            "no hay lambda en [0, 1] que reproduzca el kappa objetivo: "
            f"k(0) = {extremo_cero['kappa']:.6f}, k(1) = {extremo_uno['kappa']:.6f}"
        )

    bajo, alto = 0.0, 1.0
    resultado = _evaluar_mezcla(probabilidades, distribucion, clases, 0.5)
    for _ in range(iteraciones):
        medio = (bajo + alto) / 2.0
        resultado = _evaluar_mezcla(probabilidades, distribucion, clases, medio)
        if resultado["kappa"] > objetivo:
            bajo = medio
        else:
            alto = medio
        if alto - bajo < TOLERANCIA_BISECCION:
            break
    return resultado


def cotas_distribution_free(aciertos: int, n: int, delta: float) -> dict:
    """Cotas de exactitud bajo un presupuesto `delta` de error de referencia."""
    if n <= 0:
        raise ValueError("n debe ser positivo")
    if not 0.0 <= delta <= 1.0:
        raise ValueError(f"delta fuera de [0, 1]: {delta}")
    m = int(round(delta * n))
    inferior = max(0.0, (aciertos - m) / n)
    superior = min(1.0, (aciertos + m) / n)
    return {"delta": delta, "m": m, "inferior": inferior, "superior": superior}


def rango_tres_vias(
    referencia: dict[str, str],
    predicciones: dict[str, str],
    etiquetas: dict[str, dict[str, str]],
    casos_ids: list[str],
    etiquetadores: tuple[str, ...] = ETIQUETADORES,
) -> dict:
    """Rango de exactitud al asignar cada caso de tres vias a cada etiqueta posible."""
    total = len(referencia)
    aciertos_base = sum(
        1 for caso, clase in referencia.items() if predicciones.get(caso) == clase
    )
    casos = []
    delta_min = 0
    delta_max = 0
    for caso_id in casos_ids:
        clase_referencia = referencia[caso_id]
        prediccion = predicciones.get(caso_id)
        asignaciones = {}
        for etiquetador in etiquetadores:
            if etiquetador not in etiquetas.get(caso_id, {}):
                raise ValueError(f"Caso {caso_id!r} sin etiqueta de {etiquetador}")
            etiqueta = etiquetas[caso_id][etiquetador]
            _validar_clase(etiqueta, CLASES)
            asignaciones[etiquetador] = etiqueta
        aciertos_por_asignacion = {
            etiquetador: aciertos_base
            - int(prediccion == clase_referencia)
            + int(prediccion == etiqueta)
            for etiquetador, etiqueta in asignaciones.items()
        }
        deltas = [
            valor - aciertos_base for valor in aciertos_por_asignacion.values()
        ]
        delta_min += min(deltas)
        delta_max += max(deltas)
        casos.append(
            {
                "caso_id": caso_id,
                "asignaciones": asignaciones,
                "referencia_usada": clase_referencia,
                "prediccion": prediccion,
                "acierto_clasificador": prediccion == clase_referencia,
                "aciertos_por_asignacion": aciertos_por_asignacion,
                "rango_aciertos": [aciertos_base + min(deltas), aciertos_base + max(deltas)],
            }
        )
    aciertos_min = aciertos_base + delta_min
    aciertos_max = aciertos_base + delta_max
    return {
        "casos": casos,
        "aciertos_base": aciertos_base,
        "aciertos_min": aciertos_min,
        "aciertos_max": aciertos_max,
        "exactitud_min": aciertos_min / total if total else 0.0,
        "exactitud_max": aciertos_max / total if total else 0.0,
    }


def verificar_anclajes(n: int, aciertos: int, macro_f1: float) -> None:
    """Aborta si los anclajes canonicos no se reproducen."""
    problemas = []
    if n != N_ESPERADO:
        problemas.append(f"n = {n} != {N_ESPERADO}")
    if aciertos != ACIERTOS_ESPERADOS:
        problemas.append(f"aciertos = {aciertos} != {ACIERTOS_ESPERADOS}")
    if abs(macro_f1 - MACRO_F1_ESPERADA) > TOLERANCIA_ANCLA:
        problemas.append(
            f"macro-F1 = {macro_f1:.6f} != {MACRO_F1_ESPERADA:.4f} "
            f"(tolerancia {TOLERANCIA_ANCLA})"
        )
    if problemas:
        raise AnclaNoReproducida("; ".join(problemas))


def probabilidad_media_alternativa(
    mezcla: dict[str, dict[str, float]],
    distribucion: dict[str, float],
    clases: list[str],
) -> float:
    """Probabilidad media de etiqueta alternativa (fuera de la diagonal de la mezcla)."""
    return sum(
        distribucion[clase] * (1.0 - mezcla[clase][clase]) for clase in clases
    )


# ---------------------------------------------------------------------------
# Simulacion Monte Carlo
# ---------------------------------------------------------------------------
def _acumulados(
    probabilidades: dict[str, dict[str, float]], clases: list[str]
) -> dict[str, list[float]]:
    """Probabilidades acumuladas por fila para extraer con un unico `random()`."""
    acumulados = {}
    for clase in clases:
        total = 0.0
        fila = []
        for otra in clases:
            total += probabilidades[clase][otra]
            fila.append(total)
        acumulados[clase] = fila
    return acumulados


def _extraer(generador: random.Random, fila: list[float], clases: list[str]) -> str:
    """Extrae una clase de la fila acumulada con el generador dado."""
    uniforme = generador.random()
    for indice, limite in enumerate(fila):
        if uniforme <= limite:
            return clases[indice]
    return clases[-1]


def kappa_de_vectores(
    referencia: list[str], simulada: list[str], clases: list[str]
) -> float:
    """Kappa de Cohen entre dos vectores de etiquetas (sin bootstrap)."""
    n = len(referencia)
    if n == 0 or n != len(simulada):
        raise ValueError("Los vectores de kappa deben ser no vacios y de igual longitud")
    p_o = sum(1 for a, b in zip(referencia, simulada) if a == b) / n
    margen_referencia = {clase: 0 for clase in clases}
    margen_simulada = {clase: 0 for clase in clases}
    for a, b in zip(referencia, simulada):
        margen_referencia[a] += 1
        margen_simulada[b] += 1
    p_e = sum(
        (margen_referencia[clase] / n) * (margen_simulada[clase] / n)
        for clase in clases
    )
    if abs(1.0 - p_e) < 1e-15:
        raise ValueError("kappa no estimable: p_e = 1")
    return (p_o - p_e) / (1.0 - p_e)


def simular_referencias(
    referencia: dict[str, str],
    predicciones: dict[str, str],
    probabilidades: dict[str, dict[str, float]],
    distribucion: dict[str, float],
    lam: float,
    replicas: int,
    semilla: int,
    clases: list[str],
) -> dict:
    """Simula `replicas` referencias alternativas y recalcula exactitud y macro-F1."""
    mezcla = mezclar_kernel(probabilidades, distribucion, lam, clases)
    acumulados = _acumulados(mezcla, clases)
    ids = list(referencia)
    for caso in ids:
        if caso not in predicciones:
            raise ValueError(f"Caso sin prediccion: {caso!r}")
    n = len(ids)
    generador = random.Random(semilla)
    aciertos: list[int] = []
    macro_f1: list[float] = []
    kappas: list[float] = []
    for _ in range(replicas):
        reales: list[str] = []
        predichos: list[str] = []
        for caso in ids:
            reales.append(_extraer(generador, acumulados[referencia[caso]], clases))
            predichos.append(predicciones[caso])
        aciertos.append(sum(1 for a, b in zip(reales, predichos) if a == b))
        macro_f1.append(f1_macro(f1_por_clase(matriz_confusion(reales, predichos))))
        kappas.append(kappa_de_vectores([referencia[i] for i in ids], reales, clases))

    valores_exactitud = [acierto / n for acierto in aciertos]
    valores_macro = list(macro_f1)
    errores = [n - acierto for acierto in aciertos]
    q_exactitud = percentil_intervalo(valores_exactitud, NIVEL_CONFIANZA)
    q_macro = percentil_intervalo(valores_macro, NIVEL_CONFIANZA)
    q_errores = percentil_intervalo(errores, NIVEL_CONFIANZA)
    media_kappa = statistics.mean(kappas)
    return {
        "B": replicas,
        "semilla": semilla,
        "exactitud": {
            "aciertos": aciertos,
            "valores": [round(valor, 6) for valor in valores_exactitud],
            "mediana": round(statistics.median(valores_exactitud), 6),
            "q2_5": round(q_exactitud[0], 6),
            "q97_5": round(q_exactitud[1], 6),
            "proporcion_ge_0_6893": sum(
                1 for acierto in aciertos if acierto / n >= EXACTITUD_ESPERADA
            )
            / replicas,
        },
        "macro_f1": {
            "valores": [round(valor, 6) for valor in valores_macro],
            "mediana": round(statistics.median(valores_macro), 6),
            "q2_5": round(q_macro[0], 6),
            "q97_5": round(q_macro[1], 6),
        },
        "errores": {
            "valores": errores,
            "mediana": round(statistics.median(errores), 6),
            "q2_5": round(q_errores[0], 6),
            "q97_5": round(q_errores[1], 6),
        },
        "kappa": {
            "media": round(media_kappa, 6),
            "desvio": round(statistics.pstdev(kappas), 6),
            "min": round(min(kappas), 6),
            "max": round(max(kappas), 6),
            "dentro_de_tolerancia": abs(media_kappa - KAPPA_OBJETIVO)
            <= TOLERANCIA_KAPPA,
        },
    }


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------
def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


class EntradaInconsistente(ValueError):
    """Los conteos o los identificadores de las entradas no coinciden."""


def cargar_entradas(
    ruta_corpus: pathlib.Path = RUTA_CORPUS,
    ruta_predicciones: pathlib.Path = RUTA_PREDICCIONES,
    ruta_etiquetado: pathlib.Path = RUTA_ETIQUETADO,
    ruta_arbitraje: pathlib.Path = RUTA_ARBITRAJE,
) -> dict:
    """Lee y valida los cuatro artefactos versionados; no escribe nada."""
    corpus = json.loads(ruta_corpus.read_text(encoding="utf-8"))
    referencia = {caso["id"]: caso["sector_asignado"] for caso in corpus["casos"]}
    if len(referencia) != len(corpus["casos"]):
        raise EntradaInconsistente("Identificadores de caso duplicados en el corpus")

    predicciones_crudas = json.loads(ruta_predicciones.read_text(encoding="utf-8"))
    predicciones = {
        prediccion["caso_id"]: prediccion["sector_predicho"]
        for prediccion in predicciones_crudas["predictions"]
    }

    etiquetas: dict[str, dict[str, str]] = {}
    filas = 0
    with ruta_etiquetado.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            filas += 1
            etiquetas.setdefault(fila["id_caso"], {})[fila["id_etiquetador"]] = fila[
                "sector_etiquetado"
            ]

    arbitraje = json.loads(ruta_arbitraje.read_text(encoding="utf-8"))
    origen = {caso["id"]: caso["origen"] for caso in arbitraje["casos"]}
    tres_vias_ids = [caso["id"] for caso in arbitraje["casos"] if caso["tres_vias"]]

    n_arbitrados = sum(1 for valor in origen.values() if valor == "arbitraje_e5")
    conteos = {
        "casos": len(referencia),
        "filas_etiquetado": filas,
        "arbitrados_e5": n_arbitrados,
        "tres_vias": len(tres_vias_ids),
        "predicciones": len(predicciones),
    }
    esperados = {
        "casos": N_ESPERADO,
        "filas_etiquetado": N_ETIQUETADO_ESPERADO,
        "arbitrados_e5": N_ARBITRADOS_ESPERADO,
        "tres_vias": N_TRES_VIAS_ESPERADO,
        "predicciones": N_ESPERADO,
    }
    diferencias = [
        f"{clave}: {conteos[clave]} != {esperado}"
        for clave, esperado in esperados.items()
        if conteos[clave] != esperado
    ]
    if diferencias:
        raise EntradaInconsistente("; ".join(diferencias))
    faltan_predicciones = [caso for caso in referencia if caso not in predicciones]
    if faltan_predicciones:
        raise EntradaInconsistente(f"Casos sin prediccion: {faltan_predicciones[:5]}")
    faltan_etiquetas = [caso for caso in referencia if caso not in etiquetas]
    if faltan_etiquetas:
        raise EntradaInconsistente(f"Casos sin etiquetas: {faltan_etiquetas[:5]}")
    if set(origen) != set(referencia):
        raise EntradaInconsistente("El sidecar de arbitraje no cubre los mismos casos")

    return {
        "referencia": referencia,
        "predicciones": predicciones,
        "etiquetas": etiquetas,
        "origen": origen,
        "tres_vias_ids": tres_vias_ids,
        "conteos": conteos,
        "entradas_sha256": {
            pathlib.Path(ruta).name: sha256(pathlib.Path(ruta))
            for ruta in (
                ruta_corpus,
                ruta_predicciones,
                ruta_etiquetado,
                ruta_arbitraje,
            )
        },
    }


def calcular_anclajes(
    referencia: dict[str, str], predicciones: dict[str, str]
) -> dict:
    """Exactitud estricta y macro-F1 de las predicciones fijas contra la referencia."""
    reales = [referencia[caso] for caso in referencia]
    predichos = [predicciones[caso] for caso in referencia]
    aciertos = sum(1 for a, b in zip(reales, predichos) if a == b)
    macro_f1 = f1_macro(f1_por_clase(matriz_confusion(reales, predichos)))
    return {
        "n": len(reales),
        "aciertos_estrictos": aciertos,
        "exactitud_estricta": aciertos / len(reales),
        "macro_f1": macro_f1,
    }


def acuerdo_e3_e4(
    referencia: dict[str, str],
    etiquetas: dict[str, dict[str, str]],
    clases: list[str],
    n_principales: int = 150,
) -> dict:
    """Acuerdo y kappa E3/E4 sobre los primeros `n_principales` casos del corpus."""
    ids = list(referencia)[:n_principales]
    pares = [(etiquetas[caso]["E3"], etiquetas[caso]["E4"]) for caso in ids]
    coincidencias = sum(1 for a, b in pares if a == b)
    p_o = coincidencias / len(pares)
    return {
        "n": len(pares),
        "coincidencias": coincidencias,
        "p_o": p_o,
        "kappa": kappa_de_vectores(
            [a for a, _ in pares], [b for _, b in pares], clases
        ),
    }


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def construir_documento(
    entradas: dict | None = None,
    *,
    replicas: int = B,
    semilla: int = SEMILLA,
) -> dict:
    """Construye el documento completo; aborta antes de simular si un ancla falla."""
    if entradas is None:
        entradas = cargar_entradas()
    referencia = entradas["referencia"]
    predicciones = entradas["predicciones"]
    etiquetas = entradas["etiquetas"]
    n = len(referencia)

    anclajes = calcular_anclajes(referencia, predicciones)
    verificar_anclajes(
        anclajes["n"], anclajes["aciertos_estrictos"], anclajes["macro_f1"]
    )
    acuerdo = acuerdo_e3_e4(referencia, etiquetas, CLASES)

    kernel = construir_kernel(referencia, etiquetas, CLASES, SUAVIZADO_LAPLACE)
    marginal = marginal_empirica(referencia, CLASES)
    calibracion = calibrar_lambda(
        kernel["probabilidades"], marginal, CLASES, KAPPA_OBJETIVO, TOLERANCIA_KAPPA
    )
    mezcla = mezclar_kernel(
        kernel["probabilidades"], marginal, calibracion["lambda"], CLASES
    )
    media_alternativa = probabilidad_media_alternativa(mezcla, marginal, CLASES)
    _, delta = intervalo_wilson(media_alternativa * n, n, NIVEL_COTA)
    cotas = cotas_distribution_free(
        anclajes["aciertos_estrictos"], n, delta
    )
    simulacion = simular_referencias(
        referencia,
        predicciones,
        kernel["probabilidades"],
        marginal,
        calibracion["lambda"],
        replicas,
        semilla,
        CLASES,
    )
    tres_vias = rango_tres_vias(
        referencia, predicciones, etiquetas, entradas["tres_vias_ids"]
    )

    errores_observados = n - anclajes["aciertos_estrictos"]
    error_robusto = simulacion["errores"]["q2_5"]
    error_atribuible = errores_observados - error_robusto

    return {
        "change": "c-216-robustecer-la-referencia-el-gate-y-la-forma",
        "generador": "evaluation/data/campana/analisis/analisis_ruido_referencia_c216.py",
        "metodo": (
            "Monte Carlo de referencias alternativas calibrado al acuerdo E3/E4: kernel "
            "fila-estocastico con suavizado de Laplace 0,5, mezcla convexa con la marginal "
            "empirica, lambda por biseccion al kappa 0,6055, cotas distribution-free con "
            "delta de Wilson y rango de los casos de tres vias. Solo lectura, sin red ni "
            "Gemini; no reclasifica ni reentrena."
        ),
        "preregistro": {
            "fijado_en_docstring": True,
            "ciego": False,
            "declaracion": (
                "El metodo y los parametros se fijaron antes de generar las salidas. El "
                "prerregistro NO fue ciego: el corpus, las predicciones y los agregados "
                "canonicos ya se conocian; no se habia observado la distribucion simulada."
            ),
        },
        "parametros": {
            "B": replicas,
            "semilla": semilla,
            "suavizado_laplace": SUAVIZADO_LAPLACE,
            "kappa_objetivo": KAPPA_OBJETIVO,
            "tolerancia_kappa": TOLERANCIA_KAPPA,
            "nivel_cota": NIVEL_COTA,
            "replicas": replicas,
        },
        "entradas_sha256": entradas["entradas_sha256"],
        "conteos": entradas["conteos"],
        "anclajes": {
            "n": anclajes["n"],
            "aciertos_estrictos": anclajes["aciertos_estrictos"],
            "exactitud_estricta": round(anclajes["exactitud_estricta"], 6),
            "macro_f1": round(anclajes["macro_f1"], 6),
            "verificados": True,
            "acuerdo_e3_e4": {
                "n": acuerdo["n"],
                "coincidencias": acuerdo["coincidencias"],
                "p_o": round(acuerdo["p_o"], 6),
                "kappa": round(acuerdo["kappa"], 6),
            },
        },
        "kernel": {
            "suavizado_laplace": SUAVIZADO_LAPLACE,
            "conteos": kernel["conteos"],
            "probabilidades": {
                clase: {otra: round(valor, 6) for otra, valor in fila.items()}
                for clase, fila in kernel["probabilidades"].items()
            },
            "soporte": kernel["soporte"],
        },
        "calibracion": {
            "kappa_objetivo": KAPPA_OBJETIVO,
            "tolerancia": TOLERANCIA_KAPPA,
            "lambda": round(calibracion["lambda"], 6),
            "kappa_esperado": round(calibracion["kappa"], 6),
            "p_o_esperado": round(calibracion["p_o"], 6),
            "p_o_observado": round(acuerdo["p_o"], 6),
            "verificacion_simulada": simulacion["kappa"],
        },
        "simulacion": {
            "B": simulacion["B"],
            "semilla": simulacion["semilla"],
            "exactitud": simulacion["exactitud"],
            "macro_f1": simulacion["macro_f1"],
            "errores": simulacion["errores"],
        },
        "descomposicion": {
            "errores_observados": errores_observados,
            "intervalo_errores": [
                simulacion["errores"]["q2_5"],
                simulacion["errores"]["q97_5"],
            ],
            "error_robusto": error_robusto,
            "error_atribuible_referencia": error_atribuible,
            "rotulo": (
                "sensibilidad, no causalidad ni verdad latente; un componente negativo "
                "significa que el error observado es menor que el extremo favorable simulado"
            ),
        },
        "cotas": {
            "metodo": (
                "distribution-free: [max(0, (aciertos - m) / n), min(1, (aciertos + m) / n)] "
                "con m = round(delta * n) y delta = cota superior de Wilson al 95 % de la "
                "probabilidad media de etiqueta alternativa de Q_lambda*"
            ),
            "delta": round(delta, 6),
            "m": cotas["m"],
            "inferior": round(cotas["inferior"], 6),
            "superior": round(cotas["superior"], 6),
            "rotulo": "cotas de sensibilidad bajo un presupuesto de error de referencia, no mediciones",
        },
        "tres_vias": {
            "n": len(tres_vias["casos"]),
            "aciertos_base": tres_vias["aciertos_base"],
            "aciertos_min": tres_vias["aciertos_min"],
            "aciertos_max": tres_vias["aciertos_max"],
            "exactitud_min": round(tres_vias["exactitud_min"], 6),
            "exactitud_max": round(tres_vias["exactitud_max"], 6),
            "casos": tres_vias["casos"],
        },
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "declaracion": (
                "Las cifras de este analisis son aditivas: no reemplazan ningun numero "
                "canonico de la tesis (seccion 3.27 del memo), no cambian el corpus, las "
                "predicciones ni los artefactos congelados, y la simulacion se rotula como "
                "sensibilidad, no como medicion de la verdad latente."
            ),
        },
    }


def _num(valor: float, decimales: int = 4) -> str:
    return f"{valor:.{decimales}f}"


def renderizar(doc: dict) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF."""
    texto_json = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    lineas = [
        "# Sensibilidad a referencias alternativas plausibles (c-216)",
        "",
        f"Sobre los {doc['anclajes']['n']} casos de la referencia arbitrada. "
        f"{doc['aditivo']['declaracion']}",
        "",
        "## Preregistro",
        "",
        f"- Fijado en el docstring antes de generar las salidas: "
        f"{doc['preregistro']['fijado_en_docstring']}.",
        f"- Ciego: {doc['preregistro']['ciego']}. {doc['preregistro']['declaracion']}",
        "",
        "## Anclajes canonicos",
        "",
        "| Indicador | Valor observado |",
        "|---|---|",
        f"| Exactitud estricta | {doc['anclajes']['aciertos_estrictos']}/"
        f"{doc['anclajes']['n']} ({_num(doc['anclajes']['exactitud_estricta'])}) |",
        f"| Macro-F1 | {_num(doc['anclajes']['macro_f1'])} |",
        f"| Acuerdo E3/E4 (primeros {doc['anclajes']['acuerdo_e3_e4']['n']} casos) | "
        f"{doc['anclajes']['acuerdo_e3_e4']['coincidencias']}/"
        f"{doc['anclajes']['acuerdo_e3_e4']['n']} "
        f"(p_o = {_num(doc['anclajes']['acuerdo_e3_e4']['p_o'])}) |",
        f"| Kappa E3/E4 | {_num(doc['anclajes']['acuerdo_e3_e4']['kappa'])} |",
        "",
        "## Kernel empirico",
        "",
        f"Suavizado de Laplace: {doc['kernel']['suavizado_laplace']}. Soporte por fila: "
        + ", ".join(
            f"{clase} = {soporte}" for clase, soporte in doc["kernel"]["soporte"].items()
        )
        + ".",
        "",
        "## Calibracion de lambda",
        "",
        f"- lambda* = {_num(doc['calibracion']['lambda'], 6)}",
        f"- kappa esperado = {_num(doc['calibracion']['kappa_esperado'], 6)} "
        f"(objetivo {_num(doc['calibracion']['kappa_objetivo'])}; tolerancia "
        f"{_num(doc['calibracion']['tolerancia'])})",
        f"- p_o esperado = {_num(doc['calibracion']['p_o_esperado'], 6)}; "
        f"p_o observado = {_num(doc['calibracion']['p_o_observado'], 6)}",
        f"- Verificacion simulada: kappa medio = "
        f"{_num(doc['calibracion']['verificacion_simulada']['media'], 6)}; "
        f"desvio = {_num(doc['calibracion']['verificacion_simulada']['desvio'], 6)}; "
        f"dentro de tolerancia = "
        f"{doc['calibracion']['verificacion_simulada']['dentro_de_tolerancia']}",
        "",
        "## Distribucion bajo referencias alternativas",
        "",
        f"{doc['simulacion']['B']} replicas, semilla {doc['simulacion']['semilla']}.",
        "",
        "| Indicador | Observado | Mediana | q2,5 | q97,5 |",
        "|---|---|---|---|---|",
        f"| Exactitud estricta | {_num(doc['anclajes']['exactitud_estricta'])} | "
        f"{_num(doc['simulacion']['exactitud']['mediana'])} | "
        f"{_num(doc['simulacion']['exactitud']['q2_5'])} | "
        f"{_num(doc['simulacion']['exactitud']['q97_5'])} |",
        f"| Macro-F1 | {_num(doc['anclajes']['macro_f1'])} | "
        f"{_num(doc['simulacion']['macro_f1']['mediana'])} | "
        f"{_num(doc['simulacion']['macro_f1']['q2_5'])} | "
        f"{_num(doc['simulacion']['macro_f1']['q97_5'])} |",
        "",
        f"- Proporcion de replicas con exactitud mayor o igual a 0,6893: "
        f"{_num(doc['simulacion']['exactitud']['proporcion_ge_0_6893'])}.",
        "",
        "## Descomposicion del error",
        "",
        f"- Errores observados: {doc['descomposicion']['errores_observados']}.",
        f"- Intervalo de errores bajo referencias alternativas: "
        f"[{_num(doc['descomposicion']['intervalo_errores'][0])}; "
        f"{_num(doc['descomposicion']['intervalo_errores'][1])}].",
        f"- Error robusto (extremo favorable): {_num(doc['descomposicion']['error_robusto'])}.",
        f"- Error atribuible a la referencia: "
        f"{_num(doc['descomposicion']['error_atribuible_referencia'])}. "
        f"{doc['descomposicion']['rotulo']}.",
        "",
        "## Cotas distribution-free",
        "",
        f"- delta = {_num(doc['cotas']['delta'], 6)}; m = {doc['cotas']['m']}.",
        f"- Cotas de exactitud estricta: "
        f"[{_num(doc['cotas']['inferior'])}; {_num(doc['cotas']['superior'])}].",
        f"- {doc['cotas']['rotulo']}.",
        "",
        "## Casos de tres vias",
        "",
        "| Caso | E3 | E4 | E5 | Referencia | Acierto | Rango de exactitud |",
        "|---|---|---|---|---|---|---|",
    ]
    for caso in doc["tres_vias"]["casos"]:
        lineas.append(
            f"| {caso['caso_id']} | {caso['asignaciones']['E3']} | "
            f"{caso['asignaciones']['E4']} | {caso['asignaciones']['E5']} | "
            f"{caso['referencia_usada']} | {caso['acierto_clasificador']} | "
            f"[{caso['rango_aciertos'][0]}/{doc['anclajes']['n']}; "
            f"{caso['rango_aciertos'][1]}/{doc['anclajes']['n']}] |"
        )
    lineas += [
        "",
        f"Rango agregado: {doc['tres_vias']['aciertos_min']}/"
        f"{doc['anclajes']['n']} a {doc['tres_vias']['aciertos_max']}/"
        f"{doc['anclajes']['n']} "
        f"({_num(doc['tres_vias']['exactitud_min'])} a "
        f"{_num(doc['tres_vias']['exactitud_max'])}). "
        "No se elige una etiqueta verdadera: el rango es el resultado.",
        "",
        "## Entradas y SHA-256",
        "",
        "| Archivo | SHA-256 |",
        "|---|---|",
    ]
    for nombre, digest in doc["entradas_sha256"].items():
        lineas.append(f"| `{nombre}` | `{digest}` |")
    lineas.append("")
    return texto_json, "\n".join(lineas) + "\n"


def escribir(
    doc: dict,
    directorio: pathlib.Path = SALIDA,
    nombre_base: str = NOMBRE_BASE,
) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `SHA256SUMS` (UTF-8 sin BOM, LF)."""
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(doc)
    rutas = []
    for nombre, texto in (
        (f"{nombre_base}.json", texto_json),
        (f"{nombre_base}.md", texto_md),
    ):
        ruta = directorio / nombre
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    sumas = "".join(f"{sha256(ruta)}  {ruta.name}\n" for ruta in rutas)
    ruta_sumas = directorio / f"{nombre_base}.SHA256SUMS.txt"
    ruta_sumas.write_bytes(sumas.encode("utf-8"))
    rutas.append(ruta_sumas)
    return rutas


def ejecutar(
    salida: pathlib.Path = SALIDA,
    nombre_base: str = NOMBRE_BASE,
    *,
    replicas: int = B,
    semilla: int = SEMILLA,
) -> list[pathlib.Path]:
    """Construye y escribe el analisis; no escribe si un ancla no se reproduce."""
    doc = construir_documento(replicas=replicas, semilla=semilla)
    return escribir(doc, salida, nombre_base=nombre_base)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument("--nombre", default=NOMBRE_BASE)
    parser.add_argument("--replicas", type=int, default=B)
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    args = parser.parse_args(argv)
    try:
        rutas = ejecutar(
            args.salida,
            args.nombre,
            replicas=args.replicas,
            semilla=args.semilla,
        )
    except (AnclaNoReproducida, EntradaInconsistente, ValueError) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    for ruta in rutas:
        print(f"{sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
