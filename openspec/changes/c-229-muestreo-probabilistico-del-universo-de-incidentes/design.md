# Design: Muestreo probabilistico del universo de incidentes

## Context

La muestra del estudio es no probabilistica por conveniencia: son los `200` incidentes cronometrados
en la campana manual (`04-marco-metodologico.tex:46`), de una sola organizacion, sin estratificacion
ni asignacion proporcional (memo, seccion 3.17, ap. (f)). El universo trimestral es
`N = 42 x 63 = 2.646` y el margen de error `6,66 %` se calcula como "margen de error implicado", que
"presupone un muestreo aleatorio que no se realizo" (`04-marco-metodologico.tex:52`). La distribucion
del universo por sector NO esta disponible (memo, linea 376).

La lectura ponderada vigente de la exactitud estricta es `0,7489`, con bootstrap `[0,6822; 0,8099]`
(`07-resultados.tex:393`; memo, secciones 3.25 y 3.32). Sus pesos son la composicion por sector del
corpus de 200 (`evaluation/linea_de_base.py::prevalencia_natural` y `lectura_ponderada`), es decir una
**post-estratificacion a la composicion de la muestra**, no a la del universo (memo, requisito
OOS-020). El antecedente del diseno estratificado ya esta en `OOS-006` (cuotas por canal y sector,
sobremuestreo de la clase minoritaria y ponderacion por la distribucion del universo).

La linea de trabajo futuro de la tesis pide repetir la validacion "sobre corpus de composicion
natural, con cuotas prefijadas por canal y por sector" y estimar el intervalo "sobre el universo
completo, sin excluir casos" (`10-recomendaciones.tex:26`).

**Insumos versionados (solo lectura):**

- `evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.json`: lectura ponderada
  `0,7489` con su bootstrap `[0,6822; 0,8099]` y los pesos por sector leidos del corpus de 200.
- `data/corpus_evaluacion_pseudonimizado.json`: composicion por sector del corpus de 200 (vector
  `16 / 85 / 67 / 31 / 1`, suma `200`), usada como peso del anclaje.
- `evaluation/linea_de_base.py::lectura_ponderada`: funcion de post-estratificacion reutilizable;
  `evaluation/metrics.py::intervalo_wilson` e `evaluation/stats.py` para los IC y remuestreos.

## Goals / Non-Goals

**Goals:**

- Definir el universo, el marco muestral y los estratos (sector, canal, complejidad) con procedencia y
  criterio de inclusion verificable, registrados antes de reunir la muestra.
- Fijar un diseno estratificado probabilistico con cuotas prefijadas por canal y sector, denominadores
  y reglas de decision de tres vias, sin reajuste posterior.
- Entregar la maquinaria de estimacion ponderada (Horvitz-Thompson y post-estratificacion) con el
  efecto de diseno y un IC sobre el universo COMPLETO, sin excluir casos.
- Dejar el diseno declarado como `condicional` y honesto sobre su dependencia de datos que aun no
  existen y de la cooperacion de la organizacion.
- No cambiar ningun valor canonico y no tocar el corpus, las predicciones ni los artefactos congelados.

**Non-Goals:**

- Ejecutar la campana probabilistica (requiere poblacion del periodo y cooperacion de la organizacion).
- Elevar la exactitud del clasificador: el diseno hace valida la ESTIMACION, no mejora el modelo.
- Reemplazar la lectura ponderada `0,7489` ni la cifra primaria `0,6893`.
- Reescribir las secciones existentes de resultados, discusion o metodologia; se agregan parrafos.
- Resolver la limitacion de una sola organizacion o `n = 200` sin datos nuevos.

## Decisions

### D1 — Alcance del change: diseno + herramienta + declaracion, sin campana

El change entrega (a) el protocolo del diseno muestral, (b) la herramienta de estimacion ponderada
probada con TDD y anclada en el valor vigente, y (c) la prosa y el registro del memo. La **ejecucion**
de la campana (recolectar la poblacion del periodo, etiquetar, invocar al clasificador) queda fuera:
depende de datos que aun no existen. Las cifras del diseno probabilistico quedan en estado
`condicional`. Alternativa descartada: simular una muestra probabilistica y reportarla como resultado,
porque confundiria el diseno con una medicion y violaria la regla de rotulo del proyecto.

