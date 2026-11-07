# Guía de ejecución de la campaña de medición (c-165 a c-169)

Esta guía es el **punto de entrada único** para correr la campaña de medición: qué hay que
hacer, en qué orden, y qué se le entrega a cada colaborador. El detalle exhaustivo de cada
procedimiento vive en los runbooks de esta misma carpeta:

- `runbook-doble-etiquetado.md` (etiquetadores `E1`/`E2`).
- `runbook-brazo-manual-e-intervencion.md` (`O1`/`O2` y la intervención).
- `runbook-campana-contrabalanceada.md` (plan y brazo automatizado).
- `runbook-corpus-independiente.md` (validación fuera de muestra).
- `plan-campana-de-medicion.md` (plan general).

---

## 0. Qué mide y con quién

Cinco mediciones (los ítems que el dictamen CONEAU dejó abiertos):

- **(a)** Exactitud del brazo manual (qué tan bien clasifica una persona frente a una
  referencia independiente).
- **(b)** Tasa de intervención humana real (cuántos casos del flujo automatizado requieren
  acción manual).
- **(c)** Efecto de orden (de condición y de posición) sobre el tiempo del operador.
- **(d)** Validación fuera de muestra (el clasificador sobre un corpus nuevo).
- **(e)** Intervalo de confianza del kappa (acuerdo entre dos etiquetadores).

**Cuatro colaboradores y el director.** Todos los alias se registran en
`evaluation/data/campana/registro_sujetos.csv`:

| Alias | Rol | Función |
|---|---|---|
| `E1`, `E2` | etiquetador | doble etiquetado del corpus (ítem e y la referencia del ítem a) |
| `O1`, `O2` | operador | brazo manual (ítems a y c) e intervención en la app (ítem b) |
| — | director | custodia, coordinación y los pasos offline |

**Regla de independencia (inegociable).** `E1`, `E2`, `O1`, `O2` deben ser personas:
distintas entre sí, distintas de los dos analistas originales y distintas de los autores.
Ninguna persona puede ocupar dos roles. No se puede simular ni alterar esto: si hay solape,
se declara como limitación (ver sección 4).

---

## 1. Checklist del director

**Prerequisitos de entorno (antes de empezar).** La base de la campaña debe estar en la
revisión `024 (head)`: desde `App/Backend`, `alembic current` debe informar `024 (head)`; si
informa una revisión anterior, aplicar `alembic upgrade head` ANTES de empezar (las
intervenciones previas a la `024` no tienen metadatos y el export las excluye). La aplicación
y N8N deben estar en pie (`docker compose up -d`, `docker compose ps`): el export de
intervenciones lee la base y el brazo automatizado pasa por el flujo N8N real. Tener Python
con las dependencias de `evaluation/` y de `App/Backend/`.

### 1.0 Decisiones, antes de empezar

1. **Cantidad de casos**: por defecto los 200 del plan. Menos casos se justifican y se
   declaran.
2. **Semilla** del plan: un entero, elegido una sola vez, que se registra.
3. **Submuestra con doble cobertura**: fija. El criterio es un caso de cada diez por
   `posicion` dentro de cada mitad (mitad 1: posiciones 10, 20, ..., 100; mitad 2: posiciones
   110, 120, ..., 200): 20 casos compartidos en total. `O1` recibe 110 casos (100 de su mitad
   + 10 cruzados de la otra) y `O2` recibe 110. El criterio está registrado en
   `evaluation/data/campana/README.md` y no se cambia.
4. **Codebook**: ya está compilado y congelado en
   `evaluation/data/campana/codebook_doble_etiquetado.md` (SHA-256
   `d9777139e9eaffe7903fa63d69d2bee346ff2b43599409aedaaebd21a8be9167`). No se modifica.

### 1.1 Rellenar el registro de sujetos

Archivo: `evaluation/data/campana/registro_sujetos.csv` (registro completo: 8 filas, un código
`P1`..`P8` por persona, sin solapes por `persona`). Reglas:

- `persona` es un código `P<n>` que el **director** asigna a cada persona real; la
  correspondencia código-identidad se guarda **fuera del repositorio**.
- **La misma persona lleva el mismo código en todos los roles que tenga.** Si una persona
  ocupa dos roles, repite su `P<n>` en ambas filas (eso es lo que delata el solape).
- No se agregan nombres, correos ni legajos.

Verificación (debe imprimir `sin solapes`):

