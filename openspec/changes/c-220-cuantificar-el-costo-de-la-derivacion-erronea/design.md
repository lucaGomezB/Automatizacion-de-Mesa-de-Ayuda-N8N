## Context

Ver `proposal.md` — Why. El estado actual que condiciona el diseño:

- `c` vale hoy `10 a 15 min` (`600-900 s`) en `01-introduccion.tex:48`, memo `3.11` y `3.21`, y alimenta `B = (N/3.600)[Δt − (e_aut − e_man)c]` en `08-discusion.tex:80`. Su estado es `condicional` y su procedencia es «estimación propia de los autores, sin registro cuantitativo conservado».
- `intervenciones.csv` conserva `intervencion_inicio_en`, `validado_en` y `duracion_s` por caso: 147 filas, 138 con duración (cobertura `138/147 = 0,9388`), 25 con `cambio_sector=true`, 122 con `false`.
- `brazo_manual.csv` conserva 220 decisiones de sector (`inicio` y `timestamp`), 110 por operador (`O1`, `O2`), con la tarea declarada `brazo_manual`.
- La disciplina del memo exige, por valor, archivo y línea de origen más un estado en `{vigente, condicional, retirado}`. Los análisis de campaña son scripts de solo lectura, biblioteca estándar, semilla fija y salidas idénticas byte a byte (`analisis_calibracion_gate_c214.py`, `analisis_ruido_referencia_c216.py`).
- El balance neto arrastra dos supuestos que este change debe respetar o declarar: «cada derivación errónea cuesta `c` en ambos flujos» y «el flujo automatizado no agrega tiempo de revisión».

## Goals / Non-Goals

**Goals:**

- Convertir `c` en una magnitud con definición operacional, componentes medidos, cota anclada e intervalo, reproducible offline.
- Dejar la justificación del 85 % con un ancla numérica verificable, sin mover el umbral.
- No alterar ningún valor vigente del memo ni el veredicto del balance neto sin decisión explícita del dueño.

**Non-Goals:**

- Recolectar datos nuevos de campo (cronometraje de reasignaciones con operadores) — ver D1.
- Recalcular `B` o `a*` en `08`, `09`, `10`, `12` o `00-resumen`.
- Cambiar el umbral de 85 %, las categorías, `Δt`, `e_aut` ni `e_man`.
- Tocar `App/`, `n8n/` o el clasificador.
- Editar `CHANGES.md` (lo hace el orquestador).

## Decisions

### D1 — Descomposición medida + ancla, en lugar de literatura sola o medición nueva

**Elegido.** Análisis secundario offline de artefactos ya versionados, más una cota anclada para el único tramo que los datos no cubren. Alternativas descartadas:

- *Solo ancla bibliográfica*: no responde «¿y en esta organización?», que es exactamente lo que el dictamen objeta. La literatura de mesas de ayuda no reporta tiempo-persona de reasignación en un formato trasladable.
- *Medición controlada nueva* (`2` operadores × `40` casos con cronómetro, protocolo del brazo manual): es la medición más limpia del tramo aguas abajo, pero exige convocar operadores, instrumentar una sesión y registrar sujetos. No es offline y no se puede ejecutar dentro de este change. Queda como contingencia (D5, rama B).

**Consecuencia:** el change entrega una cifra con procedencia y declara con precisión qué tramo midió y cuál acotó. Eso es más defendible que una estimación sin registro y más honesto que una medición de campo apurada.

### D2 — `c` es tiempo-persona, y se separa del tiempo calendario

El balance neto opera en horas-persona por trimestre. `c` se define como **tiempo-persona adicional que una derivación errónea consume respecto de una correcta**, no como tiempo transcurrido hasta que el caso llega al sector correcto. Se distinguen dos regímenes, porque el flujo observado los produce ambos:

| Régimen | Cuándo ocurre | Componentes | Medición |
|---|---|---|---|
| **Corto** | el error se detecta y corrige en la compuerta de revisión | corrección en la compuerta | medida (`duracion_s`, `cambio_sector=true`) |
| **Largo** | el error escapa y el sector receptor lo rediagnostica y lo devuelve | rediagnóstico + reasignación + reanudación de la tarea interrumpida | rediagnóstico medido (proxy), reasignación y reanudación acotadas |

El texto actual no distingue los regímenes y por eso el `10 a 15 min` no es contrastable: mezcla tiempo-persona con tiempo calendario (cola y espera). La definición operacional se escribe en `04-marco-metodologico.tex` y en el memo.

**Alternativa descartada:** un único `c` agregado sin regímenes. Obliga a promediar cantidades heterogéneas y hace imposible declarar qué mide.

### D3 — Estimadores y sensibilidad al operador

