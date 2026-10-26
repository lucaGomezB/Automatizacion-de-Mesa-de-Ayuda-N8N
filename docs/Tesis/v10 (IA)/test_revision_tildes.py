"""Pruebas de `revision_tildes.py` (change c-137, revision ortotipografica).

Se ejecutan con:

    python -m pytest "docs/Tesis/v10 (IA)/test_revision_tildes.py" -q

Las fixtures LaTeX son cadenas en linea; las oraciones de la linea base
(seccion "Deteccion completa de la linea base") se copian verbatim de la
version v1.1.1 de la tesis.
"""

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import revision_tildes as rt  # noqa: E402

CABECERA = "archivo\tlinea\tcolumna\ttoken\tsugerencia\tclase\tzona\tcontexto"


def _hash(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# 1.1 Ejecucion por defecto sin efectos
# ---------------------------------------------------------------------------


def test_ejecucion_por_defecto_emite_cabecera_y_no_modifica_archivos(tmp_path, capsys):
    ruta = tmp_path / "a.tex"
    ruta.write_bytes("Texto sin novedades.\r\nOtra linea.\r\n".encode("utf-8"))
    antes = _hash(ruta)

    codigo = rt.main(["--archivos", str(ruta)])

    salida = capsys.readouterr().out
    assert codigo == 0
    assert salida.splitlines()[0] == CABECERA
    assert _hash(ruta) == antes


def test_ejecucion_por_defecto_no_crea_archivos_nuevos(tmp_path, capsys):
    ruta = tmp_path / "b.tex"
    ruta.write_bytes(b"Hola mundo\n")

    rt.main(["--archivos", str(ruta)])

    capsys.readouterr()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["b.tex"]


def inv(texto, **kw):
    """Atajo: inventario de un fragmento en memoria."""
    return rt.inventariar_texto(texto, **kw)


def tokens(texto, **kw):
    return [c.token for c in inv(texto, **kw)]


# ---------------------------------------------------------------------------
# 1.2 Zonas protegidas (decision D3)
# ---------------------------------------------------------------------------

# Cada fragmento oculta la palabra-sonda "erronea" dentro de una zona protegida.
FRAGMENTOS_PROTEGIDOS = [
    pytest.param(r"\texttt{erronea}", id="texttt"),
    pytest.param(r"\url{https://example.org/erronea}", id="url"),
    pytest.param(r"\href{https://example.org/erronea}{ver el sitio}", id="href-destino"),
    pytest.param(r"\path{erronea/ruta}", id="path"),
    pytest.param(r"\label{sec:erronea}", id="label"),
    pytest.param(r"\ref{erronea}", id="ref"),
    pytest.param(r"\autoref{erronea}", id="autoref"),
    pytest.param(r"\cref{erronea}", id="cref"),
    pytest.param(r"\eqref{erronea}", id="eqref"),
    pytest.param(r"\pageref{erronea}", id="pageref"),
    pytest.param(r"\parencite{erronea}", id="parencite"),
    pytest.param(r"\textcite[p.~3]{erronea}", id="textcite-opcional"),
    pytest.param(r"\cite{a,erronea}", id="cite-lista"),
    pytest.param(r"\input{erronea}", id="input"),
    pytest.param(r"\includegraphics[width=3cm]{erronea.png}", id="includegraphics"),
    pytest.param("\\begin{lstlisting}\nerronea = 1\n\\end{lstlisting}", id="lstlisting"),
    pytest.param("\\begin{verbatim}\nerronea\n\\end{verbatim}", id="verbatim"),
    pytest.param("\\begin{minted}{python}\nerronea\n\\end{minted}", id="minted"),
    pytest.param(r"\verb|erronea|", id="verb"),
    pytest.param(r"\lstinline|erronea|", id="lstinline"),
    pytest.param(r"\(erronea + 1\)", id="matematica-parentesis"),
    pytest.param("$erronea$", id="matematica-dolar"),
    pytest.param(r"\[ erronea \]", id="matematica-corchetes"),
    pytest.param("\\begin{equation}\nerronea\n\\end{equation}", id="matematica-entorno"),
    pytest.param("% erronea en un comentario", id="comentario"),
    pytest.param(r"\erronea", id="nombre-de-comando"),
    pytest.param(r"\begin{erronea}", id="nombre-de-entorno"),
    pytest.param(r"\begin{tabular}{erronea}", id="especificacion-de-tabular"),
    pytest.param("ruta/erronea/archivo.tex", id="ruta-de-repositorio"),
    pytest.param(r"nombre\_erronea", id="identificador-con-guion-bajo"),
]


@pytest.mark.parametrize("fragmento", FRAGMENTOS_PROTEGIDOS)
def test_zona_protegida_no_informa_candidatos_pero_la_prosa_contigua_si(fragmento):
    texto = f"Antes {fragmento}\n\nLuego la derivación erronea persiste."

    candidatos = inv(texto)

    assert [c.token for c in candidatos] == ["erronea"]
    assert candidatos[0].inicio == texto.rindex("erronea")
    assert candidatos[0].zona == "prosa"


def test_cinco_cadenas_canonicas_no_reciben_sugerencia():
    texto = (
        "Sectores: Seguridad Informatica, Soporte Tecnico Hardware, "
        "Soporte Tecnico Software, Bases de Datos y Sistemas. "
        "Pero la derivación erronea y la tecnica informatica si."
    )

    assert tokens(texto) == ["erronea", "tecnica", "informatica"]


def test_cadena_canonica_con_tilde_no_se_toca_ni_se_cuenta_como_candidato():
    # Las cadenas canonicas son exactas (sin tildes): la variante acentuada
    # es prosa legitima y no genera ningun candidato.
    assert inv("Seguridad Informática y Soporte Técnico Hardware.") == []


def test_abstract_en_ingles_se_protege_hasta_el_final_del_archivo():
    texto = "Resumen erronea.\n\\section*{Abstract}\nversion erronea\n\nOtro parrafo erronea\n"

    assert [c.inicio for c in inv(texto)] == [texto.index("erronea")]


def test_cadenas_canonicas_dentro_de_otras_palabras_no_se_enmascaran():
    # "Sistemas" solo es canonica como palabra completa.
    assert tokens("Los Metasistemas erronea y Sistemas") == ["erronea"]


def test_href_solo_protege_el_destino_el_texto_visible_es_prosa():
    assert tokens(r"\href{https://example.org}{la derivación erronea}") == ["erronea"]


def test_texttt_con_llaves_anidadas_se_protege_completo():
    assert tokens(r"\texttt{\{\"erronea\": 1\} erronea} y erronea") == ["erronea"]


def test_porcentaje_escapado_no_inicia_un_comentario():
    assert tokens(r"Un 95~\% de derivación erronea.") == ["erronea"]


def test_salto_de_fila_con_opcion_no_se_confunde_con_matematica():
    texto = "a & b \\\\[2pt]\nsegunda erronea \\\\\n"

    assert tokens(texto) == ["erronea"]


def test_dolar_escapado_no_abre_matematica():
    assert tokens(r"Cuesta 5 \$ y la derivación erronea \$ final.") == ["erronea"]


def test_palabra_con_escape_latex_de_acento_se_considera_acentuada():
    assert tokens("Documentaci{\\'o}n erronea y informaci\\'on") == ["erronea"]


def test_lstinline_con_llaves_y_entorno_matematico_con_asterisco_se_protegen():
    texto = "\\lstinline{erronea} \\begin{align*} erronea \\end{align*} erronea"

    assert [c.inicio for c in inv(texto)] == [texto.rindex("erronea")]


def test_nombres_de_archivo_en_prosa_se_protegen():
    assert tokens("Ver README.md y config.yaml con erronea") == ["erronea"]


# ---------------------------------------------------------------------------
# 1.3 Zonas tabla y cita (solo reporte) y prosa en argumentos de comandos
# ---------------------------------------------------------------------------


def test_candidato_en_celda_de_tabular_se_informa_con_zona_tabla():
    texto = (
        "\\begin{tabular}{ll}\n"
        "Campo & Valor \\\\\n"
        "derivación erronea & dato \\\\\n"
        "\\end{tabular}\n"
    )

    candidatos = inv(texto)

    assert [(c.token, c.zona) for c in candidatos] == [("erronea", "tabla")]


def test_candidato_en_longtable_y_tabularx_tambien_es_tabla():
    for entorno in ("longtable", "tabularx"):
        texto = f"\\begin{{{entorno}}}{{ll}}\nuna erronea\n\\end{{{entorno}}}\n"

        assert [c.zona for c in inv(texto)] == ["tabla"], entorno


def test_la_prosa_alrededor_de_la_tabla_sigue_siendo_prosa():
    texto = (
        "Antes erronea.\n\\begin{tabular}{l}\ncelda erronea\n\\end{tabular}\nLuego erronea.\n"
    )

    assert [c.zona for c in inv(texto)] == ["prosa", "tabla", "prosa"]


def test_candidato_entre_comillas_latex_se_informa_con_zona_cita():
    texto = "El operador escribio ``la derivación erronea del ticket'' sin más."

    assert [(c.token, c.zona) for c in inv(texto)] == [("erronea", "cita")]


def test_candidato_entre_comillas_rectas_se_informa_con_zona_cita():
    texto = 'Dice "otra derivación erronea" y luego una erronea fuera.'

    assert [c.zona for c in inv(texto)] == ["cita", "prosa"]


def test_comilla_sin_cierre_en_el_parrafo_no_convierte_el_resto_en_cita():
    texto = 'Una comilla " suelta.\n\nOtro parrafo con erronea.'

    assert [c.zona for c in inv(texto)] == ["prosa"]


def test_caption_se_trata_como_prosa():
    texto = "\\caption{Distribución erronea de casos}"

    assert [(c.token, c.zona) for c in inv(texto)] == [("erronea", "prosa")]


@pytest.mark.parametrize(
    "comando",
    ["section", "subsection", "caption", "textbf", "emph", "footnote", "item"],
)
def test_argumentos_de_comandos_portadores_de_texto_son_prosa(comando):
    if comando == "item":
        texto = "\\item una derivación erronea"
    else:
        texto = f"\\{comando}{{una derivación erronea}}"

    assert [(c.token, c.zona) for c in inv(texto)] == [("erronea", "prosa")]


def test_entorno_tabular_comentado_no_cambia_la_zona_de_la_prosa_siguiente():
    texto = "% \\begin{tabular}{l}\nuna erronea\n% \\end{tabular}\n"

    assert [c.zona for c in inv(texto)] == ["prosa"]


def test_tabla_con_cadena_canonica_protege_la_cadena_pero_informa_el_resto():
    texto = (
        "\\begin{tabular}{ll}\nSeguridad Informatica & erronea \\\\\n\\end{tabular}\n"
    )

    assert [(c.token, c.zona) for c in inv(texto)] == [("erronea", "tabla")]


# ---------------------------------------------------------------------------
# 1.4 Lexico y clasificacion (decision D2)
# ---------------------------------------------------------------------------


def clasif(texto, **kw):
    """(token, sugerencia, clase) de cada candidato en prosa."""
    return [(c.token, c.sugerencia, c.clase) for c in inv(texto, **kw)]


@pytest.mark.parametrize(
    "texto, token, sugerencia",
    [
        ("derivación erronea", "erronea", "errónea"),
        ("derivaciónes erroneas", "erroneas", "erróneas"),
        ("tareas heterogeneas", "heterogeneas", "heterogéneas"),
        ("multiples canales", "multiples", "múltiples"),
        ("más alla del caso", "alla", "allá"),
        ("tres años de antiguedad", "antiguedad", "antigüedad"),
        ("dentro del perimetro organizacional", "perimetro", "perímetro"),
        ("marcadores inequivocos", "inequivocos", "inequívocos"),
        ("resulte enganosa", "enganosa", "engañosa"),
        ("la digitalización, el escaner o la impresora", "escaner", "escáner"),
        ("el Capitulo anterior", "Capitulo", "Capítulo"),
        ("tambien lo hace", "tambien", "también"),
    ],
)
def test_forma_sin_tilde_que_no_es_palabra_valida_es_inequivoca(texto, token, sugerencia):
    assert clasif(texto) == [(token, sugerencia, "INEQUIVOCO")]


@pytest.mark.parametrize(
    "texto, token, sugerencia",
    [
        ("la clasificacion automatica", "clasificacion", "clasificación"),
        ("una decision tardia", "decision", "decisión"),
        ("Introduccion general", "Introduccion", "Introducción"),
        ("la conversion de datos", "conversion", "conversión"),
    ],
)
def test_singular_en_cion_sion_sin_tilde_es_inequivoco(texto, token, sugerencia):
    assert (token, sugerencia, "INEQUIVOCO") in clasif(texto)


def test_plurales_y_formas_acentuadas_en_cion_sion_no_se_informan():
    texto = "las clasificaciones, la decisión, las versiones, la sesión y la expression"

    assert clasif(texto) == []


def test_regla_cion_sion_se_desactiva_en_emph_y_textit():
    texto = r"el \emph{prompt injection} y \textit{version} y la version"

    assert [c.token for c in inv(texto)] == ["version"]
    assert inv(texto)[0].inicio == texto.rindex("version")


def test_el_lexico_sigue_activo_dentro_de_emph():
    assert tokens(r"una \emph{derivación erronea}") == ["erronea"]


@pytest.mark.parametrize(
    "texto, token, sugerencia",
    [
        ("éste es el caso", "éste", "este"),
        ("aquéllas organizaciones", "aquéllas", "aquellas"),
        ("aquél y ésa", "aquél", "aquel"),
        ("el caso sólo aplica", "sólo", "solo"),
    ],
)
def test_demostrativos_y_solo_con_tilde_son_inequivocos(texto, token, sugerencia):
    assert (token, sugerencia, "INEQUIVOCO") in clasif(texto)


@pytest.mark.parametrize(
    "texto, token, sugerencia",
    [
        ("sesgos hacía una clase", "hacía", "hacia"),
        ("la forma en que se fórmula la instrucción", "fórmula", "formula"),
    ],
)
def test_tildes_improcedentes_de_homografos_son_ambiguas(texto, token, sugerencia):
    assert clasif(texto) == [(token, sugerencia, "AMBIGUO")]


def test_las_sugerencias_conservan_inicial_mayuscula_y_mayusculas_sostenidas():
    assert clasif("Erronea y ERRONEA y erronea") == [
        ("Erronea", "Errónea", "INEQUIVOCO"),
        ("ERRONEA", "ERRÓNEA", "INEQUIVOCO"),
        ("erronea", "errónea", "INEQUIVOCO"),
    ]


def test_siglas_cortas_en_mayusculas_no_se_interpretan_como_palabras():
    assert clasif("El SLA y la API de SI y MAS") == []


def test_autoconsistencia_del_corpus_marca_como_ambiguo_lo_que_el_lexico_no_cubre():
    texto = "El huesped inicial y otro huésped final."

    assert clasif(texto) == [("huesped", "huésped", "AMBIGUO")]


def test_autoconsistencia_no_marca_una_palabra_que_solo_aparece_sin_tilde():
    assert clasif("El huesped inicial y otro huesped final.") == []


def test_lexico_sin_correcciones_incondicionales_de_homografos():
    prohibidas = {
        "hacia", "formula", "continua", "esta", "este", "aquellas", "aquellos",
        "desarrollo", "completo", "registro", "valida", "publica",
        "practica", "critica", "fijo", "asigno", "gestiono", "aun", "mas",
    }

    assert prohibidas.isdisjoint(rt.LEXICO_INEQUIVOCO)


def test_cada_entrada_del_lexico_es_la_forma_acentuada_de_su_clave():
    import unicodedata

    def sin_marcas(palabra):
        return "".join(
            c for c in unicodedata.normalize("NFD", palabra) if not unicodedata.combining(c)
        )

    for clave, valor in rt.LEXICO_INEQUIVOCO.items():
        assert clave == clave.lower()
        assert sin_marcas(valor) == clave, (clave, valor)
        assert valor != clave, clave


def test_palabras_correctamente_acentuadas_no_generan_candidatos():
    texto = "La clasificación automática es errónea, según la información de múltiples años."

    assert inv(texto) == []


# ---------------------------------------------------------------------------
# 1.5 Senales de contexto para pares frecuentes y opcion --todos (decision D2)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texto, token, sugerencia",
    [
        ("la forma en que se fórmula la instrucción", "fórmula", "formula"),
        ("el flujo continua automáticamente", "continua", "continúa"),
        ("el indicador esta activo", "esta", "está"),
        ("cuando no lo esta, el flujo sigue", "esta", "está"),
        ("verifica que la descripción no este vacía", "este", "esté"),
        ("como la grabación esta acotada a 45 s", "esta", "está"),
        ("La distribución de roles asigno la coordinación", "asigno", "asignó"),
        ("El tablero Kanban se gestiono mediante GitHub", "gestiono", "gestionó"),
        ("el servicio esta en línea", "esta", "está"),
        ("la presencia simultanea de las palabras", "simultanea", "simultánea"),
        ("una página publica", "publica", "pública"),
        ("el módulo valida que el texto sea JSON", "valida", "válida"),
        ("una revisión critica", "critica", "crítica"),
        ("la estrategia de pruebas se sustento en la pirámide", "sustento", "sustentó"),
        ("el caso se registro en el sistema", "registro", "registró"),
        ("el modelo se desarrollo en Python", "desarrollo", "desarrolló"),
        ("lo hacia con cuidado", "hacia", "hacía"),
        ("se hacia referencia al anexo", "hacia", "hacía"),
        ("el ahorro se promedio sobre el trimestre", "promedio", "promedió"),
        ("sesgos hacía una clase mayoritaria", "hacía", "hacia"),
        ("aun descontando 10 s por caso", "aun", "aún"),
        ("lo hizo mas rápido", "mas", "más"),
        ("no configura por si mismo una base", "si", "sí"),
        ("lo hace por sí mismo y de si, sin ayuda", "si", "sí"),
    ],
)
def test_pares_ambiguos_se_informan_con_senal_de_contexto(texto, token, sugerencia):
    assert (token, sugerencia, "AMBIGUO") in clasif(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "mejora continua",
        "la mejora continua del clasificador",
        "integración continua",
        "la gestión continua del flujo de trabajo",
        "bajo supervisión académica continua del director",
        "Cuantitativa continua & Segundos",
        "mediante la fórmula clásica",
        "una fórmula simple y de fórmula única",
        "el registro manual de incidentes",
        "derivación de incidentes hacia los sectores",
        "esta investigación se orienta a responder",
        "de esta manera y en este caso",
        "Esta lectura se limita a este dominio",
        "con este resultado y este estado",
        "devuelve esta salida y esta lista",
        "el desarrollo del módulo y el promedio de casos",
        "se formula la instrucción y se valida con pruebas",
        "no se publica un desglose",
        "tal como se indica y como lo pide el usuario",
        "el valor que se mide cuando llega el caso",
        "si el valor supera el umbral, entonces",
        "por si acaso llega otro",
    ],
)
def test_usos_legitimos_no_se_informan(texto):
    assert clasif(texto) == []