```bash
python - <<'EOF'
import collections, csv
filas = list(csv.DictReader(open("evaluation/data/campana/registro_sujetos.csv", encoding="utf-8", newline="")))
roles = collections.defaultdict(set)
for fila in filas:
    roles[fila["persona"]].add(fila["rol"])
print({p: sorted(r) for p, r in roles.items() if len(r) > 1} or "sin solapes")
EOF
```

### 1.2 Generar el plan

```bash
python -m evaluation.plan_campana generar \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --modo aleatorio --seed <entero> \
  --salida evaluation/data/campana/plan_campana.csv
```

Debe dar 200 casos con reparto balanceado. Anotar el SHA-256 en el README de la carpeta.

### 1.3 Repartir el trabajo y recogerlo

- A `E1` y `E2`: la **hoja ciega** (200 casos, solo `id_caso` + descripción) + el codebook +
  una copia vacía de la plantilla. Instrucciones: **sección 2**.
- A `O1` y `O2`: su **hoja del operador** (110 casos cada uno: 100 de su mitad + 10 cruzados de la otra; 20 casos compartidos) + el codebook + la plantilla.
  Instrucciones: **sección 3**.
- Cada colaborador entrega su archivo **al director**, no al otro colaborador.

### 1.4 Unir, validar y versionar las planillas

Doble etiquetado:

```bash
{ cat etiquetas_E1.csv; tail -n +2 etiquetas_E2.csv; } > doble_etiquetado.csv
python -m evaluation.doble_etiquetado --planilla doble_etiquetado.csv \
  --corpus data/corpus_evaluacion_pseudonimizado.json --tarea doble_etiquetado   # exit 0
sed -i 's/\r$//' doble_etiquetado.csv
cp doble_etiquetado.csv evaluation/data/campana/doble_etiquetado.csv
sha256sum evaluation/data/campana/doble_etiquetado.csv
```

Brazo manual (igual, con `--tarea brazo_manual` y `brazo_manual.csv`). Un archivo individual
de un solo colaborador **no** valida por diseño.

### 1.5 Pasos offline (los corre el director, con ayuda del agente)

El orden importa: el brazo automatizado va **después** de generar los sub-planes y **antes**
del export de intervenciones, porque el export consume los sidecars que producen los
harnesses. El detalle completo de los sub-planes y de los harnesses está en
`runbook-campana-contrabalanceada.md`, secciones 2 a 6.

#### 1.5.1 Corpus de campaña y sub-planes

Se prepara la copia de campaña del corpus y se generan los **8 sub-planes**
(2 mitades x 2 brazos x 2 turnos), con el patrón `subplan_m<mitad>_<brazo>_t<turno>.csv`:

```bash
python -m evaluation.plan_campana preparar-corpus \
  --origen data/corpus_evaluacion_pseudonimizado.json \
  --destino evaluation/data/campana/corpus_campana.json

for mitad in 1 2; do
  for brazo in manual automatizado; do
    for turno in 1 2; do
      python -m evaluation.plan_campana subplan \
        --plan evaluation/data/campana/plan_campana.csv \
        --mitad $mitad --brazo $brazo --turno $turno \
        --salida evaluation/data/campana/subplan_m${mitad}_${brazo}_t${turno}.csv
    done
  done
done
```

Los 8 sub-planes son:

- `subplan_m1_manual_t1.csv` (`O1`, mitad 1, turno 1)
- `subplan_m1_manual_t2.csv` (`O1`, mitad 1, turno 2)
- `subplan_m1_automatizado_t1.csv` (brazo automatizado, mitad 1, turno 1)
- `subplan_m1_automatizado_t2.csv` (brazo automatizado, mitad 1, turno 2)
- `subplan_m2_manual_t1.csv` (`O2`, mitad 2, turno 1)
- `subplan_m2_manual_t2.csv` (`O2`, mitad 2, turno 2)
- `subplan_m2_automatizado_t1.csv` (brazo automatizado, mitad 2, turno 1)
- `subplan_m2_automatizado_t2.csv` (brazo automatizado, mitad 2, turno 2)

Los cuatro `manual` son los que siguen `O1`/`O2` (reparto por defecto: `O1` mitad 1, `O2`
mitad 2); sus SHA-256 ya están declarados en `evaluation/data/campana/README.md`. Los cuatro
`automatizado` los corre el brazo automatizado (1.5.2).

#### 1.5.2 Brazo automatizado

