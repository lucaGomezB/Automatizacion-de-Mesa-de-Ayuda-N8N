# Runbook: campaña contrabalanceada (c-166)

Procedimiento para correr la campaña de medición con el diseño **contrabalanceado**: un plan por caso que asigna a cada caso su posición, su mitad y **qué brazo lo procesa primero** (manual o automatizado). Lo siguen el operador del brazo manual (fuera del repositorio), los harnesses de ingesta de `scripts/corpus_ingest/` y el operador del softphone.

## Para qué sirve

La tesis reconoce que el diseño pareado es secuencial y no contrabalanceado, de modo que el efecto de orden no es estimable (`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex`, línea 14). El efecto que importa es el del **operador humano**: la tesis lo enmarca como "efecto de aprendizaje del operador" y la base de conocimiento define el contrabalanceo como "una mitad procesada primero manual, la otra primero automatizada" (`knowledge-base/11_evaluacion_experimental.md`, línea 56). Reordenar el envío del brazo automatizado no produce ese efecto: una máquina no aprende ni se fatiga. Lo que hay que aleatorizar es **qué brazo ve primero cada caso**.

El repositorio entrega el plan, los harnesses que lo siguen y este procedimiento. Esto es lo que NO hace:

- No ejecuta la campaña ni recolecta datos: las llamadas, el etiquetado humano y los operadores reales corren **fuera del repositorio** (`docs/campana-medicion/plan-campana-de-medicion.md`). Este runbook no depende de ningún dato de campo ya recolectado.
- No estima el efecto de orden: eso es del análisis de c-167 (sección 7).
- No define la planilla ni su validador: son de c-168 (`evaluation/data/plantilla_etiquetado.csv`, `evaluation/doble_etiquetado.py`).

Todo se ejecuta desde la raíz del repositorio. Los pasos de generación y verificación no usan red.

## 0. Antes de empezar

1. Estar en el commit de la campaña, con Python y las dependencias de `evaluation/` (`pip install -r evaluation/requirements.txt`) y de los harnesses (`pip install -r scripts/corpus_ingest/requirements.txt`).
2. Verificar que el generador funciona en esta máquina con el corpus SINTÉTICO de prueba (no son datos reales):

   ```bash
   python -m evaluation.plan_campana generar \
     --corpus evaluation/tests/fixtures/corpus_fixture.json \
     --modo aleatorio --seed 1 --salida plan_de_prueba.csv
   ```

   Salida esperada: `OK: plan de 9 casos (modo=aleatorio, seed=1) escrito en plan_de_prueba.csv. Balance: ...` y exit code `0`. Borrar `plan_de_prueba.csv` al terminar (el generador no sobrescribe archivos existentes).
3. Tener el registro de sujetos de c-168 (`evaluation/data/campana/registro_sujetos.csv`, sin nombres) y al director de la tesis como custodio de la correspondencia entre personas y códigos (ver `docs/campana-medicion/runbook-doble-etiquetado.md`, sección 1).

## 1. Cómo funciona el plan

Cada fila del plan (`evaluation/data/campana/plan_campana.csv`) tiene seis columnas, en este orden: `id_caso,posicion,mitad,brazo_primero,modo,seed`.

| Columna | Contenido |
|---|---|
| `id_caso` | El `id` del caso del corpus (`R001`..`R200`; es el `case_id` de los sidecars) |
| `posicion` | Lugar del caso en la campaña, de 1 a n (posición GLOBAL) |
| `mitad` | `1` si `posicion <= n // 2`, `2` si no |
| `brazo_primero` | `manual` en las posiciones impares y `automatizado` en las pares |
| `modo` | `directo`, `inverso`, `alternado` o `aleatorio` (cómo se ordenaron los casos) |
| `seed` | La semilla entera con `aleatorio`; vacía en los otros modos |

Reglas:

- **Balance por mitad**: dentro de cada mitad, la cantidad de casos `manual`-primero y `automatizado`-primero difiere en a lo sumo 1. Con los 200 casos del corpus, cada mitad tiene 100 casos: 50 `manual`-primero y 50 `automatizado`-primero.
- **N impar**: la primera mitad tiene `n // 2` casos y la segunda uno más (el caso del medio cae en la segunda). Con 7 casos: 3 y 4. Con N = 1, un único caso en la mitad 2; con N = 0, un plan vacío.
- **Reproducibilidad**: `aleatorio` exige `--seed` y la deja registrada en cada fila; con la misma semilla y los mismos casos el plan es idéntico. Para la campaña se usa **`aleatorio` con una semilla elegida una sola vez y registrada**: con `directo` el reparto es sistemático (R001 manual, R002 automatizado, ...), lo que ata el brazo a la paridad del identificador.
- **`--limit` va antes del orden**: en los harnesses, `--orden inverso --limit 3` procesa el reverso de los TRES PRIMEROS casos del corpus, no de los tres últimos. Con `--plan`, `--limit` se rechaza: el plan ya es la selección. Para una corrida más chica se genera un plan más chico (`generar --limit N`) o se extrae un sub-plan (sección 3).

