# Design: c-79 — Aspectos legales (11.1-11.3)

## Context

Ver `proposal.md` — Why. Estado relevante verificado contra el arbol de trabajo v9
(2026-10-12):

- `11-aspectos-legales.tex:12` (§11.2) enuncia "el principio de limitacion del plazo
  de conservacion" y lo traduce, para los incidentes, en "una politica de conservacion
  indefinida justificada por el valor estadistico de los datos historicos". En el mismo
  parrafo funda la licitud en "el legitimo interes de la organizacion". Al final declara
  que "los incidentes en estado cerrado se preservan como registro auditable permanente:
  pueden consultarse pero no editarse ni eliminarse".
- `05-arquitectura.tex:44` declara que "los registros de cada ejecucion se conservan
  durante 30 dias para fines de auditoria y diagnostico operativo". Nunca se reconcilia
  con §11.2.
- `11-aspectos-legales.tex.bak:12` (version previa) decia "una politica de retencion de
  90 dias para los registros operativos y de un ano para los datos de incidentes
  resueltos". `knowledge-base/10_preguntas_abiertas.md` (IN-05, lineas 26-30) documenta
  que C-18 redefinio la politica a "conservacion indefinida" y que el bloqueo de escritura
  sobre tickets cerrados (C-23: `PATCH /api/v1/incidentes/{id}` devuelve 409 en estado
  terminal) es un control de integridad, no una purga ni una politica de retencion.
- `11-aspectos-legales.tex:8` (§11.1) afirma: "Argentina mantiene un regimen de adecuacion
  reconocido por la Comision Europea, lo cual facilita los flujos transfronterizos
  bidireccionales bajo determinadas condiciones". No nombra el instrumento. En el mismo
  parrafo menciona genericamente "las consideraciones del articulo 12 ... sobre
  transferencia internacional de datos personales", pero no cita el instrumento de
  transferencia (consentimiento o clausulas contractuales modelo).
- `11-aspectos-legales.tex:16` (§11.3) afirma "pseudonimizacion previa a la transmision"
  y solo discute Gemini~2.5 Flash. NO menciona a Twilio ni el articulo 12. Menciona el
  "acuerdo de procesamiento de datos" (DPA) como mitigacion.
- Orden real del canal telefonico, `docs/runbook-verificacion-telefonia-c52.md:13`:
  "Twilio graba, el backend descarga y transcribe con Gemini, pseudonimiza, persiste el
  ingreso y hace handoff autenticado a n8n". El diagrama (`:20-21`) confirma:
  `<Record>` -> callback `recording-status` -> descarga + STT + pseudonimiza. El modelo de
  transcripcion es `gemini-3.5-transcribe` (`:61,330,377`; `App/Backend/app/config/settings.py:227`).
- Fuentes juridicas: `docs/cumplimiento/marco-legal-ar-2026.md:33-36` (art. 12: EE. UU.
  no es pais adecuado), `:37-39,369-391` (Decision 2003/490/CE + revalidacion enero 2024;
  UE -> AR), `:538-542` (transferencia a Gemini y Twilio; la pseudonimizacion mitiga pero
  no sustituye el instrumento), `:230-232,550-551` (ARCO: cinco dias habiles, art. 16),
  `:552-554` (base de licitud: art. 5 inc. 2 apartados b) o d));
  `docs/seguridad/registro-requisitos-legales.md:25,29,30,36,37`.

Restriccion dura: la tesis se compila en Overleaf (sin toolchain LaTeX local). No se toca
`App/**`. No se editan artefactos de c-76/c-77/c-78 ni `CHANGES.md`. Este change cubre
11.1-11.3; c-76 cubre numeros del corpus y ventana temporal; c-77 cubre estadistica
inferencial y 11.5 (TLS/supervision humana).

