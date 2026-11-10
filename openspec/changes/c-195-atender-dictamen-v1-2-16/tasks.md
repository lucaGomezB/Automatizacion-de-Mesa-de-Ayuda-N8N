# Tasks: Atender el dictamen CONEAU sobre v1.2.16

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`E/` = `evaluation/`. "A1", "B2", "item N" remiten al dictamen
`auditorias/Dictamen_Tesis_v10_v1.2.16_CONEAU_2026-11-09.md`. Las anclas se localizan por el texto
citado (`rg -n`); las lineas del design son orientativas. Linea base: 118 paginas; resumen y
abstract <= 250 palabras y sin cambios. No se toca `App/`, `n8n/`, `docker/` ni
`openspec/changes/c-191-validacion-fuera-de-muestra-150-casos/`. Prosa del registro: "seccion N
(`archivo.tex`)" (gitleaks). Release `v1.2.17`. Rama: `change/c-195-atender-dictamen-v1-2-16`
(no cambiar de rama; los commits y el push los hace el orquestador).

**Skills que el apply debe cargar** (`.agents/SKILLS.md`): `python-testing-patterns` (preferida
para escribir las pruebas de `E/` y de `C/`), `python-testing` (marco TDD general, opcional) y
`python-design-patterns` (solo si el refactor de D4/D5 lo requiere). Strict TDD activo para los
grupos 2 y 6. No aplican `sqlalchemy-postgres` ni `tailwind-design-system`.

Gobernanza: grupo 1 diferido a los autores (HIGH); grupo 2 MEDIUM
(codigo de evaluacion); grupos 3-5 y 7 MEDIUM (texto de la tesis).

## 0. Preparacion y verificacion (solo lectura; bloqueante)

- [x] 0.1 `git fetch` y confirmar rama `change/c-195-atender-dictamen-v1-2-16`, que `auditorias/Dictamen_Tesis_v10_v1.2.16_CONEAU_2026-11-09.md` esta versionado y que `origin/main` no trae changes nuevos que choquen con la numeracion (c-191 sigue siendo de otro autor).
- [x] 0.2 Safety net del documento: compilar la linea base en Docker (`export MSYS_NO_PATHCONV=1; docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`, en segundo plano) y anotar paginas, `Overfull` (cantidad y maximo) y `verify_citations.py`; `python -I C/verificar_matriz_trazabilidad.py` -> 171 filas, 0 fallas; `cd C/ && python -m unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.
- [x] 0.3 Script descartable en el scratchpad (design D0): Wilson 25/147 = [0,1179; 0,2390]; binomial P(X >= 25 | 147; 0,15) ≈ 0,28; MDE con 0,864 / 9/pi^2 / sin ARE = 0,2834 / 0,2763 / 0,2644; `git show HEAD:evaluation/data/campana/predicciones_in_sample.json | sha256sum` igual al de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` y JSON parseado igual con 200 predicciones; Wilson del ejemplo de 11.3 (p = 0,10: n = 150 -> 0,158; n = 200 -> 0,149); `ls auditorias/Dictamen_*.md | wc -l` = 9. **Si una cifra no se reproduce, detener esa recomendacion y consultar.**
- [x] 0.4 Listar con `rg -n "v1\.2\.16" S/` las 13 menciones (12 lineas) y clasificarlas en "version entregada" (pasan a `v1.2.17`) e "historicas" (se conservan).

## 1. Consentimiento veraz (A1, items 1-2; gobernanza HIGH) — DIFERIDO A LOS AUTORES

Decision posterior a la propuesta: la redacta Luca Gomez con las firmas, fuera de c-195. No se
editan `S/11-aspectos-legales.tex`, la plantilla ni `evaluation/data/campana/README.md`.

- [~] 1.1 DIFERIDA (no hecha): checkpoint de los autores; sustituido por la decision de diferir.
- [~] 1.2 DIFERIDA (no hecha): 7.5 la reescribe Luca Gomez con las firmas y fechas reales.
- [~] 1.3 DIFERIDA (no hecha): plantilla de confirmacion.
- [~] 1.4 DIFERIDA (no hecha): registro del README de la campana.
- [~] 1.5 DIFERIDA (no hecha): verificacion de 7.5, plantilla y README. En cambio: A1 e items 1-2 constan como PENDIENTE (diferida) en el registro y en el Anexo I.

## 2. MDE del Spearman alineado con el analisis (B1, item 7; Strict TDD)

