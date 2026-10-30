# Runbook: doble etiquetado independiente (c-168)

Procedimiento para producir la **tabla primaria del doble etiquetado**: la planilla etiquetador x caso con la que se calcula el kappa de Cohen con su intervalo de confianza. El kappa `0,87` de la tesis se reporta sin intervalo porque esa tabla no se conservó (`docs/Tesis/Correcciones/numeros-canonicos.md`); además, los dos analistas que fijaron aquel consenso son las mismas personas que operaron el brazo manual, de modo que no sirven como etiquetadores independientes. Este runbook define quién etiqueta, qué ve, con qué criterio, cómo se valida y cómo se conserva la tabla.

El etiquetado corre **fuera del repositorio**. El repositorio entrega la plantilla (`evaluation/data/plantilla_etiquetado.csv`), el validador (`evaluation/doble_etiquetado.py`) y este procedimiento. El cálculo del kappa y de la exactitud del brazo manual es de c-167; la incorporación a la tesis es de c-169.

Todo se ejecuta desde la raíz del repositorio, sin red.

## 0. Antes de empezar

1. Estar en el commit de la campaña y tener Python con las dependencias de `evaluation/` (`pip install -r evaluation/requirements.txt`).
2. Verificar que el validador funciona en esta máquina con la planilla SINTÉTICA de prueba (no son datos reales):

   ```bash
   python -m evaluation.doble_etiquetado \
     --planilla evaluation/tests/fixtures/campana/doble_etiquetado_fixture.csv \
     --corpus evaluation/tests/fixtures/corpus_fixture.json \
     --tarea doble_etiquetado
   ```

   Salida esperada: `OK: planilla valida (tarea=doble_etiquetado, n_casos=9, n_registros=18, etiquetadores=E1,E2)` y exit code `0`.
3. Tener el director de la tesis como **custodio** de la correspondencia entre personas e identidades (sección 1). Esa correspondencia no entra al repositorio.

## 1. Sujetos

### 1.1 Quién puede ser etiquetador

`E1` y `E2` MUST ser personas:

- distintas entre sí;
- distintas de los **dos analistas originales** que fijaron el consenso `sector_asignado` del corpus;
- distintas de los **autores** de la tesis;
- distintas de los **operadores del brazo manual** (`O*`: `O1`, `O2`, c-165).

Una persona propuesta que coincide con cualquiera de esos roles es **inelegible**: se la reemplaza o, si no hay reemplazo, se declara la limitación (sección 9). Conviene que conozcan el dominio de la mesa de ayuda, pero esa no es una condición de elegibilidad: las exclusiones de arriba sí lo son.

### 1.2 Registro de sujetos

Se mantiene `evaluation/data/campana/registro_sujetos.csv`, **sin nombres, correos ni legajos**. Columnas:

| Columna | Contenido |
|---|---|
| `alias` | Alias del rol: `E1`, `E2` (etiquetadores), `O1`, `O2` (operadores), `A1`, `A2` (analistas originales), `T1`, `T2`, ... (autores, uno por autor) |
| `rol` | `etiquetador`, `operador`, `analista_original` o `autor` |
| `persona` | Código seudónimo `P<n>`, **estable entre roles**: la misma persona lleva el mismo código en todos los roles que tenga |

El director asigna un código `P<n>` por cada persona real y custodia la correspondencia código-identidad **fuera del repositorio**. Los alias son específicos de cada rol, por lo que no sirven para detectar que una persona ocupa dos roles: el solape se detecta por `persona`.

Ejemplo (SINTÉTICO, solo ilustra el formato):

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

Regla de aceptación del registro: **cada `persona` figura con un solo rol**. Verificarlo antes de etiquetar:

```bash
python - <<'EOF'
import collections, csv
filas = list(csv.DictReader(open("evaluation/data/campana/registro_sujetos.csv", encoding="utf-8", newline="")))
roles = collections.defaultdict(set)
for fila in filas:
    roles[fila["persona"]].add(fila["rol"])
solapes = {persona: sorted(r) for persona, r in roles.items() if len(r) > 1}
print(solapes or "sin solapes")
EOF
```

