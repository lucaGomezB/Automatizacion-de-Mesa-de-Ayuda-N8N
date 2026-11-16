# Proposal: Integrar el clasificador supervisado en la configuracion entregada

## Adaptacion a la devolucion de tercera instancia (16/11/2026)

Este change lo propuso un coautor el 15/11/2026, un dia antes de la devolucion de tercera instancia (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`), con 0 tareas aplicadas. Se reformula; no se crea de cero.

**Premisa que cayo.** La version anterior contrastaba el modelo supervisado contra el hibrido sobre la referencia retenida de 206 casos (corpus independiente de 150 mas 56 de refuerzo, etiquetado por E3/E4 y arbitrado por E5) y sus «subconjuntos alineados», anclaba el contraste en `0,6893` (`142/206`) y macro-F1 `0,7024`, citaba el techo `+34` / `0,835`, los `30 errores` de `Sistemas` y el `0,8278` del brazo manual «sobre la misma referencia», y leia `predicciones_arbitrado.json`. Los autores **retiran** esa evidencia del ejemplar; el motivo y el alcance del retiro los fija `c-235` y no se reformulan aqui. Todas esas cifras y artefactos quedan **retirados** y este change ya no los usa como ancla, insumo, conjunto de contraste ni comparador. Se elimina el Scenario «No alcanzabilidad declarada sobre los 206». El `0,8278` sobrevive en la tesis, pero se midio contra el consenso E1/E2 de la campana complementaria (`07-resultados.tex:383`), no sobre los 206; no es un anclaje de este change.

**Que se conserva.** Congelado del modelo seleccionado (SCI-001), integracion detras del contrato de `c-227` (SCI-002), neutralidad por defecto (SCI-003), proveedor seleccionable, regla de tres vias y veredicto honesto, incluida la salida «no supera».

**Que cambia.**

- El contraste cabeza a cabeza y la regla pre-registrada se definen **solo** sobre el corpus probabilistico acreditado de `c-229` con la referencia por mayoria de `c-230`. No hay lectura «retenida» alternativa.
- El pre-registro no se acredita solo con la fecha de un commit (la controlan los autores): se suma una constancia en custodia del director antes de medir.
- Compuertas de procedencia (K-01) y etica y legal (K-02) para todo dato nuevo, incluido el envio de textos a la Gemini API para obtener las predicciones del hibrido sobre el corpus acreditado.
- Lo que puede hacerse sin datos nuevos (adaptador offline, validador de manifiesto, funciones puras del contraste y de la regla, con TDD y fixtures rotulados como sinteticos) queda en un grupo propio; tambien posterior a la entrega salvo decision de los autores.
- No se usa como referencia el canario de 103 casos de `c-227` (material retirado; su rotulo lo decide `c-235` OQ6).
- Registro A-03 en el inventario de `c-237`.
- La seccion del memo conserva el numero reservado `3.42`.

**Alcance respecto de la entrega.** Por defecto (decision abierta a los autores, OQ6) este change **no modifica el ejemplar que se defiende** ni el default entregado. Queda **bloqueado** hasta que `c-228`, `c-229` y `c-230` entreguen, y se ejecuta despues del cierre de la entrega (`c-235` → `c-236` → `c-237` → `c-238` → `c-239`), ultimo en el orden `c-229` → `c-230` → `c-228` → `c-232`. La tesis lo menciona solo como trabajo futuro, en los terminos que fija `c-235`. El default entregado sigue siendo el hibrido. El tribunal no pidio un clasificador supervisado y declaro que ninguna correccion exige codigo nuevo.

**Busqueda de control de cifras y alias retirados** (criterio de aceptacion): `rg -n "206|0,6893|0,7489|0,7024|0,835|142/206|16 de 64|E3|E4|E5|arbitrado|fuera de muestra|corpus independiente" <ruta>`. Sobre este change solo debe devolver lineas de esta seccion o del bloque equivalente de `design.md`.

## Why

`c-228` entrega la maquinaria del clasificador supervisado y no toca el clasificador de produccion. Queda abierta la pregunta practica: el mejor modelo del benchmark de `c-228`, ¿reemplaza o complementa al **hibrido vigente** (filtro deterministico + Gemini) en la configuracion entregada, o no lo supera? Esa pregunta solo puede responderse sobre un conjunto de prueba cuya procedencia se pueda acreditar y que no se haya usado para ajustar ninguno de los dos sistemas. El corpus de 200 casos no sirve: el hibrido se ajusto, en parte, con el (`10-recomendaciones.tex:26`). El unico conjunto admisible es el corpus probabilistico acreditado de `c-229` con la referencia por mayoria de `c-230`.

La honestidad es el punto: el veredicto «no supera» es un resultado valido y esperado. El change MUST NOT forzar el reemplazo.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **0. Compuertas** | Compuerta de procedencia (K-01) y etica y legal (K-02) sobre el corpus acreditado y sobre todo envio de texto a terceros (incluida la corrida del hibrido contra la Gemini API). | **ALTA** |
| **A. Sin datos nuevos** | Validador del manifiesto de congelado, adaptador offline detras del contrato de `c-227`, funciones puras del contraste pareado y de la regla de tres vias; todo con TDD y fixtures rotulados como sinteticos. Posterior a la entrega salvo decision de los autores. | **ALTA** |
| **B. Consumo y congelado** | Se consume el mejor modelo de `c-228` y se congela (pesos, tokenizer, version del codebook, hash del split, preprocesamiento) con SHA-256. Bloqueado hasta `c-228`. | **ALTA** |
| **C. Contraste cabeza a cabeza** | Contraste pareado sobre el corpus probabilistico acreditado con referencia por mayoria, con IC bootstrap y McNemar. Bloqueado hasta `c-229`/`c-230`. | **ALTA** |
| **D. Regla y veredicto** | Regla pre-registrada (versionada y con constancia en custodia del director antes de medir): reemplazar / complementar / conservar. Veredicto honesto. | **ALTA** |
| **E. Memo y tesis posterior** | Seccion reservada `3.42` del memo; prosa solo en una version posterior a la defensa y con compuertas cerradas. | BAJA/MEDIA |

**No objetivos.**

- No se modifica el ejemplar que se defiende ni el default entregado en la entrega.
- No se re-entrena ni se reabre el benchmark de `c-228`.
- No se cambian las cinco cadenas canonicas, el prompt vigente, los parametros de inferencia ni el umbral del gate.
- No se fuerza el reemplazo del hibrido.
- No se usa ninguna cifra ni artefacto retirado por `c-235`, ni el canario de `c-227` como referencia.
- No se envia texto a la Gemini API ni a otro tercero sin K-02 cerrada.

## Capabilities

### New Capabilities

- `supervised-classifier-integration`: congela el modelo supervisado seleccionado como artefacto versionado y reproducible, y lo integra detras del mismo contrato del clasificador, seleccionable por configuracion, ejecutado localmente y sin romper el hibrido ni las cadenas canonicas.
- `delivered-classifier-decision`: contraste pareado cabeza a cabeza sobre el corpus probabilistico acreditado con referencia por mayoria y regla de decision pre-registrada de tres vias, con constancia previa en custodia del director y veredicto honesto.

### Modified Capabilities

- `inference-provider-abstraction`: se AGREGA el modelo supervisado local como proveedor seleccionable, sin cambiar el contrato canonico ni el default entregado salvo que la regla pre-registrada mande reemplazar.
- `tesis-document`: se AGREGA que el ejemplar de la defensa no cambia por este change y que el veredicto se informa solo en una version posterior con compuertas cerradas.
- `tesis-numeros-canonicos`: se AGREGA el registro aditivo en la seccion reservada `3.42`.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `evaluation/` (pruebas y funciones puras) | Nuevo | Validador de manifiesto, contraste pareado y regla de tres vias, con fixtures sinteticos rotulados |
| `evaluation/data/campana/analisis/` | Nuevo (condicionado) | Script, JSON/MD y manifiesto SHA-256 del contraste, solo con compuertas cerradas |
| `evaluation/data/modelo_supervisado_c232/` | Nuevo (condicionado) | Modelo congelado (o puntero + hash) con manifiesto |
| `App/Backend/app/classifiers/` | Modificado | Adaptador offline detras del contrato de `c-227`; hibrido intacto |
| `App/Backend/app/config/` | Posible | Seleccion por configuracion; default sin cambios |
| `docs/campana-medicion/runbook-veredicto-c232.md` | Nuevo | Regla pre-registrada; constancia en custodia del director |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo (condicionado) | Seccion reservada `3.42` |
| `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` | Aditivo | Registro A-03 (archivo de `c-237`) |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad y estado de compuertas |
| `docs/Tesis/v10 (IA)/paper/sections/*.tex` | Sin cambios en la entrega | Solo en una version posterior y con compuertas cerradas |

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| `c-228`/`c-229`/`c-230` no entregan: el insumo no existe | Alta | Change bloqueado y registrado; sin sustituto de conveniencia |
| Datos o etiquetas sin procedencia acreditable (repetir K-01) | Media | Compuerta de procedencia con verificacion del director |
| Envio de textos a la Gemini API sin autorizacion (repetir K-02) | Media | Corrida del hibrido sobre el corpus acreditado bloqueada hasta K-02 y declarada |
| Pre-registro no acreditable (fecha de commit controlada por los autores) | Media | Constancia en custodia del director antes de medir |
| Subconjuntos o reintentos elegidos despues de ver resultados (M-02) | Media | Conjunto y subconjuntos pre-especificados en la regla; sin reintentos a posteriori |
| Forzar el reemplazo | Media | Regla de tres vias con IC; conservar por defecto |
| Agregar evidencia nueva a la tesis sin acreditarla | Alta | Ejemplar sin cambios; prosa solo en version posterior con compuertas cerradas |

## Rollback Plan

`git revert` del commit del change: modelo congelado, script y salidas son aditivos; el adaptador se retira y el default resuelve al hibrido; la seccion `3.42` del memo se retira sin tocar las anteriores. No se modifica ninguna cadena canonica, ningun valor vigente ni el ejemplar de la defensa.

## Dependencies

- `c-235` a `c-239` cerrados (fin de la entrega), salvo decision contraria de los autores (OQ6).
- `c-228-clasificador-supervisado-sobre-el-corpus-acumulado` (benchmark, corpus y particiones congelados).
- `c-229-muestreo-probabilistico-del-universo-de-incidentes` (corpus probabilistico acreditado con sus compuertas).
- `c-230-referencia-por-mayoria-con-etiquetadores-independientes` (referencia por mayoria y kappa de Fleiss para ese corpus).
- `c-227-monitorear-el-servicio-de-inferencia-y-la-deriva-del-modelo` (aplicado; abstraccion proveedor/clasificador que se reutiliza; su canario no es referencia).
- `c-237-declarar-de-forma-completa-el-uso-de-asistentes-de-ia` (inventario A-03).
- **Datos que todavia no existen**: los tres primeros changes estan propuestos y sin aplicar.

## Success Criteria

- [ ] Compuertas K-01 y K-02 registradas como cerradas (con evidencia) o abiertas (con el bloqueo declarado) antes de tocar datos reales o enviar texto a terceros.
- [ ] El modelo seleccionado se congela con SHA-256 y procedencia; no se reabren los criterios de `c-228`.
- [ ] El modelo se integra detras del mismo contrato, corre localmente y es seleccionable por configuracion; una prueba demuestra que el default reproduce el hibrido.
- [ ] El contraste pareado se calcula solo sobre el corpus probabilistico acreditado con referencia por mayoria.
- [ ] La regla de decision consta en un documento versionado y en una constancia en custodia del director antes de medir; el veredicto es uno de reemplazar / complementar / conservar, incluido «no supera».
- [ ] Ninguna cifra ni artefacto retirado por `c-235` aparece en Requirements, Scenarios ni tareas ejecutables.
- [ ] El trabajo con asistentes de IA queda registrado en el inventario de `c-237`.
- [ ] `openspec validate c-232-integrar-el-clasificador-supervisado-en-la-configuracion-entregada --strict` pasa.
