"""
Módulo de pseudonimización de datos personales — Ley 25.326.

Responsabilidad:
    Provee la función pura `pseudonymize(text, internal_domains)` que detecta y
    reemplaza categorías de PII en texto libre mediante expresiones regulares
    compiladas a nivel de módulo. Devuelve el texto tratado y los conteos de
    reemplazos por categoría para auditoría DEBUG (sin exponer PII).

    Esta función es PURA: sin I/O, sin logging, sin acceso a settings.
    Los dominios corporativos se inyectan por parámetro desde la capa de servicio.

Categorías y etiquetas (en orden de aplicación):
    1. EMAIL   → [EMAIL]    (regex estructurado; alta especificidad)
    2. TELEFONO → [TELEFONO] (formatos argentinos: +54, con área, separadores)
    3. HOST    → [HOST]     (dominios configurados + fallback heurístico)
    4. PERSONA → [PERSONA]  (heurística: palabras capitalizadas, última)

Orden fijo (email→telefono→host→persona) para evitar colisiones: p.ej.
'juan.perez@empresa.com' colapsa a [EMAIL] antes de que el patrón de
nombres intente capturar 'juan.perez'.

Referencias:
    design.md § Decisiones 7, 8, 9
    tasks.md  §§ 1–6
"""

import re
from dataclasses import dataclass, field


# ─── Resultado ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PseudonymizationResult:
    """
    Resultado inmutable de pseudonymize().

    Atributos:
        texto:   Texto con los datos personales reemplazados por etiquetas.
        conteos: Diccionario {categoría: cantidad_de_reemplazos} para auditoría
                 DEBUG sin PII. Las categorías son: email, telefono, host, persona.
    """

    texto: str
    conteos: dict = field(default_factory=dict)


# ─── Etiquetas ────────────────────────────────────────────────────────────────

_LABEL_EMAIL = "[EMAIL]"
_LABEL_TELEFONO = "[TELEFONO]"
_LABEL_HOST = "[HOST]"
_LABEL_PERSONA = "[PERSONA]"


# ─── Patrones compilados ──────────────────────────────────────────────────────

# EMAIL: usuario@dominio.tld (soporta subdominio, +tag, punto en usuario)
# Requiere TLD de al menos 2 caracteres.
_RE_EMAIL = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# TELEFONO: formatos argentinos.
# Cubre: +54 261 555-1234 / (261) 555 1234 / 2615551234 / 261 555 1234
# Exige al menos 8 dígitos totales para evitar capturar números cortos.
_RE_TELEFONO = re.compile(
    r"""
    (?:
        # Con prefijo internacional +54 (opcional)
        (?:\+54[\s\-]?)?
        # Código de área: 3-4 dígitos (con o sin paréntesis)
        (?:\(?(?:11|[2-9]\d{2,3})\)?)
        # Separador opcional
        [\s\-]?
        # Número local: 6-8 dígitos, con separadores opcionales
        \d{3,4}
        [\s\-]?
        \d{4}
    )
    """,
    re.VERBOSE,
)

