# Tasks: Acreditar el nivel pago y el consentimiento (c-193)

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` =
`docs/Tesis/Correcciones/`; `CM/` = `docs/campana-medicion/`. "B4" e "item 13" remiten al
dictamen CONEAU `auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md` (2026-11-09) sobre
`v1.2.13`. Anclas por texto citado (`rg -n`). Linea base: 118 paginas; resumen y abstract
<= 250 palabras. No se edita `App/`, `n8n/`, `evaluation/`, `data/` ni figuras. En la prosa del
registro usar "seccion N (`archivo.tex`)". Release `v1.2.15`. Los originales firmados, el
comprobante de facturacion y la correspondencia alias-identidad NUNCA entran al repositorio ni a
Engram.

## 0. Verificacion de evidencia y linea base (solo lectura; bloqueante para el apply)

- [x] 0.1 Confirmar la rama `change/c-193-acreditar-el-nivel-pago-y-el-consentimiento` y que
  existe `.openspec.yaml`; trabajar en esa rama.
- [x] 0.2 Compilar la linea base en el entorno de registro (Docker `texlive-thesis`): anotar
  paginas (esperado 118), `Overfull` (cantidad y maximo) y estado de `verify_citations.py`.
  Safety net: `python C/verificar_matriz_trazabilidad.py` -> 0 fallas; `cd C/ && python -m
  unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.
- [x] 0.3 **Confirmar la evidencia fisica** (design D0): que existen (a) el comprobante de
  facturacion o la captura del proyecto en el nivel pago de la Gemini API y (b) las cuatro
  constancias firmadas de `E1`, `E2`, `O1` y `O2`, con la fecha de informacion verbal y de
  confirmacion de cada una. **Si alguna no existe, detener el apply y consultar a los autores**;
  el texto no declara un procedimiento sin respaldo.
- [x] 0.4 Leer el texto exacto de `S/11-aspectos-legales.tex:16`
  (`subsec:transferencia-internacional`) y `:34` (`subsec:consentimiento-derechos`); guardar el
  fragmento de partida en el scratchpad.
- [x] 0.5 Registrar en `C/dictamen-correcciones.md` (seccion c-193) la respuesta de los autores:
  comprobante de facturacion y constancias firmadas disponibles, bajo custodia del director.

## 1. Nivel pago acreditado por el registro de facturacion (B4)

- [x] 1.1 `S/11-aspectos-legales.tex:16` (oracion final de `subsec:transferencia-internacional`):
  conservar la oracion del nivel pago con creditos prepagos y la cita
  `\parencite{Google2026_gemini_api_pricing}`; retirar `(\path{docs/gemini-api-key-setup.md})`;
  agregar "El comprobante de facturacion del nivel pago se conserva bajo custodia del director
  de la tesis y no se versiona porque contiene datos de la cuenta." (design D1).
- [x] 1.2 Verificacion: `rg -n "gemini-api-key-setup" S/11-aspectos-legales.tex` = 0;
  `Google2026_gemini_api_pricing` sigue presente; la oracion del comprobante figura.
- [x] 1.3 Registrar en `C/dictamen-correcciones.md` la correccion de B4 (guia de configuracion
  retirada; acreditacion por el comprobante en custodia).

## 2. Consentimiento y plantilla (item 13, B4)

- [x] 2.1 `S/11-aspectos-legales.tex:34` (`subsec:consentimiento-derechos`): reemplazar la
  oracion que declara la ausencia de registro por el texto de design D2 (informacion verbal
  previa; confirmacion escrita posterior; originales en el expediente fisico bajo custodia del
  director y no versionados; el repositorio conserva la plantilla y el registro de que se obtuvo
  para los cuatro participantes). Conservar el resto del parrafo.
- [x] 2.2 Crear `CM/confirmacion-posterior-consentimiento.md` de una pagina (design D3): los
  cuatro puntos, marcadores de posicion sin nombres y la tabla
  `alias, rol, fecha_informacion_verbal, fecha_confirmacion, custodia`; declarar que los
  originales firmados los conserva el director y que solo la plantilla y el registro entran al
  repositorio y a Engram.
