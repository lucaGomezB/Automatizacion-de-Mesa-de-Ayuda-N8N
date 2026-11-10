# Design: Atender el dictamen CONEAU sobre v1.2.16

## Context

Ver `proposal.md` para la motivacion. Fuente: `auditorias/Dictamen_Tesis_v10_v1.2.16_CONEAU_2026-11-09.md`
(secciones "RECOMENDACIONES CONCRETAS Y ACCIONABLES", A1-A3, B1-B3, C1-C2, e "ANEXO: INVENTARIO
DE CORRECCIONES PUNTUALES", items 1-18). El archivo ya esta versionado en la rama
`change/c-195-atender-dictamen-v1-2-16` (commit `e7f5b82`).

**Numeracion.** Igual que en c-190/c-192: 1.x = `01-introduccion.tex`, 2.x =
`02-marco-teorico.tex`, 4.x = `04-marco-metodologico.tex`, 5.x = `05-arquitectura.tex`, 6.x =
`06-implementacion.tex`, 7 = `11-aspectos-legales.tex`, 8.x = `07-resultados.tex`, 9.x =
`08-discusion.tex`, 10 = `09-conclusiones.tex`, 11.x = `10-recomendaciones.tex`, Anexos =
`12-anexos.tex`. `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`.
Las lineas citadas son las del arbol al proponer; el apply localiza por texto (`rg -n`).

**Estado de partida verificado al proponer** (solo lectura, 2026-11-09):

- 7.5 (`S/11-aspectos-legales.tex:34`, `subsec:consentimiento-derechos`) dice "Con posterioridad a
  su participación firmaron una confirmación escrita ..." y "El repositorio conserva la plantilla
  de la confirmación y el registro de que se recabó para los cuatro participantes." Es la unica
  aparicion en `sections/`. Los autores confirmaron hoy que E1, E2, O1 y O2 NO firmaron todavia.
- La plantilla `docs/campana-medicion/confirmacion-posterior-consentimiento.md` dice en el
  encabezado "el registro `alias, rol, fecha_consentimiento`" y su tabla usa
  `alias | rol | fecha_informacion_verbal | fecha_confirmacion | custodia` con fechas vacias.
  `evaluation/data/campana/README.md` no tiene seccion de registro.
- 8.3 (`S/07-resultados.tex:154`) conserva "Medirla en condiciones válidas exige una corrida con
  reportantes identificados" y "no se puede descartar un valor cercano al umbral"; 9.1
  (`S/08-discusion.tex:8`) repite la ultima frase. 1.4 (`S/01-introduccion.tex:34`) y 4.7
  (`S/04-marco-metodologico.tex:81`) definen la regla sin su asimetria.
- Anexo I (`S/12-anexos.tex:205`): "La serie comprende siete dictámenes ... Este anexo traza
  cuatro". `auditorias/` versiona NUEVE dictamenes `.md` (v9 20-10, v9 corregida 21-10, v1.0.1 y
  v1.1.0 22-10, v1.2.5 28-10, v1.2.10 8-11, v1.2.12, v1.2.13 y v1.2.16 9-11); el PDF de
  auditoria `Auditoria_..._040802026.pdf` no se cuenta como dictamen (criterio heredado).
- `C/verificar_matriz_trazabilidad.py`: 171 filas, 0 fallas; secciones con matriz: FASE 36,
  c-159, c-160, c-188, c-190. Las secciones de c-192, c-193 y c-194 tienen solo tablas de 5
  columnas (`Rec | Observación | Corrección | Archivo | Estado`), que el parser ignora por diseño
  (exige 7 columnas con "Fragmento verificable").
