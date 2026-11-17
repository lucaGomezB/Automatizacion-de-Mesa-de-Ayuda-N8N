# Design: Mejorar la legibilidad del capitulo de resultados y de los anexos (M-03, B-01, B-03)

## Context

Ver `proposal.md` para la motivacion. Fuente: `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md` (seccion 3, N-07 y N-15 parciales; seccion 5, M-03, B-01 y B-03; seccion 7, puntos 8 y 10). Los deltas viven en `specs/tesis-document/spec.md`.

**Convenciones.** `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`; `P/` = `docs/Tesis/v10 (IA)/paper/`. Capitulo del PDF -> archivo: 1 = `01-introduccion`, 4 = `04-marco-metodologico`, 8 (Resultados) = `07-resultados`, 9 (Discusion) = `08-discusion`, 10 = `09-conclusiones`, 11 = `10-recomendaciones`; Anexos A a J = `12-anexos.tex` (un solo archivo; la letra sale del orden de `\section` dentro de `appendices`). Cada parrafo de los `.tex` es una sola linea fisica; **todas las lineas citadas son de `v1.5.2` y cambian tras `c-235` y `c-236`**: el apply re-localiza por texto (`rg -n`).

**Orden de aplicacion.** `c-235` (retiro de lo fuera de muestra: desaparecen enteros §8.6, §8.9 y §8.12, y parcialmente §8.4 y §8.10; del Anexo J, los parrafos de arbitraje por mayoria y de robustez de la brecha) -> `c-236` (balance como cota superior; cambia valores del Anexo J del balance) -> `c-237` (Anexo I.2) -> **`c-238`** -> `c-239` (respuestas, version, recompilacion, tag).

**Estado de partida verificado al proponer** (solo lectura, 2026-11-16, `main` en `88edd02`, `v1.5.2`):

