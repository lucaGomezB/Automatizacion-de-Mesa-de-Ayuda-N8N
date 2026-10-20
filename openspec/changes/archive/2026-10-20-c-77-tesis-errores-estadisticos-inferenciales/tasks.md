# Tasks: c-77 — Errores estadístico-inferenciales y coherencia técnica

> Convención de archivos: `S = docs/Tesis/v9 (IA)/paper/sections`.
> Verificación de texto: `rg` sobre `S`.
> Verificación de datos: `python3` sobre el corpus real.
> Recompilación: local con MiKTeX/XeLaTeX+biber (2026-10-20), 103 páginas. No se edita `App/**` salvo decisión.

## 1. A1 — Convención de W y reporte de T+/T−

- [x] 1.1 En `S/04-marco-metodologico.tex` (§Análisis estadístico) declarar la convención `W = min(T+, T−)` (estadístico de dos colas de `scipy`) antes de citar la prueba; verificar con `rg -n "W =" S/04-marco-metodologico.tex` que la convención queda enunciada.
- [x] 1.2 En `S/07-resultados.tex` (§7.1) reemplazar `W=0` por el valor real y reportar `T+=19765`, `T−=335`, `n=200`; verificar con `rg -n "W = 0|T\\+|T-" S/07-resultados.tex` que `W = 0` ya no aparece y que ambos estadísticos están presentes.
- [x] 1.3 Confirmar aritméticamente `T+`/`T−`/`p` con `python3 -c` sobre `data/corpus_evaluacion_pseudonimizado.json` (`tiempo_manual_s`, `tiempo_automatizado_s`); registrar la salida como evidencia.

## 2. A2 — Fórmula, rango y recálculo del tamaño del efecto

- [x] 2.1 En `S/04-marco-metodologico.tex:65-69` corregir la fórmula a `r=(T+−T−)/(n(n+1)/2)` (equivalente `1−4W/(n(n+1))` si `W=T−`) y el rango verdadero (no `[-1,+1]`); verificar con `rg -n "1 - \\\\frac\\{2W\\}" S/04-marco-metodologico.tex` que la fórmula vieja no queda.
- [x] 2.2 En `S/07-resultados.tex:32-36` recalcular y reportar `r=0,9667` (no `1,00`); verificar con `rg -n "r = 1|1,00|0,9667" S/07-resultados.tex` que `1,00` desaparece y `0,9667` aparece.
- [x] 2.3 **RED** — en `evaluation/tests/test_stats.py` agregar un test que exija `r=(T+−T−)/(n(n+1)/2)` y el reporte de `T+`/`T−`; ejecutar `cd evaluation && pytest tests/test_stats.py` y confirmar que FALLA.
- [x] 2.4 **GREEN** — en `evaluation/stats.py` corregir la fórmula/docstring y exponer `T+`/`T−`; ejecutar `cd evaluation && pytest tests/test_stats.py` y confirmar que PASA.
- [x] 2.5 **TRIANGULATE** — agregar un caso con pares invertidos conocidos (p. ej. 12/200) y verificar que el efecto no es `1,00`; ejecutar `pytest tests/test_stats.py` y confirmar verde.

## 3. A3 — Rótulo de dispersión

- [x] 3.1 En `S/08-discusion.tex:12` cambiar "varianza casi diez veces menor" por "desvío estándar" (los valores comparados son 38,7 s vs 4,1 s); verificar con `rg -n "varianza" S/08-discusion.tex` que el término se corrigió donde corresponde.

## 4. A4 — Aritmética de horas-persona

- [x] 4.1 En `S/08-discusion.tex:14` corregir "180 horas-persona" y añadir nota al pie con el cálculo explícito (real ≈48,1 h con `(61,6−14,8)s×3700/3600`); verificar con `rg -n "180 horas-persona|151,2|48,1" S/08-discusion.tex`.
- [x] 4.2 En `S/09-conclusiones.tex:24` alinear la cifra de horas-persona con la corregida; verificar con `rg -n "180 horas-persona" S/09-conclusiones.tex` que no queda una cifra inconsistente.
- [x] 4.3 En `S/01-introduccion.tex:18` reconciliar "200 horas-persona" con el cálculo declarado; verificar con `rg -n "horas-persona" S/01-introduccion.tex`.
- [x] 4.4 Verificar aritmética con `python3 -c` (3700/42; ahorros con tiempos de tesis y reales; 180 h → s/incidente) y adjuntar la salida.

## 5. A5 — Definición única de intervención humana

