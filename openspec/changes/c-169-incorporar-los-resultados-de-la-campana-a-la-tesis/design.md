# Design: Incorporar los resultados de la campaña a la tesis

## Context

La tesis declara hoy como no medidos, no contrastados o no computables los cinco ítems
(a)-(e) definidos en `proposal.md`. El programa c-165 a c-168 instrumenta y analiza
una campaña de medición nueva, con sujetos independientes, que corre fuera del
repositorio y deja sus tablas y salidas en `evaluation/data/campana/`. Este change
solo propaga esos resultados a `docs/Tesis/v10 (IA)/`, al memo canónico, al registro
de correcciones y a la release. Sigue gateado (tarea 0). Las enmiendas de 2026-10-30
responden a `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md`.

Terminología del change: **campaña 2026-10** = la campaña original (manual
junio-agosto, automatizada septiembre-octubre de 2026) que sostiene los valores
canónicos vigentes; **campaña de medición** = la del programa c-165 a c-168.

## Goals / Non-Goals

**Goals:**
- Cerrar cada ítem (a)-(e) con un estado único, positivo o negativo, propagado a todas
  las secciones y al memo.
- Registrar cada número nuevo en el memo antes de citarlo, con procedencia
  `archivo:línea`, método, SHA-256 y estado.
- Dejar el archive aplicable sin descartar escenarios de la spec principal.

**Non-Goals:**
- Ejecutar la campaña, recalcular métricas o tocar `evaluation/` (c-167).
- Cambiar valores canónicos vigentes o reabrir el contraste principal de tiempos.
- Tocar `docs/Tesis/v9 (IA)/` (congelada).

## Decisions

### D-kappa: dos coeficientes, dos entradas

- El `0,87` de la campaña 2026-10 se conserva como valor histórico, rótulo "casi
  perfecto", sin IC ("tabla primaria no conservada"); en el memo queda con estado
  `vigente (sin IC)`.
- La entrada "no computable" (`numeros-canonicos.md:198-209`) NO se reemplaza por un IC
  del `0,87`: se cierra con la nota "no estimable; superado por la entrada 3.N del
  kappa de la campaña" (con el número real) y se agrega la entrada nueva.
- El kappa nuevo se reporta como "fiabilidad del doble etiquetado de la campaña de
  medición" (`E1` frente a `E2`, `n` casos, etiqueta primaria, cinco clases, no
  ponderado): IC asintótico (Fleiss, Cohen y Everitt, 1969), IC bootstrap percentil
  (`B = 2000`, semilla `20261021`), `p_o`, `p_e`, PABAK y rótulo de Landis y Koch del
  valor puntual, señalando si el IC abarca dos categorías.
- Caso negativo coherente en los tres requisitos (dos en `tesis-document`, uno en
  `tesis-numeros-canonicos`): para el `0,87`, siempre "tabla no recuperable"; para el
  kappa nuevo, "IC no estimable" si c-167 lo declara (`p_e = 1` o remuestras
  degeneradas). La ausencia de `doble_etiquetado.csv` no es una rama del change:
  detiene el gate (0.2). Alternativa descartada: presentar el kappa nuevo como "IC del
  0,87" (lo prohíbe el escenario "Sin intervalo atribuido al 0,87").

### D-condicional: desenlace positivo y negativo por ítem

