# Tasks: Muestreo probabilistico del universo de incidentes

Al final de cada tarea, entre parentesis, el requisito que cumple: `PS` (`evaluation-probabilistic-sampling`), `TD` (`tesis-document`) y `NC` (`tesis-numeros-canonicos`). Nombres cortos: PS-001 «Universo y marco»; PS-002 «Cuotas y minimos»; PS-003 «Compuerta de procedencia»; PS-004 «Compuerta etica y legal»; PS-005 «Referencia por mayoria»; PS-006 «Estimacion al universo»; PS-007 «Efecto de diseno»; PS-008 «Herramienta verificada»; PS-009 «Corpus acreditado»; TD «Version posterior», TD «Validez externa», TD «Seleccion por conveniencia»; NC «Registro 3.40».

Reglas del change (adaptacion a la devolucion de tercera instancia y re-scope por `c-242`, ver `proposal.md` y `design.md`):

- Se aplica **despues de `c-242`** (reencuadre del origen y la licitud) y **despues del cierre de la entrega** (`c-239`, v1.6.0). Ninguna tarea modifica el ejemplar que se defiende.
- El estudio corre sobre el **entorno operativo del propio equipo**: no hay organizacion adoptante ni autorizacion de la organizacion. La poblacion y el marco son el universo real de incidentes del entorno del equipo; `N = 2.646 = 42 x 63` es una **proyeccion**.
- **El marco va primero.** La primera tarea sustantiva verifica o construye el marco real (grupo 4). **Sin marco completo, la campana SE DETIENE** y el change declara que el muestreo probabilistico no es posible; no se sustituye por conveniencia ni se inventa el universo.
- Gobernanza **ALTA** en compuertas, protocolo y campana. Las tareas **[COMPUERTA]** no se ejecutan sin el acta o la documentacion indicada, registrada con fecha en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- Ninguna cifra ni artefacto retirado por `c-235` se usa como ancla, insumo o comparador. Ningun nombre real de personas entra al repositorio.
- Las anclas de la tesis se citan por etiqueta LaTeX; las lineas se repuntan por contenido al aplicar.
- Cero llamadas a Gemini mientras la compuerta etica y legal este abierta.

## Estado: DETENIDO (18/11/2026)

El change queda **detenido** y se conserva como trabajo futuro. No existe un marco poblacional completo: los datos versionados son subconjuntos de la muestra por conveniencia de 200 casos y los dumps del prototipo no son un intake real. Las tareas quedan **sin marcar**; el protocolo, las compuertas y el estimador se conservan documentados. Reapertura solo con un periodo real de operacion y una exportacion completa de la tabla `incidente` (K-01 + K-02).

## 0. Preparacion y verificacion de estado

- [ ] 0.1 Confirmar con `openspec list --json` y el registro de correcciones que `c-242` y `c-235` a `c-239` estan archivados y que la entrega esta cerrada; si no, detenerse.
- [ ] 0.2 Leer `proposal.md`, `design.md` y los specs delta; cargar los `SKILL.md` de `python-testing`, `pytest-coverage` y `python-design-patterns` y registrar la resolucion.
- [ ] 0.3 Linea de base: `git status`, `git rev-parse HEAD`, `sha256sum data/corpus_evaluacion_pseudonimizado.json evaluation/data/campana/predicciones_in_sample.json`; registrar `N ≈ 2.646` (proyeccion, memo 3.4) y la composicion `85/67/31/16/1`.
- [ ] 0.4 **Red de seguridad:** `cd evaluation && pytest -q`; registrar el resultado y detenerse ante fallos preexistentes.
- [ ] 0.5 Verificar en el memo que la seccion `3.40` sigue libre y reservada a este change; si no, detenerse y consultar.
- [ ] 0.6 **[CHECKPOINT DE LOS AUTORES]** Registrar las respuestas a OQ1 (periodo, complejidad), OQ2 (tamanio y cuota minima), OQ3 (que registros de incidentes del entorno del propio equipo existen, quien los posee, que periodo cubren y si permiten un marco completo), OQ5 (nada antes de la defensa) y OQ6 (quien verifica y custodia). Sin marco viable (OQ3), los grupos 4 a 6 quedan bloqueados.

## 1. Compuertas preparadas (ALTA)

- [ ] 1.1 Redactar la lista de verificacion de la compuerta de procedencia (planillas crudas con marcas de la herramienta, constancias de etiquetadores y de exportacion del marco, hashes, independencia, textos reales, pseudonimizacion acotada) y el modelo de acta del director, sin datos personales. (PS-003 «Compuerta de procedencia»)
- [ ] 1.2 Redactar la lista de verificacion de la compuerta etica y legal (base de licitud por regimen: consentimiento informado del grupo para el regimen (a), sin datos personales en el regimen (b); consentimiento escrito previo de etiquetadores; decision sobre el envio a la Gemini API; alcance de publicacion). (PS-004 «Compuerta etica y legal»)
- [ ] 1.3 Declarar en el protocolo la herramienta de etiquetado y su formato de exportacion con marcas temporales propias, antes de etiquetar. (PS-003 «Compuerta de procedencia»)

