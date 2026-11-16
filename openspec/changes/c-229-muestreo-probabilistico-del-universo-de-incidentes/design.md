# Design: Muestreo probabilistico del universo de incidentes

## Adaptacion a la devolucion de tercera instancia (16/11/2026)

- **Premisa que cayo.** La version del 15/11 anclaba la herramienta en `0,7489` (lectura ponderada sobre el corpus fuera de muestra arbitrado, bootstrap `[0,6822; 0,8099]`, leida de `analisis_propagacion_arbitraje_c221.json`) y ubicaba la prosa junto a esa cifra en la subseccion de validacion fuera de muestra de `07-resultados.tex`. Todo eso queda **retirado** del ejemplar por decision de los autores ante K-01; el motivo esta en `c-235` (`design.md`, D1 y D3) y no se reformula aqui. El viejo D4 (anclaje en `0,7489`) y el viejo D6 (host en resultados) se reemplazan por D4 y D7 de este documento.
- **Que se conserva.** D1 (alcance diseno + herramienta), D2 (universo, marco, estratos) y D3 (Horvitz-Thompson, post-estratificacion, DEFF, bootstrap), con ajustes.
- **Que cambia.** Se agregan D5 (compuerta de procedencia), D6 (compuerta etica y legal, con el envio a la Gemini API), D8 (dependencia cruzada con `c-230`) y D9 (cuotas minimas a partir de la composicion verificada). La verificacion de la herramienta pasa a un oraculo sintetico y a un control de sanidad sobre el corpus de 200.
- **Alcance respecto de la entrega.** Ningun paso de este change modifica el ejemplar que se defiende; se ejecuta despues de `c-239`. La tesis defendida solo menciona el diseno como trabajo futuro en los terminos de `c-235` y `c-234`.

## Context

- La muestra del estudio es no probabilistica por conveniencia: los 200 incidentes cronometrados en la campana manual (`subsec:poblacion-muestra-corpus`, `04-marco-metodologico.tex`), de una sola organizacion (servicios, Mendoza). El universo trimestral es `N ≈ 2.646 = 42 × 63` (memo, seccion 3.4, linea 145), **proyectado, no medido**; la distribucion por sector no esta disponible (memo, linea 376). El margen `6,66 %` presupone un muestreo aleatorio que no se realizo.
- **Composicion del corpus de 200 (verificada en esta adaptacion)**, leida de `data/corpus_evaluacion_pseudonimizado.json` (`casos[*].sector_asignado` y `canal_origen`):

  | Sector | Casos | Correo | Formulario | Telefono |
  |---|---:|---:|---:|---:|
  | Soporte Tecnico Hardware | 85 | 23 | 32 | 30 |
  | Soporte Tecnico Software | 67 | 23 | 16 | 28 |
  | Seguridad Informatica | 31 | 14 | 3 | 14 |
  | Sistemas | 16 | 6 | 1 | 9 |
  | Bases de Datos | 1 | 0 | 1 | 0 |
  | **Total** | **200** | **66** | **53** | **81** |

  Exactitud estricta cruda sobre el corpus de 200, recalculada de `evaluation/data/campana/predicciones_in_sample.json` (`sector_predicho == sector_asignado`): `147/200 = 0,7350`, que coincide con el valor canonico `73,5 %`. Por sector: Hardware 77/85, Software 48/67, Seguridad 15/31, Sistemas 7/16, Bases de Datos 0/1.
- La tesis defendida (tras `c-234` y `c-235`) remite a este diseno como remedio empirico **condicional y no ejecutado** (`09-conclusiones.tex`, `subsec:aportes-generalizacion`; `10-recomendaciones.tex`, `subsec:estudios-replicacion`) y propone como trabajo futuro una validacion con procedencia acreditable (`subsec:corpus-independiente`, requisito agregado por `c-235`).
- El capitulo 7 (`11-aspectos-legales.tex`) declara la base de licitud del sistema, que el instrumento de transferencia internacional esta documentado pero **no suscrito** y que a los proveedores llegaron solo los textos y audios del corpus de 200 (`subsec:transferencia-internacional`; `c-235` lo deja exacto). Una campana nueva que clasifique con el hibrido agrega transferencias.
- Insumos de codigo reutilizables (solo lectura): `evaluation/linea_de_base.py::lectura_ponderada` (forma de la post-estratificacion; el modulo queda en el repo aunque su uso en la tesis se retira), `evaluation/metrics.py` (Wilson, constantes de bootstrap) y `evaluation/stats.py`.

