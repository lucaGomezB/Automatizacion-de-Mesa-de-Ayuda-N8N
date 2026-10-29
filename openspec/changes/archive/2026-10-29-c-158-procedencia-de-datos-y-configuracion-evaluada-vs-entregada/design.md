## Context

Ver `proposal.md` (Why). Verificacion previa hecha el 2026-10-28 sobre la rama `ramagonzalo` (HEAD `d186d73`, un commit por delante de `main` = `origin/main` = `d6a7c13`, que solo agrega el dictamen en `auditorias/`). Hechos que moldean el enfoque, cada uno con su fuente:

### C1. Corrida de correo y formulario web (2-10-2026, 119 casos)

- Fecha y resultado: `openspec/changes/archive/2026-10-09-c-68-corpus-ingesta-n8n/tasks.md:89` ("EJECUTADA (2026-10-02 ...) web 53/53 con valor, correo 66/66"). Hasta ese dia los 200 casos carecian de tiempo automatizado (`c-68 .../proposal.md:3`), de modo que ningun tiempo de la tesis proviene de un procesamiento de septiembre.
- Inyeccion: nadie reenvio ni cargo a mano. El arnes `scripts/corpus_ingest/ingest_via_n8n.py` envia por caso un correo SMTP nuevo al buzon dedicado (cuerpo = descripcion; `Message-ID: <corpus-<ID>@<dominio>>`) o un POST al webhook `incidente-web` de N8N (`c-68 .../design.md:52-65`; `scripts/corpus_ingest/README.md:198-213`).
- Texto: la fuente por defecto del arnes es el JSON pseudonimizado (`c-68 .../design.md:69`; `scripts/corpus_ingest/README.md:186`). El comando realmente usado el 2-10 no esta versionado (consulta Q4).
- Metrica: `tiempo_automatizado_s = t_e2e_s = persistido_en - t_envio`; en correo incluye la espera hasta la recogida del disparador IMAP (`c-68 .../design.md:33-45`; spec `corpus-n8n-ingest`).
- Disparador IMAP: `n8n/workflow.json:5-13` declara `pollTimes: everyMinute` (igual en `69b5328` y `24ab238`, 2-10-2026). El repositorio no contiene una medicion del intervalo efectivo y la exploracion paralela del coordinador advierte que en n8n 2.11.2 el parametro podria ser inerte (herencia del disparador Outlook, `c-39 .../design.md:10`). Se redacta como "configuracion declarada" y el intervalo efectivo queda como consulta (Q5).
- Configuracion del clasificador (commit `24ab238`, 2-10 20:59 -0300): `HYBRID_CACHE_VERSION = "hybrid-v1"` (`App/Backend/app/constants.py:33`), `deterministic_confidence_threshold = 0.90` (`settings.py:103`), `human_review_threshold = 0.70` (`settings.py:104`), `gemini-3.6-flash` (`settings.py:73`, desde `11036be`, 24-09-2026), vocabulario de 89 patrones y prompt sin REGLAS DE FRONTERA (`evaluation/data/sensibilidad_ajustes/procedencia.json`). Repetida fuera de linea sobre el corpus, esa logica resuelve por reglas 72 de 200 casos (Tabla 15, fila "Vocabulario y logica previos"; `c-71 .../proposal.md:7-9`, escalacion 64 %).
- Flujo N8N versionado ese dia: 38 nodos (35 operativos y 3 notas), con 3 nodos de agente LLM para telefonia; sin reintentos en el alta (`git show 24ab238:n8n/workflow.json`).

### C2. Corrida telefonica (concluida el 6-10-2026, 81 casos)