## 2. Generar y verificar el plan

1. Elegir **una** semilla entera y anotarla (queda además en cada fila del CSV). El plan se genera una sola vez por campaña:

   ```bash
   python -m evaluation.plan_campana generar \
     --corpus data/corpus_evaluacion_pseudonimizado.json \
     --modo aleatorio --seed <entero> \
     --salida evaluation/data/campana/plan_campana.csv
   ```

   El comando imprime el balance por mitad. No sobrescribe un plan existente: si hay que regenerarlo se borra a mano, y eso solo corresponde ANTES de que empiece la campaña.
2. Verificar el plan versionado (no requiere el corpus):

   ```bash
   python - <<'EOF'
   from evaluation.plan_campana import leer_plan_csv, verificar_balance
   plan = leer_plan_csv("evaluation/data/campana/plan_campana.csv")
   print(len(plan), "casos;", verificar_balance(plan))
   EOF
   ```

   Debe imprimir `200 casos;` y el conteo `{(1, 'manual'): 50, (1, 'automatizado'): 50, (2, 'manual'): 50, (2, 'automatizado'): 50}`. Si `verificar_balance` falla, el plan no se usa.
3. Calcular el SHA-256 del plan y registrarlo en `evaluation/data/campana/README.md` (tabla "SHA-256 por archivo"):

   ```bash
   sha256sum evaluation/data/campana/plan_campana.csv
   ```

   `.gitattributes` fija fin de línea LF para los CSV de esa carpeta, de modo que el hash coincide en Windows y Linux.
4. Verificar con `git status` que `data/corpus_evaluacion_pseudonimizado.json` no aparece modificado (el generador solo lo lee).

## 3. Reparto por `brazo_primero` y sub-planes por turno

Dentro de cada mitad hay dos grupos de casos: los que van `manual`-primero (A) y los que van `automatizado`-primero (B). Cada brazo ejecuta primero los casos donde él va primero (**turno 1**) y después los casos donde va segundo (**turno 2**):

| Brazo | Turno 1 (va primero) | Turno 2 (va segundo) |
|---|---|---|
| `manual` | casos A (`brazo_primero = manual`) | casos B (`brazo_primero = automatizado`) |
| `automatizado` | casos B (`brazo_primero = automatizado`) | casos A (`brazo_primero = manual`) |

Se recorre mitad por mitad (primero la mitad 1, después la 2) y, dentro de cada mitad, primero el turno 1 y después el turno 2. Dentro de un sub-plan los casos se ejecutan **en orden de `posicion`**. Cada sub-plan se extrae del plan completo y conserva la `posicion` global:

```bash
python -m evaluation.plan_campana subplan \
  --plan evaluation/data/campana/plan_campana.csv \
  --mitad 1 --brazo manual --turno 1 \
  --salida evaluation/data/campana/subplan_m1_manual_t1.csv
```

Son ocho sub-planes (dos mitades, dos brazos, dos turnos). Los cuatro de una mitad cubren cada caso de esa mitad exactamente una vez por brazo. Como un sub-plan tiene posiciones crecientes pero no contiguas, los harnesses lo aceptan con `--plan`; `subplan` en cambio solo acepta un plan completo.

## 4. El operador manual sigue el plan (fuera del repositorio)

El brazo manual lo ejecutan los operadores `O1` y `O2` fuera del repositorio. Reglas de sujetos:

- Los operadores MUST ser personas distintas de los **etiquetadores** del doble etiquetado (`E1`, `E2`), de los **dos analistas originales** que fijaron el consenso del corpus y de los **autores** de la tesis. El solape se detecta por `persona` en `registro_sujetos.csv` (`docs/campana-medicion/runbook-doble-etiquetado.md`, sección 1.2).
- Si no se consiguen operadores nuevos, se declara como limitación y no como brazo independiente.
- Qué ve el operador y cómo se instrumenta el brazo manual lo define el runbook de c-165 (`docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`, cuando c-165 esté aplicado). Este runbook solo fija el **orden**.

