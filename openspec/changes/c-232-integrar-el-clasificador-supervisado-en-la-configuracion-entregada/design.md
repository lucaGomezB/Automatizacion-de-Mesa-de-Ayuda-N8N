# Design: Integrar el clasificador supervisado en la configuracion entregada

## Context

Ver `proposal.md` — Why para la motivacion. Estado y restricciones que moldean el enfoque:

- El clasificador vigente es el **hibrido** (filtro deterministico -> Gemini) detras de la
  abstraccion de `c-227`: `App/Backend/app/classifiers/provider.py`
  (`InferenceProvider` + registro + `PROVEEDOR_POR_DEFECTO = "gemini"`),
  `App/Backend/app/classifiers/base.py` (`BaseClassifier`), `hybrid.py`,
  y `inference_provider`/`inference_model` en `Settings`. El default es neutral: reproduce
  caso por caso las predicciones vigentes.
- `c-228` entrega el benchmark (mejor modelo entre BERT-class y modelos abiertos), el
  corpus/particiones congelados y los criterios fijados de antemano; **no toca produccion**.
- `c-229` entrega el corpus de prevalencia natural; `c-230`, la referencia por mayoria.
  Los tres estan **propuestos y sin aplicar**: la linea **depende de datos que todavia no existen**.
- Anclajes vigentes inamovibles: `0,6893` (`142/206`), macro-F1 `0,7024`, veredicto del
  umbral `0,85`; el `0,85` **no es alcanzable** sobre los `206`.
- Reutilizables sin modificar: `evaluation/metrics.py`, `evaluation/stats.py`
  (`contraste_mcnemar`, bootstrap), `evaluation/no_solape.py`,
  `evaluation/data/campana/predicciones_arbitrado.json`.

## Goals / Non-Goals

**Goals:**

- Consumir el resultado del benchmark de `c-228` y congelar el modelo seleccionado como
  artefacto versionado y reproducible con procedencia.
- Integrarlo en la configuracion entregada detras del **mismo contrato** del clasificador,
  de forma seleccionable por configuracion y sin romper el hibrido ni las cadenas canonicas.
- Contrastarlo **cabeza a cabeza** contra el hibrido (referencia retenida y corpus de
  prevalencia natural) con IC y prueba pareada.
- Decidir con una **regla pre-registrada** de tres vias y dejar el **registro honesto**,
  incluida la salida «no supera».

**Non-Goals:**

- Re-entrenar, re-benchmarkear o redefinir los criterios de `c-228`.
- Cambiar las cinco cadenas canonicas, el prompt, los parametros de inferencia o el gate.
- Forzar el reemplazo del hibrido o presentar un resultado no medido como mejora.
- Remedir la referencia de `206` o el corpus de `c-229` (solo se consumen).
- Invocar a Gemini en el recomputo (usa predicciones congeladas) o hacer llamadas pagas.

## Decisions

### D1 — Alcance: consumir, congelar, integrar, contrastar y decidir

El change toma **exactamente un** modelo del benchmark de `c-228` (el mejor por los
criterios alli fijados), lo congela, lo integra detras del contrato y decide con una regla
pre-registrada. Si `c-228` no produjo modelo o benchmark, la tarea queda **bloqueada y
registrada**; no se sustituye por un modelo elegido a mano. Alternativa descartada: entrenar
o elegir el modelo dentro de este change, porque duplicaria `c-228` y reabriria sus criterios.

### D2 — Congelado versionado del modelo seleccionado

Artefacto `evaluation/data/modelo_supervisado_c232/` con manifiesto (UTF-8 sin BOM, LF):

| Campo | Contenido |
|---|---|
| `modelo`, `tokenizer` | identificador y version exactos; hash del binario (SHA-256) |
| `codebook_version` | version del codebook de `c-228`/`c-230` usada |
| `split_hash` | SHA-256 del split de entrenamiento (para reproducir) |
| `preprocesamiento` | version del pseudonimizado/normalizacion |
| `comando_evaluacion` | comando reproducible que reproduce el contraste |

