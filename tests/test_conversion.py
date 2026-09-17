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
    jacprodmake, jac2prod, jac2series,
    mprodmake, qfactor, zqfactor, qs2jaccombo, findprod,
    MProduct, QFactorResult,
    theta2, theta3, theta4,
    etaq, tripleprod,
    EtaProduct, EProduct, JacProduct, PochProduct,
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

def test_jacprodmake_basic():
    """CONV-04: jacprodmake(tripleprod(q,q^5,10), q, 10) -> JacProduct with factor (1,5,1).

    Oracle: Garvan jacprodmake doc page / D-08.
    """
    R, q = _make_ring()
    T = 10
    f = tripleprod(q, q**5, T)
    result = jacprodmake(f, q, T)
    assert isinstance(result, JacProduct)
    assert len(result.factors) == 1
    a, b, e = result.factors[0]
    assert (a, b) == (1, 5)
    assert QQ(e) == 1
    # Numeric round-trip
    s1 = result.to_series(T)
    assert s1.series.add_bigoh(T) == f.series.add_bigoh(T)


def test_jacprodmake_sqrt():
    """CONV-04 (mandatory D-08): jacprodmake(sqrt(JAC(7,14)/JAC(0,14)), q, 40) has factor (7,14,1/2).

    Oracle: Garvan tutorial D-08 mandatory sqrt example.
    """
    R, q = _make_ring()
    T = 40
    # Build JAC(7,14,inf) = tripleprod(q^7, q^14, T)
    jac7_14 = tripleprod(q**7, q**14, T)
    # Build JAC(0,14,inf) = (q^14;q^14)_inf (Pochhammer product, not theta sum)
    R2 = jac7_14.series.parent()
    q_var = R2.gen()
    jac0_14_series = R2(1).add_bigoh(T)
    for n in range(1, T):
        exp = 14 * n
        if exp < T:
            jac0_14_series = (jac0_14_series * (1 - q_var**exp)).add_bigoh(T)
        else:
            break
    jac0_14 = QSeries(jac0_14_series, T=T)
    # Ratio and sqrt
    ratio_series = (jac7_14.series / jac0_14.series).add_bigoh(T)
    sqrt_series = ratio_series.nth_root(2)
    s = QSeries(sqrt_series.add_bigoh(T), T=T)
    result = jacprodmake(s, q, T)
    assert isinstance(result, JacProduct)
    assert any(a == 7 and b == 14 and QQ(e) == QQ('1/2')
               for a, b, e in result.factors), \
        f"Expected factor (7, 14, 1/2), got factors: {result.factors}"


# ---------------------------------------------------------------------------
# CONV-08: jac2prod (Plan 04-02)
# ---------------------------------------------------------------------------

def test_jac2prod_basic():
    """CONV-08: jac2prod(JAC(1,5,inf)) -> PochProduct with 3 factors {(1,5,1),(4,5,1),(5,5,1)}.

    Oracle: Garvan jac2prod doc page.
    """
    j = JacProduct(factors=[(1, 5, 1)])
    result = jac2prod(j)
    assert isinstance(result, PochProduct)
    assert len(result.factors) == 3
    assert set(result.factors) == {(1, 5, 1), (4, 5, 1), (5, 5, 1)}


def test_jac2prod_zero():
    """CONV-08: jac2prod(JAC(0,10,inf)) -> PochProduct with 1 factor (10,10,1).

    Oracle: Garvan jac2prod doc page (a=0 special case).
    """
    j = JacProduct(factors=[(0, 10, 1)])
    result = jac2prod(j)
    assert isinstance(result, PochProduct)
    assert len(result.factors) == 1
    assert result.factors[0] == (10, 10, 1)


# ---------------------------------------------------------------------------
# CONV-09: jac2series (Plan 04-02)
# ---------------------------------------------------------------------------

def test_jac2series_oracle():
    """CONV-09: jac2series(JAC(-4,5,inf), 20) matches the Pochhammer expansion.

    Cross-check: jac2series should match jac2prod().to_series() when both are
    expressed as full Laurent series (accounting for the r-shift in jac2series).

    The full Laurent expansion of JAC(-4,5,inf) starts at q^{-4}:
      -q^{-4} + q^{-3} + 1 - q^3 - q^9 + q^{14} + O(...)
    """
    from sage.all import QQ, LaurentSeriesRing
    j = JacProduct(factors=[(-4, 5, 1)])
    result = jac2series(j, 20)
    assert isinstance(result, QSeries)

    # Build the full Laurent representation of result:
    # result.series is the integer-indexed polynomial (at shift r),
    # multiply by q^r to get the actual Laurent series for comparison.
    R = LaurentSeriesRing(QQ, 'q')
    q = R.gen()
    r = QQ(result.r)
    assert r.denominator() == 1, f"Expected integer r, got {r}"
    # The actual Laurent series = result.series * q^r
    actual_laurent = (result.series * q**int(r)).add_bigoh(15)

    # Build expected from Pochhammer expansion of JAC(-4,5):
    # (q^{-4};q^5) * (q^9;q^5) * (q^5;q^5)
    def poch_product(start, step, T):
        s = R(1).add_bigoh(T)
        for k in range(50):
            exp = start + k * step
            if exp >= T:
                break
            s = (s * (1 - q**exp)).add_bigoh(T)
        return s

    expected_laurent = (
        poch_product(-4, 5, 15) *
        poch_product(9, 5, 15) *
        poch_product(5, 5, 15)
    ).add_bigoh(15)

    assert actual_laurent == expected_laurent, \
        f"jac2series mismatch:\n  got: {actual_laurent}\n  exp: {expected_laurent}"


