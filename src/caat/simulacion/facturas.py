"""Facturas, órdenes de servicio (OS) y actas de entrega de SmartCityAndina."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np

# (código, descripción, valor unitario en COP)
CONCEPTOS = [
    ("LIC-PLAT", "Licenciamiento plataforma nube (mensual)", 18_500_000),
    ("INS-CONT", "Instalación sensores contenedor (lote 10)", 32_000_000),
    ("INS-VEH", "Instalación kit telemetría vehículo (lote 4)", 27_600_000),
    ("INS-ACO", "Instalación báscula IoT punto de acopio", 41_300_000),
    ("INT-API", "Integración API tableros de control", 24_800_000),
    ("SOP-MES", "Soporte y mantenimiento (mensual)", 9_700_000),
]
CONCEPTOS_MENSUALES = ("LIC-PLAT", "SOP-MES")
PROB_CONCEPTO_EVENTUAL = 0.38
ANIO = 2028
MESES = range(2, 12)

# Anomalías inyectadas
N_DUPLICADOS_EXACTOS = 2
CONCEPTOS_DUPLICABLES = ("INS-CONT", "INS-ACO", "INT-API")
DESFASE_DIAS_DUPLICADOS = [6, 11, 19]
FACTOR_VALOR_DUPLICADOS = [1.0, 0.995, 1.004]
N_SIN_ACTA = 3
N_OS_SUBVALORADAS = 2
FACTOR_OS_SUBVALORADA = 0.85


def _facturas_base(rng: np.random.Generator) -> list[dict]:
    facturas = []
    n = 0
    for mes in MESES:
        for codigo, descripcion, valor in CONCEPTOS:
            if codigo in CONCEPTOS_MENSUALES or rng.random() < PROB_CONCEPTO_EVENTUAL:
                n += 1
                facturas.append(dict(
                    factura=f"SCA-{1000 + n}",
                    fecha=date(ANIO, mes, int(rng.integers(3, 25))),
                    concepto=codigo, descripcion=descripcion, valor=valor,
                    os=f"OS-{2000 + n}", acta=f"AE-{3000 + n}",
                ))
    return facturas


def _inyectar_anomalias(rng: np.random.Generator, facturas: list[dict]) -> None:
    """Modifica ``facturas`` en el sitio: duplicados exactos, casi duplicados y faltas de acta."""
    n_base = len(facturas)
    # Duplicados exactos (misma factura repetida)
    for i in rng.choice(n_base, N_DUPLICADOS_EXACTOS, replace=False):
        facturas.append(dict(facturas[i]))
    # Casi duplicados: número distinto, fecha y valor ligeramente cambiados, sin acta
    candidatas = [i for i, f in enumerate(facturas[:n_base]) if f["concepto"] in CONCEPTOS_DUPLICABLES]
    elegidas = rng.choice(candidatas, len(DESFASE_DIAS_DUPLICADOS), replace=False)
    for k, (i, dias, factor) in enumerate(zip(elegidas, DESFASE_DIAS_DUPLICADOS, FACTOR_VALOR_DUPLICADOS)):
        f = dict(facturas[i])
        f.update(factura=f"SCA-{1900 + k}", fecha=f["fecha"] + timedelta(days=dias),
                 valor=int(round(f["valor"] * factor, -3)), acta="")
        facturas.append(f)
    # Facturas originales sin acta de entrega
    for i in rng.choice(n_base, N_SIN_ACTA, replace=False):
        facturas[i]["acta"] = ""


def _ordenes_servicio(rng: np.random.Generator, facturas: list[dict]) -> dict[str, int]:
    """Valor aprobado por OS; algunas quedan por debajo de lo facturado."""
    valor_os: dict[str, int] = {}
    for f in facturas:
        valor_os.setdefault(f["os"], f["valor"])
    for os_id in rng.choice(sorted(valor_os), N_OS_SUBVALORADAS, replace=False):
        valor_os[os_id] = int(round(valor_os[os_id] * FACTOR_OS_SUBVALORADA, -3))
    return valor_os


def generar(rng: np.random.Generator) -> tuple[list[dict], dict[str, int]]:
    """Devuelve ``(facturas ordenadas por fecha, {os: valor_os})``."""
    facturas = _facturas_base(rng)
    _inyectar_anomalias(rng, facturas)
    facturas.sort(key=lambda f: f["fecha"])
    return facturas, _ordenes_servicio(rng, facturas)
