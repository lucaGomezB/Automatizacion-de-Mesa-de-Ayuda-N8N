# Tasks: Consolidar el rango de robustez de los tiempos

Al final de cada tarea, entre paréntesis, el requisito del change que cumple, por nombre corto entre comillas angulares precedido de su capacidad: `TD` (`tesis-document`) y `NC` (`tesis-numeros-canonicos`). Nombres cortos: TD «Rango de robustez»; NC «Registro aditivo». Las tareas de preparación y las verificaciones transversales no llevan paréntesis.

Este change SÍ escribe un script de análisis ejecutable: aplica el ciclo TDD estricto (RED → GREEN → TRIANGULATE → REFACTOR) sobre las funciones puras, con la suite de `evaluation/` como red de seguridad. No mide de nuevo: lee el corpus versionado, `evaluation/stats.py` y `resultados.json`.

## 0. Preparación y verificación de estado

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D6) y los dos specs delta; cargar los `SKILL.md` completos de `python-testing` y `pytest-coverage` antes de escribir código y registrar la resolución.
- [ ] 0.2 Capturar la línea de base como evidencia de partida: `git status`, `git rev-parse HEAD`, `sha256sum data/corpus_evaluacion_pseudonimizado.json evaluation/data/campana/analisis/resultados.json`, y los anclajes canónicos (`71,16 %`, `68,61 %`, `65,57 %`; `76,98/51,07/93,44 %`; `199/200`, `180/200`; `O1 33,8 %`, `O2 79,7 %`, agregado `69,3 %`; efecto de posición) tomados de las Secciones 3.8 y 3.14 del memo. Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [ ] 0.3 **Red de seguridad:** correr `cd evaluation && pytest -q` y registrar el resultado (debe pasar antes de editar; si algo falla, detenerse y reportarlo como fallo preexistente).
- [ ] 0.4 Releer `evaluation/stats.py` (`reduccion_relativa`, `escenario_sensibilidad`, `granularidad_manual`) y las claves de tiempos por operador y de posición de `resultados.json`; confirmar que el script puede leerlas sin constantes.
- [ ] 0.5 **[CHECKPOINT DE LOS AUTORES — BLOQUEA EL GRUPO 3]** Confirmar D1/OQ1: el «escenario que minimiza» es el descuento de `10 s` (`65,6 %`) para el estimando primario, y `33,8 %` (operador) y `51,1 %` (canal) se informan como cotas de alcance. Registrar la respuesta.
- [ ] 0.6 Releer el índice de `numeros-canonicos.md` y fijar el primer número de sección libre (hoy la última es `3.36`; esperado `3.37`). Registrar el número elegido.

## 1. Script de consolidación (TDD)

- [ ] 1.1 **RED:** escribir `evaluation/data/campana/analisis/test_analisis_rango_robustez_tiempos_c226.py` con pruebas sintéticas de `rango_descuentos`, `resumen_por_canal`, `resumen_por_operador`, `resumen_posicion` y `cota_instrumento` antes de existir el módulo; ejecutar y confirmar que fallan por ausencia de la implementación. (NC «Registro aditivo»)
- [ ] 1.2 **GREEN:** implementar `analisis_rango_robustez_tiempos_c226.py` con la mínima lógica para pasar las pruebas; reutilizar `evaluation/stats.py` sin modificarlo. (NC «Registro aditivo»)
- [ ] 1.3 **TRIANGULATE:** agregar casos con entradas distintas (sin descuento, `5 s`, `10 s`; los tres canales; `O1`/`O2`/agregado; `5 s`/`10 s` de granularidad) y confirmar que GENERALIZA sin romper. (NC «Registro aditivo»)
- [ ] 1.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (NC «Registro aditivo»)
- [ ] 1.5 Implementar el `main()`: leer el corpus y `resultados.json`, verificar los anclajes de D2 (abortar sin escribir si no reproducen), emitir `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF). (NC «Registro aditivo»)
- [ ] 1.6 Correr el script dos veces y confirmar salidas idénticas byte a byte; verificar que no hay red, Gemini ni escritura fuera de los tres nombres fijos; registrar los SHA-256. (NC «Registro aditivo»)
- [ ] 1.7 Agregar la entrada del nuevo artefacto en `evaluation/data/campana/analisis/README.md` (solo si el README exige declarar cada salida; si no, registrar la decisión). (NC «Registro aditivo»)

## 2. Memo canónico (NC)

- [ ] 2.1 Agregar la sección aditiva `### 3.N` (ver 0.6) con el rango primario y el mínimo, la tabla por canal, la tabla por operador, el efecto de posición y la cota del instrumento; cada valor con procedencia, estado y comando; declarar que no mide de nuevo ni cambia la cifra primaria. (NC «Registro aditivo»)
- [ ] 2.2 Verificar con `git diff` dirigido que la sección es aditiva: solo líneas agregadas, sin reescritura de las Secciones 3.1 a 3.36. (NC «Registro aditivo»)

