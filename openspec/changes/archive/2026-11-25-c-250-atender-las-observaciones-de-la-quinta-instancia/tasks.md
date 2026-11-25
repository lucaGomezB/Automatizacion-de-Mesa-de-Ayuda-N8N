# Tasks: Atender las observaciones de la quinta instancia del tribunal

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`D/` = `auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md`; `E/` = `evaluation/data/campana/analisis/`.
Lineas de `main` v1.6.4 (tag `v1.6.4`), iguales a las de `S/`; el apply las re-verifica con `rg`
antes de editar, porque las ediciones las desplazan. **Mapa archivo→capítulo (obligatorio):** Ch4=
`04-marco-metodologico.tex`, Ch7 (legal)=`11-aspectos-legales.tex`, Ch8=`07-resultados.tex`, Ch9=
`08-discusion.tex`, Ch10=`09-conclusiones.tex`, Anexos=`12-anexos.tex`; el nombre del `.tex` no es el
número rendido. Equivalente de Strict TDD para prosa: cada tarea de edición corre una verificación
ANTES (muestra el defecto) y DESPUES (estado deseado), ambas registradas en `C/dictamen-correcciones.md`
sección `c-250`. Reglas: no commitear, taggear ni pushear sin pedido expreso; no cambiar cifras
canónicas, citas ni conclusiones sin ratificación de autores; español rioplatense formal sin emojis;
solo alias (`E1`, `E2`, `O1`, `O2`, `A1`, `T1`), nunca nombres reales ni la correspondencia
alias-identidad; no tocar `App/`, `n8n/`, los artefactos existentes de `evaluation/` ni los casos ni
los JSON del corpus. Dominio HIGH (`S/11-aspectos-legales.tex`, `docs/seguridad/`, `data/README.md`,
grupo de release): mostrar el texto propuesto a los autores antes de escribir. Gobernanza del change:
MEDIUM. Las decisiones de las cinco compuertas (OQ-01 a OQ-05) están RESUELTAS por los autores y
registradas en la tabla de decisiones de la sección c-250; NO hay hechos pendientes de confirmar.

## 1. Guardas y línea base

- [x] 1.1 Leer `proposal.md`, `design.md` (D1-D10, OQ-01 a OQ-05 cerradas), los dos deltas de
  `specs/` y `D/` completo (dictamen, C-01 a C-07, preguntas 1 a 10). Verificación:
  `git rev-parse v1.6.4^{commit}` coincide con el commit de `main` y
  `git diff --stat v1.6.4 HEAD -- "docs/Tesis/v10 (IA)" data` vacío (las líneas del dictamen siguen
  vigentes) o, si no, lista de desplazamientos registrada.
- [x] 1.2 Línea base de cifras canónicas y conteos. Verificación: `rg -c "61,6|17,76|71,2|73,5|W = 363|0,6508|87,2|20,09|77,0|165,3" S/`
  y el conteo de palabras de prosa del Resumen y del Abstract (regla `tesis-document`), registrados
  en la sección c-250.
- [x] 1.3 Registrar `git rev-parse v1.6.2^{commit}`, `git rev-parse v1.6.3^{commit}`,
  `git rev-parse v1.6.4^{commit}` y `sha256sum data/corpus_evaluacion_pseudonimizado.json
  data/corpus_resultados_telefonia.json data/corpus_resultados_web_correo.json` como valores que el
  apply MUST NOT cambiar.
