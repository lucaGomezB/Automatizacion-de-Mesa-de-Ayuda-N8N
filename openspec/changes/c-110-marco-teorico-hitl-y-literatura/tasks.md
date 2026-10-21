# Tasks — c-110 — Marco teórico (HITL) y protocolo de revisión de literatura

> Governance ALTO. Decisiones y reversibilidad en `design.md`. NO se editan los
> `.tex` fuera de `02-marco-teorico.tex` y `03-estado-del-arte.tex`, ni entradas
> del `.bib` fuera de las nuevas. Se aplica DESPUÉS de c-104.

## 0. Prerrequisitos (solo lectura)

- [ ] 0.1 Confirmar que `c-104-bibliografia-y-atribucion` está aplicado/archivado
  antes de tocar el `.bib`; si no, detener y aplicarlo primero (D7).
- [ ] 0.2 Registrar el conteo de páginas de partida (`main.pdf` = 103) y la fecha
  de verificación.
- [ ] 0.3 Confirmar con `git status` que el árbol está limpio antes de empezar.

## 1. Protocolo de revisión de literatura (ítem 11a, D3)

- [ ] 1.1 `03-estado-del-arte.tex`: agregar el párrafo de metodología de revisión
  con bases (Scopus, IEEE Xplore, ACM DL, ACL Anthology, Google Scholar, arXiv),
  cadenas de búsqueda, criterios de inclusión/exclusión y período (2023-2026 para
  el estado del arte moderno).
- [ ] 1.2 Crear la bitácora de búsqueda versionada en
  `docs/Tesis/Correcciones/` con una entrada por consulta (base, cadena, fecha,
  resultado) y la fecha de corte.
- [ ] 1.3 Verificar la consistencia texto–bitácora: cada base, cadena y criterio
  del texto existe en la bitácora y viceversa.

## 2. Acotamiento de la vacancia (ítem 11b, D4)

- [ ] 2.1 `03-estado-del-arte.tex` (afirmación de vacancia): reformular como
  relativa ("en las fuentes consultadas hasta la fecha de corte…"), citando bases,
  cadenas y fecha de corte; eliminar la inexistencia absoluta.
- [ ] 2.2 `03-estado-del-arte.tex` (síntesis de la brecha, cierre del capítulo):
  alinear la mención reutilizada con el alcance declarado en 1.1.
- [ ] 2.3 Verificar con búsqueda que no queda una formulación de vacancia sin
  acotar en el capítulo.

## 3. Fuentes bibliográficas nuevas (D5)

- [ ] 3.1 Agregar a `Bibliography_base.bib`, de forma aditiva, las entradas de
  HITL (Amershi 2019, Shneiderman 2020, Mosqueira-Rey 2023, Zanzotto 2019, Wu
  2022) con `author`, `title`, `year`, campo de publicación y `doi`, clave
  `ApellidoAnio_palabra_clave`.
- [ ] 3.2 Re-verificar cada DOI nuevo por Crossref o landing de editorial; retirar
  o reemplazar cualquier entrada que no resuelva.
- [ ] 3.3 Confirmar que no se editó ninguna entrada existente ni de c-104.

## 4. Subsección teórica de human-in-the-loop (ítem 12, D2)

- [ ] 4.1 `02-marco-teorico.tex`: insertar la subsección de HITL después de
  `subsec:automatizacion-orquestacion` con definición y grados de autonomía
  (revisión total, revisión selectiva por confianza, operación autónoma con
  auditoría).
- [ ] 4.2 Fundamentar cada aserción con `\textcite{}`/`\parencite{}` de las
  entradas de la Sección 3; aterrizar el concepto en el gate
  `requiere_revision_humana = (confianza < 0,70)`.
- [ ] 4.3 Actualizar el párrafo introductorio del capítulo: "siete ejes" ->
  "ocho ejes".
- [ ] 4.4 Si el resumen o las palabras clave mencionan HITL, alinear la redacción
  con la definición incorporada (sin cifras nuevas).

## 5. Verificación de integridad de citas (D6)

- [ ] 5.1 Ejecutar
  `python "docs/Tesis/v9 (IA)/verify_citations.py"` y registrar la salida.
- [ ] 5.2 Confirmar `0` citas huérfanas y `0` entradas sin usar tras agregar las
  entradas nuevas.
- [ ] 5.3 Registrar la salida del script en `tasks.md` como evidencia.

## 6. Compilación y verificación visual

- [ ] 6.1 Compilar con la imagen Docker `texlive-thesis`:
  `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
- [ ] 6.2 Confirmar `0` errores fatales y `0` referencias indefinidas en
  `main.log`.
- [ ] 6.3 Verificar en el PDF que la subsección de HITL y el protocolo de revisión
  se renderizan y que las citas nuevas aparecen.
- [ ] 6.4 Registrar el conteo de páginas final y aplicar la mitigación de D8 si
  creció de forma excesiva.

## 7. Registro y cierre

- [ ] 7.1 Registrar en `CHANGES.md` la entrada de c-110 y su estado.
- [ ] 7.2 Ejecutar `openspec validate c-110-marco-teorico-hitl-y-literatura --strict`.
- [ ] 7.3 Anotar en `docs/Tesis/Correcciones/dictamen-correcciones.md` el estado
  de los ítems 11 y 12.
