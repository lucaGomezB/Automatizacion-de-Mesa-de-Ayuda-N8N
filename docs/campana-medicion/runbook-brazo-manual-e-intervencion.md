# Runbook: brazo manual e intervención humana (c-165)

Procedimiento para producir los dos datasets que la auditoría CONEAU marcó como faltantes: la **clasificación del brazo manual** (qué sector asigna el operador a cada caso, con sus tiempos) y la **intervención humana real** (cuándo, quién y por qué origen un operador valida o reasigna una clasificación del sistema). Con ellos c-167 calcula la exactitud del brazo manual, la tasa de intervención y el efecto de orden.

La campaña corre **fuera del repositorio**: las personas que operan, las llamadas y los envíos son de los autores. El repositorio entrega el instrumento de captura (la planilla única de etiquetado de c-168), el registro de la intervención en la base (migración `024`), el export pseudonimizado y este procedimiento. Esto es lo que NO hace:

- No ejecuta la campaña ni trae datos de campo: este runbook no depende de ningún dato ya recolectado.
- No define la planilla ni su validador: son de c-168 (`evaluation/data/plantilla_etiquetado.csv`, `evaluation/doble_etiquetado.py`).
- No define el plan ni el orden de la campaña: son de c-166 (`evaluation/data/campana/plan_campana.csv`, `docs/campana-medicion/runbook-campana-contrabalanceada.md`).
- No calcula exactitud, tasa ni efecto de orden: es el análisis de c-167.

Todo se ejecuta desde la raíz del repositorio salvo el export (sección 5), que corre desde `App/Backend`. Cada paso nombra su archivo de entrada, su comando, su archivo de salida y la condición con la que se da por bueno.

## 0. Antes de empezar

1. Estar en el commit de la campaña, con Python y las dependencias de `evaluation/` (`pip install -r evaluation/requirements.txt`) y las del backend (`pip install -r App/Backend/requirements.txt`).
2. Verificar que el validador funciona en esta máquina con la planilla SINTÉTICA del brazo manual (no son datos reales):

   ```bash
   python -m evaluation.doble_etiquetado \
     --planilla evaluation/tests/fixtures/campana/brazo_manual_fixture.csv \
     --corpus evaluation/tests/fixtures/campana/corpus_brazo_manual_fixture.json \
     --tarea brazo_manual
   echo $?
   ```

   Salida esperada: `OK: planilla valida (tarea=brazo_manual, n_casos=6, n_registros=7, etiquetadores=O1,O2)` y exit code `0`.
3. Verificar que la base de la campaña está en la revisión `024` (la que agrega `validado_por_empleado_id`, `intervencion_inicio_en`, `validado_en` y `origen_intervencion` a `clasificacion_log`). Desde `App/Backend`, con el `.env` apuntando a esa base:

   ```bash
   alembic current
   ```

   Debe informar `024 (head)`. Si informa una revisión anterior, aplicar `alembic upgrade head` ANTES de que empiece la campaña. Las intervenciones anteriores a la `024` no tienen metadatos y el export las excluye (sección 5.5).
4. Dimensionar los logs ya validados que existan antes de empezar (deberían ser cero en una base de campaña nueva), con el cliente SQL habitual (por ejemplo `psql`) sobre la base de la campaña:

   ```sql
   SELECT count(*) FILTER (WHERE sector_id_validado IS NOT NULL) AS legadas, count(*) AS total FROM clasificacion_log;
   ```

   Anotar el resultado: si `legadas` es mayor que cero, esos logs saldrán de la tasa y se declaran (sección 5.5).
5. Tener al director de la tesis como **custodio** de dos secretos que NO entran al repositorio: la correspondencia entre personas y códigos `P<n>` (sección 1.2) y la clave del alias del actor del export (sección 5.3).

## 1. Sujetos

### 1.1 Quién puede ser operador del brazo manual

Los operadores son **dos personas fijas**, con alias `O1` y `O2`. Cada una MUST ser una persona:

- distinta de la otra;
- distinta de los **etiquetadores** del doble etiquetado (`E1`, `E2`, c-168);
- distinta de los **dos analistas originales** que fijaron el consenso `sector_asignado` del corpus;
- distinta de los **autores** de la tesis.

