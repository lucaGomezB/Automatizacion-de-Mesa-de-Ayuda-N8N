# Tasks: Muestreo probabilistico del universo de incidentes

Al final de cada tarea, entre parentesis, el requisito del change que cumple, por nombre corto entre comillas angulares precedido de su capacidad: `PS` (`evaluation-probabilistic-sampling`), `TD` (`tesis-document`) y `NC` (`tesis-numeros-canonicos`). Nombres cortos: PS-001 «Universo y marco»; PS-002 «Cuotas prefijadas»; PS-003 «Etiquetado y consentimiento»; PS-004 «Estimacion al universo»; PS-005 «Efecto de diseno»; PS-006 «Herramienta offline»; TD «Declaracion del diseno»; NC «Registro aditivo». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Este change NO ejecuta la campana probabilistica: depende de datos que aun no existen y de la cooperacion de la organizacion (design D1, OQ2). El bloque de protocolo (grupo 1) es gobernanza **HIGH** y requiere checkpoint de los autores. El bloque de herramienta (grupo 2) aplica el ciclo TDD estricto (RED -> GREEN -> TRIANGULATE -> REFACTOR) sobre las funciones puras, con la suite de `evaluation/` como red de seguridad, y se ancla en la lectura ponderada vigente `0,7489`.

## 0. Preparacion y verificacion de estado

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D7) y los tres specs delta; cargar los `SKILL.md` completos de `python-testing`, `pytest-coverage` y `python-design-patterns` antes de escribir codigo y registrar la resolucion.
- [ ] 0.2 Capturar la linea de base como evidencia de partida: `git status`, `git rev-parse HEAD`, `sha256sum data/corpus_evaluacion_pseudonimizado.json evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.json`, y los anclajes (`0,7489`, bootstrap `[0,6822; 0,8099]`; vector de composicion `16/85/67/31/1`, suma `200`; `N = 2.646`) tomados de las Secciones 3.4, 3.25 y 3.32 del memo y de `07-resultados.tex:393`. Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [ ] 0.3 **Red de seguridad:** correr `cd evaluation && pytest -q` y registrar el resultado (debe pasar antes de editar; si algo falla, detenerse y reportarlo como fallo preexistente).
- [ ] 0.4 Releer `evaluation/linea_de_base.py::lectura_ponderada` y `prevalencia_natural`, `evaluation/metrics.py::intervalo_wilson` y los remuestreos de `evaluation/stats.py`; confirmar que el script puede leer la composicion del corpus y la lectura ponderada sin constantes.
- [ ] 0.5 **[CHECKPOINT DE LOS AUTORES — BLOQUEA EL GRUPO 1]** Confirmar el periodo del universo a muestrear y la definicion operacional de complejidad (OQ1); registrar la respuesta. Sin confirmacion, los grupos 2 a 5 pueden avanzar con las cifras del diseno en `condicional`, pero el grupo 1 no se cierra.
- [ ] 0.6 Releer el indice de `numeros-canonicos.md` y fijar el primer numero de seccion libre (hoy la ultima es `3.37`; esperado `3.40`). Registrar el numero elegido.

## 1. Protocolo del diseno muestral (HIGH)

- [ ] 1.1 Crear `docs/campana-medicion/protocolo-muestreo-probabilistico.md` con el universo (periodo, `N` y su derivacion), el marco muestral (registro operativo, procedimiento de inclusion enumerable) y los estratos (sector, canal, complejidad) con su definicion operacional, fijados ANTES de reunir la muestra. (PS-001 «Universo y marco»)
- [ ] 1.2 Documentar en el protocolo las cuotas prefijadas por canal y por sector, el tamano objetivo, los denominadores y las reglas de decision de tres vias, con su justificacion; declarar el tratamiento de la clase minoritaria y de los estratos de soporte pequeno. (PS-002 «Cuotas prefijadas»)
- [ ] 1.3 Documentar en el protocolo el etiquetado independiente (al menos dos etiquetadores distintos de los operadores y de los autores, ciegos a las predicciones; discordantes por consenso o tercer etiquetador), el registro de sujetos con alias y codigos sin datos identificatorios, y los requisitos de consentimiento informado y pseudonimizacion. (PS-003 «Etiquetado y consentimiento»)
- [ ] 1.4 Verificar que el protocolo NO usa la composicion del corpus de 200 como la del universo y que ningun valor de resultado se presenta como medido; registrar la verificacion (`rg` dirigido sobre el protocolo). (PS-001 «Universo y marco»)

## 2. Herramienta de estimacion (TDD)

