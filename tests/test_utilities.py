"""Tests for qseries/_utilities.py — degree functions.

All expected values traced to Garvan qseries documentation examples.
"""
import pytest
from sage.all import QQ
from sage.all import LaurentSeriesRing
from qseries._series import QSeries


@pytest.fixture
def R():
    return LaurentSeriesRing(QQ, 'q')


def make_qs(R, series_expr, T=20, r=0):
    return QSeries(series_expr, T=T, r=QQ(r))


# ---------------------------------------------------------------------------
# qdegree tests
# ---------------------------------------------------------------------------

def test_qdegree_positive_exponents(R):
    """qdegree on 1 - q + q^3 returns 3.

    Oracle: qdegree doc page: highest power of q; 1 - q + q^3 has degree 3 by inspection.
    """
    from qseries._utilities import qdegree
    q = R.gen()
    s = (1 - q + q**3).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    assert qdegree(qs) == 3


def test_qdegree_negative_and_positive(R):
    """qdegree on q^-5 - q^-4 + q^2 - q^10 returns 10 (matching Maple doc example)."""
    from qseries._utilities import qdegree
    q = R.gen()
    s = (q**(-5) - q**(-4) + q**2 - q**10).add_bigoh(17)
    qs = make_qs(R, s, T=17)
    assert qdegree(qs) == 10


def test_qdegree_with_rational_shift(R):
    """qdegree includes rational shift r.

    Oracle: qdegree doc page plus the q^r shift: q^(1/4) * q^2 has degree 9/4.
    """
    from qseries._utilities import qdegree
    q = R.gen()
    # series = q^2 + O(q^5), r = 1/4; highest exponent = 2; total = 2 + 1/4 = 9/4
    s = (q**2).add_bigoh(5)
    qs = make_qs(R, s, T=5, r=QQ(1)/4)
    assert qdegree(qs) == QQ(9)/4


def test_qdegree_zero_raises(R):
    """qdegree on zero QSeries raises ValueError.

    Oracle: Design decision (Phase 1, FOUND-05): the zero series has no degree.
    """
    from qseries._utilities import qdegree
    s = R(0).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    with pytest.raises(ValueError, match="qdegree undefined for zero series"):
        qdegree(qs)


def test_qdegree_type_error():
    """qdegree on non-QSeries raises TypeError.

    Oracle: Design decision (Phase 1, FOUND-05): input must be a QSeries.
    """
    from qseries._utilities import qdegree
    with pytest.raises(TypeError):
        qdegree(42)


# ---------------------------------------------------------------------------
# lqdegree tests
# ---------------------------------------------------------------------------

def test_lqdegree_positive_start(R):
    """lqdegree on 1 - q + q^3 returns 0 (lowest exponent is q^0).

    Oracle: lqdegree doc page: lowest power of q; 1 - q + q^3 has lowest degree 0 by inspection.
    """
    from qseries._utilities import lqdegree
    q = R.gen()
    s = (1 - q + q**3).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    assert lqdegree(qs) == 0


def test_lqdegree_negative_start(R):
    """lqdegree on q^-5 - q^-4 + q^2 returns -5.

    Oracle: lqdegree doc page: lowest power of q; q^-5 - q^-4 + q^2 gives -5 by inspection.
    """
    from qseries._utilities import lqdegree
    q = R.gen()
    s = (q**(-5) - q**(-4) + q**2).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    assert lqdegree(qs) == -5


def test_lqdegree_with_rational_shift(R):
    """lqdegree with r=1/4 and series starting at q^0 returns 1/4.

    Oracle: lqdegree doc page plus the q^r shift: q^(1/4) * (2 + 2q^2) has lowest degree 1/4.
    """
    from qseries._utilities import lqdegree
    q = R.gen()
    s = (2 + 2*q**2).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(1)/4)
    assert lqdegree(qs) == QQ(1)/4


def test_lqdegree_zero_raises(R):
    """lqdegree on zero QSeries raises ValueError.

    Oracle: Design decision (Phase 1, FOUND-05): the zero series has no lowest degree.
    """
    from qseries._utilities import lqdegree
    s = R(0).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    with pytest.raises(ValueError, match="lqdegree undefined for zero series"):
        lqdegree(qs)


def test_lqdegree_type_error():
    """lqdegree on non-QSeries raises TypeError.

    Oracle: Design decision (Phase 1, FOUND-05): input must be a QSeries.
    """
    from qseries._utilities import lqdegree
    with pytest.raises(TypeError):
        lqdegree("not a series")


# ---------------------------------------------------------------------------
# lqdegree0 tests
# ---------------------------------------------------------------------------

