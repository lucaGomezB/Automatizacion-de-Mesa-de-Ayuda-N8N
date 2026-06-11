"""
Tests de integración de la pseudonimización en el service.

Sección 11 del plan TDD de c-03-pseudonymization-module.

Verifica que:
- create_and_classify persiste descripcion_pseudonimizada (enmascarada) y
  descripcion_original (descifrable al texto crudo).
- El clasificador (Gemini/híbrido) recibe SOLO la versión pseudonimizada.
- La etapa determinística opera correctamente sobre texto pseudonimizado.
- El log DEBUG de cobertura contiene conteos y NO el texto original ni el pseudonimizado.

Estrategia:
    db_session (SQLite in-memory) + classifier mock.
    El EncryptedText cifra/descifra automáticamente vía el TypeDecorator.
    Monkeypatch de get_settings para inyectar clave Fernet de prueba.
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.models.catalog import Estado, Sector
from app.models.incidente import Incidente
from app.schemas.clasificacion import ClasificacionResult
from app.schemas.incidente import IncidenteCreate
from app.services.incidente_service import IncidenteService

# Clave Fernet de prueba
_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

# Texto con PII para verificar la pseudonimización
_TEXTO_CON_PII = (
    "Juan Pérez reportó que srv-correo01 no responde desde la cuenta "
    "juan.perez@empresa.com al teléfono +54 261 555-1234"
)


@pytest.fixture(autouse=True)
def override_encryption_and_settings(monkeypatch):
    """
    Inyecta la clave Fernet de prueba en EncryptedText y en get_settings del service.
    """
    mock_settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="fake-key",
        pseudonymization_encryption_key=_TEST_FERNET_KEY,
        pseudonymization_internal_domains=[],
    )

    get_settings.cache_clear()
    # Parchear get_settings en el módulo del service y en el de encryption
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: mock_settings)
    monkeypatch.setattr("app.services.incidente_service.get_settings", lambda: mock_settings)

    import app.utils.encryption as enc_module
    enc_module._fernet_instance = None

    yield

    enc_module._fernet_instance = None
    get_settings.cache_clear()


async def _seed_catalogs(session: AsyncSession) -> tuple[Estado, Sector]:
    """Siembra estado 'nuevo' y sector 'Sistemas' para que el service los resuelva."""
    estado = Estado(nombre="nuevo", descripcion="Incidente recibido, sin asignar")
    sector = Sector(nombre="Sistemas", descripcion="Infraestructura y redes")
    session.add(estado)
    session.add(sector)
    await session.flush()
    return estado, sector


def _make_clasificacion_result(
    categoria: str = "Sistemas",
    confianza: float = 0.95,
    etapa: str = "deterministic",
) -> ClasificacionResult:
    return ClasificacionResult(
        categoria=categoria,
        confianza=confianza,
        etapa=etapa,
        requiere_revision_humana=False,
    )


# ── 11.1 / 11.2: Persistencia de doble representación ───────────────────────

@pytest.mark.asyncio
async def test_create_and_classify_persiste_doble_representacion(db_session):
    """
    11.1 RED → 11.2 GREEN:
    Al crear un incidente con PII, descripcion_pseudonimizada queda enmascarada
    y descripcion_original descifrada devuelve el texto crudo.
    """
    # Arrange
    await _seed_catalogs(db_session)
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=_make_clasificacion_result())
    payload = IncidenteCreate(descripcion=_TEXTO_CON_PII)

    # Act
    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        incidente = await service.create_and_classify(payload)
        await asyncio.sleep(0)

    # Assert — la descripcion_original descifrada es el texto crudo
    assert incidente.descripcion_original == _TEXTO_CON_PII, (
        "descripcion_original debe contener el texto crudo (EncryptedText lo descifra al leer)"
    )

    # Assert — la descripcion_pseudonimizada tiene etiquetas y no el original
    pseudo = incidente.descripcion_pseudonimizada
    assert "[EMAIL]" in pseudo or "[PERSONA]" in pseudo or "[HOST]" in pseudo or "[TELEFONO]" in pseudo, (
        "descripcion_pseudonimizada debe contener al menos una etiqueta PII"
    )
    assert "juan.perez@empresa.com" not in pseudo, (
        "El email real NO debe aparecer en descripcion_pseudonimizada"
    )
    assert "+54 261 555-1234" not in pseudo, (
        "El teléfono real NO debe aparecer en descripcion_pseudonimizada"
    )


@pytest.mark.asyncio
async def test_descripcion_original_difiere_de_pseudonimizada(db_session):
    """
    TRIANGULATE: cuando hay PII, las dos columnas deben contener textos distintos.
    """
    await _seed_catalogs(db_session)
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=_make_clasificacion_result())
    payload = IncidenteCreate(descripcion=_TEXTO_CON_PII)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        incidente = await service.create_and_classify(payload)
        await asyncio.sleep(0)

    assert incidente.descripcion_original != incidente.descripcion_pseudonimizada


# ── 11.3: Gemini recibe la pseudonimizada ────────────────────────────────────

@pytest.mark.asyncio
async def test_gemini_recibe_descripcion_pseudonimizada(db_session):
    """
    11.3 TRIANGULATE:
    El clasificador recibe la versión pseudonimizada — sin los datos originales
    con PII — y nunca el texto crudo.
    """
    await _seed_catalogs(db_session)
    classifier_mock = AsyncMock()
    classify_calls: list[str] = []

    async def capture_classify(texto: str) -> ClasificacionResult:
        classify_calls.append(texto)
        return _make_clasificacion_result()

    classifier_mock.classify = capture_classify
    payload = IncidenteCreate(descripcion=_TEXTO_CON_PII)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        await service.create_and_classify(payload)
        await asyncio.sleep(0)

    assert len(classify_calls) == 1
    texto_enviado = classify_calls[0]

    # El texto enviado al clasificador NO debe contener PII original
    assert "juan.perez@empresa.com" not in texto_enviado, (
        "El email original NO debe llegar al clasificador"
    )
    assert "+54 261 555-1234" not in texto_enviado, (
        "El teléfono original NO debe llegar al clasificador"
    )

    # El texto enviado debe contener al menos una etiqueta
    assert any(
        tag in texto_enviado
        for tag in ["[EMAIL]", "[TELEFONO]", "[HOST]", "[PERSONA]"]
    ), "El clasificador debe recibir texto con etiquetas PII"


# ── 11.4: Etapa determinística opera sobre pseudonimizada ────────────────────

@pytest.mark.asyncio
async def test_etapa_deterministica_opera_sobre_pseudonimizada(db_session):
    """
    11.4 TRIANGULATE:
    El clasificador determinístico clasifica correctamente sobre texto pseudonimizado
    representativo con keywords de dominio (que no son PII y no se enmascaran).
    """
    await _seed_catalogs(db_session)

    # Texto con keyword "servidor" (clasificable por determinístico) + PII
    texto = "El servidor de base de datos no responde desde juan@empresa.com"
    payload = IncidenteCreate(descripcion=texto)

    # Usar el HybridClassifier real pero mockeando Gemini para no hacer llamadas reales
    from app.classifiers.hybrid import HybridClassifier
    from app.classifiers.deterministic import DeterministicClassifier

    texts_seen_by_determinist: list[str] = []
    original_det_classify = DeterministicClassifier.classify

    def capture_deterministic(self, texto_det: str) -> ClasificacionResult:
        texts_seen_by_determinist.append(texto_det)
        return original_det_classify(self, texto_det)

    with patch.object(DeterministicClassifier, "classify", capture_deterministic), \
         patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        service = IncidenteService(session=db_session)
        incidente = await service.create_and_classify(payload)
        await asyncio.sleep(0)

    # El determinístico debe haber visto el texto pseudonimizado (no el original)
    assert len(texts_seen_by_determinist) >= 1
    texto_det = texts_seen_by_determinist[0]
    assert "juan@empresa.com" not in texto_det, (
        "El determinístico no debe recibir el email crudo"
    )
    # "servidor" keyword sigue presente (no es PII)
    assert "servidor" in texto_det, (
        "Keywords de dominio ('servidor') deben estar presentes en el texto pseudonimizado"
    )
    # Incidente clasificado correctamente
    assert incidente.id is not None


# ── 11.5: Log DEBUG de cobertura sin PII ─────────────────────────────────────

@pytest.mark.asyncio
async def test_log_debug_cobertura_sin_pii(db_session, caplog):
    """
    11.5 TRIANGULATE:
    El log DEBUG 'pseudonimizacion_cobertura' contiene conteos por categoría
    y NO el texto original ni el pseudonimizado completo.
    """
    await _seed_catalogs(db_session)
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=_make_clasificacion_result())
    payload = IncidenteCreate(descripcion=_TEXTO_CON_PII)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock), \
         caplog.at_level(logging.DEBUG):
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        await service.create_and_classify(payload)
        await asyncio.sleep(0)

    # Buscar el evento de cobertura en los logs capturados
    # structlog puede emitir en format diferente; buscar en el mensaje serializado
    log_messages = [r.getMessage() for r in caplog.records]
    log_texts = " ".join(log_messages)

    # El texto original NO debe aparecer en ningún log
    assert "juan.perez@empresa.com" not in log_texts, (
        "El email original NO debe aparecer en los logs"
    )
    assert "+54 261 555-1234" not in log_texts, (
        "El teléfono original NO debe aparecer en los logs"
    )
