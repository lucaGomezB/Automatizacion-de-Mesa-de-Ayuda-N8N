## 1. Preparacion y red de seguridad

- [x] 1.1 Activar el hook y confirmar estado del change (`git config core.hooksPath .githooks`; `openspec status --change c-66-privacidad-transferencias --json`). Verificacion: el status lista proposal/specs/design como `done`.
- [x] 1.2 Correr la red de seguridad backend de la guarda antes de tocar nada (`cd App/Backend; pytest tests/test_runtime_cost_guard.py -q`) y registrar el baseline (N tests pasando). Verificacion: baseline capturado; si hay fallos, detener y reportarlos como preexistentes.
- [x] 1.3 Correr la red de seguridad frontend de la pagina de reporte (`cd App/Frontend; npm run test -- IncidenteForm`) y registrar el baseline. Verificacion: baseline capturado.

## 2. Seudonimizacion del numero de origen en logs del guarda (T)

- [x] 2.1 RED: agregar en `App/Backend/tests/test_runtime_cost_guard.py` tests que fallan porque hoy se emite el numero crudo: (a) el evento de disparo con origen NO contiene el numero crudo; (b) el evento de almacen no disponible NO contiene el numero crudo. Verificacion: `cd App/Backend; pytest tests/test_runtime_cost_guard.py -q` falla en los casos nuevos.
- [x] 2.2 GREEN: implementar el helper de identificador derivado no reversible (HMAC-SHA-256 con la clave DEDICADA `cost_guard_caller_hmac_key`, truncado; ver design.md D1/D9) y reemplazar `caller=caller` en `_log_tripped` y `_log_store_unavailable` (`App/Backend/app/cost_guard/guard.py`) por el identificador derivado. Verificacion: los tests nuevos pasan y la suite de la guarda sigue verde.
- [x] 2.3 TRIANGULATE: agregar casos con entradas distintas: (a) el mismo origen en la misma ventana produce el mismo identificador derivado (correlacion); (b) dos origenes distintos producen identificadores distintos; (c) el disparo por origen sigue operando (limitacion por origen preservada); (d) el corpus no incluye el numero de origen. Verificacion: todos los casos pasan.
- [x] 2.4 REFACTOR: encapsular la derivacion en un helper del paquete `cost_guard` y dejar `guard.py` legible, sin cambiar comportamiento. Verificacion: `cd App/Backend; pytest tests/test_runtime_cost_guard.py -q` verde tras cada paso.
- [x] 2.5 Verificar que `evaluate(provider, caller, amount)` conserva su contrato hacia las rutas (`routes/cost_guard.py`, `routes/telefonia.py`) y que la purga por ventana no cambia. Verificacion: `cd App/Backend; pytest -m "not integration" -q` verde.
- [x] 2.6 RED (clave dedicada): agregar en `App/Backend/tests/test_runtime_cost_guard.py` un test que falla porque la derivacion NO esta ligada a una clave dedicada: la guarda usa la clave de configuracion `cost_guard_caller_hmac_key` para derivar el identificador y NO la clave de pseudonimizacion (`pseudonymization_encryption_key`). Verificacion: el test nuevo falla al no existir el setting ni el uso de la clave dedicada.
- [x] 2.7 GREEN (configuracion de la clave dedicada): agregar la variable requerida `cost_guard_caller_hmac_key` en `App/Backend/app/config/settings.py`; documentar `COST_GUARD_CALLER_HMAC_KEY` y su comando de generacion en `App/Backend/.env.example`; proveerla en `App/Backend/tests/conftest.py` (donde se aportan las demas settings requeridas); agregar la dummy en `.github/workflows/ci.yml` (env del job `backend-tests`). Verificacion: el test 2.6 pasa y `cd App/Backend; pytest -m "not integration" -q` verde.
- [x] 2.8 TRIANGULATE (rotacion de clave): agregar un test que verifica que (a) reemplazar/rotar `cost_guard_caller_hmac_key` cambia el identificador derivado para el mismo numero; (b) el numero crudo nunca aparece en el identificador ni en el evento; (c) con la misma clave el identificador es estable dentro de la ventana. Verificacion: los tres casos pasan y no dependen de la clave de pseudonimizacion.