## 2. Protocolo del diseno muestral (ALTA)

- [ ] 2.1 Crear `docs/campana-medicion/protocolo-muestreo-probabilistico.md` con universo, `N` a confirmar contra el marco, marco (registros del entorno del propio equipo), estratos con definicion operacional, regla de colapso y la nota sobre el canal telefonico. (PS-001 «Universo y marco»)
- [ ] 2.2 Fijar en el protocolo tamano objetivo, cuota minima por sector, sobremuestreo, regla de censo, clases candidatas a no estimables (con la senal de planificacion `1/200` para `Bases de Datos` rotulada como tal), denominadores y reglas de tres vias. (PS-002 «Cuotas y minimos»)
- [ ] 2.3 Remitir en el protocolo al protocolo de referencia por mayoria de `c-230`; fijar alias desde `E6`. (PS-005 «Referencia por mayoria»)
- [ ] 2.4 Verificar con `rg` que el protocolo no usa la composicion del corpus de 200 como peso del universo ni presenta valores como medidos. (PS-001 «Universo y marco»)
- [ ] 2.5 **[CHECKPOINT DE LOS AUTORES]** Aprobacion del protocolo con fecha, antes de cualquier extraccion. (PS-002 «Cuotas y minimos»)

## 3. Herramienta de estimacion (TDD estricto)

