## ADDED Requirements

### Requirement: Inventario reproducible de tildes de la tesis

El repositorio SHALL incluir `docs/Tesis/v10 (IA)/revision_tildes.py`, implementado solo con la biblioteca estandar de Python y cubierto por pruebas automatizadas en `docs/Tesis/v10 (IA)/test_revision_tildes.py`. Ejecutado sin opciones, el script MUST NOT modificar ningun archivo y SHALL emitir un inventario determinista de candidatos de tilde faltante o improcedente en `paper/sections/*.tex`, con archivo, linea, columna, token, forma sugerida, clase y zona. La clase SHALL ser `INEQUIVOCO` cuando la forma encontrada no es una palabra valida del espanol en ese contexto (por ejemplo "erronea", "multiples") o cuando la ortografia vigente no admite la tilde (demostrativos y adverbio "solo" con tilde), y `AMBIGUO` cuando ambas formas existen (pares diacriticos como "esta"/"está", "hacia"/"hacía", y homografos verbo/sustantivo/adjetivo como "formula"/"fórmula", "continua"/"continúa", "asigno"/"asignó"). La zona SHALL ser `prosa`, `tabla` (cuerpo de entornos `tabular`) o `cita` (texto entre comillas). El inventario MUST excluir las zonas protegidas: las cinco cadenas canonicas exactas (`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`), los argumentos de `\texttt`, `\url`, `\path`, el destino de `\href`, las claves de `\label`, `\ref`, `\autoref`, `\cref`, `\eqref`, `\pageref` y de los comandos de cita, las rutas de `\input`, `\include` e `\includegraphics`, los entornos `lstlisting`, `verbatim` y `minted`, `\verb` y `\lstinline`, la matematica, los comentarios, los nombres de comandos LaTeX y el resumen en ingles (desde `\section*{Abstract}` hasta el fin de `00-resumen.tex`).

#### Scenario: Ejecucion por defecto sin efectos

- **WHEN** se ejecuta `python "docs/Tesis/v10 (IA)/revision_tildes.py"` sin opciones
- **THEN** ningun archivo del repositorio cambia (`git status --short` es identico antes y despues)
- **AND** la salida lista los candidatos ordenados por archivo, linea y columna, y dos ejecuciones consecutivas producen exactamente la misma salida

#### Scenario: Zonas protegidas excluidas

- **WHEN** el inventario procesa un fragmento que contiene `Seguridad Informatica`, `\texttt{categoria}`, `\label{sec:introduccion}`, `\url{https://example.org/version}`, un entorno `lstlisting` con "JSON invalido", una expresion matematica, un comentario con "erronea" y un Abstract en ingles con "version"
- **THEN** no reporta ningun candidato dentro de esas zonas
- **AND** ninguna de las cinco cadenas canonicas recibe una sugerencia de tilde

#### Scenario: Clasificacion de candidatos

- **WHEN** el inventario procesa en prosa "derivación erronea", "tareas heterogeneas", "multiples canales" y "más alla del caso"
- **THEN** los reporta como `INEQUIVOCO` con las sugerencias "errónea", "heterogéneas", "múltiples" y "allá"
- **AND** reporta como `AMBIGUO` "sesgos hacía una clase", "la forma en que se fórmula la instrucción", "el flujo continua automáticamente", "el indicador esta activo", "no este vacía" y "La distribución de roles asigno la coordinación"

#### Scenario: Usos legitimos sin reporte

- **WHEN** el inventario procesa en prosa "mejora continua", "integración continua", "mediante la fórmula clásica", "el registro manual" y "derivación de incidentes hacia los sectores"
- **THEN** no reporta ningun candidato en esos fragmentos

#### Scenario: Deteccion completa de la linea base

- **WHEN** se ejecuta la prueba de regresion con las oraciones de la linea base v1.1.1 (las erratas de la muestra del dictamen y los hallazgos adicionales "multiples", "alla", "escaner" y "por si mismo")
- **THEN** cada errata se reporta con la clase esperada
- **AND** ningun uso legitimo incluido en la misma prueba (adjetivos "continua", sustantivos "fórmula", "aun" con valor de "incluso", verbos "valida" y "publica") recibe una correccion automatica