- [x] 1.4 Red de seguridad: `python "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS;
  `pytest "docs/Tesis/v10 (IA)" E/` en verde (conteo registrado); `openspec validate --all --strict`
  sin fallos. Si algo falla antes de editar, se reporta como falla preexistente y no se corrige aquí.

## 2. Registro de decisiones resueltas

- [x] 2.1 Registrar en la sección c-250 de `C/dictamen-correcciones.md` la tabla de decisiones con las
  cinco compuertas CERRADAS: OQ-01 (campaña real en octubre 2026), OQ-02 (componente de carga no
  existe), OQ-03 (sin originales con identificadores; notificación verbal 2026-09-30; arts. 2 y 28),
  OQ-04 (sin empleadores reales; art. 10; no hay aval del director), OQ-05 (sin IA en las 119;
  atribución unificada; domicilio aclarado). Cada fila: decisión literal, fecha y responsable.
  Verificación: las cinco filas existen y no queda ninguna compuerta "EN CURSO".

## 3. C-01 - Cronología en octubre 2026, propagada al corpus vigente

- [x] 3.1 `S/04-marco-metodologico.tex:14` (§4.2 "junio a agosto"): reemplazar la ventana por
  **octubre 2026**, referida a la clasificación manual del corpus **real**. Conservar la declaración
  honesta ("declaración de los autores sin registro fechado"). Verificación ANTES:
  `rg -n "junio y agosto|entre junio y agosto|junio a agosto" S/04-marco-metodologico.tex` devuelve
  `:14` sin calificación; DESPUES: la ventana dice octubre 2026 y referencia el corpus real.
- [x] 3.2 Tabla 4 `tab:procedencia-numeros` (`S/04-marco-metodologico.tex:78`): la fila de procedencia
  de los tiempos manuales referencia el corpus vigente (200 casos, campaña de octubre 2026) y no el
  sintético retirado. Verificación ANTES: `rg -n "procedencia-numeros|corpus sint.tico" S/04-marco-metodologico.tex`;
  DESPUES: la procedencia dice corpus vigente (octubre) y el sintético no figura como base.
- [x] 3.3 `S/01-introduccion.tex:16`: la mención de la ventana de recolección se alinea con octubre
  2026. Verificación ANTES: `rg -n "junio a agosto|junio y agosto" S/01-introduccion.tex` devuelve
  `:16`; DESPUES: 0 coincidencias de la ventana junio–agosto fuera de la Nota de versiones.
- [x] 3.4 Sin compuerta: verificar que el 165,3 s del corpus sintético del 3 de julio aparece solo en
  la Nota de versiones como histórico/retirado, nunca como base de medición. Verificación ANTES:
  `rg -n "165,3|165,3 s" S/`; DESPUES: 0 coincidencias fuera de I.1, y en I.1 está rotulado como
  histórico/retirado.

## 4. C-02 - Retiro del componente "~10 s de carga del ticket" (no declarar valor)

- [x] 4.1 RED: escribir `E/test_analisis_quinta_instancia_c250.py` (patrón de
  `E/test_analisis_regimen_c249.py`) con datos sintéticos mínimos: desagregación sin telefonía
  (correo+formulario) con su intervalo de diferencia pareada; reducción sin telefonía; mediana/media
  de `duracion_segundos` vs. `t_e2e_s` de telefonía. Verificación:
  `pytest E/test_analisis_quinta_instancia_c250.py` falla porque el módulo no existe.
- [x] 4.2 GREEN y TRIANGULATE: implementar `E/analisis_quinta_instancia_c250.py` con el mínimo para
  pasar; agregar al menos un segundo caso por comportamiento (p. ej. desagregación con un canal
  vacío; grabación sin `t_e2e_s`). Verificación: `pytest E/test_analisis_quinta_instancia_c250.py` en
  verde con >= 2 casos por función.
- [x] 4.3 Ejecutar el script sobre `data/corpus_evaluacion_pseudonimizado.json`,
  `data/corpus_resultados_telefonia.json` y `data/corpus_resultados_web_correo.json`; escribir
  `E/analisis_quinta_instancia_c250.{json,md,SHA256SUMS.txt}`. Verificación: el JSON reproduce la
  lectura sin telefonía (≈44,1 s → ≈16,2 s, ≈63,3 %); toda diferencia con el dictamen se consigna en
  la sección c-250.
- [x] 4.4 REFACTOR: nombres y constantes; `pytest E/` completo en verde. Verificación: suite en verde.
- [x] 4.5 Retirar el "~10 s de carga del ticket" de `S/04-marco-metodologico.tex:89` y `:131`
  (octava amenaza): el tiempo manual ES la clasificación manual (lectura + decisión), sin componente
  de carga. Verificación ANTES: `rg -n "en el orden de 10|carga del ticket" S/04-marco-metodologico.tex`
  devuelve `:89`, `:131`; DESPUES: 0 coincidencias de "carga del ticket" como componente sumado.
- [x] 4.6 Definición operacional por brazo en Tabla 3 (`S/04-marco-metodologico.tex:31`): manual =
  clasificación (lectura + decisión de sector); automatizado = E2E (recepción → persistencia);
  eliminar "hasta la persistencia confirmada del ticket" como descripción del brazo manual.
  Verificación ANTES: `rg -n "persistencia confirmada del ticket" S/04-marco-metodologico.tex`
  devuelve `:31`; DESPUES: el brazo manual no se describe como "hasta la persistencia".
- [x] 4.7 Retirar el componente de carga de Resumen (`S/00-resumen.tex:13`), Abstract (`:29`), §1.2
  (`S/01-introduccion.tex:18`), §8.1 (`S/07-resultados.tex:285`, `:36-38`), Tabla 10
  (`S/07-resultados.tex:42`) y Tabla 23 (`S/09-conclusiones.tex:14`), y `data/README.md`.
  Verificación ANTES: `rg -n "carga del ticket|10~s|10 s de carga|componente estimado" S/00-resumen.tex S/01-introduccion.tex S/07-resultados.tex S/09-conclusiones.tex data/README.md`;
  DESPUES: 0 coincidencias de un componente de carga sumado al tiempo manual.
- [x] 4.8 NO re-relatar el Anexo K como "remoción de carga": `S/12-anexos.tex:351,353,367` ya
  computa −10 s → 51,6 s / 65,6 % como **sensibilidad de redondeo** (valores redondeados ARRIBA a
  múltiplos de 5 s). Esa sensibilidad PERMANECE sin cambio. Verificación: el texto del Anexo K
  conserva la fórmula de sensibilidad de redondeo y NO introduce la palabra "carga" como componente.

## 5. C-03 - Asimetría telefónica y sub-hipótesis 1 sin telefonía

- [x] 5.1 Informar la mediana y media de duración de las 81 grabaciones
  (`duracion_segundos`: mediana 7,0 s / media 7,26 s) distinguiéndolas del `t_e2e_s` (mediana
  18,698 s) en §8.1 y en el pasaje de telefonía que corresponda (`S/07-resultados.tex:64-74` y/o
  `S/08-discusion.tex`). Verificación ANTES: `rg -n "18,7|grabaci.n" S/07-resultados.tex S/08-discusion.tex`
  sin distinción; DESPUES: los dos constructos están nombrados y con sus medias/medianas, cifras del
  JSON de 4.3.
- [x] 5.2 Ampliar la sexta amenaza (`S/04-marco-metodologico.tex:127`) con la asimetría de entrada:
  manual lee la descripción completa en voz alta vs. automatizado recita una paráfrasis con tope 45 s.
  Verificación ANTES: `rg -n "sexta amenaza|par.frasis" S/04-marco-metodologico.tex`; DESPUES: la
  sexta amenaza contrasta los dos brazos. Con el "~10 s" retirado, la asimetría se declara aún más
  fundamental (distinto alcance Y distinta entrada).
- [x] 5.3 Informar la sub-hipótesis 1 también sin telefonía: correo+formulario ≈44,1 s → ≈16,2 s,
  ≈63,3 %, recomputada por pares con intervalo, en `S/07-resultados.tex:10` y `S/08-discusion.tex:8`.
  Verificación ANTES: `rg -n "sub-hip.tesis 1|confirmada" S/07-resultados.tex S/08-discusion.tex` sin
  lectura sin telefonía; DESPUES: la lectura sin telefonía figura con cifras del JSON de 4.3.

## 6. C-04 - Estado del registro primario unificado

- [x] 6.1 Reescribir `S/07-resultados.tex:38` para que coincida con §4.5 (`S/04-marco-metodologico.tex:66`,
  `:79`), `S/12-anexos.tex:149` y `data/README.md:40-47`: 81 telefónicos respaldados por
  `corpus_resultados_telefonia.json`; 119 correo/formulario respaldados por
  `corpus_resultados_web_correo.json` (118/119, R001 el único sin registro). Verificación ANTES:
  `rg -n "SIN registro primario|sin registro primario conservado" S/07-resultados.tex` devuelve
  `:38`; DESPUES: 0 coincidencias de la fórmula contradictoria y el pasaje es coherente con §4.5,
  `12:149` y `data/README.md:40-47`; `sha256sum` de los JSON de 1.3 sin cambios.

## 7. C-05 - Consentimiento, licitud por disociación y sin originales (HIGH)

- [x] 7.1 (HIGH) `S/11-aspectos-legales.tex:18` y `data/README.md:55-63`: RETIRAR la afirmación de que
  "los originales no versionados contenían los nombres reales de sus sistemas + ID USUARIO". El corpus
  fue SIEMPRE genérico ("sistema principal"/"sistema secundario"): no hay originales con
  identificadores, ni custodio ni fecha de destrucción que declarar. Verificación ANTES:
  `rg -n "nombres reales|ID USUARIO|SISTEMA PRINCIPAL|custodi|destrucci.n" S/11-aspectos-legales.tex data/README.md`;
  DESPUES: 0 coincidencias de originales con identificadores; sin custodia ni destrucción declaradas.
- [x] 7.2 (HIGH) `S/11-aspectos-legales.tex:46`: retirar "los titulares de los datos y los
  responsables del tratamiento son las mismas personas". Separar el consentimiento de los
  colaboradores (autores + A1) del de los TITULARES (los reportantes del círculo). Verificación
  ANTES: `rg -n "titulares.*responsables.*mismas personas" S/11-aspectos-legales.tex` devuelve
  `:46`; DESPUES: 0 coincidencias, y ambos consentimientos se tratan por separado.
- [x] 7.3 (HIGH) `S/11-aspectos-legales.tex:32`: definir la notificación a los integrantes del grupo
  como **verbal el 2026-09-30** (corrige el 2026-10-01 actual): se les comunicó que se utilizarían sus
  incidentes en forma pseudonimizada y disociada, construidos a partir de sus descripciones.
  Verificación ANTES: `rg -n "notificaci.n a los integrantes del grupo|01/10|1 de octubre" S/11-aspectos-legales.tex`
  sin definición o con la fecha 01/10; DESPUES: fecha 2026-09-30 y definición presente.
- [x] 7.4 (HIGH) Fundar la licitud en la disociación citando arts. **2 y 28**: `S/11-aspectos-legales.tex:12`
  (y donde corresponda) gana la cita del art. 28. Verificación ANTES: `rg -n "art.*28|art.culo 28" S/11-aspectos-legales.tex`
  = 0; DESPUES: >= 1, junto al art. 2.

## 8. C-06 - Empleadores disueltos, reencuadre de procedencia y art. 10 (HIGH)

- [x] 8.1 (HIGH) `S/11-aspectos-legales.tex:18`: RETIRAR "los empleadores reales de los autores" y "no
  se requirió autorización de esas organizaciones". El origen real es **familiares y amigos (el
  círculo)**. No hay empleador, por lo tanto NO se requiere el aval escrito del director (la
  afirmación que respaldaba desapareció). Verificación ANTES: `rg -n "empleadores reales|no se requiri. autorizaci.n de esas organizaciones" S/11-aspectos-legales.tex`
  devuelve `:18`; DESPUES: 0 coincidencias y la procedencia dice el círculo.
- [x] 8.2 (HIGH) Agregar el deber de confidencialidad (**art. 10**, Ley 25.326) a los principios
  generales del capítulo legal (junto a la tríada CIA, hoy en `:40`). Verificación ANTES:
  `rg -n "art.culo 10|art.*10|confidencialidad" S/11-aspectos-legales.tex` = 0 (salvo CIA);
  DESPUES: >= 1 con el texto del art. 10.

## 9. Reencuadre de procedencia (conforme a C-06)

- [x] 9.1 RETIRAR "integrantes del entorno operativo del propio equipo" de toda mención de PROCEDENCIA
  en `S/01-introduccion.tex:16,48,72`, `S/04-marco-metodologico.tex:46`, `S/08-discusion.tex:22,42,50`,
  `S/09-conclusiones.tex:52`, `S/11-aspectos-legales.tex:16,46,54` y Resumen, dejando la procedencia
  como "los autores y las personas de su círculo (familiares y amigos)". Verificación ANTES:
  `rg -n "integrantes del entorno operativo del propio equipo" S/00-resumen.tex S/01-introduccion.tex S/04-marco-metodologico.tex S/08-discusion.tex S/09-conclusiones.tex S/11-aspectos-legales.tex`
  lista las 12 apariciones; DESPUES: 0 coincidencias.
- [x] 9.2 CONSERVAR (no retirar): (a) el escenario FICTICIO "organización mediana del sector servicios
  / 120 usuarios / 42 diarios" (dispositivo de dimensionamiento, explícitamente no-real por R-01); (b)
  "organización adoptante" (despliegue futuro). Verificación: `rg -n "organizaci.n adoptante|120 usuarios|42 diarios" S/`
  sigue presente con su rol de dimensionamiento.
- [x] 9.3 Registrar el reencuadre de procedencia en la Nota de versiones (Anexo I.1) como una
  corrección de veracidad (estilo R-01 a R-07). Verificación: `rg -n "procedencia|c.rculo|familiares" S/12-anexos.tex`
  devuelve la entrada de la Nota.

## 10. C-07 - Coherencia y redacción

- [x] 10.1 Fila sobre la redacción del corpus en Tabla 26 (`tab:declaracion-uso-ia`,
  `S/12-anexos.tex:257-277`): redacción del corpus → **"sin IA"** (no se usó IA en las 119
  descripciones). Verificación ANTES: `rg -n "declaracion-uso-ia" S/12-anexos.tex` sin fila de
  redacción; DESPUES: la fila existe y dice "sin IA".
- [x] 10.2 `S/12-anexos.tex:279` (I.3): corregir "el etiquetado es de los autores" → lo hicieron A1,
  T1, E1 y E2. Verificación ANTES: `rg -n "etiquetado.*de los autores" S/12-anexos.tex` devuelve
  `:279`; DESPUES: 0 coincidencias y la atribución lista A1, T1, E1, E2.
- [x] 10.3 Unificar la atribución de las reconstrucciones entre "por los autores" (I.1
  `S/12-anexos.tex:241`), "por ese autor" (§4.4 `S/04-marco-metodologico.tex:46`) y "uno de ellos"
  (`S/09-conclusiones.tex:25`) conforme a la decisión de autoría registrada (OQ-05). Verificación
  ANTES: `rg -n "por los autores|por ese autor|uno de ellos" S/` lista las discordancias; DESPUES:
  una sola atribución.
- [x] 10.4 Mencionar "Gemini 3.1" en §7.5 (`S/11-aspectos-legales.tex:54`) para la validación retirada
  (ya aparece en I.1 `S/12-anexos.tex:243`). Verificación ANTES: `rg -n "Gemini 3\.1" S/11-aspectos-legales.tex`
  = 0; DESPUES: >= 1.
- [x] 10.5 Dejar una sola vez "dispositivo de dimensionamiento y no el lugar de recolección" (aparece
  8× en `S/01-introduccion.tex:16,62,72,76`, `S/04-marco-metodologico.tex:46`,
  `S/08-discusion.tex:22,50`, `S/09-conclusiones.tex:52`). Verificación ANTES:
  `rg -c "dispositivo de dimensionamiento y no el lugar de recolecci.n" S/` = 8; DESPUES: 1.
- [x] 10.6 Retirar "corpus propio de la organización" (`S/09-conclusiones.tex:48`); aclarar "en su
  domicilio" (`S/04-marco-metodologico.tex:46`) conforme a la decisión de autoría registrada.
  Verificación ANTES: `rg -n "corpus propio de la organizaci.n" S/09-conclusiones.tex` devuelve
  `:48`; DESPUES: 0 y "en su domicilio" aclarado.

## 11. Coherencia

- [x] 11.1 Cifras canónicas intactas: repetir el conteo de 1.2. Verificación: mismos valores; el diff
  solo re-rotula o agrega cifras del JSON de 4.3.
- [x] 11.2 Sin nombres reales ni correspondencia alias-identidad en la prosa nueva. Verificación:
  revisión del `git diff` de `S/`, `docs/seguridad/`, `data/README.md`, `C/`.
- [x] 11.3 Barrido de residuos: `rg -ni "en el orden de 10|carga del ticket|persistencia confirmada del ticket|titulares.*mismas personas|corpus propio de la organizaci.n|sin registro primario conservado|empleadores reales|integrantes del entorno operativo|junio a agosto" S/ data/README.md`
  = 0 (salvo lo que la Nota de versiones conserve como histórico, registrado).
- [x] 11.4 Resumen y Abstract <= 250 palabras de prosa; hashes del corpus y tags iguales a 1.3;
  `verify_citations.py` PASS; `pytest` de 1.4 en verde; `openspec validate c-250-atender-las-observaciones-de-la-quinta-instancia --strict`
  y `openspec validate --all --strict` sin fallos.

## 12. Release v1.6.5 - versión de defensa (HIGH; OK expreso de los autores antes de cada commit y del tag)

- [ ] 12.1 Precondición: todas las tareas de 3, 4, 7, 8, 9 y 10 aplicadas (sin compuerta pendiente);
  visto bueno escrito del director (condición del tribunal); `git status` sin cambios fuera de
  alcance. No hay tarea de "obtener aval del director" (C-06 se disolvió). Verificación: lista de
  tareas abiertas vacía.
- [x] 12.2 Bump `v1.6.4` → `v1.6.5` y fecha de release en `S/00-portada.tex` (`Versión 1.6.4`),
  Anexo B (`sec:anexo-repositorio`), Nota de versiones (I.1, con el reencuadre de procedencia y el
  corpus sintético retirado), `Bibliography_base.bib` (`Gomez2026_repositorio`), `README.md`,
  `knowledge-base/` y `C/inventario-uso-asistentes-ia.md`; cifra del Anexo I.3 recomputada con
  `git rev-list --count`. Verificación: `rg -n "1\.6\.4" ` sobre esos archivos solo en registros
  históricos; conteo coincide.
- [x] 12.3 Recompilar (Docker `texlive-thesis`, `latexmk main.tex` en `docs/Tesis/v10 (IA)/paper/`).
  Verificación: `main.log` sin errores fatales; `rg -c "undefined" main.log` = 0; 0 `multiply
  defined`; biber sin advertencias; páginas registradas.
- [x] 12.4 Regenerar `docs/Tesis/v10 (IA)/paper/compilacion.md` (`C/resumir_registro_compilacion.py --fuente`
  con hash); regenerar `tesis_para_agente.md`, `tesis_para_evaluacion.txt`, `tesis_completa_extraida.txt`,
  extractos y la copia de entrega `docs/Tesis/tesis_ultima_version.pdf`. Verificación: SHA-256 de la
  copia igual al de `main.pdf`.
- [x] 12.5 Commits y tag según la regla de tags registrada por c-249 OQ-05, con el tag anotado
  `v1.6.5` sobre el commit que la regla indique, sin mover `v1.6.4` ni anteriores. Verificación:
  `git cat-file -t v1.6.5` = `tag`; `git rev-parse v1.6.5^{commit}` y el hash impreso en el Anexo B
  coinciden; `v1.6.4` sin cambios.
- [ ] 12.6 Publicar rama y tag en `origin` (solo con pedido expreso); merge a `main` con merge commit
  (nunca squash ni rebase); `engram sync` del proyecto antes del push. Verificación:
  `git merge-base --is-ancestor v1.6.5 origin/main` verdadero.

## 13. Registro y cierre

- [x] 13.1 `C/dictamen-correcciones.md`: sección "c-250: atender las observaciones de la quinta
  instancia" con la tabla de decisiones OQ-01 a OQ-05 (cerradas), las tablas ANTES/DESPUES por
  bloque, las cifras de 4.3 (y sus diferencias con el dictamen), el resultado de 11.x y la release
  (`v1.6.5`, commits, SHA-256 del PDF). Verificación: la sección existe y el diff es aditivo salvo
  los encabezados.
- [x] 13.2 `C/respuestas-tribunal-cuarta-instancia.md` y `docs/defensa/respuestas-tribunal.md`:
  respuestas a las 10 preguntas probables del dictamen de quinta instancia (cronología, carga,
  telefonía, IA en las 119, custodio, empleadores), alineadas con la v1.6.5. Verificación: las
  respuestas nuevas citan la versión y no contradicen el capítulo legal.
- [x] 13.3 `CHANGES.md`: entrada `[C-250]` con estado, objetivo, specs, dependencias (después de
  c-249), gobernanza (MEDIUM; HIGH en el capítulo legal, `docs/seguridad/`, `data/README.md` y el
  release), tag `v1.6.5` y "Leer antes", con el formato de la entrada `[C-249]`. Verificación: la
  entrada existe.
- [x] 13.4 `openspec validate --all --strict`; archivar el change. Verificación: valida y el change
  queda en `openspec/changes/archive/`.