- MDE: `evaluation/campana.py:1593` usa `ARE_WILCOXON_MINIMA` (0,864) para el Spearman; lineas
  1173 y 1230 lo usan para Mann-Whitney/Wilcoxon y deben quedar asi. `resultados.json` da
  `0.2834015929824635` en los dos bloques `posicion.spearman` (O1 y O2). Recomputo:
  ARE 0,864 -> 0,2834; 9/pi^2 = 0,91189 -> 0,2763; sin ARE -> 0,2644. La prueba
  `evaluation/tests/test_campana.py:1632` fija hoy el MDE del Spearman con `ARE_WILCOXON_MINIMA`.
  `numeros-canonicos.md:742-743` cita los SHA-256 de `resultados.json` (`e94b6bb8...`) y
  `resultados.md` (`3c1564b1...`); `:851` y `:928-937` citan 0,2834/0,276.
- La spec principal (`Efecto minimo detectable del Spearman ...`) dice 0,2644 "sin ARE",
  incoherente con la tesis (0,276, 9/pi^2) desde c-192: se corrige en el delta.
- Caches: `git show HEAD:` de `evaluation/data/campana/predicciones_in_sample.json` y de
  `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` dan el mismo SHA-256
  (`89cf956e...`), y el JSON parseado es igual (200 predicciones). Las copias de trabajo difieren
  en bytes solo por fin de linea (la de `evidence/` se extrae con CRLF).
- 6.3 (`S/06-implementacion.tex:37`): "Tres disparadores (\emph{triggers}) ... telefonía
  (callback de grabación de Twilio)". `n8n/workflow.json`: webhooks `telefonia-handoff`,
  `incidente-web` y `notificacion-clasificacion`, mas el trigger IMAP.
- 4.2 (`S/04-marco-metodologico.tex:16`): cronometraje mutuo sin decir que el observador de `A1`
  era `T1`.
- 2.4 (`S/02-marco-teorico.tex:32`): "; Los autores de esta tesis infieren" y "reclama retribuir a
  quienes producen el conocimiento que usan los sistemas y sostener la supervisión humana".
- `Bibliography_base.bib:655-662`: `Zendesk2026_help_desk` con "{Zendesk} {S}uite" en titulo y
  nota; `:673-680` `ServiceNow2026_itsm` (URL sin respuesta en el dictamen).
- Menciones de `v1.2.16` como version entregada: `05-arquitectura.tex` (3: lineas 37, 78, 104),
  `06-implementacion.tex:10`, `11-aspectos-legales.tex:91`, `12-anexos.tex` (8 en 7 lineas: 9, 24, 31,
  44, 50, 60 y dos en 81). La nota de la Tabla 19 (`:81`) declara `git diff --stat cda7712 v1.2.16
  -- App/ n8n/ docker/ docker-compose.yml` (24 archivos); c-195 no toca esas rutas.
- PDF: 118 paginas; resumen y abstract dentro de 250 palabras (no se tocan).

## Goals / Non-Goals

**Goals:**

- (Diferido a los autores, D1) Que 7.5 diga solo lo que el repositorio muestra sobre el consentimiento.
- Una sola lectura de la segunda sub-hipotesis, con la asimetria declarada en su definicion (D2).
- Que el Anexo I trace los nueve dictamenes que corresponden y que el verificador detecte un ciclo
  sin trazar (D3, D4).
- Que el MDE impreso sea el que produce el analisis versionado, o que la discrepancia quede
  declarada (D5).
- Cerrar la propagacion pendiente, Zanzotto y los residuales de forma (D6-D8).
- Release `v1.2.17` con el patron de hash vigente (D9).

**Non-Goals:**

- Recabar las firmas (lo hacen los autores con el director, fuera del repositorio).
- Nuevas mediciones, corridas del clasificador o del corpus; cambios en `App/`, `n8n/`, `docker/`.
- El change `c-191` (activo, de otro autor): no se toca ni se menciona en 11.8 (D8).
- Reducir el PDF al tope de 100 paginas; editar el resumen o el abstract.

## Decisions

### D0 — Verificacion previa (bloqueante, solo lectura)

Script descartable en el scratchpad que reproduzca: Wilson 25/147 = [0,1179; 0,2390];
P(X >= 25 | n = 147, p = 0,15) ≈ 0,28; MDE con 0,864 / 9/pi^2 / sin ARE = 0,2834 / 0,2763 /
0,2644; igualdad de los blobs de las dos caches (`git show HEAD:<ruta> | sha256sum`) y del JSON
parseado (200 predicciones); Wilson del ejemplo de dimensionamiento de D8 (p = 0,10: n = 150 da
limite superior 0,158; n = 200, 0,149); conteo de `auditorias/Dictamen_*.md` = 9. Si una cifra no
se reproduce, esa recomendacion se detiene y se consulta.