- [x] 5.1 En `S/04-marco-metodologico.tex:34,57` y `S/07-resultados.tex:84-86` unificar la definición: reportar proporción de tiempo y de casos de forma rotulada, o elegir una y ser consistente; verificar con `rg -n "intervencion humana|intervención humana" S/04-marco-metodologico.tex S/07-resultados.tex`.

## 6. A6 — Calibración de la confianza

- [x] 6.1 Recalcular y congelar las cifras reales (alta ≥0,70: 0,697=53/76; baja <0,70: 0,758=94/124; errores ≥0,90: 13/46; bandas) con `python3` sobre `evaluation/predicciones.json`; adjuntar la salida.
- [x] 6.2 **RED/GREEN** — en `evaluation/tests/` agregar test de la función de calibración y en `evaluation/metrics.py` (o `run_evaluation.py`) implementar el reporte por bandas y la contingencia; ejecutar `cd evaluation && pytest` y confirmar verde.
- [x] 6.3 Escribir la subsección de calibración en `S/07-resultados.tex` (tabla de contingencia y/o curva); verificar con `rg -n "calibrac|0,697|0,758" S/07-resultados.tex`.
- [x] 6.4 Discutir la implicancia para el gate 0,70 en `S/08-discusion.tex` y referenciar en `S/06-implementacion.tex` (§6.3) y `S/11-aspectos-legales.tex` (§supervisión humana); verificar con `rg -n "calibrac|0,70" S/08-discusion.tex S/06-implementacion.tex S/11-aspectos-legales.tex`.

## 7. A7 — Universo trimestral vs volumen diario

- [x] 7.1 En `S/01-introduccion.tex:18` y `S/04-marco-metodologico.tex:43` declarar los días del trimestre observado y reconciliar `3.700 = 42×88`; verificar con `rg -n "3.700|3\\.700|42 incidentes" S/01-introduccion.tex S/04-marco-metodologico.tex`.

## 8. B1 — Pregunta de investigación sobre el criterio humano

- [x] 8.1 [RESUELTO — OQ2=c] Retirar la sub-pregunta sobre exactitud humana (`S/01-introduccion.tex:28`) y reformular `H1` (`S/01-introduccion.tex:32-34`) para contrastar contra el umbral objetivo (≥85 %), no contra el criterio humano. Verificar con `rg -n "criterio humano|comparable o superior|proceso manual" S/01-introduccion.tex` sin la comparación humana.

## 9. B2 — Tiempo preliminar vs experimental

- [x] 9.1 En `S/01-introduccion.tex:18` y `S/07-resultados.tex:10` explicar la relación entre la medición preliminar (`2 min 45 s`) y la experimental (media real `61,6 s`) y citar el registro que respalda el tiempo; verificar con `rg -n "2 min 45|165,3|61,6" S/01-introduccion.tex S/07-resultados.tex`.

## 10. C1/C2 — Flujo real (verificado, sin cambio)

- [x] 10.1 Confirmar con `rg -n "gate|revision humana|requiere_revision" S/06-implementacion.tex` que §6.3 describe clasificar → gate y ningún LLM telefónico; registrar como "sin cambio" si se confirma (ya alineado por c-72). Verificado: sin cambio.

## 11. C3 — Canal de origen / nombre de campo

- [x] 11.1 Alinear el nombre de campo stale del Cap. 5 (`id_canal` → `canal_origen_id`) en `S/05-arquitectura.tex`; verificar con `rg -n "canal_origen_id|id_canal" S/05-arquitectura.tex`. Documentar que el canal es entrada opcional del backend (`App/Backend/app/schemas/incidente.py:162`).

## 12. C4 — Reintentos (OQ)

- [x] 12.1 [RESUELTO — OQ3=b] Reescrito `S/06-implementacion.tex:60` como limitación conocida + trabajo futuro (NO se implementa el reintento/cola). Verificado: el texto enuncia que "no se implementó un mecanismo de reintento con retroceso exponencial ni una cola de respaldo" y lo declara trabajo futuro; `rg -n "retroceso exponencial|cola de respaldo" S/06-implementacion.tex` solo devuelve la formulación de limitación conocida (línea 60).
- [x] 12.2 (residual, no numerado) `S/06-implementacion.tex:64` afirmaba que ante falla de persistencia "el flujo se reintenta desde ese paso de creación". Verificado en `n8n/workflow.json`: NO existe `retryOnFail` ni `maxTries` en ningún nodo; el nodo `HTTP POST a MESA-AYUDAS` solo declara `onError: continueErrorOutput` (enrutamiento de error, no reintento). Reescrito el párrafo para describir el enrutamiento de error real y declarar la ausencia de reintento automático como limitación conocida.

