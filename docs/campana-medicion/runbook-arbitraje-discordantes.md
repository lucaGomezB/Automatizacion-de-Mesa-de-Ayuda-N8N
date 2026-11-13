# Runbook: arbitraje de los discordantes y refuerzo de las clases chicas (c-206)

Procedimiento para resolver los **47 casos discordantes** entre `E3` y `E4` del corpus independiente con un **tercer etiquetador `E5`** (código `P11`), reforzar las clases de soporte chico (`Sistemas` y `Bases de Datos`) y clasificar el corpus resultante con el clasificador **congelado**, de modo que el resultado fuera de muestra se reporte sobre `150` casos y no sobre `103`.

## Para qué sirve

La validación fuera de muestra de c-191 quedó sobre un n efectivo de `103`: los `47` discordantes se **excluyeron** de la referencia (`docs/campana-medicion/runbook-corpus-independiente.md`, sección 4), lo que sesga la estimación hacia los casos fáciles, y dos clases quedaron con soporte chico (`Sistemas`, `5`; `Bases de Datos`, `13`, sobremuestreada). Este runbook entrega el protocolo y los instrumentos para levantar ese sesgo y hacer estimables esas clases. Lo que NO hace:

- No ejecuta el campo: el arbitraje por `E5`, la reunión y el etiquetado de los casos de refuerzo y la corrida paga los realizan los autores **fuera del repositorio**.
- No resuelve la discordancia por **consenso a posteriori** de `E3` y `E4`: el protocolo de la campaña lo prohíbe (`runbook-doble-etiquetado.md`, sección 8) porque sesgaría el kappa y la referencia. La referencia de un discordante la fija un **tercero independiente**.
- No cambia el clasificador, el corpus de ajuste, el umbral ni el prompt, y no incorpora el resultado a la tesis (eso lo hará un change posterior, cuando el campo concluya).

Todo se ejecuta desde la raíz del repositorio. La clasificación (sección 10) invoca a Gemini y tiene costo: está protegida por `--confirm-paid`.

## 0. Antes de empezar

1. Estar en la rama del change `c-206-arbitraje-de-los-discordantes-y-refuerzo-de-clases-chicas`, con Python y las dependencias de `evaluation/` y del backend.
2. Confirmar que hay exactamente `47` discordantes en la tabla primaria versionada de c-191 (`evaluation/data/campana/doble_etiquetado_independiente.csv`, `150` casos, `E3` y `E4`). Sin PII: solo cuenta ids.

   ```bash
   python - <<'EOF'
   import csv
   from collections import defaultdict
   sector = defaultdict(dict)
   with open("evaluation/data/campana/doble_etiquetado_independiente.csv", encoding="utf-8", newline="") as f:
       for fila in csv.DictReader(f):
           sector[fila["id_caso"]][fila["id_etiquetador"]] = fila["sector_etiquetado"]
   discordantes = sorted(i for i, s in sector.items() if s["E3"] != s["E4"])
   print(len(sector), "casos;", len(discordantes), "discordantes")
   EOF
   ```

   Salida esperada: `150 casos; 47 discordantes`. Si el número es otro, **detenerse**: el protocolo parte de esos `47`.
3. Correr las pruebas del validador y del ensamblador nuevos: `cd evaluation && python -m pytest tests/test_arbitraje.py tests/test_doble_etiquetado.py tests/test_ensamblado_arbitrado.py tests/test_reporte_arbitrado.py -q` (desde `evaluation/`, con las variables de entorno dummy del job de CI).

## 1. Decisiones pendientes de los autores

Estas decisiones son **de los autores** y todavía NO están tomadas. Hasta que se registren acá, no se entrega nada a `E5` ni se reúnen casos de refuerzo. El runbook no las inventa: completar cada campo **sin nombres, correos ni legajos** (solo códigos y cifras).

### 1.1 Tercer etiquetador `E5` / `P11` y custodio de identidades (tarea 0.2)

| Campo | Valor |
|---|---|
| Alias del tercer etiquetador | `E5` (fijado por el change) |
| Código de persona | `P11` (fijado por el change) |
| Persona identificada y que acepta etiquetar | **PENDIENTE** (la identidad NO se escribe acá: se custodia fuera del repositorio) |
| Custodio de la correspondencia alias-identidad | **PENDIENTE** (rol, no nombre) |
| Independencia de `E1`-`E4`, `A1`, `T1`-`T3` y `O1`/`O2` confirmada | **PENDIENTE** (sí / no, y fecha `AAAA-MM-DD` de la confirmación) |
| `estado_cegado` resultante | **PENDIENTE** (`cumplido` o `limitacion_declarada`, ver sección 12) |

