# Tasks: Bloqueo de la siguiente llamada hasta procesar la anterior (c-174)

Modo Strict TDD: cada tarea de implementacion respeta el ciclo RED -> GREEN -> TRIANGULATE -> REFACTOR. Todo el trabajo vive en `scripts/voip_softphone/`. Suite offline: `python3 -m pytest scripts/voip_softphone -q`.

## 1. Sonda: decision pura `evaluate_case_status` (`mint_token.py`)

- [x] 1.1 RED: agregar en `test_mint_token.py` un test que, dado un ingreso con `incidente_id` no nulo, espere `{"listo": true, "incidente_id": <id>, "latencia_e2e_ms": <ms>, "transcripcion_estado": "transcrito"}`. Verificacion: `pytest scripts/voip_softphone/test_mint_token.py -q` falla (funcion inexistente).
- [x] 1.2 GREEN: implementar `evaluate_case_status(payload, since_ms)` con lo minimo para pasar 1.1. Verificacion: el test de 1.1 pasa.
- [x] 1.3 TRIANGULATE: agregar tests para `payload=None` (404) -> `listo=false` con campos nulos; `incidente_id` nulo -> `listo=false`; `transcripcion_estado="error_stt"` -> `listo=false` exponiendo el estado. Verificacion: los tres tests pasan.
- [x] 1.4 TRIANGULATE (reintento): agregar tests de que `since_ms` posterior a `ingresado_en` -> `listo=false` (ingreso previo stale) y `since_ms` anterior o igual -> `listo=true`. Verificacion: ambos pasan; cubre la decision D3.
- [x] 1.5 REFACTOR: extraer el parseo de `ingresado_en` (ISO -> epoch ms) y la comparacion a helpers; re-ejecutar 1.1-1.4 verdes.

## 2. Sonda: configuracion y transporte (`mint_token.py`)

- [x] 2.1 RED: test de `load_probe_config(environ, backend_base_url, insecure)` que lee `INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD` y refleja la URL base y `insecure`; ausentes -> `None`. Verificacion: falla por inexistente.
- [x] 2.2 GREEN: implementar `ProbeConfig` y `load_probe_config` minimos. Verificacion: 2.1 pasa.
- [x] 2.3 TRIANGULATE: credenciales parciales -> `ConfigError` con mensaje claro; el `repr`/str de la config NO expone la password. Verificacion: tests pasan.
- [x] 2.4 RED: test del transporte con `opener` inyectable (monkeypatched): `login_backend` extrae `access_token`; `fetch_ingreso` devuelve `(status, payload)`; 404 -> payload `None`. Verificacion: falla por inexistente.
- [x] 2.5 GREEN: implementar `login_backend` y `fetch_ingreso` con `urllib.request` + `ssl` (CERT_NONE si `insecure`). Verificacion: 2.4 pasa sin red real.
- [x] 2.6 TRIANGULATE: 401 dispara UN re-login y reintento; 5xx se propaga como error de la sonda. Verificacion: tests pasan.

## 3. Endpoint `GET /case-status` del servidor de loopback (`mint_token.py`)

- [x] 3.1 RED: en `test_serve.py`, con una sonda fake inyectada, `GET /case-status?case_id=T1&since=...` responde 200 con el JSON `{listo, transcripcion_estado, incidente_id, latencia_e2e_ms}`. Verificacion: falla (ruta inexistente).
- [x] 3.2 GREEN: agregar `probe_config` a `build_server`/`make_handler` y rutear `/case-status` en `do_GET`. Verificacion: 3.1 pasa.
- [x] 3.3 TRIANGULATE: sin `case_id` -> 400; sonda sin configurar -> 503 con sobre `{"error":{"code":"probe_unconfigured",...}}`; una ruta desconocida sigue devolviendo 404. Verificacion: los tests pasan.
- [x] 3.4 TRIANGULATE: el endpoint no escribe descripciones ni contenido de caso en stdout/stderr (capfd). Verificacion: test pasa.

## 4. Compatibilidad con el servidor de corpus (`test_corpus_cases.py`)

- [x] 4.1 RED/GREEN: extender el fixture de servidor de `test_corpus_cases.py` para recibir `probe_config` y verificar que el MISMO servidor sirve `/corpus-cases` y `/case-status` sin interferencia. Verificacion: el listado de casos y la sonda responden lo esperado; tests verdes.

## 5. Gate en la UI (`softphone.html`)

- [x] 5.1 RED: en `test_softphone_html.py`, agregar un test estructural que exija: funcion/estado de procesamiento, `fetch("/case-status`, deshabilitar Call en el estado de procesamiento y una constante/mensaje de "procesando". Verificacion: falla.
- [x] 5.2 GREEN: implementar en la pagina la maquina de estados D6 (procesando, disable Call, poll ~2 s, timeout ~60 s) y el envio de `case_id`/`since`. Verificacion: 5.1 pasa.
- [x] 5.3 TRIANGULATE: con caso -> tras `disconnect` no se rehabilita Call hasta `listo`; sin caso -> `disconnect` vuelve a reposo sin polling; `listo=true` -> Call re-habilitado con mensaje. Verificacion: tests estructurales del cuerpo de los handlers pasan.
- [x] 5.4 TRIANGULATE: al agotar el timeout se muestra advertencia y se rehabilita Call; el temporizador de polling se cancela (sin timers huerfanos); la consulta incluye `case_id` y `since`. Verificacion: tests pasan.
- [x] 5.5 REFACTOR: extraer helpers (`pollCaseStatus`, `enterProcessing`, `leaveProcessing`) manteniendo 5.1-5.4 verdes.

## 6. Cableado del CLI `serve` (`mint_token.py`)

- [x] 6.1 RED/GREEN: `serve` acepta `--backend-base-url` (default `https://localhost`) y `--insecure`, y propaga un `ProbeConfig` a `build_server`. Verificacion: test de parser/`run` pasa.
- [x] 6.2 TRIANGULATE: los defaults son los esperados y `--insecure` se refleja en la config. Verificacion: tests pasan.

## 7. Documentacion

- [x] 7.1 `scripts/voip_softphone/README.md`: documentar el gate, `GET /case-status`, los flags `--backend-base-url`/`--insecure` y el prerequisito de `INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD`. Verificacion: seccion nueva presente y coherente con la implementacion.
- [x] 7.2 `docs/campana-medicion/guia-ejecucion-campana.md`: agregar una referencia cruzada minima (el detalle vive en el README del softphone; no duplicar). Verificacion: referencia presente.

## 8. Verificacion final

- [x] 8.1 Ejecutar `python3 -m pytest scripts/voip_softphone -q` y confirmar toda la suite verde (incluye `test_serve.py`, `test_softphone_html.py`, `test_mint_token.py`, `test_corpus_cases.py`, `test_setup_twilio.py`).
- [x] 8.2 Ejecutar el linter del repositorio sobre la herramienta y confirmar sin hallazgos nuevos.
- [x] 8.3 Verificacion MANUAL (operador, fuera de la suite offline): con el stack y el backend arriba, seleccionar un caso, colocar una llamada y confirmar que Call queda deshabilitado hasta que el incidente quede persistido; sin caso, confirmar el comportamiento previo. (Verificado 2026-11-06: con caso R076 -> incidente 121, el gate mantuvo Call deshabilitado hasta persistir; sin caso -> incidente 122, comportamiento previo.)
