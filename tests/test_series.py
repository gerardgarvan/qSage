"""Tests for QSeries wrapper class (qseries/_series.py).

Run with: sage -python -m pytest tests/test_series.py -x -q
"""
import pytest
from sage.all import QQ
from sage.all import GF
from sage.all import LaurentSeriesRing
from sage.all import LaurentPolynomialRing

from qseries._series import QSeries


def make_series(R=QQ):
    L = LaurentSeriesRing(R, 'q')
    q = L.gen()
    # 1 + q + q^2 + ... + O(q^20)
    s = sum(q**k for k in range(5))
    return s.add_bigoh(20)


# --- Basic construction ---

def test_T_stored():
    s = make_series()
    qs = QSeries(s, T=20)
    assert qs.T == 20


def test_series_attr():
    s = make_series()
    qs = QSeries(s, T=20)
    assert qs.series is s


def test_default_r_is_zero():
    s = make_series()
    qs = QSeries(s, T=20)
    assert qs.r == 0


def test_rational_shift_stored():
    s = make_series()
    qs = QSeries(s, T=10, r=QQ(1)/4)
    assert qs.r == QQ(1)/4


def test_R_inferred_QQ():
    s = make_series(R=QQ)
    qs = QSeries(s, T=20)
    assert qs.R == QQ


def test_R_inferred_GF7():
    s = make_series(R=GF(7))
    qs = QSeries(s, T=20)
    assert qs.R == GF(7)


def test_R_bivariate():
    z_ring = LaurentPolynomialRing(QQ, 'z')
    L = LaurentSeriesRing(z_ring, 'q')
    q = L.gen()
    s = (1 + q).add_bigoh(10)
    qs = QSeries(s, T=10)
    assert qs.R == z_ring


# --- Arithmetic truncation propagation ---

def test_add_truncation_propagates():
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = sum(q**k for k in range(5)).add_bigoh(20)
    s2 = sum(q**k for k in range(5)).add_bigoh(15)
    qs1 = QSeries(s1, T=20)
    qs2 = QSeries(s2, T=15)
    result = qs1 + qs2
    assert result.T == 15


def test_mul_r_propagation():
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(15)
    qs1 = QSeries(s1, T=20, r=QQ(1))
    qs2 = QSeries(s2, T=15, r=QQ(1)/4)
    result = qs1 * qs2
    assert result.r == QQ(5)/4


def test_div_r_propagation():
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(15)
    qs1 = QSeries(s1, T=20, r=QQ(1))
    qs2 = QSeries(s2, T=15, r=QQ(1)/4)
    result = qs1 / qs2
    assert result.r == QQ(3)/4


# --- Shift alignment in addition ---

def test_add_integer_shift_diff_works():
    """r=1 and r=0 differ by integer 1 — should succeed."""
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(20)
    qs1 = QSeries(s1, T=20, r=QQ(1))
    qs2 = QSeries(s2, T=20, r=QQ(0))
    result = qs1 + qs2
    assert result.r == QQ(0)


def test_add_non_integer_shift_diff_raises():
    """r=1/4 and r=3/4 differ by 1/2 — not integer, must raise ValueError."""
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(20)
    qs1 = QSeries(s1, T=20, r=QQ(1)/4)
    qs2 = QSeries(s2, T=20, r=QQ(3)/4)
    with pytest.raises(ValueError):
        _ = qs1 + qs2


def test_T_equals_series_prec():
    """T should equal Sage's actual precision after operation (D-13)."""
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(15)
    qs1 = QSeries(s1, T=20)
    qs2 = QSeries(s2, T=15)
    result = qs1 + qs2
    assert result.T == int(result.series.prec())
