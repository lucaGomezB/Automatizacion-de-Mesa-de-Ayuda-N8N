# Bitácora de búsqueda bibliográfica — c-110

Registro de la revisión de literatura que sustenta el capítulo de estado del arte
(`03-estado-del-arte.tex`) y los fundamentos del marco teórico
(`02-marco-teorico.tex`). Corresponde a los ítems 11 y 12 del dictamen CONEAU
2026-10-20.

- **Fecha de corte:** 21 de octubre de 2026.
- **Extensión c-138 (grupo C):** fecha de corte propia, 25 de octubre de 2026
  (`FECHA_CORTE_C`); cambio c-138-estado-del-arte-calibracion-y-cascadas. Los grupos A y
  B y su fecha de corte (21 de octubre de 2026) no cambian; el grupo C se registra al
  final de esta bitácora.
- **Cambio:** c-110-marco-teorico-hitl-y-literatura.
- **Bases consultadas:** Scopus, IEEE Xplore, ACM Digital Library, ACL Anthology,
  Google Scholar, arXiv.
- **Definición de "resultado":** trabajos finalmente incorporados, identificados
  por su clave bibliográfica en `docs/Tesis/v9 (IA)/Bibliography_base.bib`. El
  conteo bruto de coincidencias no es recuperable de forma programática desde el
  entorno de trabajo para las bases de suscripción (Scopus, IEEE Xplore, ACM
  Digital Library), que exigen sesión autenticada; para esas bases se registra el
  conjunto de trabajos examinados e incorporados.
- **Consistencia:** las bases, cadenas y criterios aquí registrados coinciden con
  los declarados en el párrafo "Protocolo de revisión" de
  `03-estado-del-arte.tex`. El párrafo de protocolo no declara base, cadena ni
  criterio ausente de esta bitácora, y esta bitácora no contiene consultas que el
  texto no mencione.

## Cadenas de búsqueda

Formuladas en inglés, combinando términos de dominio y de método.

- **A1:** ("help desk" OR "service desk" OR "IT support") AND
  ("ticket classification" OR "incident classification") AND
  ("machine learning" OR "natural language processing" OR "large language model")
- **A2:** ("large language model" OR "LLM") AND ("ticket" OR "incident") AND
  ("classification" OR "routing")
- **A3:** ("Spanish" OR "español") AND ("large language model" OR "LLM") AND
  ("evaluation" OR "benchmark")
- **A4:** ("Gemini" OR "Google Gemini") AND ("ticket" OR "incident" OR "help desk")
- **B1:** ("human-in-the-loop" OR "human in the loop" OR "human-AI interaction")
  AND ("machine learning" OR "large language model")
- **C1:** ("calibration" OR "confidence estimation" OR "confidence elicitation" OR
  "uncertainty") AND ("large language model" OR "LLM" OR "language model" OR
  "neural network") AND ("classification" OR "few-shot" OR "verbalized" OR
  "overconfidence")
- **C2:** ("cascade" OR "cascading" OR "routing" OR "hybrid" OR "rule-based") AND
  ("large language model" OR "LLM" OR "natural language processing" OR "NLP") AND
  ("classification" OR "cost" OR "efficiency")

## Grupo A — Estado del arte moderno de clasificación de tickets (2023-2026)

Criterios de inclusión: publicación arbitrada en el período 2023-2026, idioma
español o multilingüe, evaluación empírica de modelos o métodos. Criterios de
exclusión: literatura no arbitrada, notas de prensa y material comercial sin
respaldo metodológico.