def test_lqdegree0_qseries_r_half(R):
    """lqdegree0 on QSeries with r=1/2, series=1+O(q) returns 1/2 (like sqrt(q)*JAC).

    Oracle: lqdegree0 doc page example: lqdegree0(sqrt(q)*JAC(...)) = 1/2.
    """
    from qseries._utilities import lqdegree0
    s = R(1).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(1)/2)
    assert lqdegree0(qs) == QQ(1)/2


def test_lqdegree0_qseries_valuation_one(R):
    """lqdegree0 on QSeries with r=0, series=q+O(q^2) returns 1 (like q*JAC).

    Oracle: lqdegree0 doc page example: lqdegree0(q*JAC(...)) = 1.
    """
    from qseries._utilities import lqdegree0
    q = R.gen()
    s = q.add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(0))
    assert lqdegree0(qs) == 1


def test_lqdegree0_qseries_r_zero_val_zero(R):
    """lqdegree0 on QSeries with r=0, series=1+O(q) returns 0 (like JAC alone).

    Oracle: lqdegree0 doc page example: lqdegree0(JAC(...)) = 0.
    """
    from qseries._utilities import lqdegree0
    s = R(1).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(0))
    assert lqdegree0(qs) == 0


def test_lqdegree0_qseries_r_negative(R):
    """lqdegree0 on QSeries with r=-3, series=1+O(q) returns -3 (like JAC/q^3).

    Oracle: lqdegree0 doc page example: lqdegree0(JAC(...)/q^3) = -3.
    """
    from qseries._utilities import lqdegree0
    s = R(1).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(-3))
    assert lqdegree0(qs) == -3


def test_lqdegree0_etaproduct_r():
    """lqdegree0 on EtaProduct with r=1/4 returns 1/4 (reads .r attribute).

    Oracle: lqdegree0 doc page: the q-degree of a q-monomial is its q^r prefactor (here an eta-product with r = 1/4).
    """
    from qseries._utilities import lqdegree0
    from qseries._symbolic import EtaProduct
    ep = EtaProduct(1, QQ(1)/4, [])
    assert lqdegree0(ep) == QQ(1)/4


def test_lqdegree0_jacproduct_r():
    """lqdegree0 on JacProduct with r=-3 returns -3 (reads .r attribute).

    Oracle: lqdegree0 doc page example: lqdegree0(JAC(...)/q^3) = -3.
    """
    from qseries._utilities import lqdegree0
    from qseries._symbolic import JacProduct
    jp = JacProduct(r=QQ(-3), factors=[(0, 1, 1)])
    assert lqdegree0(jp) == -3


def test_lqdegree0_type_error():
    """lqdegree0 on object without .r and not QSeries raises TypeError.

    Oracle: Design decision (Phase 1, FOUND-05): input must be a QSeries or a symbolic product with .r.
    """
    from qseries._utilities import lqdegree0
    with pytest.raises(TypeError):
        lqdegree0(42)


# ---------------------------------------------------------------------------
# UTIL-01: sift
# ---------------------------------------------------------------------------

def test_sift_e0(q_ring):
    """sift(etaq(q,1,500), q, 5, 0, 499): extract every 5th coefficient starting at 0.
    Expected: E0 = 1 + q - q^3 - q^7 - q^8 - q^14 + q^20 + q^29 + q^31 + q^42 - q^52 - q^66 - q^69 - q^85 + q^99
    (from Garvan tutorial §6.2, not an eta quotient — its product form is
     (q^5;q^5)(q^2;q^5)(q^3;q^5)/((q;q^5)(q^4;q^5))).
    Assert these specific coefficients by position.
    Oracle: Garvan tutorial §6.2, verbatim E0 expansion.
    """
    from qseries._building_blocks import etaq
    from qseries._utilities import sift
    q = q_ring.gen()
    f = etaq(q, 1, 500)
    E0 = sift(f, q, 5, 0, 499)
    # Coefficients from tutorial §6.2 verbatim:
    expected = {
        0: 1, 1: 1, 2: 0, 3: -1, 4: 0, 5: 0, 6: 0, 7: -1, 8: -1, 9: 0,
        10: 0, 11: 0, 12: 0, 13: 0, 14: -1, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0,
        20: 1, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 1,
        30: 0, 31: 1, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0,
        40: 0, 41: 0, 42: 1, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0,
        50: 0, 51: 0, 52: -1, 53: 0, 54: 0, 55: 0, 56: 0, 57: 0, 58: 0, 59: 0,
        60: 0, 61: 0, 62: 0, 63: 0, 64: 0, 65: 0, 66: -1, 67: 0, 68: 0, 69: -1,
        70: 0, 71: 0, 72: 0, 73: 0, 74: 0, 75: 0, 76: 0, 77: 0, 78: 0, 79: 0,
        80: 0, 81: 0, 82: 0, 83: 0, 84: 0, 85: -1, 86: 0, 87: 0, 88: 0, 89: 0,
        90: 0, 91: 0, 92: 0, 93: 0, 94: 0, 95: 0, 96: 0, 97: 0, 98: 0, 99: 1,
    }
    for pos, coeff in expected.items():
        assert E0.series[pos] == coeff, f"E0 coeff[{pos}] expected {coeff}, got {E0.series[pos]}"

