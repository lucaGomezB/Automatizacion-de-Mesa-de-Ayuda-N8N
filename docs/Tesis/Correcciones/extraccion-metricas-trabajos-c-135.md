# Extracción de métricas de `tab:trabajos-academicos` — c-135

Registro de procedencia de las celdas "Corpus/idioma" y "Métrica reportada" de la
Tabla `tab:trabajos-academicos` (`03-estado-del-arte.tex`) completadas por el change
`c-135-cronologia-y-consistencia-redaccional` (B10 del dictamen CONEAU 2026-10-22;
design D8; tareas 3.1 a 3.5).

- **Fecha de consulta:** 2026-10-25.
- **Regla de consignación:** solo cifras textuales de la fuente accesible (nombre de la
  métrica, valor y modelo o condición), sin recalcular, promediar ni inferir. Donde la
  fuente accesible no consigna el dato, la celda conserva "no reportado en el alcance
  revisado" con su motivo abreviado.
- **Orden de consulta (D8):** (1) resumen (OpenAlex, Semantic Scholar o página del
  editor); (2) texto completo de acceso abierto; (3) acceso institucional de los autores
  (OQ-5).
- **OQ-5 (RESUELTA PROVISIONALMENTE, 2026-10-25):** esta máquina no tiene acceso
  institucional (Biblioteca Electrónica de Ciencia y Tecnología / UTN) ni los autores
  confirmaron tenerlo; pendiente de confirmación del autor. Las celdas que dependen de
  texto completo de acceso cerrado (Paket 2024, Colavito 2025) quedan como "no
  reportado en el alcance revisado" con el motivo.
- **Límite de acceso:** no se evadieron controles anti-bot. El texto completo de Zangari
  2023 (Elsevier, acceso abierto híbrido CC BY 4.0) no pudo recuperarse: el repositorio
  institucional `iris.unive.it` / `arca.unive.it` respondió con desafío de Cloudflare y
  HTTP 403, y `linkinghub.elsevier.com` solo redirige. Se consignó únicamente lo que
  consta en su resumen (OpenAlex, 2026-10-25).
- **Sin altas en `Bibliography_base.bib`:** las cinco claves ya existen.

## Registro por celda

| Obra (clave) | DOI | Celda | Valor consignado en la tesis | Fuente consultada (URL), tipo de acceso | Ubicación en la fuente | Nota |
|---|---|---|---|---|---|---|
| Revina 2020 (`Revina2020_it_tickets`) | 10.1109/ACCESS.2020.3032840 | Corpus/idioma | 28.243 y 4.684 tickets (30 y 60 etiquetados); inglés predominante | Texto completo IEEE Access, CC BY 4.0, versión del editor desde el repositorio `depositonce.tu-berlin.de/handle/11303/18342` (acceso abierto) | Sección IV.A "Datasets" y Tabla 4: Data1 = 28.243 tickets (2015-2018); Data2 = 4.684 entradas (enero-mayo 2019); "prevailingly English" (más del 80 % de palabras en inglés, algo de alemán); "experts labeled 30 and 60 tickets of Data1 and Data2" | Los tickets proceden del departamento ITIL CHM de una gran empresa; solo 30 y 60 están etiquetados (evaluación con un ticket de prueba por ronda). |
| Revina 2020 | 10.1109/ACCESS.2020.3032840 | Métrica reportada | exactitud 1,000 (árbol de decisión, rasgos lingüísticos) frente a 0,433 como máximo con TF-IDF (primer conjunto) | Ídem | Tabla 6 (p. 193388): Data1, rasgos lingüísticos, decision trees: exactitud, precisión media, exhaustividad media y F-score = 1,000; Data1, TF-IDF: máximo de exactitud 0,433 (decision trees, ECkNN, HFNN, NHBNN y regresión logística). Tabla 7 (p. 193389): con los cinco mejores rasgos, decision trees y naive Bayes = 1,000 en ambos conjuntos | En Data2 (Tabla 6) los árboles y naive Bayes también alcanzan 1,000 con rasgos lingüísticos y TF-IDF llega a 0,700 como máximo. Conjuntos etiquetados muy pequeños (30 y 60): cifra consignada tal como la reporta la fuente, sin interpretación. El resumen no consigna cifras. |
| Zangari 2023 (`zangari2023ticket`) | 10.1016/j.eswa.2023.119984 | Corpus/idioma | 20.000 reclamos + 35.000 issues; idioma no reportado en el alcance revisado (texto inaccesible) | Resumen vía OpenAlex (`api.openalex.org/works/doi:10.1016/j.eswa.2023.119984`); texto completo de acceso abierto híbrido no recuperable (ver "Límite de acceso") | Resumen: "20,000 customer complaints" y "35,000 issues crawled from a bug reporting website" | El resumen no declara el idioma. |
| Zangari 2023 | 10.1016/j.eswa.2023.119984 | Métrica reportada | mejor embedding: >28 % en F1 sobre el estándar; ML-BERT: hasta 5,7 % en F1 y 5,4 % en exactitud (bugs) | Ídem | Resumen: "the best method improves by more than 28% in F1-score over the standard strategy" y "ML-BERT outperforms the best baseline by up to 5.7% in F1-score and 5.4% in accuracy" (dataset de bugs) | Mejoras tal como las expresa el resumen (no se declara si son relativas o absolutas); no se consigna ningún valor absoluto de F1. Se omite de la celda por espacio la referencia de comparación del 5,7 % y el 5,4 % ("la mejor línea base" del resumen). |
| Paket 2024 (`paket2024itservice`) | 10.1109/ubmk63289.2024.10773473 | Métrica reportada | no reportado en el alcance revisado (texto cerrado); cualitativo: BERT supera a los LLM | Resumen vía OpenAlex (`api.openalex.org/works/doi:10.1109/ubmk63289.2024.10773473`); IEEE Xplore, acceso cerrado (OpenAlex: `oa_status = closed`) | Resumen: "BERT-based classification models outperform the LLMs"; sin valores numéricos | Sin acceso institucional (OQ-5). |
| Paket 2024 | 10.1109/ubmk63289.2024.10773473 | Corpus/idioma | turco, 172 clases (sin cambios) | Ídem | Resumen: "multi-class classification problem in the Turkish language, which includes 172 classes" | El tamaño del corpus no consta en el resumen; la celda no lo declara. |
| Liu 2025 (`liu2025tickit`) | 10.1145/3696630.3728558 | Corpus/idioma | tickets de nube (ByteDance), 160 de prueba; idioma: no reportado en el alcance revisado | Texto completo del preprint arXiv:2504.08475v1 (`arxiv.org/pdf/2504.08475`), acceso abierto; la versión del editor (ACM) también es de acceso abierto según OpenAlex pero no se cotejó | Sección 4.1 y Tabla 1: 148 tickets de entrenamiento I; 20.066 tickets y 654.901 mensajes procesados (1-ago a 31-dic-2024); 2.012 escalados; 472 con retroalimentación (312 de entrenamiento II y 160 de prueba) | El texto no declara el idioma. |
| Liu 2025 | 10.1145/3696630.3728558 | Métrica reportada | F1 0,862 (ajuste fino supervisado + CoT) frente a 0,801 como máximo con modelos pequeños | Ídem | Tabla 2 y Sección 4.3.1: SFT + CoT: precisión 0,818, recall 0,912, F1 0,862 ("highest F1-score (86.2%) among all methods compared"); modelos pequeños (SLM): F1 máximo 0,801 (Embed Vec. + MLP) | Cifras del preprint v1; la versión del editor podría diferir en detalle. El resumen no consigna cifras. Se omiten de la celda por espacio la precisión (0,818) y el recall (0,912) de la misma fila de la Tabla 2, y los 20.066 tickets procesados. |
| Colavito 2025 (`colavito2025benchmarking`) | 10.1016/j.infsof.2025.107758 | Corpus/idioma | dos datasets de issues de GitHub; tamaño: no reportado en el alcance revisado (texto cerrado) | Resumen vía Semantic Scholar (`api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.infsof.2025.107758?fields=abstract`); Elsevier, acceso cerrado (OpenAlex: `oa_status = closed`); repositorio `arpi.unipi.it` (desafío de Cloudflare, HTTP 403); `ricerca.uniba.it` solo se halló como registro bibliográfico en la búsqueda, sin texto completo accesible | Resumen: "two different datasets of GitHub issues" | Sin acceso institucional (OQ-5). |
| Colavito 2025 | 10.1016/j.infsof.2025.107758 | Métrica reportada | no reportado en el alcance revisado (texto cerrado); cualitativo: BERT más consistente que los LLM generativos | Ídem | Resumen: los LLM generativos "show potential for zero-shot classification" con variación significativa entre datasets; "BERT-like models show more consistent performance" | Sin valores numéricos en el resumen. |

