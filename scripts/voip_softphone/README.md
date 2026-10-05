# Softphone VoIP de desarrollo (`scripts/voip_softphone/`)

Herramienta de DESARROLLO para inyectar la voz de un operador en el pipeline
telefonico existente (canal de telefonia de c-52) mediante un softphone VoIP
de navegador, **sin tramo PSTN internacional y sin auto-llamada** entre
numeros de la misma cuenta Twilio (bloqueada con el error `21216`).

Usa el Voice SDK de Twilio sobre WebRTC. La llamada saliente apunta a un
TwiML App cuya Voice URL **reutiliza el endpoint de voz de produccion**
(`POST /api/v1/cost-guard/twilio/voice`), de modo que la llamada entra al flujo
real, incluida la admision de la guarda de costo. **El backend de produccion
no se modifica.**

> Nota de entorno: en esta maquina el interprete es `python3` (no hay alias
> `python`). Los comandos de abajo usan `python3`.

---

## 1. Prerequisites

- Stack local arriba con el nombre de proyecto fijo `mesa_local`
  (`docker compose -p mesa_local up -d`), incluyendo backend y n8n.
- Tunel ngrok arriba en el dominio reservado:
  `docker compose -p mesa_local --profile tunnel up -d ngrok`.
  El dominio debe coincidir en los TRES lugares: los numeros Twilio, la Voice
  URL del TwiML App y `BACKEND_PUBLIC_BASE_URL`.
- Twilio CLI v7 instalado. El setup se autentica con credenciales de CUENTA
  desde el entorno (`TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN`), NO con un
  perfil (ver seccion 3).
- Python 3.12.
- Al menos un numero Twilio con capacidad Voice (los existentes
  `+13146487338` / `+12295958782` ya tienen la Voice URL correcta).

Instalar la dependencia aislada (NO se agrega al backend):

```bash
python3 -m pip install --user -r scripts/voip_softphone/requirements.txt
```

## 2. Variables de entorno requeridas

La herramienta lee **todas** las credenciales exclusivamente del entorno. No
hay secretos hardcodeados ni en archivos versionados. Si falta alguna, la
utilidad aborta con un mensaje claro y codigo de salida distinto de cero.

| Variable | Origen | Descripcion |
|----------|--------|-------------|
| `TWILIO_ACCOUNT_SID` | Twilio Console | SID de la cuenta (`AC...`). Usado por el setup y por la utilidad de token. |
| `TWILIO_AUTH_TOKEN` | Twilio Console | Auth Token de la cuenta. Necesario SOLO para el setup (paso 3): la Keys API exige credenciales de cuenta. **Nunca se escribe a disco.** |
| `TWILIO_API_KEY_SID` | paso 3 | SID del API Key (`SK...`). |
| `TWILIO_API_KEY_SECRET` | paso 3 (una sola vez) | Secret del API Key. **Nunca se escribe a disco.** |
| `TWILIO_TWIML_APP_SID` | paso 3 | SID del TwiML App (`AP...`). |

Ejemplo (valores ficticios; exportar en la shell, nunca commitear):

