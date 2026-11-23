# Design: Aplicar las recomendaciones del dictamen sobre v1.6.3

## Context

Ver `proposal.md` - Why. Estado verificado el 2026-11-23 sobre `main` (`44320fd0`):

- **Lineas del dictamen vigentes.** `git diff --stat v1.6.3 HEAD -- "docs/Tesis/v10 (IA)" data`
  no devuelve diferencias: los `.tex`, el `.bib` y `data/` de `main` son los del tag. Se cotejaron
  ~95 citas `archivo:linea` del dictamen contra las fuentes (script en el scratchpad de la sesion
  de propose) y todas apuntan al pasaje descrito. Tres precisiones de ubicacion: (1) `00r:15` y
  `00r:31` escriben `1~USD` (con tilde de LaTeX), de modo que un `rg "1 USD"` no lo encuentra;
  (2) el "§2 del acta T2" es `docs/seguridad/acta-consentimiento-t2.md:28-44` (el "sin datos de
  terceros" del regimen (b) esta en `:42-44` y se repite en `:68`, §3); (3) el resumen del
  registro de compilacion es `docs/Tesis/v10 (IA)/paper/compilacion.md` (no existe un
  `compilacion.md` en `docs/Tesis/v10 (IA)/`); hoy su fila "Fuente compilada" dice "arbol de
  trabajo sobre c-248 (release v1.6.3; C4, hash consignado)", sin hash.
- **Precedentes.** c-246 (reencuadre de cuarta instancia), c-247 (compuertas OQ-01 a OQ-04 y
  recomendaciones 1 a 15 del dictamen sobre `v1.6.2`) y c-248 (release `v1.6.3`). c-249 reutiliza
  sus capacidades (`tesis-reencuadre-cuarta-instancia`, `tesis-document`), el formato de
  compuertas con respuesta literal, fecha y responsable, y la verificacion estilo prosa TDD
  (`rg` ANTES/DESPUES registrado en `docs/Tesis/Correcciones/dictamen-correcciones.md`).
- **Lo que ya registraron los autores y el texto contradice.** OQ-02 (5) de c-247
  (`dictamen-correcciones.md:6913`): "Las planillas de cronometraje no existen"; `04:97` las
  describe como instrumento. OQ-01 (2) de c-247 (`:6912`): "Los reportaron los integrantes del
  entorno operativo del propio equipo"; `11:40` dice "los integrantes del propio grupo de
  desarrollo". OQ-01 de c-246 (seccion c-246, fila OQ-01): las 81 reconstrucciones "las escribio
  el autor que recolecto los incidentes", en singular, lo que respalda "un autor" (`04:46`) frente a
  "los autores" (`08:50`, `09:24`, `09:53`, `10:26`) y abre una pregunta sobre quien "recolecto"
  los 119.
- **Tensiones del repositorio (rec. 2).** `data/README.md:53` ("contienen PII y NUNCA se
  commitean") frente a `11:24` y `12:151` ("no habia identificadores personales directos") y al
  acta T2 §2 ("datos personales (seudonimizados; no disociados)"); `12:153` ("coinciden con el
  texto de origen") frente a `04:46` ("se redactaron en tercera persona"); `01:72` ("el corpus no
  proviene de una organizacion real", conservado por OQ-01 (6) de c-247) frente a `01:16` y
  `12:239`.
- **Cifras de la rec. 6 y de la rec. 4.** Reproducibles desde artefactos versionados:
  `data/corpus_evaluacion_pseudonimizado.json` (campo `canal_origen`; los 81 `telefono` son el
  regimen (b) segun `04:46`), `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`,
  `evaluation/data/campana/intervenciones.csv`,
  `evaluation/evidence/load_test_inferencia_2026-11-17.json` y
  `..._ampliada_2026-11-18.json`. La serie guarda cada recomputo como
  `evaluation/data/campana/analisis/analisis_<tema>_c<NNN>.{py,json,md,SHA256SUMS.txt}` con su
  `test_analisis_<tema>_c<NNN>.py` al lado (p. ej. c-236, c-224).
- **Reglas vigentes que acotan el diseno.** `tesis-document` "Publicacion de una release de
  correccion sin mover tags publicados" (tag sobre C3, inmutable) quedo contradicha de hecho por el
  movimiento de `v1.6.3` a C4 (`dictamen-correcciones.md:7093`); "Presupuesto de palabras del
  resumen en espanol" y "English abstract" (250 palabras de prosa; c-247 dejo 248/246);
  "Presupuesto de paginas preservado" (tope de 100 sobre el total; un exceso SHALL estar declarado
  y honrado por decision registrada de los autores; hoy 158 paginas).
- **Fuentes de terceros.** `docs/Tesis/fuentes/` solo contiene su `README.md`: las copias de
  Paket (2024) y Revina (2020) estan fuera del repositorio y del alcance del agente. La bitacora
  `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md` registra conteos por cadena para algunas
  bases (p. ej. arXiv C1 2334, C2 3600) y la regla de "trabajo de referencia sin restriccion
  temporal".

## Goals / Non-Goals

**Goals:**

- Que el metodo, el capitulo legal y las conclusiones digan exactamente lo que el registro del
  equipo dice (rec. 1 a 3), con las preguntas que solo los autores pueden contestar convertidas en
  compuertas que bloquean solo sus tareas.
- Que cada regla de decision se aplique como se enuncia, o que su enmienda post hoc quede
  declarada (rec. 4).
- Completar el reencuadre en el Resumen, el Abstract y los capitulos 7 a 10 (rec. 5) y escribir la
  lectura por regimen con cifras recomputadas desde los artefactos, no copiadas del dictamen
  (rec. 6).
- Cerrar la consistencia y la forma (rec. 7 a 14) y publicar `v1.6.4` con una regla de tags escrita
  antes de crear el tag.

**Non-Goals:**

- No inventar hechos de procedencia, consentimiento, instrumentos ni fechas; no elegir por los
  autores ninguna opcion de las compuertas.
- No cambiar cifras canonicas ni conclusiones sin ratificacion de autores; no editar casos del
  corpus ni su JSON (D4 (i) de c-247 sigue vigente).
- No tocar `App/`, `n8n/` ni los artefactos existentes de `evaluation/`.
- No mover, borrar ni recrear `v1.6.2` ni `v1.6.3`.
- No transcribir cifras de fuentes que no estan en el repositorio (Paket, Revina).

## Decisions

### D1 - ADDED sobre las capacidades existentes

Como c-247, los requisitos nuevos se AGREGAN a `tesis-reencuadre-cuarta-instancia` (contenido) y a
`tesis-document` (release). Los requisitos de c-246 y c-247 siguen siendo verdaderos; c-249 los
completa. Alternativa descartada: MODIFIED de "Flujo manual con lugar, sistema, escucha y
definicion unica (OQ-02)" y "Cronologia unica del consentimiento (OQ-03)": copiaria bloques
largos para cambiar una clausula, con riesgo de perder escenarios al archivar. Excepcion prevista
en D8: si OQ-05 elige una regla de tags incompatible con "Publicacion de una release de correccion
sin mover tags publicados", el apply agrega un MODIFIED de ese requisito antes de archivar.

### D2 - Compuertas OQ-01 a OQ-06, cada una bloquea solo su bloque

Seis compuertas (ver Open Questions). Las tareas de los grupos 3 (veracidad y licitud) y 5
(veredictos) quedan bloqueadas por la OQ que indica cada tarea; los grupos 4 (cifras por regimen),
6 (reencuadre), 7 (consistencia) y 8 (forma) son aplicables sin compuerta salvo donde se marca.
Los pasajes tocados desde dos bloques (`04:46`, `11:30`, `09:22`, `01:38`) se editan una sola vez,
en la tarea gated, y la tarea no gated remite a ella. El grupo de release (10) depende de OQ-05 y
OQ-06 y de que no quede ninguna tarea gated sin aplicar.

### D3 - Instrumento del flujo manual: describir lo que quedo, sin recuperar nada

`04:97` deja de describir la planilla en indicativo como instrumento existente. La redaccion
depende de OQ-01: (a) "planilla completada en vivo por el companero de par; no se conservo; los
200 valores constan solo en `tiempo_manual_s`"; (b) si existe algun registro primario parcial
(archivo, foto, hoja), se describe y se versiona con aprobacion; (c) otra formula de los autores.
En los tres casos la primera amenaza (`04:117`) incorpora la falta (o la parcialidad) del registro
primario, la fila del OE5 (`09:27`) y `01:54` se matizan, y `04:89` dice que se busco y que campos
se completaron, con la diferencia de constructo frente al tiempo de extremo a extremo como amenaza
propia.

### D4 - Titularidad del regimen (a): una formula, la que confirmen los autores

Opciones de OQ-02 (el agente MUST NOT elegir): (a) los reportantes son los tres autores: la
formula de `11:40` se propaga a `04:46`, `11:16`, `11:48`, y §7.5 declara que en el regimen (a)
titulares y responsables del tratamiento son las mismas personas; (b) los reportantes son otras
personas de los lugares de trabajo de uno o mas autores: `11:40` cambia, y el capitulo legal funda
la base de licitud de esos terceros y la autorizacion o innecesariedad del empleador; (c) mixto,
con la proporcion que declaren. Sub-decisiones de la misma compuerta: que PII tenian los originales
y de quien (para `data/README.md:53`); si las descripciones son el texto de origen pseudonimizado
(entonces `04:46` deja de decir "se redactaron") o fueron reescritas por los autores (entonces
`12:153` cambia y la septima amenaza `04:129` se extiende a los 200 casos); y la formula de `01:72`
(por ejemplo, "no proviene de una organizacion que haya adoptado el sistema").

### D5 - Articulo 5: analizar la brecha, no negarla

`11:30` reemplaza "consentimiento expreso" por "consentimiento verbal del 2-10-2026, confirmado
por escrito el 20-11-2026" (hecho ya registrado por OQ-03 de c-247), reconoce que entre ambas
fechas el consentimiento no constaba por escrito y ordena las transferencias respecto del
consentimiento. Lo que depende de OQ-03 de c-249: la hora relativa de la corrida de texto del 2-10;
si entre el 21-09 y el 1-10 se envio texto del corpus a Gemini y que eran los 145 incidentes del
dashboard (`06:111`); si existe constancia contemporanea del 2-10 (mensaje, minuta) o ninguna
anterior al acta del 17-11; y el texto de valoracion de la brecha frente al articulo 5 (contenido
transferido sin dato personal, confirmacion posterior), aprobado por los autores. Dominio HIGH: el
texto propuesto se muestra antes de escribir.

### D6 - Cifras por regimen y de la sonda: recomputadas por un script aditivo con prueba

Se agrega `evaluation/data/campana/analisis/analisis_regimen_c249.py`, con
`test_analisis_regimen_c249.py` escrito primero (Strict TDD: la prueba fija sobre datos sinteticos
pequenos el conteo por regimen, el intervalo de Wilson, la proporcion 25/200 y 25/147 con su
binomial unilateral, y la extraccion del p95 del nivel 5 de N8N en ambas corridas y del subconjunto
deterministico de la ampliada), y sus salidas `.json`, `.md` y `SHA256SUMS.txt`. La prosa toma las
cifras de esa salida. Si alguna difiere de la del dictamen (94/119 = 0,790 [0,708; 0,854]; 53/81 =
0,654 [0,546; 0,749]; 3.660,4 ms; 5.024,7 ms; p = 0,28), se escribe la recomputada y la diferencia
se registra. Alternativa descartada: calcular en un script temporal fuera del repositorio; rompe la
convencion de la serie de que toda cifra de la tesis tenga generador versionado.

### D7 - Reglas de decision: la tesis aplica lo que enuncia, o declara la enmienda

Opciones de OQ-04 para la sub-hipotesis 2: (a) regla y denominador prefijados: veredicto "no
concluyente" con 25/200 = 12,5 % [8,6; 17,8]; el denominador de 147 y la binomial se informan como
datos post hoc; (b) enmendar la regla en `01:34` y `04:109`, declarando que el criterio binomial y
el denominador de 147 se agregaron despues de ver los datos, y conservar el rotulo actual. En ambos
casos la variable lleva un solo nombre. Sub-hipotesis 3 con consenso (`07:153`, `08:62`): la
disyuncion de `01:36` hace que 0,797 refute igual; se propone la redaccion del dictamen y los
autores la ratifican (no hay opcion alternativa compatible con la regla escrita). En la misma
compuerta se ratifican la separacion del OE2 en implementacion y desempeno, el veredicto "no
sostenida" de la fila del OE3 y el tratamiento de "accesibilidad" y "dispersion" en `01:38`
(operacionalizar o retirar).

### D8 - Regla de tags escrita antes de la proxima release

Opciones de OQ-05 (autores y director). La regla vigente "Publicacion de una release de correccion
sin mover tags publicados" (`tesis-document`) fija el tag anotado sobre el commit C3 (texto
corregido y PDF recompilado) y el hash consignado en C4. De las cuatro opciones, A es exactamente
esa regla y es la unica compatible; las otras tres la contradicen en el cuerpo del requisito y cada
una exige un MODIFIED (D1): (A) inmutabilidad estricta: tag sobre C3, cuyo PDF no imprime hash; C4
consigna el hash; el tag no se mueve aunque su PDF no imprima hash (compatible); (B) tag creado una
sola vez sobre C4, despues de consignar el hash de C3 y recompilar, y nunca movido (el PDF del tag
imprime el hash de un commit identico salvo esa linea, y `12:60` lo dice): incompatible, cambia el
destino del tag de C3 a C4; (C) un tag publicado puede moverse una sola vez, solo antes de difundir
el ejemplar y con registro fechado: incompatible, mueve un tag publicado; (D) no versionar PDF en el
arbol del tag: incompatible, el requisito vigente exige el PDF recompilado en C3. La opcion elegida
se escribe en `tesis-document` (requisito ADDED de c-249) y se aplica a `v1.6.4`. En la misma
compuerta: version `v1.6.4` y si la Nota de versiones (I.1) registra `v1.6.2`, `v1.6.3` y el
erratum (revierte OQ-3 de c-248, que lo habia dejado solo en el registro).

### D9 - Resumen y Abstract: reemplazar, no agregar

La oracion de escenario, composicion y laboratorio (rec. 5) entra en el Resumen y en el Abstract
reemplazando texto, porque el Resumen tiene 248 palabras de prosa (c-247) frente al tope de 250.
Candidatos a condensar: la enumeracion de cifras de `00r:13`/`:29` y el parentesis del balance de
`00r:15`/`:31`. Conteo ANTES/DESPUES con la regla de la spec (prosa, sin comandos LaTeX ni
palabras clave).

### D10 - Paginas y fuentes externas, por compuerta

El exceso de 158 sobre 100 paginas se declara y sostiene por decision registrada o se reduce (OQ-06
(1)); las secciones nuevas (modelo economico, subseccion del costo de reasignacion) suman paginas,
y los duplicados que se quitan del cap. 2 las compensan en parte. Las cifras de Paket y la
exactitud de Revina solo se escriben si los autores las transcriben de su copia (OQ-06 (2), (3));
si no, el texto explica por que no se informan.

### D11 - Verificacion estilo prosa TDD y TDD real donde hay codigo

Cada tarea de edicion corre un `rg` ANTES (muestra el defecto) y DESPUES (estado deseado),
registrados en la seccion c-249 de `dictamen-correcciones.md`. Los numeros de linea son los de
`main` `44320fd0` (= `v1.6.3` en `.tex`); el apply los re-verifica porque las ediciones los
desplazan. Patrones con `.` en lugar de vocales acentuadas. El script de D6 sigue el ciclo
RED-GREEN-TRIANGULATE-REFACTOR con `pytest`.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente decide quienes son los titulares, que existio del cronometraje o como valorar la brecha] | OQ-01 a OQ-03 bloqueantes; D3 a D5 listan opciones sin elegir; escenario "sin respuesta, la tarea queda bloqueada" |
| [Copiar cifras del dictamen en lugar de recomputarlas] | D6: script con prueba; la prosa cita la salida versionada |
| [Cambiar un veredicto sin ratificacion] | D7: OQ-04 ratifica cada rotulo nuevo |
| [Resumen o Abstract por encima de 250 palabras] | D9: reemplazar; conteo ANTES/DESPUES |
| [Nuevas secciones agravan el exceso de paginas] | D10: OQ-06 (1); duplicados del cap. 2 retirados en la misma tarea |
| [Repetir el desfasaje tag/PDF o mover otro tag] | D8: regla escrita y aprobada antes de crear `v1.6.4`; `v1.6.2` y `v1.6.3` registrados como intactos |
| [Editar el capitulo legal, las actas o `data/` sin revision (HIGH)] | Texto propuesto mostrado a los autores antes de escribir |
| [Nombres reales o correspondencia alias-identidad en prosa nueva] | Solo alias (`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); barrido final del diff |
| [Editar un change archivado reescribe historia] | La tarea 6.3 de c-248 se enmienda con una nota aditiva fechada, sin desmarcar ni borrar |
| [Romper el hash del corpus] | El JSON no se edita (D4 (i) de c-247); `sha256sum` antes y despues |

## Migration Plan

1. Presentar OQ-01 a OQ-06 (OQ-05 tambien al director) y registrar las respuestas literales con
   fecha y responsable en la seccion c-249 de `dictamen-correcciones.md`.
2. Sin esperar respuestas: script por regimen (grupo 4), reencuadre (6), consistencia (7) y forma
   (8), con ANTES/DESPUES por tarea.
3. Aplicar los grupos 3 y 5 a medida que llega cada respuesta.
4. Coherencia (9): cifras canonicas, residuos, nombres, conteos, `verify_citations.py`,
   `openspec validate --strict`.
5. Release (10): bump, recompilacion, derivados, regla de OQ-05, tag, merge, `CHANGES.md` y
   registro.

Rollback: hasta el paso 5 todo es prosa sin commit; se revierten los archivos tocados. El tag
`v1.6.4` no se publica hasta que el commit que lo recibe este verificado.

## Open Questions

- **OQ-01 (autores; bloquea 3.1 a 3.3).** (1) Del cronometraje de junio a agosto, ¿que quedo:
  nada fuera de `tiempo_manual_s`, o algun registro primario parcial (archivo, foto, hoja)? ¿Quien
  completaba la planilla (el companero de par)? (2) En "la busqueda y la carga del ticket"
  (`04:89`), ¿que se buscaba y que campos se completaban en la planilla? (3) ¿De donde salio la
  premisa de 2 min 45 s (165 s)? ¿Se tomo de los 165,3 s del corpus sintetico de julio (`12:237`)?
  (4) La ventana "junio a agosto" de los 119 casos (`04:46`), ¿se declara como declaracion de los
  autores sin registro fechado?
- **OQ-02 (autores; bloquea 3.4 a 3.7).** (1) Los 119 incidentes del regimen (a), ¿los reportaron
  los tres autores (D4 a), otras personas de sus lugares de trabajo (D4 b) o ambos (D4 c, con
  proporcion)? (2) ¿Son titulares y responsables del tratamiento las mismas personas? (3) ¿Que
  datos personales contenian los originales no versionados (`data/README.md:53`) y de quien eran?
  (4) Las descripciones del regimen (a), ¿son el texto de origen pseudonimizado o fueron
  reescritas por los autores? (5) Respecto de los empleadores reales: ¿se obtuvo autorizacion, no
  hacia falta (y por que), o no se obtuvo? (6) Nueva formula de `01:72`. (7) ¿Quien "recolecto"
  los incidentes, segun el registro de c-246 OQ-01 ("el autor que recolecto")?
- **OQ-03 (autores; bloquea 3.8 a 3.10).** (1) ¿La corrida de texto del 2-10 fue anterior o
  posterior al consentimiento verbal de ese dia? (2) Entre el 21-09 y el 1-10, ¿se envio a Gemini
  texto del corpus? ¿Que eran los incidentes que muestra el dashboard desde el 21-09 (`06:111`)?
  (3) ¿Existe una constancia contemporanea del 2-10 (mensaje, minuta) o ninguna anterior al acta
  del 17-11? (4) Texto aprobado de la valoracion de la brecha frente al articulo 5. (5) Vocabulario
  del acta T2 §2 alineado con `11:30`.
- **OQ-04 (autores; bloquea 5.1 a 5.4).** (1) Sub-hipotesis 2: opcion D7 (a) o (b), y nombre unico
  de la variable. (2) Ratificar la lectura con consenso de la sub-hipotesis 3 ("se refuta
  igualmente"). (3) Separar el OE2 en implementacion (alcanzado) y desempeno (no alcanzado), o
  conservarlo y declararlo. (4) Fila del OE3 con "no sostenida". (5) "Accesibilidad" y
  "dispersion" de `01:38`: operacionalizar o retirar.
- **OQ-05 (autores y director; bloquea 7.1 y el grupo 10).** (1) Regla de tags D8 (A), (B), (C)
  o (D). (2) Version `v1.6.4`. (3) ¿La Nota de versiones I.1 registra `v1.6.2`, `v1.6.3` y el
  erratum? (4) Cifra del inventario de IA: recomputar sobre la ref de la entrega (como en c-248
  1.3) o corregir la descripcion "el commit previo al commit de contenido".
- **OQ-06 (autores; bloquea 8.4, 7.5 en lo que toca a Paket y Revina).** (1) Tope de 100 paginas:
  declarar y sostener el exceso por escrito o reducir. (2) Cifras de Paket (2024) transcritas de la
  copia de los autores, o explicacion de por que no se informan. (3) Relectura de la exactitud
  1,000 de Revina (2020) sobre 30 tickets en el original.
