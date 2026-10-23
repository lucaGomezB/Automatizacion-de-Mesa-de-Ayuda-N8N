## Why

La tesis afirma hechos que el repositorio NO respalda y que cualquier evaluador puede refutar con acceso al repositorio publico. Se verificaron tres divergencias:

1. **Ajustes hechos sobre el corpus presentados como ajenos a el.** `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex:78` afirma que el filtro deterministico y el prompt se construyeron "sin acceso al corpus de validacion, para evitar fuga de datos"; `06-implementacion.tex:75` repite "sin exposicion al corpus de validacion de 200 casos"; `08-discusion.tex:18` declara "datos no vistos" y una "separacion estricta entre datos de construccion y datos de validacion" presentada como "garantia metodologica del presente estudio". El historial de git lo contradice: c-71 (commit `1368fd8`) amplio el vocabulario del filtro deterministico a partir de errores del corpus; c-72 (commit `a76851e`) redacto las reglas de frontera del prompt a partir de casos del corpus (R002, R038); y c-74 (commit `d6bb474`) derivo el punto de operacion `tau = 0,5166` sobre el corpus, con protocolo fuera de muestra.

2. **Corpus de preproduccion y directorio historico inexistentes.** `12-anexos.tex:135` y `docs/anexo_h_prompt_gemini.md:160` afirman que el prompt fue ajustado sobre "aproximadamente 100 incidentes representativos en entornos de preproduccion"; `12-anexos.tex:135` y `docs/anexo_h_prompt_gemini.md:162` remiten a `docs/prompt_gemini_history/`. VERIFICADO: ese directorio nunca existio en git (sin commit, sin entrada en `git ls-files`, sin rama) y no existe ningun conjunto de ~100 incidentes independientes en el repositorio (`data/` y `evaluation/` solo contienen el corpus de 200 casos y sus derivados). Las versiones historicas del prompt viven en el historial de versiones de `docs/prompt_gemini.txt`.

3. **Afirmacion de no ajuste en el framework.** `evaluation/README.md:194` afirma "El clasificador NO fue ajustado sobre el corpus de evaluacion", contradicho por la misma evidencia.

Mientras estas afirmaciones permanezcan, la tesis presenta como garantia metodologica una propiedad que el repositorio desmiente, y la memoria de Engram (evidencia de la auditoria) queda en contradiccion con el texto. Corregirlo es una declaracion documental: NO requiere codigo ni datos nuevos.

## What Changes

- Declarar en la tesis una **procedencia real**: el vocabulario del filtro deterministico, las reglas de frontera del prompt y el punto de operacion `tau` se derivaron del corpus de 200 casos; se acota la mitigacion fuera de muestra de c-74 (no cubre el vocabulario ni el prompt); se califican las metricas de clasificacion como estimaciones dentro de la muestra.
- Declarar que **no se dispuso de un corpus independiente de preproduccion** y registrar el resultado del checkpoint como "no existen / no se localizan".
- Reclasificar las afirmaciones de "no fuga" (`05-arquitectura.tex:78`, `06-implementacion.tex:75`, `08-discusion.tex:18`, Anexo H) como declaracion de procedencia, no como garantia metodologica.
- Corregir la ubicacion de las versiones historicas del prompt: el historial de versiones de `docs/prompt_gemini.txt`, NO `docs/prompt_gemini_history/`. **No se crea ese directorio.**
- Alinear `evaluation/README.md` con la procedencia factual.
- Mover la validacion sobre un corpus independiente a las lineas de trabajo futuro (`10-recomendaciones.tex`).

No cambia ningun valor numerico, ninguna metrica ni ningun rotulo.

## Capabilities

### New Capabilities

<!-- Sin capacidades nuevas: el change modifica requisitos de capacidades existentes. -->

### Modified Capabilities

- `tesis-document`: se agregan los requisitos de declaracion de procedencia real de los ajustes (vocabulario, prompt y punto de operacion derivados del corpus; ausencia de corpus independiente; resultado del checkpoint "no existen / no se localizan"; remision de la validacion independiente a trabajo futuro) y de ubicacion veraz de las versiones historicas del prompt en el Anexo H.
- `evaluation-framework`: se agrega el requisito de advertencia metodologica de `evaluation/README.md` alineada con la procedencia factual y con la naturaleza dentro de la muestra de las metricas.

## Impact

