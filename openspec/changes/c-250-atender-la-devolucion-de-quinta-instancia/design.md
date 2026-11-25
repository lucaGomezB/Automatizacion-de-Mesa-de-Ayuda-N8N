# Design: Atender la devolucion de quinta instancia

## Context

Ver `proposal.md` - Why. Estado verificado el 2026-11-25 sobre la rama
`change/c-250-atender-la-devolucion-de-quinta-instancia`, cortada de `main` (release `v1.6.4`,
tag anotado sobre `f05ef2d`, C3; hash consignado en `compilacion.md` por `c64832f`, C4). La copia de
entrega `docs/Tesis/tesis_ultima_version.pdf` tiene SHA-256
`0c208da82d0b4e349cc0a7e7a0e8731a67f92650ec61bd5f353b57a8da626e71` (157 paginas), igual a la
registrada por c-249: las paginas que cita el tribunal son las de ese PDF.

### Mapa de capitulos y tablas (v1.6.4)

El orden de `main.tex` hace que la numeracion del PDF no coincida con el prefijo de los archivos:
cap. 1 = `01-introduccion.tex`; cap. 4 = `04-marco-metodologico.tex`; **cap. 7 =
`11-aspectos-legales.tex`**; **cap. 8 = `07-resultados.tex`**; cap. 9 = `08-discusion.tex`;
cap. 10 = `09-conclusiones.tex`; cap. 11 = `10-recomendaciones.tex`; anexos = `12-anexos.tex`.
Tablas citadas: Tabla 3 = `tab:variables` (`04:24-40`, fila de tiempo `04:31`); Tabla 4 =
`tab:procedencia-numeros` (`04:70-82`, fila manual `04:78`, fila correo/formulario `04:79`);
Tabla 10 = `tab:sintesis-resultados` (`07:15-30`); Tabla 12 = `tab:tiempos-canal` (`07:65-78`, fila
telefonica `07:74`); Tabla 23 = `tab:cumplimiento-objetivos` (`09:15-30`); Tabla 26 =
`tab:declaracion-uso-ia` (`12:261-275`); Anexo K = `sec:anexo-sensibilidad` (`12:345`), con
`tab:rango-robustez-tiempos` (Tabla 29, `12:358-370`). Anexo I.1 = `subsec:nota-versiones`
(`12:239-245`); I.3 = `subsec:declaracion-uso-ia` (`12:253-279`).

### Ubicacion de cada observacion (lineas de `v1.6.4`)

| Obs. | Pasajes del tribunal | Archivo:linea |
|---|---|---|
| C-01 | §4.2 p. 37; §4.4 p. 40; Tabla 4; §4.8 p. 51; I.1 p. 150; §7.3 p. 76 | `04:16`, `04:46` (ventana y "en su domicilio"), `04:78`, `04:97`, `04:117` (primera amenaza), `12:241` (165,3 s), `11:34` (11/09 y 09/10); fuente del cronograma `docs/diagrams/cronograma.md:39`, `:74` |
| C-02 | p. 45 y octava amenaza p. 53; Tabla 3 p. 39; §1.2 p. 12; Resumen, Abstract; §8.1; Tablas 10 y 23; Anexo K | `04:89`, `04:131`, `04:31`, `01:18` ("midio el tiempo de registro incidente por incidente con cronometraje en vivo"), `00-resumen.tex:13`, `:29`, `07:15-30`, `07:36-62`, `09:15-30`, `12:349-370`; tambien `08:22`, `08:116` (ya mencionan la carga estimada) |
| C-03 | p. 45; p. 52; Tabla 12 p. 85; sexta amenaza §4.8 | `04:89` (lectura en voz alta), `04:97` (grabacion acotada a 45 s), `04:127` (sexta amenaza), `07:74` (87,2 / 20,09 / 77,0 %) |
| C-04 | §4.5 p. 43; §8.1 p. 85 | `04:66` y `04:79` ("118 de 119") frente a `07:38` ("119 ... sin registro primario conservado") |
| C-05 | §7.2 p. 73; §7.3 pp. 75-76; §7.5 pp. 78-79 | `11:16`, `11:32` (notificacion del 2026-10-01; refutacion de v1.6.0), `11:46` (titulares = responsables), `11:52` |
| C-06 | §7.2 p. 73 | `11:18` ("Por eso no se requirio autorizacion de esas organizaciones") |
| C-07 | Tabla 26 e I.3 p. 152; I.1 p. 151; §7.5 p. 79; §10.2 p. 120; §4.4 p. 41 | `12:261-275`, `12:279` ("son de los autores"), `12:241` ("redactadas por los autores") frente a `04:46` ("por ese autor"), `11:54` (sin Gemini 3.1) frente a `12:243`, frase repetida en `01:16`, `01:62`, `01:72`, `01:76`, `04:46`, `08:22`, `08:50`, `09:52` (8), `09:48` ("corpus propio de la organizacion"), `04:46` ("en su domicilio") |

