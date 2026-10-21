## 1. Preparación y baseline

- [ ] 1.1 Confirmar el estado del archivo y sus líneas: leer `docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex` y verificar que `03:24`-`03:34` y `tab:comparativa` están en el estado descrito en `design.md`.
- [ ] 1.2 Medir el baseline de páginas: compilar con la imagen `texlive-thesis` (`latexmk main.tex`) y registrar `pdfinfo main.pdf | grep Pages` (esperado 100).
- [ ] 1.3 Verificar que no existe una tabla académica previa ni colisión con `tab:comparativa`; registrar el resultado en las tareas.

## 2. Tabla comparativa

- [ ] 2.1 Redactar la tabla `tab:trabajos-academicos` con las columnas `trabajo | enfoque | corpus/idioma | métrica reportada | condición` y las seis filas de `design.md` D2, con booktabs y `\small`; verificar que compile sin errores de entorno.
- [ ] 2.2 Completar cada celda según la procedencia de `design.md` D4; marcar como "no reportado en el alcance revisado" toda celda sin fuente establecida; verificar que no hay valores sin fuente.
- [ ] 2.3 Agregar la línea de fuente APA 7 ("Fuente: elaboración propia sobre las obras citadas y sus resúmenes/DOI") y verificar que no rompe la composición de la tabla.
- [ ] 2.4 Insertar la tabla en `subsec:trabajos-academicos` y sustituir la oración agrupada de `03:32`; verificar que los cuatro trabajos de esa oración aparecen como filas propias.

## 3. Neutralidad de páginas

- [ ] 3.1 Condensar la prosa de `03:28`/`03:30` que repite el par corpus/métrica ya expuesto en la tabla, preservando la corrección de atribución de Revina et al. (2020); verificar que la afirmación corregida sigue presente.
- [ ] 3.2 Recortar la frase de cierre redundante de `03:32` y, si hace falta, comprimir caption y ancho de columnas; verificar que no se elimina ninguna afirmación sustantiva.
- [ ] 3.3 Recompilar y verificar `pdfinfo main.pdf | grep Pages <= 100`; si excede, repetir 3.1-3.2 sin tocar contenido científico.

## 4. Verificación

- [ ] 4.1 Compilar con `texlive-thesis` y verificar `0` ocurrencias de "undefined reference" y "multiply defined label" en `main.log`.
- [ ] 4.2 Verificar contra las fuentes (prosa, `.bib`, resúmenes por DOI) que cada valor numérico de la tabla coincide con su fuente; registrar el contraste.
- [ ] 4.3 Verificar que `tab:comparativa` sigue comparando soluciones comerciales y que no hay filas duplicadas entre ambas tablas.
- [ ] 4.4 Verificar que `Bibliography_base.bib` no tiene altas nuevas (salvo una fuente que resuelva por DOI) y que toda clave citada en la tabla existe.
- [ ] 4.5 Registrar como evidencia el conteo de páginas final y el resultado de la verificación de referencias en las tareas.

## 5. Cierre y secuencia

- [ ] 5.1 Confirmar que el único `.tex` modificado es `03-estado-del-arte.tex` y que no se tocaron `preambles/`, `main.tex`, el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.
- [ ] 5.2 Confirmar que este change queda cerrado antes de aplicar `c-111` (versionado y tag); registrar el orden.
