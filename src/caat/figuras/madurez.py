from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from caat.figuras.estilo import DPI, ROJO, VERDE, guardar
from caat.simulacion.catalogos import ProcesoCobit


def _cerrar(valores: list) -> list:
    """Repite el primer valor al final para cerrar el polígono del radar."""
    return valores + valores[:1]


def dibujar(evaluacion: list[ProcesoCobit], ruta: Path) -> None:
    etiquetas = [p.id for p in evaluacion]
    ang = _cerrar(np.linspace(0, 2 * np.pi, len(etiquetas), endpoint=False).tolist())
    actual = _cerrar([p.actual for p in evaluacion])
    objetivo = _cerrar([p.objetivo for p in evaluacion])

    fig = plt.figure(figsize=(5.2, 4.6), dpi=DPI)
    ax = fig.add_subplot(111, polar=True)
    ax.plot(ang, objetivo, color=VERDE, lw=1.5, label="Nivel objetivo (2030)")
    ax.fill(ang, objetivo, color=VERDE, alpha=.12)
    ax.plot(ang, actual, color=ROJO, lw=1.5, label="Nivel actual (2028)")
    ax.fill(ang, actual, color=ROJO, alpha=.25)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(etiquetas, fontsize=8)
    ax.set_ylim(0, 5)
    ax.set_yticks(range(0, 6))
    ax.tick_params(axis="y", labelsize=7)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.12), frameon=False, fontsize=8)
    guardar(fig, ruta)
