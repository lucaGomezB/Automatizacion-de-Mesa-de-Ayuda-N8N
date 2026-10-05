# Proposal: Endurecimiento del clasificador determinista (c-71)

## Why

La primera etapa del pipeline (filtro determinista) cortocircuita Gemini con una confianza que NO mide confiabilidad: el umbral 0.90 es degenerado y el vocabulario deja sin senal a la mayoria de los casos de Hardware/Software. Medido OFFLINE sobre los 200 casos de `data/corpus_evaluacion_pseudonimizado.json` (sin llamadas a Gemini):

| Evidencia | Valor |
|-----------|-------|
| Escalacion a Gemini (global) | 64% (correo 66.7%, web 73.6%, telefono 55.6%) |
| Exactitud estricta de los cortocircuitados (conf >= 0.90) | 0.51 (correo 0.59, web 0.50, telefono 0.47) |
| Pertenencia multietiqueta de los cortocircuitados | 0.76 |
| Cortocircuitados con confianza EXACTAMENTE 1.0 | 100% |
| Sobre-prediccion de "Seguridad Informatica" | 126 (real: 31) |
| Verdad: Hardware 85, Software 67, Seguridad 31, Sistemas 16, BD 1 | — |

Causas raiz: (1) la formula `winner/(winner+second+eps)` da 1.0 solo cuando UN sector matchea algun keyword, y <=0.5 si matchea un segundo; el "umbral" es en realidad un binario "un solo sector matcheo". (2) Sin ningun match, `classify` devuelve la primera clave del dict ("Seguridad Informatica") con confianza 0.0: un sesgo arbitrario, no una prediccion. (3) El `KEYWORD_MAP` (89 patrones) sub-cubre Hardware/Software. La etapa determinista es hoy un cuello de botella riesgoso, no el filtro barato confiable que el Anexo H asume.

> Nota: la linea base de F1 de Gemini/hibrido NO fue medida (no hay `evaluation/predicciones.json`; Gemini esta limitado por 429). Queda PENDIENTE (OQ5).

## What Changes

- **No-match y empate**: con senal nula, el clasificador determinista MUST devolver un estado explicito de "sin prediccion" (NO un sector arbitrario); con puntajes empatados, MUST marcar ambiguedad. Ambos casos escalan el pipeline.
- **Vocabulario**: ampliar sinonimos/frases por sector guiado por las misclasificaciones del corpus, elevando cobertura de Hardware/Software; preservar `set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)`.
- **Confianza y umbral**: redefinir la medida de confianza (conteo minimo de matches + margen sobre el segundo) y recalibrar el cortocircuito con una curva precision/cobertura derivada del corpus, con un piso de precision objetivo.
- **Re-medicion**: subir `HYBRID_CACHE_VERSION` (`hybrid-v1` -> `hybrid-v2`) e invalidar el cache; re-medir F1 determinista vs hibrido sobre el corpus y documentar el delta.
- **Tests**: TDD estricto (RED-GREEN-TRIANGULATE-REFACTOR) + tests estructurales actualizados.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sector-taxonomy`: se amplia el vocabulario del clasificador determinista (TAX-002) y se agrega la cobertura medida del mismo.
- `sector-assignment`: se agrega el estado explicito de ausencia de prediccion, la ambiguedad por empate y la confianza con conteo minimo y margen.
- `classification-resilience`: se recalibra la decision de cortocircuito y el escalamiento, y el fallback se ajusta para no fabricar un sector cuando no hubo estimacion determinista.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/classifiers/deterministic.py` | Modified | No-match/tie-break, confianza con conteo+margin |
| `App/Backend/app/classifiers/keywords.py` | Modified | Vocabulario ampliado (invariante intacto) |
| `App/Backend/app/classifiers/hybrid.py` | Modified | Escalamiento ante sin-prediccion/ambiguedad; cortocircuito calibrado |
| `App/Backend/app/schemas/clasificacion.py` | Modified | Contrato de resultado (estado sin prediccion/ambiguo) |
| `App/Backend/app/constants.py` | Modified | `HYBRID_CACHE_VERSION` -> `hybrid-v2` |
| `App/Backend/app/config/settings.py` | Modified | Umbral y parametros de calibracion |
| `App/Backend/tests/test_deterministic_classifier.py`, `test_hybrid_classifier.py` | Modified/New | TDD y estructurales |
| `evaluation/` | Modified | Camino de medicion determinista + re-medicion |
| `docs/` (parametros/Anexo H) | Modified | Documentar la calibracion y el delta |

