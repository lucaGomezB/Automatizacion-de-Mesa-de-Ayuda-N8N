"""
Tests del contrato de instrumentacion temporal end-to-end (C-39).

Cubre tres capas del contrato de medicion:
    - Modelo ORM `Incidente`: expone `ingresado_en` y `persistido_en` nullable,
      sin `onupdate` (inmutabilidad de la persistencia confirmada).
    - Schema `IncidenteCreate`: acepta `ingresado_en` ISO-8601 con zona horaria,
      lo normaliza a UTC, rechaza valores naive y valores futuros mas alla de la
      tolerancia configurable (30 s por defecto).
    - Schema `IncidenteRead`: expone ambos instantes y la latencia derivada
      `latencia_e2e_ms`; la latencia es nula si falta un instante y NUNCA se
      reporta como medicion valida cuando es negativa (se marca anomalia).

Strict TDD: cada grupo refleja un ciclo RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.models.incidente import Incidente
from app.schemas.catalog import EstadoRead
from app.schemas.incidente import IncidenteCreate, IncidenteListItem, IncidenteRead

_DESCRIPCION = "El servidor de base de datos principal no responde desde la manana."


def _read(
    *,
    ingresado_en: datetime | None,
    persistido_en: datetime | None,
) -> IncidenteRead:
    """Construye un IncidenteRead minimo con los dos instantes dados."""
    return IncidenteRead(
        id=1,
        descripcion_pseudonimizada="El servidor [HOST] no responde",
        prioridad="media",
        requiere_revision_humana=False,
        created_at=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        sector=None,
        sectores_adicionales=[],
        estado=EstadoRead(id=1, nombre="nuevo", descripcion=None, es_terminal=False),
        canal_origen=None,
        ingresado_en=ingresado_en,
        persistido_en=persistido_en,
    )


def _make_list_item(
    *,
    ingresado_en: datetime | None,
    persistido_en: datetime | None,
) -> IncidenteListItem:
    """Construye un IncidenteListItem minimo con los dos instantes dados."""
    return IncidenteListItem(
        id=1,
        prioridad="media",
        requiere_revision_humana=False,
        created_at=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        sector=None,
        estado=EstadoRead(id=1, nombre="nuevo", descripcion=None, es_terminal=False),
        ingresado_en=ingresado_en,
        persistido_en=persistido_en,
    )


# ---------------------------------------------------------------------------
# Grupo 1 — Modelo ORM (tarea 1.4)
# ---------------------------------------------------------------------------


def test_modelo_expone_columnas_de_ingreso_y_persistencia():
    """El modelo Incidente mapea `ingresado_en` y `persistido_en` como nullable."""
    columnas = Incidente.__table__.columns
    for nombre in ("ingresado_en", "persistido_en"):
        assert nombre in columnas, (
            f"El modelo Incidente no mapea la columna {nombre!r}"
        )
        assert columnas[nombre].nullable is True, (
            f"La columna {nombre!r} debe ser nullable"
        )


def test_persistido_en_no_tiene_onupdate():
    """`persistido_en` es inmutable: no declara onupdate (a diferencia de updated_at)."""
    columna = Incidente.__table__.columns["persistido_en"]
    assert columna.onupdate is None, (
        "persistido_en no debe recalcularse en cada UPDATE (onupdate); "
        "un PATCH del operador destruiria la medicion"
    )


# ---------------------------------------------------------------------------
# Grupo 2 — IncidenteCreate.ingresado_en (tareas 2.1 / 2.2)
# ---------------------------------------------------------------------------


def test_ingresado_en_acepta_z_y_normaliza_a_utc():
    """Un valor con sufijo `Z` se acepta y se normaliza a UTC."""
    payload = IncidenteCreate(
        descripcion=_DESCRIPCION,
        ingresado_en="2026-09-19T12:00:00Z",
    )
    assert payload.ingresado_en == datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)
    assert payload.ingresado_en.tzinfo is not None
    assert payload.ingresado_en.utcoffset() == timedelta(0)


def test_ingresado_en_acepta_offset_y_normaliza_a_utc():
    """Un valor con offset explicito se normaliza a UTC."""
    payload = IncidenteCreate(
        descripcion=_DESCRIPCION,
        ingresado_en="2026-09-19T09:00:00-03:00",
    )
    assert payload.ingresado_en == datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)


def test_ingresado_en_rechaza_naive():
    """Un instante sin zona horaria se rechaza con error de validacion."""
    with pytest.raises(ValidationError) as exc:
        IncidenteCreate(descripcion=_DESCRIPCION, ingresado_en="2026-09-19T12:00:00")
    assert "ingresado_en" in str(exc.value), (
        "El error de validacion debe identificar el campo 'ingresado_en'"
    )


def test_ingresado_en_rechaza_futuro_fuera_de_tolerancia():
    """Un instante futuro mas alla de la tolerancia (30 s) se rechaza."""
    futuro = datetime.now(timezone.utc) + timedelta(seconds=60)
    with pytest.raises(ValidationError) as exc:
        IncidenteCreate(descripcion=_DESCRIPCION, ingresado_en=futuro)
    assert "ingresado_en" in str(exc.value)


def test_ingresado_en_acepta_futuro_dentro_de_tolerancia():
    """Un desfase de reloj menor a la tolerancia se acepta."""
    futuro = datetime.now(timezone.utc) + timedelta(seconds=10)
    payload = IncidenteCreate(descripcion=_DESCRIPCION, ingresado_en=futuro)
    assert payload.ingresado_en is not None
    assert payload.ingresado_en.utcoffset() == timedelta(0)


def test_ingresado_en_acepta_nulo():
    """La ausencia del instante no bloquea el alta: queda nulo."""
    payload = IncidenteCreate(descripcion=_DESCRIPCION)
    assert payload.ingresado_en is None


def test_tolerancia_de_futuro_por_defecto_es_30s():
    """La tolerancia configurable tiene por defecto 30 s."""
    from app.config.settings import get_settings

    assert get_settings().timing_future_tolerance_seconds == 30


# ---------------------------------------------------------------------------
# Grupo 3 — IncidenteRead: instantes y latencia derivada (tareas 2.3 / 2.4)
# ---------------------------------------------------------------------------


def test_read_expone_ambos_instantes():
    """IncidenteRead expone `ingresado_en` y `persistido_en`."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    persistido = datetime(2026, 9, 19, 12, 0, 12, 500000, tzinfo=timezone.utc)
    read = _read(ingresado_en=ingresado, persistido_en=persistido)
    assert read.ingresado_en == ingresado
    assert read.persistido_en == persistido


