## Context

Ver `proposal.md` (Why) para la motivacion. Estado y restricciones que condicionan el diseno:

- La guarda de costo vive en `App/Backend/app/cost_guard/`. `CostGuard.evaluate(provider, caller, amount)` recibe el numero de origen ya resuelto por los llamadores de ruta (`routes/cost_guard.py:224`, `routes/telefonia.py:214`) y en el camino de disparo emite `caller=caller` en los eventos estructurados (`guard.py:236` disparo, `guard.py:252` almacen no disponible). El numero CRUDO tambien es la clave del contador por origen (`guard.py:171`, `AMBITO_CALLER`) y su purga acota la retencion a la ventana (`guard.py:208-210`).
- El esquema vigente de `runtime-cost-guard` (requisito "Captura y registro del numero de origen crudo con exclusion del corpus") hoy exige el registro CRUDO; por eso el change lo retira y agrega el contrato nuevo.
- La pseudonimizacion del backend es Fernet-based y ya tiene una clave de configuracion (`pseudonymization_encryption_key`, env `PSEUDONYMIZATION_ENCRYPTION_KEY`); el directorio NO la usa (DIR-005). La derivacion del identificador de origen en logs usa una **clave DEDICADA** (`cost_guard_caller_hmac_key`), **independiente** de la de pseudonimizacion (decision OQ1): no se reutiliza material de clave entre primitivas (Fernet vs HMAC) ni se acopla la rotacion de Fernet a los logs del guarda.
- La tesis ya justifica el contacto del directorio en texto plano por auditabilidad y control de acceso por rol (`05-arquitectura.tex:98`, `11-aspectos-legales.tex:24`), y ya reconoce el orden real del canal telefonico: audio crudo y numero del llamante cruzan a EE. UU. antes de la pseudonimizacion (`11-aspectos-legales.tex:18`, `gemini_stt.py:22-25`).
- No existe hoy ni instrumento de transferencia, ni procedimiento ARCO operativo, ni superficie de privacidad en runtime (grep de `privacidad|privacy` en `App/Frontend/src/` no devuelve la superficie publica), ni politica de retencion de logs.
- El stack es de desarrollo local; el repositorio puede cerrar lo (T) tecnico y lo (D) documental, no lo (O) organizacional.

### Referencias de lectura (Leer antes)

