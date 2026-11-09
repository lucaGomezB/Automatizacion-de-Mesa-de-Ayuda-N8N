# Design: Atender el dictamen CONEAU sobre v1.2.12

## Context

El dictamen del 2026-11-09 (`auditorias/Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`)
examina el tag `v1.2.12` (`7937efd`) y emite tres observaciones de fondo (A1-A3), cuatro de
consistencia (B1-B4), dos de forma y bibliografía (C1-C2) y un inventario de 30 correcciones
puntuales con archivo y línea. Además deja en el cuerpo del dictamen residuos sin
recomendación propia (11.3, redondeo del balance laxo, repositorios regionales, ISBN,
FrugalGPT, `main.log` no versionado). Este change los cubre todos; es un change de
documento: no cambia datos, código ni artefactos de `evaluation/`.

**Numeración.** Igual que en c-187: 4.x = `04-marco-metodologico.tex`, 5.x =
`05-arquitectura.tex`, 6.x = `06-implementacion.tex`, 7 = `11-aspectos-legales.tex`, 8.x =
`07-resultados.tex`, 9.x = `08-discusion.tex`, 10.x = `09-conclusiones.tex`, 11.x =
`10-recomendaciones.tex`, Anexos = `12-anexos.tex`. "8.3" es `subsec:reduccion-intervencion`;
"8.7" es `subsec:resultados-campana-medicion`.

**Anclas.** El dictamen numera sobre el tag `v1.2.12`; entre el tag y la cabeza de la rama de
c-188 las fuentes solo difieren en la línea del hash del Anexo B, de modo que las anclas son
casi exactas, pero en el apply cada lugar se localiza por el texto citado (`rg -n`).

**Verificaciones ya hechas al proponer** (solo lectura):

- `git diff --stat cda7712 v1.2.12 -- App/ n8n/ docker/ docker-compose.yml`: 24 archivos,
  1323 inserciones y 75 supresiones (control de costo y TwiML del backend, script y pruebas
  de reparación de codificación, cinco pruebas del backend, archivos del frontend,
  `docker-compose.yml` y `docker/n8n/{Dockerfile,apply-unified-patch.mjs,imap-simple-fromdata-charset.patch}`).
- `git diff --stat cda7712 v1.2.12 -- App/Backend/requirements.txt App/Frontend/package-lock.json n8n/workflow.json App/Backend/app/config/settings.py`: vacío.
- `git show v1.2.12:App/Backend/app/config/settings.py`: `gemini_stt_model = "gemini-3.5-transcribe"` (línea 238), usado por `App/Backend/app/clients/gemini_stt.py`.
- `tanh((z_{0,975} + z_{0,80}) / sqrt(107))` = 0,2644, frente a 0,2834 declarado en
  `07-resultados.tex:251` y en `numeros-canonicos.md:851` (fuente:
  `analisis/resultados.json:1154-1163,1326-1335`).

**Topes.** PDF de `v1.2.12`: 118 páginas (tope total del equipo: 100; exceso +18 declarado y
honrado por decisión registrada, requisito de presupuesto de páginas). Resumen y abstract:
239/239 palabras con el método sobre el `.tex` (237 con la regla de c-106); tope 250.

## Goals / Non-Goals

**Goals:**

- Que el estado de la segunda sub-hipótesis se apoye en un denominador defendible y sea
  idéntico en resumen, abstract, 1.4, 4.7, 8.3, 9.1, 10, Tabla 18 y 11.3 (A1).
- Que la descripción del enmascaramiento y del *debriefing* sea compatible con la condición de
  autor de un operador (A2).
- Que la Tabla 19 no afirme nada que `git diff` desmienta (A3).
- Una sola descripción del canal telefónico y del modelo de transcripción (B1); procedencia de
  cada cifra de la campaña declarada (B2); rótulos temporales unívocos, incluso dentro de las
  figuras (B3); formulaciones no más afirmativas que la evidencia (B4).
- Forma y bibliografía sin los residuos señalados (C1, C2).
- Que cada ítem del dictamen tenga tarea, fila en la matriz del registro y fila en el Anexo I.

**Non-Goals:**

- Revisar los 53 casos web, nuevas corridas o mediciones; cambiar el diseño de la campaña.
- Editar código o artefactos de `App/`, `n8n/`, `evaluation/` o `analisis/`.
- Ampliar el protocolo de revisión bibliográfica con búsquedas nuevas (D9).
- Reducir el PDF a 100 páginas (D7 decide si se intenta).

## Decisions

### D0 — Cruce de verificación antes de reescribir (A1, A2, B2)

