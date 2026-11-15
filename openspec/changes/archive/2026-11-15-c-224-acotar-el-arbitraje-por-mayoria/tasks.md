Al final de cada tarea, entre paréntesis, el requisito del change que cumple, por nombre corto
precedido de su capacidad: `NC` (`tesis-numeros-canonicos`) y `TD` (`tesis-document`). Nombres
cortos: NC «Registro aditivo»; TD «Acotación en limitación», TD «Rango en resultados» y
TD «Trabajo futuro». Las tareas de preparación sin requisito propio no llevan paréntesis.

## 0. Preparación y línea de base

- [x] 0.1 Leer `proposal.md`, `design.md` y los dos specs delta del change, y cargar
      `python-testing-patterns` (y `python-design-patterns` para el script). Verificar que las
      skills se cargaron y registrar sus nombres.
- [x] 0.2 `git fetch` y comparar `origin/main` con la base del change; si `main` avanzó y toca
      `sections/`, `numeros-canonicos.md`, `dictamen-correcciones.md` o
      `evaluation/data/campana/`, rebasar antes de seguir y volver a verificar las líneas
      citadas en el design. Verificar con `git rev-list --left-right --count origin/main...HEAD`
      que la rama no diverge.
- [x] 0.3 Capturar la línea de base: `python -m pytest` de `evaluation/` desde su carpeta con
      las variables dummy del CI (baseline en verde; si algo falla antes de empezar, reportarlo
      como falla preexistente y no corregirlo); `rg -n "200 de 206"` y `rg -n "más etiquetadores
      independientes"` sobre `sections/*.tex`; y el último encabezado `### 3.` del memo.
      Verificar que la línea de base queda registrada.
- [x] 0.4 Fijar el número de la sección nueva del memo como el primero libre en `origin/main` al
      aplicar (al aplicar resultó `3.35`; se verificó que c-225 y c-226 no lo tomaron) y registrar lo
      decidido en `dictamen-correcciones.md`. Verificar que el número elegido no existe ya en
      `numeros-canonicos.md`.

## 1. Script de análisis (TDD estricto)

- [x] 1.1 Fijar en el docstring de
      `evaluation/data/campana/analisis/analisis_arbitraje_mayoria_c224.py` el método completo
      de D1 a D3 (fuentes, definición de la regla vigente y de la mayoría, identidad
      `142 + 58 = 200`, los `6` casos, el rango `142/206`–`147/206` y los dos extremos de las
      métricas por clase) y los anclajes que abortan. Verificar que el docstring contiene esos
      parámetros antes de escribir código. (NC «Registro aditivo»)
- [x] 1.2 **RED** `cargar_etiquetas` y `cargar_origen`: pruebas con filas sintéticas de `E3`,
      `E4` y `E5`, un caso de consenso, uno arbitrado y uno de tres vías. Ejecutar
      `python -m pytest evaluation/data/campana/analisis/test_analisis_arbitraje_mayoria_c224.py -q`
      y confirmar que falla porque las funciones no existen. (NC «Registro aditivo»)
- [x] 1.3 **GREEN** implementar lo mínimo para pasar 1.2 y confirmar verde con el mismo
      comando. (NC «Registro aditivo»)
- [x] 1.4 **RED → GREEN** `regla_vigente` y `mayoria`: pruebas con consenso `E3 = E4`, con
      `E5` coincidente con uno de los dos y con tres etiquetas distintas; verificar que
      `mayoria` devuelve `None` en el último caso. Ejecutar en rojo, implementar y ejecutar en
      verde. (NC «Registro aditivo»)
- [x] 1.5 **RED → GREEN** `acuerdo_con_mayoria`: prueba sintética de `3` casos (dos con
      coincidencia y uno sin mayoría) y anclaje real de `200/206`. Ejecutar en rojo, implementar
      y verificar `200`. (NC «Registro aditivo»)
- [x] 1.6 **RED → GREEN** `casos_sin_mayoria`: prueba con tres etiquetas distintas y anclaje real
      de los `6` identificadores `I033`, `I042`, `I056`, `I130`, `I194`, `I198`. Ejecutar en
      rojo, implementar y verificar la lista exacta. (NC «Registro aditivo»)
- [x] 1.7 **RED → GREEN** `rango_exactitud`: prueba con dos casos donde la predicción está entre
      las etiquetas y uno donde no; anclaje real `142`–`147`. Ejecutar en rojo, implementar y
      verificar que los aciertos mínimos son `142` y los máximos `147`. (NC «Registro aditivo»)
- [x] 1.8 **RED → GREEN** `metricas_por_clase_bajo_extremos`: prueba con una matriz sintética
      conocida en ambos extremos y anclaje real contra `metricas_por_clase` de la referencia
      vigente (`0,7024` de macro-F1 y la matriz de confusión). Ejecutar en rojo, implementar y
      verificar que el extremo vigente reproduce la referencia y que el extremo máximo cambia
      solo las celdas de los casos reasignados. (NC «Registro aditivo»)
- [x] 1.9 **TRIANGULATE**: agregar como pruebas los anclajes reales `200`, `6`, `142`, `147`,
      `64` y `206`, y la verificación de que los conjuntos se derivan de los archivos y no de
      constantes. Ejecutar y confirmar verde. (NC «Registro aditivo»)
