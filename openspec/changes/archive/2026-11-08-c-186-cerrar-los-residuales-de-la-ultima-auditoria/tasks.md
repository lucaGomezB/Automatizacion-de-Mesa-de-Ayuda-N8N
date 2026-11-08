# Tasks: Cerrar los residuales de la última auditoría

## 1. Xuan et al. (2025) en la sección 3.3

- [x] 1.1 `docs/Tesis/v10 (IA)/paper/sections/03-estado-del-arte.tex:56`: reformular la oración para acotar la afirmación de CLASIFICACIÓN al benchmark que incluye tareas de clasificación (MEGA, `ahuja2023mega`) y presentar `xuan2025mmluprox` solo por la brecha de desempeño multilingüe. Verificación: la afirmación de clasificación no se atribuye a Xuan et al.; sin cambios en `Bibliography_base.bib`.

## 2. Sokolova y Lapalme (2009) como fuente que "confirma"

- [x] 2.1 `07-resultados.tex:153`: reformular la oración para presentar el desempeño desigual entre clases como hallazgo propio y citar `Sokolova2009_performance_measures` por las definiciones de las métricas. Verificación: `rg "confirma" 07-resultados.tex` no devuelve un verbo de confirmación atribuido a Sokolova; las citas de `:130`, `02-marco-teorico.tex:78` y `04-marco-metodologico.tex:69` permanecen como definiciones.

## 3. Tensión de la sección 9.2 (comparabilidad)

- [x] 3.1 `08-discusion.tex:38`: calificar la comparación con el F1 macro reportado para el inglés como indirecta y no comparable con las cifras de etiqueta única, coherente con la declaración de no comparabilidad de `:32`. Verificación: `:32` y `:38` no se contradicen; el dato numérico se conserva.

## 4. Filas B14 y B16 del Anexo I

- [x] 4.1 `12-anexos.tex:229` (B14): actualizar la fila para declarar cerradas las erratas de figuras y el `seudonimizado` por c-159 y c-163; retirar "pendientes".
- [x] 4.2 `12-anexos.tex:231` (B16): actualizar la fila para declarar cerrada la fecha de consulta de una referencia por c-163; retirar "pendiente".
- [x] 4.3 Verificación: `rg "seudonimizado|sobre que aspecto|categoría_predicha|categoría_validada" docs/Tesis/v10\ \(IA\)/paper/sections/` = 0 coincidencias (ya cerrados). Nota: la búsqueda debe excluir la subcadena de `pseudonimizado` (uso correcto); el token aislado `seudonimizado` quedó en 0.

## 5. Fila `Lím.` (cinco límites estructurales)

- [x] 5.1 `12-anexos.tex:258`: reformular la fila para declarar que el ítem (d) validación fuera de muestra queda como NEGATIVO declarado por ausencia de corpus independiente, y que no todos los cinco límites se cierran. Verificación: la fila no afirma el cierre de (d); el resto de los ítems conserva el estado que fijó c-169. (Se ajustó también la narración de `:238` por coherencia.)

## 6. B9 — Fechas de las iteraciones Scrumban (limitación declarada)

- [x] 6.1 SUPERSEDED por decisión binding del autor: `06-implementacion.tex:68` CONSERVA "sin fechar por separado" y NO se le agrega la causa (la causa se registra solo en la fila B9 del Anexo I y en `docs/diagrams/cronograma.md`). No se editó el cuerpo; ver 6.2 y 6.3. (superseded: la causa de B9 va solo en Anexo I + cronograma, por decision del autor)
- [x] 6.2 `12-anexos.tex:224` (B9): actualizar la fila para declarar la no recuperabilidad de las fechas de las iteraciones como limitación explícita, no como "pendiente".
- [x] 6.3 Verificación: la declaración es consistente entre `06-implementacion.tex:68`, la fila B9 del Anexo I y `docs/diagrams/cronograma.md`; no se introducen fechas nuevas.

## 7. Registro, compilación y validación

- [x] 7.1 Registrar en `docs/Tesis/Correcciones/dictamen-correcciones.md` una sección del change con la ubicación y la corrección de cada residual.
- [x] 7.2 Recompilar el PDF (`latexmk -xelatex main.tex`) sin errores fatales ni referencias indefinidas; `verify_citations.py` PASS; registrar el conteo de páginas y los conteos del log en `dictamen-correcciones.md`.
- [x] 7.3 Ejecutar `openspec validate c-186-cerrar-los-residuales-de-la-ultima-auditoria --strict --no-interactive`.
