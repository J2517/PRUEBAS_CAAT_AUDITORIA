from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from caat.figuras.estilo import AZUL, DPI, ROJO, guardar, limpiar_ejes
from caat.pruebas.caat04_benford import ResultadoBenford


def dibujar(r: ResultadoBenford, ruta: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=DPI)
    x = np.arange(1, 10)
    ax.bar(x - 0.2, r.obs_sensor, 0.4, label="Registros SENSOR", color=AZUL)
    ax.bar(x + 0.2, r.obs_manual, 0.4, label="Registros MANUALES", color=ROJO)
    ax.plot(x, r.esperado, "k-o", ms=3, lw=1, label="Distribución esperada (Benford)")
    ax.set_xticks(x)
    ax.set_xlabel("Primer dígito")
    ax.set_ylabel("Proporción")
    ax.legend(frameon=False)
    limpiar_ejes(ax)
    guardar(fig, ruta)
