## Why

La tesis sostiene como hipótesis subsidiaria que el esquema híbrido (reglas determinísticas,
Gemini, revisión humana) es más eficiente que usar solo el modelo de lenguaje, pero esa
hipótesis nunca se midió: el texto repite que la eficiencia frente a un esquema solo-modelo
«sigue sin contrastarse». El dictamen CONEAU sobre v1.3.0 lo señala como carencia de línea de
base (criterio 4) y como hipótesis sin contraste (criterio 1). Las líneas de base clásicas
(TF-IDF y reglas solas) ya se cubrieron en c-209, c-210 y c-213; falta el brazo «Gemini solo»,
que manda TODOS los casos a la misma etapa Gemini congelada, sin reglas. Este change prepara,
sin gasto, el código del brazo, su análisis pareado y la regla de decisión prerregistrada,
dejando la corrida paga como un paso humano explícito.

## What Changes

- **Ejecutor del brazo «Gemini solo»** (`evaluation/brazo_gemini_solo.py`): clasifica los 200
  casos dentro de la muestra y los 103 fuera de muestra (consenso `E3`/`E4`) con la etapa Gemini
  REAL del backend inyectándole un cliente instrumentado (mismo modelo, prompt, parámetros de
  muestreo, validación del Anexo H y reintentos que el híbrido). Caché incremental reanudable
  en disco, registro por caso (predicción, confianza, latencia, tokens, intentos, error), tope
  duro de llamadas, modo `--dry-run` sin red ni clave, exigencia de `--confirmar-costo` para
  llamar de verdad, verificación de la versión del SDK y de que el prompt cargado sea el
  congelado. Nunca imprime ni guarda la clave.
- **Análisis pareado** (`evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py`):
  a partir del caché del brazo y de las predicciones congeladas del híbrido calcula exactitud
  estricta y laxa y macro-F1; McNemar exacta bilateral y diferencia de exactitudes con IC
  bootstrap pareado; medidas de eficiencia (llamadas, tokens, costo y latencia por caso) con
  razones e IC; el control de deriva sobre los casos que el híbrido ya escaló; y el veredicto de
  tres vías (sostenida, no sostenida, no concluyente) con salidas JSON y Markdown deterministas.
- **Prerregistro** de la regla de decisión, el margen de no inferioridad (`δ = 0,05`), el tope
  de llamadas (`400`), el número de corridas (una) y los precios, fijados en `design.md` antes
  de cualquier dato del brazo.
- **No incluye** la corrida paga, las salidas reales, el registro de cifras canónicas ni la
  prosa de la tesis: quedan como tareas `[CORRIDA PAGA]` y `[AUTORES]` sin marcar.

## Capabilities

### New Capabilities

- `gemini-solo-arm`: ejecutor y análisis del brazo «Gemini solo» frente al híbrido congelado, con la regla de decisión prerregistrada para la hipótesis subsidiaria de eficiencia.

### Modified Capabilities

(ninguna: el change agrega código y análisis de `evaluation/` y no cambia requisitos del clasificador ni del marco de evaluación)

## Impact

- **Código nuevo** (TDD, sin tocar el backend): `evaluation/brazo_gemini_solo.py`,
  `evaluation/tests/test_brazo_gemini_solo.py`,
  `evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py` y su prueba hermana.
- **Lectura sin edición**: `App/Backend/app/classifiers/*`, `docs/prompt_gemini.txt`,
  `openspec/config.yaml`, `data/*`, las cachés de predicciones de `evaluation/evidence/` y
  `evaluation/data/campana/`.
- **Costo**: este change NO gasta nada (todas las pruebas usan un cliente simulado). La corrida
  paga posterior es de ~303 llamadas lógicas, del orden de 0,22 USD a precio introductorio y
  0,43 USD a precio estándar, con tope duro de 400 llamadas.
- **Gobernanza**: MEDIUM (análisis nuevo, sin cambio de conducta productiva). La corrida paga
  requiere a una persona con `GEMINI_API_KEY` y su visto bueno de gasto.
- **Dependencias**: se apila sobre c-214 (misma tubería de análisis y estilo de salidas).
  `google-genai` instalado en la máquina de desarrollo es 2.8.0 y el proyecto fija `>=2.33,<3`:
  el ejecutor verifica la versión y aborta con un mensaje claro si no se cumple.