```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="..."        # solo para el setup (paso 3)
export TWILIO_API_KEY_SID="SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_API_KEY_SECRET="..."   # capturado una vez al crear el API Key
export TWILIO_TWIML_APP_SID="APxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Alternativa recomendada (no contamina `App/Backend/.env`, que es del backend):
guardar `TWILIO_API_KEY_SID`, `TWILIO_API_KEY_SECRET` y `TWILIO_TWIML_APP_SID`
en `scripts/voip_softphone/softphone.env` (GITIGNORED por la regla `*.env`) y
cargarlas antes de `serve`:

```bash
set -a
source App/Backend/.env                       # aporta TWILIO_ACCOUNT_SID
source scripts/voip_softphone/softphone.env   # API Key + TwiML App SID
set +a
```

`mint_token.py serve` NO lee `.env` por si solo; siempre hay que exportar las
variables en la shell (o `source` los archivos) antes de arrancarlo.

## 3. Configuracion del lado Twilio

### 3.a Con el script (recomendado)

El CLI se autentica con **credenciales de CUENTA desde el entorno**, porque la
**Keys API exige Account SID + Auth Token**: un perfil del CLI guarda un API
Key, y un API Key NO puede administrar el recurso Keys (Twilio responde
`70004 The provided key does not have the permissions to access this
endpoint`). Exportar las credenciales de cuenta en la shell:

```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="..."        # Account Auth Token (Console)
```

Luego crear el API Key y el TwiML App. El script corre el CLI **sin** `--profile`
para que el CLI use esas credenciales de entorno:

```bash
python3 scripts/voip_softphone/setup_twilio.py
```

Si faltan `TWILIO_ACCOUNT_SID` o `TWILIO_AUTH_TOKEN`, el script aborta con un
mensaje claro y codigo de salida distinto de cero, sin invocar el CLI.

`--voice-url` por defecto es el endpoint de voz existente sobre el dominio
ngrok reservado:

```
https://tameness-trilogy-unrefined.ngrok-free.dev/api/v1/cost-guard/twilio/voice
```

Para apuntar a otra URL, pasar `--voice-url` explicitamente:

```bash
python3 scripts/voip_softphone/setup_twilio.py --voice-url https://mi-host/voice
```

`--profile` es OPCIONAL y solo para usuarios avanzados: si se pasa, se reenvia
al CLI. **Advertencia**: un perfil comun guarda un API Key y la creacion del API
Key fallara igual con `70004`; solo funciona si el perfil lleva credenciales de
cuenta. El camino soportado es el de entorno (sin `--profile`).

Capturar el `API Key Secret` impreso en `TWILIO_API_KEY_SECRET`. Cargar los
otros dos SIDs en `TWILIO_API_KEY_SID` y `TWILIO_TWIML_APP_SID`.

### 3.b Alternativa manual (Twilio Console)

1. Console > Account > API keys & tokens > Create API Key (Standard). Copiar
   el SID (`SK...`) y el secret (visible una sola vez).
2. Console > Voice > TwiML > TwiML Apps > Create:
   - Voice URL: `https://tameness-trilogy-unrefined.ngrok-free.dev/api/v1/cost-guard/twilio/voice`
   - Voice Method: `POST`
   - Copiar el `Application SID` (`AP...`).
3. Cargar las cuatro variables de entorno de la seccion 2.

## 4. Arranque del servidor local

El servidor sirve la pagina y un **token fresco por request** desde el MISMO
origen de loopback (`127.0.0.1:8765`), por lo que no hay que configurar CORS.
Escucha EXCLUSIVAMENTE en loopback y emite tokens de vida corta. En el mismo
origen expone ademas el listado de casos telefonicos del corpus (c-70):

- `GET /corpus-cases` -> `[{id, descripcion}]` de los casos de canal telefonico
  del corpus pseudonimizado, con el rotulo de canal tolerante a tildes, mayusculas
  y espacios (`llamada telefonica` / `llamada telefónica` / `telefono`).
  Solo loopback, por lo que el listado no requiere auth adicional; las
  descripciones nunca se loguean.

```bash
python3 scripts/voip_softphone/mint_token.py serve
```

La ruta del corpus es configurable con `--corpus-json` (default:
`data/corpus_evaluacion_pseudonimizado.json`). Si el archivo no existe o no es
JSON valido, el endpoint responde `500` con un mensaje claro que incluye la ruta.

```bash
python3 scripts/voip_softphone/mint_token.py serve --corpus-json /ruta/corpus.json
```

Para inspeccionar un token sin levantar el servidor:

```bash
python3 scripts/voip_softphone/mint_token.py token
```

Tanto `token` como `serve` aceptan `--identity` y `--ttl` (segundos; default
`1800`). `--corpus-json` aplica solo a `serve`.

## 5. Colocar la llamada

1. Con el servidor arriba, abrir `http://127.0.0.1:8765/`.
2. La pagina obtiene el token, registra el `Twilio.Device`, carga el listado de
   casos telefonicos y habilita `Call`.
3. (Opcional) En **Caso del corpus (telefono)** elegir un caso. La pagina muestra
   el texto del caso para **recitarlo a mano**; la herramienta **NO reproduce
   audio** (no hay TTS ni playback). El `<select>` arranca vacio por defecto.
4. Presionar **Call**: se establece la llamada saliente hacia el TwiML App.
   - Con un caso seleccionado, la llamada envia
     `device.connect({ params: { corpus_case_id: <id> } })` para correlacionar
     la llamada con el caso.
   - Sin seleccion, la llamada se coloca igual que antes (sin
     `corpus_case_id`): modo de desarrollo sin correlacion, retrocompatible con
     C-59.
   El flujo de c-52 corre: `<Say>` + `<Record maxLength=45 finishOnKey=#>`.
   Recitar el texto del caso por el microfono.
