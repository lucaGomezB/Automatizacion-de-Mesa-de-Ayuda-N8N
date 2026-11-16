# Design: Retirar la validacion fuera de muestra y declarar su procedencia

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque:

- Documento de partida: tesis **v1.5.2** (tag anotado `v1.5.2` sobre `5509cbf`; el commit `7335fa5` consigna el hash en el Anexo B), entregada al tribunal. Fuente en `docs/Tesis/v10 (IA)/paper/sections/*.tex`. Mapa de capitulos del PDF: `01`=cap. 1, `04`=cap. 4, `05`=cap. 5, `11-aspectos-legales`=cap. 7, `07-resultados`=cap. 8, `08-discusion`=cap. 9, `09-conclusiones`=cap. 10, `10-recomendaciones`=cap. 11, `12-anexos`=Anexos A a J, `00-resumen`=Resumen/Abstract.
- Fuente de las observaciones: `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`, secciones 2 (dictamen), 4 (verificacion de marcas temporales), 5 (K-01, K-02, A-02, M-02, B-02), 7 (correcciones obligatorias) y 8 (preguntas 1 a 5). Este change no reproduce nombres de personas: solo los alias `E1`..`E5`, `O1`, `O2`.
- **Decision de los autores (2026-11-16):** K-01 por **retiro** (opcion 2 del tribunal). El tribunal declara que ninguna correccion exige codigo nuevo y que "la tesis se sostiene sin ellos".
- **Insumo confirmado de un autor (2026-11-16):** las descripciones del corpus independiente son descripciones genericas de incidentes, no incidentes extraidos de la compania. **No confirmado:** como se produjeron las etiquetas y las marcas temporales de `E3`/`E4`/`E5`; quien redacto los textos y con que medio; si los nombres de sucursal y el "sistema principal" refieren a una organizacion real.
- Patron reproducido (hecho verificado): `evaluation/data/campana/doble_etiquetado_arbitrado.csv` (E3/E4/E5, 476 filas) tiene duraciones en [30, 90] s y pausas enteras de 1-5 s (E3, E5) y 1-8 s (E4); `doble_etiquetado.csv` (E1/E2) no lo muestra.
- Los artefactos estan fijados por SHA-256 (`evaluation/data/campana/analisis/SHA256SUMS.txt`, `evaluation/data/canario/canario.SHA256SUMS.txt`, tablas del README de campana) y los leen pruebas de CI: `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py` (L396-399, `predicciones_independiente.json` con 103/69), `evaluation/monitoreo/test_monitor_deriva.py` (L203-226, canario de 103 casos `I*`).
- Changes activos que anclan premisas en `0,6893` o en los 206 casos: `c-228`, `c-229`, `c-230`, `c-232`. Change activo `c-237` (solo metadatos). `c-236`, `c-238`, `c-239` se proponen despues de este.

## Goals / Non-Goals

**Goals:**

- Cerrar **K-01** por retiro: el ejemplar queda sin ninguna cifra, tabla, seccion ni afirmacion que dependa del corpus fuera de muestra, y sin referencias colgantes ni conteos desactualizados.
- Cerrar **K-02** sin datos de terceros: §4.4 deja de describir una compania financiera; §7.3 queda exacta sobre lo que se envio al proveedor; §7.5 deja de tratar a `E3`/`E4`/`E5`; los artefactos publicados quedan rotulados con su naturaleza confirmada por los autores.
- Declarar el retiro **sin ocultar su motivo** en la nota de versiones (Anexo I.1), con el patron de N-02.
- Cerrar **M-02** acotando la conclusion de eficiencia: "sin contraste limpio".
- Dejar **A-02** y **B-02** como "no aplica por retiro" en el registro de correcciones.

**Non-Goals:**

