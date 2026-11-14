## Context

Ver `proposal.md` — Why. El change parte de la release `v1.3.0` tal como la midió el dictamen
CONEAU del 2026-11-13. Los insumos ya existen y están versionados:

- **Corpus y predicciones arbitradas**: `evaluation/data/campana/corpus_independiente_arbitrado.json`
  (`206` casos), `predicciones_arbitrado.json` (`hybrid-v3` congelado, `142/206` estrictos, macro-F1
  `0,7024`), `doble_etiquetado_arbitrado.csv` (`476` filas: `E3` y `E4` sobre los `206`, `E5` sobre
  los `64` discordantes) y `arbitraje_tres_vias.json` (`142` de consenso `E3`/`E4`, `64` arbitrados
  por `E5`, `6` de tres vías).
- **Etapa determinística**: el filtro `V1` tiene `151` patrones (`keywords.py`); su cobertura sobre
  los `206` es `131` casos, cortocircuita `115` y acierta `88/115` (`0,7652`), reproducido contra
  `predicciones_arbitrado.json`. Los `62` patrones añadidos «del corpus» (los bloques `c-71` del
  código) equivalen al vocabulario previo `V0` (`89` patrones), ya medido por c-142 (memo 3.10).
- **Sensibilidad de vocabulario existente (c-142)**: `V0 + L1` cortocircuita `74` casos con `39`
  aciertos (`0,5270`); la diferencia de `21,3` puntos es una **cota pesimista** y una
  **interpretación de los autores**, y la salvedad admite que `V0` pudo ajustarse con el corpus.
- **Ruido de referencia (c-216)**: simulación calibrada al kappa `0,6055`; no desagrega por
  robustez de la referencia.
- **Fuente externa disponible**: `App/Backend/app/constants.py` define las cinco clases canónicas y
  el glosario de dominio; la bibliografía revisada (ITIL 4, catálogos de servicio) aporta el
  vocabulario externo.

## Goals / Non-Goals

**Goals:**

- Producir una medición offline, reproducible y preregistrada del sesgo del vocabulario del filtro
  atribuible a su ajuste con el mismo corpus, con un vocabulario derivado de una fuente externa y
  fijado antes de medir.
- Acotar cuánto de la exactitud depende de la robustez de la referencia, separando el subconjunto de
  consenso del arbitrado.
- Registrar todo en el memo canónico (3.29) y en la tesis (04/07/08) sin cambiar ningún número
  canónico.

**Non-Goals:**

- No reclasificar el corpus, no reentrenar, no cambiar el vocabulario `V1`, el prompt ni los
  umbrales.
- No ejecutar trabajo de campo ni una corrida paga sin autorización escrita del dueño (ver OQ1).
- No resolver las demás amenazas del criterio 4 (instrumentos asimétricos, orden fijo de los brazos,
  exclusión), ya atendidas por otros changes.
- No presentar la ablación como una «exactitud corregida» ni el análisis de subconjuntos como
  causalidad de la referencia.

## Decisions

### D1 — Vocabulario corpus-blind derivado de una fuente externa

Se construye un vocabulario alternativo `V_lit` a partir de (i) la taxonomía sectorial canónica
(`app/constants.py`) y (ii) un glosario público de mesa de ayuda / ITIL 4, **sin leer las
descripciones del corpus**. Se fija y versiona en
`evaluation/data/campana/analisis/vocabulario_corpus_blind_c219.json` con su fuente, el
procedimiento de derivación y su SHA-256, **antes** de la corrida que produce las mediciones. La
independencia es **procedimental** (prerregistro): no se inspeccionó el corpus al derivarlo; el
análisis MUST NOT afirmar que sus términos no aparezcan en el corpus.

Alternativas descartadas: (a) usar el vocabulario previo `V0` como «independiente» —ya lo hizo
c-142 y su salvedad admite que pudo ajustarse con el corpus; (b) derivar el vocabulario por pliegues
del corpus —la tesis ya declara que no es factible porque no se registra qué caso motivó cada
patrón; (c) un vocabulario traducido de una fuente en inglés —reintroduce juicio de traducción no
auditable, salvo que la fuente sea ya en español.

### D2 — Unidad de medición offline y frontera hacia el híbrido completo

La ablación se mide sobre la **etapa determinística** (regex pura, sin LLM), que es offline y sin
costo. El análisis re-implementa el conteo de matches importando `KEYWORD_MAP` de forma liviana
(`app.constants` no arrastra `get_settings`), evitando credenciales. Para cada vocabulario informa
cobertura, cortocircuito, precisión con IC de Wilson y delta frente a `V1`.

**Frontera offline/paid.** Propagar el vocabulario alternativo al **híbrido completo** (extremo a
extremo) requiere predicciones de Gemini para los casos que pasan a escalar, que no están en la
caché (esta solo cubre los `91` casos escalados por `V1`). Esa propagación es una **corrida paga
acotada** (ver OQ1) y por defecto **no** se ejecuta: el alcance offline es suficiente evidencia
nueva. Si se autoriza, se rotula como corrida separada y no reemplaza `142/206`.

### D3 — Subconjunto de alto acuerdo: definición precisa y conjunto vacío declarado

