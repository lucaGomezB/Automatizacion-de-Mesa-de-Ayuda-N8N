# Design: Atender la devolucion de segunda instancia del tribunal sobre v1.2.18

## Context

Ver `proposal.md` para la motivacion. Fuente: devolucion de segunda instancia del tribunal del
11-11-2026 sobre `v1.2.18` (seccion 5, observaciones N-01 a N-16; seccion 7, correcciones
obligatorias; seccion 8, preguntas probables). La fuente unica de decisiones y alcance es el brief
del orquestador (`brief-c-196.md`, en el scratchpad de la sesion); este design lo traslada sin
reinterpretarlo. Si un hecho del repo contradice el brief, el agente de apply se detiene y lo
reporta.

**Numeracion.** Capitulo del PDF -> archivo: 1 = `01-introduccion`, 4 = `04-marco-metodologico`,
5 = `05-arquitectura`, 6 = `06-implementacion`, 7 (legal) = `11-aspectos-legales`, 8 (Resultados)
= `07-resultados`, 9 (Discusion) = `08-discusion`, 10 (Conclusiones) = `09-conclusiones`, 11 =
`10-recomendaciones`, Anexos A-I = `12-anexos` (Anexo I = `sec:anexo-trazabilidad`, lineas
~203-386). `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`K/` = `C:\Users\Gonzalo\AppData\Local\Temp\claude\ce105e7bdc6bb43e\bea2098b-58d3-40bb-9c13-9dceda89bb8f\scratchpad\scripts\`
(scripts de recalculo de solo lectura: `n03.py`, `n05.py`, `n08_n09.py`, `n08_laxa.py`,
`sent.py`, `lines.py` + `lines_out.txt`, `ids.py`, `ids2.py`, `tildes.py`, `figsize.py`; Python
con scipy/pandas en `C:/Users/Gonzalo/AppData/Local/Temp/v313/Scripts/python.exe`). Cada parrafo
de los `.tex` es una sola linea fisica; las lineas citadas son las del arbol al proponer y el
apply localiza por texto (`rg -n`).

**Estado de partida verificado al proponer** (solo lectura, 2026-11-11, rama
`change/c-196-atender-devolucion-segunda-instancia`, HEAD `03d1612`):

- κ = 0,87 en `S/00-resumen.tex:11` (ES) y `:27` (EN), `S/01-introduccion.tex:66`,
  `S/04-marco-metodologico.tex:55` (dos menciones) y `:89` (tres), `S/08-discusion.tex:58` y
  **`S/07-resultados.tex:249` (dos menciones en 8.7, "Este kappa es un valor distinto del 0,87 de
  la campaña 2026-10 ... el 0,87 se informa sin intervalo")**, que el brief no lista. No se tocan
  `S/07-resultados.tex:113` ("0,870", otra cifra) ni `S/03-estado-del-arte.tex:34,51` (0,87 de
  literatura). `C/numeros-canonicos.md` tiene 7 menciones de 0,87 (seccion 3.6).
- "estratificad"/"stratified" en `S/00-resumen.tex:11` y `:27`, `S/04-marco-metodologico.tex:45` y
  `S/08-discusion.tex:22` ("muestra estratificada").
- Segunda sub-hipotesis declarada refutada (25/147) en `S/01-introduccion.tex:34`,
  `S/04-marco-metodologico.tex:81`, `S/07-resultados.tex:154`, `S/08-discusion.tex:8`,
  `S/09-conclusiones.tex:6, 22, 26, 41`, `S/10-recomendaciones.tex:6`, `S/12-anexos.tex:263` y la
  fila A1 de la tabla del 9-11 sobre `v1.2.12` (~`:370`); el Resumen (`:13`) y el Abstract
  (`:29`) dicen "se refuta"/"refuted" sin el participio. 1.4 y 4.7 definen la regla de tres vias
  como asimetrica ("refutada si la estimacion puntual alcanza o supera 0,15").
- "diferida" (A1, consentimiento) aparece una sola vez en `S/12-anexos.tex:358`; la linea ~370 es
  la fila A1 de la tabla del 9-11 y no contiene "diferida" (el apply revisa ambas por texto).
- Etiquetas existentes verificadas: `subsec:amenazas-validez`, `subsec:poblacion-muestra-corpus`,
  `subsec:protocolo-pruebas` (04); `subsec:hipotesis-trabajo` (01);
  `subsec:resultados-campana-medicion`, `subsec:reduccion-intervencion`, `subsec:matriz-metricas`,
  `tab:exactitud-etapa-canal` (07); `subsec:interpretacion-resultados`,
  `subsec:limitaciones-estudio`, `subsec:balance-neto` (08); `sec:anexo-corpus`,
  `sec:anexo-trazabilidad` (12); `subsec:consentimiento-derechos` (11). Las tres etiquetas nuevas
  no existen todavia.
- Comando de cobertura: `S/06-implementacion.tex:85` imprime `pytest --cov=app.routes
  --cov=app.services --cov=app.repositories --cov-report=term-missing`; el CI
  (`.github/workflows`, paso "Run backend unit tests (SQLite) with coverage") agrega
  `-m "not integration"`.
- `auditorias/` versiona la auditoria del 4-8-2026
  (`Auditoria_Tesis_Gomez_Bustos_Sevilla_040802026.pdf`) y nueve dictamenes `.md`; la devolucion
  del 11-11 NO esta versionada (solo existe como PDF en el scratchpad, `pdf/devolucion.pdf`).
- `C/dictamen-correcciones.md`: ultima seccion "## Dictamen v10 / v1.2.16 (2026-11-09) - c-195"
  (linea ~4405); `C/verificar_matriz_trazabilidad.py` exige matriz de 7 columnas en toda seccion
  `## Dictamen ... - c-NNN` con NNN >= 190. `CHANGES.md`: ultima fase FASE 60 (c-195, `v1.2.17`);
  la release `v1.2.18` (commit `457b14a`, hash consignado en `161f900`) no tiene FASE propia.