- `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§4 (fila C-66; relacion con C-53/C-67).
- `docs/cumplimiento/marco-legal-ar-2026.md` §5 (art. 12; EE. UU. no adecuado; mecanismos de transferencia).
- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas 5.34, 8.12, 8.15, 5.31).
- `docs/seguridad/politica-privacidad-runtime.md` (SGD-009) y `docs/seguridad/registro-actividades-tratamiento.md` (ROPA, SGD-010).
- `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex` (capitulo 11; afirmacion en presente que este change hace verificable).

## Goals / Non-Goals

**Goals:**

- Sacar el numero de origen CRUDO de los logs del guarda sin perder la limitacion de tasa por origen ni la capacidad de correlacionar llamadas del mismo origen en la ventana.
- Dejar documentada (y trazable) la decision de justificar por minimizacion el contacto del directorio, con el cifrado como alternativa descartada.
- Documentar el mecanismo de transferencia internacional hacia Gemini (incl. STT de audio crudo) y Twilio, dejando explicito que no se firma ningun instrumento.
- Materializar la superficie de privacidad en runtime y documentar el procedimiento ARCO con plazos.
- Definir la politica de retencion de logs y corregir las dos inconsistencias documentales.

**Non-Goals:**

- Centralizacion de logs, SIEM, deteccion de anomalias (brechas 8.15/8.16): fuera de alcance.
- Cifrado del contacto del directorio: alternativa descartada (D2).
- Endpoint backend nuevo de solicitudes ARCO: se evaluo y se DESCARTO (OQ2 resuelto). La superficie informa el canal y el procedimiento documenta la funcion responsable con registro auditable.
- Mensaje de informacion por voz para llamantes (canal telefonico): se DOCUMENTA el requisito; la implementacion por TwiML/greeting queda fuera de alcance y NO se implementa (OQ4 resuelto). Es informacion de privacidad al titular, DISTINTA de la notificacion SMS de C-67 (archivado como NO REALIZADO, no reintroducido).
- Certificacion ISO/NIST, inscripcion AAIP, firma de contratos o clausulas modelo, flujo SMS al llamante.

## Decisions

### D1 — Identificador derivado no reversible para el numero de origen en logs

Los eventos estructurados del guarda dejan de emitir el numero crudo y emiten un **identificador derivado** obtenido con **HMAC-SHA-256** sobre el numero, usando una **clave de configuracion DEDICADA** (`cost_guard_caller_hmac_key`), truncado a una longitud corta (por ejemplo 12 caracteres hex). El numero crudo sigue siendo la clave del contador por origen en el almacen, con la purga por ventana ya existente intacta.

Rationale (robustez por diseno): la clave dedicada **evita reutilizar material de clave entre primitivas** (Fernet para pseudonimizacion vs HMAC para logs) y **desacopla la rotacion** de Fernet de los identificadores de log. El tradeoff honesto es una obligacion adicional de gestion de secretos (generacion, custodia y rotacion de la nueva clave), mitigada porque los identificadores de log son efimeros y rotar la clave no afecta datos persistidos.

- **Alternativa A (descartada): quitar el numero por completo de los logs.** Pierde la capacidad de correlacionar llamadas del mismo origen durante la ventana, que es util para diagnostico operativo.
- **Alternativa B (descartada): HKDF derivado de la clave Fernet de pseudonimizacion.** Reutiliza material de clave entre primitivas y acopla el ciclo de vida y la rotacion de la clave de pseudonimizacion a los logs del guarda; la robustez por diseno prefiere una clave dedicada de un solo proposito.
- **Alternativa C (descartada): hash sin clave.** El espacio telefonico es enumerable (prefijos + area + numero), por lo que un hash sin clave es vulnerable a diccionario y no califica como no reversible para el lector de logs.
- **Alternativa D (descartada): enmascarar digitos.** Revelaria informacion parcial del numero (sigue siendo dato personal) y no resuelve el hallazgo.
- **Elegida: HMAC-SHA-256 con clave dedicada + truncado.** Deterministico dentro de la ventana (correlaciona), no reversible sin la clave, y desacoplado de la pseudonimizacion.

La derivacion se encapsula en un helper del paquete `cost_guard` para mantener `guard.py` legible y testeable; la firma de `evaluate` no cambia (el contrato de la guarda hacia las rutas se preserva).

### D2 — Contacto del directorio: justificar por minimizacion, no cifrar

Se mantiene el email y el telefono en texto plano (DIR-005) y se documenta formalmente la justificacion por minimizacion.

- **Alternativa A (descartada): cifrado de aplicacion con `EncryptedText` (Fernet).** Agrega custodia de claves (rotacion, backup, runbook) y rompe las consultas SQL operativas del directorio (resolucion de contactos, unicidad de email); el beneficio es marginal porque el dato no es sensible bajo el art. 2 de la Ley 25.326 y su proteccion ya se sustenta en RBAC + red aislada + auditoria.
- **Alternativa B (descartada): indice ciego (HMAC) para busqueda cifrada.** Suma complejidad de claves sin un caso de uso que lo justifique.
- **Elegida: justificacion documental.** Coincide con lo que la tesis ya afirma, es de bajo costo, cierra el hallazgo 5.34/8.12 como (D) y no degrada la operacion.

### D3 — Instrumento de transferencia: documentar el mecanismo, no suscribirlo

Se crea un documento que describe el mecanismo (consentimiento expreso o clausulas contractuales modelo, Disposicion DNPDP 60/2016 / Resolucion AAIP 198/2023) para Gemini y Twilio, destacando que el audio crudo y el numero del llamante cruzan a EE. UU. ANTES de la pseudonimizacion (el canal STT de Gemini y la telefonia de Twilio).

- **Alternativa A (descartada): depender solo de la pseudonimizacion.** El marco legal y la propia tesis aclaran que la pseudonimizacion mitiga pero no sustituye el instrumento; ademas el audio no se pseudonimiza.
- **Alternativa B (fuera de alcance): suscribir clausulas o consentimiento.** Es accion organizacional del adoptante; el repositorio no puede evidenciarla.
- **Elegida: documento del mecanismo con encuadre explicito de no-suscripcion.**

### D4 — Superficie de privacidad en runtime

Pagina de frontend dedicada con contenido estatico, declarada como **ruta publica `/privacidad` FUERA de `ProtectedRoute`** en `App/Frontend/src/main.tsx`. Debe declararse explicitamente porque la ruta catch-all `path="*"` redirige a `/`, de modo que el aviso queda accesible sin sesion (aviso en el punto de recoleccion). Se enlaza de forma visible desde el formulario de reporte de incidentes (`App/Frontend/src/pages/ReportarIncidente/IncidenteForm.tsx`) y desde la pagina de login (`/login`, ya publica). Contenido: finalidad, destinatarios, responsable, bases de licitud, transferencia internacional y mecanismo, derechos con plazos y canal para ejercerlos, y advertencia de respuestas automaticas. Lenguaje de alineacion.

- **Alternativa A (descartada): pagina servida por el backend.** Acopla contenido editorial al backend y complica el versionado del texto.
- **Alternativa B (descartada): modal en el formulario.** Dificulta enlazar/leer la politica completa y su versionado.
- **Alternativa C (descartada): ruta dentro de `ProtectedRoute`.** Impediria alcanzar el aviso antes de autenticarse; contradice el caracter de aviso previo al tratamiento.
- **Elegida: ruta publica de frontend fuera de `ProtectedRoute`.** Es la opcion mas simple y la correcta: accesible sin sesion, testeable, enlazable, con texto versionado en el repo.

### D5 — ARCO: procedimiento documentado y canal informado

Se crea `docs/seguridad/procedimiento-arco.md` con canal, funcion responsable (la funcion de proteccion de datos de la organizacion adoptante, sin nombrar personas), acciones por derecho, plazos (10 dias corridos / 5 dias habiles; sin derecho autonomo de oposicion) y constancia auditable. La superficie de privacidad informa el canal. **RESUELTO (OQ2): se mantiene el DEFECTO. NO se crea un endpoint backend de solicitudes ARCO**; el formulario dedicado se evaluo y se descarto (queda como eventual change futuro, sin acoplarse a C-66).

- **Alternativa (descartada): endpoint backend de solicitudes ARCO.** Alcance mayor (modelo, estados, plazos, notificacion) que no exige el plan; un canal informado con registro auditable cumple el requisito sin ampliar superficie ni datos.

### D6 — Retencion de logs

Se documenta la politica de retencion por clase de registro: registros de ejecucion del sistema 30 dias (consistente con el capitulo 11 y la poda N8N vigente); contadores de origen del guarda acotados a la ventana; el numero de origen no se registra crudo. La centralizacion y el SIEM quedan fuera de alcance (8.15/8.16).

### D7 — Correccion de inconsistencias documentales

- `knowledge-base/06_funcionalidades.md:34`: reemplazar "Ley 25.326 compliant" por lenguaje de alineacion ("alineado con la Ley 25.326").
- `docs/seguridad/registro-actividades-tratamiento.md:38`: reemplazar "conservacion indefinida" por "12 meses rodantes + anonimizacion irreversible" para incidentes, consistente con el capitulo 11 corregido, y alinear la seccion 6 del mismo documento.

### D8 — Aviso de privacidad por canal telefonico (documentado, no implementado)

**RESUELTO (OQ4)**: se DOCUMENTA el requisito de informacion de privacidad al titular por el canal telefonico (aviso al llamante) y **NO se implementa** (TwiML/greeting fuera de alcance). El aviso es la **informacion de privacidad al titular** en el punto de recoleccion telefonico y es **DISTINTO de la notificacion SMS del numero de incidente**, que correspondia al change C-67 (archivado como NO REALIZADO). C-67 NO se reintroduce aqui: no se construye ni el flujo SMS ni el greeting de voz; solo se deja el requisito documentado.

### D9 — Clave HMAC dedicada: configuracion y gestion

**RESUELTO (OQ1)**: la derivacion del identificador de origen usa una **clave HMAC dedicada** (`cost_guard_caller_hmac_key`, env `COST_GUARD_CALLER_HMAC_KEY`). Consecuencias de configuracion: nueva variable requerida en `App/Backend/app/config/settings.py`; comando de generacion documentado en `App/Backend/.env.example`; variable dummy en la CI (`.github/workflows/ci.yml`) para el subconjunto SQLite offline; y provision en el entorno de tests (`App/Backend/tests/conftest.py`). El comando de generacion sugerido es `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

