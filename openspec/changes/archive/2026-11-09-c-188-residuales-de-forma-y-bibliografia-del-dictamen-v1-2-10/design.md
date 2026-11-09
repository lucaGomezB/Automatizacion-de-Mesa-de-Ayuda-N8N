# Design: Residuales de forma y bibliografia del dictamen CONEAU sobre v1.2.10

## Context

El dictamen del 2026-11-08 (`auditorias/Dictamen_Tesis_v10_v1.2.10_CONEAU_2026-11-08.md`)
examina el tag `v1.2.10`. c-187 (archivado en
`openspec/changes/archive/2026-11-08-c-187-atender-el-dictamen-coneau-v1-2-10/`, release
`v1.2.11`, PR #72) cerro A1-A5, B1, B2, B3 y B6 y dejo en la Tabla
`tab:anexo-trazabilidad-0811` una fila que remite B4, B5, B7 y C1-C5 a un change
posterior. c-188 es ese change: documento, figuras, bibliografia y dos scripts de
verificacion. No cambia datos, codigo del sistema ni valores canonicos.

**Dependencia.** El apply corre en una rama nueva desde `main` despues de fusionar el
PR #72. Antes de empezar: `git log -1 --format=%h origin/main` contiene el commit del hash
de `v1.2.11` y `openspec list` no muestra c-187 activo.

**Numeracion y anclas.** Las secciones compiladas no coinciden con el nombre de los
archivos: 4.x = `04-marco-metodologico.tex`, 6.x = `06-implementacion.tex`, 7 =
`11-aspectos-legales.tex`, 8.x = `07-resultados.tex`, 9.x = `08-discusion.tex`, Anexos =
`12-anexos.tex`. Ademas, la numeracion que usa el dictamen para los capitulos 4 y 9 no
coincide con `paper/main.toc` de la rama de c-187 (por ejemplo, el dictamen llama "4.6"
al analisis estadistico, que el indice numera 4.7 `subsec:analisis-estadistico`, y "9.7"
al parrafo de la Ley 25.326, que esta en 9.6 `subsec:reflexiones-generalizacion`). Por
eso `tasks.md` identifica cada lugar por **etiqueta** (`\label`) y por **texto citado**;
los numeros de linea son orientativos (medidos en la rama de c-187) y se relocalizan con
`rg -n "<texto>"` en el apply.

**Topes.** PDF del tag `v1.2.11`: 118 paginas; PDF de `main` tras el commit del hash: 119
(reflujo de flotantes documentado en `dictamen-correcciones.md`, c-187). Tope del equipo:
100 (ya excedido y declarado). El resumen (237) y el abstract (237) no se tocan.

**Hechos verificados durante la propuesta (2026-11-08, solo lectura).**

- B4: `evaluation/run_evaluation.py` (~linea 976) arma el conjunto predicho como
  `{sector_predicho} ∪ sectores_adicionales`; `evaluation/metrics.py`
  (`perdida_hamming`, ~linea 217) normaliza por `|verdad ∪ predicho|` del caso (equivale
  a 1 − Jaccard), no por las cinco clases; `f1_macro` (~linea 108) es la media aritmetica
  de los F1 por clase. En `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` hay
  **8 casos con sectores adicionales, todos de la etapa deterministica** (R004, R051,
  R060, R113, R122, R126, R136, R181). Recomputo: con adicionales, subset 0,43, Hamming
  0,35858, micro-F1 0,66544 (los publicados); solo con la etiqueta principal, 0,44,
  0,35275 y 0,66916; Hamming normalizada por cinco clases, 0,182.
- B5: `panel_admin.png` y `dashboard.png` entraron en el commit `50d8b96` (c-80,
  2026-10-21) y se copiaron a v10 en c-122. Las capturas muestran "API operativa ·
  v1.0.0", 145 incidentes entre el 21-09 y el 21-10 (pico el 2-10), "Tasa revision humana
  64.8 %" y la pestaña "Revision Humana (94)": 94/145 = 0,648. Las filas visibles son del
  2-10 (corrida del corpus de correo y formulario) y del 13-10.
  `App/Frontend/Dockerfile` compila con `node:24-alpine` y sirve `/app/dist` con
  `nginx:alpine` en el puerto 3000; `docker-compose.yml` usa las redes `edge`, `data` y la
  de automatizacion (c-62), no `mesa_local_default`, y construye N8N desde
  `docker/n8n/Dockerfile` (c-182).
- B7: `.gitignore:29` (`*.log`) ignora `paper/main.log`.
  `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` → "Filas: 41;
  fallas: 22" (solo lee la seccion FASE 36); sus 11 pruebas (`unittest`) pasan.
- C2: el backend crea `genai.Client(api_key=...)`: usa la Gemini API de Google AI, no
  Vertex AI; la transcripcion telefonica la hace Gemini (`App/Backend/app/clients/gemini_stt.py`,
  c-52), no Twilio. La tesis cita hoy el precio de Vertex AI (`Google2026_vertex_pricing`).
- C3: `Ley25326_2000` ya usa la fecha de sancion (`date = {2000-10-04}`); el texto no cita
  el 30-10-2000.
- C5: UML no aparece en `sections/*.tex` fuera del glosario; FRM y UTN solo en un
  comentario de `00-portada.tex:2`. CONEAU (Anexo I), NLBSE (3), PABAK (8.7), RGPD (7),
  UTC (4.5) y GPT (3, como "GPT-3") se usan sin entrada.
- Item 36: los commits de `evaluation/data/campana/` van del 2026-11-04 (doble
  etiquetado) al 2026-11-08 (`intervenciones.csv`, `38392c1`); la barra del cronograma es
  de mes ("2026-11-01, 2026-11-30"), de modo que solo cambia la tabla de procedencia de
  `docs/diagrams/cronograma.md`, no `cronograma.png`.

## Goals / Non-Goals

**Goals:**

- Que las tres metricas multietiqueta secundarias sean reproducibles leyendo solo la tesis.
- Que ninguna figura muestre algo que el texto no explique o que contradiga la
  configuracion declarada, y que la matriz de confusion figure una sola vez.
- Que las afirmaciones del registro sobre la compilacion sean verificables desde el
  repositorio y que el verificador de trazabilidad pase sobre el arbol vigente.
- Que cada atribucion bibliografica observada sea fiel a su fuente o se rotule como
  inferencia propia, y que los proveedores y la normativa del capitulo legal tengan fuente.
- Cerrar la trazabilidad del dictamen del 8-11 en el Anexo I y en el registro.

**Non-Goals:**

- Recomendaciones A y B1, B2, B3, B6 (c-187).
- Nuevas mediciones, re-analisis o cambios de cifras.
- Busquedas bibliograficas nuevas mas alla de las fuentes que C1 y C2 nombran.
- Reemplazar el patron de release de dos commits (decidido en c-187, D7-A).

## Decisions

### D1 — Definicion de las metricas multietiqueta (B4)

Se **conserva la definicion implementada** y se declara, en lugar de recalcular con otra
convencion: en `subsec:analisis-estadistico` (4.7) una oracion define el conjunto predicho
(etiqueta principal mas los sectores adicionales que emite la etapa deterministica, 8
casos) y la Hamming loss "normalizada por la union de etiquetas verdaderas y predichas
del caso (equivalente a 1 − Jaccard), no por las cinco clases"; en `subsec:matriz-metricas`
(8.2) se reemplaza "una salida forzada a una sola etiqueta" por "una salida con una
etiqueta principal y, en 8 casos, sectores adicionales" y se remite a 4.7. No se agregan
las cifras alternativas al cuerpo (0,44 / 0,35275 / 0,182): se registran en
`numeros-canonicos.md` como verificacion, sin reemplazar valores.

Alternativa descartada: recalcular la Hamming loss por cinco clases (0,182). Cambiaria un
valor canonico y su intervalo bootstrap, que no se puede regenerar sin re-correr el
analisis, y se aleja de la "metrica del caso" que el texto ya usa.

Unificacion de los ejemplos del prompt: 5.5 (`subsec:subsistema-clasificacion`, "ejemplos
representativos balanceados") y 9.4 (`subsec:implicancias-practicas`, nota de costo
"ejemplos balanceados") pasan a "un unico ejemplo representativo por sector", como el
Anexo H (`subsec:anexo-estructura-prompt`) y `docs/prompt_gemini.txt` (verificar en el
apply que el prompt versionado tiene un ejemplo por clase).

### D2 — Matriz de confusion: conservar la Tabla 11, retirar la Figura 7 (B5)

Se retira el entorno `figure` de `fig:matriz_confusion` (`07-resultados.tex`, ~lineas
101-106) y la mencion "y en la Figura~\ref{fig:matriz_confusion}" de 8.2. Razones: la
tabla es la que el texto y los analisis citan (celdas exactas, totales), la figura no
agrega informacion, y su retiro es el ahorro principal de paginas de este change (una
figura a 0,85 del ancho, del orden de media a tres cuartos de pagina). El script
`scripts/figures/matriz_confusion.py` y `figures/matriz_confusion.pdf` se conservan como
artefacto reproducible no embebido (se anota en `conteos-canonicos-tecnicos.md`); el
requisito "Evidencia visual del sistema y de los resultados" pasa de ocho a siete figuras
y declara la matriz como tabla. La numeracion de figuras posteriores cambia sola (no hay
"Figura N" escrito a mano en las fuentes).

Alternativa descartada: conservar la figura y retirar la tabla. Perderia las cifras
exactas en el texto y obligaria a leer valores de un mapa de calor.

### D3 — Capturas de 6.8: explicar la procedencia (B5) — **decision del usuario**

| Opcion | Que hace | Costo | Riesgo |
|---|---|---|---|
| **A. Declarar la procedencia en las leyendas (recomendada)** | Leyendas de `fig:panel_admin` y `fig:dashboard`: "Captura de una instancia local de desarrollo (21-10-2026, rotulo v1.0.0) con los 145 incidentes cargados entre el 2 y el 13-10-2026; la cola y la tasa de revision reflejan el indicador `requiere_revision_humana` registrado por el backend en esa base, no la regla de confianza evaluada fuera de linea (\autoref{subsec:reduccion-intervencion})." | Bajo; ±1-2 lineas | Ninguno: cada dato se ve en la imagen o en `git log` |
| B. Reemplazar por capturas de la configuracion entregada | Levantar `v1.2.11`, cargar datos y recapturar | Alto; requiere el stack y datos sinteticos | Las capturas nuevas tambien mostrarian revisiones (regla c-82 si el reportante no se identifica); no resuelve el fondo |

**Recomendacion: A.** La causa exacta de cada uno de los 94 indicadores no se puede
reconstruir (la base de esa instancia no se versiono), de modo que la leyenda MUST NOT
atribuirla a una regla concreta: dice solo que es el indicador registrado por el backend y
que difiere de la evaluacion fuera de linea, con remision a 8.3. En el texto de 6.8 se
corrige "los casos derivados por el backend" si sugiere la regla de confianza.

### D4 — Diagrama de despliegue (B5)

`docs/diagrams/despliegue.md`: el nodo `FE` pasa a "Frontend React 19 (bundle Vite
compilado) servido por nginx:alpine :3000 (sin puerto host)"; el nodo `N8N` a "N8N 2.11.2
(imagen derivada, parche IMAP c-182)"; el subgrafo de red refleja las redes de
`docker-compose.yml` (`edge`, `data` interna y la de automatizacion) en lugar de
`mesa_local_default`, solo si cabe sin cambiar la relacion de aspecto de forma que la
figura crezca en el PDF (si no cabe, se rotula "redes Docker de `docker-compose.yml`" y se
deja constancia). El texto introductorio del `.md` se alinea. Regeneracion, con el mismo
pipeline de c-140/c-163 (`conteos-canonicos-tecnicos.md`, figura `fig:despliegue`):

