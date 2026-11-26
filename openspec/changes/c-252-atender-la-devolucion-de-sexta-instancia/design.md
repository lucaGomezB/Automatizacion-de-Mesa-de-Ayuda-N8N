# Design: Atender la devolución de sexta instancia del tribunal

## Context

Ver `proposal.md` - Why. Estado verificado el 2026-11-26 sobre `main` (tag `v1.6.5`, 159 páginas, más el
estado aplicado de c-251: commits `a4437a1a`, `049eb353`, `f1854521`). La devolución de sexta instancia
(`auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md`) emite D-01 a D-06 y diez preguntas
probables. Las páginas que cita el tribunal son las de la v1.6.5; las tareas usan `archivo:línea` de `main`.

- **Mapa archivo→capítulo (obligatorio).** Ch1=`01-introduccion.tex`, Ch4=`04-marco-metodologico.tex`,
  Ch7 (legal)=`11-aspectos-legales.tex`, Ch8 (Resultados)=`07-resultados.tex`, Ch9 (Discusión; §9.1 con las
  explicaciones rivales)=`08-discusion.tex`, Ch10=`09-conclusiones.tex`, Anexos=`12-anexos.tex`. Tablas
  rendidas (de `main.lot`): Tabla 3=`tab:variables` (`04:25`), Tabla 4=`tab:procedencia-numeros` (`04:71`),
  Tabla 10=`tab:sintesis-resultados` (`07:15`), Tabla 12=`tab:tiempos-canal` (`07:65`), Tabla 18=`tab:errores`
  (`07:255`), Tabla 23=`tab:cumplimiento-objetivos` (`09:15`), Tabla 26=`tab:declaracion-uso-ia` (`12:263`),
  Tabla 29=`tab:rango-robustez-tiempos` (`12:361`); Figura 11=`fig:cronograma` (`12:53`, fuente
  `docs/diagrams/cronograma.md` → `paper/figures/cronograma.png`).
