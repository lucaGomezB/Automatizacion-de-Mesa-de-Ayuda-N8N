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

### D-A1 — Declarar la convención de `W` y reportar ambos estadísticos

Se declara explícitamente la convención: `W = min(T+, T−)` (equivalente al
estadístico de dos colas de `scipy.stats.wilcoxon`). Se reportan `T+` y `T−`, no
un único `W` sin definición. **Alternativas**: (a) `W=T+` (suma de rangos
positivos), (b) `W=min(T+,T−)`. Se elige (b) por ser la que el código y scipy ya
producen y por ser invariante al signo del contraste. La tesis SHALL enunciar la
convención antes de citarla.

### D-A2 — Corregir fórmula, rango y recálculo del tamaño del efecto

Fórmula correcta: `r = (T+ − T−) / (n(n+1)/2)`, equivalente a
`1 − 4W/(n(n+1))` cuando `W=T−=min`. Rango real `[0,1]` para un contraste
unidireccional con esa normalización (la forma que admite `[-1,+1]` es
`(T+−T−)/(T++T−)`, que también da 0,9667 aquí). Recálculo sobre el corpus real:
`r=0,9667` (no `1,00`). Cotejo del código: `evaluation/stats.py:78` calcula
`(concordantes−discordantes)/total = 188−12/200 = 0,88`, que no coincide ni con
la tesis ni con la fórmula corregida → el código MUST alinearse.

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

### D-C4 — Reintentos (OQ)

Código real: sin `retryOnFail`/`maxTries` en `n8n/workflow.json`; la única
lógica de reintento es idempotencia de telefonía
(`App/Backend/app/services/telefonia_service.py`). Se reescribe `06:60` como
limitación conocida + trabajo futuro (recomendado) o se implementa. OQ.

### D-C5 — Nginx/TLS (OQ)

`nginx/nginx.conf:70` habilita `TLSv1.2 TLSv1.3`; el servicio `nginx` no está
bajo profile (`docker-compose.yml:234`); C-20 (2026-07-03). Se reconcilia la
redacción condicional de 5.1/9.1/11.4/Anexo A (declarar TLS 1.2+1.3, no solo
1.3) o se reafirma el estado publicado. OQ.

### D-C6 — Residuos de C-18 + anexo de log

Residuos confirmados: `IMAP` (`06:37`, `12:37`) vs Graph API (`05:20,40`);
catálogo "tres sectores" (`05:76`, `01:46,68`). Se cierran y se anexa el log de
decisiones `docs/Tesis/Correcciones/dictamen-correcciones.md` como Anexo. Los
otros 4 gaps de C-18 (pgcrypto, HMAC, retención, `/clasificar`) ya están
alineados en el árbol.

### D-C7 — Sectores del prompt (OQ)

`docs/prompt_gemini.txt:5-25` define 5 sectores canónicos (c-27); la tesis
declara 3 (`01:46,68`; `04:33,36`; `05:76,78`; Cap. 7). Se unifica a los 5
canónicos. **Alternativas**: (a) alinear tesis a 5; (b) justificar/documentar la
discrepancia. OQ (se recomienda (a)).

### D-C8 — Tag (OQ)

`12:19` referencia el tag `v1.0.0`; `git tag` no devuelve ninguno. Crear el tag
con el hash completo en el Anexo B o corregir el Anexo al tag/hash real. OQ
(crear un tag es acción del autor).

### D-B1 / D-B2 — Pregunta de investigación humana (OQ)

B1: medir la clasificación manual sobre el mismo corpus o retirar la
sub-pregunta y reformular H1. B2: explicar la relación entre la medición
preliminar (165 s) y la experimental (ahora 61,6 s), mostrando el registro que
sostiene el tiempo. OQ.

## Risks / Trade-offs

- Tocar `.tex` sin compilador local → mitigar con `openspec validate` + revisión
  en Overleaf (tarea de recompilación) y `rg` de control.
- Riesgo de solapamiento con c-76 → mitigado: c-77 solo profundiza lo
  inferencial/aritmético/técnico; los números del corpus se referencian a c-76.
- Cambiar la fórmula del efecto altera el claim `r=1,00` → mitigado con el
  recálculo explícito y el reporte de ambos estadísticos.

## Migration Plan

1. Editar `.tex` por capítulo y `evaluation/stats.py` (si el autor aprueba).
2. `evaluation/report.md` y `docs/prompt_gemini.txt` si aplica.
3. Recompilar en Overleaf; verificar PDF sin errores fatales.
4. Rollback: `git checkout --` / `git revert`.

## Open Questions

- **A1/A2**: ¿qué convención de `W` prefiere el autor declarar (`min(T+,T−)`
  recomendado, o `T+`)? ¿Se adopta `r=(T+−T−)/(n(n+1)/2)=0,9667` o la variante
  `(T+−T−)/(T++T−)`?
- **B1**: ¿medir el criterio humano o retirar la sub-pregunta y reformular H1?
- **C4**: ¿reescribir `06.5` como limitación + trabajo futuro, o implementar el
  reintento/cola?
- **C5**: ¿redacción condicional en la tesis o agregar el proxy (ya presente) al
  compose publicado?
- **C7**: ¿unificar la tesis a 5 sectores canónicos (recomendado) o
  justificar/documentar los 3?
- **C8**: ¿crear el tag `v1.0.0` (acción del autor) o corregir el Anexo B al
  tag/hash real?
