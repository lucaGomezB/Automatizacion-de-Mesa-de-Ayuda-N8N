"""
Modelo ORM de la entidad User para autenticacion del sistema.

Responsabilidad:
    Define la tabla 'users' que almacena las credenciales de los operadores
    de mesa de ayuda. Almacena el username en texto plano y la password
    hasheada con bcrypt (via passlib). El campo is_active permite deshabilitar
    usuarios sin eliminar sus registros.

    Este modelo es usado exclusivamente por el flujo de autenticacion JWT.
    No esta relacionado con la entidad Incidente ni con el dominio de
    clasificacion.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Usuario operador del sistema de mesa de ayuda.

    Autenticacion basada en JWT Bearer token: el usuario se loguea
    con username + password, recibe un token firmado, y lo envia
    en el header Authorization de cada request subsiguiente.

    Campos:
        id:              Identificador unico autogenerado.
        username:        Nombre de usuario unico para login.
        hashed_password: Hash bcrypt de la password (nunca en texto plano).
        is_active:       Si False, el login es rechazado.
        failed_attempts: Intentos de login fallidos consecutivos (IAH-002).
        lockout_window_start: Inicio de la ventana de conteo de intentos
                         fallidos (IAH-002, W2). Columna dedicada: la ventana
                         no depende de `updated_at`, que cualquier update ajeno
                         puede mover. Se fija en el primer fallo y se limpia al
                         reiniciar por exito, expiracion o re-anclaje.
        locked_until:    Instante hasta el que la cuenta esta bloqueada; None
                         si no lo esta (IAH-002).
        token_version:   Version de tokens de la cuenta. La revocacion
                         administrativa la incrementa y los access tokens
                         emitidos con la version anterior dejan de validar
                         (IAH-004).
        created_at:      Timestamp de creacion (heredado de TimestampMixin).
        updated_at:      Timestamp de ultima modificacion (heredado de TimestampMixin).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_attempts: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, server_default="0"
    )
    lockout_window_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    token_version: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, server_default="0"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