| Ítem | Positivo | Negativo | Disparador del negativo |
|---|---|---|---|
| (a) exactitud manual | medida (Wilson por operador, bootstrap agregado, McNemar) | "no medida: operadores no independientes" | solape en `registro_sujetos.csv` entre `O1`/`O2` y la referencia |
| (b) intervención | "contrastada: compatible" (LS < 0,15), "contrastada: refutada" (estimación ≥ 0,15) o "contrastada: no concluyente" (estimación < 0,15 ≤ LS) | "no contrastada: registro incompleto" | el export no cubre la corrida |
| (b') proporción del tiempo | IC bootstrap del cociente | "no estimable" | cobertura de inicio y fin < 80 % |
| (c) efecto de orden | "estimado" (con el MDE que informe c-167 para cada análisis) | "limitación residual" | c-167 lo declara no estimable |
| (d) fuera de muestra | "evaluado" | "sin corpus independiente declarado" | falta `predicciones_independiente.json` |
| (e) kappa | "con IC" | "IC no estimable" (kappa nuevo); "tabla no recuperable" (`0,87`) | ver D-kappa |

Cada estado negativo se propaga al resumen, a `01:34`, a 07, a 09 y al memo igual que
el positivo. La hipótesis principal queda "parcialmente confirmada y parcialmente
refutada" en todas las ramas (la clasificación está refutada siempre); el objetivo
general queda "Alcanzado parcialmente" en todas; el objetivo 4 sube a "Alcanzado"
solo con (a) medida y (b) contrastada (en cualquiera de sus tres ramas, porque las tres
miden la proporción).

Precisiones del orquestador tras el informe de c-167 (2026-10-30):

- **Tres ramas contrastadas de (b)**: compatible si el límite superior del IC de
  Wilson es menor que `0,15`; refutada si la estimación puntual es mayor o igual que
  `0,15`; no concluyente si la estimación es menor que `0,15` pero el límite superior
  es mayor o igual. c-167 entrega la estimación y ambos límites. La rama no
  concluyente se propaga igual que las demás (resumen, `01:34`, 07, 09 y memo) y deja
  la hipótesis principal "confirmada en tiempo, refutada en clasificación y no
  concluyente en intervención". La regla de falsación previa de `01:34` ("se falsea si
  su límite superior no queda por debajo de 0,15") se reemplaza por esta regla de tres
  vías al aplicar.
- **MDE por análisis**: el efecto de condición se mide entre grupos independientes
  (casos con `brazo_primero` manual frente a automatizado, según el plan de c-166), no
  de forma pareada; el MDE pareado de la revisión pre-apply no le aplica. El análisis
  de posición puede ser pareado si c-167 lo reporta así. La tesis cita el MDE que
  c-167 informe para cada análisis y el change no fija ningún valor a priori.
- **Exactitud de v9 contra la referencia nueva**: número nuevo de c-167 (brazo
  automatizado del McNemar), con entrada propia en el memo; no reemplaza el `73,5 %`
  ni ningún valor canónico de v9.

### D-alcance y requisitos de la spec principal

- **Renombrados + modificados** (verificado con un archive simulado sobre una copia de
  `openspec/` en el scratchpad: OpenSpec 1.6.0 aplica `RENAMED` y luego el `MODIFIED`
  con el nombre nuevo): "Intervención humana por gate declarada no medida" →
  "Intervención humana reportada según el registro de la campaña de medición";
  "Exactitud del brazo manual declarada no medida y balance neto indeterminado" →
  "Exactitud del brazo manual y balance neto según la campaña de medición".
- **Modificados** (encabezados copiados con `grep -F -x`): kappa (2), estado de la
  hipótesis principal (con tilde, `spec.md:2013`), segunda sub-hipótesis, confundido
  de la rotación, procedencia de los ajustes (restaura "ausencia de exposición al
  corpus" en el MUST NOT y agrega la salvedad del corpus independiente), priorización
  de líneas futuras, correspondencia del párrafo de priorización, subsección de
  corrección de la medición de intervención, línea futura de exactitud manual,
  replicaciones, grados de cumplimiento, párrafo introductorio de resultados,
  viabilidad operativa condicional, analistas etiquetadores, propagación de la
  dependencia etiquetadores-operadores y tabla de configuración del Anexo B.
- **Removido**: "Rotulo de la sub-hipotesis de intervencion humana como no
  contrastada", con Migration a "Declaración del estado de la hipótesis principal" y
  "Segunda sub-hipotesis con fraccion esperada explicita".
- **Preservación de escenarios**: OpenSpec 1.6.0 aborta el archive si un `MODIFIED`
  omite un escenario de la principal ("current spec contains scenario(s) not present
  in the modified block"). Se conservan todos los nombres, aunque algunos queden
  heredados ("Sub-hipótesis de intervención humana declarada no medida", "Valores
  verificados contra ambas revisiones", "Objetivos 1, 3 y 4 parcialmente
  alcanzados"); su contenido se reescribió con las ramas condicionales.
- **Redundancias eliminadas**: "Cifra retirada ausente" vive solo en el requisito
  renombrado de intervención; "Reporte de la validacion fuera de muestra" solo agrega
  el resultado y remite a "Procedencia declarada" para la calificación dentro de la
  muestra.
- **Revisados sin cambio** (compatibles con todas las ramas): "Balance neto entre el
  ahorro de registro y el costo de las derivaciones erroneas" (la grilla 10/15/20/26,5 %
  se conserva; la tasa medida se agrega aparte), "Registro canonico del balance neto y
  sus supuestos", "Hallazgo del gate de clasificacion presentado como resultado
  propio" (sigue siendo un hallazgo de la campaña 2026-10), "Retiro de la afirmacion
  de preservacion del juicio humano", "Sesgo optimista acotado en las limitaciones...",
  "Calificacion dentro de la muestra..." (resumen, abstract y etapa determinística),
  "Estado declarado de las hipotesis subsidiarias", "Presupuesto de palabras del
  resumen en español", "Aprendizaje activo condicionado a la calibracion de la
  confianza" (depende del rótulo `subsec:medicion-intervencion`, que se conserva).

### Rótulos estables

`subsec:medicion-intervencion`, `subsec:corpus-independiente`,
`subsec:reduccion-intervencion` y `subsec:estudios-replicacion` conservan su
`\label` en todas las ramas; solo cambian título y contenido. Así no se rompen las
remisiones exigidas por "Aprendizaje activo condicionado..." ni el orden de
"Correspondencia entre el parrafo de priorizacion...". Alternativa descartada:
retirar las subsecciones saldadas (rompe dos requisitos principales y el índice).

### Tercera configuración en el Anexo B

La campaña de medición corre con c-165 aplicado (instrumentación de intervención), es
decir, con otro código que la configuración evaluada (`d6bb474`) y que la entregada.
`tab:configuracion-evaluada-entregada` agrega la columna "Configuración de la campaña
de medición" (commit consignado en el README de `evaluation/data/campana/`), con la
fila `classifier_version`, que debe coincidir con la evaluada (clasificador
congelado); si no coincide, las métricas de la campaña se rotulan como de otra
configuración del clasificador.

### Denominación distintiva

El cronograma y `fig:cronograma` ya llaman "campañas de medición" a las corridas
manual y automatizada de 2026. La tesis define una sola vez, en 4.2, una denominación
distintiva para la campaña nueva (propuesta: "campaña complementaria de medición") y
la usa en todo el documento.

### Exactitud manual y balance neto

Con (a) medida, la tasa de derivación errónea manual se toma como `1 - exactitud
estricta del brazo manual` (sobre los casos de referencia `E1 = E2`) y `a*` se
recalcula con ella y su intervalo. El costo `c` sigue siendo estimación propia
(10 a 15 min) porque ninguna salida de c-167 cronometra reasignaciones; por eso el
balance queda `condicional` salvo que su intervalo quede de un lado de cero en todo el
rango de costos. El 15 % preliminar permanece rotulado y como fila de la grilla.

### Tiempos de la campaña de medición

Los tiempos manuales de la campaña de medición son insumo del efecto de orden; no
reemplazan `61,6 s` ni `17,76 s` ni rehacen el Wilcoxon principal.

### D-gate

Tarea 0 mecánica y verificable (ver `tasks.md`): archive de c-165 a c-168, presencia
de tablas y salidas con README y SHA-256, registro de sujetos sin solapes y
`pytest evaluation/` verde. La tarea 0 no escribe en `CHANGES.md`. Si 0.1 o 0.2
(salvo el corpus independiente) fallan, el change se detiene; 0.3 no detiene: elige
ramas negativas.

### D-memo

Cada número entra como entrada de una sección `3.N` consecutiva (hoy la siguiente
libre es la 3.14, tras la 3.13 de c-159) con valor, procedencia `archivo:línea` en
`evaluation/data/campana/analisis/`, comando reproducible de solo lectura, método,
SHA-256 de la tabla primaria, fecha, configuración y estado. Los valores canónicos
vigentes no cambian (requisito agregado de invariancia).

### D-release

Grupo 8 de `tasks.md`: PDF sin errores ni referencias rotas, `verify_citations.py`
PASS, `revision_tildes.py --check`, recuento del resumen con la regla de c-106,
nuevo total de páginas declarado (hoy 112 frente a 100, con exceso declarado),
renders con `build_tesis_para_agente.py`, referencias de versión (Anexos A y B, 05,
06, 11 y `Gomez2026_repositorio`), sección en `dictamen-correcciones.md`, release y
commit del hash con el flujo de `ea5e01a`/`756aabe` (`git show --stat`: el primero
actualiza versión, bibliografía, PDF y renders; el segundo consigna el hash en el
Anexo B y `CHANGES.md`), y registro en `CHANGES.md` al archivar.

### Plan de recorte del resumen

Margen actual (regla de c-106): ES 1 palabra, EN 5. Cambios previstos y compensación:

1. `00:13` / `00:29`: sustituir la cláusula "y la de intervención humana queda no
   contrastada por ausencia de registro primario" (11 palabras ES) por el estado de la
   campaña de medición con la tasa y su IC; objetivo: misma longitud o menor.
2. `00:11` / `00:27`: no se agrega el kappa nuevo al resumen (el `0,87` sigue
   exigido por "Presupuesto de palabras del resumen en español"); si se agrega una
   frase de la campaña de medición (exactitud manual), se compensa en el punto 3.
3. Recortes en orden de preferencia: (i) redundancias de `00:9` / `00:25` (p. ej.
   "con FastAPI", "the Gemini 3.6 Flash model" → "Gemini 3.6 Flash"); (ii) la frase
   final del párrafo de viabilidad `00:15` / `00:31` ("Se aporta una arquitectura
   reproducible..."), que puede acortarse sin superar el tope de 34 (ES) y 31 (EN)
   palabras ni aumentar el conteo previo del párrafo, como exige "Viabilidad operativa
   presentada como condicional".
4. Se registra el conteo ANTES/DESPUÉS en `dictamen-correcciones.md`.

### Lista ANTES / DESPUÉS (obligación de propagación)

Los valores entre llaves los fija el memo al aplicar. Reversibilidad común: cada
DESPUÉS se revierte al ANTES si la entrada `3.N` del memo que lo sustenta se retira
(por ejemplo, si se invalida la tabla primaria por su SHA-256).

| Sitio | ANTES (textual, abreviado) | DESPUÉS (según rama) |
|---|---|---|
| `00:11` / `00:27` | "El doble etiquetado independiente alcanzó un Kappa de Cohen de 0,87." | Igual (sin IC); el kappa nuevo no entra al resumen por presupuesto |
| `00:13` / `00:29` | "...y la de intervención humana queda no contrastada por ausencia de registro primario." | "...y en intervención humana resulta {compatible / refutada / no concluyente} ({p} %, IC [{a}; {b}])" o "...queda no contrastada por registro incompleto" |
| `01:34` | "Con la evidencia disponible esta sub-hipótesis no se contrasta... \emph{no contrastada por ausencia de registro primario}..." | Estado de la campaña de medición con tasa e IC, remisión a `subsec:reduccion-intervencion`; o "no contrastada: registro incompleto" |
| `04:14` | "la rotación de operadores queda confundida con el efecto del operador" | Se conserva para la campaña 2026-10 + contrabalanceo de condición de la campaña de medición y denominación distintiva |
| `04:34` (`tab:variables`) | Intervención "Se reporta de dos formas rotuladas..." | Igual + fuente: export de intervenciones (vocabulario de origen) |
| `04:55` | "Los dos analistas son, además, las mismas dos personas que operaron el brazo manual..." | Se conserva para la campaña 2026-10 + `E1`/`E2` y `O1`/`O2` independientes (o solape declarado) |
| `04:67` | "...en la versión evaluada no se midió, por ausencia de registro primario." | "...no se midió en la campaña 2026-10; en la campaña de medición se mide con el export de intervenciones" |
| `04:83` / `04:85` | Rotación confundida; κ = 0,87 y analistas = operadores como limitación | Efecto de orden estimado o limitación residual; `0,87` sin IC + kappa nuevo con IC; dependencia resuelta o declarada |
| `07:6` | "seis apartados" | "siete apartados" (con la subsección nueva) |
| `07:157-161` | Título "Intervención humana en el flujo automatizado"; "se declara no contrastada por ausencia de registro primario... queda como no medido" | Título según estado; tasa con IC y veredicto, o "no contrastada: registro incompleto"; hallazgo del gate 2026-10 conservado |
| `07` (nueva) | — | `subsec:resultados-campana-medicion` con (a), (c), (d), (e) |
| `08:20` | "No se dispuso de un corpus independiente de preproducción." | Se conserva para 2026-10 + resultado fuera de muestra o "sin corpus independiente declarado" |
| `08:22` | "...se descartaría con un diseño contrabalanceado." | Efecto de orden estimado (con el MDE de c-167 por análisis; condición entre grupos independientes) o limitación residual |
| `08:42` | "ocho limitaciones" | Cardinal real tras la reescritura |
| `08:54` ("Sexto") | Analistas = operadores, impide medir sin sesgo la exactitud manual | Limitación de la campaña 2026-10, resuelta por la campaña de medición o declarada |
| `08:58` ("Octavo") | "la proporción de intervención humana no se midió y la segunda sub-hipótesis queda no contrastada" | Se retira si (b) contrastada (y cambia el cardinal); se reescribe como "registro incompleto" si no |
| `08:97` | "La exactitud del brazo manual no se midió... El balance neto es... indeterminado" | `a*` con tasa manual medida y balance condicional al costo; o "no medida: operadores no independientes" |
| `09:6` | "---sin medir la intervención humana---"; "queda no contrastada en intervención humana por ausencia de registro primario" | Estado de la campaña de medición |
| `09:22`, `09:26` | "intervención humana no medida" | Estado de (b); fila 4 según (a) y (b) |
| `09:41` | "La comparación no cubre la exactitud del brazo manual ni la intervención humana por caso, no contrastada..." | Exactitud manual y McNemar frente a la exactitud de v9 contra la referencia nueva, o rama negativa |
| `10:6` | Prioritarias: gate, clasificador y corrección de la medición de intervención | Tercera línea prioritaria solo si (b) "registro incompleto" |
| `10:16-18` | "Corrección de la medición de intervención humana"; "quedó no contrastada" | Retitulada y reclasificada si (b) contrastada; protocolo conservado si no |
| `10:42-44` | "Esa validación no se realizó en este trabajo..." | Retitulada (replicación en corpus adicionales) si (d) evaluada; conservada si no |
| `10:48` | "Toda replicación debería medir además la exactitud del flujo manual..." | Declarada realizada en la campaña de medición si (a) medida; cronometraje de reasignaciones pendiente |
| `11:32` | "los dos operadores se cronometraron mutuamente..." | Agrega los sujetos de la campaña de medición (alias, consentimiento, seudonimización) |
| `12:38` (Anexo B) | Dos columnas (evaluada `d6bb474`, entregada `v1.2.7`) | Tres columnas (+ campaña de medición) y fila `classifier_version` |
| `12:14`, `12:23`, cronograma | Construcción, campañas 2026 y versión del modelo | + barra de la campaña de medición |
| memo `:198-209` | "IC del coeficiente kappa — no computable." | Cerrada con nota "no estimable; superado por la entrada 3.N..." |

## Lo que NO cambia

- Valores canónicos vigentes de la campaña 2026-10: `61,6 s`, `17,76 s`, `W = 363`,
  `r = 0,9639`, `73,5 %`, `0,6508`, `0,5207`, kappa `0,87`; también el `9,5 %` sigue
  `retirado`.
- Las cinco cadenas canónicas de sectores.
- `docs/Tesis/v9 (IA)/` (congelada), `evaluation/report.md`, `evaluation/predicciones.json`.
- Los enunciados de objetivos e hipótesis (solo cambian estados y grados).

## Risks / Trade-offs

- [Rama no prevista por c-167] → toda salida que no encaje en D-condicional detiene la
  tarea afectada y se registra como decisión no resoluble en el memo.
- [Escenarios heredados con nombres antiguos] → aceptado: OpenSpec no permite
  descartarlos; su contenido es condicional.
- [Resumen sobre el tope] → plan de recorte; si no alcanza, se prioriza la cláusula de
  estado de (b) y se omite toda cifra nueva distinta de la tasa.
- [Más páginas] → sustitución de declaraciones retiradas; nuevo total declarado.

## Migration Plan

Orden de aplicación: (0) gate; (1) memo; (2) marco metodológico; (3) resultados;
(4) discusión y conclusiones; (5) recomendaciones; (6) introducción y resumen; (7)
anexos, cronograma, legal y bibliografía; (8) registro y release; (9) cierre y
verificación. Rollback: revertir los commits del change; sin migraciones.

## Open Questions

- Denominación definitiva de la campaña nueva en la tesis (propuesta: "campaña
  complementaria de medición"); decisión de los autores al aplicar.
- Si la exactitud de v9 contra la referencia nueva difiere mucho del `73,5 %`, la
  discusión debe tratar la diferencia de referencias; el alcance de ese párrafo se
  decide al aplicar.
