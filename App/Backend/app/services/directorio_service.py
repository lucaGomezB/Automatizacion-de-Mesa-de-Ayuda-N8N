"""
Servicio de gestion del directorio de empleados (c-54).

Responsabilidad:
    Concentra la logica de negocio del directorio: validaciones de alta/edicion
    (campos obligatorios, unicidad de email, formato E.164, vocabulario de rol y
    coherencia rol/sector), ciclo de vida (desactivacion, reactivacion, borrado
    ARCO) y la AUDITORIA de cada operacion.

Privacidad (Ley 25.326 / DIR-006):
    El contacto se almacena en TEXTO PLANO (D4). La proteccion se logra con
    minimizacion, control de acceso por rol (capa de rutas) y auditoria. Los
    eventos de auditoria registran SOLO identificadores internos, operacion y
    resultado: NUNCA el email, el telefono ni el nombre en claro.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DirectorioValidationError,
    EntityNotFoundError,
    SectorNotFoundError,
)
from app.core.logging import get_logger
from app.models.empleado import Empleado, RolEmpleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.repositories.sector_repository import SectorRepository
from app.utils.contactos import normalizar_email, normalizar_telefono

logger = get_logger(__name__)

# Roles que EXIGEN sector (DIR-004).
_ROLES_CON_SECTOR = (RolEmpleado.usuario_final, RolEmpleado.operador)


def _normalizar_rol(rol: str | RolEmpleado | None) -> RolEmpleado:
    """Convierte el rol al vocabulario canonico o rechaza el valor."""
    if isinstance(rol, RolEmpleado):
        return rol
    try:
        return RolEmpleado(str(rol))
    except ValueError as exc:
        raise DirectorioValidationError(
            "El rol no pertenece al vocabulario permitido del directorio."
        ) from exc


class DirectorioService:
    """
    Servicio de negocio del directorio de empleados.

    Recibe la sesion por inyeccion y construye los repositorios internamente,
    compartiendo la transaccion de la solicitud. El `actor_id` identifica a
    quien ejecuta la operacion para la auditoria (no es PII del empleado).
    """

    def __init__(self, session: AsyncSession, actor_id: int | None = None) -> None:
        self._session = session
        self._repo = EmpleadoRepository(session)
        self._sector_repo = SectorRepository(session)
        self._actor_id = actor_id

    # ── Lectura ───────────────────────────────────────────────────────────────

    async def listar(
        self, *, solo_activos: bool = False, limit: int = 100, offset: int = 0
    ) -> list[Empleado]:
        """Lista empleados del directorio (administracion)."""
        return await self._repo.listar(
            solo_activos=solo_activos, limit=limit, offset=offset
        )

    async def obtener(self, empleado_id: int) -> Empleado:
        """Recupera un empleado por id; lanza EntityNotFoundError si no existe."""
        empleado = await self._repo.get_or_none(empleado_id)
        if empleado is None:
            raise EntityNotFoundError("Empleado", empleado_id)
        return empleado

    # ── Alta ──────────────────────────────────────────────────────────────────

    async def crear_empleado(
        self,
        *,
        legajo: str,
        nombre: str,
        email: str,
        telefono: str | None = None,
        sector_id: int | None = None,
        rol: str | RolEmpleado = RolEmpleado.usuario_final,
        user_id: int | None = None,
        actor_id: int | None = None,
    ) -> Empleado:
        """
        Crea un empleado validando las reglas de dominio del directorio.

        Raises:
            DirectorioValidationError: campos obligatorios, email duplicado,
                rol invalido, telefono fuera de E.164 o incoherencia rol/sector.
            SectorNotFoundError: si el sector indicado no existe en el catalogo.
        """
        legajo_norm = self._validar_texto(legajo, "legajo")
        nombre_norm = self._validar_texto(nombre, "nombre")
        email_norm = self._normalizar_email(email)
        telefono_norm = self._normalizar_telefono(telefono)
        rol_norm = _normalizar_rol(rol)
        sector_norm = await self._validar_sector_por_rol(rol_norm, sector_id)

        if await self._repo.get_by_legajo(legajo_norm) is not None:
            raise DirectorioValidationError("El legajo ya existe en el directorio.")
        if await self._repo.get_by_email(email_norm) is not None:
            raise DirectorioValidationError("El email ya esta asignado a otro empleado.")

        empleado = await self._repo.create(
            legajo=legajo_norm,
            nombre=nombre_norm,
            email=email_norm,
            telefono=telefono_norm,
            sector_id=sector_norm,
            rol=rol_norm,
            user_id=user_id,
            activo=True,
        )
        self._auditar("alta", "ok", empleado.id, actor_id)
        return empleado

    # ── Edicion ───────────────────────────────────────────────────────────────

    async def actualizar_empleado(
        self, empleado_id: int, *, actor_id: int | None = None, **campos
    ) -> Empleado:
        """
        Actualiza parcialmente un empleado. Solo aplica los campos enviados.

        Reutiliza las mismas validaciones del alta sobre el estado resultante
        (rol/sector combinados) y protege la unicidad de legajo/email.
        """
        empleado = await self.obtener(empleado_id)

        if "legajo" in campos and campos["legajo"] is not None:
            legajo = self._validar_texto(campos["legajo"], "legajo")
            existente = await self._repo.get_by_legajo(legajo)
            if existente is not None and existente.id != empleado_id:
                raise DirectorioValidationError("El legajo ya existe en el directorio.")
            empleado.legajo = legajo

        if "nombre" in campos and campos["nombre"] is not None:
            empleado.nombre = self._validar_texto(campos["nombre"], "nombre")

        if "email" in campos and campos["email"] is not None:
            email = self._normalizar_email(campos["email"])
            existente = await self._repo.get_by_email(email)
            if existente is not None and existente.id != empleado_id:
                raise DirectorioValidationError(
                    "El email ya esta asignado a otro empleado."
                )
            empleado.email = email

        if "telefono" in campos:
            empleado.telefono = self._normalizar_telefono(campos["telefono"])

        # Rol y sector se validan en conjunto sobre el estado resultante.
        if "rol" in campos or "sector_id" in campos:
            rol = _normalizar_rol(campos.get("rol", empleado.rol))
            sector_id = campos.get("sector_id", empleado.sector_id)
            empleado.sector_id = await self._validar_sector_por_rol(rol, sector_id)
            empleado.rol = rol

        if "user_id" in campos:
            empleado.user_id = campos["user_id"]

        self._session.add(empleado)
        await self._session.flush()
        await self._session.refresh(empleado)
        self._auditar("edicion", "ok", empleado.id, actor_id)
        return empleado

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    async def desactivar_empleado(
        self, empleado_id: int, *, actor_id: int | None = None
    ) -> Empleado:
        """Marca `activo=False` (desactivacion, no borrado operativo)."""
        empleado = await self.obtener(empleado_id)
        empleado.activo = False
        self._session.add(empleado)
        await self._session.flush()
        await self._session.refresh(empleado)
        self._auditar("desactivacion", "ok", empleado.id, actor_id)
        return empleado

    async def reactivar_empleado(
        self, empleado_id: int, *, actor_id: int | None = None
    ) -> Empleado:
        """Reactiva un empleado desactivado, sin recargar sus datos."""
        empleado = await self.obtener(empleado_id)
        empleado.activo = True
        self._session.add(empleado)
        await self._session.flush()
        await self._session.refresh(empleado)
        self._auditar("reactivacion", "ok", empleado.id, actor_id)
        return empleado

    async def borrar_empleado_arco(
        self, empleado_id: int, *, actor_id: int | None = None
    ) -> None:
        """Borrado FISICO por solicitud ARCO (no es el camino operativo)."""
        empleado = await self.obtener(empleado_id)
        await self._repo.delete(empleado.id)
        self._auditar("borrado_arco", "ok", empleado_id, actor_id)

    # ── Validaciones privadas ─────────────────────────────────────────────────

    @staticmethod
    def _validar_texto(valor: str | None, campo: str) -> str:
        """Exige un texto no vacio (sin exponer el valor en el mensaje)."""
        if valor is None or not str(valor).strip():
            raise DirectorioValidationError(f"El campo '{campo}' es obligatorio.")
        return str(valor).strip()

    @staticmethod
    def _normalizar_email(email: str | None) -> str:
        """Normaliza el email o lanza DirectorioValidationError (sin PII)."""
        try:
            return normalizar_email(email)
        except ValueError as exc:
            raise DirectorioValidationError(
                "El email no tiene un formato valido."
            ) from exc

    @staticmethod
    def _normalizar_telefono(telefono: str | None) -> str | None:
        """Normaliza el telefono a E.164 o lanza DirectorioValidationError."""
        if telefono is None or not str(telefono).strip():
            return None
        try:
            return normalizar_telefono(telefono)
        except ValueError as exc:
            raise DirectorioValidationError(
                "El telefono no tiene un formato E.164 valido."
            ) from exc

    async def _validar_sector_por_rol(
        self, rol: RolEmpleado, sector_id: int | None
    ) -> int | None:
        """
        Aplica la coherencia rol/sector (DIR-004) y valida la FK del catalogo.

        Returns:
            El `sector_id` normalizado a persistir (None para administrador).
        """
        if rol == RolEmpleado.administrador_directorio:
            if sector_id is not None:
                raise DirectorioValidationError(
                    "El administrador del directorio no debe tener sector asignado."
                )
            return None

        # usuario_final / operador
        if sector_id is None:
            raise DirectorioValidationError(
                "El rol requiere un sector asignado."
            )
        if await self._sector_repo.get_or_none(sector_id) is None:
            raise SectorNotFoundError(
                f"Sector con id={sector_id} no encontrado en el catalogo."
            )
        return sector_id

    def _auditar(
        self,
        operacion: str,
        resultado: str,
        empleado_id: int,
        actor_id: int | None,
    ) -> None:
        """Emite el evento de auditoria SIN datos personales (DIR-006)."""
        logger.info(
            "directorio_auditoria",
            operacion=operacion,
            resultado=resultado,
            empleado_id=empleado_id,
            actor_id=actor_id if actor_id is not None else self._actor_id,
        )
