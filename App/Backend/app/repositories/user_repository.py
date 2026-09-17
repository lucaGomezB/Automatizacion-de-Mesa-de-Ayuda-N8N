"""
Repositorio para la entidad User.

Responsabilidad:
    Encapsula la consulta por nombre de usuario utilizada tanto por el flujo
    de login (`auth_service.authenticate_user`) como por la dependencia de
    seguridad (`core.security.get_current_user`). De este modo ninguna capa
    de servicio ni dependencia de seguridad construye consultas ORM directas
    contra la sesion (regla de disciplina de capas, ERR-004).
"""

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repositorio de acceso a datos para la entidad User."""

    model = User

    async def get_by_username(self, username: str) -> User | None:
        """
        Busca un usuario por su nombre de usuario exacto.

        Args:
            username: Nombre de usuario a buscar.

        Returns:
            Instancia de User o None si no existe ningun usuario con ese nombre.
        """
        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