**Nota de verificacion (correccion al ground truth):** el ground truth afirmaba que la
tesis "nunca cita el articulo 12". La verificacion muestra que `11-aspectos-legales.tex:8`
lo menciona de forma generica ("las consideraciones del articulo 12 ... sobre transferencia
internacional"). La afirmacion correcta es: el articulo 12 se menciona como nota de
aplicabilidad en 11.1, pero NUNCA se cita el instrumento de transferencia que la norma
exige (consentimiento o clausulas contractuales modelo), y §11.3 lo omite por completo.
El requisito L4 exige citar el instrumento, no solo el numero de articulo.

## Goals / Non-Goals

**Goals:**

- Declarar UNA politica de retencion concreta y no contradictoria (11.2 vs 05:44),
  separando el bloqueo de integridad del concepto de retencion.
- Declarar una politica explicita de supresion/disposicion al vencer el plazo de retencion.
- Sustituir "legitimo interes" por la base de licitud del art. 5 inc. 2 de la Ley 25.326.
- Citar el instrumento de adecuacion europea y corregir su direccion (UE -> AR).
- Divulgar la transferencia telefonica pre-pseudonimizacion (Twilio, audio crudo +
  numero) y citar el instrumento del art. 12.
- Revisar la vigencia de todas las fuentes juridicas citadas y registrar la fecha de revision.
- Declarar el plazo ARCO (cinco dias habiles, art. 16).

**Non-Goals:**

- No reescribir §11.4 (seguridad tecnica) ni §11.5 (consentimiento de investigacion,
  Hawthorne, supervision humana) — alcance de c-76/c-77.
- No modificar `App/**`, el `.bib`, ni los numeros del corpus.
- No emitir una conclusion juridica vinculante: el documento sigue siendo un relevamiento
  informativo, no asesoramiento juridico.
- No fijar una fecha de revision legal (depende del momento de la revision del autor). Los
  valores de retencion, mecanismo de supresion, apartado del art. 5 y plazo ARCO estan
  resueltos (OQ-L1/L1b/L2/L5, 2026-10-12) y se registran tal cual; no se inventan valores
  fuera de esas decisiones.

## Decisions

### D-L1 — Politica de retencion unica y reconciliada

**Decision:** reemplazar "conservacion indefinida" por un plazo explicito y justificado.
El diseño separa DOS conjuntos de datos con finalidades distintas:

- **Logs de ejecucion** (`05-arquitectura.tex:44`): 30 dias, finalidad de auditoria y
  diagnostico operativo. Se mantiene.
- **Incidentes**: registro con valor operativo, historico y estadistico. Se les asigna un
  plazo de **12 meses rodantes desde la creacion del incidente** (OQ-L1, resuelta
  2026-10-12). El ciclo estadistico anual de la tesis (12/02/2026 -> 12/02/2027) justifica la
  longitud; el texto declara el PERIODO (12 meses), no las fechas calendario.

La reconciliacion consiste en declarar explicitamente que son conjuntos distintos con
finalidades distintas, de modo que 11.2 y 05:44 no se contradigan. El bloqueo de escritura
sobre tickets cerrados (C-23, 409) se presenta como control de integridad de auditoria,
no como politica de retencion.

Adicionalmente, la politica de retencion MUST incluir una declaracion explicita de
supresion/disposicion: al vencer el plazo, los datos de incidentes se **anonimizan**
(anonimizacion irreversible: se eliminan los identificadores de modo que los datos ya no
puedan vincularse a una persona; OQ-L1b, resuelta 2026-10-12). La afirmacion "registro
auditable permanente" se conserva unicamente como control de integridad de auditoria
(bloqueo de escritura, 409, C-23) y MUST NOT presentarse como una politica de retencion ni
como una excepcion permanente al vencimiento del plazo.

**Racional:** "conservacion indefinida" contradice el principio de limitacion temporal que
el propio parrafo enuncia; un plazo concreto y justificado es lo que el principio exige. El
valor (12 meses rodantes) responde al ciclo estadistico anual de la tesis y no debe
escribirse como fecha calendario fija dentro de la regla de retencion.

**Alternativas:** (a) mantener indefinida con justificacion estadistica — se descarta por
autocontradiccion; (b) fijar un valor arbitrario — se descarta; el valor decidido (12 meses
rodantes) esta justificado por el ciclo anual de la tesis.

### D-L2 — Base de licitud: Ley 25.326 art. 5 inc. 2

**Decision:** sustituir "el legitimo interes de la organizacion" por la Ley 25.326 art. 5
inc. 2, **apartado d) relacion contractual/laboral** (NO apartado b), como base de licitud
del tratamiento operativo de datos de empleados (OQ-L2, resuelta 2026-10-12; candidatos
segun `marco-legal-ar-2026.md:552-554`). La organizacion es empleadora y trata datos de sus
propios empleados para gestionar incidentes internos de TI; el tratamiento es necesario para
cumplir la relacion laboral. Se distingue esta base operativa del consentimiento que §11.5
discute solo para el corpus de investigacion academica. Salvedad: el deber de informacion
del art. 6 subsiste y NO queda dispensado por usar el art. 5 inc. 2.

