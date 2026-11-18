# Tasks: Referencia por mayoria con etiquetadores independientes

Al final de cada tarea, entre parentesis, el requisito que cumple: `MR` (`evaluation-majority-reference`), `EF` (`evaluation-framework`), `TD` (`tesis-document`) y `NC` (`tesis-numeros-canonicos`). Nombres cortos: MR-001 «Funciones puras»; MR-002 «Protocolo constatado»; MR-003 «Compuerta de procedencia»; MR-004 «Compuerta etica y legal»; MR-005 «Registro»; MR-006 «Referencia de la muestra»; EF «Kappa de Fleiss», EF «Kappa de Cohen»; TD «Version posterior»; NC «Registro 3.39».

Reglas del change (adaptacion a la devolucion de tercera instancia, ver `proposal.md`):

- Se aplica **despues del cierre de la entrega** (`c-239`) y depende de `c-229` (secuencia por grupos en `design.md`, D7). Ninguna tarea modifica el ejemplar que se defiende.
- Ninguna cifra ni artefacto retirado por `c-235` se usa como ancla, insumo o comparador. Sin nombres reales de personas ni de la organizacion.
- Las tareas **[COMPUERTA]** no se ejecutan sin el acta o la documentacion indicada, registrada con fecha en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- TDD estricto en los grupos 1 y 2. Este change no envia textos a terceros.

## Estado: DETENIDO (18/11/2026)

El change queda **detenido** y se conserva como trabajo futuro lo autocontenido: las funciones puras `evaluation/mayoria.py` y `kappa_fleiss` y el protocolo de referencia por mayoria. Las tareas quedan **sin marcar**; nada se aplico. Faltan los dos insumos de la familia post-entrega (marco poblacional completo y `clasificacion_log` real acumulado) y las condiciones de consentimiento de etiquetadores nuevos (desde `E6`) y K-02. Reapertura solo con un periodo real de operacion, la exportacion completa de la tabla `incidente` (marco para `c-229` y log real acumulado), el consentimiento escrito de los etiquetadores independientes y la decision K-02.

## 0. Preparacion y linea de base

- [ ] 0.1 Confirmar que la entrega esta cerrada (`c-235` a `c-239` archivados) y que `c-229` completo sus grupos 0 a 3; si no, detenerse.
- [ ] 0.2 Leer `proposal.md`, `design.md` y los specs delta; cargar los `SKILL.md` de `python-testing` y `python-design-patterns` y registrar la resolucion.
- [ ] 0.3 Linea base: `git status`, `git rev-parse HEAD`, `sha256sum evaluation/data/campana/doble_etiquetado.csv evaluation/data/campana/registro_sujetos.csv evaluation/kappa.py`; registrar kappa `E1`/`E2` `0,5569`, 62 discordantes y 29 entre `Sistemas` y `Soporte Tecnico Software`.
- [ ] 0.4 **Red de seguridad:** `cd evaluation && pytest -q`; registrar el resultado y detenerse ante fallos preexistentes.
- [ ] 0.5 Verificar en el memo que la seccion `3.39` sigue libre y reservada a este change.
- [ ] 0.6 **[CHECKPOINT DE LOS AUTORES]** Registrar las respuestas a OQ1 (cinco o tres etiquetadores), OQ2 (`sin_mayoria`), OQ3 (quienes y que vinculo), OQ4 (personas ya registradas), OQ5 (herramienta) y OQ6 (nada antes de la defensa).

## 1. Kappa de Fleiss (TDD estricto)

