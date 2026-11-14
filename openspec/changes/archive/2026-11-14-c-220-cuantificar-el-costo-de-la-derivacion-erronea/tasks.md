## 1. Preparación y trazabilidad de entradas

- [x] 1.1 Registrar en `evaluation/data/campana/analisis/README.md` la cobertura de `duracion_s` (`138/147`) y la lista de los 9 casos sin duración; verificar contra `intervenciones.csv`.
- [x] 1.2 Calcular y registrar la huella SHA-256 de `intervenciones.csv`, `brazo_manual.csv` y `resultados.json` en la cabecera del análisis; verificar que el comando de reproducción las recomputa.
- [x] 1.3 Releer el índice de `numeros-canonicos.md` y fijar el número libre de la sección nueva (esperado `3.29`); verificar que no colisiona con c-218 ni c-219.

## 2. Análisis offline (TDD)

- [x] 2.1 RED: escribir `test_analisis_costo_derivacion_c220.py` con los casos sintéticos del spec (grupos constantes, diferencia de medias, faltantes enumerados, determinismo); verificar que falla por ausencia del módulo.
- [x] 2.2 GREEN: implementar el cálculo de duraciones por `cambio_sector` con media, mediana, desvío e IC bootstrap (`B = 2000`, semilla `20261021`); verificar que los tests de 2.1 pasan.
- [x] 2.3 Triangulación: agregar el caso de exclusión de faltantes con imputación prohibida y el del grupo vacío; verificar que pasan sin tocar el código de 2.2 más de lo necesario.
- [x] 2.4 Implementar la diferencia de medias entre grupos con IC bootstrap independiente; verificar con el caso sintético de diferencia conocida.
- [x] 2.5 Implementar el proxy de rediagnóstico desde `brazo_manual.csv`, agrupado y por operador (`O1`, `O2`); verificar que reproduce `n = 220` y las medianas por operador.
- [x] 2.6 Implementar la composición de `c` en régimen corto y largo con el componente anclado y su propagación; verificar que el escenario bajo excluye el ancla y el alto la incluye sin promediar.
- [x] 2.7 Implementar la comparación con la banda `[600; 900] s` y la regla D5 (rama A / rama B); verificar con dos intervalos sintéticos, uno que intersecta y otro que excluye.
- [x] 2.8 Implementar el término de revisión `r` y su efecto sobre `B` como sensibilidad aditiva separada (D7); verificar que `B` canónico no se modifica en la salida.
- [x] 2.9 REFACTOR y emisión: generar `.json` y `.md` con procedencia, comando y SHA-256; correr dos veces y verificar salidas idénticas byte a byte.

## 3. Ejecución y compuerta de decisión

- [x] 3.1 Ejecutar el análisis sobre los artefactos versionados y registrar la rama de D5 que corresponde (A: la banda se intersecta; B: se excluye), con los valores que la determinan.
- [x] 3.2 Contrastar las cifras obtenidas con la tabla de valores esperados del `design.md`; verificar coincidencia o registrar la desviación y retirar del diseño las cifras que no se reproduzcan.

## 4. Memo canónico (aditivo)

- [x] 4.1 Agregar la sección nueva a `numeros-canonicos.md` con la tabla de insumos (valor, procedencia archivo:ruta, estado, notas) y la declaración de que es aditiva; verificar que la tabla cubre cada valor que cita la prosa de tesis.
- [x] 4.2 Agregar las fórmulas y los valores derivados (costo incremental de la compuerta, `c` por régimen, costo marginal por punto de exactitud, término `r`); verificar el recálculo con el comando de referencia.
- [x] 4.3 Agregar la remisión desde la sección que declaraba el costo sin registro, sin borrar ni reescribir su contenido; verificar que la remisión apunta a la sección nueva.
- [x] 4.4 Verificar con `git diff` acotado que ninguna sección previa del memo cambió y que solo hay líneas agregadas más la remisión.

## 5. Tesis: introducción y metodología

- [x] 5.1 Reemplazar en `01-introduccion.tex:48` solo la oración de procedencia del segundo criterio, conservando los tres criterios y el umbral; verificar que el párrafo sigue citando la paridad medida y el costo marginal.
- [x] 5.2 Agregar en `04-marco-metodologico.tex` la definición operacional de `c` (tiempo-persona, dos regímenes) y el método de medición, dentro de `subsec:operacionalizacion-variables` y `subsec:metricas-instrumentos`; verificar que la definición no contradice `tab:variables`.
- [x] 5.3 Verificar con `grep` que el umbral sigue en `85~\%` y que no quedan afirmaciones de «estimación propia sin registro» en `01` ni en `04`.

## 6. Ancla bibliográfica

- [x] 6.1 Verificar la fuente primaria del ancla de reanudación contra el texto completo (población, tarea, magnitud) y agregar la entrada a `Bibliography_base.bib` solo si no existe; verificar que la cita resuelve y que no hay entradas huérfanas.

## 7. Registro del dictamen y validación

- [x] 7.1 Agregar la entrada nueva en `docs/Tesis/Correcciones/dictamen-correcciones.md` con «Qué cambió», «Resultados de los cálculos», «Decisiones y pendientes» y la decisión del dueño de D5 si aplica.
- [x] 7.2 Agregar la matriz de trazabilidad de la entrada y verificar con `python3 docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` que las anclas resuelven.
- [x] 7.3 Correr `openspec validate c-220-cuantificar-el-costo-de-la-derivacion-erronea --strict` y verificar que pasa.