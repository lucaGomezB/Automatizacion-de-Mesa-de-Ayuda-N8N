# evaluation-baseline-paired-contrast Specification

## Purpose
TBD - created by archiving change c-213-integrar-la-linea-de-base-en-la-tesis. Update Purpose after archive.

## Requirements

### Requirement: LBP-01 — Contraste pareado sobre los mismos casos

El sistema SHALL calcular, sobre los mismos casos fuera de muestra con referencia por consenso, la tabla 2×2 de aciertos estrictos entre el híbrido congelado y cada variante de la línea de base clásica (ambos aciertan, solo el híbrido, solo la línea de base, ninguno), el contraste de McNemar con `p` exacta bilateral y `p` corregida por continuidad mediante `evaluation/stats.py::contraste_mcnemar`, y la diferencia de exactitudes pareadas con un intervalo de confianza del 95 % por bootstrap percentil pareado con semilla fija. Los casos MUST emparejarse por `caso_id`; el script MUST abortar si algún caso no tiene predicción en ambos sistemas.

#### Scenario: Tabla 2×2 y McNemar con discordancias

- **WHEN** se ejecuta el contraste sobre secuencias pareadas con discordancias
- **THEN** la tabla 2×2 suma el número de casos
- **AND** el resultado incluye `p` exacta, `p` corregida y la diferencia `(b − c)/n` con su intervalo

#### Scenario: Sin discordancias

- **WHEN** ambos sistemas aciertan y fallan exactamente en los mismos casos
- **THEN** el contraste se marca como no aplicable y no se informa ningún valor `p`

#### Scenario: Caso sin pareja

- **WHEN** un `caso_id` de la referencia no aparece en las predicciones de uno de los sistemas
- **THEN** el script termina con error y no escribe artefactos

### Requirement: LBP-02 — Predicciones por caso versionadas y anclas verificadas

El sistema SHALL reconstruir las predicciones por caso de la línea de base con `evaluation.linea_de_base.predecir` (semilla 42, sin modificar el módulo) y leer las del híbrido de `evaluation/data/campana/predicciones_independiente.json`. Antes de escribir, MUST verificar que los aciertos reconstruidos coincidan con los agregados versionados (línea de base balanceada 67/103 y sin re-ponderación 60/103 de `linea_de_base_clasica_c210.json`; híbrido 87/103 de `analisis_fuera_de_muestra_c205.json`) y abortar si alguno difiere. El artefacto SHALL incluir, por caso, la referencia, la predicción de cada sistema y su acierto estricto, y los SHA-256 de todas las entradas.

#### Scenario: Anclas reproducidas

- **WHEN** las predicciones reconstruidas reproducen los agregados versionados
- **THEN** se escribe el artefacto con las predicciones por caso y el contraste

#### Scenario: Ancla no reproducida

- **WHEN** los aciertos reconstruidos de alguna variante difieren del agregado versionado
- **THEN** el script termina con error, informa la diferencia y no escribe artefactos

### Requirement: LBP-03 — Determinismo, solo lectura y carácter aditivo

El script SHALL ser determinista (dos corridas producen JSON y MD idénticos byte a byte, LF, UTF-8 sin BOM, con `SHA256SUMS`), MUST NOT modificar ningún insumo, MUST NOT usar red, Gemini ni API paga, y su artefacto SHALL declarar que es aditivo y no reemplaza ningún número canónico. La ruta de la referencia y el `n` esperado SHALL ser parámetros, para repetir el contraste sobre el conjunto arbitrado de c-206 sin cambiar el código.

#### Scenario: Dos corridas idénticas

- **WHEN** se ejecuta el script dos veces sobre los mismos insumos
- **THEN** los SHA-256 de las salidas coinciden
- **AND** los SHA-256 de los insumos no cambian

#### Scenario: Referencia alternativa

- **WHEN** se pasa otra ruta de referencia y otro `n` esperado
- **THEN** el contraste se calcula sobre esa referencia sin editar el código
