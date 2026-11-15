# Proposal: Referencia por mayoría con etiquetadores independientes

## Why

El último dictamen CONEAU descuenta en el **criterio 4 (Metodología, peso 20, nota 8)** que la
referencia fuera de muestra tiene **un solo árbitro**: `E3` y `E4` etiquetaron los `206` casos,
pero cuando difirieron un único tercero `E5` fijó la referencia en `64 de 206` (`31 %`) con una
regla **no mayoritaria** (`E5` decide). La fiabilidad de la referencia es moderada (kappa de
Cohen `E3`/`E4` `0,6055`; `E1`/`E2` `0,5569` sobre la campaña de `200`) y hay `6` casos con tres
etiquetas distintas (`I033`, `I042`, `I056`, `I130`, `I194`, `I198`). Una referencia que depende de
una sola persona no permite estimar la mayoría ni el acuerdo entre varios evaluadores.

El autor puede convocar **`3` etiquetadores nuevos independientes** (no operadores, no autores).
Con `E3` y `E4` eso da **`5` etiquetadores sobre los `206`**, lo que habilita una referencia por
**MAYORÍA (3 de 5)**, un **acuerdo multi-evaluador (kappa de Fleiss)** y el reemplazo del árbitro
único. Es una corrección que exige trabajo de campo, datos nuevos y **consentimiento**: gobernanza
HIGH.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Sujetos y consentimiento** | Convocatoria y registro de `E6`, `E7`, `E8` (`P12`, `P13`, `P14`) en `evaluation/data/campana/registro_sujetos.csv`, distintos de operadores, autores y de `E1`-`E5`; consentimiento informado registrado con la plantilla vigente. | **HIGH** |
| **B. Etiquetado ciego** | Los tres etiquetadores nuevos etiquetan a ciegas con la hoja ciega, la plantilla vacía y el codebook congelado. Se recomienda el corpus completo de `206`; mínimo viable, los `64` divergentes. Artifacto nuevo `doble_etiquetado_mayoria.csv`. | **HIGH** |
| **C. Referencia por mayoría** | Regla declarada ANTES de ver las etiquetas: mayoría `>= 3` de `5`; los casos sin mayoría se marcan y resuelven con la regla vigente como respaldo rotulado. Sidecar nuevo con el origen de cada referencia y el conteo `sin_mayoria`. | MEDIUM |
| **D. Acuerdo multi-evaluador** | `kappa_fleiss` (Fleiss) y matriz de acuerdo por pares en `evaluation/kappa.py`, sin cambiar el contrato de dos etiquetadores de `kappa_doble_etiquetado`. | MEDIUM |
| **E. Recomputo y comparación honesta** | Script de solo lectura que recalcula la exactitud estricta y las métricas por clase bajo la referencia por mayoría y bajo la referencia vigente (árbitro único), ancladas a `142/206` (`0,6893`) y macro-F1 `0,7024`, y reporta AMBAS. La cifra primaria puede cambiar: se informa, no se oculta. | MEDIUM |
| **F. Memo, tesis y trazabilidad** | Sección aditiva del memo (primer número libre; hoy la última es `3.37`, esperado `3.39`), prosa en método/resultados/discusión/recomendaciones y entrada en `dictamen-correcciones.md`. | LOW/MEDIUM |

**No objetivos.**

- No se reclasifica el corpus de ajuste ni se recalibra el clasificador congelado; la re-clasificación
  se hace, si hace falta, con el clasificador congelado `hybrid-v3`.
- No se modifica el corpus de ajuste, `evaluation/report.md`, el prompt, el umbral ni el vocabulario.
- No se elige una etiqueta "verdadera" para los casos sin mayoría: se declara el conteo y el rango.
- No se recalibra el análisis de ruido de referencia (`evaluation-reference-noise-sensitivity`): su
  calibración usa el kappa `E3`/`E4` vigente y su actualización se difiere.
- No se reabren las limitaciones estructurales que exigen otro trabajo de campo.
- No se implementa nada ni se mide en este change: el campo lo ejecutan los autores fuera del repositorio.

## Capabilities

### New Capabilities

Ninguna. El change extiende capacidades existentes; no introduce un contrato nuevo.

### Modified Capabilities

- `discordant-arbitration`: la referencia de los casos discordantes deja de fijarla un único tercer
  etiquetador (`E5` decide) y pasa a fijarla la **mayoría de cinco etiquetadores independientes**
  (`E3`, `E4`, `E6`, `E7`, `E8`), con regla de desempate declarada antes de ver las etiquetas; se
  agregan el registro y el consentimiento de `E6`-`E8`, la cobertura de etiquetado ciego y los
  artefactos versionados de la referencia por mayoría.
- `evaluation-framework`: se AGREGA el kappa de Fleiss (multi-evaluador) y la matriz de acuerdo por
  pares, manteniendo el contrato de exactamente dos etiquetadores de `kappa_doble_etiquetado`.
- `evaluation-out-of-sample-validation`: se AGREGA el recomputo de la cifra primaria (exactitud
  estricta y métricas por clase) bajo la referencia por mayoría y su comparación honesta con la
  referencia vigente de árbitro único.
