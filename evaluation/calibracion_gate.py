"""Calibracion y discriminacion de la confianza del gate (c-214).

Funciones puras y deterministas, sin red ni modelo. Reutilizan `evaluation.metrics` para el
bootstrap y el IC de Wilson.
"""

from __future__ import annotations

import random
from typing import Callable, Optional, Sequence

from evaluation.metrics import (
    NIVEL_CONFIANZA,
    REMUESTREOS_BOOTSTRAP,
    SEMILLA_BOOTSTRAP,
    intervalo_wilson,
    percentil_intervalo,
    remuestreos_indices,
)

BANDAS_ECE = 10


def _validar(senales: Sequence[float], aciertos: Sequence[bool]) -> None:
    if len(senales) != len(aciertos):
        raise ValueError("la senal y los aciertos deben tener la misma longitud.")
    if len(senales) == 0:
        raise ValueError("no hay observaciones.")
    if any(not (0.0 <= s <= 1.0) for s in senales):
        raise ValueError("la senal debe estar en [0, 1].")


def auroc(senales: Sequence[float], aciertos: Sequence[bool]) -> Optional[float]:
    """AUROC de la senal para separar aciertos de errores (Mann-Whitney, empates a 0,5).

    Devuelve `None` si falta alguna de las dos clases (no definido).
    """
    _validar(senales, aciertos)
    positivos = [s for s, a in zip(senales, aciertos) if a]
    negativos = [s for s, a in zip(senales, aciertos) if not a]
    if not positivos or not negativos:
        return None
    suma = 0.0
    for p in positivos:
        for n in negativos:
            suma += 1.0 if p > n else 0.5 if p == n else 0.0
    return suma / (len(positivos) * len(negativos))


def ece(
    senales: Sequence[float], aciertos: Sequence[bool], bandas: int = BANDAS_ECE
) -> float:
    """ECE con `bandas` bandas de igual ancho en [0, 1] (la ultima cerrada en 1,0)."""
    _validar(senales, aciertos)
    n = len(senales)
    grupos: dict[int, list[tuple[float, bool]]] = {}
    for s, a in zip(senales, aciertos):
        indice = min(int(s * bandas), bandas - 1)
        grupos.setdefault(indice, []).append((s, a))
    total = 0.0
    for observaciones in grupos.values():
        k = len(observaciones)
        confianza_media = sum(s for s, _ in observaciones) / k
        exactitud = sum(1 for _, a in observaciones if a) / k
        total += (k / n) * abs(confianza_media - exactitud)
    return total


def brier(senales: Sequence[float], aciertos: Sequence[bool]) -> float:
    """Puntaje de Brier: media de (senal - acierto)^2."""
    _validar(senales, aciertos)
    return sum((s - (1.0 if a else 0.0)) ** 2 for s, a in zip(senales, aciertos)) / len(senales)


def sobreconfianza(senales: Sequence[float], aciertos: Sequence[bool]) -> float:
    """Confianza media menos exactitud."""
    _validar(senales, aciertos)
    n = len(senales)
    return sum(senales) / n - sum(1 for a in aciertos if a) / n