- [x] 2.3 Verificacion de contenido: `rg -n "No se conservo un registro" S/11-aspectos-legales.tex`
  = 0; figuran "verbalmente", "confirmacion escrita", "expediente fisico" y "custodia"; la tabla
  de la plantilla tiene las cinco columnas.
- [x] 2.4 Verificacion de datos personales: `rg -n "P[0-9]+" S/11-aspectos-legales.tex CM/` no
  devele nombres; ningun nombre real en el texto ni en la plantilla (solo alias y `P<n>`).

## 3. Registro, CHANGES y Anexo I

- [x] 3.1 `C/dictamen-correcciones.md`: seccion "Dictamen v10 / v1.2.13 (2026-11-09) - c-193"
  con la matriz en el formato de c-192 (Rec | Observacion | Correccion | Archivo | Estado) que
  cubra B4 y el item 13, la decision de custodia de la evidencia fisica y el libro mayor de
  paginas. Si se usa la matriz estricta de 7 columnas, el verificador SHALL dar 0 fallas.
- [x] 3.2 `CHANGES.md`: agregar la FASE 58 con el bloque de c-193 (alcance, decisiones,
  dependencias, gobernanza MEDIUM/HIGH, "Leer antes"), al estilo de la FASE 57.
- [x] 3.3 `S/12-anexos.tex` (Anexo I, `sec:anexo-trazabilidad`): declarar B4 y el item 13
  cerrados por c-193 (solo si no agrega altura neta; si agrega, compensar por D6).
- [x] 3.4 Verificacion: `python C/verificar_matriz_trazabilidad.py` -> 0 fallas; la seccion c-193
  cubre las dos recomendaciones pendientes.

## 4. Compilacion y artefactos generados

- [x] 4.1 Recompilar en el entorno de registro: 0 errores, 0 referencias o citas indefinidas,
  0 `multiply defined`, `main.blg` sin WARN/ERROR, 0 `??` en `pdftotext`, `Overfull` no mayor que
  la linea base; `verify_citations.py` PASS.
- [x] 4.2 Paginas <= 118 (D6); si se supera, recortar prosa en los parrafos tocados y
  recompilar; si aun asi no, detener y consultar. Resumen y abstract <= 250 palabras (sin tocar).
- [x] 4.3 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py`
  (no vacio) y `docs/Tesis/v10 (IA)/paper/compilacion.md` con `C/resumir_registro_compilacion.py`;
  el SHA-256 de `compilacion.md` debe coincidir con `sha256sum main.pdf`.
- [x] 4.4 Registrar el libro mayor de paginas y palabras en `C/dictamen-correcciones.md`
  (seccion c-193).

## 5. Release `v1.2.15` y archivo

- [x] 5.1 `openspec validate c-193-acreditar-el-nivel-pago-y-el-consentimiento --strict
  --no-interactive` pasa.
- [x] 5.2 `S/12-anexos.tex` (Anexo B, `sec:anexo-repositorio`): dejar la oracion de verificacion
  `git rev-list -n1 v1.2.15` y el nombre de la release entregada como `v1.2.15`; retirar el
  arrastre de `v1.2.13` (decision D5; si se limita el alcance, declarar el residuo). El texto
  MUST NOT imprimir el hash de una release previa.
- [x] 5.3 (Orquestador) Commit de contenido en
  `change/c-193-acreditar-el-nivel-pago-y-el-consentimiento` con la oracion de verificacion en el
  Anexo B y la evidencia ya versionada; tag anotado `v1.2.15`; commit siguiente que reemplaza la
  oracion por el hash completo del commit de contenido (design D5).
- [x] 5.4 Verificacion de la regla de hash: `git diff --stat v1.2.15 HEAD -- "docs/Tesis/v10
  (IA)/paper/sections"` = una linea; `pdftotext` del PDF etiquetado `v1.2.15` sin el hash de una
  release previa (`7937efd`, `f527722` ni `8deb79f`).
- [x] 5.5 (Orquestador) `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` (nunca
  `--all`), commit de `.engram/`, PR contra `main` (nunca push directo) y archive del change.