- `tesis-document`: se AGREGAN la divulgación de la referencia por mayoría en método, resultados y
  limitaciones, el registro de los etiquetadores independientes con su consentimiento y la
  reformulación de la línea de trabajo futuro que este change ejecuta.
- `tesis-numeros-canonicos`: se AGREGA el registro aditivo de la referencia por mayoría, del kappa de
  Fleiss y de la comparación de ambas referencias, con procedencia, estado y comando por valor.

`evaluation-reference-noise-sensitivity` y `evaluation-corpus-bias-mitigation` no se modifican: su
calibración y sus anclajes usan la referencia vigente y su actualización se difiere (no objetivos).

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/registro_sujetos.csv` | Modificado | Filas `E6,P12`, `E7,P13`, `E8,P14` |
| `evaluation/data/campana/doble_etiquetado_mayoria.csv` | Nuevo | Planilla unida de los `5` etiquetadores |
| `evaluation/data/campana/referencia_mayoria.json` + sidecar | Nuevo | Referencia por mayoría, origen y `sin_mayoria` |
| `evaluation/kappa.py` | Modificado | `kappa_fleiss`, matriz por pares; Cohen intacto |
| `evaluation/mayoria.py` | Nuevo | Constructor de la referencia por mayoría |
| `evaluation/data/campana/analisis/analisis_referencia_mayoria_c230.*` | Nuevo | Script, prueba, JSON, MD y SHA-256 |
| `docs/campana-medicion/runbook-referencia-mayoria.md` | Nuevo | Protocolo de convocatoria, ciego y desempate |
| `docs/campana-medicion/confirmacion-posterior-consentimiento.md` | Modificado | Alias `E6`-`E8` |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Sección nueva (esperado `3.39`) |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | Diseño de la referencia |
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` | Modificado | Cifra bajo ambas referencias |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | Limitación de la referencia acotada |
| `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` | Modificado | Línea de trabajo futuro ejecutada |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad `C30/…` |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuración, el corpus de ajuste, las
predicciones congeladas ni `evaluation/report.md`.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| No se consiguen `3` etiquetadores independientes o falta el consentimiento | Media | Es dependencia explícita; con `+1` (`3` en total) solo se cubre el mínimo. Sin campo, el change queda bloqueado y se declara la limitación en el memo |
| El resultado cambia y se lee como corrección de la cifra primaria | Alta | Se reportan AMBAS referencias; el rótulo separa "referencia por mayoría" de la vigente; el veredicto del umbral se recalcula, no se oculta |
| Los casos sin mayoría sesgan la referencia | Media | Regla de mayoría y desempate declarada ANTES de ver las etiquetas; conteo y efecto informados; rango reportado |
| Derivación del clasificador al recalcular | Baja | Clasificador congelado `hybrid-v3`, `git diff bf5e099 HEAD` registrado |
| Colisión de numeración del memo con changes concurrentes | Media | Primer número libre al aplicar (tarea 0.4) |
| Crecimiento de páginas | Media | Tabla compacta o párrafo; verificación de `\@abspage@last` |

## Rollback Plan

`git revert` del commit del change: el módulo nuevo, el script y sus salidas son aditivos; las filas
`E6`-`E8` del registro, el artefacto y el sidecar nuevos se retiran; la sección del memo se elimina
sin tocar las anteriores; la prosa vuelve por archivo. El ciclo TDD se revierte con sus pruebas. No
hay migraciones ni datos productivos que revertir; el corpus vigente y los valores canónicos previos
quedan intactos.

## Dependencies

- **Trabajo de campo FUERA del repositorio**: convocatoria de `3` etiquetadores independientes y su
  consentimiento informado. Bloquea los bloques B a F.
- Disponibilidad del custodio de identidades (director) para la correspondencia alias-identidad.
- Reutiliza los artefactos de c-206 (protocolo ciego, codebook, `validar_registro_sujetos`,
  `doble_etiquetado_arbitrado.csv`, `arbitraje_tres_vias.json`, `corpus_independiente_arbitrado.json`,
  `predicciones_arbitrado.json`) y `evaluation/kappa.py`, `evaluation/metrics.py`.
- No depende de c-223, c-224, c-225 ni c-226.

## Success Criteria

- [ ] `E6`, `E7`, `E8` figuran en `registro_sujetos.csv` sin solape por `persona` y con su
  consentimiento registrado; el protocolo ciego se respeta (los etiquetadores no ven etiquetas,
  referencia ni predicciones).
- [ ] La referencia por mayoría cubre los casos etiquetados, declara el conteo `sin_mayoria` y no
  elige una etiqueta "verdadera" para los empates.
- [ ] `kappa_fleiss` reproduce un oráculo sintético conocido y el contrato de dos etiquetadores de
  `kappa_doble_etiquetado` no cambia.
- [ ] El script reproduce los anclajes `142/206` y macro-F1 `0,7024` antes de escribir y es
  determinista byte a byte.
- [ ] El memo registra la sección aditiva (primer número libre) sin alterar las anteriores; la tesis
  informa ambas referencias y reformula la línea de trabajo futuro ejecutada.
- [ ] `openspec validate c-230-referencia-por-mayoria-con-etiquetadores-independientes --strict` pasa.
