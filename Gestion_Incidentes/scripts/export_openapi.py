"""
Script de generación del esquema OpenAPI estático (Decisión D2 de C-10).

Propósito:
    Genera docs/openapi.json importando la aplicación FastAPI directamente,
    sin necesidad de un servidor en ejecución ni de una base de datos real.

Uso:
    # Desde la raíz del repo:
    cd Gestion_Incidentes
    python scripts/export_openapi.py

    # Opcionalmente, apuntar a un directorio de salida distinto:
    python scripts/export_openapi.py --output ../docs/openapi.json

Variables de entorno:
    Si las variables requeridas por Settings (DATABASE_URL, GEMINI_API_KEY,
    PSEUDONYMIZATION_ENCRYPTION_KEY) no están presentes, este script las
    inyecta con valores dummy —suficientes para instanciar Settings sin DB
    real, el mismo patrón que usa CI (C-09).

Notas:
    - `create_app()` no abre conexiones a la DB en el import: el engine
      usa lazy connect y el lifespan de FastAPI no corre fuera de un servidor.
    - El JSON se serializa con indent=2 y sort_keys=True para producir diffs
      mínimos y determinísticos en git.
    - El archivo de salida es siempre docs/openapi.json relativo a la raíz
      del repositorio (dos niveles arriba de este script).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# ── Env dummies (mismo patrón que CI de C-09) ────────────────────────────────
# Deben setearse ANTES de importar app.config.settings (que instancia Settings
# con pydantic-settings al cargarse el módulo).
_DUMMIES = {
    "DATABASE_URL": "postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy",
    "GEMINI_API_KEY": "ci-dummy-key",
    "PSEUDONYMIZATION_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",  # gitleaks:allow
}
for _key, _val in _DUMMIES.items():
    if _key not in os.environ:
        os.environ[_key] = _val

# ── Agregar el directorio padre (Gestion_Incidentes/) al sys.path ────────────
# Necesario cuando se ejecuta el script desde cualquier directorio de trabajo.
_SCRIPT_DIR = Path(__file__).resolve().parent          # Gestion_Incidentes/scripts/
_GI_ROOT = _SCRIPT_DIR.parent                          # Gestion_Incidentes/
_REPO_ROOT = _GI_ROOT.parent                           # raíz del repo

if str(_GI_ROOT) not in sys.path:
    sys.path.insert(0, str(_GI_ROOT))

# ── Ruta de salida por defecto ────────────────────────────────────────────────
_DEFAULT_OUTPUT = _REPO_ROOT / "docs" / "openapi.json"


def generate_schema() -> dict:
    """
    Genera el esquema OpenAPI 3.1 desde la app FastAPI en memoria.

    Returns:
        Diccionario con el esquema OpenAPI completo generado por FastAPI.
    """
    from app.main import create_app  # importar DESPUÉS de setear env dummies

    application = create_app()
    # Forzar la regeneración limpia (FastAPI cachea en openapi_schema)
    application.openapi_schema = None
    return application.openapi()


def write_schema(schema: dict, output_path: Path) -> None:
    """
    Serializa el esquema a JSON con formato estable y lo escribe en disco.

    Args:
        schema:      Diccionario con el esquema OpenAPI.
        output_path: Ruta absoluta del archivo de salida.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False)
    output_path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """
    Punto de entrada del script.

    Args:
        argv: Argumentos de línea de comandos (por defecto sys.argv[1:]).

    Returns:
        Código de salida: 0 en éxito, 1 en error.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera docs/openapi.json desde la app FastAPI."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"Ruta de salida del archivo (por defecto: {_DEFAULT_OUTPUT})",
    )
    args = parser.parse_args(argv)

    output: Path = args.output.resolve()

    try:
        print(f"Generando esquema OpenAPI desde app.main:app …")
        schema = generate_schema()
        write_schema(schema, output)
        openapi_version = schema.get("openapi", "desconocida")
        path_count = len(schema.get("paths", {}))
        print(f"  OpenAPI versión : {openapi_version}")
        print(f"  Rutas exportadas: {path_count}")
        print(f"  Archivo generado: {output}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