### Requirement: Aplicacion en dos pasos de las correcciones de tildes

`revision_tildes.py --diff` SHALL mostrar, sin escribir, el diff unificado de las correcciones `INEQUIVOCO` en zona `prosa`, y `revision_tildes.py --apply` SHALL escribir exactamente esas correcciones. Los candidatos `AMBIGUO` y los candidatos en zonas `tabla` o `cita` MUST NOT corregirse automaticamente, y ningun candidato con decision `mantener` en el registro de decisiones MUST aplicarse. La aplicacion SHALL preservar la capitalizacion (inicial mayuscula y todo mayusculas), la codificacion UTF-8 y los terminadores de linea (CRLF o LF) de cada archivo, MUST NOT crear archivos de respaldo (`.bak`) y SHALL ser idempotente.

#### Scenario: Diff revisable sin escritura

- **WHEN** se ejecuta `revision_tildes.py --diff`
- **THEN** la salida es un diff unificado que contiene solo correcciones `INEQUIVOCO` en zona `prosa`
- **AND** ningun archivo cambia

#### Scenario: Aplicacion limitada a inequivocos

- **WHEN** se ejecuta `--apply` sobre un fragmento con "derivación erronea" en prosa, "sesgos hacía una clase" en prosa y la celda de tabla `telefono`
- **THEN** solo "erronea" pasa a "errónea"
- **AND** las lineas con "hacía" y con `telefono` quedan identicas byte a byte

#### Scenario: Preservacion de forma

- **WHEN** se ejecuta `--apply` sobre un archivo con terminadores CRLF que contiene "Erronea" y "ERRONEA"
- **THEN** el resultado contiene "Errónea" y "ERRÓNEA"
- **AND** los terminadores CRLF y el resto de los bytes del archivo no cambian, y no se crea ningun archivo `.bak`

#### Scenario: Idempotencia

- **WHEN** se ejecuta `--apply` por segunda vez sobre el mismo arbol
- **THEN** ningun archivo cambia
- **AND** `--diff` no muestra ninguna correccion pendiente

### Requirement: Revision humana de homografos con registro de decisiones

Cada candidato que no se corrige automaticamente (`AMBIGUO`, o ubicado en zona `tabla` o `cita`) SHALL resolverse uno por uno y registrarse en `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv` (UTF-8, separado por tabuladores) con archivo, token, contexto, decision (`corregir` o `mantener`), forma final y justificacion basada en la categoria gramatical del token en su contexto. Las decisiones SHALL seguir la ortografia vigente (RAE-ASALE, 2010): "hacia" preposicion sin tilde; "formula" verbo sin tilde y "fórmula" sustantivo con tilde; "continúa" verbo con tilde y "continua" adjetivo sin tilde; "está"/"esté" formas de "estar" con tilde y "esta"/"este" determinantes sin tilde; preteritos de tercera persona con tilde ("asignó", "gestionó"); "aún" (todavia) con tilde y "aun" (incluso) sin tilde; "sí" pronombre con tilde; demostrativos y adverbio "solo" sin tilde. Los identificadores de datos (nombres de columnas, campos o valores literales) y las citas textuales de incidentes del corpus MUST conservarse tal como estan. Las tablas que contienen alguna de las cinco cadenas canonicas MUST NOT editarse en esta revision, salvo la unificacion de nombres de sector confirmada por el usuario; sus candidatos SHALL registrarse como hallazgos.

#### Scenario: Cada candidato con decision registrada

- **WHEN** se cruza el inventario final con el registro de decisiones
- **THEN** todo candidato no automatico tiene una fila con decision y justificacion no vacia
- **AND** toda fila con decision `corregir` esta aplicada en el texto

#### Scenario: Homografos resueltos por categoria gramatical

- **WHEN** se leen los pasajes de la linea base que contenian "sesgos hacía una clase", "se fórmula la instrucción", "el flujo continua automáticamente", "el indicador esta activo", "cuando no lo esta,", "no este vacía", "la grabación esta acotada", "roles asigno" y "se gestiono"
- **THEN** se leen "sesgos hacia una clase", "se formula la instrucción", "el flujo continúa automáticamente", "el indicador está activo", "cuando no lo está,", "no esté vacía", "la grabación está acotada", "roles asignó" y "se gestionó"
- **AND** "mejora continua", "integración continua" y "mediante la fórmula clásica" permanecen sin cambios