Si no se consiguen operadores que cumplan esto, la medición se hace igual pero se declara como **limitación** y NO como brazo independiente (sección 8). La exigencia existe para evitar la circularidad: si quien clasifica a mano es quien fijó la referencia, la exactitud del brazo manual mide el acuerdo consigo mismo.

### 1.2 Registro de sujetos

Los operadores se registran en `evaluation/data/campana/registro_sujetos.csv` (el archivo que define c-168; si ya existe por el doble etiquetado, se AGREGAN las filas de `O1` y `O2`). **Sin nombres, correos ni legajos.** Columnas:

| Columna | Contenido |
|---|---|
| `alias` | `O1` o `O2` para los operadores (el archivo ya trae `E1`, `E2`, `A1`, `A2` y los autores `T<n>`) |
| `rol` | `operador` |
| `persona` | Código seudónimo `P<n>`, **estable entre roles**: la misma persona lleva el mismo código en todos los roles que tenga |

El director asigna un código `P<n>` por cada persona real y custodia la correspondencia código-identidad **fuera del repositorio**. Ejemplo (SINTÉTICO, solo ilustra el formato; los códigos reales los asigna el director):

```csv
alias,rol,persona
E1,etiquetador,P5
E2,etiquetador,P6
O1,operador,P3
O2,operador,P4
A1,analista_original,P1
A2,analista_original,P2
T1,autor,P7
T2,autor,P8
```

### 1.3 Verificar la independencia (por `persona`)

Los alias son específicos de cada rol, así que NO sirven para detectar que una persona ocupa dos roles: el solape se detecta por `persona`. Entrada: `evaluation/data/campana/registro_sujetos.csv`. Comando:

```bash
python - <<'EOF'
import collections, csv
filas = list(csv.DictReader(open("evaluation/data/campana/registro_sujetos.csv", encoding="utf-8", newline="")))
roles = collections.defaultdict(set)
for fila in filas:
    roles[fila["persona"]].add(fila["rol"])
operadores = [f for f in filas if f["rol"] == "operador"]
print("operadores registrados:", sorted(f["alias"] for f in operadores))
solapes = {p: sorted(r) for p, r in roles.items() if len(r) > 1}
print("solapes por persona:", solapes or "ninguno")
EOF
```

Se acepta si imprime `operadores registrados: ['O1', 'O2']` y `solapes por persona: ninguno`. Si una `persona` de un `O*` aparece con otro rol (`etiquetador`, `analista_original` o `autor`), hay un **incumplimiento del protocolo**: se reemplaza al operador o se declara la limitación (sección 8). **No** se corrige un solape cambiando códigos `P<n>` para que desaparezca: el registro debe reflejar a las personas reales. c-167 recibe este registro y rechaza los solapes.

### 1.4 Qué ve el operador

Los operadores MUST NOT ver, en ningún momento:

- `sector_asignado` ni `sectores_adicionales` del corpus (el consenso original);
- el consenso del doble etiquetado nuevo ni las etiquetas de `E1` y `E2`;
- la **predicción del clasificador** (ni de v9 ni de ninguna corrida del brazo automatizado);
- la clasificación del otro operador.

Reciben **solo `id_caso` y la descripción pseudonimizada**, en el orden de su sub-plan (sección 3.1). No reciben el corpus JSON, `evaluation/report.md`, `evaluation/predicciones.json` ni material del clasificador. Cada operador trabaja solo, sobre su propia copia.

### 1.5 Contra qué se mide el brazo manual

La referencia es el **consenso del doble etiquetado nuevo de c-168** (`evaluation/data/campana/doble_etiquetado.csv`) en los casos donde `E1` y `E2` **coinciden**: no es el `sector_asignado` original del corpus. Los casos donde `E1` y `E2` discrepan quedan fuera de la medición de exactitud y se **reportan aparte** con su cantidad (c-167 hace el conteo; el criterio está en la sección 8 del runbook de c-168). Este runbook no produce esa tabla: se produce con `docs/campana-medicion/runbook-doble-etiquetado.md`.

## 2. Casos, reparto y mínimo

### 2.1 Mínimo de casos

Por defecto el brazo manual clasifica **la totalidad de los casos del plan de campaña** (los 200 de `evaluation/data/campana/plan_campana.csv`, `R001`..`R200`). El mínimo se fija ANTES de la campaña y se registra; la justificación del valor por defecto es:

1. La referencia (consenso de `E1` y `E2`) se produce para los 200 casos; un subconjunto desaprovecha esa cobertura y agrega un criterio de selección que habría que justificar.
2. El efecto de orden se estima entre grupos independientes de casos (los 100 que van `manual`-primero contra los 100 que van `automatizado`-primero, según `brazo_primero`): con 100 y 100 el efecto mínimo detectable es del orden de `d ≈ 0,43` (decisión D8 del diseño de c-167). Menos casos agrandan ese umbral.
3. La tasa de intervención usa como denominador los casos del plan: el brazo manual debe cubrirlos todos para que las dos medidas se refieran a los mismos casos.

Si por restricciones de campo se elige un N menor, se decide y se justifica antes de empezar, se genera el plan para ese N (`python -m evaluation.plan_campana generar ... --limit <N>`, ver el runbook de c-166) y se registra el valor y el motivo en `evaluation/data/campana/README.md`. Un N menor se reporta como limitación del alcance.

### 2.2 Reparto entre operadores

Reglas, que aplica el validador de c-168 con `--tarea brazo_manual` (c-165 no agrega reglas propias):

- **Cada `id_caso` del plan lo clasifica al menos un operador.**
- Hay **como máximo un registro por `(id_caso, id_etiquetador)`**: un operador no clasifica dos veces el mismo caso.
- Se registran ambos `O1` y `O2` y ningún tercero.

Reparto por defecto: `O1` toma la **mitad 1** del plan y `O2` la **mitad 2** (columna `mitad` de `plan_campana.csv`); cada uno recibe los sub-planes de su mitad (sección 2.3). Una **submuestra con doble cobertura** (casos que clasifican ambos operadores) es opcional y deseable: permite medir además el acuerdo entre operadores. Si se hace, el criterio de selección se fija antes de empezar (por ejemplo, un caso de cada diez por `posicion`) y se registra en el README; en la planilla esos casos tienen dos filas, una por operador.

### 2.3 Plan de campaña y sub-planes

Los operadores siguen la `posicion` y el `brazo_primero` de `evaluation/data/campana/plan_campana.csv` (columnas `id_caso,posicion,mitad,brazo_primero,modo,seed`), que genera c-166. El brazo manual recorre el plan mitad por mitad y, dentro de cada mitad, primero el **turno 1** (casos con `brazo_primero = manual`) y después el **turno 2** (casos con `brazo_primero = automatizado`), cada turno en orden de `posicion`. Cada sub-plan se extrae del plan completo:

```bash
python -m evaluation.plan_campana subplan \
  --plan evaluation/data/campana/plan_campana.csv \
  --mitad 1 --brazo manual --turno 1 \
  --salida evaluation/data/campana/subplan_m1_manual_t1.csv
```

Entrada: el plan completo. Salida: el sub-plan (no se sobrescribe uno existente). Para el brazo manual son cuatro: `--mitad 1|2` por `--turno 1|2`. `O1` recibe los de la mitad 1 y `O2` los de la mitad 2 (reparto por defecto). El detalle del plan, de los sub-planes y de los turnos está en `docs/campana-medicion/runbook-campana-contrabalanceada.md`, secciones 1 a 4; este runbook solo agrega cómo se registra lo que hace el operador.

## 3. Sesión del brazo manual (fuera del repositorio)

### 3.1 Preparar la hoja del operador

La hoja contiene SOLO `id_caso` y `descripcion`, en el orden del sub-plan (por `posicion`). Entradas: un sub-plan (sección 2.3) y el corpus. Salida: `hoja_operador_<alias>_<subplan>.csv`. La hoja contiene descripciones pseudonimizadas: **no se versiona** ni se deja dentro del repositorio; se genera fuera de él (o se borra al terminar). Los textos están pseudonimizados (Ley 25.326) pero siguen siendo datos del organismo.

```bash
python - <<'EOF'
import csv, json
SUBPLAN = "evaluation/data/campana/subplan_m1_manual_t1.csv"      # entrada: el sub-plan del turno
SALIDA = "/ruta/fuera/del/repo/hoja_operador_O1_m1_t1.csv"        # salida: FUERA del repositorio
corpus = json.load(open("data/corpus_evaluacion_pseudonimizado.json", encoding="utf-8"))
descripciones = {caso["id"]: caso["descripcion"] for caso in corpus["casos"]}
with open(SUBPLAN, encoding="utf-8", newline="") as fh:
    filas = sorted(csv.DictReader(fh), key=lambda fila: int(fila["posicion"]))
with open(SALIDA, "w", encoding="utf-8", newline="") as fh:
    escritor = csv.writer(fh, lineterminator="\n")
    escritor.writerow(["id_caso", "descripcion"])
    for fila in filas:
        escritor.writerow([fila["id_caso"], descripciones[fila["id_caso"]]])
EOF
head -1 /ruta/fuera/del/repo/hoja_operador_O1_m1_t1.csv
```