- Grupos por `cambio_sector`, con `n`, media, mediana, desvío e IC bootstrap percentil al 95 % (`B = 2000`, semilla `20261021`, coherente con el resto de los análisis de campaña).
- Diferencia de medias entre grupos con IC bootstrap independiente. Es el estimador del **costo incremental** de corregir en la compuerta.
- Proxy de rediagnóstico: mediana del tiempo de decisión del brazo manual (`brazo_manual.csv`). Se informa **por operador** además del agrupado: `O1` y `O2` difieren casi cuatro veces (`≈18 s` vs `≈73 s`). No se elige el más conveniente: se reporta el agrupado como estimación y el operador lento como cota superior de sensibilidad. La dispersión entre operadores es, en sí misma, un hallazgo que acota la precisión del proxy.
- Media y mediana se informan juntas porque la media está traccionada por colas (`máx. 336 s` en el grupo sin cambio, `máx. 212 s` en el grupo con cambio).

**Valores esperados, a confirmar por el análisis** (calculados en la investigación previa, solo lectura):

| Cantidad | `n` | Media | Mediana | IC 95 % |
|---|---|---|---|---|
| Intervenciones con `cambio_sector=true` | 24 | 41,90 s | 18,95 s | media `[22,75; 65,61]`; mediana `[12,70; 32,02]` |
| Intervenciones con `cambio_sector=false` | 114 | 17,89 s | 8,94 s | — |
| Diferencia de medias | — | 24,01 s | — | `[4,19; 49,61]` |
| Decisión de sector, brazo manual | 220 | 48,36 s | 45,50 s | mediana `[30,00; 56,50]` |
| Decisión de sector, `O1` / `O2` | 110 / 110 | 20,10 / 76,62 s | 18,00 / 73,00 s | — |
| Término de revisión (todas las intervenciones) | 138 | 22,06 s | 9,96 s | — |

Si el análisis no reproduce estas cifras, el memo registra las del análisis y estas se retiran del diseño en la misma tarea.

### D4 — El tramo anclado: una cota declarada, no un parámetro calibrado

El tramo de reanudación tras la interrupción no se mide en este corpus. Se incorpora con **una sola** fuente primaria de la literatura sobre costo de interrupción, verificada contra el texto completo (no contra el resumen) y con la población y la tarea del estudio declaradas. Reglas de uso:

1. Se usa **solo** en el régimen largo; en el corto no hay interrupción de un técnico en curso.
2. Se reporta como **cota superior**, no como estimación puntual. No se aplica ninguna fracción arbitraria para «calzar» la banda canónica: si el ancla completa no encaja, se informa la exclusión.
3. Si la fuente no se puede verificar contra el texto completo, el tramo se declara `no medido` con cota `no disponible` y `c` queda con dos tramos, sin ancla. El change no se bloquea: la sección del memo registra la ausencia.
4. El ancla se suma en el escenario de sensibilidad **alto**, en paralelo a un escenario **bajo** que usa solo los componentes medidos. No se promedian.

### D5 — Compuerta de decisión sobre la banda canónica

El análisis compara el intervalo compuesto con `[600; 900] s` y aplica esta regla, escrita de antemano:

- **Rama A — el intervalo intersecta `[600; 900]`:** el memo conserva `c = 10 a 15 min` como valor canónico, cambia su procedencia de «estimación propia» a «componentes medidos + cota anclada» y `01:48` cita la nueva procedencia. `08` no se toca.
- **Rama B — el intervalo excluye `[600; 900]`:** el memo registra el hallazgo (el valor previo no es tiempo-persona activo) y remite a una **decisión del dueño**. El change NO recalcula `B` ni `a*` ni edita `08`, `09`, `10`, `12` ni `00-resumen`. `01:48` y `04` informan la cifra medida y su alcance, sin afirmar que el balance neto cambie. La decisión del dueño elige entre (i) recalcular el balance con el `c` medido en un change sucesor, (ii) mantener `10 a 15 min` rotulado explícitamente como **tiempo calendario agregado** y no como tiempo-persona, o (iii) ejecutar la medición controlada de D1 para fijar el tramo largo.

**Por qué esta compuerta:** el `c` medido activo es un orden de magnitud menor que la banda. Cualquier composición honesta lo va a mostrar. La compuerta evita dos errores: forzar un ancla para que el número «cierre» (mala ciencia) y arrastrar sin aviso un cambio de veredicto en el balance neto a capítulos que el change no puede tocar.

### D6 — Justificación del 85 %: paridad medida + costo marginal, no una sola frase

El umbral no se mueve. La justificación numérica se reescribe en `01:48` con dos anclas verificables:

