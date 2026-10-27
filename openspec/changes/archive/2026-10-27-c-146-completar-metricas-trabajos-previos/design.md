## Context

Este change cierra el remanente del criterio 3 y de la recomendacion B16 del dictamen CONEAU del 2026-10-22 (ver `proposal.md` - Why): c-135 completo cinco de las seis filas de `tab:trabajos-academicos` con los resumenes accesibles, pero dejo Colavito 2025 y Paket 2024 como "no reportado en el alcance revisado" por acceso cerrado (OQ-5 de c-135). Se verifico despues que el manuscrito aceptado (postprint) de Colavito, Lanubile y Novielli (2025) esta legitimamente alojado en acceso abierto por el grupo de los autores; sus metricas son extraibles sin credenciales. Ademas, Paramesh y Shreedhara (2019) tienen un trabajo companero de acceso abierto de los mismos autores sobre el mismo problema (Ramya, Paramesh y Shreedhara, arXiv:2103.15822, preprint de 2021 de un trabajo presentado en la 3rd IEEE CSITSS de 2018), cuyas metricas de clasicos son extraibles. Paket et al. (2024) no tiene copia ni alternativa accesible de sus autores (confirmado en OpenAlex y Semantic Scholar) y queda como seguimiento bloqueado; la extraccion directa de Paramesh (2019) sigue bloqueada por el acceso cerrado de su version editorial.

Abreviaturas: `S` = `docs/Tesis/v10 (IA)/paper/sections`, `C` = `docs/Tesis/Correcciones`.

**Restricciones:**

- **Sin fabricacion:** la regla de c-135 sigue vigente: solo cifras textuales de la fuente accesible (nombre de la metrica, valor y modelo o condicion), sin recalcular, promediar ni inferir.
- **Numeros canonicos congelados** (`C/numeros-canonicos.md`): ninguna cifra de resultados de la tesis cambia. Las cifras nuevas son metricas de una obra ajena, textuales de su fuente, y no entran en los capitulos de resultados.
- **Paginas:** el cuerpo del PDF no debe superar las 100 paginas vigentes (regla (b); anexos aparte). El capitulo 3 no tiene margen: cualquier linea agregada se compensa en el mismo capitulo (D6).
- **Derechos de autor:** no se versiona ninguna copia del articulo (D4).
- **Modo TDD estricto: no aplica** (cambio documental, sin codigo de produccion ni runner); la verificacion es por `rg`, `git diff`, `verify_citations.py` y conteo de paginas.

## Decisions

### D1 - Regla de extraccion (textual, con ubicacion)

La metrica consignada SHALL ser la que el manuscrito aceptado reporte textualmente; se registran el nombre de la metrica, el valor y el modelo o la condicion. No se recalcula, promedia ni infiere. Si la fuente no declara el dato (por ejemplo, el idioma de los corpus), la celda conserva "no reportado en el alcance revisado" con su motivo.

### D2 - Contenido exacto de las celdas de Colavito 2025

Fila de Colavito, Lanubile y Novielli (2025):

- **Celda "Metrica reportada"** (exacta, lista para el `.tex`):
  `macro-F1: BERT-like NLBSE'23 0,74 (RoBERTa) y 0,82-0,87 (SETFIT); NLBSE'24 0,79 (RoBERTa) y 0,82 (SETFIT). LLM zero-shot: 0,79-0,88 (NLBSE'23) y hasta 0,68 (NLBSE'24); BERT ajustado mas consistente`
- **Celda "Corpus/idioma"** (exacta):
  `dos datasets de issues de GitHub (NLBSE'23 y NLBSE'24, 1.500 issues); idioma: no reportado en el alcance revisado`
- La columna **"Enfoque"** se conserva ("benchmark de 22 LLM generativos + 2 BERT de base") y la **"Condición"** se conserva ("zero-shot vs. fine-tuning").
- Si el conteo de paginas de D6 lo exige, se admite acortar la celda de metrica a la forma compacta `macro-F1 BERT-like 0,74-0,87 (NLBSE'23) y 0,79-0,82 (NLBSE'24); LLM zero-shot 0,79-0,88 y hasta 0,68; BERT ajustado mas consistente`, conservando los valores; el detalle completo queda en el registro (D4).

### D3 - Linea de fuente de la tabla

La linea de fuente de `tab:trabajos-academicos` (`S/03-estado-del-arte.tex`) SHALL declarar la consulta del manuscrito aceptado. Se actualiza la fecha de consulta a 2026-10-26 y se conserva la mencion de "resumen y texto abierto". Cambio de longitud neutra o de reduccion (palanca de compensacion de D6).

