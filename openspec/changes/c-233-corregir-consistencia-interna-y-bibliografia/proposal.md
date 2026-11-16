# Proposal: Corregir la consistencia interna y la bibliografia de la tesis v1.5.0

## Why

La auditoria interna en estilo CONEAU sobre la tesis **v1.5.0** (commit `5cd0011`, tag `v1.5.0`) devolvio **APROBADO CON OBSERVACIONES**, con la recomendacion expresa de resolver las **inconsistencias internas** antes de la defensa oral (`docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md`, secciones 3 y 5). El dictamen detecto **10 inconsistencias internas** entre resumen, introduccion y los capitulos de resultados/discusion, **3 anomalias bibliograficas** menores y metadatos medidos sobre una revision (`v1.2.18`) distinta de la configuracion evaluada (`bf5e099`). Ninguna observacion compromete la aprobacion, pero varias deben corregirse antes de la defensa. Este change es de **redaccion, etiquetas, procedencia y bibliografia**; no introduce datos nuevos ni mediciones nuevas (salvo las cifras de cobertura re-ancladas de B4, declaradas y canalizadas por el memo).

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Bibliografia** | `Powers2011_evaluation`: `note` que aclara que la URL arXiv es un espejo posterior del articulo de 2011 (ano sin cambio). `ramonferrer2026tripletotext`: campo `publisher` (IOS Press) sin tocar el DOI que resuelve. `AAIP2023_resolucion198`: URL oficial (Boletin Oficial / AAIP). | MEDIA |
| **B. Consistencia interna** | Resumen con el calificador del cuerpo (B1); introduccion que DISTINGUE la tasa a priori del 15 % del brazo manual medido (`e_man = 26/151`, B2); mencion out-of-sample en la introduccion (B3); cobertura/pruebas re-ancladas a la configuracion evaluada (B4); desambiguacion de etiquetas `v1.2.2`/`v1.3.0` (B5); cadenas de sector canonicas sin tildes donde el texto cita el sistema (B6); signos `¿` (B7); rotulo "exactitud estricta del brazo manual" (B8); novena limitacion rotulada como superada (B9); "mapa de lectura" al final de la introduccion (B10). | MEDIA |
| **C. Cierre** | Recompilar el PDF y actualizar `compilacion.md` (C1); memo seccion aditiva `3.43` (C2); filas de trazabilidad en `dictamen-correcciones.md` (C3); entrada en `CHANGES.md` (C4); bump a **v1.5.1** (C5); tag anotado `v1.5.1` + commit posterior con el hash (C6); commit del archivo de auditoria sin trackear (C7). | **ALTA** (tag) + MEDIA |

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se AGREGAN requisitos de consistencia interna, procedencia bibliografica (localizador, ano y editor), nomenclatura canonica, tipografia, limitaciones y cierre de version; y se MODIFICA el anclaje de las cifras de cobertura/pruebas a la configuracion evaluada.
- `tesis-numeros-canonicos`: se AGREGA el registro aditivo de las cifras de cobertura y pruebas re-ancladas a la configuracion evaluada (`bf5e099` y `v1.3.0`) en una seccion nueva (`3.43`), sin renumerar ni alterar las anteriores.

No se crea una capability nueva de bibliografia: las reglas de citas y entradas ya viven en `tesis-document` (`Citation rendering`, `Bibliographic reference quality`, `Reference authenticity`); las tres anomalias son correcciones de forma de las entradas y se pliegan alli.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/Bibliography_base.bib` | Modificado | `note` en `Powers2011_evaluation`; `publisher` en `ramonferrer2026tripletotext`; `url` en `AAIP2023_resolucion198`; version en `Gomez2026_repositorio` |
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex`, `01-introduccion.tex`, `04-marco-metodologico.tex`, `05-arquitectura.tex`, `06-implementacion.tex`, `07-resultados.tex`, `08-discusion.tex`, `11-aspectos-legales.tex` | Modificado | Correcciones B1 a B10; bump de version en `00-portada.tex` y `12-anexos.tex` |
| `docs/Tesis/v10 (IA)/paper/compilacion.md`, `main.pdf` | Modificado | Recompilacion de cierre (C1) |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion `3.43` (cifras de cobertura/pruebas) sin renumerar |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Filas de trazabilidad (patron c-231) |
| `docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md` | Nuevo (trackear) | Commitea el archivo hoy sin trackear (C7) |
| `CHANGES.md` | Aditivo | Entrada C-233 |
| Tag git | Nuevo | Tag anotado `v1.5.1` (CHECKPOINT de autorizacion) |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuracion, el corpus ni las predicciones. Cero llamadas a Gemini. Ningun valor canonico cambia de valor, salvo las cifras de cobertura/pruebas de B4, declaradas y canalizadas por el memo.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Cambiar por descuido el valor de un numero canonico | Media | Revision dirigida por `git diff`; solo cambian palabras, rotulos y procedencia |
| Las cifras de cobertura de B4 no se reproducen por deriva de dependencias | Media | Entorno pinneado por revision, registro del entorno; si no se reproduce, se declara y se conservan las cifras vigentes con nota |
| Crecimiento de paginas por el mapa de lectura | Baja | Parrafo acotado; verificar `\@abspage@last` contra la linea base de 159 pp |
| Cortar el tag `v1.5.1` sin autorizacion | Baja | CHECKPOINT humano explicito antes del tag |
| Duplicar o desplazar la numeracion del memo | Baja | Seccion `3.43` aditiva; no se renumeran `3.38`-`3.42` |
| Confirmar por error una afirmacion de la introduccion | Media | B2 separa explicitamente la tasa a priori (no re-medida) de la medicion del brazo manual |

## Rollback Plan

`git revert` del commit de contenido (C1 anterior al tag): las ediciones de prosa, bibliografia y memo son textuales y aditivas; el PDF y `compilacion.md` se regeneran desde la fuente previa; el memo `3.43` y las filas de trazabilidad se retiran sin tocar las secciones anteriores; el tag `v1.5.1` se elimina (`git tag -d` y borrado del remoto si ya se publico) y se repunta la version a `v1.5.0`. Ningun valor canonico previo se modifica, de modo que el rollback no deja huecos numericos.

## Dependencies

- Ninguna dependencia dura. Este change es **independiente** de `c-228`, `c-229`, `c-230`, `c-231` y `c-232`: no los bloquea y ninguno lo bloquea. Si alguno de esos changes se aplicara despues, podria necesitar repuntar lineas de la prosa tocada aqui.

## Success Criteria

- [ ] Las tres entradas bibliograficas (A1, A2, A3) quedan corregidas sin alterar el ano de `Powers2011_evaluation` ni el DOI de `ramonferrer2026tripletotext`; `verify_citations.py` sigue en PASS.
- [ ] Las diez inconsistencias internas (B1 a B10) quedan resueltas y verificables con la busqueda textual indicada en cada tarea.
- [ ] Las cifras de cobertura/pruebas de `06-implementacion.tex` quedan ancladas a la configuracion evaluada `bf5e099` (y, si difiere, tambien a `v1.3.0`), con el cambio declarado en el memo `3.43` si algun valor cambia.
- [ ] El PDF recompila sin errores fatales, con 0 referencias/citas indefinidas y 0 etiquetas duplicadas; `compilacion.md` registra el nuevo conteo de paginas.
- [ ] La version queda en `v1.5.1` (portada, Anexo B y `.bib`) y el tag anotado `v1.5.1` se corta solo con autorizacion expresa, con el hash consignado en un commit posterior.
- [ ] `openspec validate c-233-corregir-consistencia-interna-y-bibliografia --strict` pasa.