## Goals / Non-Goals

**Goals:**

- Atender N-01 a N-15 en el ejemplar de defensa, con verificacion de aceptacion por grep para
  cada una (antes falla, despues pasa).
- Que cada numero nuevo salga de un script de `K/` o de los datos versionados.
- Que lo que solo saben los autores quede marcado y no redactado como hecho.
- Que cinco agentes de apply trabajen en paralelo sin tocar archivos ajenos (grupos A, B, C,
  Figuras y Cobertura), y que un sexto (Cierre) integre, compile y registre.

**Non-Goals:**

- Nuevas mediciones, corridas del clasificador o del corpus (unica excepcion: la lectura de la
  cobertura del backend con el comando del CI, N-10, que mide el orquestador).
- Cambios en `App/`, `n8n/`, `docker/`, `evaluation/` o en el change activo `c-191`.
- La release: version, portada, tag y hash del Anexo B los decide el orquestador con el usuario.
- N-16 (Paket et al. y Mayor-Rocher et al.) y la declaracion del uso de modelos de lenguaje en la
  redaccion (pregunta 16): pendientes de los autores.
- Reducir el PDF al tope de 100 paginas.

## Decisions

### D0 — Verificacion previa por grupo (bloqueante, solo lectura)

Cada grupo, antes de editar, corre los scripts de `K/` que respaldan sus numeros y su grep de
aceptacion "antes" (debe fallar). Si una cifra no se reproduce, esa observacion se detiene y se
consulta al orquestador. Numeros de referencia (del brief): N-03 tabla por operador (O1 110 casos,
20,1 s (9,2), mediana 18,0 s, automatizado 13,3 s, 33,8 %, p = 9,8 × 10⁻⁷, r = 0,54; O2 110,
76,6 s (21,4), 73,0 s, 15,5 s, 79,7 %, 9,0 × 10⁻²⁰, 1,00; agregado 200, 47,6 s (28,7), 49,0 s,
14,6 s, 69,3 %, 3,0 × 10⁻²⁸, 0,90; 20 casos comunes: 20,1 s O1 y 92,8 s O2; R025 de 0 s, sin el
O1 da 20,3 s y 34,3 %; Spearman manual entre campanas 0,15 (O1) y −0,05 (O2); automatizados entre
campanas ρ = 0,70). N-08: 110/138 = 0,797 [0,722; 0,856]; laxa 117/138 = 0,848 [0,779; 0,898];
original mismos 138: 109/138 = 0,790 [0,714; 0,850], laxa 125/138 = 0,906 [0,846; 0,944]; 62 sin
consenso 38/62 = 0,613; consenso = original en 116/138 (84,1 %); macro-F1 contra consenso 0,757
(IC solo si existe implementacion canonica del bootstrap en `evaluation/`; si no, puntual).
N-09: 25/147 = 17,0 %, Wilson [11,8 %; 23,9 %], binomial p = 0,28 unilateral (H1: p > 0,15),
0,49 bilateral; 25/200 = 12,5 % [8,6 %; 17,8 %]. N-05: 81/81 telefonicos coinciden con
`data/corpus_resultados_telefonia.json`; 0/119 con `data/corpus_resultados.json` (media 0,41 s).