### 1.2 Cuota de refuerzo de clases chicas (tarea 0.3)

| Clase | Casos nuevos a reunir |
|---|---|
| `Sistemas` | **PENDIENTE** (cifra a decidir por los autores) |
| `Bases de Datos` | **PENDIENTE** (cifra a decidir por los autores) |

La cuota debe quedar registrada ANTES de reunir casos. El objetivo del refuerzo es que las métricas por clase sean **estimables** (`MIN_SOPORTE_ESTIMABLE = 2` en `evaluation/metrics.py`); el change no fija un n por clase.

### 1.3 Regla del caso de tres etiquetas distintas (a confirmar)

La propuesta del design es la de la sección 6 (`E5` como árbitro con bandera de discordancia residual). Los autores la **confirman o la ajustan** (por ejemplo, un cuarto juicio) antes de ver cualquier etiqueta de `E5`: **PENDIENTE** (confirmada sí / no, con fecha `AAAA-MM-DD`).

## 2. Sujetos

1. `E5` se registra en `evaluation/data/campana/registro_sujetos.csv` con la fila `E5,etiquetador,P11` (columnas `alias,rol,persona`), sin nombres, correos ni legajos. Es la tarea 3.1 del change, que se hace en el campo una vez resuelta la sección 1.1.
2. `E5` debe ser una persona distinta de `E1`-`E4`, de `A1`, de `T1`-`T3` y de `O1`/`O2`; su `persona` NO puede figurar con otro rol. Se verifica con `validar_registro_sujetos` (sin solape por `persona`).
3. La correspondencia alias-identidad la custodia la persona de la sección 1.1 **fuera del repositorio**.

## 3. Cegado e instrumentos

`E5` etiqueta **a ciegas**. Recibe SOLO:

- la **hoja ciega** de los `64` casos (`id_caso` y descripción pseudonimizada): los `47` discordantes del corpus original de `150` más los `17` discordantes del refuerzo de clases (ver sección 14);
- **una copia vacía** de `evaluation/data/plantilla_etiquetado.csv` (solo encabezado);
- el **codebook congelado** (`evaluation/data/campana/codebook_doble_etiquetado.md`; contenido en `runbook-doble-etiquetado.md`, sección 3).

`E5` NO puede ver: la etiqueta de `E3`, la de `E4`, la referencia (`sector_asignado`/`sectores_adicionales`) ni ninguna predicción del clasificador. Trabaja solo y entrega su archivo al custodio.

### 3.1 Generar la hoja ciega

Las descripciones pseudonimizadas de los `47` discordantes del corpus original (más los del refuerzo, con la tabla `E3`/`E4` combinada; ver sección 14) están en el **JSON de trabajo** del corpus independiente (`runbook-corpus-independiente.md`, sección 3), que vive FUERA del repositorio (el JSON versionado `corpus_independiente.json` solo trae los `103` del consenso). La hoja se arma con el comando del validador nuevo, que toma los discordantes de la tabla primaria y las descripciones del JSON de trabajo:

```bash
python -m evaluation.arbitraje hoja-ciega \
  --primaria evaluation/data/campana/doble_etiquetado_independiente.csv \
  --corpus corpus_independiente_trabajo.json \
  --salida hoja_ciega_arbitraje.csv
```

- La hoja sale ordenada **por `id_caso`** (orden determinista, el mismo en toda corrida); si el orden de presentación debe aleatorizarse para `E5`, los autores lo deciden y lo declaran acá antes de entregar: **PENDIENTE** (`orden por id_caso` / `aleatorio con semilla declarada`).
- Verificar `head -1 hoja_ciega_arbitraje.csv` (debe ser exactamente `id_caso,descripcion`) y `wc -l hoja_ciega_arbitraje.csv` (**65** líneas: encabezado más `64` casos, tras el refuerzo; ver sección 14).
- Revisar a mano una muestra de las descripciones: son texto pseudonimizado (Ley 25.326) con el mismo protocolo que el corpus de ajuste, y la hoja NO contiene etiquetas, referencia ni predicciones (solo dos columnas).
- La hoja contiene descripciones del organismo: **no se versiona** ni se deja dentro del repositorio; se genera fuera de él o se borra al terminar.

### 3.2 Copia vacía de la plantilla

```bash
cp evaluation/data/plantilla_etiquetado.csv planilla_E5.csv
wc -l planilla_E5.csv
```

Debe tener `1` línea (solo el encabezado de las siete columnas `C1`). Tampoco se versiona.