### D2 — Definicion del universo, marco y estratos

- **Universo:** poblacion de incidentes informaticos registrados por la mesa de ayuda en el periodo
  declarado. El punto de partida operativo es `N = 42 x 63 = 2.646` incidentes por trimestre
  (memo, seccion 3.4), que el protocolo SHALL confirmar contra el registro del periodo elegido.
- **Marco muestral:** el registro operativo de incidentes del periodo (la tabla de incidentes de la
  base), con inclusion enumerable por identificador y probabilidad conocida y mayor que cero.
- **Estratos:** `sector` (las cinco cadenas canonicas), `canal` (correo, formulario, telefonia) y
  `complejidad` (definicion operacional a fijar en el protocolo, por ejemplo segun exigencia de
  contexto o longitud clasificable). La distribucion del universo por estrato SHALL derivarse del
  registro y, si no esta disponible, declararse como no disponible con el metodo para obtenerla
  (MUST NOT usar la composicion del corpus de 200 como sustituto).
- Alternativa descartada: estratificar solo por sector, porque el canal es una fuente de variacion
  medida (reducciones y exactitud difieren por canal) y las cuotas de la linea de trabajo futuro son
  por canal y por sector.

### D3 — Estimacion: Horvitz-Thompson, post-estratificacion y efecto de diseno

- **Pesos de Horvitz-Thompson:** `w_i = 1 / pi_i`, con `pi_i` la probabilidad de inclusion de la unidad
  en su estrato; el estimador de la exactitud estricta es la razon ponderada de aciertos sobre casos.
- **Post-estratificacion:** calibracion de los pesos a los totales conocidos de los estratos del
  universo cuando la distribucion este disponible; reutiliza la forma de `lectura_ponderada` sin
  modificarla (o su generalizacion a ponderacion por unidad).
- **Efecto de diseno (Kish):** `DEFF = n * sum(w_i^2) / (sum w_i)^2`. Se informa junto a la exactitud
  ponderada. El DEFF del diseno probabilistico es **no computable sin la muestra**; el DEFF de la
  post-estratificacion sobre el corpus existente se informa como ilustracion, rotulado y `condicional`.
- **Intervalo de confianza:** bootstrap percentil por unidad (semilla fija) sobre el **universo
  completo, sin exclusion**. Se reporta el metodo y el nivel.
- Alternativa descartada: IC de Wilson sobre la muestra, porque presupone muestreo aleatorio simple y
  no incorpora el diseno ni el efecto de diseno.

### D4 — Herramienta offline con anclaje en el valor vigente

Script `evaluation/data/campana/analisis/estimador_muestreo_probabilistico_c229.py`, pruebas en
`test_estimador_muestreo_probabilistico_c229.py`, salidas `.json`, `.md` y `.SHA256SUMS.txt` en la
misma carpeta (UTF-8 sin BOM, LF). Solo lectura, sin red ni Gemini, determinista. Funciones puras con
prueba sintetica antes de implementar:

| Funcion | Que calcula | Reutiliza |
|---|---|---|
| `pesos_horvitz_thompson(estratos, cuotas)` | `w_i = 1 / pi_i` por estrato | nada (pura) |
| `post_estratificar(casos, totales_universo)` | Pesos calibrados a los totales del universo | forma de `lectura_ponderada` |
| `exactitud_ponderada(aciertos, pesos)` | Razon ponderada de aciertos | `evaluation/metrics.py` |
| `efecto_diseno(pesos)` | DEFF de Kish | nada (pura) |
| `ic_bootstrap_universo(...)` | IC bootstrap del estimador ponderado, sin exclusion | `evaluation/stats.py` |

**Anclaje que aborta antes de escribir:** la configuracion de post-estratificacion por la composicion
del corpus de 200 sobre el corpus arbitrado DEBE reproducir `0,7489` y su bootstrap
`[0,6822; 0,8099]`; si no, el script termina con codigo distinto de cero sin escribir salidas. La
composicion se lee de `data/corpus_evaluacion_pseudonimizado.json` (vector `16/85/67/31/1`) y la
lectura de `analisis_propagacion_arbitraje_c221.json`, no de constantes. Alternativa descartada:
reportar solo el DEFF sin anclarlo, porque no dejaria comando reproducible ni verificacion de que la
funcion de ponderacion no deriva.