- [x] 1.10 Implementar la lectura con SHA-256 (normalización LF), el aborto sin salidas si un
      anclaje difiere y la escritura de `analisis_arbitraje_mayoria_c224.json`, `.md` y
      `.SHA256SUMS.txt`. Prueba: forzar un anclaje roto y verificar que no se escribe ningún
      archivo. (NC «Registro aditivo»)
- [x] 1.11 **REFACTOR**: extraer constantes (los `6` identificadores como valor esperado de
      anclaje, el rango, la ruta de salidas) y eliminar duplicación; ejecutar las pruebas
      después de cada paso. (NC «Registro aditivo»)
- [x] 1.12 Correr el script dos veces desde la raíz y verificar salidas idénticas byte a byte y
      `git status` sin cambios fuera de `evaluation/data/campana/analisis/`. Comparar las cifras
      con el recomputo del design y registrar cualquier diferencia (manda el script). (NC
      «Registro aditivo»)
- [x] 1.13 Agregar la entrada del análisis al README de `evaluation/data/campana/analisis/` y
      verificar que la sección de c-224 figura con su comando y sus salidas. (NC «Registro
      aditivo»)

## 2. Memo canónico (sección `3.35`, aditiva)

- [x] 2.1 Agregar `### 3.N` (el primer número libre; ver 0.4) a
      `docs/Tesis/Correcciones/numeros-canonicos.md` con cada cifra del JSON de c-224: `200/206`
      de coincidencia; `6` casos sin mayoría con sus identificadores y sus tres etiquetas; el
      rango `142/206`–`147/206`; y las métricas por clase en ambos extremos. Cada valor con
      archivo, clave del JSON y comando; declarar el carácter aditivo. Verificar con un diff
      dirigido que solo se agregaron líneas. (NC «Registro aditivo»)
- [x] 2.2 Verificar que ningún valor ni estado de las secciones `3.1` a `3.33` cambió y
      registrar el resultado. (NC «Registro aditivo»)

## 3. Prosa

- [x] 3.1 `08-discusion.tex` (limitación 8, párrafo «Octavo»): agregar que la regla vigente
      coincide con la mayoría de `{E3, E4, E5}` en `200` de `206` casos y que los `6` restantes
      acotan la exactitud estricta entre `0,6893` y `0,7136`; conservar la fragilidad de la
      referencia como limitación de fondo. Verificar con `rg -n "200 de 206"`
      `08-discusion.tex`. (TD «Acotación en limitación»)
- [x] 3.2 `07-resultados.tex` (párrafo del arbitraje): agregar una oración con el rango
      `142/206`–`147/206`, rotulado como sensibilidad, y remitir a la sección `3.N` del memo;
      no cambiar las cifras vigentes del párrafo. Verificar con `rg -n "147/206"` y con un
      `git diff` que el resto del párrafo conserva `0,6893`, `0,7864`, `0,7489`, `0,7467` y
      `31/61`. (TD «Rango en resultados»)
- [x] 3.3 `10-recomendaciones.tex` (`subsec:corpus-independiente`): sustituir «con arbitraje por
      mayoría de tres etiquetadores, en lugar de la regla actual en que decide un único tercer
      etiquetador» por «con más etiquetadores independientes que permitan estimar la mayoría sin
      depender de un único tercer etiquetador». Verificar con `rg -n "más etiquetadores
      independientes"` y confirmar que `rg "mayoría de tres"` no devuelve coincidencias en ese
      archivo. (TD «Trabajo futuro»)
- [x] 3.4 Verificar que no hay otros cambios de prosa y que `rg -n "c-[0-9]{3}"` sobre
      `sections/*.tex` solo devuelve comentarios. (TD «Acotación en limitación»; TD «Rango en
      resultados»; TD «Trabajo futuro»)

## 4. Trazabilidad y cierre

- [x] 4.1 Agregar la sección de c-224 a `docs/Tesis/Correcciones/dictamen-correcciones.md` con
      las filas `C24/…` (script y pruebas, salidas, sección `3.N` del memo, los tres pasajes de
      prosa y el estado de la limitación 1). Verificar que cada archivo:línea existe y que el
      ancla figura en la línea indicada. (NC «Registro aditivo»; TD «Acotación en limitación»;
      TD «Rango en resultados»; TD «Trabajo futuro»)
- [x] 4.2 Ejecutar de nuevo `python -m pytest` de `evaluation/` desde su carpeta con las
      variables dummy del CI y confirmar que la suite queda en verde; si se compila la tesis,
      confirmar cero referencias indefinidas y cero etiquetas duplicadas. (NC «Registro
      aditivo»)
- [x] 4.3 Confirmar con `git diff --stat` contra la base que ningún corpus, predicción,
      configuración ni artefacto congelado cambió, y que las únicas modificaciones son las
      listadas en `proposal.md`. (NC «Registro aditivo»)
- [x] 4.4 Agregar la fase de c-224 a `CHANGES.md` y verificar que la entrada figura con el
      estado y las dependencias correspondientes. (NC «Registro aditivo»)