- [x] 2.1 Safety net: en el venv 3.13 (`%TEMP%\v313`), desde `E/`, con las variables dummy del CI (`.github/workflows`), correr `tests/test_stats.py` y `tests/test_campana.py`; registrar "N pasan". Si alguna falla, detener y reportar como falla previa.
- [x] 2.2 RED: en `E/tests/test_stats.py`, pruebas de `ARE_SPEARMAN` (≈ 0,9119 contra el literal) y de `tanh(efecto_minimo_detectable(107, eficiencia_relativa=ARE_SPEARMAN))` ≈ 0,2763; en `E/tests/test_campana.py` (~linea 1632) el esperado del MDE del Spearman pasa a `ARE_SPEARMAN`. Ejecutar: deben fallar (la constante no existe).
- [x] 2.3 GREEN: `ARE_SPEARMAN = 9 / math.pi ** 2` en `E/stats.py` junto a `ARE_WILCOXON_MINIMA`, con comentario de su origen; importarla en `E/campana.py` y usarla solo en el MDE del Spearman (~linea 1593). Las lineas ~1173 y ~1230 conservan `ARE_WILCOXON_MINIMA`. Ejecutar: pasan.
- [x] 2.4 TRIANGULATE: segundo caso del MDE del Spearman con otro `n` de la fixture (por ejemplo el bloque de O2) y confirmar que las pruebas de Mann-Whitney/Wilcoxon (~1459, ~1549) siguen en verde sin cambios. REFACTOR si corresponde, re-ejecutando tras cada paso.
- [x] 2.5 Regenerar `E/data/campana/analisis/{resultados.json,resultados.md,SHA256SUMS.txt}` con el comando de referencia del README de `analisis/` (sin red ni Gemini), despues de comprobar que las entradas coinciden con `SHA256SUMS.txt`.
- [x] 2.6 Criterio de D5 (script en el scratchpad): comparar hoja por hoja con `git show HEAD:` -> solo cambian las dos rutas `...posicion.spearman.mde` (≈ 0,2763); en `resultados.md` solo las lineas con esos valores; en `SHA256SUMS.txt` solo las filas de `resultados.json` y `resultados.md`. Registrar el resultado.
- [x] 2.7 Si 2.6 falla o 2.5 no corre offline: camino alternativo (D5): `git restore` de codigo, pruebas y salidas, y agregar en 8.7 (`S/07-resultados.tex`, ~linea 253) la oracion de recalculo fuera del analisis (0,2834 en el analisis versionado). Registrar el motivo.
- [x] 2.8 `C/numeros-canonicos.md`: fila del MDE (~851) y seccion (c) (~928-937) con 0,276 y su procedencia segun el camino tomado; huellas SHA-256 de `resultados.json` y `resultados.md` (~742-743) si se regenero.
- [x] 2.9 Verificacion: suite completa de `E/tests` en verde con las variables dummy (desde `E/`); `rg -n "ARE_WILCOXON_MINIMA" E/campana.py` muestra solo los usos de Mann-Whitney/Wilcoxon.

## 3. Segunda sub-hipotesis (A2, items 3-5)

- [x] 3.1 `S/07-resultados.tex` (8.3, ~linea 154): reemplazar "Medirla en condiciones válidas exige una corrida con reportantes identificados" por la condicion de generalizacion de D2, con la misma remision.
- [x] 3.2 `S/07-resultados.tex` (8.3) y `S/08-discusion.tex` (9.1, ~linea 8): "no se puede descartar un valor cercano al umbral" -> "el intervalo no permite descartar una proporción inferior a la cota" (con "su límite inferior es 11,8~\%" en 8.3).
- [x] 3.3 `S/01-introduccion.tex` (1.4, ~linea 34) y `S/04-marco-metodologico.tex` (4.7, ~linea 81): agregar la declaracion de asimetria de D2 tras la definicion de la regla de tres vias.
- [x] 3.4 Verificacion: `rg -n "condiciones válidas|valor cercano al umbral" S/` = 0; `rg -n "asimétrica" S/01-introduccion.tex S/04-marco-metodologico.tex` = 2; `git diff -- S/00-resumen.tex` vacio; conteo del resumen y del abstract con la regla de c-106 <= 250.

## 4. Propagacion, Zanzotto y forma (B2, B3, C1, C2; items 8-17)

