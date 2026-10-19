"""Figura 7 - Boxplot de tiempos de registro POR CANAL.

Genera un panel por canal de origen (formulario web, correo electronico,
telefonia) comparando el flujo manual contra el automatizado. Nunca produce un
boxplot unico que mezcle canales (regla docs/medicion-latencia-e2e.md:50-53).

Salida: docs/Tesis/v9 (IA)/paper/figures/boxplot_tiempos.pdf
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"
OUT = ROOT / "docs" / "Tesis" / "v9 (IA)" / "paper" / "figures" / "boxplot_tiempos.pdf"

CHANNELS = [
    ("formulario web", "Formulario web"),
    ("correo electr\u00f3nico", "Correo electronico"),
    ("llamada telef\u00f3nica", "Telefonia"),
]


def load_corpus(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)["casos"]


def panel_data(casos: list[dict], canal: str) -> tuple[list[float], list[float]]:
    manual = [c["tiempo_manual_s"] for c in casos if c["canal_origen"] == canal]
    auto = [c["tiempo_automatizado_s"] for c in casos if c["canal_origen"] == canal]
    return manual, auto


def build_figure(casos: list[dict]) -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.8))
    for ax, (canal, titulo) in zip(axes, CHANNELS):
        manual, auto = panel_data(casos, canal)
        ax.boxplot(
            [manual, auto],
            tick_labels=["Manual", "Automatizado"],
            widths=0.5,
            patch_artist=True,
            boxprops={"facecolor": "#d8e4f0"},
            medianprops={"color": "#b03030", "linewidth": 1.6},
        )
        ax.set_title(f"{titulo}\n(n = {len(manual)})", fontsize=11)
        ax.set_ylabel("Tiempo de registro (s)")
        ax.grid(axis="y", linestyle=":", alpha=0.5)
        med_m = statistics.median(manual)
        med_a = statistics.median(auto)
        ax.set_xlabel(
            f"mediana manual = {med_m:.2f} s\nmediana automatizada = {med_a:.2f} s",
            fontsize=9,
        )
    fig.suptitle(
        "Distribucion del tiempo de registro por canal de origen",
        fontsize=13,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


def main() -> None:
    casos = load_corpus(CORPUS)
    for canal, titulo in CHANNELS:
        manual, auto = panel_data(casos, canal)
        print(
            f"{titulo:20s} n={len(manual):3d} "
            f"mediana manual={statistics.median(manual):6.2f} "
            f"mediana automatizada={statistics.median(auto):6.2f}"
        )
    fig = build_figure(casos)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"Escrito: {OUT}")


if __name__ == "__main__":
    main()