- `S/07-resultados.tex` (585 lineas): L6 "doce apartados"; L8 recordatorio de procedencia (65 palabras); §8.1 L10 (`tab:tiempos` L17, `tab:tiempos-canal` L39, descuentos de redondeo L63, `\paragraph{Rango de robustez consolidado}` L65 con la oracion mas larga del documento, 95 palabras, `tab:rango-robustez-tiempos` L70 con el bloque "Cotas de alcance" L81 y nota L89); §8.2 L99 (`tab:matriz`, `tab:exactitud-etapa-canal` L131, prosa L153-155 con 73,5 %, 0,6508, 0,797 y 0,757; `tab:metricas` L160); §8.3 L182 (25/147, p 0,28); §8.4 L192 (`tab:bandas` L200, `tab:calibracion-gate` L227, AUROC 0,5168 L234/L243); §8.5 L253 (`subsec:sensibilidad-ajustes`, `tab:sensibilidad-ajustes` L260, lectura L275); §8.6 L277; §8.7 L322 (`tab:errores`, sectores sin tilde en prosa L347, con tilde L349 y L351); §8.8 L353 (kappa 0,5569 L357, `tab:tiempos-manual-complementaria` L364, relectura con el brazo del corpus canonico en la prosa que sigue a la tabla); §8.9 L387; §8.10 L452; §8.11 L523 (`tab:carga-multicanal` L530; p95 1215,8 y 6788,4 ms; "no sostenida" L552); §8.12 L556.
- Rotulos en `07-resultados.tex`: "primaria/primario" 15, "sensibilidad" 40, "cota(s) de alcance" 3, "complementaria" 18 (casi todas en el nombre "campaña complementaria"). "superada"/"supuesto superado" vive en `08-discusion.tex` y en el Anexo J L269 (los resuelve `c-236`).
- `S/12-anexos.tex`: diez `\section` -> A diagrama, B repositorio, C esquema BD, D OpenAPI, E flujo N8N, F corpus, G documentacion operativa, H prompt, I trazabilidad (`sec:anexo-trazabilidad`), **J numeros canonicos** (`sec:anexo-numeros-canonicos`, L243-334). El anexo nuevo, agregado al final, recibe la letra **K** sin renumerar ninguno.
- Anexo J: cuatro `\paragraph` titulados "(memo, sección 3.xx)" + `table` sin `\caption` ni `\label`, `tabular` `@{}p{4.4cm} p{7.2cm} p{2.2cm}@{}` (Valor | Procedencia | Estado), sin `\raggedright`; estados "vigente (nuevo)", "vigente", "condicional", "cota de sensibilidad (nuevo)", "vigente (sin cambio)", "vigente y cota de sensibilidad"; "memo" en L245, 247, 267, 280-282, 291, 313, 330; claves JSON en `\texttt{...\_...}` sin puntos de corte (L261 `justificacion\_umbral.paridad\_manual`, L262 `costo\_marginal\_por\_punto\_horas\_trimestre`); rutas elididas `\path{...c220.json}` y procedencias `\path{07-resultados.tex}` (un archivo fuente como procedencia). `P/compilacion.md`: 164 paginas, 25 `Overfull \hbox` (maximo 82,3 pt). No hay `main.log` versionado.
- Preambulo: `array` (L66), `xurl` (L93), `hyperref`; solo define `\doi` y `\urlref`; no hay `seqsplit` ni `ragged2e`.
- Oraciones (`C/sent_c197.py`, regla D1 de c-197): 1.622 oraciones, 337 de mas de 40, **40 de mas de 60** (07: 9; 10: 8; 08: 7; 09: 4; 01, 03, 04, 06: 2; 02, 05, 11: 1; **00-portada: 1**, que es el bloque de titulo sin punto y no es prosa), "de modo que" 31. `C/list_long_c197.py <dir> 60` (por linea fisica, **sin** excluir tablas ni notas) lista 40 entradas, entre ellas una fila de `tab:cumplimiento-objetivos` (09:24) y una nota de fuente del Anexo B (12:93).
- Extension (regla D1, prosa sin tablas ni matematicas, archivos `01` a `11`): **43.241 palabras**; `wc -w` crudo de los mismos fuentes: **50.532**; `12-anexos.tex`: 3.176 (D1) / 5.153 (crudo). El tribunal mide ~51.900 sobre el PDF.
- Sectores: sin tilde en prosa `01:48`, `01:72`, `07:347`, `07:389` (la borra `c-235`), `08:26`; con tilde en prosa `04:46`, `05:70`, `07:180`, `07:349`, `07:351`; en `\texttt{}` (literales correctos) en 04, 05, 07, 08, 10 y 12. Las cadenas canonicas estan en `App/Backend/app/constants.py:18-22`. Hay **dos requisitos vigentes contradictorios**: "Coherencia de los nombres de sector con su definicion canonica" (prosa con tilde; cadena en `\texttt{}`) y "Nomenclatura canonica de los sectores en la prosa del documento" (de `c-233`, que mando a escribir sin tilde y en fuente del cuerpo los pasajes que "citan el sistema", origen de B-01). `C/revision-tildes-decisiones.tsv` registra la decision previa OQ1/D7 ("canonicos" -> sin tilde).

## Goals / Non-Goals

**Goals:**

- Que el lector encuentre en un solo lugar, al abrir el capitulo 8, que se midio, con que incertidumbre y que se concluye frente a cada hipotesis u objetivo.
- Sacar del cuerpo las lecturas de sensibilidad y robustez que sobreviven a `c-235`, sin perderlas, y reducir los rotulos a un vocabulario minimo definido una sola vez.
- Depurar el Anexo J (sin estado, sin memo, sin desbordes) y resolver B-03 con una tecnica tipografica verificable.
- Llevar a 0 las oraciones de mas de 60 palabras con el metodo del repositorio y revisar a mano lo que ese metodo excluye.
- Unificar los nombres de sector (B-01) con una regla unica y auditable.
- Reducir de forma medible la extension del cuerpo.

**Non-Goals:**

