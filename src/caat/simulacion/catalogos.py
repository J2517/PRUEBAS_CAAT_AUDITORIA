"""Datos fijos (no aleatorios): entregables del convenio y evaluación COBIT."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Entregable:
    id: str
    descripcion: str
    plan: date
    real: date | None       # None = pendiente
    acta: str               # "Sí" | "No" | "Parcial"


def _d(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


ENTREGABLES = [
    Entregable(i, desc, _d(plan), _d(real), acta) for i, desc, plan, real, acta in [
        ("E1", "Diseño de arquitectura y plan de despliegue", "2028-03-15", "2028-04-20", "Sí"),
        ("E2", "Instalación de 80 sensores en contenedores", "2028-05-31", "2028-10-25", "No"),
        ("E3", "Telemetría en 12 vehículos recolectores", "2028-06-15", "2028-10-30", "No"),
        ("E4", "6 puntos de acopio con báscula IoT conectada", "2028-06-30", None, "No"),
        ("E5", "Plataforma en la nube en producción", "2028-05-15", "2028-09-05", "Parcial"),
        ("E6", "Tableros para la Secretaría de Medio Ambiente", "2028-07-31", None, "No"),
        ("E7", "Protocolo de calibración y certificados", "2028-05-31", None, "No"),
        ("E8", "Modelo de gobierno de datos", "2028-04-30", None, "No"),
    ]
]


@dataclass(frozen=True)
class ProcesoCobit:
    id: str
    proceso: str
    actual: int      # nivel de capacidad 0–5 (2028)
    objetivo: int    # nivel meta (2030)


EVALUACION_COBIT = [
    ProcesoCobit("EDM01", "Asegurar el establecimiento y mantenimiento del marco de gobierno", 1, 3),
    ProcesoCobit("EDM03", "Asegurar la optimización del riesgo", 1, 3),
    ProcesoCobit("APO10", "Gestionar los proveedores", 1, 3),
    ProcesoCobit("APO12", "Gestionar el riesgo", 1, 3),
    ProcesoCobit("APO14", "Gestionar los datos", 0, 3),
    ProcesoCobit("BAI01", "Gestionar los programas", 2, 3),
    ProcesoCobit("BAI03", "Gestionar la identificación y construcción de soluciones", 2, 3),
    ProcesoCobit("BAI07", "Gestionar la aceptación y transición del cambio", 1, 3),
    ProcesoCobit("DSS05", "Gestionar los servicios de seguridad", 1, 3),
    ProcesoCobit("DSS06", "Gestionar los controles de procesos de negocio", 1, 3),
    ProcesoCobit("MEA01", "Monitorizar el desempeño y la conformidad", 1, 3),
    ProcesoCobit("MEA03", "Monitorizar el cumplimiento de requisitos externos", 1, 3),
]
