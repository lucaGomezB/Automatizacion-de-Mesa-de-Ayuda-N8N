# evaluation/data/campana/analisis/

Salidas del analisis de solo lectura de la campana (c-167). Las produce
`evaluation/analisis_campana.py` corriendo offline sobre las entradas de
`evaluation/data/campana/`. Esta carpeta no es una fuente de datos: es un reporte derivado y
regenerable.

## Procedencia

- Productor: `evaluation/analisis_campana.py` (CLI de solo lectura).
- Comando de referencia:

  ```bash
  python -m evaluation.analisis_campana \
    --entrada evaluation/data/campana \
    --salida evaluation/data/campana/analisis \
    --pines-in-sample '{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}' \
    --rango-google-genai-vigente ">=2.33,<3"
  ```

- El analisis NO usa red ni Gemini, NO regenera `evaluation/report.md`,
  `evaluation/predicciones.json` ni los numeros canonicos de v9, y NO escribe fuera de la
  carpeta de salida. La proteccion de los artefactos congelados es POR CONSTRUCCION: el CLI
  escribe exactamente tres nombres fijos (`resultados.json`, `resultados.md` y
  `SHA256SUMS.txt`), asi que nunca toca `evaluation/report.md`, `evaluation/predicciones.json`,
  `evaluation/predicciones_calibracion.json`, `data/corpus_resultados*.json` ni
  `evaluation/evidence/`.
- Referencia por defecto del brazo manual: `consenso_doble_etiquetado`. La referencia
  alternativa `consenso_original` se pide con `--referencia`.

## Entradas esperadas

Se leen de la carpeta `--entrada`, con estos nombres canonicos:

| Archivo | Contrato | Que aporta |
|---|---|---|
| `plantilla_etiquetado.csv` | C1 | Filas de `doble_etiquetado` (kappa y referencia) y de `brazo_manual` (exactitud y orden) |
| `registro_sujetos.csv` | C2 | Independencia de roles (`alias, rol, persona`) |
| `intervenciones.csv` | C5 | `tasa_intervencion_humana` y proporcion de tiempo |
| `plan_campana.csv` | C6 | Universo de casos de la corrida y efecto de orden |
| `corpus_campana.json` | C1/corpus | `tiempo_automatizado_s` y verdad del corpus de ajuste |
| `predicciones_in_sample.json` | v9/C9 | Bloque in-sample y contraste manual vs automatizado |
| `predicciones_independiente.json` | C9 | Bloque out-of-sample |
| `corpus_independiente.json` | C9 | Verdad del corpus independiente |

Cada seccion se ejecuta de forma independiente: si falta el archivo de una seccion, esa
seccion se declara "no se obtuvo" con el artefacto faltante y las demas se reportan igual.
Una columna faltante en un archivo presente aborta el CLI con un error que nombra el archivo
y la columna.

`plantilla_etiquetado.csv` y `predicciones_in_sample.json` no los produce ningun runbook de
manera directa: los ensambla `evaluation/preparar_entradas_analisis.py` (c-170), el unico
camino documentado. Ese helper une `doble_etiquetado.csv` + `brazo_manual.csv` en
`plantilla_etiquetado.csv` (un único encabezado C1, LF, sin BOM) y copia byte a byte el cache
congelado `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` a
`predicciones_in_sample.json`:

```bash
python -m evaluation.preparar_entradas_analisis \
  --entrada evaluation/data/campana \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json
```

## Semilla y remuestreos

- Semilla bootstrap: `SEMILLA_BOOTSTRAP` de `evaluation/metrics.py` (`20261021`).
- Remuestreos bootstrap: `REMUESTREOS_BOOTSTRAP` de `evaluation/metrics.py` (`2000`).
- Nivel de confianza: `NIVEL_CONFIANZA` de `evaluation/metrics.py` (`0.95`).
- Semilla y remuestreos se listan en `resultados.json` y en `resultados.md`. Con las mismas
  entradas, dos corridas producen `resultados.json`, `resultados.md` y `SHA256SUMS.txt`
  identicos byte a byte.

