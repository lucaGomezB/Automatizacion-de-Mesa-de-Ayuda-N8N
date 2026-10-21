# Bitácora de búsqueda bibliográfica — c-110

Registro de la revisión de literatura que sustenta el capítulo de estado del arte
(`03-estado-del-arte.tex`) y los fundamentos del marco teórico
(`02-marco-teorico.tex`). Corresponde a los ítems 11 y 12 del dictamen CONEAU
2026-10-20.

- **Fecha de corte:** 21 de octubre de 2026.
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