Los pesos se versionan como binario o como puntero + hash si exceden el limite del repo. El
modelo es **inmutable**: no se re-entrena ni se ajusta tras ver el contraste. Cumple
`supervised-classifier-integration` (SCI-001).

### D3 — Integracion detras del mismo contrato del clasificador

El modelo se expone como un proveedor/etapa seleccionable a traves de la abstraccion de
`c-227` (registro de proveedores + `Settings`), implementando `BaseClassifier`/adaptador que
respeta el contrato canonico (cinco cadenas, esquema de resultado, gate). El default
**sigue resolviendo al hibrido** y MUST NOT cambiar salvo que la regla de D6 mande
**reemplazar**. El adaptador corre **offline** (pesos locales), sin red y sin llamadas pagas
fuera del gate de confirmacion. Prueba de **neutralidad**: con el default, el sistema
reproduce caso por caso las predicciones del hibrido y ningun numero canonico cambia. Cumple
`supervised-classifier-integration` (SCI-002, SCI-003) y `inference-provider-abstraction`.

### D4 — Contraste pareado cabeza a cabeza

Sobre los **mismos casos**, emparejados por `caso_id`, se calculan por sistema (supervisado
vs hibrido) exactitud estricta y laxa, macro-F1 y P/R/F1 por clase, y la **diferencia pareada**
de la exactitud estricta con IC del 95 % (bootstrap percentil, semilla fija) y McNemar, con
`evaluation/metrics.py` y `evaluation/stats.py`. Lecturas: (a) la referencia retenida — los
`206` y los **subconjuntos alineados** que la tesis informa por separado; (b) el corpus fresco
de prevalencia natural de `c-229`, como lectura primaria. El script aborta si algun caso
carece de prediccion en algun sistema. Determinista, solo lectura, sin red ni Gemini. Cumple
`delivered-classifier-decision` (DCD-001).

### D5 — Anclaje y no alcanzabilidad

Antes de escribir, el script reproduce los anclajes vigentes (`142/206` de exactitud estricta
y macro-F1 `0,7024` sobre la referencia de arbitro unico) y aborta sin escribir si no
coinciden. Toda lectura sobre los `206` se rotula como contraste descriptivo y declara que
`0,85` **no es alcanzable** sobre esa referencia; el corpus de `c-229` es la lectura primaria.
Cumple `delivered-classifier-decision` (DCD-001).

### D6 — Regla de decision pre-registrada

La regla se fija en un documento versionado (`runbook-veredicto-c232.md`) **antes** de correr
el contraste y no se redefine despues de ver el resultado. Tres salidas mutuamente exclusivas
y exhaustivas, sobre la diferencia pareada (supervisado − hibrido):

1. **Reemplazar** la etapa semantica: el limite inferior del IC de la diferencia (exactitud
   estricta) es `> 0` sobre el corpus de `c-229` **y** `>= 0` sobre la referencia retenida,
   **y** la macro-F1 no cae por debajo del margen fijado.
2. **Complementar** (segunda opinion o senal de gate): sin dominar estrictamente, mejora un
   subconjunto pre-especificado (por ejemplo la frontera `Sistemas`↔`Soporte Tecnico Software`
   o los casos que el hibrido falla) con limite inferior del IC `> 0` tras la correccion por
   comparaciones multiples declarada, o reduce la tasa de revision humana; se integra sin
   reemplazar la etapa semantica.
3. **Conservar** el hibrido: cualquier otro caso, incluido «no supera».

El veredicto es **uno** de los tres, con su evidencia y su IC. El default entregado cambia
solo bajo **reemplazar**. Cumple `delivered-classifier-decision` (DCD-002). Alternativa
descartada: decidir despues de ver el resultado, porque invita al sesgo de confirmacion.
Alternativa descartada: exigir solo un punto estimado sin IC, porque no distingue mejora de ruido.

