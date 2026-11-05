## Context

Ver `proposal.md` — Why. La campana se documenta en cuatro piezas con roles distintos:

- `evaluation/data/campana/README.md`: **fuente de verdad** del criterio de doble cobertura (un caso de cada diez por `posicion` por mitad; 20 compartidos; O1=110 y O2=110) y del registro de SHA-256. NO se modifica.
- `docs/campana-medicion/guia-ejecucion-campana.md`: punto de entrada unico y orden de los pasos.
- `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`: procedimiento del brazo manual y de la intervencion.
- `docs/campana-medicion/runbook-doble-etiquetado.md`: procedimiento del doble etiquetado y registro de sujetos.
- `docs/campana-medicion/runbook-campana-contrabalanceada.md`: ya documenta el brazo automatizado (lineas 138-188) y sirve de fuente para el contenido que la guia omite.

Restricciones: cambio docs-only (gobernanza LOW), sin tocar codigo bajo `App/`, `n8n/`, `evaluation/`; sin ejecutar la campana; cadenas canonicas exactas sin tildes.

## Goals / Non-Goals

**Goals:**

- Que la guia describa el mismo criterio de casos que el README: 110/110 y 20 casos compartidos, sin "opcional".
- Que la guia describa el brazo automatizado completo (3 harnesses por 4 sub-planes) y su posicion en el orden del procedimiento.
- Que los prerequisitos (migracion `024 (head)`, app/N8N en pie) y los artefactos de entrada (sidecars) sean explicitos.
- Que los runbooks dejen de contradecir el registro real de sujetos (`A1` + `T1`, sin `A2`).

**Non-Goals:**

- No se modifica `evaluation/data/campana/README.md` ni sus SHA-256.
- No se modifica el comportamiento ni el codigo de los harnesses, del plan o del validador.
- No se corrige el texto "opcional" de ECM-001 en `openspec/specs/` (queda como cambio de spec posterior).
- No se ejecuta la campana ni el brazo automatizado.

## Decisions

- **D1 — Fuente de verdad unica.** El README manda: los conteos y el criterio se transcriben desde alli. La guia y los runbooks se corrigen para coincidir, nunca al reves. Alternativa descartada: editar el README para que coincida con la guia, prohibido por el alcance.
- **D2 — El brazo automatizado se documenta en la guia, no se duplica.** La guia gana una seccion breve que remite a `runbook-campana-contrabalanceada.md` secciones 5 y 6 para el detalle. Alternativa descartada: copiar el runbook entero en la guia, que duplicaria la fuente y volveria a generar deriva.
- **D3 — Orden del procedimiento.** Se fija: migracion y arranque -> plan -> sub-planes (8) -> brazo automatizado (harnesses, sidecars) -> planillas manuales -> export de intervenciones -> ensamblado y analisis. El brazo automatizado queda entre la generacion de sub-planes y el export, porque el export consume los sidecars que produce. Alternativa descartada: dejar el export antes del brazo automatizado, que lo vuelve inejecutable por falta de sidecars.
- **D4 — Nombres de sub-plan.** Se conserva el patron `subplan_m<mitad>_<brazo>_t<turno>.csv` (2 mitades x 2 brazos x 2 turnos = 8), que coincide con el plan de c-166 y con los SHA-256 ya declarados para los cuatro sub-planes manuales.
- **D5 — Sujetos.** El registro real tiene 8 filas P1..P8 con `A1` (analista) y `T1`..`T3` (autores), sin `A2`. Los ejemplos sinteticos de los runbooks se corrigen a `A1` + `T1`; el archivo `registro_sujetos.csv` no se toca.
- **D6 — Cadenas de sector.** Se enumeran las cinco cadenas exactas sin tildes y se prohibe cualquier variante. No se redefine el vocabulario: se transcribe desde `evaluation.corpus.SECTORES_CANONICOS` / codebook.

## Risks / Trade-offs

- **[Riesgo] La guia y el runbook contrabalanceado se desincronizan al editar solo uno.** -> La seccion nueva de la guia remite al runbook y repite solo flags y nombres de artefactos; cualquier cambio de flags se hace en el runbook y se referencia.
- **[Riesgo] El "opcional" de ECM-001 sigue vigente en el spec.** -> Se registra como residuo explicito en el proposal y se recomienda un cambio de spec posterior; este cambio no altera specs.
- **[Riesgo] Duplicar la lista de sectores en varios documentos.** -> Se enumeran solo donde faltaban (guia y runbook manual); se mantiene el texto identico y se verifica con `grep`.
- **[Trade-off] Se agrega detalle operativo a la guia.** -> Aumenta su longitud, pero evita que el lector tenga que saltar a tres runbooks para un prerequisito o el orden de los pasos.
