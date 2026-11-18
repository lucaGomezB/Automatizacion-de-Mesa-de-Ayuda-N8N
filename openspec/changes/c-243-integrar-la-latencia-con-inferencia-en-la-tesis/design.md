## Context

Ver `proposal.md` — Why. Hechos del repositorio que condicionan el enfoque (verificados 2026-11-18):

- **La evidencia existe y esta versionada.** `evaluation/evidence/load_test_inferencia_2026-11-17.json` (SHA-256 `08da89c6e3b21747afdf970112a3c18303b5567f6df0528027ea14f42e020c28`) y su `.md` (`3803e7c9…`), producidos por `scripts/load_test/load_test_inference.py` en el commit `bbc5865` (release `v1.6.0`). Prerregistro: `scripts/load_test/PRERREGISTRO_latencia_con_inferencia.md` (`8d8d5261…`). El arnes no modifica `load_test.py` ni la guarda de costo cero.
- **El ejemplar niega la medicion en cuatro loci.** `07-resultados.tex:336` (nota de `tab:carga-multicanal`), `07-resultados.tex:343` («la latencia con inferencia no se midio»), `08-discusion.tex:10` (medicion «del camino deterministico, sin inferencia paga») y `09-conclusiones.tex:6` («sin cuello de botella en el punto de convergencia del backend»).
- **`08-discusion.tex` y `09-conclusiones.tex` los toca `c-242`** (tareas 3.5 y siguientes). Este change se aplica despues y re-localiza por texto.
- **La tabla de capacidad de c-218 es la evidencia primaria** (`tab:carga-multicanal`, 120 solicitudes por nivel, 3 repeticiones, camino deterministico de costo cero).
- **La corrida paga es de menor potencia**: 20 solicitudes por nivel, 1 repeticion, n = 10 por subconjunto; la canonica tiene 120 por nivel. No son comparables en potencia.
- **El memo no registra la sonda.** La ultima seccion vigente es la `3.46`; la `3.29` es la lectura canonica de capacidad. La numeracion tiene huecos (`3.39` a `3.42` no existen); no se reutilizan.
- **El Anexo B fija el hash del commit de entrega** (`12-anexos.tex`, `sec:anexo-repositorio`), y la version esta en `00-portada.tex:31` y `Bibliography_base.bib:919`.

## Goals / Non-Goals

**Goals:**

- Informar la sonda con inferencia incluida con su tabla, sus dos veredictos y sus limites, sin convertirla en un resultado de capacidad.
- Corregir las cuatro afirmaciones que hoy son verdaderas solo para el camino deterministico.
- Registrar los valores como `condicional` en el memo, con procedencia por valor, sin tocar la `3.29`.
- Dejar la release preparada (version, hash, derivados) sin ejecutarla.

**Non-Goals:**

- Reejecutar la sonda, cambiar el arnes, el fixture o la guarda de costo cero.
- Reabrir el veredicto de capacidad de c-218 o reemplazar `tab:carga-multicanal`.
- Instrumentar latencia por etapa del clasificador (la sonda no la desagrega).
- Commit, tag o push; recompilar en esta fase.

## Decisions

### D1 — Subseccion nueva en resultados y tabla en el cuerpo, sin anexo

**Elegido:** una subseccion `subsec:latencia-con-inferencia` en `07-resultados.tex`, inmediatamente despues de `subsec:carga-concurrente` y antes del `\newpage`, con la tabla `tab:carga-inferencia` en el cuerpo.

**Por que:** son 8 filas por 10 columnas, del mismo orden que `tab:carga-multicanal` (8 por 7); entra con `\footnotesize` y `\setlength{\tabcolsep}{3pt}`. La evidencia primaria y la sonda quedan contiguas y comparables de un vistazo. Un anexo separaria la sonda de la tabla que la contextualiza y agregaria paginas a un documento ya cerrado.

**Alternativas rechazadas:** (i) anexo con la tabla completa — solo se justificaria si la tabla no entrara a lo ancho, y entra; (ii) integrar la sonda como filas adicionales de `tab:carga-multicanal` — mezclaria dos disenos (120 contra 20 solicitudes por nivel) y romperia la lectura de capacidad.

### D2 — Esquema de la tabla

Columnas: Capa; Concurrencia; p50 (ms); p95 (ms); p99 (ms); Throughput (sol./s); Tasa de error; Escalados; \(r = \mathrm{p95}_{esc}/\mathrm{p95}_{det}\); Veredicto del nivel. Una fila por capa y nivel (8 filas), con `\midrule` entre las dos capas. Redondeo a un decimal para latencias y cociente, dos decimales para throughput y cuatro para la tasa de error (0,0000).

