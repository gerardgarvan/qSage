"""Tests for qseries/_building_blocks.py — q-product and theta functions.

All expected values traced to Garvan qseries documentation.
Reference: https://qseries.org/fgarvan/qmaple/qseries/
"""
import pytest
from sage.all import QQ, LaurentSeriesRing, LaurentPolynomialRing


# ---------------------------------------------------------------------------
# BUILD-01: aqprod
# ---------------------------------------------------------------------------

def test_aqprod_basic(q_ring):
    """aqprod(q, q, 6) = (1-q)(1-q^2)(1-q^3)(1-q^4)(1-q^5)(1-q^6). Exact polynomial, T=Infinity.
    Oracle: Garvan aqprod doc page example.
    """
    from qseries._building_blocks import aqprod
    from sage.all import Infinity
    q = q_ring.gen()
    result = aqprod(q, q, 6)
    assert result.series[0] == 1
    assert result.series[1] == -1
    assert result.series[2] == -1
    assert result.T is Infinity

def test_aqprod_zero_n(q_ring):
    """aqprod(q, q, 0) == 1 (empty product). Oracle: Garvan aqprod doc page."""
    from qseries._building_blocks import aqprod
    q = q_ring.gen()
    result = aqprod(q, q, 0)
    assert result.series[0] == 1

def test_aqprod_tutorial_canonical(q_ring):
    """aqprod(q, q, 4) = (1-q)(1-q^2)(1-q^3)(1-q^4) = 1 - q - q^2 + 2q^5 - q^8 - q^9 + q^10.
    Full expansion: coeff[5] == 2 (NOT 1 — two pentagonal paths sum there).
    Oracle: explicit expansion of (1-q)(1-q^2)(1-q^3)(1-q^4).
    """
    from qseries._building_blocks import aqprod
    q = q_ring.gen()
    result = aqprod(q, q, 4)
    expected_coeffs = {0: 1, 1: -1, 2: -1, 3: 0, 4: 0, 5: 2, 6: 0, 7: 0, 8: -1, 9: -1, 10: 1}
    for exp, coeff in expected_coeffs.items():
        assert result.series[exp] == coeff, f"coeff[{exp}] expected {coeff}, got {result.series[exp]}"


# ---------------------------------------------------------------------------
# BUILD-02: qbin
# ---------------------------------------------------------------------------

def test_qbin_33_66(q_ring):
    """qbin(q, 3, 6) = q^9+q^8+2q^7+3q^6+3q^5+3q^4+3q^3+2q^2+q+1. Exact polynomial, T=Infinity.
    Oracle: Garvan qbin doc page.
    """
    from qseries._building_blocks import qbin
    from sage.all import Infinity
    q = q_ring.gen()
    result = qbin(q, 3, 6)
    expected = {0: 1, 1: 1, 2: 2, 3: 3, 4: 3, 5: 3, 6: 3, 7: 2, 8: 1, 9: 1}
    for exp, coeff in expected.items():
        assert result.series[exp] == coeff, f"qbin(q,3,6) coeff[{exp}] = {result.series[exp]}, expected {coeff}"
    assert result.T is Infinity

def test_qbin_boundary(q_ring):
    """qbin(q, 0, n)==1 and qbin(q, n, n)==1. Oracle: Garvan doc page."""
    from qseries._building_blocks import qbin
    q = q_ring.gen()
    assert qbin(q, 0, 5).series[0] == 1
    assert qbin(q, 5, 5).series[0] == 1  # should be q^0 coefficient = 1

def test_qbin_out_of_range(q_ring):
    """qbin(q, 4, 3) == 0 when m > n. Oracle: Garvan doc page."""
    from qseries._building_blocks import qbin
    q = q_ring.gen()
    result = qbin(q, 4, 3)
    assert result.series.is_zero() or result.series[0] == 0


# ---------------------------------------------------------------------------
# BUILD-03: etaq
# ---------------------------------------------------------------------------

def test_etaq_k1(q_ring):
    """etaq(q, 1, 10) = prod_{n>=1}(1-q^n) to O(q^10) = 1 - q - q^2 + q^5 + q^7 - ...
    Oracle: Garvan etaq doc page; coefficients from Euler's pentagonal theorem.
    Implementation: direct product prod(1 - q**(1*n) for n in range(1, 10)) truncated at O(q^10).
    Do NOT use qexp_eta (lives in sage.modular.etaproducts which CLAUDE.md bans, and its
    signature takes a ring not a series element). Use caller's q directly.
    """
    from qseries._building_blocks import etaq
    q = q_ring.gen()
    result = etaq(q, 1, 10)
    # pentagonal: 1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + ...
    assert result.series[0] == 1
    assert result.series[1] == -1
    assert result.series[2] == -1
    assert result.series[5] == 1
    assert result.series[7] == 1