- [ ] 1.1 **RED** `evaluation/tests/test_kappa_fleiss.py`: oraculo sintetico con `P_bar`, `P_e` y kappa calculados a mano; ejemplo publicado con su fuente citada y el valor tomado de la fuente; matriz por pares; confirmar que fallan por ausencia. (EF «Kappa de Fleiss»)
- [ ] 1.2 **GREEN** `kappa_fleiss` y `matriz_acuerdo_por_pares` en `evaluation/kappa.py`, reutilizando `kappa_cohen` y las constantes de bootstrap de `evaluation/metrics.py`. (EF «Kappa de Fleiss»)
- [ ] 1.3 **TRIANGULATE** cobertura variable por caso, `P_e = 1` (no estimable), tres y cinco etiquetadores. (EF «Kappa de Fleiss»)
- [ ] 1.4 Actualizar el mensaje de `kappa_doble_etiquetado` para remitir a Fleiss sin cambiar su contrato de dos etiquetadores; correr sus pruebas existentes. (EF «Kappa de Cohen»)
- [ ] 1.5 **REFACTOR** y suite de `evaluation/` en verde.

## 2. Funciones de mayoria (TDD estricto)

- [ ] 2.1 **RED** `evaluation/tests/test_mayoria.py`: mayoria absoluta, `2-2-1`, `2-1-1-1`, conjunto laxo sin repetir el principal, cobertura variable; confirmar que fallan por ausencia del modulo. (MR-001 «Funciones puras»)
- [ ] 2.2 **GREEN** `evaluation/mayoria.py` con el minimo para pasar, sin E/S ni red y sin tocar `doble_etiquetado.py` ni `arbitraje.py`. (MR-001 «Funciones puras»)
- [ ] 2.3 **TRIANGULATE** umbrales `2` y `3`, casos con un solo etiquetador, referencia de varios casos con `origen` y conteos. (MR-001 «Funciones puras»)
- [ ] 2.4 **REFACTOR** y suite de `evaluation/` en verde.

## 3. Protocolo y constancia (ALTA)

- [ ] 3.1 Crear `docs/campana-medicion/protocolo-referencia-mayoria.md`: numero de etiquetadores, umbral, `sin_mayoria` sin arbitro unico (rango acotante por defecto), conjunto laxo, cegado, codebook congelado, herramienta y formato de exportacion con marcas propias, vinculo de cada etiquetador con los autores. (MR-002 «Protocolo constatado»)
- [ ] 3.2 Crear la plantilla de consentimiento escrito previo para los etiquetadores nuevos, sin nombres, con originales en custodia del director. (MR-004 «Compuerta etica y legal»)
- [ ] 3.3 **[CHECKPOINT DE LOS AUTORES]** Aprobacion del protocolo con fecha. (MR-002 «Protocolo constatado»)
- [ ] 3.4 **[COMPUERTA]** Constancia firmada y fechada del director sobre el protocolo (o su SHA-256), antes de entregar cualquier paquete; versionar el hash del documento constatado. La fecha de commit no basta por si sola. (MR-002 «Protocolo constatado»)

## 4. Sujetos y etiquetado ciego (ALTA, despues de `c-229` grupo 4)

- [ ] 4.1 **[COMPUERTA K-02]** Confirmar que existe la autorizacion institucional y la base de licitud de `c-229` y que cada etiquetador firmo su consentimiento previo; registrar fechas por alias. (MR-004 «Compuerta etica y legal»)
- [ ] 4.2 Agregar a `registro_sujetos.csv` los alias desde `E6` con codigos desde `P12`; verificar con `validar_registro_sujetos`; sin datos personales. (MR-005 «Registro»)
- [ ] 4.3 Preparar el paquete ciego de la muestra de `c-229` (`id_caso`, texto pseudonimizado autorizado, plantilla vacia, codebook congelado) y entregarlo; registrar que ningun etiquetador vio etiquetas ajenas, referencia ni predicciones. (MR-006 «Referencia de la muestra»)
- [ ] 4.4 Recibir las planillas crudas exportadas por la herramienta, sin editarlas; versionar su SHA-256 y custodiar los originales segun la autorizacion. (MR-003 «Compuerta de procedencia»)

## 5. Referencia y acuerdo (bloqueado por compuerta)

