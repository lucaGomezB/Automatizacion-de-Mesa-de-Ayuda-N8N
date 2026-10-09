# Tasks: c-77 — Errores estadístico-inferenciales y coherencia técnica

> Convención de archivos: `S = docs/Tesis/v9 (IA)/paper/sections`.
> Verificación de texto: `rg` sobre `S` (sin compilador LaTeX local).
> Verificación de datos: `python3` sobre el corpus real.
> Recompilación: Overleaf (tarea final). No se edita `App/**` salvo decisión.

## 1. A1 — Convención de W y reporte de T+/T−

- [ ] 1.1 En `S/04-marco-metodologico.tex` (§Análisis estadístico) declarar la convención `W = min(T+, T−)` (estadístico de dos colas de `scipy`) antes de citar la prueba; verificar con `rg -n "W =" S/04-marco-metodologico.tex` que la convención queda enunciada.
- [ ] 1.2 En `S/07-resultados.tex` (§7.1) reemplazar `W=0` por el valor real y reportar `T+=19765`, `T−=335`, `n=200`; verificar con `rg -n "W = 0|T\\+|T-" S/07-resultados.tex` que `W = 0` ya no aparece y que ambos estadísticos están presentes.
- [ ] 1.3 Confirmar aritméticamente `T+`/`T−`/`p` con `python3 -c` sobre `data/corpus_evaluacion_pseudonimizado.json` (`tiempo_manual_s`, `tiempo_automatizado_s`); registrar la salida como evidencia.

## 2. A2 — Fórmula, rango y recálculo del tamaño del efecto

- [ ] 2.1 En `S/04-marco-metodologico.tex:65-69` corregir la fórmula a `r=(T+−T−)/(n(n+1)/2)` (equivalente `1−4W/(n(n+1))` si `W=T−`) y el rango verdadero (no `[-1,+1]`); verificar con `rg -n "1 - \\\\frac\\{2W\\}" S/04-marco-metodologico.tex` que la fórmula vieja no queda.
- [ ] 2.2 En `S/07-resultados.tex:32-36` recalcular y reportar `r=0,9667` (no `1,00`); verificar con `rg -n "r = 1|1,00|0,9667" S/07-resultados.tex` que `1,00` desaparece y `0,9667` aparece.
- [ ] 2.3 **RED** — en `evaluation/tests/test_stats.py` agregar un test que exija `r=(T+−T−)/(n(n+1)/2)` y el reporte de `T+`/`T−`; ejecutar `cd evaluation && pytest tests/test_stats.py` y confirmar que FALLA.
- [ ] 2.4 **GREEN** — en `evaluation/stats.py` corregir la fórmula/docstring y exponer `T+`/`T−`; ejecutar `cd evaluation && pytest tests/test_stats.py` y confirmar que PASA.
- [ ] 2.5 **TRIANGULATE** — agregar un caso con pares invertidos conocidos (p. ej. 12/200) y verificar que el efecto no es `1,00`; ejecutar `pytest tests/test_stats.py` y confirmar verde.

## 3. A3 — Rótulo de dispersión

- [ ] 3.1 En `S/08-discusion.tex:12` cambiar "varianza casi diez veces menor" por "desvío estándar" (los valores comparados son 38,7 s vs 4,1 s); verificar con `rg -n "varianza" S/08-discusion.tex` que el término se corrigió donde corresponde.

## 4. A4 — Aritmética de horas-persona

- [ ] 4.1 En `S/08-discusion.tex:14` corregir "180 horas-persona" y añadir nota al pie con el cálculo explícito (real ≈48,1 h con `(61,6−14,8)s×3700/3600`); verificar con `rg -n "180 horas-persona|151,2|48,1" S/08-discusion.tex`.
- [ ] 4.2 En `S/09-conclusiones.tex:24` alinear la cifra de horas-persona con la corregida; verificar con `rg -n "180 horas-persona" S/09-conclusiones.tex` que no queda una cifra inconsistente.
- [ ] 4.3 En `S/01-introduccion.tex:18` reconciliar "200 horas-persona" con el cálculo declarado; verificar con `rg -n "horas-persona" S/01-introduccion.tex`.
- [ ] 4.4 Verificar aritmética con `python3 -c` (3700/42; ahorros con tiempos de tesis y reales; 180 h → s/incidente) y adjuntar la salida.

## 5. A5 — Definición única de intervención humana

- [ ] 5.1 En `S/04-marco-metodologico.tex:34,57` y `S/07-resultados.tex:84-86` unificar la definición: reportar proporción de tiempo y de casos de forma rotulada, o elegir una y ser consistente; verificar con `rg -n "intervencion humana|intervención humana" S/04-marco-metodologico.tex S/07-resultados.tex`.

## 6. A6 — Calibración de la confianza

- [ ] 6.1 Recalcular y congelar las cifras reales (alta ≥0,70: 0,697=53/76; baja <0,70: 0,758=94/124; errores ≥0,90: 13/46; bandas) con `python3` sobre `evaluation/predicciones.json`; adjuntar la salida.
- [ ] 6.2 **RED/GREEN** — en `evaluation/tests/` agregar test de la función de calibración y en `evaluation/metrics.py` (o `run_evaluation.py`) implementar el reporte por bandas y la contingencia; ejecutar `cd evaluation && pytest` y confirmar verde.
- [ ] 6.3 Escribir la subsección de calibración en `S/07-resultados.tex` (tabla de contingencia y/o curva); verificar con `rg -n "calibrac|0,697|0,758" S/07-resultados.tex`.
- [ ] 6.4 Discutir la implicancia para el gate 0,70 en `S/08-discusion.tex` y referenciar en `S/06-implementacion.tex` (§6.3) y `S/11-aspectos-legales.tex` (§supervisión humana); verificar con `rg -n "calibrac|0,70" S/08-discusion.tex S/06-implementacion.tex S/11-aspectos-legales.tex`.

