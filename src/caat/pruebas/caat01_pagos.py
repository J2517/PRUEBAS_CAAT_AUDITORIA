"""CAAT-01. Facturas, órdenes de servicio y actas de entrega."""
from __future__ import annotations

from collections import Counter

from caat.config import Config


def duplicados_exactos(facturas: list[dict]) -> list[dict]:
    """Facturas cuyo número aparece más de una vez (una entrada por número)."""
    conteo = Counter(f["factura"] for f in facturas)
    return list({f["factura"]: f for f in facturas if conteo[f["factura"]] > 1}.values())


def _es_par_sospechoso(a: dict, b: dict, cfg: Config) -> bool:
    return (a["concepto"] == b["concepto"]
            and a["concepto"] not in cfg.conceptos_recurrentes
            and a["factura"] != b["factura"]
            and abs((b["fecha"] - a["fecha"]).days) <= cfg.ventana_dias_duplicado
            and abs(a["valor"] - b["valor"]) / a["valor"] <= cfg.tolerancia_valor)


def candidatos_duplicado_aproximado(facturas: list[dict], cfg: Config) -> list[dict]:
    """Pares con mismo concepto, valor ±tolerancia y fechas cercanas, pero número distinto."""
    pares = []
    for i, a in enumerate(facturas):
        for b in facturas[i + 1:]:
            if _es_par_sospechoso(a, b, cfg):
                pares.append(dict(
                    factura_a=a["factura"], factura_b=b["factura"], concepto=a["concepto"],
                    valor_a=a["valor"], valor_b=b["valor"], dias=abs((b["fecha"] - a["fecha"]).days),
                    misma_os=a["os"] == b["os"], sin_acta=not (a["acta"] and b["acta"]),
                ))
    return pares


def depurar_candidatos(pares: list[dict]) -> tuple[list[dict], list[dict]]:
    """Separa los pares en ``(confirmados, en_verificacion)``.

    Se confirman los que comparten OS; los que no la comparten pero alguno
    carece de acta quedan para verificación manual; el resto se descarta.
    """
    confirmados = [p for p in pares if p["misma_os"]]
    verificar = [p for p in pares if not p["misma_os"] and p["sin_acta"]]
    return confirmados, verificar


def facturas_sin_acta(facturas: list[dict]) -> list[dict]:
    return [f for f in facturas if not f["acta"]]


def diferencias_con_os(facturas: list[dict], valor_os: dict[str, int],
                       excluir: set[str] = frozenset()) -> list[dict]:
    """Facturas cuyo valor difiere del aprobado en su OS (una entrada por número).

    ``excluir`` recibe los números de factura ya reportados como duplicados,
    para no contar dos veces el mismo hallazgo.
    """
    difs = [f for f in facturas if f["valor"] != valor_os[f["os"]] and f["factura"] not in excluir]
    return list({f["factura"]: f for f in difs}.values())


def ejecutar(facturas: list[dict], valor_os: dict[str, int], cfg: Config) -> dict:
    exactos = duplicados_exactos(facturas)
    candidatos = candidatos_duplicado_aproximado(facturas, cfg)
    aproximados, verificar = depurar_candidatos(candidatos)
    sin_acta = facturas_sin_acta(facturas)
    ya_reportadas = {p["factura_b"] for p in aproximados}
    dif_os = diferencias_con_os(facturas, valor_os, excluir=ya_reportadas)
    return dict(
        total_facturas=len(facturas), valor_total=sum(f["valor"] for f in facturas),
        exactos=len(exactos),
        exactos_lista=[dict(factura=f["factura"], concepto=f["concepto"], valor=f["valor"]) for f in exactos],
        candidatos_aprox=len(candidatos), aproximados=len(aproximados), aproximados_lista=aproximados,
        en_verificacion=len(verificar), verificacion_lista=verificar,
        sin_acta=len(sin_acta), sin_acta_valor=sum(f["valor"] for f in sin_acta),
        dif_os=len(dif_os), dif_os_valor=sum(f["valor"] - valor_os[f["os"]] for f in dif_os),
        monto_duplicado=sum(f["valor"] for f in exactos) + sum(p["valor_b"] for p in aproximados),
    )


def total_alertas(resultado: dict) -> int:
    """Alertas de pagos para el tablero."""
    r = resultado
    return r["exactos"] + r["aproximados"] + r["sin_acta"] + r["dif_os"]