Valores del artefacto:

| Capa | Conc. | p50 | p95 | p99 | sol./s | Error | Esc. | r | Veredicto del nivel |
|---|---|---|---|---|---|---|---|---|---|
| Backend | 1 | 815,9 | 1913,1 | 1937,4 | 1,12 | 0,0000 | 10/20 | 11,3 | no cumple (inferencia) |
| Backend | 5 | 946,3 | 1982,7 | 1999,4 | 4,41 | 0,0000 | 10/20 | 5,0 | no cumple (inferencia) |
| Backend | 10 | 1182,9 | 2759,6 | 2763,9 | 6,03 | 0,0000 | 10/20 | 3,5 | cumple |
| Backend | 20 | 2185,3 | 3424,2 | 3445,8 | 5,76 | 0,0000 | 10/20 | 1,9 | cumple |
| N8N | 1 | 1314,6 | 2149,5 | 2163,2 | 0,75 | 0,0000 | 10/20 | 3,5 | cumple |
| N8N | 5 | 2129,8 | 3660,4 | 3674,8 | 1,82 | 0,0000 | 10/20 | 1,8 | cumple |
| N8N | 10 | 4519,8 | 8352,7 | 8596,7 | 1,83 | 0,0000 | 10/20 | 1,6 | no cumple (techo) |
| N8N | 20 | 8378,2 | 10183,6 | 10197,6 | 1,96 | 0,0000 | 10/20 | 1,2 | no cumple (techo) |

**Nota:** «Veredicto del nivel» es una derivacion editorial del criterio por nivel (el JSON solo emite el veredicto por capa con su lista de violaciones); la nota de la tabla lo declara. El p95 de cada subconjunto se registra en el memo, no en la tabla, para no exceder el ancho.

### D3 — Redaccion exacta de los dos veredictos

- **Backend:** «no sostenida» por la condicion de degradacion por inferencia en los niveles 1 y 5 (cociente 11,3 y 5,0 frente a T = 4); el techo absoluto de 5000 ms (p95 maximo 3424,2 ms), la tasa de error cero y la tolerancia de throughput se cumplen en los cuatro niveles.
- **N8N:** «no sostenida» por el techo absoluto de p95 en los niveles 10 y 20 (8352,7 y 10183,6 ms); el cociente de degradacion por inferencia se mantiene dentro de T = 4 en los cuatro niveles (3,5; 1,8; 1,6; 1,2), la tasa de error es cero y el throughput no decrece.
- **Global:** «no sostenida», el de la peor capa. El texto MUST NOT comparar este veredicto con el de capacidad ni presentarlo como saturacion del backend.

Redaccion fijada por este diseno; G1 resuelta (ver «Resoluciones de autores»):

> En la capa del backend la sonda arroja «no sostenida»: el techo absoluto de 5000~ms se cumple en los cuatro niveles (p95 maximo de 3424,2~ms), la tasa de error es cero y el throughput no decrece mas del 10~\%, pero la condicion de degradacion por inferencia se viola con 1 y 5 solicitudes concurrentes (el p95 del subconjunto escalado es 11,3 y 5,0 veces el del subconjunto deterministico, frente a T = 4). La violacion es relativa y no absoluta: no indica saturacion del backend, sino que la inferencia domina la latencia cuando la cola todavia no domina a ambos subconjuntos.

> En la capa del \emph{webhook} de N8N la sonda tambien arroja «no sostenida», por una condicion distinta: el techo absoluto de p95 se viola con 10 y 20 concurrentes (8352,7 y 10183,6~ms), mientras que el cociente de degradacion por inferencia se mantiene dentro de T = 4 en los cuatro niveles (3,5; 1,8; 1,6 y 1,2), la tasa de error es cero y el throughput no decrece. El veredicto global de la sonda es «no sostenida», el de la peor capa.

**Cautela obligatoria sobre el cociente:** no es monotono con la concurrencia. En el nivel 20 el subconjunto deterministico tambien esta dominado por la cola (p95 de 1782,9 ms en el backend), por lo que el cociente de 1,9 **subestima** la contribucion de la inferencia. El texto SHALL declarar que el cociente es interpretable como comparacion pareada en niveles bajos y no como contribucion marginal a alta concurrencia.

### D4 — Correcciones de las afirmaciones, con texto de reemplazo