| Base | Cadenas aplicadas | Fecha | Resultado (trabajos incorporados) |
|------|-------------------|-------|-----------------------------------|
| Scopus | A1, A2, A3, A4 | 21-10-2026 | `zangari2023ticket`, `colavito2025benchmarking`, `mayorrocher2026spanish`, `bernalbeltran2025mexicanspanish`, `ramonferrer2026tripletotext` |
| IEEE Xplore | A1, A2, A4 | 21-10-2026 | `paket2024itservice` |
| ACM Digital Library | A1, A2 | 21-10-2026 | `liu2025tickit` |
| ACL Anthology | A1, A2, A3 | 21-10-2026 | `ahuja2023mega`, `lai2023okapi`, `zhang2023multilingual`, `xuan2025mmluprox`, `grandury2025laleaderboard` |
| Google Scholar | A1, A2, A3, A4 | 21-10-2026 | Sin incorporaciones exclusivas: usado para descubrimiento y remisión a las fuentes primarias. Para A4 no arrojó coincidencias de artículo arbitrado 2023-2026 que evalúe Google Gemini sobre tickets de soporte en español. |
| arXiv | A1, A2 | 21-10-2026 | Sin incorporaciones nuevas: usado para verificación de procedencia de preimpresos. |

La cadena A4 (Gemini + tickets de soporte) no identificó, en las seis bases y a
la fecha de corte, artículo arbitrado 2023-2026 que evalúe Google Gemini sobre
tickets de soporte en español. Esta es la vacancia declarada, de forma relativa
al alcance revisado, en `03-estado-del-arte.tex`.

## Grupo B — Fundamentos de human-in-the-loop (sin restricción temporal)

Criterio de inclusión: trabajo fundacional o de referencia sobre interacción
humano-IA o aprendizaje con intervención humana. No se impuso restricción
temporal, porque los trabajos seminales que definen el concepto son anteriores a
2023.

| Base | Cadenas aplicadas | Fecha | Resultado (trabajos incorporados) |
|------|-------------------|-------|-----------------------------------|
| Scopus | B1 | 21-10-2026 | `Shneiderman2020_human_centered_ai`, `MosqueiraRey2023_human_in_the_loop`, `Zanzotto2019_human_in_the_loop` |
| ACM Digital Library | B1 | 21-10-2026 | `Amershi2019_human_ai`, `Wu2022_ai_chains` |
| Google Scholar | B1 | 21-10-2026 | Sin incorporaciones exclusivas: usado para descubrimiento y verificación cruzada de los trabajos seminales. |

## Verificación por DOI de las fuentes incorporadas

Todas las entradas nuevas del cambio se verificaron contra la API de Crossref el
21 de octubre de 2026 (resolución HTTP 200 y metadatos coincidentes: título,
contenedor y año).

| Clave | DOI | Resultado |
|-------|-----|-----------|
| `Amershi2019_human_ai` | 10.1145/3290605.3300233 | Resuelve (CHI 2019, ACM) |
| `Shneiderman2020_human_centered_ai` | 10.1080/10447318.2020.1741118 | Resuelve (IJHCI 36(6), 495-504) |
| `MosqueiraRey2023_human_in_the_loop` | 10.1007/s10462-022-10246-w | Resuelve (Artificial Intelligence Review 56(4), 3005-3054; impreso 2023-04) |
| `Zanzotto2019_human_in_the_loop` | 10.1613/jair.1.11345 | Resuelve (JAIR 64, 243-252) |
| `Wu2022_ai_chains` | 10.1145/3491102.3517582 | Resuelve (CHI 2022, ACM) |

## Grupo C — Calibración de la confianza y cascadas de modelos (c-138; sin restricción temporal)

Extensión del protocolo declarada en el párrafo "Protocolo de revisión" de
`03-estado-del-arte.tex` (cambio c-138-estado-del-arte-calibracion-y-cascadas).
Los grupos A y B y su fecha de corte (21 de octubre de 2026) no se modificaron.

- **Fecha de corte del grupo C (`FECHA_CORTE_C`):** 25 de octubre de 2026,
  idéntica en el texto y en esta bitácora.
- **Bases:** las mismas seis (Scopus, IEEE Xplore, ACM Digital Library, ACL
  Anthology, Google Scholar, arXiv).
- **Cadenas:** C1 y C2 (ver "Cadenas de búsqueda"), con los operadores y términos
  exactos de la declaración del texto.