1. **Paridad con el error manual.** `1 − e_man` con `e_man = 0,1722` (26/151, contra el consenso de `E1`/`E2`, memo `3.14`/`3.21`) da `82,78 %`. El umbral de `85 %` es, por lo tanto, **más exigente** que la paridad con la tasa de error manual medida. La referencia previa del `15 %` (paridad `85 %`) se conserva como aproximación y se declara superada por la medición. Sensibilidad: con `e_man = 0,35` (contra el etiquetado original) la paridad es `65 %` y el umbral queda todavía más exigente; se informa como complemento, no como lectura principal.
2. **Costo marginal por punto de exactitud.** Con el `c` medido, cada punto porcentual de exactitud perdido agrega `N × 0,01 × c / 3600` horas-persona por trimestre. La fórmula y el valor se registran en el memo; la prosa de `01` los usa para sostener la dirección («por debajo de la paridad el flujo automatizado es peor en las dos dimensiones: más error y más costo de corrección»), no para fijar el número.

**Alternativa descartada:** derivar el 85 % de `a* = 1 − e_man − Δt/c`. Con `e_man = 0,1722` y `c > 0` el resultado es **menor** que `82,78 %` en todos los escenarios, de modo que no puede producir `85 %`. Usar `a*` como fundamento del umbral sería un error aritmético; se documenta explícitamente para que nadie lo intente.

### D7 — Frontera con el tiempo de revisión ya contabilizado

Hallazgo de la investigación previa: el flujo automatizado **sí** agrega tiempo de revisión (`22,06 s` de media sobre 138 casos; `53,07 %` de la proporción de tiempo del proceso), y el supuesto del balance neto dice lo contrario. Para no contar dos veces la misma corrección, el memo:

- declara `c_corto` como el tiempo de la intervención que corrige, que **ya** integra la proporción de tiempo de `07-resultados.tex:163`;
- calcula, como sensibilidad **separada y aditiva**, el término de revisión `r` y su efecto sobre `B`, sin incorporarlo a `B` ni reescribir `08`.

No se corrige el balance neto en este change: se acota el hallazgo y se deja la decisión al dueño junto con D5.

### D8 — Colocación y forma de la prosa

- `01-introduccion.tex:48`: se reemplaza **solo** la oración de procedencia del segundo criterio. Se conservan los tres criterios convergentes, la estructura del párrafo y el umbral. Sin cifras nuevas fuera de las del memo.
- `04-marco-metodologico.tex`: definición operacional de `c` y método, dentro de `subsec:operacionalizacion-variables` y `subsec:metricas-instrumentos`. Se agrega una fila o una llamada en `tab:variables` si el ancho lo permite; si no, un párrafo.
- El memo es la fuente de verdad numérica; la tesis cita la cifra con su alcance y no reproduce la tabla completa.
- `dictamen-correcciones.md`: entrada nueva con «Qué cambió», «Resultados de los cálculos», «Decisiones y pendientes» y matriz de trazabilidad, en el formato de `c-216`/`c-217`.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| El `c` medido (~`40 s` activo) contradice la banda y erosiona el argumento del umbral | D6 separa la justificación del umbral (paridad medida) del costo; el costo deja de ser la única ancla |
| El proxy de rediagnóstico es la decisión de sector, no la reasignación completa | Se declara como proxy con cota inferior; el tramo faltante se nombra y se acota, no se imputa |
| La diferencia entre `O1` y `O2` (≈4×) hace inestable el proxy | Se reporta por operador y se usa el lento como sensibilidad; la dispersión se declara como límite |
| El ancla de interrupción proviene de otro dominio | D4 exige verificación contra el texto completo, uso solo en régimen largo y reporte como cota superior |
| La rama B deja el balance neto sin recalcular y un lector lo note | El memo y la entrada del dictamen lo declaran como pendiente explícito con decisión del dueño, no como omisión |
| Colisión del número de sección del memo con c-218/c-219 | Se asigna al aplicar releyendo el índice; el change tolera cualquier número libre |

## Migration Plan

1. Escribir el test y el análisis; correrlo y congelar las salidas con su SHA-256.
2. Escribir la sección del memo y verificar que las secciones previas no cambian (`git diff` acotado a líneas agregadas).
3. Editar `01` y `04`; recompilar si el dueño lo pide (el change no compila).
4. Registrar la entrada del dictamen y correr la matriz de trazabilidad.
5. Reversión: `git revert` del commit. Sin migraciones de datos ni de esquema; el análisis es aditivo.

## Open Questions

- Número definitivo de la sección del memo (`3.29` esperado; el libre al momento de aplicar). No cambia specs, enfoque ni tareas.
- Si el dueño prefiere que la cifra medida se reporte también en `07-resultados.tex` como resultado y no solo en `01`/`04`. Es una decisión de alcance editorial, no de diseño; se resuelve antes de aplicar sin alterar las tareas centrales.