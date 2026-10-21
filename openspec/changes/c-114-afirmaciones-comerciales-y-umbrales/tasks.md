# Tasks — c-114 — Afirmaciones comerciales y umbral de 5.000 casos

> Governance MEDIO. Decisiones y reversibilidad en `design.md`. NO se editan los
> `.tex` fuera de `03-estado-del-arte.tex`, `08-discusion.tex`,
> `10-recomendaciones.tex` y `12-anexos.tex`, ni entradas del `.bib` fuera de las
> nuevas (si las hubiera). NO se duplica la corrección de c-104.

> Modo de ejecución: Standard (Strict TDD no aplica — cambio documental, sin test
> runner para prosa/.bib; las compuertas son `verify_citations.py`, `grep` y la
> compilación con `texlive-thesis`).

## 0. Prerrequisitos (solo lectura)

- [ ] 0.1 Confirmar que `c-104-bibliografia-y-atribucion` está aplicado/archivado
  antes de tocar el `.bib`; no re-tipar Touvron/Jurafsky (D5).
- [ ] 0.2 Registrar el conteo de páginas de partida (`main.pdf` = 104) y la fecha
  de verificación (D6).
- [ ] 0.3 Confirmar con `git status` que el árbol está limpio antes de empezar.
- [ ] 0.4 Localizar todas las apariciones del umbral: `grep -n "5\.000" sections/*.tex`;
  registrar si son tres o cuatro (Open Question).

## 1. Afirmaciones comerciales (dimensiones 4 y 9, D2)

- [ ] 1.1 `03-estado-del-arte.tex:12`: reformular la afirmación de dominancia del
  segmento como observación propia documentada (base: documentación pública de las
  plataformas, consulta 19-10-2026) o citar un informe de mercado con DOI.
- [ ] 1.2 `03-estado-del-arte.tex:14`: reformular la afirmación de "crecimiento
  sostenido de la adopción" como observación propia acotada, sin tendencia
  cuantitativa sin fuente.
- [ ] 1.3 `03-estado-del-arte.tex:22`: revisar la afirmación de idoneidad de N8N
  para el segmento y acotarla a una observación propia o cita verificable.
- [ ] 1.4 Verificar con `grep` que no quedan afirmaciones de mercado sin respaldo
  ("dominado", "crecimiento sostenido", "más difundid") sin anclaje declarado.

## 2. Umbral de 5.000 casos (dimensión 8, D3)

- [ ] 2.1 `10-recomendaciones.tex:10`: declarar el umbral como valor indicativo
  (dependiente del régimen de aprendizaje y del desempeño objetivo), no como umbral
  fundado.
- [ ] 2.2 `08-discusion.tex:54`: alinear la mención del umbral a la misma
  formulación indicativa.
- [ ] 2.3 `12-anexos.tex:139`: alinear la mención del umbral a la misma
  formulación indicativa.
- [ ] 2.4 Verificar consistencia: las tres (o cuatro) apariciones emplean el mismo
  tratamiento; `grep` no muestra una cifra presentada como umbral fundado.

## 3. Priorización de líneas futuras (dimensión 8, D4)

- [ ] 3.1 `10-recomendaciones.tex`: agregar un párrafo breve al inicio del capítulo
  que declare prioritarias las líneas que atacan los defectos medidos (calibración
  del gate, clasificador supervisado, corrección de la medición de intervención)
  sobre las extensiones genéricas.
- [ ] 3.2 Verificar que la priorización remite a las limitaciones de la discusión
  y no introduce claims ni cifras nuevas.

## 4. Bibliografía (condicional, D2)

- [ ] 4.1 Si se opta por citar un informe de mercado: verificar que resuelve por
  DOI o landing; si no resuelve, mantener la reformulación.
- [ ] 4.2 Si se agrega entrada: hacerlo de forma aditiva, con `author`, `title`,
  `year`, campo de publicación y `doi`, clave `ApellidoAnio_palabra_clave`; no
  editar entradas existentes. Si no se agrega, marcar esta sección como no-op.

## 5. Verificación de integridad y compilación

- [ ] 5.1 Ejecutar `python "docs/Tesis/v9 (IA)/verify_citations.py"` y registrar la
  salida (0 huérfanas / 0 sin usar, o el estado real).
- [ ] 5.2 Compilar con la imagen Docker `texlive-thesis`:
  `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
- [ ] 5.3 Confirmar 0 errores fatales y 0 referencias indefinidas en `main.log`.
- [ ] 5.4 Registrar el conteo de páginas final; aplicar D6 si creció (cap <= 100
  es objetivo de `c-116`, posterior; aquí solo se exige no inflar).
- [ ] 5.5 Verificar en el PDF con `pdftotext` que las reformulaciones y la
  priorización se renderizan y no quedan frases sin respaldo.

## 6. Validación y cierre

- [ ] 6.1 Ejecutar `openspec validate c-114-afirmaciones-comerciales-y-umbrales --strict`.
- [ ] 6.2 Anotar el estado de las dimensiones 4, 8 y 9 en el registro de
  trazabilidad de correcciones (sin editar el memo canónico).
