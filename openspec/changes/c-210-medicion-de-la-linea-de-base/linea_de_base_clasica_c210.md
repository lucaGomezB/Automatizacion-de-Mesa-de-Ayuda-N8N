# Linea de base clasica (c-210)

TF-IDF (palabras y caracteres) + regresion logistica regularizada de scikit-learn. Reutiliza `evaluation/metrics.py`. Sin red, sin Gemini, sin API paga. Deterministico.

## Conjunto de evaluacion

- Entrenamiento: 200 casos in-sample (verdad = sector_asignado).
- Prueba: 103 casos fuera de muestra con referencia E3/E4 (n efectivo declarado 103).
- Discordantes excluidos: 47 de 150; no se usan ni se reinterpretan.

## Metricas muestrales (n = 103)

| Sistema | Exactitud estricta | Exactitud laxa | Macro-F1 | Balanced accuracy |
|---|---|---|---|---|
| Linea de base (balanceada) | 0.6505 | 0.6699 | 0.4877 | 0.5271 |
| Linea de base (sin re-ponderacion) | 0.5825 | 0.6019 | 0.3431 | 0.3838 |
| Hibrido hybrid-v3 (c-205) | 0.8447 | 0.8738 | 0.7447 | 0.7395 |

## F1 por clase con soporte

Linea de base (balanceada):

| Sector | Precision | Sensibilidad | F1 | Soporte |
|---|---|---|---|---|
| Seguridad Informatica | 0.5000 | 0.6190 | 0.5532 | 21 |
| Soporte Tecnico Hardware | 0.7857 | 0.8250 | 0.8049 | 40 |
| Soporte Tecnico Software | 0.6552 | 0.7917 | 0.7170 | 24 |
| Bases de Datos | 0.0000 | 0.0000 | 0.0000 | 13 |
| Sistemas | 0.3333 | 0.4000 | 0.3636 | 5 |

Hibrido hybrid-v3 (c-205):

| Sector | Precision | Sensibilidad | F1 | Soporte |
|---|---|---|---|---|
| Seguridad Informatica | 1.0000 | 0.7143 | 0.8333 | 21 |
| Soporte Tecnico Hardware | 0.8636 | 0.9500 | 0.9048 | 40 |
| Soporte Tecnico Software | 0.7692 | 0.8333 | 0.8000 | 24 |
| Bases de Datos | 0.9286 | 1.0000 | 0.9630 | 13 |
| Sistemas | 0.2500 | 0.2000 | 0.2222 | 5 |

## Lectura ponderada a la prevalencia natural (linea de base balanceada)

- Rotulo: post-estratificacion a la prevalencia natural de los 200 casos in-sample; no es una medicion nueva.
- Procedencia: distribucion de sector_asignado de corpus_campana.json.
- Macro-F1 ponderado: 0.6971; balanced accuracy ponderada: 0.7438.

## Veredicto

- La linea de base balanceada queda por debajo del hibrido en exactitud estricta.
- Exactitud estricta: linea de base (balanceada) 0.6505; hibrido 0.8447; diferencia -0.1942.
- Sin re-ponderacion: 0.5825.
- Veredicto honesto y sin maquillaje: se reportan las dos variantes de la linea de base y se declara el resultado tal como se mide, sea favorable o desfavorable.

## Declaracion aditiva

- Las cifras de esta medicion son aditivas: no reemplazan ningun numero canonico de la tesis ni el clasificador de produccion. El n de prueba es el efectivo 103; los 47 discordantes sin referencia no se usan y no se extrapola al 150.