5. Presionar **Hangup** para terminar la llamada. Al cortar, Twilio finaliza la
   grabacion y dispara el `recordingStatusCallback`: el backend descarga el
   audio, hace STT, pseudonimiza y hace handoff a n8n, que crea el incidente.
   La grabacion tambien termina sola a los 45 s o tras ~5 s de silencio.
6. La pagina queda lista para una nueva llamada.

> **Nota sobre `#`**: el canal telefonico real espera que el llamante presione
> `#` (`finishOnKey`) para cerrar la grabacion sin colgar. El softphone NO tiene
> teclado ni envio de DTMF, y **no hace falta**: colgar (Hangup) finaliza la
> grabacion y dispara el mismo callback, con el mismo resultado.

## 6. Identidad y guarda de costo (`From = client:<identity>`)

En una llamada iniciada por el Voice SDK, el endpoint de voz recibe
`From = client:<identity>` (no E.164). La guarda de costo usa ese valor CRUDO
como clave del **rate por origen** (default 3/hora). Con una identidad fija,
la tercera llamada en una hora seria denegada con `CAUSE_CALLER_RATE`
(comportamiento EXISTENTE, no un bug).

**Mitigacion**: la utilidad acuña por defecto una identidad UNICA por sesion
(`softphone-dev-<timestamp>`). Cada corrida usa una clave `caller` distinta y
el rate por origen no corta las pruebas. La identidad se fija SOLO por CLI
(`--identity`); **no es editable desde la pagina HTML**, para no romper la
garantia de unicidad. La bolsa global (`COST_GUARD_BUDGET_USD`) y el rate
global (30/h) SIGUEN aplicando: es el comportamiento deseado de seguridad.

## 7. Higiene de secretos

- El `API Key Secret` se muestra una sola vez y nunca se escribe a un archivo
  versionado.
- La herramienta no persiste tokens; los emite en memoria y de vida acortada.
- No crear un `.env` dentro de `scripts/voip_softphone/` con secretos reales
  (`.env` y `*.env` ya estan en `.gitignore`). El hook `.githooks/pre-commit` y
  el job `secret-scan` (gitleaks) bloquean cualquier fuga.

## 8. Tests offline

Sin red y sin credenciales reales (el CLI de Twilio se inyecta fakeado):

```bash
python3 -m pytest scripts/voip_softphone -q
```

## 9. Limitaciones / estado de c-52

- El defecto de sesion de `memoryRedisChat` de n8n (`NodeOperationError:
  "No session ID found"`) **YA FUE CORREGIDO en c-52** (commit `4946584`,
  `sessionIdType: customKey` + `sessionKey`). El intake telefonico es
  funcional y la verificacion end-to-end PUEDE confirmar la creacion del
  incidente. **No es un blocker.**
- La verificacion end-to-end en vivo (Docker + n8n + ngrok + navegador + cuenta
  Twilio real) es MANUAL y la realiza el operador humano (tarea 6.3).

## 10. Rollback

- Codigo: eliminar `scripts/voip_softphone/`.
- Twilio: borrar el TwiML App y el API Key creados
  (`twilio api:core:applications:delete`, `twilio api:core:keys:delete`). Los
  numeros y su `voiceUrl` no se modifican. No hay migraciones ni datos.

## 11. Evidencia de verificacion en vivo (2026-10-01)

La tarea 6.3 se verifico con llamadas reales desde el navegador (softphone en
`127.0.0.1:8765`) contra el stack local con ngrok. Resultado: APROBADO.

- Incidente #20 creado de punta a punta desde una llamada del softphone.
  CallSid `CAa8d1ae5c9f75f2a9f859b947a4b8b447` (`from: client:softphone-dev-...`,
  18 s); ingreso telefonico #8 `transcrito` (6 s), descripcion pseudonimizada sin
  PII, clasificado en `Soporte Tecnico Hardware` (0.98).
- Incidente #19 en una llamada previa (CallSid `CA0605fae...`, 30 s), misma
  secuencia end-to-end.
- Logs del backend: `telefonia_transcrito` -> handoff n8n `200` ->
  `incidente_created` -> `incidente_classified`.
- UI: el estado pasa a "en llamada" al ser atendido y a "desconectado" al colgar;
  Hangup queda habilitado al iniciar la llamada.

Nota: el mensaje de bienvenida promete una notificacion con el numero de
incidente; esa funcionalidad pertenece a c-53 (en curso) y todavia NO se envia.
