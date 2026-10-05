# Design — c-71-hardening-clasificador-determinista

## Context

Ver `proposal.md` — Why para la motivacion y la evidencia medida. Estado actual relevante:

- `DeterministicClassifier.classify` (`App/Backend/app/classifiers/deterministic.py`) calcula `score(cat)` = cantidad de patrones distintos con match y `confianza = winner/(winner+second+eps)`. Ordena por score y toma `sorted_cats[0]` como ganador; con senal nula el ganador es la primera clave del mapa (`Seguridad Informatica`) con confianza 0.0.
- `HybridClassifier.classify` (`App/Backend/app/classifiers/hybrid.py`) cortocircuita si `det_result.confianza >= deterministic_confidence_threshold` (0.90) y escala a Gemini en caso contrario; si Gemini falla, el fallback preserva `det_result.sector_predicho`.
- `ClasificacionResult.sector_predicho` es `str` no nulo; `incidente.sector_id` es `int | None` (nullable), de modo que la persistencia admite ausencia.
- `HYBRID_CACHE_VERSION = "hybrid-v1"` en `App/Backend/app/constants.py` es la version que invalida el cache de predicciones de la evaluacion (C-34).
- Los cinco strings canonicos estan LOCKED y `evaluation/corpus.py::_a_float` es intocable.

## Goals / Non-Goals

**Goals**
- Eliminar la prediccion arbitraria por no-match y la eleccion arbitraria por empate.
- Volver la confianza determinista una medida significativa y el umbral una decision calibrada y auditable.
- Elevar la cobertura del vocabulario sobre el corpus sin degradar precision por sector.
- Dejar la re-medicion reproducible (cache invalidado, medicion offline + hibrida).

**Non-Goals**
- No unificar el canal `telefono` a la cascada (OQ4: pasa por el AI Agent de n8n con clasificacion precalculada; change aparte si se desea).
- No cambiar los cinco strings canonicos, ni `evaluation/corpus.py::_a_float`, ni el esquema persistente (no hay migracion).
- No introducir dependencias nuevas ni llamadas pagas en la calibracion offline.

## Decisions

### D1: No-match -> estado explicito de ausencia de prediccion (sin inventar sector)

Con `winner_score == 0`, el determinista devuelve un resultado con `confianza=0.0` y un marcador explicito `sin_prediccion=True` (y `sector_predicho=None` en el DTO interno), en lugar de la primera clave del mapa. El estado es transitorio: el `HybridClassifier` lo detecta y escala a Gemini. Alternativas: (a) mantener un sector sentinel — descartada porque inventa un sector y sesga la metrica; (b) derivar directo a revision humana — es la OQ2, gated por el autor; el diseno implementa el marcador y deja la politica de ruteo como decision. `incidente.sector_id` nullable permite persistir la ausencia si el fallback termina sin estimacion (D4/D8).

### D2: Empate -> ambiguedad marcada, sin ganador arbitrario

Si el puntaje maximo lo comparten dos o mas sectores, el resultado se marca `ambiguo=True` y `confianza` no puede alcanzar el cortocircuito; el pipeline escala. Se elimina la dependencia del orden de las claves para desempatar. Alternativa: desempate por heuristica de prioridad — descartada porque reintroduce un sesgo arbitrario no auditable.

### D3: Confianza con conteo minimo de matches y margen sobre el segundo

La confianza deja de ser `winner/(winner+second+eps)` (que vale 1.0 con un solo match). Se define a partir de: (1) un **conteo minimo** `min_matches` — con `winner_score < min_matches` la confianza es 0.0; y (2) un **margen** `margin = winner_score - runner_up_score` — la confianza crece con el margen y se anula ante empate. Una forma candidata a validar por tests es `confianza = (winner - runner) / (winner + runner + eps)` con un factor de suficiencia por `min_matches`, acotada a [0.0, 1.0]; la forma final la fija la triangulacion, no el diseno. `min_matches` y `margin` son parametros configurables (sin recompilar).

### D4: Calibracion del umbral por curva precision/cobertura

Se construye, OFFLINE sobre el corpus, la curva de precision/cobertura del subconjunto cortocircuitado en funcion del umbral. Se elige el umbral que maximiza cobertura sujeto a un **piso de precision** (OQ1). Si OQ3 resuelve "umbral derivado del corpus", la calibracion se materializa como un valor documentado/derivado; si resuelve "setting fijo", el valor calibrado se fija en `Settings`. En ambos casos el umbral es explicito y verificable. Alternativa: mantener 0.90 — descartada porque es degenerado.

