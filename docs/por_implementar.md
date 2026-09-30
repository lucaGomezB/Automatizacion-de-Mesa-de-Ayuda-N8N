# Por Implementar

> Estado: 2026-09-17.
> El estado de changes y el conteo de tests NO se hardcodean aqui: consultar
> `openspec list` y `openspec/changes/archive/` como fuente de verdad de los changes
> vigentes, y `.github/workflows/ci.yml` (o el ultimo run de CI) para el conteo de tests.
> Este documento lista lo que falta para que el sistema funcione al 100% en un entorno real.
> Las credenciales externas son inherentemente no automatizables; se documentan aqui para referencia del operador.

---

## 1. Credenciales Externas (no estan en el repo, por diseno)

### 1.1 Gemini API Key

- **Variable**: `GEMINI_API_KEY` en `App/Backend/.env`
- **Origen**: https://aistudio.google.com/app/apikey
- **Impacto si falta**: El clasificador hibrido no puede invocar a Gemini 2.5 Flash. Solo funciona el clasificador deterministico por keywords. Los incidentes con confianza < 0.90 quedan sin clasificar o van directo a revision humana.
- **Governance**: ALTO (dependencia externa paga)

### 1.2 JWT Secret Key

- **Variable**: `JWT_SECRET_KEY` en `App/Backend/.env`
- **Como generar**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Impacto si falta**: Ningun endpoint protegido funciona. Login devuelve 500. Frontend no puede autenticar usuarios.
- **Governance**: ALTO (seguridad)

### 1.3 Fernet Encryption Key

- **Variable**: `PSEUDONYMIZATION_ENCRYPTION_KEY` en `App/Backend/.env`
- **Como generar**: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- **Impacto si falta**: `POST /api/v1/incidentes` falla al intentar cifrar `descripcion_original` at-rest. El campo pseudonimizado se persiste pero el original no.
- **Governance**: ALTO (Ley 25.326 — datos personales)
- **Advertencia**: Perder esta clave hace permanentemente ilegible la columna `descripcion_original`.

### 1.4 Credenciales Microsoft Outlook (Canal Correo)

- **Donde**: N8N UI > nodo "Llega un email a Mesa de Ayuda" (Microsoft Outlook Trigger)
- **Tipo**: OAuth2 con tenant Microsoft 365 corporativo
- **Impacto si falta**: El canal de correo no funciona. Los usuarios no pueden reportar incidentes por email.
- **Governance**: ALTO (dependencia organizacional)
- **Nota**: El nodo es `microsoftOutlookTrigger`, no IMAP. La organizacion debe proveer credenciales OAuth2.

### 1.5 Credenciales Twilio (Canal Telefonico)

- **Variables en `App/Backend/.env`**:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_PHONE_NUMBER`
- **Donde en N8N**: nodo "Llamada telefonica" (Twilio Trigger)
- **Impacto si falta**: El canal telefonico no funciona. Sin numero Twilio no hay llamadas entrantes que transcribir.
- **Governance**: ALTO (dependencia externa paga)

### 1.6 URL Publica para Webhooks Twilio

- **Donde**: N8N UI > configuracion del Twilio Trigger
- **Requisito**: URL accesible desde internet. En desarrollo: ngrok o similar. En produccion: dominio con TLS.
- **Impacto si falta**: Twilio no puede notificar transcripciones a N8N. El webhook no recibe eventos.
- **Governance**: MEDIO (depende de entorno)

---

## 2. Pasos Manuales No Automatizados

### 2.1 Crear archivo .env

```bash
cp App/Backend/.env.example App/Backend/.env
# Editar y completar las 8 variables obligatorias
```

### 2.2 Generar Certificados TLS

```bash
bash openssl/generate-certs.sh
# O en Windows PowerShell:
# .\openssl\generate-certs.ps1
```

Los certificados self-signed generados funcionan en desarrollo pero el navegador muestra advertencia. Para produccion se necesita un certificado de CA real (Let's Encrypt o corporativa).

### 2.3 Importar Workflow a N8N

El archivo `n8n/workflow.json` esta montado en el contenedor como `/data/Automatizacion_Mesa_de_Ayuda.json` pero **no se auto-importa**. Pasos manuales:

1. Abrir `https://localhost:5678` (usuario: `admin`, clave: `admin`)
2. Settings > Import from File > seleccionar el JSON
3. Configurar credenciales de Outlook y Twilio en los nodos correspondientes
4. Activar el workflow (toggle Active)

### 2.4 Configuracion Redis Chat Memory

El AI Agent del canal telefonico usa Redis para memoria de sesion. Verificar en N8N UI que el nodo "Con el fin de enviar los datos que parsee la IA como JSON, se guardaran en memoria por un momento" este correctamente conectado al servicio `redis:6379`.

---

## 3. Funcionalidad Incompleta o Parcial

> **IN-04 e IN-05 fueron resueltos por C-18 (alineacion tecnologica de la tesis) y el diseno existente:**
> - IN-04: Fernet (`utils/encryption.py`) ya provee AES-128-CBC con HMAC-SHA-256 integrado para `descripcion_original`. C-18 reescribio la seccion 11.4 de la tesis reemplazando "pgcrypto" por "Fernet a nivel de aplicacion".
> - IN-05: La politica de retencion fue redefinida en C-18 como **conservacion indefinida** -- los incidentes cerrados se preservan permanentemente como registro auditable. La pseudonimizacion y el cifrado Fernet garantizan la proteccion incluso en periodos prolongados. No se requiere purga automatica.

