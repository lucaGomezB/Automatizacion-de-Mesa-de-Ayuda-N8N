# Proposal: c-78 — Bibliografia y atribucion

## Why

La auditoria de la tesis (Plan de correccion §16.3, items 22-24) detecto una
**misatribucion verificada** a Revina, Buza & Meister (2020) en los capitulos 3.3
y 8.2: la tesis le adjudica un aporte basado en BERT, una exactitud cercana al
91 % y la conclusion de que los modelos preentrenados transfieren conocimiento al
dominio de tickets sin ajuste fino. Nada de eso es cierto: el articulo se titula
"IT Ticket Classification: The Simpler, the Better", no usa BERT ni modelos
preentrenados y concluye lo contrario (los metodos simples y explicables con
rasgos linguisticos del dominio son competitivos). En paralelo, el estado del arte
carece de literatura arbitrada 2023-2026, hay afirmaciones cuantitativas sin cita
("88 % a 94 %") y errores de atribucion de fuentes (los rangos de interpretacion
de Kappa son de Landis & Koch, no de Cohen). Corregir la atribucion y modernizar
la bibliografia es un requisito de integridad academica de nivel de governance
HIGH y no solapa con c-76 ni c-77.

## What Changes

### Grupo Bibliografia y atribucion (B1-B3) — plan de auditoria items 22-24

| Id | Item del plan | Correccion |
|----|---------------|-----------|
| B1 | 22 | Reescribir la misatribucion de Revina et al. (2020) en `03-estado-del-arte.tex:28` (§3.3) y `08-discusion.tex:20,22` (§8.2) con la conclusion real del articulo, e incorporar la tension resultante en el capitulo 8. |
| B2 | 23 | Modernizar el estado del arte con al menos 12 articulos arbitrados 2023-2026 (clasificacion de tickets con LLM/transformers, evaluacion zero-shot/few-shot multilingue, desempeno de LLM en espanol / espanol de Iberoamerica). Resolver las dos afirmaciones sin cita (`08-discusion.tex:20` "88 % a 94 %"; `03-estado-del-arte.tex:30` literatura few-shot). |
| B3 | 24 | Higiene de citas y atribucion: agregar Landis & Koch (1977) y corregir la fuente de los rangos de Kappa; corregir metadatos de `Stallings2017_computer_security`, `OGC2011_itil` y `Jurafsky2023_speech_language`; documentar las dos citas huerfanas de v7 (Karchhud et al., 2024 y Mehdi et al., 2023), verificadas como FABRICADAS y ya ausentes en v9, con guardia de no reintroduccion y re-verificacion por DOI de todas las citas restantes; normalizar la coma antes del ano en "et al.". |

Detalle de cada item:

- **B1 — Revina**: el texto MUST dejar de atribuir BERT, ~91 % de exactitud y
  transferencia de modelos preentrenados. La reescritura SHALL presentar a Revina
  et al. como evidencia de que los metodos simples y explicables con rasgos
  linguisticos del dominio son competitivos en la clasificacion de tickets de TI,
  y que los embeddings preentrenados pueden rendir peor por vocabulario
  especifico del dominio. El capitulo 8 MUST integrar esta tension (evidencia
  contraria) en la discusion, sin ocultarla ni debilitar el aporte.
- **B2 — Modernizacion**: incorporar al menos 12 referencias reales y arbitradas
  (lista candidata verificada en `design.md`). Declarar de forma explicita la
  brecha: NO existe un articulo arbitrado 2023-2026 que evalue Google Gemini
  especificamente sobre tickets de soporte en espanol; esa ausencia forma parte
  de la contribucion. Las dos afirmaciones sin cita se resuelven citando
  evaluaciones concretas de las nuevas referencias o retirando/reformulando la
  afirmacion.
