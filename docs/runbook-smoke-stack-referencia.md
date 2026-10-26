# Runbook — Prueba de humo del despliegue de referencia

Guía operativa para ejecutar, sobre el **despliegue de referencia** de la release,
la prueba de humo de extremo a extremo (canal web) y la verificación del borde
TLS, y para conservar la evidencia de la corrida.

- Change: `openspec/changes/c-140-endurecimiento-tecnico-tls-reintentos-e2e/`
- Arnés: `scripts/dry_run/` (ver `docs/dry-run-harness.md`)
- Despliegue de referencia: `docker-compose.yml` + `nginx/nginx.conf` levantados en
  limpio con certificados autofirmados efímeros.
- Proyecto Compose fijo: `mesa_local` (no usar `-p` ni nombres alternativos).

> El despliegue de referencia **no** es la instancia operativa: la reimportación
> del workflow en la instancia operativa es un paso del equipo (CP5) y queda
> fuera de este runbook.

---

## A. Prerrequisitos

| Herramienta / recurso | Verificación |
|-----------------------|--------------|
| Docker Engine + Docker Compose v2 | `docker compose version` |
| Python 3.12 (biblioteca estándar) | `python3 --version` |
| `openssl` disponible | `openssl version` |
| `App/Backend/.env` creado desde la plantilla | `ls App/Backend/.env` |
| `.env` de la raíz con las credenciales del stack | `ls .env` (gitignorado) |
| Puertos 80 y 443 libres en el host | `ss -ltn '( sport = :80 or sport = :443 )'` |

Los puertos 80/443 deben estar libres: el borde Nginx es el **único** servicio
publicado fuera de loopback, de modo que una corrida no puede convivir con otro
stack en los mismos puertos. PostgreSQL (5433) y N8N (5678) quedan en loopback.

---

## B. Corrida local del recorrido E2E (canal web)

1. Generar los certificados efímeros (idempotente; sobrescribe los previos):

   ```bash
   bash openssl/generate-certs.sh
   ```

2. Ejecutar el arnés. Escribe el reporte de evidencia **fuera** del repositorio:

   ```bash
   python3 scripts/dry_run/dry_run.py \
     --json-out /tmp/smoke-local.json \
     --with-retry-fault        # si el bloque de reintentos está aplicado
   ```

   El flag `--with-retry-fault` agrega `e2e:reintento`: desconecta el backend de la
   red `mesa_local_automation`, envía el webhook en segundo plano, reconecta a los
   ~2 s (con los alias `backend` y del contenedor) y exige un incidente con una
   sola fila. El bloque `finally` reconecta siempre, aun ante error.

3. Leer el resultado: el resumen en consola debe terminar en
   `RESULT: 16/16 checks passed. Harness GREEN.` (15/15 sin `--with-retry-fault`)
   y el exit code debe ser `0`. Cualquier `FAIL`/`PENDING` deja el exit code
   distinto de cero.

### B.1 Guardarraíl de costo (verificación)

Antes de enviar nada el arnés afirma las **dos capas** de costo cero:
`guardrail:gemini-key` (clave ficticia) y `guardrail:cost-guard-budget`
(presupuesto efectivo cero). Además, tras la corrida se puede confirmar que no
hubo llamada paga:

```bash
docker compose logs backend | grep -iE "gemini|escalad"
```

No deben aparecer eventos de llamada al proveedor; sí es esperable
`classifier_short_circuit` (etapa determinística) e `incidente_classified`.

---

## C. Lectura del reporte de evidencia

El archivo JSON de `--json-out` contiene:

- `commit` (hash verificado), `timestamp_utc`, `n8n_version`;
- `groups` y `summary` (checks ejecutados y verde/rojo);
- `checks[]` con `name`, `status`, `detail` y `action`.

El reporte no contiene la contraseña del operador, el token de acceso, claves de
API ni material criptográfico. Guardarlo (o copiarlo a un registro versionado)
como evidencia de la corrida sobre el commit indicado.

---

## D. Registro de evidencia y desmontaje

1. Registrar commit, fecha UTC, grupos y resultados en el documento de
   correcciones de la tesis (`docs/Tesis/Correcciones/dictamen-correcciones.md`).
2. Desmontar el stack cuando la corrida terminó (los volúmenes persisten):

   ```bash
   docker compose -f docker-compose.yml -f scripts/dry_run/compose.dry-run.yml down
   ```

   Usar `down` (sin `-v`) para no borrar los volúmenes del stack. Para una
   limpieza total de una corrida efímera, `down -v` es destructivo: no usarlo
   contra una base de datos cuyo contenido importe.

