"""
Servicio del ciclo de cierre de incidentes (c-86, incident-lifecycle).

Responsabilidad:
    Implementa las operaciones de ciclo de vida del incidente:
        - Cierre por sector (ILC-001): un `gestion_incidentes` cierra SU sector.
        - Cierre global (ILC-002): `mesa_de_ayuda` cierra todos los sectores.
        - Transicion terminal (ILC-003): al cerrar el ultimo sector, el incidente
          pasa al estado terminal `cerrado`.

    Cada operacion registra un `incidente_evento` con el actor y el instante
    (ILC-006, sin PII). La autorizacion se deriva del registro unico de politica
    de rol (RP-002): un rol sin el permiso correspondiente recibe 403; un
    incidente fuera del alcance del actor se comporta como 404.
"""

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EntityNotFoundError,
    IncidentValidationError,
    IncidenteCerradoError,
    PermisoDenegadoError,
)
from app.models.empleado import Empleado
from app.models.incidente import Incidente
from app.repositories.ciclo_incidente_repository import (
    IncidenteCierreSectorRepository,
    IncidenteEventoRepository,
)
from app.repositories.estado_repository import EstadoRepository
from app.repositories.incidente_repository import IncidenteRepository
from app.services.role_policy import politica_de_rol

if TYPE_CHECKING:
    from app.services.incident_visibility import AlcanceIncidentes

# Tipos de evento de ciclo de vida (D8, c-86).
TIPO_CIERRE_SECTOR = "cierre_sector"
TIPO_CIERRE_GLOBAL = "cierre_global"
TIPO_REAPERTURA = "reapertura"
TIPO_CAMBIO_ESTADO = "cambio_estado"

# Estado no terminal al que vuelve un incidente rehabilitado (D5, determinista).
ESTADO_REAPERTURA = "en proceso"

# Estados no terminales admisibles por la edicion de estado (ILC-005).
ESTADOS_EDITABLES = frozenset({"en proceso", "en espera", "resuelto"})

__all__ = [
    "CicloIncidenteService",
    "TIPO_CIERRE_SECTOR",
    "TIPO_CIERRE_GLOBAL",
    "TIPO_REAPERTURA",
    "TIPO_CAMBIO_ESTADO",
]


