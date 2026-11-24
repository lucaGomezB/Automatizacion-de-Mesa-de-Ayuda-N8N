# Tasks: Aplicar las recomendaciones del dictamen sobre v1.6.3

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`D/` = `auditorias/Dictamen_Tesis_v10_v1.6.3_CONEAU_2026-11-23.md`; `E/` =
`evaluation/data/campana/analisis/`. Lineas de `main` `44320fd0` (identicas a `v1.6.3` en `S/`,
verificadas en el propose); el apply las re-verifica con `rg` antes de editar, porque las ediciones
las desplazan. Equivalente de Strict TDD para prosa: cada tarea de edicion corre una verificacion
ANTES (muestra el defecto) y DESPUES (estado deseado), y ambas salidas se registran en
`C/dictamen-correcciones.md` seccion `c-249`. Reglas: no commitear, taggear ni pushear sin pedido
expreso; no cambiar cifras canonicas, citas ni conclusiones sin ratificacion de autores; espanol
rioplatense formal sin emojis; solo alias (`E1`, `E2`, `O1`, `O2`, `A1`, `T1`), nunca nombres
reales ni la correspondencia alias-identidad; no tocar `App/`, `n8n/`, los artefactos existentes de
`evaluation/` ni los casos ni el JSON del corpus. Marcas: **[GATED OQ-0n]** = bloqueada hasta que
la respuesta figure en la tabla de compuertas de c-249; sin marca = aplicable sin compuerta.
Dominio HIGH (`S/11-aspectos-legales.tex`, `docs/seguridad/`, `data/README.md`, grupo 10): mostrar
el texto propuesto a los autores antes de escribir. Gobernanza del change: MEDIUM.

## 1. Guardas y linea base

- [ ] 1.1 Leer `proposal.md`, `design.md` (D1-D11, OQ-01 a OQ-06), los dos deltas de `specs/` y
  `D/` completo (veredicto 1 a 7, recomendaciones 1 a 14, Anexos B, C y D). Verificacion:
  `git diff --stat v1.6.3 HEAD -- "docs/Tesis/v10 (IA)" data` vacio (las lineas del dictamen siguen
  vigentes) o, si no lo esta, lista de desplazamientos registrada.
- [ ] 1.2 Linea base de cifras canonicas y conteos. Verificacion: `rg -c "61,6|17,76|71,2|73,5|W = 363|0,6508|25,47|18,7|43,1|898,8" S/`
  y el conteo de palabras de prosa del Resumen (248) y del Abstract (246) con la regla de la spec
  (`tesis-document`, "English abstract"), registrados en la seccion c-249.
- [ ] 1.3 Registrar `git rev-parse v1.6.2^{commit}` (`e7013127...`), `git rev-parse v1.6.3^{commit}`
  (`f8618bdd...`) y `sha256sum data/corpus_evaluacion_pseudonimizado.json` (`1fd17d7e...`) como
  valores que el apply MUST NOT cambiar.
