from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.clasificaciones import router as clasificaciones_router
from app.routes.estadisticas import router as estadisticas_router
from app.routes.health import router as health_router
from app.routes.incidentes import router as incidentes_router


def register_routes(app: FastAPI) -> None:
    app.include_router(health_router)                          # /health, /health/db
    app.include_router(health_router, prefix="/api/v1")       # /api/v1/health, /api/v1/health/db
    app.include_router(auth_router, prefix="/api/v1")         # /api/v1/auth/login
    app.include_router(incidentes_router, prefix="/api/v1")
    app.include_router(clasificaciones_router, prefix="/api/v1")
    app.include_router(estadisticas_router, prefix="/api/v1")