### D1 — Consentimiento (A1; gobernanza HIGH) — DIFERIDA A LOS AUTORES

**Decision posterior a la propuesta (2026-11-09): diferida a los autores; la redacta Luca Gomez con
las firmas, fuera de c-195.** El co-autor Luca Gomez reescribira 7.5 el dia siguiente, cuando los
cuatro participantes (E1, E2, O1, O2) hayan firmado, con las fechas reales. Por lo tanto este change
NO edita `S/11-aspectos-legales.tex` (7.5), `docs/campana-medicion/confirmacion-posterior-consentimiento.md`
ni `evaluation/data/campana/README.md`. La recomendacion A1 y los items 1 y 2 del inventario quedan
registrados como "PENDIENTE (diferida: la atienden los autores al recabar las firmas)"; el verificador
acepta el estado PENDIENTE y omite esas filas. Los requisitos de consentimiento (registro y plantilla)
se retiran del delta spec: la spec principal conserva su redaccion vigente hasta que el change de los
autores la modifique.

Texto que se habia propuesto (conservado solo como referencia para quien redacte 7.5; no se aplica
aqui): las dos ultimas oraciones del parrafo de 7.5 se reemplazarian por la declaracion de que la
confirmacion escrita esta pendiente, con custodia del director y registro sin identidad en el README
de la campana; la plantilla unificaria el encabezado con las cinco columnas de su tabla
(`alias, rol, fecha_informacion_verbal, fecha_confirmacion, custodia`) y pasaria a ser un modelo.
Con las firmas ya obtenidas, la redaccion correcta es la del pasado con las fechas reales, que no se
reconstruyen aqui.