## 13. C5 — Nginx/TLS (OQ)

- [x] 13.1 [RESUELTO — OQ4=a] Redacción condicional en `S/05-arquitectura.tex:8`, `S/09-conclusiones.tex:10`, `S/11-aspectos-legales.tex:20` y `S/12-anexos.tex:10`: distinguir el diseño (Nginx + TLS 1.2/1.3) del despliegue publicado que no lo incluía. No se despliega el proxy.

## 14. C6 — Residuos de C-18 y anexo del log

- [x] 14.1 [RESUELTO — premisa corregida] Alinear `S/05-arquitectura.tex:20,40` a IMAP/SMTP: se reemplazó "Microsoft Outlook (Graph API)" por IMAP/SMTP. Se conserva IMAP en `S/06-implementacion.tex:37` y `S/12-anexos.tex:37` (ya correctos). Evidencia de artefacto: `n8n/workflow.json` usa `n8n-nodes-base.emailReadImap` (credencial "Mesa de Ayuda - IMAP", mailbox INBOX, `customEmailConfig` con sintaxis IMAP) y contiene CERO `microsoftOutlookTrigger`; `docs/n8n-workflow-guide.md:152` documenta que "C-55 ratifica IMAP" (C-55, BREAKING, migró el canal correo de Microsoft Outlook/Graph a IMAP/SMTP). Verificar con `rg -ni "outlook|graph api" S/05-arquitectura.tex S/06-implementacion.tex S/12-anexos.tex` sin resultados.
- [x] 14.2 Cerrar el catálogo stale de sectores en `S/05-arquitectura.tex:76` y `S/01-introduccion.tex:46,68`; verificar `rg -n "tres sectores|Operaciones" S/05-arquitectura.tex S/01-introduccion.tex`. Ya alineado (c-76): 05:76 "cinco sectores canónicos", 01:46 "cinco sectores canónicos", 01:68 "cinco sectores de derivación". El barrido case-sensitive devuelve cero coincidencias.
- [x] 14.3 Adjuntar `docs/Tesis/Correcciones/dictamen-correcciones.md` como anexo (nuevo `\section{Trazabilidad de las correcciones del dictamen}` en `S/12-anexos.tex`) como ejemplo de trazabilidad; verificar con `rg -n "dictamen|decisiones" S/12-anexos.tex`.

## 15. C7 — Sectores del prompt (OQ)

- [x] 15.1 [RESUELTO — OQ5=b] Alinear la TESIS a los 5 sectores canónicos de `docs/prompt_gemini.txt` (NO tocar el prompt). Aplicar en `S/01-introduccion.tex`, `S/04-marco-metodologico.tex`, `S/05-arquitectura.tex` y Cap. 7; coordinar con c-76; verificar `rg -ni "tres sectores|Operaciones" S/`. Ya alineado (c-76): 01:46/68 describe los cinco sectores canónicos y 05:76 el catálogo de cinco. El barrido case-sensitive `rg -n "tres sectores|Operaciones" S/` devuelve CERO coincidencias. El barrido case-insensitive (`-i`) solo marca usos legítimos no relacionados con el catálogo stale ("área de operaciones" 01:16, "operaciones CRUD" 06:72, "operaciones de servicio" 02:16, "operaciones" 02:52/12:47); no se reescriben por ser prosa correcta.

## 16. C8 — Tag inexistente (OQ)

- [x] 16.1 [RESUELTO — OQ6=diferido] NO crear tag ahora (verificado: no se creó ningún tag). Acción pendiente documentada en `S/12-anexos.tex:19`: al finalizar c-76+c-77, crear el tag `v1.0.0` sobre el commit entregado al jurado y consignar el hash completo en este apartado. Verificar con `rg -n "v1\.0\.0" S/12-anexos.tex`.

## D1 — Descripción de metadata del corpus

- [x] D1.1 En `data/corpus_evaluacion_pseudonimizado.json`, en `metadata.descripcion`, eliminar la cláusula falsa "tiempos automatizados pendientes de medicion end-to-end" y declarar que los 200 tiempos automatizados están medidos end-to-end (los tiempos manuales son los de clasificación manual); corregir solo la cadena, sin alterar valores numéricos ni el total de casos. Verificar con `rg -n "pendientes de medicion" data/corpus_evaluacion_pseudonimizado.json` sin resultados y con `python3 -c "import json; json.load(open('data/corpus_evaluacion_pseudonimizado.json'))"` confirmando JSON válido.