- Acreditar la procedencia (opcion 1 del tribunal): descartada por los autores.
- Medir de nuevo, escribir codigo, cambiar pruebas (salvo que los autores elijan borrar artefactos, D7) o llamar a Gemini.
- Reescribir §9.5 (balance neto, A-01) ni el umbral del 85 % (M-01): `c-236`. Solo se quitan de §9.5 las dos sensibilidades fuera de muestra.
- Declaracion de IA (A-03, `c-237`); legibilidad (M-03, B-01, B-03, `c-238`); respuestas al tribunal, recompilacion de entrega, bump y tag (M-04, `c-239`).
- Editar `c-228`, `c-229`, `c-230`, `c-232`, `.engram/` o `CHANGES.md`.

## Decisions

### D1 — Retiro completo, no parcial ni rebautizado

Se retira todo lo que depende del corpus fuera de muestra: la validacion, el arbitraje, el refuerzo, la sensibilidad a la referencia, el sesgo del vocabulario sobre los 206 casos, la linea de base clasica (probada sobre ese corpus), el bloque primario del brazo de modelo solo y las filas fuera de muestra de la calibracion. **Alternativas descartadas:** (a) conservar la validacion rebautizada como "segunda organizacion" (A-02): no aplica, porque segun los autores no hay segunda organizacion y la procedencia no se acredita; (b) conservar solo los 150 "originales": el patron de marcas temporales afecta a E3 y E4 sobre los 150, y las etiquetas no tienen procedencia confirmada; (c) conservar los analisis derivados como "sensibilidad": dependen de las mismas etiquetas. El principio rector es el del tribunal: la tesis vuelve a sostenerse sobre lo verificado (corpus de 200 casos y campana complementaria con `E1`/`E2`/`O1`/`O2`).

### D2 — Inventario del retiro (anclas verificadas sobre v1.5.2)