## Salidas

- `resultados.json`: documento deterministico con la referencia usada, la semilla, los
  remuestreos, el SHA-256 de cada entrada leida y las cinco secciones (`kappa`,
  `exactitud_brazo_manual`, `intervencion`, `orden`, `fuera_de_muestra`).
- `resultados.md`: resumen legible del mismo analisis.
- `SHA256SUMS.txt`: una linea `hash  nombre` por cada salida y por cada entrada leida. Sirve
  para verificar que una corrida uso exactamente las entradas esperadas y para comparar dos
  corridas. No incluye su propio hash. Su formato es el de `sha256sum`.

## Analisis ampliado fuera de muestra (c-205)

`analisis_fuera_de_muestra_c205.py` completa el bloque fuera de muestra de c-191 (n efectivo
`103`) con macro-F1, metricas por clase con soporte, *balanced accuracy*, kappa del
clasificador contra la referencia, matriz de confusion 5x5, precision/potencia del n
observado frente al objetivo D1 de c-191, sensibilidad al sesgo de exclusion de los `47`
discordantes (peor caso, mejor caso, cota y regla de decision) y el balance neto con la tasa
de error fuera de muestra (`condicional`).

- Entradas versionadas (solo lectura): `../corpus_independiente.json`,
  `../predicciones_independiente.json`, `../doble_etiquetado_independiente.csv`.
- Metodo: reutiliza `evaluation/metrics.py`, `evaluation/kappa.py` y `evaluation/stats.py`; no
  reimplementa el clasificador ni las metricas; sin red ni Gemini; determinista.
- Comando (desde la raiz del repositorio):

  ```bash
  python3 evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.py
  ```

- Salidas: `analisis_fuera_de_muestra_c205.json` (fuente unica de las cifras) y
  `analisis_fuera_de_muestra_c205.md`; el script imprime el SHA-256 de cada una. Dos corridas
  producen salidas identicas byte a byte.
- Prueba: `cd evaluation/data/campana/analisis && python -m pytest test_analisis_fuera_de_muestra_c205.py -q`.
- La cota del sesgo de exclusion es una definicion declarada (los excluidos aciertan a la
  tasa del limite inferior del IC de Wilson del n efectivo); los escenarios son sensibilidad,
  no medicion.

## Analisis del dictamen CONEAU v1.3.0 (c-207)

`analisis_dictamen_c207.py` calcula tres bloques de solo lectura que el dictamen pidio y que
ningun artefacto previo contenia:

- `ic_reduccion_tiempo`: IC 95 % de la reduccion relativa del tiempo de registro
  (`1 - media(automatizado) / media(manual)`, valor puntual `0,7116`) y de la diferencia de
  medias en segundos. Bootstrap percentil remuestreando los `200` pares (casos) con reemplazo.
- `acuerdo_e3_e4`: proporcion de acuerdo observada (`103` de `150`) y kappa de Cohen entre
  los etiquetadores independientes `E3` y `E4`, con IC asintotico y bootstrap. Se detiene sin
  escribir salidas si la cuenta no coincide con el n efectivo de c-205.
- `balance_neto_referencia_comun`: verifica contra que referencia mide cada tasa el balance
  neto del texto (`e_aut = 53/200` contra el etiquetado original; `e_man = 26/151` contra el
  consenso de `E1`/`E2`), y si la asimetria se confirma, recalcula `B` y `a*` con una
  referencia comun (consenso de `E1`/`E2`: `28/138` y `26/151`; segunda referencia: etiquetado
  original) para 5, 10 y 15 minutos, con IC bootstrap por caso. Declara los limites no
  igualables (unidad por caso frente a por derivacion; `dt` de otra campana).

- Entradas versionadas (solo lectura): `../../../../data/corpus_evaluacion_pseudonimizado.json`,
  `../plantilla_etiquetado.csv`, `../predicciones_in_sample.json`, `../corpus_campana.json`,
  `../doble_etiquetado_independiente.csv` y `analisis_fuera_de_muestra_c205.json`.