### Lo que el repositorio ya responde (busqueda previa a las compuertas)

**C-01. Origen de los 165,3 s y evidencia fechada.**

- **E1.** `165,3` aparece por primera vez el **2026-06-04** en `2e15de9b` ("Se ha propuesto el mapa
  de changes"), dentro de `docs/Tesis/tesis_para_agente.md` (conversion del borrador
  `1_Tesis_Mesa_Ayuda_UTN_FINAL_MEJORADA.docx`): "media aritmetica del tiempo manual ... 165,3
  segundos ... desvio 38,7 ... rango 96 a 289", junto con 18,2 s, 89 %, Wilcoxon p < 0,001 y
  exactitud 92 %. El 2026-06-10 (`826757b2`) la KB repite "registro manual previo de 165,3 s".
  Es decir, el borrador ya traia resultados completos al inicio de la ventana declarada
  (junio-agosto) y antes de cualquier rastro de la hoja de cronometraje.
- **E2.** El **2026-07-03** (`41430a21`, c-26 "corpus simulado") `evaluation/generate_corpus.py`
  genero `tiempo_manual_s` con `rng_tiempos.gauss(165.3, 38.7)` y un desplazamiento de centrado
  para caer en 163-167 s (requisito CORPUS-008); lo confirma la observacion de Engram del
  2026-07-03 ("Manual time mean from clipped gauss(165.3, 38.7) drifts to ~170s"). **Los 165,3 s
  de la version del 3 de julio no los cronometro nadie: son el parametro de un generador
  sintetico, fijado para reproducir la cifra del borrador.** El corpus sintetico se retiro el
  2026-09-11 (`5f21a258`). Lo que solo los autores pueden decir es de donde salio la cifra del
  borrador de junio (estimacion, marcador de posicion, borrador asistido) y si coincide con la
  premisa de 2 min 45 s que c-249 OQ-01 (3) declaro "estimacion a priori genuina".
- **E3. Rastros fechados de los tiempos vigentes (todos posteriores a agosto).** Observacion de
  Engram del **2026-09-16 18:33** ("Converted real 200-case corpus CSV->JSON ... min 10s, max
  300s, mean 61.6s ... CONTRADICTS the thesis claim of 165.3s"); `.gitignore` con
  `data/Corpus Tesis*` en `d8b41156` (**2026-09-17**); prueba de `c8f82892` (**2026-09-29**) con
  la fila `R001`, Correo, Seguridad Informatica, **75 s**, identica a la hoja versionada;
  versionado de la hoja pseudonimizada y del JSON en `ea625764` (**2026-10-09**). En el
  repositorio no hay rastro de la campana entre junio y agosto: 0 commits en agosto y pausa de
  actividad del 2026-07-10 al 2026-09-10 (`docs/diagrams/cronograma.md:72`). La ventana se apoya
  solo en la confirmacion del autor del 2026-10-09 (`dictamen-correcciones.md:179`, fuente de la
  barra `cronograma.md:39`, `:74`). El 2026-09-18 el usuario declaro en Engram que "los tiempos
  son estimados y redondeados a multiplos de 5 s, con contados casos exactos".
- **E4. Posible evidencia fuera del repositorio.** El nombre `Corpus Tesis - Hoja 1.csv` es el que
  Google Sheets asigna al exportar una hoja ("<libro> - <hoja>.csv"); si el original es una hoja
  de Google, su historial de versiones fecharia la carga de los tiempos. `Corpus Tesis.xlsx`
  tiene metadatos de creacion y modificacion (`docProps/core.xml`). El agente no tiene acceso a
  ninguno: es una hipotesis que los autores confirman o descartan.
- **E5. Tension.** `04:97` dice "Ese registro no se conserva en su forma original", pero
  `data/README.md:55` lista `Corpus Tesis.xlsx` y `Corpus Tesis - Hoja 1.csv` como originales no
  versionados, y `1e86c58e` (**2026-11-12**, c-201) regenero la hoja pseudonimizada desde el
  original: el original existia al menos en esa fecha. "No se conserva" debe pasar a "no se
  versiona", o declararse cuando y por que se destruyo (enlaza con C-05).

**C-02. Valor del componente de carga.** c-249 OQ-01 (2) registro: "Se sumo un tiempo de carga FIJO
a los 200 casos, ESTIMADO con A1 desde la experiencia profesional (orden de 10 s; la magnitud exacta
no se registro), YA incluido en `tiempo_manual_s`". Ningun codigo, memo ni commit contiene la
constante (busqueda de `10 s`, `carga`, `tiempo_manual` en `evaluation/`, `scripts/`, memos y
Engram). Los datos confirman la incoherencia que senala el tribunal: en
`data/corpus_evaluacion_pseudonimizado.json`, 4 casos de formulario web valen 10 s (minimo del
corpus) y 8 valen <= 15 s; con una constante de 10 s esos 4 casos tendrian lectura 0 s. `R017`
(72 s) es el unico valor que no es multiplo de 5. **El valor exacto no esta en el repositorio:
OQ-02.**

**C-03. Duracion de las grabaciones.** `data/corpus_resultados_telefonia.json` trae
`duracion_segundos` para los 81 casos telefonicos (sin nulos) y el corpus trae
`tiempo_manual_s` y `tiempo_automatizado_s` por caso: **hay datos por par**. Una inspeccion de
control (no citable; las cifras de la tesis saldran del script) muestra que la duracion media de
grabacion es del orden de 7 s, con una sola grabacion en el tope de 45 s, frente a una media
manual telefonica de 87,25 s (canonica, 87,2). Es decir, la asimetria es mayor de lo que sugiere el
calculo del tribunal sobre medias ("unos 77 s" frente a 18,7 s de grabacion mas procesamiento).
La paráfrasis recitada y la lectura completa ya estan descritas en la tesis (`04:89`, `04:97`,
`04:127`): no hace falta compuerta para describirlas; si la hace para el rotulo del veredicto
(OQ-06).

**C-04.** `data/corpus_resultados_web_correo.json` tiene `casos` con `case_id`; `04:66` dice 118 de
119 con `R001` sin registro y que ese registro "respalda la existencia y la procedencia de los
incidentes, no la medicion de extremo a extremo". La formula unica sale del repositorio (sin
compuerta): el script verifica el conteo.

