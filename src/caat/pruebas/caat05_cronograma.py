"""CAAT-05. Cronograma vs. entregables aceptados."""
from __future__ import annotations

import numpy as np

from caat.config import Config
from caat.simulacion.catalogos import Entregable


def fecha_efectiva(e: Entregable, cfg: Config):
    """Fecha real de entrega o, si está pendiente, la fecha de corte de la auditoría."""
    return e.real or cfg.corte_auditoria


def retraso_dias(e: Entregable, cfg: Config) -> int:
    return (fecha_efectiva(e, cfg) - e.plan).days


def ejecutar(entregables: list[Entregable], cfg: Config) -> dict:
    filas = [dict(id=e.id, entregable=e.descripcion, plan=e.plan.isoformat(),
                  real=e.real.isoformat() if e.real else "Pendiente", acta=e.acta,
                  retraso_dias=retraso_dias(e, cfg))
             for e in entregables]
    return dict(
        entregables=filas,
        retraso_prom=int(np.mean([f["retraso_dias"] for f in filas])),
        con_acta=sum(f["acta"] == "Sí" for f in filas),
        retraso_mayor_120=sum(f["retraso_dias"] > cfg.umbral_retraso_dias for f in filas),
    )
