## Why

El dictamen CONEAU 2026-10-21 aprueba la tesis v9 y deja **7 observaciones de forma y completitud** que no comprometen el aporte central pero son abordables antes de la defensa: una sub-hipotesis no contrastada que se lee como laguna, afirmaciones sobre plataformas comerciales apoyadas solo en URLs al pie, un kappa sin intervalo de confianza ni declaracion de no computabilidad en el cuerpo, un umbral de "5.000 casos" sin justificar, un eje teorico de ASR sobredimensionado para un componente no implementado, un capitulo legal con dos secciones de nivel superior que desplaza la numeracion, y la fuente ausente del criterio del 85~\% del umbral de exactitud. Son correcciones documentales; no hay cambios de codigo de aplicacion.

## What Changes

- **Obs 1 - Sub-hipotesis de intervencion humana:** rotularla explicitamente como "no contrastada por ausencia de registro primario" en `00-resumen.tex`, `01-introduccion.tex`, `07-resultados.tex` y `09-conclusiones.tex`; **retitular** la subseccion homonima (`07-resultados.tex`) para que no prometa un resultado que no entrega. **BREAKING** de rotulo: el cambio de titulo altera la entrada del indice.
- **Obs 2 - Plataformas comerciales y precios:** incorporar referencias bibliograficas formales en `Bibliography_base.bib` para las afirmaciones sobre plataformas (Zendesk, Freshdesk, ServiceNow), DigitalOcean y Vertex AI, o reformularlas como observacion propia; ajustar las citas en `03-estado-del-arte.tex`, `10-recomendaciones.tex` y `11-aspectos-legales.tex`.
- **Obs 3 - Intervalo de confianza del kappa:** verificar si la tabla de doble etiquetado es recuperable; si lo es, reportar el IC (bootstrap con semilla fija); en su defecto, conservar y elevar al cuerpo la declaracion explicita de no computabilidad. Decision registrada en `design.md`.
- **Obs 4 - Umbral de 5.000 casos:** justificarlo o degradarlo a referencia indicativa explicita de orden de magnitud en `10-recomendaciones.tex`.
- **Obs 5 - Eje de ASR:** recortar la subseccion de reconocimiento automatico del habla al minimo conceptual en `02-marco-teorico.tex`.
- **Obs 6 - Estructura del capitulo legal:** evaluar la fusion de las dos secciones de nivel superior en `11-aspectos-legales.tex` a una sola (numeracion limpia) y revisar los comentarios internos de numeracion en `main.tex` y `sections/*.tex`.
- **Obs 7 - Fuente del umbral del 85~\%:** declarar la fuente del criterio que hoy se apoya en "mediciones organizacionales preliminares" sin cita en `01-introduccion.tex`, o reformular el criterio como estimacion propia declarada.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos de cierre de las 7 observaciones finales del dictamen (rotulo de la sub-hipotesis no contrastada, trazabilidad bibliografica de afirmaciones comerciales, declaracion del IC del kappa, umbral de migracion como referencia indicativa, acotacion del eje de ASR, numeracion del capitulo legal y trazabilidad de la fuente del umbral del 85~\%). Se preservan los numeros canonicos y el presupuesto de paginas (<= 101).

## Impact

- Edita: `docs/Tesis/v9 (IA)/paper/sections/{00-resumen,01-introduccion,02-marco-teorico,03-estado-del-arte,07-resultados,09-conclusiones,10-recomendaciones,11-aspectos-legales}.tex`, `docs/Tesis/v9 (IA)/paper/main.tex`, `docs/Tesis/v9 (IA)/Bibliography_base.bib`.
- No toca: codigo de aplicacion (`App/Backend`, `App/Frontend`, `n8n/`), numeros canonicos, las cinco cadenas de categoria, figuras, `evaluation/`, `CHANGES.md`.
- Presupuesto de paginas: criterio duro. La tesis debe permanecer en <= 101 paginas; obs 5 (recorte) y obs 6 (restructura) reducen o son neutrales; obs 2 (referencias) MUST NOT agregar paginas netas.
- El tag `v1.0.0` existente NO se mueve; un tag nuevo queda fuera de alcance.
