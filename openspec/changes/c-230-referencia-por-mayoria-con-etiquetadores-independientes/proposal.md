# Proposal: Referencia por mayoria con etiquetadores independientes

## Adaptacion a la devolucion de tercera instancia (16/11/2026)

Este change se propuso el 15/11/2026, un dia antes de la devolucion de tercera instancia (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`), y se **reformula por completo** sin haberse aplicado (0 tareas).

- **Premisa que cayo (completa).** La version original recomputaba la referencia de los `206` casos fuera de muestra con la mayoria de `E3`, `E4` y tres etiquetadores nuevos (`E6`, `E7`, `E8`), para reemplazar al arbitro unico `E5` en los `64` casos arbitrados, y anclaba el recomputo en `142/206` (`0,6893`), macro-F1 `0,7024` y kappa `0,6055`. Todo ese corpus y sus derivados (`doble_etiquetado_arbitrado.csv`, `arbitraje_tres_vias.json`, `corpus_independiente_arbitrado.json`, `predicciones_arbitrado.json`, los 6 casos de tres vias, `confirmacion-posterior-consentimiento.md` como plantilla para los alias nuevos) quedan **retirados** del ejemplar por decision de los autores ante K-01. El motivo lo fija `c-235` (`proposal.md` y `design.md`, D1 y D3); este change no lo reformula. No hay nada que recomputar sobre esos casos.
- **Que se conserva.** La idea metodologica: una referencia que no dependa de una sola persona, construida por mayoria de varios etiquetadores independientes, con su acuerdo multievaluador (kappa de Fleiss). Tambien el numero reservado del memo (`3.39`) y la linea base que si sobrevive: el doble etiquetado `E1`/`E2` sobre los 200 casos (kappa `0,5569`; 62 casos discordantes, 29 de ellos entre `Sistemas` y `Soporte Tecnico Software`, recontados en esta adaptacion).
- **Que cambia.** El change pasa a ser: (1) funciones puras `evaluation/mayoria.py` y `kappa_fleiss` en `evaluation/kappa.py`, con TDD estricto y oraculos sinteticos y publicados; (2) el protocolo de referencia por mayoria que completa el **corpus probabilistico acreditado** de `c-229` (spec PS-009 de `evaluation-probabilistic-sampling`) (numero de etiquetadores, cegado, regla de mayoria y de `sin_mayoria` declaradas antes de etiquetar, sin arbitro unico de respaldo), sujeto a las compuertas de procedencia (K-01) y etica/legal (K-02). Se eliminan los deltas sobre `evaluation-out-of-sample-validation` (cuyo ID `OOS-026` ademas chocaba con el que agrega `c-235`) y sobre `discordant-arbitration` (sus MODIFIED ARB-001/002/004 y sus ADDED ARB-009..012 describian a `E3`/`E4`/`E5` sobre los 206 casos). La verificacion de "regla declarada antes" deja de apoyarse solo en `git log`, porque las fechas de commit las controlan los autores: se suma una constancia en custodia del director. Se registra el trabajo con asistentes de IA en el inventario de `c-237` (A-03).
- **Alcance respecto de la entrega.** Este change **no modifica el ejemplar que se defiende**. Se ejecuta despues del cierre de la entrega (`c-235` → ... → `c-239`), segundo del grupo `c-229` → `c-230` → `c-228` → `c-232`, y depende de `c-229`. Hasta entonces la tesis solo lo menciona como trabajo futuro, en los terminos de `c-235` (requisito de trabajo futuro con procedencia acreditable en `subsec:corpus-independiente`, que ya pide registro de etiquetadores y regla prefijada). Si los autores quieren hacer algo antes de la defensa, es una Open Question (`design.md`, OQ6).

## Estado: DETENIDO (18/11/2026)

El change queda **detenido** y se conserva como trabajo futuro lo autocontenido: las funciones puras `evaluation/mayoria.py` y `kappa_fleiss` (`evaluation/kappa.py`) y el protocolo de referencia por mayoria. Las tareas quedan **sin marcar**; nada se aplico.

**Motivo.** Faltan los dos insumos que comparte la familia post-entrega: un marco poblacional completo (por el que `c-229` quedo detenido) y un `clasificacion_log` real acumulado (el repositorio tiene alrededor de 153 filas de prototipo y campana, 3 validadas). A eso se suman el consentimiento escrito de los etiquetadores independientes nuevos (alias desde `E6`) y una decision explicita K-02 sobre el envio de textos nuevos a la Gemini API. Sin muestra y sin etiquetadores, no hay referencia que construir.

**Reapertura.** Solo si el equipo opera el prototipo como su propia mesa de ayuda durante un periodo declarado y exporta la tabla `incidente` completa (que aporta el marco para `c-229` y el log real acumulado), con el consentimiento escrito de los etiquetadores independientes y la decision K-02. Hasta entonces, el change no se aplica.

## Why

La referencia de verdad del estudio es fragil: en la campana complementaria, los etiquetadores independientes `E1` y `E2` coincidieron en 138 de los 200 casos (kappa de Cohen `0,5569`, moderado), y la mitad de las 62 discordancias (29) es la frontera `Sistemas`--`Soporte Tecnico Software`. Con dos etiquetadores no hay mayoria: un desacuerdo solo se resuelve con un tercero, y entonces la referencia depende de una persona. Una referencia por mayoria de tres o mas etiquetadores, con la regla fijada antes de etiquetar, y un acuerdo multievaluador permiten estimar la fiabilidad de la referencia sin ese punto unico.

La devolucion de tercera instancia no exige este trabajo. Su criterio es otro: la evidencia nueva solo vale si su procedencia puede acreditarse. Por eso el change separa lo que no necesita datos (funciones puras con oraculos) de lo que si (la referencia de la muestra de `c-229`), y somete esto ultimo a las compuertas.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Funciones puras (TDD)** | `evaluation/mayoria.py` (mayoria, `sin_mayoria`, conjunto laxo) y `kappa_fleiss` + matriz de Cohen por pares en `evaluation/kappa.py`, sin cambiar el contrato de dos etiquetadores de `kappa_doble_etiquetado`. Oraculos sinteticos y un ejemplo publicado. | MEDIA |
| **B. Protocolo de referencia** | `docs/campana-medicion/protocolo-referencia-mayoria.md`: numero de etiquetadores, cegado, herramienta de etiquetado con marcas propias, regla de mayoria y de `sin_mayoria` declaradas antes de etiquetar, sin arbitro unico; constancia de la regla en custodia del director. | **ALTA** |
| **C. Compuertas** | Procedencia (K-01) y etica/legal (K-02) previas a cualquier computo sobre etiquetas reales; las comparte con `c-229`. | **ALTA** |
| **D. Referencia de la muestra** | Con las compuertas cerradas, etiquetado ciego de la muestra de `c-229` por etiquetadores nuevos (alias desde `E6`), construccion de la referencia y del Fleiss. | **ALTA** |
| **E. Memo, tesis y trazabilidad** | Seccion reservada `3.39` del memo; prosa solo en una version posterior a la defensa; entrada en `dictamen-correcciones.md`; registro del uso de asistentes de IA en el inventario de `c-237`. | MEDIA |

**No objetivos.**

- No modifica el ejemplar que se defiende.
- No recomputa, reetiqueta ni compara nada sobre el corpus retirado; no usa sus cifras ni artefactos como ancla, insumo o comparador.
- No reemplaza la referencia del corpus de 200 casos ni cambia sus cifras canonicas (`73,5 %`, `0,6508`, `110/138`, kappa `0,5569`).
- No modifica `evaluation/doble_etiquetado.py`, `evaluation/arbitraje.py` ni sus specs.
- No elige una etiqueta "verdadera" para los casos sin mayoria.

## Capabilities

### New Capabilities

- `evaluation-majority-reference`: funciones puras de la referencia por mayoria, protocolo declarado antes de etiquetar, compuertas de procedencia y etica/legal, registro de etiquetadores independientes y construccion de la referencia de la muestra probabilistica de `c-229`.

### Modified Capabilities

- `evaluation-framework`: se AGREGA el kappa de Fleiss para tres o mas etiquetadores con matriz de Cohen por pares; se MODIFICA el requisito del kappa de Cohen solo para remitir a Fleiss en lugar de declararlo fuera de alcance.
- `tesis-document`: se AGREGA un requisito condicionado (version posterior a la defensa, referencia construida y compuertas cerradas) para divulgar la referencia por mayoria y el consentimiento de sus etiquetadores.
- `tesis-numeros-canonicos`: se AGREGA el registro de la seccion reservada `3.39`.

Ya no se modifican `discordant-arbitration` ni `evaluation-out-of-sample-validation`.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `evaluation/mayoria.py`, `evaluation/tests/test_mayoria.py` | Nuevo | Funciones puras de mayoria |
| `evaluation/kappa.py`, `evaluation/tests/test_kappa_fleiss.py` | Modificado / nuevo | `kappa_fleiss`, matriz por pares; Cohen intacto salvo el mensaje de alcance |
| `docs/campana-medicion/protocolo-referencia-mayoria.md` | Nuevo | Protocolo, regla y cegado |
| `docs/campana-medicion/consentimiento-etiquetadores-referencia-mayoria.md` (nombre a confirmar) | Nuevo | Plantilla de consentimiento escrito previo, sin nombres |
| `evaluation/data/campana/registro_sujetos.csv` | Modificado, condicionado | Filas desde `E6` con codigos `P` libres |
| `evaluation/data/campana/probabilistica/` (de `c-229`) | Nuevo, condicionado | Hashes de planillas crudas, referencia, sidecar, Fleiss |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion reservada `3.39` |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |
| `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (de `c-237`) | Aditivo | Registro A-03 |
| `sections/04`, `07`, `08`, `11` | Condicionado | Solo en una version posterior a la defensa |

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Evidencia nueva no acreditable (repeticion de K-01) | Media | Compuerta de procedencia con acta del director contra la evidencia primaria |
| Regla "declarada antes" sin prueba independiente | Media | Constancia fechada en custodia del director, ademas del commit |
| No se consiguen etiquetadores independientes | Media | Las funciones y el protocolo quedan; la referencia no se construye y no se sustituye por menos etiquetadores sin declararlo |
| Datos sin autorizacion (K-02) | Media | Compuerta etica y legal compartida con `c-229` |
| Leer el Fleiss de la muestra como mejora de la referencia de los 200 | Media | Rotulo explicito: aplica a la muestra de `c-229`; la limitacion de los 200 (kappa `0,5569`) se conserva |

## Rollback Plan

`git revert` del commit: modulo nuevo, pruebas, protocolo y seccion del memo son aditivos; `kappa.py` vuelve a su version previa (el contrato de Cohen no cambia). Si se versionaron datos y se revoca una autorizacion o un consentimiento, se retiran en commit separado y se declara.

## Dependencies

- Despues del cierre de la entrega (`c-239`).
- Depende de `c-229` (muestra probabilistica y compuertas); la estimacion de `c-229` espera a su vez la referencia de este change (secuencia por grupos en `design.md`, D7).
- Trabajo de campo de los autores: convocatoria de etiquetadores y consentimiento escrito.
- `c-237`: inventario de uso de asistentes de IA.
- Consumidores aguas abajo: `c-228`, `c-232` (los adapta otro agente).

## Success Criteria

- [ ] `kappa_fleiss` reproduce un oraculo sintetico calculado a mano y un ejemplo publicado citado; `mayoria` cubre mayoria, empates y cobertura parcial; el contrato de `kappa_doble_etiquetado` no cambia.
- [ ] El protocolo fija numero de etiquetadores, cegado, herramienta, regla de mayoria y de `sin_mayoria`, sin arbitro unico, con constancia fechada en custodia del director antes de etiquetar.
- [ ] Ninguna etiqueta real entra en un computo sin el acta de las compuertas.
- [ ] Ninguna cifra ni artefacto retirado por `c-235` aparece como ancla, insumo o comparador.
- [ ] El ejemplar que se defiende no cambia por este change.
- [ ] `openspec validate c-230-referencia-por-mayoria-con-etiquetadores-independientes --strict` pasa.