def ic_bootstrap_metrica(
    senales: Sequence[float],
    aciertos: Sequence[bool],
    metrica: Callable[[Sequence[float], Sequence[bool]], Optional[float]],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> dict:
    """Valor de la metrica con IC95 bootstrap percentil por caso.

    Las remuestras en las que la metrica no esta definida (`None`) se omiten y se cuentan en
    `remuestras_validas`. Si la metrica no esta definida en la muestra original, `ic = None`.
    """
    _validar(senales, aciertos)
    valor = metrica(senales, aciertos)
    generador = random.Random(semilla)
    valores: list[float] = []
    for indices in remuestreos_indices(generador, len(senales), remuestreos):
        v = metrica([senales[i] for i in indices], [aciertos[i] for i in indices])
        if v is not None:
            valores.append(v)
    ic = None
    if valor is not None and valores:
        ic = list(percentil_intervalo(valores, NIVEL_CONFIANZA))
    return {
        "valor": valor,
        "ic": ic,
        "remuestras_validas": len(valores),
        "nivel_confianza": NIVEL_CONFIANZA,
        "semilla": semilla,
        "remuestreos": remuestreos,
    }


# ---------------------------------------------------------------------------
# Barrido de umbral y regla de seleccion (D3, D4)
# ---------------------------------------------------------------------------
MIN_ACEPTADOS = 10


def barrido_umbral(
    senales: Sequence[float],
    aciertos: Sequence[bool],
    umbrales: Sequence[float],
    *,
    n_total_corpus: int,
) -> list[dict]:
    """Politica «aceptar si senal >= t» para cada umbral (`inf` = derivar todo lo escalado).

    `senales`/`aciertos` son los casos escalados; `n_total_corpus` es el total de casos del
    corpus (denominador de la carga de revision del sistema).
    """
    if len(senales) != len(aciertos):
        raise ValueError("la senal y los aciertos deben tener la misma longitud.")
    if n_total_corpus <= 0:
        raise ValueError("n_total_corpus debe ser positivo.")
    filas: list[dict] = []
    for t in umbrales:
        aceptados = [a for s, a in zip(senales, aciertos) if s >= t]
        derivados = [a for s, a in zip(senales, aciertos) if s < t]
        k, d = len(aceptados), len(derivados)
        ok = sum(1 for a in aceptados if a)
        filas.append(
            {
                "umbral": t,
                "escalados": len(senales),
                "aceptados": k,
                "derivados": d,
                "cobertura": k / len(senales) if senales else 0.0,
                "aciertos_aceptados": ok,
                "exactitud_selectiva": ok / k if k else None,
                "ic_wilson": list(intervalo_wilson(ok, k)) if k else None,
                "exactitud_derivados": (
                    sum(1 for a in derivados if a) / d if d else None
                ),
                "errores_atrapados": sum(1 for a in derivados if not a),
                "errores_aceptados": sum(1 for a in aceptados if not a),
                "carga_revision": d / n_total_corpus,
            }
        )
    return filas


def seleccionar_umbral(
    barrido: Sequence[dict], *, piso: float, min_aceptados: int = MIN_ACEPTADOS
) -> Optional[float]:
    """Menor `t` (distinto de `inf`) con exactitud selectiva >= `piso` y >= `min_aceptados`."""
    candidatos = [
        f["umbral"]
        for f in barrido
        if f["umbral"] != float("inf")
        and f["aceptados"] >= min_aceptados
        and f["exactitud_selectiva"] is not None
        and f["exactitud_selectiva"] >= piso
    ]
    return min(candidatos) if candidatos else None


def evaluar_fuera_de_muestra_gate(
    umbral: Optional[float],
    senales: Sequence[float],
    aciertos: Sequence[bool],
    *,
    piso: float,
    n_total_corpus: int,
    min_aceptados: int = MIN_ACEPTADOS,
) -> dict:
    """Evalua SIN reajuste el umbral elegido dentro de la muestra (resultado de tres vias).

    No recibe candidatos: no puede reelegir el umbral con estos datos. Si `umbral` es `None`
    (nada cumplio el piso dentro de la muestra) el veredicto es «sin umbral seleccionado».
    """
    if umbral is None:
        return {"umbral": None, "veredicto": "sin umbral seleccionado"}
    fila = barrido_umbral(senales, aciertos, [umbral], n_total_corpus=n_total_corpus)[0]
    sel, der = fila["exactitud_selectiva"], fila["exactitud_derivados"]
    if fila["aceptados"] < min_aceptados or fila["derivados"] == 0:
        veredicto = "no estimable"
    elif sel >= piso and der < sel:
        veredicto = "confirmado"
    else:
        veredicto = "no confirmado"
    return {**fila, "piso": piso, "min_aceptados": min_aceptados, "veredicto": veredicto}


# ---------------------------------------------------------------------------
# Recalibracion isotonica (solo correccion de nivel)
# ---------------------------------------------------------------------------
def ajustar_isotonica(
    senales: Sequence[float], aciertos: Sequence[bool]
) -> list[tuple[float, float]]:
    """Regresion isotonica (PAVA ponderada) de aciertos sobre la senal.

    Devuelve `[(x, valor)]` con un punto por valor distinto de la senal, no decreciente.
    """
    _validar(senales, aciertos)
    por_x: dict[float, list[float]] = {}
    for s, a in zip(senales, aciertos):
        acumulado = por_x.setdefault(s, [0.0, 0.0])
        acumulado[0] += 1.0 if a else 0.0
        acumulado[1] += 1.0
    xs = sorted(por_x)
    bloques: list[list] = []  # [suma, peso, [xs del bloque]]
    for x in xs:
        bloques.append([por_x[x][0], por_x[x][1], [x]])
        while len(bloques) > 1 and (
            bloques[-2][0] / bloques[-2][1] > bloques[-1][0] / bloques[-1][1]
        ):
            ultimo = bloques.pop()
            bloques[-1][0] += ultimo[0]
            bloques[-1][1] += ultimo[1]
            bloques[-1][2].extend(ultimo[2])
    return [(x, b[0] / b[1]) for b in bloques for x in b[2]]


def aplicar_isotonica(
    modelo: Sequence[tuple[float, float]], senales: Sequence[float]
) -> list[float]:
    """Funcion escalon: valor del mayor `x` ajustado <= senal (el primero si esta por debajo)."""
    if not modelo:
        raise ValueError("el modelo isotonico esta vacio.")
    salida: list[float] = []
    for s in senales:
        valor = modelo[0][1]
        for x, v in modelo:
            if x <= s:
                valor = v
            else:
                break
        salida.append(valor)
    return salida


# ---------------------------------------------------------------------------
# Senales de las reglas recomputadas offline (D5)
# ---------------------------------------------------------------------------
ACUERDO = "acuerdo"
DESACUERDO = "desacuerdo"
SIN_PREDICCION_REGLAS = "sin_prediccion_reglas"
NO_APLICA = "no_aplica"
TAU_CORTOCIRCUITO = 0.5166

#: Entorno inerte para construir `Settings` del backend sin credenciales reales (sin red).
ENTORNO_OFFLINE_C214 = {
    "DATABASE_URL": "postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy",
    "GEMINI_API_KEY": "offline-dummy-key-sin-llamadas",  # gitleaks:allow (ficticio)
    "PSEUDONYMIZATION_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",  # gitleaks:allow (ficticio)
    "JWT_SECRET_KEY": "ci-dummy-jwt-secret-key-for-testing-only",  # gitleaks:allow (ficticio)
    "COST_GUARD_CALLER_HMAC_KEY": "ci-dummy-cost-guard-caller-hmac-key",  # gitleaks:allow (ficticio)
    "DIRECTORY_BLIND_INDEX_KEY": "ci-dummy-directory-blind-index-key",  # gitleaks:allow (ficticio)
}


def asegurar_backend_en_path() -> None:
    """Agrega `App/Backend` a `sys.path` para importar el clasificador real (diferido)."""
    import pathlib
    import sys

    backend = str(pathlib.Path(__file__).resolve().parents[1] / "App" / "Backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)


def cargar_clasificador_deterministico():
    """`DeterministicClassifier` real; requiere el entorno de `ENTORNO_OFFLINE_C214`."""
    asegurar_backend_en_path()
    from app.classifiers.deterministic import DeterministicClassifier  # type: ignore

    return DeterministicClassifier()


def recomputar_senales_reglas(
    predicciones: Sequence, clasificador, *, tau: float = TAU_CORTOCIRCUITO
) -> list[dict]:
    """Recomputa `score_correctitud`, sector y acuerdo con Gemini de las reglas, caso a caso.

    `predicciones` son mapeos con `caso_id`, `descripcion`, `etapa` y `sector_predicho`. El
    cortocircuito replica `HybridClassifier`: sin ausencia de senal ni empate y
    `score_correctitud >= tau`. El sector de las reglas es `None` si no hay ganador unico.
    """
    import asyncio

    async def _correr() -> list:
        return [await clasificador.classify(p["descripcion"]) for p in predicciones]

    resultados = asyncio.run(_correr())
    filas: list[dict] = []
    for p, r in zip(predicciones, resultados):
        sin_ganador = bool(r.sin_prediccion) or bool(r.ambiguo)
        score = float(r.score_correctitud)
        sector = None if sin_ganador else r.sector_predicho
        cortocircuita = (not sin_ganador) and score >= tau
        if cortocircuita:
            acuerdo = NO_APLICA
        elif sector is None:
            acuerdo = SIN_PREDICCION_REGLAS
        else:
            acuerdo = ACUERDO if sector == p["sector_predicho"] else DESACUERDO
        filas.append(
            {
                "caso_id": p["caso_id"],
                "score_correctitud": score,
                "sector_reglas": sector,
                "cortocircuita": cortocircuita,
                "acuerdo_con_gemini": acuerdo,
            }
        )
    return filas


def verificar_reproduccion_cortocircuito(
    senales: Sequence[dict], predicciones: Sequence
) -> dict:
    """Exige que el recomputo reproduzca la etapa y el sector de los cortocircuitados.

    Lanza `ValueError` («deriva») ante cualquier diferencia respecto de la cache.
    """
    if len(senales) != len(predicciones):
        raise ValueError("deriva: distinta cantidad de casos entre el recomputo y la cache.")
    diferencias: list[str] = []
    cortos = 0
    for s, p in zip(senales, predicciones):
        if s["caso_id"] != p["caso_id"]:
            diferencias.append(f"{s['caso_id']}!={p['caso_id']}: orden distinto")
            continue
        es_det = p["etapa"] == "deterministic"
        if s["cortocircuita"] != es_det:
            diferencias.append(f"{p['caso_id']}: etapa recomputada distinta de {p['etapa']}")
        elif es_det:
            cortos += 1
            if s["sector_reglas"] != p["sector_predicho"]:
                diferencias.append(
                    f"{p['caso_id']}: sector {s['sector_reglas']} != {p['sector_predicho']}"
                )
    if diferencias:
        raise ValueError(
            f"deriva del clasificador determinista ({len(diferencias)} casos): "
            + "; ".join(diferencias[:10])
        )
    return {"cortocircuitados": cortos, "total": len(predicciones)}
