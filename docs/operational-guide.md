# Guía Operativa — Anexo G

Sistema de Automatización de Mesa de Ayuda — UTN 2026

> Para la guía de resolución de problemas, ver [`troubleshooting.md`](troubleshooting.md).
>
> Para el arnés de validación local de costo cero (dry-run), ver
> [`dry-run-harness.md`](dry-run-harness.md).

---

## Prerequisitos

| Herramienta     | Version minima | Verificacion |
|-----------------|---------------|--------------|
| Docker Engine   | 24.x          | `docker --version` |
| Docker Compose  | v2 (plugin)   | `docker compose version` |
| Git             | 2.x           | `git --version` |
| OpenSSL         | 1.1.x+        | `openssl version` |

**Recursos de hardware recomendados**: 4 GB RAM libres, 5 GB de espacio en disco.

---

## 1. Despliegue

### 1.1 Clonar el repositorio

```bash
git clone https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N.git
cd Automatizacion-de-Mesa-de-Ayuda-N8N
```

Activar el hook anti-secretos (obligatorio, una sola vez):

```bash
git config core.hooksPath .githooks
```

### 1.2 Configurar variables de entorno

```bash
cp App/Backend/.env.example App/Backend/.env
```

Editar `App/Backend/.env` y completar los valores reales:

```dotenv
# Base de datos (se usa en el contenedor; no cambiar el host cuando se usa compose)
# Debe coincidir con POSTGRES_USER/POSTGRES_PASSWORD del compose (default local:
# mesa / mesa_local_dev). Si sobreescribis POSTGRES_PASSWORD en el .env raiz,
# reflejalo aca.
DATABASE_URL=postgresql+asyncpg://mesa:mesa_local_dev@postgres:5432/mesa_de_ayuda

# API Key de Google Gemini (obtener en https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=<tu-clave-real>

# Clave Fernet para cifrado at-rest de descripciones (base64url de 32 bytes)
# Generar con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
PSEUDONYMIZATION_ENCRYPTION_KEY=<clave-generada>

# Clave de firma HS256 de los tokens JWT
# Generar con: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=<clave-generada>
```

> **Importante**: nunca commitear el archivo `.env` con credenciales reales.
> El hook pre-commit bloquea commits que contengan claves.

### 1.3 Generar certificados TLS y levantar los servicios

#### Camino recomendado: un solo comando

El comando unico de arranque es el camino recomendado. Verifica el entorno,
genera los certificados TLS auto-firmados si faltan, levanta el stack con
`docker compose up -d --build`, espera a que los servicios queden sanos y valida
los endpoints de salud por HTTPS.

**Linux / macOS:**
```bash
bash scripts/up.sh
# Alternativa equivalente si make esta instalado:
make up
```

**Windows (PowerShell):**
```powershell
.\scripts\up.ps1
# Alternativa equivalente si make esta instalado:
make up
```

Antes de tocar Docker, el comando unico ejecuta el preflight de costo
(`scripts/preflight/cost_readiness.py`). Si el preflight falla, el arranque se
bloquea y no se levanta ningun servicio. El bypass explicito es
`UP_SKIP_COST_PREFLIGHT=1`; al usarlo el arranque continua, pero imprime una
advertencia audible. Es una excepcion deliberada para escenarios controlados, no
el camino normal.

#### Camino manual (alternativa)

Si se prefiere controlar cada paso, generar primero los certificados auto-firmados
para el proxy Nginx (validez: 365 dias):

```bash
# Linux / macOS
bash openssl/generate-certs.sh

# Windows (PowerShell)
.\openssl\generate-certs.ps1
```

Esto crea `openssl/mesa.crt` (certificado) y `openssl/mesa.key` (clave privada).

> **Nota**: si los certificados expiran (365 dias), volver a ejecutar el script
> para regenerarlos. El script es idempotente: sobreescribe los archivos existentes
> sin errores. Luego reiniciar el proxy: `docker compose restart nginx`.

Luego levantar el stack:

```bash
docker compose up -d
```