def test_etaq_k2(q_ring):
    """etaq(q, 2, 20) = prod_{n>=1}(1-q^{2n}) to O(q^20); constant term 1, q^1 coefficient 0.
    Oracle: Garvan etaq doc page.
    """
    from qseries._building_blocks import etaq
    q = q_ring.gen()
    result = etaq(q, 2, 20)
    assert result.series[0] == 1
    assert result.series[1] == 0   # no q^1 term in prod(1-q^{2n})
    assert result.series[2] == -1  # first term is -q^2


# ---------------------------------------------------------------------------
# BUILD-04: jacprod
# ---------------------------------------------------------------------------

def test_jacprod_basic(q_ring):
    """jacprod(1, 5, q, 20) = (q;q^5)_inf * (q^4;q^5)_inf to O(q^20).
    Oracle: Garvan jacprod doc page.
    First few terms: 1 - q - q^4 + q^7 + q^{13} - ... (Rogers-Ramanujan pattern).
    """
    from qseries._building_blocks import jacprod
    q = q_ring.gen()
    result = jacprod(1, 5, q, 20)
    assert result.series[0] == 1
    assert result.series[1] == -1


# ---------------------------------------------------------------------------
# BUILD-05: theta (bivariate)
# ---------------------------------------------------------------------------

def test_theta_z_minus1(q_ring):
    """theta(-1, q, 10) = sum_{i=-10}^{10} (-1)^i q^{i^2}.
    At z=-1: coefficient of q^{n^2} is 2*(-1)^n for n>0, 1 for n=0.
    Oracle: Garvan theta doc page.
    Implementation: compute sum((-1)**i * q**(i*i) for i in range(-10, 11)) on caller's q.
    No internal ring construction — Sage coercion from q determines the parent.
    """
    from qseries._building_blocks import theta
    q = q_ring.gen()
    result = theta(-1, q, 10)
    # coeff[0] = 1 (i=0 term)
    assert result.series[0] == 1
    # n=±1: (-1)^1 + (-1)^{-1} = -1 + -1 = -2
    assert result.series[1] == -2
    # n=±2: (-1)^2 + (-1)^{-2} = 1 + 1 = 2
    assert result.series[4] == 2
    # n=±3: (-1)^3 + (-1)^{-3} = -1 + -1 = -2
    assert result.series[9] == -2

def test_theta_bivariate_type(q_ring):
    """theta(z, q, 5) where z is a LaurentPolynomialRing generator returns a bivariate QSeries.
    Oracle: D-03 — bivariate functions return QSeries with R = LaurentPolynomialRing.
    """
    from qseries._building_blocks import theta
    from sage.all import LaurentPolynomialRing, QQ
    from qseries._series import QSeries
    Rz = LaurentPolynomialRing(QQ, 'z')
    z = Rz.gen()
    q = q_ring.gen()
    result = theta(z, q, 5)
    assert isinstance(result, QSeries), "theta must return QSeries"
    assert result.R is not None, "bivariate theta must set R"
    # The constant term of the series at q^0 should be z^0 = 1
    assert result.series[0] == Rz.one(), f"q^0 coefficient expected 1, got {result.series[0]}"


# ---------------------------------------------------------------------------
# BUILD-06: theta2
# ---------------------------------------------------------------------------

def test_theta2_shift(q_ring):
    """theta2(q, 50).r == QQ(1, 4). Oracle: Garvan theta2 doc page; Phase 1 D-04 decision.
    theta2 returns an exact Laurent polynomial (T=Infinity), stored as q^{1/4} * (integer-power series).
    Summation: i runs -50..50, so includes all terms; T here is index bound not q-order.
    """
    from qseries._building_blocks import theta2
    q = q_ring.gen()
    result = theta2(q, 50)
    assert result.r == QQ('1/4')