| Archivo | Lineas | Alcance | Accion |
|---|---|---|---|
| `00-resumen.tex` | L13 (Resumen), L29 (Abstract) | Una frase cada uno | Quitar; reacomodar sin superar 250 palabras |
| `01-introduccion.tex` | L38 (§1.4, eficiencia, `tab:gemini-solo`), L66 (§1.7) | Parcial | Acotar eficiencia (D4); quitar la validacion fuera de muestra de la contribucion. L72/L76 (§1.8) quedan coherentes: verificar |
| `04-marco-metodologico.tex` | L60 `\paragraph{Corpus independiente de validacion}` | Total | Borrar |
| | L48, L88 ("un solo corpus congelado") | — | Verificar que siguen exactas |
| | L113 (linea de base), L117 (sensibilidad a la referencia, kappa 0,6055), L119 (sesgo del vocabulario), L123 (diseno fuera de muestra) | Total | Borrar |
| | L115 (calibracion) | Parcial | Quitar la parte "por corpus"/fuera de muestra |
| | L121 (brazo de modelo solo) | Parcial | Describir solo el bloque dentro de la muestra como descriptivo (D4) |
| | L127 ("ocho amenazas"), L141 (septima), L143 (octava) | Parcial/total | Borrar 7.a y 8.a; "ocho" pasa a "seis"; verificar ordinales |
| `05-arquitectura.tex` | L68 ("cerca de un tercio de las llamadas") | Parcial | Re-anclar al bloque dentro de la muestra (69/200) como dato descriptivo o quitar |
| `11-aspectos-legales.tex` | L48 (consentimiento de E3/E4/E5) | Total | Borrar (compuerta P8 para los documentos del repositorio) |
| | L30 ("119 textos y 81 audios") | Verificacion | Corregir segun compuerta P4 (D3.3) |
| `07-resultados.tex` | L6 ("doce apartados") | Parcial | Recontar y reenumerar |
| | §8.4: L222, filas L235-236 de `tab:calibracion-gate`, L240, L243, L245, L247, L249, L251 | Parcial | Quitar filas y frases fuera de muestra; conservar la lectura dentro de la muestra (69 casos, AUROC 0,5168) |
| | §8.6 L277-320 (`subsec:sesgo-corpus-referencia`, `tab:sesgo-vocabulario`, `tab:sesgo-subconjuntos`) | Total | Borrar |
| | §8.9 L387-450 (`subsec:validacion-fuera-muestra`, `tab:fuera-de-muestra`, `tab:fuera-de-muestra-clases`) | Total | Borrar |
| | §8.10 L452-521: linea de base L454-496 (`tab:linea-base-clasica`, `tab:robustez-linea-base`) | Total | Borrar |
| | §8.10 contraste de modelo solo L499-521, `tab:gemini-solo` | Parcial | Quitar la fila "Primario (fuera de muestra)" (L511) y su prosa (L519); conservar la fila de 200 como descriptiva (D4); decidir si la subseccion `subsec:comparacion-alternativas` se renombra o se funde |
| | §8.12 L556-585 (`subsec:ruido-referencia`, `tab:ruido-referencia`) | Total | Borrar |
| `08-discusion.tex` | L8, L10, L20, L28, L40 | Parcial | Quitar cifras y lecturas fuera de muestra; L28 (clase `Sistemas`) pasa a las cifras dentro de la muestra |
| | §9.3 L46 ("nueve limitaciones"), L56 (quinta, linea de base), L60 (septima), L62 (octava), L66, L68 | Parcial/total | Reescribir quinta y octava sin el corpus retirado; borrar L66 y L68; agregar en la septima (o donde corresponda) una unica remision a la nota de versiones; recontar |
| | §9.5 L119, L125 | Parcial | Quitar solo la sensibilidad con la tasa fuera de muestra (el resto de §9.5 es de `c-236`) |
| `09-conclusiones.tex` | L6, `tab:cumplimiento-objetivos` filas L24 (OE2) y L28 (OE6), L37, L47 | Parcial | Quitar cifras fuera de muestra; acotar eficiencia (D4) |
| `10-recomendaciones.tex` | L6 (intro), L10, L14, L18 (`subsec:frontera-sistemas`), §11.5 `subsec:corpus-independiente` L24-26, L38 | Parcial | Reescribir §11.5 como trabajo futuro con procedencia acreditable (requisito ADDED); L18 pasa a cifras dentro de la muestra; L14 acota eficiencia |
| `12-anexos.tex` | Anexo A L52 y `fig:cronograma` (`docs/diagrams/cronograma.md`) | Parcial | Retirar o rotular como retirados los hitos de noviembre de la validacion |
| | Anexo H L225 | — | Queda coherente: verificar |
| | Anexo I.1 L233-235 (`subsec:nota-versiones`) | Aditivo | Declaracion de procedencia (D3) |
| | Anexo J L245 (intro, "secciones 3.31, 3.33, 3.35 y 3.36"), L291-311 (3.35), L313-334 (3.36) | Parcial/total | Borrar los dos parrafos y ajustar la intro |

Falsos positivos de la busqueda (no se tocan): `03-estado-del-arte.tex` L8, L30, L46, L58, L64 ("arbitrada" = literatura con referato). Los capitulos 2 (TF-IDF, regresion logistica, Brier, AUROC) y el glosario se tratan en OQ7.

### D3 — Declaracion de procedencia: donde, que y con que respaldo

