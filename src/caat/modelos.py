"""Estructuras de datos compartidas entre simulación, pruebas y figuras."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ORIGEN_SENSOR = "SENSOR"
ORIGEN_MANUAL = "MANUAL"


@dataclass
class Lecturas:
    """Lecturas de sensores IoT en formato columnar (un arreglo por campo)."""

    dispositivos: list[str]   # inventario de dispositivos (orden de referencia)
    dispositivo: np.ndarray   # str, dispositivo de cada lectura
    ts: np.ndarray            # datetime64[s]
    peso: np.ndarray          # float, kg
    lat: np.ndarray
    lon: np.ndarray
    origen: np.ndarray        # "SENSOR" | "MANUAL"
    usuario: np.ndarray       # cuenta que registró la lectura

    def __len__(self) -> int:
        return len(self.peso)

    @property
    def manual(self) -> np.ndarray:
        return self.origen == ORIGEN_MANUAL

    def capacidad(self, capacidad_por_tipo: dict[str, int]) -> np.ndarray:
        """Capacidad nominal (kg) de cada lectura según el prefijo del dispositivo."""
        por_dispositivo = {d: capacidad_por_tipo[d[:3]] for d in self.dispositivos}
        return np.array([por_dispositivo[d] for d in self.dispositivo], dtype=float)

    def filas_csv(self):
        """Filas para ``lecturas_sensores.csv``."""
        ts_txt = self.ts.astype(str)
        for k in range(len(self)):
            yield [self.dispositivo[k], ts_txt[k], self.peso[k], self.lat[k], self.lon[k],
                   self.origen[k], self.usuario[k]]


ENCABEZADO_LECTURAS = ["dispositivo", "ts", "peso_kg", "lat", "lon", "origen", "usuario"]
