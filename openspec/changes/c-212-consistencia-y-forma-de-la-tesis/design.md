# Design: Consistencia y forma de la tesis (change c-212)

## Context

Ver `proposal.md` — Why. El dictamen v1.3.0 califica el documento escrito con 7,83 y proyecta 8,05 tras las seis recomendaciones necesarias. Las recomendaciones de consistencia (7 a 12) y de forma (13 y 14) no requieren evidencia nueva: son correcciones de redaccion, estructura, glosario y bibliografia. El trabajo se hace sobre la fuente LaTeX de `docs/Tesis/v10 (IA)/paper/sections/` y `Bibliography_base.bib`, sin recompilar el PDF ni tocar cifras canonicas.

Restricciones duras verificadas antes de escribir:

- Cifras canonicas intocables: macro-F1 0,7447, exactitud estricta 0,8447, IC [0,7625; 0,9021], kappa 0,7862 / 0,6055, 71,2 % / [67,2 %; 74,6 %], balance 28/138, paginas.
- El parrafo de consentimiento E3/E4 de `11-aspectos-legales.tex` (linea 38) lo edita otro flujo de trabajo: no se toca.
- `07-resultados.tex`, `08-discusion.tex` y `09-conclusiones.tex` quedan fuera del alcance.
- No se toca `.engram/`, `evaluation/**`, `App/**`, `n8n/**` ni `data/**`.

## Goals / Non-Goals

**Goals:**

- Hacer explicita la asimetria de la regla de tres vias y el caracter posterior del denominador.
- Separar el enunciado de las sub-hipotesis de su veredicto y unificar la posicion sobre el umbral del 85 %.
- Reformular los objetivos 1 y 3 para que sean consistentes con la implementacion y medibles.
- Retirar la prosa de control de versiones y las rutas internas del cuerpo; reducir el Anexo I.
- Fundamentar en el marco teorico el acuerdo entre anotadores, la clasificacion multietiqueta y las pruebas estadisticas.
- Justificar la posicion del capitulo legal sin moverlo.
- Actualizar la bibliografia y completar el glosario.
- Suavizar la afirmacion de vacancia del corpus en espanol.

**Non-Goals:**

- No se cambia ninguna cifra canonica, metrica ni artefacto de evaluacion.
- No se recompila el PDF ni se regeneran `main.pdf`/`compilacion.md`.
- No se mueve el capitulo legal ni se renumeran capitulos.
- No se tocan las conclusiones, el resumen ni la discusion.
- No se agregan fuentes nuevas ni DOI inventados.

## Decisions

### D1. Regla de tres vias asimetrica declarada en introduccion y metodologia

En `01-introduccion.tex` y en `04-marco-metodologico.tex` se agrega una oracion explicita: la rama de refutacion se decide con la estimacion puntual y no con el intervalo, de modo que basta que aquella alcance o supere la cota. Se conserva la definicion de las tres ramas y la constancia de que el denominador de 147 casos revisados se adopto despues de conocer los datos. Alternativa descartada: cambiar la regla por una simetrica. Se descarta porque alteraria el criterio de falsacion ya declarado y su veredicto, que el texto sostiene.

### D2. Enunciado sin veredicto y umbral como criterio central del estudio

En `01-introduccion.tex:32-38` se conservan el enunciado de cada sub-hipotesis, su contraste y su criterio de falsacion; se retiran las oraciones de veredicto ("se declara confirmada/refutada/no concluyente") y los resultados observados, con remision a resultados. El umbral del 85 % se unifica como criterio de exito central del estudio, fijado a priori por los autores; se elimina la frase que lo degradaba a "criterio de exito contingente" y que lo sacaba de la definicion del objetivo. La literatura sigue descripta como incapaz de fijar un piso comun, pero el umbral no se presenta como tomado de ella. Alternativa descartada: degradar el umbral en la pregunta y en la tercera sub-hipotesis. Se descarta porque obligaria a reescribir el veredicto de la tercera sub-hipotesis y sus remisiones.

### D3. Objetivos 1 y 3 medibles y consistentes con la implementacion

El objetivo 1 pasa de "comunicacion asincronica" a "comunicacion sincronica", que es lo que la implementacion y las conclusiones declaran. Del objetivo 3 se retira la clausula "sin incrementar la complejidad operativa percibida por los usuarios finales", para la que no existe metrica ni instrumento. Alternativa descartada: definir un instrumento de percepcion. Se descarta porque exigiria trabajo de campo nuevo y no hay datos.

### D4. Higiene de prosa de proceso y Anexo I reducido