Este comando construye la imagen del backend (desde `App/Backend/Dockerfile`),
descarga las imagenes de PostgreSQL, Redis, Nginx y N8N, aplica las migraciones
Alembic (`alembic upgrade head`) y levanta todos los servicios en background.
A diferencia del comando unico, este camino no ejecuta el preflight de entorno ni
el de costo: la verificacion queda a cargo de quien lo ejecuta.

**Verificar que todos los contenedores estan healthy**:

```bash
docker compose ps
```

Salida esperada (todos en estado `healthy` o `running`):

```
NAME                    STATUS          PORTS
...-postgres-1          Up (healthy)    0.0.0.0:5433->5432/tcp
...-redis-1             Up (healthy)    0.0.0.0:6379->6379/tcp
...-backend-1           Up (healthy)    
...-n8n-1               Up              0.0.0.0:5678->5678/tcp
...-frontend-1          Up              
...-nginx-1             Up              0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

> **Nota**: el backend (puerto 8000) y el frontend (puerto 3000) ya NO se publican
> en el host. Todo el trafico HTTP/HTTPS externo pasa a traves del proxy Nginx en
> los puertos 80 (HTTP, redirige a HTTPS) y 443 (HTTPS con TLS 1.3).

### 1.4 Verificar salud del backend

```bash
curl -k https://localhost/api/v1/health
```

Respuesta esperada:
```json
{"status": "ok", "version": "1.0.0"}
```

Verificar conectividad con la base de datos:
```bash
curl -k https://localhost/api/v1/health/db
```

Respuesta esperada:
```json
{"status": "ok", "database": "reachable"}
```

> **Nota**: el flag `-k` (o `--insecure`) es necesario porque se usa un certificado
> auto-firmado en desarrollo. En produccion, con un certificado de CA reconocida
> (p. ej. Let's Encrypt), este flag no es necesario.

### 1.5 Acceder a N8N e importar el workflow

1. Abrir `http://localhost:5678` en el navegador.
2. Autenticarse con usuario `admin` / contraseña `admin`.
3. Importar el workflow: **Workflows → Import from file** → seleccionar
   `n8n/workflow.json` (ya montado en `/data/` del contenedor).
4. Configurar las credenciales de Outlook, Twilio y Gemini en N8N.
5. Activar el workflow (boton toggle en la esquina superior derecha).

> **Nota**: N8N mantiene su acceso directo en el puerto 5678 (HTTP) por
> limitaciones tecnicas con path-prefix en el proxy inverso. El backend
> se comunica con N8N internamente via `http://n8n:5678/webhook`.

**Retencion de datos de ejecucion**: N8N esta configurado para eliminar
automaticamente los datos de ejecucion con una antiguedad mayor a 30 dias
(720 horas), mediante las variables de entorno `EXECUTIONS_DATA_PRUNE=true`
y `EXECUTIONS_DATA_MAX_AGE=720` en `docker-compose.yml`. Esta configuracion
cumple con la politica de retencion documentada en la tesis §5.3. No se requiere
ningun script externo ni tarea cron adicional para mantener esta politica.

### 1.6 Frontend

El frontend React se levanta como parte del compose y se accede a traves
del proxy Nginx en `https://localhost/`. El puerto 3000 no esta publicado
en el host; todo el trafico de la SPA pasa por HTTPS.

Para desarrollo con hot reload (fuera del compose):

```bash
cd App/Frontend
npm install
npm run dev
```

La aplicacion estara disponible en `http://localhost:3000` (acceso directo,
sin TLS, util solo para desarrollo de la UI).

---

## 2. Detener y reiniciar los servicios

```bash
# Detener todos los servicios (los volúmenes persisten)
docker compose down

# Detener y borrar todos los volúmenes (base de datos limpia)
docker compose down -v

# Reiniciar un servicio específico
docker compose restart backend

# Ver logs en tiempo real
docker compose logs -f backend
docker compose logs -f n8n
```

---

## 3. Backup y restauración de PostgreSQL

