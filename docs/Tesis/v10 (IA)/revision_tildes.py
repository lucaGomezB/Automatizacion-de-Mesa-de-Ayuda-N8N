#!/usr/bin/env python3
"""Inventario y revision de tildes de la tesis v10 (change c-137, recomendacion B14).

Herramienta de solo biblioteca estandar. Por defecto NO modifica ningun archivo:
emite un inventario TSV determinista de candidatos de tilde faltante o
improcedente en `paper/sections/*.tex` (relativo a este script).

Cada candidato lleva una clase (`INEQUIVOCO`: la forma sin tilde no es palabra
valida; `AMBIGUO`: ambas formas existen y decide la categoria gramatical) y una
zona (`prosa`, `tabla`, `cita`). Las zonas protegidas (cadenas canonicas, codigo,
claves, rutas, matematica, comentarios y el Abstract en ingles) nunca se informan.

Uso (desde `docs/Tesis/v10 (IA)/`):

    python revision_tildes.py                  # inventario TSV (solo lectura)
    python revision_tildes.py --diff           # diff de lo INEQUIVOCO en prosa
    python revision_tildes.py --apply          # escribe solo lo INEQUIVOCO en prosa
    python revision_tildes.py --check          # 0 si todo candidato tiene decision `mantener`
    python revision_tildes.py --base DIR       # exige cambios puramente diacriticos vs DIR
    python revision_tildes.py --todos          # sin senales de contexto (barrido exhaustivo)

Los candidatos AMBIGUO, de tabla o de cita nunca se corrigen por script: se
deciden uno por uno y se registran en
`docs/Tesis/Correcciones/revision-tildes-decisiones.tsv`.
"""

import argparse
import bisect
import difflib
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

DIR_SCRIPT = Path(__file__).resolve().parent
DIR_SECCIONES = DIR_SCRIPT / "paper" / "sections"
RUTA_DECISIONES = DIR_SCRIPT.parent / "Correcciones" / "revision-tildes-decisiones.tsv"

COLUMNAS = ("archivo", "linea", "columna", "token", "sugerencia", "clase", "zona", "contexto")

# ---------------------------------------------------------------------------
# Constantes de zonas (decision D3)
# ---------------------------------------------------------------------------

ZONA_PROSA = 0
ZONA_PROTEGIDA = 1
ZONA_TABLA = 2
ZONA_CITA = 3
NOMBRES_ZONA = {ZONA_PROSA: "prosa", ZONA_TABLA: "tabla", ZONA_CITA: "cita"}

ENTORNOS_TABLA = ("tabular", "tabular*", "tabularx", "tabulary", "longtable")
SIN_SALTO_DE_PARRAFO = r"(?:(?!\n[ \t]*\n).)*?"

CADENAS_CANONICAS = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)

# Comandos cuyos argumentos obligatorios (la cantidad indicada) y opcionales
# [..] no son prosa: claves, rutas, codigo o parametros de formato.
COMANDOS_ARGUMENTO_PROTEGIDO = {
    "texttt": 1, "url": 1, "path": 1, "href": 1,
    "label": 1, "ref": 1, "autoref": 1, "cref": 1, "Cref": 1, "eqref": 1,
    "pageref": 1, "vref": 1, "nameref": 1, "hyperref": 0,
    "cite": 1, "citep": 1, "citet": 1, "parencite": 1, "Parencite": 1,
    "textcite": 1, "Textcite": 1, "autocite": 1, "footcite": 1, "nocite": 1,
    "citeauthor": 1, "citeyear": 1, "smartcite": 1,
    "input": 1, "include": 1, "includegraphics": 1, "bibliography": 1,
    "addbibresource": 1, "bibliographystyle": 1, "usepackage": 1,
    "documentclass": 1, "begin": 1, "end": 1,
    "color": 1, "textcolor": 1, "vspace": 1, "hspace": 1, "setlength": 2,
    "foreignlanguage": 1,
}

# Entornos cuya especificacion ({..} inmediatas) no es prosa.
ENTORNOS_CON_ESPECIFICACION = ENTORNOS_TABLA + ("array", "minipage", "lstlisting", "minted", "multicols")
MAXIMO_GRUPOS_DE_ESPECIFICACION = 2

ENTORNOS_LITERALES = ("verbatim", "verbatim*", "Verbatim", "lstlisting", "minted")
ENTORNOS_MATEMATICOS = (
    "equation", "equation*", "align", "align*", "gather", "gather*",
    "multline", "multline*", "eqnarray", "eqnarray*", "displaymath", "math",
    "flalign", "flalign*", "alignat", "alignat*",
)

DIRECTORIOS_CONOCIDOS = ("docs", "evaluation", "data", "App", "n8n", "paper", "scripts")
EXTENSIONES_ARCHIVO = (
    "md|py|json|yml|yaml|tex|bib|txt|sql|env|sh|js|ts|tsx|pdf|png|jpg|csv|"
    "tsv|toml|ini|cfg|xml|html|docx"
)

RE_PALABRA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")
RE_HUECO = re.compile(r"[ \t\r\n~{}]*")  # separacion simple entre dos palabras

# ---------------------------------------------------------------------------
# Lexico curado (decision D2)
# ---------------------------------------------------------------------------


def sin_marcas(palabra):
    """Quita acento agudo, dieresis y virgulilla (NFD sin marcas combinantes)."""
    return "".join(
        c for c in unicodedata.normalize("NFD", palabra) if not unicodedata.combining(c)
    )


