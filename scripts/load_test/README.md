# Test de carga multicanal (c-218)

Mide, de forma reproducible y de costo cero, la capacidad del tramo compartido
donde convergen los canales de entrada. Contrasta la dimension medible de la
hipotesis subsidiaria de integracion multicanal: que integrar los canales no
introduce cuellos de botella adicionales.

## Que mide

Dos capas, por separado y por nivel de concurrencia:

| Capa | Destino | Que aisla |
|------|---------|-----------|
| `backend` | `POST /api/v1/incidentes/` (con `Bearer`) | reglas del clasificador y una escritura a PostgreSQL |
| `n8n` | `POST /webhook/incidente-web` de N8N | N8N -> backend: si el orquestador agrega un cuello de botella |

Por nivel y capa registra latencia de cliente (p50, p95, p99, media), la
`latencia_e2e_ms` del servidor (p50, p95), throughput (req/s) y tasa de error
(no 2xx y timeouts; nada se descarta del denominador).

**Exclusiones declaradas**: correo (sondeo IMAP por minuto, no apto para
inyeccion concurrente) y telefonia (canal pago, Twilio). La convergencia en
`POST /api/v1/incidentes/` es agnostica al canal, de modo que la medicion sobre
ese punto cubre a los tres. El reporte repite esta exclusion.

## Criterio prerregistrado (design D6)

Constantes fijadas antes de observar datos; **no se ajustan despues de ver
resultados**:

| Constante | Valor |
|-----------|-------|
| Niveles de concurrencia | 1, 5, 10, 20 |
| Solicitudes por nivel y repeticion | 40 |
| Repeticiones por nivel | 3 (las metricas del nivel agrupan las 120 solicitudes; el reporte conserva cada repeticion) |
| Techo de latencia | `p95 <= 5000 ms` en todos los niveles (inclusivo) |
| Tolerancia de throughput | no decrece mas del 10 % respecto del nivel anterior (inclusivo) |
| Tasa de error | `0` en todos los niveles |
| Control de escalado (secundario, solo se informa) | `p95(20) / p95(1) <= 20` |

Veredicto por capa: **sostenida** si en todos los niveles se cumplen las tres
condiciones primarias; **no sostenida** si algun nivel viola alguna (el reporte
nombra nivel y condicion); **no concluyente** si la corrida queda incompleta o
los niveles no son los prerregistrados. El veredicto global es el de la peor
capa (no sostenida > no concluyente > sostenida). Las metricas de latencia del
criterio son las del cliente (envio a respuesta).

## Costo cero (dos capas independientes)

`compose.load-test.yml` inyecta en `backend-corpus` una `GEMINI_API_KEY`
ficticia y `COST_GUARD_BUDGET_USD=0`. Antes de enviar nada, el arnes lee las
variables efectivas DENTRO del contenedor y aborta con codigo `3` si la clave no
es la ficticia o el presupuesto no es exactamente cero. El fixture
(`fixture_descripciones.json`, 28 descripciones por sector, score de
correctitud por encima del umbral) se resuelve en la etapa determinística; al
terminar cada nivel el arnes consulta el registro de clasificacion de cada
incidente y aborta con codigo `4` si alguno no quedo solo en la etapa
`deterministic`. No se invoca a Gemini ni a Twilio. No se envia correo.

## Entorno desechable

Usa el perfil `corpus` (base `mesa_de_ayuda_corpus`, backend en el puerto 8001,
N8N en el 5679). Nunca escribe en la base operativa `mesa_de_ayuda`. No modifica
`docker-compose.yml`, `n8n/workflow.json` ni `App/**`. Docker Compose se invoca
siempre sobre el proyecto de nombre fijo, sin `-p`.

**Arranque ACOTADO (obligatorio):** un `up --profile corpus` a secas tambien
levanta el stack base. Nombrar siempre los tres servicios:

```bash
make load-test-up        # equivale a:
docker compose -f docker-compose.yml -f scripts/load_test/compose.load-test.yml \
  --profile corpus up -d postgres-corpus backend-corpus n8n-corpus
```

**Cierre ACOTADO:** no usar `docker compose down` (con `-v` borra los volumenes
del stack base). Para detener solo lo del perfil:

```bash
make load-test-stop      # stop + rm -f de los tres servicios del perfil
```

## Ejecucion

1. Levantar el perfil (arriba).
2. Importar y activar en `n8n-corpus` la copia de costo cero del flujo web
   (no toca el `workflow.json` versionado):
   `python scripts/load_test/preparar_n8n.py`
3. Correr el arnes y versionar la evidencia:
   `make load-test`, o
   `python scripts/load_test/load_test.py --json-out evaluation/evidence/load_test_multicanal_<YYYY-MM-DD>.json`
4. Pruebas offline (sin red, sin Docker, sin claves):
   `python -m pytest scripts/load_test -q`

Salidas: `<json-out>` y su resumen `.md` (LF, UTF-8 sin BOM, deterministas, sin
secretos) con commit, fecha UTC, version de N8N, perfil, hash del fixture,
constantes, metricas por nivel y veredicto.

Codigos de salida: `0` corrida completa (cualquier veredicto), `3` guarda de
costo cero no en efecto, `4` una solicitud escalo, `5` login del operador
fallido.

## Alcance y limites

Una sola maquina, perfil desechable y camino determinístico (sin inferencia
paga): el resultado no se extrapola a produccion ni a la latencia con Gemini.
La complejidad operativa percibida no se mide aqui.
