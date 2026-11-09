# Design: Atender el dictamen CONEAU sobre v1.2.13

## Context

Ver `proposal.md` para la motivacion. Este change es de documento: corrige cuatro
observaciones, el item 12 y residuales del dictamen del 2026-11-09 sobre la release
`v1.2.13`. El archivo del dictamen todavia no esta en `auditorias/`; se referencia por su
titulo (`Dictamen v10 / v1.2.13 (2026-11-09)`) y su versionado queda como tarea no bloqueante.
No cambia datos, codigo ni artefactos de `evaluation/`.

**Numeracion.** Igual que en c-187/c-190: 4.x = `04-marco-metodologico.tex`, 5.x =
`05-arquitectura.tex`, 6.x = `06-implementacion.tex`, 7 = `11-aspectos-legales.tex`, 8.x =
`07-resultados.tex`, 9.x = `08-discusion.tex`, 10 = `09-conclusiones.tex`, 11.x =
`10-recomendaciones.tex`, Anexos = `12-anexos.tex`. "8.3" es `subsec:reduccion-intervencion`;
"8.7" es `subsec:resultados-campana-medicion`. El item 12 remite al inventario del dictamen
anterior (v1.2.12, c-190). Las anclas se localizan por el texto citado con `rg -n`.

**Estado de partida verificado al proponer** (solo lectura):

- 8.7 (`07-resultados.tex:253`) declara `rho = 0,2834` con la formula que multiplica por la
  ARE de Wilcoxon (`sqrt(107 * 0,864)`); `numeros-canonicos.md` reproduce el mismo valor
  (fila del MDE de posicion, seccion 3.16).
- 8.3 (`07-resultados.tex:154`) declara "25 de los 147 casos revisados (17,0 %; IC [11,8 %;
  23,9 %]), con 122 confirmaciones (61,0 %)" y "refutada" como veredicto.
- Tabla 18 OE4 (`09-conclusiones.tex:26`) declara "intervencion humana refutada sobre los
  casos revisados (25 de 147), sin medicion valida por la regla del reportante": se
  contradice.
- 1.6 (`01-introduccion.tex:66`) menciona "un doble etiquetado de acuerdo moderado a cargo de
  un analista externo y de un analista que es autor del trabajo" sin separar los dos pares.
- 8.7 (`07-resultados.tex:251`) define el conjunto laxo manual con la "union de los sectores
  adicionales de ambos etiquetadores".
- `evaluation/campana.py::construir_referencia` usa la interseccion
  (`_adicionales(reg_1) & _adicionales(reg_2)`, linea ~274).
- 6.3 (`06-implementacion.tex:37`) dice "telefonia (trigger de Twilio)"; 6.4 usa "callback de
  grabacion".
- Anexo B (`12-anexos.tex:46`) imprime hoy `f527722...` (hash del commit de contenido de
  v1.2.13); el PDF etiquetado de v1.2.13 se compilo con el hash de v1.2.12 (`7937efd`).

## Goals / Non-Goals

**Goals:**

- Que el PDF etiquetado de `v1.2.14` no imprima el hash de una release previa (D1).
- Que el MDE del Spearman coincida con la formula documentada sin la ARE de Wilcoxon (D2).
- Que el veredicto de la segunda sub-hipotesis y su matiz sean coherentes en 8.3 y en la
  Tabla 18, con los denominadores explicitos (D3).
- Que la atribucion del kappa separe el par `E1`/`E2` del par autor/analista (D4).
- Que el conjunto laxo manual se describa como lo calcula el codigo (D5).
- Que cada residual del dictamen quede cerrado o declarado (D6).
- Trazabilidad del dictamen en el registro y el Anexo I, y release `v1.2.14` (D7, D8).

**Non-Goals:**

- Nivel pago, consentimiento de los cuatro participantes, secciones 7 y 11 por esos motivos
  (van a `v1.2.15`).
- Mediciones, corridas del clasificador, figuras o datos de campana.
- Reduccion del PDF al tope de 100 paginas (D6).

## Decisions

