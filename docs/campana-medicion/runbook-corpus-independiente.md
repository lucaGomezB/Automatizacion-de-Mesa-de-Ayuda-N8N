# Runbook: corpus independiente y validación fuera de muestra (c-166)

Procedimiento para construir un **corpus independiente** (sin solape con el corpus de ajuste), clasificarlo con el clasificador **congelado** y dejar las predicciones en artefactos aparte, sin tocar nada de la v9.

## Para qué sirve

Las métricas de clasificación de la tesis son **in-sample**: el clasificador se ajustó y se evaluó sobre los mismos 200 casos (`docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex`, línea 18). Un corpus independiente, con el mismo protocolo de pseudonimización y de doble etiquetado, permite medir cómo se comporta el clasificador sobre casos que no vio.

Este runbook entrega los **insumos**. Lo que NO hace:

- No ejecuta la campaña: el armado del corpus, el etiquetado humano y la corrida paga las realizan los autores **fuera del repositorio** (`docs/campana-medicion/plan-campana-de-medicion.md`).
- No calcula las métricas fuera de muestra ni arma el reporte con bloques in-sample/out-of-sample: eso es de c-167 (`evaluar_fuera_de_muestra`).
- No define la planilla ni su validador: son de c-168.

Todo se ejecuta desde la raíz del repositorio. La clasificación (sección 7) invoca a Gemini y tiene costo: está protegida por `--confirm-paid`.

## 0. Antes de empezar

1. Estar en el commit de la campaña y tener Python con las dependencias de `evaluation/` (`pip install -r evaluation/requirements.txt`) y del backend (`pip install -r App/Backend/requirements.txt`).
2. Verificar que el control de no solape funciona en esta máquina con los corpus SINTÉTICOS de prueba (no son datos reales):

   ```bash
   python - <<'EOF'
   from evaluation.corpus import cargar_corpus
   from evaluation.no_solape import verificar_no_solape
   ajuste = cargar_corpus("evaluation/tests/fixtures/corpus_fixture.json")
   candidato = cargar_corpus("evaluation/tests/fixtures/campana/corpus_independiente_fixture.json")
   print("sin solape;", len(verificar_no_solape(ajuste, candidato, umbral_jaccard=0.5)), "advertencias")
   EOF
   ```

   Salida esperada: `sin solape; 0 advertencias`.
3. Tener el registro de sujetos de c-168 y al director de la tesis como custodio (ver `docs/campana-medicion/runbook-doble-etiquetado.md`, sección 1).

## 1. Construir el corpus

1. Reunir casos **nuevos** del organismo, que no estén entre los 200 del corpus de ajuste. El corpus de ajuste y el independiente son conjuntos disjuntos de incidentes; el control de la sección 5 verifica ids y textos, no el contenido semántico.
2. Los ids llevan el prefijo **`I`**: `I001`, `I002`, ... (el de ajuste usa `R001`..`R200`). `verificar_no_solape` rechaza cualquier id del candidato sin ese prefijo.
3. El corpus final es un JSON con el mismo esquema que `data/corpus_evaluacion_pseudonimizado.json` (`schema_version`, `metadata` y `casos`; ver `data/README.md`, sección "Esquema JSON"): por caso, `id`, `descripcion` (pseudonimizada), `canal_origen`, `sector_asignado`, `sectores_adicionales` y los dos tiempos, que acá pueden ir en `null` (la validación de clasificación no los usa; la sección de tiempos del reporte queda sin datos).
4. Las cinco cadenas de sector son las canónicas, exactas y sin tildes: `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos` y `Sistemas`. `cargar_corpus` rechaza cualquier otra.
5. La **referencia** (`sector_asignado` y `sectores_adicionales`) sale del doble etiquetado de la sección 4, nunca de la predicción del clasificador. Por eso el JSON se arma en dos pasadas: un JSON de **trabajo**, fuera del repositorio, con todos los casos y las descripciones pseudonimizadas (los sectores cumplen el esquema pero NO se usan para evaluar), con el que se valida la planilla; y el JSON **final** con la referencia acordada, que es el que se versiona.

