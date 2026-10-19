# Tasks: c-79 — Aspectos legales (11.1-11.3)

> Convencion de archivos: `S = docs/Tesis/v9 (IA)/paper/sections`;
> `L = docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex`;
> `A = docs/Tesis/v9 (IA)/paper/sections/05-arquitectura.tex`;
> `D = docs/Tesis/Correcciones/dictamen-correcciones.md`.
> Verificacion de texto: `rg` sobre `S` (sin compilador LaTeX local).
> Recompilacion: Overleaf (tarea final). No se edita `App/**`, ni c-76/c-77/c-78,
> ni `CHANGES.md`. Alcance: 11.1-11.3. §11.4 y §11.5 quedan fuera (c-76/c-77).

## 1. L1 — Plazo de conservacion unico y consistente

- [x] 1.1 En `L:12` (§11.2), reemplazar "una politica de conservacion indefinida justificada por el valor estadistico" por un plazo de retencion explicito y justificado para los incidentes: **12 meses rodantes desde la creacion del incidente** (OQ-L1, resuelta 2026-10-12; el ciclo estadistico anual justifica la longitud, pero el texto declara el periodo, NO las fechas). Verificar con `rg -ni "conservacion indefinida|indefinidamente" L` sin coincidencias en el pasaje de retencion de incidentes.
- [x] 1.2 En `L:12`, presentar el bloqueo de escritura sobre tickets cerrados (C-23, 409) como control de integridad de auditoria, NO como politica de retencion. Verificar con `rg -n "409|auditable permanente|integridad" L` y lectura del pasaje.
- [x] 1.3 Reconciliar la retencion en `A:44`: declarar de forma explicita que los logs de ejecucion (30 dias) y los incidentes son conjuntos de datos distintos con finalidades distintas, de modo que 11.2 y 05:44 no se contradigan. Verificar con `rg -n "30 dias|incidentes" A` y lectura del pasaje.
- [x] 1.4 Confirmar que `L:12` declara UN solo plazo de retencion para incidentes y que no queda una segunda regla contradictoria. Verificar con `rg -ni "retencion|conservacion" L` y lectura del parrafo completo.
- [x] 1.5 En `L:12` (§11.2), declarar una politica explicita de supresion/disposicion al vencer el plazo de retencion mediante **anonimizacion irreversible** (OQ-L1b, resuelta 2026-10-12) y reconciliar la contradiccion con "registro auditable permanente": ese registro es un control de integridad de auditoria, NO una politica de retencion ni una excepcion permanente al vencimiento. Verificar con `rg -ni "supresion|disposicion|anonimiz|borrado" L` y lectura del pasaje.

## 2. L2 — Base de licitud (Ley 25.326 art. 5 inc. 2)

- [x] 2.1 En `L:12` (§11.2), eliminar "el legitimo interes de la organizacion" como base de licitud y reemplazarlo por la Ley 25.326 art. 5 inc. 2, **apartado d) relacion contractual/laboral** (OQ-L2, resuelta 2026-10-12; NO apartado b). Verificar con `rg -ni "legitimo interes" L` sin coincidencias.
- [x] 2.2 En `L:12`, citar el articulo 5 inciso 2 de la Ley 25.326 de forma textual (con `\parencite{Ley25326_2000}` o referencia equivalente). Verificar con `rg -n "art.culo 5|inciso 2|5 inc" L`.
- [x] 2.3 En `L:12`, distinguir la base de licitud operativa del consentimiento que §11.5 discute solo para el corpus de investigacion, y dejar constancia de que el deber de informacion del art. 6 subsiste (no queda dispensado por usar el art. 5 inc. 2). Verificar con `rg -ni "consentimiento|investigacion|deber de informacion|articulo 6" L` en contexto de 11.2.

## 3. L3 — Adecuacion europea (instrumento y direccion)

- [x] 3.1 En `L:8` (§11.1), citar el instrumento de adecuacion: Decision 2003/490/CE (30 de junio de 2003) y su revalidacion de enero de 2024. Verificar con `rg -n "2003/490|490/CE|enero de 2024|revalid" L`.
- [x] 3.2 En `L:8`, corregir la direccion: la adecuacion cubre UE -> Argentina unicamente; la transferencia Argentina -> Estados Unidos (Gemini, Twilio) NO esta amparada por ella. Verificar con `rg -ni "bidireccional" L` sin coincidencias y lectura del pasaje.
- [x] 3.3 En `L:8`, afirmar que EE. UU. no es pais adecuado para Argentina y que la transferencia hacia EE. UU. requiere instrumento del art. 12. Verificar con `rg -n "Estados Unidos|no es pais adecuado|articulo 12" L`.

