#!/usr/bin/env python3
"""
Acentuador normalizado para la tesis v9 (IA).

Acentua la prosa espanola de los `sections/*.tex` de la tesis v9 (IA),
incluyendo el texto dentro de argumentos de comandos portadores de texto
(\\section{}, \\caption{}, \\textbf{}, \\emph{}, \\item, \\footnote{}),
y preserva una allowlist de tokens protegidos (D2 de c-106):

  - Las cinco cadenas canonicas de categorias (SIN tilde).
  - Claves de \\label/\\ref/\\autoref/\\cref/\\eqref/\\cite/\\textcite/\\parencite.
  - Rutas de \\input/\\includegraphics/\\bibliography y de \\texttt.
  - Identificadores de repositorio en prosa.
  - Entornos verbatim/lstlisting/minted y \\verb|...|.
  - URLs, DOI, correos, matematica ($...$, \\(...\\), \\[...\\]).
  - Nombres de comandos LaTeX.

No crea archivos `.tex.bak`.

Uso:
  python acentuar_tesis_v9.py            # dry-run (no modifica)
  python acentuar_tesis_v9.py --apply    # escribe los cambios
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SECTIONS_DIR = SCRIPT_DIR / "v9 (IA)" / "paper" / "sections"

# ---------------------------------------------------------------------------
# Tokens protegidos (allowlist D2)
# ---------------------------------------------------------------------------
PROTECTED_PHRASES = [
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
    # Identificadores de repositorio en prosa
    "docs/Tesis/",
    "n8n/workflow.json",
    "docs/openapi.json",
    "gemini-3.6-flash",
    "requiere_revision_humana",
    "canal_origen_id",
    "App/Backend",
    "evaluation/",
    "data/",
    # Termino en ingles (glosario): no debe recibir tilde.
    "Multi-Version",
]

# Reemplazos sensibles a mayusculas exactas (homografos que solo cambian
# cuando la forma esta capitalizada, p. ej. "Publica" adjetivo en un nombre
# propio, frente al verbo en minuscula "publica").
CASED_MAP = {
    "Publica": "Pública",
}

# Comandos cuyos argumentos NO se acentuan (claves, rutas, codigo).
PROTECT_ARG_COMMANDS = (
    "label|ref|pageref|autoref|cref|Cref|eqref|"
    "cite|citep|citet|textcite|parencite|nocite|"
    "input|include|includegraphics|bibliography|addbibresource|bibliographystyle|"
    "usepackage|documentclass|"
    "texttt|lstinline|verb|url|doi|href|path|code|mono|ensuremath"
)

# ---------------------------------------------------------------------------
# Diccionario: forma sin tilde -> forma acentuada
# ---------------------------------------------------------------------------
ACCENTED = """
también según además después así allí aquí más está están
tecnología tecnologías tecnológica tecnológicas tecnológico tecnológicos
técnico técnica técnicos técnicas tecnicatura
informática informático informáticos informáticas
metodología metodologías metodológico metodológica metodológicos metodológicas
estadístico estadística estadísticas estadísticos
práctica prácticas práctico prácticos
académico académica académicos académicas
teórico teórica teóricos teóricas
específico específica específicos específicas
análisis síntesis hipótesis énfasis
máximo máxima máximos mínima mínimas mínimo mínimos
último última últimos últimas
único única únicos únicas únicamente
código códigos
método métodos
número números
período períodos
parámetro parámetros
fórmula fórmulas
gráfico gráfica gráficos gráficas
lógico lógica lógicos lógicas lógicamente
matemático matemática matemáticos matemáticas
semántico semántica semánticos semánticas
sistémico sistémica sistémicos sistémicas
económico económica económicos económicas
histórico histórica históricos históricas
empírico empírica empíricos empíricas
electrónico electrónica electrónicos electrónicas
automático automática automáticos automáticas
jurídico jurídica jurídicos jurídicas
diagnóstico diagnóstica
dinámico dinámica dinámicos dinámicas
analítico analítica analíticos analíticas
canónico canónica canónicos canónicas
característica características
clásico clásica clásicos clásicas
cronológico cronológica
determinístico determinística determinísticas
diacrítico diacríticos
geográfica geográfico geográficas geográficos
hipotético
idéntica idéntico
lingüístico lingüística lingüísticos lingüísticas
logística logístico
métrica métricas métrico
numérico numéricos numérica
óptica
ortográfica ortográfico
paramétrica paramétricas
periódico periódicos
política políticas
pragmático
probabilístico probabilísticos
problemática problemático
programática
pública público públicas públicos
república
sintético sintéticos
sistemática sistemáticas sistemático sistemáticos
temático temáticos temática
asincrónica asincrónicas asincrónicos
sincrónica sincrónico sincrónicos
atípica
estática estático
estratégica estratégicas estratégico estratégicos
éticas
física físico físicas
genéricas genéricos
léxico léxicos
telefónica telefónicas telefónico telefónicos
término términos
índice índices
multilingüe multilingües
esquemáticamente explícitamente íntegramente léxicamente
simultáneamente sistemáticamente automáticamente técnicamente
prácticamente básicamente rápidamente lógicamente
metodológicamente estadísticamente teóricamente empíricamente
históricamente económicamente críticamente científicamente
jurídicamente mínimamente máximamente fácilmente difícilmente
útilmente ágilmente
útil útiles
fácil fácilmente
difícil difícilmente
categoría categorías
economía
ingeniería
telefonía
tipología
geografía
bibliografía bibliografías
teoría teorías
energía energías
garantía garantías
mayoría minoría
soberanía
armonía
psicología
autonomía
ortografía
tipografía
jerarquía
éxito
época
área áreas
línea líneas
día días
país países
raíz
árbol árboles
carácter
portátil
móvil móviles
señal señala señalado señalados señalada señaladas señalar señales
enseña enseñan enseñanza
desempeño desempeños desempeña desempeñan
tamaño tamaños
compañía compañías
pequeño pequeña pequeños pequeñas
año años
diseño diseños diseñado diseñados diseñada diseñadas diseñar diseña
daño daños
acompaña acompañado acompañada acompañadas acompañan
artículo artículos
híbrido híbrida híbridos híbridas
fenómeno fenómenos
explícito explícita explícitos explícitas
desafío desafíos
envío
reenvío reenvíos
desvío
estándar
capítulo capítulos título títulos
vía vías
página páginas
próximo próxima próximos próximas
réplicas
tenía
había habían
podía podían podría podrían
debería deberían
tendría tendrían
sería serían
estaría
habría
haría
diría
sabría
seguía
conocía
requería
exponía
entendía
exigía
ofrecería
permitiría
reduciría
resultaría
constituiría
consultaría
afectaría
liberaría
replicaría
sugeriría
envía
calculó cálculos
válido válidos
módulo módulos
núcleo núcleos
máquina máquinas
adoptó aisló correspondió distribuyó ejecutó quedó arrojó detalló
evitó explicó incorporó materializó mitigó organizó superó ubicó
enriqueció obedeció consistió consumió ejerció enfrentó entregó
descendió elevó implicó ofreció fijó identificó
surgió desenvolvió operaría permitiéndole
actúa actúan acentúa acentúan sitúa sitúan evalúa evalúan
alfabético alfabéticos
arquitectónico arquitectónica arquitectónicos
catálogo catálogos
foráneo foránea foráneos foráneas
imagen imágenes
desvíos
límite límites
pirámide
búsqueda
volúmenes
árbitro
patrón
auditoría
propósito
contraseña contraseñas
cláusula cláusulas
instantáneo instantánea instantáneas instantáneos
contemporáneo contemporánea contemporáneos contemporáneas
mensajería
recién
véase
vacío vacía vacíos vacías
físicas
genérica
español española españoles españolas España
América Latinoamérica
acíclico acíclica acíclicos acíclicas
aritmética aritmético aritméticos aritméticas
armónica armónico armónicos armónicas
coreografía
"""

# Formas ambiguas que NO deben acentuarse automaticamente (colision con
# otra palabra o con un verbo conjugado distinto):
#   publica (verbo), hacia (preposicion), valida (verbo),
#   desarrollo/previa/promedio/rechazo/registro/completo (homografos ambiguos),
#   solo, aun, este/esta/esto, aquel, que/como/cual/quien/cuando/donde.
AMBIGUOUS_KEYS = {
    "publica", "hacia", "valida", "desarrollo", "previo", "promedio",
    "rechazo", "registro", "completo", "solo", "aun", "este", "esta",
    "esto", "estos", "estas", "ese", "esa", "esos", "esas", "aquel",
    "aquella", "que", "como", "cual", "quien", "cuando", "donde",
}


def _deaccent(word: str) -> str:
    table = str.maketrans(
        "áéíóúüñÁÉÍÓÚÜÑ",
        "aeiouunAEIOUUN",
    )
    return word.translate(table)


def _build_map(corpus_tokens):
    """Construye el mapa de reemplazo limitado a tokens presentes."""
    acc_map = {}
    for w in ACCENTED.split():
        key = _deaccent(w).lower()
        if key != w.lower() and key not in AMBIGUOUS_KEYS:
            acc_map[key] = w

    # Reglas de sufijo sobre los tokens reales del corpus.
    for t in corpus_tokens:
        if re.search(r"[áéíóúüñ]", t):
            continue
        if t in AMBIGUOUS_KEYS:
            continue
        if t.endswith("cion") and t not in acc_map:
            acc_map[t] = t[:-4] + "ción"
        elif t.endswith("sion") and t not in acc_map and t != "session":
            acc_map[t] = t[:-4] + "sión"
        elif t.endswith("andose") and t not in acc_map:
            acc_map[t] = t[:-6] + "ándose"
        elif t.endswith("iendose") and t not in acc_map:
            acc_map[t] = t[:-7] + "iéndose"
        elif t.endswith("endose") and t not in acc_map:
            acc_map[t] = t[:-6] + "éndose"

    # Palabras espanolas terminadas en -ion (singular) que no son -cion/-sion
    for t in ("conexion", "gestion", "inflexion", "region", "union"):
        acc_map[t] = t[:-3] + "ión"
    return acc_map


def _restore(text, store):
    for i in range(len(store) - 1, -1, -1):
        text = text.replace("\x00C%d\x00" % i, store[i])
    return text


def acentuar(text, acc_map, pattern):
    store = []

    def stash(s):
        store.append(s)
        return "\x00C%d\x00" % (len(store) - 1)

    # 1. Entornos verbatim/lstlisting/minted
    text = re.sub(
        r"\\begin\{(verbatim|lstlisting|minted)\}.*?\\end\{\1\}",
        lambda m: stash(m.group(0)), text, flags=re.S,
    )
    # 2. \verb|...| y \lstinline|...|
    text = re.sub(r"\\(?:verb|lstinline)\*?(\W).*?\1",
                  lambda m: stash(m.group(0)), text, flags=re.S)
    # 3. Matematica
    text = re.sub(r"\\\[.*?\\\]", lambda m: stash(m.group(0)), text, flags=re.S)
    text = re.sub(r"\\\(.*?\\\)", lambda m: stash(m.group(0)), text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", lambda m: stash(m.group(0)), text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", lambda m: stash(m.group(0)), text)
    # 4. URLs, DOI, correos (href: solo la url, no el texto visible)
    text = re.sub(r"\\href\{[^{}]*\}", lambda m: stash(m.group(0)), text)
    text = re.sub(r"\\(?:url|doi)\{[^{}]*\}", lambda m: stash(m.group(0)), text)
    text = re.sub(r"(?:https?|ftp)://\S+", lambda m: stash(m.group(0)), text)
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", lambda m: stash(m.group(0)), text)
    # 5. Argumentos de comandos protegidos (claves, rutas, codigo)
    text = re.sub(
        r"\\(?:" + PROTECT_ARG_COMMANDS + r")\*?(?:\[[^\]]*\])?\{[^{}]*\}",
        lambda m: stash(m.group(0)), text,
    )
    # 6. Frases protegidas (cadenas de categorias e identificadores)
    for phrase in PROTECTED_PHRASES:
        text = text.replace(phrase, stash(phrase))
    # 7. Nombres de comandos LaTeX restantes
    text = re.sub(r"\\[a-zA-Z@]+\*?", lambda m: stash(m.group(0)), text)

    # 8. Aplicacion del diccionario (con preservacion de mayusculas)
    def repl(m):
        raw = m.group(0)
        base = acc_map.get(raw.lower())
        if not base:
            return raw
        if raw.isupper() and len(raw) > 1:
            return base.upper()
        if raw[0].isupper():
            return base[0].upper() + base[1:]
        return base

    text = pattern.sub(repl, text)

    # 8b. Reemplazos sensibles a mayusculas exactas
    if CASED_MAP:
        cased = re.compile(r"\b(" + "|".join(re.escape(k) for k in CASED_MAP) + r")\b")
        text = cased.sub(lambda m: CASED_MAP[m.group(0)], text)

    # 9. Restauracion
    return _restore(text, store)


def main():
    apply = "--apply" in sys.argv
    files = sorted(SECTIONS_DIR.glob("*.tex"))

    corpus_tokens = set()
    for fp in files:
        raw = fp.read_text(encoding="utf-8").lower()
        corpus_tokens.update(re.findall(r"[a-záéíóúüñ]+", raw))

    acc_map = _build_map(corpus_tokens)
    keys = sorted(acc_map, key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in keys) + r")\b",
                         re.IGNORECASE)

    print("Mapa de reemplazo (%d entradas)" % len(acc_map))
    total = 0
    diff_lines = []
    for fp in files:
        orig = fp.read_text(encoding="utf-8")
        new = acentuar(orig, acc_map, pattern)
        if new != orig:
            diffs = [(a, b) for a, b in zip(orig.splitlines(), new.splitlines())
                     if a != b]
            print("%s: %d lineas modificadas" % (fp.name, len(diffs)))
            total += len(diffs)
            for a, b in diffs:
                diff_lines.append("%s\n- %s\n+ %s\n" % (fp.name, a, b))
            if apply:
                fp.write_text(new, encoding="utf-8")
        else:
            print("%s: sin cambios" % fp.name)
    print("=" * 70)
    print("Total lineas modificadas: %d" % total)

    if "--diff" in sys.argv:
        Path("/tmp/opencode/accent_diff.txt").write_text(
            "\n".join(diff_lines), encoding="utf-8")
    if not apply:
        print("DRY-RUN: no se modifico ningun archivo (usar --apply).")


if __name__ == "__main__":
    main()