"""
Posicion real y desvios del brazo manual respecto del plan de campana (c-165, ECM-001).

El brazo manual se captura OFFLINE en la planilla unica de c-168 (`tarea = brazo_manual`,
operadores `O1` y `O2`, `inicio` y `timestamp` obligatorios). Su esquema y su validador
son de c-168 (`evaluation.doble_etiquetado.validar_doble_etiquetado`) y el plan de
campana es de c-166 (`evaluation.plan_campana`): este modulo NO define esquema, columnas,
cadenas de sector ni reglas de reparto, y no lee archivos. Agrega solo dos funciones
puras que c-167 importa para estimar el efecto de posicion:

- `reconstruir_posicion_real(filas)`: lugar 1..N de cada caso en la secuencia de su
  operador, ordenada por `inicio` (como instante, no como texto), con desempate por
  `timestamp` y, ante un empate exacto, por `id_caso` (el resultado no depende del orden
  en que llegan las filas).
- `desvios_respecto_del_plan(posiciones_reales, plan)`: los casos cuya posicion real
  difiere de la planeada.

Posicion planeada. El plan de c-166 recorre el brazo manual mitad por mitad y, dentro de
cada mitad, primero el turno 1 (casos con `brazo_primero = manual`) y despues el turno 2,
cada turno en orden de `posicion` (runbook de c-166, secciones 3 y 4; `subplan`). Ese es el
orden que el plan le indica al operador manual, y NO el de la `posicion` global: un
operador que sigue el runbook al pie de la letra hace los casos de turno 2 despues de todos
los de turno 1. Como cada operador cubre solo una parte de los casos (por mitades, mas una
submuestra con doble cobertura), la posicion planeada de un caso es su lugar en ese orden
RESTRINGIDO a los casos que ese operador registro: un operador que solo trabaja la segunda
mitad no acumula desvios por los casos de la primera, y un caso no registrado (cobertura
que valida c-168, regla b) no desplaza a los demas. Un desvio es todo caso cuya posicion
real difiere de la planeada; adelantar un caso desplaza a los que salto y esos tambien se
informan.

Precondicion: la planilla paso `validar_doble_etiquetado(..., tarea="brazo_manual")` y el
plan se leyo con `leer_plan_csv`. Aun asi, una fila con `inicio` o `timestamp` ilegibles o
sin zona horaria, un caso repetido para un operador o un caso fuera del plan levantan
`BrazoManualError` con un mensaje que nombra operador, caso y campo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

from evaluation.plan_campana import BRAZO_MANUAL, AsignacionCaso, subplan


class BrazoManualError(ValueError):
    """Entrada inconsistente del brazo manual (el mensaje nombra operador, caso y campo)."""


# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PosicionReal:
    """Lugar (1..N) que ocupo un caso en la secuencia de un operador, segun `inicio`."""

    id_etiquetador: str
    id_caso: str
    posicion: int


@dataclass(frozen=True)
class Desvio:
    """Caso cuya posicion real difiere de la planeada en la secuencia de su operador."""

    id_etiquetador: str
    id_caso: str
    posicion_planeada: int
    posicion_real: int


# ---------------------------------------------------------------------------
# Posicion real
# ---------------------------------------------------------------------------
def _instante(fila: Mapping[str, str | None], campo: str) -> datetime:
    """Instante ISO-8601 con zona horaria de `fila[campo]`; `BrazoManualError` si no lo es."""
    valor = fila.get(campo)
    try:
        instante = datetime.fromisoformat(valor) if valor else None
    except ValueError:
        instante = None
    if instante is None or instante.tzinfo is None:
        raise BrazoManualError(
            f"fila ({fila['id_etiquetador']}, {fila['id_caso']}): {campo} no es un instante "
            f"ISO-8601 con zona horaria ({valor!r})."
        )
    return instante


def reconstruir_posicion_real(filas: Sequence[Mapping[str, str | None]]) -> list[PosicionReal]:
    """Posicion 1..N de cada caso dentro de la secuencia de su operador.

    Ordena por `inicio` como instante (el texto de dos zonas horarias distintas no se
    compara), desempata por `timestamp` y despues por `id_caso`. Cada operador tiene su
    propia secuencia aunque trabaje los mismos casos que otro. Devuelve una lista nueva
    ordenada por operador y posicion; no modifica `filas`.
    """
    por_operador: dict[str, list[tuple[datetime, datetime, str]]] = {}
    vistos: set[tuple[str, str]] = set()
    for fila in filas:
        operador, id_caso = fila["id_etiquetador"], fila["id_caso"]
        if (operador, id_caso) in vistos:
            raise BrazoManualError(
                f"el caso {id_caso} aparece mas de una vez para el operador {operador}."
            )
        vistos.add((operador, id_caso))
        por_operador.setdefault(operador, []).append(
            (_instante(fila, "inicio"), _instante(fila, "timestamp"), id_caso)
        )
    return [
        PosicionReal(operador, id_caso, posicion)
        for operador in sorted(por_operador)
        for posicion, (_, _, id_caso) in enumerate(sorted(por_operador[operador]), start=1)
    ]


# ---------------------------------------------------------------------------
# Desvios respecto del plan
# ---------------------------------------------------------------------------
def _orden_planeado(plan: Sequence[AsignacionCaso]) -> list[str]:
    """Orden en que el plan indica que el brazo manual procesa los casos.

    Mitad por mitad y, dentro de cada una, turno 1 (`brazo_primero` manual) y despues
    turno 2, cada turno en orden de `posicion`. Reutiliza `subplan` de c-166.
    """
    por_posicion = sorted(plan, key=lambda fila: fila.posicion)
    return [
        fila.id_caso
        for mitad in (1, 2)
        for turno in (1, 2)
        for fila in subplan(por_posicion, mitad, BRAZO_MANUAL, turno)
    ]


def desvios_respecto_del_plan(
    posiciones_reales: Sequence[PosicionReal], plan: Sequence[AsignacionCaso]
) -> list[Desvio]:
    """Casos cuya posicion real difiere de la planeada para su operador.

    `posiciones_reales` es el resultado de `reconstruir_posicion_real` y `plan` el de
    `leer_plan_csv`. La posicion planeada de un caso es su lugar (1..N) en el orden del
    plan restringido a los casos que su operador registro (ver la docstring del modulo).
    Devuelve los desvios ordenados por operador y posicion real; vacio si no hay ninguno.
    Un caso que no figura en el plan levanta `BrazoManualError`.
    """
    lugar_en_el_plan = {id_caso: lugar for lugar, id_caso in enumerate(_orden_planeado(plan))}
    por_operador: dict[str, list[PosicionReal]] = {}
    for posicion in posiciones_reales:
        if posicion.id_caso not in lugar_en_el_plan:
            raise BrazoManualError(
                f"el caso {posicion.id_caso} del operador {posicion.id_etiquetador} "
                "no figura en el plan de campana."
            )
        por_operador.setdefault(posicion.id_etiquetador, []).append(posicion)
    desvios: list[Desvio] = []
    for operador in sorted(por_operador):
        propias = por_operador[operador]
        en_orden_del_plan = sorted(propias, key=lambda p: lugar_en_el_plan[p.id_caso])
        planeada = {p.id_caso: lugar for lugar, p in enumerate(en_orden_del_plan, start=1)}
        desvios += [
            Desvio(operador, p.id_caso, planeada[p.id_caso], p.posicion)
            for p in sorted(propias, key=lambda p: p.posicion)
            if planeada[p.id_caso] != p.posicion
        ]
    return desvios
