#!/usr/bin/env python3
"""Calibracion y punto de operacion del gate de confianza (c-214). PRERREGISTRO.

Este docstring congela las decisiones D2-D5 del `design.md` del change ANTES de generar
ninguna salida; el commit que lo introduce precede al de las salidas. Sin red, sin Gemini,
sin Docker. Determinista. No modifica configuracion productiva (CAL-005).

Declaracion de no ceguera
-------------------------
Para comprobar la factibilidad, quien propuso el change tabulo la distribucion de confianzas y
los aciertos por nivel en ambos corpus. Las reglas siguientes se fijan por principio (las
recomendaciones ya publicadas en la seccion 10 de la tesis), no por lo que esa tabulacion
sugiera, y se informan TODOS los resultados, favorables o no. El prerregistro NO fue ciego.

Insumos (solo lectura)
----------------------
- Dentro de la muestra: `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (200
  casos; referencia = `sector_asignado`, la original). Control: consenso E1/E2 sobre los 138
  casos de la planilla de la campana.
- Fuera de la muestra: `evaluation/data/campana/predicciones_independiente.json` (103 casos;
  referencia = `sector_asignado`, consenso E3/E4). Acierto = exactitud estricta.
- Secundarios NO ejecutados en esta aplicacion: (a) predicciones de un brazo Gemini solo (un
  change futuro, no propuesto todavia); (b) corpus arbitrado de c-206 (aun inexistente).

D2 - Metricas (por etapa y corpus)
----------------------------------
Etapas: Gemini (con su `confianza`) y determinista (con su `confianza` y con su
`score_correctitud` recomputado). Tabla de fiabilidad por valor observado (casos, aciertos,
exactitud, Wilson 95 %); ECE con 10 bandas de igual ancho en [0; 1] (la ultima cerrada);
Brier (media de (confianza - acierto)^2); sobreconfianza media (confianza media - exactitud);
AUROC de la senal para separar aciertos de errores (Mann-Whitney, empates a 0,5; `None` si
falta una de las dos clases). IC95 bootstrap percentil por caso con `SEMILLA_BOOTSTRAP` y
`REMUESTREOS_BOOTSTRAP` de `evaluation/metrics.py`.

D3 - Barrido de umbral (etapa Gemini)
-------------------------------------
Candidatos T = {0,70 (vigente); 0,86; 0,91; 0,96; 0,99; inf}; se acepta si confianza >= t;
inf = derivar todo lo escalado. Por t: cobertura (aceptados / escalados), exactitud selectiva
de los aceptados (Wilson), exactitud de los derivados, errores atrapados en los derivados y
carga de revision del sistema (derivados / casos del corpus).

D4 - Regla de seleccion (prerregistrada)
----------------------------------------
- Piso primario phi = 0,85; secundario phi' = 0,8278 (informado aparte).
- Seleccion en los 200: t* = el menor t en T \ {inf} cuya exactitud selectiva de los
  aceptados sea >= phi con al menos 10 aceptados; si ninguno cumple, t* = ninguno.
- Evaluacion en los 103, sin reajuste: `no estimable` si hay menos de 10 aceptados o ningun
  derivado; `confirmado` si la exactitud selectiva es >= phi y la de los derivados es menor
  que la de los aceptados; `no confirmado` en los demas casos.
- Si t* = ninguno: el resultado es que la senal no sostiene un umbral con el piso fijado;
  fuera de la muestra el barrido y el AUROC se informan solo como descripcion.
- Recalibracion isotonica (ajustada en los 200) solo como correccion de nivel (ECE y Brier
  fuera de muestra); no cambia el orden ni la curva riesgo-cobertura.
- Prohibido elegir umbrales con los datos fuera de la muestra; toda lectura adicional se
  rotula exploratoria.

D5 - Senales alternativas (costo cero), misma regla
---------------------------------------------------
- S1, acuerdo entre etapas: en los casos escalados, el sector que habrian dado las reglas
  (ganador unico, aun por debajo de tau = 0,5166) frente al de Gemini: acuerdo / desacuerdo /
  sin prediccion de las reglas (sin senal o empate). Politica: aceptar si hay acuerdo, derivar
  si no. Candidato unico t = 1,0 sobre la senal binaria (acuerdo = 1, resto = 0).
- S2, `score_correctitud` de las reglas en los casos escalados: candidatos {0,0 (sin derivar);
  cuantiles 0,25; 0,50; 0,75 del score en los escalados de los 200 (rango por posicion,
  `sorted[ceil(q * n) - 1]`); inf}; se acepta si score >= t.
- Seleccion en los 200 y evaluacion en los 103 con las mismas condiciones de D4.
- El recomputo de las reglas debe reproducir exactamente la etapa y el sector de los casos
  cortocircuitados de las caches (131/131 y 69/69); si no, se detiene y se informa la deriva.
"""