- Fecha: `openspec/changes/archive/2026-10-06-c-70-softphone-corpus-telefonia/tasks.md:96` ("REALIZADO (2026-10-06): 81/81 ... duplicado R126 limpiado"). Pero `c-71 .../tasks.md:71` (56 casos con tiempo nulo) y `c-72 .../proposal.md:7` (commit `4fedce8`, 5-10 21:50: "subconjunto telefonico medido (25 casos)") muestran que 25 casos ya estaban medidos al cierre del 5-10. El cronograma fecha el hito el 6-10 (fecha de conclusion).
- Procedimiento: softphone de navegador (C-59) con selector de caso; "El autor RECITA el texto del caso (sin reproduccion de audio)" (`c-70 .../proposal.md:9`; `design.md:51,75`); el texto mostrado es la descripcion del JSON pseudonimizado (`GET /corpus-cases`); grabacion acotada a 45 s (`n8n/twilio/twiml.xml:41-42`); perfil Compose `corpus` aislado (`postgres-corpus`, `backend-corpus`, `n8n-corpus`) con la Voice URL conmutada a mano (`c-70 .../design.md:71`). Quien recito no esta nominado (consulta Q3).
- Metrica original: `latencia_e2e_ms/1000`, desde el callback de grabacion (al colgar) hasta la persistencia (`c-70 .../design.md:16,55`).
- Configuracion: no es asignable a una sola revision. Los 25 casos del 5-10 se clasificaron con el agente LLM de N8N, que invocaba siempre al modelo y entregaba una clasificacion precalculada (`c-72 .../proposal.md:5-7`). c-71 (`1368fd8`, 5-10 21:50: vocabulario de 151 patrones, umbral 1,0, `hybrid-v2`, que cortocircuita 1/200, `c-71 .../tasks.md:70`) y c-72 (`a76851e`, 6-10 16:38: retira el agente, 38 a 28 nodos, agrega las reglas de frontera) son contemporaneos; el repositorio no registra la hora de las llamadas ni la imagen de `backend-corpus` ni el flujo importado en `n8n-corpus` (consultas Q1 y Q2). Todas las llamadas son anteriores a c-74 (`d6bb474`, 7-10 19:49).
- **Discrepancia con el dictamen**: la tabla de verificacion y la conclusion del dictamen afirman que ambas corridas usaron "la configuracion del clasificador anterior a c-71 y c-74". Es cierto para la corrida del 2-10 y para c-74 en ambas, pero no se sostiene para c-71 en la corrida telefonica, que concluyo despues de `1368fd8` y es contemporanea de c-72. La tesis describira exactamente lo que el historial sostiene.

### C3. Corrida de clasificacion (7-10-2026, fuera de linea)