Script descartable en el scratchpad, sin escribir en el repo, que reproduzca desde
`evaluation/data/campana/` y `data/corpus_evaluacion_pseudonimizado.json`: 147 intervenciones
(66 correo, 81 telefonía, 0 web), 25 cambios (14 telefonía, 11 correo) y 122 confirmaciones;
85 confirmaciones con consenso `E1 = E2` y 11 de ellas distintas del consenso; 13 cambios con
consenso (9/1/3); web 10/53 mal derivados frente a la referencia original con la caché y 7/40
frente al consenso; intervalos de Wilson 25/200 [0,0861; 0,1780], 25/147 [0,1179; 0,2390],
28/138 [0,1443; 0,2776], 53/200 [0,2087; 0,3302]; proporción de tiempo 0,5307 con los
tiempos de `corpus_campana.json` (2692,22 s, 191 casos) frente a 0,4811 con los del corpus de
octubre; exactitud laxa manual 130/151 con la unión de adicionales de E1 y E2 frente a 128/151
con los del corpus; y el origen de la salida en vivo telefónica (`sector_predicho` del export,
sidecars con sector nulo en los 81). Para A2: leer `registro_sujetos.csv` y la sección
"Sujetos" del README para fijar quiénes fueron los operadores de la campaña 2026-10, qué rol
tiene cada uno y si alguno es `T1`. **Si una cifra no se reproduce, el apply se detiene en esa
recomendación y se consulta a los autores**; el texto nunca adopta una cifra del dictamen sin
reproducirla.

### D1 — Estado de la sub-hipótesis 2 (A1) — **decisión de los autores**

La regla de tres vías declarada (límite superior < 0,15: compatible; estimación ≥ 0,15:
refutada; estimación < 0,15 con límite superior ≥ 0,15: no concluyente) da resultados
distintos según el denominador:

| Denominador | Valor | IC de Wilson 95 % | Veredicto con la regla |
|---|---|---|---|
| Todos los casos (25/200) | 12,5 % | [8,6 %; 17,8 %] | no concluyente |
| Casos revisados (25/147) | 17,0 % | [11,8 %; 23,9 %] | refutada |
| Error frente al consenso (28/138) | 20,3 % | [14,4 %; 27,8 %] | refutada |
| Error frente a la referencia original (53/200) | 26,5 % | [20,9 %; 33,0 %] | refutada |

Opciones:

| Opción | Estado que comunica el texto | Ventaja | Costo |
|---|---|---|---|
| **A. Refutada con el denominador de los casos revisados, informando ambos denominadores (recomendada)** | "Refutada" (25/147 = 17,0 % [11,8 %; 23,9 %]); 25/200 se reporta como dato secundario con la advertencia de que cuenta 53 casos sin oportunidad de revisión | Es la lectura (ii) del dictamen; usa la regla declarada sin cambiarla; coincide con las dos medidas de error | Cambia el estado de "no concluyente" a "refutada" en ~9 lugares y el grado del OE4 en la Tabla 18 |
| B. No contrastable en esta campaña | "No contrastable": la regla del reportante determinó qué casos se revisaban, y la variable no se midió en las condiciones que la hipótesis supone | Es la lectura (i) del dictamen; coherente con lo que el documento ya dice de la tasa bruta | Deja la sub-hipótesis sin estado medido; exige justificar por qué no se usa 25/147 |
| C. Ambos denominadores con veredicto por denominador | "No concluyente sobre 200; refutada sobre 147" | Máxima transparencia | El dictamen considera que "no concluyente" con 25/200 no se sostiene como conclusión; deja dos estados en el resumen |