## Grupo E — Tiempo automatizado telefónico comparable (Opción A)

> Decisión del autor (2026-10-12): implementar la Opción A dentro de c-77. Este grupo es
> SOLO planificación en esta ronda: c-77 no se aplica aquí.
> Fórmula: `tiempo_automatizado_s(telefono) = duracion_segundos + latencia_e2e_ms/1000`.
> COTA INFERIOR: la grabación está acotada a 45 s (`<Record maxLength="45">`,
> `n8n/twilio/twiml.xml`), así que `duracion_segundos` subestima la duración real.
> Cross-reference: la figura 7 de c-80 (boxplot por canal) consume esta métrica y c-80
> aplica AFTER c-77 (orden c-76 -> c-77 -> c-78 -> c-79 -> c-80).

- [x] E1.1 **RED** — en `App/Backend/tests/` agregar un test que exija `duracion_segundos` en `TelefoniaIngresoRead` (`App/Backend/app/schemas/telefonia.py:69-87`) y su proyección en `_ingreso_to_read` (`App/Backend/app/routes/telefonia.py:249-258`); ejecutar `cd App/Backend && pytest -m "not integration"` y confirmar que FALLA.
- [x] E1.2 **GREEN** — agregar el campo opcional `duracion_segundos` al schema y proyectarlo en `_ingreso_to_read`; ejecutar `pytest -m "not integration"` y confirmar que PASA.
- [x] E1.3 Regenerar `docs/openapi.json` con el comando canónico del proyecto y verificar `cd App/Backend && pytest tests/test_openapi_sync.py -v` verde.
- [x] E2.1 Prerrequisito de datos: restaurar `backups/vol_mesa_local_postgres_corpus_data_20261009T141330.tgz` en una instancia Postgres desechable y confirmar que `duracion_segundos` es legible para los 81 casos telefónicos. Registrar la evidencia (los 119 casos de web/correo no se leen para este cálculo).
- [x] E2.2 **RED** — en `scripts/corpus_ingest/` (o su suite de tests) agregar un test que exija `derive_telefonia_metric`/`build_telefonia_result` (~:85-134) devolviendo `duracion_segundos + latencia_e2e_ms/1000`; ejecutar y confirmar que FALLA.
- [x] E2.3 **GREEN** — implementar la derivación en `scripts/corpus_ingest/ingest_telefonia_corpus.py` y recomputar los 81 casos; ejecutar y confirmar que PASA.
- [x] E2.4 **TRIANGULATE** — agregar un caso con `duracion_segundos` ausente/nulo (no debe romper ni sumar un valor ficticio) y un caso con duración en el tope (45 s) para verificar la cota inferior; ejecutar y confirmar verde.
- [x] E3.1 Actualizar las 81 filas telefónicas en `data/corpus_evaluacion_pseudonimizado.json` y el sidecar `data/corpus_resultados_telefonia.json`; verificar JSON válido y el total de 200 casos con `python3 -c "import json; json.load(open('data/corpus_evaluacion_pseudonimizado.json'))"`.
- [x] E4.1 Confirmar con un test/aserción que los tiempos de web y correo NO cambian (siguen siendo la latencia end-to-end previa); registrar la salida.
- [x] E5.1 Reconciliar `S/07-resultados.tex` (tabla de tiempos por canal) con el valor telefónico corregido y declarar la cota inferior; si `S/04-marco-metodologico.tex` describe el tiempo automatizado telefónico, alinearlo. Verificar con `rg -n "duracion|grabacion|llamada|cota inferior|45" S/07-resultados.tex S/04-marco-metodologico.tex`.
- [x] E5.2 Registrar explícitamente el tope de 45 s y la cota inferior en la nota metodológica de la tesis (y en `design.md` como riesgo, ya registrado).
- [x] E5.3 Reconciliación global (decisión del autor A): aplicar el mapeo OLD→NEW (media 14,8→17,76 s; mediana 12,4→17,47 s; desvío 13,1→13,48 s; reducción 75,9→71,2 %; Wilcoxon W 335→363, T+ 19.765→19.737, T− 335→363, p 2,05e-32→3,08e-32, r 0,9667→0,9639; horas-persona 48,1→45,0 h; telefónico 12,83→20,09 s) en `S/07-resultados.tex`, `S/08-discusion.tex`, `S/09-conclusiones.tex`, `S/00-resumen.tex`, `S/01-introduccion.tex` y `S/06-implementacion.tex`; barrido de control con `rg -n "14,8|75,9|0,9667|19765|2,05e-32|335|12,4|13,1|48,1|12 a 15" S/` sin residuos en contexto de tiempo.
- [x] E6.1 Extender `specs/evaluation-framework/spec.md` con el requerimiento/escenario del tiempo automatizado telefónico (incluye duración de llamada/grabación; web/correo sin cambio; cota inferior) y `specs/tesis-document/spec.md` con el escenario de declaración de cota inferior. Verificado: los requerimientos ya están presentes y conformes — `evaluation-framework` declara el requerimiento "Medición comparable del tiempo automatizado telefónico" con la fórmula `duracion_segundos + latencia_e2e_ms/1000`, la cota inferior por el tope de 45 s (`<Record maxLength="45">`) y los escenarios "Tiempo telefónico incluye la duración de la llamada", "Web y correo sin cambio" y "Duración de grabación ausente"; `tesis-document` declara el requerimiento "Declaración del tiempo automatizado telefónico como cota inferior" con los escenarios "Cota inferior declarada" y "Web y correo sin cambio" (añadidos en c5fe5a2 al cerrar las OQ del Grupo E). Se confirmó con `rg` que las tres condiciones están cubiertas y que el formato requirement/scenario es consistente con el resto del archivo.
- [x] E6.2 Verificar que el corpus de web/correo (119 casos) no fue tocado y que no se modificó el `metadata.descripcion` por encima de D1; `rg`/`git diff --stat` sobre `data/`. Evidencia: `git diff --stat -- data/` reporta `1 file changed, 82 insertions(+), 82 deletions(-)` sobre `data/corpus_evaluacion_pseudonimizado.json` (82 = 81 filas telefónicas + 1 línea de `metadata.descripcion`). Comparación estructurada HEAD↔worktree: 200 casos con los mismos ids; 81 filas cambiadas, TODAS del canal "llamada telefónica" y con el ÚNICO campo `tiempo_automatizado_s` modificado; las 119 filas restantes (53 "formulario web" + 66 "correo electrónico") son idénticas byte a byte a HEAD. `metadata.total_casos` sigue en 200; `metadata.descripcion` cambió solo por D1 (se eliminó la cláusula falsa "tiempos automatizados pendientes de medicion end-to-end"). JSON válido con 200 casos.
- [x] E7.1 Verificación del grupo: `cd App/Backend && pytest -m "not integration"` + `pytest tests/test_openapi_sync.py -v` verde; `openspec validate c-77-tesis-errores-estadisticos-inferenciales --strict` verde. Evidencia: backend `1441 passed, 48 deselected, 1 xfailed` (335,32 s); `test_openapi_sync.py` `5 passed`; `openspec validate --strict` -> "Change 'c-77-...' is valid".