- [ ] 1.4 Red de seguridad: `python "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS;
  `pytest "docs/Tesis/v10 (IA)" E/` en verde (conteo registrado); `openspec validate --all --strict`
  sin fallos. Si algo falla antes de editar, se reporta como falla preexistente y no se corrige aqui.

## 2. Compuertas de autores y director

- [x] 2.1 **[COMPUERTA OQ-01]** Presentar a los autores las cuatro preguntas de OQ-01 de
  `design.md` (que quedo del cronometraje; busqueda y carga del ticket; origen de los 2 min 45 s;
  ventana junio-agosto) con las opciones D3 (a), (b), (c). Registrar respuesta literal, fecha y
  responsable. Verificacion: la fila existe; sin ella, 3.1 a 3.3 quedan bloqueadas.
- [ ] 2.2 **[COMPUERTA OQ-02]** Presentar las siete preguntas de OQ-02 (reportantes D4 a/b/c;
  titulares = responsables; PII de los originales; texto de origen o reescritura; empleadores;
  formula de `01:72`; quien "recolecto" segun c-246 OQ-01). Verificacion: la fila existe; sin
  ella, 3.4 a 3.7 quedan bloqueadas.
- [ ] 2.3 **[COMPUERTA OQ-03]** Presentar las cinco preguntas de OQ-03 (orden corrida/consentimiento
  del 2-10; corridas 21-09 a 1-10 y dashboard; constancia contemporanea; texto de la brecha del
  art. 5; vocabulario del acta T2 §2). Verificacion: la fila existe; sin ella, 3.8 a 3.10 quedan
  bloqueadas.
- [ ] 2.4 **[COMPUERTA OQ-04]** Presentar las cinco preguntas de OQ-04 (sub-hipotesis 2 D7 a/b y
  nombre de la variable; consenso de la sub-hipotesis 3; OE2; fila del OE3; `01:38`), con las
  cifras del recomputo de 4.3 a la vista. Verificacion: la fila existe; sin ella, 5.1 a 5.4 quedan
  bloqueadas.
- [ ] 2.5 **[COMPUERTA OQ-05]** Presentar a autores y director la regla de tags D8 (A)-(D), la
  version `v1.6.4`, la Nota de versiones con `v1.6.2`/`v1.6.3`/erratum y la cifra del inventario de
  IA. Verificacion: la fila existe con ambos responsables; sin ella, 7.1 y el grupo 10 quedan
  bloqueados.
- [ ] 2.6 **[COMPUERTA OQ-06]** Presentar el tope de paginas (declarar y sostener o reducir) y
  pedir a los autores las cifras de Paket y la relectura de Revina desde sus copias. Verificacion: la
  fila existe; sin ella, 8.4 y la parte de Paket/Revina de 7.5 quedan bloqueadas.

## 3. Bloque A - Veracidad y licitud (recomendaciones 1 a 3 y 7; gated)

- [x] 3.1 **[GATED OQ-01]** `S/04-marco-metodologico.tex:97`: reescribir el segundo instrumento
  segun D3 y OQ-01 (sin describir como existente una planilla inexistente; remitir a
  `tiempo_manual_s`). Verificacion ANTES: `rg -n "planilla de cronometraje observacional" S/04-marco-metodologico.tex`
  devuelve `:97`; DESPUES: 0 coincidencias en indicativo de existencia y el texto coincide con OQ-01.
- [x] 3.2 **[GATED OQ-01]** `S/04-marco-metodologico.tex:117` (primera amenaza) con la falta de
  registro primario; `:89` (que se busco y que campos se completaron) y nueva amenaza de constructo
  (tarea sobre planilla frente a extremo a extremo) en §4.8 (`:115-129`, ajustar el cardinal
  "siete amenazas" si cambia); `S/09-conclusiones.tex:27` (fila OE5) y `S/01-introduccion.tex:54`
  acotados. Verificacion ANTES: `rg -n "registro primario" S/04-marco-metodologico.tex` = 0 y
  `rg -n "siete amenazas" S/04-marco-metodologico.tex`; DESPUES: >= 1 en la primera amenaza, cardinal
  coherente, fila OE5 y `01:54` acotadas.
- [x] 3.3 **[GATED OQ-01]** `S/04-marco-metodologico.tex:46` (ventana "junio a agosto" como
  declaracion sin registro fechado) y `S/01-introduccion.tex:18` (origen de la premisa de 2 min
  45 s, si los autores lo confirman). Verificacion ANTES: `rg -n "recogidos entre junio y agosto" S/04-marco-metodologico.tex`
  devuelve `:46` sin calificacion; DESPUES: la ventana lleva la clausula declarativa y el origen de
  la premisa coincide con OQ-01 (3).
- [ ] 3.4 **[GATED OQ-02]** Formula unica de reportantes en `S/04-marco-metodologico.tex:46`,
  `S/11-aspectos-legales.tex:16`, `:40`, `:48` (D4) y, si corresponde, la declaracion "titulares y
  responsables del tratamiento son las mismas personas" en §7.5. Verificacion ANTES:
  `rg -n "reportados por los integrantes del entorno operativo|propio grupo de desarrollo" S/`
  devuelve las dos formulas (`04:46`, `11:16`, `11:48` frente a `11:40`); DESPUES: una sola formula.
- [ ] 3.5 **[GATED OQ-02]** "Se redactaron" (`S/04-marco-metodologico.tex:46`) frente a "coinciden
  con el texto de origen" (`S/12-anexos.tex:153`); si hubo reescritura, extender la septima amenaza
  (`S/04-marco-metodologico.tex:129`) y la fila del OE2 (`S/09-conclusiones.tex:24`) a los 200
  casos. Verificacion ANTES: `rg -n "coinciden con el texto de origen" S/12-anexos.tex` y
  `rg -n "se redactaron en tercera persona" S/04-marco-metodologico.tex`; DESPUES: descripcion
  coherente en ambos lugares y amenaza ajustada segun OQ-02 (4).
- [ ] 3.6 **[GATED OQ-02]** (HIGH) `data/README.md:53` (que PII y de quien), coherente con
  `S/11-aspectos-legales.tex:24` y `S/12-anexos.tex:151`; parrafo de empleadores reales en §7.2 o
  §7.5 (`S/11-aspectos-legales.tex`, ademas de `:48`). Verificacion ANTES: `rg -n "contienen PII" data/README.md`
  devuelve `:53`; DESPUES: el parrafo dice que datos y de quien, y `rg -n "empleador" S/11-aspectos-legales.tex`
  >= 1 fuera de la validacion retirada.
- [ ] 3.7 **[GATED OQ-02]** `S/01-introduccion.tex:72`: retirar o acotar "el corpus no proviene de
  una organizacion real" con la formula de OQ-02 (6), coherente con `:16` y `S/12-anexos.tex:239`;
  quitar "recolectado en el entorno operativo" para las 81 reconstrucciones; `:62` ("La evidencia
  recogida en el entorno operativo... cuantifica el ahorro bruto": el ahorro sale de la tarea de
  laboratorio). Verificacion ANTES: `rg -n "no proviene de una organizaci.n real|evidencia recogida en el entorno" S/01-introduccion.tex`
  devuelve `:62`, `:72`; DESPUES: formula de OQ-02 y 0 coincidencias de la frase original.
- [ ] 3.8 **[GATED OQ-03]** (HIGH) `S/11-aspectos-legales.tex:30`: "consentimiento expreso" pasa a
  "consentimiento verbal del 2-10-2026, confirmado por escrito el 20-11-2026"; brecha frente al
  art. 5 con el texto aprobado; transferencias ordenadas respecto del consentimiento; corrida del
  2-10 ubicada. Verificacion ANTES: `rg -n "consentimiento expreso|posteriores a la notificaci.n" S/11-aspectos-legales.tex`
  devuelve `:30`; DESPUES: coincide con OQ-03 (1) y (4).
- [ ] 3.9 **[GATED OQ-03]** (HIGH) `S/11-aspectos-legales.tex:30`: declarar el periodo 21-09 a
  1-10 (envios a Gemini y naturaleza de los incidentes del dashboard de `S/06-implementacion.tex:111`,
  cuya leyenda se ajusta si corresponde) y reemplazar "fue un desliz de redaccion" por la constancia
  contemporanea o su inexistencia. Verificacion ANTES: `rg -n "desliz" S/11-aspectos-legales.tex`
  devuelve `:30`; DESPUES: 0 coincidencias sin respaldo y la declaracion del periodo figura.
- [ ] 3.10 **[GATED OQ-03]** (HIGH) `docs/seguridad/acta-consentimiento-t2.md:28-44` (§2) y `:68`
  (§3) con el vocabulario de `11:30` (consentimiento verbal, confirmacion escrita; regimen (b) con
  origen y contenido distinguidos); respuesta 7 de `C/respuestas-tribunal-cuarta-instancia.md`
  (`:73-74`) alineada. Verificacion ANTES: `rg -n "de forma expresa|sin datos de terceros|sin$" docs/seguridad/acta-consentimiento-t2.md`;
  DESPUES: mismo vocabulario en acta, tesis y respuestas.

## 4. Recomputo por regimen y de la sonda (recomendaciones 4 y 6; TDD real)

- [ ] 4.1 RED: escribir `E/test_analisis_regimen_c249.py` (patron de `E/test_analisis_balance_neto_c236.py`)
  con datos sinteticos minimos: exactitud por regimen desde `canal_origen` (telefono = regimen (b)),
  intervalo de Wilson al 95 %, proporciones 25/200 y 25/147 con binomial unilateral frente a 0,15,
  y extraccion del p95 de N8N en el nivel 5 de una corrida y del subconjunto deterministico.
  Verificacion: `pytest E/test_analisis_regimen_c249.py` falla porque el modulo no existe.
- [ ] 4.2 GREEN y TRIANGULATE: implementar `E/analisis_regimen_c249.py` con el minimo para pasar;
  agregar al menos un segundo caso por comportamiento (p. ej. regimen sin aciertos; nivel ausente).
  Verificacion: `pytest E/test_analisis_regimen_c249.py` en verde con >= 2 casos por funcion.
- [ ] 4.3 Ejecutar el script sobre `data/corpus_evaluacion_pseudonimizado.json`,
  `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`,
  `evaluation/data/campana/intervenciones.csv`, `evaluation/evidence/load_test_inferencia_2026-11-17.json`
  y `..._ampliada_2026-11-18.json`; escribir `E/analisis_regimen_c249.{json,md,SHA256SUMS.txt}`.
  Verificacion: el JSON reproduce las cifras canonicas de control (147/200, 53/81, 51/66, 43/53) y
  registra las nuevas; toda diferencia con el dictamen (94/119, 53/81, [0,708; 0,854],
  [0,546; 0,749], 3.660,4 ms, 5.024,7 ms, p = 0,28) se consigna en la seccion c-249.
- [ ] 4.4 REFACTOR: nombres y constantes; `pytest E/` completo en verde (mismo conteo base de 1.4
  mas los nuevos). Verificacion: suite en verde.

## 5. Veredictos e hipotesis (recomendacion 4 y 12 en lo que toca a objetivos; gated)

- [ ] 5.1 **[GATED OQ-04]** Sub-hipotesis 2: `S/07-resultados.tex:184`, `S/09-conclusiones.tex:6`
  (y `S/07-resultados.tex:10` si repite el rotulo) segun D7 (a), o `S/01-introduccion.tex:34` y
  `S/04-marco-metodologico.tex:109` con la enmienda post hoc declarada segun D7 (b); un solo nombre
  de la variable ("requieren accion manual" frente a "cambiaron la derivacion"). Cifras desde
  `E/analisis_regimen_c249.json`. Verificacion ANTES: `rg -n "lectura literal de la regla|acci.n manual|cambiaron la derivaci.n" S/`;
  DESPUES: el criterio que decide coincide con el enunciado y la variable tiene un nombre.
- [ ] 5.2 **[GATED OQ-04]** Sub-hipotesis 3 con consenso: `S/07-resultados.tex:153` y
  `S/08-discusion.tex:62` ("se refuta igualmente; solo el limite superior del intervalo (0,856)
  supera el umbral"). Verificacion ANTES: `rg -n "ser.a no concluyente" S/07-resultados.tex S/08-discusion.tex`
  devuelve `:153`, `:62`; DESPUES: 0 coincidencias.
- [ ] 5.3 **[GATED OQ-04]** Objetivos: OE2 (`S/01-introduccion.tex:48` y fila `S/09-conclusiones.tex:24`)
  segun OQ-04 (3); fila OE3 (`S/09-conclusiones.tex:25`: "no sostenida", exclusion de correo y
  telefonia del test de carga, remision a `tab:tiempos-canal` en lugar de `tab:exactitud-etapa-canal`);
  fila OG (`:22`) con "cota superior" y "tarea de laboratorio". Verificacion ANTES:
  `rg -n "exactitud-etapa-canal" S/09-conclusiones.tex` devuelve `:25`; DESPUES: remision correcta y
  veredictos coincidentes con OQ-04.
- [ ] 5.4 **[GATED OQ-04]** `S/01-introduccion.tex:38`: "La de eficiencia no se contrasta en este
  trabajo; la de integracion, solo en su dimension de capacidad"; "accesibilidad" y "dispersion"
  operacionalizadas o retiradas; OG (`:42`) dice que se evalua un prototipo. Verificacion ANTES:
  `rg -n "se informa en el Cap|accesibilidad|dispersi.n" S/01-introduccion.tex`; DESPUES: sin promesa
  de contraste inexistente.

## 6. Reencuadre y lectura por regimen (recomendaciones 5 y 6; sin compuerta)

- [ ] 6.1 `S/00-resumen.tex:11-15` y `:27-31`: oracion de escenario, composicion 119/81 (81
  redactadas por un autor) y tarea de laboratorio; "1~USD trimestral" rotulado "sobre el volumen
  supuesto"; reemplazar, no agregar (D9). Verificacion ANTES: `rg -n "laboratorio|laboratory|escenario|scenario" S/00-resumen.tex`
  = 0 en los parrafos de metodo y resultados; DESPUES: >= 1 en cada bloque y conteo de prosa <= 250
  por bloque (registrado).
- [ ] 6.2 "Tarea de laboratorio" y fin de la sustitucion: `S/07-resultados.tex:37` ("Este valor
  describe la tarea de laboratorio...; el parametro de 2 minutos 45 segundos es una premisa del
  escenario y no se compara con esta medicion"), `S/01-introduccion.tex:18`, `S/09-conclusiones.tex:6`,
  `:22` (si 5.3 no lo hizo), `:41`. Verificacion ANTES: `rg -n "sustituye, como lectura vigente" S/`
  devuelve `07:37` y `rg -c "laboratorio" S/07-resultados.tex S/08-discusion.tex S/09-conclusiones.tex`
  = 0; DESPUES: 0 y >= 1 en `07` y `09`.
- [ ] 6.3 Derivados del volumen y extrapolaciones: `S/08-discusion.tex:72` ("32,2 horas-persona"
  sobre el volumen supuesto), `:118` ("1~USD trimestral" rotulado), `:68` ("En este corpus, el
  tiempo de registro se redujo...; su transferencia a otras organizaciones es una hipotesis por
  validar"), `:42` ("con un corpus del entorno operativo de los autores"), `S/09-conclusiones.tex:47`
  (integrable pero 73,5 % no alcanza el criterio; sin "corpus propio de la organizacion"), `:49`
  (el escenario solo dimensiona el problema). Verificacion ANTES:
  `rg -n "organizaciones medianas con vol.menes|presentado como escenario de referencia|t.cnicamente viable|curado por los autores en un escenario|organizaci.n\b" S/08-discusion.tex S/09-conclusiones.tex`;
  DESPUES: 0 coincidencias de esas formulas.
- [ ] 6.4 Poblacion, universo y muestra: `S/04-marco-metodologico.tex:46` ("El corpus de 200 casos
  se formo por conveniencia con los incidentes disponibles..." en lugar de "De ese universo se tomo";
  coordinar con 3.3, 3.4 y 3.5, que tocan el mismo parrafo), `:50` y `:54` ("N ~ 2.646, supuesto del
  escenario"); `:121` ("en otras organizaciones"). Verificacion ANTES:
  `rg -n "De ese universo se tom.|universo trimestral|otras organizaciones" S/04-marco-metodologico.tex`;
  DESPUES: N rotulado y sin extraccion desde el universo supuesto.
- [ ] 6.5 Residuos del Anexo B del dictamen no cubiertos arriba: `S/01-introduccion.tex:16` (area de
  operaciones y doble carga como premisas), `:22` ("Estos indicadores justifican"), `:48` (corpus
  con reconstrucciones), `S/10-recomendaciones.tex:6` ("en el campo"), `:14` ("sectores
  responsables"), `:38` ("dependencia medida"). Verificacion ANTES:
  `rg -n "doble carga|indicadores justifican|en el campo|sectores responsables|dependencia medida" S/`;
  DESPUES: 0 que presenten el escenario como operacion o una propiedad como medicion.
- [ ] 6.6 Lectura por regimen con cifras de `E/analisis_regimen_c249.json`: `S/08-discusion.tex:18`
  (canal telefonico = regimen (b); exactitud por regimen con Wilson); `:50` (81 de 200, 40,5 %,
  "declaracion de los autores, sin registro de procedencia por caso"); autoria unificada a "un
  autor" en `:50`, `S/09-conclusiones.tex:24`, `:53`, `S/10-recomendaciones.tex:26` conforme al
  registro de c-246 OQ-01 (`C/dictamen-correcciones.md`, seccion c-246; si 3.5 extiende la
  coautoria, se respeta). Verificacion ANTES: `rg -n "r.gimen" S/08-discusion.tex` sin cifras por
  regimen y `rg -n "redactad[ao]s? por los autores" S/` lista las discordancias; DESPUES: cifras del
  JSON y una sola atribucion.
- [ ] 6.7 `S/07-resultados.tex:376` (y nota de `tab:carga-inferencia`, `:365`): p95 de la corrida
  original en el nivel 5 de N8N y su cumplimiento del techo; subconjunto deterministico de la
  ampliada por encima del techo; la violacion del nivel 5 no es atribuible a la inferencia. Cifras
  del JSON. Verificacion ANTES: `rg -n "3660|3\.660" S/07-resultados.tex` = 0; DESPUES: >= 1 con el
  valor del JSON.

## 7. Consistencia (recomendaciones 7 a 12; sin compuerta salvo donde se marca)

- [ ] 7.1 **[GATED OQ-05]** Release en el texto: `S/12-anexos.tex:60` segun la regla elegida
  (describir que commit apunta el tag y que hash imprime); Nota de versiones `S/12-anexos.tex:235-241`
  con `v1.6.2`, `v1.6.3` y el erratum si OQ-05 (3) lo decide. Verificacion ANTES:
  `rg -n "el PDF compilado en el propio tag no lo imprime" S/12-anexos.tex` devuelve `:60` y
  `rg -n "1\.6\.2|1\.6\.3|erratum" S/12-anexos.tex` en I.1 = 0; DESPUES: texto coherente con la regla
  y la decision de OQ-05 (3).
- [ ] 7.2 Registro de c-248: encabezado `C/dictamen-correcciones.md:7081` ("EN CURSO" pasa a
  "APLICADO/ARCHIVADO (2026-11-22)", tambien el de c-247 en `:6906` si sigue en curso); nota aditiva
  fechada al pie de la tarea 6.3 de
  `openspec/changes/archive/2026-11-22-c-248-publicar-la-release-y-la-nota-de-erratum-de-v1-6-2/tasks.md`
  ("Enmienda c-249: el tag se movio a C4 `f8618bdd` por decision de los autores; ver
  `dictamen-correcciones.md:7093`"). Verificacion ANTES: `rg -n "EN CURSO" C/dictamen-correcciones.md`
  devuelve `:6906`, `:7081`; DESPUES: 0 en esos encabezados y la nota existe sin desmarcar la tarea.
- [ ] 7.3 Corpus y Anexo F: `S/12-anexos.tex:145-153` declara historica la cadena
  `metadata.descripcion` ("200 casos reales", "clasificacion manual") segun D4 (i) de c-247;
  `data/README.md:12` (parrafo de c-242) marcado como superado por el de c-247 (`:17`); referencia
  `\ref{sec:anexo-corpus}` desde §4.4 (`S/04-marco-metodologico.tex:46` o `:48`). El JSON no se edita.
  Verificacion ANTES: `rg -n "anexo-corpus" S/04-marco-metodologico.tex` = 0; DESPUES: >= 1, Anexo F
  con la declaracion y `sha256sum` del JSON igual a 1.3.
- [ ] 7.4 Marco teorico (rec. 11): subseccion breve del modelo economico (costo de derivacion
  erronea, exactitud y costo de equilibrio) con fuente; `S/02-marco-teorico.tex:100` con
  Shapiro-Wilk, Hodges-Lehmann, binomial y tamanos de efecto; quitar duplicados con el cap. 3
  (`02:44-52`/`03:58`, `02:46`/`03:62`, `02:56`/`03:64`, `02:48`/`03:34`); mover a los caps. 4 o 5
  los umbrales y fechas de `02:34`, `02:46`, `02:67`; citar o declarar como supuesto `02:20` (y
  "cuatro etapas secuenciales" de `02:12`). Sin claves bib inventadas. Verificacion ANTES:
  `rg -n "equilibrio|Hodges|Desde el 13 de octubre" S/02-marco-teorico.tex`; DESPUES: la subseccion y
  los metodos figuran, las fechas de implementacion salieron del cap. 2 y `verify_citations.py` PASS.
- [ ] 7.5 Estado del arte (rec. 10): `S/03-estado-del-arte.tex:8` (trabajos anteriores a 2023
  justificados con la regla registrada en `C/bitacora-busqueda-c-110.md` o criterio ajustado; conteos
  por cadena tomados de la bitacora, declarando los que no se registraron); `:22` (Zapier, Make, Power
  Automate citados o reformulados como observacion propia fechada); `:28` (cita o reformulacion);
  `:24` ("requisito no negociable" como premisa del escenario); `:90-92` (brecha acotada al corpus
  propio evaluado dentro de la muestra); **[GATED OQ-06]** `:49` (ficha de Paket) y `:47` (Revina
  1,000). Verificacion ANTES: `rg -n "no negociable|crecimiento considerable|exclusivamente como SaaS|precisamente en esa intersecci.n|no disponibles en el repositorio" S/03-estado-del-arte.tex`;
  DESPUES: 0 de las formulas no respaldadas; Paket y Revina segun OQ-06.
- [ ] 7.6 Implementacion y trabajos futuros (rec. 12): `S/06-implementacion.tex:62`, `:74`, `:97`
  rotulados como observaciones del desarrollo sin medicion o retirados; `:38` ("Function" por nodo
  `code`); subseccion de primer nivel "Medicion del costo de reasignacion" en
  `S/10-recomendaciones.tex` (hoy dentro de `:34`) con criterio de exito y tamano de muestra; linea
  futura de medicion por regimen o sustitucion de las 81 reconstrucciones por llamadas reales
  (junto a `:26`); §1.9 o parrafo de priorizacion (`:6`) actualizado. Verificacion ANTES:
  `rg -n "proporci.n significativa|cerca del 40|inteligencia organizacional" S/06-implementacion.tex`
  y `rg -n "subsection\{.*reasignaci" S/10-recomendaciones.tex` = 0; DESPUES: rotulados y la
  subseccion existe.

## 8. Forma y bibliografia (recomendaciones 13 y 14)

- [ ] 8.1 Flotantes: `\FloatBarrier` (o `[H]`) antes de `\section{Corpus de validacion}`
  (`S/12-anexos.tex:145`) y, si se quiere, en los Anexos A y J; glosario `S/00-glosario.tex` sin
  celdas izquierdas vacias en mitad de columna (OAuth2, RPO, SaaS, TF-IDF, TwiML, VM, VoIP).
  Verificacion: tras la compilacion de 10.3, las figuras 12 a 14 no caen dentro del Anexo F (paginas
  registradas) y el glosario se lee en orden descendente.
- [ ] 8.2 Hipotesis: definir "F1 macro de umbral" en `S/01-introduccion.tex:36` (hoy solo en
  `S/04-marco-metodologico.tex:107`); que limite del intervalo decide en `01:36`; p de
  `S/07-resultados.tex:84` alineado con la H1 unilateral segun el requisito vigente "Convencion
  declarada del valor p frente a la hipotesis direccional de tiempos"; `01:34` sin referencia hacia
  adelante al OE2. Verificacion ANTES: `rg -n "de umbral" S/01-introduccion.tex`; DESPUES: definicion
  en la hipotesis y convencion del p declarada.
- [ ] 8.3 `Bibliography_base.bib`: `Decision2003_490_CE` (`:904-910`) con "DO L 168, 5 de julio de
  2003, pp. 19-22"; "s. f." o ano de la version consultada en las entradas de n8n, PostgreSQL,
  Airflow y FastAPI; valorar una referencia tecnica de Gemini 3.6 Flash solo si existe una pagina
  oficial verificable (sin inventar). Verificacion ANTES: `rg -n "8 de julio de 2003" "docs/Tesis/v10 (IA)/Bibliography_base.bib"`
  devuelve `:910`; DESPUES: 0, y `verify_citations.py` PASS.
- [ ] 8.4 **[GATED OQ-06]** Tope de paginas: registrar en la seccion de presupuesto de paginas de
  `C/dictamen-correcciones.md` la decision de sostener el exceso (magnitud y fecha) o aplicar una
  reduccion que no elimine contenido cientifico (requisito "Presupuesto de paginas preservado").
  Verificacion: la decision figura con el total medido en 10.3.

## 9. Coherencia

- [ ] 9.1 Cifras canonicas intactas: repetir el conteo de 1.2. Verificacion: mismos valores; el diff
  solo re-rotula o agrega cifras del JSON de 4.3.
- [ ] 9.2 Sin nombres reales ni correspondencia alias-identidad en la prosa nueva. Verificacion:
  revision del `git diff` de `S/`, `docs/seguridad/`, `data/README.md`, `C/`.
- [ ] 9.3 Barrido de residuos: `rg -ni "planilla de cronometraje observacional|consentimiento expreso|desliz|sustituye, como lectura vigente|De ese universo|organizaciones medianas con vol|presentado como escenario de referencia|ser.a no concluyente|en el campo|dependencia medida|8 de julio de 2003" S/ "docs/Tesis/v10 (IA)/Bibliography_base.bib"`
  = 0 (salvo lo que una respuesta OQ conserve expresamente, registrado).
- [ ] 9.4 Resumen y Abstract <= 250 palabras de prosa; hash del corpus y tags `v1.6.2`/`v1.6.3`
  iguales a 1.3; `verify_citations.py` PASS; `pytest` de 1.4 en verde;
  `openspec validate c-249-aplicar-las-recomendaciones-del-dictamen-v1-6-3 --strict` y
  `openspec validate --all --strict` sin fallos.

## 10. Release v1.6.4 (HIGH; gated OQ-05; OK expreso de los autores antes de cada commit y del tag)

- [ ] 10.1 Precondicion: todas las tareas gated de 3, 5, 7 y 8 aplicadas o expresamente diferidas
  por los autores (registrado); `git status` sin cambios fuera del alcance. Verificacion: lista de
  tareas abiertas vacia o con su diferimiento registrado.
- [ ] 10.2 Bump a `v1.6.4` y fecha de la release en `S/00-portada.tex`, Anexo B
  (`sec:anexo-repositorio`), `Bibliography_base.bib` (`Gomez2026_repositorio`), `README.md`,
  `knowledge-base/` y `C/inventario-uso-asistentes-ia.md`; cifra del Anexo I.3 (`S/12-anexos.tex:251`)
  recomputada con `git rev-list --count` sobre la referencia que el texto describe (OQ-05 (4)).
  Verificacion: `rg -n "1\.6\.3" ` sobre esos archivos solo en registros historicos; conteo coincide.
- [ ] 10.3 Recompilar (Docker `texlive-thesis`, `latexmk main.tex` en `docs/Tesis/v10 (IA)/paper/`).
  Verificacion: `main.log` sin errores fatales; `rg -c "undefined" main.log` = 0 para referencias y
  citas; 0 `multiply defined`; biber sin advertencias; paginas registradas; flotantes de 8.1
  verificados en el PDF (requisito "Verificacion de flotantes en la release").
- [ ] 10.4 Regenerar `docs/Tesis/v10 (IA)/paper/compilacion.md` con
  `C/resumir_registro_compilacion.py --fuente` nombrando el hash del commit compilado (requisito ADDED
  de `tesis-document`); regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md`
  (`build_tesis_para_agente.py`), `tesis_para_evaluacion.txt`, `tesis_completa_extraida.txt` y la
  copia de entrega `docs/Tesis/tesis_ultima_version.pdf`. Verificacion: SHA-256 de la copia igual al
  de `main.pdf`; `tesis_para_agente.md` contiene "laboratorio" en el Resumen y la lectura por regimen.
