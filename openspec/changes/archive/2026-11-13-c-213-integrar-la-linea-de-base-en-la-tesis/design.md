## Context

> **Alcance actualizado tras rebasar sobre `main` (9d348c4).** c-210 integró en `main` el texto de la línea de base (`tab:linea-base-clasica` en `07`, reescrituras en `08`, `09`, `10`, sección 3.22 del memo). D1, D2, D3, D4, D6 y la parte del contraste de D5 y D7 siguen vigentes. Lo que D5 y D7 asignaban a la subsección `subsec:linea-de-base`, a `tab:linea-de-base`, a la reescritura de `08`/`09`/`10` y a la sección 3.22 queda **cubierto por c-210** y no se duplica: c-213 agrega el párrafo de contraste pareado en `07` tras `tab:linea-base-clasica`, una cláusula en `08` y otra en `09`, el párrafo de método en `04`, la sección 3.23 y FASE 69. La numeración de cifras y pasajes de abajo describe el estado previo a c-210.

c-209 implementó `evaluation/linea_de_base.py` (unión de TF-IDF de palabras `(1,2)` y de caracteres `(2,5)` + `LogisticRegression(solver="lbfgs", max_iter=2000, random_state=42)`, variantes `class_weight="balanced"` y `None`) y c-210 la midió: artefacto `evaluation/data/campana/analisis/linea_de_base_clasica_c210.json` (SHA-256 `2866dc1c…`), con borrador para la tesis en `openspec/changes/c-210-medicion-de-la-linea-de-base/borrador_07-resultados_linea_de_base.md`.

Cifras versionadas (n = 103, consenso `E3`/`E4`, 47 discordantes excluidos):

| Sistema | Estricta | Laxa | Macro-F1 | Balanced acc. | Fuente |
|---|---|---|---|---|---|
| Línea de base balanceada | 0,6505 (67/103) | 0,6699 (69/103) | 0,4877 | 0,5271 | `linea_de_base_clasica_c210.json` → `variantes.balanceada.lectura_muestral.metricas` |
| Línea de base sin re-ponderación | 0,5825 (60/103) | 0,6019 (62/103) | 0,3431 | 0,3838 | ídem, `variantes.sin_repoderacion` |
| Híbrido `hybrid-v3` | 0,8447 (87/103), Wilson [0,7625; 0,9021] | 0,8738 (90/103) | 0,7447 | 0,7395 | `analisis_fuera_de_muestra_c205.json` (copiado en `comparacion_hibrido` del JSON de c-210) |

F1 por clase de la línea de base balanceada: Seguridad 0,5532; Hardware 0,8049; Software 0,7170; Bases de Datos 0,0000; Sistemas 0,3636 (soportes 21/40/24/13/5).

Estado de la evidencia pareada (verificado en la exploración):
- Ningún artefacto versionado contiene un contraste pareado línea de base frente a híbrido (ni McNemar ni IC de la diferencia).
- Las predicciones por caso del híbrido SÍ están versionadas: `evaluation/data/campana/predicciones_independiente.json` (103 entradas, `caso_id`, `sector_asignado`, `sector_predicho`, `etapa`).
- Las predicciones por caso de la línea de base NO están versionadas; el JSON de c-210 solo guarda métricas agregadas. Son reconstruibles de forma determinista con `evaluation.linea_de_base.predecir` (semilla 42): una reconstrucción exploratoria (no versionada, no citable) reproduce los 67/103 y los 87/103 de los artefactos.
- `evaluation/stats.py::contraste_mcnemar` (c-131) ya existe y devuelve `p_exacto`, `p_corregido` y `p_primario` (exacto si `b + c < 25`).
- La tesis ya usa McNemar exacta bilateral (`08-discusion.tex:10`, reglas frente a Gemini, p = 0,1516) y cita `McNemar1947_sampling_error`, `Efron1993_bootstrap`, `Wilson1927_probable_inference` y `Pedregosa2011_scikit_learn`, todas en `Bibliography_base.bib`.

Pasajes de la tesis que hoy contradicen el repositorio (líneas en `docs/Tesis/v10 (IA)/paper/sections/`):
- `08-discusion.tex:56` (limitación quinta): "la comparación se hizo solo contra el flujo manual, no contra clasificadores alternativos como TF-IDF+SVM o regresión logística…"; cierra con "Una comparación sistemática contra clasificadores supervisados … queda como trabajo futuro".
- `09-conclusiones.tex:47`: "No se realizó una comparación directa contra clasificadores supervisados entrenados sobre el mismo corpus…".
- `10-recomendaciones.tex:14`: "Esta línea responde a la limitación medida de la ausencia de una línea de base: no se comparó el esquema híbrido contra un clasificador supervisado…".
- Contexto a mantener coherente: `08-discusion.tex:10` (hipótesis subsidiaria de eficiencia no contrastada), `07-resultados.tex:284-310` (validación fuera de muestra, `tab:fuera-de-muestra`), `09-conclusiones.tex:24` (fila del objetivo 2), `02-marco-teorico.tex:54` (elección supervisado/LLM/cascada), `03-estado-del-arte.tex:30,46-47` y `08-discusion.tex:34-38` (literatura TF-IDF/LR/SVM), `00-glosario.tex:58,70` (IDF, LR, SVM ya definidos).