# Semilla depurada de `acentuar_tesis.py` / `acentuar_tesis_v9.py` mas las formas
# de B14 y de la linea base. Solo palabras cuya forma sin tilde NO es una
# palabra valida del espanol: nunca homografos (practica, publica, valida,
# formula, tenia, seria, articulo, titulo de verbo, etc.) ni preteritos.
SEMILLA_INEQUIVOCA = """
también según además después así allí aquí allá ahí acá quizás jamás través detrás atrás
errónea erróneas erróneo erróneos heterogéneo heterogénea heterogéneos heterogéneas
antigüedad perímetro perímetros inequívoco inequívoca inequívocos inequívocas
engañoso engañosa engañosos engañosas múltiple múltiples escáner escáneres
simultáneos simultáneamente
tecnología tecnologías tecnológico tecnológica tecnológicos tecnológicas
técnico técnica técnicos técnicas técnicamente
informática informático informáticos informáticas
metodología metodologías metodológico metodológica metodológicos metodológicas
estadístico estadística estadísticos estadísticas estadísticamente
académico académica académicos académicas
teórico teórica teóricos teóricas teóricamente
específicos específicas específicamente
análisis síntesis hipótesis énfasis década décadas
máximo máxima máximos máximas mínimo mínima mínimos mínimas
últimos único única únicos únicas únicamente
código códigos método métodos parámetro parámetros
gráficos gráficas
lógico lógica lógicos lógicas lógicamente
matemático matemática matemáticos matemáticas
semántico semántica semánticos semánticas
sistémico sistémica sistémicos sistémicas
económico económica económicos económicas económicamente
histórico histórica históricos históricas históricamente
empírico empírica empíricos empíricas empíricamente
electrónico electrónica electrónicos electrónicas
automático automática automáticos automáticas automáticamente
jurídico jurídica jurídicos jurídicas jurídicamente
dinámico dinámica dinámicos dinámicas dinámicamente
analítico analítica analíticos analíticas analíticamente
canónico canónica canónicos canónicas
característica características
clásico clásica clásicos clásicas
cronológico cronológica cronológicos cronológicas
determinístico determinística determinísticos determinísticas
geográfico geográfica geográficos geográficas
hipotético hipotética hipotéticos hipotéticas
idéntico idéntica idénticos idénticas
lingüístico lingüística lingüísticos lingüísticas multilingüe multilingües
logístico logística métrica métricas métrico métricos
numérico numérica numéricos numéricas numéricamente
óptica ortográfica ortográfico paramétrica paramétricas periódicos
política políticas pragmático pragmática probabilístico probabilística probabilísticos
problemática problemático república sintético sintética sintéticos sintéticas
sistemática sistemático sistemáticos sistemáticas sistemáticamente
temático temática temáticos temáticas
asincrónica asincrónicas asincrónico asincrónicos sincrónica sincrónico sincrónicos
atípica estática estático estratégica estratégicas estratégico estratégicos
físico física físicas genéricos genéricas genérico genérica
léxico léxicos telefónica telefónicas telefónico telefónicos términos
básicamente prácticamente rápidamente científicamente críticamente mínimamente
máximamente fácilmente difícilmente útilmente típicamente explícitamente
íntegramente genéricamente
útil útiles fácil difícil difíciles
categoría categorías economía ingeniería telefonía tipología geografía bibliografía
bibliografías teoría teorías energía energías garantía garantías mayoría minoría
soberanía armonía psicología autonomía ortografía tipografía jerarquía mensajería
auditoría coreografía
éxito época línea líneas día días país países raíz árbol árboles carácter
portátil móvil móviles señal señales enseñanza desempeño desempeños tamaño tamaños
compañía compañías pequeño pequeña pequeños pequeñas daño daños diseño diseños
híbrido híbrida híbridos híbridas fenómeno fenómenos explícitos explícitas
desafíos estándar capítulo capítulos título títulos vías páginas
próximo próxima próximos próximas cálculos válidos módulos núcleo núcleos máquinas
actúa actúan acentúa acentúan sitúa sitúan evalúa evalúan
alfabético alfabéticos arquitectónico arquitectónica arquitectónicos arquitectónicas
catálogos foráneo foránea foráneos foráneas imágenes pirámide búsqueda volúmenes
árbitro patrón propósito contraseña contraseñas cláusulas
instantáneo instantánea instantáneas instantáneos
contemporáneo contemporánea contemporáneos contemporáneas
recién véase vacíos vacías español española españoles españolas España
América Latinoamérica aritmética aritmético aritméticos aritméticas
armónica armónico armónicos armónicas acíclico acíclica acíclicos acíclicas
había habían podía podían podría podrían debería deberían tendría tendrían serían
estaría habría haría diría sabría seguía conocía requería exponía entendía exigía
ofrecería permitiría reduciría resultaría constituiría consultaría afectaría
liberaría replicaría sugeriría
"""

LEXICO_INEQUIVOCO = {}
for _palabra in SEMILLA_INEQUIVOCA.split():
    if _palabra.lower() != sin_marcas(_palabra.lower()):
        LEXICO_INEQUIVOCO.setdefault(sin_marcas(_palabra.lower()), _palabra.lower())
del _palabra

# ---------------------------------------------------------------------------
# Pares y homografos (clase AMBIGUO, decision D2)
# ---------------------------------------------------------------------------

INTERROGATIVOS = {
    "que": "qué", "cual": "cuál", "cuales": "cuáles", "quien": "quién",
    "quienes": "quiénes", "como": "cómo", "cuando": "cuándo", "donde": "dónde",
    "cuanto": "cuánto", "cuanta": "cuánta", "cuantos": "cuántos",
    "cuantas": "cuántas", "adonde": "adónde",
}

# "que" es casi siempre conjuncion/relativo tras estos verbos: no se usa alli.
VERBOS_DE_CONOCIMIENTO = frozenset(
    "saber sabe saben sabia sabemos conocer conoce conocen determinar determina "
    "determinan indicar indica indican explicar explica explican preguntar "
    "pregunta preguntan decidir decide averiguar averigua".split()
)
CONECTORES_DE_PREGUNTA = frozenset(
    "y o e de del en a por para con sobre desde hasta entre segun hacia".split()
)

