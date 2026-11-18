# Design: Integrar el clasificador supervisado en la configuracion entregada

## Adaptacion a la devolucion de tercera instancia (16/11/2026)

- **Premisa que cayo.** La version del 15/11/2026 contrastaba sobre la referencia retenida de 206 casos (corpus independiente etiquetado por E3/E4 y arbitrado por E5) y sus subconjuntos alineados, con anclas `142/206` (`0,6893`) y macro-F1 `0,7024` y lectura de `predicciones_arbitrado.json` (antiguos D4 y D5). Todo eso queda **retirado**; el motivo lo fija `c-235` (proposal, design D2, D9, D10, OQ6, OQ8) y no se reformula aqui. El antiguo D5 («Anclaje y no alcanzabilidad») se elimina completo.
- **Correccion de un hecho.** El `0,8278` del brazo manual se midio contra el consenso E1/E2 de la campana complementaria (`07-resultados.tex:383`), no sobre los 206; no se usa en este change.
- **Que se conserva.** D1 (alcance), D2 (congelado), D3 (integracion), D6 (regla de tres vias), D8 (checkpoints).
- **Que cambia.** D0 (compuertas, nuevo), D4 (contraste solo sobre el corpus acreditado), D5 (lugar de ejecucion y envios a terceros, reemplaza al anterior), D6 (pre-registro con constancia del director), D7 (memo `3.42` y tesis posterior), D9 (grupos y orden), D10 (A-03).
- **Alcance respecto de la entrega.** Por defecto no se modifica el ejemplar ni el default entregado; el change queda bloqueado hasta `c-228`, `c-229` y `c-230`, y se ejecuta despues de `c-239` (OQ6). El destino que confirmen los autores lo registra `c-239` (D11); esta reformulacion no presupone la decision (OQ7).

## Estado: DETENIDO (18/11/2026)

El change queda **detenido** y se conserva como trabajo futuro lo autocontenido del grupo A: el validador del manifiesto, el adaptador offline detras del contrato de `c-227` y las funciones puras del contraste pareado y de la regla de tres vias. Las tareas quedan **sin marcar**; nada se aplico.

**Motivo.** Faltan los dos insumos que comparte la familia post-entrega: un marco poblacional completo (por el que `c-229` quedo detenido) y un `clasificacion_log` real acumulado (alrededor de 153 filas de prototipo y campana, 3 validadas en el repositorio), mas el consentimiento escrito de los etiquetadores independientes nuevos (desde `E6`) y la decision K-02 sobre el envio de textos nuevos a la Gemini API.

**Reapertura.** Solo con un periodo real de operacion del prototipo como mesa de ayuda del equipo y la exportacion completa de la tabla `incidente` (marco para `c-229` y log real para `c-228`), con el consentimiento escrito de los etiquetadores independientes y la decision K-02.

## Context

- El clasificador vigente es el **hibrido** detras de la abstraccion de `c-227`: `App/Backend/app/classifiers/provider.py` (`InferenceProvider`, registro, `PROVEEDOR_POR_DEFECTO = "gemini"`), `base.py` (`BaseClassifier`), `hybrid.py` y `inference_provider`/`inference_model` en `Settings`. El default es neutral.
- `c-228` entrega el benchmark y el corpus/particiones congelados; `c-229`, el diseno, el estimador y el corpus probabilistico acreditado (con compuertas K-01 y K-02); `c-230`, las funciones de mayoria y kappa de Fleiss y el protocolo de referencia por mayoria para ese corpus. Los tres estan **propuestos y sin aplicar**.
- El corpus de 200 casos es el corpus de ajuste del hibrido (`10-recomendaciones.tex:26`): no es un conjunto de contraste admisible.
- `c-227` usa como canario 103 casos del material retirado; `c-235` OQ6 decide su rotulo. Este change no depende de ese canario.
- Reutilizables sin modificar: `evaluation/metrics.py`, `evaluation/stats.py` (`contraste_mcnemar`, bootstrap), `evaluation/no_solape.py`.

## Goals / Non-Goals

**Goals:**

- Consumir el resultado de `c-228` y congelar el modelo seleccionado con procedencia.
- Integrarlo detras del mismo contrato, local y seleccionable, sin romper el hibrido.
- Contrastarlo cabeza a cabeza contra el hibrido sobre el corpus acreditado con IC y prueba pareada.
- Decidir con una regla pre-registrada y acreditada de tres vias y dejar el registro honesto.

**Non-Goals:**

