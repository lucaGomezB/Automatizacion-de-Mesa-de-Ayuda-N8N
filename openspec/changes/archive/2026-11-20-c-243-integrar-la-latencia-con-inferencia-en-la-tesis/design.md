## Context

Ver `proposal.md` — Why. Hechos del repositorio que condicionan el enfoque (verificados 2026-11-18):

- **La corrida original existe y esta versionada.** `evaluation/evidence/load_test_inferencia_2026-11-17.json` (SHA-256 `08da89c6e3b21747afdf970112a3c18303b5567f6df0528027ea14f42e020c28`) y su `.md` (`3803e7c9…`), producidos por `scripts/load_test/load_test_inference.py` en el commit `bbc5865` (release `v1.6.0`). Prerregistro: `scripts/load_test/PRERREGISTRO_latencia_con_inferencia.md` (`8d8d5261…`).
- **La corrida ampliada existe y esta versionada.** `evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json` y su `.md`, producidos por el arnes ampliado sobre el commit base `d0592d3` (fecha UTC `2026-11-18T20:04:46Z`, corrida `6ad5e32d`, N8N `2.11.2`, misma fixture `88cab878…`); la instrumentacion aditiva que produce esa evidencia se commiteo en `2159e02`. Prerregistro: `scripts/load_test/PRERREGISTRO_latencia_con_inferencia_ampliada.md`. El arnes no modifica `load_test.py` ni la guarda de costo cero.
- **El ejemplar niega la medicion en cuatro loci.** `07-resultados.tex:336` (nota de `tab:carga-multicanal`), `07-resultados.tex:343` («la latencia con inferencia no se midio»), `08-discusion.tex:10` (medicion «del camino deterministico, sin inferencia paga») y `09-conclusiones.tex:6` («sin cuello de botella en el punto de convergencia del backend»).
- **`08-discusion.tex` y `09-conclusiones.tex` los toca `c-242`** (tareas 3.5 y siguientes). Este change se aplica despues y re-localiza por texto.
- **La tabla de capacidad de c-218 es la evidencia primaria** (`tab:carga-multicanal`, 120 solicitudes por nivel, 3 repeticiones, camino deterministico de costo cero).
- **Decision editorial de los autores: opcion A.** La tabla combina dos corridas de distinta potencia: niveles 1 y 5 desde la corrida ampliada (60 solicitudes por nivel, 3 repeticiones, n = 90 escalados por subconjunto y capa) y niveles 10 y 20 desde la original (20 solicitudes por nivel, 1 repeticion, n = 10). Ninguna es comparable en potencia con la canonica de 120 por nivel.
- **El memo no registra la sonda.** La ultima seccion vigente es la `3.46`; la `3.29` es la lectura canonica de capacidad. La numeracion tiene huecos (`3.39` a `3.42` no existen); no se reutilizan.
- **El Anexo B fija el hash del commit de entrega** (`12-anexos.tex`, `sec:anexo-repositorio`), y la version esta en `00-portada.tex:31` y `Bibliography_base.bib:919`.

## Goals / Non-Goals

**Goals:**

- Informar la sonda con inferencia incluida con su tabla combinada de dos corridas, sus tres veredictos y sus limites, sin convertirla en un resultado de capacidad.
- Corregir las cuatro afirmaciones que hoy son verdaderas solo para el camino deterministico.
- Registrar los valores como `condicional` en el memo, con procedencia por valor y por corrida de origen, sin tocar la `3.29`.
- Dejar la release preparada (version, hash, derivados) sin ejecutarla.

**Non-Goals:**

- Reejecutar la sonda, cambiar el arnes, el fixture o la guarda de costo cero.
- Reabrir el veredicto de capacidad de c-218 o reemplazar `tab:carga-multicanal`.
- Instrumentar latencia por etapa del clasificador (la sonda no la desagrega).
- Commit, tag o push; recompilar en esta fase.

## Decisions

### D1 — Subseccion nueva en resultados y tabla en el cuerpo, sin anexo

**Elegido:** una subseccion `subsec:latencia-con-inferencia` en `07-resultados.tex`, inmediatamente despues de `subsec:carga-concurrente` y antes del `\newpage`, con la tabla `tab:carga-inferencia` en el cuerpo.

