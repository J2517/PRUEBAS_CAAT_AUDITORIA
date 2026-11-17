"""CAAT-03. Bitácora de accesos a la base de datos."""
from __future__ import annotations

from collections import Counter
from datetime import datetime

from caat.config import Config


def fuera_de_horario(ts: datetime, cfg: Config) -> bool:
    return (ts.hour < cfg.hora_inicio_laboral or ts.hour >= cfg.hora_fin_laboral
            or ts.weekday() in cfg.dias_no_laborales)


def es_privilegiado(e: dict, cfg: Config) -> bool:
    return e["operacion"] in cfg.operaciones_privilegiadas


def es_ip_externa(e: dict, cfg: Config) -> bool:
    return not e["ip"].startswith(cfg.prefijo_red_interna)


def es_autorizado(e: dict, cfg: Config) -> bool:
    return e["operacion"] in cfg.acl.get(e["usuario"], frozenset())


def es_critico(e: dict, cfg: Config) -> bool:
    """Operación privilegiada, sin ticket de cambio, desde IP externa y fuera de horario."""
    return (es_privilegiado(e, cfg) and not e["ticket"]
            and es_ip_externa(e, cfg) and fuera_de_horario(e["ts"], cfg))


def ejecutar(eventos: list[dict], cfg: Config) -> dict:
    priv = [e for e in eventos if es_privilegiado(e, cfg)]
    no_aut = [e for e in eventos if not es_autorizado(e, cfg)]
    fh = [e for e in eventos if fuera_de_horario(e["ts"], cfg) and e["usuario"] not in cfg.cuentas_servicio]
    ip_ext = [e for e in eventos if es_ip_externa(e, cfg)]
    sin_ticket = [e for e in priv if not e["ticket"]]
    criticos = [e for e in eventos if es_critico(e, cfg)]
    return dict(
        eventos=len(eventos), privilegiados=len(priv), no_autorizados=len(no_aut),
        fuera_horario=len(fh), ip_externa=len(ip_ext), priv_sin_ticket=len(sin_ticket),
        criticos=len(criticos),
        cuentas_genericas=sum(e["usuario"] == cfg.cuenta_generica for e in eventos),
        no_aut_por_usuario=dict(Counter(e["usuario"] for e in no_aut).most_common()),
        criticos_por_usuario=dict(Counter(e["usuario"] for e in criticos).most_common()),
    )
