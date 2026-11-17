"""Parámetros de auditoría: criterios, umbrales y datos maestros.

Aquí vive todo lo que un auditor podría querer ajustar o citar en el informe.
Los parámetros propios de la *simulación* (tasas de anomalías, perfiles de
usuarios, etc.) están en el paquete ``caat.simulacion``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


def _bbox_manizales() -> dict[str, float]:
    """Área metropolitana Manizales–Villamaría."""
    return dict(lat_min=4.95, lat_max=5.15, lon_min=-75.62, lon_max=-75.38)


def _acl_convenio() -> dict[str, frozenset[str]]:
    """Matriz de accesos aprobada en el anexo técnico del convenio (simulada)."""
    return {
        "iot-gw": frozenset({"INSERT", "SELECT"}),
        "operador.amb": frozenset({"SELECT", "UPDATE"}),
        "dashboard.ro": frozenset({"SELECT"}),
        "soporte.sca": frozenset({"SELECT"}),
    }


def _capacidad_por_tipo() -> dict[str, int]:
    """Capacidad nominal (kg) según el prefijo del dispositivo (dato maestro)."""
    return {"CNT": 1200, "VEH": 8000, "ACO": 15000}


@dataclass(frozen=True)
class Config:
    """Configuración de una ejecución completa."""

    semilla: int = 2028

    # CAAT-01: pagos
    conceptos_recurrentes: tuple[str, ...] = ("LIC-PLAT", "SOP-MES")
    tolerancia_valor: float = 0.01          # ±1 % entre facturas casi duplicadas
    ventana_dias_duplicado: int = 30

    # CAAT-02: lecturas IoT
    bbox: dict[str, float] = field(default_factory=_bbox_manizales)
    capacidad_kg: dict[str, int] = field(default_factory=_capacidad_por_tipo)
    usuarios_edicion_manual: frozenset[str] = frozenset({"operador.amb"})

    # CAAT-03: accesos a la BD
    acl: dict[str, frozenset[str]] = field(default_factory=_acl_convenio)
    cuentas_servicio: frozenset[str] = frozenset({"iot-gw", "dashboard.ro"})
    cuenta_generica: str = "admin"
    operaciones_privilegiadas: frozenset[str] = frozenset({"UPDATE", "DELETE"})
    hora_inicio_laboral: int = 6            # antes de esta hora = fuera de horario
    hora_fin_laboral: int = 20              # desde esta hora = fuera de horario
    dias_no_laborales: frozenset[int] = frozenset({6})   # 6 = domingo
    prefijo_red_interna: str = "10."

    # CAAT-05: cronograma
    inicio_convenio: date = date(2028, 2, 1)
    corte_auditoria: date = date(2028, 11, 30)
    umbral_retraso_dias: int = 120