#### Scenario: Datos y citas literales preservados

- **WHEN** se revisan las celdas de tabla que contienen identificadores (por ejemplo la columna `telefono` del modelo de datos) y las citas de incidentes del corpus entre comillas
- **THEN** no se agrega ni se quita ninguna tilde en identificadores ni en citas
- **AND** cada uno de esos candidatos consta en el registro con decision `mantener` y su justificacion

### Requirement: Ausencia de las erratas de tildes senaladas por el dictamen v1.1.0

Tras la revision, `docs/Tesis/v10 (IA)/paper/sections/*.tex` SHALL contener cero ocurrencias, fuera de zonas protegidas, de: "hacía" con valor de preposicion; "fórmula" con valor verbal; "continua" con valor verbal; "esta" y "este" con valor de verbo "estar"; "heterogeneas", "erronea", "erroneas", "antiguedad", "perimetro", "inequivocos", "enganosa", "simultanea" (adjetivo), "aquéllas", "asigno" y "gestiono" (preteritos); y de los hallazgos adicionales "multiples", "alla", "escaner" y "por si mismo". Los criterios de aceptacion SHALL expresarse por categoria gramatical y no por conteo bruto: los usos adjetivales de "continua" y nominales de "fórmula" MUST conservarse.

#### Scenario: Formas inequivocas en cero

- **WHEN** se ejecuta `grep -o -w` de cada una de las formas "heterogeneas", "erronea", "erroneas", "antiguedad", "perimetro", "inequivocos", "enganosa", "aquéllas", "asigno", "gestiono", "multiples", "alla" y "escaner" sobre `paper/sections/*.tex`
- **THEN** cada conteo es 0
- **AND** si una edicion previa a la pasada introdujo alguna de esas formas dentro de una zona protegida (por ejemplo un termino en ingles o un identificador), la ocurrencia consta en el registro de decisiones con decision `mantener` y su justificacion

#### Scenario: Homografos de la muestra resueltos

- **WHEN** se buscan en `paper/sections/*.tex` los contextos de la linea base "sesgos hacía", "concreta hacía", "incidentes hacía", "textuales hacía", "se fórmula", "incidentes continua", "flujo continua", "experto continua", "indicador esta", "lo esta,", "no este vacía", "grabación esta acotada", "presencia simultanea" y "por si mismo"
- **THEN** cada busqueda devuelve 0 ocurrencias

#### Scenario: Usos legitimos preservados

- **WHEN** se cuentan "mejora continua", "integración continua" y "la fórmula" antes y despues de la pasada
- **THEN** los conteos posteriores son iguales a los previos a la pasada

#### Scenario: Herramienta sin pendientes

- **WHEN** se ejecuta `python "docs/Tesis/v10 (IA)/revision_tildes.py" --check` al cerrar la pasada
- **THEN** el codigo de salida es 0

### Requirement: Cadenas visibles y bibliografia impresa acentuadas

Las cadenas visibles en el PDF que se definen fuera de `paper/sections/` SHALL llevar sus tildes: en `paper/main.tex`, "Índice general", "Índice de tablas", "Índice de figuras" y el titulo "Referencias bibliográficas" de `\printbibliography`; en `paper/preambles/preamble.tex`, el encabezado de pagina "AUTOMATIZACIÓN DE MESA DE AYUDA", la cadena `bibliography` de `\DefineBibliographyStrings` ("Referencias bibliográficas") y los metadatos `pdftitle` y `pdfkeywords`. En `Bibliography_base.bib`, el texto impreso en espanol de los campos `note` SHALL acentuarse con la notacion de escape LaTeX que ya usa el archivo (por ejemplo `Documentaci{\'o}n t{\'e}cnica oficial`); las claves, autores, anos, DOI, URL y demas metadatos MUST NOT cambiar. Los comentarios LaTeX quedan fuera de alcance.

#### Scenario: Encabezados y titulos con tildes