## 17. Verificación final y recompilación

- [x] 17.1 Ejecutar el barrido de control `rg -n "W = 0|r = 1,00|varianza casi diez|180 horas-persona|IMAP|tres sectores" S/` y confirmar que no quedan residuos (o que los restantes están justificados). Evidencia: CERO coincidencias de `W = 0`, `r = 1,00`, `varianza casi diez` y `tres sectores`. Residuos justificados: `IMAP` en 05:20, 05:40, 06:37 y 12:37 (alineación de canal correo a IMAP/SMTP verificada por C-18/C-55, según tarea 14.1) y `180 horas-persona` en 08:14 (aparece SOLO dentro de la nota al pie que documenta explícitamente que la cifra previa no era reproducible; no es un residuo activo).
- [x] 17.2 Ejecutar `cd evaluation && pytest tests/test_stats.py` más el test de calibración y confirmar verde. Evidencia: `pytest tests/test_stats.py tests/test_calibracion_confianza.py -q` -> `12 passed`.
- [x] 17.3 Recompilar la tesis (`main.tex`, XeLaTeX; localmente con MiKTeX) y verificar PDF sin errores fatales; registrar el resultado. — COMPLETADO 2026-10-20: recompilado localmente con MiKTeX (xelatex -> biber -> xelatex -> xelatex); 103 paginas; 0 errores fatales; 0 referencias indefinidas; 48/48 bibliografia; las 8 figuras renderizan. (latexmk no disponible: MiKTeX sin Perl.)
- [x] 17.4 Ejecutar `openspec validate c-77-tesis-errores-estadisticos-inferenciales --strict` y confirmar que pasa. Evidencia: "Change 'c-77-tesis-errores-estadisticos-inferenciales' is valid" (exit 0).
