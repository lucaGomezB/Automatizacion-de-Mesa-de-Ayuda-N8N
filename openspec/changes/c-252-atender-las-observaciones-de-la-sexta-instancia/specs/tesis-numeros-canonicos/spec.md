## ADDED Requirements

### Requirement: Extensión media de descripciones por canal y régimen (D-04 de c-252)

El registro canónico SHALL incorporar el estadístico descriptivo de la **extensión media de las
descripciones** (en palabras y en caracteres) desagregado por canal (`correo electrónico`, `formulario web`,
`llamada telefónica`) y por régimen ((a) = correo+formulario, 119 casos; (b) = telefonía, 81 casos),
computado del campo `descripcion` de `data/corpus_evaluacion_pseudonimizado.json` mediante un script de
análisis versionado con su prueba automatizada. La prosa de §4.4 y §4.8 SHALL citar estas extensiones
para sostener la explicación de por qué leer una descripción completa (87,2 s manual) no es comparable a
recitar su paráfrasis (7,26 s), y SHALL separar la parte de **lectura** de la parte de **decisión** de los
87,2 s manuales. Las cifras SHALL provenir de la salida versionada del script y MUST NOT copiarse del
dictamen.

#### Scenario: Script generador con prueba automatizada

- **WHEN** se ejecuta `pytest evaluation/data/campana/analisis/test_analisis_sexta_instancia_c252.py` y luego el script `analisis_sexta_instancia_c252.py`
- **THEN** la prueba pasa y el JSON de salida contiene la extensión media (palabras y caracteres) por canal y por régimen

#### Scenario: Cifras coherentes con el registro y la prosa

- **WHEN** se leen §4.4 y §4.8 (`04-marco-metodologico.tex`) y se contrastan con `analisis_sexta_instancia_c252.json`
- **THEN** la extensión media por canal y por régimen coincide con la salida versionada, y el texto separa lectura de decisión en los 87,2 s manuales

#### Scenario: Entrada congelada, sin editar el corpus

- **WHEN** se ejecuta `sha256sum data/corpus_evaluacion_pseudonimizado.json`
- **THEN** el hash coincide con el registrado en la línea base (el corpus no se editó)

### Requirement: Cifra primaria de la sub-hipótesis 1 determinada (D-02 de c-252)

El registro canónico SHALL fijar la cifra primaria de la sub-hipótesis 1 de tiempo en **71,2 %** (OQ-2
resuelta: el componente de carga nunca se sumó, la v1.6.4 estaba mal descrita), y SHALL mantener coherente el
bloque del rango de robustez de tiempos con esa decisión. El `-10 s` del Anexo de sensibilidad SHALL quedar
etiquetado como el escenario adverso que el tribunal (C-02) pidió cuantificar cuando la descripción de la tarea
manual aún incluía la carga ~10 s, sin contradicción con el requisito "Componente '~10 s de carga del ticket'
retirado" de c-250 ni con la re-etiqueta pendiente del change c-251: la etiqueta final SHALL registrarse una
única vez en la memo canónica con su justificación, resolviendo la contradicción entre "sensibilidad de
redondeo" (c-250) e "herencia del componente de carga retirado" (c-251).

#### Scenario: Cifra primaria coherente con OQ-2

- **WHEN** se lee la sección del rango de robustez de tiempos del registro canónico (`numeros-canonicos.md`)
- **THEN** la cifra primaria queda fijada en 71,2 % (no 65,6 %) y es coherente con "sin componente de carga" (nunca se sumó)

#### Scenario: Etiqueta del `-10 s` resuelta sin contradicción

- **WHEN** se ejecuta `rg -n "redondeo|carga|10 s" docs/Tesis/Correcciones/numeros-canonicos.md` en el bloque de sensibilidad
- **THEN** el `-10 s` queda etiquetado una única vez con su justificación, y no persisten dos lecturas contradictorias (sensibilidad de redondeo vs herencia del componente de carga)