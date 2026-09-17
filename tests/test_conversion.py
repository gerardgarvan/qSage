"""Tests for qseries/_conversion.py — Phase 4: Product Conversion.

Oracle values from Garvan's qseries doc pages only.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sage.all import QQ, LaurentSeriesRing
from qseries import (
    etamake, qetamake,
    theta2, theta3, theta4,
    etaq,
    EtaProduct, EProduct,
    QSeries,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ring():
    R = LaurentSeriesRing(QQ, 'q')
    return R, R.gen()


# ---------------------------------------------------------------------------
# CONV-02: etamake
# ---------------------------------------------------------------------------

def test_etamake_theta3():
    """CONV-02: etamake(theta3(q,100), q, 100) -> eta(2tau)^5 / (eta(4tau)^2 * eta(tau)^2)

    Oracle: Garvan etamake doc page / D-05 decision.
    factors: {(1,-2), (2,5), (4,-2)}, constant=1, r=0.
    """
    R, q = _make_ring()
    result = etamake(theta3(q, 100), q, 100)
    assert result.constant == 1
    assert QQ(result.r) == 0
    assert set(result.factors) == {(1, -2), (2, 5), (4, -2)}
    # Numeric round-trip
    s1 = result.to_series(50)
    s2 = theta3(q, 50)
    assert s1.series.add_bigoh(50) == s2.series.add_bigoh(50)


def test_etamake_theta4():
    """CONV-02: etamake(theta4(q,100), q, 100) -> eta(tau)^2 / eta(2tau)

    Oracle: Garvan etamake doc page / D-05 decision.
    factors: {(1,2), (2,-1)}, constant=1, r=0.
    """
    R, q = _make_ring()
    result = etamake(theta4(q, 100), q, 100)
    assert result.constant == 1
    assert QQ(result.r) == 0
    assert set(result.factors) == {(1, 2), (2, -1)}
    # Numeric round-trip
    s1 = result.to_series(50)
    s2 = theta4(q, 50)
    assert s1.series.add_bigoh(50) == s2.series.add_bigoh(50)


def test_etamake_theta2():
    """CONV-02: etamake(theta2(q,100), q, 100) -> 2 * eta(4tau)^2 / eta(2tau)

    Oracle: D-05 decision; r not gated (open question D-04/D-05).
    Asserts constant==2 and numeric round-trip only.
    """
    R, q = _make_ring()
    result = etamake(theta2(q, 100), q, 100)
    assert result.constant == 2
    # Numeric round-trip is the authoritative oracle (r value not asserted per plan)
    s1 = result.to_series(50)
    s2 = theta2(q, 50)
    # Both have r=s1.r; compare shifted series
    assert s1.r == s2.r
    assert s1.series.add_bigoh(50) == s2.series.add_bigoh(50)


# ---------------------------------------------------------------------------
# CONV-03: qetamake
# ---------------------------------------------------------------------------

def test_qetamake_triangular():
    """CONV-03: qetamake on triangular-number series -> EProduct({1:-1, 2:2})

    Triangular series = sum q^(n(n+1)/2) = etaq(q,2,T)^2 / etaq(q,1,T).
    Oracle: Garvan qetamake doc page.
    """
    R, q = _make_ring()
    T = 30
    # Build triangular-number series as QSeries
    f = etaq(q, 2, T) ** 2 / etaq(q, 1, T)
    result = qetamake(f, q, T)
    assert result.exponents == {1: -1, 2: 2}
    # Numeric round-trip
    s1 = result.to_series(20)
    s2 = f
    assert s1.series.add_bigoh(20) == s2.series.add_bigoh(20)


# ---------------------------------------------------------------------------
# CONV-04: jacprodmake (Plan 04-02)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-04: implemented in Plan 04-02")
def test_jacprodmake_basic():
    pass


@pytest.mark.skip(reason="CONV-04: implemented in Plan 04-02 (sqrt case)")
def test_jacprodmake_sqrt():
    pass


# ---------------------------------------------------------------------------
# CONV-08: jac2prod (Plan 04-02)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-08: implemented in Plan 04-02")
def test_jac2prod_basic():
    pass


@pytest.mark.skip(reason="CONV-08: implemented in Plan 04-02 (JAC(0,b) case)")
def test_jac2prod_zero():
    pass


# ---------------------------------------------------------------------------
# CONV-09: jac2series (Plan 04-02)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-09: implemented in Plan 04-02")
def test_jac2series_oracle():
    pass


# ---------------------------------------------------------------------------
# CONV-05: mprodmake (Plan 04-03)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-05: implemented in Plan 04-03")
def test_mprodmake():
    pass


# ---------------------------------------------------------------------------
# CONV-06: qfactor (Plan 04-03)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-06: implemented in Plan 04-03")
def test_qfactor_t8():
    pass


# ---------------------------------------------------------------------------
# CONV-07: zqfactor (Plan 04-03)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-07: implemented in Plan 04-03")
def test_zqfactor():
    pass


# ---------------------------------------------------------------------------
# CONV-10: qs2jaccombo (Plan 04-03)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-10: implemented in Plan 04-03")
def test_qs2jaccombo():
    pass


# ---------------------------------------------------------------------------
# CONV-11: findprod (Plan 04-03)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="CONV-11: implemented in Plan 04-03")
def test_findprod_trivial():
    pass
