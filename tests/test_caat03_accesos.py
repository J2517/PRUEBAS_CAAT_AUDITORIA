from datetime import datetime

from caat.pruebas import caat03_accesos as c03


def ev(usuario="jrios.sca", op="UPDATE", ip="186.84.21.77", ticket="", ts=datetime(2028, 7, 4, 23, 0)):
    return dict(ts=ts, usuario=usuario, operacion=op, ip=ip, ticket=ticket)


def test_fuera_de_horario(cfg):
    assert c03.fuera_de_horario(datetime(2028, 7, 4, 5, 59), cfg)        # madrugada
    assert c03.fuera_de_horario(datetime(2028, 7, 4, 20, 0), cfg)        # noche
    assert c03.fuera_de_horario(datetime(2028, 7, 2, 10, 0), cfg)        # domingo
    assert not c03.fuera_de_horario(datetime(2028, 7, 4, 10, 0), cfg)    # martes laboral


def test_critico_requiere_las_cuatro_condiciones(cfg):
    assert c03.es_critico(ev(), cfg)
    assert not c03.es_critico(ev(ticket="CHG-123"), cfg)
    assert not c03.es_critico(ev(ip="10.20.1.15"), cfg)
    assert not c03.es_critico(ev(op="SELECT"), cfg)
    assert not c03.es_critico(ev(ts=datetime(2028, 7, 4, 10, 0)), cfg)


def test_acl(cfg):
    assert c03.es_autorizado(ev(usuario="operador.amb", op="UPDATE"), cfg)
    assert not c03.es_autorizado(ev(usuario="soporte.sca", op="UPDATE"), cfg)
    assert not c03.es_autorizado(ev(usuario="desconocido", op="SELECT"), cfg)


def test_cuentas_de_servicio_no_cuentan_fuera_de_horario(cfg):
    r = c03.ejecutar([ev(usuario="iot-gw", op="INSERT", ip="10.20.1.15")], cfg)
    assert r["fuera_horario"] == 0
