## Context

Ver `proposal.md` — Why. El dictamen CONEAU 2026-10-20 (dimensión 1, rec.
obligatoria 8) exige "reducir el resumen a 250 palabras; normalizar la acentuación
en todo el manuscrito". c-103 archivado difirió las tildes a este change. El
objetivo de c-106 es exclusivamente formal: acentuar prosa y recortar el resumen,
sin alterar cifras, claims ni estructura. Governance BAJO/MEDIO.

Alcance de archivos: los 14 `.tex` de `docs/Tesis/v9 (IA)/paper/sections/`. NO se
toca `preambles/preamble.tex`, `main.tex`, `Bibliography_base.bib` (c-104) ni la
ruta `docs/Tesis/`.

**Magnitud.** El diccionario del helper existente marca ~297 coincidencias de
palabras sin tilde en `sections/*.tex` (además de formas fuera de diccionario como
gerundios "realizandose"); hay ~300-400 correcciones esperables. Un cambio de esta
magnitud choca con casi todas las líneas: de ahí la exigencia de tokens
protegidos explícitos y de una verificación mecánica.

## Goals / Non-Goals

**Goals:**

- Acentuar el texto español de los 14 `sections/*.tex` sin tocar tokens protegidos.
- Reducir el resumen en español a `≤ 250` palabras y alinear el abstract.
- Compilar y no aumentar el conteo de páginas (hoy 103).

**Non-Goals:**

- No editar `Bibliography_base.bib`, `main.tex`, `preambles/` ni la ruta `docs/Tesis/`.
- No reescribir cifras/claims (los posee c-107 y sus pares).
- No re-ejecutar clasificador ni llamar a Gemini/N8N/Twilio.
- No "des-acentuar" ni normalizar a ASCII; no tocar texto ya correcto.

## Decisions

### D1 — Alcance textual (IN scope)

Se acentúan únicamente segmentos de **prosa española**:

- Cuerpo de párrafos, ítems de listas, pies de página y notas.
- **Texto dentro de argumentos de comandos portadores de texto**: `\section{}`,
  `\subsection{}`, `\caption{}`, `\textbf{}`, `\emph{}`, `\item`, celdas de
  `tabular`, `\footnote{}`. (El helper actual NO acentúa dentro de `{}`; es una de
  las razones para adaptarlo — D3.)
- Encabezados y rótulos de la portada y del resumen (`00-portada.tex`,
  `00-resumen.tex`) que hoy están sin tilde (p. ej. "Introduccion", "Republica").

### D2 — Tokens protegidos (OUT of scope, allowlist)

MUST NOT modificarse (allowlist explícita, verificada mecánicamente):

1. **Cadenas canónicas de categorías** (exactas, case-sensitive, SIN tilde):
   `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`,
   `Bases de Datos`, `Sistemas`. Son identificadores de dominio (C-27); cualquier
   tilde rompe el corpus y el clasificador.
2. Claves dentro de `\label{}`, `\ref{}`, `\autoref{}`, `\cref{}`, `\eqref{}`.
3. Claves de `\cite{}`, `\textcite{}`, `\parencite{}` (bibliografía).
4. Rutas de `\input{}`, `\includegraphics{}`, `\bibliography{}`.
5. Rutas/identificadores de repositorio en prosa: `docs/Tesis/`, `evaluation/`,
   `data/`, `App/Backend`, `n8n/workflow.json`, `docs/openapi.json`,
   `gemini-3.6-flash`, `requiere_revision_humana`, `canal_origen_id`.
6. Entornos `verbatim`/`lstlisting`/`minted` y `\verb|...|`.
7. URLs, DOI y correos.
8. Matemática: `$...$`, `\(...\)`, `\[...\]`, `\begin{equation}`.
9. Nombres de comandos LaTeX (`\section`, `\textbf`, etc.).
10. Palabras ya acentuadas: MUST preservarse (no re-acentuar ni des-acentuar).
    Pares sensibles: `hipótesis`, `síntesis`, `análisis`, `metodología` — MUST
    conservarse exactamente; ninguna regla puede convertirlos a su forma sin tilde
    ni duplicar tildes.

### D3 — Evaluación de `docs/Tesis/acentuar_tesis.py`

**No es usable tal cual; es reutilizable con adaptación.** Hallazgos:

- **Ruta equivocada**: `PAPER_DIR = "v8 (IA)/paper"` (línea 18). Debe apuntar a
  `v9 (IA)`.
- **No acentúa dentro de `{}`**: `_extraer_comando_latex` copia el comando y sus
  argumentos verbatim, de modo que `\section{Introduccion}` y `\caption{...}` no se
  corrigen. Sub-cobertura severa.
- **Sin allowlist**: su diccionario es case-sensitive con claves en minúscula, de
  modo que hoy no corrompe las cadenas de categorías (Capitalizadas), pero no hay
  garantía por diseño; una variante en minúscula o un cambio a case-insensitive
  corrompería `Soporte Tecnico Hardware/Software`.
- **Escribe `.tex.bak`** por archivo: residuos versionables no deseados.
- El diccionario y el tokenizador consciente de comandos son valiosos como base.

