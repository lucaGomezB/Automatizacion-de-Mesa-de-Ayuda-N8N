## Why

La tesis corregida (v9) conserva defectos residuales de forma que ya se ven en el PDF compilado: un preambulo tabular roto imprime el literal `aggedright` (6 ocurrencias), una celda de la tabla de cumplimiento no cierra su intervalo de confianza, una remision usa un numero de tabla hardcodeado incorrecto, el indice rotula "Appendices" en ingles, Redis (retirado en c-62) sigue listado como servicio interno, y una afirmacion cuantifica 4 puntos de F1 sin medicion que la respalde. Son defectos de forma y consistencia que no tocan contenido ni numeros cientificos.

## What Changes

- Restaurar `\raggedright` en el preambulo de la tabla de tiempos (`07-resultados.tex`) para eliminar el literal `aggedright`.
- Cerrar el corchete del intervalo de confianza en la tabla de cumplimiento (`09-conclusiones.tex`).
- Reemplazar la remision literal `Tabla~5` por `\ref{tab:api}` al contrato REST real (`12-anexos.tex`).
- Rotular los anexos en espanol en el indice y la pagina de anexos (`preambles/preamble.tex`).
- Quitar Redis de la enumeracion de servicios internos (`05-arquitectura.tex`).
- Corregir/anotar la entrada de "Referencias bibliograficas" en el indice (`main.tex`).
- Rebajar a cualitativa la afirmacion de 4 puntos porcentuales de F1 sin medicion (`06-implementacion.tex`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos de correccion de defectos de forma del PDF (artefacto tabular, celda de tabla, remision cruzada, rotulo de anexos, servicios internos, entrada de indice) y de respaldo de afirmaciones cuantitativas.

## Impact

- Edita: `docs/Tesis/v9 (IA)/paper/sections/{05,06,07,09,12}-*.tex`, `docs/Tesis/v9 (IA)/paper/preambles/preamble.tex`, `docs/Tesis/v9 (IA)/paper/main.tex`.
- No toca: contenido cientifico, numeros canonicos, figuras, `Bibliography_base.bib`, memo, `CHANGES.md`, `dictamen-correcciones.md`.
- Presupuesto de paginas: cambios neutrales o reductores; el cuerpo MUST NOT superar las 100 paginas.
- El tag `v1.0.0` existente NO se mueve; un tag nuevo queda fuera de alcance.
