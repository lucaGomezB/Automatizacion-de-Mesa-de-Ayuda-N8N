from fastapi import FastAPI

from app.routes.clasificaciones import router as clasificaciones_router
from app.routes.health import router as health_router
from app.routes.incidentes import router as incidentes_router


def register_routes(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(incidentes_router, prefix="/api/v1")
    app.include_router(clasificaciones_router, prefix="/api/v1")