### D-N01 — Retirar el κ = 0,87 como evidencia de fiabilidad

Alternativa descartada: conservarlo como "valor historico sin IC" (criterio vigente desde c-169).
El tribunal muestra que el valor ya figuraba en la v7 (2-7-2026), cuando solo existia el corpus
sintetico (11-6-2026; el real se versiono el 9-10-2026), y no hay planillas ni etiquetas por
analista en el repo. Por lo tanto:

- Resumen y Abstract: se quita el 0,87; queda "El doble etiquetado independiente de la campaña
  complementaria alcanzó un kappa de 0,5569 (moderado; IC del 95 % [0,4725; 0,6413])", dentro
  del tope de 250 palabras (conteo sobre el `.tex` sin comandos, regla de c-106).
- 1.7 (`S/01:66`) y 9.3 (`S/08:58`): se quita el 0,87; 9.3 dice que el doble etiquetado original
  no conserva registro y no permite contraste.
- 4.4 (`S/04:55`): UNICA mencion permitida del 0,87 en el cuerpo. Oraciones cortas: las planillas
  del doble etiquetado original no se conservaron; el 0,87 informado en versiones anteriores no
  puede respaldarse con registros y no se presenta como evidencia (`\autoref{subsec:nota-versiones}`);
  la fiabilidad de la referencia se estima con el doble etiquetado independiente (κ = 0,5569,
  moderado). Se conserva quienes fueron los analistas (uno externo, uno autor) y el consenso
  supervisado. `% PENDIENTE-AUTORES(N-01): fecha del etiquetado original y origen del 0,87; si
  aparecen las planillas, citarlas con su fecha.`
- 4.8 (`S/04:89`): la mitigacion de la amenaza de constructo se apoya en κ = 0,5569 (fiabilidad
  limitada); se borra "se informa sin intervalo, porque su tabla...".
- 8.7 (`S/07:249`, contradiccion con el brief: no lo lista): el contraste "valor distinto del
  0,87" se reemplaza por una frase sin el valor (el doble etiquetado original no conserva
  registro). Lo hace el grupo B (dueno de `07-resultados.tex`).
- `C/numeros-canonicos.md` (Cierre): el 0,87 pasa a estado "retirado como evidencia (sin
  respaldo; ver nota de versiones)". Los rotulos de Landis y Koch siguen aplicandose al 0,5569.

Aceptacion: `rg -c "0\{?,\}?87|0\.87" S/00-resumen.tex S/01-introduccion.tex S/08-discusion.tex`
-> 0; en `S/04-marco-metodologico.tex` exactamente 1 (4.4); en `S/07-resultados.tex` solo el
"0,870" de la linea ~113.

### D-N02 — Nota de versiones y trazabilidad de la auditoria del 4 de agosto

Todo en `S/12-anexos.tex` (grupo C):

- Al inicio del Anexo I, `\subsection*`/`\subsection` breve "Nota de versiones" con
  `\label{subsec:nota-versiones}` (media pagina como maximo): la version del 3 de julio de 2026
  informo 165,3 s -> 18,2 s (89,0 %), exactitud 92 %, W = 0 y κ = 0,87; tiempos, exactitud y
  estadistico provenian de un corpus sintetico de 200 casos generado durante el desarrollo
  (`docs/anexo_f_corpus.md:18-23`), descartado y eliminado; la version actual usa el corpus real
  pseudonimizado (61,6 s -> 17,76 s, 71,2 %; 73,5 %; W = 363). El 0,87 figuraba en esa version;
  sus planillas no se conservan y ya no se presenta como evidencia
  (`\autoref{subsec:poblacion-muestra-corpus}`). MUST NOT afirmar que el 0,87 provenia del
  corpus sintetico. `% PENDIENTE-AUTORES(N-02): confirmar la fecha exacta de la version de julio
  y el origen del 0,87.`
- Primera fila/bloque de la trazabilidad: auditoria integral del tribunal del 4-8-2026 (105
  hallazgos, 28 criticos, 3,9/10; archivo en `auditorias/`), que origino la reformulacion con
  datos reales (cruce en `C/reconciliacion-cobertura.md`). La frase que hoy presenta la serie solo
  como autoevaluaciones distingue: (a) auditoria del tribunal del 4-8-2026; (b) nueve
  autoevaluaciones internas generadas con un modelo de lenguaje; (c) devolucion de segunda
  instancia del tribunal del 11-11-2026.
