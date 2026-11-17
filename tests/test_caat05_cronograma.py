from datetime import date

from caat.pruebas import caat05_cronograma as c05
from caat.simulacion.catalogos import Entregable


def test_pendiente_se_mide_hasta_el_corte(cfg):
    e = Entregable("X", "Prueba", date(2028, 11, 1), None, "No")
    assert c05.retraso_dias(e, cfg) == (cfg.corte_auditoria - date(2028, 11, 1)).days


def test_entregado_a_tiempo_tiene_retraso_cero_o_negativo(cfg):
    e = Entregable("X", "Prueba", date(2028, 5, 1), date(2028, 4, 28), "Sí")
    r = c05.ejecutar([e], cfg)
    assert r["entregables"][0]["retraso_dias"] == -3
    assert r["con_acta"] == 1 and r["retraso_mayor_120"] == 0