# Sustantivos homografos de un preterito de tercera persona: solo tras "se".
PRETERITOS_TRAS_SE = {
    "registro": "registró", "desarrollo": "desarrolló", "promedio": "promedió",
    "sustento": "sustentó", "implemento": "implementó", "ejecuto": "ejecutó",
    "utilizo": "utilizó", "configuro": "configuró", "limito": "limitó",
    "oriento": "orientó", "acoto": "acotó", "derivo": "derivó",
    "dimensiono": "dimensionó", "centro": "centró", "considero": "consideró",
}
# Preteritos curados (la forma sin tilde existe como verbo): siempre se informan.
PRETERITOS_CURADOS = {"asigno": "asignó", "gestiono": "gestionó"}
# Adjetivos homografos de verbo: se informan salvo tras el clitico "se".
ADJETIVOS_HOMOGRAFOS = {
    "valida": "válida", "publica": "pública", "simultanea": "simultánea",
    "practica": "práctica", "critica": "crítica",
}
# Pares raros: se informan siempre.
PARES_RAROS = {"aun": "aún", "mas": "más"}

COLOCACIONES_DE_CONTINUA = frozenset(
    "mejora integracion gestion supervision variable variables cuantitativa".split()
)
DETERMINANTES_Y_PREPOSICIONES = frozenset(
    "el la los las un una unos unas de del al en con por para sin sobre entre hacia "
    "hasta desde segun mediante tras ante bajo contra durante a su sus cada otra "
    "otro esta este esa ese dicha dicho misma mismo toda todo".split()
)
CLITICOS_Y_SUJETOS = frozenset("se lo la le me te nos él ella ello usted yo".split())
ANTECEDENTES_DE_ESTAR = frozenset("no lo ya se me le nos".split())
PREPOSICIONES = frozenset(
    "en de a con por para sin sobre entre hasta desde segun bajo contra tras ante "
    "hacia".split()
)
ADJETIVOS_DE_ESTADO = frozenset(
    "activo activa activos activas inactivo inactiva vacio vacia vacios vacias "
    "disponible disponibles listo listos presente presentes ausente ausentes "
    "pendiente pendientes vigente vigentes correcto correcta incorrecto incorrecta "
    "operativo operativa lleno llena fuera dentro cerca lejos bien mal "
    "todavia siempre".split()
)
PARTICIPIOS_IRREGULARES = frozenset(
    "abierto abierta abiertos abiertas hecho hecha hechos hechas escrito escrita "
    "puesto puesta visto vista roto rota resuelto resuelta cubierto cubierta "
    "impreso impresa previsto prevista dicho dicha".split()
)
SUSTANTIVOS_EN_PARTICIPIO = frozenset(
    "resultado resultados estado estados listado listados mercado mercados "
    "contenido contenidos significado sentido cuidado pedido pedidos salida "
    "salidas entrada entradas llamada llamadas medida medidas partida bajada "
    "subida comida bebida herida mirada jornada avenida corrida caida vida "
    "contenida tratado tratados dato grado lado".split()
)
TERMINACIONES_PARTICIPIO = ("ado", "ada", "ados", "adas", "ido", "ida", "idos", "idas")
MINIMO_LARGO_PARTICIPIO = 6

# Pares que se informan solo ante senales de contexto (o siempre con --todos).
PARES_CON_SENAL = {
    "esta": "está", "este": "esté", "hacia": "hacía", "continua": "continúa",
    "si": "sí", "formula": "fórmula", "fórmula": "formula",
}

# Tildes improcedentes (la ortografia vigente no las prescribe): INEQUIVOCO.
IMPROCEDENTES_INEQUIVOCOS = {
    "éste": "este", "ésta": "esta", "éstos": "estos", "éstas": "estas",
    "ése": "ese", "ésa": "esa", "ésos": "esos", "ésas": "esas",
    "aquél": "aquel", "aquélla": "aquella", "aquéllos": "aquellos",
    "aquéllas": "aquellas", "sólo": "solo",
}

# Tildes de homografos mal asignadas: AMBIGUO (depende de la categoria).
IMPROCEDENTES_AMBIGUOS = {"hacía": "hacia"}

SUFIJOS_SINGULARES = (("cion", "ción"), ("sion", "sión"))
MINIMO_LARGO_SUFIJO = 6


@dataclass(frozen=True)
class Candidato:
    """Una tilde faltante o improcedente detectada."""

    archivo: str
    linea: int
    columna: int
    token: str
    sugerencia: str
    clase: str
    zona: str
    contexto: str
    inicio: int  # desplazamiento absoluto en el texto (no se imprime)


# ---------------------------------------------------------------------------
# Calculo de zonas
# ---------------------------------------------------------------------------


def _fin_grupo(texto, pos, abre="{", cierra="}"):
    """Devuelve el indice posterior al cierre que corresponde a `texto[pos]`, o -1."""
    nivel = 0
    i = pos
    while i < len(texto):
        c = texto[i]
        if c == "\\":
            i += 2
            continue
        if c == abre:
            nivel += 1
        elif c == cierra:
            nivel -= 1
            if nivel == 0:
                return i + 1
        i += 1
    return -1


class Mascara:
    """Marca por caracter la zona de un texto LaTeX y una copia de trabajo
    donde los tramos ya clasificados se reemplazan por espacios."""

    def __init__(self, texto):
        self.texto = texto
        self.zonas = bytearray(len(texto))
        self.comentarios = bytearray(len(texto))
        self._trabajo = list(texto)

    def vista(self):
        return "".join(self._trabajo)

    def proteger(self, a, b):
        if a >= b:
            return
        self.zonas[a:b] = bytes([ZONA_PROTEGIDA]) * (b - a)
        for i in range(a, b):
            if self._trabajo[i] != "\n":
                self._trabajo[i] = " "

    def marcar_prosa_como(self, a, b, zona):
        """Reclasifica como `zona` los caracteres que aun son prosa en [a, b)."""
        for i in range(a, b):
            if self.zonas[i] == ZONA_PROSA:
                self.zonas[i] = zona

    def proteger_regex(self, patron, flags=0):
        for m in list(re.finditer(patron, self.vista(), flags)):
            self.proteger(m.start(), m.end())