```bash
# desde la raiz; bloque mermaid extraido a un .mmd temporal FUERA del repositorio
python - <<'EOF' > "$TMP/despliegue.mmd"
import re; t=open("docs/diagrams/despliegue.md",encoding="utf-8").read()
print(re.search(r"```mermaid\n(.*?)```", t, re.S).group(1))
EOF
npx -y @mermaid-js/mermaid-cli@12.0.0 -i "$TMP/despliegue.mmd" -o "$TMP/despliegue.png" -b white -s 2
cp "$TMP/despliegue.png" "docs/Tesis/v10 (IA)/paper/figures/despliegue.png"
```

La version 12 es obligatoria (la 11 produce el diagrama apaisado). Se registran version de
mmdc, dimensiones (hoy 1568x1712) y relacion alto/ancho en `conteos-canonicos-tecnicos.md`
y se inspecciona visualmente el PNG (sin `\n` literales). `cronograma.png` **no** se
regenera (D9).

### D5 — Resumen versionado del registro de compilacion (B7) — **decision del usuario (no bloqueante)**

| Opcion | Que se versiona | Pros | Contras |
|---|---|---|---|
| **A. Resumen generado por script (recomendada)** | `paper/compilacion.md`, salida determinista de `docs/Tesis/Correcciones/resumir_registro_compilacion.py` | Diffs legibles; cifras exactas que el registro afirma; liga el resumen al PDF por SHA-256; probado | Un script mas que mantener |
| B. Des-ignorar `main.log` (`!docs/Tesis/v10 (IA)/paper/main.log`) | El log completo | Evidencia cruda | ~cientos de KB por release, rutas del contenedor y marcas de tiempo; diffs ruidosos; las cifras siguen sin estar resumidas |

