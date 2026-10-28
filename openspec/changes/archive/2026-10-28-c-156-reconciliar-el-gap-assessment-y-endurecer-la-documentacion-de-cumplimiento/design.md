## Context

Ver `proposal.md` — Why. El repositorio ya cerro C-61, C-62, C-63a/b/c, C-64, C-65, C-66 y C-67 (archivados entre 2026-10-01 y 2026-10-19), pero la documentacion de cumplimiento conserva el snapshot del 2026-10-01. El unico tramo reconciliado hasta ahora es el de respaldo y continuidad (C-65). Los documentos de `docs/seguridad/` tienen encabezados normalizados y un indice con mapa de trazabilidad; el lint prometido en `docs/seguridad/README.md:203-205` nunca se implemento. El canal telefonico ya genera TwiML estatico en `app/cost_guard/twiml.py` y su contrato esta cubierto por `tests/test_twiml_record.py`.

## Goals / Non-Goals

**Goals:**
- Que el gap assessment y el cuerpo documental describan el estado real del repositorio sin perder los residuales genuinos del adoptante.
- Que la integridad documental sea verificable de forma automatica y hermetica.
- Que el aviso de privacidad telefonico exista en runtime, no solo en la politica.
- Que la tesis no atribuya como pendiente un control ya implementado.

**Non-Goals:**
- Reescribir el gap assessment completo ni convertirlo en una auditoria.
- Implementar KMS/PAM, copia offsite, contratos con proveedores o revision independiente.
- Agregar un escaner de licencias con red o una dependencia nueva.
- Recompilar ni publicar el PDF en este change; solo dejar la fuente corregida y el rebuild registrado.
- Modificar `ci.yml`, `requirements.txt`, `openspec/config.yaml` o las cadenas canonicas de sector.

## Decisions

### 1. Reconciliar con registro de estado vigente + correccion en sitio

Se agrega al gap assessment una seccion "Registro de estado vigente" con una tabla `control -> estado -> evidencia -> residual -> change archivado`, y ademas se corrigen en sitio las afirmaciones mas contradictorias (resumen ejecutivo §2.3, filas 5.1, 5.9, 5.12, 5.15, 5.19, 5.24, 5.32, 5.34, 8.5, 8.8, 8.15, 8.20, 8.28 y 5.28). Se elige este enfoque mixto porque un registro solo-agregado deja el cuerpo principal afirmando lo contrario y confunde al lector; una reescritura total arriesga borrar matices y residuales validos del snapshot original.

Alternativa descartada: reemplazar el documento por un informe nuevo fechado 2026-10-28. Se descarta para preservar la trazabilidad historica del assessment y el esfuerzo de remediacion original.

### 2. Lint documental como test pytest hermetico

Se implementa `App/Backend/tests/test_compliance_docs_lint.py`, que resuelve la raiz del repo desde `__file__` y opera solo con el sistema de archivos. Se elige pytest sobre un script suelto porque el job `backend-tests` ya ejecuta la suite y no requiere tocar `ci.yml`; ademas hereda el aislamiento offline del subset SQLite. El test valida cuatro invariantes: indice -> archivo existente, archivo -> indice, encabezados minimos por documento y frases de certificacion afirmativas. Para no producir falsos positivos, la deteccion de terminos prohibidos usa patrones afirmativos ("esta certificado", "es compliant", "cumple ISO", "cumple NIST", "certificacion obtenida") y excluye lineas que contienen negaciones o el encuadre "alineado con". La lista de documentos de gobernanza se deriva de los archivos `.md` de la carpeta, excluyendo el anexo `acta-consentimiento-t1.md` mediante una allowlist explicita y documentada en el test.

Alternativa descartada: `scripts/preflight/docs_compliance_lint.py` invocado desde CI. Agrega un paso de workflow y una superficie de ejecucion adicional para el mismo resultado; se prefiere el test mientras el lint sea de solo lectura.

### 3. Aviso de privacidad telefonico: implementar, no diferir

Se agrega un `<Say>` de aviso al inicio de `render_twiml_allowed`, antes del `<Record>`, con texto estatico. Se elige implementar porque es un cambio de bajo riesgo, sin nuevas dependencias, ya cubierto por el patron de test existente, y porque el requisito de informacion en el punto de recoleccion es una obligacion real de la Ley 25.326 (art. 6). El texto se mantiene corto para no degradar la experiencia telefonica y no interpola datos del llamante, preservando la garantia anti-inyeccion del XML. No se toca `render_twiml_record_complete` ni `render_twiml_denied`.

Alternativa descartada: registrar el aviso como residual aceptado. Se descarta porque el coste de implementacion es marginal y el residual seria dificil de justificar ante el marco legal que la propia tesis invoca.

### 4. Inventario de licencias manual y acotado

Se crea `docs/seguridad/inventario-licencias.md` con las dependencias principales de `App/Backend/requirements.txt` y `App/Frontend/package.json`, su licencia declarada y las obligaciones de atribucion/copyleft. No se agrega un verificador de licencias en CI: requeriria red o una dependencia nueva y el control 5.32 es de severidad baja. El documento declara que la verificacion legal definitiva es del adoptante.

### 5. Correccion de tesis en v10 y v9, rebuild diferido

Se corrige el parrafo de brechas en ambas fuentes LaTeX para separar "implementado en el repositorio" de "KMS/PAM y produccion como accion del adoptante". El PDF no se recompila en este change: se registra como tarea de release posterior a v1.2.3, consistente con la regla de no mover tags publicados.

## Risks / Trade-offs

- [El lint puede fallar por documentos nuevos no listados] -> La allowlist y el mensaje de error indican el archivo exacto; agregar un documento obliga a actualizar el indice, que es el comportamiento deseado.
- [Frases de certificacion en contexto negativo] -> Patrones afirmativos acotados y exclusion de lineas con "no", "sin", "alineado con"; se valida contra los documentos actuales antes de cerrar.
- [El aviso de voz alarga la llamada] -> Texto breve, sin datos dinamicos; se mantiene el `<Record>` con `maxLength=45` intacto.
- [Reconciliar el gap assessment puede introducir afirmaciones no verificadas] -> Cada fila del registro cita archivo o change archivado; los residuales del adoptante se conservan textualmente.
- [La tesis queda con fuente y PDF desalineados hasta el rebuild] -> Se registra explicitamente en tasks y en el registro de release; no se publica el PDF como si estuviera actualizado.

## Migration Plan

1. Reconciliar y corregir documentos (sin impacto en runtime).
2. Agregar el test de lint y hacerlo pasar sobre el cuerpo documental ya corregido.
3. Modificar el TwiML y su prueba; ejecutar la suite de backend.
4. Corregir la fuente LaTeX y registrar el rebuild pendiente.
5. Revertir es cambiar solo archivos de documentacion, el texto del TwiML y los tests; no hay migracion de datos ni cambios de esquema.

## Open Questions

Ninguna que afecte specs, enfoque o desglose de tareas.