Se acepta si `head -1` imprime exactamente `id_caso,descripcion` y `wc -l` da la cantidad de casos del sub-plan más uno. El corpus se abre en modo lectura: verificar con `git status` que `data/corpus_evaluacion_pseudonimizado.json` no aparece modificado.

### 3.2 Entrega a cada operador

Cada operador recibe: su hoja (o sus hojas, una por sub-plan), **una copia vacía** de `evaluation/data/plantilla_etiquetado.csv` (solo encabezado) y el codebook congelado del doble etiquetado (`docs/campana-medicion/runbook-doble-etiquetado.md`, sección 3: el mismo criterio de sector para todos). Nada más (sección 1.4).

### 3.3 Registrar cada caso

El operador procesa los casos **en el orden de `posicion` de su sub-plan** y registra **una fila por caso** en la planilla única de c-168, con las siete columnas de la plantilla y en este orden:

| Columna | Qué poner |
|---|---|
| `id_caso` | El `id` del caso en su hoja (`R001`..`R200`) |
| `id_etiquetador` | Su alias: `O1` o `O2` |
| `tarea` | `brazo_manual` |
| `sector_etiquetado` | Exactamente una de las cinco cadenas canónicas (etiqueta primaria) |
| `sectores_adicionales_etiquetados` | Lista separada por `\|` sin espacios alrededor; vacío si no hay; sin repetir el sector principal |
| `inicio` | **Obligatorio** en `brazo_manual`: instante ISO-8601 **con zona horaria** en que **toma el caso** |
| `timestamp` | **Obligatorio**: instante ISO-8601 **con zona horaria** en que **asigna el sector** (el fin de la clasificación del caso) |

El tiempo del operador por caso es `timestamp - inicio`: `inicio` y `timestamp` **reemplazan cualquier cronómetro aparte**. `inicio` permite además reconstruir en qué posición clasificó realmente cada caso (sección 4.2). Las cinco cadenas canónicas, exactas y sin tildes, son `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos` y `Sistemas`.

Fila de ejemplo (SINTÉTICA):

```csv
R017,O1,brazo_manual,Soporte Tecnico Software,Sistemas,2026-11-17T10:00:00-03:00,2026-11-17T10:01:20-03:00
```

Notas de formato (las mismas que en el doble etiquetado):

- Si se completa en una planilla de cálculo, exportar como **CSV UTF-8 sin BOM, separador coma**, y fijar `inicio` y `timestamp` como texto: los formatos regionales (`17/11/2026 10:00`) los rechaza el validador.
- No agregar columnas (nombre, correo, legajo, teléfono, descripción): el validador las rechaza.
- El operador no corrige filas ya registradas para "mejorar" tiempos: un `inicio` mal tomado se informa al director, no se reescribe.

Al terminar cada sub-plan, el operador entrega su archivo (`brazo_manual_O1.csv`, `brazo_manual_O2.csv`) **al director**, no al otro operador.

## 4. Validar la planilla, reconstruir la posición y versionarla

### 4.1 Unir y validar

Entradas: `brazo_manual_O1.csv` y `brazo_manual_O2.csv` (cada uno con su encabezado). El director los une con un único encabezado:

```bash
{ cat brazo_manual_O1.csv; tail -n +2 brazo_manual_O2.csv; } > brazo_manual.csv
```

Y valida contra el corpus con el validador único de c-168:

```bash
python -m evaluation.doble_etiquetado \
  --planilla brazo_manual.csv \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --tarea brazo_manual
echo $?
```

Se acepta si sale con exit code `0`: ambos `O1` y `O2` presentes y ningún tercero, al menos un operador por caso del corpus, un solo registro por `(id_caso, id_etiquetador)`, `inicio` presente y no posterior a `timestamp`, sectores canónicos. Los códigos de error son los de la sección 6 de `docs/campana-medicion/runbook-doble-etiquetado.md` (por ejemplo `10` etiquetadores, `11` cobertura, `12` duplicados, `19` `inicio` posterior a `timestamp`). El CLI imprime todas las ofensas; se corrige el registro de origen y se vuelve a validar hasta obtener `0`. El validador no modifica la planilla.