## 4. Codebook

El mismo codebook congelado del doble etiquetado de `E3`/`E4`; no se modifica para el arbitraje ni se le agregan ejemplos de los discordantes.

## 5. Completar la plantilla (E5)

`E5` completa **una fila por caso de la hoja** con las siete columnas, igual que en `runbook-doble-etiquetado.md`, sección 5, con estas diferencias:

| Columna | Qué poner |
|---|---|
| `id_caso` | El `id` de la hoja ciega (prefijo `I`) |
| `id_etiquetador` | `E5` |
| `tarea` | `doble_etiquetado` |
| `sector_etiquetado` | Exactamente una de las cinco cadenas canónicas |
| `sectores_adicionales_etiquetados` | Lista separada por `\|`, sin repetir el principal |
| `inicio`, `timestamp` | ISO-8601 con zona horaria (`inicio` opcional) |

`E5` arbitra SOLO los discordantes: no etiqueta casos donde `E3` y `E4` coincidieron (el validador lo rechaza, regla (b)).

## 6. Regla de arbitraje (se fija ANTES de ver a `E5`)

La regla es determinista y la implementa `evaluation/arbitraje.py::construir_referencia`:

1. **`E3` y `E4` coinciden** en `sector_etiquetado`: la referencia es ese sector (consenso original, sin cambios). Los adicionales son la intersección de los de `E3` y `E4` (como en c-191).
2. **`E3` y `E4` difieren** (discordancia de dos vías, o `E5` coincide con uno de ellos): la referencia es la etiqueta de `E5`. Es un tercero independiente, **no un consenso**: no se promedian ni se negocian las etiquetas de `E3` y `E4`.
3. **Las tres etiquetas son distintas** (`E3`, `E4` y `E5`): la referencia es la de `E5` y el caso se marca con la **bandera de discordancia residual** (`tres_vias`). Se informa el conteo de casos marcados. (Propuesta del design, a confirmar en la sección 1.3.)
4. **Conjunto de verdad laxo de un caso arbitrado**: el sector de `E5` más los adicionales marcados por **al menos dos de los tres** etiquetadores, sin repetir el sector de la referencia.

La regla queda fija al registrar la confirmación de la sección 1.3; cambiarla después de ver las etiquetas de `E5` invalida el arbitraje.

## 7. Refuerzo de las clases chicas

1. Reunir casos **nuevos** del organismo para `Sistemas` y `Bases de Datos` según la cuota de la sección 1.2, que no estén entre los `200` del corpus de ajuste ni entre los `150` actuales.
2. Ids nuevos con prefijo **`I`**, distintos de `I001`..`I150` (la numeración de los nuevos queda a cargo de los autores y se registra acá: **PENDIENTE**).
3. Pseudonimizar con el mismo protocolo (`runbook-corpus-independiente.md`, sección 2).
4. Etiquetar con el **mismo procedimiento**: doble etiquetado `E3`/`E4` y, si difieren, arbitraje de `E5` con la regla de la sección 6. El `sector_asignado` de referencia de cada caso sale de ese procedimiento, nunca de la predicción del clasificador.
5. Los casos de refuerzo pasan `verificar_no_solape` como los demás (sección 9).

## 8. Unir y validar

Con las planillas de `E3`/`E4` (casos originales y de refuerzo) y la de `E5` unidas en una sola tabla `doble_etiquetado_arbitrado.csv` (un único encabezado, LF, UTF-8 sin BOM) y el JSON de trabajo con todos los casos:

```bash
python -m evaluation.arbitraje validar \
  --planilla doble_etiquetado_arbitrado.csv \
  --corpus corpus_independiente_trabajo.json
```

Debe salir con exit code `0`. Las reglas (c)-(j) son las del validador de `doble_etiquetado.py` (`runbook-doble-etiquetado.md`, sección 6) y la regla (a) exige exactamente `E3`, `E4` y `E5`; la (b) exige que `E3` y `E4` cubran el corpus y que `E5` cubra exactamente los discordantes. El contrato de dos etiquetadores de `python -m evaluation.doble_etiquetado` NO cambia: la planilla de tres etiquetadores se valida solo con este comando.

## 9. Corpus final arbitrado, no solape y control de congelamiento

