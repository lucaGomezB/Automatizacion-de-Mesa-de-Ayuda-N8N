"""Figura 8 - Matriz de confusion 5x5 del clasificador.

Deriva la matriz real (5x5) desde `evaluation/report.md` (owned by c-76) en el
orden canonico de sectores. NO hardcodea las celdas: las parsea del reporte y
valida que los totales sumen los 200 casos del corpus.

Salida: docs/Tesis/v9 (IA)/paper/figures/matriz_confusion.pdf
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "evaluation" / "report.md"
OUT = ROOT / "docs" / "Tesis" / "v9 (IA)" / "paper" / "figures" / "matriz_confusion.pdf"

ETIQUETAS = [
    "Seguridad\nInformatica",
    "Soporte Tecnico\nHardware",
    "Soporte Tecnico\nSoftware",
    "Bases de\nDatos",
    "Sistemas",
]


def parse_matriz(report: Path) -> tuple[list[str], np.ndarray]:
    lines = report.read_text(encoding="utf-8").splitlines()
    header: list[str] | None = None
    filas: list[list[int]] = []
    for line in lines:
        if not line.startswith("|"):
            continue
        celdas = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None and celdas and celdas[0].startswith("Asignado"):
            header = celdas[1:]
            continue
        if header is not None:
            etiqueta = re.sub(r"[*_ ]", "", celdas[0])
            if re.match(r"^[A-Za-z]+$", etiqueta) and len(celdas) - 1 == len(header):
                try:
                    filas.append([int(c) for c in celdas[1:]])
                except ValueError:
                    break
    if header is None or len(filas) != 5:
        raise ValueError("No se pudo parsear la matriz 5x5 de evaluation/report.md")
    return header, np.array(filas, dtype=int)


def build_figure(matriz: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8.6, 7.2))
    im = ax.imshow(matriz, cmap="Blues")
    ax.set_xticks(range(len(ETIQUETAS)), labels=ETIQUETAS)
    ax.set_yticks(range(len(ETIQUETAS)), labels=ETIQUETAS)
    ax.set_xlabel("Sector predicho principal")
    ax.set_ylabel("Sector asignado (verdad)")
    ax.set_title("Matriz de confusion del clasificador (n = 200)")

    umbral = matriz.max() / 2.0
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            ax.text(
                j,
                i,
                str(matriz[i, j]),
                ha="center",
                va="center",
                color="white" if matriz[i, j] > umbral else "black",
                fontsize=11,
            )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Casos")
    fig.tight_layout()
    return fig


def main() -> None:
    header, matriz = parse_matriz(REPORT)
    total = int(matriz.sum())
    aciertos = int(np.trace(matriz))
    print("Columnas:", header)
    print("Totales por fila:", matriz.sum(axis=1).tolist())
    print(f"Total = {total} | aciertos (traza) = {aciertos} | exactitud = {aciertos / total:.4f}")
    if total != 200:
        raise SystemExit(f"El total de la matriz ({total}) no es 200")
    fig = build_figure(matriz)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"Escrito: {OUT}")


if __name__ == "__main__":
    main()