Con los 4 sub-planes `automatizado` se corren los tres harnesses de ingesta, **primero con
`--dry-run`** (cuenta los casos sin red ni escritura) y después sin él. Cada corrida usa un
`--id-corrida` único y su propio sidecar `evaluation/data/campana/sidecar_<id_corrida>.json`;
el `--json` apunta a la copia de campaña `corpus_campana.json`. Detalle completo:
`runbook-campana-contrabalanceada.md`, sección 5. Un ejemplo por harness:

```bash
# web y correo, por el flujo N8N real
python scripts/corpus_ingest/ingest_via_n8n.py \
  --plan evaluation/data/campana/subplan_m1_automatizado_t1.csv \
  --id-corrida m1-automatizado-t1 \
  --json evaluation/data/campana/corpus_campana.json \
  --sidecar evaluation/data/campana/sidecar_m1-automatizado-t1.json

# backend directo (mismos flags; su fuente son el CSV/XLSX locales)
python scripts/corpus_ingest/ingest_corpus.py \
  --plan evaluation/data/campana/subplan_m1_automatizado_t1.csv \
  --id-corrida m1-automatizado-t1 \
  --json evaluation/data/campana/corpus_campana.json \
  --sidecar evaluation/data/campana/sidecar_m1-automatizado-t1.json

# telefonía (NO ingesta: el operador del softphone hace las llamadas siguiendo el plan;
# el harness lee las mediciones)
python scripts/corpus_ingest/ingest_telefonia_corpus.py \
  --insecure \
  --sleep 1.1 \
  --plan evaluation/data/campana/subplan_m1_automatizado_t1.csv \
  --id-corrida m1-automatizado-t1-tel \
  --json evaluation/data/campana/corpus_campana.json \
  --sidecar evaluation/data/campana/sidecar_m1-automatizado-t1-tel.json
```

Cada harness se repite una vez por cada sub-plan `automatizado` (4 en total) con su
`--id-corrida` y su `--sidecar` propios, siempre con `--dry-run` primero. Los ejemplos de
telefonía llevan `--insecure` (el default `--base-url https://localhost` apunta al
certificado autofirmado de nginx) y `--sleep 1.1`, que espacia los requests consecutivos
para respetar el límite de nginx `webhook_limit` (60 r/m sobre `/api/v1/telefonia/`, ~55 r/m
con el default) y evita los 429 por ráfaga al recuperar los 81 casos; aplica a las 4 corridas
por sub-plan `automatizado`. Los **sidecars** (`evaluation/data/campana/sidecar_<id_corrida>.json`, uno por corrida) son las
entradas que produce este paso y las que consume el export de 1.5.3. Los CSV/XLSX locales con
datos personales no se versionan: los datos de campaña viven solo en el sidecar y en la copia
de campaña.

##### 1.5.2.1 Brazo de telefonía (softphone)

El brazo de telefonía corre sobre el **stack principal** de la campaña (nginx base + el
dominio ngrok reservado), NO sobre el perfil corpus aislado de
`docs/runbook-corpus-telefonia.md` (c-70): ese perfil usa una base descartable y la campaña
no lo usa. El detalle del softphone (variables, setup de Twilio, arranque y colocación de la
llamada) vive en `scripts/voip_softphone/README.md`, que es la **fuente de verdad única**;
acá se repite solo el mínimo operativo.

**Quién llama y en qué orden.** Cada sub-plan `automatizado` tiene su mitad asignada a `O1`
(mitad 1) o `O2` (mitad 2). El operador realiza las llamadas **en orden de `posicion`**,
eligiendo el `corpus_case_id` de cada caso en la lista de casos telefónicos del corpus. En
total son 81 llamadas (m1-t1=16, m1-t2=24, m2-t1=18, m2-t2=23).

**Arranque del softphone.** Con el stack principal y el túnel ngrok arriba:

```bash
python3 scripts/voip_softphone/mint_token.py serve
```

Sirve la página y un token fresco por request desde el mismo origen de loopback. Abrir
`http://127.0.0.1:8765/`, elegir **Caso del corpus (teléfono)**, presionar **Call**, recitar
el texto del caso por el micrófono y presionar **Hangup** al terminar. La herramienta no
reproduce audio (no hay TTS ni playback).

> **Gate por caso (c-174).** Con un caso seleccionado, `Call` queda deshabilitado tras
> colgar hasta que el incidente quede persistido (la página consulta la sonda
> `GET /case-status`). Requiere exportar `INGEST_OPERATOR_USERNAME` /
> `INGEST_OPERATOR_PASSWORD` y puede necesitar `--insecure`. El detalle de la sonda y de
> los flags vive en `scripts/voip_softphone/README.md` (sección 4.b), que es la fuente de
> verdad única; no duplicar acá.

