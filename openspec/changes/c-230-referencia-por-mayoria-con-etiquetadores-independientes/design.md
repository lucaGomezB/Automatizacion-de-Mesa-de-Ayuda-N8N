# Design: Referencia por mayoria con etiquetadores independientes

## Context

El ultimo dictamen CONEAU descuenta en el **criterio 4 (Metodologia, peso 20, nota 8)** que la
referencia fuera de muestra tiene un solo arbitro. El estado actual, sobre los artefactos versionados
por c-206:

- `evaluation/data/campana/doble_etiquetado_arbitrado.csv` (`476` filas): `E3` y `E4` sobre los `206`
  casos y `E5` sobre los `64` discordantes.
- `evaluation/data/campana/arbitraje_tres_vias.json` (`206` casos): `origen` (`consenso_e3_e4` en
  `142`, `arbitraje_e5` en `64`) y bandera `tres_vias` (los `6` casos `I033`, `I042`, `I056`, `I130`,
  `I194`, `I198`).
- `evaluation/data/campana/corpus_independiente_arbitrado.json` (`206` casos) y
  `evaluation/data/campana/predicciones_arbitrado.json` (clasificador congelado `hybrid-v3`).
- `evaluation/kappa.py::kappa_cohen` (exactamente dos etiquetadores; el kappa de Fleiss **no** esta
  implementado); `evaluation/metrics.py` (matrices y metricas por clase); `evaluation/campana.py`
  (`validar_registro_sujetos`, sin solape por `persona`).
- `evaluation/data/campana/registro_sujetos.csv` registra `E1`-`E5`; `P11` es de `E5`.

Protocolo ciego reutilizable: `docs/campana-medicion/runbook-arbitraje-discordantes.md` (hoja ciega
`id_caso,descripcion` pseudonimizada + copia vacia de `evaluation/data/plantilla_etiquetado.csv` +
codebook congelado `evaluation/data/campana/codebook_doble_etiquetado.md`), generador
`python -m evaluation.arbitraje hoja-ciega`.

La referencia vigente es un consenso de dos (`E3`/`E4`) con decision de un unico tercero (`E5`) en el
`31 %` (`64/206`). La fiabilidad es moderada (kappa `E3`/`E4` `0,6055`; `E1`/`E2` `0,5569`). Este
change agrega `3` etiquetadores independientes para construir una referencia por mayoria y estimar el
acuerdo multievaluador.

## Goals / Non-Goals

**Goals:**

- Disenar la convocatoria y el registro de `3` etiquetadores nuevos (`E6`, `E7`, `E8`) con
  consentimiento, sin datos personales.
- Construir, con `5` etiquetadores (`E3`, `E4`, `E6`, `E7`, `E8`), una referencia por MAYORIA con la
  regla de mayoria y el tratamiento de empates declarados ANTES de ver las etiquetas.
- Implementar el kappa de Fleiss y la matriz de acuerdo por pares sin cambiar el contrato de dos
  etiquetadores.
- Recomputar la cifra primaria bajo la nueva referencia y COMPARARLA con la vigente, informando ambas.
- Registrar todo en una seccion aditiva del memo, incorporarlo a la tesis y dejar trazabilidad.

**Non-Goals:**

- Reclasificar con otro clasificador, recalibrar tau, el prompt o el vocabulario.
- Elegir una etiqueta «verdadera» para los casos sin mayoria: se declara el conteo y el rango.
- Recalibrar `evaluation-reference-noise-sensitivity` ni `evaluation-corpus-bias-mitigation`.
- Ejecutar el campo dentro del repositorio: lo hacen los autores fuera y el change depende de ello.

## Decisions

### D1 — Cantidad de etiquetadores: `5` en total (se convocan `3` nuevos)

El diseno recomendado es `5` etiquetadores (`E3`, `E4`, `E6`, `E7`, `E8`). Con `5`, la mayoria
`>= 3` solo queda indefinida en empates `2-2-1` (sin mayoria absoluta) o `2-1-1-1` (mayoria relativa
de `2`); es el menor numero que da margen para estimar un acuerdo multievaluador estable y responder al
«un solo arbitro en el `31 %`». Alternativas: `+1` (total `3`), que hace imposible el empate `2-2-1`
pero es fragil (una sola persona cambia la mayoria y el Fleiss sobre `3` es inestable) y es el
**minimo viable**; `+2` (total `4`) admite empate `2-2` en la mitad de la mayoria. Se elige `+3`. El
`E5` actual no entra en la mayoria (sus etiquetas quedan como referencia vigente de comparacion);
incluirlo seria una variante de `6` etiquetadores que se descarta por no responder al diseno `5` y por
reintroducir al arbitro unico en la referencia primaria.

