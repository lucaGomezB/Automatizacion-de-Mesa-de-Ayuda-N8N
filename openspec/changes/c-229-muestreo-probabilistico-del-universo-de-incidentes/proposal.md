# Proposal: Muestreo probabilistico del universo de incidentes

## Why

La amenaza 5 (validez externa, `04-marco-metodologico.tex:114`) declara que los 200 casos **no son una muestra probabilistica**: son los incidentes cronometrados en la campana manual, una muestra por conveniencia de una sola organizacion. El corpus se tomo sin estratificacion ni asignacion proporcional (memo, seccion 3.17, ap. (f), N-04) y la distribucion del universo por sector **no esta disponible** (memo, linea 376). Por eso el margen de error del `6,66 %` y todo IC reportado **presuponen un muestreo aleatorio que no se realizo** (`04-marco-metodologico.tex:52`): son una referencia, no una garantia de representatividad.

La lectura ponderada de la exactitud estricta (`0,7489`, `07-resultados.tex:393`) usa como pesos la **composicion por sector del corpus de 200** y no la del universo (memo, requisito OOS-020): pondera la muestra, no la refiere a la poblacion. La tesis ya fija la linea de trabajo futuro: repetir la validacion sobre un "corpus de composicion natural, con cuotas prefijadas por canal y por sector" y estimar el intervalo de confianza sobre el "universo completo, sin excluir casos" (`10-recomendaciones.tex:26`).