**C-05.** `docs/seguridad/acta-consentimiento-t1.md` (v1, "aprobada/firmada el 2026-10-01") es el
consentimiento de los tres autores para el tratamiento T1 (piloto); `acta-consentimiento-t2.md:84-86`
dice que la notificacion "se realizo el 2026-10-01" y el consentimiento verbal el 2026-10-02. No
hay registro de que se notifico, a quienes (A1 no figura en la tabla de T2) ni por que medio. No
hay en `docs/seguridad/`, `data/README.md` ni en la tesis una regla de custodia ni de destruccion
de los originales con identificadores (`rg -i "destru|plazo de conservaci"` sin resultados
pertinentes); el unico dato es E5 (existian el 2026-11-12). No hay registro de consentimiento de
las personas del circulo de los autores. **OQ-03.**

**C-06.** `11:18` funda la innecesariedad de autorizacion en que no se tratan datos personales ni
informacion reservada; c-249 OQ-02 (5) lo registro como respuesta de los autores. No hay aval del
director ni registro de informacion a los empleadores. **OQ-04.**

**C-07.** El 2026-09-16 una sesion de agente convirtio la hoja a JSON aplicando 40 correcciones a
las descripciones (7 erratas y 33 espacios colgantes; observacion de Engram de esa fecha); la
pseudonimizacion posterior fue determinista (`scripts/corpus_ingest/pseudonymize_corpus.py`,
2026-09-30; regeneracion c-201, 2026-11-12). c-249 OQ-02 (4) registro que las 119 descripciones
"fueron REESCRITAS por los autores y disociadas a un lexico generico"; no consta si esa
reescritura uso un asistente de IA, ni el inventario (`inventario-uso-asistentes-ia.md`) lo
trata. **OQ-05.** Lo demas de C-07 se resuelve con el registro existente: autoria de las 81
reconstrucciones = "un autor" (c-246 OQ-01; c-249 6.6); etiquetado de A1, T1, E1 y E2 (`04:58`);
Gemini 3.1 consta en I.1 (`12:243`).

**Diez preguntas (seccion 6).** 1 y 2 dependen de OQ-01; 3 de OQ-02; 4 y 5 del script; 6 de OQ-05;
7 y 9 de OQ-03; 8 de OQ-04; 10 se responde con cifras canonicas existentes (Anexo K
`subsec:sensibilidad-ajustes`, Tabla 30; brazo Gemini solo de c-215; reparto por etapa de
`tab:exactitud-etapa-canal`), sin computo nuevo.

### Precedentes y reglas vigentes

- c-246 abrio `tesis-reencuadre-cuarta-instancia` y `respuestas-tribunal-cuarta-instancia.md`;
  c-249 fijo el formato de compuertas (respuesta literal, fecha, responsable), la verificacion
  estilo prosa TDD (`rg` ANTES/DESPUES), la regla A de tags (OQ-05 de c-249) y la declaracion del
  exceso de paginas por release ("Presupuesto de paginas preservado": total del PDF, tope 100;
  `v1.6.4` = 157, +57 declarado el 2026-11-24).
