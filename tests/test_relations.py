"""
tests/test_relations.py
Tests for qseries._relations — the 8 exact relation-finding functions (Phase 5).
Oracles from Garvan's tutorial "A q-product tutorial for a q-series MAPLE package"
(qseriesdoc.pdf / arXiv math/9812092) §4.1–4.5, and the findcong oracle in 05-CONTEXT D-07.
Expected values never come from this package's own output.
"""
import pytest
from sage.all import QQ, LaurentSeriesRing, PolynomialRing, kronecker, var

from qseries._series import QSeries
from qseries._building_blocks import etaq, theta2, theta3, theta4
from qseries._relations import (
    findhom, findhomcombo, findnonhom, findnonhomcombo,
    findlincombo, findmaxind, findpoly, findcong,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_q(T=100):
    """Return (R, q) for a LaurentSeriesRing over QQ with precision T."""
    R = LaurentSeriesRing(QQ, 'q', default_prec=T + 10)
    return R, R.gen()


def _proportional(p, target):
    """True if polynomial p is a non-zero scalar multiple of target (same ring)."""
    if p == 0:
        return False
    return p * target.lc() == target * p.lc()


def _span_contains(result, target):
    return any(_proportional(p, target) for p in result)


def _eval_poly(poly, basis, T):
    """P(basis[0].series, basis[1].series, ...) truncated to O(q^T) (all basis r == 0)."""
    parent = basis[0].series.parent()
    val = poly(*[s.series for s in basis])
    return parent(val).add_bigoh(T)


def UE(q, k, p, trunk):
    """
    Tutorial §4.2 Eisenstein series U_{p,k}(q) = sum_{m,n>=1} (m/p) n^(k-1) q^(mn),
    through q^trunk.  Built independently of B1, B2 and the target polynomial.
    """
    x = 0
    for m in range(1, trunk + 1):
        for n in range(1, trunk // m + 1):
            x += kronecker(m, p) * n**(k - 1) * q**(m * n)
    R = q.parent()
    return QSeries(R(x).add_bigoh(trunk + 1), T=trunk + 1)


def theta2_q3(q, T):
    """
    theta2(q^3) with the correct q^(3/4) shift.  theta2(q**3, T) in _building_blocks keeps
    r = 1/4 regardless of its argument (Phase 2 issue, see 05-03-SUMMARY), so fix r here.
    """
    t = theta2(q**3, T)
    return QSeries(t.series, T=t.T, r=QQ('3/4'))


# ---------------------------------------------------------------------------
# REL-01: findhom
# ---------------------------------------------------------------------------

def _theta_family(q, T=100):
    return [theta3(q, T), theta4(q, T), theta3(q**2, T), theta4(q**2, T)]


def test_findhom_linear_empty(capsys):
    """No linear relations among theta3(q), theta4(q), theta3(q^2), theta4(q^2) (tutorial §4.1)."""
    R, q = make_q(100)
    result = findhom(_theta_family(q), q, 1, 0)
    assert result == set(), f"Expected no linear relations, got {result}"
    assert "# of terms , 25" in capsys.readouterr().out


def test_findhom_quadratic_two_relations(capsys):
    """
    Exactly two quadratic relations (tutorial §4.1, '# of terms , 31'):
    theta3(q)^2 + theta4(q)^2 = 2 theta3(q^2)^2 and theta3(q) theta4(q) = theta4(q^2)^2.
    """
    R, q = make_q(100)
    result = findhom(_theta_family(q), q, 2, 0)
    assert len(result) == 2, f"Expected 2 quadratic relations, got {len(result)}: {result}"
    assert "# of terms , 31" in capsys.readouterr().out
    PR = PolynomialRing(QQ, ['X1', 'X2', 'X3', 'X4'])
    X1, X2, X3, X4 = PR.gens()
    # Span check: both known relations lie in the span of the returned basis.
    from sage.all import matrix
    monos = sorted({m for p in result for m in p.monomials()} |
                   set((X1**2 + X2**2 - 2 * X3**2).monomials()) |
                   set((X1 * X2 - X4**2).monomials()))
    basis = matrix(QQ, [[p.monomial_coefficient(m) for m in monos] for p in result])
    for target in (X1**2 + X2**2 - 2 * X3**2, X1 * X2 - X4**2):
        row = [target.monomial_coefficient(m) for m in monos]
        assert basis.stack(matrix(QQ, [row])).rank() == basis.rank(), f"{target} not in span"


def test_findhom_shortfall_raises():
    """A series with fewer than N terms raises ValueError naming the shortfall (D-04)."""
    R, q = make_q(30)
    L = [etaq(q, 1, 20), etaq(q, 2, 20)]  # degree 2 -> 3 rows -> N = 24 > 20
    with pytest.raises(ValueError, match="precision.*required"):
        findhom(L, q, 2, 0)


# ---------------------------------------------------------------------------
# REL-02: findhomcombo
# ---------------------------------------------------------------------------

def test_findhomcombo_ue_example(capsys):
    """
    findhomcombo(UE(q,6,5,50), [B1, B2], q, 3, 0, yes) = X1^2*X2 + 40*X1*X2^2 + 335*X2^3
    (tutorial §4.2, '# of terms , 25').
    """
    T = 50
    R, q = make_q(T)
    f = UE(q, 6, 5, T)
    B1 = etaq(q, 1, T)**5 / etaq(q, 5, T)
    B2 = QSeries(q * etaq(q, 5, T).series**5 / etaq(q, 1, T).series, T)
    result = findhomcombo(f, [B1, B2], q, 3, 0, 'yes')
    out = capsys.readouterr().out
    assert "# of terms , 25" in out
    PR = PolynomialRing(QQ, ['X1', 'X2'])
    X1, X2 = PR.gens()
    assert result == {X1**2 * X2 + 40 * X1 * X2**2 + 335 * X2**3}, result


# ---------------------------------------------------------------------------
# REL-05: findnonhom
# ---------------------------------------------------------------------------

def test_findnonhom_relations_vanish():
    """
    findnonhom finds relations of degree <= 3 among theta3(q), theta4(q), theta3(q^4),
    theta4(q^4) (e.g. theta3(q) + theta4(q) = 2 theta3(q^4)); every returned relation
    vanishes to O(q^100) when the series are substituted.
    """
    T = 100
    R, q = make_q(T)
    L = [theta3(q, T), theta4(q, T), theta3(q**4, T), theta4(q**4, T)]
    result = findnonhom(L, q, 3, 0)
    assert len(result) > 0, "findnonhom returned no relations"
    PR = PolynomialRing(QQ, ['X1', 'X2', 'X3', 'X4'])
    X1, X2, X3, X4 = PR.gens()
    assert _span_contains(result, X1 + X2 - 2 * X3) or len(result) > 1
    for poly in result:
        assert _eval_poly(poly, L, T) == 0, f"{poly} does not vanish"


def test_findnonhom_topshift_terms(capsys):
    """3 series, degree <= 3 (20 monomials), topshift 20 prints '# of terms , 61' (tutorial §4.3)."""
    T = 100
    R, q = make_q(T)
    L = [theta3(q, T), theta4(q, T), theta3(q**4, T)]
    findnonhom(L, q, 3, 20)
    assert "# of terms , 61" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# REL-06: findnonhomcombo
# ---------------------------------------------------------------------------

def test_findnonhomcombo_watson(capsys):
    """
    Tutorial §4.4 (Watson's modular equation for 7):
    findnonhomcombo(T^2, [T, xi], q, 7, -15) prints '# of terms , 42' and
    'matrix is , 37, x, 42', and gives
    T^2 = (35 xi^2 + 49 xi^3 + 7 xi) T + 343 xi^7 + 343 xi^6 + 147 xi^5 + 49 xi^4
          + 21 xi^3 + 7 xi^2 + xi,
    where xi = eta(49 tau)/eta(tau) and T = (eta(7 tau)/eta(tau))^4.
    """
    N = 100
    R, q = make_q(N)
    E1 = etaq(q, 1, N).series
    xi = QSeries(q**2 * etaq(q, 49, N).series / E1, N)
    Tq = QSeries(q * etaq(q, 7, N).series**4 / E1**4, N)
    result = findnonhomcombo(Tq**2, [Tq, xi], q, 7, -15)
    out = capsys.readouterr().out
    assert "# of terms , 42" in out
    assert "matrix is , 37, x, 42" in out
    PR = PolynomialRing(QQ, ['X1', 'X2'])
    X1, X2 = PR.gens()
    expected = ((35 * X2**2 + 49 * X2**3 + 7 * X2) * X1
                + 343 * X2**7 + 343 * X2**6 + 147 * X2**5 + 49 * X2**4
                + 21 * X2**3 + 7 * X2**2 + X2)
    # T^2 is itself one of the 36 monomials (X1^2), so the monomials are dependent and the
    # trivial combination X1^2 is also returned; the doc page notes that more than one
    # combination may come back in that case.  Watson's relation must be among them.
    assert expected in result, result
    assert result <= {expected, X1**2}, result


def test_findnonhomcombo_reproduces_f():
    """Each returned P satisfies P(L) = f to O(q^T) when f is a known combination of L."""
    T = 100
    R, q = make_q(T)
    L = [theta3(q, T), theta4(q, T), theta3(q**4, T)]
    f = QSeries(theta3(q, T).series + theta4(q, T).series, T)
    result = findnonhomcombo(f, L, q, 2, 0)
    assert len(result) > 0, "findnonhomcombo returned no combination"
    for poly in result:
        assert _eval_poly(poly, L, T) == f.series.add_bigoh(T), f"{poly} does not reproduce f"


# ---------------------------------------------------------------------------
# REL-07: findlincombo
# ---------------------------------------------------------------------------

def test_findlincombo_known_combo():
    """findlincombo(12*f1 + 13*f2, [f1, f2], [F1, F2], q, 0) gives 12*X1 + 13*X2."""
    T = 50
    R, q = make_q(T)
    f1 = etaq(q, 1, T)
    f2 = etaq(q, 2, T)
    f = QSeries(12 * f1.series + 13 * f2.series, T)
    result = findlincombo(f, [f1, f2], [var('F1'), var('F2')], q, 0)
    PR = PolynomialRing(QQ, ['X1', 'X2'])
    X1, X2 = PR.gens()
    assert result == {12 * X1 + 13 * X2}, result


def test_findlincombo_not_a_combo(capsys):
    """A series outside the span returns an empty set and prints %NOT A LINEAR COMBO.%."""
    T = 50
    R, q = make_q(T)
    f1 = etaq(q, 1, T)
    f2 = etaq(q, 2, T)
    f = etaq(q, 3, T)
    result = findlincombo(f, [f1, f2], [var('F1'), var('F2')], q, 0)
    assert result == set()
    assert "%NOT A LINEAR COMBO.%" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# REL-09: findmaxind
# ---------------------------------------------------------------------------

def test_findmaxind_returns_pair():
    """findmaxind([f1, f2, f1+f2], 0) == [[f1, f2], [1, 2]] (f1+f2 is dependent)."""
    T = 60
    R, q = make_q(T)
    f1 = theta3(q, T)
    f2 = theta4(q, T)
    f3 = QSeries(f1.series + f2.series, T)
    P, NXFL = findmaxind([f1, f2, f3], 0)
    assert NXFL == [1, 2]
    assert P[0] is f1 and P[1] is f2


def test_findmaxind_skips_middle_dependent():
    """A dependent element in the middle is skipped and later independent ones kept."""
    T = 60
    R, q = make_q(T)
    f1, f2 = etaq(q, 1, T), etaq(q, 2, T)
    dep = QSeries(2 * f1.series - f2.series, T)
    f4 = etaq(q, 3, T)
    P, NXFL = findmaxind([f1, f2, dep, f4], 0)
    assert NXFL == [1, 2, 4]


# ---------------------------------------------------------------------------
# REL-10: findpoly
# ---------------------------------------------------------------------------

def test_findpoly_tutorial_example(capsys):
    """
    Tutorial §4.5 (Borwein cubic theta functions):
      x = theta2(q)^2/theta2(q^3)^2 + theta3(q)^2/theta3(q^3)^2
      a = theta3(q) theta3(q^3) + theta2(q) theta2(q^3)
      c = 3 q^(1/3) eta(3 tau)^3 / eta(tau),  y = c^3/a^3
    findpoly(x, y, q, 3, 1, 60) gives (X+6)^3*Y - 27*(X+2)^2 (up to a scalar).
    """
    T = 100
    R, q = make_q(T)
    t2q3 = theta2_q3(q, 40)
    x = theta2(q, T)**2 / t2q3**2 + theta3(q, T)**2 / theta3(q**3, 40)**2
    a = theta3(q, T) * theta3(q**3, 40) + theta2(q, T) * t2q3
    c = QSeries(3 * etaq(q, 3, T).series**3 / etaq(q, 1, T).series, T, r=QQ('1/3'))
    y = c**3 / a**3
    result = findpoly(x, y, q, 3, 1, 60)
    assert "verified to O(q^60)" in capsys.readouterr().out
    PR = PolynomialRing(QQ, ['X', 'Y'])
    X, Y = PR.gens()
    target = (X + 6)**3 * Y - 27 * (X + 2)**2
    assert len(result) == 1 and _span_contains(result, target), result


# ---------------------------------------------------------------------------
# REL-11: findcong
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def partitions_1001():
    """1/etaq(q,1,1001), built once: etaq at T=1001 is slow (untruncated products)."""
    R, q = make_q(1001)
    return QSeries(etaq(q, 1, 1001).series.__invert__(), 1001)


def test_findcong_partition_congruences(partitions_1001):
    """findcong(1/etaq(q,1,1001), 1000) == {(4,5,5),(5,7,7),(6,11,11),(24,25,25)} (D-07)."""
    result = findcong(partitions_1001, 1000)
    assert result == {(4, 5, 5), (5, 7, 7), (6, 11, 11), (24, 25, 25)}, result


def test_findcong_xset_excludes(partitions_1001):
    """XSET={5} drops the modulus-5 congruence and keeps the rest."""
    result = findcong(partitions_1001, 1000, 31, {5})
    assert (4, 5, 5) not in result
    assert {(5, 7, 7), (6, 11, 11), (24, 25, 25)} <= result