### 4.2 Posición real y desvíos respecto del plan

Entradas: `brazo_manual.csv` (ya validada) y `evaluation/data/campana/plan_campana.csv`. Comando:

```bash
python - <<'EOF'
import csv
from evaluation.brazo_manual import desvios_respecto_del_plan, reconstruir_posicion_real
from evaluation.plan_campana import leer_plan_csv

plan = leer_plan_csv("evaluation/data/campana/plan_campana.csv")
with open("brazo_manual.csv", encoding="utf-8", newline="") as fh:
    filas = list(csv.DictReader(fh))
reales = reconstruir_posicion_real(filas)
desvios = desvios_respecto_del_plan(reales, plan)
print("casos registrados:", len(reales))
print("desvios respecto del plan:", len(desvios))
for d in desvios:
    print(d.id_etiquetador, d.id_caso, "planeada", d.posicion_planeada, "real", d.posicion_real)
EOF
```

La posición real de cada caso se reconstruye ordenando por `inicio` (como instante, no como texto) dentro de cada operador, con desempate por `timestamp`. La posición planeada es el lugar del caso en el orden que el plan le indica al brazo manual (mitad, turno 1 y turno 2, cada turno por `posicion`) restringido a los casos que ese operador registró. Se acepta si el comando termina sin error y el resultado queda **informado tal cual**: los desvíos no invalidan la planilla (los analiza c-167 como covariable), pero tampoco se corrigen a mano. Un error `BrazoManualError` nombra operador, caso y campo; se corrige el registro de origen.

### 4.3 Versionar la planilla del brazo manual

```bash
sed -i 's/\r$//' brazo_manual.csv
cp brazo_manual.csv evaluation/data/campana/brazo_manual.csv
sha256sum evaluation/data/campana/brazo_manual.csv
```

(En PowerShell: `(Get-FileHash -Algorithm SHA256 evaluation\data\campana\brazo_manual.csv).Hash.ToLower()`.) Salida: `evaluation/data/campana/brazo_manual.csv` con fin de línea LF (`.gitattributes` lo fija para los `*.csv` de esa carpeta). Registrar el SHA-256 en `evaluation/data/campana/README.md` (subsección "Planilla del brazo manual (c-165)", fila `brazo_manual.csv`) y la cantidad de desvíos informados en 4.2 en el campo `brazo_manual_desvios_informados`. El registro de sujetos (sección 1.2) se versiona con la misma carpeta.

### 4.4 Ensamblar las entradas del análisis

Con `brazo_manual.csv` y `doble_etiquetado.csv` versionados en `evaluation/data/campana/`, el director produce las dos entradas que consume el análisis de c-167:

```bash
python -m evaluation.preparar_entradas_analisis \
  --entrada evaluation/data/campana \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json
```

El comando une las dos planillas C1 en `plantilla_etiquetado.csv` (un único encabezado, LF, sin BOM), re-valida cada tarea (`doble_etiquetado` y `brazo_manual`) con `validar_doble_etiquetado` y copia **byte a byte** el cache congelado `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` a `predicciones_in_sample.json`. Aborta sin escribir si una fuente falta o no pasa el validador, y nunca escribe en `evaluation/evidence/`. Imprime el SHA-256 de cada salida y su procedencia (fuente y hash de la fuente): registrarlos en `evaluation/data/campana/README.md`. Este paso es el único camino documentado para producir las dos entradas y no se puede saltar en silencio.

## 5. Dataset de intervención: registro en la app y export

### 5.1 Qué se registra y cuándo

Cada vez que un operador **valida** una clasificación en la app (diálogo de validación de la cola de revisión) o **reasigna el sector** de un incidente, el backend guarda en el log de clasificación: el actor (`validado_por_empleado_id`, solo el id), el inicio declarado por el cliente (`intervencion_inicio_en`, el instante en que se abrió el diálogo), el instante del servidor (`validado_en`) y el **origen**, que el backend deriva siempre (el cliente no lo declara):