## Risks / Trade-offs

- [La modificacion de logs rompe la limitacion por origen] → El identificador derivado es solo para logs; la clave del contador sigue siendo el numero crudo en el almacen. Test de no regresion del rate por origen.
- [Un identificador truncado colisiona y mezcla origenes] → Longitud elegida (12 caracteres hex) mantiene colisiones improbables para el volumen del piloto; se documenta el tradeoff y se puede subir la longitud sin cambiar el contrato.
- [Gestion de secretos de la nueva clave HMAC dedicada] → Comando de generacion y custodia documentados como secreto de despliegue; se DESACOPLA de la rotacion de Fernet. Rotarla solo cambia identificadores de log efimeros, no datos persistidos.
- [La superficie de privacidad afirma conformidad] → Test de contenido que rechaza los terminos prohibidos; encuadre de alineacion.
- [El documento de transferencia se lee como instrumento firmado] → Encuadre explicito y scenario de spec que lo prohibe.
- [Deriva futura entre ROPA, capitulo 11 y politica de retencion] → Referencias cruzadas y tarea de validacion de consistencia.

## Migration Plan

- **Backend (D1, D9)**: cambio aditivo + reemplazo de dos llamadas de logging + nueva variable de configuracion (`cost_guard_caller_hmac_key`); sin migracion de base de datos. Los contadores por origen son efimeros. Desplegar con la clave provista; revertir el commit restaura el logging crudo.
- **Frontend (D4)**: ruta publica nueva fuera de `ProtectedRoute` mas dos enlaces; sin migraciones; rollback = quitar la ruta y los enlaces.
- **Documentacion (D2, D3, D5, D6, D7, D8)**: archivos nuevos y dos ediciones puntuales; rollback = revertir el commit.
- **Rollback y governance**: revertir D1 reintroduce la fuga de PII en logs (5.34/8.12); cualquier rollback debe quedar justificado por escrito.

