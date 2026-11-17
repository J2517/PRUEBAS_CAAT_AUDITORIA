"""Estilo común de las figuras."""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

AZUL = "#4C78A8"
ROJO = "#E45756"
NARANJA = "#F58518"
VERDE = "#54A24B"
TURQUESA = "#72B7B2"
GRIS = "#BBBBBB"
DPI = 200


def aplicar() -> None:
    """Backend sin ventana y tipografía tipo APA. Llamar una vez al inicio."""
    matplotlib.use("Agg")
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]
    plt.rcParams["font.size"] = 10


def limpiar_ejes(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)


def guardar(fig, ruta: Path, ajustar: bool = True) -> None:
    if ajustar:
        fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)
