# Tasks: Atender el dictamen CONEAU sobre v1.2.10

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`. Anclas en el formato
"dictamen `:N` → main `:M`" (el dictamen numera sobre el tag `v1.2.10`; en `main` hay
deriva). Localizar siempre por el texto citado. Numeración compilada: 4.x = `04`, 8.x =
`07`, 9.x = `08`, 10.x = `09`, 11.x = `10`. Línea base: 118 páginas; resumen 245 y
abstract 240 palabras (tope 250). No se edita código ni artefactos de `evaluation/`.

## 1. Verificación del mecanismo de derivación (solo lectura; bloqueante para el grupo 2)

- [x] 1.1 Leer `App/Backend/app/services/incidente_service.py` (`crear_incidente`, VIS-005) y las rutas que resuelven `reportante_empleado_id` por canal (VIS-003/VIS-004): documentar cómo se resuelve el reportante en correo (`reportante_email`, c-162), telefonía (`reportante_telefono`, c-162) y formulario web (hipótesis: sesión autenticada). Confirmar que no hay otra condición que active `requiere_revision_humana` en las etapas determinística y Gemini con confianza ≥ 0,70.
- [x] 1.2 Cruzar `evaluation/data/campana/intervenciones.csv` (147 filas, `origen_intervencion = gate`, 122 `cambio_sector = false` / 25 `true`) con los ocho `sidecar_*.json` (por `case_id`): confirmar 66/66 correo con `revision = true`, 81/81 telefonía con `revision` nulo, 0/53 web con `revision = false`; y con `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (92 determinísticos y 55 Gemini entre los intervenidos). Script descartable en el scratchpad, sin escribir en el repo.
- [x] 1.3 Confirmar que los remitentes `corpus-RXXX@corpus.local` y el número del softphone no figuran en el directorio de empleados del despliegue de la campaña (seed o documentación de `docs/campana-medicion/` y `scripts/corpus_ingest/`).
- [x] 1.4 Fijar con `git log --since 2026-11-05 --until 2026-11-08` y `docs/campana-medicion/guia-ejecucion-campana.md` la revisión o el rango de revisiones de cada tramo (correo/web 5-11 ≈ `cda7712`/`9109a03`; telefonía 6-11 tras c-174/c-175; intervenciones validadas el 7-11) y la imagen de N8N vigente en cada tramo (c-182, `000abeb`, 7-11 18:18 −03). Lo no recuperable se declara "no registrado".
- [x] 1.5 Recomputar el IC de Wilson de 25/200 con la función del análisis (`evaluation/`): esperado [0,086; 0,178].
- [x] 1.6 Registrar la nota de verificación en una sección nueva "Dictamen v10 / v1.2.10 (2026-11-08) - c-187" de `docs/Tesis/Correcciones/dictamen-correcciones.md`. **Si 1.1-1.3 no confirman c-82, detener el apply y consultar al usuario.**

## 2. A1 — Derivación por confianza frente a derivación por reportante; sub-hipótesis 2

- [x] 2.1 `S/07-resultados.tex` dictamen `:157` → main `:159` (8.3, párrafo del gate): conservar "derivación por confianza = 0 casos"; retirar "Sobre el 65,5 % de los casos no existió … derivación" (B2, inventario 7) o rotularlo como cobertura de la etapa determinística.
- [x] 2.2 `S/07-resultados.tex` dictamen `:159` → main `:161` (8.3, sub-hipótesis 2): reescribir con dos lecturas rotuladas (tasa bruta 147/200 [67,0 %; 79,1 %], atribuida a la derivación por reportante no identificado, desglose 66/66 correo, 81/81 telefonía, 0/53 web; intervenciones con cambio de derivación 25/200 = 12,5 % [8,6 %; 17,8 %] → **no concluyente**); precisar que `origen_intervencion = gate` registra el indicador, no la regla de confianza (inventario 8). Revisar el título de `subsec:reduccion-intervencion` (conservar el label).
- [x] 2.3 `S/07-resultados.tex` (8.7, `subsec:resultados-campana-medicion`): una oración que remita al mecanismo de 8.3; sin duplicar cifras.
- [x] 2.4 `S/01-introduccion.tex` dictamen `:32` → main `:34` (1.4): estado de la sub-hipótesis 2 = no concluyente con la medida pertinente (inventario 3).
- [x] 2.5 `S/00-resumen.tex:13` y abstract (inventario 1): reemplazar el paréntesis "(73,5 %, IC [67,0 %, 79,1 %])" por una formulación que nombre la magnitud y no se confunda con la exactitud; estado no concluyente. Compensar palabras (tope 250).
- [x] 2.6 `S/08-discusion.tex:8` (9.1, inventario 14): incluir la sub-hipótesis 2 en el resumen de la hipótesis con su estado; revisar `:16` (lectura de la intervención por gate) para coherencia.
- [x] 2.7 `S/09-conclusiones.tex:19-26` (Tabla 18, inventario 20): fila del objetivo general (main `:22`) sin "medida y refutada"; fila del OE4 (main `:26`) matizada (grado a confirmar con el usuario, design D2); revisar `:6` y `:41` por coherencia.
- [x] 2.8 `S/10-recomendaciones.tex:16-18` (11.3, inventario 23): retirar "descienda respecto del 73,5 %" como defecto del clasificador; proponer medir la variable con reportantes identificados. Revisar `:6`.
- [x] 2.9 `docs/Tesis/Correcciones/numeros-canonicos.md`: entrada nueva 25/200 = 0,125, IC [0,086; 0,178], veredicto no concluyente, y desglose por canal con fuente; tasa bruta intacta.
- [x] 2.10 Verificación: `rg -n "refutad" S/` sin coincidencias referidas a la sub-hipótesis 2; `rg -n "73,5" S/00-resumen.tex S/10-recomendaciones.tex` sin el uso como intervención ambigua; estado idéntico en resumen, abstract, 1.4, 9.1, Tabla 18 y 11.3.

