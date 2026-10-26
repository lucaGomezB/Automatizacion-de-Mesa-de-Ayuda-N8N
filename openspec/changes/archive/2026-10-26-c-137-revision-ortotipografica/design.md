## Context

El change atiende la recomendacion B14 del dictamen CONEAU sobre la v10 (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`, seccion 1, tercer defecto de forma, y B14): revision ortotipografica completa de las fuentes LaTeX, con atencion a las tildes diacriticas y a las palabras con tilde omitida (ver `proposal.md` - Why). Es documental: edita solo tildes, dieresis y eñe en la tesis, y agrega una herramienta de inventario con pruebas. Restricciones que condicionan el diseno:

- **Neutralidad**: ningun cambio de contenido, cifras, claves, rutas ni de las cinco cadenas canonicas (`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`, sin tildes por diseno). Presupuesto de 101 paginas; el change debe ser neutral en paginas.
- **Orden**: se aplica despues de todos los changes que editan prosa (c-130 a c-136, c-138, c-139) y antes de c-141, que integra y publica v1.2.0. Las cifras de linea base de este documento son informativas y se re-miden al aplicar.
- **Entorno**: el host no tiene TeX; se compila con la imagen Docker `texlive-thesis` (`paper/Dockerfile`). El arbol de trabajo en Windows tiene terminadores CRLF (`core.autocrlf=true`). El Python global (3.14) no trae `pytest`.

Estado verificado (solo lectura) sobre el arbol de trabajo de `ramagonzalo` (secciones identicas a `v1.1.1`, commit `4160d84`, salvo las dos lineas del hash del Anexo B agregadas por `e18b9c4`):

| Forma | Ocurrencias | Lectura en contexto | Correcciones |
|---|---|---|---|
| "hacía" | 4 | preposicion en los 4 casos (`02:84`, `10:12`, `10:38`, `11:8`) | 4 -> "hacia" |
| "fórmula" | 4 | 1 verbal (`02:44`, "se fórmula la instrucción"); 3 sustantivos correctos (`04:47`, `04:51` x2) | 1 -> "formula" |
| "continua" | 16 | 4 verbales (`01:10`, `06:40`, `06:50`, `08:54`); 12 adjetivos correctos ("mejora/integración/gestión/supervisión ... continua", "cuantitativa continua") | 4 -> "continúa" |
| "esta"/"este" verbales | 4 | `06:40` ("el indicador esta activo", "cuando no lo esta,", "no este vacía"), `07:32` ("la grabación esta acotada") | 4 -> "está"/"esté" |
| heterogeneas, erronea/erroneas, antiguedad, perimetro, inequivocos, enganosa, simultanea, aquéllas, asigno, gestiono | 2, 3, 2, 2, 2, 1, 1, 1, 1, 1 | en contexto solo admiten la forma corregida ("aquéllas" es determinante: "aquéllas organizaciones"); la herramienta igual clasifica "simultanea", "asigno" y "gestiono" como `AMBIGUO` porque la forma sin tilde existe como verbo | 16 |
| Fuera de la muestra: multiples, alla ("más alla"), escaner, "por si mismo" | 6, 3, 1, 1 | idem ("por si mismo" -> pronombre "sí") | 11 |
| **Total en `sections/`** | | | **40** |

Hallazgos adicionales fuera de `sections/`: `paper/main.tex` declara "Indice general", "Indice de tablas", "Indice de figuras" y el titulo "Referencias bibliograficas"; `paper/preambles/preamble.tex` declara el encabezado de pagina "AUTOMATIZACION DE MESA DE AYUDA" (visible en casi todas las paginas), la cadena `bibliography = {Referencias bibliograficas}` y los metadatos `pdftitle`/`pdfkeywords` sin tildes; `Bibliography_base.bib` imprime "Documentacion tecnica [oficial]" (4 notas), "Documentacion de la plataforma ..." (3) y "Borrador de la 3ra edicion" (1). Ademas, 5 pasajes enumeran los "sectores canonicos" con tildes ("Seguridad Informática", "Soporte Técnico Hardware/Software": `01-introduccion.tex:48,72`, `04-marco-metodologico.tex:36,45`, `05-arquitectura.tex:100`; 15 menciones), mientras la propia tesis define esos strings como exactos y sin tildes (`05-arquitectura.tex:84`, `12-anexos.tex:79`) y los usa asi en resultados (`07-resultados.tex`).

Discrepancias con la muestra del dictamen: el dictamen informa 4 "fórmula" verbales y 11 "continua" verbales; la verificacion encuentra 1 y 4. Por eso los criterios de aceptacion se formulan por categoria gramatical y no por conteo bruto (un reemplazo ciego de las 16 "continua" o de las 4 "fórmula" introduciria 15 erratas nuevas).

Causa raiz (evidencia de `git log -S` y lectura de los scripts): "se fórmula" entra con el commit `f0546ec` (c-106, normalizacion de acentos con `acentuar_tesis_v9.py`, cuyo lexico incluye `fórmula`); los 4 "hacía" y "aquéllas" existen desde `e2bbd3f`, el mismo commit que agrega `acentuar_tesis.py`, cuyo diccionario mapea incondicionalmente `hacia`->`hacía` y `aquellas`->`aquéllas`. c-80 (F1) ya tuvo que revertir 50 erratas de formas que ese mismo diccionario produce ("desarrolló", "completó", "aquéllos").

## Goals / Non-Goals

**Goals:**

- Dejar la tesis sin tildes faltantes ni improcedentes en prosa, con una revision completa y reproducible, no limitada a la muestra del dictamen.
- Separar lo corregible por script (inequivoco) de lo que exige juicio gramatical (homografos), con cada decision humana justificada y registrada.
- Garantizar por construccion la neutralidad del cambio (diff puramente diacritico) y verificarla (cadenas canonicas, cifras, claves, paginas, citas).
- Dejar una pasada corta ejecutable por c-141 que detecte erratas reintroducidas por ediciones tardias.
- Neutralizar la causa raiz: que las utilidades previas no vuelvan a aplicarse sobre la tesis.

**Non-Goals:**

- No se reescribe prosa ni se cambia estilo, puntuacion, comillas, rayas, mayusculas ni espaciado: solo diacriticos (tildes, dieresis, eñe). Una errata no diacritica que aparezca durante la revision se anota en el registro como hallazgo para c-141, sin corregirla aqui.
- No se tocan las ocurrencias existentes de las cinco cadenas canonicas, los identificadores de datos (nombres de columnas y campos, por ejemplo `telefono`), el contenido de `lstlisting`, `\texttt`, URLs, claves de cita ni labels.
- No se corrigen citas textuales de incidentes del corpus (`07-resultados.tex`) ni las cadenas de busqueda en ingles del protocolo de revision (`03-estado-del-arte.tex`): se reportan y se resuelven como `mantener`.
- No se editan claves ni metadatos bibliograficos (autores, anos, DOI, URL): eso es de c-139. Solo tildes del texto impreso en espanol de `note` (y la etiqueta de version del titulo de `Gomez2026_repositorio`, por decision registrada).
- No se edita el dictamen auditado ni las figuras (texto dentro de imagenes).
- No se regeneran los extractos heredados `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt`; solo `tesis_para_agente.md`, que es el render de referencia.
- No se agrega la prueba de la herramienta a la CI (`.github/workflows/ci.yml`): queda como mejora posible de un change tecnico.
- No se publica release ni se crea tag: es de c-141.

## Decisions

### D1 - Herramienta nueva `revision_tildes.py`; no reutilizar `acentuar_tesis*.py`

Se escribe `docs/Tesis/v10 (IA)/revision_tildes.py` (junto a `verify_citations.py` y `build_tesis_para_agente.py`), un unico archivo con biblioteca estandar. Los lexicos de las utilidades previas se aprovechan solo como datos semilla, depurados, nunca su aplicacion ciega.

Motivo, verificado sobre el texto actual:

- `acentuar_tesis.py` (v8) corrige de forma incondicional homografos: `hacia`->`hacía`, `formula`->`fórmula`, `aquellas`/`aquellos`->`aquéll-`, `completo`->`completó`, `desarrollo`->`desarrolló`, `practica`->`práctica`, `critica`->`crítica`. Escribe por defecto (el dry-run es opcional), crea `.tex.bak`, procesa comentarios y no protege las cadenas canonicas (sobreviven solo porque la expresion es sensible a mayusculas). Simulado en memoria sobre el texto actual de v10 (sin escribir), introduciria 47 erratas nuevas (13 "hacía", 17 "completó", 11 "desarrolló", 6 "aquéllos").
- `acentuar_tesis_v9.py` (c-106) es mejor (protege las cadenas canonicas, excluye pares ambiguos, dry-run por defecto) pero mantiene `formula`->`fórmula` (origen de "se fórmula"), `fijo`->`fijó` (la misma simulacion muestra que su unico cambio hoy seria "tamaño fijo" -> "tamaño fijó", una errata nueva) y `practica`->`práctica`; su lexico no cubre ninguna de las erratas de B14 salvo las ya corregidas; su regla de sufijo `-sion`->`-sión` no excluye el Abstract en ingles (hoy no contiene palabras en `-sion`, pero las ediciones del resumen y del abstract previstas por otros changes de la familia podrian introducir "decision" o "precision"); no distingue tablas ni citas; su `--diff` escribe en una ruta fija `/tmp/opencode/` y su directorio objetivo esta fijado a `v9 (IA)`.

**Alternativas consideradas:** (a) re-ejecutar `acentuar_tesis_v9.py` repuntado a v10 y revisar a mano el resultado, como sugiere el dictamen: se descarta porque reintroduce "fórmula" y "fijó" y no detecta las erratas de B14 ni las tildes improcedentes; (b) revision exclusivamente manual: se descarta porque no es reproducible ni deja una pasada corta para c-141; (c) corrector externo (hunspell, LanguageTool): se descarta por agregar una dependencia y la descarga de diccionarios, por no entender LaTeX y por su bajo rendimiento con homografos diacriticos.

### D2 - Clasificacion `INEQUIVOCO` / `AMBIGUO` y fuentes de candidatos

Cada candidato se clasifica:

- `INEQUIVOCO`: la forma encontrada no es palabra valida en el contexto de la tesis ("erronea", "heterogeneas", "antiguedad", "perimetro", "inequivocos", "enganosa", "multiples", "alla", "escaner", singulares en `-cion`/`-sion` en espanol), o la ortografia vigente no admite su tilde (demostrativos con tilde, "sólo"). Se corrige por script.
- `AMBIGUO`: ambas formas existen y la eleccion depende de la categoria gramatical: pares diacriticos ("esta"/"está", "este"/"esté", "si"/"sí", "aun"/"aún", "mas"/"más", interrogativos), "hacia"/"hacía", "formula"/"fórmula", "continua"/"continúa", preteritos homografos de presente o sustantivo ("asigno"/"asignó", "gestiono"/"gestionó", "registro"/"registró"), adjetivos homografos de verbo ("valida"/"válida", "publica"/"pública", "simultanea"/"simultánea"). Se resuelve a mano.

Fuentes de candidatos: (1) un lexico curado `sin tilde -> con tilde`, con la clase de cada entrada; (2) la regla morfologica de singulares `-cion`/`-sion` (no plurales), desactivada en `\emph`/`\textit` y en zonas en ingles; (3) autoconsistencia del corpus: un token sin tilde cuya variante con tilde aparece en otra parte del corpus se informa como `AMBIGUO` (captura generica de lo que el lexico no cubra); (4) deteccion de tildes improcedentes ("hacía", "fórmula", demostrativos con tilde, "sólo").

Para que la revision humana sea abordable sin perder recall en las palabras frecuentes (hay unas 158 "como" y 69 "esta" en la linea base), los pares frecuentes se informan solo ante senales de contexto: "esta"/"este" seguidos de participio, adjetivo de estado, preposicion o signo de puntuacion, o precedidos de "no"/"lo"/"ya"; interrogativos dentro de signos de interrogacion o exclamacion o tras verbos de conocimiento o comunicacion; "continua" salvo en colocaciones adjetivales conocidas ("mejora", "integración", "gestión", "supervisión", "variable", "cuantitativa" + "continua"); "fórmula" cuando no la precede determinante, articulo o preposicion, y "formula" cuando si; "hacia" tras clitico o pronombre sujeto; sustantivos homografos de preterito ("registro", "desarrollo", "promedio") solo tras el clitico "se"; "si" ante "mismo/a/os/as" o tras "por/de/en/entre/para" seguido de puntuacion. Los pares raros ("hacía", "aun"/"aún", preteritos curados como "asigno"/"gestiono", incluso tras "se") se informan siempre; los adjetivos homografos de verbo ("valida", "publica", "simultanea") se informan siempre salvo tras el clitico "se", que fija la lectura verbal ("se valida"). La opcion `--todos` desactiva las senales para un barrido exhaustivo de los pares.

**Alternativas consideradas:** (a) solo lexico, sin senales: obliga a revisar cientos de "como", "que" y "esta" correctos; se descarta; (b) limitar la revision a la lista del dictamen: se descarta porque B14 pide una revision completa y la linea base ya muestra 11 erratas fuera de la muestra.

### D3 - Zonas protegidas, zonas de solo reporte y prosa

- **Protegidas (no se informan ni se modifican):** las cinco cadenas canonicas exactas; argumentos de `\texttt`, `\url`, `\path` y destino de `\href`; claves de `\label`, `\ref`, `\autoref`, `\cref`, `\eqref`, `\pageref` y de comandos de cita; rutas de `\input`, `\include`, `\includegraphics`; entornos `lstlisting`, `verbatim`, `minted`; `\verb`, `\lstinline`; matematica; comentarios; nombres de comandos y especificaciones de entorno; el Abstract en ingles (desde `\section*{Abstract}` hasta el fin de `00-resumen.tex`); identificadores de repositorio en prosa (rutas como `docs/Tesis/`, nombres con `\_`).
- **Solo reporte (nunca se corrigen por script; decision manual registrada):** cuerpo de entornos `tabular` (zona `tabla`), porque mezcla identificadores de datos, etiquetas canonicas de la matriz de confusion, expansiones en ingles del glosario y prosa; texto entre comillas ``...'' o "..." (zona `cita`), porque reproduce incidentes del corpus o cadenas de busqueda en ingles. En tablas sin cadenas canonicas se admite la correccion manual de una palabra de prosa, sin tocar identificadores. Las tablas que contienen alguna de las cinco cadenas canonicas (matriz de confusion, metricas por clase, tabla de variables, modelo de datos) no se editan en esta revision: sus candidatos se registran como hallazgos para el usuario, con la unica excepcion de la unificacion de nombres de sector si el usuario la confirma (D7). En la linea base los candidatos en tablas son un identificador y un termino en ingles: `telefono` (columna del modelo de datos, `05-arquitectura.tex`) y "Version" (expansion "Multi-Version" del glosario), ambos `mantener`.
- **Prosa:** el resto, incluidos los argumentos de comandos portadores de texto (`\section`, `\caption`, `\textbf`, `\emph`, `\item`, `\footnote`).

**Alternativa considerada:** excluir todas las tablas del inventario (no informarlas). Se descarta porque ocultaria erratas reales en celdas de prosa; en su lugar las tablas se informan siempre, nunca se corrigen por script, y las que contienen cadenas canonicas tampoco se editan a mano, lo que cumple la regla de no tocar las cadenas canonicas dentro de tablas.

### D4 - Aplicacion en dos pasos con registro de decisiones en TSV

Paso 1: `--diff` (revision humana del diff) y `--apply`, que escribe solo `INEQUIVOCO` en `prosa`. Paso 2: cada candidato `AMBIGUO`, `tabla` o `cita` se decide uno por uno, se corrige a mano si corresponde y se registra en `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv` con `archivo`, `token`, `contexto`, `decision` (`corregir` | `mantener`), `forma_final` y `justificacion` (categoria gramatical en contexto). La clave de cada fila es (archivo, token, contexto normalizado: hasta cinco palabras a cada lado dentro de la linea, sin comandos LaTeX), independiente del numero de linea. La escritura usa `open(..., encoding="utf-8", newline="")` para preservar CRLF/LF y no crea respaldos.

**Alternativas consideradas:** marcas en comentarios LaTeX junto a cada token revisado (ensucian las fuentes); registro por numero de linea (se rompe con cualquier edicion previa); tabla Markdown (parseo fragil con barras verticales). Se elige TSV por ser legible en el diff y trivial de leer desde `--check`.

### D5 - Pasada corta (`--check`) e invariante diacritico (`--base`)

- `--check` termina con 0 si no quedan `INEQUIVOCO` en `prosa` y todo candidato restante tiene decision `mantener` en el registro; si no, termina con 1 y lista lo pendiente. Protocolo para c-141 tras cualquier edicion tardia: ejecutar `--check`; si falla, `--diff`/`--apply` para lo inequivoco, decidir y registrar lo ambiguo, y repetir hasta 0. Si c-141 edita `main.tex`, el preambulo o el `.bib`, repite ademas los controles por `grep` del bloque de cadenas visibles.
- `--base <dir>` compara cada archivo con su homonimo en `<dir>` y exige igual cantidad de lineas y que cada linea modificada sea igual a la previa tras quitar diacriticos (NFD sin marcas de acento agudo, dieresis y virgulilla) y normalizar los escapes LaTeX de acento (`{\'o}`, `\'{o}`, `\'o`, `\~n`, `\"u`). Con `--archivos` se aplica tambien a `main.tex`, el preambulo y el `.bib`. Esta unica comprobacion garantiza que no cambiaron cifras, claves, rutas ni palabras.

**Alternativas consideradas:** verificar por separado cifras, labels y citas (queda subsumido y es mas debil que el invariante); confiar en la lectura del `git diff` (no es verificable).

### D6 - Cadenas visibles fuera de `sections/` y bibliografia: edicion manual

Las 8 lineas de `main.tex` y del preambulo y las 8 notas del `.bib` se corrigen a mano: el preambulo es casi todo opciones y comandos (el script daria falsos positivos) y son pocas lineas. En el `.bib` se usa la notacion de escape que el archivo ya emplea (hoy no contiene acentos UTF-8 crudos), por ejemplo `Documentaci{\'o}n t{\'e}cnica oficial`. La etiqueta "(Version 1.1.1)" del titulo de `Gomez2026_repositorio` se registra como decision manual con recomendacion `corregir` a "Versi{\'o}n" (titulo en espanol, convencion APA en espanol) y se deja nota para que c-141 conserve la tilde al actualizar el numero de version. La mayuscula acentuada del encabezado de pagina y de "Índice" esta soportada por la fuente (la portada ya usa "TECNOLÓGICA").

**Alternativa considerada:** pasar estos archivos por la herramienta con `--apply`. Se descarta por el riesgo de tocar opciones de paquetes; la herramienta puede usarse sobre ellos solo en modo inventario como control.

### D7 - Coherencia de los nombres de sector (OQ1)

Se recomienda unificar las 15 menciones con tilde de los 5 pasajes que enumeran los "sectores canonicos" a la cadena canonica exacta: la propia tesis define esos strings como exactos y sin tildes (`05-arquitectura.tex:84`, `12-anexos.tex:79`) y los usa asi en resultados; el cambio es diacritico y neutral en paginas. Por tocar el dominio de las cadenas canonicas, se aplica solo con confirmacion del usuario; si no la hay al momento del apply, los pasajes quedan como estan y la convencion (nombre legible con tildes en prosa, cadena canonica como dato del clasificador) se documenta en el registro como inconsistencia conocida.

**Alternativas consideradas:** conservar la forma con tildes (legible) sin documentar (deja una contradiccion visible para el tribunal); escribir los nombres con `\texttt` (cambia tipografia y ancho, no es diacritico y arriesga paginas).

### D8 - Politica ortografica de referencia

Ortografia de la lengua espanola (RAE-ASALE, 2010): sin tilde en el adverbio "solo" ni en los demostrativos (el corpus ya cumple: 14 "solo", 0 "sólo"); tilde diacritica en monosilabos y en interrogativos y exclamativos segun la norma; las mayusculas llevan tilde; las variantes admitidas ("período"/"periodo") se uniforman a la forma mayoritaria del corpus (hoy "período", sin variantes). Los preteritos de tercera persona llevan tilde ("asignó"); los preteritos fuertes no ("hizo", "propuso", "obtuvo", "produjo"), y se excluyen de la regla del clitico "se".

### D9 - Pruebas y TDD

`docs/Tesis/v10 (IA)/test_revision_tildes.py` junto al script (precedente: `scripts/preflight/test_*.py`), con fixtures LaTeX en linea y una prueba de regresion que copia verbatim las oraciones de la linea base (las 40 erratas y los usos legitimos: 12 "continua" adjetivales, 3 "fórmula" nominales, "aun" concesivo, "valida"/"publica" verbales). Hay una prueba por escenario del spec: zonas protegidas, clasificacion, senales, tablas y citas, mayusculas, CRLF, idempotencia, ausencia de `.bak`, registro de decisiones robusto a desplazamientos, codigos de salida de `--check`, invariante de `--base` (incluidos escapes del `.bib`), determinismo y lexico sin correcciones incondicionales de homografos. Se ejecuta con `python -m pytest "docs/Tesis/v10 (IA)/test_revision_tildes.py" -q`; si `pytest` no esta disponible se instala en un entorno virtual temporal fuera del repositorio. Si la ejecucion real detecta un falso negativo o positivo, primero se agrega la prueba que lo reproduce y luego se ajusta el lexico o la senal.

### D10 - Orden de aplicacion y deprecacion de las utilidades previas

- El bloque de la herramienta no toca la tesis y puede implementarse en paralelo con c-130 a c-139. Los bloques que editan la tesis esperan a que esos changes esten aplicados (y c-140, si llegara a editar prosa); al iniciar se registra el commit base y se re-mide la linea base.
- `acentuar_tesis.py` y `acentuar_tesis_v9.py` reciben un aviso "DEPRECADO (c-137)" en su docstring de cabecera con el motivo (correcciones incondicionales de homografos que introdujeron erratas) y la herramienta que los reemplaza, sin cambios de logica. Se descarta borrarlos (trazabilidad de c-80 y c-106, citados en changes archivados) y corregir sus diccionarios (duplicaria herramientas y apuntan a v8/v9).
- En el requisito modificado "Acentuación normalizada del manuscrito" se elimina la linea residual "no se presentan como controles implementados en el repositorio" del escenario "Sin residuos de la herramienta", que no guarda relacion con el requisito.

## Risks / Trade-offs

- **[Falsos negativos por las senales de contexto]** -> la prueba de regresion exige detectar las 40 erratas de la linea base; durante el apply se hace un barrido `--todos` de los pares de mayor riesgo ("esta"/"este", "continua", "fórmula", "hacía", "si"/"sí") y se deja constancia en el registro.
- **[Falsos positivos]** -> se resuelven como `mantener` con justificacion (costo bajo); los recurrentes se corrigen en el lexico o la senal con prueba previa.
- **[Sobrecorreccion de cadenas canonicas o identificadores]** -> zonas protegidas con prueba, tablas y citas sin correccion automatica, control de conteo de las cadenas canonicas e invariante diacritico.
- **[Ediciones tardias reintroducen erratas, incluida prosa redactada sin tildes por agentes que siguen la convencion de artefactos sin tildes]** -> `--check` como pasada corta de c-141; la regla de sufijos y el lexico detectan prosa sin acentuar en general, no solo la muestra.
- **[Conflictos de merge con los changes de prosa]** -> los bloques de edicion se aplican despues de ellos; el registro usa claves de contexto, no numeros de linea.
- **[Terminadores de linea y codificacion en Windows]** -> lectura y escritura con `newline=""` y UTF-8 sin BOM; prueba con fixture CRLF.
- **[Cambio en el conteo de paginas por cortes de linea]** -> los cambios no alteran la cantidad de caracteres de cada palabra; se compila antes y despues con el mismo entorno y se compara; si difiere, se localiza el parrafo afectado antes de cerrar.
- **[Advertencia de altura de encabezado por la mayuscula acentuada]** -> se revisa el log; la portada ya usa mayusculas acentuadas con la misma fuente; si aparece la advertencia se documenta y se evalua sin alterar el diseno de pagina.
- **[Re-ejecucion accidental de las utilidades previas]** -> aviso DEPRECADO en ambas; sus rutas siguen fijadas a v8/v9.
- **[El dictamen y la verificacion no coinciden en los conteos]** -> criterios por categoria gramatical; la discrepancia se documenta en el registro.
- **[OQ1 sin respuesta al momento del apply]** -> se bloquea solo esa tarea; por defecto no se unifica y se documenta.

## Migration Plan

1. (En paralelo, sin tocar la tesis) Implementar `revision_tildes.py` con TDD estricto y dejar sus pruebas en verde.
2. Esperar a que c-130, c-131, c-132, c-133, c-134, c-135, c-136, c-138 y c-139 (y c-140 si edita prosa) esten aplicados; verificar arbol limpio en `docs/Tesis/v10 (IA)/`.
3. Linea base: registrar el commit base, compilar con `texlive-thesis`, registrar paginas, conteos de las cinco cadenas canonicas y de los usos legitimos, y copiar al scratchpad las secciones, `main.tex`, el preambulo y el `.bib` previos.
4. Inventario sin efectos; paso 1 (`--diff`, revision, `--apply`); paso 2 (ambiguos, tablas y citas uno por uno, con registro); barrido `--todos` de los pares de riesgo.
5. Cadenas visibles de `main.tex` y el preambulo, notas del `.bib` y, segun la respuesta a OQ1, nombres de sector.
6. Verificacion: `--base` (invariante diacritico), controles por `grep`, conteo de cadenas canonicas, compilacion y paginas, Biber, `verify_citations.py`, regeneracion de `tesis_para_agente.md` y `--check` en 0.
7. Registro B14 en `dictamen-correcciones.md` y aviso DEPRECADO en las utilidades previas.
8. Entrega a c-141: la pasada corta es `python "docs/Tesis/v10 (IA)/revision_tildes.py" --check`.

Rollback: `git checkout <base> -- "docs/Tesis/v10 (IA)/paper/sections" "docs/Tesis/v10 (IA)/paper/main.tex" "docs/Tesis/v10 (IA)/paper/preambles/preamble.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib"`, recompilar y regenerar `tesis_para_agente.md`. La herramienta, sus pruebas y el registro pueden quedar (no modifican nada por defecto).

## Open Questions

- **OQ1 (bloquea solo la tarea de nombres de sector):** ¿se unifican a la cadena canonica sin tildes las 15 menciones con tilde de los sectores en los 5 pasajes que los presentan como "sectores canonicos" (`01-introduccion.tex:48,72`, `04-marco-metodologico.tex:36,45`, `05-arquitectura.tex:100`)? Recomendacion: si (D7). Sin respuesta: no se unifica y se documenta.
- **OQ2 (no bloqueante):** ¿se agrega una fe de errata al dictamen auditado sobre los conteos de "fórmula" (1 verbal, no 4) y "continua" (4 verbales, no 11), como hizo c-121 con la REC 4? Recomendacion: no editar el dictamen; consignar la discrepancia solo en `dictamen-correcciones.md`.