1. **JSON final** `evaluation/data/campana/corpus_independiente_arbitrado.json`: mismo esquema que `corpus_independiente.json`, con la referencia que arma `construir_referencia` (consenso `E3`/`E4`; `E5` en los discordantes; adicionales según la sección 6) y los casos de refuerzo. Se ensambla con el subcomando `ensamblar` de `evaluation/arbitraje.py`, que valida la planilla unida (sección 8) y escribe el corpus junto con su sidecar en una sola corrida:

   ```bash
   python -m evaluation.arbitraje ensamblar \
     --primaria  ~/Desktop/campana-hojas/campana_extra/doble_etiquetado_independiente.csv \
     --arbitraje ~/Desktop/campana-hojas/campana_extra/E5/etiquetas_E5.csv \
     --corpus    ~/Desktop/campana-hojas/campana_extra/corpus_independiente_trabajo.json \
     --salida    evaluation/data/campana/corpus_independiente_arbitrado.json \
     --sidecar   evaluation/data/campana/arbitraje_tres_vias.json
   ```

   Las tres entradas son rutas fuera del repositorio (la planilla `E5` todavía no existe: el comando falla con exit `2` hasta que el archivo llegue). El comando imprime el número de casos, el SHA-256 del corpus y del sidecar, y el conteo de casos de tres vías. Es determinista: dos corridas producen bytes idénticos. La planilla `E3`/`E4` versionada (`evaluation/data/campana/doble_etiquetado_independiente.csv`) es idéntica a la de `~/Desktop`; cualquiera de las dos sirve.

   **Bandera `tres_vias` (decisión D9 del design):** el `origen` de cada referencia y la bandera `tres_vias` NO entran al esquema del corpus; viven en el sidecar `evaluation/data/campana/arbitraje_tres_vias.json` (`schema_version`, `metadata` con `corpus_sha256`, y una fila `{"id", "origen", "tres_vias"}` por caso). Se eligió el sidecar sobre un campo nuevo en `cargar_corpus` porque ese esquema lo consumen `run_evaluation.py`, `no_solape.py`, `evaluar_fuera_de_muestra` y `metrics.py`: cambiarlo el día de la entrega es riesgoso y `_parsear_caso` descartaría un campo extra en silencio. Verificación: `cargar_corpus` carga los `150` casos (más el refuerzo) con prefijo `['I']`; el sidecar tiene una fila por caso y su `corpus_sha256` coincide con el del corpus.

2. **No solape** (paso previo obligatorio, repetido por el runner):

   ```bash
   python - <<'EOF'
   from evaluation.corpus import cargar_corpus
   from evaluation.no_solape import verificar_no_solape
   ajuste = cargar_corpus("data/corpus_evaluacion_pseudonimizado.json")
   candidato = cargar_corpus("evaluation/data/campana/corpus_independiente_arbitrado.json")
   for a in verificar_no_solape(ajuste, candidato, umbral_jaccard=0.8):
       print("ADVERTENCIA", a.id_candidato, "~", a.id_ajuste, round(a.similitud, 3))
   print("sin solape de ids ni de descripciones")
   EOF
   ```

   Sin `SolapeError`; cada advertencia se revisa a mano y se registra.
3. **Control de clasificador congelado** (`hybrid-v3`, sin recalibrar):

   ```bash
   git diff bf5e099 HEAD -- App/Backend/app/classifiers docs/prompt_gemini.txt App/Backend/app/constants.py App/Backend/app/config/settings.py
   ```

   Solo se admiten diferencias ajenas a la clasificación (comentarios, importaciones, campos no clasificatorios). Si cambió algo que afecte la clasificación, **no se clasifica**. **Prohibido recalibrar** tau, el prompt, el mapa de palabras clave o el vocabulario tras ver el corpus arbitrado.

## 10. Clasificar con rutas propias (`--confirm-paid`)

Requiere `GEMINI_API_KEY` y las variables del backend; esta corrida **tiene costo**. Solo se corre con las secciones 8 y 9 en verde:

```bash
PYTHONPATH=App/Backend python -m evaluation.run_evaluation \
  --corpus evaluation/data/campana/corpus_independiente_arbitrado.json \
  --predicciones evaluation/data/campana/predicciones_arbitrado.json \
  --reporte evaluation/data/campana/reporte_arbitrado.md \
  --confirm-paid
```

El runner se comporta como en `runbook-corpus-independiente.md`, sección 7 (rutas propias obligatorias, no solape, procedencia y gate de costo). El `cache_meta` debe traer `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines`.

## 11. Versionar, registrar y analizar

