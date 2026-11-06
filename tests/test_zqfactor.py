"""
tests/test_zqfactor.py — CONV-07: zqfactor (Phase 7).

Oracles:
  - Maple 2026 + qseries 1.3 output (parity battery, maple_results.txt), for the doc-page
    example g = tripleprod(-z^2 q^3, q^4, 20) - tripleprod(-z^2 q, q^4, 20)/z and for
    prod (1 + z q^n).  (The doc page shows only nine factors for N = 10; real Maple gives
    factors through q^10, and the port follows Maple.)
  - Mathematical identities (stated per test): Jacobi triple product, Euler's product
    (q;q)_inf, the product (-zq;q)_inf, and Phi_3(z) = (1 - z^3)/(1 - z).
"""
import warnings
import pytest
from sage.all import QQ, LaurentPolynomialRing, LaurentSeriesRing

from qseries._series import QSeries
from qseries._building_blocks import tripleprod, etaq
from qseries._zqfactor import zqfactor, ZQProduct


@pytest.fixture
def zq():
    Lz = LaurentPolynomialRing(QQ, 'z')
    z = Lz.gen()
    R = LaurentSeriesRing(Lz, 'q', default_prec=60)
    return z, R.gen()


def _doc_g(z, q):
    return tripleprod(-z**2 * q**3, q**4, 20) - tripleprod(-z**2 * q, q**4, 20) / z


def test_zqfactor_doc_example(zq):
    """Oracle: Maple 2026 + qseries 1.3 (parity case zqfactor_doc): zqfactor(g, z, q, 10) gives
    the constant (1 - 1/z) and the factors (1 - z q^j)(1 - q^j)(1 - q^j/z) for j = 1..10."""
    z, q = zq
    result = zqfactor(_doc_g(z, q), z, q, 10)
    assert isinstance(result, ZQProduct)
    assert result.constant == 1 - 1 / z
    assert result.factors == [f for j in range(1, 11) for f in ((1, 1, j, 1), (1, 0, j, 1), (1, -1, j, 1))]


def test_zqfactor_doc_example_round_trip(zq):
    """Oracle: Jacobi triple product -- g = (1/z;q)_inf (zq;q)_inf (q;q)_inf, so expanding the
    returned product reproduces g to O(q^40)."""
    z, q = zq
    g = _doc_g(z, q)
    result = zqfactor(g, z, q, 39)
    assert all(e == 1 and a == 1 for a, i, j, e in result.factors)
    expanded = result.to_series(40, z)
    assert expanded.series == g.series.add_bigoh(40)


def test_zqfactor_euler_product(zq):
    """Oracle: Euler -- etaq(q,1,T) = prod (1 - q^n); with no z the factors are (1 - q^n)."""
    z, q = zq
    f = etaq(q, 1, 30)
    result = zqfactor(f, z, q)
    assert result.factors == [(1, 0, n, 1) for n in range(1, 30)]


def test_zqfactor_plus_factors(zq):
    """Oracle: Maple 2026 + qseries 1.3 (parity case zqfactor_plus): prod_{n=1}^{12} (1 + z q^n)
    to O(q^13), N = 12, comes back as the twelve factors (1 + z q^n)."""
    z, q = zq
    s = q.parent()(1).add_bigoh(13)
    for n in range(1, 13):
        s = (s * (1 + z * q**n)).add_bigoh(13)
    result = zqfactor(QSeries(s, 13), z, q, 12)
    assert result.factors == [(-1, 1, n, 1) for n in range(1, 13)]
    assert "(1 + z*q)" in repr(result)


def test_zqfactor_constant_kept(zq):
    """Oracle: Maple zqfactor keeps the q^0 coefficient unfactored (parity case zqfactor_doc
    prints (1-1/z)); (1 + z + z^2)(1 - q) -> constant 1 + z + z^2 and the factor (1 - q)."""
    z, q = zq
    f = QSeries(((1 + z + z**2) * (1 - q)).add_bigoh(20), 20)
    result = zqfactor(f, z, q)
    assert result.constant == 1 + z + z**2
    assert result.factors == [(1, 0, 1, 1)]


def test_zqfactor_monomial_prefactor(zq):
    """Oracle: q^2 * z * (1 - q) -> prefactor q^2, constant z and the single factor (1 - q)."""
    z, q = zq
    f = QSeries((z * q**2 * (1 - q)).add_bigoh(20), 20)
    result = zqfactor(f, z, q)
    assert (result.qpow, result.constant) == (2, z)
    assert result.factors == [(1, 0, 1, 1)]


def test_zqfactor_fails_gracefully(zq):
    """Design decision: a coefficient that is not a Laurent polynomial in z after dividing by
    the q^0 term (here 1/(1+z) at q^1) -> warn and return None."""
    z, q = zq
    f = QSeries(((1 + z) + q).add_bigoh(20), 20)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert zqfactor(f, z, q) is None
    assert any(issubclass(w.category, UserWarning) for w in caught)


def test_zqfactor_type_error():
    """Design decision: input must be a QSeries.

    Oracle: Design decision (Phase 7): input must be a QSeries.
    """
    with pytest.raises(TypeError):
        zqfactor(None, None, None, 10)
