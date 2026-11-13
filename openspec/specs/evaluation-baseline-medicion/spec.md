# evaluation-baseline-medicion Specification

## Purpose
Ejecuta la linea de base clasica de c-209 sobre los artefactos versionados y produce la
medicion reproducible con la comparacion contra el hibrido en el mismo conjunto de prueba,
lista para integrar en la tesis. Es una medicion aditiva: no cambia ningun numero canonico.

## Requirements

### Requirement: LB-101 — Ejecucion reproducible y artefactos versionados

El sistema SHALL ejecutar la linea de base sobre los artefactos versionados de c-209
(`corpus_campana.json` de `200` casos in-sample y `corpus_independiente.json` de `103` casos
con referencia) y SHALL escribir sus resultados en el directorio de la change: un JSON
autosuficiente, un resumen Markdown y un `SHA256SUMS.txt`. Dos ejecuciones consecutivas SHALL
producir los mismos bytes. El JSON SHALL registrar los SHA-256 de las entradas y de las
salidas. La ejecucion MUST NOT escribir fuera del directorio de la change ni modificar los
artefactos de entrada.

#### Scenario: Dos corridas identicas con hashes

- **WHEN** se ejecuta la medicion dos veces seguidas
- **THEN** el JSON, el Markdown y el `SHA256SUMS.txt` son identicos byte a byte
- **AND** los SHA-256 de las salidas coinciden entre corridas

#### Scenario: Solo escritura en el directorio de la change

- **WHEN** se ejecuta la medicion
- **THEN** los corpus, las predicciones y el clasificador de produccion quedan intactos
- **AND** solo se escriben los artefactos propios de la change

### Requirement: LB-102 — Comparacion con el hibrido en el mismo conjunto de prueba

El sistema SHALL reportar, en el mismo conjunto efectivo de `103` casos con referencia, las
cifras de la linea de base y las del hibrido congelado `hybrid-v3`. Las cifras del hibrido
SHALL tomarse de `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json` y
MUST NOT recalcularse, corregirse ni reinterpretarse. La comparacion SHALL incluir, para ambos
sistemas: exactitud estricta, exactitud laxa, macro-F1, *balanced accuracy* y F1 por clase con
soporte. El documento SHALL declarar que las cifras son aditivas y que no reemplazan ningun
valor canonico.

#### Scenario: Tabla comparativa en el mismo n

- **WHEN** se lee el documento de medicion
- **THEN** la tabla compara linea de base y hibrido sobre los mismos `103` casos
- **AND** cada sistema trae exactitud estricta, exactitud laxa, macro-F1, balanced accuracy y F1 por clase con soporte

#### Scenario: Cifras canonicas intactas

- **WHEN** se compara el documento nuevo con `analisis_fuera_de_muestra_c205.json`
- **THEN** las cifras del hibrido coinciden con el artefacto versionado
- **AND** no se modifica ningun valor canonico previo

### Requirement: LB-103 — Lectura muestral y lectura ponderada a la prevalencia natural

El sistema SHALL reportar las metricas de la linea de base en dos lecturas: (a) sobre la
muestra de `103` casos tal como esta, y (b) ponderadas a la prevalencia natural del corpus de
ajuste de `200` casos, cuando la variante del modelo use re-ponderacion de clases. Cada
lectura SHALL rotularse y SHALL declarar su procedencia. El documento MUST NOT presentar una
sola cifra que pueda leerse como inflada por la composicion de la muestra. Las variantes con y
sin re-ponderacion de clases SHALL reportarse por separado.

#### Scenario: Dos lecturas rotuladas

- **WHEN** se lee la tabla de metricas de la linea de base
- **THEN** figuran la lectura muestral y la lectura ponderada a la prevalencia natural
- **AND** cada lectura declara su procedencia y su rotulo

#### Scenario: Variantes con y sin re-ponderacion

- **WHEN** se lee el documento de medicion
- **THEN** figuran las metricas de la variante con re-ponderacion de clases y de la variante sin re-ponderacion
- **AND** se declara cual es la variante primaria y por que

### Requirement: LB-104 — Soporte por clase y clases debil y fuerte

El sistema SHALL reportar el soporte por clase de los `103` casos de prueba y SHALL mantener
separadas las observaciones del hibrido de las de la linea de base. La clase `Sistemas` es la
clase debil del hibrido (`F1 0.2222`, soporte `5`); `Bases de Datos` es la mejor clase del
hibrido (`F1 0.963`, soporte `13`). El documento SHALL reportar la F1 de la linea de base por
clase sin transferirle las etiquetas de debil/fuerte del hibrido.

#### Scenario: Soporte y clases del hibrido bien rotulados

- **WHEN** se lee la tabla comparativa
- **THEN** el soporte por clase figura y suma `103`
- **AND** `Sistemas` se identifica como clase debil del hibrido y `Bases de Datos` como su mejor clase, sin atribuirselo a la linea de base

#### Scenario: F1 de la linea de base por clase

- **WHEN** se leen las metricas por clase de la linea de base
- **THEN** cada clase trae su F1 y su soporte
- **AND** no se confunde la F1 de la linea de base con la del hibrido

### Requirement: LB-105 — Veredicto honesto y sin cambios canonicos

El documento SHALL declarar si la linea de base ayuda o perjudica el caso de la tesis, con las
cifras exactas medidas y sin maquillaje. Si la linea de base supera o iguala al hibrido, SHALL
decirlo; si queda por debajo, SHALL decirlo con las mismas cifras. MUST NOT cambiar, corregir
ni reinterpretar ningun numero canonico existente. MUST NOT editar archivos `.tex`,
`Bibliography_base.bib`, `CHANGES.md` ni changes ajenas.

#### Scenario: Veredicto con cifras exactas

- **WHEN** se lee el veredicto de la medicion
- **THEN** declara si la linea de base ayuda o perjudica, con las cifras medidas
- **AND** no se presenta un resultado desfavorable como favorable ni se omite

#### Scenario: Sin cambios canonicos ni de tesis

- **WHEN** se revisa el diff de la change
- **THEN** no figura ningun cambio en numeros canonicos, `.tex`, `Bibliography_base.bib`, `CHANGES.md` ni changes ajenas
- **AND** las cifras nuevas quedan en los artefactos de la change
