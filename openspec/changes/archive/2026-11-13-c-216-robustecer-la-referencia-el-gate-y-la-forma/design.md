## Context

El change parte del estado de la release v1.3.0 tal como lo midió el dictamen CONEAU del
2026-11-13 (ver `proposal.md` para el motivo). Los insumos ya existen y están versionados:

- **Referencia arbitrada**: `evaluation/data/campana/corpus_independiente_arbitrado.json`
  (`206` casos), `predicciones_arbitrado.json` (`hybrid-v3` congelado, `142/206` estrictos,
  macro-F1 `0,7024`), `doble_etiquetado_arbitrado.csv` (`476` filas: `E3` y `E4` sobre los
  `206`, `E5` sobre los `64` discordantes) y `arbitraje_tres_vias.json` (`64` arbitrados, `6`
  de tres vías).
- **Acuerdo inter-etiquetador**: `p_o = 0,6867` (`103/150`), kappa `0,6055`
  (`[0,5186; 0,6924]` asintótico; `[0,5175; 0,6839]` bootstrap), memo 3.21.
- **Calibración de la confianza**: AUROC de Gemini `0,5168` `[0,3796; 0,6528]` dentro de la
  muestra; ningún umbral alcanza el piso (memo 3.24, c-214).
- **Intervención humana**: `147` intervenciones (`66` correo + `81` telefonía), `25` cambios
  de derivación (`17,0 %`), regla del reportante no identificado (memo 3.14/3.17).
- **Consentimiento**: `docs/campana-medicion/confirmacion-posterior-consentimiento.md` con
  `E3`/`E4`/`E5` informados el `2026-11-12` y firmantes el `2026-11-13`;
  `11-aspectos-legales.tex:40` ya lo declara; `dictamen-correcciones.md` registra R4 como
  resuelto.
- **Forma**: el PDF de la release ronda las `145` páginas (tope declarado de `100`, exceso
  honrado); `sent_c197.py` informa `3` oraciones de más de `60` palabras en el capítulo 11 y
  hay párrafos de hasta `2441` caracteres.

## Goals / Non-Goals

**Goals:**

- Producir una medición de sensibilidad, offline y reproducible, del error del clasificador
  frente a referencias alternativas plausibles, calibrada al acuerdo observado, sin cambiar
  ningún número canónico.
- Corregir la lectura del human-in-the-loop sin ocultar el hallazgo negativo de la señal de
  confianza.
- Verificar y cerrar R4, y dejar la forma del capítulo 11 y la repetición de cifras dentro de
  límites verificables.

**Non-Goals:**

- No reclasificar el corpus, no reentrenar, no cambiar el prompt ni la configuración.
- No ejecutar trabajo de campo ni una corrida paga sin autorización escrita del dueño.
- No resolver las demás amenazas del criterio 4 (ajuste y evaluación sobre el mismo corpus,
  instrumentos asimétricos, orden fijo de los brazos): el análisis de ruido solo ataca la
  fragilidad de la referencia.
- No reconciliar en este change el requisito histórico de `tesis-dictamen-v1-3-0` que declara
  el arbitraje diferido; c-206 ya cambió el texto y su propia spec.

## Decisions

### D1 — Método primario: simulación de etiquetas calibrada al kappa

Se elige una **simulación Monte Carlo de referencias alternativas** calibrada al acuerdo
observado, y no un modelo latente de clases (Dawid-Skene). Con `206` casos, `5` clases y tres
etiquetadores (uno de ellos solo en `64` casos), un modelo latente tiene celdas con soporte
insuficiente y su resultado sería opaco para el tribunal. La simulación es transparente,
reproducible y se puede auditar con las etiquetas recolectadas.

**Procedimiento (fijado en el docstring antes de correr):**

1. **Kernel de ruido `Q`.** Construir una matriz `5x5` fila-estocástica contra la referencia
   arbitrada, con las etiquetas de `E3` y `E4` (todo el corpus) y `E5` (los `64` arbitrados),
   ponderando cada etiquetador por la cantidad de casos que etiquetó. Aplicar suavizado de
   Laplace `0,5` por fila y declarar el soporte de cada fila. `Q[c, c']` es la probabilidad
   empírica de que un etiquetador independiente asigne `c'` cuando la referencia es `c`.
