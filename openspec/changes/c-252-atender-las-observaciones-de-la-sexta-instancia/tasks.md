# Tasks: Atender las observaciones de la sexta instancia del tribunal

> Orden por dependencia. Las cuatro compuertas OQ-01 a OQ-04 quedaron RESUELTAS por los autores el
> 2026-11-26; el apply CODIFICA cada decisión (no la pregunta). Solo el **visto bueno escrito del director**
> (grupo 11) bloquea la release. Rutas `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` =
> `docs/Tesis/Correcciones/`.

## 1. Registro de la sexta instancia y compuertas

- [x] 1.1 Versionar la transcripción `.md` de la sexta instancia en `auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md` con `pdftotext -layout` del PDF y el bloque de metadatos (versión 1.6.5, emisión 26/11/2026, calificación 7,5/10, condición: D-01 a D-03 en la versión de defensa + visto bueno del director). Verificar: el archivo existe y su bloque de metadatos repite el formato de la quinta instancia.
- [x] 1.2 Registrar en `C/dictamen-correcciones.md` la sección c-252 con las cuatro compuertas **RESUELTAS** (OQ-01 a OQ-04) y la tabla de decisiones cerradas (respuesta literal, fecha 2026-11-26, responsable). Verificar: `rg -n "OQ-0[1-4] .* RESUELTA" docs/Tesis/Correcciones/dictamen-correcciones.md` devuelve 4 coincidencias.
- [x] 1.3 Consignar en la sección c-252 las respuestas ya recibidas de los autores (OQ-01 a OQ-04) con fecha y responsable. Verificar: cada OQ figura RESUELTA con su respuesta literal (nunca se sumó; ámbito laboral disociado; automatizado primero; juntos en un domicilio).

## 2. Script de análisis D-04 (extensión de descripciones) — TDD

- [x] 2.1 Escribir `evaluation/data/campana/analisis/test_analisis_sexta_instancia_c252.py` primero (Strict TDD) con casos sintéticos: extensión media en palabras y caracteres por canal y por régimen, agrupación (a)=correo+formulario / (b)=telefonía, y escritura determinista. Verificar: `pytest .../test_analisis_sexta_instancia_c252.py` falla solo por `ModuleNotFoundError` del módulo aún inexistente.
- [x] 2.2 Implementar `analisis_sexta_instancia_c252.py`: lee `data/corpus_evaluacion_pseudonimizado.json` (campo `descripcion`), agrupa por `canal_origen`, computa media de palabras/caracteres por canal y régimen, y escribe `.json`, `.md` y `SHA256SUMS.txt` deterministas. Verificar: `pytest` verde y `sha256sum data/corpus_evaluacion_pseudonimizado.json` sin cambios.
- [x] 2.3 Escribir en §4.4 y §4.8 (`S/04-marco-metodologico.tex`) la extensión media por canal/régimen citada de la salida versionada, y separar la parte de lectura de la de decisión en los 87,2 s manuales. Verificar: las cifras de la prosa coinciden con `analisis_sexta_instancia_c252.json`.

## 3. D-05 — propagación y trazabilidad (no gated)

- [x] 3.1 Resumen, Abstract (`S/00-resumen.tex`) y Tabla 10 (`S/07-resultados.tex`): decir que el brazo manual midió solo la clasificación (no el registro) e informar el 63,3 % sin telefonía (44,1 → 16,2 s). Verificar: `rg -n "63,3|solo la clasificaci"` en `S/00-resumen.tex` y en la Tabla 10.
- [x] 3.2 Anexo I.1 (`S/12-anexos.tex:239-247`): registrar el cambio de fechas (junio–agosto → octubre 2026) y el del componente de carga con el criterio de los retiros anteriores. Verificar: `rg -n "carga|octubre"` en el bloque de la Nota de versiones muestra ambos registros.
- [x] 3.3 Anexo I.2 (`S/12-anexos.tex:251`): sumar la devolución de quinta instancia (25/11/2026) y la de sexta instancia (26/11/2026). Verificar: `rg -n "quinta instancia|sexta instancia|2026-11-25|2026-11-26"` en `S/12-anexos.tex`.

## 4. D-02 — definición del tiempo manual (RESUELTA — nunca se sumó, 71,2 %)

