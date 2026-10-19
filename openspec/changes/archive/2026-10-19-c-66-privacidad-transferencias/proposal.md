## Why

El capitulo 11 de la tesis afirma en tiempo presente un runtime de privacidad que el codigo no entrega: una politica de privacidad accesible desde los canales de entrada y un procedimiento ARCO documentado con plazos, ademas de un instrumento de transferencia internacional para Gemini/Twilio. El gap assessment (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`, brecha 5.34/8.12/8.15) confirma que hoy no existe ese instrumento, que el numero llamante se registra CRUDO en los logs de la guarda de costo (`App/Backend/app/cost_guard/guard.py:236,252`) y que el contacto del directorio se almacena en texto plano sin justificacion documentada en el cuerpo de gobernanza. C-66 cierra esa brecha entre lo que la tesis declara y lo que el sistema hace, y corrige dos inconsistencias documentales. Es la ultima pieza pendiente del workstream de cumplimiento (`docs/cumplimiento/plan-cambios-cumplimiento.md`, fase 21) y se alinea con C-53.

## What Changes

- **Numero llamante fuera de los logs (T)**: dejar de emitir el numero de origen CRUDO en los eventos estructurados de la guarda de costo (`cost_guard/guard.py:236,252`) y en la notificacion externa; emitir en su lugar un identificador derivado no reversible apto para correlacion dentro de la ventana. La derivacion usa **HMAC-SHA-256 con una clave de configuracion DEDICADA** (`cost_guard_caller_hmac_key`), **independiente** de la clave de pseudonimizacion (Fernet): no se reutiliza material de clave entre primitivas ni se acopla la rotacion de Fernet. La clave del contador de tasa por origen y el comportamiento de limitacion por origen se preservan sin cambios. Este cambio MODIFICA un requisito vigente de `runtime-cost-guard` que hoy exige registrar el numero crudo.
- **Contacto del directorio justificado por minimizacion (D)**: mantener el email y el telefono del directorio en texto plano (no se agrega cifrado) y documentar formalmente la justificacion por minimizacion, alineada con la tesis (`05-arquitectura.tex:98`, `11-aspectos-legales.tex:24`). El cifrado de aplicacion se registra como alternativa evaluada y descartada. Resuelve el hallazgo de `models/empleado.py:16-18`.
- **Instrumento de transferencia internacional (D)**: documentar el mecanismo de transferencia hacia Gemini (incluida la transcripcion de audio CRUDO previa a la pseudonimizacion, `gemini_stt.py:22-25`) y Twilio (audio crudo + numero llamante), ambos hacia Estados Unidos, pais NO adecuado. Mecanismo = consentimiento expreso del titular o clausulas contractuales modelo (Disposicion DNPDP 60/2016; Resolucion AAIP 198/2023); el instrumento se documenta, NO se firma (accion organizacional).
- **Superficie de privacidad en runtime y derechos ARCO (T+D)**: materializar una superficie de politica de privacidad accesible desde los canales de entrada (frontend) que informe finalidad, destinatarios, responsable, transferencia internacional y derechos. La superficie es una **ruta publica estatica `/privacidad` declarada FUERA de `ProtectedRoute`** (debe ser alcanzable sin sesion, porque `path="*"` redirige a `/`) y se enlaza desde el formulario de reporte y desde la pagina de login. El procedimiento ARCO se documenta con sus plazos legales (acceso: 10 dias corridos; rectificacion/actualizacion/supresion: 5 dias habiles) y con el canal informado (funcion responsable de proteccion de datos) mas registro auditable; **NO se implementa un endpoint backend de solicitudes ARCO**.
- **Retencion de logs (D)**: documentar la politica de retencion de logs (registros de ejecucion del sistema 30 dias; numero de origen acotado a la ventana del contador por origen) y su no-PII.
- **Correccion de dos inconsistencias (D)**:
  - `knowledge-base/06_funcionalidades.md:34` afirma "Ley 25.326 compliant": se reemplaza por el lenguaje de alineacion (prohibido "compliant"/"cumple").
  - `docs/seguridad/registro-actividades-tratamiento.md:38` mantiene "conservacion indefinida" para incidentes, contradiciendo el capitulo 11 corregido (12 meses rodantes + anonimizacion irreversible). Se reconcilia el ROPA.

### Out of scope (no-goals)

- NO se persigue certificacion ISO/NIST ni se usa lenguaje de "compliant"/"cumple"/"certificado" (prohibido por la regla de lenguaje del proyecto).
- NO se inscribe ninguna base ante la AAIP: es responsabilidad de la organizacion adoptante.
- NO se firman contratos reales ni clausulas modelo: solo se documenta el mecanismo; la suscripcion es accion organizacional.
- NO se implementa un endpoint backend de solicitudes ARCO: se informa el canal (la funcion responsable de proteccion de datos de la organizacion adoptante) con registro auditable; el formulario dedicado se evaluo y se descarto.
- NO se implementa el aviso/informacion por voz al llamante: se documenta el requisito. Este aviso es la INFORMACION DE PRIVACIDAD al titular por canal telefonico y es DISTINTO de la notificacion SMS del numero de incidente (change C-67, archivado como NO REALIZADO, no reintroducido aqui).
- NO se construye el flujo de SMS al llamante: C-67 fue archivado como NO REALIZADO y no se reintroduce.
- NO se implementa centralizacion de logs, SIEM ni deteccion (brechas 8.15/8.16 fuera de este cambio): aqui solo se define la politica de retencion y se saca la PII de los logs del guarda.
- NO se cifra el contacto del directorio (alternativa descartada por costo/beneficio y auditabilidad).

## Capabilities

### New Capabilities

- `privacy-runtime-surface`: superficie de politica de privacidad en runtime accesible desde los canales de entrada (pagina de frontend enlazada) mas la informacion al titular y el canal para ejercer los derechos con sus plazos.

### Modified Capabilities

- `runtime-cost-guard`: el requisito "Captura y registro del numero de origen crudo con exclusion del corpus" cambia: los logs y la notificacion NO SHALL contener el numero crudo, sino un identificador derivado no reversible; la clave del contador por origen y la limitacion por origen se preservan.
- `security-governance-docs`: se corrigen SGD-010 (retencion del ROPA: incidentes 12 meses + anonimizacion irreversible, no "indefinida") y SGD-011 (la regla de lenguaje se extiende a `knowledge-base/`); se agregan SGD-013 (procedimiento ARCO documentado con plazos), SGD-014 (instrumento de transferencia internacional documentado) y SGD-015 (politica de retencion de logs).
- `employee-directory`: se agrega DIR-010 (justificacion documental de la minimizacion del contacto en texto plano, alineada con la tesis; cifrado de aplicacion como alternativa descartada).

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/cost_guard/guard.py` | Modified | `_log_tripped` y `_log_store_unavailable` dejan de emitir `caller=caller` crudo; usan un identificador derivado no reversible. La clave del contador y la limitacion por origen no cambian. |
| `App/Backend/app/cost_guard/*` | Modified | Helper de derivacion del identificador de origen (HMAC-SHA-256 con clave dedicada); sin cambios de contrato de `evaluate`. |
| `App/Backend/app/config/settings.py` | Modified | Nueva variable requerida `cost_guard_caller_hmac_key` (clave dedicada HMAC-SHA-256, independiente de `pseudonymization_encryption_key`). |
| `App/Backend/.env.example` | Modified | Documenta `COST_GUARD_CALLER_HMAC_KEY` y su comando de generacion. |
| `App/Backend/tests/` | Modified | Tests que verifican que ningun evento lleva el numero crudo, que la limitacion por origen sigue operando y que la derivacion usa la clave dedicada. |
| `App/Backend/tests/conftest.py` | Modified | Provee la nueva variable requerida en el entorno de tests. |
| `.github/workflows/ci.yml` | Modified | Variable dummy `COST_GUARD_CALLER_HMAC_KEY` para el subconjunto SQLite offline. |
| `App/Frontend/src/` | New | Ruta publica `/privacidad` declarada FUERA de `ProtectedRoute` en `main.tsx` y pagina de politica de privacidad enlazada desde el formulario de reporte y desde `/login`; contenido de informacion al titular y derechos. |
| `App/Frontend/src/**/*.test.tsx` | New | Tests de la superficie de privacidad (existencia, contenido, enlace y acceso sin sesion). |
| `docs/seguridad/procedimiento-arco.md` | New | Procedimiento ARCO documentado con plazos (10 dias corridos / 5 dias habiles), canal informado y registro auditable (sin endpoint backend). |
| `docs/seguridad/instrumento-transferencia-internacional.md` | New | Mecanismo de transferencia hacia Gemini (incl. STT de audio crudo) y Twilio. |
| `docs/seguridad/politica-retencion-logs.md` | New | Politica de retencion de logs y no-PII. |
| `docs/seguridad/registro-actividades-tratamiento.md` | Modified | Reconciliacion de la retencion (incidentes 12 meses + anonimizacion; sin "indefinida"). |
| `docs/seguridad/README.md` | Modified | Indice de los nuevos documentos y mapa de trazabilidad (5.34, 8.12, 8.15, 5.31). |
| `docs/seguridad/politica-privacidad-runtime.md` | Modified | Referencia a la superficie en runtime y a los nuevos documentos. |
| `knowledge-base/06_funcionalidades.md` | Modified | Corregido "Ley 25.326 compliant" a lenguaje de alineacion. |
| `openspec/changes/c-66-privacidad-transferencias/**` | New | Artefactos OPSX (proposal, specs, design, tasks). |

Sin cambios de esquema de datos, API REST ni dependencias. La CI suma unicamente la nueva variable de entorno dummy `COST_GUARD_CALLER_HMAC_KEY`.

## Governance

**ALTO (HIGH)**. El cambio trata datos personales (Ley 25.326), define el tratamiento del numero llamante y el instrumento de transferencia internacional hacia un pais no adecuado. Bajo la gobernanza por dominio: la modificacion de logs del guarda (analisis + propuesta antes de escribir, no reescribir el contrato de limitacion por origen), el documento de transferencia internacional y la superficie de privacidad requieren revision del autor antes de dar por cerrado el change. No se escribe logica de produccion en la fase de propose.

## Decisiones resueltas

- **OQ1 — Derivacion del numero llamante (RESUELTO)**: el identificador no reversible se deriva con **HMAC-SHA-256 usando una clave de configuracion DEDICADA** (`cost_guard_caller_hmac_key`), truncada (~12 caracteres hex), deterministica dentro de la ventana y no reversible sin la clave. Se DESCARTA derivar por HKDF desde la clave Fernet de pseudonimizacion (acopla ciclos de vida y reutiliza material de clave entre primitivas) y se descartan el hash sin clave y el enmascarado de digitos. Consecuencia: nueva variable requerida en `settings.py`, `.env.example`, la CI y `conftest.py`.
- **OQ2 — Canal de ARCO (RESUELTO)**: se mantiene el DEFECTO. El procedimiento se documenta con un canal informado (la funcion responsable de proteccion de datos de la organizacion adoptante) y registro auditable; **NO se implementa endpoint backend**. El formulario dedicado se evaluo y se descarto (queda como eventual change futuro, sin acoplarse a C-66).
- **OQ3 — Superficie publica vs autenticada (RESUELTO)**: la pagina es una **ruta publica estatica `/privacidad` declarada FUERA de `ProtectedRoute`** en `App/Frontend/src/main.tsx` (obligatorio, porque `path="*"` redirige a `/`), enlazada desde `IncidenteForm.tsx` y desde `/login`. Debe ser alcanzable antes de autenticarse: es el aviso en el punto de recoleccion.
- **OQ4 — Canal telefonico (RESUELTO)**: se DOCUMENTA el requisito de aviso/informacion de privacidad por voz al llamante; **NO se implementa** (TwiML/greeting fuera de alcance). Es la informacion de privacidad al titular por canal telefonico y es DISTINTA de la notificacion SMS del numero de incidente (C-67, archivado como NO REALIZADO, no reintroducido).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Que la modificacion de logs rompa la limitacion por origen | Med | El identificador derivado es solo para logs; la clave del contador sigue siendo el numero crudo en el almacen, purgado al vencer la ventana. Test de no regresion del rate por origen. |
| Custodia/rotacion de la nueva clave HMAC dedicada | Med | Se documenta el comando de generacion y la custodia como secreto de despliegue; se DESACOPLA de la rotacion de Fernet. Rotarla solo cambia los identificadores derivados de logs (efimeros), no datos persistidos. |
| Que la superficie de privacidad afirme conformidad | Med | Regla de lenguaje: "alineado con"; test de contenido sin terminos prohibidos. |
| Duplicar el procedimiento ARCO con SGD-009 | Med | SGD-013 es el procedimiento operativo; SGD-009 describe derechos y plazos en la politica. Referencias cruzadas, sin contradiccion. |
| Documentar el instrumento como si estuviera firmado | Med | Encuadre explicito: se documenta el mecanismo, la firma es accion organizacional. |
| Deriva entre ROPA y capitulo 11 | Baja | Tarea de reconciliacion (fix b) y validacion de consistencia. |

## Rollback Plan

Revertir el commit restaura el comportamiento previo del guarda (numero crudo en logs) y elimina los documentos y la superficie nuevos. No hay migraciones, datos ni cambios de API que deshacer. Consideracion de governance: revertir reintroduce un hallazgo de PII en logs (5.34/8.12), por lo que un rollback debe quedar justificado.

## Dependencies

- Insumos de alcance y normativos: `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§4, `docs/cumplimiento/marco-legal-ar-2026.md` §5 (art. 12; EE. UU. no adecuado; mecanismos), `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas 5.34/8.12/8.15/5.31).
- Base documental: `docs/seguridad/politica-privacidad-runtime.md`, `docs/seguridad/registro-actividades-tratamiento.md` (ROPA).
- Se alinea con C-53 (numero canonico/notificacion) y con C-67 (cerrado NO REALIZADO; no se consume).