Cómo sigue el plan:

1. Recibe el sub-plan del turno que le toca (sección 3) y los casos en ese orden, sin el sector del consenso ni la predicción del clasificador.
2. Procesa los casos **en orden de `posicion`**, en el turno que indica `brazo_primero`: en el turno 1 los casos con `brazo_primero = manual`, en el turno 2 los de `brazo_primero = automatizado`.
3. Registra **cada caso** en la planilla única de c-168 (`evaluation/data/plantilla_etiquetado.csv`, siete columnas), con:
   - `tarea` = `brazo_manual`;
   - `id_etiquetador` = su alias, `O1` o `O2` (sin nombres ni otros datos personales);
   - `inicio`: instante ISO-8601 **con zona horaria** en que **toma el caso**;
   - `sector_etiquetado` y, si corresponde, `sectores_adicionales_etiquetados` (lista separada por `|`);
   - `timestamp`: instante ISO-8601 con zona horaria en que **asigna el sector**.

   La **duración por caso** es `duracion_s = timestamp - inicio`: es la variable respuesta del efecto de orden que estima c-167. Fila de ejemplo (SINTÉTICA):

   ```csv
   R017,O1,brazo_manual,Soporte Tecnico Software,Sistemas,2026-11-17T10:00:00-03:00,2026-11-17T10:01:20-03:00
   ```
4. Al terminar, entrega su archivo al director (custodio), que une las planillas de `O1` y `O2` y las valida con el validador único de c-168:

   ```bash
   python -m evaluation.doble_etiquetado \
     --planilla brazo_manual.csv \
     --corpus data/corpus_evaluacion_pseudonimizado.json \
     --tarea brazo_manual
   ```

   Debe salir con exit code `0`: ambos `O1` y `O2` presentes y ningún tercero, al menos un operador por caso, `inicio` presente y no posterior a `timestamp`, sectores canónicos. Los códigos de salida son los de la sección 6 del runbook de c-168.

## 5. Correr los harnesses

Los harnesses de ingesta ejecutan el brazo automatizado y registran, por caso, `orden` (el modo del plan), `posicion`, `mitad`, `brazo_primero` e `id_corrida`. Las reglas de seguridad son las mismas para los tres y se evalúan **antes** de leer credenciales o enviar nada.

1. **Copia de campaña del corpus.** Una corrida con `--plan` no puede escribir sobre el corpus versionado: su `--json` apunta a una copia con `tiempo_automatizado_s` y `tiempo_manual_s` en `null`, de modo que un caso no medido en la campaña quede nulo y no herede el tiempo canónico:

   ```bash
   python -m evaluation.plan_campana preparar-corpus \
     --origen data/corpus_evaluacion_pseudonimizado.json \
     --destino evaluation/data/campana/corpus_campana.json
   ```
2. **Un sidecar propio por corrida**, bajo `evaluation/data/campana/`, y un `--id-corrida` único por sub-plan (por ejemplo `m1-automatizado-t1`).
3. **Probar primero con `--dry-run`** (cuenta los casos sin red ni escritura) y después correr sin él. Web y correo, por el flujo N8N real:

   ```bash
   python scripts/corpus_ingest/ingest_via_n8n.py \
     --plan evaluation/data/campana/subplan_m1_automatizado_t1.csv \
     --id-corrida m1-automatizado-t1 \
     --json evaluation/data/campana/corpus_campana.json \
     --sidecar evaluation/data/campana/sidecar_m1-automatizado-t1.json
   ```

   Contra el backend directo se usa `ingest_corpus.py` con los mismos flags de campaña (sin `--json`: su fuente son el CSV o el XLSX locales).
4. **Telefonía.** `ingest_telefonia_corpus.py` NO ingesta: el operador del softphone realiza las llamadas siguiendo el plan (en orden de `posicion`, eligiendo el `corpus_case_id` de cada caso) y después se leen las mediciones:

   ```bash
   python scripts/corpus_ingest/ingest_telefonia_corpus.py \
     --plan evaluation/data/campana/subplan_m1_automatizado_t1.csv \
     --id-corrida m1-automatizado-t1-tel \
     --json evaluation/data/campana/corpus_campana.json \
     --sidecar evaluation/data/campana/sidecar_m1-automatizado-t1-tel.json
   ```

   Selecciona los casos `telefono` del plan, recupera cada medición como siempre y copia `orden`, `posicion`, `mitad` y `brazo_primero` al sidecar, sin decidir el orden de las llamadas.
