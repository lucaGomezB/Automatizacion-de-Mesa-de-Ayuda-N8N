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
| Paquete del SDK de Google | **`google-genai`** | `App/Backend/requirements.txt:34` (`google-genai>=2.20.0,<3`) | vigente |
| Paquete `google-generativeai` | **retirado** (SDK deprecado) | `App/Backend/requirements.txt:25` (comentario: reemplaza al deprecado) | retirado |
| Tiempo de espera de la inferencia por intento (backend → modelo) | **30 s** | `App/Backend/app/config/settings.py:85` (`gemini_timeout_seconds`), introducido en el commit `11036be` (2026-09-24) | vigente |
| Presupuesto total de reloj por clasificación | **60 s** | `App/Backend/app/config/settings.py:104` (`gemini_total_timeout_seconds`), introducido en el commit `429f2c9` (2026-09-29, c-58) | vigente |
| Reintentos adicionales del backend al modelo | **2** (peor caso, 3 intentos) | `App/Backend/app/config/settings.py:97` (`gemini_max_retries`), commit `429f2c9` (2026-09-29) | vigente |
| Tiempo de espera de la inferencia de 10 s | **retirado** | valor previo a `11036be` (2026-09-24); desmentido por `settings.py:85` | retirado |

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
  devuelve `2026-09-24 11036be fix(gemini): migrar el clasificador a Gemini 3.6 Flash y timeout de 30s`.
- `git log -S "gemini_total_timeout_seconds" ...` y `git log -S "gemini_max_retries" ...`
  devuelven `2026-09-29 429f2c9 feat(c-58): resiliencia de Gemini (reintentos acotados, presupuesto y guard de costo)`.
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
| Pruebas de integracion PostgreSQL | **54** | `App/Backend/tests` | vigente |
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

y, desde `App/Backend`, `pytest -m integration --collect-only -q` (informa `54/...`).

Figura `fig:despliegue`: se regenero desde la fuente Mermaid versionada
`docs/diagrams/despliegue.md` (rotulo "TLS 1.2/1.3", antes "TLS 1.3").
Render: `npx -y @mermaid-js/mermaid-cli@12.0.0 -i <tmp>.mmd -o despliegue.png -b white -s 2`
(bloque `mermaid` extraido a un `.mmd` temporal fuera del repositorio; salida
1568x1712, formato retrato). Procedencia: paquete npm oficial `@mermaid-js/mermaid-cli`.
Nota: `mermaid-cli@11` produce el mismo diagrama en formato apaisado; el retrato del
manuscrito requiere la version 12.

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

---

_Producido por c-109. Cualquier rama que reescriba los conteos técnicos de `05`, `06`
o `12` debe citar únicamente los valores `vigente` de la Sección 2 y MUST NOT
redefinirlos de forma aislada._
