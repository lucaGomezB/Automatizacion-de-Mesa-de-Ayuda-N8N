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

  Parametros: `--referencia` (corpus de prueba) y `--n-esperado`, para repetir el contraste
  con la referencia arbitrada sin cambiar el codigo.
- Salidas: `contraste_linea_de_base_c213.json` (fuente unica de las cifras, con las
  predicciones por caso y el SHA-256 de cada entrada), `.md` y `.SHA256SUMS.txt`. Dos
  corridas producen salidas identicas byte a byte.
- Prueba: `cd evaluation/data/campana/analisis && python -m pytest test_contraste_linea_de_base_c213.py -q`.
- Aditivo: no reemplaza ningun numero canonico; no es el brazo solo-LLM.

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

## Brazo «Gemini solo» y contraste de la hipotesis de eficiencia (c-215)

El brazo «Gemini solo» manda TODOS los casos (200 dentro de la muestra y 103 fuera de muestra)
a la misma etapa Gemini congelada del backend, sin reglas, y se compara de forma pareada con las
predicciones congeladas de `hybrid-v3`. El codigo y el analisis estan listos y probados con
clientes simulados; la corrida paga NO se hizo. La regla de decision (margen de no inferioridad
0,05, ahorro material si el limite superior del IC de las razones de costo y de llamadas es
menor que 0,90, tope de 400 llamadas, una sola corrida) esta prerregistrada en
`openspec/changes/c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia/design.md`.

- Ejecutor: `evaluation/brazo_gemini_solo.py` (cache reanudable en
  `evaluation/data/campana/brazo_gemini_solo/cache_brazo_gemini_solo.jsonl`, que NO existe hasta la
  corrida paga). Analisis: `evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py`.

### Requisitos de la corrida real (los cumple una persona, no un agente)

- `google-genai` dentro de `>=2.33,<3` (pin de `openspec/config.yaml`). El ejecutor verifica la
  version instalada y aborta con codigo 2 si no cumple; no instala paquetes.
- Variable de entorno `GEMINI_API_KEY` con la clave real, exportada en la sesion que corre el
  comando. Se lee solo del entorno, no se imprime ni se guarda. Si `Settings` del backend
  requiere otras variables (`DATABASE_URL`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY`,
  `COST_GUARD_CALLER_HMAC_KEY`, `DIRECTORY_BLIND_INDEX_KEY`), el ejecutor completa con valores
  inertes las que falten y nunca pisa las existentes.
- Visto bueno de gasto: unas 303 llamadas, del orden de USD 0,22 a precio introductorio y USD 0,43
  a precio estandar; tope duro de 400 llamadas (USD 0,29 / 0,57 como maximo).
- Ejecutar desde la raiz del repositorio y con el prerregistro ya commiteado.

### Comandos exactos

1. Dry-run (sin red, sin clave, sin escribir el cache; cuenta casos pendientes, llamadas y costo):

   ```bash
   python -m evaluation.brazo_gemini_solo --dry-run
   ```

2. Corrida real (PAGA; exige confirmacion explicita; reanudable: si se corta, se relanza el mismo
   comando y no se vuelve a pagar lo ya registrado). Codigos de salida: 0 completa, 2 una guarda
   impidio la corrida, 3 tope alcanzado con casos pendientes:

   ```bash
   python -m evaluation.brazo_gemini_solo --confirmar-costo
   ```

3. Analisis (solo lectura; sale con codigo distinto de cero y sin escribir si falta el cache o esta
   incompleto; escribe `analisis_brazo_gemini_solo_c215.{json,md}` y `.SHA256SUMS.txt` en esta
   carpeta):

   ```bash
   python evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py
   ```

### Reintento de fallos tecnicos (desviacion declarada del 2026-11-13)

En la corrida paga, 112 casos de `dentro_muestra` quedaron como fallos tecnicos (sin respuesta del
modelo: `GeminiUnavailableError`, 0 tokens). La desviacion y su amenaza a la validez estan en la
seccion «Desviaciones del prerregistro» de `design.md`. Solo se reintentan los registros en
`fallback` con error de indisponibilidad o transporte y sin tokens; las respuestas invalidas del
modelo no se reintentan. El cache es append-only: el reintento agrega un registro nuevo con
`reintento_de_fallo_tecnico: true` y `ronda`, y el analisis usa el ultimo registro de cada caso.

Contabilidad: el tope de 400 rige las llamadas que obtuvieron respuesta del modelo; los intentos
sin respuesta se cuentan aparte y un cinturon de 600 acota los intentos totales.

```bash
# sin costo: informa casos a reintentar, pendientes nuevos y costo estimado; no escribe nada
python -m evaluation.brazo_gemini_solo --dry-run --reintentar-fallos-tecnicos

# PAGA (requiere GEMINI_API_KEY bien cargada y el visto bueno de gasto)
python -m evaluation.brazo_gemini_solo --confirmar-costo --reintentar-fallos-tecnicos
```

Sin `--reintentar-fallos-tecnicos` el ejecutor no vuelve a llamar ningun caso ya registrado.

- Pruebas (cliente simulado, sin red): `python -m pytest evaluation/tests/test_brazo_gemini_solo.py -q`
  y `python -m pytest evaluation/data/campana/analisis/test_analisis_brazo_gemini_solo_c215.py -q`.
- Limitaciones declaradas: los intentos fallidos sin respuesta no aportan tokens (el costo de un
  caso con fallas queda subestimado); la latencia es del lado del cliente y desde la maquina de
  quien corre; el control de deriva no separa deriva del modelo de azar de muestreo a temperatura
  0,3.
