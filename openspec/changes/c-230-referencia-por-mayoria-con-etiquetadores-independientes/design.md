# Design: Referencia por mayoria con etiquetadores independientes

## Adaptacion a la devolucion de tercera instancia (16/11/2026)

- **Premisa que cayo.** El diseno del 15/11 (D1 a D10) construia la referencia por mayoria de `E3`, `E4`, `E6`, `E7` y `E8` sobre los `206` casos fuera de muestra, conservaba al arbitro unico `E5` como respaldo y comparador, y anclaba un recomputo en `142/206`, `0,7024` y kappa `0,6055`, leyendo `doble_etiquetado_arbitrado.csv`, `arbitraje_tres_vias.json`, `corpus_independiente_arbitrado.json` y `predicciones_arbitrado.json`. Todo eso queda **retirado** del ejemplar por decision de los autores ante K-01; el motivo esta en `c-235` (`design.md`, D1 y D3). Ese diseno no se parchea: se reemplaza por el de este documento.
- **Deltas eliminados.** (a) `evaluation-out-of-sample-validation` (OOS-026 recomputo): su objeto ya no existe y su ID chocaba con el `OOS-026` que agrega `c-235`. (b) `discordant-arbitration`: los ADDED ARB-009..012 y los MODIFIED ARB-001/002/004 describian a `E3`/`E4`/`E5` sobre los 206 casos. `c-235` decide conservar sin cambios las specs de codigo de esa capability porque el codigo queda (`c-235`, `design.md`, D8); este change no la toca y crea una capability propia. Ver "Hallazgo" en Context.
- **Que se conserva.** La mayoria con regla prefijada, el tratamiento de `sin_mayoria`, el conjunto laxo, el kappa de Fleiss con matriz por pares, el modulo propio `evaluation/mayoria.py`, la seccion reservada `3.39`.
- **Que cambia.** Sin arbitro unico de respaldo; destino: la muestra probabilistica de `c-229`; compuertas K-01/K-02; constancia de la regla en custodia del director; consentimiento escrito previo con plantilla nueva (la de confirmacion posterior se retira con la validacion); alias nuevos desde `E6`.
- **Alcance respecto de la entrega.** Ningun paso modifica el ejemplar que se defiende; se ejecuta despues de `c-239` y de `c-229`.

## Context

- **Linea base que sobrevive (verificada en esta adaptacion).** `evaluation/data/campana/doble_etiquetado.csv`: 400 filas, `E1` y `E2` con 200 casos cada uno (`tarea = doble_etiquetado`). Coinciden en 138 casos y discrepan en **62**; las discordancias por par de sectores son: `Sistemas`/`Soporte Tecnico Software` **29**, `Soporte Tecnico Hardware`/`Soporte Tecnico Software` 15, `Seguridad Informatica`/`Soporte Tecnico Software` 8, `Sistemas`/`Soporte Tecnico Hardware` 4, `Seguridad Informatica`/`Sistemas` 4, `Bases de Datos`/`Soporte Tecnico Software` 1, `Seguridad Informatica`/`Soporte Tecnico Hardware` 1. Kappa de Cohen recalculado: `p_o = 0,69`, `p_e = 0,30045`, kappa `= 0,5569` (coincide con el canonico). Codebook: `evaluation/data/campana/codebook_doble_etiquetado.md`.
- **Codigo existente.** `evaluation/kappa.py::kappa_cohen` y `kappa_doble_etiquetado` (exactamente dos etiquetadores; hoy el mensaje declara Fleiss "fuera del alcance", L62 y L351). `evaluation/mayoria.py` no existe. `evaluation/campana.py::validar_registro_sujetos` valida el registro sin solape por `persona`.
- **Registro de sujetos.** `evaluation/data/campana/registro_sujetos.csv` usa los codigos `P1` a `P11`; el primer codigo libre es `P12`. Los alias nuevos empiezan en `E6`.
- **Tesis defendida.** `subsec:corpus-independiente` (requisito de `c-235`) ya pide, como trabajo futuro, etiquetadores identificados en un registro de sujetos, marcas temporales registradas por la herramienta y regla prefijada. La octava limitacion de `subsec:limitaciones-estudio` (`08-discusion.tex`) trata la fragilidad de la referencia con el kappa `0,5569`; `c-235` la reescribe sin el corpus retirado.
- **Hallazgo para el orquestador.** La spec principal `openspec/specs/discordant-arbitration/spec.md` (ARB-001..008) sigue describiendo como requisitos vigentes el arbitraje del corpus retirado; `c-235` la conserva a proposito porque el codigo queda. Este change no la modifica para no editar requisitos que otro change decidio conservar; queda como decision fuera de este change.

