## ADDED Requirements

### Requirement: Advertencia metodologica del framework coherente con el historial

`evaluation/README.md` SHALL describir la procedencia factual de los ajustes del clasificador realizados con el corpus de evaluacion (vocabulario del filtro deterministico, c-71, commit `1368fd8`; reglas de frontera del prompt, c-72, commit `a76851e`; punto de operacion del cortocircuito por validacion cruzada fuera de muestra, c-74, commit `d6bb474`), SHALL declarar que la mitigacion fuera de muestra cubre el punto de operacion pero no el vocabulario ni las reglas del prompt, SHALL calificar las metricas del reporte como estimaciones dentro de la muestra, SHALL declarar que no se dispuso de un corpus independiente de preproduccion y SHALL enunciar la regla vigente: el corpus de evaluacion se usa solo para diagnostico y todo ajuste posterior se mide sobre datos separados. La documentacion MUST NOT afirmar que el clasificador no fue ajustado sobre el corpus de evaluacion.

#### Scenario: Sin afirmacion de no ajuste

- **WHEN** se busca en `evaluation/README.md` una afirmacion de que el clasificador no fue ajustado sobre el corpus de evaluacion
- **THEN** no aparece ninguna

#### Scenario: Procedencia de los tres ajustes presente

- **WHEN** se lee la advertencia metodologica de `evaluation/README.md`
- **THEN** enumera los ajustes de c-71, c-72 y c-74 con su commit
- **AND** declara que la mitigacion fuera de muestra no cubre el vocabulario ni las reglas del prompt

#### Scenario: Naturaleza dentro de la muestra y ausencia de corpus independiente

- **WHEN** se lee la advertencia metodologica
- **THEN** las metricas del reporte se califican como estimaciones dentro de la muestra
- **AND** se declara que no se dispuso de un corpus independiente de preproduccion
- **AND** la validacion sobre un corpus independiente figura como linea de trabajo futuro
