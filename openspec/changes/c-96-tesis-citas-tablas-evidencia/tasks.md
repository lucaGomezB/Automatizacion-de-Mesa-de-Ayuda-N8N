# Tasks: c-96 — Citas, tablas y evidencia transversal

> Convencion de rutas: `S = docs/Tesis/v9 (IA)/paper/sections`;
> `B = docs/Tesis/v9 (IA)/Bibliography_base.bib`.
> Verificacion de texto: `rg` sobre `S` y `B` (sin compilador LaTeX local; los
> `.bak` no se editan ni se cuentan).
> Verificacion de citas: `python3 "docs/Tesis/v9 (IA)/verify_citations.py"` y
> comparacion de las claves de `docs/Tesis/v9 (IA)/paper/main.bcf` contra `B`.
> Recompilacion: Overleaf (`main.tex`, XeLaTeX), tarea final.
> No se edita `App/**`, ni artefactos de c-76/c-77/c-78/c-80, ni `CHANGES.md`, ni
> `docs/Tesis/Correcciones/dictamen-correcciones.md`.
>
> **Orden de aplicacion (D-ORDER):** ejecutar DESPUES de c-78 (para reutilizar su
> bibliografia 2023-2026) y en coordinacion con c-80 (dueno del formato de
> tablas). No existe `_.tex`: las lineas de fuente van en el `.tex` dueno de cada
> tabla.
>
> **Presupuesto de entradas nuevas:** exactamente DOS (SEPyME y APA~2017). Toda
> otra cita MUST resolverse contra entradas ya existentes en `B`.

## 1. A-26 — Tabla 1 con fuente, citas y sin autoevaluacion

- [x] 1.1 En `S/03-estado-del-arte.tex:51` retirar la fila `\textbf{Propuesta} & Hibrida (iPaaS + modulo propio) & ...` de la grilla de `tab:comparativa`, dejando la tabla con las cinco soluciones comerciales. Verificar con `rg -n "Propuesta" S/03-estado-del-arte.tex` (sin la fila dentro del entorno `table`, solo en prosa si corresponde).
- [x] 1.2 Agregar a `tab:comparativa` (`S/03-estado-del-arte.tex:36-54`) la linea de fuente con la referencia de cada proveedor y la fecha de consulta, inmediatamente despues de `\bottomrule`. Verificar con `rg -n "Fuente|consultad" S/03-estado-del-arte.tex`.
- [x] 1.3 Asegurar una cita por fila de solucion comercial: reutilizar entradas de `B` cuando existan o respaldar la afirmacion en la linea de fuente con la documentacion oficial (URL) y la fecha de consulta, SIN crear entradas nuevas (el presupuesto es de dos). Verificar que cada fila de solucion tenga cita o URL de fuente asociada; registrar el criterio elegido. Criterio aplicado: no existia entrada en `B` para ningun proveedor, por lo que cada fila queda respaldada por la URL oficial en la linea de fuente (Zendesk, Freshdesk, Jira SM, ServiceNow ITSM, osTicket).
- [x] 1.4 Confirmar que la comparacion de la propuesta contra las soluciones queda en prosa (`S/03-estado-del-arte.tex:56-58`) con respaldo, sin autoevaluacion en la grilla. Verificar por inspeccion del entorno `table`. Se retiro "frente a la propuesta del presente trabajo" de la entradilla (`:36`) para no atribuir a la grilla la comparacion de la propuesta.

## 2. M-01 — SEPyME y cita huerfana APA 2017