- Tabla final `tab:trazabilidad-devolucion-segunda-instancia`: N-01 a N-16, observacion (4-8
  palabras), seccion corregida (`\autoref`), estado ("Atendida" / "Atendida en parte; resta dato
  de los autores" / "Pendiente"). Estado esperado: N-16 pendiente; N-01, N-02, N-04, N-05 y N-13
  atendidas en parte; el resto atendidas. En el Anexo I puede figurar `c-196`.
- `% PENDIENTE-AUTORES(P16): declarar el uso de modelos de lenguaje en la redacción de la tesis.`
- La historia de la segunda sub-hipotesis en la Tabla 24 (~`:316`) puede decir que una version
  intermedia la declaro refutada y que la actual la lee como no concluyente (D-N09).

### D-N03 — Tiempos manuales de la campana complementaria

La tarea manual de la campana complementaria (`docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`)
mide la decision de sector (instante en que el operador toma el caso y en que asigna el sector);
la de la campana 2026-10 incluyo lectura, comprension, busqueda y carga (y la escucha en
telefonia). No son la misma tarea. 4.5 (`S/04:65`, grupo A) lo declara en 3-4 oraciones y remite a
`\autoref{tab:tiempos-manual-complementaria}`. 8.7 (grupo B) agrega el parrafo "Tiempos del brazo
manual por operador" y la tabla `tab:tiempos-manual-complementaria` (columnas: Operador, Casos,
Manual media (desvio), Manual mediana, Automatizado mismos casos: media, Reduccion, p Wilcoxon
pareado, r rank-biserial; fuente: elaboracion propia sobre `brazo_manual.csv` y
`corpus_campana.json`), con: automatizado = corrida propia de la complementaria (14,6 s, no el
17,76 s canonico); R025 de 0 s; los 20 casos comunes; las correlaciones; que miden la decision de
sector y no reemplazan el contraste principal; que el 69,3 % agregado es del mismo orden que el
71,2 %. 9.1 (`S/08:22`, grupo B) agrega la dependencia del operador como explicacion rival
(33,8 % a 79,7 %; el tiempo manual no es propiedad estable del incidente; la reduccion sigue
significativa con el operador mas rapido) y actualiza el conteo de rivales.

### D-N04 — Muestreo no probabilistico por conveniencia

Una sola forma: los 200 casos son los incidentes cronometrados en la campana manual (muestreo no
probabilistico por conveniencia o disponibilidad). Se quitan "estratificado" y "asignacion
proporcional" de `S/04:45`, Resumen y Abstract ("convenience sample") y "muestra estratificada" de
`S/08:22`. La formula de tamano muestral se informa como margen de error implicado, no como
diseno. El sesgo de seleccion pasa a 4.8 como amenaza a la validez externa. No se inventan
fechas: `% PENDIENTE-AUTORES(N-04): fechas exactas del período relevado y criterio con que se
tomaron los 200 casos entre los ~2.646.` La composicion por sector (85/67/31/16/1) se presenta
como la observada, no como asignacion. Alternativa descartada: conservar "estratificado"
describiendo la composicion; el corpus no tiene fechas ni marco muestral que lo respalde.

### D-N05 — Registro primario de los tiempos automatizados

4.5 (`S/04:63`, grupo A): 2-3 oraciones: los 119 valores de correo (66) y formulario (53) no tienen
registro primario conservado; constan solo como valores del corpus versionado;
`data/corpus_resultados.json` es otra corrida y no los respalda; los 81 telefonicos coinciden con
su registro (`data/corpus_resultados_telefonia.json`). `% PENDIENTE-AUTORES(N-05): de qué
registro se transcribieron los 119 tiempos del 2-10-2026; si existe, versionarlo.` 8.1 (grupo B):
una oracion en la comparacion de tiempos (81 con registro primario y 119 sin el;
`\autoref{subsec:protocolo-pruebas}`). Anexo F (`S/12:119`, grupo C): alinear con 4.5 si hace falta.

### D-N06 — Llamadas recitadas por un autor

