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

    # ── Parámetros de Gemini 2.5 Flash ────────────────────────────────────────
    # Valores calibrados empíricamente sobre el corpus de 200 casos (Anexo H).
    # Modificar estos valores requiere re-evaluar las métricas de exactitud.
    gemini_api_key: str                         # Clave de API de Google AI (obligatoria)
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.3             # Reduce variabilidad; mejora consistencia
    gemini_top_p: float = 0.9                   # Nucleus sampling para variantes léxicas rioplatenses
    gemini_max_output_tokens: int = 100         # Suficiente para JSON (~15 tokens) + margen
    gemini_candidate_count: int = 1             # Respuesta única; optimiza latencia
    gemini_timeout_seconds: int = 10            # Límite de espera antes de activar fallback

    # ── Umbrales del clasificador híbrido ─────────────────────────────────────
    # Determinados empíricamente; documentados en docs/parameters_gemini.md.
    deterministic_confidence_threshold: float = 0.90  # Por encima: se omite Gemini
    human_review_threshold: float = 0.70              # Por debajo: se requiere revisión humana

    # ── Integración con N8N ───────────────────────────────────────────────────
    # Si n8n_webhook_url está vacío, la notificación se omite silenciosamente.
    n8n_webhook_url: str = ""
    n8n_webhook_secret: str = ""   # Header X-N8N-Secret para autenticación básica

    # ── Logging estructurado ──────────────────────────────────────────────────
    log_level: str = "INFO"        # Nivel mínimo de emisión de eventos
    log_format: str = "json"       # "json" para producción; "console" para desarrollo


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
