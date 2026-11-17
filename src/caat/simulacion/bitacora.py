"""Bitácora de accesos a la base de datos de la plataforma."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import numpy as np

from caat.simulacion import INICIO_MONITOREO

N_EVENTOS = 6000
DIAS_PERIODO = 120
HORAS_NOCTURNAS = [0, 1, 2, 3, 4, 5, 20, 21, 22, 23]
IPS_INTERNAS = ["10.20.1.15", "10.20.1.22", "10.20.3.4"]
IPS_EXTERNAS = ["186.84.21.77", "45.162.10.9"]
PROB_TICKET = 0.45


@dataclass(frozen=True)
class PerfilUsuario:
    peso: float                         # probabilidad de que el evento sea de este usuario
    operaciones: list[str]
    prob_operaciones: list[float]
    prob_ip_externa: float
    prob_fuera_horario: float | None    # None = cuenta de servicio, opera 24 h


PERFILES = {
    "iot-gw": PerfilUsuario(.55, ["INSERT", "SELECT"], [.97, .03], 0.0, None),
    "dashboard.ro": PerfilUsuario(.12, ["SELECT"], [1.0], 0.0, None),
    "operador.amb": PerfilUsuario(.12, ["SELECT", "UPDATE", "DELETE"], [.88, .11, .01], .02, .04),
    "soporte.sca": PerfilUsuario(.09, ["SELECT", "UPDATE", "DELETE"], [.80, .16, .04], .25, .15),
    "jrios.sca": PerfilUsuario(.06, ["SELECT", "UPDATE", "DELETE"], [.60, .33, .07], .45, .35),
    "admin": PerfilUsuario(.04, ["SELECT", "UPDATE", "DELETE"], [.55, .35, .10], .40, .30),
    "mcastro.alc": PerfilUsuario(.02, ["SELECT", "UPDATE"], [.70, .30], .30, .25),
}


def _evento(rng: np.random.Generator, usuario: str) -> dict:
    p = PERFILES[usuario]
    dia = INICIO_MONITOREO + timedelta(days=int(rng.integers(0, DIAS_PERIODO)))
    if p.prob_fuera_horario is None:
        hora = int(rng.integers(0, 24))
    elif rng.random() < p.prob_fuera_horario:
        hora = int(rng.choice(HORAS_NOCTURNAS))
    else:
        hora = int(rng.integers(7, 19))
        if dia.weekday() == 6:          # los usuarios humanos no trabajan el domingo
            dia -= timedelta(days=1)
    ts = dia.replace(hour=hora, minute=int(rng.integers(0, 60)))
    op = str(rng.choice(p.operaciones, p=p.prob_operaciones))
    ip = (str(rng.choice(IPS_EXTERNAS)) if rng.random() < p.prob_ip_externa
          else str(rng.choice(IPS_INTERNAS)))
    ticket = (f"CHG-{int(rng.integers(100, 999))}"
              if op in ("UPDATE", "DELETE") and rng.random() < PROB_TICKET else "")
    return dict(ts=ts, usuario=usuario, operacion=op, ip=ip, ticket=ticket)


def generar(rng: np.random.Generator, n_eventos: int = N_EVENTOS) -> list[dict]:
    """Eventos con ``ts`` como ``datetime`` (se convierte a texto al guardar)."""
    usuarios = list(PERFILES)
    elegidos = rng.choice(usuarios, n_eventos, p=[PERFILES[u].peso for u in usuarios])
    return [_evento(rng, str(u)) for u in elegidos]


def a_filas_csv(eventos: list[dict]) -> list[dict]:
    return [{**e, "ts": e["ts"].isoformat()} for e in eventos]
