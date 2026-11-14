## Context

Hechos verificados en el repositorio (2026-11-13):

- **`c-215` está completa y sin fusionar.** Vive en `origin/change/c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia` (commit de punta `4bfd4d4`), no está archivada y `main` no tiene `evaluation/brazo_gemini_solo.py` ni el análisis `analisis_brazo_gemini_solo_c215.*`. Su `merge-base` con `main` es `524124a` (cierre de c-214), así que **no** incluye c-206/c-208 ni el retargeteo de c-213 a la referencia arbitrada.
- **`main` hoy usa la referencia arbitrada de 206** (c-206) para la validación fuera de muestra: exactitud estricta del híbrido `142/206 = 0,6893`; el memo termina en la sección `3.26` (c-213 + c-206, n = 206). El bloque de 103 casos con consenso `E3`/`E4` (`0,8447`) se conserva como «etapa previa y cota de sensibilidad».
- **El contraste de c-215 es sobre los 103 de consenso** (bloque primario) y los 200 dentro de la muestra (secundario). Veredicto prerregistrado del bloque primario: **no concluyente**. Cifras del caché versionado: H `87/103 = 0,8447`; L `90/103 = 0,8738`; McNemar `p = 0,5078`; Δ `H−L = −0,0291` `[−0,0874; 0,0291]`; llamadas H/L `0,3301` `[0,2427; 0,4175]`; costo H/L `0,3295` `[0,2421; 0,4176]`; fallos `0/103`. Corrida paga ya hecha (303 llamadas con respuesta); el caché se versiona en la rama.
- **La prosa de c-215 ya está escrita** para `01`, `04`, `07`, `08`, `09` y `10`, pero sobre el texto previo a c-206/c-213. Varios de esos pasajes hoy dicen «no se contrastó» en `main` y otros ya fueron reescritos con la referencia de 206, de modo que el merge tendrá conflictos.
- **El memo colisiona**: c-215 agregó su sección como `3.25`; `main` ya usa `3.25` (c-206), `3.26` (c-213) y `3.27` (c-216). La sección nueva debe ser `3.28`.
- **`c-216`** («robustecer la referencia, el gate y la forma») es dueño de los ítems L2-L5 (referencia, gate y forma). Este change NO los toca.

## Goals / Non-Goals

**Goals:**

- Dejar en `main` el código y las salidas de c-215 sin re-correr el brazo (costo cero) y sin tocar el clasificador, el corpus ni la referencia.
- Resolver la deriva de referencia de forma explícita y honesta, con una decisión justificada y con su costo declarado.
- Llevar la prosa de la tesis al veredicto honesto (ahorro medido, exactitud indeterminada) en `01/04/07/08/09/10`, sin contradicciones internas.
- Registrar las cifras de forma aditiva (`numeros-canonicos.md` sección `3.28`) y documentar la decisión en `dictamen-correcciones.md`.

**Non-Goals:**

- Repetir la corrida paga del brazo sobre la referencia arbitrada de 206 (ver D1; requiere autorización y gasto).
- Tocar L2-L5: la robustez de la referencia, el gate de confianza y la forma (change `c-216`).
- Cambiar el clasificador de producción, el corpus, los precios, el gate, ni ningún valor canónico de las secciones `3.1`-`3.26`.
- Recompilar el PDF (queda como tarea del dueño, como en c-215).

## Decisions

### D1 — Deriva de referencia: la de 103 es la etapa previa preregistrada; la de 206 es el complemento de exactitud

**Elegido: opción (b).** El contraste de eficiencia se presenta sobre el **bloque de 103 casos con consenso `E3`/`E4`** (etapa previa y prerregistrada) y la **referencia arbitrada de 206** se presenta, por separado, como el complemento de exactitud fuera de muestra que la tesis ya reporta (c-206/c-213).

Justificación:

1. **El preregistro se fijó sobre 103.** El margen `δ = 0,05`, el tope de llamadas y la regla de tres vías se congelaron en el commit de la propuesta de c-215, antes de cualquier dato del brazo, con la referencia de 103 como primaria. Re-expresar el contraste sobre 206 rompería ese preregistro y exigiría uno nuevo (la referencia de 206 no existía al prerregistrar; la arbitró c-206 después).
2. **El bloque de 103 es un subconjunto limpio de la de 206.** La referencia arbitrada coincide con el consenso `E3`/`E4` en esos 103 casos; solo cambia los 47 discordantes y agrega 56 de refuerzo. Presentar el contraste sobre 103 no introduce un sesgo distinto del que la tesis ya declara.
3. **Costo cero y aditivo.** No se emite ninguna llamada nueva; no se toca la referencia ni ningún valor canónico. La prosa declara la relación de referencias (103 previa / 206 complemento) para que un tribunal no lea las dos estimaciones como una sola.
4. **Coherencia con `main`.** `main` ya conserva los 103 como «etapa previa y cota de sensibilidad»; el contraste de eficiencia sobre 103 encaja en esa lectura sin reescribir el capítulo de resultados.

