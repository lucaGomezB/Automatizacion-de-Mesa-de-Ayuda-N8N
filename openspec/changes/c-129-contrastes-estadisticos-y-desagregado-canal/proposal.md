## Why

El dictamen CONEAU 2026-10-22 sobre la v10/v1.1.0 (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`, seccion 6 observaciones primera, segunda, tercera y quinta; seccion 7, parrafo del desagregado por canal; recomendaciones B7 -parte de tiempos-, B12 y B13 -parte de cronometraje-) observa que el analisis de tiempos, aunque aritmeticamente correcto, no es verificable ni homogeneo en cuatro puntos: (1) H1 es unilateral (`M_manual > M_automatizado`) pero el p reportado (3,08e-32) es el bilateral de `scipy.stats.wilcoxon`; (2) la potencia compara un `d_z ~ 0,20` minimo detectable con una reduccion relativa (71,2 %), que no es un tamano del efecto estandarizado; (3) el muestreo se declara "estratificado proporcional" sin la distribucion del universo y con Bases de Datos `n = 1`; (4) el cronometraje "no anunciado" convive con un cronometraje "en vivo por el companero", y la discusion afirma "reducciones positivas en los tres" canales sin tabla que lo respalde. Todo es computable sobre el corpus versionado (`data/corpus_evaluacion_pseudonimizado.json`, 200 pares, `canal_origen` 81/66/53), sin caches de predicciones ni llamadas pagas, y conviene cerrarlo antes de la defensa porque el dictamen lo cuenta entre los descuentos del criterio "Metodologia de investigacion" (peso 20).

## What Changes

- **Framework de evaluacion (test-first, `evaluation/stats.py` y `evaluation/run_evaluation.py`):** funciones puras nuevas para estadisticos descriptivos (media, mediana, desvio muestral, minimo, maximo), reduccion relativa, tamano del efecto `d_z = media(d) / desvio(d)`, efecto minimo detectable (aproximacion normal, con y sin eficiencia relativa asintotica) y escenarios de sensibilidad del redondeo manual (descuentos de 5 s y 10 s); `ResultadoWilcoxon` agrega el p unilateral (`alternative="greater"` sobre manual - automatizado) sin alterar `W = min(T+, T-)` ni el p bilateral.
- **Reporte (`evaluation/report.md`), seccion "Tiempos" aditiva:** subsecciones nuevas con descriptivos global y por canal (brazo manual y automatizado, reduccion relativa, pares no mas rapidos), contraste direccional (p bilateral y unilateral), `d_z` y minimo detectable global y por canal, escenarios de sensibilidad y granularidad de la medicion manual. Las tablas existentes (Shapiro, Wilcoxon global, reduccion, desglose por canal) se conservan intactas.
- **Regeneracion sin predicciones:** nuevo modo `python -m evaluation.run_evaluation --solo-tiempos` que reemplaza solo el bloque "## Tiempos" del reporte, sin cache ni clasificador; la huella SHA-256 del corpus pasa a ser independiente del fin de linea (CRLF/LF), de modo que en Windows siga siendo la canonica `1fd17d7e...`.
- **Tesis (`docs/Tesis/v10 (IA)/paper/sections/`):** `tab:tiempos-canal` (`07-resultados.tex`) incorpora el brazo manual, la reduccion relativa, los pares no mas rapidos y el contraste intra-canal (valor p y `d_z`; `W`, `T+`, `T-` y `r` por canal quedan en el reporte, ver `design.md` D7); la frase de `08-discusion.tex:20` remite a esa tabla; `04-marco-metodologico.tex` declara la convencion bilateral/unilateral con el p correspondiente (y `01-introduccion.tex:32`), corrige la comparacion de potencia con `d_z`, hace verificable (o declara no verificable) la proporcionalidad del muestreo y discute la asignacion con Bases de Datos `n = 1`, y precisa el procedimiento de cronometraje en vivo y su relacion con la mitigacion del efecto Hawthorne (propagado a `11-aspectos-legales.tex:32`, `08-discusion.tex:20` y al resumen/abstract).
- **Hallazgos adicionales del propose (mismo dominio, bajo costo):** el desvio estandar automatizado `13,48 s` usa la convencion poblacional mientras el manual `44,9 s` usa la muestral; se unifica en muestral (`13,52 s`). La planilla manual registra valores multiplos de 5 s (199/200; 180/200 multiplos de 10 s), dato verificable que precisa el instrumento y ancla los escenarios de sensibilidad de 5 s y 10 s. `04-marco-metodologico.tex:65` promete un intervalo de confianza al 95 % del tiempo medio que no se reporta; se alinea.
- **Numeros canonicos:** `docs/Tesis/Correcciones/numeros-canonicos.md` recibe una seccion nueva (upsert c-129) con cada valor nuevo o hasta hoy no registrado del bloque de tiempos, con procedencia en el reporte regenerado; `13,48` pasa a `retirado`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `evaluation-framework`: se agregan requisitos para los descriptivos de tiempos global y por canal, el contraste direccional con p unilateral, el tamano del efecto `d_z` con efecto minimo detectable homogeneo, los escenarios de sensibilidad del redondeo y la granularidad de la medicion manual, y la regeneracion de la seccion "Tiempos" sin predicciones con huella del corpus independiente del fin de linea.
- `tesis-document`: se agregan requisitos para la tabla de tiempos por canal con brazo manual y contraste intra-canal, la convencion declarada del valor p frente a H1 unilateral, la comparacion de potencia sobre `d_z`, la verificabilidad del muestreo y de la asignacion por sector, la precision del procedimiento de cronometraje y la convencion unica del desvio estandar. El requisito existente de `tesis-numeros-canonicos` ("Registro canonico con procedencia por valor") se cumple sin modificarse.

## Impact

- Codigo: `evaluation/stats.py`, `evaluation/run_evaluation.py` (seccion de tiempos, `--solo-tiempos`, huella del corpus), `evaluation/tests/test_stats.py`, `evaluation/tests/test_run_evaluation.py`, `evaluation/README.md`, `evaluation/report.md` (regenerado).
- Tesis: `sections/{00-resumen,01-introduccion,04-marco-metodologico,07-resultados,08-discusion,11-aspectos-legales}.tex`; render `docs/Tesis/v10 (IA)/tesis_para_agente.md`.
- Correcciones: `docs/Tesis/Correcciones/numeros-canonicos.md`.
- Specs: deltas de `evaluation-framework` y `tesis-document`.
- No toca: backend, clasificador, N8N, el corpus (contenido), las metricas de clasificacion del reporte, la exactitud por canal (c-126), el gate (c-125), la cronologia y la salvedad telefonica de conclusiones (c-130), las recomendaciones (c-131), la bibliografia metodologica de B15, `CHANGES.md`, tags.
- Sin dependencias nuevas: `scipy` ya esta en `evaluation/requirements.txt`; el minimo detectable usa `statistics.NormalDist`.
- Gobernanza: MEDIUM (codigo de evaluacion y numeros canonicos con checkpoints; las redacciones sobre muestreo y cronometraje describen hechos del estudio y requieren confirmacion del autor, ver `design.md` Open Questions).
- Presupuesto de paginas: impacto bruto estimado +0,4 a +0,6 pagina, con compensacion propuesta dentro de los mismos pasajes; neto esperado <= +0,4 pagina. Tope duro <= 101 paginas; la verificacion final integrada la hace c-136.

## Rollback

Revertir los archivos afectados con `git checkout <commit-previo> -- evaluation/ "docs/Tesis/v10 (IA)/" docs/Tesis/Correcciones/numeros-canonicos.md` y recompilar el PDF. `evaluation/report.md` vuelve a su version previa con el mismo checkout (no requiere predicciones). No hay migraciones de datos ni tags involucrados.

## Success Criteria

- [ ] `pytest` de `evaluation/` en verde, con cobertura completa de las funciones nuevas de `stats.py` y de las ramas nuevas del runner.
- [ ] `python -m evaluation.run_evaluation --solo-tiempos` regenera el bloque "## Tiempos" sin predicciones ni llamadas pagas; las filas previas (W=363, T+=19737, T-=363, p=3.08e-32, r=0.9639; desglose por canal) no cambian y el SHA-256 emitido es `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` en Windows y en Linux.
- [ ] `tab:tiempos-canal` muestra brazo manual, automatizado, reduccion y contraste intra-canal por canal, y la frase de la discusion sobre "reducciones positivas en los tres" es verificable contra esa tabla.
- [ ] La tesis declara la convencion del p frente a H1 unilateral, compara la potencia sobre `d_z`, declara la verificabilidad del muestreo y la asignacion de Bases de Datos, y describe el cronometraje sin contradiccion con la mitigacion del efecto Hawthorne.
- [ ] Todo numero nuevo citado en la tesis figura en `numeros-canonicos.md` con procedencia; `13,48` queda `retirado` y no aparece en las fuentes.
- [ ] El PDF compila sin errores fatales ni referencias indefinidas y el impacto neto en paginas queda medido y registrado (tope duro <= 101).
