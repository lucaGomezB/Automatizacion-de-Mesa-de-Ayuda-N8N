# Design: c-77 — Errores estadístico-inferenciales y coherencia técnica

## Context

Ver `proposal.md` — Why. Estado relevante confirmado contra el árbol de trabajo
(2026-10-09) y el corpus real (`data/corpus_evaluacion_pseudonimizado.json`,
`evaluation/predicciones.json`, `evaluation/report.md`):

- Cap. 4/7/8/9 conservan la convención y fórmula del efecto del corpus sintético
  descartado: `W=0`, `r=1−2W/(n(n+1))=1,00`, rango declarado `[-1,+1]`.
- Datos reales de tiempos (n=200, todos pares no nulos): `T+=19765`, `T−=335`,
  `n(n+1)/2=20100`; scipy two-sided devuelve `335`; `p=2,05e-32`; 12/200 pares
  invertidos.
- La confianza del clasificador está anti-calibrada (ver Datos A6).
- No existe ninguna tabla/curva de calibración en la tesis.
- c-72 ya alineó C1/C2; c-20 ya agregó nginx/TLS.

Restricción dura: la tesis se compila en Overleaf (sin toolchain LaTeX local) y
c-77 no debe tocar `App/**` salvo decisión explícita del autor.

## Goals / Non-Goals

**Goals:**

- Corregir el aparato estadístico-inferencial de la tesis (convención, fórmula,
  rango, recalculo) y hacerlo ejecutable/verificable contra el corpus real.
- Añadir el reporte de calibración de la confianza y su discusión.
- Corregir la aritmética metodológica (horas-persona, universo trimestral,
  rótulos, proporción de intervención).
- Cerrar residuos de coherencia técnica tesis–implementación (C6) sin duplicar
  el alcance de c-76.

**Non-Goals:**

- No reemplazar los números del corpus ni el redondeo de tiempos (c-76).
- No implementar cambios en `App/**` (reintentos, canal, Nginx): se resuelven
  como decisión del autor.
- No recompilar localmente (Overleaf).

## Decisions

### D-A1 — Definir el tamaño del efecto directamente; reportar `T+` y `T−` (OQ1 = c)

**Decisión del autor (OQ1 = c):** no se usa un `W` ambiguo. La tesis SHALL reportar
explícitamente `T+` (suma de rangos positivos = 19765) y `T−` (suma de rangos
negativos = 335), y definir el tamaño del efecto directamente como el
rank-biserial `r = (T+ − T−)/(n(n+1)/2)`, con rango real `[−1,+1]`. Se menciona
que `scipy.stats.wilcoxon` (dos colas) devuelve `335`, para trazabilidad.

### D-A2 — Corregir fórmula, rango y recálculo del tamaño del efecto

Fórmula correcta: `r = (T+ − T−) / (n(n+1)/2)` = `(T+ − T−)/(T+ + T−)`, rango
real `[−1,+1]`. Recálculo sobre el corpus real: `r = 19430/20100 = 0,9667`
(no `1,00`). Cotejo del código: `evaluation/stats.py:78` calcula
`(concordantes−discordantes)/total = (188−12)/200 = 0,88`, que no coincide ni con
la tesis ni con la fórmula corregida → el código MUST alinearse a `r=0,9667`.

### D-A3 — Rótulo de dispersión

`08:12` compara desvíos estándar (38,7 s vs 4,1 s; razón ≈9,4) y no varianzas
(razón ≈89). Se corrige el término a "desvío estándar" y, si se cita la razón, se
declara que es sobre desvíos.

### D-A4 — Aritmética de horas-persona

Se elimina la proyección "180 h-persona" o se documenta su cálculo en nota al
pie. Cálculos verificados: 3700/42=88,1 días (incompatible con un trimestre
laborable); con tiempos de la tesis `(165,3−18,2)s×3700/3600≈151,2 h`; con datos
reales `(61,6−14,8)s×3700/3600≈48,1 h`; 180 h implicaría 175 s ahorrados por
incidente, que no corresponde a ningún escenario. Se adopta el valor real con el
cálculo explícito. **Alternativa**: conservar 180 h con una base declarada — se
descarta por no ser reproducible.