## Goals / Non-Goals

**Goals:**

- Definir universo, marco y estratos con procedencia verificable, registrados antes de reunir la muestra.
- Fijar un diseno estratificado con cuotas prefijadas por canal y sector, con minimos por sector y clases no estimables declaradas de antemano.
- Entregar la estimacion ponderada (Horvitz-Thompson, post-estratificacion), el DEFF y un IC sobre el universo completo, verificados sin datos retirados.
- Cerrar dos compuertas (procedencia y etica/legal) antes de cualquier extraccion, envio a terceros o computo sobre datos nuevos.
- Dejar el resultado, si existe, listo para una version posterior a la defensa.

**Non-Goals:**

- Modificar el ejemplar que se defiende.
- Usar cifras o artefactos retirados por `c-235`.
- Elevar la exactitud del clasificador.
- Definir el protocolo de etiquetado y la regla de referencia: los define `c-230`.
- Resolver la limitacion de una sola organizacion: el diseno estima sobre el universo de esa organizacion en un periodo, no sobre otras.

## Decisions

### D1 — Alcance: diseno + herramienta + campana condicionada

El change entrega (a) el protocolo, (b) la herramienta verificada y (c), solo si las compuertas se cierran, la campana y su estimacion. Sin compuertas cerradas, el change termina en (a) y (b) y la tesis no cambia. Alternativa descartada: simular una muestra y reportarla como resultado (confunde diseno con medicion).

### D2 — Universo, marco y estratos

- **Universo:** incidentes informaticos registrados por la mesa de ayuda de la organizacion en un periodo declarado. `N ≈ 2.646` es solo el punto de partida (proyectado); el protocolo SHALL confirmarlo contra el registro del periodo y, si difiere, informar ambos.
- **Marco:** el registro operativo de incidentes del periodo, enumerable por identificador, con probabilidad de inclusion conocida y mayor que cero.
- **Estratos:** sector (cinco cadenas canonicas), canal (correo, formulario, telefono) y complejidad (definicion operacional en el protocolo, OQ1). La distribucion del universo por estrato SHALL derivarse del registro; la composicion del corpus de 200 MUST NOT usarse como peso.
- **Canal telefonico:** en el registro, una llamada figura como texto cargado por el operador; la campana no dispone de audio. El estrato identifica el origen, pero el insumo del clasificador es el texto registrado, no la transcripcion de una llamada; se declara como diferencia respecto del canal telefonico del estudio.
- **Celdas escasas:** el cruce sector × canal × complejidad tendra celdas vacias o minimas (en el corpus de 200, 13 de las 15 celdas sector × canal no estan vacias y `Bases de Datos` solo aparece en formulario). La regla de colapso de estratos se fija en el protocolo antes de reunir la muestra.

### D3 — Estimacion: Horvitz-Thompson, post-estratificacion, DEFF y bootstrap

- `w_i = 1 / pi_i`; exactitud estricta como razon ponderada de aciertos.
- Post-estratificacion a los totales del universo cuando esten disponibles del registro.
- DEFF de Kish `n · Σw_i² / (Σw_i)²`, informado junto a la exactitud ponderada. Sin muestra probabilistica, el DEFF del diseno es **no computable** y se declara asi.
- IC bootstrap percentil por unidad, estratificado por el diseno, con semilla fija, sobre el universo completo (sin excluir casos por discordancia: los casos `sin_mayoria` de `c-230` entran con su tratamiento declarado).
- Alternativa descartada: IC de Wilson sobre la muestra (presupone muestreo aleatorio simple).