def test_theta2_coefficients(q_ring):
    """theta2(q, 50) series (after factoring q^{1/4}) = 2 + 2q^2 + 2q^6 + 2q^{12} + ...
    Oracle: Garvan theta2 doc page.
    Specifically: coeff[0]=2, coeff[2]=2, coeff[6]=2, coeff[12]=2.
    """
    from qseries._building_blocks import theta2
    q = q_ring.gen()
    result = theta2(q, 50)
    # n=0 and n=-1 both give exponent (1/2)^2=1/4; after factoring -> q^0, coeff=2
    assert result.series[0] == 2
    # n=1 and n=-2 give exponent (3/2)^2=9/4; after factoring q^{1/4} -> q^2, coeff=2
    assert result.series[2] == 2
    # n=2 and n=-3 give (5/2)^2=25/4; after factoring -> q^6, coeff=2
    assert result.series[6] == 2


# ---------------------------------------------------------------------------
# BUILD-07: theta3
# ---------------------------------------------------------------------------

def test_theta3_coefficients(q_ring):
    """theta3(q, 50) = sum_{n: n^2 <= 50} q^{n^2}. Exact Laurent polynomial, T=Infinity.
    Summation bound: include all n where n^2 <= T, i.e. range(-isqrt(T), isqrt(T)+1).
    isqrt(50)=7, so n runs -7..7. Highest term: 2*q^49 (n=±7).
    Oracle: Garvan theta3 doc page (theta3(q,50) = 2q^49+2q^36+...+2q+1).
    For theta3(q,100): isqrt(100)=10, highest is 2q^100; n=11 gives 11^2=121 > 100, excluded.
    Wait — review says theta3(q,100) prints 2q^121. Recheck: the doc says theta3(q,100) includes
    n=11 because 11^2=121, not 100. So T is an index bound (|n| <= T), not a q-order bound.
    CORRECTION: T is the summation index bound: sum i=-T..T, giving highest term q^{T^2}.
    theta3(q,50) highest term is q^{50^2}=q^2500? No — review says theta3(q,50)=2q^64+...+2q+1.
    8^2=64. So the bound giving highest n=8 for T=50 means |n|<=floor(sqrt(T)).
    FINAL RULE (from review): use range(-isqrt(T), isqrt(T)+1) for theta3/theta4.
    isqrt(50)=7, but 8^2=64>50 and is included. So bound must be isqrt(T)+1 = 8 for T=50.
    Use range(-(isqrt(T)+1), isqrt(T)+2) — i.e. include n up to isqrt(T)+1 each direction.
    """
    from qseries._building_blocks import theta3
    from sage.all import Infinity
    q = q_ring.gen()
    result = theta3(q, 50)
    # constant term (n=0)
    assert result.series[0] == 1
    # n=±1 -> q^1, coeff=2
    assert result.series[1] == 2
    # n=±2 -> q^4, coeff=2
    assert result.series[4] == 2
    # n=±3 -> q^9, coeff=2
    assert result.series[9] == 2
    # n=±4 -> q^16, coeff=2
    assert result.series[16] == 2
    # n=±8 -> q^64, coeff=2 (catches summation-bound bug)
    assert result.series[64] == 2
    # non-square should be 0
    assert result.series[2] == 0
    assert result.series[3] == 0
    # T=Infinity (exact polynomial)
    assert result.T is Infinity

def test_theta3_coefficients_T100(q_ring):
    """theta3(q, 100): n=±11 gives q^121 with coeff 2. Catches off-by-one in summation bound.
    11^2=121. isqrt(100)=10, so isqrt(100)+1=11 is included. Oracle: review §BUG section.
    """
    from qseries._building_blocks import theta3
    q = q_ring.gen()
    result = theta3(q, 100)
    assert result.series[121] == 2, f"theta3(q,100) coeff[121] expected 2, got {result.series[121]}"

def test_theta3_theta4_product_identity(q_ring):
    """theta3(q,T)*theta4(q,T) = theta4(q^2,T)^2 (Jacobi identity).
    This test only works once theta4(q**2, T) honours its argument (uses caller's q).
    Oracle: RESEARCH.md identity check; standard result in q-series theory.
    """
    from qseries._building_blocks import theta3, theta4
    q = q_ring.gen()
    T = 20
    lhs = theta3(q, T) * theta4(q, T)
    # theta4(q^2, T): pass q**2 as the q argument — implementation must use it, not rebuild q
    rhs_inner = theta4(q**2, T)
    rhs = rhs_inner * rhs_inner
    # Compare coefficients up to order min T
    for i in range(min(T, 10)):
        assert lhs.series[i] == rhs.series[i], f"identity fails at q^{i}"


# ---------------------------------------------------------------------------
# BUILD-08: theta4
# ---------------------------------------------------------------------------