### D-A5 — Definición única de "intervención humana"

Se unifica midiendo y reportando ambos: proporción de tiempo (definición de la
Tabla 2) y proporción de casos (9,5 % = 19/200). **Alternativa**: elegir una sola
— se descarta porque ambas son informativas y ya están calculadas.

### D-A6 — Reporte de calibración

Se agrega una subsección de calibración en Cap. 7 y su discusión en Cap. 8,
con la tabla de contingencia alta/baja confianza × acierto/error y/o la curva de
calibración, cuyos valores reales son: alta (≥0,70): 0,697 (53/76); baja
(<0,70): 0,758 (94/124); 13/46 predicciones con confianza ≥0,90 son errores;
bins: [0;0,5)=0,765; [0,5;0,7)=0,731; [0,7;0,85)=0,333; [0,85;0,95)=0,710;
[0,95;1,0)=0,744. Se discute la implicancia para el gate 0,70 en 6.3/7.3/11.5.

### D-A7 — Universo trimestral

Se declara el número de días del trimestre observado y su naturaleza (calendario
vs laborables). 3.700 = 42×88; un trimestre laborable (63–66 días) da
2.646–2.772. Se reconcilia el texto sin inventar un volumen distinto.

### D-C1 / D-C2 — Sin cambio (ya alineados)

`06:39-40` describe clasificar → gate; el agente LLM telefónico fue removido
(`05:60`, `06:44`, `09:14`, c-72). Se documenta como verificado; solo se corrige
el residuo `IMAP` (ver D-C6).

### D-C3 — Campo de canal

El backend SÍ recibe el canal (`App/Backend/app/schemas/incidente.py:162`,
`canal_origen_id: int | None`; `n8n/workflow.json:101`). Se alinea el nombre de
campo stale del Cap. 5 (`id_canal` → `canal_origen_id`). **Decisión**: documentar
que el canal es entrada opcional del backend, no reescribir la arquitectura.

### D-C4 — Reintentos (RESUELTO: OQ3 = b)

Código real: sin `retryOnFail`/`maxTries` en `n8n/workflow.json`; la única
lógica de reintento es idempotencia de telefonía
(`App/Backend/app/services/telefonia_service.py`). **Decisión del autor (OQ3=b):**
se reescribe `06:60` como **limitación conocida + trabajo futuro**; NO se
implementa el reintento/cola en el código.

### D-C5 — Nginx/TLS (RESUELTO: OQ4 = a)

`nginx/nginx.conf:70` habilita `TLSv1.2 TLSv1.3`; el servicio `nginx` no está
bajo profile (`docker-compose.yml:234`); C-20 (2026-07-03). **Decisión del autor
(OQ4=a):** redacción **condicional** de 5.1/9.1/11.4/Anexo A — distinguir el
diseño (proxy Nginx + TLS 1.2/1.3) del despliegue efectivamente publicado, que no
lo incluía. No se despliega el proxy en esta ronda.

### D-C6 — Residuos de C-18 + anexo de log

Residuos confirmados: `IMAP` (`06:37`, `12:37`) vs Graph API (`05:20,40`);
catálogo "tres sectores" (`05:76`, `01:46,68`). Se cierran y se anexa el log de
decisiones `docs/Tesis/Correcciones/dictamen-correcciones.md` como Anexo. Los
otros 4 gaps de C-18 (pgcrypto, HMAC, retención, `/clasificar`) ya están
alineados en el árbol.

### D-C7 — Sectores del prompt (RESUELTO: OQ5 = b)

`docs/prompt_gemini.txt:5-25` define 5 sectores canónicos (c-27); la tesis
declara 3 (`01:46,68`; `04:33,36`; `05:76,78`; Cap. 7). **Decisión del autor
(OQ5=b):** alinear la TESIS a los **5 sectores canónicos** (no unificar el prompt
a 3). Debe quedar consistente con c-76.

### D-C8 — Tag (RESUELTO: OQ6 = diferido)

