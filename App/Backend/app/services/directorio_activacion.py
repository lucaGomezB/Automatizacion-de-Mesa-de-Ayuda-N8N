"""
Mecanismo de activacion deliberada y auditada de datos reales del directorio.

Responsabilidad (c-153, Tema F — DIR-014):
    Reemplaza la compuerta historica "sin mecanismo de activacion" por un
    procedimiento EXPLICITO y AUDITABLE que habilita el uso de datos personales
    reales en el directorio. El mecanismo esta gobernado por:

        (a) un gate de entorno (`DIRECTORY_ACTIVATION_APPROVAL_ARTIFACT`), y
        (b) un artefacto de aprobacion humana HIGH registrado de forma
            verificable (`docs/directorio-evidencia-cumplimiento.md`, seccion 4).

    Esta BLOQUEADO POR DEFECTO: sin artefacto de aprobacion valido no hay
    activacion, y el directorio permanece en modo sintetico. NO existe un
    interruptor de runtime oculto (ni flag booleano de `Settings` ni endpoint
    HTTP): la unica via es invocar deliberadamente este mecanismo (o su CLI
    env-gateado, `scripts/activar_directorio.py`).

    Cuando la aprobacion existe y es verificable, la activacion deja constancia
    en la traza durable `directorio_auditoria` (append-only y sin PII), ademas
    del evento estructurado.

Verificabilidad del artefacto:
    Se exige que el documento exista, contenga la seccion de revision humana HIGH
    (encabezado `## 4.`) y declare la aprobacion como `CONCEDIDA` con una fecha
    ISO-8601 (`YYYY-MM-DD`) dentro de esa seccion. Un artefacto `PENDIENTE` o un
    documento que mencione `CONCEDIDA` fuera de la seccion NO habilita nada.
"""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.directorio_auditoria import DirectorioAuditoria
from app.services.auditoria_directorio import registrar_evento_auditoria

# Operacion auditada del cambio de estado (durable, sin PII).
ACTIVACION_OPERACION = "activacion_datos_reales"

# Variable de entorno que apunta al artefacto de aprobacion (gate de entorno).
ARTEFACTO_APROBACION_ENV = "DIRECTORY_ACTIVATION_APPROVAL_ARTIFACT"

# Artefacto canonico de evidencia, relativo a la raiz del repositorio.
ARTEFACTO_APROBACION_POR_DEFECTO = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "directorio-evidencia-cumplimiento.md"
)

_SECCION_REVISION_RE = re.compile(r"^##\s*4\..*$", re.MULTILINE)
_FECHA_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

__all__ = [
    "ACTIVACION_OPERACION",
    "ARTEFACTO_APROBACION_ENV",
    "ARTEFACTO_APROBACION_POR_DEFECTO",
    "ActivacionNoAprobadaError",
    "activar_datos_reales",
    "verificacion_aprobacion",
]


class ActivacionNoAprobadaError(RuntimeError):
    """La activacion se rechaza: falta la aprobacion humana HIGH verificable."""


def _texto_de_seccion_revision(texto: str) -> str | None:
    """Devuelve el cuerpo de la seccion de revision humana HIGH, o None.

    La seccion se delimita por el encabezado `## 4.` y el siguiente encabezado
    `## ` de nivel 2 (o el final del documento). Aislar la seccion evita aceptar
    un `CONCEDIDA` historico o de otro apartado.
    """
    encabezado = _SECCION_REVISION_RE.search(texto)
    if encabezado is None:
        return None
    inicio = encabezado.end()
    siguiente = re.search(r"^##\s+", texto[inicio:], re.MULTILINE)
    fin = inicio + siguiente.start() if siguiente else len(texto)
    return texto[inicio:fin]


def verificacion_aprobacion(artefacto: str | Path | None) -> str:
    """
    Valida el artefacto de aprobacion y devuelve la fecha de la aprobacion.

    Bloqueado por defecto: sin artefacto, o con un artefacto que no declare la
    aprobacion HIGH como `CONCEDIDA` con fecha, la verificacion falla.

    Args:
        artefacto: ruta al artefacto de aprobacion (absoluta o relativa al CWD).

    Returns:
        La fecha ISO-8601 (`YYYY-MM-DD`) de la aprobacion concedida.

    Raises:
        ActivacionNoAprobadaError: si falta el artefacto, no existe, no contiene
            la seccion de revision humana HIGH o no declara `CONCEDIDA` con fecha.
    """
    if artefacto is None or not str(artefacto).strip():
        raise ActivacionNoAprobadaError(
            "Se requiere el artefacto de aprobacion humana HIGH; sin el no hay "
            "activacion (el directorio permanece en modo sintetico)."
        )

    path = Path(artefacto)
    if not path.is_file():
        raise ActivacionNoAprobadaError(
            f"El artefacto de aprobacion no existe: {path}"
        )

    texto = path.read_text(encoding="utf-8")
    seccion = _texto_de_seccion_revision(texto)
    if seccion is None:
        raise ActivacionNoAprobadaError(
            "El artefacto no contiene la seccion de revision humana HIGH "
            "(encabezado '## 4.')."
        )

    if "CONCEDIDA" not in seccion.upper():
        raise ActivacionNoAprobadaError(
            "El artefacto no declara la aprobacion humana HIGH como CONCEDIDA."
        )

    fecha = _FECHA_RE.search(seccion)
    if fecha is None:
        raise ActivacionNoAprobadaError(
            "El artefacto declara la aprobacion CONCEDIDA pero no registra una "
            "fecha ISO-8601 (YYYY-MM-DD) verificable."
        )

    return fecha.group(1)


async def activar_datos_reales(
    session: AsyncSession,
    *,
    artefacto: str | Path | None,
    actor_id: int | None = None,
) -> DirectorioAuditoria:
    """
    Ejecuta la activacion deliberada y registra el cambio de estado (DIR-014).

    La verificacion del artefacto ocurre ANTES de cualquier efecto: si la
    aprobacion no es verificable, se lanza `ActivacionNoAprobadaError` y no se
    escribe ninguna fila. Con aprobacion valida se emite la constancia durable
    sin PII (`activacion_datos_reales` / `ok`).

    Returns:
        La fila durable que registra la activacion.
    """
    verificacion_aprobacion(artefacto)
    return await registrar_evento_auditoria(
        session,
        operacion=ACTIVACION_OPERACION,
        resultado="ok",
        actor_id=actor_id,
    )