**Recomendacion: A** (se aplica por defecto si el usuario no elige otra). Contrato del
script (pura lectura de archivos, sin red ni subprocesos):

- Entradas: `--log main.log --blg main.blg --pdf main.pdf --fuente <texto>` (la fuente es
  una descripcion pasada por el orquestador, por ejemplo "arbol de trabajo sobre
  `<hash corto>`", porque el commit de contenido aun no existe al compilar).
- Extrae: motor y version (primera linea del log), version de biber (`.blg`), paginas
  ("Output written on main.xdv (N pages"), errores (`^!`), referencias y citas
  indefinidas, etiquetas `multiply defined`, cantidad de `Overfull \hbox` y el maximo en
  pt, lineas `WARN`/`ERROR` del `.blg`, y el SHA-256 de `main.pdf` (`hashlib`).
- Salida: Markdown determinista (sin fecha del sistema; mismas entradas → mismos bytes),
  escrita en `paper/compilacion.md`.
- Funciones puras separadas de la E/S (`resumir(log_texto, blg_texto, pdf_bytes, fuente)
  -> dict` y `a_markdown(dict) -> str`), probadas con fragmentos sinteticos de log.

En el release, el resumen se regenera en el commit de contenido (el PDF del tag) y otra
vez en el commit del hash (su PDF), de modo que cada `compilacion.md` describe el PDF del
mismo commit. `dictamen-correcciones.md` remite al resumen en lugar de transcribir las
cifras. El requisito "Thesis PDF compilation" se modifica en ese sentido.

### D6 — Verificador de la matriz de trazabilidad (B7, Strict TDD)

Se **actualiza** (no se retira): sigue siendo la unica verificacion automatica de que las
correcciones declaradas existen en el texto. Cambios de comportamiento, cada uno precedido
por su prueba en `test_verificar_matriz_trazabilidad.py` (RED → GREEN → TRIANGULATE →
REFACTOR; las 11 pruebas actuales son la red de seguridad y se ajustan solo donde el
comportamiento cambia a proposito):

1. **Todas las matrices**: parsea toda tabla de 7 columnas cuyo encabezado incluya
   "Fragmento verificable", en cualquier seccion `## ` del registro (hoy FASE 36, A3/A4 y
   B5-B8 del 28-10; mas la nueva matriz del 8-11 que crea c-188). Cada fila registra su
   seccion de origen. La prueba vigente que excluye la matriz de "Siguiente seccion" se
   reemplaza por una que la incluye.
2. **Fragmento antes que linea**: una fila pasa si el fragmento aparece en el archivo y el
   ancla existe; si el fragmento esta en otra linea, pasa con aviso "desplazada N -> M"
   (las anclas de linea son orientativas). Con `--estricto` la linea exacta vuelve a ser
   obligatoria. Falla si el fragmento no aparece en ningun lugar del archivo o el ancla no
   existe.
3. **Filas superadas**: un estado que empieza con "SUPERADA" (por ejemplo,
   "SUPERADA por c-187") se omite como hoy "PENDIENTE".
4. Se conservan `--rev` y `--reubicar`; el resumen final informa filas, avisos y fallas
   por seccion.

Datos: tras el GREEN se corre sobre el arbol; cada falla restante se resuelve en el
registro (`dictamen-correcciones.md`, documentacion LOW) actualizando el fragmento al texto
vigente que sostiene la misma correccion, o marcando la fila "SUPERADA por c-NNN" cuando un
change posterior reescribio el parrafo a proposito (por ejemplo, filas de kappa o de la
intervencion que c-187 reescribio). Meta: 0 fallas en el arbol de trabajo y con
`--rev v1.2.12`. Se agrega al registro la matriz del 8-11 con fragmentos verificables para
las filas de c-187 (A1-A5, B1, B2, B3, B6) y de c-188. Ejecucion de las pruebas (desde
`docs/Tesis/Correcciones/`): `python -m unittest test_verificar_matriz_trazabilidad
test_resumir_registro_compilacion -v` (o `pytest` con el venv 3.13 local).

Alternativa descartada: retirar el script. Eliminaria la unica verificacion mecanica y el
dictamen admite ambas salidas; actualizarlo cuesta poco y cubre los tres dictamenes.

### D7 — Fidelidad bibliografica (C1 e item 32)

- **Galup et al. (2009)**: el texto (CACM 52(5), 124-127) es cerrado y no se verifico en tres
  dictamenes. Se conserva la cita de 2.1 para la caracterizacion de ITSM
  (`subsec:gestion-servicios-ti`, primera mencion, que coincide con el resumen de la obra)
  y se **reformulan como inferencia de los autores** la degradacion con el volumen "con un
  impacto desproporcionado en organizaciones medianas" de 1.2
  (`subsec:planteamiento-problema`) y la segunda mencion de 2.1 (`subsec:mesa-ayuda-itil`,
  "advierten que los procesos manuales de soporte tienden a degradarse"). Si en el apply
  alguien accede al texto y encuentra la afirmacion, se cita la pagina y se registra.
- **Item 32**: "ha recibido una atencion notablemente menor" (3,
  `subsec:trabajos-academicos` o `subsec:analisis-comparativo`, localizar por texto) se
  rotula como inferencia de los autores a partir de las obras citadas.
- **F1 macro**: `f1_macro` es la media aritmetica de los F1 por clase. Sokolova y Lapalme
  (2009) definen el F-score macro a partir de la precision y la sensibilidad
  macro-promediadas (F1 de los promedios). En 2.8, 4.6 (`subsec:metricas-instrumentos`)
  y 8.2 se cita a Sokolova y Lapalme para el promedio macro en general y a Opitz y Burst
  (2019, arXiv:1911.03347, "Macro F1 and Macro F1") para la variante empleada, con una
  frase que declare que existen dos formulas y cual se usa. Entrada nueva verificada en
  arXiv (`@misc` o `@online` con `eprint`, `url` y `urldate`).
- **Efecto Hawthorne** (4.2, `subsec:diseno-experimental`): se cita una fuente primaria o
  una revision sistematica verificada en Crossref, conservando o retirando Hernandez
  Sampieri segun quede sin pagina. Candidatas a verificar (no se citan sin verificar DOI,
  autores, anio y que la obra trate el efecto): McCambridge, Witton y Elbourne (2014,
  *Journal of Clinical Epidemiology*, revision sistematica del efecto Hawthorne); Adair
  (1984, *Journal of Applied Psychology*); Roethlisberger y Dickson (1939, *Management
  and the Worker*, Harvard University Press, fuente historica de los estudios).

### D8 — Fuentes de proveedores y normativa (C2)

Regla dura: **ninguna entrada se agrega sin abrir la URL en el apply**; cada entrada
`@online` lleva `url`, `urldate` (fecha de la consulta real) y autor institucional; la que
no se pueda verificar se omite y se registra la omision. Entradas previstas (titulos y
URL definitivos se fijan al verificar):

| Clave prevista | Fuente | Donde se cita |
|---|---|---|
| `Google2026_gemini_api_terms` | Terminos adicionales de la Gemini API (Google AI for Developers) y, si hace falta, la pagina de uso de datos | 7 `subsec:transferencia-internacional` (inferencia y transcripcion), 6.x donde se describe el cliente |
| `Google2026_gemini_audio` (opcional) | Documentacion de la Gemini API sobre comprension o transcripcion de audio | 7, transcripcion telefonica (si no la cubre la anterior) |
| `Twilio2026_programmable_voice` | Documentacion de Twilio Programmable Voice (grabacion `<Record>`/grabaciones) | 7 y 6.4 `subsec:integracion-canal-telefonico` |
| `Docker2026_docs` | Documentacion de Docker / Docker Compose | 6.1 `subsec:entorno-despliegue` |
| `Atlassian2026_jira_service_management` | Pagina oficial de Jira Service Management | 3.1 y Tabla 2 (`tab:comparativa`) |
| `osTicket2026` | Sitio oficial de osTicket | 3.1 y Tabla 2 |
| `Decreto1558_2001` | Decreto 1558/2001, reglamentario de la Ley 25.326 (art. 12) | 7 `subsec:transferencia-internacional` |
| `DNPDP2016_disposicion60` | Disposicion DNPDP 60-E/2016 (paises adecuados y contratos modelo de transferencia), o la norma vigente de la AAIP que la reemplace | 7 `subsec:transferencia-internacional` |

Hallazgo que condiciona C2: el backend usa la Gemini API de Google AI (clave de API) y
Gemini transcribe el audio; Twilio solo graba. Por eso la entrada de Twilio es de
Programmable Voice (grabacion), no de su servicio de transcripcion, y la oracion de 7 que
dice que el audio "se transcribe mediante reconocimiento del habla" en "la infraestructura
del proveedor" se precisa (Twilio graba; el backend envia el audio a la Gemini API para
transcribirlo) si la redaccion actual lo deja ambiguo. La cita de precios de Vertex AI
(`Google2026_vertex_pricing`) **no** se cambia en este change; se registra la discrepancia
servicio usado / fuente de precio como pregunta abierta.

