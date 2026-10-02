> **Nota (tarea 1.4):** este change es **documental** y **no tiene runner de tests**. La
> verificacion es la existencia/contenido de los documentos, la busqueda de terminos
> prohibidos y `openspec validate --strict`. No se agregan tests de backend ni scripts.

## 1. Preparacion y contrato documental

- [x] 1.1 Crear `docs/seguridad/` y el indice `docs/seguridad/README.md` con proposito, estado de cada documento, periodicidad de revision y el mapa de trazabilidad control -> documento -> requisito SGD (design D1/D3). Verificacion: el README existe y su mapa cubre los controles objetivo (5.1, 5.2, 5.9, 5.12, 5.13, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26) y NIST CSF Govern/Identify.
- [x] 1.2 Registrar en el README la plantilla comun de documento (encabezado con control mapeado, estado, alcance, encuadre) y la regla de lenguaje "alineado con" / "controles mapeados a", con la lista de terminos prohibidos (design D2/D4). Verificacion: la plantilla y la regla quedan explicitas y son aplicables a todos los documentos.
- [x] 1.3 Registrar en el README el encuadre transversal: stack de desarrollo local, controles organizacionales/fisicos (O) como responsabilidad de la organizacion adoptante y aviso de que la documentacion no es certificacion ni auditoria (design D5). Verificacion: la nota de encuadre aparece en el README.
- [x] 1.4 Dejar constancia de que el change es documental y no tiene runner de tests: la verificacion es la existencia/contenido de los documentos, la busqueda de terminos prohibidos y `openspec validate --strict` (design D6). Verificacion: la nota figura en `tasks.md`/README y no se agregan tests de backend.

## 2. Politica de seguridad y clasificacion de la informacion

- [x] 2.1 Redactar `docs/seguridad/politica-seguridad-informacion.md` (SGD-002; 5.1): proposito, alcance, principios, ciclo de aprobacion/comunicacion/revision y encuadre del stack local. Verificacion: el documento cubre las secciones exigidas y no afirma certificacion.
- [x] 2.2 Redactar `docs/seguridad/clasificacion-etiquetado-informacion.md` (SGD-003; 5.12/5.13): niveles, criterios, reglas de etiquetado, tratamiento por nivel, clasificacion de PII y de datos del directorio con vinculo a pseudonimizacion/cifrado/minimizacion. Verificacion: PII y directorio clasificados; ejemplos sin PII real.

## 3. Roles y gestion de incidentes de seguridad

- [x] 3.1 Redactar `docs/seguridad/roles-responsabilidades-seguridad.md` (SGD-004; 5.2): responsable de seguridad y responsable de proteccion de datos (DPO) como **FUNCIONES** de la organizacion adoptante (sin nombrar personas concretas), matriz RACI y distincion de roles organizacionales vs. tecnicos. Verificacion: roles y matriz presentes; no hay nombres de personas; (O) encuadrado como externo.
- [x] 3.2 Redactar `docs/seguridad/plan-respuesta-incidentes-seguridad.md` (SGD-005; 5.24/5.26): fases del ciclo, severidad/triaje, canal de notificacion, encuadre de la ley vigente (sin obligacion general; 72 h por prudencia) y leccion aprendida del caso historico de `docs/security-hardening.md`. Verificacion: el plan cubre las fases y la seccion de notificacion es coherente con `marco-legal-ar-2026.md`.
- [x] 3.3 Redactar `docs/seguridad/procedimiento-reporte-eventos.md` (SGD-005; 5.25/5.27/6.8): canal de reporte, rol evaluador y registro de lecciones aprendidas. Verificacion: canal y evaluador definidos; encadenamiento con el plan de IR.

## 4. Activos de informacion y requisitos legales

- [x] 4.1 Redactar `docs/seguridad/inventario-activos-informacion.md` (SGD-006; 5.9): activos de datos, software y servicios (PostgreSQL, Redis, backend, N8N, frontend, Gemini/Twilio/Microsoft) con responsable y clasificacion, sin secretos. Verificacion: cada activo tiene responsable y clasificacion; no hay credenciales.
- [x] 4.2 Redactar `docs/seguridad/registro-requisitos-legales.md` (SGD-007; 5.31): Ley 25.326 y normas AAIP aplicables, cada una vinculada al documento/control que la atiende, distinguiendo normas vigentes de proyectos no sancionados. Verificacion: vigentes vs. proyectos distinguidos; cada requisito con su vinculo.
- [x] 4.3 Documentar el **consentimiento informado del propio grupo** (acta breve: Luca Gomez, Carla Bustos, Gonzalo Sevilla) como base de licitud del tratamiento **T1** (piloto/desarrollo con datos reales del grupo). Verificacion: el acta de consentimiento existe y queda referenciada desde el ROPA/registro legal; T1 declara el consentimiento como base de licitud.
- [x] 4.4 Describir en el registro de requisitos legales / ROPA el **responsable del tratamiento** (el propio grupo durante la tesis, responsable directo, NO UTN-FRM) y los **tres tratamientos** por separado: T1 piloto con datos reales del grupo; T2 corpus de investigacion con incidentes reales pseudonimizados (pseudonimizacion != disociacion, art. 2); T3 adoptante futuro (organizacion adoptante, rol funcional generico). Verificacion: responsable y T1/T2/T3 descritos por separado, con base de licitud y salvaguarda de cada uno; queda explicito que no se usan datos ficticios.

## 5. SDLC seguro, privacidad y ROPA

