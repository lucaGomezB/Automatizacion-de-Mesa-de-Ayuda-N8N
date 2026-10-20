# Tasks: c-78 — Bibliografia y atribucion

> Convencion de archivos: `S = docs/Tesis/v9 (IA)/paper/sections`;
> `B = docs/Tesis/v9 (IA)/Bibliography_base.bib`;
> `D = docs/Tesis/Correcciones/dictamen-correcciones.md`.
> Verificacion de texto: `rg` sobre `S` y `B` (sin compilador LaTeX local).
> Verificacion de citas: `python3 "docs/Tesis/v9 (IA)/verify_citations.py"` y
> comparacion de `paper/main.bcf` contra `B`.
> Recompilacion: Overleaf (tarea final). No se edita `App/**`, ni c-67/c-76/c-77,
> ni `CHANGES.md`.

## 1. B1 — Reescribir la misatribucion de Revina et al. (2020)

- [x] 1.1 Reescribir `S/03-estado-del-arte.tex:28` (seccion 3.3) para presentar la conclusion real de Revina et al. (2020): metodos simples y explicables con rasgos linguisticos del dominio son competitivos; los embeddings preentrenados pueden rendir peor por vocabulario especifico del dominio. Verificar con `rg -ni "BERT|91~?%|preentrenad" S/03-estado-del-arte.tex` que no queda la atribucion falsa en la descripcion de Revina.
- [x] 1.2 Reescribir `S/08-discusion.tex:20` (seccion 8.2) eliminando "91 % con arquitecturas basadas en BERT" para Revina y reemplazando la comparacion por su resultado real. Verificar con `rg -ni "Revina|BERT" S/08-discusion.tex`.
- [x] 1.3 Reescribir `S/08-discusion.tex:22` para quitar "Frente al enfoque BERT de Revina (91 %)" e integrar la tension: la evidencia de Revina et al. es contraria a asumir transferencia trivial de modelos preentrenados, y se explica por que fortalece el analisis del LLM basado en tarea. Verificar con `rg -ni "BERT|91~?%" S/08-discusion.tex` sin coincidencias en contexto de Revina.
- [x] 1.4 Confirmar que la entrada `Revina2020_bert_tickets` en `B` conserva titulo/DOI reales y que su clave o comentario no reafirma "BERT" de forma enganosa (evaluar renombrar la clave y actualizar las citas, o dejar la clave con nota). Verificar con `rg -n "Revina2020" S B`.

## 2. B2 — Modernizar el estado del arte (2023-2026)

- [x] 2.1 Agregar a `B` al menos 12 entradas del anexo de `design.md` (verbatim), cubriendo (a) clasificacion de tickets / mesa de servicio con LLM, (b) evaluacion zero-shot/few-shot multilingue, (c) LLM en espanol/Iberoamerica. Verificar con `python3 -c` que cada entrada nueva tiene `doi` o `url` y `year >= 2023`.
- [x] 2.2 En `S/03-estado-del-arte.tex` (seccion 3.3) integrar las referencias nuevas de clasificacion de tickets con LLM y la linea multilingue/espanol; reemplazar la afirmacion sin cita de `:30` por una cita concreta (p. ej. `\textcite{ahuja2023mega}` / `\textcite{grandury2025laleaderboard}`). Verificar con `rg -n "ahuja2023mega|lai2023okapi|zhang2023multilingual|grandury2025laleaderboard" S/03-estado-del-arte.tex`.
- [x] 2.3 En `S/08-discusion.tex:20` reemplazar el rango sin cita "88 % a 94 %" por resultados concretos citados de las evaluaciones incorporadas, o retirarlo y reformular. Verificar con `rg -n "88~?\\\\?%|94~?\\\\?%|88 a 94" S/08-discusion.tex` y que toda cifra comparativa tenga `\cite`/`\textcite`/`\parencite` asociado.
- [x] 2.4 Declarar en `S/03-estado-del-arte.tex` (o en `S/08-discusion.tex`) la brecha: no existe articulo arbitrado 2023-2026 que evalue Google Gemini sobre tickets de soporte en espanol. Verificar con `rg -ni "Gemini" S/03-estado-del-arte.tex S/08-discusion.tex`.

## 3. B3 — Higiene de citas y atribucion