**Racional:** "legitimo interes" es la base del art. 6.1.f del RGPD y no existe como base
autonoma en la Ley 25.326; citarla como tal es juridicamente incorrecto para el derecho
argentino.

**Alternativas:** (a) fundar todo en consentimiento — se descarta para el tratamiento
operativo (los empleados reportan en ejercicio de sus funciones, no por consentimiento
libre); (b) dejar la redaccion vaga — se descarta, el objetivo es exactitud.

### D-L3 — Adecuacion europea: instrumento y direccion

**Decision:** en 11.1, nombrar y citar la Decision 2003/490/CE (30 de junio de 2003) y su
revalidacion de enero de 2024, y afirmar que la adecuacion cubre el flujo UE -> Argentina
unicamente. La transferencia Argentina -> Estados Unidos (Gemini, Twilio) NO esta amparada
por la adecuacion y requiere instrumento del art. 12. Eliminar la expresion
"bidireccionales".

**Racional:** `marco-legal-ar-2026.md:369-391` documenta la decision, la revalidacion y la
distincion clave de direccion; EE. UU. no integra la lista argentina de paises adecuados
(`:33-36`).

**Alternativas:** (a) omitir la adecuacion — se descarta, es pertinente como marco; (b)
mantener la redaccion vaga — se descarta por enganosa.

### D-L4 — Transferencia telefonica pre-pseudonimizacion

**Decision:** reescribir 11.3 para (1) nombrar a Twilio, (2) declarar que el audio crudo
del llamante y su numero telefonico se transfieren a un proveedor de EE. UU. ANTES de
cualquier pseudonimizacion, (3) describir el orden real grabar -> transferir/transcribir
-> pseudonimizar (`runbook-verificacion-telefonia-c52.md:13,20-21`; STT
`gemini-3.5-transcribe`), y (4) citar el instrumento de transferencia del art. 12
(consentimiento o clausulas contractuales modelo, Disposicion DNPDP 60/2016 / Resolucion
AAIP 198/2023). El DPA del proveedor se menciona como complemento, no como sustituto
(`marco-legal-ar-2026.md:538-542`).

**Racional:** afirmar "pseudonimizacion previa a la transmision" para telefonia es falso:
la pseudonimizacion de texto (regex Python) corre en el backend sobre el texto ya
transcrito, despues de que el audio crudo salio hacia Twilio y del STT. La ley argentina
exige un instrumento de transferencia (art. 12) que el DPA no reemplaza.

**Alternativas:** (a) limitar 11.3 a Gemini — se descarta, oculta la transferencia del
canal telefonico; (b) afirmar que la pseudonimizacion cubre tambien el audio — se descarta,
es factualmente falso.

### D-L5 — Plazo ARCO (cinco dias habiles)

**Decision:** el Capitulo 11 SI declara el plazo ARCO, expresado como **cinco dias habiles**
conforme al art. 16 (`marco-legal-ar-2026.md:230-232,550-551`). No se declara "cinco dias
corridos". OQ-L5 resuelta el 2026-10-12.

