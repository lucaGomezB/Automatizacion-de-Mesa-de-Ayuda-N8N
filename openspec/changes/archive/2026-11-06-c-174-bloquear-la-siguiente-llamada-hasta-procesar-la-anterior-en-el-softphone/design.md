# Design: Bloqueo de la siguiente llamada hasta procesar la anterior (c-174)

## Context

Ver `proposal.md` para la motivacion. Estado actual y restricciones que moldean el diseno:

- La pagina (`scripts/voip_softphone/softphone.html`) y el token se sirven del MISMO origen de loopback (`127.0.0.1:8765`); hoy la pagina rehabilita Call en el evento `disconnect` del `Call` resuelto por `device.connect()` (`setConnected(false)`, lineas ~64-67 y ~172-175).
- El endpoint de lectura existe y NO debe modificarse: `GET /api/v1/telefonia/ingresos?corpus_case_id=<id>&latest=true` (rol `administrador_directorio`), que devuelve `TelefoniaIngresoRead` con `id`, `call_sid`, `corpus_case_id`, `transcripcion_estado`, `ingresado_en`, `persistido_en`, `incidente_id`, `latencia_e2e_ms`, `duracion_segundos`. Un `corpus_case_id` sin ingreso responde 404.
- El login del harvest es el contrato a reutilizar: `POST /api/v1/auth/login` con `{"username","password"}` -> `{"access_token"}` (`scripts/corpus_ingest/ingest_via_n8n.py::login`). Credenciales: `INGEST_OPERATOR_USERNAME` / `INGEST_OPERATOR_PASSWORD`. URL base por defecto `https://localhost`; certificado autofirmado -> opcion `--insecure` (verify=False + `urllib3.disable_warnings()`).
- `curl`/navegador del operador y backend corren en la MISMA maquina (tooling de desarrollo): relojes compartidos, skew despreciable.
- Restriccion dura: NO tocar `App/Backend/**`. Governance MEDIUM.
- La herramienta de softphone hoy es stdlib + `twilio` (sin `requests`).

## Goals / Non-Goals

**Goals:**

- Convertir el no-solapamiento de "disciplina del operador" a "impuesto por la herramienta", sin dejar nunca atrapado al operador.
- Reutilizar el endpoint y el login existentes; cero cambios de backend.
- Disenar la decision "procesado/no procesado" como logica pura y testeable offline.

**Non-Goals:**

- No medir ni alterar la metrica `latencia_e2e_ms`; el gate solo serializa las llamadas.
- No agregar endpoints de backend (por `CallSid` u otros).
- No introducir una cola, un lock distribuido ni un servicio nuevo.
- No cambiar el modo de desarrollo sin caso (retrocompatible con C-59/C-70).

## Decisions

### D1 - Sonda server-side en el servidor de loopback, no desde el navegador

El modo `serve` expone `GET /case-status`; el navegador solo consume ese endpoint del MISMO origen. Razones: (1) los secretos (credenciales del operador y JWT) quedan server-side y nunca llegan a la pagina; (2) el origen del navegador es `127.0.0.1:8765` y el backend es otro host, por lo que un `fetch` directo exigiria CORS y exponer credenciales; (3) el certificado autofirmado ya se maneja server-side con `--insecure`.
Alternativa considerada y descartada: `fetch` directo del navegador al backend.

### D2 - Reutilizar el endpoint de ingreso existente; "procesado" = ingreso con incidente

`listo = (existe ingreso) AND (incidente_id no es nulo)`, equivalente a `latencia_e2e_ms` no nulo. Un 404 (sin ingreso) => `listo=false`. Alternativa considerada y descartada: endpoint backend por `CallSid` (fuera de alcance, ver D3).

### D3 - RESOLUCION DEL REINTENTO: comparacion temporal con `since` (opcion a)

**Recomendacion: opcion (a), comparacion de `ingresado_en` contra un `since` provisto por la pagina (el instante de INICIO de la llamada en curso).**

Contrato: la pagina captura `since = Date.now()` al presionar Call y lo envia como `GET /case-status?case_id=<id>&since=<epoch_ms>`. El servidor descarta cualquier ingreso cuyo `ingresado_en < since` (ingreso de una corrida PREVIA) y solo cuenta un ingreso con `ingresado_en >= since`.

Justificacion:

- El backend sella `ingresado_en` en la recepcion del callback de grabacion, que ocurre DESPUES del colgado. Por lo tanto un ingreso NUEVO siempre cumple `ingresado_en >= since` con un margen amplio (la duracion de la llamada: segundos), y un ingreso PREVIO siempre cumple `ingresado_en < since`. La comparacion es unidireccional y con holgura.
- En este tooling el backend y el navegador corren en la misma maquina: el skew de reloj es despreciable.
- No depende de la exposicion de `CallSid` al navegador por parte del SDK de Twilio, ni de un endpoint de backend nuevo.
- La comparacion vive server-side (recibe `since` como parametro), lo que la vuelve unitariamente testeable sin red.

