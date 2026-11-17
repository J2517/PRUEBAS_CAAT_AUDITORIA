import numpy as np

from caat.modelos import Lecturas
from caat.pruebas import caat02_sensores as c02


def lecturas(dispositivo, peso, lat=None, lon=None, origen=None, usuario=None):
    n = len(peso)
    return Lecturas(
        dispositivos=list(dict.fromkeys(dispositivo)),
        dispositivo=np.array(dispositivo),
        ts=np.arange(n).astype("datetime64[h]").astype("datetime64[s]"),
        peso=np.array(peso, dtype=float),
        lat=np.array(lat if lat is not None else [5.05] * n),
        lon=np.array(lon if lon is not None else [-75.5] * n),
        origen=np.array(origen or ["SENSOR"] * n, dtype=object),
        usuario=np.array(usuario or ["iot-gw"] * n, dtype=object),
    )


def test_negativos_y_sobre_capacidad(cfg):
    lec = lecturas(["CNT-001"] * 3, [-5, 600, 1500])   # capacidad CNT = 1200 kg
    r = c02.ejecutar(lec, cfg)
    assert r["negativos"] == 1 and r["sobre_capacidad"] == 1


def test_fuera_de_area(cfg):
    fuera = c02.fuera_de_area(np.array([5.05, 4.70]), np.array([-75.5, -74.1]), cfg.bbox)
    assert fuera.tolist() == [False, True]


def test_sensor_congelado_ignora_registros_manuales():
    lec = lecturas(["CNT-001"] * 3 + ["CNT-002"] * 2, [300, 300, 800, 100, 200],
                   origen=["SENSOR", "SENSOR", "MANUAL", "SENSOR", "SENSOR"])
    assert c02.dispositivos_congelados(lec) == ["CNT-001"]


def test_edicion_manual_no_autorizada(cfg):
    lec = lecturas(["CNT-001"] * 3, [500, 600, 700], origen=["MANUAL"] * 3,
                   usuario=["admin", "operador.amb", "jrios.sca"])
    r = c02.ejecutar(lec, cfg)
    assert r["manuales"] == 3 and r["manuales_no_aut"] == 2
