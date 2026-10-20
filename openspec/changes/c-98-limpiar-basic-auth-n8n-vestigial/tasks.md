## 1. Limpieza de configuracion versionada

- [x] 1.1 Eliminar `N8N_BASIC_AUTH_ACTIVE`, `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` del servicio `n8n` en `docker-compose.yml`, junto con el comentario "Autenticacion basica de N8N". Verificacion: `rg -n "N8N_BASIC_AUTH" docker-compose.yml` no devuelve coincidencias.
- [x] 1.2 Eliminar las mismas tres variables del servicio `n8n-corpus` en `docker-compose.yml`. Verificacion: el mismo `rg` sobre el archivo no devuelve coincidencias en ninguna seccion.
- [x] 1.3 Eliminar `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` (y su comentario) de `.env.example`. Verificacion: `rg -n "N8N_BASIC_AUTH" .env.example` sin coincidencias.
- [x] 1.4 Validar que el compose sigue siendo correcto. Verificacion: `docker compose config -q` termina con exit code cero.

## 2. Documentacion alineada con el acceso real

- [x] 2.1 Reescribir `README.md:291` para indicar que el acceso es la cuenta owner creada en el primer arranque (volumen `n8n_data`), sin usuario/password hardcodeados. Verificacion: la linea no menciona `admin`, `n8n_local_dev` ni `N8N_BASIC_AUTH_*`.
- [x] 2.2 Reescribir `docs/operational-guide.md:244` con el mismo mensaje. Verificacion: no quedan credenciales ni variables de basic auth en el paso.
- [x] 2.3 Reescribir `docs/n8n-workflow-guide.md:472` con el mismo mensaje. Verificacion: idem.
- [x] 2.4 Corregir `docs/por_implementar.md:86`, que ademas usaba la clave inconsistente `admin`. Verificacion: la linea no afirma un login usuario/clave inexistente.
- [x] 2.5 Actualizar `docs/security-hardening.md:191` agregando una nota de que `N8N_BASIC_AUTH_PASSWORD` se removio por vestigial (c-98), preservando el registro historico del commit `597c03e`. Verificacion: el texto historico se conserva y la nota aclara la remocion.
- [x] 2.6 Verificacion de conjunto: `rg -n "N8N_BASIC_AUTH|n8n_local_dev" README.md docs/` no devuelve referencias que afirmen un login vigente (solo se admite el registro historico de `security-hardening.md`).

## 3. Paso de operador (no versionado)

- [x] 3.1 Remover `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` del `.env` de la raiz (gitignorado). Verificacion: `rg -n "N8N_BASIC_AUTH" .env` sin coincidencias.

## 4. Verificacion final e integracion

- [x] 4.1 Confirmar que ningun archivo versionado referencia las variables. Verificacion: `rg -n "N8N_BASIC_AUTH" --hidden -g '!.git' -g '!openspec/changes/archive/**'` solo devuelve artefactos de este change y el registro historico justificado.
- [x] 4.2 Verificar que el stack sigue operativo tras la remocion (las variables eran inertes). Verificacion: `docker compose up -d` levanta el stack y `docker compose ps` muestra los servicios sanos.
- [x] 4.3 Validar la especificacion del change. Verificacion: `openspec validate c-98-limpiar-basic-auth-n8n-vestigial --strict` pasa.