def test_interrogativos_solo_se_informan_en_contexto_interrogativo():
    texto = "?`cual es la magnitud del efecto y como se distribuyen los errores?"

    assert clasif(texto) == [
        ("cual", "cuál", "AMBIGUO"),
        ("como", "cómo", "AMBIGUO"),
    ]


def test_interrogativo_tras_preposicion_dentro_de_pregunta():
    assert clasif("?`Por que falla el sistema?") == [("que", "qué", "AMBIGUO")]


def test_relativo_dentro_de_pregunta_no_se_informa():
    texto = "?`reduce la automatización el tiempo que se mide en cada caso?"

    assert clasif(texto) == []


def test_interrogativo_indirecto_tras_verbo_de_conocimiento():
    texto = "El estudio determina cuanto tarda y explica como se mide, pero no sabe donde."

    assert clasif(texto) == [
        ("cuanto", "cuánto", "AMBIGUO"),
        ("como", "cómo", "AMBIGUO"),
        ("donde", "dónde", "AMBIGUO"),
    ]


def test_conjuncion_que_tras_verbo_de_comunicacion_no_se_informa():
    assert clasif("El informe indica que el valor es mayor y explica que falla.") == []


def test_interrogativos_con_signos_de_apertura_unicode():
    assert [c.sugerencia for c in inv("¿Quien lo hizo?")] == ["Quién"]


