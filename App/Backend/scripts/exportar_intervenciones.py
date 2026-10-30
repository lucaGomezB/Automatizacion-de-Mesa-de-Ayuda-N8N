r"""
Export pseudonimizado de las intervenciones humanas para el analisis (c-165, ECM-003).

Responsabilidad:
    Producir `evaluation/data/campana/intervenciones.csv`, el dataset de intervencion
    que consume c-167, a partir de `clasificacion_log`. Una fila por log INTERVENIDO
    (`validado_en` no nulo), con las columnas, en este orden:

        id_caso, incidente_id, log_id, origen_intervencion, intervencion_inicio_en,
        validado_en, duracion_s, sector_predicho, sector_validado, cambio_sector,
        actor_alias

    - `id_caso` se vincula por `incidente_id` desde el/los sidecars de la corrida
      (`case_id`); queda vacio si el incidente no figura (o figura en dos casos
      distintos: vinculo ambiguo).
    - `duracion_s = validado_en - intervencion_inicio_en`, en segundos; vacia si falta el
      inicio o si es negativa (reloj del cliente adelantado). Se cuentan en el resumen.
    - `cambio_sector` es `true` o `false` (un predicho nulo cuenta como cambio).
    - `actor_alias` es HMAC-SHA256 del id del empleado con la clave de la variable de
      entorno `INTERVENCION_EXPORT_HMAC_KEY`, truncado a 12 hex; vacio si el actor es NULL.
      Un hash plano de un entero chico seria reversible por enumeracion: por eso se usa
      clave. No se exporta nunca nombre, email, telefono, legajo ni el id en claro.
    - Los logs legados (sector validado sin `validado_en`, previos a la migracion 024) NO
      se exportan: se cuentan en el resumen.

    La cohorte es la de la metrica `tasa_intervencion_backend`: logs con `created_at` en
    el rango `--desde`/`--hasta` (dias de negocio America/Argentina/Buenos_Aires, ambos
    inclusivos). El denominador de la tasa de campana NO sale de este export (solo trae
    filas intervenidas): c-167 lo toma del plan de campana o del sidecar de la corrida.

Archivos congelados:
    El script se niega a escribir (sale con error SIN tocar el archivo) sobre
    `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`,
    `evaluation/predicciones.json` y todo lo que haya bajo `evaluation/evidence/`.

Uso (desde la raiz de App/Backend; la clave NO se versiona ni se imprime):
    export INTERVENCION_EXPORT_HMAC_KEY='<clave secreta>'
    python -m scripts.exportar_intervenciones \
        --sidecar ../../evaluation/data/campana/sidecar_<id_corrida>.json \
        --desde 2026-11-01 --hasta 2026-11-30 \
        --salida ../../evaluation/data/campana/intervenciones.csv

    `--sidecar` se repite una vez por corrida. Sin `--salida` se usa la ruta de campana
    anterior (relativa a la raiz del repositorio, no al directorio de trabajo).
"""

import argparse
import asyncio
import csv
import fnmatch
import hashlib
import hmac
import json
import os
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Final

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.catalog import Sector
from app.models.clasificacion_log import (
    ClasificacionLog,
    condicion_intervenido,
    condicion_legado,
)
from app.services.intervencion_estado import a_utc, hubo_cambio_de_sector
from app.utils.business_time import business_range_to_utc

#: Columnas del CSV, en el orden acordado con c-167 (contrato C5).
COLUMNAS: Final[tuple[str, ...]] = (
    "id_caso",
    "incidente_id",
    "log_id",
    "origen_intervencion",
    "intervencion_inicio_en",
    "validado_en",
    "duracion_s",
    "sector_predicho",
    "sector_validado",
    "cambio_sector",
    "actor_alias",
)

#: Variable de entorno con la clave del alias del actor (propia del export).
ENV_CLAVE_HMAC: Final[str] = "INTERVENCION_EXPORT_HMAC_KEY"

