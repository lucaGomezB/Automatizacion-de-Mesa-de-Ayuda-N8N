# Evaluación Experimental (extra — alimenta C-08)

Síntesis del marco metodológico (tesis §4) y resultados esperados (§7) para reproducir la evaluación.

## Diseño

- Cuasi experimental, muestras pareadas, mediciones repetidas; cada incidente procesado por flujo manual y automatizado.
- Contrabalanceo: corpus dividido en mitades; una procesada primero manual, la otra primero automatizada (mitiga efecto de aprendizaje).
- Observación naturalista (sin efecto Hawthorne): operadores no informados del cronometraje.
- **Anti data-leakage**: keywords y prompt se construyeron SIN acceso al corpus de validación; la evaluación sobre los 200 casos es estrictamente held-out.

## Corpus (Anexo F — CSV no versionado)

| Estrato | Casos | Proporción |
|---|---|---|
| Sistemas | 82 | 41 % |
| Operaciones | 64 | 32 % |
| Soporte Técnico | 54 | 27 % |
| **Total** | **200** | muestreo estratificado proporcional sobre ~3.700 incidentes/trimestre |

- Nivel de confianza 95 %, margen de error 6,5 %.
- Doble etiquetado independiente; Kappa de Cohen = 0,87; discrepancias resueltas por consenso.
- Columnas esperadas del CSV: id anónimo, descripción pseudonimizada, canal, categoría consenso, categoría predicha, tiempos por flujo, confianza.

## Métricas a calcular (C-08)

| Métrica | Herramienta | Valor esperado (tesis) |
|---|---|---|
| Exactitud global | scikit-learn | 92 % (184/200), IC Wilson 95 % [87,2 ; 95,2] |
| Matriz de confusión 3×3 | scikit-learn | Tabla 7 de la tesis |
| Precision/Recall/F1 por clase | scikit-learn | Sistemas 0,933 · Operaciones 0,906 · Soporte Técnico 0,917 (F1) |
| F1 macro | scikit-learn | 0,919 |
| Wilcoxon rangos con signo (tiempos pareados) | scipy.stats | W = 0, p < 0,001 |
| Tamaño del efecto rank-biserial | manual: r = 1 − 2W/(n(n+1)) | r = 1,00 |
| Tiempos descriptivos | pandas | manual x̄ 165,3 s (σ 38,7) vs auto x̄ 18,2 s (σ 4,1) |
| Intervención humana | agregación | 100 % → 9,5 % |
| Distribución por etapa | agregación | ~62 % deterministic / ~38 % gemini |

## Matriz de confusión esperada (Tabla 7)

| Real \ Predicho | Sistemas | Operaciones | Soporte Técnico | Total |
|---|---|---|---|---|
| Sistemas | **76** | 4 | 2 | 82 |
| Operaciones | 3 | **58** | 3 | 64 |
| Soporte Técnico | 2 | 2 | **50** | 54 |

## Tipología de errores (Tabla 9 — para análisis cualitativo)

1. Descripciones < 15 palabras (7 casos) — falta de contexto léxico.
2. Mezcla de categorías (6 casos) — p. ej. hardware que afecta una aplicación.
3. Jerga local / nombres internos (3 casos) — fuera del contexto del prompt.

## Entregables de C-08

- `evaluation/run_evaluation.py` — carga CSV, clasifica, recolecta resultados.
- `evaluation/report.md` — tablas de métricas.
- `evaluation/analysis.ipynb` — matriz de confusión, distribución de confianzas, curva de calibración.
- `evaluation/requirements.txt` — scikit-learn, scipy, pandas, matplotlib, seaborn.
- `evaluation/README.md` — procedimiento reproducible.

## Baseline de referencia (§8.3)

TF-IDF + SVM sobre subconjunto de 40 casos: exactitud 78 %, F1 macro 0,764 — el esquema híbrido aporta ganancia sustantiva sobre baseline trivial.