- **Anclas verificadas (rg sobre `main`).** "del sector servicios y con sede en la provincia de Mendoza":
  `01:16` y `09:52` (la segunda aparición no la cita el tribunal y se trata igual). "retirado el componente
  de carga": `04:127`. "ya no contempla": `12:354` (introducida por c-251 E5). "no incluye componente de
  carga": `04:89`; "sin componente de carga": `04:31`, `04:46`, `07:38`, `07:285`, `08:22`. "respaldados
  por": `07:38` (dos veces). "distintos de los autores": `11:46`. "registro histórico/retirado": `12:247`.
  "redactadas por los autores": `12:149`; "por uno de los autores": `04:46`, `00:11`, `12:241`, `11:16`,
  `11:36`, `11:54`, `09:40`, `09:54`, `10-recomendaciones.tex:26`. "en el domicilio de cada analista":
  `04:46`. "165,3": `12:241`, `12:247`. Léxico «cliente», «sucursal», «estado de cuenta»: `04:46`; «sistema
  principal»: `11:18`. R015: `07:277`. Orden manual → automatizado: `04:14` (campaña 2026-10), `08:22` (tercera
  explicación rival: "El orden temporal de la campaña (manual antes que automatizado) sesga, de hacerlo, en
  contra de la hipótesis"), primera amenaza `04:117`. "registro manual de cada incidente": `04:16`. I.1:
  `12:239-247`; I.2: `12:249-251` (lista hasta la cuarta instancia, sin la quinta). Pie de la Figura 11:
  "la confirmación del 9-10-2026 cubre las ventanas de las campañas" (`12:53`). Ninguna ancla quedó sin
  encontrar; "generales, sin detalles explícitos" figura como "una descripción general, pseudonimizada, sin
  detalles explícitos" (`04:46`).
- **Evidencia fechada disponible para D-01 (no sustituye la declaración de los autores).**
  - `b0dcc057` (2026-10-02 16:08 −03): la propuesta de c-68 describe un `data/corpus_evaluacion_pseudonimizado.json`
    local con 200 casos (R001..R200), los tres canales con su conteo (66/53/81) y `tiempo_automatizado_s = null`
    en 200/200. Acredita que las 200 descripciones ya existían esa tarde; no acredita si `tiempo_manual_s`
    estaba cargado (el JSON no estaba versionado).
  - `38e79c9b` (2026-10-02 18:51), `361b06bd`, `eb7ca59d`, `f0c07a38` (02/10 noche): corrida de ingesta de
    los 119 casos de correo y formulario (c-68).
  - `5dcccf53` (2026-10-05 16:10) "selector de casos del corpus en el softphone" y commits de c-70 del 05 y
    06/10: corrida telefónica de los 81.
  - `ea625764` (2026-10-09 14:24) versiona el corpus con `tiempo_manual_s` y el CSV con "Tiempo de Registro
    Manual"; su mensaje dice "mantener los crudos fuera" y el `data/README.md` de ese commit afirma que "el
    original pre-pseudonimizacion (crudo) NUNCA se versiona". Esto choca con la v1.6.5 (`11:18`: "no existen
    originales con identificadores que custodiar ni destruir") y debe resolverse en OQ-03.
  - `35592473` (2026-06-11) genera el corpus sintético con `scripts/gen_corpus.py`, que no produce ninguna
    columna de tiempo: los 165,3 s del 3 de julio no salen de ese script. OQ-01 debe responder quién los midió
    o generó y sobre qué textos.
- **Evidencia disponible para D-02.** `v1.6.4:04:89`: "Al tiempo de esa lectura se le sumó un tiempo fijo de
  carga del ticket, estimado a partir de la experiencia profesional del analista externo (`A1`) en el orden
  de 10 s, cuya magnitud exacta no consta, y ya incluido en `tiempo_manual_s`". c-250 (OQ-02 cerrada) registró
  que ese componente "no existe en los datos" y lo trató como fabricación; c-251 E5 rotuló luego el −10 s
  como "escenario adverso en que se restara el componente de carga que una descripción anterior [...]
  incluía, componente que la presente versión ya no contempla". Ninguna de las dos decisiones explicó en la
  tesis por qué la v1.6.4 lo afirmó, que es lo que el tribunal pide.
- **Cálculo preliminar para D-04 (verificación de orden de magnitud, no cifra de la tesis).** Sobre
  `data/corpus_evaluacion_pseudonimizado.json` (sin columna de régimen: el régimen se deriva del canal por la
  declaración 119/81, (a) = correo + formulario, (b) = telefonía): telefonía 81 casos, ≈11,8 palabras y
  ≈68,5 caracteres de media, tiempo manual medio 87,2 s; correo 66, ≈11,3 palabras, ≈67,0 caracteres, 56,5 s;
  formulario 53, ≈9,3 palabras, ≈53,9 caracteres, 28,7 s. Leer en voz alta unas doce palabras no explica
  87 s: la mayor parte del tiempo telefónico manual debe ser algo distinto de la lectura. Esto agrava D-04 y
  obliga a una declaración de los autores (OQ-05); el script versionado fija las cifras definitivas.
- **c-251.** Contenido aplicado en `main`, tareas sin marcar. c-252 parte de ese estado, no repite sus
  correcciones y retoca solo dos piezas que c-251 introdujo (`12:354` y la barra de la Figura 11).

## Goals / Non-Goals

**Goals:**

- Que la línea base manual quede documentada sin contradicciones: cronología día por día con evidencia por
  fecha (D-01), una sola definición del tiempo manual con su historia registrada (D-02), procedencia del
  régimen (a) sin rastros de versiones anteriores y con el visto bueno del director (D-03).
- Informar la extensión de las descripciones con un script reproducible y explicar la composición de los
  87,2 s (D-04); completar la propagación y la trazabilidad (D-05); cerrar la redacción (D-06).
- Dejar escritas las respuestas a las diez preguntas (1 a 4 obligatorias) y publicar la versión de defensa
  `v1.6.6` con la trazabilidad de c-250.

**Non-Goals:**

- No inventar fechas, operadores, orígenes ni la composición del tiempo manual: todo hecho no respaldado por
  un artefacto se toma de la respuesta registrada de los autores y se declara como tal.
- No cambiar cifras canónicas salvo por decisión de OQ-02 (rama A); no editar casos ni JSON del corpus.
- No rehacer lo que c-251 ya aplicó; no tocar `App/`, `n8n/` ni los artefactos existentes de `evaluation/`.
- No mover, borrar ni recrear `v1.6.0` a `v1.6.5`.

## Decisions

### D1 - Capacidad nueva `tesis-sexta-instancia` más dos MODIFIED y un ADDED

Las observaciones D-01 a D-06 son nuevas y se agrupan en una capacidad nueva, como las instancias anteriores
agruparon las suyas. Dos requisitos de c-250 sincronizados en `tesis-reencuadre-cuarta-instancia` quedan en
tensión con la sexta instancia y se MODIFICAN (bloque completo, conservando el nombre de cada escenario):
"Cronología [...] (C-01 de c-250)" (fecha mensual → cronología acotada) y "Componente "~10 s de carga del
ticket" retirado (C-02 de c-250)" (la retirada pasa a depender de OQ-02 y de su nota en I.1; además su
escenario del Anexo K ya contradecía el re-etiquetado de c-251 E5). La release va como ADDED en
`tesis-document`. Alternativa descartada: ADDED en `tesis-reencuadre-cuarta-instancia` sin MODIFIED, que
dejaría vigentes dos requisitos contradictorios.

### D2 - Cinco compuertas de autores (OQ-01 a OQ-05)

Igual que c-249: cada compuerta se presenta a los autores (y, cuando corresponde, al director), la respuesta
literal se registra con fecha y responsable en la sección c-252 de `dictamen-correcciones.md`, y solo
entonces se ejecutan las tareas marcadas **[GATED OQ-0n]**. El agente MUST NOT completar una compuerta con
inferencias propias; puede presentar la evidencia fechada de Context como insumo. OQ-05 se agrega a las
cuatro previstas porque el cálculo preliminar de D-04 muestra que la composición de los 87,2 s es un hecho
que solo los autores conocen.

### D3 - D-01: dos ramas según OQ-01

En ambas ramas: (i) se agrega una cronología día por día (tabla en §4.4 o en el Anexo de la Figura 11, con
una columna "evidencia" que distingue commit, archivo versionado o "declaración de los autores");
(ii) §4.2 (`04:14`), §4.4 (`04:46`), Tabla 4 (`04:78`) y el pie de la Figura 11 (`12:53`) declaran que la
fecha del cronometraje manual es una declaración de los autores acotada superiormente por `ea62576`
(09/10/2026) y, si los autores lo confirman, por `b0dcc057` (02/10/2026); (iii) la barra de la campaña manual
de `docs/diagrams/cronograma.md` deja de extenderse al 31/10 (termina en la cota declarada) y se regenera
`cronograma.png`; (iv) I.1 registra la respuesta sobre los 165,3 s (quién, sobre qué textos o, si fueron
generados, que no hubo cronometraje).

- **Rama A (el orden manual → automatizado se sostiene).** La cronología ubica recolección, redacción,
  doble etiquetado con consenso y cronometraje de los 119 casos antes del 02/10 (corrida automatizada) y el
  de los 81 antes del 05/10. Si el intervalo entre la notificación del 01/10 y el 02/10 no alcanza para esas
  cuatro tareas, la tesis debe decir cuándo se recolectaron y redactaron (por ejemplo, antes de la
  notificación) y conciliarlo con el capítulo legal (la notificación y el consentimiento del 01-02/10).
- **Rama B (no se sostiene: el automatizado precedió al manual en todos o parte de los casos).** Se corrige
  §4.2 (`04:14`: "primero por el flujo manual [...] y luego por el flujo automatizado"), la primera amenaza
  (`04:117`) y la tercera explicación rival de §9.1 (`08:22`: el sesgo de orden ya no va "en contra de la
  hipótesis"), y se declara si los operadores manuales vieron la clasificación automatizada antes de
  cronometrar (contaminación). Se revisan `07:311` y `09:42`, que hablan del orden en la campaña
  complementaria, para no confundir las dos campañas.

### D4 - D-02: dos ramas según OQ-02

- **Rama A (la carga de ~10 s SÍ se sumó y los valores la incluyen).** La v1.6.5 (y c-250) es la inexacta.
  La cifra primaria de la sub-hipótesis 1 pasa a la del descuento de 10 s (51,6 s → 17,76 s, 65,6 %), con el
  71,2 % como lectura con carga incluida; se recomputan por pares la reducción sin telefonía y las cifras por
  canal (el script de D-04 lo agrega como función con su prueba); se propaga a Resumen, Abstract, Tablas 3,
  10, 12, 23 y 29, octava amenaza (`04:131`), §8.1, §9.1, Conclusiones y `numeros-canonicos.md` (sección
  aditiva, valores previos marcados como superados). I.1 registra que la v1.6.5 retiró por error un
  componente que los datos sí contienen.
- **Rama B (nunca se sumó).** La descripción de la v1.6.4 (`v1.6.4:04:89`) era inexacta: I.1 lo registra
  con el criterio de los retiros anteriores (qué decía, por qué figuró en una versión entregada, qué la
  reemplaza). `04:127` pasa a "el 87,2 s manual mide solo la clasificación" (sin "retirado"); `12:354`
  pasa a una forma que no sugiera un cambio de valores (por ejemplo, "el de 10 s cuantifica el escenario
  que el tribunal pidió para una descripción anterior de la tarea, que los valores nunca incluyeron").
  La cifra primaria sigue en 71,2 %.

En las dos ramas el texto de la tesis deja de usar "retirado" o "ya no contempla" para algo que no cambió
en los datos, y el ANTES/DESPUES se registra en la sección c-252.

### D5 - D-03: procedencia con una sola declaración en §4.4 (HIGH)

Según OQ-03: si los incidentes del régimen (a) ocurrieron en el ámbito laboral de quienes los reportaron, se
dice en §4.4 (`04:46`) una sola vez, junto con la explicación del léxico corporativo, de R015 (`07:277`) y de
los sectores de la Tabla 18, y el capítulo legal (`11:16`, `:18`, `:46`, `:54`) menciona el deber de
confidencialidad del art. 10 de la Ley 25.326 respecto de esos lugares de trabajo; si no, se explica de dónde
proviene ese léxico. En ambos casos: se retira o explica "del sector servicios y con sede en la provincia de
Mendoza" (`01:16`, `09:52`), que describe a una organización y no a personas; §4.4 dice que la composición
119/81 descansa en la declaración de los autores, sin originales; I.1 registra el cambio de origen respecto
de la v1.6.4 ("empleadores de los autores" → "círculo de los autores"); se reconcilia la afirmación de que no
existen originales (`11:18`) con el mensaje de `ea625764` ("mantener los crudos fuera"); y el visto bueno
escrito del director sobre la procedencia declarada queda incorporado (constancia en
`docs/seguridad/` o en el expediente, citada desde I.1). Toda edición del capítulo legal se muestra a los
autores antes de escribir.

### D6 - D-04: script TDD aditivo y declaración de la composición del tiempo

`evaluation/data/campana/analisis/analisis_sexta_instancia_c252.py` con
`test_analisis_sexta_instancia_c252.py` escrito primero (patrón de `analisis_quinta_instancia_c250.py` y
`test_analisis_quinta_instancia_c250.py`). Funciones puras: conteo de palabras y caracteres de una
descripción; extensión media por canal y por régimen (régimen derivado del canal por la regla declarada,
parametrizada para que la prueba no la fije en silencio); tiempo manual medio y segundos por palabra por
canal; en rama A de OQ-02, la recomputación con −10 s. Salidas `.json`, `.md`, `SHA256SUMS.txt`. La prosa
toma las cifras de la salida y la composición "lectura / decisión" de la respuesta de OQ-05 (si los autores
no pueden separarla, se declara que no se midió por separado y se acota con la extensión).

### D7 - D-05 y D-06: propagación y redacción sin compuerta (salvo el domicilio)

Resumen y Abstract ganan una cláusula ("el brazo manual midió solo la clasificación, no el registro"; "sin
telefonía, 63,3 %") dentro del tope de 250 palabras de prosa; la Tabla 10 lo dice en la fila del tiempo;
`04:16` deja de decir "registro manual". I.1 registra el cambio de fechas (junio-agosto → octubre, con la
cota de D-01) y el del componente de carga (D-02); I.2 suma la quinta (25/11/2026) y la sexta (26/11/2026)
instancia. D-06: fórmula de §4.5 en `07:38`; "uno de los autores" unificado en `12:149`; `11:46` reformulado
porque los autores también son reportantes y titulares; "registro histórico/retirado" → "registro histórico,
retirado"; el "por pares" desde el domicilio queda GATED OQ-04.

### D8 - Respuestas a las diez preguntas

`docs/Tesis/Correcciones/respuestas-tribunal-sexta-instancia.md` con el formato de
`respuestas-tribunal-quinta-instancia.md` (pregunta + respuesta autónoma, remisión a artefacto versionado o
"declaración de los autores", solo alias). Las 1 a 4 dependen de OQ-01 y OQ-02 y son obligatorias; la 5 y la
6 de OQ-03; la 7 de OQ-05 y del script; la 8 de OQ-04; la 9 se responde con honestidad (fuera de la
declaración, solo los commits fechados y la ausencia de originales); la 10 con la sensibilidad al ajuste del
vocabulario (`tab:sensibilidad-ajustes`, Tabla 30) y la séptima amenaza (`04:129`). Se cotejan las cifras con
`cotejar_cifras_respuestas.py` y se alinea `docs/defensa/respuestas-tribunal.md`.

### D9 - Release v1.6.6 y autoverificación

Bump `v1.6.5` → `v1.6.6`, regla de tags de c-249 OQ-05 (commit de contenido C3, commit del hash en el
Anexo B C4, tag anotado sobre C3), `compilacion.md`, derivados, `CHANGES.md`, `README.md`, `knowledge-base/`
e inventario de IA. Antes del tag, autoverificación estilo CONEAU (método de la memoria del proyecto: fechas
de corridas frente a commits, figuras frente a texto, pines del tag frente a los declarados) sobre el PDF
compilado, con un barrido `rg` de cada frase que el tribunal citó. Precondición: compuertas cerradas y visto
bueno escrito del director a la versión de defensa.

### D10 - Verificación ANTES/DESPUES

Como c-250: cada tarea de prosa corre un `rg` ANTES (muestra el defecto) y DESPUES (estado deseado),
registrados en la sección c-252. El script sigue RED-GREEN-TRIANGULATE-REFACTOR con `pytest`. Patrones con `.`
en lugar de vocales acentuadas.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente completa la cronología o la composición del tiempo con inferencias] | D2: tareas GATED; la evidencia de Context es insumo, no respuesta |
| [La cronología de rama A no cierra entre el 01/10 y el 02/10] | D3: la tesis lo dice y concilia con el capítulo legal, o pasa a rama B |
| [Rama A de OQ-02 deja cifras viejas en algún lugar] | D4: barrido de `71,2`, `61,6`, `87,2`, `63,3` y sección aditiva en `numeros-canonicos.md` |
| [Volver a sugerir un cambio de datos que no ocurrió] | D4: `rg "retirado el componente|ya no contempla"` = 0 al cierre |
| [Contradicción entre "no existen originales" y "mantener los crudos fuera"] | D5: reconciliación explícita en OQ-03 antes de escribir |
| [El Resumen o el Abstract superan 250 palabras] | D7: conteo antes y después; se compacta otra frase si hace falta |
| [Cruce de specs con c-251 al archivar] | Proposal: cerrar c-251 antes del apply de c-252 |
| [Editar el capítulo legal sin revisión (HIGH)] | Texto propuesto mostrado a los autores antes de escribir |
| [Desfasaje tag/PDF] | D9: regla de c-249; `git rev-parse v1.6.6^{commit}` frente al hash impreso |
| [Nombres reales en prosa nueva] | Solo alias; barrido final del diff |
| [Falso positivo de gitleaks en prosa] | Evitar "capitulo" seguido de coma y nombre de archivo dentro de 20 caracteres |

## Migration Plan

1. Cerrar c-251 (marcar tareas aplicadas y archivar) o confirmar que su contenido aplicado es la base.
2. Presentar OQ-01 a OQ-05 con la evidencia de Context; registrar respuestas.
3. Script de D-04 (TDD) y tareas sin compuerta (D-05, D-06 salvo domicilio).
4. Tareas GATED según cada respuesta, con la rama elegida de D3 y D4; capítulo legal con revisión previa.
5. Coherencia, respuestas a las diez preguntas, autoverificación CONEAU, visto bueno del director.
6. Release `v1.6.6`.

Rollback: hasta el paso 6 todo es prosa sin commit y se revierte por archivo; el tag no se crea hasta que el
commit esté verificado y el director haya dado su visto bueno.

## Open Questions

- **OQ-01 (autores; bloquea D-01 y las preguntas 1 a 3).** (1) Fecha de cada etapa para los 119 casos de
  correo y formulario y para los 81 telefónicos: recolección, redacción disociada, doble etiquetado y
  consenso supervisado por el director, cronometraje manual (cada mitad y cada operador). (2) ¿El
  cronometraje manual precedió a la corrida automatizada del 02/10 (119) y a la del 05-06/10 (81)? Si no,
  ¿los operadores vieron la salida automatizada? (3) ¿El JSON local que describe `b0dcc057` (02/10 16:08)
  tenía ya `tiempo_manual_s`? (4) ¿Por qué la v1.6.4 ubicaba la campaña en junio-agosto: qué evidencia
  cambió? (5) ¿Quién midió o generó los 165,3 s del 3 de julio y sobre qué textos?
- **OQ-02 (autores; bloquea D-02 y la pregunta 4).** ¿Los valores de `tiempo_manual_s` incluyen unos 10 s de
  carga? Si sí: rama A (cifra primaria 65,6 %). Si no: rama B, y ¿por qué la v1.6.4 declaró que se sumaron
  y que estaban "ya incluido[s]"?
- **OQ-03 (autores y director; HIGH; bloquea D-03 y las preguntas 5, 6 y 9).** (1) ¿Los incidentes del
  régimen (a) ocurrieron en el ámbito laboral de quienes los reportaron? (2) ¿A qué refiere "del sector
  servicios y con sede en la provincia de Mendoza"? (3) ¿Por qué la v1.6.4 los atribuía a los empleadores de
  los autores? (4) ¿Qué eran los "crudos" que `ea625764` mantuvo fuera del repositorio, y existen hoy?
  (5) Visto bueno escrito del director sobre la procedencia declarada (texto y fecha).
- **OQ-04 (autores; bloquea D-06 domicilio y la pregunta 8).** ¿Cómo se cronometraron A1 y T1 "por pares"
  trabajando "en el domicilio de cada analista" (presencial en un domicilio, en ambos por turnos, a
  distancia)?
- **OQ-05 (autores; bloquea la prosa de D-04 y la pregunta 7).** ¿Qué incluyó el tiempo manual telefónico
  además de leer en voz alta una descripción de unas doce palabras (pausas, simulación de diálogo, consulta,
  decisión)? ¿Se puede separar lectura de decisión o solo se declara?
