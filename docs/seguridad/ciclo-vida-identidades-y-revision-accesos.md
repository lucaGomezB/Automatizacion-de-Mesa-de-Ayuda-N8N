# Ciclo de vida de identidades y revision de accesos (organizacional)

| Campo | Contenido |
|-------|-----------|
| Control mapeado | ISO/IEC 27002:2022 5.16 (gestion del ciclo de vida de la identidad) y 5.18 (derechos de acceso); requisito IAH-011 del change `c-63c` |
| Estado | v1 — aprobada por el autor el 2026-10-08 (governance CRITICO) |
| Alcance | Procesos ORGANIZACIONALES de alta, cambio y baja de identidades y de aprobacion/revision periodica de derechos de acceso. NO es codigo del repositorio |
| Encuadre | Control organizacional (O): responsabilidad de la organizacion adoptante. El repositorio no lo implementa ni lo opera |
| Aviso de lenguaje | Alineado con ISO/IEC 27002:2022 5.16 y 5.18. No constituye certificacion ni auditoria |

## 1. Proposito

Documentar, como responsabilidad de la organizacion adoptante (control
organizacional, O), el ciclo de vida de las identidades y el proceso de
aprobacion y revision de derechos de acceso. El sistema aporta los mecanismos
tecnicos de soporte; la organizacion aporta el proceso, la aprobacion y la
periodicidad.

## 2. Ciclo de vida de identidades (5.16)

El sistema soporta las operaciones tecnicas; el PROCESO es organizacional.

| Etapa | Responsabilidad de la organizacion (O) | Soporte tecnico en el sistema |
|-------|----------------------------------------|-------------------------------|
| Alta | Solicitud, aprobacion por el responsable del recurso y registro de la persona | Creacion de la cuenta (`users`), asignacion de rol y sector, `is_privileged` segun corresponda |
| Cambio | Revalidacion ante cambio de puesto, sector o nivel de privilegio | Reasignacion de rol/sector; `is_privileged` es la fuente de verdad del privilegio (IAH-005) |
| Baja | Revocacion oportuna y registro del cese | `is_active=false`; revocacion de sesiones con `token_version` y refresh (IAH-004); reset/desactivacion de MFA |

Reglas:
- Toda alta, cambio o baja MUST quedar aprobada por el responsable designado y
  registrada. La organizacion define el circuito de aprobacion.
- La baja MUST ejecutarse dentro del plazo definido por la organizacion y
  verificarse contra las cuentas activas.
- El privilegio administrativo se otorga por excepcion, con justificacion y
  plazo, y se revisa con mayor frecuencia (8.2).

## 3. Aprobacion y revision de derechos de acceso (5.18)

| Actividad | Descripcion | Periodicidad sugerida |
|-----------|-------------|-----------------------|
| Aprobacion inicial | Los derechos se otorgan solo tras la aprobacion del responsable del recurso | Por evento (alta/cambio) |
| Revision periodica | La organizacion revisa que cada identidad conserve solo los accesos necesarios | Al menos semestral |
| Revision de privilegiados | Revision reforzada de las cuentas con privilegio administrativo | Al menos trimestral |
| Recertificacion | Confirmacion explicita de la vigencia de cada derecho o su retiro | Anual |
| Retiro | Revocacion de derechos obsoletos y registro de la accion | Al detectarse |

Reglas:
- El proceso y la periodicidad son definidos por la organizacion adoptante (O);
  los valores de la tabla son sugeridos, no impuestos por el repositorio.
- La revision MUST producir evidencia (registro de la revision y de las
  decisiones) y MUST contemplar el retiro de accesos no justificados.
- La revision aprovecha el soporte tecnico disponible: listado de cuentas
  activas, marca `is_privileged`, estado de MFA y revocacion de sesiones.

## 4. Limites

- Este documento es ORGANIZACIONAL (O). No describe controles implementados por
  el repositorio.
- La gestion de secretos y claves (8.2/8.24) se documenta en
  `docs/seguridad/gestion-secretos-y-rotacion.md`.
- La respuesta a incidentes de seguridad sigue el
  `docs/seguridad/plan-respuesta-incidentes-seguridad.md`.

## 5. Fuentes internas

- `docs/seguridad/README.md` — indice del cuerpo documental.
- `docs/seguridad/roles-responsabilidades-seguridad.md` — roles y matriz RACI.
- `App/Backend/app/services/auth_service.py` — revocacion y sesiones.
- `App/Backend/app/services/privilege_service.py` — privilegio de la identidad.
