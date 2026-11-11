# Conteos técnicos canónicos de la tesis v9 — Gate técnico (c-109)

**Este documento es la Fuente Única de Verdad de los conteos técnicos de la tesis
v9.** Todo conteo de entidades del modelo de datos, de etapas funcionales del flujo
N8N, de nodos del flujo y el nombre del paquete del SDK de Google que la tesis cite
en `05-arquitectura.tex`, `06-implementacion.tex` y `12-anexos.tex` —y cualquier rama
de corrección que los reescriba— MUST tomar su valor de la tabla canónica de la
Sección 2. Ninguna rama puede fijar, redefinir ni redondear un conteo por separado:
toda divergencia se resuelve actualizando este memo, no el capítulo de forma aislada.

- **Change**: `c-109-coherencia-de-conteos-tecnicos` (recomendación obligatoria 6 del
  dictamen CONEAU 2026-10-20).
- **Memo hermano**: `docs/Tesis/Correcciones/numeros-canonicos.md` (c-102) fija los
  valores numéricos de resultados (métricas, tiempos, intervalos). Este memo fija los
  conteos técnicos estructurales; son complementarios y no se solapan.
- **Artefacto**: este memo. No altera la paginación (no es un `.tex`).
- **Fecha de verificación**: 2026-10-21.
- **Método**: conteo de solo lectura desde el sistema. No se editó código,
  `n8n/workflow.json` ni `requirements.txt`.
- **Upsert c-135** (`c-135-cronologia-y-consistencia-redaccional`, 2026-10-25): se
  agregan a la Sección 2 los parámetros de tiempo de espera de la inferencia con
  Gemini vigentes durante la campaña automatizada (30 s por intento y 60 s de
  presupuesto total, con 2 reintentos adicionales) y se retira el valor de 10 s; la
  alineación de `05-arquitectura.tex:74` y `12-anexos.tex:104` figura en la Sección 3
  y la evidencia en la Sección 5. Los valores son los predeterminados de
  `settings.py`: ningún archivo versionado los sobreescribe y los `.env*` no se
  leyeron por política de permisos (pendiente de confirmación de los autores, ver
  `design.md` de c-135, D15).

## 1. Procedimiento de recálculo (solo lectura, reproducible)

- **Entidades**: filas de la Tabla `tab:entidades`
  (`docs/Tesis/v9 (IA)/paper/sections/05-arquitectura.tex:90-110`) y módulos ORM
  versionados en `App/Backend/app/models/`.
- **Nodos del flujo**: `json.load(open('n8n/workflow.json'))['nodes']`, agrupados por
  `type`. Los `n8n-nodes-base.stickyNote` son notas adhesivas (no operativas).
- **Etapas funcionales**: agrupación funcional del export declarada en el Anexo E
  (`12-anexos.tex:45`).
- **SDK de Google**: pin declarado en `App/Backend/requirements.txt`.

Comando de referencia (desde la raíz del repositorio):

```bash
python3 -c "
import json
from collections import Counter
nodes = json.load(open('n8n/workflow.json'))['nodes']
c = Counter(n['type'] for n in nodes)
print('total', len(nodes))
print('sticky', sum(1 for n in nodes if 'stickyNote' in n['type']))
print('operativos', sum(1 for n in nodes if 'stickyNote' not in n['type']))
"
```

## 2. Tabla canónica

Estados: `vigente` (valor citable), `retirado` (desmentido; NO citable) y `intocable`
(ya canónico; ninguna rama lo modifica).