- Cambiar cifras, intervalos, veredictos o conclusiones; recalcular nada; tocar `numeros-canonicos.md`.
- Lo fuera de muestra (`c-235`), el balance y el umbral (`c-236`), el Anexo I.2 (`c-237`), las respuestas al tribunal, el bump de version, la recompilacion versionada y el tag (`c-239`).
- Renombrar etiquetas existentes; cambiar el nombre propio "campaña complementaria".
- `App/`, `n8n/`, `evaluation/`.

## Decisions

### D1 — Tabla unica de sintesis al abrir el capitulo 8

- **Ubicacion.** Despues de los dos parrafos de apertura vigentes (enumeracion de apartados, que el requisito "Parrafo introductorio del capitulo de resultados coherente con sus subsecciones" protege, y recordatorio de procedencia, protegido por "Recordatorio de la procedencia al abrir la seccion de resultados") y antes de `\subsection` §8.1: un parrafo breve "que se concluye" + `tab:sintesis-resultados`. Asi se satisfacen los dos requisitos vigentes sin modificarlos. Alternativa descartada: reemplazar el parrafo de enumeracion por la tabla (rompe ambos requisitos y obliga a MODIFIED adicionales).
- **Columnas** (`\footnotesize`, `>{\raggedright\arraybackslash}p{}`): Medida | Cifra primaria | `n` | Intervalo al 95 % | Veredicto frente a la hipotesis u objetivo | Desarrollo (`\autoref`). Sin columna de rol ni de estado: todas las filas son primarias por definicion, salvo la marcada en la propia celda.
- **Filas candidatas** (in-sample; el apply **verifica cada valor en el `.tex` resultante de `c-235`/`c-236` y en `C/numeros-canonicos.md`**, no en esta lista):
  1. Tiempo de registro: 61,6 s -> 17,76 s; reduccion 71,2 % [67,2 %; 74,6 %]; `n = 200`; Wilcoxon `W = 363`, `p = 3,08e-32`; primera sub-hipotesis confirmada (cota superior por redondeo) -> `subsec:comparacion-tiempos`.
  2. Exactitud estricta 73,5 % (147/200) [67,0 %; 79,1 %] y macro-F1 de umbral 0,6508 (cuatro clases estimables); criterio 85 % / 0,85 no alcanzado; tercera sub-hipotesis refutada -> `subsec:matriz-metricas`.
  3. Contra el consenso `E1`/`E2`: 110/138 = 0,797 [0,722; 0,856]; macro-F1 0,757; lectura de la referencia alternativa, el criterio sigue sin alcanzarse en macro-F1 -> `subsec:matriz-metricas` (ver Open Questions sobre su inclusion).
  4. Fiabilidad de la referencia: kappa `E1`/`E2` 0,5569 [0,4725; 0,6413], moderado -> `subsec:resultados-campana-medicion`.
  5. Intervencion humana: 25 de 147 revisados = 17,0 % [11,8 %; 23,9 %], `p` unilateral 0,28; segunda sub-hipotesis no concluyente, con estimacion puntual por encima de la cota; la revision bruta 147/200 = 73,5 % mide la regla `VIS-005`, no la hipotesis (dicho en la celda) -> `subsec:reduccion-intervencion`.
  6. Confianza de Gemini: AUROC 0,5168 [0,3796; 0,6528], `n = 69`; no discrimina; ningun umbral seleccionado -> `subsec:calibracion`.
  7. Carga concurrente: p95 con 20 concurrentes 1215,8 ms (backend) y 6788,4 ms (webhook de N8N) frente al techo de 5000 ms; `n = 120` por nivel; dimension de capacidad de la hipotesis de integracion "no sostenida" -> `subsec:carga-concurrente`.
  8. Eficiencia (brazo de modelo solo): **solo si** `c-235` deja un veredicto in-sample citado en el capitulo; si queda solo como bloque informativo "no limpio", no entra en la tabla (Open Question).
