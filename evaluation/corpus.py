"""
Carga y validación del corpus de evaluación.

El corpus es un CSV con columnas `id`, `descripcion`, `categoria_real` (requeridas)
y, opcionalmente, `tiempo_manual_s` y `tiempo_automatizado_s`.

La carga valida presencia de columnas y dominio de categorías, fallando con
error claro ante cualquier desviación (nada silencioso).
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes de dominio (1.5 REFACTOR — extraídas aquí para reutilización)
# ---------------------------------------------------------------------------
CATEGORIAS_VALIDAS: frozenset[str] = frozenset(
    {"Sistemas", "Operaciones", "Soporte Técnico"}
)

COLUMNAS_REQUERIDAS: list[str] = ["id", "descripcion", "categoria_real"]


# ---------------------------------------------------------------------------
# Modelo de datos
# ---------------------------------------------------------------------------
@dataclass
class CasoEvaluacion:
    """Caso individual del corpus de evaluación."""

    id: str
    descripcion: str
    categoria_real: str
    tiempo_manual_s: Optional[float] = None
    tiempo_automatizado_s: Optional[float] = None


# ---------------------------------------------------------------------------
# Función pura de carga
# ---------------------------------------------------------------------------
def cargar_corpus(path: pathlib.Path | str) -> List[CasoEvaluacion]:
    """
    Carga el corpus de evaluación desde un CSV.

    Args:
        path: Ruta al archivo CSV.

    Returns:
        Lista de CasoEvaluacion en el orden original del CSV.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        ValueError: Si falta una columna requerida o una categoría es inválida.
    """
    path = pathlib.Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el corpus de evaluación en: {path}"
        )

    df = pd.read_csv(path, dtype=str)

    # Validar columnas requeridas
    for columna in COLUMNAS_REQUERIDAS:
        if columna not in df.columns:
            raise ValueError(
                f"El corpus no contiene la columna requerida: '{columna}'. "
                f"Columnas presentes: {list(df.columns)}"
            )

    # Validar dominio de categorías
    for _, fila in df.iterrows():
        categoria = fila["categoria_real"]
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValueError(
                f"Categoría inválida '{categoria}' en el caso id='{fila['id']}'. "
                f"Valores válidos: {sorted(CATEGORIAS_VALIDAS)}"
            )

    # Mapear a dataclasses
    casos: List[CasoEvaluacion] = []
    for _, fila in df.iterrows():
        caso = CasoEvaluacion(
            id=str(fila["id"]),
            descripcion=str(fila["descripcion"]),
            categoria_real=str(fila["categoria_real"]),
            tiempo_manual_s=(
                float(fila["tiempo_manual_s"])
                if "tiempo_manual_s" in df.columns and pd.notna(fila.get("tiempo_manual_s"))
                else None
            ),
            tiempo_automatizado_s=(
                float(fila["tiempo_automatizado_s"])
                if "tiempo_automatizado_s" in df.columns and pd.notna(fila.get("tiempo_automatizado_s"))
                else None
            ),
        )
        casos.append(caso)

    return casos