- [x] 4.1 Registrar en el Anexo I.1 que la descripción correcta es "clasificación pura sin carga" y que la v1.6.4 estaba mal descrita (OQ-02 RESUELTA: nunca se sumó). Verificar: `rg -n "componente de carga|10 s"` en el bloque de la Nota de versiones.
- [x] 4.2 Reemplazar "retirado el componente de carga" (`S/04-marco-metodologico.tex:127`) y "componente que la presente versión ya no contempla" (`S/12-anexos.tex:354`) por redacción que no sugiera cambio de valores. Verificar: `rg -n "retirado el componente de carga|ya no contempla" S/` = 0 coincidencias.
- [x] 4.3 Homogeneizar la descripción en Tabla 3 (`tab:variables`, `04:31`), octava amenaza (`04:131`), §8.1 (`07:38`) y `07:285`. Verificar: `rg -n "componente de carga" S/` no devuelve descripciones contradictorias.
- [x] 4.4 Fijar en `C/numeros-canonicos.md` la cifra primaria de la sub-hipótesis 1 en **71,2 %** (no 65,6 %) y la etiqueta única del `-10 s` como "escenario C-02" (resuelve la contradicción c-250 "redondeo" vs c-251 "carga"). Verificar: `rg -n "10 s|redondeo|carga"` en el bloque de sensibilidad del memo canónico muestra una sola etiqueta coherente con OQ-02.

## 5. D-01 — cronología de la campaña manual (RESUELTA — automatizado primero)

- [x] 5.1 Declarar la cronología día por día en §4.2 (`04:14`) y §4.4 (`04:46`): 01/10 notificación; 01–02/10 recolección + redacción disociada (simultáneas); 02/10 corrida automatizada (119); 05–06/10 telefonía; 06–09/10 doble etiquetado con consenso; 09/10 cronometraje manual por pares (A1/T1, posterior al etiquetado); 09/10 versionado (commit `ea62576`). Declarar la fecha del cronometraje como declaración de los autores acotada por el commit `ea62576`. Verificar: `rg -n "ea62576|09/10|cronometraje"` en `S/04-marco-metodologico.tex`.
- [x] 5.2 Propagar la cota del 09/10 a la Tabla 4 (`tab:procedencia-numeros`, `04:71`) y a la Figura 11 (`fig:cronograma`, `S/12-anexos.tex:53`), sin extender la barra manual a todo octubre. Verificar: lectura del caption de la Figura 11 y de la Tabla 4.
- [x] 5.3 Citar los commits `68d06ec` (sintético) y `ea62576` (real) como evidencia fechada, e incorporar en la Nota de versiones que los 165,3 s del 3 de julio provenían del corpus sintético (simulado) y no de una medición real del corpus vigente. Verificar: `rg -n "68d06ec|165,3"` en `S/12-anexos.tex`.
- [x] 5.4 OQ-01 RESUELTA (automatizado primero, cronometraje 09/10 posterior al etiquetado): corregir §4.2 (`S/04-marco-metodologico.tex:14`), §4.8 primera amenaza (`04:117`) y §9.1 tercera explicación rival (`S/08-discusion.tex:22`) para decir "primero el automatizado (02/10), luego el manual (09/10, posterior al etiquetado)" y declarar la DIRECCIÓN del sesgo como conservadora (manual sub-estimado → reducción cota inferior). Verificar: `rg -n "precedi|manual antes que automatizado|cronometraje manual"` en los pasajes, coherente con la respuesta OQ-01.

## 6. D-03 — origen del régimen (a) y legal (RESUELTA — ámbito laboral, disociado; HIGH)