- **Criterios de inclusión:** publicación arbitrada (revistas y actas con revisión
  por pares, incluidas ICML/PMLR, ICLR, las sedes de ACL y TMLR) que trate
  explícitamente la calibración o la estimación de la confianza de clasificadores o
  modelos de lenguaje (C1), o las cascadas o el enrutamiento de modelos con criterio
  de costo y exactitud (C2), con evaluación empírica o método de referencia, sin
  restricción temporal (como B1, porque los trabajos fundacionales son anteriores a
  2023).
- **Criterios de exclusión:** literatura no arbitrada (incluidos los preprints sin
  versión arbitrada), notas de prensa y material comercial.
- **Regla de selección:** entre los trabajos que cumplen los criterios se incorporan,
  hasta seis, los más próximos al escenario de este trabajo (un modelo consultado como
  servicio y una cascada de dos etapas: una económica y otra costosa).

### Método de ejecución y límites de acceso (convención de la bitácora c-110)

Las seis fuentes núcleo se preseleccionaron en la fase de propuesta (22-10-2026) a
partir del dictamen CONEAU del 22-10-2026 y de conocimiento previo de los trabajos de
referencia; en la ejecución del 25-10-2026 se corrieron las cadenas y se verificó que
ningún resultado examinado sustituyera a una fuente núcleo según la regla de selección.
El conteo bruto de coincidencias solo es recuperable para arXiv (API pública); para el
resto se registran los trabajos examinados. Los controles anti-bot (CAPTCHA de Google
Scholar, desafío de verificación de OpenReview) no se evadieron.

| Base | Cadenas aplicadas | Fecha | Trabajos examinados | Resultado (trabajos incorporados) |
|------|-------------------|-------|---------------------|-----------------------------------|
| Scopus | C1, C2 | 25-10-2026 | 0 (sin acceso desde esta máquina: requiere sesión de suscripción) | Sin incorporaciones desde esta base |
| IEEE Xplore | C1, C2 | 25-10-2026 | 0 (sin acceso a la búsqueda con sesión; dos consultas por motor web restringido al dominio no devolvieron resultados de `ieeexplore.ieee.org`) | Sin incorporaciones desde esta base |
| ACM Digital Library | C1, C2 | 25-10-2026 | 4 (consultas por motor web restringido al dominio; el motor no admite operadores booleanos y se usaron los términos de las cadenas: Sycophantic Metacognition, ConfTuner, BudgetMLAgent y la revisión de enrutamiento de JAIR; todos examinados por título y resumen) | Sin incorporaciones desde esta base |
| ACL Anthology | C1, C2 | 25-10-2026 | 8 (consultas por motor web restringido a `aclanthology.org` con los términos de las cadenas: `2024.acl-long.652`, `2025.trustnlp-main.26`, `2025.gem-1.49`, `2024.findings-acl.357`, `2026.findings-acl.1671`, `2025.emnlp-main.1505`, `2026.acl-industry.93`, `2025.emnlp-main.531`) más las fuentes núcleo de la sede | `Tian2023_verbalized_confidence`, `Varshney2022_model_cascading` (ACL Anthology, EMNLP; preseleccionadas y verificadas en las tres compuertas) |
| Google Scholar | C1, C2 | 25-10-2026 | 0 (la interfaz respondió con CAPTCHA; no se evadió) | Sin incorporaciones desde esta base |
| arXiv | C1, C2 | 25-10-2026 | 200 (los 100 primeros resultados por relevancia de cada cadena, de 2334 en C1 y 3600 en C2, con la cadena aplicada a los resúmenes; título y, para los candidatos, resumen) más 3 consultas dirigidas a tickets y a Gemini (7 resultados) | `Xiong2024_confidence_elicitation` (C1, arXiv:2306.13063; versión arbitrada ICLR 2024), `Chen2024_frugalgpt` (C2, arXiv:2305.05176; versión arbitrada TMLR 2024), `Varshney2022_model_cascading` (C2, arXiv:2210.05528; versión arbitrada EMNLP 2022). `Guo2017_calibration` y `Zhao2021_calibrate_before_use` no figuran entre los 100 primeros resultados de C1: se incorporan por la regla de trabajo de referencia sin restricción temporal y por su proximidad al escenario |