- `evaluation/evidence/README.md:14-26` y `cache_meta` de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`: `classifier_version = hybrid-v3`, `generated_at = 2026-10-07T22:22:01Z`, `corpus_hash = 1fd17d7e...` (igual al `sha256` del corpus versionado vigente), 131 determinista / 69 Gemini. Es una ejecucion del framework sobre el corpus JSON, sin canales ni N8N.
- **Matiz 1 (no senalado por el dictamen)**: 22:22 UTC son las 19:22 -0300, 27 minutos ANTES del commit `d6bb474` (19:49:21 -0300). La corrida se hizo sobre el arbol de trabajo y `d6bb474` es la primera revision versionada que contiene `hybrid-v3` (`constants.py:43`). La tesis dira "la version `hybrid-v3`, que versiona el commit `d6bb474`", nunca "ejecutada sobre el commit".
- **Matiz 2 (no senalado por el dictamen)**: el hash `1fd17d7e...` corresponde a la version del corpus creada el 19-10 por `4602bf5` (la del 9-10, `8f7e6ec`, es `5f062e14...`). Entre ambas solo cambiaron los 81 `tiempo_automatizado_s` telefonicos y `metadata.descripcion` (verificado por diff de campos), no descripciones ni etiquetas; la `cache_meta` fue reasociada despues del 19-10 sin reclasificar. La tesis consignara el hash y aclarara que la entrada de la clasificacion no cambio; el modo de la reasociacion queda como consulta de registro (Q6).

### C4. Recalculo del tiempo telefonico (19-10-2026)

Commit `4602bf5` (c-77, grupo E; decision del autor del 2026-10-12): `tiempo_automatizado_s(telefono) = duracion_segundos + latencia_e2e_ms/1000`, porque la medicion original excluia la duracion de la llamada y el tiempo manual telefonico incluye escucharla (`openspec/changes/archive/2026-10-20-c-77-tesis-errores-estadisticos-inferenciales/proposal.md:64-82`; `design.md:169-200`). `duracion_segundos` se leyo del respaldo `backups/vol_mesa_local_postgres_corpus_data_20261009T141330.tgz` (no versionado). Correo y formulario no cambiaron. Coincide con el hito "Recalculo del tiempo telefonico (19/10/2026)" de `docs/diagrams/cronograma.md:41,72`.

### C5. Registros primarios del brazo automatizado

Versionado solo `data/corpus_evaluacion_pseudonimizado.json` (un `tiempo_automatizado_s` por caso, 200/200). El CSV versionado tiene 200 tiempos manuales y 0 automatizados (verificado). No versionados: sidecars `data/corpus_resultados*.json` (`.gitignore:66`), originales XLSX/CSV (`.gitignore:62-63`), `backups/` (`.gitignore:56`), caches de predicciones (`.gitignore:72-73`), bases de datos y ejecuciones de N8N. El sidecar de correo y formulario conserva solo 4/119 casos por un defecto de sobrescritura (`c-68 .../tasks.md:107`, "W2 ACEPTADO (no reparable)"). En esta copia de trabajo `backups/` solo tiene `.gitkeep`.

### C6. Configuracion evaluada frente a entregada (verificada con `git show`)

| Elemento | `d6bb474` (7-10-2026) | `v1.2.5` (28-10-2026, `e5508850`) | Cambio |
|---|---|---|---|
| FastAPI / Uvicorn | 0.115.0 / 0.30.6 | 0.162.0 / 0.54.0 | `e477c24` (19-10, c-97), `3876a7c` (22-10, c-127), `f666316` (27-10, c-149) |
| SQLAlchemy | 2.0.36 | 2.1.6 | c-127, c-149 |
| google-genai | `>=2.20.0` | `>=2.33.0,<3` | `0928df3` (19-10, c-64), c-127, c-149 |
| pytest / pytest-cov | 8.3.3 / 5.0.0 | 9.1.1 / 7.1.0 | c-97, c-127 |
| React (package-lock) | 18.3.1 | 19.3.1 | `84aa304` (23-10, c-128) |
| Flujo N8N | 28 nodos (25 + 3); 38 (35 + 3) hasta c-72 | 32 (29 + 3) | c-72, c-140 y otros |
| Reintentos del alta | no (`continueErrorOutput` sin `retryOnFail`) | 3 intentos, 5000 ms, 10 s / 75 s | c-140 (archivado 27-10) |
| Revision por reportante no identificado | no | si (VIS-005, `c-82 .../design.md:94-96`) | c-82 (archivado 13-10) |
| Prueba de humo E2E y TLS del borde | no | si; corrida 25/25 del 27-10 sobre `b4b3be9`, sin cambios de borde, flujo ni arnes hasta `v1.2.5` | c-140 |
| Sin cambios | N8N 2.11.2, Python 3.12-slim, PostgreSQL 15.5-alpine, `gemini-3.6-flash` y parametros (0,3 / 0,9 / 100 / 30 s / 60 s / 2 reintentos), umbrales 0,5166 y 0,70, vocabulario y prompt; la logica del clasificador solo cambio en comentarios e import perezoso | | |

Las dependencias no cambiaron entre `11036be` (24-09) y `d6bb474` (7-10), de modo que la columna evaluada rige para las tres corridas. La tesis no menciona MFA ni cifrado del directorio como rasgos evaluados; no se agregan filas para ellos.

### C7. Pasajes de la tesis afectados (leidos el 2026-10-28)

`01-introduccion.tex:76` (fecha "desde el 24-09-2026", que en realidad es la integracion de `gemini-3.6-flash`, `11036be`); `04-marco-metodologico.tex:61` (procesamiento "sobre la misma infraestructura ... con monitoreo continuo", sin respaldo); `05-arquitectura.tex:72,74`; `06-implementacion.tex:10,14,40,52,60,64,85,87,89` (React 19 en 89, ausente del inventario del dictamen); `07-resultados.tex:6`; `08-discusion.tex:10`; `11-aspectos-legales.tex:24`; `12-anexos.tex:21,27,66-68,96,115`; `Bibliography_base.bib:810-817`. El render `tesis_para_agente.md` coincide con las fuentes. Linea base de compilacion (orquestador, 2026-10-28): 106 paginas, 0 errores, 0 indefinidas, 26 Overfull; el Overfull de `12-anexos.tex:66` (106 pt, ruta del corpus) es "la linea que excede el margen" del Anexo F.

## Goals / Non-Goals

**Goals:**
- Declarar en 4.5, con remision al abrir 8, de donde sale cada conjunto de datos del brazo automatizado, con que configuracion y con que procedimiento, usando solo lo que el repositorio documenta.
- Corregir 1.8, 9.1, 6.4, la leyenda de la Figura 10 y el Anexo F en consecuencia.
- Distinguir en una tabla verificada la configuracion evaluada de la entregada y remitir a ella desde cada pasaje que cita versiones o capacidades posteriores a las corridas.
- Dejar trazables las consultas a los autores, sin texto inventado.

**Non-Goals:**
- No reejecutar corridas ni versionar registros que este clon no tiene (la decision de versionarlos es de los autores, Q7).
- No tocar las Figuras 1, 2, 4 y 5, las Tablas 5 y 8 ni la seccion 8.6 (c-159).
- No atender B5-B13 (residuos del proceso de correccion, naturaleza del Anexo I, seccion 10, "Capitulo 7" y "Anexo B" en 5.1, "linea 98" en 8.5, alcance del gate en 8.3, tratamiento del disparador por directorio en 2.4/5.5/7.5/Anexo H, glosario, bibliografia formal); quedan para un change posterior.
- No regenerar `cronograma.png` ni modificar el bloque Mermaid.
- No publicar tag ni release.
- No modificar numeros canonicos, `App/`, `openspec/config.yaml`, `requirements.txt` ni `docs/Tesis/v9 (IA)/`.

## Decisions

### D1. Forma del apartado de procedencia: encabezado de parrafo dentro de 4.5

Se usa `\paragraph{Procedencia de los datos del brazo automatizado.}` (nivel 4 de APA, en linea, sin numero ni entrada en el indice) al final de 4.5, y las remisiones apuntan a `\autoref{subsec:protocolo-pruebas}`. Alternativas: `\subsubsection` (RECHAZADA: crea un 4.5.1 solitario y una linea mas en el indice); seccion nueva (RECHAZADA: costo de pagina). Si `\paragraph` compila con espaciado anomalo bajo `titlesec`, el apply usa `\textbf{...}` en linea con el mismo texto y lo registra.

### D2. Contenido del apartado: borrador acotado a lo documentado

Presupuesto: <= 300 palabras. Borrador de referencia (el apply ajusta la redaccion y la acentuacion sin agregar hechos):

> Los datos del brazo automatizado provienen de tres corridas con configuraciones distintas del clasificador. Los tiempos de correo electronico y formulario web (119 casos) se midieron el 2-10-2026 con un arnes de ingesta que envio cada caso por el canal real del flujo N8N ---un correo nuevo al buzon dedicado o un envio al webhook del formulario--- con la descripcion pseudonimizada del corpus como texto; el tiempo de cada caso va desde el envio hasta la persistencia del incidente que registra el backend, de modo que en el correo incluye la espera hasta la recogida del mensaje por el disparador IMAP, configurado para sondear el buzon una vez por minuto. Ese dia regian el vocabulario original del filtro (89 patrones), el prompt sin reglas de frontera y el cortocircuito por confianza determinista >= 0,90 (version `hybrid-v1`), que, repetidos fuera de linea, resuelven por reglas 72 de los 200 casos (Tabla 15). Los tiempos telefonicos (81 casos) se midieron en una corrida concluida el 6-10-2026 en un entorno de medicion aislado: uno de los autores llamo desde un softphone de navegador y leyo en voz alta la descripcion pseudonimizada de cada caso, con la grabacion acotada a 45 s. Esa corrida no tiene una configuracion unica: 25 casos ya estaban medidos el 5-10, cuando la clasificacion telefonica la resolvia un agente LLM del flujo que invocaba siempre al modelo, y la ampliacion del vocabulario (c-71) y la unificacion de la clasificacion telefonica con la cascada del backend (c-72) son contemporaneas de las llamadas; todas son anteriores al criterio de cortocircuito evaluado (c-74). Las metricas de clasificacion provienen, en cambio, de una ejecucion fuera de linea del framework de evaluacion sobre el corpus JSON, generada el 7-10-2026 a las 22:22 UTC con la version `hybrid-v3` que versiona el commit `d6bb474` (evidencia `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, hash del corpus `1fd17d7e...`; la version del corpus con ese hash solo difiere en los tiempos telefonicos recalculados). El 19-10-2026 esos 81 tiempos se recalcularon sumando la duracion de la grabacion a la latencia posterior al cuelgue, que era lo unico que medía la corrida, para compararlos con el tiempo manual, que incluye escuchar la llamada. Como las corridas de tiempos invocaban al modelo con mas frecuencia que la configuracion evaluada en la clasificacion, los tiempos medidos no favorecen al flujo automatizado frente a ella; es una inferencia, no una medicion.