| Origen | Cuándo se escribe |
|---|---|
| `gate` | Se valida un log que estaba marcado para revisión humana |
| `muestreo` | Se valida un log que NO estaba marcado (hoy solo posible por la API; ver sección 8) |
| `rederivacion` | El sector del incidente cambia por `PATCH /api/v1/incidentes/{id}` |
| `completado_manual` | Reservado: sin escritor en c-165; no debe aparecer |

Una **confirmación** del sector predicho también cuenta como intervención (queda con `cambio_sector = false`). Gana la última escritura: si un log vuelve a validarse o reasignarse, el origen y los metadatos son los de la última intervención.

### 5.2 Requisitos de las cuentas

La cuenta con la que se valida debe tener un **empleado activo vinculado** en el directorio: así se registra el actor. Sin empleado vinculado la validación funciona igual, pero `actor_alias` queda vacío en el export. No hace falta registrar a estas personas en `registro_sujetos.csv` (el alias del actor no se usa como clave de análisis).

### 5.3 Exportar

Entradas: la base de la campaña (`DATABASE_URL` del `.env` del backend) y los **sidecars** de las corridas (`evaluation/data/campana/sidecar_<id_corrida>.json`, de c-166). Salida: `evaluation/data/campana/intervenciones.csv`.

1. Definir la clave del alias del actor en la terminal. Es una cadena secreta elegida por el director: **no se versiona, no se imprime y debe ser la MISMA en todas las corridas del export**, para que el alias de una persona sea estable:

   ```bash
   export INTERVENCION_EXPORT_HMAC_KEY='<clave secreta del director>'
   ```

   Sin esta variable el comando falla con un error que la nombra (no toca `Settings`, `.env.example` ni el CI).
2. Ejecutar desde `App/Backend`, con `--sidecar` repetido una vez por corrida y el rango de días de la campaña (días de negocio, ambos inclusivos; acota por la fecha de creación del log):

   ```bash
   cd App/Backend
   ARGS=""; for f in ../../evaluation/data/campana/sidecar_*.json; do ARGS="$ARGS --sidecar $f"; done
   python -m scripts.exportar_intervenciones $ARGS \
     --desde AAAA-MM-DD --hasta AAAA-MM-DD \
     --salida ../../evaluation/data/campana/intervenciones.csv
   cd ../..
   ```

   El comando imprime un resumen: filas exportadas, logs legados excluidos, filas sin `id_caso` (con cuántas por vínculo ambiguo) y filas sin `duracion_s` (sin inicio o con inicio posterior a la validación). **Guardar ese resumen**: es parte de la declaración de la sección 5.5.
3. El CSV trae una fila por log intervenido, con las columnas `id_caso, incidente_id, log_id, origen_intervencion, intervencion_inicio_en, validado_en, duracion_s, sector_predicho, sector_validado, cambio_sector, actor_alias`. El detalle de cada columna está en `evaluation/data/campana/README.md`, sección "Export de intervenciones (c-165)".

**Ventana de retención (DIR-007).** Exportar ANTES de cualquier purga del directorio (`python -m scripts.purgar_directorio` o la purga por la API). La clave foránea del actor es `ON DELETE SET NULL`: si la purga manual elimina a un empleado dado de baja, sus intervenciones pierden el actor y un export posterior dejaría `actor_alias` vacío. La purga nunca es automática (DIR-007), así que alcanza con no ejecutarla hasta versionar el CSV; una vez versionado, el archivo conserva el alias.

### 5.4 Verificar el export

Entrada: `evaluation/data/campana/intervenciones.csv`. Comando (desde la raíz del repositorio):

