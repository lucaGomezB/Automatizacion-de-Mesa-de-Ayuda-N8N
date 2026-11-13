# tesis-baseline-comparison Specification

## Purpose
Deja un borrador de seccion de resultados, en el estilo de `07-resultados.tex`, con la tabla
comparativa entre la linea de base clasica y el hibrido, para que el dueno de la tesis lo
integre. No edita ningun archivo de la tesis.

## Requirements

### Requirement: LB-201 — Borrador de seccion de resultados en el directorio de la change

El sistema SHALL producir un borrador Markdown en el directorio de la change con la estructura
y el tono de `07-resultados.tex`, que incluya la tabla comparativa completa y las notas
metodologicas necesarias para integrarla. El borrador MUST NOT editar, reemplazar ni escribir
ningun archivo `.tex` de la tesis. El borrador SHALL declarar que es un insumo para el dueno de
la tesis y que las cifras provienen de los artefactos de la medicion.

#### Scenario: Borrador en el directorio de la change

- **WHEN** se busca el borrador de la seccion
- **THEN** existe un archivo Markdown dentro del directorio de c-210
- **AND** contiene la tabla comparativa y las notas metodologicas

#### Scenario: Sin edicion de la tesis

- **WHEN** se revisa el repositorio despues de la medicion
- **THEN** ningun archivo `.tex` de la tesis fue modificado
- **AND** el borrador se identifica como insumo para integracion manual

### Requirement: LB-202 — Contenido minimo del borrador

El borrador SHALL incluir: el conjunto de prueba y su `n`; la procedencia de cada cifra; la
tabla con exactitud estricta, exactitud laxa, macro-F1, *balanced accuracy* y F1 por clase con
soporte para la linea de base y el hibrido; la lectura muestral y la ponderada a la prevalencia
natural; y el veredicto honesto sobre si la linea de base ayuda o perjudica el caso de la
tesis. El borrador SHALL declarar que no reemplaza ningun numero canonico.

#### Scenario: Tabla y procedencia en el borrador

- **WHEN** se lee el borrador
- **THEN** la tabla trae las cinco metricas y la F1 por clase con soporte para ambos sistemas
- **AND** cada cifra declara su archivo de procedencia

#### Scenario: Veredicto y advertencia aditiva

- **WHEN** se lee el cierre del borrador
- **THEN** declara si la linea de base ayuda o perjudica, con las cifras medidas
- **AND** declara que las cifras son aditivas y no reemplazan numeros canonicos

### Requirement: LB-203 — Honestidad y no inflacion

El borrador MUST NOT presentar una cifra unica como definitiva cuando existan lectura muestral
y ponderada. MUST NOT omitir un resultado desfavorable para la tesis. MUST NOT cambiar la
etiqueta de clase debil del hibrido (`Sistemas`) ni la de mejor clase (`Bases de Datos`), ni
atribuirselas a la linea de base. Si la linea de base queda por debajo del hibrido, el borrador
SHALL reportarlo con las cifras exactas.

#### Scenario: Resultado desfavorable reportado

- **WHEN** la linea de base queda por debajo del hibrido
- **THEN** el borrador lo declara con las cifras exactas y sin maquillaje
- **AND** no se cambia la conclusion metodologica para ocultarlo

#### Scenario: Dos lecturas y rotulos de clase

- **WHEN** se lee la tabla y las notas
- **THEN** figuran la lectura muestral y la ponderada, ambas rotuladas
- **AND** `Sistemas` y `Bases de Datos` conservan sus rotulos de debil y mejor clase del hibrido, sin transferencia a la linea de base