- La serie de recomputos usa `evaluation/data/campana/analisis/analisis_<tema>_c<NNN>.{py,json,md,SHA256SUMS.txt}`
  con su prueba al lado; el IC de la reduccion es bootstrap percentil por pares con semilla
  `20261021` y `B = 2000` (`analisis_dictamen_c207.py`, `ic_reduccion_tiempo`); los descuentos de
  5 y 10 s sobre las medias ya existen en `analisis_rango_robustez_tiempos_c226.py` (68,61 % y
  65,57 %) pero sin IC por pares ni corte por canal.
- El Resumen tiene 234 palabras de prosa y el Abstract 232 (c-249): hay margen de unas 16 para
  mencionar el componente estimado.
- `numeros-canonicos.md`: ultima seccion `3.48`; la siguiente libre es `3.49`.

## Goals / Non-Goals

**Goals:**

- Que la cronologia de la campana manual diga exactamente lo que la evidencia sostiene, y que el
  origen de los 165,3 s quede explicado con el registro del repositorio (C-01).
- Que el tiempo manual se lea como lo que es (lectura medida mas un componente estimado) en todo el
  documento, con la reduccion sin el componente y sin telefonia recomputada por pares (C-02, C-03).
- Un solo estado del registro primario (C-04); capitulo legal con la licitud fundada en la
  disociacion y los consentimientos separados (C-05, C-06); coherencia de C-07.
- Respuestas escritas a las diez preguntas; release de defensa `v1.6.5` con el visto bueno del
  director.

**Non-Goals:**

- No inventar ni reconstruir fechas, valores, custodias, consentimientos, avisos a empleadores ni
  usos de IA; no elegir por los autores ninguna rama de las compuertas.
- No copiar cifras del tribunal; no cambiar cifras canonicas vigentes (se agregan las nuevas).
- No editar el JSON del corpus ni la hoja pseudonimizada; no tocar `App/`, `n8n/` ni artefactos
  existentes de `evaluation/`; no mover tags; no hacer llamadas pagas.
- No reescribir el cuerpo de actas firmadas (se agregan anexos de revision fechados, como c-249).

## Decisions

### D1 - Capacidad nueva `tesis-quinta-instancia` y dos MODIFIED

Los requisitos de C-01 a C-07, las respuestas, la transcripcion y la release van en una capacidad
nueva, como c-246 hizo con la cuarta instancia; `tesis-reencuadre-cuarta-instancia` ya tiene 751
lineas y mezclaria dos devoluciones. Regla de c-249 (D1): ADDED salvo que el cuerpo vigente
contradiga lo nuevo. Dos requisitos lo contradicen y van como **MODIFIED** en
`tesis-reencuadre-cuarta-instancia`: "Capitulo 7 reescrito sin base de empleador (R-05)" (su
escenario "Base real del regimen (a) explicada" funda la licitud en el consentimiento del grupo,
art. 5 inc. 1, y dice que los titulares son los integrantes del grupo) y "Titularidad unica del
regimen (a) y tensiones del repositorio explicadas (OQ-02 de c-249)" (exige declarar en §7.5 que
titulares y responsables son las mismas personas). Los demas requisitos vigentes son compatibles:
R-03 y "Instrumento del flujo manual ... (OQ-01 de c-249)" piden declarar fechas y procedencia, lo
que la rama (b) de C-01 cumple; "Flujo manual con lugar, sistema, escucha y definicion unica" pide
una definicion unica del tiempo manual, que C-02 conserva; "Consentimiento verbal y articulo 5"
no exige la frase de refutacion de v1.6.0. En `tesis-numeros-canonicos` se AGREGA el registro de la
seccion `3.49`. Alternativa descartada: todo como ADDED en la capacidad de cuarta instancia; dejaria
dos requisitos vigentes que exigen lo que el tribunal pide retirar.

### D2 - Compuertas OQ-01 a OQ-07 y compuerta externa del director

Cada compuerta bloquea solo sus tareas (ver Open Questions y la marca **[GATED OQ-0n]** de
`tasks.md`). Sin compuerta: el script (grupo 3), la definicion por brazo de la Tabla 3 en lo que no
depende del valor del componente, C-03 salvo el rotulo, C-04, la parte de C-07 ya registrada y la
pregunta 10. Los pasajes tocados desde varios bloques (`04:46`, `04:89`, `04:131`, `11:32`, `11:46`)
se editan una sola vez, en la ultima tarea gated que los toca; las demas remiten a ella. **G-DIR**
(visto bueno escrito del director sobre la version de defensa) es externa al repositorio: se
registra con fecha, medio y alcance (sin reproducir el documento si contiene datos personales) y
bloquea la entrega de la version al tribunal, no el tag.

