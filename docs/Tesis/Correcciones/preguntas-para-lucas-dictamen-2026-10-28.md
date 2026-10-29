# Preguntas para Lucas - dictamen CONEAU del 2026-10-28 (changes c-158 a c-160)

Son los datos que la tesis necesita y que el repositorio no documenta. Cada respuesta cierra un marcador `% PENDIENTE AUTORES` en las fuentes LaTeX (Q1-Q5 en `04-marco-metodologico.tex`, Q7 en `12-anexos.tex`) o una entrada PENDIENTE del registro `dictamen-correcciones.md`. Si algo no se recuerda o no se conservo, la respuesta valida es "no consta": la tesis lo declara asi y no se inventa.

## Bloque 1 - Corrida de tiempos de correo y formulario web (2 de octubre)

- **Q4. Quien corrio el harness y como.** Quien ejecuto `scripts/corpus_ingest/ingest_via_n8n.py` el 2-10-2026, con que flags (sobre todo `--source`: JSON pseudonimizado o CSV/XLSX), contra que stack (`--base-url`, perfil de Compose) y que host SMTP (remitente, destinatario, servidor).
- **Q5. Intervalo real del buzon.** El flujo declara `everyMinute` en el nodo IMAP, pero en n8n 2.11.2 ese parametro parece no tener efecto y no hay medicion del intervalo efectivo. Sabes cada cuanto levantaba el buzon la instancia del 2-10 (o si fue por eventos IMAP)?
- **Q8. Nginx.** La tesis dice que el despliegue de la campana no incluyo el proxy, pero el harness lee por defecto a traves de nginx (`https://localhost`). Estaba nginx activo el 2-10, aunque fuera del tramo medido?

## Bloque 2 - Corrida telefonica (5 y 6 de octubre)

- **Q1. Fechas y horas.** El historial muestra 25 casos ya medidos el 5-10 (antes de c-71 y c-72) y 56 el 6-10. Confirmas que la corrida telefonica empezo el 5-10 y termino el 6-10, y a que horas aproximadas cada tramo? Si se confirma, 1.8, 4.5, la Figura 10 y el cronograma pasan a decir "5 y 6 de octubre".
- **Q2. Version desplegada para los 56 casos del 6-10.** Que imagen de `backend-corpus` y que flujo importado en `n8n-corpus` procesaron esos casos: anteriores o posteriores a c-71 (`1368fd8`, 5-10 21:50) y a c-72 (`a76851e`, 6-10 16:38)? Se reimporto el flujo de `n8n-corpus` despues de retirar el AI Agent?
- **OQ4. AI Agent de N8N.** Los 25 casos del 5-10 se clasificaron con el AI Agent de N8N (Gemini siempre). Los 81 tiempos telefonicos incluyen esa etapa, o alguno se midio con la cascada del backend?
- **Q3. Quien recito y en que condiciones.** Nombre de quien recito las 81 llamadas, si fue una sola persona, si leyo la descripcion tal como la mostraba el softphone (literal) o la parafraseo, dispositivo, microfono, red y entorno (lugar silencioso o no), y si hubo repeticiones ademas de R126 y R002.

## Bloque 3 - Registros y evidencia

- **Q7. Registros primarios.** Se conservan fuera del repo la base operativa del 2-10, el respaldo del 9-10 con los 81 ingresos telefonicos, los sidecars `data/corpus_resultados_n8n*.json` y las ejecuciones de N8N? Si si, podemos versionar una exportacion pseudonimizada (id de caso y marcas temporales)? Si no, la tesis dira "no se conservaron" (solo con tu confirmacion).
- **Q6. Hash del corpus.** La `cache_meta` de `hybrid-v3` quedo asociada al hash `1fd17d7e...` del corpus del 19-10, no al del 9-10 (`5f062e14...`), sin reclasificar. Como se hizo esa reasociacion? Solo cambia el registro, no la tesis.

## Bloque 4 - Decisiones de redaccion y hallazgo nuevo

- **OQ1. Naturaleza de los dictamenes.** El Anexo I ahora dice que los dictamenes son revisiones previas a la defensa pedidas por los autores, con el perfil `Prompt2.docx` aplicado mediante un modelo de lenguaje, no vinculantes. Estas de acuerdo con declararlo asi?
- **OQ5 / hallazgo.** `n8n/workflow.json` no envia `reportante_email` ni `reportante_telefono` en el `POST /api/v1/incidentes`. En la version entregada, todo incidente de correo o telefonia que entre por N8N quedaria sin reportante identificado y derivado a revision humana (VIS-005). No lo verificamos en ejecucion: es asi en el stack real? Si lo es, hay que decidir si se corrige el flujo o se declara en la tesis.
- **Figura 2.** Se reemplazo por un diagrama Mermaid nuevo de cinco capas y tres canales (`docs/diagrams/arquitectura_sistema.md`); tu `Diagrama de Capas.drawio` esta desactualizado (N8N 1.62, Gemini 2.5, sin frontend). Preferis actualizar el drawio en lugar del Mermaid?