- Metodo: reutiliza `evaluation/metrics.py` (`SEMILLA_BOOTSTRAP = 20261021`,
  `REMUESTREOS_BOOTSTRAP = 2000`, `percentil_intervalo`), `evaluation/kappa.py` y
  `evaluation/campana.py`; sin red ni Gemini; determinista.
- Comando (desde la raiz del repositorio):

  ```bash
  python3 evaluation/data/campana/analisis/analisis_dictamen_c207.py
  ```

- Salidas: `analisis_dictamen_c207.json` (fuente unica de las cifras, con el SHA-256 de cada
  entrada) y `analisis_dictamen_c207.md`; el script imprime el SHA-256 de cada una. Dos
  corridas producen salidas identicas byte a byte.
- Prueba: `cd evaluation/data/campana/analisis && python -m pytest test_analisis_dictamen_c207.py -q`.
- `dt` (`43,82 s`) y `N` (`2.646`) se toman como constantes del memo canonico; la
  incertidumbre de `dt` no entra en el IC de `B`.

## Contraste pareado linea de base frente a hibrido (c-213)

`contraste_linea_de_base_c213.py` reconstruye las predicciones por caso de la linea de base
clasica (`evaluation.linea_de_base.predecir`, semilla `42`), lee las del hibrido de
`../predicciones_independiente.json` y calcula, sobre los mismos `103` casos con consenso, la
tabla 2x2 de aciertos estrictos, el contraste de McNemar (`evaluation/stats.py`) y la
diferencia de exactitudes pareadas con IC 95 % bootstrap percentil pareado (`10000`
remuestreos, `SEMILLA_BOOTSTRAP`). Aborta sin escribir salidas si no reproduce los aciertos
agregados (`67` y `60` de la linea de base en c-210; `87` del hibrido en c-205).

- Entradas versionadas (solo lectura): `../corpus_campana.json`, `../corpus_independiente.json`,
  `../predicciones_independiente.json`, `analisis_fuera_de_muestra_c205.json` y
  `linea_de_base_clasica_c210.json`.
- Comando (desde la raiz del repositorio):

  ```bash
  python3 evaluation/data/campana/analisis/contraste_linea_de_base_c213.py
  ```

  Parametros: `--referencia` (corpus de prueba), `--predicciones` (predicciones del hibrido;
  por defecto `../predicciones_independiente.json`), `--n-esperado`, `--nombre` (nombre base de
  las salidas; por defecto `contraste_linea_de_base_c213`) y `--anclas SISTEMA=N` (aciertos
  estrictos esperados por sistema; con `--anclas` se agrega el bloque `metricas_globales` al
  artefacto). Sin `--anclas` el script conserva el comportamiento por defecto (anclas de c-205
  y c-210) y la corrida por defecto queda byte a byte identica a la versionada.
- Salidas: `contraste_linea_de_base_c213.json` (fuente unica de las cifras, con las
  predicciones por caso y el SHA-256 de cada entrada), `.md` y `.SHA256SUMS.txt`. Dos
  corridas producen salidas identicas byte a byte.
- Prueba: `cd evaluation/data/campana/analisis && python -m pytest test_contraste_linea_de_base_c213.py -q`.
- Aditivo: no reemplaza ningun numero canonico; no es el brazo solo-LLM.

### Corrida sobre la referencia arbitrada (c-206, n = 206)

`contraste_linea_de_base_c213_arbitrado.py` no existe: es el MISMO script corrido con la
referencia arbitrada de c-206 y el nombre base de salida `contraste_linea_de_base_c213_arbitrado`,
de modo que NO clobbea los artefactos de `103`. Reutiliza la linea de base clasica
(`evaluation.linea_de_base.predecir`, semilla `42`) entrenada con los `200` casos de
`../corpus_campana.json`, lee el hibrido de `../predicciones_arbitrado.json` y contrasta sobre
la referencia `../corpus_independiente_arbitrado.json` (`206` casos, sin exclusion). Antes de
escribir, el ancla declarada `--anclas hibrido=142` obliga a que el hibrido reproduzca sus
`142/206` aciertos estrictos versionados (Seccion 3.25); si no, aborta sin escribir.