- **Parrafo "que se concluye"** (<= 120 palabras, sin cifras que no esten en la tabla): una oracion por sub-hipotesis y una por la hipotesis de integracion, con el mismo calificador que el resumen y la discusion.
- **No repeticion.** Dentro de `07-resultados.tex`, cada cifra primaria aparece en la tabla de sintesis, en su seccion de desarrollo (prosa y/o su tabla propia) y en ningun otro lugar de prosa del capitulo; las demas menciones se reemplazan por una remision (`\autoref{tab:sintesis-resultados}` o a la seccion). Las tablas propias de cada seccion quedan exentas. Verificacion: conteo por cifra con `rg -o` antes/despues, registrado. La regla no se extiende a 08-11 (los capitulos de discusion y conclusiones necesitan citar sus cifras; ya estan acotados por requisitos previos).
- La tabla no duplica `tab:procedencia-numeros` (capitulo 4), que sigue siendo el mapa de corridas; la sintesis remite a ella en su nota.

### D2 — Anexo K de sensibilidad y robustez

- **Ubicacion y nombre.** `\section{Lecturas de sensibilidad y robustez}\label{sec:anexo-sensibilidad}` al final de `12-anexos.tex`, despues del Anexo J -> letra K; no renumera A a J. Alternativa descartada: insertarlo antes de J (renumeraria J a K y romperia las remisiones del documento de respuestas y de la matriz de `c-239`).
- **Que se traslada** (criterio: es relectura de valores ya calculados bajo un supuesto alternativo o un ambito distinto, no la medicion que decide una hipotesis u objetivo). Inventario sobre `v1.5.2`; el apply lo confirma contra el texto post-`c-235`:
  - K.1 Tiempos: el detalle de los descuentos de redondeo (L63: 56,6 s / 51,6 s, 68,6 % / 65,6 %, `p = 1,8e-26`, `r = 0,8683`), el parrafo "Rango de robustez consolidado" (L65) y `tab:rango-robustez-tiempos` (L67-90). En §8.1 queda una oracion: la reduccion se lee como cota superior y su sensibilidad al redondeo y su rango estan en `\autoref{sec:anexo-sensibilidad}`.
  - K.2 Ajuste del clasificador con el corpus: la subseccion entera `subsec:sensibilidad-ajustes` (L253-275) con `tab:sensibilidad-ajustes`, como `\subsection` del anexo, **conservando las etiquetas** `subsec:sensibilidad-ajustes` y `tab:sensibilidad-ajustes` (las remiten 05, 07, 08, 09 y 10 y varios requisitos vigentes) y la cita de la linea 95 de `evaluation/report_sensibilidad_ajustes.md`. En §8.2 queda la remision "estimaciones dentro de la muestra (\autoref{subsec:sensibilidad-ajustes})" que ya existe.
  - K.3 Campana complementaria: la relectura de las reducciones por operador con el brazo automatizado del corpus canonico (19,6 %, 75,9 %, 62,7 %), la variante sin el registro R025 y las correlaciones entre campanas, que siguen a `tab:tiempos-manual-complementaria`. La tabla y la medicion por operador quedan en §8.8.
  - Lo que `c-235` deje de §8.4 (barrido de umbrales y senales alternativas dentro de la muestra) **se queda** en §8.4: es la aplicacion de una regla prerregistrada, no una sensibilidad (Open Question si el apply encuentra lo contrario).
  - Si `c-235` no retirara §8.6, §8.12 o `tab:robustez-linea-base`, van a K (es lo que pide el tribunal); con el retiro previsto, no hay nada que trasladar de ellos.