- [ ] 10.5 Commits y tag segun la regla de OQ-05 (D8): C3 de contenido y C4 que consigna el hash,
  con el tag anotado `v1.6.4` sobre el commit que la regla indique y sin mover ningun tag publicado
  (salvo las opciones B, C o D, cada una con su MODIFIED del requisito vigente agregado a
  `specs/tesis-document/spec.md` antes de archivar; A es la unica compatible). Verificacion:
  `git cat-file -t v1.6.4` = `tag`; `git rev-parse v1.6.4^{commit}` y el hash impreso en el Anexo B
  coinciden con lo que dice `12:60`; `v1.6.2` y `v1.6.3` sin cambios.
- [ ] 10.6 Publicar rama y tag en `origin` (solo con pedido expreso); merge a `main` con merge commit
  (nunca squash ni rebase); `engram sync` del proyecto antes del push, segun la convencion del
  repositorio. Verificacion: `git merge-base --is-ancestor v1.6.4 origin/main` verdadero.

## 11. Registro y cierre

- [ ] 11.1 `C/dictamen-correcciones.md`: seccion "c-249: aplicar las recomendaciones del dictamen
  v1.6.3" con la tabla de compuertas OQ-01 a OQ-06, las tablas ANTES/DESPUES por bloque, las cifras
  de 4.3 (y sus diferencias con el dictamen), el resultado de 9.x, la regla de tags y la release
  (`v1.6.4`, commits, SHA-256 del PDF). Verificacion: la seccion existe y el diff del archivo es
  aditivo salvo los encabezados de 7.2.
- [ ] 11.2 `C/respuestas-tribunal-cuarta-instancia.md`: respuestas afectadas por 3.4, 3.8 y 3.9
  (titularidad, consentimiento, periodo 21-09 a 1-10) alineadas con la version. Verificacion:
  `rg -n "expreso|desliz" C/respuestas-tribunal-cuarta-instancia.md` coherente con `11:30`.
- [ ] 11.3 `CHANGES.md`: entrada `[C-249]` con estado, objetivo, specs, dependencias (despues de
  c-247 y c-248), gobernanza (MEDIUM; HIGH en el capitulo legal y la release), tag y "Leer antes",
  con el formato de la entrada `[C-248]`. Verificacion: la entrada existe.
- [ ] 11.4 `openspec validate --all --strict`; archivar el change. Verificacion: valida y el change
  queda en `openspec/changes/archive/`.
