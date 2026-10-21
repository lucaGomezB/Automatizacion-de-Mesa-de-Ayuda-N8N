## 1. Preparación y baseline

- [x] 1.1 Confirmar el estado del archivo y sus líneas: leer `docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex` y verificar que `03:24`-`03:34` y `tab:comparativa` están en el estado descrito en `design.md`.
- [x] 1.2 Medir el baseline de páginas: compilar con la imagen `texlive-thesis` (`latexmk main.tex`) y registrar `pdfinfo main.pdf | grep Pages` (esperado 100).
- [x] 1.3 Verificar que no existe una tabla académica previa ni colisión con `tab:comparativa`; registrar el resultado en las tareas.

## 2. Tabla comparativa

- [x] 2.1 Redactar la tabla `tab:trabajos-academicos` con las columnas `trabajo | enfoque | corpus/idioma | métrica reportada | condición` y las seis filas de `design.md` D2, con booktabs y `\small`; verificar que compile sin errores de entorno.
- [x] 2.2 Completar cada celda según la procedencia de `design.md` D4; marcar como "no reportado en el alcance revisado" toda celda sin fuente establecida; verificar que no hay valores sin fuente.
- [x] 2.3 Agregar la línea de fuente APA 7 ("Fuente: elaboración propia sobre las obras citadas y sus resúmenes/DOI") y verificar que no rompe la composición de la tabla.
- [x] 2.4 Insertar la tabla en `subsec:trabajos-academicos` y sustituir la oración agrupada de `03:32`; verificar que los cuatro trabajos de esa oración aparecen como filas propias.

## 3. Neutralidad de páginas

- [x] 3.1 Condensar la prosa de `03:28`/`03:30` que repite el par corpus/métrica ya expuesto en la tabla, preservando la corrección de atribución de Revina et al. (2020); verificar que la afirmación corregida sigue presente.
- [x] 3.2 Recortar la frase de cierre redundante de `03:32` y, si hace falta, comprimir caption y ancho de columnas; verificar que no se elimina ninguna afirmación sustantiva.
- [x] 3.3 Recompilar y verificar `pdfinfo main.pdf | grep Pages <= 100`; si excede, repetir 3.1-3.2 sin tocar contenido científico.

## 4. Verificación

- [x] 4.1 Compilar con `texlive-thesis` y verificar `0` ocurrencias de "undefined reference" y "multiply defined label" en `main.log`.
- [x] 4.2 Verificar contra las fuentes (prosa, `.bib`, resúmenes por DOI) que cada valor numérico de la tabla coincide con su fuente; registrar el contraste.
- [x] 4.3 Verificar que `tab:comparativa` sigue comparando soluciones comerciales y que no hay filas duplicadas entre ambas tablas.
- [x] 4.4 Verificar que `Bibliography_base.bib` no tiene altas nuevas (salvo una fuente que resuelva por DOI) y que toda clave citada en la tabla existe.
- [x] 4.5 Registrar como evidencia el conteo de páginas final y el resultado de la verificación de referencias en las tareas.

## 5. Cierre y secuencia

- [x] 5.1 Confirmar que el único `.tex` modificado es `03-estado-del-arte.tex` y que no se tocaron `preambles/`, `main.tex`, el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.
- [x] 5.2 Confirmar que este change queda cerrado antes de aplicar `c-111` (versionado y tag); registrar el orden.

## Evidencia de aplicación

- Baseline (1.2): `pdfinfo main.pdf | grep Pages` = 100 páginas antes del cambio (compilación `texlive-thesis`).
- Colisión (1.3): no existía tabla académica previa; `tab:comparativa` (c-96) compara soluciones comerciales; la tabla nueva usa el rótulo distinto `tab:trabajos-academicos`.
- Neutralidad (3.3 / 4.5): conteo final = 100 páginas (`pdfinfo main.pdf | grep Pages`). Ajuste logrado sin eliminar contenido científico: se sustituyó la oración agrupada de `03:32`, se condensó `03:28`/`03:30` (se retiró la repetición del par corpus/métrica), se recortó el caption y se acotaron las columnas `p{}` (ancho total dentro del `textwidth`; `\tabcolsep` a 4pt). El float se ancló con `[!ht]` para compartir página con el texto y evitar una página de flotante.
- Referencias (4.1): `main.log` con 0 "undefined", 0 "multiply defined" y 0 errores fatales.
- Procedencia (4.2): Paramesh (~10.000 tickets, inglés; exactitud ~87 %) desde prosa `03:28`; Zangari (20.000 reclamos + 35.000 issues; >28 % F1) desde resumen ESWA DOI `10.1016/j.eswa.2023.119984`; Paket (turco, 172 clases; BERT supera a los LLM) desde resumen UBMK DOI `10.1109/ubmk63289.2024.10773473`; Liu (ByteDance Volcano Engine; eficacia en despliegue) desde resumen FSE/arXiv DOI `10.1145/3696630.3728558`; Colavito (22 LLM + 2 BERT; dos datasets de GitHub) desde resumen IST DOI `10.1016/j.infsof.2025.107758`. Las celdas no establecidas en fuente accesible quedan como "no reportado en el alcance revisado" (Revina corpus/métrica; Paket métrica; Liu corpus/métrica; Colavito corpus/métrica), conforme D5.
- Bibliografía (4.4): `Bibliography_base.bib` sin altas (54 entradas antes y después); las seis claves citadas en la tabla existen.
- Atribución (3.1): la prosa corregida de Revina et al. (2020) se preserva (sin BERT, sin 91 %; conclusión sobre métodos simples y explicables).
- Alcance (5.1): único `.tex` modificado = `03-estado-del-arte.tex`.
- Secuencia (5.2): c-117 aplicado; c-111 (versionado y tag) queda pendiente y posterior.