4.8 (grupo A): amenaza nueva (actualizar el conteo): un autor que conocia el caso y el sistema
recito las 81 llamadas parafraseando la descripcion pseudonimizada; habla mas claro y breve que un
usuario real, lo que favorece el tiempo medido; dos configuraciones (25 casos el 5-10 y 56 el
6-10; la version del dia 6 no consta); magnitud no estimada. MUST NOT afirmar como hecho que
favorecio la exactitud: pudo favorecer la transcripcion, y aun asi el canal tuvo la exactitud mas
baja (0,654). 9.1 (grupo B): explicacion rival sobre la procedencia de las llamadas; las cifras
telefonicas no se extrapolan a usuarios reales.

### D-N07 — Concision e identificadores de cambio

(a) Fuera del Anexo I no quedan identificadores de cambio (`c-NNN`, `C-NN`, `C-63a`) ni la palabra
"changes". Inventario de `K/ids.py`/`ids2.py`: `S/04:63` (c-71, c-72, c-74), `S/04:65` (c-165),
`S/05:78` epigrafe (c-82, c-86, c-153) y `:92` (c-153), `S/06:10` (c-182) y `:102` epigrafe (c-80),
`S/07:154` (c-82), `S/11:34, 58, 61, 82-86, 96` (c-165 a c-168; C-61...C-66, C-63a/b, C-156;
"seis changes"), `S/12:24, 31, 38` (epigrafes del Anexo A) y `:50, 67-73, 81, 84` (tabla del Anexo
B), y el glosario si define el termino. Se reemplazan por la descripcion de lo que el cambio hizo
o por una remision unica a `\autoref{sec:anexo-trazabilidad}`. Los comentarios `%` no cuentan. El
contenido de los PNG queda fuera de este criterio salvo en las figuras que regenera el grupo
Figuras (abierto: ver Open Questions).
(b) Se parten las oraciones de mas de 60 palabras de 01, 04, 07 y 08 (30 oraciones listadas en
`K/lines_out.txt`) sin cambiar cifras ni citas; "de modo que" -> punto o "por lo tanto" donde se
toque. `K/sent.py` al final: n > 60 = 0 en esos cuatro archivos, o cada excepcion justificada
(falsos positivos por notas al pie o tablas).

### D-N08 — Exactitud contra el consenso independiente

Grupo B, `S/07-resultados.tex`: la Tabla 12 (`tab:exactitud-etapa-canal`, lineas ~100-120) suma
dos filas: "Casos con consenso E1 = E2, referencia original" (109/138 = 0,790 [0,714; 0,850];
laxa 125/138 = 0,906 [0,846; 0,944]) y "Mismos casos, referencia de consenso E1 = E2" (110/138 =
0,797 [0,722; 0,856]; laxa 117/138 = 0,848 [0,779; 0,898]), con nota al pie sobre los 62 casos
sin consenso (38/62 = 0,613 contra el original) y la definicion de la laxa contra el consenso.
3-4 oraciones en 8.2. **Decision**: el veredicto de la tercera sub-hipotesis se mantiene sobre la
referencia primaria (el etiquetado original, prefijada); se dice que, contra el consenso, el
limite superior (0,856) supera el umbral de 0,85 y con esa referencia el criterio de exactitud
quedaria no concluyente; el macro-F1 (0,757) sigue por debajo. Una oracion en 9.3 (`S/08:58`).
Alternativa descartada: cambiar la referencia primaria a posteriori (seria la misma falta que
N-09 senala).

### D-N09 — Segunda sub-hipotesis: no concluyente, con estimacion puntual por encima de la cota

Antes del 9-11-2026 la regla de tres vias se aplicaba a 25/200 (12,5 %; IC [8,6; 17,8]) y daba
"no concluyente". El 9-11 se cambio el denominador a 147 y se declaro "refutada". Binomial contra
0,15: p = 0,28 unilateral (H1: p > 0,15), 0,49 bilateral; el intervalo [11,8 %; 23,9 %] incluye
0,15. **Decision**: veredicto "no concluyente, con estimación puntual por encima de la cota".

- 1.4 (`S/01:34`) y 8.3 (`S/07:154`) declaran que la eleccion del denominador (147 revisados) y la
  lectura de la regla se fijaron despues de conocer los datos, y que p = 0,28 es unilateral.