## 7. A7 — Universo trimestral vs volumen diario

- [ ] 7.1 En `S/01-introduccion.tex:18` y `S/04-marco-metodologico.tex:43` declarar los días del trimestre observado y reconciliar `3.700 = 42×88`; verificar con `rg -n "3.700|3\\.700|42 incidentes" S/01-introduccion.tex S/04-marco-metodologico.tex`.

## 8. B1 — Pregunta de investigación sobre el criterio humano

- [ ] 8.1 [RESUELTO — OQ2=c] Retirar la sub-pregunta sobre exactitud humana (`S/01-introduccion.tex:28`) y reformular `H1` (`S/01-introduccion.tex:32-34`) para contrastar contra el umbral objetivo (≥85 %), no contra el criterio humano. Verificar con `rg -n "criterio humano|comparable o superior|proceso manual" S/01-introduccion.tex` sin la comparación humana.

## 9. B2 — Tiempo preliminar vs experimental

- [ ] 9.1 En `S/01-introduccion.tex:18` y `S/07-resultados.tex:10` explicar la relación entre la medición preliminar (`2 min 45 s`) y la experimental (media real `61,6 s`) y citar el registro que respalda el tiempo; verificar con `rg -n "2 min 45|165,3|61,6" S/01-introduccion.tex S/07-resultados.tex`.

## 10. C1/C2 — Flujo real (verificado, sin cambio)

- [ ] 10.1 Confirmar con `rg -n "gate|revision humana|requiere_revision" S/06-implementacion.tex` que §6.3 describe clasificar → gate y ningún LLM telefónico; registrar como "sin cambio" si se confirma (ya alineado por c-72).

## 11. C3 — Canal de origen / nombre de campo

- [ ] 11.1 Alinear el nombre de campo stale del Cap. 5 (`id_canal` → `canal_origen_id`) en `S/05-arquitectura.tex`; verificar con `rg -n "canal_origen_id|id_canal" S/05-arquitectura.tex`. Documentar que el canal es entrada opcional del backend (`App/Backend/app/schemas/incidente.py:162`).

## 12. C4 — Reintentos (OQ)

- [ ] 12.1 [RESUELTO — OQ3=b] Reescribir `S/06-implementacion.tex:60` como limitación conocida + trabajo futuro (NO se implementa el reintento/cola). Verificar con `rg -n "retroceso exponencial|cola de respaldo" S/06-implementacion.tex` sin resultados.

## 13. C5 — Nginx/TLS (OQ)

- [ ] 13.1 [RESUELTO — OQ4=a] Redacción condicional en `S/05-arquitectura.tex:8`, `S/09-conclusiones.tex:10`, `S/11-aspectos-legales.tex:20` y `S/12-anexos.tex:10`: distinguir el diseño (Nginx + TLS 1.2/1.3) del despliegue publicado que no lo incluía. No se despliega el proxy.

## 14. C6 — Residuos de C-18 y anexo del log

- [ ] 14.1 Corregir `IMAP` → Outlook/Graph API en `S/06-implementacion.tex:37` y `S/12-anexos.tex:37`; verificar `rg -n "IMAP" S/06-implementacion.tex S/12-anexos.tex` sin resultados.
- [ ] 14.2 Cerrar el catálogo stale de sectores en `S/05-arquitectura.tex:76` y `S/01-introduccion.tex:46,68`; verificar `rg -n "tres sectores|Operaciones" S/05-arquitectura.tex S/01-introduccion.tex`.
- [ ] 14.3 Adjuntar `docs/Tesis/Correcciones/dictamen-correcciones.md` como anexo (nuevo `\section` en `S/12-anexos.tex`) como ejemplo de trazabilidad; verificar con `rg -n "dictamen|decisiones" S/12-anexos.tex`.

## 15. C7 — Sectores del prompt (OQ)

- [ ] 15.1 [RESUELTO — OQ5=b] Alinear la TESIS a los 5 sectores canónicos de `docs/prompt_gemini.txt` (NO tocar el prompt). Aplicar en `S/01-introduccion.tex`, `S/04-marco-metodologico.tex`, `S/05-arquitectura.tex` y Cap. 7; coordinar con c-76; verificar `rg -ni "tres sectores|Operaciones" S/` sin resultados.

## 16. C8 — Tag inexistente (OQ)

- [ ] 16.1 [RESUELTO — OQ6=diferido] NO crear tag ahora. Acción pendiente: al finalizar c-76+c-77, crear el tag `v1.0.0` sobre el commit entregado al jurado y consignar el hash completo en `S/12-anexos.tex:19`. Verificar con `git tag` y `rg -n "v1\.0\.0" S/12-anexos.tex`.

## 17. Verificación final y recompilación

- [ ] 17.1 Ejecutar el barrido de control `rg -n "W = 0|r = 1,00|varianza casi diez|180 horas-persona|IMAP|tres sectores" S/` y confirmar que no quedan residuos (o que los restantes están justificados).
- [ ] 17.2 Ejecutar `cd evaluation && pytest tests/test_stats.py` más el test de calibración y confirmar verde.
- [ ] 17.3 Recompilar la tesis en Overleaf (`main.tex`, XeLaTeX) y verificar PDF sin errores fatales; registrar el resultado (no hay toolchain local).
- [ ] 17.4 Ejecutar `openspec validate c-77-tesis-errores-estadisticos-inferenciales --strict` y confirmar que pasa.