#: Largo del alias del actor, en caracteres hexadecimales.
LARGO_ALIAS: Final[int] = 12

#: Raiz del repositorio (scripts -> Backend -> App -> raiz).
REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

#: Ruta de campana por defecto del CSV.
SALIDA_POR_DEFECTO: Final[Path] = REPO_ROOT / "evaluation" / "data" / "campana" / "intervenciones.csv"

# Archivos congelados (rutas relativas a la raiz del repo, en minusculas y con "/").
_CONGELADOS_EXACTOS: Final[tuple[str, ...]] = (
    "data/corpus_evaluacion_pseudonimizado.json",
    "evaluation/predicciones.json",
)
_CONGELADOS_PATRON: Final[tuple[str, ...]] = ("data/corpus_resultados*.json",)
_CONGELADOS_DIRECTORIOS: Final[tuple[str, ...]] = ("evaluation/evidence",)


class ClaveHmacAusente(RuntimeError):
    """Falta (o esta vacia) la variable de entorno con la clave del alias del actor."""


class SalidaCongelada(RuntimeError):
    """La salida pedida es un archivo congelado de la evidencia: no se escribe."""


class SidecarInvalido(ValueError):
    """Un sidecar no existe, no es JSON o no tiene la forma de lista de entradas."""


@dataclass
class ResumenExportacion:
    """Conteos de una corrida del export, para declarar lo que quedo afuera."""

    exportados: int = 0
    legados_excluidos: int = 0
    sin_id_caso: int = 0
    vinculos_ambiguos: int = 0
    sin_inicio: int = 0
    duracion_negativa: int = 0

    def lineas(self, salida: Path | None = None) -> list[str]:
        destino = f" -> {salida}" if salida is not None else ""
        return [
            f"Export de intervenciones: {self.exportados} filas exportadas{destino}",
            "  logs legados excluidos (validados antes de la migracion 024): "
            f"{self.legados_excluidos}",
            f"  filas sin id_caso (incidente no vinculable por los sidecars): {self.sin_id_caso}"
            f" (con vinculo ambiguo: {self.vinculos_ambiguos})",
            f"  filas sin duracion_s: sin inicio {self.sin_inicio}, inicio posterior a la "
            f"validacion {self.duracion_negativa}",
        ]


# -- Precondiciones: clave, salida, sidecars -------------------------------------


def leer_clave_hmac(entorno: Any = None) -> str:
    """
    Lee la clave del alias del actor de `INTERVENCION_EXPORT_HMAC_KEY` (os.environ).

    No toca `Settings`, `.env.example` ni el CI: la clave es del export y no se versiona.

    Raises:
        ClaveHmacAusente: Si la variable no existe o esta vacia. El mensaje nombra la
            variable y NUNCA imprime su valor.
    """
    fuente = os.environ if entorno is None else entorno
    clave = (fuente.get(ENV_CLAVE_HMAC) or "").strip()
    if not clave:
        raise ClaveHmacAusente(
            f"Falta la variable de entorno {ENV_CLAVE_HMAC}: es la clave secreta con la que "
            "se calcula actor_alias y no se versiona. Definila antes de exportar."
        )
    return clave


def alias_de_actor(empleado_id: int | None, clave: str) -> str:
    """
    Alias estable y no reversible del empleado: HMAC-SHA256 truncado a 12 hex.

    Vacio si el actor es NULL (cuenta sin empleado vinculado o empleado purgado).
    """
    if empleado_id is None:
        return ""
    digest = hmac.new(
        clave.encode("utf-8"), str(empleado_id).encode("ascii"), hashlib.sha256
    ).hexdigest()
    return digest[:LARGO_ALIAS]


