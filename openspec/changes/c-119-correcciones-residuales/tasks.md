## 1. Defectos visibles del PDF

- [ ] 1.1 Restaurar `\raggedright\arraybackslash` en una sola linea en `07-resultados.tex:17-18` (eliminar la linea 18); verificar que `pdftotext "main.pdf" - | grep -c aggedright` devuelve 0 tras recompilar y que anchos/contenido de la tabla son identicos
- [ ] 1.2 Cerrar el corchete del intervalo en `09-conclusiones.tex:24` a `IC [67,0~\%, 79,1~\%]`; verificar `grep -c 'IC \[67,0~\\%, 79,1~\\%\]' 09-conclusiones.tex` == 1
- [ ] 1.3 Reemplazar `Tabla~5` por `Tabla~\ref{tab:api}` en `12-anexos.tex:35`; verificar que `grep -n 'Tabla~5' 12-anexos.tex` no devuelve nada y que `tab:api` existe en `05-arquitectura.tex:128`

## 2. Estructura y cosmética

- [ ] 2.1 Agregar en `preambles/preamble.tex` (junto al bloque de apendices) `\renewcommand{\appendixname}{Anexo}`, `\renewcommand{\appendixtocname}{Anexos}` y `\renewcommand{\appendixpagename}{Anexos}`; verificar `pdftotext "main.pdf" - | grep -c Appendices` == 0 y entrada en espanol en `main.toc`
- [ ] 2.2 Quitar `, Redis` de la enumeracion de servicios internos en `05-arquitectura.tex:8`; verificar `grep -c Redis 05-arquitectura.tex` == 0
- [ ] 2.3 Insertar `\phantomsection` antes de `\printbibliography` en `main.tex:78`; verificar que `grep 'Referencias bibliograficas' main.toc` ya no muestra `subsection.12.8`; si el ancla no cambia, registrar la limitacion cosmetica aceptada

## 3. Afirmacion cuantitativa no respaldada

- [ ] 3.1 Reformular `06-implementacion.tex:62` a forma cualitativa (quitar "en aproximadamente 4 puntos porcentuales de F1"); verificar `grep -c 'puntos porcentuales' 06-implementacion.tex` == 0 y que no se introduce ningun numero nuevo

## 4. Compilacion y verificacion global

- [ ] 4.1 Confirmar que no hay medicion que respalde los 4 puntos en `evaluation/` (revisar `evaluation/README.md`) antes de dar 3.1 por cerrada
- [ ] 4.2 Compilar con `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex` y verificar ausencia de errores fatales
- [ ] 4.3 Verificar presupuesto de paginas: cuerpo <= 100 y total sin aumento respecto de 102; verificar `aggedright`==0 y `Appendices`==0 en el texto extraido
- [ ] 4.4 Confirmar que no se modifico contenido cientifico, numeros canonicos, `Bibliography_base.bib`, el memo, `CHANGES.md` ni `dictamen-correcciones.md`, y que `v1.0.0` no se movio (verificar con `git tag -l v1.0.0` y `git diff --stat`)