Riesgo asumido y declarado: hasta que los autores reescriban 7.5, el texto vigente ("firmaron una
confirmacion escrita ...") es la declaracion que el dictamen observa; c-195 no la corrige.

### D2 — Segunda sub-hipotesis (A2)

- **8.3** (`S/07-resultados.tex:154`): la oracion "Medirla en condiciones válidas exige una
  corrida con reportantes identificados (\autoref{subsec:medicion-intervencion})." se reemplaza
  por "Extender esta conclusión al formulario web y a reportantes identificados en el directorio
  exige una corrida en la que la revisión alcance a todos los canales
  (\autoref{subsec:medicion-intervencion})."
- **8.3 y 9.1** (`S/08-discusion.tex:8`): "de modo que la lectura conservadora es que no se puede
  descartar un valor cercano al umbral" -> "de modo que el intervalo no permite descartar una
  proporción inferior a la cota (su límite inferior es 11,8~\%)". En 9.1 puede omitirse el
  parentesis para no repetir la cifra.
- **1.4 y 4.7**: tras la definicion de la regla de tres vias se agrega: "La regla es asimétrica:
  \emph{refutada} significa que la estimación puntual alcanza la cota, no un rechazo estadístico
  de la hipótesis $p \leq 0{,}15$, mientras que \emph{compatible} exige que todo el intervalo
  quede por debajo de ella." En 4.7 puede abreviarse a "La regla es asimétrica (véase la
  \autoref{subsec:hipotesis-trabajo})" si se busca ahorrar lineas; la definicion completa debe
  quedar al menos en 1.4 y la mencion de la asimetria en ambos.
- Resumen y abstract: no se tocan (el veredicto "refutada sobre los 147 casos revisados" sigue
  siendo correcto; la asimetria se declara en la definicion). Se mide el conteo con la regla de
  c-106 solo para registrar que no cambio.

Alternativa descartada: cambiar la regla o el veredicto. El dictamen pide declarar la asimetria,
no reabrir el contraste.

### D3 — Anexo I: conteo y dos tablas nuevas (A3)

- Parrafo de presentacion (`S/12-anexos.tex:205`): "La serie comprende siete dictámenes" ->
  "nueve dictámenes"; "Este anexo traza cuatro: ..." -> "traza seis: ... el del 9 de noviembre
  sobre la \texttt{v1.2.12} (\autoref{tab:anexo-trazabilidad-0911}), el del mismo dia sobre la
  \texttt{v1.2.13} (\autoref{tab:anexo-trazabilidad-0911-v1213}) y el del mismo dia sobre la
  \texttt{v1.2.16} (\autoref{tab:anexo-trazabilidad-0911-v1216})".
- **Tabla del dictamen sobre `v1.2.13`** (`tab:anexo-trazabilidad-0911-v1213`), formato de
  `tab:anexo-trazabilidad-0911` (`\footnotesize`, columnas Rec. | Change | Secciones), con las
  recomendaciones del archivo `auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md` (la
  numeracion del dictamen manda sobre la del registro) y los changes de las secciones c-192, c-193
  y c-194 de `C/dictamen-correcciones.md`. Borrador de filas (las anclas se confirman con
  `rg -n "\\label\{"` al aplicar):
  - A1 (hash del PDF del tag) — `c-192` — `sec:anexo-repositorio`.
  - A2 (lectura unica de la sub-hipotesis) — `c-192` — `subsec:reduccion-intervencion`,
    `subsec:interpretacion-resultados`, `tab:cumplimiento-objetivos`.
  - A3 (kappa de 1.6) — `c-192` — `subsec:justificacion`.
  - B1 (laxo por interseccion) — `c-192` — `subsec:resultados-campana-medicion`.
  - B2 (MDE del Spearman) — `c-192` — `subsec:resultados-campana-medicion`.
  - B3 (propagacion: 6.3, Xiong, 7.5) — `c-192` — `subsec:construccion-flujo-n8n` (o la
    subseccion de 6.3), la de Xiong en el capitulo 3, `subsec:consentimiento-derechos`.
  - B4 (nivel pago y consentimiento) — `c-193` — `subsec:transferencia-internacional`,
    `subsec:consentimiento-derechos`.
  - C1 (VIS, fila "Lim.", Zanzotto) — `c-192`, `c-194` — `subsec:reduccion-intervencion`,
    `tab:anexo-trazabilidad-2810`, `subsec:human-in-the-loop`.
  - C2 (FrugalGPT, Zendesk, URL) — `c-192`, `c-194` — Lista de referencias.
- **Tabla del dictamen sobre `v1.2.16`** (`tab:anexo-trazabilidad-0911-v1216`), mismo formato,
  change `c-195` en la leyenda (como la del 8-11, sin columna Change para ahorrar ancho): A1
  `subsec:consentimiento-derechos`; A2 `subsec:hipotesis-trabajo`, la subseccion de 4.7,
  `subsec:reduccion-intervencion`, `subsec:interpretacion-resultados`; A3
  `sec:anexo-trazabilidad`; B1 `subsec:resultados-campana-medicion`; B2 la subseccion de 6.3,
  `subsec:diseno-experimental` (4.2), `subsec:resultados-campana-medicion`; B3
  `subsec:human-in-the-loop`; C1 `subsec:human-in-the-loop`, `subsec:reduccion-intervencion`,
  `sec:recomendaciones`; C2 `subsec:medicion-intervencion`, Lista de referencias.
- Cuerpo `\footnotesize`, `\setlength{\tabcolsep}{4pt}`, filas de una o dos lineas, misma nota de
  fuente que las demas. Sin numeros de linea.

### D4 — Registro y verificador (A3, Strict TDD)

- `C/dictamen-correcciones.md`: en cada seccion c-192, c-193 y c-194 se agrega una subseccion
  "### Matriz de trazabilidad (verificada por `verificar_matriz_trazabilidad.py`)" con la matriz
  de 7 columnas; las tablas de 5 columnas existentes se conservan. Las filas cuyo parrafo reescribe
  c-195 (7.5 de c-193; "callback de grabación" de c-192; Zanzotto de c-194; la frase del matiz de
  c-192) van como `SUPERADA por c-195`. Seccion nueva "## Dictamen v10 / v1.2.16 (2026-11-09) -
  c-195" con: resumen, matriz de 7 columnas (una fila por recomendacion A1-C2 y por item 1-18,
  fragmentos tomados del texto final), decisiones (D1, D5 con el camino tomado, D8, D9), estado de
  la URL de ServiceNow, items fuera de alcance, libro mayor de paginas y palabras y nota de release.
