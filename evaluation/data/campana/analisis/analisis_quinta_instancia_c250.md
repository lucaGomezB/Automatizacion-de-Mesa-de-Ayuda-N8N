# Recomputo de la asimetria telefonica y de la sub-hipotesis 1 sin telefonia (c-250)

Salida generada por `analisis_quinta_instancia_c250.py`. Analisis de solo lectura sobre los artefactos versionados; no reclasifica ni modifica el corpus.

## Telefonia: grabacion cruda frente a grabacion mas procesamiento

- Casos (grabaciones): 81.
- `duracion_segundos` (grabacion cruda): media 7.2593 s; mediana 7.0000 s; rango [3.0000; 45.0000] s.
- `t_e2e_s` (grabacion mas procesamiento): media 20.0883 s; mediana 18.6980 s.

## Sub-hipotesis 1 sin telefonia (correo electronico + formulario web, regimen (a))

- Casos: 119.
- Media manual: 44.1176 s.
- Media automatizada: 16.1762 s.
- Reduccion (media): 63.3340 % [56.0756; 69.6178].
- Diferencia pareada media: 27.9415 s [22.7801; 33.9751].
- Wilcoxon pareado (lectura suplementaria): T = 302.0000, p = 4.471e-18.

## Entradas

| Archivo | SHA-256 |
|---|---|
| `data/corpus_resultados_telefonia.json` | `7f8c9d293e6aaf2e64a6024fe235b0224d4daa1997c7cd030f90071f05d288cb` |
| `data/corpus_evaluacion_pseudonimizado.json` | `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` |
