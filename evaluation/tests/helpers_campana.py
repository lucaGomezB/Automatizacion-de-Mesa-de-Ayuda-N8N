"""
Helpers compartidos por los tests del analisis de campana (c-167).

No es un modulo de tests (pytest solo recolecta `test_*.py`): concentra las rutas de los
fixtures SINTETICOS de `tests/fixtures/campana/`, los lectores de CSV y JSON y los valores
de referencia que los tests de kappa, de campana y del CLI comparten.

El corpus se carga siempre desde una copia en `tmp_path`: `cargar_corpus` puede reescribir
`metadata.total_casos` y un fixture versionado no debe cambiar durante la suite.
"""

from __future__ import annotations

import csv
import json
import pathlib
import shutil
from typing import Any

RAIZ_EVALUATION = pathlib.Path(__file__).resolve().parents[1]
RAIZ_REPO = RAIZ_EVALUATION.parent
DIR_CAMPANA = RAIZ_EVALUATION / "tests" / "fixtures" / "campana"

# Fixtures SINTETICOS de c-167 (ver tests/fixtures/README.md).
PLANILLA = DIR_CAMPANA / "plantilla_etiquetado.csv"
REGISTRO_SUJETOS = DIR_CAMPANA / "registro_sujetos.csv"
REGISTRO_SUJETOS_SOLAPE = DIR_CAMPANA / "registro_sujetos_solape.csv"
CORPUS_CAMPANA = DIR_CAMPANA / "corpus_campana.json"
PLAN = DIR_CAMPANA / "plan_campana.csv"
INTERVENCIONES = DIR_CAMPANA / "intervenciones.csv"
PREDICCIONES_IN_SAMPLE = DIR_CAMPANA / "predicciones_in_sample.json"
PREDICCIONES_INDEPENDIENTE = DIR_CAMPANA / "predicciones_independiente.json"
PREDICCIONES_INDEPENDIENTE_PINES = DIR_CAMPANA / "predicciones_independiente_pines_distintos.json"
PREDICCIONES_INDEPENDIENTE_VERSION = DIR_CAMPANA / "predicciones_independiente_version_distinta.json"
CORPUS_INDEPENDIENTE = DIR_CAMPANA / "corpus_independiente.json"
CORPUS_INDEPENDIENTE_SOLAPE = DIR_CAMPANA / "corpus_independiente_solape.json"

# Contratos de las entradas (encabezados exactos).
COLUMNAS_C2 = ("alias", "rol", "persona")
COLUMNAS_C5 = (
    "id_caso",
    "incidente_id",
    "log_id",
    "origen_intervencion",
    "intervencion_inicio_en",
    "validado_en",
    "duracion_s",
    "sector_predicho",
    "sector_validado",
    "cambio_sector",
    "actor_alias",
)

# Valores de la validacion fuera de muestra del fixture (README del fixture).
PINES_IN_SAMPLE = {"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}
RANGO_VIGENTE_GOOGLE_GENAI = ">=2.33,<3"


def leer_csv(ruta: pathlib.Path) -> list[dict[str, str]]:
    """Filas de un CSV UTF-8 como dicts de texto."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def encabezado_csv(ruta: pathlib.Path) -> tuple[str, ...]:
    """Primera fila (encabezado) de un CSV."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return tuple(next(csv.reader(archivo)))


def leer_json(ruta: pathlib.Path) -> Any:
    return json.loads(ruta.read_text(encoding="utf-8"))


def escribir_json(ruta: pathlib.Path, documento: Any) -> pathlib.Path:
    ruta.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta


def copiar_fixture(origen: pathlib.Path, directorio: pathlib.Path) -> pathlib.Path:
    """Copia un fixture a `directorio` y devuelve la copia (el original no se toca)."""
    destino = directorio / origen.name
    shutil.copyfile(origen, destino)
    return destino


def filas_de_tarea(filas: list[dict[str, str]], tarea: str) -> list[dict[str, str]]:
    return [fila for fila in filas if fila["tarea"] == tarea]