def test_sift_basic(q_ring):
    """sift picks residue class n=2, k=0 from 1+q+q^2+q^3+q^4+q^5.
    sift gives 1 + q + q^2 (coefficients at positions 0,2,4 become 0,1,2).
    Oracle: sift doc page definition sift(s,q,n,k,T) = sum a[n*i+k]*q^i.
    Also: sift must use s.series.parent() for output ring, not build a fresh QQ ring,
    so that GF(p) inputs survive.
    """
    from qseries._utilities import sift
    q = q_ring.gen()
    # Build series sum_{i=0}^{5} q^i
    s_raw = sum(q**i for i in range(6)).add_bigoh(10)
    from qseries._series import QSeries
    s = QSeries(s_raw, T=10)
    result = sift(s, q, 2, 0, 9)
    # a[0]=1, a[2]=1, a[4]=1 -> result = 1 + q + q^2
    assert result.series[0] == 1
    assert result.series[1] == 1
    assert result.series[2] == 1


# ---------------------------------------------------------------------------
# UTIL-05: checkmult
# ---------------------------------------------------------------------------

def test_checkmult_tau_function(q_ring):
    """checkmult(etaq(q,1,T)**24, T) returns True — Ramanujan tau is multiplicative.
    Oracle: tau(2)=-24, tau(3)=252, tau(6)=-6048 = tau(2)*tau(3). External oracle, not self-referential.
    This test uses etaq(q,1,T)**24 = sum tau(n)*q^n (up to q-shift) as a real multiplicative example.
    """
    from qseries._building_blocks import etaq
    from qseries._utilities import checkmult
    from qseries._series import QSeries
    q = q_ring.gen()
    T = 30
    # Delta(q) = q * etaq(q,1,T)^24 = sum_{n>=1} tau(n)*q^n
    # etaq(q,1,T)**24 has series[n] = tau(n+1), so multiply by q to shift:
    # (q * etaq(q,1,T)**24).series[n] = tau(n) for n>=1
    # tau(1)=1, tau(2)=-24, tau(3)=252, tau(6)=-6048=tau(2)*tau(3) -- multiplicative
    f_raw = etaq(q, 1, T) ** 24
    # Multiply series by q to get tau(n) at index n
    raw_shifted = (q * f_raw.series).add_bigoh(T)
    f = QSeries(raw_shifted, T=T)
    assert checkmult(f, T) is True

def test_checkmult_non_multiplicative(q_ring):
    """checkmult returns False for a non-multiplicative series.
    Craft: a(1)=1, a(2)=1, a(3)=1, a(6)=5 -> a(6) != a(2)*a(3) -> not multiplicative.
    Oracle: D-07; checkmult doc page.
    """
    from qseries._utilities import checkmult
    q = q_ring.gen()
    from qseries._series import QSeries
    # Craft: a(1)=1, a(2)=1, a(3)=1, a(6)=5 -> a(6)!=a(2)*a(3) -> not multiplicative
    raw = (1 + q + q**2 + q**3 + q**4 + q**5 + 5*q**6).add_bigoh(30)
    f = QSeries(raw, T=30)
    assert checkmult(f, 30) is False


# ---------------------------------------------------------------------------
# UTIL-06: checkprod (stub)
# ---------------------------------------------------------------------------

def test_checkprod_raises():
    """checkprod raises ValueError when passed None (not a QSeries).
    Phase 3 replaced the stub; passing None now fails in prodmake with AttributeError
    or similar — just verify it no longer raises NotImplementedError.
    Oracle: Phase 3 implementation; checkprod doc page.
    """
    from qseries._utilities import checkprod
    # Phase 3 checkprod is implemented; passing None raises AttributeError not NotImplementedError
    with pytest.raises((AttributeError, TypeError, ValueError)):
        checkprod(None, 10, 10)


# ---------------------------------------------------------------------------
# UTIL-07/08: packageversion and changes
# ---------------------------------------------------------------------------

def test_packageversion():
    """packageversion() returns a non-empty string. Oracle: Garvan packageversion doc page."""
    from qseries._utilities import packageversion
    v = packageversion()
    assert isinstance(v, str)
    assert len(v) > 0

def test_changes():
    """changes() returns a non-empty string. Oracle: Garvan changes doc page."""
    from qseries._utilities import changes
    result = changes()
    assert isinstance(result, str)
    assert len(result) > 0