## 3. Justificacion por minimizacion del contacto del directorio (D)

- [x] 3.1 Crear `docs/seguridad/justificacion-minimizacion-directorio.md` que documente la justificacion por minimizacion (auditabilidad directa + control de acceso por rol + red aislada), alinee con la tesis (`05-arquitectura.tex:98`, `11-aspectos-legales.tex:24`) y registre el cifrado de aplicacion y el indice ciego como alternativas evaluadas y descartadas, vinculando la decision al hallazgo 5.34/8.12 sobre `models/empleado.py`. Verificacion: el documento existe, contiene finalidad/razon, alternativas descartadas y el vinculo con el hallazgo.
- [x] 3.2 Referenciar el documento desde `docs/seguridad/README.md` (indice y mapa de trazabilidad 5.34/8.12) sin romper referencias cruzadas. Verificacion: el indice lista el documento y la referencia resuelve a un archivo existente.
- [x] 3.3 Confirmar que no se agrega cifrado ni indice ciego (sin regresion de DIR-005). Verificacion: `grep -rn "EncryptedText\|blind" App/Backend/app/models/empleado.py` no arroja usos nuevos; `cd App/Backend; pytest tests/ -k directorio -m "not integration" -q` verde.

## 4. Instrumento de transferencia internacional (D)

- [x] 4.1 Crear `docs/seguridad/instrumento-transferencia-internacional.md` que cubra la transferencia a Gemini (incluida la transcripcion de audio CRUDO previa a la pseudonimizacion) y a Twilio (audio crudo + numero del llamante), declare EE. UU. como pais NO adecuado (art. 12) y describa los mecanismos (consentimiento expreso o clausulas modelo: Disposicion DNPDP 60/2016; Resolucion AAIP 198/2023). Verificacion: el documento existe y contiene ambos canales, el caracter de pais no adecuado y los mecanismos.
- [x] 4.2 Incluir el encuadre explicito de no-suscripcion (documenta el mecanismo; la firma es accion organizacional) y la aclaracion de que la pseudonimizacion mitiga pero no sustituye el instrumento. Verificacion: ambas afirmaciones estan presentes en el documento.
- [x] 4.3 Referenciar el documento desde el ROPA (`docs/seguridad/registro-actividades-tratamiento.md` §4) y desde `docs/seguridad/README.md`. Verificacion: las referencias resuelven.

## 5. Superficie de privacidad en runtime (T+D, frontend)

- [x] 5.1 RED: crear el test de la superficie (`App/Frontend/src/pages/Privacidad/index.test.tsx`) que falla porque la ruta y el enlace no existen: (a) el formulario de reporte enlaza la politica; (b) la pagina de login (`/login`) enlaza la politica; (c) la ruta publica `/privacidad` se renderiza SIN sesion; (d) la superficie renderiza finalidad, responsable, destinatarios y transferencia. Verificacion: `cd App/Frontend; npm run test -- Privacidad` falla en los casos nuevos.
- [x] 5.2 GREEN: crear la pagina de privacidad y declarar la **ruta publica `/privacidad` FUERA de `ProtectedRoute`** en `App/Frontend/src/main.tsx` (explicita, porque `path="*"` redirige a `/`); agregar el enlace visible en `App/Frontend/src/pages/ReportarIncidente/IncidenteForm.tsx` y en la pagina de login, con contenido de informacion al titular y el canal para ejercer derechos. Verificacion: los tests nuevos pasan.
- [x] 5.3 TRIANGULATE: agregar casos para (a) plazos correctos (acceso 10 dias corridos; rectificacion/actualizacion/supresion 5 dias habiles); (b) ausencia de los terminos prohibidos ("certificado", "compliant", "cumple"); (c) la superficie es alcanzable sin autenticarse y sin completar un reporte (no queda detras de `ProtectedRoute`). Verificacion: todos los casos pasan.
- [x] 5.4 REFACTOR: extraer el texto/contenido de la politica a un modulo o constante testeable; re-correr los tests. Verificacion: `cd App/Frontend; npm run test -- Privacidad` verde tras cada paso.
- [x] 5.5 Verificar que no se recolectan datos personales nuevos en la superficie y que el build typechecka. Verificacion: `cd App/Frontend; npm run build` termina con exito y `npm run lint` no reporta errores.