1. `07-resultados.tex:336` (nota de tabla): «…y camino deterministico sin inferencia paga.» pasa a «…y camino deterministico de costo cero, sin inferencia paga; mide capacidad.»
2. `07-resultados.tex:343`: «…y el camino deterministico, sin inferencia paga; la latencia con inferencia no se midio.» pasa a «…y el camino deterministico de costo cero. Estas cifras miden capacidad y no incluyen la inferencia paga; la latencia con inferencia incluida se informa, como sonda ancilar de una sola corrida, en la \autoref{subsec:latencia-con-inferencia}.»
3. `08-discusion.tex:10`: (a) «El punto de convergencia del backend cumplio la regla prerregistrada» pasa a «En el camino deterministico, el punto de convergencia del backend cumplio la regla prerregistrada»; (b) «y la latencia no se midio por etapa.» pasa a «y la latencia no se midio por etapa; la sonda con inferencia incluida no la desagrega por etapa.»; (c) «La medicion corresponde a una sola maquina, a un perfil desechable y al camino deterministico, sin inferencia paga» pasa a «La medicion de capacidad corresponde a una sola maquina, a un perfil desechable y al camino deterministico, sin inferencia paga» y se agrega, al final del parrafo, la remision a la sonda con sus dos veredictos y su caracter ancilar.
4. `09-conclusiones.tex:6`: «…y sin cuello de botella en el punto de convergencia del backend» pasa a «…y sin cuello de botella en el punto de convergencia del backend en el camino deterministico, mas una sonda acotada con inferencia incluida, de una sola corrida, con veredicto «no sostenida» en ambas capas por condiciones distintas que no modifica el veredicto de capacidad», con remision a la subseccion nueva.
5. `04-marco-metodologico.tex:91` (una oracion al final del parrafo): declara la sonda, su tamano, la mezcla esperada del 50 %, la condicion T = 4 y la remision a la subseccion; aclara que no reemplaza el contraste de capacidad.

Criterio de redaccion: se conserva «la latencia no se midio por etapa» porque sigue siendo verdadero; la sonda compara subconjuntos, no instrumenta etapas.

### D5 — Los siete limites, literales

1. Una sola corrida.
2. n = 10 por subconjunto (20 solicitudes por nivel).
3. Una sola maquina.
4. Entorno desechable (perfil `corpus`, `mesa_de_ayuda_corpus`).
5. Gasto no registrado en la evidencia; no se estima como medido.
6. Deriva posible de proveedor y de version del modelo entre la corrida y la defensa; la evidencia no fija la version exacta del modelo.
7. No comparable en potencia con la corrida canonica de capacidad (120 solicitudes por nivel, 3 repeticiones) ni extrapolable a produccion.

### D6 — Registro en el memo

Seccion nueva y aditiva con el primer numero libre posterior a la `3.46` (al redactar, `3.47`; verificar al aplicar) y estado `condicional` por valor. No se reutilizan los huecos `3.39`–`3.42`. Se agrega una nota de remision en la `3.29` sin tocar sus cifras ni su estado. Se registran las metricas de las dos capas, los dos p95 por subconjunto, los dos veredictos y los limites, con la advertencia de no monotonia del cociente.

### D7 — Anexo de numeros canonicos: sin filas nuevas

`sec:anexo-numeros-canonicos` reune los numeros canonicos que el cuerpo cita; las cifras de `tab:carga-multicanal` no figuran alli y la tabla se sostiene con su nota de fuente. La sonda sigue el mismo precedente: tabla con nota de fuente en el cuerpo y valores en el memo con estado `condicional`. No se agregan filas al anexo, porque los valores no son canonicos.

### D8 — Verificacion de fidelidad numerica (Strict TDD)

El unico artefacto nuevo verificable es la tabla. Se agrega `docs/Tesis/Correcciones/test_cotejar_carga_inferencia.py` (Strict TDD) que extrae las filas de `tab:carga-inferencia` del `.tex` y las compara con el JSON de evidencia: 8 filas, orden capa/nivel, valores redondeados, cociente recalculado y veredicto derivado. Triangulacion con copias mutadas en directorio temporal (fila ausente, redondeo erroneo, cociente que no cierra, capa invertida). El test es de solo lectura y no mide de nuevo.

### D9 — Orden de aplicacion y anclajes

Precondicion: `c-242` aplicado (toca `08` y `09`). Los anclajes se localizan por texto, no por numero de linea. Si `c-242` cambio la redaccion del parrafo de la subsidiaria multicanal, se reescribe el pasaje completo en vez de parchear la oracion. `openspec list --json` y `openspec status --change c-242-…` son la comprobacion.