### 3.1 Backup automatizado (recomendado)

El proyecto incluye scripts de backup automatizados que ejecutan `pg_dump` desde
el contenedor Docker, crean un dump SQL con marca de fecha y rotan los backups
manteniendo los ultimos 7 dias.

**Linux / macOS:**

```bash
bash scripts/backup.sh
```

**Windows (PowerShell):**

```powershell
.\scripts\backup.ps1
```

Ambos scripts son idempotentes:
- Crean el directorio `backups/` si no existe.
- Generan un archivo `backups/backup_YYYY-MM-DD.sql`.
- Conservan los 7 backups mas recientes y eliminan los mas antiguos.
- Emiten un mensaje de error claro si el contenedor PostgreSQL no esta corriendo.

#### Programacion automatica diaria

**Linux / macOS (cron):**

Agregar al crontab (reemplazar `/ruta/al/repo` con la ruta real):

```cron
0 3 * * * cd /ruta/al/repo && bash scripts/backup.sh >> /var/log/mesa_backup.log 2>&1
```

**Windows (Task Scheduler):**

Crear una tarea programada que ejecute diariamente:

```
Program: powershell.exe
Arguments: -ExecutionPolicy Bypass -File "C:\ruta\al\repo\scripts\backup.ps1"
```

### 3.2 Backup manual (alternativa)

```bash
# Crear un dump completo de la base de datos
docker compose exec postgres pg_dump -U mesa mesa_de_ayuda > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3.2 Restauración

```bash
# 1. Asegurarse de que el servicio postgres está corriendo
docker compose up -d postgres

# 2. Restaurar desde el dump
docker compose exec -T postgres psql -U mesa mesa_de_ayuda < backup_20260101_030000.sql
```

> **Precaución**: la restauración sobreescribe los datos existentes. Crear un
> backup previo antes de restaurar en un entorno con datos.

### 3.3 Backup del volumen Docker (alternativa)

```bash
# Exportar el volumen completo a un tar
docker run --rm \
  -v automatizacion-de-mesa-de-ayuda-n8n_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_volume_$(date +%Y%m%d).tar.gz -C /data .

# Restaurar el volumen desde el tar
docker run --rm \
  -v automatizacion-de-mesa-de-ayuda-n8n_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_volume_20260101.tar.gz -C /data
```

> **Nota**: verificar el nombre real del volumen con `docker volume ls | grep postgres`.

---

## 4. Monitoreo de salud

### 4.1 Endpoints de salud del backend

| Endpoint            | Descripción                                  | Salida esperada |
|---------------------|----------------------------------------------|-----------------|
| `GET /health`       | Liveness probe: ¿el proceso está corriendo?  | `{"status":"ok"}` |
| `GET /health/db`    | Readiness probe: ¿PostgreSQL es alcanzable?  | `{"status":"ok","database":"reachable"}` |

```bash
# Verificacion rapida
curl -k -s https://localhost/api/v1/health | python -m json.tool
curl -k -s https://localhost/api/v1/health/db | python -m json.tool
```

### 4.2 Estado de los contenedores

```bash
# Estado detallado de todos los servicios
docker compose ps

# Uso de recursos en tiempo real
docker stats
```

### 4.3 Logs estructurados

El backend emite logs estructurados (structlog) en formato JSON:

```bash
# Seguir logs del backend filtrando errores
docker compose logs -f backend 2>&1 | grep '"level":"error"'

