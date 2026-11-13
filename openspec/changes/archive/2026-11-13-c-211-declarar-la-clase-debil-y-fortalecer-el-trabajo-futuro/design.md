# Design: Declarar la clase debil y fortalecer el trabajo futuro (change c-211)

## Context

Ver `proposal.md` --- Why. Estado verificado al proponer (2026-11-13), sobre `main`:

- `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` tiene catorce subsecciones. Su parrafo introductorio declara tres niveles de prioridad (defectos medidos; fortalecimiento de la evidencia o del clasificador; extensiones funcionales), pero el orden de las subsecciones no los respeta: items de prioridad 3 (`cola-respaldo`, `ampliacion-canales`, `panel-monitoreo`, `integracion-inventario`) aparecen antes de items de prioridad 2 (`aprendizaje-activo`, `corpus-independiente`, `estudios-replicacion`, `evaluacion-modelos-abiertos`).
- La subseccion `corpus-independiente` (linea 44) informa un resultado: la validacion fuera de muestra (0,8447; IC de Wilson [0,7625; 0,9021]; 150 casos; n efectivo 103; 47 discordantes excluidos). Ese resultado ya esta en `07-resultados.tex` (subseccion `subsec:resultados-campana-medicion`, tabla `tab:fuera-de-muestra`) y en `08-discusion.tex` y `09-conclusiones.tex`.
- El artefacto versionado `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json` fija las figuras por clase: `Bases de Datos` 0,9630 (soporte 13), `Soporte Tecnico Hardware` 0,9048 (40), `Seguridad Informatica` 0,8333 (21), `Soporte Tecnico Software` 0,8000 (24), `Sistemas` 0,2222 (5); macro-F1 0,7447; exactitud estricta 0,8447 (87/103). En `frontera_confusion`, 3 de los 5 casos de `Sistemas` se predijeron como `Soporte Tecnico Software`. `07-resultados.tex:284` ya reproduce esas figuras por clase, incluida `Sistemas` 0,2222 (0,2500; 0,2000; 5). `08-discusion.tex:26` discute la confusion de `Sistemas` dentro de la muestra (16 casos asignados) sin el encuadre fuera de muestra ni el proximo paso de medicion.
- Solo `subsec:cola-respaldo` esta referenciado desde otro archivo (`06-implementacion.tex:60`). Los demas labels de producto (`ampliacion-canales`, `panel-monitoreo`, `integracion-inventario`, `base-conocimientos`, `automatizacion-resolucion`, `agente-conversacional`) solo se referencian dentro de `10-recomendaciones.tex`.
- `python3 docs/Tesis/v10 (IA)/verify_citations.py` reporta `STATUS: PASS` (91 entradas, 91 claves citadas, 0 huerfanas, 0 sin usar) al inicio del change.
- No se recompila el PDF (`main.pdf`, `compilacion.md`): lo compilan los autores.

## Goals / Non-Goals

**Goals:**

- Declarar de forma explicita y sin atenuantes la clase medida mas debil (`Sistemas`) con sus cifras verbatim del artefacto versionado, su frontera taxonomica y un proximo paso de medicion concreto.
- Ordenar las subsecciones de trabajos futuros por la prioridad declarada y fundamentar cada item en una limitacion medida o en un criterio de exito/tamano de muestra.
- Retirar de trabajos futuros el resultado de la validacion fuera de muestra.
- Rotular honestamente las ampliaciones de producto que no derivan de una limitacion medida.

**Non-Goals:**

- No se cambia ninguna cifra, metrica, ni los archivos del corpus (`data/*.json`, `data/*.csv`).
- No se toca `App/`, `n8n/`, `evaluation/` ni el clasificador.
- No se tocan los archivos que posee el otro workstream (`01`, `02`, `03`, `04`, `11`, `12`, `00-glosario`, `Bibliography_base.bib`).
- No se recompila el PDF.
- No se tocan las versiones archivadas de la tesis.

## Decisions

### D1. Orden de las subsecciones por la prioridad declarada

El parrafo introductorio se reescribe para declarar la prioridad de forma explicita y ordenada, y el orden de las subsecciones lo sigue:

1. **Prioridad 1 --- atacan defectos medidos:** calibracion del gate de confianza (`subsec:calibracion-gate`); clasificador supervisado con corpus propio (`subsec:clasificador-supervisado`).
2. **Prioridad 2 --- fortalecen la evidencia o el clasificador:** medicion de la frontera `Sistemas`/`Soporte Tecnico Software` (nueva, `subsec:frontera-sistemas`); medicion continua de la intervencion humana (`subsec:medicion-intervencion`); validacion sobre un corpus independiente (`subsec:corpus-independiente`); aprendizaje activo (`subsec:aprendizaje-activo`); estudios de replicacion (`subsec:estudios-replicacion`); evaluacion de modelos abiertos (`subsec:evaluacion-modelos-abiertos`).
3. **Prioridad 3 --- extensiones funcionales:** cola de respaldo y alta asincronica (`subsec:cola-respaldo`), y el parrafo rotulado de ampliaciones de producto (nuevo, `subsec:ampliaciones-producto`).

Alternativa descartada: mantener el orden actual y solo anadir criterios. Se descarta porque el dictamen senala especificamente que el orden no sigue la prioridad declarada; reordenar es la correccion solicitada por la recomendacion 15.

