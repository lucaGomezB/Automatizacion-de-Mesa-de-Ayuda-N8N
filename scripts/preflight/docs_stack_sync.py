"""Preflight estatico de sincronizacion documental del stack (c-145, DOC-005).

Verifica, leyendo UNICAMENTE artefactos del repositorio, que la documentacion que
heredan los agentes (`CLAUDE.md` y `openspec/config.yaml`) declare solo valores de
stack reproducibles desde el codigo o desde los archivos de dependencias:

- `App/Backend/app/config/settings.py`  -> modelo, parametros y umbrales de inferencia
- `App/Backend/app/constants.py`        -> `SECTORES_CANONICOS`
- `App/Backend/requirements.txt`        -> pins de FastAPI, Uvicorn y google-genai
- `docker-compose.yml`                  -> imagen de N8N y servicios existentes

Doce chequeos independientes (design D15), cada uno devuelve su propio `Check` para
que el mensaje nombre el valor divergente. El chequeo 12 deriva de `config.yaml`, en
tiempo de ejecucion, los literales volatiles que `CLAUDE.md` no debe restatear; solo
la lista de identificadores retirados (`2.5 Flash`, `1.62`) queda estatica.

NO accede a red, no requiere Docker ni credenciales y no importa el backend (lee
`settings.py` con `ast`, sin ejecutarlo).

Contrato (mismo patron que `cost_readiness.py` y `gemini_readiness.py`):
- ``check_docs(...)`` devuelve ``list[Check]``.
- ``run_docs_stack_sync(...)`` devuelve ``list[Check]`` con las rutas por defecto.
- ``exit_code(checks)`` es 0 si y solo si TODOS los checks son PASS.
- ``format_summary(checks)`` renderiza la lista y la sintesis final.

CLI (desde la raiz del repo):
    python3 scripts/preflight/docs_stack_sync.py
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SETTINGS_PATH = REPO_ROOT / "App" / "Backend" / "app" / "config" / "settings.py"
CONSTANTS_PATH = REPO_ROOT / "App" / "Backend" / "app" / "constants.py"
REQUIREMENTS_PATH = REPO_ROOT / "App" / "Backend" / "requirements.txt"
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
CONFIG_PATH = REPO_ROOT / "openspec" / "config.yaml"
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"

EXIT_OK = 0
EXIT_FAIL = 1

#: Servicios de infraestructura que la documentacion para agentes puede describir
#: como parte del stack, con su clave de servicio en `docker-compose.yml`.
SERVICIOS_ESPERADOS: Dict[str, str] = {
    "Redis": "redis",
    "PostgreSQL": "postgres",
    "N8N": "n8n",
    "Nginx": "nginx",
    "ngrok": "ngrok",
    "FastAPI": "backend",
}

#: Identificadores retirados que ya no figuran en `config.yaml`; no se pueden derivar
#: de ningun lado y son los que reaparecen por copiar texto viejo.
IDENTIFICADORES_RETIRADOS: Tuple[str, ...] = ("2.5 Flash", "1.62")

#: Etapas o tecnologias retiradas del flujo de clasificacion (c-72).
ETAPAS_RETIRADAS: Tuple[str, ...] = ("LangChain",)

#: Claves de `config.yaml` que consume el CLI de OpenSpec.
CLAVES_REQUERIDAS: Tuple[Tuple[str, ...], ...] = (
    ("stack", "backend", "framework"),
    ("stack", "inference", "model"),
    ("conventions", "thresholds"),
    ("conventions", "categorias"),
)

_MISSING = object()
_MODELO_RE = re.compile(r"Gemini\s+(\d+(?:\.\d+)?(?:\s+[A-Za-z]+)?)")
_GENAI_RE = re.compile(r"google-genai\s*([<>=]+\s*[0-9][0-9.,<>=]*)")
_VERSION_RE = re.compile(r"\d+(?:\.\d+)*")


@dataclass
class Check:
    """Resultado de un chequeo verificado."""

    name: str
    status: str
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == STATUS_PASS


def _passing(name: str, detail: str = "") -> Check:
    return Check(name=name, status=STATUS_PASS, detail=detail)


def _failing(name: str, detail: str) -> Check:
    return Check(name=name, status=STATUS_FAIL, detail=detail)


def _get(datos: Any, *claves: str, default: Any = None) -> Any:
    actual = datos
    for clave in claves:
        if not isinstance(actual, dict) or clave not in actual:
            return default
        actual = actual[clave]
    return actual


# ---------------------------------------------------------------------------
# Parsers puros (lectura estatica, sin red y sin importar el backend)
# ---------------------------------------------------------------------------
def _leer_settings(path: "pathlib.Path | str") -> Dict[str, Any]:
    """Defaults de `Settings` leidos con `ast` (no importa el backend)."""
    arbol = ast.parse(pathlib.Path(path).read_text(encoding="utf-8"))
    valores: Dict[str, Any] = {}
    for nodo in ast.walk(arbol):
        if (
            isinstance(nodo, ast.AnnAssign)
            and isinstance(nodo.target, ast.Name)
            and nodo.value is not None
        ):
            try:
                valores[nodo.target.id] = ast.literal_eval(nodo.value)
            except (ValueError, SyntaxError):
                continue
    return valores


def _leer_constantes(path: "pathlib.Path | str") -> Tuple[str, ...]:
    """`SECTORES_CANONICOS` leido con `ast` (no importa el backend)."""
    arbol = ast.parse(pathlib.Path(path).read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if (
            isinstance(nodo, ast.AnnAssign)
            and isinstance(nodo.target, ast.Name)
            and nodo.target.id == "SECTORES_CANONICOS"
        ):
            return tuple(ast.literal_eval(nodo.value))
    return ()


def _leer_requirements(path: "pathlib.Path | str") -> Dict[str, str]:
    """Pins de `requirements.txt`: nombre normalizado -> especificador."""
    requerimientos: Dict[str, str] = {}
    for linea in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0].strip()
        if not linea or linea.startswith("-"):
            continue
        coincidencia = re.match(r"^([A-Za-z0-9_.\-]+)(\[[^\]]*\])?\s*(.*)$", linea)
        if not coincidencia:
            continue
        requerimientos[coincidencia.group(1).lower()] = coincidencia.group(3).strip()
    return requerimientos


def _leer_compose(path: "pathlib.Path | str") -> Dict[str, Any]:
    """`docker-compose.yml` como diccionario."""
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")) or {}


def _leer_docs(path: "pathlib.Path | str") -> Dict[str, Any]:
    """`openspec/config.yaml` como diccionario."""
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")) or {}


def _leer_claude(path: "pathlib.Path | str") -> str:
    """`CLAUDE.md` como texto."""
    return pathlib.Path(path).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Utilidades de versiones
# ---------------------------------------------------------------------------
def _tupla_version(texto: Optional[str]) -> Tuple[int, ...]:
    return tuple(int(parte) for parte in texto.split(".")) if texto else ()


def _cmp_version(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    n = max(len(a), len(b))
    a_pad = a + (0,) * (n - len(a))
    b_pad = b + (0,) * (n - len(b))
    return (a_pad > b_pad) - (a_pad < b_pad)


def _extraer_version(texto: str, etiqueta: str) -> Optional[str]:
    coincidencia = re.search(rf"\b{etiqueta}\s+(\d+(?:\.\d+)*)", texto or "")
    return coincidencia.group(1) if coincidencia else None


def _pin_exacto(spec: str) -> Optional[str]:
    coincidencia = re.match(r"==\s*(\d+(?:\.\d+)*)", spec or "")
    return coincidencia.group(1) if coincidencia else None


def _prefijo_declarado(declarada: str, pin: Optional[str]) -> bool:
    """`declarada` es compatible si es un prefijo por componentes del pin exacto."""
    if pin is None:
        return False
    a = _tupla_version(declarada)
    b = _tupla_version(pin)
    return bool(a) and a == b[: len(a)]


def _parse_restriccion(spec: str) -> Tuple[Optional[Tuple[int, ...]], Optional[Tuple[int, ...]]]:
    lower: Optional[Tuple[int, ...]] = None
    upper: Optional[Tuple[int, ...]] = None
    for parte in (spec or "").split(","):
        coincidencia = re.match(r"\s*(>=|<=|==|>|<)\s*(\d+(?:\.\d+)*)", parte)
        if not coincidencia:
            continue
        operador = coincidencia.group(1)
        version = _tupla_version(coincidencia.group(2))
        if operador in (">=", ">", "=="):
            if lower is None or _cmp_version(version, lower) > 0:
                lower = version
        if operador in ("<=", "<", "=="):
            if upper is None or _cmp_version(version, upper) < 0:
                upper = version
    return lower, upper


def _restriccion_compatible(config_spec: str, req_spec: str) -> bool:
    """La restriccion de la documentacion debe ser al menos tan estricta como el pin."""
    c_low, c_up = _parse_restriccion(config_spec)
    r_low, r_up = _parse_restriccion(req_spec)
    if c_low is None or r_low is None:
        return False
    if _cmp_version(c_low, r_low) < 0:
        return False
    if r_up is not None and (c_up is None or _cmp_version(c_up, r_up) > 0):
        return False
    return True


def _restriccion_genai(texto: Optional[str]) -> Optional[str]:
    coincidencia = _GENAI_RE.search(texto or "")
    return coincidencia.group(1).strip() if coincidencia else None


def _modelos_mencionados(texto: str) -> List[str]:
    return sorted(
        {f"gemini-{m.strip().lower().replace(' ', '-')}" for m in _MODELO_RE.findall(texto or "")}
    )


def _modelo_normalizado(texto: str) -> str:
    return re.sub(r"\s+", "-", (texto or "").split("(")[0].strip().lower())


def _n8n_tag(compose: Dict[str, Any]) -> Optional[str]:
    servicios = compose.get("services", {}) if isinstance(compose, dict) else {}
    for configuracion in (servicios or {}).values():
        imagen = configuracion.get("image") if isinstance(configuracion, dict) else None
        if isinstance(imagen, str) and "n8nio/n8n" in imagen:
            return imagen.rsplit(":", 1)[-1]
    return None


def _literal(valor: Any) -> str:
    return str(valor)


def _literales_prohibidos(config: Dict[str, Any]) -> Dict[str, str]:
    """Literales volatiles derivados de `config.yaml` + identificadores retirados."""
    prohibidos: Dict[str, str] = {}

    umbrales = _get(config, "conventions", "thresholds", default={})
    if isinstance(umbrales, dict):
        for clave, valor in umbrales.items():
            prohibidos[_literal(valor)] = f"conventions.thresholds.{clave}"

    framework = _get(config, "stack", "backend", "framework")
    for version in _VERSION_RE.findall(framework or ""):
        if "." in version:
            prohibidos[version] = "stack.backend.framework"

    restriccion = _restriccion_genai(_get(config, "stack", "inference", "model"))
    if restriccion:
        prohibidos[restriccion] = "stack.inference.model (google-genai)"

    n8n = _extraer_version(str(_get(config, "stack", "orchestration", "tool", default="")), "N8N")
    if n8n:
        prohibidos[n8n] = "stack.orchestration.tool"

    for retirado in IDENTIFICADORES_RETIRADOS:
        prohibidos[retirado] = "lista estatica de identificadores retirados"

    return prohibidos


# ---------------------------------------------------------------------------
# Chequeos 1 a 12
# ---------------------------------------------------------------------------
def _check_modelo(settings: Dict[str, Any], config: Dict[str, Any], claude: str) -> Check:
    nombre = "modelo: config.yaml y CLAUDE.md coinciden con Settings.gemini_model"
    esperado = settings.get("gemini_model")
    problemas: List[str] = []

    modelo_config = _get(config, "stack", "inference", "model")
    if not isinstance(modelo_config, str):
        problemas.append("config.yaml (stack.inference.model) no declara el modelo")
    elif _modelo_normalizado(modelo_config) != esperado:
        problemas.append(
            f"config.yaml declara {modelo_config.split('(')[0].strip()!r} y Settings dice {esperado!r}"
        )

    mencionados = _modelos_mencionados(claude)
    if not mencionados:
        problemas.append("CLAUDE.md no menciona el modelo")
    else:
        for mencionado in mencionados:
            if mencionado != esperado:
                problemas.append(f"CLAUDE.md menciona {mencionado!r} y Settings dice {esperado!r}")

    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre, esperado)


def _comparar_valores(declarados: Any, esperados: Dict[str, Any]) -> List[str]:
    """Divergencias entre los valores declarados en config.yaml y los de Settings."""
    problemas: List[str] = []
    for clave, esperado in esperados.items():
        if not isinstance(declarados, dict) or clave not in declarados:
            problemas.append(f"config.yaml no declara {clave} (Settings: {esperado!r})")
        elif declarados[clave] != esperado:
            problemas.append(f"{clave}: config.yaml={declarados[clave]!r} vs Settings={esperado!r}")
    return problemas


def _check_timeouts(settings: Dict[str, Any], config: Dict[str, Any]) -> Check:
    nombre = "timeout y reintentos: config.yaml coincide con Settings"
    params = _get(config, "stack", "inference", "params", default={})
    problemas = _comparar_valores(
        params,
        {
            "timeout_s": settings.get("gemini_timeout_seconds"),
            "total_timeout_s": settings.get("gemini_total_timeout_seconds"),
            "max_retries": settings.get("gemini_max_retries"),
        },
    )
    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre)


def _check_muestreo(settings: Dict[str, Any], config: Dict[str, Any]) -> Check:
    nombre = "parametros de muestreo: config.yaml coincide con Settings"
    params = _get(config, "stack", "inference", "params", default={})
    problemas = _comparar_valores(
        params,
        {
            "temperature": settings.get("gemini_temperature"),
            "top_p": settings.get("gemini_top_p"),
            "max_output_tokens": settings.get("gemini_max_output_tokens"),
        },
    )
    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre)


def _check_framework(config: Dict[str, Any], requirements: Dict[str, str]) -> Check:
    nombre = "framework: FastAPI/Uvicorn de config.yaml compatibles con requirements.txt"
    framework = _get(config, "stack", "backend", "framework")
    problemas: List[str] = []
    for etiqueta, paquete in (("FastAPI", "fastapi"), ("Uvicorn", "uvicorn")):
        declarada = _extraer_version(framework or "", etiqueta)
        pin = _pin_exacto(requirements.get(paquete, ""))
        if declarada is None:
            continue
        if not _prefijo_declarado(declarada, pin):
            problemas.append(
                f"{etiqueta}: config.yaml declara {declarada} y requirements.txt fija {pin}"
            )
    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre)


def _check_genai(config: Dict[str, Any], claude: str, requirements: Dict[str, str]) -> Check:
    nombre = "google-genai: restriccion de config.yaml y CLAUDE.md compatible con requirements.txt"
    req = requirements.get("google-genai", "")
    problemas: List[str] = []

    restriccion_config = _restriccion_genai(_get(config, "stack", "inference", "model"))
    if restriccion_config is None:
        problemas.append("config.yaml no declara la restriccion de google-genai")
    elif not _restriccion_compatible(restriccion_config, req):
        problemas.append(
            f"config.yaml declara google-genai {restriccion_config} y requirements.txt fija {req}"
        )

    restriccion_claude = _restriccion_genai(claude)
    if restriccion_claude is not None and not _restriccion_compatible(restriccion_claude, req):
        problemas.append(
            f"CLAUDE.md declara google-genai {restriccion_claude} y requirements.txt fija {req}"
        )

    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre)


def _check_n8n(config: Dict[str, Any], claude: str, compose: Dict[str, Any]) -> Check:
    nombre = "n8n: version declarada coincide con la imagen del compose"
    tag = _n8n_tag(compose)
    problemas: List[str] = []
    if tag is None:
        problemas.append("docker-compose.yml no declara una imagen n8nio/n8n")
    else:
        declarada_config = _extraer_version(
            str(_get(config, "stack", "orchestration", "tool", default="")), "N8N"
        )
        if declarada_config != tag:
            problemas.append(
                f"config.yaml declara N8N {declarada_config} y la imagen es n8nio/n8n:{tag}"
            )
        declarada_claude = _extraer_version(claude, "N8N")
        if declarada_claude is not None and declarada_claude != tag:
            problemas.append(
                f"CLAUDE.md declara N8N {declarada_claude} y la imagen es n8nio/n8n:{tag}"
            )
    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre, tag or "")


def _check_servicios(claude: str, compose: Dict[str, Any]) -> Check:
    nombre = "servicios: los descritos en CLAUDE.md existen en el compose"
    servicios = set((compose.get("services") or {}).keys()) if isinstance(compose, dict) else set()
    faltantes: List[str] = []
    for etiqueta, clave in SERVICIOS_ESPERADOS.items():
        if re.search(rf"\b{re.escape(etiqueta)}\b", claude) and clave not in servicios:
            faltantes.append(f"{etiqueta} (servicio {clave!r} ausente en docker-compose.yml)")
    if faltantes:
        return _failing(nombre, "CLAUDE.md describe servicios inexistentes: " + "; ".join(faltantes))
    return _passing(nombre)


def _check_etapas(claude: str) -> Check:
    nombre = "etapas retiradas: ninguna se describe como vigente"
    mencionadas = [etapa for etapa in ETAPAS_RETIRADAS if re.search(rf"\b{re.escape(etapa)}\b", claude)]
    if mencionadas:
        return _failing(
            nombre,
            f"CLAUDE.md menciona la etapa retirada {', '.join(mencionadas)} (retirada por c-72)",
        )
    return _passing(nombre)


def _check_yaml(config: Any, error: Optional[str]) -> Check:
    nombre = "config.yaml: YAML valido y con las claves que consume el CLI"
    if error is not None:
        return _failing(nombre, f"openspec/config.yaml no parsea como YAML: {error}")
    faltantes = [
        ".".join(ruta)
        for ruta in CLAVES_REQUERIDAS
        if _get(config, *ruta, default=_MISSING) is _MISSING
    ]
    if faltantes:
        return _failing(nombre, "faltan claves en config.yaml: " + ", ".join(faltantes))
    return _passing(nombre)


def _check_umbrales(settings: Dict[str, Any], config: Dict[str, Any]) -> Check:
    nombre = "umbrales: config.yaml coincide con Settings"
    umbrales = _get(config, "conventions", "thresholds", default={})
    problemas = _comparar_valores(
        umbrales,
        {
            "deterministic_score": settings.get("deterministic_score_threshold"),
            "human_review": settings.get("human_review_threshold"),
        },
    )
    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre)


def _check_categorias(config: Dict[str, Any], constantes: Tuple[str, ...]) -> Check:
    nombre = "categorias: config.yaml coincide con SECTORES_CANONICOS (contenido y orden)"
    declaradas = _get(config, "conventions", "categorias")
    if list(declaradas or []) != list(constantes or ()):
        return _failing(
            nombre,
            f"config.yaml declara {declaradas!r} y constants.py define {list(constantes or ())!r}",
        )
    return _passing(nombre)


def _check_duplicacion(config: Dict[str, Any], claude: str) -> Check:
    nombre = "duplicacion: CLAUDE.md no restatea literales volatiles de config.yaml"
    prohibidos = _literales_prohibidos(config)
    encontrados = [
        f"{literal!r} (derivado de {origen})"
        for literal, origen in prohibidos.items()
        if literal and literal in claude
    ]
    if encontrados:
        return _failing(
            nombre,
            "CLAUDE.md repite literales que viven en openspec/config.yaml: "
            + "; ".join(encontrados),
        )
    return _passing(nombre)


# ---------------------------------------------------------------------------
# Orquestacion
# ---------------------------------------------------------------------------
def _cargar_yaml(path: "pathlib.Path | str") -> Tuple[Any, Optional[str]]:
    try:
        return _leer_docs(path), None
    except (OSError, yaml.YAMLError) as exc:
        return None, str(exc)


def check_docs(
    settings_path: "pathlib.Path | str" = SETTINGS_PATH,
    constants_path: "pathlib.Path | str" = CONSTANTS_PATH,
    requirements_path: "pathlib.Path | str" = REQUIREMENTS_PATH,
    compose_path: "pathlib.Path | str" = COMPOSE_PATH,
    config_path: "pathlib.Path | str" = CONFIG_PATH,
    claude_path: "pathlib.Path | str" = CLAUDE_PATH,
) -> List[Check]:
    """Ejecuta los doce chequeos de sincronizacion documental."""
    settings = _leer_settings(settings_path)
    constantes = _leer_constantes(constants_path)
    requirements = _leer_requirements(requirements_path)
    compose = _leer_compose(compose_path)
    config, error_yaml = _cargar_yaml(config_path)
    claude = _leer_claude(claude_path)
    config = config if isinstance(config, dict) else {}

    return [
        _check_modelo(settings, config, claude),
        _check_timeouts(settings, config),
        _check_muestreo(settings, config),
        _check_framework(config, requirements),
        _check_genai(config, claude, requirements),
        _check_n8n(config, claude, compose),
        _check_servicios(claude, compose),
        _check_etapas(claude),
        _check_yaml(config if error_yaml is None else None, error_yaml),
        _check_umbrales(settings, config),
        _check_categorias(config, constantes),
        _check_duplicacion(config, claude),
    ]


def run_docs_stack_sync(
    settings_path: "pathlib.Path | str" = SETTINGS_PATH,
    constants_path: "pathlib.Path | str" = CONSTANTS_PATH,
    requirements_path: "pathlib.Path | str" = REQUIREMENTS_PATH,
    compose_path: "pathlib.Path | str" = COMPOSE_PATH,
    config_path: "pathlib.Path | str" = CONFIG_PATH,
    claude_path: "pathlib.Path | str" = CLAUDE_PATH,
) -> List[Check]:
    """Alias de `check_docs` con las rutas del repositorio por defecto."""
    return check_docs(
        settings_path=settings_path,
        constants_path=constants_path,
        requirements_path=requirements_path,
        compose_path=compose_path,
        config_path=config_path,
        claude_path=claude_path,
    )


def exit_code(checks: List[Check]) -> int:
    """0 si y solo si hay checks y todos son PASS; 1 en cualquier otro caso."""
    if not checks:
        return EXIT_FAIL
    return EXIT_OK if all(check.ok for check in checks) else EXIT_FAIL


def format_summary(checks: List[Check]) -> str:
    """Renderiza cada check con su estado y la sintesis final."""
    lines = []
    for check in checks:
        line = f"[{check.status}] {check.name}"
        if check.detail:
            line += f" - {check.detail}"
        lines.append(line)
    passed = sum(1 for check in checks if check.ok)
    total = len(checks)
    lines.append("")
    if total and passed == total:
        lines.append(f"RESULT: {passed}/{total} chequeos en PASS. Documentacion sincronizada.")
    else:
        failed = sum(1 for check in checks if check.status == STATUS_FAIL)
        lines.append(
            f"RESULT: {passed}/{total} chequeos en PASS ({failed} en FAIL). "
            "Documentacion desincronizada."
        )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight estatico de sincronizacion documental: compara CLAUDE.md y "
            "openspec/config.yaml contra settings.py, constants.py, requirements.txt "
            "y docker-compose.yml, sin red ni credenciales."
        )
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Punto de entrada CLI. Imprime el resumen y devuelve 0/1."""
    _build_parser().parse_args(argv)
    checks = run_docs_stack_sync()
    print(format_summary(checks))
    return exit_code(checks)


if __name__ == "__main__":
    raise SystemExit(main())
