# Registro de actividades de tratamiento (ROPA)

> **Control mapeado**: Registro de actividades de tratamiento segun Ley 25.326, en
> **alineacion con** ISO/IEC 27002:2022 5.34 y 5.31; NIST CSF 2.0 GV. Requisitos SGD-010 y
> SGD-012.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: actividades de tratamiento, transferencias, conservacion, responsable y los
> tratamientos T1/T2/T3; template de inscripcion de bases para el adoptante.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria.

## 1. Proposito

Registrar las actividades de tratamiento del sistema (finalidad, categorias de datos y de
titulares, destinatarios/encargados, transferencias internacionales y plazo de
conservacion), identificar al responsable del tratamiento, describir por separado los tres
tratamientos T1/T2/T3 y entregar el template de inscripcion de bases (arts. 21/24) para la
organizacion adoptante.

## 2. Responsable del tratamiento

- **Durante la tesis:** el **grupo de desarrollo** (Luca Gomez, Carla Bustos, Gonzalo
  Sevilla), como **responsable directo** del tratamiento, **NO la UTN-FRM**.
- **T3 (adoptante futuro):** la organizacion que despliegue el sistema, como responsable
  funcional generico.

## 3. Actividades de tratamiento

### 3.1 Gestion de incidentes

| Campo | Contenido |
|-------|-----------|
| Finalidad | Registro, clasificacion y derivacion de incidentes de mesa de ayuda |
| Categorias de datos | Identificador de usuario, descripcion del incidente (original cifrada / pseudonimizada), canal de origen, numero llamante |
| Categorias de titulares | Empleados/usuarios internos; llamantes |
| Destinatarios/encargados | N8N (orquestacion), Google Gemini (inferencia, solo texto pseudonimizado) |
| Transferencia internacional | Gemini (EE. UU. — pais NO adecuado) |
| Conservacion | Incidentes: conservacion indefinida por decision de diseno (revisar contra minimizacion); logs N8N podados a 30 dias |

### 3.2 Directorio de empleados

| Campo | Contenido |
|-------|-----------|
| Finalidad | Enrutar y notificar incidentes; gestion operativa del personal |
| Categorias de datos | Nombre, correo, celular, sector, estado, rol |
| Categorias de titulares | Empleados |
| Destinatarios/encargados | Microsoft Outlook (correo), Twilio (SMS/telefonia) |
| Transferencia internacional | Twilio / Microsoft (EE. UU. — pais NO adecuado) |
| Conservacion | Purga de bajas a 1 ano (`directorio_service.py`) |

### 3.3 Clasificacion automatica

| Campo | Contenido |
|-------|-----------|
| Finalidad | Asignar sector con confianza; revision humana con confianza < 0,70 |
| Categorias de datos | Texto pseudonimizado del incidente, confianza, respuesta cruda del modelo |
| Categorias de titulares | Llamantes/usuarios de los que proviene el incidente |
| Destinatarios/encargados | Google Gemini (inferencia) |
| Transferencia internacional | Gemini (EE. UU. — pais NO adecuado) |
| Conservacion | Trazas de clasificacion asociadas al incidente |

## 4. Transferencias internacionales

- **Estados Unidos NO es pais adecuado** (art. 12 de la Ley 25.326). Afecta a Gemini,
  Twilio y Microsoft.
- **Instrumento requerido**: consentimiento expreso del titular o **clausulas
  contractuales modelo** (Disposicion DNPDP 60/2016; Resolucion AAIP 198/2023) o normas
  corporativas vinculantes (Resolucion AAIP 159/2018).
- La **pseudonimizacion** previa mitiga el riesgo, pero **no sustituye** el instrumento.
- El instrumento y su documentacion se abordan en el change **C-66**.

## 5. Responsable del tratamiento y los tres tratamientos

| | **T1 Piloto/desarrollo** | **T2 Corpus de investigacion** | **T3 Adoptante futuro** |
|---|---|---|---|
| Datos | **REALES**: cuentas del grupo y usuarios de prueba cuyos correos/celulares apuntan a contactos del grupo | Incidentes **reales pseudonimizados** | Datos de produccion de una empresa que despliegue el sistema |
| Responsable | El grupo (responsable directo) | El grupo | Organizacion adoptante (rol funcional generico) |
| Base de licitud / salvaguarda | **Consentimiento informado** del grupo (`acta-consentimiento-t1.md`) | Pseudonimizacion | Politica y base de licitud propias del adoptante |

### 5.1 T1 — Piloto/desarrollo

- Datos **reales** del grupo (cuentas) y usuarios de prueba cuyos correos/celulares apuntan
  a contactos del **propio grupo**, usados para depuracion.
- Base de licitud: **consentimiento informado** documentado en `acta-consentimiento-t1.md`.
- **El sistema no usa datos ficticios**: es un piloto con datos reales del equipo.

### 5.2 T2 — Corpus de investigacion

- Incidentes **reales pseudonimizados**.
- **Aclaracion:** la pseudonimizacion **no** equivale a la **disociacion** (art. 2) porque
  el original existe y es **reidentificable** con informacion adicional.
- Salvaguarda: pseudonimizacion determinista + cifrado at-rest del original.

### 5.3 T3 — Adoptante futuro

- Datos de produccion de una **organizacion que despliegue el sistema**; el responsable es
  el adoptante como **rol funcional generico**.
- Los datos de produccion de un adoptante **no se activan** sin su aprobacion y sin su
  propia base de licitud e instrumentos de transferencia.

## 6. Conservacion y minimizacion

- Incidentes: sin politica de borrado definida (brecha mapeada a ISO 8.10).
- Directorio: purga de bajas a 1 ano.
- N8N: poda de ejecuciones a 30 dias.
- Logs: sin retencion documentada; el numero llamante crudo en logs es una brecha mapeada a
  ISO 8.12/8.15 (change C-66).

## 7. Inscripcion de bases (arts. 21/24) — template/checklist para el adoptante

La inscripcion de las bases de datos ante la AAIP es **responsabilidad de la organizacion
adoptante**. **La tesis no inscribe bases.** Checklist documental para el adoptante:

- [ ] Identificar las bases alcanzadas (incidentes, directorio) y su finalidad.
- [ ] Designar al responsable del tratamiento y al responsable de seguridad (funciones).
- [ ] Determinar la base de licitud por base (art. 5) y el deber de informacion (art. 6).
- [ ] Completar los formularios de inscripcion de la AAIP (Registro Nacional de Bases de
      Datos Personales, arts. 21 y 24).
- [ ] Documentar las medidas de seguridad (Resolucion AAIP 47/2018).
- [ ] Documentar el instrumento de transferencia internacional (art. 12) para Gemini,
      Twilio y Microsoft.
- [ ] Registrar altas, modificaciones y bajas de bases en el registro de la AAIP.
- [ ] Conservar la constancia de inscripcion como evidencia.

> La tesis **no** inscribe bases ni afirma hacerlo. El template se entrega como guia; el
> tramite ante la AAIP es del adoptante.

## 8. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.34/5.31 y NIST CSF 2.0 GV. No
constituye certificacion ni auditoria. Las actividades, transferencias y conservacion son
el objetivo/norma; el estado actual de implementacion vive en el gap assessment.
