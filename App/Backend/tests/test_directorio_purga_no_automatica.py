"""
Inspeccion: la purga por retencion NO tiene automatizacion (c-60, 5.4 / DIR-007).

El borrado fisico por retencion es MANUAL: solo se dispara por una invocacion
humana explicita (la ruta `POST /api/v1/directorio/purga` o el script CLI). Este
test inspecciona el codigo de produccion (`app/` y `scripts/`) para garantizar
que NO se introdujo ningun cron/scheduler/worker que dispare la purga por si solo.
"""

from __future__ import annotations

import ast
from pathlib import Path

# `tests/` -> `App/Backend/`
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_APP_DIR = _BACKEND_ROOT / "app"
_SCRIPTS_DIR = _BACKEND_ROOT / "scripts"

# Librerias conocidas de planificacion/ejecucion en background. Su sola
# importacion en el codigo de produccion del directorio es una senal de alarma.
_SCHEDULER_MODULES = frozenset(
    {"apscheduler", "celery", "croniter", "schedule", "rq", "dramatiq", "arq"}
)

# Unicas entradas humanas autorizadas a invocar la purga. Si aparece un cuarto
# archivo que la llama, la automatizacion se colo por algun lado.
_INVOCADORES_ESPERADOS = frozenset(
    {
        "app/services/directorio_service.py",
        "app/routes/directorio.py",
        "scripts/purgar_directorio.py",
    }
)


def _raices_importadas(tree: ast.AST) -> set[str]:
    """Devuelve los modulos de primer nivel importados por un AST."""
    raices: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                raices.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            raices.add(node.module.split(".")[0])
    return raices


def _archivos_produccion() -> list[Path]:
    """Todos los modulos Python de produccion (sin tests ni caches)."""
    archivos: list[Path] = []
    for base in (_APP_DIR, _SCRIPTS_DIR):
        archivos.extend(sorted(base.rglob("*.py")))
    return archivos


def test_no_hay_librerias_de_scheduler_en_el_codigo_de_produccion():
    """Ningun modulo de produccion importa una libreria de planificacion."""
    offenders: list[tuple[str, list[str]]] = []
    for path in _archivos_produccion():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        coincidence = _raices_importadas(tree) & _SCHEDULER_MODULES
        if coincidence:
            offenders.append(
                (path.relative_to(_BACKEND_ROOT).as_posix(), sorted(coincidence))
            )

    assert offenders == [], (
        "El codigo de produccion no debe importar schedulers/cron: " f"{offenders}"
    )


def test_la_purga_solo_se_invoca_desde_entradas_humanas():
    """`purgar_vencidos` solo aparece en el servicio, la ruta manual y el CLI."""
    invocadores: set[str] = set()
    for path in _archivos_produccion():
        if "purgar_vencidos" in path.read_text(encoding="utf-8"):
            invocadores.add(path.relative_to(_BACKEND_ROOT).as_posix())

    assert invocadores == set(_INVOCADORES_ESPERADOS), (
        "La purga solo debe invocarse desde entradas humanas explicitas; se "
        f"encontro: {sorted(invocadores)}"
    )