def test_latencia_derivada_en_milisegundos():
    """12.5 s de diferencia derivan 12500 ms."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    persistido = ingresado + timedelta(seconds=12.5)
    read = _read(ingresado_en=ingresado, persistido_en=persistido)
    assert read.latencia_e2e_ms == 12500


def test_latencia_nula_si_falta_ingresado():
    """Sin `ingresado_en` la latencia es nula."""
    read = _read(
        ingresado_en=None,
        persistido_en=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
    )
    assert read.latencia_e2e_ms is None


def test_latencia_nula_si_falta_persistido():
    """Sin `persistido_en` la latencia es nula."""
    read = _read(
        ingresado_en=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        persistido_en=None,
    )
    assert read.latencia_e2e_ms is None


def test_latencia_negativa_no_se_reporta_y_marca_anomalia():
    """Una latencia negativa no se reporta como valida y queda marcada anomalia."""
    ingresado = datetime(2026, 9, 19, 12, 0, 30, tzinfo=timezone.utc)
    persistido = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    read = _read(ingresado_en=ingresado, persistido_en=persistido)
    assert read.latencia_e2e_ms is None, (
        "Una latencia negativa no debe reportarse como medicion valida"
    )
    assert read.latencia_anomala is True, (
        "Una latencia negativa debe quedar marcada como anomalia"
    )


def test_latencia_no_negativa_no_es_anomala():
    """Una latencia valida no marca la bandera de anomalia."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    read = _read(ingresado_en=ingresado, persistido_en=ingresado + timedelta(seconds=1))
    assert read.latencia_anomala is False
    assert read.latencia_e2e_ms == 1000