2. **Calibración de la intensidad `λ`.** Definir la mezcla convexa
   `Q_λ = (1 − λ)·Q + λ·m`, donde `m` es la distribución marginal empírica de clases repetida
   por fila. En `λ = 0` la concordancia es la del kernel empírico (superior al kappa observado);
   en `λ = 1` la etiqueta simulada es independiente de la referencia (kappa `≈ 0`). Buscar por
   bisección el `λ*` tal que una etiqueta simulada con `Q_{λ*}` reproduzca `0,6055` con
   tolerancia `±0,005`; informar también el `p_o` resultante contra `0,6867` como chequeo. La
   mezcla con la marginal (y no con la identidad) garantiza que el kappa decrezca de forma
   monótona y que siempre exista solución en `[0, 1]`. El `λ*` es una **intensidad de ruido
   consistente con el acuerdo medido**, no una estimación de la verdad.
3. **Réplicas.** Para `B = 2000` réplicas con semilla `20261021`, generar una referencia
   alternativa `R*` por caso con `R* ~ Q_{λ*}(R, ·)` y recalcular exactitud estricta y
   macro-F1 con las predicciones fijas. Informar mediana, percentiles `2,5`/`97,5`, proporción
   de réplicas con exactitud `≥ 0,6893` y la distribución completa en el JSON.
4. **Descomposición.** Con `64` errores observados, informar el intervalo de errores bajo
   referencias alternativas (`[q2,5; q97,5]`) y separar: (i) **error robusto**, el que persiste
   en el extremo más favorable de la simulación (cota inferior de errores); y (ii) **error
   atribuible a la referencia**, la diferencia entre el error observado y ese extremo. Rotular
   la separación como sensibilidad, no como causalidad ni como verdad latente.

Alternativas descartadas: (a) modelo latente de clases, por soporte y opacidad; (b) solo cotas,
porque no cuantifican la plausibilidad; (c) solo simulación, porque no da una cota
distribution-free. Se usan simulación (primaria) y cotas (secundaria).

### D2 — Método secundario: cotas distribution-free

Con `δ` = cota superior de Wilson al 95 % de la probabilidad media de etiqueta alternativa
(fuera de la diagonal de `Q_{λ*}`) y `m = round(δ·206)`, informar las cotas
`[max(0, (142 − m)/206), min(1, (142 + m)/206)]`. Son cotas válidas bajo el supuesto "a lo sumo
`m` etiquetas de referencia son erróneas"; se declaran como sensibilidad y no como medición.
Esta parte no depende de la calibración por kappa y sirve de contraste.

### D3 — Casos de tres vías

Listar los `6` casos con `tres_vias = true`, sus etiquetas `E3`/`E4`/`E5`, la referencia usada y
el rango de exactitud si se asigna cada una de las tres etiquetas (cada caso mueve como máximo
`1/206`). No se elige una etiqueta "verdadera": el rango es el resultado.

### D4 — Artefacto, determinismo y registro

Script nuevo `evaluation/data/campana/analisis/analisis_ruido_referencia_c216.py`, de solo
lectura, reutilizando `evaluation/metrics.py` (`intervalo_wilson`, `resumen_exactitud`) y
`evaluation/kappa.py` (`kappa_cohen`); sin red ni Gemini. Salidas
`analisis_ruido_referencia_c216.json`, `.md` y `.SHA256SUMS.txt` en la misma carpeta, UTF-8 sin
BOM y LF. Dos corridas idénticas byte a byte; el script imprime los SHA-256. Antes de simular,
aborta si no reproduce `142/206` y `0,7024`. La sección 3.27 del memo canónico registra cada
cifra con fuente y comando y declara el carácter aditivo. Pruebas unitarias de las funciones
puras (kernel, calibración, cotas, rango de tres vías) con casos sintéticos, incluida la
reproducción del kappa.

### D5 — Ubicación en la tesis y presupuesto de páginas

- `04-marco-metodologico.tex`: párrafo de método (simulación calibrada, `B`, semilla, cotas)
  junto al protocolo fuera de muestra; sin duplicar la teoría de kappa que ya está en el marco
  teórico.