## Goals / Non-Goals

**Goals:**

- Funciones puras de mayoria y de Fleiss probadas con TDD estricto contra oraculos sinteticos y un ejemplo publicado, sin datos del estudio.
- Protocolo de referencia por mayoria declarado y constatado antes de etiquetar, sin arbitro unico.
- Referencia de la muestra de `c-229` construida solo con las compuertas cerradas; con ella, esa muestra pasa a ser el **corpus probabilistico acreditado** (PS-009 de `c-229`), unico conjunto retenido que consumen `c-228` y `c-232`.

**Non-Goals:**

- Cualquier operacion sobre el corpus retirado.
- Reemplazar la referencia del corpus de 200 o sus cifras.
- Modificar `doble_etiquetado.py`, `arbitraje.py` o las specs `discordant-arbitration`.

## Decisions

### D1 — Funciones puras primero, sin datos

`evaluation/mayoria.py` expone:

| Funcion | Que hace |
|---|---|
| `mayoria(etiquetas, umbral)` | Sector con al menos `umbral` votos, o `None` |
| `clasificar_caso(etiquetas, umbral)` | `mayoria` o `sin_mayoria`, con el recuento por sector |
| `conjunto_laxo(etiquetas_adicionales, umbral, principal)` | Sectores adicionales con al menos `umbral` votos, sin repetir el principal |
| `construir_referencia(registros, umbral)` | Referencia por caso con `origen` (`mayoria` o `sin_mayoria`) y conteos |

`evaluation/kappa.py` agrega `kappa_fleiss(conteos)` (cantidad variable de etiquetadores por caso) y `matriz_acuerdo_por_pares(registros)` (reutiliza `kappa_cohen`). Oraculos: (a) matrices sinteticas pequenas con `P_bar`, `P_e` y kappa calculados a mano en la prueba; (b) un ejemplo publicado del kappa de Fleiss, citado en la prueba con su fuente y con el valor tomado de esa fuente al aplicar (no se fija aqui un valor no verificado); (c) casos limite: `P_e = 1` (no estimable), cobertura variable.

### D2 — Numero de etiquetadores y regla de mayoria

Por defecto **cinco** etiquetadores nuevos por caso, umbral `>= 3`. Con cinco, la mayoria absoluta falla solo en empates `2-2-1` y `2-1-1-1`. Minimo aceptable: tres (umbral `>= 2`), mas fragil. La eleccion es OQ1 y se fija en el protocolo antes de etiquetar.

### D3 — Casos sin mayoria: sin arbitro unico

Un caso sin mayoria se marca `sin_mayoria`, se lista con su recuento y **no** se resuelve con la decision de una persona. Tratamiento por defecto, declarado antes de etiquetar: entra en la estimacion de `c-229` con dos lecturas acotantes (acierto si el clasificador elige cualquiera de los sectores empatados en el maximo; error en otro caso), informadas como rango, y su conteo se informa. Alternativas descartadas: un sexto etiquetador o un arbitro (reintroduce la dependencia de una persona); excluir los casos (sesga la estimacion y contradice el IC sobre el universo completo de `c-229`). OQ2.

### D4 — Constancia de la regla en custodia del director

La fecha de commit del protocolo no prueba por si sola que la regla precede al etiquetado (la controlan los autores). Antes de entregar el paquete ciego, el protocolo impreso o su hash SHA-256 se entrega al director, que firma una constancia con fecha; el original queda en su custodia y el hash del documento constatado se versiona. La regla vigente es la del documento constatado.

### D5 — Compuertas (comparten acta con `c-229`)

