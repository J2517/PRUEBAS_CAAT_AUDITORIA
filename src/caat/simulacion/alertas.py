"""Serie ilustrativa de alertas semanales para la maqueta del tablero.

OJO: estos valores son inventados (no salen de las pruebas CAAT). En el
informe deben presentarse como ilustrativos.
"""
from __future__ import annotations

import numpy as np

N_SEMANAS = 17


def alertas_semanales(rng: np.random.Generator) -> np.ndarray:
    return rng.poisson(lam=np.linspace(4, 14, N_SEMANAS))