**Por que:** son 8 filas por 11 columnas, del mismo orden que `tab:carga-multicanal` (8 por 7); entra con `\footnotesize` y `\setlength{\tabcolsep}{3pt}`. La evidencia primaria y la sonda quedan contiguas y comparables de un vistazo. Un anexo separaria la sonda de la tabla que la contextualiza y agregaria paginas a un documento ya cerrado.

**Alternativas rechazadas:** (i) anexo con la tabla completa — solo se justificaria si la tabla no entrara a lo ancho, y entra; (ii) integrar la sonda como filas adicionales de `tab:carga-multicanal` — mezclaria dos disenos (120 contra 20/60 solicitudes por nivel) y romperia la lectura de capacidad.

### D2 — Esquema de la tabla (opcion A: dos corridas combinadas)

Columnas: Capa; **Corrida/n**; Concurrencia; p50 (ms); p95 (ms); p99 (ms); Throughput (sol./s); Tasa de error; Escalados; \(r = \mathrm{p95}_{esc}/\mathrm{p95}_{det}\); Veredicto del nivel. La columna «Corrida/n» rotula, por fila, la corrida de origen (`ampl.` / `orig.`) y el n escalado por subconjunto (90 en los niveles 1 y 5; 10 en los niveles 10 y 20). Una fila por capa y nivel (8 filas), con `\midrule` entre las dos capas. Redondeo a un decimal para latencias, dos decimales para throughput y **para el cociente \(r\)** (la corrida ampliada existe para afinar su precision) y cuatro para la tasa de error (0,0000).

Valores del artefacto (niveles 1 y 5 recomputados del JSON ampliado; 10 y 20 del JSON original):

| Capa | Corrida/n | Conc. | p50 | p95 | p99 | sol./s | Error | Esc. | r | Veredicto del nivel |
|---|---|---|---|---|---|---|---|---|---|---|
| Backend | ampl. 90 | 1 | 1007,6 | 2089,3 | 2330,6 | 0,93 | 0,0000 | 90/180 | 5,05 | no cumple (inferencia) |
| Backend | ampl. 90 | 5 | 1221,9 | 2708,4 | 3968,1 | 3,50 | 0,0000 | 90/180 | 3,74 | cumple |
| Backend | orig. 10 | 10 | 1182,9 | 2759,6 | 2763,9 | 6,03 | 0,0000 | 10/20 | 3,55 | cumple |
| Backend | orig. 10 | 20 | 2185,3 | 3424,2 | 3445,8 | 5,76 | 0,0000 | 10/20 | 1,93 | cumple |
| N8N | ampl. 90 | 1 | 1757,9 | 2919,8 | 5033,4 | 0,56 | 0,0000 | 90/180 | 2,35 | cumple |
| N8N | ampl. 90 | 5 | 4307,7 | 7545,7 | 8684,4 | 1,07 | 0,0000 | 90/180 | 1,70 | no cumple (techo) |
| N8N | orig. 10 | 10 | 4519,8 | 8352,7 | 8596,7 | 1,83 | 0,0000 | 10/20 | 1,58 | no cumple (techo) |
| N8N | orig. 10 | 20 | 8378,2 | 10183,6 | 10197,6 | 1,96 | 0,0000 | 10/20 | 1,22 | no cumple (techo) |

**Nota:** «Veredicto del nivel» es una derivacion editorial del criterio por nivel (el JSON solo emite el veredicto por capa con su lista de violaciones); la nota de la tabla lo declara. El p95 de cada subconjunto se registra en el memo, no en la tabla, para no exceder el ancho.

### D3 — Redaccion exacta de los tres veredictos

- **Backend:** «no sostenida» por la condicion de degradacion por inferencia **solo en el nivel 1** (cociente 5,05 frente a T = 4); el nivel 5 **cumple** (cociente 3,74, contra 5,0 en la corrida original). El techo absoluto de 5000 ms (p95 maximo 3424,2 ms), la tasa de error cero y la tolerancia de throughput se cumplen en los cuatro niveles. La violacion es relativa y NO es saturacion del backend.
- **N8N:** «no sostenida» por el techo absoluto de p95 en los niveles 5 (corrida ampliada, 7545,7 ms), 10 (8352,7 ms) y 20 (10183,6 ms); el nivel 1 cumple (2919,8 ms). El cociente de degradacion por inferencia se mantiene dentro de T = 4 en los cuatro niveles (2,35; 1,70; 1,58; 1,22), la tasa de error es cero y el throughput no decrece.
- **Global:** «no sostenida», el de la peor capa. El texto MUST NOT comparar este veredicto con el de capacidad ni presentarlo como saturacion del backend.

