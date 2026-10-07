# Design — c-74-calibracion-cortocircuito-determinista

## Context

Ver `proposal.md` — Why para la motivacion y la evidencia medida. Estado actual relevante:

- `DeterministicClassifier.classify` (`App/Backend/app/classifiers/deterministic.py`)
  calcula `_score` = cantidad de patrones distintos con match por sector. Con senal
  nula devuelve `sin_prediccion=True` y `sector_predicho=None`; con empate marca
  `ambiguo=True`. La `_confidence` (c-71 ASG-009) combina `min_matches`, `margin_ratio`
  y `sufficiency`, y devuelve 0.0 si `winner_score < min_matches`.
- `HybridClassifier.classify` (`App/Backend/app/classifiers/hybrid.py`) cortocircuita
  si `not sin_prediccion and not ambiguo and det_result.confianza >= deterministic_confidence_threshold`
  (`Settings.deterministic_confidence_threshold = 1.0`). Los disparadores
  `sin_prediccion`/`ambiguo` ya escalan con independencia del umbral.
- `Settings` expone `deterministic_confidence_threshold` (1.0), `deterministic_min_matches`
  (2) y `human_review_threshold` (0.70).
- `evaluation/deterministic_measurement.py` construye la curva precision/cobertura y
  elige el umbral con `elegir_umbral` sujeto a `PISO_PRECISION_DEFAULT = 0.90`
  (OQ1 de c-71). El resultado (umbral 1.0, cobertura 0.005) esta en
  `docs/deterministic_calibration.md`.
- `evaluation/README.md` §8.1 establece que el clasificador NO se ajusta sobre el
  corpus de evaluacion (anti data leakage); el corpus es el test reportado.
- Los cinco strings canonicos, `KEYWORD_MAP`, el prompt de Gemini y
  `evaluation/corpus.py::_a_float` estan LOCKED.

## Goals / Non-Goals

**Goals:**
- Sustituir la `confianza` ad-hoc como criterio de seleccion por un score calibrado de
  correctitud que SI separe predicciones correctas de incorrectas.
- Habilitar un cortocircuito con cobertura no trivial a un punto de operacion controlado.
- Preservar la integridad metodologica: el test reportado permanece intocado.
- Dejar la seleccion auditable y reproducible.

**Non-Goals:**
- No cambiar los cinco strings canonicos, `KEYWORD_MAP`, el prompt de Gemini ni
  `evaluation/corpus.py::_a_float`.
- No tocar los disparadores `sin_prediccion`/`ambiguo` ni su escalamiento (OQ5).
- No cambiar el esquema persistente ni la capa HTTP; no hay migracion.
- No introducir dependencias pagas en la calibracion; corre offline.

## Decisions

### D1: La senal de seleccion deja de ser la `confianza`

La evidencia (proposal.md) muestra que `confianza` es no monotona respecto de la
exactitud y que `min_matches >= 2` es contraproducente. La seleccion del cortocircuito
pasa a gobernarse por un score calibrado de correctitud. `confianza` se conserva como
medida de fuerza de senal reportada (ASG-009) pero NO como criterio. Alternativa
descartada: recalibrar el umbral de `confianza` sobre la misma formula — no puede
separar correctas de incorrectas porque la formula no mide correctitud.

### D2: Enfoque del score calibrado (OQ1)

El score mapea features deterministicas observables a P(correcta). Features candidatas:
score del ganador, score del runner-up, margen, cantidad de matches, longitud del texto,
relacion ganador/runner-up y senales por sector. Enfoques candidatos a evaluar por el
autor:

- **Seleccion / risk-controlled prediction**: elegir la accion (cortocircuitar o
  escalar) para controlar el riesgo (error) por encima de un nivel, sin un modelo de
  probabilidad explicito.
- **Regresion logistica** sobre las features: score parametrico, interpretable,
  probabilidad calibrada.
- **Isotonic regression**: calibracion no parametrica de un score base de senal.
- **Conformal prediction**: conjuntos/decisiones con garantia de cobertura del error
  a un nivel elegido, con calibracion out-of-fold.