Si imprime `sin solapes`, el registro es válido. Si imprime personas con más de un rol, hay solape: aplicar la sección 9. **No** se corrige un solape cambiando códigos `P<n>` para que desaparezca: el registro debe reflejar a las personas reales.

El registro se agrega al repositorio después de la campaña, junto con la tabla, y c-167 lo consume para rechazar solapes.

## 2. Cegado

Los etiquetadores MUST NOT ver, en ningún momento:

- `sector_asignado` ni `sectores_adicionales` del corpus (el consenso original);
- la **predicción del clasificador** (ni de v9 ni de ninguna corrida);
- las etiquetas del otro etiquetador.

Reciben **solo `id_caso` y la descripción pseudonimizada**. Cada uno trabaja solo, sobre su propia copia, sin comunicarse con el otro hasta que ambos entregaron.

### 2.1 Preparar la hoja ciega

El corpus (`data/corpus_evaluacion_pseudonimizado.json`) trae columnas de verdad y de tiempos que NO se entregan. La hoja ciega se genera con solo dos columnas:

```bash
python - <<'EOF'
import csv, json
corpus = json.load(open("data/corpus_evaluacion_pseudonimizado.json", encoding="utf-8"))
with open("hoja_ciega.csv", "w", encoding="utf-8", newline="") as f:
    escritor = csv.writer(f, lineterminator="\n")
    escritor.writerow(["id_caso", "descripcion"])
    for caso in corpus["casos"]:
        escritor.writerow([caso["id"], caso["descripcion"]])
EOF
```

Verificar `head -1 hoja_ciega.csv` (debe ser exactamente `id_caso,descripcion`) y `wc -l hoja_ciega.csv` (201 líneas: encabezado más 200 casos). La hoja contiene descripciones pseudonimizadas: **no se versiona** ni se deja dentro del repositorio; se genera fuera de él o se borra al terminar. Los textos son pseudonimizados (Ley 25.326), pero siguen siendo datos del organismo.

### 2.2 Entrega a cada etiquetador

Cada etiquetador recibe: la hoja ciega, **una copia vacía** de `evaluation/data/plantilla_etiquetado.csv` (solo encabezado) y el codebook congelado (sección 3). Nada más. En particular, no reciben el corpus JSON, `evaluation/report.md`, `evaluation/predicciones.json` ni material del clasificador.

## 3. Codebook

El codebook es el mismo para ambos etiquetadores y se **congela antes de etiquetar**: una vez entregado, no se modifica; si se encuentra un error, se documenta y se reinicia el etiquetado de ambos.

### 3.1 Fuentes (todas ya versionadas)

Se arma un único documento operativo con:

1. `openspec/specs/sector-taxonomy/spec.md`, **solo TAX-001**: las cinco cadenas exactas, sensibles a mayúsculas y sin tildes; `Operaciones` no existe; `Sistemas` es una categoría propia (servidor en producción o sistema corporativo sin encuadre específico de seguridad, hardware, software o datos).
2. `docs/anexo_f_corpus.md`: la verdad es multietiqueta, `{sector_asignado} ∪ sectores_adicionales`, con las invariantes (un único sector principal; los adicionales no lo repiten; todo valor es canónico).
3. `knowledge-base/05_reglas_de_negocio.md`, regla **RN-CL-01**: exactamente un sector principal y opcionalmente adicionales, entre los cinco canónicos.
4. El criterio de etiqueta primaria para casos multicategoría de la tesis (`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex`, línea 53): los casos con pertenencia a más de un sector se conservan y se les asigna **una etiqueta primaria** como sector responsable.

### 3.2 Exclusiones

El codebook MUST NOT incluir materiales del clasificador, porque expondrían el criterio del sistema evaluado y circularizarían la referencia: ni `docs/prompt_gemini.txt`, ni el mapa de keywords, ni TAX-002 y TAX-004 de `sector-taxonomy` (describen el clasificador y las reglas de frontera de su prompt), ni los resultados de `evaluation/`.

