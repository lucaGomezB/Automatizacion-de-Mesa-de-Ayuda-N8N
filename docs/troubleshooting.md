# Guía de Resolución de Problemas

Sistema de Automatización de Mesa de Ayuda — UTN 2026

Cada entrada sigue el formato: **Síntoma → Causa probable → Remediación**.

Para el procedimiento de despliegue y monitoreo, ver [`operational-guide.md`](operational-guide.md).

---

## 1. El backend no levanta

### 1.1 El contenedor `backend` queda en estado `unhealthy` o se reinicia repetidamente

**Síntoma**: `docker compose ps` muestra el servicio `backend` como `unhealthy` o
en bucle de reinicios.

**Causa probable A — Variables de entorno faltantes**:
El backend requiere `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`.
Si alguna falta, `Settings` (pydantic-settings) lanza un error al iniciar.

**Remediación**:
```bash
# Verificar que el .env existe y tiene las tres variables
cat Gestion_Incidentes/.env
# Si falta, copiar el ejemplo y completar
cp Gestion_Incidentes/.env.example Gestion_Incidentes/.env
# Editar el .env y luego reiniciar
docker compose up -d --force-recreate backend
```

**Causa probable B — PostgreSQL no está healthy todavía**:
El backend espera que `postgres` esté en estado `healthy` antes de arrancar.
En máquinas lentas, el healthcheck puede tardar más de lo esperado.

**Remediación**:
```bash
# Ver el estado real de postgres
docker compose ps postgres
# Ver los logs del healthcheck
docker compose logs postgres | tail -20
# Esperar y volver a intentar
docker compose restart backend
```

**Causa probable C — Error en la migración Alembic**:
El comando `alembic upgrade head` falla si hay inconsistencias en el esquema.

**Remediación**:
```bash
# Ver los logs completos del backend
docker compose logs backend | tail -50
# Si hay un error de migración, reiniciar con volumen limpio
docker compose down -v
docker compose up -d
```

---

## 2. Base de datos no disponible

### 2.1 El endpoint `/health/db` devuelve 500

**Sintoma**: `curl -k https://localhost/api/v1/health/db` retorna un error 500 o
`{"detail":"..."}`.

**Causa probable A — PostgreSQL no está corriendo**:

**Remediación**:
```bash
docker compose ps postgres
# Si está parado:
docker compose up -d postgres
# Verificar que quedó healthy:
docker compose ps postgres
```

**Causa probable B — Credenciales incorrectas en `DATABASE_URL`**:
El usuario o contraseña en `DATABASE_URL` no coincide con los valores de
`POSTGRES_USER` / `POSTGRES_PASSWORD` en el compose.

**Remediación**:
```bash
# Verificar el DATABASE_URL en .env
grep DATABASE_URL Gestion_Incidentes/.env
# Debe coincidir con: postgresql+asyncpg://mesa:mesa@postgres:5432/mesa_de_ayuda
# (cuando se usa desde dentro del compose; el host es 'postgres', no 'localhost')
```

**Causa probable C — Pool de conexiones agotado**:
En carga alta, el pool asyncpg puede agotarse.

**Remediación**:
```bash
# Reiniciar el backend (descarta las conexiones del pool)
docker compose restart backend
# Monitorear logs para ver errores de conexión
docker compose logs -f backend 2>&1 | grep '"event":"db'
```

---

## 3. Clasificaciones caen a revisión humana por baja confianza

### 3.1 Muchos incidentes con `requiere_revision_humana=true`

**Síntoma**: `GET /api/v1/clasificaciones/revision-pendiente` devuelve una lista
larga; los incidentes tienen `confianza < 0.70`.

**Causa probable A — Descripciones ambiguas o muy cortas**:
El clasificador necesita contexto suficiente para superar el umbral de 0.70.

**Remediación**:
- Revisar el canal N8N: verificar que el paso de validación exige una descripción
  mínima antes de enviar al backend.
- Si la descripción es adecuada, el operador debe validar manualmente y el sistema
  aprende del ground truth para mejoras futuras.

**Causa probable B — Temperatura de Gemini demasiado alta o prompt degradado**:
Un prompt mal formado o una temperatura ≥ 0.5 produce respuestas menos determinísticas.

**Remediación**:
- Verificar `docs/prompt_gemini.txt`: el prompt debe estar intacto y contener
  las instrucciones de formato JSON.
- Confirmar los parámetros en el servicio Gemini: `temperature=0.3`, `top_p=0.9`,
  `max_tokens=100`.

**Causa probable C — Deriva de distribución (concept drift)**:
Si la naturaleza de los incidentes cambió respecto del conjunto con que se diseñó
el prompt, el clasificador puede degradar.