**Decisión**: adaptar el helper (retarget a v9, acentuar dentro de argumentos de
texto, agregar allowlist de tokens protegidos, sin `.bak`) o escribir un pase
único equivalente. Alternativa descartada: `sed` global — corrompe tokens
protegidos. Alternativa descartada: usar el helper tal cual — ruta v8 y
sub-cobertura.

### D4 — Regla de no-regresión

Ninguna corrección puede (a) des-acentuar, (b) duplicar tildes, (c) tocar tokens
protegidos, (d) alterar dígitos, `%`, `~`, `$`, `\` ni comandos. La verificación
(D8) compara el diff contra la allowlist.

### D5 — Reducción del resumen a ≤ 250 palabras

El resumen español tiene ~538 palabras; debe caer a `≤ 250`. Regla: comprimir los
cinco párrafos conservando (i) problema, (ii) método/diseño (200 casos pareados),
(iii) resultados clave (61,6 s → 17,76 s, 71,2 %, `W=363`, `r=0,9639`, exactitud
73,5 %, macro-F1 0,5207, Kappa 0,87) y (iv) conclusión, y descartando detalle
secundario (listas de componentes, canal por canal). El texto de partida es la
versión ya corregida por c-107 (que retira el 9,5 %, adopta `≈ 2.646` y declara la
hipótesis parcialmente confirmada/refutada); c-106 MUST NOT reintroducir valores
retirados.

**Regla de conteo**: cuentan las palabras de prosa del cuerpo del resumen; NO
cuentan comandos LaTeX, la línea "Palabras clave" ni su contenido, ni la
puntuación suelta.

### D6 — Consistencia del abstract

El abstract (`00-resumen.tex:25`) MUST quedar `≤ 250` palabras y cubrir la misma
información que el resumen reducido (mismos números, mismas categorías, mismo
estado de hipótesis). El cambio MUST respetar la coherencia terminológica del
requisito "English abstract" vigente.

### D7 — Secuenciación

c-106 MUST aplicarse **después** de los changes que editan prosa en
`sections/*.tex`: c-104 (bibliografía), c-105 (reubicación del cap. 11), c-107
(números canónicos, que edita `00-resumen.tex`, `01`, `04`, `07`, `08`, `09`,
`10`) y los planificados c-108/c-109/c-110. Motivo: la acentuación choca con casi
todas las líneas y la reducción del resumen consume la versión de c-107.
Alternativa descartada: aplicar c-106 primero — obligaría a re-acentuar tras cada
change posterior.

### D8 — Verificación

- **Tokens protegidos**: `rg` de control de las cinco cadenas de categorías y de
  claves `\label`/`\ref`/`\cite` antes y después; el conjunto de claves MUST ser
  idéntico.
- **Sin residuos**: `git diff` MUST NOT mostrar cambios en líneas que contengan
  solo tokens protegidos; MUST NOT aparecer `.tex.bak` nuevos.
- **Palabras del resumen**: conteo reproducible (script de conteo de prosa) `≤ 250`.
- **Compilación**: imagen `texlive-thesis`,
  `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`;
  cero errores fatales; cero "undefined reference" nuevas.

### D9 — Presupuesto de páginas

El resumen más corto puede **reducir** el conteo de páginas. c-106 MUST NOT
aumentarlo y MUST registrar el conteo final. El requisito "103 páginas (±0)" de
c-103 está acotado a la portada; c-106 no lo fuerza.

### D10 — Capacidades modificadas

Se modifica UNA capacidad: `tesis-document`. Alternativa descartada: crear una
capacidad nueva — la acentuación y el resumen son criterios de calidad del mismo
documento ya cubierto por `tesis-document`.

## Risks / Trade-offs

- **[Riesgo] Corromper cadenas de categorías.** `Soporte Tecnico` con tilde rompe
  corpus/clasificador. → **Mitigación**: allowlist D2 + verificación D8.
- **[Riesgo] Corromper `hipótesis`/`síntesis` u otro par sensible.** → **Mitigación**:
  D2.10 + diff revisado por palabra completa.
- **[Riesgo] Churn masivo e irrevisable.** ~300-400 cambios. → **Mitigación**: pase
  mecánico con allowlist + verificación de conjuntos de claves + conteo.
- **[Riesgo] Reducción del resumen que borre una cifra exigida.** → **Mitigación**:
  D5 lista los números que MUST sobrevivir; verificación por `rg` de cada uno.
- **[Riesgo] Conflicto con c-104/c-105/c-107.** → **Mitigación**: D7 (aplicar al
  final).
- **[Riesgo] Sub-cobertura por no acentuar dentro de `{}`.** → **Mitigación**: D3.

## Migration Plan

1. Aplicar c-106 último, con el árbol limpio y los changes previos ya aplicados.
2. Adaptar/escribir el pase de acentuación con allowlist (D2/D3); correr en
   dry-run y revisar el diff de tokens protegidos.
3. Aplicar el pase; reducir el resumen y alinear el abstract (D5/D6).
4. Verificar tokens protegidos, claves, conteo de palabras y compilación (D8).
5. Revertir = `git checkout` de `sections/*.tex` (sin otros artefactos).

## Open Questions

Ninguna que cambie las specs. La decisión de conservar o retirar el helper
(`acentuar_tesis.py`) tras la adaptación queda a criterio del apply.
