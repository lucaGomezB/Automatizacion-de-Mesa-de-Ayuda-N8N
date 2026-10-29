# Design: Analisis de la campana y fiabilidad entre etiquetadores

## Context

Ver `proposal.md` - Why. El framework ya expone `intervalo_wilson`, `intervalos_por_clase`,
`intervalos_conjunto` y bootstrap con semilla en `evaluation/metrics.py`, y Wilcoxon/Shapiro/
rank-biserial/dz/McNemar en `evaluation/stats.py`. NO existe funcion de kappa (Cohen, Fleiss,
Landis-Koch) en el repositorio. Los tests viven en `evaluation/tests/` y corren offline con
fixtures; el corpus real y los datasets de campana NO estan en el repo.

## Goals / Non-Goals

- **Goals**: cinco funciones de analisis puras, un CLI fino de lectura, tests offline, kappa con IC.
- **Non-Goals**: ejecutar la campana, generar los datasets, editar la tesis, agregar dependencias nuevas, cambiar el runner de evaluacion existente.

## Decisions

- **D1 — Ubicacion: nuevo modulo `evaluation/campana.py` (analisis) y `evaluation/kappa.py`.** Alternativa: todo en `metrics.py`. Se opta por separar para no engordar `metrics.py` (ya 700+ lineas) y mantener imports claros; `stats.py` queda para contraste de tiempos. El CLI `evaluation/analisis_campana.py` solo hace I/O de lectura y delega en funciones puras.
- **D2 — Reutilizacion: NO reimplementar.** Exactitudes y Wilson vienen de `metrics.py`; el contraste de orden usa `stats.wilcoxon_tiempos_detallado` + `tamano_efecto_dz`; out-of-sample usa `run_evaluation`/metricas existentes con la ruta del corpus independiente. Solo kappa es codigo nuevo.
- **D3 — Kappa: Cohen (1960) con dos IC.** IC1 por bootstrap percentil con semilla fija y numero de remuestreos constante (mismo patron que `intervalos_por_clase`); IC2 asintotico por varianza de Fleiss. Se reportan ambos; si el denominador es indeterminado (`pe == 1`) se declara no estimable. Etiqueta interpretativa Landis-Koch como funcion pura separada, sin fijar el valor 0,87 (numero canonico de la tesis).
- **D4 — Contrato de entrada: registros ya cargados (listas/dicts), no rutas.** Las funciones reciben `Sequence[dict]` con claves documentadas (`id_corpus`, `etiquetador`, `sector`, etc.); el CLI valida y carga CSV/JSON. Esto mantiene pureza y testabilidad sin I/O.
- **D5 — Efecto de orden: contraste pareado por posicion** (primera vs segunda mitad) cuando hay pares; si no, se reporta `no_aplicable`. Alternativa: termino de orden en modelo mixto; se descarta por no sumar dependencias (statsmodels) y por el tamano muestral.
- **D6 — TDD estricto**: por cada requisito, test que falla primero sobre fixture sintetico, luego implementacion minima, triangulacion con un segundo caso y refactor. Semillas fijas para determinismo.
- **D7 — Coordinacion**: c-165/c-166 agregaron requisitos a `evaluation-campaign-instrumentation` (instrumento y diseño). c-167 AGREGA requisitos a `evaluation-framework` porque gobierna `metrics.py`/`stats.py` y el analisis consume, no produce, los datasets. Al archivar c-167 debe aplicarse despues de c-165/c-166 para que los datasets existan en la narrativa.

## Risks / Trade-offs

- Kappa con n chico produce IC ancho → reportar ambos metodos y declarar la limitacion.
- Bootstrap costoso en datasets grandes → remuestreos acotados y semilla fija.
- Divergencia entre CSV de campo y contrato de entrada → validacion explicita con error accionable en el CLI.
- Duplicar definiciones de exactitud → prohibido: importar de `metrics.py` (test de consistencia).

## Migration Plan

1. Agregar `kappa.py` y `campana.py` con sus tests (sin tocar codigo existente).
2. Agregar el CLI de lectura y un fixture sintetico en `evaluation/tests/fixtures/`.
3. Rollback: eliminar los archivos nuevos; nada existente se modifica.

## Open Questions

- Formato exacto del CSV de campo (c-165) y del dataset de doble etiquetado (c-168): se resuelve al implementar, sin cambiar el contrato de funciones ni los specs.
