## Context

Ver `proposal.md` — Why. Estado de partida (c-191, ver `evaluation/data/campana/README.md`):

- `corpus_independiente.json` tiene **`103`** casos (solo los del consenso `E3`/`E4`); los
  **`47`** discordantes quedaron fuera ANTES de clasificar, por lo que NO tienen predicción.
- `predicciones_independiente.json` tiene **`103`** predicciones del clasificador congelado
  `hybrid-v3` (commit `561b3c4`).
- `doble_etiquetado_independiente.csv` tiene **`150`** casos (tabla primaria del doble
  etiquetado `E3`/`E4`).
- `evaluation/doble_etiquetado.py` exige **exactamente dos** etiquetadores para la tarea
  `doble_etiquetado` (`re.compile(r"E\d+")`): un tercer etiquetador NO valida con ese
  contrato.
- `evaluation/no_solape.py::verificar_no_solape`, `evaluation/run_evaluation.py` (con
  `--corpus`, `--predicciones`, `--reporte`, `--confirm-paid`) y `evaluation/metrics.py`
  son reutilizables sin edición.

## Goals / Non-Goals

**Goals:**

- Arbitrar los `47` discordantes con un tercer etiquetador `E5`/`P11` (blind, codebook
  congelado) y subir el n efectivo a `150`, removiendo el sesgo de exclusión.
- Reforzar `Sistemas` y `Bases de Datos` para que sus métricas por clase sean estimables.
- Entregar protocolo, instrumentos, validador y artefactos versionados.
- Clasificar el corpus arbitrado con el clasificador congelado (corrida paga).

**Non-Goals:**

- Cambiar el clasificador, el corpus de ajuste, el umbral o el prompt.
- Incorporar el resultado a la tesis: se difiere a un change posterior (el campo lo hacen
  los autores; el resultado puede no estar a tiempo).
- Resolver la discordancia por consenso a posteriori de `E3`/`E4`.

## Decisions

### D1 — Arbitraje por un módulo nuevo, sin tocar el contrato de dos etiquetadores

Se agrega un módulo nuevo (`evaluation/arbitraje.py`) con el validador de la planilla de
arbitraje (acepta exactamente `E3`, `E4` y `E5`) y el constructor de la referencia
arbitrada. `evaluation/doble_etiquetado.py` NO se modifica: su contrato de dos etiquetadores
para la tarea `doble_etiquetado` queda intacto. Alternativa descartada: agregar `E5` como
tercer etiquetador a la tarea `doble_etiquetado`; rompería la validación del doble
etiquetado y el kappa de `E1`/`E2` de la campaña.

### D2 — Regla de arbitraje y conjunto laxo

Para un caso donde `E3` y `E4` difieren, la referencia es la etiqueta de `E5` (tercero
independiente, no consenso). Si las tres etiquetas son distintas, la referencia es la de
`E5` y el caso se marca con una bandera de discordancia residual declarada. El conjunto de
verdad laxo de un caso arbitrado es la etiqueta de `E5` más la INTERSECCIÓN de los
adicionales que marquen al menos dos de los tres etiquetadores. La regla se fija en el
runbook ANTES de ver `E5`.

### D3 — Refuerzo de clases chicas

Se agregan casos nuevos para `Sistemas` y `Bases de Datos`, etiquetados con el mismo
procedimiento (doble etiquetado `E3`/`E4`; arbitraje `E5` cuando `E3`/`E4` difieran), de
modo que el soporte por clase permita métricas estimables (`MIN_SOPORTE_ESTIMABLE = 2` en
`evaluation/metrics.py`, holgadamente superado). Los casos de refuerzo llevan ids nuevos con
prefijo `I` y pasan `verificar_no_solape`.

### D4 — Construcción de la referencia y n efectivo

La referencia arbitrada cubre los `150` casos originales más los de refuerzo; el n efectivo
del corpus arbitrado es `150` (o el total tras el refuerzo), sin exclusión por discordancia.
La estimación de c-191 sobre `103` se conserva rotulada como estimación con exclusión.

### D5 — Clasificador congelado y corrida paga

Se reutiliza `evaluation/run_evaluation.py --corpus <arbitrado> --predicciones <arbitrado>
--reporte <arbitrado> --confirm-paid`. Control `git diff bf5e099 HEAD` sobre
`App/Backend/app/classifiers`, `docs/prompt_gemini.txt`, `App/Backend/app/constants.py` y
`App/Backend/app/config/settings.py`. Prohibido recalibrar tras ver el corpus.

### D6 — Aceptación

`verificar_no_solape` (paso previo obligatorio, repetido por el runner), validador de la
planilla de arbitraje con exit code `0`, y control de clasificador congelado registrado en el
README. Si falta alguno, no se clasifica ni se versiona.

### D7 — Artefactos y SHA-256

En `evaluation/data/campana/`: tabla primaria del arbitraje, `corpus_independiente_arbitrado.json`,
`predicciones_arbitrado.json`, `reporte_arbitrado.md`, `registro_sujetos.csv` (con `E5,P11`)
y `README.md` con SHA-256 y el commit. Los artefactos de la v9 y el corpus de ajuste quedan
intactos.

### D8 — Incorporación a la tesis diferida

El resultado arbitrado se versiona, pero su incorporación a la prosa de la tesis se difiere a
un change posterior (análogo a c-169), porque depende de que el campo concluya. Se declara
como dependencia, no como residual oculto.

## Risks / Trade-offs

- [No se consigue `E5` independiente] → `estado_cegado: limitacion_declarada`; no se presenta como ciego.
- [Discordancias residuales de tres vías] → regla declarada y bandera por caso; se informa el conteo.
- [El refuerzo desbalancea el global] → se informa con y sin ponderación (c-191 D2).
- [Deriva del clasificador] → control `git diff` antes de clasificar; si cambió, se detiene.
- [Solape con el corpus de ajuste] → `verificar_no_solape` como paso previo obligatorio.
- [Gitleaks marca prosa con nombres de archivo] → referencias "sección N (`archivo.tex`)".

## Migration Plan

Apply en el orden de `tasks.md`: protocolo e instrumentos, validador/constructor (TDD),
registro de sujetos, campo (autores, fuera del repo), no solape + corrida + control,
artefactos y validación. Rollback: revertir los artefactos nuevos, la fila `E5`, el runbook y
el módulo nuevo al commit previo; el tag se elimina si no se publicó.

## Open Questions

- **Volumen del refuerzo**: cuántos casos nuevos por clase chica. Se decide con los autores
  al iniciar el campo; no cambia las specs (el objetivo es "estimable", no un n fijo).
- **Regla del caso de tres etiquetas distintas**: `E5` como árbitro con bandera es la
  propuesta; si los autores prefieren un cuarto juicio, se ajusta el runbook antes de ver
  las etiquetas.
