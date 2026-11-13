## Context

Hechos verificados en el repositorio al proponer (2026-11-13):

- **Híbrido congelado `hybrid-v3`.** Predicciones en
  `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (200 casos: 131 resueltos por las
  reglas y 69 por Gemini) y `evaluation/data/campana/predicciones_independiente.json` (103 casos
  con consenso `E3`/`E4`: 69 reglas y 34 Gemini; commit `561b3c4`, `google-genai 2.34.0`). Cada
  registro guarda `sector_predicho`, `confianza` y `etapa`; NO guardan latencia, tokens ni
  reintentos. Las predicciones del bloque de 200 son del 2026-10-07; las del bloque de 103, del
  2026-11-12.
- **Etapa Gemini real.** `GeminiClassifier` (`App/Backend/app/classifiers/gemini_classifier.py`)
  acepta un cliente inyectado y llama a `client.aio.models.generate_content`; aplica la
  validación del Anexo H (§H.3), un reintento acotado ante fallas transitorias
  (`gemini_max_retries = 2`, hasta 3 intentos por caso) y un `fallback` con confianza 0,0 ante
  respuesta inválida. Un cliente instrumentado desde `evaluation/` permite medir latencia y
  `usage_metadata` sin tocar el backend.
- **Patrón de las ablaciones pagas existentes** (`evaluation/sensibilidad_ajustes.py`): guarda
  `PaidRunNotConfirmedError`, entorno inerte para construir `Settings`, hash del prompt cargado,
  `cache_meta` con pines. Este change imita el patrón, pero lee `GEMINI_API_KEY` SOLO del entorno
  y no abre archivos `.env`.
- **Estadística disponible.** `evaluation/stats.py` (`contraste_mcnemar`, exacta bilateral),
  `evaluation/metrics.py` (`intervalo_wilson`, `f1_por_clase`, `f1_macro`, `aciertos_laxos`,
  `percentil_intervalo`, `remuestreos_indices`, `SEMILLA_BOOTSTRAP = 20261021`). El análisis
  hermano `contraste_linea_de_base_c213.py` fija el estilo de salida (JSON y Markdown con LF,
  UTF-8 sin BOM, `SHA256SUMS`) y el bootstrap pareado con 10 000 remuestreos.
- **Precio.** El repositorio no versiona ningún precio actual: solo
  `ESTIMATED_COST_PER_CALL_USD = 0.0002` (orden de magnitud viejo, «no es una tarifa»). El
  precio citado por la tesis (sección 8, `08-discusion.tex`, consultado el 2026-10-19) es
  0,75 USD por millón de tokens de entrada y 3,75 USD por millón de salida, introductorio hasta
  el 2026-12-31, y 1,50/7,50 USD desde el 2027-01-01. Se declara como PARÁMETRO del ejecutor y del
  análisis (D6), no como constante oculta.
- **Memoria del proyecto.** No hay corrida previa del brazo «Gemini solo» sobre `hybrid-v3`. La
  única caché de Gemini sobre todos los casos es la histórica FORCE-ESCALATE `hybrid-v2`, con
  hash de corpus distinto y versión de prompt no atribuible: no sirve como brazo de este change.

## Goals / Non-Goals

**Goals:**

- Dejar listo y probado (sin gasto) el código para correr el brazo «Gemini solo» y analizarlo de
  forma pareada contra el híbrido congelado.
- Prerregistrar, antes de cualquier dato, qué se compara, con qué estadístico y cómo se decide
  la hipótesis de eficiencia, incluido el resultado desfavorable.
- Que la corrida paga sea reproducible, reanudable, acotada en gasto y auditable.

**Non-Goals:**

- Cambiar clasificador, prompt, umbrales, vocabulario, `settings.py` o `openspec/config.yaml`.
- Correr el brazo, generar salidas reales, registrar cifras canónicas o escribir la prosa de la
  tesis (tareas `[CORRIDA PAGA]` y `[AUTORES]`).
- Reponer las líneas de base clásicas (TF-IDF, reglas solas): ya están en c-209, c-210 y c-213.
- Medir tiempos de extremo a extremo o variabilidad entre repeticiones del modelo.

## Decisions

### D1 — Brazos y qué se compara

- **H**: híbrido congelado `hybrid-v3`, predicciones de las cachés versionadas; sin re-correr.
- **L** («Gemini solo»): TODOS los casos pasan por la etapa Gemini real con el prompt, el modelo
  y los parámetros de muestreo congelados, la validación del Anexo H y los reintentos del
  backend, sin reglas.
- **Calidad**: exactitud estricta (PRIMARIA), exactitud laxa (sector predicho dentro de
  `sector_asignado` más `sectores_adicionales`, definición de c-191/c-205) y macro-F1 sobre las
  cinco clases (incluida toda clase de soporte cero, como en c-205).
- **Eficiencia**: llamadas al modelo por caso (todo intento a la API cuenta, reintentos
  incluidos), tokens de entrada y de salida, costo estimado en USD y latencia por caso.
- **Sensibilidad H\***: «híbrido recompuesto», es decir, la predicción cacheada de H donde las
  reglas resolvieron (`etapa = deterministic`) y la predicción NUEVA de L donde H escaló. Aísla
  el efecto del enrutamiento del ruido o la deriva del modelo entre fechas. Se informa, no decide.

### D2 — Corpus y apareamiento

- **Primario**: bloque fuera de muestra de 103 casos (`evaluation/data/campana/corpus_independiente.json`,
  consenso `E3`/`E4`). Ni el vocabulario, ni el prompt ni el ajuste de umbrales vieron esos
  casos.
- **Secundario**: los 200 casos dentro de la muestra, referencia original. Rotulado «dentro de
  la muestra»: el vocabulario y el prompt se ajustaron con esos casos, así que NO es prueba
  limpia y es optimista para H (las reglas se diseñaron con ellos).
- Se reutilizan los cargadores existentes (`cargar_corpus_solo_lectura`, `cargar_predicciones`).
  El apareamiento es por `caso_id`; el análisis aborta sin escribir si falta o sobra algún caso
  en cualquiera de los dos brazos o si el hash del corpus del caché difiere del corpus actual.
- No se mezclan bloques en una sola estimación (referencias distintas): cada bloque se analiza
  por separado y solo el primario decide.

### D3 — Ejecutor del brazo L

- Reutiliza `GeminiClassifier` por inyección: NO duplica el prompt ni la validación. Inyecta un
  cliente instrumentado (envoltorio de `client.aio.models.generate_content`) que mide
  `perf_counter` por intento, copia `usage_metadata` (entrada, salida más razonamiento, total),
  cuenta intentos y hace cumplir el tope de llamadas.
- **Caché incremental reanudable**: archivo JSONL, una línea de metadatos y una línea por caso
  terminado, con `flush` y `fsync` por caso. Al reanudar se omiten los casos ya registrados, el
  contador de llamadas es acumulado y se verifica que los metadatos (hashes de corpus, modelo,
  parámetros, SHA-256 del prompt, versión del SDK) coincidan; si no, aborta.
- **Registro por caso**: bloque, `caso_id`, `sector_predicho`, `confianza`, `etapa`, `intentos`,
  `latencia_ms` (total del caso, incluidas esperas de reintento), `latencias_intento_ms`,
  `tokens_entrada`, `tokens_salida`, `tokens_total`, `tokens_origen` (`api` o `supuesto`) y
  `error`. Un fallo del proveedor se registra con `sector_predicho = null`; una respuesta
  inválida conserva el marcador del backend (`Sistemas`, confianza 0,0, etapa `fallback`).
- **Guardas, en este orden y antes de la primera llamada**: confirmación explícita
  (`--confirmar-costo`), versión del SDK dentro de `>=2.33,<3` (el pin de `openspec/config.yaml`),
  presencia de `GEMINI_API_KEY` en el entorno (jamás impresa ni guardada), SHA-256 del prompt
  cargado igual al de `docs/prompt_gemini.txt`, tope de llamadas no superior al prerregistrado.
- **`--dry-run`**: no llama a la API, no lee la clave y no escribe el caché; cuenta casos
  pendientes, llamadas mínimas y máximas y costo estimado con los precios declarados.
- **Tope duro de llamadas: 400** (303 casos más un margen de ~32 % para reintentos). Si el
  contador acumulado llegaría a superarlo, el cliente instrumentado se niega a emitir la llamada,
  el ejecutor conserva lo hecho, sale con código 3 y reporta cuántos casos quedaron pendientes.
  El tope NO puede subirse por línea de comandos (solo bajarse); subirlo exige cambiar este
  diseño.

### D4 — Corridas y no determinismo

- **Una sola corrida** del brazo L. La temperatura configurada es 0,3 (`top_p` 0,9): la salida
  del modelo no es determinística, así que cualquier diferencia caso a caso mezcla azar de
  muestreo, deriva del modelo servido y efecto del enrutamiento. La repetición (p. ej. 3 corridas)
  triplicaría el gasto y, con n = 103, no cambia la potencia del contraste; se declara como
  limitación y como trabajo futuro, y el control de deriva (D8) cuantifica la inestabilidad.
- Las salidas del análisis incluyen el rótulo de procedencia de la corrida (fechas, pines, SDK).

### D5 — Estadística del contraste de calidad

Sobre cada bloque, pareado caso a caso entre H y L:

- Tabla 2×2 de aciertos estrictos y **McNemar exacta bilateral** (`contraste_mcnemar`,
  p exacto; se informa también el corregido por continuidad y el criterio de `stats.py`).
- **Diferencia de exactitudes** `Δ = exactitud(H) − exactitud(L) = (b − c)/n` con IC95 bootstrap
  percentil pareado (remuestreo de casos, **semilla 20261021**, 10 000 remuestreos, como c-213).
- Exactitud y exactitud laxa con IC de Wilson por brazo; macro-F1 por brazo (puntual, sin IC,
  como en c-205). Un contraste no significativo se rotula «no se detectó diferencia», nunca
  «equivalentes».

### D6 — Eficiencia: medidas y precio

- **Llamadas por caso**: L = intentos observados. Para H se imputa `1[H escaló] × intentos_L` del
  mismo caso (mismo prompt y modelo); las reglas no llaman al modelo. Por construcción H no puede
  usar más llamadas que L.
- **Tokens y costo**: de la corrida de L, con la misma imputación para H. El costo por caso es
  `tokens_entrada × p_in + tokens_salida × p_out`, sumando todos los intentos (cada intento
  facturable). Si la API no devuelve `usage_metadata` de un intento, se imputa el supuesto de la
  tesis (800 tokens de entrada y 30 de salida) y el caso se rotula `tokens_origen = supuesto`; el
  análisis informa cuántos casos usaron el supuesto.
- **Precio (parámetro declarado, no versionado en el repositorio)**: escenario introductorio
  (0,75/3,75 USD por millón de tokens de entrada/salida, vigente hasta 2026-12-31) como
  escenario principal, porque es el vigente al correr; escenario estándar (1,50/7,50) como
  sensibilidad. Fuente: sección 8 de la tesis. Los precios viven en un diccionario único de
  `evaluation/brazo_gemini_solo.py` y el análisis los toma de los metadatos del caché, de modo
  que lo reportado es lo que se usó. El dry-run estima 0,0007125 USD por llamada (800/30 tokens).
- **Razones**: `razón_llamadas = Σ llamadas_H / Σ llamadas_L` y `razón_costo = Σ costo_H / Σ costo_L`,
  cada una con IC95 bootstrap pareado (mismos remuestreos de casos, misma semilla).
- **Latencia por caso**: media por caso con IC95 bootstrap de la diferencia `L − H`. Para H se
  imputa `1[H escaló] × latencia_L` del caso y 0 ms para las reglas (cota inferior: la latencia
  de las reglas es de milisegundos y se declara despreciable). Es latencia de clasificación del
  lado del cliente, desde la máquina de los autores; no es tiempo de extremo a extremo. Se informa
  pero NO entra en la regla de decisión (depende de la red y de la carga del proveedor).

### D7 — Regla de decisión prerregistrada de tres vías

Sobre el bloque PRIMARIO (103), con `δ = 0,05` y `Δ` e IC95 de D5:

- **Componente de exactitud (no inferioridad)**: *no inferior* si `Δ_inf > −δ`; *inferior* si
  `Δ_sup < −δ`; *indeterminado* en otro caso.
- **Componente de eficiencia**: *cumplido* si el límite superior del IC95 de `razón_costo` Y el de
  `razón_llamadas` son menores que 0,90 (el híbrido ahorra de forma material al menos 10 %);
  *no cumplido* en otro caso.
- **Veredicto**: **«sostenida»** = no inferior y eficiencia cumplida; **«no sostenida»** =
  inferior, o eficiencia no cumplida; **«no concluyente»** = exactitud indeterminada con
  eficiencia cumplida.
- **Validez de la corrida**: el análisis exige cobertura completa de los 303 casos y que los
  `fallback` y errores del brazo L sean ≤ 5 % de los casos del bloque; si los superan, el
  veredicto se fuerza a «no concluyente» con el motivo escrito. Una corrida incompleta aborta.
- La lectura dentro de la muestra y la sensibilidad H\* se informan con la misma regla aplicada
  y rotuladas, pero no cambian el veredicto.

**Justificación de `δ = 0,05` (por principio, antes de los datos).** Un punto de no inferioridad
debe fijarse por lo que es operativamente tolerable, no por lo observado: 5 puntos porcentuales
equivalen a una derivación equivocada adicional por cada 20 incidentes, magnitud que un
operador de mesa de ayuda aceptaría a cambio de un ahorro material de costo y de latencia, y es
el orden de la tolerancia usada habitualmente en pruebas de no inferioridad de clasificadores.
Se fija una sola vez y no se reajusta. Con n = 103 el contraste tiene poca potencia para
demostrar no inferioridad con este margen salvo que H y L discrepen en muy pocos casos; por eso
«no concluyente» es un resultado posible y esperable, y se informa con ese nombre.

### D8 — Amenazas a la validez y controles

- **Deriva del modelo servido.** Las predicciones de H son del 2026-10-07 (200) y del 2026-11-12
  (103); L se correrá en otra fecha. Control: sobre los casos que H ya escaló (69 + 34 = 103),
  L re-llama al mismo modelo con el mismo prompt, así que su acuerdo con la predicción cacheada
  de H mide concordancia (con IC de Wilson) y, además, McNemar entre ambas. No requiere llamadas
  extra. Bandera prerregistrada: concordancia < 0,90 → «deriva o ruido relevante: leer el
  contraste con cautela». Este control NO separa deriva de azar de muestreo a temperatura 0,3.
- **Casos de ajuste.** Dentro de la muestra no es prueba limpia (D2); el primario es el bloque
  fuera de muestra.
- **Análisis no ciego.** Las exactitudes de H ya son conocidas por los autores; se mitiga con
  este prerregistro en el commit previo a cualquier dato del brazo, que debe ser anterior al
  commit del caché de L.
- **Fallos del proveedor.** Se cuentan y se acota su incidencia (D7); no se reintenta fuera de los
  reintentos del backend.
- **Versión del SDK.** El ejecutor aborta si no se cumple `>=2.33,<3`; la versión usada se
  registra en el caché.

### D9 — Artefactos, archivos y salidas

Código: `evaluation/brazo_gemini_solo.py`, `evaluation/tests/test_brazo_gemini_solo.py`,
`evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py` y su prueba hermana. Caché
del brazo: `evaluation/data/campana/brazo_gemini_solo/cache_brazo_gemini_solo.jsonl` (no existe
hasta la corrida paga). Salidas del análisis: `analisis_brazo_gemini_solo_c215.{json,md}` y
`.SHA256SUMS.txt`, deterministas (LF, UTF-8 sin BOM). Si el caché real no existe, el análisis
sale con código distinto de cero y un mensaje claro, sin escribir nada. Los comandos exactos
(dry-run, corrida, análisis) viven en `evaluation/data/campana/analisis/README.md`.

### D10 — Gobernanza

MEDIUM: código y análisis nuevos, sin cambio de conducta productiva ni de configuración. La
corrida paga requiere a una persona con `GEMINI_API_KEY` y su visto bueno de gasto; ningún agente
la ejecuta.

## Risks / Trade-offs

- [Con n = 103 el veredicto probablemente sea «no concluyente»] → se prerregistra y se informa con
  ese nombre; no se amplía `δ` ni se agrega cobertura post hoc.
- [Ruido de muestreo mezcla enrutamiento y azar] → H\* y el control de deriva (D8); una sola
  corrida declarada (D4).
- [Precio no versionado en el repositorio] → parámetro declarado y guardado en los metadatos del
  caché; se reportan ambos escenarios.
- [La clave podría filtrarse por logs] → el código solo la lee del entorno, no la imprime, no la
  guarda y los errores del SDK se reducen al nombre de su clase.
- [Una caída a mitad de corrida] → caché reanudable con contador acumulado de llamadas.
- [SDK instalado local (2.8.0) por debajo del pin] → aborto explícito; la persona que corra debe
  instalar la versión del pin fuera de este change.
