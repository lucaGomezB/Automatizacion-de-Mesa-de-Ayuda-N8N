# Borrador — Linea de base clasica (insumo para la seccion de resultados)

> **Insumo para el dueno de la tesis.** Este archivo es un BORRADOR en Markdown. NO se edito
> ningun `.tex`, ni `Bibliography_base.bib`, ni el memo canonico de numeros. Su contenido esta
> listo para integrarse en `07-resultados.tex` (seccion de comparacion de clasificacion) con las
> adaptaciones de formato que correspondan.
>
> Todas las cifras son ADITIVAS: no reemplazan ningun numero canonico de la tesis ni el
> clasificador de produccion. Proceden de los artefactos versionados
> `evaluation/data/campana/analisis/linea_de_base_clasica_c210.json` (linea de base) y
> `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json` (hibrido `hybrid-v3`,
> cifras LEIDAS, no recalculadas).

## 1. Motivacion

El dictamen CONEAU v1.3.0 califico el criterio 4 (metodologia, peso 20) con 7/10 y enumero
entre las limitaciones la ausencia de una linea de base: "Sin linea de base. No hay
comparacion con el modelo de lenguaje solo ni con un clasificador supervisado clasico." Este
apartado agrega la comparacion con un clasificador supervisado clasico de texto, reproducible
y offline, evaluado sobre el MISMO conjunto fuera de muestra que el sistema propuesto.

## 2. Metodo

Se entreno un clasificador supervisado clasico de texto con los 200 casos in-sample del corpus
de ajuste (verdad = `sector_asignado`). El modelo es una union de TF-IDF de palabras
(`ngram_range=(1,2)`, `sublinear_tf=True`) y de caracteres (`ngram_range=(2,5)`,
`sublinear_tf=True`) seguida de una regresion logistica regularizada
(`solver="lbfgs"`, `max_iter=2000`, semilla fija 42). Se reportan dos variantes: la primaria
con re-ponderacion de clases (`class_weight="balanced"`), motivada por el fuerte desbalance del
corpus de ajuste, y una variante de sensibilidad sin re-ponderacion (`class_weight=None`).

La evaluacion se hizo sobre los 103 casos fuera de muestra con referencia por consenso E3/E4,
el mismo n efectivo de los analisis de c-191 y c-205. Los 47 casos discordantes quedan fuera de
la referencia y NO se usan; el n de prueba no se extrapola al 150. Las metricas se calcularon
con las mismas funciones puras (`evaluation/metrics.py`) que usa el analisis del hibrido, de
modo que las cifras son comparables. El entrenamiento y la prediccion son deterministicos
(semilla fija) y no usan red, Gemini ni API paga.

## 3. Comparacion sobre el mismo n efectivo (103 casos)

### 3.1 Metricas globales

| Sistema | Exactitud estricta | Exactitud laxa | Macro-F1 | Balanced accuracy |
|---|---|---|---|---|
| Linea de base (balanceada) | 0,6505 (67/103) | 0,6699 (69/103) | 0,4877 | 0,5271 |
| Linea de base (sin re-ponderacion) | 0,5825 (60/103) | 0,6019 (62/103) | 0,3431 | 0,3838 |
| Hibrido `hybrid-v3` (c-205) | 0,8447 (87/103) | 0,8738 (90/103) | 0,7447 | 0,7395 |

*Fuente:* linea de base, `linea_de_base_clasica_c210.json`; hibrido,
`analisis_fuera_de_muestra_c205.json`. La exactitud estricta del hibrido coincide con el ancla
de c-191/c-205; no se recalculo.

### 3.2 F1 por clase con soporte

Linea de base (balanceada):

| Sector | Precision | Sensibilidad | F1 | Soporte |
|---|---|---|---|---|
| Seguridad Informatica | 0,5000 | 0,6190 | 0,5532 | 21 |
| Soporte Tecnico Hardware | 0,7857 | 0,8250 | 0,8049 | 40 |
| Soporte Tecnico Software | 0,6552 | 0,7917 | 0,7170 | 24 |
| Bases de Datos | 0,0000 | 0,0000 | 0,0000 | 13 |
| Sistemas | 0,3333 | 0,4000 | 0,3636 | 5 |