- **Vocabulario minimo de rotulos**, definido una sola vez en el parrafo "que se concluye" (o en la nota de `tab:sintesis-resultados`) y usado solo con ese sentido: **primaria** (la cifra que decide una hipotesis u objetivo y figura en la sintesis), **secundaria** (metrica descriptiva o de otro marco que no decide) y **sensibilidad** (relectura de valores ya calculados bajo un supuesto alternativo; vive en el Anexo K). Se retiran del capitulo 8 "cota de alcance", "complementaria" como rotulo de cifra, "vigente" y "superada"; "campaña complementaria" se conserva como nombre propio de la campana. "Cota superior/inferior" se conserva cuando describe la direccion de un sesgo de medicion (redondeo, grabacion de 45 s), no como rotulo de categoria. Verificacion: `rg -c "cota[s]? de alcance" S/07-resultados.tex` = 0; conteo de "sensibilidad" en 07 registrado antes/despues y sin usos fuera de la remision al Anexo K, de "sensibilidad (recall)" y de los nombres de seccion.
- La nota de la tabla trasladada que hoy usa "Cotas de alcance (no comparables con el estimando primario)" (L81) se reescribe con el vocabulario minimo ("Otros ambitos, no comparables con la cifra primaria") sin cambiar valores.

### D3 — Anexo J depurado y formato que no desborda (B-03)

- **Sin estado.** Se retira la columna "Estado". Si un estado distinto de "vigente" lleva informacion sustantiva (por ejemplo, una fila de sensibilidad o condicional que `c-236` haya dejado), esa calificacion pasa al texto de la celda "Valor" con el vocabulario de D2 ("sensibilidad"); "(nuevo)", "(sin cambio)" y "vigente" se eliminan sin reemplazo.
- **Sin memo.** El parrafo de apertura (L245) se reescribe: el anexo reune los valores que el cuerpo cita y, para cada uno, el artefacto versionado y el comando que lo reproducen. Los titulos `\paragraph{... (memo, sección 3.xx).}` pierden el parentesis. Las procedencias "memo 3.11", "memo 3.1 y 3.4", "memo 3.21 (c)" y "memo 3.1 a 3.35" se reemplazan por el artefacto y la clave que ya figuran en la misma celda o por la remision a la tabla de la tesis que muestra el valor (`\autoref{tab:...}`); `\path{07-resultados.tex}` se reemplaza por esa remision. Verificacion: `rg -n -i "memo" ` sobre el rango de `sec:anexo-numeros-canonicos` = 0. `C/numeros-canonicos.md` sigue siendo la fuente interna y no se toca.
- **Formato.** Cada tabla: `\caption{}` + `\label{tab:anexo-nc-<tema>}` (para que el Anexo J tenga remisiones estables y figure en el indice de tablas), `\footnotesize`, dos columnas `@{}>{\raggedright\arraybackslash}p{5.6cm} >{\raggedright\arraybackslash}p{9.8cm}@{}` (suma 15,4 cm frente a un `\textwidth` de ~15,9 cm; el apply ajusta si el log lo pide). Las claves JSON se escriben con `\path{escenario_central}` (xurl permite cortar en cualquier caracter; en columna `\raggedright` el corte no estira el espacio entre letras); se prohibe `\texttt{...\_...}` para claves. Las rutas completas del artefacto y del comando van **una vez**, en el parrafo que precede a cada tabla; en las celdas va solo la clave (sin `\path{...c220.json}` ni "idem" con "..."). La causa raiz de las rutas espaciadas letra por letra es `\path` en una columna `p{}` justificada: `\raggedright` la elimina. Alternativas descartadas: `seqsplit` (dependencia nueva y corte sin semantica), `tabularx` (dependencia nueva para un problema que `array` ya resuelve), achicar a `\scriptsize` (ilegible a tamano de impresion).
- **Criterio.** Compilacion de verificacion (D8): 0 `Overfull \hbox` cuyo rango de lineas de entrada cae en `sec:anexo-numeros-canonicos` y total del documento < 25 (la cifra de `v1.5.2`); se registra el total y el maximo. Las tablas nuevas de los Anexos K y la sintesis tampoco agregan `Overfull`.

### D4 — Oraciones de mas de 60 palabras (N-07)