## Goals / Non-Goals

**Goals:**
- Dejar en la tesis un método, una tabla y una lectura de la línea de base trazables a artefactos versionados.
- Agregar el contraste pareado sobre los mismos 103 casos con un script de solo lectura probado (TDD estricto) que versiona también las predicciones por caso de la línea de base.
- Eliminar toda afirmación de que no existe comparación con un clasificador supervisado, sin inflar la conclusión.
- Dejar el texto y la tabla preparados para que la llegada de c-206 (n = 150 arbitrado) sea un seguimiento mecánico.

**Non-Goals:**
- Cifras del arbitraje (c-206), brazo solo-LLM, calibración del gate, recompilar el PDF.
- Modificar números canónicos, el clasificador de producción, los corpus, `linea_de_base.py` o los artefactos de c-205/c-210.
- Afinar la línea de base (búsqueda de hiperparámetros, otros modelos): cambiaría la medición congelada de c-210.

## Decisions

**D1 — Lectura honesta, fijada antes de escribir prosa.** El texto SHALL decir exactamente esto, y nada más fuerte:
- Sobre los 103 casos fuera de muestra con consenso, el híbrido congelado superó a UN clasificador supervisado clásico (TF-IDF + regresión logística) entrenado con 200 ejemplos etiquetados del mismo dominio: 0,8447 frente a 0,6505 de exactitud estricta (variante balanceada) y 0,5825 (sin re-ponderación).
- No es una afirmación de superioridad general de los LLM ni del esquema híbrido sobre los clasificadores supervisados: con más datos etiquetados, otro modelo (SVM, BERT ajustado) o hiperparámetros afinados el resultado podría cambiar; la literatura revisada (`paket2024itservice`, `Revina2020_it_tickets`) muestra supervisados fuertes en otros corpus.
- Condiciones de equidad que se declaran: mismo conjunto de prueba y mismas funciones de métrica (`evaluation/metrics.py`); ambos sistemas se desarrollaron con los mismos 200 casos (el híbrido ajustó vocabulario y reglas de frontera con ellos; la línea de base se entrenó con ellos); ninguno vio los 103 casos de prueba.
- Amenazas que se declaran: el conjunto de prueba excluye los 47 discordantes, sesgado a casos más fáciles (afecta a ambos sistemas, pero no necesariamente por igual); clases chicas (Sistemas 5, Bases de Datos 13 en prueba; Bases de Datos tiene 1 solo caso de ajuste, lo que explica su F1 0,0 en la línea de base y favorece estructuralmente a un sistema con instrucciones); una sola organización; un único modelo supervisado sin afinar.
- La hipótesis subsidiaria "híbrido más eficiente que el LLM solo" SIGUE sin contrastarse: la línea de base no es el brazo solo-LLM y el texto MUST NOT sugerir lo contrario. El párrafo de `08-discusion.tex:10` se conserva.

**D2 — Contraste pareado: McNemar exacta como cifra principal, IC bootstrap pareado de la diferencia.** Por coherencia con el precedente de `08-discusion.tex:10` se informa la McNemar exacta bilateral (`p_exacto` de `contraste_mcnemar`) y, como sensibilidad, la corregida por continuidad; el JSON guarda ambas y el `criterio` que elegiría `stats.py`. La diferencia de exactitudes pareadas `(b − c)/n` lleva un IC 95 % bootstrap percentil pareado (remuestreo de índices de caso, B = 10 000, semilla fija), citando `Efron1993_bootstrap`. Alternativa descartada: IC de Newcombe para diferencias pareadas, porque exige una referencia nueva que no está en la bibliografía y el bootstrap ya se usa en la tesis. Variante primaria de la comparación: la balanceada; la sin re-ponderación se contrasta también y se informa como sensibilidad.

**D3 — Predicciones por caso de la línea de base: versionarlas en el artefacto nuevo.** El script reconstruye las predicciones con `evaluation.linea_de_base.predecir` (sin modificar el módulo), verifica que reproduzcan los aciertos agregados del JSON de c-210 (67/103 y 60/103) y del híbrido (87/103) y aborta si no coinciden. El artefacto `contraste_linea_de_base_c213.json` incluye, por `caso_id`: referencia, predicción del híbrido, predicción de cada variante de la línea de base y acierto estricto de cada sistema; más los SHA-256 de las entradas (corpus, `predicciones_independiente.json`, JSON de c-205 y de c-210). Así ningún número de la tesis depende de una corrida no versionada.