### D3 - C-01: dos ramas, y el origen de los 165,3 s con evidencia del repositorio

Lo que se escribe sin depender de la rama (con la confirmacion de OQ-01 (1)): I.1 (`12:241`) dice
que los 165,3 s del 3 de julio no fueron un cronometraje sino el parametro de media de un generador
sintetico (`41430a21`), que a su vez reproducia una cifra del borrador de junio (`2e15de9b`), y
como "conviven" ambas cosas: no hubo dos mediciones en el mismo periodo, porque la del 3 de julio
no fue una medicion. **Rama (a)** (OQ-01 (2) aporta evidencia fechada: historial de la hoja de
Google, metadatos del `.xlsx`, mensajes o fotos): §4.2, §4.4, Tabla 4 y §4.8 citan la evidencia con
su fecha y alcance (que casos y que fechas cubre); el extracto se versiona sin datos personales en
`docs/Tesis/Correcciones/` solo con aprobacion de los autores. Si la evidencia cubre parte de la
ventana o parte de los casos, se declara exactamente esa parte. **Rama (b)** (no existe): esos
cuatro lugares y la fuente del cronograma (`cronograma.md:74`, leyenda de `fig:cronograma`) dicen
que la fecha de la campana manual es una declaracion de los autores no verificable, y la primera
amenaza (`04:117`) agrega que el rastro fechado mas temprano de los 200 tiempos es del 2026-09-16
(E3). En ambas ramas `04:97` deja de decir que el registro "no se conserva en su forma original" si
OQ-01 (3) confirma que los originales existen (E5). No hay rama que permita afirmar la ventana sin
calificarla: el tribunal advierte que, sin acreditacion, revisa la nota del capitulo de resultados,
y eso se registra como riesgo aceptado, no se mitiga con redaccion.

### D4 - C-02: definicion por brazo y valor del componente segun OQ-02

**Tabla 3 (`04:31`)**, sin compuerta en la estructura: la fila "Tiempo de registro" se desdobla en
una definicion operacional por brazo: manual = lectura (y, en telefonia, lectura en voz alta)
cronometrada por el par con redondeo hacia arriba a 5 s, mas un componente de carga del ticket
estimado y no medido (ningun ticket se cargo en una herramienta ni se persistio); automatizado =
latencia de extremo a extremo hasta la persistencia confirmada (correo y formulario) o duracion de
la grabacion mas latencia posterior al cuelgue (telefonia). El valor del componente depende de
OQ-02: **(a)** constante conocida `k`: se declara `k`, se explica el minimo de 10 s (lectura de
`10 - k` s) y el script usa `k`; **(b)** variable con regla conocida (por canal, por caso o sumada
antes del redondeo): se declara la regla y, si hay dato por caso, el script la aplica; si no lo
hay, se declara y se trata como (c); **(c)** desconocido: el texto retira "fijo" (o lo mantiene
solo si los autores sostienen que fue una constante cuyo valor no se registro, declarando
expresamente la tension que senala el tribunal y que 4 casos de 10 s implicarian lectura nula con
`k = 10`), informa la magnitud como desconocida y la sensibilidad por pares para `k = 5` y `k = 10`.
La mencion del componente entra en Resumen y Abstract **reemplazando o ajustando** texto para
quedar en <= 250 palabras de prosa, y en `01:18`, §8.1, Tablas 10 y 23 (nota o celda), con remision
al Anexo K.

### D5 - Script de recomputo por pares, Strict TDD

`evaluation/data/campana/analisis/analisis_quinta_instancia_c250.py`, solo lectura, determinista,
offline, biblioteca estandar mas lo que ya usan c-207 y c-226 (importar `ic_reduccion_tiempo` y los
lectores existentes en lugar de duplicarlos, si la importacion no arrastra `app.*`; si la arrastra,
replicar la funcion con la misma semilla y documentarlo). Prueba primero:
`test_analisis_quinta_instancia_c250.py` (patron de `test_analisis_rango_robustez_tiempos_c226.py`).

- **Entradas:** `data/corpus_evaluacion_pseudonimizado.json` (`tiempo_manual_s`,
  `tiempo_automatizado_s`, `canal_origen`), `data/corpus_resultados_telefonia.json`
  (`case_id`, `duracion_segundos`), `data/corpus_resultados_web_correo.json` (`casos[].case_id`).
