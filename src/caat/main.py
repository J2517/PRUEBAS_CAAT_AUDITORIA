"""Orquestador: simula los datos, ejecuta las pruebas CAAT y genera las salidas.

Uso:
    python -m caat                        # salida en ./salida
    python -m caat --salida resultados --semilla 2028 --sin-figuras
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from caat import io_utils
from caat.config import Config
from caat.figuras import arquitectura, benford, estilo, gantt, madurez as fig_madurez, mapa, tablero
from caat.modelos import ENCABEZADO_LECTURAS, Lecturas
from caat.pruebas import (caat01_pagos, caat02_sensores, caat03_accesos, caat04_benford,
                          caat05_cronograma, madurez)
from caat.simulacion import alertas, bitacora, facturas as sim_facturas, sensores
from caat.simulacion.catalogos import ENTREGABLES, EVALUACION_COBIT


@dataclass
class DatosSimulados:
    facturas: list[dict]
    valor_os: dict[str, int]
    lecturas: Lecturas
    pesos_viaje: np.ndarray
    muestra_mapa: np.ndarray
    eventos: list[dict]
    alertas_semana: np.ndarray


def simular(cfg: Config) -> DatosSimulados:
    """Genera todos los datos aleatorios.

    ⚠ El ORDEN de estas llamadas define qué números produce la semilla. Si se
    cambia, cambian los resultados (y el test golden lo detectará).
    """
    rng = np.random.default_rng(cfg.semilla)
    facturas, valor_os = sim_facturas.generar(rng)
    lecturas = sensores.generar(rng, cfg.capacidad_kg)
    pesos_viaje = sensores.simular_pesos_viaje(rng, lecturas)
    fuera = caat02_sensores.fuera_de_area(lecturas.lat, lecturas.lon, cfg.bbox)
    muestra_mapa = mapa.seleccionar_muestra(rng, fuera)
    eventos = bitacora.generar(rng)
    alertas_semana = alertas.alertas_semanales(rng)
    return DatosSimulados(facturas, valor_os, lecturas, pesos_viaje, muestra_mapa, eventos, alertas_semana)


def guardar_datos(d: DatosSimulados, carpeta: Path) -> None:
    io_utils.guardar_csv_dicts(carpeta / "facturas.csv", d.facturas)
    io_utils.guardar_csv_dicts(carpeta / "ordenes_servicio.csv",
                               [dict(os=k, valor_os=v) for k, v in d.valor_os.items()])
    io_utils.guardar_csv_filas(carpeta / "lecturas_sensores.csv", ENCABEZADO_LECTURAS, d.lecturas.filas_csv())
    io_utils.guardar_csv_dicts(carpeta / "bitacora_bd.csv", bitacora.a_filas_csv(d.eventos))


def ejecutar_pruebas(d: DatosSimulados, cfg: Config) -> tuple[dict, caat04_benford.ResultadoBenford]:
    r_benford = caat04_benford.ejecutar(d.pesos_viaje, d.lecturas.peso[d.lecturas.manual])
    R = dict(
        caat01=caat01_pagos.ejecutar(d.facturas, d.valor_os, cfg),
        caat02=caat02_sensores.ejecutar(d.lecturas, cfg),
        caat03=caat03_accesos.ejecutar(d.eventos, cfg),
        caat04=r_benford.resumen(),
        caat05=caat05_cronograma.ejecutar(ENTREGABLES, cfg),
        madurez=madurez.brechas(EVALUACION_COBIT),
        madurez_prom=madurez.promedio_actual(EVALUACION_COBIT),
    )
    return R, r_benford


def generar_figuras(d: DatosSimulados, R: dict, r_benford, cfg: Config, carpeta: Path) -> None:
    estilo.aplicar()
    lec = d.lecturas
    fuera = caat02_sensores.fuera_de_area(lec.lat, lec.lon, cfg.bbox)
    benford.dibujar(r_benford, carpeta / "fig_benford.png")
    mapa.dibujar(lec.lat, lec.lon, fuera, d.muestra_mapa, cfg.bbox, carpeta / "fig_mapa.png")
    gantt.dibujar(ENTREGABLES, cfg, carpeta / "fig_gantt.png")
    fig_madurez.dibujar(EVALUACION_COBIT, carpeta / "fig_madurez.png")
    tablero.dibujar(R, d.alertas_semana, carpeta / "fig_tablero.png")
    arquitectura.dibujar(carpeta / "fig_arquitectura.png")


def ejecutar(cfg: Config, salida: Path, con_figuras: bool = True) -> dict:
    """Pipeline completo. Devuelve el diccionario de resultados."""
    carpeta_datos, carpeta_fig = salida / "data", salida / "fig"
    carpeta_datos.mkdir(parents=True, exist_ok=True)

    datos = simular(cfg)
    guardar_datos(datos, carpeta_datos)
    R, r_benford = ejecutar_pruebas(datos, cfg)
    if con_figuras:
        carpeta_fig.mkdir(parents=True, exist_ok=True)
        generar_figuras(datos, R, r_benford, cfg, carpeta_fig)
    io_utils.guardar_json(salida / "results.json", R)
    return R


def _argumentos(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulación de datos y pruebas CAAT – Proyecto 6.")
    p.add_argument("--salida", type=Path, default=Path("salida"), help="carpeta de salida (default: ./salida)")
    p.add_argument("--semilla", type=int, default=Config.semilla, help="semilla aleatoria (default: 2028)")
    p.add_argument("--sin-figuras", action="store_true", help="no generar los PNG")
    p.add_argument("--silencioso", action="store_true", help="no imprimir results.json en consola")
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = _argumentos(argv)
    cfg = replace(Config(), semilla=args.semilla)
    R = ejecutar(cfg, args.salida, con_figuras=not args.sin_figuras)
    if not args.silencioso:
        print(json.dumps(R, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