`12:19` referencia el tag `v1.0.0`; `git tag` no devuelve ninguno. **Decisión del
autor (OQ6):** **diferir** la creación del tag: se hará como **v1.0.0 al terminar
estas correcciones** (c-76 + c-77), sobre el commit entregado, y entonces se
consignará el **hash completo** en el Anexo B. Se deja constancia de la acción
pendiente (ver `docs/Tesis/Correcciones/dictamen-correcciones.md`).

### D-B1 / D-B2 — Pregunta de investigación humana (RESUELTO: OQ2 = c)

**Decisión del autor (OQ2=c):** se **retira** la sub-pregunta sobre la exactitud
humana (`01:28`) y se **reformula `H1`** (`01:32-34`) para quitar la comparación
con el criterio humano; la exactitud se contrasta contra el umbral objetivo
(≥85 %), no contra el operador. Motivo: no existen los etiquetados por analista
necesarios para medirla y no se agrega fieldwork.
B2 (independiente, no OQ): explicar la relación entre la medición preliminar
(165 s) y la experimental (ahora 61,6 s), mostrando el registro que sostiene el
tiempo.

### D-D1 — Descripción de metadata del corpus fiel a los datos

La descripción `metadata.descripcion` de `data/corpus_evaluacion_pseudonimizado.json`
declara "tiempos automatizados pendientes de medicion end-to-end", pero los 200/200
valores de `tiempo_automatizado_s` están medidos end-to-end (derivados de timestamps
de la base). Se corrige la cadena para eliminar la cláusula falsa y declarar que los
tiempos automatizados están medidos (y que los tiempos manuales son los de
clasificación manual). **Restricción**: la corrección es solo textual; no altera
ningún valor numérico ni el total de casos (200) y no duplica el alcance de c-76
(números/redondeo).

## Grupo E — Tiempo automatizado telefónico comparable (Opción A)

### D-E0 — Asimetría de medición y decisión del autor (Opción A)

El tiempo manual telefónico incluye escuchar la llamada (media ≈87,25 s); el
automatizado mide solo `persistido_en − ingresado_en` (media ≈12,83 s), porque
`ingresado_en` se fija en el callback de grabación de Twilio, que dispara AL COLGAR
(`App/Backend/app/services/telefonia_service.py:272-273,399`), excluyendo la duración
de la llamada (`docs/medicion-latencia-e2e.md:59-65`). **Decisión del autor
(2026-10-12):** implementar la **Opción A** dentro de c-77 — sumar la duración de la
grabación para igualar conceptualmente la base de comparación:

`tiempo_automatizado_s(telefono) = duracion_segundos + latencia_e2e_ms/1000`

### D-E1 — Exponer `duracion_segundos` en la API de lectura

`duracion_segundos` existe en `App/Backend/app/models/telefonia_ingreso.py:94-96`
(Twilio `RecordingDuration`) pero no se expone: `TelefoniaIngresoRead`
(`App/Backend/app/schemas/telefonia.py:69-87`) lo omite y `_ingreso_to_read`
(`App/Backend/app/routes/telefonia.py:249-258`) no lo proyecta. Se agrega el campo
(opcional) y la proyección. Como cambia el contrato de la API, **MUST** regenerarse
`docs/openapi.json`; el test `tests/test_openapi_sync.py` lo verifica.

### D-E2 — Derivación y recomputo de los 81 casos telefónicos

`scripts/corpus_ingest/ingest_telefonia_corpus.py` (`derive_telefonia_metric` /
`build_telefonia_result`, ~:85-134) se extiende para sumar `duracion_segundos` a la
latencia end-to-end y recomputar los 81 casos telefónicos del corpus. **Prerrequisito
de datos:** `duracion_segundos` no está en el sidecar
`data/corpus_resultados_telefonia.json`; las 81 filas viven en el backup del volumen
`backups/vol_mesa_local_postgres_corpus_data_20261009T141330.tgz`, que debe restaurarse
en una instancia Postgres para leer la columna.

### D-E3 — Datos corregidos

Se actualizan las 81 filas telefónicas de
`data/corpus_evaluacion_pseudonimizado.json` y el sidecar
`data/corpus_resultados_telefonia.json`. Los 119 casos de web/correo **MUST NOT**
modificarse (su tiempo automatizado sigue siendo la latencia end-to-end).