1. **Lugar:** el Anexo I.1 (`subsec:nota-versiones`, `12-anexos.tex:233-235`), a continuacion del parrafo de N-02, con la misma estructura: que se informo, en que versiones, por que se retira, que lo reemplaza. **Alternativa descartada:** una seccion nueva en el cuerpo; el precedente N-02 muestra que la nota de versiones es el lugar que el tribunal reconoce, y el cuerpo solo necesita **una** remision (D3.4).
2. **Contenido minimo (plantilla; la redaccion final es compuerta):** (a) las versiones 1.3.0 a 1.5.2 incluyeron una validacion fuera de muestra sobre 150 casos mas 56 de refuerzo, etiquetados por `E3`/`E4` y arbitrados por `E5`, y los analisis que dependian de ella (linea de base clasica, bloque primario del brazo de modelo solo, calibracion fuera de muestra, sensibilidad a la referencia, sesgo del vocabulario, arbitraje por mayoria); (b) esa evidencia se retira; (c) por que: su procedencia no puede acreditarse como registro primario y los textos no eran incidentes extraidos de una organizacion sino descripciones genericas de incidentes (confirmado por un autor); (d) lo que los autores confirmen sobre como se produjeron las etiquetas y las marcas temporales, **o** la declaracion de que no puede acreditarse, sin conjeturar; (e) si las cifras retiradas se mencionan (como hizo N-02 con 165,3 s y 92 %) o no (OQ4).
3. **§7.3 (L30):** la frase "119 textos y 81 audios" describe lo que llego al proveedor. Si los textos del corpus retirado se enviaron a la Gemini API (corridas del 12 y el 13-11 y brazo de modelo solo, segun el tribunal), la frase debe decir tambien eso, con la naturaleza de esos textos que los autores confirmen (descripciones genericas, sin datos personales). No se resuelve "haciendo exacta" la frase por omision: la nota de versiones o §7.3 declara la transferencia adicional. Redaccion final: compuerta P4.
4. **Remision en el cuerpo:** una sola, en §9.3 (limitacion de las metricas dentro de la muestra, L60) o en §4.4, del tipo "no se dispone de validacion fuera de muestra; la que se informo en versiones anteriores se retiro (\autoref{subsec:nota-versiones})". Evita que el retiro sea silencioso sin repetir el motivo.
5. **Regla de honestidad:** ninguna frase factual sobre como se produjeron los datos se escribe sin la respuesta registrada de los autores (tabla de compuertas en `dictamen-correcciones.md`). El retiro MUST NOT atribuirse a extension, legibilidad u otra causa que no sea la procedencia.

### D4 — Hipotesis subsidiaria de eficiencia (M-02): "sin contraste limpio"

Sin el bloque primario de 103 casos, el unico bloque es el de 200 casos dentro de la muestra, que el propio texto rotula "no limpio y optimista" (ajustes con el mismo corpus; 112 casos reintentados despues de ver los resultados). Se adopta:

- **Estado:** "sin contraste limpio" (no "contrastada: no concluyente", no "confirmada", no "refutada"). La etiqueta exacta es OQ5; el requisito MODIFIED fija la por defecto.
- **Bloque de 200:** se conserva en `tab:gemini-solo` como **descriptivo**, con la desviacion declarada y sin aplicar la regla de tres vias como veredicto (opcion recomendada, OQ3). La razon de llamadas (cerca de un tercio de los casos invocan al modelo) es un dato de la arquitectura y no depende de las etiquetas.
- **Alternativas:** (a) quitar `tab:gemini-solo` entero y declarar la hipotesis sin contrastar: mas austero, pierde un dato descriptivo honesto; (b) medir el brazo sobre otro corpus: fuera de alcance (sin datos acreditables, sin llamadas pagas). La medicion queda como trabajo futuro (§11.5).
- Anclas: `01:38`, `04:121`, `05:68`, `07:499-521`, `08:10`, `09:6`, `09:37`, `09:47`, `10:14`.

### D5 — Linea de base clasica: retiro sin sustituto

La linea de base se entreno con los 200 casos de ajuste y se probo sobre el corpus retirado; no existe una prueba limpia alternativa (probarla sobre los 200 seria evaluar sobre el entrenamiento). Se retira completa (`04:113`, `07:454-496`, `08:56`, Anexo J 3.36) y la comparacion pasa a trabajo futuro. TLB-04 se modifica para que la tesis no la niegue de forma plana: se declara realizada y retirada en la nota de versiones.

### D6 — Calibracion (§8.4): se conserva la lectura dentro de la muestra

La regla prerregistrada ya elegia solo con los 200 casos de ajuste (L247). Se quitan las filas L235-236 y las frases fuera de muestra (L222, L240, L243, L245, L247, L249, L251); la conclusion (AUROC 0,5168, ningun umbral sostenido) no cambia. `10:10` deja de pedir confirmacion "en un corpus independiente" como hecho y la conserva como trabajo futuro.

### D7 — Artefactos del repositorio: conservar y re-rotular (recomendado) frente a eliminar