El subconjunto de alto acuerdo es el **consenso `E3` = `E4`** (`origen = consenso_e3_e4`, `n = 142`),
donde la referencia no requiere árbitro. Se contrasta con el **arbitrado por `E5`**
(`origen = arbitraje_e5`, `n = 64`) y con el total (`206`). Se informa además el subconjunto de
discordancia de tres vías (`n = 6`). **Hallazgo verificado**: el subconjunto literal `E3` = `E4` =
`E5` es **vacío** (`0` casos), porque `E5` solo etiquetó los `64` discordantes; se declara como
hallazgo y no se fuerza un subconjunto artificial. Las exactitudes esperadas (a reproducir) son
`109/142` (`0,7676`, IC `[0,6916; 0,8295]`), `33/64` (`0,5156`, IC `[0,3958; 0,6337]`) y `142/206`
(`0,6893`, IC `[0,6231; 0,7486]`). No se afirma causalidad de la referencia.

### D4 — Artefacto, determinismo y pruebas

Script nuevo `evaluation/data/campana/analisis/analisis_sesgo_corpus_referencia_c219.py`, de solo
lectura, reutilizando `evaluation/metrics.py` (`intervalo_wilson`) cuando aplique; sin red ni
Gemini. Salidas `.json`, `.md` y `.SHA256SUMS.txt` en la misma carpeta, UTF-8 sin BOM y LF. Dos
corridas idénticas byte a byte; el script imprime los SHA-256. Antes de medir, aborta si no
reproduce `115`/`88` (etapa determinística) y `142/206` (híbrido). Pruebas unitarias de las
funciones puras (adaptador de scoring, cobertura/precisión, construcción de subconjuntos, Wilson)
con casos sintéticos, incluida la reproducción de los anclajes y del conjunto vacío de tres vías.

### D5 — Ubicación en la tesis y presupuesto de páginas

- `04-marco-metodologico.tex`: párrafo de método (ablación con vocabulario externo, independencia
  procedimental; subconjunto de consenso vs arbitrado) junto al protocolo fuera de muestra.
- `07-resultados.tex`: subsección `subsec:sesgo-corpus-referencia` después de
  `subsec:sensibilidad-ajustes`, con dos tablas compactas (cobertura/precisión por vocabulario;
  exactitud por subconjunto) y dos párrafos de lectura.
- `08-discusion.tex`: un párrafo en limitaciones que lee ambos resultados como sensibilidad y
  declara que no eliminan las amenazas del criterio 4.
- **Presupuesto**: crecimiento neto `≤ 2` páginas, registrado en `dictamen-correcciones.md`.

### D6 — Decisión del dueño: offline por defecto, corrida paga opcional

| Opción | Qué aporta | Costo / riesgo | Recomendación |
|---|---|---|---|
| **A. Solo offline (por defecto)** | Ablación de la etapa determinística + análisis de subconjuntos; evidencia nueva sobre las dos amenazas sin costo | Ninguno; no propaga el vocabulario al híbrido extremo a extremo | **Recomendada** |
| **B. Corrida paga acotada** | Mediría el híbrido completo bajo `V_lit` para los casos que pasan a escalar (a lo sumo los que dejan de cortocircuitar) | Llamadas a Gemini sobre un subconjunto de los `206`; un caché nuevo; riesgo de un resultado que no mejore | Solo con autorización escrita del dueño; rotulada como corrida separada |

La corrida, si se autoriza, usa el runner con `--confirm-paid` y un caché nuevo; no escribe sobre
los artefactos congelados. **Es la única decisión de dueño que bloquea una tarea (5.5).**

### D7 — Gobernanza y cierre

Análisis + memo + prosa de resultados/discusión: **MEDIUM**. No hay edición de documentos legales ni
de configuración de producción. Cierre: `pytest` del script nuevo, compilación Docker
`texlive-thesis`, `verify_citations.py`, `pdfinfo`, `sent_c197.py` y registro en el libro mayor.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| La ablación se lee como «accuracy corregida» | Rotular como sensibilidad; informar cobertura y precisión por separado; declarar la independencia como procedimental |
| `V_lit` es tan pobre que la comparación pierde valor | Informar el control `V0` de c-142 como segundo punto; declarar el límite de la comparación (conjuntos de casos distintos) |
| El conjunto literal de tres vías es vacío y confunde | Declararlo explícitamente como hallazgo; definir el alto acuerdo como consenso `E3` = `E4` |
| La corrida paga se ejecuta sin autorización | Tarea bloqueada; por defecto se aplica la rama offline |
| Crecimiento de páginas | Tope neto `≤ 2`; registro en el libro mayor |

## Migration Plan

1. Fijar el método y el vocabulario corpus-blind antes de correr (prerregistro).
2. Escribir las pruebas del script (TDD) e implementar; verificar anclajes y determinismo.
3. Correr la ablación y el análisis de subconjuntos; registrar SHA-256.
4. Agregar la sección 3.29 al memo canónico.
5. Escribir el método en `04`, la subsección en `07` y la lectura en `08`.
6. Compilar, verificar citas y páginas; actualizar el libro mayor y la trazabilidad.

**Rollback**: `git revert` del script, del vocabulario, de los artefactos nuevos y de la sección del
memo. No hay migración de datos ni cambio de configuración.

## Open Questions

- **OQ1 (dueño, bloquea 5.5)**: ¿se autoriza la corrida paga acotada para propagar el vocabulario
  corpus-blind al híbrido completo? Por defecto **no**; sin autorización se aplica la rama offline y
  se declara la frontera. La decisión solo cambia si la tarea 5.5 se ejecuta o se cierra como
  offline; no cambia las specs ni los anclajes.