Se retiran las dos oraciones "Una version anterior de esta tesis la declaro refutada" (`01-introduccion.tex:34` y `04-marco-metodologico.tex:81`) y la ruta interna del repositorio en `03-estado-del-arte.tex:8`. El Anexo I (`12-anexos.tex`, `sec:anexo-trazabilidad`) se reduce a la nota de versiones y a un parrafo breve que remite la trazabilidad operativa al repositorio; se eliminan las seis tablas de dictamenes y la tabla de la devolucion de segunda instancia. Se conserva la divulgacion de asistencia de un modelo de lenguaje. Las etiquetas `sec:anexo-trazabilidad` y `subsec:nota-versiones` se conservan para que las remisiones externas sigan resolviendo. Alternativa descartada: eliminar la seccion completa. Se descarta porque romperia `\autoref{sec:anexo-trazabilidad}` usado en metodologia, resultados y discusion.

### D5. Fundamentos teoricos previos a la evidencia

Se agregan tres subsecciones al final de `02-marco-teorico.tex`: acuerdo entre anotadores y coeficiente kappa (Cohen, Landis y Koch, Fleiss), clasificacion multietiqueta (Tsoumakas) y pruebas estadisticas de contraste (Wilcoxon, Wilson, bootstrap, McNemar). Se actualiza la frase introductoria de "ocho ejes tematicos" al nuevo conteo. Solo se citan claves ya presentes en `Bibliography_base.bib`, de modo que el verificador de citas no cambie su conjunto. Alternativa descartada: insertar los conceptos dentro de la metodologia. Se descarta porque el dictamen pide sustento teorico previo.

### D6. Posicion del capitulo legal justificada, no movida

Se agrega una oracion al inicio de `11-aspectos-legales.tex` que explica que el capitulo se ubica entre implementacion y resultados porque las condiciones legales y eticas del tratamiento de datos condicionan la lectura de la evidencia. No se mueve el capitulo: la especificacion vigente `Ubicacion del capitulo de consideraciones eticas y legales` ya fija esa posicion, y moverlo el dia de la entrega arriesga `\autoref` y la base de paginas.

### D7. Bibliografia: version, tipos de entrada, pagina y DOI

Se actualiza `Gomez2026_repositorio` a la version 1.3.0. Se convierten a `@inproceedings` las tres entradas PMLR cargadas como `@article` (Radford 2023, Guo 2017, Zhao 2021), conservando volumen, paginas y URL. Se agrega `p.~243` a la atribucion de Zanzotto, pagina verificada contra el PDF del articulo (`citation_firstpage` = 243). Los siete DOI de 2025 y 2026 se verificaron contra `doi.org`: los siete resuelven con redireccion 302 al editor. No se modifica ningun DOI.

### D8. Glosario completo

Se agregan iPaaS, SaaS, kNN y CoT en su posicion alfabetica. Para no desalinear la tabla de dos columnas, cada entrada nueva ocupa una fila con la celda opuesta vacia; el orden de lectura de cada columna se conserva. Se actualiza el comentario de cabecera del glosario.

### D9. Vacancia del corpus en espanol acotada a la evidencia

En `01-introduccion.tex` se reemplaza "ninguno declara un corpus en espanol" por una formulacion que reconoce que el idioma no se informa en la mayoria de los trabajos y que, entre los que lo consignan, ninguno declara espanol; se aclara que la ausencia se limita al alcance revisado. No se fortalece ninguna afirmacion.

## Risks / Trade-offs

- **Romper remisiones al reducir el Anexo I** -> se conservan `sec:anexo-trazabilidad` y `subsec:nota-versiones`; las etiquetas de las tablas eliminadas solo se referenciaban dentro del bloque eliminado (verificado con `rg`).
- **Desalinear el glosario** -> cada entrada nueva va en una fila con celda opuesta vacia; el orden alfabetico de cada columna se mantiene.
- **Introducir una fuente inexistente** -> solo se usan claves existentes; el verificador de citas debe quedar en PASS.
- **Tocar el parrafo E3/E4** -> se edita `11-aspectos-legales.tex` solo en su encabezado; el parrafo de consentimiento no se modifica.
- **Residuos fuera de alcance** -> las frases "una version anterior..." de `07-resultados.tex:159` y `08-discusion.tex:8` quedan intactas por estar fuera del alcance autorizado; se reportan como residuales.

## Migration Plan

No hay migracion de datos: el cambio es editorial. Rollback: revertir los `.tex` y el `.bib` afectados. Ninguna cifra ni artefacto de evaluacion cambia.

## Open Questions

None.