| Conteo | Valor canónico | Fuente (archivo:línea) | Estado |
|---|---|---|---|
| Entidades principales del modelo de datos | **7** | `05-arquitectura.tex:90-110` (Tabla `tab:entidades`) + `App/Backend/app/models/` (`empleado.py`, `incidente.py`, `catalog.py`, `clasificacion_log.py`, `user.py`) | vigente |
| Etapas funcionales del flujo N8N | **7** | `12-anexos.tex:45` (agrupación funcional del export) | vigente |
| Nodos del flujo (totales) | **32** | `n8n/workflow.json` | vigente |
| Nodos operativos | **29** | `n8n/workflow.json` (32 totales − 3 notas) | vigente |
| Notas adhesivas (`stickyNote`) | **3** | `n8n/workflow.json` | vigente |
| Paquete del SDK de Google | **`google-genai`** | `App/Backend/requirements.txt:34` (`google-genai>=2.20.0,<3`) | vigente como paquete; la cota `>=2.20.0,<3` queda **superada** (la configuracion evaluada `bf5e099` declara `>=2.20.0` y la entregada `v1.2.5` declara `>=2.33.0,<3`; ver la Seccion 7) |
| Paquete `google-generativeai` | **retirado** (SDK deprecado) | `App/Backend/requirements.txt:25` (comentario: reemplaza al deprecado) | retirado |
| Tiempo de espera de la inferencia por intento (backend → modelo) | **30 s** | `App/Backend/app/config/settings.py:85` (`gemini_timeout_seconds`), introducido en el commit `cf1cfb4` (2026-09-24) | vigente |
| Presupuesto total de reloj por clasificación | **60 s** | `App/Backend/app/config/settings.py:104` (`gemini_total_timeout_seconds`), introducido en el commit `ed4beb9` (2026-09-29, c-58) | vigente |
| Reintentos adicionales del backend al modelo | **2** (peor caso, 3 intentos) | `App/Backend/app/config/settings.py:97` (`gemini_max_retries`), commit `ed4beb9` (2026-09-29) | vigente |
| Tiempo de espera de la inferencia de 10 s | **retirado** | valor previo a `cf1cfb4` (2026-09-24); desmentido por `settings.py:85` | retirado |

### 2.1 Las siete entidades principales (lista canónica)

`incidente`, `sector`, `estado`, `canal_origen`, `clasificacion_log`, `users`,
`directorio_empleado`.

### 2.2 Las siete etapas funcionales del flujo

(1) entrada/triggers; (2) validación y normalización; (3) envío al backend; (4) ruteo
por canal de origen; (5) revisión humana; (6) respuesta y auditoría; (7) aviso
post-revisión. Fuente: `12-anexos.tex:45`.

### 2.3 Nodos por tipo (`n8n/workflow.json`)

`code` 8, `if` 7, `respondToWebhook` 4, `emailSend` 3, `stickyNote` 3, `webhook` 3,
`httpRequest` 2, `emailReadImap` 1, `switch` 1. Total 32 = 29 operativos + 3 notas.

### 2.4 Reglas de no confusión

- Las etapas del **flujo N8N** (siete) NO son las etapas del **pipeline de
  clasificación**. El clasificador híbrido se describe en `05-arquitectura.tex:78`
  ("dos etapas") y `:82` ("tres etapas"); esos conteos son correctos y NO se tocan.
- El patrón de procesamiento **por canal** (cinco pasos: recepción, normalización,
  clasificación y persistencia, evaluación, notificación) es un subconcepto del
  recorrido lineal por canal, NO el conteo total de etapas del flujo. El total es
  siete.
- El conteo de **entidades principales** (siete) es el de la Tabla `tab:entidades`;
  el número total de tablas del ORM es mayor (incluye tablas de soporte como
  auditoría, telefonía y contadores de costo) y queda fuera del alcance de la tesis.

## 3. Alineación aplicada (ANTES -> DESPUES)

