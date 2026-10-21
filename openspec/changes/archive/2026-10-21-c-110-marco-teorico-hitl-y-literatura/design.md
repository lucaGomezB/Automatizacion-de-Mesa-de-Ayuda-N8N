## Context

Ver `proposal.md` — Why. Este change cubre los ítems 11 y 12 del dictamen CONEAU
2026-10-20 (recomendaciones 11 y 12) sobre `03-estado-del-arte.tex` y
`02-marco-teorico.tex`. Estado actual: el estado del arte tiene cuatro
subsecciones y no declara protocolo de revisión; la vacancia sobre Gemini en
español aparece en `03:32` y su síntesis en `03:58`. El marco teórico tiene siete
ejes y no define HITL (solo se lo menciona tardíamente en el capítulo legal). El
`.bib` tiene 48 entradas y ninguna entrada de HITL. Existe el helper
`docs/Tesis/v9 (IA)/verify_citations.py`.

## Goals / Non-Goals

**Goals:**

- Declarar un protocolo de revisión de literatura verificable en `03`.
- Acotar la afirmación de vacancia a lo efectivamente buscado.
- Agregar una subsección teórica de HITL con fuentes en `02`.
- Incorporar entradas bibliográficas nuevas de forma aditiva y verificada.

**Non-Goals:**

- No reescribir la tabla comparativa de trabajos académicos (ítem A-26, fuera de
  alcance; ya cubierto por changes previos).
- No re-ejecutar la revisión sistemática completa ni reemplazar la literatura
  arbitrada 2023-2026 ya incorporada por c-78.
- No editar el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.

## Decisions

### D1 — Capacidad delta: `tesis-document` (MODIFIED), sin capacidad nueva

Se modifica la capacidad existente `tesis-document` con tres requisitos ADDED
(protocolo, vacancia acotada, subsección HITL). No se crea una capacidad nueva:
los tres requisitos son contratos de calidad del documento de tesis, ya regidos
por `tesis-document`. Alternativa descartada: crear `tesis-marco-teorico-*
como capacidad nueva, que duplicaría la organización existente y fragmentaría el
contrato del documento.

### D2 — Ubicación y contenido de la subsección HITL

La subsección se inserta en `02-marco-teorico.tex` después del eje de
"Automatización de procesos y orquestación" (`subsec:automatizacion-orquestacion`)
y antes del eje de NLP/LLM, porque define el rol humano en el lazo de automatización
y prepara la discusión del gate de confianza. El párrafo introductorio del capítulo
pasa de "siete ejes" a "ocho ejes". La subsección define HITL y distingue grados de
autonomía (revisión total, revisión selectiva por umbral de confianza, operación
autónoma con auditoría), y aterriza el concepto en el gate
`requiere_revision_humana = (confianza < 0,70)` del sistema propuesto.

### D3 — Protocolo de revisión: instrumento y registro

Se declara en `03` un párrafo de metodología con bases (Scopus, IEEE Xplore, ACM
Digital Library, ACL Anthology, Google Scholar y arXiv), cadenas de búsqueda,
criterios de inclusión/exclusión (arbitrado, 2023-2026 para el estado del arte
moderno, idioma español o multilingüe) y fecha de corte. El protocolo se duplica
en una bitácora de búsqueda versionada en `docs/Tesis/Correcciones/` (una entrada
por consulta: base, cadena, fecha, resultado). El texto y la bitácora MUST ser
consistentes entre sí.

### D4 — Acotamiento de la vacancia

Formulación objetivo: "en las fuentes consultadas hasta la fecha de corte
(DD-MM-AAAA), con las cadenas declaradas en el protocolo, no se identificó artículo
arbitrado 2023-2026 que evalúe Google Gemini sobre tickets de soporte en español".
Se elimina toda formulación de inexistencia absoluta. La mención `03:58` se alinea
con el alcance declarado.

### D5 — Fuentes HITL candidatas (DOI verificado en propose; re-verificar en apply)

- Amershi et al. (2019), *Guidelines for Human-AI Interaction*, CHI 2019, DOI
  `10.1145/3290605.3300233`.
- Shneiderman (2020), *Human-Centered AI: Reliable, Safe & Trustworthy*, IJHCI,
  DOI `10.1080/10447318.2020.1741118`.
- Mosqueira-Rey et al. (2023), *Human-in-the-loop machine learning: a state of the
  art*, Artificial Intelligence Review, DOI `10.1007/s10462-022-10246-w`.
- Zanzotto (2019), *Viewpoint: Human-in-the-loop Artificial Intelligence*, JAIR,
  DOI `10.1613/jair.1.11345`.
- Wu, Terry & Cai (2022), *AI Chains: Transparent and Controllable Human-AI
  Interaction…*, CHI 2022, DOI `10.1145/3491102.3517582`.

Para el protocolo se evaluó PRISMA 2020 (DOI `10.1136/bmj.n71`, verificado) como
cita metodológica opcional. Cada entrada nueva lleva `author`, `title`, `year`,
campo de publicación y `doi`, con clave `ApellidoAnio_palabra_clave`. Ninguna se
agrega sin resolver por DOI o landing.

### D6 — Utilidad de `verify_citations.py`

Se evalúa como instrumento de integridad de citas: verifica citas huérfanas y
entradas sin usar cruzando `.tex` ↔ `.bib`, y sirve para confirmar `0` huérfanas y
`0` sin usar tras agregar entradas. NO verifica existencia de la fuente, NO valida
metadatos y NO implementa un protocolo de revisión (no consulta bases ni registra
búsquedas). Conclusión: usable como guardia de integridad al cierre, NO como
instrumento del protocolo; este requiere la bitácora de D3 y la verificación por
DOI de D5.

### D7 — Orden respecto de c-104 y de los otros changes de contenido

`c-104-bibliografia-y-atribucion` y este change tocan `Bibliography_base.bib`.
c-110 solo AGREGA entradas nuevas y MUST NOT editar las entradas existentes; se
aplica DESPUÉS de c-104. Respecto de `c-107` (00/01/04/07/08/09/10) no hay solape
de archivos; respecto de los demás changes de contenido (c-105/c-106/c-108/c-109)
se declara independencia por archivo y se re-verifica el solape antes de aplicar.

### D8 — Presupuesto de páginas

El PDF tiene 103 páginas. La subsección HITL y el párrafo de protocolo agregan
longitud; se redacta de forma compacta y se registra el conteo de páginas antes y
después. Si se excede un umbral aceptable, se recorta redundancia en los propios
párrafos agregados, sin alterar contenido ajeno al change.

## Risks / Trade-offs

- **Colisión del `.bib` con c-104.** Mitigación: D7 (aditivo, orden explícito).
- **Protocolo no reproducible.** Mitigación: bitácora versionada y consistencia
  texto–bitácora (D3).
- **Fuente HITL no verificable.** Mitigación: re-verificación por DOI en apply;
  retirar cualquier entrada que no resuelva (D5).
- **Crecimiento de páginas.** Mitigación: D8.

## Open Questions

Ninguna pendiente: D1–D8 cierran las decisiones de ubicación, alcance, fuentes y
orden. La fecha de corte exacta del protocolo se fija en apply y se registra en la
bitácora.
