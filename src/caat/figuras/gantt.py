from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from caat.config import Config
from caat.figuras.estilo import DPI, GRIS, NARANJA, ROJO, guardar, limpiar_ejes
from caat.pruebas.caat05_cronograma import fecha_efectiva
from caat.simulacion.catalogos import Entregable


def dibujar(entregables: list[Entregable], cfg: Config, ruta: Path) -> None:
    inicio, corte = cfg.inicio_convenio, cfg.corte_auditoria
    orden = list(reversed(entregables))   # E1 arriba
    fig, ax = plt.subplots(figsize=(6.5, 3.3), dpi=DPI)
    for i, e in enumerate(orden):
        ax.barh(i, (e.plan - inicio).days, color=GRIS, height=.35, align="edge")
        ax.barh(i - .35, (fecha_efectiva(e, cfg) - inicio).days,
                color=NARANJA if e.real else ROJO, height=.35, align="edge")
    ax.set_yticks(np.arange(len(orden)))
    ax.set_yticklabels([e.id for e in orden])
    ax.set_xlabel(f"Días desde el inicio del convenio ({inicio:%d/%m/%Y})")
    ax.axvline((corte - inicio).days, color="k", ls="--", lw=.8)
    ax.text((corte - inicio).days - 4, len(orden) - .5, "Corte de\nauditoría", fontsize=7, ha="right")
    ax.legend(handles=[Patch(color=GRIS, label="Fecha planeada"),
                       Patch(color=NARANJA, label="Fecha real de entrega"),
                       Patch(color=ROJO, label="Pendiente a la fecha de corte")],
              frameon=False, fontsize=7, loc="lower left", bbox_to_anchor=(0, -0.42), ncol=3)
    limpiar_ejes(ax)
    guardar(fig, ruta)