**D4 — Ubicación y forma del script.** `evaluation/data/campana/analisis/contraste_linea_de_base_c213.py` con su prueba `test_contraste_linea_de_base_c213.py`, siguiendo el patrón de `analisis_fuera_de_muestra_c205.py` y `analisis_dictamen_c207.py`: funciones puras (emparejar por `caso_id`, tabla 2×2, bootstrap pareado), salida JSON/MD en LF, UTF-8 sin BOM, deterministas byte a byte, `SHA256SUMS`. Solo lectura sobre los insumos. TDD estricto: prueba que falla primero para el emparejamiento, la tabla 2×2 (incluido el caso sin discordancias), el bootstrap con semilla y la verificación de anclas.

**D5 — Dónde va cada pieza en la tesis.**
- `04-marco-metodologico.tex`, `subsec:analisis-estadistico` (o un párrafo nuevo en `subsec:protocolo-pruebas`): `\paragraph{Línea de base supervisada clásica.}` con qué es (TF-IDF de palabras y caracteres + regresión logística, `Pedregosa2011_scikit_learn`), qué no es (no es el brazo solo-LLM ni un supervisado afinado), entrenamiento con los 200 casos, prueba en los 103, control de filtración (los 103 no se usan para entrenar ni para elegir variantes; las dos variantes se fijaron antes de medir), contraste pareado (D2).
- `07-resultados.tex`: subsección nueva `\subsection{Comparación con una línea de base supervisada}\label{subsec:linea-de-base}` a continuación de la validación fuera de muestra, con `tab:linea-de-base` (filas: línea de base balanceada, sin re-ponderación, híbrido; columnas: estricta con Wilson, laxa, macro-F1, balanced accuracy) y una segunda tabla o párrafo con F1 por clase y el contraste pareado (b, c, p exacta, diferencia e IC). La lectura ponderada de c-210 se menciona como post-estratificación, no como medición nueva.
- `08-discusion.tex`: reescribir la limitación quinta (de "no se comparó" a "se comparó contra un único supervisado clásico con 200 ejemplos; queda abierto…") y agregar en `subsec:interpretacion-resultados` o en `subsec:comparacion-literatura` la lectura D1.
- `09-conclusiones.tex:47`: reemplazar la última oración por la conclusión acotada D1; evaluar si la fila del objetivo 2 (`:24`) admite una mención breve (sin cambiar el veredicto "No alcanzado").
- `10-recomendaciones.tex:14`: la línea de trabajo futuro deja de responder a la "ausencia de una línea de base" y pasa a lo que falta: brazo solo-LLM (para la hipótesis de eficiencia), más datos de entrenamiento, supervisados más fuertes (SVM, modelos tipo BERT ajustados) y la repetición sobre n = 150 arbitrado.
- `00-resumen.tex` y `01-introduccion.tex`: verificar por grep; editar solo si afirman la inexistencia de la comparación (la exploración no encontró afirmaciones explícitas).

**D6 — Preparación para c-206.** La tabla y la prosa nombran el conjunto como "los 103 casos con consenso de `E3` y `E4`" y llevan una nota "con el arbitraje de los 47 discordantes (\autoref{…}) la comparación se repite sobre los 150"; el script recibe la ruta de la referencia y el `n` esperado como parámetros, de modo que la actualización a n = 150 sea volver a correrlo con la referencia arbitrada y sustituir cifras. Este change no anticipa ninguna cifra de c-206.

**D7 — Trazabilidad.** Sección `### 3.22 Línea de base supervisada clásica y contraste pareado (c-209, c-210, c-213)` en `numeros-canonicos.md` (aditiva: declara que no reemplaza ningún valor de la tabla canónica), entrada `## … c-213` en `dictamen-correcciones.md` atada al criterio 4, `## FASE 69` en `CHANGES.md` con el patrón de la FASE 68, regeneración de `tesis_para_agente.md` con `build_tesis_para_agente.py` y `verify_citations.py` sin claves nuevas.

## Risks / Trade-offs

- [El contraste pareado podría no ser significativo o el IC cruzar cero] → La lectura D1 no depende de la significación; se informa lo que salga. (La reconstrucción exploratoria sugiere b = 27, c = 7, pero esa cifra no es citable hasta que el artefacto versionado la produzca.)
- [La reconstrucción de las predicciones no reproduce los agregados de c-210 por versión de scikit-learn] → El script aborta (D3) y la tarea queda bloqueada con el diagnóstico; no se publica ninguna cifra pareada.
- [Sobreinterpretación por parte del tribunal o de los autores] → D1 fija las frases permitidas; la revisión de la tarea final verifica que ninguna oración afirme superioridad general ni eficiencia frente al LLM solo.
- [Choque de redacción con c-207/c-211/c-212, ya integrados] → Se relee cada párrafo tocado contra el texto vigente y se mantienen los rótulos (`Sistemas` como clase débil del híbrido, no de la línea de base).
- [El PDF queda desfasado del `.tex`] → Tarea manual explícita para el dueño (recompilación con Docker).