- **Metodo de medicion.** Unico y reproducible: `C/sent_c197.py "<S>"` (regla D1 de c-197, que excluye tablas, figuras, listados, matematicas y comentarios) para el criterio principal, y `C/list_long_c197.py "<S>" 60` (por linea fisica, **incluye** pies de tabla, notas y vinetas) para la revision manual. Ambos con `PYTHONDONTWRITEBYTECODE=1` y sin modificar los scripts.
- **Criterio.** `sent_c197.py`: 0 oraciones de mas de 60 palabras en todos los archivos, con una sola excepcion declarada: `00-portada.tex` (bloque de titulo sin signo de cierre, no es prosa). `list_long_c197.py ... 60`: solo quedan filas de datos de tabla (lineas con `&`), cuyo "largo" es concatenacion de celdas; toda nota (`\textit{Nota:}`, `\textit{Fuente:}`), `\caption`, `\item` o `\footnote` de mas de 60 palabras se parte.
- **Diferencia con el tribunal.** El tribunal cuenta 85 en `v1.5.2` con un metodo propio que incluye mas contextos (notas, epigrafes, vinetas, celdas); el repositorio cuenta 40 con D1. Se registra en `C/dictamen-correcciones.md` la linea base con ambos scripts, la explicacion de la diferencia y el resultado; la respuesta al tribunal la redacta `c-239`.
- **Como partir.** Oracion por oracion: se divide en dos o mas sin dejar ninguna nueva de mas de 60; se conservan sujeto, verbo, cifras, citas y remisiones; no se borra contenido sustantivo (si una clausula es redundante con la tabla de sintesis, se reemplaza por una remision, que no es borrar). "de modo que" se reemplaza por punto o "por eso" donde ayude a partir; meta secundaria: no superar 31.

### D5 — Nombres de sector (B-01, cierre de N-15)

- **Par de macros** en `P/preambles/preamble.tex`, junto a `\doi`/`\urlref`:
  - `\sectorcad{<clave>}` -> `\texttt{<cadena del sistema>}`: `si` = `Seguridad Informatica`, `hw` = `Soporte Tecnico Hardware`, `sw` = `Soporte Tecnico Software`, `bd` = `Bases de Datos`, `sis` = `Sistemas` (byte a byte con `constants.py:18-22`).
  - `\sectorprosa{<clave>}` -> fuente del cuerpo, con tilde: `Seguridad Informática`, `Soporte Técnico Hardware`, `Soporte Técnico Software`, `Bases de Datos`, `Sistemas`.
  - Implementacion sin paquetes nuevos (`\csname` o `\ifstrequal`-libre: cinco `\@namedef` y un `\@nameuse`, o `\newcommand` con `\csname sectorcad@#1\endcsname`); una clave desconocida debe producir error de compilacion, no texto vacio.
- **Regla de uso.** `\sectorcad` cuando el texto cita la cadena exacta del sistema: tablas de datos (matriz de confusion, metricas por clase, fronteras de error, carga), definicion de la taxonomia del clasificador (04, 05), prompt y anexos tecnicos, y toda enumeracion presentada como "los cinco sectores canonicos" o "cadenas". `\sectorprosa` en toda otra mencion narrativa (analisis de errores, discusion, objetivos, alcance). Un mismo pasaje no mezcla ambas para el mismo sector salvo que distinga explicitamente nombre y cadena. Esta regla **reemplaza** la decision OQ1/D7 de `C/revision-tildes-decisiones.tsv` y el requisito de `c-233`, que mandaban la forma sin tilde en fuente del cuerpo.
- **Alcance de la migracion.** Todas las menciones de los cinco sectores en `S/*.tex` (prosa y `\texttt{}` existentes) pasan a una de las dos macros, salvo dentro de `lstlisting`/`verbatim` (prompt literal) y de `\path{}`. "Sistemas" y "Bases de Datos" se migran solo cuando nombran al sector (mayuscula inicial en ese sentido), no la palabra comun. Verificacion: `rg -n "Seguridad Inform|Soporte T[eé]cnico (Hardware|Software)" S/` solo devuelve lineas dentro de entornos literales; `rg -n "\\\\texttt\{(Seguridad|Soporte|Bases de Datos|Sistemas)" S/` = 0; inventario por archivo de `\sectorcad` y `\sectorprosa` registrado. Alternativa descartada: no introducir macros y corregir a mano (no auditable; ya fallo dos veces, N-15 y B-01). Alternativa descartada: una macro por sector y forma (diez macros; mas superficie de error).