## 2. Pseudonimizar (mismo protocolo que el corpus de ajuste)

Los originales con datos personales NUNCA se versionan. La descripción se pseudonimiza con el mismo módulo de producción que usó el corpus de ajuste (Ley 25.326), a través de `scripts/corpus_ingest/pseudonymize_corpus.py`, que enmascara solo la columna `Descripcion` y falla con un exit code distinto de cero si queda PII visible:

```bash
python scripts/corpus_ingest/pseudonymize_corpus.py --dry-run --csv <crudo.csv> --out <pseudonimizado.csv>
python scripts/corpus_ingest/pseudonymize_corpus.py --csv <crudo.csv> --out <pseudonimizado.csv>
```

El CSV crudo usa el formato "Hoja 1" del corpus (columnas `ID`, `Descripcion`, `Canal de Origen`, ...; ver `scripts/corpus_ingest/README.md`, sección "Pseudonimizacion del corpus"). Los dominios internos se enmascaran con `--internal-domains` o `PSEUDONYMIZATION_INTERNAL_DOMAINS`, igual que en el corpus de ajuste. Después de pseudonimizar, se revisa a mano una muestra de las descripciones antes de entregarlas a los etiquetadores.

## 3. Convertir al JSON de trabajo

Con las descripciones pseudonimizadas se arma el JSON de trabajo (sección 1, punto 5) y se comprueba que cargue:

```bash
python - <<'EOF'
from evaluation.corpus import cargar_corpus
casos = cargar_corpus("corpus_independiente_trabajo.json")
print(len(casos), "casos;", sorted({c.id[0] for c in casos}))
EOF
```

Debe imprimir la cantidad de casos y `['I']`. Atención: `cargar_corpus` reescribe `metadata.total_casos` si está desincronizado; por eso se corre sobre el JSON de trabajo y nunca sobre `data/corpus_evaluacion_pseudonimizado.json`.

## 4. Doble etiquetado con la plantilla y el validador de c-168

El corpus independiente se etiqueta con el **mismo procedimiento y el mismo validador** que el de ajuste (`docs/campana-medicion/runbook-doble-etiquetado.md`): hoja ciega con solo `id_caso` y descripción, dos etiquetadores `E1` y `E2`, el mismo codebook congelado y la planilla única `evaluation/data/plantilla_etiquetado.csv`. Cambia el corpus contra el que se valida, no el procedimiento:

```bash
python -m evaluation.doble_etiquetado \
  --planilla doble_etiquetado_independiente.csv \
  --corpus corpus_independiente_trabajo.json \
  --tarea doble_etiquetado
```

Debe salir con exit code `0` (los códigos por regla están en la sección 6 del runbook de c-168). Los `id_caso` llevan prefijo `I`; el validador no impone prefijos, solo exige que cada `id_caso` exista en el JSON indicado.

Reglas que se mantienen:

- **Sujetos**: `E1` y `E2` son personas distintas entre sí, de los dos analistas originales, de los autores y de los operadores `O*` (`registro_sujetos.csv`). Si no se consiguen etiquetadores nuevos, se declara como limitación y no como etiquetado ciego (sección 9 del runbook de c-168).
- **Referencia**: la del runbook de c-168 (sección 8): los casos donde `sector_etiquetado` de `E1` y de `E2` **coinciden**. Los discordantes no entran en la referencia y se informa cuántos son; el JSON final contiene los casos con referencia y el recorte se documenta.
- **Tabla primaria**: se versiona con su SHA-256 como en la sección 7 del runbook de c-168. Para el corpus independiente se usa un nombre propio (por ejemplo `evaluation/data/campana/doble_etiquetado_independiente.csv`) para no pisar la del corpus de ajuste.

## 5. `verificar_no_solape`: paso previo obligatorio

Antes de clasificar, el JSON final se contrasta con el corpus de ajuste:

