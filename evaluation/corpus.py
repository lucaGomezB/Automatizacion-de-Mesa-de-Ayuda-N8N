"""
Carga y validacion del corpus de evaluacion multietiqueta (C-27).

El corpus es un documento JSON con:

    {
      "schema_version": 1,
      "metadata": {"descripcion": "...", "total_casos": N},
      "casos": [
        {
          "id": "...",
          "descripcion": "...",
          "canal_origen": "...",
          "sector_asignado": "...",
          "sectores_adicionales": ["...", ...],
          "tiempo_manual_s": <numero>,
          "tiempo_automatizado_s": <numero>
        }
      ]
    }

Invariantes de la verdad multietiqueta:
- `sectores_adicionales` es obligatorio (arreglo vacio `[]` cuando no hay).
- `sector_asignado` no puede repetirse dentro de `sectores_adicionales`.
- Todos los valores pertenecen al conjunto canonico de cinco sectores.

La carga falla con un error claro (con ruta y motivo) solo ante JSON malformado.
Ante `metadata.total_casos` desincronizado, el loader NORMALIZA `total_casos` a
`len(casos)` y lo persiste en disco antes de validar y usar el corpus (de forma
idempotente: si ya coincide, no reescribe). El resto de las validaciones
(campos faltantes, sectores invalidos, invariantes) sigue fallando con error.
Nunca continúa en silencio con datos malformados.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, List, Optional

# ---------------------------------------------------------------------------
# Vocabulario canonico (paridad con App/Backend/app/constants.py)
# ---------------------------------------------------------------------------
SECTORES_CANONICOS: tuple[str, ...] = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)

CATEGORIAS_VALIDAS: frozenset[str] = frozenset(SECTORES_CANONICOS)

CAMPOS_CASO_REQUERIDOS: tuple[str, ...] = (
    "id",
    "descripcion",
    "canal_origen",
    "sector_asignado",
    "sectores_adicionales",
    "tiempo_manual_s",
    "tiempo_automatizado_s",
)


class CorpusError(ValueError):
    """Error de contrato o de invariante del corpus de evaluacion."""


# ---------------------------------------------------------------------------
# Modelo de datos
# ---------------------------------------------------------------------------
@dataclass
class CasoEvaluacion:
    """Caso individual del corpus de evaluacion multietiqueta."""

    id: str
    descripcion: str
    sector_asignado: str
    sectores_adicionales: List[str] = field(default_factory=list)
    canal_origen: Optional[str] = None
    tiempo_manual_s: Optional[float] = None
    tiempo_automatizado_s: Optional[float] = None

    @property
    def conjunto_verdad(self) -> frozenset[str]:
        """Conjunto de verdad = sector asignado + sectores adicionales."""
        return frozenset({self.sector_asignado, *self.sectores_adicionales})


# ---------------------------------------------------------------------------
# Helpers de validacion
# ---------------------------------------------------------------------------
def _validar_sector(valor: Any, caso_id: str, campo: str) -> str:
    if not isinstance(valor, str) or valor not in CATEGORIAS_VALIDAS:
        raise CorpusError(
            f"Sector invalido '{valor}' en el caso id='{caso_id}' (campo '{campo}'). "
            f"Valores validos: {sorted(CATEGORIAS_VALIDAS)}"
        )
    return valor


def _parsear_caso(item: Any, path: pathlib.Path) -> CasoEvaluacion:
    if not isinstance(item, dict):
        raise CorpusError(
            f"Caso malformado en {path}: se esperaba un objeto JSON, "
            f"se obtuvo {type(item).__name__}."
        )

    caso_id = item.get("id", "desconocido")

    for campo in CAMPOS_CASO_REQUERIDOS:
        if campo not in item:
            raise CorpusError(
                f"El caso id='{caso_id}' en {path} omite el campo requerido '{campo}'."
            )

    sector_asignado = _validar_sector(item["sector_asignado"], str(caso_id), "sector_asignado")

    adicionales = item["sectores_adicionales"]
    if not isinstance(adicionales, list):
        raise CorpusError(
            f"El campo 'sectores_adicionales' del caso id='{caso_id}' en {path} "
            f"debe ser un arreglo, se obtuvo {type(adicionales).__name__}."
        )

    adicionales_validados = [
        _validar_sector(valor, str(caso_id), "sectores_adicionales") for valor in adicionales
    ]

    if sector_asignado in adicionales_validados:
        raise CorpusError(
            f"Invariante violada en el caso id='{caso_id}' de {path}: "
            f"'sector_asignado' ('{sector_asignado}') se repite dentro de "
            f"'sectores_adicionales'."
        )

    def _a_float(valor: Any, campo: str) -> float:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise CorpusError(
                f"El campo '{campo}' del caso id='{caso_id}' en {path} "
                f"debe ser numerico, se obtuvo '{valor}'."
            )
        return float(valor)

    return CasoEvaluacion(
        id=str(caso_id),
        descripcion=str(item["descripcion"]),
        sector_asignado=sector_asignado,
        sectores_adicionales=adicionales_validados,
        canal_origen=str(item["canal_origen"]),
        tiempo_manual_s=_a_float(item["tiempo_manual_s"], "tiempo_manual_s"),
        tiempo_automatizado_s=_a_float(item["tiempo_automatizado_s"], "tiempo_automatizado_s"),
    )


# ---------------------------------------------------------------------------
# Funcion pura de carga
# ---------------------------------------------------------------------------
def cargar_corpus(path: pathlib.Path | str) -> List[CasoEvaluacion]:
    """
    Carga el corpus de evaluacion desde un documento JSON.

    Args:
        path: Ruta al archivo JSON.

    Returns:
        Lista de CasoEvaluacion en el orden original de `casos`.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        CorpusError: Si el JSON es malformado, la estructura es invalida
            o un caso viola el contrato.

    Nota:
        `metadata.total_casos` desincronizado se normaliza y se persiste; no
        es un error.
    """
    path = pathlib.Path(path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el corpus de evaluación en: {path}")

    try:
        documento = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CorpusError(
            f"JSON malformado en {path}: {exc.msg} (linea {exc.lineno}, columna {exc.colno})."
        ) from exc

    if not isinstance(documento, dict):
        raise CorpusError(
            f"El corpus de {path} debe ser un objeto JSON con 'schema_version', "
            f"'metadata' y 'casos'."
        )

    for campo in ("schema_version", "metadata", "casos"):
        if campo not in documento:
            raise CorpusError(f"El corpus de {path} omite el campo requerido '{campo}'.")

    metadata = documento["metadata"]
    if not isinstance(metadata, dict):
        raise CorpusError(f"El campo 'metadata' de {path} debe ser un objeto JSON.")

    casos_raw = documento["casos"]
    if not isinstance(casos_raw, list):
        raise CorpusError(f"El campo 'casos' de {path} debe ser un arreglo JSON.")

    total_casos = metadata.get("total_casos")
    if total_casos != len(casos_raw):
        metadata["total_casos"] = len(casos_raw)
        path.write_text(
            json.dumps(documento, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return [_parsear_caso(item, path) for item in casos_raw]