- **Documentos editados (solo declaracion, sin codigo):** `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex`, `06-implementacion.tex`, `08-discusion.tex`, `12-anexos.tex`, `10-recomendaciones.tex`; `docs/anexo_h_prompt_gemini.md`; `evaluation/README.md`.
- **Artefactos regenerados:** `docs/Tesis/v10 (IA)/tesis_para_agente.md` (render del manuscrito) y `docs/Tesis/v10 (IA)/paper/main.pdf` (recompilacion).
- **Registro de trazabilidad:** `docs/Tesis/Correcciones/numeros-canonicos.md` (Seccion 7, decisiones no resolubles) y `docs/Tesis/Correcciones/dictamen-correcciones.md` (grupo c-144).
- **No se toca:** codigo de `App/`, `n8n/`, el corpus, `evaluation/report.md`, `evaluation/predicciones*.json`, `docs/prompt_gemini.txt` ni ningun numero canonico.
- **Gobernanza:** MEDIUM en lo documental (declara la procedencia de ajustes); no introduce codigo ni migraciones. Requiere checkpoint de autores sobre el texto final.

## Overlap y reconciliacion con c-130 y c-142

Los changes `c-130-gate-revision-humana-por-etapa` y `c-142-sensibilidad-fuera-de-muestra-ajustes-clasificador` YA cubren buena parte de estas correcciones, pero **viven en la rama del PR #40, sin fusionar**. Este change aplica las mismas correcciones sobre `main` AHORA. Este apartado es obligatorio para no duplicar en silencio.

### Superficies solapadas

| Superficie c-144 | Change que la cubre en PR #40 | Requisito en PR #40 | Accion de reconciliacion |
|---|---|---|---|
| Procedencia de vocabulario, prompt y `tau` en `05:78`, `06:75` y `08:18` | c-130 (D9) | `Procedencia declarada de los ajustes realizados sobre el corpus de validacion` (tesis-document) | c-144 lo SUPERSEDE. Al fusionar PR #40, eliminar el bloque `## ADDED Requirements` de ese requisito en c-130 (todas sus tareas T04, T12, T13 quedan redundantes). |
| Resultado del checkpoint "no existen / no se localizan" y corpus independiente como trabajo futuro | c-142 (D11/D13) | parcial en `Ubicacion veraz...` y en su limitacion | c-144 lo SUPERSEDE y lo completa. Al fusionar PR #40, c-142 conserva solo su analisis de sensibilidad; retira la declaracion del checkpoint y la remision a trabajo futuro. |
| Ubicacion del historial del prompt en el Anexo H (`12:135`, `anexo_h:160/162`) | c-142 (D13/T08) | `Ubicacion veraz de las versiones historicas del prompt en el Anexo H` (tesis-document) | c-144 lo SUPERSEDE. Al fusionar PR #40, eliminar el bloque `## ADDED Requirements` de ese requisito en c-142. |
| Advertencia metodologica de `evaluation/README.md` | c-142 (D13/R01) | `Advertencia metodologica del framework coherente con el historial` (evaluation-framework) | c-144 lo SUPERSEDE. Al fusionar PR #40, eliminar el bloque de ese requisito en c-142; si c-142 aplica su analisis de sensibilidad, agrega la remision al mismo en un requisito propio. |
| Linea de trabajo futuro sobre validacion con corpus independiente (`10-recomendaciones.tex`) | c-136 | consigna de c-130 (D9) a c-136: conservar la confirmacion sobre un corpus independiente | c-144 aplica la subseccion en `main` AHORA. Al fusionar PR #40, c-136 debe deduplicar: si ya cubre la linea, no la repite; si no, la hereda de c-144 y omite su propio texto. |
| Numero de change | PR #40 declara c-128 y c-130..c-142 | c-143 el siguiente | c-144 no colisiona. |

### Regla de reconciliacion

1. **c-144 es la fuente canonica** de las correcciones documentales de procedencia sobre `main`. Se aplica y archiva de forma independiente.
2. **Al fusionar PR #40**, los bloques `## ADDED Requirements` de c-130 y c-142 listados en la tabla MUST eliminarse (o convertirse en no-op) porque el requisito ya existe en el spec principal tras el archivado de c-144.
3. c-130 conserva todo lo que NO es la declaracion de procedencia (definicion de magnitudes por etapa, alcance del gate, criterio de cortocircuito, etc.). c-142 conserva todo su analisis de sensibilidad y su metodologia. c-136 hereda la linea de trabajo futuro sobre el corpus independiente de c-144 y no la duplica.
4. Si el autor prefiere NO fusionar PR #40 con esta premisa, la alternativa es rebasar c-144 sobre el PR y deduplicar alli; en ningun caso deben quedar dos requisitos vigentes que cubran la misma conducta.