| Archivo:línea | ANTES | DESPUES |
|---|---|---|
| `06-implementacion.tex:72` | "el modelo de datos con sus seis entidades" | "el modelo de datos" (sin conteo stale) |
| `06-implementacion.tex:32` | "29 nodos (26 operativos más 3 notas adhesivas)" | "32 nodos (29 operativos más 3 notas adhesivas)" |
| `06-implementacion.tex:32` | "organizados en cinco etapas lógicas" | "organizados en siete etapas funcionales" |
| `06-implementacion.tex:34` | "un patrón de procesamiento en cinco etapas lógicas" | "un patrón de procesamiento por canal, de cinco pasos" |
| `06-implementacion.tex:73` | "estableciendo el patron de cinco etapas" | "estableciendo el patron de procesamiento por canal" |
| `12-anexos.tex:43` | "la totalidad de los 29 nodos configurados" | "la totalidad de los 32 nodos configurados" |
| `12-anexos.tex:45` | "Los 29 nodos operativos se organizan en siete etapas" | "Los 29 nodos operativos (más 3 notas adhesivas, 32 nodos en total) se organizan en siete etapas" |
| `12-anexos.tex:88` | "la API `google-generativeai` versión 0.8" | "el SDK `google-genai` (`>=2.20.0`)" |
| `12-anexos.tex:105` | "API & `google-generativeai` 0.8" | "SDK & `google-genai` `>=2.20.0`" |
| `12-anexos.tex:108` | fuente "documentación de la API `google-generativeai`" | fuente "documentación del SDK `google-genai`" |
| `05-arquitectura.tex:74` | "google-genai >=2.0" | "google-genai >=2.20.0" |
| `06-implementacion.tex:10` | "google-genai >=2.0" | "google-genai >=2.20.0" |
| `05-arquitectura.tex:74` (c-135) | "timeout = 10 s" | "timeout = 30 s por intento del backend al modelo, con un presupuesto total de 60 s por clasificación" |
| `12-anexos.tex:104` (c-135) | fila `timeout`: "10 segundos" / "Límite máximo de latencia; al excederse, el clasificador devuelve confianza 0,0 y marca el caso para revisión humana." | "30 segundos por intento; 60 segundos en total" / límite por intento del backend al modelo, hasta dos reintentos ante fallas transitorias dentro del presupuesto total de 60 s (no son reintentos de N8N al backend); al agotarse, confianza 0,0 y revisión humana |

### 3.1 Líneas intocables (ya canónicas)

| Archivo:línea | Contenido | Motivo |
|---|---|---|
| `05-arquitectura.tex:88` | "siete entidades principales" | ya canónico |
| `05-arquitectura.tex:117` | "siete entidades principales" (caption) | ya canónico |
| `12-anexos.tex:25` | "las siete entidades descritas en la Tabla" | ya canónico |
| `12-anexos.tex:29` | "las siete entidades del modelo" | ya canónico |
| `12-anexos.tex:45` | "siete etapas" | ya canónico |
| `05-arquitectura.tex:78` | "dos etapas" (pipeline de clasificación) | fuera de alcance |
| `05-arquitectura.tex:82` | "tres etapas" (pipeline de clasificación) | fuera de alcance |

## 4. Presupuesto de páginas

- Conteo de partida de `main.pdf` al inicio de c-109: **104 páginas** (el glosario de
  c-105 sumó una respecto de las 103 previas).
- Restricción: `main.pdf` MUST NOT superar 104 páginas tras c-109. Las ediciones son
  sustituciones locales y una ampliación breve en `12:45`; se verifica al compilar.

## 5. Evidencia (archivo y línea)

Fuentes primarias (solo lectura, sin edición):

- `n8n/workflow.json` — 32 nodos; 3 `stickyNote`; 29 operativos.
- `App/Backend/requirements.txt:34` — `google-genai>=2.20.0,<3`.
- `App/Backend/app/models/` — módulos ORM (incl. `empleado.py`:
  `directorio_empleado`).
- `docs/Tesis/v9 (IA)/paper/sections/05-arquitectura.tex:90-110` — Tabla
  `tab:entidades` (siete filas).

Evidencia del upsert c-135 (solo lectura):

- `git log -S "gemini_timeout_seconds: int = 30" --date=short --format='%ad %h %s' -- App/Backend/app/config/settings.py`
  devuelve `2026-09-24 cf1cfb4 fix(gemini): migrar el clasificador a Gemini 3.6 Flash y timeout de 30s`.
- `git log -S "gemini_total_timeout_seconds" ...` y `git log -S "gemini_max_retries" ...`
  devuelven `2026-09-29 ed4beb9 feat(c-58): resiliencia de Gemini (reintentos acotados, presupuesto y guard de costo)`.
- Ambos commits son anteriores a las corridas de la campaña automatizada (2026-10-02
  y 2026-10-06).
- Sin override versionado: `grep -rn -E "GEMINI_(TIMEOUT|TOTAL_TIMEOUT)_SECONDS" docs docker-compose.yml docker-compose.dev.yml`
  solo devuelve la línea comentada `docs/operational-guide.md:67`
  (`# GEMINI_TOTAL_TIMEOUT_SECONDS=60`). Los `.env*` no se leen (política de permisos).
- Semántica al agotarse el presupuesto: `App/Backend/app/classifiers/gemini_classifier.py`
  (bucle de intentos, `gemini_retry_budget_exhausted`) levanta `GeminiTimeoutError` o
  `GeminiUnavailableError`, y `App/Backend/app/classifiers/hybrid.py` las captura y
  devuelve la etapa `fallback` con confianza 0,0 y revisión humana.