- `C/verificar_matriz_trazabilidad.py`: el parser ya lee toda matriz de 7 columnas en cualquier
  seccion, asi que las matrices nuevas se verifican sin cambiar el parseo. Lo que falta es que el
  verificador detecte la regresion que observo el dictamen (un ciclo sin matriz). Se agrega una
  funcion pura `secciones_sin_matriz(texto, desde=190)` que devuelve los titulos `## Dictamen ...`
  cuyo change `c-NNN` (ultimo `c-\d+` del titulo) es >= `desde` y que no tienen ninguna fila de
  matriz; `main` cuenta cada una como falla con el mensaje "FALLA seccion sin matriz: <titulo>".
  Orden TDD: (1) pruebas nuevas en `C/test_verificar_matriz_trazabilidad.py` (seccion c-192 sin
  matriz -> falla; con matriz -> no; seccion c-188 sin matriz -> no se cuenta; titulo sin change ->
  no se cuenta; `main` con una seccion sin matriz devuelve 1) que fallan; (2) codigo minimo;
  (3) triangulacion; (4) agregar las matrices al registro y correr el script sobre el arbol (0
  fallas). Safety net previa: `python -m unittest test_verificar_matriz_trazabilidad
  test_resumir_registro_compilacion -v` en verde y el script en 0 fallas.
- Gotcha gitleaks: en la prosa del registro usar "seccion N (`archivo.tex`)", nunca "capitulo"
  seguido de coma o igual y un token largo.

### D5 — MDE del Spearman alineado con el analisis (B1; codigo MEDIUM, Strict TDD)

**Camino preferido (codigo + regeneracion):**

1. Safety net: en el venv 3.13 (`%TEMP%\v313`), desde `evaluation/`, con las variables dummy del
   CI (`.github/workflows`: `DATABASE_URL`, `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`,
   `JWT_SECRET_KEY`, `COST_GUARD_CALLER_HMAC_KEY`, `DIRECTORY_BLIND_INDEX_KEY`), correr
   `tests/test_stats.py` y `tests/test_campana.py`; registrar el baseline.
2. RED: en `tests/test_stats.py`, prueba de la constante nueva `ARE_SPEARMAN` (valor 0,9119 a
   cuatro decimales, contra el literal, no contra `9/pi**2`) y de
   `tanh(efecto_minimo_detectable(107, eficiencia_relativa=ARE_SPEARMAN))` = 0,2763; en
   `tests/test_campana.py:1632` cambiar el esperado del MDE del Spearman a `ARE_SPEARMAN`; las
   pruebas de 1459 y 1549 (Mann-Whitney/Wilcoxon con `ARE_WILCOXON_MINIMA`) quedan como estan y
   prueban que esos MDE no cambian. Ejecutar: fallan.
3. GREEN: `ARE_SPEARMAN = 9 / math.pi ** 2` en `evaluation/stats.py`, junto a
   `ARE_WILCOXON_MINIMA`, con comentario (eficiencia asintotica de Spearman frente a Pearson bajo
   normalidad); importarla en `evaluation/campana.py` y usarla SOLO en la linea 1593. Ejecutar:
   pasan. Triangular con el bloque de O2 (n = 18 u otro de la fixture) y refactor sin cambios de
   comportamiento.