Las bases sin acceso (Scopus, IEEE Xplore y Google Scholar) quedan registradas con
trabajos examinados = 0: la afirmación de vacancia de `03-estado-del-arte.tex` se
formula por ello relativa a las fuentes efectivamente consultadas con C1 y C2 hasta
`FECHA_CORTE_C`, sin declararla sobre las seis bases en conjunto.

### Revisión contra las condiciones de la tarea 2.3

- **(a) Cascada de reglas y LLM con confianza verbalizada sobre tickets de soporte en
  español:** ningún resultado examinado la evalúa. Las consultas dirigidas (arXiv:
  cascada/enrutamiento/confianza/calibración AND tickets/mesa de ayuda AND LLM; y
  cascada/reglas AND español AND tickets AND LLM) devolvieron 3 y 1 resultados, ninguno
  pertinente (entre ellos TickIt, arXiv:2504.08475, ya relevado en el grupo A como
  `liu2025tickit`, que trata la escalación de tickets y no una cascada de reglas y LLM
  con confianza verbalizada). Las búsquedas web abiertas (sin restricción de dominio)
  tampoco identificaron trabajo arbitrado. Se conserva la vacancia acotada en 3.x.
- **(b) Trabajo arbitrado 2023-2026 que evalúe Gemini sobre tickets en español:**
  ninguno identificado (consulta dirigida de arXiv con "Gemini" AND ticket/incident/help
  desk: 3 resultados no pertinentes; búsqueda web abierta: solo entradas de blogs
  comerciales de 2023 y una tesis de grado ecuatoriana, no arbitrada). La vacancia A4
  del grupo A no cambia.

### Trabajos excluidos o no seleccionados

| Trabajo | Motivo |
|---------|--------|
| Kadavath et al. (2022), arXiv:2207.05221 | Excluido: preprint sin versión arbitrada |
| Chen, Zaharia y Zou, versión arXiv de FrugalGPT (arXiv:2305.05176v1) | Excluida como cita: existe versión arbitrada (TMLR 2024), que se cita; el texto se leyó en la versión arXiv v1 (ver nota de FrugalGPT) |
| Hybrid LLM Routing for Efficient App Feedback Classification (arXiv:2507.08250); C³: Confidence Calibration Model Cascade (arXiv:2402.15991); Cost-Aware Model Selection for Text Classification (arXiv:2602.06370) | Excluidos: preprints sin versión arbitrada declarada en arXiv al 25-10-2026 |
| Zhou et al., Batch Calibration (ICLR 2024, arXiv:2309.17249); Agreement-Based Cascading (TMLR 2025, arXiv:2407.02348); Optimising Calls to LLMs with Uncertainty-Based Two-Tier Selection (COLM 2024, arXiv:2405.02134); Assessing Generative Language Models in Classification Tasks (NLDB 2024, arXiv:2408.17362); Moslem y Kelleher, survey de enrutamiento y cascadas (TMLR 2026, arXiv:2603.04445) | No seleccionados: cumplen los criterios por sede arbitrada declarada en arXiv, pero exceden el tope de seis o son menos próximos al escenario según la regla de selección; examinados por título y resumen, no verificados en texto completo y no citados |
| Reserva D2 (Geng et al. 2024; Desai y Durrett 2020; Jiang et al. 2021; Moslem y Kelleher 2026; Lin, Hilton y Evans 2022; Zhou, Jurafsky y Hashimoto 2023; Brier 1950; Naeini et al. 2015) | No utilizada: ninguna fuente núcleo falló una compuerta |
| ITSM-BERT (SBBD 2026) y Alsac et al. (UBMK 2025) | Fuera de alcance (Open Question 2, decisión PROVISIONAL del orquestador, 2026-10-25): no son capturadas por C1-C2; pertenecen a la cadena A1, cuyo corte no se mueve |

## Verificación por fuente del grupo C (25 de octubre de 2026)

Compuertas: (1) existencia, (2) metadatos, (3) contenido (texto completo leído). Las seis
fuentes superan las tres.