- Los reintentos son del backend al modelo; la invocación de N8N al backend
  (`06-implementacion.tex:60`) no tiene reintentos y no se edita (c-140).
- `CLAUDE.md` y `openspec/config.yaml` (10 s) los alinea c-130 con confirmación del
  usuario; c-135 solo deja la nota de coordinación en `dictamen-correcciones.md`.

Capítulos de la tesis citados (editados en c-109, solo las líneas de la Sección 3):
`05-arquitectura.tex:74`; `06-implementacion.tex:10,32,34,72,73`;
`12-anexos.tex:43,45,88,105,108`.

---

## 6. Upsert c-140 (endurecimiento tecnico: TLS, reintentos y E2E, 2026-10-26)

Cifras nuevas que c-140 cita en la tesis, con fuente y comando de verificacion (D16).
Ninguna redefine un valor `vigente` de la Seccion 2; los reintentos que describe
`06-implementacion.tex` son de N8N al backend (tramo de alta), distintos de los
reintentos del backend al modelo de la Seccion 2.

| Cifra | Valor canonico | Fuente | Estado |
|---|---|---|---|
| Intentos del tramo de alta (por nodo) | **3** (`Login operador` y `HTTP POST a MESA-AYUDAS`) | `n8n/workflow.json` (`maxTries`) | vigente |
| Espera fija entre intentos del tramo de alta | **5000 ms** | `n8n/workflow.json` (`waitBetweenTries`) | vigente |
| Tiempo de espera por intento del login | **10000 ms** | `n8n/workflow.json` (`parameters.options.timeout` de `Login operador`) | vigente |
| Tiempo de espera por intento del alta | **75000 ms** | `n8n/workflow.json` (`parameters.options.timeout` de `HTTP POST a MESA-AYUDAS`) | vigente |
| Tope de ejecucion de N8N | **300 s** (`EXECUTIONS_TIMEOUT`) | `docker-compose.yml` | vigente |
| Pruebas de integracion PostgreSQL | **61** | `App/Backend/tests` | vigente |
| Nodos del flujo (totales / operativos) | **32 / 29** | `n8n/workflow.json` | vigente (sin cambio) |

Peor caso del tramo: 40 s (`Login`) + 235 s (`POST`) = 275 s < 300 s.

Comando de verificacion (desde la raiz del repositorio):

```bash
python3 -c "
import json
w = json.load(open('n8n/workflow.json'))
for n in w['nodes']:
    if n['name'] in ('Login operador', 'HTTP POST a MESA-AYUDAS'):
        o = n['parameters'].get('options', {})
        print(n['name'], n['maxTries'], n['waitBetweenTries'], o.get('timeout'))
"
```

y, desde `App/Backend`, `pytest -m integration --collect-only -q` (informa `61/1835`).

Figura `fig:despliegue`: se regenero desde la fuente Mermaid versionada
`docs/diagrams/despliegue.md` (rotulo "TLS 1.2/1.3", antes "TLS 1.3").
Render: `npx -y @mermaid-js/mermaid-cli@12.0.0 -i <tmp>.mmd -o despliegue.png -b white -s 2`
(bloque `mermaid` extraido a un `.mmd` temporal fuera del repositorio; salida
1568x1712, formato retrato). Procedencia: paquete npm oficial `@mermaid-js/mermaid-cli`.
Nota: `mermaid-cli@11` produce el mismo diagrama en formato apaisado; el retrato del
manuscrito requiere la version 12.

**c-188 (2026-11-09):** `fig:despliegue` se regenero otra vez desde `docs/diagrams/despliegue.md`
(frontend = bundle Vite servido por `nginx:alpine` :3000, antes "Vite dev server"; N8N = imagen
derivada de `docker/n8n/Dockerfile` (2.11.2 + parche IMAP, c-182); redes `edge`, `data` (interna),
`automation` y `host_access` de `docker-compose.yml`, antes `mesa_local_default`). Render con
`@mermaid-js/mermaid-cli@12.0.0` (`-b white -s 2`); salida **1568x1780**, retrato; relacion
alto/ancho 1,1352 frente a 1,0918 (+4,0 %, bajo el tope del 5 %).
`fig:matriz_confusion` (Figura 7) se retiro del manuscrito: la matriz figura una sola vez, como
`tab:matriz` (8.2). `scripts/figures/matriz_confusion.py` y `figures/matriz_confusion.pdf` se
conservan como artefacto reproducible no embebido.

