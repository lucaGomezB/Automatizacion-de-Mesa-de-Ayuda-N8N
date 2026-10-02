# Registro de requisitos legales y regulatorios

> **Control mapeado**: ISO/IEC 27002:2022 5.31 (Requisitos legales, estatutarios,
> regulatorios y contractuales); NIST CSF 2.0 GV (Govern). Requisitos SGD-007 y SGD-012.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: requisitos legales vigentes y proyectos no sancionados aplicables al sistema.
> **Encuadre**: relevamiento informativo, **no** asesoramiento juridico. Documento
> **alineado con** la Ley 25.326; no es certificacion ni auditoria.

## 1. Proposito

Enumerar los requisitos legales y regulatorios aplicables al sistema, distinguir los
**vigentes** de los **proyectos no sancionados**, y vincular cada requisito con el
documento o control del sistema que lo atiende, senalando lo que queda como responsabilidad
de la organizacion adoptante.

## 2. Requisitos vigentes

Autoridad de aplicacion: **Agencia de Acceso a la Informacion Publica (AAIP)**; area
tecnica: Direccion Nacional de Proteccion de Datos Personales (DNPDP). Fuente:
`docs/cumplimiento/marco-legal-ar-2026.md`.

| Norma / requisito | Contenido relevante | Documento/control que lo atiende |
|-------------------|---------------------|----------------------------------|
| Ley 25.326 art. 5 | Consentimiento libre, expreso e informado | ROPA (bases de licitud); `acta-consentimiento-t1.md` (T1) |
| Ley 25.326 art. 6 | Deber de informacion al titular (finalidad, destinatarios, identidad, derechos) | `politica-privacidad-runtime.md` |
| Ley 25.326 art. 9 | Medidas tecnicas y organizativas de seguridad y confidencialidad | `politica-seguridad-informacion.md`; controles mapeados a C-62 a C-67 |
| Ley 25.326 art. 10 | Deber de confidencialidad, subsistente tras la relacion | `roles-responsabilidades-seguridad.md`; (O) adoptante |
| Ley 25.326 arts. 14 y 16 | Acceso: 10 dias corridos; rectificacion/actualizacion/supresion: 5 dias habiles | `politica-privacidad-runtime.md` |
| Ley 25.326 art. 12 | Transferencias internacionales; EE. UU. no es pais adecuado | ROPA `registro-actividades-tratamiento.md`; change C-66 |
| Ley 25.326 arts. 21 y 24 | Inscripcion de bases de datos ante la AAIP | Responsabilidad del **adoptante**; template en ROPA §7 |
| Ley 25.326 arts. 2 y 11 | Disociacion de datos; no hay regulacion expresa de pseudonimizacion | `politica-privacidad-runtime.md`; ROPA T2 |
| Resolucion AAIP 4/2019 | Criterios obligatorios; decisiones automatizadas y explicabilidad | `modelado-amenazas-sdlc.md`; revision humana del clasificador |
| Resolucion AAIP 47/2018 | Medidas de seguridad "recomendadas" | `politica-seguridad-informacion.md`; clasificacion |
| Resolucion AAIP 14/2018 | Informacion al titular en sitio visible | `politica-privacidad-runtime.md` |
| Disposicion DNPDP 60/2016 y Res. AAIP 34/2019 | Paises adecuados y clausulas contractuales modelo | ROPA (transferencias); change C-66 |
| Resolucion AAIP 198/2023 | Clausulas contractuales modelo de la RIPD | ROPA (transferencias); change C-66 |
| Resolucion AAIP 159/2018 | Normas corporativas vinculantes | ROPA (mecanismo alternativo) |
| Ley 27.483 | Aprobacion del Convenio 108 del Consejo de Europa | ROPA (marco de transferencias) |
| Ley 26.951 | Registro Nacional No Llame y su regimen sancionatorio | (O) adoptante; evaluar en contacto telefonico |
| Ley 25.326 art. 31 | Sanciones administrativas; art. 32: tipos penales | Contexto de cumplimiento; (O) adoptante |

## 3. Proyectos no sancionados (distinguir de vigentes)

Los siguientes **no son ley** a la fecha de referencia (2026-10); su contenido no obliga,
pero informa decisiones de prudencia:

| Proyecto | Estado | Contenido relevante |
|----------|--------|---------------------|
| Mensaje 87/2023 (reforma alineada al RGPD) | Caduco parlamentariamente | Obligacion de notificacion de brechas en **72 horas** (art. 21 propuesto) |
| Expediente 1948-D-2025 (Carro) | En tramite | Reproduce la notificacion de 72 horas; "dato inferido" |
| Expediente 3540-D-2025 | En tramite | Transparencia algoritmica y derecho a la explicacion |
| Expediente 2968-D-2025 | En tramite | Proteccion especial de ninos, ninas y adolescentes |
| Ley nacional integral de IA | No existe | Solo normas sectoriales (BCRA, SIGEN, MPF, provincias) |

**Decision de prudencia**: se adopta el estandar de **72 horas** de los proyectos de
reforma para la notificacion de brechas, aunque la ley vigente no lo imponga
(`plan-respuesta-incidentes-seguridad.md` §4).

## 4. Responsable del tratamiento

Durante la tesis, el **responsable del tratamiento** es el propio **grupo de desarrollo**
(Luca Gomez, Carla Bustos, Gonzalo Sevilla), como **responsable directo**, **NO la
UTN-FRM**. La UTN-FRM no actua como responsable del tratamiento del piloto.

La organizacion que despliegue el sistema en produccion (adoptante) sera responsable del
tratamiento de **T3** (rol funcional generico). Ver `registro-actividades-tratamiento.md`.

## 5. Los tres tratamientos (resumen)

| Tratamiento | Datos | Responsable | Base de licitud / salvaguarda |
|-------------|-------|-------------|-------------------------------|
| **T1 Piloto/desarrollo** | Datos REALES del grupo y usuarios de prueba que apuntan a contactos del grupo | El grupo | **Consentimiento informado** del grupo (`acta-consentimiento-t1.md`) |
| **T2 Corpus de investigacion** | Incidentes reales **pseudonimizados** | El grupo | Pseudonimizacion; **no** equivale a disociacion (art. 2) |
| **T3 Adoptante futuro** | Datos de produccion de una empresa que despliegue el sistema | Organizacion adoptante | Politica y base de licitud propias del adoptante |

El sistema **no usa datos ficticios**: es un piloto con datos reales del equipo. Detalle
completo en `registro-actividades-tratamiento.md`.

## 6. Inscripcion de bases (arts. 21/24) — responsabilidad del adoptante

La inscripcion de las bases de datos ante la AAIP es responsabilidad de la **organizacion
adoptante**. La tesis **no inscribe** bases. El sistema entrega un **template/checklist**
documental en `registro-actividades-tratamiento.md` §7 para que el adoptante complete el
tramite.

## 7. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.31 y NIST CSF 2.0 GV. Relevamiento
informativo, no asesoramiento juridico. No constituye certificacion ni auditoria. Las
normas vigentes y los proyectos se distinguen en §2 y §3.