- **Funciones (cada una con >= 2 casos de prueba):** `reduccion_pareada(pares, descuento_s)`
  (media manual con descuento, media automatizada, `R = 1 - media_aut / media_man`, diferencia de
  medias, conteo de pares con lectura `<= 0` tras el descuento, sin truncar); `ic_bootstrap_pares`
  (percentil 95 %, semilla `20261021`, `B = 2000`, remuestreo de pares); `wilcoxon_pares` (W y p
  bilateral, con la implementacion ya usada por la serie); `escenarios(casos, descuentos)` para
  {200 pares, 119 sin telefonia, 81 telefonicos} x {0, 5, 10 s y el `k` de OQ-02 si existe};
  `grabaciones_frente_a_lectura(casos, telefonia, descuento_s)` (media, mediana, maximo y conteo en
  el tope de 45 s de las 81 duraciones; lectura manual por par con descuento; diferencia y cociente
  por par, media e IC); `registro_primario(web_correo, casos)` (cuantos de los 119 tienen fila y
  cuales faltan).
- **Anclas que abortan antes de escribir:** 71,16 % (0 s, 200), 68,61 % (5 s), 65,57 % (10 s), IC
  `[0,6716; 0,7459]` (c-207), 87,25 / 20,09 / 77,0 % (telefonia), medias 61,585 y 17,76, 118/119 con
  `R001` ausente.