**Racional:** la fuente corrige explicitamente el plazo (la v7 decia "cinco dias
corridos"). Es un item del mismo bloque legal.

### D-L6 — Revision de vigencia de las fuentes juridicas

**Decision:** incorporar una revision explicita de vigencia de TODAS las fuentes legales
citadas en el Capitulo 11, realizada a una fecha declarada. El alcance cubre la Ley 25.326
y su decreto reglamentario, las disposiciones/resoluciones vigentes de la AAIP, el RGPD y
su base normativa, el estado de la Decision 2003/490/CE (revalidada en enero de 2024) y los
instrumentos de transferencia del art. 12. La revision MUST confirmar que cada norma citada
esta vigente, MUST descartar toda norma superada o derogada, y MUST registrar la fecha de la
revision legal en el Capitulo 11 o en el registro del dictamen.

**Racional:** hoy el change solo corrige UN instrumento (L3). Sin un control de vigencia,
una norma superada puede permanecer citada (por ejemplo, un decreto reglamentario o una
resolucion de la AAIP reemplazados). La vigencia es verificable y no requiere inventar
valores; es una tarea de control, distinta de la correccion puntual de L3.

**Alternativas:** (a) limitar la revision a la adecuacion europea (L3) — se descarta, deja
sin control al resto de las fuentes; (b) fijar una fecha de vigencia en el design — se
descarta, la fecha depende del momento de la revision del autor.

## Risks / Trade-offs

- Tocar `.tex` sin compilador local -> mitigar con `openspec validate` + revision en
  Overleaf + `rg` de control.
- Apartado del art. 5 inc. 2 (b o d) -> resuelto en OQ-L2 (2026-10-12): apartado d)
  relacion contractual/laboral; el texto cita "art. 5 inc. 2, apartado d)".
- Plazo de retencion -> resuelto en OQ-L1/L1b (2026-10-12): 12 meses rodantes desde la
  creacion del incidente, con anonimizacion irreversible al vencimiento.
- Solapamiento con c-76/c-77 -> mitigado: este change solo toca 11.1-11.3; 11.5 y los
  numeros quedan fuera.
- El ground truth afirmaba "nunca se cita el art. 12"; el texto si lo menciona en 11.1 ->
  mitigado explicitando en design y tareas que el requisito es citar el INSTRUMENTO, no
  solo el numero.
- Citar una norma superada (decreto reglamentario, resolucion AAIP, RGPD) sin revisar su
  vigencia -> mitigado con el grupo L6 y la fecha de revision registrada.

## Migration Plan

1. Reescribir `11-aspectos-legales.tex` §11.1 (L3), §11.2 (L1, L2) y §11.3 (L4).
2. Reconciliar la retencion en `05-arquitectura.tex:44` si el plazo elegido lo exige
   (declarar la distincion entre logs y incidentes).
3. Verificar por `rg` los barridos de control (ver `tasks.md`).
4. Append del grupo L1-L5 en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
5. Recompilar en Overleaf; verificar PDF sin errores fatales.
6. Rollback: `git checkout --` / `git revert`.

## Open Questions

- **OQ-L1 (RESUELTA, 2026-10-12):** plazo de conservacion de incidentes = **12 meses
  rodantes desde la creacion del incidente**. El ciclo estadistico de la tesis es anual
  (12/02/2026 -> 12/02/2027), lo que JUSTIFICA la longitud (12 meses); el texto de retencion
  declara el PERIODO (12 meses), NO las fechas calendario. Coherente con
  `05-arquitectura.tex:44` (los 30 dias son LOGS de ejecucion, un conjunto de datos distinto
  ya separado por la tarea 1.3). No se escriben fechas fijas en la regla de retencion.
- **OQ-L1b (RESUELTA, 2026-10-12):** mecanismo de supresion/disposicion al vencer el plazo =
  **anonimizacion** (anonimizacion irreversible: se eliminan los identificadores de modo que
  los datos ya no puedan vincularse a una persona). Es el mecanismo decidido.
- **OQ-L2 (RESUELTA, 2026-10-12):** apartado del art. 5 inc. 2 = **apartado d) relacion
  contractual/laboral** (NO apartado b). La organizacion es empleadora y trata datos de sus
  propios empleados para gestionar incidentes internos de TI; el tratamiento es necesario
  para cumplir la relacion laboral. Salvedades que se mantienen: (1) el deber de informacion
  del art. 6 subsiste y NO queda dispensado por usar el art. 5 inc. 2; (2) el consentimiento
  solo se discute para el corpus de investigacion (§11.5), NO para el tratamiento operativo.
- **OQ-L5 (RESUELTA, 2026-10-12):** el Capitulo 11 SI declara el plazo ARCO, expresado como
  **cinco dias habiles** (art. 16); nunca "cinco dias corridos".

