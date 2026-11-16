# Proposal: Recomponer el relato del corpus y reforzar la validez externa

## Why

La auditoria interna en estilo CONEAU sobre la tesis **v1.5.0** (`docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md`) devolvio **APROBADO CON OBSERVACIONES** y, en su seccion 4 "Fondo (no bloqueantes)", dejo **dos** recomendaciones sin cerrar. El change **c-233** ya cerro las recomendaciones 1 a 6 y 9; quedan pendientes:

- **Recomendacion 7**: recomponer el relato de un unico corpus congelado (que numero proviene de que configuracion).
- **Recomendacion 8**: reforzar la validez externa en la conclusion (sesgo de seleccion).

La auditoria funda ambas en la seccion 2.6 ("Configuracion efectiva no unica: tiempos de `hybrid-v1` frente a metricas de `hybrid-v3`"; "Universo proyectado, no medido: 2.646 = 42 x 63; muestreo no probabilistico por conveniencia") y en la seccion 5: mientras subsistan esos residuos, el veredicto no puede elevarse a "aprobado sin observaciones". Este change es de **prosa y procedencia**: no mide de nuevo, no introduce datos y no cambia el valor de ningun numero canonico.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Relato del corpus unico congelado (rec 7)** | Prosa de procedencia que hace explicito que hay **un solo corpus congelado** y **varias configuraciones/corridas**: `04-marco-metodologico.tex` (datos del brazo automatizado y procedencia por cifra), `07-resultados.tex` y `08-discusion.tex` (que cifra proviene de que corrida), y el Anexo B (`tab:configuracion-evaluada-entregada`) o el anexo de trazabilidad con el mapeo. Cuando un pasaje sugiera una configuracion unica donde hubo varias, se distingue. Solo palabras y remisiones: ningun valor canonico cambia. | MEDIA |
| **B. Validez externa en la conclusion (rec 8)** | `09-conclusiones.tex` (y `10-recomendaciones.tex` si ayuda) declaran la amenaza con la fuerza correcta: muestra **no probabilistica por conveniencia** (los 200 cronometrados), **una sola organizacion** (servicios, Mendoza) y **universo proyectado, no medido** (`2.646 = 42 x 63`); las cifras valen para este corpus y no se extrapolan. Se senala el **diseno de muestreo probabilistico (c-229)** como remedio empirico, declarado **condicional y no ejecutado**. | MEDIA |
| **C. Cierre** | Recompilar el PDF (imagen `texlive-thesis`) y regenerar `compilacion.md`; memo seccion aditiva (primer libre, esperado `3.44`); filas de trazabilidad y fila del libro mayor de paginas en `dictamen-correcciones.md`; entrada en `CHANGES.md`. **Sin bump de version ni tag salvo pedido explicito de los autores.** | MEDIA |

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se AGREGAN dos requisitos: (i) el relato de procedencia de un unico corpus congelado (que cifra proviene de que configuracion/corrida) y (ii) la declaracion de la validez externa en las conclusiones con su remedio empirico (c-229), ambos sin alterar ningun valor canonico.
- `tesis-numeros-canonicos`: se AGREGA el registro aditivo del mapeo de procedencia del corpus unico y de la declaracion de validez externa en una seccion nueva (esperado `3.44`), sin renumerar ni alterar valores ni estados previos.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex`, `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex` | Modificado | Prosa de procedencia (rec 7) y de validez externa (rec 8) |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado | Mapeo de procedencia en el Anexo B o el anexo de trazabilidad |
| `docs/Tesis/v10 (IA)/paper/main.pdf`, `compilacion.md` | Modificado | Recompilacion de cierre |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion nueva (esperado `3.44`), sin renumerar |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Filas de trazabilidad (patron C28) y fila `+c-234` del libro mayor de paginas (G0) |
| `CHANGES.md` | Aditivo | Entrada C-234 |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuracion, el corpus, las predicciones ni los artefactos congelados. Ningun valor canonico cambia de valor. Cero llamadas a Gemini. Este change es **independiente** de `c-228`..`c-232` y **no duplica `c-229`**: `c-229` entrega el diseno empirico (datos nuevos); `c-234` solo declara el estado actual y senala ese remedio.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Cambiar por descuido el valor de un numero canonico | Media | Principio "cambia la forma, no el valor"; `git diff` dirigido sobre los `.tex`; solo cambian palabras y remisiones |
| Duplicar o solapar con `c-229` (diseno probabilistico) | Media | `c-234` es prosa de estado actual y remision; el diseno y sus datos nuevos quedan en `c-229` (declarado condicional) |
| Desplazar la numeracion del memo | Baja | Seccion aditiva en el primer numero libre (esperado `3.44`); no se renumeran `3.38`-`3.43` |
| Crecimiento del PDF por la prosa nueva | Media | Parrafos acotados; verificar `\@abspage@last` contra la linea base de 161 pp y registrar el delta |
| Si `c-229` se aplica antes, la prosa compartida queda desfasada | Baja | Se declaran independientes; al aplicar el segundo, repuntar lineas de la prosa tocada por el primero |

## Rollback Plan

`git revert` del commit de contenido: las ediciones de prosa, el memo `3.44`, las filas de trazabilidad y la fila del libro mayor son **aditivos o sustituciones textuales**; el PDF y `compilacion.md` se regeneran desde la fuente previa. Ningun valor canonico previo se modifica, de modo que el rollback no deja huecos numericos. No hay tag ni bump que deshacer por defecto.

## Dependencies

- Ninguna dependencia dura. **Independiente** de `c-228`, `c-229`, `c-230`, `c-231` y `c-232`: no los bloquea y ninguno lo bloquea. `c-229` (diseno probabilistico) es el **remedio empirico** que este change **referencia**, no ejecuta ni duplica.

## Success Criteria

- [ ] El documento declara que la evidencia se apoya en un **unico corpus congelado** y hace explicito que cifra proviene de que configuracion/corrida (`hybrid-v1` en los tiempos; `hybrid-v3` en las metricas; `bf5e099` evaluada frente a `v1.3.0` entregada; campana complementaria), sin cambiar ningun valor canonico.
- [ ] Las conclusiones declaran la validez externa con la fuerza correcta (muestra no probabilistica por conveniencia, organizacion unica, universo proyectado `2.646 = 42 x 63`) y senalan `c-229` como remedio empirico condicional y no ejecutado.
- [ ] El memo incorpora una seccion aditiva (primer libre; esperado `3.44`) con el mapeo de procedencia y la declaracion de validez externa, sin renumerar ni alterar valores previos.
- [ ] El PDF recompila sin errores fatales, con 0 referencias/citas indefinidas y 0 etiquetas duplicadas; `compilacion.md` registra el nuevo conteo de paginas y el SHA-256.
- [ ] `openspec validate c-234-recomponer-el-relato-del-corpus-y-reforzar-la-validez-externa --strict` pasa.
