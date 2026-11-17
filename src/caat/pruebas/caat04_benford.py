"""CAAT-04. Ley de Benford (primer dígito): registros SENSOR vs. MANUAL."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DIGITOS = np.arange(1, 10)


def esperado_benford() -> np.ndarray:
    return np.log10(1 + 1 / DIGITOS)


def primer_digito(x: np.ndarray) -> np.ndarray:
    """Primer dígito significativo de cada valor positivo (los ≤ 0 se descartan)."""
    x = x[x > 0]
    return (x / 10 ** np.floor(np.log10(x))).astype(int)


def distribucion_primer_digito(x: np.ndarray) -> tuple[np.ndarray, float]:
    """Devuelve ``(proporciones observadas para 1..9, MAD frente a Benford)``."""
    d = primer_digito(x)
    obs = np.array([(d == k).mean() for k in DIGITOS])
    return obs, float(np.abs(obs - esperado_benford()).mean())


def _a_dict(v: np.ndarray) -> dict[int, float]:
    return {k + 1: round(float(p), 3) for k, p in enumerate(v)}


@dataclass
class ResultadoBenford:
    obs_sensor: np.ndarray
    obs_manual: np.ndarray
    mad_sensor: float
    mad_manual: float
    esperado: np.ndarray

    def resumen(self) -> dict:
        return dict(mad_sensor=round(self.mad_sensor, 4), mad_manual=round(self.mad_manual, 4),
                    obs_sensor=_a_dict(self.obs_sensor), obs_manual=_a_dict(self.obs_manual),
                    esperado=_a_dict(self.esperado))


def ejecutar(pesos_sensor: np.ndarray, pesos_manual: np.ndarray) -> ResultadoBenford:
    obs_s, mad_s = distribucion_primer_digito(pesos_sensor)
    obs_m, mad_m = distribucion_primer_digito(pesos_manual)
    return ResultadoBenford(obs_s, obs_m, mad_s, mad_m, esperado_benford())
