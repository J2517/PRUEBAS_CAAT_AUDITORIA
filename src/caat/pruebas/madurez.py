"""Madurez de gobierno de I&T (COBIT 2019, capacidad 0–5)."""
from __future__ import annotations

import numpy as np

from caat.simulacion.catalogos import ProcesoCobit


def brechas(evaluacion: list[ProcesoCobit]) -> list[dict]:
    return [dict(id=p.id, proceso=p.proceso, actual=p.actual, objetivo=p.objetivo,
                 brecha=p.objetivo - p.actual) for p in evaluacion]


def promedio_actual(evaluacion: list[ProcesoCobit]) -> float:
    return round(float(np.mean([p.actual for p in evaluacion])), 2)