El diseno NO elige por el autor: cada enfoque tiene costo, interpretabilidad y supuestos
distintos. La decision gatea la seccion 1 de `tasks.md` (OQ1).

**RESUELTO (autor, 2026-10-07):** Conformal / risk-controlled prediction, con calibracion
out-of-fold. Se usa un score de no-conformidad sobre las features deterministicas y se
elige el punto de operacion para controlar el error (precisión) al nivel objetivo, con
garantia de cobertura a nivel de muestra. Complementa (no sustituye) la procedencia de
OQ2 (cross-fitting).

### D3: Procedencia de los datos de calibracion (OQ2, anti-fuga)

El score NO puede ajustarse sobre el corpus de evaluacion, porque ese corpus es el test
reportado (README 8.1). Opciones a presentar al autor:

| Opcion | Que hace | Ventajas | Costos / riesgos |
|--------|----------|----------|------------------|
| (i) Held-out nuevo | Etiquetar un conjunto adicional, ajustar ahi | Test reportado intacto; sin supuestos de split | Requiere etiquetado nuevo; menor n de ajuste |
| (ii) Split dev/test pre-registrado | Particion fija y publicada del corpus; ajuste en dev, reporte en test | Reusa el corpus; reproducible | Reduce el n de test reportado; split debe pre-registrarse antes de mirar |
| (iii) Cross-fitting / conformal out-of-fold | Ajustar en folds que excluyen el fold evaluado | Aprovecha todo el corpus; garantia de cobertura | Mas complejo; supuestos de intercambiabilidad |

El diseno NO elige por el autor. La decision gatea la seccion 2 y determina como se
reportan las metricas.

**RESUELTO (autor, 2026-10-07):** (iii) Cross-fitting / conformal out-of-fold. La senal se
ajusta en folds que excluyen el fold evaluado; las metricas se reportan out-of-fold y el
test reportado (el corpus completo) nunca se usa para ajustar. Se documenta la
procedencia y la particion.

### D4: Punto de operacion explicito (OQ3)

El punto de operacion es una decision del autor: piso de precision y/o objetivo de
cobertura. Reemplaza/aumenta el piso 0.90 vigente (que hoy deja cobertura ~0.005). El
sistema elige el punto que maximiza el objetivo sujeto al piso, sobre datos de
calibracion, y lo reporta sobre el test intocado. Alternativa descartada: dejar 0.90
sin revisar, porque anula el atajo.

**RESUELTO (autor, 2026-10-07; REVISADO a criterio comparativo):** medido out-of-fold, ningun score alcanza un piso ABSOLUTO de 0.85 con cobertura util (techo ~6%, 12/200). Sin embargo, en el conjunto cortocircuitable el determinista (precision 0.740) supera a Gemini (0.679). Por eso el punto de operacion se define con un **piso COMPARATIVO**: maximizar cobertura sujeto a `precision_det(region) >= precision_gem(region)`, ambas estimadas out-of-fold con predicciones de Gemini cacheadas (sin invocar al proveedor). Sobre este corpus el criterio se cumple en todo el conjunto cortocircuitable, por lo que el punto de operacion equivale a cortocircuitar todo el conjunto con senal no ambigua. El test se reporta una sola vez con el punto ya fijado.

### D5: Destino de `deterministic_min_matches` (OQ4)

El conteo minimo de matches es contraproducente como gate de precision (match unico
0.7444 vs multi-match 0.7317). Opciones: mantener (retrocompatible), retirar, o
redefinir como feature del score (no como gate binario). Si se conserva, MUST NOT ser
el criterio de seleccion (ASG-011). Gatea la seccion 1/3 de `tasks.md`.

**RESUELTO (autor, 2026-10-07):** convertir `deterministic_min_matches` en **feature**
del score calibrado (no como gate binario). Se retira como criterio de seleccion; su
valor puede informar el score. ASG-011.

### D6: Disparadores de escalamiento intactos (OQ5)