# Ver todos los logs desde el último reinicio
docker compose logs --since 1h backend
```

### 4.4 Cola de revisión humana

Verificar si hay clasificaciones pendientes de revisión:

```bash
curl -k -s https://localhost/api/v1/clasificaciones/revision-pendiente | python -m json.tool
```

Un número alto de revisiones pendientes indica baja confianza sistemática del
clasificador (posible degradación del modelo o cambio de distribución de incidentes).

---

## 5. Regenerar la especificación OpenAPI

Si se agregan o modifican rutas en el backend, regenerar `docs/openapi.json`:

```bash
cd App/Backend
python scripts/export_openapi.py
```

El test de sincronía fallará en CI hasta que el archivo regenerado se commitee.

---

## 6. Actualizar dependencias del backend

```bash
# Editar App/Backend/requirements.txt con las nuevas versiones
# Reconstruir la imagen
docker compose build backend
docker compose up -d backend
```

---

## 7. Aplicar migraciones Alembic manualmente

Las migraciones se aplican automáticamente al iniciar el contenedor (`alembic upgrade head`).
Para aplicarlas manualmente (p. ej. en una base de datos existente sin reiniciar):

```bash
docker compose exec backend alembic upgrade head
```

Para ver el historial de migraciones:

```bash
docker compose exec backend alembic history
docker compose exec backend alembic current
```

---

## 8. Evaluacion del clasificador

El framework de evaluacion (`evaluation/`) permite medir el desempeno del
clasificador hibrido sobre el corpus real de evaluacion.

### 8.1 Ejecutar evaluacion

```bash
# Desde la raiz del repositorio:
PYTHONPATH=App/Backend python -m evaluation.run_evaluation
```

Esto carga el corpus, ejecuta el clasificador (o FakeClassifier en entornos
de test) y genera un reporte en `evaluation/report.md` con:
- Exactitud global y F1 macro
- Matriz de confusion
- Metricas por clase (precision, sensibilidad, F1)

### 8.2 Gate de corrida paga

Una corrida que invocaria el clasificador real (Gemini) exige confirmacion
explicita del operador: el runner se niega a invocarlo sin ella.

```bash
# Confirmacion por flag:
PYTHONPATH=App/Backend python -m evaluation.run_evaluation --confirm-paid

# Confirmacion por variable de entorno:
EVALUATION_CONFIRM_PAID=1 PYTHONPATH=App/Backend python -m evaluation.run_evaluation
```

Sin confirmacion, la corrida aborta con codigo de salida 2 y un mensaje claro,
sin invocar el clasificador real. Al confirmar, el runner imprime una estimacion
orientativa del costo antes de ejecutar (no es una factura).

### 8.3 Ejecutar tests de evaluacion

```bash
cd evaluation
pytest tests/ -v
```

### 8.4 Preparar el corpus real

El corpus de evaluacion (`data/corpus_evaluacion_pseudonimizado.json`) no esta
trackeado en git por privacidad. El procedimiento para construir y colocar el
corpus real esta documentado en `docs/como_cargar_datos_corpus.md`.

---

## 9. Arnés de ejecución en seco (dry-run)

Antes de configurar credenciales pagas (Gemini, Twilio), validar localmente y sin
costo el tramo compartido de registro de incidentes con:

```bash
make dry-run
# o
python3 scripts/dry_run/dry_run.py
```

El arnés levanta o reutiliza el stack `mesa_local` con una `GEMINI_API_KEY`
ficticia, importa/activa el workflow de N8N, ejecuta un preflight de contratos y
recorre el canal web end-to-end verificando la persistencia con
`canal_origen_id == 2`. No invoca servicios pagos y falla ruidosamente con un
mensaje accionable ante cualquier quiebre de cableado.

- Guía completa (prerrequisitos, guardarraíles de costo, checks, canal correo
  opcional y procedimiento telefónico manual de pago):
  [`dry-run-harness.md`](dry-run-harness.md).

---

## 10. Medición de latencia end-to-end

El sistema instrumenta la latencia END-TO-END por incidente (ingreso del mensaje
al sistema → persistencia confirmada) para alimentar `tiempo_automatizado_s` del
corpus. El contrato completo —definiciones, unidades, validación, política de
latencia negativa, caveats por canal y exclusión de replays— vive en:

- [`medicion-latencia-e2e.md`](medicion-latencia-e2e.md).

Los instantes se exponen en la representación de lectura del incidente
(`ingresado_en`, `persistido_en`, `latencia_e2e_ms`, `latencia_anomala`). El
análisis debe reportarse **por canal**, porque los puntos de ingreso no son
homogéneos.

