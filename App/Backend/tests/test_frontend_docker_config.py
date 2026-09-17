"""
Tests de configuracion de build del frontend (seam FE 1).

Estos tests NO levantan servicios ni construyen imagenes: leen los archivos de
configuracion (`docker-compose.yml`, `App/Frontend/Dockerfile`) y verifican la
costura entre la variable `VITE_API_BASE_URL` que consume el cliente HTTP y el
mecanismo que la hornea en el bundle de produccion.

Motivacion (seam FE 1):
    - `api.ts` compone la URL base como `${VITE_API_BASE_URL}/api/v1`.
    - `docker-compose.yml` define `VITE_API_BASE_URL: https://localhost/api/v1`,
      lo que produce `https://localhost/api/v1/api/v1`.
    - `VITE_API_BASE_URL` aparece solo bajo `environment` (runtime) y no bajo
      `build.args`, por lo que Vite nunca la incorpora al bundle.
    - `App/Frontend/Dockerfile` no declara `ARG VITE_API_BASE_URL`.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
FRONTEND_DOCKERFILE = REPO_ROOT / "App" / "Frontend" / "Dockerfile"

API_V1_SUFFIX = "/api/v1"


def _load_compose() -> dict:
    """Carga docker-compose.yml como estructura de datos."""
    return yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))


def _frontend_service() -> dict:
    """Devuelve el bloque del servicio 'frontend' del compose."""
    return _load_compose()["services"]["frontend"]


def test_compose_forwards_vite_api_base_url_as_build_arg():
    """docker-compose debe reenviar VITE_API_BASE_URL bajo build.args.

    Solo `environment` (runtime) no alcanza: el bundle de Vite se genera en
    tiempo de build, por lo que la variable debe llegar como build arg para
    quedar embebida en el bundle de produccion.
    """
    frontend = _frontend_service()
    build_args = (frontend.get("build") or {}).get("args") or {}

    assert "VITE_API_BASE_URL" in build_args, (
        "El servicio 'frontend' de docker-compose.yml no declara "
        "VITE_API_BASE_URL en build.args; hoy solo aparece en environment y "
        "Vite no la incorpora al bundle. build.args actual: "
        f"{build_args}"
    )


def test_compose_vite_api_base_url_has_no_duplicated_api_v1():
    """El valor de VITE_API_BASE_URL no debe terminar en /api/v1.

    `api.ts` agrega '/api/v1' por su cuenta al construir `baseURL`, por lo que
    un valor terminado en /api/v1 produce una URL duplicada
    (.../api/v1/api/v1).
    """
    frontend = _frontend_service()
    build_args = (frontend.get("build") or {}).get("args") or {}
    environment = frontend.get("environment") or {}

    # El valor puede declararse en build.args (preferido) o environment (legado).
    value = build_args.get(
        "VITE_API_BASE_URL", environment.get("VITE_API_BASE_URL")
    )

    assert value is not None, (
        "VITE_API_BASE_URL no esta declarada en build.args ni en environment "
        "del servicio 'frontend'."
    )
    assert not str(value).rstrip("/").endswith(API_V1_SUFFIX), (
        f"VITE_API_BASE_URL='{value}' termina en '{API_V1_SUFFIX}', pero "
        "api.ts ya agrega '/api/v1' al construir baseURL: se produce "
        "'.../api/v1/api/v1'. El valor debe ser el origen, sin el sufijo."
    )


def test_frontend_dockerfile_declares_vite_api_base_url_arg_before_build():
    """El Dockerfile debe declarar ARG VITE_API_BASE_URL antes de npm run build.

    Sin `ARG`, el `--build-arg` enviado por compose no existe dentro de la
    etapa de build y Vite compila con la URL por defecto.
    """
    lines = FRONTEND_DOCKERFILE.read_text(encoding="utf-8").splitlines()

    arg_index = next(
        (
            i
            for i, line in enumerate(lines)
            if line.strip() == "ARG VITE_API_BASE_URL"
        ),
        None,
    )
    build_index = next(
        (i for i, line in enumerate(lines) if "npm run build" in line),
        None,
    )

    assert arg_index is not None, (
        "App/Frontend/Dockerfile no declara 'ARG VITE_API_BASE_URL'. "
        "Contenido actual:\n" + "\n".join(lines)
    )
    assert build_index is not None, (
        "No se encontro 'npm run build' en App/Frontend/Dockerfile."
    )
    assert arg_index < build_index, (
        f"'ARG VITE_API_BASE_URL' (linea {arg_index + 1}) debe declararse "
        f"antes de 'npm run build' (linea {build_index + 1})."
    )
