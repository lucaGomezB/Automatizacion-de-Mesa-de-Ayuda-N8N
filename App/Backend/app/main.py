"""
Punto de entrada principal de la aplicación FastAPI.

Responsabilidad:
    Define la función de fábrica create_app() que construye y configura la
    instancia de FastAPI de forma programática. Este patrón de fábrica
    facilita la creación de instancias independientes para testing sin
    afectar la instancia de producción.

    La función lifespan() gestiona el ciclo de vida de la aplicación:
    inicializa el logging al arranque y libera el pool de conexiones al cierre,
    garantizando un shutdown limpio en entornos containerizados.

Convenciones:
    - La documentación interactiva (/docs, /redoc) solo se habilita en modo debug
      para evitar exposición de la API en entornos de producción.
    - El CORS está configurado permisivo por defecto; restringirlo según el
      entorno de despliegue antes de producción.

Arquitectura del stack de middleware (de más externo a más interno):
    ServerErrorMiddleware  ← siempre outermost, lo agrega FastAPI automáticamente
      CORSMiddleware       ← agrega los headers Access-Control-Allow-Origin
        _InternalErrorMiddleware  ← captura excepciones que escapan de los handlers
          ExceptionMiddleware     ← llama a los @exception_handler registrados
            Router                ← endpoints de la API

    El orden de add_middleware() es contraintuitivo en Starlette: cada llamada
    inserta el middleware en la POSICIÓN 0 de la lista interna, y la lista se
    recorre en reversa al construir el stack. Por eso el último middleware
    agregado es el MÁS EXTERNO.

    Para que _InternalErrorMiddleware quede DENTRO de CORSMiddleware (de modo
    que sus respuestas de error pasen por el wrapper `send` de CORS y reciban
    los headers), debe agregarse ANTES que CORSMiddleware.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config.settings import get_settings
from app.core.database import engine
from app.core.error_handlers import register_error_handlers
from app.core.logging import configure_logging, get_logger
from app.routes import register_routes

_middleware_logger = get_logger(__name__)


class _InternalErrorMiddleware:
    """
    Middleware ASGI de captura de última instancia para garantizar CORS en errores.

    Problema que resuelve:
        CORSMiddleware (Starlette) agrega los headers Access-Control-Allow-Origin
        envolviendo el callable `send` del protocolo ASGI. Solo agrega los headers
        cuando la respuesta pasa a través de ese wrapper. Si una excepción escapa
        de ExceptionMiddleware (p. ej. porque unhandled_handler crasheó) sin que
        ninguna respuesta haya sido enviada, la excepción llega hasta
        ServerErrorMiddleware, que usa el `send` original (sin el wrapper de CORS),
        y el cliente recibe el 500 sin Access-Control-Allow-Origin.

    Solución:
        Este middleware se ubica DENTRO de CORSMiddleware. Captura cualquier
        excepción que escape de ExceptionMiddleware y retorna un JSONResponse
        de forma controlada. Como el response se envía a través del `send` que
        recibe este middleware (que ya es el wrapper de CORSMiddleware), los
        headers CORS son agregados correctamente.

    Cuándo se activa:
        Solo cuando unhandled_handler crashea (escenario extremadamente raro en
        producción correctamente configurada). En operación normal, todas las
        excepciones son capturadas por los @exception_handler y este middleware
        simplemente hace pass-through.

    Nota de implementación:
        Se implementa como ASGI puro (sin BaseHTTPMiddleware) para evitar los
        problemas de buffering de body y de compatibilidad con streaming responses
        que tiene BaseHTTPMiddleware en Starlette.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            # Pasar WebSockets y otros tipos de conexión sin modificar.
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            # Esta rama solo se alcanza si ExceptionMiddleware dejó escapar
            # la excepción (i.e. el unhandled_handler lanzó). Loguear y responder.
            try:
                _middleware_logger.error(
                    "escaped_exception_captured_by_safety_middleware",
                    exc_type=type(exc).__name__,
                    exc_info=exc,
                )
            except Exception:
                pass  # El logging nunca puede impedir que se envíe la respuesta.

            response = JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred.",
                    }
                },
            )
            # `send` aquí es el wrapper de CORSMiddleware → los headers CORS
            # se agregan automáticamente antes de llegar al cliente.
            await response(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Contexto de ciclo de vida de la aplicación (startup / shutdown).

    FastAPI ejecuta el bloque anterior al yield al iniciar el servidor
    y el bloque posterior al yield cuando el servidor se cierra.

    Acciones al inicio:
        - Configura el sistema de logging estructurado antes de que
          cualquier componente emita su primer evento.

    Acciones al cierre:
        - Libera todas las conexiones del pool de SQLAlchemy para
          evitar conexiones huérfanas en la base de datos PostgreSQL.
    """
    # ── Startup ───────────────────────────────────────────────────────────────
    configure_logging()
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Fábrica de la aplicación FastAPI.

    Construye y configura la instancia con todos sus componentes:
    middleware de CORS, manejadores de errores y rutas de la API.
    Al centralizar la creación en una función, los tests pueden
    invocarla independientemente para obtener instancias aisladas.

    Returns:
        Instancia configurada y lista para servir solicitudes HTTP.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        # La documentación interactiva solo se expone en modo debug
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── Stack de middleware ────────────────────────────────────────────────────
    # ORDEN CRÍTICO: en Starlette, el último add_middleware() es el más externo.
    #
    # Paso 1: agregar _InternalErrorMiddleware PRIMERO → quedará más INTERNO
    #         (dentro de CORSMiddleware), asegurando que sus respuestas de error
    #         pasen por el wrapper `send` de CORS y reciban los headers.
    app.add_middleware(_InternalErrorMiddleware)

    # Paso 2: agregar CORSMiddleware ÚLTIMO → quedará más EXTERNO.
    #         allow_credentials=False es obligatorio con allow_origins=["*"].
    #         En producción: reemplazar ["*"] por ["https://mi-frontend.com"].
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept", "Authorization"],
        expose_headers=["X-Request-ID"],
    )

    # ── Registro de componentes ───────────────────────────────────────────────
    register_error_handlers(app)  # Manejadores de excepción → respuestas HTTP
    register_routes(app)          # Rutas de la API bajo /api/v1 y /health

    return app


# Instancia global utilizada por uvicorn al ejecutar:
#   uvicorn app.main:app --host 0.0.0.0 --port 8000
app = create_app()