- [x] 2.1 Agregar en `B` la entrada de la Secretaria de la Pequena y Mediana Empresa (SEPyME) con `author` institucional, `title`, `year`, `url` de la fuente oficial y fecha de consulta (o, si no se verifica la fuente, reformular). Verificar con `rg -n "SEPyME|Pequena y Mediana" B`. Se agrego `SEPyME2026_mipyme` (pagina oficial "Que es una MiPyME?", argentina.gob.ar, consultada el 19-10-2026). DESVIACION: el rango "50-200 trabajadores" NO se pudo respaldar contra la fuente oficial (los topes de personal ocupado de SEPyME para servicios son 7/30/165/535); se reformulo la afirmacion sin ese rango (ver flag F-01).
- [x] 2.2 En `S/01-introduccion.tex:12` (§1.1) agregar `\parencite{<clave_sepyme>}` a la definicion de empresa mediana (50-200 trabajadores). Verificar con `rg -n "50 y 200|Pequena y Mediana" S/01-introduccion.tex` y que la clave citada existe en `B`. Se agrego `\parencite{SEPyME2026_mipyme}`; la clave existe en `B`. El rango 50-200 se retiro por no ser verificable (ver 2.1).
- [x] 2.3 En `B` agregar la entrada `APA2017` (Asociacion Americana de Psicologia, 2017) o retirar la cita de `S/11-aspectos-legales.tex:28` y sostener el argumento sin ella. Verificar con `rg -n "APA, 2017|APA2017" S/11-aspectos-legales.tex B`. Se agrego la entrada `APA2017` (Ethical Principles of Psychologists and Code of Conduct, APA, 2017, https://www.apa.org/ethics/code, consultada el 19-10-2026) y se reemplazo la cita textual huerfana "(APA, 2017)" por `\parencite{APA2017}`.
- [x] 2.4 Ejecutar `python3 "docs/Tesis/v9 (IA)/verify_citations.py"` y la comparacion de `main.bcf` contra `B`; confirmar CERO citas huerfanas y CERO entradas sin usar. Registrar la salida. Salida: 48 entradas / 48 claves citadas / 0 huerfanas / 0 sin usar / STATUS: PASS. `main.bcf` esta desactualizado (ultimo compile previo a este change); se recompila en Overleaf.

## 3. A-27 — N8N fuera del rotulo "codigo abierto"

- [x] 3.1 En `S/01-introduccion.tex:60` (§1.7) reescribir la enumeracion "herramientas de bajo costo y codigo abierto ---N8N, Python, FastAPI, PostgreSQL---" para que N8N no quede bajo "codigo abierto"; separar N8N y explicitar su licencia Sustainable Use (o citar solo Python/FastAPI/PostgreSQL como codigo abierto). Verificar con `rg -n "codigo abierto" S/01-introduccion.tex` sin N8N en esa enumeracion. Opcion (a): componentes de codigo abierto (Python, FastAPI, PostgreSQL) + N8N como plataforma autoalojada bajo licencia Sustainable Use (fair-code).
- [x] 3.2 En `S/06-implementacion.tex:8` (§6.1) reemplazar "exclusivamente tecnologias de codigo abierto" por una formulacion que distinga las piezas de codigo abierto de N8N (Sustainable Use / fair-code). Verificar con `rg -n "codigo abierto" S/06-implementacion.tex` y que N8N quede matizado. Se reemplazo "exclusivamente tecnologias de codigo abierto" por "combinando componentes de codigo abierto (Python, FastAPI, PostgreSQL) con N8N, cuya licencia Sustainable Use (fair-code) permite auditar su codigo fuente".
- [x] 3.3 Confirmar consistencia con §3.2 y §6.3. Verificar con `rg -n "Sustainable Use|fair-code" S/03-estado-del-arte.tex S/06-implementacion.tex` (presente en 3.2 y 6.3, y ahora coherente en 1.7 y 6.1). Coherente: 3.2 "licencia Sustainable Use", 6.3 "fair-code", y ahora 1.7 y 6.1 con ambas expresiones.
- [x] 3.4 Confirmar que NO se toco la version de N8N (`S/06-implementacion.tex:10`), que es alcance de c-80. Verificar con `rg -n "1\.62|2\.11\.2" S/06-implementacion.tex`. Sin cambios: `N8N~2.11.2` intacto.

## 4. B-01 — Organizacion adoptante consistente

- [x] 4.1 Definir la caracterizacion canonica: "una organizacion mediana del sector servicios con sede en la provincia de Mendoza, de aproximadamente 120 usuarios internos distribuidos en cinco areas funcionales" (sin nombre propio).
- [x] 4.2 En `S/01-introduccion.tex:16` (§1.2) aplicar la denominacion canonica. Verificar con `rg -n "organizacion mediana del sector servicios" S/01-introduccion.tex`. §1.2 ya contenia la denominacion canonica (se conserva).
- [x] 4.3 En `S/01-introduccion.tex:68` (§1.8) reemplazar "una unica organizacion del sector servicios" por la misma denominacion y atributos. Verificar con `rg -n "unica organizacion" S/01-introduccion.tex` sin residuo y con la etiqueta consistente en ambas secciones. §1.8 ahora dice "una organizacion mediana del sector servicios con sede en la provincia de Mendoza, de aproximadamente 120 usuarios internos distribuidos en cinco areas funcionales". Residuos de "unica organizacion" en §1.9 (`:72`) y en `08-discusion.tex:42` (fuera de alcance; ver flag F-02).

## 5. T1 — Linea de fuente en las nueve tablas

- [x] 5.1 `tab:comparativa` (`S/03-estado-del-arte.tex:36`): linea de fuente con referencias y fecha de consulta (cubierta por 1.2). Verificar con `rg -n "Fuente" S/03-estado-del-arte.tex`.
- [x] 5.2 `tab:variables` (`S/04-marco-metodologico.tex:22`): agregar "Fuente: elaboracion propia." Verificar con `rg -n "Fuente" S/04-marco-metodologico.tex`.
- [x] 5.3 `tab:capas` (`S/05-arquitectura.tex:12`), `tab:entidades` (`:66`) y `tab:api` (`:92`): agregar "Fuente: elaboracion propia." Verificar con `rg -c "Fuente" S/05-arquitectura.tex` (3).
- [x] 5.4 `tab:tiempos` (`S/07-resultados.tex:12`), `tab:matriz` (`:42`), `tab:metricas` (`:61`) y `tab:errores` (`:92`): agregar "Fuente: elaboracion propia a partir del corpus de validacion (\(n = 200\))." Verificar con `rg -c "Fuente" S/07-resultados.tex` (4).
- [x] 5.5 Confirmar el total: `rg -c "Fuente" S` debe dar 9 en las secciones con tablas y cero en las demas; y que la linea de fuente no altera `\small`/`\raggedright` (c-80). Verificar con `rg -n "Fuente" S`.

## 6. T2 — Cobertura y densidad de citas (sin duplicar c-78)

- [x] 6.1 En `S/07-resultados.tex` (hoy 0 citas) agregar citas en las afirmaciones apoyadas en literatura o en metodos de terceros (metricas de evaluacion, intervalos de confianza, pruebas no parametricas), reutilizando entradas existentes (`Sokolova2009_performance_measures`, `Wilson1927_probable_inference`, etc.) o las referencias 2023-2026 de c-78. NO editar cifras (c-76). Verificar con `rg -c "\\\\textcite|\\\\parencite|\\\\cite" S/07-resultados.tex` (> 0).
- [x] 6.2 En `S/06-implementacion.tex` reforzar afirmaciones metodologicas con entradas existentes; no crear referencias nuevas. Verificar con `rg -c "\\\\textcite|\\\\parencite|\\\\cite" S/06-implementacion.tex` (>= al conteo previo, sin claves nuevas fuera de `B`).
- [x] 6.3 En `S/03-estado-del-arte.tex` asegurar que la comparacion de la Tabla~1 y su sintesis en prosa queden respaldadas (articulado con la seccion 1 de estas tareas). Verificar con `rg -c "\\\\textcite|\\\\parencite|\\\\cite" S/03-estado-del-arte.tex`.
- [x] 6.4 Confirmar el presupuesto de entradas nuevas: las unicas claves agregadas a `B` son SEPyME y APA~2017. Verificar con `git diff B` y que no haya duplicados ni huerfanas nuevas. Si c-78 no esta aplicado, marcar como condicionadas las citas que dependen de sus referencias (OQ-C96-1).

## 7. Verificacion final y recompilacion

- [x] 7.1 Barrido de control: `rg -ni "Propuesta & Hibrida|Secretaria de la Pequena y Mediana Empresa(?!.*cite)|\(APA, 2017\)|exclusivamente tecnologias de codigo abierto|N8N, Python, FastAPI|unica organizacion del sector servicios" S` sin residuos.
- [x] 7.2 Confirmar cero citas huerfanas y cero entradas sin usar con `python3 "docs/Tesis/v9 (IA)/verify_citations.py"` y la comparacion de `main.bcf` contra `B`; registrar la salida.
- [x] 7.3 Recompilar la tesis en Overleaf (`main.tex`, XeLaTeX): PDF sin errores fatales, las nueve tablas muestran su linea de fuente, la Tabla~1 ya no incluye la fila "Propuesta", y la longitud total no supera las 100 paginas. Registrar el conteo de paginas. — COMPLETADO 2026-10-20: recompilado localmente con MiKTeX (xelatex -> biber -> xelatex -> xelatex); 103 paginas; 0 errores fatales; 0 referencias indefinidas; 48/48 bibliografia; las 8 figuras renderizan. (latexmk no disponible: MiKTeX sin Perl.)
- [x] 7.4 Ejecutar `openspec validate c-96-tesis-citas-tablas-evidencia --strict` y confirmar que pasa.