### D2 — Cobertura del etiquetado: corpus completo `206` (recomendado); minimo los `64` divergentes

Etiquetar los `206` casos permite que la mayoria sea estimable en todos y que el kappa de Fleiss se
calcule sobre el corpus completo. El **minimo viable** es etiquetar solo los `64` casos divergentes
(los que hoy decide `E5`); entonces la mayoria y el Fleiss se estiman sobre los `64` y los `142`
restantes conservan el consenso `E3`/`E4`, rotulado. La cobertura efectiva se declara y decide el
alcance del Fleiss (RN de OOS-026). No se imputan etiquetas faltantes.

### D3 — Regla de mayoria y tratamiento de empates, declarados a priori

Regla deterministica y reproducible, fijada en el runbook ANTES de ver cualquier etiqueta de `E6`-`E8`:

1. **Mayoria absoluta**: si un sector obtiene `>= 3` de `5` votos, es la referencia.
2. **Empate** (`2-2-1` sin mayoria, o `2-1-1-1` con mayoria relativa de `2`): el caso se marca
   `sin_mayoria` y se resuelve con la **regla de respaldo**: la referencia vigente de arbitro unico
   (`E5` si `E3`/`E4` difieren; consenso `E3`/`E4` si coinciden), **rotulada como respaldo**. No se
   elige una etiqueta «verdadera» ni se promedia.
3. **Conjunto laxo**: la union de los sectores adicionales marcados por al menos `3` de los `5`
   etiquetadores, sin repetir el sector de la referencia.
4. El conteo de `sin_mayoria`, sus identificadores y sus etiquetas se informan, y el efecto de la
   regla de respaldo se reporta como rango.

Alternativa descartada: escalar cada empate a un `6` etiquetador, porque reabre la dependencia de una
persona y complica la reproducibilidad. Alternativa descartada: elegir el minimo del conjunto por
conveniencia, porque es sesgo de seleccion.

### D4 — Kappa de Fleiss y matriz por pares en `evaluation/kappa.py`

