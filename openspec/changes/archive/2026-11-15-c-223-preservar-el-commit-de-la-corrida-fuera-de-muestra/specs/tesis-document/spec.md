## MODIFIED Requirements

### Requirement: Reproducibilidad declarada

La tesis SHALL declarar que la confianza de Gemini difirió entre las dos corridas fuera de muestra
en los casos comunes, con la cantidad registrada, y que el orden del prerregistro de la calibración
se demuestra con las fechas de autor de los commits. La documentación de la campaña SHALL registrar
que el `commit` declarado en `predicciones_independiente.json` no es alcanzable desde `main`, que se
preserva mediante el tag anotado `archivo/corrida-fuera-de-muestra-561b3c4` con su SHA completo, y
cuál commit versionó el archivo. La tesis SHALL declarar en el apartado metodológico del diseño
fuera de muestra que el árbol de fuentes de la corrida se preserva por ese tag y SHALL consignar el
SHA-256 de `predicciones_independiente.json` y de `reporte_independiente.md` tal como están
versionados. Si el tag no puede publicarse, la documentación y la tesis SHALL declarar la salvedad
de forma explícita, con el commit que versionó el archivo, y MUST NOT presentar la salvedad como
equivalente a la preservación. MUST NOT afirmar que ese commit no existe, MUST NOT afirmar que el
tag contiene los artefactos de salida si no los contiene, y MUST NOT presentar la preservación por
tag como alcanzabilidad desde `main`.

#### Scenario: Declaraciones presentes

- **WHEN** se leen la calibración de resultados y la metodología
- **THEN** figuran la variación entre corridas y la nota sobre las fechas de autor

#### Scenario: Commit de la primera corrida descrito por alcanzabilidad

- **WHEN** se lee el README de la campaña y la declaración metodológica sobre `predicciones_independiente.json`
- **THEN** dicen que el `commit` declarado no es alcanzable desde `main`, nombran el tag de archivo con su SHA completo y el commit que versionó el archivo
- **AND** la tesis consigna el SHA-256 de las predicciones y del reporte versionados
- **AND** no afirman que el commit no exista ni que el tag contenga los artefactos de salida

#### Scenario: Salvedad explícita si el tag no se publica

- **WHEN** el tag de archivo no se publica
- **THEN** el README y la tesis declaran la salvedad de forma explícita, con el commit que versionó el archivo y los SHA-256
- **AND** la salvedad no se presenta como equivalente a la preservación por tag