1. Dejar en `evaluation/data/campana/`: la tabla primaria `doble_etiquetado_arbitrado.csv`, `corpus_independiente_arbitrado.json`, el sidecar `arbitraje_tres_vias.json`, `predicciones_arbitrado.json`, `reporte_arbitrado.md` y `registro_sujetos.csv` actualizado (con `E5,etiquetador,P11`).
2. Calcular el SHA-256 de cada archivo (`sha256sum`) y completarlo en `evaluation/data/campana/README.md`, junto con el `commit` del cache, el resultado del control de la sección 9 y el `estado_cegado`.
3. Verificar que los artefactos de la v9 no cambiaron: `git status` no muestra `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json` ni `evaluation/report.md`.
4. Correr `evaluar_fuera_de_muestra` con el cache arbitrado (tarea 6.2). El comando reutiliza el módulo del repositorio (sin red ni Gemini: lee las predicciones persistidas de la sección 10) y reporta el n efectivo **sin exclusión** y las métricas por clase:

   ```bash
   python -m evaluation.reporte_arbitrado \
     --predicciones-arbitrado evaluation/data/campana/predicciones_arbitrado.json \
     --corpus-arbitrado       evaluation/data/campana/corpus_independiente_arbitrado.json
   ```

   Los otros dos artefactos (in-sample y corpus de ajuste) toman sus rutas por defecto. Debe imprimir `n efectivo (sin exclusion): 150` (o el total tras el refuerzo) y, por clase, `Sistemas` y `Bases de Datos` marcadas `estimable`. Si falta el cache arbitrado, sale con exit `2` nombrando el artefacto faltante sin caer a datos in-sample. El resultado de c-191 sobre `103` se conserva rotulado como **estimación con exclusión**.

## 12. Limitación declarada: no se consigue un `E5` independiente

Si no se consigue un tercer etiquetador independiente, se registra `estado_cegado: limitacion_declarada` (con `motivo_limitacion`) en `evaluation/data/campana/README.md` y el resultado **no se presenta como etiquetado ciego**. El arbitraje igual puede hacerse, pero su independencia queda declarada como limitación.

## 13. Criterio de aceptación

El arbitraje queda aceptado solo si se cumple todo lo siguiente:

1. `E5`/`P11` figura en `registro_sujetos.csv` sin nombres y sin solapes por `persona`.
2. `python -m evaluation.arbitraje validar` sale con exit code `0` y la regla de tres vías está declarada y confirmada (sección 1.3).
3. `verificar_no_solape` pasa entre el corpus arbitrado y el de ajuste; las advertencias se revisaron.
4. La referencia arbitrada cubre los `150` casos (más el refuerzo) y `Sistemas` y `Bases de Datos` son estimables.
5. El control de clasificador congelado está registrado y no hubo recalibración posterior.
6. Los artefactos nuevos están versionados con su SHA-256 y los de la v9 no cambiaron.
7. `openspec validate c-206-arbitraje-de-los-discordantes-y-refuerzo-de-clases-chicas --strict` pasa.

## 14. Registro de ejecución (2026-11-13)

El refuerzo de clases chicas y la preparación del arbitraje ya se ejecutaron parcialmente. Este registro documenta lo hecho, sin reescribir el protocolo de arriba.

- **Refuerzo de clases chicas**: se reunieron `56` casos nuevos (`I151`..`I206`) y los etiquetaron `E3` y `E4` (tarea `doble_etiquetado`), fuera del repositorio. Coinciden en `39` casos y discrepan en `17`. El consenso es mayoritariamente `Sistemas` (`33` de `39`), con `4` de `Soporte Tecnico Software` y `2` de `Seguridad Informatica`; los casos de infraestructura, servidores y red se cargaron a `Sistemas`. Con esto `Sistemas` deja de ser clase chica en el corpus arbitrado (pasa de `5` a unos `38` casos de consenso), que era el objetivo del refuerzo.
- **Hoja ciega de `E5`**: pasó de `47` a `64` casos (los `47` del corpus original más los `17` del refuerzo). Se armó con el comando de la sección 3.1 sobre la **tabla `E3`/`E4` combinada** (`150` originales + `56` del refuerzo) y el JSON de trabajo de `206` casos. El paquete de `E5` (hoja ciega, plantilla y codebook) está en `~/Desktop/campana-hojas/campana_extra/E5/`; la hoja y la plantilla tienen `64` filas con los mismos `id_caso` (las versiones de `47` quedaron como `*.47.bak.csv`).
- **Cegado**: la hoja contiene solo `id_caso` y descripción; no lleva etiquetas de `E3`/`E4`, referencia ni predicciones. El orden es por `id_caso`.
- **Pendiente**: `E5` arbitra los `64` casos; después, `ensamblar` (sección 9) con la tabla combinada y la planilla de `E5`.