### D2. Degradar las ampliaciones de producto a un unico parrafo, no eliminarlas

Los seis items de expansion de producto (canales de mensajeria, panel de monitoreo, inventario/CMDB, base de conocimientos, automatizacion de la resolucion, agente conversacional) se degradan a un unico parrafo rotulado "ampliaciones de producto no derivadas de una limitacion medida". Se conserva su contenido en prosa breve, sin subsecciones ni labels.

Se elige degradar en lugar de eliminar por tres razones. Primera, la recomendacion 15 admite ambas lecturas ("quitar o fundamentar"); el rotulo explicito satisface el objetivo del dictamen sin borrar lineas que el documento declara como trabajo futuro. Segunda, eliminar seis subsecciones reduce el alcance declarado de la tesis en la recta final de entrega, con riesgo de que un miembro del tribunal lo lea como una perdida de contenido. Tercera, varias de esas subsecciones se referencian entre si dentro de `10-recomendaciones.tex`; al colapsarlas en un parrafo se eliminan los labels y sus referencias internas, sin romper referencias externas (las unicas externas son a `subsec:cola-respaldo`, que se conserva).

Alternativa descartada: eliminar por completo los seis items. Se descarta por el motivo de contenido de la segunda razon. Alternativa descartada: dejar `integracion-inventario` y `automatizacion-resolucion` como subsecciones con criterio de exito. Se descarta porque ambos derivan de la base de conocimientos (a su vez sin limitacion medida) y mantenerlos como subsecciones contradiria la rotulacion de que no derivan de una limitacion medida.

### D3. Retirar de trabajos futuros el resultado de la validacion fuera de muestra

La subseccion `corpus-independiente` se reescribe para conservar solo el trabajo futuro: repetir la validacion sobre otros corpus, con muestras mayores y sin el sesgo de exclusion, y el sobremuestreo de las clases adyacentes. Las cifras (0,8447, macro-F1 0,7447, n efectivo 103, 47 excluidos) se remiten a `07-resultados.tex` (subseccion `subsec:resultados-campana-medicion`) y no se re-informan. El texto conserva la afirmacion de la limitacion (que el vocabulario y las reglas se ajustaron sobre el mismo corpus) porque es una limitacion, no un resultado.

Alternativa descartada: dejar una mencion minima de la cifra para contexto. Se descarta porque el dictamen senala que la seccion "informa un resultado"; la instruccion es sacarla, y la cifra ya esta en resultados.

### D4. Ubicacion del statement de `Sistemas`

El statement explicito de la clase debil se agrega en la discusion (`08-discusion.tex`), en la subseccion "Interpretacion de los resultados", inmediatamente despues del parrafo sobre la confusion de `Sistemas` en la muestra; y se cierra con una mencion breve en las conclusiones (`09-conclusiones.tex`). `07-resultados.tex` ya reproduce las figuras por clase con su soporte; no se modifica para no mover cifras ni tocar un archivo que ya las contiene. La subseccion nueva de trabajos futuros (`subsec:frontera-sistemas`) tambien referencia el statement.

Alternativa considerada: colocar el statement solo en resultados. Se descarta porque el enfasis pedido es que la debilidad se lea como un hallazgo interpretado, no como una linea de tabla.

### D5. Cifras verbatim del artefacto; ninguna cifra nueva

Todas las cifras del statement (`Sistemas` 0,2222; soporte 5; 3 de 5 predichos como `Soporte Tecnico Software`; macro-F1 0,7447; exactitud 0,8447; n efectivo 103; 47 excluidos) se toman verbatim de `analisis_fuera_de_muestra_c205.json`. No se introduce ninguna cifra que no este en un artefacto versionado. Si hiciera falta una cifra ausente, el change se detiene y pregunta; no se inventa.

### D6. Gobernanza MEDIA: solo redaccion, sin datos ni seguridad

El cambio es de gobernanza MEDIA (texto academico). Restriccion dura: no se modifica ninguna cifra canonica, ningun artefacto de datos, ni el clasificador. La verificacion final compara el diff y confirma que las cifras por clase y de la validacion coinciden con el artefacto.

## Risks / Trade-offs

- **Mover una cifra por descuido** -> la verificacion final compara las cifras del texto con `analisis_fuera_de_muestra_c205.json`; el diff no debe introducir cambios numericos.
- **Romper una referencia a un label** -> solo `subsec:cola-respaldo` es externa y se conserva; las referencias internas a los labels degradados se eliminan junto con ellos.
- **Degradar de mas y perder contenido** -> D2 conserva el contenido en un parrafo rotulado, no lo borra.
- **Statement que parezca promesa de mejora** -> D4 y la redaccion prohiben explicitamente afirmar que el clasificador mejorara; se declara la debilidad y se propone medirla.
- **Tocar archivos fuera de alcance** -> la verificacion de alcance (`git status`) restringe el change a `10-recomendaciones.tex`, `08-discusion.tex`, `09-conclusiones.tex` y los artefactos del change.

## Migration Plan

No hay migracion de datos: el cambio es editorial. Rollback: revertir los tres `.tex`. El corpus y las metricas no se tocan, por lo que el rollback no afecta la evidencia.

## Open Questions

None.
