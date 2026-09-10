"""
Dependencias de seguridad para FastAPI — autenticacion JWT.

Responsabilidad:
    Define el esquema OAuth2PasswordBearer y la dependencia get_current_user
    que valida el token JWT en cada request protegido. Esta dependencia se
    inyecta via Depends() en las rutas que requieren autenticacion.

    Tambien re-exporta create_access_token y get_password_hash desde
    auth_service para que los tests puedan importarlos desde un solo lugar,
    evitando dependencia circular con services/auth_service.py.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.database import get_db_session
from app.core.logging import get_logger
from app.models.user import User
from app.services.auth_service import create_access_token, get_password_hash  # noqa: F401 — re-export

logger = get_logger(__name__)

# Esquema OAuth2: espera el token en el header Authorization: Bearer <token>.
# tokenUrl es el endpoint de login; FastAPI lo usa para la documentacion interactiva.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """
    Dependencia de FastAPI que valida el JWT y retorna el usuario autenticado.

    Flujo:
        1. Verifica que el token este presente en el header Authorization.
        2. Decodifica el JWT usando la clave secreta y algoritmo configurados.
        3. Extrae el username del campo 'sub' del payload.
        4. Busca al usuario en la base de datos.
        5. Retorna la instancia de User si todo es valido.

    Args:
        token: Token JWT extraido del header Authorization (via OAuth2PasswordBearer).
        session: Sesion de base de datos inyectada por FastAPI.

    Returns:
        Instancia de User autenticado.

    Raises:
        HTTPException 401: Si el token esta ausente, es invalido, expiro,
                           o el usuario no existe / esta inactivo.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        logger.warning("auth_invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning("auth_user_not_found", username=username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("auth_inactive_user", username=username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
