## Why

El repositorio es PUBLICO (`lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N`). Una auditoria de exposicion de secretos encontro el arbol actual limpio, pero dejo cuatro brechas abiertas: (a) una clave Google Gemini revocada permanece en el historial de git; (b) dos funciones de escaneo de secretos de GitHub siguen deshabilitadas; (c) existe una alerta de secret scanning abierta; y (d) la rotacion previa de credenciales se aplico directamente sobre la spec principal `local-bootstrap`, sin proveniencia OPSX. Esta change codifica una postura de seguridad repetible y auditable para que esas brechas no puedan reabrirse en silencio.

## What Changes

- **Nueva capacidad `secret-hygiene`**: contrato verificable del escaneo de secretos del repositorio, que cubre el hook pre-commit local, el escaneo del lado de GitHub (secret scanning + push protection), el triaje y la resolucion de alertas, y el runbook de rotacion de credenciales expuestas.
- **Delta de `local-bootstrap`**: se formaliza con proveniencia OPSX el requisito de credenciales de desarrollo local parametrizadas por variables de entorno, sin secretos adivinables hardcodeados en archivos versionados. No se reescribe ni se duplica el texto ya editado directamente en la spec principal.
- **Runbook nuevo `docs/security-hardening.md`**: documenta que funciones de GitHub son configurables por API y cuales son solo por UI, la proteccion de push, como triar y resolver alertas (`state`/`resolution`), la instalacion del hook pre-commit y el procedimiento de rotacion de credenciales usando la filtracion de Gemini como caso de estudio.
- **Automatizacion nueva `scripts/security/configure_github_secret_scanning.sh`**: script idempotente que habilita por `gh api` las protecciones configurables por API e IMPRIME los pasos que solo se pueden hacer por UI; opcionalmente resuelve una alerta por numero con confirmacion explicita. Sin secretos embebidos.
- **Tareas operativas**: habilitar en la UI los patrones no-proveedor y las verificaciones de validez, resolver la alerta #1 como `revoked` y verificar el estado final.

**Fuera de alcance**: reimplementar la rotacion de credenciales (ya hecha en `597c03e`); reescribir el historial de git (la clave ya esta revocada, por lo que la remocion del historial es innecesaria); agregar gitleaks a CI (el escaneo server-side de GitHub mas el hook local ya cubren el caso) salvo que design.md lo justifique.

## Capabilities

### New Capabilities

- `secret-hygiene`: deteccion automatizada de secretos en el repositorio (hook pre-commit), escaneo del lado de GitHub con proteccion de push, triaje y resolucion de alertas con resolucion explicita, script de configuracion idempotente y runbook de rotacion de credenciales expuestas.

### Modified Capabilities

- `local-bootstrap`: se agrega el requisito de que las credenciales de desarrollo local se resuelvan por variables de entorno, sin valores por defecto trivialmente adivinables hardcodeados en archivos versionados, y que los valores reales vivan solo en el `.env` gitignorado. Es la formalizacion OPSX de la edicion directa aplicada en `597c03e`; el texto ya editado de la spec principal no se modifica.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/secret-hygiene/spec.md` | New | Contrato del escaneo de secretos, triaje de alertas, script y runbook |
| `openspec/specs/local-bootstrap/spec.md` | Modified (delta) | Requisito de credenciales locales parametrizadas por entorno |
| `docs/security-hardening.md` | New | Runbook operativo de endurecimiento de secretos |
| `scripts/security/configure_github_secret_scanning.sh` | New | Automatizacion idempotente de protecciones API-settable + pasos UI-only |
| GitHub (configuracion del repositorio) | External | Habilitar patrones no-proveedor y verificaciones de validez (UI); resolver alerta #1 como `revoked` |
| `.githooks/pre-commit` | Sin cambios | El hook ya existe; la spec lo caracteriza y exige su instalacion documentada |

- **Gobernanza**: CRITICAL en seguridad. El change PROPONE; el apply MUST obtener checkpoint humano antes de ejecutar acciones con efecto externo (resolver la alerta, cambiar la configuracion del repositorio en GitHub). El script solo habilita protecciones API-settable y, por defecto, imprime los pasos manuales; la resolucion de alertas es opt-in con confirmacion explicita. No se reescribe historial.
- **Dependencias**: ninguna bloqueante. `597c03e` y `2784b1b` ya estan en `origin/main`; el hook y la spec `local-bootstrap` ya existen. El unico prerequisito operativo es un `gh` autenticado con permisos de administracion del repositorio para ejecutar el script.