class CicloIncidenteService:
    """Logica de negocio del ciclo de cierre (IB: cierre por sector y global)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._incidente_repo = IncidenteRepository(session)
        self._cierre_repo = IncidenteCierreSectorRepository(session)
        self._evento_repo = IncidenteEventoRepository(session)
        self._estado_repo = EstadoRepository(session)

    # ── Cierre por sector (ILC-001) ───────────────────────────────────────────

    async def cerrar_sector(
        self,
        incidente_id: int,
        actor: Empleado | None,
        alcance: "AlcanceIncidentes | None" = None,
    ) -> Incidente:
        """
        Cierra el incidente para el sector del actor `gestion_incidentes`.

        Idempotente por el par (incidente, sector). Tras el cierre, verifica la
        transicion terminal (si todos los sectores cerraron, pasa a `cerrado`).
        """
        politica = self._politica(actor)
        if not politica.cierra_sector:
            raise PermisoDenegadoError("cierra_sector")
        if actor.sector_id is None:
            raise PermisoDenegadoError("cierra_sector")

        incidente = await self._incidente_repo.get_with_relations(incidente_id)
        if incidente is None:
            raise EntityNotFoundError("Incidente", incidente_id)

        # Idempotencia (ILC-001): si el sector del actor ya cerro, la operacion es
        # un no-op exitoso. Se resuelve ANTES del chequeo de alcance, porque tras
        # el cierre el incidente deja de estar visible para ese sector.
        cerrados = set(await self._cierre_repo.listar_sector_ids(incidente.id))
        if actor.sector_id in cerrados:
            return incidente

        if alcance is not None and not alcance.permite_incidente(incidente):
            raise EntityNotFoundError("Incidente", incidente_id)

        _, creado = await self._cierre_repo.registrar_cierre(
            incidente_id=incidente.id,
            sector_id=actor.sector_id,
            actor_empleado_id=actor.id,
        )
        if creado:
            await self._evento_repo.registrar(
                incidente_id=incidente.id,
                tipo=TIPO_CIERRE_SECTOR,
                actor_empleado_id=actor.id,
                sector_id=actor.sector_id,
            )
        await self._aplicar_transicion_terminal(incidente)
        return await self._incidente_repo.get_with_relations(incidente.id)  # type: ignore[return-value]

    # ── Cierre global (ILC-002) ───────────────────────────────────────────────

    async def cerrar_global(
        self,
        incidente_id: int,
        actor: Empleado | None,
        alcance: "AlcanceIncidentes | None" = None,
    ) -> Incidente:
        """
        Cierra globalmente el incidente `mesa_de_ayuda`: todos los sectores + terminal.

        Idempotente: si el incidente ya esta cerrado, no duplica cierres ni eventos.
        Un incidente sin sectores asignados se lleva a `cerrado` sin filas de sector.
        """
        politica = self._politica(actor)
        if not politica.cierra_global:
            raise PermisoDenegadoError("cierra_global")
        assert actor is not None  # garantizado por _politica

        incidente = await self._cargar(incidente_id, alcance)
        if incidente.estado is not None and incidente.estado.es_terminal:
            # Idempotente: ya esta globalmente cerrado.
            return await self._incidente_repo.get_with_relations(incidente.id)  # type: ignore[return-value]

        estado_anterior = incidente.estado.nombre if incidente.estado else None
        for sector_id in sorted(incidente.sector_ids):
            await self._cierre_repo.registrar_cierre(
                incidente_id=incidente.id,
                sector_id=sector_id,
                actor_empleado_id=actor.id,
            )

        terminal = await self._estado_repo.get_terminal()
        if terminal is not None and incidente.estado_id != terminal.id:
            incidente.estado_id = terminal.id
            # Refrescar la relacion cargada (evita serializar un estado obsoleto).
            incidente.estado = terminal
            self._session.add(incidente)
            await self._session.flush()

        await self._evento_repo.registrar(
            incidente_id=incidente.id,
            tipo=TIPO_CIERRE_GLOBAL,
            actor_empleado_id=actor.id,
            estado_anterior=estado_anterior,
            estado_nuevo=terminal.nombre if terminal is not None else None,
        )
        return await self._incidente_repo.get_with_relations(incidente.id)  # type: ignore[return-value]

    # ── Reapertura (ILC-004) ──────────────────────────────────────────────────

    async def rehabilitar(
        self,
        incidente_id: int,
        actor: Empleado | None,
        alcance: "AlcanceIncidentes | None" = None,
    ) -> Incidente:
        """
        Rehabilita (reabre) un incidente cerrado: limpia los cierres por sector,
        lo devuelve a `en proceso` y registra el evento de reapertura.

        Exclusiva del rol con `reabre` (mesa de ayuda); 403 en otro caso. Rechaza
        la reapertura de un incidente que no esta cerrado (422).
        """
        politica = self._politica(actor)
        if not politica.reabre:
            raise PermisoDenegadoError("reabre")
        assert actor is not None

        incidente = await self._cargar(incidente_id, alcance)
        if incidente.estado is None or not incidente.estado.es_terminal:
            raise IncidentValidationError(
                "Solo se puede rehabilitar un incidente cerrado."
            )

        estado_anterior = incidente.estado.nombre
        await self._cierre_repo.eliminar_por_incidente(incidente.id)
        # El Core DELETE no toca la coleccion ORM ya cargada: se expira para que
        # la recarga posterior no referencie instancias eliminadas.
        self._session.expire(incidente, ["cierres_sector"])

        nuevo = await self._estado_repo.get_by_nombre(ESTADO_REAPERTURA)
        if nuevo is None:
            raise IncidentValidationError(
                f"Estado '{ESTADO_REAPERTURA}' no encontrado en el catalogo."
            )
        incidente.estado_id = nuevo.id
        incidente.estado = nuevo
        self._session.add(incidente)
        await self._session.flush()

        await self._evento_repo.registrar(
            incidente_id=incidente.id,
            tipo=TIPO_REAPERTURA,
            actor_empleado_id=actor.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo.nombre,
        )
        return incidente

    # ── Edicion de estado (ILC-005) ───────────────────────────────────────────

    async def editar_estado(
        self,
        incidente_id: int,
        nombre_estado: str,
        actor: Empleado | None,
        alcance: "AlcanceIncidentes | None" = None,
    ) -> Incidente:
        """
        Fija el estado del incidente entre los valores NO terminales.

        `cerrado` (o cualquier valor fuera de `ESTADOS_EDITABLES`) produce 422.
        El rol debe tener `edita_estado` (403 si no) y el incidente debe estar
        dentro de su alcance (404 si no).
        """
        politica = self._politica(actor)
        if not politica.edita_estado:
            raise PermisoDenegadoError("edita_estado")
        assert actor is not None

        if nombre_estado not in ESTADOS_EDITABLES:
            raise IncidentValidationError(
                "El estado no es editable; solo 'en proceso', 'en espera' o "
                "'resuelto'."
            )

        incidente = await self._cargar(incidente_id, alcance)
        if incidente.estado is not None and incidente.estado.es_terminal:
            raise IncidenteCerradoError(incidente_id)

        estado_anterior = incidente.estado.nombre if incidente.estado else None
        nuevo = await self._estado_repo.get_by_nombre(nombre_estado)
        if nuevo is None:
            raise IncidentValidationError(
                f"Estado '{nombre_estado}' no encontrado en el catalogo."
            )
        incidente.estado_id = nuevo.id
        incidente.estado = nuevo
        self._session.add(incidente)
        await self._session.flush()

        await self._evento_repo.registrar(
            incidente_id=incidente.id,
            tipo=TIPO_CAMBIO_ESTADO,
            actor_empleado_id=actor.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo.nombre,
        )
        return incidente

    # ── Auxiliares privados ───────────────────────────────────────────────────

    def _politica(self, actor: Empleado | None):
        politica = politica_de_rol(actor.rol) if actor is not None else None
        if politica is None:
            raise PermisoDenegadoError("rol_desconocido")
        return politica

    async def _cargar(
        self, incidente_id: int, alcance: "AlcanceIncidentes | None"
    ) -> Incidente:
        incidente = await self._incidente_repo.get_with_relations(incidente_id)
        if incidente is None or (
            alcance is not None and not alcance.permite_incidente(incidente)
        ):
            raise EntityNotFoundError("Incidente", incidente_id)
        return incidente

    async def _aplicar_transicion_terminal(self, incidente: Incidente) -> None:
        """Lleva el incidente a `cerrado` si TODOS sus sectores cerraron (ILC-003)."""
        conjunto = incidente.sector_ids
        if not conjunto:
            return
        cerrados = set(await self._cierre_repo.listar_sector_ids(incidente.id))
        if not conjunto <= cerrados:
            return
        terminal = await self._estado_repo.get_terminal()
        if terminal is not None and incidente.estado_id != terminal.id:
            incidente.estado_id = terminal.id
            # Refrescar la relacion cargada (evita serializar un estado obsoleto).
            incidente.estado = terminal
            self._session.add(incidente)
            await self._session.flush()