Este change convierte esa linea en un **diseno probabilistico reproducible**: define el universo y su marco, fija un muestreo estratificado con cuotas prefijadas por canal y por sector, y entrega la maquinaria de estimacion ponderada (Horvitz-Thompson / post-estratificacion) con su efecto de diseno, para que las metricas puedan referirse al universo. No mide de nuevo, no cambia ningun valor canonico y **no eleva la exactitud del clasificador**: valida la estimacion.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Diseno muestral** | Protocolo nuevo `docs/campana-medicion/protocolo-muestreo-probabilistico.md`: universo (poblacion del periodo, `N`), marco muestral, estratos (sector, canal, complejidad), cuotas prefijadas por canal y por sector, denominadores y reglas de decision prefijados, etiquetado independiente y consentimiento. Sin valores numericos nuevos de resultado. | **HIGH** (datos nuevos, etiquetado humano, consentimiento) |
| **B. Herramienta de estimacion** | Script offline de solo lectura `evaluation/data/campana/analisis/estimador_muestreo_probabilistico_c229.py` (TDD) que calcula pesos de Horvitz-Thompson y post-estratificacion, la exactitud estricta ponderada y el **efecto de diseno** (Kish), con IC bootstrap sobre el universo completo (sin exclusion). Corre sobre un fixture sintetico y reproduce el ancla vigente `0,7489`. | MEDIUM |
| **C. Tesis** | Marco metodologico (`04`, subseccion de poblacion, muestra y corpus) declara el diseno probabilistico y su estado `condicional`; resultados (`07`) reportan la lectura ponderada y su efecto de diseno rotulados; discusion (`08`, amenaza y limitacion de seleccion) precisa que el diseno no elimina el sesgo sin datos; recomendaciones (`10`) remiten al diseno. | MEDIUM |
| **D. Memo canonico** | Seccion aditiva `3.40` en `docs/Tesis/Correcciones/numeros-canonicos.md` que registra la lectura ponderada y su efecto de diseno con procedencia y estado `condicional`. | LOW |
| **E. Trazabilidad** | Entrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` con el change, el artefacto y las anclas de prosa. | LOW |

**No objetivos.**

- No se ejecuta la campana probabilistica: **depende de datos que aun no existen y de la cooperacion de la organizacion**. El cambio entrega el diseno, la herramienta y la declaracion honesta.
- No se cambia ningun valor canonico: `71,2 %`, `[67,2 %; 74,6 %]`, `73,5 %`, `0,6508`, `0,6893` y `0,7489` permanecen.
- No se afirma que el diseno suba la exactitud del clasificador; solo habilita una **estimacion valida**.
- No se tocan `App/`, `n8n/`, el clasificador, el corpus, las predicciones ni los artefactos congelados.
- No hay llamadas pagas a Gemini ni trabajo de campo.

## Capabilities

### New Capabilities

- `evaluation-probabilistic-sampling`: el diseno de muestreo probabilistico estratificado del universo de incidentes (marco, estratos, cuotas, reglas de decision) y la estimacion ponderada referida al universo (Horvitz-Thompson / post-estratificacion, efecto de diseno, IC sobre el universo completo).

### Modified Capabilities

- `tesis-document`: se agrega el requisito de declarar el diseno probabilistico y su estado `condicional` en metodologia y trabajo futuro, y de reportar la lectura ponderada con su efecto de diseno rotulados, sin afirmar que la muestra es probabilistica.
- `tesis-numeros-canonicos`: se agrega el requisito de registro aditivo de la lectura ponderada y del efecto de diseno, con procedencia y estado `condicional`.

`evaluation-out-of-sample-validation` no se modifica: su ponderacion (OOS-006 / OOS-020) es el antecedente que este change generaliza, y el contrato que cambia es el del diseno probabilistico, que vive en la capability nueva.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/campana-medicion/protocolo-muestreo-probabilistico.md` | Nuevo | Diseno muestral, marco, estratos, cuotas, reglas y consentimiento |
| `evaluation/data/campana/analisis/` | Nuevo | Script TDD, prueba, fixture sintetico, JSON/MD y manifiesto SHA-256 |
| `evaluation/data/campana/analisis/README.md` | Modificado | Registro de entradas, comando, salidas y pruebas |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion nueva (esperado `3.40`) con la lectura y el efecto de diseno |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | Declaracion del diseno y su estado `condicional` |
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` | Modificado | Lectura ponderada con su efecto de diseno, rotulada |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | Precision en la amenaza 5 y en la limitacion de seleccion |
| `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` | Modificado | Remision al diseno probabilistico |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuracion, el corpus ni las predicciones. Cero llamadas a Gemini.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Que el diseno se lea como una medicion realizada o que la muestra de 200 se presente como probabilistica | Alta | Rotulo `condicional` y de "diseno planificado"; la cifra primaria sigue siendo `0,6893` y la muestra por conveniencia se declara como tal |
| Confundir el efecto de diseno de la post-estratificacion sobre la muestra por conveniencia con el del diseno probabilistico | Media | El script declara la procedencia de los pesos y el estado `condicional`; el efecto de diseno del diseno probabilistico se declara no computable sin la muestra |
| Duplicar o reinterpretar la lectura `0,7489` | Media | Se cita desde su seccion del memo (3.25 / 3.32) y no se redefine; la seccion nueva solo agrega el efecto de diseno |
| Que la numeracion del memo colisione | Baja | Se fija el primer numero libre al aplicar (hoy la ultima es `3.37`; esperado `3.40`) |
| Crecimiento de paginas | Media | Un parrafo por archivo de prosa; verificacion de `\@abspage@last` |

## Rollback Plan

`git revert` del commit del change: el protocolo y el script con sus salidas son aditivos; la seccion del memo se retira sin tocar las anteriores; los parrafos de `04`, `07`, `08` y `10` se revierten por archivo. Ningun valor canonico previo se modifica, de modo que el rollback no deja huecos numericos.

## Dependencies

- Bloqueada por datos externos: la ejecucion de la campana requiere la poblacion del periodo y la cooperacion de la organizacion. Sin ellos el change entrega diseno, herramienta y declaracion, y deja las cifras del diseno en estado `condicional`.
- Antecedentes internos: `evaluation-out-of-sample-validation` (OOS-006, OOS-020) y `evaluation-campaign-instrumentation`; `evaluation/linea_de_base.py::lectura_ponderada` como funcion de post-estratificacion reutilizable.
- `docs/Tesis/Correcciones/analisis-limitaciones-estructurales-v1.4.1.md` (limitacion 3, no factible sin datos nuevos).

## Success Criteria

- [ ] El protocolo define el universo, el marco, los estratos (sector, canal, complejidad), las cuotas prefijadas por canal y sector, los denominadores y las reglas de decision, y el consentimiento; ningun valor se presenta como medido.
- [ ] El script es determinista (dos corridas byte a byte), de solo lectura, sin red ni Gemini, y reproduce el ancla vigente `0,7489` antes de escribir.
- [ ] El script calcula los pesos de Horvitz-Thompson y de post-estratificacion, la exactitud estricta ponderada y el efecto de diseno, con IC bootstrap sobre el universo completo (sin exclusion).
- [ ] La tesis declara el diseno como `condicional` y no afirma que la muestra de 200 sea probabilistica ni que su IC se estime sobre el universo.
- [ ] La seccion nueva del memo no modifica ningun valor de las Secciones 3.1 a 3.37 y registra el efecto de diseno como `condicional`.
- [ ] `openspec validate c-229-muestreo-probabilistico-del-universo-de-incidentes --strict` pasa.