**Prerequisito de la guarda de costo.** El stack base usa `COST_GUARD_RATE_LIMIT_CALLS=30`
(rate global, 1 h) y `COST_GUARD_CALLER_RATE_LIMIT_CALLS=3` (por origen, 1 h)
(`App/Backend/app/config/settings.py:192-194`). Con 81 llamadas, la llamada 31 se deniega.
Antes de correr el brazo, subir el rate global (por ejemplo a 200) en `App/Backend/.env` (el
`env_file` del servicio `backend`) y recrear el servicio para que tome el valor:

```bash
docker compose up -d backend
```

El rate por origen (3/h) no es obstáculo: `mint_token.py` acuña una identidad única por
sesión, de modo que la clave `caller` cambia y el 3/h no se agota; el global de 30/h SIGUE
aplicando. Solo el perfil aislado `corpus` relaja el rate a 200
(`docker-compose.yml:348-354`) y la campaña NO corre en ese perfil.

**Prerequisitos de Twilio.** Los números Twilio, la Voice URL del TwiML App y
`BACKEND_PUBLIC_BASE_URL` (`App/Backend/.env:14`) deben ser el MISMO dominio ngrok reservado
`tameness-trilogy-unrefined.ngrok-free.dev`. `TWILIO_ACCOUNT_SID` proviene de
`App/Backend/.env`; `TWILIO_API_KEY_SID`, `TWILIO_API_KEY_SECRET` y `TWILIO_TWIML_APP_SID`
de `scripts/voip_softphone/softphone.env` (gitignored).

#### 1.5.3 Export de intervenciones (desde `App/Backend`, con la app de pie)

```bash
cd App/Backend
export INTERVENCION_EXPORT_HMAC_KEY='<clave secreta, la misma en toda la campaña>'
ARGS=""; for f in ../../evaluation/data/campana/sidecar_*.json; do ARGS="$ARGS --sidecar $f"; done
python -m scripts.exportar_intervenciones $ARGS \
  --desde AAAA-MM-DD --hasta AAAA-MM-DD \
  --salida ../../evaluation/data/campana/intervenciones.csv
cd ../..
```

El comando imprime un resumen (filas exportadas, logs **legados** excluidos, filas sin
`id_caso` y filas sin `duracion_s`): guardarlo. La verificación de salida del export
(columnas exactas, orígenes del vocabulario, alias de 12 hex, sectores canónicos y sin
correos) es la sección 5.4 de `runbook-brazo-manual-e-intervencion.md` y debe imprimir
`sin problemas`. Del resumen del comando se declaran los **legados** (logs previos a la
migración `024`) y los **vínculos faltantes** (filas sin `id_caso` o sin `duracion_s`) en
`evaluation/data/campana/README.md`.

#### 1.5.4 Ensamblar las entradas del análisis (c-170)

```bash
python -m evaluation.preparar_entradas_analisis --entrada evaluation/data/campana \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json
```

#### 1.5.5 Análisis final (solo lectura)

```bash
python -m evaluation.analisis_campana --entrada evaluation/data/campana \
  --salida evaluation/data/campana/analisis \
  --pines-in-sample '{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}' \
  --rango-google-genai-vigente ">=2.33,<3"
```

### 1.6 Verificar el gate de c-169 y cerrar

La campaña está "terminada" cuando existen, con SHA-256 en el README de la carpeta:
`brazo_manual.csv`, `doble_etiquetado.csv`, `plan_campana.csv`, `intervenciones.csv`,
`plantilla_etiquetado.csv`, `predicciones_in_sample.json`, `registro_sujetos.csv` y
`analisis/` (más `predicciones_independiente.json` si se corrió la validación fuera de
muestra). Ahí se aplica `c-169`.

---

## 2. Instrucciones para los etiquetadores (E1 y E2)

> Se les entrega: la hoja ciega, el codebook y una copia vacía de la plantilla. Nada más.

Ustedes van a **etiquetar incidentes**. La tarea es simple: leer la descripción de cada caso
y elegir el sector que le corresponde.

**Qué reciben**

- Una planilla con dos columnas: el `id_caso` y la descripción del incidente.
- El **codebook**: la lista de los cinco sectores y cómo elegir. Las cinco cadenas
  canónicas, exactas y sin tildes, son `Seguridad Informatica`, `Soporte Tecnico Hardware`,
  `Soporte Tecnico Software`, `Bases de Datos` y `Sistemas`.