## 6. Procedimiento ARCO con plazos (D)

- [x] 6.1 Crear `docs/seguridad/procedimiento-arco.md` con canal de presentacion, funcion responsable (la funcion de proteccion de datos de la organizacion adoptante, sin nombres), acciones por derecho y plazos (acceso 10 dias corridos; rectificacion/actualizacion/supresion 5 dias habiles), constancia auditable y remision al canal informado en la superficie. Verificacion: el documento existe y contiene canal, responsable, acciones y plazos correctos.
- [x] 6.2 Asegurar que el documento NO atribuye a la ley vigente un derecho autonomo de oposicion. Verificacion: revision de texto; no hay "derecho de oposicion" atribuido a la Ley 25.326.
- [x] 6.3 Referenciar desde la superficie de privacidad (tarea 5) y desde `docs/seguridad/README.md`. Verificacion: referencias resueltas.
- [x] 6.4 Confirmar el encuadre de OQ2 resuelto: el canal es INFORMADO y NO se implementa un endpoint backend de solicitudes ARCO. Verificacion: `grep -rn "arco\|ARCO" App/Backend/app/routes/` no arroja rutas nuevas de solicitudes ARCO; el documento declara el canal y la constancia auditable.
- [x] 6.5 DOCUMENTAR (OQ4 resuelto, sin implementar) el requisito de informacion de privacidad al titular por el canal telefonico (aviso al llamante) en la documentacion de privacidad, dejando explicito que es DISTINTO de la notificacion SMS del numero de incidente (C-67, archivado NO REALIZADO) y que NO se reintroduce ni el flujo SMS ni el greeting de voz. Verificacion: el requisito queda documentado y NO existe implementacion de greeting/TwiML ni de SMS agregada por este change.

## 7. Politica de retencion de logs (D)

- [x] 7.1 Crear `docs/seguridad/politica-retencion-logs.md` con la retencion por clase de registro (ejecucion del sistema 30 dias; contadores de origen acotados a la ventana), el no-PII en logs y la exclusion de centralizacion/SIEM (8.15/8.16). Verificacion: el documento existe y define al menos las dos clases con plazos y el encuadre de alcance.
- [x] 7.2 Referenciar desde `docs/seguridad/README.md` y desde `docs/seguridad/registro-actividades-tratamiento.md` §6. Verificacion: referencias resueltas.

## 8. Correccion de inconsistencias documentales (D)

- [x] 8.1 En `knowledge-base/06_funcionalidades.md:34`, reemplazar "Ley 25.326 compliant" por lenguaje de alineacion. Verificacion: `grep -n "compliant" knowledge-base/06_funcionalidades.md` no arroja resultados.
- [x] 8.2 En `docs/seguridad/registro-actividades-tratamiento.md`, reemplazar "conservacion indefinida" (linea ~38) por la retencion correcta (12 meses rodantes + anonimizacion irreversible) y alinear la seccion 6; dejar consistente con el capitulo 11. Verificacion: `grep -n "indefinida" docs/seguridad/registro-actividades-tratamiento.md` no arroja resultados y la seccion de conservacion cita 12 meses.
- [x] 8.3 Actualizar `docs/seguridad/README.md` (indice y mapa de trazabilidad 5.34/8.12/8.15/5.31) con los nuevos documentos. Verificacion: el indice lista los documentos nuevos y las referencias cruzadas resuelven.

## 9. Verificacion de integracion y validacion OPSX

- [x] 9.1 Correr la suite backend completa offline y confirmar que no hay regresiones. Verificacion: `cd App/Backend; pytest -m "not integration" -q` verde.
- [x] 9.2 Correr lint backend y frontend. Verificacion: `cd App/Backend; ruff check .` y `cd App/Frontend; npm run lint` sin errores.
- [x] 9.3 Validar el change con `openspec validate --strict c-66-privacidad-transferencias` (y `openspec validate --strict --changes`). Verificacion: la validacion pasa sin errores.
- [x] 9.4 Revision humana (governance ALTO): verificar el encuadre de no-suscripcion del instrumento, la regla de lenguaje y la no reintroduccion del flujo SMS (C-67). Verificacion: checklist firmado por el autor.
