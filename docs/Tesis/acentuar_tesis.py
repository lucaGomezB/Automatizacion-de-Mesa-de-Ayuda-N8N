#!/usr/bin/env python3
"""
Acentuador automatico de texto espanol en archivos LaTeX.
Preserva comandos LaTeX, bloques verbatim, referencias y URLs.
Aplica diccionario de palabras comunes + reglas de patrones.
Genera backup de cada archivo antes de modificar.

Uso: python acentuar_tesis.py [--dry-run]
"""

import re
import sys
import os
import shutil
from pathlib import Path

# --- DIRECTORIOS ---
PAPER_DIR = Path(__file__).parent / "v8 (IA)" / "paper"
SECTIONS_DIR = PAPER_DIR / "sections"

# --- MAPEO DE PALABRAS SIN TILDE → CON TILDE ---
# Palabras completas que siempre llevan tilde en espanol.
# Ordenado: las mas largas primero para evitar reemplazos parciales.
DICCIONARIO = {
    # -ción / -sión
    "automatizacion": "automatización",
    "clasificacion": "clasificación",
    "implementacion": "implementación",
    "evaluacion": "evaluación",
    "organizacion": "organización",
    "solucion": "solución",
    "aplicacion": "aplicación",
    "informacion": "información",
    "comunicacion": "comunicación",
    "configuracion": "configuración",
    "integracion": "integración",
    "validacion": "validación",
    "documentacion": "documentación",
    "investigacion": "investigación",
    "presentacion": "presentación",
    "definicion": "definición",
    "introduccion": "introducción",
    "conclusion": "conclusión",
    "justificacion": "justificación",
    "delimitacion": "delimitación",
    "orquestacion": "orquestación",
    "intervencion": "intervención",
    "persistencia": "persistencia",  # no lleva tilde, pero esta por si acaso
    "descripcion": "descripción",
    "recepcion": "recepción",
    "resolucion": "resolución",
    "migracion": "migración",
    "exportacion": "exportación",
    "importacion": "importación",
    "provision": "provisión",
    "supervision": "supervisión",
    "dispersion": "dispersión",
    "interaccion": "interacción",
    "ejecucion": "ejecución",
    "version": "versión",
    "atencion": "atención",
    "visualizacion": "visualización",
    "restauracion": "restauración",
    "seleccion": "selección",
    "compilacion": "compilación",
    "especificacion": "especificación",
    "asignacion": "asignación",
    "comparacion": "comparación",
    "composicion": "composición",
    "normalizacion": "normalización",
    "separacion": "separación",
    "reproduccion": "reproducción",
    "interpretacion": "interpretación",
    "observacion": "observación",
    "limitacion": "limitación",
    "acumulacion": "acumulación",
    "modificacion": "modificación",
    "dependencia": "dependencia",  # no lleva tilde
    "adopcion": "adopción",
    "construccion": "construcción",
    "distincion": "distinción",
    "proporcion": "proporción",
    "reduccion": "reducción",
    "derivacion": "derivación",
    "sugerencia": "sugerencia",  # no lleva tilde
    "continuacion": "continuación",
    "exposicion": "exposición",
    "operacion": "operación",
    "combinacion": "combinación",
    "colaboracion": "colaboración",
    "correccion": "corrección",
    "administracion": "administración",
    "centralizacion": "centralización",
    "cuantificacion": "cuantificación",
    "sincronizacion": "sincronización",
    "generalizacion": "generalización",
    "planificacion": "planificación",
    "capacitacion": "capacitación",
    "depuracion": "depuración",
    "depreciacion": "depreciación",
    "federacion": "federación",
    "finalizacion": "finalización",
    "generacion": "generación",
    "identificacion": "identificación",
    "transcripcion": "transcripción",
    "proyeccion": "proyección",
    "replicacion": "replicación",
    "representacion": "representación",
    "satisfaccion": "satisfacción",
    "transformacion": "transformación",
    "utilizacion": "utilización",
    "variacion": "variación",
    "verificacion": "verificación",
    "recomendacion": "recomendación",
    "digitacion": "digitación",
    "digitalizacion": "digitalización",
    "dimension": "dimensión",
    "duracion": "duración",
    "estandarizacion": "estandarización",
    "explicacion": "explicación",
    "explicitacion": "explicitación",
    "implicacion": "implicación",
    "revision": "revisión",
    "extraccion": "extracción",
    "funcion": "función",
    "fijacion": "fijación",
    "gestion": "gestión",
    "conservacion": "conservación",
    "depuracion": "depuración",
    "instruccion": "instrucción",
    "intencion": "intención",
    "interrupcion": "interrupción",
    "medicion": "medición",
    "notacion": "notación",
    "ocasion": "ocasión",
    "orientacion": "orientación",
    "participacion": "participación",
    "particion": "partición",
    "peticion": "petición",
    "publicacion": "publicación",
    "recoleccion": "recolección",
    "recuperacion": "recuperación",
    "redaccion": "redacción",
    "reestructuracion": "reestructuración",
    "reparacion": "reparación",
    "restriccion": "restricción",
    "solicitud": "solicitud",  # no lleva tilde
    "sustitucion": "sustitución",
    "trazabilidad": "trazabilidad",  # no lleva tilde
    "traduccion": "traducción",
    "validacion": "validación",

    # Palabras agudas terminadas en vocal
    "tambien": "también",
    "segun": "según",
    "ademas": "además",
    "despues": "después",
    "asi": "así",
    "alli": "allí",
    "aqui": "aquí",

    # Palabras esdrujulas y otras con tilde
    "capitulo": "capítulo",
    "titulo": "título",
    "tecnico": "técnico",
    "tecnicos": "técnicos",
    "metodologico": "metodológico",
    "metodologica": "metodológica",
    "estadistico": "estadístico",
    "estadistica": "estadística",
    "estadisticas": "estadísticas",
    "practico": "práctico",
    "practica": "práctica",
    "practicas": "prácticas",
    "academico": "académico",
    "academica": "académica",
    "teorico": "teórico",
    "teorica": "teórica",
    "teoricos": "teóricos",
    "especifico": "específico",
    "especifica": "específica",
    "especificos": "específicos",
    "especificas": "específicas",
    "critico": "crítico",
    "critica": "crítica",
    "criticos": "críticos",
    "criticas": "críticas",
    "cientifico": "científico",
    "cientifica": "científica",
    "cientificos": "científicos",
    "cientificas": "científicas",
    "analisis": "análisis",
    "maximo": "máximo",
    "maxima": "máxima",
    "minimo": "mínimo",
    "minima": "mínima",
    "ultimo": "último",
    "ultima": "última",
    "ultimos": "últimos",
    "codigo": "código",
    "codigos": "códigos",
    "genero": "género",
    "generos": "géneros",
    "metodo": "método",
    "metodos": "métodos",
    "numero": "número",
    "numeros": "números",
    "periodo": "período",
    "periodos": "períodos",
    "parametro": "parámetro",
    "parametros": "parámetros",
    "formula": "fórmula",
    "formulas": "fórmulas",
    "grafico": "gráfico",
    "grafica": "gráfica",
    "graficos": "gráficos",
    "graficas": "gráficas",
    "logico": "lógico",
    "logica": "lógica",
    "logicos": "lógicos",
    "logicas": "lógicas",
    "matematico": "matemático",
    "matematica": "matemática",
    "matematicos": "matemáticos",
    "matematicas": "matemáticas",
    "didactico": "didáctico",
    "didactica": "didáctica",
    "didacticos": "didácticos",
    "didacticas": "didácticas",
    "mecanico": "mecánico",
    "mecanica": "mecánica",
    "mecanicos": "mecánicos",
    "mecanicas": "mecánicas",
    "optimo": "óptimo",
    "optima": "óptima",
    "optimos": "óptimos",
    "optimas": "óptimas",
    "unico": "único",
    "unica": "única",
    "unicos": "únicos",
    "unicas": "únicas",
    "basico": "básico",
    "basica": "básica",
    "basicos": "básicos",
    "basicas": "básicas",
    "juridico": "jurídico",
    "juridica": "jurídica",
    "juridicos": "jurídicos",
    "juridicas": "jurídicas",
    "demografico": "demográfico",
    "demografica": "demográfica",
    "epigrafe": "epígrafe",
    "epigrafes": "epígrafes",
    "electronico": "electrónico",
    "electronica": "electrónica",
    "electronicos": "electrónicos",
    "electronicas": "electrónicas",
    "automatico": "automático",
    "automatica": "automática",
    "automaticos": "automáticos",
    "automaticas": "automáticas",
    "economico": "económico",
    "economica": "económica",
    "economicos": "económicos",
    "economicas": "económicas",
    "historico": "histórico",
    "historica": "histórica",
    "historicos": "históricos",
    "historicas": "históricas",
    "empirico": "empírico",
    "empirica": "empírica",
    "empiricos": "empíricos",
    "empiricas": "empíricas",
    "sintactico": "sintáctico",
    "sintactica": "sintáctica",
    "semantico": "semántico",
    "semantica": "semántica",
    "semanticos": "semánticos",
    "sistemico": "sistémico",
    "sistemica": "sistémica",
    "sistemicos": "sistémicos",
    "sistemicas": "sistémicas",
    "operativo": "operativo",  # no lleva tilde

    # Verbos en pasado (3a persona singular preterito)
    "implemento": "implementó",
    "desarrollo": "desarrolló",
    "utilizo": "utilizó",
    "analizo": "analizó",
    "determino": "determinó",
    "evaluo": "evaluó",
    "genero": "generó",
    "realizo": "realizó",
    "aplico": "aplicó",
    "identifico": "identificó",
    "presento": "presentó",
    "demostro": "demostró",
    "verifico": "verificó",
    "confirmo": "confirmó",
    "alcanzo": "alcanzó",
    "completo": "completó",
    "diseno": "diseñó",
    "integro": "integró",
    "modifico": "modificó",
    "observo": "observó",
    "proporciono": "proporcionó",
    "redujo": "redujo",  # no lleva tilde
    "construyo": "construyó",
    "establecio": "estableció",
    "permitio": "permitió",
    "propuso": "propuso",  # no lleva tilde
    "resulto": "resultó",
    "supuso": "supuso",  # no lleva tilde
    "tradujo": "tradujo",  # no lleva tilde
    "obtuvo": "obtuvo",  # no lleva tilde
    "mantuvo": "mantuvo",  # no lleva tilde
    "produjo": "produjo",  # no lleva tilde
    "introdujo": "introdujo",  # no lleva tilde

    # Otras palabras comunes
    "que": "qué",          # solo interrogativo/exclamativo → NO reemplazar automaticamente
    "como": "cómo",        # idem
    "cual": "cuál",        # idem
    "quien": "quién",      # idem
    "cuanto": "cuánto",    # idem
    "donde": "dónde",      # idem
    "cuando": "cuándo",    # idem

    "ingles": "inglés",
    "frances": "francés",
    "aleman": "alemán",
    "portugues": "portugués",
    "catalan": "catalán",
    "despues": "después",
    "traves": "través",
    "interes": "interés",
    "arbol": "árbol",
    "facil": "fácil",
    "dificil": "difícil",
    "util": "útil",
    "inutil": "inútil",
    "album": "álbum",
    "caracter": "carácter",
    "caracteres": "caracteres",  # no lleva tilde en plural
    "regimen": "régimen",
    "regimenes": "regímenes",
    "habil": "hábil",
    "debiles": "débiles",
    "debil": "débil",
    "esteril": "estéril",
    "fertil": "fértil",
    "mastil": "mástil",
    "portatil": "portátil",
    "textil": "textil",  # no lleva tilde
    "versatil": "versátil",
    "volatil": "volátil",
    "facilmente": "fácilmente",
    "dificilmente": "difícilmente",
    "utilmente": "útilmente",
    "agilmente": "ágilmente",
    "rapidamente": "rápidamente",
    "automaticamente": "automáticamente",
    "especificamente": "específicamente",
    "teoricamente": "teóricamente",
    "practicamente": "prácticamente",
    "estadisticamente": "estadísticamente",
    "historicamente": "históricamente",
    "empiricamente": "empíricamente",
    "sistematicamente": "sistemáticamente",
    "tecnicamente": "técnicamente",
    "economicamente": "económicamente",
    "metodologicamente": "metodológicamente",
    "criticamente": "críticamente",
    "cientificamente": "científicamente",
    "logicamente": "lógicamente",
    "unicamente": "únicamente",
    "maximamente": "máximamente",
    "minimamente": "mínimamente",
    "basicamente": "básicamente",
    "juridicamente": "jurídicamente",
    "electronica": "electrónica",  # ya esta pero por si acaso
    "exito": "éxito",
    "epoca": "época",
    "area": "área",
    "areas": "áreas",
    "linea": "línea",
    "lineas": "líneas",
    "dia": "día",
    "dias": "días",
    "rio": "río",
    "rios": "ríos",
    "pais": "país",
    "paises": "países",
    "raiz": "raíz",
    "raices": "raíces",
    "oido": "oído",
    "oidos": "oídos",
    "reir": "reír",
    "sonreir": "sonreír",
    "freir": "freír",
    "prohibir": "prohibir",  # no lleva tilde
    "prohibe": "prohíbe",
    "prohiben": "prohíben",
    "aereo": "aéreo",
    "aerea": "aérea",
    "aereos": "aéreos",
    "aereas": "aéreas",
    "petroleo": "petróleo",
    "oleo": "óleo",
    "oleos": "óleos",
    "heroe": "héroe",
    "heroes": "héroes",
    "marmol": "mármol",
    "angel": "ángel",
    "angeles": "ángeles",
    "lapiz": "lápiz",
    "lapices": "lápices",
    "carcel": "cárcel",
    "carceles": "cárceles",
    "dolar": "dólar",
    "dolares": "dólares",
    "arbol": "árbol",
    "arboles": "árboles",
    "automovil": "automóvil",
    "automoviles": "automóviles",
    "movil": "móvil",
    "moviles": "móviles",
    "esten": "estén",
    "estenograficos": "estenográficos",
    "ultimamente": "últimamente",
    "intrinseco": "intrínseco",
    "intrinseca": "intrínseca",
    "intrinsecos": "intrínsecos",
    "intrinsecas": "intrínsecas",
    "extrinseco": "extrínseco",
    "extrinseca": "extrínseca",
    "caustico": "cáustico",
    "caustica": "cáustica",

    # Terminaciones en -ia, -io (hiato)
    "tecnologia": "tecnología",
    "tecnologias": "tecnologías",
    "metodologia": "metodología",
    "metodologias": "metodologías",
    "biologia": "biología",
    "psicologia": "psicología",
    "sociologia": "sociología",
    "filosofia": "filosofía",
    "geografia": "geografía",
    "categoria": "categoría",
    "categorias": "categorías",
    "energia": "energía",
    "energias": "energías",
    "estrategia": "estrategia",  # no lleva tilde (ia no es hiato)
    "garantia": "garantía",
    "garantias": "garantías",
    "mayoria": "mayoría",
    "minoria": "minoría",
    "policia": "policía",
    "policias": "policías",
    "teoria": "teoría",
    "teorias": "teorías",
    "tutoria": "tutoría",
    "tutorias": "tutorías",
    "asesoria": "asesoría",
    "asesorias": "asesorías",
    "bibliografia": "bibliografía",
    "bibliografias": "bibliografías",
    "demografia": "demografía",
    "ortografia": "ortografía",
    "tipografia": "tipografía",
    "caligrafia": "caligrafía",
    "autonomia": "autonomía",
    "soberania": "soberanía",
    "alegoria": "alegoría",
    "anatomia": "anatomía",
    "armonia": "armonía",
    "melodia": "melodía",
    "sinfonia": "sinfonía",
    "cirugia": "cirugía",
    "magia": "magia",  # no lleva tilde (ia no es hiato)
    "regia": "regía",
    "tenia": "tenía",
    "venia": "venía",
    "habia": "había",
    "habian": "habían",
    "podria": "podría",
    "podrian": "podrían",
    "deberia": "debería",
    "deberian": "deberían",
    "tendria": "tendría",
    "tendrian": "tendrían",
    "vendria": "vendría",
    "vendrian": "vendrían",
    "seria": "sería",
    "serian": "serían",
    "estaria": "estarían",
    "habria": "habría",
    "habrian": "habrían",
    "haria": "haría",
    "harian": "harían",
    "diria": "diría",
    "dirian": "dirían",
    "querrria": "querría",
    "sabria": "sabría",
    "saldria": "saldría",
    "pondria": "pondría",
    "valdria": "valdría",
    "cabria": "cabría",
    "seguia": "seguía",
    "seguian": "seguían",
    "conocia": "conocía",
    "conocian": "conocían",
    "podia": "podía",
    "podian": "podían",
    "queria": "quería",
    "querian": "querían",
    "hacia": "hacía",
    "hacian": "hacían",
    "decia": "decía",
    "decian": "decían",
    "pedia": "pedía",
    "pedian": "pedían",
    "sentia": "sentía",
    "sentian": "sentían",
    "solia": "solía",
    "solian": "solían",
    "veia": "veía",
    "veian": "veían",
    "traia": "traía",
    "traian": "traían",
    "caia": "caía",
    "caian": "caían",
    "oia": "oía",
    "oian": "oían",
    "reia": "reía",
    "reian": "reían",
    "creia": "creía",
    "creian": "creían",
    "leia": "leía",
    "leian": "leían",

    # Palabras con Ñ
    "senal": "señal",
    "senalado": "señalado",
    "senalados": "señalados",
    "senalada": "señalada",
    "senaladas": "señaladas",
    "ensena": "enseña",
    "ensenan": "enseñan",
    "ensenanza": "enseñanza",
    "desempeno": "desempeño",
    "desempenos": "desempeños",
    "desempena": "desempeña",
    "desempenan": "desempeñan",
    "tamano": "tamaño",
    "tamanos": "tamaños",
    "compania": "compañía",
    "companias": "compañías",
    "pequeno": "pequeño",
    "pequena": "pequeña",
    "pequenos": "pequeños",
    "pequenas": "pequeñas",
    "extrano": "extraño",
    "extrana": "extraña",
    "extranos": "extraños",
    "extranas": "extrañas",
    "sueno": "sueño",
    "suenos": "sueños",

    # Mas palabras
    "aun": "aún",  # ambiguo: "aun" (incluso) vs "aún" (todavia). Dejamos para revision manual.
    "solo": "sólo",  # ambiguo: "solo" (alone) vs "sólo" (solamente). RAE 2010 ya no exige tilde.
    "este": "éste",  # pronombres demostrativos — RAE ya no exige tilde
    "esta": "ésta",
    "estos": "éstos",
    "estas": "éstas",
    "ese": "ése",
    "esa": "ésa",
    "esos": "ésos",
    "esas": "ésas",
    "aquel": "aquél",
    "aquella": "aquélla",
    "aquellos": "aquéllos",
    "aquellas": "aquéllas",
}