- Entradas versionadas (solo lectura): `../corpus_campana.json`,
  `../corpus_independiente_arbitrado.json`, `../predicciones_arbitrado.json`,
  `analisis_fuera_de_muestra_c205.json` y `linea_de_base_clasica_c210.json`.
- Comando (desde la raiz del repositorio):

  ```bash
  python3 evaluation/data/campana/analisis/contraste_linea_de_base_c213.py \
    --referencia evaluation/data/campana/corpus_independiente_arbitrado.json \
    --predicciones evaluation/data/campana/predicciones_arbitrado.json \
    --n-esperado 206 \
    --nombre contraste_linea_de_base_c213_arbitrado \
    --anclas hibrido=142
  ```

- Salidas: `contraste_linea_de_base_c213_arbitrado.json` (fuente unica de las cifras; incluye
  el contraste pareado por variante y el bloque `metricas_globales` de los tres sistemas),
  `.md` y `.SHA256SUMS.txt`. Dos corridas producen salidas identicas byte a byte.
  - `contraste_linea_de_base_c213_arbitrado.json`: `9fedd6cbda558c883e77d3879095adef759086ce3450abe55dafd6afa711d513`
  - `contraste_linea_de_base_c213_arbitrado.md`: `6257e6103a3f96d5d4b57abdd86ab74fb2c09412a2d40dcd6f722ca11e29b28d`
- Aditivo: NO reemplaza los numeros del contraste de `103` (Seccion 3.23 del memo) ni ningun
  otro numero canonico; es la misma comparacion repetida sobre el n arbitrado.

## Calibracion y punto de operacion del gate de confianza (c-214)

`analisis_calibracion_gate_c214.py` mide la calibracion (ECE, Brier, sobreconfianza) y la
discriminacion (AUROC, con IC95 bootstrap) de la confianza por etapa, dentro de la muestra (200
casos) y fuera de ella (103), el barrido de umbral de la etapa Gemini y dos senales alternativas
de derivacion (S1, acuerdo entre etapas; S2, `score_correctitud` de las reglas). La regla de
seleccion esta prerregistrada en el docstring del generador y se fijo antes de generar las
salidas; el prerregistro NO fue ciego (se declara alli). El umbral se elige solo con los 200
casos y se evalua sin reajuste en los 103. No modifica la configuracion productiva.

- Entradas versionadas (solo lectura): `../../../evidence/predicciones_hybrid-v3_2026-10-07.json`,
  `../predicciones_independiente.json`, `../plantilla_etiquetado.csv` y
  `../senales_reglas_c214.csv` (recomputo offline de las reglas; ver `../README.md`).
- Comando (desde la raiz del repositorio):

  ```bash
  python3 evaluation/data/campana/analisis/analisis_calibracion_gate_c214.py
  # regenerar ademas el CSV de senales con el backend (offline, sin red):
  python3 evaluation/data/campana/analisis/analisis_calibracion_gate_c214.py --recomputar-senales
  ```

- Salidas (UTF-8 sin BOM, LF; dos corridas producen salidas identicas byte a byte), con su
  SHA-256 (tambien en `analisis_calibracion_gate_c214.SHA256SUMS.txt`):
  - `analisis_calibracion_gate_c214.json`: `a5e4bca568890f57ec3346dd9c54e4425793c26704c362785f07a8ff0e4b4afd`
  - `analisis_calibracion_gate_c214.md`: `6cd5a9ec7bf3d90b3c771f02fe4c38f1bfff7e6e2db04ef6a67c79f10252517c`
  - `../senales_reglas_c214.csv`: `a7d4a703e2c5b70c3fc898a1c55c50fbad971255285b5e3630cf65f0c983c56a`
- Prueba: `cd evaluation/data/campana/analisis && python -m pytest test_analisis_calibracion_gate_c214.py -q`
  y `python -m pytest evaluation/tests/test_calibracion_gate.py -q`.

