## Why

El dictamen CONEAU del 2026-11-13 formulo dos observaciones vinculadas sobre la tesis v10 (release `v1.3.0`). En la seccion de trabajos futuros, el orden de las subsecciones no sigue la prioridad declarada y, salvo un item, ninguno trae criterio de exito ni tamano de muestra; el resto es una lista de ampliaciones de producto sin relacion con ninguna limitacion medida, y la seccion informa ademas un resultado ---la validacion fuera de muestra--- que corresponde a resultados. Por separado, la clase medida mas debil del clasificador (`Sistemas`, F1 0,2222 sobre 5 casos, con 3 de 5 predichos como `Soporte Tecnico Software`) no se declara de forma explicita como tal. Ambas observaciones son editoriales, corregibles antes de la defensa, y ninguna exige evidencia nueva.

## What Changes

- Declarar explicitamente, en la discusion y en las conclusiones, que `Sistemas` es la clase medida mas debil: F1 0,2222 sobre un soporte de 5 casos, con confusion sistematica con `Soporte Tecnico Software` (3 de 5), soporte pequeno que vuelve imprecisa la estimacion. Su frontera con `Soporte Tecnico Software` es un problema de taxonomia o de criterio de etiquetado antes que de capacidad del clasificador; el proximo paso de medicion es el sobremuestreo de las dos clases adyacentes con doble etiquetado y arbitraje. No se afirma que el clasificador vaya a mejorar.
- Reordenar las subsecciones de `10-recomendaciones.tex` por la prioridad declarada y fundamentar cada item: atarlo a una limitacion medida (con su cifra) o darle criterio de exito y/o tamano de muestra.
- Retirar de la seccion de trabajos futuros los resultados de la validacion fuera de muestra (exactitud 0,8447 sobre el n efectivo de 103 con 47 discordantes excluidos); la seccion solo conserva el trabajo futuro derivado y remite a resultados para las cifras.
- Degradar a un unico parrafo rotulado "ampliaciones de producto no derivadas de una limitacion medida" los items de expansion de producto: canales de mensajeria, panel de monitoreo, integracion con inventario/CMDB, base de conocimientos, automatizacion de la resolucion tecnica y agente conversacional telefonico.

**BREAKING**: ninguna. No cambia ninguna cifra canonica, metrica, ni artefacto de datos.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agrega el requisito de que la tesis declare de forma explicita la clase medida mas debil con su cifra y su frontera taxonomica, ordene los trabajos futuros por la prioridad declarada, fundamente cada item en una limitacion medida o en un criterio de exito/tamano de muestra, y no informe la validacion fuera de muestra como trabajo futuro.

## Impact

- Tesis: seccion 10 (`docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex`) como archivo principal; seccion 08 (`08-discusion.tex`) y seccion 09 (`09-conclusiones.tex`) solo para el statement explicito de `Sistemas` y el punto de frontera/taxonomia.
- No se toca: `01-introduccion.tex`, `02-marco-teorico.tex`, `03-estado-del-arte.tex`, `04-marco-metodologico.tex`, `12-anexos.tex`, `00-glosario.tex`, `Bibliography_base.bib`, `11-aspectos-legales.tex` (los posee otro workstream); `07-resultados.tex` (ya contiene las cifras por clase y de la validacion fuera de muestra); `App/`, `n8n/`, `evaluation/`, el clasificador, el corpus (`data/*.json`, `data/*.csv`) y las versiones archivadas de la tesis.
- No se recompila el PDF (`main.pdf`, `compilacion.md`): compilan los autores.
- Gobernanza: MEDIA (texto academico; no toca datos, seguridad, autenticacion ni facturacion). Restriccion dura: ninguna cifra canonica cambia.
- Metricas: sin cambios.