4. Regenerar con el comando de referencia de `evaluation/data/campana/analisis/README.md`
   (`python -m evaluation.analisis_campana --entrada evaluation/data/campana --salida
   evaluation/data/campana/analisis --pines-in-sample '{"google_genai": ">=2.20.0", "modelo":
   "gemini-3.6-flash"}' --rango-google-genai-vigente ">=2.33,<3"`), sin red ni Gemini. Antes,
   confirmar que `plantilla_etiquetado.csv` y `predicciones_in_sample.json` coinciden con
   `SHA256SUMS.txt` (no hace falta re-ensamblarlas).
5. Criterio de aceptacion (script en el scratchpad): comparar el `resultados.json` nuevo con
   `git show HEAD:...resultados.json` hoja por hoja; las UNICAS hojas distintas deben ser las dos
   rutas `...posicion.spearman.mde`, con valor nuevo ≈ 0,2763. `resultados.md`: solo cambian las
   lineas que contienen esos valores. `SHA256SUMS.txt`: solo las filas de `resultados.json` y
   `resultados.md`. Cualquier otra diferencia, o un error de ejecucion por red o entradas
   faltantes, activa el camino alternativo.
6. Si se acepta: actualizar `numeros-canonicos.md` (fila 851, seccion (c) 928-937 y huellas de
   742-743) y la fila del registro; 8.7 conserva 0,276 y la formula (sin texto nuevo).

**Camino alternativo (si falla 5):** `git restore` de `evaluation/stats.py`,
`evaluation/campana.py`, las pruebas y las salidas; 8.7 agrega, tras la formula: "valor
recalculado fuera del análisis versionado (\path{evaluation/data/campana/analisis/resultados.json}),
que con la eficiencia de la prueba de Wilcoxon informa 0,2834". El registro anota el motivo.

Criterio de decision: el preferido se adopta solo si la regeneracion es reproducible sin red y el
diff se limita a los dos MDE; no se aceptan diferencias "menores" en otras hojas.

### D6 — Propagacion pendiente (B2)

- **6.3** (`S/06-implementacion.tex:37`): "Tres disparadores (\emph{triggers}) reciben las
  entradas desde correo electrónico (IMAP), formulario web (Webhook) y telefonía (callback de
  grabación de Twilio)" -> "Tres disparadores de canal (\emph{triggers}) reciben las entradas
  desde correo electrónico (IMAP), formulario web (Webhook) y telefonía (webhook
  \texttt{telefonia-handoff}, al que el backend entrega la transcripción)". Cotejar con 5.2 y 6.4
  que digan lo mismo; MUST NOT aparecer "webhook de transcripción" (requisito de c-187). El cuarto
  webhook (`notificacion-clasificacion`) ya figura en el Anexo E; no se agrega texto.
- **4.2** (`S/04-marco-metodologico.tex:16`): tras "Así se atenuó, sin eliminarlo, el efecto
  Hawthorne ... \parencite{McCambridge2014_hawthorne}, ..." se agrega: "La atenuación es menor
  para \texttt{A1}: en el cronometraje mutuo, su observador fue \texttt{T1}, autor del trabajo."
  (sin repetir que T1 conocia el proposito, ya dicho en la oracion previa).
- **8.7** (`S/07-resultados.tex:251`): "El 0,7971 proviene de
  \texttt{predicciones\_in\_sample.json} (7-10), no de la salida en vivo" -> "El 0,7971 proviene
  de \texttt{predicciones\_in\_sample.json} (7-10), que contiene las mismas 200 predicciones que
  \path{evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json}, y no de la salida en vivo".
  Verificado en D0 sobre los blobs.
- **`numeros-canonicos.md`**: (b'') lineas ~811-826: el estado vigente pasa a "refutada sobre los
  147 revisados (25/147 = 0,170; Wilson [0,118; 0,239]; binomial p = 0,28; el intervalo no
  descarta una proporcion inferior a la cota); 25/200 = 0,125 queda como dato secundario"; las
  notas historicas de c-187 se conservan marcadas "superado por c-190". Linea ~920: "la unión" ->
  "la intersección" (130/151; la union daria 137). Fila del MDE segun D5.

### D7 — Zanzotto (B3)

