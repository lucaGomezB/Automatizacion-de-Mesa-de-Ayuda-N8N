## Context

Ver `proposal.md` — Why para la motivacion. Estado actual que condiciona el enfoque:

- `docker-compose.yml` declara `N8N_BASIC_AUTH_ACTIVE`, `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` en los servicios `n8n` (lineas ~141-143) y `n8n-corpus` (lineas ~391-393), con el comentario "Autenticacion basica de N8N".
- `.env.example` publica `N8N_BASIC_AUTH_USER=admin` y `N8N_BASIC_AUTH_PASSWORD=n8n_local_dev`.
- Cuatro documentos afirman un login que no funciona: `README.md:291`, `docs/operational-guide.md:244`, `docs/n8n-workflow-guide.md:472` (usuario `admin` / password `n8n_local_dev`) y `docs/por_implementar.md:86` (usuario `admin` / clave `admin`, ademas inconsistente con los otros). `docs/security-hardening.md:191` menciona la variable como credencial parametrizada.
- Dos specs normativas dependen de las variables: `foundation-environment` (escenario "Resto de la configuracion N8N sin cambios" lista `N8N_BASIC_AUTH_ACTIVE`) y `local-bootstrap` (requisito "Credenciales de desarrollo local parametrizadas por entorno").
- Imagen fijada: `n8nio/n8n:2.11.2`.

### Evidencia empirica (stack en ejecucion)

- `GET /rest/workflows` y `GET /rest/credentials` devuelven 401 AUN pasando las credenciales de basic auth del `.env`.
- `GET /` devuelve 200 unicamente porque sirve la SPA estatica; no prueba autenticacion.
- `GET /rest/settings` expone `userManagement.smtpSetup=false`: el SMTP propio de n8n no esta configurado.
- El acceso real es la cuenta owner (email) obligatoria del primer arranque, almacenada HASHEADA en el volumen `n8n_data` (`/home/node/.n8n/database.sqlite`).
- Conclusion: las tres variables son inertes; n8n las ignora desde v1.0.

## Goals / Non-Goals

**Goals:**

- Retirar de la configuracion versionada toda variable de basic auth de N8N.
- Alinear la documentacion con el mecanismo real de acceso (cuenta owner + volumen `n8n_data`).
- Realinear las dos specs normativas sin perder la intencion de seguridad de `local-bootstrap`.

**Non-Goals:**

- Integrar un IdP (parte diferida del design de c-62).
- Cambiar credenciales de PostgreSQL u otros secretos.
- Rediseñar la autenticacion de N8N, recrear el volumen `n8n_data` o migrar datos.
- Alterar la retencion de ejecuciones o el workflow de N8N.

## Decisions

### Decision 1: Eliminar las variables inertes (en lugar de conservarlas)

- **Elegido**: eliminar las tres variables de ambos servicios y de `.env.example`.
- **Alternativa A — conservarlas inertes con un comentario "no-op"**: descartada. Deja configuracion enganosa, invita a creer que basic auth funciona y contradice la intencion de seguridad de `local-bootstrap`.
- **Alternativa B — conservarlas y documentarlas como deprecadas**: descartada. No existe consumidor de la deprecacion; agrega superficie de documentacion sin beneficio.
- **Racional**: al ser inertes, la remocion NO cambia el comportamiento; reduce confusion y hace que specs y docs digan la verdad.

### Decision 2: La documentacion describe el mecanismo real, sin inventar un default

Los documentos deben indicar que el login es la cuenta owner creada en el primer arranque, persistida en el volumen `n8n_data`, y que su password vive en el gestor de passwords del operador (no en el repo). No se reemplaza un default por otro.

### Decision 3: Realineacion de specs preservando la intencion de seguridad

- `foundation-environment`: MODIFIED del requisito ENV-001, quitando `N8N_BASIC_AUTH_ACTIVE` del escenario de variables preservadas.
- `local-bootstrap`: MODIFIED del requisito de credenciales, acotado a `POSTGRES_PASSWORD`. Se conserva integra la prohibicion de credenciales hardcodeadas o adivinables en archivos versionados.

### Decision 4: Limpieza del `.env` raiz como paso de operador

El `.env` de la raiz es gitignorado y no es artefacto versionado; su limpieza se documenta como tarea de operador y no como edicion del repositorio.

## Risks / Trade-offs

- [El operador olvida limpiar el `.env` local] → tarea de operador documentada; como las variables son inertes, no hay impacto funcional mientras tanto.
- [La documentacion vuelve a divergir] → los docs apuntan al volumen `n8n_data` como fuente de verdad del acceso.
- [La delta MODIFIED pierde detalle al archivar] → el delta copia el bloque completo del requisito original y solo edita lo necesario.
- [Expectativa de que "algo de seguridad se pierde"] → no se pierde ninguna proteccion real: la proteccion efectiva (cuenta owner) permanece; solo se retira una capa inexistente.

## Migration Plan

Cambio solo de configuracion, reversible:

1. Editar `docker-compose.yml` y `.env.example` (remocion de las variables).
2. Como las variables son inertes, no se requiere recrear el volumen `n8n_data`; basta con `docker compose up -d` para aplicar el compose sin las claves.
3. Rollback: revertir los commits de configuracion y documentacion; `docker compose up -d` restaura el estado previo. No hay migracion de datos ni cambio de codigo de aplicacion.