### D0 — Verificacion previa antes de reescribir (bloqueante, solo lectura)

Script descartable en el scratchpad, sin escribir en el repo, que reproduzca desde
`evaluation/data/` y el codigo:

1. MDE del Spearman: `tanh((z_{0,975} + z_{0,80}) / sqrt(107 * 0,912)) = 0,276` (frente a
   0,2834). Confirmar que 0,2834 surge de usar `ARE = 0,864` (Wilcoxon); el valor correcto
   usa la eficiencia de Spearman frente a Pearson bajo normalidad, `9/pi^2 ≈ 0,912`.
2. Denominadores del 122: 122/200 = 61,0 % y 122/147 = 83,0 %. Wilson de 25/147 =
   [11,79 %; 23,90 %]; prueba binomial de 25 exitos en 147 con p = 0,15.
3. `construir_referencia`: la interseccion de adicionales da 130/151 laxa manual; la union
   daria 137 (recomputo sobre `doble_etiquetado.csv`).
4. Kappa: 0,5569 es el par `E1`/`E2` (`p_o = 0,69`; `p_e = 0,30`); el par autor/analista tiene
   0,87 sin intervalo.
5. Anexo B: `git show v1.2.13:"docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"` y el
   `pdftotext` del PDF etiquetado no deben contener el hash de la release propia; hoy imprimen
   el de v1.2.12.

**Si una cifra no se reproduce, el apply se detiene en esa recomendacion y se consulta a los
autores**; el texto nunca adopta una cifra del dictamen sin reproducirla.

### D1 — Regla de hash de release en el Anexo B (critica)

Problema: el commit de contenido mantiene el hash de la release previa en el Anexo B y el
commit del hash lo reemplaza despues; como el tag apunta al commit de contenido, el PDF
etiquetado imprime el hash de la release ANTERIOR.

Regla (patron c-188): el commit de contenido SHALL llevar una oracion de reemplazo en lugar
del hash, del estilo "El PDF compilado en el propio tag no imprime ese hash: el hash completo
de la release v1.2.14 se consigna en el commit que sigue al tag en la rama principal, y los
commits posteriores no modifican las fuentes de la tesis." El commit posterior al tag
reemplaza esa oracion por el hash completo del commit de contenido. El Anexo B SHALL explicar
el mecanismo (un commit no puede contener su propio hash) sin imprimir ningun hash de una
release previa.

Verificacion: `git diff --stat v1.2.14 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` muestra
una sola linea (la del hash), y el `pdftotext` del PDF etiquetado `v1.2.14` no contiene
`7937efd` ni `f527722`.

Esta decision se codifica como requisito del spec (regla permanente del proceso de release),
no solo como tarea de la release actual.

### D2 — MDE del Spearman (item 12)

La formula vigente ajusta el denominador por la eficiencia relativa asintotica de Wilcoxon
(`ARE = 0,864`), que corresponde a la prueba de rangos con signo de Wilcoxon, no a la
correlacion de rangos de Spearman. Correccion:

`rho_MDE = tanh((z_{0,975} + z_{0,80}) / sqrt((n - 3) * 0,912)) = tanh((1,95996 + 0,84162) / sqrt(107 * 0,912)) = 0,276`.

- 8.7 (`07-resultados.tex:253`): reemplazar 0,2834 por 0,276 y la formula
  `sqrt(107 * 0,864)` por `sqrt(107 * 0,912)`, reemplazando la ARE de Wilcoxon por la
  eficiencia de Spearman (`9/pi^2 ≈ 0,912`).
- `numeros-canonicos.md` (3.16, fila del MDE de posicion): actualizar el valor y anotar la
  fuente y la correccion (el valor previo usaba la ARE de Wilcoxon).
- Registro del dictamen: fila con el valor anterior, el nuevo y la justificacion.
- No se edita `analisis/resultados.json`; si alli figura 0,2834, se declara la discrepancia
  (el JSON conserva el valor historico; la tesis publica el corregido).

### D3 — Segunda sub-hipotesis: veredicto, matiz y denominadores