- Modificar el ejemplar de la defensa o el default entregado durante la entrega.
- Re-entrenar o redefinir los criterios de `c-228`.
- Cambiar cadenas canonicas, prompt, parametros de inferencia o gate.
- Usar cifras o artefactos retirados, el corpus de 200 como contraste o el canario de `c-227` como referencia.
- Enviar texto a terceros sin K-02.

## Decisions

### D0 — Compuertas de procedencia (K-01) y etica y legal (K-02)

**Procedencia.** Ningun dato nuevo entra al contraste sin: el registro crudo exportado del sistema con las marcas temporales que el sistema registra (nunca reconstruidas); constancia de la organizacion sobre la extraccion con el original en custodia del director; hash SHA-256 del export crudo en el repositorio; prohibicion de que un texto redactado por los autores o generado o asistido por IA entre como dato presentado como real; verificacion del director contra la evidencia primaria antes del analisis. Para el corpus acreditado se verifica que `c-229` y `c-230` registraron esas compuertas como cerradas; no se repiten, se comprueban. Los fixtures sinteticos se rotulan en nombre de archivo, cabecera y salida.

**Etica y legal.** Autorizacion institucional escrita, base de licitud (Ley 25.326) y consentimiento. Se declara donde corre cada sistema:

| Sistema | Donde corre | Envio a terceros |
|---|---|---|
| Modelo supervisado congelado | Local, offline, pesos fijados por hash | Ninguno |
| Hibrido, etapa deterministica | Backend local | Ninguno |
| Hibrido, etapa Gemini | Gemini API (tercero) | Si: el texto de cada caso que llega a esa etapa |

Las predicciones del hibrido sobre el corpus acreditado se toman, si existen, de las registradas en operacion (`clasificacion_log.sector_id_predicho` con la version del proveedor). Si hay que generarlas, la corrida envia textos a la Gemini API: queda **bloqueada** hasta que la autorizacion de K-02 cubra ese envio de forma expresa, y el envio se declara (cantidad de textos, fecha, modelo). Si la autorizacion no lo cubre, el contraste no se ejecuta (OQ3).

### D1 — Alcance: consumir, congelar, integrar, contrastar y decidir

El change toma **exactamente un** modelo del benchmark de `c-228`. Si `c-228` no produjo modelo o benchmark, la tarea queda **bloqueada y registrada**; no se sustituye por un modelo elegido a mano.

### D2 — Congelado versionado del modelo seleccionado

Artefacto `evaluation/data/modelo_supervisado_c232/` con manifiesto (UTF-8 sin BOM, LF):

| Campo | Contenido |
|---|---|
| `modelo`, `tokenizer` | identificador y version exactos; SHA-256 del binario |
| `codebook_version` | version del codebook de `c-228`/`c-230` |
| `split_hash` | SHA-256 del split de entrenamiento |
| `preprocesamiento` | version del pseudonimizado/normalizacion |
| `procedencia_datos` | SHA-256 del export crudo y estado de las compuertas de `c-228` |
| `comando_evaluacion` | comando reproducible del contraste |

El modelo es **inmutable**. Cumple SCI-001.

### D3 — Integracion detras del mismo contrato del clasificador

Proveedor/etapa seleccionable a traves de la abstraccion de `c-227`, respetando el contrato canonico. El default **sigue resolviendo al hibrido** salvo veredicto **reemplazar** y checkpoint B. El adaptador corre **offline**. Prueba de neutralidad con el default. Cumple SCI-002, SCI-003 e `inference-provider-abstraction`.

### D4 — Contraste pareado solo sobre el corpus acreditado

Sobre los mismos casos del corpus probabilistico acreditado de `c-229`, emparejados por `caso_id`, con la referencia por mayoria de `c-230`: por sistema, exactitud estricta y laxa, macro-F1 y P/R/F1 por clase; diferencia pareada de la exactitud estricta con IC 95 % (bootstrap percentil, semilla fija) y McNemar; estimacion referida al universo con el estimador de `c-229`. Todos los casos, sin exclusiones; los subconjuntos que la regla use (por ejemplo, la frontera `Sistemas`↔`Soporte Tecnico Software`) se pre-especifican en la regla; no hay reintentos ni subconjuntos decididos despues de ver resultados (leccion de M-02). Antes de comparar, el script verifica los SHA-256 de entradas declarados en la regla y aborta sin escribir si no coinciden o si un caso carece de prediccion. Determinista, solo lectura, sin red. Cumple DCD-001.

### D5 — Lugar de ejecucion y envios

Resumido en la tabla de D0. El script del contraste nunca llama a la red: consume predicciones ya obtenidas. Cumple SCI-002 y DCD-001.

### D6 — Regla de decision pre-registrada y acreditada