### D-E4 — Pruebas (TDD, test-first)

Se escriben primero los tests: (a) `TelefoniaIngresoRead` expone `duracion_segundos` y
`_ingreso_to_read` lo proyecta; (b) `derive_telefonia_metric` devuelve
`duracion_segundos + latencia_e2e_ms/1000`; (c) un caso sin duración no rompe la
derivación; (d) web/correo no se ven afectados. Seguir el ciclo RED → GREEN →
TRIANGULATE descrito en `tasks.md`.

### D-E5 — Reconciliación del texto de la tesis y cota inferior

`docs/Tesis/v9 (IA)/paper/sections/07-resultados.tex` (tabla de tiempos por canal) y,
si describe el tiempo automatizado telefónico, `04-marco-metodologico.tex` se
reconcilian con la métrica corregida. **Cota inferior (registro explícito):** la
grabación está acotada a 45 s por `<Record maxLength="45">` (`n8n/twilio/twiml.xml`),
por lo que `duracion_segundos` es una cota inferior de la duración real de la llamada
y el tiempo automatizado telefónico resultante es una **cota inferior** del tiempo
automatizado comparable. El texto MUST declararlo.

### D-E6 — Delta spec

Se extiende `specs/evaluation-framework/spec.md` con un requerimiento/escenario que
exige que el tiempo automatizado telefónico incluya la duración de llamada/grabación y
que web/correo queden sin cambio, más la cota inferior por el tope de 45 s.
`specs/tesis-document/spec.md` recibe el escenario de la declaración de cota inferior en
el documento.

### D-E7 — Cross-reference con c-80

La figura 7 de c-80 (boxplot por canal) consume esta métrica corregida. El orden de
aplicación es duro: c-76 → c-77 → c-78 → c-79 → c-80; c-80 aplica **después** de c-77.

## Risks / Trade-offs

- Tocar `.tex` sin compilador local → mitigar con `openspec validate` + revisión
  en Overleaf (tarea de recompilación) y `rg` de control.
- Riesgo de solapamiento con c-76 → mitigado: c-77 solo profundiza lo
  inferencial/aritmético/técnico; los números del corpus se referencian a c-76.
- Cambiar la fórmula del efecto altera el claim `r=1,00` → mitigado con el
  recálculo explícito y el reporte de ambos estadísticos.
- **Cota inferior del tiempo telefónico (Riesgo E):** el tope de 45 s de la grabación
  (`<Record maxLength="45">`) hace que `duracion_segundos` sea una cota inferior de la
  duración real; el tiempo automatizado telefónico corregido SUBESTIMA el tiempo
  comparable. Mitigación: declarar la cota explícitamente en tesis, diseño y spec, y no
  presentar el valor como igualación exacta.
- **Dependencia de datos (Riesgo E):** `duracion_segundos` solo está en el backup del
  volumen Postgres; sin restaurarlo no hay insumo. Mitigación: el prerrequisito queda
  como tarea explícita (E2.1) y el resultado se marca bloqueado hasta disponer de él.

## Migration Plan

1. Editar `.tex` por capítulo y `evaluation/stats.py` (si el autor aprueba).
2. `evaluation/report.md` y `docs/prompt_gemini.txt` si aplica.
3. Recompilar en Overleaf; verificar PDF sin errores fatales.
4. Rollback: `git checkout --` / `git revert`.

## Open Questions

Ninguna abierta. Todas resueltas por el autor (2026-10-09): OQ1=c (D-A1/D-A2),
OQ2=c (D-B1), OQ3=b (D-C4), OQ4=a (D-C5), OQ5=b (D-C7), OQ6=diferido (D-C8).

Grupo E (2026-10-12): la decisión es la Opción A. **OQ-E1 (no bloqueante):** forma de
presentación de la cota inferior en la tabla de resultados del canal telefónico
(nota al pie vs. columna rotulada). Se prefija la nota al pie en D-E5; si el autor la
prefiere rotulada, no altera el cálculo. No hay OQ bloqueante para planificar.
