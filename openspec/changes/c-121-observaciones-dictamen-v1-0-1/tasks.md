## 1. Tabla comparativa del estado del arte (REC 1)

- [x] 1.1 En `sections/03-estado-del-arte.tex:60`, ajustar el parrafo introductorio de `tab:comparativa` para que declare exactamente las cuatro dimensiones que la tabla tiene (Solucion, Despliegue, Clasificacion automatica, Modelo de costo) y retire "soberania sobre los datos" de la enumeracion de dimensiones; verificar que la sintesis posterior (`03-estado-del-arte.tex:82`) y `01-introduccion.tex:64` conservan la soberania sobre los datos como prosa, sin eliminar ninguna propiedad sustantiva (decision D1 de `design.md`)
- [x] 1.2 Verificar que la tabla `tab:comparativa` mantiene sus cuatro columnas y su `\label` intactos; confirmar con `grep -c "soberania sobre los datos" sections/03-estado-del-arte.tex` que la propiedad no queda enunciada como dimension de la tabla

## 2. Hallazgo del gate como resultado propio (REC 2)

- [x] 2.1 En `sections/08-discusion.tex`, agregar un parrafo (o frase) que presente la conducta observada del gate ---la etapa Gemini nunca devolvio una confianza inferior a 0,85 en los 200 casos, de modo que el gate no derivo ningun caso--- como hallazgo empirico positivo sobre el comportamiento del clasificador en el dominio evaluado; verificar que no se introduce ningun numero fuera de `docs/Tesis/Correcciones/numeros-canonicos.md` (decision D2)
- [x] 2.2 En `sections/07-resultados.tex` (`subsec:reduccion-intervencion`, linea ~136), reencuadrar la frase existente sobre la confianza de Gemini (>= 0,85) para que se lea como hallazgo positivo ademas de justificacion de la no contraste; verificar que se conserva el `\label{subsec:reduccion-intervencion}` y que no se duplica el argumento de la discusion

## 3. Cobertura bibliografica de plataformas comerciales (REC 3)

- [x] 3.1 Agregar en `Bibliography_base.bib`, a continuacion del bloque c-120 (lineas 525-541), tres entradas `@online` para Zendesk, Freshdesk y ServiceNow siguiendo el patron exacto de `DigitalOcean2026_pricing` / `Google2026_vertex_pricing` (`author` como entidad, `title`, `year = {2026}`, `url`, `urldate = {2026-10-19}`, `note`); la `note` declara la pagina de documentacion (capacidades/precios) sin inventar cifras de precio (decision D3)
- [x] 3.2 En `sections/01-introduccion.tex:68`, agregar `\parencite` a las tres entradas nuevas al final de la mencion a Zendesk Suite, Freshdesk y ServiceNow ITSM, conservando la prosa como observacion de relevamiento propio con fecha
- [x] 3.3 Verificar con `python3 verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) cero citas huerfanas y cero entradas sin usar tras las tres incorporaciones

## 4. Version y trazabilidad de la release v1.1.0 (D2)

- [x] 4.1 En `sections/12-anexos.tex` (`sec:anexo-repositorio`, lineas ~19-21), reemplazar el tag `v1.0.1` por `v1.1.0` (patron C1 de c-111), conservando la estructura de la frase; verificar `grep -c "v1.1.0" sections/12-anexos.tex` >= 1
- [x] 4.2 Crear el tag anotado `v1.1.0` sobre el commit de cierre de v10 (SOLO despues de aplicar c-122 y c-121 y recompilar) y publicarlo en `origin`; verificar `git cat-file -t v1.1.0` == `tag` (anotado, no lightweight)
- [x] 4.3 Consignar el hash completo de 40 caracteres del commit etiquetado en `12-anexos.tex` (nuevo parrafo, patron C2 de c-111) y en `docs/Tesis/Correcciones/dictamen-correcciones.md`; verificar coincidencia con `git rev-parse v1.1.0^{commit}`

## 5. Compilacion y verificacion global

- [x] 5.1 Compilar con XeLaTeX (`latexmk -xelatex main.tex`, o el contenedor usado en c-120) y verificar ausencia de errores fatales y de referencias indefinidas en el `.log`
- [x] 5.2 Verificar el presupuesto de paginas: el total del PDF MUST ser <= 101 paginas (criterio duro); registrar el conteo obtenido y, si se supera, aplicar el recorte previsto en `design.md` (Risks) antes de cerrar
- [x] 5.3 Confirmar que no se modificaron numeros canonicos, las cinco cadenas de categoria, las figuras, `evaluation/` ni `CHANGES.md`, y que `v1.0.1` no se movio (`git rev-parse v1.0.1^{commit}` == `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`)
- [x] 5.4 Verificar que el tag `v1.1.0` esta anotado y publicado en `origin` (`git ls-remote --tags origin v1.1.0`)