### D7 — Tesis, memo y trazabilidad

- `07-resultados.tex`: contraste cabeza a cabeza con IC, por sistema y por lectura (retenida y
  prevalencia natural), rotulado.
- `08-discusion.tex`: alcance y limitaciones del veredicto; no se afirma mas de lo medido.
- `09-conclusiones.tex` y `10-recomendaciones.tex`: el veredicto y su consecuencia sobre la
  configuracion entregada; si el veredicto es conservar o complementar, se declara que el
  hibrido sigue siendo el clasificador entregado.
- Si el veredicto es **reemplazar**, se revisa con los autores la declaracion de configuracion
  entregada (Anexo B / nota de version, `12-anexos.tex`) y se actualiza.
- `numeros-canonicos.md`: seccion aditiva (primer numero libre al aplicar; hoy la ultima
  planificada es `3.41`; esperado `3.42`) con los valores del contraste y el veredicto, cada
  uno con procedencia, ambito y estado.
- Declarar en la prosa la dependencia de `c-228`/`c-229`/`c-230` y de datos que no existen.
- Cumple `tesis-document` y `tesis-numeros-canonicos`.

### D8 — Gobernanza y checkpoints

Gobernanza **ALTA** (toca la linea del clasificador de produccion y la configuracion
entregada). Checkpoints humanos: **A** antes de consumir el resultado de `c-228` y congelar el
modelo; **B** antes de cambiar el default entregado o registrar el adaptador como seleccionable
por defecto; **C** antes de emitir el veredicto y de tocar la declaracion de configuracion
entregada. Sin bloque LOW critico. Cero llamadas pagas fuera del gate.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| `c-228`/`c-229`/`c-230` sin aplicar: el insumo no existe | Dependencia declarada; tarea bloqueada y registrada, sin sustituto de conveniencia |
| Presentar la integracion como mejora no medida | Veredicto honesto; «no supera» se informa; `0,85` no alcanzable sobre `206` rotulado |
| Forzar el reemplazo | Regla de tres vias con IC; conservar es la salida por defecto |
| Romper el contrato canonico o el hibrido | Integracion detras del mismo contrato; prueba de neutralidad y no regresion |
| Deriva del modelo congelado | Congelado versionado con SHA-256; el default no cambia |
| Sesgo de confirmacion en la regla | Regla pre-registrada antes de ver el resultado; no se redefine |
| Crecimiento de paginas | Prosa acotada; verificar `\@abspage@last` |

## Migration Plan

1. Preparacion y linea de base (tareas 0); checkpoints A/B/C registrados.
2. Consumo del benchmark y congelado del modelo (tareas 1).
3. Integracion detras del contrato (tareas 2).
4. Contraste cabeza a cabeza (tareas 3).
5. Regla pre-registrada y veredicto (tareas 4).
6. Tesis, memo y trazabilidad (tareas 5).
7. Verificacion de cierre (tareas 6).

Rollback: `git revert` del commit; el modelo, el script y sus salidas son aditivos; el
adaptador se retira y el default vuelve al hibrido; el memo, la prosa y la trazabilidad
vuelven por archivo. Ningun valor canonico previo cambia.

## Open Questions

- **OQ1 (autores, aplica a tarea 1)**: confirmar el criterio de seleccion del «mejor modelo»
  ya fijado por `c-228` y si su artefacto se versiona como binario o como puntero + hash.
  Se resuelve al aplicar; no cambia specs ni aprobacion.
- **OQ2 (autores, aplica a tarea 4)**: confirmar el margen de macro-F1 y la correccion por
  comparaciones multiples de la regla de tres vias. Por defecto se fijan en el runbook antes
  de correr el contraste.
- **OQ3 (aplicacion, tareas 1/3)**: si `c-228`/`c-229`/`c-230` no entregan su artefacto, las
  tareas quedan bloqueadas y se registran; el change se conserva como diseno y declaracion.