- [ ] 2.1 **RED:** escribir `evaluation/data/campana/analisis/test_estimador_muestreo_probabilistico_c229.py` con pruebas sinteticas de `pesos_horvitz_thompson`, `post_estratificar`, `exactitud_ponderada`, `efecto_diseno` e `ic_bootstrap_universo` antes de existir el modulo; ejecutar y confirmar que fallan por ausencia de la implementacion. (PS-006 «Herramienta offline»)
- [ ] 2.2 **GREEN:** implementar `estimador_muestreo_probabilistico_c229.py` con la minima logica para pasar las pruebas; reutilizar `evaluation/metrics.py` y `evaluation/stats.py` sin modificarlos. (PS-004 «Estimacion al universo», PS-005 «Efecto de diseno»)
- [ ] 2.3 **TRIANGULATE:** agregar casos con entradas distintas (pesos iguales y desiguales; cuotas proporcionales y no proporcionales; una clase minoritaria; efecto de diseno mayor y menor que 1) y confirmar que GENERALIZA sin romper. (PS-004 «Estimacion al universo», PS-005 «Efecto de diseno»)
- [ ] 2.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (PS-006 «Herramienta offline»)
- [ ] 2.5 Implementar el `main()`: leer `data/corpus_evaluacion_pseudonimizado.json` y `analisis_propagacion_arbitraje_c221.json`, verificar el anclaje de D4 (abortar sin escribir si la post-estratificacion por la composicion del corpus de 200 no reproduce `0,7489` y su bootstrap), emitir `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF), con los pesos de procedencia, la exactitud ponderada y el efecto de diseno rotulados y en estado `condicional` para el diseno no computable. (PS-004 «Estimacion al universo», PS-005 «Efecto de diseno»)
- [ ] 2.6 Correr el script dos veces y confirmar salidas identicas byte a byte; verificar que no hay red, Gemini ni escritura fuera de los tres nombres fijos; registrar los SHA-256. (PS-006 «Herramienta offline»)
- [ ] 2.7 Agregar la entrada del nuevo artefacto en `evaluation/data/campana/analisis/README.md` (solo si el README exige declarar cada salida; si no, registrar la decision). (PS-006 «Herramienta offline»)

## 3. Memo canonico (NC)

- [ ] 3.1 Agregar la seccion aditiva `### 3.N` (ver 0.6) con la lectura ponderada `0,7489` y su bootstrap con la aclaracion de que sus pesos son la composicion del corpus de 200 y NO la del universo; el efecto de diseno de la post-estratificacion sobre el corpus con metodo y procedencia, estado `condicional`; el universo, el marco y los estratos del diseno como plan; y la declaracion de dependencia de datos inexistentes. Declarar que no mide de nuevo y que no cambia ninguna cifra. (NC «Registro aditivo»)
- [ ] 3.2 Verificar con `git diff` dirigido que la seccion es aditiva: solo lineas agregadas, sin reescritura de las Secciones 3.1 a 3.37; y que el efecto de diseno del diseno probabilistico figura como no computable, sin valor estimado. (NC «Registro aditivo»)

## 4. Prosa de la tesis (TD)

- [ ] 4.1 Agregar en `04-marco-metodologico.tex` (`subsec:poblacion-muestra-corpus`) un parrafo que declare el diseno probabilistico estratificado planificado, su estado `condicional`, la dependencia de datos nuevos y que no eleva la exactitud del clasificador sino que valida la estimacion. No crear subseccion. (TD «Declaracion del diseno»)
- [ ] 4.2 Agregar en `07-resultados.tex` (subseccion de validacion fuera de muestra, junto a `:393`) el efecto de diseno rotulado como complementario y `condicional`, sin cambiar la cifra primaria `0,6893` ni la ponderada `0,7489`. (TD «Declaracion del diseno»)
- [ ] 4.3 Precisar en la amenaza 5 (`04-marco-metodologico.tex:114`) y en la limitacion de seleccion de `08-discusion.tex` que el diseno probabilistico existe como plan y no elimina el sesgo sin datos. (TD «Declaracion del diseno»)
- [ ] 4.4 Remitir en `10-recomendaciones.tex` (`subsec:corpus-independiente`) al diseno probabilistico con cuotas prefijadas por canal y sector y al IC sobre el universo completo, sin excluir casos. (TD «Declaracion del diseno»)
- [ ] 4.5 Verificar que la tesis no afirma que la muestra de 200 es probabilistica ni que su IC se estima sobre el universo; que `71,2 %`, `[67,2 %; 74,6 %]`, `73,5 %`, `0,6508`, `0,6893` y `0,7489` siguen siendo los valores vigentes; que no se introdujeron identificadores `c-NNN` fuera de comentarios (`rg -n "c-[0-9]{3}" sections/*.tex`) y que las referencias nuevas resuelven. (TD «Declaracion del diseno»)
- [ ] 4.6 Compilar con XeLaTeX (`latexmk -xelatex main.tex`), verificar `\@abspage@last`, cero referencias indefinidas y cero etiquetas duplicadas; si un parrafo empuja una pagina, compensar dentro del mismo bloque. Si el entorno no tiene LaTeX, registrar la compilacion como tarea diferida al release. (TD «Declaracion del diseno»)

## 5. Trazabilidad y verificacion de cierre

- [ ] 5.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada del change con el protocolo nuevo, el artefacto nuevo, la seccion del memo y las anclas de prosa (archivo:linea y frase verificable). (NC «Registro aditivo»)
- [ ] 5.2 Volver a correr `cd evaluation && pytest -q` y confirmar que no hay regresiones; correr el script una vez mas y comparar SHA-256 con 2.6.
- [ ] 5.3 Confirmar con `git diff --stat` que no cambiaron `App/`, `n8n/`, el clasificador, la configuracion, el corpus, las predicciones ni los artefactos congelados.
- [ ] 5.4 Correr `openspec validate c-229-muestreo-probabilistico-del-universo-de-incidentes --strict` y verificar que pasa.
- [ ] 5.5 Dejar a cargo del orquestador la actualizacion de `CHANGES.md` y el `engram sync`; no pushear, no crear tag ni release.
- [ ] 5.6 Guardar en Engram el resumen del change con el nombre, el protocolo, el artefacto, la seccion del memo, los SHA-256 y el resultado de las verificaciones; reportar al orquestador con la tabla de evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 2.1-2.4 | `evaluation/data/campana/analisis/test_estimador_muestreo_probabilistico_c229.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | pesos iguales/desiguales, cuotas proporcionales/no, clase minoritaria, DEFF > 1 y < 1 | limpio |