**Recomendación: A.** En cualquier opción: 8.3 declara que la revisión alcanzó solo correo y
telefonía; 8.3 informa el cotejo con el consenso (11/85; 13 con consenso: 9/1/3) sin lectura
causal; 11.3 incorpora los dos requisitos de una medición válida (D8). La Tabla 18 ajusta las
filas del objetivo general y del OE4 al estado elegido (el grado del OE4 queda "alcanzado
parcialmente", acotado a tiempo y exactitud manual, si se elige A o B). El resumen nombra la
magnitud y el denominador sin superar 250 palabras.

Alternativa descartada: conservar "no concluyente" con 25/200 y una nota al pie. El dictamen
objeta el denominador; una nota no cambia el veredicto que el texto comunica.

### D2 — Enmascaramiento de los operadores (A2) — **decisión de los autores (tras D0)**

| Opción | Condición | Qué dice el texto |
|---|---|---|
| **A. Enmascaramiento parcial (recomendada si D0 confirma que los operadores de 2026-10 son los dos analistas originales)** | `T1` (autor) y `A1` (externo) operaron el brazo manual | 4.2 y 7.5: el propósito comparativo se ocultó, a lo sumo, al operador externo, y solo él lo conoció en el *debriefing*; `T1` lo conocía por ser autor. 4.8: la amenaza Hawthorne se agrava para la mitad del brazo manual (sesgo esperado: si el operador autor fue más rápido, la reducción de tiempo se subestima; si más lento, se sobrestima; se declara sin signo si no hay evidencia). 9.1 (explicaciones rivales): la misma condición. Se agrega el contraste de tiempos por operador de 2026-10 si ya figura en `numeros-canonicos.md`; no se calcula uno nuevo |
| B. Los operadores de 2026-10 no son los analistas | `registro_sujetos.csv` o el README muestran otras personas | Se corrigen 4.4, 4.8 y 9.3, que hoy afirman la coincidencia, y se conserva 4.2 |

La decisión la toman los autores con la evidencia de D0; el apply no elige por ellos. Sin datos
personales: solo códigos (`T1`, `A1`, `O1`, `O2`, `E1`, `E2`) y roles.

### D3 — Nota de la Tabla 19 (A3)

Texto verificable en una oración, sin agregar altura: "entre `cda7712` y `v1.2.12` no cambian
`requirements.txt`, `package-lock.json`, `n8n/workflow.json` ni `settings.py`; cambian
`docker-compose.yml` y `docker/n8n/` (imagen derivada) y 20 archivos del backend (control de
costo y TwiML, un script de reparación de codificación y pruebas; 7) y del frontend (13) que no
intervienen en la clasificación". La cifra (24 = 1 + 3 + 7 + 13)
se registra en `conteos-canonicos-tecnicos.md` con el comando exacto. La fila nueva del
modelo de transcripción (B1) se agrega a la misma tabla compactando celdas si hace falta.

### D4 — Canal telefónico y modelo de transcripción (B1)

- 5.2 (`05-arquitectura.tex:50`) y la etapa 4 de 6.6 (`06-implementacion.tex:74`) se
  reescriben según 6.4: Twilio graba la llamada y notifica la grabación al backend (callback),
  el backend la transcribe con la Gemini API (`gemini-3.5-transcribe`) y entrega el texto al
  flujo; "webhook de transcripción" → "callback de grabación".
- `gemini-3.5-transcribe` se declara en 6.4 (`06-implementacion.tex:50`), en una fila de la
  Tabla 19 (si el valor en `d6bb474` y en `cda7712` se verifica con `git show`; si no,
  "no registrado") y en el Anexo H; 9.5 declara que el costo de la transcripción queda
  excluido del cálculo económico (y por qué).
- Figura de despliegue: agregar en `docs/diagrams/despliegue.md` la arista backend → Gemini
  API rotulada "clasificación y transcripción", regenerar con el pipeline de c-188
  (`@mermaid-js/mermaid-cli@12.0.0`, `-b white -s 2`) y actualizar la leyenda
  (`05-arquitectura.tex:44`) a "redes Docker" con las cuatro redes que la figura dibuja.
  Relación alto/ancho no mayor que la previa en más de un 5 %.

### D5 — Procedencia de cifras y MDE (B2) — **decisión de los autores sobre el MDE**

- 8.3: declarar que el denominador de la proporción de tiempo usa los tiempos automatizados de
  la campaña complementaria (`corpus_campana.json`, 191 casos); y resolver el anacoluto en la
  misma reescritura (C1).
- 8.7: declarar que la salida en vivo telefónica proviene de `sector_predicho` del export de
  intervenciones (los sidecars telefónicos tienen sector nulo), que el McNemar usa la caché, y
  la definición del conjunto laxo del brazo manual (consenso + unión de los adicionales de E1 y
  E2).
- MDE del Spearman: leer en `evaluation/campana.py` qué `n` y qué fórmula produjeron 0,2834 en
  `analisis/resultados.json`. Opciones: **(a) corregir a 0,264 si el código con n = 110 da ese
  valor y 0,2834 resulta de otro `n` o de un error de transcripción (recomendada)**; (b)
  conservar 0,2834 y declarar el `n` y la fórmula que lo producen (por ejemplo, un MDE por
  operador). El valor elegido se registra en `numeros-canonicos.md` con su fuente; no se edita
  `analisis/resultados.json` (se declara la discrepancia si la hubiera).
- Balance laxo máximo (+138,0 con Δt = 43,8 frente a +138,1 con 43,82): unificar el Δt de la
  Tabla 16 con el que usa el texto y registrar el redondeo.

### D6 — Rótulos, matiz de 4.5 y formulaciones (B3, B4)

- "posterior a las corridas de la campaña" → "posterior a la campaña 2026-10" en 2.4, 5.5
  (`05-arquitectura.tex:68`), 6.3 (`06-implementacion.tex:40`) y 7.5
  (`11-aspectos-legales.tex:36`).
- `componentes.png` y `secuencia.png`: el rótulo está dentro de la imagen; se edita la fuente
  Mermaid de `docs/diagrams/` y se regeneran con el pipeline de D4. Se corrige en
  `dictamen-correcciones.md` la afirmación previa de que esos rótulos estaban solo en las
  leyendas.
- 4.5 (`04-marco-metodologico.tex:65`): la campaña complementaria corrió con `hybrid-v3` pero
  con la regla del reportante activa y con una salida en vivo que difiere de la caché en 13
  casos; "métricas comparables" se acota a las calculadas sobre la caché.
- 1.6 (`01-introduccion.tex:66`): "validación rigurosa … doble etiquetado independiente" →
  validación dentro de la muestra con doble etiquetado de acuerdo moderado y un analista autor.
- Resumen y abstract: "confirman" → "respaldan" / "confirm" → "support".
- Tabla 18, fila del OE1 (`09-conclusiones.tex:23`): "reintentos idempotentes de la
  configuración entregada".

### D7 — Presupuesto de páginas — **decisión de los autores**

El PDF tiene 118 páginas frente al tope total de 100. Opciones: **(a) sostener el exceso
declarado (+18) con una nueva entrada fechada en el libro mayor y la neutralidad de páginas de
este change (≤ 118) (recomendada; es lo que el requisito vigente admite)**; (b) intentar una
reducción hacia 100 sin eliminar contenido científico (otro change, por su alcance); (c)
renegociar el tope con la cátedra y registrarlo. El change no agrega páginas netas en ningún
caso.

### D8 — Línea futura de 11.3

`subsec:medicion-intervencion` agrega dos requisitos de una medición válida: que la revisión
alcance a todos los canales (o a una muestra aleatoria de cada uno), para que el denominador
sea el de los casos revisables, y que cada validación se coteje con una referencia
independiente, para medir cuántas veces la revisión acierta y no solo cuántas cambia.

### D9 — Bibliografía y residuos (C2 y otros) — decisiones parciales de los autores

- **Zanzotto (2.4)**: reformular como inferencia de los autores apoyada en el paradigma *HitAI*
  (recomendado), o citar la página exacta si los autores acceden al texto completo y la
  afirmación figura.
- **Xiong et al. (2.5, 9.2)**: "discrimina poco" → "predecir las fallas sigue siendo un
  desafío"; conservar sobreconfianza y concentración en la parte alta.
- **Galup (2.1, `02-marco-teorico.tex:12`)**: punto único de contacto con `OGC2011_itil`.
- **Precios (9.5, `08-discusion.tex:66`)**: entrada nueva para la página de precios de la
  Gemini API (verificada, con `urldate`); `Google2026_vertex_pricing` se retira si queda sin
  uso.
- **Nivel de servicio de la Gemini API (7)** — **decisión de los autores (dato que solo ellos
  conocen)**: declarar si el sistema operó en el nivel gratuito o en el pago durante las
  campañas y la consecuencia sobre el uso de los datos transferidos según la página citada.
  Si fue gratuito, 7 y 9.6 declaran que los datos pseudonimizados pudieron usarse para mejorar
  los productos del proveedor. El apply se detiene en esa oración hasta tener el dato.
- **URL**: Zendesk (ficha de Zendesk Suite), Vertex (retirada o actualizada), Decreto 1558/2001
  (argentina.gob.ar).
- **Ramya et al.**: versión IEEE CSITSS 2018, pp. 221-227, con DOI verificado en Crossref.
- **Kerby (2014)**: localizador 3:11.IT.3.1.
- **Efron y Tibshirani**: año y DOI de la misma edición (verificar en Crossref).
- **FrugalGPT**: confirmar la publicación en TMLR (OpenReview); si no se confirma, citar el
  preprint de arXiv.
- **ISBN**: no se agregan (APA 7 no los exige); se registra la decisión.
- **Repositorios regionales (SciELO, Redalyc, JAIIO)**: no se hacen búsquedas nuevas; se
  declara la ausencia como limitación del protocolo de revisión en el estado del arte (una
  oración) o se registra como residuo aceptado. **Decisión de los autores**; recomendada la
  oración.
- **`main.log` no versionado**: lo cubre `compilacion.md` (c-188); el Anexo B lo nombra (C1).

### D10 — Glosario (C1) — decisión menor

Agregar TI, URL, E2E, MDE, VIS, HS256, CA y las abreviaturas NB, LR y DT de la Tabla 1, o
desarrollar en el primer uso las que aparecen una sola vez (recomendado para VIS, HS256 y CA,
para no alargar el glosario). TI frente a IT: unificar el término del cuerpo con el del
glosario o agregar ambas. Cada sigla del glosario debe tener uso (requisito de c-188).

### D11 — Consentimiento de los sujetos de la campaña complementaria (inventario 25)

7 (`11-aspectos-legales.tex:34`) describe cómo se informó y consintió a E1, E2, O1 y O2. El
procedimiento lo aportan los autores (o `docs/campana-medicion/` si lo registra); el texto no
inventa un procedimiento. Si no hay registro, se declara así.

### D12 — Registro, Anexo I y release

- `dictamen-correcciones.md`: sección "Dictamen v10 / v1.2.12 (2026-11-09) - c-190" con la
  matriz de 7 columnas (Rec | Síntesis | Change | Archivo:línea | Ancla | Fragmento verificable
  | Estado) con una fila por recomendación e ítem del inventario; decisiones D1, D2, D5, D7, D9
  y D10; libro mayor de páginas. `verificar_matriz_trazabilidad.py` en 0 fallas.
- `12-anexos.tex`, `sec:anexo-trazabilidad`: cuarta tabla `tab:anexo-trazabilidad-0911` (Rec.
  | Change | Secciones) con A1-A3, B1-B4 y C1-C2; la frase de cabecera pasa a siete dictámenes
  hasta el 9 de noviembre de 2026.
- Release `v1.2.13` con el patrón D7-A de c-187: commit de contenido (que versiona además
  `auditorias/Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`, como `a42f005` versionó el del
  8-11) con tag anotado, y commit siguiente que consigna el hash completo en el Anexo B; `git
  diff --stat v1.2.13 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` muestra una línea.

## Risks / Trade-offs

- [D1-A cambia el estado de una sub-hipótesis y el grado del OE4] → se propaga con un
  `rg` de verificación que exige el mismo estado en los nueve lugares; la Tabla 18 explica el
  denominador en una línea.
- [D0 no reproduce una cifra del dictamen] → el apply se detiene en esa recomendación y se
  consulta; el texto usa solo cifras reproducidas.
- [El resumen supera 250 palabras al nombrar el denominador] → compensar en el mismo resumen;
  medir con el método de c-169 y registrar.
- [Regenerar tres PNG cambia su tamaño y agrega páginas] → mismo pipeline y escala que c-188;
  control de relación alto/ancho; libro mayor de páginas.
- [El nivel de servicio de la Gemini API fue gratuito] → la consecuencia sobre los datos se
  declara en 7 y 9.6; puede requerir matizar afirmaciones de 7 sobre transferencias. Se
  revisa en el apply con los autores.
- [Fuentes externas no verificables (FrugalGPT, Zanzotto completo)] → se registran como no
  verificadas y se usa la formulación prudente.
- [Gitleaks marca prosa con "capitulo" seguido de coma y nombre de archivo] → en el registro y
  en el Anexo I se usa "sección N (`archivo.tex`)".

## Migration Plan

Apply en el orden de `tasks.md`; compilación en el entorno de registro (Docker
`texlive-thesis`, `MSYS_NO_PATHCONV=1`), `verify_citations.py`, verificador de la matriz y
`openspec validate --strict`. Release (orquestador): rama `change/c-190-dictamen-coneau-v1-2-12`,
commit de contenido con el dictamen versionado, tag `v1.2.13`, commit del hash, `engram sync
--project`, PR contra `main`. Rollback: revertir las fuentes, figuras y memos al commit previo;
no hay datos ni código que revertir.

## Open Questions

- **D1**: opción A (recomendada), B o C para el estado de la sub-hipótesis 2. Bloquea el grupo 2.
- **D2**: opción A o B según lo que muestre `registro_sujetos.csv`. Bloquea el grupo 3.
- **D5**: MDE corregido a 0,264 (recomendado) o justificado.
- **D7**: sostener el exceso de páginas (recomendado), reducir o renegociar.
- **D9**: nivel de servicio de la Gemini API (gratuito o pago) durante las campañas: dato de
  los autores, bloquea la oración de 7. Zanzotto: reformular o paginar. Repositorios
  regionales: oración de limitación o residuo aceptado.
- **D11**: cómo se informó y consintió a E1, E2, O1 y O2.