Marcadores `% PENDIENTE AUTORES` obligatorios en el `.tex` (comentarios, invisibles en el PDF): Q1 (inicio el 5-10 y horas), Q2 (version desplegada), Q3 (quien recito, una sola persona, consigna y entorno), Q4 (fuente y comando del arnes), Q5 (intervalo efectivo del disparador). "Uno de los autores" se sostiene en "el autor" de c-70 (`tasks.md:96`, `proposal.md:9`); el nombre no se escribe hasta Q3. La palabra "configurado" para el disparador expresa la configuracion declarada del flujo, no un intervalo medido.

La inferencia de direccion se apoya en: 2-10, Gemini en 128/200 frente a 69/200 de `hybrid-v3` (correo y web: 32/66 y 14/53 en `hybrid-v3` frente a 66,7 % y 73,6 % con la logica previa, `c-71 .../proposal.md:7-9`); telefonia, agente LLM (siempre), `hybrid-v1` (55,6 %) o `hybrid-v2` (1/200 cortocircuitos) frente a 23/81 en `hybrid-v3` (`c-72 .../tasks.md:53`). En todos los escenarios documentados el modelo intervenia mas.

### D3. Recordatorio en la seccion 8: parrafo propio tras la introduccion

Se agrega un segundo parrafo despues de `07-resultados.tex:6` (<= 70 palabras) que remite a 4.5 y separa tiempos (2-10 y 6-10, recalculo del 19-10) de metricas (7-10, `hybrid-v3`). La enumeracion del primer parrafo no cambia (requisito "Parrafo introductorio del capitulo de resultados coherente con sus subsecciones").

