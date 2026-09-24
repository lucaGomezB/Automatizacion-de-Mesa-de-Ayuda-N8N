"""
Módulo de configuración centralizada de la aplicación.

Responsabilidad:
    Define y expone todos los parámetros de configuración del sistema a través
    de la clase Settings, basada en Pydantic-Settings. Los valores se leen
    desde variables de entorno o desde el archivo .env, garantizando que ningún
    valor sensible (claves API, credenciales de base de datos) quede embebido
    en el código fuente.

    La función get_settings() actúa como punto de acceso único a la
    configuración, utilizando caché LRU para garantizar que la instancia
    sea construida una sola vez durante el ciclo de vida de la aplicación.

Referencia técnica:
    Los parámetros de Gemini (temperatura, top_p, max_tokens, etc.) reproducen
    exactamente los valores documentados en docs/parameters_gemini.md y en el
    Anexo H de la tesis.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Contenedor tipado de variables de entorno para todo el sistema.

    Pydantic-Settings valida cada atributo al momento de construcción,
    lanzando una excepción descriptiva si falta algún campo requerido
    o si el tipo no coincide. Esto hace que los errores de configuración
    sean detectados al inicio y no en tiempo de ejecución.

    Los campos marcados con tipo sin valor por defecto (por ejemplo,
    database_url, gemini_api_key) son obligatorios y deben estar presentes
    en el entorno o en el archivo .env antes de arrancar la aplicación.
    """

    model_config = SettingsConfigDict(
        env_file=".env",           # Archivo de variables de entorno para desarrollo local
        env_file_encoding="utf-8",
        case_sensitive=False,      # Permite tanto DATABASE_URL como database_url
    )

    # ── Identificación de la aplicación ───────────────────────────────────────
    app_name: str = "Gestion de Incidentes API"
    app_version: str = "1.0.0"
    debug: bool = False            # En True, habilita /docs y /redoc de FastAPI
    environment: str = "production"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Lista de orígenes permitidos. En desarrollo se usa ["*"] para simplicidad.
    # En producción reemplazar por los dominios reales del frontend.
    # Ejemplo .env: CORS_ALLOW_ORIGINS=["https://mi-app.com","http://localhost:3000"]
    cors_allow_origins: list[str] = ["*"]

    # ── Base de datos PostgreSQL ───────────────────────────────────────────────
    # URL completa con driver asyncpg para operaciones no bloqueantes.
    # Ejemplo: postgresql+asyncpg://usuario:clave@host:5432/nombre_db
    database_url: str
    db_pool_size: int = 10         # Conexiones mantenidas activas en el pool
    db_max_overflow: int = 20      # Conexiones adicionales permitidas bajo pico de carga
    db_echo: bool = False          # Si True, SQLAlchemy imprime cada sentencia SQL generada

    # ── Parámetros de Gemini 3.6 Flash ────────────────────────────────────────
    # Los parámetros de generación (temperatura, top_p, etc.) se calibraron
    # empíricamente sobre el corpus de 200 casos (Anexo H) con Gemini 2.5 Flash.
    # El modelo default se migró a Gemini 3.6 Flash porque la familia 2.5 ya no
    # está disponible para cuentas nuevas. Cambiar el modelo exige re-evaluar las
    # métricas de exactitud.
    gemini_api_key: str                         # Clave de API de Google AI (obligatoria)
    gemini_model: str = "gemini-3.6-flash"
    gemini_temperature: float = 0.3             # Reduce variabilidad; mejora consistencia
    gemini_top_p: float = 0.9                   # Nucleus sampling para variantes léxicas rioplatenses
    gemini_max_output_tokens: int = 100         # Suficiente para JSON (~15 tokens) + margen
    gemini_candidate_count: int = 1             # Respuesta única; optimiza latencia
    # 30s (antes 10s): la familia 3.x puede encadenar reintentos del SDK ante 503
    # transitorios de alta demanda; 10s cortaba esos reintentos con falso timeout.
    gemini_timeout_seconds: int = 30            # Límite de espera antes de activar fallback
    # Ruta al archivo de prompt. Vacío = autoresolver desde la raíz del repositorio
    # (docs/prompt_gemini.txt). El override es necesario en contenedores donde la
    # estructura difiere del repo (ej. GEMINI_PROMPT_PATH=/app/docs/prompt_gemini.txt).
    gemini_prompt_path: str = ""

    # ── Umbrales del clasificador híbrido ─────────────────────────────────────
    # Determinados empíricamente; documentados en docs/parameters_gemini.md.
    deterministic_confidence_threshold: float = 0.90  # Por encima: se omite Gemini
    human_review_threshold: float = 0.70              # Por debajo: se requiere revisión humana

    # ── Integración con N8N ───────────────────────────────────────────────────
    # Si n8n_webhook_url está vacío, la notificación se omite silenciosamente.
    n8n_webhook_url: str = ""
    n8n_webhook_secret: str = ""   # Header X-N8N-Secret para autenticación básica
    # c-52: webhook de handoff del canal de telefonía en n8n. El backend envía
    # SOLO la descripción pseudonimizada ({descripcion_pseudonimizada, call_sid,
    # caller, ingresado_en}) autenticado con `n8n_webhook_secret` (header
    # `X-N8N-Secret`). Si queda vacío, el handoff se omite con evento observable.
    n8n_telefonia_webhook_url: str = ""

    # ── Instrumentación temporal end-to-end (C-39) ────────────────────────────
    # Tolerancia de futuro para `ingresado_en`: se acepta un ingreso hasta este
    # desfase por delante del ahora del servidor (skew de relojes entre n8n y el
    # backend). Valores más allá se rechazan para evitar latencias negativas.
    # 30 s es suficiente porque en docker-compose todos los contenedores comparten
    # el reloj del host; una tolerancia amplia encubriría datos inválidos.
    timing_future_tolerance_seconds: int = 30

    # ── Guarda de costo en runtime (c-45) ─────────────────────────────────────
    # Tope de gasto pago de las CUATRO superficies (Gemini backend, Gemini n8n,
    # admision de voz Twilio y STT del backend) con una bolsa GLOBAL compartida.
    # Default conservador HABILITADO, sobrescribible por .env/Settings. Los
    # costos unitarios son ESTIMACIONES configurables, NO contabilidad exacta: el
    # objetivo es acotar el gasto con un tope determinista, no medir tokens ni
    # duraciones reales. Los defaults no estan verificados contra precios
    # vigentes.
    cost_guard_enabled: bool = True
    cost_guard_budget_usd: float = 10.0           # bolsa global semanal (USD)
    cost_guard_budget_window_seconds: int = 604800  # 7 dias (ventana tumbling)
    cost_guard_unit_cost_backend_gemini_usd: float = 0.0005   # ESTIMACION por incidente
    cost_guard_unit_cost_n8n_gemini_usd: float = 0.0015       # ESTIMACION por ejecucion
    # c-52: la admision de voz de Twilio ya NO incluye transcripcion (el STT es
    # del backend y se reserva en su propia superficie). Re-estimado a partir del
    # costo de voz programable + almacenamiento de la grabacion (~USD 0.0075 por
    # llamada de 45 s). Es una ESTIMACION.
    cost_guard_unit_cost_twilio_transcription_usd: float = 0.0075  # ESTIMACION por llamada
    # c-52: superficie paga del STT del backend, reservada ANTES de descargar y
    # transcribir. Default ~USD 0.0038 por llamada de 45 s (gemini-3.5-transcribe
    # ~USD 0.005/min). Es una ESTIMACION configurable.
    cost_guard_unit_cost_backend_stt_usd: float = 0.0038   # ESTIMACION por llamada
    cost_guard_rate_limit_calls: int = 30         # rate global de llamadas pagas
    cost_guard_rate_window_seconds: int = 3600    # ventana del rate global
    cost_guard_caller_rate_limit_calls: int = 3   # rate por numero de origen
    cost_guard_caller_rate_window_seconds: int = 3600  # ventana del rate por origen
    cost_guard_degradation_policy: str = "deterministic_review"  # vs "hard_block"
    # Politica ante almacen caido. El default RESUELTO es "fail_closed". El valor
    # "fail_open" permite la llamada paga sin tope y solo debe usarse de forma
    # deliberada; cualquier valor distinto de "fail_open" se trata como fail_closed.
    cost_guard_store_failure_policy: str = "fail_closed"         # vs "fail_open"
    # Si True, ademas del evento estructurado obligatorio se dispara la
    # notificacion externa al webhook de N8N (N8N_WEBHOOK_URL) cuando el almacen
    # cae. El evento estructurado se emite SIEMPRE (observabilidad).
    cost_guard_alert_enabled: bool = True
    # Secreto compartido OBLIGATORIO para autenticar los endpoints de guarda
    # (header `X-Cost-Guard-Secret`): el endpoint de reserva que consume n8n y el
    # webhook de voz pre-llamada de Twilio. Si queda vacio, los endpoints
    # RECHAZAN toda peticion con HTTP 401 y se emite una advertencia al arrancar:
    # no existe configuracion con la guarda habilitada y los endpoints abiertos.
    # El secreto NUNCA se acepta por query string (se registraria en los logs).
    cost_guard_shared_secret: str = ""
    # Auth token de la cuenta de Twilio. Cuando esta configurado, el webhook de
    # voz exige la firma `X-Twilio-Signature` (HMAC-SHA1, ver
    # app/cost_guard/twilio_signature.py). Cuando falta (credencial pendiente),
    # se omite la validacion de firma pero el secreto compartido sigue siendo
    # obligatorio: el endpoint nunca queda abierto.
    twilio_auth_token: str = ""

    # ── Canal de telefonia / STT del backend (c-52) ───────────────────────────
    # Account SID de Twilio: se usa como usuario del HTTP Basic al descargar la
    # grabacion (`AccountSid:AuthToken`). Junto con `twilio_auth_token`.
    twilio_account_sid: str = ""
    # Base publica del backend tal como la ve Twilio, para construir los
    # callbacks del `<Record>` (estado de grabacion y accion de cierre). Debe ser
    # accesible desde internet (p. ej. el host de Nginx del stack). Sin valor,
    # los callbacks quedan como rutas relativas y Twilio no puede alcanzarlos.
    backend_public_base_url: str = ""
    # Modelo dedicado de speech-to-text de Gemini (verbatim). Configurable sin
    # tocar codigo; default `gemini-3.5-transcribe` (Stable).
    gemini_stt_model: str = "gemini-3.5-transcribe"

    # ── Logging estructurado ──────────────────────────────────────────────────
    log_level: str = "INFO"        # Nivel mínimo de emisión de eventos
    log_format: str = "json"       # "json" para producción; "console" para desarrollo

    # ── Pseudonimización (Ley 25.326) ─────────────────────────────────────────
    # Dominios corporativos internos cuyos hosts se enmascaran como [HOST].
    # Ejemplo .env: PSEUDONYMIZATION_INTERNAL_DOMAINS=["empresa.local","corp.empresa.com"]
    pseudonymization_internal_domains: list[str] = []
    # Clave Fernet (base64 urlsafe de 32 bytes) para cifrar descripcion_original at-rest.
    # Generar con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # OBLIGATORIA antes de arrancar la app o correr migraciones que toquen incidentes.
    # Ejemplo .env: PSEUDONYMIZATION_ENCRYPTION_KEY=<resultado del comando anterior>
    pseudonymization_encryption_key: str

    # ── Autenticación JWT ──────────────────────────────────────────────────────
    # Clave secreta para firmar tokens JWT (algoritmo HS256). OBLIGATORIA.
    # Generar con: python -c "import secrets; print(secrets.token_urlsafe(32))"
    jwt_secret_key: str
    # Algoritmo de firma; HS256 es simétrico y suficiente para un backend monolítico.
    jwt_algorithm: str = "HS256"
    # Tiempo de expiración del token en minutos (24 horas por defecto).
    jwt_expire_minutes: int = 1440


@lru_cache
def get_settings() -> Settings:
    """
    Retorna la instancia única de configuración del sistema.

    El decorador lru_cache garantiza que Settings() se construya una sola vez,
    evitando múltiples lecturas del archivo .env durante el ciclo de vida
    de la aplicación. En los tests, este caché puede limpiarse con
    get_settings.cache_clear() para inyectar configuración de prueba.
    """
    return Settings()