- **Consecuencia sobre la definicion de la regla** (el brief no la explicita; ver Open
  Questions): la definicion vigente en 1.4 y 4.7 ("refutada si la estimacion puntual alcanza o
  supera 0,15"; "la regla es asimetrica") produce "refutada" con 17,0 %, lo que contradiria el
  veredicto nuevo. Propuesta: conservar la regla prefijada y su aplicacion al denominador
  prefijado (200 -> no concluyente), declarar posterior la lectura sobre 147 y adoptar la lectura
  estadistica: con 147, el intervalo contiene 0,15 y la estimacion puntual queda por encima, por lo
  tanto "no concluyente, con estimación puntual por encima de la cota". La frase "la regla es
  asimetrica: refutada significa que la estimacion puntual alcanza la cota..." se retira o se
  reformula como antecedente de la lectura posterior.
- Propagacion a TODAS las apariciones referidas a esta sub-hipotesis: `S/00-resumen.tex:13` y
  `:29`, `S/01:34`, `S/04:81`, `S/07:154`, `S/08:8`, `S/09:6, 22, 26, 41`, `S/10:6, 18`,
  `S/12:263` y la Tabla 24 (~`:316`; puede contar la historia). Conteo de veredictos: una
  corroborada (tiempo), una no concluyente (intervencion) y una refutada (exactitud y macro-F1).
  La tercera sub-hipotesis sigue refutada.
- Aceptacion: en esas lineas "refutada"/"refuta"/"refuted"/"refutó" ya no califica a la segunda
  sub-hipotesis; `rg -c -i "unilateral"` >= 1 en `S/07` y en `S/08`.

### D-N10 — Cobertura del backend

El orquestador mide la cobertura con el comando del CI (`pytest -m "not integration"
--cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing`, desde
`App/Backend/` con las variables dummy del CI) y entrega valor, commit y fecha al grupo C. Texto en
6.7 (`S/06:85`): "La cobertura de sentencias de la suite unitaria sobre rutas, servicios y
repositorios es de X % (commit H, fecha), medida con el comando anterior.", con el comando del
texto unificado con el del CI. Sin valor: `% PENDIENTE-AUTORES(N-10)` y ninguna cifra (requisito
"Evidencia de cobertura de pruebas"). El valor se registra en `C/numeros-canonicos.md`.

### D-N11 — Figuras 2, 7, 8 y 10

Grupo Figuras: regenera los PNG desde `docs/diagrams/*.md` (apaisado o por capas) para que el texto
quede >= 6 pt en A4 (`K/figsize.py` antes y despues). No toca `.tex`; entrega al grupo C la lista
de cambios de `\includegraphics` (ancho, `landscape`, division en subfiguras). El grupo C los
integra. Si al regenerar aparece un identificador de cambio en el rotulo, se reemplaza por su
descripcion (D-N07) salvo que el requisito de la figura lo exija (ver Open Questions).

### D-N12 — Conclusiones

Grupo B, `S/09-conclusiones.tex`: se quitan "un valor que lo posiciona como una vía prácticamente
útil" (`:39`), "representaba el mayor desafío técnico", "aisló la complejidad..." , "económicamente
accesible" (`:6`; el balance neto central es negativo, `subsec:balance-neto`) y "resultó el rasgo
más relevante" (`:37`). No se repiten las cifras del capitulo 8 en la prosa: quedan en la tabla de
objetivos y se remite con `\autoref`. Se menciona que el tiempo telefonico se midio con llamadas
recitadas (`\autoref{subsec:amenazas-validez}`). Se mantiene el grado de cumplimiento de cada
objetivo (con el estado de D-N09 para el objetivo de intervencion).

### D-N13 — Instrumento del art. 12 de la Ley 25.326

Grupo C, `S/11-aspectos-legales.tex` (7.3, lineas ~14-20): parrafo final: durante el estudio no
se suscribieron clausulas contractuales modelo (Disposicion 60-E/2016) ni se recabo consentimiento
de titulares para la transferencia; a los proveedores llegaron descripciones pseudonimizadas como
texto y audio recitado por uno de los autores; el instrumento queda como requisito previo del
adoptante. "suscripto" (linea ~20) -> "las condiciones de servicio aceptadas" si no consta un
acuerdo firmado (`docs/seguridad/instrumento-transferencia-internacional.md` dice "documentado, no
suscrito"). `% PENDIENTE-AUTORES(N-13): confirmar que no se firmó ningún instrumento con Google ni
Twilio y que no cruzó ningún dato personal de terceros.` Gobernanza HIGH en lo factico: solo se
afirma lo que consta en el repo.

### D-N14 — Consentimiento en el Anexo I

Grupo C: `S/12:358` (y cualquier otra mencion de A1 como "diferida" o "pendiente") pasa a
"atendida el 10 de noviembre de 2026", segun
`docs/campana-medicion/confirmacion-posterior-consentimiento.md:45-48` (informacion verbal 1-11,
confirmacion escrita 10-11 para E1, E2, O1, O2; originales en poder del director).

### D-N15 — Tildes en los nombres de sector

Convencion (excepcion documentada del requisito "Coherencia de los nombres de sector"): en prosa,
con tilde ("Seguridad Informática", "Soporte Técnico Hardware", "Soporte Técnico Software");
donde se cita la cadena exacta del sistema (tablas de datos, matriz de confusion, prompt),
`\texttt{Seguridad Informatica}`. Inventario de `K/tildes.py` (29 en prosa: `S/01:48, 72`;
`S/04:45`; `S/05:70`; `S/07:148, 239, 241, 243`; `S/08:24`). Cada grupo corrige las de sus
archivos; nada se reemplaza a ciegas. La convencion se registra en `C/dictamen-correcciones.md`.

### D-N16 — Bibliografia pendiente

No se cambia la bibliografia. Grupo C: `% PENDIENTE-AUTORES(N-16)` en una linea propia ANTES de
las entradas `paket2024itservice` y `mayorrocher2026spanish` de `Bibliography_base.bib` (un `%`
dentro de una entrada no es seguro). `verify_citations.py` debe seguir en PASS.

### D-PEND — Mecanismo `% PENDIENTE-AUTORES(N-xx)`

Lo que solo saben los autores no se redacta como hecho. Se deja un comentario LaTeX
`% PENDIENTE-AUTORES(N-xx): <qué falta>` en la linea anterior al pasaje, y el texto visible queda
verdadero sin ese dato. Marcadores esperados: N-01 (4.4), N-02 (nota de versiones), P16 (Anexo
I), N-04 (4.4), N-05 (4.5), N-10 (6.7, solo si no hay valor), N-13 (7.3), N-16 (`.bib`). El Cierre
los inventaria (`rg -n "PENDIENTE-AUTORES" S/ "docs/Tesis/v10 (IA)/Bibliography_base.bib"`) y los
lista en el registro.

### D-LBL — Etiquetas nuevas acordadas

Nombres exactos, cada una con un solo dueno: `tab:tiempos-manual-complementaria` (tabla de 8.7,
grupo B); `subsec:nota-versiones` (Anexo I, grupo C);
`tab:trazabilidad-devolucion-segunda-instancia` (Anexo I, grupo C). Los grupos remiten a etiquetas
de otro grupo con `\autoref{...}` aunque todavia no existan; el Cierre verifica que resuelvan. No
se cambia ningun `\label` existente.

### D-OWN — Propiedad de archivos por grupo (sin solapamiento)

| Grupo | Archivos (solo estos) | Observaciones |
|-------|-----------------------|---------------|
| A | `S/00-resumen.tex`, `S/01-introduccion.tex`, `S/04-marco-metodologico.tex` | N-01, N-03 (4.5), N-04, N-05 (4.5), N-06 (4.8), N-07, N-09, N-15 |
| B | `S/07-resultados.tex`, `S/08-discusion.tex`, `S/09-conclusiones.tex`, `S/10-recomendaciones.tex` | N-01 (8.7, 9.3), N-03, N-04 (9.1), N-05 (8.1), N-06 (9.1), N-07, N-08, N-09, N-12, N-15 |
| C | `S/12-anexos.tex`, `S/11-aspectos-legales.tex`, `S/05-arquitectura.tex`, `S/06-implementacion.tex`, `S/00-glosario.tex`, `Bibliography_base.bib`, `paper/preambles/` | N-02, N-05 (Anexo F), N-07, N-09 (Anexo I), N-10, N-11 (integracion), N-13, N-14, N-15, N-16 |
| Figuras | `docs/diagrams/*.md`, `paper/figures/*.png` (no `.tex`) | N-11 |
| Cobertura | ninguno en la tesis (lee `App/Backend/` y entrega el valor) | N-10 (medicion) |
| Cierre | `C/dictamen-correcciones.md`, `C/numeros-canonicos.md`, `paper/compilacion.md`, `tesis_para_agente.md`, `CHANGES.md`, `auditorias/` | integracion y registro |

### D-REG — Registro (convencion de c-195)

`C/dictamen-correcciones.md`: seccion nueva "## Dictamen v10 / v1.2.18 (2026-11-11) - c-196
(devolucion de segunda instancia)" (titulo con el prefijo "## Dictamen" que reconoce el
verificador) con resumen, matriz de 7 columnas (Rec | Sintesis | Change | Archivo:linea |
Ancla | Fragmento verificable | Estado), una fila por N-01 a N-16, fragmentos tomados del texto
final; las filas con dato de los autores en estado "PENDIENTE (dato de los autores)" (el
verificador las omite); decisiones (D-N01, D-N08, D-N09, D-N15); inventario de
`PENDIENTE-AUTORES`; libro mayor de paginas y palabras. Como el titulo nombra `c-196` (>= 190), el
verificador exige la matriz. Las filas de matrices anteriores cuyo parrafo reescribe c-196 (por
ejemplo, la segunda sub-hipotesis "refutada" de c-190/c-192/c-195, el kappa de 1.6) se marcan
"SUPERADA por c-196". Gotcha gitleaks: en la prosa del registro, "seccion N (`archivo.tex`)",
nunca "capitulo" + coma/igual + token largo. `C/numeros-canonicos.md`: 0,87 retirado; estado de la
sub-hipotesis 2; tiempos manuales por operador; exactitud contra el consenso; cobertura del backend.

## Risks / Trade-offs

- [Paginacion del Anexo I fragil: nota de versiones y tabla de 16 filas] -> no se fuerza; se
  compila y se reporta el total; tabla en `\footnotesize`, filas de una linea; se registra en el
  libro mayor (linea base: la de `v1.2.18`, 120 paginas segun el tribunal).
- [Tope de 250 palabras del Resumen y el Abstract] -> el kappa nuevo con IC y "convenience sample"
  agregan palabras; se compensa en el mismo resumen; conteo con la regla de c-106 antes y despues.
- [Renumeracion de tablas y figuras: la tabla nueva de 8.7 y la del Anexo I corren la numeracion;
  el tribunal cita "Tabla 12", "Tabla 24", "Tabla 26"] -> todas las remisiones son `\autoref`; el
  registro cita etiquetas, no numeros; la tabla de la devolucion nombra secciones.
- [Conflicto de veredicto en la regla de tres vias (D-N09)] -> decision explicita del orquestador
  antes de aplicar 1.4 y 4.7 (Open Questions).
- [Requisitos vigentes de la spec que exigian el 0,87 como "vigente sin IC", "VIS-005 (c-82)" en
  8.3 o "C-61 a C-66" en el capitulo 7] -> el delta spec los modifica.
- [Partir oraciones puede cambiar cifras o citas] -> diff revisado: ningun numero ni clave de cita
  cambia en los parrafos partidos (`rg` de numeros antes/despues).
- [Agentes paralelos con remisiones cruzadas a etiquetas inexistentes] -> D-LBL; el Cierre compila
  con 0 referencias indefinidas.
- [Gitleaks en la prosa del registro] -> "seccion N (`archivo.tex`)".

## Migration Plan

Orden: D0 por grupo; grupos A, B, C, Figuras y Cobertura en paralelo (cada uno solo sus archivos);
el grupo C integra Figuras (`\includegraphics`) y Cobertura (valor de 6.7) cuando llegan; Cierre
al final. Los commits, el versionado de la devolucion en `auditorias/`, la release (version,
portada, tag, hash del Anexo B), `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` y el
PR contra `main` los hace el orquestador con el usuario. Rollback: revertir los commits del change.

## Open Questions

- **D-N09, definicion de la regla de tres vias en 1.4 y 4.7**: el brief fija el veredicto pero no
  como redactar la regla. Propuesta de este design (arriba). Requiere confirmacion del orquestador
  antes de que el grupo A edite 1.4/4.7 y el grupo B 8.3.
- **D-N07, identificadores dentro de los PNG**: el requisito vigente de `fig:componentes` y
  `fig:secuencia` exige que el rotulo cite "c-82". Si esas figuras no estan entre las 2, 7, 8 y 10,
  quedan como estan; si estan, el orquestador decide si se reemplaza "c-82" por "especificacion
  de visibilidad de incidentes".
- **N-10**: valor de la cobertura (lo entrega el orquestador).
- **Devolucion en `auditorias/`**: nombre del archivo y si se versiona el PDF (decision del
  orquestador con el usuario).
- Pendientes de los autores (no bloquean el apply): origen y fecha del 0,87; periodo y criterio
  de seleccion; registro de los 119 tiempos; instrumentos firmados con Google o Twilio; Paket et
  al. y Mayor-Rocher et al.; declaracion del uso de modelos de lenguaje; release.