- [ ] 5.1 **[COMPUERTA K-01]** Acta del director (o tercero) que verifica planillas crudas, marcas de la herramienta, constancias, hashes, independencia y textos reales contra la evidencia primaria. Puede ser la misma acta de `c-229` si cubre el etiquetado. Sin acta, detenerse. (MR-003 «Compuerta de procedencia»)
- [ ] 5.2 Construir la referencia con `evaluation/mayoria.py` y la regla constatada; versionar referencia y sidecar (`origen`, conteo de `sin_mayoria`) con SHA-256. (MR-006 «Referencia de la muestra»)
- [ ] 5.3 Calcular el kappa de Fleiss con su IC y la matriz por pares sobre la muestra; versionar el resultado. (MR-006 «Referencia de la muestra», EF «Kappa de Fleiss»)
- [ ] 5.4 Entregar la referencia a `c-229` (grupo 5), que con ella publica el manifiesto del corpus probabilistico acreditado y corre la estimacion. (MR-006 «Referencia de la muestra»)

## 6. Memo, tesis y trazabilidad

- [ ] 6.1 Agregar la seccion `3.39` del memo (protocolo y fecha de la constancia, verificacion contra oraculos, estado de compuertas y, si existe, cobertura, `sin_mayoria`, Fleiss y matriz por pares); conservar por remision el kappa `0,5569`; verificar con `git diff` que es aditiva y con `rg` que no cita cifras `retirado`. (NC «Registro 3.39»)
- [ ] 6.2 Solo si 5.1 a 5.3 se cumplieron y la muestra se incorpora por `c-229`, en una version posterior a la defensa: metodo, resultados, limitacion de fiabilidad (conserva `0,5569`) y `subsec:consentimiento-derechos` por alias. (TD «Version posterior»)
- [ ] 6.3 Verificar en esa version: el `rg` de cifras y alias retirados de `c-235` sigue sin coincidencias fuera de la nota de versiones; sin nombres reales; sin `c-NNN` en el cuerpo; compilacion sin referencias indefinidas. (TD «Version posterior»)
- [ ] 6.4 Agregar en `dictamen-correcciones.md` la entrada del change con modulos, pruebas, protocolo, constancia y actas (fechas, sin datos personales), seccion `3.39` y anclas de prosa. (NC «Registro 3.39»)
- [ ] 6.5 **A-03:** registrar en `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (de `c-237`) que partes de los modulos, pruebas, protocolo y prosa produjo un asistente de IA, con que herramienta y como se verifico cada resultado.

## 7. Verificacion de cierre

- [ ] 7.1 `cd evaluation && pytest -q` sin regresiones; pruebas de `doble_etiquetado.py` y `arbitraje.py` sin cambios de contrato.
- [ ] 7.2 `git diff --stat`: sin cambios en `App/`, `n8n/`, el clasificador, el corpus de 200, `doble_etiquetado.csv` ni artefactos congelados.
- [ ] 7.3 Buscar con `rg` las cifras, alias y artefactos retirados que lista la seccion de adaptacion de `proposal.md` sobre los archivos nuevos del change: sin coincidencias.
- [ ] 7.4 `openspec validate c-230-referencia-por-mayoria-con-etiquetadores-independientes --strict`.
- [ ] 7.5 Dejar a cargo del orquestador `CHANGES.md` y `engram sync`; no pushear ni etiquetar.
- [ ] 7.6 Guardar en Engram el resumen y reportar con la tabla de evidencia TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1-1.5 | `evaluation/tests/test_kappa_fleiss.py` | Unit | `pytest -q` de `evaluation/` | pendiente | pendiente | cobertura variable, `P_e = 1`, tres y cinco etiquetadores, ejemplo publicado | pendiente |
| 2.1-2.4 | `evaluation/tests/test_mayoria.py` | Unit | `pytest -q` de `evaluation/` | pendiente | pendiente | mayoria, `2-2-1`, `2-1-1-1`, laxo, cobertura parcial, umbrales 2 y 3 | pendiente |