### D4. Seccion 1.8: conservar el dato del 24-09 y fechar las corridas

"(desde el 24-09-2026)" es cierto como fecha de integracion de `gemini-3.6-flash` (`11036be`; cronograma), pero se lee como inicio de la campana. Redaccion: "...reflejan el comportamiento de `gemini-3.6-flash`, integrado al clasificador el 24-09-2026 y vigente en las corridas del brazo automatizado del 2 y el 6 de octubre de 2026 y en la clasificacion fuera de linea del 7 de octubre (\autoref{subsec:protocolo-pruebas}), sujeta a ...". Mantiene el modelo dentro del periodo de la campana (requisito "Cronologia unica y fechada").

### D5. Seccion 9.1: la reduccion no se apoya en el 65,5 %

La oracion de `08-discusion.tex:10` pasa a: la reduccion se midio con la inferencia externa incluida y con configuraciones que invocaban al modelo con mas frecuencia que la evaluada en la clasificacion, cuya etapa determinista resuelve el 65,5 % de los casos (\autoref{subsec:protocolo-pruebas}); esa proporcion no interviene en la reduccion medida. Se conserva la cifra 65,5 % (requisito "Divulgacion de las etapas del pipeline incluida la etapa fallback"). El resto del parrafo (B5) no se toca.

### D6. Seccion 6.4 y leyenda de la Figura 10

- `06-implementacion.tex:52`: "desde el inicio de la llamada hasta la confirmacion del numero de incidente" se reemplaza por la suma de la duracion de la grabacion y la latencia desde el cuelgue hasta la persistencia del incidente (recalculo del 19-10, c-77), que es lo que el corpus registra. Inconsistencia hallada por la exploracion paralela y verificada; cae en A1 (condiciones de las llamadas).
- Figura 10 (`12-anexos.tex:21`): `\caption[Cronograma de la construccion, las campanas y la version del modelo]{...}` con la fuente desdoblada: historial del repositorio para los hitos (incluido el recalculo del 19-10-2026, c-77) y confirmacion de los autores del 9-10-2026 para las ventanas de las campanas. El titulo corto evita alargar el indice de figuras.