### D4 - Registro de procedencia (seccion c-146)

Se agrega una seccion c-146 al final de `C/extraccion-metricas-trabajos-c-135.md`, sin reescribir sus secciones previas, con:

- **URL del manuscrito aceptado:** `https://collab.di.uniba.it/nicole/wp-content/uploads/sites/6/2025/05/Extended_Benchmark_LLM_4_Issue_Report_Classification__IST_Accepted.pdf` (grupo de los autores, Universidad de Bari).
- **Tipo de version:** manuscrito aceptado (postprint) de acceso abierto, 8 paginas.
- **Fecha de consulta:** 2026-10-26.
- **Valores extraidos y ubicacion:** las tablas de resultados del manuscrito (baselines tipo BERT y LLM generativos zero-shot por dataset). Se consigna por celda: obra, clave, DOI `10.1016/j.infsof.2025.107758`, URL, tipo de acceso, ubicacion (seccion y tabla), valor consignado y nota.
- **Seguimiento bloqueado:** Paramesh y Shreedhara (2019), DOI `10.1007/978-981-13-2514-4_28` (Springer, LNNS vol. 43, pp. 331-346) y Paket et al. (2024), DOI `10.1109/UBMK63289.2024.10773473` (IEEE UBMK 2024, pp. 135-140); ambos requieren acceso institucional (Biblioteca Electronica de Ciencia y Tecnologia / UTN).
- Se actualiza la linea de OQ-5 del encabezado para registrar que Colavito 2025 se resolvio por acceso abierto y que Paket 2024 sigue bloqueado.
- **No se versiona ninguna copia (PDF) del articulo.**

### D5 - Restricciones de acceso

- **Colavito 2025:** resuelto. El manuscrito aceptado es una version legitima de acceso abierto alojada por el grupo de los autores; es la unica fuente citada en la celda. No se usa la version editorial cerrada.
- **Paramesh 2019:** la obra original (capitulo Springer) sigue cerrada; sin copia de acceso abierto en Unpaywall, OpenAlex, Crossref, Semantic Scholar, OpenAIRE, arXiv, CORE ni DBLP. Su trabajo companero de acceso abierto (Ramya, Paramesh y Shreedhara, arXiv:2103.15822), en cambio, si es accesible y es la fuente que se cita (D10).
- **Paket 2024:** cerrado; sin copia de acceso abierto. OpenAlex `oa_status = closed`. Verificado en OpenAlex y Semantic Scholar: tampoco existe un trabajo alternativo accesible de sus autores que cuantifique el hallazgo (D11).
- No se evaden controles anti-bot. La extraccion directa de Paramesh 2019 y la de Paket 2024 quedan como tarea bloqueada (D7).

### D6 - Presupuesto de paginas (regla (b), cuerpo <= 100)

El cuerpo del PDF esta en el tope vigente (100) y el capitulo 3 no tiene margen. La celda de metrica de Colavito crece; el cambio SHALL ser neutral en paginas. Palancas en orden:

1. Redaccion compacta de la celda (D2, forma compacta).
2. Condensar la linea de fuente de la tabla (D3) o la celda "Condicion" de la misma fila, sin eliminar datos con fuente.
3. Si el desborde persiste, acortar una celda redundante del registro en el mismo capitulo, sin perder cifras de la tabla.

Verificacion obligatoria: recompilar con la misma cadena (XeLaTeX y biber) y contar el cuerpo del PDF (paginas totales menos anexos) con `pdfinfo`; debe ser <= 100. Se registran el conteo previo y el posterior.

### D7 - Tarea bloqueada (extraccion directa de Paramesh 2019 y Paket 2024)

La extraccion directa de la obra cerrada de Paramesh 2019 (Springer) y de Paket 2024 (IEEE) permanece bloqueada por falta de acceso institucional. Para Paramesh 2019 se agrega, ademas, el puntero a su companero accesible (D10); la fila conserva "no reportado en el alcance revisado (texto cerrado)" para la obra original. La tarea bloqueada lista los dos DOI y el acceso requerido, y su cierre depende de una decision externa (acceso institucional), no de este change.

### D8 - Gobernanza

Ediciones editoriales (`S/03-estado-del-arte.tex`, `Bibliography_base.bib`, `C/extraccion-metricas-trabajos-c-135.md`, `C/dictamen-correcciones.md`): **LOW** (el alta bibliografica es una entrada nueva verificada por DOI, no un cambio de las existentes). Delta de `tesis-document`: **MEDIUM** (se expone al usuario la redaccion del requisito antes de cerrar).

### D10 - Companero accesible de Paramesh (fila y prosa)