- [ ] 3.1 **RED:** escribir `evaluation/data/campana/analisis/test_estimador_muestreo_probabilistico_c229.py` y el fixture `fixture_sintetico_c229.json` (cabecera `sintetico: true`) con valores esperados calculados a mano para `pesos_horvitz_thompson`, `post_estratificar`, `exactitud_ponderada`, `efecto_diseno` e `ic_bootstrap_universo`; confirmar que fallan por ausencia del modulo. (PS-008 «Herramienta verificada»)
- [ ] 3.2 **GREEN:** implementar el minimo en `estimador_muestreo_probabilistico_c229.py`, reutilizando `evaluation/metrics.py` y `evaluation/stats.py` sin modificarlos. (PS-006 «Estimacion al universo», PS-007 «Efecto de diseno»)
- [ ] 3.3 **TRIANGULATE:** agregar pesos iguales y desiguales, cuotas proporcionales y no proporcionales, un estrato censado (`pi = 1`) y DEFF mayor que 1. (PS-006 «Estimacion al universo», PS-007 «Efecto de diseno»)
- [ ] 3.4 **RED/GREEN:** prueba del control de sanidad: post-estratificar el corpus de 200 con su propia composicion devuelve `147/200 = 0,7350` y DEFF `1`, leyendo `data/corpus_evaluacion_pseudonimizado.json` y `evaluation/data/campana/predicciones_in_sample.json`. (PS-008 «Herramienta verificada»)
- [ ] 3.5 **REFACTOR:** nombres y constantes; pruebas tras cada paso.
- [ ] 3.6 `main()`: correr oraculo y control de sanidad antes de escribir (abortar sin escribir si fallan); emitir `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF) con el DEFF del diseno como no computable y `condicional`. Verificar con `rg` que el script no referencia ningun artefacto retirado por `c-235`. (PS-007 «Efecto de diseno», PS-008 «Herramienta verificada»)
- [ ] 3.7 Dos corridas identicas byte a byte; sin red; registrar SHA-256. (PS-008 «Herramienta verificada»)

## 4. Marco poblacional, extraccion y seleccion (bloqueado por compuertas)

- [ ] 4.1 **[MARCO]** Verificar o construir el marco poblacional real desde los registros de incidentes del entorno operativo del propio equipo (sistema de tickets / base de datos) del periodo; documentar completitud, campos disponibles y exclusiones; registrar el SHA-256 de la exportacion cruda. (PS-001 «Universo y marco», PS-003 «Compuerta de procedencia»)
- [ ] 4.2 **[PARADA DURA]** Si no existe un marco completo (identificador y contenido clasificable para todo el periodo y los campos necesarios), detenerse: declarar en `dictamen-correcciones.md` que el muestreo probabilistico no es posible, sin sustituirlo por una muestra por conveniencia ni inventar el universo. (PS-001 «Universo y marco»)
- [ ] 4.3 **[COMPUERTA K-02]** Registrar el acta T2 (consentimiento informado del grupo, Ley 25.326 articulo 5 inciso 1), la base de licitud por regimen y el alcance de publicacion, con fecha; originales en custodia del director. Sin esto, detenerse. (PS-004 «Compuerta etica y legal»)
- [ ] 4.4 Confirmar `N` y la distribucion por estrato contra el marco; aplicar la regla de colapso y la de censo tal como se fijaron. (PS-001 «Universo y marco», PS-002 «Cuotas y minimos»)
- [ ] 4.5 Seleccionar la muestra con semilla registrada y probabilidades de inclusion conocidas; versionar la lista de identificadores pseudonimizados y la semilla; entregar la muestra a `c-230` para el etiquetado y la referencia (ver `design.md`, D8). (PS-002 «Cuotas y minimos»)

## 5. Clasificacion y estimacion (bloqueado por compuertas y por `c-230`)

- [ ] 5.1 **[COMPUERTA K-01]** Registrar el acta del director (o tercero) que verifica las planillas crudas, las constancias, los hashes, la independencia y los textos reales contra la evidencia primaria. Sin acta, detenerse. (PS-003 «Compuerta de procedencia»)
- [ ] 5.2 **[COMPUERTA K-02]** Registrar la decision escrita sobre el envio de los textos a la Gemini API (pseudonimizacion, instrumento de transferencia, base de licitud). Si es negativa, declarar la estimacion del hibrido como no realizada y saltar a 5.4. (PS-004 «Compuerta etica y legal»)
- [ ] 5.3 Clasificar la muestra con el clasificador congelado; registrar version, cantidad de textos enviados al proveedor y SHA-256 de las predicciones. (PS-006 «Estimacion al universo»)
- [ ] 5.4 Publicar el manifiesto del corpus probabilistico acreditado (estrato, probabilidad de inclusion, referencia y `origen` por caso; fecha del acta) o custodiarlo con su SHA-256 publicado si el consentimiento del grupo no permite publicarlo. Sin las cuatro condiciones, no usar ese nombre ni continuar. (PS-009 «Corpus acreditado»)
- [ ] 5.5 Correr el estimador sobre el corpus probabilistico acreditado con la referencia de `c-230`: exactitud ponderada y cruda, DEFF, IC estratificado sin exclusiones, cuotas alcanzadas y clases no estimables. (PS-006 «Estimacion al universo», PS-007 «Efecto de diseno»)

## 6. Memo, tesis y trazabilidad

- [ ] 6.1 Agregar la seccion `3.40` del memo con el plan, el control de sanidad rotulado, el estado de las compuertas y, si existe, la estimacion; verificar con `git diff` que es aditiva y con `rg` que no cita cifras `retirado`. (NC «Registro 3.40»)
- [ ] 6.2 Solo si 4.2 se supero (marco completo) y 5.1 a 5.4 se cumplieron, y en una version posterior a la defensa: `subsec:poblacion-muestra-corpus` (muestra nueva distinta del corpus de 200), `subsec:muestra-probabilistica` nueva en `07-resultados.tex`, quinta amenaza de `subsec:amenazas-validez`. (TD «Version posterior», TD «Seleccion por conveniencia»)
- [ ] 6.3 En la misma version: `subsec:aportes-generalizacion` y `subsec:estudios-replicacion` pasan de "condicional y no ejecutado" a ejecutado con alcance acotado al entorno operativo del propio equipo; `subsec:corpus-independiente` agrega la remision sin perder los elementos de su requisito. (TD «Validez externa», TD «Version posterior»)
- [ ] 6.4 En la misma version: `11-aspectos-legales.tex` declara la base de licitud por regimen (consentimiento del grupo para el regimen (a); sin datos personales en el (b)), el consentimiento de los etiquetadores y las transferencias con su cantidad. (TD «Version posterior»)
- [ ] 6.5 Verificar en esa version: cifras canonicas del corpus de 200 intactas; el `rg` de cifras y alias retirados de `c-235` sigue sin coincidencias fuera de la nota de versiones; sin `c-NNN` en el cuerpo; compilacion sin referencias indefinidas. (TD «Version posterior»)
- [ ] 6.6 Agregar en `dictamen-correcciones.md` la entrada del change con protocolo, artefactos, estado del marco, actas (fecha, sin datos personales), seccion `3.40` y anclas de prosa. (NC «Registro 3.40»)
- [ ] 6.7 **A-03:** registrar en `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (de `c-237`) que partes del protocolo, del script, de las pruebas y de la prosa produjo un asistente de IA, con que herramienta y como se verifico cada cifra.

## 7. Verificacion de cierre

- [ ] 7.1 `cd evaluation && pytest -q` sin regresiones; tercera corrida del script con SHA-256 iguales a 3.7.
- [ ] 7.2 `git diff --stat`: sin cambios en `App/`, `n8n/`, el clasificador, el corpus de 200, sus predicciones ni artefactos congelados.
- [ ] 7.3 Buscar con `rg` las cifras, alias y artefactos retirados que lista la seccion de adaptacion de `proposal.md` sobre los archivos nuevos del change (protocolo, script, salidas, seccion `3.40`): sin coincidencias.
- [ ] 7.4 `openspec validate c-229-muestreo-probabilistico-del-universo-de-incidentes --strict`.
- [ ] 7.5 Dejar a cargo del orquestador `CHANGES.md` y `engram sync`; no pushear ni etiquetar.
- [ ] 7.6 Guardar en Engram el resumen y reportar con la tabla de evidencia TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 3.1-3.5 | `evaluation/data/campana/analisis/test_estimador_muestreo_probabilistico_c229.py` | Unit | `pytest -q` de `evaluation/` | pendiente | pendiente | pesos iguales/desiguales, cuotas proporcionales/no, estrato censado, DEFF > 1, control de sanidad | pendiente |
