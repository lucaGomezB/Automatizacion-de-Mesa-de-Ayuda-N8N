## Context

Ver `proposal.md` - Why para la evidencia y la motivacion. En sintesis: el repositorio publico contradice tres afirmaciones del manuscrito y de su documentacion de soporte. Los commits que las contradicen estan en el historial (`1368fd8` c-71, `a76851e` c-72, `d6bb474` c-74) y el directorio `docs/prompt_gemini_history/` nunca existio.

Restricciones que enmarcan el enfoque:

- **Numeros canonicos congelados** (`openspec/specs/tesis-numeros-canonicos/spec.md`): este change NO recalcula ni cambiar ningun valor.
- **Regla dura de gobernanza documental**: la memoria de Engram se versiona en un repositorio publico y es evidencia de auditoria; la tesis no puede contradecirla.
- **Solapamiento declarado** con c-130 y c-142 (PR #40 sin fusionar); ver la seccion de reconciliacion del proposal.
- **Sin datos nuevos**: no existe ningun corpus de preproduccion que versionar.

## Goals / Non-Goals

**Goals:**

- Reemplazar la afirmacion de no fuga (filtro, prompt, punto de operacion) por una declaracion de procedencia verificable.
- Declarar que no se dispuso de un corpus independiente de preproduccion y registrar el resultado del checkpoint como "no existen / no se localizan".
- Corregir la ubicacion de las versiones historicas del prompt al historial de versiones de `docs/prompt_gemini.txt`.
- Alinear `evaluation/README.md` con la procedencia factual.
- Remitir la validacion sobre un corpus independiente a las lineas de trabajo futuro.
- Registrar la reconciliacion con c-130 y c-142 sin duplicar requisitos.

**Non-Goals:**

- No se crea `docs/prompt_gemini_history/` (D2).
- No se recolecta, pseudonimiza ni etiqueta ningun conjunto de preproduccion (seria un change de gobernanza HIGH propio).
- No se re-mide el clasificador, no se re-deriva `tau` ni se toca el vocabulario, el prompt o el codigo.
- No se ejecuta el analisis de sensibilidad de c-142 ni se agrega su subseccion ni su tabla.
- No se cambia ningun valor numerico, rotulo ni la conclusion de ningun analisis.

## Decisions

### D1 - Declarar procedencia en lugar de garantizar la ausencia de fuga

Las afirmaciones de "sin acceso al corpus", "sin exposicion al corpus", "datos no vistos" y "separacion estricta" pasan a ser una declaracion de procedencia: el vocabulario (c-71), las reglas de frontera del prompt (c-72) y el punto de operacion (c-74) se derivaron del corpus de validacion. Se acota expresamente la mitigacion fuera de muestra de c-74 (validacion cruzada de cinco pliegues para el umbral) y se declara que esa mitigacion NO cubre el vocabulario ni las reglas del prompt, que se fijaron sobre el corpus completo. Las metricas de clasificacion se califican como estimaciones dentro de la muestra, probablemente optimistas.

**Alternativas descartadas:** (a) conservar "garantia metodologica" y matizarla: el repositorio la desmiente de forma verificable y el dictamen la contradice; (b) eliminar toda mencion al tema: un evaluador que contrasta la tesis con el codigo encontraria la contradiccion igual y se perderia la trazabilidad de la procedencia.

### D2 - NO crear `docs/prompt_gemini_history/`

El texto remite a un directorio que nunca existio. La correccion es del TEXTO, no del repositorio: adaptar el repositorio al texto (creando el directorio con copias del prompt) fabricaria un artefacto historico artificial y duplicaria el historial de git, que ya es la fuente de verdad (`git log -- docs/prompt_gemini.txt`). Se declara la ubicacion real y se remite al historial de versiones.

**Alternativas descartadas:** (a) crear el directorio: invierte la relacion entre evidencia y afirmacion, y las copias no tendrian la autoridad del historial de git; (b) mantener la remision y anotar el error: deja una referencia inexistente publicada.

### D3 - Correccion documental, sin codigo ni datos

El change edita unicamente `.tex`, `.md` de documentacion de soporte y el render generado. No toca `App/`, `n8n/`, el corpus, las caches ni `docs/prompt_gemini.txt`. La verificacion es por `rg`/`grep`, recompilacion del PDF, regeneracion del render y `openspec validate --strict`, no por tests de software. No aplica modo TDD estricto (no hay codigo nuevo).

### D4 - Reconciliacion con c-130 y c-142

c-144 aplica sobre `main` lo que c-130 (D9) y c-142 (D11/D13/T08) aplican sobre el PR #40. Para no duplicar en silencio:

- c-144 nombra sus requisitos de `tesis-document` y `evaluation-framework` con los MISMOS nombres que usa PR #40 (`Procedencia declarada de los ajustes realizados sobre el corpus de validacion`, `Ubicacion veraz de las versiones historicas del prompt en el Anexo H`, `Advertencia metodologica del framework coherente con el historial`), de modo que la deduplicacion al fusionar sea mecanica.
- **c-144 es la fuente canonica**: al fusionar PR #40, los bloques `## ADDED Requirements` de esos tres requisitos en c-130 y c-142 se eliminan o se convierten en no-op.
- c-130 conserva su definicion de magnitudes por etapa, el alcance del gate y el criterio de cortocircuito; c-142 conserva su analisis de sensibilidad completo. El change c-144 NO absorbe ninguno de esos contenidos.
- Si el autor prefiere rebasar c-144 sobre el PR #40 y deduplicar alli, es valido; lo que no puede ocurrir es que queden dos requisitos vigentes para la misma conducta.

**Alternativa descartada:** nombrar los requisitos de c-144 de forma distinta para evitar el choque de nombres. Produciria dos requisitos vigentes que cubren la misma conducta y traslada la ambiguedad al archivado.

## Objetivos de propagacion (ANTES -> DESPUES)

Las rutas `sections/` se resuelven desde `docs/Tesis/v10 (IA)/paper/`. Los textos DESPUES son carga util LaTeX/markdown y llevan la acentuacion normativa del manuscrito. No se modifica ningun valor numerico.

**T01** `05-arquitectura.tex:78`, oracion intermedia.

```latex
% ANTES
Tanto la construcción del filtro determinístico como el ajuste del prompt se realizaron sin acceso al corpus de validación, para evitar fuga de datos (véase \autoref{subsec:interpretacion-resultados}).
% DESPUES
La procedencia de los datos empleados para construir el filtro determinístico, redactar las reglas de frontera del prompt y fijar el punto de operación se declara en la \autoref{subsec:interpretacion-resultados}.
```

**T02** `06-implementacion.tex:75`, segunda oracion del item.

```latex
% ANTES
Los ajustes se realizaron exclusivamente sobre incidentes representativos en entornos de preproducción, sin exposición al corpus de validación de 200 casos, preservando la integridad de la etapa experimental posterior.
% DESPUES
Los ajustes se realizaron a partir de errores observados en el corpus de validación; no se dispuso de un conjunto independiente de incidentes de preproducción (\autoref{subsec:interpretacion-resultados}).
```

**T03** `08-discusion.tex:18`, parrafo completo.

```latex
% ANTES
El rigor metodológico adoptado para evitar \emph{data leakage} merece una observación aparte. El filtro determinístico se construyó mediante análisis manual de incidentes no incluidos en el corpus y el prompt fue ajustado en entornos de preproducción sin exposición a los 200 casos de validación; solo después de completar el desarrollo se evaluó el desempeño sobre la totalidad del corpus, garantizando que las métricas reportadas reflejan el desempeño del sistema sobre datos no vistos. Esta separación estricta entre datos de construcción y datos de validación constituye una garantía metodológica del presente estudio.
% DESPUES
La procedencia de los datos de ajuste merece una observación aparte. Las reglas de frontera del prompt, la ampliación del vocabulario del filtro determinístico y el punto de operación del cortocircuito se derivaron de errores y casos observados en el corpus de evaluación; el punto de operación se fijó con un protocolo fuera de muestra (validación cruzada), pero ese protocolo no cubre la ampliación del vocabulario ni las reglas del prompt, que se definieron sobre la totalidad del corpus. No se dispuso de un corpus independiente de preproducción. En consecuencia, las métricas de clasificación reportadas son estimaciones dentro de la muestra, probablemente optimistas, cuya confirmación exige un corpus independiente (\autoref{sec:recomendaciones}).
```

**T04** `12-anexos.tex:135`, parrafo completo (primera oracion: procedencia; segunda: ubicacion del historial).

```latex
% ANTES
El prompt se validó y ajustó de forma iterativa sobre un conjunto de aproximadamente 100 incidentes representativos en entornos de preproducción, sin exposición al corpus de validación de 200 casos. Las versiones históricas del prompt se conservan en el repositorio bajo \texttt{docs/prompt\_gemini\_history/} para auditoría y eventual reversión.
% DESPUES
El prompt de la versión evaluada se ajustó de forma iterativa a partir de errores observados en el corpus de validación; no se dispuso de un corpus independiente de preproducción. Las versiones históricas del prompt se conservan en el historial de versiones del repositorio (archivo \texttt{docs/prompt\_gemini.txt}) para auditoría y eventual reversión.
```

**T05** `docs/anexo_h_prompt_gemini.md:160` y `:162`.

```markdown
<!-- ANTES (:160) -->
El prompt ha sido validado y ajustado iterativamente sobre un conjunto de ~100 incidentes representativos en entornos de preproducción, **sin exposición al corpus de validación utilizado en el estudio**.
<!-- DESPUES (:160) -->
El prompt de la versión evaluada ha sido validado y ajustado iterativamente a partir de errores observados en el corpus de validación; no se dispuso de un corpus independiente de incidentes de preproducción (c-72).
<!-- ANTES (:162) -->
Versiones históricas del prompt se mantienen en el repositorio bajo `docs/prompt_gemini_history/` para auditoría y posible rollback.
<!-- DESPUES (:162) -->
Las versiones históricas del prompt se conservan en el historial de versiones de `docs/prompt_gemini.txt` (`git log -- docs/prompt_gemini.txt`) para auditoría y posible rollback.
```

**T06** `evaluation/README.md:192-204`, seccion completa.

```markdown
<!-- ANTES -->
## Advertencia Metodológica (Anti Data Leakage — §8.1)

> **El clasificador NO fue ajustado sobre el corpus de evaluación.**

Este framework solo **evalúa** el clasificador. Las reglas determinísticas
(keywords) y el prompt de Gemini fueron definidos antes de la recolección del
corpus final. El framework **nunca modifica** reglas ni prompts a partir de los
resultados de evaluación.

Ajustar el clasificador sobre el corpus de evaluación invalidaría las métricas
reportadas (data leakage). Si identificás errores sistemáticos y necesitás
ajustar el sistema, usá el corpus de evaluación **solo para diagnóstico** y
medí el impacto sobre datos separados.

<!-- DESPUES -->
## Advertencia Metodológica (procedencia de los ajustes)

> **Parte del clasificador evaluado se ajustó con el corpus de evaluación.**

El historial del repositorio registra ajustes hechos sobre
`data/corpus_evaluacion_pseudonimizado.json` antes de la corrida oficial: el
vocabulario del filtro determinístico se amplió a partir de sus errores (c-71,
commit `1368fd8`); las reglas de frontera del prompt se redactaron a partir de
casos del corpus (c-72, commit `a76851e`; R002 y R038); y el punto de operación
del cortocircuito se derivó sobre el corpus por validación cruzada fuera de
muestra (c-74, commit `d6bb474`). El protocolo fuera de muestra cubre el punto de
operación, no el vocabulario ni las reglas del prompt. No se dispuso de un corpus
independiente de preproducción. Las métricas de `report.md` son, por lo tanto,
estimaciones dentro de la muestra.

Regla vigente: el framework solo **evalúa**; el corpus de evaluación se usa
**solo para diagnóstico** y todo ajuste posterior del clasificador se mide sobre
datos separados y declara su procedencia. La validación sobre un corpus
independiente queda como línea de trabajo futuro.
```

**T07** `10-recomendaciones.tex`, subseccion nueva antes de `\subsection{Estudios de replicación}\label{subsec:estudios-replicacion}` (hoy `:28`).

```latex
% ANTES
(no existe)
% DESPUES
\subsection{Validación sobre un corpus independiente}\label{subsec:corpus-independiente}

El clasificador evaluado se ajustó, en parte, con el mismo corpus sobre el que se reportan las métricas de clasificación (vocabulario del filtro determinístico y reglas de frontera del prompt), de modo que esas métricas son estimaciones dentro de la muestra. La confirmación del desempeño fuera de la muestra exige construir un corpus independiente, etiquetado con el mismo protocolo y sin solapamiento con el corpus de evaluación, y reportar sobre él las métricas de la etapa determinística y de la etapa semántica. Esa validación no se realizó en este trabajo porque no se dispuso de un corpus de preproducción con esas características.
```

## Risks / Trade-offs

- [Los autores discuten la procedencia de los ajustes de c-71/c-72] -> Checkpoint previo (tarea 1.2) con la evidencia citada (commits y casos R002/R038); si los autores acreditan datos ajenos al corpus, se restituye la afirmacion de no exposicion citando esa evidencia.
- [La divulgacion debilita la afirmacion de validez] -> No cambia ningun numero; la historia es publica en `openspec/changes/archive/` y en el historial de git, y un evaluador puede encontrarla de todos modos.
- [Duplicacion con c-130/c-142] -> Nombres de requisito identicos y seccion de reconciliacion explicita; la deduplicacion al fusionar PR #40 es mecanica (D4).
- [Choque de edicion con changes que tocan las mismas lineas] -> Las ediciones son por fragmento y conservan los `\label`; c-130/c-142 se deduplican, no se reescriben sobre estas lineas.
- [El render `tesis_para_agente.md` queda con la afirmacion vieja] -> Se regenera con `build_tesis_para_agente.py` y se verifica por `rg`.
- [Paginas] -> El cambio es aproximadamente neutro en extension (T03 y T04 crecen, T01 y T02 se acortan, T07 agrega una subseccion corta); se registra el conteo para la release.

## Migration Plan

1. Verificar la evidencia (directorio inexistente, corpus de preproduccion inexistente, commits de c-71/c-72/c-74) y registrar la linea base del PDF.
2. Checkpoint de autores sobre el texto final de T03, T04 y T05 (declaracion de procedencia).
3. Aplicar T01-T07 por archivo.
4. Registrar el resultado del checkpoint ("no existen / no se localizan") en `numeros-canonicos.md` (Seccion 7) y el grupo c-144 en `dictamen-correcciones.md`.
5. Regenerar `tesis_para_agente.md`, recompilar el PDF, contar paginas.
6. `openspec validate c-144-declarar-procedencia-real-y-ausencia-de-preproduccion --strict`.
7. **Rollback:** `git checkout <commit-previo> -- <rutas>` de los archivos editados, regenerar el render y recompilar. Sin migraciones ni re-ejecucion de la evaluacion.

## Open Questions

1. **(Autores, bloquea T03/T04/T05)** Confirman que el vocabulario de c-71 y las reglas de frontera de c-72 se derivaron de casos del corpus de evaluacion? La evidencia del historial de git lo indica; de confirmarse, se aplica la declaracion de procedencia.
2. **(Autores)** Se acepta eliminar la afirmacion de "aproximadamente 100 incidentes representativos en entornos de preproduccion" (no verificable), o existieron alguna vez fuera del repositorio? Si existieron, corresponde un change de gobernanza HIGH propio para pseudonimizarlos y etiquetarlos; este change registra el desenlace "no existen / no se localizan".
3. **(Autor / integracion)** Prefiere deduplicar c-130/c-142 al fusionar PR #40 (default, D4) o rebasar c-144 sobre el PR?
