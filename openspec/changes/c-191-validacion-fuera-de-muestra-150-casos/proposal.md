# Proposal: Validación fuera de muestra sobre 150 casos con el clasificador congelado

## Why

El dictamen CONEAU del 2026-11-09 sobre la release `v1.2.12`
(`auditorias/Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`, criterio 4, metodología)
deja como ÚNICO dock explícito de rúbrica pendiente la "validación fuera de muestra no
realizada". La tesis lo declara hoy en `08-discusion.tex` (`subsec:interpretacion-resultados`
y `subsec:limitaciones-estudio`) y en `10-recomendaciones.tex` (`subsec:corpus-independiente`):
la validación "queda como no realizada en ambas campañas" y la campaña complementaria
"tampoco obtuvo un corpus independiente". Cerrar el dock exige medir el clasificador
CONGELADO sobre casos que no vio, con la misma pseudonimización y el mismo protocolo de doble
etiquetado, y actualizar el documento con el resultado, su intervalo y sus límites. El mismo
dictamen deja un residual de atribución bibliográfica (Galup 2009) que este change cierra.

## What Changes

- **Campaña de validación fuera de muestra, SOLO de clasificación congelada.** No mide el
  brazo manual; no participan operadores `O1`/`O2` (la exactitud 125/151 ya está resuelta por
  el dictamen A4). 150 casos nuevos `I001..I150`, sin solape con los 200 de ajuste,
  pseudonimizados con `scripts/corpus_ingest/pseudonymize_corpus.py`.
- **Doble etiquetado con dos etiquetadores NUEVOS `E3` y `E4`** (distintos entre sí y de los
  analistas `A1`, los autores `T1`-`T3` y los operadores `O1`/`O2`); se actualiza
  `evaluation/data/campana/registro_sujetos.csv` con `rol = etiquetador` y códigos `P<n>`. La
  correspondencia alias-identidad queda FUERA del repositorio (custodia del director).
- **Referencia = consenso de `E3` y `E4`** sobre `sector_etiquetado`
  (`consenso_doble_etiquetado`); conjunto de verdad laxo = sector consensuado más la
  INTERSECCIÓN de los adicionales que ambos marcaron. Los discordantes se EXCLUYEN y se
  informan con la advertencia de sesgo hacia casos fáciles.
- **Clasificador CONGELADO** `classifier_version = hybrid-v3`, commit `bf5e099`; sin
  recalibrar tau, prompt ni vocabulario después de ver el corpus. Se REUTILIZAN
  `evaluar_fuera_de_muestra` y el guard `--confirm-paid`; no se agrega código salvo lo
  estrictamente necesario.
- **Muestreo estratificado por canal y sector**, con sobremuestreo de la clase minoritaria
  (`Bases de Datos`, n=1 en el corpus de 200) y ponderación de las estimaciones globales,
  como recomienda la tesis 10.2. Los estratos exactos los fijan los autores ANTES de empezar
  (design D2).
- **Artefactos versionados con SHA-256** en `evaluation/data/campana/`: corpus independiente
  JSON, predicciones, tabla de doble etiquetado independiente, registro de sujetos, salidas
  de análisis y README.
- **Tesis**: la validación pasa de "no realizada" a "realizada" con el resultado y su IC de
  Wilson; se declaran el n efectivo y el sesgo de exclusión; se actualizan la recomendación de
  corpus independiente, `docs/Tesis/Correcciones/{numeros-canonicos,dictamen-correcciones}.md`
  y el Anexo I; resumen y abstract solo si el resultado lo amerita.
- **Residual Galup**: en 2.1 la definición de ITSM pasa a ser general con
  `\parencite{Galup2009_itsm}` (sin atribuirle una afirmación específica) y en 1.2 se retira
  "de Galup".
- **Release**: tag `v1.2.14` y archivo del change.

## Capabilities

### New Capabilities

