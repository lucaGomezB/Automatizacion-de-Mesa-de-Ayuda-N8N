"""
Tests del numero de incidente canonico y legible (C-53, OQ1 / design D1).

Contrato:
    - Existe UN unico punto de derivacion del numero: `formatear_numero_incidente(id)`
      (hoy `str(id)`), de modo que el prefijo de negocio futuro sea un cambio de un solo
      lugar.
    - `IncidenteRead` expone el campo normalizado `numero_incidente` (string), que el
      backend retorna en el alta y el workflow propaga en sus notificaciones. NO se expone
      el `id` crudo como numero al usuario final.

Strict TDD: cada grupo refleja un ciclo RED -> GREEN -> TRIANGULATE.
"""

from datetime import datetime, timezone

from app.schemas.catalog import EstadoRead
from app.schemas.incidente import IncidenteRead
from app.utils.numero_incidente import formatear_numero_incidente


def _read(incidente_id: int) -> IncidenteRead:
    """Construye un IncidenteRead minimo para el id dado."""
    return IncidenteRead(
        id=incidente_id,
        descripcion_pseudonimizada="El servidor [HOST] no responde",
        prioridad="media",
        requiere_revision_humana=False,
        created_at=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        sector=None,
        sectores_adicionales=[],
        estado=EstadoRead(id=1, nombre="nuevo", descripcion=None, es_terminal=False),
        canal_origen=None,
    )


# ---------------------------------------------------------------------------
# Grupo 1 — Punto unico de derivacion (OQ1)
# ---------------------------------------------------------------------------


def test_formatear_numero_incidente_devuelve_string():
    """RED -> GREEN: el numero canonico es el string del id persistido."""
    assert formatear_numero_incidente(123) == "123"
    assert isinstance(formatear_numero_incidente(123), str)


def test_formatear_numero_incidente_es_punto_unico():
    """TRIANGULATE: varios ids derivan de la MISMA funcion, sin logica por canal."""
    for value in (1, 42, 999999):
        assert formatear_numero_incidente(value) == str(value)


# ---------------------------------------------------------------------------
# Grupo 2 — IncidenteRead expone `numero_incidente` (OQ1)
# ---------------------------------------------------------------------------


def test_incidente_read_expone_numero_incidente_string():
    """RED -> GREEN: el alta/detalle expone `numero_incidente` como string."""
    read = _read(123)
    assert read.numero_incidente == "123"
    assert isinstance(read.numero_incidente, str)


def test_incidente_read_serializa_numero_incidente():
    """TRIANGULATE: el campo normalizado viaja en la serializacion (response del alta)."""
    dump = _read(7).model_dump()
    assert dump["numero_incidente"] == "7"


def test_numero_incidente_no_es_el_id_crudo():
    """TRIANGULATE: el contrato expone el numero normalizado, no el `id` crudo."""
    read = _read(7)
    assert read.numero_incidente == str(read.id)
    assert read.numero_incidente != read.id