### D6 — Meta de extension (M-03)

- **Metodo unico, aplicado a `v1.5.2` y al cierre:** (A) palabras de prosa con la limpieza D1 de `sent_c197` (`word_count(clean(texto))` por archivo) sobre `S/01` a `S/11`; (B) `wc -w` crudo de los mismos fuentes; (C) paginas del PDF y paginas hasta el inicio de los anexos, de la compilacion de verificacion. Linea base `v1.5.2`: A = 43.241, B = 50.532, C = 164 (registrar tambien la pagina de inicio de los anexos al compilar `v1.5.2` o tomarla de `main.toc`). El apply registra ademas A y B al empezar (texto post-`c-237`) para separar el aporte de `c-235`/`c-236` del de `c-238`.
- **Meta.** (1) Reduccion bloqueante frente a la linea base `v1.5.2`: A al cierre al menos 4 % menor que A en `v1.5.2` (A <= 0,96 x 43.241 = 41.511, redondeado), medida con el mismo metodo. Esta reduccion queda subsumida por la meta conjunta con `c-235` frente a `v1.5.2`: A <= 38.900 (-10 %) y paginas del cuerpo menores que en `v1.5.2`. (2) El aporte propio de `c-238` (A al cierre respecto del estado al comenzar, registrado en 1.4) se informa como referencia, NO como umbral bloqueante: exigir otro 4 % sobre el estado post-`c-235` duplicaria el retiro de lo fuera de muestra que ya hizo `c-235`, y la version de referencia para el tribunal es `v1.5.2`. Si la meta conjunta no se alcanza por el alcance real de `c-235`/`c-238`, se registra la cifra y su causa. Los anexos pueden crecer (el traslado los engrosa) y se informan aparte.

### D7 — Guardarrailes