### D7. Anexo F: evidencia versionada, registros primarios y margen

- Las predicciones se remiten a `\path{evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json}` (copia versionada de la cache, que no se versiona).
- "Se incluyen ... los registros automaticos generados por el flujo automatizado" se reemplaza por: los tiempos automatizados se conservan por caso en el corpus JSON; sus registros primarios (marcas temporales del backend, archivos de trazabilidad de los arneses y ejecuciones de N8N) no estan versionados en el repositorio. "No se conservaron" solo se escribe si los autores lo confirman (Q7); hasta entonces, comentario `% PENDIENTE AUTORES`.
- Las rutas largas pasan a `\path{...}` (url.sty, cargado por hyperref), que corta en `/` y `_`; desaparece el Overfull de 106 pt. Para el CSV con espacios se usa `\texttt` o se lo nombra sin ruta (`\path` descarta espacios).
- Se modifica el requisito "Trazabilidad del corpus real en el anexo de validacion", que hoy exige `evaluation/predicciones.json`.

### D8. Ubicacion de la tabla: Anexo B; etiqueta `tab:configuracion-evaluada-entregada`

Criterio: minimizar paginas del cuerpo y maximizar remisiones. En el Anexo B (a) el cuerpo crece solo por remisiones breves; (b) no se renumeran las Tablas 1-18 del cuerpo, que el dictamen y c-159 citan por numero (5, 8, 15, 17, 18): solo pasan la del Anexo H (19 a 20) y la del Anexo I (20 a 21); (c) comparte contexto con la identificacion del tag y del hash y con la precision de D10. Alternativa 6.1 (RECHAZADA: renumera 14 tablas del cuerpo y agrega un flotante de media pagina al cuerpo). **c-159 debe usar `Tabla~\ref{tab:configuracion-evaluada-entregada}` (Anexo B) desde las leyendas de las Figuras 1 y 4.**

Forma: `table` [htbp], `\small`, `booktabs`, tres columnas `p{}` (Elemento | Configuracion evaluada | Configuracion entregada) con las filas de C6 (revision, clasificador, FastAPI/Uvicorn, SQLAlchemy, google-genai, pytest/pytest-cov, React, flujo N8N, reintentos del alta, revision por directorio, humo E2E, TLS del borde y una fila "Sin cambios" con `\multicolumn{2}`), y fuente "elaboracion propia a partir de `git show d6bb474:...` y `git show v1.2.5:...` y de los changes archivados". Solo valores verificados en C6; la columna entregada nombra el tag que consigna el Anexo B.

### D9. Remisiones uniformes

Regla: todo pasaje que cite una version o una capacidad posterior a las corridas declara a que configuracion pertenece y remite a la tabla. Concretamente:
- 5.4 (`05-arquitectura.tex:72`): "(versiones de la configuracion evaluada; Anexo~B, Tabla~\ref{...})"; cubre tambien google-genai de la linea 74.
- 6.1 (`06-implementacion.tex:10`): la enumeracion queda rotulada como configuracion evaluada y se agrega que la entregada actualiza backend y frontend (tabla).
- 6.2 (`:14`): se quitan "~0.115" y "0.30.6" (ya declarados en 6.1); compensa lineas.
- 6.3 (`:40`): el tercer disparador queda fechado: "(este ultimo, incorporado despues de las corridas; Tabla~\ref{...})". El tratamiento del disparador en 2.4/5.5/7.5/Anexo H es B8 y queda fuera; si el change de B8 lo retira de 6.3, retira tambien esta acotacion.
- 6.5 (`:60`): "En la configuracion entregada ---no en la evaluada (Tabla~\ref{...})---, el tramo de alta declara ...".
- 6.7 (`:85,87,89`): se quitan los numeros de version de pytest y pytest-cov con remision a la tabla; la prueba de humo se presenta como de la configuracion entregada; "React 19" pasa a "React" con remision.
- 7.4 (`11-aspectos-legales.tex:24`): remision tras la frase de TLS. 5.1 ya declara que la campana no incluyo el proxy y sus erratas ("Capitulo 7", "Anexo B") son B8: no se toca.
- Anexo H (`12-anexos.tex:96` y fila SDK de la tabla, `:115`): "`>=2.20.0` en la configuracion evaluada" con remision.

