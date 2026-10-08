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

    async def get_by_username_for_update(self, username: str) -> User | None:
        """
        Igual que `get_by_username` pero adquiere un lock de fila (W2).

        Emite `SELECT ... FOR UPDATE`, serializando las lecturas concurrentes
        de la misma cuenta (p. ej. el contador de intentos fallidos del bloqueo
        por cuenta). En motores que no soportan FOR UPDATE (SQLite) la clausula
        se ignora silenciosamente y el metodo se comporta como `get_by_username`.

        El lock se mantiene hasta el commit/rollback de la transaccion (Unit of
        Work gestionado por `get_db_session`).

        Args:
            username: Nombre de usuario a buscar y bloquear.

        Returns:
            Instancia de User o None si no existe ningun usuario con ese nombre.
        """
        result = await self._session.execute(
            select(User).where(User.username == username).with_for_update()
        )
        return result.scalar_one_or_none()