def test_opcion_todos_informa_todas_las_ocurrencias_de_los_pares():
    texto = (
        "esta investigación, la fórmula, mejora continua, derivación hacia los sectores, "
        "el que como si el registro."
    )

    sin_todos = clasif(texto)
    con_todos = {(c.token, c.sugerencia) for c in inv(texto, todos=True)}

    assert sin_todos == []
    assert con_todos == {
        ("esta", "está"),
        ("fórmula", "formula"),
        ("continua", "continúa"),
        ("hacia", "hacía"),
        ("que", "qué"),
        ("como", "cómo"),
        ("si", "sí"),
        ("registro", "registró"),
    }


def test_las_formas_de_los_pares_no_se_proponen_por_autoconsistencia():
    texto = "está aquí, esté allí, cómo sí, qué cuál. Esta casa, este valor, como si."

    assert clasif(texto) == []


# ---------------------------------------------------------------------------
# 1.6 Regresion de la linea base v1.1.1 (oraciones verbatim de la tesis)
# ---------------------------------------------------------------------------

I, A = "INEQUIVOCO", "AMBIGUO"

# (oracion verbatim de v1.1.1, token, sugerencia, clase). 40 erratas en total.
ERRATAS_LINEA_BASE = [
    # "hacia" escrito "hacía" (4)
    (r"confusiones sistemáticas entre dos categorías particulares, sesgos hacía una clase mayoritaria o aciertos preferenciales sobre una clase específica.", "hacía", "hacia", A),
    (r"lo que abre una vía concreta hacía un sistema completamente autoalojado.", "hacía", "hacia", A),
    (r"se concentra en la clasificación y derivación de incidentes hacía los sectores responsables, pero no aborda la resolución de aquellos casos.", "hacía", "hacia", A),
    (r"Dado que el sistema realiza transferencia de fragmentos textuales hacía infraestructura de inferencia operada por proveedores con sede en los Estados Unidos.", "hacía", "hacia", A),
    # "fórmula" verbal (1)
    (r"La forma en que se fórmula la instrucción condiciona el resultado tanto como la capacidad del modelo.", "fórmula", "formula", A),
    # "continua" verbal (4)
    (r"el proceso de registro inicial de incidentes continua realizándose manualmente, lo que introduce demoras.", "continua", "continúa", A),
    (r"cuando no lo esta, el flujo continua automáticamente con las confirmaciones al usuario.", "continua", "continúa", A),
    (r"A partir de ese punto, el flujo continua de manera idéntica a la de los canales escritos.", "continua", "continúa", A),
    (r"etapa en la cual el juicio experto continua siendo insustituible.", "continua", "continúa", A),
    # "esta"/"este" verbales (4)
    (r"Cuando el indicador esta activo ---es decir, cuando la confianza del clasificador fue inferior al umbral de 0,70--- el flujo notifica al operador.", "esta", "está", A),
    (r"el flujo notifica al operador; cuando no lo esta, el flujo sigue.", "esta", "está", A),
    (r"verifica que la descripción no este vacía y respete la longitud mínima y máxima aceptada por el backend", "este", "esté", A),
    (r"como la grabación esta acotada a un máximo de 45~s (véase la \autoref{subsec:metricas-instrumentos}), su valor constituye una cota inferior", "esta", "está", A),
    # formas inequivocas de la muestra (16)
    (r"la interpretación de descripciones textuales heterogeneas, la clasificación del problema según el área responsable", "heterogeneas", "heterogéneas", I),
    (r"o cuando el personal debe alternar entre tareas operativas heterogeneas, situación que coincide con la observada", "heterogeneas", "heterogéneas", I),
    (r"una tasa de derivación erronea inicial cercana al 15~\%.", "erronea", "errónea", I),
    (r"Segundo, el costo organizacional de una derivación erronea se estima en el orden de 10 a 15 minutos adicionales de reasignación", "erronea", "errónea", I),
    (r"genera derivaciones erroneas en un sector específico y puede erosionar la confianza de ese equipo", "erroneas", "erróneas", I),
    (r"con más de tres años de antiguedad en la mesa de ayuda, ambos capacitados previamente", "antiguedad", "antigüedad", I),
    (r"los empleados con mayor antiguedad tienden a resistir los cambios de procedimiento", "antiguedad", "antigüedad", I),
    (r"exige mantener la información dentro del perimetro organizacional.", "perimetro", "perímetro", I),
    (r"manteniendo los flujos de procesamiento y los datos dentro del perimetro organizacional.", "perimetro", "perímetro", I),
    (r"presenta marcadores léxicos inequivocos que no requieren consulta al modelo de lenguaje.", "inequivocos", "inequívocos", I),
    (r"aquellos incidentes que contienen marcadores inequivocos.", "inequivocos", "inequívocos", I),
    (r"la exactitud global puede resultar enganosa y recomiendan reportar valores macro promediados", "enganosa", "engañosa", I),
    (r"Por ejemplo, la presencia simultanea de las palabras \texttt{impresora}, \texttt{papel} y \texttt{atasco} sugiere con alta certeza", "simultanea", "simultánea", A),
    (r"particularmente Slack y Microsoft Teams en aquéllas organizaciones donde estas plataformas constituyen el canal", "aquéllas", "aquellas", I),
    (r"La distribución de roles asigno la coordinación general y la integración de componentes a Luca Gomez", "asigno", "asignó", A),
    (r"El tablero Kanban se gestiono mediante GitHub Projects, con seguimiento diario del estado de las tareas", "gestiono", "gestionó", A),
    # hallazgos fuera de la muestra del dictamen (11)
    (r"agrava la situación al obligar al personal a monitorear multiples fuentes simultáneamente.", "multiples", "múltiples", I),
    (r"donde el personal combina multiples roles (véase \autoref{subsec:gestion-servicios-ti}).", "multiples", "múltiples", I),
    (r"la integración de multiples canales de entrada dentro de un único flujo automatizado mejora la accesibilidad", "multiples", "múltiples", I),
    (r"y soporte específico para canales multiples incluyendo telefonía con transcripción automática.", "multiples", "múltiples", I),
    (r"fue diseñada para admitir multiples registros de clasificación por incidente", "multiples", "múltiples", I),
    (r"permite la arquitectura propuesta integrar canales multiples de recepción sin degradar la latencia", "multiples", "múltiples", I),
    (r"Más alla del cumplimiento de los objetivos específicos, los resultados permiten formular una conclusión acotada.", "alla", "allá", I),
    (r"El trabajo aporta tres contribuciones que se sostienen más alla del caso particular.", "alla", "allá", I),
    (r"Más alla del monitoreo operativo, los datos acumulados de incidentes constituyen una fuente de inteligencia organizacional", "alla", "allá", I),
    (r"la digitalización, el escaner o la impresora se orientan a Soporte Tecnico Hardware; el servidor, la red, SMTP o una VM se orientan a Sistemas", "escaner", "escáner", I),
    (r"no configura por si mismo una de las bases de transferencia que la ley admite.", "si", "sí", A),
]

