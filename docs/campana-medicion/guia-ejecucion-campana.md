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

### 1.0 Decisiones, antes de empezar

1. **Cantidad de casos**: por defecto los 200 del plan. Menos casos se justifican y se
   declaran.
2. **Semilla** del plan: un entero, elegido una sola vez, que se registra.
3. **Submuestra con doble cobertura**: opcional. Si se hace, se fija el criterio antes (p.
   ej. un caso de cada diez) y se registra.
4. **Codebook**: ya está compilado y congelado en
   `evaluation/data/campana/codebook_doble_etiquetado.md` (SHA-256
   `d9777139e9eaffe7903fa63d69d2bee346ff2b43599409aedaaebd21a8be9167`). No se modifica.

### 1.1 Rellenar el registro de sujetos

Archivo: `evaluation/data/campana/registro_sujetos.csv` (la plantilla ya trae las filas;
solo falta la columna `persona`). Reglas:

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
- A `O1` y `O2`: su **hoja del operador** (100 casos cada uno) + el codebook + la plantilla.
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

```bash
# corpus de campaña y subplanes
python -m evaluation.plan_campana preparar-corpus --origen data/corpus_evaluacion_pseudonimizado.json \
  --destino evaluation/data/campana/corpus_campana.json
python -m evaluation.plan_campana subplan --plan evaluation/data/campana/plan_campana.csv \
  --mitad 1 --brazo manual --turno 1 --salida evaluation/data/campana/subplan_m1_manual_t1.csv

# export de intervenciones (desde App/Backend, con la app de pie)
export INTERVENCION_EXPORT_HMAC_KEY='<clave secreta, la misma en toda la campaña>'
python -m scripts.exportar_intervenciones --sidecar <cada sidecar> \
  --desde AAAA-MM-DD --hasta AAAA-MM-DD --salida ../../evaluation/data/campana/intervenciones.csv

# ensamblar las dos entradas del análisis (c-170)
python -m evaluation.preparar_entradas_analisis --entrada evaluation/data/campana \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json

# análisis final (solo lectura)
python -m evaluation.analisis_campana --entrada evaluation/data/campana \
  --salida evaluation/data/campana/analisis \
  --pines-in-sample '{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}' \
  --rango-google-genai-vigente ">=2.33,<3"
```

### 1.6 Verificar el gate de c-169 y cerrar

La campaña está "terminada" cuando existen, con SHA-256 en el README de la carpeta:
`doble_etiquetado.csv`, `plan_campana.csv`, `intervenciones.csv`, `plantilla_etiquetado.csv`,
`predicciones_in_sample.json`, `registro_sujetos.csv` y `analisis/` (más
`predicciones_independiente.json` si se corrió la validación fuera de muestra). Ahí se aplica
`c-169`.

---

## 2. Instrucciones para los etiquetadores (E1 y E2)

> Se les entrega: la hoja ciega, el codebook y una copia vacía de la plantilla. Nada más.

Ustedes van a **etiquetar incidentes**. La tarea es simple: leer la descripción de cada caso
y elegir el sector que le corresponde.

**Qué reciben**

- Una planilla con dos columnas: el `id_caso` y la descripción del incidente.
- El **codebook**: la lista de los cinco sectores y cómo elegir.
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

**Al terminar**: entregar el archivo al director (Luca). No se lo pasan entre ustedes.

---

## 3. Instrucciones para los operadores (O1 y O2)

> Se les entrega: su hoja de casos, el codebook y la plantilla. Nada más.

Van a **clasificar manualmente un conjunto de casos** (la "mitad" que les toque) y, en la
aplicación, **revisar las clasificaciones del sistema** según se les indique.

**Qué reciben**

- Una hoja con los casos que les toca (100 cada uno), en un orden determinado.
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
