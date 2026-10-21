## Context

Ver `proposal.md — Why`. Estado actual del documento:

- `03-estado-del-arte.tex` tiene cuatro subsecciones. La subsección
  `subsec:trabajos-academicos` (líneas 24-34) describe seis trabajos de
  clasificación de tickets. Las líneas `03:28` (Paramesh) y `03:30` (Revina) son
  prosa sustantiva; la línea `03:32` agrupa cuatro trabajos de LLM en una sola
  oración sin corpus, métrica ni condición; la línea `03:34` agrupa benchmarks
  multilingües y trabajos en español con una afirmación genérica de dependencia del
  idioma.
- `tab:comparativa` (03:40-58) compara SOLUCIONES COMERCIALES (Zendesk, Freshdesk,
  Jira, ServiceNow, osTicket), no trabajos académicos; su fuente por fila fue
  cableada por c-96 (A-26). No debe duplicarse.
- El PDF mide exactamente 100 páginas (tope duro confirmado por el autor; c-116 lo
  llevó allí). No hay margen de crecimiento.
- La regla de vacancia acotada de c-110 exige formular la ausencia relativa al
  alcance revisado; en tablas se traduce en marcar "no reportado en el alcance
  revisado".
- Los requisitos de las líneas `03:28`-`03:34` incluyen la corrección de atribución
  de Revina et al. (2020) (sin BERT, sin 91 %, con la conclusión real sobre métodos
  simples y explicables). Esa prosa NO puede revertirse.

## Goals / Non-Goals

**Goals:**

- Exponer corpus, métrica y condición de cada trabajo agrupado en una tabla
  comparativa, cerrando el segundo déficit de la dimensión 4 del dictamen.
- Garantizar procedencia por celda y marcar los datos no establecidos sin fabricar.
- Sostener el tope de 100 páginas (neutralidad de páginas).

**Non-Goals:**

- No re-modernizar la literatura ni agregar obras fuera de las ya citadas en la
  subsección.
- No reescribir la tabla comercial `tab:comparativa` ni su fuente (c-96).
- No editar el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.
- No crear el tag (eso es c-111).

## Decisions

### D1 — Capacidad delta: `tesis-document` (MODIFIED), sin capacidad nueva

La tabla es un contrato de calidad del documento de tesis, ya regido por
`tesis-document`. Se agregan cuatro requisitos ADDED. Alternativa descartada: crear
`tesis-estado-del-arte-comparativa` como capacidad nueva, que fragmentaría el
contrato del documento y duplicaría la organización existente.

### D2 — Obras incluidas y ubicación

La tabla `tab:trabajos-academicos` se inserta dentro de la subsección
`subsec:trabajos-academicos`, tras la prosa de `03:30`, y sustituye la oración
agrupada de `03:32`. Incluye los seis trabajos de clasificación de tickets citados
en la subsección (dos clásicos y cuatro de LLM):

| # | Trabajo | Clave `.bib` |
|---|---------|--------------|
| 1 | Paramesh & Shreedhara (2019) | `Paramesh2019_it_service_desk` |
| 2 | Revina, Buza & Meister (2020) | `Revina2020_it_tickets` |
| 3 | Zangari et al. (2023) | `zangari2023ticket` |
| 4 | Paket et al. (2024) | `paket2024itservice` |
| 5 | Liu et al. (2025) — TickIt | `liu2025tickit` |
| 6 | Colavito, Lanubile & Novielli (2025) | `colavito2025benchmarking` |

Se incluyen los dos clásicos para dar una vista única de comparabilidad de la
subsección (la prosa que los describe se condensa, ver D7). La oración de `03:34`
(benchmarks multilingües y trabajos en español) NO se tabula: ver D6.

### D3 — Columnas