- `07-resultados.tex`: subsección `subsec:ruido-referencia` después de
  `subsec:resultados-campana-medicion`, con una tabla compacta (observado, mediana, `q2,5`,
  `q97,5`, `δ`, cotas y rango de tres vías) y dos párrafos de lectura.
- `08-discusion.tex`: un párrafo en limitaciones que lee el resultado como sensibilidad y
  declara que no elimina las demás amenazas.
- **Presupuesto**: crecimiento neto `≤ 2` páginas. L5 debe recuperar al menos `0,5` página; el
  delta se registra en el libro mayor de `dictamen-correcciones.md`.

### D6 — Reencuadre del human-in-the-loop

La afirmación vigente que equipara "la revisión humana no actuó" con "la señal de confianza no
discriminó" se reemplaza por dos afirmaciones separadas:

1. **El human-in-the-loop actuó**, por la regla del reportante no identificado: `147`
   intervenciones (`66` correo, `81` telefonía), `25` cambios de derivación (`17,0 %; [11,8 %;
   23,9 %]`). Es una medición operativa de la campaña complementaria, no una re-clasificación.
2. **La señal de confianza no discriminó**: AUROC `0,5168` `[0,3796; 0,6528]` dentro de la
   muestra; ningún umbral alcanzó el piso; el gate de `0,70` no derivó casos en el corpus. El
   hallazgo negativo se conserva íntegro.

Se distingue la configuración **evaluada** (clasificador congelado `hybrid-v3`) de la
**entregada** (regla del reportante vigente desde el 2026-10-13, posterior a la campaña
2026-10). Se editan `07`, `08`, `09`, `10` y la frase de supervisión de `11`; no se agregan
cifras nuevas ni se cambia el veredicto de la segunda sub-hipótesis.

### D7 — Corrida de la configuración entregada: decisión del dueño

| Opción | Qué aporta | Costo / riesgo | Recomendación |
|---|---|---|---|
| **A. No ejecutar (por defecto)** | Honestidad: se declara que la configuración entregada no se midió; se conserva la limitación "lo evaluado no es lo entregado" | Ninguno; el criterio 5 mantiene ese descuento | **Recomendada** si no hay autorización explícita |
| **B. Corrida paga pequeña** | Mediría la configuración entregada (clasificación + regla del reportante) y respondería al descuento de "lo evaluado no es lo entregado" | Llamadas a Gemini sobre el corpus (máximo ~`206`, escalados ~`90`), una versión nueva del clasificador y una comparación no directamente equivalente con `hybrid-v3`; riesgo de un resultado que no mejore | Solo con autorización escrita del dueño; se rotula como configuración separada, no como reemplazo de `0,6893` |

La corrida, si se autoriza, usa `evaluation/run_evaluation.py` con `--confirm-paid` y un cache
nuevo; no se escribe sobre los artefactos congelados. Sin autorización, el texto declara la
configuración entregada como no medida. **Esta es la única decisión de dueño que bloquea una
tarea (4.2).**

### D8 — Verificación de R4 (no reescritura)

Checklist de verificación, en este orden:

1. `confirmacion-posterior-consentimiento.md`: filas `E3`, `E4`, `E5` con información verbal
   `2026-11-12` y confirmación `2026-11-13`, sin identidad.
2. `11-aspectos-legales.tex:40`: menciona a los tres y las mismas fechas; no dice "pendiente".
3. `registro_sujetos.csv`: `11` filas, `E3`/`E4`/`E5` con `rol = etiquetador`, sin datos
   personales.
4. `evaluation/data/campana/README.md`: dice "8 filas"; se corrige a `11` y se listan los roles
   nuevos (sin identidad).
5. `dictamen-correcciones.md`: R4 figura resuelto; se agrega la fila de verificación de c-216.
6. Si algo no coincide, se corrige el documento (no la afirmación); el capítulo legal no se
   reescribe más allá de la consistencia.

La edición del capítulo legal y del registro es de gobernanza **HIGH** por tratarse de
afirmaciones sobre consentimiento: el apply debe mostrar el diff al dueño antes de escribir.

### D9 — Reducción de repetición y oraciones largas