- [x] 4.1 `S/06-implementacion.tex` (6.3, ~linea 37): "Tres disparadores de canal" y "telefonía (webhook \texttt{telefonia-handoff}, al que el backend entrega la transcripción)" (D6); cotejar con 5.2 y 6.4.
- [x] 4.2 `S/04-marco-metodologico.tex` (4.2, ~linea 16): oracion de D6 sobre el observador de `A1` (`T1`, autor).
- [x] 4.3 `S/07-resultados.tex` (8.7, ~linea 251): declarar que `predicciones_in_sample.json` contiene las mismas 200 predicciones que `predicciones_hybrid-v3_2026-10-07.json` (D6; verificado en 0.3).
- [x] 4.4 `C/numeros-canonicos.md`: (b'') ~811-826 a "refutada sobre los 147 revisados" con los matices; ~920 "unión" -> "intersección" (130/151; la unión daría 137) (D6).
- [x] 4.5 `S/02-marco-teorico.tex` (2.4, ~linea 32): Zanzotto limitado a "retribuir a quienes aportan el conocimiento que usan los sistemas" (D7) y "; Los autores" -> "; los autores" (D8).
- [x] 4.6 `S/07-resultados.tex` (8.3): VIS-005 como requisito de la especificacion de visibilidad de incidentes (c-82) (D8); VIS sigue desarrollada.
- [x] 4.7 `S/10-recomendaciones.tex`: introduccion del capitulo 11 (~linea 6) con "cuya sub-hipótesis la campaña complementaria refutó"; 11.3 (~linea 18) con "Tres requisitos" y el de dimensionamiento de la muestra (D8).
- [x] 4.8 `Bibliography_base.bib`: `Zendesk2026_help_desk` sin "Suite" en la nota; titulo segun el `<title>` real verificado con `curl -sL -A "Mozilla/5.0" https://www.zendesk.com/service/`. `ServiceNow2026_itsm`: `curl -sI -A "Mozilla/5.0" https://www.servicenow.com/products/itsm.html`; si responde, actualizar `urldate`; si no, dejarla y registrar fecha y codigo en la seccion c-195.
- [x] 4.9 Verificacion: `rg -n "trigger de Twilio|callback de grabación de Twilio|webhook de transcripción" S/06-implementacion.tex` = 0; `rg -n "sostener la supervisión humana|; Los autores" S/02-marco-teorico.tex` = 0; `rg -n "campaña complementaria de medición refutó" S/10-recomendaciones.tex` = 0; `rg -n "Suite" Bibliography_base.bib` sin la nota de Zendesk; `rg -n "no concluyente|la unión de los sectores" C/numeros-canonicos.md` solo en notas historicas marcadas como superadas; `python verify_citations.py` PASS.

## 5. Anexo I (A3, item 6)

- [x] 5.1 `S/12-anexos.tex` (parrafo de presentacion de `sec:anexo-trazabilidad`, ~linea 205): "nueve dictámenes" y "traza seis", con las dos remisiones nuevas (D3).
- [x] 5.2 Tabla `tab:anexo-trazabilidad-0911-v1213` (dictamen del 9-11 sobre `v1.2.13`; changes `c-192`, `c-193`, `c-194`), con parrafo de presentacion de una oracion, despues de `tab:anexo-trazabilidad-0911`; filas segun D3, rotulos del dictamen v1.2.13; `\footnotesize`, filas con `\\`, sin numeros de linea.
- [x] 5.3 Tabla `tab:anexo-trazabilidad-0911-v1216` (dictamen sobre `v1.2.16`; change `c-195` en la leyenda), filas A1-C2 segun D3.
- [x] 5.4 Verificacion: todas las `\autoref` nuevas resuelven (0 `??` en `pdftotext`); `rg -n "siete dictámenes" S/` = 0; los `\label` citados existen (`rg -n "\\label\{<ancla>\}" S/`).

## 6. Registro y verificador (A3; Strict TDD)