### 3.1 Notificaciones por Correo (Dependencia Outlook)

El workflow N8N tiene el nodo "Correo de confirmacion al usuario" que envia confirmacion via Microsoft Outlook. Si las credenciales Outlook no estan configuradas, este nodo falla. El sistema sigue funcionando (el incidente se registra) pero el usuario no recibe confirmacion por correo.

---

## 4. Limitaciones y Deuda Tecnica

### 4.1 N8N — imagen pinneada (Resuelto por C-34)

Resuelto: `docker-compose.yml` fija `image: n8nio/n8n:2.11.2` (la version validada localmente, 2.11.2). Ya no se usa `latest`, por lo que no hay cambios silenciosos de version ni riesgo de romper los nodos del workflow (`@n8n/n8n-nodes-langchain`) sin rollback.

### 4.2 Frontend usa Vite Dev Server en Docker

El compose mapea el frontend como Vite dev server con HMR (hot module replacement). En produccion real deberia usarse el build estatico servido por nginx. El `Dockerfile` multi-stage de `App/Frontend/` ya esta preparado para build de produccion, pero el compose actual no lo usa.

### 4.3 Divergencias Documentadas Tesis vs Codigo

| ID | Tema | Tesis dice | Codigo hace |
|----|------|------------|-------------|
| IN-01 | Endpoint clasificacion | `POST /api/v1/clasificar` separado | Clasificacion embebida en `POST /api/v1/incidentes` |
| IN-03 | Driver BD | psycopg2-binary | asyncpg + SQLAlchemy async |
| IN-06 | Nodos workflow | 12 nodos | 16 nodos operativos + 3 sticky notes |

Estas divergencias ya estan documentadas en `knowledge-base/10_preguntas_abiertas.md`. La decision para IN-01 es definitiva: NO se agrega endpoint `/clasificar` separado. La tesis debe corregirse en revision futura.

### 4.4 Sin Job de Backup Automatico

Los scripts `scripts/backup.sh` y `scripts/backup.ps1` existen pero requieren ejecucion manual. No hay cron, systemd timer, ni scheduler N8N que los dispare automaticamente.

**Recomendacion**: Agregar un cron job en el host o un workflow N8N dedicado que ejecute el backup diariamente.

### 4.5 Calidad de la transcripcion STT del canal telefonico (mejora futura)

El canal telefonico transcribe la grabacion con Gemini (`GEMINI_STT_MODEL`, default `gemini-3.5-transcribe`), modo verbatim, `language_codes=["es-419"]` (`es-AR` no esta soportado), sobre audio de Twilio a **8 kHz mono** (techo de la red telefonica). Verificado en llamadas reales (2026-09-30): la calidad es variable; aparecen errores como "le pie" por "lo pisé". No es un fallo del pipeline — el transcript se genera, la pseudonimizacion opera y el incidente se crea — sino una limitacion de calidad del reconocimiento sobre audio telefonico mas acento rioplatense.

**Estado**: mejora futura, **no bloqueante**. Registrada tambien como riesgo vivo en `docs/runbook-verificacion-telefonia-c52.md` §7.2.

Palancas a evaluar (de menor a mayor esfuerzo):

1. **Medir**: banco de ~10 frases tipicas con su texto esperado y calcular WER por modelo. Hoy **no existe metrica de calidad de STT**.
2. **Config sin codigo**: `GEMINI_STT_MODEL` y los `language_codes` se ajustan por `.env`; permite A/B de modelos sin tocar codigo.
3. **Audio**: agregar `trim="trim-silence"` al `<Record>` en `App/Backend/app/cost_guard/twiml.py` (recorta silencio inicial/final y reduce ruido).
4. **Motor STT dedicado** (Google Cloud Speech-to-Text v2, Deepgram, Whisper): mayor salto esperado; requiere un change propio (nuevo proveedor, costo y dependencia).
5. **Post-correccion controlada** del texto, con guarda anti-alucinacion y conservando el transcript crudo. Nota: hoy el AI Agent de n8n ya reescribe/normaliza la descripcion (sin guarda explicita).

**Impacto**: calidad del texto que ve el operador. NO afecta la creacion del incidente ni la frontera de PII (la pseudonimizacion es posterior a la transcripcion).

---

## 5. Resumen de Prioridades

| Prioridad | Item | Tipo | Bloquea |
|-----------|------|------|---------|
| **Critica** | Gemini API Key | Credencial | Clasificacion hibrida |
| **Critica** | JWT Secret Key | Credencial | Autenticacion |
| **Critica** | Fernet Encryption Key | Credencial | Cifrado at-rest |
| **Alta** | Credenciales Outlook | Credencial | Canal correo |
| **Alta** | Credenciales Twilio | Credencial | Canal telefonico |
| **Media** | URL publica Twilio | Config | Webhook telefonico |
| **Media** | Backup automatico | Feature | Operacion prolongada |
| — | Pinear version N8N | **Resuelto (C-34)** | — |
| **Baja** | Build produccion frontend | Deuda tecnica | Rendimiento en prod |
| **Baja** | Calidad de transcripcion STT (canal telefonia) | Mejora futura | — |