# Proposal: Bloquear la siguiente llamada hasta procesar la anterior en el softphone

## Why

El brazo de telefonia de la campana (c-169) mide casos del corpus con el softphone de desarrollo (`scripts/voip_softphone/`). El backend procesa cada grabacion de forma SINCRONA (descarga + STT + pseudonimizacion + handoff a n8n + alta del incidente, ~6-7 s medidos). Si dos llamadas se procesan a la vez, la contencion infla `latencia_e2e_ms` (`persistido_en - ingresado_en`) y sesga la medicion. Hoy el no-solapamiento depende solo de la cadencia natural del operador (~40-60 s de recitado), no esta impuesto por la herramienta: la pagina rehabilita el boton Call en el evento `disconnect`.

## What Changes

- Nueva sonda de estado server-side en el modo `serve` del servidor de loopback: `GET /case-status?case_id=<id>&since=<epoch_ms>` que autentica contra el backend, cachea el JWT y consulta el endpoint EXISTENTE `GET /api/v1/telefonia/ingresos?corpus_case_id=<id>&latest=true`; responde `{listo, transcripcion_estado, incidente_id, latencia_e2e_ms}`.
- Gate en la UI: con un caso del corpus seleccionado, tras `disconnect` la pagina entra en estado "procesando", deshabilita Call, consulta la sonda cada ~2 s con timeout acotado (~60 s) y rehabilita Call solo cuando el caso quedo procesado (incidente persistido). Sin caso seleccionado (modo desarrollo) el comportamiento NO cambia.
- Config nueva para `serve`: `--backend-base-url` (default `https://localhost`), `--insecure` y credenciales del operador reutilizadas del entorno del harvest (`INGEST_OPERATOR_USERNAME` / `INGEST_OPERATOR_PASSWORD`).
- Documentacion minima del gate en `scripts/voip_softphone/README.md` y referencia cruzada en `docs/campana-medicion/guia-ejecucion-campana.md` (sin duplicar el README).
- NO se modifica el backend (`App/Backend/**`): la sonda consume el endpoint existente.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `telephony-test-softphone`: se agrega el bloqueo de la siguiente llamada hasta procesar la anterior y la sonda de estado por loopback; el retorno a reposo tras colgar pasa a ser condicional a que no haya un caso seleccionado.

## Impact

- Codigo: `scripts/voip_softphone/mint_token.py`, `scripts/voip_softphone/softphone.html`.
- Tests a extender: `scripts/voip_softphone/{test_serve.py, test_softphone_html.py, test_mint_token.py, test_corpus_cases.py}`.
- Docs: `scripts/voip_softphone/README.md`, `docs/campana-medicion/guia-ejecucion-campana.md`.
- Sin cambios en el backend, el esquema de base de datos ni los datos de la tesis. Governance MEDIUM (tooling de desarrollo).