Tabla 2: la nota al pie de URL se reemplaza por `\parencite` a las cinco plataformas
(Zendesk, Freshdesk y ServiceNow ya tienen entrada), lo que acorta la nota.

### D9 — Terminologia, Tabla 1, forma y glosario (C3, C4, C5, item 36)

- **C3**: 9.6 (`subsec:reflexiones-generalizacion`, ~`08-discusion.tex:101`): "minimizacion
  y pseudonimizacion" → "minimizacion y disociacion" (art. 2). Tabla 1
  (`tab:trabajos-academicos`): Zangari et al. (acceso abierto en Elsevier) se lee en el
  apply; si declara el idioma de los datasets se consigna, si no, "idioma no reportado"
  sin "(texto inaccesible)"; Ramya et al.: "compañero accesible de dos de los tres autores
  (arXiv:2103.15822)". `Ley25326_2000`: se conserva la fecha de sancion (4-10-2000) y se
  agrega en `note` "sancionada el 4 de octubre de 2000 y promulgada el 30 de octubre de
  2000" solo si el texto o la bibliografia la mencionan; se verifica que ninguna parte del
  texto diga otra fecha.
- **C4** (`Bibliography_base.bib`; se verifica en la salida de `biblatex-apa`, no solo en
  el `.bib`): `booktitle` EMNLP con el anio en todas las actas ("(EMNLP 2023)", "(EMNLP
  2025)"); las actas de PMLR (Guo 2017, Zhao 2021, Radford 2023) se imprimen como
  *Proceedings of Machine Learning Research*, volumen y paginas (APA 7, actas publicadas en
  serie periodica: `@article` con `journaltitle = {Proceedings of Machine Learning
  Research}`, `volume`, `pages`, `url` de proceedings.mlr.press; verificar el volumen de
  Radford, v202, en PMLR); Mosqueira-Rey: "{A} state of the art"; Jurafsky: "3.ª"
  (U+00AA) y comprobar que XeLaTeX con Arial lo imprime; URL verificada en Brown 2020 y
  Vaswani 2017 (proceedings.neurips.cc), Radford 2023 (PMLR), Pedregosa 2011 (jmlr.org) y
  Powers 2011 (URL o DOI estable verificado; si no existe, se registra); Mayor-Rocher:
  `note = {Publicación anticipada en línea}`; "Gomez"/"Gómez" segun la decision del
  usuario (recomendado: la grafia de la portada y del autor, "Gomez", en
  `Gomez2026_repositorio`). De paso se comprueba en el PDF que "Şenerkek" (Paket et al.) se
  imprime (pdftotext lo extrae como "enerkek"); si falta el glifo, se corrige.