## 4. L4 — Transferencia telefonica previa a la pseudonimizacion

- [x] 4.1 En `L:16` (§11.3), nombrar a Twilio como proveedor de telefonia con sede en Estados Unidos. Verificar con `rg -n "Twilio" L`.
- [x] 4.2 En `L:16`, declarar que el audio crudo del llamante y su numero telefonico se transfieren a EE. UU. ANTES de cualquier pseudonimizacion. Verificar con `rg -ni "audio|grabacion|numero" L` en contexto telefonico.
- [x] 4.3 En `L:16`, describir el orden real del canal telefonico: grabar -> transferir/transcribir -> pseudonimizar (fuente `runbook-verificacion-telefonia-c52.md:13`; STT `gemini-3.5-transcribe`). Verificar con `rg -ni "pseudonimizacion previa a la transmision" L` sin coincidencias para el canal telefonico.
- [x] 4.4 En `L:16`, citar el instrumento de transferencia del art. 12 de la Ley 25.326 (consentimiento o clausulas contractuales modelo) y aclarar que el DPA del proveedor es complemento, no sustituto. Verificar con `rg -ni "clausulas contractuales|acuerdo de procesamiento|articulo 12" L`.

## 5. L5 — Plazo ARCO

- [x] 5.1 El Capitulo 11 SI declara el plazo para rectificacion/actualizacion/supresion; expresarlo como **cinco dias habiles** conforme al art. 16 (OQ-L5, resuelta 2026-10-12); no usar "cinco dias corridos". Verificar con `rg -ni "cinco dias|5 dias|dias habiles|dias corridos" L`.

## L6 — Revision de vigencia de fuentes juridicas

- [x] L6.1 Confirmar que cada norma citada en 11.1-11.3 esta vigente a la fecha de revision: Ley 25.326 y su decreto reglamentario, disposiciones/resoluciones vigentes de la AAIP, RGPD, estado de la Decision 2003/490/CE y los instrumentos de transferencia del art. 12. Registrar la evidencia (fuente consultada y fecha). Verificar con `rg -n "Ley 25.326|decreto|AAIP|RGPD|2003/490|articulo 12" L`.
- [x] L6.2 Confirmar que no se cita ninguna norma superada o derogada; si se detecta, corregir la referencia. Verificar por lectura de las referencias legales de 11.1-11.3.
- [x] L6.3 Registrar la fecha de la revision legal y el resultado del control de vigencia en `D`. Verificar con `rg -ni "vigencia|revision legal|fecha de revision" D`.

## 6. Registro del dictamen

- [x] 6.1 Agregar a `D` la seccion `## Grupo: Aspectos legales (L1-L6)` mapeando L1-L6 al item 25 del plan, con la evidencia verificada (retencion indefinida vs 30 dias de logs y politica de supresion, legitimo interes vs art. 5 inc. 2, Decision 2003/490/CE y direccion UE -> AR, transferencia pre-pseudonimizacion a Twilio y art. 12, revision de vigencia de fuentes, plazo ARCO art. 16). Verificar con `rg -n "Grupo: Aspectos legales|L1|L2|L3|L4|L6" D`.

## 7. Verificacion final y recompilacion

- [x] 7.1 Barrido de control: `rg -ni "conservacion indefinida|legitimo interes|bidireccional|pseudonimizacion previa a la transmision" L` sin residuos en los pasajes de 11.1-11.3 (Twilio y la retencion quedan explicitados). Registrar la salida.
- [x] 7.2 Confirmar por lectura que 11.1-11.3 cubren los puntos L1-L6 y que no se introdujeron afirmaciones juridicas nuevas sin fuente (no inventar valores; aplicar los valores resueltos: OQ-L1 = 12 meses rodantes, OQ-L1b = anonimizacion, OQ-L2 = art. 5 inc. 2 apartado d), OQ-L5 = cinco dias habiles).
- [x] 7.3 Confirmar que no se tocaron §11.4 ni §11.5 ni artefactos de c-76/c-77/c-78. Verificar con `git diff --stat` y lectura del rango editado.
- [ ] 7.4 (DIFERIDO a Overleaf: no hay toolchain LaTeX local; el texto ya fue verificado con `rg` y `openspec validate --strict`) Recompilar la tesis en Overleaf (`main.tex`, XeLaTeX) y verificar PDF sin errores fatales. Registrar el resultado.
- [x] 7.5 Ejecutar `openspec validate c-79-tesis-aspectos-legales --strict` y confirmar que pasa.