- **Procedencia (K-01):** (a) planilla cruda por etiquetador, exportada de la herramienta declarada con sus marcas temporales propias, nunca reconstruidas ni completadas a mano; (b) constancia firmada por cada etiquetador y constancia de extraccion de la organizacion, originales en custodia del director, SHA-256 de cada planilla cruda en el repositorio; (c) independencia: no autores, no operadores medidos, vinculo con los autores declarado; (d) los textos son incidentes reales del registro de la organizacion (constancia de `c-229`), ninguno redactado por los autores ni generado o asistido por IA; (e) el director (o un tercero) verifica contra la evidencia primaria antes de habilitar el computo. Ninguna comprobacion estadistica de forma sustituye esa verificacion.
- **Etica y legal (K-02):** autorizacion institucional y base de licitud (Ley 25.326) de `c-229`; consentimiento **escrito previo** de cada etiquetador con una plantilla nueva (la de confirmacion posterior queda retirada con la validacion); los etiquetadores reciben solo textos pseudonimizados y autorizados; este change no envia textos a terceros (la clasificacion es de `c-229`); al repositorio publico entra solo material pseudonimizado y autorizado.

### D6 — Registro y cegado

Alias nuevos desde `E6`, codigos `P` desde `P12`, sin reutilizar alias previos. Por defecto, personas distintas de todas las registradas (`P1`..`P11`); la participacion de una persona ya registrada es OQ4. El paquete ciego contiene solo `id_caso`, texto pseudonimizado, una plantilla vacia y el codebook congelado; ningun etiquetador ve etiquetas ajenas, la referencia ni las predicciones.

### D7 — Secuencia con `c-229`

`c-229` grupos 0–3 → `c-230` grupos 0–3 (funciones y protocolo constatado) → `c-229` grupo 4 (extraccion y seleccion) → `c-230` grupos 4–5 (consentimiento, etiquetado, compuerta, referencia) → `c-229` grupo 5 (estimacion) → memo y prosa de ambos.

### D8 — Tesis y memo

Sin referencia construida y compuertas cerradas, la tesis no cambia. Con ellas, en una version posterior a la defensa: metodo (protocolo y regla), resultados (Fleiss y matriz por pares rotulados como fiabilidad entre etiquetadores de la muestra nueva, conteo `sin_mayoria`), discusion (la limitacion de la referencia de los 200 se conserva; la muestra nueva tiene su propia fiabilidad), capitulo 7 (consentimiento escrito previo de los etiquetadores, solo alias). Memo: seccion reservada `3.39`.

### D9 — Gobernanza

Funciones puras: **MEDIA**, TDD estricto. Protocolo, compuertas, sujetos y etiquetado: **ALTA**, checkpoint de autores y acta del director. Memo y prosa: **MEDIA**, solo tras la referencia.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| Evidencia no acreditable | D5, acta previa |
| Regla modificada tras ver etiquetas | D4, constancia del director |
| Empates frecuentes en `Sistemas`/`Software` (29 de 62 discordancias en los 200) | Cinco etiquetadores por defecto; rango de `sin_mayoria` informado |
| Oraculo publicado mal transcrito | Valor tomado de la fuente al aplicar, con cita en la prueba |
| Confundir Fleiss de la muestra con mejora de los 200 | D8, rotulo explicito |

## Migration Plan

1. Grupo 0: estado (entrega cerrada, `c-229` en curso), linea base, checkpoint de autores.
2. Grupos 1–2: TDD de `kappa_fleiss` y `mayoria`.
3. Grupo 3: protocolo y constancia del director.
4. Grupo 4: consentimiento, registro, etiquetado ciego.
5. Grupo 5: compuerta K-01 y construccion de la referencia y del Fleiss.
6. Grupos 6–7: memo, prosa posterior a la defensa, trazabilidad, A-03, verificacion.

Rollback: `git revert`; datos versionados se retiran en commit separado si se revoca una autorizacion o consentimiento.

## Open Questions

- **OQ1 (autores):** cinco etiquetadores por caso (recomendado) o el minimo de tres.
- **OQ2 (autores):** tratamiento de `sin_mayoria` (rango acotante por defecto) frente a otra regla sin arbitro unico.
- **OQ3 (autores):** ¿quienes serian los etiquetadores y que vinculo tienen con los autores? ¿Estan dispuestos a firmar consentimiento previo y constancia?
- **OQ4 (autores):** ¿puede participar una persona ya registrada (por ejemplo, de `E1`/`E2`) con alias nuevo? Por defecto, no.
- **OQ5 (autores):** herramienta de etiquetado que exporte marcas temporales propias.
- **OQ6 (autores):** ¿quieren hacer algo de este change antes de la defensa? Por defecto, nada; a lo sumo, las funciones puras no afectan el ejemplar.
- **OQ7 (orquestador):** destino de la spec principal `discordant-arbitration` (ver Hallazgo).