## Sensibilidad a referencias alternativas plausibles (c-216)

`analisis_ruido_referencia_c216.py` mide, de solo lectura y sin red, cuánto del error
observado del clasificador congelado `hybrid-v3` sobre la referencia arbitrada de `206`
casos es atribuible a la fragilidad de esa referencia. Antes de simular reproduce los
anclajes canónicos `142/206` (`0,6893`) y macro-F1 `0,7024`; si no los reproduce, aborta
sin escribir salidas. Es aditivo: no reemplaza ningún número canónico, no reclasifica, no
reentrena y no modifica el corpus, las predicciones ni los artefactos congelados.

- Método (fijado en el docstring antes de correr; el prerregistro NO fue ciego): kernel
  `5x5` fila-estocástico contra la referencia con las etiquetas de `E3`/`E4` sobre los `206`
  casos y `E5` sobre los `64` arbitrados, suavizado de Laplace `0,5`; mezcla convexa
  `Q_λ = (1−λ)·Q + λ·m` con la marginal empírica; calibración de `λ` por bisección al
  kappa `0,6055 ± 0,005`; `B = 2000` réplicas con semilla `20261021`; cotas
  distribution-free con `δ` de Wilson; rango de los `6` casos de tres vías.
- Entradas versionadas (solo lectura): `../corpus_independiente_arbitrado.json`,
  `../predicciones_arbitrado.json`, `../doble_etiquetado_arbitrado.csv` y
  `../arbitraje_tres_vias.json`.
- Comando (desde la raíz del repositorio):

  ```bash
  python3 evaluation/data/campana/analisis/analisis_ruido_referencia_c216.py
  ```

- Salidas (UTF-8 sin BOM, LF; dos corridas producen salidas idénticas byte a byte), con su
  SHA-256 (también en `analisis_ruido_referencia_c216.SHA256SUMS.txt`):
  - `analisis_ruido_referencia_c216.json`: `bda0a81769614b5a2a2a1ef03a95f8491b17a5bac3e71697cdd23e44d9f2cae2`
  - `analisis_ruido_referencia_c216.md`: `c9889df98ed772a1a7aa21c3aea7b5813d182593d0897d4dc968649fd80e340f`
- Prueba: `cd evaluation/data/campana/analisis && python -m pytest test_analisis_ruido_referencia_c216.py -q`.
- Resultado registrado (sección 3.27 del memo): `λ* = 0,231391`; mediana de exactitud
  `0,5097` con `q2,5 = 0,4515` y `q97,5 = 0,5631`; mediana de macro-F1 `0,5109`; `δ =
  0,369817`, `m = 76` y cotas `[0,3204; 1,0000]`; rango de tres vías `142/206` a
  `147/206`. La descomposición da error robusto `90` y error atribuible a la referencia
  `−26`: el error observado (`64`) es MENOR que el extremo favorable simulado, de modo que
  el análisis no atribuye el error observado al ruido de la referencia. La simulación se
  rotula como sensibilidad, no como medición de la verdad latente.

## Sesgo de corpus y fragilidad de la referencia (c-219)

`analisis_sesgo_corpus_referencia_c219.py` mide, de solo lectura, sin red y sin Gemini, (a) cuánto
cambian la cobertura, el cortocircuito y la precisión de la etapa determinística cuando el
vocabulario del filtro se deriva de una fuente externa al corpus, y (b) cómo varía la exactitud
estricta del híbrido congelado `hybrid-v3` entre el subconjunto de consenso `E3 = E4`, el arbitrado
por `E5` y el total. Antes de medir reproduce los anclajes (`115` cortocircuitados, `88/115`, cobertura
`131`, `142/206`, macro-F1 `0,7024`, `109/142`, `33/64`) y que el adaptador de scoring sobre `V1`
coincide caso a caso con el clasificador real; si algo no se reproduce, aborta sin escribir salidas.
Es aditivo: no reemplaza ningún número canónico y no modifica el corpus, las predicciones, el
vocabulario vigente `V1` ni los artefactos congelados.

