"""
Job de reevaluacion del canario y deteccion de deriva del servicio y del modelo (c-227).

Responsabilidad:
    Recalcular las metricas de clasificacion sobre un conjunto canario fijo con las
    mismas definiciones del framework de evaluacion (reutiliza `evaluation.metrics`
    SIN modificarlo), compararlas contra una linea de base congelada, distinguir un
    cambio de identidad (proveedor/version de modelo) de una degradacion de metricas
    con identidad estable, y emitir alertas por metrica bajo su piso.

    Por defecto es OFFLINE: reproduce la linea de base desde los artefactos
    versionados sin invocar al proveedor. Una corrida con predicciones frescas exige
    confirmacion explicita del operador (gate reutilizado de `evaluation.run_evaluation`)
    y MUST NOT ejecutarse sin ella.

    Es una senal operativa: NO modifica ningun numero canonico ni la evidencia
    congelada (`evaluation/evidence/`), ni reemplaza ninguna medicion de la tesis.

Diseno (design.md D4-D7):
    - `metricas_canario(pares)`: exactitud estricta, F1 macro y por sector.
    - `comparar_con_base(actual, base)`: diferencia por metrica y bandera de degradacion.
    - `detectar_deriva(metricas, base, tolerancias, identidad, base_identidad)`: veredicto.
    - `evaluar_alertas(metricas, pisos)`: alertas por metrica bajo su piso.
    - `identidad_proveedor(config)`: proveedor y modelo efectivos.

Gobernanza: MEDIUM. Cero llamadas pagas fuera del gate.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Sequence

from evaluation.corpus import cargar_corpus
from evaluation.metrics import (
    CLASES,
    exactitud_global,
    f1_macro,
    f1_por_clase,
    matriz_confusion,
)
from evaluation.run_evaluation import (
    CONFIRM_PAID_ENV_VAR,
    PaidRunNotConfirmedError,
    _compute_corpus_hash,
    _ensure_backend_on_path,
    _env_confirm_paid,
    _identidad_inferencia_por_defecto,
    _resolver_clasificador_real,
    cargar_cache_meta,
    cargar_predicciones,
    evaluar_corpus,
    guardar_predicciones,
)

# ---------------------------------------------------------------------------
# Rutas y constantes
# ---------------------------------------------------------------------------
_ROOT = pathlib.Path(__file__).resolve().parents[2]
CANARIO_DIR = _ROOT / "evaluation" / "data" / "canario"
CANARIO_PATH = CANARIO_DIR / "canario.json"
CANARIO_PREDICCIONES_PATH = CANARIO_DIR / "canario_predicciones.json"
BASELINE_PATH = CANARIO_DIR / "canario_baseline.json"
CANARIO_SHA256SUMS_PATH = CANARIO_DIR / "canario.SHA256SUMS.txt"
REPORTES_DIR = CANARIO_DIR / "reportes"

#: Metricas monitoreadas por el job (checkpoint 0.6: exactitud estricta y F1 macro).
METRICAS_MONITOREADAS: tuple[str, ...] = ("exactitud_estricta", "f1_macro")

#: Tolerancia por defecto (checkpoint 0.6): piso = max(0, linea de base - delta).
TOLERANCIA_DEFECTO: float = 0.05

#: Fallback operativo vigente (referencia a `classification-resilience`).
DOC_FALLBACK = (
    "Ante la indisponibilidad del servicio de inferencia, la cascada degrada al "
    "filtro deterministico con revision humana (`classification-resilience`): "
    "etapa=fallback, confianza=0.0 y requiere_revision_humana=true."
)

#: Criterio para restablecer el servicio tras una alerta.
CRITERIO_RESTABLECIMIENTO = (
    "Restablecer el servicio cuando el proveedor y la version de modelo efectivos "
    "coincidan con la identidad de la linea de base y las metricas del canario "
    "vuelvan a estar sobre sus pisos en una corrida offline."
)


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ParCanario:
    """Par (verdad, prediccion) de un caso del canario."""

    caso_id: str
    real: str
    predicho: Optional[str]
    adicionales: tuple[str, ...] = ()


@dataclass(frozen=True)
class MetricasCanario:
    """Metricas monitoreadas del canario (con desglose por sector)."""

    casos: int
    exactitud_estricta: float
    f1_macro: float
    f1_por_sector: Mapping[str, float]

    def monitoreadas(self) -> dict[str, float]:
        """Metricas escalares que el job monitorea (las del checkpoint 0.6)."""
        return {
            "exactitud_estricta": self.exactitud_estricta,
            "f1_macro": self.f1_macro,
        }


@dataclass(frozen=True)
class DiferenciaMetrica:
    """Diferencia de una metrica contra la linea de base."""

    metrica: str
    base: float
    actual: float
    diferencia: float
    degradada: bool


@dataclass(frozen=True)
class VeredictoDeriva:
    """Veredicto del job: sin deriva, de identidad, de metrica o ambas."""

    veredicto: str
    identidad_cambio: bool
    metricas_degradadas: tuple[str, ...]


@dataclass(frozen=True)
class AlertaMetrica:
    """Alerta por una metrica que cayo bajo su piso."""

    metrica: str
    valor: float
    piso: float


@dataclass(frozen=True)
class ResultadoMonitoreo:
    """Resultado de una corrida del job."""

    corrida: str
    veredicto: VeredictoDeriva
    metricas: MetricasCanario
    alertas: list[AlertaMetrica]
    reporte_path: pathlib.Path


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def metricas_canario(pares: Sequence[ParCanario]) -> MetricasCanario:
    """Exactitud estricta, F1 macro y por sector sobre el canario (reutiliza metrics).

    Un sector predicho ausente (fallback) cuenta como error y se excluye de la
    matriz de confusion, que solo admite los cinco sectores canonicos.
    """
    reales = [p.real for p in pares]
    predichos = [(p.predicho or "") for p in pares]
    exactitud = exactitud_global(reales, predichos)

    canonicos = [(r, p) for r, p in zip(reales, predichos) if p in CLASES]
    mc = matriz_confusion(
        [r for r, _ in canonicos], [p for _, p in canonicos]
    )
    f1s = f1_por_clase(mc)

    return MetricasCanario(
        casos=len(pares),
        exactitud_estricta=exactitud,
        f1_macro=f1_macro(f1s),
        f1_por_sector=dict(f1s),
    )


def comparar_con_base(
    actual: Mapping[str, float], base: Mapping[str, float]
) -> dict[str, DiferenciaMetrica]:
    """Diferencia (`actual - base`) por metrica y bandera de degradacion."""
    diferencias: dict[str, DiferenciaMetrica] = {}
    for metrica in sorted(actual):
        valor_actual = float(actual[metrica])
        valor_base = float(base.get(metrica, valor_actual))
        diferencia = valor_actual - valor_base
        diferencias[metrica] = DiferenciaMetrica(
            metrica=metrica,
            base=valor_base,
            actual=valor_actual,
            diferencia=diferencia,
            degradada=diferencia < 0,
        )
    return diferencias


def detectar_deriva(
    metricas: Mapping[str, float],
    base: Mapping[str, float],
    tolerancias: Mapping[str, float],
    identidad: tuple[str, str],
    base_identidad: tuple[str, str],
) -> VeredictoDeriva:
    """Veredicto de deriva: dos ejes separados (identidad y metrica).

    Se declara una degradacion de metrica cuando `base - actual > tolerancia`. El
    cambio de identidad (proveedor o version de modelo) se reporta por separado.
    """
    identidad_cambio = tuple(identidad) != tuple(base_identidad)
    degradadas = tuple(
        metrica
        for metrica in sorted(metricas)
        if (base.get(metrica, metricas[metrica]) - metricas[metrica])
        > tolerancias.get(metrica, 0.0)
    )

    if identidad_cambio and degradadas:
        veredicto = "ambas"
    elif identidad_cambio:
        veredicto = "deriva_de_identidad"
    elif degradadas:
        veredicto = "deriva_de_metrica"
    else:
        veredicto = "sin_deriva"

    return VeredictoDeriva(
        veredicto=veredicto,
        identidad_cambio=identidad_cambio,
        metricas_degradadas=degradadas,
    )


def evaluar_alertas(
    metricas: Mapping[str, float], pisos: Mapping[str, float]
) -> list[AlertaMetrica]:
    """Alertas por metrica estrictamente bajo su piso (orden estable)."""
    return [
        AlertaMetrica(metrica=metrica, valor=float(metricas[metrica]), piso=float(pisos[metrica]))
        for metrica in sorted(metricas)
        if metrica in pisos and metricas[metrica] < pisos[metrica]
    ]


def identidad_proveedor(config: Any) -> tuple[str, str]:
    """Proveedor y modelo efectivos segun la configuracion (`Settings`)."""
    return (str(config.inference_provider), str(config.inference_model))


# ---------------------------------------------------------------------------
# Artefactos e IO
# ---------------------------------------------------------------------------
def pares_desde(corpus: Sequence, predicciones: Sequence) -> list[ParCanario]:
    """Empareja corpus y predicciones por posicion (verifica alineacion)."""
    predicciones = list(predicciones)
    if len(predicciones) != len(corpus):
        raise ValueError(
            f"Predicciones desalineadas con el canario: {len(predicciones)} "
            f"predicciones frente a {len(corpus)} casos."
        )
    pares: list[ParCanario] = []
    for caso, pred in zip(corpus, predicciones):
        if pred.caso_id != caso.id:
            raise ValueError(
                f"Predicciones desalineadas en '{pred.caso_id}' frente a '{caso.id}'."
            )
        pares.append(
            ParCanario(
                caso_id=pred.caso_id,
                real=pred.sector_asignado,
                predicho=pred.sector_predicho,
                adicionales=tuple(pred.sectores_adicionales),
            )
        )
    return pares


def _identidad_tupla(identidad: Mapping[str, str]) -> tuple[str, str]:
    return (str(identidad["provider"]), str(identidad["model"]))


def calcular_linea_de_base(
    canario_path: pathlib.Path | str = CANARIO_PATH,
    predicciones_path: pathlib.Path | str = CANARIO_PREDICCIONES_PATH,
    *,
    tolerancia: float = TOLERANCIA_DEFECTO,
) -> dict[str, Any]:
    """Calcula la linea de base congelada del canario desde los artefactos (offline).

    No invoca al proveedor: deriva las metricas de las predicciones versionadas.
    """
    canario_path = pathlib.Path(canario_path)
    corpus = cargar_corpus(canario_path)
    predicciones = cargar_predicciones(pathlib.Path(predicciones_path))
    metricas = metricas_canario(pares_desde(corpus, predicciones))

    meta = cargar_cache_meta(pathlib.Path(predicciones_path)) or {}
    provider, model = _identidad_inferencia_por_defecto()
    return {
        "canario_count": len(corpus),
        "canario_hash": _compute_corpus_hash(canario_path),
        "clasificador_version": meta.get("classifier_version", "hybrid-v3"),
        "metricas": metricas.monitoreadas(),
        "f1_por_sector": dict(metricas.f1_por_sector),
        "identidad": {"provider": provider, "model": model},
        "tolerancia": tolerancia,
        "pisos": {
            metrica: max(0.0, metricas.monitoreadas()[metrica] - tolerancia)
            for metrica in METRICAS_MONITOREADAS
        },
    }


def formatear_reporte(
    *,
    corrida: str,
    canario_hash: str,
    canario_count: int,
    base: Mapping[str, Any],
    identidad: tuple[str, str],
    diferencias: Mapping[str, DiferenciaMetrica],
    tolerancias: Mapping[str, float],
    veredicto: VeredictoDeriva,
    alertas: Sequence[AlertaMetrica],
    pisos: Mapping[str, float],
) -> str:
    """Renderiza el reporte del job (determinista: solo depende de las entradas)."""
    base_identidad = _identidad_tupla(base["identidad"])
    lineas: list[str] = [
        "# Reporte de monitoreo de la deriva (c-227)",
        "",
        f"- **Corrida:** `{corrida}`",
        f"- **Canario:** `{canario_count}` casos, SHA-256 `{canario_hash}`",
        f"- **Clasificador:** `{base.get('clasificador_version', 'hybrid-v3')}`",
        f"- **Identidad de la linea de base:** proveedor `{base_identidad[0]}`, "
        f"modelo `{base_identidad[1]}`",
        f"- **Identidad de la corrida:** proveedor `{identidad[0]}`, modelo `{identidad[1]}`",
        "",
        f"## Veredicto: `{veredicto.veredicto}`",
        "",
        f"- Cambio de identidad: `{veredicto.identidad_cambio}`",
        f"- Metricas degradadas: "
        f"`{', '.join(veredicto.metricas_degradadas) if veredicto.metricas_degradadas else 'ninguna'}`",
        "",
        "## Metricas del canario",
        "",
        "| Metrica | Linea de base | Actual | Diferencia | Tolerancia | Degradada |",
        "|---|---|---|---|---|---|",
    ]
    for metrica in sorted(diferencias):
        d = diferencias[metrica]
        lineas.append(
            f"| {metrica} | {d.base!r} | {d.actual!r} | {d.diferencia!r} "
            f"| {tolerancias.get(metrica, 0.0)!r} | {d.degradada} |"
        )

    lineas += ["", "## Alertas por piso", ""]
    if not alertas:
        lineas.append("Sin alertas: ninguna metrica monitoreada quedo bajo su piso.")
    else:
        for alerta in alertas:
            lineas.append(
                f"- Metrica `{alerta.metrica}`: valor `{alerta.valor!r}` < piso "
                f"`{alerta.piso!r}` (corrida `{corrida}`)."
            )
    lineas += [
        "",
        "- Pisos vigentes: "
        + ", ".join(f"`{m}` = `{pisos[m]!r}`" for m in sorted(pisos)),
        "",
        "### Fallback operativo",
        "",
        DOC_FALLBACK,
        "",
        "### Criterio para restablecer el servicio",
        "",
        CRITERIO_RESTABLECIMIENTO,
        "",
        "---",
        "_Generado por `evaluation/monitoreo/monitor_deriva.py`. Senal operativa: "
        "no reemplaza ningun numero canonico de la tesis._",
    ]
    return "\n".join(lineas) + "\n"


# ---------------------------------------------------------------------------
# main() del job
# ---------------------------------------------------------------------------
def _config_por_defecto() -> Any:
    """Configuracion efectiva del job (Settings del backend), estable al cwd.

    Carga explicitamente el `.env` del backend (`App/Backend/.env`) cuando existe,
    de modo que el job funcione tanto desde la raiz del repositorio (donde el
    `.env` de la raiz es el de docker-compose, con claves ajenas a `Settings`)
    como desde `App/Backend`. Las variables de entorno del proceso tienen
    precedencia, de modo que los pisos siguen siendo sobrescribibles sin recompilar.
    """
    _ensure_backend_on_path()
    from app.config.settings import Settings  # type: ignore[import]

    env_file = _ROOT / "App" / "Backend" / ".env"
    return Settings(_env_file=str(env_file) if env_file.exists() else None)


def _resolver_clasificador(confirm_paid: bool) -> Any:
    """Gate de corrida paga: solo resuelve el clasificador real con confirmacion."""
    if not confirm_paid and not _env_confirm_paid():
        raise PaidRunNotConfirmedError(
            "Corrida paga sin confirmar: el job invocaria al clasificador real. "
            f"Confirma explicitamente con --confirm-paid o {CONFIRM_PAID_ENV_VAR}=1."
        )
    return _resolver_clasificador_real()


def main(
    *,
    canario_path: pathlib.Path | str = CANARIO_PATH,
    predicciones_path: pathlib.Path | str = CANARIO_PREDICCIONES_PATH,
    baseline_path: pathlib.Path | str = BASELINE_PATH,
    reportes_dir: pathlib.Path | str = REPORTES_DIR,
    fresh: bool = False,
    confirm_paid: bool = False,
    fecha: str | None = None,
    config: Any = None,
    classifier: Any = None,
    escribir: bool = True,
) -> ResultadoMonitoreo:
    """Ejecuta el job: reproduce la linea de base (offline) o clasifica fresco.

    Args:
        canario_path: canario versionado.
        predicciones_path: predicciones versionadas (modo offline por defecto).
        baseline_path: linea de base congelada.
        reportes_dir: directorio de reportes fechados.
        fresh: si True, pide predicciones frescas (corrida paga detras del gate).
        confirm_paid: autoriza la corrida paga cuando `fresh` y no hay clasificador
            inyectado.
        fecha: identificador de la corrida (por defecto, la fecha UTC actual).
        config: configuracion con identidad y pisos (por defecto, `Settings`).
        classifier: clasificador inyectable (tests); evita el gate y el proveedor.
        escribir: si False, no escribe el reporte (tests).

    Raises:
        PaidRunNotConfirmedError: si `fresh` sin confirmacion y sin clasificador.
    """
    corrida = fecha or datetime.now(timezone.utc).date().isoformat()
    config = config if config is not None else _config_por_defecto()
    reportes_dir = pathlib.Path(reportes_dir)

    base = json.loads(pathlib.Path(baseline_path).read_text(encoding="utf-8"))
    corpus = cargar_corpus(pathlib.Path(canario_path))

    if fresh:
        if classifier is None:
            classifier = _resolver_clasificador(confirm_paid)
        predicciones = asyncio.run(evaluar_corpus(corpus, classifier))
        if escribir:
            reportes_dir.mkdir(parents=True, exist_ok=True)
            guardar_predicciones(
                predicciones,
                reportes_dir / f"predicciones_{corrida}.json",
                cache_meta={
                    "provider": str(config.inference_provider),
                    "model": str(config.inference_model),
                },
            )
    else:
        predicciones = cargar_predicciones(pathlib.Path(predicciones_path))

    metricas = metricas_canario(pares_desde(corpus, predicciones))
    actual = metricas.monitoreadas()
    tolerancias = {m: float(config.monitoring_tolerancia) for m in METRICAS_MONITOREADAS}
    identidad = identidad_proveedor(config)
    veredicto = detectar_deriva(
        actual,
        base["metricas"],
        tolerancias,
        identidad,
        _identidad_tupla(base["identidad"]),
    )
    pisos = {
        m: float(getattr(config, f"monitoring_{m}_floor")) for m in METRICAS_MONITOREADAS
    }
    alertas = evaluar_alertas(actual, pisos)
    diferencias = comparar_con_base(actual, base["metricas"])

    reporte = formatear_reporte(
        corrida=corrida,
        canario_hash=base["canario_hash"],
        canario_count=base["canario_count"],
        base=base,
        identidad=identidad,
        diferencias=diferencias,
        tolerancias=tolerancias,
        veredicto=veredicto,
        alertas=alertas,
        pisos=pisos,
    )
    reporte_path = reportes_dir / f"reporte_{corrida}.md"
    if escribir:
        reporte_path.parent.mkdir(parents=True, exist_ok=True)
        reporte_path.write_text(reporte, encoding="utf-8")

    return ResultadoMonitoreo(
        corrida=corrida,
        veredicto=veredicto,
        metricas=metricas,
        alertas=alertas,
        reporte_path=reporte_path,
    )


def _main_cli(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Monitoreo de la deriva del servicio de inferencia y del modelo (c-227)."
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Pide predicciones frescas del proveedor (corrida paga detras del gate).",
    )
    parser.add_argument(
        "--confirm-paid",
        action="store_true",
        help=f"Autoriza la corrida paga. Tambien con {CONFIRM_PAID_ENV_VAR}=1.",
    )
    parser.add_argument(
        "--fecha",
        default=None,
        help="Identificador de la corrida (por defecto, la fecha UTC actual).",
    )
    args = parser.parse_args(argv)

    try:
        resultado = main(fresh=args.fresh, confirm_paid=args.confirm_paid, fecha=args.fecha)
    except PaidRunNotConfirmedError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
    print(
        f"Veredicto: {resultado.veredicto.veredicto}. "
        f"Reporte: {resultado.reporte_path}"
    )


if __name__ == "__main__":
    _main_cli()