def _proteger_comentarios(mascara):
    texto = mascara.texto
    inicio_linea = 0
    for linea in texto.split("\n"):
        barras = 0
        for i, c in enumerate(linea):
            if c == "\\":
                barras += 1
                continue
            if c == "%" and barras % 2 == 0:
                a, b = inicio_linea + i, inicio_linea + len(linea)
                mascara.proteger(a, b)
                mascara.comentarios[a:b] = bytes([1]) * (b - a)
                break
            barras = 0
        inicio_linea += len(linea) + 1


CIERRES = {"{": "}", "[": "]"}


def _proteger_grupos(mascara, vista, pos, cantidad, abridores="{["):
    """Protege hasta `cantidad` grupos {..} o [..] contiguos desde `pos`.

    Devuelve (posicion posterior al ultimo grupo, texto del primer grupo).
    """
    primero = None
    while cantidad > 0 and pos < len(vista) and vista[pos] in abridores:
        fin = _fin_grupo(vista, pos, vista[pos], CIERRES[vista[pos]])
        if fin < 0:
            break
        if primero is None:
            primero = vista[pos + 1:fin - 1]
        mascara.proteger(pos, fin)
        pos = fin
        cantidad -= 1
    return pos, primero


def _proteger_argumentos(mascara):
    """Protege claves, rutas y parametros de los comandos de COMANDOS_ARGUMENTO_PROTEGIDO."""
    vista = mascara.vista()
    for m in list(re.finditer(r"\\([A-Za-z]+)\*?", vista)):
        nombre = m.group(1)
        if nombre not in COMANDOS_ARGUMENTO_PROTEGIDO:
            continue
        pos = m.end()
        while pos < len(vista) and vista[pos] == " ":
            pos += 1
        pos, _ = _proteger_grupos(mascara, vista, pos, 9, "[")  # opcionales
        pos, primero = _proteger_grupos(
            mascara, vista, pos, COMANDOS_ARGUMENTO_PROTEGIDO[nombre], "{"
        )
        if nombre == "begin" and primero in ENTORNOS_CON_ESPECIFICACION:
            _proteger_grupos(mascara, vista, pos, MAXIMO_GRUPOS_DE_ESPECIFICACION)
        elif nombre == "foreignlanguage":
            _proteger_grupos(mascara, vista, pos, 1, "{")  # texto en otro idioma


def _marcar_tablas(mascara):
    """Cuerpo de los entornos tabulares: solo reporte (zona `tabla`)."""
    entornos = "|".join(re.escape(e) for e in ENTORNOS_TABLA)
    patron = r"\\begin\{(" + entornos + r")\}(.*?)\\end\{\1\}"
    for m in re.finditer(patron, mascara.texto, re.DOTALL):
        if mascara.comentarios[m.start()]:
            continue  # entorno comentado
        mascara.marcar_prosa_como(m.start(2), m.end(2), ZONA_TABLA)


def _marcar_citas(mascara):
    """Texto entre comillas: solo reporte (zona `cita`)."""
    patrones = (
        r"``" + SIN_SALTO_DE_PARRAFO + r"''",
        r'"' + SIN_SALTO_DE_PARRAFO + r'"',
        "\u00ab" + SIN_SALTO_DE_PARRAFO + "\u00bb",
        "\u201c" + SIN_SALTO_DE_PARRAFO + "\u201d",
    )
    for patron in patrones:
        for m in re.finditer(patron, mascara.texto, re.DOTALL):
            if mascara.zonas[m.start()] == ZONA_PROTEGIDA:
                continue
            mascara.marcar_prosa_como(m.start(), m.end(), ZONA_CITA)


def _proteger_entornos(mascara, nombres):
    """Protege el contenido completo de los entornos `nombres`."""
    for nombre in nombres:
        e = re.escape(nombre)
        mascara.proteger_regex(r"\\begin\{" + e + r"\}.*?\\end\{" + e + r"\}", re.DOTALL)


def calcular_mascara(texto):
    """Clasifica cada caracter de `texto` (zonas protegidas de la decision D3)."""
    mascara = Mascara(texto)
    _proteger_comentarios(mascara)
    # Resumen en ingles: desde \section*{Abstract} hasta el fin del archivo.
    m = re.search(r"\\section\*?\s*\{\s*Abstract\s*\}", mascara.vista(), re.IGNORECASE)
    if m:
        mascara.proteger(m.start(), len(texto))
    _proteger_entornos(mascara, ENTORNOS_LITERALES)
    mascara.proteger_regex(r"\\verb\*?(.).*?\1", re.DOTALL)
    mascara.proteger_regex(r"\\lstinline(?:\[[^\]]*\])?(?:\{[^}]*\}|(.).*?\1)", re.DOTALL)
    mascara.proteger_regex(r"\$\$.*?\$\$", re.DOTALL)
    mascara.proteger_regex(r"(?<!\\)\$" + SIN_SALTO_DE_PARRAFO + r"(?<!\\)\$", re.DOTALL)
    mascara.proteger_regex(r"(?<!\\)\\\(.*?(?<!\\)\\\)", re.DOTALL)
    mascara.proteger_regex(r"(?<!\\)\\\[.*?(?<!\\)\\\]", re.DOTALL)
    _proteger_entornos(mascara, ENTORNOS_MATEMATICOS)
    # Palabras con escape LaTeX de acento ({\'o}): ya estan acentuadas.
    mascara.proteger_regex(
        r"[A-Za-z]*(?:\{?\\['\"`^~]\s*\{?(?:\\i|[A-Za-z])\}?\}?[A-Za-z]*)+"
    )
    _proteger_argumentos(mascara)
    for cadena in CADENAS_CANONICAS:
        mascara.proteger_regex(r"\b" + re.escape(cadena) + r"\b")
    # Identificadores y rutas en prosa.
    mascara.proteger_regex(r"[^\s{}]*(?:\\_|(?<!\\)_)[^\s{}]*")
    mascara.proteger_regex(
        r"[\w.-]+(?:/[\w.-]+){2,}|(?:" + "|".join(DIRECTORIOS_CONOCIDOS) + r")/[\w.-]+"
    )
    mascara.proteger_regex(r"\b[\w-]+\.(?:" + EXTENSIONES_ARCHIVO + r")\b")
    # Nombres de comando y escapes de un caracter.
    mascara.proteger_regex(r"\\(?:[A-Za-z@]+\*?|.)", re.DOTALL)
    _marcar_tablas(mascara)
    _marcar_citas(mascara)
    return mascara


