"""
Diccionario de palabras clave y patrones regex para el clasificador determinístico.

Responsabilidad:
    Define el vocabulario controlado de términos técnicos asociados a cada
    categoría de incidente. El clasificador determinístico (DeterministicClassifier)
    utiliza estos patrones para calcular una puntuación por categoría y determinar
    si puede clasificar con suficiente confianza sin invocar a Gemini.

Criterios de diseño del diccionario:
    - Cada patrón es una expresión regular con límites de palabra (\b) para
      evitar coincidencias parciales (ej. "red" en "redacción").
    - Se incluyen variantes morfológicas del español rioplatense:
      plurales, formas verbales conjugadas, acentuación alternativa.
    - Los patrones de Sistemas priorizan terminología de infraestructura técnica.
    - Los patrones de Operaciones priorizan procesos administrativos y de gestión.
    - Los patrones de Soporte Técnico priorizan hardware de usuario y software de escritorio.

Extensibilidad:
    Para agregar nuevos términos a una categoría, únicamente es necesario
    añadir el patrón regex a la lista correspondiente. No es necesario
    modificar el código del clasificador. Los patrones se compilan al iniciar
    la aplicación (via lru_cache) y no tienen costo de compilación en runtime.
"""

from typing import Final

# Mapa de categoría → lista de patrones regex.
# Las claves coinciden exactamente con los valores válidos del campo "categoría"
# definido en el prompt de Gemini (docs/prompt_gemini.txt) y en el Anexo H.
KEYWORD_MAP: Final[dict[str, list[str]]] = {
    "Sistemas": [
        # Infraestructura de servidores y redes
        r"\bservidor(?:es)?\b",
        r"\bbase[s]?\s+de\s+datos\b",
        r"\bred(?:es)?\b",
        r"\binfrastructura\b",
        r"\binfrastructure\b",
        r"\bciberseguridad\b",
        r"\bfirewall\b",
        r"\bvpn\b",
        # Operaciones de backup y recuperación
        r"\bbackup\b",
        r"\brestore\b",
        r"\brestaurar\b",
        # Protocolos y servicios de red
        r"\bSMTP\b",
        r"\bcorreo\s+(?:corporativo|del\s+servidor)\b",
        r"\bDNS\b",
        r"\bDHCP\b",
        # Autenticación y directorio corporativo
        r"\bActive\s+Directory\b",
        r"\bautenticaci[oó]n\s+corporativa\b",
        r"\bcertificado(?:s)?\s+(?:SSL|digital(?:es)?)\b",
        # Virtualización y contenedores
        r"\bvirtualizaci[oó]n\b",
        r"\bhypervisor\b",
        r"\bcontainer(?:es)?\b",
        r"\bdocker\b",
        r"\bkubernetes\b",
        # Síntomas típicos de falla de sistemas (español rioplatense)
        r"\bcaído\b",
        r"\bca[eé](?:r|rse)\b",
        r"\bno\s+levanta\b",
        r"\bno\s+responde\b",
        r"\btimeout\b",
        r"\blatencia\b",
        r"\bcortó\s+la\s+red\b",
    ],
    "Operaciones": [
        # Gestión de reuniones y espacios físicos
        r"\breunión\b",
        r"\bsala(?:s)?\b",
        r"\breserva(?:r)?\b",
        # Trámites y procesos administrativos
        r"\btr[aá]mite(?:s)?\b",
        r"\btr[aá]mites\s+administrativos\b",
        r"\bproceso(?:s)?\s+compartido(?:s)?\b",
        r"\bplanificaci[oó]n\b",
        r"\bcontinuidad\s+operativa\b",
        r"\bservice\s+management\b",
        r"\bgestión\s+de\s+servicios\b",
        r"\bprocedimiento(?:s)?\b",
        # Gestión de proveedores y contratos
        r"\bproveed(?:or|ores)\b",
        r"\bcontrato(?:s)?\b",
        r"\bfacturaci[oó]n\b",
        r"\bpresupuesto(?:s)?\b",
        # Gestión de accesos y altas/bajas de usuarios
        r"\bhabilitaci[oó]n\b",
        r"\bformulario\s+de\s+solicitud\b",
        r"\bacceso\s+(?:a\s+)?(?:sistemas|aplicación)\b",
        r"\bnuevo\s+(?:empleado|ingreso|usuario)\b",
        r"\bbaja\s+de\s+(?:empleado|usuario)\b",
        r"\bcambio\s+de\s+(?:area|sector|rol)\b",
    ],
    "Soporte Técnico": [
        # Periféricos de impresión
        r"\bimpresora(?:s)?\b",
        r"\bimprime\b",
        # Periféricos de entrada y salida
        r"\bteclado(?:s)?\b",
        r"\bmouse\b",
        r"\bmonitor(?:es)?\b",
        r"\bpantalla\b",
        # Equipos de usuario final
        r"\bequipo(?:s)?\b",
        r"\bpc\b",
        r"\blaptop(?:s)?\b",
        r"\bnotebook(?:s)?\b",
        r"\bperiférico(?:s)?\b",
        # Software de escritorio y asistencia remota
        r"\bsoftware\s+cliente\b",
        r"\bsoftware\s+de\s+escritorio\b",
        r"\basistencia\s+remota\b",
        r"\bremoto\b",
        # Operaciones de instalación y configuración
        r"\binstalar\b",
        r"\binstalación\b",
        r"\bdesinstalar\b",
        r"\bactualizar\b",
        r"\bactualización\b",
        r"\bconfiguraci[oó]n\s+(?:de)?\s+(?:equipo|pc|dispositivo)\b",
        # Síntomas típicos de problemas de hardware/software de usuario
        r"\batasco(?:ado)?\b",
        r"\bpapel\s+atascado\b",
        r"\bcódigo\s+de\s+error\b",
        r"\bno\s+(?:enciende|prende|funciona)\b",
        r"\bse\s+traba\b",
        r"\bcolgado\b",
        r"\blento\b",
        # Aplicaciones de productividad de escritorio
        r"\boutlook\s+(?:del\s+)?(?:usuario|escritorio)\b",
        r"\bteams\b",
        r"\bzoom\b",
        r"\boffice\b",
        r"\bwindows\b",
    ],
}
