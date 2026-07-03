"""
Contrato abstracto del clasificador de incidentes.

Responsabilidad:
    Define la interfaz que deben implementar todas las etapas del pipeline
    de clasificación híbrido. Al depender de esta abstracción (y no de
    implementaciones concretas), el HybridClassifier puede intercambiar
    etapas sin modificar su lógica de orquestación, cumpliendo el principio
    de inversión de dependencias (SOLID-D).

    El contrato establece un invariante de seguridad crítico: las implementaciones
    NO deben lanzar excepciones ante fallas internas. En cambio, deben retornar
    un resultado de fallback con confianza=0.0 y requiere_revision_humana=True.
    Esto garantiza que el pipeline siempre produzca una salida válida, incluso
    ante condiciones de error inesperadas.
"""

from abc import ABC, abstractmethod

from app.schemas.clasificacion import ClasificacionResult


class BaseClassifier(ABC):
    """
    Interfaz abstracta para las etapas del clasificador híbrido.

    Toda clase que participe en el pipeline de clasificación debe heredar
    de esta clase e implementar el método classify(). La separación mediante
    ABC (Abstract Base Class) permite testear el HybridClassifier inyectando
    mocks que cumplan este contrato sin depender de implementaciones reales
    de Gemini o del clasificador determinístico.

    Contrato de seguridad:
        Las implementaciones deben capturar internamente cualquier excepción
        y retornar un ClasificacionResult de fallback. Solo se permite
        propagar excepciones de tipo GeminiTimeoutError y GeminiUnavailableError,
        que son manejadas explícitamente por el HybridClassifier.
    """

    @abstractmethod
    async def classify(self, descripcion: str) -> ClasificacionResult:
        """
        Clasifica la descripción de un incidente y retorna el resultado.

        Args:
            descripcion: Texto pseudonimizado del incidente a clasificar.
                         Se espera texto en español rioplatense según la
                         especificación del Anexo H de la tesis.

        Returns:
            ClasificacionResult con la categoría predicha, la confianza
            asociada, la etapa del pipeline que produjo el resultado y
            el indicador de revisión humana.

        Nota:
            Las implementaciones deben garantizar que ante cualquier falla
            interna (parseo, conexión, validación) se retorne un resultado
            con confianza=0.0 y requiere_revision_humana=True, en lugar
            de propagar la excepción hacia el pipeline orquestador.
        """
        ...