- [x] 3.1 Agregar la entrada `Landis1977_kappa` a `B` (DOI 10.2307/2529310) segun `design.md`. Verificar con `rg -n "Landis1977_kappa|10.2307/2529310" B`.
- [x] 3.2 En `S/04-marco-metodologico.tex:47` (seccion 4.4) citar `\parencite{Landis1977_kappa}` para los rangos y cambiar el rotulo de \(\kappa = 0{,}87\) de "sustancial" a "casi perfecto". Verificar con `rg -n "sustancial|casi perfecto|Landis1977_kappa" S/04-marco-metodologico.tex` (sin "sustancial").
- [x] 3.3 En `S/04-marco-metodologico.tex:79` (seccion 4.8, "Amenazas a la validez") citar `\parencite{Landis1977_kappa}` para los rangos y rotular "casi perfecto". Verificar con `rg -n "Landis1977_kappa|casi perfecto" S/04-marco-metodologico.tex`.
- [x] 3.4 En `S/04-marco-metodologico.tex:47` dejar `Cohen1960_kappa` solo para la definicion del coeficiente. Verificar con `rg -n "Cohen1960_kappa" S/04-marco-metodologico.tex` en contexto de definicion.
- [x] 3.5 En `B`, `Stallings2017_computer_security`: agregar `Brown, Lawrie` como co-autor. Verificar con `rg -n "Stallings, William and Brown" B`.
- [x] 3.6 En `B`, `OGC2011_itil`: quitar `edition = {2011}`; dejar `publisher = {The Stationery Office}` y agregar `note` sobre la titularidad AXELOS/PeopleCert. Verificar con `rg -n "OGC2011_itil|Office of Government Commerce|The Stationery Office" B`.
- [x] 3.7 En `B`, `Jurafsky2023_speech_language`: cambiar `publisher = {Pearson}` por `publisher = {Stanford University}` con `note` de borrador de la 3ra edicion. Verificar con `rg -n "Jurafsky2023_speech_language|Stanford" B` y sin "Pearson" en esa entrada.
- [x] 3.8 Coma antes del ano en las citas "et al." (APA: "Revina et al., 2020"): el preambulo (`preambles/preamble.tex:92`) ya carga `biblatex` con `style=apa`, que aplica la coma por diseno, por lo que NO se edita el preambulo. Auditar el fuente/PDF y normalizar solo cualquier pasaje manual sin coma. Verificar con `rg -n "et al\.? [0-9]{4}" S/` sin coincidencias.

## 4. Estado de citas huerfanas (resuelto) y guardia contra fabricaciones