## 3. A2 — Orden efectivamente ejecutado

- [x] 3.1 `S/04-marco-metodologico.tex` dictamen `:12` → main `:14` (4.2) y dictamen `:63` → main `:65` (4.5) (inventario 4): describir el plan `brazo_primero` y lo ejecutado (manual 5-11 09:20-18:49 −03 en los 200 casos; automatizado 5-11 23:47 UTC a 6-11 22:45 UTC; grupos intercalados por `posicion`, sin turno 1 → turno 2 del runbook).
- [x] 3.2 `S/04-marco-metodologico.tex` dictamen `:79` → main `:81` (4.6): el contraste entre grupos `brazo_primero` no estima el efecto de orden; el de posición (Spearman) sí.
- [x] 3.3 `S/04-marco-metodologico.tex` dictamen `:85` → main `:87` (4.7, amenazas): efecto de orden como amenaza no resuelta; retirar "sí aborda el efecto de orden con el contrabalanceo".
- [x] 3.4 `S/07-resultados.tex` dictamen `:256` → main `:258` (8.7, inventario 13): retirar el efecto de condición como evidencia sobre el orden (preferible retirar sus p del cuerpo); conservar Spearman (O1 ρ = −0,0628, p = 0,5147; O2 ρ = −0,3604, p = 0,00011; EMD ρ = 0,2834).
- [x] 3.5 `S/08-discusion.tex:22` (explicaciones rivales): retirar "se abordó con un diseño contrabalanceado"; mantener que el orden manual → automatizado sesga, de hacerlo, en contra de la hipótesis de tiempos.
- [x] 3.6 Verificación: `rg -n "contrabalance" S/` → cada coincidencia describe el plan con la salvedad de lo ejecutado o la amenaza no resuelta.

## 4. A3 — Referencia de verdad y analistas originales

- [x] 4.1 `S/04-marco-metodologico.tex` dictamen `:53` → main `:55` (4.4, inventario 5): reemplazar "ajenos al equipo de autores del trabajo" por la declaración de que uno de los analistas originales (`T1`, `registro_sujetos.csv` y README "Sujetos") es autor y ambos operaron el brazo manual de 2026-10; sin datos personales.
- [x] 4.2 `S/04-marco-metodologico.tex` main `:87` (4.7) y `S/08-discusion.tex:54` (9.4, "Sexto…"): llevar la coincidencia analista-autor como limitación.
- [x] 4.3 `S/08-discusion.tex` (9.4): limitación compacta sobre la fiabilidad de la referencia (kappa 0,5569 [0,4725; 0,6413] con tabla conservada frente a 0,87 sin intervalo ni tabla; consenso `E1 = E2` = referencia original en 116/138, 84,1 %; las métricas primarias heredan esa incertidumbre).
- [x] 4.4 `S/09-conclusiones.tex:51` (10.2, inventario 22): matizar la segunda contribución con el kappa moderado; agregar en el capítulo 10 la conclusión sobre el efecto de posición significativo para `O2` (B6).
- [x] 4.5 `S/00-resumen.tex` y abstract: ambos kappa con su naturaleza (formulación mínima; tope 250).
- [x] 4.6 Verificación: `rg -n "ajenos al equipo de autores" S/` = 0 referido a los analistas originales; `rg -n "0,5569|0{,}5569" S/00-resumen.tex S/08-discusion.tex S/09-conclusiones.tex` ≥ 1 en cada uno.

## 5. A4 — Denominador del brazo manual