---

## Anexo A — Evidencia verificada (verbatim, file:line)

> No re-investigar; usar tal cual al aplicar.

- `11-aspectos-legales.tex:12` (§11.2): "El principio de licitud establece que todo
  tratamiento debe ampararse en una base juridica valida; en este caso, dicha base se
  encuentra en el legitimo interes de la organizacion [...] El principio de limitacion del
  plazo de conservacion se traduce, para los incidentes, en una politica de conservacion
  indefinida justificada por el valor estadistico de los datos historicos [...] Los
  incidentes en estado cerrado se preservan como registro auditable permanente".
- `05-arquitectura.tex:44`: "Los registros de cada ejecucion se conservan durante 30 dias
  para fines de auditoria y diagnostico operativo."
- `11-aspectos-legales.tex.bak:12` (historico): "una politica de retencion de 90 dias para
  los registros operativos y de un ano para los datos de incidentes resueltos."
- `knowledge-base/10_preguntas_abiertas.md` (IN-05): "El bloqueo de escritura sobre
  incidentes cerrados esta implementado (C-23: `PATCH /api/v1/incidentes/{id}` devuelve 409
  si el estado es terminal). No se requiere purga automatica."
- `11-aspectos-legales.tex:8` (§11.1): "Argentina mantiene un regimen de adecuacion
  reconocido por la Comision Europea, lo cual facilita los flujos transfronterizos
  bidireccionales bajo determinadas condiciones."
- `11-aspectos-legales.tex:16` (§11.3): "el sistema aplica un procedimiento de
  pseudonimizacion previa a la transmision [...] Adicionalmente, la organizacion ha
  suscripto el acuerdo de procesamiento de datos provisto por el proveedor del servicio de
  inferencia."
- `docs/runbook-verificacion-telefonia-c52.md:13`: "Twilio graba, el backend descarga y
  transcribe con Gemini, pseudonimiza, persiste el ingreso y hace handoff autenticado a
  n8n". Modelo STT `gemini-3.5-transcribe` (`:61,330,377`).
- `docs/cumplimiento/marco-legal-ar-2026.md:33-36`: "Para transferencias a Estados Unidos
  rige el articulo 12 [...] Estados Unidos NO integra la lista argentina de paises con
  nivel adecuado, por lo que se requiere consentimiento expreso, clausulas contractuales
  modelo (Disposicion DNPDP 60/2016 y Resolucion AAIP 198/2023) o normas corporativas
  vinculantes".
- `docs/cumplimiento/marco-legal-ar-2026.md:37-39`: "La decision de adecuacion de la Union
  Europea respecto de Argentina (Decision 2003/490/CE) sigue vigente y fue revalidada en
  enero de 2024".
- `docs/cumplimiento/marco-legal-ar-2026.md:388-390`: "UE -> Argentina: Argentina es pais
  adecuado para la UE (Decision 2003/490/CE). Argentina -> EE. UU.: Estados Unidos no es
  pais adecuado para Argentina; se requiere consentimiento o clausulas contractuales
  modelo."
- `docs/cumplimiento/marco-legal-ar-2026.md:538-542`: "Transferencia a Gemini y Twilio
  (EE. UU.): Estados Unidos no es pais adecuado. La organizacion deberia apoyarse en
  clausulas contractuales modelo [...] o consentimiento expreso [...] La pseudonimizacion
  previa mitiga el riesgo, pero no sustituye el instrumento de transferencia."
- `docs/cumplimiento/marco-legal-ar-2026.md:552-554`: "la base de licitud de los empleados
  puede encuadrarse en el articulo 5, inciso 2, apartados b) o d) (obligacion legal /
  relacion laboral), pero el deber de informacion del articulo 6 subsiste."
- `docs/cumplimiento/marco-legal-ar-2026.md:230-232,550-551`: "la ley dice CINCO DIAS
  HABILES (art. 16, inc. 2). Corresponde corregir ese punto."
- `docs/seguridad/registro-requisitos-legales.md:25,30`: "Ley 25.326 art. 5 |
  Consentimiento libre, expreso e informado"; "Ley 25.326 art. 12 | Transferencias
  internacionales; EE. UU. no es pais adecuado".