- `evaluation-out-of-sample-validation`: protocolo y artefactos de la validación de
  clasificación del clasificador congelado sobre un corpus independiente de 150 casos
  (alcance, etiquetadores `E3`/`E4`, referencia por consenso, muestreo con sobremuestreo y
  ponderación, n efectivo y sesgo de exclusión, congelamiento y versionado).

### Modified Capabilities

- `tesis-document`: se agrega el estado "realizada" de la validación fuera de muestra con su
  resultado, n efectivo y sesgo de exclusión; la reformulación de la atribución a Galup
  (2009); y la trazabilidad del cierre en el registro y el Anexo I.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/{01-introduccion,02-marco-teorico,08-discusion,10-recomendaciones,12-anexos}.tex`;
  `docs/Tesis/v10 (IA)/paper/{main.pdf,compilacion.md}` recompilados.
- `docs/Tesis/Correcciones/{numeros-canonicos,dictamen-correcciones}.md`.
- `docs/campana-medicion/{runbook-corpus-independiente,runbook-doble-etiquetado}.md` (protocolo
  actualizado para la campaña independiente).
- `evaluation/data/campana/`: `corpus_independiente.json`, `doble_etiquetado_independiente.csv`,
  `registro_sujetos.csv`, `predicciones_independiente.json`, `reporte_independiente.md`,
  `analisis/` y `README.md` (SHA-256 y resultado del control de congelamiento).
- Lectura sin edición de `evaluation/campana.py`, `evaluation/no_solape.py`,
  `evaluation/run_evaluation.py` y `evaluation/data/plantilla_etiquetado.csv`.
- Gobernanza: MEDIUM/HIGH (sujetos humanos, datos organizacionales pseudonimizados, cambia
  una limitación estructural declarada). El trabajo de campo lo hacen los autores FUERA del
  repositorio; el repositorio entrega instrumentos y registros.

## Risks

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Acuerdo `E3`/`E4` ~69 %, ~46 casos excluidos | Alta | Declarar n efectivo y sesgo de exclusión; IC de Wilson (semi-ancho ~8,4 pts) aceptado |
| No se consiguen etiquetadores nuevos | Media | Registrar `estado_cegado: limitacion_declarada`; no presentarlo como ciego |
| Deriva del clasificador respecto de `bf5e099` | Baja | Control `git diff bf5e099 HEAD`; registrar en README |
| Sobremuestreo desbalancea el global | Media | Ponderar por distribución del universo; informar sin ponderar y ponderado |
| Interpretar el resultado como confirmación fuerte | Media | Reportar con su IC, n efectivo y exclusión; no extrapolar |

## Rollback Plan

El change no modifica `App/`, `n8n/`, `analisis/` ni datos canónicos. Revertir las fuentes
`.tex`, los memos de `docs/Tesis/Correcciones/` y los artefactos nuevos de
`evaluation/data/campana/` al commit previo deja el repositorio en el estado de `v1.2.13`; el
tag `v1.2.14` se elimina si no se publicó. No hay migraciones ni datos productivos que revertir.

## Dependencies

- Campo (recolección de 150 casos, doble etiquetado, corrida paga) fuera del repositorio: lo
  ejecutan los autores. El repositorio entrega instrumentos y registros.
- `GEMINI_API_KEY` y las variables del backend para la corrida con `--confirm-paid`.
- Decisión de los autores sobre los estratos (design D2) antes de reunir el corpus.

## Success Criteria

- [ ] `verificar_no_solape` pasa entre el corpus independiente y el de 200; el corpus valida y
      se versiona con su SHA-256.
- [ ] El doble etiquetado de `E3`/`E4` valida con exit code `0` y el registro de sujetos no
      tiene solapes (o la limitación está declarada).
- [ ] El control de clasificador congelado está registrado; no hubo recalibración posterior.
- [ ] `evaluar_fuera_de_muestra` reporta el bloque out-of-sample con n efectivo, exclusión e IC.
- [ ] La tesis declara la validación como "realizada" con el resultado y sus límites, en todas
      las secciones afectadas; el residual Galup está cerrado.
- [ ] `openspec validate c-191-validacion-fuera-de-muestra-150-casos --strict` pasa.