- **C5** (`00-glosario.tex`): agregar CONEAU (Comision Nacional de Evaluacion y
  Acreditacion Universitaria), NLBSE (International Workshop on Natural Language-Based
  Software Engineering, verificar la expansion en la fuente citada), PABAK
  (Prevalence-Adjusted Bias-Adjusted Kappa), RGPD (Reglamento General de Proteccion de
  Datos), UTC (Coordinated Universal Time / Tiempo Universal Coordinado) y GPT (Generative
  Pre-trained Transformer); retirar UML, FRM y UTN. Se respeta la disposicion en dos
  columnas con orden alfabetico descendente (la columna izquierda llega hasta la mitad) y
  se actualiza el comentario de cabecera (79 → 82 entradas).
- **Item 36**: `docs/diagrams/cronograma.md`, fila "Campaña complementaria de medicion" de
  la tabla de procedencia: "las tablas primarias entre el 2026-11-04 y el 2026-11-08"
  (intervenciones exportadas el 8-11, `38392c1`); el parrafo de la linea ~52 ya dice "entre
  el 1 y el 8 de noviembre". No se regenera `cronograma.png`.

### D10 — Paginas

Libro mayor previsto (se mide en el apply, se registra en `dictamen-correcciones.md`):

| Cambio | Efecto estimado |
|---|---|
| Retiro de la Figura 7 | −0,5 a −0,75 pag. |
| Nota de la Tabla 2 por `\parencite` | −2 a −3 lineas |
| B4 (dos oraciones), D3-A (leyendas), C1 (frases de F1 y Hawthorne), C3 | +6 a +10 lineas |
| C2: 7-8 entradas nuevas en referencias | +0,3 a +0,5 pag. |
| C5: +6 −3 entradas (una fila mas del glosario) | +1 linea |