### D4 — Verificacion de la herramienta sin datos retirados

Sustituye al viejo anclaje. Dos verificaciones, ambas previas a escribir salidas:

1. **Oraculo sintetico rotulado como tal.** Un fixture sintetico (`fixture_sintetico_c229.json`, rotulado `sintetico: true` en su cabecera) con estratos, probabilidades de inclusion y aciertos fijados a mano, cuyos valores esperados (pesos, exactitud ponderada, DEFF) se calculan a mano en la prueba. No es un dato del estudio y MUST NOT citarse como resultado.
2. **Control de sanidad sobre el corpus de 200.** Post-estratificar el corpus de 200 con **su propia** composicion por sector da pesos iguales: la exactitud ponderada SHALL reproducir la cruda `147/200 = 0,7350` y el DEFF SHALL ser `1`. Se leen `data/corpus_evaluacion_pseudonimizado.json` y `evaluation/data/campana/predicciones_in_sample.json`, no constantes. Este control prueba la implementacion; MUST NOT presentarse como estimacion poblacional ni como DEFF del diseno.

Si alguna falla, el script termina con codigo distinto de cero sin escribir. El script MUST NOT leer ningun artefacto que `c-235` retira (lista en la seccion de adaptacion del `proposal.md`).

| Funcion | Que calcula |
|---|---|
| `pesos_horvitz_thompson(estratos, tamanos_universo, tamanos_muestra)` | `w_i = 1 / pi_i` por estrato |
| `post_estratificar(casos, totales_universo)` | Pesos calibrados a totales del universo |
| `exactitud_ponderada(aciertos, pesos)` | Razon ponderada |
| `efecto_diseno(pesos)` | DEFF de Kish |
| `ic_bootstrap_universo(casos, pesos, estratos, semilla, remuestreos)` | IC percentil estratificado |

### D5 — Compuerta de procedencia (K-01)

Antes de computar sobre datos nuevos, el director (o un tercero que los autores designen y el director acepte) verifica contra la evidencia primaria y firma un acta con fecha:

- **(a) Planillas crudas:** una por etiquetador, exportadas de la herramienta de etiquetado con las marcas temporales que la herramienta registra. Nunca reconstruidas ni completadas a mano. La herramienta y el formato de exportacion se declaran en el protocolo antes de etiquetar.
- **(b) Constancias:** constancia firmada por cada etiquetador y constancia de la organizacion sobre la extraccion de los incidentes (fecha, periodo, sistema de origen, cantidad). Originales en custodia del director, fuera del repositorio. En el repositorio, el SHA-256 de cada planilla cruda y de la exportacion.
- **(c) Independencia:** los etiquetadores no son autores ni operadores medidos; se declara su vinculo con los autores (ninguno, laboral, academico, familiar u otro).
- **(d) Textos reales:** los textos son incidentes reales del registro de la organizacion, con constancia de extraccion. Ningun texto redactado por los autores, ni generado o asistido por IA, entra como dato. La pseudonimizacion se limita a reemplazar identificadores con un procedimiento declarado y su registro de cambios; no reescribe el texto.
- **(e) Verificacion:** el director (o el tercero) coteja (a)–(d) contra la evidencia primaria antes de habilitar el analisis. Ninguna comprobacion estadistica de forma (distribucion de duraciones, pausas, longitud de textos) sustituye esa verificacion; puede complementarla.

Sin acta firmada, la estimacion sobre datos reales no se ejecuta.

### D6 — Compuerta etica y legal (K-02)

Antes de extraer:

- **Autorizacion institucional escrita** de la organizacion para extraer y usar los incidentes del periodo, con su alcance (fines, publicacion, transferencias).
- **Base de licitud** conforme a la Ley 25.326 y **consentimiento** de los sujetos que corresponda: etiquetadores (consentimiento escrito previo, no confirmacion posterior) y, segun la autorizacion, titulares de los datos de los incidentes.
- **Envio a terceros:** clasificar con el hibrido envia el texto de cada caso a la Gemini API. Antes de clasificar SHALL decidirse por escrito si los textos se envian (y con que pseudonimizacion e instrumento de transferencia, dado que el instrumento del capitulo 7 no esta suscrito) o no. Si no se envian, el hibrido no puede medirse sobre la muestra y la estimacion se limita a lo que no requiere al proveedor; se declara. El capitulo 7 de la version posterior (§7.3 y la base de licitud) SHALL tratar estas transferencias con sus cantidades.
- **Publicacion:** en el repositorio publico entra solo material pseudonimizado y autorizado; el resto queda en custodia del director, con su hash publicado.

### D7 — Ubicacion en la tesis (solo version posterior a la defensa)

Sin la campana ejecutada y las compuertas cerradas, la tesis no cambia: la menciones vigentes de `c-234` y `c-235` bastan. Con ellas:

- `04-marco-metodologico.tex`, `subsec:poblacion-muestra-corpus`: un parrafo que describe la muestra probabilistica nueva como distinta del corpus de 200 (que sigue siendo por conveniencia) y la quinta amenaza de `subsec:amenazas-validez` precisa que la estimacion se refiere al universo del periodo de esa organizacion.
- `07-resultados.tex`: subseccion nueva (etiqueta propuesta `subsec:muestra-probabilistica`), no la que `c-235` retira, con exactitud ponderada y cruda rotuladas, DEFF, IC, cuotas alcanzadas y clases no estimables.
- `09-conclusiones.tex` (`subsec:aportes-generalizacion`) y `10-recomendaciones.tex` (`subsec:estudios-replicacion`): la remision pasa de "condicional y no ejecutado" a ejecutado, con su alcance. Requiere MODIFICAR el requisito de `c-234` (delta incluido).
- `10-recomendaciones.tex` (`subsec:corpus-independiente`): **no se modifica el requisito de `c-235`**; se agrega una remision a la subseccion de resultados, conservando los elementos que ese requisito exige (lo que queda pendiente: comparacion con linea de base clasica y brazo de modelo solo). Si los autores prefieren reescribir esa subseccion, se agrega al aplicar un delta MODIFIED sobre el requisito de `c-235`, ya archivado para entonces.
- `11-aspectos-legales.tex`: autorizacion, base de licitud, consentimiento de etiquetadores y transferencias nuevas.
- La redaccion de la muestra nueva como "estratificada" choca con el requisito vigente "Seleccion de los casos por conveniencia declarada" (escenario sin "estratificad" afirmativo en `04`); se MODIFICA para permitirlo solo respecto de la muestra nueva.

### D8 — Dependencia cruzada con `c-230`

`c-230` define las funciones puras de mayoria y Fleiss y el protocolo de referencia; `c-229` define el diseno y extrae la muestra. Secuencia por grupos: `c-229` grupos 0–3 (diseno, compuertas preparadas, herramienta) → `c-230` grupos 0–2 (funciones y protocolo) → `c-229` grupo 4 (extraccion y seleccion, con compuertas cerradas) → `c-230` etiquetado y referencia → `c-229` grupo 5 (clasificacion y estimacion) → memo y prosa de ambos. El orden de inicio `c-229` → `c-230` se mantiene; la estimacion sobre datos reales de `c-229` queda bloqueada hasta la referencia de `c-230`. Alternativa descartada: que `c-229` defina su propia regla de etiquetado (dos etiquetadores y tercero en discordancia), porque reintroduce el arbitro unico que `c-230` elimina.

### D9 — Cuotas minimas y clases no estimables

La composicion del corpus de 200 no representa al universo, pero es la unica senal disponible para planificar: si la prevalencia de `Bases de Datos` en el universo se pareciera a `1/200`, un periodo trimestral (`N ≈ 2.646`) tendria del orden de una decena de incidentes de esa clase, y una asignacion proporcional de `n = 200` daria uno. Decision:

