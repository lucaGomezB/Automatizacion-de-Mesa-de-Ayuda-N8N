## ADDED Requirements

> **Alcance actualizado (rebase sobre `main` 9d348c4).** c-210 cubre TLB-04 y la parte textual de TLB-02 y TLB-03 (tabla `tab:linea-base-clasica`, discusión, conclusiones, recomendaciones). c-213 aporta el contraste pareado: lo que sigue vale para el párrafo de `07-resultados.tex` tras esa tabla, las cláusulas de `08` y `09`, el método de `04` y la sección 3.23 del memo. Toda referencia a `tab:linea-de-base` o `subsec:linea-de-base` se lee como `tab:linea-base-clasica`; toda referencia a la sección 3.22 del memo para las cifras del contraste, como 3.23.

### Requirement: TLB-01 — Método de la línea de base en el marco metodológico

La tesis SHALL describir en `04-marco-metodologico.tex` qué es la línea de base (TF-IDF de palabras y caracteres + regresión logística regularizada, dos variantes fijadas antes de medir), con qué datos se entrenó (los 200 casos de ajuste) y se probó (los 103 casos fuera de muestra con consenso de `E3` y `E4`), el control de filtración (los casos de prueba no intervienen en entrenamiento ni en la elección de variantes), el contraste pareado aplicado y qué NO es (no es el brazo solo-LLM ni un supervisado afinado).

#### Scenario: Método completo

- **WHEN** se lee el marco metodológico
- **THEN** figuran el modelo, los conjuntos de entrenamiento y prueba con su `n`, el control de filtración y el contraste pareado
- **AND** se declara que la línea de base no es el brazo solo-LLM

### Requirement: TLB-02 — Resultados trazables a artefactos versionados

La tesis SHALL incluir en `07-resultados.tex` una tabla de la línea de base frente al híbrido sobre los mismos 103 casos (exactitud estricta con intervalo de Wilson, exactitud laxa, macro-F1, *balanced accuracy*) y el contraste pareado. Cada cifra MUST provenir de `linea_de_base_clasica_c210.json`, `analisis_fuera_de_muestra_c205.json` o `contraste_linea_de_base_c213.json`, y MUST estar registrada en la sección nueva de `numeros-canonicos.md`. Ningún número canónico existente SHALL cambiar.

#### Scenario: Cifra sin artefacto

- **WHEN** una cifra de la tabla o del texto nuevo no aparece en un artefacto versionado
- **THEN** la tarea no se da por terminada

#### Scenario: Números canónicos intactos

- **WHEN** se compara la tabla canónica del memo antes y después del change
- **THEN** no hay valores modificados, solo la sección aditiva nueva

### Requirement: TLB-03 — Lectura acotada y honesta

La tesis SHALL presentar el resultado como superioridad del híbrido frente a un único clasificador supervisado clásico entrenado con 200 ejemplos, en este corpus y este conjunto de prueba, y SHALL declarar las condiciones de equidad y las amenazas (desarrollo de ambos sistemas con los mismos 200 casos, exclusión de los 47 discordantes, clases chicas, `Bases de Datos` con un solo caso de ajuste, una sola organización, un solo modelo sin afinar). La tesis MUST NOT afirmar superioridad general de los LLM o del esquema híbrido sobre los clasificadores supervisados, y MUST NOT presentar la comparación como contraste de la hipótesis subsidiaria de eficiencia frente al LLM solo, que sigue sin contrastarse.

#### Scenario: Sin generalización

- **WHEN** se revisan las oraciones nuevas o modificadas
- **THEN** ninguna afirma superioridad general ni eficiencia frente a un esquema solo de modelo

#### Scenario: Hipótesis de eficiencia

- **WHEN** se lee la discusión de la hipótesis subsidiaria de eficiencia
- **THEN** sigue declarada como no contrastada

### Requirement: TLB-04 — Ninguna afirmación de inexistencia de la comparación

Después del change, ningún pasaje de la tesis MUST afirmar que no se comparó el esquema híbrido contra un clasificador supervisado o que falta una línea de base; las recomendaciones y el trabajo futuro SHALL enumerar lo que queda pendiente (brazo solo-LLM, más datos de entrenamiento, supervisados más fuertes, repetición con n = 150 arbitrado).

#### Scenario: Grep de afirmaciones obsoletas

- **WHEN** se buscan en `sections/*.tex` las expresiones "ausencia de una línea de base", "no se comparó" y "No se realizó una comparación directa"
- **THEN** no quedan coincidencias referidas al clasificador supervisado

### Requirement: TLB-05 — Trazabilidad y preparación para c-206

El change SHALL registrar la integración en `dictamen-correcciones.md` (criterio 4), en `CHANGES.md` (FASE nueva), regenerar `tesis_para_agente.md` y pasar `verify_citations.py` sin claves bibliográficas sin resolver. La tabla y la prosa SHALL identificar el conjunto como los 103 casos con consenso y anunciar que la comparación se repetirá sobre los 150 casos cuando exista el arbitraje, de modo que esa actualización sea mecánica.

#### Scenario: Citas verificadas

- **WHEN** se corre `verify_citations.py`
- **THEN** todas las claves citadas existen en `Bibliography_base.bib`

#### Scenario: Seguimiento de c-206

- **WHEN** c-206 entrega la referencia arbitrada
- **THEN** basta volver a correr el script de contraste con esa referencia y sustituir las cifras señaladas en la tabla y el memo