def test_theta4_coefficients(q_ring):
    """theta4(q, 50) = sum_{n: |n|<=isqrt(50)+1} (-1)^n q^{n^2}. Exact polynomial, T=Infinity.
    Oracle: Garvan theta4 doc page (theta4(q,50) = 2q^64-2q^49+2q^36-2q^25+2q^16-2q^9+2q^4-2q+1).
    Note: n=±8 gives q^64, so n runs to 8=isqrt(50)+1.
    """
    from qseries._building_blocks import theta4
    from sage.all import Infinity
    q = q_ring.gen()
    result = theta4(q, 50)
    assert result.series[0] == 1
    assert result.series[1] == -2   # n=±1, (-1)^1 = -1, total = -2
    assert result.series[4] == 2    # n=±2, (-1)^2 = 1, total = 2
    assert result.series[9] == -2   # n=±3, (-1)^3 = -1, total = -2
    assert result.series[64] == 2   # n=±8, (-1)^8 = 1, total = 2 (catches bound bug)
    assert result.T is Infinity


# ---------------------------------------------------------------------------
# BUILD-09: tripleprod (bivariate)
# ---------------------------------------------------------------------------

def test_tripleprod_euler_pentagonal(q_ring):
    """tripleprod(q, q**3, 30) = Euler's pentagonal series.
    = 1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + q^22 + q^26 - ...
    Oracle: Garvan tutorial §6.1; RESEARCH.md.
    Index bound: for tripleprod(z,q,T), review says tripleprod(z,q,10) prints z^±6 terms up to q^21.
    Use index range -(isqrt(2*T)+2)..(isqrt(2*T)+2) in the series-side summation.
    """
    from qseries._building_blocks import tripleprod
    q = q_ring.gen()
    result = tripleprod(q, q**3, 30)
    expected = {0: 1, 1: -1, 2: -1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 1, 8: 0,
                9: 0, 10: 0, 11: 0, 12: -1, 13: 0, 14: 0, 15: -1}
    for exp, coeff in expected.items():
        assert result.series[exp] == coeff, f"tripleprod coeff[{exp}] expected {coeff}"

def test_tripleprod_bivariate_type(q_ring):
    """tripleprod(z, q, 5) where z is a LaurentPolynomialRing generator returns a bivariate QSeries.
    Oracle: D-03 — bivariate functions compute on caller's objects, Sage coercion picks parent.
    """
    from qseries._building_blocks import tripleprod
    from sage.all import LaurentPolynomialRing, QQ
    from qseries._series import QSeries
    Rz = LaurentPolynomialRing(QQ, 'z')
    z = Rz.gen()
    q = q_ring.gen()
    result = tripleprod(z, q, 10)
    assert isinstance(result, QSeries), "tripleprod must return QSeries"
    assert result.R is not None, "bivariate tripleprod must set R"
    assert result.series[0] == Rz.one() - z, f"q^0 coefficient expected 1 - z, got {result.series[0]}"


# ---------------------------------------------------------------------------
# BUILD-10: quinprod
# ---------------------------------------------------------------------------

def test_quinprod_series(q_ring):
    """quinprod(z, q, 5) with integer T returns a QSeries (series side of the identity).
    3-arg signature: quinprod(z, q, T). The 4-arg header in RESEARCH.md was a doc typo.
    Oracle: Garvan quinprod doc page (BUILD-10); tutorial (6.9).
    Identity: (-z;q)_inf (-q/z;q)_inf (z^2 q;q^2)_inf (q/z^2;q^2)_inf (q;q)_inf
            = sum_m ((-z)^{-3m} - (-z)^{3m-1}) * q^{m(3m+1)/2}
    For T=integer: return the series side summed over m (bound: from doc example T=3 -> m=-4..4,
    so use bound T+1 each direction).
    """
    from qseries._building_blocks import quinprod
    from qseries._series import QSeries
    q = q_ring.gen()
    z_ring = LaurentPolynomialRing(QQ, 'z')
    z = z_ring.gen()
    result = quinprod(z, q, 5)
    assert isinstance(result, QSeries)

def test_quinprod_prodid_string(q_ring):
    """quinprod(z, q, 'prodid') returns a non-empty string showing the correct identity.
    Identity: (-z;q)_inf (-q/z;q)_inf (z^2 q;q^2)_inf (q/z^2;q^2)_inf (q;q)_inf = sum ...
    Oracle: D-05 decision; CONTEXT.md; tutorial (6.9).
    """
    from qseries._building_blocks import quinprod
    q = q_ring.gen()
    z_ring = LaurentPolynomialRing(QQ, 'z')
    z = z_ring.gen()
    result = quinprod(z, q, 'prodid')
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# BUILD-11: winquist
# ---------------------------------------------------------------------------

