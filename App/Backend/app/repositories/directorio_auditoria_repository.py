"""
Repositorio de la auditoria durable del directorio (c-153, Tema D, DIR-013).

Responsabilidad:
    Persistir y leer la traza durable de las operaciones del directorio. Es
    APPEND-ONLY por diseno: NO hereda de `BaseRepository` (que expone `delete`)
    y NO declara metodos de edicion ni de borrado. Solo `registrar` escribe y
    `listar_*` lee.

Privacidad:
    Solo se persisten identificadores internos, operacion, resultado, canal e
    instante. El repositorio no recibe ni almacena el contacto en claro.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.directorio_auditoria import DirectorioAuditoria

__all__ = ["DirectorioAuditoriaRepository"]


class DirectorioAuditoriaRepository:
    """Acceso append-only a la tabla `directorio_auditoria`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def registrar(
        self,
        *,
        operacion: str,
        resultado: str,
        empleado_id: int | None = None,
        actor_empleado_id: int | None = None,
        canal: str | None = None,
    ) -> DirectorioAuditoria:
        """
        Inserta una fila de auditoria SIN PII y la deja disponible en la sesion.

        No hace commit: comparte la transaccion de la solicitud. El `flush`
        asigna el id y hace visible la fila dentro de la misma transaccion.
        """
        registro = DirectorioAuditoria(
            operacion=operacion,
            resultado=resultado,
            empleado_id=empleado_id,
            actor_empleado_id=actor_empleado_id,
            canal=canal,
        )
        self._session.add(registro)
        await self._session.flush()
        return registro

    async def listar_por_empleado(
        self, empleado_id: int, *, limit: int = 100
    ) -> list[DirectorioAuditoria]:
        """Devuelve la traza del sujeto indicado, en orden cronologico."""
        result = await self._session.execute(
            select(DirectorioAuditoria)
            .where(DirectorioAuditoria.empleado_id == empleado_id)
            .order_by(DirectorioAuditoria.id)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def listar_recientes(self, *, limit: int = 100) -> list[DirectorioAuditoria]:
        """Devuelve los ultimos eventos de auditoria del directorio."""
        result = await self._session.execute(
            select(DirectorioAuditoria)
            .order_by(DirectorioAuditoria.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