- **B3 — Higiene**:
  - Agregar **Landis, J. R., & Koch, G. G. (1977). The Measurement of Observer
    Agreement for Categorical Data. Biometrics, 33(1), 159-174. DOI
    10.2307/2529310**. Los rangos interpretativos de Kappa atribuidos a Cohen son
    de Landis & Koch. Corregir el rotulo: con \(\kappa = 0{,}87\) corresponde
    "casi perfecto" (el texto de §4.4 dice "sustancial"). Actualizar §4.4
    (`04-marco-metodologico.tex:47`) y §4.8 ("Amenazas a la validez", `:79`).
  - `Stallings2017_computer_security`: agregar co-autor **Lawrie Brown** (4ta ed.
    de "Computer Security: Principles and Practice" es de Stallings & Brown).
  - `OGC2011_itil`: verificar/corregir la autoria de ITIL Service Operation
    (2011); el campo `author` y la editorial deben reflejar la publicacion real
    (The Stationery Office / herencia AXELOS).
  - `Jurafsky2023_speech_language`: corregir la editorial; el borrador de la 3ra
    edicion NO es Pearson (la 2da edicion si lo era). Ajustar a
    Stanford University / borrador autopublicado.
  - Citas huerfanas: las dos citas huerfanas estaban en la version v7 (la
    version auditada) y eran **Karchhud, R., Singh, A., & Patel, M. (2024)**
    ("Few-shot ticket classification with large language models: A multilingual
    evaluation", JISEM 9(2), 145-168) y **Mehdi, S., Kapoor, A., & Larsson, J.
    (2023)** ("The state of AI in customer support: Industry adoption survey
    2020-2023", International Journal of Service Operations Management 45(3),
    211-234). Ambas fueron **verificadas como FABRICADAS** (no existen: Crossref
    y OpenAlex dan cero resultados para autores y titulos; el journal JISEM
    existe pero el articulo no; en el segundo caso el propio nombre del journal
    es un near-miss del real "International Journal of Services and Operations
    Management"). Ya fueron **retiradas entre v7 y v9**, por lo que v9 tiene cero
    citas huerfanas. El change MUST NOT reintroducirlas y MUST volver a citar,
    reformular o retirar las dos afirmaciones que sostenian (el rango "88 % a
    94 %" en `08-discusion.tex:20` y la afirmacion de adopcion de IA en
    `03-estado-del-arte.tex:12`), lo cual ya cubre B2. Ademas, como las
    fabricaciones suelen agruparse, MUST re-verificar todas las citas restantes
    contra resolucion por DOI (ver `design.md` §D-B3).
  - Normalizar la coma antes del ano en las citas "et al." segun APA
    ("Revina et al., 2020", no "Revina et al. 2020") donde la tesis se desvie.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: integridad de citas (invariante de cero huerfanas / cero
  entradas sin usar), atribucion correcta de Revina et al. (2020), estado del
  arte modernizado con literatura arbitrada 2023-2026, fuente de la
  interpretacion de Kappa, y higiene de metadatos bibliograficos. Se actualiza el
  requisito de renderizado de citas (el conteo de entradas "exactamente 33" deja
  de ser valido). `evaluation-framework` NO se modifica.

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex`
- `docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex`
- `docs/Tesis/v9 (IA)/paper/sections/08-discusion.tex`
- `docs/Tesis/v9 (IA)/Bibliography_base.bib`
- `main.pdf` (se recompila despues en Overleaf, no en este repo)
- `docs/Tesis/Correcciones/dictamen-correcciones.md` (nuevo grupo de registro)
- `openspec/specs/tesis-document/spec.md` (delta aplicado al archivar)

No se toca `App/**`. No se modifican artefactos de c-67, c-76 ni c-77. No se
edita `CHANGES.md`.

## Rollback Plan

`git checkout --` sobre los `.tex` y `Bibliography_base.bib` afectados, o
`git revert` del commit del change. Los artefactos OPSX se descartan con el
directorio del change.

## Success Criteria

- [ ] La tesis ya no atribuye BERT, ~91 % ni transferencia sin ajuste fino a
      Revina et al. (2020); §3.3 y §8.2 reflejan su conclusion real.
- [ ] El capitulo 8 discute explicitamente la tension (metodos simples/explicables
      competitivos; embeddings preentrenados pueden rendir peor por vocabulario de
      dominio).
- [ ] Se incorporan al menos 12 articulos arbitrados 2023-2026, verificables por
      DOI, cubriendo (a) clasificacion de tickets con LLM, (b) evaluacion
      zero-shot/few-shot multilingue, (c) LLM en espanol / Iberoamerica.
- [ ] La bibliografia NO contiene ninguna referencia fabricada (en particular
      Karchhud et al., 2024 ni Mehdi et al., 2023, ya retiradas en v9); todas las
      citas restantes quedan re-verificadas contra resolucion por DOI/landing
      page.
- [ ] "88 % a 94 %" (`08:20`) y la afirmacion few-shot (`03:30`) quedan citadas o
      reformuladas; no queda ninguna afirmacion cuantitativa sin respaldo.
- [ ] Existe entrada `Landis1977_kappa` con DOI 10.2307/2529310; §4.4 y §4.8 citan
      Landis & Koch para los rangos y rotulan \(\kappa = 0{,}87\) como "casi
      perfecto".
- [ ] `Stallings2017_computer_security`, `OGC2011_itil` y
      `Jurafsky2023_speech_language` tienen metadatos correctos.
- [ ] Cero citas huerfanas y cero entradas de bibliografia sin usar tras el cambio
      (verificado por `verify_citations.py` y por `main.bcf` contra el `.bib`).
- [ ] Las citas "et al." usan la coma antes del ano segun APA.
- [ ] La tesis NO supera las 100 paginas (actual ~74); la expansion de la
      bibliografia no la excede.
- [ ] `openspec validate c-78-tesis-bibliografia-atribucion --strict` pasa.
- [ ] `pdf` recompilado en Overleaf sin errores fatales (tarea posterior; no hay
      toolchain LaTeX local).
