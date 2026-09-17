"""
Utilidades de calendario de negocio (zona horaria America/Argentina/Buenos_Aires).

Responsabilidad:
    Centraliza la conversion entre el dia calendario de negocio (UTC-3) y los
    limites UTC con los que se consultan los timestamps almacenados.

Por que existe este modulo:
    Los timestamps de las entidades (por ejemplo Incidente.created_at) se
    persisten en UTC (DateTime(timezone=True), default utcnow()). El dashboard,
    en cambio, razona en terminos de la jornada laboral de la empresa:
    America/Argentina/Buenos_Aires (UTC-3).

    Comparar una fecha local contra un instante UTC es ambiguo cerca de la
    medianoche: entre las 21:00 y las 24:00 de Buenos Aires la fecha UTC ya
    pertenece al dia calendario siguiente. Usar `date.today()` (fecha local del
    servidor) como limite de un rango contra columnas UTC desplaza el dia de
    negocio y excluye incidentes recientes. Estas funciones eliminan esa
    ambiguedad resolviendo el rango en la zona de negocio y convirtiendolo a
    instantes UTC con limites semiabiertos.
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# Zona horaria de negocio: la jornada laboral de la empresa es UTC-3.
BUSINESS_TZ = ZoneInfo("America/Argentina/Buenos_Aires")


def business_today(now: datetime | None = None) -> date:
    """
    Retorna el dia calendario de negocio correspondiente a `now`.

    Args:
        now: Instante de referencia. Si es None se usa el instante actual en
            UTC. Se acepta la inyeccion explicita para que el comportamiento
            sea determinista en los tests.

    Returns:
        La fecha del dia de negocio en America/Argentina/Buenos_Aires.
    """
    moment = now if now is not None else datetime.now(timezone.utc)
    return moment.astimezone(BUSINESS_TZ).date()


def business_range_to_utc(desde: date, hasta: date) -> tuple[datetime, datetime]:
    """
    Convierte un rango de dias de negocio a sus limites UTC semiabiertos.

    El rango resultante es [desde 00:00 BA, (hasta + 1 dia) 00:00 BA), con el
    limite superior EXCLUSIVO. Expresarlo asi permite comparar directamente
    contra columnas DateTime(timezone=True) sin ambiguedad de zona horaria:
    un incidente creado en la ventana 21:00-24:00 BA del dia `hasta` queda
    incluido porque su instante UTC sigue siendo menor que las 00:00 BA del
    dia siguiente.

    Args:
        desde: Primer dia de negocio del rango (inclusivo).
        hasta: Ultimo dia de negocio del rango (inclusivo en terminos de
            calendario, pero representado por un limite UTC exclusivo).

    Returns:
        Tupla (lower, upper_exclusive) de datetimes con zona horaria UTC.
    """
    next_day = hasta + timedelta(days=1)

    # Se construye cada limite a las 00:00 en la zona de negocio y recien
    # despues se convierte a UTC. Calcular la medianoche directamente en UTC
    # reintroduciria el desfase que este modulo elimina.
    lower = datetime(desde.year, desde.month, desde.day, tzinfo=BUSINESS_TZ)
    upper_exclusive = datetime(
        next_day.year, next_day.month, next_day.day, tzinfo=BUSINESS_TZ
    )

    return lower.astimezone(timezone.utc), upper_exclusive.astimezone(timezone.utc)