| Clave | DOI o URL oficial | Compuerta 1 (existencia) | Compuerta 2 (metadatos) | Compuerta 3 (contenido) |
|-------|-------------------|--------------------------|-------------------------|-------------------------|
| `Guo2017_calibration` | https://proceedings.mlr.press/v70/guo17a.html | HTTP 200 (PMLR) | Metadatos `citation_*` de PMLR: 4 autores, ICML 2017, PMLR 70, pp. 1321-1330, fecha 2017-07-17 | Texto completo de la versión PMLR (PDF oficial) |
| `Zhao2021_calibrate_before_use` | https://proceedings.mlr.press/v139/zhao21c.html | HTTP 200 (PMLR) | Metadatos de PMLR: 5 autores, ICML 2021, PMLR 139, pp. 12697-12706 | Texto completo de la versión PMLR |
| `Tian2023_verbalized_confidence` | 10.18653/v1/2023.emnlp-main.330 | `curl -sI https://doi.org/...` devuelve 302 a `aclanthology.org/2023.emnlp-main.330` | Crossref: título, 8 autores, EMNLP 2023, pp. 5433-5442, DOI coincidentes | Texto completo del PDF de ACL Anthology |
| `Xiong2024_confidence_elicitation` | https://openreview.net/forum?id=gjeQKFxFpZ | El foro de OpenReview responde con un desafío de verificación (no se evadió); la existencia se confirma por la página oficial de ICLR (`iclr.cc/virtual/2024/poster/18135`, que enlaza ese foro), por MLAnthology y por el encabezado "Published as a conference paper at ICLR 2024" del PDF | 7 autores y título coincidentes entre el PDF arXiv v2 (2306.13063v2), la página de ICLR y MLAnthology; ICLR 2024 no tiene paginación | Texto completo de arXiv v2 (encabezado ICLR 2024) |
| `Varshney2022_model_cascading` | 10.18653/v1/2022.emnlp-main.756 | `curl -sI https://doi.org/...` devuelve 302 a `aclanthology.org/2022.emnlp-main.756` | Crossref: título, 2 autores, EMNLP 2022, pp. 11007-11021, DOI coincidentes | Texto completo del PDF de ACL Anthology |
| `Chen2024_frugalgpt` | https://openreview.net/forum?id=cSimKw5p6R | Listado y `.bib` oficiales de TMLR (`jmlr.org/tmlr/papers/bib/cSimKw5p6R.bib`) responden 200; el PDF de OpenReview devuelve 403 con desafío anti-bot (no se evadió) | `.bib` oficial de TMLR: 3 autores, TMLR, ISSN 2835-8856, 2024 (Featured Certification) | Texto completo de arXiv:2305.05176v1 (única versión en arXiv); no se leyó el texto de la versión TMLR |

**Nota de FrugalGPT (tarea 3.4, Open Question 4).** El PDF de la versión TMLR en
OpenReview exige verificación anti-bot y no se accedió a él. El contenido se verificó
sobre arXiv:2305.05176v1 (sec. 3, p. 5), y la atribución en la tesis se limita al
concepto de cascada de LLM de costo creciente con una función de puntaje aprendida y un
umbral que decide aceptar o escalar. No se cita ninguna cifra de ahorro ni se atribuyen
a la versión TMLR resultados experimentales. Una verificación posterior del texto de la
versión TMLR por parte del usuario queda como mejora opcional.

## Correspondencia afirmación-fuente del grupo C

Paginación: la de la publicación (Guo: página del PDF + 1320; Zhao: + 12696; Tian: + 5432;
Varshney: + 11006); Xiong y FrugalGPT, la del PDF de arXiv (v2 y v1).