- **Salidas:** `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF, claves ordenadas, dos corridas
  identicas byte a byte; SHA-256 contra el blob de git por `core.autocrlf=true`). Registro en la
  seccion aditiva `3.49` de `numeros-canonicos.md` con procedencia por valor y estado `vigente
  (nuevo)` o `condicional` (los escenarios de `k` sin valor declarado son sensibilidad, no
  estimacion). Si `k` llega despues de la corrida, se agrega el escenario y se regenera (nuevo
  SHA-256 registrado).

Alternativa descartada: usar las cifras del tribunal o del c-226 sobre medias; el tribunal pide
"recalcular por pares con su intervalo".

### D6 - C-03: asimetria declarada y sub-hipotesis 1 sin telefonia

La sexta amenaza (`04:127`) se amplia con la asimetria de entradas (lectura completa en voz alta
frente a paráfrasis recitada, grabacion acotada a 45 s) y la duracion media de las 81 grabaciones
frente a la lectura manual, con cifras del script. §8.1 y Tabla 12 (nota) informan la
sub-hipotesis 1 sobre los 119 pares de correo y formulario con su IC y su Wilcoxon, y la reduccion
telefonica queda rotulada como contraste de entradas no equivalentes. El rotulo del veredicto
("confirmada") en Tablas 10 y 23, `09:6`, `08:8` y Resumen se decide en **OQ-06**, con la salida del
script a la vista: (a) conservar "confirmada" con el contraste sin telefonia como lectura principal
y la telefonia como cota no comparable; (b) "confirmada en correo y formulario; no evaluable en
telefonia"; (c) otra formula de los autores. El agente MUST NOT cambiar el rotulo sin la respuesta.

### D7 - C-04: una sola formula del registro primario

`04:66`, `04:79` y `07:38` dicen lo mismo, tomado del script: 118 de los 119 tiempos automatizados
de correo y formulario tienen registro primario versionado de las marcas de la base
(`corpus_resultados_web_correo.json`; `R001` sin registro), que respalda la existencia de los
incidentes y no la medicion de extremo a extremo; los 81 telefonicos tienen registro primario en
`corpus_resultados_telefonia.json`; los 200 tiempos manuales, el registro pseudonimizado de la
hoja de campana con resolucion de 5 s (y, segun OQ-01, el estado de los originales).

### D8 - C-05 y C-06: capitulo legal, texto aprobado antes de escribir

Sin elegir por los autores: (1) §7.5 y §7.3 separan el consentimiento de los colaboradores (autores
y `A1`, acta T2, consentimiento verbal del 02/10, constancia del 20/11) de la situacion de los
titulares de los incidentes (personas del circulo y reportantes), sobre quienes se declara lo que
diga OQ-03 (2); (2) se retiran `11:46` ("titulares y responsables son las mismas personas") y, en
`11:32`, la frase que presenta el consentimiento del 02/10 como refutacion de lo dicho en v1.6.0
sobre los titulares; (3) la licitud del tratamiento del corpus se funda en la disociacion (arts. 2
y 28 de la Ley 25.326) y se acota la fase previa (originales con identificadores en poder de quien
diga OQ-03 (3)), con destino y fecha o evento de destruccion; (4) "notificacion a los integrantes
del grupo" se define con OQ-03 (1); (5) `11:18` lleva el aval escrito del director o la declaracion
de si los empleadores fueron informados, con mencion del deber de confidencialidad (art. 10),
segun OQ-04. Se propagan a `docs/seguridad/acta-consentimiento-t2.md` (anexo de revision fechado,
sin reescribir el cuerpo firmado), `registro-actividades-tratamiento.md`, `data/README.md` y
`docs/defensa/respuestas-tribunal.md` si repiten las frases retiradas. Dominio HIGH.

### D9 - C-07 sin inventar

Tabla 26 recibe una fila "Corpus (descripciones del regimen (a))": la correccion de 40 erratas y
espacios en la conversion del 2026-09-16 por una sesion de agente es un hecho del repositorio y
figura en todas las ramas; si la reescritura previa uso IA se declara segun OQ-05. I.3 (`12:279`):
"la recoleccion de datos ... son de los autores" pasa a nombrar que el etiquetado lo hicieron
`A1`, `T1`, `E1` y `E2` y el cronometraje `A1` y `T1`. "Por los autores" (`12:241`) pasa a "por un
autor" (registro de c-246 y c-249). §7.5 (`11:54`) menciona Gemini 3.1 como en `12:243`. La frase
"dispositivo de dimensionamiento y no el lugar de recoleccion" queda solo en `04:46` (definicion
en el metodo); las otras siete ocurrencias se reformulan o remiten. `09:48` sin "corpus propio de
la organizacion". "En su domicilio" (`04:46`) se aclara con OQ-01 (4).

### D10 - Release `v1.6.5`, regla A y paginas

Convencion de la serie: releases de correccion sobre el mismo ejemplar incrementan el parche
(`v1.6.1` a `v1.6.4`); c-250 no cambia cifras canonicas, solo agrega lecturas y corrige prosa, por
lo que corresponde **`v1.6.5`**, confirmada por autores y director en OQ-07 (que puede preferir
`v1.7.0` para marcar la version de defensa; el diseno no depende del numero). Regla A de tags
(c-249 OQ-05, requisito vigente de `tesis-document`): tag anotado sobre C3 (texto y PDF
recompilado), hash en C4, sin mover tags publicados. Recompilacion con Docker `texlive-thesis`
(`MSYS_NO_PATHCONV=1`, `latexmk main.tex`); total de paginas medido y declarado en el libro mayor
con la decision de los autores de sostener el exceso (OQ-07 (2)); el agregado de filas al Anexo K y
la Tabla 3 desdoblada suman paginas, que se compensan solo con palancas de forma.

### D11 - Verificacion estilo prosa TDD y TDD real en el script

Cada tarea de prosa corre un `rg` ANTES (defecto) y DESPUES (estado deseado), registrados en la
seccion c-250 de `dictamen-correcciones.md`; patrones con `.` en lugar de vocales acentuadas. Las
lineas de este diseno son las de `v1.6.4`; el apply las re-verifica. El script sigue
RED-GREEN-TRIANGULATE-REFACTOR con `pytest` corrido desde `evaluation/` con las variables dummy
del CI (memoria del entorno: el venv `v313` puede estar roto; la biblioteca estandar alcanza si no
se importa `app.*`).

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente fecha la campana, fija `k`, nombra custodios o declara avisos a empleadores] | OQ-01 a OQ-05 bloqueantes; ramas listadas sin elegir; escenario "sin respuesta, la tarea queda bloqueada" |
| [C-01 no acreditable: el tribunal revisa la nota del capitulo de resultados] | Rama (b) honesta; se registra como riesgo aceptado; la respuesta 2 lo dice |
| [Copiar cifras del tribunal] | D5: anclas y salida versionada; `cotejar_cifras_respuestas.py` sobre las respuestas |
| [Cambiar el veredicto de la sub-hipotesis 1 sin ratificacion] | OQ-06 con la salida del script a la vista |
| [Resumen o Abstract > 250 palabras] | D4: reemplazar; conteo ANTES/DESPUES |
| [Mas paginas] | D10: declaracion del exceso por decision registrada (OQ-07) |
| [Editar actas firmadas] | Anexo de revision fechado, como c-249 3.10 |
| [Nombres reales o correspondencia alias-identidad] | Solo alias (`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); barrido del diff |
| [Publicar evidencia con datos personales (historial de la hoja, mensajes)] | Solo extractos sin datos personales y con aprobacion de los autores (HIGH) |
| [Gitleaks por "capitulo" + coma + archivo en prosa] | Escribir "seccion N (`archivo.tex`)" |

## Migration Plan

1. Presentar OQ-01 a OQ-07 (OQ-04 y OQ-07 tambien al director) y registrar las respuestas literales
   con fecha y responsable en la seccion c-250 de `dictamen-correcciones.md`.
2. Sin esperar respuestas: script (grupo 3), C-03 salvo rotulo, C-04, C-07 registrado, Tabla 3 en
   estructura, pregunta 10.