# Palabras ambiguas que NO deben acentuarse automaticamente
# (se marcan con TODO en lugar de cambiarlas)
AMBIGUAS = {
    "aun": "aún",    # "aun" (incluso) vs "aún" (todavia)
    "solo": "sólo",  # RAE2010 permite sin tilde
    "este": None,    # demostrativos — RAE2010 permite sin tilde
    "esta": None,
    "estos": None,
    "estas": None,
    "ese": None,
    "esa": None,
    "esos": None,
    "esas": None,
    "aquel": None,
    "que": None,     # interrogativos
    "como": None,
    "cual": None,
    "cuales": None,
    "quien": None,
    "quienes": None,
    "cuanto": None,
    "cuanta": None,
    "cuantos": None,
    "cuantas": None,
    "donde": None,
    "cuando": None,
}

# No incluir AMBIGUAS en DICCIONARIO para reemplazo automatico
for amb in AMBIGUAS:
    DICCIONARIO.pop(amb, None)


# --- FUNCIONES DE PROCESAMIENTO ---

def procesar_archivo(filepath: Path, dry_run: bool = False):
    """Procesa un archivo .tex, acentuando el texto espanol."""
    with open(filepath, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    cambios = 0
    en_verbatim = False
    en_lstlisting = False

    for i, linea in enumerate(lineas):
        # Detectar entornos verbatim y listings
        if "\\begin{verbatim}" in linea or "\\begin{lstlisting}" in linea:
            en_verbatim = True
        if "\\end{verbatim}" in linea or "\\end{lstlisting}" in linea:
            en_verbatim = False
            nuevas_lineas.append(linea)
            continue

        if en_verbatim:
            nuevas_lineas.append(linea)
            continue

        # Detectar comentarios (solo la parte comentada)
        if linea.strip().startswith("%"):
            # Procesar comentarios tambien
            nueva = _acentuar_texto(linea)
            if nueva != linea:
                cambios += 1
            nuevas_lineas.append(nueva)
            continue

        # Separar comandos LaTeX del texto
        nueva = _procesar_linea_latex(linea)
        if nueva != linea:
            cambios += 1
        nuevas_lineas.append(nueva)

    if cambios > 0 and not dry_run:
        # Backup
        backup = filepath.with_suffix(".tex.bak")
        shutil.copy2(filepath, backup)
        # Escribir
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(nuevas_lineas)
        print(f"  {filepath.name}: {cambios} cambios aplicados (backup en .bak)")
    elif cambios > 0 and dry_run:
        print(f"  {filepath.name}: {cambios} cambios DETECTADOS (dry-run, no modificado)")
    else:
        print(f"  {filepath.name}: sin cambios")

    return cambios


def _procesar_linea_latex(linea: str) -> str:
    """
    Procesa una linea LaTeX: protege comandos y argumentos, acentua el resto.
    Estrategia: dividir la linea en segmentos LaTeX y segmentos texto.
    """
    # Patron: comandos LaTeX
    # \comando{arg1}{arg2} o \comando[opcional]{arg1}
    # o \comando o \begin{algo} o \end{algo}
    partes = []
    pos = 0

    while pos < len(linea):
        # Buscar inicio de comando
        cmd_match = re.search(r'(\\[a-zA-Z@]+)', linea[pos:])
        if cmd_match:
            cmd_start = pos + cmd_match.start()
            cmd_name = cmd_match.group(1)

            # Agregar texto antes del comando
            if cmd_start > pos:
                texto = linea[pos:cmd_start]
                partes.append(_acentuar_texto(texto))

            pos = cmd_start
            # Procesar el comando y sus argumentos
            segmento_latex, nueva_pos = _extraer_comando_latex(linea, pos)
            partes.append(segmento_latex)
            pos = nueva_pos
        else:
            # No hay mas comandos, acentuar el resto
            texto = linea[pos:]
            partes.append(_acentuar_texto(texto))
            break

    return "".join(partes)


def _extraer_comando_latex(linea: str, pos: int) -> tuple:
    """Extrae un comando LaTeX completo con sus argumentos, desde pos."""
    inicio = pos
    # Nombre del comando
    cmd_match = re.match(r'(\\[a-zA-Z@]+)', linea[pos:])
    if not cmd_match:
        return linea[pos:], len(linea)

    pos += len(cmd_match.group(1))

    # Buscar argumentos opcionales: [texto]
    while pos < len(linea) and linea[pos:].lstrip().startswith("["):
        pos += len(linea[pos:]) - len(linea[pos:].lstrip()) + 1  # saltear espacio y [
        depth = 1
        while pos < len(linea) and depth > 0:
            if linea[pos] == "[":
                depth += 1
            elif linea[pos] == "]":
                depth -= 1
            pos += 1

    # Buscar argumentos obligatorios: {texto}
    while pos < len(linea) and linea[pos:].lstrip().startswith("{"):
        pos += len(linea[pos:]) - len(linea[pos:].lstrip()) + 1
        depth = 1
        while pos < len(linea) and depth > 0:
            if linea[pos] == "{":
                depth += 1
            elif linea[pos] == "}":
                depth -= 1
            pos += 1

    # Incluir espacio en blanco despues del comando (si lo hay)
    if pos < len(linea) and linea[pos] in (" ", "\t"):
        pos += 1

    return linea[inicio:pos], pos


def _acentuar_texto(texto: str) -> str:
    """Aplica el diccionario de acentuacion a un fragmento de texto puro."""
    resultado = texto

    # Reemplazar palabras completas del diccionario
    # Usamos \b para limites de palabra
    for sin_tilde, con_tilde in sorted(DICCIONARIO.items(), key=lambda x: -len(x[0])):
        patron = r'\b' + re.escape(sin_tilde) + r'\b'
        resultado = re.sub(patron, con_tilde, resultado)

    return resultado


# --- MAIN ---

def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    if dry_run:
        print("ACENTUADOR DE TESIS — MODO DRY-RUN (sin modificar archivos)")
    else:
        print("ACENTUADOR DE TESIS")
    print("=" * 60)

    archivos_tex = sorted(SECTIONS_DIR.glob("*.tex"))
    total_cambios = 0

    for fp in archivos_tex:
        cambios = procesar_archivo(fp, dry_run=dry_run)
        total_cambios += cambios

    print("=" * 60)
    print(f"Total: {total_cambios} cambios en {len(archivos_tex)} archivos")
    if dry_run:
        print("Ejecuta sin --dry-run para aplicar los cambios.")
    else:
        print("Backups guardados como .tex.bak en cada archivo.")
        print("Recompila con: cd paper && xelatex main && biber main && xelatex main && xelatex main")


if __name__ == "__main__":
    main()