```bash
python - <<'EOF'
from evaluation.corpus import cargar_corpus
from evaluation.no_solape import verificar_no_solape
ajuste = cargar_corpus("data/corpus_evaluacion_pseudonimizado.json")
candidato = cargar_corpus("evaluation/data/campana/corpus_independiente.json")
for a in verificar_no_solape(ajuste, candidato, umbral_jaccard=0.8):
    print("ADVERTENCIA", a.id_candidato, "~", a.id_ajuste, round(a.similitud, 3))
print("sin solape de ids ni de descripciones")
EOF
```

`verificar_no_solape` falla con `SolapeError`, nombrando cada caso, si:

- un id del candidato no lleva el prefijo `I`;
- un id aparece en ambos corpus;
- la descripción normalizada (NFKC, minúsculas, espacios colapsados) tiene el mismo SHA-256 que la de un caso de ajuste: el mismo texto con otro id bloquea la corrida.

Con `umbral_jaccard`, los pares cuya similitud Jaccard de palabras supera el umbral se informan como **advertencia** (no como error): se revisan a mano y se decide si el caso sale del corpus. **Límite declarado: el control no detecta paráfrasis.** Un caso reescrito con otras palabras pasa la verificación aunque trate el mismo incidente; la independencia semántica depende de cómo se reunieron los casos (sección 1).

El runner repite este control como paso previo obligatorio (sección 7): si falla, no se clasifica nada.

## 6. Clasificador congelado

La validación fuera de muestra solo tiene sentido si el clasificador es **el mismo** que el del in-sample (`hybrid-v3`, `evaluation/evidence/README.md`) y no se ajusta después de ver el corpus independiente.

1. **`classifier_version`**: el cache independiente la registra sola (hoy `hybrid-v3`); debe ser idéntica a la del in-sample.
2. **Commit y archivos del clasificador**: el cache independiente registra el `commit` de `HEAD` al generarlo. La corrida in-sample no registró commit (`evaluation/data/campana/README.md`, sección "Referencia in-sample"), así que se comprueba que **el clasificador no cambió** desde `d6bb474`, la primera revisión que versiona la cascada `hybrid-v3` (Anexo B de la tesis):

   ```bash
   git diff d6bb474 HEAD -- App/Backend/app/classifiers docs/prompt_gemini.txt App/Backend/app/constants.py
   git diff d6bb474 HEAD -- App/Backend/app/config/settings.py
   ```

   Solo se admiten diferencias en comentarios, importaciones y campos ajenos a la clasificación. No pueden cambiar reglas, `KEYWORD_MAP`, el prompt, el vocabulario de sectores, `deterministic_score_threshold` (tau), `human_review_threshold`, el modelo ni los parámetros de Gemini. El resultado del control y el commit se anotan en el README de la carpeta.
3. **Pines**: el modelo debe coincidir con el del in-sample (`gemini-3.6-flash`) y la versión instalada de `google-genai` cumplir el rango declarado del in-sample; el cache independiente registra ambos.
4. **Prohibido recalibrar**: no se ajusta tau, el prompt, el mapa de palabras clave ni el vocabulario **después de ver** el corpus independiente (ni sus etiquetas ni sus predicciones). Si aparece un defecto, se informa como hallazgo; corregirlo y volver a medir sobre estos mismos casos invalida la medición fuera de muestra, y habría que reunir un corpus independiente nuevo. El cross-fitting dentro del corpus de ajuste para tau no se modifica.

## 7. Clasificar con rutas propias (`--confirm-paid`)

La clasificación usa el runner de siempre con tres flags que separan sus salidas de los artefactos de la v9. Requiere `GEMINI_API_KEY` y las variables del backend (`evaluation/README.md`, sección "Setup del Entorno"); esta corrida **tiene costo**:

```bash
PYTHONPATH=App/Backend python -m evaluation.run_evaluation \
  --corpus evaluation/data/campana/corpus_independiente.json \
  --predicciones evaluation/data/campana/predicciones_independiente.json \
  --reporte evaluation/data/campana/reporte_independiente.md \
  --confirm-paid
```

Qué hace el runner, en este orden, y cuándo aborta sin tocar ningún archivo:

