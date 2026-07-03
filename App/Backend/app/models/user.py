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

from sqlalchemy import Boolean, String
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

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
