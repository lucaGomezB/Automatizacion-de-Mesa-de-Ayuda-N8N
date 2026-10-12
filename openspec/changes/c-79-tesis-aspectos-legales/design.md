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
- Sustituir "legitimo interes" por la base de licitud del art. 5 inc. 2 de la Ley 25.326.
- Citar el instrumento de adecuacion europea y corregir su direccion (UE -> AR).
- Divulgar la transferencia telefonica pre-pseudonimizacion (Twilio, audio crudo +
  numero) y citar el instrumento del art. 12.
- Registrar el plazo ARCO (cinco dias habiles, art. 16) sin inventar.

**Non-Goals:**

- No reescribir §11.4 (seguridad tecnica) ni §11.5 (consentimiento de investigacion,
  Hawthorne, supervision humana) — alcance de c-76/c-77.
- No modificar `App/**`, el `.bib`, ni los numeros del corpus.
- No emitir una conclusion juridica vinculante: el documento sigue siendo un relevamiento
  informativo, no asesoramiento juridico.
- No inventar el valor exacto de retencion, el apartado del art. 5 ni el plazo ARCO.

## Decisions

### D-L1 — Politica de retencion unica y reconciliada

**Decision:** reemplazar "conservacion indefinida" por un plazo explicito y justificado.
El diseño separa DOS conjuntos de datos con finalidades distintas:

- **Logs de ejecucion** (`05-arquitectura.tex:44`): 30 dias, finalidad de auditoria y
  diagnostico operativo. Se mantiene.
- **Incidentes**: registro con valor operativo, historico y estadistico. Se les asigna un
  plazo acotado (el valor exacto es OQ-L1).

La reconciliacion consiste en declarar explicitamente que son conjuntos distintos con
finalidades distintas, de modo que 11.2 y 05:44 no se contradigan. El bloqueo de escritura
sobre tickets cerrados (C-23, 409) se presenta como control de integridad de auditoria,
no como politica de retencion.

**Racional:** "conservacion indefinida" contradice el principio de limitacion temporal que
el propio parrafo enuncia; un plazo concreto y justificado es lo que el principio exige.
El valor no se inventa porque es una decision del autor con consecuencias operativas
(volumen de datos, requisitos de la organizacion adoptante).

**Alternativas:** (a) mantener indefinida con justificacion estadistica — se descarta por
autocontradiccion; (b) fijar un valor arbitrario en el design — se descarta, el autor debe
decidirlo (OQ-L1).

### D-L2 — Base de licitud: Ley 25.326 art. 5 inc. 2

**Decision:** sustituir "el legitimo interes de la organizacion" por la Ley 25.326 art. 5
inc. 2 como base de licitud del tratamiento operativo de datos de empleados. Los apartados
candidatos son b) (obligacion legal / funciones del Estado) y d) (relacion contractual,
cientifica o profesional cuando resulte necesaria para su cumplimiento), segun
`marco-legal-ar-2026.md:552-554`. Se distingue esta base operativa del consentimiento que
§11.5 discute solo para el corpus de investigacion academica.

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

**Decision:** si el Capitulo 11 declara un plazo para rectificacion/actualizacion/
supresion, expresarlo como cinco dias habiles conforme al art. 16 (`marco-legal-ar-2026.md:230-232,550-551`).
No se declara "cinco dias corridos". Si el autor prefiere no declarar plazo, el requisito
de spec se cumple por vacuidad; se registra como OQ-L5.

**Racional:** la fuente corrige explicitamente el plazo (la v7 decia "cinco dias
corridos"). Es un item opcional del mismo bloque legal.

## Risks / Trade-offs

- Tocar `.tex` sin compilador local -> mitigar con `openspec validate` + revision en
  Overleaf + `rg` de control.
- Elegir un apartado del art. 5 inc. 2 (b o d) sin el autor -> mitigado dejandolo como
  OQ-L2; el texto puede citar "art. 5 inc. 2" y el apartado se precisa al aplicar.
- Fijar un plazo de retencion sin decision del autor -> mitigado con OQ-L1; el design no
  inventa el valor.
- Solapamiento con c-76/c-77 -> mitigado: este change solo toca 11.1-11.3; 11.5 y los
  numeros quedan fuera.
- El ground truth afirmaba "nunca se cita el art. 12"; el texto si lo menciona en 11.1 ->
  mitigado explicitando en design y tareas que el requisito es citar el INSTRUMENTO, no
  solo el numero.

## Migration Plan

1. Reescribir `11-aspectos-legales.tex` §11.1 (L3), §11.2 (L1, L2) y §11.3 (L4).
2. Reconciliar la retencion en `05-arquitectura.tex:44` si el plazo elegido lo exige
   (declarar la distincion entre logs y incidentes).
3. Verificar por `rg` los barridos de control (ver `tasks.md`).
4. Append del grupo L1-L5 en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
5. Recompilar en Overleaf; verificar PDF sin errores fatales.
6. Rollback: `git checkout --` / `git revert`.

## Open Questions

- **OQ-L1 (ABIERTA):** valor exacto del plazo de conservacion de incidentes. Candidatos a
  evaluar por el autor: alinear con un periodo acotado (p. ej. el ciclo estadistico de la
  tesis) o un plazo fijo de retencion con anonimizacion posterior. El design NO fija el
  valor.
- **OQ-L2 (ABIERTA):** apartado exacto del art. 5 inc. 2 (b obligacion legal / d relacion
  laboral). El autor debe elegir; el texto puede citar el inciso y precisar el apartado al
  aplicar.
- **OQ-L5 (ABIERTA):** si el Capitulo 11 declara o no el plazo ARCO. Si lo declara, el
  valor correcto es cinco dias habiles (art. 16).

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