### 3.3 Congelado

1. Compilar el documento (por ejemplo `codebook_doble_etiquetado.md`) con las cuatro fuentes y la instrucción de uso: etiqueta primaria única más adicionales opcionales, cadenas exactas.
2. Calcular su SHA-256 y registrarlo como `codebook_sha256` en `evaluation/data/campana/README.md` (sección 7). El documento puede conservarse junto a la tabla: no contiene PII.

### 3.4 Alcance declarado

No hay un codebook conservado del etiquetado original, así que **no es verificable que este codebook sea el mismo que usaron los analistas originales**. Esto se declara; el kappa nuevo mide el acuerdo entre `E1` y `E2` con este codebook, no reproduce el `0,87`.

## 4. Tamaño

- **Corpus de ajuste**: los **200 casos completos** (`R001`..`R200`). No se etiqueta un subconjunto.
- **Corpus independiente** (c-166): se usa la misma plantilla y el mismo validador; los `id_caso` llevan prefijo `I` (`I001`..). Se valida contra el JSON de ese corpus, no contra el de ajuste (el validador no impone prefijos: solo exige que cada `id_caso` exista en el corpus indicado). El armado del corpus independiente está en el runbook de c-166 (`docs/campana-medicion/runbook-corpus-independiente.md`).

## 5. Completar la plantilla

Cada etiquetador completa **una fila por caso**, con las siete columnas de la plantilla y en este orden:

| Columna | Qué poner |
|---|---|
| `id_caso` | El `id` del caso en la hoja ciega (`R001`..`R200`) |
| `id_etiquetador` | Su alias: `E1` o `E2` |
| `tarea` | `doble_etiquetado` |
| `sector_etiquetado` | Exactamente una de las cinco cadenas canónicas (etiqueta primaria) |
| `sectores_adicionales_etiquetados` | Lista separada por `\|` sin espacios alrededor; vacío si no hay; sin repetir el sector principal |
| `inicio` | Opcional en esta tarea: instante ISO-8601 **con zona horaria** en que empezó el caso; puede quedar vacío |
| `timestamp` | Instante ISO-8601 **con zona horaria** en que terminó el caso, por ejemplo `2026-11-03T14:05:00-03:00` |

Las cinco cadenas canónicas, exactas y sin tildes, son: `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos` y `Sistemas`. Cualquier otra variante (con tilde, en minúsculas, `Operaciones`) la rechaza el validador.

Fila de ejemplo (SINTÉTICA):

```csv
R017,E1,doble_etiquetado,Soporte Tecnico Software,Sistemas,2026-11-03T14:00:00-03:00,2026-11-03T14:01:10-03:00
```

Notas de formato:

- La columna de la planilla se llama `sector_etiquetado`, no `sector_asignado`: ese nombre queda reservado al consenso del corpus.
- Si se completa en una planilla de cálculo, exportar como **CSV UTF-8 sin BOM, separador coma**, y fijar `inicio` y `timestamp` como texto: los formatos regionales (`03/11/2026 14:05`) los rechaza el validador (regla g).
- No agregar columnas (nombre, correo, legajo, teléfono, descripción): el validador las rechaza (regla h).

Al terminar, cada etiquetador entrega su archivo **al director** (custodio), no al otro etiquetador.

## 6. Unir las dos planillas y validar

El director une los dos archivos en uno solo (un único encabezado):

```bash
{ cat etiquetas_E1.csv; tail -n +2 etiquetas_E2.csv; } > doble_etiquetado.csv
```

Validar contra el corpus indicado:

```bash
python -m evaluation.doble_etiquetado \
  --planilla doble_etiquetado.csv \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --tarea doble_etiquetado
echo $?
```

Un archivo individual (solo `E1` o solo `E2`) no pasa el validador por diseño: falla la regla (a) y la (b). Se valida únicamente la planilla unida.