### D5 — Gobernanza y consentimiento

El bloque A (protocolo con datos nuevos, etiquetado humano y consentimiento) es **HIGH**: se propone y
se espera la revision de los autores antes de fijar cuotas, periodo y protocolo de consentimiento; NO
se ejecuta ninguna recoleccion en este change. El bloque B (herramienta offline sobre artefactos
versionados) es **MEDIUM**. Los bloques C y D (prosa y memo) son **MEDIUM** con checkpoint de los
autores sobre la redaccion de la amenaza 5. No hay bloque CRITICAL: no se toca el capitulo legal; el
protocolo cita sus requisitos de consentimiento y el capitulo 11 los desarrolla.

### D6 — Ubicacion y forma en la tesis

- `04-marco-metodologico.tex` (`subsec:poblacion-muestra-corpus`): un parrafo que declara el diseno
  probabilistico planificado, su estado `condicional` y que no eleva la exactitud sino que valida la
  estimacion. No se agrega subseccion.
- `07-resultados.tex` (subseccion de validacion fuera de muestra): se agrega, junto a la lectura
  ponderada `0,7489`, el efecto de diseno rotulado como complementario y `condicional`; la cifra
  primaria no cambia.
- `08-discusion.tex` (amenaza 5 y limitacion de seleccion): una oracion que remite al diseno y precisa
  que no elimina el sesgo sin datos.
- `10-recomendaciones.tex` (`subsec:corpus-independiente`): remite al diseno probabilistico con cuotas
  prefijadas por canal y sector y al IC sobre el universo completo.
- Todas las citas de cifras usan la seccion del memo, no constantes inline.

### D7 — Orden de las tareas

1. Linea de base y verificacion de estado (incluye fijar el numero libre del memo).
2. Protocolo del diseno muestral (bloque HIGH; checkpoint de los autores antes de fijar cuotas).
3. Herramienta TDD, salidas y SHA-256 con anclaje.
4. Seccion aditiva del memo.
5. Prosa de la tesis (04, 07, 08, 10).
6. Trazabilidad y verificaciones; cierre.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| El diseno se lee como medicion realizada | Rotulo `condicional` y "diseno planificado" en protocolo, prosa y memo |
| Se confunde el DEFF de la post-estratificacion con el del diseno | D3 declara el DEFF del diseno no computable sin la muestra; el del corpus se rotula ilustrativo |
| La muestra de 200 se lee como probabilistica | Se declara no probabilistica por conveniencia en 4.4 y el resumen; el diseno es `condicional` |
| La ponderacion duplica o reinterpreta `0,7489` | Se ancla y se cita desde el memo; solo se agrega el efecto de diseno |
| Colision de numeracion del memo | Fijar el primer numero libre al aplicar (hoy `3.37`; esperado `3.40`) |
| Crecer en paginas | Un parrafo por archivo; verificar `\@abspage@last` y compensar dentro del mismo bloque |
| Dependencia externa no satisfecha | El change queda util como diseno + herramienta; las cifras del diseno quedan `condicional` |

## Migration Plan

1. Preparacion y linea de base (tareas 0).
2. Protocolo del diseno muestral (tarea 1), con checkpoint HIGH de los autores.
3. Herramienta TDD, salidas y SHA-256 (tarea 2).
4. Seccion del memo (tarea 3).
5. Prosa de la tesis (tarea 4).
6. Trazabilidad y verificaciones (tarea 5).
   Rollback: `git revert` del commit; todo es aditivo y no toca valores canonicos.

## Open Questions

- **OQ1 (autores, no bloquea el apply de B/C/D)**: confirmar el periodo del universo a muestrear (para
  el protocolo) y la definicion operacional de complejidad. No cambia los specs ni la herramienta.
- **OQ2 (externo, bloquea la ejecucion de la campana)**: la organizacion proveera el registro del
  periodo y el consentimiento. Si no, el diseno queda `condicional` y no se ejecuta nada.