### D10 — Gobernanza y compuertas

**ALTA**: cambia un veredicto publicado y el manuscrito entregado. Cuatro compuertas de autores antes de escribir `.tex`: (G1) lectura autorizada del veredicto del backend como violacion relativa, no saturacion — **confirmada**; (G2) suficiencia de una corrida con n = 10 — **abierta**, con una investigacion aparte en curso (corrida acotada de repeticion y plan de instrumentacion en evaluacion); (G3) gasto real y version/instantanea del modelo — **abierta**, el texto no los estima como medidos; (G4) version de release — **resuelta en `v1.6.1`**, con la aprobacion del director pendiente para taguear. El agente no decide las compuertas abiertas.

### D11 — Release (no se ejecuta en esta fase)

Bump de version a `v1.6.1` en `00-portada.tex:31`, `Bibliography_base.bib:919` y la mencion del Anexo B; recompilar; regenerar `paper/compilacion.md`, `tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt`, `tesis_para_agente.md` y `docs/Tesis/tesis_ultima_version.pdf`; commit de contenido, tag anotado y commit posterior que consigna el hash completo en el Anexo B (misma convencion que `c-239`). Sin OK expreso de los autores no hay commit ni tag. El locus de version en `Bibliography_base.bib:919` es el titulo de la entrada de repositorio y se conserva.

## Risks / Trade-offs

- [La sonda se lee como capacidad] → requisito explicito de primacia de `tab:carga-multicanal`, rotulo «ancilar» y prohibicion de extrapolar.
- [El veredicto del backend se lee como saturacion] → declarar la condicion relativa, el techo absoluto cumplido y la cautela de no monotonia (G1 resuelta: la lectura relativa esta autorizada).
- [El cociente de 1,9 se cita como prueba de que la inferencia deja de pesar] → nota obligatoria de que a alta concurrencia ambos subconjuntos estan dominados por la cola.
- [Una corrida con n = 10 se sobreinterpreta] → siete limites literales y prohibicion de comparar potencia con c-218.
- [Conflicto con `c-242`] → aplicar despues y re-localizar por texto.
- [La tabla desborda el ancho] → `\footnotesize`, `\tabcolsep=3pt`, encabezados abreviados; criterio de rechazo: cualquier `Overfull \hbox` originado en la tabla obliga a mover columnas al memo o a rotar la tabla, no a recortar cifras.

## Migration Plan

1. Verificar precondiciones (`c-242` aplicado) y registrar linea base (`git status`, `git describe`, `compilacion.md`).
2. Comprobar la fidelidad numerica con el test de D8 (RED antes de la tabla, GREEN despues).
3. Editar el memo (seccion nueva y nota de remision), luego los `.tex`: subseccion nueva, correcciones de D4 y oracion de D4.5.
4. Verificar: `openspec validate … --strict`, `verify_citations.py`, matriz de trazabilidad, test de fidelidad, recompilacion de verificacion.
5. **Rollback:** revertir los `.tex`, retirar la seccion del memo y la entrada del registro, y recompilar. La evidencia y el arnes no se tocan.
6. Release: solo con las compuertas de autores de D10 resueltas y autorizacion expresa.

## Resoluciones de autores

- **G1 (confirmado):** los autores autorizan informar el veredicto del backend como violacion de una condicion RELATIVA (degradacion por inferencia: `p95 escalado / p95 deterministico > T = 4`), de forma explicita NO como saturacion del backend. El techo absoluto (p95 maximo 3424,2 ms), la tolerancia de throughput y la tasa de error cero se mantienen como cumplidos. Resuelta; no es pregunta abierta y habilita la redaccion de D3 tal cual.
- **G4 (resuelto):** la version de release es `v1.6.1` (corrige la propuesta previa).

## Open Questions

- **G2:** ¿Una sola corrida con n = 10 por subconjunto alcanza para informar el resultado en el ejemplar, o se declara insuficiente y se integra solo como nota metodologica? La decision cambia el alcance de la subseccion y de las specs. **Abierta:** corre una investigacion aparte; se evaluan una corrida acotada de repeticion y un plan de instrumentacion. No se inventa respuesta.
- **G3:** ¿Cual es el gasto real de la corrida y la version/instantanea exacta del modelo? La evidencia no los registra. **Abierta:** el change MUST NOT afirmar el gasto ni la instantanea del modelo como medidos hasta que se registren.
- **G5:** ¿Se autoriza la oracion de remision en `04-marco-metodologico.tex`? Si no, la subseccion queda sin anclaje metodologico y debe autodescribir el protocolo.
