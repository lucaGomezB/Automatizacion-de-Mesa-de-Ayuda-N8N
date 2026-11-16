# Proposal: Retirar la validacion fuera de muestra y declarar su procedencia

## Why

La **devolucion de tercera instancia** del tribunal sobre la tesis **v1.5.2** (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`, 16-11-2026, 6,7/10) dictamino **apta para defensa condicionada a K-01 y K-02**: no se fija fecha hasta que el grupo acredite la procedencia del corpus fuera de muestra o lo **retire del ejemplar con todo lo que depende de el** (Seccion 2 y Seccion 5, K-01, opcion 2). El tribunal no afirma que los datos sean inventados; afirma que, tal como estan versionados, no pueden aceptarse como el registro primario que la tesis describe (marcas temporales de `E3`/`E4`/`E5` con duraciones en [30, 90] s y pausas enteras de 1 a 8 s; casos de refuerzo con forma de catalogo; cronologia del 12 y el 13-11).

**Decision de los autores (2026-11-16): K-01 se resuelve por RETIRO.** Insumo de un autor sobre K-02: las descripciones del corpus independiente son **descripciones genericas de incidentes, no incidentes extraidos de la compania**; por lo tanto la descripcion de `04-marco-metodologico.tex:60` (150 casos de una compania financiera, 2-11-2025 a 12-2-2026) no es exacta y no hay datos de una tercera organizacion que requieran autorizacion. Todavia **no se sabe** como se produjeron las etiquetas y las marcas temporales de `E3`/`E4`/`E5`: esa respuesta es una **compuerta de autores**.

El retiro debe hacerse **sin ocultar por que se retira**: siguiendo el precedente de N-02 (corpus sintetico de julio declarado en la nota de versiones, que el tribunal valoro como honestidad), el Anexo I.1 declarara que las versiones 1.3.0 a 1.5.2 incluyeron una validacion fuera de muestra, que se retira y por que.

## What Changes

| Bloque | Que cambia | Observaciones que cierra | Gobernanza |
|---|---|---|---|
| **A. Compuertas de autores** | Antes de escribir cualquier texto factual o de borrar cualquier artefacto, los autores responden las preguntas de procedencia (alineadas con las preguntas 1 a 5 de la Seccion 8 de la devolucion) y fijan las decisiones abiertas (redaccion de la nota de versiones, destino de los artefactos, bloque dentro de la muestra del brazo de modelo solo, changes activos afectados) | K-01, K-02 (precondicion) | **ALTA** |
| **B. Retiro del ejemplar** | Se retira de la tesis toda cifra, tabla, seccion y afirmacion que dependa del corpus fuera de muestra: §8.6, §8.9 y §8.12 completos; la linea de base clasica de §8.10; el bloque primario del brazo de modelo solo; las filas fuera de muestra de §8.4; §4.4 (corpus independiente), cuatro parrafos de §4.7 y dos amenazas de §4.8; las frases del Resumen, el Abstract, §1.4, §1.7, §5, §7.5, §9, §10 (Tabla 31), §11; los hitos del cronograma (Anexo A) y dos apartados del Anexo J. Se corrigen conteos ("doce apartados", "ocho amenazas", "nueve limitaciones") y referencias colgantes. **BREAKING** respecto de v1.5.2: desaparecen etiquetas LaTeX y cifras publicadas | K-01 (opcion 2), A-02 y B-02 (no aplican por retiro) | ALTA |
| **C. Declaracion de procedencia** | El Anexo I.1 (nota de versiones) declara que las versiones 1.3.0 a 1.5.2 incluyeron la validacion fuera de muestra y los analisis que dependian de ella, que se retira y por que (procedencia no acreditable como registro primario; textos que no eran incidentes extraidos de una organizacion). §7.3 queda exacta respecto de lo que se envio al proveedor; §7.5 pierde el parrafo de `E3`/`E4`/`E5`. Toda frase sobre etiquetas y marcas temporales espera la respuesta de los autores | K-01, K-02 | **ALTA** |
| **D. Eficiencia acotada (M-02)** | Sin bloque primario, la hipotesis subsidiaria de eficiencia queda **sin contraste limpio**: el bloque de 200 casos se informa como descriptivo, con su desviacion declarada (112 reintentos decididos despues de ver los resultados; ajustes con el mismo corpus). Afecta `01:38`, `04:121`, `05:68`, `08:10`, `09:6/37/47`, `10:14` | M-02 | MEDIA |
| **E. Artefactos y documentos del repositorio** | Por defecto se **conservan** los artefactos de `evaluation/data/campana/` y `evaluation/data/canario/` sin tocar bytes fijados por SHA-256, y se **re-rotulan** a nivel README y runbook (material retirado de la tesis, no evidencia, procedencia no acreditada). La eliminacion es alternativa sujeta a decision de autores. Se sincronizan el memo canonico (seccion aditiva de retiro), el registro de correcciones, la KB y los runbooks | K-02 (publicacion), coherencia | ALTA |

Fuera de alcance: recompilar el PDF de entrega, bump y tag (`c-239`); balance neto y umbral (`c-236`, salvo quitar de §9.5 la sensibilidad con la tasa fuera de muestra); declaracion de IA (`c-237`); legibilidad (`c-238`); `docs/defensa/respuestas-tribunal.md` (`c-239`). Este change **no escribe codigo**, no mide de nuevo y no hace llamadas a Gemini.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se REMUEVEN los requisitos que exigen contenido fuera de muestra (reporte, tablas, sensibilidad a la referencia, sesgo de corpus, arbitraje por mayoria, robustez de la brecha, resumen con evidencia fuera de muestra, entre otros); se MODIFICAN los que la mencionan de forma parcial (contraste y estado de la hipotesis de eficiencia, consistencia interna, procedencia de los ajustes, afirmaciones acotadas, version entregada, balance neto); se AGREGAN el retiro del ejemplar, la declaracion de procedencia en la nota de versiones y la validacion fuera de muestra como trabajo futuro con procedencia acreditable.
- `tesis-dictamen-v1-3-0`: se REMUEVEN los tres requisitos de la validacion fuera de muestra y del consentimiento de `E3`/`E4`; se MODIFICA el de conclusiones y resumen acotados (veredicto de eficiencia).
- `tesis-baseline-integration`: se REMUEVEN TLB-01, TLB-02, TLB-03 y TLB-05 (la linea de base se probo sobre el corpus retirado) y se MODIFICA TLB-04 (ninguna negacion plana de la comparacion: se declara realizada y retirada).
- `tesis-numeros-canonicos`: se AGREGA el registro aditivo del retiro (estados `retirado` por upsert, sin borrar cifras) y se MODIFICA el registro de la robustez de la linea de base (deja de exigir el estado `vigente (nuevo)`).
- `evaluation-out-of-sample-validation`: se AGREGA el rotulado de los artefactos retirados de la tesis (README y runbooks), sin alterar bytes hasheados ni el codigo; las especificaciones de codigo se conservan porque el codigo queda.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex`, `01-introduccion.tex`, `04-marco-metodologico.tex`, `05-arquitectura.tex`, `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex`, `11-aspectos-legales.tex`, `12-anexos.tex` | Modificado (retiro) | Ver inventario en `design.md` (D2) |
| `docs/diagrams/cronograma.md` y `fig:cronograma` | Modificado | Hitos de la validacion fuera de muestra retirados o rotulados |
| `docs/Tesis/v10 (IA)/Bibliography_base.bib` | Posible | Entradas que queden sin cita (`verify_citations.py`) |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion de retiro (primer numero libre; esperado `3.45`), estados `retirado` por upsert |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada del change y filas K-01, K-02, A-02, M-02, B-02 |
| `knowledge-base/11_evaluacion_experimental.md`, `docs/campana-medicion/runbook-*.md`, `docs/campana-medicion/confirmacion-posterior-consentimiento.md` | Modificado | Marcado como retirado, sin borrar historia; afirmaciones de procedencia segun compuerta |
| `evaluation/data/campana/README.md` (L99-258 y afines), README del canario | Modificado (texto) | Re-rotulado; bytes de los datos intactos |
| `evaluation/data/campana/*independiente*`, `*arbitrad*`, `arbitraje_tres_vias.json`, `analisis/*`, `evaluation/data/canario/canario.json` | Sin cambio por defecto | Borrarlos rompe `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py` (L396-399), `evaluation/monitoreo/test_monitor_deriva.py` (L203-226) y `analisis/SHA256SUMS.txt` |
| Extractos `tesis_para_agente.md`, `tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt` | Regeneracion | Con `build_tesis_para_agente.py`; la regeneracion final puede quedar en `c-239` |
| Changes activos `c-228`, `c-229`, `c-230`, `c-232` | **Impacto, no se tocan** | Anclan premisas en `0,6893` o en los 206 casos; decision de autores: reformular o archivar |
| `c-236` | Coordinacion | Este change quita de §9.5 la sensibilidad fuera de muestra (L119, L125) y modifica el requisito del balance solo en esa clausula; `c-236` construye sobre ese texto |

Sin cambios en `App/`, `n8n/`, el clasificador, el corpus congelado de 200 casos ni sus cifras canonicas (`61,6 s`, `17,76 s`, `W = 363`, `73,5 %`, `0,6508`, `110/138`). Cero llamadas a Gemini.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Redactar la procedencia con hechos no confirmados por los autores | Media | Compuertas de autores (grupo 1 de `tasks.md`); toda frase factual se escribe solo con la respuesta registrada en `dictamen-correcciones.md` |
| Redactar el retiro de modo que oculte su motivo | Media | Requisito ADDED con escenario "motivo no ocultado"; precedente N-02; revision de la nota por los autores |
| Referencias colgantes o conteos desactualizados tras borrar secciones | Alta | Bateria de `rg` sobre etiquetas y cardinales; compilacion de verificacion en un directorio temporal; `verify_citations.py` |
| Romper CI al borrar artefactos | Alta si se borra | Opcion por defecto: conservar y re-rotular sin tocar bytes; la eliminacion queda como decision de autores con ajuste de pruebas |
| Conflicto de specs con `c-236` sobre el balance neto | Media | Este change toca solo la clausula de la sensibilidad fuera de muestra; `c-236` se propone sobre el texto resultante |
| Changes activos con premisas retiradas | Alta | Se registran como impacto con una tarea de decision; no se editan aqui |
| Afirmaciones previas del consentimiento de `E3`/`E4`/`E5` que no se sostengan | Media | Compuerta P8; se corrige el registro solo con la respuesta de los autores |

## Rollback Plan

`git revert` del commit de contenido: las ediciones de `.tex` son eliminaciones y sustituciones textuales sobre v1.5.2 (tag `v1.5.2`); el memo y el registro son aditivos; los artefactos de datos no se modifican por defecto. Si los autores eligieran eliminar artefactos, esa eliminacion iria en un commit separado para revertirla de forma independiente.

## Dependencies

- **Precondicion dura:** respuestas de los autores a las compuertas del grupo 1 de `tasks.md` antes de escribir la nota de versiones, §7.3, §7.5 y cualquier README con afirmaciones de procedencia.
- Este change se aplica **primero** del conjunto `c-235` a `c-239`; `c-236` (balance), `c-237` (IA), `c-238` (legibilidad) y `c-239` (cierre, recompilacion, tag) dependen de su resultado.
- Afecta, sin modificarlos, a `c-228`, `c-229`, `c-230` y `c-232`.

## Success Criteria

- [ ] Ningun archivo de `sections/*.tex` contiene cifras, tablas, secciones ni afirmaciones del corpus fuera de muestra, salvo la declaracion de retiro en la nota de versiones (y, si los autores lo deciden, sus cifras rotuladas como retiradas).
- [ ] Cero referencias indefinidas y conteos coherentes (apartados del capitulo 8, amenazas de §4.8, limitaciones de §9.3) en una compilacion de verificacion.
- [ ] La nota de versiones declara que v1.3.0 a v1.5.2 incluyeron la validacion, que se retira y por que, con cada frase factual respaldada por una respuesta registrada de los autores.
- [ ] La hipotesis subsidiaria de eficiencia figura como "sin contraste limpio" de forma coherente en todos los capitulos.
- [ ] Los artefactos del repositorio estan rotulados como retirados de la tesis, con bytes hasheados intactos y CI verde (o eliminados por decision registrada de los autores, con CI verde).
- [ ] `openspec validate c-235-retirar-la-validacion-fuera-de-muestra-y-declarar-su-procedencia --strict` pasa.
