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
    """Oracle: Design decision (Phase 1, FOUND-01): QSeries stores its truncation order T."""
    s = make_series()
    qs = QSeries(s, T=20)
    assert qs.T == 20


def test_series_attr():
    """Oracle: Design decision (Phase 1, FOUND-01): the wrapped Sage series is kept as given."""
    s = make_series()
    qs = QSeries(s, T=20)
    assert qs.series is s


def test_default_r_is_zero():
    """Oracle: Design decision (Phase 1, FOUND-02): the default q-power shift is r = 0."""
    s = make_series()
    qs = QSeries(s, T=20)
    assert qs.r == 0


def test_rational_shift_stored():
    """Oracle: Design decision (Phase 1, FOUND-02): a rational shift is stored, needed for theta2's q^(1/4) (theta2 doc page)."""
    s = make_series()
    qs = QSeries(s, T=10, r=QQ(1)/4)
    assert qs.r == QQ(1)/4


def test_R_inferred_QQ():
    """Oracle: Design decision (Phase 1, FOUND-02): the coefficient ring R is inferred from the series parent (QQ)."""
    s = make_series(R=QQ)
    qs = QSeries(s, T=20)
    assert qs.R == QQ


def test_R_inferred_GF7():
    """Oracle: Design decision (Phase 1, FOUND-02): R inferred from the series parent (GF(p), used by the mod-p functions)."""
    s = make_series(R=GF(7))
    qs = QSeries(s, T=20)
    assert qs.R == GF(7)


def test_R_bivariate():
    """Oracle: Design decision (Phase 1, FOUND-02): R inferred as the Laurent polynomial ring in z (theta, tripleprod, zqfactor)."""
    z_ring = LaurentPolynomialRing(QQ, 'z')
    L = LaurentSeriesRing(z_ring, 'q')
    q = L.gen()
    s = (1 + q).add_bigoh(10)
    qs = QSeries(s, T=10)
    assert qs.R == z_ring


# --- Arithmetic truncation propagation ---

def test_add_truncation_propagates():
    """Oracle: Truncated-series arithmetic: a sum is known only to the smaller order min(T1, T2) (ROADMAP Phase 1 criterion 1)."""
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = sum(q**k for k in range(5)).add_bigoh(20)
    s2 = sum(q**k for k in range(5)).add_bigoh(15)
    qs1 = QSeries(s1, T=20)
    qs2 = QSeries(s2, T=15)
    result = qs1 + qs2
    assert result.T == 15


def test_mul_r_propagation():
    """Oracle: Exponent law q^r1 * q^r2 = q^(r1 + r2) (design decision D-12)."""
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(15)
    qs1 = QSeries(s1, T=20, r=QQ(1))
    qs2 = QSeries(s2, T=15, r=QQ(1)/4)
    result = qs1 * qs2
    assert result.r == QQ(5)/4


def test_div_r_propagation():
    """Oracle: Exponent law q^r1 / q^r2 = q^(r1 - r2) (design decision D-12)."""
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
    """r=1 and r=0 differ by integer 1 — should succeed.

    Oracle: Design decision D-12: shifts differing by an integer are aligned to the smaller shift.
    """
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(20)
    qs1 = QSeries(s1, T=20, r=QQ(1))
    qs2 = QSeries(s2, T=20, r=QQ(0))
    result = qs1 + qs2
    assert result.r == QQ(0)


def test_add_non_integer_shift_diff_raises():
    """r=1/4 and r=3/4 differ by 1/2 — not integer, must raise ValueError.

    Oracle: Design decision D-12: shifts differing by a non-integer cannot form one q^r * series, so raise ValueError.
    """
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(20)
    qs1 = QSeries(s1, T=20, r=QQ(1)/4)
    qs2 = QSeries(s2, T=20, r=QQ(3)/4)
    with pytest.raises(ValueError):
        _ = qs1 + qs2


def test_T_equals_series_prec():
    """T should equal Sage's actual precision after operation (D-13).

    Oracle: Design decision D-13: T equals Sage's actual precision after arithmetic.
    """
    L = LaurentSeriesRing(QQ, 'q')
    q = L.gen()
    s1 = (1 + q).add_bigoh(20)
    s2 = (1 + q).add_bigoh(15)
    qs1 = QSeries(s1, T=20)
    qs2 = QSeries(s2, T=15)
    result = qs1 + qs2
    assert result.T == int(result.series.prec())