## Governance

MEDIO. Cambia resultados de clasificacion que alimentan la evaluacion de la tesis (puede afectar F1). No toca auth, esquema persistente ni infraestructura; el impacto es sobre calidad de clasificacion y metricas. Las decisiones de calibracion (OQ1) las resuelve el autor.

## Open Questions (autor)

- **OQ1**: piso de precision aceptable del cortocircuito vs objetivo de cobertura (que fraccion del corpus puede cortocircuitar sin Gemini).
- **OQ2**: ante no-match, escalar SIEMPRE a Gemini (recomendado) vs derivar directo a revision humana.
- **OQ3**: el umbral queda como setting fijo vs se vuelve derivado del corpus (recalculado por corrida).
- **OQ4**: unificar `telefono` a la cascada queda FUERA DE ALCANCE (el canal pasa por el AI Agent de n8n y usa clasificacion precalculada); si se quiere, change aparte.
- **OQ5**: capturar primero la linea base de F1 Gemini/hibrido cuando se restaure la cuota (la clave la administra un colega).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Recalibrar baja la cobertura del cortocircuito y sube el costo Gemini | Med | La curva precision/cobertura elige el umbral con OQ1; documentar el tradeoff |
| Ampliar vocabulario introduce falsos positivos | Med | Triangulacion por sector + medir precision sobre el corpus, no solo cobertura |
| Cambiar el contrato de resultado rompe consumidores | Med | Estado aditivo con default seguro; tests de contrato y API |
| Delta de F1 no atribuible (cache/sin baseline Gemini) | Med | Version de cache bump + baseline explicito (OQ5) |
| Tocar `_a_float` o los strings canonicos | Baja | Prohibido por constraints; tests estructurales lo verifican |

## Rollback Plan

Revertir el commit restaura `deterministic.py`, `keywords.py`, `hybrid.py`, schemas y `HYBRID_CACHE_VERSION` a `hybrid-v1`; el cache de evaluacion previo vuelve a ser valido. Sin migraciones ni cambios de esquema persistente: el rollback es puramente de codigo y no requiere pasos de datos.

## Dependencies

- `C-27` (sector-taxonomy/sector-assignment, archivado): vocabulario canonico y contrato multietiqueta que este change extiende.
- `C-34`/`C-58` (evaluacion/cache y resiliencia Gemini): runner y `HYBRID_CACHE_VERSION`.
- Corpus `data/corpus_evaluacion_pseudonimizado.json` (200 casos, no trackeado).

## Success Criteria

- [ ] Con senal nula, el determinista no emite un sector arbitrario y el pipeline escala; con empate, marca ambiguedad y escala.
- [ ] La cobertura del vocabulario sobre el corpus sube y la tasa de no-match baja, sin degradar precision por sector.
- [ ] La confianza deja de ser degenerada (no 100% en 1.0) y el umbral se justifica con una curva precision/cobertura y un piso de precision (OQ1).
- [ ] `HYBRID_CACHE_VERSION` = `hybrid-v2` y el cache previo queda invalidado.
- [ ] Delta de F1 determinista vs hibrido documentado (o baseline pendiente declarado, OQ5).
- [ ] `openspec validate c-71-hardening-clasificador-determinista --strict` pasa; tests TDD y estructurales en verde.