Se AGREGA `kappa_fleiss(matriz_o_registros)` (formula de Fleiss con cantidad variable de etiquetadores
por caso) y `matriz_acuerdo_por_pares(registros)` (kappas de Cohen por par, reutilizando
`kappa_cohen`). No se modifica el contrato de `kappa_doble_etiquetado` (exactamente dos). El resultado
de Fleiss incluye `P_bar`, `P_e`, kappa, n, etiquetadores por caso, rotulo de Landis y Koch e IC
(asintotico declarado o bootstrap con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`); con `P_e = 1` se
declara no estimable. Funciones puras con pruebas sinteticas antes de implementar (TDD estricto).

### D5 — Constructor de la referencia por mayoria en un modulo propio `evaluation/mayoria.py`

Modulo nuevo que reutiliza `evaluation/doble_etiquetado.py` (reglas de planilla y
`TAREA_DOBLE_ETIQUETADO`), `evaluation/arbitraje.py` (hoja ciega y helpers) y `evaluation/corpus.py`,
sin cambiar sus contratos. Expone `mayoria(etiquetas)` (sector con `>= 3` o `None`), `construir_referencia_mayoria(...)`
y `ensamblar_mayoria(...)` que emiten `referencia_mayoria.json` y un sidecar con `origen`
(`mayoria_5`, `sin_mayoria_respaldo`) y el conteo. El sidecar replica la decision de c-206 (no cambiar
el esquema de `cargar_corpus`). El registro se valida con `validar_registro_sujetos` (sin solape por
`persona`) y se rechazan alias no registrados.

### D6 — Recomputo con anclaje y comparacion honesta

Script `evaluation/data/campana/analisis/analisis_referencia_mayoria_c230.py` (solo lectura, sin red
ni Gemini) que lee `referencia_mayoria.json`, `corpus_independiente_arbitrado.json` y
`predicciones_arbitrado.json`; reproduce los anclajes `142/206` (`0,6893`) y macro-F1 `0,7024` sobre la
referencia vigente antes de escribir (aborta sin escribir si no coinciden); y emite
`analisis_referencia_mayoria_c230.{json,md,SHA256SUMS.txt}` con: las dos lecturas (mayoria y vigente)
de exactitud estricta y metricas por clase con IC de Wilson; el delta y el conteo de casos que cambian
de acierto a error y viceversa; el veredicto del umbral `0,85` por lectura; y el Fleiss con la matriz
por pares. Determinista byte a byte. La rotulacion de la cifra «primaria» es decision editorial de los
autores (Open Question OQ2); el script no la impone.

### D7 — Consentimiento y registro

`evaluation/data/campana/registro_sujetos.csv` suma `E6,etiquetador,P12`, `E7,etiquetador,P13`,
`E8,etiquetador,P14`. La plantilla `docs/campana-medicion/confirmacion-posterior-consentimiento.md` se
extiende para admitir los alias nuevos y su tabla de registro. La correspondencia alias-identidad la
custodia el director fuera del repositorio. Sin consentimiento registrado, las etiquetas de ese sujeto
no entran en la referencia. Gobernanza **HIGH**.

### D8 — Memo y prosa

Seccion aditiva del memo (primer numero libre al aplicar; hoy la ultima es `3.37`, esperado `3.39`)
con todos los valores, procedencia, estado y comando (D6). Prosa: `04-marco-metodologico.tex` (diseno),
`07-resultados.tex` (dos lecturas + Fleiss), `08-discusion.tex` (limitacion acotada),
`10-recomendaciones.tex` (linea ejecutada retirada). Trazabilidad en
`docs/Tesis/Correcciones/dictamen-correcciones.md` (`C30/…`).

### D9 — Orden de las tareas

1. Linea de base y verificacion de estado (incluye fijar el numero libre del memo).
2. **Checkpoint de los autores**: cantidad de etiquetadores y cobertura (D1/D2) y regla de desempate
   (D3), antes de cualquier etiquetado.
3. Registro de sujetos y consentimiento (D7).
4. Modulos y pruebas TDD (D4, D5).
5. Etiquetado ciego (campo, fuera del repositorio) y artefactos (D2/D5).
6. Recomputo y comparacion (D6).
7. Memo y prosa (D8).
8. Verificaciones y cierre.

### D10 — Gobernanza y frontera

- Sujetos y consentimiento (bloques A/B): **HIGH**; checkpoint de los autores.
- Regla de mayoria/empates y rotulacion de la cifra primaria: **HIGH/MEDIUM** (decision editorial).
- Modulos, script y memo/prosa: **MEDIUM**.
- Sin cambios en `App/`, `n8n/`, el clasificador, el corpus de ajuste ni los artefactos congelados.
- Cero llamadas pagas (el recomputo usa predicciones congeladas).

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| Los `3` etiquetadores no se consiguen o falta consentimiento | Bloquea el change; se declara la limitacion; con `+1` solo se cubre el minimo |
| El resultado cambia y se lee como correccion silenciosa | Se reportan AMBAS referencias con su rotulo; el delta y el veredicto se informan |
| Los casos `sin_mayoria` sesgan la referencia | Regla declarada a priori; conteo y efecto informados como rango |
| Cobertura parcial (`64`) y Fleiss inestable | Se declara la cobertura; el Fleiss se limita a los casos con cobertura |
| La prosa promete una medicion no hecha | El change depende del campo; los no objetivos lo declaran |
| Colision de numeracion del memo | Primer numero libre al aplicar (tarea 0.5) |
| Cambio no deseado en el contrato de dos etiquetadores | Pruebas de `doble_etiquetado.py` y `arbitraje.py` en la red de seguridad |

## Migration Plan

1. Preparacion y linea de base (tareas 0).
2. Checkpoint de autores y registro/consentimiento (tareas 1 y 2).
3. Modulos y pruebas TDD (tareas 3 y 4).
4. Campo y artefactos (tarea 5).
5. Recomputo (tarea 6).
6. Memo, prosa y trazabilidad (tareas 7 y 8).
7. Verificaciones y cierre (tarea 9).

**Rollback**: `git revert` del commit; el modulo, el script, sus salidas, la seccion del memo y la
prosa vuelven; el registro y el artefacto nuevos se retiran. Ningun valor canonico previo cambia.

## Open Questions

- **OQ1 (autores, bloquea la tarea 1)**: confirmar el diseno de `5` etiquetadores (`E3`, `E4`, `E6`,
  `E7`, `E8`) frente al minimo de `3` (`+1`), y la cobertura (corpus completo `206` frente a los `64`
  divergentes).
- **OQ2 (autores, bloquea la prosa)**: confirmar si la cifra por mayoria pasa a ser la primaria y la
  de arbitro unico queda como comparacion, o si ambas se informan sin rotular una como primaria.
- **OQ3 (autores, opcional)**: confirmar la regla de respaldo de los casos `sin_mayoria` (referencia
  vigente de arbitro unico) frente a escalar a un `6` etiquetador.
