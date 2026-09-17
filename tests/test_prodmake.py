"""Tests for prodmake and checkprod (Phase 3).

All expected values taken from:
  - Garvan qseries tutorial §3.1 (Rogers-Ramanujan)
  - Garvan prodmake / checkprod doc pages
  - Mathematical identity checks (round-trip via QProduct.to_series)

No expected values computed by running prodmake itself.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sage.all import QQ, LaurentSeriesRing
from qseries._series import QSeries
from qseries._symbolic import QProduct
from qseries._building_blocks import etaq, aqprod
from qseries._prodmake import prodmake


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ring():
    R = LaurentSeriesRing(QQ, 'q')
    return R, R.gen()


# ---------------------------------------------------------------------------
# Test 1: Degenerate — constant 1 series gives empty product
# ---------------------------------------------------------------------------

def test_prodmake_constant_one():
    """prodmake(1 + O(q^20), q, 20) -> QProduct(exponents={}) (D-03)."""
    R, q = _make_ring()
    series = R(1).add_bigoh(20)
    f = QSeries(series, T=20)
    p = prodmake(f, q, 20)
    assert isinstance(p, QProduct)
    # All a_n = 0 -> empty exponents dict
    assert p.exponents == {}


# ---------------------------------------------------------------------------
# Test 2: Round-trip via etaq
# ---------------------------------------------------------------------------

def test_prodmake_etaq_roundtrip():
    """prodmake(etaq(q,1,20), q, 20).to_series(20) == etaq(q,1,20)."""
    R, q = _make_ring()
    f = etaq(q, 1, 20)
    p = prodmake(f, q, 20)
    g = p.to_series(20)
    # Coefficients must match to O(q^20)
    for i in range(20):
        assert f.series[i] == g.series[i], f"coefficient mismatch at q^{i}"


# ---------------------------------------------------------------------------
# Test 3: ValueError — non-zero fractional shift r
# ---------------------------------------------------------------------------

def test_prodmake_raises_on_nonzero_r():
    """prodmake raises ValueError if f.r != 0."""
    R, q = _make_ring()
    series = R(1).add_bigoh(20)
    f = QSeries(series, T=20, r=QQ('1/4'))
    with pytest.raises(ValueError):
        prodmake(f, q, 20)


# ---------------------------------------------------------------------------
# Test 4: ValueError — constant term != 1
# ---------------------------------------------------------------------------

def test_prodmake_raises_on_nonunit_constant():
    """prodmake raises ValueError if constant term of f is not 1."""
    R, q = _make_ring()
    # Build q + q^2 + ... (valuation 1, constant term = 0)
    series = (q + q**2).add_bigoh(20)
    f = QSeries(series, T=20)
    with pytest.raises(ValueError):
        prodmake(f, q, 20)


# ---------------------------------------------------------------------------
# Test 5: Rogers-Ramanujan G-series (tutorial §3.1)
# ---------------------------------------------------------------------------

def test_prodmake_rogers_ramanujan():
    """prodmake on G(q) recovers exponent dict {1:1,4:1,6:1,9:1,11:1,14:1,16:1,19:1}.

    G(q) = sum_{n>=0} q^{n^2} / (q;q)_n   (Rogers-Ramanujan G-series).

    Expected product: prod_{n>=1, n not≡0,±2 mod 5} (1-q^n)
    i.e. exponents = 1 at n ≡ ±1 mod 5, 0 otherwise.
    From tutorial §3.1:
      n=1  (1 mod 5):  e=1
      n=4  (4≡-1 mod 5): e=1
      n=6  (6≡1 mod 5):  e=1
      n=9  (9≡4≡-1 mod 5): e=1
      n=11 (11≡1 mod 5): e=1
      n=14 (14≡4≡-1 mod 5): e=1
      n=16 (16≡1 mod 5): e=1
      n=19 (19≡4≡-1 mod 5): e=1

    The sign convention: f = prod(1-q^n)^(-a_n), QProduct stores e_n = -a_n.
    G = prod(1-q^n)^(-1) for n≡±1 mod 5 (reciprocal product), so a_n = 1, e_n = -1.
    """
    R, q = _make_ring()

    # Build G(q) = sum_{n=0}^{N} q^{n^2} / (q;q)_n   to sufficient order
    # Use enough terms so truncation at O(q^20) is correct
    T = 20
    # q^{n^2} vanishes for n^2 >= 20, so n <= 4 suffices
    G_series = R(0).add_bigoh(T)
    for n in range(5):  # n=0,1,2,3,4; q^{25} >= T so we stop at n=4
        if n * n >= T:
            break
        # (q;q)_n = prod_{i=0}^{n-1}(1 - q^i); build in the ring directly
        if n == 0:
            denom_s = R(1).add_bigoh(T)
        else:
            denom_s = R(1).add_bigoh(T)
            for i in range(n):
                denom_s = (denom_s * (1 - q**(i + 1))).add_bigoh(T)
        # q^{n^2} factor
        numerator = q**(n * n)
        # Division in LaurentSeriesRing
        term = (numerator / denom_s).add_bigoh(T)
        G_series = (G_series + term).add_bigoh(T)

    f = QSeries(G_series, T=T)
    p = prodmake(f, q, T)

    # G(q) = 1 / prod_{n≡±1 mod 5}(1-q^n)
    # So G = prod(1-q^n)^(-1) for those n.
    # Maple: f = prod(1-q^n)^(-a_n) => -a_n = -1 => a_n = 1, e_n = -a_n = -1
    expected = {1: -1, 4: -1, 6: -1, 9: -1, 11: -1, 14: -1, 16: -1, 19: -1}
    # Convert expected to QQ for comparison
    expected_qq = {n: QQ(e) for n, e in expected.items()}
    # Convert actual exponents to QQ
    actual_qq = {n: QQ(e) for n, e in p.exponents.items()}

    assert actual_qq == expected_qq, (
        f"Rogers-Ramanujan exponent dict mismatch.\n"
        f"Expected: {expected_qq}\n"
        f"Got:      {actual_qq}"
    )


# ---------------------------------------------------------------------------
# Task 2 tests: checkprod
# ---------------------------------------------------------------------------

def test_checkprod_nice():
    """checkprod(etaq(q,1,20), 2, 20) returns [1, exps] with all |exps[i]| <= 2."""
    from qseries._utilities import checkprod
    R, q = _make_ring()
    f = etaq(q, 1, 20)
    result = checkprod(f, 2, 20)
    assert result is not False, "checkprod should return a result for etaq with M=2"
    assert isinstance(result, list) and len(result) == 2
    c, exps = result
    assert QQ(c) == 1
    for e in exps:
        assert abs(QQ(e)) <= 2


def test_checkprod_not_nice():
    """checkprod returns False when a product exponent exceeds M."""
    from qseries._utilities import checkprod
    R, q = _make_ring()
    # etaq has all exponents = 1, so checkprod with M=0 should return False
    f = etaq(q, 1, 20)
    result = checkprod(f, 0, 20)
    assert result is False


def test_prodmake_importable():
    """from qseries import prodmake must succeed and be callable."""
    from qseries import prodmake as pm
    assert callable(pm)