- [x] 6.1 RED: en `C/test_verificar_matriz_trazabilidad.py`, pruebas de `secciones_sin_matriz` (seccion `## Dictamen ... - c-192` sin matriz -> devuelta; con matriz -> no; seccion de c-188 sin matriz -> no; titulo sin `c-NNN` -> no) y de `main` (registro con una seccion c-19x sin matriz -> codigo 1 y mensaje que nombra la seccion). Ejecutar: fallan.
- [x] 6.2 GREEN: implementar `secciones_sin_matriz(texto, desde=190)` en `C/verificar_matriz_trazabilidad.py` y contarlas como falla en `main`, con el mensaje "seccion sin matriz"; actualizar el docstring. Ejecutar: pasan.
- [x] 6.3 TRIANGULATE/REFACTOR: un caso con dos secciones c-19x (una con y otra sin matriz) y el resumen por seccion; re-ejecutar tras cada refactor. Correr el script sobre el arbol: debe FALLAR por c-192, c-193 y c-194 (prueba de que detecta la regresion) antes de 6.4.
- [x] 6.4 `C/dictamen-correcciones.md`: subseccion "### Matriz de trazabilidad" de 7 columnas en las secciones c-192, c-193 y c-194 (D4), con `SUPERADA por c-195` donde c-195 reescribe el parrafo; conservar las tablas de 5 columnas.
- [x] 6.5 `C/dictamen-correcciones.md`: seccion nueva "## Dictamen v10 / v1.2.16 (2026-11-09) - c-195" con resumen, matriz de 7 columnas (A1-C2 e items 1-18, fragmentos del texto final), decisiones (D1 y checkpoint, camino de D5, D8 c-191 fuera de alcance, ServiceNow, discrepancia de rotulos del registro de c-192), libro mayor de paginas y palabras y nota de release.
- [x] 6.6 Verificacion: `python -I C/verificar_matriz_trazabilidad.py` -> 0 fallas y filas informadas para c-192, c-193, c-194 y c-195; `cd C/ && python -m unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.

## 7. Version entregada, compilacion y registro de fase

- [x] 7.1 Pasar a `v1.2.17` las menciones de version entregada de 0.4 (`05-arquitectura.tex` x3, `06-implementacion.tex`, `11-aspectos-legales.tex` nota NIST, `12-anexos.tex` x8 incluidos Anexo A, leyendas, Anexo B, encabezado y nota de la Tabla 19); conservar las historicas. Anexo B con la oracion de verificacion de D9 (`git rev-list -n1 v1.2.17`), sin ningun hash.
- [x] 7.2 Nota de la Tabla 19: confirmar con `git diff --stat cda7712 HEAD -- App/ n8n/ docker/ docker-compose.yml` que el conteo sigue en 24 archivos (c-195 no toca esas rutas); si difiere, corregir el numero.
- [x] 7.3 Compilar en Docker (en segundo plano): 0 errores, 0 referencias o citas indefinidas, 0 `multiply defined`, `main.blg` sin WARN/ERROR, 0 `??`, `Overfull` no mayor que la linea base; `verify_citations.py` PASS.
- [x] 7.4 Paginas: <= 120 y crecimiento sobre 118 causado solo por las tablas del Anexo I; si supera 120, compactar las tablas y recompilar; si aun supera, detener y consultar. Registrar el libro mayor en la seccion c-195.
- [x] 7.5 Regenerar `docs/Tesis/v10 (IA)/paper/compilacion.md` con `C/resumir_registro_compilacion.py` (SHA-256 igual a `sha256sum main.pdf`) y `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py` (no vacio).
- [x] 7.6 `CHANGES.md`: FASE 60 con la entrada `[C-195] atender-dictamen-v1-2-16` (formato de FASE 58/59: estado, scope, dependencias, governance, leer antes) y actualizacion de la linea "Total" (activos c-191 y c-195; release vigente `v1.2.17`; `v1.2.16` superada en `ca3c885`).
- [x] 7.7 `openspec validate c-195-atender-dictamen-v1-2-16 --strict --no-interactive`.

## 8. Release (orquestador)

- [ ] 8.1 (Orquestador) Commit de contenido en `change/c-195-atender-dictamen-v1-2-16` con la oracion de verificacion del Anexo B; tag anotado `v1.2.17` sobre ese commit.
- [ ] 8.2 (Orquestador) Commit siguiente que solo reemplaza la oracion por el hash completo del commit de contenido; `git diff --stat v1.2.17 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` = un archivo, una linea; `pdftotext` del PDF del tag sin cadenas hexadecimales de 40 caracteres; `python -I C/verificar_matriz_trazabilidad.py --rev v1.2.17` -> 0 fallas.
- [ ] 8.3 (Orquestador) `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` (nunca `--all`), commit de `.engram/`, PR contra `main` (nunca push directo) y CI en verde; push del tag con confirmacion del usuario.