`S/02-marco-teorico.tex:32`: "En línea con el paradigma \emph{HitAI},
\textcite{Zanzotto2019_human_in_the_loop} reclama retribuir a quienes producen el conocimiento que
usan los sistemas y sostener la supervisión humana." -> "En línea con el paradigma \emph{HitAI},
\textcite{Zanzotto2019_human_in_the_loop} reclama retribuir a quienes aportan el conocimiento que
usan los sistemas." La supervision humana queda respaldada en el mismo parrafo por Amershi et al.
y Shneiderman. Alternativa descartada: paginar el pasaje; el cuerpo del articulo no fue accesible
y el resumen no lo respalda.

### D8 — Forma y bibliografia (C1, C2)

- `S/02-marco-teorico.tex:32`: "; Los autores" -> "; los autores".
- 8.3: "corresponden a la regla de visibilidad y derivación por reportante no identificado
  (\texttt{VIS-005}), que el backend aplica" -> "corresponden a la regla de derivación por
  reportante no identificado (requisito \texttt{VIS-005} de la especificación de visibilidad de
  incidentes, c-82), que el backend aplica". VIS sigue desarrollada en su primer uso.
- 11 (`S/10-recomendaciones.tex:6`): "la medición de la intervención humana con reportantes
  identificados (\autoref{subsec:medicion-intervencion}), que la campaña complementaria de
  medición refutó sobre los casos revisados" -> "..., cuya sub-hipótesis la campaña
  complementaria refutó sobre los casos revisados".
- 11.3 (`S/10-recomendaciones.tex:18`): "Dos requisitos acotan esa medición futura: que ... y que
  ..." -> "Tres requisitos acotan esa medición futura: que ..., que ... y que la muestra se
  dimensione para que el límite superior del intervalo de Wilson pueda quedar por debajo de 0,15:
  con una proporción cercana a la cota, una muestra del orden de 150 casos no permite declarar
  compatibilidad." (D0: con p = 0,10, n = 150 da 0,158 y n = 200, 0,149.)
- 11.8: NO se menciona `c-191`. El dictamen lo condiciona a que la validacion se ejecute antes de
  la defensa; hoy esta propuesta y es de otro autor. Se registra como fuera de alcance.
