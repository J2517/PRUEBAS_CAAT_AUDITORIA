"""Maqueta del tablero de auditoría continua."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from caat.figuras.estilo import AZUL, DPI, NARANJA, ROJO, TURQUESA, guardar, limpiar_ejes
from caat.pruebas import caat01_pagos, caat02_sensores

UMBRAL_ESCALAMIENTO = 8


def _kpis(R: dict) -> list[tuple[str, object, str]]:
    c1, c2, c3 = R["caat01"], R["caat02"], R["caat03"]
    return [("Accesos críticos\na la BD", c3["criticos"], ROJO),
            ("Lecturas\nanómalas", f'{c2["pct_anomalas"]} %', NARANJA),
            ("Ediciones manuales\nno autorizadas", c2["manuales_no_aut"], ROJO),
            ("Facturas\nsin acta", c1["sin_acta"], NARANJA),
            ("Sensores sin\ncalibración", len(c2["congelados"]), NARANJA),
            ("Madurez COBIT\npromedio", R["madurez_prom"], AZUL)]


def _alertas_por_dominio(R: dict) -> tuple[list[str], list[int], list[str]]:
    filas = [("Pagos", caat01_pagos.total_alertas(R["caat01"]), ROJO),
             ("Lecturas IoT", caat02_sensores.total_alertas_lecturas(R["caat02"]), NARANJA),
             ("Accesos BD", R["caat03"]["criticos"], ROJO),
             ("Ediciones\nmanuales", R["caat02"]["manuales_no_aut"], ROJO),
             ("Contractual", R["caat05"]["retraso_mayor_120"], TURQUESA)]
    cats, vals, colores = zip(*filas)
    return list(cats), list(vals), list(colores)


def dibujar(R: dict, alertas_semana: np.ndarray, ruta: Path) -> None:
    """``R`` es el diccionario completo de resultados; ``alertas_semana`` es ilustrativa."""
    fig = plt.figure(figsize=(7.5, 4.6), dpi=DPI)
    fig.patch.set_facecolor("#F4F6F8")
    fig.text(.02, .95, "Tablero de auditoría continua – Convenio de trazabilidad de residuos, Manizales",
             fontsize=11, weight="bold")
    fig.text(.02, .91, "Corte simulado: 28/10/2028 · Fuentes: plataforma SmartCityAndina, ERP GesMetal, "
             "bitácora de BD, actas", fontsize=7, color="#555")

    for i, (titulo, valor, color) in enumerate(_kpis(R)):
        a = fig.add_axes([.02 + i * .163, .70, .15, .17])
        a.set_xticks([])
        a.set_yticks([])
        a.set_facecolor("white")
        for s in a.spines.values():
            s.set_color(color)
        a.text(.5, .64, str(valor), ha="center", va="center", fontsize=15, weight="bold", color=color)
        a.text(.5, .22, titulo, ha="center", va="center", fontsize=6.5)

    a1 = fig.add_axes([.06, .1, .40, .5])
    semanas = np.arange(1, len(alertas_semana) + 1)
    a1.plot(semanas, alertas_semana, "-o", ms=3, color=ROJO)
    a1.set_title("Alertas por semana (jul.–oct. 2028)", fontsize=8)
    a1.set_xlabel("Semana", fontsize=7)
    a1.tick_params(labelsize=6)
    a1.axhline(UMBRAL_ESCALAMIENTO, ls="--", color="gray", lw=.8)
    a1.text(1, UMBRAL_ESCALAMIENTO + .4, "Umbral de escalamiento", fontsize=6, color="gray")
    limpiar_ejes(a1)

    a2 = fig.add_axes([.60, .1, .36, .5])
    cats, vals, colores = _alertas_por_dominio(R)
    a2.barh(cats, vals, color=colores)
    for y, v in enumerate(vals):
        a2.text(v + 1, y, str(v), va="center", fontsize=6)
    a2.set_title("Alertas acumuladas por dominio", fontsize=8)
    a2.tick_params(labelsize=6)
    limpiar_ejes(a2)
    guardar(fig, ruta, ajustar=False)
