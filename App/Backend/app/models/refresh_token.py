"""
Modelo ORM del token de refresco persistido (IAH-003, c-63a).

Responsabilidad:
    Almacena los refresh tokens OPACOS del sistema. El valor en claro NUNCA se
    persiste: solo se guarda su hash SHA-256. Cada token referencia al usuario,
    su expiracion, su revocacion y el token del que proviene (`rotated_from`),
    lo que habilita la rotacion y la deteccion de reutilizacion.

Decisiones (design.md D4):
    - Persistencia en PostgreSQL (y compatible con SQLite para el subconjunto
      offline, que crea la tabla via `Base.metadata`).
    - El access se valida por firma; el refresh, en servidor.
    - `token_version` en `users` es el complemento para la revocacion
      administrativa masiva, no este modelo.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class RefreshToken(Base, TimestampMixin):
    """Refresh token opaco rotativo almacenado como hash.

    Campos:
        id:           Clave primaria.
        user_id:      FK al usuario dueno del token (ON DELETE CASCADE).
        token_hash:   SHA-256 hexadecimal del valor opaco (unico, indexado).
        expires_at:   Instante de expiracion (UTC).
        revoked_at:   Instante de revocacion; None si sigue activo.
        rotated_from: FK al token predecesor que fue rotado (None para el
                      primer token de una sesion).
        created_at / updated_at: auditoria temporal (TimestampMixin).
    """

    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    rotated_from: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("refresh_token.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<RefreshToken id={self.id} user_id={self.user_id} "
            f"revoked={self.revoked_at is not None}>"
        )