1. Con un `--corpus` distinto del canónico, `--predicciones` y `--reporte` son **obligatorios** y no pueden ser `evaluation/predicciones.json` ni `evaluation/report.md` (exit code 2, antes de construir el clasificador). `--solo-tiempos` no se puede usar con un corpus no canónico.
2. Ejecuta `verificar_no_solape` contra `data/corpus_evaluacion_pseudonimizado.json`; si falla, aborta (exit code 2).
3. Pide la procedencia: el `commit` de `HEAD` (`git rev-parse --short HEAD`) y los `pines` (versión instalada de `google-genai` y modelo de la configuración del backend). Si no puede obtener alguno (sin repositorio git, sin `git`, sin el paquete o sin las variables del backend), **falla antes de invocar al clasificador y antes de escribir** (exit code 2).
4. Aplica el gate de costo: sin `--confirm-paid` (o `EVALUATION_CONFIRM_PAID=1`) aborta con exit code 2 y no llama a Gemini. Con confirmación imprime una estimación orientativa del costo y clasifica.
5. Escribe las predicciones con este `cache_meta` (los cuatro campos de siempre más `commit` y `pines`) y el reporte propio:

   ```json
   {"cache_meta": {"corpus_hash": "...", "corpus_count": 0, "classifier_version": "hybrid-v3",
                   "generated_at": "...", "commit": "<hash corto>",
                   "pines": {"google_genai": "<version instalada>", "modelo": "gemini-3.6-flash"}},
    "predictions": []}
   ```

Un cache válido (mismo hash de corpus, misma cantidad de casos y misma versión del clasificador) se reutiliza sin pagar ni volver a pedir la procedencia; `--force` obliga a clasificar de nuevo. Sin ninguno de los tres flags nuevos, el runner se comporta exactamente como antes.

El reporte propio es el de siempre aplicado al corpus independiente: **no** es el análisis fuera de muestra (sección 9).

## 8. Versionar y registrar

1. Dejar en `evaluation/data/campana/` el corpus final pseudonimizado (`corpus_independiente.json`), la tabla del doble etiquetado independiente y su `registro_sujetos.csv`, las predicciones (`predicciones_independiente.json`) y el reporte (`reporte_independiente.md`).
2. Calcular el SHA-256 de cada archivo y completar la tabla "SHA-256 por archivo" de `evaluation/data/campana/README.md`.
3. Anotar en ese README el resultado del control de clasificador congelado (sección 6) y el `commit` con el que se generó el cache.
4. Verificar que los artefactos de la v9 no cambiaron: `git status` no debe mostrar `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json` ni `evaluation/report.md`, y el SHA-256 de `evaluation/predicciones.json` (cache local, fuera de git) debe ser el mismo de antes de la corrida.

## 9. El análisis fuera de muestra es de c-167

Este runbook deja las predicciones separadas y con su procedencia completa. El cálculo de las métricas fuera de muestra y el reporte con bloques **in-sample** y **out-of-sample** rotulados (`evaluar_fuera_de_muestra`) son de **c-167**, que compara `classifier_version` y `pines` del cache independiente contra la referencia in-sample de `evaluation/data/campana/README.md` (el `commit` solo se compara si ambos lo traen). La incorporación a la tesis es de c-169.

## 10. Criterio de aceptación

El corpus independiente queda aceptado solo si se cumple todo lo siguiente:

1. `verificar_no_solape` pasa (ids con prefijo `I`, sin ids ni descripciones repetidos) y las advertencias de similitud se revisaron.
2. El corpus se pseudonimizó con el mismo protocolo que el de ajuste y el pseudonimizador salió con exit code `0`.
3. El doble etiquetado validó con exit code `0` y el registro de sujetos no tiene solapes, o la limitación está declarada.
4. El control de clasificador congelado (sección 6) está registrado y no hubo recalibración posterior.
5. `predicciones_independiente.json` trae en su `cache_meta` `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines`.
6. Los artefactos de la v9 no cambiaron (sección 8, punto 4) y todos los archivos nuevos están versionados con su SHA-256.
