## Why

Cada ejecucion de `evaluation/run_evaluation.py` re-invoca el clasificador sobre todos los casos del corpus, lo que puede generar hasta ~200 llamadas pagas a Gemini aunque el corpus y la configuracion del clasificador no hayan cambiado. Ademas, `docker-compose.yml` usa `n8nio/n8n:latest`, lo que expone la pila a roturas silenciosas en el siguiente `docker compose pull`. Por ultimo, `App/Backend/.env.example` expone variables Twilio que ningun modulo del backend utiliza, induciendo a error a quienes operan el sistema.

## What Changes

- **A1 — Cache de predicciones en el runner de evaluacion**: antes de invocar el clasificador, `main_con_corpus_real` verifica si `predicciones.json` fue producido con el mismo corpus (hash SHA-256 del archivo JSON + cantidad de casos) y la misma clave de configuracion del clasificador; si el cache es valido, carga las predicciones y omite las llamadas al clasificador. La invalidacion ocurre automaticamente ante cualquier cambio en el corpus o en la config. Se agrega una bandera `--force` / `--no-cache` para saltar el cache. Gobernanza LOW (solo afecta el modulo de evaluacion, sin superficie de produccion).
- **A2 — Pin de imagen N8N a 2.11.2**: se reemplaza `n8nio/n8n:latest` por `n8nio/n8n:2.11.2` en `docker-compose.yml`. Se actualiza el comentario de la linea para reflejar la version fijada y su razon. Gobernanza MEDIUM (config que afecta el workflow N8N activo).
- **A4 — Comentar variables Twilio en `.env.example`**: las cuatro variables `TWILIO_*` se comentan con una nota que indica que esas credenciales pertenecen a la configuracion de N8N, no al backend. Se elige comentar (opcion b) en lugar de eliminar para que el archivo siga siendo una referencia completa del entorno. La decision queda registrada en `design.md`.

## Capabilities

### New Capabilities

- `evaluation-prediction-cache`: comportamiento del cache de predicciones en el runner de evaluacion — cuándo se usa el cache, cuándo se invalida y como se omite con `--force`.

### Modified Capabilities

None

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `evaluation/run_evaluation.py` | Modified | Logica de cache agregada a `main_con_corpus_real`; nuevo flag `--force` en el punto de entrada CLI |
| `evaluation/predicciones.json` | Modified | El archivo pasa a tener un campo de metadata de cache ademas de las predicciones |
| `docker-compose.yml` | Modified | Imagen N8N fijada a `n8nio/n8n:2.11.2` |
| `App/Backend/.env.example` | Modified | Variables `TWILIO_*` comentadas con nota explicativa |
| `evaluation/tests/` | New tests | Tests TDD para los tres escenarios del cache (hit, invalidacion, force) |