- **WHEN** se buscan "Indice general", "Indice de tablas", "Indice de figuras", "Referencias bibliograficas" y "AUTOMATIZACION" en las lineas no comentadas de `paper/main.tex` y `paper/preambles/preamble.tex`
- **THEN** no queda ninguna ocurrencia
- **AND** el indice general del PDF compilado muestra "Referencias bibliográficas" y el encabezado de pagina muestra "AUTOMATIZACIÓN DE MESA DE AYUDA"

#### Scenario: Metadatos del PDF con tildes

- **WHEN** se leen `pdftitle` y `pdfkeywords` en `paper/preambles/preamble.tex`
- **THEN** contienen "Automatización", "automatización", "clasificación" y "español"

#### Scenario: Notas de la bibliografia con tildes y metadatos intactos

- **WHEN** se buscan "Documentacion", "tecnica" y "edicion" en los campos `note` de `Bibliography_base.bib` y se compara el conjunto de claves `@tipo{clave` con el previo a la pasada
- **THEN** no queda ninguna ocurrencia y el conjunto de claves es identico
- **AND** `verify_citations.py` reporta PASS y el registro de Biber no contiene advertencias ni errores

### Requirement: Coherencia de los nombres de sector con su definicion canonica

Las menciones de los cinco sectores que la tesis presenta como "sectores canonicos" SHALL escribirse con la cadena canonica exacta, sin tildes, que la propia tesis define como string del clasificador (`05-arquitectura.tex`, `12-anexos.tex`), salvo que el usuario decida conservar en esos pasajes la forma legible con tildes; en ese caso la convencion y los pasajes afectados SHALL constar en el registro de la revision. En cualquiera de los dos casos, las ocurrencias previas de las cinco cadenas canonicas MUST NOT alterarse.

#### Scenario: Convencion canonica aplicada

- **WHEN** el usuario confirma la unificacion y se buscan "Seguridad Informática", "Soporte Técnico Hardware" y "Soporte Técnico Software" en `paper/sections/*.tex`
- **THEN** no queda ninguna ocurrencia en los pasajes que enumeran los "sectores canonicos"
- **AND** cada mencion unificada coincide byte a byte con una de las cinco cadenas canonicas

#### Scenario: Excepcion documentada

- **WHEN** el usuario decide conservar la forma con tildes en esos pasajes
- **THEN** los pasajes quedan sin cambios
- **AND** el registro de la revision consigna la convencion (nombre legible con tildes en prosa, cadena canonica sin tildes como dato del clasificador) y la lista de pasajes

### Requirement: Neutralidad de la revision ortotipografica

Todas las modificaciones que esta revision introduce en archivos de la tesis SHALL ser puramente diacriticas: cada linea modificada MUST ser igual a su version previa al normalizar tildes, dieresis y eñe (incluidas las secuencias de escape LaTeX de acentos del `.bib`), y la cantidad de lineas de cada archivo MUST conservarse. En consecuencia la revision MUST NOT alterar cifras, claves de `\label`/`\ref`/citas ni rutas. El PDF SHALL compilar con XeLaTeX sin errores fatales ni referencias indefinidas y con el mismo numero de paginas que la compilacion previa a la pasada, dentro del presupuesto de 101 paginas. `verify_citations.py` SHALL reportar PASS y `tesis_para_agente.md` SHALL regenerarse desde las fuentes corregidas.

#### Scenario: Diff puramente diacritico

- **WHEN** se ejecuta `revision_tildes.py --base <copia de paper/sections previa a la pasada>`
- **THEN** el codigo de salida es 0 y no se reporta ninguna linea con cambios no diacriticos
- **AND** la comparacion equivalente de `paper/main.tex`, `paper/preambles/preamble.tex` y `Bibliography_base.bib` contra el commit base tambien resulta puramente diacritica

#### Scenario: Cadenas canonicas sin alteraciones

- **WHEN** se cuenta cada una de las cinco cadenas canonicas en `paper/sections/*.tex` antes y despues de la pasada
- **THEN** el conteo posterior es igual al previo mas las menciones unificadas por la decision de coherencia de nombres de sector (cero si no se unifica)
- **AND** ninguna ocurrencia previa cambia ni incorpora tilde

#### Scenario: Conteo de paginas invariante

- **WHEN** se compila el PDF despues de la pasada con el mismo entorno que la compilacion previa
- **THEN** el numero de paginas es igual al previo y no supera 101
- **AND** el registro de compilacion no contiene errores fatales, referencias indefinidas ni advertencias nuevas de altura de encabezado

