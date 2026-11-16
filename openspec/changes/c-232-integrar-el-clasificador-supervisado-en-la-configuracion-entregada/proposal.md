# Proposal: Integrar el clasificador supervisado en la configuracion entregada

## Why

`c-228` entrega la **maquinaria** del clasificador supervisado (curacion, particion,
arnes tipo BERT, benchmark de modelos abiertos) y lo declara explicitamente: **no toca
el clasificador de produccion**. Queda abierta la pregunta de mayor valor practico: el
mejor modelo del benchmark de `c-228`, ¿alcanza para reemplazar o complementar al
**hibrido vigente** (filtro deterministico + Gemini) en la configuracion entregada, o
no lo supera? Hoy la referencia fuera de muestra del hibrido es `0,6893` (`142/206`) y
sobre esos `206` el umbral `0,85` **no es alcanzable** (`+34` aciertos; techo `0,835`
aun corrigiendo los `30` errores de `Sistemas`; brazo manual `0,8278`). Este change
lleva el mejor modelo de `c-228` a la configuracion entregada, lo contrasta **cabeza a
cabeza** contra el hibrido y decide —con una **regla pre-registrada**— si lo reemplaza,
lo complementa o **no lo supera**.

La honestidad es el punto: el veredicto «no supera» es un resultado valido y esperado.
El change MUST NOT forzar el reemplazo.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Consumo y congelado** | Se consume el mejor modelo del benchmark de `c-228` (criterios fijados de antemano) y su corpus/particiones congelados; se **congela** el modelo seleccionado (pesos, tokenizer, version del codebook, hash del split de entrenamiento, version de preprocesamiento) como artefacto versionado, reproducible y con SHA-256. | **ALTA** |
| **B. Integracion** | El modelo congelado se integra en la configuracion entregada detras del **mismo contrato del clasificador** (abstraccion proveedor/clasificador de `c-227`), como proveedor/etapa seleccionable por configuracion; no rompe el hibrido ni las cinco cadenas canonicas. | **ALTA** |
| **C. Contraste cabeza a cabeza** | Contraste **pareado** (mismos casos) del modelo supervisado contra el hibrido, sobre la referencia retenida (`206` y los subconjuntos alineados) y sobre el corpus de prevalencia natural de `c-229`, con IC bootstrap y McNemar. | **ALTA** |
| **D. Regla y veredicto** | **Regla de decision pre-registrada** (antes de ver el resultado): reemplazar la etapa semantica / complementar (segunda opinion o senal de gate) / **conservar el hibrido**. Veredicto honesto, incluido «no supera». | **ALTA** |
| **E. Tesis, memo y trazabilidad** | Prosa honesta en resultados, discusion, conclusiones y recomendaciones; seccion aditiva del memo canonico; entrada en el dictamen. Si se integra, se revisa con los autores la declaracion de configuracion entregada (Anexo B / nota de version). | BAJA/MEDIA |

**No objetivos.**

- No se re-entrena ni se reabre el benchmark de `c-228`: se **consume** su resultado y sus criterios, fijados de antemano.
- No se cambian las cinco cadenas canonicas, el prompt vigente, los parametros de inferencia ni el umbral del gate de revision humana.
- No se fuerza el reemplazo del hibrido: «no supera» es un veredicto valido y se informa.
- No se remide la referencia de `206` ni el corpus de `c-229`: se consumen.
- No hay llamadas pagas fuera del gate de confirmacion; el recomputo usa predicciones congeladas.
- No se reclasifica el corpus de ajuste.

## Capabilities

### New Capabilities

- `supervised-classifier-integration`: congela el modelo supervisado seleccionado (pesos, tokenizer, codebook, hash del split) como artefacto versionado y reproducible, y lo integra en la configuracion entregada detras del mismo contrato del clasificador, sin romper el hibrido ni las cadenas canonicas.
- `delivered-classifier-decision`: contraste pareado cabeza a cabeza del modelo supervisado contra el hibrido vigente (referencia retenida y corpus de prevalencia natural) y regla de decision pre-registrada de tres vias (reemplazar / complementar / conservar), con veredicto honesto.

### Modified Capabilities

