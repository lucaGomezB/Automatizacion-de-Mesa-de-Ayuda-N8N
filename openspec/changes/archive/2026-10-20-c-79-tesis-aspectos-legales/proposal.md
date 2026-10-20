# Proposal: c-79 — Aspectos legales (11.1-11.3)

## Why

La auditoria de la tesis (plan de correccion, item 25, §11.2) detecto que el
Capitulo 11 (`docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex`) contiene
cuatro errores de correccion juridica en las secciones 11.1-11.3:

- **Plazo de conservacion contradictorio.** `11-aspectos-legales.tex:12` (§11.2)
  anuncia "el principio de limitacion del plazo de conservacion" y acto seguido
  declara "conservacion indefinida" para los incidentes, justificada por su "valor
  estadistico". No hay un plazo concreto y contradice los 30 dias de logs de
  ejecucion de `05-arquitectura.tex:44`.
- **Base de licitud legalmente incorrecta.** `11-aspectos-legales.tex:12` funda el
  tratamiento en "el legitimo interes de la organizacion". "Legitimo interes" es una
  base del RGPD (art. 6.1.f) que NO existe como base autonoma en la Ley 25.326.
- **Adecuacion europea vaga y mal direccionada.** `11-aspectos-legales.tex:8` (§11.1)
  menciona un "regimen de adecuacion reconocido por la Comision Europea" sin citar el
  instrumento y describiendo flujos "bidireccionales", lo cual es enganoso.
- **Pseudonimizacion previa falsa para telefonia.** `11-aspectos-legales.tex:16`
  (§11.3) afirma "pseudonimizacion previa a la transmision" y solo discute Gemini;
  nunca menciona a Twilio, aunque el audio crudo del llamante llega a EE. UU. antes
  de cualquier pseudonimizacion.

Corregir esto es un requisito de exactitud legal y privacidad de governance HIGH. No
solapa con c-76 (numeros del corpus y ventana temporal) ni con c-77 (estadistica
inferencial y 11.5 TLS/supervision humana): este change cubre 11.1-11.3.

## What Changes

### Grupo Aspectos legales (L1-L6) — plan de auditoria item 25

| Id | Punto | Correccion |
|----|-------|-----------|
| L1 | Plazo de conservacion y politica de supresion | Reemplazar "conservacion indefinida" por UNA politica de retencion concreta y justificada, consistente entre 11.2 y `05-arquitectura.tex:44` (30 dias de logs). Plazo decidido: **12 meses rodantes desde la creacion del incidente** (OQ-L1, resuelta 2026-10-12; el ciclo estadistico anual de la tesis justifica la longitud, pero el texto declara el periodo, NO las fechas). Al vencer el plazo, los datos de incidentes se **anonimizan** (anonimizacion irreversible; OQ-L1b, resuelta 2026-10-12). Reconciliar la contradiccion con "registro auditable permanente". |
| L2 | Base legal | Reemplazar "legitimo interes de la organizacion" por la Ley 25.326 art. 5 inc. 2, **apartado d) relacion contractual/laboral** (OQ-L2, resuelta 2026-10-12; NO apartado b), citando el articulo. El deber de informacion del art. 6 subsiste y no queda dispensado; el consentimiento solo se discute para el corpus de investigacion (§11.5). |
| L3 | Adecuacion europea | Nombrar el instrumento (Decision 2003/490/CE, 30 de junio de 2003) y su revalidacion de enero de 2024; corregir la direccion: la adecuacion cubre UE -> Argentina unicamente y NO autoriza Argentina -> Estados Unidos. |
| L4 | Transferencia previa | Nombrar a Twilio y revelar la transferencia de audio crudo + numero del llamante a EE. UU. ANTES de la pseudonimizacion; citar el instrumento de transferencia del art. 12 (consentimiento o clausulas contractuales modelo). |
| L5 | ARCO | El Capitulo 11 SI declara el plazo de rectificacion/supresion, expresado como **cinco dias habiles** (art. 16; OQ-L5, resuelta 2026-10-12); nunca "cinco dias corridos". |
| L6 | Revision de vigencia de fuentes | Verificar que TODAS las normas citadas en el Capitulo 11 estan vigentes a la fecha de revision (Ley 25.326 y su decreto reglamentario, disposiciones/resoluciones vigentes de la AAIP, RGPD, estado de la Decision 2003/490/CE, instrumentos de transferencia del art. 12); que no se cite ninguna norma superada; y registrar la fecha de la revision legal. No se inventa ningun valor: es una tarea de verificacion. |

Detalle de cada item:

- **L1 — Conservacion y supresion**: el texto MUST dejar de declarar "conservacion
  indefinida" para los incidentes y MUST declarar un plazo unico y explicito,
  coherente con `05-arquitectura.tex:44` (logs de ejecucion: 30 dias). Plazo decidido:
  **12 meses rodantes desde la creacion del incidente** (OQ-L1, resuelta 2026-10-12);
  el ciclo estadistico anual de la tesis justifica la longitud, pero el texto declara
  el periodo (12 meses), NO las fechas calendario. Al vencer el plazo, los datos de
  incidentes se **anonimizan** (anonimizacion irreversible; OQ-L1b, resuelta
  2026-10-12). El texto MUST presentar "registro auditable permanente" (bloqueo de
  escritura sobre tickets cerrados, PATCH -> 409, C-23) como control de integridad de
  auditoria, NO como politica de retencion.
