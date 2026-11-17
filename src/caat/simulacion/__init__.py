"""Generación de datasets simulados.

Estos módulos SOLO generan datos; no analizan nada. Todos reciben el mismo
``numpy.random.Generator`` y lo consumen en orden: el orden de llamada en
``caat.main`` determina los números obtenidos (ver README).
"""
from datetime import datetime

INICIO_MONITOREO = datetime(2028, 7, 1)
FIN_MONITOREO = datetime(2028, 10, 29)