# Usos legitimos de la linea base: ni siquiera se informan.
USOS_LEGITIMOS_SIN_REPORTE = [
    (r"el tercero es la mejora continua del proceso, que en el sistema propuesto se habilita", "continua"),
    (r"Tiempo de registro & Cuantitativa continua & Segundos (s) & Lapso entre la recepción", "continua"),
    (r"combinando la planificación por iteraciones con la gestión continua del flujo de trabajo característica del método Kanban", "continua"),
    (r"bajo supervisión académica continua del director del trabajo, Prof. Alberto Cortez.", "continua"),
    (r"cuyo reporte se genera en cada ejecución del pipeline de integración continua; la cifra exacta queda sujeta", "continua"),
    (r"queda sujeta al reporte vigente en cada ejecución del pipeline de integración continua.", "continua"),
    (r"La integración continua (CI) se ejecuta automáticamente en cada solicitud de incorporación", "continua"),
    (r"o a actividades de mejora continua. La magnitud de esta liberación", "continua"),
    (r"habilita dos procesos de mejora continua. Por un lado, permite identificar", "continua"),
    (r"y acelera la mejora continua del clasificador con un costo operativo controlado.", "continua"),
    (r"los flujos de integración continua sobre GitHub Actions se encuentran disponibles", "continua"),
    (r"se verifica automáticamente en el pipeline de integración continua.", "continua"),
    (r"El tamaño muestral se determinó mediante la fórmula clásica de muestreo aleatorio simple", "fórmula"),
    (r"no un tamaño derivado a priori de la fórmula.", "fórmula"),
    (r"con un margen del 6,66~\% la fórmula reproduce el tamaño de 200 casos", "fórmula"),
    (r"La pseudonimización se valida con expresiones regulares del dominio y pruebas unitarias dedicadas.", "valida"),
    (r"de modo que no se publica un desglose de latencias que el repositorio no permite reproducir", "publica"),
]

# Usos legitimos que la herramienta informa como AMBIGUO (nunca INEQUIVOCO).
USOS_LEGITIMOS_AMBIGUOS = [
    (r"lo debilita el análisis de sensibilidad, que mantiene la reducción por encima del 65~\% aun descontando 10~s por caso", "aun"),
    (r"el módulo de clasificación valida que el texto sea JSON parseable, que contenga exactamente las claves \texttt{categoría} y \texttt{confianza}", "valida"),
    (r"Esta investigación diseña, implementa y valida un sistema automatizado de mesa de ayuda que integra orquestación con N8N", "valida"),
]


def test_la_linea_base_contiene_las_40_erratas_documentadas():
    assert len(ERRATAS_LINEA_BASE) == 40


@pytest.mark.parametrize(
    "oracion, token, sugerencia, clase",
    ERRATAS_LINEA_BASE,
    ids=[f"{i:02d}-{e[1]}" for i, e in enumerate(ERRATAS_LINEA_BASE)],
)
def test_cada_errata_de_la_linea_base_se_informa_con_la_clase_esperada(
    oracion, token, sugerencia, clase
):
    assert (token, sugerencia, clase) in clasif(oracion)


@pytest.mark.parametrize("oracion, token", USOS_LEGITIMOS_SIN_REPORTE)
def test_los_usos_legitimos_de_la_linea_base_no_se_informan(oracion, token):
    assert token not in tokens(oracion)


@pytest.mark.parametrize("oracion, token", USOS_LEGITIMOS_AMBIGUOS)
def test_los_usos_legitimos_ambiguos_nunca_reciben_correccion_automatica(oracion, token):
    candidatos = [c for c in inv(oracion) if c.token == token]

    assert candidatos and all(c.clase == "AMBIGUO" for c in candidatos)


def test_ningun_uso_legitimo_es_inequivoco():
    for oracion, _ in USOS_LEGITIMOS_SIN_REPORTE + USOS_LEGITIMOS_AMBIGUOS:
        assert [c for c in inv(oracion) if c.clase == "INEQUIVOCO"] == [], oracion