def test_latencia_cero_no_es_anomala():
    """Una latencia exactamente cero es valida (no negativa)."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    read = _read(ingresado_en=ingresado, persistido_en=ingresado)
    assert read.latencia_e2e_ms == 0
    assert read.latencia_anomala is False


# ---------------------------------------------------------------------------
# Grupo 4 — IncidenteListItem: instantes y latencia derivada (c-48)
#
# La proyeccion de listado debe exponer los dos instantes fuente y derivar la
# latencia con la misma logica que el detalle. Cubre los escenarios de la delta
# spec `e2e-timing-instrumentation`: exposicion en listado, instantes ausentes,
# paridad detalle/listado y anomalia visible en el listado.
# ---------------------------------------------------------------------------


def test_list_item_expone_ambos_instantes():
    """IncidenteListItem expone `ingresado_en` y `persistido_en`."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    persistido = datetime(2026, 9, 19, 12, 0, 12, 500000, tzinfo=timezone.utc)
    item = _make_list_item(ingresado_en=ingresado, persistido_en=persistido)
    assert item.ingresado_en == ingresado
    assert item.persistido_en == persistido


def test_list_item_latencia_derivada_en_milisegundos():
    """12.5 s de diferencia derivan 12500 ms en la proyeccion de listado."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    persistido = ingresado + timedelta(seconds=12.5)
    item = _make_list_item(ingresado_en=ingresado, persistido_en=persistido)
    assert item.latencia_e2e_ms == 12500


def test_list_item_latencia_nula_si_falta_ingresado():
    """Sin `ingresado_en` la latencia del listado es nula."""
    item = _make_list_item(
        ingresado_en=None,
        persistido_en=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
    )
    assert item.latencia_e2e_ms is None


def test_list_item_latencia_nula_si_falta_persistido():
    """Sin `persistido_en` la latencia del listado es nula."""
    item = _make_list_item(
        ingresado_en=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        persistido_en=None,
    )
    assert item.latencia_e2e_ms is None


def test_list_item_latencia_nula_si_ambos_instantes_son_nulos():
    """Con ambos instantes nulos el item se construye sin error y la latencia es nula."""
    item = _make_list_item(ingresado_en=None, persistido_en=None)
    assert item.latencia_e2e_ms is None
    assert item.latencia_anomala is False


def test_list_item_latencia_negativa_no_se_reporta_y_marca_anomalia():
    """Una latencia negativa en el listado no se reporta como valida y queda marcada."""
    ingresado = datetime(2026, 9, 19, 12, 0, 30, tzinfo=timezone.utc)
    persistido = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    item = _make_list_item(ingresado_en=ingresado, persistido_en=persistido)
    assert item.latencia_e2e_ms is None, (
        "Una latencia negativa no debe reportarse como medicion valida en el listado"
    )
    assert item.latencia_anomala is True, (
        "Una latencia negativa debe quedar marcada como anomalia en el listado"
    )


def test_list_item_latencia_no_negativa_no_es_anomala():
    """Una latencia valida en el listado no marca la bandera de anomalia."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    item = _make_list_item(
        ingresado_en=ingresado, persistido_en=ingresado + timedelta(seconds=1)
    )
    assert item.latencia_anomala is False
    assert item.latencia_e2e_ms == 1000


def test_list_item_latencia_cero_no_es_anomala():
    """Una latencia exactamente cero es valida en el listado (no negativa)."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    item = _make_list_item(ingresado_en=ingresado, persistido_en=ingresado)
    assert item.latencia_e2e_ms == 0
    assert item.latencia_anomala is False


def test_paridad_de_derivacion_entre_detalle_y_listado():
    """El mismo par de instantes deriva la misma latencia en detalle y listado."""
    ingresado = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    persistido = ingresado + timedelta(seconds=7.25)
    read = _read(ingresado_en=ingresado, persistido_en=persistido)
    item = _make_list_item(ingresado_en=ingresado, persistido_en=persistido)
    assert item.latencia_e2e_ms == read.latencia_e2e_ms == 7250
    assert item.latencia_anomala is read.latencia_anomala is False