- [x] 5.1 `S/07-resultados.tex` dictamen `:254` → main `:256` (8.7, inventario 11): "0,8278 (125 de 151 derivaciones de operador, 80 de `O1` y 71 de `O2`, sobre 138 casos únicos, 13 con doble cobertura; IC bootstrap por caso [0,7647; 0,8882])" y "laxa, de 0,8609 (130 de 151)".
- [x] 5.2 Misma oración: expresar la comparación con el automatizado (110 de 138 casos) declarando la diferencia de unidad y remitiendo al McNemar por operador.
- [x] 5.3 `S/08-discusion.tex:95` (9.6, inventario 17): conservar `e_man` = 0,1722 y `a*` = 68,2/75,5/77,9 %; agregar "por derivación" solo si la oración queda ambigua.
- [x] 5.4 `docs/Tesis/Correcciones/numeros-canonicos.md` dictamen `:768` (sección (a), fila de la agregada): "125/151 derivaciones sobre 138 casos" y "130/151"; nota sobre el rótulo "138" de `analisis/resultados.json` (no se edita el artefacto).
- [x] 5.5 Verificación: `rg -n "125 de 138|130 de 138|125/138|130/138" S/ docs/Tesis/Correcciones/numeros-canonicos.md` = 0.

## 6. A5 — Trazabilidad de la versión entregada

- [x] 6.1 **Decisión del usuario** sobre el patrón de release (design D7: A recomendada, B o C). Registrar la decisión en `dictamen-correcciones.md`.
- [x] 6.2 `S/12-anexos.tex:44-46` (Anexo B, inventario 24), según D7-A: en el commit de contenido, reemplazar la oración del hash por el enunciado de que el hash de `v1.2.11` se consigna en el commit siguiente con el procedimiento de verificación (`git rev-parse v1.2.11^{commit}`; `git diff --stat v1.2.11 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"`). El commit del hash (grupo 9) lo reemplaza por el hash completo.
- [x] 6.3 `S/12-anexos.tex:48-77` (Tabla 19, inventario 25): rótulo de columna "campaña complementaria"; completar las celdas con lo verificado en 1.4 (rango de revisiones, c-82 Sí, c-162 Sí, c-165, `hybrid-v3`, imagen de N8N por fecha); "no registrado" donde no sea recuperable; fila nueva "Imagen de N8N" (evaluada `n8nio/n8n:2.11.2`; entregada imagen derivada `docker/n8n/Dockerfile` + parche IMAP, c-182) y retirar N8N 2.11.2 de "Sin cambios"; "(c-162, posterior a la campaña)" → "posterior a la campaña 2026-10"; nota de fuente sin "la misma configuración evaluada"; párrafo `:48` coherente. Sin agregar altura neta de página (compactar celdas si hace falta).
- [x] 6.4 `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`: registrar los valores nuevos de la Tabla 19 con su comando de verificación (`git log`, `git show v1.2.10:docker/n8n/Dockerfile`, `git show 000abeb`).
- [x] 6.5 `S/06-implementacion.tex` dictamen `:5` → main `:10` (6.1): una oración que declare la imagen derivada de N8N de la configuración entregada (c-182).
- [x] 6.6 `S/00-portada.tex` dictamen `:27` → main `:30` (inventario 2): "30 de octubre de 2026" → fecha de la release `v1.2.11`.
- [x] 6.7 Verificación: `rg -n "misma configuración evaluada" S/12-anexos.tex` sin referencia a la campaña; `rg -n "30 de octubre de 2026" S/00-portada.tex` = 0; `rg -n "c-182" S/06-implementacion.tex S/12-anexos.tex` ≥ 1 en cada uno.

## 7. B1, B3, B6 y B2 — Consistencia de los párrafos tocados

