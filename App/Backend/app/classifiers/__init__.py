"""Paquete de clasificadores del pipeline de clasificacion.

El import de los submodulos es PEREZOSO (PEP 562, `__getattr__` de modulo): importar
el paquete NO debe ejecutar los efectos colaterales de sus submodulos. En particular,
`gemini_classifier` lee el prompt del disco al importarse (`_PROMPT_TEMPLATE =
_load_prompt()`); si el paquete lo importara de forma anticipada, cualquier importador
(por ejemplo el arnes de evaluacion, que importa `app.classifiers.deterministic` para
seleccionar los casos offline) congelaria el prompt vigente antes de poder fijar
`GEMINI_PROMPT_PATH` para el brazo sin reglas. La resolucion perezosa elimina ese
efecto colateral y preserva la API publica del paquete.
"""

from importlib import import_module

__all__ = [
    "BaseClassifier",
    "DeterministicClassifier",
    "GeminiClassifier",
    "HybridClassifier",
]

#: Mapa nombre publico -> submodulo que lo define. El submodulo se importa al primer acceso.
_SUBMODULOS = {
    "BaseClassifier": "app.classifiers.base",
    "DeterministicClassifier": "app.classifiers.deterministic",
    "GeminiClassifier": "app.classifiers.gemini_classifier",
    "HybridClassifier": "app.classifiers.hybrid",
}


def __getattr__(nombre: str):
    """Importa el submodulo de un nombre publico solo cuando se accede a el (PEP 562)."""
    try:
        submodulo = _SUBMODULOS[nombre]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {nombre!r}") from None
    valor = getattr(import_module(submodulo), nombre)
    globals()[nombre] = valor
    return valor