## Decisiones resueltas

- **OQ1 — Derivacion (RESUELTO)**: HMAC-SHA-256 con **clave DEDICADA** (`cost_guard_caller_hmac_key`), truncado ~12 hex. Se DESCARTA HKDF desde la clave Fernet (reutiliza material de clave y acopla ciclos de vida) y se descartan hash sin clave y enmascarado de digitos. Consecuencia: nueva variable requerida (settings/.env.example/CI/conftest). Ver D1 y D9.
- **OQ2 — Canal ARCO (RESUELTO)**: se mantiene el DEFECTO: canal informado (funcion responsable de proteccion de datos) + registro auditable; NO se implementa endpoint backend. El formulario dedicado se evaluo y se descarto. Ver D5.
- **OQ3 — Accesibilidad de la superficie (RESUELTO)**: ruta publica estatica `/privacidad` declarada FUERA de `ProtectedRoute` (obligatorio por el catch-all `path="*"`), enlazada desde `IncidenteForm.tsx` y `/login`. Ver D4.
- **OQ4 — Canal telefonico (RESUELTO)**: se DOCUMENTA el aviso/informacion de privacidad por voz al llamante; NO se implementa. DISTINTO de la notificacion SMS de C-67 (archivado NO REALIZADO, no reintroducido). Ver D8.