- Una plantilla vacía con las columnas a completar.

**Qué tienen que hacer**

Una fila por cada caso (son 200), completando estas columnas:

| Columna | Qué poner |
|---|---|
| `id_caso` | el identificador del caso (por ejemplo `R017`) |
| `id_etiquetador` | su alias: `E1` o `E2` |
| `tarea` | siempre `doble_etiquetado` |
| `sector_etiquetado` | **un** sector principal, una de las cinco cadenas exactas |
| `sectores_adicionales_etiquetados` | si el caso toca otros sectores, separados por `|` sin espacios (ejemplo `Sistemas|Bases de Datos`); si no, se deja vacío |
| `inicio` | puede quedar vacío |
| `timestamp` | la fecha y hora en que terminaron el caso, por ejemplo `2026-11-03T14:05:00-03:00` |

Ejemplo de fila:

```
R017,E1,doble_etiquetado,Soporte Tecnico Software,Sistemas,2026-11-03T14:00:00-03:00,2026-11-03T14:01:10-03:00
```

**Reglas importantes**

- Usar exactamente las cadenas del codebook, con mayúsculas y sin tildes. Cualquier variante
  (con tilde, en minúsculas, "Operaciones") se rechaza.
- Elegir **un** sector principal; los adicionales son solo si el caso toca más de un área.
- No agregar columnas de más (nombre, correo, etc.): rompen la validación.
- Si completan en Excel/Sheets, exportar como **CSV UTF-8 (sin BOM), separador coma**, y
  dejar `inicio`/`timestamp` como texto.

**Cómo trabajar**

- Cada uno trabaja **por separado**: no se muestran las etiquetas al otro hasta que ambos
  terminaron, ni se consulta el resultado del sistema automático.
- Ante un caso dudoso, se guían por el codebook; no hay respuestas "correctas" que buscar.

**Al terminar**: entregar el archivo al director de la tesis. No se lo pasan entre ustedes.

---

## 3. Instrucciones para los operadores (O1 y O2)

> Se les entrega: su hoja de casos, el codebook y la plantilla. Nada más.

Van a **clasificar manualmente un conjunto de casos** (la "mitad" que les toque) y, en la
aplicación, **revisar las clasificaciones del sistema** según se les indique.

**Qué reciben**

- Una hoja con los casos que les toca (110 cada uno: 100 de su mitad + 10 cruzados de la otra; 20 casos compartidos), en un orden determinado.
- El **codebook** (la lista de los cinco sectores).
- La plantilla para registrar.

**Qué tienen que hacer en la hoja**

Una fila por caso, en el orden de la hoja:

| Columna | Qué poner |
|---|---|
| `id_caso` | el identificador del caso |
| `id_etiquetador` | su alias: `O1` o `O2` |
| `tarea` | siempre `brazo_manual` |
| `sector_etiquetado` | el sector que ustedes asignan |
| `sectores_adicionales_etiquetados` | opcional, igual que en la sección 2 |
| `inicio` | **obligatorio**: la hora en que empezaron el caso |
| `timestamp` | **obligatorio**: la hora en que terminaron |

Las horas de `inicio` y `timestamp` son lo que permite medir el efecto de orden; sirven para
eso y no hay que apurarse ni cronometrar aparte.

**En la aplicación**: cuando se les indique, validarán o reasignarán casos del flujo
automático. Cada acción queda registrada automáticamente; no hay que anotar nada a mano.

**Cómo trabajar**

- Seguir el orden de la hoja al pie de la letra (el orden importa).
- No mirar las predicciones del sistema antes de clasificar manualmente.

**Al terminar**: entregar el archivo al director.

---

## 4. Qué NO se puede hacer (para no invalidar la medición)

- **No** completar roles que no corresponden a personas reales, ni repetir una persona en dos
  roles para "llegar a cuatro".
- **No** reutilizar a los autores ni a los analistas originales como `E` u `O`.
- **No** cambiar los códigos `P<n>` para ocultar un solape: si existe, se declara.
- **No** presentar como "etiquetado ciego" un trabajo donde los roles se solapan.
- **No** recalibrar el clasificador después de ver el corpus independiente.

Si por restricciones no se consiguen las cuatro personas independientes, se aplica la
sección 9 del runbook de doble etiquetado: se etiqueta igual y se registra
`estado_cegado: limitacion_declarada`, y los ítems afectados se reportan **como limitación**.