def verificar_salida_permitida(salida: Path, *, repo_root: Path = REPO_ROOT) -> None:
    """
    Rechaza una salida que apunte a un archivo congelado de la evidencia.

    Compara la ruta RESUELTA (absoluta, sin `..` ni enlaces) contra la lista de congelados
    relativa a la raiz del repo, sin distinguir mayusculas. Una ruta fuera del repo no
    puede ser un congelado.

    Raises:
        SalidaCongelada: Si la salida es un archivo congelado.
    """
    destino = Path(salida).resolve()
    try:
        relativa = destino.relative_to(Path(repo_root).resolve()).as_posix().lower()
    except ValueError:
        return
    congelado = (
        relativa in _CONGELADOS_EXACTOS
        or any(fnmatch.fnmatchcase(relativa, patron) for patron in _CONGELADOS_PATRON)
        or any(relativa.startswith(f"{d}/") for d in _CONGELADOS_DIRECTORIOS)
    )
    if congelado:
        raise SalidaCongelada(
            f"{destino.name} es un archivo congelado de la evidencia ({relativa}): el export "
            "no escribe sobre el corpus pseudonimizado, los resultados del corpus, "
            "evaluation/predicciones.json ni evaluation/evidence/. Usa una ruta de campana, "
            "por ejemplo evaluation/data/campana/intervenciones.csv."
        )


def _a_entero(valor: Any) -> int | None:
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    if isinstance(valor, str) and valor.strip().lstrip("-").isdigit():
        return int(valor.strip())
    return None


def cargar_vinculos(rutas: Sequence[Path]) -> tuple[dict[int, str], set[int]]:
    """
    Arma el mapa `incidente_id -> case_id` a partir de los sidecars de las corridas.

    Cada sidecar es una lista JSON de entradas con `case_id` e `incidente_id`. Las
    entradas sin alguno de los dos no vinculan. Un incidente asignado a DOS casos
    distintos (en el mismo sidecar o en corridas distintas) es AMBIGUO: no se vincula y
    se devuelve en el segundo valor, para declararlo.

    Raises:
        SidecarInvalido: Si un sidecar no existe, no es JSON o no es una lista.
    """
    vinculos: dict[int, str] = {}
    ambiguos: set[int] = set()
    for ruta in rutas:
        ruta = Path(ruta)
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise SidecarInvalido(f"No existe el sidecar {ruta}.") from exc
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SidecarInvalido(f"No se pudo leer el sidecar {ruta.name} como JSON: {exc}") from exc
        if not isinstance(datos, list):
            raise SidecarInvalido(
                f"El sidecar {ruta.name} debe ser una lista de entradas con 'case_id' e "
                "'incidente_id'."
            )
        for entrada in datos:
            if not isinstance(entrada, dict):
                continue
            incidente = _a_entero(entrada.get("incidente_id"))
            caso = str(entrada.get("case_id") or "").strip()
            if incidente is None or not caso or incidente in ambiguos:
                continue
            previo = vinculos.get(incidente)
            if previo is None:
                vinculos[incidente] = caso
            elif previo != caso:
                ambiguos.add(incidente)
                del vinculos[incidente]
    return vinculos, ambiguos


# -- Consulta, filas y CSV --------------------------------------------------------


def _formatear_duracion(segundos: float) -> str:
    """Segundos con hasta tres decimales y sin ceros sobrantes (`30`, `12.5`)."""
    return f"{segundos:.3f}".rstrip("0").rstrip(".")


def _instante(valor: datetime | None) -> str:
    """ISO-8601 en UTC con zona explicita (`2026-10-30T15:00:00+00:00`); vacio si no hay."""
    normalizado = a_utc(valor)
    return normalizado.isoformat() if normalizado is not None else ""


def _limites(
    desde: date | None, hasta: date | None
) -> tuple[datetime | None, datetime | None]:
    """Dias de negocio inclusivos -> limites UTC semiabiertos (superior EXCLUSIVO)."""
    inferior = business_range_to_utc(desde, desde)[0] if desde is not None else None
    superior = business_range_to_utc(hasta, hasta)[1] if hasta is not None else None
    return inferior, superior