- `Bibliography_base.bib`: nota de `Zendesk2026_help_desk` sin "Suite" ("Página del producto de
  software de servicio al cliente de {Zendesk}"); el titulo se ajusta al `<title>` real de
  `https://www.zendesk.com/service/` verificado con `curl -sL -A "Mozilla/5.0"` (si no incluye
  "Suite", se retira tambien del titulo). `ServiceNow2026_itsm`: `curl -sI -A "Mozilla/5.0"
  https://www.servicenow.com/products/itsm.html`; si responde 200 (o 301/302 a la misma pagina)
  se actualiza `urldate`; si no, se deja la entrada como esta y se registra el resultado (fecha,
  codigo) en la seccion c-195. `verify_citations.py` PASS.

### D9 — Release `v1.2.17` y paginas

- Patron de c-188/c-192: commit de contenido con la oracion del Anexo B ("El PDF compilado en el
  propio tag no imprime ese hash: el hash completo de \texttt{v1.2.17} se consigna en el commit que
  sigue al tag en la rama principal. Se verifica con \texttt{git rev-list -n1 v1.2.17}, y un
  \texttt{git diff --stat} entre el tag y la rama principal sobre \texttt{docs/Tesis/v10
  (IA)/paper/sections} muestra que ese commit solo cambia esa línea."); tag anotado `v1.2.17` sobre
  ese commit; commit siguiente que solo reemplaza esa linea por el hash completo.
- Las 13 menciones de `v1.2.16` (12 lineas) como version entregada pasan a `v1.2.17` (D0 las lista); se
  conservan las historicas (los dictamenes "sobre la \texttt{v1.2.16}" del Anexo I nuevo). La nota
  de la Tabla 19 recalcula `git diff --stat cda7712 v1.2.17 -- App/ n8n/ docker/
  docker-compose.yml` despues del tag (se espera 24 archivos; si cambia, se corrige en el commit de
  contenido con el conteo de `HEAD`, que es igual al del tag para esas rutas). La fecha de la
  portada es la de la release.
- Compilacion en Docker (`export MSYS_NO_PATHCONV=1; docker run --rm -v "$PWD/docs/Tesis/v10
  (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`, 2-4 min, en segundo plano);
  `compilacion.md` con `C/resumir_registro_compilacion.py`; `tesis_para_agente.md` con
  `build_tesis_para_agente.py`.
- **Paginas (decision):** linea base 118. Se acepta el crecimiento causado solo por las dos tablas
  del Anexo I, hasta 120 paginas, y se registra en el libro mayor (antes, despues, causa, fecha).
  Si supera 120: compactar las tablas (agrupar filas, recortar secciones repetidas) y recompilar;
  si aun supera, detener y consultar. El resto de las ediciones se escribe neutro en lineas
  (reemplazos de igual o menor extension donde se pueda).
- Gotchas: filas de tabla con `\\` (no `\`); no escribir LaTeX desde Python sin cadenas crudas
  (`\t` en `\texttt`); gitleaks y "capitulo".
- `CHANGES.md`: FASE 60 con la entrada C-195 (formato de FASE 58/59) y actualizacion de la linea
  "Total" (activos c-191 y c-195; release vigente `v1.2.17`; `v1.2.16` superada, inmutable en
  `ca3c885`).

## Risks / Trade-offs

- [El texto de 7.5 queda en futuro y puede quedar desfasado cuando se firme] -> el requisito ata el
  texto al estado del registro; el change que complete las fechas reescribe 7.5 en pasado.
- [Fechas de la informacion verbal desconocidas para el README] -> se marcan "pendiente"; no se
  derivan de la fecha de la campana (seria una reconstruccion).
- [La regeneracion del analisis cambia mas que el MDE (orden de claves, flotantes, version de
  scipy)] -> criterio estricto de D5 y camino alternativo con texto ya redactado.
- [Las dos tablas nuevas del Anexo I suben las paginas] -> decision registrada, tope 120,
  `\footnotesize` y filas compactas.
- [La regla nueva del verificador marca secciones viejas] -> umbral `desde=190`; c-190 ya tiene
  matriz, asi que solo exige c-192 en adelante, que este change completa.
- [Los rotulos de recomendacion del registro de c-192 no coinciden con los del dictamen v1.2.13
  (por ejemplo, Xiong figura como C2 en el registro y es B3 en el dictamen)] -> la tabla del
  Anexo I y las matrices usan la numeracion del dictamen; la discrepancia se anota en la seccion
  c-195.
- [La frase de 6.3 puede rozar el requisito que prohibe "webhook de transcripción"] -> la frase
  nombra el webhook por su ruta y el verbo "entrega", y el apply busca la cadena prohibida.
- [El Anexo I traza en `v1.2.17` el dictamen que esa misma release atiende] -> mismo criterio que
  `tab:anexo-trazabilidad-0911` con c-190; la tabla nombra secciones, no estados futuros.
- [Gitleaks en la prosa del registro] -> "seccion N (`archivo.tex`)".

## Migration Plan

Apply en el orden de `tasks.md` en la rama `change/c-195-atender-dictamen-v1-2-16`: verificacion
D0, checkpoint HIGH de D1, codigo con Strict TDD y regeneracion (D5), texto de la tesis,
registro y verificador (D4), compilacion, release. El orquestador hace los commits, el tag
`v1.2.17`, el commit del hash, `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` y el
PR contra `main`. Rollback: revertir los commits del change; si el tag ya se publico, queda
inmutable y se emite una release posterior. El camino alternativo de D5 es el rollback parcial
del codigo.

## Open Questions

- D1: diferida; la redacta Luca Gomez con las firmas, fuera de c-195.
- D5: el camino se decide por el criterio del diff; no requiere decision previa.
- D8: titulo de la entrada de Zendesk segun el `<title>` real de la pagina.
- `ServiceNow2026_itsm` conserva la nota "capacidades y precios"; el dictamen no la observa y la
  pagina no es verificable: se deja como esta y se anota como posible residual.