#### Scenario: Integridad de citas y render

- **WHEN** se ejecuta `verify_citations.py` y se regenera `tesis_para_agente.md`
- **THEN** la verificacion reporta PASS
- **AND** el render regenerado no contiene ninguna de las formas erroneas corregidas en las secciones

### Requirement: Pasada corta repetible para la integracion

`revision_tildes.py --check` SHALL terminar con codigo 0 si y solo si no quedan candidatos `INEQUIVOCO` en zona `prosa` y todo candidato restante tiene decision `mantener` en el registro de decisiones; en caso contrario SHALL terminar con codigo distinto de 0 y listar los candidatos pendientes con archivo, linea, token y forma sugerida. La correspondencia entre candidato y decision SHALL basarse en archivo, token y contexto normalizado, y MUST NOT depender del numero de linea. El procedimiento SHALL quedar documentado para que c-141 lo ejecute despues de cualquier edicion tardia de la prosa.

#### Scenario: Check limpio al cerrar la pasada

- **WHEN** se ejecuta `--check` con todas las correcciones aplicadas y las decisiones registradas
- **THEN** el codigo de salida es 0

#### Scenario: Errata reintroducida detectada

- **WHEN** una edicion posterior agrega "derivación erronea" en prosa y se ejecuta `--check`
- **THEN** el codigo de salida es distinto de 0
- **AND** la salida lista el archivo, la linea, el token y la sugerencia "errónea"

#### Scenario: Homografo nuevo sin decision

- **WHEN** una edicion posterior agrega "el flujo continua sin cambios" sin fila en el registro y se ejecuta `--check`
- **THEN** el codigo de salida es distinto de 0
- **AND** tras registrar la decision y aplicarla, `--check` termina con codigo 0

#### Scenario: Decisiones robustas a desplazamientos de linea

- **WHEN** se insertan lineas antes de un candidato con decision `mantener` y se ejecuta `--check`
- **THEN** la decision se sigue reconociendo y el candidato no se informa como pendiente

### Requirement: Registro de la revision ortotipografica y neutralizacion de la causa raiz

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incorporar una seccion de la recomendacion B14 con: commit base de la pasada, conteos por forma antes y despues, correcciones por clase, cantidad de decisiones y ruta del registro de decisiones, discrepancias con los conteos del dictamen ("fórmula" y "continua" con valor verbal), hallazgos fuera de la muestra, decision sobre los nombres de sector, causa raiz y procedimiento de la pasada corta. `docs/Tesis/acentuar_tesis.py` y `docs/Tesis/acentuar_tesis_v9.py` SHALL declarar en su cabecera que estan deprecados para la tesis v10, con el motivo y la herramienta que los reemplaza, sin cambios en su logica. El lexico de correcciones automaticas de `revision_tildes.py` MUST NOT contener correcciones incondicionales de homografos.

#### Scenario: Registro completo

- **WHEN** se lee la seccion B14 de `dictamen-correcciones.md`
- **THEN** contiene el commit base, los conteos antes y despues, las correcciones por clase, la ruta del registro de decisiones, las discrepancias con el dictamen, la causa raiz y la decision sobre los nombres de sector
- **AND** documenta el uso de `revision_tildes.py --check` como pasada corta para c-141

#### Scenario: Utilidades previas deprecadas

- **WHEN** se ejecuta `grep -c "DEPRECADO"` sobre `docs/Tesis/acentuar_tesis.py` y `docs/Tesis/acentuar_tesis_v9.py`
- **THEN** cada archivo devuelve al menos 1
- **AND** ambos compilan con `python -m py_compile` y su diff solo modifica el docstring de cabecera

#### Scenario: Lexico sin correcciones incondicionales de homografos

- **WHEN** una prueba unitaria inspecciona el lexico de correcciones automaticas de `revision_tildes.py`
- **THEN** ninguna de las claves "hacia", "formula", "continua", "esta", "este", "aquellas", "aquellos", "desarrollo", "completo", "registro", "valida" y "publica" figura como correccion `INEQUIVOCO`

## MODIFIED Requirements

### Requirement: Acentuación normalizada del manuscrito

