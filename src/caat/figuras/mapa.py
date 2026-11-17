from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from caat.figuras.estilo import AZUL, DPI, ROJO, guardar, limpiar_ejes

N_PUNTOS_DENTRO = 4000


def seleccionar_muestra(rng: np.random.Generator, fuera: np.ndarray, n: int = N_PUNTOS_DENTRO) -> np.ndarray:
    """Índices de una muestra de lecturas dentro del área (para no dibujar ~70 000 puntos).

    Consume el generador aleatorio, por eso ``main`` la llama en la fase de simulación.
    """
    return rng.choice(np.flatnonzero(~fuera), n, replace=False)


def dibujar(lat: np.ndarray, lon: np.ndarray, fuera: np.ndarray, muestra: np.ndarray,
            bbox: dict[str, float], ruta: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 3.6), dpi=DPI)
    ax.scatter(lon[muestra], lat[muestra], s=2, c=AZUL, alpha=.4, label="Dentro del área metropolitana")
    ax.scatter(lon[fuera], lat[fuera], s=10, c=ROJO, marker="x", label=f"Fuera del área (n = {int(fuera.sum())})")
    ax.add_patch(plt.Rectangle((bbox["lon_min"], bbox["lat_min"]), bbox["lon_max"] - bbox["lon_min"],
                               bbox["lat_max"] - bbox["lat_min"], fill=False, ls="--", color="gray"))
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.legend(frameon=False, loc="lower left")
    limpiar_ejes(ax)
    guardar(fig, ruta)
