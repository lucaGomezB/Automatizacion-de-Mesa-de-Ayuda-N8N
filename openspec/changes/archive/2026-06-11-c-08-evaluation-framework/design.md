## Context

La tesis (Capítulo 7) reporta dos familias de resultados sobre el corpus de 200 casos (§4.4): métricas de clasificación (§7.2: exactitud global 92%, matriz de confusión, F1 macro 0.919, IC de Wilson) y comparación de tiempos manual vs. automatizado (§7.1: Wilcoxon W=0, p<0.001, efecto rank-biserial 1.00). Hoy nada en el repositorio regenera esas tablas. C-08 construye el framework que las produce a partir del corpus.

Estado del clasificador (ya implementado, C-01..C-05): `HybridClassifier` (`Gestion_Incidentes/app/classifiers/hybrid.py`) orquesta dos etapas — `DeterministicClassifier` (reglas/regex, cortocircuita si confianza ≥ 0.90) y `GeminiClassifier` (Gemini 2.5 Flash, escala si la confianza determinística es baja, con fallback a confianza 0.0 si Gemini falla). `classify(descripcion)` es `async` y devuelve `ClasificacionResult(categoria, confianza, etapa, requiere_revision_humana, respuesta_raw)`. Las categorías válidas son exactamente `"Sistemas"`, `"Operaciones"`, `"Soporte Técnico"`. Umbrales en `Settings`: deterministic 0.90, human_review 0.70.

Restricciones duras verificadas:
- El corpus real `data/corpus_evaluacion_pseudonimizado.csv` (82 Sistemas / 64 Operaciones / 54 Soporte Técnico = 200) **no está en este clon** (`data/` no existe; CLAUDE.md: "not tracked in git"). El framework debe ser correcto y testeado sin él.
- Governance del dominio: **BAJO** (utilidad de evaluación, read-only sobre el sistema, no toca auth/billing/datos productivos) → autonomía completa si los tests pasan.
- Convenciones del proyecto: Python 3.12+ (clon corre 3.13), pytest async-mode auto, español rioplatense en código/docs, identificadores de dominio en español, TDD estricto, funciones puras para el cálculo separado de la I/O.

## Goals / Non-Goals

**Goals:**
- Calcular de forma **reproducible y testeada** las métricas del Capítulo 7 a partir del corpus.
- Definir el **contrato/esquema** del CSV del corpus a partir de §4.3-§4.4 de la tesis, validado en la carga.
- Implementar el cálculo de métricas como **funciones puras** (matriz de confusión, P/R/F1 por clase, F1 macro, exactitud, IC de Wilson) y el análisis de tiempos (Wilcoxon + rank-biserial) — todo testeable sin red ni I/O.
- Dejar la corrida real como **un solo comando** que el usuario ejecuta tras colocar el corpus verdadero.
- Documentar el procedimiento, el esquema y la decisión de invocación del clasificador.
- Aislar las dependencias pesadas (scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter) en `evaluation/requirements.txt`, sin tocar el runtime del backend.

**Non-Goals:**
- **NO** crear ni inventar un corpus de 200 casos "reales". Los números de la tesis salen del corpus verdadero; el fixture de tests es sintético y pequeño, marcado como tal.
- **NO** modificar el backend (`Gestion_Incidentes/app/`), su API, ni la lógica del clasificador.
- **NO** acoplar el evaluador a las rutas FastAPI ni levantar el servidor para evaluar.
- **NO** medir tiempos del flujo manual: esos datos provienen del protocolo observacional de la tesis (§4.2); el framework solo aporta la **prueba estadística** dados los pares de tiempos.
- **NO** versionar `report.md` con resultados reales en este change (su formato sí se documenta).

## Decisions

### D1. Cómo el evaluador invoca al clasificador: **import directo del `HybridClassifier`**, no HTTP al backend

El runner importa `HybridClassifier` y llama `await classifier.classify(descripcion)` directamente, en lugar de hacer `POST /api/v1/incidentes` contra el backend FastAPI.

- **Por qué import directo (elegido):**
  - **Reproducibilidad**: evita depender de un servidor corriendo, de la base PostgreSQL, de migraciones y del estado de la API. La evaluación es una función del corpus + el código del clasificador, no del despliegue.
  - **Aislamiento**: no contamina la base de datos productiva con 200 incidentes de evaluación ni dispara la notificación a N8N (C-02) ni la persistencia.
  - **Testabilidad / inyección**: el runner recibe el clasificador por parámetro, así los tests inyectan un `FakeClassifier` determinístico y **nunca pegan a Gemini** (regla python-testing). El cálculo de métricas queda separado de la invocación.
  - **Costo de API Gemini**: la corrida real solo invoca Gemini en los casos ambiguos (confianza determinística < 0.90; la tesis estima ~62% resuelto por reglas). Con import directo controlamos exactamente cuándo y cuántas llamadas se hacen, y podemos cachear/loggear etapa por caso. Vía HTTP el control es indirecto.
- **Alternativa descartada (HTTP al backend):** probaría el sistema "end-to-end" incluyendo serialización y rutas, pero introduce dependencia de entorno (servidor + DB), efectos secundarios (persistencia + webhook N8N) y hace la evaluación no reproducible offline. El end-to-end del workflow ya se cubre en C-04/C-05.
- **Trade-off asumido:** la evaluación mide el **clasificador**, no la capa HTTP. Es lo correcto para reproducir el Capítulo 7, que evalúa la calidad de clasificación, no la API.

### D2. Esquema del corpus CSV (derivado de §4.3-§4.4)