- No cambia ninguna cifra, intervalo, veredicto ni cita. Foto de cifras antes/despues con el patron de `C/foto-cifras-c197.txt`, ampliada a las cifras de la tabla de sintesis y del Anexo J (`rg -n` de un conjunto fijo de cadenas sobre `S/`, guardado en `C/foto-cifras-c238-antes.txt` y `-despues.txt`); el cotejo se hace por **multiconjunto de valores** (las lineas cambian por los traslados) y la unica diferencia admitida es el aumento de apariciones de una cifra primaria en `tab:sintesis-resultados` compensado por remisiones.
- No se renombran etiquetas; las trasladadas conservan su nombre. Toda `\ref`/`\autoref` resuelve (0 referencias indefinidas).
- `verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) en PASS; `Bibliography_base.bib` sin cambios.
- No se reintroducen identificadores de cambio en el cuerpo; no se tocan 4.5, 4.8 ni 9.1 por N-06.

### D8 — Compilacion de verificacion

`latexmk -xelatex -outdir=<directorio temporal fuera del repo> main.tex` desde `P/`: no sobrescribe `main.pdf` ni `compilacion.md` (los regenera `c-239`). Del `main.log` temporal se extraen: errores fatales, referencias/citas indefinidas, etiquetas duplicadas, `Overfull \hbox` totales y los del Anexo J (por el rango de lineas de `12-anexos.tex` que el log informa), paginas totales y pagina de inicio de los anexos. Se registran en `C/dictamen-correcciones.md`.

### D9 — Registro y derivados

- `C/dictamen-correcciones.md`, seccion `c-238`: lineas base y resultados de D4 y D6, inventario de traslados al Anexo K (origen -> destino), inventario de oraciones partidas por archivo, conteo de repeticiones de cifras primarias en 07 (antes/despues), inventario de macros de sector, resultado de D7 y D8.
- `docs/Tesis/v10 (IA)/tesis_para_agente.md` se regenera con `build_tesis_para_agente.py`; no se edita a mano.

## Risks / Trade-offs

- [`c-235` o `c-236` dejan el capitulo 8 distinto de lo previsto] -> los anclajes son orientativos; el grupo 0 de tareas re-inventaria la estructura real y ajusta las filas de la sintesis y el inventario del Anexo K antes de editar.
- [Conflicto de MODIFIED sobre "Anexo de números canónicos citados y cuerpo sin referencias internas al memo" si `c-235`/`c-236` tambien lo modifican] -> `c-238` se archiva despues; antes del archive se reconcilia el bloque MODIFIED con el texto ya archivado (los escenarios de este change no citan secciones concretas del memo para ser compatibles con el retiro de 3.35 y 3.36).
- [Partir oraciones altera una cifra o un matiz causal] -> foto de cifras por multiconjunto; diff revisado por archivo; cada oracion partida conserva sujeto, verbo y conectores causales.
- [Trasladar §8.5 al anexo debilita la salvedad "dentro de la muestra"] -> la remision de §8.2 y de las limitaciones ya existe y se conserva; la etiqueta no cambia.
- [La tabla de sintesis repite cifras que el tribunal ya ve en cada seccion] -> la regla de no repeticion de D1 retira las repeticiones en prosa; la tabla es el unico lugar de lectura conjunta.
- [La migracion a macros introduce un error de cadena] -> la clave desconocida falla la compilacion; `rg` de cadenas literales y cotejo del PDF extraido contra `constants.py`.
- [Mover rotulos cambia el sentido de una salvedad] -> el vocabulario minimo conserva "cota superior/inferior" cuando describe la direccion de un sesgo; solo se retira el rotulo de categoria.
- [La meta de extension se mide contra `v1.5.2`] -> la reduccion bloqueante de 4 % se mide contra la linea base `v1.5.2` (subsumida por la meta conjunta A <= 38.900); el aporte propio de `c-238` respecto del estado al comenzar es informativo, no bloqueante; la conjunta se registra con su causa si no se alcanza.
- [La compilacion de verificacion pisa `main.pdf`] -> `-outdir` temporal fuera del repo.

## Migration Plan

1. Grupo 0: inventario post-`c-237`, lineas base (oraciones, palabras, rotulos, repeticiones, sectores, overfull) y foto de cifras.
2. Macros de sector y migracion (D5).
3. Anexo K y traslados (D2); tabla de sintesis y no repeticion (D1).
4. Anexo J (D3).
5. Pase de oraciones (D4) sobre el texto ya reorganizado.
6. Verificacion (D7, D8), medicion final (D6), registro y derivados (D9).

Rollback: `git revert` del commit de contenido; no hay datos ni codigo de aplicacion afectados.

## Open Questions

- ¿Entra la exactitud contra el consenso `E1`/`E2` (110/138 = 0,797; macro-F1 0,757) en la tabla de sintesis como fila propia o como segunda linea de la fila de exactitud? Propuesta por defecto: segunda linea de la fila 2, porque no decide el criterio (lo decide la exactitud sobre la referencia primaria) pero el tribunal la exigio (N-08).
- ¿Queda en el capitulo 8, tras `c-235`, un veredicto de la hipotesis subsidiaria de eficiencia citable en la sintesis, o solo el bloque in-sample informativo? Por defecto: si no hay veredicto, la fila no se incluye y el parrafo "que se concluye" remite a la discusion.
- ¿El barrido de umbrales in-sample de §8.4 es "sensibilidad" (Anexo K) o aplicacion de la regla prerregistrada (cuerpo)? Por defecto: cuerpo.
- ¿La entrada de `CHANGES.md` la escribe `c-238` o la consolida `c-239`? Por defecto: `c-238` agrega su entrada y `c-239` la referencia.
- Titulo exacto del Anexo K ("Lecturas de sensibilidad y robustez" por defecto) y si conviene un parrafo de una linea en el Anexo J que remita al K.