Códigos de salida:

| Código | Significado |
|---|---|
| `0` | Sin ofensas: planilla válida |
| `10` | (a) Etiquetadores fijos: exactamente dos alias distintos en `doble_etiquetado` (en `brazo_manual`, ambos `O1` y `O2` y ningún tercero) |
| `11` | (b) Cobertura: cada caso del corpus con registro de los dos etiquetadores |
| `12` | (c) Duplicados: a lo sumo un registro por `(id_caso, id_etiquetador, tarea)` |
| `13` | (d) `id_caso` inexistente en el corpus indicado |
| `14` | (e) Sector que no es una de las cinco cadenas canónicas |
| `15` | (f) Un adicional repite el sector principal |
| `16` | (g) `timestamp` (o `inicio`, si se informa) no es ISO-8601 con zona horaria |
| `17` | (h) Columna con PII o alias que no tiene la forma `E<n>` |
| `18` | (i) `tarea` inválida |
| `19` | (j) `inicio` posterior a `timestamp` (obligatorio solo en `brazo_manual`) |
| `2` | Error de uso o archivo ilegible |

El CLI imprime **todas** las ofensas (regla, `id_caso`, `id_etiquetador`, detalle) y sale con el código de la primera regla ofendida en el orden (a)-(j). Corregir y volver a validar hasta obtener `0`.

El validador opera sin red y no modifica la planilla. Para el corpus real, `cargar_corpus` solo reescribiría el JSON si `metadata.total_casos` estuviera desincronizado; el corpus versionado está sincronizado (200), por lo que no cambia. Aun así, verificar con `git status` que `data/corpus_evaluacion_pseudonimizado.json` no aparece modificado.

## 7. Aceptación y versionado de la tabla primaria

La campaña acepta el doble etiquetado solo si se cumple todo lo siguiente:

1. El validador sale con `0` sobre los 200 casos (cobertura completa, sin celdas vacías en las columnas obligatorias).
2. El registro de sujetos no tiene solapes, o la limitación está declarada (sección 9).
3. La tabla primaria queda **versionada con su SHA-256**, como se indica a continuación.

Versionado:

1. Asegurar fin de línea LF y UTF-8 sin BOM, y copiar la planilla validada:

   ```bash
   sed -i 's/\r$//' doble_etiquetado.csv
   cp doble_etiquetado.csv evaluation/data/campana/doble_etiquetado.csv
   ```

2. Calcular el SHA-256 (en minúsculas) de ese archivo:

   ```bash
   sha256sum evaluation/data/campana/doble_etiquetado.csv
   ```

   En PowerShell: `(Get-FileHash -Algorithm SHA256 evaluation\data\campana\doble_etiquetado.csv).Hash.ToLower()`.
3. Completar en `evaluation/data/campana/README.md` la sección "Procedencia de la tabla primaria": `archivo`, `sha256`, `fecha` (`AAAA-MM-DD`), `corpus` y `corpus_sha256`, `tarea`, `comando_de_validacion` (con su resultado `0`), `codebook_sha256` y `estado_cegado` (`cumplido` o `limitacion_declarada`, con `motivo_limitacion`).
4. Agregar `evaluation/data/campana/registro_sujetos.csv` (sección 1.2).
5. Correr el test de integridad, que **deja de omitirse** cuando la tabla existe:

   ```bash
   pytest evaluation/tests/test_doble_etiquetado.py -k tabla_primaria
   ```

   Debe pasar: la tabla valida contra el corpus real y su SHA-256 coincide con el declarado en el README.