Hallazgo verificado (2026-10-10): las dos citas huerfanas que reportaba la
auditoria estaban en la version **v7** (la version auditada) y eran **Karchhud et
al. (2024)** ("Few-shot ticket classification with large language models: A
multilingual evaluation", JISEM 9(2), 145-168) y **Mehdi et al. (2023)** ("The
state of AI in customer support: Industry adoption survey 2020-2023",
International Journal of Service Operations Management 45(3), 211-234). Ambas
fueron **verificadas como FABRICADAS** (Crossref/OpenAlex: cero resultados para
autores y titulos; el journal JISEM existe pero el articulo no; el segundo journal
es un near-miss del real "International Journal of Services and Operations
Management"). Ya fueron **retiradas entre v7 y v9**, por lo que v9 tiene cero citas
huerfanas. Estas referencias NO deben reintroducirse.

- [x] 4.1 Confirmar que `Karchhud` y `Mehdi` NO aparecen en el arbol v9 (ni en `B` ni en `S`). Verificar con `rg -n "Karchhud|Mehdi" "docs/Tesis/v9 (IA)"` sin coincidencias. Es la guardia de no reintroduccion.
  - **Evidencia (2026-10-19)**: `rg -n "Karchhud|Mehdi" "docs/Tesis/v9 (IA)"` devuelve **una sola coincidencia**, y NO es una cita: es el docstring explicativo de `docs/Tesis/v9 (IA)/verify_citations.py:18`, que menciona las dos fabricaciones de v7 para advertir que el script no las detecta. Ni `B` ni `S` contienen `Karchhud` ni `Mehdi`. Guardia de no reintroduccion OK.
- [x] 4.2 Re-verificar que **todas** las entradas restantes de `B` resuelven por DOI o URL de editorial/ACL Anthology (las fabricaciones suelen agruparse). Registrar el metodo de verificacion y listar cualquier entrada que no resuelva; retirarla o reemplazarla.
  - **Evidencia (2026-10-10)**: re-verificacion completa de las 33 entradas de `docs/Tesis/v9 (IA)/Bibliography_base.bib` por DOI/landing page. Resultado: **31 REAL, 2 METADATA WRONG, 0 FABRICADAS**. Las 2 con metadatos erroneos coinciden exactamente con el alcance de c-78: `Stallings2017_computer_security` (falta el co-autor Lawrie Brown, tarea 3.5) y `Jurafsky2023_speech_language` (sobra `publisher = {Pearson}`, tarea 3.7). Las 2 fabricaciones de v7 (Karchhud 2024, Mehdi 2023) estan **ausentes** de v9. `OGC2011_itil` es correcto como esta escrito (ITIL 2011 fue OGC/TSO; AXELOS asumio recien en 2013), solo el `edition = {2011}` es un uso cosmetico erroneo (tarea 3.6). El DOI de Landis & Koch (10.2307/2529310) resuelve correctamente. Cero entradas a retirar o reemplazar por este motivo.
  - **Evidencia (2026-10-19, re-verificacion de las 46 entradas de v9)**: metodo = parseo del `.bib` y resolucion de cada entrada con DOI contra la API de Crossref (`https://api.crossref.org/works/{doi}`, User-Agent explicito, reintentos ante HTTP 429). **22 entradas con DOI resueltas: 21 OK via Crossref + `Touvron2023_llama2` OK via DataCite** (10.48550/arXiv.2307.09288 no esta en Crossref; arXiv se resuelve por DataCite). **24 entradas sin DOI verificadas por pagina de aterrizaje de editorial/ACL**: 7 URLs con HTTP 200 (`Apache2024_airflow`, `n8n2024_docs`, `PostgreSQL2024_docs`, `Tiangolo2024_fastapi`, `Wiggins2017_12factor`, `Gomez2026_repositorio` + el resto de manuals); las obras monograficas/proceedings (`Brown2020_few_shot` NeurIPS, `Crispin2009_agile_testing` Addison-Wesley, `Date2003_database` Addison-Wesley, `HernandezSampieri2018_metodologia` McGraw-Hill, `Hohpe2003_eip` Addison-Wesley, `Jurafsky2023_speech_language` Stanford, `Ladas2009_scrumban` Modus Cooperandi, `Pedregosa2011_scikit_learn` JMLR, `Powers2011_evaluation` JMLT, `Pressman2020_software_engineering` McGraw-Hill, `Rabiner1993_speech_recognition` Prentice Hall, `Radford2023_whisper` ICML, `Russell2021_ai_modern` Pearson, `Stallings2017_computer_security` Pearson, `Vaswani2017_attention` NIPS, `OGC2011_itil` TSO) se confirman por editor/venue. **Unica URL con HTTP 403**: `Ley25326_2000` (portal oficial InfoLeg, `servicios.infoleg.gob.ar`) — es bloqueo anti-bot del dominio gubernamental, NO un enlace muerto. **Resultado: 46/46 resuelven, 0 FABRICADAS, 0 no resueltas, ninguna retirada.** No hay entradas a reemplazar.
- [x] 4.3 Ejecutar `python3 "docs/Tesis/v9 (IA)/verify_citations.py"` y la comparacion de las claves de `docs/Tesis/v9 (IA)/paper/main.bcf` contra `B` con `python3 -c`; confirmar STATUS PASS (33/33, cero huerfanas, cero sin usar) **antes** de agregar las referencias nuevas. Registrar ambas salidas.
  - **Evidencia (2026-10-19)**: `verify_citations.py` sobre el estado actual (46 entradas): `Summary: 46 bib entries, 46 unique keys cited, 76 total citation commands` / `Orphan citations: 0` / `Unused entries: 0` / `STATUS: PASS`.
  - **Nota `.bcf`**: `paper/main.bcf` es un artefacto **obsoleto** (compilado en julio, previo a las ediciones de c-78). La comparacion correcta de `<bcf:citekey>` contra `B` (46 claves) da 33 claves en el `.bcf`; las diferencias son exactamente los cambios aplicados: el `.bcf` stale aun cita la clave vieja `Revina2020_bert_tickets` (renombrada a `Revina2020_it_tickets`, tarea 1.4) y aun no contiene las 14 claves nuevas (`Landis1977_kappa` + 12 de B2 + la clave renombrada). El `.bcf` real solo se regenera en la recompilacion (diferida a Overleaf, 6.3). La fuente autoritativa en este punto es `verify_citations.py`.
- [x] 4.4 Tras las adiciones de B2 (2.1), re-ejecutar 4.3 y confirmar cero citas huerfanas y cero entradas sin usar con el nuevo total. Registrar la salida.
  - **Evidencia (2026-10-19)**: re-ejecucion post-adiciones = mismo resultado que 4.3, **con el nuevo total**: `46 bib entries, 46 unique keys cited, Orphan citations: 0, Unused entries: 0, STATUS: PASS`. Las 14 claves nuevas estan todas citadas en `S` y todas resuelven en `B`; cero huerfanas, cero sin usar.

## 5. Registro del dictamen

- [x] 5.1 Agregar a `D` la seccion `## Grupo: Bibliografia y atribucion (B1-B3)` mapeando B1/B2/B3 a los items 22/23/24 del plan, con la evidencia verificada (conclusion real de Revina, fuente Landis & Koch, lista candidata, citas huerfanas fabricadas Karchhud 2024 / Mehdi 2023 retiradas en v9). Verificar con `rg -n "Grupo: Bibliografia y atribucion|B1|B2|B3" D`.
  - **Evidencia (2026-10-19)**: la seccion `## Grupo: Bibliografia y atribucion (B1-B3)` ya existia (sesion previa, 2026-10-10) en `docs/Tesis/Correcciones/dictamen-correcciones.md:194`; se **actualizo en vez de duplicar**, agregando el bloque **"Estado de aplicacion de c-78 (2026-10-19)"** con: conclusion real de Revina (titulo "IT Ticket Classification: The Simpler, the Better" + DOI 10.1109/ACCESS.2020.3032840), clave renombrada a `Revina2020_it_tickets`, las 12 claves de B2 agregadas, la fuente Landis & Koch (DOI 10.2307/2529310) y el rotulo "casi perfecto", las 3 correcciones de metadatos B3, las fabricaciones Karchhud 2024 / Mehdi 2023 retiradas, y el resultado 46/46 PASS.

## 6. Verificacion final y recompilacion

- [x] 6.1 Barrido de control: `rg -ni "Revina.*BERT|BERT.*Revina|91 % con arquitecturas|88 % a 94 %|considerado sustancial|Karchhud2024|Mehdi2023" S` sin residuos. La clausula `Karchhud2024|Mehdi2023` es la guardia de no reintroduccion de las referencias fabricadas.
  - **Evidencia (2026-10-19)**: el barrido sobre `docs/Tesis/v9 (IA)/paper/sections` da **SIN RESIDUOS**. Un barrido ampliado (`Karchhud|Mehdi|sustancial`) solo detecta la palabra comun "sustancial/sustancialmente" en contextos ajenos a kappa (§1.2, §4.1, §5.3, §6.4, §7.6, §8.2, §8.7, §11.2) y ninguna mencion a Karchhud/Mehdi. En `04-marco-metodologico.tex`, \(\kappa = 0{,}87\) esta rotulado **"casi perfecto"** en §4.4 (`:47`, con `\parencite{Landis1977_kappa}`) y §4.8 (`:79`, "casi perfecto segun los rangos de Landis y Koch"); `Cohen1960_kappa` aparece solo en la definicion del coeficiente (`:47`). Cero residuos injustificados.
- [x] 6.2 Confirmar que `B` no contiene referencias fabricadas y que cada entrada nueva es verificable por DOI/URL; registrar el listado de claves agregadas.
  - **Evidencia (2026-10-19)**: `B` = 46 entradas, ninguna fabricada. Las **14 claves nuevas/renombradas** respecto de las 33 de v7: `Landis1977_kappa` (DOI 10.2307/2529310) y las 12 de B2 (`ahuja2023mega`, `lai2023okapi`, `zhang2023multilingual`, `xuan2025mmluprox`, `grandury2025laleaderboard`, `mayorrocher2026spanish`, `bernalbeltran2025mexicanspanish`, `ramonferrer2026tripletotext`, `paket2024itservice`, `liu2025tickit`, `zangari2023ticket`, `colavito2025benchmarking`), mas la renombrada `Revina2020_it_tickets`. Todas verificables: 13 por DOI resuelto (Crossref; `Touvron2023_llama2` via DataCite) y el resto por landing de editorial. Detalle en 4.2.
- [x] 6.3 Recompilar la tesis en Overleaf (`main.tex`, XeLaTeX) y verificar: PDF sin errores fatales, bibliografia con todas las entradas declaradas, cero citas huerfanas renderizadas, y longitud total <= 100 paginas. Registrar el conteo de paginas. — COMPLETADO 2026-10-20: recompilado localmente con MiKTeX (xelatex -> biber -> xelatex -> xelatex); 103 paginas; 0 errores fatales; 0 referencias indefinidas; 48/48 bibliografia; las 8 figuras renderizan. (latexmk no disponible: MiKTeX sin Perl.)
  - **DIFERIDO: se recompila en Overleaf (XeLaTeX)**. No se compila localmente; el `.bcf`/`.bbl` en repo son artefactos obsoletos hasta esa recompilacion.
- [x] 6.4 Ejecutar `openspec validate c-78-tesis-bibliografia-atribucion --strict` y confirmar que pasa.
