# Tasks: Referencia por mayoria con etiquetadores independientes

Al final de cada tarea, entre parentesis, el requisito del change que cumple, por nombre corto entre
comillas angulares precedido de su capacidad: `DA` (`discordant-arbitration`), `EF`
(`evaluation-framework`), `OOS` (`evaluation-out-of-sample-validation`), `TD` (`tesis-document`) y
`NC` (`tesis-numeros-canonicos`). Nombres cortos: DA «Referencia por mayoria», DA «Registro y
consentimiento», DA «Cobertura y cegado», DA «Artefactos versionados»; EF «Kappa de Fleiss»; OOS
«Recompto y comparacion»; TD «Referencia por mayoria divulgada», TD «Registro y consentimiento», TD
«Trabajo futuro actualizado»; NC «Registro aditivo». Las tareas de preparacion y las verificaciones
transversales no llevan parentesis.

Este change DEPENDE del trabajo de campo de los autores (convocatoria de `3` etiquetadores
independientes y su consentimiento). Las tareas 2 a 6 se ejecutan una vez que el campo concluye;
sin campo, el change queda bloqueado y se declara la limitacion. Este change SI escribe codigo
ejecutable (kappa de Fleiss y constructor de la referencia): aplica el ciclo TDD estricto
(RED -> GREEN -> TRIANGULATE -> REFACTOR) sobre las funciones puras, con la suite de `evaluation/`
como red de seguridad. No mide de nuevo el clasificador: usa las predicciones congeladas.

## 0. Preparacion y linea de base

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D10) y los cinco specs delta; cargar los `SKILL.md`
      completos de `python-testing` y `python-design-patterns` antes de escribir codigo y registrar la
      resolucion.
- [ ] 0.2 Capturar la linea de base: `git status`, `git rev-parse HEAD` y `sha256sum` de
      `evaluation/data/campana/doble_etiquetado_arbitrado.csv`,
      `evaluation/data/campana/arbitraje_tres_vias.json`,
      `evaluation/data/campana/corpus_independiente_arbitrado.json` y
      `evaluation/data/campana/predicciones_arbitrado.json`; registrar los anclajes canonicos
      (`142/206`, `0,6893`, macro-F1 `0,7024`, `64` arbitrados, `6` de tres vias, kappa `E3`/`E4`
      `0,6055`). Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [ ] 0.3 **Red de seguridad:** correr `cd evaluation && pytest -q` (con las variables dummy del CI) y
      registrar el resultado; si algo falla antes de empezar, detenerse y reportarlo como fallo
      preexistente.
- [ ] 0.4 Releer `evaluation/kappa.py`, `evaluation/arbitraje.py`, `evaluation/doble_etiquetado.py`,
      `evaluation/campana.py::validar_registro_sujetos` y las claves de
      `arbitraje_tres_vias.json`; confirmar que el modulo nuevo puede reutilizarlos sin cambiar sus
      contratos.
- [ ] 0.5 Releer el indice de `docs/Tesis/Correcciones/numeros-canonicos.md` y fijar el primer numero
      de seccion libre (hoy la ultima es `3.37`; esperado `3.39`) y registrarlo. Verificar que no
      existe ya.
- [ ] 0.6 **[CHECKPOINT DE LOS AUTORES — BLOQUEA LA TAREA 1]** Resolver OQ1 y OQ2 del design: cantidad
      de etiquetadores (`5` recomendado frente al minimo `3`) y cobertura (corpus completo `206`
      frente a los `64` divergentes). Registrar la respuesta.

## 1. Regla declarada antes de ver las etiquetas

- [ ] 1.1 Fijar en `docs/campana-medicion/runbook-referencia-mayoria.md` la regla deterministica:
      mayoria `>= 3` de `5`; tratamiento de los casos `sin_mayoria` con la regla de respaldo
      (referencia vigente de arbitro unico, rotulada); conjunto laxo por `>= 3` de `5`; y confirmacion
      de OQ3. Declarar la fecha, anterior al etiquetado de `E6`-`E8`. (DA «Referencia por mayoria»)