6. `.gitattributes` fija LF para `evaluation/data/campana/*.csv`, de modo que el hash coincide en Windows y Linux. Tras `git add`, comprobar que `git status` no muestra la tabla como modificada por cambios de fin de línea.
7. Ensamblar las entradas que consume el análisis de c-167. Una vez que `doble_etiquetado.csv` y `brazo_manual.csv` (sección 4.3 de `runbook-brazo-manual-e-intervencion.md`) están versionados en `evaluation/data/campana/`:

   ```bash
   python -m evaluation.preparar_entradas_analisis \
     --entrada evaluation/data/campana \
     --corpus data/corpus_evaluacion_pseudonimizado.json \
     --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json
   ```

   El comando une las dos planillas C1 en `plantilla_etiquetado.csv` (un único encabezado, LF, sin BOM) y copia byte a byte el cache congelado a `predicciones_in_sample.json`; re-valida cada tarea con `validar_doble_etiquetado` y aborta sin escribir si una fuente falta o no pasa el validador. Imprime el SHA-256 de cada salida y su procedencia: registrarlos en `evaluation/data/campana/README.md`. Es el paso documentado que produce las dos entradas que lee `evaluation/analisis_campana.py` (c-167) y **no se puede saltar en silencio**.

La conservación de esta tabla es criterio de aceptación de la campaña. La cita del hash en `docs/Tesis/Correcciones/numeros-canonicos.md` la hace c-169 al incorporar los resultados.

## 8. Discordancias

- Las discordancias entre `E1` y `E2` (casos donde `sector_etiquetado` difiere) **no se resuelven por consenso a posteriori antes de calcular el kappa**. La tabla primaria queda tal como se registró y el kappa se computa sobre esas etiquetas.
- La **referencia para medir el brazo manual** (c-167) son los casos donde `sector_etiquetado` de `E1` y `E2` **coinciden**. Los discordantes quedan fuera de esa referencia y se **reporta cuántos son**.
- Advertencia declarada: excluir los discordantes sesga la referencia hacia los casos más fáciles; por eso el número excluido se informa siempre junto con la exactitud.
- Si el director quiere analizar las discordancias (por ejemplo para entender patrones de error), lo hace en un documento aparte, sin modificar la tabla primaria.

## 9. Limitación declarada: no se consiguen etiquetadores nuevos

Si por restricciones de campo no se consiguen etiquetadores distintos de los analistas originales, los autores o los operadores:

1. Se etiqueta igual (con el mismo codebook y las mismas reglas de formato) para no perder la tabla.
2. En `evaluation/data/campana/README.md` se registra `estado_cegado: limitacion_declarada` y en `motivo_limitacion` el motivo y los **roles solapados** (por ejemplo, "E2 es también analista_original").
3. El `registro_sujetos.csv` refleja el solape con la misma `persona` bajo ambos roles. El análisis de c-167 rechaza por defecto un registro con solape: cómo analizar ese caso se decide con c-167 y c-169, pero **no** se oculta el solape.
4. El resultado se reporta como **limitación y NO como etiquetado ciego**. Presentarlo como cegado está prohibido (c-169 lo reporta con el estado del README).

El valor esperado en el caso normal es `estado_cegado: cumplido`.

## 10. Recuperación manual de una tabla parcial

Si reaparece una tabla parcial del etiquetado original (etiquetas por analista original para algunos casos):

- **El camino por defecto sigue siendo el re-etiquetado** (secciones 1 a 7). Esta ruta es solo un respaldo.
- **No hay código de importación**. Se transcribe a mano al esquema de la plantilla (siete columnas, alias `E1` y `E2` para los dos analistas, `tarea = doble_etiquetado`) y se pasa por **el mismo validador**. Un segundo revisor compara la transcripción contra la fuente.
- Si la tabla cubre solo un subconjunto, el validador informará la regla (b) para los casos faltantes. Para validar el subconjunto se recorta una copia del corpus a esos ids (mismo formato JSON, `metadata.total_casos` igual al nuevo `len(casos)`) y se pasa con `--corpus`; el recorte y su criterio se documentan en el README y el kappa se reporta con su `n` real, menor que 200.
- Una tabla recuperada **no es independiente ni ciega**: sus etiquetadores son los analistas originales. Corresponde `estado_cegado: limitacion_declarada` (sección 9).
- La tabla recuperada se versiona con el mismo procedimiento de la sección 7 (hash y README).