- Método (fijado en el docstring antes de correr; el prerregistro NO es ciego en sentido estricto): el
  vocabulario corpus-blind se derivó de las definiciones canónicas de los cinco sectores
  (`CLAUDE.md`) y del «Glosario de términos de ciberseguridad: una guía de aproximación para el
  empresario» (INCIBE, 2017, v1; consultado el 2026-11-13), sin leer descripciones del corpus ni el
  vocabulario vigente; su independencia es procedimental. Se fijó y hasheó antes de medir en
  `vocabulario_corpus_blind_c219.json` (`90` patrones; SHA-256 del contenido
  `ec350b9615410defe531183e317c197a21f778638eb5ccccdbe9a77b2a34d581`; el script aborta si
  no coincide). Límite: el glosario público es de ciberseguridad, no de mesa de ayuda; el
  vocabulario de Hardware y Software es pobre.
- Entradas versionadas (solo lectura): `../corpus_independiente_arbitrado.json`,
  `../predicciones_arbitrado.json`, `../doble_etiquetado_arbitrado.csv`,
  `../arbitraje_tres_vias.json`, el vocabulario corpus-blind y el control `V0`
  (`../../sensibilidad_ajustes/keywords_pre_c71.json`, c-142).
- Comando (desde la raíz del repositorio, con las variables de entorno inertes del job de CI; el
  script se ejecuta en una carpeta sin `.env` para no cargar el `.env` local):

  ```bash
  python3 evaluation/data/campana/analisis/analisis_sesgo_corpus_referencia_c219.py
  ```

- Salidas (UTF-8 sin BOM, LF; dos corridas idénticas byte a byte), con su SHA-256 (también en
  `analisis_sesgo_corpus_referencia_c219.SHA256SUMS.txt`):
  - `analisis_sesgo_corpus_referencia_c219.json`: `768065f157ae4fdbfd047ea852bfb556a661343084f89fb0a14bd63a24d021fe`
  - `analisis_sesgo_corpus_referencia_c219.md`: `2f1fba560228ba824448e213a3b59cda4b2216632c29b82979b36a8b70a26416`
  - `vocabulario_corpus_blind_c219.json`: `2f4473a41be962eda23672120da98c7225a6e6cbd1b818f724a1b3496642beab`
- Prueba: `cd evaluation/data/campana/analisis && python -m pytest test_analisis_sesgo_corpus_referencia_c219.py -q`.
- Resultado registrado (sección 3.30 del memo): etapa determinística sobre los `206` casos, `V1` cobertura
  `131`, cortocircuito `115`, `88/115` (`0,7652`); corpus-blind cobertura `83`, cortocircuito `75`,
  `54/75` (`0,7200`, `[0,6096; 0,8090]`); `V0` cobertura `97`, cortocircuito `88`, `65/88` (`0,7386`).
  Exactitud estricta del híbrido: consenso `109/142` (`0,7676`), arbitrado `33/64` (`0,5156`),
  total `142/206` (`0,6893`); el subconjunto `E3 = E4 = E5` es vacío por construcción. Ambos
  resultados se rotulan como sensibilidad, sin causalidad de la referencia.

## Brazo «Gemini solo» y contraste de la hipotesis de eficiencia (c-215; integrado por c-217)

El brazo «Gemini solo» manda TODOS los casos (200 dentro de la muestra y 103 fuera de muestra) a la
misma etapa Gemini congelada del backend, sin reglas, y se compara de forma pareada con las predicciones
congeladas de `hybrid-v3`. La corrida paga YA se hizo (2026-11-13, `gemini-3.6-flash`, temperatura 0,3,
`google-genai` 2.34.0) y su caché se versiona. La regla de decisión (margen de no inferioridad 0,05,
ahorro material si el límite superior del IC de las razones de costo y de llamadas es menor que 0,90,
tope de 400 llamadas, una sola corrida) está prerregistrada en
`openspec/changes/c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia/design.md`.