def _cohorte(inferior: datetime | None, superior: datetime | None) -> list[Any]:
    condiciones: list[Any] = []
    if inferior is not None:
        condiciones.append(ClasificacionLog.created_at >= inferior)
    if superior is not None:
        condiciones.append(ClasificacionLog.created_at < superior)
    return condiciones


async def generar_filas(
    session: AsyncSession,
    *,
    vinculos: dict[int, str],
    ambiguos: set[int],
    clave: str,
    desde: date | None = None,
    hasta: date | None = None,
) -> tuple[list[dict[str, str]], ResumenExportacion]:
    """
    Consulta los logs intervenidos de la cohorte y arma las filas del CSV.

    Solo lee columnas escalares (nombres de sector por JOIN): no carga relationships.
    El orden es por `log_id` ascendente, de modo que el export es reproducible.
    """
    inferior, superior = _limites(desde, hasta)
    predicho = aliased(Sector)
    validado = aliased(Sector)
    registros = (
        await session.execute(
            select(
                ClasificacionLog.id.label("log_id"),
                ClasificacionLog.incidente_id,
                ClasificacionLog.origen_intervencion,
                ClasificacionLog.intervencion_inicio_en,
                ClasificacionLog.validado_en,
                ClasificacionLog.validado_por_empleado_id,
                ClasificacionLog.sector_id_predicho,
                ClasificacionLog.sector_id_validado,
                predicho.nombre.label("sector_predicho"),
                validado.nombre.label("sector_validado"),
            )
            .select_from(ClasificacionLog)
            .join(predicho, ClasificacionLog.sector_id_predicho == predicho.id, isouter=True)
            .join(validado, ClasificacionLog.sector_id_validado == validado.id, isouter=True)
            .where(condicion_intervenido(), *_cohorte(inferior, superior))
            .order_by(ClasificacionLog.id)
        )
    ).all()
    legados = (
        await session.execute(
            select(func.count(ClasificacionLog.id)).where(
                condicion_legado(), *_cohorte(inferior, superior)
            )
        )
    ).scalar_one()

    resumen = ResumenExportacion(legados_excluidos=int(legados))
    filas: list[dict[str, str]] = []
    for registro in registros:
        inicio = a_utc(registro.intervencion_inicio_en)
        validado_en = a_utc(registro.validado_en)
        duracion = ""
        if inicio is None:
            resumen.sin_inicio += 1
        else:
            segundos = (validado_en - inicio).total_seconds()
            if segundos < 0:
                resumen.duracion_negativa += 1
            else:
                duracion = _formatear_duracion(segundos)
        id_caso = vinculos.get(registro.incidente_id, "")
        if registro.incidente_id in ambiguos:
            resumen.vinculos_ambiguos += 1
        if not id_caso:
            resumen.sin_id_caso += 1
        cambio = hubo_cambio_de_sector(registro.sector_id_predicho, registro.sector_id_validado)
        filas.append(
            {
                "id_caso": id_caso,
                "incidente_id": str(registro.incidente_id),
                "log_id": str(registro.log_id),
                "origen_intervencion": registro.origen_intervencion or "",
                "intervencion_inicio_en": _instante(inicio),
                "validado_en": _instante(validado_en),
                "duracion_s": duracion,
                "sector_predicho": registro.sector_predicho or "",
                "sector_validado": registro.sector_validado or "",
                "cambio_sector": "true" if cambio else "false",
                "actor_alias": alias_de_actor(registro.validado_por_empleado_id, clave),
            }
        )
    resumen.exportados = len(filas)
    return filas, resumen


def escribir_csv(filas: Sequence[dict[str, str]], salida: Path) -> None:
    """Escribe el CSV en UTF-8 con saltos de linea LF (los mismos en Windows y Linux)."""
    verificar_salida_permitida(salida)
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(COLUMNAS), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)


