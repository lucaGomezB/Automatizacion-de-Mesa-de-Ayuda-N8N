# Proposal: Muestreo probabilistico del universo de incidentes

## Adaptacion a la devolucion de tercera instancia (16/11/2026)

Este change se propuso el 15/11/2026, un dia antes de la devolucion de tercera instancia (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`), y se reformula sin haberse aplicado (0 tareas).

- **Premisa que cayo.** La version original anclaba la herramienta y la prosa en la lectura ponderada `0,7489` (bootstrap `[0,6822; 0,8099]`) y citaba como cifra primaria `0,6893`. Ambas son cifras de la validacion fuera de muestra que los autores **retiran** del ejemplar (K-01, opcion 2), junto con `analisis_propagacion_arbitraje_c221.json` y las secciones 3.25 y 3.32 del memo. El motivo del retiro lo fija `c-235` (`proposal.md` y `design.md`, D1 y D3); este change no lo reformula. Tambien caen como destino los hosts de prosa que `c-235` elimina (la subseccion de `07-resultados.tex` donde iba la lectura ponderada).
- **Que se conserva.** El nucleo: universo, marco y estratos; diseno estratificado con cuotas prefijadas; estimacion de Horvitz-Thompson y post-estratificacion; efecto de diseno de Kish; IC bootstrap sobre el universo completo. Tambien el numero reservado del memo (`3.40`).
- **Que cambia.** (1) La verificacion de la herramienta ya no depende de datos retirados: oraculo sintetico rotulado como tal y control de sanidad sobre el corpus de 200 (post-estratificar con su propia composicion reproduce la exactitud cruda `147/200` y da DEFF = 1). (2) La campana nueva queda sujeta a dos compuertas previas a cualquier computo: **procedencia** (K-01) y **etica y legal** (K-02), incluida la brecha que la version original no cubria: clasificar los casos nuevos con el hibrido envia su texto a la Gemini API. (3) El etiquetado sigue el protocolo de referencia por mayoria de `c-230`, sin arbitro unico. (4) La composicion por sector del corpus de 200, verificada (`85 / 67 / 31 / 16 / 1`), se usa solo como senal de planificacion para fijar cuotas minimas y declarar de antemano que clases no son estimables. (5) Se registra el trabajo con asistentes de IA en el inventario de `c-237` (A-03).
- **Alcance respecto de la entrega.** Este change **no modifica el ejemplar que se defiende**. Se ejecuta despues del cierre de la entrega (`c-235` → `c-236` → `c-237` → `c-238` → `c-239`), primero del grupo `c-229` → `c-230` → `c-228` → `c-232`. Hasta entonces la tesis solo lo menciona como trabajo futuro, en los terminos que ya fijan `c-235` (requisito de trabajo futuro con procedencia acreditable en `subsec:corpus-independiente`) y `c-234` (remedio empirico condicional en `subsec:aportes-generalizacion` y `subsec:estudios-replicacion`). Toda prosa de este change se condiciona a una version posterior a la defensa, con la campana ejecutada y las compuertas cerradas. Si los autores quieren hacer algo antes de la defensa, es una Open Question (`design.md`, OQ5), no el plan por defecto.

## Adaptacion al reencuadre del origen y la licitud del corpus (18/11/2026)

El reencuadre de `c-242-reencuadrar-el-origen-y-la-licitud-del-corpus` establecio que la "organizacion" del estudio es un **dispositivo narrativo**, no un adoptante real: no existe organizacion adoptante ni carta de autorizacion, y el corpus es una mezcla de dos regimenes. Este change se re-scopea en consecuencia, sin haberse aplicado (0 tareas):

- **Premisa que cae.** El estudio de muestreo corre sobre el **entorno operativo del propio equipo**, no sobre una organizacion adoptante. Se elimina toda dependencia de una organizacion real y de su autorizacion escrita. La poblacion y el marco son el universo real de incidentes del entorno del equipo; `N = 2.646 = 42 x 63` es una **proyeccion**, no un marco medido.
- **Marco, nuevo primer paso sustantivo.** Antes de cualquier seleccion, el change SHALL verificar o construir un marco poblacional real a partir de los registros de incidentes del equipo (sistema de tickets / base de datos) del periodo, y documentar su completitud, campos y exclusiones. Si no existe un marco completo, la campana **SE DETIENE**: el change declara que el muestreo probabilistico no es posible; no se sustituye por una muestra por conveniencia ni se inventa un universo.
- **Compuertas.** K-01 (procedencia: exportacion cruda, SHA-256 y verificacion del director) se mantiene. K-02 (etica y legal) se adapta: el consentimiento informado del grupo (acta T2, Ley 25.326 articulo 5 inciso 1) cubre el regimen (a); el regimen (b) no contiene datos personales; la decision explicita sobre la Gemini API y la pseudonimizacion se mantienen. Se retira la "autorizacion de la organizacion" de la compuerta.
- **Estimador.** Sin cambios: Horvitz-Thompson, post-estratificacion, DEFF de Kish, bootstrap y control de sanidad con oraculo sintetico.
- **Dependencias.** Despues de `c-242` y despues del cierre de la entrega (`c-239`, v1.6.0). El orden `c-229` -> `c-230` -> `c-228` -> `c-232` se mantiene; la referencia por mayoria de `c-230` sigue siendo la referencia de etiquetado.

## Estado: DETENIDO (18/11/2026)

El change queda **detenido** y se conserva como trabajo futuro: el protocolo, las compuertas (K-01/K-02) y el estimador (Horvitz-Thompson, post-estratificacion, DEFF de Kish, bootstrap y control de sanidad con oraculo sintetico) quedan documentados, sin campana ni medicion. Las tareas quedan sin marcar.

**Motivo.** No existe hoy un marco poblacional completo. Los activos versionados son subconjuntos de la misma muestra por conveniencia de 200 casos: el corpus congelado (`R001`-`R200`, sin fechas), sus sidecars de corrida (200 / 118 / 81, con fechas de octubre), y los dumps de la base del prototipo (alrededor de 150 filas en 18 dias, filas de prototipo/campana, no intake de una mesa de ayuda real). La tesis ya declara que no se dispone de un marco poblacional y que `N = 2.646` es una proyeccion, no un universo medido. Sin marco completo, el muestreo probabilistico no es posible y no se sustituye por conveniencia ni se inventa un universo.

**Reapertura.** Solo si el equipo opera el prototipo como su propia mesa de ayuda durante un periodo declarado y exporta la tabla `incidente` completa (`id`, `created_at`, `ingresado_en`, `persistido_en`, `sector_id`, `canal_origen_id`, `descripcion_pseudonimizada`), con control de completitud, SHA-256, acta K-01 y consentimiento K-02 (acta T2). Hasta entonces, el change no se aplica.

## Why

La amenaza de sesgo de seleccion (quinta amenaza de `subsec:amenazas-validez`, `04-marco-metodologico.tex`) declara que los 200 casos **no son una muestra probabilistica**: son los incidentes cronometrados en la campana manual, una muestra por conveniencia. La distribucion del universo por sector **no esta disponible** (memo, linea 376) y el margen de error del `6,66 %` presupone un muestreo aleatorio que no se realizo (`subsec:poblacion-muestra-corpus`). Las conclusiones (`subsec:aportes-generalizacion`, agregado por `c-234`) declaran que el remedio empirico es un diseno de muestreo probabilistico del universo, **condicional y no ejecutado**.

Este change convierte esa remision en un diseno reproducible y, si el entorno operativo del equipo aporta un marco completo, en una medicion: verifica o construye el marco, define el universo, fija un muestreo estratificado con cuotas prefijadas por canal y por sector, y entrega la maquinaria de estimacion ponderada con su efecto de diseno. La devolucion de tercera instancia no lo exige; el criterio del tribunal es que la evidencia nueva solo vale si su procedencia puede acreditarse. Por eso las dos compuertas son condicion de todo computo sobre datos nuevos, y sin un marco completo no hay muestreo probabilistico. El diseno **no eleva la exactitud del clasificador**: hace valida la estimacion.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A0. Marco poblacional** | Verificar o construir un marco real a partir de los registros de incidentes del entorno operativo del propio equipo (sistema de tickets / base de datos) del periodo: completitud, campos y exclusiones. Sin marco completo, la campana se detiene y se declara que el muestreo probabilistico no es posible. | **ALTA** |
| **A. Compuertas** | Compuerta de procedencia (K-01) y compuerta etica y legal (K-02), cerradas por el director (o un tercero) contra la evidencia primaria antes de extraer, enviar a terceros o computar. Incluye la decision explicita sobre el envio de los textos a la Gemini API. | **ALTA** |
| **B. Diseno muestral** | Protocolo nuevo `docs/campana-medicion/protocolo-muestreo-probabilistico.md`: universo, marco, estratos (sector, canal, complejidad), cuotas prefijadas con minimos por sector, clases no estimables declaradas de antemano, denominadores y reglas de decision, y remision al protocolo de referencia de `c-230`. | **ALTA** |
| **C. Herramienta de estimacion** | Script offline `evaluation/data/campana/analisis/estimador_muestreo_probabilistico_c229.py` (TDD estricto): pesos de Horvitz-Thompson y post-estratificacion, exactitud ponderada, DEFF de Kish, IC bootstrap sobre el universo completo. Verificacion con oraculo sintetico rotulado y control de sanidad sobre el corpus de 200. | MEDIA |
| **D. Campana** | Extraccion, seleccion y clasificacion de la muestra, solo con las compuertas cerradas. El etiquetado y la referencia los aporta `c-230`. | **ALTA** |
| **D2. Corpus probabilistico acreditado** | Se denomina **corpus probabilistico acreditado** a la muestra seleccionada segun el diseno, con las dos compuertas cerradas (acta del director) y la referencia por mayoria de `c-230`. Es el unico conjunto retenido de evaluacion que este change y sus consumidores (`c-228`, `c-232`) pueden usar. | **ALTA** |
| **E. Memo, tesis y trazabilidad** | Seccion reservada `3.40` del memo; prosa de una version posterior a la defensa, condicionada a la campana ejecutada y las compuertas cerradas; entrada en `dictamen-correcciones.md`; registro del uso de asistentes de IA en el inventario de `c-237`. | MEDIA |

**No objetivos.**

- No modifica el ejemplar que se defiende ni ninguna cifra canonica vigente (`61,6 s`, `17,76 s`, `W = 363`, `73,5 %`, `0,6508`, `110/138`, `6,66 %`, `N = 2.646`).
- No usa como ancla, insumo ni comparador ninguna cifra ni artefacto que `c-235` retira.
- No afirma que el diseno suba la exactitud del clasificador.
- No toca `App/`, `n8n/`, el clasificador, el corpus de 200 ni sus predicciones.
- No ejecuta llamadas a Gemini ni trabajo de campo mientras alguna compuerta este abierta.
- No sustituye un muestreo probabilistico por una muestra por conveniencia ni inventa un universo si falta un marco completo.

## Capabilities

### New Capabilities

- `evaluation-probabilistic-sampling`: diseno de muestreo probabilistico estratificado del universo de incidentes (marco, estratos, cuotas, reglas), definicion del **corpus probabilistico acreditado** (PS-009), compuertas de procedencia y etica/legal previas a todo computo, y estimacion ponderada referida al universo (Horvitz-Thompson / post-estratificacion, DEFF, IC sobre el universo completo).

### Modified Capabilities

- `tesis-document`: se AGREGA un requisito condicionado (version posterior a la defensa, campana ejecutada y compuertas cerradas) para incorporar el diseno y su resultado; se MODIFICAN "Validez externa declarada en las conclusiones con su remedio empirico" (agrega la rama "ejecutado") y "Seleccion de los casos por conveniencia declarada" (permite describir como estratificada la muestra nueva, nunca la de 200).
- `tesis-numeros-canonicos`: se AGREGA el registro de la seccion reservada `3.40` con el plan, el control de sanidad y, si existe, la estimacion.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/campana-medicion/protocolo-muestreo-probabilistico.md` | Nuevo | Diseno, cuotas, compuertas y remision al protocolo de `c-230` |
| `docs/campana-medicion/compuertas-c229.md` (nombre a confirmar) | Nuevo | Lista de verificacion de las compuertas y acta del director, sin datos personales |
| `evaluation/data/campana/analisis/` | Nuevo | Script TDD, prueba, fixture sintetico, salidas y manifiesto SHA-256 |
| `evaluation/data/campana/probabilistica/` (nombre a confirmar) | Nuevo, condicionado | Muestra pseudonimizada consentida, hashes de planillas crudas, predicciones |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion reservada `3.40` |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |
| `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (de `c-237`) | Aditivo | Registro del trabajo con asistentes de IA (A-03) |
| `sections/04`, `07`, `08`, `09`, `10`, `11` | Condicionado | Solo en una version posterior a la defensa, con la campana ejecutada y las compuertas cerradas |

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Repetir el problema de K-01 (evidencia no acreditable) | Media | Compuerta de procedencia previa a todo computo, verificada por el director contra la evidencia primaria; ninguna prueba estadistica de forma la sustituye |
| Usar datos personales del regimen (a) o enviarlos a un tercero sin base legal (K-02) | Media | Compuerta etica y legal: consentimiento informado del grupo (Ley 25.326 articulo 5 inciso 1) para el regimen (a); decision explicita sobre la Gemini API antes de clasificar; solo material pseudonimizado en el repositorio publico |
| Que el diseno se lea como medicion realizada | Alta | Rotulo `condicional` hasta que exista la muestra; prosa solo en version posterior a la defensa |
| Clases raras no estimables (`Bases de Datos`) | Alta | Cuotas minimas y clases no estimables declaradas antes de reunir la muestra |
| El marco del entorno operativo del equipo es incompleto | Alta | El change detiene la campana y declara que el muestreo probabilistico no es posible; no se sustituye por muestreo de conveniencia ni se inventa el universo |
| Desfase de anclas `archivo:linea` por `c-235` | Alta | Se citan etiquetas LaTeX; las lineas se repuntan por contenido al aplicar |

## Rollback Plan

`git revert` del commit del change: protocolo, script y salidas son aditivos; la seccion `3.40` se retira sin tocar las demas; la prosa (si se llego a escribir en una version posterior) se revierte por archivo. Si se versionaron datos de la muestra y el consentimiento del grupo se revoca, se retiran del arbol en un commit separado y se declara en el registro de correcciones.

## Dependencies

- Despues de `c-242` (reencuadre del origen y la licitud) y despues del cierre de la entrega (`c-239`, v1.6.0). Primero del grupo `c-229` → `c-230` → `c-228` → `c-232`.
- Bloqueada por el entorno operativo del propio equipo: disponibilidad y completitud de los registros de incidentes del periodo (sistema de tickets / base de datos). Sin marco completo, la campana no se ejecuta.
- **Dependencia cruzada con `c-230`:** el etiquetado y la referencia de la muestra los define y construye `c-230` (funciones puras y protocolo); la estimacion sobre datos reales de este change espera esa referencia (ver `design.md`, D8).
- `c-237`: el inventario de uso de asistentes de IA debe existir para la tarea de A-03.
- Consumidores aguas abajo: `c-228` y `c-232` (los adapta otro agente).

## Success Criteria

- [ ] El marco poblacional se verifica o construye con su completitud, campos y exclusiones documentados; si no existe, el change declara que el muestreo probabilistico no es posible y no ejecuta la campana.
- [ ] El protocolo define universo, marco, estratos, cuotas con minimos por sector, clases no estimables, denominadores, reglas de decision y la remision al protocolo de referencia de `c-230`; ningun valor se presenta como medido.
- [ ] Las dos compuertas tienen acta del director (o tercero) con fecha, cerrada antes de extraer, enviar o computar; sin acta, la campana no se ejecuta.
- [ ] El script es determinista, de solo lectura, sin red; reproduce el oraculo sintetico y el control de sanidad (`147/200`, `0,7350`, DEFF = 1) y no lee ningun artefacto retirado.
- [ ] Ninguna cifra ni artefacto retirado por `c-235` aparece como ancla, insumo o comparador.
- [ ] El ejemplar que se defiende no cambia por este change.
- [ ] `openspec validate c-229-muestreo-probabilistico-del-universo-de-incidentes --strict` pasa.