Redaccion fijada por este diseno:

> En la capa del backend la sonda arroja «no sostenida»: el techo absoluto de 5000~ms se cumple en los cuatro niveles (p95 maximo de 3424,2~ms), la tasa de error es cero y el throughput no decrece mas del 10~\%, pero la condicion de degradacion por inferencia se viola en el nivel de 1 solicitud concurrente (el p95 del subconjunto escalado es 5,05 veces el del subconjunto deterministico, frente a T = 4); el nivel de 5 concurrentes pasa a cumplirla (3,74). La violacion es relativa y no absoluta: no indica saturacion del backend, sino que la inferencia domina la latencia cuando la cola todavia no domina a ambos subconjuntos.

> En la capa del \emph{webhook} de N8N la sonda tambien arroja «no sostenida», por una condicion distinta: el techo absoluto de p95 se viola con 5, 10 y 20 concurrentes (7545,7; 8352,7 y 10183,6~ms), mientras que el cociente de degradacion por inferencia se mantiene dentro de T = 4 en los cuatro niveles (2,35; 1,70; 1,58 y 1,22), la tasa de error es cero y el throughput no decrece. El veredicto global de la sonda es «no sostenida», el de la peor capa.

**Cautela obligatoria sobre el cociente:** no es monotono con la concurrencia. En el nivel 20 el subconjunto deterministico tambien esta dominado por la cola (p95 de 1782,9 ms en el backend), por lo que el cociente de 1,93 **subestima** la contribucion de la inferencia. El texto SHALL declarar que el cociente es interpretable como comparacion pareada en niveles bajos y no como contribucion marginal a alta concurrencia.

### D4 — Correcciones de las afirmaciones, con texto de reemplazo

1. `07-resultados.tex:336` (nota de tabla): «…y camino deterministico sin inferencia paga.» pasa a «…y camino deterministico de costo cero, sin inferencia paga; mide capacidad.»
2. `07-resultados.tex:343`: «…y el camino deterministico, sin inferencia paga; la latencia con inferencia no se midio.» pasa a «…y el camino deterministico de costo cero. Estas cifras miden capacidad y no incluyen la inferencia paga; la latencia con inferencia incluida se informa, como sonda ancilar de dos corridas combinadas, en la \autoref{subsec:latencia-con-inferencia}.»
3. `08-discusion.tex:10`: (a) «El punto de convergencia del backend cumplio la regla prerregistrada» pasa a «En el camino deterministico, el punto de convergencia del backend cumplio la regla prerregistrada»; (b) «y la latencia no se midio por etapa.» pasa a «y la latencia no se midio por etapa; la sonda con inferencia incluida no la desagrega por etapa.»; (c) «La medicion corresponde a una sola maquina, a un perfil desechable y al camino deterministico, sin inferencia paga» pasa a «La medicion de capacidad corresponde a una sola maquina, a un perfil desechable y al camino deterministico, sin inferencia paga» y se agrega, al final del parrafo, la remision a la sonda con sus tres veredictos y su caracter ancilar.
4. `09-conclusiones.tex:6`: «…y sin cuello de botella en el punto de convergencia del backend» pasa a «…y sin cuello de botella en el punto de convergencia del backend en el camino deterministico, mas una sonda acotada con inferencia incluida, de dos corridas combinadas, con veredicto «no sostenida» en ambas capas por condiciones distintas que no modifica el veredicto de capacidad», con remision a la subseccion nueva.
5. `04-marco-metodologico.tex:91` (una oracion al final del parrafo): declara la sonda, su tamano por corrida, la mezcla esperada del 50 %, la condicion T = 4 y la remision a la subseccion; aclara que no reemplaza el contraste de capacidad.

Criterio de redaccion: se conserva «la latencia no se midio por etapa» porque sigue siendo verdadero; la sonda compara subconjuntos, no instrumenta etapas.

### D5 — Los siete limites, literales, con el n y las repeticiones por fila