```bash
python - <<'EOF'
import csv
import re

from evaluation.corpus import SECTORES_CANONICOS

COLUMNAS = [
    "id_caso", "incidente_id", "log_id", "origen_intervencion", "intervencion_inicio_en",
    "validado_en", "duracion_s", "sector_predicho", "sector_validado", "cambio_sector",
    "actor_alias",
]
ORIGENES = {"gate", "muestreo", "rederivacion"}  # completado_manual esta reservado: no debe aparecer
with open("evaluation/data/campana/intervenciones.csv", encoding="utf-8", newline="") as fh:
    lector = csv.DictReader(fh)
    assert lector.fieldnames == COLUMNAS, lector.fieldnames
    filas = list(lector)
problemas = []
for n, fila in enumerate(filas, start=2):  # la linea 1 es el encabezado
    if fila["origen_intervencion"] not in ORIGENES:
        problemas.append((n, "origen_intervencion", fila["origen_intervencion"]))
    if not re.fullmatch(r"[0-9a-f]{12}|", fila["actor_alias"]):
        problemas.append((n, "actor_alias con otro formato"))
    if fila["cambio_sector"] not in ("true", "false"):
        problemas.append((n, "cambio_sector", fila["cambio_sector"]))
    for columna in ("sector_predicho", "sector_validado"):
        if fila[columna] and fila[columna] not in SECTORES_CANONICOS:
            problemas.append((n, columna, fila[columna]))
    if fila["duracion_s"] and float(fila["duracion_s"]) < 0:
        problemas.append((n, "duracion_s negativa"))
    if any("@" in valor for valor in fila.values()):
        problemas.append((n, "contiene @ (posible email)"))
print(len(filas), "filas;", "sin problemas" if not problemas else problemas)
print("sin id_caso (no vinculables):", sum(1 for f in filas if not f["id_caso"]))
print("sin duracion_s:", sum(1 for f in filas if not f["duracion_s"]))
EOF
```

Se acepta si imprime `sin problemas`: las columnas son exactamente las acordadas y en ese orden, el origen es del vocabulario, el alias tiene 12 caracteres hexadecimales (o está vacío), los sectores son canónicos y ninguna celda contiene un email. Además, revisar a ojo que el archivo no tiene nombres, teléfonos ni legajos: el export no los lee, pero la verificación final es humana.

### 5.5 Declarar legados y vínculos faltantes

Del resumen de 5.3 y de la verificación 5.4, registrar en `evaluation/data/campana/README.md` (sección "Export de intervenciones (c-165)", campo `intervenciones_legados_excluidos` y una nota por cada punto):

- **Legados excluidos**: logs validados antes de la migración `024` (sector validado sin `validado_en`). En una base de campaña nueva son cero por construcción; si son más, se declara la cantidad y se investiga por qué la base tenía validaciones previas.
- **Filas sin `id_caso`**: el incidente no figura en los sidecars de las corridas (o figura en dos casos distintos). c-167 las cuenta como no vinculables y las deja fuera de la tasa; se declara la cantidad.
- **Filas sin `duracion_s`**: sin `intervencion_inicio_en` (siempre las `rederivacion`, que no tienen diálogo) o con el inicio posterior a la validación (reloj del cliente adelantado). Si falta la duración en demasiados casos intervenidos, c-167 declara la proporción de tiempo como no estimable; se informa la cobertura.

El denominador de la tasa (los casos de la corrida) **no sale del export**, que solo trae filas intervenidas: c-167 lo toma de `plan_campana.csv` o del sidecar de la corrida.

### 5.6 Versionar el export

```bash
sha256sum evaluation/data/campana/intervenciones.csv
```

Completar en el README los campos `intervenciones_sha256`, `intervenciones_fecha`, `intervenciones_comando` (el comando exacto de 5.3, sin la clave) e `intervenciones_rango`, y la fila de la tabla de SHA-256. El archivo no tiene PII (el actor es un alias con clave) y se versiona con LF.

## 6. Criterio de aceptación y verificación por dataset

| Dataset | Se acepta si | Evidencia |
|---|---|---|
| **Brazo manual** (`brazo_manual.csv`) | (1) el validador sale con `0` sobre `--tarea brazo_manual` (sección 4.1); (2) cobertura de los casos del plan con al menos un operador; (3) la posición real se reconstruyó y los **desvíos** respecto del plan se informaron (4.2); (4) el registro de sujetos no tiene solapes por `persona`, o la limitación está declarada (1.3 y 8); (5) los operadores no vieron la predicción ni el consenso (1.4) | Salida del validador, salida de 4.2, SHA-256 en `evaluation/data/campana/README.md` |
| **Intervención** (`intervenciones.csv`) | (1) la verificación 5.4 dice `sin problemas` (**export sin PII**); (2) los **legados** y los **vínculos faltantes** están declarados con su cantidad (5.5); (3) la base estaba en la revisión `024` (sección 0, punto 3); (4) el export se hizo antes de cualquier purga del directorio (5.3); (5) la clave no está en ningún archivo del repositorio | Resumen del comando, salida de 5.4, SHA-256 y procedencia en el README |
| **Referencia** (consenso del doble etiquetado) | La produce c-168 con su propio criterio de aceptación; acá solo se exige que `E1` y `E2` sean personas distintas de `O1` y `O2` (1.3) y que los discordantes se reporten aparte (1.5) | `docs/campana-medicion/runbook-doble-etiquetado.md`, sección 7 |