Veredicto segun la regla de tres vias declarada: estimacion 17,0 % >= 0,15 -> "refutada". Se
conserva, con el matiz explicito (requisito de honestidad estadistica): el IC de Wilson de
25/147 es [11,8 %; 23,9 %], que contiene 0,15, y la prueba binomial (25 exitos en 147 con
p = 0,15) da p = 0,28; por tanto la evidencia es compatible con un valor cercano al umbral y la
lectura conservadora es "no se puede descartar 0,15".

Correcciones puntuales:

- 8.3 (`07-resultados.tex:154`): el "122 (61,0 %)" es 122/200; son 83,0 % de los 147 revisados.
  Reescribir con ambos denominadores explicitos (p. ej. "122 de los 147 casos revisados
  (83,0 %), sobre 200 casos 122 (61,0 %)") sin cambiar las cifras.
- Tabla 18, OE4 (`09-conclusiones.tex:26`): retirar la contradiccion ("refutada ... sin
  medicion valida por la regla del reportante") y alinear la celda con el veredicto y el
  matiz; la fila del objetivo general y la del OE4 ya declaran el denominador revisado
  (25 de 147).
- Propagacion del matiz solo donde se enuncia el veredicto: 8.3 y, opcionalmente, 9.1. El
  resumen y el abstract MUST NOT superar 250 palabras: si el matiz se incluye alli, se
  compensa en el mismo resumen.

Alternativa descartada: cambiar el veredicto a "no concluyente". La regla declarada da
"refutada" con el punto estimado; el matiz informa la incertidumbre sin contradecir la regla.

### D4 — Atribucion del kappa en 1.6

1.6 (`01-introduccion.tex:66`) atribuye el "acuerdo moderado" al par analista externo +
analista autor. El 0,5569 (moderado) es el doble etiquetado `E1`/`E2`; el par autor/analista
tiene acuerdo 0,87 sin intervalo. Reescribir 1.6 para separar ambos pares: la validacion
dentro de la muestra tiene dos componentes de fiabilidad distintos, y cada kappa se atribuye
a su par. Sin datos personales: solo codigos y roles. Revisar coherencia con 4.4, 8.7 y 9.3.

### D5 — Conjunto laxo del brazo manual

8.7 (`07-resultados.tex:251`) define el conjunto laxo como "consenso de E1 y E2 mas la union
de los sectores adicionales de ambos etiquetadores". El codigo usa la interseccion
(`construir_referencia`). Corregir "union" por "interseccion" y confirmar que la cifra
publicada (130/151) corresponde a la interseccion; la union daria 137. No se modifica la
cifra, solo la descripcion del criterio.

### D6 — Residuales menores

- **6.3 (`06-implementacion.tex:37`)**: "telefonia (trigger de Twilio)" -> "telefonia
  (callback de grabacion de Twilio)", alineado con 6.4 y con el canal telefonico real.
- **Xiong (`03-estado-del-arte.tex:62`)**: "poca capacidad para separar aciertos de errores"
  -> "predecir las fallas sigue siendo un desafio", como en 2.5 y 9.2; se conservan
  sobreconfianza y concentracion en la parte alta.
- **VIS**: no esta desarrollada en el cuerpo. Desarrollarla en su primer uso (7,
  `07-resultados.tex:154`, "regla de visibilidad y derivacion por reportante no identificado
  (VIS-005)") o agregarla al glosario. Cada entrada del glosario SHALL tener uso en el cuerpo
  (requisito de c-188).
- **FrugalGPT**: el dictamen no pudo confirmar la publicacion en TMLR. Conservar la entrada
  TMLR con la URL de OpenReview (`cSimKw5p6R`) como evidencia, o agregar el preprint de arXiv
  (`2305.05176`) como nota de respaldo. Registrar la decision; no inventar venue.
- **Paginas**: el exceso de 118 paginas sobre el tope de 100 ya esta declarado en el libro
  mayor. Registrar que sigue siendo un residual declarado; no se intenta reduccion en este
  change. El PDF del tag `v1.2.14` MUST NOT superar 118 paginas.

### D7 — Registro, Anexo I y verificadores

- `dictamen-correcciones.md`: seccion "Dictamen v10 / v1.2.13 (2026-11-09) - c-192" con la
  matriz de 7 columnas (Rec | Sintesis | Change | Archivo:linea | Ancla | Fragmento
  verificable | Estado), una fila por observacion (1-4), el item 12 y cada residual; las
  decisiones de este design; y el libro mayor de paginas y palabras.
- Anexo I (`sec:anexo-trazabilidad`): tabla de trazabilidad del dictamen del 9-11 sobre
  v1.2.13 (o actualizacion de la existente) con las secciones tocadas y `\autoref`; sin
  numeros de linea.
- `verificar_matriz_trazabilidad.py` -> 0 fallas sobre el arbol y sobre el tag de la release.
- `tesis_para_agente.md` regenerado.

### D8 — Versionado del dictamen y release `v1.2.14` (no bloqueante el archivo)

- El archivo `auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md` no esta en el repo:
  la tarea de versionarlo queda abierta y NO bloquea la release. Cuando Gonzalo lo entregue,
  se agrega con `git add` y, si la release ya cerro, en un commit posterior.
- Release `v1.2.14` con la regla D1: commit de contenido (con la oracion de reemplazo en el
  Anexo B) + tag anotado `v1.2.14` + commit del hash que reemplaza la oracion. Verificar con
  `git diff --stat v1.2.14 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` (una linea) y con
  `pdftotext` del PDF etiquetado (sin `7937efd`/`f527722`).

## Risks / Trade-offs

- [El matiz del intervalo debilita la lectura "refutada"] -> se conserva el veredicto segun la
  regla declarada; el matiz explicita la incertidumbre sin cambiar la regla, como pide el
  dictamen.
- [El Anexo B queda con una oracion de reemplazo poco elegante en el PDF etiquetado] -> es el
  precio de no imprimir un hash ajeno; la oracion es explicita y verificable (D1).
- [Cambiar el MDE puede no ser lo que produjo el JSON] -> D0 reproduce 0,276 con la formula
  documentada; si no coincide, se detiene y se consulta. No se edita el JSON.
- [FrugalGPT sin confirmacion de TMLR] -> se conserva la URL de OpenReview como evidencia o se
  agrega el preprint de arXiv; se registra la decision, sin inventar venue.
- [El resumen supera 250 palabras al agregar el matiz] -> se incluye el matiz solo si entra;
  compensar en el mismo resumen y medir con la regla registrada.
- [Gitleaks marca prosa con "capitulo" seguido de coma y nombre de archivo] -> en el registro y
  el Anexo I se usa "seccion N (`archivo.tex`)".
- [El dictamen no versionado antes del tag] -> la tarea de versionado es no bloqueante y queda
  declarada como residual operativo (D8).

## Migration Plan

Apply en el orden de `tasks.md`; compilacion en el entorno de registro (Docker
`texlive-thesis`, `MSYS_NO_PATHCONV=1`), `verify_citations.py`, verificador de la matriz y
`openspec validate --strict`. Release (orquestador): rama
`change/c-192-atender-el-dictamen-v1-2-13`, commit de contenido con la oracion de reemplazo en
el Anexo B, tag `v1.2.14`, commit del hash, `engram sync --project`, PR contra `main`.
Rollback: revertir las fuentes y memos al commit previo; no hay datos ni codigo que revertir.

## Open Questions

- D2: confirmar con D0 que el MDE correcto es 0,276 (formula sin ARE). Si el JSON conserva
  0,2834 por otro `n`, se declara la discrepancia.
- D3: incluir o no el matiz en el resumen/abstract (compensando palabras). Recomendado
  mantenerlo en 8.3 y 9.1, fuera del resumen.
- D6/FrugalGPT: conservar TMLR con OpenReview o agregar arXiv `2305.05176` como respaldo.
- D6/VIS: desarrollar en el primer uso o agregar al glosario. Recomendado el primer uso.
- D8: fecha de entrega del archivo del dictamen por Gonzalo (no bloquea la release).
