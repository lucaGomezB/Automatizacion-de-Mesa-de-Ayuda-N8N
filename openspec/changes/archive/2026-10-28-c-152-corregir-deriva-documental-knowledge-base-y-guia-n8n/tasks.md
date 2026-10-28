## 1. Verificacion previa de estado

- [x] 1.1 Re-verificar contra `openspec/changes/archive/` que `C-02`, `C-04`, `C-05` y `C-17` siguen archivados y confirmar en `CHANGES.md` que sus preguntas quedaron resueltas; verificar que el resultado coincide con el design D3 antes de editar cualquier archivo.

## 2. Corregir la base de conocimiento

- [x] 2.1 En `knowledge-base/07_flujos_principales.md` corregir la linea 11 (`*(Pendiente C-02)*` en el Flujo 1) al estado real implementado, preservando el hecho historico de que en su momento estaba pendiente; verificar por inspeccion que el Flujo 1 ya no rotula `C-02` como pendiente.
- [x] 2.2 En `knowledge-base/07_flujos_principales.md` corregir los encabezados de los Flujos 2 y 3 (lineas 26 y 36) que declaran "(pendiente C-04/C-05)" y "(pendiente C-05)"; declarar el estado implementado real y conservar el contexto historico rotulado; verificar que ninguno de los dos encabezados presenta el flujo como pendiente.
- [x] 2.3 En `knowledge-base/10_preguntas_abiertas.md` marcar como resueltas/cerradas las preguntas de las lineas 41 (CSV del corpus, `C-17`), 43 (credenciales Outlook/Twilio, `C-05`) y 45 (instancia N8N de pruebas, `C-02`); verificar que la tabla de preguntas abiertas no lista como pendiente ninguna pregunta cuyo change ya este archivado.
- [x] 2.4 Confirmar por inspeccion que las correcciones 2.1-2.3 no borran las afirmaciones de estado originales cuando son evidencia historica, sino que las reencuadran (conforme al requisito de no reescritura).

## 3. Rotular el registro historico de la guia N8N

- [x] 3.1 En `docs/n8n-workflow-guide.md` incorporar un marcador de `MARCADORES_HISTORICOS` en el encabezado del bloque "Resultados de verificacion 7.1-7.6 (2026-06-11, C-05)" (linea 765), de modo que la seccion completa quede rotulada como historica; verificar que el encabezado contiene al menos uno de los tokens reconocidos (`historico`, `historica`, `antecedente`, `superad`, `migro`, `migrado`, `retirado`, `previo`, `calibrad`).
- [x] 3.2 Verificar por inspeccion que la linea 767 (`N8N 2.25.7`) queda dentro del pasaje historico rotulado y que el texto original del registro (contenido y fecha) se conserva sin reescribirse; confirmar que no se reemplaza `2.25.7` por `2.11.2`.
- [x] 3.3 Confirmar que la version vigente de N8N declarada en el resto de la guia (lineas 505 y 575) sigue coincidiendo con la imagen pinneada `n8nio/n8n:2.11.2` de `docker-compose.yml` y que el encabezado de la seccion vigente no recibio el marcador historico.

## 4. Verificacion final

- [x] 4.1 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` y verificar que termina con codigo 0 (sin nuevos hallazgos respecto de la linea base).
- [x] 4.2 Ejecutar `python3 -m pytest scripts/preflight -q` y verificar que la suite sigue en verde.
- [x] 4.3 Ejecutar `openspec validate "c-152-corregir-deriva-documental-knowledge-base-y-guia-n8n" --strict --no-interactive` y verificar que el change valida sin errores.
- [x] 4.4 Revisar `git diff` de los tres archivos tocados y verificar que no hay emojis, que el texto esta en espanol tecnico neutral, y que no se modificaron los cinco identificadores canonicos de sector, los valores de `gemini-3.6-flash`, `requirements.txt`, `openspec/config.yaml` ni codigo de `App/`.
