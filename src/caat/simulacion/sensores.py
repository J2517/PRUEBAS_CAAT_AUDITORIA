"""Lecturas de sensores IoT (peso, ubicación, origen del registro)."""
from __future__ import annotations

import numpy as np

from caat.modelos import ORIGEN_MANUAL, ORIGEN_SENSOR, Lecturas
from caat.simulacion import FIN_MONITOREO, INICIO_MONITOREO

DISPOSITIVOS = ([f"CNT-{i:03d}" for i in range(1, 81)]
                + [f"VEH-{i:02d}" for i in range(1, 13)]
                + [f"ACO-{i:02d}" for i in range(1, 7)])
PASO_HORAS = 4
CENTRO = (5.0689, -75.5174)            # lat, lon de referencia (Manizales)
DISPERSION_INSTALACION = 0.02          # grados entre dispositivos
DISPERSION_LECTURA = {"VEH": 0.015, "OTRO": 0.002}
CUENTA_GATEWAY = "iot-gw"

# Anomalías inyectadas (en el orden en que se toman del índice aleatorio)
N_NEGATIVOS = 61
N_SOBRE_CAPACIDAD = 37
N_FUERA_AREA = 43
N_MANUALES = 73
ZONA_FUERA = dict(lat=(4.60, 4.75), lon=(-74.20, -74.00))   # Bogotá
PESOS_MANUALES = [500, 600, 700, 800, 900, 750, 650]
USUARIOS_MANUALES = ["jrios.sca", "admin", "operador.amb", "mcastro.alc", "soporte.sca"]
PROB_USUARIOS_MANUALES = [0.30, 0.28, 0.17, 0.10, 0.15]
SENSORES_CONGELADOS = ["CNT-017", "CNT-044", "CNT-061", "ACO-05"]


def _n_pasos() -> int:
    return int((FIN_MONITOREO - INICIO_MONITOREO).total_seconds() // (PASO_HORAS * 3600))


def generar(rng: np.random.Generator, capacidad_por_tipo: dict[str, int]) -> Lecturas:
    T, D = _n_pasos(), len(DISPOSITIVOS)
    N = D * T
    cap = np.repeat([capacidad_por_tipo[d[:3]] for d in DISPOSITIVOS], T).astype(float)
    dispositivo = np.repeat(np.array(DISPOSITIVOS), T)
    tidx = np.tile(np.arange(T), D)
    es_vehiculo = np.char.startswith(dispositivo, "VEH")

    peso = (rng.uniform(0.05, 0.9, N) * cap).round(1)
    lat0 = np.repeat(CENTRO[0] + rng.normal(0, DISPERSION_INSTALACION, D), T)
    lon0 = np.repeat(CENTRO[1] + rng.normal(0, DISPERSION_INSTALACION, D), T)
    sd = np.where(es_vehiculo, DISPERSION_LECTURA["VEH"], DISPERSION_LECTURA["OTRO"])
    lat = (lat0 + rng.normal(0, 1, N) * sd).round(5)
    lon = (lon0 + rng.normal(0, 1, N) * sd).round(5)
    origen = np.full(N, ORIGEN_SENSOR, dtype=object)
    usuario = np.full(N, CUENTA_GATEWAY, dtype=object)

    # --- anomalías -------------------------------------------------------------
    idx = rng.choice(N, N_NEGATIVOS + N_SOBRE_CAPACIDAD + N_FUERA_AREA + N_MANUALES, replace=False)
    cortes = np.cumsum([N_NEGATIVOS, N_SOBRE_CAPACIDAD, N_FUERA_AREA])
    i_neg, i_sobre, i_fuera, i_man = np.split(idx, cortes)

    peso[i_neg] = -rng.uniform(5, 400, len(i_neg)).round(1)
    peso[i_sobre] = (cap[i_sobre] * rng.uniform(1.3, 4, len(i_sobre))).round(1)
    lat[i_fuera] = rng.uniform(*ZONA_FUERA["lat"], len(i_fuera)).round(5)
    lon[i_fuera] = rng.uniform(*ZONA_FUERA["lon"], len(i_fuera)).round(5)
    origen[i_man] = ORIGEN_MANUAL
    peso[i_man] = rng.choice(PESOS_MANUALES, len(i_man)).astype(float)
    usuario[i_man] = rng.choice(USUARIOS_MANUALES, len(i_man), p=PROB_USUARIOS_MANUALES)
    for s in SENSORES_CONGELADOS:
        sel = (dispositivo == s) & (origen == ORIGEN_SENSOR)
        peso[sel] = float(rng.integers(100, 400))

    ts = (np.datetime64(INICIO_MONITOREO, "s")
          + tidx.astype("timedelta64[h]") * PASO_HORAS).astype("datetime64[s]")
    return Lecturas(dispositivos=list(DISPOSITIVOS), dispositivo=dispositivo, ts=ts, peso=peso,
                    lat=lat, lon=lon, origen=origen, usuario=usuario)


def simular_pesos_viaje(rng: np.random.Generator, lecturas: Lecturas) -> np.ndarray:
    """Pesos acumulados por viaje (vehículos y acopio), que abarcan varios órdenes de
    magnitud; se usan como población de referencia para la prueba de Benford."""
    sel = ((np.char.startswith(lecturas.dispositivo, "VEH") | np.char.startswith(lecturas.dispositivo, "ACO"))
           & ~lecturas.manual & (lecturas.peso > 0))
    return lecturas.peso[sel] * rng.lognormal(0, 1.1, sel.sum())