- [ ] 1.2 Verificar con `git log`/fecha que la regla quedo fijada antes de cualquier etiqueta nueva y
      registrar la evidencia. (DA «Referencia por mayoria»)

## 2. Sujetos y consentimiento (bloque HIGH)

- [ ] 2.1 Agregar a `evaluation/data/campana/registro_sujetos.csv` las filas `E6,etiquetador,P12`,
      `E7,etiquetador,P13`, `E8,etiquetador,P14`; verificar con `validar_registro_sujetos` que no hay
      solape por `persona` ni alias con mas de un rol. Sin nombres, correos ni legajos. (DA «Registro y
      consentimiento»)
- [ ] 2.2 Extender `docs/campana-medicion/confirmacion-posterior-consentimiento.md` para admitir los
      alias `E6`, `E7` y `E8` y registrar su informacion verbal, confirmacion escrita y custodia.
      Verificar que no figura ningun nombre real ni la correspondencia alias-identidad. (TD «Registro y
      consentimiento»)
- [ ] 2.3 Confirmar que cada etiquetador nuevo tiene consentimiento registrado antes de usar sus
      etiquetas; si falta, excluirlo de la referencia y declarar la limitacion. (DA «Registro y
      consentimiento»)

## 3. Modulos y pruebas (TDD estricto)

- [ ] 3.1 **RED** `evaluation/tests/test_kappa_fleiss.py`: pruebas sinteticas de `kappa_fleiss` (matriz
      de conteos conocida) y de `matriz_acuerdo_por_pares`; ejecutar y confirmar que fallan por
      ausencia de implementacion. (EF «Kappa de Fleiss»)
- [ ] 3.2 **GREEN** implementar `kappa_fleiss` y `matriz_acuerdo_por_pares` en `evaluation/kappa.py`
      con la minima logica; no modificar el contrato de `kappa_doble_etiquetado`. (EF «Kappa de
      Fleiss»)
- [ ] 3.3 **TRIANGULATE** agregar casos con cobertura variable por caso, con `P_e = 1` (no estimable)
      y con los cinco etiquetadores; confirmar que generaliza. (EF «Kappa de Fleiss»)
- [ ] 3.4 **REFACTOR** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar
      verde. (EF «Kappa de Fleiss»)
- [ ] 3.5 **RED** `evaluation/tests/test_mayoria.py`: pruebas sinteticas de `mayoria` (mayoria absoluta,
      empate `2-2-1`, `2-1-1-1`) antes de existir el modulo; ejecutar y confirmar que fallan. (DA
      «Referencia por mayoria»)
- [ ] 3.6 **GREEN** implementar `evaluation/mayoria.py` (`mayoria`, `construir_referencia_mayoria`,
      `ensamblar_mayoria`) reutilizando `doble_etiquetado.py` y `arbitraje.py` sin cambiar sus
      contratos; emitir `referencia_mayoria.json` y su sidecar. (DA «Referencia por mayoria»; DA
      «Artefactos versionados»)
- [ ] 3.7 **TRIANGULATE** cubrir mayoria completa, cobertura parcial y `sin_mayoria` con respaldo;
      confirmar que generaliza. (DA «Referencia por mayoria»)
- [ ] 3.8 **REFACTOR** limpiar y correr la suite de `evaluation/` completa como red de seguridad. (DA
      «Referencia por mayoria»)

## 4. Campo ciego y artefactos

- [ ] 4.1 Generar la hoja ciega con `python -m evaluation.arbitraje hoja-ciega` para los casos de la
      cobertura decidida (corpus completo o los `64` divergentes); verificar encabezado
      `id_caso,descripcion` y conteo. (DA «Cobertura y cegado»)
