# Tasks: Atender la devolución de sexta instancia del tribunal

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`D/` = `auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md`; `E/` = `evaluation/data/campana/analisis/`.
Líneas de `main` al 2026-11-26 (tag `v1.6.5` más el estado aplicado de c-251); el apply las re-verifica con
`rg` antes de editar, porque las ediciones las desplazan. Mapa archivo→capítulo: Ch4=`04-marco-metodologico.tex`,
Ch7 (legal)=`11-aspectos-legales.tex`, Ch8=`07-resultados.tex`, Ch9=`08-discusion.tex`, Ch10=`09-conclusiones.tex`,
Anexos=`12-anexos.tex`. Equivalente de Strict TDD para prosa: cada tarea de edición corre un `rg` ANTES
(muestra el defecto) y DESPUES (estado deseado), registrados en la sección c-252 de `C/dictamen-correcciones.md`.
Marcas: **[GATED OQ-0n]** = bloqueada hasta que la respuesta de OQ-0n figure en la tabla de compuertas de la
sección c-252; sin marca = aplicable sin compuerta. Dominio HIGH (`S/11-aspectos-legales.tex`, `docs/seguridad/`,
`data/README.md`, procedencia, grupo de release): mostrar el texto propuesto a los autores antes de escribir.
Reglas: no commitear, taggear ni pushear sin pedido expreso; no cambiar cifras canónicas salvo por la rama A
de OQ-02; español neutro sin emojis; solo alias (`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); no tocar `App/`, `n8n/`,
los artefactos existentes de `evaluation/` ni los casos y JSON del corpus; no rehacer lo que c-251 ya aplicó;
evitar en prosa "capitulo" seguido de coma y nombre de archivo (falso positivo de gitleaks).

## 1. Guardas, línea base y dependencia con c-251

- [ ] 1.1 Leer `proposal.md`, `design.md` (D1-D10, OQ-01 a OQ-05), los tres deltas de `specs/` y `D/` completo.
  Verificación: `git rev-parse v1.6.5^{commit}` registrado; `git diff --stat v1.6.5 HEAD -- "docs/Tesis/v10 (IA)/paper/sections" docs/diagrams`
  lista solo los archivos de c-251 (`04`, `08`, `11`, `12`, `cronograma.md`) o la diferencia queda registrada.
- [ ] 1.2 Estado de c-251: confirmar que su contenido está aplicado (`git show --stat a4437a1a 049eb353 f1854521`)
  y pedir a los autores cerrarlo (marcar tareas y archivar) antes de seguir, o registrar en la sección c-252
  que c-252 se aplica sobre su estado aplicado sin archivarlo. Verificación: `openspec list --json` muestra
  c-251 archivado, o la decisión está registrada.
- [ ] 1.3 Línea base: `rg -c "61,6|17,76|71,2|65,6|63,3|87,2|20,09|73,5|165,3" S/`, conteo de palabras de
  prosa del Resumen y del Abstract, y `sha256sum data/corpus_evaluacion_pseudonimizado.json data/corpus_resultados_telefonia.json data/corpus_resultados_web_correo.json`,
  registrados en la sección c-252 como valores que el apply no cambia (salvo rama A de OQ-02 en las cifras).
- [ ] 1.4 Red de seguridad: `python "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS; `pytest E/` en verde
  desde su carpeta con las variables dummy del CI (conteo registrado); `openspec validate --all --strict`.
  Una falla previa se reporta como preexistente y no se corrige aquí.

## 2. Compuertas de autores y director

- [ ] 2.1 **[COMPUERTA OQ-01]** Presentar a los autores las cinco preguntas de OQ-01 (design, Open Questions)
  junto con la evidencia fechada de Context (`b0dcc057`, commits de c-68 del 02/10, de c-70 del 05-06/10,
  `ea625764`, `35592473`). Registrar respuesta literal, fecha y responsable; anotar la rama de D3 (A: manual
  primero sostenido; B: no sostenido). Verificación: la fila existe con rama elegida.
- [ ] 2.2 **[COMPUERTA OQ-02]** Presentar la pregunta de OQ-02 con la cita de `v1.6.4:04:89` y las decisiones
  previas de c-250 (OQ-02) y c-251 (E5). Registrar la respuesta y la rama de D4 (A: la carga se sumó; B: nunca
  se sumó) con la explicación de por qué la otra descripción figuró en una versión entregada. Verificación:
  la fila existe con rama elegida.
- [ ] 2.3 **[COMPUERTA OQ-03]** (HIGH) Presentar a autores y director las cinco preguntas de OQ-03, incluida la
  conciliación entre `S/11-aspectos-legales.tex:18` ("no existen originales") y `ea625764` ("mantener los
  crudos fuera"). Registrar la respuesta y la constancia fechada del visto bueno escrito del director sobre la
  procedencia (ruta del documento). Verificación: fila y constancia existen.
- [ ] 2.4 **[COMPUERTA OQ-04]** Presentar la pregunta sobre el cronometraje por pares desde el domicilio.
  Registrar la respuesta. Verificación: la fila existe.
- [ ] 2.5 **[COMPUERTA OQ-05]** Presentar la pregunta sobre la composición del tiempo manual telefónico, junto con
  la salida de 3.3 (extensión media por canal). Registrar la respuesta (o que la composición no se midió por
  separado). Verificación: la fila existe.

## 3. D-04 - Script de extensión de las descripciones (TDD, sin compuerta)

- [ ] 3.1 RED: escribir `E/test_analisis_sexta_instancia_c252.py` (patrón de `E/test_analisis_quinta_instancia_c250.py`)
  con datos sintéticos mínimos: conteo de palabras y caracteres de una descripción (incluye espacios múltiples
  y vocales acentuadas); media por canal; media por régimen con la regla de régimen pasada como parámetro;
  tiempo manual medio y segundos por palabra por canal. Verificación:
  `pytest E/test_analisis_sexta_instancia_c252.py` falla porque el módulo no existe.
- [ ] 3.2 GREEN y TRIANGULATE: implementar `E/analisis_sexta_instancia_c252.py` con el mínimo para pasar y
  agregar al menos un segundo caso por función (canal vacío, descripción vacía, régimen sin casos).
  Verificación: la prueba en verde con >= 2 casos por función.
- [ ] 3.3 Ejecutar sobre `data/corpus_evaluacion_pseudonimizado.json` y escribir
  `E/analisis_sexta_instancia_c252.{json,md,SHA256SUMS.txt}`. Verificación: el JSON trae los tres canales
  (81/66/53) y los dos regímenes (81/119); las cifras coinciden en orden de magnitud con el cálculo preliminar
  de design (telefonía ≈11,8 palabras, 87,2 s); diferencias registradas en la sección c-252.
- [ ] 3.4 REFACTOR: nombres y constantes; `pytest E/` completo en verde. Verificación: suite en verde.
- [ ] 3.5 **[GATED OQ-02, solo rama A]** Agregar con su prueba primero la recomputación con −10 s (global, por
  canal y sin telefonía, por pares con intervalo, semilla 20261021). Verificación: prueba en verde y salida
  versionada con el 65,6 % global.

## 4. D-01 - Cronología día por día acotada por evidencia

- [ ] 4.1 **[GATED OQ-01]** Agregar la cronología día por día (tabla en §4.4 de `S/04-marco-metodologico.tex`
  o en el Anexo de la Figura 11) con etapa, fecha o intervalo, operador o mitad cuando corresponda y evidencia
  (commit, archivo o "declaración de los autores"). Verificación ANTES: `rg -n "cronolog" S/04-marco-metodologico.tex S/12-anexos.tex`
  sin tabla día por día; DESPUES: la tabla existe y cada fila tiene evidencia.
- [ ] 4.2 **[GATED OQ-01]** Declarar la cota del commit del 09/10 en §4.2 (`S/04-marco-metodologico.tex:14`),
  §4.4 (`:46`, las dos menciones de "octubre de 2026" del cronometraje), Tabla 4 (`:78`, "Campaña 2026-10 (oct
  2026)") y el pie de la Figura 11 (`S/12-anexos.tex:53`, "la confirmación del 9-10-2026 cubre las ventanas de
  las campañas"). Verificación ANTES: `rg -n "octubre de 2026|oct 2026|9-10-2026" S/04-marco-metodologico.tex S/12-anexos.tex`;
  DESPUES: cada pasaje dice que la fecha es declaración de los autores acotada por `ea62576`.
- [ ] 4.3 **[GATED OQ-01]** `docs/diagrams/cronograma.md`: la línea `Campaña manual (oct) :cm, 2026-10-01, 2026-10-31`
  (introducida por c-251) termina en la cota declarada; actualizar la fila de la tabla de evidencia; regenerar
  `docs/Tesis/v10 (IA)/paper/figures/cronograma.png`. Verificación ANTES: `rg -n "Campa.a manual" docs/diagrams/cronograma.md`
  devuelve `2026-10-31`; DESPUES: fecha final <= 2026-10-09 y PNG regenerado.
- [ ] 4.4 **[GATED OQ-01, solo rama B]** Corregir el orden de los brazos: §4.2 (`S/04-marco-metodologico.tex:14`,
  "primero por el flujo manual [...] y luego por el flujo automatizado"), primera amenaza (`:117`) y tercera
  explicación rival de §9.1 (`S/08-discusion.tex:22`, "El orden temporal de la campaña (manual antes que
  automatizado) sesga, de hacerlo, en contra de la hipótesis"), y declarar si los operadores vieron la salida
  automatizada. Revisar `S/07-resultados.tex:311` y `S/09-conclusiones.tex:42` para no confundirlos con la
  campaña complementaria. Verificación ANTES: `rg -n "precedi|primero por el flujo manual|manual antes que automatizado" S/`;
  DESPUES: ninguna afirmación del orden manual → automatizado para la campaña 2026-10 contraria a OQ-01.
- [ ] 4.5 **[GATED OQ-01, solo rama A]** Si el intervalo 01/10-02/10 no alcanza para las cuatro tareas de los
  119 casos, la cronología dice cuándo se recolectaron y redactaron, y se concilia con la notificación y el
  consentimiento del capítulo legal (`S/11-aspectos-legales.tex:32`). Verificación: sin contradicción de fechas
  entre §4.4 y §7.3 (lectura cruzada registrada).
- [ ] 4.6 **[GATED OQ-01]** Anexo I.1 (`S/12-anexos.tex:241`): declarar quién midió o generó los 165,3 s del 3 de
  julio y sobre qué textos. Verificación ANTES: `rg -n "165,3" S/12-anexos.tex` sin autoría; DESPUES: la
  autoría consta.

## 5. D-02 - Definición del tiempo manual con su historia

- [ ] 5.1 **[GATED OQ-02]** Reemplazar "retirado el componente de carga, el 87,2~s manual es la clasificación
  pura" (`S/04-marco-metodologico.tex:127`) por una redacción que no sugiera cambio de valores (rama B: "el
  87,2 s manual mide solo la clasificación"; rama A: la definición con la carga). Verificación ANTES:
  `rg -n "retirado el componente de carga" S/` devuelve `04:127`; DESPUES: 0.
- [ ] 5.2 **[GATED OQ-02]** Anexo K (`S/12-anexos.tex:354`): reescribir "el de 10~s recoge el escenario adverso
  en que se restara el componente de carga [...] componente que la presente versión ya no contempla"
  (introducida por c-251 E5) según la rama, conservando los valores de la Tabla 29. Verificación ANTES:
  `rg -n "ya no contempla" S/` devuelve `12:354`; DESPUES: 0 y los valores 56,6/68,6 y 51,6/65,6 intactos.
- [ ] 5.3 **[GATED OQ-02]** Anexo I.1 (`S/12-anexos.tex:239-247`): registrar la historia de la definición (qué
  decía la v1.6.4, qué dice la vigente, cuál es correcta, por qué la otra figuró en una versión entregada),
  con el criterio de los retiros anteriores. Verificación ANTES: `rg -n "carga" S/12-anexos.tex` sin entrada en
  I.1; DESPUES: la entrada existe.
- [ ] 5.4 **[GATED OQ-02, solo rama A]** Cambiar la cifra primaria a 65,6 % y propagar con las cifras de 3.5:
  Tabla 3 (`04:31`), `04:46`, `04:89`, octava amenaza (`04:131`), Resumen (`S/00-resumen.tex:13`), Abstract
  (`:29`), Tabla 10 (`S/07-resultados.tex:22`), §8.1 (`07:38`, `07:57-60`), Tabla 12, `07:285`, §9.1
  (`S/08-discusion.tex:8`, `:22`), Tabla 23 (`S/09-conclusiones.tex:15`), Tabla 29 y una sección aditiva en
  `C/numeros-canonicos.md` (71,2 % marcado como lectura con carga). Verificación ANTES:
  `rg -n "71,2|sin componente de carga|no incluye componente de carga" S/`; DESPUES: 65,6 % primaria en cada
  pasaje y 0 coincidencias de "sin componente de carga".

## 6. D-03 - Procedencia del régimen (a) (HIGH)

- [ ] 6.1 **[GATED OQ-03]** Retirar o explicar "del sector servicios y con sede en la provincia de Mendoza"
  aplicado a las personas del círculo en `S/01-introduccion.tex:16` y `S/09-conclusiones.tex:52`, sin tocar el
  escenario de referencia ficticio ("organización mediana del sector servicios", 120 usuarios). Verificación
  ANTES: `rg -n "con sede en la provincia de Mendoza" S/` devuelve `01:16`, `09:52`; DESPUES: 0 aplicadas a
  personas, o explicación según OQ-03.
- [ ] 6.2 **[GATED OQ-03]** §4.4 (`S/04-marco-metodologico.tex:46`): una sola declaración del ámbito (laboral o
  no) de los incidentes del régimen (a), del léxico corporativo («cliente», «sucursal», «estado de cuenta»,
  «sistema principal»), de los casos de trabajo de §8.5 (`S/07-resultados.tex:277`, R015) y de los sectores de
  la Tabla 18 (`07:255`), y de que la composición 119/81 descansa en la declaración de los autores, sin
  originales. Verificación ANTES: `rg -n "«cliente»|registro narrativo" S/04-marco-metodologico.tex`;
  DESPUES: una sola declaración y sin repeticiones en `07` ni `11`.
- [ ] 6.3 **[GATED OQ-03]** (HIGH) Capítulo legal (`S/11-aspectos-legales.tex:16`, `:18`, `:46`, `:54`): si el
  ámbito es laboral, deber de confidencialidad del art. 10 de la Ley 25.326 respecto de esos lugares de
  trabajo; conciliar "no existen originales con identificadores" (`:18`) con la respuesta sobre los "crudos" de
  `ea625764` (y `data/README.md` si corresponde). Texto propuesto mostrado a los autores antes de escribir.
  Verificación ANTES: `rg -n "art.culo 10|confidencialidad|originales" S/11-aspectos-legales.tex`; DESPUES:
  coincide con OQ-03 y no contradice §4.4.
- [ ] 6.4 **[GATED OQ-03]** Anexo I.1: registrar el cambio de origen del régimen (a) respecto de la v1.6.4 y citar
  la constancia del visto bueno escrito del director sobre la procedencia. Verificación ANTES:
  `rg -n "empleador|visto bueno" S/12-anexos.tex`; DESPUES: la entrada y la cita existen.

## 7. D-04 - Prosa de la lectura telefónica

- [ ] 7.1 **[GATED OQ-05]** Informar la extensión media por canal y régimen (salida de 3.3) y la composición de
  los 87,2 s en §4.4 (`S/04-marco-metodologico.tex:46`, "descripción general [...] sin detalles explícitos"),
  la sexta amenaza (`:127`), §8.1 (`S/07-resultados.tex:57-60`) y la nota de la Tabla 12. Verificación ANTES:
  `rg -n "palabras|caracteres" S/04-marco-metodologico.tex S/07-resultados.tex` sin extensión; DESPUES: cifras
  de la salida versionada y composición según OQ-05.

## 8. D-05 - Propagación y trazabilidad (sin compuerta, salvo cifras de la rama A)

- [ ] 8.1 Resumen (`S/00-resumen.tex:11-13`) y Abstract (`:27-29`): agregar que el brazo manual midió solo la
  clasificación (no el registro) y la reducción sin telefonía (63,3 %, o la de 3.5 en rama A), dentro de 250
  palabras de prosa. Verificación ANTES: `rg -n "clasificaci.n|63,3|classification|63.3" S/00-resumen.tex`;
  DESPUES: ambas cláusulas presentes en los dos idiomas y conteos <= 250 registrados.
- [ ] 8.2 Tabla 10 (`S/07-resultados.tex:22`): la fila del tiempo dice que el brazo manual midió la clasificación
  e incluye la reducción sin telefonía. Verificación ANTES: `rg -n "Tiempo de registro \(media\)" S/07-resultados.tex`;
  DESPUES: fila ampliada.
- [ ] 8.3 `S/04-marco-metodologico.tex:16`: "cronometró en vivo el registro manual de cada incidente" pasa a "la
  clasificación manual". Verificación ANTES: `rg -n "registro manual de cada incidente" S/` devuelve `04:16`;
  DESPUES: 0.
- [ ] 8.4 Anexo I.1: registrar el cambio de fechas de la campaña manual (junio-agosto en la v1.6.4 → octubre,
  con la cota de 4.2) junto con las entradas de 5.3 y 6.4. Verificación: `rg -n "junio" S/12-anexos.tex` solo
  en I.1, con el registro del cambio.
- [ ] 8.5 Anexo I.2 (`S/12-anexos.tex:251`): agregar la devolución de quinta instancia (25 de noviembre de 2026)
  y la de sexta instancia (26 de noviembre de 2026). Verificación ANTES: `rg -n "quinta instancia|sexta instancia" S/12-anexos.tex`
  sin I.2; DESPUES: ambas en I.2.

## 9. D-06 - Coherencia y redacción

- [ ] 9.1 **[GATED OQ-04]** Aclarar en §4.4 (`S/04-marco-metodologico.tex:46`, "cronometraron por pares, en el
  domicilio de cada analista") y en `:16` cómo se cronometraron por pares. Verificación ANTES:
  `rg -n "domicilio" S/04-marco-metodologico.tex`; DESPUES: coincide con OQ-04 y sin contradicción con "por pares".
- [ ] 9.2 Anexo F (`S/12-anexos.tex:149`): "redactadas por los autores" → "redactadas por uno de los autores",
  coherente con §4.4. Verificación ANTES: `rg -n "redactadas por los autores" S/` devuelve `12:149`; DESPUES: 0.
- [ ] 9.3 §8.1 (`S/07-resultados.tex:38`): reemplazar las dos apariciones de "respaldados por" por la fórmula de
  §4.5 (`04:66`: el registro "respalda la existencia y la procedencia de los incidentes, no la medición de
  extremo a extremo"). Verificación ANTES: `rg -n "respaldados por" S/` devuelve `07:38`; DESPUES: 0.
- [ ] 9.4 (HIGH) §7.5 (`S/11-aspectos-legales.tex:46`): corregir "los titulares de los datos son los reportantes
  del círculo, distintos de los autores", porque los autores también son reportantes y titulares de sus
  propios incidentes. Texto mostrado a los autores antes de escribir. Verificación ANTES:
  `rg -n "distintos de los autores" S/` devuelve `11:46`; DESPUES: 0.
- [ ] 9.5 Anexo I.1 (`S/12-anexos.tex:247`): "registro histórico/retirado" → "registro histórico, retirado".
  Verificación ANTES: `rg -n "hist.rico/retirado" S/` devuelve `12:247`; DESPUES: 0.

## 10. Respuestas a las diez preguntas de la sección 6

- [ ] 10.1 **[GATED OQ-01, OQ-02]** Redactar `C/respuestas-tribunal-sexta-instancia.md` con el formato de
  `C/respuestas-tribunal-quinta-instancia.md`, preguntas 1 a 4 (obligatorias): días exactos de cada etapa;
  por qué junio-agosto en la v1.6.4 y octubre en la v1.6.5; quién midió los 165,3 s; si `tiempo_manual_s`
  incluye la carga y por qué la versión anterior decía lo contrario. Verificación: cuatro respuestas sin
  marcas de pendiente, cada hecho con artefacto o rótulo "declaración de los autores".
- [ ] 10.2 **[GATED OQ-03, OQ-04, OQ-05]** Preguntas 5 a 8: ámbito laboral y léxico; cambio de atribución
  v1.6.4 → v1.6.5; extensión media de las 81 descripciones y 87 s frente a 7 s (cifras de 3.3); cronometraje
  por pares desde el domicilio. Verificación: respuestas presentes y coherentes con la tesis.
- [ ] 10.3 Preguntas 9 y 10 (sin compuerta): qué evidencia, fuera de la declaración, distingue un caso real de
  uno redactado (commits fechados `b0dcc057` y `ea625764`, ausencia de originales; se dice con honestidad que no
  hay más); qué parte del 73,5 % es atribuible al clasificador (Tabla 30 `tab:sensibilidad-ajustes`, séptima
  amenaza `04:129`). Verificación: respuestas presentes, cifras canónicas.
- [ ] 10.4 Cotejo y alineación: `python C/cotejar_cifras_respuestas.py` sobre el documento nuevo y alinear
  `docs/defensa/respuestas-tribunal.md`. Verificación: ejecución limpia y sin contradicciones con el ejemplar.

## 11. Coherencia y autoverificación estilo CONEAU

- [ ] 11.1 Cifras canónicas: repetir el conteo de 1.3. Verificación: mismos valores (o, en rama A de OQ-02, los
  cambios previstos en 5.4 y nada más).
- [ ] 11.2 Barrido de frases citadas por `D/`: `rg -ni "del sector servicios y con sede|retirado el componente de carga|ya no contempla|respaldados por|distintos de los autores|hist.rico/retirado|redactadas por los autores|registro manual de cada incidente|junio a agosto" S/`
  = 0 fuera de I.1 (lo que I.1 conserve como histórico, registrado). Verificación: resultado registrado.
- [ ] 11.3 Autoverificación estilo CONEAU sobre el PDF compilado: fechas de corridas frente a commits (02/10,
  05-06/10, 09/10, 19/10), Figura 11 frente al texto, cronología de 4.1 frente al capítulo legal, pines del tag
  frente a los declarados, sin nombres reales ni correspondencia alias-identidad, Resumen y Abstract <= 250
  palabras, `verify_citations.py` PASS, `pytest E/` en verde, hashes del corpus iguales a 1.3. Verificación:
  tabla de resultados en la sección c-252.
- [ ] 11.4 `openspec validate c-252-atender-la-devolucion-de-sexta-instancia --strict` y
  `openspec validate --all --strict` sin fallos. Verificación: salida registrada.

## 12. Release v1.6.6 - versión de defensa (HIGH; OK expreso de los autores antes de cada commit y del tag)

- [ ] 12.1 Precondición: compuertas OQ-01 a OQ-05 cerradas; tareas de 4, 5 y 6 aplicadas (D-01 a D-03 son
  condición del tribunal); tareas de 7, 8 y 9 aplicadas o registradas como "a exponer en la defensa"; visto
  bueno escrito del director a la versión de defensa, con constancia fechada citada en la sección c-252.
  Verificación: lista de tareas abiertas vacía salvo 12.x y 13.x.
- [ ] 12.2 Bump `v1.6.5` → `v1.6.6` y fecha en `S/00-portada.tex`, Anexo B (`sec:anexo-repositorio`), I.1,
  `docs/Tesis/v10 (IA)/Bibliography_base.bib` (`Gomez2026_repositorio`), `README.md`, `knowledge-base/` y
  `C/inventario-uso-asistentes-ia.md`; cifra del Anexo I.3 recomputada con `git rev-list --count`.
  Verificación: `rg -n "1\.6\.5"` sobre esos archivos solo en registros históricos; conteo coincide.
- [ ] 12.3 Recompilar (Docker `texlive-thesis` con `MSYS_NO_PATHCONV=1`, `latexmk main.tex` en
  `docs/Tesis/v10 (IA)/paper/`). Verificación: `main.log` sin errores fatales, 0 `undefined`, 0 `multiply
  defined`, biber sin advertencias, páginas registradas, flotantes contenidos.
- [ ] 12.4 Commit de contenido C3 (conventional commit, sin atribución de IA). Regenerar `compilacion.md` con
  `C/resumir_registro_compilacion.py --fuente` (hash de C3) y los derivados (`tesis_para_agente.md`,
  `tesis_para_evaluacion.txt`, `tesis_completa_extraida.txt`, extractos, `docs/Tesis/tesis_ultima_version.pdf`).
  Verificación: SHA-256 de la copia igual al de `main.pdf`.
- [ ] 12.5 Commit C4 con el hash de C3 en el Anexo B; tag anotado `v1.6.6` sobre C3 según la regla de c-249
  OQ-05, sin mover `v1.6.0` a `v1.6.5`. Verificación: `git cat-file -t v1.6.6` = `tag`;
  `git rev-parse v1.6.6^{commit}` igual al hash impreso; `git rev-parse v1.6.5^{commit}` igual a 1.1.
- [ ] 12.6 Publicar rama y tag (solo con pedido expreso): rama nueva y PR, nunca push directo a `main`;
  `engram sync` del proyecto (nunca `--all`) antes del push; esperar CI en verde. Verificación:
  `git merge-base --is-ancestor v1.6.6 origin/main` verdadero tras el merge.

## 13. Registro y cierre

- [ ] 13.1 `C/dictamen-correcciones.md`: sección "c-252: atender la devolución de sexta instancia" con la tabla
  de compuertas OQ-01 a OQ-05 (respuesta literal, fecha, responsable, rama), las tablas ANTES/DESPUES por
  tarea, las cifras de 3.3 (y 3.5), el resultado de 11.x y la release (`v1.6.6`, commits, SHA-256 del PDF).
  Verificación: la sección existe y el diff es aditivo salvo encabezados.
- [ ] 13.2 `CHANGES.md`: entrada `[C-252]` con estado, objetivo, specs, dependencias (después de c-250 y sobre
  el estado aplicado de c-251), gobernanza (MEDIUM; HIGH en el capítulo legal, la procedencia y la release),
  tag `v1.6.6` y "Leer antes", con el formato de `[C-250]`. Verificación: la entrada existe.
- [ ] 13.3 `openspec validate --all --strict`; archivar el change (sincroniza `tesis-sexta-instancia`, los dos
  MODIFIED de `tesis-reencuadre-cuarta-instancia` y el ADDED de `tesis-document`). Verificación: valida y el
  change queda en `openspec/changes/archive/`.