## Residuo "no reportado en el alcance revisado" (motivo)

| Celda | Motivo |
|---|---|
| Zangari 2023, idioma | El resumen no lo consigna y el texto completo no fue recuperable desde esta máquina. |
| Paket 2024, métrica | El resumen es cualitativo; el texto completo es de acceso cerrado y no hay acceso institucional. |
| Liu 2025, idioma | El texto completo (preprint) no declara el idioma. |
| Colavito 2025, tamaño | El resumen no lo consigna; el texto completo es de acceso cerrado. |
| Colavito 2025, métrica | El resumen no consigna cifras; el texto completo es de acceso cerrado. |

## Discrepancias detectadas con frases de c-139 (no editadas en c-135)

- **`03-estado-del-arte.tex`, frase "desplazamiento hacia LLM" (propiedad de c-139):** afirma que la literatura reciente
  "confirma el desplazamiento del enfoque clásico hacia arquitecturas basadas en LLM".
  La tabla completada muestra que dos de las cuatro obras recientes de LLM relevan
  resultados favorables a BERT (Paket 2024: BERT supera a los LLM en 172 clases;
  Colavito 2025: los BERT son más consistentes y requieren menos recursos) y que la
  mejora de Zangari 2023 se obtiene con BERT. Solo Liu 2025 (TickIt) reporta un LLM con
  ajuste fino como el mejor método (F1 0,862). c-139 debería matizar "confirma el
  desplazamiento".
- **`01-introduccion.tex:66` (idiomas de los corpus; propiedad de c-139):** atribuye a
  Zangari 2023 y Colavito 2025 corpus "en inglés y, en menor medida, en alemán o
  portugués". El idioma de los corpus de Zangari 2023, de Liu 2025 y de Colavito 2025 no consta en
  las fuentes accesibles (resumen o preprint); el único corpus con idioma verificado es el
  de Revina 2020 (inglés predominante con algo de alemán) y el de Paket 2024 (turco, en
  el resumen). c-139 debería sustentar esa frase con una fuente o reformularla.
- **Segunda frase de `03-estado-del-arte.tex` sobre Revina (`:30`, propiedad de c-139):**
  describe los resultados de Revina en términos cualitativos; la tabla ahora consigna que
  sus cifras (exactitud 1,000) provienen de conjuntos etiquetados de 30 y 60 tickets, un
  matiz que c-139 puede incorporar al mencionar su alcance.