| Lugar en la tesis | Afirmación | Fuente | Sección o página que la sostiene |
|-------------------|------------|--------|----------------------------------|
| `02` 2.5; `03` 3.4 | La calibración se mide con diagramas de fiabilidad y con el error de calibración esperado (ECE) | `Guo2017_calibration` | Sec. 2, pp. 1322-1323 (el ECE se atribuye allí a Naeini et al., 2015; la tesis no atribuye a Guo su invención) |
| `02` 2.5 | La calibración puede corregirse a posteriori, por ejemplo con escalado de temperatura | `Guo2017_calibration` | Resumen (p. 1321) y sec. 4.2 (pp. 1326-1327) |
| `03` 3.4 | Las redes neuronales modernas tienden a la sobreconfianza; experimentos que incluyen clasificación de documentos; corrección con un parámetro de temperatura | `Guo2017_calibration` | Resumen y sec. 1 (p. 1321); sec. 5, 20 News, Reuters y SST (pp. 1327-1328) y Fig. 4 (sobreconfianza de ResNet sin calibrar) |
| `03` 3.4 | En clasificación por instrucciones (GPT-3 y GPT-2) las predicciones se sesgan hacia ciertas etiquetas; una calibración contextual de la distribución de salida reduce el sesgo | `Zhao2021_calibrate_before_use` | Resumen y sec. 1 (p. 12697); sec. 4 (pp. 12700-12701); sec. 5 (p. 12701) |
| `02` 2.5; `03` 3.4; `08` 9.2 | Con modelos ajustados con retroalimentación humana, la confianza verbalizada puede estar mejor calibrada que las probabilidades condicionales, en tareas de preguntas y respuestas (TriviaQA, SciQ, TruthfulQA) | `Tian2023_verbalized_confidence` | Resumen y sec. 1 (p. 5433); conclusiones (p. 5437) |
| `02` 2.5; `08` 9.2 | La calidad de la confianza verbalizada depende de cómo se la elicita | `Tian2023_verbalized_confidence`; `Xiong2024_confidence_elicitation` | Tian: p. 5437 (los prompts de una y dos etapas difieren en calibración); Xiong: sec. 5.2, p. 7 (ninguna estrategia de elicitación supera de forma consistente a las demás) |
| `02` 2.5 | Un servicio de caja negra expone solo entrada y salida textuales; la confianza se obtiene verbalizada | `Xiong2024_confidence_elicitation` | Resumen y p. 2 (API comerciales solo textuales) |
| `02` 2.5; `03` 3.4; `08` 9.2 | La confianza verbalizada tiende a la sobreconfianza, se concentra en valores altos y discrimina poco los aciertos de los errores | `Xiong2024_confidence_elicitation` | Resumen (p. 1); sec. 5.1, p. 6 (valores altos; la cifra "80 % a 100 %" no se cita en la tesis) y sec. 5.1, p. 7 (poca capacidad de distinguir aciertos de errores incluso en GPT-4) |
| `03` 3.4 | Distinguen la calibración (ECE) de la predicción de fallos (AUROC) | `Xiong2024_confidence_elicitation` | Sec. 5, "Evaluation Metrics", p. 7 |
| `02` 2.5; `03` 3.4; `08` 9.2 | Cascada de modelos de capacidad creciente con derivación por umbral sobre la confianza de predicción | `Varshney2022_model_cascading` | Resumen (p. 11007); sec. 3 (confianza de predicción MaxProb y umbral), p. 11010 |
| `03` 3.4 | Mejoras de eficiencia y exactitud en clasificación de comprensión del lenguaje natural | `Varshney2022_model_cascading` | Resumen (p. 11007); sec. 4.1-4.2 (diez conjuntos de clasificación de comprensión del lenguaje natural), pp. 11011-11012 |
| `02` 2.5; `03` 3.4; `08` 9.2 | Cascada de LLM de costo creciente con función de puntaje aprendida y umbral que decide aceptar o escalar | `Chen2024_frugalgpt` | Verificado en arXiv v1: sec. 3, p. 5 (componentes de la cascada: función de puntaje y enrutador; se acepta si el puntaje supera un umbral) |

Las afirmaciones sobre el sistema propio (primera etapa de reglas, confianza verbalizada
en JSON de la etapa Gemini, puntaje de correctitud) son del texto de la tesis y no se
atribuyen a estas fuentes; ninguna oración agregada atribuye resultados sobre Gemini,
sobre tickets de soporte o sobre una primera etapa de reglas.