def test_hallazgos_adicionales_de_la_linea_base_fuera_de_la_lista_de_40():
    # Erratas no documentadas por el dictamen que la herramienta tambien detecta.
    casos = [
        (r"?`cual es la magnitud de la reducción del tiempo de registro? Segundo", "cual", "cuál"),
        (r"?`alcanza el clasificador el umbral de exactitud global, y como se distribuyen los errores?", "como", "cómo"),
        (r"La evolución del campo durante la última decada ha estado dominada por la arquitectura Transformer", "decada", "década"),
        (r"La estrategia de pruebas se sustento en la pirámide clásica descrita por Crispin", "sustento", "sustentó"),
    ]

    for oracion, token, sugerencia in casos:
        assert (token, sugerencia) in [(c.token, c.sugerencia) for c in inv(oracion)], oracion


# ---------------------------------------------------------------------------
# 1.7 Salida del inventario y CLI por defecto
# ---------------------------------------------------------------------------


def escribir(ruta, texto, newline="\n"):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(texto.replace("\n", newline))


def filas(capsys):
    lineas = capsys.readouterr().out.splitlines()
    assert lineas[0] == CABECERA
    return [linea.split("\t") for linea in lineas[1:]]


def test_inventario_emite_una_fila_tsv_por_candidato_con_las_ocho_columnas(tmp_path, capsys):
    ruta = tmp_path / "a.tex"
    escribir(ruta, "Primera fila.\nUna derivación erronea inicial.\n")

    assert rt.main(["--archivos", str(ruta)]) == 0

    (fila,) = filas(capsys)
    assert fila[0].endswith("a.tex")
    assert fila[1:] == [
        "2", "16", "erronea", "errónea", "INEQUIVOCO", "prosa",
        "Una derivación erronea inicial.",
    ]


def test_linea_y_columna_son_correctas_con_terminadores_crlf(tmp_path, capsys):
    ruta = tmp_path / "crlf.tex"
    escribir(ruta, "uno\ndos erronea\ntres\n", newline="\r\n")

    rt.main(["--archivos", str(ruta)])

    (fila,) = filas(capsys)
    assert fila[1:3] == ["2", "5"]
    assert fila[-1] == "dos erronea"


def test_el_contexto_tiene_hasta_cinco_palabras_por_lado_y_sin_comandos(tmp_path, capsys):
    ruta = tmp_path / "ctx.tex"
    escribir(
        ruta,
        r"a b c d \emph{e} f g h i j erronea k l m n o p q" + "\n",
    )

    rt.main(["--archivos", str(ruta)])

    (fila,) = filas(capsys)
    assert fila[-1] == "f g h i j erronea k l m n o"
    assert "\\" not in fila[-1]


def test_dos_ejecuciones_consecutivas_producen_exactamente_la_misma_salida(tmp_path, capsys):
    for nombre in ("b.tex", "a.tex"):
        escribir(tmp_path / nombre, "una erronea y otra multiples\n")
    argumentos = ["--archivos", str(tmp_path / "b.tex"), str(tmp_path / "a.tex")]

    rt.main(argumentos)
    primera = capsys.readouterr().out
    rt.main(argumentos)
    segunda = capsys.readouterr().out

    assert primera == segunda
    assert primera.count("\n") == 5  # cabecera + 4 candidatos


def test_las_filas_salen_ordenadas_por_archivo_linea_y_columna(tmp_path, capsys):
    escribir(tmp_path / "b.tex", "erronea\n")
    escribir(tmp_path / "a.tex", "x\nmultiples erronea\nerronea\n")

    rt.main(["--archivos", str(tmp_path / "b.tex"), str(tmp_path / "a.tex")])

    orden = [(Path(f[0]).name, int(f[1]), int(f[2])) for f in filas(capsys)]
    assert orden == [("a.tex", 2, 1), ("a.tex", 2, 11), ("a.tex", 3, 1), ("b.tex", 1, 1)]


def test_la_autoconsistencia_usa_el_corpus_de_todos_los_archivos(tmp_path, capsys):
    escribir(tmp_path / "a.tex", "El huésped final.\n")
    escribir(tmp_path / "b.tex", "El huesped inicial.\n")

    rt.main(["--archivos", str(tmp_path / "a.tex"), str(tmp_path / "b.tex")])

    (fila,) = filas(capsys)
    assert fila[0].endswith("b.tex") and fila[3:6] == ["huesped", "huésped", "AMBIGUO"]


def test_el_objetivo_por_defecto_es_paper_sections_relativo_al_script(
    tmp_path, capsys, monkeypatch
):
    destino = tmp_path / "paper" / "sections"
    destino.mkdir(parents=True)
    escribir(destino / "01.tex", "una erronea\n")
    escribir(destino / "notas.txt", "otra multiples\n")
    monkeypatch.setattr(rt, "DIR_SCRIPT", tmp_path)
    monkeypatch.setattr(rt, "DIR_SECCIONES", destino)

    assert rt.main([]) == 0

    (fila,) = filas(capsys)
    assert fila[0] == "paper/sections/01.tex"


def test_el_objetivo_por_defecto_real_existe_en_el_repositorio():
    assert rt.DIR_SECCIONES == Path(rt.__file__).resolve().parent / "paper" / "sections"
    assert rt.DIR_SECCIONES.name == "sections"


def test_un_archivo_inexistente_termina_con_codigo_2_y_mensaje(tmp_path, capsys):
    assert rt.main(["--archivos", str(tmp_path / "no-existe.tex")]) == 2

    capturado = capsys.readouterr()
    assert "no-existe.tex" in capturado.err
    assert capturado.out == ""


def test_el_inventario_no_cambia_los_hashes_de_los_archivos(tmp_path, capsys):
    rutas = [tmp_path / "a.tex", tmp_path / "b.tex"]
    escribir(rutas[0], "una erronea\r\n", newline="")
    escribir(rutas[1], "otra multiples\n")
    antes = [_hash(r) for r in rutas]

    rt.main(["--archivos", *map(str, rutas)])

    capsys.readouterr()
    assert [_hash(r) for r in rutas] == antes
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.tex", "b.tex"]


# ---------------------------------------------------------------------------
# 1.8 --diff y --apply (decision D4)
# ---------------------------------------------------------------------------

FRAGMENTO_MIXTO = (
    "Una derivación erronea en prosa.\n"
    "Sesgos hacía una clase.\n"
    "\\begin{tabular}{ll}\n"
    "telefono & erronea \\\\\n"
    "\\end{tabular}\n"
    "Dijo ``la derivación erronea del ticket'' y siguió.\n"
)


def bytes_de(ruta):
    return Path(ruta).read_bytes()


def test_diff_muestra_solo_correcciones_inequivocas_en_prosa_y_no_escribe(tmp_path, capsys):
    ruta = tmp_path / "m.tex"
    escribir(ruta, FRAGMENTO_MIXTO)
    antes = bytes_de(ruta)

    assert rt.main(["--diff", "--archivos", str(ruta)]) == 0

    lineas = capsys.readouterr().out.splitlines()
    quitadas = [x for x in lineas if x.startswith("-") and not x.startswith("---")]
    agregadas = [x for x in lineas if x.startswith("+") and not x.startswith("+++")]
    assert quitadas == ["-Una derivación erronea en prosa."]
    assert agregadas == ["+Una derivación errónea en prosa."]
    assert lineas[0].startswith("--- ") and lineas[1].startswith("+++ ")
    assert bytes_de(ruta) == antes


def test_diff_sin_correcciones_pendientes_no_imprime_nada(tmp_path, capsys):
    ruta = tmp_path / "limpio.tex"
    escribir(ruta, "Sesgos hacía una clase y una errónea derivación.\n")

    assert rt.main(["--diff", "--archivos", str(ruta)]) == 0

    assert capsys.readouterr().out == ""