- [ ] 4.2 Entregar el paquete ciego (`hoja ciega` + copia vacia de
      `evaluation/data/plantilla_etiquetado.csv` + codebook congelado) a `E6`, `E7` y `E8`; registrar
      que no vieron etiquetas de `E3`/`E4`/`E5`, la referencia ni predicciones. (DA «Cobertura y
      cegado»)
- [ ] 4.3 Unir las planillas en `evaluation/data/campana/doble_etiquetado_mayoria.csv` (un encabezado,
      UTF-8 sin BOM, LF), validar con el validador correspondiente y ensamblar la referencia con
      `ensamblar_mayoria`; registrar el conteo de `sin_mayoria` y los casos `tres_vias` remanentes.
      (DA «Cobertura y cegado»; DA «Artefactos versionados»)
- [ ] 4.4 Versionar `doble_etiquetado_mayoria.csv`, `referencia_mayoria.json` y su sidecar con SHA-256
      en `evaluation/data/campana/README.md`; declarar la cobertura efectiva y el `estado_cegado`. (DA
      «Artefactos versionados»)

## 5. Recomputo y comparacion honesta

- [ ] 5.1 **RED** `evaluation/data/campana/analisis/test_analisis_referencia_mayoria_c230.py`: pruebas
      sinteticas de las funciones puras (lecturas de exactitud y metricas por clase, delta, veredicto
      por lectura) antes del modulo; ejecutar y confirmar que fallan. (OOS «Recompto y comparacion»)
- [ ] 5.2 **GREEN** implementar `analisis_referencia_mayoria_c230.py` reutilizando
      `evaluation/metrics.py` y `evaluation/kappa.py` sin modificarlos. (OOS «Recompto y comparacion»)
- [ ] 5.3 **TRIANGULATE** cubrir distintos casos conocidos (sin cambio, cambio de acierto a error,
      cambio de error a acierto) y el Fleiss con cobertura parcial. (OOS «Recompto y comparacion»)
- [ ] 5.4 **REFACTOR** limpiar y correr la suite de `evaluation/`. (OOS «Recompto y comparacion»)
- [ ] 5.5 Implementar el `main()`: leer `referencia_mayoria.json`,
      `corpus_independiente_arbitrado.json` y `predicciones_arbitrado.json`; reproducir los anclajes
      `142/206` y `0,7024` (abortar sin escribir si no coinciden); emitir
      `analisis_referencia_mayoria_c230.{json,md,SHA256SUMS.txt}` con las dos lecturas, el delta y el
      veredicto por lectura. (OOS «Recompto y comparacion»)
- [ ] 5.6 Correr el script dos veces y confirmar salidas identicas byte a byte; verificar que no hay
      red, Gemini ni escritura fuera de los tres nombres fijos; registrar los SHA-256. (OOS «Recompto y
      comparacion»)

## 6. Memo canonico (NC)

- [ ] 6.1 Agregar la seccion aditiva `### 3.N` (ver 0.5) con la composicion y el umbral de la
      referencia, el conteo y los identificadores de `sin_mayoria`, el Fleiss y la matriz por pares, y
      las dos lecturas (mayoria y vigente) de exactitud estricta y macro-F1 con IC de Wilson, el delta
      y el veredicto por lectura; cada valor con procedencia, estado y comando. Declarar que la
      referencia por mayoria reemplaza como primaria a la de arbitro unico en el `31 %` y que ambas
      lecturas se conservan. (NC «Registro aditivo»)
- [ ] 6.2 Verificar con `git diff` dirigido que la seccion es aditiva: solo lineas agregadas, sin
      reescritura de las secciones anteriores. (NC «Registro aditivo»)

## 7. Prosa de la tesis (TD)

- [ ] 7.1 `04-marco-metodologico.tex`: describir la referencia como mayoria de cinco con umbral, regla
      de respaldo y conteo `sin_mayoria`; retirar la descripcion de la decision de un unico tercer
      etiquetador. (TD «Referencia por mayoria divulgada»)
