"""CAAT-02. Validación de lecturas de sensores IoT."""
from __future__ import annotations

from collections import Counter

import numpy as np

from caat.config import Config
from caat.modelos import Lecturas


def fuera_de_area(lat: np.ndarray, lon: np.ndarray, bbox: dict[str, float]) -> np.ndarray:
    dentro = ((lat >= bbox["lat_min"]) & (lat <= bbox["lat_max"])
              & (lon >= bbox["lon_min"]) & (lon <= bbox["lon_max"]))
    return ~dentro


def dispositivos_congelados(lecturas: Lecturas) -> list[str]:
    """Dispositivos cuyas lecturas automáticas no varían nunca (posible falta de calibración)."""
    automatica = ~lecturas.manual
    congelados = []
    for d in lecturas.dispositivos:
        pesos = lecturas.peso[(lecturas.dispositivo == d) & automatica]
        if pesos.size and np.std(pesos) == 0:   # sin lecturas automáticas no hay evidencia
            congelados.append(d)
    return congelados


def mascaras(lecturas: Lecturas, cfg: Config) -> dict[str, np.ndarray]:
    """Una máscara booleana por tipo de anomalía."""
    return dict(
        negativo=lecturas.peso < 0,
        sobre_capacidad=lecturas.peso > lecturas.capacidad(cfg.capacidad_kg),
        fuera_area=fuera_de_area(lecturas.lat, lecturas.lon, cfg.bbox),
        manual=lecturas.manual,
    )


def ejecutar(lecturas: Lecturas, cfg: Config) -> dict:
    m = mascaras(lecturas, cfg)
    usuarios_manual = lecturas.usuario[m["manual"]]
    no_autorizadas = [u for u in usuarios_manual if u not in cfg.usuarios_edicion_manual]
    anomala = m["negativo"] | m["sobre_capacidad"] | m["fuera_area"] | m["manual"]
    n = len(lecturas)
    return dict(
        lecturas=n, dispositivos=len(lecturas.dispositivos),
        negativos=int(m["negativo"].sum()), sobre_capacidad=int(m["sobre_capacidad"].sum()),
        fuera_area=int(m["fuera_area"].sum()), congelados=dispositivos_congelados(lecturas),
        manuales=int(m["manual"].sum()), manuales_no_aut=len(no_autorizadas),
        manual_por_usuario=dict(Counter(usuarios_manual).most_common()),
        anomalas=int(anomala.sum()), pct_anomalas=round(100 * anomala.sum() / n, 2),
    )


def total_alertas_lecturas(resultado: dict) -> int:
    r = resultado
    return r["negativos"] + r["sobre_capacidad"] + r["fuera_area"]
