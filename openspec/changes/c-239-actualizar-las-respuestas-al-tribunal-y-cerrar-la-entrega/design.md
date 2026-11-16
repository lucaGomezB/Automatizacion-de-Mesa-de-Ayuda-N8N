## Context

- **Fuente.** Devolucion de tercera instancia del tribunal (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`, hoy sin trackear junto con su PDF): 12 observaciones (K-01, K-02 criticas; A-01 a A-03 altas; M-01 a M-04 medias; B-01 a B-03 bajas), apta para defensa **condicionada a K-01 y K-02**, y 12 preguntas probables en su Seccion 8. La seccion 7 cierra con: la defensa se evaluara "sobre el ejemplar corregido y sobre las respuestas del grupo a la Seccion 8"; la Seccion 8 agrega que las 16 respuestas de segunda instancia "siguen vigentes, una vez actualizadas segun M-04".
- **Decision de los autores (2026-11-16).** K-01 se resuelve por **retiro** de la validacion fuera de muestra. Insumo de un autor sobre K-02: las descripciones del corpus independiente eran descripciones genericas de incidentes, no incidentes extraidos de una compania; aun no se sabe como se produjeron las etiquetas y marcas temporales de `E3`, `E4` y `E5`.
- **Orden de aplicacion.** `c-235` (retiro; nota de versiones I.1; K-01, K-02, A-02/B-02 no aplica, M-02 por acotacion) -> `c-236` (balance como cota superior con termino de revision; umbral del 85 % a priori; A-01, M-01) -> `c-237` (declaracion completa de IA en I.2; A-03) -> `c-238` (legibilidad; M-03, B-01, B-03) -> **`c-239`** (este). Al proponer este change, `c-235` a `c-238` se estan proponiendo en paralelo (ninguno aplicado): este diseno fija el contrato con sus salidas, no sus valores. Fronteras ya declaradas por ellos: `c-236` no toca `respuestas-tribunal.md`, la version, la compilacion final ni el tag; `c-237` retira la declaracion de IA de `12-anexos.tex:241`, crea la subseccion `subsec:declaracion-uso-ia`, el inventario `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (su seccion 6 es el texto fuente de Q16) y el script `contar_uso_asistentes.py`, y encarga a `c-239` re-ejecutarlo sobre la ref de la entrega; `c-238` crea el Anexo K de sensibilidad, fija el metodo unico de conteo (D6: prosa limpia `A`, `wc -w` crudo `B`, paginas `C`; linea base `v1.5.2`: 43.241, 50.532, 164) y de oraciones largas (D4: `sent_c197.py`, 40 frente a 85 del tribunal), compila solo en un directorio temporal y deja `main.pdf` y `compilacion.md` a `c-239`; agrega su propia entrada en `CHANGES.md`.
- **Estado verificado del documento de respuestas** (`docs/defensa/respuestas-tribunal.md`, 139 lineas, creado por `c-198`): encabezado que responde solo a la segunda instancia sobre `v1.2.18` (L3); Q14 (L115-121) con balance `-18,5` a `-43,9` h-p y restos `~\%`, `{,}`; Q15 (L125-131) con "119 casos" de texto y "81" de audio; Q16 (L133-139) con la declaracion de IA que `c-237` reemplaza. Restos de LaTeX tambien en Q1, Q2, Q3, Q5, Q10, Q12, Q13. Las remisiones mezclan numero de archivo y numero de capitulo: el orden de `main.tex` es `01`..`06` = cap. 1..6, `11-aspectos-legales` = cap. 7, `07-resultados` = cap. 8, `08-discusion` = cap. 9, `09-conclusiones` = cap. 10, `10-recomendaciones` = cap. 11; Q8 y Q15 citan "11-aspectos-legales.tex (subseccion 11.3)" para el §7.3 del PDF.
- **Loci de version (hoy `1.5.2`)**: `00-portada.tex:31`; `Bibliography_base.bib:919` (titulo de `Gomez2026_repositorio`); `12-anexos.tex:58` y `:62` (Anexo B); `paper/compilacion.md:8`. Otras coincidencias de `1.5.2` en `docs/campana-medicion/guia-ejecucion-campana.md` son numeracion de apartados, no version.
- **Derivados desactualizados**: `docs/Tesis/tesis_ultima_version.pdf` y `README.md:7` declaran `v1.4.1` (commit `00333ce`); `tesis_para_agente.md` se regenero por ultima vez en `c-207`; los extractos `.txt`, en `c-199/c-200`. `knowledge-base/11_evaluacion_experimental.md` y `knowledge-base/README.md` declaran la release `v1.2.0` y la primera menciona "fuera de muestra".
- **Registro**: `docs/Tesis/Correcciones/dictamen-correcciones.md` (6340 lineas; ultima matriz `C29/...` de `c-234`; la tabla de c-196 da N-07 y N-15 como "cerrada", L4530 y L4538, mientras la tercera instancia las declara "Parcial"). `verificar_matriz_trazabilidad.py` exige al menos una fila de matriz en toda seccion `## Dictamen ...` que nombre un change >= 190. `CHANGES.md`: c-227 a c-234 bajo "Cambios propuestos — mejoras estructurales" con encabezados `### [C-2xx] ...`; lineas "Actualizacion <fecha> (...)" en "Notas del analisis".
- **Changes activos cuyas premisas se retiraron**: `c-228` (anclaba en `0,6893` = `142/206`), `c-230` (referencia `E3`/`E4`/`E5` sobre 206 casos), `c-232` (depende de `c-228`), `c-229` (muestreo probabilistico; citaba `0,7489`, que es fuera de muestra; la tesis remite a su diseno en `09-conclusiones.tex` como remedio condicional). 0 tareas aplicadas en los cuatro. Los cuatro fueron reformulados el 16/11/2026 por indicacion de un coautor (seccion «Adaptacion a la devolucion de tercera instancia» de cada uno).
- **Restricciones**: espanol sin emojis; solo alias (`E1`..`E5`, `O1`, `O2`, "los autores", "el director"), nunca nombres reales; cero llamadas a Gemini; no tocar `App/`, `n8n/`, `evaluation/`, `data/` ni `.engram/`; no commitear, taguear ni pushear sin OK expreso de los autores.

## Goals / Non-Goals

**Goals:**
- Dejar `docs/defensa/respuestas-tribunal.md` coherente con el ejemplar corregido (M-04) y con respuestas escritas a las 12 preguntas de tercera instancia, sin una sola afirmacion de procedencia, autorizacion, autoria o verificacion que los autores no hayan confirmado.
- Verificar mecanicamente que cada cifra del documento existe en el ejemplar corregido.
- Asentar la trazabilidad de las 12 observaciones de tercera instancia y el estado final de N-07 y N-15.
- Cerrar la entrega con la version identificable, la compilacion verificada, los derivados regenerados y el registro al dia, con el checklist de las dos condiciones del tribunal antes de pedir el tag.

**Non-Goals:**
- Redactar las correcciones de fondo del ejemplar (son de `c-235` a `c-238`); si al aplicar se detecta que falta una, se reporta y no se corrige aqui.
- Acreditar la procedencia del corpus retirado o redactar por los autores las respuestas de procedencia y autoria.
- Reintroducir, recalcular o resumir la validacion fuera de muestra.
- Ejecutar `c-228`, `c-229`, `c-230` o `c-232`: tras su adaptacion son posteriores a esta entrega; aqui solo se registra el destino que confirmen los autores.

## Decisions

### D1. Aplicar al final y tomar las cifras de las salidas de c-235 a c-238

El grupo 0 verifica con `openspec list --json` y `openspec status` que `c-235` a `c-238` estan aplicados (o archivados) y lee sus salidas: texto vigente de la nota de versiones I.1 y del §7.3 (`c-235`), cifras del balance y su seccion del memo (`c-236`), declaracion de IA en `subsec:declaracion-uso-ia` e inventario con su texto fuente para Q16 (`c-237`), metodo y lineas base de conteo, tabla primaria del cap. 8 y Anexo K (`c-238`). Si alguno no esta aplicado, el change se detiene en el grupo 0. **Alternativa descartada:** redactar ahora con las cifras previstas (`~+18,7` h-p, `r = 22,06 s`): violaria la regla de que las cifras finales las fija `c-236` y obligaria a un segundo pase.

### D2. Estructura del documento: Q1-Q16 conservadas y P1-P12 en una parte nueva

Se conserva la numeracion Q1 a Q16 (la exige la spec y el tribunal dice que esas respuestas "siguen vigentes") y se agrega una segunda parte "Devolucion de tercera instancia (16-11-2026)" con P1 a P12 en los cuatro bloques de la Seccion 8. El prefijo P evita colisiones con Q y permite marcas `PENDIENTE-AUTORES(Pn)` inequivocas. Encabezado: nombra ambas devoluciones y la version del ejemplar cotejado. **Alternativas:** renumerar Q17-Q28 (mezcla dos instancias en una serie y rompe la spec de 16 respuestas) o un documento separado (duplica nota de alcance y fuentes; el tribunal habla de "las respuestas del grupo" como un todo).

### D3. Compuerta de autores con marcas y un borrador que no afirma

P1 a P5, P11 y P12 se redactan como borrador limitado a lo que dice el ejemplar corregido ("la validacion fuera de muestra se retiro del ejemplar; vease la nota de versiones del Anexo I.1") seguido de `PENDIENTE-AUTORES(Pn): <dato que falta>`. El insumo de los autores se registra por escrito (fecha y texto) en el inventario `PENDIENTE-AUTORES` de la seccion de `c-239` en `dictamen-correcciones.md` antes de redactar la respuesta definitiva; cada afirmacion de la respuesta debe poder senalarse en ese insumo o en el ejemplar. El insumo ya dado por un autor sobre K-02 (descripciones genericas, no incidentes de una compania) **no se usa como hecho** hasta que (a) los autores lo confirmen por escrito y (b) coincida con lo que declara la nota de versiones de `c-235`: si contradice lo que la tesis afirmaba, la respuesta debe decirlo sin eufemismos. Patron heredado de `c-198` (`% PENDIENTE-AUTORES(Q1)`). Q14, Q15, Q16 y P6 a P10 no son compuerta: se derivan del ejemplar corregido. **Alternativa descartada:** dejar las preguntas bloqueadas sin texto; el tribunal pide una respuesta escrita por pregunta y el borrador acotado ya responde la parte verificable (que se retiro y por que).

### D4. Cotejo de cifras con script probado (Strict TDD)

Se crea `docs/Tesis/Correcciones/cotejar_cifras_respuestas.py` (solo lectura, biblioteca estandar) y `test_cotejar_cifras_respuestas.py`, siguiendo el patron del repo (`verificar_matriz_trazabilidad.py`, `resumir_registro_compilacion.py`, `recontar_errores_frontera.py`, cada uno con su `test_*.py`). Contrato:
- **Entrada:** `--respuestas docs/defensa/respuestas-tribunal.md`, `--ejemplar "docs/Tesis/v10 (IA)/tesis_completa_extraida.txt"` (regenerado desde el PDF de cierre), `--lista-blanca docs/defensa/cotejo-lista-blanca.tsv` (cifra, justificacion; p. ej. fechas de la devolucion o cifras citadas de la propia devolucion al enunciar la pregunta).
- **Extraccion:** cifras con coma decimal, enteros de 2 o mas digitos, porcentajes, fracciones `a/b`, signo `-`/`−`/`+`; se excluyen el texto entre comillas invertidas (rutas, identificadores), los encabezados `Qn`/`Pn`, los alias (`E1`, `O2`) y los numeros de seccion precedidos de `§` o "subseccion" (se verifican aparte en la tarea de remisiones).
- **Normalizacion:** `{,}` -> `,`; `−` -> `-`; espacios finos y no separables; `2.646` y `2646` equivalentes.
- **Fallas:** cifra ausente del ejemplar y de la lista blanca; cifra de la lista de retirados (`0,6893`, `142/206`, `0,7489`, `0,7024`, `-18,5`, `-43,9`, `+30,6`, `206`, `56`) en una oracion sin las palabras "retir" o "super"; restos LaTeX (`~\%`, `{,}`, `\texttt`, `\ref`). Codigo de salida 0 solo sin fallas.
- **Por que codigo y no `rg` manual:** son ~120 cifras en 28 respuestas y el cotejo se repite al menos dos veces (tras reescribir y tras regenerar el extracto final); un script probado hace reproducible la verificacion que exige M-04. **Alternativa descartada:** ampliar `verificar_matriz_trazabilidad.py` (otra responsabilidad: filas de matriz contra `.tex`).

### D5. Remisiones con la numeracion de capitulos del PDF

Toda linea "Fuentes:" usa "§N.M" segun el PDF y el archivo `.tex` real, con la tabla de correspondencia de Context. Se verifica contra el indice del PDF de cierre (o `main.toc`). Corrige Q8, Q9 y Q15, que hoy citan numeros de archivo como si fueran de capitulo.

### D6. Trazabilidad en una seccion `## Dictamen v10 / v1.5.2 (2026-11-16) - c-239`

Encabezado `## Dictamen ...` (no `###`) porque es una devolucion nueva del tribunal, como la de c-196; asi `verificar_matriz_trazabilidad.py` exige su matriz. Matriz `T3/...`: una fila por observacion como minimo, con el change que la atendio y un fragmento tomado del texto final de `c-235`..`c-238`. A-02 y B-02 (y M-02 si `c-235` la cierra por acotacion) llevan estado "no aplica por retiro (c-235)" con fragmento del texto que declara el retiro. N-07 y N-15: filas nuevas con su estado final (cerradas por `c-238` si M-03 y B-01 quedan atendidas) y las filas de c-196 (L4530, L4538) conciliadas: se agrega "SUPERADA por c-239" o se anota el cierre, sin borrar historia. Incluye el inventario `PENDIENTE-AUTORES` (P1-P5, P11, P12), el checklist de condiciones (D9) y el libro mayor de paginas y palabras (D8). El Anexo I.2 (`12-anexos.tex:239`) agrega la devolucion de tercera instancia del 16-11-2026 en la misma oracion de las revisiones previas (`c-237` retira la declaracion de IA de L241 y la traslada a la subseccion nueva `subsec:declaracion-uso-ia`; este change no la redacta).

### D7. Version propuesta `v1.6.0`, decidida por los autores

El retiro de una familia de evidencia (validacion fuera de muestra) y el cambio de lectura del balance alteran el contenido sustantivo, no solo la forma: se propone subir el componente menor (`v1.5.2` -> `v1.6.0`), como se hizo de `v1.4.x` a `v1.5.0`. La decision es de los autores (OQ1); los loci a repuntar son los cuatro de Context. **Alternativa:** `v1.5.3` (sugiere correccion menor y subrepresenta el retiro).

### D8. Conteo de paginas y palabras con el metodo unico de c-238

Paginas: `\@abspage@last` via `compilacion.md`, mas la pagina de inicio de los anexos (`main.toc`). Palabras del cuerpo: se **reusa** el metodo unico de `c-238` (D6: `A` = prosa limpia con la regla D1 de `sent_c197.py` sobre `01` a `11`; `B` = `wc -w` crudo de los mismos fuentes; `C` = paginas), con su linea base `v1.5.2` (43.241; 50.532; 164), y se aplica a la compilacion de cierre. El tribunal no publica su metodo (~51.900 palabras sobre `v1.5.2`); como lectura de comparacion se agrega `pdftotext -layout` del `main.pdf` de `v1.5.2` y del de cierre, desde la primera pagina del Capitulo 1 hasta la anterior a "Anexos"; se informan las tres cifras, la variacion relativa entre versiones (comparable con cualquier metodo constante) y la diferencia con la del tribunal, sin afirmar que se reproduce su metodo. Oraciones de mas de 60 palabras: `sent_c197.py` y `list_long_c197.py` segun D4 de `c-238` (40 frente a 85 del tribunal en `v1.5.2`). **Alternativa descartada:** un metodo propio nuevo; dejaria dos series de conteo incompatibles con la de `c-238`.

### D8b. Re-ejecucion del inventario de uso de asistentes (c-237)

`c-237` encarga a `c-239` re-ejecutar `contar_uso_asistentes.py` sobre la ref de la entrega. Como los commits de la propia entrega alteran el conteo, se fija la ref como **el commit inmediatamente anterior al commit de contenido de la entrega** (declarada en el inventario y en el Anexo I); si las cifras cambian frente a las de `c-237`, se actualizan el inventario y la subseccion `subsec:declaracion-uso-ia` antes de recompilar. **Alternativa descartada:** contar sobre el tag (circular: el commit de contenido y el del hash cambiarian el valor que el propio PDF imprime).

### D9. Checklist de condiciones antes del tag y gobernanza ALTA

Antes de pedir el tag se registra el checklist: K-01 (busquedas sin coincidencias de `0,6893`, `142/206`, `206 casos`, `fuera de muestra` como evidencia en Resumen, Abstract, §1.7, cap. 8 a 10, tabla de balance, Anexo J y Anexo K de `c-238`; mencion solo en la nota de versiones I.1) y K-02 (§7.3 con todas las transferencias; textos de la tercera organizacion fuera de la tesis; destino en el repositorio publico segun lo decidido en `c-235`), mas "comunicado al director" como dato de autores. Patron de release: commit de contenido con el bump y la recompilacion -> **CHECKPOINT ALTA** -> tag anotado sobre ese commit -> commit siguiente que consigna el hash en el Anexo B, recompila y regenera derivados y copia; `tesis_ultima_version.pdf` debe ser byte a byte el `main.pdf` de ese commit siguiente (asi lo verifico el tribunal para `v1.5.2`). Ningun commit, tag ni push sin OK expreso de los autores.

### D10. Derivados y documentacion

`build_tesis_para_agente.py <version>` para `tesis_para_agente.md` (determinista); `pdftotext` UTF-8 del PDF de cierre para `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt` (saltos de pagina = paginas); copia de `main.pdf` a `docs/Tesis/tesis_ultima_version.pdf`; `README.md:7` a la version nueva. `knowledge-base/`: la spec `project-documentation` ("Sincronia de la base de conocimiento con la release publicada de la tesis") exige valores identicos al memo, sin valores retirados como vigentes; se actualiza la release declarada y se retira o rotula como retirada toda cifra fuera de muestra, solo si difiere del memo vigente tras `c-235`.

### D11. Destino de c-228, c-229, c-230 y c-232: adaptados; registrar lo que confirmen los autores

La recomendacion inicial de este change era archivar sin aplicar `c-228`, `c-230` y `c-232` y reformular `c-229`. El 16/11/2026 un coautor indico que corresponde adaptarlos, y los cuatro se reformularon ese dia: sin cifras ni artefactos retirados como ancla, con compuerta de procedencia (K-01) y compuerta etica y legal (K-02) para todo dato nuevo, y fuera del ejemplar que se defiende. Orden de ejecucion, posterior a esta entrega: `c-229`, `c-230`, `c-228`, `c-232`. La devolucion no exige esa evidencia (la validacion fuera de muestra "no fue exigida por este tribunal") y atribuye la baja de la nota a evidencia nueva que no pudo acreditar; por eso el default es no ejecutar ninguno antes de la defensa. OQ2 queda como la confirmacion de los tres autores de ese destino; si alguno no se confirma, se archiva con el precedente de C-67 ("NO REALIZADO", `--skip-specs`). Se refleja en `CHANGES.md`.

## Risks / Trade-offs

- [`c-235`..`c-238` aplicados de forma parcial o con cifras distintas de las previstas] -> D1: el grupo 0 lee sus salidas reales y se detiene si falta alguno; el cotejo (D4) detecta cifras sin respaldo.
- [Presion por cerrar P1-P5 sin insumo] -> D3: las marcas `PENDIENTE-AUTORES` bloquean el tag (D9 incluye "inventario sin pendientes o pendientes declarados al tribunal"); ninguna respuesta afirma hechos no confirmados.
- [El insumo de los autores sobre K-02 contradice lo que la tesis afirmaba del corpus] -> la respuesta lo declara de forma directa, coherente con la nota de versiones; es la unica lectura honesta y la que el tribunal pidio ("si alguno fue construido o reconstruido, debe declararse").
- [Falsos positivos del cotejo (cifras de la propia pregunta del tribunal, fechas)] -> lista blanca versionada con justificacion por entrada; pruebas con casos de enunciado.
- [El metodo de palabras no reproduce la cifra del tribunal] -> D8: se informan ambas y la diferencia; la variacion relativa entre versiones sigue siendo comparable.
- [Nombres reales en la devolucion transcripta] -> las respuestas usan solo alias; una busqueda de los nombres de la ficha del tribunal forma parte de la verificacion de cierre.
- [La devolucion y su PDF estan sin trackear] -> se versionan en el commit de contenido de la entrega, solo con OK de los autores (contienen nombres reales: decision de autores, OQ5).

## Migration Plan

1. Grupo 0: precondiciones (c-235..c-238 aplicados), linea base y decisiones OQ1-OQ5 de los autores.
2. Cotejo con TDD; reescritura de Q1-Q16; P6-P10; borradores de P1-P5, P11, P12.
3. Trazabilidad y Anexo I.2.
4. Bump, recompilacion, conteos, derivados, README, knowledge-base, CHANGES.
5. Checklist de condiciones; CHECKPOINT ALTA; tag y commit del hash solo con autorizacion.
Reversion: todo es texto versionado; antes del tag basta `git restore`; despues, el tag no se mueve y una correccion va en una version siguiente.

## Open Questions

- **OQ1.** Numero de version de la entrega: `v1.6.0` (recomendado) o `v1.5.3`.
- **OQ2.** Confirmacion por los tres autores del destino de `c-228`, `c-229`, `c-230` y `c-232`: adaptados y posteriores a la entrega (D11), o archivar.
- **OQ3.** Insumo escrito de los autores para P1-P5 (quienes son `E3`/`E4`/`E5` respecto de la compania y de los autores; como se produjeron las marcas temporales y los textos del refuerzo; existencia de autorizacion; correspondencia de sectores), P11 (que produjeron los asistentes de IA y como se verifico cada cifra; debe coincidir con `c-237`) y P12 (distribucion del trabajo de la ultima version entre los tres autores).
- **OQ4.** Si quedan pendientes de autores al momento del tag: ¿se corta la entrega con P marcadas como pendientes y declaradas al tribunal, o se espera el insumo?
- **OQ5.** Versionar en git la devolucion de tercera instancia (`.md` y `.pdf`, con nombres reales en la ficha), como se hizo con la de segunda instancia, o mantenerla fuera del repositorio publico.
- **OQ6.** Comunicacion al director de K-01 y K-02 resueltas: fecha y medio, para el checklist (dato de autores).
- **OQ7.** `knowledge-base/11_evaluacion_experimental.md` declara la release `v1.2.0`: ¿se actualiza a la version nueva completa (alcance mayor) o solo se retiran las cifras fuera de muestra y se rotula la release?