### D10. Anexo B: "commit definitivo"

`12-anexos.tex:27`: "creado sobre el commit definitivo del repositorio" pasa a "creado sobre el commit que fija el contenido de la version entregada; como un commit no puede contener su propio hash, la rama principal registra despues un commit que solo consigna esta linea, y los commits posteriores no modifican las fuentes de la tesis". Verificado: entre `v1.2.5` y `d6a7c13` solo cambian la linea del hash (`1aa35ef`), artefactos de compilacion, renders, `.engram/` y la reversion de `docs/Tesis/v9 (IA)` (`0b544fe`); el apply verifica de nuevo con `git diff --stat v1.2.5 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` y ajusta la frase si hubiera mas (tras aplicar c-158 la frase sigue siendo cierta respecto de `v1.2.5` solo hasta la proxima release: ver D11).

### D11. Bibliografia

`Gomez2026_repositorio`: titulo "(Versi{\'o}n 1.2.5)" y `urldate = {2026-10-28}`; el resto de los campos no cambia. Las releases `v1.2.3` a `v1.2.5` omitieron esta actualizacion, que el requisito vigente reserva al change de la release; se modifica el requisito para que el primer change documental que detecte el desfase lo realinee y lo registre. **La proxima release (la que publique c-158 y c-159) debe volver a actualizar la entrada, la columna "entregada" de la tabla y la frase de D10 en el mismo commit que cambia el tag del Anexo B (patron de dos commits).**

### D12. Anexo I, registro y cronograma

- Anexo I: un parrafo (no una tabla) tras la tabla del 22-10: el dictamen del 28-10-2026 sobre `v1.2.5`; A1 y A2 atendidas por c-158 con sus secciones. c-159 extiende el mismo parrafo con A3 y A4. La reestructuracion del anexo (B6) queda para el change de las observaciones B.
- `dictamen-correcciones.md`: seccion nueva "## Dictamen v10 / v1.2.5 (2026-10-28) - c-158" con trazabilidad observacion -> cambio -> archivo:linea, consultas Q1-Q8 como PENDIENTE, discrepancias con el dictamen y fila del libro mayor de paginas (prevision declarada +1 a +2).
- `docs/diagrams/cronograma.md`: se agregan a "Anclas que no se dibujan" c-72 (6-10, `a76851e`) y la clasificacion `hybrid-v3` (7-10, 22:22 UTC), y a "Coherencia" la nota de los 25 casos del 5-10 y el cierre parcial de OQ-2 (sin tiempos antes del 2-10). El bloque Mermaid no cambia.
- `conteos-canonicos-tecnicos.md`: seccion "Configuracion evaluada frente a entregada (c-158)" con cada valor de la tabla y su comando de verificacion; la fila del SDK (`>=2.20.0,<3`, que no corresponde a ninguna de las dos revisiones) se anota como superada sin borrarla.
- `CHANGES.md`: si c-155, c-156 y c-157 no tienen entrada (hoy no la tienen y la linea Total aun dice "c-155 en aplicacion"), se registran como regularizacion (FASE 47, formato de la FASE 46), exigencia del requisito "Coherencia del indice de changes con el archivo de changes"; c-158 abre la FASE 48 "Correcciones de la tesis por el dictamen CONEAU v10/v1.2.5", a la que c-159 agrega su entrada. Se actualizan las lineas Total, Fases, numeracion y release vigente (`v1.2.5`).

## Risks / Trade-offs