- [ ] 7.2 `07-resultados.tex`: informar las dos lecturas con sus intervalos y el delta, el kappa de
      Fleiss rotulado y el veredicto del umbral por lectura; no ocultar el cambio de la cifra primaria.
      (TD «Referencia por mayoria divulgada»)
- [ ] 7.3 `08-discusion.tex`: acotar la limitacion de la referencia (ya no depende de un unico arbitro
      en el `31 %`, cobertura efectiva y `sin_mayoria`) sin sobreafirmar. (TD «Referencia por mayoria
      divulgada»)
- [ ] 7.4 `11-aspectos-legales.tex` (`subsec:consentimiento-derechos`): declarar `E6`, `E7` y `E8` por
      alias, la informacion verbal, la confirmacion escrita y la custodia; sin nombres reales. (TD
      «Registro y consentimiento»)
- [ ] 7.5 `10-recomendaciones.tex`: retirar la linea que propone conseguir mas etiquetadores
      independientes como trabajo futuro y reformularla con criterio de exito. (TD «Trabajo futuro
      actualizado»)
- [ ] 7.6 Verificar que `142/206`, `0,6893`, `0,7024` y el veredicto previo del umbral conservan su
      valor como referencia vigente; que no se introdujeron identificadores `c-NNN` fuera de comentarios
      (`rg -n "c-[0-9]{3}" sections/*.tex`) y que las remisiones resuelven. (TD «Referencia por mayoria
      divulgada»)
- [ ] 7.7 Compilar con XeLaTeX (`latexmk -xelatex main.tex`), verificar `\@abspage@last`, cero
      referencias indefinidas y cero etiquetas duplicadas; si la tabla empuja una pagina, compensar
      dentro del mismo bloque. Si el entorno no tiene LaTeX, registrar la compilacion como diferida al
      release. (TD «Referencia por mayoria divulgada»)

## 8. Trazabilidad y verificacion de cierre

- [ ] 8.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la seccion `C30/…` con el
      modulo y las pruebas, las salidas, la seccion del memo, los pasajes de prosa y el estado de la
      limitacion del arbitro unico. (NC «Registro aditivo»)
- [ ] 8.2 Volver a correr `cd evaluation && pytest -q` y confirmar que no hay regresiones; correr el
      script una vez mas y comparar SHA-256 con 5.6.
- [ ] 8.3 Confirmar con `git diff --stat` que no cambiaron `App/`, `n8n/`, el clasificador, la
      configuracion, el corpus de ajuste, las predicciones congeladas ni `evaluation/report.md`.
- [ ] 8.4 Correr `openspec validate c-230-referencia-por-mayoria-con-etiquetadores-independientes
      --strict` y verificar que pasa.
- [ ] 8.5 Dejar a cargo del orquestador la actualizacion de `CHANGES.md` y el `engram sync`; no
      pushear, no crear tag ni release.
- [ ] 8.6 Guardar en Engram el resumen del change con el nombre, los artefactos, la seccion del memo,
      los SHA-256 y el resultado de las verificaciones; reportar al orquestador con la tabla de
      evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 3.1-3.4 | `evaluation/tests/test_kappa_fleiss.py` | Unit | `pytest -q` de `evaluation/` | pendiente | pendiente | casos: cobertura variable, `P_e = 1`, cinco etiquetadores | pendiente |
| 3.5-3.8 | `evaluation/tests/test_mayoria.py` | Unit | `pytest -q` de `evaluation/` | pendiente | pendiente | casos: mayoria absoluta, `2-2-1`, `2-1-1-1`, cobertura parcial | pendiente |
| 5.1-5.4 | `evaluation/data/campana/analisis/test_analisis_referencia_mayoria_c230.py` | Unit | `pytest -q` de `evaluation/` | pendiente | pendiente | casos: sin cambio, acierto a error, error a acierto, Fleiss parcial | pendiente |