---

## E. Ejecución en CI

Las pruebas **offline** del arnés (`python -m pytest scripts/dry_run -q`) se
suman al job `backend-tests` y no requieren Docker, red ni secretos. La corrida
completa con Docker es **local** en esta release (OQ2 = local); el workflow de
CI de humo queda diferido. Ver `docs/dry-run-harness.md` §11.

---

## F. Verificación del borde TLS

Se ejecuta con el flag `--with-tls` sobre el despliegue de referencia levantado con
certificados autofirmados efímeros. Requiere que `openssl/mesa.crt` exista (paso B.1).

```bash
python3 scripts/dry_run/dry_run.py \
  --with-tls \
  --json-out /tmp/smoke-tls.json
```

El grupo `tls:*` verifica, en ejecución:

| Check | Qué verifica |
|-------|--------------|
| `tls:exposure` | `docker compose config`: el único servicio publicado fuera de loopback es nginx (80/443). |
| `tls:handshake-1.3` | Handshake TLS 1.3 con SNI `localhost`. |
| `tls:handshake-1.2` | Handshake limitado a TLS 1.2. |
| `tls:identity` | El certificado presentado coincide con `openssl/mesa.crt` (ancla de confianza o huella SHA-256). |
| `tls:redirect` | `GET http://localhost/api/v1/health?origen=smoke` responde 301 preservando ruta y query, sin HSTS. |
| `tls:headers` | HSTS exacto (`max-age=31536000; includeSubDomains`) y cabeceras de seguridad presentes. |
| `tls:server-header` | La cabecera `Server` no expone número de versión. |
| `tls:unknown-host` | Un Host desconocido cierra la conexión sin respuesta (catch-all 444). |
| `tls:reject-1.1` | El handshake TLS 1.1 es rechazado; queda PENDING si el cliente local no puede ofrecerlo. |

La verificación **nunca** desactiva la comprobación de identidad ni se apoya en
`CERT_NONE`: el ancla es el certificado generado para la corrida o, si la
plataforma rechaza un autofirmado como ancla, la huella SHA-256.

### F.1 Sobre el certificado de referencia

El certificado del despliegue de referencia es **autofirmado** y se genera con
`bash openssl/generate-certs.sh` (RSA 2048, SHA-256, 365 días, SAN `localhost`,
`mesa.local`, `127.0.0.1`). **En producción el adoptante debe emitir un
certificado de una CA**; la referencia no sustituye ese paso. Los certificados y
claves generados están excluidos de Git (`openssl/*.crt`, `openssl/*.key`).

### F.2 Puertos y solución de problemas

- El borde publica 80 (redirección) y 443 (TLS) en todas las interfaces; el resto
  del stack queda en loopback. Los puertos 80/443 deben estar libres.
- `tls:identity` FAIL: el certificado servido no es el de la corrida; regenerar
  con `bash openssl/generate-certs.sh` y reiniciar nginx (`docker compose restart nginx`).
- `tls:reject-1.1` PENDING: la plataforma local no puede ofrecer TLS 1.1; no
  cuenta como éxito y la verificación termina con exit code distinto de cero.
- Un `tls:*` FAIL que revele un defecto de `nginx/nginx.conf` o del compose se
  detiene y se propone la corrección (gobernanza HIGH; requiere CP1).

---

## G. Solución de problemas

| Síntoma | Causa probable | Acción |
|---------|----------------|--------|
| `stack:up` FAIL (`dependency failed to start`) | El backend no conecta a PostgreSQL (password del `.env` raíz ausente o distinta del volumen). | Definir `POSTGRES_PASSWORD` en el `.env` raíz con el valor del volumen, o recrear el volumen. |
| `e2e:reintento` FAIL con `EAI_AGAIN` | El backend volvió a la red sin el alias `backend`. | Reconectar con `docker network connect --alias backend mesa_local_automation mesa_local-backend-1`; el arnés ya lo hace. |
| `tls:*` FAIL de identidad | El certificado servido no es el generado para la corrida. | Regenerar con `bash openssl/generate-certs.sh` y reiniciar nginx. |
| Puerto 80/443 ocupado | Otro stack en el mismo host. | Detener el otro stack; el borde de la referencia debe ser el único en 80/443. |