# ---------------------------------------------------------------------------
# Deteccion
# ---------------------------------------------------------------------------


def _preservar_forma(token, sugerencia):
    """Traslada la capitalizacion de `token` (inicial o todo mayusculas)."""
    if len(token) > 1 and token.isupper():
        return sugerencia.upper()
    if token[:1].isupper():
        return sugerencia[:1].upper() + sugerencia[1:]
    return sugerencia


def _limpiar_para_contexto(fragmento):
    fragmento = re.sub(r"\\[A-Za-z@]+\*?", " ", fragmento)
    fragmento = re.sub(r"[{}$~]", " ", fragmento)
    return fragmento.split()


def calcular_contexto(linea, desde, hasta, token):
    """Hasta cinco palabras a cada lado dentro de la linea, sin comandos LaTeX."""
    izquierda = _limpiar_para_contexto(linea[:desde])[-5:]
    derecha = _limpiar_para_contexto(linea[hasta:])[:5]
    return " ".join(izquierda + [token] + derecha)


def _marcar_enfasis(texto):
    """Caracteres dentro de \\emph / \\textit / \\textsl (terminos extranjeros)."""
    enfasis = bytearray(len(texto))
    for m in re.finditer(r"\\(?:emph|textit|textsl)\s*\{", texto):
        fin = _fin_grupo(texto, m.end() - 1)
        if fin > 0:
            enfasis[m.end():fin] = bytes([1]) * (fin - m.end())
    return enfasis


def _palabras_visibles(texto, mascara):
    """Palabras que no caen en ninguna zona protegida: (inicio, fin, texto)."""
    return [
        (m.start(), m.end(), m.group(0))
        for m in RE_PALABRA.finditer(texto)
        if ZONA_PROTEGIDA not in mascara.zonas[m.start():m.end()]
    ]


def construir_corpus_acentos(texto, mascara=None):
    """Mapa `forma sin marcas -> Counter(formas, con y sin tilde)` de la prosa."""
    mascara = mascara or calcular_mascara(texto)
    corpus = {}
    for inicio, _fin, palabra in _palabras_visibles(texto, mascara):
        if mascara.zonas[inicio] == ZONA_PROSA:
            bajo = palabra.lower()
            corpus.setdefault(sin_marcas(bajo), Counter())[bajo] += 1
    return corpus


def _variante_por_autoconsistencia(bajo, corpus):
    """Forma acentuada que el corpus usa para `bajo`, si es al menos tan frecuente.

    Si la forma sin tilde domina (p. ej. "activo" frente a "activó"), es otra
    palabra y no una errata.
    """
    formas = corpus.get(bajo)
    if not formas:
        return None
    acentuadas = Counter({f: n for f, n in formas.items() if f != bajo})
    if acentuadas and formas[bajo] <= sum(acentuadas.values()):
        return acentuadas.most_common(1)[0][0]
    return None


@dataclass(frozen=True)
class Entorno:
    """Palabras contiguas y signos que rodean a un token (para las senales)."""

    previas: tuple = ()  # hasta tres palabras previas contiguas, minusculas
    siguiente: str = ""
    puntuacion_siguiente: bool = False
    en_pregunta: bool = False
    primera_en_pregunta: bool = False

    @property
    def previa(self):
        return self.previas[0] if self.previas else None


def _es_participio(palabra):
    sm = sin_marcas(palabra)
    if sm in SUSTANTIVOS_EN_PARTICIPIO:
        return False
    if sm in PARTICIPIOS_IRREGULARES:
        return True
    return len(sm) >= MINIMO_LARGO_PARTICIPIO and sm.endswith(TERMINACIONES_PARTICIPIO)


def _senal_de_estar(entorno):
    """El token es forma de `estar` (esta/este) y no un demostrativo."""
    previa = entorno.previa
    if previa in ANTECEDENTES_DE_ESTAR:
        return True
    if (
        previa is None
        or previa == "que"  # "los que este apartado remite": relativo + demostrativo
        or sin_marcas(previa) in DETERMINANTES_Y_PREPOSICIONES
    ):
        return False  # inicio de oracion o tras preposicion/articulo: demostrativo
    if entorno.puntuacion_siguiente:
        return True
    siguiente = sin_marcas(entorno.siguiente)
    return (
        _es_participio(entorno.siguiente)
        or siguiente in ADJETIVOS_DE_ESTADO
        or siguiente in PREPOSICIONES
    )


def _senal_de_interrogativo(bajo, entorno):
    previa = entorno.previa
    if entorno.en_pregunta and (
        entorno.primera_en_pregunta or (previa and sin_marcas(previa) in CONECTORES_DE_PREGUNTA)
    ):
        return True
    if bajo == "que":
        return False  # tras verbos de comunicacion es conjuncion
    return previa is not None and sin_marcas(previa) in VERBOS_DE_CONOCIMIENTO


