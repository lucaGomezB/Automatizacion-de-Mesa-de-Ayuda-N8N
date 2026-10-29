"""
Modelo ORM del directorio de empleados (c-54).

Responsabilidad:
    Define la tabla `directorio_empleado`, una entidad de contacto SEPARADA de
    la autenticacion (`users`) que almacena los datos minimizados de un empleado
    de la mesa de ayuda: legajo, nombre, email, telefono, sector, rol y estado.

Decisiones (design.md D1-D6b):
    - D1: entidad propia; `user_id` es un vinculo opcional a `users` (FK nullable,
      ON DELETE SET NULL) para saber que cuenta corresponde a que empleado, sin
      fusionar el dominio de autenticacion con el de contacto.
    - D2/D3 (c-82) y c-86: rol de CUATRO valores (`usuario_final`, `mesa_de_ayuda`,
      `administrador_directorio` y `gestion_incidentes`, este ultimo incorporado
      por c-86). El `sector_id` es dato organizacional OPCIONAL
      sin efecto en la autorizacion. La politica de cada rol vive en
      `app.services.role_policy`.
    - D4 (c-153, REVERTIDA): el email y el telefono se almacenan CIFRADOS
      at-rest con `EncryptedText` (Fernet). La decision original de texto plano
      (DIR-005/DIR-010) quedo SUPERADA por el ADR de reversion; la justificacion
      por minimizacion previa se conserva como registro historico.
    - D6b: se almacenan EXACTAMENTE los campos definidos, nada mas.

Nota sobre async: la relacion `sector` debe cargarse con `selectinload()` en el
repositorio cuando se serializa; nunca se accede de forma lazy fuera de una
sesion activa.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.utils.blind_index import email_blind_index, telefono_blind_index
from app.utils.encryption import EncryptedText


class RolEmpleado(str, PyEnum):
    """
    Vocabulario minimo de roles del directorio (DIR-003, c-82).

    Hereda de `str` para almacenar el valor textual y serializarlo directamente.
    El conocimiento de politica de cada rol vive en `app.services.role_policy`
    (fuente unica de verdad); este enum solo fija el VOCABULARIO.

    Valores (EXACTAMENTE CUATRO):
        usuario_final:            reportante; alcance PROPIO (solo lo que reporto).
        mesa_de_ayuda:            rol transversal; alcance GLOBAL, privilegiado y
                                  destinatario de la notificacion de revision.
        administrador_directorio: alcance GLOBAL, privilegiado y gestiona el directorio.
        gestion_incidentes:       rol operativo por sector (c-86); alcance SECTOR,
                                  NO privilegiado, cierra y edita el estado de los
                                  incidentes de su sector y es destinatario del aviso
                                  post-revision.
    """

    usuario_final = "usuario_final"
    mesa_de_ayuda = "mesa_de_ayuda"
    administrador_directorio = "administrador_directorio"
    gestion_incidentes = "gestion_incidentes"


class Empleado(Base, TimestampMixin):
    """
    Empleado del directorio interno de la mesa de ayuda.

    Campos (D6b, minimizacion):
        id:       Clave primaria.
        legajo:   Identificador laboral, obligatorio y unico.
        nombre:   Nombre del empleado, obligatorio.
        email:    Contacto por correo, obligatorio, unico e indexado. Cifrado
                  at-rest con `EncryptedText` (c-153).
        telefono: Contacto telefonico E.164, opcional, indexado y repetible.
                  Cifrado at-rest con `EncryptedText` (c-153).
        email_bidx / telefono_bidx: Indice ciego determinista (HMAC-SHA-256 de la
                  forma normalizada, c-153 DIR-011). Columnas derivadas, no PII en
                  claro; `email_bidx` es UNIQUE (unicidad del email) y
                  `telefono_bidx` no (telefono repetible).
        sector_id: FK al catalogo `sector` (obligatorio para usuario_final/operador).
        rol:      Rol del empleado (RolEmpleado).
        activo:   Estado de la relacion; False desactiva sin borrar.
        fecha_baja: Instante de desactivacion (UTC); None si esta activo. Es la
                    base de la retencion: se borra fisicamente al vencer
                    "fecha_baja + 1 año" (DIR-007). Se limpia al reactivar.
        user_id:  FK nullable a `users` (ON DELETE SET NULL).
        created_at / updated_at: auditoria temporal (TimestampMixin).
    """

    __tablename__ = "directorio_empleado"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    legajo: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(
        EncryptedText, nullable=False, unique=True, index=True
    )
    # Telefono cifrado at-rest (E.164), opcional y repetible (no unique).
    telefono: Mapped[str | None] = mapped_column(EncryptedText, nullable=True, index=True)
    # Indice ciego determinista del contacto (c-153, DIR-011): HMAC-SHA-256 de la
    # forma normalizada, derivado con la clave dedicada `directory_blind_index_key`.
    # NO es PII en claro y no permite reconstruir el valor sin la clave. La
    # unicidad del email vive sobre `email_bidx` (el ciphertext Fernet no es
    # determinista, de modo que un UNIQUE sobre `email` no detecta duplicados);
    # `telefono_bidx` NO es UNIQUE porque el telefono es repetible. Ambas columnas
    # son nullable (indice derivado; la aplicacion las completa en cada escritura),
    # y `email_bidx` es UNIQUE: los valores no nulos deben ser unicos.
    email_bidx: Mapped[str | None] = mapped_column(
        String(64), nullable=True, unique=True, index=True
    )
    telefono_bidx: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    sector_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sector.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Instante de desactivacion (retencion DIR-007). Nullable: None = activo.
    fecha_baja: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relacion unidireccional al catalogo canonico. Debe cargarse con
    # selectinload() cuando se serializa (async).
    sector: Mapped["Sector | None"] = relationship("Sector", lazy="select")  # type: ignore[name-defined]

    __table_args__ = (
        # El CHECK enumera el vocabulario porque la base no lee codigo; debe
        # coincidir con `ROLES_VALIDOS` de `app.services.role_policy` (RP-003,
        # verificado por tests/test_role_policy.py).
        CheckConstraint(
            "rol IN ('usuario_final', 'mesa_de_ayuda', 'administrador_directorio', "
            "'gestion_incidentes')",
            name="ck_directorio_empleado_rol",
        ),
    )

    def __repr__(self) -> str:
        # Sin datos personales en la representacion (no-PII en logs).
        return f"<Empleado id={self.id} legajo={self.legajo!r} rol={self.rol!r}>"


@event.listens_for(Empleado, "before_insert")
@event.listens_for(Empleado, "before_update")
def _derivar_indices_ciegos(mapper, connection, target: Empleado) -> None:
    """Deriva `email_bidx`/`telefono_bidx` del contacto en claro al persistir.

    Se engancha en los eventos del mapper para que TODA escritura (servicio,
    repositorio o un modelo construido en un test) mantenga el indice ciego
    coherente con el contacto cifrado, sin depender de que cada llamador lo
    calcule. La derivacion es determinista e idempotente.
    """
    if target.email is not None:
        target.email_bidx = email_blind_index(target.email)
    target.telefono_bidx = telefono_blind_index(target.telefono)