# ---------------------------------------------------------------------------
# CONV-05: mprodmake (Plan 04-03)
# ---------------------------------------------------------------------------

def test_mprodmake():
    """CONV-05: mprodmake(etaq(q,2,T)^2/etaq(q,4,T)/etaq(q,1,T), q, 17)
    -> MProduct([1,3,5,7,9,11,13,15,17])

    Oracle: Garvan mprodmake doc page.
    """
    R, q = _make_ring()
    T = 18
    EP = etaq(q, 2, T) ** 2 * (etaq(q, 4, T) ** (-1)) * (etaq(q, 1, T) ** (-1))
    result = mprodmake(EP, q, 17)
    assert isinstance(result, MProduct)
    assert sorted(result.exponents) == [1, 3, 5, 7, 9, 11, 13, 15, 17]


# ---------------------------------------------------------------------------
# CONV-06: qfactor (Plan 04-03)
# ---------------------------------------------------------------------------

def test_qfactor_t8():
    """CONV-06: qfactor of t8 rational back-computation.

    t8 = q^6*(1-q^9)*(1-q^10)*(1-q^11)*(1-q^16) / ((1-q)*(1-q^2)*(1-q^3)*(1-q^4))
    -> QFactorResult(numerator={9,10,11,16}, denominator={1,2,3,4}, r=6)

    Oracle: Garvan qfactor doc page / D-06/D-07.
    """
    from sage.all import PolynomialRing
    Rq = PolynomialRing(QQ, 'q')
    q_poly = Rq.gen()
    # Pass as (numerator, denominator) tuple to avoid Sage fraction field auto-simplification
    num_poly = q_poly**6 * (1 - q_poly**9) * (1 - q_poly**10) * (1 - q_poly**11) * (1 - q_poly**16)
    den_poly = (1 - q_poly) * (1 - q_poly**2) * (1 - q_poly**3) * (1 - q_poly**4)
    result = qfactor((num_poly, den_poly), 20)
    assert isinstance(result, QFactorResult)
    assert QQ(result.r) == 6
    assert set(result.numerator.exponents.keys()) == {9, 10, 11, 16}
    assert set(result.denominator.exponents.keys()) == {1, 2, 3, 4}
    assert all(e == 1 for e in result.numerator.exponents.values())
    assert all(e == 1 for e in result.denominator.exponents.values())


# ---------------------------------------------------------------------------
# CONV-07: zqfactor (Plan 04-03)
# ---------------------------------------------------------------------------

def test_zqfactor():
    """CONV-07: zqfactor is a documented best-effort stub for v1.0.
    Returns None and emits UserWarning; does not raise.
    Full bivariate factorization deferred to Phase 5.
    """
    import warnings
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = zqfactor(None, None, None, 10)
    assert result is None
    assert any(issubclass(w.category, UserWarning) for w in caught), \
        "zqfactor must emit a UserWarning"


# ---------------------------------------------------------------------------
# CONV-10: qs2jaccombo (Plan 04-03)
# ---------------------------------------------------------------------------

def test_qs2jaccombo():
    """CONV-10: qs2jaccombo([theta3, theta4], q, T) -> list of 2 JacProducts.

    Oracle: qs2jaccombo on 2-term list returns list of 2 JacProduct objects.
    """
    R, q = _make_ring()
    T = 30
    term1 = theta3(q, T)
    term2 = theta4(q, T)
    result = qs2jaccombo([term1, term2], q, T)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(j, JacProduct) for j in result)


# ---------------------------------------------------------------------------
# CONV-11: findprod (Plan 04-03)
# ---------------------------------------------------------------------------

def test_findprod_trivial():
    """CONV-11: findprod([etaq(q,1,T)], 1, 3, 20) -> at least one entry.

    Oracle: trivial case — etaq itself with coefficient 1 is a nice product.
    """
    R, q = _make_ring()
    T = 25
    FL = [etaq(q, 1, T)]
    result = findprod(FL, 1, 3, 20)
    assert isinstance(result, list)
    assert len(result) >= 1