Alternativas evaluadas:

- (b) Endpoint de backend por `CallSid`: la mas precisa, pero REQUIERE modificar `App/Backend/**` -> fuera de alcance. Se registra como endurecimiento futuro (Open Question OQ2); el endpoint actual ya devuelve `call_sid`, por lo que migrar mas adelante no cambia el contrato del gate.
- (c) Aceptar el reintento como limitacion documentada: RECHAZADA. Re-medir un caso es un flujo real de la campana (c-172 `--resume`, `--replace`); reportar `listo` con el ingreso previo reabriria exactamente el solapamiento que este change elimina.

Borde conocido y aceptado: si el operador fuerza el avance por timeout y vuelve a llamar el MISMO caso, el ingreso de la llamada forzada (aun sin procesar) tiene `ingresado_en < since` de la nueva llamada y por lo tanto NO se reporta como procesado; la sonda espera correctamente al ingreso nuevo.

### D4 - Cliente HTTP con stdlib, sin dependencia nueva

El servidor de loopback usa `urllib.request` + `ssl.SSLContext` (con `check_hostname=False` y `verify_mode=CERT_NONE` cuando `--insecure`), mas `json` y `datetime.fromisoformat`. Se evita agregar `requests` a `scripts/voip_softphone/requirements.txt` para no incorporar una dependencia que la herramienta no necesita.

### D5 - Configuracion del `serve` y degradacion segura

Flags nuevos de `serve`: `--backend-base-url` (default `https://localhost`), `--insecure`. Credenciales desde `INGEST_OPERATOR_USERNAME` / `INGEST_OPERATOR_PASSWORD`. Si faltan las credenciales, `serve` sigue operativo pero `/case-status` responde un error claro (`probe_unconfigured`) y la pagina degrada a advertencia visible SIN bloquear (fail-open). El runbook de campana debe exportar las credenciales para que el gate quede ACTIVO; el fail-open evita dejar al operador atrapado por una mala configuracion.

### D6 - Maquina de estados de la UI

`inicializando -> registrado -> llamando -> en llamada -> procesando -> registrado`. Al terminar una llamada: si `selectedCaseId()` es no nulo -> entra en `procesando` (Call deshabilitado, estado "procesando <case>…"), arranca un temporizador de polling (~2 s) con timeout acotado (~60 s); si `listo` -> vuelve a `registrado` con mensaje claro; si timeout -> advertencia y vuelve a `registrado` (Call habilitado). Sin caso -> transicion directa a `registrado` (comportamiento actual). El temporizador se cancela de forma explicita al resolver o al iniciar otra llamada, para no dejar timers huerfanos ni doble polling.

### D7 - Manejo de errores de la sonda

404 => `listo=false` (seguir). Estado terminal (`error_stt`, `error_descarga`, `guarda_denegada`) => `listo` nunca sera verdadero; la sonda expone `transcripcion_estado` y la UI lo menciona en la advertencia de timeout. Error de red / HTTP 5xx / `probe_unconfigured` => advertencia y fail-open. La UI solo usa `listo` para decidir el bloqueo.

### D8 - Privacidad e higiene de secretos

El JWT se cachea en memoria del servidor y se re-loguea ante 401; nunca se expone a la pagina ni se persiste. La sonda no loguea descripciones ni contenido de casos (solo identificadores/estados). No se versiona ningun secreto.

## Risks / Trade-offs

- [Skew de reloj entre navegador y backend] -> misma maquina; comparacion unidireccional con margen de la duracion de la llamada.
- [Credenciales ausentes en la shell] -> fail-open con advertencia visible; documentado como prerequisito del runbook.
- [Timeout ~60 s insuficiente bajo carga] -> advertencia y escape del operador; el valor es un default ajustable sin cambiar el contrato.
- [`latest=true` con reintento] -> mitigado por D3 (`since`).
- [Doble polling / timers huerfanos] -> cancelacion explicita del temporizador (D6), cubierta por test estructural.

## Migration Plan

Tooling de desarrollo, sin migraciones de datos ni cambios de backend.

1. Aplicar cambios en `mint_token.py` y `softphone.html` con sus tests (Strict TDD).
2. Documentar flags y prerequisito de credenciales en `README.md` y la referencia cruzada en la guia de campana.
3. Rollback: revertir los dos archivos y los tests; no hay estado persistido ni recursos externos que limpiar.

## Open Questions

- OQ1: el timeout de la UI (~60 s) y el intervalo (~2 s) podrian exponerse como flags de `serve`. Son defaults; ajustarlos no cambia specs, enfoque ni tasks.
- OQ2: migrar la sonda a una consulta por `call_sid` cuando exista un endpoint de backend dedicado. Endurecimiento futuro; no requerido ahora porque D3 es suficiente y no toca el backend.
