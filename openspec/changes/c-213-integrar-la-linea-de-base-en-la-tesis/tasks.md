## 1. Contraste pareado (TDD estricto; LOW)

- [ ] 1.1 Red de seguridad: correr `cd evaluation && pytest tests/test_linea_de_base.py -q` y las pruebas de `evaluation/data/campana/analisis/` y registrar la línea de base de pruebas en verde.
- [ ] 1.2 RED: escribir `evaluation/data/campana/analisis/test_contraste_linea_de_base_c213.py` con pruebas que fallen para el emparejamiento por `caso_id` (incluido el caso sin pareja, que aborta), la tabla 2×2, el caso sin discordancias, el bootstrap pareado con semilla fija y la verificación de anclas (67/103, 60/103, 87/103; aborta si difieren).
- [ ] 1.3 GREEN/TRIANGULAR/REFACTOR: implementar `contraste_linea_de_base_c213.py` (funciones puras; reutiliza `evaluation.linea_de_base.predecir` y `evaluation/stats.py::contraste_mcnemar` sin modificarlos; ruta de referencia y `n` esperado como parámetros).
- [ ] 1.4 Ejecutar el script dos veces, comprobar salidas idénticas byte a byte y versionar `contraste_linea_de_base_c213.{json,md}` y `contraste_linea_de_base_c213.SHA256SUMS.txt` (LF, UTF-8 sin BOM); actualizar `evaluation/data/campana/analisis/README.md`.
- [ ] 1.5 Si las anclas no se reproducen (p. ej., por versión de scikit-learn), marcar el grupo 1 como bloqueado, documentar el diagnóstico y continuar el grupo 2 sin cifras pareadas.

## 2. Integración en la tesis (MEDIUM, checkpoint con el dueño antes de cerrar)

- [ ] 2.1 `04-marco-metodologico.tex`: párrafo de método de la línea de base (D5): modelo (`Pedregosa2011_scikit_learn`), 200/103, control de filtración, variantes fijadas antes de medir, contraste pareado (`McNemar1947_sampling_error`, `Efron1993_bootstrap`) y qué no es.
- [ ] 2.2 `07-resultados.tex`: subsección `subsec:linea-de-base` tras la validación fuera de muestra con `tab:linea-de-base` (tres filas, cuatro métricas, Wilson del híbrido y de la línea de base si el artefacto lo trae) y el contraste pareado; nota de repetición sobre n = 150 con c-206.
- [ ] 2.3 `08-discusion.tex:56`: reescribir la limitación quinta según D1; agregar la lectura acotada y las amenazas de la comparación; verificar que `08-discusion.tex:10` siga declarando no contrastada la hipótesis de eficiencia.
- [ ] 2.4 `09-conclusiones.tex:47`: reemplazar "No se realizó una comparación directa…" por la conclusión acotada; revisar la fila del objetivo 2 (`:24`) sin cambiar su veredicto.
- [ ] 2.5 `10-recomendaciones.tex:14`: reemplazar la referencia a la "ausencia de una línea de base" por lo que queda pendiente (brazo solo-LLM, más datos, supervisados más fuertes, n = 150 arbitrado).
- [ ] 2.6 Grep de verificación en `sections/*.tex` ("ausencia de una línea de base", "no se comparó", "No se realizó una comparación directa", "TF-IDF+SVM", "supervisado"); revisar `00-resumen.tex` y `01-introduccion.tex` y editar solo si contradicen la evidencia.
- [ ] 2.7 Revisión de lectura (TLB-03): ninguna oración nueva afirma superioridad general ni eficiencia frente al LLM solo; acentos correctos; sin nombres reales (solo `E1..E5`, `O1`, `O2`).

## 3. Trazabilidad

- [ ] 3.1 `numeros-canonicos.md`: sección 3.22 aditiva con cada cifra nueva, su artefacto y su ruta JSON.
- [ ] 3.2 `dictamen-correcciones.md`: entrada c-213 atada al criterio 4 del dictamen v1.3.0.
- [ ] 3.3 `CHANGES.md`: `## FASE 69` con el patrón de la FASE 68.
- [ ] 3.4 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py` y correr su prueba.
- [ ] 3.5 Correr `verify_citations.py`: cero claves sin resolver, sin entradas bibliográficas nuevas.

## 4. Cierre

- [ ] 4.1 `openspec validate c-213-integrar-la-linea-de-base-en-la-tesis --strict --no-interactive`.
- [ ] 4.2 Commits convencionales en español, sin atribución, sin tocar `.engram/`.
- [ ] 4.3 MANUAL/BLOQUEADO (dueño): recompilar `main.pdf` con Docker y revisar la paginación de las tablas nuevas.
- [ ] 4.4 SEGUIMIENTO (cuando c-206 entregue el arbitraje): volver a correr el contraste con la referencia de 150 casos y sustituir las cifras señaladas (fuera del alcance de este change).