1. Sonda de **dos corridas complementarias**, no una serie; los niveles 1 y 5 provienen de la corrida ampliada y los niveles 10 y 20 de la corrida original.
2. n escalado por subconjunto distinto por fila: **90 en los niveles 1 y 5** (60 solicitudes por nivel, 3 repeticiones) y **10 en los niveles 10 y 20** (20 solicitudes por nivel, 1 repeticion).
3. Una sola maquina.
4. Entorno desechable (perfil `corpus`, `mesa_de_ayuda_corpus`).
5. El gasto solo consta en la corrida ampliada y su procedencia es `tokens_calculado` (calculado desde tokens con el precio declarado), no facturacion del proveedor; la corrida original no lo registra.
6. Deriva posible de proveedor y de version del modelo entre las corridas, la defensa y el estado actual.
7. No comparable en potencia con la corrida canonica de capacidad (120 solicitudes por nivel, 3 repeticiones) ni extrapolable a produccion.

### D6 — Registro en el memo

Seccion nueva y aditiva con el primer numero libre posterior a la `3.46` (al redactar, `3.47`; verificar al aplicar) y estado `condicional` por valor. No se reutilizan los huecos `3.39`–`3.42`. Se registran las **8 filas** con su corrida de origen y su n, los p95 por subconjunto, las **constantes de ambas corridas** (niveles, solicitudes por nivel, repeticiones y tope de cada una) y los tres veredictos, con la advertencia de no monotonia del cociente. Se agrega una nota de remision en la `3.29` sin tocar sus cifras ni su estado.

### D7 — Anexo de numeros canonicos: sin filas nuevas

`sec:anexo-numeros-canonicos` reune los numeros canonicos que el cuerpo cita; las cifras de `tab:carga-multicanal` no figuran alli y la tabla se sostiene con su nota de fuente. La sonda sigue el mismo precedente: tabla con nota de fuente en el cuerpo y valores en el memo con estado `condicional`. No se agregan filas al anexo, porque los valores no son canonicos.

### D8 — Verificacion de fidelidad numerica (Strict TDD)

El unico artefacto nuevo verificable es la tabla. Se agrega `docs/Tesis/Correcciones/test_cotejar_carga_inferencia.py` (Strict TDD) que extrae las filas de `tab:carga-inferencia` del `.tex` y las compara con **ambos JSON de evidencia**: lee la corrida ampliada para los niveles 1 y 5 y la original para los niveles 10 y 20, y valida ademas la **corrida de origen y el n** rotulados en cada fila. Comprueba 8 filas, orden capa/nivel, valores redondeados, cociente recalculado y veredicto derivado. Triangulacion con copias mutadas en directorio temporal (fila ausente, redondeo erroneo, cociente que no cierra, capa invertida, corrida de origen equivocada). El test es de solo lectura y no mide de nuevo.

### D9 — Orden de aplicacion y anclajes

Precondicion: `c-242` aplicado (toca `08` y `09`). Los anclajes se localizan por texto, no por numero de linea. Si `c-242` cambio la redaccion del parrafo de la subsidiaria multicanal, se reescribe el pasaje completo en vez de parchear la oracion. `openspec list --json` y `openspec status --change c-242-…` son la comprobacion.

### D10 — Gobernanza y compuertas

**ALTA**: cambia un veredicto publicado y el manuscrito entregado. Cuatro compuertas de autores antes de escribir `.tex`, **todas resueltas**: (G1) lectura autorizada del veredicto del backend como violacion relativa, no saturacion — **resuelta**; (G2) suficiencia y decision editorial — **resuelta**: la corrida ampliada ya se ejecuto y la opcion A (tabla combinada de dos corridas) es la decision; (G3) gasto y version/instantanea del modelo — **resuelta**: `gemini-3.6-flash`, 274920/6648/281568 tokens y USD 0,23112 con `gasto_origen = tokens_calculado`; (G4) version de release — **resuelta en `v1.6.1`**, con la aprobacion del director pendiente para taguear.

### D11 — Release (no se ejecuta en esta fase)

Bump de version a `v1.6.1` en `00-portada.tex:31`, `Bibliography_base.bib:919` y la mencion del Anexo B; recompilar; regenerar `paper/compilacion.md`, `tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt`, `tesis_para_agente.md` y `docs/Tesis/tesis_ultima_version.pdf`; commit de contenido, tag anotado y commit posterior que consigna el hash completo en el Anexo B (misma convencion que `c-239`). Sin OK expreso de los autores no hay commit ni tag. El locus de version en `Bibliography_base.bib:919` es el titulo de la entrada de repositorio y se conserva.

