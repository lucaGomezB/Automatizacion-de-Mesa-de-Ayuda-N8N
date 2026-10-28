## 1. Reconciliacion del gap assessment

- [x] 1.1 Verificar contra el codigo y los changes archivados (C-61, C-62, C-63a/b/c, C-64, C-65, C-66, C-67) el estado real de cada control citado, y confirmar que MFA existe en `App/Backend/app/routes/auth.py`, que Redis fue retirado y que CI ejecuta bandit, pip-audit y npm audit.
- [x] 1.2 Agregar la seccion "Registro de estado vigente" con la tabla `control -> estado -> evidencia -> residual abierto -> change archivado`, cubriendo al menos 5.1, 5.9, 5.12, 5.15, 5.17, 5.19, 5.24, 5.28, 5.32, 5.34, 8.5, 8.8, 8.15, 8.20, 8.24 y 8.28.
- [x] 1.3 Corregir en sitio el resumen ejecutivo §2.3 y las filas contradictorias, y verificar por busqueda que no queden afirmaciones de "sin MFA", "Redis expuesto", "sin politica", "sin inventario", "sin evaluacion de proveedores" ni "sin SAST/pip-audit" presentadas como estado vigente.
- [x] 1.4 Verificar que 5.35, 8.14 y la copia offsite sigan declarados como residuales o acciones del adoptante, sin suavizarlos.

## 2. Correccion de referencias cruzadas

- [x] 2.1 En `docs/seguridad/inventario-activos-informacion.md`, retirar Redis de los activos activos, marcar Microsoft Outlook como inactivo desde C-55 y reemplazar la referencia al change C-63 por `gestion-secretos-y-rotacion.md`; verificar que cada archivo enlazado exista.
- [x] 2.2 En `docs/seguridad/README.md`, actualizar §3 y §7 para presentar C-62 a C-67 como archivados, corregir el mapa de 5.34/8.12 hacia `adr-001-reversion-minimizacion-directorio.md` y `clasificacion-etiquetado-informacion.md`, y eliminar la nota "Pendiente para el orquestador" sobre `CHANGES.md`.
- [x] 2.3 En `docs/seguridad/registro-actividades-tratamiento.md`, agregar la nota de Microsoft Outlook como procesador historico inactivo; verificar que no se altere la conservacion ni las transferencias declaradas.
- [x] 2.4 Verificar con un chequeo de enlaces relativos que todas las referencias cruzadas de `docs/seguridad/` resuelven a archivos existentes.

## 3. Lint documental (TDD)

- [x] 3.1 Escribir `App/Backend/tests/test_compliance_docs_lint.py` con los cuatro casos de RED: documento listado inexistente, documento no listado, encabezado requerido faltante y afirmacion positiva de certificacion; ejecutar `pytest App/Backend/tests/test_compliance_docs_lint.py` y confirmar que falla por la ausencia del validador.
- [x] 3.2 Implementar en el mismo test el validador hermetico (resolucion de raiz, parseo de indice, allowlist del acta, patrones afirmativos y exclusion de negaciones) hasta que los casos pasen; ejecutar el archivo completo y confirmar GREEN.
- [x] 3.3 Triangular con casos adicionales: documento con encuadre "alineado con" que no debe fallar, documento con "no constituye certificacion" que no debe fallar y archivo del anexo que no debe exigir encabezados de gobernanza; confirmar que todos pasan.
- [x] 3.4 Ejecutar `pytest App/Backend/tests/test_compliance_docs_lint.py` sin red y sin PostgreSQL y confirmar que el lint no depende de servicios externos.

## 4. Aviso de privacidad telefonico (TDD)

- [x] 4.1 Escribir en `App/Backend/tests/test_twiml_record.py` los tests RED del aviso: el `<Say>` previo al `<Record>` menciona grabacion, finalidad, responsable, transferencia y derechos; no contiene datos del llamante ni promete alta inmediata; el `<Record>` conserva sus atributos y callbacks. Ejecutar y confirmar que fallan.
- [x] 4.2 Agregar el texto estatico del aviso en `App/Backend/app/cost_guard/twiml.py` (`render_twiml_allowed`) hasta que los tests pasen; ejecutar `pytest App/Backend/tests/test_twiml_record.py` y confirmar GREEN.
- [x] 4.3 Triangular verificando que `render_twiml_record_complete` y `render_twiml_denied` no cambian, que el XML sigue siendo parseable y que el aviso no contiene los terminos "certificado", "compliant" ni "cumple".
- [x] 4.4 Actualizar `docs/seguridad/politica-privacidad-runtime.md` §1.1 para declarar el aviso telefonico como implementado en el saludo TwiML, sin tocar el resto de la politica; verificar coherencia con el texto del test.

## 5. Evidencia y cadena de custodia (5.28)

- [x] 5.1 Agregar al `docs/seguridad/plan-respuesta-incidentes-seguridad.md` una seccion de manejo de evidencia (identificacion, recoleccion, preservacion, integridad con hash, custodios y transferencias); verificar que la seccion exista y que el encuadre atribuya la custodia formal al adoptante.
- [x] 5.2 Agregar en `docs/seguridad/politica-retencion-logs.md` la referencia cruzada a la retencion de evidencia por clase de registro; verificar que no se contradiga con los plazos ya declarados (30 dias, ventana del contador, directorio).

## 6. Inventario de licencias (5.32)

- [x] 6.1 Crear `docs/seguridad/inventario-licencias.md` con las dependencias principales de `App/Backend/requirements.txt` y `App/Frontend/package.json`, su licencia declarada y las obligaciones de atribucion/copyleft; verificar que no incluya credenciales ni secretos.
- [x] 6.2 Listar el documento en `docs/seguridad/README.md` y verificar que el lint documental lo acepte con los encabezados requeridos.

## 7. Correccion de la tesis

- [x] 7.1 Corregir el parrafo de brechas de `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` para separar MFA y rotacion de claves implementadas en el repositorio de KMS/PAM y custodia como accion del adoptante; verificar por busqueda que no quede la afirmacion sin calificar.
- [x] 7.2 Aplicar la misma correccion en `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex` y comparar ambos textos.
- [x] 7.3 Registrar en `tasks.md` o en el registro de release que el PDF debe recompilarse en una release de correccion posterior a v1.2.3; verificar que el registro exista y que no se mueva ningun tag publicado.

## 8. Verificacion final

- [x] 8.1 Ejecutar `cd App/Backend; pytest -m "not integration"` y confirmar que la suite SQLite pasa, incluido el lint documental.
- [x] 8.2 Ejecutar `cd App/Backend; ruff check .` y confirmar que no hay hallazgos nuevos.
- [x] 8.3 Ejecutar `openspec validate "c-156-reconciliar-el-gap-assessment-y-endurecer-la-documentacion-de-cumplimiento" --strict --no-interactive` y confirmar que pasa.
- [x] 8.4 Revisar que no se hayan modificado las cinco cadenas canonicas de sector, `requirements.txt`, `openspec/config.yaml`, los parametros de Gemini ni `.github/workflows/ci.yml`.