El SHA-256 de cada dataset se registra en `evaluation/data/campana/README.md` (en minúsculas, calculado sobre el archivo tal como queda versionado, con LF), con el mismo patrón que `evaluation/evidence/README.md`. Un dataset sin hash registrado no se considera entregado.

## 7. Archivos congelados: ningún paso escribe sobre ellos

Este runbook MUST NOT escribir, ni siquiera de paso, sobre:

- `data/corpus_evaluacion_pseudonimizado.json` (se abre solo en lectura);
- `data/corpus_resultados*.json`;
- `evaluation/predicciones.json`;
- los sidecars versionados como evidencia (`evaluation/evidence/`).

Los datos de la campaña se escriben solo en `evaluation/data/campana/`. Los comandos de este runbook que escriben (sub-planes, `brazo_manual.csv`, `intervenciones.csv`) tienen destinos de esa carpeta o fuera del repositorio, y el export se **niega** a escribir (código de salida `2`, sin tocar el archivo) si se lo apunta a cualquiera de esos archivos. Verificación al terminar cada sesión, desde la raíz:

```bash
git status --short data/ evaluation/predicciones.json evaluation/evidence/ evaluation/report.md
git diff --stat -- data/ evaluation/predicciones.json evaluation/evidence/ evaluation/report.md
```

Se acepta si ambos comandos no imprimen nada. Si imprimen algo, se descarta el cambio (`git checkout -- <archivo>`) y se informa: nunca se "arregla" un congelado para que coincida con la campaña.

## 8. Limitaciones declaradas

- **Sin operadores independientes**: si no se consiguen `O1`/`O2` distintos de los etiquetadores, los analistas originales y los autores, la medición se registra igual, pero se rotula como **limitación** (no como brazo independiente) en `evaluation/data/campana/README.md`, con los roles solapados. c-167 rechaza por defecto un registro con solape; cómo analizarlo se decide con c-167 y c-169, pero el solape no se oculta.
- **`muestreo` sin superficie de UI**: la cola de la app solo lista logs marcados para revisión. Un origen `muestreo` solo se produce validando por la API (`PATCH /api/v1/clasificaciones/{log_id}/validar`) un log no marcado. Si el diseño de la campaña lo requiere, se hace por la API con la cuenta de un operador; si no, el desglose por origen muestra cero en `muestreo`.
- **`completado_manual` sin escritor**: el valor está reservado; ningún flujo de c-165 lo escribe.
- **Una sola intervención por log**: gana la última escritura. Un log re-derivado después de validarse queda con origen `rederivacion` y el origen previo no se conserva.
- **Inicio declarado por el cliente**: `intervencion_inicio_en` depende del reloj de quien valida. Una duración negativa se anula y se cuenta; no se corrige.

## 9. Si algo falla

| Síntoma | Qué hacer |
|---|---|
| El validador sale con un código distinto de `0` | Leer las ofensas que imprime (regla, `id_caso`, operador). Corregir el registro de origen del operador y volver a validar. No editar la planilla unida a mano sin dejar constancia |
| `BrazoManualError` en 4.2 | El mensaje nombra operador, caso y campo. Suele ser un `inicio` sin zona horaria o un caso repetido; corregir en el registro de origen |
| El export dice que falta `INTERVENCION_EXPORT_HMAC_KEY` | Definir la variable en esa terminal (5.3, paso 1). No se pega la clave en el comando ni en un archivo del repositorio |
| El export dice que es un archivo congelado | La ruta `--salida` apunta a uno de la sección 7. Usar `../../evaluation/data/campana/intervenciones.csv` |
| El export dice que no existe o no es válido un sidecar | Revisar que el archivo exista y sea una lista JSON con `case_id` e `incidente_id` (lo escriben los harnesses de c-166) |
| `actor_alias` vacío en muchas filas | La cuenta que validó no tenía empleado activo vinculado, o el empleado se purgó antes del export (sección 5.3). No se reconstruye retroactivamente |
| La verificación 5.4 informa problemas | No se versiona. Se corrige la causa en la base o en el comando y se vuelve a exportar (el export sobrescribe la salida) |
