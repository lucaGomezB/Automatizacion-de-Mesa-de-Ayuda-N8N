# Tasks: Analisis de la campana y fiabilidad entre etiquetadores

## 1. Kappa con intervalo de confianza (fiabilidad entre etiquetadores)

- [ ] 1.1 Escribir el test de `kappa_cohen` sobre una matriz de acuerdo conocida (ej. 5x5 sintetica) con valor esperado calculado a mano, y verificar que falla antes de implementar
- [ ] 1.2 Implementar `evaluation/kappa.py` con `kappa_cohen` (Cohen 1960) y verificar que el test 1.1 pasa
- [ ] 1.3 Triangular con una matriz perfectamente diagonal (kappa = 1.0) y una de acuerdo solo por azar (kappa = 0.0), y verificar ambos casos
- [ ] 1.4 Escribir el test del IC por bootstrap con semilla fija: dos corridas devuelven el mismo intervalo, y verificar
- [ ] 1.5 Implementar `kappa_intervalo_bootstrap` reutilizando el patron de remuestreo de `metrics.py` y verificar el test 1.4
- [ ] 1.6 Escribir el test del IC asintotico (varianza de Fleiss) sobre la matriz sintetica y verificar el valor esperado
- [ ] 1.7 Implementar `kappa_intervalo_asintotico` y verificar el test 1.6
- [ ] 1.8 Escribir el test de denominador indeterminado (`pe == 1`) y verificar que el resultado declara no estimable sin valor numerico
- [ ] 1.9 Implementar la deteccion de no estimable y verificar el test 1.8

## 2. Analisis de exactitud del brazo manual

- [ ] 2.1 Escribir el test de exactitud estricta y laxa por etiquetador y agregada sobre un fixture sintetico, y verificar que falla
- [ ] 2.2 Implementar `exactitud_brazo_manual` reutilizando las funciones de `metrics.py` y verificar el test 2.1
- [ ] 2.3 Triangular con un caso donde la exactitud laxa supera a la estricta y verificar la relacion esperada
- [ ] 2.4 Escribir el test de etiqueta ausente contada como error y verificarlo (incluye conteo de casos faltantes)
- [ ] 2.5 Verificar que cada exactitud reporta su IC de Wilson con nivel declarado

## 3. Tasa de intervencion humana con IC

- [ ] 3.1 Escribir el test de proporcion de casos y de tiempo con IC de Wilson sobre un dataset sintetico, y verificar que falla
- [ ] 3.2 Implementar `tasa_intervencion_humana` y verificar el test 3.1
- [ ] 3.3 Triangular con dataset sin intervenciones (tasa cero, IC valido, sin division por cero) y verificar
- [ ] 3.4 Escribir el test de casos elegibles no intervenidos excluidos del numerador y verificarlo

## 4. Efecto de orden del run contrabalanceado

- [ ] 4.1 Escribir el test de contraste primera vs segunda mitad con pares sinteticos y verificar que falla
- [ ] 4.2 Implementar `efecto_de_orden` usando `stats.wilcoxon_tiempos_detallado` y `tamano_efecto_dz`, y verificar el test 4.1
- [ ] 4.3 Triangular con pares insuficientes y verificar que el resultado declara no aplicable

## 5. Evaluacion out-of-sample del corpus independiente

- [ ] 5.1 Escribir el test que evalua ambas etapas sobre un corpus independiente sintetico y verifica que falla
- [ ] 5.2 Implementar `evaluar_fuera_de_muestra` reutilizando las funciones de metrica del runner, y verificar el test 5.1
- [ ] 5.3 Triangular con un reporte que incluye in-sample y out-of-sample y verificar que las secciones quedan separadas
- [ ] 5.4 Escribir el test de corpus independiente ausente y verificar que lanza error nombrando el artefacto, sin caer a in-sample

## 6. CLI de lectura y ejecucion offline

- [ ] 6.1 Agregar el fixture sintetico en `evaluation/tests/fixtures/` y verificar que los tests de las secciones 1-5 lo consumen
- [ ] 6.2 Implementar el CLI `evaluation/analisis_campana.py` (solo lectura + delegacion) y verificar con un fixture sintetico end-to-end sin red
- [ ] 6.3 Verificar reproducibilidad: dos ejecuciones con la misma semilla producen numeros e intervalos identicos
- [ ] 6.4 Ejecutar `cd evaluation; pytest` y verificar que la suite completa pasa offline, sin Gemini ni credenciales