La regla se fija en `docs/campana-medicion/runbook-veredicto-c232.md` **antes** de obtener las predicciones sobre el corpus acreditado, con los SHA-256 de las entradas previstas, los umbrales, el margen de macro-F1 y la correccion por comparaciones multiples. La fecha del commit no basta (la controlan los autores): se entrega al director una **constancia** (copia firmada o impresa con el SHA-256 del runbook), que queda en su custodia, y se registra su fecha en `dictamen-correcciones.md`. La regla no se redefine despues.

Tres salidas, sobre la diferencia pareada (supervisado − hibrido) en el corpus acreditado:

1. **Reemplazar** la etapa semantica: limite inferior del IC de la diferencia de exactitud estricta `> 0` y macro-F1 sin caer por debajo del margen fijado.
2. **Complementar** (segunda opinion o senal de gate): sin dominar, mejora un subconjunto pre-especificado con limite inferior del IC `> 0` tras la correccion declarada, o reduce la tasa de revision humana.
3. **Conservar** el hibrido: cualquier otro caso, incluido «no supera».

El default cambia solo bajo **reemplazar**. Cumple DCD-002.

### D7 — Memo y tesis

- `numeros-canonicos.md`: seccion **`3.42`** (reservada; `c-235` declara `3.39`-`3.42` reservadas y toma `3.45`), solo con valores producidos con compuertas cerradas.
- La tesis no cambia en la entrega. En una version posterior a la defensa, y solo con compuertas cerradas, se informa el veredicto respetando el texto que deja `c-235`. Si el veredicto es reemplazar, se revisa con los autores la declaracion de configuracion entregada de esa version.

### D8 — Gobernanza y checkpoints

Gobernanza **ALTA**. Checkpoints: **A** antes de consumir `c-228` y congelar; **B** antes de cambiar el default; **C** antes de emitir el veredicto; **D** antes de cualquier envio de texto a terceros.

### D9 — Grupos y orden

- Grupo «sin datos nuevos» (validador, adaptador, contraste y regla como funciones puras, con fixtures sinteticos rotulados): posterior a la entrega salvo decision de los autores (OQ6); no cambia el default.
- Grupos con datos: bloqueados hasta `c-228`, `c-229` y `c-230`.

### D10 — Registro del uso de asistentes de IA (A-03)

Toda tarea hecha con un asistente de IA se registra en `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (archivo de `c-237`).

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| Insumos inexistentes | Change bloqueado y registrado |
| Envio a la Gemini API sin autorizacion | D0: bloqueado hasta K-02 expresa |
| Pre-registro no acreditable | D6: constancia en custodia del director |
| Subconjuntos o reintentos a posteriori | D4: pre-especificados en la regla |
| Forzar el reemplazo | Regla de tres vias; conservar por defecto |
| Romper el contrato o el hibrido | Integracion detras del contrato; prueba de neutralidad |
| Contradiccion con `c-235` | El ejemplar no cambia (D7) |

## Migration Plan

1. Compuertas y linea de base (grupo 0).
2. Grupo sin datos nuevos (grupo 1).
3. Congelado (grupo 2, tras `c-228`).
4. Integracion (grupo 3).
5. Regla pre-registrada y constancia (grupo 4).
6. Contraste y veredicto (grupo 5, tras `c-229`/`c-230` y K-02).
7. Memo y registro (grupo 6).
8. Verificacion de cierre (grupo 7).

## Open Questions

- **OQ1 (autores):** criterio de seleccion del «mejor modelo» fijado por `c-228` y versionado como binario o puntero + hash.
- **OQ2 (autores):** margen de macro-F1, subconjuntos pre-especificados y correccion por comparaciones multiples.
- **OQ3 (autores):** ¿la autorizacion de la organizacion cubre enviar los textos del corpus acreditado a la Gemini API para obtener las predicciones del hibrido? ¿O existen predicciones del hibrido ya registradas en operacion para esos casos? Sin una de las dos, el contraste no se ejecuta.
- **OQ4 (autores):** ¿con que medio se entrega al director la constancia del pre-registro (copia firmada, impresa con hash)?
- **OQ5 (aplicacion):** si `c-228`/`c-229`/`c-230` no entregan, el change se conserva como diseno y declaracion.
- **OQ6 (autores):** ¿quieren ejecutar algo antes de la defensa (por ejemplo, el grupo sin datos nuevos)? Por defecto, nada; en ningun caso se modifica el ejemplar ni el default.
- **OQ7 (autores):** ¿confirman esta adaptacion (posterior a la entrega) o prefieren archivar el change sin aplicar? El destino lo registra `c-239` (D11).