Columnas requeridas: `id`, `descripcion`, `categoria_real`. Columnas opcionales para §7.1: `tiempo_manual_s`, `tiempo_automatizado_s` (cuando estén presentes, habilitan el análisis de tiempos; si faltan, el runner omite esa sección sin fallar). `categoria_real` ∈ `{"Sistemas", "Operaciones", "Soporte Técnico"}` exacto y case-sensitive. La carga valida presencia de columnas y dominio de categorías, y falla con error claro ante cualquier desviación (nada silencioso). Decisión: usar pandas para la lectura (ya es dependencia del notebook) pero exponer la colección de casos como estructuras simples (dataclasses / dicts) hacia las funciones puras, para no acoplar el cálculo a pandas.

### D3. Métricas: implementación propia testeada + scikit-learn como cross-check

Las funciones de métricas (matriz de confusión, P/R/F1 por clase, F1 macro, exactitud) se implementan **a mano** como funciones puras sobre las tres clases fijas, porque (a) son triviales y auditables, (b) permiten TDD con asserts numéricos exactos, (c) evitan ambigüedad de configuración de `average=` y manejo de ceros de sklearn. scikit-learn se usa en el notebook y, opcionalmente, como verificación cruzada en un test (comparar nuestro resultado contra `sklearn.metrics` sobre el fixture). El IC de Wilson se implementa con la fórmula cerrada (o `statsmodels`/`scipy` si está disponible) — funciones puras testeadas contra valores de referencia. Manejo de denominador cero → 0.0 (definido en spec).

### D4. Estadística de tiempos con SciPy

`scipy.stats.wilcoxon` para la prueba de rangos con signo; el tamaño del efecto rank-biserial se calcula de la salida (`r = 1 − 2W/(n(n+1))`, consistente con §7.1). Se envuelve en una función pura `wilcoxon_tiempos(manual, automatizado) -> (W, p, r)` que valida longitudes iguales y delega en SciPy. Los tests inyectan series pequeñas con resultado conocido (p. ej. automatizado siempre menor → p<0.05, r alto) y verifican el rechazo de longitudes distintas.

### D5. Reporte y notebook separados del cálculo

`run_evaluation.py` produce `report.md` (texto/markdown con las tablas) reusando las funciones puras. `analysis.ipynb` consume resultados ya calculados (o el corpus) para las visualizaciones (matriz de confusión como heatmap, histograma de confianzas por etapa, curva de calibración confianza-vs-acierto). El notebook es no-TDD (verificación manual). Esto mantiene el cálculo testeable y la presentación desacoplada.

### D6. Dependencias aisladas

`evaluation/requirements.txt` con scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter. No se agregan al `requirements.txt` del backend para no inflar la imagen de runtime. El framework reusa el paquete `app` de `Gestion_Incidentes` vía import; el README documenta cómo configurar el `PYTHONPATH`/entorno para que el import del clasificador resuelva.

## Risks / Trade-offs

- **Corpus real ausente** → el runner no puede producir los números de tesis en este clon. Mitigación: tests corren contra fixture sintético versionado; el runner falla con mensaje claro pidiendo colocar el corpus; el README documenta el procedimiento de un comando. La validez de las métricas la garantizan los tests, no el corpus.
- **Costo y variabilidad de Gemini en la corrida real** → invocar el LLM en casos ambiguos cuesta tokens y es no-determinístico (aunque temperature=0.3). Mitigación: el runner registra etapa por caso (cuántos resolvió `deterministic` vs `gemini` vs `fallback`) y persiste las predicciones a un CSV/JSON intermedio para no re-invocar Gemini al regenerar el reporte o el notebook. Reproducibilidad parcial: los resultados de reglas son deterministas; los de Gemini se congelan en el artefacto intermedio.
- **Dependencia del entorno para importar `app`** → el evaluador necesita resolver `from app.classifiers.hybrid import HybridClassifier`. Mitigación: documentar en el README el setup (correr desde `Gestion_Incidentes/` en el `PYTHONPATH` o instalar el paquete); los tests del cálculo puro no dependen de ese import (inyectan `FakeClassifier`), así que la suite pasa aunque el entorno del backend no esté configurado.
- **Riesgo de data leakage conceptual** → la tesis (§8.1) enfatiza que el clasificador NO se ajustó sobre el corpus de 200. Mitigación: el framework solo **evalúa**, nunca ajusta reglas ni prompt a partir del corpus; el README lo deja explícito como advertencia metodológica.
- **Divergencia con sklearn en bordes (empates, clases vacías)** → implementación propia podría diferir. Mitigación: test de cross-check contra `sklearn.metrics` sobre el fixture y reglas explícitas de denominador-cero en la spec.

## Migration Plan

Aditivo, sin migración de datos ni rollback complejo. Para correr la evaluación real: (1) colocar el corpus verdadero en `data/corpus_evaluacion_pseudonimizado.csv`; (2) instalar `evaluation/requirements.txt` y configurar el entorno del backend (`GEMINI_API_KEY` operativa); (3) ejecutar el runner; (4) abrir el notebook para las visualizaciones. Rollback: borrar el paquete `evaluation/` (no afecta a nada más).

## Open Questions

- **Tiempos del flujo automatizado**: ¿se derivan de timestamps reales del backend durante la corrida (entrada→persistencia) o vienen pre-cargados en el CSV del corpus (columnas `tiempo_*_s`)? Decisión de diseño: soportar ambos — si el CSV trae las columnas de tiempo, se usan; si no, la sección §7.1 del reporte se omite con una nota. A confirmar con el usuario al colocar el corpus real.
- **Curva de calibración**: bineado de confianzas (cantidad de bins) a fijar en el notebook; no afecta al cálculo testeable de métricas.
