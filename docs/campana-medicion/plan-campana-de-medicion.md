# Plan de la corrida de campo (campana de medición)

Registro de la campana que se ejecuta **después de aplicar** los changes `c-165` a `c-169`. Su objetivo es producir las mediciones que la auditoría CONEAU v1.2.5 marcó como faltantes y que caparon los criterios 1 y 4 de la rúbrica: exactitud del brazo manual, tasa de intervención humana, efecto de orden, validación fuera de muestra e intervalo de confianza del kappa.

Estado: **PENDIENTE** (no ejecutada). Se dispara cuando `c-165`, `c-166`, `c-167` y `c-168` estén aplicados.

## Alcance

La corrida produce cinco conjuntos de datos:

1. **Doble etiquetado independiente** del corpus (200 casos, o un subconjunto justificado) → tabla primaria de acuerdo → kappa con intervalo.
2. **Exactitud del brazo manual**: el sector que asigna el operador por caso, bajo la condición manual, medido con etiquetadores independientes.
3. **Intervención humana real**: por caso, actor, instante, origen (gate, revisión, muestreo, completado manual, reasignación) y delta antes/después.
4. **Efecto de orden**: corrida contrabalanceada (orden directo/inverso o alternado) para estimar el efecto de orden del diseño pareado.
5. **Validación fuera de muestra**: corpus independiente (sin solape, mismo protocolo de pseudonimización y doble etiquetado) con métricas de las dos etapas.

## Prerrequisitos (aplicar antes)

| Change | Aporta |
|---|---|
| `c-165` | Instrumento de captura del brazo manual + esquema de intervención (actor/instante/origen/delta) + protocolo de campana |
| `c-166` | Control de orden/brazo en los harness (`--orden`/`--seed`) + protocolo de contrabalanceo + protocolo de corpus independiente |
| `c-167` | Scripts de análisis: exactitud manual, tasa de intervención, efecto de orden, métricas fuera de muestra, **kappa + IC** |
| `c-168` | Plantilla y protocolo de doble etiquetado (independencia/blinding) |
| `c-169` | (Post-campana) incorporación de los resultados a la tesis |

## Pasos de la corrida (en orden)

1. **Doble etiquetado** (c-168): dos etiquetadores independientes etiquetan el corpus con la plantilla; verificar cobertura completa y ausencia de celdas vacías. Salida: tabla primaria de acuerdo.
2. **Corrida contrabalanceada con brazo manual medido e intervención instrumentada** (c-165 + c-166): ejecutar la campana con el parámetro de orden, registrando por caso la clasificación del operador (condición manual) y la intervención real. Salida: datasets de exactitud manual, intervención y efecto de orden.
3. **Corpus independiente** (c-166): construir, pseudonimizar y doble-etiquetar un corpus sin solape con el de ajuste; correrlo y registrar las métricas fuera de muestra.
4. **Análisis** (c-167): correr los scripts sobre los datasets 1-3; producir exactitud manual (estricta/laxa con IC de Wilson), tasa de intervención (proporción de casos y del tiempo con IC), efecto de orden, métricas fuera de muestra y **kappa + IC** (bootstrap y/o asintótico).
5. **Registro y documentación** (c-169): consignar los valores canónicos con procedencia en `docs/Tesis/Correcciones/numeros-canonicos.md` y llevar los resultados a la tesis (4.4/4.5/4.7/4.8, 8.x, resumen/abstract), retirando los rótulos de "no medido / no contrastada / no estimable" que correspondan.

## Criterios de aceptación

- Cobertura completa del doble etiquetado (sin casos sin etiqueta).
- Independencia verificable (blinding registrado; los etiquetadores no vieron el consenso ni entre sí).
- Corpus independiente sin solape con el corpus de ajuste (verificación explícita).
- Contrabalanceo efectivo registrado por caso (campo de orden en el sidecar).
- Todos los números nuevos con su procedencia y su intervalo.

## Fuera del repositorio

La corrida de campo (llamadas, etiquetado humano, operadores reales) ocurre fuera del repositorio. El repositorio entrega los instrumentos, protocolos y scripts; la ejecución la hacen los autores. La incorporación documental de los resultados es `c-169`.

## Activos de la campana

- Instrumento y esquema: `c-165`.
- Control de orden y corpus independiente: `c-166`.
- Análisis y kappa + IC: `c-167`.
- Plantilla de doble etiquetado: `c-168`.
- Documentación final: `c-169`.
