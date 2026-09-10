"""
Servicio de autenticacion de usuarios.

Responsabilidad:
    Implementa la logica de negocio del flujo de login: verificacion de
    credenciales contra el hash bcrypt almacenado, generacion de tokens
    JWT firmados, y resolucion de usuarios desde la base de datos.

    Capa intermedia entre routes/auth.py (HTTP) y el modelo User (ORM).
    No contiene dependencias de FastAPI; es puramente logica de negocio.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una password en texto plano coincida con su hash bcrypt.

    Args:
        plain_password: Password ingresada por el usuario en el login.
        hashed_password: Hash bcrypt almacenado en la base de datos.

    Returns:
        True si la password coincide, False en caso contrario.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """
    Genera el hash bcrypt de una password en texto plano.

    Se utiliza durante la creacion de usuarios (migracion de seed) y
    potencialmente en endpoints de administracion futuros.

    Args:
        password: Password en texto plano a hashear.

    Returns:
        String con el hash bcrypt.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    data: dict,
    secret: str,
    algorithm: str = "HS256",
    expires_delta: int | None = None,
) -> str:
    """
    Crea un token JWT firmado con los datos proporcionados.

    Args:
        data: Payload a incluir en el token (tipicamente {"sub": username}).
        secret: Clave secreta para firmar el token.
        algorithm: Algoritmo de firma (por defecto HS256).
        expires_delta: Minutos hasta la expiracion. Si es None, no expira.

    Returns:
        Token JWT codificado como string.
    """
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> User | None:
    """
    Autentica un usuario por username y password.

    Busca al usuario en la base de datos, verifica que este activo,
    y compara la password contra el hash almacenado.

    Args:
        session: Sesion de base de datos activa.
        username: Nombre de usuario a autenticar.
        password: Password en texto plano a verificar.

    Returns:
        Instancia de User si las credenciales son validas, None en caso contrario.
    """
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        return None
    if not user.is_active:
        logger.info("auth_inactive_user", username=username)
        return None
    if not verify_password(password, user.hashed_password):
        return None

    logger.info("auth_login_success", username=username, user_id=user.id)
    return user
