# Tasks — c-103 — Portada formal y remisiones cruzadas (Gate 0)

## 0. Prerrequisitos (solo lectura)

- [ ] 0.1 Confirmar la rama `RamaLuca` y que `docs/Tesis/v9 (IA)/paper/main.pdf` compila en 103 páginas antes del change (`pdfinfo main.pdf | grep Pages`).
- [ ] 0.2 Confirmar la existencia de `docs/Tesis/v9 (IA)/paper/assets/logo-utn-frm.png` (PNG 332×62 RGBA) y registrar su hash.
- [ ] 0.3 Registrar la línea base: `grep -rnoE '(Cap[íi]tulo|Secci[óo]n)[~ ]*[0-9]+' sections/ | wc -l` y `grep -rohE '\\label\{[^}]*\}' sections/ | sort -u | wc -l` (esperado: 23 labels).

## 1. Etiquetas de sección

- [ ] 1.1 Agregar `\label{sec:<slug>}` a cada `\section` de `sections/*.tex` que no lo tenga; verificar que el conteo de `\label{sec:` coincide con el de `\section{`.
- [ ] 1.2 Agregar `\label{subsec:<slug>}` a cada `\subsection` que no lo tenga; verificar el conteo equivalente.
- [ ] 1.3 Conservar `sec:metricas-multiclase` y `subsec:calibracion`; verificar que no hay etiquetas duplicadas (`grep -rohE '\\label\{[^}]*\}' sections/ | sort | uniq -d` vacío).

## 2. Conversión de remisiones

- [ ] 2.1 Convertir cada remisión dura "Capítulo N"/"Sección N.N" de prosa a `\autoref{...}`; definir `\sectionautorefname`/`\subsectionautorefname` como "Sección" en el preamble.
- [ ] 2.2 Corregir la remisión de `sections/07-resultados.tex:32` de "Sección~4.4" a la sección de métricas e instrumentos (4.6).
- [ ] 2.3 Estandarizar la prosa a "Sección" en lugar de "Capítulo".
- [ ] 2.4 Verificar cero remisiones duras: `grep -rnoE '(Cap[íi]tulo|Secci[óo]n)[~ ]*[0-9]+' sections/ | grep -v ':%' | wc -l` devuelve 0.

## 3. Portada y metadatos

- [ ] 3.1 Insertar `assets/logo-utn-frm.png` en `sections/00-portada.tex` y ajustar `\graphicspath` en el preamble para resolverlo.
- [ ] 3.2 Asegurar el rótulo "Trabajo Final de Carrera" y los autores Luca Gomez, Carla Bustos y Gonzalo Sevilla.
- [ ] 3.3 Reemplazar "Director: Prof. Alberto Cortez" por "Directores: Prof. Alberto Cortez y Prof. Ariel Enferrel".
- [ ] 3.4 Reemplazar el "2026" fijo por `\today`.
- [ ] 3.5 Cambiar `pdfsubject` a "Trabajo Final — Tecnicatura Universitaria en Programación" y revisar `pdftitle`/`pdfauthor`/`pdfkeywords`.

## 4. Nomenclatura

- [ ] 4.1 Renombrar las 6 ocurrencias de "Tesis de Grado" (preamble 2, 3, 85; main 2, 33; portada 2) revisando cada una.
- [ ] 4.2 Verificar que la ruta `docs/Tesis/Correcciones/` en `sections/12-anexos.tex` permanece intacta y que "hipótesis"/"síntesis" no se corrompen.

## 5. Verificación

- [ ] 5.1 Compilar con XeLaTeX y verificar `pdfinfo main.pdf | grep Pages` == 103.
- [ ] 5.2 Verificar el log: cero "undefined reference" y cero "multiply defined label".
- [ ] 5.3 Verificar la portada: logo presente, "Trabajo Final de Carrera", dos directores con "Prof." y fecha de compilación.
- [ ] 5.4 Verificar metadatos: `pdfsubject` con "Trabajo Final — Tecnicatura Universitaria en Programación".
- [ ] 5.5 Registrar la nota de seguimiento: el logo de 332 px es insuficiente para 300 dpi y se solicitará una versión ≥1200 px o vectorial (no bloquea el change).
- [ ] 5.6 Confirmar que NO se tocaron `Bibliography_base.bib`, ni tildes, ni contenido científico, ni se crearon figuras nuevas.

## 6. Verificación global

- [ ] 6.1 Ejecutar `openspec validate c-103-portada-formal-y-remisiones --strict` y confirmar que pasa.
- [ ] 6.2 Simular el movimiento del capítulo 11 (reordenar los `\input` en una copia de `main.tex`) y confirmar que ninguna referencia queda indefinida; descartar la copia.