## Success Criteria

- [ ] Ningun evento estructurado ni notificacion de la guarda contiene el numero de origen CRUDO; la limitacion por origen sigue operando (tests verdes).
- [ ] La derivacion usa la clave HMAC dedicada `cost_guard_caller_hmac_key` (independiente de la clave de pseudonimizacion); rotar la clave cambia el identificador derivado y el numero crudo nunca aparece.
- [ ] Existe un documento que justifica por minimizacion el contacto del directorio, alineado con la tesis, con el cifrado como alternativa descartada; y `employee-directory` lo refleja.
- [ ] Existe el documento del instrumento de transferencia internacional para Gemini (incl. STT de audio crudo) y Twilio, con el mecanismo y el encuadre de que no se firma.
- [ ] Existe una superficie de politica de privacidad como ruta publica `/privacidad` (fuera de `ProtectedRoute`), alcanzable sin sesion y enlazada desde el formulario de reporte y desde `/login`, con informacion al titular y derechos, sin lenguaje de conformidad.
- [ ] Existe el procedimiento ARCO documentado con los plazos correctos (10 dias corridos / 5 dias habiles), canal informado y registro auditable, sin endpoint backend.
- [ ] Existe la politica de retencion de logs; el ROPA ya no dice "conservacion indefinida".
- [ ] `knowledge-base/06_funcionalidades.md` ya no afirma "Ley 25.326 compliant".
- [ ] `openspec validate --strict --changes c-66-privacidad-transferencias` pasa.