`trabajo | enfoque | corpus/idioma | métrica reportada | condición`, con booktabs
(`\toprule`/`\midrule`/`\bottomrule`), `\small` y columnas `p{}` acotadas. Caption
breve y línea de fuente APA 7 ("Fuente: elaboración propia sobre las obras citadas
y sus resúmenes/DOI").

### D4 — Procedencia por celda

Todos los valores provienen de la prosa de la tesis o del resumen de la obra vía
`api.semanticscholar.org`/DOI (verificado en propose el 2026-10-21). Celdas sin
dato establecido -> "no reportado en el alcance revisado".

| Trabajo | enfoque | corpus/idioma | métrica reportada | condición | Procedencia |
|---|---|---|---|---|---|
| Paramesh 2019 | SVM + TF-IDF | ~10.000 tickets, inglés | exactitud ~87 % | clasificación clásica supervisada | prosa `03:28` |
| Revina 2020 | complejidad baja/media/alta; TF-IDF vs rasgos lingüísticos; kNN, DT, NB, LR, SVM, semi-supervisado | no reportado en el alcance revisado | no reportado en el alcance revisado (cualitativo: rasgos lingüísticos > TF-IDF) | comparación de representaciones y selección de rasgos | prosa `03:30` + resumen IEEE Access |
| Zangari 2023 | revisión + BERT; inyección de jerarquía de etiquetas | 20.000 reclamos + 35.000 issues (idioma no declarado en el resumen) | mejor embedding: >28 % en F1 sobre el estándar | clasificación multinivel, dos datasets | resumen ESWA 2023 (DOI `10.1016/j.eswa.2023.119984`) |
| Paket 2024 | LLM (Titan, Llama, Mistral) vs BERT; zero-shot, fine-tuning, RAG | turco, 172 clases | no reportado en el alcance revisado (cualitativo: BERT supera a los LLM) | clasificación multiclase 172 clases | resumen UBMK 2024 (DOI `10.1109/ubmk63289.2024.10773473`) |
| Liu 2025 (TickIt) | escalada de tickets con LLM; fine-tuning supervisado guiado por categoría | tickets de nube (ByteDance Volcano Engine); tamaño/idioma no reportado en el resumen | no reportado en el alcance revisado (cualitativo: eficacia en despliegue) | escalada online, dinámica y por relaciones | resumen FSE 2025 / arXiv:2504.08475 (DOI `10.1145/3696630.3728558`) |
| Colavito 2025 | benchmark de 22 LLM generativos + 2 BERT baseline | dos datasets de issues de GitHub (tamaño no reportado en el resumen) | no reportado en el alcance revisado (comparación de desempeño/tiempo/recursos) | zero-shot vs fine-tuning | resumen IST 2025 (DOI `10.1016/j.infsof.2025.107758`) |

Los espacios "no reportado" pueden refinarse en apply si se accede al texto
completo por DOI; en su defecto permanecen acotados.

### D5 — Regla de dato no reportado (c-110)

Se reutiliza la formulación de vacancia acotada de c-110: la ausencia se declara
relativa al alcance revisado ("no reportado en el alcance revisado"), nunca como
inexistencia absoluta, y nunca se completa con un valor estimado o inferido sin
fuente. Complementa la honestidad de datos: cada número en la tabla es rastreable.

### D6 — Alcance de `03:34` (ambigüedad resuelta)

La oración de `03:34` agrupa benchmarks multilingües y trabajos en español, que
pertenecen a OTRA familia de trabajos (evaluación de LLM por idioma), no a
clasificación de tickets. Se resuelve mantenerlos como prosa —condensando la
afirmación genérica en dos formulaciones acotadas (benchmarks multilingües;
trabajos en español)— sin una segunda tabla, porque (a) el pedido es una tabla
singular y (b) una segunda tabla comprometería la neutralidad de páginas (D7). Si
el autor prefiere tabular también esa línea, es una extensión posterior.

### D7 — Neutralidad de páginas (estrategia y gate)

El PDF está en 100 páginas. Una tabla de 6 filas y 5 columnas puede ocupar ~10-14
líneas compaginadas; para compensarlas, la tabla SUSTITUYE la oración de `03:32`
(4-5 líneas) y se condensan redundancias de la subsección sin tocar afirmaciones
sustantivas: la prosa de `03:28`/`03:30` deja de repetir el par corpus/métrica que
la tabla ya expone, se preserva la corrección de atribución de Revina, y se recorta
la frase de cierre redundante de `03:32`. Si el ahorro no alcanza, se comprime el
caption y el ancho de columnas antes de tocar cualquier otro pasaje. Regla
invariante: no se altera contenido científico, ni la tabla comercial, ni los
números canónicos, ni las correcciones c-102..c-116. Gate de verificación:
compilar con `texlive-thesis` y exigir `pdfinfo main.pdf | grep Pages <= 100` y
`0` referencias indefinidas.

### D8 — Governance y secuencia

Governance: MEDIO (edición de contenido de tesis con verificación por compilación y
tope de páginas). Reversibilidad: alta (`git revert` del commit del change restaura
la versión de 100 páginas sin tabla). Secuencia: el change se aplica ANTES de
`c-111` (versionado y tag), de modo que el tag capture la tabla ya presente.

### D9 — No duplicación de la tabla comercial

`tab:comparativa` (c-96) compara soluciones comerciales y su fuente por fila ya está
cableada. La tabla nueva es exclusivamente académica; el diseño la rotula distinto
(`tab:trabajos-academicos`) y no comparte filas ni fuente con la comercial.

## Risks / Trade-offs

- [La tabla excede el tope de páginas] -> aplicar D7: compensar con la oración
  sustituida y la condensación de la subsección; medir tras cada edición.
- [Un dato no establecido se completa de memoria] -> aplicar D5: toda celda sin
  fuente se marca "no reportado en el alcance revisado".
- [Se revierte la corrección de atribución de Revina] -> preservar explícitamente
  la prosa corregida de `03:30` al condensar (D7).
- [Colisión con otra edición de `03-estado-del-arte.tex`] -> re-verificar solape
  antes de aplicar; `c-110` ya está archivado y no reescribe el archivo.
- [Confusión con la tabla comercial] -> D9: rótulos y contenidos separados.

## Migration Plan

1. Medir baseline: `pdfinfo main.pdf | grep Pages` (esperado 100) y registrar.
2. Insertar `tab:trabajos-academicos` en la subsección y sustituir/condensar la
   oración de `03:32`; condensar la prosa de `03:28`/`03:30` sin perder la
   corrección de Revina.
3. Ajustar la línea de fuente APA 7 y las columnas `p{}`.
4. Recompilar con `texlive-thesis` y verificar D7 (<= 100 páginas, 0 referencias
   indefinidas) y ausencia de valores fabricados (D5).
5. Rollback: `git revert` del commit del change (restaura las 100 páginas sin tabla).

## Open Questions

- ¿Se desea una segunda tabla para la línea de evaluación de LLM por idioma
  (`03:34`)? El diseño la excluye por neutralidad de páginas (D6); se puede
  reincorporar como change posterior si el autor lo pide.