## 3. Prosa de la tesis (TD; tras 0.5)

- [ ] 3.1 Agregar en `07-resultados.tex`, dentro de `subsec:comparacion-tiempos` y después del párrafo de sensibilidad (`:63`), la tabla `tab:rango-robustez-tiempos` o, si la paginación lo impide, el párrafo compacto con el rango y el mínimo; incluir la nota de sensibilidad y de no comparabilidad. No crear subsección ni cambiar la enumeración de `:6`. (TD «Rango de robustez»)
- [ ] 3.2 Agregar en `08-discusion.tex:22-24` la remisión a la síntesis y la frase con el rango `[65,6 %; 71,2 %]`, su mínimo `65,6 %` y las lecturas adversas de operador y canal rotuladas; conservar las cifras existentes. (TD «Rango de robustez»)
- [ ] 3.3 Precisar en la limitación de tiempos de `08-discusion.tex` (subsección de limitaciones) el alcance del rango y que no elimina la asimetría de instrumentos ni el orden fijo. (TD «Rango de robustez»)
- [ ] 3.4 Agregar en `04-marco-metodologico.tex:106` (amenaza 1) una oración que remita a la síntesis y declare que el rango acota la magnitud pero no estima el efecto de orden. (TD «Rango de robustez»)
- [ ] 3.5 Verificar que `71,2 %` y `[67,2 %; 74,6 %]` siguen siendo la cifra primaria; que no se introdujeron identificadores `c-NNN` fuera de comentarios (`rg -n "c-[0-9]{3}" sections/*.tex`) y que las referencias a `tab:rango-robustez-tiempos` resuelven. (TD «Rango de robustez»)
- [ ] 3.6 Compilar con XeLaTeX (`latexmk -xelatex main.tex`), verificar `\@abspage@last`, cero referencias indefinidas y cero etiquetas duplicadas; si la tabla empuja una página, compensar dentro del mismo bloque. Si el entorno no tiene LaTeX, registrar la compilación como tarea diferida al release. (TD «Rango de robustez»)

## 4. Trazabilidad (NC)

- [ ] 4.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada del change con el artefacto nuevo, la sección del memo y las anclas de prosa (archivo:línea y frase verificable). (NC «Registro aditivo»)

## 5. Verificación de cierre

- [ ] 5.1 Volver a correr `cd evaluation && pytest -q` y confirmar que no hay regresiones; correr el script una vez más y comparar SHA-256 con 1.6.
- [ ] 5.2 Confirmar con `git diff --stat` que no cambiaron `App/`, `n8n/`, el clasificador, la configuración, el corpus, las predicciones ni los artefactos congelados.
- [ ] 5.3 Correr `openspec validate c-226-consolidar-el-rango-de-robustez-de-tiempos --strict` y verificar que pasa.
- [ ] 5.4 Dejar a cargo del orquestador la actualización de `CHANGES.md` y el `engram sync`; no pushear, no crear tag ni release.
- [ ] 5.5 Guardar en Engram el resumen del change con el nombre, el artefacto, la sección del memo, los SHA-256 y el resultado de las verificaciones; reportar al orquestador con la tabla de evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1-1.4 | `evaluation/data/campana/analisis/test_analisis_rango_robustez_tiempos_c226.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | casos 5/10 s, canal, operador, granularidad | limpio |