- `inference-provider-abstraction`: se AGREGA el modelo supervisado local como proveedor/etapa seleccionable por configuracion, sin cambiar el contrato canonico ni el default entregado salvo que la regla pre-registrada mande reemplazar.
- `tesis-document`: se AGREGA la divulgacion honesta del veredicto (resultados, discusion, conclusiones y recomendaciones) y, si se integra, la revision con los autores de la declaracion de configuracion entregada (Anexo B / nota de version).
- `tesis-numeros-canonicos`: se AGREGA el registro aditivo del contraste cabeza a cabeza y del veredicto, con procedencia, ambito y estado.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `evaluation/data/campana/analisis/` | Nuevo | Script, prueba, JSON/MD y manifiesto SHA-256 del contraste y del veredicto |
| `evaluation/data/modelo_supervisado_c232/` | Nuevo | Modelo congelado (o puntero + hash si el binario no se versiona) con manifiesto |
| `App/Backend/app/classifiers/` | Modificado | Adaptador del modelo supervisado detras del contrato de `c-227` (nuevo; hibrido intacto) |
| `App/Backend/app/config/` | Posible | Seleccion por configuracion del proveedor supervisado; default sin cambios |
| `docs/Tesis/v10 (IA)/paper/sections/07`, `08`, `09`, `10` | Modificado | Veredicto honesto en resultados, discusion, conclusiones y recomendaciones |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Condicional | Nota de version / Anexo B si el veredicto es reemplazar |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion nueva (esperado `3.42`) con el contraste y el veredicto |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |

Sin cambios en las cinco cadenas canonicas, el prompt vigente ni las predicciones congeladas. Cero llamadas a Gemini fuera del gate.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Que `c-228`/`c-229`/`c-230` no se apliquen y el insumo no exista | Alta | Dependencia declarada; la tarea queda bloqueada y registrada, sin sustituir por datos de conveniencia |
| Presentar la integracion como mejora no medida | Alta | Regla pre-registrada y veredicto honesto; «no supera» se informa |
| Forzar el reemplazo del hibrido | Media | La regla de tres vias exige superioridad pareada con IC; conservar es la salida por defecto |
| Deriva del modelo congelado | Media | Congelado versionado con SHA-256 y procedencia; el default no cambia |
| Romper el contrato canonico o el hibrido | Media | Integracion detras del mismo contrato; prueba de neutralidad y no regresion |
| Sobreactuar sobre los `206` | Alta | Rotulo de no alcanzabilidad del `0,85`; el corpus fresco de `c-229` es la lectura primaria |
| Crecimiento de paginas | Media | Prosa acotada; verificacion de `\@abspage@last` |

## Rollback Plan

`git revert` del commit del change: el modelo congelado, el script y sus salidas son aditivos; el adaptador se retira y el default resuelve de nuevo al hibrido; la seccion del memo se retira sin tocar las anteriores; la prosa y la trazabilidad vuelven por archivo. No se modifica ninguna cadena canonica ni ningun valor vigente, de modo que el rollback no deja huecos numericos.

## Dependencies

- `c-228-clasificador-supervisado-sobre-el-corpus-acumulado` (resultado del benchmark, corpus y particiones congelados).
- `c-229-muestreo-probabilistico-del-universo-de-incidentes` (corpus de prevalencia natural).
- `c-230-referencia-por-mayoria-con-etiquetadores-independientes` (referencia por mayoria).
- `c-227-monitorear-el-servicio-de-inferencia-y-la-deriva-del-modelo` (aplicado; abstraccion proveedor/clasificador que se reutiliza).
- **Datos que todavia no existen**: los tres changes anteriores estan propuestos y sin aplicar.

## Success Criteria

- [ ] El modelo seleccionado se congela (pesos, tokenizer, codebook, hash del split) como artefacto versionado, reproducible y con SHA-256; se declara la no reapertura de los criterios de `c-228`.
- [ ] El modelo se integra detras del mismo contrato y es seleccionable por configuracion; una prueba demuestra que el default reproduce el hibrido y que las cinco cadenas canonicas no cambian.
- [ ] El contraste pareado cabeza a cabeza reporta exactitud estricta, macro-F1 y metricas por clase por sistema, con IC de la diferencia y McNemar, sobre la referencia retenida y el corpus de `c-229`.
- [ ] La regla de decision esta declarada antes de ver el resultado y el veredicto es uno de reemplazar / complementar / conservar, informado honestamente (incluido «no supera»).
- [ ] La tesis informa el veredicto sin presentar el modelo como entregado si no lo es; el memo registra el contraste y el veredicto sin alterar valores previos.
- [ ] `openspec validate c-232-integrar-el-clasificador-supervisado-en-la-configuracion-entregada --strict` pasa.