- [x] 6.1 Declarar si los incidentes del régimen (a) ocurrieron en el ámbito laboral de los reportantes, en una única formulación en §4.4 (`04:46`). Verificar: el pasaje de procedencia lo declara una sola vez y con claridad.
- [x] 6.2 OQ-03 RESUELTA (ámbito laboral): citar el deber de confidencialidad del art. 10 (Ley 25.326) junto a la tríada CIA en `S/11-aspectos-legales.tex`, explicar el léxico corporativo (§7.2 `11:18`, caso R015 `07:277`) y corregir `11:18` (deja de negar "información de sistemas ajenos"). Verificar: `rg -n "art.*10|confidencialidad"` en `S/11-aspectos-legales.tex`.
- [x] 6.3 Retirar o explicar "del sector servicios y con sede en la provincia de Mendoza" de §1.2 (`S/01-introduccion.tex:16`), las conclusiones (`S/09-conclusiones.tex:52`) y la limitación (`01:76`). Verificar: `rg -n "del sector servicios y con sede en la provincia de Mendoza" S/` no devuelve una mención sin aclaración.
- [x] 6.4 Registrar el cambio de origen del régimen (a) en el Anexo I.1 (`S/12-anexos.tex:239-247`). Verificar: `rg -n "origen|c.rculo|r.gimen"` en la Nota de versiones.
- [ ] 6.5 Gestionar y registrar el visto bueno escrito del director sobre la procedencia declarada (condición del tribunal, HIGH). Verificar: queda constancia del aval escrito y de su fecha antes de la release.

## 7. D-06 — coherencia y redacción (RESUELTA — juntos, domicilio único)

- [x] 7.1 Aclarar que A1 y T1 cronometraron "por pares" juntos, en un único domicilio (`S/04-marco-metodologico.tex:16`), según OQ-04. Verificar: el pasaje no deja contradicción interna entre "por pares" y el domicilio.
- [x] 7.2 Unificar la atribución de las 81 reconstrucciones ("redactadas por los autores" Anexo F `S/12-anexos.tex:149` vs "por uno de los autores" `04:129`, `09:54`, `06:54`, `12:241`) a una sola forma, según OQ-04. Verificar: `rg -n "redactadas por (los autores|uno de los autores)" S/` muestra una única forma.
- [x] 7.3 En §8.1 (`S/07-resultados.tex:38`) reemplazar "respaldados por" por la fórmula de §4.5 (`04:66`, `:79`). Verificar: `rg -n "respaldados por" S/07-resultados.tex` = 0.
- [x] 7.4 En §7.5 (`S/11-aspectos-legales.tex:46`) corregir "titulares… distintos de los autores" (los autores también son reportantes) y reemplazar "registro histórico/retirado" (`S/12-anexos.tex:247`) por una forma sin barra. Verificar: `rg -n "distintos de los autores|hist.rico/retirado" S/` = 0.

## 8. Coherencia y verificación final

- [x] 8.1 Barrido de residuos de las fórmulas retiradas y de las dos etiquetas del `-10 s`; `openspec validate --strict`. Verificar: `openspec validate --strict` PASS y los `rg` de residuos no devuelven coincidencias.
- [x] 8.2 Revisar coherencia de cifras: las globales y por canal quedan intactas (OQ-02: nunca se sumó, 71,2 % se mantiene); `sha256sum` del corpus sin cambios. Verificar: hashes del corpus idénticos a la línea base.

## 9. Respuestas de defensa (sección 6 de la devolución)

- [x] 9.1 Redactar `C/respuestas-tribunal-sexta-instancia.md` con las 10 preguntas probables del tribunal, verificables contra artefactos versionados, y actualizar `docs/defensa/respuestas-tribunal.md`. Verificar: las 10 preguntas quedan respondidas con su fuente; `openspec validate --strict` sigue PASS.

## 10. Release v1.6.6 — versión de defensa (HIGH, BLOQUEADA por aval del director)

- [ ] 10.1 Bump `v1.6.5` → `v1.6.6` en portada, Anexo B (`sec:anexo-repositorio`), Nota de versiones, `Bibliography_base.bib` (`Gomez2026_repositorio`), `README.md`, `knowledge-base/` y `C/inventario-uso-asistentes-ia.md`. Verificar: `rg -n "1\.6\.6"` en portada y Anexo B; sin menciones vigentes a `1.6.5` fuera de históricas.
- [ ] 10.2 Recompilar, regenerar derivados y consignar el hash del commit en `docs/Tesis/v10 (IA)/paper/compilacion.md`. Verificar: compilación sin errores fatales y `git rev-parse HEAD` consignado.
- [ ] 10.3 Publicar el tag anotado `v1.6.6` SOLO tras D-01..D-03 aplicados y el visto bueno escrito del director, y registrar en `dictamen-correcciones.md`, `CHANGES.md` y las respuestas de defensa. Verificar: `git rev-parse v1.6.6^{commit}` existe y coincide con el hash del Anexo B; los tags anteriores intactos.