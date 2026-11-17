# Pruebas CAAT – Proyecto 6 MetalVerde Andina / SmartCityAndina

Genera datasets simulados con una semilla fija, ejecuta las pruebas CAAT y produce
`results.json`, los CSV de datos y las figuras PNG del informe.

## Uso

```bash
pip install -e ".[dev]"          # una vez
python -m caat                   # salida en ./salida  (data/, fig/, results.json)
python -m caat --salida resultados --sin-figuras --silencioso
pytest                           # pruebas unitarias + regresión
```

Sin instalar: `PYTHONPATH=src python -m caat`.

## Estructura

```
src/caat/
├── config.py          Criterios de auditoría: umbrales, ACL, área geográfica, fechas
├── modelos.py         Estructura de datos de las lecturas IoT
├── io_utils.py        Escritura de CSV/JSON
├── simulacion/        SOLO genera datos (usa el generador aleatorio)
│   ├── facturas.py    facturas, OS y anomalías inyectadas
│   ├── sensores.py    lecturas IoT y pesos por viaje
│   ├── bitacora.py    eventos de acceso a la BD
│   ├── alertas.py     serie ilustrativa del tablero
│   └── catalogos.py   entregables y evaluación COBIT (datos fijos)
├── pruebas/           SOLO analiza (funciones puras, sin aleatoriedad)
│   ├── caat01_pagos.py       duplicados, conciliación factura–OS–acta
│   ├── caat02_sensores.py    negativos, sobrecapacidad, geocerca, congelados, ediciones manuales
│   ├── caat03_accesos.py     ACL, horario, IP externa, tickets, accesos críticos
│   ├── caat04_benford.py     primer dígito, MAD
│   ├── caat05_cronograma.py  retrasos de entregables
│   └── madurez.py            brechas COBIT 2019
├── figuras/           SOLO dibuja (recibe resultados, guarda PNG)
└── main.py            orquestador y línea de comandos
tests/
├── test_caat0X_*.py   pruebas unitarias con datos hechos a mano
├── test_golden.py     regresión contra la salida del script original
└── actualizar_golden.py
```

## Reproducibilidad

Todo usa **un solo** generador (`numpy.random.default_rng(semilla)`), creado en
`main.simular()`. El orden de las llamadas en esa función define los números
obtenidos. Si se reordena, los resultados cambian y `test_golden.py` falla.

Los archivos de `tests/golden/` se tomaron del script monolítico original. La
versión refactorizada reproduce byte a byte los CSV, el `results.json` y las figuras.

Si cambias la simulación o un criterio **a propósito**, ejecuta
`python tests/actualizar_golden.py`, revisa el diff y actualiza las cifras del informe.

## Cambios de criterio frente al script original

- **Conciliación factura–OS (CAAT-01):** el original excluía las facturas con número
  `>= "SCA-1900"`, es decir, usaba un dato que solo conoce quien simuló. Ahora se
  excluyen las facturas ya confirmadas como duplicadas, que es el criterio que podría
  aplicar un auditor. En este dataset el resultado es el mismo.
- **Alertas por semana (tablero):** la serie es inventada (Poisson). Ahora vive en
  `simulacion/alertas.py` y debe presentarse como ilustrativa en el informe.