def test_apply_corrige_solo_inequivocos_en_prosa(tmp_path, capsys):
    ruta = tmp_path / "m.tex"
    escribir(ruta, FRAGMENTO_MIXTO)

    assert rt.main(["--apply", "--archivos", str(ruta)]) == 0

    esperado = FRAGMENTO_MIXTO.replace(
        "Una derivación erronea en prosa.", "Una derivación errónea en prosa."
    )
    assert bytes_de(ruta) == esperado.encode("utf-8")
    # La linea con "hacía" y la celda `erronea`/`telefono` quedan identicas.
    resultado = ruta.read_text(encoding="utf-8")
    assert "Sesgos hacía una clase." in resultado
    assert "telefono & erronea" in resultado
    assert "``la derivación erronea del ticket''" in resultado


def test_apply_corrige_varias_ocurrencias_en_la_misma_linea(tmp_path, capsys):
    ruta = tmp_path / "v.tex"
    escribir(ruta, "multiples erronea y multiples tambien.\n")

    rt.main(["--apply", "--archivos", str(ruta)])

    assert ruta.read_text(encoding="utf-8") == "múltiples errónea y múltiples también.\n"


def test_apply_preserva_capitalizacion_crlf_y_no_crea_bak(tmp_path, capsys):
    ruta = tmp_path / "crlf.tex"
    original = "Erronea y ERRONEA.\r\nSegunda erronea fila final\r\n"
    ruta.write_bytes(original.encode("utf-8"))

    rt.main(["--apply", "--archivos", str(ruta)])

    esperado = "Errónea y ERRÓNEA.\r\nSegunda errónea fila final\r\n"
    assert ruta.read_bytes() == esperado.encode("utf-8")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["crlf.tex"]


def test_apply_preserva_lf_en_un_archivo_lf(tmp_path, capsys):
    ruta = tmp_path / "lf.tex"
    ruta.write_bytes("Una erronea.\nOtra.\n".encode("utf-8"))

    rt.main(["--apply", "--archivos", str(ruta)])

    assert ruta.read_bytes() == "Una errónea.\nOtra.\n".encode("utf-8")


def test_apply_es_idempotente_y_el_diff_posterior_queda_vacio(tmp_path, capsys):
    ruta = tmp_path / "i.tex"
    escribir(ruta, FRAGMENTO_MIXTO)
    rt.main(["--apply", "--archivos", str(ruta)])
    despues_de_la_primera = bytes_de(ruta)
    capsys.readouterr()

    rt.main(["--apply", "--archivos", str(ruta)])
    rt.main(["--diff", "--archivos", str(ruta)])

    assert bytes_de(ruta) == despues_de_la_primera
    assert capsys.readouterr().out == ""


def test_apply_informa_en_stderr_la_cantidad_de_correcciones(tmp_path, capsys):
    ruta = tmp_path / "c.tex"
    escribir(ruta, "multiples y erronea.\n")

    rt.main(["--apply", "--archivos", str(ruta)])

    capturado = capsys.readouterr()
    assert capturado.out == ""
    assert "2 correcciones" in capturado.err


def test_apply_no_aplica_candidatos_con_decision_mantener(tmp_path, capsys):
    ruta = tmp_path / "d.tex"
    escribir(ruta, "La derivación erronea del termino en ingles.\nOtra erronea derivación.\n")
    decisiones = tmp_path / "decisiones.tsv"
    escribir(
        decisiones,
        "archivo\ttoken\tcontexto\tdecision\tforma_final\tjustificacion\n"
        "d.tex\terronea\tLa derivación erronea del termino en ingles.\tmantener\terronea\t"
        "termino citado en ingles\n",
    )

    rt.main(["--apply", "--archivos", str(ruta), "--decisiones", str(decisiones)])

    resultado = ruta.read_text(encoding="utf-8")
    assert "La derivación erronea del" in resultado
    assert "Otra errónea derivación." in resultado


def test_diff_y_apply_ignoran_las_decisiones_ajenas_al_candidato(tmp_path, capsys):
    ruta = tmp_path / "e.tex"
    escribir(ruta, "Una erronea derivación.\n")
    decisiones = tmp_path / "decisiones.tsv"
    escribir(
        decisiones,
        "archivo\ttoken\tcontexto\tdecision\tforma_final\tjustificacion\n"
        "e.tex\terronea\tOtro contexto distinto erronea aqui\tmantener\terronea\tx\n"
        "otro.tex\terronea\tUna erronea derivación\tmantener\terronea\tx\n",
    )

    rt.main(["--apply", "--archivos", str(ruta), "--decisiones", str(decisiones)])

    assert ruta.read_text(encoding="utf-8") == "Una errónea derivación.\n"


# ---------------------------------------------------------------------------
# 1.9 Registro de decisiones y --check (decisiones D4 y D5)
# ---------------------------------------------------------------------------

ENCABEZADO_DECISIONES = "archivo\ttoken\tcontexto\tdecision\tforma_final\tjustificacion\n"


def correr_check(tmp_path, texto, decisiones="", nombre="t.tex", newline_tsv="\n"):
    """Escribe un archivo y su registro, y ejecuta `--check`."""
    ruta = tmp_path / nombre
    escribir(ruta, texto)
    tsv = tmp_path / "decisiones.tsv"
    escribir(tsv, ENCABEZADO_DECISIONES + decisiones, newline=newline_tsv)
    return rt.main(["--check", "--archivos", str(ruta), "--decisiones", str(tsv)])


def test_check_limpio_termina_con_codigo_0(tmp_path, capsys):
    texto = "Una derivación errónea. Hay mejora continua y la fórmula clásica.\n"

    assert correr_check(tmp_path, texto) == 0
    assert capsys.readouterr().out == ""


def test_check_detecta_una_errata_reintroducida_y_la_lista(tmp_path, capsys):
    texto = "Fila uno.\nHay una derivación erronea ahora.\n"

    codigo = correr_check(tmp_path, texto, nombre="reintroducida.tex")

    assert codigo == 1
    fila = [f for f in filas(capsys) if f[3] == "erronea"][0]
    assert fila[0].endswith("reintroducida.tex")
    assert (fila[1], fila[3], fila[4]) == ("2", "erronea", "errónea")


def test_check_homografo_nuevo_sin_decision_falla_y_pasa_al_corregirlo(tmp_path, capsys):
    assert correr_check(tmp_path, "el flujo continua sin cambios\n") == 1
    capsys.readouterr()

    assert correr_check(tmp_path, "el flujo continúa sin cambios\n") == 0


def test_check_homografo_nuevo_pasa_si_se_registra_mantener(tmp_path, capsys):
    texto = "el flujo continua sin cambios\n"
    decision = "t.tex\tcontinua\tel flujo continua sin cambios\tmantener\tcontinua\tadjetivo\n"

    assert correr_check(tmp_path, texto, decision) == 0


def test_check_una_decision_corregir_no_aplicada_sigue_pendiente(tmp_path, capsys):
    texto = "el flujo continua sin cambios\n"
    decision = "t.tex\tcontinua\tel flujo continua sin cambios\tcorregir\tcontinúa\tverbo\n"

    assert correr_check(tmp_path, texto, decision) == 1


def test_check_las_decisiones_sobreviven_al_desplazamiento_de_lineas(tmp_path, capsys):
    decision = "t.tex\tcontinua\tel flujo continua sin cambios\tmantener\tcontinua\tadjetivo\n"
    original = "el flujo continua sin cambios\n"
    desplazado = "Nueva primera fila.\nOtra fila.\n" + original

    assert correr_check(tmp_path, original, decision) == 0
    assert correr_check(tmp_path, desplazado, decision) == 0


def test_check_la_decision_no_se_aplica_a_un_contexto_distinto(tmp_path, capsys):
    decision = "t.tex\tcontinua\tel flujo continua sin cambios\tmantener\tcontinua\tadjetivo\n"

    assert correr_check(tmp_path, "el sistema continua con otros cambios\n", decision) == 1


