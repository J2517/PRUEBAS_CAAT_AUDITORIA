"""Prueba de regresión: el pipeline completo debe reproducir los resultados de referencia.

Los archivos de ``tests/golden`` se generaron con el script monolítico original
(semilla 2028). Si cambias a propósito la simulación o un criterio de auditoría,
regenera los golden con ``python tests/actualizar_golden.py`` y revisa el diff.
"""
import hashlib
import json
from pathlib import Path

import pytest

from caat.config import Config
from caat.main import ejecutar

GOLDEN = Path(__file__).parent / "golden"


@pytest.fixture(scope="module")
def salida(tmp_path_factory):
    carpeta = tmp_path_factory.mktemp("salida")
    ejecutar(Config(), carpeta, con_figuras=False)
    return carpeta


def test_results_json_igual_al_golden(salida):
    esperado = json.loads((GOLDEN / "results.json").read_text(encoding="utf-8"))
    obtenido = json.loads((salida / "results.json").read_text(encoding="utf-8"))
    for clave in esperado:
        assert obtenido[clave] == esperado[clave], f"Cambió la sección {clave}"


@pytest.mark.parametrize("nombre", sorted(json.loads((GOLDEN / "csv_sha256.json").read_text())))
def test_csv_identicos(salida, nombre):
    hashes = json.loads((GOLDEN / "csv_sha256.json").read_text())
    assert hashlib.sha256((salida / "data" / nombre).read_bytes()).hexdigest() == hashes[nombre]