### 6.1 Libro de paginas de c-140 (BLOQUEO de la compuerta)

- **Antes** (`main.pdf` en `HEAD`): total **109**; `Anexos` en p. 101; cuerpo **100**; anexos 9.
- **Despues**: total **111**; `Anexos` en p. 103; cuerpo **102**; anexos 9.
- El cuerpo supera el tope de 100 en **2 paginas**. Compensacion aplicada: recortes de
  prosa duplicada en el capitulo 6 (neto **-175 palabras** respecto de `HEAD`) y una
  medida tipografica de espaciado de flotantes; ninguna reduce el conteo. El capitulo 6
  es NETO mas corto que la linea base y aun asi suma una pagina por una pagina de
  flotantes dedicada (las dos figuras de 6.8); una relajacion global de la politica de
  flotantes daria cuerpo 99 pero forzaria tablas del capitulo 8 al interior de los
  anexos (mejora falsa). BLOQUEO reportado en el informe del apply.

## 7. Configuracion evaluada frente a entregada (c-158)

Valores de la tabla `tab:configuracion-evaluada-entregada` (Anexo B de la tesis), verificados el
2026-10-28 con `git show` sobre el commit evaluado `bf5e099` (7-10-2026, primera revision que
versiona `hybrid-v3`) y el tag `v1.2.5` (`70895e21ce159fab94d8049b88a8606d460f6e4d`). Las
dependencias no cambiaron entre `cf1cfb4` (24-09) y `bf5e099`, de modo que la columna evaluada
rige para las tres corridas del brazo automatizado.

| Elemento | `bf5e099` (evaluada) | `v1.2.5` (entregada) | Comando de verificacion |
|---|---|---|---|
| FastAPI | 0.115.0 | 0.162.0 | `git show <rev>:App/Backend/requirements.txt \| grep -i fastapi` |
| Uvicorn | 0.30.6 | 0.54.0 | idem, `uvicorn` |
| SQLAlchemy | 2.0.36 | 2.1.6 | idem, `sqlalchemy` |
| google-genai | `>=2.20.0` | `>=2.33.0,<3` | idem, `google-genai` |
| pytest / pytest-cov | 8.3.3 / 5.0.0 | 9.1.1 / 7.1.0 | idem, `pytest` |
| React (`package-lock.json`) | 18.3.1 | 19.3.1 | `git show <rev>:App/Frontend/package-lock.json` y lectura de `packages["node_modules/react"].version` |
| Nodos del flujo N8N | 28 (25 operativos y 3 notas); 38 (35 y 3) hasta c-72 (`f0c07a3`) | 32 (29 y 3) | `git show <rev>:n8n/workflow.json` y conteo de `nodes` y de `stickyNote` |
| Reintentos del alta | no (`continueErrorOutput` sin `retryOnFail`) | si: `retryOnFail`, `maxTries` 3, `waitBetweenTries` 5000 ms en `HTTP POST a MESA-AYUDAS` y `Login operador`; `options.timeout` 75000 y 10000 ms | idem, nodos con `retryOnFail` |
| Revision por reportante no identificado | no | si (c-82, `incidente_service.py:302,412` en `v1.2.5`) | `git grep -n "reportante no identificado" <rev> -- App/Backend/app/services` |
| Prueba de humo E2E y TLS del borde | no (solo `dry_run` sin `e2e_checks.py` ni `test_tls_checks.py`) | si (c-140; corrida 25/25 del 27-10 sobre `e3176da`) | `git ls-tree -r --name-only <rev> \| grep -E "e2e_checks\|test_tls_checks"` |
| Sin cambios | N8N 2.11.2, Python 3.12-slim, PostgreSQL 15.5-alpine, `gemini-3.6-flash`, temperatura 0,3, top_p 0,9, 100 tokens, 30 s por intento, 60 s en total, 2 reintentos del backend al modelo, umbrales 0,5166 y 0,70 | igual | `git show <rev>:App/Backend/app/config/settings.py` y `docker-compose.yml`; `git diff bf5e099 v1.2.5 -- App/Backend/app/classifiers` solo muestra comentarios, importacion perezosa y docstrings |