**Remediación**:
- Revisar una muestra de los incidentes clasificados con baja confianza.
- Actualizar el prompt con nuevos ejemplos o ajustar las definiciones de categoría.

---

## 4. Fallo de la API de Google Gemini

### 4.1 El sistema clasifica todos los incidentes como `etapa=fallback`

**Síntoma**: los registros en `clasificacion_log` tienen `etapa="fallback"` y
`confianza=0.0`; `requiere_revision_humana=true` en todos los incidentes nuevos.

**Causa probable A — `GEMINI_API_KEY` inválida o expirada**:

**Remediación**:
```bash
# Verificar que la clave está bien configurada
grep GEMINI_API_KEY Gestion_Incidentes/.env
# Probar la clave directamente
python -c "
import os; os.environ['GEMINI_API_KEY'] = '<tu-clave>'
import google.generativeai as genai
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
print('Clave OK')
"
# Si es inválida: generar una nueva en https://aistudio.google.com/app/apikey
# Luego reiniciar el backend
docker compose restart backend
```

**Causa probable B — Timeout de Gemini (10 segundos)**:
Si la API de Google tarda más de 10 segundos en responder, el clasificador
registra un fallback automático.

**Remediación**:
- Verificar la conectividad del contenedor backend a la internet:
```bash
docker compose exec backend curl -I https://generativelanguage.googleapis.com
```
- Si hay un proxy corporativo, configurarlo en las variables de entorno del
  servicio `backend` en el compose.

**Causa probable C — Cuota de la API agotada**:

**Remediación**:
- Verificar el dashboard de Google AI Studio para el estado de la cuota.
- Mientras la cuota se restablece, el sistema opera en modo manual
  (todos los incidentes van a revisión humana).

---

## 5. N8N no recibe eventos o el workflow está inactivo

### 5.1 Los incidentes de correo o llamada no llegan al backend

**Síntoma**: no se crean incidentes nuevos aunque haya correos o llamadas entrantes.

**Causa probable A — Workflow inactivo**:
El workflow está en estado `inactive` (por defecto al importar).

**Remediación**:
1. Abrir `http://localhost:5678`.
2. Ir al workflow **Automatizacion_Mesa_de_Ayuda**.
3. Activarlo con el toggle de la esquina superior derecha.

**Causa probable B — Credenciales de Outlook o Twilio no configuradas**:

**Remediación**:
1. En N8N ir a **Settings → Credentials**.
2. Verificar que existen credenciales para Microsoft Outlook y Twilio.
3. Probar la conexión desde la pantalla de edición de cada credencial.

**Causa probable C — El backend no es alcanzable desde N8N**:
N8N llama al backend usando la URL `http://backend:8000` (servicio interno de Docker).
Si el servicio `backend` no está healthy, las peticiones fallan.

**Remediación**:
```bash
# Verificar que el backend está healthy
docker compose ps backend
# Probar la conectividad desde dentro del contenedor N8N
docker compose exec n8n wget -qO- http://backend:8000/health
```

---

## 6. Problemas con el Frontend (opcional)

### 6.1 El Frontend no levanta o no puede conectar al backend

**Síntoma**: `npm run dev` falla o las peticiones al backend dan CORS error.

**Causa probable — Variable de entorno de URL del backend no configurada**:

**Remediación**:
```bash
# En Frontend/, verificar si existe un .env.local con la URL del backend
cat Frontend/.env.local
# Si no existe, crearlo:
echo "VITE_API_BASE_URL=https://localhost/api/v1" > App/Frontend/.env.local
npm run dev
```

> **Nota**: el Frontend es opcional y no es parte del flujo principal de
> clasificación de incidentes (N8N → backend). Solo es necesario para la
> interfaz de revisión humana.

---

## 7. Referencia rápida de comandos de diagnóstico

```bash
# Estado general de todos los servicios
docker compose ps

# Logs en tiempo real del backend
docker compose logs -f backend

# Salud del backend (a traves del proxy Nginx)
curl -k https://localhost/api/v1/health
curl -k https://localhost/api/v1/health/db

# Cola de revision humana (cuantos incidentes esperan validacion)
curl -k https://localhost/api/v1/clasificaciones/revision-pendiente | python -m json.tool

# Conectividad de N8N al backend (desde dentro del contenedor)
docker compose exec n8n wget -qO- http://backend:8000/health

# Conexión directa a PostgreSQL
docker compose exec postgres psql -U mesa -d mesa_de_ayuda -c "SELECT COUNT(*) FROM incidente;"

# Ver el último error del clasificador
docker compose exec backend grep '"level":"error"' /proc/1/fd/1 2>/dev/null || \
  docker compose logs backend 2>&1 | grep '"level":"error"' | tail -5
```