`sin_prediccion` y `ambiguo` se mantienen como estan: escalan con independencia del
score. Este change solo modifica la condicion de cortocircuito con senal dominante.

### D7: Contrato de features y determinismo

El score se deriva solo de la descripcion y el vocabulario; no usa informacion no
disponible en runtime ni servicios externos. Debe ser deterministico. La logica vive
en los clasificadores (internos al backend); routes -> services -> repositories ->
models se respeta. Si la senal cambia el resultado, se sube `HYBRID_CACHE_VERSION`
para invalidar el cache de predicciones (C-34).

### D8: Calibracion offline y anti-fuga verificable

`evaluation/deterministic_measurement.py` gana la logica de calibracion con la
procedencia elegida en OQ2 y reporta la calidad sobre datos no usados para el ajuste.
`PISO_PRECISION_DEFAULT` se revisa segun OQ3. La calibracion MUST NOT invocar Gemini ni
tocar `_a_float`. Se agrega una verificacion de que el ajuste no lee el test reportado.

### D9: TDD y tests estructurales

Todo cambio de codigo con RED-GREEN-TRIANGULATE-REFACTOR y safety net por tarea. Tests
estructurales: strings canonicos intactos, `KEYWORD_MAP` intacto, `_a_float` intacto,
score acotado a [0,1], cortocircuito gobernado por el score, escalamiento por
`sin_prediccion`/`ambiguo` intacto.

### D10: Gobernanza

ALTO. La senal de confianza alimenta las metricas de la tesis y el punto de operacion es
decision del autor. Sin auth, sin esquema persistente, sin infraestructura.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|--------|------------|
| Tuning sobre el corpus de evaluacion (fuga) | Procedencia anti-fuga obligatoria (D3); verificacion de que el ajuste no lee el test |
| El punto de operacion baja cobertura y sube costo Gemini | Tradeoff explicito de OQ3; curva precision/cobertura documentada |
| El score no generaliza fuera de muestra | Validacion out-of-fold; reportar sobre datos no usados para ajustar |
| Features con informacion no disponible en runtime | Restriccion D7; solo descripcion + vocabulario |
| Cambio de senal desatribuye el delta de F1 | Bump de `HYBRID_CACHE_VERSION`; re-medicion explicita |
| Tocar strings canonicos, keywords, prompt o `_a_float` | Prohibido; tests estructurales lo verifican |

## Migration Plan

1. Resolver los gates OQ1..OQ4 (autor) antes de codificar (seccion 0 de `tasks.md`).
2. Definir el contrato de features y el score en `deterministic.py` (TDD).
3. Ajustar la seleccion en `hybrid.py` para consumir el score y el punto de operacion (TDD).
4. Exponer los parametros en `settings.py`; revisar/retirar `deterministic_min_matches`.
5. Implementar la calibracion con procedencia anti-fuga en `evaluation/` y reportar la
   calidad out-of-fold / sobre test intocado.
6. Subir `HYBRID_CACHE_VERSION` si la senal cambia resultados; re-medir la mezcla
   determinista/Gemini y su F1 sobre el corpus.
7. Documentar el punto de operacion y la procedencia en `docs/`.

Rollback: revertir el commit restaura el comportamiento de c-71/c-72 y la version de
cache anterior; sin migraciones ni pasos de datos.

## Open Questions

RESUELTAS por el autor el 2026-10-07 (las tareas gateadas ya pueden ejecutarse):

- **OQ1**: RESUELTA — Conformal / risk-controlled prediction (calibracion out-of-fold). Ver D2, §1.
- **OQ2**: RESUELTA — (iii) cross-fitting / conformal out-of-fold. Ver D3, §2.
- **OQ3**: RESUELTA (revisada) — piso COMPARATIVO: `precision_det(region) >= precision_gem(region)` estimado OOF, maximizando cobertura. Ver D4, §4.
- **OQ4**: RESUELTA — `deterministic_min_matches` pasa a ser feature del score (no gate). Ver D5, §1/§3.
- **OQ5**: CONFIRMADA — `sin_prediccion`/`ambiguo` se mantienen (restriccion, no decision abierta).
