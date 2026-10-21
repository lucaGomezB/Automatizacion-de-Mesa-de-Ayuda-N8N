## Context

Ver `proposal.md` — Why. Governance **MEDIO**: el change toca conteos y nombres
tecnicos del documento (no afirmaciones de resultados), por lo que se implementa
con checkpoints y se expone cada decision. No se edita ningun `.tex` en la fase de
propose; la alineacion se ejecuta en apply.

Dictamen: `auditorias/Dictamen_Tesis_v9_CONEAU_2026-10-20.md`, recomendacion
obligatoria 6. Registro de trazabilidad:
`docs/Tesis/Correcciones/dictamen-correcciones.md` (grupo T1-T7 e item 6 del plan).

**Fuentes de verdad (solo lectura) para fijar los conteos:**

| Conteo | Fuente | Valor canonico |
|---|---|---|
| Entidades principales | `05-arquitectura.tex` Tabla `tab:entidades` + `App/Backend/app/models/` (`directorio_empleado.py`) | **7** |
| Etapas funcionales del flujo | `n8n/workflow.json` (agrupacion funcional) | **7** |
| Nodos del flujo | `n8n/workflow.json` (32 nodos: 3 `stickyNote` + 29 operativos) | **29 operativos + 3 notas = 32** |
| SDK de Google | `App/Backend/requirements.txt` | **`google-genai` (`>=2.20.0,<3`)** |

## Goals / Non-Goals

**Goals:**

- Fijar los cuatro conteos/nombres desde el sistema, antes de editar el texto.
- Alinear `05-arquitectura.tex`, `06-implementacion.tex`, `12-anexos.tex` y las
  tablas afectadas al conteo unico.
- Registrar el conteo canonico para que las ramas posteriores no divergan.

**Non-Goals:**

- No editar `.tex` en la fase de propose.
- No reescribir resultados, metricas ni la tabla 7.5 (titularidad de c-107/c-108).
- No modificar el codigo, `n8n/workflow.json` ni `requirements.txt`.
- No tocar `Bibliography_base.bib` (titularidad de c-104/c-78).

## Decisions

### D1 — Entidades: siete (no seis)

La Tabla `tab:entidades` y el diagrama ER listan siete entidades
(`incidente`, `sector`, `estado`, `canal_origen`, `clasificacion_log`, `users`,
`directorio_empleado`); el ORM versionado confirma `directorio_empleado`
(`App/Backend/app/models/empleado.py:80`). La unica ocurrencia de "seis" esta en
`06-implementacion.tex:72`, dentro de la narracion de la iteracion 2 ("entrego el
modelo de datos con sus seis entidades"). **Regla**: declarar siete de forma
consistente. **Implementacion**: reescribir `06:72` para no afirmar un conteo
stale del modelo final (por ejemplo, describir el entregable de la iteracion sin
el numeral, o declarar las siete entidades del modelo vigente). **Alternativa
descartada**: conservar "seis" como valor historico de la iteracion; se descarta
porque el dictamen lo lee como discrepancia de conteo y la iteracion no es el
lugar para fijar el numero del modelo final. **Reversible**: no; el modelo tiene
siete entidades principales.

### D2 — Etapas del flujo: siete (no cinco)

`12-anexos.tex:45` agrupa los 29 nodos en **siete** etapas funcionales derivadas
del export JSON: (1) entrada/triggers, (2) validacion y normalizacion, (3) envio
al backend, (4) ruteo por canal de origen, (5) revision humana, (6) respuesta y
auditoria, (7) aviso post-revision. `06-implementacion.tex:32,34,73` declara
"cinco etapas logicas" (Recepcion, Normalizacion, Clasificacion y persistencia,
Evaluacion, Notificacion), que es el **patron de procesamiento por canal**, no la
agrupacion funcional completa. **Regla**: el conteo total de etapas del flujo es
**siete**; la descripcion de cinco etapas se conserva solo si queda rotulada como
el patron por canal. **Implementacion**: en `06:32` y `06:34`, reemplazar
"organizados en cinco etapas logicas" por "organizados en siete etapas funcionales"
(alineado al Anexo) y rotular el patron por canal como subconcepto, o unificar el
enumerado a siete etapas. **Alternativa descartada**: fijar cinco como canonico y
reducir el Anexo; se descarta porque la agrupacion de siete es la derivada del
export y es la mas completa. **Reversible**: si; es una decision editorial de
granularidad.

### D3 — Nodos: 29 operativos + 3 notas = 32 (no "26 + 3" ni "29")

`n8n/workflow.json` tiene 32 nodos: 3 `n8n-nodes-base.stickyNote` y 29 operativos.
`06:32` dice "29 nodos (26 operativos mas 3 notas adhesivas)": el total y el
subconteo operativo son incorrectos. `12-anexos.tex:45` dice "Los 29 nodos
operativos", correcto como conteo operativo, pero debe explicitar que hay 3 notas y
32 totales. **Regla**: "29 nodos operativos mas 3 notas adhesivas (32 nodos
totales)". **Alternativa descartada**: "29 totales"; se descarta porque ignora las
3 notas y contradice el conteo de 32. **Reversible**: no; el export es la fuente.

### D4 — SDK de Google: `google-genai` (no `google-generativeai`)