Paramesh y Shreedhara (2019) tienen un trabajo companero de acceso abierto de los mismos autores sobre el mismo problema: C. Ramya, S. P. Paramesh y K. S. Shreedhara, "Classifying the Unstructured IT Service Desk Tickets Using Ensemble of Classifiers", arXiv:2103.15822 (preprint, 2021; presentado en la 3rd IEEE CSITSS, 2018), DOI 10.48550/arXiv.2103.15822. Metricas verificadas en su texto completo (exactitud): arbol de decision 90,60 %, arbol de decision con bagging 92,04 %, RandomForest 91,81 %, voting 81,11 %, Naive Bayes multinomial 69,93 % (con bagging 70,17 %).

- **Celda "Metrica reportada"** (exacta, lista para el `.tex`):
  `no reportado en el alcance revisado (texto cerrado); companero accesible de los mismos autores (arXiv:2103.15822): arbol de decision 90,60\,\% y RandomForest 91,81\,\%`
- Se conservan las columnas "Enfoque" ("NB, LR, kNN y SVM"), "Corpus/idioma" y "Condicion" de la fila. Se conserva la frase cualitativa "SVM con buen desempeno" si el presupuesto de paginas (D6) lo admite; es la unica frase prescindible de la celda (su contenido ya esta en la prosa de `03:28`), y si se retira se documenta como uso de la palanca 3 de D6.
- **Prosa `03:28`**: se agrega una oracion con las dos metricas de titular, citando la clave nueva: `En su trabajo accesible sobre el mismo problema, \textcite{ramya2021classifying} reportan una exactitud de 90,60\,\% con arbol de decision y de 91,81\,\% con RandomForest.`
- Solo entran a la tesis las cifras de titular (arbol de decision 90,60 % y RandomForest 91,81 %) para acotar el crecimiento; el detalle completo queda en el registro (D4).

### D11 - Verdicto de Paket 2024 (fila sin cambios de contenido)

Paket et al. (2024) no tiene copia accesible ni una alternativa accesible de sus autores: OpenAlex `oa_status = closed` y en Semantic Scholar no se hallo un trabajo de los mismos autores que cuantifique el resultado. La fila permanece **cualitativa con su motivo** ("no reportado en el alcance revisado (texto cerrado); cualitativo: BERT supera a los LLM"). El hallazgo que la sustenta (los modelos tipo BERT por encima de los LLM generativos) queda cuantificado por la fila accesible de Colavito 2025, de modo que la tabla no pierde su valor comparativo. La verificacion se consigna en la seccion c-146 del registro.

### D12 - Alta bibliografica (unico cambio del `.bib`)

Se agrega **exactamente una** entrada nueva a `Bibliography_base.bib`:

```
@misc{ramya2021classifying,
  author        = {Ramya, C. and Paramesh, S. P. and Shreedhara, K. S.},
  title         = {Classifying the Unstructured {IT} Service Desk Tickets Using Ensemble of Classifiers},
  howpublished  = {arXiv preprint},
  eprint        = {2103.15822},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  note          = {arXiv:2103.15822; presentado en la 3rd IEEE International Conference on Computational Systems and Information Technology for Sustainable Solutions ({CSITSS}), 2018},
  year          = {2021},
  doi           = {10.48550/arXiv.2103.15822},
  url           = {https://arxiv.org/abs/2103.15822},
}
```

Tipo `@misc` por ser preprint (conforme a la spec de higiene de metadatos bibliograficos, que prohibe tipar un preprint de arXiv como `@article`). La clave sigue la convencion autor-ano-palabra de las claves recientes (`paket2024itservice`, `colavito2025benchmarking`). Ninguna entrada existente se modifica. El delta de `tesis-document` se ajusta para permitir esta unica alta (la live spec ya admite altas de fuentes nuevas que resuelvan por DOI).

## Open Questions

- **OQ-1 (RESUELTA 2026-10-26):** Colavito 2025 tiene un manuscrito aceptado de acceso abierto legitimo; su metrica se extrae. OQ-5 de c-135 queda parcialmente resuelta.
- **OQ-2 (BLOQUEADA):** acceso institucional a la obra original de Paramesh 2019 (Springer) y Paket 2024 (IEEE Xplore). Hasta obtenerlo, la extraccion directa de esas dos obras no se realiza; la fila de Paramesh agrega el puntero a su companero accesible (D10) y la de Paket permanece cualitativa (D11).
- **OQ-3 (RESUELTA 2026-10-26):** se adopta la forma de celda de Colavito de D2 y la celda de Paramesh de D10; la decision final de recorte por paginas se toma con la medicion (D6).