- **L2 — Base legal**: el texto MUST citar la Ley 25.326 art. 5 inc. 2, **apartado d)
  relacion contractual/laboral** (OQ-L2, resuelta 2026-10-12; NO apartado b), como base
  de licitud del tratamiento operativo de datos de empleados (la organizacion es
  empleadora y trata datos de sus propios empleados), y MUST dejar de usar "legitimo
  interes" como base autonoma. El deber de informacion del art. 6 subsiste. El
  consentimiento solo se discute para el corpus de investigacion (11.5), no para el
  tratamiento operativo.
- **L3 — Adecuacion**: el texto MUST citar la Decision 2003/490/CE y su revalidacion
  de enero de 2024, y MUST dejar de describir los flujos como "bidireccionales". La
  adecuacion habilita UE -> Argentina; la transferencia Argentina -> Estados Unidos
  (Gemini, Twilio) NO esta amparada por ella y requiere instrumento del art. 12.
- **L4 — Transferencia telefonica**: el texto MUST nombrar a Twilio, MUST declarar
  que el audio crudo del llamante (y su numero) se transfiere a un proveedor de
  EE. UU. antes de la pseudonimizacion (orden: grabar -> transferir/transcribir ->
  pseudonimizar), y MUST citar el instrumento del art. 12. El acuerdo de
  procesamiento de datos (DPA) NO sustituye ese instrumento.
- **L6 — Vigencia de fuentes**: el texto MUST basarse solo en normas vigentes a la
  fecha de revision. Debe revisarse la vigencia de la Ley 25.326 y su decreto
  reglamentario, de las disposiciones/resoluciones vigentes de la AAIP, del RGPD, del
  estado de la Decision 2003/490/CE y de los instrumentos de transferencia del art. 12,
  sin citar normas superadas, y MUST registrarse la fecha de la revision legal. Es una
  tarea de verificacion: no introduce valores nuevos.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: se agregan requisitos de correccion legal para las secciones
  11.1-11.3 del Capitulo 11 (plazo de conservacion unico y consistente con una
  politica explicita de supresion/disposicion, base de licitud conforme a la Ley
  25.326 art. 5 inc. 2, adecuacion europea citada y direccionada, divulgacion de la
  transferencia telefonica pre-pseudonimizacion con el instrumento del art. 12, y
  vigencia de las fuentes juridicas citadas). Se actualiza el requisito de calidad de
  referencias legales del capitulo. `evaluation-framework` NO se modifica.

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex` (§11.1, §11.2, §11.3)
- `docs/Tesis/v9 (IA)/paper/sections/05-arquitectura.tex` (reconciliacion de la
  retencion en la linea 44)
- `docs/Tesis/Correcciones/dictamen-correcciones.md` (nuevo grupo de registro)
- `openspec/specs/tesis-document/spec.md` (delta aplicado al archivar)

No se toca `App/**`. No se modifican artefactos de c-76, c-77 ni c-78. No se edita
`CHANGES.md`. No se recompila localmente (Overleaf).

## Rollback Plan

`git checkout --` sobre `11-aspectos-legales.tex` y `05-arquitectura.tex`, o
`git revert` del commit del change. Los artefactos OPSX se descartan con el
directorio del change.

## Success Criteria

- [ ] §11.2 declara un plazo de conservacion unico y explicito para los incidentes
      (12 meses rodantes desde la creacion del incidente), consistente con
      `05-arquitectura.tex:44`, y una politica explicita de supresion/disposicion al
      vencer el plazo (anonimizacion irreversible); el bloqueo de tickets cerrados no se
      presenta como politica de retencion.
- [ ] §11.2 funda la licitud en la Ley 25.326 art. 5 inc. 2, apartado d) relacion
      contractual/laboral, y NO usa "legitimo interes" como base autonoma; el deber de
      informacion del art. 6 subsiste.
- [ ] §11.1 cita la Decision 2003/490/CE y su revalidacion de enero de 2024, y
      afirma que la adecuacion cubre UE -> Argentina, no Argentina -> Estados Unidos.
- [ ] §11.3 nombra a Twilio, declara la transferencia de audio crudo + numero del
      llamante antes de la pseudonimizacion y cita el instrumento del art. 12.
- [ ] §11.1-11.3 solo citan normas vigentes a la fecha de revision (Ley 25.326 y su
      decreto reglamentario, disposiciones/resoluciones de la AAIP, RGPD, Decision
      2003/490/CE, instrumentos del art. 12), sin normas superadas, y queda registrada
      la fecha de la revision legal.
- [ ] §11.1-11.3 declaran el plazo ARCO como cinco dias habiles (art. 16); no usan
      "cinco dias corridos".
- [ ] Las Open Questions L1 (12 meses rodantes), L1b (anonimizacion), L2 (art. 5 inc. 2,
      apartado d) y L5 (cinco dias habiles) quedan resueltas y registradas (2026-10-12).
- [ ] `openspec validate c-79-tesis-aspectos-legales --strict` pasa.
- [ ] El PDF se recompila en Overleaf sin errores fatales (tarea posterior; no hay
      toolchain LaTeX local).
