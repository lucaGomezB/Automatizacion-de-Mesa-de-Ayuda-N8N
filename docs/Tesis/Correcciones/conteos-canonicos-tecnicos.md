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

Capítulos de la tesis citados (editados en c-109, solo las líneas de la Sección 3):
`05-arquitectura.tex:74`; `06-implementacion.tex:10,32,34,72,73`;
`12-anexos.tex:43,45,88,105,108`.

---

_Producido por c-109. Cualquier rama que reescriba los conteos técnicos de `05`, `06`
o `12` debe citar únicamente los valores `vigente` de la Sección 2 y MUST NOT
redefinirlos de forma aislada._
