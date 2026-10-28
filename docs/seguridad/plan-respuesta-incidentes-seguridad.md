# Plan de respuesta a incidentes de seguridad

> **Control mapeado**: ISO/IEC 27002:2022 5.24 (Planificacion de la gestion de incidentes),
> 5.26 (Respuesta a incidentes de seguridad) y 5.28 (Recoleccion de evidencia); NIST CSF 2.0
> RS (Respond). Requisito SGD-005.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: ciclo de gestion de incidentes de seguridad del sistema.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. Los controles organizacionales (6.x) competen al adoptante.

## 1. Proposito

Definir las fases de gestion de incidentes de seguridad, los criterios de severidad y
triaje, el canal de notificacion y el registro de lecciones aprendidas. Se complementa con
`procedimiento-reporte-eventos.md` (como se reporta un evento y quien lo evalua).

## 2. Fases del ciclo de gestion

1. **Preparacion.** Roles definidos (`roles-responsabilidades-seguridad.md`), canal de
   reporte activo, inventario de activos actualizado, runbook de higiene de secretos
   (`docs/security-hardening.md`).
2. **Deteccion y triaje.** Recepcion del evento, verificacion inicial, clasificacion por
   severidad y activacion del plan.
3. **Contencion.** Acciones para limitar el impacto (revocar/rotar credenciales, aislar
   servicio, cortar egreso) sin destruir evidencia.
4. **Erradicacion.** Corregir la causa raiz (parche, configuracion, rotacion definitiva).
5. **Recuperacion.** Restaurar el servicio y verificar el estado seguro; monitorear
   reincidencia.
6. **Lecciones aprendidas.** Registrar causa raiz, acciones y mejoras de control (ver
   `procedimiento-reporte-eventos.md` §4).

## 3. Severidad y triaje

| Severidad | Criterio | Tiempo de primera respuesta |
|-----------|----------|-----------------------------|
| **S1 Critica** | Exposicion de PII o de material de clave; compromiso de servicio con datos | Inmediata |
| **S2 Alta** | Acceso no autorizado, fuga contenida, servicio interno expuesto | Mismo dia |
| **S3 Media** | Desviacion de configuracion, error con impacto acotado | 1-3 dias |
| **S4 Baja** | Hallazgo sin exposicion inmediata; mejora recomendada | Backlog de seguridad |

El triaje lo realiza el **responsable de seguridad** (funcion), con consulta al **DPO** si
hay datos personales involucrados.

## 4. Canal de notificacion y encuadre legal

- **Canal interno de reporte**: `procedimiento-reporte-eventos.md`. Todo incidente se
  registra con un identificador unico.
- **Encuadre legal (Ley 25.326 vigente)**: la ley **NO impone una obligacion general y
  autonoma** de notificar brechas de seguridad a la autoridad ni a los titulares. El deber
  de notificacion aparece **solo en los proyectos de reforma** (72 horas) y en regimenes
  sectoriales. Ver `docs/cumplimiento/marco-legal-ar-2026.md` §4.
- **Decision de prudencia**: se adopta el estandar de **72 horas** de los proyectos de
  reforma por prudencia, para no quedar en incumplimiento si la reforma se sanciona. La
  notificacion a la AAIP y a los titulares, cuando corresponda, la decide el
  **responsable de seguridad** con el **DPO**.
- **Notificacion a terceros**: si el incidente involucra a un proveedor (Gemini, Twilio,
  Microsoft, N8N), se activa el contacto del proveedor y se documenta el analisis.

## 5. Manejo de evidencia y cadena de custodia (5.28)

Define como se maneja la evidencia de un incidente de seguridad (ISO/IEC 27002:2022 5.28)
cuando el incidente ocurre dentro del alcance del repositorio. La **cadena de custodia
formal** y la **preservacion forense completa** competen a la organizacion adoptante cuando
el incidente exceda ese alcance; este documento describe el procedimiento minimo aplicable.

### 5.1 Identificacion de la evidencia

Evidencia recolectable del sistema:

- **Logs estructurados** del backend (`App/Backend/app/core/logging.py`): eventos de
  autenticacion, errores, accesos y decisiones del guarda de costo; el numero de origen
  aparece como identificador HMAC no reversible.
- **Traza de auditoria del directorio** (`directorio_auditoria`): actor, operacion,
  resultado e instante, sin PII.
- **Registro de auditoria de cambios** del incidente (historial y comentarios).
- **Artefactos de infraestructura**: `docker-compose.yml`, `nginx/nginx.conf`, imagenes
  fijadas y salidas de los preflight de costo.
- **Respaldo cifrado** vigente cuando el incidente afecta integridad de datos.

### 5.2 Recoleccion y preservacion

- Recolectar **antes de la contencion o erradicacion** que pueda destruir la evidencia
  (rotacion de credenciales, purga, reescritura de archivos).
- Preservar el **original sin editar**: copiar el artefacto a un almacenamiento con control
  de acceso (N3/N4) y trabajar sobre la copia.
- Registrar por cada artefacto: identificador, origen, fecha/hora de recoleccion, actor que
  recolecta y ubicacion.

### 5.3 Integridad verificable

- Calcular un **hash criptografico** (SHA-256) de cada artefacto al momento de recolectarlo y
  volver a calcularlo antes de cada transferencia; registrar ambos valores.
- Cualquier diferencia de hash se trata como posible alteracion y se documenta como incidente
  secundario.
- El **numero de origen** y los datos personales no se incorporan a la evidencia en claro;
  se preservan mediante los identificadores derivados.

### 5.4 Custodios y transferencias

| Evento | Registro minimo |
|--------|-----------------|
| Recoleccion | Artefacto, hash, actor, fecha/hora, ubicacion |
| Custodia | Custodio responsable (funcion) y periodo |
| Transferencia | Origen, destino, motivo, hash de salida y hash de entrada, fecha/hora |

### 5.5 Retencion

La retencion de cada clase de evidencia se rige por `politica-retencion-logs.md` (por clase
de registro) y por el ROPA (`registro-actividades-tratamiento.md`). La evidencia de un
incidente no se conserva mas alla de lo necesario para su tratamiento y las obligaciones
legales aplicables.

### 5.6 Encuadre

La **cadena de custodia formal** (formularios, sellado, peritaje) y la **preservacion forense
completa** son responsabilidad de la **organizacion adoptante** cuando el incidente exceda el
alcance del repositorio. El repositorio garantiza la recoleccion, el hash de integridad y el
registro de custodios y transferencias descritos arriba.

## 6. Leccion aprendida historica (caso Gemini)

Se registra como leccion aprendida el **caso historico de filtracion de la clave Google
Gemini**, documentado en `docs/security-hardening.md` §5:

- Un archivo `.env` con una `GEMINI_API_KEY` real fue commiteado al historial; Google
  bloqueo la clave por estar expuesta.
- El tratamiento correcto fue: **revocar en el proveedor primero**, **rotar** el valor en
  el `.env` gitignorado, verificar el arbol limpio, resolver la alerta de secret scanning
  como `revoked` y **no** reescribir el historial de git.
- Mejora de control derivada: hook pre-commit, gitleaks en CI y push protection de GitHub
  como defensa en profundidad (controles mapeados a ISO 8.28 y al change C-64).

## 7. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.24/5.26/5.28 y NIST CSF 2.0 RS. No
constituye certificacion ni auditoria. El plan no reemplaza los procedimientos operativos
(`docs/troubleshooting.md`, `docs/operational-guide.md`): los complementa para eventos de
seguridad.
