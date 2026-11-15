## ADDED Requirements

### Requirement: Registro aditivo de la robustez de la línea de base frente a la referencia

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL recibir una sección aditiva
nueva (la `3.36`, primera libre tras la `3.35` de c-224) que registre, por subconjunto de referencia
—consenso `E3`/`E4` (`n = 142`), `150` originales (`n = 150`) y arbitrado completo (`n = 206`)—, la
brecha híbrido menos línea de base con su IC 95 %, sus aciertos, el criterio de McNemar aplicado, la
fuente (el JSON del análisis de robustez) y el comando que lo produce. Cada valor SHALL figurar con
estado `vigente (nuevo)`, SHALL declararse aditivo y MUST NOT reemplazar ningún valor de las
secciones `3.1` a `3.35`. La sección SHALL declarar que la cifra primaria `0,6893/206`, el macro-F1
`0,7024` y el veredicto del umbral `0,85` no cambian.

#### Scenario: Sección aditiva con procedencia por valor

- **WHEN** se lee la sección `3.36` del memo
- **THEN** cada cifra de la brecha por subconjunto figura con su fuente (JSON) y su comando
- **AND** cada valor se marca `vigente (nuevo)` y aditivo

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones `3.1` a `3.35` antes y después de la incorporación
- **THEN** ningún valor `vigente` cambia
- **AND** la cifra primaria `0,6893/206`, el macro-F1 `0,7024` y el veredicto del umbral `0,85` se declaran sin cambios