- Ejecutor: `evaluation/brazo_gemini_solo.py` (caché reanudable en
  `evaluation/data/campana/brazo_gemini_solo/cache_brazo_gemini_solo.jsonl`, SHA-256
  `3bf290168bda5e8ddb0536e8a1470054213692ef598227289198dec340cdcd31`; blob de git
  `d0ea438581bf12dadc495e36f882352fa5778153`).
- Análisis (solo lectura; sale con código distinto de cero y sin escribir si falta el caché o está
  incompleto): `evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py`.

### Comandos exactos

1. Análisis (solo lectura):

   ```bash
   python3 evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py
   ```

2. Ejecutor (PAGA; exige `--confirmar-costo`; reanudable; NO se volvió a correr en c-217):

   ```bash
   python -m evaluation.brazo_gemini_solo --confirmar-costo
   ```

   Dry-run (sin red, sin clave, sin escribir el caché):

   ```bash
   python -m evaluation.brazo_gemini_solo --dry-run
   ```

### Salidas versionadas

`analisis_brazo_gemini_solo_c215.{json,md}` y `analisis_brazo_gemini_solo_c215.SHA256SUMS.txt` (UTF-8
sin BOM, LF; dos corridas idénticas byte a byte):

- `analisis_brazo_gemini_solo_c215.json`: `bc936061a06b094e3b30aeeb4ff461d1ab7956642db44cbe704367f54abdc88b`
- `analisis_brazo_gemini_solo_c215.md`: `77cdaaf76e1af00b733cda15a2ff90c05de9134b51e65e97d618b10ec7fc61a5`

Nota: el artefacto de la rama de c-215 registraba el SHA-256 CRLF `3fb5bacd…` de
`predicciones_hybrid-v3_2026-10-07.json`; regenerado en `main` registra el hash canónico LF
`89cf956e…` (el mismo de la Sección 3.24 del memo). Las cifras no cambian; es el fin de línea del
archivo de entrada. La salida `.md` es byte-idéntica a la de la rama.

### Reintento de fallos técnicos (desviación declarada del 2026-11-13)

En la corrida paga, 112 casos de `dentro_muestra` quedaron como fallos técnicos (sin respuesta del
modelo: `GeminiUnavailableError`, 0 tokens). La desviación y su amenaza a la validez están en la sección
«Desviaciones del prerregistro» de `design.md` de c-215 y en la sección 3.28 del memo. Solo se
reintentan los registros en `fallback` con error de indisponibilidad o transporte y sin tokens; las
respuestas inválidas del modelo no se reintentan. El caché es append-only.

### Lectura registrada (sección 3.28 del memo)

- Veredicto prerregistrado sobre el bloque primario (103 fuera de muestra con consenso de `E3`/`E4`):
  **no concluyente**.
- Componente de eficiencia: **cumplido y concluyente** (razón de llamadas `0,3301` `[0,2427; 0,4175]`;
  razón de costo `0,3295` `[0,2421; 0,4176]`; ambos límites superiores menores que `0,90`).
- Componente de exactitud: **indeterminado** (H `87/103`; L `90/103`; McNemar `p = 0,5078`; diferencia
  `−0,0291` `[−0,0874; 0,0291]`).
- Control de deriva: `98/103` `[0,8914; 0,9791]`, bandera `false`. Deriva de H verificada sobre los 103
  compartidos con `predicciones_arbitrado.json`: `0` discrepancias de sector/etapa.

### Pruebas

`python -m pytest evaluation/tests/test_brazo_gemini_solo.py -q` y
`python -m pytest evaluation/data/campana/analisis/test_analisis_brazo_gemini_solo_c215.py -q`
(cliente simulado, sin red). Requieren que el `.env` raíz de docker compose NO se cargue como
`sources` de `Settings` (en local, correr con ese `.env` fuera del directorio de trabajo, como en CI).

- Limitaciones declaradas: los intentos fallidos sin respuesta no aportan tokens (el costo de un caso
  con fallas queda subestimado); la latencia es del lado del cliente y desde la máquina de quien corre;
  el control de deriva no separa deriva del modelo del azar de muestreo a temperatura 0,3.
