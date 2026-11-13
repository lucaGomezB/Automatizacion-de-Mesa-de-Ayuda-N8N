## Why

La validación fuera de muestra de c-191 quedó sobre un n efectivo de `103`: los `47` casos
discordantes entre `E3` y `E4` se EXCLUYERON de la referencia (design D6 de c-191), lo que
sesga la estimación hacia los casos fáciles y deja la exactitud estricta (`0,8447`) sin
cobertura sobre el universo de `150`. Además, dos clases quedaron con soporte chico
(`Sistemas`, `5`; `Bases de Datos`, `13` sobremuestreada), lo que limita las métricas por
clase. El tribunal reestimó la tesis en ~8,3/10. Levantar el sesgo de exclusión y hacer
estimables las clases chicas es la **palanca cara**: exige trabajo de campo de los autores
(un tercer etiquetador que arbitre, casos nuevos) y una corrida paga del clasificador
congelado, pero es lo que permite reportar el resultado sobre los `150` casos. Impacto
estimado: +0,5 a +1,0 en `Resultados` y +0,3 en `Marco metodológico`. Llegar a ≥9 depende
de este change MÁS el cierre de c-146/6.1.

## What Changes

- **Tercer etiquetador `E5` (código `P11`)** que ARBITRA los `47` casos discordantes; se
  registra en `evaluation/data/campana/registro_sujetos.csv` sin nombres. El arbitraje es
  explícitamente NO un consenso a posteriori de `E3`/`E4` (el protocolo lo prohíbe).
- **Regla de arbitraje para la discordancia de tres vías** con el codebook congelado; la
  referencia de los casos discordantes pasa a estar definida y el n efectivo pasa a `150`.
- **Refuerzo de las clases chicas**: casos nuevos para `Sistemas` y `Bases de Datos`, de
  modo que sus métricas por clase sean estimables.
- **Protocolo e instrumentos** (hoja ciega + plantilla `C1` + codebook) versionados en un
  runbook nuevo de `docs/campana-medicion/`.
- **Artefactos versionados** con SHA-256: tabla primaria del arbitraje, JSON final del
  corpus arbitrado, predicciones y reporte del clasificador congelado (corrida paga).
- **Aceptación**: el validador de la planilla de arbitraje sale con exit code `0`; pasa
  `verificar_no_solape`; el control de clasificador congelado queda registrado.
- **Incorporación a la tesis**: diferida a un change posterior, cuando el campo concluya.

## Capabilities

### New Capabilities

- `discordant-arbitration`: protocolo, instrumentos y artefactos del arbitraje de los casos discordantes por un tercer etiquetador `E5`/`P11` y del refuerzo de las clases chicas, con el n efectivo de `150`.

### Modified Capabilities

- `evaluation-out-of-sample-validation`: el n efectivo pasa de `103` a `150` al arbitrar los discordantes (se levanta el sesgo de exclusión) y las métricas por clase de `Sistemas` y `Bases de Datos` pasan a ser estimables.

## Impact

- Nuevo: `docs/campana-medicion/runbook-arbitraje-discordantes.md` (protocolo e instrumentos).
- Nuevo: un validador/constructor de la referencia arbitrada (módulo nuevo de `evaluation/`, sin tocar el contrato de dos etiquetadores de la tarea `doble_etiquetado`) y sus pruebas.
- `evaluation/data/campana/registro_sujetos.csv` (`E5,P11`), y artefactos nuevos en
  `evaluation/data/campana/`: tabla primaria del arbitraje, `corpus_independiente_arbitrado.json`,
  `predicciones_arbitrado.json`, `reporte_arbitrado.md` y el `README.md` con SHA-256.
- Lectura sin edición de `evaluation/run_evaluation.py`, `evaluation/no_solape.py`,
  `evaluation/metrics.py` y del clasificador congelado.
- Gobernanza: HIGH (protocolo de campo, PII/organizacional, cambia una limitación estructural declarada).
- Non-goals: sin cambio al clasificador, al corpus de ajuste ni a los artefactos de la v9.

## Risks

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| No se consigue `E5` o no es independiente | Media | Registrar `estado_cegado: limitacion_declarada`; no presentarlo como ciego |
| El arbitraje se opera como consenso post-hoc | Media | Regla de arbitraje declarada y separada; el protocolo lo prohíbe |
| Discordancias residuales de 3 vías | Media | Regla declarada para el caso de tres etiquetas distintas |
| Deriva del clasificador respecto de `bf5e099` | Baja | Control `git diff bf5e099 HEAD`; registrar en el README |
| Doble conteo o solape con el corpus de ajuste | Baja | `verificar_no_solape` como paso previo obligatorio |

## Rollback Plan

El change no modifica el clasificador ni el corpus de ajuste. Revertir los artefactos
nuevos de `evaluation/data/campana/`, la fila `E5` del registro, el runbook nuevo y el
módulo/validador nuevo al commit previo deja el repositorio en el estado de `v1.3.0`. El
tag de release se elimina si no se publicó. No hay migraciones ni datos productivos que
revertir.

## Dependencies

- Trabajo de campo de los autores FUERA del repositorio (arbitraje y casos de refuerzo).
- Disponibilidad de un tercer etiquetador independiente y del custodio de identidades.
- `GEMINI_API_KEY` y variables del backend para la corrida paga (`--confirm-paid`).
- Artefactos de c-191 (corpus independiente, tabla primaria del doble etiquetado).

## Success Criteria

- [ ] `E5`/`P11` figura en `registro_sujetos.csv` sin nombres ni solapes por `persona`.
- [ ] La planilla de arbitraje valida con exit code `0` y la regla de tres vías está declarada.
- [ ] `verificar_no_solape` pasa entre el corpus arbitrado y el de ajuste.
- [ ] La referencia arbitrada cubre los `150` casos; las clases `Sistemas` y `Bases de Datos` son estimables.
- [ ] El control de clasificador congelado está registrado; no hubo recalibración posterior.
- [ ] Los artefactos quedan versionados con su SHA-256 y los de la v9 sin cambios.
- [ ] `openspec validate c-206-arbitraje-de-los-discordantes-y-refuerzo-de-clases-chicas --strict` pasa.