Tope: el PDF del commit de contenido (el que recibe el tag `v1.2.12`) MUST NOT superar 118
paginas. Si la primera compilacion lo supera, se recorta prosa redundante en los mismos
parrafos tocados (nunca cifras ni salvedades) y, como ultimo recurso, se compactan notas al
pie de las entradas `@online` nuevas. El commit del hash puede reflujar flotantes como en
c-187; se registra.

## Risks / Trade-offs

- [Una fuente de C2 no es verificable o la URL cambio] → se omite y se registra; el texto
  no cita lo que no se verifico.
- [Opitz y Burst o la fuente de Hawthorne no confirman lo que se les atribuye] → se elige
  otra candidata de D7 o se reformula sin cita, registrando la decision.
- [El cambio de PMLR a `@article` altera el orden o el formato de otras entradas] → se
  compara la lista impresa antes y despues (pdftotext) y `verify_citations.py` debe quedar
  en PASS; biber sin advertencias.
- [El diagrama de despliegue crece en altura al agregar las redes] → se simplifica el
  rotulo de red; la relacion alto/ancho no debe superar la previa en mas de un 5 %.
- [El verificador "afloja" la verificacion al ignorar la linea] → el modo `--estricto`
  conserva la comprobacion exacta y los avisos de desplazamiento quedan listados.
