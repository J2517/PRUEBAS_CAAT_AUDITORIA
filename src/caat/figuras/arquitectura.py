"""Diagrama de la arquitectura de la auditoría continua (estático)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from caat.figuras.estilo import DPI, guardar

AZUL_CLARO, AMARILLO, SALMON, VERDE_CLARO = "#DCE6F2", "#FFF2CC", "#FCE4D6", "#E2EFDA"
FUENTES = ["Sensores IoT /\nplataforma nube", "Bitácora BD\n(logs)", "ERP GesMetal\n(pagos, OC)",
           "SECOP / contratos\ny actas"]


def _caja(ax, x, y, w, h, texto, color):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=color, ec="#333", lw=.8))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=7)


def _flecha(ax, destino, origen, lw=.8):
    ax.annotate("", destino, origen, arrowprops=dict(arrowstyle="->", lw=lw))


def dibujar(ruta: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.2), dpi=DPI)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.4)
    for i, texto in enumerate(FUENTES):
        _caja(ax, .1, 3.3 - i * 1.0, 1.9, .8, texto, AZUL_CLARO)
        _flecha(ax, (2.7, 2.15), (2.0, 3.7 - i * 1.0), lw=.7)
    _caja(ax, 2.7, 1.2, 1.9, 1.9, "Extracción diaria\n(ETL con hash\nSHA-256 para\nintegridad)", AMARILLO)
    _caja(ax, 5.2, 1.2, 1.9, 1.9, "Motor de reglas\nCAAT (Python/SQL)\nR01–R12", SALMON)
    _caja(ax, 7.7, 2.4, 2.1, 1.0, "Tablero de alertas\n(semáforo, KPI)", VERDE_CLARO)
    _caja(ax, 7.7, .8, 2.1, 1.0, "Gestión de casos\n(responsable, SLA)", VERDE_CLARO)
    _flecha(ax, (5.2, 2.15), (4.6, 2.15))
    _flecha(ax, (7.7, 2.9), (7.1, 2.4))
    _flecha(ax, (7.7, 1.3), (7.1, 1.8))
    ax.text(8.75, .35, "Comité de auditoría / comité directivo", ha="center", fontsize=7, style="italic")
    guardar(fig, ruta)