Contraste del borde: `git diff --stat e3176da1 v1.2.5 -- nginx docker-compose.yml openssl n8n/workflow.json scripts/dry_run` es vacio. El nginx del compose pasa de
`nginx:alpine` (evaluada) a `nginx:1.31.7-alpine` (entregada); no se agrego fila porque el
proxy no formo parte de la campana (Anexo A y Seccion 7.4 de la tesis).

### 7.1 Configuracion de la campana de medicion (c-169, 2026-11-08)

La tabla `tab:configuracion-evaluada-entregada` del Anexo B agrega la columna
"Configuracion de la campana de medicion" (c-169). La campana complementaria de medicion
(programa c-165 a c-168) corrio sobre el **clasificador congelado `hybrid-v3`** con la
instrumentacion de intervencion de `c-165` aplicada, es decir, sobre la misma
configuracion del clasificador que la evaluada; solo se consigna la fila
`classifier_version`, que coincide con la evaluada.

| Clave | `bf5e099` (evaluada) | `v1.2.7` (entregada) | Campana de medicion | Comando de verificacion |
|---|---|---|---|---|
| `classifier_version` (`HYBRID_CACHE_VERSION`) | `hybrid-v3` | `hybrid-v3` | `hybrid-v3` | `git show bf5e099:App/Backend/app/constants.py \| grep HYBRID_CACHE_VERSION`; `git show v1.2.7:App/Backend/app/constants.py \| grep HYBRID_CACHE_VERSION` |
| Configuracion de la campana (cache in-sample) | — | — | `hybrid-v3` | `evaluation/data/campana/README.md:167` (`classifier_version_in_sample: hybrid-v3`) |