async def exportar_intervenciones(
    session: AsyncSession,
    *,
    sidecars: Sequence[Path],
    salida: Path,
    clave: str,
    desde: date | None = None,
    hasta: date | None = None,
) -> ResumenExportacion:
    """
    Exporta las intervenciones a `salida` y devuelve el resumen de lo excluido.

    La salida se valida ANTES de leer nada: un archivo congelado nunca se toca.
    """
    verificar_salida_permitida(salida)
    vinculos, ambiguos = cargar_vinculos(sidecars)
    filas, resumen = await generar_filas(
        session, vinculos=vinculos, ambiguos=ambiguos, clave=clave, desde=desde, hasta=hasta
    )
    escribir_csv(filas, salida)
    return resumen


# -- CLI ---------------------------------------------------------------------------


def _crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.exportar_intervenciones",
        description=(
            "Exporta las intervenciones humanas (logs con validado_en) a un CSV "
            "pseudonimizado para c-167. La clave del alias del actor se lee de la variable "
            f"de entorno {ENV_CLAVE_HMAC}."
        ),
    )
    parser.add_argument(
        "--sidecar",
        action="append",
        required=True,
        type=Path,
        help="Sidecar de una corrida (lista JSON con case_id e incidente_id); se repite por corrida.",
    )
    parser.add_argument(
        "--desde",
        type=date.fromisoformat,
        default=None,
        help="Primer dia de negocio de la cohorte (AAAA-MM-DD, inclusivo), por created_at del log.",
    )
    parser.add_argument(
        "--hasta",
        type=date.fromisoformat,
        default=None,
        help="Ultimo dia de negocio de la cohorte (AAAA-MM-DD, inclusivo).",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA_POR_DEFECTO,
        help=f"CSV de salida (por defecto {SALIDA_POR_DEFECTO}). Nunca un archivo congelado.",
    )
    return parser


async def _ejecutar(
    args: argparse.Namespace,
    *,
    clave: str,
    vinculos: dict[int, str],
    ambiguos: set[int],
    session_factory: Callable[[], AsyncSession] | None,
) -> ResumenExportacion:
    """Abre la sesion (la inyectada o la del engine de la app), genera y escribe el CSV."""
    if session_factory is not None:
        async with session_factory() as session:
            filas, resumen = await generar_filas(
                session, vinculos=vinculos, ambiguos=ambiguos, clave=clave,
                desde=args.desde, hasta=args.hasta,
            )
    else:
        from sqlalchemy.ext.asyncio import async_sessionmaker

        from app.core.database import engine

        try:
            async with async_sessionmaker(engine, expire_on_commit=False)() as session:
                filas, resumen = await generar_filas(
                    session, vinculos=vinculos, ambiguos=ambiguos, clave=clave,
                    desde=args.desde, hasta=args.hasta,
                )
        finally:
            await engine.dispose()
    escribir_csv(filas, args.salida)
    return resumen


def main(
    argv: Sequence[str] | None = None,
    *,
    session_factory: Callable[[], AsyncSession] | None = None,
) -> int:
    """
    Punto de entrada. Valida las precondiciones ANTES de abrir la base de datos.

    Orden: salida no congelada, clave presente, sidecars legibles. Cualquier fallo
    termina con codigo 2 y un mensaje en stderr, sin escribir ni conectarse.

    Returns:
        0 en exito; 2 ante una precondicion incumplida.
    """
    args = _crear_parser().parse_args(argv)
    try:
        verificar_salida_permitida(args.salida)
        clave = leer_clave_hmac()
        vinculos, ambiguos = cargar_vinculos(args.sidecar)
    except (SalidaCongelada, ClaveHmacAusente, SidecarInvalido) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    resumen = asyncio.run(
        _ejecutar(
            args, clave=clave, vinculos=vinculos, ambiguos=ambiguos, session_factory=session_factory
        )
    )
    print("\n".join(resumen.lineas(args.salida)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