- [Afirmar un hecho no documentado (quien llamo, intervalo efectivo, version desplegada)] -> Solo se redacta lo citado en Context; lo demas va en `% PENDIENTE AUTORES` y en el registro. Verificacion: cada oracion nueva tiene su fuente en la seccion del registro.
- [Aumento de paginas (106 actuales, tope 100 con exceso defendido)] -> Tabla en anexo, apartado <= 300 palabras, eliminacion de versiones redundantes en 6.2 y 6.7, titulo corto de la Figura 10. Si el total supera 108, compensar con palancas de forma ya usadas (espaciado de tablas del anexo) y registrar.
- [Nuevos Overfull por rutas largas] -> `\path{}` en toda ruta nueva; el apply compara el conteo con la linea base de 26.
- [Referencias indefinidas al reordenar] -> Solo se agrega la etiqueta de la tabla; el apply exige 0 `undefined` y 0 `??`.
- [Que c-159 edite los mismos archivos] -> c-158 se aplica primero; las zonas de c-159 (Figuras 1/2/4/5, Tablas 5 y 8, 8.6) no se tocan.
- [Que los autores respondan algo distinto de lo inferido (por ejemplo, que la telefonia empezo el 5-10)] -> Las tareas de cierre de marcadores preven ajustar 1.8, 4.5, Figura 10 y el cronograma con la respuesta.
- [Falso positivo de gitleaks por la palabra "capitulo" seguida de coma y una ruta] -> Revisar el diff con la regla `generic-api-key` antes del commit y reformular si aparece.

## Migration Plan

1. Verificacion previa (grupo 1 de `tasks.md`).
2. Edicion de las fuentes por bloques (A1, conexas, A2, Anexo B y bibliografia).
3. Render, compilacion Docker, `verify_citations.py`, Anexo I, registro, memo, cronograma y `CHANGES.md`.

Rollback: `git checkout --` de los archivos editados (sin efecto en runtime). No hay migracion ni release.

## Open Questions

Consultas a los autores (no bloquean el apply; cada una deja un marcador `% PENDIENTE AUTORES` y una entrada PENDIENTE en el registro):

- **Q1 (fechas)**: la corrida telefonica, ¿comenzo el 5-10 (25 casos medidos segun c-71 y c-72) y concluyo el 6-10? ¿A que horas? Si se confirma, 1.8, 4.5, la leyenda de la Figura 10 y el cronograma pasan a "5 y 6 de octubre".
- **Q2 (version desplegada)**: ¿que imagen de `backend-corpus` y que flujo importado en `n8n-corpus` procesaron los 56 casos del 6-10: anteriores o posteriores a c-71 (`1368fd8`) y a c-72 (`a76851e`)?
- **Q3 (quien y como)**: nombre de quien recito las 81 llamadas; si fue una sola persona; si leyo la descripcion tal como la mostraba el softphone; dispositivo, microfono, red y entorno; repeticiones ademas de R126 y R002.
- **Q4 (arnes)**: quien ejecuto `ingest_via_n8n.py` el 2-10, con que flags (en particular `--source`, por defecto `json`), contra que stack y que `--base-url` (por defecto nginx, `scripts/corpus_ingest/README.md:183`), y el host SMTP usado.
- **Q5 (disparador IMAP)**: intervalo efectivo de recogida del buzon en la instancia del 2-10 (el flujo declara `everyMinute`; ¿hubo recogida inmediata por eventos IMAP?).
- **Q6 (registro)**: como paso la `cache_meta` de `hybrid-v3` al hash `1fd17d7e...` del corpus del 19-10 sin reclasificar. No cambia la tesis.
- **Q7 (registros primarios)**: ¿se conservan fuera del repositorio la base operativa con los incidentes del 2-10, el respaldo del 9-10 con los 81 ingresos, los sidecars y las ejecuciones de N8N? Si se conservan, ¿se versiona una exportacion pseudonimizada (id de caso y marcas temporales)? Si no, confirmar "no se conservaron" para el Anexo F.
- **Q8 (proxy)**: la tesis (5.1, 7.4, Anexo A) dice que el despliegue de la campana no incluyo el proxy, pero el arnes lee por defecto a traves de nginx (`https://localhost`); ¿estaba activo nginx el 2-10 (fuera del tramo medido)? No cambia la tabla ("sin TLS verificado").

Fuera de alcance, para un change posterior: `openspec/specs/telefonia-corpus-medicion/spec.md:47-52` y `docs/medicion-latencia-e2e.md:72-91` conservan la formula telefonica previa a c-77; `docs/medicion-latencia-e2e.md:55-58` dice que el correo "sub-mide", cierto para `latencia_e2e_ms` pero no para el valor del corpus.