def test_check_inequivoco_en_prosa_con_decision_mantener_no_es_pendiente(tmp_path, capsys):
    texto = "El termino citado: erronea tal cual.\n"
    decision = "t.tex\terronea\tEl termino citado: erronea tal cual.\tmantener\terronea\tcita\n"

    assert correr_check(tmp_path, texto, decision) == 0


def test_check_exige_decision_para_candidatos_en_tabla_y_cita(tmp_path, capsys):
    tabla = "\\begin{tabular}{l}\ndato erronea\n\\end{tabular}\n"
    cita = "Dijo ``una erronea cosa'' ayer.\n"

    assert correr_check(tmp_path, tabla) == 1
    assert correr_check(tmp_path, cita) == 1
    capsys.readouterr()
    decision_tabla = "t.tex\terronea\tdato erronea\tmantener\terronea\tcelda\n"
    decision_cita = "t.tex\terronea\tDijo ``una erronea cosa'' ayer.\tmantener\terronea\tcita\n"
    assert correr_check(tmp_path, tabla, decision_tabla) == 0
    assert correr_check(tmp_path, cita, decision_cita) == 0


def test_check_lee_un_registro_con_terminadores_crlf(tmp_path, capsys):
    texto = "el flujo continua sin cambios\n"
    decision = "t.tex\tcontinua\tel flujo continua sin cambios\tmantener\tcontinua\tadjetivo\n"

    assert correr_check(tmp_path, texto, decision, newline_tsv="\r\n") == 0


def test_check_avisa_en_stderr_de_decisiones_sin_candidato_pero_no_falla(tmp_path, capsys):
    decision = "t.tex\tcontinua\tuna frase que ya no existe\tmantener\tcontinua\tobsoleta\n"

    assert correr_check(tmp_path, "Texto limpio.\n", decision) == 0
    assert "sin candidato" in capsys.readouterr().err


def test_check_sin_archivo_de_decisiones_equivale_a_un_registro_vacio(tmp_path, capsys):
    ruta = tmp_path / "t.tex"
    escribir(ruta, "Texto limpio.\n")

    codigo = rt.main(["--check", "--archivos", str(ruta), "--decisiones", str(tmp_path / "x.tsv")])

    assert codigo == 0


def test_cargar_decisiones_indexa_por_archivo_token_y_contexto_normalizado(tmp_path):
    tsv = tmp_path / "d.tsv"
    escribir(
        tsv,
        ENCABEZADO_DECISIONES
        + "paper/sections/01.tex\testa\tel  indicador esta   activo\tcorregir\tstá\tverbo\n"
        + "\n# comentario\n",
    )

    decisiones = rt.cargar_decisiones(tsv)

    assert decisiones == {
        ("01.tex", "esta", "el indicador esta activo"): rt.Decision("corregir", "stá", "verbo"),
    }


def test_clave_de_decision_no_depende_del_numero_de_linea(tmp_path):
    a = inv("x\ny el flujo continua sin cambios z\n", archivo="t.tex")
    b = inv("\n\n\nx\ny el flujo continua sin cambios z\n", archivo="t.tex")

    assert a[0].linea != b[0].linea
    assert rt.clave_de(a[0]) == rt.clave_de(b[0])


def test_la_opcion_todos_amplia_el_inventario_de_la_cli(tmp_path, capsys):
    ruta = tmp_path / "t.tex"
    escribir(ruta, "esta investigación avanza.\n")

    rt.main(["--archivos", str(ruta)])
    sin_todos = filas(capsys)
    rt.main(["--todos", "--archivos", str(ruta)])
    con_todos = filas(capsys)

    assert sin_todos == []
    assert [(f[3], f[4], f[5]) for f in con_todos] == [("esta", "está", "AMBIGUO")]


# ---------------------------------------------------------------------------
# 1.10 --base: invariante puramente diacritico (decision D5)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "izquierda, derecha",
    [
        ("Documentacion tecnica", "Documentaci{\\'o}n t{\\'e}cnica"),
        ("Documentacion", "Documentaci\\'{o}n"),
        ("Documentacion", "Documentaci\\'on"),
        ("erronea", "errónea"),
        ("espanol", "espa\\~nol"),
        ("espanol", "espa{\\~n}ol"),
        ("espanol", "espa\\~{n}ol"),
        ("pinguino", "ping\\\"uino"),
        ("pinguino", "ping{\\\"u}ino"),
        ("pinguino", "pingüino"),
        ("indice", "{\\'\\i}ndice"),
        ("indice", "\\'{\\i}ndice"),
        ("Indice general", "Índice general"),
        ("AUTOMATIZACION", "AUTOMATIZACIÓN"),
    ],
)
def test_sin_diacriticos_iguala_formas_acentuadas_y_escapes_latex(izquierda, derecha):
    assert rt.sin_diacriticos(izquierda) == rt.sin_diacriticos(derecha)


@pytest.mark.parametrize(
    "izquierda, derecha",
    [
        ("61,6 s", "61,7 s"),
        ("erronea", "erronee"),
        ("a", "à"),
        ("\\label{sec:a}", "\\label{sec:b}"),
        ("casa", "Casa"),
    ],
)
def test_sin_diacriticos_distingue_cambios_no_diacriticos(izquierda, derecha):
    assert rt.sin_diacriticos(izquierda) != rt.sin_diacriticos(derecha)


def test_comparar_con_base_acepta_cambios_solo_diacriticos():
    base = "Una derivacion erronea.\nSegunda fila.\n"
    nuevo = "Una derivación errónea.\nSegunda fila.\n"

    assert rt.comparar_con_base(base, nuevo) == []


def test_comparar_con_base_acepta_una_diferencia_de_terminadores():
    assert rt.comparar_con_base("uno\r\ndos\r\n", "uno\ndos\n") == []


def test_comparar_con_base_rechaza_un_cambio_de_cifra():
    base = "El tiempo fue 61,6 s en promedio.\nOtra.\n"
    nuevo = "El tiempo fue 61,7 s en promedio.\nOtra.\n"

    assert rt.comparar_con_base(base, nuevo) == [
        (1, "El tiempo fue 61,6 s en promedio.", "El tiempo fue 61,7 s en promedio.")
    ]


def test_comparar_con_base_rechaza_un_cambio_de_letra_no_diacritica():
    assert [v[0] for v in rt.comparar_con_base("la erronea\nx\n", "la erronee\nx\n")] == [1]


def test_comparar_con_base_rechaza_una_cantidad_distinta_de_lineas():
    violaciones = rt.comparar_con_base("a\nb\n", "a\nb\nc\n")

    assert len(violaciones) == 1 and violaciones[0][0] == 0


def _preparar_base(tmp_path, base, nuevo, nombre="s.tex"):
    carpeta_base = tmp_path / "base"
    carpeta_base.mkdir()
    escribir(carpeta_base / nombre, base)
    escribir(tmp_path / nombre, nuevo)
    return carpeta_base, tmp_path / nombre


def test_cli_base_termina_en_0_con_cambios_puramente_diacriticos(tmp_path, capsys):
    carpeta, ruta = _preparar_base(
        tmp_path, "Documentacion erronea.\n", "Documentaci{\\'o}n errónea.\n"
    )

    codigo = rt.main(["--base", str(carpeta), "--archivos", str(ruta)])

    assert codigo == 0
    assert capsys.readouterr().out == ""


def test_cli_base_termina_en_1_y_senala_la_linea_ante_un_cambio_de_cifra(tmp_path, capsys):
    carpeta, ruta = _preparar_base(tmp_path, "uno\nvalor 0,85 fijo\n", "uno\nvalor 0,86 fijo\n")

    codigo = rt.main(["--base", str(carpeta), "--archivos", str(ruta)])

    salida = capsys.readouterr().out
    assert codigo == 1
    assert "s.tex:2" in salida and "0,85" in salida and "0,86" in salida