- [x] 7.1 **B1** `S/07-resultados.tex` dictamen `:254` → main `:256` (inventario 12): declarar que 0,7971 (110/138) proviene de `predicciones_in_sample.json` (copia de la evidencia del 7-10), no de la salida en vivo de la campaña (difiere en 13 casos: 7/119 escritos, 6/81 telefónicos); justificar (predicción del clasificador evaluado sobre la que se calculan las métricas primarias) y declarar que el McNemar usa la caché. Acotar "con el clasificador congelado" donde sugiera salida idéntica.
- [x] 7.2 **B3**: "campaña de medición" → "campaña 2026-10" / "campaña complementaria" en las leyendas de las Figuras 3 y 4 (localizar con `rg -n "posterior a la campaña de medición" S/`), el pie de la Tabla 5 (`S/05-arquitectura.tex:78`, inventario 26), el Anexo B y la Tabla 19. Si el rótulo está dentro del PNG, regenerar desde `docs/diagrams/*.md` con el pipeline de `scripts/figures/`; si no, solo `.tex`.
- [x] 7.3 **B6**: `S/09-conclusiones.tex:47` (inventario 21) "técnicamente viable" + "dentro de la muestra"; "5.000 casos" una sola vez: conservar en `S/08-discusion.tex:62` y reemplazar por remisión en `S/10-recomendaciones.tex:14` y `S/12-anexos.tex:196` (inventario 16); `S/08-discusion.tex:56` (inventario 15) calificativo de interpretación de 8.5 en la "cota pesimista"; kappa moderado y efecto de posición en el capítulo 10 y en el resumen (cubierto en 4.4 y 4.5; verificar).
- [x] 7.4 **B2**: `S/07-resultados.tex` dictamen `:6` → main `:8` (inventario 6) "2 y el 6 de octubre" → "del 2 y del 5 y 6 de octubre"; dictamen `:161` → main `:163` (inventario 9) denominador de la proporción de tiempo: tiempos automatizados de los 191 casos de la corrida, incluidos los no intervenidos, más la duración de las intervenciones; dictamen `:250` → main `:252` (inventario 10) retirar "únicamente" y mencionar la proporción de tiempo. (El "65,5 %" de B2 se atiende en 2.1.)
- [x] 7.5 Verificación: `rg -n "2 y el 6 de octubre|únicamente el análisis|posterior a la campaña de medición" S/` = 0; `rg -n "técnicamente viable" S/09-conclusiones.tex` con "dentro de la muestra"; `rg -n "5\.000|5\{\.\}000" S/` = 1.

## 8. Anexo I y registro

- [x] 8.1 `S/12-anexos.tex:200` (`sec:anexo-trazabilidad`): "cinco dictámenes … entre el 20 y el 28 de octubre" → seis, hasta el 8 de noviembre de 2026.
- [x] 8.2 `S/12-anexos.tex`: tercera tabla `tab:anexo-trazabilidad-0811` (estructura común: Rec. | Change | Secciones) con filas A1-A5, B1, B2, B3, B6 (`c-187`, con `\autoref` a las secciones y tablas tocadas) y una fila que remita B4, B5, B7 y C1-C5 a un change posterior; párrafo introductorio de una oración. Sin números de línea.
- [x] 8.3 `docs/Tesis/Correcciones/dictamen-correcciones.md`: completar la sección de c-187 (iniciada en 1.6) con la matriz recomendación → ubicación → corrección (A1-A5, B1, B2, B3, B6), la decisión de D7 y la remisión de B4, B5, B7 y C1-C5.

## 9. Compilación y release

- [x] 9.1 (Docker no disponible; recompilación diferida al orquestador) Recompilar (`latexmk -xelatex main.tex` en `docs/Tesis/v10 (IA)/paper/`): 0 errores fatales, 0 referencias o citas indefinidas; `verify_citations.py` PASS. [Compilado con Docker (texlive-thesis, latexmk): 0 errores fatales, 0 undefined, 0 multiply defined, 0 WARN/ERROR en main.blg, 0 Overfull > 10 pt, 0 "??" en el PDF; 121 paginas.]
- [x] 9.2 Contar páginas (≤ 118; ninguna página neta agregada) y palabras (resumen y abstract ≤ 250; párrafo de viabilidad ≤ 34) con el procedimiento de c-169; registrar en `dictamen-correcciones.md`. [HECHO: 118 páginas (`abspage@last` = 118; referencias en la 102, anexos en la 106) tras recortar prosa y compactar tablas desde 121; resumen 237 y abstract 237 palabras por la regla de c-106 (248-251 con todos los tokens de `pdftotext`); 0 errores, 0 `undefined`, 0 `multiply defined`, `.blg` limpio, 0 `??`; párrafo de viabilidad sin cambios.]
- [x] 9.3 `openspec validate c-187-atender-el-dictamen-coneau-v1-2-10 --strict --no-interactive`.
- [x] 9.4 (Orquestador) Rama nueva, commit de contenido de la release y tag anotado `v1.2.11` sobre ese commit. [HECHO: tag anotado `v1.2.11` sobre el commit `a42f005078a1a7f1d4eea8bd11a7757335f2ce58` en la rama `change/c-187-dictamen-coneau-v1-2-10`, 2026-11-08.]
- [ ] 9.5 (Orquestador) Commit del hash según D7 (patrón `c3c63c8` → `2103292`): consignar el hash completo de `v1.2.11` en el Anexo B, recompilar, registrar en `dictamen-correcciones.md` y `CHANGES.md`; verificar con `git diff --stat v1.2.11 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` que solo cambia esa línea. [En curso por el orquestador.]
- [ ] 9.6 (Orquestador) `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"`, commit de `.engram/` y PR (nunca push directo a `main`); push del tag con confirmación del usuario. [En curso por el orquestador.]