`App/Backend/requirements.txt:27,34` declara `google-genai>=2.20.0,<3` (SDK
unificado; reemplaza al deprecado `google-generativeai`). `05:74` y `06:10` ya usan
`google-genai` (correcto). `12-anexos.tex:88,105,108` usa `google-generativeai`
0.8 (stale). **Regla**: unificar a `google-genai`. **Observacion de version**:
`05:74` y `06:10` declaran ">=2.0", mientras `requirements.txt` declara
`>=2.20.0,<3`; la version se alinea a `>=2.20.0` (o al rango completo) al editar.
**Alternativa descartada**: conservar `google-generativeai` por fidelidad
historica; se descarta porque el anexo documenta la API efectivamente invocada y el
paquete real es `google-genai`. **Reversible**: no; correccion de exactitud.

### D5 — Registro del conteo canonico

Se registra el conteo fijado (D1-D4) en un memo de `docs/Tesis/Correcciones/`
(mismo patron que `numeros-canonicos.md` de c-102), para que c-104/c-105/c-106/
c-107/c-108/c-110 lo citen y no lo redefinan. El memo no es un `.tex` y no altera
la paginacion.

### D6 — Dependencia de secuencia

`c-109` comparte archivos con las ramas de contenido de la tesis:

- `05-arquitectura.tex` y `06-implementacion.tex`: compartidos con c-94
  (implementacion/verificabilidad, si existe) y con c-96 (citas/tablas).
- `12-anexos.tex`: compartido con c-80 (anexos) y c-76 (Anexo F).
- `c-107` (numeros canonicos) toca `00/01/04/07/08/09/10`; `c-108` (metricas) toca
  `07`. Sin solape con los conteos de c-109.

**Regla de secuencia**: aplicar c-109 **despues** de c-107 y c-108 (comparten el
documento y c-107 fija el marco numerico) y **despues** de c-80/c-94/c-96 si tocan
los mismos archivos, para evitar ediciones cruzadas sobre las mismas lineas.

## Objetivos de alineacion (ANTES -> DESPUES)

| Archivo | ANTES (palabra clave) | DESPUES (regla) |
|---|---|---|
| `06:72` | "el modelo de datos con sus seis entidades" | Sin conteo stale; referir el modelo vigente de siete entidades |
| `06:32` | "29 nodos (26 operativos mas 3 notas adhesivas)" | "32 nodos (29 operativos mas 3 notas adhesivas)" |
| `06:32` | "organizados en cinco etapas logicas" | "organizados en siete etapas funcionales" (o rotular cinco como patron por canal) |
| `06:34` | "patron de procesamiento en cinco etapas logicas" | "siete etapas funcionales" (o rotular como patron por canal) |
| `06:73` | "estableciendo el patron de cinco etapas" | Rotular como patron por canal, no como total del flujo |
| `12:45` | "Los 29 nodos operativos se organizan en siete etapas" | "Los 29 nodos operativos (mas 3 notas, 32 totales) se organizan en siete etapas" |
| `12:88` | "la API `google-generativeai` version 0.8" | "el SDK `google-genai` (`>=2.20.0`)" |
| `12:105` | "API & `google-generativeai` 0.8" | "SDK & `google-genai` `>=2.20.0`" |
| `12:108` | fuente "documentacion de la API `google-generativeai`" | fuente "documentacion del SDK `google-genai`" |
| `05:74` / `06:10` | "google-genai >=2.0" | "google-genai >=2.20.0" (alinear version) |
| `05:88` / `05:117` | "siete entidades principales" | INTOCABLE (ya canonico) |

## Risks / Trade-offs

- **[Riesgo] Confundir etapas del flujo con las etapas del pipeline de
  clasificacion.** `05:78,82` usa "dos etapas"/"tres etapas" para el clasificador
  hibrido. → **Mitigacion**: la regla de siete aplica SOLO a las etapas del flujo
  N8N; no se toca el pipeline de clasificacion.
- **[Riesgo] Presupuesto de paginas.** El PDF parte de 103 y el plan exige <= 100;
  c-109 no posee la reduccion. → **Mitigacion**: los cambios son sustituciones
  locales; compilar y registrar el conteo; si sube, usar la variante mas corta.
- **[Riesgo] Edicion cruzada con otras ramas.** Comparte `05/06/12`. →
  **Mitigacion**: aplicar despues de c-107/c-108 y coordinar con c-80/c-94/c-96
  (D6).
- **[Riesgo] Version del SDK imprecisa.** ">=2.0" vs ">=2.20.0". → **Mitigacion**:
  alinear a `>=2.20.0` al editar el nombre del paquete.

## Migration Plan

1. Fijar y registrar el conteo canonico (D1-D4, D5) leyendo el sistema.
2. Editar los `.tex` segun la tabla ANTES -> DESPUES (un pase por archivo).
3. Compilar con Docker (`texlive-thesis`) y confirmar cero errores fatales y
   conteo de paginas.
4. Verificar por busqueda que no queden "seis entidades", "cinco etapas",
   "26 operativos" ni `google-generativeai` como vigentes.
5. Revertir = `git checkout` de los `.tex` y del memo.

## Open Questions

- El conteo de etapas (siete) depende de adoptar la agrupacion funcional del
  Anexo como canonica; si el autor prefiere el patron de cinco por canal como
  descripcion principal, D2 se revisa (reversible) y se reduce el Anexo.
- No se fija aqui el numero de entidades "de soporte" (auditoria, telefonia,
  contadores): la tesis habla de "entidades principales" (siete); el conteo total
  de tablas del ORM es mayor y queda fuera de alcance.