- [x] 5.1 Redactar `docs/seguridad/modelado-amenazas-sdlc.md` (SGD-008; 8.26): metodo de modelado de amenazas, requisitos de seguridad por change y mapeo de amenazas a controles o a C-62..C-67 sin declararlos implementados. Verificacion: cada amenaza se asocia a un control o change.
- [x] 5.2 Redactar `docs/seguridad/politica-privacidad-runtime.md` (SGD-009; 5.34): informacion al titular, base de licitud, derechos con plazos correctos (acceso 10 dias corridos; rectificacion/actualizacion/supresion 5 dias habiles) y distincion pseudonimizacion vs. disociacion (art. 2), sin atribuir derecho autonomo de oposicion. El documento describe el **objetivo/norma**, no el estado actual: este vive en `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`. Verificacion: plazos y distincion conforme a `marco-legal-ar-2026.md`; el documento no mezcla diagnostico con objetivo.
- [x] 5.3 Redactar `docs/seguridad/registro-actividades-tratamiento.md` (SGD-010; ROPA Ley 25.326): por actividad (incidentes, directorio, clasificacion automatica) finalidad, categorias de datos/titulares, destinatarios/encargados, transferencias internacionales y conservacion; transferencias a EE. UU. como pais no adecuado con instrumento requerido. El ROPA incluye el **responsable del tratamiento** y los **tres tratamientos T1/T2/T3** (ver 4.4), con el consentimiento del grupo como base de licitud de T1, y trata la inscripcion de bases (arts. 21/24) como responsabilidad de la **organizacion adoptante**, entregando un **template/checklist** documental (la tesis no inscribe). Verificacion: actividades, transferencias y conservacion registradas; responsable y T1/T2/T3 presentes; template de inscripcion disponible y sin afirmar que la tesis inscribe.

## 6. Referencias cruzadas y relaciones entre changes

- [x] 6.1 Cargar las referencias cruzadas entre documentos y completar el mapa control -> documento del README (SGD-001). Verificacion: todas las referencias resuelven a archivos existentes y el mapa cubre todos los controles objetivo.
- [x] 6.2 Documentar en el README que C-61 habilita C-63 (parametros de politica) y que C-62/C-64/C-65/C-66/C-67 son changes separados. Verificacion: la relacion figura explicitamente y es coherente con `plan-cambios-cumplimiento.md` §3/§4.
- [x] 6.3 Verificar la coherencia legal transversal: plazos ARCO (10 corridos / 5 habiles), no oposicion autonoma, pseudonimizacion vs. disociacion y transferencias (EE. UU. no adecuado). Verificacion: los documentos de privacidad y ROPA coinciden con `marco-legal-ar-2026.md`.
- [x] 6.4 Registrar como PENDIENTE la aprobacion humana (MEDIO) de la politica de seguridad y de los roles; no declarar nada vigente. El piloto opera con datos reales del grupo (T1) bajo consentimiento documentado; los datos de produccion de un adoptante (T3) no se activan sin su aprobacion. Verificacion: la aprobacion pendiente figura en el README; el consentimiento de T1 esta referenciado; T3 no se declara activado.

## 7. Validacion y cierre

- [x] 7.1 Buscar los terminos prohibidos ("certificado", "compliant", "cumple ISO") en `docs/seguridad/` y corregir cualquier aparicion. Verificacion: la busqueda no arroja coincidencias indebidas.
- [x] 7.2 Verificar la cobertura de requisitos: cada SGD-001..SGD-012 tiene su documento/seccion y al menos un escenario verificable. Verificacion: matriz requisito -> documento completa.
- [x] 7.3 Verificar que los 11 documentos de `docs/seguridad/` existen y que cada uno aplica la plantilla comun y el encuadre. Verificacion: inspeccion de la carpeta y encabezados.
- [x] 7.4 Ejecutar `openspec validate --strict --changes c-61-compliance-gobernanza` y completar la lista de comprobacion **manual** (existencia, secciones, encuadre, terminos prohibidos). Verificacion: validacion estricta sin errores y checklist manual completo.
- [x] 7.5 Anotar para el orquestador la posible actualizacion de `CHANGES.md` con la entrada de C-61 (governance MEDIO, habilita C-63, dependencias nulas) — NO se modifica `CHANGES.md` en este change. Verificacion: la anotacion queda registrada como pendiente para el orquestador.
- [x] 7.6 Registrar como **change futuro** el doc-lint automatizado de `docs/seguridad/` (patron c-42); NO se implementa en C-61. Verificacion: la anotacion del change futuro figura en `tasks.md`/README y no se agregaron scripts ni tests de backend.

---

## Notas de verificacion (manual)

- **Tarea 7.5 (pendiente para el orquestador):** evaluar agregar la entrada de C-61 en
  `CHANGES.md` (governance MEDIO, habilita C-63, dependencias nulas). NO se modifico
  `CHANGES.md` en este change.
- **Tarea 7.6 (change futuro):** registrar un change de **doc-lint automatizado** de
  `docs/seguridad/` (patron c-42) que valide estructura, encabezados y terminos prohibidos.
  NO se implemento en C-61 (no se agregaron scripts ni tests de backend).
- **Tarea 7.1:** la busqueda de terminos prohibidos solo encuentra las apariciones
  meta (la lista de terminos que el propio README declara prohibidos, exigida por 1.2). No
  hay afirmaciones del sistema en estado de certificacion ni de conformidad.
- **Modo:** Standard (change documental, sin runner de tests; design D6).