| Opcion | Pros | Contras |
|---|---|---|
| **A. Conservar y re-rotular (por defecto)** | No toca bytes hasheados ni pruebas; CI verde; cumple "ninguna correccion exige codigo nuevo"; deja la historia auditable; los textos, segun los autores, no son datos de terceros | El repositorio publico sigue alojando material retirado (rotulado) |
| B. Eliminar | El repositorio deja de alojarlos en la punta | Rompe `test_linea_de_base.py`, `test_calibracion_gate.py` (L396-399), `test_monitor_deriva.py` (L203-226) y `SHA256SUMS.txt`; exige editar pruebas y el monitor de deriva (codigo); la historia de git los conserva igual (quitarlos de la historia exige reescribirla, fuera de alcance) |

El re-rotulado (requisito ADDED OOS-026) se hace en `evaluation/data/campana/README.md` (secciones de c-191 L99, c-206 L180, c-166 L228 y la referencia in-sample L298), `evaluation/data/canario/README.md`, `docs/operational-guide.md:842`, `docs/campana-medicion/runbook-corpus-independiente.md`, `runbook-arbitraje-discordantes.md` y `knowledge-base/11_evaluacion_experimental.md`: material retirado de la tesis (c-235), no evidencia, procedencia no acreditada como registro primario; las frases "del organismo" o "compania financiera" se corrigen solo con lo que confirmen los autores. **La eleccion es de los autores (OQ2).** El canario de deriva (103 casos `I*`) puede seguir operando como insumo tecnico, rotulado como sin referencia acreditada (OQ6).

### D8 — Politica de deltas de specs

- **REMOVED** cuando el requisito exige contenido que deja de existir (20 en `tesis-document`, 3 en `tesis-dictamen-v1-3-0`, 4 en `tesis-baseline-integration`), con **Reason** y **Migration** que remiten a los requisitos ADDED.
- **MODIFIED** cuando el requisito sigue vigente y solo una clausula depende del corpus retirado (7 en `tesis-document`, 1 en `tesis-dictamen-v1-3-0`, TLB-04, 1 en `tesis-numeros-canonicos`).
- **Sin tocar, por compatibles:** "Cierre de los items (a) a (e)..." y "Secuencia temporal de la fila Lim. ..." (ya declaran la validacion fuera de muestra como limitacion negativa); "Trazabilidad y alcance del baseline TF-IDF+SVM" (la comparacion "pendiente" vuelve a ser cierta); "Grados de cumplimiento..." y "Subseccion de resultados de la campana de medicion" (menciones condicionales); los registros historicos del memo con estados en `{vigente, retirado, condicional}`; `tesis-baseline-comparison` (LB-201..203, borrador dentro de `c-210`); las specs de codigo (`evaluation-out-of-sample-validation` OOS-001..025, `discordant-arbitration`, `evaluation-linea-de-base-clasica`, `gemini-solo-arm`, `evaluation-reference-noise-sensitivity`, `evaluation-corpus-bias-mitigation`, `model-drift-monitoring`), porque el codigo queda; `tesis-defensa` (Anexo de respuestas), que trata `c-239`.
- **Coordinacion con `c-236`:** este change MODIFICA "Balance neto entre el ahorro de registro y el costo de las derivaciones erroneas" solo en la clausula y el escenario de la sensibilidad mixta de c-221; `c-236` debe proponer su delta sobre el texto que resulte de archivar este change.

### D9 — Sincronizacion documental (marcar, no borrar historia)