def _evaluar_par_con_senal(bajo, entorno):
    """True si el par `bajo` (esta, hacia, si...) se informa por su contexto."""
    previa = entorno.previa
    previa_sm = sin_marcas(previa) if previa else None
    if bajo in ("esta", "este"):
        return _senal_de_estar(entorno)
    if bajo == "continua":
        return not any(sin_marcas(p) in COLOCACIONES_DE_CONTINUA for p in entorno.previas[:2])
    if bajo == "fórmula":
        return previa_sm not in DETERMINANTES_Y_PREPOSICIONES
    if bajo == "formula":
        return previa_sm in DETERMINANTES_Y_PREPOSICIONES
    if bajo == "hacia":
        return previa in CLITICOS_Y_SUJETOS
    # bajo == "si": pronombre reflexivo ("por si mismo", "de si,").
    mismo = sin_marcas(entorno.siguiente) in ("mismo", "misma", "mismos", "mismas")
    tras_preposicion = previa_sm in PREPOSICIONES or previa_sm == "por"
    return mismo or (tras_preposicion and entorno.puntuacion_siguiente)


def _evaluar_palabra(token, enfasis, corpus, entorno=None, todos=False):
    """Devuelve (sugerencia, clase) para un token o None si no hay candidato."""
    entorno = entorno or Entorno()
    if len(token) <= 3 and token.isupper():
        return None  # sigla (SLA, API, SI)
    bajo = token.lower()
    if bajo in IMPROCEDENTES_INEQUIVOCOS:
        return IMPROCEDENTES_INEQUIVOCOS[bajo], "INEQUIVOCO"
    if bajo in IMPROCEDENTES_AMBIGUOS:
        return IMPROCEDENTES_AMBIGUOS[bajo], "AMBIGUO"
    if bajo in LEXICO_INEQUIVOCO:
        return LEXICO_INEQUIVOCO[bajo], "INEQUIVOCO"
    if bajo in PARES_RAROS:
        return PARES_RAROS[bajo], "AMBIGUO"
    if bajo in PRETERITOS_CURADOS:
        return PRETERITOS_CURADOS[bajo], "AMBIGUO"
    if bajo in ADJETIVOS_HOMOGRAFOS and entorno.previa != "se":
        return ADJETIVOS_HOMOGRAFOS[bajo], "AMBIGUO"
    if bajo in PRETERITOS_TRAS_SE and (todos or entorno.previa == "se"):
        return PRETERITOS_TRAS_SE[bajo], "AMBIGUO"
    if bajo in PARES_CON_SENAL and (todos or _evaluar_par_con_senal(bajo, entorno)):
        return PARES_CON_SENAL[bajo], "AMBIGUO"
    if bajo in INTERROGATIVOS and (todos or _senal_de_interrogativo(bajo, entorno)):
        return INTERROGATIVOS[bajo], "AMBIGUO"
    if not enfasis and len(bajo) >= MINIMO_LARGO_SUFIJO and not bajo.endswith("ssion"):
        for sin_tilde, con_tilde in SUFIJOS_SINGULARES:
            if bajo.endswith(sin_tilde):
                return bajo[: -len(sin_tilde)] + con_tilde, "INEQUIVOCO"
    if len(bajo) >= 4 and bajo not in EXCLUIDAS_AUTOCONSISTENCIA:
        variante = _variante_por_autoconsistencia(bajo, corpus)
        if variante:
            return variante, "AMBIGUO"
    return None


# La autoconsistencia nunca propone estas formas: son pares frecuentes o
# palabras funcionales cuya variante acentuada convive legitimamente.
EXCLUIDAS_AUTOCONSISTENCIA = frozenset(
    {sin_marcas(k) for k in PARES_CON_SENAL}
    | set(INTERROGATIVOS)
    | set(PARES_RAROS)
    | set(PRETERITOS_TRAS_SE)
    | set(PRETERITOS_CURADOS)
    | set(ADJETIVOS_HOMOGRAFOS)
    | {"esto", "ese", "esa", "solo", "estos", "estas"}
)


def _entorno_de(texto, palabras, i, aperturas, cierres):
    """Construye el `Entorno` de la palabra `i` de la lista `palabras`."""
    inicio, fin, _token = palabras[i]
    previas = []
    limite = inicio
    for j in range(i - 1, max(i - 4, -1), -1):
        a, b, p = palabras[j]
        if RE_HUECO.fullmatch(texto[b:limite]):
            previas.append(p.lower())
            limite = a
        else:
            break
    siguiente = ""
    if i + 1 < len(palabras):
        a, b, p = palabras[i + 1]
        if RE_HUECO.fullmatch(texto[fin:a]):
            siguiente = p.lower()
    resto = texto[fin:fin + 6].lstrip(" \t}")
    puntuacion = bool(resto) and resto[0] in ",.;:)!?"
    en_pregunta = False
    primera = False
    k = bisect.bisect_right(aperturas, inicio) - 1
    if k >= 0 and inicio < cierres[k]:
        en_pregunta = True
        primera = bool(RE_HUECO.fullmatch(texto[aperturas[k]:inicio]))
    return Entorno(tuple(previas), siguiente, puntuacion, en_pregunta, primera)


def _signos_de_pregunta(texto):
    """Pares (fin de apertura, posicion de cierre) de las preguntas del texto."""
    aperturas, cierres = [], []
    for m in re.finditer(r"\?`|¿", texto):
        cierre = None
        for c in re.finditer(r"\?(?!`)|!(?!`)", texto[m.end():m.end() + 600]):
            cierre = m.end() + c.start()
            break
        salto = re.search(r"\n[ \t]*\n", texto[m.end():m.end() + 600])
        if cierre is None or (salto and m.end() + salto.start() < cierre):
            continue
        aperturas.append(m.end())
        cierres.append(cierre)
    return aperturas, cierres


