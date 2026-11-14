Al final de cada tarea, entre paréntesis, los requisitos del change que cumple, por nombre corto entre comillas angulares precedido de su capacidad: `EF` (`evaluation-framework`), `NC` (`tesis-numeros-canonicos`) y `TD` (`tesis-document`). Nombres cortos: EF «Recomputo»; NC «Registro aditivo»; TD «Balance neto», TD «Registro canonico», TD «Linea futura» y TD «Viabilidad operativa». Las tareas de preparación y las verificaciones transversales no llevan paréntesis. La sección nueva del memo toma el primer número libre al aplicar (ver 0.3); ninguna tarea lo hardcodea.

## 0. Preparación y trazabilidad de entradas

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D7) y los tres specs delta; leer `.agents/SKILLS.md` y cargar `python-testing-patterns` y `python-design-patterns`; registrar qué skills se cargaron.
- [ ] 0.2 Capturar la línea de base: conteo de palabras del resumen y del *abstract* con la regla de c-106; `rg -n "10 a 15 min|estimación propia|69,51|5 min|10 min|15 min"` sobre `sections/*.tex`; SHA-256 de `analisis_costo_derivacion_c220.json`, `analisis_propagacion_arbitraje_c221.json` y `analisis_dictamen_c207.json`; `git status` limpio. Guardar como evidencia de partida.
- [ ] 0.3 Releer el índice de `numeros-canonicos.md` y fijar el primer número libre de la sección nueva (hoy la última es `3.32`, esperado `3.33`); registrar el número elegido. (NC «Registro aditivo»)
- [ ] 0.4 **[CHECKPOINT DE LOS AUTORES — BLOQUEA EL GRUPO 3]** Presentar la lectura central con el `c` medido y el cambio de estatus de la viabilidad operativa (de condicional a la que el intervalo sostenga) y registrar la conformidad antes de editar `00`, `08`, `09`, `10` y `12`. Sin respuesta, las tareas del grupo 3 no se ejecutan.

## 1. Análisis offline (TDD estricto)

- [ ] 1.1 **RED**: escribir `evaluation/data/campana/analisis/test_analisis_balance_neto_c222.py` con casos sintéticos de `balance_neto`, `exactitud_equilibrio`, `ic_bootstrap_condicional` y `suma_de_extremos` (signos, esquinas y misma semilla); verificar que falla por ausencia del módulo. (EF «Recomputo»)
- [ ] 1.2 **GREEN**: implementar lo mínimo de cada función pura reutilizando `evaluation/metrics.remuestreos_indices` y `percentil_intervalo`; verificar que los tests de 1.1 pasan. (EF «Recomputo»)
- [ ] 1.3 **TRIANGULATE**: agregar el intervalo condicional con `c` fijo, la suma de extremos sobre las cuatro esquinas y dos corridas con la misma semilla; verificar verde sin ampliar el código más de lo necesario. (EF «Recomputo»)
- [ ] 1.4 Implementar los anclajes que abortan antes de escribir (`+25,4 / +18,7 / +11,9`, `69,51 s` y los tres IC de la `3.21` `[+8,6; +42,4]`, `[-15,0; +52,5]`, `[-38,6; +62,7]`) leídos de los artefactos versionados; verificar con un anclaje roto forzado que no se escribe ningún archivo. (EF «Recomputo»)
- [ ] 1.5 Leer las entradas con SHA-256 desde los artefactos (sin constantes) y emitir `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF, claves ordenadas) con remuestreos `B = 2000`, semilla `20261021`, nivel `0,95`; contrastar `B` central `≈ +30,6 h-persona` y `a* ≈ 19,7 %`. (EF «Recomputo»)
- [ ] 1.6 **REFACTOR**: extraer las constantes (anclajes, semilla, nivel, rejilla superada) y eliminar duplicación; ejecutar las pruebas después de cada paso. (EF «Recomputo»)
- [ ] 1.7 Correr el script dos veces desde la raíz y verificar salidas idénticas byte a byte y `git status` sin cambios fuera de `evaluation/data/campana/analisis/`. (EF «Recomputo»)

## 2. Memo canónico (sección aditiva)

- [ ] 2.1 Agregar `### 3.N` (primer libre; ver 0.3) a `docs/Tesis/Correcciones/numeros-canonicos.md` con insumos, fórmulas de `B` y `a*`, `B` y `a*` con el `c` medido, método de propagación y ambos intervalos, y estado `{vigente, condicional, retirado}` y procedencia (`archivo:línea` o comando) por valor; declarar el reemplazo del supuesto «10 a 15 minutos» y la grilla como sensibilidad superada con sus cifras. (NC «Registro aditivo»; TD «Registro canonico»)
- [ ] 2.2 Agregar la remisión desde la `3.21` con líneas agregadas (sin reescribirla) y verificar con `git diff` acotado que ninguna sección `3.1`–`3.32` cambia de cifra ni estado. (NC «Registro aditivo»)
- [ ] 2.3 Verificar que el comando de recálculo reproduce `B` y `a*` del escenario medido y de cada celda de la rejilla, y que la convención de redondeo queda declarada. (TD «Registro canonico»)