- [Filas marcadas SUPERADA ocultan una correccion perdida] → cada SUPERADA nombra el
  change que reescribio el parrafo y la fila nueva de ese change debe cubrir la misma
  recomendacion.
- [Las 118 paginas no se alcanzan] → recorte en los parrafos tocados; si aun asi no, se
  detiene antes del tag y se consulta al usuario.
- [Deriva de lineas entre el dictamen, la rama de c-187 y `main`] → anclas por etiqueta y
  texto.

## Migration Plan

Apply en el orden de `tasks.md` sobre una rama nueva desde `main` (con c-187 fusionado).
Compilacion en el entorno de registro: `MSYS_NO_PATHCONV=1 docker run --rm -v
"<paper>":/workdir texlive-thesis latexmk main.tex`; `verify_citations.py` PASS; resumen
de compilacion regenerado; `openspec validate --strict`. Release (orquestador): commit de
contenido, tag anotado `v1.2.12`, commit del hash (patron D7-A de c-187), `CHANGES.md`,
`engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` y PR (nunca push directo a
`main`). Rollback: revertir las fuentes de la tesis, el `.bib`, las figuras, los memos y los
dos scripts al commit previo; no hay datos que revertir.

## Open Questions

- **D3**: RESUELTA el 2026-11-08 por el usuario: opcion A, declarar la procedencia de las capturas en los pies de figura (no se recapturan).
- **C4**: grafia del apellido del primer autor, "Gomez" (portada, recomendada) o "Gómez"
  (bibliografia actual). Solo los autores pueden decidirlo.
- **D5**: resumen generado (A, por defecto) o des-ignorar `main.log` (B).
- **D8**: la tesis cita el precio de Vertex AI mientras el backend usa la Gemini API de
  Google AI; ¿se mantiene la fuente de precio o se cambia en un change posterior? (fuera del
  alcance de c-188; no bloquea).
- **D7**: si alguien del equipo tiene acceso al texto de Galup et al. (2009), citar la
  pagina en lugar de reformular.