- El protocolo fija, antes de reunir la muestra, una **cuota minima por sector** (por defecto 30 casos, OQ2) y sobremuestrea los sectores raros, con sus pesos de Horvitz-Thompson.
- Si el universo del periodo tiene menos casos de un sector que la cuota minima, ese estrato se toma **completo** (censo, `pi = 1`), y si aun asi queda por debajo del minimo, sus metricas por clase se declaran **no estimables** de antemano. Con la senal actual, `Bases de Datos` es candidata a no estimable; `Sistemas` (16/200) requiere sobremuestreo.
- La exactitud global ponderada si es estimable; el DEFF crece con el sobremuestreo y se informa.

### D9b — Corpus probabilistico acreditado

Termino de referencia comun con `c-228` y `c-232`: **corpus probabilistico acreditado** es la muestra seleccionada segun D2 y D9, con la compuerta de procedencia (D5) y la etica y legal (D6) cerradas por acta, y con la referencia por mayoria de `c-230` (D8). Se publica con un manifiesto (estrato, probabilidad de inclusion, referencia y `origen` por caso; fecha del acta) o, si la autorizacion no permite publicarlo, se custodia con su SHA-256 publicado. Es el unico conjunto retenido de evaluacion admisible para este change y sus consumidores; un conjunto al que le falte una condicion no lleva ese nombre (spec PS-009).

### D10 — Gobernanza

Compuertas, protocolo y campana: **ALTA** (datos de una organizacion, sujetos humanos, transferencia internacional); checkpoint de los autores y acta del director. Herramienta: **MEDIA**, TDD estricto. Memo y prosa: **MEDIA**, solo tras la campana.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| Evidencia nueva no acreditable (repeticion de K-01) | D5; acta del director previa a todo computo |
| Datos sin autorizacion o enviados a terceros sin base (K-02) | D6; decision escrita sobre la Gemini API antes de clasificar |
| Control de sanidad leido como estimacion | D4: rotulado como verificacion de implementacion |
| Oraculo sintetico leido como dato | Cabecera `sintetico: true` y rotulo en salidas |
| Clases raras no estimables | D9: minimos y no estimables declarados antes |
| Dependencia circular con `c-230` | D8: secuencia por grupos |
| Organizacion no coopera | El change queda en diseno y herramienta; no se sustituye por conveniencia |

## Migration Plan

1. Grupo 0: linea de base, verificacion de estado y de que `c-235`..`c-239` estan cerrados.
2. Grupo 1: compuertas preparadas (listas de verificacion, modelos de constancia y autorizacion).
3. Grupo 2: protocolo (checkpoint de autores).
4. Grupo 3: herramienta TDD.
5. Grupo 4: extraccion y seleccion (solo con compuertas cerradas).
6. Grupo 5: clasificacion y estimacion (tras la referencia de `c-230`).
7. Grupos 6–7: memo, prosa posterior a la defensa, trazabilidad, A-03, verificacion.

Rollback: `git revert`; datos versionados se retiran en commit separado si se revoca la autorizacion.

## Open Questions

- **OQ1 (autores):** periodo del universo y definicion operacional de complejidad.
- **OQ2 (autores):** tamano objetivo y cuota minima por sector (por defecto 30).
- **OQ3 (autores):** ¿la organizacion va a cooperar (registro del periodo, autorizacion escrita, constancia de extraccion)? Sin eso, la campana no se ejecuta.
- **OQ4 (autores):** ¿se envian los textos de la muestra a la Gemini API? En caso afirmativo, ¿con que instrumento de transferencia y base de licitud?
- **OQ5 (autores):** ¿quieren hacer algo de este change antes de la defensa? Por defecto, nada: se ejecuta despues de `c-239` y la tesis defendida solo lo menciona como trabajo futuro.
- **OQ6 (autores):** ¿quien verifica las compuertas, el director o un tercero? ¿Quien custodia los originales?
- **OQ7 (aplicacion):** nombres definitivos de `compuertas-c229.md` y de la carpeta de datos de la muestra.
