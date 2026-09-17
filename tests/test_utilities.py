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
    """qdegree on 1 - q + q^3 returns 3."""
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
    """qdegree includes rational shift r."""
    from qseries._utilities import qdegree
    q = R.gen()
    # series = q^2 + O(q^5), r = 1/4; highest exponent = 2; total = 2 + 1/4 = 9/4
    s = (q**2).add_bigoh(5)
    qs = make_qs(R, s, T=5, r=QQ(1)/4)
    assert qdegree(qs) == QQ(9)/4


def test_qdegree_zero_raises(R):
    """qdegree on zero QSeries raises ValueError."""
    from qseries._utilities import qdegree
    s = R(0).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    with pytest.raises(ValueError, match="qdegree undefined for zero series"):
        qdegree(qs)


def test_qdegree_type_error():
    """qdegree on non-QSeries raises TypeError."""
    from qseries._utilities import qdegree
    with pytest.raises(TypeError):
        qdegree(42)


# ---------------------------------------------------------------------------
# lqdegree tests
# ---------------------------------------------------------------------------

def test_lqdegree_positive_start(R):
    """lqdegree on 1 - q + q^3 returns 0 (lowest exponent is q^0)."""
    from qseries._utilities import lqdegree
    q = R.gen()
    s = (1 - q + q**3).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    assert lqdegree(qs) == 0


def test_lqdegree_negative_start(R):
    """lqdegree on q^-5 - q^-4 + q^2 returns -5."""
    from qseries._utilities import lqdegree
    q = R.gen()
    s = (q**(-5) - q**(-4) + q**2).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    assert lqdegree(qs) == -5


def test_lqdegree_with_rational_shift(R):
    """lqdegree with r=1/4 and series starting at q^0 returns 1/4."""
    from qseries._utilities import lqdegree
    q = R.gen()
    s = (2 + 2*q**2).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(1)/4)
    assert lqdegree(qs) == QQ(1)/4


def test_lqdegree_zero_raises(R):
    """lqdegree on zero QSeries raises ValueError."""
    from qseries._utilities import lqdegree
    s = R(0).add_bigoh(10)
    qs = make_qs(R, s, T=10)
    with pytest.raises(ValueError, match="lqdegree undefined for zero series"):
        lqdegree(qs)


def test_lqdegree_type_error():
    """lqdegree on non-QSeries raises TypeError."""
    from qseries._utilities import lqdegree
    with pytest.raises(TypeError):
        lqdegree("not a series")


# ---------------------------------------------------------------------------
# lqdegree0 tests
# ---------------------------------------------------------------------------

def test_lqdegree0_qseries_r_half(R):
    """lqdegree0 on QSeries with r=1/2, series=1+O(q) returns 1/2 (like sqrt(q)*JAC)."""
    from qseries._utilities import lqdegree0
    s = R(1).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(1)/2)
    assert lqdegree0(qs) == QQ(1)/2


def test_lqdegree0_qseries_valuation_one(R):
    """lqdegree0 on QSeries with r=0, series=q+O(q^2) returns 1 (like q*JAC)."""
    from qseries._utilities import lqdegree0
    q = R.gen()
    s = q.add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(0))
    assert lqdegree0(qs) == 1


def test_lqdegree0_qseries_r_zero_val_zero(R):
    """lqdegree0 on QSeries with r=0, series=1+O(q) returns 0 (like JAC alone)."""
    from qseries._utilities import lqdegree0
    s = R(1).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(0))
    assert lqdegree0(qs) == 0


def test_lqdegree0_qseries_r_negative(R):
    """lqdegree0 on QSeries with r=-3, series=1+O(q) returns -3 (like JAC/q^3)."""
    from qseries._utilities import lqdegree0
    s = R(1).add_bigoh(10)
    qs = make_qs(R, s, T=10, r=QQ(-3))
    assert lqdegree0(qs) == -3


def test_lqdegree0_etaproduct_r():
    """lqdegree0 on EtaProduct with r=1/4 returns 1/4 (reads .r attribute)."""
    from qseries._utilities import lqdegree0
    from qseries._symbolic import EtaProduct
    ep = EtaProduct(1, QQ(1)/4, [])
    assert lqdegree0(ep) == QQ(1)/4


def test_lqdegree0_jacproduct_r():
    """lqdegree0 on JacProduct with r=-3 returns -3 (reads .r attribute)."""
    from qseries._utilities import lqdegree0
    from qseries._symbolic import JacProduct
    jp = JacProduct(r=QQ(-3), factors=[(0, 1, 1)])
    assert lqdegree0(jp) == -3


def test_lqdegree0_type_error():
    """lqdegree0 on object without .r and not QSeries raises TypeError."""
    from qseries._utilities import lqdegree0
    with pytest.raises(TypeError):
        lqdegree0(42)
