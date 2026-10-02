## Context

Ver `proposal.md — Why`. Restricciones verificadas que moldean el enfoque:

- **Change documental (categoria D).** No toca runtime, API, esquema, CI ni infraestructura. El entregable es un cuerpo de documentos versionados; el "behavior" verificable es la existencia, el contenido y el lenguaje de esos documentos (specs `security-governance-docs`).
- **Insumos normativos ya existentes.** `docs/cumplimiento/plan-cambios-cumplimiento.md` (§1-§3, fila C-61), `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas y controles) y `docs/cumplimiento/marco-legal-ar-2026.md` (Ley 25.326, AAIP, plazos, transferencias). No se re-investiga: se destila y se referencia.
- **Stack de desarrollo local.** `docker-compose.yml` (`name: mesa_local`); no existe despliegue productivo declarado. Varios controles ISO/NIST (produccion, fisicos, personas) NO son exigibles al repositorio.
- **Convenciones del proyecto.** Documentacion en `docs/` con nombres en espanol (`por_implementar.md`, `security-hardening.md`); el texto de tesis vive en `docs/Tesis/v9 (IA)` y queda FUERA de alcance. Capas y codigo no se tocan.
- **Precedente documental.** Changes previos (c-42/c-43/c-44) modelaron requisitos de documentacion en OpenSpec y agregaron verificacion estructural; C-61 puede seguir el patron del indice y el mapa de trazabilidad sin escribir codigo de produccion.
- **Governance MEDIO.** Define politicas de seguridad, clasificacion de PII y manejo de incidentes; la aprobacion formal de la politica de seguridad es humana.

## Goals / Non-Goals

**Goals:**

- Ubicar y estructurar los 11 documentos de gobernanza en `docs/seguridad/` con un indice y un mapa de trazabilidad control -> documento.
- Fijar una plantilla comun de documento (control mapeado, estado, alcance, encuadre) y una regla de lenguaje verificable.
- Destilar el gap assessment y el marco legal en documentos accionables, sin re-investigar.
- Dejar explicito el encuadre (D) documental / (O) organizacional y el caracter de stack de desarrollo local.
- Definir como se referencia C-61 desde los demas changes (habilitador de C-63; marco para C-62/C-64/C-65/C-66/C-67).

**Non-Goals:**

- Implementar politicas, controles tecnicos ni la interfaz de privacidad en runtime (eso es C-62 a C-67).
- Escribir la prosa de tesis (`docs/Tesis/v9 (IA)`) ni modificar `CHANGES.md`.
- Agregar codigo de produccion, tests de backend, migraciones, CI o infraestructura.
- Declarar conformidad, certificacion o auditoria.

## Decisions

### D1: Ubicacion y estructura de la carpeta

Los documentos viven en `docs/seguridad/` (carpeta nueva, hermana de `docs/cumplimiento/`). `docs/seguridad/README.md` es el indice: lista cada documento, su proposito, su estado (borrador/aprobado) y la fecha/periodicidad de revision. Se elige una carpeta dedicada en vez de dispersar los documentos en `docs/` porque forman un cuerpo coherente, referenciable y extensible por los changes posteriores. Alternativa considerada: reutilizar `docs/cumplimiento/` — descartada porque esa carpeta contiene los insumos de analisis (gap assessment, marco legal, plan), no las politicas del sistema; mezclarlos confundiria insumo con entregable.

### D2: Plantilla comun por documento

Cada documento abre con un encabezado que declara: control(es) mapeado(s) (ISO/IEC 27002 y NIST CSF), estado del documento, alcance y la nota de encuadre (stack de desarrollo local; controles (O) fuera del repositorio). Luego desarrolla las secciones exigidas por su requisito SGD. Se unifica la plantilla para que el mapa de trazabilidad, la revision y el lenguaje se apliquen de forma homogenea. Alternativa considerada: formato libre por documento — descartada porque dificulta la verificacion y la consistencia.

### D3: Mapa de trazabilidad en el indice

`docs/seguridad/README.md` contiene una tabla control -> documento -> requisito SGD. El mapa cubre los controles objetivo del plan (5.1, 5.2, 5.9, 5.12, 5.13, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26) y las funciones NIST CSF Govern/Identify. Es la evidencia de cobertura del change y la base de la seccion de cumplimiento de la tesis (que se redacta aparte). Alternativa considerada: sin mapa y solo documentos sueltos — descartada: el valor para la defensa esta en la trazabilidad explicita.

### D4: Regla de lenguaje verificable

Todos los documentos usan "alineado con" / "controles mapeados a". Se prohibe "certificado", "compliant", "cumple ISO/NIST". La verificacion es mecanica: busqueda de los terminos prohibidos en `docs/seguridad/` durante la tarea de validacion, ademas de `openspec validate --strict`. El encuadre de "no es certificacion ni auditoria" se declara en el indice y en cada politica. Alternativa considerada: depender solo de revision humana — descartada (el lenguaje de alineacion es una regla del plan y debe poder verificarse).

### D5: Encuadre (D)/(O) y stack local

Cada documento distingue lo que el repositorio evidencia (D) de lo que compete a la organizacion adoptante (O: personas 6.x, fisicos 7.x, seleccion/formacion/sanciones, endpoints, contratos). Se repite una nota de encuadre: el stack es de desarrollo local, varios controles de produccion no aplican todavia. Alternativa considerada: omitir el encuadre — descartada: el gap assessment ya advierte que no debe presentarse documentacion como control implementado.

### D6: Verificacion manual (sin doc-lint en este change)

La verificacion es **MANUAL**: la lista de comprobacion de este `tasks.md` (existencia de los 11 documentos, secciones requeridas, encuadre, terminos prohibidos) mas `openspec validate --strict --changes c-61-compliance-gobernanza`. No se agrega ningun runner, script ni test de backend: mantiene el change en categoria D. Un **doc-lint automatizado** queda registrado como **change futuro** y NO se implementa en C-61. Alternativa considerada: test estructural en `App/Backend/tests/` (patron c-42) — descartada; se difiere al change de doc-lint.

### D7: Limites con los changes hermanos

C-61 define el **marco documental** (que existe y como se encuadra). No implementa: C-62 (hardening), C-63 (identidad/accesos/claves), C-64 (vulnerabilidades/supply chain), C-65 (backup/continuidad), C-66 (privacidad/transferencias runtime) y C-67 (SMS) son changes separados. C-61 **habilita C-63** fijando los parametros de politica (clasificacion, roles, requisitos) que C-63 consume. La politica de privacidad en runtime y el ROPA documentan el marco legal, pero el tratamiento del numero llamante y los instrumentos de transferencia son de C-66. Alternativa considerada: absorber C-64/C-65 (ambos tienen parte documental) — descartada: el plan los define como changes independientes.

### D8: Governance, roles funcionales y datos del piloto

Gobierno **MEDIO**: documental pero condicionante. Los documentos se crean como borradores; la aprobacion formal de la politica de seguridad queda explicitamente pendiente del autor. Los **roles de seguridad** (responsable de seguridad, DPO) se documentan como **FUNCIONES** de la organizacion adoptante, sin nombrar personas concretas en el repositorio (evita datos personales); la asignacion nominal es responsabilidad del adoptante. El piloto de la tesis usa **datos reales del grupo** (T1, ver D9) con consentimiento documentado; los datos de produccion de un adoptante (T3) no se activan sin su aprobacion.

### D9: Responsable del tratamiento y los tres tratamientos

Durante la tesis el **responsable del tratamiento** es el propio **grupo de desarrollo** (Luca Gomez, Carla Bustos, Gonzalo Sevilla), como responsable directo, NO la UTN-FRM. Se documenta el **consentimiento informado del propio grupo** como base de licitud. El diseno describe **tres tratamientos separados**; el sistema **no usa datos ficticios**: es un piloto con datos reales del equipo.

| Tratamiento | Datos | Responsable | Base de licitud / salvaguarda |
|-------------|-------|-------------|-------------------------------|
| **T1 Piloto/desarrollo** | Datos REALES: cuentas del grupo y usuarios de prueba cuyos correos/celulares apuntan a contactos del grupo (debugging) | El grupo | Consentimiento informado del propio grupo (acta documentada) |
| **T2 Corpus de investigacion** | Incidentes reales **pseudonimizados** | El grupo | Pseudonimizacion. Aclaracion: pseudonimizacion != disociacion (art. 2), porque el original existe y es reidentificable |
| **T3 Adoptante futuro** | Datos de produccion de una empresa que despliegue el sistema | Organizacion adoptante (rol funcional, generico) | Politica y base de licitud propias del adoptante |

Alternativa considerada: tratar el sistema como demo con datos ficticios — descartada: el piloto opera con datos reales del grupo.

### D10: Alcance de la politica de privacidad

`docs/seguridad/politica-privacidad-runtime.md` describe el **objetivo/norma** (que debe informarse al titular, bases de licitud y derechos), no el estado actual de implementacion. El estado actual (brechas, controles presentes/ausentes) vive en `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`. Alternativa considerada: describir el estado actual en la politica — descartada: mezcla objetivo normativo con diagnostico y envejece mal.

### D11: Registro de bases (arts. 21/24) como responsabilidad del adoptante

La inscripcion de las bases de datos ante la AAIP (Ley 25.326 arts. 21/24) es responsabilidad de la **organizacion adoptante**; la tesis **no inscribe** bases. El sistema entrega un **template/checklist documental** (dentro del ROPA / registro de requisitos legales) para que el adoptante complete el tramite. Alternativa considerada: inscribir durante la tesis — descartada: no corresponde a un desarrollo no desplegado y excede el alcance.

## Risks / Trade-offs

- **[Lenguaje que sugiera certificacion]** → Mitigacion: regla D4 + busqueda de terminos prohibidos en la validacion; revision de redaccion.
- **[Sobredeclarar controles (O) como implementados]** → Mitigacion: encuadre D5 repetido por documento; cada documento declara que no es certificacion.
- **[Solapamiento con C-64/C-65/C-66]** → Mitigacion: D7 fija los limites; C-61 documenta el marco, los demas changes implementan y lo extienden.
- **[Deriva entre documentos]** → Mitigacion: plantilla comun D2, indice con estado/version y mapa de trazabilidad D3.
- **[Documentos que envejecen sin revision]** → Mitigacion: campo de revision periodica en el indice; nota de periodicidad por documento.

## Migration Plan

1. Crear `docs/seguridad/` y el indice `README.md` con proposito, estado y mapa de trazabilidad (D1, D3).
2. Redactar los documentos en orden de dependencia: politica de seguridad (5.1) -> clasificacion (5.12/5.13) -> roles (5.2, funciones) -> plan de IR y reporte (5.24-5.27) -> inventario de activos (5.9) -> requisitos legales (5.31, con responsable y T1/T2/T3) -> SDLC/modelado de amenazas (8.26) -> privacidad en runtime (5.34, objetivo/norma) -> ROPA (responsable, T1/T2/T3, template de inscripcion). Documentar en paralelo el acta de consentimiento del grupo (T1).
3. Aplicar la plantilla comun (D2) y la regla de lenguaje (D4) a todos; cargar referencias cruzadas y el encuadre (D5).
4. Verificar: `openspec validate --strict --changes c-61-compliance-gobernanza`, existencia de los 11 documentos y busqueda de terminos prohibidos (D6); confirmar el mapeo control -> documento (D3).
5. Registrar la aprobacion humana pendiente de la politica/roles (D8).
6. Rollback: revertir el commit elimina `docs/seguridad/` y el delta spec; no hay migraciones, datos ni runtime que restaurar.

## Open Questions

Todas resueltas por decision del autor (2026-10):

1. **Roles** → funciones de la organizacion adoptante, sin nombres de personas (D8).
2. **Verificacion** → manual (checklist + `openspec validate --strict`); doc-lint automatizado = change futuro, no se implementa aca (D6).
3. **Ubicacion** → `docs/seguridad/` confirmada (D1).
4. **Politica de privacidad** → describe el objetivo/norma; el estado actual vive en el gap assessment (D10).
5. **Inscripcion de bases (arts. 21/24)** → responsabilidad del adoptante; el sistema entrega template/checklist; la tesis no inscribe (D11).

Nuevo (antes inexistente): responsable del tratamiento y los tres tratamientos (T1/T2/T3) fijados en D9, con el consentimiento del grupo como base de licitud de T1.
