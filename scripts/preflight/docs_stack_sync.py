"""Preflight estatico de sincronizacion documental del stack (c-145, DOC-005).

Verifica, leyendo UNICAMENTE artefactos del repositorio, que la documentacion que
heredan los agentes (`CLAUDE.md` y `openspec/config.yaml`) declare solo valores de
stack reproducibles desde el codigo o desde los archivos de dependencias:

- `App/Backend/app/config/settings.py`  -> modelo, parametros y umbrales de inferencia
- `App/Backend/app/constants.py`        -> `SECTORES_CANONICOS`
- `App/Backend/requirements.txt`        -> pins de FastAPI, Uvicorn y google-genai
- `docker-compose.yml`                  -> imagen de N8N y servicios existentes

Diecisiete chequeos independientes (design D15), cada uno devuelve su propio `Check`
para que el mensaje nombre el valor divergente. El chequeo 12 deriva de `config.yaml`,
en tiempo de ejecucion, los literales volatiles que `CLAUDE.md` no debe restatear; solo
la lista de identificadores retirados (`2.5 Flash`, `1.62`) queda estatica. El chequeo
17 deriva de `requirements.txt` y del compose las versiones de componentes que declara
`knowledge-base/`, sin hardcodear ninguna.

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
import unicodedata
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

#: Superficie ampliada (chequeos 13-15): la base de conocimiento y el material de
#: referencia que los documentos para agentes alcanzan.
KB_DIR = REPO_ROOT / "knowledge-base"
DOCS_REFERENCIA: Tuple[pathlib.Path, ...] = (
    REPO_ROOT / "docs" / "parameters_gemini.md",
    REPO_ROOT / "docs" / "n8n-workflow-guide.md",
)

#: Cliente HTTP del frontend (chequeo 16): declara su timeout de Axios.
API_TS_PATH = REPO_ROOT / "App" / "Frontend" / "src" / "services" / "api.ts"

#: Archivos de la base de conocimiento que la barrera espera encontrar (chequeo 15).
KB_ARCHIVOS_ESPERADOS: Tuple[str, ...] = (
    "README.md",
    "01_vision_y_objetivos.md",
    "02_descripcion_general.md",
    "03_actores_y_roles.md",
    "04_modelo_de_datos.md",
    "05_reglas_de_negocio.md",
    "06_funcionalidades.md",
    "07_flujos_principales.md",
    "08_arquitectura_propuesta.md",
    "09_decisiones_y_supuestos.md",
    "10_preguntas_abiertas.md",
    "11_evaluacion_experimental.md",
)

#: Substrings (sin tilde) que rotulan un pasaje como historico. Un valor retirado
#: se exime SOLO si su linea o el encabezado de su seccion contiene un marcador.
#: `deprecad` NO es un marcador: en esta superficie rotula al SDK retirado
#: (`google-generativeai`), no al modelo, y eximiria por error una mencion de
#: `gemini-2.5-flash` en una linea que solo dice que algo quedo deprecado.
MARCADORES_HISTORICOS: Tuple[str, ...] = (
    "historico",
    "historica",
    "historicamente",
    "calibrad",
    "antecedente",
    "superad",
    "migro",
    "migrado",
    "retirado",
    "previo",
)

#: Timeouts retirados del contexto de parametros de Gemini (chequeo 14).
TIMEOUTS_RETIRADOS: Tuple[int, ...] = (10,)

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
#: Acepta el nombre entre backticks (`google-genai` >=2.31,<3), forma usada en la KB.
_GENAI_RE = re.compile(r"google-genai[`\s]*([<>=]+\s*[0-9][0-9.,<>=]*)")
_VERSION_RE = re.compile(r"\d+(?:\.\d+)*")

#: Tokens de modelo en la superficie ampliada: forma kebab (`gemini-2.5-flash`) o
#: forma textual (`Gemini 2.5 Flash` / `2.5 Flash`). Se normalizan a `gemini-<version>-flash`.
_MODELO_SUPERFICIE_RE = re.compile(
    r"gemini-(\d+\.\d+)-flash|(gemini\s+)?(\d+\.\d+)\s+Flash", re.IGNORECASE
)
#: Valor de timeout explicito (`timeout 10 s`, `timeout=10`, `timeout | 10s`, `timeout: 10`).
_TIMEOUT_EXPLICITO_RE = re.compile(r"timeout\s*[=:|]?\s*(\d+)", re.IGNORECASE)
#: Declaracion del timeout de Axios (`timeout: 65_000`).
_AXIOS_TIMEOUT_RE = re.compile(r"timeout\s*:\s*([0-9_]+)")
#: Linea en contexto de parametros de Gemini (para restringir el chequeo 14).
_PARAM_GEMINI_RE = re.compile(
    r"gemini|top_p|max_output_tokens|candidate_count|max_tokens|timeout_seconds",
    re.IGNORECASE,
)
#: Version de N8N declarada en la KB (tabla `| N8N | 1.62 |`, `N8N v1.62`,
#: `N8N oficial 1.62`, `N8N 1.62 autoalojado`). Anclada a `N8N` para no capturar
#: cualquier numero de la linea (puertos, dias, Python 3.12, postgres 15.5).
_N8N_VERSION_RE = re.compile(r"N8N(?:\s+oficial)?\s*(?:\|\s*|v)?\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE)
#: FastAPI/Uvicorn declarados en la KB, en tabla (`... | 0.143.3 / 0.54.0`) o en
#: prosa (`FastAPI 0.143.3 sobre Uvicorn 0.54.0`). Anclado para no capturar la
#: version de Python que suele acompanar a la fila de la tabla.
_FASTAPI_UVICORN_TABLA_RE = re.compile(
    r"FastAPI\s*\+\s*Uvicorn\s*\|\s*(\d+(?:\.\d+)*)\s*/\s*(\d+(?:\.\d+)*)", re.IGNORECASE
)
_FASTAPI_UVICORN_PROSA_RE = re.compile(
    r"FastAPI\s+(\d+(?:\.\d+)*)\s+sobre\s+Uvicorn(?:\s+(\d+(?:\.\d+)*))?", re.IGNORECASE
)


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
# Parsers de la superficie ampliada (chequeos 13-16)
# ---------------------------------------------------------------------------
def _normalizar_texto(texto: str) -> str:
    """Minusculas y sin tildes, para comparar marcadores y tokens."""
    descompuesto = unicodedata.normalize("NFKD", (texto or "").lower())
    return "".join(caracter for caracter in descompuesto if not unicodedata.combining(caracter))


def _tiene_marcador(texto: str) -> bool:
    """True si el texto rotula un pasaje como historico."""
    normalizado = _normalizar_texto(texto)
    return any(marcador in normalizado for marcador in MARCADORES_HISTORICOS)


def _leer_superficie_kb(kb_dir: "pathlib.Path | str") -> List[pathlib.Path]:
    """Archivos Markdown de la base de conocimiento, ordenados."""
    directorio = pathlib.Path(kb_dir)
    if not directorio.is_dir():
        return []
    return sorted(directorio.glob("**/*.md"))


def _lineas_con_marcador(path: "pathlib.Path | str") -> List[Tuple[int, str, bool]]:
    """(numero de linea, texto, True si la linea o su encabezado de seccion rotula historia)."""
    encabezado = ""
    filas: List[Tuple[int, str, bool]] = []
    for numero, linea in enumerate(
        pathlib.Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if linea.lstrip().startswith("#"):
            encabezado = linea
        filas.append((numero, linea, _tiene_marcador(linea) or _tiene_marcador(encabezado)))
    return filas


def _archivos_superficie(
    kb_dir: "pathlib.Path | str", referencia_paths: Sequence["pathlib.Path | str"]
) -> List[pathlib.Path]:
    """Superficie ampliada: base de conocimiento + material de referencia."""
    archivos = _leer_superficie_kb(kb_dir)
    archivos.extend(pathlib.Path(ruta) for ruta in referencia_paths)
    return archivos


def _modelos_superficie(texto: str) -> List[Tuple[str, str]]:
    """Pares (token tal como aparece, token normalizado `gemini-<version>-flash`)."""
    tokens: List[Tuple[str, str]] = []
    for coincidencia in _MODELO_SUPERFICIE_RE.finditer(texto or ""):
        version = coincidencia.group(1) or coincidencia.group(3)
        if version:
            tokens.append(
                (coincidencia.group(0).strip(), f"gemini-{version.lower()}-flash")
            )
    return tokens


def _timeouts_en_linea(linea: str) -> List[int]:
    """Valores de timeout declarados en una linea (formas explicitas y tupla de parametros)."""
    valores = [int(coincidencia.group(1)) for coincidencia in _TIMEOUT_EXPLICITO_RE.finditer(linea)]
    if re.search(r"timeout_seconds", linea, re.IGNORECASE):
        partes = linea.split("·")
        if len(partes) > 1:
            ultimo = re.search(r"(\d+)", partes[-1])
            if ultimo:
                valores.append(int(ultimo.group(1)))
    return valores


def _timeout_axios(texto: str) -> Optional[int]:
    """Timeout de Axios declarado en `api.ts`, en milisegundos."""
    coincidencia = _AXIOS_TIMEOUT_RE.search(texto or "")
    return int(coincidencia.group(1).replace("_", "")) if coincidencia else None


def _versiones_n8n_en_linea(linea: str) -> List[str]:
    """Versiones de N8N declaradas en una linea de la KB (chequeo 17)."""
    return [coincidencia.group(1) for coincidencia in _N8N_VERSION_RE.finditer(linea or "")]


def _versiones_fastapi_uvicorn_en_linea(linea: str) -> List[Tuple[str, str]]:
    """Pares (componente, version) de FastAPI/Uvicorn declarados en una linea."""
    pares: List[Tuple[str, str]] = []
    for coincidencia in _FASTAPI_UVICORN_TABLA_RE.finditer(linea or ""):
        pares.append(("FastAPI", coincidencia.group(1)))
        pares.append(("Uvicorn", coincidencia.group(2)))
    for coincidencia in _FASTAPI_UVICORN_PROSA_RE.finditer(linea or ""):
        pares.append(("FastAPI", coincidencia.group(1)))
        if coincidencia.group(2):
            pares.append(("Uvicorn", coincidencia.group(2)))
    return pares


def _restricciones_genai_en_linea(linea: str) -> List[str]:
    """Restricciones de `google-genai` declaradas en una linea (chequeo 17)."""
    return [coincidencia.group(1).strip() for coincidencia in _GENAI_RE.finditer(linea or "")]


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
# Chequeos 13 a 16 - superficie ampliada (c-148)
# ---------------------------------------------------------------------------
def _check_superficie_modelo(
    settings: Dict[str, Any],
    kb_dir: "pathlib.Path | str",
    referencia_paths: Sequence["pathlib.Path | str"],
) -> Check:
    nombre = "modelo vigente en knowledge-base y material de referencia (retirados solo si estan rotulados)"
    esperado = settings.get("gemini_model")
    problemas: List[str] = []
    for ruta in _archivos_superficie(kb_dir, referencia_paths):
        if not ruta.exists():
            continue  # lo reporta el chequeo 15
        for numero, linea, marcada in _lineas_con_marcador(ruta):
            for crudo, token in _modelos_superficie(linea):
                if token == esperado or marcada:
                    continue
                problemas.append(
                    f"{ruta.name}:{numero}: token de modelo retirado {crudo!r} ({token})"
                )
    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre, str(esperado or ""))


def _check_superficie_timeout(
    settings: Dict[str, Any],
    kb_dir: "pathlib.Path | str",
    referencia_paths: Sequence["pathlib.Path | str"],
) -> Check:
    nombre = "timeout vigente en contexto de parametros de Gemini (retirados solo si estan rotulados)"
    esperado = settings.get("gemini_timeout_seconds")
    problemas: List[str] = []
    for ruta in _archivos_superficie(kb_dir, referencia_paths):
        if not ruta.exists():
            continue
        es_params = ruta.name == "parameters_gemini.md"
        for numero, linea, marcada in _lineas_con_marcador(ruta):
            if not (es_params or _PARAM_GEMINI_RE.search(linea)):
                continue
            for valor in _timeouts_en_linea(linea):
                if valor not in TIMEOUTS_RETIRADOS or marcada:
                    continue
                problemas.append(
                    f"{ruta.name}:{numero}: timeout retirado {valor} s (vigente: {esperado} s)"
                )
    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(nombre, f"{esperado} s")


def _check_superficie_cubierta(
    kb_dir: "pathlib.Path | str",
    referencia_paths: Sequence["pathlib.Path | str"],
) -> Check:
    nombre = "superficie documental: knowledge-base y material de referencia presentes"
    faltantes: List[str] = []
    directorio = pathlib.Path(kb_dir)
    if not directorio.is_dir():
        faltantes.append(f"{directorio} (directorio ausente)")
    else:
        for archivo in KB_ARCHIVOS_ESPERADOS:
            if not (directorio / archivo).is_file():
                faltantes.append(f"knowledge-base/{archivo}")
    for ruta in referencia_paths:
        ruta = pathlib.Path(ruta)
        if not ruta.is_file():
            faltantes.append(ruta.name)
    if faltantes:
        return _failing(nombre, "archivos esperados ausentes: " + ", ".join(faltantes))
    return _passing(
        nombre,
        f"{len(KB_ARCHIVOS_ESPERADOS)} archivos de KB + {len(list(referencia_paths))} de referencia",
    )


def _check_invariante_timeout_cliente(
    settings: Dict[str, Any], api_ts_path: "pathlib.Path | str"
) -> Check:
    nombre = "invariante de timeout: el cliente Axios supera el peor caso total del backend"
    total = settings.get("gemini_total_timeout_seconds")
    ruta = pathlib.Path(api_ts_path)
    if total is None:
        return _failing(nombre, "Settings no declara gemini_total_timeout_seconds")
    if not ruta.is_file():
        return _failing(nombre, f"{ruta.name} no existe")
    cliente = _timeout_axios(ruta.read_text(encoding="utf-8"))
    if cliente is None:
        return _failing(nombre, f"{ruta.name} no declara timeout de Axios")
    backend_ms = int(total) * 1000
    if cliente <= backend_ms:
        return _failing(
            nombre,
            f"cliente {cliente} ms <= backend {backend_ms} ms (peor caso total de una clasificacion)",
        )
    return _passing(nombre, f"cliente {cliente} ms > backend {backend_ms} ms")


def _check_versiones_componentes(
    requirements: Dict[str, str],
    compose: Dict[str, Any],
    kb_dir: "pathlib.Path | str",
) -> Check:
    """Chequeo 17: las versiones de componentes de la KB coinciden con su fuente.

    Las fuentes son las mismas que usan los chequeos 4/5/6 para `config.yaml` y
    `CLAUDE.md`: `requirements.txt` para FastAPI/Uvicorn/google-genai y el compose
    para la imagen de N8N. Los valores esperados se derivan en tiempo de ejecucion;
    no se hardcodea ninguna version. Un pasaje rotulado como historico se exime.
    """
    nombre = "versiones de componentes: knowledge-base coincide con requirements.txt y el compose"
    tag = _n8n_tag(compose)
    fastapi_pin = _pin_exacto(requirements.get("fastapi", ""))
    uvicorn_pin = _pin_exacto(requirements.get("uvicorn", ""))
    genai_req = requirements.get("google-genai", "")
    problemas: List[str] = []

    if tag is None:
        problemas.append("docker-compose.yml no declara una imagen n8nio/n8n")

    for ruta in _leer_superficie_kb(kb_dir):
        for numero, linea, marcada in _lineas_con_marcador(ruta):
            if marcada:
                continue
            if tag is not None:
                for version in _versiones_n8n_en_linea(linea):
                    if version != tag:
                        problemas.append(
                            f"{ruta.name}:{numero}: N8N {version} (compose: {tag})"
                        )
            for componente, version in _versiones_fastapi_uvicorn_en_linea(linea):
                pin = fastapi_pin if componente == "FastAPI" else uvicorn_pin
                if not _prefijo_declarado(version, pin):
                    problemas.append(
                        f"{ruta.name}:{numero}: {componente} {version} (requirements: {pin})"
                    )
            for restriccion in _restricciones_genai_en_linea(linea):
                if not _restriccion_compatible(restriccion, genai_req):
                    problemas.append(
                        f"{ruta.name}:{numero}: google-genai {restriccion} "
                        f"(requirements: {genai_req})"
                    )

    if problemas:
        return _failing(nombre, "; ".join(problemas))
    return _passing(
        nombre,
        f"N8N {tag}, FastAPI {fastapi_pin}, Uvicorn {uvicorn_pin}, google-genai {genai_req}",
    )


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
    kb_dir: "pathlib.Path | str" = KB_DIR,
    referencia_paths: Sequence["pathlib.Path | str"] = DOCS_REFERENCIA,
    api_ts_path: "pathlib.Path | str" = API_TS_PATH,
) -> List[Check]:
    """Ejecuta los diecisiete chequeos de sincronizacion documental."""
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
        _check_superficie_modelo(settings, kb_dir, referencia_paths),
        _check_superficie_timeout(settings, kb_dir, referencia_paths),
        _check_superficie_cubierta(kb_dir, referencia_paths),
        _check_invariante_timeout_cliente(settings, api_ts_path),
        _check_versiones_componentes(requirements, compose, kb_dir),
    ]


def run_docs_stack_sync(
    settings_path: "pathlib.Path | str" = SETTINGS_PATH,
    constants_path: "pathlib.Path | str" = CONSTANTS_PATH,
    requirements_path: "pathlib.Path | str" = REQUIREMENTS_PATH,
    compose_path: "pathlib.Path | str" = COMPOSE_PATH,
    config_path: "pathlib.Path | str" = CONFIG_PATH,
    claude_path: "pathlib.Path | str" = CLAUDE_PATH,
    kb_dir: "pathlib.Path | str" = KB_DIR,
    referencia_paths: Sequence["pathlib.Path | str"] = DOCS_REFERENCIA,
    api_ts_path: "pathlib.Path | str" = API_TS_PATH,
) -> List[Check]:
    """Alias de `check_docs` con las rutas del repositorio por defecto."""
    return check_docs(
        settings_path=settings_path,
        constants_path=constants_path,
        requirements_path=requirements_path,
        compose_path=compose_path,
        config_path=config_path,
        claude_path=claude_path,
        kb_dir=kb_dir,
        referencia_paths=referencia_paths,
        api_ts_path=api_ts_path,
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