- `numeros-canonicos.md`: seccion aditiva en el primer numero libre (esperado `3.45`; `3.39`-`3.42` reservadas a `c-230`/`c-229`/`c-228`/`c-232`; `3.43` y `3.44` ocupadas). Pasa a `retirado`, por upsert y sin borrar cifras, cada valor de las secciones `3.19`, `3.20`, `3.22`, `3.23`, `3.25`, `3.26`, `3.27`, `3.30`, `3.32`, `3.34`, `3.35`, `3.36` y la parte fuera de muestra de `3.14`, `3.21` (acuerdo y kappa `E3`/`E4`), `3.24`, `3.28` (bloque primario) y `3.33` (sensibilidad), a verificar en la tarea correspondiente. El bloque dentro de la muestra de `3.28` conserva `condicional`.
- `dictamen-correcciones.md`: entrada del change con filas K-01 (retiro), K-02 (sin datos de terceros, segun autores; §7.3 y §7.5), A-02 y B-02 ("no aplica por retiro"), M-02 (conclusion acotada), mas la tabla de compuertas con las respuestas de los autores y su fecha.
- `knowledge-base/11_evaluacion_experimental.md`, runbooks de `docs/campana-medicion/` y `confirmacion-posterior-consentimiento.md`: marcado como retirado; afirmaciones de procedencia y consentimiento solo segun compuertas P1-P8.
- Extractos `tesis_para_agente.md`, `tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt`: regenerar con `build_tesis_para_agente.py` al final del change; si depende del PDF recompilado, queda en `c-239`.

### D10 — Changes activos con premisas retiradas

`c-228` (clasificador supervisado sobre el corpus acumulado), `c-229` (muestreo probabilistico), `c-230` (referencia por mayoria con etiquetadores independientes) y `c-232` (integrar el supervisado) citan `0,6893` o los 206 casos como linea de partida. No se editan aqui. Una tarea registra, por cada uno, la decision de los autores: **reformular** (cambiar la premisa al corpus de 200 casos) o **archivar sin aplicar**. `c-229` interesa ademas como remedio empirico declarado en las conclusiones por `c-234`.

### D11 — Gobernanza y red de seguridad

Gobernanza **ALTA**: declaraciones de procedencia y posible retiro de artefactos publicados. CHECKPOINTS de autores: antes de la nota de versiones, §7.3, §7.5 y READMEs (P1-P8); antes de cualquier borrado de archivos (OQ2); antes de cerrar el estado de la hipotesis de eficiencia (OQ5). TDD estricto no aplica (no hay logica nueva). Red de seguridad: `verify_citations.py` (`STATUS: PASS`), bateria de `rg` sobre cifras, alias y etiquetas retiradas, compilacion de verificacion en un directorio temporal (sin versionar el PDF), `pytest` de `evaluation/` verde (sin cambios de codigo) y `sha256sum -c` de las sumas fijadas.

### D12 — Paginas

El retiro reduce paginas. El conteo de entrega lo registra `c-239` tras la recompilacion; este change anota en su entrada de `dictamen-correcciones.md` el conteo de la compilacion de verificacion como provisorio.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [Texto factual sin confirmar] → acusacion de nueva fabricacion | D3.5; compuertas P1-P8 registradas antes de escribir; frases condicionales prohibidas como sustituto de una respuesta |
| [Retiro silencioso] → el tribunal lo lee como ocultamiento | Nota de versiones con motivo (D3.2) y remision unica desde el cuerpo (D3.4) |
| [Referencias colgantes] | Lista cerrada de etiquetas retiradas; `rg` de `\autoref`/`\ref`; compilacion de verificacion |
| [Conteos] "doce apartados", "ocho amenazas", "nueve limitaciones", intro del Anexo J | Tareas de recuento explicitas con su verificacion |
| [Resumen sobre el tope] | Conteo con la regla de c-106 (250 palabras) |
| [Eliminar rompe CI] | Opcion A por defecto (D7) |
| [Conflicto de specs con `c-236`] | D8; `c-236` se propone sobre el texto resultante |
| [Afirmaciones del consentimiento de E3/E4/E5 en documentos del repositorio no sostenibles] | Compuerta P8; correccion solo con respuesta de autores |
| [Memo con cifras retiradas que la tesis siga citando] | Cruce `rg` entre la seccion de retiro y `sections/*.tex` |

## Migration Plan