**Alternativa rechazada (a): re-expresar el contraste sobre la referencia arbitrada de 206.** Requeriría una corrida paga nueva del brazo «Gemini solo» sobre los ~103 casos de la de 206 que no están en el caché de c-215 (los 47 discordantes arbitrados más los 56 de refuerzo; los 103 de consenso ya están cacheados). Costo: ~103 llamadas mínimas, ~136 con el margen de reintento (~32 %), hasta ~209 en el peor caso, del orden de **USD 0,07–0,15 a precio introductorio** (hasta ~USD 0,28 a precio estándar) según la tasa de dry-run de `design.md` de c-215 (`0,0007125 USD/llamada`). Exigiría `GEMINI_API_KEY` y **autorización explícita de gasto** (gobernanza MEDIUM) y un preregistro nuevo. Se difiere como trabajo futuro; el change no la ejecuta.

### D2 — Mecanismo de integración

Crear una rama desde `main` e integrar el contenido de c-215 con `git merge origin/change/c-215-…` (nunca squash ni rebase), resolviendo los conflictos a mano. Los conflictos esperados son: `numeros-canonicos.md` (ambas ramas agregaron `3.25`), `dictamen-correcciones.md`, `CHANGES.md` (c-215 agregó FASE 71; lo reconcilia el orquestador, fuera del alcance de edición de este change) y los pasajes de `08-discusion.tex`/`09-conclusiones.tex` que c-206/c-213 ya reescribieron. La resolución NO revierte el texto de `main`; re-aplica la intención de c-215 sobre el texto vigente.

### D3 — Anclas de la prosa en `main` actual

- `04-marco-metodologico.tex`: insertar el `\paragraph{Brazo de modelo de lenguaje solo.}` tras el párrafo de calibración del gate (`subsec:metricas-instrumentos`).
- `07-resultados.tex`: insertar el párrafo del contraste + `tab:gemini-solo` + el párrafo de eficiencia + el de bloque secundario/deriva/desviación después del contraste pareado frente a la línea de base (que hoy es sobre 206).
- `08-discusion.tex`: reemplazar «no se contrastó»/«sigue sin contrastarse» por el contraste con resultado no concluyente en los tres pasajes (interpretación, cascadas, alternativas).
- `09-conclusiones.tex`: reemplazar «Las dos hipótesis subsidiarias no se contrastaron» y los dos pasajes de estrategia compositiva/alcance por el estado «contrastada: no concluyente».
- `01-introduccion.tex` y `10-recomendaciones.tex`: incluidos aunque no estaban en la lista corta del pedido, porque c-215 los modifica y porque dejar «Ninguna de las dos se somete a un contraste formal» (criterio 1) contradiría el resultado; se marcan como requeridos para la coherencia.

### D4 — Numeración del memo

La sección nueva del memo es la `3.28` (después de la `3.27` de c-216 y de la `3.26` vigente). Es aditiva: no se renumera nada y las frases previas que declaran la eficiencia «sin contrastar» se declaran superadas por remisión, sin borrar contenido.

### D5 — Gobernanza y costo

MEDIUM: prosa y análisis; sin cambio de conducta productiva, de configuración ni de referencia. Costo **cero**: la corrida paga ya se hizo en c-215 y su caché se versiona. Ningún agente emite llamadas.

## Risks / Trade-offs

- [Conflicto de merge que revierta texto de `main`] → revisar cada conflicto contra el texto vigente de `main`; la resolución re-aplica la intención, no el archivo viejo.
- [Deriva entre la predicción de H del caché de c-215 (consenso, 2026-11-12) y la de `predicciones_arbitrado.json` (2026-11-13) sobre los 103 compartidos] → verificar la coincidencia en los 103 casos; si difiere, declararlo como limitación en el memo y en la prosa, sin recalcular el veredicto.
- [Que el lector lea las dos referencias (103 y 206) como una sola] → requisito explícito de declarar la relación y no agrupar (delta `tesis-document`).
- [Colisión con `c-216` en `tesis-dictamen-v1-3-0`] → el delta modifica solo el requisito del ahorro/eficiencia; si c-216 toca el mismo requisito, reconciliar al integrar y re-validar.
- [Sobreventa del ahorro] → el requisito prohíbe afirmar no inferioridad de exactitud y exige el veredicto «no concluyente» junto al ahorro.
- [Sección `3.25` duplicada] → usar `3.28` y verificar que la `3.26` y la `3.27` sigan intactas.

## Migration Plan

1. Rama desde `main`; `git merge` de la rama de c-215; resolver conflictos (D2).
2. Re-aplicar la prosa sobre el texto vigente (D3) y ajustar la numeración del memo (D4).
3. `openspec validate … --strict`; pruebas de `evaluation/` (subconjunto offline) para el código fusionado.
4. Rollback: `git merge --abort` antes de commitear; después, revertir el merge commit. El código y el caché de c-215 siguen disponibles en su rama.

## Open Questions

- ¿Se ejecutará la opción (a) como change de seguimiento? Queda diferida y sujeta a autorización de gasto; no cambia el alcance de este change.
- La recompilación del PDF y el ajuste de paginación de `tab:gemini-solo` los decide el dueño (como en c-215); no cambian las specs ni las tareas.