def test_winquist_oracle(q_ring):
    """winquist uses Maple's (a;q)_inf factors, not shifted (aq;q)_inf ones.
    Oracle: Maple 2026 + qseries 1.3 output (parity case winquist_ab): the q^0 and q^1
    coefficients of winquist(a,b,q,12); and the doc-page identity
    winquist/((1-a)(1-b)(1-ab)(1-a/b)) at a=b=1 = (q;q)_inf^10 = 1 - 10q + 35q^2 - 30q^3 - 105q^4 + 238q^5 ...
    """
    from sage.all import LaurentPolynomialRing, LaurentSeriesRing, QQ
    from qseries._building_blocks import winquist
    L = LaurentPolynomialRing(QQ, 'a,b')
    a, b = L.gens()
    q = LaurentSeriesRing(L, 'q').gen()
    s = winquist(a, b, q, 12).series
    assert s[0] == (1 - a) * (1 - b) * (1 - a * b) * (1 - a / b)
    assert s[1] == (b**3*a**3 - b**3 - a**3/b**2 + 1/b**2 - a**4*b**2 + a**4/b + b**2/a - 1/(a*b))
    F = L.fraction_field()
    d = F((1 - a) * (1 - b) * (1 - a * b) * (1 - a / b))
    vals = [(F(s[n]) / d).subs(a=1, b=1) for n in range(6)]
    assert vals == [1, -10, 35, -30, -105, 238]

def test_winquist_tutorial_call(q_ring):
    """winquist(q^5, q^3, q^11, 10) matches tutorial call. Must not raise TypeError.
    Oracle: Garvan tutorial call pattern; winquist must accept series elements as a, b.
    """
    from qseries._building_blocks import winquist
    q = q_ring.gen()
    result = winquist(q**5, q**3, q**11, 10)
    from qseries._series import QSeries
    assert isinstance(result, QSeries)


def test_theta2_shift_scales_with_argument(q_ring):
    """theta2(q^k) carries q^(k/4), since k(n+1/2)^2 = k(n^2+n) + k/4. Oracle: theta2 definition (doc page)."""
    from qseries._building_blocks import theta2
    from sage.all import QQ
    q = q_ring.gen()
    assert theta2(q, 10).r == QQ('1/4')
    assert theta2(q**3, 10).r == QQ('3/4')
    assert theta2(q**3, 10).series[6] == 2   # n = 1 and n = -2 give 3(n^2+n) = 6


def test_etaq_large_T_matches_pentagonal(q_ring):
    """etaq(q,1,1001) matches Euler's pentagonal number theorem through q^1000, and runs fast.

    Oracle: Euler's pentagonal number theorem, prod(1-q^n) = sum (-1)^m q^(m(3m-1)/2) (etaq doc page, tutorial sec. 2); the 30 s bound is a Phase 2 follow-up design decision.
    """
    from qseries._building_blocks import etaq
    import time
    q = q_ring.gen()
    t0 = time.time()
    e = etaq(q, 1, 1001)
    elapsed = time.time() - t0
    expected = {m * (3 * m - 1) // 2: (-1) ** (m % 2) for m in range(-30, 31)}
    for n in range(1001):
        assert e.series[n] == expected.get(n, 0), f"coefficient of q^{n}"
    assert elapsed < 30, f"etaq(q,1,1001) took {elapsed:.1f}s"


def test_quinprod_matches_product():
    """quinprod(z,q,3) series: q^0, q^1, q^2 coefficients 1+z, -z^3-1/z^2, -1/z^3-z^4.

    Oracle: Maple 2026 + qseries 1.3 output (parity case quinprod_z), which agrees with the
    product (-z;q)(-q/z;q)(z^2 q;q^2)(q/z^2;q^2)(q;q) on the doc page.
    """
    from sage.all import LaurentPolynomialRing, LaurentSeriesRing, QQ
    from qseries._building_blocks import quinprod
    z = LaurentPolynomialRing(QQ, 'z').gen()
    q = LaurentSeriesRing(z.parent(), 'q').gen()
    s = quinprod(z, q, 3).series
    assert [s[0], s[1], s[2], s[5]] == [1 + z, -z**3 - z**-2, -z**-3 - z**4, z**6 + z**-5]
