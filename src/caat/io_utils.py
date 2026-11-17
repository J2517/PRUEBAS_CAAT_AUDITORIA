"""Lectura y escritura de archivos de salida."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Sequence


def guardar_csv_dicts(ruta: Path, filas: Sequence[dict[str, Any]]) -> None:
    """Guarda una lista de diccionarios; las columnas salen de la primera fila."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


def guardar_csv_filas(ruta: Path, encabezado: Sequence[str], filas: Iterable[Sequence[Any]]) -> None:
    """Guarda filas posicionales (útil para datasets grandes generados al vuelo)."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)


def guardar_json(ruta: Path, datos: Any) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1, default=str)