### D5: Estrategia de ampliacion del vocabulario

Ampliacion guiada por las misclasificaciones del corpus: agregar sinonimos, variantes morfologicas y frases por sector, priorizando Hardware y Software (mayor soporte real). Se preserva la invariante `set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)` (assert estructural) y los cinco strings exactos. La ampliacion se valida por triangulacion por sector (falsos positivos) y por la metrica de cobertura (D6), no por inspeccion.

### D6: Medicion de cobertura offline

Se agrega un camino de medicion que corre el `DeterministicClassifier` sobre el corpus (sin Gemini) y reporta cobertura global y por sector, cantidad de no-match, y la curva precision/cobertura. Reutiliza el corpus y `evaluation/metrics.py`; NO toca `_a_float`.

### D7: Contrato aditivo y disciplina de capas

`ClasificacionResult` gana campos aditivos con default seguro (`sin_prediccion: bool = False`, `ambiguo: bool = False`) y `sector_predicho` pasa a `str | None`; los consumidores y schemas de API se ajustan para manejar la ausencia sin romper. La logica vive en los clasificadores (internos al backend); routes -> services -> repositories -> models se respeta. No hay migracion: `incidente.sector_id` ya es nullable.

### D8: Cache version y re-medicion

`HYBRID_CACHE_VERSION` se sube a `hybrid-v2` para invalidar las predicciones persistidas por C-34. Plan de re-medicion: (1) F1 determinista y cobertura OFFLINE sobre el corpus (sin Gemini); (2) F1 hibrido cuando se restaure la cuota de Gemini (OQ5), con baseline explicito; (3) documentar el delta en `docs/` (parametros/Anexo H). Si no hay baseline Gemini, se declara PENDIENTE en lugar de fabricar comparaciones.

### D9: TDD y tests estructurales

Todo cambio de codigo con RED-GREEN-TRIANGULATE-REFACTOR y safety net por tarea. Tests estructurales: invariante de claves del mapa, confianza acotada, strings canonicos intactos, `_a_float` intacto, y el cortocircuito gobernado por el umbral calibrado.

### D10: Gobernanza

MEDIO. Cambia resultados de clasificacion que alimentan la evaluacion de la tesis (puede afectar F1). Sin auth, sin esquema persistente, sin infraestructura. Las decisiones de calibracion y ruteo quedan como OQ para el autor.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|--------|------------|
| Recalibrar baja cobertura y sube costo Gemini | Curva precision/cobertura con piso de precision (OQ1); tradeoff documentado |
| Vocabulario ampliado genera falsos positivos | Triangulacion por sector + medir precision, no solo cobertura |
| Cambio de contrato (`sector_predicho` opcional) rompe consumidores | Campos aditivos con default seguro; tests de contrato/API |
| Delta de F1 no atribuible sin baseline Gemini | Cache version bump + declarar baseline pendiente (OQ5) |
| Tocar strings canonicos o `_a_float` | Prohibido; tests estructurales lo verifican |

## Migration Plan

1. Redefinir la confianza y el no-match/tie-break en `deterministic.py` (TDD).
2. Ampliar `keywords.py` preservando la invariante (TDD + cobertura).
3. Ajustar el contrato en `schemas/clasificacion.py` y el escalamiento en `hybrid.py` (TDD).
4. Calibrar el umbral y fijarlo en `settings.py` segun OQ1/OQ3.
5. Subir `HYBRID_CACHE_VERSION` a `hybrid-v2`.
6. Re-medir offline y documentar; re-medir hibrido cuando haya cuota (OQ5).

Rollback: revertir el commit restaura la logica y `hybrid-v1`; sin migraciones ni pasos de datos.

## Open Questions

Las siguientes OQ las resuelve el autor (ver proposal.md). Ninguna bloquea la escritura de artefactos; cada una gatea una tarea de implementacion marcada en `tasks.md` §0:

- **OQ1**: piso de precision aceptable vs objetivo de cobertura (gatea D4 y §3).
- **OQ2**: no-match -> Gemini (recomendado) vs revision humana (gatea D1 y §1).
- **OQ3**: umbral fijo vs derivado del corpus (gatea D4).
- **OQ4**: `telefono` fuera de alcance (no gatea; documentado).
- **OQ5**: capturar baseline F1 Gemini/hibrido antes/despues (gatea la re-medicion hibrida, §4).
