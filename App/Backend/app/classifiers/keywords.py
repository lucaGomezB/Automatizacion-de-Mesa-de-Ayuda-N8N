"""
Diccionario de palabras clave y patrones regex para el clasificador determinístico.

Responsabilidad:
    Define el vocabulario controlado de términos técnicos asociados a cada
    sector canónico (C-27). El clasificador determinístico
    (DeterministicClassifier) usa estos patrones para calcular una puntuación
    por sector y decidir si puede clasificar sin invocar a Gemini.

Vocabulario canónico: cinco sectores, sin tildes. `Operaciones` fue eliminada
y sus términos se redistribuyeron; el viejo `Soporte Técnico` se dividió en
`Soporte Tecnico Hardware` y `Soporte Tecnico Software`.

Criterios de diseño:
    - Cada patrón usa límites de palabra (\\b) para evitar coincidencias parciales.
    - Se incluyen variantes morfológicas y de acentuación del español rioplatense.
    - Las claves provienen de `app.constants.SECTORES_CANONICOS` para garantizar
      una única fuente de verdad (design.md D8).
"""

from typing import Final

from app.constants import SECTORES_CANONICOS

KEYWORD_MAP: Final[dict[str, list[str]]] = {
    # ── Seguridad Informatica ────────────────────────────────────────────────
    "Seguridad Informatica": [
        r"\bciberseguridad\b",
        r"\bfirewall(?:s)?\b",
        r"\bvpn\b",
        r"\bmalware\b",
        r"\bransomware\b",
        r"\bphishing\b",
        r"\bantivirus\b",
        r"\bintrusi[oó]n(?:es)?\b",
        r"\bincidente\s+de\s+seguridad\b",
        r"\bfuga\s+de\s+(?:datos|informaci[oó]n)\b",
        r"\bpermisos\s+de\s+acceso\b",
        r"\bautenticaci[oó]n\s+corporativa\b",
        r"\bcertificado(?:s)?\s+(?:SSL|digital(?:es)?)\b",
        r"\bcuenta(?:s)?\s+comprometida(?:s)?\b",
    ],
    # ── Soporte Tecnico Hardware ─────────────────────────────────────────────
    "Soporte Tecnico Hardware": [
        r"\bimpresora(?:s)?\b",
        r"\bimprime\b",
        r"\bteclado(?:s)?\b",
        r"\bmouse\b",
        r"\bmonitor(?:es)?\b",
        r"\bpantalla(?:s)?\b",
        r"\bequipo(?:s)?\b",
        r"\bpc\b",
        r"\blaptop(?:s)?\b",
        r"\bnotebook(?:s)?\b",
        r"\bperif[eé]rico(?:s)?\b",
        r"\bpapel\s+atascado\b",
        r"\bno\s+(?:enciende|prende)\b",
        r"\bdisco\s+(?:r[ií]gido|duro)\b",
        r"\bmemoria\s+ram\b",
        r"\bbater[ií]a\b",
        r"\bcargador\b",
        r"\bdocking\b",
        r"\besc[aá]ner\b",
        r"\bc[aá]mara\b",
    ],
    # ── Soporte Tecnico Software ─────────────────────────────────────────────
    "Soporte Tecnico Software": [
        r"\bsoftware\s+(?:cliente|de\s+escritorio)\b",
        r"\basistencia\s+remota\b",
        r"\bremoto\b",
        r"\binstalar\b",
        r"\binstalaci[oó]n\b",
        r"\bdesinstalar\b",
        r"\bactualizar\b",
        r"\bactualizaci[oó]n\b",
        r"\bconfiguraci[oó]n\b",
        r"\boutlook\b",
        r"\bteams\b",
        r"\bzoom\b",
        r"\boffice\b",
        r"\bwindows\b",
        r"\bc[oó]digo\s+de\s+error\b",
        r"\bse\s+traba\b",
        r"\bcolgado\b",
        r"\blento\b",
        r"\baplicaci[oó]n(?:es)?\b",
        r"\bcorreo\s+del\s+usuario\b",
        r"\bno\s+funciona\b",
    ],
    # ── Bases de Datos ───────────────────────────────────────────────────────
    "Bases de Datos": [
        r"\bbases?\s+de\s+datos\b",
        r"\bbase\s+de\s+datos\b",
        r"\bSQL\b",
        r"\bconsulta(?:s)?\b",
        r"\bbackup\b",
        r"\brestore\b",
        r"\brestaurar\b",
        r"\breplicaci[oó]n\b",
        r"\besquema\s+de\s+datos\b",
        r"\bcorrupci[oó]n\s+de\s+datos\b",
        r"\bpostgresql\b",
        r"\bmysql\b",
        r"\boracle\b",
        r"\bmongodb\b",
        r"\b[ií]ndice\s+de\s+la\s+tabla\b",
    ],
    # ── Sistemas ─────────────────────────────────────────────────────────────
    "Sistemas": [
        r"\bservidor(?:es)?\b",
        r"\bred(?:es)?\b",
        r"\binfraestructura\b",
        r"\bDNS\b",
        r"\bDHCP\b",
        r"\bSMTP\b",
        r"\bActive\s+Directory\b",
        r"\bvirtualizaci[oó]n\b",
        r"\bhypervisor\b",
        r"\bcontainer(?:es)?\b",
        r"\bdocker\b",
        r"\bkubernetes\b",
        r"\bno\s+responde\b",
        r"\btimeout\b",
        r"\blatencia\b",
        r"\bca[ií]do\b",
        r"\bno\s+levanta\b",
        r"\bse\s+cay(?:o|ó)\b",
        r"\bcorreo\s+corporativo\b",
    ],
}

# Invariante del vocabulario: las claves del mapa son exactamente los 5 sectores.
assert set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS), (
    "KEYWORD_MAP debe cubrir exactamente SECTORES_CANONICOS"
)
