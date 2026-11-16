"""
Interfaz abstracta del proveedor de inferencia y su taxonomia de errores (c-227, D1).

Responsabilidad:
    Desacoplar la etapa semantica del clasificador hibrido del SDK de un proveedor
    concreto. La interfaz expone una operacion asincrona de generacion en el nivel
    del TEXTO CRUDO: el clasificador conserva del lado semantico la construccion del
    prompt, la validacion del contrato de respuesta, el reintento acotado y el
    fallback; el proveedor solo envuelve su SDK, arma la configuracion de generacion
    y ejecuta la llamada.

    Los tipos de esta interfaz NO exponen tipos ni excepciones del SDK de ningun
    proveedor. La implementacion concreta traduce los errores de su SDK a la
    taxonomia canonica (transitorio/terminal) para que el bucle de reintento del
    clasificador no dependa de `genai_errors`.

Gobernanza: MEDIUM. Cero llamadas pagas: la interfaz solo define el contrato; el
gate de corrida paga vive en el runner de evaluacion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, runtime_checkable


@dataclass(frozen=True)
class InferenceParams:
    """Parametros de inferencia independientes del proveedor (todos primitivos).

    Solo lleva los parametros de generacion comunes y ajustables: el modelo, los
    parametros calibrados (temperatura, top_p, tokens, candidatos) y el limite de
    latencia por llamada. Los detalles propios de cada API (por ejemplo el modo
    JSON, el schema de respuesta o el presupuesto de razonamiento de Gemini) quedan
    del lado de la implementacion concreta, no del contrato.
    """

    model: str
    temperature: float
    top_p: float
    max_output_tokens: int
    candidate_count: int
    timeout: float


class InferenceProviderError(Exception):
    """Falla canonica del proveedor de inferencia (base de la taxonomia)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InferenceTransientError(InferenceProviderError):
    """Falla transitoria: elegible para reintento acotado.

    Agrupa la indisponibilidad del proveedor (5xx) y los limites de tasa (429).
    """


class InferenceTimeoutError(InferenceTransientError):
    """Timeout del proveedor: transitorio y distinguible para el mensaje final.

    Es una falla transitoria (admite reintento) pero el clasificador la separa para
    reportar `GeminiTimeoutError` (en vez de `GeminiUnavailableError`) al agotar los
    intentos, preservando el contrato de `classification-resilience`.
    """


class InferenceTerminalError(InferenceProviderError):
    """Falla terminal: no admite reintento (peticion, autenticacion, autorizacion)."""


@runtime_checkable
class InferenceProvider(Protocol):
    """Contrato del proveedor de inferencia (nivel de generacion, no de clasificacion).

    El clasificador depende de este Protocol y no de un SDK concreto (D1). Una
    implementacion falsa que cumpla la firma se inyecta sin importar el SDK.
    """

    async def generate(self, *, prompt: str, params: InferenceParams) -> str:
        """Genera y devuelve el texto crudo de la respuesta para `prompt`.

        Args:
            prompt: prompt completo ya construido por la etapa semantica.
            params: parametros de inferencia independientes del proveedor.

        Returns:
            El texto crudo de la respuesta (sin parsear ni validar: eso es
            responsabilidad de la etapa semantica).

        Raises:
            InferenceTransientError: falla reintentable del proveedor.
            InferenceTimeoutError: timeout reintentable de la llamada.
            InferenceTerminalError: falla no reintentable del proveedor.
        """
        ...


class UnknownProviderError(ValueError):
    """El nombre de proveedor configurado no esta registrado (fallo explicito).

    Se levanta en la inicializacion para que el sistema no arranque con un proveedor
    silenciosamente inexistente (spec `inference-provider-abstraction`).
    """


#: Factory de un proveedor: recibe kwargs y devuelve una instancia.
ProviderFactory = Callable[..., InferenceProvider]

#: Nombre del proveedor por defecto (vigente). Lo resuelve el registro a su factory.
PROVEEDOR_POR_DEFECTO = "gemini"

_REGISTRO: dict[str, ProviderFactory] = {}


def registrar_proveedor(nombre: str, factory: ProviderFactory) -> None:
    """Registra (o reemplaza) la factory de un proveedor por nombre.

    El registro arranca con un unico proveedor (Gemini). Se agregan entradas solo
    cuando exista un proveedor real que evaluar (evita sobre-ingenieria, D1).
    """
    _REGISTRO[nombre] = factory


def proveedores_registrados() -> tuple[str, ...]:
    """Nombres de proveedores registrados, en orden alfabetico (para mensajes)."""
    return tuple(sorted(_REGISTRO))


def _factory_gemini(**kwargs: object) -> InferenceProvider:
    """Factory perezosa del proveedor Gemini.

    Importa `GeminiProvider` dentro de la funcion para evitar un import circular
    (`gemini_classifier` importa este modulo al definir su proveedor).
    """
    from app.classifiers.gemini_classifier import GeminiProvider

    return GeminiProvider(**kwargs)


_REGISTRO.setdefault(PROVEEDOR_POR_DEFECTO, _factory_gemini)


def resolver_proveedor(nombre: str, **kwargs: object) -> InferenceProvider:
    """Resuelve el nombre del proveedor a una instancia concreta.

    Args:
        nombre: nombre registrado (por defecto, el proveedor vigente).
        **kwargs: se pasan a la factory del proveedor (por ejemplo `client=`).

    Raises:
        UnknownProviderError: si el nombre no esta registrado.
    """
    factory = _REGISTRO.get(nombre)
    if factory is None:
        raise UnknownProviderError(
            f"proveedor de inferencia desconocido: {nombre!r}. "
            f"Registrados: {list(proveedores_registrados())}."
        )
    return factory(**kwargs)
