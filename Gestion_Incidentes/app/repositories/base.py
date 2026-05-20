"""
Repositorio base genérico para operaciones CRUD asíncronas.

Responsabilidad:
    Provee una abstracción sobre SQLAlchemy que encapsula las operaciones
    de persistencia más comunes (leer por ID, listar, crear, eliminar).
    Los repositorios concretos heredan de esta clase y obtienen estas
    operaciones de forma gratuita, pudiendo agregar consultas específicas
    de su dominio sin duplicar código.

Patrón Repository (SOLID):
    Al centralizar todo el acceso a datos en repositorios, la lógica de
    negocio de la capa de servicios permanece desacoplada de SQLAlchemy.
    Esto facilita el testing (se puede mockear el repositorio), la migración
    a otro ORM, y el cumplimiento del principio de responsabilidad única.

Diseño genérico:
    La clase usa Generic[ModelT] con TypeVar bound=Base, lo que permite
    que el type checker infiera el tipo correcto en cada repositorio concreto
    sin necesidad de casteos manuales.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.exceptions import EntityNotFoundError

# TypeVar vinculado a Base garantiza que solo se pueda usar con modelos ORM
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Repositorio genérico asíncrono con operaciones CRUD fundamentales.

    Las subclases deben declarar el atributo de clase 'model' apuntando
    al modelo ORM correspondiente. Todas las operaciones de esta clase
    operan sobre ese modelo automáticamente.

    Ejemplo de uso:
        class SectorRepository(BaseRepository[Sector]):
            model = Sector
            # Las operaciones get_by_id, create, etc. están disponibles sin código adicional.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa el repositorio con la sesión de base de datos activa.

        La sesión es provista por la dependencia get_db_session() de FastAPI
        y es compartida por todos los repositorios que participan en la misma
        solicitud HTTP, garantizando atomicidad transaccional.

        Args:
            session: Sesión asíncrona de SQLAlchemy para la solicitud actual.
        """
        self._session = session

    async def get_by_id(self, entity_id: int) -> ModelT:
        """
        Recupera una entidad por su clave primaria.

        Args:
            entity_id: Identificador único de la entidad.

        Returns:
            Instancia del modelo ORM.

        Raises:
            EntityNotFoundError: Si no existe ningún registro con ese ID.
        """
        instance = await self._session.get(self.model, entity_id)
        if instance is None:
            raise EntityNotFoundError(self.model.__name__, entity_id)
        return instance

    async def get_or_none(self, entity_id: int) -> ModelT | None:
        """
        Recupera una entidad por su clave primaria sin lanzar excepción si no existe.

        Útil cuando la ausencia del registro es un caso de negocio válido
        y no constituye un error (por ejemplo, resolución opcional de FK).

        Args:
            entity_id: Identificador único de la entidad.

        Returns:
            Instancia del modelo ORM o None si no existe.
        """
        return await self._session.get(self.model, entity_id)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """
        Lista todos los registros de la tabla con paginación básica.

        Diseñado para tablas de catálogo de tamaño acotado.
        Para listados complejos con filtros, implementar métodos específicos
        en el repositorio concreto.

        Args:
            limit:  Cantidad máxima de registros a retornar.
            offset: Cantidad de registros a saltear (para paginación).

        Returns:
            Lista de instancias ORM.
        """
        result = await self._session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelT:
        """
        Crea un nuevo registro en la base de datos.

        Utiliza flush() en lugar de commit() para integrar la operación
        en la transacción gestionada por get_db_session(), permitiendo
        que múltiples operaciones de escritura formen una unidad atómica.

        Args:
            **kwargs: Atributos del modelo a asignar al nuevo registro.

        Returns:
            Instancia del modelo ORM recién creada con ID asignado.
        """
        instance = self.model(**kwargs)
        self._session.add(instance)
        # flush() envía la sentencia SQL sin confirmar la transacción,
        # lo que genera el ID autoincrementado y permite usarlo inmediatamente
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, entity_id: int) -> None:
        """
        Elimina un registro de la base de datos por su ID.

        Args:
            entity_id: Identificador del registro a eliminar.

        Raises:
            EntityNotFoundError: Si no existe ningún registro con ese ID.
        """
        instance = await self.get_by_id(entity_id)
        await self._session.delete(instance)
        await self._session.flush()
