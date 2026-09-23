from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.catalogos import router as catalogos_router
from app.routes.clasificaciones import router as clasificaciones_router
from app.routes.cost_guard import router as cost_guard_router
from app.routes.estadisticas import router as estadisticas_router
from app.routes.health import router as health_router
from app.routes.incidentes import router as incidentes_router
from app.routes.telefonia import router as telefonia_router


def register_routes(app: FastAPI) -> None:
    app.include_router(health_router)                          # /health, /health/db
    app.include_router(health_router, prefix="/api/v1")       # /api/v1/health, /api/v1/health/db
    app.include_router(auth_router, prefix="/api/v1")         # /api/v1/auth/login
    app.include_router(incidentes_router, prefix="/api/v1")
    app.include_router(clasificaciones_router, prefix="/api/v1")
    app.include_router(estadisticas_router, prefix="/api/v1")
    app.include_router(catalogos_router, prefix="/api/v1")    # /api/v1/catalogos/sectores
    app.include_router(cost_guard_router, prefix="/api/v1")   # /api/v1/cost-guard/*
    app.include_router(telefonia_router, prefix="/api/v1")    # /api/v1/telefonia/*