## Risks / Trade-offs

- [La sonda se lee como capacidad] → requisito explicito de primacia de `tab:carga-multicanal`, rotulo «ancilar» y prohibicion de extrapolar.
- [El veredicto del backend se lee como saturacion] → declarar la condicion relativa (solo nivel 1), el techo absoluto cumplido y la cautela de no monotonia.
- [Se mezclan dos corridas de distinta potencia sin decirlo] → columna «Corrida/n» por fila, nota de la tabla con ambas fuentes y siete limites con el n y las repeticiones por fila.
- [El cociente de 1,93 se cita como prueba de que la inferencia deja de pesar] → nota obligatoria de que a alta concurrencia ambos subconjuntos estan dominados por la cola.
- [Conflicto con `c-242`] → aplicar despues y re-localizar por texto.
- [La tabla desborda el ancho] → `\footnotesize`, `\tabcolsep=3pt`, encabezados abreviados; criterio de rechazo: cualquier `Overfull \hbox` originado en la tabla obliga a mover columnas al memo o a rotar la tabla, no a recortar cifras.

## Migration Plan

1. Verificar precondiciones (`c-242` aplicado) y registrar linea base (`git status`, `git describe`, `compilacion.md`).
2. Comprobar la fidelidad numerica con el test de D8 (RED antes de la tabla, GREEN despues), leyendo ambos JSON y la corrida de origen por fila.
3. Editar el memo (seccion nueva y nota de remision), luego los `.tex`: subseccion nueva, correcciones de D4 y oracion de D4.5.
4. Verificar: `openspec validate … --strict`, `verify_citations.py`, matriz de trazabilidad, test de fidelidad, recompilacion de verificacion.
5. **Rollback:** revertir los `.tex`, retirar la seccion del memo y la entrada del registro, y recompilar. La evidencia y el arnes no se tocan.
6. Release: solo con las compuertas de autores de D10 resueltas y autorizacion expresa.

## Resoluciones de autores

- **G1 (resuelto):** los autores autorizan informar el veredicto del backend como violacion de una condicion RELATIVA (degradacion por inferencia: `p95 escalado / p95 deterministico > T = 4`), de forma explicita NO como saturacion del backend. El techo absoluto (p95 maximo 3424,2 ms), la tolerancia de throughput y la tasa de error cero se mantienen como cumplidos. Habilita la redaccion de D3 tal cual.
- **G2 (resuelto):** la corrida ampliada ya se ejecuto y la decision editorial es la opcion A (tabla combinada de 8 filas). Hechos de la corrida ampliada: niveles 1 y 5, 60 solicitudes por nivel, 3 repeticiones, 2 capas = 720 solicitudes; 360 escaladas (90 por nivel y capa); tope USD 1,25; duracion 13 min 32 s; commit base `d0592d3`; corrida `6ad5e32d`; N8N `2.11.2`; fixture `88cab878…`. Veredictos: global `no sostenida`; backend `no sostenida` solo por el nivel 1 (r = 5,05), con el nivel 5 ahora cumpliendo (r = 3,74, contra 5,0 en la corrida original); N8N `no sostenida` por techo absoluto en el nivel 5 (p95 = 7545,7 ms), con el nivel 1 cumpliendo (2919,8 ms); cero errores en los cuatro niveles. Efecto: la corrida ampliada afina la precision de `r` y registra gasto y modelo; no cambia la evidencia primaria ni el veredicto global.
- **G3 (resuelto):** 360 eventos `gemini_classified`, todos con conteo de la API (`tokens_origen = api`); 274920 tokens de entrada, 6648 de salida, 281568 totales; `model_version = gemini-3.6-flash`; costo USD 0,23112 con el precio declarado de la tesis (escenario `introductorio`); `gasto_origen = tokens_calculado` (no es facturacion del proveedor).
- **G4 (resuelto):** la version de release es `v1.6.1`.
- **Instrumentacion:** aditiva en el backend (`gemini_classified` con `modelo_solicitado`, `model_version`, `tokens_entrada`, `tokens_salida`, `tokens_total`, `tokens_origen`): solo lectura, no altera el camino de costo cero.

## Open Questions

Ninguna. Las cuatro compuertas de autores (G1 a G4) estan resueltas; la decision editorial de G2 es la opcion A.