Hibrido `hybrid-v3` (c-205):

| Sector | Precision | Sensibilidad | F1 | Soporte |
|---|---|---|---|---|
| Seguridad Informatica | 1,0000 | 0,7143 | 0,8333 | 21 |
| Soporte Tecnico Hardware | 0,8636 | 0,9500 | 0,9048 | 40 |
| Soporte Tecnico Software | 0,7692 | 0,8333 | 0,8000 | 24 |
| Bases de Datos | 0,9286 | 1,0000 | 0,9630 | 13 |
| Sistemas | 0,2500 | 0,2000 | 0,2222 | 5 |

El soporte de los 103 casos es 40/24/21/13/5 (Hardware, Software, Seguridad, Bases de Datos,
Sistemas). La clase debil del HIBRIDO es `Sistemas` (F1 0,2222, soporte 5) y su mejor clase es
`Bases de Datos` (F1 0,963, soporte 13); esos rotulos se mantienen atados al hibrido y NO se
transfieren a la linea de base.

### 3.3 Lectura muestral y lectura ponderada

La lectura muestral usa los 103 casos tal como estan. La lectura ponderada es una
post-estratificacion a la prevalencia natural del corpus de ajuste (85 hardware, 67 software,
31 seguridad, 16 sistemas, 1 base de datos) y NO es una medicion nueva:

| Sistema | Macro-F1 muestral | Macro-F1 ponderado | Balanced accuracy muestral | Balanced accuracy ponderada |
|---|---|---|---|---|
| Linea de base (balanceada) | 0,4877 | 0,6971 | 0,5271 | 0,7438 |
| Linea de base (sin re-ponderacion) | 0,3431 | 0,5743 | 0,3838 | 0,6747 |

## 4. Veredicto honesto

La linea de base clasica queda POR DEBAJO del hibrido en las cuatro metricas globales. La
variante balanceada obtiene 0,6505 de exactitud estricta frente a 0,8447 del hibrido (diferencia
de -0,1942); la variante sin re-ponderacion obtiene 0,5825. El resultado es desfavorable a la
linea de base y se reporta sin maquillaje.

El hallazgo es informativo para la tesis: (a) el sistema propuesto supera a un clasificador
supervisado clasico razonable sobre el mismo conjunto; (b) la clase `Bases de Datos`, con un
unico caso de ajuste, cae a F1 0,0 en la linea de base, lo que evidencia la dependencia del
enfoque clasico de la disponibilidad de ejemplos por clase; (c) la re-ponderacion de clases
mejora la exactitud de la linea de base (0,6505 frente a 0,5825) pero no alcanza al hibrido.

## 5. Notas metodologicas y de procedencia

- Modelo, semilla y variantes: `evaluation/linea_de_base.py` (c-209), semilla fija 42.
- Artefacto unico de las cifras de la linea de base:
  `evaluation/data/campana/analisis/linea_de_base_clasica_c210.json` (LF, UTF-8 sin BOM).
- Comando de reproduccion: `python3 -m evaluation.linea_de_base --salida <directorio>`.
- Cifras del hibrido: `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json`
  (se LEEN; no se recalculan).
- Determinismo: dos corridas producen artefactos identicos byte a byte
  (SHA-256 `2866dc1c09bbc2054c088766da79bf8b90b38066d0db0e044fe980eebd50c1de` para el JSON y
  `f3e965590c060e844d722ba3409afc1fb19fb05c064a25f7729c0a38db4294bd` para el Markdown).
- Sin red, sin Gemini y sin API paga. Sin dependencias nuevas.
- Cifras aditivas: no reemplazan ningun valor canonico de la tesis. El n de prueba es 103; los
  47 discordantes sin referencia no se usan.