# HOST heurístico de fallback (siempre activo, sin configuración).
# Captura: srv-XXX, pc-XXX, cualquier-cosa.local, localhost.
_RE_HOST_FALLBACK = re.compile(
    r"""
    (?:
        (?:srv|pc)-\w+(?:\.\w+)*  # srv-correo01 / pc-recepcion.local
        |
        \w[\w.\-]*\.local          # nombre.local / pc.departamento.local
        |
        localhost                  # localhost (caso especial)
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

# PERSONA: secuencia de 2+ palabras capitalizadas (con tildes y ñ).
# Se aplica DESPUÉS de los demás patrones; las etiquetas [MAYÚSCULAS] ya insertadas
# son excluidas mediante negative lookahead para no reprocessarlas.
_RE_PERSONA = re.compile(
    r"(?<!\[)"                         # No precedido por '[' (inicio de etiqueta)
    r"\b[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñA-ZÁÉÍÓÚÜÑ]*"  # Primera palabra capitalizada
    r"(?:\s+[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+)+"  # Resto de palabras capitalizadas
    r"\b",
    re.UNICODE,
)

# Lista de exclusión: términos que empiezan con mayúscula pero NO son personas.
# Incluye las tres categorías del dominio y arranques de oración frecuentes.
_EXCLUSION_PERSONA: frozenset[str] = frozenset({
    # Categorías del dominio (exactas)
    "Sistemas",
    "Operaciones",
    "Soporte Técnico",
    # Palabras técnicas frecuentes con mayúscula inicial
    "FastAPI",
    "SQLAlchemy",
    "PostgreSQL",
    "Python",
    "Redis",
    "Docker",
    "Alembic",
    "Gemini",
    "Google",
    "Microsoft",
    "Outlook",
    "Twilio",
    "Linux",
    "Windows",
    "Internet",
    # Meses en español (pueden aparecer capitalizados en fechas)
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    # Días de la semana
    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo",
})


def _build_host_pattern(internal_domains: list[str]) -> re.Pattern | None:
    """
    Construye un patrón de regex para dominios corporativos configurados.

    Cada dominio en internal_domains se escapa y se usa para detectar cualquier
    hostname que termine en ese dominio (incluyendo subdominios).

    Retorna None si la lista está vacía.
    """
    if not internal_domains:
        return None
    # Para cada dominio, detectar: <cualquier-cosa>.dominio o el dominio solo
    escaped = [re.escape(d) for d in internal_domains]
    pattern = r"(?:" + "|".join(
        r"(?:\w[\w.\-]*\.)?" + e for e in escaped
    ) + r")"
    return re.compile(pattern, re.IGNORECASE)


def pseudonymize(text: str, internal_domains: list[str]) -> PseudonymizationResult:
    """
    Pseudonimiza datos personales en `text` reemplazándolos con etiquetas genéricas.

    Función PURA: sin I/O, sin efectos secundarios, sin acceso a settings.
    Los dominios corporativos se inyectan por parámetro desde la capa de servicio.

    Orden de aplicación (fijo para evitar colisiones):
        1. EMAIL    → [EMAIL]
        2. TELEFONO → [TELEFONO]
        3. HOST     → [HOST]    (dominios configurados + fallback heurístico)
        4. PERSONA  → [PERSONA] (heurística regex, con lista de exclusión)

    Args:
        text:             Texto libre con posible PII.
        internal_domains: Lista de dominios corporativos a enmascarar como [HOST].
                          Ejemplo: ["corp.empresa.com", "empresa.local"]

    Returns:
        PseudonymizationResult con el texto pseudonimizado y los conteos por categoría.
    """
    conteos: dict[str, int] = {"email": 0, "telefono": 0, "host": 0, "persona": 0}

    # 1. EMAIL
    text, n = _RE_EMAIL.subn(_LABEL_EMAIL, text)
    conteos["email"] = n

    # 2. TELEFONO
    text, n = _RE_TELEFONO.subn(_LABEL_TELEFONO, text)
    conteos["telefono"] = n

    # 3. HOST — dominios corporativos configurados (si los hay)
    re_corp = _build_host_pattern(internal_domains)
    if re_corp:
        text, n = re_corp.subn(_LABEL_HOST, text)
        conteos["host"] += n

    # 3b. HOST — fallback heurístico (srv-*, pc-*, *.local, localhost)
    text, n = _RE_HOST_FALLBACK.subn(_LABEL_HOST, text)
    conteos["host"] += n

    # 4. PERSONA — heurística regex con lista de exclusión
    def _replace_persona(match: re.Match) -> str:
        matched_text = match.group(0)
        if matched_text in _EXCLUSION_PERSONA:
            return matched_text
        # Excluir si es una etiqueta ya insertada (ej. [EMAIL])
        if matched_text.startswith("[") and matched_text.endswith("]"):
            return matched_text
        return _LABEL_PERSONA

    new_text = _RE_PERSONA.sub(_replace_persona, text)
    # Contar reemplazos de PERSONA
    n_persona = new_text.count(_LABEL_PERSONA) - text.count(_LABEL_PERSONA)
    conteos["persona"] = max(0, n_persona)
    text = new_text

    return PseudonymizationResult(texto=text, conteos=conteos)
