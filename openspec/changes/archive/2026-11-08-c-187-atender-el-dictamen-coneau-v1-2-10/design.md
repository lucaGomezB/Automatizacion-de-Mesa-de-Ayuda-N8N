# Design: Atender el dictamen CONEAU sobre v1.2.10

## Context

El dictamen del 2026-11-08 (`auditorias/Dictamen_Tesis_v10_v1.2.10_CONEAU_2026-11-08.md`)
examina el tag `v1.2.10` (`c3c63c8`) y emite cinco observaciones de fondo (A1-A5), siete
de consistencia (B1-B7) y cinco de forma (C1-C5), con un inventario de 36 correcciones
puntuales con archivo y línea. Este change cubre A1-A5 y las B que tocan los mismos
párrafos (B1, B2, B3, B6). Es un change de documento: no cambia datos, código ni valores
canónicos (salvo el rótulo del denominador de A4).

**Numeración.** Las secciones compiladas no coinciden con el nombre de los archivos
(`paper/main.toc`): 4.x = `04-marco-metodologico.tex`, 6.x = `06-implementacion.tex`,
7 = `11-aspectos-legales.tex`, 8.x = `07-resultados.tex`, 9.x = `08-discusion.tex`,
10.x = `09-conclusiones.tex`, 11.x = `10-recomendaciones.tex`, Anexos =
`12-anexos.tex`. En este design, "8.3" es `subsec:reduccion-intervencion` y "8.7" es
`subsec:resultados-campana-medicion`.

**Deriva de líneas.** Las anclas del inventario del dictamen están numeradas sobre el tag.
En `main` varias aparecen desplazadas (por ejemplo `01-introduccion.tex:32` está en `:34`,
`04-marco-metodologico.tex:12/53/63/79/85` en `:14/55/65/81/87`,
`07-resultados.tex:157/159/161/250/254/256` en `:159/161/163/252/256/258`). `tasks.md`
da ambas (dictamen → `main`); en el apply cada ancla se localiza por el texto citado, no
por el número.

**Topes.** El PDF tiene 118 páginas (tope del equipo: 100); el change no debe agregar
páginas netas. El resumen tiene 245 palabras y el abstract 240 (tope 250 cada uno); el
párrafo de viabilidad 34/34 (ES) y 31/34 (EN) (`dictamen-correcciones.md`, release
v1.2.9). Toda adición al resumen se compensa con recortes en el mismo resumen.

## Goals / Non-Goals

**Goals:**

- Que cada cifra de la campaña complementaria signifique en el texto lo que los
  artefactos de `evaluation/data/campana/` muestran (A1, A2, A4, B1).
- Que la fiabilidad de la referencia de verdad y la independencia de los analistas
  originales queden declaradas y propagadas (A3).
- Que un jurado que reciba el PDF del tag `v1.2.11` pueda verificar la versión sin
  encontrar un hash ajeno, una imagen no declarada ni una fecha anterior a los datos (A5).
- Que los estados de las sub-hipótesis y de los objetivos sean idénticos en resumen,
  abstract, 1.4, 9.1, Tabla 18, capítulo 10 y 11.3.
- Registrar el dictamen y su trazabilidad (registro de correcciones y Anexo I).

**Non-Goals:**

- B4, B5, B7 y C1-C5 (change posterior).
- Nuevas mediciones, corridas del clasificador o re-análisis de la campaña. El único
  cálculo nuevo admitido es el intervalo de Wilson de 25/200, aritmética sobre conteos
  ya publicados.
- Corregir `docs/diagrams/cronograma.md:74` (ítem 36 del inventario) salvo que la Tabla 19
  o el Anexo B citen esa fecha.

## Decisions

### D0 — Verificación del mecanismo de derivación antes de reescribir (A1)

El dictamen atribuye los 147 casos intervenidos a la regla c-82 como **inferencia**
("que los autores deben confirmar"). Antes de tocar 8.3 se ejecuta una tarea de
verificación de solo lectura, sin mediciones nuevas:

1. Código: `App/Backend/app/services/incidente_service.py` (docstring de
   `crear_incidente`: "Un reportante no identificado persiste NULL y deriva a revision
   humana (VIS-005)") y las rutas que resuelven `reportante_empleado_id` por canal
   (VIS-003/VIS-004); confirmar cómo se resuelve el reportante en el formulario web
   (hipótesis: por la sesión autenticada, lo que explica `revision = false` en los 53
   casos) y en correo y telefonía (por `reportante_email` / `reportante_telefono`, que el
   flujo N8N propaga desde c-162).
2. Datos: cruzar `intervenciones.csv` (147 filas, todas `origen_intervencion = gate`,
   122 confirmaciones y 25 cambios) con los ocho `sidecar_*.json` (66/66 correo con
   `revision = true`, 81/81 telefonía con `revision` nulo, 0/53 web con
   `revision = false`) y con `predicciones_hybrid-v3_2026-10-07.json` (92 determinísticos
   y 55 de Gemini entre los intervenidos); confirmar que los remitentes
   `corpus-RXXX@corpus.local` y el número del softphone no figuran en el directorio de
   empleados sembrado en el despliegue de la campaña.
3. Despliegue: `docs/campana-medicion/guia-ejecucion-campana.md`, los runbooks y
   `git log` del 5 al 7-11 para fijar con qué revisión corrió cada tramo. Hallazgo
   preliminar: la campaña **no corrió sobre un único commit** (brazo automatizado de
   correo y web el 5-11 con `cda7712`/`9109a03`; telefonía el 6-11 tras c-174 y c-175;
   intervenciones validadas el 7-11, `validado_en` del export, en paralelo con c-177 a
   c-182; el README declara que parte de las intervenciones de `O1` se hicieron con una
   imagen del frontend previa a c-165). La columna de la campaña de la Tabla 19 consigna,
   por tanto, un **rango de revisiones** con sus fechas, o "commit no registrado en los
   sidecars" con el rango acotado por `git log`, nunca un commit inventado.
4. Resultado: una nota de verificación en `dictamen-correcciones.md` (sección del change)
   con el mecanismo confirmado y su evidencia. **Si la verificación no confirma c-82**
   (por ejemplo, otra causa de `requiere_revision_humana`), el apply se detiene y se
   consulta al usuario antes de reescribir 8.3; el texto nunca afirma un mecanismo no
   verificado.

Alternativa descartada: reescribir 8.3 tomando la inferencia del dictamen como hecho. Se
descarta porque reproduciría el mismo defecto que el dictamen observa (afirmar más de lo
que los artefactos muestran).

### D1 — Derivación por confianza frente a derivación por reportante (A1)

8.3 (`07-resultados.tex`, párrafos del gate y de la sub-hipótesis 2) se reescribe con dos
magnitudes separadas:

- **Derivación por confianza** (regla de 0,70 sobre Gemini): 0 casos en el corpus
  (resultado fuera de línea de la configuración evaluada, que se conserva).
- **Derivación por reportante no identificado** (c-82, activa en la campaña
  complementaria): 147 de 200 casos, desglosada por canal (66/66 correo, 81/81 telefonía,
  0/53 formulario), independiente de la etapa y de la confianza.

La frase "Sobre el 65,5 % de los casos no existió … derivación" (B2) se retira o se
reescribe: el 65,5 % es la cobertura de la etapa determinística, no una proporción de
derivación. La frase "El origen de todas las intervenciones registradas fue el gate" se
precisa: el `origen_intervencion = gate` del export registra que la intervención la
disparó el indicador `requiere_revision_humana`, no la regla de confianza.

### D2 — Estado de la sub-hipótesis 2 (A1)

La regla de tres vías declarada (límite superior < 0,15: compatible; estimación ≥ 0,15:
refutada; estimación < 0,15 con límite superior ≥ 0,15: no concluyente) se aplica a dos
lecturas que la tesis reporta juntas y con su rótulo:

| Lectura | Valor | IC de Wilson 95 % | Veredicto |
|---|---|---|---|
| Tasa bruta de intervención (cualquier intervención) | 147/200 = 73,5 % | [67,0 %; 79,1 %] | no compatible con 0,15, pero mide la configuración de la prueba (regla c-82), no la necesidad de revisión del clasificador |
| Intervenciones que cambiaron la derivación | 25/200 = 12,5 % | [8,6 %; 17,8 %] | **no concluyente** |

**Estado reformulado de la sub-hipótesis 2: "no concluyente".** La medida pertinente a la
variable que la hipótesis define ("proporción de casos del flujo automatizado que
requieren acción manual de un operador") es la de las intervenciones que cambian la
derivación, porque las 122 confirmaciones fueron provocadas por una regla de
identificación ajena a la clasificación. La tesis declara además que la tasa bruta no es
compatible con la cota, por qué, y que una medición válida de la variable exige una
corrida con reportantes identificados (línea futura de 11.3). El intervalo [8,6 %;
17,8 %] se recomputa en el apply con la misma función de Wilson del análisis y se
registra en `numeros-canonicos.md` como entrada nueva (no reemplaza ningún valor).

Propagación con estado idéntico: 1.4 (`01-introduccion.tex`, sub-hipótesis 2), resumen y
abstract (el paréntesis "(73,5 %, IC [67,0 %, 79,1 %])" se reemplaza por una formulación
que nombra la magnitud y no puede confundirse con la exactitud, que también es 147/200),
9.1 (`08-discusion.tex:8`, que además debe mencionar la sub-hipótesis 2), Tabla 18 (fila
del objetivo general: retirar "medida y refutada"; fila del OE4: "alcanzado" se matiza
a "alcanzado parcialmente" o se acota a tiempo y exactitud manual, sin apoyarse en la
intervención), y 11.3 (`10-recomendaciones.tex`, `subsec:medicion-intervencion`: retirar
"reducir … respecto del 73,5 %" como defecto del clasificador y plantear la medición con
reportantes identificados). El título de `subsec:reduccion-intervencion` se revisa para
que sea coherente con "no concluyente".

Alternativa descartada: mantener "refutada" con una nota al pie. Se descarta porque el
dictamen objeta que la variable medida no es la postulada; una nota no cambia el
veredicto que el texto comunica.

### D3 — Tabla 19 (A1, A5)

`tab:configuracion-evaluada-entregada` (`12-anexos.tex`):

- Columna "Configuración de la campaña de medición" → rótulo "campaña complementaria"
  (B3) y celdas completadas con lo verificado en D0: rango de revisiones y fechas,
  `classifier_version = hybrid-v3`, revisión por reportante no identificado **Sí (c-82)**,
  propagación del contacto del reportante **Sí (c-162)**, instrumentación de c-165, imagen
  de N8N (oficial 2.11.2 hasta c-182; derivada desde el 7-11 si algún tramo corrió con
  ella; se determina por fecha). Celdas no verificables: "no registrado", no "---".
- Fila "Propagación del contacto…": "(c-162, posterior a la campaña)" → "posterior a la
  campaña 2026-10".
- Fila "Sin cambios": retirar "N8N 2.11.2" de la celda combinada y agregar una fila
  "Imagen de N8N": evaluada `n8nio/n8n:2.11.2`; entregada imagen derivada
  (`docker/n8n/Dockerfile`, `FROM n8nio/n8n:2.11.2` + parche de decodificación IMAP,
  c-182).
- Nota de fuente: reemplazar "(la misma configuración evaluada, commit `d6bb474`)" por
  "el mismo clasificador congelado que la configuración evaluada (`hybrid-v3`), sobre un
  backend posterior con c-82 y c-162 activos".
- 6.1 (`06-implementacion.tex:5`/`:10`): declarar la imagen derivada de la configuración
  entregada en una oración.
- La tabla no debe crecer en altura de forma que agregue una página: se compactan celdas
  existentes si hace falta.

### D4 — Orden ejecutado (A2)

- 4.2 (`04-marco-metodologico.tex:14`) y 4.5 (`:65`): el plan asignaba `brazo_primero`
  por caso, pero en la ejecución el brazo manual precedió al automatizado en los 200
  casos (manual: 5-11 09:20-18:49 −03; automatizado: 5-11 23:47 UTC a 6-11 22:45 UTC) y
  los dos grupos se intercalaron por `posicion` en la misma ventana, sin el turno 1 →
  turno 2 del runbook (`docs/campana-medicion/runbook-campana-contrabalanceada.md`).
- 4.6 (`:81`): el contraste entre grupos `brazo_primero` no estima el efecto de orden.
- 4.7 (`:87`): el efecto de orden queda como amenaza **no resuelta**; se retira "sí
  aborda el efecto de orden con el contrabalanceo".
- 8.7 (`07-resultados.tex:258`): el contraste de condición se reporta (si se conserva)
  rotulado como comparación entre dos subconjuntos que recibieron la misma condición en
  el mismo orden, **sin** valor como evidencia sobre el orden; se conserva el efecto de
  posición (Spearman) como único análisis válido: no significativo para `O1` (ρ =
  −0,0628, p = 0,5147), significativo para `O2` (ρ = −0,3604, p = 0,00011).
- 9.1/explicaciones rivales (`08-discusion.tex:22`): retirar "se abordó con un diseño
  contrabalanceado"; el orden manual → automatizado sesga, de hacerlo, en contra de la
  hipótesis de tiempos (argumento ya presente que se conserva).

Recomendación de economía: retirar los dos valores p del contraste de condición de 8.7
(ahorra espacio y elimina la lectura errónea) y consignarlos solo en el memo.

### D5 — Referencia de verdad y analistas (A3)

- 4.4 (`04-marco-metodologico.tex:55`): "ajenos al equipo de autores del trabajo" → uno
  de los dos analistas originales (`T1` en `registro_sujetos.csv`) es autor; el otro
  (`A1`) es externo; ambos operaron el brazo manual de 2026-10. Se conserva que no
  participaron del diseño del clasificador ni vieron las predicciones si los artefactos lo
  sostienen. Sin datos personales.
- 4.7 y 9.4 (`08-discusion.tex:54`, "Sexto…"): la limitación incorpora la coincidencia
  analista-autor.
- 9.4: nueva limitación, compacta, sobre la fiabilidad de la referencia: kappa 0,5569
  (moderado; IC [0,4725; 0,6413]; tabla conservada) frente a 0,87 (sin intervalo; tabla
  no conservada); el consenso `E1 = E2` coincide con el sector original en 116/138
  (84,1 %); las métricas primarias se calculan contra la referencia original y heredan su
  incertidumbre.
- 10.2 (`09-conclusiones.tex:51`): la segunda contribución ("doble etiquetado") se
  matiza con el kappa moderado de la campaña complementaria.
- Resumen y abstract: ambos kappa con su naturaleza (en la formulación más corta posible).

### D6 — Denominador del brazo manual (A4)

Se elige **conservar la unidad por derivación** y corregir el rótulo, en lugar de
recalcular por caso único:

- 8.7 (`07-resultados.tex:256`): "0,8278 (125 de 151 derivaciones de operador, 80 de `O1`
  y 71 de `O2`, sobre 138 casos únicos, 13 con doble cobertura; IC bootstrap por caso
  [0,7647; 0,8882])" y "laxa, de 0,8609 (130 de 151)".
- Comparación con el automatizado: declarar que 110/138 es por caso y 125/151 por
  derivación, y que el contraste formal es el McNemar por operador (que ya empareja
  casos), no la diferencia de proporciones agregadas.
- `e_man` = 0,1722 y los `a*` = 68,2/75,5/77,9 % de 9.6 (`08-discusion.tex:95`) **no
  cambian**: la tasa de derivación errónea es por derivación por definición, y el balance
  neto se expresa por derivación (304 derivaciones). Solo se agrega "por derivación" donde
  la oración lo deje ambiguo.
- Memo: la fila de la agregada (`numeros-canonicos.md`, sección (a), hoy `:768`) pasa a
  "125/151 derivaciones sobre 138 casos" y "130/151"; se anota el error de rótulo de
  `analisis/resultados.json` sin editar ese artefacto (salida del análisis; se declara).

Alternativa descartada: recalcular por caso único. Exige fijar un criterio ad hoc para los
13 casos de doble cobertura y propagar a `e_man`, sus intervalos y los tres `a*`, con
riesgo de introducir cifras no producidas por el análisis regenerable.

### D7 — Trazabilidad de la versión entregada (A5) — **decisión del usuario**

El patrón actual de dos commits (`c3c63c8` contenido + tag; `2103292` consigna el hash)
deja dentro del tag un PDF con el hash de la release anterior, porque un commit no puede
contener su propio hash. Opciones:

| Opción | Qué imprime el PDF del tag | Costo | Compatibilidad con la spec vigente |
|---|---|---|---|
| **A. Documentar el patrón y no imprimir un hash ajeno (recomendada)** | En el commit etiquetado, el Anexo B no muestra el hash anterior: dice que el hash de `v1.2.11` se consigna en el commit siguiente de `main` y da el procedimiento de verificación (`git rev-parse v1.2.11^{commit}`; `git diff --stat v1.2.11 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` muestra que solo cambia esa línea). El commit posterior reemplaza esa oración por el hash. | Bajo; sin scripts | Compatible: se modifica solo "Precisión del commit de referencia en el Anexo B" |
| B. Etiquetar el segundo commit | El hash del commit de contenido (padre del tag), declarado como tal; verificable con `git rev-parse v1.2.11^` | Medio: cambia qué commit etiqueta el tag y exige recompilar en el segundo commit | Requiere modificar los requisitos de hash del tag (el hash impreso ya no es el del tag) |
| C. Release de un solo commit sin hash en el PDF | Solo el nombre del tag y el comando de verificación; el hash va al registro y a `CHANGES.md` | Bajo | Contradice los requisitos que exigen el hash de 40 caracteres en el Anexo B |

**Recomendación: A.** Es la única que elimina el hash ajeno del PDF del tag sin tocar el
procedimiento de etiquetado ni los requisitos de hash vigentes, y mantiene el hash
completo en el PDF de `main`. Es gobernanza LOW. Si el usuario elige B o C, el cambio
pasa a MEDIUM y se ajustan los requisitos de hash antes del apply.

Además (no sujeto a decisión): imagen derivada de N8N en la Tabla 19 y en 6.1 (D3), y
portada (`00-portada.tex:30`, "30 de octubre de 2026") → fecha de la release `v1.2.11`.

### D8 — Consistencia de los párrafos tocados (B1, B2, B3, B6)

- **B1** (8.7): la exactitud automatizada 110/138 proviene de `predicciones_in_sample.json`
  (copia byte a byte de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`),
  no de la salida en vivo de la campaña, que difiere en 13 casos (7 de 119 escritos, 6 de
  81 telefónicos). Justificación: es la predicción del clasificador evaluado sobre la que
  se calculan todas las métricas primarias; la salida en vivo refleja el no determinismo
  de la inferencia. Se declara que el McNemar usa la caché. Se retira o acota "con el
  clasificador congelado" donde sugiera salida idéntica.
- **B2**: `07-resultados.tex:8` "2 y el 6 de octubre" → "del 2 y del 5 y 6 de octubre";
  `:159` "65,5 %" (D1); `:163` denominador de la proporción de tiempo: suma de los tiempos
  automatizados de 191 casos de la corrida, incluidos los no intervenidos, más la
  duración de las intervenciones; `:252` "alimentan únicamente el análisis del efecto de
  orden" → también la proporción de tiempo.
- **B3**: "campaña de medición" → "campaña 2026-10" o "campaña complementaria" según
  corresponda, en las leyendas de las Figuras 3 y 4, el pie de la Tabla 5
  (`05-arquitectura.tex:78`), el Anexo B y la Tabla 19. Si el rótulo está dentro de la
  imagen (PNG generado desde `docs/diagrams/*.md`), se regenera la figura; si solo está en
  la leyenda, se edita el `.tex`.
- **B6**: kappa moderado y efecto de posición en el capítulo 10 y el resumen; "dentro de
  la muestra" en 10.2 (`09-conclusiones.tex:47`); "5.000 casos" una sola vez (se
  conserva en 9.5, `08-discusion.tex:62`, y se retira de `10-recomendaciones.tex:14` y
  `12-anexos.tex:196`, con remisión); calificativo de interpretación en la "cota
  pesimista" de 9.4 (`08-discusion.tex:56`), igual al de 8.5.

### D9 — Registro y Anexo I

- `dictamen-correcciones.md`: sección "Dictamen v10 / v1.2.10 (2026-11-08) - c-187" con
  la matriz recomendación → ubicación → corrección, la nota de verificación de D0, la
  decisión de D7 y el conteo de páginas y palabras.
- `12-anexos.tex`, `sec:anexo-trazabilidad`: tercera tabla `tab:anexo-trazabilidad-0811`
  con la estructura común de las dos anteriores (Rec. | Change | Secciones), filas A1-A5,
  B1, B2, B3, B6 y una fila que remita B4, B5, B7 y C1-C5 al change posterior; párrafo
  introductorio breve. `:200` "cinco dictámenes … entre el 20 y el 28 de octubre" → seis,
  hasta el 8 de noviembre.
- Para no agregar páginas, la tabla nueva usa `\small` y filas de una línea cuando sea
  posible; si el Anexo I crece, se compensa en las reescrituras del cuerpo.

## Risks / Trade-offs

- [La verificación D0 no confirma c-82] → el apply se detiene en el grupo 1 y se consulta
  al usuario; ninguna reescritura de 8.3 se hace antes.
- [El commit de la campaña no es recuperable con precisión] → la Tabla 19 declara el rango
  y "no registrado"; no se inventa un commit.
- [Resumen y abstract superan 250 palabras al agregar kappas, mecanismo y posición] → cada
  adición se compensa en el mismo resumen; se mide con el mismo método de c-169 y se
  registra.
- [El change agrega páginas netas] → se reescriben párrafos más cortos (8.3, 8.7, 4.7) y se
  retiran cifras sin valor probatorio (p del contraste de condición); el conteo final se
  registra y se compara con 118.
- ["No concluyente" se lee como retroceso del objetivo 4] → la Tabla 18 lo explica en una
  línea: la variable no se midió en condiciones válidas por la regla del reportante.
- [Deriva de líneas entre el dictamen y `main`] → anclas por texto; `tasks.md` lista ambas.
- [Regenerar figuras por B3 cambia PNG sin necesidad] → solo si el rótulo está dentro de
  la imagen.

## Migration Plan

Apply en el orden de `tasks.md`; compilación con `latexmk -xelatex main.tex`,
`verify_citations.py` y `openspec validate --strict`. Release (orquestador, no el
sub-agente): commit de contenido, tag anotado `v1.2.11`, commit del hash según la opción
elegida en D7 (patrón `c3c63c8` / `2103292`), `engram sync` y PR. Rollback: revertir las
fuentes de la tesis y los dos memos al commit previo; no hay datos ni código que revertir.

## Open Questions

- **D7**: opción A (recomendada), B o C para el patrón de release. Se resuelve antes del
  grupo de A5.
- **D2**: confirmar con el usuario la redacción del estado "no concluyente" de la
  sub-hipótesis 2 y el grado del OE4 en la Tabla 18 ("alcanzado parcialmente" o
  "alcanzado" acotado a tiempo y exactitud manual).
- **D0**: cómo se resuelve el reportante del formulario web (sesión autenticada u otro
  mecanismo); el dictamen dice que "no transporta reportante", lo que por sí solo
  implicaría derivación bajo c-82, contrario al 0/53 observado. La verificación lo fija.
