"""
Tests unitarios del clasificador determinístico basado en reglas.

Responsabilidad:
    Verifica el comportamiento del DeterministicClassifier sobre los casos
    canónicos del dominio, los invariantes de la fórmula de confianza, y la
    robustez ante entradas de baja señal (sin keywords relevantes).

    Estos tests no realizan llamadas de red ni acceden a la base de datos,
    por lo que son independientes del entorno de despliegue y pueden
    ejecutarse en cualquier máquina sin configuración adicional.

Casos de test documentados:
    - Los tres ejemplos canónicos del prompt de Gemini (docs/prompt_gemini.txt)
      deben clasificarse correctamente con el clasificador determinístico.
    - La confianza siempre debe estar en el rango normalizado [0.0, 1.0].
    - El sistema debe retornar un resultado válido incluso sin keywords.
"""

import pytest

from app.classifiers.deterministic import DeterministicClassifier


@pytest.fixture
def classifier() -> DeterministicClassifier:
    """
    Fixture que provee una instancia del clasificador determinístico para los tests.
    Se crea una vez por función de test para garantizar el aislamiento del estado.
    """
    return DeterministicClassifier()


@pytest.mark.asyncio
async def test_sistemas_server_crash(classifier: DeterministicClassifier) -> None:
    """
    Verifica la clasificación correcta del ejemplo canónico de Sistemas.

    El ejemplo es el mismo utilizado en el prompt de Gemini:
    "Se cayó el servidor de correo. No pueden conectarse los clientes de Outlook. Error SMTP timeout."
    Debe clasificarse como "Sistemas" con confianza positiva.
    """
    result = await classifier.classify(
        "Se cayó el servidor de correo. No pueden conectarse los clientes de Outlook. Error SMTP timeout."
    )
    assert result.categoria == "Sistemas"
    assert result.confianza > 0.0
    assert result.etapa == "deterministic"


@pytest.mark.asyncio
async def test_soporte_tecnico_printer(classifier: DeterministicClassifier) -> None:
    """
    Verifica la clasificación correcta del ejemplo canónico de Soporte Técnico.

    Ejemplo del prompt: "Mi impresora no imprime. Sale papel atascado. Código de error 13."
    Debe clasificarse como "Soporte Técnico" con confianza positiva.
    """
    result = await classifier.classify(
        "Mi impresora no imprime. Sale papel atascado. Código de error 13."
    )
    assert result.categoria == "Soporte Técnico"
    assert result.confianza > 0.0


@pytest.mark.asyncio
async def test_operaciones_room_booking(classifier: DeterministicClassifier) -> None:
    """
    Verifica la clasificación correcta del ejemplo canónico de Operaciones.

    Ejemplo del prompt: "Necesitamos reservar una sala de 15 personas para reunión..."
    Debe clasificarse como "Operaciones" con confianza positiva.
    """
    result = await classifier.classify(
        "Necesitamos reservar una sala de 15 personas para reunión el próximo miércoles a las 14 horas."
    )
    assert result.categoria == "Operaciones"
    assert result.confianza > 0.0


@pytest.mark.asyncio
async def test_confidence_is_normalised(classifier: DeterministicClassifier) -> None:
    """
    Verifica que la confianza esté siempre en el rango normalizado [0.0, 1.0].

    Texto con múltiples keywords de Soporte Técnico: aunque haya muchos matches,
    la fórmula de normalización debe garantizar que la confianza no supere 1.0.
    """
    result = await classifier.classify("impresora teclado mouse pantalla laptop periférico")
    assert 0.0 <= result.confianza <= 1.0


@pytest.mark.asyncio
async def test_empty_description_returns_result(classifier: DeterministicClassifier) -> None:
    """
    Verifica que el clasificador retorne un resultado válido incluso sin keywords reconocidas.

    Cuando no hay matches, todos los scores son 0. La fórmula con epsilon
    debe seleccionar una categoría y retornar confianza cercana a 0.5
    (sin señal diferenciadora). El resultado debe ser un ClasificacionResult válido.
    """
    result = await classifier.classify("x")
    # La categoría debe ser una de las tres válidas del dominio
    assert result.categoria in {"Sistemas", "Operaciones", "Soporte Técnico"}
    # La confianza debe estar en el rango válido incluso sin señal
    assert 0.0 <= result.confianza <= 1.0
