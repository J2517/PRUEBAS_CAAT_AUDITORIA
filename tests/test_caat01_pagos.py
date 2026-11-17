from datetime import date

from caat.pruebas import caat01_pagos as c01


def fac(num, concepto="INS-CONT", valor=32_000_000, fecha=date(2028, 3, 1), os="OS-1", acta="AE-1"):
    return dict(factura=num, fecha=fecha, concepto=concepto, valor=valor, os=os, acta=acta)


def test_duplicado_exacto_se_reporta_una_vez():
    facturas = [fac("A"), fac("A"), fac("B", os="OS-2")]
    assert [f["factura"] for f in c01.duplicados_exactos(facturas)] == ["A"]


def test_aproximado_dentro_de_tolerancia_y_ventana(cfg):
    a = fac("A", valor=32_000_000)
    b = fac("B", valor=32_300_000, fecha=date(2028, 3, 20))   # +0,94 %, 19 días
    pares = c01.candidatos_duplicado_aproximado([a, b], cfg)
    assert len(pares) == 1 and pares[0]["misma_os"]


def test_aproximado_fuera_de_ventana_no_se_reporta(cfg):
    a = fac("A")
    b = fac("B", fecha=date(2028, 5, 1))
    assert c01.candidatos_duplicado_aproximado([a, b], cfg) == []


def test_conceptos_recurrentes_se_ignoran(cfg):
    a = fac("A", concepto="LIC-PLAT")
    b = fac("B", concepto="LIC-PLAT", fecha=date(2028, 3, 10))
    assert c01.candidatos_duplicado_aproximado([a, b], cfg) == []


def test_depuracion_separa_confirmados_y_verificacion():
    pares = [dict(misma_os=True, sin_acta=False),
             dict(misma_os=False, sin_acta=True),
             dict(misma_os=False, sin_acta=False)]
    confirmados, verificar = c01.depurar_candidatos(pares)
    assert len(confirmados) == 1 and len(verificar) == 1


def test_diferencias_con_os_excluye_duplicados_ya_reportados():
    facturas = [fac("A", valor=100, os="OS-1"), fac("B", valor=120, os="OS-1")]
    assert [f["factura"] for f in c01.diferencias_con_os(facturas, {"OS-1": 100})] == ["B"]
    assert c01.diferencias_con_os(facturas, {"OS-1": 100}, excluir={"B"}) == []
