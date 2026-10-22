## 1. Ediciones de contenido

- [x] 1.1 En `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (`sec:anexo-repositorio`, linea ~19), insertar `\url{https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N}` como enlace visible dentro de la prosa existente, conservando la oracion introductoria y la cita `\parencite{Gomez2026_repositorio}` (decision D1 de `design.md`: `\url` en lugar de `\urlref`); verificar con `grep -c "\\\\url{https://github.com/lucaGomezB" sections/12-anexos.tex` que el valor es >= 1
- [x] 1.2 Verificar que la cita `\parencite{Gomez2026_repositorio}` y la prosa del anexo se conservan sin eliminar ninguna oracion sustantiva; confirmar con `grep -c "Gomez2026_repositorio" sections/12-anexos.tex` que el conteo no disminuye respecto de la version previa
- [x] 1.3 En `docs/Tesis/v10 (IA)/Bibliography_base.bib` (entrada `Gomez2026_repositorio`, linea ~615), reemplazar `(Version 1.0.0)` por `(Version 1.1.1)` en el campo `title`, conservando `author`, `year`, `url` y `note` (decision D2); verificar con `grep "Version 1.1.1" Bibliography_base.bib` que la cadena nueva figura y con `grep -c "Version 1.0.0" Bibliography_base.bib` que da 0
- [ ] 1.4 En `sections/12-anexos.tex` (`sec:anexo-repositorio`, linea ~19), reemplazar el tag `v1.1.0` por `v1.1.1` (patron C1), conservando la estructura de la frase; verificar `grep -c "v1.1.1" sections/12-anexos.tex` >= 1 y que `v1.1.0` ya no figura en la linea del tag

## 2. Compilacion y presupuesto de paginas

- [x] 2.1 Compilar con XeLaTeX (`latexmk -xelatex main.tex`, o el contenedor `texlive-thesis` usado en changes previos) y verificar en el `.log` ausencia de errores fatales, de referencias indefinidas y de `Overfull \hbox` en la linea de la URL
- [x] 2.2 Verificar el presupuesto de paginas: el total del PDF MUST ser <= 101 paginas (criterio duro); registrar el conteo obtenido con `pdfinfo main.pdf` y, si se supera, aplicar el recorte previsto en `design.md` (D4/Risks) antes de continuar
- [x] 2.3 Ejecutar la verificacion de citas desde `docs/Tesis/v10 (IA)/` (`python3 verify_citations.py`) y confirmar cero citas huerfanas y cero entradas sin usar tras las ediciones

## 3. Commit, tag v1.1.1 y trazabilidad del hash (patron C1/C2)

- [ ] 3.1 Crear el commit de cierre (C) con las ediciones ya compiladas y verificadas (grupos 1 y 2) y confirmar que el arbol queda limpio con `git status --short`; verificar que C es posterior a la aplicacion de este change
- [ ] 3.2 Crear el tag anotado `v1.1.1` sobre el commit de cierre (patron C1) y publicarlo en `origin`; verificar `git cat-file -t v1.1.1` == `tag` (anotado) y que `git ls-remote --tags origin v1.1.1` lo devuelve
- [ ] 3.3 Consignar el hash completo de 40 caracteres del commit etiquetado en `sections/12-anexos.tex` (patron C2) y en `docs/Tesis/Correcciones/dictamen-correcciones.md`; verificar coincidencia exacta con `git rev-parse v1.1.1^{commit}` y recompilar el PDF final

## 4. Verificacion global

- [ ] 4.1 Confirmar que no se modificaron numeros canonicos, las cinco cadenas de categoria, las figuras, `evaluation/` ni `CHANGES.md`, que no se toco `docs/Tesis/v9 (IA)/` ni `auditorias/`, y que los tags previos siguen en sus commits (`git rev-parse v1.0.0^{commit}` == `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `git rev-parse v1.0.1^{commit}` == `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `git rev-parse v1.1.0^{commit}` == `7103b649d8c4f51737ad6ad4095dad22c9406400`)
- [ ] 4.2 Verificar que el tag `v1.1.1` esta anotado y publicado en `origin` y que el hash consignado en el manuscrito y en `dictamen-correcciones.md` coincide con `git rev-parse v1.1.1^{commit}`
