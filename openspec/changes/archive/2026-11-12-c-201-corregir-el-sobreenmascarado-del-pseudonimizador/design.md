# Design: Corregir el sobreenmascarado del pseudonimizador (change c-201)

## Context

Ver `proposal.md` — Why. Estado de partida verificado al proponer (2026-11-12):

- `App/Backend/app/utils/pseudonymizer.py` aplica `_RE_PERSONA` (2+ palabras capitalizadas) y `_is_excluded_persona` solo consulta `_EXCLUSION_PERSONA` y `_TECHNICAL_TERMS` (más la composición de tokens técnicos). No hay regla de determinante ni comparación insensible a tildes.
- La salida del módulo sobre el corpus de la tesis (`data/Corpus Tesis - Hoja 1 (pseudonimizado).csv`) tiene 9 etiquetas: 1 `[TELEFONO]` sobre el código DLL de R067 y 8 `[PERSONA]` (R032, R034, R070, R074, R125, R161, R167, R193).
- El corpus evaluado `data/corpus_evaluacion_pseudonimizado.json` (200 casos) tiene 0 etiquetas y coincide con el crudo `data/Corpus Tesis - Hoja 1.csv` en las 200 descripciones, ignorando espacios finales. Verificado: 0 diferencias crudo/JSON y 9 diferencias CSV-pseudonimizado/JSON.
- No hay test que afirme el contenido ni el SHA-256 del CSV pseudonimizado. `data/README.md` no registra hash de ese archivo; `evaluation/data/campana/README.md` registra hashes de otros artefactos (corpus JSON, tablas de campaña), que este change no toca.
- Producción pseudonimiza antes de clasificar (`App/Backend/app/services/incidente_service.py:345-347`). El corpus evaluado es el texto crudo limpio, por lo que hoy producción clasifica texto sobreenmascarado y la evaluación no.

## Goals / Non-Goals

**Goals:**

- Reducir a cero los falsos positivos observados en la heurística de persona sin debilitar la cobertura de PII genuina.
- Fijar el comportamiento con tests que cubran cada falso positivo y las regresiones de PII real.
- Regenerar el CSV publicado con el módulo corregido y probar su equivalencia con el corpus evaluado.
- Documentar la frontera y dejar asentado que las métricas no cambian.

**Non-Goals:**

- No se modifica `app/classifiers/`, `docs/prompt_gemini.txt`, `app/constants.py`, el clasificador, el JSON del corpus evaluado ni la tesis.
- No se ejecuta una corrida paga de Gemini ni se re-miden métricas.
- No se implementa NER ni un modelo de lenguaje: sigue siendo una heurística regex.

## Decisions

### D1. Determinante inicial: se quita y se evalúa el resto, no se salta la frase completa

Alternativa considerada: si la frase empieza con determinante, preservarla entera. Se descarta porque debilitaría la cobertura: `"El Juan Pérez"` o `"La Presidenta Cristina Fernández"` dejarían de enmascarar el nombre real.

Decisión: en `_replace_persona`, si el primer token pertenece a `_DETERMINANTES` (`El`, `La`, `Los`, `Las`, `Un`, `Una`, `Unos`, `Unas`, `Su`, `Sus`, `Este`, `Esta`, `Estos`, `Estas`, `Ese`, `Esa`, `Esos`, `Esas`, `Aquel`, `Aquella`, `Mi`, `Mis`, `Tu`, `Tus`, `Nuestro`, `Nuestra`, `Nuestros`, `Nuestras`), se separa el determinante y se evalúa el resto con las reglas existentes:

- resto de una sola palabra (`PC`, `ID`, `Heras`) → se preserva la frase completa;
- resto con 2+ palabras capitalizadas y no excluido → se enmascara solo el resto y se conserva el determinante (`"El Juan Pérez"` → `"El [PERSONA]"`, `"La PC de Juan Pérez"` → `"La PC de [PERSONA]"`);
- resto excluido por sector o allowlist → se preserva.

Esto cubre `Su PC`, `La PC`, `El ID` y `Las Heras` sin depender de una lista de lugares.

### D2. Sectores canónicos insensibles a tildes

Se normaliza el candidato y cada sector con `unicodedata.normalize("NFKD")`, se descartan los caracteres combinantes y se compara en minúsculas. Así `Seguridad Informática` cae en el mismo conjunto que `Seguridad Informatica`. No se tocan los strings canónicos de `app/constants.py`; la normalización es local al pseudonimizador.

### D3. Allowlist ampliada por frase completa, no por token ambiguo

Se agregan frases observadas a `_TECHNICAL_TERMS` (o a una allowlist equivalente): `Adobe PDF Reader`, `Microsoft Vision`, `NET Framework`, `Recursos Humanos`, `Acceso Denegado`, `San Juan`, `Casa Matriz`, `Rio Negro`, `Cordoba Capital`. La comparación de frases es insensible a tildes para admitir `Río Negro` y `Córdoba Capital`.