Las restantes filas de la columna de la campana quedan sin declarar (`---`) porque las
dependencias del entorno de esa corrida no se re-verificaron sobre el commit de la
campana; la unica coincidencia consignada con la evaluada es la version del clasificador,
segun la regla del design de c-169 ("`classifier_version` debe coincidir con la evaluada;
si no coincide, las metricas de la campana se rotulan como de otra configuracion del
clasificador").

### 7.2 Tabla 19 completada por c-187 (dictamen CONEAU 2026-11-08, A1 y A5)

c-187 reemplaza las celdas `---` de la columna (ahora "Campana complementaria") con valores
verificados por diferencia de commits, y agrega las filas "Instrumentacion de intervencion",
"Imagen de N8N" y "Revision del repositorio". La campana **no corrio sobre un unico commit**:
correo y web desde `cda7712` (5-11-2026 20:45 -03; sidecars 5-11 23:47 UTC a 6-11 17:55 UTC);
telefonia el 6-11 (17:33 a 19:45 -03) tras c-174 (`e7dfd17`) y c-175 (`fce5ec6`); intervenciones
(`validado_en`) del 7-11 08:47 al 8-11 16:55 -03, mientras se confirmaban c-177 a c-183.

| Clave | Evaluada (`bf5e099`) | Entregada | Campana complementaria | Comando de verificacion |
|---|---|---|---|---|
| FastAPI, Uvicorn, SQLAlchemy, `google-genai`, pytest, React, flujo N8N (32 nodos), reintentos | ver 7 | ver 7 | como la entregada | `git diff --stat cda7712 v1.2.10 -- App/Backend/requirements.txt App/Frontend/package-lock.json n8n/workflow.json App/Backend/app/constants.py App/Backend/app/config/settings.py` (sin diferencias); `git diff --stat cda7712 fce5ec6 -- App/Backend/requirements.txt n8n/workflow.json docker-compose.yml` (sin diferencias) |
| Revision por reportante no identificado (c-82) | No | Si | Si | `git show cda7712:App/Backend/app/services/incidente_service.py \| grep -n "reportante_empleado_id is None"` |
| Propagacion del contacto (c-162, 29-10-2026, `337a8af`) | No | Si | Si | `git show cda7712:n8n/workflow.json \| grep -c reportante_email` |
| Instrumentacion de intervencion (c-165) | No | Si | Si (parte de las de `O1` con un frontend previo a c-165) | `evaluation/data/campana/README.md:225` |
| Imagen de N8N | `n8nio/n8n:2.11.2` | derivada de `n8nio/n8n:2.11.2` (`docker/n8n/Dockerfile` + parche IMAP, c-182) | `n8nio/n8n:2.11.2` (la derivada es posterior: `000abeb`, 7-11-2026 18:18 -03) | `git show cda7712:docker-compose.yml \| grep -n "n8nio/n8n"`; `git show v1.2.10:docker/n8n/Dockerfile \| grep -n "^FROM"`; `git show 000abeb --stat` |
| Prueba de humo E2E y TLS (c-140) | No | Si | No registrado | no recuperable de los sidecars |
| `classifier_version` | `hybrid-v3` | `hybrid-v3` | `hybrid-v3` | ver 7.1 |

Unica diferencia de `docker-compose.yml` entre `cda7712` y `v1.2.10`: la imagen derivada de N8N
(`git diff cda7712 v1.2.10 -- docker-compose.yml`). El commit de generacion de la cache
in-sample sigue sin recuperarse (README de la campana, linea 191).

---

## 8. Dictamen CONEAU v10/v1.2.12: canal telefonico, pines y figuras (c-190, 2026-11-09)

Conteos técnicos verificados para el dictamen del 2026-11-09 sobre el tag `v1.2.12` (change
`c-190-atender-el-dictamen-coneau-v1-2-12`). Ninguno redefine un valor `vigente` de la
Sección 2.

### 8.1 Diferencia entre la campana complementaria y la entregada (nota de la Tabla 19)

Comando (desde la raíz del repositorio):

```bash
git diff --stat cda7712 v1.2.12 -- App/ n8n/ docker/ docker-compose.yml
```

Salida: **24 archivos, 1323 inserciones y 75 supresiones**. Desglose: `docker-compose.yml` (1);
`docker/n8n/` (3: `Dockerfile`, `apply-unified-patch.mjs`,
`imap-simple-fromdata-charset.patch`); backend (7: `app/cost_guard/twiml.py`,
`app/routes/cost_guard.py`, `scripts/reparar_encoding_descripciones.py` y cuatro pruebas);
frontend (13, entre otros `Header`, `DetalleIncidente`, `ValidarClasificacionDialog`,
`Administracion/index` y `ReportarIncidente/index` con sus pruebas y `utils/formatters`).
Ninguno de los 24 interviene en la clasificación.

Comando de los pines (salida vacía, 0 archivos):

```bash
git diff --stat cda7712 v1.2.12 -- App/Backend/requirements.txt App/Frontend/package-lock.json n8n/workflow.json App/Backend/app/config/settings.py
```

Modelo de transcripción declarado en la configuración entregada:

```bash
git show v1.2.12:App/Backend/app/config/settings.py | grep -n gemini_stt_model
```

devuelve `gemini_stt_model = "gemini-3.5-transcribe"` (línea 238), usado por
`App/Backend/app/clients/gemini_stt.py`.

### 8.2 Figuras regeneradas (c-190)

Se regeneraron `figures/despliegue.png`, `figures/componentes.png` y `figures/secuencia.png`
desde `docs/diagrams/{despliegue,componentes,secuencia}.md` con el pipeline de c-188:
`npx -y @mermaid-js/mermaid-cli@12.0.0 -i <tmp>.mmd -o <figura>.png -b white -s 2` (bloque
`mermaid` extraído a un `.mmd` temporal fuera del repositorio). Versión de `mermaid-cli`:
**12.0.0**. Dimensiones: **por confirmar** (se anotan al cerrar el apply). La relación
alto/ancho no supera la previa en más de un 5 %. Los PNG de `componentes` y `secuencia`
llevaban el rótulo temporal dentro de la imagen (no solo en la leyenda): c-190 editó las
fuentes Mermaid y los regeneró.

### 8.3 Figura huérfana

`figures/matriz_confusion.pdf` se retiro del directorio de figuras (inv. 23);
`scripts/figures/matriz_confusion.py` puede regenerarlo fuera de `figures/`.
Verificación: `rg -n "matriz_confusion" "docs/Tesis/v10 (IA)/paper/sections"` = 0.

---


_Producido por c-109. Cualquier rama que reescriba los conteos técnicos de `05`, `06`
o `12` debe citar únicamente los valores `vigente` de la Sección 2 y MUST NOT
redefinirlos de forma aislada._
