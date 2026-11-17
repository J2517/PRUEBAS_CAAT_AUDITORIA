import numpy as np
import pytest

from caat.pruebas import caat04_benford as c04


def test_esperado_suma_uno():
    assert c04.esperado_benford().sum() == pytest.approx(1.0)


def test_primer_digito_descarta_no_positivos():
    assert c04.primer_digito(np.array([0.0, -3.0, 0.042, 7.5, 1234.0])).tolist() == [4, 7, 1]


def test_datos_benford_tienen_mad_bajo_y_redondos_alto():
    rng = np.random.default_rng(0)
    benford = 10 ** rng.uniform(0, 5, 20_000)          # log-uniforme ⇒ cumple Benford
    redondos = np.array([500, 600, 700, 800, 900] * 100, dtype=float)
    _, mad_b = c04.distribucion_primer_digito(benford)
    _, mad_r = c04.distribucion_primer_digito(redondos)
    assert mad_b < 0.006 < mad_r