Los archivos `.tex` de `docs/Tesis/v10 (IA)/paper/sections/` SHALL presentar el
texto español acentuado conforme a las reglas ortográficas vigentes del español
(Ortografía de la lengua española, RAE-ASALE, 2010). La normalización SHALL
aplicarse a la prosa (cuerpo, encabezados, pies de página, pies de figura y tabla,
celdas de texto) incluyendo el texto dentro de argumentos de comandos portadores
de texto (`\section{}`, `\subsection{}`, `\caption{}`, `\textbf{}`, `\emph{}`,
`\item`, `\footnote{}`). El documento MUST NOT modificar tokens protegidos: las
cinco cadenas canónicas de categorías (`Seguridad Informatica`, `Soporte Tecnico
Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`), las claves
de `\label{}`/`\ref{}`/`\autoref{}`/`\cref{}`, las claves de
`\cite{}`/`\textcite{}`/`\parencite{}`, las rutas de
`\input{}`/`\includegraphics{}`/`\bibliography{}` y las rutas de repositorio en
prosa (`docs/Tesis/`, `evaluation/`, `data/`, `App/Backend`), el contenido de
`verbatim`/`lstlisting`/`\verb`, los argumentos de `\texttt{}`, las URLs y DOI, la
matemática, los nombres de comandos LaTeX, el resumen en inglés (desde
`\section*{Abstract}` hasta el fin de `00-resumen.tex`) y las palabras
correctamente acentuadas. Ninguna corrección SHALL des-acentuar una palabra
correctamente acentuada, duplicar tildes ni alterar cifras. Las tildes
improcedentes ---las diacríticas mal asignadas a un homógrafo (por ejemplo "hacía"
con valor de preposición o "fórmula" con valor verbal) y las de los demostrativos
y del adverbio "solo", que la ortografía vigente no prescribe--- SHALL retirarse
con justificación contextual registrada. La normalización MUST NOT editar
`Bibliography_base.bib` salvo las tildes del texto impreso en español de sus
campos `note` y `title`, sin alterar claves, autores, años, DOI, URL ni demás
metadatos.

#### Scenario: Prosa acentuada
- **WHEN** se busca en `sections/*.tex` una forma sin tilde de una palabra que la requiere (por ejemplo "clasificacion", "informacion", "metodologico", "Capitulo", "Introduccion", "erronea", "multiples")
- **THEN** no queda ninguna ocurrencia en prosa sin acentuar
- **AND** el texto correctamente acentuado permanece sin cambios (no se des-acentúa ni se duplica la tilde)

#### Scenario: Tildes improcedentes retiradas con justificación
- **WHEN** se inspeccionan las ocurrencias de "hacía", "fórmula", de los demostrativos con tilde y de "sólo" en `sections/*.tex`
- **THEN** "hacía" solo aparece como pretérito de "hacer", "fórmula" solo como sustantivo, y no quedan demostrativos con tilde ni "sólo"
- **AND** cada tilde retirada de un homógrafo consta con su justificación en el registro de decisiones de la revisión

#### Scenario: Tokens protegidos intactos
- **WHEN** se comparan antes y después las cinco cadenas canónicas de categorías, las claves de `\label`/`\ref`/`\autoref`, las claves de citas y las rutas de `\input`/`\includegraphics`
- **THEN** las claves y rutas forman un conjunto idéntico y ninguna ocurrencia previa de las cinco cadenas canónicas se altera
- **AND** ninguna cadena de categoría incorpora tilde

#### Scenario: Pares sensibles preservados
- **WHEN** se inspeccionan las ocurrencias de `hipótesis` y `síntesis`
- **THEN** se conservan exactamente acentuadas como corresponde
- **AND** no aparecen como `hipotesis`/`sintesis` ni con tilde duplicada

#### Scenario: Sin residuos de la herramienta
- **WHEN** se revisa el árbol de trabajo tras aplicar la normalización
- **THEN** no existen archivos `.tex.bak` nuevos
- **AND** ningún archivo de la tesis fuera de `paper/sections/`, `paper/main.tex`, `paper/preambles/preamble.tex`, `Bibliography_base.bib` y del render regenerado `tesis_para_agente.md` fue modificado por la normalización