def test_cli_base_termina_en_1_ante_un_cambio_de_una_letra_no_diacritica(tmp_path, capsys):
    carpeta, ruta = _preparar_base(tmp_path, "la erronea\n", "la errónee\n")

    assert rt.main(["--base", str(carpeta), "--archivos", str(ruta)]) == 1


def test_cli_base_termina_en_1_si_falta_el_homonimo_en_la_base(tmp_path, capsys):
    carpeta, ruta = _preparar_base(tmp_path, "x\n", "x\n")
    otro = tmp_path / "otro.tex"
    escribir(otro, "x\n")

    codigo = rt.main(["--base", str(carpeta), "--archivos", str(ruta), str(otro)])

    assert codigo == 1
    assert "otro.tex" in capsys.readouterr().err


def test_cli_base_con_objetivo_por_defecto_compara_paper_sections(tmp_path, capsys, monkeypatch):
    destino = tmp_path / "paper" / "sections"
    destino.mkdir(parents=True)
    escribir(destino / "01.tex", "una errónea\n")
    monkeypatch.setattr(rt, "DIR_SCRIPT", tmp_path)
    monkeypatch.setattr(rt, "DIR_SECCIONES", destino)
    base = tmp_path / "previa"
    base.mkdir()
    escribir(base / "01.tex", "una erronea\n")

    assert rt.main(["--base", str(base)]) == 0


def test_cli_base_no_modifica_ningun_archivo(tmp_path, capsys):
    carpeta, ruta = _preparar_base(tmp_path, "erronea\n", "errónea\n")
    antes = (_hash(ruta), _hash(carpeta / "s.tex"))

    rt.main(["--base", str(carpeta), "--archivos", str(ruta)])

    assert (_hash(ruta), _hash(carpeta / "s.tex")) == antes


# ---------------------------------------------------------------------------
# 1.5 (ajuste tras el inventario real): falsos positivos observados en la tesis
# ---------------------------------------------------------------------------


def test_autoconsistencia_no_propone_la_variante_acentuada_si_la_sin_tilde_domina():
    # "activo" (sustantivo/adjetivo) convive con "activó" (verbo): no es una errata.
    texto = "Un activo fijo y otro activo inicial; el sistema se activó luego."

    assert clasif(texto) == []


def test_autoconsistencia_propone_la_variante_si_la_acentuada_es_al_menos_tan_frecuente():
    texto = "Que evalue el sistema lo que evalúe otro y evalúe un tercero."

    assert ("evalue", "evalúe", "AMBIGUO") in clasif(texto)


def test_como_tras_define_o_describe_no_es_interrogativo():
    texto = "La exactitud se define como la proporción y se describe como útil."

    assert clasif(texto) == []


def test_este_tras_que_relativo_no_se_toma_por_verbo_estar():
    assert clasif("a los que este apartado remite sin reproducir su contenido") == []
    assert clasif("los casos que esta investigación acota") == []


# ---------------------------------------------------------------------------
# 1.11 Suite completa: invariantes globales de la herramienta
# ---------------------------------------------------------------------------


def test_la_herramienta_solo_importa_la_biblioteca_estandar():
    import ast

    arbol = ast.parse(Path(rt.__file__).read_text(encoding="utf-8"))
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            importados.add(nodo.module.split(".")[0])

    assert importados and importados <= set(sys.stdlib_module_names)


def test_ejecutada_como_script_emite_el_inventario_y_respeta_el_codigo_de_salida(tmp_path):
    import subprocess

    ruta = tmp_path / "s.tex"
    escribir(ruta, "Una derivación erronea.\n")
    base = [sys.executable, "-I", rt.__file__]

    inventario = subprocess.run(
        base + ["--archivos", str(ruta)], capture_output=True, text=True, encoding="utf-8"
    )
    check = subprocess.run(
        base + ["--check", "--archivos", str(ruta), "--decisiones", str(tmp_path / "n.tsv")],
        capture_output=True, text=True, encoding="utf-8",
    )

    assert inventario.returncode == 0
    assert inventario.stdout.splitlines()[0] == CABECERA
    assert "\terronea\terrónea\tINEQUIVOCO\tprosa\t" in inventario.stdout
    assert check.returncode == 1


def test_el_inventario_del_arbol_real_no_modifica_ningun_archivo(capsys):
    archivos = sorted(rt.DIR_SECCIONES.glob("*.tex"))
    if not archivos:
        pytest.skip("el arbol de la tesis no esta disponible")
    antes = [_hash(a) for a in archivos]

    assert rt.main([]) == 0

    capsys.readouterr()
    assert [_hash(a) for a in archivos] == antes


def test_el_inventario_con_todos_es_un_superconjunto_del_inventario_por_defecto():
    texto = (
        "Esta investigación esta activa; el flujo continua y la mejora continua. "
        "?`cual es la magnitud? Se registro el caso, derivación erronea hacia el area."
    )

    base = {(c.inicio, c.token) for c in inv(texto)}
    todos = {(c.inicio, c.token) for c in inv(texto, todos=True)}

    assert base and base < todos


def test_apply_seguido_de_check_deja_solo_lo_ambiguo_pendiente(tmp_path, capsys):
    ruta = tmp_path / "ciclo.tex"
    escribir(ruta, "Una erronea derivación, el flujo continua y multiples canales.\n")
    tsv = tmp_path / "d.tsv"
    argumentos = ["--archivos", str(ruta), "--decisiones", str(tsv)]

    assert rt.main(["--check", *argumentos]) == 1
    rt.main(["--apply", *argumentos])
    capsys.readouterr()
    assert rt.main(["--check", *argumentos]) == 1
    pendientes = [f[3] for f in filas(capsys)]
    assert pendientes == ["continua"]

    ruta.write_text(
        ruta.read_text(encoding="utf-8").replace("continua", "continúa"), encoding="utf-8"
    )
    assert rt.main(["--check", *argumentos]) == 0


# ---------------------------------------------------------------------------
# 1.11 Cobertura: ramas de borde (LaTeX mal formado y cierres incompletos)
# ---------------------------------------------------------------------------


def test_fin_grupo_devuelve_menos_uno_si_el_grupo_no_se_cierra():
    assert rt._fin_grupo("{abc {anidado}", 0) == -1
    assert rt._fin_grupo("[abc", 0, "[", "]") == -1
    assert rt._fin_grupo("{a\\}b}", 0) == 6  # la llave escapada no cierra


def test_proteger_un_rango_vacio_no_cambia_la_mascara():
    mascara = rt.Mascara("abc")

    mascara.proteger(1, 1)

    assert bytes(mascara.zonas) == bytes(3)


def test_argumento_opcional_sin_cierre_no_rompe_y_deja_el_resto_como_prosa():
    assert tokens("\\cite[p. 3 sin cierre y la derivación erronea") == ["erronea"]


def test_espacio_entre_comando_y_argumento_protegido():
    assert tokens("\\ref {erronea} y erronea") == ["erronea"]


def test_foreignlanguage_protege_el_texto_en_otro_idioma():
    texto = "\\foreignlanguage{english}{the erronea text} y erronea"

    assert [c.inicio for c in inv(texto)] == [texto.rindex("erronea")]


def test_participio_irregular_tras_esta_es_senal_de_estar():
    assert ("esta", "está", "AMBIGUO") in clasif("el campo esta abierto")


def test_puntuacion_tras_esta_con_sujeto_nominal_es_senal_de_estar():
    assert ("esta", "está", "AMBIGUO") in clasif("el sistema esta. Luego sigue")


def test_pregunta_sin_cierre_o_con_salto_de_parrafo_no_define_un_contexto_interrogativo():
    assert clasif("?`cual es el caso sin cierre") == []
    assert clasif("?`cual es el caso\n\ny ahora termina?") == []


def test_aplicar_correcciones_rechaza_un_texto_que_ya_no_coincide():
    (candidato,) = inv("una erronea derivación")

    with pytest.raises(ValueError):
        rt.aplicar_correcciones("una otra derivación", [candidato])