1. Linea base y compuertas de autores (grupos 0 y 1). Sin respuestas, solo se ejecutan los retiros que no requieren texto factual nuevo (grupos 2 a 5).
2. Retiro en capitulos 4, 8, 9, 10, 11, 1, 5, Resumen y Anexos (grupos 2 a 6).
3. Declaracion de procedencia y §7.3/§7.5 (grupo 6, bloqueado por compuertas).
4. Referencias, conteos, bibliografia y compilacion de verificacion (grupo 7).
5. Memo, registro, KB, runbooks, READMEs (grupos 8 y 9).
6. Verificacion de cierre (grupo 10).

Rollback: `git revert` del commit de contenido; los artefactos de datos no cambian por defecto; una eventual eliminacion (opcion B) va en commit separado.

## Open Questions

Preguntas a los autores (compuertas; alineadas con las preguntas 1 a 5 de la Seccion 8 de la devolucion):

- **P1:** ¿Quienes son `E3`, `E4` y `E5` respecto de los autores y de cualquier organizacion? ¿Son personas distintas de los autores? ¿Etiquetaron efectivamente los casos? ¿Como registraron el inicio y el fin de cada caso?
- **P2:** ¿Por que todas las duraciones caen entre 30 y 90 s y ninguna pausa supera los 8 s? ¿Las marcas temporales se registraron, se reconstruyeron o se generaron? ¿Y las etiquetas?
- **P3:** ¿Quien redacto los 56 casos de refuerzo (I151-I206), cuando y con que medio (incluido, si corresponde, un asistente de IA; coordinar con `c-237`)?
- **P4:** ¿Quien redacto los 150 textos "originales" y con que medio? ¿Los nombres de sucursal y el "sistema principal" refieren a una organizacion real? Confirmar que no contienen datos personales ni de terceros y que se enviaron a la Gemini API (corridas del 12 y el 13-11 y brazo de modelo solo), para la redaccion de §7.3.
- **P5:** ¿Quien asigno los sectores a los textos y con que criterio? (Pregunta 5 del tribunal; con el retiro deja de exigir una correspondencia de taxonomia, pero la respuesta informa la nota.)
- **P6:** ¿Hubo alguna parte de la descripcion de `04:60` (compania financiera; 2-11-2025 a 12-2-2026) que fuera cierta? ¿Que frase la reemplaza en la nota?
- **P7:** ¿Con que redaccion exacta aprueban la nota de versiones (D3.2)? ¿Mencionan las cifras retiradas, como N-02, o no (OQ4)?
- **P8:** ¿Que es cierto de `docs/campana-medicion/confirmacion-posterior-consentimiento.md` y de las filas `E3`, `E4`, `E5` de `evaluation/data/campana/registro_sujetos.csv` (informacion verbal del 12-11, firma del 13-11, originales en poder del director)? Si no se sostiene, ¿como se corrige?

Decisiones abiertas:

- **OQ2 (autores):** artefactos: conservar y re-rotular (A, recomendado) o eliminar (B). Por defecto A.
- **OQ3 (autores):** conservar en `tab:gemini-solo` la fila de 200 casos como descriptiva (recomendado) o retirar la tabla.
- **OQ4 (autores):** mencionar o no las cifras retiradas en la nota de versiones (con N-02 se mencionaron).
- **OQ5 (autores):** etiqueta del estado de la hipotesis de eficiencia; por defecto "sin contraste limpio". Si cambia, se actualiza el delta antes de aplicar.
- **OQ6 (autores):** el canario de deriva sigue operando como insumo tecnico rotulado, o se reemplaza en un change posterior.
- **OQ7 (aplicacion/autores):** si el marco teorico (§2: TF-IDF, regresion logistica) y el glosario conservan esos terminos tras retirar la linea de base; Brier y AUROC siguen en uso por la calibracion dentro de la muestra. `verify_citations.py` decide sobre las entradas sin cita.
- **OQ8 (autores):** `c-228`, `c-229`, `c-230`, `c-232`: reformular o archivar (D10).
- **OQ9 (aplicacion):** si `subsec:comparacion-alternativas` se conserva con solo el bloque descriptivo del modelo solo o se funde en otra subseccion; fijar el nuevo cardinal de apartados del capitulo 8.