def inventariar_texto(texto, archivo="texto.tex", todos=False, corpus=None):
    """Inventario de candidatos de un texto LaTeX en memoria."""
    mascara = calcular_mascara(texto)
    enfasis = _marcar_enfasis(texto)
    if corpus is None:
        corpus = construir_corpus_acentos(texto, mascara)
    inicios_linea = [0] + [m.end() for m in re.finditer("\n", texto)]
    candidatos = []
    palabras = _palabras_visibles(texto, mascara)
    aperturas, cierres = _signos_de_pregunta(texto)
    for i, (inicio, fin, token) in enumerate(palabras):
        entorno = _entorno_de(texto, palabras, i, aperturas, cierres)
        veredicto = _evaluar_palabra(token, enfasis[inicio], corpus, entorno, todos)
        if veredicto is None:
            continue
        sugerencia, clase = veredicto
        indice = bisect.bisect_right(inicios_linea, inicio) - 1
        inicio_linea = inicios_linea[indice]
        fin_linea = texto.find("\n", inicio)
        linea = texto[inicio_linea:fin_linea if fin_linea >= 0 else len(texto)].rstrip("\r")
        candidatos.append(
            Candidato(
                archivo=archivo,
                linea=indice + 1,
                columna=inicio - inicio_linea + 1,
                token=token,
                sugerencia=_preservar_forma(token, sugerencia),
                clase=clase,
                zona=NOMBRES_ZONA[mascara.zonas[inicio]],
                contexto=calcular_contexto(
                    linea, inicio - inicio_linea, fin - inicio_linea, token
                ),
                inicio=inicio,
            )
        )
    return candidatos


def nombre_de_archivo(ruta):
    """Ruta relativa al script si esta debajo de el; si no, la ruta tal cual."""
    ruta = Path(ruta)
    try:
        return ruta.resolve().relative_to(DIR_SCRIPT.resolve()).as_posix()
    except ValueError:
        return ruta.as_posix()


def leer_texto(ruta):
    """Lee UTF-8 sin traducir terminadores de linea (CRLF/LF se preservan)."""
    with open(ruta, "r", encoding="utf-8", newline="") as f:
        return f.read()


def inventariar_archivos(rutas, todos=False):
    """Inventario de varios archivos; la autoconsistencia usa el corpus conjunto."""
    textos = [(nombre_de_archivo(r), leer_texto(r)) for r in rutas]
    corpus = {}
    for _nombre, texto in textos:
        for sin, formas in construir_corpus_acentos(texto).items():
            corpus.setdefault(sin, Counter()).update(formas)
    candidatos = []
    for nombre, texto in textos:
        candidatos.extend(inventariar_texto(texto, nombre, todos, corpus))
    return sorted(candidatos, key=lambda c: (c.archivo, c.linea, c.columna))


@dataclass(frozen=True)
class Decision:
    """Fila del registro de decisiones (`revision-tildes-decisiones.tsv`)."""

    decision: str
    forma_final: str
    justificacion: str


def normalizar_contexto(contexto):
    return " ".join(contexto.split())


def clave_de(candidato):
    """Clave de una decision: archivo, token y contexto, sin numero de linea."""
    return (Path(candidato.archivo).name, candidato.token, normalizar_contexto(candidato.contexto))


def cargar_decisiones(ruta):
    """Lee el registro TSV; devuelve {clave: Decision}. Sin archivo, vacio."""
    ruta = Path(ruta)
    if not ruta.is_file():
        return {}
    decisiones = {}
    for linea in leer_texto(ruta).splitlines():
        if not linea.strip() or linea.startswith("#"):
            continue
        campos = linea.split("\t")
        if campos[0] == "archivo":
            continue
        campos += [""] * (6 - len(campos))
        archivo, token, contexto, decision, forma_final, justificacion = campos[:6]
        decisiones[(Path(archivo).name, token, normalizar_contexto(contexto))] = Decision(
            decision.strip(), forma_final, justificacion
        )
    return decisiones


def es_aplicable(candidato, decisiones):
    """INEQUIVOCO en prosa y sin decision `mantener`."""
    if candidato.clase != "INEQUIVOCO" or candidato.zona != "prosa":
        return False
    decision = decisiones.get(clave_de(candidato))
    return not (decision and decision.decision == "mantener")


def aplicar_correcciones(texto, candidatos):
    """Devuelve `texto` con las sugerencias de `candidatos` aplicadas."""
    for c in sorted(candidatos, key=lambda c: c.inicio, reverse=True):
        if texto[c.inicio:c.inicio + len(c.token)] != c.token:
            raise ValueError(f"el texto no coincide con el candidato {c.token!r} en {c.archivo}")
        texto = texto[:c.inicio] + c.sugerencia + texto[c.inicio + len(c.token):]
    return texto


def escribir_texto(ruta, texto):
    """Escribe UTF-8 sin traducir terminadores de linea y sin crear respaldos."""
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(texto)


def _revisar_y_corregir(rutas, decisiones, todos, escribir, mostrar_diff):
    total = 0
    for ruta in rutas:
        texto = leer_texto(ruta)
        nombre = nombre_de_archivo(ruta)
        candidatos = [
            c for c in inventariar_texto(texto, nombre, todos) if es_aplicable(c, decisiones)
        ]
        if not candidatos:
            continue
        nuevo = aplicar_correcciones(texto, candidatos)
        total += len(candidatos)
        if mostrar_diff:
            diff = difflib.unified_diff(
                texto.splitlines(keepends=True), nuevo.splitlines(keepends=True),
                fromfile=f"a/{nombre}", tofile=f"b/{nombre}",
            )
            sys.stdout.writelines(diff)
        if escribir:
            escribir_texto(ruta, nuevo)
    return total


