# Proposal: Analisis de la nueva campana y de la fiabilidad entre etiquetadores

## Why

Los datasets de la campana (brazo manual e intervencion, c-165) y del doble etiquetado
(c-168) no tienen consumidores analiticos: hoy no existe codigo que calcule la exactitud
del brazo manual, la tasa de intervencion con IC, el efecto de orden, las metricas
out-of-sample ni el kappa con intervalo de confianza. Sin esos scripts la tesis no puede
reportar los resultados que esos datasets habilitan.

## What Changes

- **Exactitud del brazo manual**: exactitud estricta y laxa contra la verdad de consenso,
  por etiquetador y agregada, con IC de Wilson.
- **Tasa de intervencion humana**: proporcion de casos y proporcion de tiempo de proceso,
  con IC de Wilson, segun la definicion operativa de la tesis (11.3).
- **Efecto de orden**: contraste primera vs segunda mitad del run contrabalanceado (c-166),
  reutilizando las funciones de `evaluation/stats.py`.
- **Metricas out-of-sample**: evaluacion del corpus independiente (c-166) para ambas etapas
  (deterministica y Gemini) con las funciones de metrica existentes.
- **Kappa con IC**: coeficiente de Cohen + IC (bootstrap con semilla y aproximacion
  asintotica/Fleiss) sobre el dataset de doble etiquetado (c-168). Hoy no existe funcion
  de kappa en el repositorio.
- Nuevo modulo de analisis en `evaluation/` con suite offline sobre fixtures sinteticos.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `evaluation-framework`: se AGREGAN requisitos de analisis de campana (exactitud manual,
  tasa de intervencion con IC, efecto de orden, out-of-sample y kappa con IC) como
  comportamiento nuevo del framework, sin alterar los requisitos existentes.

## Impact

- `evaluation/` (nuevo modulo de analisis + funciones de kappa en `stats.py` o modulo adyacente)
- `evaluation/tests/` (tests offline nuevos, mismo patron que las suites existentes)
- `evaluation/requirements.txt` solo si se requiere una dependencia nueva (por defecto, stdlib)
- Coordinacion: c-165 y c-166 AGREGAN requisitos a `evaluation-campaign-instrumentation`
  (instrumento y diseño); c-167 consume sus salidas y vive en `evaluation-framework`.
- Sin cambios a `docs/Tesis/v9 (IA)/`, strings de categorias ni numeros canonicos.
- Sin datos de campo en el repositorio: los scripts corren contra datasets externos.

## Approach

Biblioteca pura y deterministica en `evaluation/`, reutilizando `intervalo_wilson`,
`intervalos_por_clase`, `intervalos_conjunto` y el bootstrap con semilla declarada de
`metrics.py`, y Wilcoxon/dz de `stats.py`. Cada analisis es una funcion pura que recibe
los registros ya cargados; un CLI fino los lee de ruta. El kappa se implementa desde cero
(Cohen 1960) con IC por bootstrap reproducible y por la varianza asintotica (Fleiss).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Datos de campo ausentes al implementar | Alta | Tests con fixtures sinteticos; el CLI falla con error claro si falta el dataset |
| IC del kappa inestable con n chico | Med | Reportar ambos metodos y declarar no estimable cuando corresponda |
| Duplicar logica de metricas | Baja | Reutilizar funciones existentes; solo kappa es codigo nuevo |

## Rollback Plan

Eliminar el modulo de analisis y sus tests; no hay migraciones, cambios de esquema ni
dependencias obligatorias. Los artefactos existentes del framework y el corpus quedan intactos.

## Dependencies

- Salidas de c-165 (brazo manual e intervencion), c-166 (contrabalanceo y corpus
  independiente) y c-168 (doble etiquetado), disponibles fuera del repositorio.

## Success Criteria

- [ ] Cada uno de los cinco analisis es una funcion pura cubierta por tests offline.
- [ ] El kappa reporta valor e IC por bootstrap (semilla fija) y por via asintotica.
- [ ] Los IC de proporciones usan Wilson y declaran el nivel de confianza.
- [ ] El CLI procesa un fixture sintetico end-to-end sin red ni Gemini.
