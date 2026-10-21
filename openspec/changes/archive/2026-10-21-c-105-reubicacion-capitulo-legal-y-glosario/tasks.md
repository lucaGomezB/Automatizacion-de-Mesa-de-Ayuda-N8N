# Tasks — c-105 — Reubicación del capítulo legal y glosario de siglas

## 0. Prerrequisitos (solo lectura)

- [x] 0.1 Confirmar en `main.tex` el orden actual de los `\input` (`11-aspectos-legales` después de `10-recomendaciones`) y registrar la línea base de `pdfinfo "docs/Tesis/v9 (IA)/paper/main.pdf" | grep Pages` (esperado: 103); verificación: ambas lecturas coinciden con la línea base.
- [x] 0.2 Confirmar que todas las remisiones son `\label`/`\autoref` y que `grep -rnE "\\label\\{sec:aspectos-legales\\}" "docs/Tesis/v9 (IA)/paper/sections/"` encuentra la etiqueta; verificación: sin remisiones duras nuevas (c-103 ya aplicado).
- [x] 0.3 Confirmar que `openspec/changes/c-105-reubicacion-capitulo-legal-y-glosario/.openspec.yaml` existe y que la rama de trabajo es la correcta; verificación: `git status` limpio antes de editar `.tex`.

## 1. Decisión de la nueva posición

- [x] 1.1 Registrar la decisión "antes de resultados, después de implementación" (design.md D1) y verificar que el dictamen la respalda: `grep -n "reubicar el capítulo legal\|antes de resultados" auditorias/Dictamen_Tesis_v9_CONEAU_2026-10-20.md`; verificación: la cita aparece.
- [x] 1.2 Identificar la posición destino exacta entre `06-implementacion` y `07-resultados` en `main.tex`; verificación: quedan anotadas las líneas de inserción.

## 2. Reordenamiento de los `\input`

- [x] 2.1 Mover `\input{sections/11-aspectos-legales.tex}` a entre `06-implementacion.tex` y `07-resultados.tex` en `main.tex`; verificación: `grep -n "input{sections/" main.tex` muestra el capítulo legal antes de resultados.
- [x] 2.2 Actualizar los comentarios/banners de numeración en `main.tex` y en la cabecera de `sections/11-aspectos-legales.tex` para reflejar la nueva posición; verificación: los comentarios coinciden con la numeración esperada.
- [x] 2.3 Verificar que no se renombró ningún archivo de `sections/` y que el cuerpo de `11-aspectos-legales.tex` no cambió salvo la cabecera; verificación: `git diff --stat` sobre `sections/` solo muestra el glosario y la cabecera.

## 3. Glosario de siglas

- [x] 3.1 Inventariar las siglas/acrónimos del cuerpo (`grep -rohE "\\b[A-Z]{2,}\\b" sections/*.tex | sort -u`), depurar falsos positivos y acordar la lista de entradas; verificación: la lista queda registrada con cada expansión.
- [x] 3.2 Crear `sections/00-glosario.tex` con la lista sigla → expansión en orden alfabético y su `\input` en el material preliminar, después de `\listoffigures` y antes del cuerpo; verificación: el archivo existe y el `\input` figura en `main.tex`.
- [x] 3.3 Asegurar que el glosario aparece en el índice general y no requiere un paso de build adicional; verificación: sin `\makeglossaries`/`\printglossaries` en el preámbulo y con entrada en TOC.

## 4. Verificación de compilación

- [x] 4.1 Compilar con `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`; verificación: el comando termina sin errores.
- [x] 4.2 Verificar cero referencias indefinidas y cero etiquetas duplicadas: `grep -iE "undefined reference|multiply defined label" "docs/Tesis/v9 (IA)/paper/main.log"`; verificación: sin coincidencias.
- [x] 4.3 Verificar la numeración recalculada y la posición en el índice general (`main.toc`): el capítulo legal figura antes de resultados y no después de conclusiones/recomendaciones; verificación: la secuencia del TOC es la esperada.
- [x] 4.4 Verificar el glosario en el PDF (`pdftotext` o lectura): aparece en material preliminar, con todas las entradas en orden alfabético; verificación: cada sigla inventariada en 3.1 tiene entrada.
- [x] 4.5 Verificar cobertura inversa: ninguna entrada del glosario queda sin uso en el cuerpo; verificación: `grep` de cada sigla del glosario contra `sections/*.tex` devuelve al menos una ocurrencia.
- [x] 4.6 Registrar el conteo final de páginas (`pdfinfo main.pdf | grep Pages`) y anotar la variación respecto de 103; verificación: el conteo queda documentado para c-107.

## 5. Verificación global

- [x] 5.1 Ejecutar `openspec validate c-105-reubicacion-capitulo-legal-y-glosario --strict`; verificación: pasa.
- [x] 5.2 Confirmar que NO se tocaron `Bibliography_base.bib` (c-104), tildes (c-106), números canónicos (c-107), métricas (c-108) ni figuras (c-80); verificación: `git status` no muestra esos archivos.
- [x] 5.3 Ejecutar `openspec status --change c-105-reubicacion-capitulo-legal-y-glosario --json`; verificación: la planificación figura completa y `applyRequires` resuelto.