No se agregan tokens ambiguos (`Reader`, `Vision`, `Framework`) al mecanismo de composición por tokens: eximirían por sí solos frases que podrían ser nombres reales (`John Reader`). El mecanismo de tokens existente se conserva solo para tokens técnicos inequívocos.

### D4. Alcance de los topónimos

`Las Heras` queda cubierto por D1. `San Juan`, `Casa Matriz`, `Rio Negro` y `Cordoba Capital` quedan cubiertos por D3. Un topónimo no listado y sin determinante sigue siendo un falso positivo residual posible; se documenta como limitación, coherente con el tradeoff regex ya aceptado.

### D5. Regeneración del CSV con el script existente

Se usa `scripts/corpus_ingest/pseudonymize_corpus.py`, que importa el pseudonimizador de producción y es la única fuente de verdad de los patrones. Comando: `python scripts/corpus_ingest/pseudonymize_corpus.py --out "data/Corpus Tesis - Hoja 1 (pseudonimizado).csv"`. El writer preserva CRLF y las columnas; la verificación compara las 200 descripciones con el JSON ignorando espacios finales. No se actualiza ningún SHA-256 porque no existe referencia al CSV; los hashes de `evaluation/data/campana/README.md` corresponden al corpus JSON y a artefactos de campaña que no cambian.

### D6. Métricas: el cambio es un no-op sobre la evaluación

El corpus evaluado es el texto crudo, que no contiene PII. Con el módulo corregido, la pseudonimización del crudo devuelve el mismo texto (0 etiquetas), igual que hoy. Por lo tanto el JSON evaluado no cambia, las predicciones y métricas reportadas siguen siendo válidas y no se requiere una corrida paga. El único efecto observable es en producción: los incidentes nuevos dejan de perder términos como `PC`, `Adobe PDF Reader` o `Recursos Humanos` antes de clasificar.

### D7. TDD y orden de trabajo

Primero se agregan los tests que fallan (falsos positivos y regresiones de PII real), luego la implementación mínima, después la triangulación con variantes acentuadas y mixtas, y por último el refactor. La suite existente `App/Backend/tests/test_pseudonymizer.py` y `scripts/corpus_ingest/test_pseudonymize_corpus.py` es la red de seguridad y debe seguir verde.

### D8. Teléfono: lookbehind `(?<![\w])` para no fragmentar dígitos embebidos en un token alfanumérico

Decisión implementada durante el apply que no figuraba en las decisiones originales. En `App/Backend/app/utils/pseudonymizer.py`, `_RE_TELEFONO` ahora arranca con el lookbehind `(?<![\w])`; el mismo criterio se aplicó a `_RE_RESIDUAL_PHONE` en `scripts/corpus_ingest/pseudonymize_corpus.py`.

- (a) Motivo: el spec exige 0 `[TELEFONO]` sobre el corpus. La descripción de R067 contiene el código DLL `axm0102301239999320002302`, una corrida de dígitos EMBEBIDA en un token alfanumérico; sin el lookbehind, el patrón la fragmentaba como teléfono y producía un falso positivo. Con el lookbehind, un teléfono solo se reconoce cuando arranca en el límite de un token.
- (b) Riesgo residual (tradeoff deliberado): un teléfono pegado a un carácter de palabra precedente (por ejemplo `tel2615551234`) ya no se detecta, porque la corrida de dígitos arranca en medio de un token alfanumérico. Se acepta: en el corpus y en el flujo de producción los teléfonos aparecen como tokens delimitados (espacios, signos o inicio de texto), y la prioridad es eliminar el falso positivo que el spec prohíbe.
- (c) Tests que lo fijan: `test_pseudonymize_r067_dll_no_se_clasifica_como_telefono` (el código DLL de R067 no se fragmenta como teléfono), `test_pseudonymize_pii_genuina_completa_sigue_enmascarandose` (un teléfono genuino, junto con el resto de la PII, sigue enmascarándose) y `test_residual_scan_ignores_digits_embedded_in_alphanumeric_token` (el escaneo residual del script ignora los dígitos embebidos en un token alfanumérico).

## Risks / Trade-offs

- **Subenmascaramiento por D1** → el resto se sigue evaluando con las reglas existentes; se agregan regresiones con nombres reales en la misma oración (`"La PC de Juan Pérez"`, `"María Núñez"`).
- **Frase de allowlist que colisione con un nombre real** → se usan frases completas y se evitan tokens ambiguos.
- **Topónimos no listados** → limitación residual documentada; no se promete cobertura universal de lugares.
- **Cambio de formato al regenerar el CSV** → el writer conserva CRLF, quoting y columnas; la revisión del diff debe mostrar solo la eliminación de las 9 etiquetas.
- **Dependencia oculta de que el término se enmascare** → se corre la suite completa del backend, no solo el archivo del pseudonimizador.

## Migration Plan

No hay migración de datos ni backfill: el cambio solo afecta el procesamiento de texto nuevo. Rollback: revertir `pseudonymizer.py`, sus tests, `docs/pseudonymization.md` y el CSV regenerado. El corpus evaluado no se toca, por lo que el rollback no afecta métricas ni evidencia.

## Open Questions

None.