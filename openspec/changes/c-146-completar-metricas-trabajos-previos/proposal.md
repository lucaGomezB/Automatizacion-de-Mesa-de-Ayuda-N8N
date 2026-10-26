# Proposal: Completar las metricas de la tabla de trabajos academicos previos (Colavito 2025)

## Why

El dictamen CONEAU del 2026-10-22 sobre la version de trabajo v10 (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`, aplicable a `v1.1.1`) descuenta al trabajo, en el criterio 3, que la tabla `tab:trabajos-academicos` consigne "no reportado en el alcance revisado" como metrica en cuatro de sus seis filas: "un estado del arte que compara trabajos sin extraer las metricas que ellos reportan tiene un valor comparativo limitado". La recomendacion B16 pide completar esas metricas a partir de las fuentes accesibles.

c-135 completo cinco filas con los resumenes accesibles, pero dejo Paket 2024 y Colavito 2025 sin metrica por acceso cerrado (OQ-5). Se verifico despues que el manuscrito aceptado (postprint) de Colavito, Lanubile y Novielli (2025) esta legitimamente alojado en acceso abierto por el grupo de los autores (Universidad de Bari). Sus cifras de F1 macro se pueden extraer sin credenciales institucionales. Paramesh y Shreedhara (2019) y Paket et al. (2024) siguen detras de Springer Link e IEEE Xplore y requieren acceso institucional que esta maquina no tiene; su extraccion directa queda explicitamente bloqueada.

Como paliativo para Paramesh y Shreedhara (2019), se identifico un trabajo companero de acceso abierto de los mismos autores sobre el mismo problema (C. Ramya, S. P. Paramesh y K. S. Shreedhara, "Classifying the Unstructured IT Service Desk Tickets Using Ensemble of Classifiers", arXiv:2103.15822, preprint 2021 de un trabajo presentado en la 3rd IEEE CSITSS de 2018). Su texto completo es accesible y reporta la exactitud de varios clasicos sobre tickets no estructurados de mesa de servicio. Paket et al. (2024), en cambio, no tiene copia accesible ni una alternativa accesible de sus autores (confirmado en OpenAlex y Semantic Scholar); su fila permanece cualitativa con su motivo, y el hallazgo que la sustenta (BERT por encima de los LLM generativos) queda cuantificado por la fila accesible de Colavito 2025.

## What Changes

- **Fila de Colavito 2025 (`03-estado-del-arte.tex`, `tab:trabajos-academicos`)**: completar la celda "Metrica reportada" con el F1 macro de los modelos tipo BERT y de los LLM generativos zero-shot, por dataset (NLBSE'23 y NLBSE'24), y la celda "Corpus/idioma" con los dos datasets de issues de GitHub (NLBSE'24, 1.500 issues). El idioma queda como "no reportado en el alcance revisado" porque el manuscrito aceptado no lo declara.
- **Fila de Paramesh y Shreedhara (2019) (`03-estado-del-arte.tex`)**: conservar "no reportado en el alcance revisado (texto cerrado)" y agregar un puntero compacto al trabajo companero accesible de los mismos autores (Ramya, Paramesh y Shreedhara, arXiv:2103.15822), con sus dos metricas de titular (arbol de decision 90,60 % y RandomForest 91,81 %), atribuidas explicitamente a ese trabajo. Ademas, la prosa de la subseccion (`03:28`) agrega una oracion con esas metricas, citando la clave nueva.
- **Fila de Paket et al. (2024) (`03-estado-del-arte.tex`)**: permanece cualitativa con su motivo de acceso cerrado; se registra en la procedencia que no tiene copia accesible ni alternativa accesible de sus autores (OpenAlex y Semantic Scholar) y que el hallazgo (BERT por encima de los LLM generativos) queda cuantificado por la fila de Colavito 2025.
- **Alta bibliografica (`Bibliography_base.bib`)**: agregar una unica entrada nueva para el trabajo companero accesible de Paramesh (`@misc`, arXiv:2103.15822, DOI 10.48550/arXiv.2103.15822). Es el unico cambio del `.bib`; ninguna entrada existente se modifica.
- **Registro de procedencia (`docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`)**: agregar una seccion c-146 con la URL del manuscrito aceptado de Colavito, su tipo de version (postprint aceptado), los valores extraidos y su ubicacion en el manuscrito; con la URL de arXiv:2103.15822 del companero de Paramesh, su tipo de version (preprint) y sus metricas; y con el verdicto de Paket 2024 (sin copia ni alternativa accesible). Se extiende el registro; no se reescribe su historia.
- **Delta spec `tesis-document`**: modificar el requisito "Completitud de las metricas de la tabla de trabajos academicos" para exigir que toda fila reporte su metrica de fuente o declare "no reportado en el alcance revisado" con su motivo, que las metricas de textos completos de acceso abierto se extraigan y su fuente se registre, que una obra cerrada pueda apuntar a un trabajo companero accesible de los mismos autores, y que las obras de acceso cerrado sin alternativa accesible permanezcan declaradas con su motivo.
- **Trazabilidad**: registrar el grupo c-146 en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se modifica el requisito "Completitud de las metricas de la tabla de trabajos academicos" (extraccion obligatoria de las metricas de todo texto completo de acceso abierto y declaracion con motivo de las obras de acceso cerrado, con su procedencia registrada).

## Impact

- **Edita:** `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex` (celdas de las filas de Colavito y de Paramesh, la prosa de la subseccion y la linea de fuente de `tab:trabajos-academicos`), `docs/Tesis/v10 (IA)/Bibliography_base.bib` (una unica entrada nueva, la del companero accesible de Paramesh), `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md` (seccion c-146) y `docs/Tesis/Correcciones/dictamen-correcciones.md` (grupo c-146).
- **No toca:** codigo de aplicacion (`App/`, `n8n/`, `scripts/`), `evaluation/`, `data/`, `docs/Tesis/Correcciones/numeros-canonicos.md` (ningun numero canonico cambia), las entradas del `.bib` de las claves existentes, las cinco cadenas de categoria, los capitulos de resultados (ninguna cifra nueva entra en ellos), la fila de Paket 2024 (permanece cualitativa con su motivo), `CLAUDE.md` ni `openspec/config.yaml`.
- **Paginas:** el cuerpo del PDF no debe superar las 100 paginas vigentes (regla (b); anexos aparte). La celda de metrica de Colavito crece; el cambio debe ser neutral en paginas con compensacion de longitud en el mismo capitulo y verificacion del conteo al recompilar.
- **Derechos de autor:** no se versiona ninguna copia del articulo. El registro guarda la URL, el tipo de version y las cifras extraidas; nunca el PDF.

## Governance

- **LOW** para las ediciones editoriales (dos `.tex`/`.md` de la tesis y el registro de procedencia).
- **MEDIUM** para el cambio de spec (delta de `tesis-document`): se implementa con checkpoint y se expone al usuario la redaccion del requisito antes de cerrar.

## Dependencies

- **c-135** (tabla `tab:trabajos-academicos` y registro de procedencia vigentes): este change los extiende.
- **c-139** (fila de Paramesh y atribuciones): deja la fila de Paramesh como "no reportado" (rama B); c-146 conserva esa declaracion y solo agrega un puntero al companero accesible de los mismos autores.
- **Acceso institucional** (OQ-5): requisito externo para desbloquear la extraccion directa de Paramesh 2019 y Paket 2024.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| La celda de metrica mas larga empuja el cuerpo por encima de 100 paginas | Media | Celda compacta, compensacion de longitud neutra en el capitulo 3 y conteo de paginas obligatorio al recompilar |
| Versionar el PDF del articulo (infraccion de derechos) | Baja | El registro guarda URL, tipo de version y cifras; ninguna copia del PDF entra al repositorio |
| Ampliacion de alcance hacia Paramesh y Paket | Media | Se explicita que la fila de Paramesh solo agrega un puntero al companero accesible de los mismos autores (su obra original sigue cerrada) y que la fila de Paket no se toca; los DOI de las dos obras cerradas quedan en el seguimiento |
| Atribuir al companero de Paramesh lo que es del capitulo original | Baja | El companero se identifica con sus propios autores (Ramya, Paramesh y Shreedhara) y su preprint; la fila conserva "no reportado" para la obra cerrada |
| Cifra mal atribuida a la fuente | Baja | Extraccion literal del manuscrito aceptado, con ubicacion registrada; sin recalcular, promediar ni inferir |

## Rollback

Revertir con `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib" docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md docs/Tesis/Correcciones/dictamen-correcciones.md` y recompilar el PDF. No hay migraciones, datos, codigo ni tags que revertir.

## Success Criteria

- [ ] La celda "Metrica reportada" de la fila de Colavito 2025 consigna el F1 macro de BERT-like y de LLM zero-shot por dataset, con procedencia en el registro.
- [ ] La celda "Corpus/idioma" de Colavito 2025 declara los dos datasets (NLBSE'24, 1.500 issues) y "no reportado" para el idioma.
- [ ] La fila de Paramesh y Shreedhara (2019) conserva "no reportado en el alcance revisado (texto cerrado)" y agrega el puntero al companero accesible con arbol de decision 90,60 % y RandomForest 91,81 %; la prosa de `03:28` cita la clave nueva.
- [ ] La fila de Paket 2024 permanece cualitativa y el registro declara su verdicto (sin copia ni alternativa accesible).
- [ ] Existe exactamente una entrada nueva en `Bibliography_base.bib` (el companero accesible de Paramesh, arXiv:2103.15822), citada y resuelta por DOI; ninguna entrada existente cambia.
- [ ] El registro de procedencia tiene una seccion c-146 con la URL del manuscrito aceptado (Colavito), la URL de arXiv:2103.15822 (companero de Paramesh), los valores extraidos y su ubicacion, y el verdicto de Paket.
- [ ] El delta de `tesis-document` pasa `openspec validate --strict`.
- [ ] El cuerpo del PDF compilado no supera las 100 paginas; sin errores fatales ni referencias indefinidas.
- [ ] `verify_citations.py` sin citas huerfanas ni entradas sin usar; la unica entrada agregada esta citada; ningun PDF de los articulos versionado.