## 3. Prosa de la tesis (bloque C, tras 0.4)

- [ ] 3.1 `08-discusion.tex:84`: reemplazar el `c = 10 a 15 min` por `c = 69,51 s` e IC `[33,42; 106,56] s` como insumo central, con remisión a la sección nueva, y rotular el supuesto como reemplazado. (TD «Balance neto»)
- [ ] 3.2 `08-discusion.tex:107`: conservar y rotular como sensibilidad del supuesto superado las cifras `304`, `50,7/76,1 h` y `-18,5/-43,9 h`. (TD «Balance neto»)
- [ ] 3.3 `08-discusion.tex:111`: pasar la fila del `c` medido a lectura central e informar el intervalo combinado y el condicional; enunciar el signo solo si el intervalo lo fija. (TD «Balance neto»)
- [ ] 3.4 `tab:balance-neto`: fila central = `c` medido; grilla rotulada como superada con sus cifras; nota con el método de propagación y el redondeo. (TD «Balance neto»)
- [ ] 3.5 `08-discusion.tex:117`: declarar la viabilidad operativa con el signo y el rango que el intervalo sostenga y remitir a `subsec:balance-neto`. (TD «Viabilidad operativa»)
- [ ] 3.6 `00-resumen.tex` (ES y EN): alinear la lectura y el signo con la discusión; verificar ≤ 34 palabras (ES) y ≤ 31 (EN) y que el conteo no aumenta. (TD «Viabilidad operativa»)
- [ ] 3.7 `09-conclusiones.tex:6`, `:22` y `:24`: alinear la lectura del balance y la viabilidad operativa con el intervalo y remitir a `subsec:balance-neto`. (TD «Viabilidad operativa»)
- [ ] 3.8 `10-recomendaciones.tex`: presentar el cronometraje de reasignaciones como refinamiento del tramo largo de `c`, no como condición para cerrar el balance. (TD «Linea futura»)
- [ ] 3.9 **[CONDICIONAL]** `12-anexos.tex`: si existe una mención del balance, alinearla; si no, dejarlo sin cambios y retirarlo del alcance. Registrar la decisión. (TD «Balance neto»)
- [ ] 3.10 Verificar con `rg` en `00`, `08`, `09`, `10` y `12`: cero «10 a 15 minutos» como insumo y «estimación propia» para `c`; cifra medida y remisión presentes; `subsec:balance-neto` y `tab:balance-neto` únicos; misma lectura y signo; y que `a* ≈ 19,7 %` no se presenta como fundamento del 85 %. (TD «Balance neto»; TD «Viabilidad operativa»)
- [ ] 3.11 Compilar con XeLaTeX y verificar cero referencias indefinidas y cero etiquetas duplicadas. (TD «Balance neto»)

## 4. Trazabilidad y verificación de cierre

- [ ] 4.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada que cierra la decisión (i) de D5 de c-220 y la observación del dictamen v1.3.0, con los archivos afectados.
- [ ] 4.2 Agregar las filas `C22/…` (archivo, línea, etiqueta y frase ancla por cada artefacto) y verificar con `python3 docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` que las anclas resuelven.
- [ ] 4.3 Verificar con `git diff` acotado al memo que las secciones `3.1`–`3.32` quedan intactas y que solo hay líneas agregadas más la remisión.
- [ ] 4.4 Ejecutar `python "docs/Tesis/v10 (IA)/verify_citations.py"` y confirmar que las citas resuelven.
- [ ] 4.5 Correr `openspec validate c-222-recalcular-el-balance-neto-con-el-costo-medido --strict` y verificar que pasa.
- [ ] 4.6 Confirmar con `git diff --stat` que ningún corpus, predicción, clasificador, `App/`, `n8n/` ni `docker-compose.yml` cambió ni ningún artefacto congelado.