5. `--orden/--seed` (en `ingest_via_n8n.py` e `ingest_corpus.py`) es un atajo que genera el plan al vuelo y lo deja en `<sidecar>.plan.csv`. **No se usa en la campaña**: el plan oficial es el versionado, con una semilla registrada.

Qué abortan los harnesses (exit code 2, sin enviar ni escribir nada):

| Situación | Motivo |
|---|---|
| `--plan` junto con `--orden` | son excluyentes |
| falta `--id-corrida` | identifica la corrida en cada entrada del sidecar |
| `--plan` con `--limit` | el plan ya es la selección |
| `--orden aleatorio` sin `--seed` | la semilla es obligatoria para poder reproducirlo |
| `--json` o `--sidecar` apuntan a `data/corpus_evaluacion_pseudonimizado.json` o a `data/corpus_resultados*.json` (incluye los valores por defecto) | son archivos versionados; el mensaje nombra el archivo y la ruta de campaña a usar |
| falta `--sidecar` | es obligatorio y propio de la corrida (no hay valor por defecto) |
| el sidecar ya existe con otro `id_corrida` (`ingest_via_n8n.py`, telefonía) | no se mezclan corridas; con el mismo `id_corrida` se reanuda |
| el sidecar ya existe (`ingest_corpus.py`) | su escritor sobrescribe todo: cada corrida usa otro sidecar |
| un `id_caso` del plan no está en el corpus | el plan no corresponde a este corpus |

Con `--plan`/`--orden` los harnesses NO escriben los originales locales CSV/XLSX (tienen datos personales): los datos de campaña viven solo en el sidecar y en la copia de campaña.

## 6. Criterio de aceptación: contrabalanceo efectivo registrado por caso

La campaña se acepta como **contrabalanceada** solo si se cumple todo lo siguiente:

1. El plan versionado pasa `verificar_balance` (sección 2) y su SHA-256 está declarado en `evaluation/data/campana/README.md`.
2. **Cada caso de la campaña tiene `posicion`, `mitad` y `brazo_primero` en el sidecar** de la corrida que lo procesó (web, correo y telefonía), y **su registro manual en la planilla** de `brazo_manual`, validada con exit code `0` (sección 4).
3. **La asignación realizada coincide con el plan**: la `posicion`, la `mitad` y el `brazo_primero` de cada entrada de sidecar son los de la fila del plan para ese caso. Verificación (desde la raíz, sobre los sidecars versionados):

```python
import glob
import json

from evaluation.plan_campana import leer_plan_csv, verificar_balance

plan = {fila.id_caso: fila for fila in leer_plan_csv("evaluation/data/campana/plan_campana.csv")}
print("balance:", verificar_balance(list(plan.values())))

cubiertos, discrepancias = set(), []
for ruta in sorted(glob.glob("evaluation/data/campana/sidecar_*.json")):
    for entrada in json.load(open(ruta, encoding="utf-8")):
        fila = plan[entrada["case_id"]]
        cubiertos.add(entrada["case_id"])
        esperado = (fila.posicion, fila.mitad, fila.brazo_primero)
        if (entrada["posicion"], entrada["mitad"], entrada["brazo_primero"]) != esperado:
            discrepancias.append((ruta, entrada["case_id"]))
print("casos con asignacion registrada:", len(cubiertos), "de", len(plan))
print("discrepancias con el plan:", discrepancias or "ninguna")
```

   Debe informar `200 de 200` y `ninguna`. Un caso ausente o con una asignación distinta de la del plan invalida el contrabalanceo de ese caso y se informa tal cual: no se corrige el sidecar a mano.
4. Los sidecars y el plan quedan versionados con su SHA-256 en el README de la carpeta; los CSV/XLSX locales de los originales no se versionan.

## 7. La estimación del efecto de orden es de c-167

Este runbook garantiza que los campos existan y sean confiables; no estima nada. El análisis de **c-167** parea por caso las mediciones de las distintas corridas (por `id_caso`/`case_id` y `id_corrida`), toma como factor el `brazo_primero` y como covariable de aprendizaje la `posicion` **del plan** (no el orden de llegada), junto con la `mitad`. La variable respuesta del brazo manual es `duracion_s = timestamp - inicio` de la planilla. El mínimo de pares, el efecto mínimo detectable y la decisión de qué contraste corresponde son de c-167; la incorporación de los resultados a la tesis es de c-169.
