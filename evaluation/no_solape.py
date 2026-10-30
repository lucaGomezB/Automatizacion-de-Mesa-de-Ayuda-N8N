"""
Verificacion de no solape entre el corpus de ajuste y un corpus independiente (c-166, ECM-006).

Es el paso previo obligatorio antes de clasificar el corpus independiente. Es una
funcion pura sobre dos secuencias de `CasoEvaluacion`: no lee archivos ni usa red.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Sequence

from evaluation.corpus import CasoEvaluacion

#: Prefijo obligatorio de los ids del corpus independiente (`I001`, `I002`, ...).
PREFIJO_ID_INDEPENDIENTE = "I"


class SolapeError(ValueError):
    """El corpus candidato solapa el de ajuste o incumple el formato de ids."""


@dataclass(frozen=True)
class AdvertenciaSimilitud:
    """Par candidato/ajuste cuya similitud Jaccard de tokens supera el umbral pedido."""

    id_candidato: str
    id_ajuste: str
    similitud: float


def normalizar_descripcion(descripcion: str) -> str:
    """NFKC, minusculas y espacios colapsados y recortados (tabs y saltos incluidos)."""
    return " ".join(unicodedata.normalize("NFKC", descripcion).lower().split())


def _huella(descripcion: str) -> str:
    """SHA-256 de la descripcion normalizada."""
    return hashlib.sha256(normalizar_descripcion(descripcion).encode("utf-8")).hexdigest()


def _tokens(descripcion: str) -> frozenset[str]:
    return frozenset(re.findall(r"\w+", normalizar_descripcion(descripcion)))


def _similitud_jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def verificar_no_solape(
    ajuste: Sequence[CasoEvaluacion],
    candidato: Sequence[CasoEvaluacion],
    umbral_jaccard: float | None = None,
) -> list[AdvertenciaSimilitud]:
    """Falla con `SolapeError` si el `candidato` no es independiente del `ajuste`.

    Errores (se informan todos juntos, nombrando cada caso): un id del candidato sin el
    prefijo `I`, un id presente en ambos corpus, o una descripcion normalizada (NFKC,
    minusculas, espacios colapsados) con el mismo SHA-256 que la de un caso de ajuste.

    Con `umbral_jaccard`, cada par candidato/ajuste cuya similitud Jaccard de tokens
    supera ESTRICTAMENTE el umbral se devuelve como advertencia (no como error), en el
    orden del candidato y del ajuste. Sin umbral no se calcula y se devuelve `[]`.

    LIMITE DECLARADO: este control NO detecta parafrasis. Un caso reescrito con otras
    palabras pasa la verificacion aun si trata el mismo incidente; la similitud Jaccard
    es solo una advertencia sobre solapes textuales parciales.
    """
    ids_ajuste = {caso.id for caso in ajuste}
    id_por_huella: dict[str, str] = {}
    for caso in ajuste:
        id_por_huella.setdefault(_huella(caso.descripcion), caso.id)
    motivos: list[str] = []
    for caso in candidato:
        if not caso.id.startswith(PREFIJO_ID_INDEPENDIENTE):
            motivos.append(
                f"el id {caso.id!r} del candidato no lleva el prefijo {PREFIJO_ID_INDEPENDIENTE!r}"
            )
        if caso.id in ids_ajuste:
            motivos.append(f"el id {caso.id!r} aparece en ambos corpus")
        igual = id_por_huella.get(_huella(caso.descripcion))
        if igual is not None:
            motivos.append(
                f"el caso {caso.id!r} del candidato tiene la misma descripcion que el caso "
                f"{igual!r} del corpus de ajuste"
            )
    if motivos:
        raise SolapeError("el corpus candidato no es independiente: " + "; ".join(motivos) + ".")
    if umbral_jaccard is None:
        return []
    tokens_ajuste = [(caso.id, _tokens(caso.descripcion)) for caso in ajuste]
    advertencias: list[AdvertenciaSimilitud] = []
    for caso in candidato:
        tokens = _tokens(caso.descripcion)
        for id_ajuste, tokens_otro in tokens_ajuste:
            similitud = _similitud_jaccard(tokens, tokens_otro)
            if similitud > umbral_jaccard:
                advertencias.append(AdvertenciaSimilitud(caso.id, id_ajuste, similitud))
    return advertencias