MARCAS_DIACRITICAS = frozenset({"\u0301", "\u0308", "\u0303"})  # agudo, dieresis, virgulilla
ESCAPES_DE_ACENTO = (
    re.compile(r"\{\\['\"~]\s*\{?(\\i|[A-Za-z])\}?\}"),  # {\'o}, {\'{o}}, {\~n}
    re.compile(r"\\['\"~]\{(\\i|[A-Za-z])\}"),  # \'{o}, \~{n}
    re.compile(r"\\['\"~]\s*(\\i|[A-Za-z])"),  # \'o, \~n, \"u, \'\i
)


def sin_diacriticos(texto):
    """Quita agudo, dieresis y virgulilla y normaliza los escapes LaTeX de acento."""
    for patron in ESCAPES_DE_ACENTO:
        texto = patron.sub(lambda m: m.group(1).replace("\\i", "i"), texto)
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if c not in MARCAS_DIACRITICAS
    )


def comparar_con_base(base, nuevo):
    """Violaciones del invariante diacritico: [(linea, linea_base, linea_nueva)].

    La linea 0 indica una cantidad distinta de lineas.
    """
    lineas_base, lineas_nuevo = base.splitlines(), nuevo.splitlines()
    if len(lineas_base) != len(lineas_nuevo):
        return [(0, f"{len(lineas_base)} lineas", f"{len(lineas_nuevo)} lineas")]
    return [
        (numero, previa, actual)
        for numero, (previa, actual) in enumerate(zip(lineas_base, lineas_nuevo), start=1)
        if previa != actual and sin_diacriticos(previa) != sin_diacriticos(actual)
    ]


def verificar_base(rutas, carpeta_base):
    """Compara cada archivo con su homonimo en `carpeta_base`; devuelve el codigo de salida."""
    codigo = 0
    for ruta in rutas:
        previa = Path(carpeta_base) / Path(ruta).name
        if not previa.is_file():
            print(f"error: no existe el homonimo de {ruta} en {carpeta_base}", file=sys.stderr)
            codigo = 1
            continue
        nombre = nombre_de_archivo(ruta)
        for numero, antes, despues in comparar_con_base(leer_texto(previa), leer_texto(ruta)):
            print(f"{nombre}:{numero}\n  base:  {antes}\n  nuevo: {despues}")
            codigo = 1
    return codigo


def comprobar(rutas, decisiones, todos=False):
    """Pasada corta: candidatos sin decision `mantener`. Devuelve (pendientes, huerfanas)."""
    candidatos = inventariar_archivos(rutas, todos)
    pendientes = [
        c for c in candidatos
        if not (decisiones.get(clave_de(c)) and decisiones[clave_de(c)].decision == "mantener")
    ]
    claves_vistas = {clave_de(c) for c in candidatos}
    nombres = {Path(r).name for r in rutas}
    huerfanas = [k for k in decisiones if k[0] in nombres and k not in claves_vistas]
    return pendientes, huerfanas


def objetivos_por_defecto():
    return sorted(DIR_SECCIONES.glob("*.tex"))


def formatear_fila(c):
    campos = (c.archivo, c.linea, c.columna, c.token, c.sugerencia, c.clase, c.zona, c.contexto)
    return "\t".join(str(campo).replace("\t", " ") for campo in campos)


def _configurar_salida():
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", newline="\n")


def construir_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--archivos", nargs="+", metavar="ARCHIVO",
        help="archivos a revisar (por defecto paper/sections/*.tex junto al script)",
    )
    parser.add_argument(
        "--diff", action="store_true",
        help="muestra el diff unificado de las correcciones INEQUIVOCO en prosa, sin escribir",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="escribe solo las correcciones INEQUIVOCO en prosa",
    )
    parser.add_argument(
        "--decisiones", metavar="TSV", default=str(RUTA_DECISIONES),
        help="registro de decisiones (por defecto docs/Tesis/Correcciones/...)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="codigo 0 si todo candidato tiene decision `mantener`; si no, 1 y los lista",
    )
    parser.add_argument(
        "--base", metavar="DIR",
        help="exige que cada archivo difiera de su homonimo en DIR solo en diacriticos",
    )
    parser.add_argument(
        "--todos", action="store_true",
        help="desactiva las senales de contexto: informa todas las ocurrencias de los pares",
    )
    return parser


def main(argv=None):
    _configurar_salida()
    args = construir_parser().parse_args(argv)
    rutas = [Path(a) for a in args.archivos] if args.archivos else objetivos_por_defecto()
    faltantes = [r for r in rutas if not r.is_file()]
    if faltantes:
        for ruta in faltantes:
            print(f"error: no existe el archivo {ruta}", file=sys.stderr)
        return 2
    if args.base:
        return verificar_base(rutas, args.base)
    if args.check:
        pendientes, huerfanas = comprobar(rutas, cargar_decisiones(args.decisiones), args.todos)
        for archivo, token, contexto in huerfanas:
            print(
                f"aviso: decision sin candidato en el texto: {archivo} | {token} | {contexto}",
                file=sys.stderr,
            )
        if not pendientes:
            return 0
        print("\t".join(COLUMNAS))
        for candidato in pendientes:
            print(formatear_fila(candidato))
        print(f"{len(pendientes)} candidatos pendientes", file=sys.stderr)
        return 1
    if args.diff or args.apply:
        total = _revisar_y_corregir(
            rutas, cargar_decisiones(args.decisiones), args.todos, args.apply, args.diff
        )
        if args.apply:
            print(f"{total} correcciones aplicadas", file=sys.stderr)
        return 0
    print("\t".join(COLUMNAS))
    for candidato in inventariar_archivos(rutas, args.todos):
        print(formatear_fila(candidato))
    return 0


if __name__ == "__main__":
    sys.exit(main())