3. Aplicar los bloques gated a medida que llegan las respuestas; regenerar el script si OQ-02 da `k`.
4. Coherencia, respuestas escritas, release `v1.6.5` (OK de autores), G-DIR y entrega.

Rollback: hasta el commit de la release todo es prosa y un script aditivo sin commit; se revierten
los archivos tocados. El tag no se publica hasta verificar el commit que lo recibe.

## Open Questions

- **OQ-01 (autores; C-01; bloquea 4.1 a 4.4 y la parte de 9.6 sobre el domicilio).**
  (1) Confirmar E1-E2: los 165,3 s del 3 de julio fueron el parametro de media de
  `generate_corpus.py`, no un cronometraje. ¿Que era la cifra de 165,3 s del borrador de junio
  (`2e15de9b`): una estimacion propia, un valor de marcador de posicion, un texto producido con un
  asistente? ¿Es la misma premisa de 2 min 45 s? (2) ¿Existe evidencia fechada de que los 200
  tiempos se cronometraron entre junio y agosto: historial de versiones de la hoja "Corpus Tesis"
  (si es de Google), metadatos de `Corpus Tesis.xlsx`, mensajes, fotos? Si existe: que fechas
  muestra, que casos cubre y si puede versionarse un extracto sin datos personales. Si no existe:
  aprobar la rama (b). (3) ¿Siguen existiendo los originales (`Corpus Tesis.xlsx`,
  `Corpus Tesis - Hoja 1.csv`, hoja en linea)? (E5: existian el 2026-11-12.) (4) "En su
  domicilio": ¿en el domicilio de quien (de `A1`, de `T1`, de cada uno por turno)?
- **OQ-02 (autores, con `A1`; C-02; bloquea 5.2 a 5.4 en lo que depende del valor).** (1) ¿El
  componente fue una constante? Si si, ¿cual es su valor exacto `k`? (2) Si vario: ¿con que regla
  (por canal, por caso, segun la complejidad) y queda algun dato por caso? (3) ¿Se sumo antes del
  redondeo a 5 s o el par anotaba directamente el total? (4) ¿Como se obtuvieron los 4 casos de
  formulario de 10 s (lectura de 0 s si `k = 10`)? (5) Si no se sabe: aprobar la rama (c) (magnitud
  desconocida, "fijo" retirado o declarado en tension, sensibilidad 5 y 10 s).
- **OQ-03 (autores; C-05; HIGH; bloquea 8.1 a 8.3).** (1) ¿Que fue la "notificacion a los
  integrantes del grupo" del 2026-10-01: que se informo, a quienes (los tres autores, `A1`), por
  que medio, y si es el acta T1 firmada ese dia? (2) ¿Que consentimiento dieron, si alguno, las
  personas del circulo de los autores que reportaron incidentes del regimen (a)? (3) ¿Quien guarda
  hoy los originales con identificadores (la hoja, el `.xlsx`, el `.csv`), donde, y cuando se
  destruyen (fecha o evento: aprobacion de la tesis, defensa, plazo)? ¿O ya se destruyeron, y
  cuando? (4) Aprobar el texto de la licitud por disociacion (arts. 2 y 28) y la separacion de
  consentimientos.
- **OQ-04 (autores y director; C-06; HIGH; bloquea 8.4).** (1) ¿Los empleadores de los autores
  (los de los sistemas de los originales del regimen (a) y el del puesto de trabajo del regimen
  (b)) fueron informados de que incidentes de su operacion forman parte del corpus? (2) ¿El
  director avala por escrito la afirmacion "no se requirio autorizacion de esas organizaciones"?
  (fecha y medio del aval). (3) Aprobar el texto con la mencion del deber de confidencialidad
  (art. 10).
- **OQ-05 (autores; C-07; bloquea 9.1 en lo que toca a la reescritura).** ¿Se uso un asistente de
  IA para reescribir o disociar las 119 descripciones del regimen (a) antes de la hoja? Si si:
  herramienta, que produjo y como se verifico (para la fila de la Tabla 26 y el inventario).
- **OQ-06 (autores; C-02/C-03; bloquea 6.3 y el rotulo en 5.4).** Con la salida del script a la
  vista: rotulo de la sub-hipotesis 1 segun D6 (a), (b) o (c), y la oracion del Resumen y el
  Abstract.
- **OQ-07 (autores y director; bloquea el grupo 12).** (1) Version `v1.6.5` (o `v1.7.0`). (2)
  Decision sobre el total de paginas medido (sostener y declarar el exceso, o reducir con palancas
  de forma). (3) OK para commits, tag y merge.
- **G-DIR (director; externa).** Visto bueno escrito sobre la version de defensa: fecha, medio y
  version a la que se refiere. Bloquea la entrega al tribunal (12.8), no el tag.