- **Repetición**: en prosa, `0,8447` con `n = 103` y `0,6893` con `n = 206` aparecen como
  máximo una vez fuera de `07-resultados.tex`; el resto se reemplaza por
  `\autoref{tab:fuera-de-muestra}` o `\autoref{subsec:resultados-campana-medicion}`. Las tablas
  quedan exentas. Se usa un conteo con `rg` antes y después; el objetivo es bajar de `6`
  apariciones en `07`, `3` en `08` y `2` en `09` a una por capítulo en prosa.
- **Oraciones y párrafos**: `11-aspectos-legales.tex` debe dar `0` oraciones `> 60` palabras con
  `sent_c197.py` y ningún párrafo `> 2000` caracteres. Se parten, en este orden, los párrafos
  de las líneas 14 (`2441` caracteres), 42 (`1907`), 10 (`1756`), 38 (`1527`) y 18 (`1404`), y
  las oraciones de las líneas 28 y 42. No se tocan tablas ni se cambian cifras, citas o
  salvedades. El registro enumera cada corte con su ubicación previa.

### D10 — Gobernanza y verificación de cierre

- L2 (análisis + memo) y L5 (redacción): **MEDIUM**; L3 (prosa de resultados/discusión) es
  **MEDIUM** con revisión del dueño del veredicto; L4 (consentimiento/legal): **HIGH**, con diff
  revisado antes de escribir.
- Cierre: `pytest` del script nuevo, `sent_c197.py`, conteo de repeticiones, compilación Docker
  `texlive-thesis`, `verify_citations.py`, `pdfinfo` y registro en el libro mayor.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| La simulación se lee como verdad latente o como "accuracy corregida" | Rotular como sensibilidad; informar cotas y supuestos; no publicar un punto único |
| Celdas chicas del kernel (`Bases de Datos` `n = 16`, `Sistemas` `n = 61`) | Suavizado de Laplace `0,5`; informar soporte por fila; la calibración global es la que manda |
| El resultado es incómodo (la exactitud puede subir bajo ruido) | Se informan todos los escenarios; el método se fija en el docstring antes de correr y se declara que el prerregistro no fue ciego |
| El reencuadre se percibe como defensa interesada | Se conserva el AUROC `0,5168` y el veredicto negativo; solo se separan las dos señales |
| La corrida paga se ejecuta sin autorización | Tarea bloqueada; por defecto se declara la limitación |
| Las ediciones del capítulo legal alteran el significado | Diff revisado por el dueño; solo se parten oraciones y párrafos; checklist de citas y salvedades |
| Crecimiento de páginas | Tope neto `≤ 2`; L5 compensa; libro mayor |

## Migration Plan

1. Fijar el método en el docstring y escribir las pruebas del script (TDD) antes de correr.
2. Implementar y correr el análisis; verificar anclajes y determinismo; registrar SHA-256.
3. Agregar la sección 3.27 al memo canónico.
4. Escribir el método en el capítulo 4 y la subsección en el 7; leer en el 8.
5. Aplicar el reencuadre L3 en 07/08/09/10/11 (con revisión del dueño para el 11).
6. Verificar R4 y corregir el conteo del README de campaña.
7. Aplicar L5 (repetición y cortes) y registrar cada corte.
8. Compilar, verificar citas, conteo de oraciones, repeticiones y páginas; actualizar el libro
   mayor y la trazabilidad.

**Rollback**: `git revert` de los `.tex`, del script, de los artefactos nuevos y de la sección
del memo. No hay migración de datos ni cambio de configuración; los corpus y valores canónicos
quedan intactos.

## Open Questions

- **OQ1 (dueño, bloquea 4.2)**: ¿se autoriza la corrida paga de la configuración entregada?
  Por defecto **no**; sin autorización se aplica la rama de limitación declarada. La decisión
  solo cambia si la tarea 4.2 se ejecuta o se cierra como limitación; no cambia las specs.
- **OQ2 (dueño)**: ¿se confirma que el registro de fechas sin identidad de
  `confirmacion-posterior-consentimiento.md` es el registro canónico de R4 y que no hace falta
  ninguna firma nueva? Si el dueño aporta una firma posterior, se actualiza la fecha y se
  re-verifica la consistencia; no se reescribe el capítulo legal.