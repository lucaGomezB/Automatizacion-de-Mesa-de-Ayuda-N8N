"""
Repositorio de refresh tokens (IAH-003/IAH-004, c-63a).

Responsabilidad:
    Encapsula la persistencia y consulta de los refresh tokens opacos. Ninguna
    capa de servicio construye consultas ORM directas contra `refresh_token`
    (disciplina de capas). El valor en claro nunca llega aqui: solo su hash.

Modelo de acceso:
    - `create`: registra un token nuevo (hash + expiracion + origen de rotacion).
    - `get_by_hash`: resuelve un token presentado (indice unico por hash).
    - `revoke`: marca `revoked_at` (logout o rotacion).
    - `revoke_active_for_user`: revoca masivamente los tokens activos (logout
      administrativo / cambio de contrasena).
"""

from datetime import datetime
from typing import Any

from sqlalchemy import select, update

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class TokenRepository(BaseRepository[RefreshToken]):
    """Repositorio de acceso a datos para `RefreshToken`."""

    model = RefreshToken

    async def create(  # type: ignore[override]
        self,
        *,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        rotated_from: int | None = None,
    ) -> RefreshToken:
        """Persiste un refresh token (solo el hash, nunca el valor en claro)."""
        return await super().create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            rotated_from=rotated_from,
        )

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Busca un refresh token por el hash de su valor opaco."""
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken, *, now: datetime) -> None:
        """Marca un token como revocado (idempotente: no sobreescribe)."""
        if token.revoked_at is None:
            token.revoked_at = now
            await self._session.flush()

    async def revoke_active_for_user(self, user_id: int, *, now: datetime) -> int:
        """Revoca todos los tokens activos del usuario; retorna cuantos afecto."""
        result = await self._session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        await self._session.flush()
        return result.rowcount or 0


__all__: list[Any] = ["TokenRepository"]